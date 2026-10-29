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
from mvp.dominio import carrega
from mvp.motor import Resposta
from mvp.test_motor import roda

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
    gabarito = {a.id: a.indice_correto for a in d.atividades}
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
        return Resposta(escolha=gabarito.get(tela.dados["atividade"], 0))
    return politica


# --------------------------------------------------------------------------
# A lacuna deixa de ser beco sem saída
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", ["kc_00", "kc_02"])
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
    t = motor.avanca(d2, t.estado, Resposta(escolha=item.indice_correto))
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
    errada = next(i for i, o in enumerate(item.opcoes) if not o.correta)
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
