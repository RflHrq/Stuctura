"""Carga e validação do domínio declarativo (RF01).

Princípio §1: falha na carga, nunca em sessão. Se um YAML estiver
inconsistente, `load()` levanta DomainError e o sistema não sobe. Nunca
descobrir isso com um aluno na frente.

Este módulo é o único do motor que toca disco. Todo o resto recebe o
`Domain` pronto e é puro.

SOBRE O SCHEMA: os quatro arquivos de domain/c_pointers/ são a fonte, e
este loader se adapta a eles — não o contrário. Propriedades que o motor
precisa e que os YAMLs não declaram são DERIVADAS aqui (se uma crença é
fundacional, se um KC exige diagrama), nunca acrescentadas ao domínio.
O que é decisão do experimento, e não do conteúdo, vive em study.yaml.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DEFAULT_DOMAIN = RAIZ / "domain" / "c_pointers"
DEFAULT_STUDY = RAIZ / "study.yaml"

# Referência a um nó: (kc, node). Sempre absoluta depois da resolução.
Ref = tuple[str, str]

NODE_TYPES = ("base", "inference")
GRADES = ("D", "T", "L", "N", "E")
CIU_PHASES = ("diagnostic", "traversal", "variation")

# Cada forma de CIU declara os campos que a definem. É o que permite ao
# validador dizer "common_wrong_orders num path_choice" em vez de ignorar
# em silêncio um campo que a interface nunca vai renderizar.
CIU_TYPES: Mapping[str, tuple[str, ...]] = {
    "mcq":         ("options",),
    "prediction":  ("options",),
    "contrast":    ("options",),
    "fill_blank":  ("answer",),
    "parsons":     ("steps_correct",),
    "path_choice": ("paths",),
}

# Campos que só fazem sentido em um tipo. Aparecer em outro é erro.
CIU_EXCLUSIVE: Mapping[str, str] = {
    "options": "escolha",           # mcq | prediction | contrast
    "answer": "fill_blank",
    "accept": "fill_blank",
    "distractor_patterns": "fill_blank",
    "steps_correct": "parsons",
    "common_wrong_orders": "parsons",
    "paths": "path_choice",
}

ESCOLHA = ("mcq", "prediction", "contrast")


class DomainError(Exception):
    """Domínio inconsistente. O sistema não sobe."""

    def __init__(self, problemas: Iterable[str]) -> None:
        self.problemas = list(problemas)
        super().__init__(
            "domínio inválido (%d problema(s)):\n  - %s"
            % (len(self.problemas), "\n  - ".join(self.problemas))
        )


# --------------------------------------------------------------------------
# Entidades
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Node:
    kc: str
    id: str
    type: str
    text: str
    support: tuple[Ref, ...] = ()
    imported_from: Ref | None = None

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
    conclusion: str
    nodes: Mapping[str, Node]

    @property
    def conclusion_ref(self) -> Ref:
        return (self.id, self.conclusion_node)


@dataclass(frozen=True, slots=True)
class Misconception:
    id: str
    kc: str
    node: str
    belief: str
    grade: str
    sources: tuple[str, ...]
    patterns: tuple[str, ...] = ()
    notes: str | None = None
    # DERIVADO do tipo do nó negado, não declarado no YAML.
    kind: str = "derivational"

    @property
    def negates(self) -> Ref:
        return (self.kc, self.node)

    @property
    def is_foundational(self) -> bool:
        """Nega um nó BASE: não há premissa anterior para confrontá-lo, e
        por isso o confronto visual é obrigatório antes do traversal (RF08)."""
        return self.kind == "foundational"


@dataclass(frozen=True, slots=True)
class Option:
    text: str
    correct: bool = False
    misconception: str | None = None


@dataclass(frozen=True, slots=True)
class DistractorPattern:
    """Padrão de resposta livre que revela uma crença."""

    pattern: tuple[str, ...]
    misconception: str | None = None

    def hits(self, texto: str) -> bool:
        alvo = texto.casefold()
        return any(p.casefold() in alvo for p in self.pattern)


@dataclass(frozen=True, slots=True)
class WrongOrder:
    """Permutação errada dos passos de uma CIU `parsons`."""

    order: tuple[str, ...]
    misconception: str | None = None


@dataclass(frozen=True, slots=True)
class PathOption:
    """Um caminho completo numa CIU `path_choice`.

    Distinto de `parsons`: os caminhos têm passos diferentes entre si, não
    são permutação um do outro. Renderizar como arrastar-e-soltar tornaria
    o distrator inatingível.
    """

    label: str
    steps: tuple[str, ...]
    correct: bool = False
    misconception: str | None = None


@dataclass(frozen=True, slots=True)
class CIU:
    id: str
    kc: str
    type: str
    phase: str
    targets: tuple[str, ...]
    prompt: str
    options: tuple[Option, ...] = ()
    answer: str | None = None
    accept: tuple[str, ...] = ()
    distractor_patterns: tuple[DistractorPattern, ...] = ()
    steps_correct: tuple[str, ...] = ()
    common_wrong_orders: tuple[WrongOrder, ...] = ()
    paths: tuple[PathOption, ...] = ()
    visual: Mapping[str, Any] | None = None
    notes: str | None = None

    @property
    def is_choice(self) -> bool:
        return self.type in ESCOLHA

    # NÃO existem `question` e `code` separados de propósito.
    #
    # O `prompt` é um bloco único e a ordem interna varia: em ciu_kc01_001 o
    # código vem antes da pergunta; em ciu_kc09_003 a pergunta vem no meio e
    # os dois trechos comparados vêm depois. Qualquer heurística de corte
    # erra em algum item, e errar aqui significa renderizar código como prosa
    # na frente do participante.
    #
    # A interface apresenta o prompt inteiro em bloco monoespaçado. Se o
    # piloto exigir tipografia diferente para código e enunciado, o YAML
    # precisa carregar essa separação — não o motor adivinhá-la.

    def accepts(self, texto: str) -> bool:
        alvo = texto.strip().casefold()
        return alvo == (self.answer or "").strip().casefold() or any(
            alvo == a.strip().casefold() for a in self.accept
        )

    def misconception_ids(self) -> tuple[str, ...]:
        """Toda crença que esta CIU detecta, por qualquer via."""
        out = [o.misconception for o in self.options if o.misconception]
        out += [p.misconception for p in self.distractor_patterns if p.misconception]
        out += [w.misconception for w in self.common_wrong_orders if w.misconception]
        out += [p.misconception for p in self.paths if p.misconception]
        return tuple(dict.fromkeys(m for m in out if m))


@dataclass(frozen=True, slots=True)
class Study:
    """Configuração do experimento. Não é domínio."""

    def mask(self, texto: str) -> str:
        """Esconde os termos de nomeação tardia num texto de apresentação.

        Da frase mais longa para a mais curta, para que uma substituição de
        duas palavras seja aplicada antes da de uma palavra que a prefixa.
        """
        for termo in sorted(self.late_name_substitutions, key=len, reverse=True):
            substituto = self.late_name_substitutions[termo]
            for variante in (termo, termo.capitalize()):
                texto = texto.replace(variante, substituto)
        return texto

    pilot_sequence: tuple[str, ...] = ()
    late_named_terms: tuple[str, ...] = ()
    late_name_substitutions: Mapping[str, str] = field(default_factory=dict)
    reveal_names: Mapping[str, str] = field(default_factory=dict)
    max_attempts_per_node: int = 3
    diagnostic_policy: str = "all"
    max_diagnostics_per_kc: int = 3
    confidence_scale: tuple[str, ...] = ()

    @property
    def guessed(self) -> str:
        """O valor de confiança que marca premissa AUSENTE, não errada (§7.3)."""
        return self.confidence_scale[0] if self.confidence_scale else "chutei"


@dataclass(frozen=True, slots=True)
class Domain:
    id: str
    kcs: Mapping[str, KC]
    misconceptions: Mapping[str, Misconception]
    cius: Mapping[str, CIU]
    study: Study
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

    def misconceptions_of(self, kc: str) -> tuple[Misconception, ...]:
        return tuple(m for m in self.misconceptions.values() if m.kc == kc)

    def cius_of(self, kc: str, phase: str | None = None) -> tuple[CIU, ...]:
        return tuple(
            c for c in self.cius.values()
            if c.kc == kc and (phase is None or c.phase == phase)
        )

    def attackers(self, kc: str, node: str) -> tuple[Misconception, ...]:
        return tuple(m for m in self.misconceptions.values() if m.negates == (kc, node))

    def requires_diagram(self, kc: str) -> bool:
        """DERIVADO: o KC tem crença que nega nó-base, logo exige confronto
        visual antes do traversal (RF08). Não é declarado no YAML — cai da
        estrutura, que é o ponto do §2.1."""
        return any(m.is_foundational for m in self.misconceptions_of(kc))

    def teaching_sequence(self) -> tuple[str, ...]:
        return tuple(sorted(self.kcs, key=lambda k: self.kcs[k].teaching_order))

    @property
    def pilot_sequence(self) -> tuple[str, ...]:
        return self.study.pilot_sequence


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------

FILES = ("kcs.yaml", "premise_graphs.yaml", "misconceptions.yaml", "cius.yaml")


def load(path: str | Path | None = None, study_path: str | Path | None = None) -> Domain:
    """Carrega, resolve referências cross-KC e valida. Levanta DomainError."""
    base = Path(path) if path is not None else DEFAULT_DOMAIN
    problemas: list[str] = []

    raw: dict[str, Any] = {}
    for nome in FILES:
        arquivo = base / nome
        if not arquivo.exists():
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
    _check_prerequisites(kcs, problemas)

    estudo = _load_study(study_path, kcs, problemas)

    if problemas:
        raise DomainError(problemas)

    return Domain(
        id=raw["kcs.yaml"].get("domain", "unnamed"),
        kcs=kcs,
        misconceptions=miscs,
        cius=cius,
        study=estudo,
        hash=domain_hash(base),
        source=base,
    )


def domain_hash(path: str | Path | None = None) -> str:
    """SHA-256 dos arquivos do domínio, em ordem estável (§15).

    Gravado em `session_started`. Responde "os participantes viram
    exatamente o mesmo conteúdo?" — a primeira pergunta quando os dados
    surpreendem. study.yaml fica de fora: mudar o recorte do piloto não
    muda o conteúdo que o aluno viu.
    """
    base = Path(path) if path is not None else DEFAULT_DOMAIN
    h = hashlib.sha256()
    for nome in FILES:
        arquivo = base / nome
        h.update(nome.encode("utf-8"))
        h.update(arquivo.read_bytes() if arquivo.exists() else b"")
    return "sha256:" + h.hexdigest()


def _load_study(path: str | Path | None, kcs: Mapping[str, KC],
                problemas: list[str]) -> Study:
    arquivo = Path(path) if path is not None else DEFAULT_STUDY
    if not arquivo.exists():
        return Study()
    dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
    seq = tuple(dados.get("pilot_sequence") or ())
    for kc_id in seq:
        if kc_id not in kcs:
            problemas.append("study.yaml: pilot_sequence cita KC inexistente: %s" % kc_id)
    ordens = [kcs[k].teaching_order for k in seq if k in kcs]
    if ordens != sorted(ordens):
        problemas.append("study.yaml: pilot_sequence fora da ordem de ensino: %s" % list(seq))
    return Study(
        pilot_sequence=seq,
        late_named_terms=tuple(dados.get("late_named_terms") or ()),
        late_name_substitutions=dict(dados.get("late_name_substitutions") or {}),
        reveal_names=dict(dados.get("reveal_names") or {}),
        max_attempts_per_node=int(dados.get("max_attempts_per_node", 3)),
        diagnostic_policy=dados.get("diagnostic_policy", "all"),
        max_diagnostics_per_kc=int(dados.get("max_diagnostics_per_kc", 3)),
        confidence_scale=tuple(dados.get("confidence_scale") or ()),
    )


# --------------------------------------------------------------------------
# Construção
# --------------------------------------------------------------------------

def _ref(valor: Any, kc_atual: str, onde: str, problemas: list[str]) -> Ref | None:
    if not isinstance(valor, str):
        problemas.append("%s: referência não é texto: %r" % (onde, valor))
        return None
    if "." in valor:
        kc, _, node = valor.partition(".")
        return (kc, node)
    return (kc_atual, valor)


def _build_kcs(kcs_raw: Mapping, graphs_raw: Mapping, problemas: list[str]) -> dict[str, KC]:
    graphs = graphs_raw.get("graphs") or {}
    out: dict[str, KC] = {}

    for meta in kcs_raw.get("kcs") or []:
        kc_id = meta.get("id")
        if not kc_id:
            problemas.append("kcs.yaml: entrada sem id")
            continue
        grafo = graphs.get(kc_id)
        if grafo is None:
            problemas.append("KC %s sem grafo em premise_graphs.yaml" % kc_id)
            continue

        nodes: dict[str, Node] = {}
        for node_id, nd in (grafo.get("nodes") or {}).items():
            tipo = nd.get("type")
            onde = "%s:%s" % (kc_id, node_id)
            if tipo not in NODE_TYPES:
                problemas.append("%s: tipo inválido %r" % (onde, tipo))
                continue
            sup = tuple(
                r for r in (
                    _ref(s, kc_id, "%s support" % onde, problemas)
                    for s in (nd.get("support") or ())
                ) if r is not None
            )
            if tipo == "base" and sup:
                problemas.append("%s é base mas declara support" % onde)
            if tipo == "inference" and not sup:
                problemas.append("%s é inferência sem support" % onde)
            imp = nd.get("imported_from")
            nodes[node_id] = Node(
                kc=kc_id, id=node_id, type=tipo, text=nd.get("text", ""), support=sup,
                imported_from=_ref(imp, kc_id, "%s imported_from" % onde, problemas)
                if imp else None,
            )
            if not nodes[node_id].text:
                problemas.append("%s sem texto" % onde)

        concl = meta.get("conclusion_node")
        if concl not in nodes:
            problemas.append("KC %s: conclusion_node %r não existe no grafo" % (kc_id, concl))

        out[kc_id] = KC(
            id=kc_id,
            name=meta.get("name", ""),
            teaching_order=int(meta.get("teaching_order", 0)),
            prerequisites=tuple(meta.get("prerequisites") or ()),
            conclusion_node=concl or "",
            conclusion=meta.get("conclusion", ""),
            nodes=nodes,
        )

    declarados = {m.get("id") for m in (kcs_raw.get("kcs") or [])}
    for kc_id in graphs:
        if kc_id not in declarados:
            problemas.append("grafo %s sem KC correspondente em kcs.yaml" % kc_id)

    return out


def _build_misconceptions(
    raw: Mapping, kcs: Mapping[str, KC], problemas: list[str]
) -> dict[str, Misconception]:
    out: dict[str, Misconception] = {}
    for m in raw.get("misconceptions") or []:
        mid = m.get("id")
        kc, node = m.get("kc"), m.get("negates")
        if kc not in kcs or node not in kcs.get(kc, KC("", "", 0, (), "", "", {})).nodes:
            problemas.append("crença %s nega nó inexistente: %s:%s" % (mid, kc, node))
            continue
        if m.get("grade") not in GRADES:
            problemas.append("crença %s: grade inválido %r" % (mid, m.get("grade")))
        if not m.get("sources"):
            problemas.append("crença %s sem fonte declarada" % mid)

        # A classe cai do grafo: nega base => fundacional. Não se declara.
        negado = kcs[kc].nodes[node]
        out[mid] = Misconception(
            id=mid, kc=kc, node=node,
            belief=m.get("belief", ""),
            grade=m.get("grade", "E"),
            sources=tuple(m.get("sources") or ()),
            patterns=tuple(m.get("patterns") or ()),
            notes=m.get("notes"),
            kind="foundational" if negado.is_base else "derivational",
        )
    return out


def _build_cius(
    raw: Mapping, kcs: Mapping[str, KC], miscs: Mapping[str, Misconception],
    problemas: list[str],
) -> dict[str, CIU]:
    out: dict[str, CIU] = {}
    for c in raw.get("cius") or []:
        cid = c.get("id")
        kc = c.get("kc")
        if kc not in kcs:
            problemas.append("CIU %s referencia KC inexistente: %r" % (cid, kc))
            continue

        tipo, fase = c.get("type"), c.get("phase")
        if tipo not in CIU_TYPES:
            problemas.append("CIU %s: type inválido %r" % (cid, tipo))
        if fase not in CIU_PHASES:
            problemas.append("CIU %s: phase inválida %r" % (cid, fase))

        alvos = tuple(c.get("targets") or ())
        if not alvos:
            problemas.append("CIU %s sem nó-alvo: não alimenta a Q-matrix" % cid)
        for t in alvos:
            if t not in kcs[kc].nodes:
                problemas.append("CIU %s: target %s:%s não existe" % (cid, kc, t))

        def mid(valor, onde):
            if valor is not None and valor not in miscs:
                problemas.append("CIU %s (%s): crença desconhecida %r" % (cid, onde, valor))
                return None
            return valor

        opcoes = tuple(
            Option(o.get("text", ""), bool(o.get("correct")),
                   mid(o.get("misconception"), "distrator"))
            for o in (c.get("options") or ())
        )
        padroes = tuple(
            DistractorPattern(tuple(p.get("pattern") or ()),
                              mid(p.get("misconception"), "distractor_pattern"))
            for p in (c.get("distractor_patterns") or ())
        )
        ordens = tuple(
            WrongOrder(tuple(w.get("order") or ()),
                       mid(w.get("misconception"), "common_wrong_order"))
            for w in (c.get("common_wrong_orders") or ())
        )
        caminhos = tuple(
            PathOption(p.get("label", ""), tuple(p.get("steps") or ()),
                       bool(p.get("correct")), mid(p.get("misconception"), "path"))
            for p in (c.get("paths") or ())
        )

        ciu = CIU(
            id=cid, kc=kc, type=tipo or "mcq", phase=fase or "diagnostic",
            targets=alvos, prompt=c.get("prompt", ""),
            options=opcoes,
            answer=c.get("answer"),
            accept=tuple(c.get("accept") or ()),
            distractor_patterns=padroes,
            steps_correct=tuple(c.get("steps_correct") or ()),
            common_wrong_orders=ordens,
            paths=caminhos,
            visual=c.get("visual"),
            notes=c.get("notes"),
        )
        _check_ciu_shape(ciu, c, problemas)
        out[cid] = ciu
    return out


def _check_ciu_shape(ciu: CIU, bruto: Mapping, problemas: list[str]) -> None:
    """Cada forma de CIU tem os campos que a interface sabe renderizar.

    Um campo no tipo errado não quebra nada em execução: só produz uma
    atividade cujo distrator o aluno nunca alcança.
    """
    if ciu.type not in CIU_TYPES:
        return

    for campo in CIU_TYPES[ciu.type]:
        if not bruto.get(campo):
            problemas.append("CIU %s é %s mas não tem %s" % (ciu.id, ciu.type, campo))

    for campo, dono in CIU_EXCLUSIVE.items():
        if not bruto.get(campo):
            continue
        pertence = ciu.type in ESCOLHA if dono == "escolha" else ciu.type == dono
        if not pertence:
            problemas.append(
                "CIU %s é %s e traz %r, que só existe em %s"
                % (ciu.id, ciu.type, campo, dono)
            )

    if ciu.is_choice:
        corretas = [o for o in ciu.options if o.correct]
        if len(corretas) != 1:
            problemas.append(
                "CIU %s: precisa de exatamente 1 alternativa correta, tem %d"
                % (ciu.id, len(corretas))
            )
        if not any(o.misconception for o in ciu.options if not o.correct):
            problemas.append("CIU %s: nenhum distrator mapeado a crença" % ciu.id)

    if ciu.type == "parsons":
        for w in ciu.common_wrong_orders:
            if sorted(w.order) != sorted(ciu.steps_correct):
                problemas.append(
                    "CIU %s é parsons mas a ordem errada não é permutação de "
                    "steps_correct; se são caminhos distintos, o tipo é path_choice"
                    % ciu.id
                )
            if not w.misconception:
                problemas.append("CIU %s: ordem errada sem crença mapeada" % ciu.id)

    if ciu.type == "path_choice":
        corretos = [p for p in ciu.paths if p.correct]
        if len(corretos) != 1:
            problemas.append(
                "CIU %s: path_choice precisa de exatamente 1 caminho correto, tem %d"
                % (ciu.id, len(corretos))
            )
        for p in ciu.paths:
            if not p.correct and not p.misconception:
                problemas.append(
                    "CIU %s: caminho %r não é o correto e não mapeia crença"
                    % (ciu.id, p.label)
                )

    if ciu.type == "fill_blank" and not ciu.answer:
        problemas.append("CIU %s é fill_blank sem answer" % ciu.id)

    # Nem toda CIU pergunta. `fill_blank` afirma com uma lacuna, `parsons`
    # e `path_choice` mandam ordenar ou escolher. Exigir "?" de todas
    # rejeitaria atividades boas.
    if ciu.is_choice and "?" not in ciu.prompt:
        problemas.append("CIU %s é de escolha e o prompt não pergunta nada" % ciu.id)
    if ciu.type == "fill_blank" and "___" not in ciu.prompt:
        problemas.append("CIU %s é fill_blank e o prompt não tem lacuna" % ciu.id)


# --------------------------------------------------------------------------
# Verificações estruturais
# --------------------------------------------------------------------------

def _check_refs(kcs: Mapping[str, KC], problemas: list[str]) -> None:
    for kc in kcs.values():
        for node in kc.nodes.values():
            for alvo in node.support:
                if alvo[0] not in kcs or alvo[1] not in kcs[alvo[0]].nodes:
                    problemas.append("%s:%s tem support pendurado: %s:%s" % (*node.ref, *alvo))
            imp = node.imported_from
            if imp and (imp[0] not in kcs or imp[1] not in kcs[imp[0]].nodes):
                problemas.append("%s:%s importa nó inexistente: %s:%s" % (*node.ref, *imp))


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


def _check_prerequisites(kcs: Mapping[str, KC], problemas: list[str]) -> None:
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
