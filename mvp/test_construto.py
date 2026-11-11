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

    Este teste guarda a separação: o MATERIAL tem de existir, e o
    `status` tem de continuar segurado enquanto ninguém auditar. Se o
    dono promover, a segunda metade cai e aponta para si mesma.
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
    assert e["status"] == "so_avaliado", (
        "o `comparacao_de_ponteiros` saiu de `so_avaliado`. Se foi o dono "
        "promovendo depois de auditar, atualize este teste, o "
        "`test_ampliar_o_b1_nao_mexe_no_inventario`, e os números de "
        "OPORTUNIDADES e TRAJETORIAS em test_arquitetura.py — a lista está "
        "no campo `pendente` da entrada.")
    assert not ev.get("cartoes"), (
        "entrada segurada não declara cartão: é `cartoes` que libera")
    assert ev.get("pendente"), (
        "a entrada segura o conceito e não diz o que falta para soltá-lo")


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
# CAI PARA 17 no dia em que o `comparacao_de_ponteiros` for promovido:
# o cartão do `kc_02:B1` já o ensina, e o que segura é a decisão, não o
# material. Esse é o único dos dezoito que está a uma assinatura de
# distância; os outros dezessete precisam de material que não existe.
USA_SEM_ENSINAR = 18


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
