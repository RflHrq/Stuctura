"""Traversal socrático: ordem topológica, perguntas e regressão (§7.1, §7.4).

Puro. Sem I/O, sem estado global, sem aleatoriedade. Recebe o domínio e o
que já foi confirmado; devolve o plano e as perguntas. É o que permite
congelar os 34 planos de refutação num teste golden e reproduzir qualquer
sessão na defesa.

O texto das perguntas é MONTADO a partir do grafo, nunca escrito à mão.
Os moldes das perguntas vivem em `feedback.yaml`, não aqui: são texto que o
aluno lê, e por isso são domínio. O motor decide QUAL molde e com que
conteúdo; o conteúdo vem do grafo. Ver PROMPT_KEYS em loader.py —
andaime linguístico, não conhecimento de domínio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from engine.loader import Domain, Ref

# Limite de tentativas por nó antes de encerrar o KC como "em progresso"
# (§6, §7.4). Sem essa guarda, um aluno travado entra em laço. O valor
# efetivo vem de study.yaml; esta constante é só o padrão de segurança.
MAX_ATTEMPTS = 3


@dataclass(frozen=True, slots=True)
class Step:
    """Um passo do traversal. `idx`/`total` são 1-based, para exibição."""

    kc: str
    node: str
    kind: str          # "base" | "inference"
    text: str          # o enunciado do nó, como está no YAML
    question: str      # a pergunta montada a partir do grafo
    idx: int
    total: int

    @property
    def ref(self) -> Ref:
        return (self.kc, self.node)


# --------------------------------------------------------------------------
# §7.1 Traversal
# --------------------------------------------------------------------------

def plan(
    domain: Domain,
    kc: str,
    target: str,
    confirmed: Iterable[Ref] = (),
) -> list[Ref]:
    """Ordem em que os nós devem ser percorridos para refutar `target`.

    Pós-ordem em profundidade sobre o suporte: todo suporte de um nó
    aparece antes dele. Termina em no máximo |nós| passos porque o grafo é
    acíclico — propriedade garantida pelo validador, não presumida.

    Nós já confirmados na sessão são pulados (RF07), exceto o próprio
    alvo: o nó negado é sempre percorrido, porque é ele que está errado.
    """
    ordem: list[Ref] = []
    visto: set[Ref] = set()

    def visitar(ref: Ref) -> None:
        if ref in visto:
            return
        visto.add(ref)
        try:
            node = domain.node(*ref)
        except KeyError:
            return
        for s in node.support:
            visitar(s)
        ordem.append(ref)

    visitar((kc, target))

    ja = set(confirmed)
    alvo = (kc, target)
    return [r for r in ordem if r not in ja or r == alvo]


def full_plan(domain: Domain, kc: str, target: str) -> list[Ref]:
    """O plano sem filtro de confirmados. É o que o teste golden congela."""
    return plan(domain, kc, target, confirmed=())


def steps(
    domain: Domain,
    kc: str,
    target: str,
    confirmed: Iterable[Ref] = (),
    with_diagram: bool = False,
) -> list[Step]:
    """O plano já com as perguntas montadas, pronto para a estratégia."""
    refs = plan(domain, kc, target, confirmed)
    total = len(refs)
    return [
        Step(
            kc=k,
            node=n,
            kind=domain.node(k, n).type,
            text=domain.study.mask(domain.node(k, n).text),
            question=question(domain, k, n, with_diagram),
            idx=i,
            total=total,
        )
        for i, (k, n) in enumerate(refs, start=1)
    ]


def steps_from(domain: Domain, refs: Sequence[Ref],
               with_diagram: bool = False) -> list[Step]:
    """Monta os passos a partir de um plano JÁ congelado.

    A FSM congela o plano ao entrar na correção e caminha sobre ele. Não
    pode recalcular a cada turno: confirmar um nó no meio do traversal
    encolheria o plano sob os pés do aluno, e o "passo 3 de 7" viraria
    "passo 3 de 5" entre uma tela e a seguinte.
    """
    total = len(refs)
    return [
        Step(kc=k, node=n, kind=domain.node(k, n).type,
             text=domain.study.mask(domain.node(k, n).text),
             question=question(domain, k, n, with_diagram), idx=i, total=total)
        for i, (k, n) in enumerate(refs, start=1)
    ]


# --------------------------------------------------------------------------
# Geração das perguntas
# --------------------------------------------------------------------------

def question(domain: Domain, kc: str, node: str,
             with_diagram: bool = False) -> str:
    """Monta a pergunta do nó a partir da sua posição no grafo.

    Nó BASE: fato observável. Pergunta direta, ancorada no diagrama — não
    há premissa anterior para invocar.

    Nó de INFERÊNCIA: cita o suporte que o aluno já confirmou e pede a
    conclusão. É aqui que o socrático morde: o aluno não consegue
    reinterpretar uma conclusão construída com as respostas dele.
    """
    nd = domain.node(kc, node)
    corpo = domain.study.mask(nd.text).rstrip(".")

    if nd.is_base:
        # "Olhando o diagrama" só pode ser dito se HOUVER um diagrama na
        # tela. O confronto visual acontece antes do traversal e só quando
        # a crença nega um nó-base; na maioria dos casos não há diagrama
        # nenhum, e a pergunta mandava o aluno olhar para o que não existe.
        chave = "base_with_diagram" if with_diagram else "base_plain"
        return _molde(domain, chave, "%s, certo?", node=corpo)

    citados = "; ".join(
        domain.study.mask(domain.node(*s).text).rstrip(".")
        for s in nd.support
        if _existe(domain, s)
    )
    if not citados:  # inferência sem suporte resolvível: o validador já reclamou
        return _molde(domain, "inference_no_support", "%s, certo?", node=corpo)
    return _molde(domain, "inference", "%s, certo?", node=corpo, support=citados)


def _molde(domain: Domain, chave: str, reserva: str, **valores: str) -> str:
    """Preenche um molde de `feedback.yaml`.

    Sem o molde, cai num texto mínimo em vez de quebrar: os moldes são
    SHOULD como o resto do RF17, e faltar um não pode derrubar uma coleta
    no meio. O validador avisa antes.
    """
    molde = domain.prompts.get(chave)
    if not molde:
        return reserva % valores.get("node", "")
    for marcador, valor in valores.items():
        molde = molde.replace("{" + marcador + "}", valor)
    return molde.strip()


def _existe(domain: Domain, ref: Ref) -> bool:
    try:
        domain.node(*ref)
        return True
    except KeyError:
        return False


def conclusion(domain: Domain, kc: str) -> str:
    """O enunciado da conclusão do KC. A nomeação tardia acontece aqui.

    RF10: os termos de `study.late_named_terms` só podem aparecer neste
    ponto e no texto do nó de conclusão. Nenhum nó intermediário, pergunta
    ou rótulo de diagrama pode contê-los antes — o validador confere.
    """
    return domain.kcs[kc].conclusion


# --------------------------------------------------------------------------
# §7.4 Regressão controlada (RF09)
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Regression:
    """O que fazer depois de um erro num nó do traversal.

    `action`:
      reformulate  1ª tentativa: repete o nó citando o suporte por extenso
      regress      2ª tentativa: volta um passo. O confirmado NÃO é descartado
      abandon      3ª tentativa: encerra o KC como "em progresso" e segue
    """

    action: str
    cursor: int            # índice do passo em que o traversal continua
    attempts: int
    from_node: str | None = None
    to_node: str | None = None
    prompt: str | None = None


def on_wrong(
    domain: Domain,
    steps_: Sequence[Step],
    cursor: int,
    attempts: int,
    max_attempts: int | None = None,
    with_diagram: bool = False,
) -> Regression:
    """Decide o próximo passo depois de o aluno errar o nó em `cursor`.

    `attempts` é quantas vezes ele JÁ errou este nó, antes desta. A função
    é pura: não incrementa nada, não escreve nada. Quem persiste é a FSM.

    O progresso confirmado nunca é descartado — só o cursor anda para trás.
    """
    atual = steps_[cursor]
    n = attempts + 1
    limite = max_attempts or domain.study.max_attempts_per_node or MAX_ATTEMPTS

    if n >= limite:
        return Regression(action="abandon", cursor=cursor, attempts=n,
                          from_node=atual.node)

    if n == 1:
        return Regression(
            action="reformulate",
            cursor=cursor,
            attempts=n,
            from_node=atual.node,
            prompt=reformulate(domain, atual, with_diagram),
        )

    # n == 2: volta um passo. Se já está no primeiro, não há para onde
    # voltar — reformula de novo em vez de sair do traversal.
    if cursor == 0:
        return Regression(
            action="reformulate",
            cursor=0,
            attempts=n,
            from_node=atual.node,
            prompt=reformulate(domain, atual, with_diagram),
        )

    anterior = steps_[cursor - 1]
    return Regression(
        action="regress",
        cursor=cursor - 1,
        attempts=n,
        from_node=atual.node,
        to_node=anterior.node,
        prompt=anterior.question,
    )


def reformulate(domain: Domain, step: Step,
                with_diagram: bool = False) -> str:
    """Repete a pergunta com o suporte explicitado nó a nó.

    Primeira tentativa de recuperação: em vez de mudar de assunto, torna
    visível a cadeia que sustenta a conclusão pedida.
    """
    nd = domain.node(step.kc, step.node)
    if nd.is_base:
        chave = "retry_base_with_diagram" if with_diagram else "retry_base_plain"
        return _molde(domain, chave, "%s — você concorda?",
                      node=domain.study.mask(nd.text))

    textos = [domain.study.mask(domain.node(*s).text)
              for s in nd.support if _existe(domain, s)]
    return _molde(
        domain, "retry_inference", "%s",
        node=domain.study.mask(nd.text),
        support="; ".join(t.rstrip(".") for t in textos),
        support_list=chr(10).join("- " + t for t in textos),
    )
