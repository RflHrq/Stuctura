"""A trilha: o tópico em sequência, com o trabalho que cada premissa pede.

    transicao = inicia(dominio, escadas, semente)
    transicao = avanca(dominio, escadas, estado, entrada)

O mesmo contrato do motor atual, num motor ao lado dele: estado e entrada
entram; estado, tela e eventos saem. Puro — não toca disco, não sorteia,
não consulta relógio. O desenho inteiro está em docs/trilha.md.

O QUE MUDA EM RELAÇÃO AO MOTOR ATUAL. Lá o tópico é uma sessão só, igual
para todo mundo: cartões antes da primeira pergunta, duas respostas
certas por premissa, três telas por pergunta. Aqui as premissas vêm uma
de cada vez, na ordem do grafo; cada uma abre com UMA pergunta, numa
tela; e a resposta decide o caminho.

    firme     certa, pela razão certa, com certeza: segue
    reforço   certa sem certeza, escorregão, ou razão errada: mais uma
    lacuna    não sabe: sobe a escada da premissa, do primeiro degrau
    crença    errada pela razão errada, com confiança: a prova da máquina

A classificação não é daqui: é `motor.classifica`, sem mudança. O que é
daqui é o que se faz com ela.

O QUE CONTA COMO TELA. A spec fixa um teto de oito telas por premissa, e
a conta é esta: cada pergunta, cada degrau de produzir ou de treino, as
duas telas da prova e a revisão contam uma; a subida inteira da escada
conta uma; o retorno não conta, porque aparece na tela em que a pessoa
já está; a reconferência do fim é contada à parte.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from mvp import motor
from mvp.dominio import Atividade, Dominio
from mvp.motor import Evento, Tela
from mvp.trilha_escada import Degrau, Escada, corrige, ordem_das_pecas

MODOS = ("direto", "explique")
RITMOS = ("completo", "rapido")
RITMO_PADRAO = "completo"

# Como uma premissa termina. É o que o mapa mostra.
JA_SABIA = "ja_sabia"            # uma resposta firme, sem abrir a explicação
FIRMOU = "firmou"                # estava inseguro, e confirmou
APRENDEU = "aprendeu_agora"      # foi ensinado, e acertou a pergunta seguinte
CORRIGIU = "corrigiu"            # viu a prova, e fechou o treino
EM_ABERTO = "em_aberto"          # o trabalho não fechou dentro do teto
RESULTADOS = (JA_SABIA, FIRMOU, APRENDEU, CORRIGIU, EM_ABERTO)

# Como a reconferência do fim termina.
ASSIMILOU = "assimilou"
NAO_SE_MANTEVE = "nao_se_manteve"
A_IDEIA_VOLTOU = "a_ideia_voltou"
SEM_QUESTAO = "sem_questao"

TETO_TELAS = 8
TREINO_ALVO = 2                  # certas seguidas para fechar o treino
TREINO_MAX = 3                   # perguntas de treino, no máximo

ACOES = ("comecar", "responder", "nao_sei", "continuar", "explicacao",
         "modo", "ritmo")


class EntradaInvalida(ValueError):
    """A entrada não cabe na tela que está na frente da pessoa.

    Não é resposta errada: é pedido que não faz sentido agora — a segunda
    resposta de um duplo clique, um índice que não existe. Nada é gravado
    e o estado não anda.
    """


@dataclass(frozen=True)
class Entrada:
    """O que a pessoa fez. Índices são posições NA TELA."""

    acao: str = "responder"
    escolha: int | None = None
    razao: int | None = None
    confianca: str = ""
    pecas: tuple[int, ...] = ()
    texto: str = ""
    modo: str = ""
    ritmo: str = ""
    ms: int = 0


@dataclass(frozen=True)
class EstadoPremissa:
    resultado: str = ""              # vazio enquanto a premissa está aberta
    telas: int = 0
    trabalho: str = ""               # "", "lacuna" ou "crenca"
    degrau: int = 0                  # degraus certos na primeira tentativa
    reconferencia: str = ""
    abriu_explicacao: bool = False
    crenca: str = ""                 # a crença trabalhada nesta premissa
    usadas: tuple[str, ...] = ()     # questões de marcar já mostradas
    mostrados: tuple[tuple[str, int], ...] = ()   # (degrau, versão) já vistos
    formato_anterior: str = ""       # o da última pergunta de marcar


@dataclass(frozen=True)
class Passo:
    """O que está na tela, do jeito que o motor precisa para ler a resposta."""

    tipo: str = "entrada"
    premissa: str = ""
    papel: str = ""
    atividade: str = ""
    degrau: str = ""
    versao: int = 0
    tentativa: int = 1
    adiante: str = ""                # para onde o "continuar" leva


@dataclass(frozen=True)
class Estado:
    semente: str = ""
    modo: str = ""                   # a escolha da pessoa, que ela pode trocar
    ritmo: str = RITMO_PADRAO
    # O modo e o ritmo EM VIGOR na premissa aberta. A troca vale a partir
    # da premissa seguinte: quem está no meio de uma pergunta não pode
    # tê-la trocada debaixo de si.
    em_vigor: tuple[str, str] = ("", RITMO_PADRAO)
    atual: str = ""                  # a premissa da sequência
    formato_da_abertura: str = ""    # o da abertura da premissa anterior
    premissas: Mapping[str, EstadoPremissa] = field(default_factory=dict)
    passo: Passo = Passo()
    tela: Tela | None = None
    fim: bool = False

    def premissa(self, no: str) -> EstadoPremissa:
        return self.premissas.get(no, EstadoPremissa())

    def com(self, no: str, **campos) -> "Estado":
        return replace(self, premissas={
            **self.premissas, no: replace(self.premissa(no), **campos)})


@dataclass(frozen=True)
class Transicao:
    estado: Estado
    tela: Tela
    eventos: tuple[Evento, ...] = ()
    explicacao: dict | None = None


# --------------------------------------------------------------------------
# Peças pequenas
# --------------------------------------------------------------------------

def _ev(tipo: str, **dados) -> Evento:
    return Evento(tipo, dados)


def _indice(valor: Any, quantas: int, onde: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise EntradaInvalida("%s: %r não é uma posição da tela" % (onde, valor))
    if not 0 <= valor < quantas:
        raise EntradaInvalida("%s: a posição %d não existe (são %d)"
                              % (onde, valor, quantas))
    return valor


def _atividade(d: Dominio, aid: str) -> Atividade:
    return next(a for a in d.atividades if a.id == aid)


def _razoes_na_tela(d: Dominio, semente: str, a: Atividade) -> tuple:
    brutas = motor.razoes_de(d, a)
    ordem = motor.ordem_das_razoes(semente, a.id, len(brutas))
    return tuple(brutas[i] for i in ordem)


def _mostra(e: Estado, tela: Tela, passo: Passo, eventos,
            explicacao: dict | None = None) -> Transicao:
    return Transicao(replace(e, tela=tela, passo=passo), tela,
                     tuple(eventos), explicacao)


def abertura(d: Dominio, no: str, evita_formato: str = "") -> Atividade:
    """A pergunta que abre a premissa: a de código, de degrau 2.

    Uma resposta só pode fechar a premissa, e por isso ela tem de ser de
    APLICAR a ideia, não de reconhecer a definição. E precisa de duas
    razões ou mais: é a razão marcada que diz qual é a crença.

    `evita_formato` é o formato da abertura da premissa anterior — duas
    premissas vizinhas não abrem do mesmo jeito, quando há escolha.
    """
    serve = [a for a in d.atividades_do_no(no, "diagnostico")
             if len(motor.razoes_de(d, a)) >= 2]
    de_codigo = [a for a in serve if a.nivel == 2] or serve
    if not de_codigo:
        raise ValueError("a premissa %s não tem pergunta de abertura" % no)
    return next((a for a in de_codigo if a.formato != evita_formato),
                de_codigo[0])


def resumo(d: Dominio, escadas: Mapping[str, Escada], e: Estado) -> list[dict]:
    """O estado de cada premissa, para o mapa e para a barra de progresso."""
    saida = []
    for no in d.ordem:
        ep, escada = e.premissa(no), escadas[no]
        total = len(escada.degraus)
        saida.append({
            "no": no,
            "texto": d.nos[no].simples,
            "resultado": ep.resultado,
            "trabalho": ep.trabalho,
            # Quem fechou pelo topo não subiu degrau nenhum, e não foi por
            # falta: a medida dele é a escada inteira.
            "degrau": total if ep.resultado in (JA_SABIA, FIRMOU) else ep.degrau,
            "degraus": total,
            "reconferencia": ep.reconferencia,
            "telas": ep.telas,
            "crenca": (d.crencas[ep.crenca].afirma
                       if ep.crenca in d.crencas else ""),
            "frases": [f for g in escada.guiados for f in g.frases],
            "codigo": escada.revisao.codigo,
        })
    return saida


# --------------------------------------------------------------------------
# As telas
# --------------------------------------------------------------------------

def _pergunta(d: Dominio, e: Estado, no: str, a: Atividade, papel: str,
              eventos: list, certeza: bool) -> Transicao:
    ep = e.premissa(no)
    conta = 0 if papel == "reconferencia" else 1
    e = e.com(no, telas=ep.telas + conta, usadas=ep.usadas + (a.id,),
              formato_anterior=a.formato)
    razoes = _razoes_na_tela(d, e.semente, a)
    tela = Tela("pergunta", texto=a.enunciado, dados={
        "premissa": no, "papel": papel, "atividade": a.id,
        "codigo": a.codigo, "formato": a.formato,
        "opcoes": [{"texto": o.texto}
                   for o in motor.opcoes_na_tela(e.semente, a)],
        "razoes": [{"texto": z.texto} for z in razoes],
        "escala": list(motor.CONFIANCAS) if certeza else [],
        "pede_razao": len(razoes) >= 2,
        "pede_certeza": certeza,
    })
    return _mostra(e, tela, Passo("pergunta", premissa=no, papel=papel,
                                  atividade=a.id), eventos)


def _degrau(escadas: Mapping[str, Escada], e: Estado, no: str, g: Degrau,
            versao: int, papel: str, eventos: list,
            tentativa: int = 1, conta: bool = True) -> Transicao:
    escada, v = escadas[no], g.versoes[versao]
    ordem = ordem_das_pecas(e.semente, g.id, versao, g.forma, len(v.pecas))
    ep = e.premissa(no)
    soma = 1 if (conta and papel in ("produzir", "treino", "subida")) else 0
    e = e.com(no, telas=ep.telas + soma,
              mostrados=ep.mostrados + ((g.id, versao),))
    tela = Tela("degrau", dados={
        "premissa": no, "papel": papel, "degrau": g.id,
        "indice": escada.degraus.index(g) + 1, "total": len(escada.degraus),
        "guiado": g.guiado,
        "frases": list(g.frases) if papel == "subida" else [],
        "forma": g.forma, "pede": v.pede, "mostra": v.mostra,
        "antes": v.antes, "pecas": [v.pecas[i] for i in ordem],
        "tentativa": tentativa,
    })
    return _mostra(e, tela, Passo("degrau", premissa=no, papel=papel,
                                  degrau=g.id, versao=versao,
                                  tentativa=tentativa), eventos)


def _retorno(d: Dominio, e: Estado, no: str, veredito: str, adiante: str,
             eventos: list, texto: str = "", mostra_certa: str = "",
             escolheu: str = "", contradiz: bool = False) -> Transicao:
    """O retorno, que a tela mostra ABAIXO do que a pessoa acabou de fazer."""
    tela = Tela("retorno", texto=texto, dados={
        "premissa": no, "veredito": veredito, "mostra_certa": mostra_certa,
        "premissa_texto": d.nos[no].simples, "escolheu": escolheu,
        "contradiz": contradiz, "sobre": no,
    })
    return _mostra(e, tela, Passo("retorno", premissa=no, adiante=adiante),
                   eventos)


def _versao_livre(ep: EstadoPremissa, g: Degrau, fora: int = -1) -> int:
    """A primeira versão do degrau ainda não mostrada nesta sessão.

    Esgotadas, volta a primeira diferente de `fora` — o que não pode é
    repetir a que a pessoa acabou de ver.
    """
    for k in range(len(g.versoes)):
        if (g.id, k) not in ep.mostrados and k != fora:
            return k
    return next((k for k in range(len(g.versoes)) if k != fora), 0)


# --------------------------------------------------------------------------
# Início, sequência e fim
# --------------------------------------------------------------------------

def inicia(d: Dominio, escadas: Mapping[str, Escada],
           semente: str = "") -> Transicao:
    tela = Tela("entrada", dados={
        "titulo": d.titulo, "premissas": len(d.ordem),
        "modos": list(MODOS), "ritmos": list(RITMOS),
        "ritmo_padrao": RITMO_PADRAO,
    })
    return _mostra(Estado(semente=semente), tela, Passo("entrada"),
                   [_ev("trilha_iniciada", topico=d.id,
                        premissas=len(d.ordem))])


def _comeca(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
            r: Entrada) -> Transicao:
    if e.passo.tipo != "entrada":
        raise EntradaInvalida("a trilha já começou")
    if r.modo not in MODOS:
        raise EntradaInvalida("modo desconhecido: %r" % r.modo)
    ritmo = r.ritmo or RITMO_PADRAO
    if ritmo not in RITMOS:
        raise EntradaInvalida("ritmo desconhecido: %r" % r.ritmo)
    e = replace(e, modo=r.modo, ritmo=ritmo)
    return _abre_proxima(d, escadas, e,
                         [_ev("trilha_comecada", modo=r.modo, ritmo=ritmo)])


def _abre_proxima(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                  eventos: list) -> Transicao:
    """A próxima premissa ainda sem resultado, na ordem do grafo."""
    for no in d.ordem:
        if not e.premissa(no).resultado:
            return _abre(d, escadas, e, no, eventos)
    return _mapa(d, escadas, e, eventos)


def _abre(d: Dominio, escadas: Mapping[str, Escada], e: Estado, no: str,
          eventos: list) -> Transicao:
    e = replace(e, atual=no, em_vigor=(e.modo, e.ritmo))
    eventos.append(_ev("premissa_aberta", no=no, modo=e.modo, ritmo=e.ritmo))
    a = abertura(d, no, e.formato_da_abertura)
    e = replace(e, formato_da_abertura=a.formato)
    return _pergunta(d, e, no, a, "abertura", eventos, certeza=True)


def _fecha(e: Estado, no: str, resultado: str, eventos: list) -> Estado:
    e = e.com(no, resultado=resultado)
    eventos.append(_ev("premissa_fechada", no=no, resultado=resultado,
                       telas=e.premissa(no).telas))
    return e


def _firme(e: Estado, no: str) -> str:
    """Quem abriu a explicação antes de responder não "já sabia"."""
    return APRENDEU if e.premissa(no).abriu_explicacao else JA_SABIA


def _mapa(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
          eventos: list) -> Transicao:
    premissas = resumo(d, escadas, e)
    eventos.append(_ev("trilha_encerrada", resultados={
        p["no"]: p["resultado"] for p in premissas}))
    tela = Tela("mapa", dados={"premissas": premissas})
    return _mostra(replace(e, fim=True), tela, Passo("mapa"), eventos)


# --------------------------------------------------------------------------
# As respostas
# --------------------------------------------------------------------------

def _responde_pergunta(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                       r: Entrada) -> Transicao:
    p, dados = e.passo, e.tela.dados
    no, a = p.premissa, _atividade(d, p.atividade)
    escolha = razao_i = None
    razao = None
    certa = False
    if r.acao == "nao_sei":
        episodio = motor.LACUNA_EP
    else:
        opcoes = motor.opcoes_na_tela(e.semente, a)
        escolha = _indice(r.escolha, len(opcoes), "alternativa")
        if dados["pede_razao"]:
            razoes = _razoes_na_tela(d, e.semente, a)
            razao_i = _indice(r.razao, len(razoes), "razão")
            razao = razoes[razao_i]
        if dados["pede_certeza"] and r.confianca not in motor.CONFIANCAS:
            raise EntradaInvalida("certeza fora da escala: %r" % r.confianca)
        certa = opcoes[escolha].correta
        if not dados["pede_razao"]:
            # Questão sem camada de razão: a resposta responde sozinha.
            razao = motor.Razao(texto="", correta=certa, no=no)
        episodio = motor.classifica(
            certa, razao, r.confianca if dados["pede_certeza"] else "")

    eventos = [
        _ev("resposta_registrada", no=no, atividade=a.id, papel=p.papel,
            escolha=escolha, razao=razao_i, correta=certa,
            razao_correta=bool(razao and razao.correta),
            crenca=(razao.crenca if razao else None),
            confianca=r.confianca if dados["pede_certeza"] else "",
            nao_sei=r.acao == "nao_sei", ms=r.ms),
        _ev("episodio_classificado", no=no, estado=episodio,
            atividade=a.id, papel=p.papel),
    ]

    if p.papel == "abertura" and episodio == motor.CONFIRMADA:
        completo = e.em_vigor[1] == "completo" and escadas[no].pratica
        return _retorno(d, e, no, "firme",
                        "produzir" if completo else "fecha_firme", eventos)

    e = _fecha(e, no, EM_ABERTO, eventos)
    return _abre_proxima(d, escadas, e, eventos)


def _responde_degrau(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                     r: Entrada) -> Transicao:
    p = e.passo
    no = p.premissa
    g = next(x for x in escadas[no].degraus if x.id == p.degrau)
    v = g.versoes[p.versao]
    if g.forma == "digitar":
        if not (r.texto or "").strip():
            raise EntradaInvalida("resposta vazia")
        c = corrige(v, g.forma, texto=r.texto)
    else:
        ordem = ordem_das_pecas(e.semente, g.id, p.versao, g.forma,
                                len(v.pecas))
        c = corrige(v, g.forma, pecas=tuple(
            ordem[_indice(i, len(ordem), "peça")] for i in r.pecas))

    eventos = [_ev("degrau_respondido", no=no, degrau=g.id, versao=p.versao,
                   papel=p.papel, certa=c.certa, tentativa=p.tentativa,
                   ms=r.ms)]

    if p.papel == "produzir":
        if c.certa:
            e = _fecha(e, no, _firme(e, no), eventos)
            return _abre_proxima(d, escadas, e, eventos)
        return _retorno(d, e, no, "errada", "fecha_aberto", eventos,
                        texto=c.retorno, mostra_certa=c.mostra_certa)

    raise EntradaInvalida("degrau de papel %r ainda não tem caminho" % p.papel)


def _segue(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
           eventos: list) -> Transicao:
    """O "continuar": para onde a tela que a pessoa acabou de ler leva."""
    no, adiante = e.passo.premissa, e.passo.adiante
    if adiante == "fecha_firme":
        e = _fecha(e, no, _firme(e, no), eventos)
        return _abre_proxima(d, escadas, e, eventos)
    if adiante == "fecha_aberto":
        e = _fecha(e, no, EM_ABERTO, eventos)
        return _abre_proxima(d, escadas, e, eventos)
    if adiante == "produzir":
        g = escadas[no].pratica[-1]
        return _degrau(escadas, e, no, g, _versao_livre(e.premissa(no), g),
                       "produzir", eventos)
    raise EntradaInvalida("não há para onde continuar daqui")


def avanca(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
           r: Entrada) -> Transicao:
    """Uma entrada, uma transição. Entrada que não cabe levanta e nada muda."""
    if r.acao not in ACOES:
        raise EntradaInvalida("ação desconhecida: %r" % r.acao)
    if e.fim:
        raise EntradaInvalida("a trilha já terminou")
    if r.acao == "comecar":
        return _comeca(d, escadas, e, r)

    tipo = e.passo.tipo
    if tipo == "pergunta" and r.acao in ("responder", "nao_sei"):
        return _responde_pergunta(d, escadas, e, r)
    if tipo == "degrau" and r.acao == "responder":
        return _responde_degrau(d, escadas, e, r)
    if tipo == "retorno" and r.acao == "continuar":
        return _segue(d, escadas, e, [])
    raise EntradaInvalida("a ação %r não cabe na tela %r" % (r.acao, tipo))
