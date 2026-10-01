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

# Formatos do banco de atividades. Não é taxonomia fechada: é o que a
# regra de variação precisa comparar para não repetir o mesmo molde.
FORMATOS = ("reconhecer_conceito", "comparar_casos", "achar_o_erro", "prever_saida")

# Cada nó tem um par: a pergunta TEÓRICA e a de CÓDIGO. O par é o que
# sustenta a checagem de vacilo — errar a teórica com confiança leva à de
# código antes de a refutação disparar.
TIPOS = ("teorica", "codigo")


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
    tipo: str                      # teorica | codigo
    formato: str
    enunciado: str
    opcoes: tuple[Opcao, ...]
    codigo: str = ""
    crenca: str | None = None      # a crença que um erro aqui levanta

    @property
    def indice_correto(self) -> int:
        return next(i for i, o in enumerate(self.opcoes) if o.correta)

    @property
    def texto(self) -> str:
        """O que o aluno lê: o código, quando há, e o enunciado."""
        return (self.codigo.rstrip() + "\n\n" + self.enunciado).strip()


@dataclass(frozen=True)
class Dominio:
    id: str
    titulo: str
    conclusao: str
    nos: Mapping[str, No]
    crencas: Mapping[str, Crenca]
    atividades: tuple[Atividade, ...] = ()
    # Analogia única do tópico, e a versão dela para cada nó. Quem aparece
    # na validação é a DO NÓ: o resumo mapeia os cinco de uma vez e
    # entregaria a resposta das atividades que ainda não foram feitas.
    analogia: str = ""
    resgates: Mapping[str, str] = field(default_factory=dict)

    def resgate(self, no: str) -> str:
        return self.resgates.get(no) or self.analogia

    def atividades_do_no(self, no: str) -> tuple[Atividade, ...]:
        """As atividades do nó, teórica antes de código."""
        itens = [a for a in self.atividades if a.no == no]
        return tuple(sorted(itens, key=lambda a: TIPOS.index(a.tipo)))

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
    cru_atv = yaml.safe_load((base / "activities_kc00.yaml").read_text(encoding="utf-8"))

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
    for bruto in (cru_atv or {}).get("activities") or ():
        aid = bruto.get("id")
        if aid in vistos:
            problemas.append("atividade %s duplicada" % aid)
        vistos.add(aid)

        # "kc00:B1", "kc_00:B1" e "B1" apontam o mesmo nó num domínio de um
        # tópico só. O que importa é a parte depois dos dois-pontos.
        alvo = str(bruto.get("node", "")).split(":")[-1]
        if alvo not in nos:
            problemas.append("atividade %s mira %r, que não é nó" % (aid, bruto.get("node")))
        if bruto.get("tipo") not in TIPOS:
            problemas.append("atividade %s: tipo inválido %r" % (aid, bruto.get("tipo")))
        if bruto.get("formato") not in FORMATOS:
            problemas.append("atividade %s: formato inválido %r" % (aid, bruto.get("formato")))

        crenca = bruto.get("belief_context")
        if crenca and crenca not in crencas:
            problemas.append("atividade %s: belief_context %r não está no catálogo"
                             % (aid, crenca))
        if crenca and alvo in nos and crencas.get(crenca) and crencas[crenca].nega != alvo:
            problemas.append(
                "atividade %s mira %s mas carrega a crença %s, que nega %s"
                % (aid, alvo, crenca, crencas[crenca].nega))

        # As alternativas vêm como mapa (a/b/c, ou certo/errado) e o gabarito
        # nomeia a chave certa. A ordem é a de escrita: o YAML a preserva.
        alternativas = bruto.get("alternativas") or {}
        gabarito = bruto.get("gabarito")
        if gabarito not in alternativas:
            problemas.append("atividade %s: gabarito %r não está entre as alternativas"
                             % (aid, gabarito))
        opcoes = tuple(
            Opcao(texto=_texto(txt), correta=(chave == gabarito),
                  # Num banco assim, a crença não é de uma alternativa: é do
                  # item. Qualquer erro aqui aponta para a mesma ideia.
                  crenca=None if chave == gabarito else crenca)
            for chave, txt in alternativas.items()
        )
        if len(opcoes) < 2:
            problemas.append("atividade %s: menos de duas alternativas" % aid)

        atividades.append(Atividade(
            id=aid, no=alvo, tipo=bruto.get("tipo", "teorica"),
            formato=bruto.get("formato", "reconhecer_conceito"),
            enunciado=_texto(bruto.get("enunciado")),
            codigo=(bruto.get("codigo") or "").strip("\n"),
            opcoes=opcoes, crenca=crenca,
        ))

    for cid, c in crencas.items():
        if not _texto(((cru_atv or {}).get("resgates") or {}).get(c.nega)):
            problemas.append(
                "nó %s tem crença (%s) e não tem analogia de resgate" % (c.nega, cid))

    # Toda crença precisa de atividade que a levante, e todo nó precisa do
    # par teórica + código: é o par que sustenta a checagem de vacilo.
    for cid in crencas:
        if not any(a.crenca == cid for a in atividades):
            problemas.append("crença %s não é levantada por nenhuma atividade" % cid)
    for nid in nos:
        tipos = {a.tipo for a in atividades if a.no == nid}
        if not tipos:
            problemas.append("nó %s não tem atividade nenhuma" % nid)
        elif tipos != set(TIPOS):
            problemas.append("nó %s não tem o par teórica + código (tem: %s)"
                             % (nid, ", ".join(sorted(tipos))))

    if problemas:
        raise DominioInvalido(problemas)

    return Dominio(
        id=topico.get("id", "kc_00"),
        titulo=_texto(topico.get("title")),
        conclusao=topico.get("conclusion_node", "I1"),
        nos=nos, crencas=crencas, atividades=tuple(atividades),
        analogia=_texto((cru_atv or {}).get("analogy")),
        resgates={k: _texto(v) for k, v in ((cru_atv or {}).get("resgates") or {}).items()},
    )
