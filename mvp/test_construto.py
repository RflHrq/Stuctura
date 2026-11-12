# -*- coding: utf-8 -*-
"""O detector de construtos: o que ele promete, e o que ele errava.

QUEM DEPENDE DISTO. O `CONSTRUTOS` de `mvp/conceitos.py` é a varredura
que decide, em três lugares, o que uma pessoa pode ver:

    conceitos.faltando          o portão `liberada` das cadeias de descida
    conceitos.faltando_para_exibir  o portão da prova na tela de refutação
    revisa_material             as 67 cobranças de construto não ensinado

Um falso positivo aqui bloqueia material correto; um falso negativo
mostra construto não ensinado a quem não o viu. Os dois são caros, e
nenhum dos dois era testado antes deste arquivo.

O DEFEITO QUE PEDIU O ARQUIVO, 11/11/2026. O padrão de
`funcao_com_parametro` acusava uma CHAMADA como se fosse uma
DEFINIÇÃO:

    puts(sizeof p > 0 ? "ocupa lugar" : "FALHOU");

`puts` casava como nome de função, `(` abria, e `sizeof p` casava como
"tipo seguido de nome de parâmetro". O programa não define função
nenhuma. Ele foi barrado do portão de exibição por um construto que não
usa, e eu só percebi porque reescrevi o programa até passar — que é o
jeito errado de lidar com um portão, e teria escondido o defeito.

O QUE SEPARA OS DOIS, e é a correção: uma DEFINIÇÃO tem tipo de retorno
E nome antes do parêntese — dois nomes. Uma CHAMADA tem um só.
"""
from __future__ import annotations

import pytest

from mvp.conceitos import construtos_de

DEFINE = (
    "int soma(int a, int b)\n{\n    return a + b;\n}\n",
    "static void poe(int *onde, int valor)\n{\n    *onde = valor;\n}\n",
    "static int igual(int *a, int *b)\n{\n    return a == b;\n}\n",
    "double media(double v[], int n);\n",
    "char *copia(char *destino, const char *origem)\n{\n    return destino;\n}\n",
)

NAO_DEFINE = (
    # a CHAMADA que era acusada, e as vizinhas dela
    '    puts(sizeof p > 0 ? "o ponteiro ocupa lugar" : "FALHOU");\n',
    '    puts(sizeof x > 0 ? "sim" : "nao");\n',
    "    int n = soma(a, b);\n",
    "    resultado = soma(a, b);\n",
    "int main(void)\n{\n    return 0;\n}\n",
    '    printf("%d\\n", x);\n',
    "    free(p);\n",
)


@pytest.mark.parametrize("codigo", DEFINE)
def test_definicao_de_funcao_com_parametro_e_acusada(codigo):
    """O verdadeiro positivo, primeiro.

    Sem este lado, a correção do falso positivo poderia ser "nunca
    acuse nada" — e passaria.
    """
    assert "funcao_com_parametro" in construtos_de(codigo), codigo


@pytest.mark.parametrize("codigo", NAO_DEFINE)
def test_chamada_de_funcao_nao_e_definicao(codigo):
    """E o falso positivo que motivou o arquivo."""
    assert "funcao_com_parametro" not in construtos_de(codigo), codigo


def test_o_montador_do_validador_nao_le_while_como_funcao():
    """O MESMO falso positivo, do outro lado do projeto.

    `revisa_material._monta` separa escopo de arquivo de statements
    para montar o programa que o oráculo compila, e usa `ASSINATURA`
    para isso. O padrão pedia UM nome antes do parêntese — e
    `while (n < 3) {` tem um nome antes do parêntese.

    O resultado era um cartão correto sendo REPROVADO: o `while` e o
    corpo dele subiam para o escopo de arquivo, e o gcc respondia
    `expected identifier or '(' before 'while'`. Visto no caso
    resolvido do `kc_10:I2`, que zera uma matriz com dois laços.

    Definição de função tem tipo E nome — dois nomes; `while`, `if` e
    `switch` têm um só. É a mesma distinção que consertou o detector de
    construtos em 11/11/2026, e ela estava corrigida num lado e não no
    outro.
    """
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve()
                           .parent.parent / "scripts"))
    from revisa_material import _monta

    prog = _monta(["int n = 0;\nwhile (n < 3) {\n    n = n + 1;\n}\n"])
    antes_do_main = prog.split("int main(void)")[0]
    assert "while" not in antes_do_main, prog
    assert "n = n + 1" not in antes_do_main, prog


def test_o_montador_poe_definicao_de_funcao_no_escopo_de_arquivo():
    """O verdadeiro positivo, para que a correção não vire 'nunca separe'."""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve()
                           .parent.parent / "scripts"))
    from revisa_material import _monta

    prog = _monta(["void f(int n) {\n    (void) n;\n}\n", "f(1);\n"])
    antes_do_main = prog.split("int main(void)")[0]
    assert "void f(int n)" in antes_do_main, prog


def test_main_sem_parametro_nunca_conta():
    """`int main(void)` aparece em todo programa, e não ensina nada."""
    for codigo in ("int main(void)\n{\n    return 0;\n}\n",
                   "int main(void) { return 0; }\n"):
        assert "funcao_com_parametro" not in construtos_de(codigo), codigo


# --------------------------------------------------------------------------
# Os outros construtos, que ninguém testava
# --------------------------------------------------------------------------

@pytest.mark.parametrize("codigo,esperado", [
    ("    int n = sizeof(x);\n", "sizeof"),
    ('    scanf("%d", &x);\n', "scanf"),
    ('    printf("%p\\n", (void *) p);\n', "printf_ponteiro"),
    ("    int **pp = &p;\n", "ponteiro_de_ponteiro"),
    ("    int v[3];\n", "array"),
    ("    if (&x == &y) { }\n", "comparacao_de_ponteiros"),
])
def test_cada_construto_reconhece_o_seu_caso(codigo, esperado):
    assert esperado in construtos_de(codigo), (codigo, construtos_de(codigo))


def test_o_que_comparacao_de_ponteiros_abrange_e_o_que_nao():
    """O nome é largo e a varredura é estreita, e isso está certo.

    O padrão exige `&` à esquerda: pega `&x == &y` e `&x == p`, e NÃO
    pega `p == &x`. Não é descuido — é o que o cartão `kc_02:B1` ensina,
    nessa forma e não na outra, e o comentário daquele nó registra que
    `p == &x` "fica fora" porque `p` é do B2.

    Se um dia a varredura passar a pegar `p == &x`, o cartão que a
    ensina deixa de cobrir o que ela acusa — e este teste é onde isso
    aparece.
    """
    assert "comparacao_de_ponteiros" in construtos_de("&x == &y")
    assert "comparacao_de_ponteiros" in construtos_de("&idade == outra")
    assert "comparacao_de_ponteiros" not in construtos_de("p == &x")
    assert "comparacao_de_ponteiros" not in construtos_de("x == y")


# --------------------------------------------------------------------------
# O inventário contra o material: quem diz que ensina, ensina?
# --------------------------------------------------------------------------

import pathlib  # noqa: E402

import yaml  # noqa: E402

from mvp.conceitos import CONSTRUTOS  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

INVENTARIO = yaml.safe_load(
    (pathlib.Path(__file__).resolve().parent / "dominio" / "conceitos.yaml")
    .read_text(encoding="utf-8"))["conceitos"]


def test_o_cartao_que_o_inventario_cita_realmente_traz_o_construto():
    """`evidencia.cartoes` é afirmação sobre o material, e é conferível.

    Dizer "`kc_02:B2` ensina `sizeof`" é dizer que o exemplo daquele
    cartão usa `sizeof`. Se não usar, o inventário libera um construto
    apontando para um cartão que não o mostra — e o portão passa a
    autorizar com base numa citação falsa, que é o mesmo defeito que a
    curadoria de crenças existe para impedir, noutro lugar.
    """
    padrao = dict((cid, p) for p, cid in CONSTRUTOS)
    fora = []
    for cid, e in sorted(INVENTARIO.items()):
        cartoes = ((e.get("evidencia") or {}).get("cartoes")
                   if isinstance(e.get("evidencia"), dict) else None) or []
        if cid not in padrao:
            continue
        for alvo in cartoes:
            topico, _, nid = str(alvo).partition(":")
            d = carrega(topico=topico)
            texto = (d.exemplo(nid) or "") + "\n" + (d.nos[nid].interpretacao or "")
            if not padrao[cid].search(texto):
                fora.append((cid, alvo))
    assert not fora, (
        "o inventário cita um cartão que não traz o construto: %s" % fora)


def test_o_material_do_b1_existe_e_a_decisao_de_liberar_e_que_nao():
    """Duas coisas que estavam no mesmo campo, e não são a mesma.

    A entrada do `comparacao_de_ponteiros` dizia *"nenhum cartão de
    ensino compara ponteiros"*. Isso foi verdade até 05/11/2026 —
    quando o cartão do `kc_02:B1` ganhou a ampliação que EXPLICA a
    comparação e um exemplo que a executa.

    EU LI AQUELE TEXTO FALSO E PROMOVI O CONCEITO, em 11/11/2026.
    Dezesseis testes caíram, e um deles disse por quê com todas as
    letras: *"a liberação é decisão à parte, depois da auditoria do
    conteúdo final. Escrever o cartão não é auditá-lo"*
    (`test_ampliar_o_b1_nao_mexe_no_inventario`). O texto estava
    esquecido; o `status` era uma decisão em aberto, segurada de
    propósito — e as duas coisas moravam na mesma entrada.

    O DONO PROMOVEU EM 12/11/2026, e a segunda metade deste teste caiu
    apontando para si mesma, como estava escrito que cairia. O que ela
    guarda agora é o outro lado da mesma separação: com a decisão
    tomada, a entrada tem de DECLARAR o cartão — porque é `cartoes` que
    o motor lê, e registro que fica para trás foi o defeito original
    desta entrada.
    """
    d = carrega(topico="kc_02")
    exemplo = d.exemplo("B1") or ""
    ampliacao = d.nos["B1"].interpretacao or ""
    padrao = next(p for p, c in CONSTRUTOS if c == "comparacao_de_ponteiros")
    assert padrao.search(exemplo), (
        "o exemplo do kc_02:B1 não compara endereços: %r" % exemplo)
    assert "==" in ampliacao and "endereço" in ampliacao.lower(), (
        "a ampliação do kc_02:B1 não explica a comparação")

    e = INVENTARIO["comparacao_de_ponteiros"]
    ev = e["evidencia"]
    assert e["status"] == "disponivel", (
        "o `comparacao_de_ponteiros` voltou a ficar segurado. Se a "
        "liberação foi desfeita, desfaça junto o `cartoes`, o `tipo` e os "
        "números de OPORTUNIDADES e TRAJETORIAS em test_arquitetura.py — "
        "os cinco andam juntos.")
    assert ev.get("cartoes") == ["kc_02:B1"], (
        "entrada liberada sem declarar o cartão: é `cartoes` que o motor "
        "lê, e foi registro ficando para trás que estragou esta entrada "
        "da primeira vez")
    assert "05/11/2026" in ev.get("aprovacao", "") or            "12/11/2026" in ev.get("aprovacao", ""), (
        "liberação sem registro de quando: a data é o que separa decisão "
        "de acidente")


# Pares (cartão, construto) em que o EXEMPLO do cartão usa um construto
# que o inventário não declara ensinado. Medido em 11/11/2026.
#
# É dívida, e é de duas naturezas diferentes:
#
#   `funcao_com_parametro`  usado em exemplo de 10 cartões, explicado em
#                           NENHUM. O kc_06 inteiro — que se chama
#                           "passagem por referência" — tem a ampliação
#                           VAZIA nos seis nós.
#   `ponteiro_de_ponteiro`  usado nos seis cartões do kc_10, `so_avaliado`
#   `printf_ponteiro`       usado no kc_03:B3, e nem entrada tem
#
# O NÚMERO FICA AQUI porque nomear a dívida é o que separa "ainda não
# fizemos" de "ninguém reparou". Baixá-lo exige ensinar o construto num
# cartão — não mexer no detector.
#
# CAIU DE 18 PARA 8 EM 12/11/2026, e a baixa é a prevista: os dez
# cartões que usavam `funcao_com_parametro` no exemplo saíram de uma vez
# quando o kc_06 ganhou material e o construto foi liberado, com
# `kc_06:B1` como evidência. Foi material novo, e não detector mexido.
#
# DE 8 PARA 7 NO MESMO DIA, com a assinatura do
# `comparacao_de_ponteiros`: aquele era o único dos oito a uma decisão
# de distância, e o cartão do `kc_02:B1` já o ensinava desde 05/11.
#
# E DE 7 PARA 1, ainda no mesmo dia, com os SEIS materiais do kc_10
# assinados: o `ponteiro_de_ponteiro` era a maior dívida que restava —
# os seis cartões daquele tópico usavam no exemplo o construto que dá
# nome a ele, e nenhum o explicava.
#
# E DE 1 PARA ZERO, com a troca do exemplo do `kc_03:B3`. Aquele era o
# último, e ele não saiu por material novo: saiu porque o exemplo que o
# usava estava errado por outro motivo. Ele era
#
#   int *p;
#   printf("%p\n", (void *)p);   /* o que estava ali antes */
#
# e LIA UM PONTEIRO NÃO INICIALIZADO — o comportamento indefinido de
# que a premissa daquele nó fala, demonstrado cometendo-o, na primeira
# coisa que a pessoa vê. O `%p` saiu junto.
#
# 18 -> 8 -> 7 -> 1 -> 0 em 12/11/2026. As três primeiras baixas vieram
# de material escrito e assinado; a última, de um exemplo consertado.
# Nenhuma veio de mexer no detector.
#
# ZERO NÃO É O FIM DA HISTÓRIA, e é bom dizer: o número conta cartões
# cujo EXEMPLO usa construto sem ensino. Item que cobra o que ninguém
# ensinou é outra conta, e está no `test_coerencia` — lá ainda há três,
# todos `scanf`.
USA_SEM_ENSINAR = 0


def test_quantos_cartoes_usam_construto_que_ninguem_ensina():
    pares = []
    for i in range(13):
        topico = "kc_%02d" % i
        d = carrega(topico=topico)
        for nid in d.ordem:
            ex = d.exemplo(nid) or ""
            for padrao, cid in CONSTRUTOS:
                if not padrao.search(ex):
                    continue
                e = INVENTARIO.get(cid) or {}
                if e.get("status") != "disponivel":
                    pares.append(("%s:%s" % (topico, nid), cid))
    assert len(pares) == USA_SEM_ENSINAR, (
        "mudou quantos cartões usam construto não ensinado: %d (a "
        "constante diz %d)\n%s" % (len(pares), USA_SEM_ENSINAR, sorted(pares)))
