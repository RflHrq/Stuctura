"""Log de eventos append-only (RF13) e acesso ao banco.

Este modulo e a unica porta de escrita do sistema. Toda decisao do motor
entra aqui como um evento imutavel; nada mais e verdade. `node_state` e
projecao, e `store.projections` a reconstroi deste log a qualquer momento.

Regra de ouro: se um evento nao carrega informacao suficiente para
reconstruir o que aconteceu, ele esta incompleto (Definition of Done, §14).
Por isso qualquer evento pode carregar `node_updates`: e o canal pelo qual
o motor registra a decisao que tomou sobre o vetor de premissas, em vez de
deixar a projecao readivinhar essa decisao a partir do dominio.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "structura.db"

# Estados possiveis de um no do grafo de premissas (§5.1, §7.2).
NODE_STATES = ("unknown", "confirmed", "absent", "wrong")

# Confianca declarada, coletada antes da submissao (RF02) e usada para
# distinguir premissa ausente de errada (RF04, §7.3).
#
# A FONTE da escala e study.yaml. Esta constante e so o padrao de
# arranque: a API chama `set_confidence_scale()` na inicializacao com a
# escala do estudo. `store` nao importa `engine` — a direcao de
# dependencia se manteria invertida —, entao quem conhece as duas pontas
# injeta o valor.
CONFIDENCE_VALUES: tuple[str, ...] = ("chutei", "acho que sei", "tenho certeza")


def set_confidence_scale(values: Sequence[str]) -> None:
    """Alinha a validacao do log a escala declarada em study.yaml."""
    global CONFIDENCE_VALUES
    if not values:
        raise EventError("escala de confianca vazia")
    CONFIDENCE_VALUES = tuple(values)

ARMS = ("socratic", "direct")

# Catalogo de eventos (§5.2). type -> campos obrigatorios no payload.
# Campos extras sao permitidos; campos faltantes abortam a escrita.
# `node_updates` e opcional em todos e tratado a parte.
EVENT_SCHEMA: Mapping[str, tuple[str, ...]] = {
    "session_started":          ("arm", "kc_sequence", "domain_hash"),
    "ciu_presented":            ("ciu_id", "kc", "targets", "phase"),
    "answer_submitted":         ("ciu_id", "option_idx", "confidence", "elapsed_ms"),
    "misconception_detected":   ("misconception_id", "node", "kc"),
    "diagram_toggled":          ("from_state", "to_state", "elapsed_ms"),
    "socratic_step_shown":      ("kc", "node", "kind", "step_idx", "total"),
    "socratic_step_answered":   ("kc", "node", "accepted", "elapsed_ms"),
    "regression_triggered":     ("from_node", "to_node"),
    "direct_explanation_shown": ("kc", "node", "elapsed_ms"),
    # Dois acréscimos ao catálogo do §5.2, ambos exigidos pela retomada
    # (RNF06): o estado da sessão é RECONSTRUÍDO replicando as entradas do
    # log, e sem estes dois eventos as confirmações de diagrama, conclusão
    # e leitura não deixariam rastro — a sessão retomada divergiria.
    # `explanation_acknowledged` é também o par simétrico de
    # `socratic_step_answered` para o pareamento de tempo do §8.
    "explanation_acknowledged": ("kc", "node", "elapsed_ms"),
    "stage_acknowledged":       ("stage", "kc", "elapsed_ms"),
    "kc_completed":             ("kc", "vector", "elapsed_ms"),
    "kc_incomplete":            ("kc", "node", "attempts"),
    "session_ended":            ("reason", "total_ms"),
}


class EventError(ValueError):
    """Payload invalido ou tipo de evento desconhecido."""


@dataclass(frozen=True, slots=True)
class Event:
    id: int
    session_id: str
    seq: int
    ts: str
    type: str
    payload: dict[str, Any]

    @property
    def node_updates(self) -> tuple[dict[str, str], ...]:
        return tuple(self.payload.get("node_updates", ()))


# --------------------------------------------------------------------------
# Conexao
# --------------------------------------------------------------------------

Clock = Callable[[], str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Abre o banco com as pragmas que o piloto precisa.

    WAL para nao travar leitura durante a sessao; foreign_keys porque o
    esquema depende delas; isolation_level=None para controlarmos as
    transacoes explicitamente (o append precisa de BEGIN IMMEDIATE).
    """
    path = Path(db_path) if db_path is not None else DEFAULT_DB
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if str(path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")  # coleta presencial: durabilidade > velocidade
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Cria o esquema. Idempotente: seguro em toda inicializacao."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def open_db(db_path: str | Path | None = None) -> sqlite3.Connection:
    conn = connect(db_path)
    init_db(conn)
    return conn


# --------------------------------------------------------------------------
# Escrita de cabecalho (participantes e sessoes)
# --------------------------------------------------------------------------

def add_participant(
    conn: sqlite3.Connection,
    code: str,
    arm: str,
    prior_c: str | None = None,
    *,
    consented: bool = True,
    clock: Clock = utc_now,
) -> None:
    """Registra o participante. `consent_at` so e gravado com consentimento.

    A coluna e NOT NULL desde o §5.1, entao um participante sem
    consentimento simplesmente nao entra. E o comportamento certo: um
    banco que AFIRMA consentimento sem que ele tenha sido dado e pior do
    que um que nao o registra, e e o primeiro item que um comite de etica
    verifica.
    """
    if arm not in ARMS:
        raise EventError("arm invalido: %r; esperado um de %s" % (arm, ARMS))
    if not consented:
        raise EventError(
            "participante %s sem consentimento: nada e gravado" % code
        )
    conn.execute(
        "INSERT INTO participants (code, arm, prior_c, consent_at) VALUES (?,?,?,?)",
        (code, arm, prior_c, clock()),
    )


def start_session(
    conn: sqlite3.Connection,
    participant: str,
    arm: str,
    kc_sequence: Sequence[str],
    domain_hash: str,
    *,
    session_id: str | None = None,
    clock: Clock = utc_now,
) -> str:
    """Cria a sessao e emite `session_started`, numa unica transacao.

    `domain_hash` e obrigatorio de proposito (§15): sem ele nao se responde
    "os participantes viram exatamente o mesmo conteudo?".
    """
    if arm not in ARMS:
        raise EventError("arm invalido: %r; esperado um de %s" % (arm, ARMS))
    sid = session_id or uuid.uuid4().hex
    now = clock()
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            "INSERT INTO sessions (id, participant, arm, kc_sequence, started_at)"
            " VALUES (?,?,?,?,?)",
            (sid, participant, arm, json.dumps(list(kc_sequence)), now),
        )
        _insert_event(
            conn,
            sid,
            "session_started",
            {"arm": arm, "kc_sequence": list(kc_sequence), "domain_hash": domain_hash},
            now,
        )
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return sid


def end_session(
    conn: sqlite3.Connection,
    session_id: str,
    reason: str,
    total_ms: int,
    *,
    clock: Clock = utc_now,
) -> Event:
    now = clock()
    conn.execute("BEGIN IMMEDIATE")
    try:
        ev = _insert_event(
            conn, session_id, "session_ended", {"reason": reason, "total_ms": total_ms}, now
        )
        conn.execute("UPDATE sessions SET ended_at = ? WHERE id = ?", (now, session_id))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return ev


# --------------------------------------------------------------------------
# Append
# --------------------------------------------------------------------------

def append(
    conn: sqlite3.Connection,
    session_id: str,
    type: str,
    payload: Mapping[str, Any] | None = None,
    *,
    clock: Clock = utc_now,
) -> Event:
    """Grava um evento e devolve o que ficou gravado.

    O `seq` e alocado dentro de BEGIN IMMEDIATE, o que serializa escritores
    concorrentes; UNIQUE(session_id, seq) e a rede de seguranca caso alguem
    contorne esta funcao.
    """
    body = validate(type, payload or {})
    conn.execute("BEGIN IMMEDIATE")
    try:
        ev = _insert_event(conn, session_id, type, body, clock())
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return ev


def append_many(
    conn: sqlite3.Connection,
    session_id: str,
    items: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    clock: Clock = utc_now,
) -> list[Event]:
    """Grava varios eventos atomicamente: ou entram todos, ou nenhum."""
    prepared = [(t, validate(t, p or {})) for t, p in items]
    out: list[Event] = []
    conn.execute("BEGIN IMMEDIATE")
    try:
        for type_, body in prepared:
            out.append(_insert_event(conn, session_id, type_, body, clock()))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return out


def _insert_event(
    conn: sqlite3.Connection,
    session_id: str,
    type: str,
    payload: Mapping[str, Any],
    ts: str,
) -> Event:
    """Insere sem abrir transacao. So chamar de dentro de uma."""
    row = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 AS next FROM events WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    seq = int(row["next"])
    cur = conn.execute(
        "INSERT INTO events (session_id, seq, ts, type, payload) VALUES (?,?,?,?,?)",
        (session_id, seq, ts, type, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
    )
    return Event(int(cur.lastrowid), session_id, seq, ts, type, dict(payload))


# --------------------------------------------------------------------------
# Validacao (falha na escrita, nunca na analise)
# --------------------------------------------------------------------------

def validate(type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Confere o payload contra o catalogo do §5.2 e devolve-o normalizado."""
    if type not in EVENT_SCHEMA:
        raise EventError(
            "tipo de evento desconhecido: %r. Conhecidos: %s"
            % (type, ", ".join(sorted(EVENT_SCHEMA)))
        )
    faltando = [k for k in EVENT_SCHEMA[type] if k not in payload]
    if faltando:
        raise EventError("evento %r sem campo(s) obrigatorio(s): %s" % (type, faltando))

    body = dict(payload)

    if type == "answer_submitted" and body["confidence"] not in CONFIDENCE_VALUES:
        raise EventError(
            "confidence invalida: %r; esperado um de %s"
            % (body["confidence"], CONFIDENCE_VALUES)
        )

    if "node_updates" in body:
        body["node_updates"] = [_validate_update(u, type) for u in body["node_updates"]]

    try:
        json.dumps(body)
    except TypeError as exc:  # pragma: no cover - defensivo
        raise EventError("payload de %r nao e serializavel em JSON: %s" % (type, exc)) from exc
    return body


def _validate_update(update: Any, ev_type: str) -> dict[str, str]:
    if not isinstance(update, Mapping):
        raise EventError(
            "node_updates de %r: esperado objeto, veio %s"
            % (ev_type, update.__class__.__name__)
        )
    faltando = [k for k in ("kc", "node", "state") if k not in update]
    if faltando:
        raise EventError("node_updates de %r sem campo(s): %s" % (ev_type, faltando))
    if update["state"] not in NODE_STATES:
        raise EventError(
            "node_updates de %r: state %r invalido; esperado um de %s"
            % (ev_type, update["state"], NODE_STATES)
        )
    return {"kc": str(update["kc"]), "node": str(update["node"]), "state": str(update["state"])}


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

def read(
    conn: sqlite3.Connection,
    session_id: str,
    *,
    since_seq: int = 0,
    types: Sequence[str] | None = None,
) -> list[Event]:
    sql = "SELECT * FROM events WHERE session_id = ? AND seq > ?"
    args: list[Any] = [session_id, since_seq]
    if types:
        sql += " AND type IN (%s)" % ",".join("?" * len(types))
        args.extend(types)
    sql += " ORDER BY seq"
    return [_row_to_event(r) for r in conn.execute(sql, args)]


def read_all(conn: sqlite3.Connection) -> list[Event]:
    """Todos os eventos de todas as sessoes, em ordem estavel (export, §12)."""
    rows = conn.execute("SELECT * FROM events ORDER BY session_id, seq")
    return [_row_to_event(r) for r in rows]


def session_ids(conn: sqlite3.Connection) -> list[str]:
    return [r["id"] for r in conn.execute("SELECT id FROM sessions ORDER BY started_at, id")]


def last_seq(conn: sqlite3.Connection, session_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) AS s FROM events WHERE session_id = ?", (session_id,)
    ).fetchone()
    return int(row["s"])


def _row_to_event(row: sqlite3.Row) -> Event:
    return Event(
        id=int(row["id"]),
        session_id=row["session_id"],
        seq=int(row["seq"]),
        ts=row["ts"],
        type=row["type"],
        payload=json.loads(row["payload"]),
    )
