"""A camada 2: a razão, e de onde ela vem.

A tese do sistema é que conhecimento é uma cadeia de premissas. Se isso é
verdade, a justificativa de uma resposta **já está no grafo**: a razão
certa é o enunciado da premissa, e as erradas são as crenças que a negam.
Nenhuma delas é escrita à mão — se fossem, a razão e a premissa poderiam
divergir, e o diagnóstico passaria a medir a redação do item.

Estes testes defendem três coisas: que as razões vêm do grafo, que a
camada 1 tranca antes de elas aparecerem, e que uma razão pode falar de
**outro nó** que não o do item.
"""

from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import Resposta

D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


def ate_a_primeira_razao(d, semente=""):
    """Avança até a primeira tela de razão, acertando tudo no caminho."""
    t = motor.inicia(d, semente=semente)
    for _ in range(50):
        if t.tela.tipo == "razao":
            return t
        if t.tela.tipo == "frase":
            t = motor.avanca(d, t.estado, Resposta(texto="x"))
            continue
        if t.tela.tipo == "atividade":
            a = next(x for x in d.atividades if x.id == t.tela.dados["atividade"])
            t = motor.avanca(d, t.estado,
                             Resposta(
                                 escolha=motor.indice_correto_na_tela(
                                     t.estado.semente, a),
                                 confianca="tenho certeza"))
        else:
            t = motor.avanca(d, t.estado, Resposta())
    raise AssertionError("nenhuma tela de razão apareceu")


# --------------------------------------------------------------------------
# As razões vêm do grafo
# --------------------------------------------------------------------------

def test_a_razao_certa_e_o_enunciado_do_no_que_o_item_mira(d):
    for a in d.atividades:
        razoes = motor.razoes_de(d, a)
        certas = [z for z in razoes if z.correta]
        assert len(certas) == 1, a.id
        assert certas[0].texto == d.nos[a.no].simples
        assert certas[0].no == a.no


def test_nenhuma_razao_e_texto_escrito_no_banco_de_atividades(d):
    """A prova de que não há banco de razões: toda frase oferecida é, letra
    por letra, ou o enunciado de um nó ou o que uma crença afirma."""
    do_grafo = {n.simples for n in d.nos.values()}
    do_catalogo = {c.afirma for c in d.crencas.values()}
    for a in d.atividades:
        for z in motor.razoes_de(d, a):
            assert z.texto in do_grafo or z.texto in do_catalogo, (a.id, z.texto)


def test_uma_razao_errada_pode_falar_de_outro_no(d):
    """O caso que a decisão D-9 criou, e que o banco já contém.

    O item mira B1. Um dos distratores é a crença de que sem valor não há
    memória — que nega **B2**. Explicar por ela é informação sobre B2.
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    razoes = motor.razoes_de(d, a)
    alheia = next(z for z in razoes if z.crenca == "no_value_no_memory")
    assert a.no == "B1"
    assert alheia.no == "B2"


def test_toda_crenca_das_alternativas_vira_razao_oferecida(d):
    for a in d.atividades:
        das_opcoes = {o.crenca for o in a.opcoes if o.crenca}
        das_razoes = {z.crenca for z in motor.razoes_de(d, a) if z.crenca}
        assert das_opcoes == das_razoes, a.id


# --------------------------------------------------------------------------
# A camada 1 tranca
# --------------------------------------------------------------------------

def test_a_diagnostica_passa_pela_tela_da_razao(d):
    t = ate_a_primeira_razao(d)
    assert t.tela.tipo == "razao"
    assert t.estado.fase == motor.RAZAO
    assert [e.tipo for e in t.eventos] == ["camada1_respondida", "razoes_apresentadas"]


def test_a_tela_da_razao_mostra_a_resposta_trancada(d):
    t = ate_a_primeira_razao(d)
    a = next(x for x in d.atividades if x.id == t.estado.pendente.atividade)
    assert (t.tela.dados["trancada"]
            == a.opcoes[a.indice_correto_no_arquivo].texto)


def test_responder_a_razao_nao_muda_a_camada_1(d):
    """O cadeado não é enfeite: a escolha mandada na camada 2 indexa as
    RAZÕES, e o que foi respondido na camada 1 segue trancado no estado."""
    t = ate_a_primeira_razao(d)
    p = t.estado.pendente
    errada = next(i for i, z in enumerate(p.razoes) if not z.correta)
    t = motor.avanca(d, t.estado, Resposta(escolha=errada))
    # Camada 3 no meio (T3): a confiança vem depois das duas escolhas.
    depois = motor.avanca(d, t.estado, Resposta(confianca="tenho certeza"))
    registrada = next(e for e in depois.eventos if e.tipo == "resposta_registrada")
    assert registrada.dados["escolha"] == p.escolha
    assert registrada.dados["correta"] is True


def test_a_camada_2_registra_de_qual_no_a_razao_fala(d):
    t = ate_a_primeira_razao(d)
    p = t.estado.pendente
    alheia = next((i for i, z in enumerate(p.razoes)
                   if z.crenca == "no_value_no_memory"), None)
    if alheia is None:
        pytest.skip("o primeiro item não oferece a crença de outro nó")
    depois = motor.avanca(d, t.estado, Resposta(escolha=alheia))
    c2 = next(e for e in depois.eventos if e.tipo == "camada2_respondida")
    assert c2.dados["crenca"] == "no_value_no_memory"
    assert c2.dados["fala_do_no"] == "B2"
    assert c2.dados["razao_correta"] is False


def test_um_item_sem_crenca_nas_alternativas_pula_a_razao(d):
    """Perguntar o porquê com uma alternativa só seria teatro: não há
    escolha a fazer. O log registra o atalho, para a análise saber."""
    sem = next(a for a in d.atividades
               if not any(o.crenca for o in a.opcoes))
    estado = motor.Estado(fase=motor.DIAGNOSTICO, atividade=sem.id, alvo=sem.no)
    t = motor.avanca(d, estado, Resposta(
        escolha=motor.indice_correto_na_tela(estado.semente, sem),
                                         confianca="tenho certeza"))
    tipos = [e.tipo for e in t.eventos]
    assert "razao_pulada" in tipos
    assert t.tela.tipo != "razao"


# --------------------------------------------------------------------------
# A ordem não entrega a resposta, e não é sorteada
# --------------------------------------------------------------------------

def test_a_ordem_das_razoes_nao_e_sempre_a_mesma(d):
    """A correta é sempre a primeira na montagem. Se a tela mostrasse nessa
    ordem, a primeira alternativa seria sempre o gabarito."""
    ordens = {motor.ordem_das_razoes(s, "ciu_kc00_002", 3)
              for s in ("a", "b", "c", "d", "e", "f")}
    assert len(ordens) > 1


def test_a_mesma_semente_devolve_a_mesma_ordem(d):
    """O motor não sorteia: recarregar a página não pode reembaralhar as
    alternativas debaixo de quem está lendo."""
    for _ in range(3):
        assert (motor.ordem_das_razoes("sessao-x", "ciu_kc00_002", 3)
                == motor.ordem_das_razoes("sessao-x", "ciu_kc00_002", 3))


def test_a_ordem_e_uma_permutacao_completa(d):
    for n in (2, 3, 4):
        assert sorted(motor.ordem_das_razoes("s", "a", n)) == list(range(n))


# --------------------------------------------------------------------------
# Camada 3: a confiança, em tela própria e em toda atividade (T3)
# --------------------------------------------------------------------------

def _episodio(d, erra=False, semente=""):
    """Um episódio de diagnóstico inteiro, devolvendo os eventos."""
    t = motor.inicia(d, semente=semente)
    eventos = []
    for _ in range(80):
        eventos.extend(t.eventos)
        tela = t.tela
        if tela.tipo == "frase":
            t = motor.avanca(d, t.estado, Resposta(texto="x"))
            continue
        if tela.tipo == "atividade":
            a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
            na_tela = motor.opcoes_na_tela(t.estado.semente, a)
            i = (next(k for k, o in enumerate(na_tela) if not o.correta)
                 if erra
                 else motor.indice_correto_na_tela(t.estado.semente, a))
            t = motor.avanca(d, t.estado, Resposta(escolha=i, ms=11))
        elif tela.tipo == "razao":
            i = (0 if erra else
                 next(k for k, z in enumerate(t.estado.pendente.razoes) if z.correta))
            t = motor.avanca(d, t.estado, Resposta(escolha=i, ms=22))
        elif tela.tipo == "confianca":
            t = motor.avanca(d, t.estado,
                             Resposta(confianca="tenho certeza", ms=33))
            eventos.extend(t.eventos)
            return eventos
        else:
            t = motor.avanca(d, t.estado, Resposta())
    raise AssertionError("o episódio não fechou")


def test_as_tres_camadas_gravam_eventos_separados_e_em_ordem(d):
    eventos = _episodio(d)
    camadas = [e.tipo for e in eventos if e.tipo.startswith("camada")]
    assert camadas == ["camada1_respondida", "camada2_respondida",
                       "camada3_respondida"]


def test_cada_camada_tem_o_proprio_tempo(d):
    """Sem isto não dá para saber se a pessoa demorou a responder ou a
    justificar — e é a segunda que interessa."""
    por = {e.tipo: e.dados["ms"] for e in _episodio(d)
           if e.tipo.startswith("camada")}
    assert por == {"camada1_respondida": 11, "camada2_respondida": 22,
                   "camada3_respondida": 33}


def test_a_confianca_nao_e_mais_pedida_na_tela_da_atividade(d):
    t = motor.inicia(d)
    while t.tela.tipo != "atividade":
        t = motor.avanca(d, t.estado, Resposta())
    assert t.tela.dados["pede_confianca"] is False


def test_a_tela_da_confianca_mostra_as_duas_escolhas_ja_feitas(d):
    t = ate_a_primeira_razao(d)
    certa = next(i for i, z in enumerate(t.estado.pendente.razoes) if z.correta)
    t = motor.avanca(d, t.estado, Resposta(escolha=certa))
    assert t.tela.tipo == "confianca"
    assert t.tela.dados["resposta"]
    assert t.tela.dados["razao"] == t.estado.pendente.razao.texto


def test_o_treino_tambem_pergunta_a_confianca(d):
    """O critério diz 'a razão muda SEM QUEDA DE CONFIANÇA'. Duas medidas,
    não uma — e a segunda acontece depois da refutação, no treino."""
    from mvp.test_motor import _politica, roda
    _, eventos = roda(d, _politica(erra_no="B3", erra_diagnostico=2, d=d))
    no_treino = [e for e in eventos
                 if e.tipo == "camada3_respondida" and e.dados["origem"] == "treino"]
    assert no_treino, "nenhuma confiança registrada no treino"
    assert all(e.dados["confianca"] for e in no_treino)


def test_a_confianca_declarada_chega_inteira_ao_registro(d):
    eventos = _episodio(d)
    registrada = next(e for e in eventos if e.tipo == "resposta_registrada")
    assert registrada.dados["confianca"] == "tenho certeza"
