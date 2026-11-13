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
# AS PROVAS QUE PODEM CHEGAR A QUEM ESTÁ NESTE TÓPICO. O nome é privado
# no motor atual, e é importado assim de propósito: o motor atual não
# muda (é restrição do plano), e a regra de exibição — só passa o
# programa cujos construtos o tópico já ensinou — não pode ter cópia.
# Duas regras de exibição divergem em silêncio; uma só não tem como.
from mvp.motor import _prova as provas_exibiveis
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
    # A crença dita na abertura, mesmo com "chutei". Se ela voltar no
    # topo da escada, é a ideia, e não chute (spec 6.6 e 6.14).
    crenca_da_abertura: str = ""
    # A crença da razão errada de quem acertou a resposta. Uma vez pode
    # ser tropeço de alternativa; a mesma duas vezes vai para a prova.
    razao_errada: str = ""
    streak: int = 0                  # certas seguidas no treino
    treinos: int = 0                 # perguntas de treino já feitas
    # Crenças que apareceram sem abrir prova. Vão para o mapa.
    apareceu: tuple[str, ...] = ()


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
    # Enquanto uma prova corre: a premissa em que a crença foi dita, e
    # por onde ela continua quando a prova é de OUTRA premissa.
    origem: str = ""
    volta: str = ""
    previu: str | None = None        # a previsão dada antes de ver a máquina

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
            "apareceu": [d.crencas[c].afirma for c in ep.apareceu
                         if c in d.crencas],
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
             escolheu: str = "", contradiz: bool = False,
             degrau: str = "", versao: int = 0) -> Transicao:
    """O retorno, que a tela mostra ABAIXO do que a pessoa acabou de fazer.

    `degrau` e `versao` viajam no passo quando o retorno é de um degrau:
    é por eles que o "continuar" sabe qual degrau repetir, e com que
    versão NÃO repetir.
    """
    tela = Tela("retorno", texto=texto, dados={
        "premissa": no, "veredito": veredito, "mostra_certa": mostra_certa,
        "premissa_texto": d.nos[no].simples, "escolheu": escolheu,
        "contradiz": contradiz, "sobre": no,
    })
    return _mostra(e, tela, Passo("retorno", premissa=no, adiante=adiante,
                                  degrau=degrau, versao=versao), eventos)


def _revisao(escadas: Mapping[str, Escada], e: Estado, no: str,
             eventos: list) -> Transicao:
    """O exemplo resolvido da premissa, para quem errou o topo da escada."""
    r = escadas[no].revisao
    e = e.com(no, telas=e.premissa(no).telas + 1)
    tela = Tela("revisao", dados={
        "premissa": no, "frases": list(r.frases), "codigo": r.codigo,
        "saida": r.saida,
    })
    return _mostra(e, tela, Passo("revisao", premissa=no,
                                  adiante="confirmacao"), eventos)


def _explicacao(d: Dominio, escadas: Mapping[str, Escada], no: str) -> dict:
    """A explicação que a pessoa abre quando quer: o texto dos degraus
    guiados, em ordem, e o código da revisão.

    Não usa o exemplo nem a ampliação do cartão antigo: aquele material
    tem outro cenário e outro nível, e foi o que motivou a escada.
    """
    escada = escadas[no]
    return {"premissa": no, "no": no, "simples": d.nos[no].simples,
            "frases": [f for g in escada.guiados for f in g.frases],
            "codigo": escada.revisao.codigo}


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
    if e.modo == "explique":
        # "Me explique antes": a premissa abre pelo primeiro degrau, e a
        # pergunta de abertura não existe. Quem é ensinado é reconferido
        # no fim, e por isso o trabalho já nasce marcado.
        return _inicia_lacuna(escadas, e, no, eventos)
    a = abertura(d, no, e.formato_da_abertura)
    e = replace(e, formato_da_abertura=a.formato)
    return _pergunta(d, e, no, a, "abertura", eventos, certeza=True)


# --------------------------------------------------------------------------
# A lacuna: subir a escada
# --------------------------------------------------------------------------

def _inicia_lacuna(escadas: Mapping[str, Escada], e: Estado, no: str,
                   eventos: list) -> Transicao:
    e = e.com(no, trabalho="lacuna")
    eventos.append(_ev("trabalho_iniciado", no=no, trabalho="lacuna"))
    return _sobe(escadas, e, no, 0, eventos, primeiro=True)


def _sobe(escadas: Mapping[str, Escada], e: Estado, no: str, i: int,
          eventos: list, primeiro: bool = False) -> Transicao:
    """O degrau `i` da escada. A subida inteira conta UMA tela."""
    g = escadas[no].degraus[i]
    return _degrau(escadas, e, no, g, _versao_livre(e.premissa(no), g),
                   "subida", eventos, conta=primeiro)


def _proxima_pergunta(d: Dominio, e: Estado, no: str) -> Atividade | None:
    """Uma questão de marcar ainda não usada nesta premissa.

    As de diagnóstico antes das de treino, e com duas razões ou mais:
    sem razão a pergunta não mede o que a trilha precisa. Entre as que
    servem, vem primeiro a de formato diferente da pergunta anterior.
    """
    ep = e.premissa(no)
    livres = [a for uso in ("diagnostico", "treino")
              for a in d.atividades_do_no(no, uso)
              if a.id not in ep.usadas and len(motor.razoes_de(d, a)) >= 2]
    return next((a for a in livres if a.formato != ep.formato_anterior),
                livres[0] if livres else None)


def _topo(d: Dominio, escadas: Mapping[str, Escada], e: Estado, no: str,
          eventos: list) -> Transicao:
    """A pergunta da premissa, depois do último degrau."""
    ep = e.premissa(no)
    # Sem pergunta respondida nesta premissa, é o topo que decide o
    # caminho — o caso do modo "explique" —, e aí ele pede a certeza.
    decide = not ep.usadas
    a = abertura(d, no, e.formato_da_abertura)
    if a.id in ep.usadas:
        a = _proxima_pergunta(d, e, no)
    elif decide:
        e = replace(e, formato_da_abertura=a.formato)
    if a is None:
        # O banco acabou antes de a premissa poder ser conferida.
        e = _fecha(e, no, EM_ABERTO, eventos)
        return _abre_proxima(d, escadas, e, eventos)
    return _pergunta(d, e, no, a, "topo", eventos, certeza=decide)


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

    # Certa pela razão certa, com ou sem certeza declarada.
    bem = episodio in (motor.CONFIRMADA, motor.FRAGIL_EP)
    # A crença que a razão marcada diz, quando diz alguma.
    crenca = razao.crenca if (razao and razao.crenca in d.crencas) else ""

    if p.papel == "abertura":
        if crenca:
            e = e.com(no, crenca_da_abertura=crenca)
        if episodio == motor.CONFIRMADA:
            completo = e.em_vigor[1] == "completo" and escadas[no].pratica
            return _retorno(d, e, no, "firme",
                            "produzir" if completo else "fecha_firme", eventos)
        if episodio == motor.FRAGIL_EP:
            return _retorno(d, e, no, "inseguro", "reforco", eventos)
        if episodio == motor.FALSO_NEGATIVO_EP:
            return _retorno(d, e, no, "escorregao", "reforco", eventos)
        if episodio == motor.FALSO_POSITIVO_EP:
            e = e.com(no, razao_errada=crenca)
            return _retorno(
                d, e, no, "razao_errada", "reforco", eventos,
                escolheu=d.crencas[crenca].afirma if crenca else "",
                contradiz=bool(crenca and d.crencas[crenca].nega == no))
        if episodio == motor.CRENCA_EP and crenca:
            return _inicia_prova(d, escadas, e, no, crenca, eventos,
                                 volta="reforco")
        # "Não sei", erro com "chutei", ou erro sem crença que se saiba.
        return _inicia_lacuna(escadas, e, no, eventos)

    if p.papel == "reforco":
        if bem:
            e = _fecha(e, no, FIRMOU, eventos)
            return _abre_proxima(d, escadas, e, eventos)
        repetiu = (episodio == motor.FALSO_POSITIVO_EP and crenca
                   and crenca == e.premissa(no).razao_errada)
        if crenca and (episodio == motor.CRENCA_EP or repetiu):
            return _inicia_prova(d, escadas, e, no, crenca, eventos,
                                 volta="lacuna")
        return _lacuna_ou_aberto(d, escadas, e, no, eventos)

    if p.papel == "topo":
        if bem:
            e = _fecha(e, no, APRENDEU, eventos)
            return _abre_proxima(d, escadas, e, eventos)
        # Duas crenças levam do topo à prova. No topo que DECIDE (modo
        # "explique"), a de sempre: errada, razão errada, com confiança.
        # No topo da lacuna, a MESMA que foi dita na abertura — ali a
        # pessoa disse "chutei", e voltar à mesma ideia depois de subir a
        # escada mostra que não era chute.
        if dados["pede_certeza"]:
            leva = episodio == motor.CRENCA_EP
        else:
            leva = crenca == e.premissa(no).crenca_da_abertura
        if crenca and leva:
            return _inicia_prova(d, escadas, e, no, crenca, eventos,
                                 volta="revisao", troca=True)
        if crenca:
            e = _registra(e, no, crenca, eventos)
        return _revisao(escadas, e, no, eventos)

    if p.papel == "confirmacao":
        if bem:
            e = _fecha(e, no, APRENDEU, eventos)
            return _abre_proxima(d, escadas, e, eventos)
        if crenca:
            e = _registra(e, no, crenca, eventos)
        return _retorno_da_pergunta(d, e, no, razao, "fecha_aberto", eventos)

    e = _fecha(e, no, EM_ABERTO, eventos)
    return _abre_proxima(d, escadas, e, eventos)


def _registra(e: Estado, no: str, crenca: str, eventos: list) -> Estado:
    """Uma crença que apareceu DENTRO de um trabalho.

    Não abre prova: ali a resposta só conta como certa pela razão certa,
    ou não. Mas a pessoa disse a crença, e isso é dado — vai para o
    registro e para o mapa.
    """
    eventos.append(_ev("crenca_registrada", no=no, crenca=crenca))
    return _anota(e, no, crenca)


def _anota(e: Estado, no: str, crenca: str) -> Estado:
    ep = e.premissa(no)
    if crenca in ep.apareceu:
        return e
    return e.com(no, apareceu=ep.apareceu + (crenca,))


def _lacuna_ou_aberto(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                      no: str, eventos: list) -> Transicao:
    """Cada premissa recebe UM trabalho. Já teve: fecha em aberto."""
    if not e.premissa(no).trabalho:
        return _inicia_lacuna(escadas, e, no, eventos)
    e = _fecha(e, no, EM_ABERTO, eventos)
    return _abre_proxima(d, escadas, e, eventos)


def _reforco(d: Dominio, escadas: Mapping[str, Escada], e: Estado, no: str,
             eventos: list) -> Transicao:
    """UMA pergunta a mais, em outro formato. Ela decide o caminho."""
    a = _proxima_pergunta(d, e, no)
    if a is None:
        e = _fecha(e, no, EM_ABERTO, eventos)
        return _abre_proxima(d, escadas, e, eventos)
    return _pergunta(d, e, no, a, "reforco", eventos, certeza=True)


def _retoma(d: Dominio, escadas: Mapping[str, Escada], e: Estado, no: str,
            volta: str, eventos: list) -> Transicao:
    """A premissa em que a crença foi dita continua de onde estava."""
    if volta == "reforco":
        return _reforco(d, escadas, e, no, eventos)
    if volta == "revisao":
        return _revisao(escadas, e, no, eventos)
    return _lacuna_ou_aberto(d, escadas, e, no, eventos)


# --------------------------------------------------------------------------
# A crença: a prova
# --------------------------------------------------------------------------

PREVISOES = {
    "nao_compila": "Este programa compila?",
    "avisa": "O compilador reclama de alguma coisa aqui?",
}


def _primeira_prova(d: Dominio, no: str) -> dict | None:
    provas = provas_exibiveis(d, no)
    return provas[0] if provas else None


def _inicia_prova(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                  origem: str, crenca: str, eventos: list, volta: str,
                  troca: bool = False) -> Transicao:
    """A prova acontece NA HORA, na premissa que a crença nega.

    Essa premissa pode não ser a da pergunta: uma alternativa do B1 pode
    dizer uma crença sobre o B2. A prova é o trabalho do B2 — ainda que a
    trilha não tivesse chegado nele, e ainda que ele já estivesse fechado
    como "já sabia" — e depois a premissa de origem continua por `volta`.

    Uma prova por premissa. Se a premissa negada já teve o seu trabalho,
    o fato é registrado e a origem segue. `troca` é a única exceção: a
    crença achada no topo da escada troca o trabalho daquela premissa de
    lacuna para crença.
    """
    alvo = d.crencas[crenca].nega
    ea = e.premissa(alvo)
    pode = not ea.trabalho or (troca and alvo == origem
                               and ea.trabalho == "lacuna")
    if not pode:
        eventos.append(_ev("prova_dispensada", no=alvo, crenca=crenca,
                           veio_de=origem))
        return _retoma(d, escadas, _anota(e, alvo, crenca), origem, volta,
                       eventos)
    if ea.resultado:
        eventos.append(_ev("premissa_reaberta", no=alvo, era=ea.resultado))
    e = e.com(alvo, trabalho="crenca", crenca=crenca, resultado="",
              streak=0, treinos=0)
    e = replace(e, origem=origem, volta=volta, previu=None)
    eventos.append(_ev("trabalho_iniciado", no=alvo, trabalho="crenca"))
    eventos.append(_ev("prova_apresentada", no=alvo, crenca=crenca,
                       veio_de=origem))

    prova = _primeira_prova(d, alvo)
    forma = ("nao_compila" if prova and prova["nao_compila"]
             else "avisa" if prova and prova["avisa"] else "")
    # Onde a prova é o que o compilador DIZ, a previsão sai de graça: a
    # pessoa se compromete antes de ver. Onde a prova é uma saída, a
    # previsão pede conteúdo escrito por crença, que ainda não existe.
    previsao = ({"pergunta": PREVISOES[forma], "opcoes": ["Sim", "Não"]}
                if forma else None)
    e = e.com(alvo, telas=e.premissa(alvo).telas + 1)
    tela = Tela("voce_disse", dados={
        "premissa": alvo, "crenca": d.crencas[crenca].afirma,
        "previsao": previsao,
        "programa": prova["programa"] if previsao else "",
    })
    return _mostra(e, tela, Passo("voce_disse", premissa=alvo), eventos)


def _responde_previsao(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                       r: Entrada) -> Transicao:
    alvo, previsao = e.passo.premissa, e.tela.dados["previsao"]
    eventos: list = []
    if previsao:
        if r.acao != "responder":
            raise EntradaInvalida("esta tela pede a previsão antes de seguir")
        i = _indice(r.escolha, len(previsao["opcoes"]), "previsão")
        e = replace(e, previu=previsao["opcoes"][i])
        eventos.append(_ev("previsao_registrada", no=alvo, previu=e.previu,
                           ms=r.ms))
    elif r.acao != "continuar":
        raise EntradaInvalida("esta tela só continua")
    return _maquina(d, escadas, e, alvo, eventos)


def _maquina(d: Dominio, escadas: Mapping[str, Escada], e: Estado, alvo: str,
             eventos: list) -> Transicao:
    """O programa e o que a máquina respondeu — no centro, e aberto.

    `tem_prova` existe para a tela não mentir: sem demonstração exibível
    ela mostra o código da revisão e NÃO diz que a máquina respondeu.
    """
    prova = _primeira_prova(d, alvo)
    e = e.com(alvo, telas=e.premissa(alvo).telas + 1)
    tela = Tela("maquina", dados={
        "premissa": alvo,
        "tem_prova": prova is not None,
        "programa": prova["programa"] if prova else escadas[alvo].revisao.codigo,
        "espera": prova["espera"] if prova else "",
        "nao_compila": bool(prova and prova["nao_compila"]),
        "avisa": prova["avisa"] if prova else "",
        "ambiente": prova["ambiente"] if prova else "",
        "afirma": prova["afirma"] if prova else "",
        "premissa_texto": d.nos[alvo].simples,
        # As premissas que sustentam esta. Na ordem do grafo a pessoa já
        # passou por elas antes de chegar aqui.
        "apoio": [{"no": s, "texto": d.nos[s].simples}
                  for s in d.nos[alvo].suporte],
        "previu": e.previu,
    })
    return _mostra(e, tela, Passo("maquina", premissa=alvo, adiante="treino"),
                   eventos)


def _treino(d: Dominio, escadas: Mapping[str, Escada], e: Estado, alvo: str,
            eventos: list) -> Transicao:
    """Os degraus de prática, até duas certas seguidas. No máximo três.

    A ordem é a primeira versão de cada degrau de prática, depois a
    segunda — e nunca um exercício que a pessoa já viu nesta sessão.
    """
    ep = e.premissa(alvo)
    if ep.streak >= TREINO_ALVO:
        return _fim_da_prova(d, escadas, e, alvo, CORRIGIU, eventos)
    pratica = escadas[alvo].pratica
    fila = [(g, k)
            for k in range(max((len(g.versoes) for g in pratica), default=0))
            for g in pratica
            if k < len(g.versoes) and (g.id, k) not in ep.mostrados]
    if ep.treinos >= TREINO_MAX or not fila:
        return _fim_da_prova(d, escadas, e, alvo, EM_ABERTO, eventos)
    g, k = fila[0]
    return _degrau(escadas, e, alvo, g, k, "treino", eventos)


def _fim_da_prova(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                  alvo: str, resultado: str, eventos: list) -> Transicao:
    e = _fecha(e, alvo, resultado, eventos)
    origem, volta = e.origem, e.volta
    e = replace(e, origem="", volta="", previu=None)
    if origem and origem != alvo:
        return _retoma(d, escadas, e, origem, volta, eventos)
    return _abre_proxima(d, escadas, e, eventos)


def _retorno_da_pergunta(d: Dominio, e: Estado, no: str, razao,
                         adiante: str, eventos: list) -> Transicao:
    """O erro numa pergunta de marcar que só confirma.

    Montado do domínio, como o motor atual faz no treino: a fala da
    crença que a razão marcada afirma, e se ela contradiz ESTA premissa
    ou outra. Sem razão marcada ("não sei"), não há ideia a nomear.
    """
    crenca = d.crencas.get(razao.crenca) if (razao and razao.crenca) else None
    return _retorno(d, e, no, "errada", adiante, eventos,
                    escolheu=crenca.afirma if crenca else "",
                    contradiz=bool(crenca and crenca.nega == no))


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
        # Marcou certo e escreveu errado: a segunda evidência não fechou,
        # e quem decide é mais uma pergunta.
        return _retorno(d, e, no, "errada", "reforco", eventos,
                        texto=c.retorno, mostra_certa=c.mostra_certa)

    if p.papel == "treino":
        ep = e.premissa(no)
        e = e.com(no, treinos=ep.treinos + 1,
                  streak=ep.streak + 1 if c.certa else 0)
        if c.certa:
            return _treino(d, escadas, e, no, eventos)
        if c.crenca:
            e = _registra(e, no, c.crenca, eventos)
        return _retorno(d, e, no, "errada", "treino", eventos,
                        texto=c.retorno, mostra_certa=c.mostra_certa)

    if p.papel == "subida":
        if c.certa:
            if p.tentativa == 1:
                e = e.com(no, degrau=e.premissa(no).degrau + 1)
            return _depois_do_degrau(d, escadas, e, no, g, eventos)
        if p.tentativa == 1:
            # Primeiro erro: o retorno daquele erro, e o MESMO degrau com
            # outros valores. A resposta certa ainda não aparece.
            return _retorno(d, e, no, "errada", "degrau_de_novo", eventos,
                            texto=c.retorno, degrau=g.id, versao=p.versao)
        # Segundo erro: mostra a certa, e a escada segue. Ninguém fica
        # preso num degrau.
        return _retorno(d, e, no, "errada", "degrau_seguinte", eventos,
                        texto=c.retorno, mostra_certa=c.mostra_certa,
                        degrau=g.id, versao=p.versao)

    raise EntradaInvalida("degrau de papel %r ainda não tem caminho" % p.papel)


def _depois_do_degrau(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
                      no: str, g: Degrau, eventos: list) -> Transicao:
    degraus = escadas[no].degraus
    i = degraus.index(g) + 1
    if i < len(degraus):
        return _sobe(escadas, e, no, i, eventos)
    return _topo(d, escadas, e, no, eventos)


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
    if adiante == "reforco":
        return _reforco(d, escadas, e, no, eventos)
    if adiante == "treino":
        return _treino(d, escadas, e, no, eventos)
    if adiante in ("degrau_de_novo", "degrau_seguinte"):
        g = next(x for x in escadas[no].degraus if x.id == e.passo.degrau)
        if adiante == "degrau_seguinte":
            return _depois_do_degrau(d, escadas, e, no, g, eventos)
        outra = _versao_livre(e.premissa(no), g, fora=e.passo.versao)
        return _degrau(escadas, e, no, g, outra, "subida", eventos,
                       tentativa=2, conta=False)
    if adiante == "confirmacao":
        a = _proxima_pergunta(d, e, no)
        if a is None:
            e = _fecha(e, no, EM_ABERTO, eventos)
            return _abre_proxima(d, escadas, e, eventos)
        return _pergunta(d, e, no, a, "confirmacao", eventos, certeza=False)
    raise EntradaInvalida("não há para onde continuar daqui")


def _a_parte(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
             r: Entrada) -> Transicao:
    """As três ações que não respondem à tela: devolvem a MESMA tela.

    `explicacao` abre a explicação da premissa por cima do que está na
    frente da pessoa. `modo` e `ritmo` trocam a escolha da entrada, e a
    troca vale a partir da premissa seguinte.
    """
    tipo = e.passo.tipo
    if r.acao == "explicacao":
        if tipo not in ("pergunta", "degrau"):
            raise EntradaInvalida("a explicação abre em pergunta e em degrau")
        no = e.passo.premissa
        e = e.com(no, abriu_explicacao=True)
        return Transicao(e, e.tela, (_ev("explicacao_aberta", no=no),),
                         _explicacao(d, escadas, no))
    if tipo in ("entrada", "mapa"):
        raise EntradaInvalida("não há o que trocar nesta tela")
    if r.acao == "modo":
        if r.modo not in MODOS:
            raise EntradaInvalida("modo desconhecido: %r" % r.modo)
        e = replace(e, modo=r.modo)
        return Transicao(e, e.tela, (_ev("modo_trocado", modo=r.modo),))
    if r.ritmo not in RITMOS:
        raise EntradaInvalida("ritmo desconhecido: %r" % r.ritmo)
    e = replace(e, ritmo=r.ritmo)
    return Transicao(e, e.tela, (_ev("ritmo_trocado", ritmo=r.ritmo),))


def avanca(d: Dominio, escadas: Mapping[str, Escada], e: Estado,
           r: Entrada) -> Transicao:
    """Uma entrada, uma transição. Entrada que não cabe levanta e nada muda."""
    if r.acao not in ACOES:
        raise EntradaInvalida("ação desconhecida: %r" % r.acao)
    if e.fim:
        raise EntradaInvalida("a trilha já terminou")
    if r.acao == "comecar":
        return _comeca(d, escadas, e, r)
    if r.acao in ("explicacao", "modo", "ritmo"):
        return _a_parte(d, escadas, e, r)

    tipo = e.passo.tipo
    if tipo == "pergunta" and r.acao in ("responder", "nao_sei"):
        return _responde_pergunta(d, escadas, e, r)
    if tipo == "degrau" and r.acao == "responder":
        return _responde_degrau(d, escadas, e, r)
    if tipo == "voce_disse" and r.acao in ("responder", "continuar"):
        return _responde_previsao(d, escadas, e, r)
    if tipo in ("retorno", "revisao", "maquina") and r.acao == "continuar":
        return _segue(d, escadas, e, [])
    raise EntradaInvalida("a ação %r não cabe na tela %r" % (r.acao, tipo))
