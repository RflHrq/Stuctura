# -*- coding: utf-8 -*-
"""A mesma crença tem a mesma procedência em todo tópico.

A OCORRÊNCIA QUE PEDIU ESTE ARQUIVO, 11/11/2026. Catorze crenças
aparecem em mais de um tópico, e **cada cópia tem o seu próprio campo de
fonte**, escrito à mão. Elas derivaram:

    no_value_no_memory   `L` no kc_00, `D` no kc_03
    declaration_zeroes   `L` no kc_00, `D` no kc_03
    memory_is_uniform    `T` no kc_12, `E` no kc_01

E o kc_03 estava CERTO nos dois primeiros — citava "Sorva (2012), p. 360,
item 22", com página e item —, enquanto o kc_00 citava o estudo original
sem mediação. O trabalho já tinha sido feito num tópico e não foi
propagado ao outro.

POR QUE A GRADE NÃO PODE DIVERGIR, e o texto pode. A grade é afirmação
sobre a LITERATURA: ou a concepção está documentada com fonte e posição,
ou é obra técnica, ou é transposição declarada, ou é hipótese. Isso não
depende do tópico em que a crença é usada. Se ela é `D` no kc_03 e `L` no
kc_00, uma das duas afirmações é falsa — e num trabalho acadêmico isso é
a diferença entre citar e alegar.

O TEXTO da fonte, ao contrário, PODE e deve diferir: cada tópico
contextualiza o que aquela crença nega ali. Os catorze divergem no texto,
e está certo que divirjam.
"""
from __future__ import annotations

import collections
import pathlib
import unicodedata

import pytest
import yaml

DOMINIO = pathlib.Path(__file__).resolve().parent / "dominio"
PILOTOS = ("kc_02", "kc_07", "kc_09", "kc_11")


def _catalogo():
    """{id: [(tópico, grade, fonte)]}, lido dos YAMLs."""
    fora = collections.defaultdict(list)
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        topico = "kc_" + p.stem[len("beliefs_kc"):]
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            fora[b["id"]].append((topico, b.get("provenance"),
                                  " ".join((b.get("source") or "").split())))
    return dict(fora)


@pytest.fixture(scope="module")
def catalogo():
    return _catalogo()


def test_catorze_crencas_vivem_em_mais_de_um_topico(catalogo):
    """Sem isto o teste abaixo ficaria vazio e passaria sozinho."""
    repetidas = {k: v for k, v in catalogo.items() if len(v) > 1}
    assert len(repetidas) == 14, sorted(repetidas)


def test_a_grade_nao_diverge_entre_topicos(catalogo):
    """A trava. Grade é afirmação sobre a literatura, e não sobre o uso."""
    fora = []
    for cid, ocor in sorted(catalogo.items()):
        grades = {g for _, g, _ in ocor}
        if len(grades) > 1:
            fora.append((cid, [(t, g) for t, g, _ in ocor]))
    assert not fora, (
        "a mesma crença tem grades diferentes em tópicos diferentes: %s\n"
        "Uma das afirmações é falsa. Decida qual fonte vale e alinhe as "
        "cópias — não escolha a mais generosa." % fora)


# Crenças cujo RÓTULO muda de tópico para tópico. Medido em 11/11/2026,
# e são DUAS coisas diferentes:
#
#   instanciado  a cauda da frase é do tópico, o tronco é o mesmo. É
#                desenho, e está explicado no teste abaixo.
#   só o acento  a mesma frase, uma cópia sem acento. O
#                `beliefs_kc00.yaml` é escrito sem acento do começo ao
#                fim, de uma era anterior do projeto — então a diferença
#                é de transcrição, não de conteúdo, e normalizá-la é
#                limpar aquele arquivo inteiro, não uma linha.
ROTULO_INSTANCIADO = ("ampersand_copies", "declaration_zeroes",
                      "pointer_is_data", "pointer_is_just_a_name",
                      "pointer_knows_block_size")
ROTULO_SO_ACENTO = ("no_value_no_memory",)


def test_o_rotulo_e_instanciado_por_topico_e_isso_e_deliberado():
    """CINCO crenças dizem a mesma coisa com a cauda do tópico.

    A primeira versão deste teste PROIBIA isso, e caiu — e a premissa
    dela estava errada. O padrão é visível no `pointer_is_data`: o tronco
    é idêntico e a cauda é do tópico.

        kc_02, kc_04  "...o que está dentro dele é o valor, não o endereço"
        kc_08         "...o que malloc devolve é o bloco, não o endereço"
        kc_12         "...retornar &local devolve a variável"

    Uma crença, instanciada nos termos de cada tópico. Não é deriva.

    E ISSO TEM CONSEQUÊNCIA PARA A TESE, que precisa ficar declarada: o
    reteste entre contextos compara a resposta da pessoa a **frases
    diferentes** sob um id só. Isso não enfraquece a medida — argumenta
    a favor dela. Transferência é reconhecer o mesmo erro num contexto
    OUTRO; se a frase fosse idêntica, o que se mediria era reconhecimento
    de frase.

    O que o teste guarda é o NÚMERO: rótulo novo que divirja entra
    declarado, e não de contrabando.
    """
    rotulos = collections.defaultdict(set)
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            rotulos[b["id"]].add(" ".join((b.get("label_pt") or "").split()))
    def sem_acento(s):
        return "".join(c for c in unicodedata.normalize("NFD", s)
                       if unicodedata.category(c) != "Mn").lower()

    instanciado, so_acento = [], []
    for cid, vs in sorted(rotulos.items()):
        if len(vs) < 2:
            continue
        (so_acento if len({sem_acento(v) for v in vs}) == 1
         else instanciado).append(cid)
    assert tuple(instanciado) == ROTULO_INSTANCIADO, (
        "mudou quais crenças têm rótulo instanciado por tópico.\n"
        "  agora: %s\n  antes: %s\n"
        "Se é instanciação deliberada, acrescente à lista. Se é deriva, "
        "alinhe as cópias." % (tuple(instanciado), ROTULO_INSTANCIADO))
    assert tuple(so_acento) == ROTULO_SO_ACENTO, (
        "mudou quais divergem só por acento: %s" % (tuple(so_acento),))


def test_o_tronco_do_rotulo_instanciado_e_o_mesmo():
    """E a instanciação muda a CAUDA, não a afirmação.

    É o que separa instanciar de derivar: as primeiras palavras — o que
    a crença afirma — têm de ser as mesmas. Se mudar o tronco, são duas
    crenças com um nome.
    """
    rotulos = collections.defaultdict(list)
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            rotulos[b["id"]].append(" ".join((b.get("label_pt") or "").split()))
    fora = []
    for cid in ("pointer_is_data", "pointer_is_just_a_name",
                "ampersand_copies"):
        troncos = {v.split(":")[0].strip() if ":" in v else v[:34]
                   for v in rotulos[cid]}
        if len(troncos) > 1:
            fora.append((cid, sorted(troncos)))
    assert not fora, (
        "o tronco do rótulo mudou, e não só a cauda: %s" % fora)


def test_a_fonte_pode_divergir_e_diverge(catalogo):
    """O contrário do teste acima, e de propósito.

    Cada tópico contextualiza o que aquela crença nega ali, e o campo de
    fonte carrega isso. Exigir texto idêntico mataria a contextualização
    — e foi justamente lendo esses textos diferentes que a divergência de
    GRADE apareceu.
    """
    divergem = [cid for cid, ocor in catalogo.items()
                if len(ocor) > 1 and len({s for _, _, s in ocor}) > 1]
    assert len(divergem) == 14, sorted(divergem)


# --------------------------------------------------------------------------
# O que uma grade afirma, e o que ela exige
# --------------------------------------------------------------------------

def test_toda_grade_D_cita_posicao(catalogo):
    """`D` é "documentada com fonte E POSIÇÃO". Sem página ou item, é `L`."""
    import re

    fora = []
    for cid, ocor in sorted(catalogo.items()):
        for topico, grade, fonte in ocor:
            if grade != "D":
                continue
            if not re.search(r"\bp\.\s*\d|\bpp\.\s*\d|\bitem\s+\d", fonte):
                fora.append((cid, topico))
    assert not fora, (
        "crença `D` sem página nem item na fonte: %s. `D` afirma posição "
        "localizável; sem ela a grade é `L`." % fora)


def test_toda_grade_E_diz_que_e_hipotese(catalogo):
    """`E` só vale declarada como tal — é a regra do `docs/linguagem.md`.

    Uma `E` que não se anuncia é uma invenção com cara de achado, e é
    exatamente o que a grade existe para impedir.
    """
    fora = []
    for cid, ocor in sorted(catalogo.items()):
        for topico, grade, fonte in ocor:
            if grade != "E":
                continue
            if "HIPÓTESE" not in fonte.upper() and "HIPOTESE" not in fonte.upper():
                fora.append((cid, topico))
    assert not fora, (
        "crença `E` que não se declara hipótese na fonte: %s" % fora)


def test_as_tres_hipoteses_estao_fora_do_piloto(catalogo):
    """As `E` existem, e nenhuma em tópico que vai para a coleta.

    Duplica de propósito o `test_piloto_nao_tem_crenca_estimada`, por
    outro caminho: aquele carrega o domínio, este lê o YAML. Em
    11/11/2026 a `memory_is_uniform` desceu para `E` e aparece em kc_01 e
    kc_12 — se algum dia ela entrar num piloto, os dois caem.
    """
    estimadas = {cid: [t for t, g, _ in ocor if g == "E"]
                 for cid, ocor in catalogo.items()
                 if any(g == "E" for _, g, _ in ocor)}
    assert len(estimadas) == 3, sorted(estimadas)
    for cid, topicos in sorted(estimadas.items()):
        for t in topicos:
            assert t not in PILOTOS, (cid, t)


def test_toda_crenca_tem_grade_conhecida(catalogo):
    for cid, ocor in sorted(catalogo.items()):
        for topico, grade, _ in ocor:
            assert grade in ("D", "L", "T", "N", "E"), (cid, topico, grade)
