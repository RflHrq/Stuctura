"""O conteúdo: a escada das cinco premissas do kc_00.

O kc_00 — declaração de variáveis — é o primeiro tópico a ter escada
escrita, e foi por ele que o Rafael apontou o problema dos textos: a
explicação começava pela parte difícil, usava coisas avançadas, e
nenhuma tela pedia que a pessoa ESCREVESSE uma declaração.

Estes testes guardam a parte da régua que programa mede
(docs/trilha.md, 6.16). A leitura mede o resto: se o texto ensina é
julgamento humano, e o arquivo `docs/escada-kc00-leitura.md` existe para
essa leitura.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import confere_escada  # noqa: E402
import oraculo  # noqa: E402

from mvp import trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

D = carrega(topico="kc_00")
CAMINHO = RAIZ / "mvp" / "dominio" / "escada_kc00.yaml"

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)


@pytest.fixture(scope="module")
def escadas():
    return trilha_escada.le(CAMINHO, D)


def _versoes(escadas):
    for e in escadas.values():
        for g in e.degraus:
            for k, v in enumerate(g.versoes):
                yield e, g, k, v


def test_as_cinco_premissas_tem_escada(escadas):
    assert trilha_escada.faltando(D, escadas) == ()
    assert set(escadas) == set(D.ordem)


def test_cada_escada_tem_de_cinco_a_sete_degraus_e_duas_versoes(escadas):
    for e in escadas.values():
        assert 5 <= len(e.degraus) <= 7, e.premissa
        assert all(len(g.versoes) >= 2 for g in e.degraus), e.premissa
        assert len(e.guiados) >= 2 and len(e.pratica) >= 2, e.premissa


def test_os_ids_seguem_o_padrao_do_topico(escadas):
    for e in escadas.values():
        assert [g.id for g in e.degraus] == [
            "esc_kc00_%s_%d" % (e.premissa, i + 1)
            for i in range(len(e.degraus))]


# O que o kc_00 não ensina, e por isso nenhum degrau pode usar: tamanho,
# conversão, ponteiro, endereço, array. O `*` barra também o comentário
# `/* */`, e é de propósito — comentário é mais uma coisa para ler num
# trecho que tem de caber num olhar.
PROIBIDOS = ("sizeof", "(char)", "(int)", "*", "&", "[")


def test_nenhum_degrau_usa_o_que_o_topico_nao_ensina(escadas):
    for e, g, k, v in _versoes(escadas):
        texto = " ".join((v.mostra, v.antes, v.programa) + v.pecas)
        assert not [p for p in PROIBIDOS if p in texto], (g.id, k + 1)
    for e in escadas.values():
        assert not [p for p in PROIBIDOS if p in e.revisao.codigo], e.premissa


def test_as_duas_versoes_de_um_degrau_nao_sao_a_mesma(escadas):
    for e in escadas.values():
        for g in e.degraus:
            caras = {(v.pede, v.mostra, v.antes, v.pecas, v.programa)
                     for v in g.versoes}
            assert len(caras) == len(g.versoes), g.id


def test_todo_degrau_tem_ao_menos_um_erro_previsto(escadas):
    for e, g, k, v in _versoes(escadas):
        assert v.erros, (g.id, k + 1)


def test_nenhum_retorno_e_so_a_palavra_errado(escadas):
    """O retorno diz o que faltou. "Errado" sozinho é o que o sistema
    fazia antes, e é o que a decisão 4 do Rafael manda acabar."""
    for e, g, k, v in _versoes(escadas):
        for texto in [x.retorno for x in v.erros] + [v.retorno_geral]:
            assert len(texto.split()) >= 5, (g.id, k + 1, texto)


def test_as_cinco_crencas_do_topico_estao_ligadas_a_um_erro(escadas):
    ligadas = {x.crenca for e, g, k, v in _versoes(escadas)
               for x in v.erros if x.crenca}
    assert ligadas == set(D.crencas)


def test_a_crenca_e_ligada_na_escada_da_premissa_que_ela_nega(escadas):
    for e, g, k, v in _versoes(escadas):
        for x in v.erros:
            if x.crenca:
                assert D.crencas[x.crenca].nega == e.premissa, (g.id, x.crenca)


def test_o_b3_nao_tem_degrau_que_execute_programa(escadas):
    """O B3 é a premissa de que o C não limpa a variável. Os trechos dele
    que leem antes de escrever são para ESCOLHER e para ORDENAR — nunca
    para rodar e dizer o que saiu."""
    assert all(g.forma != "digitar" for g in escadas["B3"].degraus)
    r = escadas["B3"].revisao
    assert r.saida == "" or r.codigo.index("=") < r.codigo.index("printf")


def test_o_topico_trabalha_o_mesmo_cenario_do_comeco_ao_fim(escadas):
    """Um exemplo que cresce: `idade` aparece nas cinco escadas."""
    for e in escadas.values():
        texto = " ".join(" ".join((v.mostra, v.antes, v.programa, v.pede)
                                  + v.pecas)
                         for g in e.degraus for v in g.versoes)
        assert "idade" in texto, e.premissa


@tem_gcc
def test_o_compilador_aprova_a_escada_inteira(escadas):
    assert confere_escada.confere(escadas) == []


def test_a_leitura_cobre_as_cinco_premissas(escadas):
    texto = confere_escada.leitura(D, escadas)
    for premissa in D.ordem:
        assert "## %s — %s" % (premissa, D.nos[premissa].simples) in texto
