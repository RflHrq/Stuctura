"""O laço do MVP: identifica, confirma a suspeita, refuta, treina, confirma.

    transicao = avanca(dominio, estado, resposta)

Puro: não toca disco, não sorteia, não consulta relógio. Recebe o estado e
uma entrada, devolve o estado novo, a próxima tela e os eventos a gravar.

AS DUAS PEÇAS QUE ESTE MVP ACRESCENTA
-------------------------------------
**A razão é a prova.** Errar não basta para refutar, e errar duas vezes
também não era prova de nada: era proxy. Quem erra a resposta e acerta a
RAZÃO escorregou, e o sistema não contesta uma ideia que a pessoa acabou de
enunciar direito. Quem erra a resposta e explica por uma crença, com
confiança, nomeou a própria rota torta — e a refutação começa no nó que
**aquela crença** nega, que pode ser o vizinho.

**Um acerto isolado não confirma.** Nem no diagnóstico (CS-5: duas
superfícies diferentes, pela razão certa, com confiança) nem depois da
refutação, onde o nó entra em treino e só vira premissa correta depois de
`STREAK_ALVO` acertos seguidos, em formatos diferentes. Um acerto logo depois da refutação pode ser sorte,
decoreba do item, ou apenas responder o oposto do que acabou de ser
contestado.

  RF33  depois da refutação o nó entra em treino, nunca direto em confirmado
  RF34  cada tentativa muda de formato, e nunca repete o item anterior
  RF35  errar zera a sequência DAQUELE nó, sem mexer nos outros
  RF36  esgotar os itens do nó sem fechar a sequência encerra em aberto

O streak é mecanismo de PRODUTO: ele decide o que o mapa mostra ao aluno,
emite `training_streak_completed` e nunca escreve em `belief_retested`. O
reteste da pesquisa continua sendo outra medida, longe do treino.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from mvp.dominio import NIVEIS, Atividade, Dominio, Opcao

# Parâmetros do documento. Ponto de partida, não valores validados: ajustar
# no ensaio antes da coleta.
STREAK_ALVO = 2        # acertos seguidos, de formatos diferentes, para confirmar
TETO_TENTATIVAS = 4    # o dobro do streak: se não bastou, não é falta de repetição
# ERROS_PARA_CRENCA saiu na T4. Ele valia 2, e existia porque não havia como
# saber POR QUE a pessoa errou: o segundo erro era um proxy de "não foi
# escorregão". A camada 2 substituiu o proxy pela coisa — quem erra pelo
# motivo certo escorregou, e quem erra pelo motivo errado com confiança já
# disse qual é a crença.

# Quantas vezes a mesma premissa pode ser reapresentada quando o aluno diz
# que não entendeu. Depois disso o percurso segue: insistir uma quarta vez
# na mesma frase não ensina, e o treino ainda vem depois para pegar o que
# ficou. Quem não fechar lá termina o nó em aberto, que é honesto.
LIMITE_REEXPLICACAO = 2

# Quantos falsos positivos na MESMA crença até ela virar refutação. Um
# isolado pode ser acidente de alternativa; dois, na mesma ideia, é a ideia.
FALSOS_POSITIVOS_PARA_CRENCA = 2

# Estados de um nó.
DESCONHECIDO = "desconhecido"
LACUNA = "lacuna"              # a pessoa sabe que não sabe
FRAGIL = "fragil"              # certa pela razão certa, mas numa superfície só
CONFIRMADO = "confirmado"      # premissa correta e sustentada
FALSO_POSITIVO = "falso_positivo"   # certa pela razão errada
REFUTADO = "refutado"          # crença detectada, ainda não trabalhada
EM_TREINO = "em_treino"        # a refutação passou; falta fechar a sequência
EM_ABERTO = "em_aberto"        # o banco de itens acabou antes da sequência
# O banco do nó acabou e NENHUM episódio foi atribuído a ele: ou não houve
# item, ou toda razão errada escolhida nos itens dele apontou um vizinho.
# Não é o mesmo que `desconhecido`, que significa "ainda não chegou a vez" —
# e a diferença importa: uma premissa que a unidade não mediu precisa
# aparecer como não medida, no mapa e na análise.
NAO_MEDIDO = "nao_medido"
# A lacuna foi TRATADA: o nó foi ensinado e a pessoa acertou o item de
# entrada. Não é "confirmada" — um item fácil não demonstra premissa, e a
# CS-5 continua exigindo duas superfícies. É "saiu do zero", e o nó volta
# à fila do diagnóstico como qualquer outro.
CONSTRUIDO = "construido"

CONFIANCAS = ("chutei", "acho que sei", "tenho certeza")
CHUTE = "chutei"
CERTEZA = "tenho certeza"

# Como se chama cada episódio. Não é o estado do nó: é o que aconteceu numa
# atividade. O estado do nó é o que o motor FAZ com isso, logo abaixo.
CONFIRMADA = "confirmada"
FRAGIL_EP = "fragil"
FALSO_POSITIVO_EP = "falso_positivo"
FALSO_NEGATIVO_EP = "falso_negativo"
CRENCA_EP = "crenca"
LACUNA_EP = "lacuna"


def classifica(certa: bool, razao: Razao | None, confianca: str) -> str:
    """Resposta × razão × confiança, nos cinco estados do instrumento.

    É a tabela de `docs/problema.md`, e é função pura de propósito: a banca
    pode conferir linha a linha, sem rodar nada.

    O meio da escala (*acho que sei*) puxa para o lado **conservador de
    cada linha**: não confirma um acerto, e não livra um erro de
    refutação. Acertar acreditando pela metade não é evidência de premissa
    de pé; errar acreditando pela metade é acreditar o bastante.
    """
    if razao is None:
        return LACUNA_EP
    if certa and razao.correta:
        return CONFIRMADA if confianca == CERTEZA else FRAGIL_EP
    if certa:
        # Acertou pela razão errada. NÃO confirma: investiga.
        return FALSO_POSITIVO_EP
    if razao.correta:
        # Errou pelo motivo certo — escorregão, não mal-entendido.
        return FALSO_NEGATIVO_EP
    return LACUNA_EP if confianca == CHUTE else CRENCA_EP

# Fases da unidade.
ABERTURA = "ABERTURA"          # a frase do começo
ENSINO = "ENSINO"
DIAGNOSTICO = "DIAGNOSTICO"
RAZAO = "RAZAO"
CONFIANCA = "CONFIANCA"
VALIDACAO = "VALIDACAO"
REFUTACAO = "REFUTACAO"
# A refutação INTERROGATIVA, atrás de uma chave. A de hoje AFIRMA as
# premissas corretas, uma por tela, e põe a contradição lado a lado no
# fim. A descida PERGUNTA: o que decorre de tomar a sua crença como
# verdadeira? E segue perguntando até a consequência que a própria pessoa
# sabe ser falsa.
DESCIDA = "DESCIDA"
# O fim da descida, nos dois jeitos de ela acabar: a pessoa contradisse a
# própria crença (tela `descida_fim`), ou sustentou até o último degrau e
# recebe o fato (tela `evidencia`). A fase é uma só porque o que vem
# depois é o mesmo: o treino.
FECHO_DESCIDA = "FECHO_DESCIDA"
# O caminho que o fluxo do PRD descreve e que não existia: "lacuna →
# constrói: ensino do nó e item de entrada". Sem ele, declarar que não
# sabe registrava a lacuna e passava para a pergunta seguinte — quatro
# etapas para quem está errado e nenhuma para quem não sabe.
CONSTRUCAO = "CONSTRUCAO"      # o ensino daquele nó, sob demanda
ENTRADA = "ENTRADA"            # o item mais fácil do nó, depois do ensino
# A premissa é apresentada na primeira vez que vai ser perguntada. Não é
# construção — ninguém declarou que não sabe —, é não perguntar sobre uma
# ideia que a unidade nunca disse.
PRIMEIRO_CONTATO = "PRIMEIRO_CONTATO"
TREINO = "TREINO"
RETESTE = "RETESTE"            # a crença refutada volta uma vez, no fim
FECHAMENTO = "FECHAMENTO"      # a frase do fim
FIM = "FIM"


# A descida fica DESLIGADA por padrão, e liga com STRUCTURA_DESCIDA=1.
#
# Dois motivos para a chave. Pedir que alguém raciocine A PARTIR da
# crença dela pode reforçá-la, se a cadeia não fechar — é risco
# pedagógico de verdade, e quem decide corrê-lo é quem conduz a coleta,
# não o código. E uma coleta em andamento mede o fluxo de hoje: trocá-lo
# no meio invalida a comparação entre participantes.
#
# É nome de módulo, e não leitura do ambiente a cada chamada, porque o
# teste troca o valor com `monkeypatch.setattr(motor, "DESCIDA_LIGADA",
# True)`. Recarregar o módulo para reler o ambiente quebra quem já
# importou os nomes dele — já aconteceu neste projeto, com seis testes.
DESCIDA_LIGADA = (os.environ.get("STRUCTURA_DESCIDA") or "") == "1"


class EscolhaInvalida(ValueError):
    """O índice mandado não existe entre as alternativas oferecidas.

    Estourar é a correção de um defeito achado na revisão do ciclo 1:
    `opcoes[-1]` é a última alternativa em Python, então um índice
    negativo virava uma resposta de verdade — classificada, com a crença
    daquela opção no registro, indistinguível no log.

    O motor não escolhe por quem chamou. `None` continua valendo: é como
    "não sei" chega.
    """


def _indice(escolha: int | None, quantas: int, onde: str) -> int | None:
    if escolha is None:
        return None
    if not isinstance(escolha, int) or isinstance(escolha, bool):
        raise EscolhaInvalida("%s: %r não é índice de alternativa" % (onde, escolha))
    if not 0 <= escolha < quantas:
        raise EscolhaInvalida(
            "%s: alternativa %d não existe (são %d)" % (onde, escolha, quantas))
    return escolha


@dataclass(frozen=True)
class Resposta:
    """Entrada do aluno. `escolha` é a posição na tela.

    `repetir` é o "ainda não entendi" do percurso: não é erro, é pedido de
    reexplicação, e o log registra os dois casos separados.
    """

    escolha: int | None = None
    confianca: str = ""
    ms: int = 0
    repetir: bool = False
    # "Não sei", em qualquer das três camadas. Não é o mesmo que não
    # responder: é uma declaração, e vale como dado.
    nao_sei: bool = False
    # Texto livre do teach-back. O sistema NÃO corrige e NÃO classifica:
    # guarda, e devolve para a própria pessoa comparar.
    texto: str = ""


@dataclass(frozen=True)
class Razao:
    """Uma justificativa oferecida na camada 2.

    `no` é o nó que esta razão **afirma** (quando correta) ou **nega**
    (quando é crença). Os dois podem ser diferentes do nó do item: é essa
    diferença que permite registrar a crença onde ela pertence.
    """

    texto: str
    correta: bool = False
    crenca: str | None = None
    no: str = ""


@dataclass(frozen=True)
class Pendente:
    """A resposta trancada, esperando a razão.

    Existir é o que garante que a camada 1 não pode ser mudada depois de a
    camada 2 aparecer: o motor não aceita outra escolha para esta atividade.
    """

    atividade: str
    escolha: int | None
    correta: bool
    crenca_da_opcao: str | None
    ms: int
    origem: str = DIAGNOSTICO          # DIAGNOSTICO ou TREINO
    nao_sei: str = ""                  # camada1 | camada2 | camada3
    confianca: str = ""
    razoes: tuple[Razao, ...] = ()
    razao: Razao | None = None         # a escolhida na camada 2


@dataclass(frozen=True)
class Tela:
    tipo: str                      # ensino | atividade | validacao | refutacao | mapa
    no: str | None = None
    texto: str = ""
    dados: Mapping[str, Any] = field(default_factory=dict)

    def json(self) -> dict:
        saida: dict[str, Any] = {"tipo": self.tipo, "texto": self.texto}
        if self.no:
            saida["no"] = self.no
        saida.update(self.dados)
        return saida


@dataclass(frozen=True)
class Evento:
    tipo: str
    dados: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EstadoNo:
    """O que o sistema sabe sobre uma premissa.

    `streak`, `erros` e `tentativas` são locais ao nó de propósito (RF35):
    domínio de um conceito não empresta nem tira domínio de outro.
    """

    estado: str = DESCONHECIDO
    erros: int = 0                      # erros com confiança no diagnóstico
    streak: int = 0
    tentativas: int = 0
    usadas: tuple[str, ...] = ()        # atividades já apresentadas neste nó
    ultimo_formato: str = ""
    ultima_atividade: str = ""
    crenca: str | None = None           # a hipótese levantada aqui
    vacilou: bool = False               # errou uma vez e corrigiu sozinho
    # CS-5: formatos em que a pessoa acertou PELA RAZÃO CERTA, com
    # confiança. Confirmar exige dois diferentes — um acerto só pode ser
    # reconhecimento do molde da pergunta.
    superficies: tuple[str, ...] = ()
    # Quantas vezes explicou alguma coisa por ESTA crença acertando a
    # resposta. Dois falsos positivos na mesma crença viram refutação (T6).
    falsos_positivos: int = 0
    # Quantas vezes este nó foi construído. Teto de uma: sem teto, quem
    # responde "não sei" a tudo recebe ensino, erra o item de entrada,
    # declara que não sabe de novo e a unidade nunca termina.
    construcoes: int = 0
    # O degrau em que este nó está. Sobe de um em um, e só quando a
    # premissa ficou de pé naquele degrau — errar, chutar ou acertar pela
    # razão errada não promove ninguém.
    nivel: int = 1
    # Este nó já foi apresentado? A abertura ensina só os observáveis, e
    # no kc_02 isso é metade: as três premissas de inferência eram
    # perguntadas sem nunca terem sido ditas. Quem atravessou primeiro
    # chamou de "entrar no chefão já", e estava certo.
    ensinado: bool = False
    # De qual nó veio o item em que a crença foi escolhida, quando não foi
    # deste. É o que permite a tela dizer por que ESTE nó ficou vermelho
    # sem a pessoa ter respondido nada sobre ele.
    origem_crenca: str = ""
    # As duas evidências que ENFRAQUECEM uma premissa, na tabela de força:
    # ter precisado ouvir a mesma premissa de novo, e ter errado no treino
    # dela. Ficam no nó, e não no passo, porque força é histórico do nó.
    reexplicacoes: int = 0
    tropecos: int = 0
    # As instâncias de molde que ela acertou PELA RAZÃO CERTA, uma
    # assinatura por acerto: "<molde>|<k=v ordenado>". Duas assinaturas
    # distintas do mesmo molde são a mesma ideia com a roupa trocada — é
    # a diferença entre generalizar e ter decorado aquela pergunta. Vazio
    # nos itens escritos à mão, que são todos os de hoje.
    instancias: tuple[str, ...] = ()


@dataclass(frozen=True)
class Estado:
    nos: Mapping[str, EstadoNo] = field(default_factory=dict)
    fase: str = ENSINO
    cartao: int = 0
    atividade: str | None = None
    passo: int = 0
    plano: tuple[str, ...] = ()
    alvo: str | None = None
    repeticoes: int = 0            # reexplicações pedidas NESTE passo
    pendente: Pendente | None = None   # camada 1 trancada, esperando a razão
    frase_inicial: str = ""
    frase_final: str = ""
    # A fila do reteste: as crenças refutadas nesta sessão que ainda não
    # voltaram. Fica no estado, e não é recalculada do grafo, porque o nó
    # guarda a crença mas não guarda se ela já foi reperguntada.
    a_retestar: tuple[str, ...] = ()
    # As que já voltaram. Contar pela fila não serve: ela esvazia tanto
    # quando o reteste acontece quanto quando falta item para ele.
    retestadas: tuple[str, ...] = ()
    # Embaralha as razões sem sortear: o motor continua puro, e a mesma
    # semente devolve a mesma ordem. Quem fornece é a sessão.
    semente: str = ""
    # O nó em construção, enquanto a fase é CONSTRUCAO ou ENTRADA.
    construindo: str | None = None

    def no(self, nid: str) -> EstadoNo:
        return self.nos.get(nid, EstadoNo())

    def com(self, nid: str, **campos) -> "Estado":
        return replace(self, nos={**self.nos, nid: replace(self.no(nid), **campos)})


@dataclass(frozen=True)
class Transicao:
    estado: Estado
    tela: Tela
    eventos: tuple[Evento, ...] = ()


# --------------------------------------------------------------------------
# Início e ensino
# --------------------------------------------------------------------------

def inicia(d: Dominio, semente: str = "") -> Transicao:
    estado = Estado(fase=ABERTURA, cartao=0, semente=semente)
    return Transicao(estado, _tela_frase(d, "inicio"),
                     (Evento("unidade_iniciada", {"topico": d.id}),))


def _tela_frase(d: Dominio, momento: str, antes: str = "") -> Tela:
    """A mesma pergunta, duas vezes: antes da unidade e no fim.

    Não tem resposta certa e o sistema não corrige — quem classifica é o
    pesquisador, depois, com codebook. O que a pessoa ganha é ver as duas
    frases lado a lado: é o teach-back de Feynman com antes e depois, e é
    o momento em que a mudança fica visível para ela mesma.
    """
    return Tela("frase", texto=d.teachback, dados={
        "momento": momento,
        "antes": antes,
        # Portão G: dado pessoal é texto livre. A tela diz que fica
        # guardado, e nunca pede nada que identifique.
        "aviso": ("O que você escrever fica guardado com o seu código de "
                  "participante, sem nome. Ninguém corrige esta frase."),
    })


def _cartoes(d: Dominio) -> tuple[str, ...]:
    """O ensino é o enunciado simples dos nós observáveis, um por tela."""
    return tuple(n for n in d.ordem if d.nos[n].observavel)


def _evento_ensino(d: Dominio, e: Estado) -> Evento:
    """O cartão da abertura, no log.

    Sem isto a abertura não deixava rastro: quem lê o log não sabia o que
    a pessoa chegou a ver antes da primeira pergunta — nem dá para
    conferir que nenhuma premissa foi perguntada sem ser apresentada.
    """
    nid = _cartoes(d)[e.cartao]
    return Evento("ensino_apresentado", {
        "no": nid, "indice": e.cartao + 1, "total": len(_cartoes(d)),
        "momento": "abertura"})


def _tela_ensino(d: Dominio, e: Estado) -> Tela:
    nid = _cartoes(d)[e.cartao]
    return Tela("ensino", no=nid, texto=d.nos[nid].simples, dados={
        "indice": e.cartao + 1, "total": len(_cartoes(d)),
        # A frase sozinha fica abstrata para quem nunca declarou uma
        # variável. O exemplo ancora, e é o mesmo código que as atividades
        # daquele nó usam.
        "codigo": d.exemplo(nid),
    })


def avanca(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    if e.fase == ABERTURA:
        return _abre(d, e, r)
    if e.fase == FECHAMENTO:
        return _fecha_unidade(d, e, r)
    if e.fase == ENSINO:
        return _segue_ensino(d, e)
    if e.fase in (DIAGNOSTICO, RETESTE):
        # O reteste pergunta as TRÊS camadas, como o diagnóstico: o
        # critério fala da razão e da confiança, não só do acerto.
        return _responde_diagnostico(d, e, r)
    if e.fase == RAZAO:
        return _responde_razao(d, e, r)
    if e.fase == CONFIANCA:
        return _responde_confianca(d, e, r)
    if e.fase == VALIDACAO:
        return _segue_validacao(d, e)
    if e.fase == REFUTACAO:
        return _segue_refutacao(d, e, repetir=r.repetir)
    if e.fase == DESCIDA:
        return _responde_descida(d, e, r)
    if e.fase == FECHO_DESCIDA:
        return _para_treino(d, e, e.alvo or "", via="descida")
    if e.fase == TREINO:
        return _responde_treino(d, e, r)
    if e.fase == PRIMEIRO_CONTATO:
        a = next(x for x in d.atividades if x.id == e.atividade)
        return _apresenta(d, replace(e, fase=DIAGNOSTICO), a)
    if e.fase == CONSTRUCAO:
        return _segue_construcao(d, e)
    if e.fase == ENTRADA:
        return _responde_entrada(d, e, r)
    return Transicao(e, _mapa(d, e))


def _abre(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    frase = (r.texto or "").strip()
    novo = replace(e, fase=ENSINO, cartao=0, frase_inicial=frase)
    evento = Evento("teachback_inicial", {
        "topico": d.id, "texto": frase,
        "caracteres": len(frase), "em_branco": not frase, "ms": r.ms})
    return Transicao(novo, _tela_ensino(d, novo),
                     (evento, _evento_ensino(d, novo)))


def _fecha_unidade(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    frase = (r.texto or "").strip()
    novo = replace(e, fase=FIM, frase_final=frase)
    evento = Evento("teachback_final", {
        "topico": d.id, "texto": frase,
        "caracteres": len(frase), "em_branco": not frase, "ms": r.ms})
    return Transicao(novo, _mapa(d, novo), (evento,))


def _segue_ensino(d: Dominio, e: Estado) -> Transicao:
    # O cartão que acabou de ser lido marca o nó: ele não precisa de
    # primeiro contato depois.
    e = e.com(_cartoes(d)[e.cartao], ensinado=True)
    proximo = e.cartao + 1
    if proximo < len(_cartoes(d)):
        novo = replace(e, cartao=proximo)
        return Transicao(novo, _tela_ensino(d, novo), (_evento_ensino(d, novo),))
    return _proxima_diagnostica(d, replace(e, fase=DIAGNOSTICO))


# --------------------------------------------------------------------------
# Diagnóstico, com checagem de vacilo
# --------------------------------------------------------------------------

def forca(en: EstadoNo) -> int:
    """Quão sustentada está esta premissa **agora**.

    Sem modelo probabilístico e sem parâmetro estimado. O Duolingo estima
    quando você vai esquecer, o que exige medir retenção ao longo de dias;
    aqui a pergunta é outra, e a resposta sai só do histórico do nó. É a
    tabela de `docs/problema.md`, e é função pura de propósito: a banca
    confere linha a linha sem rodar nada.

    | Evidência | Efeito |
    | --- | --- |
    | certa pela razão certa, com confiança, numa superfície nova | +2 |
    | sobreviveu à troca de superfície | é a SEGUNDA superfície, já contada |
    | acerto pela razão errada | 0 — não conta |
    | erro pela razão certa (vacilo) | 0 — não enfraquece |
    | acerto no treino | +1 |
    | precisou de reexplicação | −1 |
    | tropeçou no treino | −1 |
    | veio de refutação de crença | −2, frágil até o reteste |

    Os dois zeros são decisões, não omissões. Tratar o falso positivo como
    erro puniria esta premissa pelo que aconteceu com **outra** — a crença
    escolhida fala de outro nó. E quem erra enunciando a premissa direito
    escorregou: escorregão não é premissa bamba.
    """
    pontos = 2 * len(set(en.superficies))
    pontos += en.streak
    pontos -= en.reexplicacoes
    pontos -= en.tropecos
    if en.crenca:
        pontos -= 2
    return pontos


def _de_pe(en: EstadoNo) -> bool:
    return en.estado == CONFIRMADO


def _proxima_diagnostica(d: Dominio, e: Estado,
                         preferir: str | None = None) -> Transicao:
    """A próxima premissa é a **mais fraca que ainda não está de pé**.

    É o "trabalhar onde está fraco" sem inventar número: a ordem sai de
    `forca`, que sai do histórico. Empate vale a ordem do grafo — não pode
    virar sorteio, e premissa que vem antes sustenta as de depois.

    O efeito que se vê na tela é a unidade varrer o grafo em largura em
    vez de esgotar um nó de cada vez. Duas perguntas seguidas sobre a
    mesma premissa medem o que ficou do item anterior, não a premissa.

    Dentro do nó, a teórica continua vindo antes da de código: é o par que
    fornece as duas superfícies de CS-5.

    `preferir` põe um nó na frente, **acima da força**. É o que faz o
    falso positivo trazer outra superfície do MESMO nó em vez de seguir
    adiante: a pergunta em aberto é sobre aquela premissa, e adiar não a
    responde.
    """
    posicao = {nid: i for i, nid in enumerate(d.ordem)}
    ordem = sorted(d.ordem, key=lambda nid: (forca(e.no(nid)), posicao[nid]))
    if preferir in d.nos:
        ordem = [preferir] + [nid for nid in ordem if nid != preferir]
    for nid in ordem:
        if tratado(e.no(nid).estado):
            continue
        escolhida, pulo, motivo = _no_degrau(d, e, nid)
        if escolhida is None:
            continue
        novo = replace(e, fase=DIAGNOSTICO, alvo=nid)
        extra = ()
        if pulo is not None:
            # Subiu sem a pessoa ter vencido o degrau. Dois motivos, e eles
            # são coisas MUITO diferentes:
            #
            #   "sem item"  o banco nunca teve item naquele degrau. É furo
            #               de conteúdo, e a curadoria do domínio antigo já
            #               avisava: "tópico sem algum degrau não oferece a
            #               escada inteira";
            #   "esgotado"  o banco tinha, e acabaram. Com UM item por
            #               degrau, quem erra não tem onde tentar de novo —
            #               a escada vira corredor de mão única, e segurar
            #               alguém num degrau exige mais de um item nele.
            #
            # Subir calado esconderia os dois.
            extra = (Evento("degrau_pulado", {
                "no": nid, "de": e.no(nid).nivel, "para": pulo,
                "motivo": motivo}),)
            novo = novo.com(nid, nivel=pulo)
        if not novo.no(nid).ensinado:
            passo = _primeiro_contato(d, novo, nid, escolhida)
            return Transicao(passo.estado, passo.tela, extra + passo.eventos)
        passo = _apresenta(d, novo, escolhida)
        return Transicao(passo.estado, passo.tela, extra + passo.eventos)
    return _encerra(d, e)


def _primeiro_contato(d: Dominio, e: Estado, nid: str,
                      a: Atividade) -> Transicao:
    """A premissa, antes da primeira pergunta sobre ela.

    O ensino da abertura cobre só os nós observáveis — no kc_02, três de
    seis. Os de inferência chegavam como pergunta sobre uma ideia que a
    unidade nunca tinha dito. Perguntar o que não foi apresentado não mede
    concepção errônea: mede quem já sabia de antes.

    Uma tela, uma vez por nó, e o item escolhido vem logo atrás.
    """
    novo = replace(e, fase=PRIMEIRO_CONTATO, alvo=nid, atividade=a.id)
    novo = novo.com(nid, ensinado=True)
    return Transicao(novo, _tela_construcao(d, nid, "primeiro_contato"),
                     (Evento("premissa_apresentada",
                             {"no": nid, "antes_de": a.id}),))


def _no_degrau(d: Dominio, e: Estado, nid: str):
    """O próximo item do nó, respeitando a escada.

    Nunca pula degrau por conta própria: só sobe quando o banco não tem
    item no degrau atual — e, quando faz isso, devolve para onde subiu,
    porque isso vira evento.
    """
    en = e.no(nid)
    todas = d.atividades_do_no(nid, "diagnostico")
    livres = [a for a in todas if a.id not in en.usadas]
    if not livres:
        return None, None, ""
    aqui = [a for a in livres if a.nivel == en.nivel]
    if aqui:
        return aqui[0], None, ""
    acima = sorted([a for a in livres if a.nivel > en.nivel],
                   key=lambda a: a.nivel)
    if acima:
        tinha = any(a.nivel == en.nivel for a in todas)
        return acima[0], acima[0].nivel, (
            "o degrau %d do nó acabou: todos os itens dele já foram usados"
            % en.nivel if tinha else
            "o banco do nó não tem item no degrau %d" % en.nivel)
    # Só restam degraus mais baixos: o nó já passou por eles e o que
    # sobrou ainda mede alguma coisa. Usa sem mexer no degrau.
    return sorted(livres, key=lambda a: -a.nivel)[0], None, ""


def _procedencia(a: Atividade) -> dict:
    """De que molde o item saiu, para o evento — vazio quando não há.

    FORA do evento quando não há molde, e não dentro dele com valor
    vazio: campo vazio em toda linha é ruído que a análise precisa
    aprender a ignorar, e um log que muda de forma sem mudar de conteúdo
    estraga a comparação com as sessões já gravadas.
    """
    if not a.do_molde:
        return {}
    return {"do_molde": a.do_molde, "parametros": dict(a.parametros)}


def _instancia(a: Atividade) -> str:
    """A assinatura da variação, ou vazio quando o item não vem de molde."""
    if not a.do_molde:
        return ""
    return "%s|%s" % (a.do_molde,
                      ",".join("%s=%s" % kv for kv in sorted(a.parametros.items())))


def _instancias_de(a: Atividade) -> tuple[str, ...]:
    """A instância para somar ao nó: vazia quando não há molde."""
    assinatura = _instancia(a)
    return (assinatura,) if assinatura else ()


def _apresenta(d: Dominio, e: Estado, a: Atividade, *, reapresentada: bool = False) -> Transicao:
    en = e.no(a.no)
    novo = replace(e, atividade=a.id)
    novo = novo.com(a.no,
                    usadas=en.usadas if a.id in en.usadas else en.usadas + (a.id,),
                    ultimo_formato=a.formato, ultima_atividade=a.id)
    tela = Tela("atividade", no=a.no, texto=a.texto, dados={
        "atividade": a.id, "fase": e.fase, "formato": a.formato, "item": a.tipo,
        # O degrau vai para a tela: quem responde merece saber que a
        # pergunta ficou mais dura porque ele subiu, e não por acaso.
        "nivel": a.nivel, "niveis": max(NIVEIS),
        "opcoes": [{"texto": o.texto}
                   for o in opcoes_na_tela(e.semente, a)],
        # A confiança saiu daqui: ela é da DUPLA resposta-razão, e tem tela
        # própria depois das duas (T3).
        "pede_confianca": False,
    })
    eventos = [Evento("atividade_apresentada", {
        "atividade": a.id, "no": a.no, "fase": e.fase, "formato": a.formato,
        "item": a.tipo, "nivel": a.nivel, "streak": en.streak,
        "tentativas": en.tentativas, "erros": en.erros,
        **_procedencia(a),
    })]
    if reapresentada:
        eventos.append(Evento("item_reapresentado", {"atividade": a.id, "no": a.no}))
    return Transicao(novo, tela, tuple(eventos))


def razoes_de(d: Dominio, a: Atividade,
              e: Estado | None = None) -> tuple[Razao, ...]:
    """As razões de um item, montadas DO GRAFO.

    A certa é o enunciado do nó que o item mira. As erradas são as crenças
    que as alternativas apontam — e elas podem negar **outros** nós: um
    distrator do item de B1 pode ser uma crença sobre B2. Nenhuma destas
    frases está escrita num banco de razões, porque banco de razões não
    existe: se existisse, a razão e a premissa poderiam divergir.

    COM O ESTADO, a crença de um nó já SUSTENTADO sai do cardápio. Sem
    isso o nó hospedeiro morre de fome: foi medido no kc_02, e o rastro é

        nó B2 — os três itens dele apresentados
        razão escolhida em 004 -> crença de I1
        razão escolhida em 005 -> crença de B3
        razão escolhida em 006 -> crença de I1   (I1 já confirmado)
        estado final de B2: desconhecido

    A crença do próprio B2 estava na cédula nas três vezes. Oferecer para
    sempre uma ideia que a unidade já tratou é o que gasta os itens do nó
    sem nunca medi-lo — e quem checa se ela voltou é o reteste, que é
    explícito e tem fase própria.

    Nunca reduz o cardápio a menos de duas: com uma razão só não há
    escolha, e a camada 2 vira teatro. Nesse caso devolve a lista inteira.

    Ordem canônica, a correta primeiro. Quem apresenta embaralha.
    """
    saida = [Razao(texto=d.nos[a.no].simples, correta=True, no=a.no)]
    vistas: set[str] = set()
    for o in a.opcoes:
        if o.crenca and o.crenca not in vistas and o.crenca in d.crencas:
            vistas.add(o.crenca)
            c = d.crencas[o.crenca]
            saida.append(Razao(texto=c.afirma, crenca=o.crenca, no=c.nega))
    if e is None:
        return tuple(saida)
    vivas = [z for z in saida
             if z.correta or not tratado(e.no(z.no).estado)]
    return tuple(vivas) if len(vivas) >= 2 else tuple(saida)


def ordem_das_razoes(semente: str, atividade: str, n: int) -> tuple[int, ...]:
    """Permutação estável, derivada da semente. Sem sortear: o motor é puro
    e a mesma sessão redesenha a mesma tela depois de um recarregamento."""
    digest = hashlib.sha256(("%s|razoes|%s" % (semente, atividade)).encode()).digest()
    return tuple(i for _, i in sorted((digest[i % len(digest)], i) for i in range(n)))


def ordem_das_opcoes(semente: str, atividade: str, n: int) -> tuple[int, ...]:
    """A mesma permutação estável, agora na camada 1.

    Ela já existia para as razões, e a camada 1 ficou de fora: a tela
    entregava `a.opcoes` na ordem crua do YAML, e o YAML escreve a certa
    em primeiro porque é assim que um humano escreve um gabarito. Daí os
    98,4%.

    O separador é `|opcoes|`, e não `|razoes|`: com o mesmo, as duas
    camadas receberiam a MESMA permutação para o mesmo item, e a posição
    da resposta prediria a posição da razão — um segundo viés no lugar
    do primeiro.

    Devolve índices DO ARQUIVO na ordem da TELA: `ordem[2]` é a opção do
    arquivo que aparece na terceira posição.
    """
    digest = hashlib.sha256(("%s|opcoes|%s" % (semente, atividade)).encode()).digest()
    return tuple(i for _, i in sorted((digest[i % len(digest)], i) for i in range(n)))


def indice_correto_na_tela(semente: str, a: Atividade) -> int:
    """Onde, NA TELA, está a alternativa certa daquele item.

    A companheira de `Atividade.indice_correto_no_arquivo`. Os dois
    nomes existem porque a pergunta "qual é a posição da certa?" passou
    a ter duas respostas, e confundi-las dá resposta errada sem dar
    erro.
    """
    ordem = ordem_das_opcoes(semente, a.id, len(a.opcoes))
    return next(i for i, k in enumerate(ordem) if a.opcoes[k].correta)


def opcoes_na_tela(semente: str, a: Atividade) -> tuple[Opcao, ...]:
    """As alternativas na ordem em que a pessoa as vê.

    As seis pontas que dependiam da posição passam por aqui: duas que
    ESCREVEM a tela e quatro que LEEM o que voltou dela. É a simetria
    que torna a fatia verificável — qualquer uma que ficasse para trás
    produziria o desencontro entre o que foi mostrado e o que foi
    julgado, e o motor aceitaria o índice sem reclamar.
    """
    return tuple(a.opcoes[k]
                 for k in ordem_das_opcoes(semente, a.id, len(a.opcoes)))


def _responde_diagnostico(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    """Camada 1: a resposta TRANCA, e vem a pergunta do porquê.

    Trancar não é detalhe de interface: as razões erradas são enunciados de
    crenças, e lê-las antes de responder entrega a pista — pior, muda a
    resposta de quem ia acertar. Com a camada 1 fechada, o par
    resposta-razão é independente, que é o que a classificação pressupõe.
    """
    a = next(x for x in d.atividades if x.id == e.atividade)
    i = _indice(r.escolha, len(a.opcoes), "camada 1")
    escolhida = opcoes_na_tela(e.semente, a)[i] if i is not None else None
    certo = bool(escolhida and escolhida.correta)

    pendente = Pendente(
        atividade=a.id, escolha=r.escolha, correta=certo,
        crenca_da_opcao=(escolhida.crenca if escolhida else None),
        ms=r.ms, origem=e.fase,
        nao_sei="camada1" if r.nao_sei else "",
    )
    evento = Evento("camada1_respondida", {
        # A origem é a fase: a mesma função atende o diagnóstico e o
        # reteste, e a análise precisa saber de qual dos dois veio a linha.
        "atividade": a.id, "no": a.no, "item": a.tipo, "origem": e.fase.lower(),
        "escolha": r.escolha, "correta": certo, "nao_sei": r.nao_sei,
        "crenca_da_opcao": pendente.crenca_da_opcao, "ms": r.ms,
    })

    # Quem diz que não sabe não tem resposta a justificar nem convicção a
    # declarar. Perguntar as outras duas camadas seria teatro, e a tabela
    # já decidiu: "não sei" em qualquer camada é lacuna.
    if r.nao_sei:
        seguinte = _resolve(d, e, a, pendente)
        return Transicao(seguinte.estado, seguinte.tela,
                         (evento,) + seguinte.eventos)

    razoes = razoes_de(d, a, e)
    # Com uma razão só não há escolha a fazer, e perguntar seria teatro.
    # Acontece em item cujos distratores não apontam crença nenhuma.
    if len(razoes) < 2:
        seguinte = _pede_confianca(d, e, a, pendente)
        return Transicao(seguinte.estado, seguinte.tela,
                         (evento, Evento("razao_pulada", {
                             "atividade": a.id, "no": a.no,
                             "motivo": "item sem crença nas alternativas"}))
                         + seguinte.eventos)

    ordem = ordem_das_razoes(e.semente, a.id, len(razoes))
    pendente = replace(pendente, razoes=tuple(razoes[i] for i in ordem))
    novo = replace(e, fase=RAZAO, pendente=pendente)
    tela = Tela("razao", no=a.no,
                texto="Qual destas ideias explica a sua resposta?",
                dados={
                    "atividade": a.id,
                    "trancada": escolhida.texto if escolhida else "",
                    "opcoes": [{"texto": z.texto} for z in pendente.razoes],
                })
    return Transicao(novo, tela, (evento, Evento("razoes_apresentadas", {
        "atividade": a.id, "no": a.no,
        "quantas": len(pendente.razoes),
        "crencas": [z.crenca for z in pendente.razoes if z.crenca],
    })))


def _responde_razao(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    """Camada 2: a razão escolhida, e em qual nó ela fala."""
    p = e.pendente
    assert p is not None, "fase RAZAO sem resposta trancada"
    a = next(x for x in d.atividades if x.id == p.atividade)
    # Antes, índice fora da faixa virava None — e None na razão é LACUNA.
    # Um erro de cliente entrava na base como alguém dizendo que não sabe.
    j = _indice(r.escolha, len(p.razoes), "camada 2")
    escolhida = p.razoes[j] if j is not None else None

    if r.nao_sei:
        escolhida = None
        p = replace(p, nao_sei="camada2")

    evento = Evento("camada2_respondida", {
        "atividade": a.id, "no": a.no, "escolha": r.escolha,
        "nao_sei": r.nao_sei,
        "razao_correta": bool(escolhida and escolhida.correta),
        "crenca": escolhida.crenca if escolhida else None,
        # O nó de que a razão fala. Diferente de `no` quando a pessoa
        # explicou um item por uma crença que nega o vizinho.
        "fala_do_no": escolhida.no if escolhida else None,
        "ms": r.ms,
    })
    p = replace(p, razao=escolhida)
    if r.nao_sei:
        seguinte = _resolve(d, e, a, p)
    else:
        seguinte = _pede_confianca(d, e, a, p)
    return Transicao(seguinte.estado, seguinte.tela, (evento,) + seguinte.eventos)


# --------------------------------------------------------------------------
# Camada 3: a confiança
# --------------------------------------------------------------------------

def _pede_confianca(d: Dominio, e: Estado, a: Atividade,
                    p: Pendente) -> Transicao:
    """Tela própria, uma vez por atividade, depois das duas escolhas.

    Própria, e não no pé da tela da razão, porque é das duas escolhas
    JUNTAS que se pergunta a confiança — e porque declarar confiança antes
    de ver o par formado mede outra coisa.

    Em **toda** atividade, não só no diagnóstico: o critério de sucesso diz
    que a razão muda *sem queda de confiança*, e isso exige duas medidas.
    """
    novo = replace(e, fase=CONFIANCA, pendente=p)
    tela = Tela("confianca", no=a.no,
                texto="Quanta confiança você tem nessa dupla?",
                dados={
                    "atividade": a.id,
                    "resposta": (opcoes_na_tela(e.semente, a)[p.escolha].texto
                                 if p.escolha is not None else ""),
                    "razao": p.razao.texto if p.razao else "",
                    "escala": list(CONFIANCAS),
                })
    return Transicao(novo, tela, ())


def _responde_confianca(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    p = e.pendente
    assert p is not None, "fase CONFIANCA sem resposta trancada"
    a = next(x for x in d.atividades if x.id == p.atividade)
    p = replace(p, confianca=r.confianca,
                nao_sei="camada3" if r.nao_sei else p.nao_sei)

    evento = Evento("camada3_respondida", {
        "atividade": a.id, "no": a.no, "confianca": r.confianca,
        "nao_sei": r.nao_sei, "origem": p.origem.lower(), "ms": r.ms,
    })
    seguinte = _resolve(d, e, a, p)
    return Transicao(seguinte.estado, seguinte.tela, (evento,) + seguinte.eventos)


def _resolve(d: Dominio, e: Estado, a: Atividade, p: Pendente) -> Transicao:
    """Quem fecha o episódio depende de ONDE ele aconteceu.

    A origem viaja no `Pendente` desde a camada 1 — não na fase do estado,
    que `_apresenta` não toca. Sem isso o reteste seria resolvido como
    diagnóstico, e uma pergunta feita para medir viraria uma pergunta que
    muda o que mede.
    """
    if p.origem == TREINO:
        return _resolve_treino(d, e, a, p)
    if p.origem == RETESTE:
        return _resolve_reteste(d, e, a, p)
    return _resolve_diagnostico(d, e, a, p)


def _resolve_diagnostico(d: Dominio, e: Estado, a: Atividade,
                         p: Pendente) -> Transicao:
    """O que o episódio faz com o nó — e com qual nó.

    Aqui a camada 2 passa a mandar. O erro isolado deixa de ser tratado
    como vacilo "até prova em contrário": a razão **é** a prova. Quem erra
    pelo motivo certo escorregou; quem erra pelo motivo errado, com
    confiança, nomeou a própria crença, e não há por que fazer uma segunda
    pergunta para descobrir o que já foi dito.

    E a crença vai para o nó que **ela** nega, não para o nó do item: errar
    uma pergunta sobre B1 dizendo que sem valor não há memória é informação
    sobre **B2**, e é lá que ela pertence.
    """
    # A resolução acontece sempre a partir do DIAGNÓSTICO, venha ela da
    # camada 2 ou do atalho de item sem razões: `_apresenta` não mexe na
    # fase, e a segunda pergunta do nó sairia marcada como RAZAO.
    e = replace(e, fase=DIAGNOSTICO, pendente=None)
    certo = p.correta
    r = Resposta(escolha=p.escolha, confianca=p.confianca, ms=p.ms)
    en = e.no(a.no)
    # CS-4: "não sei" em QUALQUER camada é lacuna, e lacuna declarada —
    # observada, não inferida de confiança baixa.
    episodio = LACUNA_EP if p.nao_sei else classifica(certo, p.razao, p.confianca)

    eventos = [
        Evento("resposta_registrada", {
            "atividade": a.id, "no": a.no, "fase": "diagnostico", "item": a.tipo,
            "escolha": r.escolha, "correta": certo,
            "crenca_em_jogo": a.crenca, "confianca": r.confianca, "ms": r.ms,
        }),
        Evento("episodio_classificado", {
            "atividade": a.id, "no": a.no, "estado": episodio,
            "correta": certo, "confianca": r.confianca,
            "nao_sei": p.nao_sei or None,
            "razao_correta": bool(p.razao and p.razao.correta),
            "crenca": p.razao.crenca if p.razao else None,
        }),
    ]

    # ---------------------------------------------------------- acertou
    if episodio == CONFIRMADA:
        # CS-5: duas superfícies diferentes. Um acerto só pode ser
        # reconhecimento do molde da pergunta, não da ideia.
        superficies = en.superficies + (a.formato,)
        fechou = len(set(superficies)) >= 2
        novo = e.com(a.no, superficies=superficies,
                     estado=CONFIRMADO if fechou else FRAGIL,
                     nivel=min(max(NIVEIS), en.nivel + 1),
                     vacilou=bool(en.erros),
                     instancias=en.instancias + _instancias_de(a))
        eventos.append(_degrau(a.no, en.nivel, novo.no(a.no).nivel, a))
        if fechou:
            eventos.append(Evento("no_confirmado", {
                "no": a.no, "via": "vacilo" if en.erros else "diagnostico",
                "superficies": sorted(set(superficies))}))
        else:
            eventos.append(Evento("no_fragil", {
                "no": a.no, "motivo": "uma superfície só",
                "superficies": sorted(set(superficies))}))
        return _segue(d, novo, eventos)

    if episodio == FRAGIL_EP:
        # Certa pela razão certa, mas sem convicção. Não conta superfície —
        # mas sobe o degrau: a premissa ficou de pé ali, com meia certeza.
        novo = e.com(a.no, estado=FRAGIL,
                     nivel=min(max(NIVEIS), en.nivel + 1),
                     instancias=en.instancias + _instancias_de(a))
        eventos.append(_degrau(a.no, en.nivel, novo.no(a.no).nivel, a))
        eventos.append(Evento("no_fragil", {
            "no": a.no, "motivo": "confiança abaixo de certeza",
            "confianca": r.confianca}))
        return _segue(d, novo, eventos)

    if episodio == FALSO_POSITIVO_EP:
        # Acertou pela razão errada: o nó do item NÃO confirma, e a crença
        # escolhida é contada no nó que ela nega.
        crenca = p.razao.crenca if p.razao else None
        alvo = p.razao.no if p.razao else a.no
        novo = e.com(a.no, estado=FALSO_POSITIVO)
        if not crenca:
            return _segue(d, novo, eventos)

        alvo_en = novo.no(alvo)
        vezes = alvo_en.falsos_positivos + 1
        novo = novo.com(alvo, falsos_positivos=vezes, crenca=crenca,
                        origem_crenca=a.no if alvo != a.no else "")
        eventos.append(Evento("falso_positivo", {
            "no": a.no, "crenca": crenca, "fala_do_no": alvo, "vezes": vezes}))

        # Uma vez pode ser acidente de alternativa — ela marcou a certa por
        # eliminação e explicou mal. Duas vezes, na MESMA ideia, é a ideia.
        if vezes >= FALSOS_POSITIVOS_PARA_CRENCA and not tratado(alvo_en.estado):
            eventos.append(Evento("crenca_detectada", {
                "crenca": crenca, "no": alvo, "veio_do_item_de": a.no,
                "via": "falso positivo repetido", "vezes": vezes,
                "confianca": r.confianca}))
            novo = novo.com(alvo, estado=REFUTADO)
            inicio = _inicia_validacao(d, novo, alvo)
            return Transicao(inicio.estado, inicio.tela,
                             tuple(eventos) + inicio.eventos)

        # Ainda não refuta: traz OUTRA superfície do mesmo nó, para ver se
        # a explicação errada se repete ou foi tropeço de alternativa.
        return _segue(d, novo, eventos, preferir=a.no)

    # ----------------------------------------------------------- errou
    if episodio == FALSO_NEGATIVO_EP:
        # CS-3: errar pelo motivo certo não dispara refutação. O sistema
        # não contesta uma ideia que a pessoa acabou de enunciar direito.
        novo = e.com(a.no, erros=en.erros + 1, vacilou=True)
        eventos.append(Evento("vacilo_detectado", {
            "no": a.no, "crenca_suspeita": None, "atividade": a.id}))
        return _segue(d, novo, eventos)

    if episodio == LACUNA_EP:
        # Não refuta o que a pessoa não pensa — CONSTRÓI.
        eventos.append(Evento("lacuna_registrada", {
            "no": a.no, "confianca": r.confianca,
            "declarada": p.nao_sei or None}))
        novo = e.com(a.no, estado=LACUNA)
        if novo.no(a.no).construcoes == 0:
            inicio = _inicia_construcao(d, novo, a.no)
            return Transicao(inicio.estado, inicio.tela,
                             tuple(eventos) + inicio.eventos)
        # Já construiu uma vez neste nó. Ensinar de novo a mesma coisa não
        # ensina mais, e sem teto a unidade não termina.
        eventos.append(Evento("construcao_dispensada", {
            "no": a.no, "motivo": "o nó já foi construído nesta sessão"}))
        return _segue(d, novo, eventos)

    # --------------------------------------------------- crença ativa
    crenca = p.razao.crenca if p.razao else a.crenca
    alvo = p.razao.no if (p.razao and p.razao.crenca) else a.no
    eventos.append(Evento("crenca_detectada", {
        "crenca": crenca, "no": alvo, "veio_do_item_de": a.no,
        "erros": en.erros + 1, "confianca": r.confianca}))
    novo = e.com(a.no, erros=en.erros + 1)

    # O QUARTO TETO. A atribuição cruzada manda a crença para o nó da
    # RAZÃO, que pode ser outro — e aquele nó pode já ter fechado nesta
    # sessão. Sem este portão ele voltava a REFUTADO e levava validação,
    # refutação e mais quatro tentativas de treino, uma vez por item de
    # vizinho que oferecesse a crença dele. Na sessão mais longa do kc_03
    # com dois itens por degrau isso dava 16 telas de treino num nó só.
    #
    # A evidência não se perde: `crenca_detectada` já está no log acima,
    # porque a pessoa disse a crença de novo e isso é dado. O que não
    # acontece é o laço rodar outra vez.
    if tratado(novo.no(alvo).estado):
        eventos.append(Evento("refutacao_dispensada", {
            "no": alvo, "crenca": crenca, "veio_do_item_de": a.no,
            "motivo": "o nó já fechou nesta sessão",
            "estado": novo.no(alvo).estado}))
        return _segue(d, novo, eventos)

    novo = novo.com(alvo, estado=REFUTADO, crenca=crenca,
                    origem_crenca=a.no if alvo != a.no else "")
    inicio = _inicia_validacao(d, novo, alvo)
    return Transicao(inicio.estado, inicio.tela, tuple(eventos) + inicio.eventos)


# --------------------------------------------------------------------------
# Lacuna → constrói
#
# O fluxo do PRD sempre disse "lacuna → constrói: ensino do nó e item de
# entrada". Até aqui a lacuna era registrada e a unidade seguia: quatro
# etapas para quem está errado (valida, refuta, treina, confirma) e zero
# para quem não sabe. A primeira pessoa que atravessou a unidade declarando
# "não sei" em tudo sentiu isso em cinco minutos.
#
# Três passos, e só três: ensina o nó, oferece o item mais fácil dele, e
# devolve a pessoa ao fluxo. Uma vez por nó.
# --------------------------------------------------------------------------

def _inicia_construcao(d: Dominio, e: Estado, no: str) -> Transicao:
    """O ensino daquele nó, sob demanda, com a analogia de resgate junto."""
    en = e.no(no)
    novo = replace(e, fase=CONSTRUCAO, construindo=no, atividade=None,
                   pendente=None)
    novo = novo.com(no, construcoes=en.construcoes + 1, ensinado=True)
    tem_item = d.entrada(no, en.usadas) is not None
    evento = Evento("construcao_iniciada", {
        "no": no, "tem_item_de_entrada": tem_item})
    return Transicao(novo, _tela_construcao(d, no), (evento,))


def _tela_construcao(d: Dominio, no: str, motivo: str = "lacuna") -> Tela:
    """A mesma premissa da tela de ensino, com o resgate e o exemplo.

    `motivo` existe para a tela poder dizer POR QUE ela apareceu agora: a
    abertura da unidade, a resposta a um "não sei", ou a primeira vez que
    aquela premissa vai ser perguntada.
    """
    return Tela("ensino", no=no, texto=d.nos[no].simples, dados={
        "motivo": motivo,
        "codigo": d.exemplo(no),
        "resgate": d.resgate(no),
    })


def _segue_construcao(d: Dominio, e: Estado) -> Transicao:
    """Depois do ensino, o item de entrada — se o banco tiver um."""
    no = e.construindo or ""
    item = d.entrada(no, e.no(no).usadas)
    if item is None:
        # Sem item de entrada o nó foi ensinado e nada foi medido. Dizer
        # isso é o mínimo: calar faria a construção parecer completa.
        novo = replace(e, fase=DIAGNOSTICO, construindo=None)
        evento = Evento("entrada_sem_item", {
            "no": no, "motivo": "o banco do nó não tem item de entrada"})
        return _segue(d, novo, [evento], preferir=no)
    en = e.no(no)
    novo = replace(e, fase=ENTRADA, atividade=item.id)
    novo = novo.com(no, usadas=en.usadas + (item.id,),
                    ultima_atividade=item.id, ultimo_formato=item.formato)
    tela = Tela("atividade", no=no, texto=item.texto, dados={
        "atividade": item.id, "fase": ENTRADA, "formato": item.formato,
        "item": item.tipo, "opcoes": [{"texto": o.texto}
                   for o in opcoes_na_tela(e.semente, item)],
        "pede_confianca": False,
    })
    evento = Evento("atividade_apresentada", {
        "atividade": item.id, "no": no, "fase": ENTRADA,
        "formato": item.formato, "item": item.tipo,
        "streak": en.streak, "tentativas": en.tentativas, "erros": en.erros,
        **_procedencia(item),
    })
    return Transicao(novo, tela, (evento,))


def _responde_entrada(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    """Camada 1 e só ela.

    Perguntar "por quê" logo depois de ensinar mediria o eco do ensino, não
    o que a pessoa pensa — e poderia levantar uma crença que ela não tem.
    """
    item = next(x for x in d.atividades if x.id == e.atividade)
    no = e.construindo or item.no
    i = _indice(r.escolha, len(item.opcoes), "item de entrada")
    escolhida = (opcoes_na_tela(e.semente, item)[i]
                 if i is not None else None)
    certo = bool(escolhida and escolhida.correta)

    en = e.no(no)
    novo = replace(e, fase=DIAGNOSTICO, construindo=None, atividade=None)
    novo = novo.com(no, estado=CONSTRUIDO if certo else LACUNA,
                    tropecos=en.tropecos + (0 if certo else 1))
    eventos = [
        Evento("resposta_registrada", {
            "atividade": item.id, "no": no, "fase": "entrada",
            "item": item.tipo, "escolha": r.escolha, "correta": certo,
            "crenca_em_jogo": item.crenca, "confianca": "", "ms": r.ms,
        }),
        Evento("construcao_concluida", {
            "no": no, "atividade": item.id, "acertou": certo,
            # Acertar aqui NÃO confirma: a CS-5 continua exigindo duas
            # superfícies, e o item de entrada é o degrau mais baixo.
            "estado": CONSTRUIDO if certo else LACUNA,
        }),
    ]
    # Volta ao fluxo preferindo o próprio nó: a pergunta em aberto é sobre
    # ele, e seguir para outro deixaria a construção sem desfecho.
    return _segue(d, novo, eventos, preferir=no)


def _degrau(no: str, de: int, para: int, a: Atividade) -> Evento:
    """Subiu, ou bateu no teto. Os dois casos viram dado: quem chega ao
    degrau 3 e quem fica no 1 a unidade inteira não aprenderam a mesma
    coisa, e o estado do nó sozinho não distingue."""
    return Evento("degrau", {
        "no": no, "de": de, "para": para,
        # O degrau do ITEM que acabou de ser respondido. `para` é só o
        # contador do nó, e os dois divergem: um nó confirmado na CS-5 no
        # degrau 2 tem o contador em 3 sem nunca ter visto um item de 3.
        # Quem analisa precisa saber qual dos dois está olhando.
        "degrau_do_item": a.nivel, "atividade": a.id,
        "subiu": para > de, "no_teto": para == max(NIVEIS),
    })


def sustentado(estado: str) -> bool:
    """A premissa está de pé? Nem frágil nem falso positivo contam."""
    return estado == CONFIRMADO


def tratado(estado: str) -> bool:
    """A sessão já gastou o laço nesta premissa?

    `em_aberto` NÃO é `confirmado` — a premissa não está de pé, e é por
    isso que `sustentado` continua valendo só para o confirmado. O que as
    duas têm em comum é outra coisa: a unidade já rodou identifica →
    refuta → treina nelas, e chegou ao fim daquele laço. Uma confirmou; a
    outra bateu no teto de tentativas ou esgotou o banco.

    Em qualquer dos dois casos, voltar a refutar é insistir no que já foi
    insistido. É o mesmo argumento de TETO_TENTATIVAS e de uma construção
    por nó, escrito uma vez só e usado em quatro lugares: a fila do
    diagnóstico, o cardápio da camada 2, a promoção do falso positivo
    repetido, e o portão da refutação.
    """
    return estado in (CONFIRMADO, EM_ABERTO)


def _segue(d: Dominio, e: Estado, eventos: list[Evento],
           preferir: str | None = None) -> Transicao:
    seguinte = _proxima_diagnostica(d, e, preferir=preferir)
    return Transicao(seguinte.estado, seguinte.tela,
                     tuple(eventos) + seguinte.eventos)


# --------------------------------------------------------------------------
# Validação e refutação
# --------------------------------------------------------------------------

def _inicia_validacao(d: Dominio, e: Estado, no: str) -> Transicao:
    """Antes de refutar, reconhecer — e dar a analogia de resgate.

    Quem se sente corrigido defende a posição; quem se sente ouvido examina
    a própria premissa. A analogia não é conteúdo novo: é a mesma premissa,
    dita de um jeito que não depende de já se entender o conceito.
    """
    crenca = d.crencas.get(e.no(no).crenca or "")
    novo = replace(e, fase=VALIDACAO, alvo=no)
    tela = Tela("validacao", no=no, texto=d.resgate(no), dados={
        "crenca": crenca.afirma if crenca else "",
    })
    return Transicao(novo, tela, (Evento("validacao_apresentada", {
        "no": no, "crenca": e.no(no).crenca}),))


def _segue_validacao(d: Dominio, e: Estado) -> Transicao:
    """Daqui saem os dois caminhos: a refutação de hoje, ou a descida.

    A descida só roda com a chave ligada E com cadeia escrita para
    AQUELA crença. Tópico sem descida, ou crença sem cadeia, segue pela
    refutação de sempre — é o que torna o protótipo de uma crença
    possível sem mexer nas outras setenta e oito.
    """
    alvo = e.alvo or ""
    descida = d.descida(e.no(alvo).crenca) if DESCIDA_LIGADA else None
    if descida is not None:
        return _inicia_descida(d, e, alvo, descida)
    return _inicia_refutacao(d, e, alvo)


def _plano(d: Dominio, no: str) -> tuple[str, ...]:
    """As premissas que sustentam o nó, das observáveis até ele.

    Pós-ordem, cada nó uma vez. O percurso é derivado do grafo: nenhuma
    dessas telas está escrita em lugar nenhum.
    """
    vistos: list[str] = []

    def visita(nid: str) -> None:
        if nid in vistos:
            return
        for s in d.nos[nid].suporte:
            visita(s)
        vistos.append(nid)

    visita(no)
    return tuple(vistos)


def _inicia_refutacao(d: Dominio, e: Estado, no: str) -> Transicao:
    plano = _plano(d, no)
    novo = replace(e, fase=REFUTACAO, alvo=no, plano=plano, passo=0, repeticoes=0)
    evento = Evento("refutacao_iniciada", {
        "no": no, "crenca": e.no(no).crenca, "passos": list(plano)})
    return Transicao(novo, _tela_refutacao(d, novo), (evento,))


def _tela_refutacao(d: Dominio, e: Estado) -> Tela:
    nid = e.plano[e.passo]
    alvo = e.alvo or nid
    crenca = d.crencas.get(e.no(alvo).crenca or "")
    ultimo = e.passo == len(e.plano) - 1
    return Tela("refutacao", no=nid, texto=d.nos[nid].simples, dados={
        "passo": e.passo + 1, "total": len(e.plano),
        # No último passo — o nó que a crença nega — as duas frases ficam
        # lado a lado. A contradição é entre coisas que ele mesmo disse.
        "contradiz": crenca.afirma if (ultimo and crenca) else "",
        # Pediu de novo: volta a mesma premissa, agora com a analogia
        # daquele nó. É a mesma afirmação, dita por outro caminho.
        "reexplicacao": d.resgate(nid) if e.repeticoes else "",
        "repeticoes": e.repeticoes,
        "pode_repetir": e.repeticoes < LIMITE_REEXPLICACAO,
    })


def _segue_refutacao(d: Dominio, e: Estado, repetir: bool = False) -> Transicao:
    nid = e.plano[e.passo]

    # "Ainda não entendi" não é erro: é pedido de reexplicação. A premissa
    # volta com a analogia, e o percurso não anda enquanto isso.
    if repetir and e.repeticoes < LIMITE_REEXPLICACAO:
        novo = replace(e, repeticoes=e.repeticoes + 1)
        # Enfraquece a premissa REAPRESENTADA, não o alvo da refutação: foi
        # ela que a pessoa disse não ter entendido.
        novo = novo.com(nid, reexplicacoes=novo.no(nid).reexplicacoes + 1)
        evento = Evento("premissa_reapresentada", {
            "no": nid, "alvo": e.alvo, "vez": novo.repeticoes})
        return Transicao(novo, _tela_refutacao(d, novo), (evento,))

    eventos: tuple[Evento, ...] = ()
    if repetir:
        # Estourou o limite: segue, e o log diz que esta premissa ficou sem
        # ser entendida. O treino depois é quem vai pegar isso.
        eventos = (Evento("premissa_nao_fechou", {
            "no": nid, "alvo": e.alvo, "repeticoes": e.repeticoes}),)

    proximo = e.passo + 1
    if proximo < len(e.plano):
        novo = replace(e, passo=proximo, repeticoes=0)
        return Transicao(novo, _tela_refutacao(d, novo), eventos)

    return _para_treino(d, e, e.alvo or e.plano[-1], eventos)


def _para_treino(d: Dominio, e: Estado, alvo: str,
                 eventos: tuple[Evento, ...] = (),
                 via: str = "refutacao") -> Transicao:
    """O fim do percurso, por onde quer que ele tenha passado.

    RF33: a refutação NÃO confirma o nó. Ela o põe em treino. Vale igual
    para a descida: a pessoa ter dito "não é assim" com as próprias
    palavras é melhor evidência do que ter ouvido, e continua não sendo
    prova de que ela resolve o próximo item.
    """
    novo = e.com(alvo, estado=EM_TREINO, streak=0, tentativas=0)
    crenca = novo.no(alvo).crenca
    novo = replace(novo, fase=TREINO, plano=(), passo=0, repeticoes=0,
                   # A crença entra na fila do reteste aqui, e não no fim:
                   # é agora que se sabe que ela foi mesmo refutada.
                   a_retestar=(novo.a_retestar + (crenca,)
                               if crenca and crenca not in novo.a_retestar
                               else novo.a_retestar))
    eventos = tuple(eventos) + (
        Evento("refutacao_concluida", {"no": alvo, "via": via}),
        Evento("treino_iniciado", {"no": alvo, "streak_alvo": STREAK_ALVO}),
    )
    seguinte = _proximo_treino(d, novo, alvo)
    return Transicao(seguinte.estado, seguinte.tela, eventos + seguinte.eventos)


# --------------------------------------------------------------------------
# Descida interrogativa
# --------------------------------------------------------------------------

# A INVERSÃO: em toda atividade deste sistema a alternativa certa é a
# verdadeira. Aqui não. `DECORRE` é o que a CRENÇA prevê, e é ela que faz
# a cadeia andar — estamos pedindo consistência com o erro, de propósito.
DECORRE = 0
VERDADE = 1


def _inicia_descida(d: Dominio, e: Estado, no: str, desc) -> Transicao:
    novo = replace(e, fase=DESCIDA, alvo=no, plano=(), passo=0, repeticoes=0)
    evento = Evento("descida_iniciada", {
        "no": no, "crenca": desc.crenca, "degraus": len(desc.passos),
        "colide_com": desc.colide_com})
    return Transicao(novo, _tela_descida(d, novo, desc), (evento,))


def _tela_descida(d: Dominio, e: Estado, desc) -> Tela:
    p = desc.passos[e.passo]
    ultimo = e.passo == len(desc.passos) - 1
    crenca = d.crencas.get(desc.crenca)
    # A premissa da colisão entra só no último degrau, e a ATRIBUIÇÃO dela
    # depende do que esta sessão viu: "você confirmou" só se ela confirmou
    # mesmo. Dizer a alguém que ela afirmou o que não afirmou destrói a
    # única coisa que faz a descida funcionar, que é a pessoa reconhecer
    # cada passo como seu.
    disse = ultimo and sustentado(e.no(desc.colide_com).estado)
    return Tela("descida", no=e.alvo, texto=p.pergunta, dados={
        "passo": e.passo + 1, "total": len(desc.passos),
        "crenca": crenca.afirma if crenca else "",
        "opcoes": [p.decorre, p.verdade],
        "premissa": d.nos[desc.colide_com].simples if ultimo else "",
        "premissa_no": desc.colide_com if ultimo else "",
        "voce_disse": disse,
    })


def _responde_descida(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    alvo = e.alvo or ""
    desc = d.descida(e.no(alvo).crenca)
    if desc is None:
        # A chave caiu no meio da sessão, ou o domínio foi trocado. Não é
        # para acontecer, e se acontecer a refutação de sempre assume.
        return _inicia_refutacao(d, e, alvo)

    p = desc.passos[e.passo]
    ultimo = e.passo == len(desc.passos) - 1
    base = {"no": alvo, "crenca": desc.crenca,
            "profundidade": e.passo + 1, "total": len(desc.passos)}

    escolha = None if r.nao_sei else _indice(r.escolha, 2, "descida")

    if escolha is None:
        # Nem seguiu nem contradisse: a cadeia não fecha pela boca dela, e
        # inventar que fechou seria falso. Vai para o fato.
        return _evidencia(d, e, desc, (Evento("descida_sem_resposta", dict(
            base, nao_sei=r.nao_sei, ms=r.ms)),))

    if escolha == VERDADE:
        # A pessoa acabou de contradizer a própria crença. É o fim da
        # descida: insistir depois disto é argumentar com quem já
        # concordou.
        crenca = d.crencas.get(desc.crenca)
        novo = replace(e, fase=FECHO_DESCIDA)
        tela = Tela("descida_fim", no=alvo, texto=p.porque, dados={
            "passo": e.passo + 1, "total": len(desc.passos),
            "crenca": crenca.afirma if crenca else "",
            "voce_disse": p.verdade,
            # Chegar ao último degrau e só ali recuar é outro dado que
            # recuar no primeiro: a tela não muda, o log sabe.
            "no_fim": ultimo,
        })
        return Transicao(novo, tela, (Evento("descida_fechou",
                                             dict(base, no_fim=ultimo,
                                                  ms=r.ms)),))

    eventos = (Evento("descida_passo", dict(base, escolha="decorre",
                                            ms=r.ms)),)
    if not ultimo:
        novo = replace(e, passo=e.passo + 1)
        return Transicao(novo, _tela_descida(d, novo, desc), eventos)

    # Sustentou a crença até o fim. A cadeia inteira não bastou, e é aqui
    # que o sistema para de perguntar e mostra o fato.
    return _evidencia(d, e, desc, eventos + (Evento(
        "descida_sustentada", dict(base)),))


def _evidencia(d: Dominio, e: Estado, desc,
               eventos: tuple[Evento, ...]) -> Transicao:
    ev = desc.evidencia
    novo = replace(e, fase=FECHO_DESCIDA)
    # `evidencia`, e NÃO `tipo`: o log escreve {"tipo": <evento>, **dados},
    # então um dado chamado `tipo` sobrescrevia o nome do evento. Esta
    # linha já saiu no log como "erro_de_compilacao" uma vez. O log agora
    # protege os campos da casa (ver `log._linha`), e este nome continua
    # sendo o certo: o que está aqui é o tipo DA EVIDÊNCIA.
    eventos = eventos + (Evento("evidencia_apresentada", {
        "no": e.alvo, "crenca": desc.crenca, "evidencia": ev.tipo,
        "origem": ev.origem, "gravada": ev.gravada}),)
    tela = Tela("evidencia", no=e.alvo, texto=ev.afirmacao, dados={
        "programa": ev.fonte, "comando": ev.comando, "garantia": ev.garantia,
        # Terminal só quando houve terminal. Esta tela promete evidência,
        # e evidência inventada é pior que evidência nenhuma: sem saída
        # gravada, ela mostra o programa e a garantia do padrão, e diz que
        # ninguém rodou.
        "saida": ev.saida if ev.gravada else "",
        "gravada": ev.gravada, "origem": ev.origem, "onde": ev.onde,
    })
    return Transicao(novo, tela, eventos)


# --------------------------------------------------------------------------
# Treino
# --------------------------------------------------------------------------

def proximo_item(d: Dominio, e: Estado, no: str) -> tuple[Atividade | None, bool]:
    """O próximo item de treino do nó, e se ele está sendo reapresentado.

    O treino tem banco PRÓPRIO (`uso: treino`): a sequência de acertos não
    é feita das perguntas que o aluno acabou de responder no diagnóstico —
    isso seria reapresentar a mesma pergunta logo depois de ela ter sido
    discutida, e provaria pouco.

    RF34 pede formato diferente do anterior e nenhum item repetido em
    sequência. Esgotado o banco de treino, o seletor aceita reapresentar um
    item do diagnóstico em vez de deixar o nó sem como fechar — e marca a
    reapresentação no log, para a análise poder descontá-la.
    """
    en = e.no(no)
    proprios = [a for a in d.atividades_do_no(no, "treino")
                if a.id not in en.usadas and a.id != en.ultima_atividade]
    if proprios:
        outro = [a for a in proprios if a.formato != en.ultimo_formato]
        return (outro or proprios)[0], False

    todas = [a for a in d.atividades_do_no(no) if a.id != en.ultima_atividade]
    if not todas:
        return None, False
    if not todas:
        return None, False
    outro_formato = [a for a in todas if a.formato != en.ultimo_formato]
    escolhidas = outro_formato or todas
    inedita = [a for a in escolhidas if a.id not in en.usadas]
    if inedita:
        return inedita[0], False
    return escolhidas[0], True


def _proximo_treino(d: Dominio, e: Estado, no: str) -> Transicao:
    en = e.no(no)

    if en.streak >= STREAK_ALVO:
        novo = e.com(no, estado=CONFIRMADO)
        eventos = (
            Evento("training_streak_completed", {
                "no": no, "streak": en.streak, "tentativas": en.tentativas,
                "crenca": en.crenca}),
            Evento("no_confirmado", {"no": no, "via": "treino"}),
        )
        seguinte = _proxima_diagnostica(d, replace(novo, fase=DIAGNOSTICO, alvo=None))
        return Transicao(seguinte.estado, seguinte.tela, eventos + seguinte.eventos)

    item, reapresentada = proximo_item(d, e, no)
    estourou = en.tentativas >= TETO_TENTATIVAS

    # RF36: banco esgotado ou teto atingido encerra o nó em aberto. A sessão
    # não trava, e o log diz por quê.
    if item is None or estourou:
        novo = e.com(no, estado=EM_ABERTO)
        evento = Evento("no_em_aberto", {
            "no": no, "motivo": "teto de tentativas" if estourou else "banco esgotado",
            "streak": en.streak, "tentativas": en.tentativas})
        seguinte = _proxima_diagnostica(d, replace(novo, fase=DIAGNOSTICO, alvo=None))
        return Transicao(seguinte.estado, seguinte.tela, (evento,) + seguinte.eventos)

    return _apresenta(d, replace(e, fase=TREINO, alvo=no), item,
                      reapresentada=reapresentada)


def _responde_treino(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    """O treino não pergunta o porquê — pergunta a confiança.

    A razão é do diagnóstico: é lá que ela separa chute, vacilo e crença.
    No treino o nó já foi refutado e o que está em jogo é se a premissa se
    sustenta em outra superfície — e com quanta convicção.
    """
    a = next(x for x in d.atividades if x.id == e.atividade)
    k = _indice(r.escolha, len(a.opcoes), "camada 1 do treino")
    escolhida = None if r.nao_sei else (
        opcoes_na_tela(e.semente, a)[k] if k is not None else None)
    certo = bool(escolhida and escolhida.correta)

    pendente = Pendente(
        atividade=a.id, escolha=r.escolha, correta=certo,
        crenca_da_opcao=(escolhida.crenca if escolhida else None),
        ms=r.ms, origem=TREINO,
        nao_sei="camada1" if r.nao_sei else "",
    )
    evento = Evento("camada1_respondida", {
        "atividade": a.id, "no": a.no, "item": a.tipo, "origem": "treino",
        "escolha": r.escolha, "correta": certo, "nao_sei": r.nao_sei,
        "crenca_da_opcao": pendente.crenca_da_opcao, "ms": r.ms,
    })
    # No treino "não sei" zera a sequência como um erro zeraria: a
    # sequência mede premissa de pé, e quem não sabe não a tem de pé.
    if r.nao_sei:
        seguinte = _resolve_treino(d, e, a, pendente)
        return Transicao(seguinte.estado, seguinte.tela,
                         (evento,) + seguinte.eventos)
    # A confiança do TREINO fica só no item que FECHA a sequência. Nas
    # tentativas do meio ela custa uma tela por item — 33 por sessão de
    # quem erra muito, medido — e não entra em decisão nenhuma: a
    # classificação não roda no treino (`_resolve_treino` só olha
    # certo/errado). O que a medida exige são DUAS: a confiança de quando a
    # crença foi detectada, e a de quando a premissa foi confirmada. Essas
    # duas continuam.
    en = e.no(a.no)
    fecha = bool(pendente.correta) and en.streak + 1 >= STREAK_ALVO
    if not fecha:
        seguinte = _resolve_treino(d, e, a, pendente)
        return Transicao(seguinte.estado, seguinte.tela,
                         (evento, Evento("confianca_pulada", {
                             "atividade": a.id, "no": a.no, "fase": "treino",
                             "motivo": "tentativa intermediária do treino"}))
                         + seguinte.eventos)
    seguinte = _pede_confianca(d, e, a, pendente)
    return Transicao(seguinte.estado, seguinte.tela, (evento,) + seguinte.eventos)


def _resolve_treino(d: Dominio, e: Estado, a: Atividade,
                    p: Pendente) -> Transicao:
    e = replace(e, fase=TREINO, pendente=None)
    certo = p.correta
    r = Resposta(escolha=p.escolha, confianca=p.confianca, ms=p.ms)
    en = e.no(a.no)

    # RF35: a sequência é do nó. Zerar aqui não toca em nenhum outro.
    streak = en.streak + 1 if certo else 0
    novo = e.com(a.no, streak=streak, tentativas=en.tentativas + 1,
                 tropecos=en.tropecos + (0 if certo else 1),
                 # A instância conta AQUI também, e é aqui que ela mais
                 # conta: os moldes começam pelos itens de treino, e
                 # `atividades_do_no(no, "diagnostico")` garante que item
                 # de treino nunca chega ao diagnóstico. Sem esta linha,
                 # `generalizou` era um falso constante justamente para o
                 # banco que os moldes constroem.
                 instancias=(en.instancias + _instancias_de(a) if certo
                             else en.instancias))

    eventos = [
        Evento("resposta_registrada", {
            "atividade": a.id, "no": a.no, "fase": "treino", "item": a.tipo,
            "escolha": r.escolha, "correta": certo,
            "crenca_em_jogo": a.crenca, "confianca": r.confianca, "ms": r.ms,
        }),
        Evento("treino_tentativa", {
            "no": a.no, "atividade": a.id, "formato": a.formato, "item": a.tipo,
            "correta": certo, "streak": streak, "tentativas": en.tentativas + 1,
        }),
    ]
    seguinte = _proximo_treino(d, novo, a.no)
    return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)


# --------------------------------------------------------------------------
# Fim
# --------------------------------------------------------------------------

def _item_de_reteste(d: Dominio, e: Estado, crenca: str) -> Atividade | None:
    """Um item que ofereça esta crença e que a pessoa NÃO tenha visto.

    Reperguntar o mesmo item mediria memória daquele item, não a premissa.
    Entre os que sobraram, prefere um formato que ela não viu naquele nó:
    "sobrevive à troca de superfície" é parte do critério, e repetir o
    molde da pergunta deixa de testar isso.

    `None` quando o banco acabou. Quem chamou registra a falta — fingir
    que houve reteste seria pior do que não ter um.
    """
    def usado(a: Atividade) -> bool:
        return a.id in e.no(a.no).usadas

    def oferece(a: Atividade) -> bool:
        return any(o.crenca == crenca for o in a.opcoes)

    livres = [a for a in d.atividades if oferece(a) and not usado(a)]
    if not livres:
        return None
    # A comparação que importa é com as superfícies em que ESTA crença já
    # foi oferecida a esta pessoa. Um formato que ela viu noutro nó, com
    # outra crença, não compromete a troca de superfície aqui.
    vistos = {a.formato for a in d.atividades if oferece(a) and usado(a)}
    novos = [a for a in livres if a.formato not in vistos]
    # Nem sempre sobra formato novo: com quatro itens por crença em três
    # formatos, o treino costuma gastar os que faltavam. O item sai assim
    # mesmo, e quem grava o evento diz que a superfície repetiu — reteste
    # no mesmo molde é evidência mais fraca, e a análise tem de saber.
    return (novos or livres)[0]


def _superficie_nova(d: Dominio, e: Estado, crenca: str, a: Atividade) -> bool:
    return a.formato not in {x.formato for x in d.atividades
                             if x.id in e.no(x.no).usadas and x.id != a.id
                             and any(o.crenca == crenca for o in x.opcoes)}


def _proximo_reteste(d: Dominio, e: Estado) -> Transicao:
    """A próxima crença da fila, ou o fim da unidade."""
    eventos: tuple[Evento, ...] = ()
    fila = e.a_retestar
    while fila:
        crenca, resto = fila[0], fila[1:]
        a = _item_de_reteste(d, e, crenca)
        if a is not None:
            novo = replace(e, fase=RETESTE, a_retestar=resto, alvo=a.no)
            seguinte = _apresenta(d, novo, a)
            return Transicao(seguinte.estado, seguinte.tela,
                             eventos + seguinte.eventos)
        eventos += (Evento("reteste_sem_item", {
            "crenca": crenca, "no": d.crencas[crenca].nega if crenca in d.crencas else "",
            "motivo": "nenhuma atividade por ver oferece esta crença"}),)
        fila = resto
    seguinte = _fecha(d, replace(e, a_retestar=()))
    return Transicao(seguinte.estado, seguinte.tela, eventos + seguinte.eventos)


def _resolve_reteste(d: Dominio, e: Estado, a: Atividade,
                     p: Pendente) -> Transicao:
    """O reteste OBSERVA. Não mexe no nó, não refuta de novo, não confirma.

    Uma medida que corrige o que está medindo deixa de ser medida — e
    refutar outra vez no fim nunca terminaria. Por isso aqui só saem
    eventos: nenhuma escrita em `EstadoNo`.
    """
    e = replace(e, fase=RETESTE, pendente=None)
    crenca = p.razao.crenca if p.razao else None
    alvo = next((c for c in (p.crenca_da_opcao, crenca) if c), None)
    # A crença desta pergunta é a que o item oferece e que estava em
    # reteste; `voltou` é tê-la escolhido como RAZÃO, que é onde o critério
    # olha — a resposta pode sair certa por outro caminho.
    em_jogo = next((o.crenca for o in a.opcoes
                    if o.crenca and o.crenca == crenca), None) or alvo
    eventos = (
        Evento("resposta_registrada", {
            "atividade": a.id, "no": a.no, "fase": "reteste", "item": a.tipo,
            "escolha": p.escolha, "correta": p.correta,
            "crenca_em_jogo": em_jogo, "confianca": p.confianca, "ms": p.ms,
        }),
        Evento("belief_retested", {
            "crenca": _crenca_do_reteste(d, e, a),
            "no": a.no, "atividade": a.id, "formato": a.formato,
            "item": a.tipo,
            # "Sobrevive à troca de superfície" é parte do critério. Quando
            # o banco não tinha formato novo a oferecer, isto sai falso, e
            # o reteste vale menos — dito, e não escondido.
            "superficie_nova": _superficie_nova(
                d, e, _crenca_do_reteste(d, e, a), a),
            "voltou": bool(crenca and crenca == _crenca_do_reteste(d, e, a)),
            "correta": p.correta,
            "razao_correta": bool(p.razao and p.razao.correta),
            "confianca": p.confianca,
            "nao_sei": p.nao_sei or None,
        }),
    )
    e = replace(e, retestadas=e.retestadas + (_crenca_do_reteste(d, e, a),))
    seguinte = _proximo_reteste(d, e)
    return Transicao(seguinte.estado, seguinte.tela, eventos + seguinte.eventos)


def _crenca_do_reteste(d: Dominio, e: Estado, a: Atividade) -> str:
    """Qual crença esta pergunta está reperguntando.

    É a crença refutada nesta sessão que o item oferece. Sai do estado dos
    nós, e não da fila — a fila já andou quando o episódio fecha.
    """
    refutadas = {en.crenca for en in e.nos.values() if en.crenca}
    for o in a.opcoes:
        if o.crenca in refutadas:
            return o.crenca
    return ""


def _encerra(d: Dominio, e: Estado) -> Transicao:
    """As atividades acabaram. Antes da frase do fim, o reteste.

    O critério de sucesso tem três condições, e a terceira é **não volta**
    no reteste do fim da sessão. Se alguma crença foi refutada aqui, ela
    volta uma vez antes de a unidade fechar.
    """
    if e.a_retestar:
        return _proximo_reteste(d, e)
    return _fecha(d, e)


def _fecha(d: Dominio, e: Estado) -> Transicao:
    """Não há mais evidência a coletar. Antes do mapa, a frase do fim.

    O critério do documento é "a unidade termina quando a premissa mais
    fraca está de pé". Com DUAS atividades de diagnóstico por nó nem
    sempre dá para chegar lá: uma premissa que ficou frágil nas duas não
    tem terceira superfície para oferecer. Então o encerramento registra
    onde cada uma parou e qual era a mais fraca — o critério vira dado
    conferível, em vez de afirmação.
    """
    novo = replace(e, fase=FECHAMENTO, atividade=None, alvo=None)

    # O que a unidade NÃO mediu, dito em voz alta. `desconhecido` no fim da
    # unidade não é "ainda não chegou a vez": é o banco do nó ter acabado
    # sem nenhum episódio atribuído a ele. Calar isso faz a premissa sumir
    # do dado com a mesma cara de quem nunca foi perguntado.
    nao_medidos = []
    for nid in d.ordem:
        en = novo.no(nid)
        if en.estado != DESCONHECIDO:
            continue
        novo = novo.com(nid, estado=NAO_MEDIDO)
        nao_medidos.append(Evento("no_nao_medido", {
            "no": nid,
            "itens_gastos": len(en.usadas),
            "motivo": ("os itens do nó foram gastos e toda razão errada "
                       "escolhida neles apontou outro nó"
                       if en.usadas else
                       "nenhum item deste nó chegou a ser apresentado"),
        }))

    forcas = {n: forca(novo.no(n)) for n in d.ordem}
    mais_fraca = min(d.ordem, key=lambda n: (forcas[n], d.ordem.index(n)))
    evento = Evento("unidade_encerrada", {
        "confirmados": [n for n in d.ordem if novo.no(n).estado == CONFIRMADO],
        "em_aberto": [n for n in d.ordem if novo.no(n).estado == EM_ABERTO],
        "forcas": forcas,
        "mais_fraca": mais_fraca,
        "mais_fraca_de_pe": _de_pe(novo.no(mais_fraca)),
        # Quantas crenças foram refutadas e quantas chegaram a voltar. A
        # diferença entre os dois números é o que o banco de itens não deu.
        "refutadas": len({n.crenca for n in novo.nos.values() if n.crenca}),
        "retestadas": len(set(e.retestadas)),
        "nao_medidos": [x.dados["no"] for x in nao_medidos],
    })
    # A pergunta volta SEM a frase de antes à vista: escrever olhando a
    # própria frase antiga é copiá-la ou corrigi-la, não reformulá-la. As
    # duas aparecem juntas só depois, no mapa.
    return Transicao(novo, _tela_frase(d, "fim"), tuple(nao_medidos) + (evento,))


def _generalizou(instancias: tuple[str, ...]) -> bool:
    por_molde: dict[str, set[str]] = {}
    for assinatura in instancias:
        molde, _, parametros = assinatura.partition("|")
        por_molde.setdefault(molde, set()).add(parametros)
    return any(len(p) >= 2 for p in por_molde.values())


def estado_dos_nos(d: Dominio, e: Estado) -> list[dict]:
    """O grafo com o estado de cada premissa, pronto para desenhar.

    Serve às duas telas: o mapa do fim e o painel que fica à vista DURANTE
    a unidade. O aluno vê a cadeia inteira o tempo todo e acompanha o que
    já está de pé — é o mesmo dado, desenhado em dois tamanhos.
    """
    nos = []
    for nid in d.ordem:
        en = e.no(nid)
        nos.append({
            "no": nid, "texto": d.nos[nid].simples, "estado": en.estado,
            "tipo": d.nos[nid].tipo, "suporte": list(d.nos[nid].suporte),
            "streak": en.streak, "tentativas": en.tentativas,
            # Três caminhos até o verde, e o mapa guarda qual foi: direto,
            # depois de um vacilo, ou depois de refutação e treino.
            # Sustentou a mesma ideia com a roupa trocada: duas
            # instâncias DO MESMO molde, com parâmetros distintos. Moldes
            # diferentes são perguntas diferentes, e isso o critério de
            # hoje já mede pelas duas superfícies.
            "generalizou": _generalizou(en.instancias),
            "via_treino": en.estado == CONFIRMADO and bool(en.crenca),
            "vacilou": en.vacilou,
            "crenca": en.crenca,
            # Para a tela poder dizer POR QUE este nó ficou assim sem a
            # pessoa ter respondido nada sobre ele.
            "crenca_afirma": (d.crencas[en.crenca].afirma
                              if en.crenca in d.crencas else ""),
            "origem_crenca": en.origem_crenca,
            "superficies": len(set(en.superficies)),
            "falsos_positivos": en.falsos_positivos,
            # Quão sustentada a premissa está agora. Quem lê é o painel do
            # pesquisador: é o número que responde "qual está mais fraca".
            "forca": forca(en),
        })
    return nos


def _mapa(d: Dominio, e: Estado) -> Tela:
    return Tela("mapa", texto=d.nos[d.conclusao].simples,
                dados={"nos": estado_dos_nos(d, e),
                       "frase_inicial": e.frase_inicial,
                       "frase_final": e.frase_final})
