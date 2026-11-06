# -*- coding: utf-8 -*-
"""O caminho de quem NÃO SABE: a pergunta não endurece contra ela.

MEDIDO antes de escrever uma linha, persona `nao_sabe` nos treze tópicos
(replicação validada contra o HTTP: kc_02 deu 36/6/30 pelos dois
caminhos, número por número):

    250  "não sei" declarados
     79  momentos de ensino — exatamente um por nó
    171  construções dispensadas
    245  perguntas feitas DEPOIS do "não sei" naquele nó
    153  dessas, com nível MAIS ALTO do que onde a pessoa desistiu  (62%)

O DEFEITO NÃO ERA A ESCADA. Ela está certa: o nível de um nó só sobe em
acerto (`CONFIRMADA` e `FRAGIL_EP`), e `test_escada.py` guarda isso. O que
endurecia a pergunta era `_no_degrau`: cada "não sei" **consome um item**
daquele degrau, e quando os do degrau atual acabam o seletor é obrigado a
subir. Esgotamento de banco, não progressão — e o resultado para quem
declarou que não sabe nada era receber nível 2 e depois nível 3.

A REGRA DESTA FATIA: enquanto o nó estiver em lacuna declarada, o
seletor não sobe de degrau. Ele aceita um degrau mais BAIXO, se houver, e
devolve nada se não houver — e nada é honesto, porque `lacuna` já é um
estado terminal legítimo ("a pessoa sabe que não sabe") e conta como
medida no portão da CS-10.

Quem não declarou lacuna continua subindo exatamente como antes:
`test_quem_nao_declarou_continua_subindo` é o guarda disso, e sem ele
esta fatia consertaria um caso quebrando todos os outros.
"""
from __future__ import annotations

import collections
import hashlib

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d2():
    return D2


def _ids(d, no, ate_nivel):
    """Os itens de diagnóstico do nó até aquele degrau, inclusive."""
    return tuple(a.id for a in d.atividades_do_no(no, "diagnostico")
                 if a.nivel <= ate_nivel)


# --------------------------------------------------------------------------
# O seletor, direto
# --------------------------------------------------------------------------

def test_quem_declarou_lacuna_nao_sobe_de_degrau(d2):
    """O caso dos 153: degrau 1 esgotado, e a pessoa disse que não sabe."""
    e = motor.Estado().com("B1", nivel=1, estado=motor.LACUNA,
                           usadas=_ids(d2, "B1", 1))
    escolhida, pulo, _ = motor._no_degrau(d2, e, "B1")
    assert pulo is None, "subiu de degrau contra quem declarou lacuna"
    assert escolhida is None or escolhida.nivel <= 1, (
        "entregou um item de nível %s a quem desistiu no nível 1"
        % (escolhida.nivel if escolhida else None))


def test_quem_nao_declarou_continua_subindo(d2):
    """O guarda: sem este teste, a fatia conserta um caso e quebra o resto.

    Mesmo nó, mesmo esgotamento, SEM lacuna declarada — e aí subir é o
    comportamento certo, porque o degrau acabou por uso, não por
    desistência. É o que `test_escada.py` já cobra.
    """
    e = motor.Estado().com("B1", nivel=1, usadas=_ids(d2, "B1", 1))
    escolhida, pulo, motivo = motor._no_degrau(d2, e, "B1")
    assert escolhida is not None and escolhida.nivel == 2
    assert pulo == 2 and "acabou" in motivo


def test_lacuna_aceita_um_degrau_mais_BAIXO(d2):
    """Não subir não é parar: se sobrou item mais fácil, ele serve.

    Quem declarou lacuna no degrau 2 e tem item de 1 sem usar recebe o de
    1 — mais fácil é exatamente o que o caso pede.
    """
    usadas = tuple(a.id for a in d2.atividades_do_no("B1", "diagnostico")
                   if a.nivel == 2)
    e = motor.Estado().com("B1", nivel=2, estado=motor.LACUNA, usadas=usadas)
    escolhida, pulo, _ = motor._no_degrau(d2, e, "B1")
    assert escolhida is not None and escolhida.nivel < 2
    assert pulo is None


def test_sem_item_abaixo_o_no_acaba(d2):
    """Nada mais fácil para oferecer: devolve nada, e `lacuna` é terminal
    legítimo. Inventar uma pergunta mais difícil era o defeito."""
    e = motor.Estado().com("B1", nivel=1, estado=motor.LACUNA,
                           usadas=_ids(d2, "B1", 1))
    escolhida, _, _ = motor._no_degrau(d2, e, "B1")
    assert escolhida is None


# --------------------------------------------------------------------------
# A sessão inteira: a invariante nos treze tópicos
# --------------------------------------------------------------------------

def _cala(atividade):
    """A persona `nao_sabe` do caminhante: metade dos itens, pelo id."""
    return hashlib.sha256(atividade.encode("utf-8")).digest()[0] % 2 == 0


def percorre_nao_sabe(d, semente="NAOSEI", limite=900):
    """Devolve (eventos, estado final). O estado importa: é por ele que se
    confere que a fatia não deixou nós sem medida."""
    t = motor.inicia(d, semente=semente)
    ev = list(t.eventos)
    for _ in range(limite):
        tela = t.tela
        if tela.tipo == "mapa":
            return ev, t.estado
        if tela.tipo == "frase":
            r = Resposta(texto="nao sei dizer")
        elif tela.tipo == "confianca":
            r = Resposta(confianca="chutei")
        elif tela.tipo == "razao":
            r = Resposta(nao_sei=True)
        elif tela.tipo == "atividade":
            aid = tela.dados["atividade"]
            if _cala(aid):
                r = Resposta(nao_sei=True)
            else:
                a = next(x for x in d.atividades if x.id == aid)
                na_tela = motor.opcoes_na_tela(semente, a)
                i = next((k for k, o in enumerate(na_tela)
                          if a.crenca is not None and o.crenca == a.crenca),
                         next((k for k, o in enumerate(na_tela)
                               if not o.correta), 0))
                r = Resposta(escolha=i)
        else:
            r = Resposta()
        t = motor.avanca(d, t.estado, r)
        ev.extend(t.eventos)
    raise AssertionError("a unidade não terminou em %d passos" % limite)


def _subidas_apos_lacuna(ev):
    """(subidas, perguntas) feitas depois de um "não sei" naquele nó."""
    nivel_no_item = {}
    onde_desistiu = {}
    subiu = perguntas = 0
    for e in ev:
        if e.tipo == "atividade_apresentada":
            no, nv = e.dados.get("no"), e.dados.get("nivel")
            if no in onde_desistiu:
                perguntas += 1
                if nv and onde_desistiu[no] and nv > onde_desistiu[no]:
                    subiu += 1
            nivel_no_item[no] = nv
        elif e.tipo == "lacuna_registrada":
            no = e.dados.get("no")
            onde_desistiu[no] = nivel_no_item.get(no)
    return subiu, perguntas


@pytest.mark.parametrize("topico", topicos())
def test_nenhuma_pergunta_endurece_depois_do_nao_sei(topico):
    """A invariante, nos treze tópicos. Eram 153 ocorrências."""
    d = carrega(topico=topico)
    ev, _ = percorre_nao_sabe(d)
    subiu, perguntas = _subidas_apos_lacuna(ev)
    assert subiu == 0, (
        "%s: %d das %d perguntas feitas depois de um 'não sei' vieram num "
        "degrau MAIS ALTO" % (topico, subiu, perguntas))


def test_a_invariante_nao_e_vazia():
    """O guarda anti-vacuidade, e ele é do CONJUNTO, não de cada tópico.

    Zero perguntas depois de um "não sei" é resultado legítimo da fatia —
    no kc_00 o nó acaba ali mesmo, porque não há degrau mais baixo. Mas se
    isso valesse nos treze, `subiu == 0` não provaria nada em lugar
    nenhum: estaria contando o vazio.
    """
    total = 0
    for topico in topicos():
        ev, _ = percorre_nao_sabe(carrega(topico=topico))
        total += _subidas_apos_lacuna(ev)[1]
    assert total >= 20, (
        "só %d perguntas depois de um 'não sei' em treze tópicos: a "
        "invariante estaria contando o vazio" % total)


@pytest.mark.parametrize("topico", topicos())
def test_a_unidade_continua_terminando(topico):
    """Não subir não pode virar sessão que não acaba, nem nó sem medida.

    `lacuna` conta como medida no portão da CS-10; `desconhecido`,
    `nao_medido`, `refutado` e `em_treino` não contam. Se a fatia deixasse
    nós nesses estados, ela teria trocado um defeito por outro.
    """
    d = carrega(topico=topico)
    ev, final = percorre_nao_sabe(d)          # levanta se não terminar
    assert any(e.tipo == "unidade_encerrada" for e in ev), (
        "%s: a unidade não encerrou" % topico)
    assert any(e.tipo == "lacuna_registrada" for e in ev), (
        "%s não registrou lacuna nenhuma" % topico)
    sem_medida = ("desconhecido", "nao_medido", "refutado", "em_treino")
    parados = [n["no"] for n in motor.estado_dos_nos(d, final)
               if n["estado"] in sem_medida]
    assert not parados, (
        "%s: a fatia deixou %s sem medida — trocou um defeito por outro"
        % (topico, parados))
