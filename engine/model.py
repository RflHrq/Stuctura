"""Vetor de premissas e leitura do estado cognitivo (RF03, RF04, §7.2, §7.3).

O estado é LIDO do vetor, não classificado. Sem BKT, sem limiar, sem
modelo estatístico: o padrão de estados dos nós responde sozinho qual é a
situação do aluno naquele KC. É o que torna o diagnóstico inspecionável
linha a linha na banca.

A confiança declarada faz o tratamento de ruído que o BKT faria: o mesmo
erro tem significado diagnóstico oposto conforme o aluno tenha chutado ou
tenha certeza. Nenhum parâmetro para calibrar.

Puro. Sem I/O. Recebe o domínio e um vetor; devolve leitura e deltas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from engine.loader import CIU, Domain, Ref

# Estados de um nó no vetor de premissas (§5.1).
UNKNOWN = "unknown"
CONFIRMED = "confirmed"
ABSENT = "absent"      # o aluno sabe que não sabe
WRONG = "wrong"        # crença ativa
NODE_STATES = (UNKNOWN, CONFIRMED, ABSENT, WRONG)

# Estados cognitivos possíveis num KC (§7.2).
DESCONHECIMENTO = "desconhecimento"
LACUNA = "lacuna"
MISCONCEPTION = "misconception"
DOMINADO = "dominado"

Vector = Mapping[Ref, str]


@dataclass(frozen=True, slots=True)
class Update:
    """Um delta no vetor. É o que vira `node_updates` no log de eventos."""

    kc: str
    node: str
    state: str

    @property
    def ref(self) -> Ref:
        return (self.kc, self.node)

    def as_payload(self) -> dict[str, str]:
        return {"kc": self.kc, "node": self.node, "state": self.state}


# --------------------------------------------------------------------------
# §7.2 Leitura do estado
# --------------------------------------------------------------------------

def state_of(vector: Vector, kc: str, node: str) -> str:
    return vector.get((kc, node), UNKNOWN)


def cognitive_state(domain: Domain, vector: Vector, kc: str) -> str:
    """Lê o estado do KC a partir do vetor. Ordem das regras importa.

    Um nó errado domina tudo: há crença ativa a refutar, e não adianta
    preencher lacuna por cima dela.
    """
    nos = domain.kcs[kc].nodes
    estados = [state_of(vector, kc, n) for n in nos]

    if any(e == WRONG for e in estados):
        return MISCONCEPTION
    if all(e == CONFIRMED for e in estados):
        return DOMINADO
    if not any(e == CONFIRMED for e in estados):
        return DESCONHECIMENTO
    return LACUNA


def wrong_nodes(domain: Domain, vector: Vector, kc: str) -> tuple[str, ...]:
    return tuple(n for n in domain.kcs[kc].nodes if state_of(vector, kc, n) == WRONG)


def confirmed_refs(vector: Vector) -> tuple[Ref, ...]:
    """Todos os nós confirmados, de qualquer KC.

    É o que alimenta RF07: o traversal pula nó já confirmado na sessão,
    inclusive vindo de um KC prerequisito já dominado.
    """
    return tuple(ref for ref, estado in vector.items() if estado == CONFIRMED)


def frontier(domain: Domain, vector: Vector, kc: str) -> tuple[str, ...]:
    """Nós não confirmados cujo suporte está inteiro confirmado.

    É onde intervir num estado de LACUNA: o primeiro ponto em que o aluno
    não consegue mais avançar sozinho. Corresponde ao *fringe* da KST.
    """
    out = []
    for node_id, node in domain.kcs[kc].nodes.items():
        if state_of(vector, kc, node_id) == CONFIRMED:
            continue
        if all(vector.get(s) == CONFIRMED for s in node.support):
            out.append(node_id)
    return tuple(out)


def core_nodes(domain: Domain, kc: str) -> tuple[str, ...]:
    """A cadeia causal até a conclusão do KC: o que o aluno tem de construir.

    O grafo é um esboço de prova e a conclusão é o teorema (§2.1). Erguer
    o KC significa erguer essa cadeia — não todo nó que alguma crença
    poderia atacar. Os nós de outros ramos entram no traversal quando, e
    só quando, uma crença que os nega for detectada.

    É também o que torna RF11 satisfazível: exigir o grafo inteiro
    exigiria nós que nenhum plano apresenta, e o participante nunca sairia
    do KC. O `tools.validate` continua nomeando cada nó que fica fora de
    todo traversal, então a lacuna de domínio não some — só deixa de
    travar uma sessão.
    """
    from engine import socratic  # local: evita import circular

    k = domain.kcs[kc]
    if k.conclusion_node not in k.nodes:
        return tuple(k.nodes)
    return tuple(
        n for c, n in socratic.full_plan(domain, kc, k.conclusion_node) if c == kc
    )


def is_complete(domain: Domain, vector: Vector, kc: str) -> bool:
    """RF11: a cadeia até a conclusão está erguida e não sobrou crença ativa."""
    if wrong_nodes(domain, vector, kc):
        return False
    nucleo = core_nodes(domain, kc)
    return bool(nucleo) and all(state_of(vector, kc, n) == CONFIRMED for n in nucleo)


def pending_nodes(domain: Domain, vector: Vector, kc: str) -> tuple[str, ...]:
    """O que ainda falta para encerrar: núcleo não confirmado, mais os errados."""
    faltando = [n for n in core_nodes(domain, kc)
                if state_of(vector, kc, n) != CONFIRMED]
    return tuple(dict.fromkeys(list(wrong_nodes(domain, vector, kc)) + faltando))


# --------------------------------------------------------------------------
# §7.3 Ingestão de resposta
# --------------------------------------------------------------------------

def ingest(
    domain: Domain,
    vector: Vector,
    ciu: CIU,
    correct: bool,
    confidence: str,
    misconception_id: str | None = None,
) -> list[Update]:
    """Traduz uma resposta em deltas do vetor.

    É aqui que a confiança substitui o BKT:

      acertou                -> alvos confirmados
      errou com "chutei"     -> alvos AUSENTES: ele sabe que não sabe.
                                Estado resultante: lacuna, não crença.
      errou com confiança    -> o nó que a crença nega vira ERRADO, e os
                                alvos ainda não vistos viram ausentes.

    Um nó já confirmado nunca é rebaixado por um "chutei": o que ele já
    demonstrou não se apaga por uma resposta insegura depois.

    E, simetricamente, um nó ERRADO nunca é promovido por uma resposta
    certa numa atividade. Só o percurso de refutação o desfaz.

    Por quê: com a gradação, a crença costuma aparecer na atividade de
    nível 1, e a de nível 2 que mira o mesmo nó vem depois. Se acertar a
    segunda confirmasse o nó, a evidência da primeira se apagaria e a
    refutação não aconteceria — justamente para quem mostrou a crença com
    certeza. Decisão do autor: a crença declarada com convicção fica ativa
    até ser refutada. O dado cru das duas respostas continua no log.
    """
    alvos = [(ciu.kc, t) for t in ciu.targets]

    if correct:
        return [Update(kc, n, CONFIRMED) for kc, n in alvos
                if vector.get((kc, n)) != WRONG]

    chutou = confidence == domain.study.guessed
    if chutou:
        return [
            Update(kc, n, ABSENT) for kc, n in alvos
            if vector.get((kc, n)) != CONFIRMED
        ]

    # Errou com confiança: crença ativa.
    updates: list[Update] = []
    negado: Ref | None = None
    if misconception_id and misconception_id in domain.misconceptions:
        m = domain.misconceptions[misconception_id]
        negado = m.negates
        updates.append(Update(m.kc, m.node, WRONG))

    for kc, n in alvos:
        if (kc, n) == negado:
            continue
        if vector.get((kc, n)) in (CONFIRMED, WRONG):
            continue
        updates.append(Update(kc, n, ABSENT))
    return updates


def detect(ciu: CIU, option_idx: int | None = None, text: str | None = None) -> tuple[bool, str | None]:
    """(acertou?, misconception_id) para uma resposta.

    RF05: a crença sai do `misconception_id` do distrator escolhido — não
    de inferência sobre o erro. Distrator sem crença mapeada devolve None,
    e isso é deliberado: se ele for escolhido com frequência, é crença
    fora do catálogo, que é achado e não falha (§4.4).
    """
    if ciu.is_choice:
        if option_idx is None or not (0 <= option_idx < len(ciu.options)):
            raise ValueError("CIU %s: option_idx inválido: %r" % (ciu.id, option_idx))
        escolhida = ciu.options[option_idx]
        return escolhida.correct, escolhida.misconception

    if ciu.type == "fill_blank":
        if text is None:
            raise ValueError("CIU %s espera resposta em texto" % ciu.id)
        if ciu.accepts(text):
            return True, None
        for p in ciu.distractor_patterns:
            if p.hits(text):
                return False, p.misconception
        return False, None

    if ciu.type == "parsons":
        ordem = tuple(text or ())  # aqui `text` é a sequência escolhida
        if ordem == tuple(ciu.steps_correct):
            return True, None
        for w in ciu.common_wrong_orders:
            if ordem == w.order:
                return False, w.misconception
        return False, None

    if ciu.type == "path_choice":
        for p in ciu.paths:
            if p.label == text:
                return p.correct, p.misconception
        raise ValueError("CIU %s: caminho desconhecido: %r" % (ciu.id, text))

    raise ValueError("CIU %s: tipo sem regra de correção: %r" % (ciu.id, ciu.type))


def apply(vector: Vector, updates: Iterable[Update]) -> dict[Ref, str]:
    """Devolve um vetor novo. Não muta o de entrada: o estado é imutável
    para que a FSM continue sendo uma função pura."""
    novo = dict(vector)
    for u in updates:
        novo[u.ref] = u.state
    return novo
