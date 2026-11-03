"""O oráculo: o compilador como juiz do molde.

Estes testes rodam um compilador de verdade. Onde não houver um, eles
são PULADOS e dizem isso — um molde não conferido não pode sair igual a
um molde aprovado, nem no relatório nem aqui.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import oraculo  # noqa: E402

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)

CONTA = """#include <stdio.h>
int main(void) {
    int a[5];
    printf("%zu\\n", sizeof a / sizeof a[0]);
    return 0;
}
"""


@tem_gcc
def test_o_que_imprime_o_esperado_passa():
    ok, nota = oraculo.roda(CONTA, "5")
    assert ok, nota


@tem_gcc
def test_o_que_imprime_outra_coisa_reprova():
    """A nota diz as duas coisas: quem conserta o molde precisa saber o
    que saiu E o que o molde prometia."""
    ok, nota = oraculo.roda(CONTA, "20")
    assert not ok
    assert "'5'" in nota and "'20'" in nota, nota


@tem_gcc
def test_o_que_nao_compila_reprova_com_a_fala_do_compilador():
    ok, nota = oraculo.roda("int main(void) { return x; }", "0")
    assert not ok
    assert "não compilou" in nota
    assert "x" in nota, nota


@tem_gcc
def test_programa_que_nao_termina_e_cortado():
    """Foco 4: oráculo que pendura o gerador não confere nada."""
    ok, nota = oraculo.roda("int main(void) { for (;;) ; }", "0", timeout=2)
    assert not ok
    assert "não terminou" in nota, nota


def test_sem_compilador_a_mensagem_diz_onde_procurou(tmp_path):
    """Foco 3: molde não conferido não é molde reprovado.

    Por isso é exceção, e não `(False, nota)`: os dois não podem sair
    iguais no relatório da expansão.
    """
    with pytest.raises(oraculo.SemCompilador) as erro:
        oraculo.roda(CONTA, "5", gcc=tmp_path / "nao" / "existe" / "gcc.exe")
    assert "nao" in str(erro.value) and "STRUCTURA_GCC" in str(erro.value)


@tem_gcc
def test_o_caminho_do_compilador_vem_do_ambiente(monkeypatch):
    """A máquina da coleta não precisa ter a instalação desta."""
    import importlib
    monkeypatch.setenv("STRUCTURA_GCC", str(oraculo.GCC))
    recarregado = importlib.reload(oraculo)
    try:
        assert recarregado.GCC == oraculo.GCC
    finally:
        monkeypatch.delenv("STRUCTURA_GCC", raising=False)
        importlib.reload(oraculo)


@tem_gcc
def test_a_compilacao_tambem_tem_timeout():
    """A restrição global do plano diz: todo programa do oráculo roda com
    timeout. A execução tinha; a compilação, não."""
    import inspect
    fonte = inspect.getsource(oraculo.roda)
    compila = fonte[fonte.index("compilou = subprocess.run"):]
    assert "timeout=" in compila[:compila.index(")\n")], compila[:300]


# --------------------------------------------------------------------------
# O oráculo que espera a RECUSA
# --------------------------------------------------------------------------

@tem_gcc
def test_nao_compila_passa_quando_o_compilador_recusa():
    """Em `achar_o_erro`, o que se prova é o contrário: que não compila."""
    ok, nota = oraculo.roda("int main(void){int a[5];int *p;a=p;return 0;}",
                            "", nao_compila=True)
    assert ok, nota
    assert "error:" in nota, nota          # a nota traz a fala do compilador


@tem_gcc
def test_nao_compila_reprova_quando_o_programa_compila():
    """Foco 3: um "ache o erro" num programa que compila é item sem erro."""
    ok, nota = oraculo.roda("int main(void){return 0;}", "", nao_compila=True)
    assert not ok
    assert "compilou sem reclamação" in nota, nota
