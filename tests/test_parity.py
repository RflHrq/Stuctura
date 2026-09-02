"""Paridade dos braços A e B (§8, §11). O TESTE CRÍTICO.

Falha aqui invalida o experimento inteiro: significa que o grupo de
controle recebeu conteúdo diferente do grupo socrático, e nenhuma
diferença de aprendizado poderia ser atribuída ao método.

Escrito ANTES da interface, de propósito. É o que se mostra à banca quando
perguntarem como a variável foi controlada.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic, strategy
from engine.loader import load


@pytest.fixture(scope="module")
def d():
    return load()


# --------------------------------------------------------------------------
# O invariante central
# --------------------------------------------------------------------------

def test_paridade_sobre_todo_o_catalogo(d):
    """Os dois braços recebem os mesmos nós, na mesma ordem, para as 34 crenças."""
    quebrados = [r for r in strategy.parity_over_catalog(d) if not r.ok]
    assert not quebrados, "\n".join(str(r) for r in quebrados)


def test_paridade_sobre_toda_conclusao_de_kc(d):
    for kc in d.kcs.values():
        r = strategy.parity(d, kc.id, kc.conclusion_node)
        assert r.ok, str(r)


def test_paridade_sobre_todo_no_do_dominio(d):
    """Não só nos alvos do catálogo: qualquer nó, como alvo, mantém paridade."""
    for kc in d.kcs.values():
        for node in kc.nodes:
            r = strategy.parity(d, kc.id, node)
            assert r.ok, str(r)


def test_paridade_se_mantem_com_nos_ja_confirmados(d):
    """RF07 pula nós confirmados — e tem de pular os mesmos nos dois braços."""
    kc, alvo = "kc_09", "I2"
    plano = socratic.full_plan(d, kc, alvo)
    for corte in range(len(plano)):
        confirmados = plano[:corte]
        r = strategy.parity(d, kc, alvo, confirmados)
        assert r.ok, "com %d nó(s) confirmado(s): %s" % (corte, r)


# --------------------------------------------------------------------------
# O que PODE diferir — e só isso
# --------------------------------------------------------------------------

def test_o_que_difere_e_apenas_o_tipo_de_acao(d):
    a = strategy.SocraticStrategy().correct(d, "kc_09", "I1")
    b = strategy.DirectStrategy().correct(d, "kc_09", "I1")

    assert [x.kind for x in a] == ["ask"] * len(a)
    assert [x.kind for x in b[:-1]] == ["explain"] * (len(b) - 1)
    assert b[-1].kind == "confirm"

    # Mesmos nós, mesma ordem, mesma numeração de passo.
    assert [(x.kc, x.node, x.idx) for x in a] == [(x.kc, x.node, x.idx) for x in b[:-1]]


def test_braco_b_tem_exatamente_uma_acao_a_mais(d):
    """A confirmação de leitura pareia com o ato de responder do braço A."""
    for m in d.misconceptions.values():
        a = strategy.SocraticStrategy().correct(d, m.kc, m.node)
        b = strategy.DirectStrategy().correct(d, m.kc, m.node)
        assert len(b) == len(a) + 1


def test_o_texto_do_braco_b_sai_do_mesmo_no_do_yaml(d):
    """O braço B não pode ter texto próprio: é o mesmo nó, outra forma verbal."""
    for m in d.misconceptions.values():
        for acao in strategy.DirectStrategy().correct(d, m.kc, m.node):
            if acao.kind == "confirm":
                continue
            assert acao.text == d.node(acao.kc, acao.node).text


def test_braco_desconhecido_falha_alto(d):
    with pytest.raises(ValueError, match="braço desconhecido"):
        strategy.for_arm("hibrido")


# --------------------------------------------------------------------------
# Propriedades do traversal (§11, nível "propriedade")
# --------------------------------------------------------------------------

def test_plano_nunca_repete_no(d):
    for kc in d.kcs.values():
        for node in kc.nodes:
            plano = socratic.full_plan(d, kc.id, node)
            assert len(plano) == len(set(plano)), "%s:%s repete nó" % (kc.id, node)


def test_suporte_sempre_vem_antes_do_no(d):
    """A pós-ordem garante ordem topológica. É o que sustenta o socrático."""
    for kc in d.kcs.values():
        for node in kc.nodes:
            plano = socratic.full_plan(d, kc.id, node)
            posicao = {r: i for i, r in enumerate(plano)}
            for i, ref in enumerate(plano):
                for s in d.node(*ref).support:
                    if s in posicao:
                        assert posicao[s] < i, (
                            "%s:%s aparece depois de %s:%s, que ele sustenta"
                            % (*s, *ref)
                        )


def test_plano_termina_e_nao_excede_o_numero_de_nos(d):
    total = sum(len(k.nodes) for k in d.kcs.values())
    for kc in d.kcs.values():
        for node in kc.nodes:
            assert len(socratic.full_plan(d, kc.id, node)) <= total


def test_plano_e_deterministico(d):
    """RNF02: mesmo estado, mesmo plano. 100 execuções."""
    resultados = {tuple(socratic.full_plan(d, "kc_09", "I2")) for _ in range(100)}
    assert len(resultados) == 1


def test_alvo_e_sempre_o_ultimo_passo(d):
    for kc in d.kcs.values():
        for node in kc.nodes:
            assert socratic.full_plan(d, kc.id, node)[-1] == (kc.id, node)


def test_alvo_nao_e_pulado_mesmo_se_ja_confirmado(d):
    """O nó negado é sempre percorrido: é ele que está errado.

    Confirmar o alvo não confirma o suporte dele — o plano completo
    continua de pé. Com TODO o suporte confirmado, sobra só o alvo.
    """
    alvo = ("kc_09", "I2")
    completo = socratic.full_plan(d, *alvo)

    assert socratic.plan(d, *alvo, confirmed=[alvo]) == completo

    suporte = [r for r in completo if r != alvo]
    assert socratic.plan(d, *alvo, confirmed=suporte + [alvo]) == [alvo]
