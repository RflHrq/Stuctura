"""Carga e validação do domínio declarativo (RF01).

Princípio §1: falha na carga, nunca em sessão. Se um YAML estiver
inconsistente, `load()` levanta DomainError e o sistema não sobe. Nunca
descobrir isso com um aluno na frente.

Este módulo é o único do motor que toca disco. Todo o resto recebe o
`Domain` pronto e é puro.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

DEFAULT_DOMAIN = Path(__file__).resolve().parent.parent / "domain" / "c_pointers"

# Referência a um nó: (kc, node). Sempre absoluta depois da resolução.
Ref = tuple[str, str]

NODE_TYPES = ("base", "inference")
GRADES = ("D", "T", "L", "N", "E")
KINDS = ("foundational", "derivational")
SOCRATIC_MODES = ("pure", "diagram")

# Fases de uma CIU (§6). `traversal` e usada durante a correcao; so as
# `diagnostic` alimentam o diagnostico inicial, e a `variation` encerra o KC.
CIU_PHASES = ("diagnostic", "traversal", "variation")
CIU_KINDS = ("multiple_choice", "prediction", "fill_in", "ordering", "contrast")


class DomainError(Exception):
    """Domínio inconsistente. O sistema não sobe."""

    def __init__(self, problemas: Iterable[str]) -> None:
        self.problemas = list(problemas)
        corpo = "\n  - ".join(self.problemas)
        super().__init__(
            "domínio inválido (%d problema(s)):\n  - %s" % (len(self.problemas), corpo)
        )


@dataclass(frozen=True, slots=True)
class Node:
    kc: str
    id: str
    type: str
    text: str
    support: tuple[Ref, ...] = ()
    imports: Ref | None = None

    @property
    def ref(self) -> Ref:
        return (self.kc, self.id)

    @property
    def is_base(self) -> bool:
        return self.type == "base"


@dataclass(frozen=True, slots=True)
class KC:
    id: str
    name: str
    teaching_order: int
    prerequisites: tuple[str, ...]
    conclusion_node: str
    conclusion_text: str
    technical_name: str
    socratic: str
    nodes: Mapping[str, Node]

    @property
    def conclusion_ref(self) -> Ref:
        return (self.id, self.conclusion_node)


@dataclass(frozen=True, slots=True)
class Misconception:
    id: str
    belief: str
    negates: Ref
    also_negates: tuple[Ref, ...]
    kind: str
    plan_length: int
    grade: str
    provenance: str
    analogy: str | None = None
    note: str | None = None
    disputed: bool = False

    @property
    def kc(self) -> str:
        return self.negates[0]

    @property
    def node(self) -> str:
        return self.negates[1]


@dataclass(frozen=True, slots=True)
class Option:
    text: str
    correct: bool = False
    misconception: str | None = None


@dataclass(frozen=True, slots=True)
class FreeAnswer:
    """Resposta livre de uma CIU de lacuna guiada."""

    expected: str
    also_accepts: tuple[str, ...] = ()

    def accepts(self, texto: str) -> bool:
        alvo = texto.strip().casefold()
        return alvo == self.expected.strip().casefold() or any(
            alvo == a.strip().casefold() for a in self.also_accepts
        )


@dataclass(frozen=True, slots=True)
class Pattern:
    """Padrao de resposta livre que revela uma crenca (§12: crenca fora do
    catalogo aparece como padrao nao previsto)."""

    match: tuple[str, ...]
    misconception: str | None = None

    def hits(self, texto: str) -> bool:
        alvo = texto.casefold()
        return any(m.casefold() in alvo for m in self.match)


@dataclass(frozen=True, slots=True)
class WrongOrder:
    """Uma sequencia errada numa CIU de ordenacao.

    Duas semanticas convivem no catalogo, e a interface precisa distingui-las:
    quando `order` e permutacao de `CIU.steps`, o aluno reordena os mesmos
    passos; quando nao e, sao dois caminhos diferentes e ele escolhe um.
    """

    order: tuple[str, ...]
    misconception: str | None = None


@dataclass(frozen=True, slots=True)
class CIU:
    id: str
    kc: str
    targets: tuple[str, ...]
    phase: str
    kind: str
    stem: str
    code: str
    options: tuple[Option, ...] = ()
    steps: tuple[str, ...] = ()
    wrong_orders: tuple[WrongOrder, ...] = ()
    answer: FreeAnswer | None = None
    patterns: tuple[Pattern, ...] = ()
    visual: Mapping[str, Any] | None = None

    @property
    def is_choice(self) -> bool:
        """Tem alternativas? As de lacuna e ordenacao nao tem."""
        return bool(self.options)

    @property
    def correct_index(self) -> int:
        for i, o in enumerate(self.options):
            if o.correct:
                return i
        raise ValueError("CIU %s sem alternativa correta" % self.id)

    def is_permutation(self, wrong: "WrongOrder") -> bool:
        return bool(self.steps) and sorted(wrong.order) == sorted(self.steps)

    def misconception_ids(self) -> tuple[str, ...]:
        """Toda crenca que esta CIU consegue detectar, por qualquer via."""
        out = [o.misconception for o in self.options if o.misconception]
        out += [p.misconception for p in self.patterns if p.misconception]
        out += [w.misconception for w in self.wrong_orders if w.misconception]
        return tuple(dict.fromkeys(out))


@dataclass(frozen=True, slots=True)
class Domain:
    id: str
    name: str
    kcs: Mapping[str, KC]
    misconceptions: Mapping[str, Misconception]
    cius: Mapping[str, CIU]
    pilot_sequence: tuple[str, ...]
    hash: str
    source: Path = field(compare=False, default=DEFAULT_DOMAIN)

    # -- consultas -------------------------------------------------------

    def node(self, kc: str, node: str) -> Node:
        try:
            return self.kcs[kc].nodes[node]
        except KeyError:
            raise KeyError("nó inexistente: %s:%s" % (kc, node)) from None

    def support(self, kc: str, node: str) -> tuple[Ref, ...]:
        return self.node(kc, node).support

    def nodes_of(self, kc: str) -> tuple[str, ...]:
        return tuple(self.kcs[kc].nodes)

    def misconceptions_of(self, kc: str) -> tuple[Misconception, ...]:
        return tuple(m for m in self.misconceptions.values() if m.kc == kc)

    def cius_of(self, kc: str) -> tuple[CIU, ...]:
        return tuple(c for c in self.cius.values() if c.kc == kc)

    def attackers(self, kc: str, node: str) -> tuple[Misconception, ...]:
        """Crenças que negam este nó, primária ou secundariamente."""
        alvo = (kc, node)
        return tuple(
            m for m in self.misconceptions.values()
            if m.negates == alvo or alvo in m.also_negates
        )

    def teaching_sequence(self) -> tuple[str, ...]:
        return tuple(sorted(self.kcs, key=lambda k: self.kcs[k].teaching_order))


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------

FILES = ("kcs.yaml", "premise_graphs.yaml", "misconceptions.yaml", "cius.yaml")


def load(path: str | Path | None = None) -> Domain:
    """Carrega, resolve referências cross-KC e valida. Levanta DomainError."""
    base = Path(path) if path is not None else DEFAULT_DOMAIN
    problemas: list[str] = []

    raw = {}
    for nome in FILES:
        arquivo = base / nome
        if not arquivo.exists():
            if nome == "cius.yaml":
                raw[nome] = {}
                problemas.append("cius.yaml ausente: nenhuma atividade carregada")
                continue
            raise DomainError(["arquivo obrigatório ausente: %s" % arquivo])
        try:
            raw[nome] = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise DomainError(["%s não é YAML válido: %s" % (nome, exc)]) from exc

    kcs = _build_kcs(raw["kcs.yaml"], raw["premise_graphs.yaml"], problemas)
    miscs = _build_misconceptions(raw["misconceptions.yaml"], kcs, problemas)
    cius = _build_cius(raw["cius.yaml"], kcs, miscs, problemas)

    _check_refs(kcs, problemas)
    _check_acyclic(kcs, problemas)
    _check_prerequisites(raw["kcs.yaml"], kcs, problemas)

    if problemas:
        raise DomainError(problemas)

    meta = raw["kcs.yaml"].get("domain", {})
    return Domain(
        id=meta.get("id", "unnamed"),
        name=meta.get("name", ""),
        kcs=kcs,
        misconceptions=miscs,
        cius=cius,
        pilot_sequence=tuple(raw["kcs.yaml"].get("pilot_sequence", ())),
        hash=domain_hash(base),
        source=base,
    )


def domain_hash(path: str | Path | None = None) -> str:
    """SHA-256 dos arquivos do domínio, em ordem estável (§15).

    Gravado em `session_started`. Responde "os participantes viram
    exatamente o mesmo conteúdo?" — a primeira pergunta quando os dados
    surpreendem.
    """
    base = Path(path) if path is not None else DEFAULT_DOMAIN
    h = hashlib.sha256()
    for nome in FILES:
        arquivo = base / nome
        h.update(nome.encode("utf-8"))
        h.update(arquivo.read_bytes() if arquivo.exists() else b"")
    return "sha256:" + h.hexdigest()


# --------------------------------------------------------------------------
# Construção
# --------------------------------------------------------------------------

def _ref(valor: str, kc_atual: str, onde: str, problemas: list[str]) -> Ref | None:
    if not isinstance(valor, str):
        problemas.append("%s: referência não é texto: %r" % (onde, valor))
        return None
    if "." in valor:
        kc, _, node = valor.partition(".")
        return (kc, node)
    return (kc_atual, valor)


def _build_kcs(kcs_raw: Mapping, graphs_raw: Mapping, problemas: list[str]) -> dict[str, KC]:
    graphs = graphs_raw.get("graphs", {})
    entradas = kcs_raw.get("kcs", {})
    out: dict[str, KC] = {}

    for kc_id, meta in entradas.items():
        grafo = graphs.get(kc_id)
        if grafo is None:
            problemas.append("KC %s declarado em kcs.yaml sem grafo em premise_graphs.yaml" % kc_id)
            continue

        nodes: dict[str, Node] = {}
        for node_id, nd in grafo.items():
            tipo = nd.get("type")
            if tipo not in NODE_TYPES:
                problemas.append("%s:%s tipo inválido: %r" % (kc_id, node_id, tipo))
                continue
            sup = tuple(
                r for r in (
                    _ref(s, kc_id, "%s:%s support" % (kc_id, node_id), problemas)
                    for s in nd.get("support", ())
                ) if r is not None
            )
            if tipo == "base" and sup:
                problemas.append("%s:%s é base mas declara support" % (kc_id, node_id))
            if tipo == "inference" and not sup:
                problemas.append("%s:%s é inferência sem support" % (kc_id, node_id))
            imp = nd.get("imports")
            nodes[node_id] = Node(
                kc=kc_id,
                id=node_id,
                type=tipo,
                text=nd.get("text", ""),
                support=sup,
                imports=_ref(imp, kc_id, "%s:%s imports" % (kc_id, node_id), problemas) if imp else None,
            )
            if not nodes[node_id].text:
                problemas.append("%s:%s sem texto" % (kc_id, node_id))

        concl = meta.get("conclusion_node")
        if concl not in nodes:
            problemas.append(
                "KC %s: conclusion_node %r não existe no grafo" % (kc_id, concl)
            )
        socratic = meta.get("socratic")
        if socratic not in SOCRATIC_MODES:
            problemas.append("KC %s: socratic inválido: %r" % (kc_id, socratic))

        out[kc_id] = KC(
            id=kc_id,
            name=meta.get("name", ""),
            teaching_order=int(meta.get("teaching_order", 0)),
            prerequisites=tuple(meta.get("prerequisites", ())),
            conclusion_node=concl or "",
            conclusion_text=meta.get("conclusion_text", ""),
            technical_name=meta.get("technical_name", ""),
            socratic=socratic or "pure",
            nodes=nodes,
        )

    for kc_id in graphs:
        if kc_id not in entradas:
            problemas.append("grafo %s sem KC correspondente em kcs.yaml" % kc_id)

    return out


def _build_misconceptions(
    raw: Mapping, kcs: Mapping[str, KC], problemas: list[str]
) -> dict[str, Misconception]:
    out: dict[str, Misconception] = {}
    for mid, m in (raw.get("misconceptions") or {}).items():
        neg = m.get("negates") or {}
        alvo = (neg.get("kc"), neg.get("node"))
        if alvo[0] not in kcs or alvo[1] not in kcs.get(alvo[0], KC("", "", 0, (), "", "", "", "pure", {})).nodes:
            problemas.append("crença %s nega nó inexistente: %s:%s" % (mid, *alvo))
            continue

        grade = m.get("grade")
        if grade not in GRADES:
            problemas.append("crença %s: grade inválido %r" % (mid, grade))
        kind = m.get("kind")
        if kind not in KINDS:
            problemas.append("crença %s: kind inválido %r" % (mid, kind))

        # A classe tem de bater com o tipo do nó negado: é o que decide se
        # o confronto visual é obrigatório (RF08).
        negado = kcs[alvo[0]].nodes[alvo[1]]
        esperado = "foundational" if negado.is_base else "derivational"
        if kind in KINDS and kind != esperado:
            problemas.append(
                "crença %s é %s mas nega nó %s (%s:%s) — deveria ser %s"
                % (mid, kind, negado.type, *alvo, esperado)
            )

        if not m.get("provenance"):
            problemas.append("crença %s sem proveniência" % mid)

        out[mid] = Misconception(
            id=mid,
            belief=m.get("belief", ""),
            negates=alvo,
            also_negates=tuple(
                (a.get("kc"), a.get("node")) for a in (m.get("also_negates") or ())
            ),
            kind=kind or esperado,
            plan_length=int(m.get("plan_length", 0)),
            grade=grade or "E",
            provenance=m.get("provenance", ""),
            analogy=m.get("analogy"),
            note=m.get("note"),
            disputed=bool(m.get("disputed")),
        )
    return out


def _build_cius(
    raw: Mapping, kcs: Mapping[str, KC], miscs: Mapping[str, Misconception],
    problemas: list[str],
) -> dict[str, CIU]:
    out: dict[str, CIU] = {}
    for cid, c in (raw.get("cius") or {}).items():
        kc = c.get("kc")
        if kc not in kcs:
            problemas.append("CIU %s referencia KC inexistente: %r" % (cid, kc))
            continue

        alvos = tuple(c.get("targets") or ())
        if not alvos:
            problemas.append("CIU %s sem nó-alvo: não alimenta a Q-matrix" % cid)
        for t in alvos:
            if t not in kcs[kc].nodes:
                problemas.append("CIU %s: target %s:%s não existe" % (cid, kc, t))

        fase = c.get("phase")
        if fase not in CIU_PHASES:
            problemas.append("CIU %s: phase inválida %r" % (cid, fase))
        tipo = c.get("kind")
        if tipo not in CIU_KINDS:
            problemas.append("CIU %s: kind inválido %r" % (cid, tipo))

        def _mid(valor, onde):
            """Confere um misconception_id contra o catálogo."""
            if valor is not None and valor not in miscs:
                problemas.append("CIU %s (%s): crença desconhecida %r" % (cid, onde, valor))
                return None
            return valor

        opcoes = tuple(
            Option(o.get("text", ""), bool(o.get("correct")),
                   _mid(o.get("misconception"), "distrator"))
            for o in (c.get("options") or ())
        )
        if opcoes:
            corretas = [o for o in opcoes if o.correct]
            if len(corretas) != 1:
                problemas.append(
                    "CIU %s: precisa de exatamente 1 alternativa correta, tem %d"
                    % (cid, len(corretas))
                )
            if not any(o.misconception for o in opcoes if not o.correct):
                problemas.append("CIU %s: nenhum distrator mapeado a crença" % cid)

        passos = tuple(c.get("steps") or ())
        ordens = tuple(
            WrongOrder(tuple(w.get("order") or ()),
                       _mid(w.get("misconception"), "ordem errada"))
            for w in (c.get("wrong_orders") or ())
        )
        bruto = c.get("answer")
        resposta = FreeAnswer(
            bruto.get("expected", ""), tuple(bruto.get("also_accepts") or ())
        ) if bruto else None

        padroes = tuple(
            Pattern(tuple(p.get("match") or ()), _mid(p.get("misconception"), "padrão"))
            for p in (c.get("patterns") or ())
        )

        # Toda CIU tem de ter ALGUMA forma de resposta, ou não mede nada.
        if not (opcoes or passos or resposta):
            problemas.append("CIU %s não tem alternativas, passos nem resposta" % cid)

        out[cid] = CIU(
            id=cid,
            kc=kc,
            targets=alvos,
            phase=fase or "diagnostic",
            kind=tipo or "multiple_choice",
            stem=c.get("stem", ""),
            code=c.get("code", ""),
            options=opcoes,
            steps=passos,
            wrong_orders=ordens,
            answer=resposta,
            patterns=padroes,
            visual=c.get("visual"),
        )
    return out


# --------------------------------------------------------------------------
# Verificações estruturais
# --------------------------------------------------------------------------

def _check_refs(kcs: Mapping[str, KC], problemas: list[str]) -> None:
    """Toda referência de support e imports tem de resolver."""
    for kc in kcs.values():
        for node in kc.nodes.values():
            for alvo in node.support:
                if alvo[0] not in kcs or alvo[1] not in kcs[alvo[0]].nodes:
                    problemas.append(
                        "%s:%s tem support pendurado: %s:%s" % (*node.ref, *alvo)
                    )
            if node.imports and (
                node.imports[0] not in kcs
                or node.imports[1] not in kcs[node.imports[0]].nodes
            ):
                problemas.append(
                    "%s:%s importa nó inexistente: %s:%s" % (*node.ref, *node.imports)
                )


def _check_acyclic(kcs: Mapping[str, KC], problemas: list[str]) -> None:
    """O grafo de premissas tem de ser um DAG.

    É o que garante que o traversal termina — propriedade garantida aqui,
    não presumida no algoritmo (§7.1).
    """
    BRANCO, CINZA, PRETO = 0, 1, 2
    cor: dict[Ref, int] = {}

    def visitar(ref: Ref, caminho: list[Ref]) -> None:
        if cor.get(ref) == PRETO:
            return
        if cor.get(ref) == CINZA:
            ciclo = caminho[caminho.index(ref):] + [ref]
            problemas.append(
                "ciclo no grafo de premissas: " + " -> ".join("%s:%s" % r for r in ciclo)
            )
            return
        cor[ref] = CINZA
        kc, node = ref
        if kc in kcs and node in kcs[kc].nodes:
            for s in kcs[kc].nodes[node].support:
                visitar(s, caminho + [ref])
        cor[ref] = PRETO

    for kc in kcs.values():
        for node in kc.nodes:
            visitar((kc.id, node), [])


def _check_prerequisites(raw: Mapping, kcs: Mapping[str, KC], problemas: list[str]) -> None:
    """Prerequisitos existem, não têm ciclo, e respeitam teaching_order."""
    for kc in kcs.values():
        for pre in kc.prerequisites:
            if pre not in kcs:
                problemas.append("KC %s requer KC inexistente: %s" % (kc.id, pre))
            elif kcs[pre].teaching_order >= kc.teaching_order:
                problemas.append(
                    "KC %s (ordem %d) requer %s (ordem %d): prerequisito vem depois"
                    % (kc.id, kc.teaching_order, pre, kcs[pre].teaching_order)
                )

    ordens = [k.teaching_order for k in kcs.values()]
    if len(set(ordens)) != len(ordens):
        problemas.append("teaching_order repetido entre KCs: %s" % sorted(ordens))

    seq = raw.get("pilot_sequence") or ()
    for kc_id in seq:
        if kc_id not in kcs:
            problemas.append("pilot_sequence cita KC inexistente: %s" % kc_id)
    ordem_seq = [kcs[k].teaching_order for k in seq if k in kcs]
    if ordem_seq != sorted(ordem_seq):
        problemas.append(
            "pilot_sequence fora da ordem de ensino: %s" % list(seq)
        )
