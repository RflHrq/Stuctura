"""Orquestração: liga a FSM pura ao log append-only.

É o único módulo que importa `engine` e `store` ao mesmo tempo. A regra de
dependência do §3 continua valendo — `engine` não conhece `store`, `store`
não conhece `engine` — e quem conhece as duas pontas é esta camada.

Não há regra de negócio aqui. A FSM decide; o service traduz e persiste.

RETOMADA POR REPLAY (RNF06)
---------------------------
O estado da sessão NÃO é guardado em memória. A cada requisição ele é
reconstruído replicando as entradas do log através da FSM. Custa uma
varredura de algumas dezenas de eventos e compra três coisas:

  - a sessão sobrevive a fechar a aba, a matar o processo e a reiniciar
    o servidor no meio da coleta;
  - o estado em memória nunca pode divergir do log, porque não existe
    estado em memória;
  - RNF04 vale para o fluxo, não só para o vetor de premissas.

Só funciona porque a FSM é determinística e pura: as mesmas entradas
produzem exatamente o mesmo estado. Se algum dia entrar aleatoriedade ou
relógio no motor, a retomada quebra silenciosamente — e é por isso que
`tests/test_api.py` compara uma sessão retomada com a original.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any, Mapping

from engine import model, session as fsm, strategy
from engine.loader import Domain
from store import events as store_events
from store import projections

# Eventos do log que correspondem a uma ENTRADA do aluno. Só estes são
# reproduzidos: os demais são consequência, e a FSM os reemite sozinha.
ENTRADAS = {
    "answer_submitted",
    "socratic_step_answered",
    "explanation_acknowledged",
    "stage_acknowledged",
}


class SessionNotFound(LookupError):
    pass


class OutOfSync(ValueError):
    """A requisição não corresponde ao que a sessão espera agora.

    Acontece quando o aluno usa o botão voltar do navegador ou reenvia um
    formulário. A resposta correta é 409 com o `next_action` atual, para
    que a interface se realinhe em vez de gravar um evento fora de ordem.
    """


@dataclass(frozen=True, slots=True)
class SessionView:
    """O que a API devolve sobre uma sessão. Nada aqui é decisão."""

    session_id: str
    arm: str
    kc_sequence: tuple[str, ...]
    state: fsm.SessionState
    action: fsm.Action
    # Eventos emitidos NESTA transição. É daqui que a rota tira o que
    # aconteceu agora — em vez de reler o banco e criar uma segunda fonte.
    emitted: tuple[fsm.Emit, ...] = ()

    def emitted_of(self, type: str) -> dict[str, Any] | None:
        for e in self.emitted:
            if e.type == type:
                return e.payload
        return None

    def as_json(self, domain: Domain) -> dict[str, Any]:
        kc = self.state.kc
        return {
            "session_id": self.session_id,
            "arm": self.arm,
            "phase": self.state.phase,
            "kc": kc,
            "kc_sequence": list(self.kc_sequence),
            "kc_status": dict(self.state.kc_status),
            "cognitive_state": (
                model.cognitive_state(domain, self.state.vector, kc) if kc else None
            ),
            "vector": (
                {n: model.state_of(self.state.vector, kc, n)
                 for n in domain.kcs[kc].nodes} if kc else {}
            ),
            "next_action": self.action.as_json(),
            "done": self.state.done,
        }


# --------------------------------------------------------------------------
# Criação
# --------------------------------------------------------------------------

def create_session(
    conn: sqlite3.Connection,
    domain: Domain,
    participant: str,
    arm: str,
    kc_sequence: list[str] | None = None,
    consented: bool = False,
    prior_c: str | None = None,
) -> SessionView:
    """Cria participante (se novo), sessão e primeira ação.

    `arm` e `consented` não têm padrão de propósito. A alocação é decisão
    do pesquisador e o consentimento é do participante: qualquer valor
    assumido em silêncio aqui vira um dado que ninguém declarou.
    """
    sequencia = tuple(kc_sequence or domain.pilot_sequence)
    if not sequencia:
        raise ValueError("sem sequência de KCs: study.yaml define pilot_sequence")
    if arm not in strategy.ARMS:
        raise ValueError(
            "braço %r inválido; a alocação tem de ser explícita, um de %s"
            % (arm, list(strategy.ARMS))
        )

    existe = conn.execute(
        "SELECT arm FROM participants WHERE code = ?", (participant,)
    ).fetchone()

    if existe is None:
        if not consented:
            raise ValueError(
                "o participante %s ainda não consentiu; nada é gravado" % participant
            )
        opcoes = domain.study.prior_c_options
        if opcoes and prior_c not in opcoes:
            # É a variável de estratificação do §4.3. Perdê-la significa
            # não conseguir mostrar que os grupos ficaram equilibrados.
            raise ValueError(
                "experiência prévia %r fora das opções declaradas: %s"
                % (prior_c, list(opcoes))
            )
        store_events.add_participant(conn, participant, arm, prior_c,
                                     consented=True)
    elif existe["arm"] != arm:
        # A alocação é feita uma vez e não muda: trocar de braço no meio da
        # coleta contaminaria a comparação. Este teste vem ANTES da retomada
        # de propósito — braço divergente é erro de digitação do
        # pesquisador, e retomar em silêncio o esconderia.
        raise ValueError(
            "participante %s já está alocado no braço %r" % (participant, existe["arm"])
        )
    else:
        # RNF06 diz "reabrir com o MESMO CÓDIGO". O aluno não conhece o
        # session_id — ele conhece o código que recebeu. Reabrir com um
        # código que já tem sessão em aberto RETOMA, não cria outra.
        #
        # Sem isto, fechar a aba e digitar o código de novo geraria uma
        # segunda sessão do mesmo participante, e a análise teria de
        # decidir qual das duas conta.
        aberta = conn.execute(
            "SELECT id FROM sessions WHERE participant = ? AND ended_at IS NULL"
            " ORDER BY started_at DESC LIMIT 1", (participant,)
        ).fetchone()
        if aberta is not None:
            return load_session(conn, domain, aberta["id"])

    sid = store_events.start_session(
        conn, participant, arm, sequencia, domain.hash
    )
    t = fsm.start(domain, arm, sequencia)
    _persist(conn, sid, t.events)
    return SessionView(sid, arm, sequencia, t.state, t.action, t.events)


# --------------------------------------------------------------------------
# Retomada por replay
# --------------------------------------------------------------------------

def load_session(conn: sqlite3.Connection, domain: Domain, session_id: str) -> SessionView:
    """Reconstrói a sessão do log. É também a rota de retomada (RNF06)."""
    linha = conn.execute(
        "SELECT id, arm, kc_sequence FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    if linha is None:
        raise SessionNotFound(session_id)

    import json
    sequencia = tuple(json.loads(linha["kc_sequence"]))
    t = fsm.start(domain, linha["arm"], sequencia)

    for e in store_events.read(conn, session_id):
        entrada = _to_input(e)
        if entrada is None:
            continue
        t = fsm.advance(domain, t.state, entrada)

    return SessionView(session_id, linha["arm"], sequencia, t.state, t.action)


def _to_input(e: store_events.Event) -> fsm.Event | None:
    """Traduz um evento do log de volta para a entrada que o produziu."""
    if e.type not in ENTRADAS:
        return None
    p = e.payload

    if e.type == "answer_submitted":
        texto = p.get("text")
        return fsm.Answer(
            ciu_id=p["ciu_id"], confidence=p["confidence"],
            elapsed_ms=int(p.get("elapsed_ms", 0)),
            option_idx=p.get("option_idx"),
            text=tuple(texto) if isinstance(texto, list) else texto,
        )
    if e.type == "socratic_step_answered":
        return fsm.StepAnswer(bool(p.get("accepted")), int(p.get("elapsed_ms", 0)))
    if e.type == "explanation_acknowledged":
        return fsm.StepAnswer(True, int(p.get("elapsed_ms", 0)))
    return fsm.Acknowledge(int(p.get("elapsed_ms", 0)))


# --------------------------------------------------------------------------
# Avanço
# --------------------------------------------------------------------------

def submit_answer(
    conn: sqlite3.Connection, domain: Domain, session_id: str,
    ciu_id: str, confidence: str, elapsed_ms: int,
    option_idx: int | None = None, text: Any = None,
) -> SessionView:
    vista = load_session(conn, domain, session_id)
    _exige(vista, ("ciu",))
    if vista.action.ciu_id != ciu_id:
        raise OutOfSync(
            "a sessão espera %r, veio resposta para %r" % (vista.action.ciu_id, ciu_id)
        )
    if ciu_id not in domain.cius:
        raise ValueError("CIU desconhecida: %r" % ciu_id)
    if confidence not in domain.study.confidence_scale:
        raise ValueError(
            "confiança %r fora da escala %s"
            % (confidence, list(domain.study.confidence_scale))
        )

    ev = fsm.Answer(ciu_id, confidence, elapsed_ms, option_idx, text)
    return _avanca(conn, domain, vista, ev)


def submit_step(
    conn: sqlite3.Connection, domain: Domain, session_id: str,
    accepted: bool, elapsed_ms: int,
    kc: str | None = None, node: str | None = None,
) -> SessionView:
    vista = load_session(conn, domain, session_id)
    _exige(vista, ("ask", "explain"))
    # O cliente manda (kc, node) para que um clique atrasado não seja
    # aplicado ao passo seguinte. Divergiu, é dessincronização.
    if kc is not None and (kc, node) != (vista.action.kc, vista.action.node):
        raise OutOfSync(
            "a sessão está em %s:%s, veio passo de %s:%s"
            % (vista.action.kc, vista.action.node, kc, node)
        )
    return _avanca(conn, domain, vista, fsm.StepAnswer(accepted, elapsed_ms))


def acknowledge(
    conn: sqlite3.Connection, domain: Domain, session_id: str, elapsed_ms: int = 0
) -> SessionView:
    vista = load_session(conn, domain, session_id)
    _exige(vista, ("diagram", "conclude"))
    return _avanca(conn, domain, vista, fsm.Acknowledge(elapsed_ms))


def record_telemetry(
    conn: sqlite3.Connection, session_id: str, type: str, payload: Mapping[str, Any]
) -> None:
    """Eventos sem decisão de fluxo (§9): `diagram_toggled` e afins.

    Não passa pela FSM de propósito: nenhum evento que o cliente possa
    emitir livremente pode mover a máquina de estados.
    """
    if type not in TELEMETRIA:
        raise ValueError(
            "telemetria não aceita %r; permitidos: %s" % (type, sorted(TELEMETRIA))
        )
    _persist(conn, session_id, (fsm.Emit(type, dict(payload)),))


# Só estes podem chegar pela rota aberta de telemetria. Um cliente não
# pode injetar `kc_completed` nem `answer_submitted` no log.
TELEMETRIA = {"diagram_toggled"}


def _exige(vista: SessionView, kinds: tuple[str, ...]) -> None:
    if vista.state.done:
        raise OutOfSync("a sessão já terminou")
    if vista.action.kind not in kinds:
        raise OutOfSync(
            "a sessão espera %r, não %s" % (vista.action.kind, " nem ".join(kinds))
        )


def _avanca(
    conn: sqlite3.Connection, domain: Domain, vista: SessionView, ev: fsm.Event
) -> SessionView:
    t = fsm.advance(domain, vista.state, ev)
    _persist(conn, vista.session_id, t.events)
    return SessionView(vista.session_id, vista.arm, vista.kc_sequence,
                       t.state, t.action, t.events)


def _persist(conn: sqlite3.Connection, session_id: str, emits) -> None:
    """Grava os eventos e atualiza a projeção derivada.

    `session_ended` passa por `store.end_session`, que também fecha a linha
    da sessão — é a única saída que precisa tocar duas tabelas.
    """
    for emit in emits:
        if emit.type == "session_ended":
            store_events.end_session(
                conn, session_id, emit.payload.get("reason", "concluida"),
                int(emit.payload.get("total_ms", 0)),
            )
            continue
        gravado = store_events.append(conn, session_id, emit.type, emit.payload)
        projections.apply_event(conn, gravado)
