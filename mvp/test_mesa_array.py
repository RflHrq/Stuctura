# -*- coding: utf-8 -*-
"""O teste de mesa aprende índice de array.

POR QUE ISTO EXISTE. O B1 do kc_07 afirma que `int a[5]` cria cinco
caixas grudadas, e o nome vale pelo conjunto. A ilustração perfeita
dessa afirmação é a tabela: uma linha por instrução, uma coluna por
caixa, mostrando que escrever em `a[1]` não mexe em `a[0]`.

E o gerador recusava: `NaoSeiSondar: não sei sondar: a[0] = 7;`. O
padrão de atribuição dele não casava com índice, e `_variaveis`
devolveria `a` — que `printf("%d", a)` não imprime.

A DECISÃO DE DESENHO: uma declaração de array declara N VARIÁVEIS,
chamadas `a[0]`..`a[N-1]`. Com isso a máquina toda continua valendo sem
exceção — par de colunas por caixa, valor e endereço —, e o que a tabela
mostra é exatamente o que o nó afirma: cada caixa é uma caixa.

E O `?`. `int a[3];` sem inicializador deixa as três indeterminadas, e
imprimir o lixo que estiver lá daria uma tabela que muda a cada execução
— afirmação dependente de ambiente, que é o portão 3 da revisão de
material. Então valor indeterminado sai `?`, e o endereço sai, porque
ele É determinado. A tabela passa a ensinar, de graça, que C não zera o
que declara — que é o kc_00:B3.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "scripts"))

from mesa import (ATRIBUICAO, NaoSeiSondar, _executaveis,  # noqa: E402
                  _variaveis, gera)

NL = chr(10)

B1 = NL.join(["int a[3];", "a[0] = 10;", "a[1] = 20;"])


# --------------------------------------------------------------------------
# As peças
# --------------------------------------------------------------------------

def test_a_atribuicao_com_indice_e_aceita():
    """O padrão que recusava `a[0] = 7;`."""
    for linha in ("a[0] = 7;", "a[2] = 99;", "dados[1] = x;",
                  "a[0] = a[1];"):
        assert ATRIBUICAO.match(linha), linha


def test_a_atribuicao_sem_indice_continua_aceita():
    """Regressão: o que já passava não pode parar de passar."""
    for linha in ("x = 7;", "*p = 9;", "p = &y;"):
        assert ATRIBUICAO.match(linha), linha


def test_executaveis_nao_recusa_mais_o_indice():
    assert _executaveis(B1) == ["int a[3];", "a[0] = 10;", "a[1] = 20;"]


def test_a_declaracao_de_array_vira_uma_variavel_por_caixa():
    """É a decisão de desenho, e é o que faz o resto funcionar sem
    exceção nenhuma."""
    assert _variaveis(["int a[3];"]) == [
        ("a[0]", "int", False),
        ("a[1]", "int", False),
        ("a[2]", "int", False)]


def test_array_e_escalar_na_mesma_lista():
    assert _variaveis(["int x = 1;", "int a[2];"]) == [
        ("x", "int", False),
        ("a[0]", "int", False),
        ("a[1]", "int", False)]


def test_o_tamanho_do_array_tem_de_ser_literal():
    """`int a[n];` não dá tabela: o gerador não executa para descobrir
    quantas colunas emitir, e inventar um número seria pior."""
    with pytest.raises(NaoSeiSondar) as erro:
        _variaveis(["int a[n];"])
    assert "literal" in str(erro.value).lower() or "n" in str(erro.value)


def test_array_de_tamanho_zero_e_recusado():
    with pytest.raises(NaoSeiSondar):
        _variaveis(["int a[0];"])


def test_indice_fora_do_declarado_e_recusado():
    """`a[5] = 1;` num `int a[3]` é acesso fora do array. Gerar a tabela
    significaria compilar e rodar isso, e o resultado não é afirmação
    sobre nada."""
    with pytest.raises(NaoSeiSondar) as erro:
        _executaveis(NL.join(["int a[3];", "a[5] = 1;"]))
    assert "a[5]" in str(erro.value)


# --------------------------------------------------------------------------
# A tabela de verdade, gerada pela execução
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tabela():
    return gera(B1)


def test_uma_coluna_de_valor_e_uma_de_endereco_por_caixa(tabela):
    assert tabela["colunas"] == ["a[0]", "&a[0]", "a[1]", "&a[1]",
                                 "a[2]", "&a[2]"]


def test_uma_linha_por_instrucao(tabela):
    assert [l["codigo"] for l in tabela["linhas"]] == [
        "int a[3];", "a[0] = 10;", "a[1] = 20;"]


def test_caixa_sem_valor_sai_interrogacao(tabela):
    """A primeira linha: três caixas declaradas e nenhuma escrita.

    Imprimir o lixo daria número diferente a cada execução — e a tabela
    é guardada no YAML, então ela ficaria errada no dia seguinte.
    """
    primeira = tabela["linhas"][0]["valores"]
    assert primeira[0] == "?", primeira
    assert primeira[2] == "?", primeira
    assert primeira[4] == "?", primeira


def test_o_endereco_sai_mesmo_sem_valor(tabela):
    """O endereço é determinado desde a declaração: a caixa já existe."""
    primeira = tabela["linhas"][0]["valores"]
    for i in (1, 3, 5):
        assert primeira[i].strip(), primeira
        assert primeira[i] != "?", primeira


def test_escrever_numa_caixa_nao_mexe_na_outra(tabela):
    """A AFIRMAÇÃO DO NÓ, agora visível na tabela.

    Depois de `a[0] = 10;` a primeira caixa vale 10 e as outras duas
    continuam `?`. Depois de `a[1] = 20;` as duas primeiras valem 10 e
    20 ao mesmo tempo — que é o contrário de "uma caixa só com os
    valores dentro", a crença que o cartão confronta.
    """
    depois_da_1a = tabela["linhas"][1]["valores"]
    assert depois_da_1a[0] == "10", depois_da_1a
    assert depois_da_1a[2] == "?", depois_da_1a

    depois_da_2a = tabela["linhas"][2]["valores"]
    assert depois_da_2a[0] == "10", depois_da_2a
    assert depois_da_2a[2] == "20", depois_da_2a
    assert depois_da_2a[4] == "?", depois_da_2a


def test_as_caixas_estao_grudadas(tabela):
    """A outra metade da afirmação: a distância entre duas vizinhas é o
    tamanho de um int. A ampliação do cartão afirma isso, e é aqui que a
    afirmação vira medida."""
    valores = tabela["linhas"][2]["valores"]
    enderecos = [int(valores[i], 16) for i in (1, 3, 5)]
    assert enderecos[1] - enderecos[0] == 4, enderecos
    assert enderecos[2] - enderecos[1] == 4, enderecos


def test_os_tres_enderecos_sao_diferentes(tabela):
    valores = tabela["linhas"][0]["valores"]
    enderecos = [valores[i] for i in (1, 3, 5)]
    assert len(set(enderecos)) == 3, enderecos


# --------------------------------------------------------------------------
# O escalar não mudou
# --------------------------------------------------------------------------

def test_escalar_inicializado_continua_mostrando_o_valor():
    """Regressão do formato antigo: nenhuma das tabelas já guardadas
    pode mudar por causa desta fatia. As quatro do kc_02 declaram com
    inicializador, então nenhuma tem `?`."""
    t = gera(NL.join(["int x = 42;", "int y = 7;"]))
    assert t["colunas"] == ["x", "&x", "y", "&y"]
    assert t["linhas"][0]["valores"][0] == "42"
    assert t["linhas"][1]["valores"][2] == "7"


def test_escalar_declarado_sem_valor_tambem_sai_interrogacao():
    """A regra é a mesma para escalar, e é o certo: `int x;` não tem
    valor, e dizer um número ali seria inventar."""
    t = gera(NL.join(["int x;", "x = 5;"]))
    assert t["linhas"][0]["valores"][0] == "?"
    assert t["linhas"][1]["valores"][0] == "5"


def test_a_tabela_do_caso_resolvido_do_b1_do_kc07():
    """O cenário que o rascunho usa, de ponta a ponta."""
    t = gera(NL.join(["int a[3];", "a[0] = 7;", "a[1] = 7;",
                      "a[2] = 7;", "a[1] = 99;"]))
    ultima = t["linhas"][-1]["valores"]
    assert [ultima[0], ultima[2], ultima[4]] == ["7", "99", "7"], ultima
