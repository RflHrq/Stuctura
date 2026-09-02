"""Os dois braços do experimento (§8). Ponto de maior risco de validade.

Se os braços diferirem em algo além da FORMA da correção, o resultado não
mede nada. A garantia mecânica é estrutural, não de disciplina: as duas
estratégias chamam o MESMO `socratic.steps()` e diferem apenas no tipo de
ação que envolvem cada passo.

    SocraticStrategy  ->  [Ask(passo), ...]
    DirectStrategy    ->  [Explain(passo), ...] + [Confirm()]

A variável isolada é a geração ativa: no braço A o aluno responde cada
passo e a conclusão é dele; no braço B o mesmo conteúdo, na mesma ordem,
é apresentado pronto e ele confirma que leu.

Não há como um braço divergir do outro sem que `parity()` acuse — e é isso
que se mostra à banca quando perguntarem como a variável foi controlada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence

from engine.loader import Domain, Ref
from engine.socratic import Step, steps

ARM_SOCRATIC = "socratic"
ARM_DIRECT = "direct"
ARMS = (ARM_SOCRATIC, ARM_DIRECT)


# --------------------------------------------------------------------------
# Ações
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Action:
    """Uma unidade apresentável. `kind` é o que muda entre os braços."""

    kind: str          # "ask" | "explain" | "confirm"
    kc: str
    node: str
    text: str
    idx: int
    total: int

    @property
    def ref(self) -> Ref:
        return (self.kc, self.node)


def Ask(step: Step) -> Action:
    """Braço A: o aluno responde. A conclusão é construída por ele."""
    return Action("ask", step.kc, step.node, step.question, step.idx, step.total)


def Explain(step: Step) -> Action:
    """Braço B: o mesmo nó, apresentado como afirmação já pronta.

    O texto vem do MESMO campo do YAML que alimenta a pergunta do braço A.
    O que muda é a forma verbal, não o conteúdo.
    """
    return Action("explain", step.kc, step.node, step.text, step.idx, step.total)


def Confirm(kc: str, total: int) -> Action:
    """Fecha o braço B: "entendi". É o que pareia com responder no braço A."""
    return Action("confirm", kc, "", "Entendi.", total + 1, total + 1)


# --------------------------------------------------------------------------
# Estratégias
# --------------------------------------------------------------------------

class Strategy(Protocol):
    arm: str

    def correct(
        self, domain: Domain, kc: str, node: str, confirmed: Iterable[Ref] = ()
    ) -> list[Action]:
        ...


class SocraticStrategy:
    """Braço A. Percorre o grafo; o aluno gera cada conclusão."""

    arm = ARM_SOCRATIC

    def correct(
        self, domain: Domain, kc: str, node: str, confirmed: Iterable[Ref] = ()
    ) -> list[Action]:
        return [Ask(s) for s in steps(domain, kc, node, confirmed)]


class DirectStrategy:
    """Braço B. A mesma cadeia causal, já pronta, como texto."""

    arm = ARM_DIRECT

    def correct(
        self, domain: Domain, kc: str, node: str, confirmed: Iterable[Ref] = ()
    ) -> list[Action]:
        plano = steps(domain, kc, node, confirmed)
        if not plano:
            return []
        return [Explain(s) for s in plano] + [Confirm(kc, len(plano))]


def for_arm(arm: str) -> Strategy:
    if arm == ARM_SOCRATIC:
        return SocraticStrategy()
    if arm == ARM_DIRECT:
        return DirectStrategy()
    raise ValueError("braço desconhecido: %r; esperado um de %s" % (arm, ARMS))


# --------------------------------------------------------------------------
# Paridade
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ParityReport:
    kc: str
    node: str
    socratic_nodes: tuple[Ref, ...]
    direct_nodes: tuple[Ref, ...]

    @property
    def ok(self) -> bool:
        return self.socratic_nodes == self.direct_nodes

    def __str__(self) -> str:
        if self.ok:
            return "%s:%s paridade ok (%d nós)" % (self.kc, self.node, len(self.socratic_nodes))
        return (
            "%s:%s PARIDADE QUEBRADA\n  socrático: %s\n  direto:    %s"
            % (
                self.kc, self.node,
                [" ".join(r) for r in self.socratic_nodes],
                [" ".join(r) for r in self.direct_nodes],
            )
        )


def content_nodes(actions: Sequence[Action]) -> tuple[Ref, ...]:
    """Os nós de conteúdo de um roteiro, na ordem.

    `confirm` sai fora: é o pareamento do ato de responder, não conteúdo.
    """
    return tuple(a.ref for a in actions if a.kind != "confirm")


def parity(
    domain: Domain, kc: str, node: str, confirmed: Iterable[Ref] = ()
) -> ParityReport:
    """Compara os dois braços sobre o mesmo alvo.

    Afirma que a sequência de nós é idêntica, variando só o tipo de ação.
    Falha aqui invalida o experimento.
    """
    ja = tuple(confirmed)
    a = SocraticStrategy().correct(domain, kc, node, ja)
    b = DirectStrategy().correct(domain, kc, node, ja)
    return ParityReport(kc, node, content_nodes(a), content_nodes(b))


def parity_over_catalog(domain: Domain) -> list[ParityReport]:
    """Paridade sobre as 34 crenças do catálogo, ataque primário e secundário."""
    alvos: list[tuple[str, str]] = []
    for m in sorted(domain.misconceptions.values(), key=lambda x: x.id):
        alvos.append(m.negates)
        alvos.extend(m.also_negates)
    return [parity(domain, kc, node) for kc, node in alvos]
