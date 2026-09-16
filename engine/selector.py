"""Seleção da próxima CIU (§7.5).

Três regras, nesta ordem:

  1. alvo na fronteira do conhecimento — a atividade tem de tocar o ponto
     em que o aluno parou de conseguir avançar sozinho;
  2. nível mais baixo primeiro — entre as que tocam o ponto certo, começa
     pela mais leve e sobe. Sem isto, a ordem de apresentação era a ordem
     de declaração no YAML, e a primeira tela da sessão era simplesmente a
     primeira atividade escrita;
  3. tipo diferente do anterior — evita que o aluno responda pelo formato
     em vez de pelo conteúdo;
  4. fase compatível com o estado.

Sem CIU elegível, cai para qualquer não usada do KC na fase pedida.

Determinístico (RNF02): empate se resolve pela ordem de declaração no
YAML, nunca por sorteio. Duas sessões no mesmo estado veem a mesma CIU.
"""

from __future__ import annotations

from typing import Iterable, Sequence

from engine import model
from engine.loader import CIU, Domain


def next_ciu(
    domain: Domain,
    vector: model.Vector,
    kc: str,
    phase: str,
    used: Iterable[str] = (),
    last_type: str | None = None,
    nivel_minimo: int = 1,
    garantir_uma: bool = False,
) -> CIU | None:
    """A próxima atividade, ou None se o KC não tem mais nenhuma na fase.

    `nivel_minimo` é o DESAFIO: quem vem acertando com certeza pula as
    atividades abaixo dele. Se nenhuma sobra acima do piso, não há o que
    apresentar — exceto quando `garantir_uma`, que é o caso da primeira
    atividade do KC: todo KC recebe pelo menos uma, e ela é a mais difícil
    que houver. Pular o KC inteiro tiraria dele toda chance de diagnóstico.
    """
    ja = set(used)
    candidatas = [c for c in domain.cius_of(kc, phase) if c.id not in ja]
    if not candidatas:
        return None

    acima = [c for c in candidatas if c.nivel >= nivel_minimo]
    if not acima:
        if not garantir_uma:
            return None
        topo = max(c.nivel for c in candidatas)
        acima = [c for c in candidatas if c.nivel == topo]
    candidatas = acima

    fronteira = set(model.frontier(domain, vector, kc))
    # Ordem de declaração no YAML: é o desempate determinístico (RNF02).
    declaracao = {cid: i for i, cid in enumerate(domain.cius)}

    def pontua(c: CIU) -> tuple[int, int, int, int]:
        # Menor é melhor. A ordem das chaves é a ordem das regras do §7.5,
        # com o NÍVEL entrando logo depois da fronteira.
        #
        # Por que o nível não vem primeiro: a fronteira é o que faz a
        # atividade tocar o ponto em que o aluno parou de avançar. Uma
        # atividade fácil sobre um nó que ele já domina é agradável e
        # inútil. Entre as que tocam o ponto certo, aí sim vem a mais leve.
        #
        # Por que vem antes do tipo: variar o formato evita responder pelo
        # padrão da pergunta, mas é preferência de desenho. Entrar pelo
        # degrau certo é o que decide se a pessoa continua.
        na_fronteira = 0 if (set(c.targets) & fronteira) else 1
        tipo_novo = 0 if (last_type is None or c.type != last_type) else 1
        return (na_fronteira, c.nivel, tipo_novo, declaracao[c.id])

    return min(candidatas, key=pontua)


def next_diagnostic(
    domain: Domain,
    vector: model.Vector,
    kc: str,
    used: Iterable[str] = (),
    last_type: str | None = None,
    nivel_minimo: int = 1,
    garantir_uma: bool = False,
) -> CIU | None:
    return next_ciu(domain, vector, kc, "diagnostic", used, last_type,
                    nivel_minimo, garantir_uma)


def nivel_minimo(domain: Domain, sequencia_certa: int) -> int:
    """O piso de nível para quem vem acertando com certeza.

    Começa no 1 — todo mundo entra pelo degrau mais leve. A cada
    `desafio_sequencia` acertos seguidos com a confiança mais alta, sobe um
    degrau, até o 3. Um erro, ou um acerto sem certeza, zera a sequência e
    devolve o piso ao 1: quem tropeça volta a ser levado pela mão.
    """
    passo = domain.study.desafio_sequencia
    if passo <= 0:
        return 1
    return min(3, 1 + sequencia_certa // passo)


def next_variation(
    domain: Domain,
    vector: model.Vector,
    kc: str,
    used: Iterable[str] = (),
    last_type: str | None = None,
) -> CIU | None:
    """RF11: mesmo invariante, código novo. Encerra o KC.

    Uma CIU de variação já usada pode ser reapresentada se for a única —
    é melhor repetir o item do que deixar o KC sem fechamento. O evento
    registra a reapresentação, e a análise pode descontá-la.
    """
    nova = next_ciu(domain, vector, kc, "variation", used, last_type)
    if nova is not None:
        return nova
    disponiveis = domain.cius_of(kc, "variation")
    return disponiveis[0] if disponiveis else None


def traversal_ciu(
    domain: Domain,
    vector: model.Vector,
    kc: str,
    used: Iterable[str] = (),
    last_type: str | None = None,
) -> CIU | None:
    return next_ciu(domain, vector, kc, "traversal", used, last_type)


def kc_order(domain: Domain, sequence: Sequence[str]) -> tuple[str, ...]:
    """Ordena a sequência de KCs respeitando prerequisitos (RF16).

    Só reordena o que a sequência já contém: um prerequisito fora do
    recorte não é acrescentado. O piloto roda 3 KCs de propósito, e
    puxar prerequisitos para dentro estouraria os 40 minutos.
    """
    return tuple(sorted(sequence, key=lambda k: domain.kcs[k].teaching_order))
