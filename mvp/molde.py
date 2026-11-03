"""O molde: uma pergunta com buracos, e um programa que a confere.

    moldes = le(Path("mvp/dominio/moldes_kc07.yaml"), dominio)

Um item do banco é texto fixo: `int a[5]` é `int a[5]` sempre, com o
mesmo nome, o mesmo tamanho e as mesmas três alternativas. Um molde é a
REGRA que produz esse item — e produz as outras cento e quarenta e nove.

O que isso compra não é só variedade. É um eixo que o instrumento não
tinha: perguntar a MESMA ideia com a roupa trocada. Duas superfícies
hoje são dois formatos — duas perguntas distintas, que alguém pode ter
decorado uma a uma. Duas instâncias do mesmo molde são a mesma pergunta
com outro nome, outro tamanho, outro tipo, e quem sustenta as duas
generalizou.

O PREÇO: um molde errado erra em todas as variações de uma vez. É por
isso que a validação daqui é tão desconfiada quanto a do domínio, e por
isso que o `oraculo` é obrigatório — o que a máquina não puder conferir
não entra por molde, e continua sendo escrito à mão.

Este módulo é PURO: lê, valida, e nada mais. Quem compila é o
`scripts/oraculo.py`, quem orquestra é o `scripts/gerar.py`, e quem
nunca ouve falar de molde é o motor — a expansão é offline, e o que
chega à sessão é um item de YAML como todos os outros.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import yaml

from mvp.dominio import FORMATOS, NIVEIS, TIPOS, USOS, Dominio
# O mesmo normalizador do carregador do domínio: um espaço entre
# palavras, sem quebra de linha. Texto de item e texto de molde
# passam pela mesma régua.
from mvp.dominio import _texto

# Um buraco é um identificador entre chaves: `{tipo}`, `{n}`, `{extenso}`.
#
# A varredura ignora as chaves do C de propósito. O oráculo é um programa
# em C, e C é cheio de chaves: se a substituição fosse `str.format`, cada
# `{` do programa teria de ser dobrado, e quem escreve o molde escreveria
# C errado para o Python ficar feliz.
BURACO = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

# Derivados: não são parâmetros, saem de um. `extenso` é o número por
# extenso, e só existe quando há `n`.
EXTENSO = {1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco",
           6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez"}

# Os campos que podem ter buraco, e que portanto são varridos.
COM_BURACO = ("enunciado", "gabarito", "oraculo", "espera")


class MoldeInvalido(Exception):
    """Um ou mais defeitos no arquivo de moldes, todos de uma vez.

    Devolver o primeiro faria quem escreve molde consertar um por
    execução. É a mesma escolha de `DominioInvalido`.
    """

    def __init__(self, problemas):
        self.problemas = list(problemas)
        super().__init__("; ".join(self.problemas))


@dataclass(frozen=True)
class Redacao:
    """Um jeito de perguntar a afirmação do molde.

    Os distratores são só os TEXTOS: a crença de cada um vem de
    `Molde.crencas`, pela posição. É isso que garante que todo formato
    carrega as mesmas ideias erradas — se cada redação escolhesse as
    suas, dois formatos do mesmo molde mediriam coisas diferentes, e aí
    não são duas superfícies da mesma afirmação, são duas perguntas.
    """
    formato: str
    tipo: str
    enunciado: str
    gabarito: str
    distratores: tuple[str, ...]
    codigo: str = ""
    # Vazios quando a redação usa o oráculo da família.
    oraculo: str = ""
    espera: str = ""
    # `achar_o_erro` prova o contrário: que o programa NÃO compila.
    nao_compila: bool = False


@dataclass(frozen=True)
class Molde:
    id: str
    no: str
    tipo: str                               # teorica | codigo
    formato: str
    nivel: int
    uso: str
    parametros: Mapping[str, tuple]
    enunciado: str
    gabarito: str
    distratores: tuple[tuple[str, str], ...]   # (texto, id da crença)
    oraculo: str
    espera: str
    revisado_por: str = ""
    # A impressão digital do conteúdo que FOI revisado. Sem ela, o nome
    # do revisor sobrevive a qualquer edição do molde — e as variações
    # novas saem estampadas com o nome de quem nunca as leu.
    revisado_sha: str = ""
    digest: str = ""
    # As crenças são da AFIRMAÇÃO, não da redação, e as redações são as
    # formas de perguntá-la. Molde sem `formatos:` é família de UM: as
    # crenças saem dos distratores dele, na ordem em que estão.
    crencas: tuple[str, ...] = ()
    redacoes: tuple[Redacao, ...] = ()
    # O prefixo que o `node` do item usa: "kc07", do nome do arquivo.
    # Sai do mesmo lugar de onde o carregador do domínio tira o dele.
    topico: str = ""

    @property
    def revisado(self) -> bool:
        """Revisado é nome MAIS assinatura do conteúdo lido.

        Só o nome não basta: a spec documenta reexpandir depois de
        editar, e prescreve editar — estreitar o domínio de um parâmetro
        — como o conserto de um molde reprovado. Sem amarrar o nome ao
        conteúdo, o conserto apaga a revisão sem avisar ninguém.
        """
        return bool(self.revisado_por.strip()) and self.revisado_sha == self.digest


def assinatura(bruto: Mapping) -> str:
    """A impressão digital do molde, sem os campos da própria revisão.

    Doze hexadecimais bastam: isto não é segurança, é detecção de
    mudança — ninguém está tentando forjar um molde, mas qualquer um
    pode editar um e esquecer que já tinha sido lido.
    """
    limpo = {k: v for k, v in dict(bruto).items()
             if k not in ("revisado_por", "revisado_sha")}
    texto = yaml.safe_dump(limpo, allow_unicode=True, sort_keys=True)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def preenche(texto: str, valores: Mapping[str, object]) -> str:
    """Troca os buracos pelos valores. NÃO é `str.format` — ver `BURACO`."""
    return BURACO.sub(
        lambda m: str(valores[m.group(1)]) if m.group(1) in valores
        else m.group(0), texto)


def _buracos(molde_cru: dict) -> set[str]:
    achados: set[str] = set()
    for campo in COM_BURACO:
        achados |= set(BURACO.findall(str(molde_cru.get(campo) or "")))
    for d in molde_cru.get("distratores") or ():
        achados |= set(BURACO.findall(str((d or {}).get("texto") or "")))
    return achados


def le(caminho: Path, d: Dominio) -> dict[str, Molde]:
    """Os moldes daquele arquivo, validados contra aquele tópico.

    Arquivo que não existe devolve vazio: doze dos treze tópicos não têm
    molde nenhum, e isso não é defeito.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return {}

    cru = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    sufixo = caminho.stem.split("_", 1)[-1]        # moldes_kc07 -> kc07
    problemas: list[str] = []
    moldes: dict[str, Molde] = {}

    for mid, bruto in cru.items():
        bruto = bruto or {}
        onde = "molde %s" % mid
        # Com `formatos:`, a redação é que tem formato, tipo, enunciado,
        # gabarito e distratores — os campos de topo deixam de existir, e
        # as regras que os cobram valem só para a família de um.
        em_familia = bruto.get("formatos") is not None

        # `node`, e não `no`: em YAML 1.1 a chave `no` é o booleano
        # FALSO — o problema da Noruega —, e o campo simplesmente some.
        # Os arquivos do domínio sempre usaram `node`; o molde nasceu com
        # `no` e isso só apareceu na primeira expansão de verdade.
        if False in bruto:
            problemas.append(
                "%s: o campo `no` virou booleano ao ser lido (em YAML, `no` "
                "é falso). Escreva `node:`, como nas atividades" % onde)
        no = str(bruto.get("node") or "").split(":")[-1]
        if no not in d.nos:
            problemas.append("%s: nó %r não é deste tópico" % (onde, no))
        if not em_familia and bruto.get("tipo") not in TIPOS:
            problemas.append("%s: tipo %r (use %s)"
                             % (onde, bruto.get("tipo"), ", ".join(TIPOS)))
        if not em_familia and bruto.get("formato") not in FORMATOS:
            problemas.append("%s: formato %r (use %s)"
                             % (onde, bruto.get("formato"), ", ".join(FORMATOS)))
        if bruto.get("nivel") not in NIVEIS:
            problemas.append("%s: nível %r (use 1, 2 ou 3)"
                             % (onde, bruto.get("nivel")))
        if bruto.get("uso") not in USOS:
            problemas.append("%s: uso %r (use %s)"
                             % (onde, bruto.get("uso"), ", ".join(USOS)))

        parametros = {k: tuple(v or ())
                      for k, v in (bruto.get("parametros") or {}).items()}
        if not parametros:
            problemas.append("%s: sem parâmetro nenhum — isto é um item, "
                             "não um molde" % onde)
        for nome, valores in parametros.items():
            if not valores:
                problemas.append(
                    "%s: o parâmetro %r está sem valor, e um parâmetro vazio "
                    "não gera variação nenhuma" % (onde, nome))

        # O que a máquina não pode conferir não entra por molde.
        tem_oraculo_de_topo = bool(str(bruto.get("oraculo") or "").strip())
        todas_tem_o_seu = em_familia and all(
            str((r or {}).get("oraculo") or "").strip()
            for r in (bruto.get("formatos") or {}).values())
        if not tem_oraculo_de_topo and not todas_tem_o_seu:
            problemas.append(
                "%s: sem oráculo — molde sem programa que o confira é texto "
                "de modelo sem conferência nenhuma" % onde)
        # O `espera` acompanha o oráculo, e `nao_compila` dispensa os dois:
        # não há saída que esperar de um programa que não vira executável.
        if not em_familia and not str(bruto.get("espera") or "").strip():
            problemas.append(
                "%s: sem `espera` — programa que roda e não diz o que devia "
                "sair não confere nada" % onde)

        crus = bruto.get("distratores") or []
        if not em_familia and len(crus) < 2:
            problemas.append(
                "%s: %d distrator(es) — item de duas alternativas é cara ou "
                "coroa" % (onde, len(crus)))
        distratores = []
        for i, dist in enumerate(crus, 1):
            dist = dist or {}
            cid = dist.get("crenca")
            if cid not in d.crencas:
                problemas.append("%s, distrator %d: crença %r não existe "
                                 "neste tópico" % (onde, i, cid))
            if not str(dist.get("texto") or "").strip():
                problemas.append("%s, distrator %d: sem texto" % (onde, i))
            distratores.append((str(dist.get("texto") or "").strip(),
                                str(cid or "")))

        # O ORÁCULO TEM DE DEPENDER DOS PARÂMETROS. Sem isto, um
        # programa constante satisfaz a obrigatoriedade e não confere
        # nada: seis compilações do mesmo programa, seis "passou",
        # relatório verde — e com cara de conferido, que é o pior
        # resultado possível numa camada feita para separar conferido de
        # não conferido.
        juntos = str(bruto.get("oraculo") or "") + str(bruto.get("espera") or "")
        if juntos.strip() and not BURACO.search(juntos):
            problemas.append(
                "%s: o oráculo não usa parâmetro nenhum, então roda o mesmo "
                "programa em toda variação e não confere nada" % onde)

        # `prever_saida` promete, na spec, que o oráculo vira GABARITO: a
        # resposta certa é o que o programa imprime, e a máquina a
        # calcula. Enquanto isso não existir, `gabarito` e `espera` são
        # campos independentes — o oráculo prova que o programa imprime
        # `espera`, e ninguém prova que a alternativa certa diz o mesmo.
        # Formato aceito e meio implementado é pior que recusado.
        if not em_familia and bruto.get("formato") == "prever_saida":
            problemas.append(
                "%s: prever_saida ainda não vale como molde — neste formato "
                "o gabarito tem de SAIR do oráculo, e isso não está feito. "
                "Escreva o item à mão" % onde)

        # A trava da revisão: nome e assinatura andam juntos.
        digest = assinatura(bruto)
        tem_nome = bool(str(bruto.get("revisado_por") or "").strip())
        sha = str(bruto.get("revisado_sha") or "").strip()
        if tem_nome and not sha:
            problemas.append(
                "%s: tem `revisado_por` e não tem `revisado_sha` — nome sem "
                "assinatura é revisão de conteúdo nenhum. A assinatura deste "
                "molde é %s" % (onde, digest))
        elif tem_nome and sha != digest:
            problemas.append(
                "%s: o molde mudou depois da revisão (assinado %s, hoje %s). "
                "Leia a folha outra vez e assine de novo, ou apague o "
                "`revisado_por`" % (onde, sha, digest))

        # Todo buraco tem de ter de onde sair.
        for buraco in sorted(_buracos(bruto)):
            if buraco in parametros:
                continue
            if buraco == "extenso":
                if "n" not in parametros:
                    problemas.append(
                        "%s: usa {extenso}, que é derivado de `n`, e não há "
                        "parâmetro `n`" % onde)
                    continue
                # Fora da faixa que tem nome, o buraco fica LITERAL no
                # item, e quem o recebe lê "{extenso} caixas de int".
                # Nenhum dos quatro portões pega isso: o oráculo não usa
                # {extenso}, o contrato não repara, a variedade não
                # repara.
                sem_nome = [v for v in parametros["n"] if v not in EXTENSO]
                if sem_nome:
                    problemas.append(
                        "%s: usa {extenso}, e %s não tem nome por extenso "
                        "(há até %d)" % (onde, sem_nome, max(EXTENSO)))
                continue
            problemas.append(
                "%s: buraco {%s} não é parâmetro deste molde (há %s)"
                % (onde, buraco, ", ".join(sorted(parametros)) or "nenhum"))

        # ---------------------------------------------------- redações
        crus_formatos = bruto.get("formatos")
        if crus_formatos is None:
            # Família de um: o molde de ontem, lido igual.
            crencas_da_familia = tuple(cid for _, cid in distratores)
            redacoes = (Redacao(
                formato=str(bruto.get("formato") or ""),
                tipo=str(bruto.get("tipo") or ""),
                enunciado=_texto(bruto.get("enunciado")),
                gabarito=_texto(bruto.get("gabarito")),
                distratores=tuple(texto for texto, _ in distratores),
                codigo=(bruto.get("codigo") or "").strip("\n")),)
        else:
            crencas_da_familia = tuple(bruto.get("crencas") or ())
            if not crencas_da_familia:
                problemas.append(
                    "%s: família sem crença nenhuma — é a crença que faz o "
                    "erro ter diagnóstico" % onde)
            for cid in crencas_da_familia:
                if cid not in d.crencas:
                    problemas.append("%s: crença %r não existe neste tópico"
                                     % (onde, cid))
            # A regra do contrato, cobrada UMA vez por família em vez de
            # uma por redação: sem um distrator que aponte a crença do
            # próprio nó, o nó nunca recebe atribuição e termina a sessão
            # sem medida.
            if crencas_da_familia and not any(
                    cid in d.crencas and d.crencas[cid].nega == no
                    for cid in crencas_da_familia):
                problemas.append(
                    "%s: nenhuma crença da família nega o próprio nó (%s) — "
                    "sem isso o nó não recebe atribuição" % (onde, no))
            redacoes = []
            for nome_formato, cru_r in (crus_formatos or {}).items():
                cru_r = cru_r or {}
                aqui = "%s, formato %s" % (onde, nome_formato)
                if nome_formato not in FORMATOS:
                    problemas.append("%s: formato %r não está no catálogo"
                                     % (aqui, nome_formato))
                for campo in ("enunciado", "gabarito"):
                    if not _texto(cru_r.get(campo)):
                        problemas.append("%s: sem %s" % (aqui, campo))
                if cru_r.get("tipo") not in TIPOS:
                    problemas.append("%s: tipo %r (use %s)"
                                     % (aqui, cru_r.get("tipo"), ", ".join(TIPOS)))
                # Um distrator por crença, pela posição.
                quantos = len(cru_r.get("distratores") or ())
                if crencas_da_familia and quantos != len(crencas_da_familia):
                    problemas.append(
                        "%s: %d distrator(es) para %d crença(s) — a "
                        "correspondência é pela posição, e precisa de uma "
                        "para uma" % (aqui, quantos, len(crencas_da_familia)))
                # `do_oraculo` é marcador, e só faz sentido onde a
                # saída do programa É a resposta certa.
                pede_oraculo = _texto(cru_r.get("gabarito")) == "do_oraculo"
                if pede_oraculo and nome_formato != "prever_saida":
                    problemas.append(
                        "%s: `gabarito: do_oraculo` só vale em prever_saida — "
                        "noutro formato a saída do programa não é a resposta"
                        % aqui)
                if nome_formato == "prever_saida" and not pede_oraculo:
                    problemas.append(
                        "%s: prever_saida exige `gabarito: do_oraculo` — sem "
                        "isso o gabarito e o `espera` voltam a ser campos "
                        "independentes, e ninguém prova que dizem o mesmo"
                        % aqui)
                redacoes.append(Redacao(
                    formato=nome_formato,
                    tipo=str(cru_r.get("tipo") or ""),
                    enunciado=_texto(cru_r.get("enunciado")),
                    gabarito=_texto(cru_r.get("gabarito")),
                    distratores=tuple(_texto(x)
                                      for x in (cru_r.get("distratores") or ())),
                    codigo=(cru_r.get("codigo") or "").strip("\n"),
                    oraculo=str(cru_r.get("oraculo") or ""),
                    espera=_texto(cru_r.get("espera")),
                    nao_compila=bool(cru_r.get("nao_compila"))))
            redacoes = tuple(redacoes)

        moldes[mid] = Molde(
            id=mid, no=no, tipo=str(bruto.get("tipo") or ""),
            formato=str(bruto.get("formato") or ""),
            nivel=bruto.get("nivel") if bruto.get("nivel") in NIVEIS else 1,
            uso=str(bruto.get("uso") or ""),
            parametros=parametros,
            enunciado=str(bruto.get("enunciado") or "").strip(),
            gabarito=str(bruto.get("gabarito") or "").strip(),
            distratores=tuple(distratores),
            oraculo=str(bruto.get("oraculo") or ""),
            espera=str(bruto.get("espera") or "").strip(),
            revisado_por=str(bruto.get("revisado_por") or ""),
            revisado_sha=str(bruto.get("revisado_sha") or ""),
            digest=digest,
            crencas=crencas_da_familia,
            redacoes=redacoes,
            topico=sufixo)

    if problemas:
        raise MoldeInvalido(problemas)
    return moldes


def _hamming(a: Mapping[str, object], b: Mapping[str, object]) -> int:
    """Em quantos parâmetros as duas variações diferem."""
    return sum(1 for k in a if a[k] != b[k])


def _com_extenso(p: dict) -> dict:
    """O número por extenso, quando há `n`. Não é parâmetro: é derivado."""
    if "n" in p and p["n"] in EXTENSO:
        return dict(p, extenso=EXTENSO[p["n"]])
    return dict(p)


def expande(molde: Molde, quantas: int = 6) -> list[dict]:
    """As `quantas` variações mais distantes entre si, determinísticas.

    GULOSO, pela distância de Hamming: começa pela combinação de índices
    mais baixos e, a cada passo, acrescenta aquela cuja distância mínima
    às já escolhidas é a maior. Empate cai na ordem de escrita do YAML,
    porque `max` devolve o primeiro máximo.

    Por que distância e não as primeiras combinações: seis variações que
    diferem num parâmetro só são a mesma pergunta seis vezes, e o eixo
    que o molde existe para criar — perguntar a mesma ideia com a roupa
    trocada — não aparece.

    Por que determinístico e não sorteado: reexpandir um molde revisado
    tem de dar o mesmo banco. Senão o `revisado_por` passa a valer para
    itens que ninguém viu.

    Menos combinações do que o pedido devolve o que existe.
    """
    import itertools

    nomes = list(molde.parametros)
    restam = [dict(zip(nomes, valores)) for valores in
              itertools.product(*(molde.parametros[k] for k in nomes))]

    escolhidas: list[dict] = []
    while restam and len(escolhidas) < quantas:
        if escolhidas:
            alvo = max(restam, key=lambda c: min(_hamming(c, e)
                                                 for e in escolhidas))
        else:
            alvo = restam[0]
        escolhidas.append(alvo)
        restam.remove(alvo)
    return [_com_extenso(p) for p in escolhidas]


def serve_de_alternativa(saida: str) -> tuple[bool, str]:
    """A saída do programa pode virar a alternativa certa?

    Em `prever_saida` o oráculo deixa de conferir e vira gabarito. Mas
    nem toda saída é uma alternativa: vazia não diz nada, com quebra de
    linha não cabe num botão, e muito longa vira a pista de superfície
    que o contrato já proíbe.
    """
    texto = (saida or "").strip()
    if not texto:
        return False, "a saída é vazia, e não serve como alternativa"
    if "\n" in texto:
        return False, ("a saída tem mais de uma linha, e não serve como "
                       "alternativa")
    if len(texto) > 60:
        return False, "a saída é longa demais para uma alternativa"
    return True, texto


def item_de(molde: Molde, redacao: Redacao, parametros: dict,
            i: int) -> dict:
    """Uma variação de UMA redação, no formato de `activities_*.yaml`.

    O `revisado_por` do item é CÓPIA do molde: é assim que o
    `gerar.py --aprovar` de hoje continua valendo sem saber o que é
    molde — ele olha o campo de cada item, e o item herda o do molde.
    Uma revisão passa a valer pela família inteira.

    O `do_molde` é o da FAMÍLIA, e não o da redação: duas redações da
    mesma afirmação são duas superfícies dela, e é assim que a medida da
    generalização precisa enxergá-las.

    O gabarito fica em `a`, como em 547 dos 556 itens escritos à mão.
    Não é escolha deste módulo: é a convenção do banco, e divergir dela
    só nos itens de molde criaria uma diferença entre eles e os outros
    bem no meio da coleta.
    """
    valores = dict(parametros)
    letras = ["b", "c", "d", "e"]
    alternativas = {"a": preenche(redacao.gabarito, valores)}
    crencas = {}
    for letra, texto, cid in zip(letras, redacao.distratores, molde.crencas):
        alternativas[letra] = preenche(texto, valores)
        crencas[letra] = cid
    return {
        "id": "%s__%s_%02d" % (molde.id, redacao.formato, i),
        "node": "%s:%s" % (molde.topico, molde.no),
        "nivel": molde.nivel,
        "formato": redacao.formato,
        "tipo": redacao.tipo,
        "uso": molde.uso,
        "codigo": preenche(redacao.codigo, valores),
        "enunciado": preenche(redacao.enunciado, valores),
        "alternativas": alternativas,
        "gabarito": "a",
        "crencas": crencas,
        "do_molde": molde.id,
        # Sem o `extenso`: ele é derivado do `n`, e guardar derivado no
        # log é guardar a mesma coisa duas vezes.
        "parametros": {k: v for k, v in valores.items() if k != "extenso"},
        "gerado_por": "molde %s" % molde.id,
        "revisado_por": molde.revisado_por if molde.revisado else "",
    }


def _hamming(a: Mapping[str, object], b: Mapping[str, object]) -> int:
    """Em quantos parâmetros as duas variações diferem."""
    return sum(1 for k in a if a[k] != b[k])


def _com_extenso(p: dict) -> dict:
    """O número por extenso, quando há `n`. Não é parâmetro: é derivado."""
    if "n" in p and p["n"] in EXTENSO:
        return dict(p, extenso=EXTENSO[p["n"]])
    return dict(p)


def expande(molde: Molde, quantas: int = 6) -> list[dict]:
    """As `quantas` variações mais distantes entre si, determinísticas.

    GULOSO, pela distância de Hamming: começa pela combinação de índices
    mais baixos e, a cada passo, acrescenta aquela cuja distância mínima
    às já escolhidas é a maior. Empate cai na ordem de escrita do YAML,
    porque `max` devolve o primeiro máximo.

    Por que distância e não as primeiras combinações: seis variações que
    diferem num parâmetro só são a mesma pergunta seis vezes, e o eixo
    que o molde existe para criar — perguntar a mesma ideia com a roupa
    trocada — não aparece.

    Por que determinístico e não sorteado: reexpandir um molde revisado
    tem de dar o mesmo banco. Senão o `revisado_por` passa a valer para
    itens que ninguém viu.

    Menos combinações do que o pedido devolve o que existe.
    """
    import itertools

    nomes = list(molde.parametros)
    restam = [dict(zip(nomes, valores)) for valores in
              itertools.product(*(molde.parametros[k] for k in nomes))]

    escolhidas: list[dict] = []
    while restam and len(escolhidas) < quantas:
        if escolhidas:
            alvo = max(restam, key=lambda c: min(_hamming(c, e)
                                                 for e in escolhidas))
        else:
            alvo = restam[0]
        escolhidas.append(alvo)
        restam.remove(alvo)
    return [_com_extenso(p) for p in escolhidas]

