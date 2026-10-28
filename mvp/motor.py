"""O laço do MVP: identifica, confirma a suspeita, refuta, treina, confirma.

    transicao = avanca(dominio, estado, resposta)

Puro: não toca disco, não sorteia, não consulta relógio. Recebe o estado e
uma entrada, devolve o estado novo, a próxima tela e os eventos a gravar.

AS DUAS PEÇAS QUE ESTE MVP ACRESCENTA
-------------------------------------
**Um erro isolado é vacilo até prova em contrário.** Errar a pergunta
teórica com confiança não dispara a refutação: dispara a pergunta de código
do mesmo nó. Acertou ali, foi vacilo e o nó segue confirmado; errou de novo,
aí sim há hipótese de crença. Dois erros no mesmo nó, não um.

**Um acerto isolado não confirma.** Depois da refutação o nó entra em
treino e só vira premissa correta depois de `STREAK_ALVO` acertos seguidos,
em formatos diferentes. Um acerto logo depois da refutação pode ser sorte,
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
from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from mvp.dominio import Atividade, Dominio

# Parâmetros do documento. Ponto de partida, não valores validados: ajustar
# no ensaio antes da coleta.
STREAK_ALVO = 2        # acertos seguidos, de formatos diferentes, para confirmar
TETO_TENTATIVAS = 4    # o dobro do streak: se não bastou, não é falta de repetição
ERROS_PARA_CRENCA = 2  # erros no mesmo nó antes de a refutação disparar

# Quantas vezes a mesma premissa pode ser reapresentada quando o aluno diz
# que não entendeu. Depois disso o percurso segue: insistir uma quarta vez
# na mesma frase não ensina, e o treino ainda vem depois para pegar o que
# ficou. Quem não fechar lá termina o nó em aberto, que é honesto.
LIMITE_REEXPLICACAO = 2

# Estados de um nó.
DESCONHECIDO = "desconhecido"
CONFIRMADO = "confirmado"      # premissa correta e sustentada
REFUTADO = "refutado"          # crença detectada, ainda não trabalhada
EM_TREINO = "em_treino"        # a refutação passou; falta fechar a sequência
EM_ABERTO = "em_aberto"        # o banco de itens acabou antes da sequência

CONFIANCAS = ("chutei", "acho que sei", "tenho certeza")
CHUTE = "chutei"

# Fases da unidade.
ENSINO = "ENSINO"
DIAGNOSTICO = "DIAGNOSTICO"
RAZAO = "RAZAO"
CONFIANCA = "CONFIANCA"
VALIDACAO = "VALIDACAO"
REFUTACAO = "REFUTACAO"
TREINO = "TREINO"
FIM = "FIM"


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
    # Embaralha as razões sem sortear: o motor continua puro, e a mesma
    # semente devolve a mesma ordem. Quem fornece é a sessão.
    semente: str = ""

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
    estado = Estado(fase=ENSINO, cartao=0, semente=semente)
    return Transicao(estado, _tela_ensino(d, estado),
                     (Evento("unidade_iniciada", {"topico": d.id}),))


def _cartoes(d: Dominio) -> tuple[str, ...]:
    """O ensino é o enunciado simples dos nós observáveis, um por tela."""
    return tuple(n for n in d.ordem if d.nos[n].observavel)


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
    if e.fase == ENSINO:
        return _segue_ensino(d, e)
    if e.fase == DIAGNOSTICO:
        return _responde_diagnostico(d, e, r)
    if e.fase == RAZAO:
        return _responde_razao(d, e, r)
    if e.fase == CONFIANCA:
        return _responde_confianca(d, e, r)
    if e.fase == VALIDACAO:
        return _segue_validacao(d, e)
    if e.fase == REFUTACAO:
        return _segue_refutacao(d, e, repetir=r.repetir)
    if e.fase == TREINO:
        return _responde_treino(d, e, r)
    return Transicao(e, _mapa(d, e))


def _segue_ensino(d: Dominio, e: Estado) -> Transicao:
    proximo = e.cartao + 1
    if proximo < len(_cartoes(d)):
        novo = replace(e, cartao=proximo)
        return Transicao(novo, _tela_ensino(d, novo))
    return _proxima_diagnostica(d, replace(e, fase=DIAGNOSTICO))


# --------------------------------------------------------------------------
# Diagnóstico, com checagem de vacilo
# --------------------------------------------------------------------------

def _proxima_diagnostica(d: Dominio, e: Estado) -> Transicao:
    """A próxima premissa não resolvida, na ordem do grafo.

    Dentro do nó, a teórica vem antes da de código: é o par que sustenta a
    checagem de vacilo.
    """
    for nid in d.ordem:
        if e.no(nid).estado in (CONFIRMADO, EM_ABERTO):
            continue
        for a in d.atividades_do_no(nid, "diagnostico"):
            if a.id in e.no(nid).usadas:
                continue
            return _apresenta(d, replace(e, fase=DIAGNOSTICO, alvo=nid), a)
    return _encerra(d, e)


def _apresenta(d: Dominio, e: Estado, a: Atividade, *, reapresentada: bool = False) -> Transicao:
    en = e.no(a.no)
    novo = replace(e, atividade=a.id)
    novo = novo.com(a.no,
                    usadas=en.usadas if a.id in en.usadas else en.usadas + (a.id,),
                    ultimo_formato=a.formato, ultima_atividade=a.id)
    tela = Tela("atividade", no=a.no, texto=a.texto, dados={
        "atividade": a.id, "fase": e.fase, "formato": a.formato, "item": a.tipo,
        "opcoes": [{"texto": o.texto} for o in a.opcoes],
        # A confiança saiu daqui: ela é da DUPLA resposta-razão, e tem tela
        # própria depois das duas (T3).
        "pede_confianca": False,
    })
    eventos = [Evento("atividade_apresentada", {
        "atividade": a.id, "no": a.no, "fase": e.fase, "formato": a.formato,
        "item": a.tipo, "streak": en.streak, "tentativas": en.tentativas,
        "erros": en.erros,
    })]
    if reapresentada:
        eventos.append(Evento("item_reapresentado", {"atividade": a.id, "no": a.no}))
    return Transicao(novo, tela, tuple(eventos))


def razoes_de(d: Dominio, a: Atividade) -> tuple[Razao, ...]:
    """As razões de um item, montadas DO GRAFO.

    A certa é o enunciado do nó que o item mira. As erradas são as crenças
    que as alternativas apontam — e elas podem negar **outros** nós: um
    distrator do item de B1 pode ser uma crença sobre B2. Nenhuma destas
    frases está escrita num banco de razões, porque banco de razões não
    existe: se existisse, a razão e a premissa poderiam divergir.

    Ordem canônica, a correta primeiro. Quem apresenta embaralha.
    """
    saida = [Razao(texto=d.nos[a.no].simples, correta=True, no=a.no)]
    vistas: set[str] = set()
    for o in a.opcoes:
        if o.crenca and o.crenca not in vistas and o.crenca in d.crencas:
            vistas.add(o.crenca)
            c = d.crencas[o.crenca]
            saida.append(Razao(texto=c.afirma, crenca=o.crenca, no=c.nega))
    return tuple(saida)


def ordem_das_razoes(semente: str, atividade: str, n: int) -> tuple[int, ...]:
    """Permutação estável, derivada da semente. Sem sortear: o motor é puro
    e a mesma sessão redesenha a mesma tela depois de um recarregamento."""
    digest = hashlib.sha256(("%s|razoes|%s" % (semente, atividade)).encode()).digest()
    return tuple(i for _, i in sorted((digest[i % len(digest)], i) for i in range(n)))


def _responde_diagnostico(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    """Camada 1: a resposta TRANCA, e vem a pergunta do porquê.

    Trancar não é detalhe de interface: as razões erradas são enunciados de
    crenças, e lê-las antes de responder entrega a pista — pior, muda a
    resposta de quem ia acertar. Com a camada 1 fechada, o par
    resposta-razão é independente, que é o que a classificação pressupõe.
    """
    a = next(x for x in d.atividades if x.id == e.atividade)
    escolhida = a.opcoes[r.escolha] if r.escolha is not None else None
    certo = bool(escolhida and escolhida.correta)

    pendente = Pendente(
        atividade=a.id, escolha=r.escolha, correta=certo,
        crenca_da_opcao=(escolhida.crenca if escolhida else None),
        ms=r.ms, origem=DIAGNOSTICO,
    )
    evento = Evento("camada1_respondida", {
        "atividade": a.id, "no": a.no, "item": a.tipo, "origem": "diagnostico",
        "escolha": r.escolha, "correta": certo,
        "crenca_da_opcao": pendente.crenca_da_opcao, "ms": r.ms,
    })

    razoes = razoes_de(d, a)
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
    escolhida = (p.razoes[r.escolha]
                 if r.escolha is not None and 0 <= r.escolha < len(p.razoes)
                 else None)

    evento = Evento("camada2_respondida", {
        "atividade": a.id, "no": a.no, "escolha": r.escolha,
        "razao_correta": bool(escolhida and escolhida.correta),
        "crenca": escolhida.crenca if escolhida else None,
        # O nó de que a razão fala. Diferente de `no` quando a pessoa
        # explicou um item por uma crença que nega o vizinho.
        "fala_do_no": escolhida.no if escolhida else None,
        "ms": r.ms,
    })
    seguinte = _pede_confianca(d, e, a, replace(p, razao=escolhida))
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
                    "resposta": (a.opcoes[p.escolha].texto
                                 if p.escolha is not None else ""),
                    "razao": p.razao.texto if p.razao else "",
                    "escala": list(CONFIANCAS),
                })
    return Transicao(novo, tela, ())


def _responde_confianca(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    p = e.pendente
    assert p is not None, "fase CONFIANCA sem resposta trancada"
    a = next(x for x in d.atividades if x.id == p.atividade)
    p = replace(p, confianca=r.confianca)

    evento = Evento("camada3_respondida", {
        "atividade": a.id, "no": a.no, "confianca": r.confianca,
        "origem": p.origem.lower(), "ms": r.ms,
    })
    if p.origem == TREINO:
        seguinte = _resolve_treino(d, e, a, p)
    else:
        seguinte = _resolve_diagnostico(d, e, a, p)
    return Transicao(seguinte.estado, seguinte.tela, (evento,) + seguinte.eventos)


def _resolve_diagnostico(d: Dominio, e: Estado, a: Atividade,
                         p: Pendente) -> Transicao:
    """O que o episódio faz com o nó.

    Por enquanto decide só pela camada 1 — a classificação nos cinco
    estados, que usa também a razão, é a tarefa seguinte (T4). A razão já
    é coletada e registrada: o dado existe antes de o motor saber usá-lo.
    """
    # A resolução acontece sempre a partir do DIAGNÓSTICO, venha ela da
    # camada 2 ou do atalho de item sem razões: `_apresenta` não mexe na
    # fase, e a segunda pergunta do nó sairia marcada como RAZAO.
    e = replace(e, fase=DIAGNOSTICO, pendente=None)
    certo = p.correta
    r = Resposta(escolha=p.escolha, confianca=p.confianca, ms=p.ms)
    en = e.no(a.no)

    eventos = [Evento("resposta_registrada", {
        "atividade": a.id, "no": a.no, "fase": "diagnostico", "item": a.tipo,
        "escolha": r.escolha, "correta": certo,
        "crenca_em_jogo": a.crenca, "confianca": r.confianca, "ms": r.ms,
    })]

    if certo:
        # Acertar depois de um erro com confiança é VACILO, não domínio
        # frágil: a pessoa demonstrou o conceito noutro formato. Fica
        # registrado, porque o pesquisador quer saber quão direto foi o
        # caminho até o verde.
        if en.erros:
            eventos.append(Evento("vacilo_detectado", {
                "no": a.no, "crenca_suspeita": a.crenca, "atividade": a.id}))
        novo = e.com(a.no, estado=CONFIRMADO, vacilou=bool(en.erros))
        eventos.append(Evento("no_confirmado", {
            "no": a.no, "via": "vacilo" if en.erros else "diagnostico"}))
        seguinte = _proxima_diagnostica(d, novo)
        return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)

    # Errar chutando é lacuna: não refuta o que a pessoa não pensa, e não
    # conta como evidência para a hipótese de crença.
    if r.confianca == CHUTE or not a.crenca:
        eventos.append(Evento("lacuna_registrada", {"no": a.no, "confianca": r.confianca}))
        novo = e.com(a.no, estado=DESCONHECIDO)
        seguinte = _proxima_diagnostica(d, novo)
        return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)

    erros = en.erros + 1
    novo = e.com(a.no, erros=erros)
    restantes = [x for x in d.atividades_do_no(a.no, "diagnostico")
                 if x.id not in novo.no(a.no).usadas]

    # Um erro só não basta. Vem a outra pergunta do nó, de formato diferente,
    # antes de a refutação disparar.
    if erros < ERROS_PARA_CRENCA and restantes:
        eventos.append(Evento("suspeita_de_crenca", {
            "no": a.no, "crenca": a.crenca, "erros": erros,
            "confirma_com": restantes[0].id}))
        seguinte = _apresenta(d, novo, restantes[0])
        return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)

    eventos.append(Evento("crenca_detectada", {
        "crenca": a.crenca, "no": a.no, "erros": erros, "confianca": r.confianca}))
    novo = novo.com(a.no, estado=REFUTADO, crenca=a.crenca)
    inicio = _inicia_validacao(d, novo, a.no)
    return Transicao(inicio.estado, inicio.tela, tuple(eventos) + inicio.eventos)


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
    return _inicia_refutacao(d, e, e.alvo or "")


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

    # RF33: a refutação NÃO confirma o nó. Ela o põe em treino.
    alvo = e.alvo or e.plano[-1]
    novo = e.com(alvo, estado=EM_TREINO, streak=0, tentativas=0)
    novo = replace(novo, fase=TREINO, plano=(), passo=0, repeticoes=0)
    eventos = eventos + (
        Evento("refutacao_concluida", {"no": alvo}),
        Evento("treino_iniciado", {"no": alvo, "streak_alvo": STREAK_ALVO}),
    )
    seguinte = _proximo_treino(d, novo, alvo)
    return Transicao(seguinte.estado, seguinte.tela, eventos + seguinte.eventos)


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
    escolhida = a.opcoes[r.escolha] if r.escolha is not None else None
    certo = bool(escolhida and escolhida.correta)

    pendente = Pendente(
        atividade=a.id, escolha=r.escolha, correta=certo,
        crenca_da_opcao=(escolhida.crenca if escolhida else None),
        ms=r.ms, origem=TREINO,
    )
    evento = Evento("camada1_respondida", {
        "atividade": a.id, "no": a.no, "item": a.tipo, "origem": "treino",
        "escolha": r.escolha, "correta": certo,
        "crenca_da_opcao": pendente.crenca_da_opcao, "ms": r.ms,
    })
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
    novo = e.com(a.no, streak=streak, tentativas=en.tentativas + 1)

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

def _encerra(d: Dominio, e: Estado) -> Transicao:
    novo = replace(e, fase=FIM, atividade=None, alvo=None)
    evento = Evento("unidade_encerrada", {
        "confirmados": [n for n in d.ordem if novo.no(n).estado == CONFIRMADO],
        "em_aberto": [n for n in d.ordem if novo.no(n).estado == EM_ABERTO],
    })
    return Transicao(novo, _mapa(d, novo), (evento,))


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
            "via_treino": en.estado == CONFIRMADO and bool(en.crenca),
            "vacilou": en.vacilou,
            "crenca": en.crenca,
        })
    return nos


def _mapa(d: Dominio, e: Estado) -> Tela:
    return Tela("mapa", texto=d.nos[d.conclusao].simples,
                dados={"nos": estado_dos_nos(d, e)})
