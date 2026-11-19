# Curadoria do catálogo de crenças — auditoria de procedência

**11/11/2026.** As 61 crenças errôneas do catálogo, uma por linha, com a
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
| crenças distintas | **61** |
| conferidas na obra primária nesta auditoria | **53** |
| grades | `D` 6, `E` 3, `L` 33, `N` 3, `T` 16 |
| hipóteses `E` | **3**, todas fora dos quatro tópicos-piloto |

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
| Sorva (2012), *Visual Program Simulation in Introductory Programming Education* | 21 |  **texto integral** do repositório aberto da Aalto (handle 123456789/3534, bundle TEXT). Para cada citação, a frase em inglês entre aspas foi procurada no texto da obra. **23 frases localizadas verbatim.** |
| FAQ comp.lang.c | 39 | **índices das seções 1, 4, 5, 6 e 7** abertos em c-faq.com. As 48 perguntas citadas nessas seções existem, e os títulos conferem com o que o catálogo cita. |
| CERT C / CWE | 5 | fontes públicas, **não reabertas nesta auditoria** |
| Ma (2007), Kaczmarczyk et al. (2010), du Boulay (1986), Samurçay (1989) | 5 | **citadas `apud` Sorva (2012)**, com página e item. Os artigos originais não foram abertos — a mediação está declarada no campo de fonte de cada crença, e o que foi lido é o item do Sorva que os atribui. |
| K&R, *The C Programming Language* | 1 | citada como **refutação**, não como fonte da crença: é a obra que diz que a crença é falsa |

## As duas classes de fonte, e por que as duas valem

O catálogo se apoia em **dois tipos de fonte**, e a diferença entre eles
não é de qualidade: é de **que tipo de afirmação cada um sustenta**.
Confundi-los seria o defeito; declará-los é o que torna o catálogo
auditável.

### Classe 1 — literatura de concepções errôneas (23 crenças)

Estudo empírico com estudantes, ou revisão sistemática que os agrega.
A principal é o **Apêndice A do Sorva (2012)**: um catálogo de 162
concepções errôneas levantadas da literatura, cada uma com tópico,
descrição e fonte. Ao lado dela, os estudos que ela mesma agrega — Ma
(2007), Kaczmarczyk et al. (2010), du Boulay (1986), Holland et al.
(1997), Soloway et al. (1982), Doukakis et al. (2007) — e Hermans et al.
(2018).

**O que esta classe sustenta:** que a concepção foi *observada em
estudantes*, por alguém que a estudou.

### Classe 2 — corpus de praticante (34 crenças)

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

`memory_is_by_name` e `pointer_has_no_address` saem das duas frases do
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
| `ampersand_copies` | kc_04, kc_06, kc_10, kc_12 | B2 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `ampersand_takes_value` | kc_04 | B1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `any_zero_is_null` | kc_05 | B2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `arr_equals_addr_of_arr` | kc_07 | B4 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `array2d_is_double_pointer` | kc_10 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `array_confused_with_cell` | kc_07 | B1 | **1** · concepção estudada | `D` | página/item, seção da obra | **conferida** — texto integral do Sorva |
| `array_is_assignable` | kc_07 | I1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `array_is_pointer` | kc_07 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `array_passed_by_reference` | kc_07 | B3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `assignment_symmetric` | kc_00 | I1 | **1** · concepção estudada | `D` | página/item | **conferida** — texto integral do Sorva |
| `declaration_allocates` | kc_03, kc_07 | I1 | **1** · concepção estudada | `T` | página/item, pergunta do FAQ | **conferida** — texto integral do Sorva |
| `declaration_zeroes` | kc_00, kc_03 | B3 | **1** · concepção estudada | `D` | página/item, pergunta do FAQ, seção da obra | **conferida** — texto integral do Sorva |
| `double_deref_is_data` | kc_10 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `double_free_is_safe` | kc_09 | I4 | 2 · corpus de praticante | `N` | pergunta do FAQ, id CWE/CERT | **conferida** — índice em c-faq.com |
| `estrela_e_do_tipo` | kc_03 | B2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `free_kills_pointer` | kc_09 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ, id CWE/CERT | **conferida** — índice em c-faq.com |
| `free_nullifies` | kc_09 | I1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `funcao_usa_a_variavel_do_chamador` | kc_06 | B1 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `function_gets_original` | kc_06, kc_09 | I1 | **1** · concepção estudada | `T` | página/item, pergunta do FAQ | **conferida** — texto integral do Sorva |
| `heap_dies_with_function` | kc_01 | I1 | — sem fonte | `T` | — | sem item na literatura — busca declarada |
| `heap_persists` | kc_09 | B4 | 2 · corpus de praticante | `L` | pergunta do FAQ, id CWE/CERT | **conferida** — índice em c-faq.com |
| `indice_nao_e_soma` | kc_11 | I1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `local_sobrevive` | kc_01 | B2 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `local_survives_return` | kc_12 | I3 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `malloc_always_succeeds` | kc_08 | I2 | 2 · corpus de praticante | `N` | id CWE/CERT | não conferida — fonte pública, não aberta aqui |
| `malloc_conta_elementos` | kc_08 | B1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `malloc_initializes_zero` | kc_08 | B3 | **1** · concepção estudada | `L` | página/item, pergunta do FAQ | **conferida** — texto integral do Sorva |
| `memoria_e_do_computador` | kc_01 | B1 | hipótese | `E` | página/item | sem fonte, por desenho |
| `memory_is_by_name` | kc_02 | B1 | **1** · concepção estudada | `D` | página/item | **conferida** — texto integral do Sorva |
| `memory_is_uniform` | kc_01, kc_12 | I2 | hipótese | `E` | — | sem item na literatura — busca declarada |
| `modify_pp_changes_p` | kc_06, kc_10 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `no_value_no_memory` | kc_00, kc_03 | B2 | **1** · concepção estudada | `D` | página/item | **conferida** — texto integral do Sorva |
| `null_after_free_redundant` | kc_09 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `null_is_absence` | kc_05 | B1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `null_is_safe_to_deref` | kc_05 | I3 | 2 · corpus de praticante | `N` | pergunta do FAQ, id CWE/CERT | **conferida** — índice em c-faq.com |
| `null_is_zero_always` | kc_05 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `null_points_to_zero` | kc_05 | B3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `passa_a_expressao` | kc_06 | B2 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `pode_usar_logo` | kc_03 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `pointer_and_target_are_one` | kc_02 | I1 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `pointer_copy_is_alias` | kc_06 | I4 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `pointer_has_no_address` | kc_02 | B2 | **1** · concepção estudada | `T` | página/item, pergunta do FAQ | **conferida** — texto integral do Sorva |
| `pointer_is_data` | kc_02, kc_04, kc_08, kc_12 | B3 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `pointer_is_integer` | kc_02, kc_11 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `pointer_is_just_a_name` | kc_04, kc_05, kc_10 | I1 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `pointer_is_pointless` | kc_02 | I3 | **1** · concepção estudada | `L` | pergunta do FAQ | citação abreviada; forma íntegra localizada |
| `pointer_knows_block_size` | kc_09, kc_11 | B1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `pointer_lives_in_heap` | kc_08, kc_09 | I1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `ptr_arith_is_bytes` | kc_11 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `retorno_fica_guardado` | kc_12 | B3 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `sizeof_array_via_pointer` | kc_07 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `star_assigns_pointer` | kc_04 | I3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `star_binds_to_the_pointer` | kc_04 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `static_is_scope` | kc_12 | I2 | **1** · concepção estudada | `T` | página/item | **conferida** — texto integral do Sorva |
| `string_literal_is_array` | kc_07, kc_11 | B1 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `system_frees_auto` | kc_01, kc_08 | B3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |
| `type_is_a_hint` | kc_00 | B1 | hipótese | `E` | — | sem fonte, por desenho |
| `uninitialized_is_null` | kc_03 | I2 | **1** · concepção estudada | `D` | página/item | citada sem frase entre aspas |
| `variable_remembers` | kc_00 | B4 | **1** · concepção estudada | `T` | página/item, seção da obra | **conferida** — texto integral do Sorva |
| `voidptr_arith_ok` | kc_11 | I2 | 2 · corpus de praticante | `L` | pergunta do FAQ | parcial — seção 11 não reaberta |
| `voidptr_is_universal` | kc_10 | B3 | 2 · corpus de praticante | `L` | pergunta do FAQ | **conferida** — índice em c-faq.com |

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
