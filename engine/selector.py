"""Seleção da próxima CIU (§7.5).

Três regras, nesta ordem:

  1. alvo na fronteira do conhecimento — a atividade tem de tocar o ponto
     em que o aluno parou de conseguir avançar sozinho;
  2. tipo diferente do anterior — evita que o aluno responda pelo formato
     em vez de pelo conteúdo;
  3. fase compatível com o estado.

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
) -> CIU | None:
    """A próxima atividade, ou None se o KC não tem mais nenhuma na fase."""
    ja = set(used)
    candidatas = [c for c in domain.cius_of(kc, phase) if c.id not in ja]
    if not candidatas:
        return None

    fronteira = set(model.frontier(domain, vector, kc))
    # Ordem de declaração no YAML: é o desempate determinístico (RNF02).
    declaracao = {cid: i for i, cid in enumerate(domain.cius)}

    def pontua(c: CIU) -> tuple[int, int, int]:
        # Menor é melhor. A ordem das chaves é a ordem das regras do §7.5.
        na_fronteira = 0 if (set(c.targets) & fronteira) else 1
        tipo_novo = 0 if (last_type is None or c.type != last_type) else 1
        return (na_fronteira, tipo_novo, declaracao[c.id])

    return min(candidatas, key=pontua)


def next_diagnostic(
    domain: Domain,
    vector: model.Vector,
    kc: str,
    used: Iterable[str] = (),
    last_type: str | None = None,
) -> CIU | None:
    return next_ciu(domain, vector, kc, "diagnostic", used, last_type)


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
