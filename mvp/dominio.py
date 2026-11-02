"""Carga do domínio do MVP: tópico, grafo, crenças e atividades.

Lê os quatro YAMLs de `mvp/dominio/` com as chaves que o documento do kc_00
definiu — `type: observavel|inferencia`, `support`, `negated_by`,
`provenance` — e recusa o domínio na carga se algo não fechar.

Falha aqui, nunca em sessão: um YAML inconsistente derruba o processo antes
de qualquer participante ver a tela.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import yaml

RAIZ = Path(__file__).resolve().parent / "dominio"

# O tópico que uma execução carrega. UM por processo: o motor é de uma
# unidade, e o log registra o tópico na abertura da sessão — misturar dois
# num mesmo arquivo faria a reexecução aplicar o domínio errado.
#
#   STRUCTURA_TOPICO=kc_02 python -m mvp.app
#
# Era fixo em "kc_00" dentro de `carrega`, o que bastava enquanto havia um
# tópico só.
TOPICO_PADRAO = os.environ.get("STRUCTURA_TOPICO", "kc_00")

# Quantas PREMISSAS a sessão atravessa, do começo da ordem do grafo.
#
# `docs/plano-tcc.md` define a unidade da coleta em quatro estágios —
# ensina (2 telas), pratica (4 a 6), refuta (3 a 5), fecha (1) — e diz que
# a sessão são DUAS unidades em cerca de 30 minutos. Medido, um nó custa
# 14 telas, das quais 10 são desses quatro estágios: a unidade do plano é
# UMA PREMISSA, e não um tópico inteiro.
#
# O tópico inteiro continua sendo o padrão, porque é o que o motor sempre
# fez e o que os testes medem. Com isto posto, a sessão para em N
# premissas:
#
#   STRUCTURA_TOPICO=kc_12 STRUCTURA_PREMISSAS=2 python -m mvp.app
#
# O corte é por PREFIXO da ordem do grafo — observáveis antes de
# inferências —, e não por nome. Prefixo garante que nenhuma inferência
# fique sem o suporte dela, e isso está conferido nos treze tópicos: não
# há N em que alguma referência de suporte caia fora. Se algum dia
# houver, a carga recusa e diz qual nó e qual suporte — nunca em sessão.
#
# Escolher QUAIS premissas a coleta mede é decisão de pesquisa, e um
# subconjunto por nome permitiria pedir um recorte incoerente (a conclusão
# sem as premissas dela). Se isso fizer falta, entra depois, com a
# checagem de fechamento do suporte.
PREMISSAS_PADRAO = int(os.environ.get("STRUCTURA_PREMISSAS") or 0) or None

# Formatos do banco de atividades. Não é taxonomia fechada: é o que a
# regra de variação precisa comparar para não repetir o mesmo molde.
FORMATOS = ("reconhecer_conceito", "comparar_casos", "achar_o_erro", "prever_saida")

# Cada nó tem um par: a pergunta TEÓRICA e a de CÓDIGO. O par é o que
# sustenta a checagem de vacilo — errar a teórica com confiança leva à de
# código antes de a refutação disparar.
TIPOS = ("teorica", "codigo")

# Onde a atividade entra. O par teorica+codigo do diagnostico sustenta a
# checagem de vacilo; o treino tem banco PROPRIO, para a sequencia de
# acertos nao ser feita de perguntas que o aluno acabou de ver.
#
# `entrada` e o item que vem DEPOIS do ensino, quando a pessoa declarou que
# nao sabe. Ele e o degrau mais baixo do no: existe para a pessoa sair da
# lacuna, nao para discriminar crenca. E opcional — topico sem item de
# entrada constroi assim mesmo, ensinando, e o log registra que faltou.
USOS = ("diagnostico", "treino", "entrada")

# O degrau de dificuldade do item, dentro do no.
#
# O dominio antigo de ponteiros ja tinha `nivel: 1|2|3`, e a curadoria
# descreve a escada: "a sessao comeca no nivel 1 e sobe um degrau por vez;
# topico sem algum degrau nao consegue oferecer a escada inteira". O MVP
# tinha perdido o campo — e a primeira pessoa a atravessar a unidade disse,
# nessas palavras, que parecia "entrar no chefao ja".
NIVEIS = (1, 2, 3)


def topicos(raiz: Path | None = None) -> tuple[str, ...]:
    """Os tópicos que existem no disco, em ordem.

    Existe por um motivo chato: cada tópico novo precisava entrar à mão em
    seis listas de teste espalhadas, e duas delas já estavam defasadas —
    o kc_03 e o kc_04 nunca tinham sido varridos pelos testes de
    construção e de escada. Lista escrita à mão é lista que envelhece.

    O nome do arquivo é a fonte: `topic_kc02.yaml` -> `kc_02`. A ordem é a
    do nome, que para `kc_NN` é a ordem de ensino.
    """
    base = Path(raiz) if raiz else RAIZ
    achados = []
    for caminho in sorted(base.glob("topic_*.yaml")):
        bruto = caminho.stem[len("topic_"):]          # kc02
        achados.append("%s_%s" % (bruto[:2], bruto[2:]) if bruto[:2].isalpha()
                       and bruto[2:].isdigit() else bruto)
    return tuple(achados)


# A DESCIDA: os tipos de evidência que a tela do fim aceita, e de onde a
# saída dela pode ter vindo.
#
# `origem` existe porque a tela promete evidência, e evidência inventada é
# pior que evidência nenhuma:
#
#   gravada   rodamos, e `saida` traz o que saiu; `onde` diz em que
#             máquina e com que compilador
#   citada    a saída está publicada; `onde` traz a citação
#   pendente  ninguém rodou ainda. `saida` fica vazia e a tela mostra o
#             programa com a GARANTIA — o que o padrão obriga —, sem
#             desenhar um terminal que não existiu
TIPOS_EVIDENCIA = ("erro_de_compilacao", "saida_definida", "dois_programas")
ORIGENS_EVIDENCIA = ("gravada", "citada", "pendente")


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
    uso: str = "diagnostico"       # diagnostico | treino | entrada
    nivel: int = 1                 # o degrau: 1, 2 ou 3

    @property
    def indice_correto(self) -> int:
        return next(i for i, o in enumerate(self.opcoes) if o.correta)

    @property
    def texto(self) -> str:
        """O que o aluno lê: o código, quando há, e o enunciado."""
        return (self.codigo.rstrip() + "\n\n" + self.enunciado).strip()


@dataclass(frozen=True)
class Passo:
    """Um degrau da descida.

    ATENÇÃO À INVERSÃO: `decorre` é o que a CRENÇA prevê, e é ele que faz a
    cadeia andar. Não é a resposta certa — é a resposta consistente com o
    erro. `verdade` é o que de fato acontece, e escolhê-lo encerra a
    descida, porque a pessoa acabou de contradizer a própria crença.
    """
    pergunta: str
    decorre: str
    verdade: str
    porque: str


@dataclass(frozen=True)
class Evidencia:
    """O que se mostra a quem sustentou a crença até o último degrau."""
    tipo: str
    fonte: str
    comando: str
    afirmacao: str
    garantia: str
    saida: str = ""
    origem: str = "pendente"
    onde: str = ""

    @property
    def gravada(self) -> bool:
        return self.origem != "pendente" and bool(self.saida)


@dataclass(frozen=True)
class Descida:
    crenca: str
    colide_com: str
    passos: tuple[Passo, ...]
    evidencia: Evidencia


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
    # A pergunta do teach-back, do YAML do tópico.
    teachback: str = ""
    resgates: Mapping[str, str] = field(default_factory=dict)

    def resgate(self, no: str) -> str:
        return self.resgates.get(no) or self.analogia

    exemplos: Mapping[str, str] = field(default_factory=dict)

    def atividades_do_no(self, no: str, uso: str | None = None) -> tuple[Atividade, ...]:
        """As atividades do nó, teórica antes de código."""
        itens = [a for a in self.atividades
                 if a.no == no and (uso is None or a.uso == uso)]
        # Degrau primeiro: a escada manda mais que o par teórica/código.
        return tuple(sorted(itens, key=lambda a: (a.nivel, TIPOS.index(a.tipo))))

    def exemplo(self, no: str) -> str:
        """O código que acompanha a premissa na tela de ensino."""
        return self.exemplos.get(no, "")

    def entrada(self, no: str, usadas: tuple[str, ...] = ()) -> Atividade | None:
        """O item de entrada do nó, se o banco tiver um ainda não usado."""
        return next((a for a in self.atividades_do_no(no, "entrada")
                     if a.id not in usadas), None)

    def crenca_que_nega(self, no: str) -> Crenca | None:
        return next((c for c in self.crencas.values() if c.nega == no), None)

    descidas: Mapping[str, Descida] = field(default_factory=dict)

    def descida(self, crenca: str | None) -> Descida | None:
        """A cadeia daquela crença, se alguém a escreveu.

        Tópico sem descida nenhuma continua funcionando: o motor cai na
        refutação de sempre. É o que torna o protótipo de UMA crença
        possível sem tocar nas outras setenta e oito.
        """
        return self.descidas.get(crenca or "")

    @property
    def ordem(self) -> tuple[str, ...]:
        """Nós na ordem em que a unidade os percorre: base antes da conclusão."""
        base = [n for n in self.nos if self.nos[n].observavel]
        inferencia = [n for n in self.nos if not self.nos[n].observavel]
        return tuple(base + inferencia)


def _texto(valor) -> str:
    return " ".join(str(valor or "").split())


def _corta(alvo: str, quantas: int, cru_topico, grafo,
           cru_crencas, cru_atv, cru_desc) -> None:
    """Deixa só as `quantas` primeiras premissas, no dado CRU.

    Mexe no dado antes de qualquer parse, de propósito: assim todas as
    invariantes da carga — crença que não é apontada por alternativa
    nenhuma, nó sem o par teórica+código, nó sem item de nível 1 — valem
    para o domínio CORTADO, e não para o inteiro. Um corte que produzisse
    um domínio inválido falha na carga, que é onde este projeto quer
    falhar.
    """
    nos = grafo.get("nodes") or {}
    if not isinstance(quantas, int) or isinstance(quantas, bool) or quantas < 1:
        raise DominioInvalido(
            ["premissas=%r: pedi um inteiro de 1 em diante" % (quantas,)])
    if quantas > len(nos):
        raise DominioInvalido(
            ["premissas=%d: o tópico %r tem %d premissa(s)"
             % (quantas, alvo, len(nos))])

    # A MESMA ordem que `Dominio.ordem` usa: observáveis antes de
    # inferências, e dentro de cada grupo a ordem de escrita do YAML.
    ordem = ([k for k, v in nos.items() if v.get("type") == "observavel"]
             + [k for k, v in nos.items() if v.get("type") != "observavel"])
    fica = ordem[:quantas]
    vivos = set(fica)

    faltando = [(nid, s) for nid in fica
                for s in (nos[nid].get("support") or []) if s not in vivos]
    if faltando:
        raise DominioInvalido(
            ["premissas=%d corta %r, que sustenta %r" % (quantas, s, nid)
             for nid, s in faltando])

    grafo["nodes"] = {k: v for k, v in nos.items() if k in vivos}

    crencas_vivas = {c["id"] for c in (cru_crencas or ())
                     if str(c.get("negates", "")).split(":")[-1] in vivos}
    cru_crencas[:] = [c for c in (cru_crencas or ())
                      if c["id"] in crencas_vivas]

    sobram = []
    for a in (cru_atv or {}).get("activities") or ():
        if str(a.get("node", "")).split(":")[-1] not in vivos:
            continue
        a = dict(a)
        # Distrator cuja crença saiu fica SEM crença. O carregador aceita,
        # e a cédula da camada 2 encurta — `razoes_de` já tem o piso de
        # duas razões. É o preço de medir menos premissas.
        a["crencas"] = {k: v for k, v in (a.get("crencas") or {}).items()
                        if v in crencas_vivas}
        sobram.append(a)
    cru_atv["activities"] = sobram
    for chave in ("resgates", "exemplos"):
        if cru_atv.get(chave):
            cru_atv[chave] = {k: v for k, v in cru_atv[chave].items()
                              if k in vivos}

    if cru_topico.get("conclusion_node") not in vivos:
        cru_topico["conclusion_node"] = fica[-1]

    # A descida de uma crença que saiu no corte sai junto.
    if cru_desc and cru_desc.get("descidas"):
        cru_desc["descidas"] = {k: v for k, v in cru_desc["descidas"].items()
                                if k in crencas_vivas}


def carrega(raiz: Path | None = None, topico: str | None = None,
            premissas: int | None = None) -> Dominio:
    base = Path(raiz) if raiz else RAIZ
    alvo = topico or TOPICO_PADRAO

    # O id do tópico tem underscore (`kc_02`) e o nome do arquivo não
    # (`topic_kc02.yaml`). A convenção veio do kc_00 e fica: normalizar
    # aqui custa uma linha e evita um erro de digitação por tópico novo.
    sufixo = alvo.replace("_", "")

    def le(prefixo: str, obrigatorio: bool = True):
        caminho = base / ("%s_%s.yaml" % (prefixo, sufixo))
        if not caminho.exists():
            if not obrigatorio:
                return None
            raise DominioInvalido(
                ["não achei %s: o tópico %r não está em %s"
                 % (caminho.name, alvo, base)])
        return yaml.safe_load(caminho.read_text(encoding="utf-8"))

    cru_topico = le("topic")
    grafo = le("graph")
    cru_crencas = le("beliefs")
    cru_atv = le("activities")
    # Arquivo OPCIONAL: tópico sem descida escrita carrega igual.
    cru_desc = le("descidas", obrigatorio=False) or {}

    quantas = premissas if premissas is not None else PREMISSAS_PADRAO
    if quantas is not None:
        _corta(alvo, quantas, cru_topico, grafo, cru_crencas,
               cru_atv, cru_desc)

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
        if bruto.get("uso", "diagnostico") not in USOS:
            problemas.append("atividade %s: uso inválido %r" % (aid, bruto.get("uso")))
        if bruto.get("tipo") not in TIPOS:
            problemas.append("atividade %s: tipo inválido %r" % (aid, bruto.get("tipo")))
        if bruto.get("formato") not in FORMATOS:
            problemas.append("atividade %s: formato inválido %r" % (aid, bruto.get("formato")))
        if bruto.get("nivel") not in NIVEIS:
            problemas.append("atividade %s: nivel inválido %r (use 1, 2 ou 3)"
                             % (aid, bruto.get("nivel")))

        # As alternativas vêm como mapa (a/b/c, ou certo/errado) e o gabarito
        # nomeia a chave certa. A ordem é a de escrita: o YAML a preserva.
        alternativas = bruto.get("alternativas") or {}
        gabarito = bruto.get("gabarito")
        if gabarito not in alternativas:
            problemas.append("atividade %s: gabarito %r não está entre as alternativas"
                             % (aid, gabarito))

        # A crença é DA ALTERNATIVA, não do item (P1-1). Antes, toda
        # alternativa errada recebia a crença do item inteiro: com três
        # alternativas, as duas erradas ficavam indistinguíveis, e a camada
        # de razão não teria de onde sair.
        if "belief_context" in bruto:
            problemas.append(
                "atividade %s ainda usa belief_context; a crença agora é da "
                "alternativa, em `crencas:`" % aid)
        por_alternativa = bruto.get("crencas") or {}
        for chave, cid in por_alternativa.items():
            if chave not in alternativas:
                problemas.append("atividade %s: crença em %r, que não é alternativa"
                                 % (aid, chave))
            elif chave == gabarito:
                problemas.append(
                    "atividade %s: %r é o gabarito e não pode carregar crença"
                    % (aid, chave))
            if cid not in crencas:
                problemas.append("atividade %s: crença %r não está no catálogo"
                                 % (aid, cid))

        opcoes = tuple(
            Opcao(texto=_texto(txt), correta=(chave == gabarito),
                  crenca=None if chave == gabarito else por_alternativa.get(chave))
            for chave, txt in alternativas.items()
        )
        if len(opcoes) < 2:
            problemas.append("atividade %s: menos de duas alternativas" % aid)

        # A crença DO ITEM é derivada: entre os distratores, a que nega o nó
        # que o item mira. Um distrator que nega outro nó não vira a crença
        # do item — ele é informação sobre o vizinho, e quem trata disso é a
        # camada de razão, que sabe em qual nó registrar.
        crenca = next((o.crenca for o in opcoes
                       if o.crenca and crencas.get(o.crenca)
                       and crencas[o.crenca].nega == alvo), None)

        atividades.append(Atividade(
            id=aid, no=alvo, tipo=bruto.get("tipo", "teorica"),
            formato=bruto.get("formato", "reconhecer_conceito"),
            enunciado=_texto(bruto.get("enunciado")),
            codigo=(bruto.get("codigo") or "").strip("\n"),
            opcoes=opcoes, crenca=crenca,
            uso=bruto.get("uso", "diagnostico"),
            nivel=bruto.get("nivel") if bruto.get("nivel") in NIVEIS else 1,
        ))

    for cid, c in crencas.items():
        if not _texto(((cru_atv or {}).get("resgates") or {}).get(c.nega)):
            problemas.append(
                "nó %s tem crença (%s) e não tem analogia de resgate" % (c.nega, cid))

    # Toda crença precisa de uma ALTERNATIVA que a levante, e todo nó precisa
    # do par teórica + código: é o par que sustenta a checagem de vacilo.
    # A conta é por alternativa, não por item: uma crença que só exista no
    # catálogo é uma razão que nunca vai poder ser escolhida.
    for cid in crencas:
        if not any(o.crenca == cid for a in atividades for o in a.opcoes):
            problemas.append(
                "crença %s não é apontada por nenhuma alternativa" % cid)
    for nid in nos:
        diag = [a for a in atividades if a.no == nid and a.uso == "diagnostico"]
        tipos = {a.tipo for a in diag}
        if not diag:
            problemas.append("nó %s não tem atividade de diagnóstico" % nid)
        elif tipos != set(TIPOS):
            problemas.append("nó %s não tem o par teórica + código (tem: %s)"
                             % (nid, ", ".join(sorted(tipos))))

        # A escada precisa do PRIMEIRO degrau. Sem item de nível 1 o nó
        # começa no meio, que é exatamente o "entrar no chefão já".
        if diag and not any(a.nivel == 1 for a in diag):
            problemas.append(
                "nó %s não tem item de diagnóstico de nível 1 (tem: %s)"
                % (nid, ", ".join(str(a.nivel) for a in diag)))

        # O treino precisa de pelo menos dois itens próprios, de formatos
        # diferentes: é esse o tamanho da sequência que confirma o nó.
        treino = [a for a in atividades if a.no == nid and a.uso == "treino"]
        if len({a.formato for a in treino}) < 2:
            problemas.append(
                "nó %s tem menos de dois formatos no banco de treino "
                "(tem %d item(ns))" % (nid, len(treino)))

    descidas: dict[str, Descida] = {}
    for cid, bruto in (cru_desc.get("descidas") or {}).items():
        onde = "descida %s" % cid
        if cid not in crencas:
            problemas.append("%s: %r não é crença deste tópico" % (onde, cid))
        colide = str(bruto.get("colide_com") or "").split(":")[-1]
        if colide not in nos:
            problemas.append("%s: colide_com %r não é nó deste tópico"
                             % (onde, bruto.get("colide_com")))
        crus = bruto.get("passos") or []
        if len(crus) < 2:
            problemas.append(
                "%s: menos de dois degraus — uma descida de um passo é só "
                "uma pergunta" % onde)
        passos = []
        for i, p in enumerate(crus, 1):
            faltam = [k for k in ("pergunta", "decorre", "verdade", "porque")
                      if not _texto(p.get(k))]
            if faltam:
                problemas.append("%s, degrau %d: falta %s"
                                 % (onde, i, ", ".join(faltam)))
            passos.append(Passo(
                pergunta=_texto(p.get("pergunta")),
                decorre=_texto(p.get("decorre")),
                verdade=_texto(p.get("verdade")),
                porque=_texto(p.get("porque"))))

        ev = bruto.get("evidencia") or {}
        if ev.get("tipo") not in TIPOS_EVIDENCIA:
            problemas.append("%s: evidência de tipo %r (use %s)"
                             % (onde, ev.get("tipo"), ", ".join(TIPOS_EVIDENCIA)))
        if ev.get("origem") not in ORIGENS_EVIDENCIA:
            problemas.append("%s: origem %r (use %s)"
                             % (onde, ev.get("origem"), ", ".join(ORIGENS_EVIDENCIA)))
        if not (ev.get("fonte") or "").strip():
            problemas.append("%s: evidência sem programa" % onde)
        # A tela promete evidência. Saída que diz de onde veio, ou nenhuma.
        if ev.get("origem") in ("gravada", "citada"):
            if not (ev.get("saida") or "").strip():
                problemas.append(
                    "%s: origem %r e saída vazia — ou grava, ou põe pendente"
                    % (onde, ev.get("origem")))
            if not _texto(ev.get("onde")):
                problemas.append(
                    "%s: origem %r sem dizer ONDE (máquina e compilador, ou "
                    "a citação)" % (onde, ev.get("origem")))
        else:
            for k in ("afirmacao", "garantia"):
                if not _texto(ev.get(k)):
                    problemas.append(
                        "%s: evidência pendente sem %s — sem saída gravada, "
                        "é só isto que a tela tem de verdadeiro" % (onde, k))
        descidas[cid] = Descida(
            crenca=cid, colide_com=colide, passos=tuple(passos),
            evidencia=Evidencia(
                tipo=str(ev.get("tipo") or ""),
                fonte=(ev.get("fonte") or "").strip("\n"),
                comando=_texto(ev.get("comando")),
                afirmacao=_texto(ev.get("afirmacao")),
                garantia=_texto(ev.get("garantia")),
                saida=(ev.get("saida") or "").strip("\n"),
                origem=str(ev.get("origem") or ""),
                onde=_texto(ev.get("onde"))))

    if problemas:
        raise DominioInvalido(problemas)

    return Dominio(
        id=cru_topico.get("id", alvo),
        titulo=_texto(cru_topico.get("title")),
        conclusao=cru_topico.get("conclusion_node", "I1"),
        teachback=_texto(cru_topico.get("teachback")),
        nos=nos, crencas=crencas, atividades=tuple(atividades),
        analogia=_texto((cru_atv or {}).get("analogy")),
        resgates={k: _texto(v) for k, v in ((cru_atv or {}).get("resgates") or {}).items()},
        exemplos={k: (v or "").strip("\n")
                  for k, v in ((cru_atv or {}).get("exemplos") or {}).items()},
        descidas=descidas,
    )
