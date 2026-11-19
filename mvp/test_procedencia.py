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
#
# VAZIA DESDE 12/11/2026. A unica era `no_value_no_memory`, e a causa
# era a que o comentario acima descreve: o `beliefs_kc00.yaml` escrito
# sem acento. A limpeza "daquele arquivo inteiro" foi feita naquele
# dia, na passada de acentos do kc_00, e as copias ficaram iguais.
ROTULO_SO_ACENTO = ()


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


# --------------------------------------------------------------------------
# O documento não pode dizer "conferida" sobre uma busca que falhou
# --------------------------------------------------------------------------

CURADORIA = (pathlib.Path(__file__).resolve().parent.parent
             / "docs" / "curadoria-crencas.md")


def _sem_item():
    """{id: nota}, das crenças que DECLARAM que a busca não achou item.

    O campo é `sem_item`, e existe porque prosa não serve de marcador. A
    `pointer_has_no_address` e a `array_confused_with_cell` também
    contam, no corpo da fonte, uma busca que falhou — só que a delas
    falhou ANTES, e o item foi achado depois. Procurar por "PROCUREI" ou
    "não está lá" no texto confundiria as duas coisas, e o gerador
    precisa saber a diferença sem interpretar português.
    """
    fora = {}
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            if b.get("sem_item"):
                fora[b["id"]] = " ".join(str(b["sem_item"]).split())
    return fora


def test_a_crenca_sem_item_declara_onde_procurou():
    """O campo não é um sinalizador: ele carrega o que a busca fez.

    Sem isso, `sem_item: true` seria um jeito curto de dizer "não achei"
    e de nunca contar onde se procurou — e a próxima pessoa refaria a
    mesma busca com o mesmo vocabulário.
    """
    declaradas = _sem_item()
    assert declaradas, (
        "nenhuma crença declara `sem_item`. Se nenhuma busca falhou, "
        "apague este teste; se alguma falhou, declare.")
    for cid, nota in sorted(declaradas.items()):
        assert len(nota) >= 80, (cid, "a nota é curta demais para dizer "
                                 "onde se procurou: %r" % nota)


def test_o_documento_nao_diz_conferida_de_busca_que_falhou():
    """A TRAVA, e ela nasceu de um defeito real.

    A `heap_dies_with_function` não cita obra nenhuma: o que ela tem é a
    analogia com Java e Python, declarada. Em 11/11/2026 a busca foi
    refeita pelo vocabulário do fenômeno e registrada no campo de fonte
    — e essa nota CITA, entre aspas, a frase do item 5 do Sorva, que é o
    mais próximo que existe e não é a crença.

    O classificador do gerador então procurou a frase no texto integral,
    achou, e escreveu **"conferida — texto integral do Sorva"** na linha
    dela. O documento passou a afirmar conferência de uma citação que o
    próprio campo de fonte diz não existir.

    Um gerador que não sabe distinguir uma citação de um achado negativo
    não é auditor: é um amplificador de erro com cara de tabela.
    """
    doc = CURADORIA.read_text(encoding="utf-8")
    linhas = {}
    for ln in doc.splitlines():
        if ln.startswith("| `") and ln.count("|") >= 7:
            partes = [c.strip() for c in ln.strip("|").split("|")]
            linhas[partes[0].strip("`")] = partes[-1]

    fora = []
    for cid in sorted(_sem_item()):
        conf = linhas.get(cid)
        assert conf is not None, (
            "a crença %s não tem linha na tabela de %s" % (cid, CURADORIA.name))
        if "conferida" in conf and "não conferida" not in conf:
            fora.append((cid, conf))
    assert not fora, (
        "a curadoria diz 'conferida' para crença que declara `sem_item`: "
        "%s\nA frase entre aspas na nota é o que NÃO foi achado, e o "
        "gerador a leu como fonte." % fora)


def test_o_sem_item_nao_fica_numa_copia_so(catalogo):
    """Mesmo defeito da grade, numa chave nova.

    O `sem_item` entrou em 11/11/2026 e a primeira versao dele ficou no
    `beliefs_kc01.yaml` e nao no `kc_12`, que tem a mesma crenca. Como a
    curadoria deduplica por id, o documento sairia certo e o catalogo
    ficaria divergente — que foi exatamente como as tres grades
    divergiram sem ninguem notar.
    """
    declarado = collections.defaultdict(set)
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        topico = "kc_" + p.stem[len("beliefs_kc"):]
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            declarado[b["id"]].add((topico, bool(b.get("sem_item"))))
    fora = []
    for cid, ocor in sorted(declarado.items()):
        if len({tem for _, tem in ocor}) > 1:
            fora.append((cid, sorted(ocor)))
    assert not fora, (
        "a crença declara `sem_item` em um tópico e não no outro: %s\n"
        "A busca que falhou falhou para a crença, não para o tópico." % fora)


# As crenças `D` cuja citação traz frase entre aspas do Apêndice A do
# Sorva. Medido em 11/11/2026. Elas existem para cobrar do GERADOR que
# reconheça a frase: a curadoria é escrita por um programa, e um
# programa que não vê a frase escreve "citada sem frase entre aspas"
# numa linha que tem a frase. O documento então subestima o próprio
# rigor, que é um erro mais silencioso que superestimar.
D_COM_FRASE = ("array_confused_with_cell", "assignment_symmetric",
               "declaration_zeroes", "memory_is_by_name",
               "no_value_no_memory")


def test_a_curadoria_reconhece_a_frase_das_crencas_D():
    """O `assignment_symmetric` foi o caso.

    A citação dela passou a trazer *"Primitive assignment works both
    directions (swaps)"* — item 12, p. 359, localizado no texto
    integral. O gerador continuou dizendo "citada sem frase entre
    aspas", porque o filtro de frase inglesa exigia uma palavra de uma
    lista curta — the, is, are, of, that, not, a, an — e aquela frase
    não tem nenhuma delas.

    Um filtro de inglês que recusa inglês não é conservador: ele faz o
    documento descrever o catálogo pior do que ele é.
    """
    doc = CURADORIA.read_text(encoding="utf-8")
    linhas = {}
    for ln in doc.splitlines():
        if ln.startswith("| `") and ln.count("|") >= 7:
            partes = [c.strip() for c in ln.strip("|").split("|")]
            linhas[partes[0].strip("`")] = partes[-1]
    fora = [(cid, linhas.get(cid)) for cid in D_COM_FRASE
            if "conferida** — texto integral do Sorva" not in (linhas.get(cid) or "")]
    assert not fora, (
        "crença `D` com frase entre aspas que a curadoria não reconheceu "
        "como conferida: %s" % fora)


# --------------------------------------------------------------------------
# O capítulo da monografia não pode divergir do catálogo
# --------------------------------------------------------------------------

CAPITULO = (pathlib.Path(__file__).resolve().parent.parent
            / "docs" / "monografia" / "curadoria.md")

# Os números que o capítulo afirma, e de onde cada um tem de sair. É a
# mesma regra que o projeto aplicou ao apêndice: número digitado à mão
# diverge do dado, e divergiu três vezes só nesta auditoria. A diferença
# é que o apêndice é GERADO e o capítulo é escrito — então o que prende
# o capítulo é este teste.
AFIRMA_O_CAPITULO = {
    "concepções distintas no catálogo | **61**": lambda c: c["total"] == 61,
    "conferidas na obra primária | **53**": lambda c: c["conferidas"] == 53,
    "`D` 6, `L` 33, `T` 16, `N` 3, `E` 3": lambda c: c["grades"] == {
        "D": 6, "L": 33, "T": 16, "N": 3, "E": 3},
    "Classe 1: literatura de concepções errôneas (23 concepções)":
        lambda c: c["classe1"] == 23,
    "Classe 2: corpus de praticante (34 concepções)":
        lambda c: c["classe2"] == 34,
    "hipóteses `E` | **3**": lambda c: c["grades"]["E"] == 3,
    "Quatorze concepções aparecem em mais de um tópico": lambda c: c["em_dois_topicos"] == 14,
}


@pytest.fixture(scope="module")
def contagens(catalogo):
    doc = CURADORIA.read_text(encoding="utf-8")
    conf = collections.Counter()
    cls = collections.Counter()
    for ln in doc.splitlines():
        if ln.startswith("| `") and ln.count("|") >= 7:
            p = [x.strip() for x in ln.strip("|").split("|")]
            conf[p[-1].replace("**", "")] += 1
            cls[p[3].replace("**", "")] += 1
    grades = collections.Counter()
    for ocor in catalogo.values():
        grades[ocor[0][1]] += 1
    return {
        "total": len(catalogo),
        "conferidas": sum(v for k, v in conf.items() if k.startswith("conferida")),
        "grades": dict(grades),
        "classe1": cls["1 · concepção estudada"],
        "classe2": cls["2 · corpus de praticante"],
        "em_dois_topicos": sum(1 for o in catalogo.values() if len(o) > 1),
    }


def test_o_capitulo_existe_e_afirma_o_que_o_catalogo_diz(contagens):
    """Cada número do capítulo, conferido contra o catálogo.

    A chave do dicionário é o TRECHO LITERAL do capítulo; o valor é a
    conta que o sustenta. Se o catálogo mudar, este teste cai e aponta a
    frase a reescrever — o que é a única defesa possível contra um
    capítulo que envelhece sem avisar.
    """
    assert CAPITULO.exists(), CAPITULO
    texto = CAPITULO.read_text(encoding="utf-8")
    fora = []
    for trecho, confere in AFIRMA_O_CAPITULO.items():
        if trecho not in texto:
            fora.append(("trecho não está mais no capítulo", trecho))
        elif not confere(contagens):
            fora.append(("o catálogo não sustenta mais", trecho))
    assert not fora, (
        "o capítulo e o catálogo divergiram: %s\nContagens de agora: %s"
        % (fora, contagens))


# --------------------------------------------------------------------------
# A mesma crença, o mesmo lugar na obra
# --------------------------------------------------------------------------

def test_a_mesma_crenca_cita_o_mesmo_item_do_sorva_em_todo_topico():
    """A cauda da fonte muda com o tópico; o item da obra, não.

    Em 18/11/2026 a `pointer_is_data` citava o item 65 no kc_02 — com a
    nota de correção — e ainda o item 14 no kc_04, no kc_08 e no kc_12:
    a correção tinha sido feita só no tópico piloto. Conferido no texto
    integral de Sorva (2012), repositório da Aalto: o item 14 (p. 360) é
    sobre variável ser um par nome-valor; o 65 (p. 362) é a crença.
    """
    import re

    itens = collections.defaultdict(dict)
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            fonte = " ".join(str(b.get("source", "")).split())
            m = re.search(r"Sorva \(2012\),\s*p\.\s*\d+,\s*item\s+(\d+)", fonte)
            if m:
                itens[b["id"]][p.stem] = m.group(1)
    divergem = {cid: t for cid, t in itens.items() if len(set(t.values())) > 1}
    assert not divergem, divergem
