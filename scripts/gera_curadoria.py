# -*- coding: utf-8 -*-
"""Gera docs/curadoria-crencas.md: a tabela sai dos dados, nao da mao.

A tabela de 61 linhas e GERADA do YAML e da conferencia feita nesta
sessao. Digitar 61 linhas a mao seria convidar divergencia entre o
documento e o catalogo -- que e exatamente o defeito que este documento
existe para medir nos outros.
"""
import collections
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import yaml  # noqa: E402

NL = chr(10)

# O TEXTO DA OBRA, que o script nao guarda: ele e de 1,3 MB e nao entra
# no repositorio. Passe o caminho como argumento:
#
#   python scripts/gera_curadoria.py caminho/para/sorva2012.txt
#
# Para obter: o repositorio aberto da Aalto serve o texto JA EXTRAIDO
# pelo proprio DSpace, no bundle TEXT do item 123456789/3534 --
# `isbn9789526046266.pdf.txt`. A URL do conteudo sai da API:
#
#   /server/api/core/items/<uuid>/bundles -> bundle TEXT -> bitstreams
#
# SEM O ARQUIVO o script roda igual: as citacoes do Sorva saem como NAO
# CONFERIDAS, e o documento diz isso. Script que mente quando falta
# insumo e pior que script que nao roda.
SORVA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
TEM_SORVA = bool(SORVA and SORVA.exists())
PILOTO = ("kc_02", "kc_07", "kc_09", "kc_11")

# As secoes do FAQ cujos indices foram abertos em c-faq.com nesta
# auditoria. A 11.x nao foi.
SECOES_ABERTAS = {"1", "4", "5", "6", "7"}

texto_sorva = (SORVA.read_text(encoding="utf-8", errors="replace")
               if TEM_SORVA else "")


def reduz(s):
    return " ".join(re.sub(r"[^A-Za-z0-9 ]+", " ", s).lower().split())


ALVO = reduz(texto_sorva)

# ---------------------------------------------------------------- catalogo
cr = {}
for p in sorted((RAIZ / "mvp" / "dominio").glob("beliefs_kc*.yaml")):
    t = "kc_" + p.stem[len("beliefs_kc"):]
    for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
        cr.setdefault(b["id"], {"topicos": [], "b": b})["topicos"].append(t)

LOCALIZADOR = [
    ("página/item", r"\bp\.\s*\d|\bpp\.\s*\d|\bitens?\s+\d"),
    ("pergunta do FAQ", r"\b\d{1,2}\.\d{1,2}[a-z]?\b"),
    ("id CWE/CERT", r"CWE-\d+|\b[A-Z]{3}\d{2}-C\b"),
    ("seção da obra", r"se[cç][aã]o\s+[\d.]+|\bSec\.\s*[\d.]+"),
]


def localizador(f, sem_item=""):
    # A pagina citada numa nota de busca que falhou e a pagina do item
    # que NAO e a crenca. Nao e localizador de fonte: e endereco de uma
    # ausencia.
    if sem_item:
        return "—"
    fora = [n for n, pat in LOCALIZADOR if re.search(pat, f, re.I)]
    return ", ".join(fora) if fora else "—"


# O FILTRO DE FRASE INGLESA, em duas listas e nao em uma.
#
# A primeira versao exigia uma palavra de uma lista curta -- the, is,
# are, of, that, not, a, an -- e RECUSOU a frase do item 12 do Sorva,
# "Primitive assignment works both directions (swaps)", que nao tem
# nenhuma delas. O gerador escreveu "citada sem frase entre aspas" numa
# linha que TINHA a frase, e o documento passou a descrever o catalogo
# pior do que ele e. Filtro de ingles que recusa ingles nao e
# conservador: e um erro silencioso para baixo.
#
# E o acento nao serve de guarda contra portugues: o `beliefs_kc00.yaml`
# e escrito sem acento do comeco ao fim, de uma era anterior do projeto.
# Entao o que exclui portugues sao as PALAVRAS DE FUNCAO dele, e o que
# admite ingles e uma lista larga.
INGLES = (r"\b(the|is|are|was|were|of|that|not|an?|and|or|to|in|on|by|"
          r"with|it|its|has|have|had|can|cannot|does|do|no|all|both|"
          r"same|other|only|works?|holds?|stores?|creates?|receives?|"
          r"points?|returns?|means?|allocat\w*|variabl\w*|pointer\w*|"
          r"memory|value|values|object|array|reference|directions?)\b")
PORTUGUES = (r"\b(de|da|do|das|dos|que|nao|não|como|em|uma|um|para|pelo|"
             r"pela|com|por|ele|ela|isso|está|esta|são|sao|ser|tem|têm|"
             r"já|ja|mesmo|mesma|crença|crenca|variável|variavel|"
             r"ponteiro|memória|memoria)\b")


def frases_inglesas(f):
    fora = []
    for q in re.findall(r'"([^"]{18,300})"', f):
        if (re.search(INGLES, q, re.I)
                and not re.search(PORTUGUES, q, re.I)
                and not re.search(r"[áàâãéêíóôõúçÁÉÍÓÚÇ]", q)):
            fora.append(q)
    return fora


# As duas classes de fonte. Estudo com estudantes de um lado; corpus de
# praticante do outro. A diferenca nao e de qualidade: e de QUE TIPO DE
# AFIRMACAO cada uma sustenta, e a tabela declara isso por crenca.
MISCONCEPCAO = ("Sorva", "Ma,", "Ma (", "Kaczmarczyk", "Boulay", "Hermans",
                "Holland", "Doukakis", "Soloway", "Putnam", "Sleeman",
                "tienne", "Hristova", "Sajaniemi", "Ragonis", "Kahney",
                "Bayman")
PRATICANTE = ("FAQ", "c-faq", "CWE", "CERT", "Kernighan", "Ritchie", "K&R",
              "ISO")


def classe(f, grade, sem_item=""):
    if grade == "E":
        return "hipótese"
    if sem_item:
        return "— sem fonte"
    if any(k in f for k in MISCONCEPCAO):
        return "**1** · concepção estudada"
    if any(k in f for k in PRATICANTE):
        return "2 · corpus de praticante"
    return "— sem fonte"


def conferencia(cid, f, grade, sem_item=""):
    """Como esta crenca foi conferida, e por quem.

    O `sem_item` VEM PRIMEIRO, antes de qualquer busca de frase, e e por
    um defeito real: a nota de uma busca que falhou CITA, entre aspas, a
    frase do item mais proximo -- aquele que NAO e a crenca. O
    classificador procurava a frase no texto integral, achava, e
    escrevia "conferida" na linha. Prosa nao serve de marcador, porque a
    `pointer_has_no_address` tambem conta uma busca que falhou e a dela
    achou o item na segunda tentativa. Quem declara o achado negativo e
    o campo, nao o paragrafo.
    """
    if sem_item:
        return "sem item na literatura — busca declarada"
    if grade == "E":
        return "sem fonte, por desenho"
    if "Sorva" in f:
        if not TEM_SORVA:
            return "não conferida — texto da obra não dado nesta execução"
        for q in frases_inglesas(f):
            r = reduz(q)
            if r in ALVO or (len(r) > 60 and r[:60] in ALVO):
                return "**conferida** — texto integral do Sorva"
        if not frases_inglesas(f):
            return "citada sem frase entre aspas"
        return "citação abreviada; forma íntegra localizada"
    nums = re.findall(r"\b(\d{1,2})\.\d{1,2}[a-z]?\b", f)
    if ("FAQ" in f or "c-faq" in f) and nums:
        if all(n in SECOES_ABERTAS for n in nums):
            return "**conferida** — índice em c-faq.com"
        return "parcial — seção 11 não reaberta"
    if "CWE" in f or "CERT" in f:
        return "não conferida — fonte pública, não aberta aqui"
    # NAO HA OBRA PARA ABRIR. Dizer "nao conferida -- acesso" aqui seria
    # culpar a biblioteca por uma crenca que nunca citou obra nenhuma. O
    # que ela tem e a analogia, declarada no campo de fonte, e e isso
    # que a grade `T` afirma -- nem mais, nem menos.
    if classe(f, grade) == "— sem fonte":
        return "sem obra citada — transposição declarada"
    return "não conferida — acesso"


linhas, conta = [], collections.Counter()
for cid in sorted(cr):
    d = cr[cid]
    b = d["b"]
    f = " ".join((b.get("source") or "").split())
    grade = b.get("provenance", "?")
    nega = str(b.get("negates", "")).split(":")[-1]
    ts = sorted(set(d["topicos"]))
    si = " ".join(str(b.get("sem_item") or "").split())
    conf = conferencia(cid, f, grade, si)
    conta[conf.replace("**", "")] += 1
    conta["grade " + grade] += 1
    cl = classe(f, grade, si)
    conta["classe " + cl.replace("**", "")] += 1
    linhas.append("| `%s` | %s | %s | %s | `%s` | %s | %s |"
                  % (cid, ", ".join(ts), nega, cl, grade,
                     localizador(f, si), conf))

tabela = NL.join(linhas)
n = len(cr)
confs = sum(v for k, v in conta.items() if k.startswith("conferida"))

doc = """# Curadoria do catálogo de crenças — auditoria de procedência

**11/11/2026.** As %d crenças errôneas do catálogo, uma por linha, com a
grade de procedência, o localizador da fonte e **se ela foi conferida na
obra primária, e por quem**.

A tabela abaixo é **gerada** do `mvp/dominio/beliefs_kc*.yaml` e da
conferência desta sessão. Digitar 61 linhas à mão seria convidar
divergência entre o documento e o catálogo — que é o defeito que este
documento existe para medir.

## Por que esta auditoria é a contribuição, e não um anexo

O instrumento não foi avaliado com participantes. Então a força do
trabalho não está em "o sistema ensina" — está em **o sistema afirma
sobre concepções errôneas só o que a literatura registra, e recusa
afirmar o resto**.

Isso é verificável sem participante nenhum, e é o que esta auditoria
verifica.

## A régua

`docs/linguagem.md` define cinco grades, e o cabeçalho do
`beliefs_kc02.yaml` fixa o padrão: *"AS FONTES FORAM CONFERIDAS NA OBRA
PRIMÁRIA, não de memória"*.

| grade | o que afirma |
| --- | --- |
| `D` | documentada, com fonte e posição localizável |
| `L` | registrada em obra técnica |
| `T` | transposta de outra linguagem, **com a analogia declarada** |
| `N` | norma (CERT C, CWE) |
| `E` | hipótese a testar, **declarada como tal** |

E uma regra que o projeto se impôs: *"uma crença sem procedência é uma
invenção sua que vai virar dado"*.

## O resultado

| | |
| --- | --- |
| crenças distintas | **%d** |
| conferidas na obra primária nesta auditoria | **%d** |
| grades | %s |
| hipóteses `E` | **%d**, todas fora dos quatro tópicos-piloto |

### Como cada obra foi conferida

**A coluna "crenças" soma mais que 61 de propósito:** uma crença pode
citar duas obras — `pointer_is_pointless` cita o Sorva e o FAQ, e as de
grade `N` costumam citar a norma e o FAQ. Na tabela por crença, a coluna
de conferência registra **a verificação mais forte alcançada** para
aquela linha, não todas as obras que ela cita. É por isso que só uma
linha aparece como "fonte pública, não aberta aqui" embora cinco crenças
citem CERT/CWE: as outras quatro foram conferidas pela citação do FAQ
que trazem ao lado.

| obra | crenças | como |
| --- | --- | --- |
| Sorva (2012), *Visual Program Simulation in Introductory Programming Education* | 21 | %s **texto integral** do repositório aberto da Aalto (handle 123456789/3534, bundle TEXT). Para cada citação, a frase em inglês entre aspas foi procurada no texto da obra. **23 frases localizadas verbatim.** |
| FAQ comp.lang.c | 39 | **índices das seções 1, 4, 5, 6 e 7** abertos em c-faq.com. As 48 perguntas citadas nessas seções existem, e os títulos conferem com o que o catálogo cita. |
| CERT C / CWE | 5 | fontes públicas, **não reabertas nesta auditoria** |
| Ma (2007), Kaczmarczyk et al. (2010), du Boulay (1986), Samurçay (1989) | 5 | **citadas `apud` Sorva (2012)**, com página e item. Os artigos originais não foram abertos — a mediação está declarada no campo de fonte de cada crença, e o que foi lido é o item do Sorva que os atribui. |
| K&R, *The C Programming Language* | 1 | citada como **refutação**, não como fonte da crença: é a obra que diz que a crença é falsa |

## As duas classes de fonte, e por que as duas valem

O catálogo se apoia em **dois tipos de fonte**, e a diferença entre eles
não é de qualidade: é de **que tipo de afirmação cada um sustenta**.
Confundi-los seria o defeito; declará-los é o que torna o catálogo
auditável.

### Classe 1 — literatura de concepções errôneas (%d crenças)

Estudo empírico com estudantes, ou revisão sistemática que os agrega.
A principal é o **Apêndice A do Sorva (2012)**: um catálogo de 162
concepções errôneas levantadas da literatura, cada uma com tópico,
descrição e fonte. Ao lado dela, os estudos que ela mesma agrega — Ma
(2007), Kaczmarczyk et al. (2010), du Boulay (1986), Holland et al.
(1997), Soloway et al. (1982), Doukakis et al. (2007) — e Hermans et al.
(2018).

**O que esta classe sustenta:** que a concepção foi *observada em
estudantes*, por alguém que a estudou.

### Classe 2 — corpus de praticante (%d crenças)

O **FAQ do comp.lang.c**. Conferido na fonte: a lista *"was first
composed in 1990, for posting to the Usenet newsgroup comp.lang.c. It
has undergone episodic refinement ever since, including being published
as a book"* (c-faq.com/about.html). A forma publicada é:

> Steve Summit. *C Programming FAQs: Frequently Asked Questions*.
> Addison-Wesley, 1996. ISBN 0-201-84519-9.

**Ressalva de citação, registrada:** a versão on-line corresponde a
cerca de **metade** do livro (c-faq.com/book/). As citações deste
catálogo são da versão on-line, por número de pergunta, que é o que foi
consultado — e não do livro.

**E por que o FAQ é evidência sobre concepção errônea, e não só sobre C.**
Porque o título de muitas perguntas **é a concepção dita por quem a
tem**, em primeira pessoa:

| pergunta | o título |
| --- | --- |
| 6.2 | *"But I heard that `char a[]` was identical to `char *a`."* |
| 6.9 | *"Someone explained to me that arrays were really just constant pointers."* |
| 6.4b | *"So arrays are passed by reference, even though the rest of C uses pass by value?"* |
| 4.11 | *"Does C even have ``pass by reference''?"* |

O catálogo não **infere** a concepção a partir de uma explicação
técnica: ele **lê a frase de quem a sustenta**. Esse é o critério de
inclusão, e ele é conferível — qualquer pessoa abre a pergunta e vê se o
título é a crença ou só o assunto.

Em termos de método, isso faz do FAQ uma **fonte documental**: um corpus
de confusões auto-relatadas, ocorrido naturalmente e curado por
**recorrência** ao longo de mais de três décadas. O uso aqui é análise
documental desse corpus.

**O que esta classe sustenta — e o que ela NÃO sustenta:**

- sustenta que a confusão **ocorre e recorre** entre quem aprende C;
- **não** sustenta prevalência. A população é auto-selecionada — quem
  escreve para um grupo de Usenet —, e a frequência é juízo do editor,
  não medida. Nenhuma afirmação de proporção sai desta fonte.

### Por que as duas são necessárias, e isto é um achado

Procurado item por item no catálogo do Sorva: ele tem um tópico
dedicado a referências — `Refs`, 17 dos 162 itens — e itens sobre
memória e tempo de vida espalhados por `VarAssign`, `ObjState` e `Misc`.
O que falta é o que importa aqui, e esta contagem é reprodutível por
busca de termo no texto da Tabela A.1:

| termo | ocorrências na Tabela A.1 |
| --- | --- |
| `malloc`, `free`, `deallocat`, `garbage` | **0** |
| `heap`, `stack` | **0** |
| `arithmetic`, `decay`, `dangling`, `sizeof` | **0** |
| `null` | **1**, e é "Null model of recursion" (item 54), que não é ponteiro nulo |
| `lifetime` | **1**, o item 5 |
| `memory` | 7 |

A CONTAGEM ANTERIOR DIZIA "26 itens sobre memória, referência, array e
tempo de vida", e saiu em 11/11/2026 por não ser reprodutível: o número
dependia da lista de palavras-chave de quem contou, e uma lista
razoável devolve 21. O que sustenta o argumento são os ZEROS, que não
dependem de lista.

A razão é que aquele catálogo é de programação introdutória em **Java,
Python e BASIC**, onde esses construtos não existem. A literatura de
concepções errôneas **não pode** documentar confusões sobre o que
distingue C.

Então a conclusão não é que as 35 crenças sejam fracas. É que **um
catálogo de concepções errôneas para C exige uma segunda classe de
fonte, e ela tem de ser declarada como segunda classe** — com o que ela
sustenta e o que não sustenta escrito ao lado. É o que a coluna de
classe desta tabela faz, linha por linha.

## O que esta auditoria achou, e que vale mais que a tabela

### 1. Três vezes a busca errou de vocabulário ou de item, e as três vezes o certo estava lá

É o achado metodológico do projeto, e ele é sobre **construir catálogo a
partir da literatura**, não sobre C.

| crença | o que a nota dizia | o que estava lá |
| --- | --- | --- |
| `pointer_has_no_address` | *"PROCUREI no catálogo do Sorva e NÃO ESTÁ LÁ: nenhum dos 162 itens afirma que a referência não ocupa espaço"* | item 14, p. 360, **segunda frase**: *"It is not stored inside the computer"*. A busca procurou REFERÊNCIA e ESPAÇO; o item fala de VARIÁVEL. |
| `array_confused_with_cell` | *"não tem fonte empírica, entra como `E`"* | item 151, p. 367: *"Confusion between an array and its cell"*, e item 9, p. 359: *"A variable can hold multiple values at a time"*. A busca procurou ARRAY numa fonte de C; o item 9 fala de VARIÁVEL e o 151 está no tópico `Misc`. |
| `assignment_symmetric` | citava o item 11 **com a aproximação declarada**: *"o 11 é sobre a direção INVERTIDA, e esta crença é sobre os DOIS lados"* | item 12, p. 359, **a linha logo abaixo do 11**: *"Primitive assignment works both directions (swaps)"*. É a frase do rótulo, traduzida. |

Nos três casos a grade subiu — `E` → `T`, `E` → `D` e `L` → `D` —
**porque a busca foi refeita**, não porque alguém decidiu confiar na
intuição.

É um resultado replicável e é uma recomendação de método: buscar pelo
FENÔMENO, não pelo termo da própria linguagem. Em catálogo de
concepções errôneas de linguagem X, o item que você procura pode estar
escrito no vocabulário da linguagem Y.

E O TERCEIRO CASO ACRESCENTA UM SEGUNDO PRINCÍPIO, que é sobre
honestidade de citação: **foi a aproximação DECLARADA que tornou o erro
achável.** A citação dizia em que o item 11 diferia da crença, e foi
essa diferença que apontou para o item vizinho. Citação que esconde a
folga não dá esse aviso — ela fica errada em silêncio.

### 2. Uma citação estava no item errado, e a crença estava certa

`pointer_is_data` apontava o item 14 do Sorva, que é sobre variável ser
par nome-valor — **não é sobre ponteiro**. A crença está no catálogo,
mas no **item 65**: *"A (non-primitive Java) variable does not hold a
reference but a set of object properties."* A fonte estava certa; o item
não.

Achado abrindo a obra. Não há como achar isso sem abrir.

### 3. Três crenças citam o FAQ numa pergunta cuja resposta tem duas metades

`pointer_has_no_address` e `pointer_is_data` saem das duas frases do
**mesmo** item 14. A FAQ 7.21 sustenta três crenças do kc_09, a 7.22
duas do kc_08, a 4.9 duas do kc_10.

Isso não é economia de fonte: é que uma resposta de FAQ costuma
responder a **duas confusões diferentes**, e separá-las é trabalho de
curadoria, não de leitura.

## O que fica em aberto, nomeado

1. **Cinco crenças citam estudo que só foi lido pela mediação do
   Sorva** — Ma (2007), Kaczmarczyk et al. (2010), du Boulay (1986) e
   Samurçay (1989). A citação delas traz `apud`, com página e item do
   Sorva, e **diz que o original não foi aberto**. Fechar isso exige o
   portal da biblioteca; o que não fica em aberto é o leitor saber em
   que mão a citação está.
2. **Cinco crenças de grade `N`** citam CERT C e CWE, que são públicos e
   não foram reabertos aqui.
3. **A FAQ 11.24** (`voidptr_arith_ok`) não foi reaberta — a seção 11 do
   FAQ ficou fora desta passada.
4. **Uma crença cita o Sorva sem frase entre aspas** —
   `uninitialized_is_null` —, o que torna a citação não verificável
   mecanicamente pelo gerador. Ela traz página e item. Eram duas: a
   `assignment_symmetric` passou a trazer a frase do item 12 em
   11/11/2026, e o caso dela está contado no achado 1.
5. **Uma crença de grade `T` não cita obra nenhuma** —
   `heap_dies_with_function` (kc_01). O que ela tem é a analogia,
   declarada: em Java e Python o que a função alocou e ninguém mais
   alcança desaparece sozinho. A busca por vocabulário do fenômeno foi
   refeita — *lifetime*, *scope*, *deallocate*, *garbage* — e o que o
   Apêndice A tem de mais próximo é o item 5, p. 359, *"Difficulties
   understanding the lifetime of values"*, que é DIFICULDADE com tempo
   de vida e não a crença. O próprio campo de fonte dela diz
   "PRECISA DE FONTE antes da coleta, ou desce para `E`".
6. **As três `E`** — `type_is_a_hint` (kc_00),
   `memoria_e_do_computador` (kc_01) e `memory_is_uniform` (kc_01,
   kc_12) — seguem declaradas como hipótese. Estão fora dos
   tópicos-piloto, e há dois testes proibindo `E` em piloto, por
   caminhos diferentes (`test_piloto_nao_tem_crenca_estimada` carrega o
   domínio; `test_as_tres_hipoteses_estao_fora_do_piloto` lê o YAML). O
   precedente desta auditoria diz o que tentar antes de aceitá-las:
   refazer a busca com outro vocabulário — foi o que fez duas delas
   subirem de grade, e o que confirmou que esta terceira não tem item.

## A tabela

| crença | tópicos | nega | classe da fonte | grade | localizador | conferência |
| --- | --- | --- | --- | --- | --- | --- |
%s

---

*Gerado de `mvp/dominio/beliefs_kc*.yaml` em 11/11/2026. A coluna de
conferência registra o que foi aberto NESTA auditoria; o que foi
conferido em auditoria anterior está em `docs/revisao-crencas-kc02.md`.*

### Como reproduzir, e por que o número muda

    python scripts/gera_curadoria.py CAMINHO/DO/sorva2012.txt

O argumento é o texto integral do Sorva (2012), baixado do repositório
aberto da Aalto (handle `123456789/3534`, bundle TEXT). A coluna de
conferência das crenças de classe 1 é produzida **procurando a frase em
inglês de cada citação nesse texto** — o programa não confia no campo de
fonte, ele confere.

**Sem o argumento, o número cai de 52 para 32**, e as linhas que
dependiam do texto passam a dizer "texto da obra não dado nesta
execução". Isso é deliberado: o documento não afirma uma conferência que
a execução não fez. O arquivo não entra no repositório porque é a obra
de outra pessoa; quem quiser reconferir baixa do handle acima.
""" % (n, n, confs, ", ".join("%s %d" % (k.replace("grade ", "`") + "`", v)
                              for k, v in sorted(conta.items())
                              if k.startswith("grade")),
       conta["grade E"],
       ("" if TEM_SORVA else
        "**NÃO CONFERIDO nesta execução** (texto da obra não foi dado). "
        "Na auditoria de 11/11/2026 foi conferido assim:"),
       conta["classe 1 · concepção estudada"],
       conta["classe 2 · corpus de praticante"],
       tabela)

alvo = RAIZ / "docs" / "curadoria-crencas.md"
alvo.write_text(doc, encoding="utf-8", newline=NL)
print("escrito:", alvo)
print("%d crenças, %d conferidas nesta auditoria" % (n, confs))
print()
for k, v in sorted(conta.items()):
    print("   %-48s %d" % (k, v))
