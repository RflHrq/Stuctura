"""Carga do domínio do MVP: tópico, grafo, crenças e atividades.

Lê os quatro YAMLs de `mvp/dominio/` com as chaves que o documento do kc_00
definiu — `type: observavel|inferencia`, `support`, `negated_by`,
`provenance` — e recusa o domínio na carga se algo não fechar.

Falha aqui, nunca em sessão: um YAML inconsistente derruba o processo antes
de qualquer participante ver a tela.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import yaml

RAIZ = Path(__file__).resolve().parent / "dominio"

FORMATOS = ("reconhecer", "achar_erro", "comparar", "prever")
TRANSFERENCIAS = ("proxima", "media", "distante")
FASES = ("diagnostico", "treino")


class DominioInvalido(Exception):
    def __init__(self, problemas):
        self.problemas = list(problemas)
        super().__init__("domínio inválido (%d problema(s)):\n  - %s"
                         % (len(self.problemas), "\n  - ".join(self.problemas)))


@dataclass(frozen=True)
class No:
    id: str
    tipo: str                      # observavel | inferencia
    texto: str
    simples: str
    suporte: tuple[str, ...] = ()
    negado_por: tuple[str, ...] = ()

    @property
    def observavel(self) -> bool:
        return self.tipo == "observavel"


@dataclass(frozen=True)
class Crenca:
    id: str
    nega: str                      # id do nó, dentro deste tópico
    procedencia: str
    afirma: str                    # como o aluno diria
    fonte: str = ""


@dataclass(frozen=True)
class Opcao:
    texto: str
    correta: bool = False
    crenca: str | None = None


@dataclass(frozen=True)
class Atividade:
    id: str
    no: str
    fase: str
    formato: str
    transferencia: str
    enunciado: str
    opcoes: tuple[Opcao, ...]

    @property
    def indice_correto(self) -> int:
        return next(i for i, o in enumerate(self.opcoes) if o.correta)


@dataclass(frozen=True)
class Dominio:
    id: str
    titulo: str
    conclusao: str
    nos: Mapping[str, No]
    crencas: Mapping[str, Crenca]
    atividades: tuple[Atividade, ...] = ()

    def atividades_do_no(self, no: str, fase: str) -> tuple[Atividade, ...]:
        return tuple(a for a in self.atividades if a.no == no and a.fase == fase)

    def crenca_que_nega(self, no: str) -> Crenca | None:
        return next((c for c in self.crencas.values() if c.nega == no), None)

    @property
    def ordem(self) -> tuple[str, ...]:
        """Nós na ordem em que a unidade os percorre: base antes da conclusão."""
        base = [n for n in self.nos if self.nos[n].observavel]
        inferencia = [n for n in self.nos if not self.nos[n].observavel]
        return tuple(base + inferencia)


def _texto(valor) -> str:
    return " ".join(str(valor or "").split())


def carrega(raiz: Path | None = None) -> Dominio:
    base = Path(raiz) if raiz else RAIZ
    topico = yaml.safe_load((base / "topic_kc00.yaml").read_text(encoding="utf-8"))
    grafo = yaml.safe_load((base / "graph_kc00.yaml").read_text(encoding="utf-8"))
    cru_crencas = yaml.safe_load((base / "beliefs_kc00.yaml").read_text(encoding="utf-8"))
    cru_atv = yaml.safe_load((base / "atividades_kc00.yaml").read_text(encoding="utf-8"))

    problemas: list[str] = []

    nos: dict[str, No] = {}
    for nid, bruto in (grafo.get("nodes") or {}).items():
        tipo = bruto.get("type")
        if tipo not in ("observavel", "inferencia"):
            problemas.append("nó %s: type inválido %r" % (nid, tipo))
        nos[nid] = No(
            id=nid, tipo=tipo or "observavel",
            texto=_texto(bruto.get("text")),
            simples=_texto(bruto.get("plain_text")) or _texto(bruto.get("text")),
            suporte=tuple(bruto.get("support") or ()),
            negado_por=tuple(bruto.get("negated_by") or ()),
        )

    for nid, no in nos.items():
        for s in no.suporte:
            if s not in nos:
                problemas.append("nó %s: suporte %r não existe" % (nid, s))
        if not no.observavel and not no.suporte:
            problemas.append("nó %s é inferência e não tem suporte" % nid)

    crencas: dict[str, Crenca] = {}
    for bruto in cru_crencas or ():
        cid = bruto.get("id")
        alvo = str(bruto.get("negates", ""))
        # "kc_00:B2" e "B2" são a mesma coisa num domínio de um tópico só.
        no_alvo = alvo.split(":")[-1]
        if no_alvo not in nos:
            problemas.append("crença %s nega %r, que não é nó deste tópico"
                             % (cid, alvo))
        crencas[cid] = Crenca(
            id=cid, nega=no_alvo,
            procedencia=bruto.get("provenance", "E"),
            afirma=_texto(bruto.get("label_pt")),
            fonte=_texto(bruto.get("source")),
        )

    # Uma crença nega exatamente um nó, e o nó aponta de volta. Divergir
    # aqui significa que o grafo e o catálogo discordam — e o percurso de
    # refutação sairia errado, em silêncio.
    for nid, no in nos.items():
        for cid in no.negado_por:
            if cid not in crencas:
                problemas.append("nó %s é negado por %r, que não está no catálogo"
                                 % (nid, cid))
            elif crencas[cid].nega != nid:
                problemas.append("crença %s nega %s no catálogo e %s no grafo"
                                 % (cid, crencas[cid].nega, nid))

    atividades: list[Atividade] = []
    vistos: set[str] = set()
    for bruto in (cru_atv or {}).get("atividades") or ():
        aid = bruto.get("id")
        if aid in vistos:
            problemas.append("atividade %s duplicada" % aid)
        vistos.add(aid)
        if bruto.get("premissa") not in nos:
            problemas.append("atividade %s mira %r, que não é nó" % (aid, bruto.get("premissa")))
        if bruto.get("fase") not in FASES:
            problemas.append("atividade %s: fase inválida %r" % (aid, bruto.get("fase")))
        if bruto.get("formato") not in FORMATOS:
            problemas.append("atividade %s: formato inválido %r" % (aid, bruto.get("formato")))
        if bruto.get("transferencia") not in TRANSFERENCIAS:
            problemas.append("atividade %s: transferência inválida %r"
                             % (aid, bruto.get("transferencia")))
        opcoes = tuple(
            Opcao(texto=_texto(o.get("texto")), correta=bool(o.get("correta")),
                  crenca=o.get("crenca"))
            for o in bruto.get("opcoes") or ()
        )
        if sum(1 for o in opcoes if o.correta) != 1:
            problemas.append("atividade %s: precisa de exatamente uma correta" % aid)
        for o in opcoes:
            if o.crenca and o.crenca not in crencas:
                problemas.append("atividade %s: distrator aponta crença %r inexistente"
                                 % (aid, o.crenca))
            if o.crenca and o.correta:
                problemas.append("atividade %s: alternativa correta não carrega crença" % aid)
        atividades.append(Atividade(
            id=aid, no=bruto["premissa"], fase=bruto["fase"], formato=bruto["formato"],
            transferencia=bruto["transferencia"],
            enunciado=(bruto.get("enunciado") or "").strip("\n"),
            opcoes=opcoes,
        ))

    # Sem diagnóstica não há como a crença aparecer; sem itens de treino
    # suficientes, o nó nunca fecha a sequência (RF36 cuida do caso, mas o
    # domínio não deveria nascer assim).
    for cid, c in crencas.items():
        if not any(o.crenca == cid for a in atividades if a.fase == "diagnostico"
                   for o in a.opcoes):
            problemas.append("crença %s não é oferecida por nenhuma diagnóstica" % cid)
    for nid in nos:
        treino = [a for a in atividades if a.no == nid and a.fase == "treino"]
        if nos[nid].negado_por and len({a.formato for a in treino}) < 2:
            problemas.append(
                "nó %s tem crença mapeada mas menos de dois formatos de treino" % nid)

    if problemas:
        raise DominioInvalido(problemas)

    return Dominio(
        id=topico.get("id", "kc_00"),
        titulo=_texto(topico.get("title")),
        conclusao=topico.get("conclusion_node", "I1"),
        nos=nos, crencas=crencas, atividades=tuple(atividades),
    )
