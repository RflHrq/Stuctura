"""Feedback em três etapas (RF17): validação, contradição, reconstrução.

Puro. Recebe o domínio, o vetor e o ponto do fluxo; devolve texto montado
a partir dos moldes de `feedback.yaml`. Nenhuma frase é escrita aqui — o
módulo só decide QUAL molde e com QUE conteúdo, e o conteúdo vem do grafo.

SIMETRIA ENTRE OS BRAÇOS
------------------------
As três etapas acontecem nos mesmos pontos nos dois braços, com o mesmo
conteúdo. Só a etapa de reconstrução tem molde distinto por braço, e a
diferença é de VERBO — "cada premissa foi uma resposta sua" contra "cada
passo apoia o seguinte" —, porque afirmar que o aluno respondeu quando ele
apenas leu seria falso.

Se um braço recebesse elaboração verbal que o outro não recebe, a variável
isolada deixaria de ser a geração ativa. `tests/test_feedback.py` afirma
que os dois braços recebem as três etapas, nos mesmos nós.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from engine import model
from engine.loader import Domain, Ref

VALIDATION = "validation"
CONTRADICTION = "contradiction"
RECONSTRUCTION = "reconstruction"
STAGES = (VALIDATION, CONTRADICTION, RECONSTRUCTION)

# Marcadores que um molde pode usar. O validador recusa qualquer outro:
# um `{premissa}` digitado errado apareceria cru na tela do participante.
PLACEHOLDERS = ("belief", "support", "node", "conclusion", "kc_name")

_MARCADOR = re.compile(r"\{([a-z_]+)\}")


@dataclass(frozen=True, slots=True)
class Feedback:
    stage: str
    text: str

    def as_json(self) -> dict[str, str]:
        return {"stage": self.stage, "text": self.text}


def placeholders_of(molde: str) -> tuple[str, ...]:
    return tuple(_MARCADOR.findall(molde or ""))


def _preenche(molde: str, **valores: str) -> str:
    """Substitui só os marcadores conhecidos, sem `str.format`.

    `format` explodiria em qualquer chave ausente e, pior, interpretaria
    chaves que aparecessem no TEXTO DO DOMÍNIO — um enunciado com `{` viraria
    erro em sessão. Aqui, marcador sem valor fica como está e o validador
    já terá reclamado na carga.
    """
    def troca(m: re.Match) -> str:
        return valores.get(m.group(1), m.group(0))
    return _MARCADOR.sub(troca, molde or "").strip()


def _lista_suporte(domain: Domain, ref: Ref) -> str:
    """As premissas de um nó, em prosa corrida e sem o nome técnico.

    `display_text`, não `text`: a força da etapa 2 do RF17 é dizer "repare
    no que VOCÊ confirmou". Devolver a premissa no enunciado canônico
    enquanto o aluno a confirmou em linguagem corrente quebra exatamente
    isso — ele não reconhece como sua uma frase que não leu.
    """
    nd = domain.node(*ref)
    textos = []
    for s in nd.support:
        try:
            textos.append(
                domain.study.mask(domain.node(*s).display_text).rstrip("."))
        except KeyError:
            continue
    if not textos:
        return ""
    if len(textos) == 1:
        return textos[0] + "."
    return "; ".join(textos[:-1]) + "; e " + textos[-1] + "."


# --------------------------------------------------------------------------
# As três etapas
# --------------------------------------------------------------------------

def validation(domain: Domain, vector: model.Vector, kc: str,
               belief_id: str | None) -> Feedback | None:
    """Etapa 1, ao entrar na correção. Reconhece o que há de legítimo."""
    moldes = domain.feedback.get(VALIDATION) or {}
    estado = model.cognitive_state(domain, vector, kc)

    if belief_id and belief_id in domain.misconceptions:
        molde = moldes.get("misconception")
        crenca = domain.study.mask(domain.misconceptions[belief_id].belief)
        return _monta(VALIDATION, molde, belief=crenca,
                      kc_name=domain.kcs[kc].name)

    chave = "unknown" if estado == model.DESCONHECIMENTO else "gap"
    return _monta(VALIDATION, moldes.get(chave), kc_name=domain.kcs[kc].name)


def contradiction(domain: Domain, kc: str, node: str,
                  belief_id: str | None) -> Feedback | None:
    """Etapa 2, ao chegar ao nó que a crença nega.

    A contradição é entre coisas que o ALUNO afirmou — as premissas que ele
    acabou de confirmar contra a ideia de que ele partiu. Não é entre ele e
    o sistema, e é isso que a torna difícil de reinterpretar.
    """
    moldes = domain.feedback.get(CONTRADICTION) or {}
    suporte = _lista_suporte(domain, (kc, node))
    if not suporte:
        return None

    if belief_id and belief_id in domain.misconceptions:
        return _monta(
            CONTRADICTION, moldes.get("template"), support=suporte,
            belief=domain.study.mask(domain.misconceptions[belief_id].belief),
            node=domain.study.mask(domain.node(kc, node).display_text),
        )
    return _monta(CONTRADICTION, moldes.get("without_belief"), support=suporte)


def reconstruction(domain: Domain, kc: str, arm: str,
                   houve_correcao: bool = False) -> Feedback | None:
    """Etapa 3, no fecho. Diz de onde a conclusão veio, não qual é.

    O molde difere por braço porque afirmar que o aluno respondeu quando
    ele apenas leu seria falso — e o participante notaria. A diferença é
    de verbo; o conteúdo é o mesmo.
    """
    moldes = domain.feedback.get(RECONSTRUCTION) or {}
    base = _monta(RECONSTRUCTION, moldes.get(arm) or moldes.get("socratic"),
                  conclusion=domain.kcs[kc].conclusion,
                  kc_name=domain.kcs[kc].name)
    if base is None:
        return None
    extra = moldes.get("after_correction") if houve_correcao else None
    if extra:
        return Feedback(RECONSTRUCTION, base.text + "\n\n" + _preenche(extra))
    return base


def _monta(stage: str, molde: str | None, **valores: str) -> Feedback | None:
    if not molde:
        return None
    texto = _preenche(molde, **valores)
    return Feedback(stage, texto) if texto else None
