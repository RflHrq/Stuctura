# Apêndice B — O catálogo de concepções errôneas, linha por linha

Este apêndice traz as 61 concepções errôneas do catálogo, uma por linha,
com a procedência de cada uma (Capítulo 4). Ele não foi digitado: é gerado
do catálogo (`mvp/dominio/beliefs_kc*.yaml`) por `scripts/gera_curadoria.py`,
que procura no texto integral de Sorva (2012) a frase em inglês de cada
citação daquela obra. Rodado sem esse texto, o programa marca essas linhas
como não conferidas, em vez de afirmar uma conferência que não fez.

As colunas são: a concepção, pelo identificador do catálogo; os tópicos
em que ela aparece; a premissa que ela nega, no primeiro desses tópicos; a
classe da fonte (1, concepção estudada com estudantes; 2, corpus de
praticante; ou hipótese); o grau de procedência (Quadro 4.1); o
localizador, isto é, o tipo de posição que a citação dá na obra; e a
conferência, como a citação foi conferida na obra primária (Quadro 4.4).
A conferência é a da curadoria; a das normas CERT C e CWE, feita à parte,
está em 4.7.

**Quadro B.1 — As 61 concepções errôneas do catálogo e a procedência de cada uma**

| concepção | tópicos | premissa | classe | grau | localizador | conferência |
| --- | --- | --- | --- | --- | --- | --- |
| `ampersand_copies` | kc_04, kc_06, kc_10, kc_12 | B2 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `ampersand_takes_value` | kc_04 | B1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `any_zero_is_null` | kc_05 | B2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `arr_equals_addr_of_arr` | kc_07 | B4 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `array2d_is_double_pointer` | kc_10 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `array_confused_with_cell` | kc_07 | B1 | 1, concepção estudada | `D` | página/item, seção da obra | conferida: texto integral do Sorva |
| `array_is_assignable` | kc_07 | I1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `array_is_pointer` | kc_07 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `array_passed_by_reference` | kc_07 | B3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `assignment_symmetric` | kc_00 | I1 | 1, concepção estudada | `D` | página/item | conferida: texto integral do Sorva |
| `declaration_allocates` | kc_03, kc_07 | I1 | 1, concepção estudada | `T` | página/item, pergunta do FAQ | conferida: texto integral do Sorva |
| `declaration_zeroes` | kc_00, kc_03 | B3 | 1, concepção estudada | `D` | página/item, pergunta do FAQ, seção da obra | conferida: texto integral do Sorva |
| `double_deref_is_data` | kc_10 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `double_free_is_safe` | kc_09 | I4 | 2, corpus de praticante | `N` | pergunta do FAQ, id CWE/CERT | conferida: índice em c-faq.com |
| `estrela_e_do_tipo` | kc_03 | B2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `free_kills_pointer` | kc_09 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ, id CWE/CERT | conferida: índice em c-faq.com |
| `free_nullifies` | kc_09 | I1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `funcao_usa_a_variavel_do_chamador` | kc_06 | B1 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `function_gets_original` | kc_06, kc_09 | I1 | 1, concepção estudada | `T` | página/item, pergunta do FAQ | conferida: texto integral do Sorva |
| `heap_dies_with_function` | kc_01 | I1 | sem fonte | `T` | não há | sem item na literatura: busca declarada |
| `heap_persists` | kc_09 | B4 | 2, corpus de praticante | `L` | pergunta do FAQ, id CWE/CERT | conferida: índice em c-faq.com |
| `indice_nao_e_soma` | kc_11 | I1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `local_sobrevive` | kc_01 | B2 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `local_survives_return` | kc_12 | I3 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `malloc_always_succeeds` | kc_08 | I2 | 2, corpus de praticante | `N` | id CWE/CERT | não conferida: fonte pública, não aberta aqui |
| `malloc_conta_elementos` | kc_08 | B1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `malloc_initializes_zero` | kc_08 | B3 | 1, concepção estudada | `L` | página/item, pergunta do FAQ | conferida: texto integral do Sorva |
| `memoria_e_do_computador` | kc_01 | B1 | hipótese | `E` | página/item | sem fonte, por desenho |
| `memory_is_by_name` | kc_02 | B1 | 1, concepção estudada | `D` | página/item | conferida: texto integral do Sorva |
| `memory_is_uniform` | kc_01, kc_12 | I2 | hipótese | `E` | não há | sem item na literatura: busca declarada |
| `modify_pp_changes_p` | kc_06, kc_10 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `no_value_no_memory` | kc_00, kc_03 | B2 | 1, concepção estudada | `D` | página/item | conferida: texto integral do Sorva |
| `null_after_free_redundant` | kc_09 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `null_is_absence` | kc_05 | B1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `null_is_safe_to_deref` | kc_05 | I3 | 2, corpus de praticante | `N` | pergunta do FAQ, id CWE/CERT | conferida: índice em c-faq.com |
| `null_is_zero_always` | kc_05 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `null_points_to_zero` | kc_05 | B3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `passa_a_expressao` | kc_06 | B2 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `pode_usar_logo` | kc_03 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `pointer_and_target_are_one` | kc_02 | I1 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `pointer_copy_is_alias` | kc_06 | I4 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `pointer_has_no_address` | kc_02 | B2 | 1, concepção estudada | `T` | página/item, pergunta do FAQ | conferida: texto integral do Sorva |
| `pointer_is_data` | kc_02, kc_04, kc_08, kc_12 | B3 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `pointer_is_integer` | kc_02, kc_11 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `pointer_is_just_a_name` | kc_04, kc_05, kc_10 | I1 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `pointer_is_pointless` | kc_02 | I3 | 1, concepção estudada | `L` | pergunta do FAQ | citação abreviada; forma íntegra localizada |
| `pointer_knows_block_size` | kc_09, kc_11 | B1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `pointer_lives_in_heap` | kc_08, kc_09 | I1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `ptr_arith_is_bytes` | kc_11 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `retorno_fica_guardado` | kc_12 | B3 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `sizeof_array_via_pointer` | kc_07 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `star_assigns_pointer` | kc_04 | I3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `star_binds_to_the_pointer` | kc_04 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `static_is_scope` | kc_12 | I2 | 1, concepção estudada | `T` | página/item | conferida: texto integral do Sorva |
| `string_literal_is_array` | kc_07, kc_11 | B1 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `system_frees_auto` | kc_01, kc_08 | B3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |
| `type_is_a_hint` | kc_00 | B1 | hipótese | `E` | não há | sem fonte, por desenho |
| `uninitialized_is_null` | kc_03 | I2 | 1, concepção estudada | `D` | página/item | citada sem frase entre aspas |
| `variable_remembers` | kc_00 | B4 | 1, concepção estudada | `T` | página/item, seção da obra | conferida: texto integral do Sorva |
| `voidptr_arith_ok` | kc_11 | I2 | 2, corpus de praticante | `L` | pergunta do FAQ | parcial: seção 11 não reaberta |
| `voidptr_is_universal` | kc_10 | B3 | 2, corpus de praticante | `L` | pergunta do FAQ | conferida: índice em c-faq.com |

*Fonte: gerado do catálogo do Structura por `scripts/gera_curadoria.py`, com o texto integral de Sorva (2012).*
