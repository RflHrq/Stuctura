# -*- coding: utf-8 -*-
"""A ampliação do B1: endereços se comparam.

A auditoria da cadeia liberada achou que ela exigia comparação de
endereços sem declarar e sem que o material ensinasse. A decisão do dono
foi que isso é conteúdo legítimo do kc_02 — o B1 já ensina que o
endereço IDENTIFICA um lugar, e identificar é exatamente o que permite
dizer se dois lugares são o mesmo — mas que ainda não estava ensinado.

AMPLIAÇÃO, não premissa nova: a afirmação do B1 não muda, a crença que
o nega não muda, nenhum nó entra no grafo. Mesma forma do B3.

O QUE ESTE CARTÃO ENSINA E O QUE NÃO ENSINA, e o limite é técnico:

    &idade == &outra    compila limpo, dá 0        <- ensinado aqui
    &idade == &idade    AVISA (self-comparison)    <- não entra
    p == &x             limpo, mas p é do B2       <- não entra aqui
    &p == &x            AVISA (tipos distintos)    <- não entra em lugar nenhum

A metade "mesmo lugar" exige dois nomes para o mesmo lugar, e o único
jeito sem ponteiro é comparar um endereço consigo mesmo — que o gcc
acusa. Então o cartão AFIRMA que endereços iguais são o mesmo lugar e
DEMONSTRA o caso diferente. Afirmar sem demonstrar é menos do que o
ideal, e é melhor que demonstrar com um exemplo que avisa.

NÃO ANTECIPA O B2: nenhum ponteiro aparece. Pôr `int *p` aqui seria
antecipar o cartão seguinte, que é o erro que esta auditoria inteira
existe para pegar.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

from mvp import conceitos, motor
from mvp.dominio import carrega

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import oraculo  # noqa: E402

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


# --------------------------------------------------------------------------
# A premissa não mudou
# --------------------------------------------------------------------------

def test_o_b1_continua_sendo_a_mesma_premissa(d):
    assert d.nos["B1"].texto == (
        "Cada lugar da memória tem um número que o identifica: o endereço.")
    assert d.nos["B1"].negado_por == ("memory_is_by_name",)
    assert d.nos["B1"].suporte == ()
    assert len(d.nos) == 6 and len(d.crencas) == 6


def test_a_frase_canonica_do_b1_nao_inchou(d):
    """`simples` é alternativa de resposta na camada 2: a ampliação vai
    em `interpretation`, nunca ali."""
    assert len(d.nos["B1"].simples.strip()) < 200


# --------------------------------------------------------------------------
# O que a ampliação ensina
# --------------------------------------------------------------------------

def test_o_b1_ganhou_interpretacao(d):
    assert d.interpretacao("B1"), "a ampliação não chegou ao domínio"


def test_a_interpretacao_ensina_a_comparar_enderecos(d):
    t = d.interpretacao("B1")
    assert "==" in t, t
    assert "mesmo lugar" in t.lower(), t
    assert "lugares diferentes" in t.lower(), t


def test_a_interpretacao_diz_o_que_o_resultado_significa(d):
    """Comparar sem saber ler o resultado não ensina nada: 1 e 0 têm de
    aparecer com o significado ao lado."""
    t = d.interpretacao("B1")
    assert re.search(r"\b1\b", t) and re.search(r"\b0\b", t), t


def test_o_exemplo_do_b1_compara_dois_enderecos(d):
    codigo = d.exemplo("B1")
    sem_comentario = re.sub(r"/\*.*?\*/", " ", codigo, flags=re.S)
    assert "==" in sem_comentario, codigo


# --------------------------------------------------------------------------
# O LIMITE: não antecipa o B2, e não entra exemplo que avisa
# --------------------------------------------------------------------------

def test_o_b1_nao_usa_ponteiro(d):
    """Ponteiro é o B2. Pôr `int *p` aqui seria antecipar o cartão
    seguinte — o erro que esta auditoria existe para pegar."""
    tudo = (d.interpretacao("B1") or "") + " " + d.exemplo("B1")
    assert not re.search(r"int\s*\*|\bponteiro\b|\*\s*p\b", tudo), tudo


def test_o_b1_nao_compara_um_endereco_consigo_mesmo(d):
    """`&idade == &idade` compila com aviso de self-comparison. Material
    de ensino que produz aviso é material que o aluno copia e vê o
    aviso."""
    codigo = d.exemplo("B1")
    for m in re.finditer(r"&\s*(\w+)\s*==\s*&\s*(\w+)", codigo):
        assert m.group(1) != m.group(2), m.group(0)


@tem_gcc
def test_o_exemplo_do_b1_compila_SEM_AVISO_e_sai_o_prometido(d):
    """O portão que o B3 não teve e devia ter tido.

    `-Wall -Wextra` e **stderr vazio**. Exemplo de ensino que compila
    com aviso é exemplo que o aluno copia e vê o aviso — e foi
    exatamente o aviso de self-comparison que decidiu o que este cartão
    pode demonstrar.

    Conferido por sabotagem: trocando a comparação pelo caso que avisa,
    este teste cai com a mensagem do gcc.
    """
    prog = ("#include <stdio.h>\nint main(void) {\n"
            + "\n".join("    " + l for l in d.exemplo("B1").splitlines())
            + "\n    return 0;\n}\n")
    # O GCC É CHAMADO DIRETO, e não pelo oráculo.
    #
    # A primeira versão deste teste usava `oraculo.roda` e cobrava que a
    # nota não contivesse "warning". Era VAZIA: o oráculo só traz a
    # mensagem do compilador quando a compilação FALHA — num programa
    # que compila com aviso ele devolve a saída e cala. A asserção
    # passaria para sempre, inclusive no exemplo com self-comparison que
    # este cartão existe para não usar.
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        fonte = pathlib.Path(tmp) / "b1.c"
        fonte.write_text(prog, encoding="utf-8")
        r = subprocess.run(
            [str(oraculo.GCC), "-std=c17", "-Wall", "-Wextra",
             "-o", str(pathlib.Path(tmp) / "b1.exe"), str(fonte)],
            capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        assert r.stderr.strip() == "", (
            "o exemplo do cartão compila com aviso:\n" + r.stderr)
        saida = subprocess.run([str(pathlib.Path(tmp) / "b1.exe")],
                               capture_output=True, text=True, timeout=30)

    # A primeira linha é um endereço e muda a cada execução; o que se
    # cobra é o que é determinístico.
    linhas = saida.stdout.split()
    assert linhas[-2:] == ["20", "0"], saida.stdout


# --------------------------------------------------------------------------
# E NÃO libera cadeia nenhuma
# --------------------------------------------------------------------------

def test_liberar_o_b1_foi_decisao_separada_de_escrever_o_cartao():
    """A liberação é decisão à parte, depois da auditoria do conteúdo
    final. Escrever o cartão não é auditá-lo — foi assim no B3 e foi
    assim aqui.

    ESTE TESTE AFIRMAVA `so_avaliado` ATÉ 12/11/2026, e mudar hoje é o
    trabalho dele. O material estava escrito desde 05/11; o que faltava
    era a decisão, e o dono a tomou.

    O QUE ELE GUARDA AGORA é que a decisão foi tomada INTEIRA. Os três
    campos andam juntos — `status`, `evidencia.cartoes` e
    `evidencia.tipo` —, e a entrada registra a aprovação com data. Em
    11/11/2026 eu mexi só no `status`, sem autoridade e sem os outros
    dois, e dezesseis testes caíram dizendo isso de dezesseis maneiras.
    """
    cru = conceitos.carrega()["comparacao_de_ponteiros"]
    assert conceitos.status("comparacao_de_ponteiros") == conceitos.DISPONIVEL
    assert conceitos.cartoes("comparacao_de_ponteiros") == ("kc_02:B1",)
    assert cru["evidencia"]["tipo"] == "explicacao_com_exemplo"
    assert "12/11/2026" in cru["evidencia"].get("aprovacao", ""), (
        "promoção sem registro de aprovação: a data é o que separa "
        "decisão de acidente")
    assert "pendente" not in cru["evidencia"], (
        "a decisão foi tomada e o campo que a chamava de pendente ficou")


def test_as_cadeias_liberadas_continuam_sem_rodar(d):
    """O inventário abriu três cadeias, e o portão pedagógico as segura.

    AFIRMAVA QUE NENHUMA ESTAVA LIBERADA, e deixou de valer em
    12/11/2026 — duas vezes no mesmo dia. Primeiro o
    `comparacao_de_ponteiros` abriu a `pointer_is_data` e a
    `pointer_and_target_are_one`; depois o `ponteiro_de_ponteiro`, com
    os seis materiais do kc_10, abriu a `pointer_has_no_address`.

    E NENHUMA DAS DUAS RODA, que é o que importa para quem usa o
    sistema. São DUAS autorizações independentes, e `Dominio.descida`
    exige as duas: `liberada` diz que o currículo ensinou o que a cadeia
    precisa, `aprovada` diz que ALGUÉM revisou aquela sequência. A
    `pointer_and_target_are_one` está reprovada e a `pointer_is_data`
    está em revisão.

    O comentário de `Dominio.descida` previu este dia com todas as
    letras: "liberar `comparacao_de_ponteiros` abriria duas cadeias de
    uma vez, e uma delas reprova em três das cinco perguntas da
    revisão".
    """
    liberadas = sorted(c for c, de in d.descidas.items() if de.liberada)
    assert liberadas == ["pointer_and_target_are_one",
                         "pointer_has_no_address", "pointer_is_data"],         liberadas
    for c in liberadas:
        assert d.descida(c) is None, (
            "a cadeia %s passou os dois portões e vai RODAR para o "
            "participante — se é isso que se quer, é outra decisão" % c)
