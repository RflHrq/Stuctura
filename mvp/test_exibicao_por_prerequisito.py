"""O portão de exibição lê o grafo curricular: cartão de tópico ANTERIOR vale.

ATÉ 12/11/2026 o portão exigia cartão DO PRÓPRIO TÓPICO, e a razão
escrita nele era de ORDEM: "o `array` tem cartão no `kc_07:B1`, e isso
não ajuda quem está no kc_02: o tópico vem depois". A regra implementada
era mais severa que a própria justificativa — ela barrava também o que
foi ensinado ANTES.

Medido naquele dia: 93 evidências, 15 barradas, e 10 das 15 barradas por
construto com cartão em tópico que o grafo curricular declara como
pré-requisito. O grafo existe nos treze `topic_kcXX.yaml`, o
`test_arquitetura` o fixa, e nada o lia entre tópicos — "declaração sem
dente", nas palavras daquele teste.

A REGRA NOVA: um construto é exibível num tópico se tem cartão NELE ou
num tópico do FECHO dos pré-requisitos dele. As cinco que continuam
barradas são as que a justificativa original descreve: construto cujo
cartão está em tópico POSTERIOR, ou fora do caminho.

O QUE ESTA REGRA NÃO É, e fica dito: ela não sabe por onde UMA PESSOA
passou. Ela lê o currículo declarado, e uma coleta que roda um
subconjunto dos tópicos assume os pré-requisitos que pula — como já
assume nos itens. O último teste deste arquivo fixa quais evidências
liberadas dependem de tópico fora da sequência do piloto, para o fato
ficar visível em vez de implícito.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp import conceitos
from mvp.dominio import carrega, topicos

COM_SIZEOF = "int x = 0;\nprintf(\"%d\\n\", (int) sizeof(x));\n"
COM_ARRAY = "int v[3];\nv[0] = 1;\n"
COM_FUNCAO = "void f(int n) { n = 0; }\n"
COM_PP = "int x = 0;\nint *p = &x;\nint **pp = &p;\n"
COM_PRINTF_P = "int x = 0;\nprintf(\"%p\\n\", (void *) &x);\n"


# --------------------------------------------------------------------------
# O fecho
# --------------------------------------------------------------------------

def test_o_fecho_do_kc_11_e_o_que_o_grafo_declara():
    assert conceitos.anteriores("kc_11") == frozenset(
        {"kc_00", "kc_02", "kc_03", "kc_04", "kc_06", "kc_07"})


def test_a_raiz_nao_tem_anterior_nenhum():
    assert conceitos.anteriores("kc_00") == frozenset()


def test_o_fecho_e_transitivo():
    """kc_09 declara [kc_08, kc_06]; o kc_02 chega por dois níveis."""
    assert "kc_02" in conceitos.anteriores("kc_09")
    assert "kc_00" in conceitos.anteriores("kc_09")


def test_um_topico_nunca_e_anterior_a_si_mesmo():
    for t in topicos():
        assert t not in conceitos.anteriores(t), t


def test_ciclo_no_grafo_nao_trava_o_fecho(monkeypatch):
    """Grafo malformado não pode pendurar o portão: ele roda em toda tela."""
    falso = {"a": ("b",), "b": ("c",), "c": ("a",)}
    monkeypatch.setattr(conceitos, "_prerequisitos",
                        lambda t: falso.get(t, ()))
    assert conceitos.anteriores("a") == frozenset({"b", "c"})


# --------------------------------------------------------------------------
# A regra
# --------------------------------------------------------------------------

def test_construto_de_topico_anterior_passa():
    """`sizeof` é do kc_02 e `array` do kc_07: os dois antecedem o kc_11."""
    assert conceitos.faltando_para_exibir(COM_SIZEOF, "kc_11") == ()
    assert conceitos.faltando_para_exibir(COM_ARRAY, "kc_11") == ()
    assert conceitos.exibivel(COM_SIZEOF + COM_ARRAY, "kc_11")


def test_construto_do_proprio_topico_continua_passando():
    assert conceitos.faltando_para_exibir(COM_SIZEOF, "kc_02") == ()
    assert conceitos.faltando_para_exibir(COM_ARRAY, "kc_07") == ()


def test_construto_de_topico_posterior_continua_barrado():
    """A justificativa original do portão, que tem de continuar de pé.

    O kc_02 vem DEPOIS do kc_00, e o kc_07 depois do kc_02: quem está no
    tópico de trás ainda não viu o cartão do tópico da frente.
    """
    assert conceitos.faltando_para_exibir(COM_SIZEOF, "kc_00") == ("sizeof",)
    assert conceitos.faltando_para_exibir(COM_ARRAY, "kc_02") == ("array",)
    assert conceitos.faltando_para_exibir(COM_FUNCAO, "kc_02") == (
        "funcao_com_parametro",)


def test_construto_de_topico_fora_do_caminho_continua_barrado():
    """Ter cartão em ALGUM tópico não basta: tem de ser no caminho.

    O kc_10 não é pré-requisito do kc_09, e o kc_06 não é do kc_08.
    """
    assert "kc_10" not in conceitos.anteriores("kc_09")
    assert conceitos.faltando_para_exibir(COM_PP, "kc_09") == (
        "ponteiro_de_ponteiro",)
    assert "kc_06" not in conceitos.anteriores("kc_08")
    assert conceitos.faltando_para_exibir(COM_FUNCAO, "kc_08") == (
        "funcao_com_parametro",)


def test_construto_sem_cartao_continua_barrado_em_todo_lugar():
    """`printf` de ponteiro não tem cartão em tópico nenhum."""
    for t in topicos():
        assert conceitos.faltando_para_exibir(COM_PRINTF_P, t) == (
            "printf_ponteiro",), t


# --------------------------------------------------------------------------
# O efeito, medido e fixado
# --------------------------------------------------------------------------

def _barradas():
    fora = []
    for t in topicos():
        d = carrega(topico=t)
        for nid in d.ordem:
            for i, dem in enumerate(d.nos[nid].evidencia):
                if not conceitos.exibivel(dem.programa, t):
                    fora.append("%s:%s[%d]" % (t, nid, i))
    return fora


def test_as_que_continuam_barradas_sao_as_cinco_de_topico_posterior():
    """De 15 para 5, e as cinco são as que a regra deve barrar.

    O `kc_00:B2` pede `sizeof`, cujo cartão está no kc_02, que vem depois.
    As quatro do kc_02 pedem construto do kc_06, do kc_07 e do kc_10 —
    todos posteriores a ele. Se esta lista crescer, o portão voltou a
    barrar o que foi ensinado antes; se encolher, alguém ensinou o
    construto no lugar certo, e o número desce declarado.
    """
    assert _barradas() == [
        "kc_00:B2[0]",
        "kc_02:B1[0]", "kc_02:B2[0]", "kc_02:I2[0]", "kc_02:I3[0]",
    ]


# A sequência que a coleta roda. Ela é um SUBCONJUNTO do currículo, e por
# isso pula pré-requisitos que o grafo declara.
SEQUENCIA_DO_PILOTO = ("kc_02", "kc_07", "kc_11", "kc_09")


def test_o_que_o_piloto_exibe_apoiado_em_topico_que_ele_nao_roda():
    """O fato que a regra curricular não vê, posto à vista.

    O portão lê o currículo DECLARADO. A coleta roda quatro tópicos, e
    três evidências que ela passa a exibir usam função com parâmetro,
    cujo cartão é o `kc_06:B1` — pré-requisito declarado do kc_07 e do
    kc_09, e fora da sequência do piloto.

    Não é defeito da regra, e não é novidade: seis itens do kc_09 já
    cobram função com parâmetro de quem não passou pelo kc_06, e o
    cabeçalho do grafo do kc_09 registra que "quem montar a sessão da
    coleta precisa saber" da ordem. O que este teste faz é impedir que a
    lista cresça calada: se uma quarta evidência do piloto passar a
    depender de tópico fora da sequência, ele acusa.
    """
    dependem = []
    for pos, t in enumerate(SEQUENCIA_DO_PILOTO):
        vistos = set(SEQUENCIA_DO_PILOTO[:pos + 1])
        d = carrega(topico=t)
        for nid in d.ordem:
            for i, dem in enumerate(d.nos[nid].evidencia):
                if not conceitos.exibivel(dem.programa, t):
                    continue
                for cid in conceitos.construtos_de(dem.programa):
                    de = {str(c).split(":")[0] for c in conceitos.cartoes(cid)}
                    if not de & vistos:
                        dependem.append(("%s:%s[%d]" % (t, nid, i), cid,
                                         tuple(sorted(de))))
    assert dependem == [
        ("kc_07:I2[0]", "funcao_com_parametro", ("kc_06",)),
        ("kc_09:B2[0]", "funcao_com_parametro", ("kc_06",)),
        ("kc_09:I1[0]", "funcao_com_parametro", ("kc_06",)),
    ], dependem
