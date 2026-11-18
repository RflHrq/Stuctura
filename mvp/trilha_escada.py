"""A escada da premissa: o conteúdo passo a passo da trilha.

    escadas = le(Path("mvp/dominio/escada_kc00.yaml"), dominio)
    correcao = corrige(versao, "montar", pecas=(0, 1, 2))

Uma escada é a sequência de degraus de UMA premissa, do mais mecânico
até a ideia (docs/trilha.md, 6.16). Explicar e exercitar são a mesma
sequência: um degrau guiado é uma ou duas frases e um exercício pequeno;
um degrau de prática é só o exercício, um pouco maior que o anterior.

Todo exercício é de PRODUZIR — tocar numa parte, montar uma linha,
escolher, completar, digitar —, e a correção é exata: sem compilador na
sessão e sem adivinhar. Cada versão de um degrau lista as respostas
aceitas e os erros previstos, cada erro com o seu retorno.

O compilador entra ANTES, quando o conteúdo é escrito: quem confere que
a linha dita certa compila, e que a dita inválida é recusada, é o
`scripts/confere_escada.py`. Este módulo é puro: lê, valida e corrige.

A VALIDAÇÃO É A RÉGUA, na parte que programa consegue medir: de três a
sete degraus, os guiados antes dos de prática, uma ou duas frases curtas
por degrau guiado, duas versões por degrau. O que ela não mede — se o
texto ensina — é leitura humana.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from mvp.dominio import Dominio

FORMAS = ("tocar", "montar", "escolher", "completar", "digitar")
# As formas em que a resposta é UMA peça. Em `montar` é uma sequência, e
# em `digitar` é texto.
UMA_PECA = ("tocar", "escolher", "completar")

MIN_DEGRAUS, MAX_DEGRAUS = 3, 7
MIN_PRATICA = 2
MIN_VERSOES = 2
MAX_FRASES, MAX_PALAVRAS = 2, 30
MAX_FRASES_DA_REVISAO = 3
MAX_PALAVRAS_DO_NOME = 12

LACUNA = "___"

# Na saída esperada de uma prova, um endereço DE EXEMPLO. O número de um
# lugar muda a cada máquina e a cada execução: a prova mostra um número
# curto no lugar dele, e o conferidor compara a forma, não o número.
ENDERECO_DE_EXEMPLO = re.compile(r"0x[0-9A-Fa-f]+")

# As opções de compilador que uma prova pode pedir a mais. A lista é
# fechada porque o que está em `avisos` vira argumento de comando.
# `-fanalyzer` entrou com o kc_01: é o analisador de fluxo do gcc, o que
# aponta o bloco pedido com malloc e nunca devolvido. `-Wpointer-arith`
# entrou com o kc_11: conta em void * o gcc aceita por extensão própria,
# e só reclama dela com esse aviso.
AVISOS_PERMITIDOS = ("-O1", "-O2", "-Wextra", "-Wnull-dereference",
                     "-fanalyzer", "-Wpointer-arith")


class EscadaInvalida(Exception):
    """O arquivo da escada tem problema. `problemas` traz TODOS, de uma vez."""

    def __init__(self, problemas) -> None:
        self.problemas = list(problemas)
        super().__init__("escada inválida:\n  " + "\n  ".join(self.problemas))


class RespostaInvalida(ValueError):
    """A resposta não é uma resposta: peça repetida, índice fora da faixa.

    Não é resposta errada, e a diferença importa: errada vira retorno para
    a pessoa; inválida é pedido malformado, e não pode virar episódio.
    """


@dataclass(frozen=True)
class Erro:
    """Um erro previsto, com o retorno dele."""

    retorno: str
    exata: tuple[int, ...] = ()   # a resposta, em índices do ARQUIVO
    sem: tuple[int, ...] = ()     # montar: sequência que não usa NENHUMA destas
    texto: str = ""               # digitar
    invalida: bool = False        # a linha formada não compila
    crenca: str = ""              # id de crença do tópico


@dataclass(frozen=True)
class Versao:
    """Um degrau com valores concretos. A segunda versão troca os valores."""

    pede: str
    mostra: str = ""              # em `completar`, contém LACUNA uma vez
    antes: str = ""               # linhas de C que vêm antes
    pecas: tuple[str, ...] = ()
    certa: tuple[tuple[int, ...], ...] = ()
    aceitas: tuple[str, ...] = ()
    certa_texto: str = ""
    invalidas: tuple[int, ...] = ()
    programa: str = ""
    erros: tuple[Erro, ...] = ()
    retorno_geral: str = ""


@dataclass(frozen=True)
class Degrau:
    id: str
    guiado: bool
    forma: str
    codigo: bool
    frases: tuple[str, ...]
    versoes: tuple[Versao, ...]
    # O nome curto do passo, que diz a IDEIA dele. É o que o fechamento
    # mostra quando a pessoa tropeça ali: o enunciado de um exercício de
    # prever a saída não diz qual ideia foi.
    nome: str = ""


@dataclass(frozen=True)
class Revisao:
    """O exemplo resolvido da premissa, para quem errou o topo da escada."""

    frases: tuple[str, ...]
    codigo: str
    saida: str = ""               # vazia: o trecho não é executado


@dataclass(frozen=True)
class Previsao:
    """O que a pessoa responde ANTES de ver a máquina.

    `real` é a alternativa que a máquina confirma; `crenca`, a que a
    crença espera. São diferentes por construção: se a crença previsse o
    que a máquina faz, a prova não a refutaria.
    """

    pergunta: str
    opcoes: tuple[str, ...]
    real: int
    crenca: int


@dataclass(frozen=True)
class Prova:
    """A demonstração que responde a UMA crença, em código de iniciante.

    `programa` é só o trecho que a pessoa lê — o `main` em volta é do
    conferidor. A prova é uma de duas coisas: o que o programa IMPRIME
    (`espera`), ou o que o compilador DIZ dele (`reclama`, um pedaço da
    mensagem). A segunda nunca é executada.
    """

    crenca: str
    programa: str
    afirma: str
    previsao: Previsao
    espera: str = ""
    reclama: str = ""
    ambiente: str = ""
    # Com `reclama`: o pedaço de mensagem que NÃO pode aparecer ("de p
    # ele não reclama"), e as opções de compilador a mais que o aviso
    # pede. O conferidor confere as duas coisas.
    cala: str = ""
    avisos: tuple[str, ...] = ()


@dataclass(frozen=True)
class Escada:
    premissa: str
    degraus: tuple[Degrau, ...]
    revisao: Revisao
    provas: tuple[Prova, ...] = ()
    # Questões de marcar desta premissa que a trilha NÃO serve: usam o
    # que a escada do tópico não ensina. O banco não muda — o fluxo
    # anterior, que tem cartão para cada construto, continua servindo.
    fora: tuple[str, ...] = ()

    @property
    def guiados(self) -> tuple[Degrau, ...]:
        return tuple(g for g in self.degraus if g.guiado)

    @property
    def pratica(self) -> tuple[Degrau, ...]:
        return tuple(g for g in self.degraus if not g.guiado)

    def prova(self, crenca: str) -> Prova | None:
        """A prova que responde a esta crença, se a escada tem uma."""
        return next((p for p in self.provas if p.crenca == crenca), None)


@dataclass(frozen=True)
class Correcao:
    certa: bool
    retorno: str = ""
    mostra_certa: str = ""
    crenca: str = ""


# --------------------------------------------------------------------------
# A leitura
# --------------------------------------------------------------------------

def _str(valor: Any) -> str:
    return valor if isinstance(valor, str) else ""


def _strs(valor: Any) -> tuple[str, ...]:
    if not isinstance(valor, (list, tuple)):
        return ()
    return tuple(str(x) for x in valor)


def _indices(valor: Any) -> tuple[int, ...]:
    if not isinstance(valor, (list, tuple)):
        return ()
    return tuple(x for x in valor
                 if isinstance(x, int) and not isinstance(x, bool))


def _fora(seq: tuple[int, ...], quantas: int) -> bool:
    return any(not 0 <= i < quantas for i in seq)


def _erro(cru: Any) -> Erro:
    cru = cru if isinstance(cru, Mapping) else {}
    return Erro(
        retorno=_str(cru.get("retorno")).strip(),
        exata=_indices(cru.get("exata")),
        sem=_indices(cru.get("sem")),
        texto=str(cru.get("texto", "") or ""),
        invalida=bool(cru.get("invalida", False)),
        crenca=_str(cru.get("crenca")),
    )


def _versao(cru: Any) -> Versao:
    cru = cru if isinstance(cru, Mapping) else {}
    certa = cru.get("certa")
    return Versao(
        pede=_str(cru.get("pede")).strip(),
        mostra=_str(cru.get("mostra")),
        antes=_str(cru.get("antes")),
        pecas=_strs(cru.get("pecas")),
        certa=tuple(_indices(s) for s in certa)
        if isinstance(certa, (list, tuple)) else (),
        aceitas=_strs(cru.get("aceitas")),
        certa_texto=_str(cru.get("certa_texto")).strip(),
        invalidas=_indices(cru.get("invalidas")),
        programa=_str(cru.get("programa")),
        erros=tuple(_erro(x) for x in (cru.get("erros") or ())),
        retorno_geral=_str(cru.get("retorno_geral")).strip(),
    )


def _confere_versao(onde: str, forma: str, codigo: bool, v: Versao,
                    d: Dominio, problemas: list[str]) -> None:
    if not v.pede:
        problemas.append("%s: sem o que se pede (`pede`)" % onde)
    if not v.certa_texto:
        problemas.append("%s: sem certa_texto — é o que a tela mostra "
                         "quando a pessoa erra" % onde)
    if not v.retorno_geral:
        problemas.append("%s: sem retorno geral" % onde)

    n = len(v.pecas)
    if forma == "digitar":
        if not v.aceitas:
            problemas.append("%s: sem resposta aceita (`aceitas`)" % onde)
        # O programa pode vir inteiro em `programa`, ou só o trecho em
        # `mostra` — aí o conferidor o embrulha num `main`, e o que a
        # pessoa lê e o que o compilador roda são o MESMO texto.
        if codigo and not (v.programa.strip() or v.mostra.strip()):
            problemas.append("%s: digitar sem programa — a resposta é a "
                             "saída de um programa que o compilador roda"
                             % onde)
    else:
        if not v.pecas:
            problemas.append("%s: sem peças" % onde)
        if not v.certa or any(not s for s in v.certa):
            problemas.append("%s: sem resposta aceita (`certa`)" % onde)
        for s in v.certa:
            if _fora(s, n):
                problemas.append("%s: peça fora da faixa em `certa` %s"
                                 % (onde, list(s)))
            if len(set(s)) != len(s):
                problemas.append("%s: peça repetida em `certa` %s"
                                 % (onde, list(s)))
            if forma in UMA_PECA and len(s) != 1:
                problemas.append("%s: em `%s` a resposta é uma peça só, e "
                                 "veio %s" % (onde, forma, list(s)))
        if _fora(v.invalidas, n):
            problemas.append("%s: peça fora da faixa em `invalidas`" % onde)
    if forma == "completar" and v.mostra.count(LACUNA) != 1:
        problemas.append("%s: a lacuna (%s) tem de aparecer uma vez em "
                         "`mostra`" % (onde, LACUNA))

    aceitas = {a.strip() for a in v.aceitas}
    for i, x in enumerate(v.erros):
        aqui = "%s/erro %d" % (onde, i + 1)
        if not x.retorno:
            problemas.append("%s: erro previsto sem retorno" % aqui)
        if _fora(x.exata, n) or _fora(x.sem, n):
            problemas.append("%s: peça fora da faixa" % aqui)
        casa_com_certa = (
            (x.exata and x.exata in v.certa)
            or (x.sem and any(not set(x.sem) & set(s) for s in v.certa))
            or (forma == "digitar" and x.texto.strip() in aceitas))
        if casa_com_certa:
            problemas.append("%s: erro previsto é uma resposta aceita" % aqui)
        if x.crenca and x.crenca not in d.crencas:
            problemas.append("%s: crença desconhecida: %s" % (aqui, x.crenca))


def _escada(premissa: str, cru: Any, d: Dominio, vistos: set[str],
            problemas: list[str]) -> Escada:
    cru = cru if isinstance(cru, Mapping) else {}
    brutos = cru.get("degraus")
    brutos = brutos if isinstance(brutos, list) else []

    degraus: list[Degrau] = []
    ja_teve_pratica = False
    for i, b in enumerate(brutos):
        b = b if isinstance(b, Mapping) else {}
        did = _str(b.get("id")) or "%s[%d]" % (premissa, i + 1)
        onde = "%s/%s" % (premissa, did)
        if did in vistos:
            problemas.append("%s: id repetido" % onde)
        vistos.add(did)

        guiado = bool(b.get("guiado", False))
        forma = _str(b.get("forma"))
        codigo = bool(b.get("codigo", False))
        frases = tuple(f.strip() for f in _strs(b.get("frases")))
        versoes = tuple(_versao(v) for v in (b.get("versoes") or ()))
        nome = " ".join(_str(b.get("nome")).split())
        if len(nome.split()) > MAX_PALAVRAS_DO_NOME:
            problemas.append("%s: o nome do passo tem mais de %d palavras — "
                             "é um nome, e não uma frase"
                             % (onde, MAX_PALAVRAS_DO_NOME))

        if guiado and ja_teve_pratica:
            problemas.append("%s: degrau guiado depois de prática — os "
                             "guiados vêm antes" % onde)
        if not guiado:
            ja_teve_pratica = True

        if guiado:
            if not frases:
                problemas.append("%s: degrau guiado sem frase" % onde)
            if len(frases) > MAX_FRASES:
                problemas.append("%s: no máximo %d frases por degrau, e "
                                 "vieram %d" % (onde, MAX_FRASES, len(frases)))
            for f in frases:
                if len(f.split()) > MAX_PALAVRAS:
                    problemas.append("%s: frase com mais de %d palavras"
                                     % (onde, MAX_PALAVRAS))
        elif frases:
            problemas.append("%s: degrau de prática não tem frase — é só o "
                             "exercício" % onde)

        if len(versoes) < MIN_VERSOES:
            problemas.append("%s: ao menos %d versões por degrau, e há %d"
                             % (onde, MIN_VERSOES, len(versoes)))
        if forma not in FORMAS:
            problemas.append("%s: forma desconhecida: %r" % (onde, forma))
        else:
            for k, v in enumerate(versoes):
                _confere_versao("%s/versão %d" % (onde, k + 1), forma, codigo,
                                v, d, problemas)
        degraus.append(Degrau(did, guiado, forma, codigo, frases, versoes,
                              nome))

    if len(degraus) < MIN_DEGRAUS:
        problemas.append("%s: ao menos %d degraus, e há %d"
                         % (premissa, MIN_DEGRAUS, len(degraus)))
    if len(degraus) > MAX_DEGRAUS:
        problemas.append("%s: no máximo %d degraus, e há %d"
                         % (premissa, MAX_DEGRAUS, len(degraus)))
    pratica = sum(1 for g in degraus if not g.guiado)
    if pratica < MIN_PRATICA:
        problemas.append("%s: ao menos %d degraus de prática, e há %d — o "
                         "treino e a reconferência saem deles"
                         % (premissa, MIN_PRATICA, pratica))

    r = cru.get("revisao")
    r = r if isinstance(r, Mapping) else {}
    revisao = Revisao(frases=tuple(f.strip() for f in _strs(r.get("frases"))),
                      codigo=_str(r.get("codigo")),
                      saida=_str(r.get("saida")).strip())
    if not revisao.frases:
        problemas.append("%s: revisão sem frase" % premissa)
    if len(revisao.frases) > MAX_FRASES_DA_REVISAO:
        problemas.append("%s: revisão com mais de %d frases"
                         % (premissa, MAX_FRASES_DA_REVISAO))
    if not revisao.codigo.strip():
        problemas.append("%s: revisão sem código" % premissa)
    provas = _provas(premissa, cru.get("provas"), d, problemas)
    fora = _fora_da_trilha(premissa, cru.get("fora_da_trilha"), d, problemas)
    return Escada(premissa, tuple(degraus), revisao, provas, fora)


def _fora_da_trilha(premissa: str, cru: Any, d: Dominio,
                    problemas: list[str]) -> tuple[str, ...]:
    """As questões da premissa que a trilha não serve.

    Tem de sobrar com o que ABRIR a premissa: uma questão de diagnóstico
    em que algum distrator diz uma crença — é a razão marcada que diz
    qual, e sem ela a abertura não mede nada.
    """
    fora = _strs(cru)
    por_id = {a.id: a for a in d.atividades}
    for i in fora:
        if i not in por_id:
            problemas.append("%s: questão desconhecida em fora_da_trilha: %r"
                             % (premissa, i))
        elif por_id[i].no != premissa:
            problemas.append("%s: %s não é desta premissa — é do %s"
                             % (premissa, i, por_id[i].no))
    sobra = [a for a in d.atividades_do_no(premissa, "diagnostico")
             if a.id not in fora
             and any(o.crenca in d.crencas for o in a.opcoes if o.crenca)]
    if fora and not sobra:
        problemas.append("%s: com essas questões fora, a premissa fica sem "
                         "pergunta de abertura" % premissa)
    return fora


def _inteiro(valor: Any) -> int:
    """Um índice, ou -1 — que fica fora de qualquer faixa."""
    ok = isinstance(valor, int) and not isinstance(valor, bool)
    return valor if ok else -1


def _provas(premissa: str, cru: Any, d: Dominio,
            problemas: list[str]) -> tuple[Prova, ...]:
    """As provas da premissa: uma por crença que a nega.

    São opcionais — sem prova na escada, a trilha mostra a demonstração
    do grafo. Mas a que vier tem de estar inteira: é ela que a pessoa vê
    na tela em que o sistema diz "a máquina respondeu".
    """
    provas: list[Prova] = []
    vistas: set[str] = set()
    for b in (cru if isinstance(cru, list) else []):
        b = b if isinstance(b, Mapping) else {}
        crenca = _str(b.get("crenca"))
        onde = "%s/prova de %s" % (premissa, crenca or "?")

        if crenca not in d.crencas:
            problemas.append("%s: crença desconhecida: %r" % (onde, crenca))
        elif d.crencas[crenca].nega != premissa:
            problemas.append("%s: a crença nega %s, e não %s — a prova dela "
                             "mora lá" % (onde, d.crencas[crenca].nega,
                                          premissa))
        if crenca in vistas:
            problemas.append("%s: mais de uma prova para a mesma crença" % onde)
        vistas.add(crenca)

        programa = _str(b.get("programa"))
        espera = str(b.get("espera", "") or "").strip()
        reclama = " ".join(_str(b.get("reclama")).split())
        afirma = " ".join(_str(b.get("afirma")).split())
        if not programa.strip():
            problemas.append("%s: sem programa" % onde)
        if "#include" in programa or "main" in programa:
            problemas.append("%s: o programa é só o trecho que a pessoa lê — "
                             "sem #include e sem main" % onde)
        if bool(espera) == bool(reclama):
            problemas.append("%s: a prova é `espera` ou `reclama`, uma das "
                             "duas — o que o programa imprime, ou o que o "
                             "compilador diz dele" % onde)
        if not afirma:
            problemas.append("%s: sem `afirma` — é a frase que diz o que a "
                             "máquina mostrou" % onde)
        ambiente = " ".join(_str(b.get("ambiente")).split())
        if ENDERECO_DE_EXEMPLO.search(espera) and not ambiente:
            problemas.append("%s: a saída traz endereço de exemplo, e a tela "
                             "a mostra como resposta da máquina — `ambiente` "
                             "tem de dizer que o número é de exemplo" % onde)
        cala = " ".join(_str(b.get("cala")).split())
        avisos = tuple(_str(b.get("avisos")).split())
        if (cala or avisos) and not reclama:
            problemas.append("%s: `cala` e `avisos` só fazem sentido com "
                             "`reclama` — são do que o compilador diz" % onde)
        proibidas = [a for a in avisos if a not in AVISOS_PERMITIDOS]
        if proibidas:
            problemas.append("%s: opção de compilador não permitida em "
                             "`avisos`: %s — só passam %s"
                             % (onde, " ".join(proibidas),
                                " ".join(AVISOS_PERMITIDOS)))
        if avisos and not ambiente:
            problemas.append("%s: o aviso só sai com opções a mais do "
                             "compilador — `ambiente` tem de dizer quais"
                             % onde)

        pv = b.get("previsao")
        if not isinstance(pv, Mapping):
            problemas.append("%s: sem previsão — a pessoa se compromete "
                             "antes de ver a máquina" % onde)
            pv = {}
        previsao = Previsao(
            pergunta=_str(pv.get("pergunta")).strip(),
            opcoes=tuple(o.strip() for o in _strs(pv.get("opcoes"))),
            real=_inteiro(pv.get("real")), crenca=_inteiro(pv.get("crenca")))
        if pv:
            n = len(previsao.opcoes)
            if not previsao.pergunta:
                problemas.append("%s: previsão sem pergunta" % onde)
            if n < 2:
                problemas.append("%s: a previsão pede ao menos duas "
                                 "alternativas" % onde)
            elif _fora((previsao.real, previsao.crenca), n):
                problemas.append("%s: `real` ou `crenca` fora da faixa das "
                                 "alternativas da previsão" % onde)
            elif previsao.real == previsao.crenca:
                problemas.append("%s: a alternativa da crença não pode ser a "
                                 "mesma que a máquina confirma" % onde)

        provas.append(Prova(crenca=crenca, programa=programa, afirma=afirma,
                            previsao=previsao, espera=espera, reclama=reclama,
                            ambiente=ambiente, cala=cala, avisos=avisos))
    return tuple(provas)


def le(caminho: Path, d: Dominio) -> dict[str, Escada]:
    """As escadas de um arquivo, validadas contra o domínio do tópico.

    Valida o que está NO ARQUIVO. Se o tópico inteiro está coberto é
    outra pergunta, e quem a responde é `faltando`.
    """
    cru = yaml.safe_load(Path(caminho).read_text(encoding="utf-8")) or {}
    if not isinstance(cru, Mapping):
        raise EscadaInvalida(["%s: o arquivo não é um mapa de premissas"
                              % caminho])
    problemas: list[str] = []
    vistos: set[str] = set()
    escadas: dict[str, Escada] = {}
    for chave, bloco in cru.items():
        premissa = str(chave)
        if premissa not in d.nos:
            problemas.append("premissa desconhecida no tópico %s: %s"
                             % (d.id, premissa))
            continue
        escadas[premissa] = _escada(premissa, bloco, d, vistos, problemas)
    if problemas:
        raise EscadaInvalida(problemas)
    return escadas


def assinatura(escadas: Mapping[str, Escada]) -> str:
    """Doze dígitos que mudam quando o conteúdo das escadas muda.

    Vai para o registro na abertura de cada sessão. A escada é conteúdo
    que ainda vai ser lido e corrigido, e uma sessão refeita pelas
    entradas contra OUTRA escada daria um estado plausível e errado — as
    entradas são posições de peças, e as peças teriam mudado.

    Sai do `repr` das estruturas congeladas, na ordem das premissas: tudo
    o que chega à tela ou decide uma correção entra na conta.
    """
    texto = repr(sorted(escadas.items()))
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def faltando(d: Dominio, escadas: Mapping[str, Escada]) -> tuple[str, ...]:
    """As premissas do tópico que ainda não têm escada, na ordem do grafo."""
    return tuple(n for n in d.ordem if n not in escadas)


# --------------------------------------------------------------------------
# A ordem das peças
# --------------------------------------------------------------------------

def ordem_das_pecas(semente: str, degrau: str, versao: int, forma: str,
                    n: int) -> tuple[int, ...]:
    """A ordem em que as peças aparecem. Índices do ARQUIVO na ordem da TELA.

    Estável e derivada da semente, como a ordem das alternativas no motor
    atual: a mesma sessão redesenha a mesma tela, e nada é sorteado.

    `tocar` não embaralha — as peças são a própria linha, na ordem em que
    se lê. `digitar` não tem peça. As outras três embaralham: o banco de
    `completar` não é uma linha, e deixá-lo na ordem do arquivo poria a
    peça certa sempre onde quem escreveu a pôs.
    """
    if forma in ("tocar", "digitar") or n <= 0:
        return tuple(range(max(n, 0)))
    digest = hashlib.sha256(
        ("%s|pecas|%s|%d" % (semente, degrau, versao)).encode()).digest()
    return tuple(i for _, i in sorted((digest[i % len(digest)], i)
                                      for i in range(n)))


# --------------------------------------------------------------------------
# A correção
# --------------------------------------------------------------------------

def _errada(v: Versao, retorno: str, crenca: str = "") -> Correcao:
    return Correcao(False, retorno=retorno, mostra_certa=v.certa_texto,
                    crenca=crenca)


def corrige(v: Versao, forma: str, pecas: tuple[int, ...] = (),
            texto: str = "") -> Correcao:
    """A resposta, contra o que o conteúdo previu.

    `pecas` vem em índices do ARQUIVO — quem desfaz a ordem da tela é o
    motor. O primeiro erro previsto que casar vence; nenhum casando, vale
    o retorno geral da versão.
    """
    if forma not in FORMAS:
        raise RespostaInvalida("forma desconhecida: %r" % forma)

    if forma == "digitar":
        dito = (texto or "").strip()
        if dito and dito in {a.strip() for a in v.aceitas}:
            return Correcao(True)
        for x in v.erros:
            if x.texto.strip() and x.texto.strip() == dito:
                return _errada(v, x.retorno, x.crenca)
        return _errada(v, v.retorno_geral)

    seq = tuple(pecas)
    if not seq:
        raise RespostaInvalida("resposta sem peça nenhuma")
    if any(isinstance(i, bool) or not isinstance(i, int) for i in seq):
        raise RespostaInvalida("peça que não é índice: %r" % (seq,))
    if _fora(seq, len(v.pecas)):
        raise RespostaInvalida("peça fora da faixa: %r" % (seq,))
    if len(set(seq)) != len(seq):
        raise RespostaInvalida("peça repetida: %r" % (seq,))
    if forma in UMA_PECA and len(seq) != 1:
        raise RespostaInvalida("em `%s` a resposta é uma peça só" % forma)

    if seq in v.certa:
        return Correcao(True)
    for x in v.erros:
        if x.exata and x.exata == seq:
            return _errada(v, x.retorno, x.crenca)
        if x.sem and not set(x.sem) & set(seq):
            return _errada(v, x.retorno, x.crenca)
    return _errada(v, v.retorno_geral)
