"""O laço do MVP: identifica, refuta, treina, confirma.

    transicao = avanca(dominio, estado, resposta)

Puro: não toca disco, não sorteia, não consulta relógio. Recebe o estado e
uma entrada, devolve o estado novo, a próxima tela e os eventos a gravar.

A PEÇA QUE ESTE MVP ACRESCENTA
------------------------------
Um nó refutado NÃO vira premissa correta no primeiro acerto. Ele entra em
`em_treino` e só vira `confirmado` depois de `STREAK_ALVO` acertos seguidos,
cada um num formato diferente do anterior. Um acerto isolado logo depois da
refutação pode ser sorte, decoreba do item, ou apenas responder o oposto do
que acabou de ser contestado.

Os quatro requisitos que isso cria:

  RF33  depois da refutação o nó entra em treino, nunca direto em confirmado
  RF34  cada tentativa usa formato diferente da anterior, e nunca o mesmo item
  RF35  errar zera a sequência DAQUELE nó, sem mexer nos outros
  RF36  esgotar os itens do nó sem fechar a sequência encerra em aberto

O streak é mecanismo de PRODUTO: ele decide o que o mapa mostra ao aluno.
Ele emite `training_streak_completed` e nunca escreve em `belief_retested` —
o reteste formal da pesquisa continua sendo outra coisa, no fim da sessão.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from mvp.dominio import Atividade, Dominio

# Parâmetros do documento. Ponto de partida, não valores validados: ajustar
# no ensaio antes da coleta.
STREAK_ALVO = 2        # acertos seguidos, de formatos diferentes, para confirmar
TETO_TENTATIVAS = 4    # o dobro do streak: se não bastou, não é falta de repetição

# Estados de um nó.
DESCONHECIDO = "desconhecido"
CONFIRMADO = "confirmado"      # premissa correta e sustentada
REFUTADO = "refutado"          # crença detectada, ainda não trabalhada
EM_TREINO = "em_treino"        # a refutação passou; falta fechar a sequência
EM_ABERTO = "em_aberto"        # o banco de itens acabou antes da sequência

# Confiança declarada. Só "chutei" impede que o erro vire hipótese de crença.
CONFIANCAS = ("chutei", "acho que sei", "tenho certeza")
CHUTE = "chutei"

# Fases da unidade.
ENSINO = "ENSINO"
DIAGNOSTICO = "DIAGNOSTICO"
REFUTACAO = "REFUTACAO"
TREINO = "TREINO"
FIM = "FIM"


@dataclass(frozen=True)
class Resposta:
    """Entrada do aluno. `escolha` é a posição na tela, não o índice do YAML."""

    escolha: int | None = None
    confianca: str = ""
    ms: int = 0


@dataclass(frozen=True)
class Tela:
    """O que apresentar em seguida. A interface só desenha isto."""

    tipo: str                      # ensino | atividade | refutacao | mapa
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

    `streak` e `tentativas` são locais ao nó de propósito (RF35): domínio de
    um conceito não empresta nem tira domínio de outro.
    """

    estado: str = DESCONHECIDO
    streak: int = 0
    tentativas: int = 0
    usadas: tuple[str, ...] = ()        # atividades de treino já apresentadas
    ultimo_formato: str = ""
    crenca: str | None = None           # a hipótese que foi levantada aqui


@dataclass(frozen=True)
class Estado:
    nos: Mapping[str, EstadoNo] = field(default_factory=dict)
    fase: str = ENSINO
    cartao: int = 0                     # índice do cartão de ensino
    atividade: str | None = None        # atividade na tela
    passo: int = 0                      # passo da refutação
    plano: tuple[str, ...] = ()         # nós do percurso de refutação
    alvo: str | None = None             # nó em refutação ou em treino
    vistas: tuple[str, ...] = ()        # toda atividade já apresentada

    def no(self, nid: str) -> EstadoNo:
        return self.nos.get(nid, EstadoNo())

    def com(self, nid: str, **campos) -> "Estado":
        novo = replace(self.no(nid), **campos)
        return replace(self, nos={**self.nos, nid: novo})


@dataclass(frozen=True)
class Transicao:
    estado: Estado
    tela: Tela
    eventos: tuple[Evento, ...] = ()


# --------------------------------------------------------------------------
# Início
# --------------------------------------------------------------------------

def inicia(d: Dominio) -> Transicao:
    estado = Estado(fase=ENSINO, cartao=0)
    return Transicao(estado, _tela_ensino(d, estado),
                     (Evento("unidade_iniciada", {"topico": d.id}),))


def _cartoes(d: Dominio) -> tuple[str, ...]:
    """O ensino é o enunciado simples dos nós observáveis, um por tela.

    É material que já existe no grafo: a mesma frase que o percurso usa para
    pedir confirmação serve para apresentar a ideia antes de cobrar.
    """
    return tuple(n for n in d.ordem if d.nos[n].observavel)


def _tela_ensino(d: Dominio, e: Estado) -> Tela:
    nid = _cartoes(d)[e.cartao]
    return Tela("ensino", no=nid, texto=d.nos[nid].simples,
                dados={"indice": e.cartao + 1, "total": len(_cartoes(d))})


# --------------------------------------------------------------------------
# Avanço
# --------------------------------------------------------------------------

def avanca(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    if e.fase == ENSINO:
        return _segue_ensino(d, e)
    if e.fase == DIAGNOSTICO:
        return _responde_diagnostico(d, e, r)
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


# ------------------------------------------------------------ diagnóstico

def _proxima_diagnostica(d: Dominio, e: Estado) -> Transicao:
    """A próxima premissa ainda não resolvida, na ordem do grafo."""
    for nid in d.ordem:
        if e.no(nid).estado in (CONFIRMADO, EM_ABERTO):
            continue
        for a in d.atividades_do_no(nid, "diagnostico"):
            if a.id in e.vistas:
                continue
            return _apresenta(d, replace(e, fase=DIAGNOSTICO, alvo=nid), a)
    return _encerra(d, e)


def _apresenta(d: Dominio, e: Estado, a: Atividade) -> Transicao:
    novo = replace(e, atividade=a.id, vistas=e.vistas + (a.id,))
    tela = Tela("atividade", no=a.no, texto=a.enunciado, dados={
        "atividade": a.id, "fase": a.fase, "formato": a.formato,
        "transferencia": a.transferencia,
        "opcoes": [{"texto": o.texto} for o in a.opcoes],
        "pede_confianca": a.fase == "diagnostico",
    })
    evento = Evento("atividade_apresentada", {
        "atividade": a.id, "no": a.no, "fase": a.fase, "formato": a.formato,
        "transferencia": a.transferencia,
        "streak": e.no(a.no).streak, "tentativas": e.no(a.no).tentativas,
    })
    return Transicao(novo, tela, (evento,))


def _responde_diagnostico(d: Dominio, e: Estado, r: Resposta) -> Transicao:
    a = next(x for x in d.atividades if x.id == e.atividade)
    escolhida = a.opcoes[r.escolha] if r.escolha is not None else None
    certo = bool(escolhida and escolhida.correta)
    crenca = escolhida.crenca if escolhida else None

    eventos = [Evento("resposta_registrada", {
        "atividade": a.id, "no": a.no, "fase": "diagnostico",
        "escolha": r.escolha, "correta": certo, "crenca_escolhida": crenca,
        "confianca": r.confianca, "ms": r.ms,
    })]

    if certo:
        # Acertar no diagnóstico confirma a premissa direto: não houve crença
        # a desmontar, e treinar quem já demonstrou seria castigo.
        novo = e.com(a.no, estado=CONFIRMADO)
        eventos.append(Evento("no_confirmado", {"no": a.no, "via": "diagnostico"}))
        seguinte = _proxima_diagnostica(d, novo)
        return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)

    # Errar chutando é lacuna, não crença: o sistema ensina de novo e segue.
    if crenca is None or r.confianca == CHUTE:
        novo = e.com(a.no, estado=DESCONHECIDO)
        eventos.append(Evento("lacuna_registrada", {"no": a.no, "confianca": r.confianca}))
        seguinte = _proxima_diagnostica(d, novo)
        return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)

    # Errou sem chutar, num distrator mapeado: hipótese de crença.
    eventos.append(Evento("crenca_detectada", {
        "crenca": crenca, "no": a.no, "confianca": r.confianca}))
    novo = e.com(a.no, estado=REFUTADO, crenca=crenca)
    inicio = _inicia_refutacao(d, novo, a.no)
    return Transicao(inicio.estado, inicio.tela, tuple(eventos) + inicio.eventos)


# ------------------------------------------------------------- refutação

def _plano(d: Dominio, no: str) -> tuple[str, ...]:
    """As premissas que sustentam o nó, das observáveis até ele.

    Pós-ordem: o suporte vem antes do nó que ele sustenta, e cada nó entra
    uma vez só. É o percurso derivado do grafo — nenhuma dessas telas está
    escrita em lugar nenhum.
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
    no = d.nos[nid]
    alvo = e.alvo or nid
    crenca = d.crencas.get(e.no(alvo).crenca or "")
    ultimo = e.passo == len(e.plano) - 1
    return Tela("refutacao", no=nid, texto=no.simples, dados={
        "passo": e.passo + 1, "total": len(e.plano),
        # No último passo — o nó que a crença nega — o aluno vê lado a lado o
        # que ele afirmou e o que as premissas sustentam. É o momento da
        # contradição, e é entre coisas que ele mesmo disse.
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


# ----------------------------------------------------------------- treino

def proximo_item(d: Dominio, e: Estado, no: str) -> Atividade | None:
    """O próximo item de treino do nó, ou None se o banco acabou.

    RF34: nunca o mesmo item duas vezes, e nunca o mesmo formato da tentativa
    anterior. Um streak de dois itens de formatos diferentes é evidência mais
    forte do que quatro repetições do mesmo molde.
    """
    en = e.no(no)
    candidatas = [a for a in d.atividades_do_no(no, "treino") if a.id not in en.usadas]
    if not candidatas:
        return None
    outro_formato = [a for a in candidatas if a.formato != en.ultimo_formato]
    return (outro_formato or candidatas)[0]


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

    item = proximo_item(d, e, no)
    estourou = en.tentativas >= TETO_TENTATIVAS

    # RF36: banco esgotado ou teto atingido encerra o nó em aberto — do mesmo
    # jeito que três recusas no mesmo passo encerram o tópico. A sessão não
    # trava, e o log diz por quê.
    if item is None or estourou:
        novo = e.com(no, estado=EM_ABERTO)
        evento = Evento("no_em_aberto", {
            "no": no, "motivo": "teto de tentativas" if estourou else "banco esgotado",
            "streak": en.streak, "tentativas": en.tentativas})
        seguinte = _proxima_diagnostica(d, replace(novo, fase=DIAGNOSTICO, alvo=None))
        return Transicao(seguinte.estado, seguinte.tela, (evento,) + seguinte.eventos)

    novo = e.com(no, usadas=en.usadas + (item.id,), ultimo_formato=item.formato)
    return _apresenta(d, replace(novo, fase=TREINO, alvo=no), item)


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
            "atividade": a.id, "no": a.no, "fase": "treino",
            "escolha": r.escolha, "correta": certo,
            "crenca_escolhida": escolhida.crenca if escolhida else None,
            "confianca": r.confianca, "ms": r.ms,
        }),
        Evento("treino_tentativa", {
            "no": a.no, "atividade": a.id, "formato": a.formato,
            "transferencia": a.transferencia, "correta": certo,
            "streak": streak, "tentativas": en.tentativas + 1,
        }),
    ]
    seguinte = _proximo_treino(d, novo, a.no)
    return Transicao(seguinte.estado, seguinte.tela, tuple(eventos) + seguinte.eventos)


# -------------------------------------------------------------------- fim

def _encerra(d: Dominio, e: Estado) -> Transicao:
    novo = replace(e, fase=FIM, atividade=None, alvo=None)
    confirmados = [n for n in d.ordem if novo.no(n).estado == CONFIRMADO]
    evento = Evento("unidade_encerrada", {
        "confirmados": confirmados,
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
            "tipo": d.nos[nid].tipo,
            "suporte": list(d.nos[nid].suporte),
            "streak": en.streak, "tentativas": en.tentativas,
            # Verde direto ou verde depois de refutação: a cor é a mesma para
            # o aluno, mas o mapa guarda a diferença para o pesquisador.
            "via_treino": bool(en.crenca),
            "crenca": en.crenca,
        })
    return Tela("mapa", texto=d.nos[d.conclusao].simples, dados={"nos": nos})
