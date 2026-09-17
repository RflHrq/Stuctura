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

import hashlib
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from engine import feedback as fb, model, selector, socratic, strategy
from engine.loader import CIU, Domain, Ref

# Fases da sessão (§6).
ABERTA = "ABERTA"
INTRO = "INTRO"
DIAGNOSTICO = "DIAGNOSTICO"
CONFRONTO = "CONFRONTO"
CORRECAO = "CORRECAO"
CONCLUSAO = "CONCLUSAO"
# KC deixado em aberto: o aluno recusou o mesmo passo três vezes, estourou
# o limite de rodadas, ou o domínio não tinha como fechar o tópico. Antes
# a sessão pulava direto para o KC seguinte, e a pessoa saía dali com a
# crença com que entrou. Agora ela lê a frase certa antes de seguir.
FECHAMENTO = "FECHAMENTO"
# SONDAGEM: a escolha entre o enunciado do nó e o que a crença afirma,
# apresentada ANTES do passo que derruba a crença. Uma por KC, nos dois
# braços. Ver `_talvez_sondagem`.
SONDAGEM = "SONDAGEM"
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
    # Semente do embaralhamento das alternativas. É o id da sessão, então
    # a ordem é a mesma em toda reconstrução do log (RNF06) e diferente
    # entre participantes.
    seed: str = ""
    kc_index: int = 0
    phase: str = ABERTA
    vector: Mapping[Ref, str] = field(default_factory=dict)

    # Introdução (§ intro.yaml): cartão corrente. Fica no estado para que
    # a sessão retomada volte ao mesmo cartão, não ao começo.
    intro_index: int = 0

    # Diagnóstico
    diagnostics_done: int = 0
    # Acertos seguidos com a confiança mais alta, ao longo da SESSÃO (não
    # zera ao trocar de KC). É o que sobe o nível mínimo das diagnósticas.
    # Não é persistido à parte: a retomada o reconstrói reexecutando as
    # respostas, como todo o resto do estado.
    sequencia_certa: int = 0
    # Maior nível já apresentado NESTE KC. O piso diz de onde o aluno parte;
    # este campo é o teto, e sobe um degrau por atividade: é o que impede o
    # KC de pular do nível 1 para o 3. Zera a cada KC.
    nivel_visto: int = 0
    used_cius: tuple[str, ...] = ()
    last_ciu_type: str | None = None
    current_ciu: str | None = None

    # Correção
    detected: str | None = None            # misconception_id
    target: Ref | None = None              # nó que o traversal vai reconstruir
    plan: tuple[Ref, ...] = ()             # congelado ao entrar na correção
    # Diagrama que acompanha ESTA correção, quando ela veio de um confronto
    # visual. Fica no estado para que a pergunta possa dizer "olhando o
    # diagrama" apenas quando há um — e para que ele siga visível durante o
    # traversal, que é onde o aluno precisa dele para confirmar nós-base.
    visual: Mapping[str, Any] | None = None
    cursor: int = 0
    attempts: Mapping[Ref, int] = field(default_factory=dict)
    # Nós já sondados nesta sessão. A sondagem acontece UMA vez por nó: ela
    # mede o que o aluno produz antes de o sistema falar, e repeti-la depois
    # da refutação mediria memória da tela anterior.
    probed: tuple[Ref, ...] = ()
    rounds: int = 0                        # rodadas de correção neste KC

    # Encerramento
    kc_status: Mapping[str, str] = field(default_factory=dict)
    # Soma dos `elapsed_ms` que o aluno gastou nas telas. NAO e a diferenca
    # entre carimbos de tempo: uma pausa para o pesquisador falar, ou a aba
    # aberta durante o intervalo, nao entram. E o que o §8 quer parear.
    total_ms: int = 0

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

def start(domain: Domain, arm: str, kc_sequence: Sequence[str],
          seed: str = "") -> Transition:
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
    estado = SessionState(arm=arm, kc_sequence=ordem, seed=seed, phase=DIAGNOSTICO)
    # A introdução vem antes de tudo, e é idêntica nos dois braços — vem
    # antes de eles divergirem, então a simetria do §8.1 é estrutural.
    if domain.intro:
        return _apresenta_intro(domain, replace(estado, phase=INTRO))
    return _abre_kc(domain, estado)


def advance(domain: Domain, state: SessionState, event: Event) -> Transition:
    """(estado, evento) -> (estado, ação, eventos). Único ponto de decisão."""
    # O tempo se acumula das ENTRADAS, não de um relógio: a FSM continua
    # pura e a sessão retomada soma exatamente o mesmo total.
    state = replace(state, total_ms=state.total_ms + max(0, event.elapsed_ms))

    if state.phase == INTRO:
        if not isinstance(event, Acknowledge):
            raise ValueError("INTRO espera Acknowledge, veio %s" % type(event).__name__)
        cartao = domain.intro[state.intro_index]
        ev = Emit("stage_acknowledged", {
            "stage": "intro", "kc": "", "card": cartao.id,
            "card_index": state.intro_index + 1, "total": len(domain.intro),
            "elapsed_ms": event.elapsed_ms,
        })
        seguinte = replace(state, intro_index=state.intro_index + 1)
        if seguinte.intro_index >= len(domain.intro):
            t = _abre_kc(domain, replace(seguinte, phase=DIAGNOSTICO))
        else:
            t = _apresenta_intro(domain, seguinte)
        return Transition(t.state, t.action, (ev,) + t.events)
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

    if state.phase == FECHAMENTO:
        if not isinstance(event, Acknowledge):
            raise ValueError("FECHAMENTO espera Acknowledge, veio %s"
                             % type(event).__name__)
        ev = Emit("stage_acknowledged", {
            "stage": "closure", "kc": state.kc,
            "node": domain.kcs[state.kc].conclusion_node,
            "elapsed_ms": event.elapsed_ms,
        })
        t = _proximo_kc(domain, state)
        return Transition(t.state, t.action, (ev,) + t.events)

    if state.phase == SONDAGEM:
        if not isinstance(event, Answer):
            raise ValueError("SONDAGEM espera Answer, veio %s" % type(event).__name__)
        return _responde_sondagem(domain, state, event)

    if state.phase == VARIACAO:
        if not isinstance(event, Answer):
            raise ValueError("VARIACAO espera Answer, veio %s" % type(event).__name__)
        return _responde_variacao(domain, state, event)

    if state.phase == FIM:
        return Transition(state, Action("done"))

    raise ValueError("fase desconhecida: %r" % state.phase)


def _apresenta_intro(domain: Domain, state: SessionState) -> Transition:
    """Um cartão da introdução. Não emite evento ao APRESENTAR — só ao ser
    confirmado, que é quando existe um tempo de leitura para registrar."""
    cartao = domain.intro[state.intro_index]
    dados = cartao.as_json()
    dados["index"] = state.intro_index + 1
    dados["total"] = len(domain.intro)
    return Transition(state, Action("intro", text=cartao.title, data=dados))


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
                   nivel_visto=0,
                   detected=None, target=None, plan=(), cursor=0, attempts={},
                   visual=None)

    if model.is_complete(domain, novo.vector, kc):
        return _entra_variacao(domain, novo)

    return _apresenta_diagnostica(domain, novo)


def _apresenta_diagnostica(domain: Domain, state: SessionState) -> Transition:
    kc = state.kc
    piso = selector.nivel_minimo(domain, state.sequencia_certa)
    ciu = selector.next_diagnostic(
        domain, state.vector, kc, state.used_cius, state.last_ciu_type,
        nivel_minimo=piso,
        garantir_uma=state.diagnostics_done == 0,
        # Um degrau por vez dentro do KC, a partir de onde o piso permitiu
        # entrar. Ver `nivel_visto`.
        nivel_maximo=max(state.nivel_visto + 1, piso),
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
        nivel_visto=max(state.nivel_visto, ciu.nivel),
    )
    ordem = option_order(domain, state.seed, ciu)
    evento = Emit("ciu_presented", {
        "ciu_id": ciu.id, "kc": ciu.kc, "targets": list(ciu.targets), "phase": ciu.phase,
        "type": ciu.type,
        # `phase` é a do CATÁLOGO; esta é a da SESSÃO. As duas divergem no
        # reteste: sem atividade de variação que ofereça a crença refutada,
        # quem fecha o KC é uma diagnóstica que a ofereça. Sem este campo, a
        # análise leria "diagnostic" e contaria uma tela de fechamento como
        # tela de diagnóstico.
        "session_phase": fase,
        # Qual crença esta atividade está reperguntando, se for o caso.
        # É o que permite ler no log, sem reconstruir nada, que aquela tela
        # era a medida de correção e não uma atividade qualquer.
        "retest_of": _reteste_de(domain, state, ciu),
        # O nível e o piso vão para o log: a análise precisa saber quem foi
        # desafiado e quem foi levado pela mão, e por quê.
        "nivel": ciu.nivel,
        "sequencia_certa": state.sequencia_certa,
        "nivel_minimo": selector.nivel_minimo(domain, state.sequencia_certa),
        # A permutação vai para o log: a análise não precisa rededuzi-la, e
        # fica registrado o que este participante viu, nesta posição.
        "option_order": list(ordem),
    })
    return Transition(novo, _acao_ciu(ciu, ordem), (evento,))


def _reteste_de(domain: Domain, state: SessionState, ciu: CIU) -> str | None:
    """A crença que esta atividade repergunta, ou None.

    Só há reteste depois de uma refutação: a crença precisa ter sido
    detectada neste KC, e a atividade precisa oferecê-la de novo, noutra
    superfície. É a medida de correção dentro da sessão — sem ela, dá para
    dizer que o aluno percorreu a refutação, não que ele mudou de ideia.
    """
    crenca = state.detected
    if not crenca:
        return None
    return crenca if crenca in selector.beliefs_of(ciu) else None


def option_order(domain: Domain, seed: str, ciu: CIU) -> tuple[int, ...]:
    """A ordem em que as alternativas de `ciu` são exibidas nesta sessão.

    Devolve os índices CANÔNICOS na ordem de exibição. Fisher-Yates guiado
    por um digest de (semente, id da atividade): mesma entrada, mesma
    ordem, sempre — sem `random`, que traria estado e quebraria o replay.

    `hash()` do Python NÃO serve: é salgado por processo, então reiniciar
    o servidor no meio da coleta mudaria a ordem de quem retomasse.
    """
    n = len(ciu.options)
    ordem = list(range(n))
    if not domain.study.shuffle_options or n < 2 or not seed:
        return tuple(ordem)

    digest = hashlib.sha256(("%s|%s" % (seed, ciu.id)).encode("utf-8")).digest()
    for i in range(n - 1, 0, -1):
        j = digest[(n - 1 - i) % len(digest)] % (i + 1)
        ordem[i], ordem[j] = ordem[j], ordem[i]
    return tuple(ordem)


def _acao_ciu(ciu: CIU, ordem: Sequence[int] = ()) -> Action:
    dados: dict[str, Any] = {
        "type": ciu.type, "phase": ciu.phase, "prompt": ciu.prompt,
    }
    if ciu.is_choice:
        exibicao = list(ordem) or list(range(len(ciu.options)))
        dados["options"] = [{"text": ciu.options[i].text} for i in exibicao]
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

def _canonico(domain: Domain, state: SessionState, ciu: CIU,
              exibido: int | None) -> tuple[int | None, list[int]]:
    """Traduz o índice EXIBIDO para o índice canônico do YAML.

    O cliente devolve a posição em que o aluno clicou; o catálogo, a
    Q-matrix e todo o `answers.csv` falam em índice canônico. Sem esta
    tradução, embaralhar faria o sistema diagnosticar a crença ERRADA —
    silenciosamente, e em toda a coleta.
    """
    ordem = list(option_order(domain, state.seed, ciu))
    if exibido is None or not ciu.is_choice:
        return exibido, ordem
    if not (0 <= exibido < len(ordem)):
        raise ValueError(
            "CIU %s: posição %r fora das %d alternativas exibidas"
            % (ciu.id, exibido, len(ordem))
        )
    return ordem[exibido], ordem


def _sequencia(domain: Domain, state: SessionState, correto: bool,
              confianca: str) -> int:
    """Acertos seguidos com certeza. Qualquer outra resposta zera.

    Acerto com "acho que sei" também zera, de propósito: o desafio sobe para
    quem SABE que sabe. Quem acerta hesitando ainda está construindo, e é
    justamente quem precisa do degrau mais leve.
    """
    if correto and confianca == domain.study.certain:
        return state.sequencia_certa + 1
    return 0


def _responde_diagnostico(domain: Domain, state: SessionState, ev: Answer) -> Transition:
    ciu = domain.cius[ev.ciu_id]
    canonico, ordem = _canonico(domain, state, ciu, ev.option_idx)
    correto, mid = model.detect(ciu, canonico, ev.text)
    updates = model.ingest(domain, state.vector, ciu, correto, ev.confidence, mid)
    vetor = model.apply(state.vector, updates)

    # O distrator escolhido vai para o log SEMPRE: é o dado cru da
    # validação da Q-matrix, e independe de confiança.
    #
    # `option_idx` é o índice CANÔNICO — é o que o catálogo e a análise
    # falam. `displayed_idx` é a posição em que a alternativa apareceu para
    # este participante, e permite medir viés de posição em vez de só
    # eliminá-lo.
    eventos = [Emit("answer_submitted", {
        "ciu_id": ciu.id, "kc": ciu.kc, "option_idx": canonico,
        "displayed_idx": ev.option_idx, "option_order": ordem,
        "text": list(ev.text) if isinstance(ev.text, tuple) else ev.text,
        "confidence": ev.confidence, "elapsed_ms": ev.elapsed_ms,
        "correct": correto, "misconception_id": mid,
        "session_phase": state.phase,
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
                   detected=state.detected or ativa,
                   sequencia_certa=_sequencia(domain, state, correto, ev.confidence))

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
    # O diagrama segue para a correção: RF08 existe porque só a observação
    # direta reintroduz um fato-base, e tirá-lo da tela justo quando o aluno
    # vai confirmar esses fatos desfaria o efeito.
    return Transition(replace(state, phase=CONFRONTO, visual=visual or None), acao)


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
        return _fecha_em_aberto(
            domain, state, "limite de rodadas de correcao",
            node=pendentes[0] if pendentes else "", attempts=state.rounds)

    alvo = state.target or domain.kcs[state.kc].conclusion_ref
    plano = tuple(socratic.plan(
        domain, alvo[0], alvo[1], model.confirmed_refs(state.vector)
    ))
    novo = replace(state, phase=CORRECAO, target=alvo, plan=plano, cursor=0,
                   attempts={}, rounds=state.rounds + 1)
    t = _apresenta_passo(domain, novo)
    # RF17 etapa 1: reconhecer o que há de legítimo, ANTES de refutar. Vai
    # junto do primeiro passo, nos dois braços.
    if state.rounds == 0:
        validacao = fb.validation(domain, state.vector, state.kc, state.detected)
        if validacao:
            t = Transition(t.state, _com_feedback(t.action, validacao), t.events)
    return t


def _passos(domain: Domain, state: SessionState) -> list[socratic.Step]:
    return socratic.steps_from(domain, state.plan, with_diagram=bool(state.visual))


def _dados_do_passo(state: SessionState, passo: socratic.Step) -> dict[str, Any]:
    """O que acompanha o enunciado na tela. Idêntico nos dois braços (§8.1).

    Duas figuras podem disputar o mesmo espaço:

      `visual`  o diagrama do confronto RF08. É manipulação experimental —
                entra só nos nós-base, que são onde a pergunta manda olhar.
      `figure`  a analogia do próprio nó, que vem do grafo.

    Quando as duas existem, o diagrama vence: ele é o que o RF08 exige que
    o aluno observe, e duas ilustrações lado a lado dividiriam a atenção
    justamente no passo em que ela importa (§10.1).
    """
    dados: dict[str, Any] = {"node_kind": passo.kind}
    if state.visual and passo.kind == "base":
        dados["visual"] = dict(state.visual)
    elif passo.figure:
        dados["figure"] = dict(passo.figure)
    return dados


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

    # SONDAGEM antes do passo que derruba a crença, e antes de o sistema
    # dizer qualquer coisa sobre aquele nó.
    sonda = _talvez_sondagem(domain, state, passo)
    if sonda is not None:
        return sonda

    socratico = state.arm == strategy.ARM_SOCRATIC

    if socratico:
        dados = _dados_do_passo(state, passo)
        acao = Action("ask", kc=passo.kc, node=passo.node,
                      text=prompt or passo.question,
                      step_idx=passo.idx, step_total=passo.total,
                      data=dados)
        acao = _talvez_contradicao(domain, state, passo, acao)
        evento = Emit("socratic_step_shown", {
            "kc": passo.kc, "node": passo.node, "kind": passo.kind,
            "step_idx": passo.idx, "total": passo.total,
        })
    else:
        dados = _dados_do_passo(state, passo)      # idêntico ao braço A (§8.1)
        acao = Action("explain", kc=passo.kc, node=passo.node, text=passo.text,
                      step_idx=passo.idx, step_total=passo.total,
                      data=dados)
        acao = _talvez_contradicao(domain, state, passo, acao)
        evento = Emit("direct_explanation_shown", {
            "kc": passo.kc, "node": passo.node, "elapsed_ms": 0,
            "step_idx": passo.idx, "total": passo.total,
        })  # apresentação; o tempo de exposição vem no acknowledged
    return Transition(state, acao, (evento,))


def _talvez_sondagem(domain: Domain, state: SessionState,
                     passo: socratic.Step) -> Transition | None:
    """A única tela do percurso em que o aluno PRODUZ, em vez de concordar.

    O percurso ergue a cadeia premissa por premissa, e cada passo põe a
    frase na tela e pede confirmação. Isso basta para construir, mas não
    mede: clicar em "Sim, confirmo" é indistinguível de saber (ver
    `model.ACCEPTED`). Aqui, no nó que a crença nega — e só nele —, o
    sistema pergunta ANTES de dizer: das duas frases, qual segue do que
    você confirmou?

    As duas alternativas saem do próprio domínio: o enunciado do nó e o que
    a crença afirma. Nenhuma foi escrita para esta tela.

    Acontece nos DOIS braços, na mesma posição e com o mesmo texto. É
    medida, não tratamento — o que muda entre os braços continua sendo o
    passo seguinte: pergunta no A, afirmação no B.

    Sem confiança declarada, de propósito: a escolha não é "o quanto você
    sabe", é "o que você diz que segue daqui". Uma escala a mais dentro do
    percurso cobraria duas decisões do aluno no meio de uma cadeia.
    """
    crenca = state.detected
    if not crenca or crenca not in domain.misconceptions:
        return None
    if passo.ref != domain.misconceptions[crenca].negates:
        return None
    if passo.ref in state.probed:
        return None

    pergunta, (frase_no, frase_crenca) = socratic.probe(
        domain, passo.kc, passo.node, crenca)
    ordem = _ordem_da_sondagem(state.seed, passo.ref)
    frases = (frase_no, frase_crenca)
    novo = replace(state, phase=SONDAGEM, probed=state.probed + (passo.ref,))
    # O MESMO material do passo: o diagrama do confronto (RF08) quando há um,
    # ou a figura do nó. A sondagem de um nó-base acontece logo depois do
    # confronto visual, e perguntar "qual destas duas é o que acontece?" com
    # o diagrama fora da tela mandaria o aluno decidir no vácuo.
    dados = dict(_dados_do_passo(state, passo))
    dados.update({"options": [{"text": frases[i]} for i in ordem],
                  "misconception_id": crenca})
    acao = Action("probe", kc=passo.kc, node=passo.node, text=pergunta,
                  step_idx=passo.idx, step_total=passo.total, data=dados)
    evento = Emit("probe_shown", {
        "kc": passo.kc, "node": passo.node, "misconception_id": crenca,
        "option_order": list(ordem), "arm": state.arm,
    })
    return Transition(novo, acao, (evento,))


def _ordem_da_sondagem(seed: str, ref: Ref) -> tuple[int, ...]:
    """Qual das duas frases aparece primeiro. Determinístico (RNF02).

    Mesma semente e mesmo nó, mesma ordem — inclusive quando a sessão é
    reconstruída do log. Sem isto, a posição da frase certa seria sempre a
    mesma e o aluno poderia responder pela posição.
    """
    if not seed:
        return (0, 1)
    digest = hashlib.sha256(("%s|probe|%s:%s" % (seed, ref[0], ref[1]))
                            .encode("utf-8")).digest()
    return (0, 1) if digest[0] % 2 == 0 else (1, 0)


def _responde_sondagem(domain: Domain, state: SessionState, ev: Answer) -> Transition:
    """Registra o que o aluno produziu e segue para o passo, sem mudá-lo.

    A sondagem NÃO desvia o fluxo: escolher a frase certa não pula a
    refutação, e escolher a crença não acrescenta nada. Ela é medida —
    desviar o percurso conforme a resposta faria dela tratamento, e aí o
    que o braço A e o braço B recebem deixaria de ser o mesmo.

    O que ela muda é o VETOR: acertar aqui é evidência produzida pelo
    aluno, e o nó passa a `confirmed` em vez do `accepted` que o clique do
    passo deixaria. São duas alternativas, então metade acerta no chute —
    o evento registra a escolha, e a análise desconta isso se quiser.
    """
    passos = _passos(domain, state)
    passo = passos[state.cursor]
    ref = passo.ref
    crenca = state.detected

    ordem = _ordem_da_sondagem(state.seed, ref)
    exibido = ev.option_idx
    if exibido is None or not (0 <= exibido < 2):
        raise ValueError("sondagem em %s:%s: posição %r fora das duas alternativas"
                         % (ref[0], ref[1], exibido))
    canonico = ordem[exibido]          # 0 = frase do nó, 1 = frase da crença
    escolheu_o_no = canonico == 0

    updates = ([model.Update(ref[0], ref[1], model.CONFIRMED)]
               if escolheu_o_no else [])
    vetor = model.apply(state.vector, updates)

    evento = Emit("probe_answered", {
        "kc": ref[0], "node": ref[1], "misconception_id": crenca,
        "chose": "node" if escolheu_o_no else "belief",
        "correct": escolheu_o_no, "displayed_idx": exibido,
        "elapsed_ms": ev.elapsed_ms, "arm": state.arm,
        "node_updates": [u.as_payload() for u in updates],
    })

    novo = replace(state, vector=vetor, phase=CORRECAO,
                   total_ms=state.total_ms + max(0, ev.elapsed_ms))
    seguinte = _apresenta_passo(domain, novo)
    return Transition(seguinte.state, seguinte.action, (evento,) + seguinte.events)


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
        # ACEITO, não CONFIRMADO: o aluno concordou com a premissa que lhe
        # foi posta, ou leu e seguiu. A cadeia se ergue com isso — o fluxo
        # é o mesmo de antes —, mas não é a mesma evidência que acertar uma
        # atividade que mira o nó, e o log precisa poder dizer qual das duas
        # aconteceu. Ver `model.ACCEPTED`.
        # Nó que o aluno JÁ demonstrou numa atividade não é rebaixado para
        # aceito por passar de novo por aqui. O percurso pula nó sustentado,
        # então isto é rede — mas é a rede que garante que a evidência mais
        # forte nunca se perde por ordem de eventos.
        ja = model.state_of(state.vector, ref[0], ref[1])
        novo_estado = model.CONFIRMED if ja == model.CONFIRMED else model.ACCEPTED
        updates = [model.Update(ref[0], ref[1], novo_estado)]
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
    reg = socratic.on_wrong(domain, passos, state.cursor, ja,
                            with_diagram=bool(state.visual))
    tentativas[ref] = reg.attempts

    eventos = [Emit("socratic_step_answered", {
        "kc": ref[0], "node": ref[1], "accepted": False, "elapsed_ms": ev.elapsed_ms,
        "attempt": reg.attempts,
    })]

    if reg.action == "abandon":
        fecho = _fecha_em_aberto(
            domain, replace(state, attempts=tentativas),
            "tentativas no mesmo no", node=ref[1], attempts=reg.attempts)
        return Transition(fecho.state, fecho.action, tuple(eventos) + fecho.events)

    if reg.action == "regress":
        eventos.append(Emit("regression_triggered", {
            "from_node": reg.from_node, "to_node": reg.to_node, "kc": state.kc,
        }))

    novo = replace(state, cursor=reg.cursor, attempts=tentativas)
    seguinte = _apresenta_passo(domain, novo, prompt=reg.prompt)
    return Transition(seguinte.state, seguinte.action, tuple(eventos) + seguinte.events)


def _com_feedback(acao: Action, f: fb.Feedback) -> Action:
    dados = dict(acao.data)
    dados["feedback"] = f.as_json()
    return replace(acao, data=dados)


def _talvez_contradicao(domain: Domain, state: SessionState,
                        passo: socratic.Step, acao: Action) -> Action:
    """RF17 etapa 2, e SÓ no nó que a crença nega.

    Ancorada no nó da CRENÇA, não no alvo corrente do traversal. São
    coisas diferentes: a partir da segunda rodada de correção o alvo passa
    a ser a conclusão do KC, e usá-lo faria a contradição reaparecer num
    ponto onde ela já foi resolvida — o aluno seria confrontado duas vezes
    com uma ideia que já abandonou.

    Como o nó da crença é confirmado na primeira rodada, ele some dos
    planos seguintes: a etapa acontece exatamente uma vez.
    """
    if not state.detected or state.detected not in domain.misconceptions:
        return acao
    if passo.ref != domain.misconceptions[state.detected].negates:
        return acao
    contra = fb.contradiction(domain, passo.kc, passo.node, state.detected)
    return _com_feedback(acao, contra) if contra else acao


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
    # RF17 etapa 3: dizer de ONDE a conclusão veio, não qual é.
    recon = fb.reconstruction(domain, kc, state.arm, houve_correcao=state.rounds > 0)
    if recon:
        acao = _com_feedback(acao, recon)
    return Transition(replace(state, phase=CONCLUSAO), acao)


def _fecha_em_aberto(domain: Domain, state: SessionState, motivo: str,
                     node: str = "", attempts: int = 0) -> Transition:
    """Deixa o KC em aberto — mas não deixa o aluno sem a frase certa.

    Ponto ÚNICO das três saídas por desistência: três recusas no mesmo nó,
    limite de rodadas de correção, e domínio sem atividade de variação.
    Antes cada uma pulava direto para o próximo KC, e quem travasse saía do
    tópico com a crença com que entrou, sem nunca ler o que a cadeia
    sustenta. Não dá para exigir que ele construa; dá para não deixá-lo
    sair sem saber.

    A tela NÃO revela o nome técnico: nomear é o fecho de quem construiu
    (RF10). E o evento `kc_incomplete` continua o mesmo, com o motivo — a
    análise não perde a diferença entre concluir e receber.
    """
    kc = state.kc
    evento = Emit("kc_incomplete", {
        "kc": kc, "node": node, "attempts": attempts, "reason": motivo,
    })
    dados: dict[str, Any] = {
        "conclusion_text": domain.study.mask(domain.kcs[kc].conclusion),
        # É o que faz a interface trocar o título: dizer "você acabou de
        # construir isto" a quem não construiu seria mentira na cara dele.
        "incomplete": True,
        "reason": motivo,
    }
    acao = Action("conclude", kc=kc, node=domain.kcs[kc].conclusion_node,
                  data=dados)
    fecho = fb.closure(domain, kc, state.detected)
    if fecho:
        acao = _com_feedback(acao, fecho)
    novo = replace(state, phase=FECHAMENTO,
                   kc_status={**state.kc_status, kc: EM_PROGRESSO})
    return Transition(novo, acao, (evento,))


def _entra_variacao(domain: Domain, state: SessionState) -> Transition:
    """RF11: mesmo invariante, código novo. É o que encerra o KC."""
    kc = state.kc
    # RETESTE: com crença refutada neste KC, quem fecha é, de preferência,
    # outra atividade que ofereça A MESMA crença. Ver `selector`.
    ciu = selector.next_variation(domain, state.vector, kc,
                                 state.used_cius, state.last_ciu_type,
                                 crenca=state.detected)
    if ciu is None:
        # Sem CIU de variação o KC não tem como ser encerrado. O validador
        # avisa antes da coleta; aqui a sessão não pode travar por isso.
        return _fecha_em_aberto(domain, state, "sem CIU de variacao")
    return _apresenta(domain, replace(state, phase=VARIACAO), ciu, VARIACAO)


def _responde_variacao(domain: Domain, state: SessionState, ev: Answer) -> Transition:
    ciu = domain.cius[ev.ciu_id]
    canonico, ordem = _canonico(domain, state, ciu, ev.option_idx)
    correto, mid = model.detect(ciu, canonico, ev.text)
    updates = model.ingest(domain, state.vector, ciu, correto, ev.confidence, mid)
    vetor = model.apply(state.vector, updates)

    eventos = [Emit("answer_submitted", {
        "ciu_id": ciu.id, "kc": ciu.kc, "option_idx": canonico,
        "displayed_idx": ev.option_idx, "option_order": ordem,
        "text": list(ev.text) if isinstance(ev.text, tuple) else ev.text,
        "confidence": ev.confidence, "elapsed_ms": ev.elapsed_ms,
        "correct": correto, "misconception_id": mid, "phase": "variation",
        "session_phase": state.phase,
        "retest_of": _reteste_de(domain, state, ciu),
        "node_updates": [u.as_payload() for u in updates],
    })]

    # O DESFECHO DE CORREÇÃO, num evento só: a crença foi refutada no
    # percurso e reaparece aqui noutra superfície. `still_held` é o aluno
    # escolhendo de novo a mesma ideia — o caso em que a refutação não
    # pegou. A confiança vai junto porque um acerto chutado não é correção.
    crenca_em_teste = _reteste_de(domain, state, ciu)
    if crenca_em_teste:
        eventos.append(Emit("belief_retested", {
            "misconception_id": crenca_em_teste, "ciu_id": ciu.id, "kc": ciu.kc,
            "still_held": (not correto) and mid == crenca_em_teste,
            "correct": correto, "chose": mid, "confidence": ev.confidence,
        }))

    novo = replace(state, vector=vetor,
                   sequencia_certa=_sequencia(domain, state, correto, ev.confidence))

    if correto and model.is_complete(domain, vetor, state.kc):
        eventos.append(Emit("kc_completed", {
            "kc": state.kc, "elapsed_ms": ev.elapsed_ms,
            # Só os nós que têm estado. Um nó que nenhuma resposta tocou não
            # aparece — antes ele entrava como `unknown`, e a projeção do
            # log, que só conhece os nós que algum evento mencionou, não
            # tinha como reproduzir essa chave. O checkpoint do RNF04
            # comparava um vetor com o outro e acusava divergência onde não
            # havia nenhuma. Nó ausente aqui significa nó nunca tocado.
            "vector": {n: model.state_of(vetor, state.kc, n)
                       for n in domain.kcs[state.kc].nodes
                       if model.state_of(vetor, state.kc, n) != model.UNKNOWN},
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
        "total_ms": state.total_ms,
        "kc_status": dict(state.kc_status),
    })
    acao = Action("done", data={
        "kc_status": dict(state.kc_status),
        "completed": completos,
        "total": len(state.kc_sequence),
    })
    return Transition(replace(state, phase=FIM), acao, (evento,))
