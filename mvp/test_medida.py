"""Onde a unidade mede, e o que ela admite não ter medido.

Ciclo 3. Três garantias, e as três vêm de uma medição, não de uma suspeita:
o caminhante atravessou 30 sessões do kc_02 e mostrou (a) premissas
terminando sem medida nenhuma, e (b) um terço das telas pedindo confiança
onde ela não entra em decisão.

O CARDÁPIO DE RAZÕES
--------------------
A crença de um nó já sustentado sai da cédula. O rastro que obrigou a isso:

    nó B2 — os três itens dele apresentados
    razão escolhida em 004 -> crença de I1
    razão escolhida em 005 -> crença de B3
    razão escolhida em 006 -> crença de I1   (I1 já confirmado)
    estado final de B2: desconhecido

A crença do próprio B2 estava na cédula nas três vezes. Oferecer para
sempre uma ideia que a unidade já tratou gasta os itens do nó hospedeiro
sem nunca medi-lo — e quem checa se ela voltou é o reteste.

O QUE NÃO FOI MEDIDO
--------------------
`desconhecido` no fim não é "ainda não chegou a vez": é o banco do nó ter
acabado sem nenhum episódio atribuído a ele. Calar isso faz a premissa
sumir do dado com a cara de quem nunca foi perguntado.

A CONFIANÇA
-----------
Fica onde ela decide alguma coisa: no diagnóstico, no reteste e no item que
FECHA a sequência do treino. As tentativas do meio custavam uma tela cada
— 33 por sessão de quem erra muito — e a classificação não roda no treino.
"""

from __future__ import annotations

import pytest

import pathlib
import re

from mvp import motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta
from mvp.test_motor import _politica, roda

D = carrega()
D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d():
    return D


@pytest.fixture(scope="module")
def d2():
    return D2


def _pior_caso(d):
    """Erra sempre, e explica SEMPRE pela crença de OUTRO nó quando ela
    está na cédula. É o pior caso para o nó hospedeiro, e é o que produz,
    de forma determinística, a premissa que a unidade não mede.

    Sem isto os testes abaixo passam no vazio: a sabotagem mostrou que
    apagar a marcação do `nao_medido` não derrubava nada, porque nenhuma
    das sessões normais deixava um nó sem estado.
    """
    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="x")
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            a = next(x for x in d.atividades
                     if x.id == estado.pendente.atividade)
            fora = [i for i, z in enumerate(razoes)
                    if z.crenca and z.no != a.no]
            if fora:
                return Resposta(escolha=fora[0])
            qualquer = [i for i, z in enumerate(razoes) if z.crenca]
            return Resposta(escolha=qualquer[0] if qualquer else 0)
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        return Resposta(escolha=next(i for i, o in enumerate(a.opcoes)
                                     if not o.correta))
    return politica


def _dos(eventos, tipo):
    return [e for e in eventos if e.tipo == tipo]


# --------------------------------------------------------------------------
# O cardápio de razões
# --------------------------------------------------------------------------

def test_a_crenca_de_um_no_sustentado_sai_do_cardapio(d2):
    """A regra, no item que a mediu."""
    a = next(x for x in d2.atividades if x.id == "ciu_kc02_004")   # nó B2
    aberto = {z.crenca for z in motor.razoes_de(d2, a)}
    assert "pointer_and_target_are_one" in aberto

    e = motor.Estado().com("I1", estado=motor.CONFIRMADO)
    fechado = {z.crenca for z in motor.razoes_de(d2, a, e)}
    assert "pointer_and_target_are_one" not in fechado
    # e a crença do PRÓPRIO nó continua lá: é ela que faltava ser escolhida
    assert "pointer_has_no_address" in fechado


def test_so_o_no_confirmado_tira_a_crenca_do_cardapio(d2):
    """Frágil e falso positivo NÃO tiram: a premissa não está de pé, e a
    ideia que a nega continua sendo uma explicação possível."""
    a = next(x for x in d2.atividades if x.id == "ciu_kc02_004")
    for estado in (motor.FRAGIL, motor.FALSO_POSITIVO, motor.REFUTADO,
                   motor.EM_TREINO):
        e = motor.Estado().com("I1", estado=estado)
        oferecidas = {z.crenca for z in motor.razoes_de(d2, a, e)}
        assert "pointer_and_target_are_one" in oferecidas, estado


def test_o_cardapio_nunca_cai_para_uma_razao_so(d):
    """Com uma razão só a camada 2 vira teatro — e é a camada 2 que
    diagnostica. Quando filtrar deixaria a cédula com uma opção, ela volta
    inteira: em `ciu_kc00_001` os dois distratores apontam a MESMA crença.
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_001")
    e = motor.Estado().com("B2", estado=motor.CONFIRMADO)
    razoes = motor.razoes_de(d, a, e)
    assert len(razoes) >= 2
    assert "no_value_no_memory" in {z.crenca for z in razoes}


def test_sem_estado_o_cardapio_e_o_de_sempre(d2):
    """`razoes_de(d, a)` sem estado continua pura e igual ao que era: a
    reexecução do log e os testes antigos dependem disso."""
    for a in d2.atividades:
        assert motor.razoes_de(d2, a) == motor.razoes_de(d2, a, None)


# --------------------------------------------------------------------------
# O que a unidade não mediu
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
@pytest.mark.parametrize("erra_no", ["B1", "B2", "B3", "pior_caso"])
def test_nenhuma_premissa_termina_como_desconhecida(topico, erra_no):
    """A garantia que a CS-10 queria e não tinha: no fim, toda premissa tem
    um estado — nem que o estado seja "não medida"."""
    dd = carrega(topico=topico)
    pol = (_pior_caso(dd) if erra_no == "pior_caso"
           else _politica(erra_no=erra_no, erra_diagnostico=99, d=dd))
    t, _ = roda(dd, pol)
    restam = [n for n in dd.ordem
              if t.estado.no(n).estado == motor.DESCONHECIDO]
    assert restam == [], restam


# O PIOR CASO DEIXOU DE PRODUZIR NÓ SEM MEDIDA, e é de propósito.
#
# Este teste rodava a sessão inteira com `_pior_caso` e cobrava o motivo do
# `nao_medido` que aquela política produzia. O quarto teto tirou a crença
# do nó já fechado da cédula — a mesma regra que o C1 aplicou ao nó
# confirmado —, e com isso a razão errada volta a cair no nó hospedeiro:
# no pior caso roteirizado, os cinco tópicos fecham TODOS os nós como
# `em_aberto`, que é medida, em vez de deixar algum sem medida.
#
# A asserção de mordida do ciclo 3 avisou isso, que é o trabalho dela.
#
# A propriedade que vale a pena guardar nunca foi "o pior caso esfomeia um
# nó" — é "quando um nó fica sem medida, o fechamento o marca e diz por
# quê". Essa é do FECHAMENTO, e é onde ela passa a ser testada, com os dois
# motivos montados à mão. O `nao_medido` fica sendo a rede de segurança que
# sempre foi: existe para o caso que o laço não alcançou, inclusive um
# banco mal formado que nenhuma política de sessão produz de propósito.

@pytest.mark.parametrize("topico", topicos())
def test_o_fechamento_marca_e_explica_a_premissa_sem_medida(topico):
    """Os dois motivos, nos dois estados que os distinguem.

    `itens_gastos` é o que separa um do outro: nó com itens usados e sem
    atribuição é starvation; nó sem item usado nem chegou a ser
    perguntado. Chamar errado faria o dado mentir sobre a causa.
    """
    dd = carrega(topico=topico)
    primeiro, segundo = dd.ordem[0], dd.ordem[1]
    a = dd.atividades_do_no(primeiro, "diagnostico")[0]

    # os outros nós fechados, para o fechamento ter só estes dois a marcar
    e = motor.Estado()
    for nid in dd.ordem[2:]:
        e = e.com(nid, estado=motor.EM_ABERTO)
    # primeiro: gastou item e não recebeu atribuição
    e = e.com(primeiro, usadas=(a.id,))
    # segundo: nenhum item apresentado
    assert e.no(primeiro).estado == motor.DESCONHECIDO
    assert e.no(segundo).estado == motor.DESCONHECIDO

    t = motor._fecha(dd, e)
    avisos = {x.dados["no"]: x.dados for x in t.eventos
              if x.tipo == "no_nao_medido"}

    assert sorted(avisos) == sorted([primeiro, segundo]), sorted(avisos)
    assert t.estado.no(primeiro).estado == motor.NAO_MEDIDO
    assert t.estado.no(segundo).estado == motor.NAO_MEDIDO

    assert avisos[primeiro]["itens_gastos"] == 1
    assert "gastos" in avisos[primeiro]["motivo"]
    assert avisos[segundo]["itens_gastos"] == 0
    assert "chegou a ser apresentado" in avisos[segundo]["motivo"]

    fim = [x for x in t.eventos if x.tipo == "unidade_encerrada"][-1]
    assert sorted(fim.dados["nao_medidos"]) == sorted([primeiro, segundo])


@pytest.mark.parametrize("topico", topicos())
def test_no_pior_caso_nenhuma_premissa_fica_sem_medida(topico):
    """O que o quarto teto comprou, cobrado como garantia.

    Era 1 ou mais nós sem medida por sessão de pior caso; passou a ser
    zero, com todos em `em_aberto`. Se alguém desfizer o teto, este teste
    é o que cai.
    """
    dd = carrega(topico=topico)
    t, _ = roda(dd, _pior_caso(dd))
    sem = [n for n in dd.ordem
           if t.estado.no(n).estado == motor.NAO_MEDIDO]
    assert sem == [], sem
    assert all(t.estado.no(n).estado == motor.EM_ABERTO for n in dd.ordem),         {n: t.estado.no(n).estado for n in dd.ordem}


def test_o_mapa_mostra_a_premissa_nao_medida(d2):
    """Quem responde tem de ver que aquela premissa ficou sem resposta, em
    vez de vê-la cinza igual às que nem começaram."""
    t, _ = roda(d2, _pior_caso(d2))
    estados = {n["no"]: n["estado"] for n in motor.estado_dos_nos(d2, t.estado)}
    assert motor.DESCONHECIDO not in estados.values()


# --------------------------------------------------------------------------
# A confiança
# --------------------------------------------------------------------------

def _treino(d):
    """Uma sessão com refutação e treino de verdade."""
    return roda(d, _politica(erra_no="B3", erra_diagnostico=2, d=d))


def test_a_confianca_do_treino_so_aparece_no_item_que_fecha(d):
    """Uma por sequência fechada, não uma por tentativa."""
    _, eventos = _treino(d)
    tentativas = _dos(eventos, "treino_tentativa")
    perguntas = [e for e in _dos(eventos, "camada3_respondida")
                 if e.dados.get("origem") == motor.TREINO.lower()]
    fechadas = _dos(eventos, "training_streak_completed")
    assert tentativas, "a sessão não treinou nada; o teste não morde"
    assert len(perguntas) == len(fechadas)
    assert len(perguntas) < len(tentativas)


def test_a_tentativa_do_meio_registra_que_pulou(d):
    """Pular em silêncio seria pior: quem lê o log precisa distinguir
    "não perguntei" de "perguntei e a pessoa não respondeu"."""
    _, eventos = _treino(d)
    pulos = _dos(eventos, "confianca_pulada")
    assert pulos
    for e in pulos:
        assert e.dados["fase"] == "treino"
        assert e.dados["motivo"]


def test_a_confianca_continua_em_toda_atividade_de_diagnostico(d):
    """O corte é só no treino. No diagnóstico a confiança É a camada 3, e
    `classifica` não roda sem ela."""
    _, eventos = _treino(d)
    itens = [e for e in _dos(eventos, "atividade_apresentada")
             if e.dados["fase"] == motor.DIAGNOSTICO]
    perguntas = [e for e in _dos(eventos, "camada3_respondida")
                 if e.dados.get("origem") == "diagnostico"]
    assert len(perguntas) == len(itens)


# --------------------------------------------------------------------------
# A tela sabe desenhar todos os estados
# --------------------------------------------------------------------------

ESTADOS_DO_NO = (motor.DESCONHECIDO, motor.LACUNA, motor.FRAGIL,
                 motor.CONFIRMADO, motor.FALSO_POSITIVO, motor.REFUTADO,
                 motor.EM_TREINO, motor.EM_ABERTO, motor.NAO_MEDIDO,
                 motor.CONSTRUIDO)

WEB = pathlib.Path(__file__).resolve().parent / "web"


def _citado(estado, fonte):
    """O estado aparece como VALOR ou como CHAVE, inteiro.

    Substring não serve: renomear `nao_medido` para `nao_medidoX` passava
    limpo na primeira versão deste teste, porque o nome novo contém o
    antigo. A sabotagem pegou.
    """
    return re.search(r'["\']%s["\']|\b%s\s*:' % (estado, estado), fonte) is not None


def test_a_tela_de_quem_responde_desenha_todo_estado():
    """Estado novo no motor e esquecido na tela sai em branco — a premissa
    aparece sem marca nenhuma, igual às que nem começaram. Foi o que quase
    aconteceu com `nao_medido`."""
    js = (WEB / "app.js").read_text(encoding="utf-8")
    # `desconhecido` é o único sem marca de propósito: ainda não chegou a vez.
    faltam = [s for s in ESTADOS_DO_NO
              if s != motor.DESCONHECIDO and not _citado(s, js)]
    assert faltam == [], faltam


def test_o_painel_desenha_todo_estado():
    """No painel até `desconhecido` tem símbolo: quem lê é o pesquisador, e
    ele precisa distinguir 'não tocada' de 'não medida'."""
    html = (WEB / "painel.html").read_text(encoding="utf-8")
    faltam = [s for s in ESTADOS_DO_NO if not _citado(s, html)]
    assert faltam == [], faltam


def test_a_figura_e_do_topico_que_esta_no_ar():
    """Id de nó se repete entre tópicos — todo tópico tem um B1. Enquanto
    havia um tópico só isso não aparecia; com o kc_02 no ar, a tela que
    ensina "a memória é uma rua de lugares numerados" desenhava os quartos
    de hotel do kc_00.

    Figura do tópico errado é pior que figura nenhuma: ela ensina uma
    analogia que o texto não usa.
    """
    js = (WEB / "figuras.js").read_text(encoding="utf-8")
    assert "POR_TOPICO" in js
    for topico in topicos():
        assert re.search(r"POR_TOPICO\.%s\s*=" % topico, js), topico
    # e a tela precisa dizer qual tópico está no ar
    app = (WEB / "app.js").read_text(encoding="utf-8")
    assert "Figuras.topico(" in app


def test_todo_no_de_todo_topico_tem_figura():
    """Nó novo sem desenho sai só com texto, e ninguém percebe até alguém
    atravessar a unidade. Foi assim que o kc_02 passou a mostrar os quartos
    de hotel do kc_00: o banco era global, e o id do nó se repete.
    """
    js = (WEB / "figuras.js").read_text(encoding="utf-8")
    blocos = dict(re.findall(r"POR_TOPICO\.(\w+)\s*=\s*\{(.*?)\n  \};",
                             js, re.S))
    assert set(blocos) >= set(topicos()), sorted(blocos)
    faltam = []
    for topico, bloco in blocos.items():
        dd = carrega(topico=topico)
        for nid in dd.ordem:
            if not re.search(r"\n    %s:\s*function" % nid, bloco):
                faltam.append("%s:%s" % (topico, nid))
    assert faltam == [], faltam


def test_a_tela_sabe_os_tres_momentos_do_ensino():
    """A mesma tela serve à abertura, à construção depois de um "não sei",
    e à apresentação na primeira pergunta. Motivo novo esquecido na tela
    cai na etiqueta da abertura e mostra "Ideia undefined de undefined"."""
    js = (WEB / "app.js").read_text(encoding="utf-8")
    for motivo in ("lacuna", "primeiro_contato"):
        assert _citado(motivo, js), motivo
