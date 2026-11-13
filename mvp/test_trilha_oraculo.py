"""O compilador como juiz da escada.

A sessão corrige uma resposta produzida sem compilador: a sequência de
peças bate, ou não, com o que o conteúdo previu. Então o que o conteúdo
previu tem de estar certo ANTES — toda linha que um degrau chama de
certa compila, toda linha que um retorno chama de inválida é recusada, e
todo valor que um degrau espera é o que o programa imprime.

Quem confere isso é `scripts/confere_escada.py`, e estes testes rodam um
compilador de verdade. Onde não houver um, são PULADOS e dizem isso.

UMA REGRA A MAIS, e ela é do tópico: o kc_00 ensina que ler uma variável
sem valor não é coisa que se faça. O conferidor então só COMPILA o que
não é de `digitar` — nunca executa —, e há teste guardando isso.
"""

from __future__ import annotations

import copy
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
from mvp.test_trilha_escada import _escreve, _valida  # noqa: E402

D = carrega(topico="kc_00")

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)


def _escadas(tmp_path, bloco):
    return trilha_escada.le(_escreve(tmp_path, {"B1": bloco}), D)


# --------------------------------------------------------------------------
# As peças do conferidor
# --------------------------------------------------------------------------

def test_o_programa_embrulha_as_linhas():
    p = confere_escada.programa_de("int idade;", "idade = 20;")
    assert "#include <stdio.h>" in p and "int main(void)" in p
    assert p.index("int idade;") < p.index("idade = 20;") < p.index("return 0;")


def test_o_programa_sem_antes_tem_so_as_linhas():
    p = confere_escada.programa_de("", "int nota ;")
    assert "int nota ;" in p and "\n\n\n" not in p


def test_a_linha_de_montar_junta_as_pecas_com_espaco(tmp_path):
    v = _escadas(tmp_path, _valida())["B1"].degraus[0].versoes[0]
    assert confere_escada.linha_de(v, (0, 1, 2)) == "int nota ;"
    assert confere_escada.linha_de(v, (1, 0, 2)) == "nota int ;"


def test_a_linha_de_completar_poe_a_peca_na_lacuna():
    v = trilha_escada.Versao(pede="Complete.", mostra="___ = 7;",
                             pecas=("idade", "int"), certa=((0,),),
                             certa_texto="idade = 7;")
    assert confere_escada.linha_de(v, (0,)) == "idade = 7;"
    assert confere_escada.linha_de(v, (1,)) == "int = 7;"


@tem_gcc
def test_declaracao_valida_compila():
    assert confere_escada.compila(
        confere_escada.programa_de("", "int nota ;"))[0]


@tem_gcc
def test_tipo_depois_do_nome_nao_compila():
    ok, nota = confere_escada.compila(
        confere_escada.programa_de("", "nota int ;"))
    assert not ok and nota


@tem_gcc
def test_ler_sem_valor_compila_e_nao_e_executado(monkeypatch):
    """O trecho é o que o B3 ensina a NÃO fazer. Compilar, sim; rodar, não."""
    monkeypatch.setattr(oraculo, "roda",
                        lambda *a, **k: pytest.fail("executou o programa"))
    ok, _ = confere_escada.compila(confere_escada.programa_de(
        "", 'int n;\nprintf("%d\\n", n);'))
    assert ok


# --------------------------------------------------------------------------
# O que o conferidor acusa
# --------------------------------------------------------------------------

@tem_gcc
def test_a_escada_certa_passa(tmp_path):
    assert confere_escada.confere(_escadas(tmp_path, _valida())) == []


@tem_gcc
def test_o_conferidor_acusa_resposta_certa_que_nao_compila(tmp_path):
    b = _valida()
    for v in b["degraus"][0]["versoes"]:
        v["certa"] = [[1, 0, 2]]            # "nota int ;"
        v["erros"] = v["erros"][1:]
    problemas = confere_escada.confere(_escadas(tmp_path, b))
    assert len(problemas) == 2
    assert all("esc_t_B1_1" in p and "não compila" in p for p in problemas)


@tem_gcc
def test_o_conferidor_acusa_erro_dito_invalido_que_compila(tmp_path):
    b = _valida()
    v = b["degraus"][0]["versoes"][0]
    v["pecas"] = ["int", "nota", ";", "=", "idade"]
    v["erros"].append({"exata": [0, 4, 2], "invalida": True,
                       "retorno": "Isto não é uma declaração."})
    problemas = confere_escada.confere(_escadas(tmp_path, b))
    assert len(problemas) == 1
    assert "esc_t_B1_1" in problemas[0] and "compila" in problemas[0]
    assert "int idade ;" in problemas[0]


@tem_gcc
def test_o_conferidor_acusa_opcao_marcada_no_lado_errado(tmp_path):
    b = _valida()
    b["degraus"][1]["versoes"][0]["invalidas"] = [0]
    problemas = confere_escada.confere(_escadas(tmp_path, b))
    assert len(problemas) == 2 and all("esc_t_B1_2" in p for p in problemas)


@tem_gcc
def test_o_conferidor_acusa_saida_que_nao_bate(tmp_path):
    b = _valida()
    v = b["degraus"][2]["versoes"][0]
    v["aceitas"], v["certa_texto"] = ["9"], "9"
    problemas = confere_escada.confere(_escadas(tmp_path, b))
    assert len(problemas) == 1
    assert "esc_t_B1_3" in problemas[0] and "21" in problemas[0]


@tem_gcc
def test_digitar_sem_programa_e_conferido_pelo_trecho_mostrado(tmp_path):
    trecho = chr(10).join(["int idade = 20;", "idade = 21;",
                           'printf("%d' + chr(92) + 'n", idade);'])
    b = _valida()
    v = b["degraus"][2]["versoes"][0]
    v["mostra"], v["programa"] = trecho, ""
    assert confere_escada.confere(_escadas(tmp_path, b)) == []

    v["aceitas"], v["certa_texto"], v["erros"] = ["20"], "20", []
    problemas = confere_escada.confere(_escadas(tmp_path, b))
    assert len(problemas) == 1 and "esc_t_B1_3" in problemas[0]


@tem_gcc
def test_o_conferidor_acusa_revisao_que_nao_imprime_o_que_diz(tmp_path):
    b = _valida()
    b["revisao"] = {"frases": ["Vale o último valor."],
                    "codigo": 'int idade = 20;\nidade = 21;\n'
                              'printf("%d\\n", idade);\n',
                    "saida": "20"}
    problemas = confere_escada.confere(_escadas(tmp_path, b))
    assert len(problemas) == 1 and "revisão" in problemas[0]

    b["revisao"]["saida"] = "21"
    assert confere_escada.confere(_escadas(tmp_path, b)) == []


@tem_gcc
def test_degrau_que_nao_e_codigo_nao_vai_ao_compilador(tmp_path):
    b = _valida()
    degrau = copy.deepcopy(b["degraus"][1])
    degrau.update(id="esc_t_B1_9", codigo=False)
    for v in degrau["versoes"]:
        v.update(pecas=["Sim, já existe", "Só quando receber um valor"],
                 certa=[[0]], certa_texto="Sim, já existe", invalidas=[],
                 erros=[{"exata": [1], "retorno": "A linha já reservou."}])
    b["degraus"].append(degrau)
    assert confere_escada.confere(_escadas(tmp_path, b)) == []


# --------------------------------------------------------------------------
# A leitura, para quem vai revisar o texto
# --------------------------------------------------------------------------

def test_a_leitura_traz_frases_exercicio_e_retornos(tmp_path):
    texto = confere_escada.leitura(D, _escadas(tmp_path, _valida()))
    assert "## B1" in texto and D.nos["B1"].simples in texto
    assert "Declare uma variável inteira chamada nota." in texto
    assert "Monte a linha com as peças." in texto
    assert "Em C o tipo vem primeiro" in texto
    assert "Toda declaração termina com ;" in texto
    assert "int nota;" in texto and "int ano;" in texto
    assert "Toda variável tem um nome e um tipo." in texto     # a revisão
