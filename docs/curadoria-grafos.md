# Curadoria dos grafos de premissas

Gerado por `python -m tools.curadoria`. Não editar à mão: mexa nos
YAMLs e gere de novo.

Domínio `c_pointers`, hash `cc58e441b512`.

| | |
| --- | --- |
| Tópicos | 12 (4 no piloto: kc_02, kc_07, kc_11, kc_09) |
| Nós | 93 (43 observáveis, 50 de inferência) |
| Crenças | 34 |
| Atividades | 65 |

## kc_01 — Modelo de memoria

Conclusão (`I2`): A memoria do processo tem regioes com regras de vida diferentes: a stack e gerenciada pelo compilador, o heap pelo programador.

Prerequisitos declarados: nenhum. O percurso deste tópico alcança 5 nós, sendo 0 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 4 | — | — |
| `B2` | observável | espinha | — | 4 | — | ciu_kc01_002 n1 |
| `B3` | observável | espinha | — | 5 | system_frees_auto (L) | ciu_kc01_003 n2, ciu_kc01_004 n2 |
| `I1` | inferência | espinha | B2, B3 | 4 | — | ciu_kc01_002 n1, ciu_kc01_003 n2 |
| `I2` | inferência | espinha | B1, I1 | 4 | memory_is_uniform (T) | ciu_kc01_001 n2 |

**O que cada nó afirma**

- `B1` — O programa tem memoria propria enquanto executa.
    - em linguagem corrente: Enquanto o programa roda, ele tem um espaço de memória só dele — uma rua de posições numeradas.
- `B2` — Variaveis locais nascem e morrem com a funcao.
    - em linguagem corrente: As caixas criadas dentro de uma função aparecem quando ela começa e somem quando ela termina.
- `B3` — malloc pede um bloco que nao morre com a funcao.
    - em linguagem corrente: Quando você pede um pedaço de memória com malloc, esse pedaço não some quando a função termina.
- `I1` — Existem duas disciplinas de vida distintas.
    - em linguagem corrente: Então existem dois jeitos de uma caixa durar: uma some sozinha, a outra fica até você devolver.
- `I2` — Logo ha duas regioes: stack e heap.
    - em linguagem corrente: Logo a memória do programa tem duas áreas com regras de arrumação diferentes.

## kc_02 — O que e um ponteiro · **piloto**

Conclusão (`I2`): Um ponteiro e uma variavel cujo valor e o endereco de outro objeto. O ponteiro e o objeto apontado sao duas entidades separadas.

Prerequisitos declarados: kc_01. O percurso deste tópico alcança 11 nós, sendo 5 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | órfão | — | 2 | — | — |
| `B2` | observável | espinha | — | 3 | — | — |
| `B3` | observável | espinha | — | 5 | — | — |
| `I1` | inferência | espinha | B2, B3 | 3 | pointer_is_data (T) | ciu_kc02_001 n1, ciu_kc02_005 n2 |
| `I2` | inferência | espinha | I1, kc_01:I2 | 2 | pointer_lives_in_heap (L) | ciu_kc02_002 n2 |
| `I3` | inferência | órfão | B1, B3 | 2 | pointer_is_integer (L), voidptr_is_universal (L) | ciu_kc02_003 n3, ciu_kc02_004 n3, ciu_kc02_006 n3, ciu_kc02_007 n3 |

**O que cada nó afirma**

- `B1` — Todo objeto na memoria tem um endereco.
    - em linguagem corrente: Toda caixa na memória tem um endereço: o número que diz onde ela está.
- `B2` — p e uma variavel: ocupa espaco e tem endereco proprio.
    - em linguagem corrente: p é uma caixa como qualquer outra: ocupa lugar e tem endereço próprio.
- `B3` — O valor guardado em p e um endereco.
    - em linguagem corrente: O que está guardado dentro de p é um endereço — o lugar de outra caixa.
- `I1` — p e o objeto apontado sao duas entidades.
    - em linguagem corrente: Então p e a caixa apontada são duas caixas diferentes, cada uma no seu lugar.
- `I2` — p vive onde foi declarado, nao onde aponta.
    - em linguagem corrente: p fica na área onde foi criada. Apontar para a outra área não muda o lugar de p.
- `I3` — Endereco nao e inteiro: tem tipo e regras proprias.
    - em linguagem corrente: Endereço não é um número comum: ele carrega junto o tipo do que está no destino.

## kc_03 — Declaracao e inicializacao

Conclusão (`I3`): int *p; cria so o ponteiro, com valor indeterminado. Nao cria nem inicializa o objeto apontado.

Prerequisitos declarados: kc_02. O percurso deste tópico alcança 6 nós, sendo 0 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 3 | — | — |
| `B2` | observável | espinha | — | 3 | — | — |
| `B3` | observável | espinha | — | 2 | — | — |
| `I1` | inferência | espinha | B1, B2 | 3 | declaration_allocates (T) | ciu_kc03_001 n1, ciu_kc03_003 n2 |
| `I2` | inferência | espinha | B3, I1 | 2 | uninitialized_is_null (D) | ciu_kc03_002 n2 |
| `I3` | inferência | espinha | I1, I2 | 1 | — | ciu_kc03_003 n2 |

**O que cada nó afirma**

- `B1` — A declaracao reserva espaco para a variavel declarada.
    - em linguagem corrente: Declarar uma variável cria a caixa dela. Uma caixa, a que você nomeou.
- `B2` — int *p declara p, nao *p.
    - em linguagem corrente: Em int *p; quem é criado é p. O * faz parte do tipo, não é uma segunda caixa.
- `B3` — C nao zera variaveis automaticas.
    - em linguagem corrente: C não limpa as caixas novas. O que estava naquele lugar antes continua lá.
- `I1` — Declarar p nao cria o objeto apontado.
    - em linguagem corrente: Então declarar p não cria a caixa para onde p vai apontar. Só existe uma caixa até aqui.
- `I2` — p contem lixo, nao NULL.
    - em linguagem corrente: Nesse ponto p guarda um valor qualquer, sobra do que estava ali. Não é NULL.
- `I3` — Desreferenciar p antes de atribuir e invalido.
    - em linguagem corrente: Por isso usar *p antes de dar um endereço a p manda o programa a um lugar que ninguém escolheu.

## kc_04 — Dereferencia (* e &)

Conclusão (`I3`): &x produz o endereco de x; *p acessa o objeto no endereco guardado em p. Sao operacoes inversas sobre objetos que ocupam memoria.

Prerequisitos declarados: kc_02, kc_03. O percurso deste tópico alcança 8 nós, sendo 0 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | órfão | — | 1 | — | — |
| `B2` | observável | espinha | — | 10 | — | — |
| `B3` | observável | espinha | — | 4 | — | — |
| `B4` | observável | órfão | — | 2 | star_assigns_pointer (L) | ciu_kc04_002 n2 |
| `I1` | inferência | órfão | B1 | 1 | ampersand_takes_value (L) | ciu_kc04_001 n1 |
| `I2` | inferência | espinha | B2, B3 | 4 | — | ciu_kc04_003 n2 |
| `I3` | inferência | espinha | B2, I2 | 1 | — | ciu_kc04_003 n2, ciu_kc04_004 n2 |
| `I4` | inferência | órfão | B4, I2 | 1 | — | — |

**O que cada nó afirma**

- `B1` — So o que ocupa memoria tem endereco.
    - em linguagem corrente: Só tem endereço o que ocupa um lugar na memória.
- `B2` — &x devolve o endereco de x; nao copia x.
    - em linguagem corrente: &x dá o endereço de x — o número do lugar dela. Não faz cópia nenhuma de x.
- `B3` — p guarda um endereco.
    - em linguagem corrente: p guarda um endereço dentro dela.
    - importado de `kc_02:B3`
- `B4` — Na declaracao o * pertence ao tipo; na expressao e operador.
    - em linguagem corrente: O mesmo * quer dizer duas coisas: em int *p ele faz parte do tipo; em *p ele é a ação de ir até lá.
- `I1` — &5 e invalido: 5 nao e objeto.
    - em linguagem corrente: Por isso &5 não existe: 5 não ocupa lugar nenhum, então não há endereço para dar.
- `I2` — *p vai ate o endereco e acessa o que esta la.
    - em linguagem corrente: Então *p vai até o endereço guardado em p e mexe no que está lá.
- `I3` — * e & sao inversos: *(&x) e x.
    - em linguagem corrente: & pergunta onde a caixa está; * vai até lá. Um desfaz o outro: *(&x) é o próprio x.
- `I4` — *p = v escreve no objeto apontado, nao em p.
    - em linguagem corrente: *p = 7 troca o que está dentro da caixa apontada. A caixa p continua com o mesmo endereço dentro.

## kc_05 — Ponteiro NULL

Conclusão (`I3`): NULL e um valor de ponteiro que garantidamente nao designa objeto algum. Desreferencia-lo e comportamento indefinido.

Prerequisitos declarados: kc_03, kc_04. O percurso deste tópico alcança 11 nós, sendo 3 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | órfão | — | 2 | — | — |
| `B2` | observável | órfão | — | 3 | — | — |
| `B3` | observável | espinha | — | 2 | — | — |
| `B4` | observável | órfão | — | 1 | — | — |
| `I1` | inferência | órfão | B1, B2 | 2 | — | ciu_kc05_003 n1, ciu_kc05_004 n2 |
| `I2` | inferência | órfão | I1 | 0 | — | ciu_kc05_003 n1 |
| `I3` | inferência | espinha | B3, kc_04:I2 | 2 | null_is_safe_to_deref (N) | ciu_kc05_001 n2 |
| `I4` | inferência | órfão | B2, B4 | 1 | null_is_zero_always (L) | ciu_kc05_002 n3 |

**O que cada nó afirma**

- `B1` — Um ponteiro precisa poder indicar ausencia de destino.
    - em linguagem corrente: Às vezes um ponteiro precisa dizer 'não aponto para lugar nenhum'. Isso também é uma informação.
- `B2` — A constante 0 em contexto de ponteiro vira o ponteiro nulo.
    - em linguagem corrente: Escrever 0 onde se espera um ponteiro dá exatamente esse valor de 'nenhum lugar'.
- `B3` — Nenhum objeto tem o endereco do ponteiro nulo.
    - em linguagem corrente: Nenhuma caixa mora nesse endereço. Ele é reservado justamente para significar 'nenhum lugar'.
- `B4` — A representacao interna do ponteiro nulo nao precisa ser zero.
    - em linguagem corrente: O que a máquina guarda ali não precisa ser o número zero. Isso é detalhe de máquina, não do seu código.
- `I1` — NULL e um valor de ponteiro, nao um nao-valor.
    - em linguagem corrente: Então NULL é um valor de verdade, escrito dentro do ponteiro. Não é a caixa estar vazia.
- `I2` — p == NULL e teste, nao desreferencia.
    - em linguagem corrente: Comparar p == NULL só olha o que está dentro de p. Não vai a lugar nenhum.
- `I3` — *p com p nulo nao acessa objeto: comportamento indefinido.
    - em linguagem corrente: Então *p com p em NULL manda o programa a um endereço onde não existe caixa nenhuma.
- `I4` — NULL igual a 0 vale na linguagem-fonte, nao no padrao de bits.
    - em linguagem corrente: p == 0 funciona no código que você escreve. Isso não quer dizer que os bits guardados sejam zeros.

## kc_06 — Passagem por referencia

Conclusão (`I5`): C passa tudo por valor. Uma funcao recebe copia do argumento; para modificar o objeto do chamador, precisa receber o endereco dele.

Prerequisitos declarados: kc_04. O percurso deste tópico alcança 12 nós, sendo 5 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 8 | — | — |
| `B2` | observável | espinha | — | 9 | — | — |
| `I1` | inferência | espinha | B1, B2 | 8 | function_gets_original (T) | ciu_kc06_001 n2 |
| `I2` | inferência | espinha | B2, kc_04:B2 | 7 | — | ciu_kc06_003 n2 |
| `I3` | inferência | espinha | I2, kc_04:I4 | 1 | — | ciu_kc06_003 n2, ciu_kc06_004 n3 |
| `I4` | inferência | órfão | I1, I2 | 6 | pointer_copy_is_alias (T) | ciu_kc06_002 n2, ciu_kc06_004 n3 |
| `I5` | inferência | espinha | I1, I3 | 1 | — | — |

**O que cada nó afirma**

- `B1` — Ao chamar f(x), o parametro e variavel nova, local a f.
    - em linguagem corrente: Ao chamar f(x), a função cria uma caixa nova para o parâmetro — uma caixa só dela.
- `B2` — O valor de x e copiado para essa variavel.
    - em linguagem corrente: O valor de x é copiado para dentro dessa caixa nova.
- `I1` — Modificar o parametro nao afeta x.
    - em linguagem corrente: Então mexer nessa caixa nova não mexe em x. São duas caixas em lugares diferentes.
- `I2` — Se o argumento e &x, f recebe copia do endereco.
    - em linguagem corrente: Se você passa &x, o que é copiado é o endereço de x. E um endereço copiado ainda leva ao mesmo lugar.
- `I3` — *p = v dentro de f altera x.
    - em linguagem corrente: Por isso *p = 7 dentro de f troca o conteúdo de x: p leva até a caixa de x.
- `I4` — Atribuir a p dentro de f nao altera o ponteiro do chamador.
    - em linguagem corrente: Mas trocar o próprio p dentro de f não muda o ponteiro de quem chamou: esse p também é cópia.
- `I5` — C nao tem passagem por referencia: passa enderecos por valor.
    - em linguagem corrente: C sempre copia o que você passa. Passar um endereço é copiar o endereço — e é isso que dá acesso ao original.

## kc_07 — Ponteiro e array · **piloto**

Conclusão (`I1`): Array e ponteiro sao tipos distintos. Em quase toda expressao o nome do array converte-se no endereco do primeiro elemento, mas o array nao e um ponteiro.

Prerequisitos declarados: kc_04, kc_06. O percurso deste tópico alcança 10 nós, sendo 1 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 6 | string_literal_is_array (L) | ciu_kc07_006 n2, ciu_kc07_007 n1, ciu_kc07_008 n3 |
| `B2` | observável | espinha | — | 5 | — | — |
| `B3` | observável | espinha | — | 7 | — | — |
| `B4` | observável | órfão | — | 2 | — | — |
| `I1` | inferência | espinha | B1, B2, B3 | 5 | array_is_pointer (L) | ciu_kc07_001 n2 |
| `I2` | inferência | corolário | B1, I1 | 1 | array_is_assignable (L) | ciu_kc07_003 n2, ciu_kc07_009 n2 |
| `I3` | inferência | corolário | B4, I1 | 1 | sizeof_array_via_pointer (L) | ciu_kc07_002 n3 |
| `I4` | inferência | órfão | B3, kc_06:B2 | 1 | array_passed_by_reference (L) | ciu_kc07_004 n2, ciu_kc07_010 n3 |
| `I5` | inferência | corolário | B4, I1 | 1 | arr_equals_addr_of_arr (L) | ciu_kc07_005 n3, ciu_kc07_011 n3 |

**O que cada nó afirma**

- `B1` — int a[5] reserva 5 ints contiguos e nomeados.
    - em linguagem corrente: int a[5] cria 5 caixas de inteiro grudadas uma na outra. O nome a vale para o conjunto inteiro, não para uma caixa só.
- `B2` — int *p reserva so o ponteiro.
    - em linguagem corrente: int *p cria uma caixa só: a de p. Nenhuma caixa de inteiro nasce junto.
    - importado de `kc_03:I1`
- `B3` — Em expressao, o nome do array converte-se em ponteiro ao primeiro elemento.
    - em linguagem corrente: Quando você usa a numa conta, C troca a pelo endereço da primeira caixa.
- `B4` — Ha contextos onde a conversao nao ocorre: sizeof e &.
    - em linguagem corrente: Essa troca acontece quase sempre. Em dois lugares ela não acontece: sizeof(a) e &a.
- `I1` — a e p tem tipos diferentes, ainda que a[i] e p[i] se parecam.
    - em linguagem corrente: a e p são coisas diferentes, mesmo que a[i] e p[i] se escrevam do mesmo jeito.
- `I2` — Nao se atribui ao nome do array: nao e modificavel.
    - em linguagem corrente: Dá para trocar o que está dentro de cada caixa. Não dá para trocar o conjunto inteiro por outro.
- `I3` — sizeof(a) da o array; sizeof(p), o ponteiro.
    - em linguagem corrente: sizeof(a) mede as 5 caixas juntas. sizeof(p) mede só a caixa de p.
- `I4` — Como parametro, int a[] e reescrito como int *a; dai a perda do tamanho.
    - em linguagem corrente: Ao passar um array para uma função, só o endereço da primeira caixa viaja. Lá dentro não dá mais para saber quantas caixas eram.
- `I5` — arr e &arr apontam ao mesmo lugar, com tipos diferentes.
    - em linguagem corrente: arr e &arr marcam o mesmo ponto na memória, mas não significam a mesma coisa.

## kc_11 — Aritmetica de ponteiros · **piloto**

Conclusão (`I2`): p + n avanca n elementos do tipo apontado, nao n bytes. A escala vem do tipo, e o compilador a aplica sozinho.

Prerequisitos declarados: kc_04, kc_07. O percurso deste tópico alcança 10 nós, sendo 1 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 3 | — | — |
| `B2` | observável | espinha | — | 3 | — | — |
| `B3` | observável | espinha | — | 3 | — | — |
| `B4` | observável | espinha | — | 3 | — | — |
| `I1` | inferência | espinha | B1, B3 | 3 | — | ciu_kc11_002 n1, ciu_kc11_005 n3, ciu_kc11_006 n1, ciu_kc11_007 n2 |
| `I2` | inferência | espinha | B2, B4, I1 | 3 | ptr_arith_is_bytes (L) | ciu_kc11_001 n3, ciu_kc11_002 n1, ciu_kc11_005 n3, ciu_kc11_007 n2 |
| `I3` | inferência | corolário | I2 | 0 | — | ciu_kc11_001 n3 |
| `I4` | inferência | órfão | I1, kc_07:B3 | 0 | — | ciu_kc11_003 n2 |
| `I5` | inferência | corolário | B1, I2 | 1 | voidptr_arith_ok (L) | ciu_kc11_004 n2, ciu_kc11_008 n3 |

**O que cada nó afirma**

- `B1` — p aponta para um objeto de um tipo definido.
    - em linguagem corrente: Todo ponteiro sabe o tipo do que está no destino. Não existe ponteiro sem essa informação.
- `B2` — Objetos de um tipo tem tamanho fixo, dado por sizeof.
    - em linguagem corrente: Cada tipo tem um tamanho fixo, sempre o mesmo. sizeof diz qual é.
- `B3` — Elementos de um array sao contiguos.
    - em linguagem corrente: Os elementos de um array ficam grudados, um logo depois do outro, sem buraco entre eles.
    - importado de `kc_07:B1`
- `B4` — O compilador conhece o tipo de p em tempo de compilacao.
    - em linguagem corrente: O compilador já sabe o tipo de p antes de o programa rodar — está escrito na declaração.
- `I1` — p + 1 precisa chegar ao proximo objeto, nao ao proximo byte.
    - em linguagem corrente: Então p + 1 tem de cair na próxima caixa inteira. Cair no meio de uma caixa não serviria para nada.
- `I2` — Logo o compilador multiplica por sizeof(*p) sozinho.
    - em linguagem corrente: Como o compilador sabe o tamanho da caixa, ele mesmo faz a conta. Você escreve p + 1; ele anda uma caixa inteira.
- `I3` — Multiplicar por sizeof na mao escala duas vezes.
    - em linguagem corrente: Se você multiplicar por sizeof também, a conta é feita duas vezes e o ponteiro pula longe demais.
- `I4` — a[i] e exatamente *(a + i).
    - em linguagem corrente: a[i] é só outro jeito de escrever *(a + i): ande i caixas a partir do começo e olhe o que tem lá.
- `I5` — void * nao tem aritmetica: sem tipo, nao ha escala.
    - em linguagem corrente: Um void * não sabe o tamanho do destino. Sem isso não há quanto andar, e a conta simplesmente não existe.

## kc_08 — Alocacao dinamica

Conclusão (`I4`): malloc reserva um bloco no heap e devolve seu endereco, ou NULL se falhar. O bloco nao e inicializado e vive ate o free.

Prerequisitos declarados: kc_01, kc_02, kc_05. O percurso deste tópico alcança 14 nós, sendo 6 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | órfão | — | 0 | — | — |
| `B2` | observável | órfão | — | 1 | — | — |
| `B3` | observável | órfão | — | 1 | — | — |
| `B4` | observável | espinha | — | 1 | — | — |
| `I1` | inferência | órfão | B1, B2, kc_02:I1 | 0 | — | ciu_kc08_003 n1 |
| `I2` | inferência | órfão | B2, kc_05:I1 | 1 | malloc_always_succeeds (N) | ciu_kc08_002 n2 |
| `I3` | inferência | órfão | B3 | 1 | malloc_initializes_zero (L) | ciu_kc08_001 n2 |
| `I4` | inferência | espinha | B4 | 1 | — | ciu_kc08_004 n2 |

**O que cada nó afirma**

- `B1` — malloc(n) pede n bytes ao alocador.
    - em linguagem corrente: malloc(n) pede emprestado um pedaço de memória com n bytes.
- `B2` — malloc devolve o endereco do bloco, ou NULL.
    - em linguagem corrente: Ele devolve o endereço do pedaço que arrumou — ou NULL, se não conseguiu arrumar.
- `B3` — O bloco devolvido nao tem conteudo definido.
    - em linguagem corrente: O que está dentro desse pedaço é sobra: ninguém limpou antes de entregar.
- `B4` — O bloco nao morre com a funcao que o pediu.
    - em linguagem corrente: Esse pedaço não some quando a função que o pediu termina.
    - importado de `kc_01:B3`
- `I1` — O ponteiro e uma variavel; o bloco e outra coisa.
    - em linguagem corrente: A caixa do ponteiro e o pedaço emprestado são duas coisas diferentes, em áreas diferentes.
- `I2` — Verificar NULL e necessario: falhar e resultado possivel.
    - em linguagem corrente: Como NULL é uma das respostas possíveis, é preciso conferir antes de usar o que veio.
- `I3` — O conteudo precisa ser escrito antes de lido.
    - em linguagem corrente: Você precisa escrever ali antes de ler, senão está lendo a sobra de outra pessoa.
- `I4` — Ninguem libera o bloco por voce.
    - em linguagem corrente: E ninguém devolve esse pedaço por você. Enquanto não devolver, ele continua ocupado.

## kc_09 — free() e dangling pointer · **piloto**

Conclusão (`I4`): free(p) devolve o bloco ao alocador. p continua existindo com o mesmo endereco, que agora nao designa objeto valido.

Prerequisitos declarados: kc_08, kc_06. O percurso deste tópico alcança 19 nós, sendo 9 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 3 | — | — |
| `B2` | observável | espinha | — | 4 | — | — |
| `B3` | observável | espinha | — | 3 | — | — |
| `B4` | observável | espinha | — | 3 | — | — |
| `I1` | inferência | espinha | B2, kc_06:I4 | 4 | free_nullifies (L) | ciu_kc09_001 n2 |
| `I2` | inferência | espinha | B4, I1 | 3 | free_kills_pointer (L) | ciu_kc09_001 n2, ciu_kc09_004 n1, ciu_kc09_007 n2 |
| `I3` | inferência | espinha | B1, B3 | 3 | heap_persists (L), double_free_is_safe (N) | ciu_kc09_002 n2, ciu_kc09_005 n3, ciu_kc09_008 n3 |
| `I4` | inferência | espinha | I2, I3 | 1 | — | ciu_kc09_003 n3 |
| `I5` | inferência | corolário | I4 | 0 | — | ciu_kc09_002 n2 |
| `I6` | inferência | órfão | I2, kc_05:I1 | 1 | null_after_free_redundant (L) | ciu_kc09_003 n3, ciu_kc09_006 n2 |

**O que cada nó afirma**

- `B1` — free recebe o endereco do bloco.
    - em linguagem corrente: free recebe o endereço do pedaço que você quer devolver.
- `B2` — free(p) recebe uma copia de p.
    - em linguagem corrente: Ao chamar free(p), o que entra na função é uma cópia de p — como em qualquer chamada.
    - importado de `kc_06:I1`
- `B3` — Devolver o bloco o marca como nao mais valido.
    - em linguagem corrente: Devolvido, o pedaço deixa de ser seu. Pode ser entregue a outro pedido a qualquer momento.
- `B4` — p e variavel do chamador.
    - em linguagem corrente: A caixa p é sua, de quem chamou. Ela não pertence à função free.
    - importado de `kc_02:I2`
- `I1` — free nao pode alterar p, nem se quisesse.
    - em linguagem corrente: Então free não tem como mudar o que está dentro de p: ela só recebeu uma cópia do valor.
- `I2` — p continua existindo, com o mesmo valor.
    - em linguagem corrente: Depois do free, a caixa p continua ali, com o mesmo endereço escrito dentro.
- `I3` — O bloco deixou de ser valido.
    - em linguagem corrente: Mas o pedaço para onde ela aponta já não é seu.
- `I4` — p guarda endereco que nao designa objeto: dangling pointer.
    - em linguagem corrente: Juntando: p continua com um endereço bom de aparência, apontando para um lugar que já não guarda nada seu. E nada no programa avisa isso.
- `I5` — Usar p depois, mesmo sem desreferenciar, e comportamento indefinido.
    - em linguagem corrente: Depois disso, até copiar ou comparar p já é território sem garantia — não é preciso chegar a usar *p.
- `I6` — Atribuir NULL a p e o que registra o estado.
    - em linguagem corrente: Escrever NULL em p logo depois do free deixa registrado que ela não aponta mais para nada.

## kc_12 — Dangling por escopo

Conclusão (`I3`): Uma variavel local deixa de existir quando a funcao retorna. Um ponteiro para ela sobrevive e passa a nao designar objeto valido, sem que nenhum free tenha sido chamado.

Prerequisitos declarados: kc_01, kc_04, kc_06. O percurso deste tópico alcança 17 nós, sendo 8 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 2 | — | — |
| `B2` | observável | espinha | — | 3 | — | — |
| `B3` | observável | espinha | — | 2 | — | — |
| `B4` | observável | espinha | — | 2 | — | — |
| `I1` | inferência | espinha | B3, B4 | 2 | — | ciu_kc12_001 n2 |
| `I2` | inferência | espinha | B1, B2, I1 | 2 | local_survives_return (T) | ciu_kc12_001 n2 |
| `I3` | inferência | espinha | I2 | 1 | — | ciu_kc12_003 n3 |
| `I4` | inferência | órfão | B2 | 1 | static_is_scope (T) | ciu_kc12_002 n2 |
| `I5` | inferência | órfão | I2, kc_06:I3 | 0 | — | ciu_kc12_004 n3 |

**O que cada nó afirma**

- `B1` — Variaveis locais existem durante a execucao da funcao.
    - em linguagem corrente: As caixas criadas dentro de uma função existem enquanto ela está rodando.
    - importado de `kc_01:B2`
- `B2` — O retorno da funcao encerra a existencia das suas locais.
    - em linguagem corrente: Quando a função retorna, essas caixas deixam de existir. Ninguém precisa mandar apagar.
- `B3` — &local e endereco valido enquanto a funcao executa.
    - em linguagem corrente: Enquanto a função roda, o endereço de uma caixa dela é um endereço perfeitamente bom.
    - importado de `kc_04:B2`
- `B4` — O valor retornado e copiado para o chamador.
    - em linguagem corrente: O que a função retorna é copiado para quem chamou. É sempre uma cópia do valor.
    - importado de `kc_06:B2`
- `I1` — Retornar &local copia um endereco, nao o objeto.
    - em linguagem corrente: Então retornar &local copia o endereço, não a caixa. A caixa fica para trás.
- `I2` — Quando o chamador recebe o endereco, o objeto ja nao existe.
    - em linguagem corrente: Quando quem chamou recebe esse endereço, a caixa já sumiu: ela sumiu no mesmo instante do retorno.
- `I3` — Logo ha dangling sem nenhum free.
    - em linguagem corrente: Juntando: dá para acabar com um ponteiro apontando para o nada sem ter chamado free uma única vez.
- `I4` — static muda a duracao, nao o escopo; por isso as vezes parece funcionar.
    - em linguagem corrente: Marcar a caixa como static faz ela durar o programa inteiro, mas o nome continua só de dentro da função. Sem static, o lugar pode ainda guardar o valor antigo — e aí o erro parece funcionar.
- `I5` — O caminho correto e o chamador fornecer o armazenamento.
    - em linguagem corrente: O jeito certo é quem chama criar a caixa e passar o endereço dela para a função preencher.

## kc_10 — Ponteiro para ponteiro

Conclusão (`I2`): int **pp e uma variavel cujo valor e o endereco de um int *. Cada * desfaz exatamente um nivel de indirecao.

Prerequisitos declarados: kc_04, kc_06, kc_07. O percurso deste tópico alcança 15 nós, sendo 7 de outros tópicos.

| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |
| --- | --- | --- | --- | --- | --- | --- |
| `B1` | observável | espinha | — | 3 | — | — |
| `B2` | observável | espinha | — | 3 | — | — |
| `B3` | observável | espinha | — | 2 | — | — |
| `B4` | observável | órfão | — | 1 | — | — |
| `I1` | inferência | espinha | B1, B2 | 3 | — | ciu_kc10_004 n2 |
| `I2` | inferência | espinha | B3, I1 | 2 | double_deref_is_data (L) | ciu_kc10_002 n2 |
| `I3` | inferência | órfão | I1, kc_06:I4 | 1 | modify_pp_changes_p (L) | ciu_kc10_001 n2, ciu_kc10_004 n2 |
| `I4` | inferência | órfão | B4, kc_07:B3 | 1 | array2d_is_double_pointer (L) | ciu_kc10_003 n3 |

**O que cada nó afirma**

- `B1` — Um ponteiro e variavel e, como toda variavel, tem endereco.
    - em linguagem corrente: Um ponteiro é uma caixa. E toda caixa tem endereço próprio.
    - importado de `kc_02:B2`
- `B2` — &p produz o endereco de p, que e um int duplo ponteiro.
    - em linguagem corrente: &p dá o endereço da caixa p. Guardar esse endereço exige uma caixa de mais um nível.
    - importado de `kc_04:B2`
- `B3` — Cada aplicacao de * desfaz um nivel.
    - em linguagem corrente: Cada * dá um passo: vai de uma caixa até a caixa cujo endereço ela guarda.
- `B4` — O tipo diz quantos niveis existem; nao e opcional.
    - em linguagem corrente: O tipo é que diz quantos passos existem até o valor. Não dá para chutar nem descobrir depois.
- `I1` — pp e p sao variaveis distintas, em niveis distintos.
    - em linguagem corrente: Então pp e p são duas caixas diferentes, uma guardando o endereço da outra.
- `I2` — *pp e o ponteiro p; **pp e o int.
    - em linguagem corrente: *pp chega em p. **pp dá mais um passo e chega no número.
- `I3` — Para uma funcao alterar o p do chamador, precisa receber &p.
    - em linguagem corrente: Para uma função mudar o p de quem chamou, ela precisa receber o endereço de p — não o p.
- `I4` — int a[N][M] nao e int duplo ponteiro: e bloco contiguo, nao vetor de ponteiros.
    - em linguagem corrente: int a[3][4] é um bloco de 12 caixas grudadas. Não são três caixas apontando para fileiras separadas.

## O que pede decisão sua

### Nós que nenhuma atividade mede (41 de 93)

Estes nós só podem ser ACEITOS no percurso, nunca demonstrados. Se um
deles é premissa de carga (muitos caminhos), vale escrever atividade.

| Nó | Caminhos | Enunciado |
| --- | --- | --- |
| `kc_04:B2` | 10 | &x devolve o endereco de x; nao copia x. |
| `kc_06:B2` | 9 | O valor de x e copiado para essa variavel. |
| `kc_06:B1` | 8 | Ao chamar f(x), o parametro e variavel nova, local a f. |
| `kc_07:B3` | 7 | Em expressao, o nome do array converte-se em ponteiro ao primeiro elemento. |
| `kc_02:B3` | 5 | O valor guardado em p e um endereco. |
| `kc_07:B2` | 5 | int *p reserva so o ponteiro. |
| `kc_01:B1` | 4 | O programa tem memoria propria enquanto executa. |
| `kc_04:B3` | 4 | p guarda um endereco. |
| `kc_09:B2` | 4 | free(p) recebe uma copia de p. |
| `kc_02:B2` | 3 | p e uma variavel: ocupa espaco e tem endereco proprio. |
| `kc_03:B1` | 3 | A declaracao reserva espaco para a variavel declarada. |
| `kc_03:B2` | 3 | int *p declara p, nao *p. |
| `kc_05:B2` | 3 | A constante 0 em contexto de ponteiro vira o ponteiro nulo. |
| `kc_11:B1` | 3 | p aponta para um objeto de um tipo definido. |
| `kc_11:B2` | 3 | Objetos de um tipo tem tamanho fixo, dado por sizeof. |
| `kc_11:B3` | 3 | Elementos de um array sao contiguos. |
| `kc_11:B4` | 3 | O compilador conhece o tipo de p em tempo de compilacao. |
| `kc_09:B1` | 3 | free recebe o endereco do bloco. |
| `kc_09:B3` | 3 | Devolver o bloco o marca como nao mais valido. |
| `kc_09:B4` | 3 | p e variavel do chamador. |
| `kc_12:B2` | 3 | O retorno da funcao encerra a existencia das suas locais. |
| `kc_10:B1` | 3 | Um ponteiro e variavel e, como toda variavel, tem endereco. |
| `kc_10:B2` | 3 | &p produz o endereco de p, que e um int duplo ponteiro. |
| `kc_02:B1` | 2 | Todo objeto na memoria tem um endereco. |
| `kc_03:B3` | 2 | C nao zera variaveis automaticas. |

### Nós que nenhuma crença nega (61)

O diagnóstico nunca chega a eles por erro do aluno: eles existem como
degrau do percurso. Isso é legítimo — mas um nó de inferência com muitos
caminhos e nenhuma crença costuma ser lugar onde falta mapear erro.

| Nó | Tipo | Caminhos | Enunciado |
| --- | --- | --- | --- |
| `kc_06:I2` | inferência | 7 | Se o argumento e &x, f recebe copia do endereco. |
| `kc_01:I1` | inferência | 4 | Existem duas disciplinas de vida distintas. |
| `kc_04:I2` | inferência | 4 | *p vai ate o endereco e acessa o que esta la. |
| `kc_11:I1` | inferência | 3 | p + 1 precisa chegar ao proximo objeto, nao ao proximo byte. |
| `kc_10:I1` | inferência | 3 | pp e p sao variaveis distintas, em niveis distintos. |
| `kc_05:I1` | inferência | 2 | NULL e um valor de ponteiro, nao um nao-valor. |
| `kc_12:I1` | inferência | 2 | Retornar &local copia um endereco, nao o objeto. |

### Nós que talvez precisem ser divididos (9)

Heurística, não regra: o enunciado tem ponto e vírgula, "mas" ou
"porque" ligando duas afirmações, ou passa de 16 palavras. O aluno pode
concordar com metade da frase e o sistema registra que ele concordou com
tudo — é aqui que o grafo está raso e a granularidade precisa aumentar.

| Nó | Sinal | Enunciado |
| --- | --- | --- |
| `kc_04:B2` | ; | &x devolve o endereco de x; nao copia x. |
| `kc_04:B4` | ; | Na declaracao o * pertence ao tipo; na expressao e operador. |
| `kc_07:I3` | ; | sizeof(a) da o array; sizeof(p), o ponteiro. |
| `kc_07:I4` | ; | Como parametro, int a[] e reescrito como int *a; dai a perda do tamanho. |
| `kc_08:I1` | ; | O ponteiro e uma variavel; o bloco e outra coisa. |
| `kc_09:I5` | , e | Usar p depois, mesmo sem desreferenciar, e comportamento indefinido. |
| `kc_12:I4` | ; | static muda a duracao, nao o escopo; por isso as vezes parece funcionar. |
| `kc_10:B4` | ; | O tipo diz quantos niveis existem; nao e opcional. |
| `kc_10:I2` | ; | *pp e o ponteiro p; **pp e o int. |

### Cobertura de nível por tópico

A sessão começa no nível 1 e sobe um degrau por vez. Tópico sem algum
degrau não consegue oferecer a escada inteira.

| Tópico | n1 | n2 | n3 | Atividades | Crenças |
| --- | --- | --- | --- | --- | --- |
| kc_01 ⚠ falta n3 | 1 | 3 | 0 | 4 | 2 |
| kc_02 | 1 | 2 | 4 | 7 | 4 |
| kc_03 ⚠ falta n3 | 1 | 2 | 0 | 3 | 2 |
| kc_04 ⚠ falta n3 | 1 | 3 | 0 | 4 | 2 |
| kc_05 | 1 | 2 | 1 | 4 | 2 |
| kc_06 ⚠ falta n1 | 0 | 3 | 1 | 4 | 2 |
| kc_07 | 1 | 5 | 5 | 11 | 6 |
| kc_11 | 2 | 3 | 3 | 8 | 2 |
| kc_08 ⚠ falta n3 | 1 | 3 | 0 | 4 | 2 |
| kc_09 | 1 | 4 | 3 | 8 | 5 |
| kc_12 ⚠ falta n1 | 0 | 2 | 2 | 4 | 2 |
| kc_10 ⚠ falta n1 | 0 | 3 | 1 | 4 | 3 |

### Crenças por procedência

| Procedência | O que significa | Quantas |
| --- | --- | --- |
| D | documentada: achado empírico com fonte e página | 1 |
| T | transposta de outra linguagem, com analogia declarada | 7 |
| L | registrada como erro comum em obra técnica de C | 23 |
| N | o erro está em norma (CERT C, CWE); a crença, não | 3 |
| E | elaborada a partir do modelo de máquina; hipótese a testar | 0 |

