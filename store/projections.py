"""Projecao do log de eventos para o estado derivado (RF14, RNF04).

A projecao e um *fold* puro: percorre os eventos de uma sessao em ordem de
`seq` e aplica os `node_updates` que cada um carrega. Nao ha politica aqui -
nenhuma decisao sobre o que uma resposta significa, nenhuma leitura do
dominio. Quem decide e o motor, no momento da sessao; a projecao apenas
reaplica a decisao registrada.

E isso que torna RNF04 verificavel: `verify()` refaz o fold do zero e compara
com a tabela `node_state`. Se divergirem, ou o motor escreveu no banco sem
emitir evento, ou alguem alterou a tabela derivada a mao. Ambos sao bug.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable, Mapping

from store.events import Event, read, session_ids

# (kc, node) -> (state, updated_seq)
Projection = dict[tuple[str, str], tuple[str, int]]


@dataclass(frozen=True, slots=True)
class Divergence:
    """Uma diferenca entre a tabela derivada e o fold do log."""

    kc: str
    node: str
    na_tabela: tuple[str, int] | None
    no_log: tuple[str, int] | None

    def __str__(self) -> str:
        return "%s/%s: tabela=%s log=%s" % (self.kc, self.node, self.na_tabela, self.no_log)


# --------------------------------------------------------------------------
# Fold puro (sem I/O, testavel isolado)
# --------------------------------------------------------------------------

def project(events: Iterable[Event]) -> Projection:
    """Reduz uma sequencia de eventos ao vetor de premissas resultante.

    Determinismo (RNF02): a mesma lista de eventos produz sempre o mesmo
    dicionario. O ultimo update de um no vence, e `updated_seq` guarda em
    que ponto da sessao aquilo foi decidido.
    """
    out: Projection = {}
    seq_anterior = 0
    for ev in events:
        if ev.seq <= seq_anterior:
            raise ValueError(
                "eventos fora de ordem na sessao %s: seq %d apos %d"
                % (ev.session_id, ev.seq, seq_anterior)
            )
        seq_anterior = ev.seq
        for upd in ev.node_updates:
            out[(upd["kc"], upd["node"])] = (upd["state"], ev.seq)
    return out


def vector(projection: Projection, kc: str) -> dict[str, str]:
    """O vetor de premissas de um KC: node -> state, sem o `seq`."""
    return {node: st for (k, node), (st, _) in projection.items() if k == kc}


def kcs_tocados(projection: Projection) -> list[str]:
    return sorted({kc for kc, _ in projection})


# --------------------------------------------------------------------------
# Escrita da tabela derivada
# --------------------------------------------------------------------------

def apply_event(conn: sqlite3.Connection, event: Event) -> None:
    """Aplica um unico evento a `node_state` (caminho quente da sessao).

    Chamado logo apos o append, para nao refazer o fold inteiro a cada
    interacao (RNF03). Equivalente, por construcao, ao que `rebuild()` faria.
    """
    for upd in event.node_updates:
        conn.execute(
            "INSERT INTO node_state (session_id, kc, node, state, updated_seq)"
            " VALUES (?,?,?,?,?)"
            " ON CONFLICT(session_id, kc, node) DO UPDATE SET"
            "   state = excluded.state, updated_seq = excluded.updated_seq",
            (event.session_id, upd["kc"], upd["node"], upd["state"], event.seq),
        )


def rebuild(conn: sqlite3.Connection, session_id: str) -> Projection:
    """Apaga e reconstroi `node_state` da sessao a partir do log (RF14).

    Atomico: se falhar no meio, a tabela derivada fica como estava.
    """
    proj = project(read(conn, session_id))
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("DELETE FROM node_state WHERE session_id = ?", (session_id,))
        conn.executemany(
            "INSERT INTO node_state (session_id, kc, node, state, updated_seq)"
            " VALUES (?,?,?,?,?)",
            [(session_id, kc, node, st, seq) for (kc, node), (st, seq) in proj.items()],
        )
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return proj


def rebuild_all(conn: sqlite3.Connection) -> dict[str, Projection]:
    return {sid: rebuild(conn, sid) for sid in session_ids(conn)}


# --------------------------------------------------------------------------
# Leitura e verificacao
# --------------------------------------------------------------------------

def snapshot(conn: sqlite3.Connection, session_id: str) -> Projection:
    """Le `node_state` como esta gravada, sem tocar no log."""
    rows = conn.execute(
        "SELECT kc, node, state, updated_seq FROM node_state WHERE session_id = ?",
        (session_id,),
    )
    return {(r["kc"], r["node"]): (r["state"], int(r["updated_seq"])) for r in rows}


def verify(conn: sqlite3.Connection, session_id: str) -> list[Divergence]:
    """Compara a tabela derivada com o fold do log. Vazio = RNF04 satisfeito."""
    tabela = snapshot(conn, session_id)
    log = project(read(conn, session_id))
    chaves = sorted(set(tabela) | set(log))
    return [
        Divergence(kc, node, tabela.get((kc, node)), log.get((kc, node)))
        for kc, node in chaves
        if tabela.get((kc, node)) != log.get((kc, node))
    ]


def verify_all(conn: sqlite3.Connection) -> dict[str, list[Divergence]]:
    return {
        sid: d for sid in session_ids(conn) if (d := verify(conn, sid))
    }


def checkpoint_mismatches(conn: sqlite3.Connection, session_id: str) -> list[str]:
    """Confere os `kc_completed` contra a projecao no ponto em que ocorreram.

    Cada `kc_completed` carrega o vetor que o motor acreditava ter (§5.2).
    Se ele nao bate com o que o log projeta ate aquele `seq`, o motor tomou
    uma decisao que nao registrou - exatamente o que a DoD proibe.
    """
    eventos = read(conn, session_id)
    problemas: list[str] = []
    for i, ev in enumerate(eventos):
        if ev.type != "kc_completed":
            continue
        esperado = ev.payload.get("vector")
        if not isinstance(esperado, Mapping):
            continue
        obtido = vector(project(eventos[: i + 1]), ev.payload["kc"])
        if dict(esperado) != obtido:
            problemas.append(
                "seq %d kc_completed(%s): payload=%s projecao=%s"
                % (ev.seq, ev.payload["kc"], dict(esperado), obtido)
            )
    return problemas
