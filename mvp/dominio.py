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

from mvp import conceitos

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
    # A AMPLIAÇÃO EXPLICATIVA do cartão de ensino, opcional.
    #
    # Não vai em `simples` de propósito: aquela frase é a canônica do nó
    # e aparece em SETE telas, inclusive como a alternativa CERTA da
    # camada 2 (`motor.razoes_de`). Esticá-la transformaria uma opção de
    # resposta num parágrafo. Este campo é lido só pela tela de ensino.
    interpretacao: str = ""
    # A PROVA DA PREMISSA, conferida pelo compilador. Lista, e vazia
    # para os 73 nós que ainda não têm. Ver `Demonstracao`.
    evidencia: tuple["Demonstracao", ...] = ()

    @property
    def observavel(self) -> bool:
        return self.tipo == "observavel"


@dataclass(frozen=True)
class Demonstracao:
    """Um programa em C que demonstra a premissa, e o que dele se espera.

    A CRENÇA tem procedência — grade, obra, página, item — porque é
    afirmação sobre o que estudantes pensam, e quem a sustenta é o
    estudo empírico. A PREMISSA é afirmação sobre C, e quem a sustenta é
    o compilador. Procurar premissa na literatura de concepções errôneas
    seria a mesma confusão de categoria que procurar concepção errônea
    no padrão da linguagem.

    TRÊS FORMAS, e o oráculo já provava as duas primeiras antes disto
    existir:

        espera        o programa compila, roda, e a saída tem de ser esta
        nao_compila   a demonstração é o compilador RECUSAR
        avisa         a demonstração é o compilador DIAGNOSTICAR sem
                      recusar, e o programa NÃO É EXECUTADO

    `ambiente` é obrigatório nas duas últimas, e não é zelo: recusa e
    diagnóstico são fatos sobre um compilador, não sobre a linguagem.
    `int n = p;` é `error:` no gcc 16 e AVISO no gcc 13 — o que o padrão
    exige de todo compilador conforme é o diagnóstico, não a recusa de
    traduzir.

    A TERCEIRA NASCEU DE NOVE NÓS, em 12/11/2026, e o desenho dela é
    ditado pelas premissas que ela serve: kc_00:B3, kc_03:B3/I2/I3,
    kc_05:I3, kc_08:B3, kc_09:B4/I4 e kc_12:I1 falam de valor
    indeterminado e de comportamento indefinido. Rodar o programa
    exibiria o próprio UB como prova — o contrário de ensinar —, e o
    compilador não recusa, porque o padrão não exige recusa. Por isso
    `avisa` não convive com `espera`: não executar é a premissa, e não
    economia.

    E NÃO HÁ CAMPO DIZENDO SE PODE SER EXIBIDA. Quem decide isso é
    `conceitos.exibivel`, varrendo os construtos do código: um campo
    escrito por quem escreveu o programa seria julgado na mesma passada
    de quem o escreveu.
    """
    afirma: str                    # que metade da premissa esta prova
    programa: str
    espera: str = ""
    nao_compila: bool = False
    ambiente: str = ""
    avisa: str = ""                # trecho que o diagnóstico tem de trazer


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
    # De que MOLDE este item saiu, e com que parâmetros. Vazios nos itens
    # escritos à mão, que são todos os de hoje. É o que torna mensurável
    # a diferença entre generalizar e decorar: duas instâncias do mesmo
    # molde, com parâmetros distintos, são a mesma ideia com a roupa
    # trocada.
    do_molde: str = ""
    parametros: Mapping[str, object] = field(default_factory=dict)

    @property
    def indice_correto_no_arquivo(self) -> int:
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
    # A FUNÇÃO PEDAGÓGICA: explicitar, confrontar ou reconstruir.
    # Declarar obriga quem escreve a responder "o que esta pergunta faz?"
    # antes de escrevê-la, e um degrau que não faz nenhuma das três
    # provavelmente é dispensável.
    funcao: str = ""
    # OS CONCEITOS QUE O DEGRAU EXIGE. Tupla vazia é declaração válida —
    # quer dizer "nada além do que o tópico ensina". O que não vale é o
    # campo não existir, porque aí ninguém decidiu.
    requer: tuple = ()


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
    # Se os requisitos de TODO degrau estão disponíveis. Cadeia bloqueada
    # existe no domínio e não é entregue ao motor: ver `Dominio.descida`.
    liberada: bool = False


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

    # OS TRES CAMPOS DE ENSINO QUE FALTAVAM. A unidade do kc_02 oferecia
    # 811 palavras para seis premissas sobre ponteiros, e o dono, depois
    # de usar o sistema, disse que nao conseguia aprender.
    #
    #   narracoes        o exemplo explicado LINHA A LINHA
    #   casos_resolvidos um caso trabalhado ANTES de pedir qualquer coisa
    #   outras_rotas     o que o "Ainda nao entendi" mostra na segunda vez
    #
    # SAO LISTAS DE BLOCOS, e nao texto corrido, porque `_paragrafos`
    # preserva linha em branco e COLA o resto -- rodei a primeira versao
    # do material por ela e as linhas de codigo sairam grudadas numa so.
    narracoes: Mapping[str, tuple] = field(default_factory=dict)
    casos_resolvidos: Mapping[str, tuple] = field(default_factory=dict)
    outras_rotas: Mapping[str, tuple] = field(default_factory=dict)

    def narracao(self, no: str) -> list:
        """O exemplo do cartao, linha a linha. Vazio quando nao ha."""
        return list(self.narracoes.get(no) or ())

    def caso_resolvido(self, no: str) -> list:
        return list(self.casos_resolvidos.get(no) or ())

    def outra_rota(self, no: str) -> list:
        """O material da SEGUNDA vez. Vazio cai no resgate, no motor."""
        return list(self.outras_rotas.get(no) or ())

    # O TESTE DE MESA: o valor de cada variavel depois de cada linha.
    # GERADO por `scripts/mesa.py`, que instrumenta o exemplo do cartao,
    # compila e executa -- nao e escrito a mao. `test_mesa.py` regenera e
    # compara, para a tabela nao envelhecer quando o exemplo mudar.
    #
    # E e ele que tira o `(void *)` da tela: o cast fica no programa
    # instrumentado, e o aluno ve o valor.
    testes_de_mesa: Mapping[str, Mapping] = field(default_factory=dict)

    def teste_de_mesa(self, no: str) -> dict:
        t = self.testes_de_mesa.get(no)
        if not t:
            return {}
        return {"colunas": list(t.get("colunas") or ()),
                "linhas": [{"codigo": l.get("codigo", ""),
                            "valores": list(l.get("valores") or ())}
                           for l in (t.get("linhas") or ())]}

    def atividades_do_no(self, no: str, uso: str | None = None) -> tuple[Atividade, ...]:
        """As atividades do nó, teórica antes de código."""
        itens = [a for a in self.atividades
                 if a.no == no and (uso is None or a.uso == uso)]
        # Degrau primeiro: a escada manda mais que o par teórica/código.
        return tuple(sorted(itens, key=lambda a: (a.nivel, TIPOS.index(a.tipo))))

    def exemplo(self, no: str) -> str:
        """O código que acompanha a premissa na tela de ensino."""
        return self.exemplos.get(no, "")

    def interpretacao(self, no: str) -> str:
        """A ampliação explicativa daquele cartão, se houver.

        Opcional: nó sem ampliação devolve vazio, e a tela não desenha a
        seção. Doze dos treze tópicos não têm nenhuma.
        """
        n = self.nos.get(no)
        return n.interpretacao if n else ""

    def conceitos_de(self, no: str) -> tuple[str, ...]:
        """Os conceitos que o cartão deste nó APRESENTA, pelo inventário.

        Vazio quando o inventário não declarou nenhum — doze dos treze
        tópicos, hoje, porque a auditoria cobriu kc_00, kc_01 e kc_02. O
        motor pergunta aqui, e não ao `conceitos` direto, pelo mesmo
        motivo que `descida()` existe: o estado de autorização é do
        domínio, e o motor fica sem saber que o inventário existe.
        """
        return conceitos.do_cartao(self.id, no)

    def assinatura(self, no: str) -> str:
        """A versão do MATERIAL daquele cartão: 12 hex do sha256.

        A mesma convenção do `revisado_sha` que os candidatos já usam.

        PARA QUE SERVE. O histórico individual grava que a pessoa teve
        oportunidade de aprender um conceito naquele cartão. Se o cartão
        mudar amanhã, é preciso saber o que ela viu ontem — e este
        projeto reescreveu dois cartões inteiros numa única noite. Sem
        assinatura, o histórico mente em silêncio quando o material
        evolui.

        POR CARTÃO, E NÃO POR ARQUIVO. O cartão do B2 mora em dois
        arquivos — a ampliação no `graph_`, a narração e o teste de mesa
        no `activities_` —, e um sha do arquivo mudaria quando um item de
        outro nó mudasse. Isto cobre o que a TELA mostra, e só isso.

        E NÃO DEPENDE DO MOMENTO. `reexplicacao` muda conforme quantas
        vezes a pessoa pediu de novo; a assinatura cobre TODAS as rotas
        do cartão, senão o mesmo cartão teria três assinaturas na mesma
        sessão.

        `mvp/test_conceitual.py` exige que mexer em qualquer campo de
        conteúdo que as duas telas de ensino mandam mude a assinatura:
        campo novo no cartão sem entrar aqui é histórico mentindo.
        """
        import hashlib
        import json

        n = self.nos.get(no)
        # O ID DO NÓ NÃO ENTRA, e a primeira versão o punha aqui. A
        # sabotagem mostrou que ele era inútil — dois cartões já diferem
        # pelo conteúdo — e pior que inútil: com o id dentro, dois
        # cartões de material IDÊNTICO sairiam com assinaturas
        # diferentes, e a duplicação ficaria escondida. A assinatura é do
        # MATERIAL; material igual é assinatura igual. Conferido nos
        # treze tópicos: não há dois cartões com o mesmo conteúdo.
        corpo = {
            "texto": n.texto if n else "",
            "simples": n.simples if n else "",
            "interpretacao": n.interpretacao if n else "",
            "exemplo": self.exemplo(no),
            "resgate": self.resgate(no),
            "narracao": self.narracao(no),
            "caso_resolvido": self.caso_resolvido(no),
            "outra_rota": self.outra_rota(no),
            "teste_de_mesa": self.teste_de_mesa(no),
        }
        cru = json.dumps(corpo, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(cru.encode("utf-8")).hexdigest()[:12]

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

        DUAS AUTORIZAÇÕES, e as duas são exigidas aqui:

            liberada   todo conceito que a cadeia exige está ensinado
            aprovada   aquela cadeia passou na revisão pedagógica

        São perguntas diferentes. A primeira é curricular e vale para o
        conceito; a segunda é sobre ESTA sequência. Uma simulação mostrou
        por que não podem ser a mesma: liberar `comparacao_de_ponteiros`
        abriria duas cadeias de uma vez, e uma delas reprova em três das
        cinco perguntas da revisão.

        Faltando qualquer uma, o motor cai na refutação afirmativa de um
        tópico sem cadeia escrita. O portão tem de estar no caminho, e
        não só no relatório.
        """
        from mvp import aprovacao

        d = self.descidas.get(crenca or "")
        if d is None or not d.liberada:
            return None
        return d if aprovacao.aprovada(d.crenca) else None

    @property
    def ordem(self) -> tuple[str, ...]:
        """Nós na ordem em que a unidade os percorre: base antes da conclusão."""
        base = [n for n in self.nos if self.nos[n].observavel]
        inferencia = [n for n in self.nos if not self.nos[n].observavel]
        return tuple(base + inferencia)


BLOCOS_DE_ENSINO = ("prosa", "codigo", "saida")


def _blocos(cru, chave):
    """Le um campo de blocos: {no: [{prosa|codigo|saida: texto}]}.

    A prosa passa por `_texto` (um espaco entre palavras); o codigo e a
    saida NAO, porque neles a quebra de linha e o conteudo. Era isso que
    `_paragrafos` destruia quando o material vinha como texto corrido.
    """
    fora = {}
    for no, lista in ((cru or {}).get(chave) or {}).items():
        blocos = []
        for b in lista or ():
            if not isinstance(b, dict):
                continue
            for k, v in b.items():
                if k not in BLOCOS_DE_ENSINO:
                    continue
                blocos.append({k: _texto(v) if k == "prosa"
                               else (v or "").strip(chr(10))})
        fora[no] = tuple(blocos)
    return fora


def _mesas(cru):
    """{no: {colunas, linhas}} -- o teste de mesa gerado.

    So estrutura: os valores sao strings que vieram da execucao, e
    normalizar texto aqui estragaria um endereco.
    """
    fora = {}
    for no, t in ((cru or {}).get("testes_de_mesa") or {}).items():
        if not isinstance(t, dict):
            continue
        fora[no] = {
            "colunas": tuple(str(c) for c in (t.get("colunas") or ())),
            "linhas": tuple({"codigo": str(l.get("codigo", "")).strip(),
                             "valores": tuple(str(v) for v in
                                              (l.get("valores") or ()))}
                            for l in (t.get("linhas") or ())
                            if isinstance(l, dict)),
        }
    return fora


def _narracoes(cru):
    """{no: [{linha, diz}]} -- o exemplo explicado linha a linha."""
    fora = {}
    for no, lista in ((cru or {}).get("narracoes") or {}).items():
        fora[no] = tuple({"linha": (x.get("linha") or "").strip(),
                          "diz": _texto(x.get("diz"))}
                         for x in (lista or ()) if isinstance(x, dict))
    return fora


def _texto(valor) -> str:
    return " ".join(str(valor or "").split())


def _paragrafos(valor) -> str:
    """Como `_texto`, mas a linha em branco SOBREVIVE.

    A ampliacao explicativa de um cartao tem partes — ler, escrever, a
    distincao entre as expressoes — e `_texto` colapsava tudo num
    paragrafo so. Quatro ideias espremidas numa parede de texto e pior
    que tres, e foi o que a tela mostrou antes deste conserto.
    """
    branco = "\n\n"
    partes = [" ".join(b.split()) for b in str(valor or "").split(branco)]
    return branco.join(x for x in partes if x)


def _demonstracoes(nid, bruto, problemas) -> tuple[Demonstracao, ...]:
    """A `evidencia` do nó, recusada na carga se estiver malformada.

    RECUSAR NA CARGA, e não no teste: a prova de uma premissa vai para a
    tela de quem está sendo refutado, e uma prova que promete saída e
    não compila — ou que não compila e promete saída — mostraria à
    pessoa uma demonstração que não demonstra. Domínio que carrega
    quebrado é pior que domínio que não carrega.

    O PROGRAMA NÃO PASSA POR `_texto`. Ele é código, e `_texto` colapsa
    espaço: a indentação morreria, e a tela mostraria C sem recuo.
    """
    if bruto is None:
        return ()
    if not isinstance(bruto, list):
        problemas.append("nó %s: `evidencia` não é lista" % nid)
        return ()
    fora = []
    for i, dem in enumerate(bruto):
        if not isinstance(dem, dict):
            problemas.append("nó %s: evidência %d não é mapa" % (nid, i))
            continue
        programa = str(dem.get("programa") or "")
        nao_compila = bool(dem.get("nao_compila"))
        espera = str(dem.get("espera") or "")
        avisa = " ".join(str(dem.get("avisa") or "").split())
        ambiente = _paragrafos(dem.get("ambiente"))
        onde = "nó %s, evidência %d" % (nid, i)
        if not programa.strip():
            problemas.append("%s: sem programa" % onde)
            continue
        if not str(dem.get("afirma") or "").strip():
            problemas.append("%s: sem `afirma`" % onde)
        if avisa:
            # A TERCEIRA FORMA. O programa COMPILA e não é executado:
            # executá-lo seria exibir o comportamento indefinido que a
            # premissa descreve. Por isso ela exclui as outras duas.
            if espera.strip():
                problemas.append(
                    "%s: prova por aviso não pode prometer saída — o "
                    "programa dela existe porque executá-lo é "
                    "comportamento indefinido" % onde)
            if nao_compila:
                problemas.append(
                    "%s: `avisa` e `nao_compila` são formas diferentes — a "
                    "primeira é o compilador que DIAGNOSTICA e traduz, a "
                    "segunda é a recusa" % onde)
            if not ambiente.strip():
                problemas.append(
                    "%s: prova por aviso sem `ambiente` — diagnóstico é "
                    "fato sobre um compilador, não sobre a linguagem"
                    % onde)
        elif nao_compila:
            if espera.strip():
                problemas.append(
                    "%s: prova por recusa do compilador não pode prometer "
                    "saída" % onde)
            if not ambiente.strip():
                problemas.append(
                    "%s: prova por recusa sem `ambiente` — recusa é fato "
                    "sobre um compilador, não sobre a linguagem" % onde)
        elif not espera.strip():
            problemas.append(
                "%s: programa que roda e não diz o que tem de sair não "
                "demonstra nada" % onde)
        fora.append(Demonstracao(
            afirma=_paragrafos(dem.get("afirma")), programa=programa,
            espera=espera.rstrip("\n"), nao_compila=nao_compila,
            ambiente=ambiente, avisa=avisa))
    return tuple(fora)


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
    for chave in ("resgates", "exemplos", "narracoes",
                  "casos_resolvidos", "outras_rotas",
                  "testes_de_mesa"):
        if cru_atv.get(chave):
            cru_atv[chave] = {k: v for k, v in cru_atv[chave].items()
                              if k in vivos}

    if cru_topico.get("conclusion_node") not in vivos:
        cru_topico["conclusion_node"] = fica[-1]

    # A descida de uma crença que saiu no corte sai junto — e também a
    # que sobrevive apontando `colide_com` para um nó que saiu.
    #
    # O segundo caso faltava, e derrubava a CARGA INTEIRA com "colide_com
    # não é nó deste tópico". Ficou invisível enquanto só existia a cadeia
    # do kc_07, que nega I3 e colide com B1: todo corte que a preserva
    # preserva o B1 junto, por ele ser o primeiro. A primeira cadeia que
    # nega o PRIMEIRO nó de um tópico expõe a lacuna — e é o caso de
    # `memory_is_by_name` no kc_02.
    #
    # Descartar é o conserto, e não cortar menos: numa sessão sem a
    # premissa da colisão o último degrau não teria onde bater, e a
    # descida degrada para a refutação afirmativa — que é o que ela já faz
    # em todo tópico sem cadeia escrita.
    if cru_desc and cru_desc.get("descidas"):
        cru_desc["descidas"] = {
            k: v for k, v in cru_desc["descidas"].items()
            if k in crencas_vivas
            and str((v or {}).get("colide_com") or "").split(":")[-1] in vivos}


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
            interpretacao=_paragrafos(bruto.get("interpretation")),
            evidencia=_demonstracoes(nid, bruto.get("evidencia"), problemas),
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
            do_molde=str(bruto.get("do_molde") or ""),
            parametros=dict(bruto.get("parametros") or {}),
        ))

        # Meia procedência é pior que nenhuma, porque PARECE procedência:
        # sem os parâmetros não dá para dizer qual variação a pessoa
        # respondeu, e sem o molde os parâmetros não significam nada.
        if bool(bruto.get("do_molde")) != bool(bruto.get("parametros")):
            problemas.append(
                "atividade %s: meia procedência — `do_molde` e `parametros` "
                "andam juntos ou não andam" % aid)

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
            funcao = str(p.get("funcao") or "")
            if funcao not in conceitos.FUNCOES:
                problemas.append(
                    "%s, degrau %d: funcao %r (use %s) — um degrau que não "
                    "explicita, não confronta e não reconstrói provavelmente "
                    "é dispensável"
                    % (onde, i, funcao, ", ".join(conceitos.FUNCOES)))
            # `requer` AUSENTE é erro; `requer: []` é declaração válida.
            # A diferença importa: lista vazia diz "nada além do que o
            # tópico ensina", e campo ausente diz que ninguém decidiu.
            if "requer" not in p:
                problemas.append(
                    "%s, degrau %d: sem `requer` — declare os conceitos "
                    "exigidos, ou [] para nenhum" % (onde, i))
            requer = tuple(str(x) for x in (p.get("requer") or []))
            passos.append(Passo(
                pergunta=_texto(p.get("pergunta")),
                decorre=_texto(p.get("decorre")),
                verdade=_texto(p.get("verdade")),
                porque=_texto(p.get("porque")),
                funcao=funcao, requer=requer))

        if passos:
            # A cadeia não pode terminar na contradição: confrontar sem
            # reconstruir deixa a pessoa sabendo que a ideia dela não
            # fecha e sem nenhuma no lugar — que é o estado em que uma
            # crença volta, não o estado em que ela é trocada.
            if passos[-1].funcao != conceitos.RECONSTRUIR:
                problemas.append(
                    "%s: o último degrau é %r, e tem de ser %r"
                    % (onde, passos[-1].funcao, conceitos.RECONSTRUIR))
            if not any(x.funcao == conceitos.CONFRONTAR for x in passos):
                problemas.append(
                    "%s: nenhum degrau confronta — só explicitar e "
                    "reconstruir é uma aula, não uma refutação" % onde)

        ev = bruto.get("evidencia") or {}
        if ev.get("tipo") not in TIPOS_EVIDENCIA:
            problemas.append("%s: evidência de tipo %r (use %s)"
                             % (onde, ev.get("tipo"), ", ".join(TIPOS_EVIDENCIA)))
        if ev.get("origem") not in ORIGENS_EVIDENCIA:
            problemas.append("%s: origem %r (use %s)"
                             % (onde, ev.get("origem"), ", ".join(ORIGENS_EVIDENCIA)))
        if not (ev.get("fonte") or "").strip():
            problemas.append("%s: evidência sem programa" % onde)
        # A AFIRMAÇÃO é o texto da tela de evidência, nos três casos de
        # origem. Ela era cobrada só no pendente, e uma evidência gravada
        # sem afirmação passava na carga e chegava à tela com a ideia em
        # branco — apareceu no dia em que a primeira evidência deixou de
        # ser pendente.
        if not _texto(ev.get("afirmacao")):
            problemas.append(
                "%s: evidência sem afirmação — é ela que a tela escreve, "
                "com saída gravada ou sem" % onde)

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
        elif not _texto(ev.get("garantia")):
            # A garantia é o que sustenta a tela quando não houve terminal:
            # o que a norma obriga, no lugar do que a máquina mostrou.
            problemas.append(
                "%s: evidência pendente sem garantia — sem saída gravada, "
                "é só isto que a tela tem de verdadeiro" % onde)
        parcial = Descida(
            crenca=cid, colide_com=colide, passos=tuple(passos),
            evidencia=Evidencia(tipo="", fonte="", comando="", afirmacao="",
                                garantia=""))
        descidas[cid] = Descida(
            crenca=cid, colide_com=colide, passos=tuple(passos),
            liberada=conceitos.liberada(parcial),
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
        narracoes=_narracoes(cru_atv),
        casos_resolvidos=_blocos(cru_atv, "casos_resolvidos"),
        outras_rotas=_blocos(cru_atv, "outras_rotas"),
        testes_de_mesa=_mesas(cru_atv),
        descidas=descidas,
    )
