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

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from mvp.dominio import Atividade, Dominio

# Parâmetros do documento. Ponto de partida, não valores validados: ajustar
# no ensaio antes da coleta.
STREAK_ALVO = 2        # acertos seguidos, de formatos diferentes, para confirmar
TETO_TENTATIVAS = 4    # o dobro do streak: se não bastou, não é falta de repetição
ERROS_PARA_CRENCA = 2  # erros no mesmo nó antes de a refutação disparar

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
VALIDACAO = "VALIDACAO"
REFUTACAO = "REFUTACAO"
TREINO = "TREINO"
FIM = "FIM"


@dataclass(frozen=True)
class Resposta:
    """Entrada do aluno. `escolha` é a posição na tela."""

    escolha: int | None = None
    confianca: str = ""
    ms: int = 0


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

def inicia(d: Dominio) -> Transicao:
    estado = Estado(fase=ENSINO, cartao=0)
    return Transicao(estado, _tela_ensino(d, estado),
                     (Evento("unidade_iniciada", {"topico": d.id}),))


def _cartoes(d: Dominio) -> tuple[str, ...]:
    """O ensino é o enunciado simples dos nós observáveis, um por tela."""
    return tuple(n for n in d.ordem if d.nos[n].observavel)


def _tela_ensino(d: Dominio, e: Estado) -> Tela:
    nid = _cartoes(d)[e.cartao]
    return Tela("ensino", no=nid, texto=d.nos[nid].simples,
                dados={"indice": e.cartao + 1, "total": len(_cartoes(d))})


def avanca(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    if e.fase == ENSINO:
        return _segue_ensino(d, e)
    if e.fase == DIAGNOSTICO:
        return _responde_diagnostico(d, e, r)
    if e.fase == VALIDACAO:
        return _segue_validacao(d, e)
    if e.fase == REFUTACAO:
        return _segue_refutacao(d, e)
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
        for a in d.atividades_do_no(nid):
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
        # A confiança só é pedida no diagnóstico: é lá que ela decide se o
        # erro vira lacuna ou suspeita de crença.
        "pede_confianca": e.fase == DIAGNOSTICO,
    })
    eventos = [Evento("atividade_apresentada", {
        "atividade": a.id, "no": a.no, "fase": e.fase, "formato": a.formato,
        "item": a.tipo, "streak": en.streak, "tentativas": en.tentativas,
        "erros": en.erros,
    })]
    if reapresentada:
        eventos.append(Evento("item_reapresentado", {"atividade": a.id, "no": a.no}))
    return Transicao(novo, tela, tuple(eventos))


def _responde_diagnostico(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    a = next(x for x in d.atividades if x.id == e.atividade)
    escolhida = a.opcoes[r.escolha] if r.escolha is not None else None
    certo = bool(escolhida and escolhida.correta)
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
    restantes = [x for x in d.atividades_do_no(a.no) if x.id not in novo.no(a.no).usadas]

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
    novo = replace(e, fase=REFUTACAO, alvo=no, plano=plano, passo=0)
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
    })


def _segue_refutacao(d: Dominio, e: Estado) -> Transicao:
    proximo = e.passo + 1
    if proximo < len(e.plano):
        novo = replace(e, passo=proximo)
        return Transicao(novo, _tela_refutacao(d, novo))

    # RF33: a refutação NÃO confirma o nó. Ela o põe em treino.
    alvo = e.alvo or e.plano[-1]
    novo = e.com(alvo, estado=EM_TREINO, streak=0, tentativas=0)
    novo = replace(novo, fase=TREINO, plano=(), passo=0)
    eventos = (
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

    RF34 pede formato diferente do anterior e nenhum item repetido EM
    SEQUÊNCIA. Com duas atividades por nó — a teórica e a de código —, as
    duas já foram usadas no diagnóstico quando o treino começa; exigir item
    inédito deixaria todo nó refutado sem treino nenhum. Então o treino pode
    reapresentar um item de antes da refutação, desde que não seja o que
    acabou de aparecer e que mude de formato. A reapresentação vai para o
    log, e a análise pode descontá-la.
    """
    en = e.no(no)
    todas = [a for a in d.atividades_do_no(no) if a.id != en.ultima_atividade]
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
    a = next(x for x in d.atividades if x.id == e.atividade)
    escolhida = a.opcoes[r.escolha] if r.escolha is not None else None
    certo = bool(escolhida and escolhida.correta)
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


def _mapa(d: Dominio, e: Estado) -> Tela:
    """O mapa de premissas: o que ficou verde, e por qual caminho."""
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
    return Tela("mapa", texto=d.nos[d.conclusao].simples, dados={"nos": nos})
