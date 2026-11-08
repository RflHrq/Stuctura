"""Lacuna → constrói: o caminho que o PRD descrevia e não existia.

O fluxo da fase 4 sempre disse:

    ├─ lacuna   constrói: ensino do nó e item de entrada

e até aqui a lacuna era registrada e a unidade seguia. Quatro etapas para
quem está errado — valida, refuta, treina, confirma — e **zero** para quem
não sabe. O sistema era um refutador, não um professor.

A primeira pessoa que atravessou a unidade respondendo "não sei" em tudo
sentiu isso em cinco minutos. O caminhante tinha rodado trinta sessões e
não sentiu nada: ele prova que a unidade **termina**, e não tem como
provar que ela **ensina**.

Três passos, e só três: ensina o nó, oferece o item mais fácil dele, e
devolve a pessoa ao fluxo. Uma vez por nó, porque sem teto quem responde
"não sei" a tudo recebe ensino, erra a entrada, declara que não sabe de
novo e a unidade nunca termina.
"""

from __future__ import annotations

import pytest

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


def _dos(eventos, tipo):
    return [e for e in eventos if e.tipo == tipo]


def _so_nao_sei(d):
    """Diz que não sabe em tudo. Foi assim que o buraco apareceu."""
    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="")
        return Resposta(nao_sei=True)
    return politica


def _nao_sabia_e_aprendeu(d):
    """Diz "não sei" na PRIMEIRA vez que vê cada nó e, depois do ensino,
    acerta. É o caminho que a construção existe para abrir."""
    gabarito = {a.id: a for a in d.atividades}
    visto = set()

    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="x")
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            return Resposta(escolha=next(i for i, z in enumerate(razoes)
                                         if z.correta))
        if tela.dados.get("fase") != motor.ENTRADA and tela.no not in visto:
            visto.add(tela.no)
            return Resposta(nao_sei=True)
        a = gabarito.get(tela.dados["atividade"])
        return Resposta(escolha=0 if a is None else
                        motor.indice_correto_na_tela(estado.semente, a))
    return politica


# --------------------------------------------------------------------------
# A lacuna deixa de ser beco sem saída
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_declarar_que_nao_sabe_abre_o_ensino_daquele_no(topico):
    """O teste que a tarefa pede. Antes disto, declarar que não sabe
    produzia um evento e a pergunta seguinte."""
    dd = carrega(topico=topico)
    _, eventos = roda(dd, _so_nao_sei(dd))
    aberturas = _dos(eventos, "construcao_iniciada")
    assert aberturas, "a lacuna não construiu nada"
    # uma por nó, não uma por lacuna
    assert len({e.dados["no"] for e in aberturas}) == len(aberturas)


def test_o_ensino_da_construcao_e_do_no_que_a_pessoa_nao_sabia(d2):
    """Reensinar a unidade inteira seria punição, não construção."""
    t = motor.inicia(d2, semente="s")
    # até a primeira atividade
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    no = t.tela.no
    t = motor.avanca(d2, t.estado, Resposta(nao_sei=True))
    assert t.tela.tipo == "ensino"
    assert t.tela.no == no
    assert t.tela.dados["motivo"] == "lacuna"
    # a analogia de resgate vai junto: é o que a tela de abertura não tem
    assert t.tela.dados["resgate"]


def test_a_construcao_leva_a_ampliacao_do_cartao(d2):
    """A ampliação é o texto que caminha pela figura, e ela não chegava aqui.

    `_tela_ensino` mandava `interpretacao`; `_tela_construcao` não. O
    cliente desenha o mesmo elemento nas duas, então quem declarava
    lacuna em B1 ou B3 — os dois únicos nós dos treze tópicos com
    ampliação — recebia o cartão SEM ela. Justo quem mais precisava.

    Achado ao ligar o "ainda não entendi", e separado dele de propósito:
    aquilo era mecanismo, isto é material de ensino.
    """
    com_ampliacao = [n for n in d2.nos if (d2.interpretacao(n) or "").strip()]
    assert com_ampliacao, "o kc_02 perdeu as ampliações de B1 e B3"
    for no in com_ampliacao:
        tela = motor._tela_construcao(d2, no, "lacuna")
        assert tela.dados.get("interpretacao") == d2.interpretacao(no), (
            "a construção do nó %s não leva a ampliação" % no)


def test_no_sem_ampliacao_nao_inventa_campo():
    """Nó sem ampliação recebe campo vazio, nunca texto de outro nó.

    O TÓPICO MUDOU DEBAIXO DESTE TESTE, e a trava de vacuidade dele foi
    quem avisou. Ele usava o kc_02 e exigia achar lá um nó sem
    ampliação; quando o material profundo entrou, os seis passaram a
    ter uma e a lista ficou vazia. O teste não estava errado — o
    exemplo é que acabou.

    Agora ele procura o nó sem ampliação onde ainda há muitos: dos 79
    do projeto, a grande maioria continua sem. Se um dia não houver
    nenhum, a trava dispara de novo, e aí o teste perdeu o objeto —
    que é exatamente o que ela existe para dizer.
    """
    achou = False
    for topico in topicos():
        dd = carrega(topico=topico)
        for no in dd.nos:
            if (dd.interpretacao(no) or "").strip():
                continue
            achou = True
            tela = motor._tela_construcao(dd, no, "lacuna")
            assert not (tela.dados.get("interpretacao") or "").strip(), (
                "%s/%s" % (topico, no))
    assert achou, "nenhum nó sem ampliação em tópico nenhum: teste sem objeto"


def test_depois_do_ensino_vem_o_item_mais_facil(d2):
    """E ele é o item de entrada, não um item de diagnóstico."""
    t = motor.inicia(d2, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    t = motor.avanca(d2, t.estado, Resposta(nao_sei=True))      # ensino
    t = motor.avanca(d2, t.estado, Resposta())                  # item de entrada
    assert t.tela.tipo == "atividade"
    assert t.tela.dados["fase"] == motor.ENTRADA
    item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
    assert item.uso == "entrada"
    assert item.no == t.tela.no


def test_o_item_de_entrada_nao_pergunta_por_que(d2):
    """Perguntar a razão logo depois de ensinar mediria o eco do ensino —
    e poderia levantar uma crença que a pessoa não tem."""
    _, eventos = roda(d2, _nao_sabia_e_aprendeu(d2))
    entradas = {e.dados["atividade"] for e in _dos(eventos, "atividade_apresentada")
                if e.dados["fase"] == motor.ENTRADA}
    assert entradas
    razoes = {e.dados["atividade"] for e in _dos(eventos, "razoes_apresentadas")}
    assert not (entradas & razoes)


def test_quem_nao_sabia_e_aprendeu_termina_com_a_premissa_de_pe(d2):
    """O caminho inteiro: não sabia, foi ensinado, acertou o degrau de
    entrada, voltou ao fluxo e demonstrou a premissa."""
    t, eventos = roda(d2, _nao_sabia_e_aprendeu(d2))
    concluidas = _dos(eventos, "construcao_concluida")
    assert len(concluidas) == len(d2.ordem), "nem todo nó passou pela construção"
    assert all(e.dados["acertou"] for e in concluidas)
    assert all(t.estado.no(n).estado == motor.CONFIRMADO for n in d2.ordem)


def test_acertar_a_entrada_nao_confirma_a_premissa(d2):
    """A CS-5 continua exigindo duas superfícies. O degrau mais baixo tira
    do zero; não demonstra."""
    t = motor.inicia(d2, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    no = t.tela.no
    t = motor.avanca(d2, t.estado, Resposta(nao_sei=True))
    t = motor.avanca(d2, t.estado, Resposta())
    item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
    t = motor.avanca(d2, t.estado, Resposta(
        escolha=motor.indice_correto_na_tela(t.estado.semente, item)))
    assert t.estado.no(no).estado == motor.CONSTRUIDO
    assert t.estado.no(no).estado != motor.CONFIRMADO


def test_errar_a_entrada_mantem_a_lacuna(d2):
    """Sem fingir: continua lacuna, e fica no log que o degrau não foi
    vencido."""
    t = motor.inicia(d2, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    no = t.tela.no
    t = motor.avanca(d2, t.estado, Resposta(nao_sei=True))
    t = motor.avanca(d2, t.estado, Resposta())
    item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
    errada = next(i for i, o in enumerate(
        motor.opcoes_na_tela(t.estado.semente, item)) if not o.correta)
    t = motor.avanca(d2, t.estado, Resposta(escolha=errada))
    assert t.estado.no(no).estado == motor.LACUNA


# --------------------------------------------------------------------------
# Os limites
# --------------------------------------------------------------------------

def test_constroi_uma_vez_por_no(d2):
    """Sem teto, quem diz "não sei" a tudo recebe ensino, erra a entrada,
    declara que não sabe de novo — e a unidade não termina."""
    t, eventos = roda(d2, _so_nao_sei(d2))
    aberturas = _dos(eventos, "construcao_iniciada")
    assert len(aberturas) == len(d2.ordem)
    assert _dos(eventos, "construcao_dispensada"), \
        "a segunda lacuna do mesmo nó não foi dispensada"
    assert t.tela.tipo == "mapa", "a unidade não terminou"


def test_sem_item_de_entrada_o_no_e_ensinado_assim_mesmo(d):
    """O kc_00 ainda não tem banco de entrada, e isso NÃO pode impedir a
    construção: ensinar já é mais do que havia. O que não pode é calar —
    o log diz que faltou item."""
    assert all(a.uso != "entrada" for a in d.atividades), \
        "o kc_00 ganhou itens de entrada; este teste perdeu o caso"
    t, eventos = roda(d, _so_nao_sei(d))
    assert _dos(eventos, "construcao_iniciada")
    faltas = _dos(eventos, "entrada_sem_item")
    assert faltas
    for e in faltas:
        assert e.dados["motivo"]
    assert t.tela.tipo == "mapa"


def test_a_construcao_nao_apaga_o_que_ja_foi_medido(d2):
    """Construir um nó não pode mexer no estado de outro: RF35, domínio de
    um conceito não empresta nem tira domínio de outro."""
    e = motor.Estado().com("I3", estado=motor.CONFIRMADO,
                           superficies=("reconhecer_conceito", "prever_saida"))
    t = motor._inicia_construcao(d2, e, "B1")
    assert t.estado.no("I3").estado == motor.CONFIRMADO
    assert t.estado.no("B1").construcoes == 1


# --------------------------------------------------------------------------
# A premissa antes da primeira pergunta sobre ela
#
# O ensino da abertura cobre só os nós observáveis. No kc_02 isso é metade:
# I1, I2 e I3 eram perguntados sem nunca terem sido ditos. Perguntar o que
# não foi apresentado não mede concepção errônea — mede quem já sabia.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_nenhum_no_e_perguntado_sem_ter_sido_apresentado(topico):
    """A garantia inteira, e ela vale para os dois tópicos."""
    dd = carrega(topico=topico)
    _, eventos = roda(dd, _nao_sabia_e_aprendeu(dd))
    apresentado = set()
    for e in eventos:
        if e.tipo in ("premissa_apresentada", "construcao_iniciada"):
            apresentado.add(e.dados["no"])
        if e.tipo == "ensino_apresentado":
            apresentado.add(e.dados["no"])
        if e.tipo == "atividade_apresentada":
            assert e.dados["no"] in apresentado, (
                "%s foi perguntado antes de ser apresentado" % e.dados["no"])


def test_a_abertura_ensina_os_observaveis_e_o_resto_vem_na_hora(d2):
    """Os de inferência não vão para a abertura de propósito: enfileirar
    seis telas antes da primeira pergunta é aula, não diagnóstico. Eles
    aparecem um a um, cada um colado na pergunta que vem."""
    t, eventos = roda(d2, _nao_sabia_e_aprendeu(d2))
    na_hora = {e.dados["no"] for e in _dos(eventos, "premissa_apresentada")}
    assert na_hora == {"I1", "I2", "I3"}, na_hora


def test_a_tela_diz_que_e_a_primeira_vez(d2):
    """A mesma tela serve a três momentos, e tem de dizer qual é."""
    t = motor.inicia(d2, semente="s")
    vistos = []
    for _ in range(40):
        if t.tela.tipo == "ensino" and t.tela.dados.get("motivo") == "primeiro_contato":
            vistos.append(t.tela.no)
            break
        if t.tela.tipo == "frase":
            t = motor.avanca(d2, t.estado, Resposta(texto="x"))
        elif t.tela.tipo == "atividade":
            item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
            t = motor.avanca(d2, t.estado, Resposta(
        escolha=motor.indice_correto_na_tela(t.estado.semente, item)))
        elif t.tela.tipo == "razao":
            rz = t.estado.pendente.razoes
            t = motor.avanca(d2, t.estado,
                             Resposta(escolha=next(i for i, z in enumerate(rz) if z.correta)))
        elif t.tela.tipo == "confianca":
            t = motor.avanca(d2, t.estado, Resposta(confianca="tenho certeza"))
        else:
            t = motor.avanca(d2, t.estado, Resposta())
    assert vistos, "nenhuma premissa foi apresentada na hora"
    assert t.tela.dados["resgate"], "sem a analogia do nó"


def test_apresenta_uma_vez_so(d2):
    """Reapresentar a cada pergunta viraria repetição, não construção.

    A política é a que ACERTA TUDO, de propósito. Com a que declara "não
    sei", a construção também marca o nó como ensinado, e a sabotagem de
    tirar a marcação do primeiro contato passava limpa — um nó pode voltar
    várias vezes (a CS-5 pede duas superfícies) e só esta política faz ele
    voltar sem passar pela construção.
    """
    _, eventos = roda(d2, _politica(d=d2))
    nos = [e.dados["no"] for e in _dos(eventos, "premissa_apresentada")]
    assert len(nos) == len(set(nos)), nos
    # e cada nó voltou mesmo, senão o teste não morde
    perguntas = [e.dados["no"] for e in _dos(eventos, "atividade_apresentada")]
    assert any(perguntas.count(n) > 1 for n in set(perguntas)),         "nenhum nó voltou; o teste não exercita a reapresentação"


def test_o_item_prometido_e_o_que_vem(d2):
    """A tela promete uma pergunta; tem de ser aquela, e não outra.

    SABOTAGEM FRACA, declarada: trocar o caminho por uma reescolha
    (`_proxima_diagnostica` de novo) não derruba este teste, porque a
    escolha é determinística e cai no mesmo item. O que ele garante de
    verdade é que a pergunta seguinte é DO NÓ que acabou de ser
    apresentado — e isso vale a pena ter escrito, mesmo sem morder o
    caminho inteiro.
    """
    t = motor.inicia(d2, semente="s")
    for _ in range(40):
        if t.tela.tipo == "ensino" and t.tela.dados.get("motivo") == "primeiro_contato":
            break
        if t.tela.tipo == "frase":
            t = motor.avanca(d2, t.estado, Resposta(texto="x"))
        elif t.tela.tipo == "atividade":
            item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
            t = motor.avanca(d2, t.estado, Resposta(
        escolha=motor.indice_correto_na_tela(t.estado.semente, item)))
        elif t.tela.tipo == "razao":
            rz = t.estado.pendente.razoes
            t = motor.avanca(d2, t.estado,
                             Resposta(escolha=next(i for i, z in enumerate(rz) if z.correta)))
        elif t.tela.tipo == "confianca":
            t = motor.avanca(d2, t.estado, Resposta(confianca="tenho certeza"))
        else:
            t = motor.avanca(d2, t.estado, Resposta())
    prometido, no = t.estado.atividade, t.tela.no
    t = motor.avanca(d2, t.estado, Resposta())
    assert t.tela.tipo == "atividade"
    assert t.tela.dados["atividade"] == prometido
    assert t.tela.no == no, "ensinou uma premissa e perguntou de outra"
