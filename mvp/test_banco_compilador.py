"""O banco de questões contra o compilador.

O conferidor das escadas (`confere_escada.py`) nunca olhou o banco: das
560 questões, a revisão mecânica conferia a ligação com o catálogo e a
forma, mas não o que o código faz. A conferência de 18/11/2026 rodou o
código das 321 questões que têm código e achou dois defeitos:

- oito questões do kc_02 com o `\\n` do `printf` virado quebra de linha de
  verdade — a pessoa via o código partido, e uma delas abria a premissa B3;
- a `ciu_kc12_t12`, que dá como certo um 0 que o gcc 16.2 não imprime (já
  estava fora da trilha).

Estes testes prendem as duas coisas.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import confere_banco  # noqa: E402
import oraculo  # noqa: E402
from mvp import trilha_escada  # noqa: E402
from mvp.dominio import carrega, topicos  # noqa: E402

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem o compilador do oráculo")


def test_nenhum_trecho_parte_uma_string_entre_linhas():
    """Uma linha com aspas ímpares é uma string que continua na linha de
    baixo — em C, não compila; na tela, é o código partido ao meio."""
    partidos = []
    for t in topicos():
        d = carrega(topico=t)
        for a in d.atividades:
            if confere_banco.linhas_com_string_partida(a.codigo):
                partidos.append(a.id)
        for no in d.ordem:
            if confere_banco.linhas_com_string_partida(d.exemplo(no) or ""):
                partidos.append("%s/%s cartão" % (t, no))
    assert partidos == []


def test_a_string_partida_e_reconhecida():
    inteira = 'printf("%d\\n", x);'           # barra e n, como no código
    partida = 'printf("%d\n", x);'            # quebra de linha de verdade
    assert confere_banco.linhas_com_string_partida(inteira) == []
    assert confere_banco.linhas_com_string_partida(partida) == [1, 2]
    assert confere_banco.linhas_com_string_partida("char c = '\"';") == []
    assert confere_banco.linhas_com_string_partida('puts("a \\" b");') == []


def test_o_valor_da_alternativa():
    v = confere_banco.valor
    assert v("30: só o último valor escrito") == "30"
    assert v("0 — são endereços de duas variáveis diferentes") == "0"
    assert v("0, porque são dois lugares diferentes") == "0"
    assert v("15 e depois 16: cada um mostra o valor daquele momento") == "15 16"
    assert v("1 e 2: a caixa durou entre elas") == "1 2"
    assert v("Talvez 7: b caiu onde a esteve") is None
    assert v("Não dá para saber: idade não recebeu valor") is None


def test_a_montagem_chama_a_funcao_quando_o_trecho_e_so_ela():
    p = confere_banco.monta("void f(void) {\n    printf(\"%d\\n\", 9);\n}")
    assert "int main(void) {\nf();" in p
    p = confere_banco.monta("int main(void) { return 0; }")
    assert p.count("int main") == 1
    # A que devolve valor é chamada pela outra; chamá-la também contaria
    # uma vez a mais (ciu_kc12_t08).
    p = confere_banco.monta(
        "int conta(void) { static int n = 0; n++; return n; }\n"
        "void f(void) {\n    conta();\n    printf(\"%d\\n\", conta());\n}")
    assert "int main(void) {\nf();\nreturn 0;" in p


def test_so_confere_a_questao_que_imprime():
    """'Quanto vale o a no fim da segunda chamada?' é prever_saida, mas
    não imprime: o valor está na variável, não na tela (ciu_kc01_t05)."""
    assert not confere_banco.imprime("void f(void) { int a = 1; }\nf();")
    assert confere_banco.imprime('printf("%d\\n", x);')
    assert confere_banco.imprime('puts("oi");')


@tem_gcc
def test_a_resposta_certa_de_prever_a_saida_e_a_que_o_gcc_imprime():
    """Toda questão de prever a saída cuja alternativa certa é um valor
    imprime esse valor no gcc 16.2; a que não imprime está fora da trilha
    (a escada do tópico a declara em `fora_da_trilha`). Hoje não há
    nenhuma: a única, a `ciu_kc12_t12`, foi reescrita em 18/11/2026."""
    todos = []
    for t in topicos():
        d = carrega(topico=t)
        arquivo = RAIZ / "dominio" / ("escada_%s.yaml" % t.replace("_", ""))
        fora = {i for e in trilha_escada.le(arquivo, d).values() for i in e.fora}
        for problema in confere_banco.confere(d):
            assert problema.id in fora, problema
            todos.append(problema.id)
    assert todos == []


def test_a_afirmacao_de_severidade_e_reconhecida():
    s = confere_banco.afirma_severidade
    assert s("Por que o compilador recusa a terceira linha?")
    assert s("Por que a segunda linha não compila?")
    assert s("Recusa: b não é modificável")
    assert not s("Por que o compilador reclama da segunda linha?")


@tem_gcc
def test_recusa_de_verdade_e_a_que_falha_ate_com_fpermissive():
    """`-fpermissive` rebaixa a aviso o que o gcc 14 passou a tratar como
    erro (e que antes era aviso). O que ainda falha com ela falha em
    qualquer gcc: atribuir a array, & de um número, nome não declarado."""
    assert confere_banco.falha_mesmo_permissivo('char s[10];\ns = "oi";')
    assert not confere_banco.falha_mesmo_permissivo(
        "int x = 42;\nint *p = &x;\nchar *c = p;")


@tem_gcc
def test_a_trilha_so_diz_recusa_onde_todo_gcc_recusa():
    """Em 18/11/2026, quatro questões da trilha diziam "recusa" ou "não
    compila" de conversões que um gcc anterior ao 14 só avisa; passaram a
    dizer "reclama", como manda `docs/linguagem.md`."""
    fora_da_regra = []
    for t in topicos():
        d = carrega(topico=t)
        arquivo = RAIZ / "dominio" / ("escada_%s.yaml" % t.replace("_", ""))
        fora = {i for e in trilha_escada.le(arquivo, d).values() for i in e.fora}
        for a in d.atividades:
            if a.id in fora or not a.codigo.strip():
                continue
            textos = [a.enunciado] + [o.texto for o in a.opcoes if o.correta]
            if (any(confere_banco.afirma_severidade(x) for x in textos)
                    and not confere_banco.falha_mesmo_permissivo(a.codigo)):
                fora_da_regra.append(a.id)
    assert fora_da_regra == []


@tem_gcc
def test_a_conferencia_acusa_uma_resposta_errada_de_proposito():
    """A versão antiga da t12, como ela era: a certa dizia 0, e sai 1."""
    from types import SimpleNamespace

    from mvp.dominio import Atividade, Opcao
    errada = Atividade(
        id="t12_antiga", no="kc12:I1", tipo="codigo", formato="prever_saida",
        enunciado="O que sai?",
        codigo=("int *f(void) { int n = 7; return &n; }\n"
                "void g(void) {\n    int *p = f();\n"
                "    printf(\"%d\\n\", p == NULL);\n}"),
        opcoes=(Opcao("0: p tem um endereço, mas ruim", correta=True),
                Opcao("0: p tem o 7 dentro"), Opcao("0: p aponta uma caixa viva")))
    problemas = confere_banco.confere(SimpleNamespace(atividades=[errada]))
    assert [(p.id, p.saiu) for p in problemas] == [("t12_antiga", "1")]
