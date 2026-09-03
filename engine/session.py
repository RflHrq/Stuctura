"""Máquina de estados da sessão (§6). O único ponto que decide o próximo passo.

Nenhuma decisão de fluxo mora na interface. O navegador recebe um
`next_action` e renderiza; toda transição acontece aqui e emite evento.

PURA. Não importa `store` nem `api`, não toca disco, não sorteia, não
consulta relógio. Recebe (estado, evento) e devolve (estado, ação, eventos
a gravar). É o que permite rodar uma sessão inteira num teste, sem HTTP e
sem banco, e reproduzi-la na defesa.

    Transition = advance(domain, state, event)

O estado é um dataclass congelado e serializável: ele pode ser guardado,
transmitido, ou reconstruído do log (RF14, RNF06).

INVARIANTE CENTRAL (§6): a sessão nunca sai de CORRECAO sem que todos os
nós do plano estejam confirmados ou o limite de tentativas seja atingido.
Sem essa guarda, um aluno travado entra em laço. Ver `_avanca_correcao`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from engine import model, selector, socratic, strategy
from engine.loader import CIU, Domain, Ref

# Fases da sessão (§6).
ABERTA = "ABERTA"
DIAGNOSTICO = "DIAGNOSTICO"
CONFRONTO = "CONFRONTO"
CORRECAO = "CORRECAO"
CONCLUSAO = "CONCLUSAO"
VARIACAO = "VARIACAO"
FIM = "FIM"

# Situação de um KC ao ser deixado para trás.
COMPLETO = "completed"
EM_PROGRESSO = "in_progress"

# Teto de rodadas de correção num mesmo KC. Não é regra pedagógica: é a
# rede que garante que nenhuma configuração de domínio trave a sessão.
MAX_ROUNDS = 6


# --------------------------------------------------------------------------
# Entrada e saída
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Answer:
    """Resposta a uma CIU. `option_idx` para escolha, `text` para o resto."""

    ciu_id: str
    confidence: str
    elapsed_ms: int
    option_idx: int | None = None
    text: Any = None


@dataclass(frozen=True, slots=True)
class StepAnswer:
    """Resposta a um passo do traversal (braço A) ou confirmação de leitura (B)."""

    accepted: bool
    elapsed_ms: int


@dataclass(frozen=True, slots=True)
class Acknowledge:
    """O aluno seguiu adiante: fechou o diagrama ou leu a conclusão."""

    elapsed_ms: int = 0


Event = Answer | StepAnswer | Acknowledge


@dataclass(frozen=True, slots=True)
class Emit:
    """Um evento a gravar. A API traduz para `store.events.append`."""

    type: str
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Action:
    """O que apresentar em seguida. É o `next_action` do §9.

    `kind` ∈ ciu | diagram | ask | explain | conclude | done
    """

    kind: str
    kc: str | None = None
    node: str | None = None
    ciu_id: str | None = None
    text: str | None = None
    step_idx: int = 0
    step_total: int = 0
    data: Mapping[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.kind}
        for campo in ("kc", "node", "ciu_id", "text"):
            valor = getattr(self, campo)
            if valor is not None:
                out[campo] = valor
        if self.step_total:
            out["step"] = {"idx": self.step_idx, "total": self.step_total}
        if self.data:
            out.update(self.data)
        return out


@dataclass(frozen=True, slots=True)
class SessionState:
    """Todo o estado da sessão. Serializável e reconstruível do log."""

    arm: str
    kc_sequence: tuple[str, ...]
    kc_index: int = 0
    phase: str = ABERTA
    vector: Mapping[Ref, str] = field(default_factory=dict)

    # Diagnóstico
    diagnostics_done: int = 0
    used_cius: tuple[str, ...] = ()
    last_ciu_type: str | None = None
    current_ciu: str | None = None

    # Correção
    detected: str | None = None            # misconception_id
    target: Ref | None = None              # nó que o traversal vai reconstruir
    plan: tuple[Ref, ...] = ()             # congelado ao entrar na correção
    cursor: int = 0
    attempts: Mapping[Ref, int] = field(default_factory=dict)
    rounds: int = 0                        # rodadas de correção neste KC

    # Encerramento
    kc_status: Mapping[str, str] = field(default_factory=dict)

    @property
    def kc(self) -> str | None:
        if 0 <= self.kc_index < len(self.kc_sequence):
            return self.kc_sequence[self.kc_index]
        return None

    @property
    def done(self) -> bool:
        return self.phase == FIM


@dataclass(frozen=True, slots=True)
class Transition:
    state: SessionState
    action: Action
    events: tuple[Emit, ...] = ()


# --------------------------------------------------------------------------
# Início
# --------------------------------------------------------------------------

def start(domain: Domain, arm: str, kc_sequence: Sequence[str]) -> Transition:
    """Abre a sessão no primeiro KC da sequência.

    Não emite `session_started`: quem o emite é `store.start_session`, que
    é também quem grava o hash do domínio (§15). Duplicar aqui criaria
    dois pontos de verdade sobre o começo da sessão.
    """
    if arm not in strategy.ARMS:
        raise ValueError("braço desconhecido: %r; esperado um de %s" % (arm, strategy.ARMS))
    ordem = selector.kc_order(domain, kc_sequence)
    if not ordem:
        raise ValueError("sequência de KCs vazia")
    estado = SessionState(arm=arm, kc_sequence=ordem, phase=DIAGNOSTICO)
    return _abre_kc(domain, estado)


def advance(domain: Domain, state: SessionState, event: Event) -> Transition:
    """(estado, evento) -> (estado, ação, eventos). Único ponto de decisão."""
    if state.phase == DIAGNOSTICO:
        if not isinstance(event, Answer):
            raise ValueError("DIAGNOSTICO espera Answer, veio %s" % type(event).__name__)
        return _responde_diagnostico(domain, state, event)

    if state.phase == CONFRONTO:
        if not isinstance(event, Acknowledge):
            raise ValueError("CONFRONTO espera Acknowledge, veio %s" % type(event).__name__)
        ev = Emit("stage_acknowledged", {
            "stage": "diagram", "kc": state.kc,
            "node": state.target[1] if state.target else "",
            "elapsed_ms": event.elapsed_ms,
        })
        t = _entra_correcao(domain, state)
        return Transition(t.state, t.action, (ev,) + t.events)

    if state.phase == CORRECAO:
        if not isinstance(event, StepAnswer):
            raise ValueError("CORRECAO espera StepAnswer, veio %s" % type(event).__name__)
        return _avanca_correcao(domain, state, event)

    if state.phase == CONCLUSAO:
        if not isinstance(event, Acknowledge):
            raise ValueError("CONCLUSAO espera Acknowledge, veio %s" % type(event).__name__)
        ev = Emit("stage_acknowledged", {
            "stage": "conclusion", "kc": state.kc,
            "node": domain.kcs[state.kc].conclusion_node,
            "elapsed_ms": event.elapsed_ms,
        })
        t = _entra_variacao(domain, state)
        return Transition(t.state, t.action, (ev,) + t.events)

    if state.phase == VARIACAO:
        if not isinstance(event, Answer):
            raise ValueError("VARIACAO espera Answer, veio %s" % type(event).__name__)
        return _responde_variacao(domain, state, event)

    if state.phase == FIM:
        return Transition(state, Action("done"))

    raise ValueError("fase desconhecida: %r" % state.phase)


# --------------------------------------------------------------------------
# Abertura de um KC
# --------------------------------------------------------------------------

def _abre_kc(domain: Domain, state: SessionState) -> Transition:
    """Entra no KC atual pela fase de diagnóstico.

    Se o KC já está dominado quando chega a vez dele — pode acontecer,
    porque um KC anterior confirma nós importados (RF07) — pula direto
    para a variação, que é o que fecha o KC (RF11).
    """
    kc = state.kc
    if kc is None:
        return _encerra(domain, state)

    novo = replace(state, phase=DIAGNOSTICO, diagnostics_done=0, rounds=0,
                   detected=None, target=None, plan=(), cursor=0, attempts={})

    if model.is_complete(domain, novo.vector, kc):
        return _entra_variacao(domain, novo)

    return _apresenta_diagnostica(domain, novo)


def _apresenta_diagnostica(domain: Domain, state: SessionState) -> Transition:
    kc = state.kc
    ciu = selector.next_diagnostic(
        domain, state.vector, kc, state.used_cius, state.last_ciu_type
    )
    if ciu is None:
        # Acabaram as diagnósticas: decide com o que já se sabe.
        return _decide_apos_diagnostico(domain, state)
    return _apresenta(domain, state, ciu, DIAGNOSTICO)


def _apresenta(domain: Domain, state: SessionState, ciu: CIU, fase: str) -> Transition:
    novo = replace(
        state,
        phase=fase,
        current_ciu=ciu.id,
        used_cius=state.used_cius + (ciu.id,) if ciu.id not in state.used_cius
        else state.used_cius,
        last_ciu_type=ciu.type,
    )
    evento = Emit("ciu_presented", {
        "ciu_id": ciu.id, "kc": ciu.kc, "targets": list(ciu.targets), "phase": ciu.phase,
        "type": ciu.type,
    })
    return Transition(novo, _acao_ciu(ciu), (evento,))


def _acao_ciu(ciu: CIU) -> Action:
    dados: dict[str, Any] = {
        "type": ciu.type, "phase": ciu.phase, "prompt": ciu.prompt,
    }
    if ciu.is_choice:
        dados["options"] = [{"text": o.text} for o in ciu.options]
    if ciu.type == "parsons":
        dados["steps"] = list(ciu.steps_correct)
    if ciu.type == "path_choice":
        dados["paths"] = [{"label": p.label, "steps": list(p.steps)} for p in ciu.paths]
    if ciu.visual:
        dados["visual"] = dict(ciu.visual)
    return Action("ciu", kc=ciu.kc, ciu_id=ciu.id, data=dados)


# --------------------------------------------------------------------------
# Diagnóstico
# --------------------------------------------------------------------------

def _responde_diagnostico(domain: Domain, state: SessionState, ev: Answer) -> Transition:
    ciu = domain.cius[ev.ciu_id]
    correto, mid = model.detect(ciu, ev.option_idx, ev.text)
    updates = model.ingest(domain, state.vector, ciu, correto, ev.confidence, mid)
    vetor = model.apply(state.vector, updates)

    # O distrator escolhido vai para o log SEMPRE: é o dado cru da
    # validação da Q-matrix, e independe de confiança.
    eventos = [Emit("answer_submitted", {
        "ciu_id": ciu.id, "kc": ciu.kc, "option_idx": ev.option_idx,
        "text": list(ev.text) if isinstance(ev.text, tuple) else ev.text,
        "confidence": ev.confidence, "elapsed_ms": ev.elapsed_ms,
        "correct": correto, "misconception_id": mid,
        "node_updates": [u.as_payload() for u in updates],
    })]

    # Mas CRENÇA DETECTADA é outra coisa. Escolher um distrator no chute
    # não é evidência de sustentar a crença: contá-la ali inflaria a
    # frequência de cada crença na população (§5.2) e acionaria uma
    # refutação socrática contra algo que o aluno não pensa.
    ativa = mid if (mid and not correto
                    and ev.confidence != domain.study.guessed) else None
    if ativa:
        m = domain.misconceptions[ativa]
        eventos.append(Emit("misconception_detected",
                            {"misconception_id": ativa, "kc": m.kc, "node": m.node}))

    novo = replace(state, vector=vetor, diagnostics_done=state.diagnostics_done + 1,
                   detected=state.detected or ativa)

    # Nenhum feedback é dado nesta fase (§6): só se decide se apresenta
    # mais uma diagnóstica ou se parte para a correção.
    teto = domain.study.max_diagnostics_per_kc
    para_cedo = (domain.study.diagnostic_policy == "until_misconception"
                 and novo.detected is not None)
    if novo.diagnostics_done < teto and not para_cedo:
        proxima = _apresenta_diagnostica(domain, novo)
        return Transition(proxima.state, proxima.action, tuple(eventos) + proxima.events)

    decidida = _decide_apos_diagnostico(domain, novo)
    return Transition(decidida.state, decidida.action, tuple(eventos) + decidida.events)


def _decide_apos_diagnostico(domain: Domain, state: SessionState) -> Transition:
    """A ramificação do §6, lida do vetor — não classificada (§7.2)."""
    kc = state.kc
    estado_cognitivo = model.cognitive_state(domain, state.vector, kc)

    # DOMINADO é lido sobre os nós PRODUTIVOS, os mesmos que encerram o KC
    # (RF11). Usar o conjunto todo faria a sessão exigir nós que nenhum
    # traversal apresenta — e o participante nunca sairia do KC.
    if estado_cognitivo != model.MISCONCEPTION and model.is_complete(
            domain, state.vector, kc):
        return _entra_variacao(domain, state)

    alvo = _escolhe_alvo(domain, state, estado_cognitivo)
    return _corrige(domain, replace(state, target=alvo), alvo)


def _corrige(domain: Domain, state: SessionState, alvo: Ref) -> Transition:
    """Entra na correção pelo caminho certo para o tipo do nó (RF08).

    Ponto único: crença que nega nó-base não tem premissa anterior para
    confrontá-la, e só a observação direta reintroduz o fato. Antes isto
    vivia só na saída do diagnóstico, e a mesma crença detectada na CIU de
    variação ia direto ao traversal — sem o diagrama que ela exige.
    """
    if domain.node(*alvo).is_base and model.state_of(state.vector, *alvo) == model.WRONG:
        return _apresenta_confronto(domain, state)
    return _entra_correcao(domain, state)


def _escolhe_alvo(domain: Domain, state: SessionState, estado_cognitivo: str) -> Ref:
    """Onde intervir, conforme o estado lido (§7.2)."""
    kc = state.kc

    if estado_cognitivo == model.MISCONCEPTION:
        # O nó errado. Se houver mais de um, o mais raso: refutá-lo pode
        # arrastar os outros, e o plano dele é o mais curto.
        errados = model.wrong_nodes(domain, state.vector, kc)
        return min(
            ((kc, n) for n in errados),
            key=lambda r: (len(socratic.full_plan(domain, *r)), r[1]),
        )

    # LACUNA e DESCONHECIMENTO miram a CONCLUSÃO, não um nó isolado.
    #
    # Não é atalho: o plano até a conclusão, filtrado pelos nós já
    # confirmados, COMEÇA exatamente na fronteira — a pós-ordem descarta
    # o que ele já demonstrou. "Ancorar na última premissa correta e
    # avançar pela fronteira" (§6) cai da estrutura, sem escolher nó a mão.
    #
    # Mirar um nó da fronteira por vez faria a sessão confirmar um nó por
    # rodada e voltar à variação entre cada um.
    return domain.kcs[kc].conclusion_ref


def _apresenta_confronto(domain: Domain, state: SessionState) -> Transition:
    """CONFRONTO VISUAL antes do traversal (RF08).

    Dois estados, alternados pelo aluno — nunca animação automática. O
    evento `diagram_toggled` só tem sentido se a ação for dele, e é o que
    transforma o apelo visual em dado (§5.2).
    """
    kc = state.kc
    com_visual = [c for c in domain.cius_of(kc) if c.visual]
    visual = dict(com_visual[0].visual) if com_visual else {}
    m = domain.misconceptions.get(state.detected or "")
    acao = Action(
        "diagram", kc=kc, node=state.target[1] if state.target else None,
        text=m.belief if m else None,
        data={"visual": visual, "controlled_by": "student"},
    )
    return Transition(replace(state, phase=CONFRONTO), acao)


# --------------------------------------------------------------------------
# Correção (§8: é aqui, e só aqui, que os braços diferem)
# --------------------------------------------------------------------------

def _entra_correcao(domain: Domain, state: SessionState) -> Transition:
    """Congela o plano e apresenta o primeiro passo.

    O plano é fixado agora e não recalculado: confirmar um nó no meio do
    traversal encolheria o plano sob os pés do aluno.
    """
    # Guarda dura: nenhuma forma do domínio pode prender um participante.
    # As rodadas normais são poucas (uma por crença, mais uma por variação
    # errada); estourar MAX_ROUNDS significa que o grafo tem um nó que
    # nenhum plano confirma, e o certo é registrar e seguir.
    if state.rounds >= MAX_ROUNDS:
        pendentes = model.pending_nodes(domain, state.vector, state.kc)
        evento = Emit("kc_incomplete", {
            "kc": state.kc, "node": pendentes[0] if pendentes else "",
            "attempts": state.rounds, "reason": "limite de rodadas de correcao",
        })
        novo = replace(state, kc_status={**state.kc_status, state.kc: EM_PROGRESSO})
        seguinte = _proximo_kc(domain, novo)
        return Transition(seguinte.state, seguinte.action, (evento,) + seguinte.events)

    alvo = state.target or domain.kcs[state.kc].conclusion_ref
    plano = tuple(socratic.plan(
        domain, alvo[0], alvo[1], model.confirmed_refs(state.vector)
    ))
    novo = replace(state, phase=CORRECAO, target=alvo, plan=plano, cursor=0,
                   attempts={}, rounds=state.rounds + 1)
    return _apresenta_passo(domain, novo)


def _passos(domain: Domain, state: SessionState) -> list[socratic.Step]:
    return socratic.steps_from(domain, state.plan)


def _apresenta_passo(domain: Domain, state: SessionState,
                     prompt: str | None = None) -> Transition:
    passos = _passos(domain, state)
    if state.cursor >= len(passos):
        # Fim do plano. Antes de concluir, verifica se o KC está de fato
        # erguido: refutar a crença fecha a cadeia DELA, não a cadeia até
        # a conclusão. Sem isto o aluno via duas conclusões e a mesma CIU
        # de variação duas vezes — uma por rodada de correção.
        if not model.is_complete(domain, state.vector, state.kc)                 and state.rounds < MAX_ROUNDS:
            restante = tuple(socratic.plan(
                domain, state.kc, domain.kcs[state.kc].conclusion_node,
                model.confirmed_refs(state.vector)))
            if restante and restante != state.plan:
                novo = replace(state, target=domain.kcs[state.kc].conclusion_ref,
                               plan=restante, cursor=0, attempts={},
                               rounds=state.rounds + 1)
                return _apresenta_passo(domain, novo)
        return _entra_conclusao(domain, state)

    passo = passos[state.cursor]
    socratico = state.arm == strategy.ARM_SOCRATIC

    if socratico:
        acao = Action("ask", kc=passo.kc, node=passo.node,
                      text=prompt or passo.question,
                      step_idx=passo.idx, step_total=passo.total,
                      data={"node_kind": passo.kind})
        evento = Emit("socratic_step_shown", {
            "kc": passo.kc, "node": passo.node, "kind": passo.kind,
            "step_idx": passo.idx, "total": passo.total,
        })
    else:
        acao = Action("explain", kc=passo.kc, node=passo.node, text=passo.text,
                      step_idx=passo.idx, step_total=passo.total,
                      data={"node_kind": passo.kind})
        evento = Emit("direct_explanation_shown", {
            "kc": passo.kc, "node": passo.node, "elapsed_ms": 0,
            "step_idx": passo.idx, "total": passo.total,
        })  # apresentação; o tempo de exposição vem no acknowledged
    return Transition(state, acao, (evento,))


def _avanca_correcao(domain: Domain, state: SessionState, ev: StepAnswer) -> Transition:
    """O coração do invariante do §6.

    Só existem três saídas daqui: todos os nós do plano confirmados, o
    limite de tentativas atingido, ou continuar dentro da correção.
    """
    passos = _passos(domain, state)
    passo = passos[state.cursor]
    ref = passo.ref
    socratico = state.arm == strategy.ARM_SOCRATIC

    # Braço B não tem caminho de erro: o aluno lê e confirma. A regressão
    # só existe onde há geração ativa — que é justamente a variável isolada.
    if not socratico or ev.accepted:
        updates = [model.Update(ref[0], ref[1], model.CONFIRMED)]
        vetor = model.apply(state.vector, updates)
        # Simétrico de propósito: cada braço tem um evento de apresentação
        # e um de resposta, os dois com o mesmo par (kc, node) e o mesmo
        # `elapsed_ms`. É o que permite parear tempo em tarefa entre A e B
        # (§8) sem depender de contar eventos de tipos diferentes.
        evento = Emit(
            "socratic_step_answered" if socratico else "explanation_acknowledged",
            {"kc": ref[0], "node": ref[1], "accepted": True,
             "elapsed_ms": ev.elapsed_ms,
             "node_updates": [u.as_payload() for u in updates]},
        )
        novo = replace(state, vector=vetor, cursor=state.cursor + 1)
        seguinte = _apresenta_passo(domain, novo)
        return Transition(seguinte.state, seguinte.action, (evento,) + seguinte.events)

    # Errou (só braço A). §7.4.
    tentativas = dict(state.attempts)
    ja = tentativas.get(ref, 0)
    reg = socratic.on_wrong(domain, passos, state.cursor, ja)
    tentativas[ref] = reg.attempts

    eventos = [Emit("socratic_step_answered", {
        "kc": ref[0], "node": ref[1], "accepted": False, "elapsed_ms": ev.elapsed_ms,
        "attempt": reg.attempts,
    })]

    if reg.action == "abandon":
        eventos.append(Emit("kc_incomplete", {
            "kc": state.kc, "node": ref[1], "attempts": reg.attempts,
        }))
        novo = replace(state, attempts=tentativas,
                       kc_status={**state.kc_status, state.kc: EM_PROGRESSO})
        seguinte = _proximo_kc(domain, novo)
        return Transition(seguinte.state, seguinte.action, tuple(eventos) + seguinte.events)

    if reg.action == "regress":
        eventos.append(Emit("regression_triggered", {
            "from_node": reg.from_node, "to_node": reg.to_node, "kc": state.kc,
        }))

    novo = replace(state, cursor=reg.cursor, attempts=tentativas)
    seguinte = _apresenta_passo(domain, novo, prompt=reg.prompt)
    return Transition(seguinte.state, seguinte.action, tuple(eventos) + seguinte.events)


# --------------------------------------------------------------------------
# Conclusão e variação
# --------------------------------------------------------------------------

def _entra_conclusao(domain: Domain, state: SessionState) -> Transition:
    """Nomeação tardia (RF10): o termo técnico aparece AQUI, e só aqui.

    Nada foi explicado antes; no braço A todas as premissas vieram de
    respostas do próprio aluno.
    """
    kc = state.kc
    concl = domain.kcs[kc].conclusion_node
    dados: dict[str, Any] = {
        # AQUI o texto vem SEM máscara: é o único ponto em que o termo
        # técnico pode aparecer, e é o que a nomeação tardia entrega.
        "conclusion_text": domain.node(kc, concl).text,
    }
    nome = domain.study.reveal_names.get(kc)
    if nome:
        dados["technical_name"] = nome
    acao = Action("conclude", kc=kc, text=socratic.conclusion(domain, kc),
                  node=concl, data=dados)
    return Transition(replace(state, phase=CONCLUSAO), acao)


def _entra_variacao(domain: Domain, state: SessionState) -> Transition:
    """RF11: mesmo invariante, código novo. É o que encerra o KC."""
    kc = state.kc
    ciu = selector.next_variation(domain, state.vector, kc,
                                 state.used_cius, state.last_ciu_type)
    if ciu is None:
        # Sem CIU de variação o KC não tem como ser encerrado. O validador
        # avisa antes da coleta; aqui a sessão não pode travar por isso.
        novo = replace(state, kc_status={**state.kc_status, kc: EM_PROGRESSO})
        evento = Emit("kc_incomplete", {"kc": kc, "node": "", "attempts": 0,
                                        "reason": "sem CIU de variacao"})
        seguinte = _proximo_kc(domain, novo)
        return Transition(seguinte.state, seguinte.action, (evento,) + seguinte.events)
    return _apresenta(domain, replace(state, phase=VARIACAO), ciu, VARIACAO)


def _responde_variacao(domain: Domain, state: SessionState, ev: Answer) -> Transition:
    ciu = domain.cius[ev.ciu_id]
    correto, mid = model.detect(ciu, ev.option_idx, ev.text)
    updates = model.ingest(domain, state.vector, ciu, correto, ev.confidence, mid)
    vetor = model.apply(state.vector, updates)

    eventos = [Emit("answer_submitted", {
        "ciu_id": ciu.id, "kc": ciu.kc, "option_idx": ev.option_idx,
        "text": list(ev.text) if isinstance(ev.text, tuple) else ev.text,
        "confidence": ev.confidence, "elapsed_ms": ev.elapsed_ms,
        "correct": correto, "misconception_id": mid, "phase": "variation",
        "node_updates": [u.as_payload() for u in updates],
    })]
    novo = replace(state, vector=vetor)

    if correto and model.is_complete(domain, vetor, state.kc):
        eventos.append(Emit("kc_completed", {
            "kc": state.kc, "elapsed_ms": ev.elapsed_ms,
            "vector": {n: model.state_of(vetor, state.kc, n)
                       for n in domain.kcs[state.kc].nodes},
        }))
        novo = replace(novo, kc_status={**novo.kc_status, state.kc: COMPLETO})
        seguinte = _proximo_kc(domain, novo)
        return Transition(seguinte.state, seguinte.action, tuple(eventos) + seguinte.events)

    if correto:
        # Acertou a variação mas o vetor não fechou: ainda há premissa não
        # confirmada. Volta para a correção mirando o que falta.
        alvo = _escolhe_alvo(domain, novo, model.cognitive_state(domain, vetor, state.kc))
        seguinte = _corrige(domain, replace(novo, target=alvo), alvo)
        return Transition(seguinte.state, seguinte.action, tuple(eventos) + seguinte.events)

    if mid:
        m = domain.misconceptions[mid]
        eventos.append(Emit("misconception_detected",
                            {"misconception_id": mid, "kc": m.kc, "node": m.node}))

    # §6: errou a variação -> rodada socrática focada SÓ na premissa que
    # não generalizou. O progresso confirmado não é descartado.
    alvo = _premissa_que_falhou(domain, novo, ciu, mid)
    seguinte = _corrige(
        domain, replace(novo, target=alvo, detected=mid or novo.detected), alvo)
    return Transition(seguinte.state, seguinte.action, tuple(eventos) + seguinte.events)


def _premissa_que_falhou(domain: Domain, state: SessionState,
                         ciu: CIU, mid: str | None) -> Ref:
    """O nó a reconstruir depois de errar a variação.

    Se a crença foi identificada, é o nó que ela nega. Senão, o alvo da
    CIU que ainda não está confirmado — a premissa que não generalizou.
    """
    if mid and mid in domain.misconceptions:
        return domain.misconceptions[mid].negates
    for t in ciu.targets:
        if model.state_of(state.vector, ciu.kc, t) != model.CONFIRMED:
            return (ciu.kc, t)
    return domain.kcs[ciu.kc].conclusion_ref


# --------------------------------------------------------------------------
# Encadeamento e encerramento
# --------------------------------------------------------------------------

def _proximo_kc(domain: Domain, state: SessionState) -> Transition:
    """RF16: encadeia os KCs da sequência, na ordem de prerequisito."""
    novo = replace(state, kc_index=state.kc_index + 1, current_ciu=None,
                   detected=None, target=None, plan=(), cursor=0, attempts={})
    if novo.kc is None:
        return _encerra(domain, novo)
    return _abre_kc(domain, novo)


def _encerra(domain: Domain, state: SessionState) -> Transition:
    completos = sum(1 for s in state.kc_status.values() if s == COMPLETO)
    evento = Emit("session_ended", {
        "reason": "concluida" if completos == len(state.kc_sequence) else "parcial",
        "total_ms": 0,
        "kc_status": dict(state.kc_status),
    })
    acao = Action("done", data={
        "kc_status": dict(state.kc_status),
        "completed": completos,
        "total": len(state.kc_sequence),
    })
    return Transition(replace(state, phase=FIM), acao, (evento,))
