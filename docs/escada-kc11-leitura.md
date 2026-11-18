# A escada do kc_11 — Aritmética de ponteiros

Texto para leitura, gerado de `mvp/dominio/escada_kc11.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — Todo ponteiro sabe o tipo do que está no destino. Não existe ponteiro sem essa informação.

### Degrau 1 — guiado, escolher

> Um ponteiro guarda um endereço e sabe o tipo do que está lá: int *p aponta para um int, char *c para um char.
> O tipo vem escrito na declaração. Ponteiro não é um número solto.

**Versão 1.** O que a declaração int *p; diz sobre p?

Já está escrito:

```c
int *p;
```

Opções: `Que p guarda o endereço de um int`  `Nada além de um número: ponteiro é só um número inteiro, e dá para trocar um pelo outro`  `Que p guarda um int`

Resposta certa: `Que p guarda o endereço de um int`

Se errar:

- respondeu `Nada além de um número: ponteiro é só um número inteiro, e dá para trocar um pelo outro` → Ponteiro não é um número solto: a declaração diz que p guarda o endereço de um int. É assim que o * sabe o que ler lá. _(aponta a crença `pointer_is_integer`)_
- respondeu `Que p guarda um int` → Quem guarda um int é int x;. A estrela de int *p diz outra coisa: p guarda o ENDEREÇO de um int.
- qualquer outro erro → int *p; diz que p guarda o endereço de um int: endereço, e com o tipo do destino.

**Versão 2.** O que a declaração char *c; diz sobre c?

Já está escrito:

```c
char *c;
```

Opções: `Que c guarda um char`  `Que c guarda o endereço de um char`  `Nada além de um número: ponteiro é só um número inteiro, e dá para trocar um pelo outro`

Resposta certa: `Que c guarda o endereço de um char`

Se errar:

- respondeu `Nada além de um número: ponteiro é só um número inteiro, e dá para trocar um pelo outro` → Ponteiro não é um número solto: a declaração diz que c guarda o endereço de um char. É assim que o * sabe o que ler lá. _(aponta a crença `pointer_is_integer`)_
- respondeu `Que c guarda um char` → Quem guarda um char é char x;. A estrela de char *c diz outra coisa: c guarda o ENDEREÇO de um char.
- qualquer outro erro → char *c; diz que c guarda o endereço de um char: endereço, e com o tipo do destino.

### Degrau 2 — guiado, completar

> Por isso o compilador reclama de p = 1000;: 1000 é um int, e p quer o endereço de um int.

**Versão 1.** Complete com o que cabe em p.

Já está escrito:

```c
int idade = 15;
int *p;
```

```c
p = ___;
```

Peças: `&idade`  `idade`  `1000`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = idade;` → idade guarda um número, e p quer um endereço: o compilador reclama. O endereço de idade é &idade.
- respondeu `p = 1000;` → 1000 é um int, e não o endereço de um int: o compilador reclama. O que cabe em p é &idade.
- qualquer outro erro → Em p cabe o endereço de um int: p = &idade;

**Versão 2.** Complete com o que cabe em q.

Já está escrito:

```c
int nota = 7;
int *q;
```

```c
q = ___;
```

Peças: `500`  `&nota`  `nota`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = nota;` → nota guarda um número, e q quer um endereço: o compilador reclama. O endereço de nota é &nota.
- respondeu `q = 500;` → 500 é um int, e não o endereço de um int: o compilador reclama. O que cabe em q é &nota.
- qualquer outro erro → Em q cabe o endereço de um int: q = &nota;

### Degrau 3 — guiado, digitar

> p + 1 é o endereço da caixa seguinte. Quanto andar, p sabe pelo tipo: uma caixa de int inteira.

**Versão 1.** p aponta para notas[0]. Que número aparece?

```c
int notas[3] = {7, 8, 9};
int *p = notas;

printf("%d\n", *(p + 1));
```

Resposta certa: `8`

Se errar:

- digitou `7` → 7 está em notas[0], onde p aponta. p + 1 é a caixa seguinte, e o * lê o que está nela: 8.
- digitou `9` → 9 está duas caixas adiante, em notas[2]. p + 1 anda uma caixa só: 8.
- qualquer outro erro → p + 1 é a caixa seguinte a notas[0]: notas[1], que guarda 8.

**Versão 2.** q aponta para pontos[0]. Que número aparece?

```c
int pontos[3] = {3, 6, 9};
int *q = pontos;

printf("%d\n", *(q + 1));
```

Resposta certa: `6`

Se errar:

- digitou `3` → 3 está em pontos[0], onde q aponta. q + 1 é a caixa seguinte, e o * lê o que está nela: 6.
- digitou `9` → 9 está duas caixas adiante, em pontos[2]. q + 1 anda uma caixa só: 6.
- qualquer outro erro → q + 1 é a caixa seguinte a pontos[0]: pontos[1], que guarda 6.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Ponteiro guarda endereço, e não um número qualquer_

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int nota = 7;
int *q;
```

Opções: `q = 7;`  `q = &nota;`  `q = nota;`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = 7;` → 7 é um int, e q quer o endereço de um int: o compilador reclama. O que serve é &nota.
- respondeu `q = nota;` → nota guarda um número, e q guarda endereço: o compilador reclama. O endereço de nota é &nota.
- qualquer outro erro → q guarda o endereço de um int: q = &nota;

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idade = 15;
int *p;
```

Opções: `p = idade;`  `p = 15;`  `p = &idade;`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = 15;` → 15 é um int, e p quer o endereço de um int: o compilador reclama. O que serve é &idade.
- respondeu `p = idade;` → idade guarda um número, e p guarda endereço: o compilador reclama. O endereço de idade é &idade.
- qualquer outro erro → p guarda o endereço de um int: p = &idade;

### Degrau 5 — prática, digitar

**Versão 1.** Que número aparece?

```c
int dias[3] = {28, 30, 31};
int *q = dias;

printf("%d\n", *(q + 2));
```

Resposta certa: `31`

Se errar:

- digitou `28` → 28 está em dias[0], onde q aponta. q + 2 anda duas caixas de int: dias[2], que guarda 31.
- digitou `30` → 30 está em dias[1], uma caixa adiante. q + 2 anda duas: 31.
- qualquer outro erro → q + 2 fica duas caixas adiante de dias[0]: dias[2], que guarda 31.

**Versão 2.** Que número aparece?

```c
int notas[3] = {5, 10, 15};
int *p = notas;

printf("%d\n", *(p + 1));
```

Resposta certa: `10`

Se errar:

- digitou `5` → 5 está em notas[0], onde p aponta. p + 1 anda uma caixa de int: notas[1], que guarda 10.
- digitou `15` → 15 está duas caixas adiante, em notas[2]. p + 1 anda uma caixa só: 10.
- qualquer outro erro → p + 1 é a caixa seguinte a notas[0]: notas[1], que guarda 10.

### Se errar a pergunta do topo: a revisão

> Um ponteiro guarda um endereço, e a declaração diz o tipo do que está lá: int *p aponta para um int.
> Por isso o * lê um int inteiro, e p não aceita um número qualquer.

```c
int idade = 15;
int *p = &idade;

printf("%d\n", *p + 1);
```

A máquina imprime:

```
16
```

### Se a pessoa disser a crença: a prova

Você disse:

> Ponteiro é só um número inteiro; dá para trocar um pelo outro.

```c
int idade = 15;
int *p;

p = &idade;
p = 1000;
```

**p é um int *. As duas últimas linhas guardam alguma coisa em p. De qual delas o compilador reclama?**

- De nenhuma: ponteiro é só um número, e 1000 é um número _(é o que a crença espera)_
- Da última: 1000 é um int, e p quer um endereço de int _(é o que a máquina faz)_

O compilador reclama:

```
makes pointer from integer without a cast
```

_Mensagem do gcc 16.2. Nele a reclamação é um erro; em versões mais antigas, um aviso. Nos dois casos ele reclama da última linha, e só dela._

O que isto mostra: O compilador aceita p = &idade; e reclama de p = 1000;. Ponteiro não é um número qualquer: guarda um endereço e sabe o tipo do que está lá. 1000 é um int, e não o endereço de um int.

## B2 — Cada tipo tem um tamanho fixo, e esse tamanho está na declaração — o compilador já sabe qual é antes de o programa rodar.

### Degrau 1 — guiado, escolher

> O tamanho de um tipo é fixo: todo char ocupa 1 byte, e todo int ocupa o mesmo tanto, numa mesma máquina.
> O compilador sabe esse tamanho pela declaração, antes de o programa rodar.

**Versão 1.** Quando o compilador fica sabendo quanto ocupa a caixa para onde c aponta?

Já está escrito:

```c
char *c;
```

Opções: `Na declaração, antes de rodar: char *c diz que lá é um char`  `Em execução: o tamanho vem com o ponteiro, e não da declaração`  `Só depois que c recebe um bloco`

Resposta certa: `Na declaração, antes de rodar: char *c diz que lá é um char`

Se errar:

- respondeu `Em execução: o tamanho vem com o ponteiro, e não da declaração` → O ponteiro não traz tamanho nenhum: guarda um endereço. O tamanho do destino vem da declaração, char *c, e o compilador já o conhece antes de rodar. _(aponta a crença `pointer_knows_block_size`)_
- respondeu `Só depois que c recebe um bloco` → O bloco não muda o tipo: com bloco ou sem, char *c aponta para um char. O compilador sabe isso pela declaração.
- qualquer outro erro → O tamanho do destino vem da declaração: char *c diz que lá é um char, antes de rodar.

**Versão 2.** Quando o compilador fica sabendo quanto ocupa a caixa para onde p aponta?

Já está escrito:

```c
int *p;
```

Opções: `Só depois que p recebe um bloco`  `Em execução: o tamanho vem com o ponteiro, e não da declaração`  `Na declaração, antes de rodar: int *p diz que lá é um int`

Resposta certa: `Na declaração, antes de rodar: int *p diz que lá é um int`

Se errar:

- respondeu `Em execução: o tamanho vem com o ponteiro, e não da declaração` → O ponteiro não traz tamanho nenhum: guarda um endereço. O tamanho do destino vem da declaração, int *p, e o compilador já o conhece antes de rodar. _(aponta a crença `pointer_knows_block_size`)_
- respondeu `Só depois que p recebe um bloco` → O bloco não muda o tipo: com bloco ou sem, int *p aponta para um int. O compilador sabe isso pela declaração.
- qualquer outro erro → O tamanho do destino vem da declaração: int *p diz que lá é um int, antes de rodar.

### Degrau 2 — guiado, digitar

> sizeof *c mede a caixa do destino de c. O compilador responde só pelo tipo, sem olhar o que há em c.

**Versão 1.** c ainda não recebeu valor. Que número aparece?

```c
char *c;

printf("%zu\n", sizeof *c);
```

Resposta certa: `1`

Se errar:

- digitou `0` → c não recebeu valor, mas sizeof não precisa dele: mede o tipo do destino, um char. Sai 1.
- qualquer outro erro → sizeof *c mede um char, pelo tipo da declaração: 1.

**Versão 2.** c aponta para letras, que tem vinte caixas. Que número aparece?

```c
char letras[20];
char *c = letras;

printf("%zu\n", sizeof *c);
```

Resposta certa: `1`

Se errar:

- digitou `20` → letras tem vinte caixas, mas c não guarda esse tamanho. sizeof *c mede o tipo do destino, um char: 1.
- qualquer outro erro → sizeof *c mede um char, pelo tipo da declaração: 1.

### Degrau 3 — guiado, escolher

> Dois ponteiros do mesmo tipo têm o mesmo tamanho de destino, para onde quer que apontem: quem decide é o tipo, e não o bloco.

**Versão 1.** c aponta para um bloco de 10 chars, e d para um de 500. O que dão sizeof *c e sizeof *d?

Já está escrito:

```c
char *c = malloc(10);
char *d = malloc(500);
```

Opções: `O mesmo: o tamanho de um char, nos dois`  `10 e 500: o tamanho vem com o ponteiro, e não da declaração`  `Nada: sizeof não mede o destino de um ponteiro`

Resposta certa: `O mesmo: o tamanho de um char, nos dois`

Se errar:

- respondeu `10 e 500: o tamanho vem com o ponteiro, e não da declaração` → Os blocos são de 10 e de 500, mas c e d não carregam esses números: guardam um endereço cada. sizeof *c e sizeof *d medem um char, nos dois. _(aponta a crença `pointer_knows_block_size`)_
- respondeu `Nada: sizeof não mede o destino de um ponteiro` → sizeof *c mede o destino de c pelo tipo da declaração: um char. Funciona com qualquer ponteiro.
- qualquer outro erro → Os dois medem um char: o tipo decide o tamanho do destino, e não o bloco.

**Versão 2.** p aponta para um bloco de 3 ints, e q para um de 100 ints. O que dão sizeof *p e sizeof *q?

Já está escrito:

```c
int *p = malloc(3 * sizeof(int));
int *q = malloc(100 * sizeof(int));
```

Opções: `Nada: sizeof não mede o destino de um ponteiro`  `O mesmo: o tamanho de um int, nos dois`  `3 e 100 ints: o tamanho vem com o ponteiro, e não da declaração`

Resposta certa: `O mesmo: o tamanho de um int, nos dois`

Se errar:

- respondeu `3 e 100 ints: o tamanho vem com o ponteiro, e não da declaração` → Os blocos são de 3 e de 100 ints, mas p e q não carregam esses números: guardam um endereço cada. sizeof *p e sizeof *q medem um int, nos dois. _(aponta a crença `pointer_knows_block_size`)_
- respondeu `Nada: sizeof não mede o destino de um ponteiro` → sizeof *p mede o destino de p pelo tipo da declaração: um int. Funciona com qualquer ponteiro.
- qualquer outro erro → Os dois medem um int: o tipo decide o tamanho do destino, e não o bloco.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O tamanho vem do tipo, e não do bloco_

**Versão 1.** Que número aparece?

```c
char nome[30] = "ana";
char *c = nome;

printf("%zu\n", sizeof *c);
```

Resposta certa: `1`

Se errar:

- digitou `30` → nome tem 30 caixas, mas c não carrega esse tamanho. sizeof *c mede o tipo do destino, um char: 1.
- digitou `4` → O texto usa quatro caixas, contando a marca de fim, mas sizeof *c não olha o texto: mede um char, 1.
- qualquer outro erro → sizeof *c mede um char, pelo tipo da declaração de c: 1.

**Versão 2.** Que número aparece?

```c
char letras[8];
char *c = letras + 3;

printf("%zu\n", sizeof *c);
```

Resposta certa: `1`

Se errar:

- digitou `5` → De c até o fim de letras restam cinco caixas, mas c não carrega isso. sizeof *c mede o tipo do destino, um char: 1.
- digitou `8` → letras tem oito caixas, mas c não carrega esse tamanho. sizeof *c mede um char: 1.
- qualquer outro erro → sizeof *c mede um char, pelo tipo da declaração de c: 1.

### Degrau 5 — prática, escolher

**Versão 1.** Para responder sizeof *p, o compilador precisa rodar o programa?

Já está escrito:

```c
int *p;
```

Opções: `Não: o tipo está na declaração`  `Precisa: o tamanho vem do bloco para onde p aponta`  `Precisa: p ainda não tem valor`

Resposta certa: `Não: o tipo está na declaração`

Se errar:

- respondeu `Precisa: o tamanho vem do bloco para onde p aponta` → O bloco não entra na conta: sizeof *p mede o tipo do destino, que está escrito em int *p. O compilador responde sem rodar nada.
- respondeu `Precisa: p ainda não tem valor` → sizeof não lê o valor de p: mede o tipo do destino, que está na declaração. O compilador responde sem rodar nada.
- qualquer outro erro → O tipo está na declaração: o compilador responde sizeof *p sem rodar o programa.

**Versão 2.** Para responder sizeof *c, o compilador precisa rodar o programa?

Já está escrito:

```c
char *c;
```

Opções: `Precisa: c ainda não tem valor`  `Precisa: o tamanho vem do bloco para onde c aponta`  `Não: o tipo está na declaração`

Resposta certa: `Não: o tipo está na declaração`

Se errar:

- respondeu `Precisa: o tamanho vem do bloco para onde c aponta` → O bloco não entra na conta: sizeof *c mede o tipo do destino, que está escrito em char *c. O compilador responde sem rodar nada.
- respondeu `Precisa: c ainda não tem valor` → sizeof não lê o valor de c: mede o tipo do destino, que está na declaração. O compilador responde sem rodar nada.
- qualquer outro erro → O tipo está na declaração: o compilador responde sizeof *c sem rodar o programa.

### Se errar a pergunta do topo: a revisão

> Cada tipo tem um tamanho fixo, e o compilador o conhece pela declaração, antes de o programa rodar.
> sizeof *c mede o tipo do destino de c: não precisa do bloco, nem de valor em c.

```c
char letras[5] = "casa";
char *c = letras;

printf("%zu\n", sizeof *c);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> O tamanho vem com o ponteiro, e não da declaração.

```c
char *c = malloc(10);

printf("%zu\n", sizeof *c);
free(c);
```

**c recebe um bloco de dez chars. O trecho mostra sizeof *c. O que aparece?**

- 1 _(é o que a máquina faz)_
- 10: o ponteiro traz o tamanho do bloco que recebeu _(é o que a crença espera)_

A máquina imprime:

```
1
```

O que isto mostra: Saiu 1. sizeof *c mede um char, o tipo que a declaração de c diz. O tamanho do bloco, c não carrega: o compilador respondeu pela declaração, sem olhar para o bloco.

## B3 — Os elementos de um array ficam grudados, um logo depois do outro, sem buraco entre eles.

### Degrau 1 — guiado, escolher

> Os elementos de um array ficam grudados, um logo depois do outro, sem buraco entre eles.
> Por isso a distância de &notas[0] a &notas[2] é de duas caixas: &notas[2] - &notas[0] dá 2.

**Versão 1.** Quantas caixas há de &notas[0] até &notas[2]?

Já está escrito:

```c
int notas[3];
```

Opções: `Duas: as caixas são grudadas`  `Não dá para saber: os elementos ficam espalhados`  `Oito: a distância é contada em bytes`

Resposta certa: `Duas: as caixas são grudadas`

Se errar:

- respondeu `Não dá para saber: os elementos ficam espalhados` → Num array não há espalhado: as caixas ficam uma logo depois da outra. De notas[0] a notas[2] são duas caixas.
- respondeu `Oito: a distância é contada em bytes` → A diferença entre dois endereços do mesmo array conta caixas, e não bytes: de notas[0] a notas[2], duas.
- qualquer outro erro → As caixas são grudadas: de &notas[0] até &notas[2] há duas caixas.

**Versão 2.** Quantas caixas há de &letras[0] até &letras[3]?

Já está escrito:

```c
char letras[4];
```

Opções: `Não dá para saber: os elementos ficam espalhados`  `Três: as caixas são grudadas`  `Quatro: conta-se a caixa de onde se sai`

Resposta certa: `Três: as caixas são grudadas`

Se errar:

- respondeu `Não dá para saber: os elementos ficam espalhados` → Num array não há espalhado: as caixas ficam uma logo depois da outra. De letras[0] a letras[3] são três caixas.
- respondeu `Quatro: conta-se a caixa de onde se sai` → A distância conta os passos, e não as caixas visitadas: de letras[0] a letras[3] são três passos.
- qualquer outro erro → As caixas são grudadas: de &letras[0] até &letras[3] há três caixas.

### Degrau 2 — guiado, escolher

> char s[] = "pai"; cria quatro caixas de char grudadas, cópia do texto, e elas são de s.
> char *t = "pai"; cria uma caixa só, um ponteiro para letras grudadas que não são de t.

**Versão 1.** O que cada uma destas linhas cria?

Já está escrito:

```c
char s[] = "pai";
char *t = "pai";
```

Opções: `s são quatro caixas de char; t é um ponteiro para o texto`  `O mesmo: char *s = "abc" e char s[] = "abc" guardam do mesmo jeito`  `s é um ponteiro para o texto; t são quatro caixas de char`

Resposta certa: `s são quatro caixas de char; t é um ponteiro para o texto`

Se errar:

- respondeu `O mesmo: char *s = "abc" e char s[] = "abc" guardam do mesmo jeito` → O texto é o mesmo, mas guardado de outro jeito: s são quatro caixas de char, que são de s; t é uma caixa só, que aponta para letras de fora. _(aponta a crença `string_literal_is_array`)_
- respondeu `s é um ponteiro para o texto; t são quatro caixas de char` → É o contrário: os colchetes de s[] criam as caixas, e a estrela de *t cria um ponteiro.
- qualquer outro erro → s são quatro caixas de char, que são de s; t é um ponteiro para o texto.

**Versão 2.** O que cada uma destas linhas cria?

Já está escrito:

```c
char *u = "ana";
char nome[] = "ana";
```

Opções: `u são quatro caixas de char; nome é um ponteiro para o texto`  `u é um ponteiro para o texto; nome são quatro caixas de char`  `O mesmo: char *s = "abc" e char s[] = "abc" guardam do mesmo jeito`

Resposta certa: `u é um ponteiro para o texto; nome são quatro caixas de char`

Se errar:

- respondeu `O mesmo: char *s = "abc" e char s[] = "abc" guardam do mesmo jeito` → O texto é o mesmo, mas guardado de outro jeito: nome são quatro caixas de char, que são de nome; u é uma caixa só, que aponta para letras de fora. _(aponta a crença `string_literal_is_array`)_
- respondeu `u são quatro caixas de char; nome é um ponteiro para o texto` → É o contrário: os colchetes de nome[] criam as caixas, e a estrela de *u cria um ponteiro.
- qualquer outro erro → u é um ponteiro para o texto; nome são quatro caixas de char, que são de nome.

### Degrau 3 — guiado, digitar

> Grudadas, as caixas ficam em fila: de notas[1] a notas[3] há duas caixas de distância.

**Versão 1.** A última linha pergunta se a distância é 2. Que número aparece?

```c
int notas[4];

printf("%d\n", &notas[3] - &notas[1] == 2);
```

Resposta certa: `1`

Se errar:

- digitou `0` → notas[1] e notas[3] ficam a duas caixas uma da outra, sem buraco: a pergunta é verdadeira, 1.
- digitou `2` → O printf mostra a resposta da pergunta, e não a distância. A distância é 2, e a pergunta é verdadeira: 1.
- qualquer outro erro → De notas[1] a notas[3] há duas caixas: a pergunta é verdadeira, 1.

**Versão 2.** A última linha pergunta se a distância é 4. Que número aparece?

```c
char letras[5];

printf("%d\n", &letras[4] - &letras[0] == 4);
```

Resposta certa: `1`

Se errar:

- digitou `0` → letras[0] e letras[4] ficam a quatro caixas uma da outra, sem buraco: a pergunta é verdadeira, 1.
- digitou `4` → O printf mostra a resposta da pergunta, e não a distância. A distância é 4, e a pergunta é verdadeira: 1.
- qualquer outro erro → De letras[0] a letras[4] há quatro caixas: a pergunta é verdadeira, 1.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Os elementos do array ficam grudados_

**Versão 1.** O que dá &notas[2] - &notas[0]?

Já está escrito:

```c
int notas[5];
```

Opções: `2`  `8: a conta é em bytes`  `Depende de onde cada caixa caiu`

Resposta certa: `2`

Se errar:

- respondeu `8: a conta é em bytes` → A diferença entre dois endereços do mesmo array conta caixas, e não bytes: de notas[0] a notas[2], 2.
- respondeu `Depende de onde cada caixa caiu` → As caixas de um array não caem em qualquer lugar: ficam grudadas, em fila. A distância é 2.
- qualquer outro erro → As caixas ficam grudadas: de notas[0] a notas[2] são 2.

**Versão 2.** O que dá &letras[5] - &letras[1]?

Já está escrito:

```c
char letras[6];
```

Opções: `Depende de onde cada caixa caiu`  `5: conta-se a caixa de onde se sai`  `4`

Resposta certa: `4`

Se errar:

- respondeu `Depende de onde cada caixa caiu` → As caixas de um array não caem em qualquer lugar: ficam grudadas, em fila. A distância é 4.
- respondeu `5: conta-se a caixa de onde se sai` → A distância conta os passos, e não as caixas visitadas: de letras[1] a letras[5] são 4.
- qualquer outro erro → As caixas ficam grudadas: de letras[1] a letras[5] são 4.

### Degrau 5 — prática, digitar

**Versão 1.** Que número aparece?

```c
char s[] = "sol";

printf("%zu\n", sizeof s);
```

Resposta certa: `4`

Se errar:

- digitou `3` → sol tem três letras, mas s guarda também a marca de fim: são quatro caixas de char, e sizeof s mede todas.
- digitou `1` → sizeof s mede o array inteiro, e não uma caixa: as três letras e a marca de fim, 4.
- qualquer outro erro → s são quatro caixas de char grudadas, as três letras e a marca de fim: 4.

**Versão 2.** Que número aparece?

```c
char nome[] = "rua";

printf("%zu\n", sizeof nome);
```

Resposta certa: `4`

Se errar:

- digitou `3` → rua tem três letras, mas nome guarda também a marca de fim: são quatro caixas de char, e sizeof nome mede todas.
- digitou `1` → sizeof nome mede o array inteiro, e não uma caixa: as três letras e a marca de fim, 4.
- qualquer outro erro → nome são quatro caixas de char grudadas, as três letras e a marca de fim: 4.

### Se errar a pergunta do topo: a revisão

> Os elementos de um array ficam grudados: notas[1] fica logo depois de notas[0], sem buraco.
> Por isso &notas[1] - &notas[0] é 1: uma caixa de distância.

```c
int notas[3] = {7, 8, 9};

printf("%d\n", &notas[1] - &notas[0] == 1);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> char *s = "abc" e char s[] = "abc" guardam do mesmo jeito.

```c
char s[] = "pai";
char *t = "pai";

s[0] = s[1];
t[0] = t[1];
```

**s e t recebem o mesmo texto. As duas últimas linhas trocam a primeira letra de cada um. De qual delas o compilador reclama?**

- De nenhuma: s e t guardam o texto do mesmo jeito _(é o que a crença espera)_
- Da última: as letras para onde t aponta não são de t _(é o que a máquina faz)_

O compilador reclama:

```
write to string literal
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer). O programa não é executado: mudar uma letra do texto entre aspas é o que este degrau ensina a não fazer._

O que isto mostra: O compilador reclama só da última linha ("write to string literal"). s são quatro caixas de char, cópia do texto, e são de s. t é uma caixa só, um ponteiro para letras que não são dela: o mesmo texto, guardado de outro jeito.

## I1 — a[i] é só outro jeito de escrever *(a + i): ande i caixas a partir do começo e olhe o que tem lá.

### Degrau 1 — guiado, escolher

> notas[i] é, por definição, *(notas + i): ande i caixas a partir do começo e olhe o que tem lá.
> O colchete é a soma escrita curta.

**Versão 1.** O que notas[2] quer dizer?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
```

Opções: `*(notas + 2): a caixa duas adiante do começo`  `Uma operação própria do array, e não a soma notas + 2`  `O endereço notas + 2`

Resposta certa: `*(notas + 2): a caixa duas adiante do começo`

Se errar:

- respondeu `Uma operação própria do array, e não a soma notas + 2` → O colchete não é uma operação à parte: notas[2] é, por definição, *(notas + 2). Ande duas caixas e olhe lá. _(aponta a crença `indice_nao_e_soma`)_
- respondeu `O endereço notas + 2` → notas + 2 é o endereço da caixa. notas[2] é o que está nela: *(notas + 2), com o * na frente.
- qualquer outro erro → notas[2] é *(notas + 2): ande duas caixas a partir do começo e olhe lá.

**Versão 2.** O que pontos[1] quer dizer?

Já está escrito:

```c
int pontos[3] = {3, 6, 9};
```

Opções: `O endereço pontos + 1`  `Uma operação própria do array, e não a soma pontos + 1`  `*(pontos + 1): a caixa uma adiante do começo`

Resposta certa: `*(pontos + 1): a caixa uma adiante do começo`

Se errar:

- respondeu `Uma operação própria do array, e não a soma pontos + 1` → O colchete não é uma operação à parte: pontos[1] é, por definição, *(pontos + 1). Ande uma caixa e olhe lá. _(aponta a crença `indice_nao_e_soma`)_
- respondeu `O endereço pontos + 1` → pontos + 1 é o endereço da caixa. pontos[1] é o que está nela: *(pontos + 1), com o * na frente.
- qualquer outro erro → pontos[1] é *(pontos + 1): ande uma caixa a partir do começo e olhe lá.

### Degrau 2 — guiado, completar

> Com um ponteiro vale o mesmo: p[1] é *(p + 1). A soma vem antes do *.
> E dá para andar para trás: *(p - 1) é a caixa de trás, que também se escreve p[-1].

**Versão 1.** Complete para mostrar notas[1], escrito como soma.

Já está escrito:

```c
int notas[3] = {7, 9, 4};
int *p = notas;
```

```c
printf("%d\n", ___);
```

Peças: `*(p + 1)`  `*p + 1`  `*(p + 2)`

Resposta certa: `printf("%d\n", *(p + 1));`

Se errar:

- respondeu `printf("%d\n", *p + 1);` → *p + 1 lê notas[0] e soma 1 ao valor: dá 8. Para chegar em notas[1], a soma vem antes do *: *(p + 1).
- respondeu `printf("%d\n", *(p + 2));` → *(p + 2) anda duas caixas e chega em notas[2]. notas[1] fica uma caixa adiante: *(p + 1).
- qualquer outro erro → notas[1] escrito como soma é *(p + 1): a soma antes do *.

**Versão 2.** q aponta para pontos[2]. Complete para mostrar pontos[1], a caixa de trás.

Já está escrito:

```c
int pontos[3] = {3, 5, 2};
int *q = pontos + 2;
```

```c
printf("%d\n", ___);
```

Peças: `*(q + 1)`  `*(q - 1)`  `*q - 1`

Resposta certa: `printf("%d\n", *(q - 1));`

Se errar:

- respondeu `printf("%d\n", *q - 1);` → *q - 1 lê pontos[2] e tira 1 do valor: dá 1. Para chegar na caixa de trás, a conta vem antes do *: *(q - 1).
- respondeu `printf("%d\n", *(q + 1));` → *(q + 1) anda para a frente, e depois de pontos[2] o array acabou. A caixa de trás é *(q - 1).
- qualquer outro erro → A caixa de trás de pontos[2] é *(q - 1), que também se escreve q[-1].

### Degrau 3 — guiado, digitar

> A soma vale nos dois sentidos: pontos + 1 é 1 + pontos. Por isso 1[pontos] é a mesma caixa que pontos[1].

**Versão 1.** Que número aparece?

```c
int pontos[3] = {3, 6, 9};

printf("%d\n", 1[pontos]);
```

Resposta certa: `6`

Se errar:

- digitou `3` → 1[pontos] é *(1 + pontos): a caixa uma adiante do começo, pontos[1]. Sai 6.
- digitou `1` → O 1 não é o valor: é quantas caixas andar. 1[pontos] é pontos[1]: 6.
- qualquer outro erro → 1[pontos] é *(1 + pontos), a mesma caixa que pontos[1]: 6.

**Versão 2.** Que número aparece?

```c
int dias[4] = {10, 20, 30, 40};

printf("%d\n", 3[dias]);
```

Resposta certa: `40`

Se errar:

- digitou `30` → 3[dias] é *(3 + dias): três caixas adiante do começo, dias[3]. Sai 40.
- digitou `3` → O 3 não é o valor: é quantas caixas andar. 3[dias] é dias[3]: 40.
- qualquer outro erro → 3[dias] é *(3 + dias), a mesma caixa que dias[3]: 40.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O colchete é a soma escrita curta_

**Versão 1.** p começa em notas[1]. Que número aparece?

```c
int notas[4] = {2, 4, 6, 8};
int *p = notas + 1;

printf("%d\n", p[2]);
```

Resposta certa: `8`

Se errar:

- digitou `6` → 6 está em notas[2]. p começa em notas[1], e p[2] anda duas caixas a partir dali: notas[3], que guarda 8.
- digitou `4` → 4 está em notas[1], onde p aponta. p[2] é *(p + 2), duas caixas adiante: 8.
- qualquer outro erro → p[2] é *(p + 2): duas caixas adiante de notas[1], em notas[3], que guarda 8.

**Versão 2.** q começa em pontos[2]. Que número aparece?

```c
int pontos[5] = {1, 3, 5, 7, 9};
int *q = pontos + 2;

printf("%d\n", q[1]);
```

Resposta certa: `7`

Se errar:

- digitou `3` → 3 está em pontos[1]. q começa em pontos[2], e q[1] anda uma caixa a partir dali: pontos[3], que guarda 7.
- digitou `5` → 5 está em pontos[2], onde q aponta. q[1] é *(q + 1), uma caixa adiante: 7.
- qualquer outro erro → q[1] é *(q + 1): uma caixa adiante de pontos[2], em pontos[3], que guarda 7.

### Degrau 5 — prática, escolher

**Versão 1.** Qual expressão é o mesmo que notas[3]?

Já está escrito:

```c
int notas[5] = {1, 2, 3, 4, 5};
```

Opções: `*(notas + 3)`  `*notas + 3`  `notas + 3`

Resposta certa: `*(notas + 3)`

Se errar:

- respondeu `*notas + 3` → *notas + 3 lê notas[0] e soma 3 ao valor. notas[3] é *(notas + 3): a soma vem antes do *.
- respondeu `notas + 3` → notas + 3 é o endereço da caixa, e não o que está nela. notas[3] é *(notas + 3).
- qualquer outro erro → notas[3] é *(notas + 3): ande três caixas e olhe lá.

**Versão 2.** Qual expressão é o mesmo que 2[pontos]?

Já está escrito:

```c
int pontos[4] = {6, 7, 8, 9};
```

Opções: `pontos + 2`  `*pontos + 2`  `pontos[2]`

Resposta certa: `pontos[2]`

Se errar:

- respondeu `pontos + 2` → pontos + 2 é o endereço da caixa. 2[pontos] é *(2 + pontos), o que está nela: o mesmo que pontos[2].
- respondeu `*pontos + 2` → *pontos + 2 lê pontos[0] e soma 2 ao valor. 2[pontos] é *(2 + pontos): pontos[2].
- qualquer outro erro → 2[pontos] é *(2 + pontos), a mesma caixa que pontos[2].

### Se errar a pergunta do topo: a revisão

> notas[2] é só outro jeito de escrever *(notas + 2): ande duas caixas a partir do começo e olhe lá.
> Como a soma vale nos dois sentidos, 2[notas] é a mesma caixa.

```c
int notas[3] = {4, 5, 6};

printf("%d\n", *(notas + 2));
```

A máquina imprime:

```
6
```

### Se a pessoa disser a crença: a prova

Você disse:

> a[i] é uma operação própria do array, e não a soma a + i.

```c
int notas[3] = {7, 8, 9};

printf("%d\n", 2[notas]);
```

**O trecho escreve 2[notas], com o número fora dos colchetes. O que acontece?**

- O compilador reclama: o índice é uma operação do array, e 2 não é array _(é o que a crença espera)_
- 9 _(é o que a máquina faz)_

A máquina imprime:

```
9
```

O que isto mostra: Saiu 9. notas[2] é *(notas + 2), e a soma vale nos dois sentidos: 2[notas] é *(2 + notas), a mesma caixa. O índice não é uma operação própria do array: é a soma escrita curta.

## I2 — Um void * não sabe o tamanho do destino. Sem isso não há quanto andar, e a conta simplesmente não existe.

### Degrau 1 — guiado, escolher

> Para andar, o ponteiro precisa saber o tamanho da caixa do destino. O void * não sabe: não tem tipo nenhum.
> Por isso o padrão do C não define v + 1: não há quanto andar.

**Versão 1.** v é um void *. O que o padrão do C diz de v + 1?

Já está escrito:

```c
void *v;
```

Opções: `Não define: sem tipo, não há quanto andar`  `Anda uma caixa: dá para fazer aritmética em void * como em qualquer ponteiro`  `Anda o tamanho de um int`

Resposta certa: `Não define: sem tipo, não há quanto andar`

Se errar:

- respondeu `Anda uma caixa: dá para fazer aritmética em void * como em qualquer ponteiro` → O padrão do C não define v + 1: o void * não sabe o tamanho do destino, e sem tamanho não há quanto andar. O gcc aceita por conta própria, andando 1 byte, mas isso é dele. _(aponta a crença `voidptr_arith_ok`)_
- respondeu `Anda o tamanho de um int` → O void * não sabe que há um int lá: não tem tipo nenhum. Sem tipo, não há quanto andar.
- qualquer outro erro → Sem tipo, não há quanto andar: o padrão do C não define v + 1.

**Versão 2.** w é um void *. O que o padrão do C diz de w + 2?

Já está escrito:

```c
void *w;
```

Opções: `Anda o tamanho de dois ints`  `Não define: sem tipo, não há quanto andar`  `Anda duas caixas: dá para fazer aritmética em void * como em qualquer ponteiro`

Resposta certa: `Não define: sem tipo, não há quanto andar`

Se errar:

- respondeu `Anda duas caixas: dá para fazer aritmética em void * como em qualquer ponteiro` → O padrão do C não define w + 2: o void * não sabe o tamanho do destino, e sem tamanho não há quanto andar. O gcc aceita por conta própria, andando 2 bytes, mas isso é dele. _(aponta a crença `voidptr_arith_ok`)_
- respondeu `Anda o tamanho de dois ints` → O void * não sabe que há um int lá: não tem tipo nenhum. Sem tipo, não há quanto andar.
- qualquer outro erro → Sem tipo, não há quanto andar: o padrão do C não define w + 2.

### Degrau 2 — guiado, completar

> Para andar a partir de um void *, dê um tipo antes: (char *)v é o mesmo endereço, visto como char *.

**Versão 1.** Complete para c ficar uma caixa de char adiante do começo de letras.

Já está escrito:

```c
char letras[4] = "sol";
void *v = letras;
```

```c
char *c = ___ + 1;
```

Peças: `(char *)v`  `v`  `*v`

Resposta certa: `char *c = (char *)v + 1;`

Se errar:

- respondeu `char *c = v + 1;` → v + 1 é conta em void *, que o padrão não define; o gcc aceita por extensão própria. Dê o tipo antes: (char *)v + 1.
- respondeu `char *c = *v + 1;` → *v tentaria ler o destino, e um void * não diz o que há lá: o compilador reclama. O que serve é (char *)v + 1.
- qualquer outro erro → Com o tipo dado antes, a conta existe: char *c = (char *)v + 1;

**Versão 2.** Complete para c ficar duas caixas de char adiante do começo de nome.

Já está escrito:

```c
char nome[4] = "ana";
void *w = nome;
```

```c
char *c = ___ + 2;
```

Peças: `*w`  `(char *)w`  `w`

Resposta certa: `char *c = (char *)w + 2;`

Se errar:

- respondeu `char *c = w + 2;` → w + 2 é conta em void *, que o padrão não define; o gcc aceita por extensão própria. Dê o tipo antes: (char *)w + 2.
- respondeu `char *c = *w + 2;` → *w tentaria ler o destino, e um void * não diz o que há lá: o compilador reclama. O que serve é (char *)w + 2.
- qualquer outro erro → Com o tipo dado antes, a conta existe: char *c = (char *)w + 2;

### Degrau 3 — guiado, digitar

> Convertido, o ponteiro anda pelo tipo novo: (char *)v + 2 fica duas caixas de char adiante.

**Versão 1.** A última linha pergunta se c chegou em letras[2]. Que número aparece?

```c
char letras[4] = "sol";
void *v = letras;
char *c = (char *)v + 2;

printf("%d\n", c == &letras[2]);
```

Resposta certa: `1`

Se errar:

- digitou `0` → (char *)v + 2 anda duas caixas de char a partir de letras[0] e chega em letras[2]: a pergunta é verdadeira, 1.
- digitou `2` → O printf mostra a resposta da pergunta c == &letras[2], e não a distância. A pergunta é verdadeira: 1.
- qualquer outro erro → (char *)v + 2 chega em letras[2]: a pergunta é verdadeira, 1.

**Versão 2.** A última linha pergunta se c chegou em nome[3]. Que número aparece?

```c
char nome[5] = "mesa";
void *w = nome;
char *c = (char *)w + 3;

printf("%d\n", c == &nome[3]);
```

Resposta certa: `1`

Se errar:

- digitou `0` → (char *)w + 3 anda três caixas de char a partir de nome[0] e chega em nome[3]: a pergunta é verdadeira, 1.
- digitou `3` → O printf mostra a resposta da pergunta c == &nome[3], e não a distância. A pergunta é verdadeira: 1.
- qualquer outro erro → (char *)w + 3 chega em nome[3]: a pergunta é verdadeira, 1.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: void * não anda: falta o tipo_

**Versão 1.** Qual destas somas o padrão do C define?

Já está escrito:

```c
char letras[4] = "sol";
void *v = letras;
```

Opções: `(char *)v + 1`  `v + 1`  `v + 1 * sizeof(char)`

Resposta certa: `(char *)v + 1`

Se errar:

- respondeu `v + 1` → v + 1 é conta em void *, e o padrão não a define: falta o tamanho do destino. Dê o tipo antes: (char *)v + 1.
- respondeu `v + 1 * sizeof(char)` → Multiplicar não dá tipo ao v: continua sendo conta em void *. O que o padrão define é (char *)v + 1.
- qualquer outro erro → Só a conta com o tipo dado antes existe: (char *)v + 1.

**Versão 2.** Qual destas somas o padrão do C define?

Já está escrito:

```c
char nome[4] = "ana";
void *w = nome;
```

Opções: `w + 2`  `w + 2 * sizeof(char)`  `(char *)w + 2`

Resposta certa: `(char *)w + 2`

Se errar:

- respondeu `w + 2` → w + 2 é conta em void *, e o padrão não a define: falta o tamanho do destino. Dê o tipo antes: (char *)w + 2.
- respondeu `w + 2 * sizeof(char)` → Multiplicar não dá tipo ao w: continua sendo conta em void *. O que o padrão define é (char *)w + 2.
- qualquer outro erro → Só a conta com o tipo dado antes existe: (char *)w + 2.

### Degrau 5 — prática, digitar

**Versão 1.** Que número aparece?

```c
int notas[3] = {7, 8, 9};
void *v = notas;
int *p = (int *)v + 2;

printf("%d\n", *p);
```

Resposta certa: `9`

Se errar:

- digitou `8` → 8 está em notas[1]. (int *)v + 2 anda duas caixas de int a partir de notas[0]: notas[2], que guarda 9.
- digitou `7` → 7 está em notas[0], onde v aponta. Com o tipo int dado, + 2 anda duas caixas: 9.
- qualquer outro erro → (int *)v + 2 anda duas caixas de int: notas[2], que guarda 9.

**Versão 2.** Que número aparece?

```c
int pontos[4] = {1, 3, 5, 7};
void *v = pontos;
int *q = (int *)v + 1;

printf("%d\n", *q);
```

Resposta certa: `3`

Se errar:

- digitou `1` → 1 está em pontos[0], onde v aponta. Com o tipo int dado, + 1 anda uma caixa: pontos[1], que guarda 3.
- digitou `5` → 5 está duas caixas adiante, em pontos[2]. (int *)v + 1 anda uma caixa só: 3.
- qualquer outro erro → (int *)v + 1 anda uma caixa de int: pontos[1], que guarda 3.

### Se errar a pergunta do topo: a revisão

> Um void * não sabe o tamanho do destino, e sem tamanho não há quanto andar: o padrão do C não define v + 1.
> Para andar, dê um tipo antes: (char *)v + 1 anda uma caixa de char.

```c
char nome[4] = "ana";
void *v = nome;
char *c = (char *)v + 1;

printf("%d\n", c == &nome[1]);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> Dá para fazer aritmética em void * como em qualquer ponteiro.

```c
char letras[4] = "sol";
char *c = letras;
void *v = letras;

c = c + 1;
v = v + 1;
```

**c é um char *, e v é um void *, os dois no começo de letras. As duas últimas linhas somam 1 a cada um. De qual delas o compilador reclama?**

- Da última: void * não tem tipo, e sem tipo não há quanto andar _(é o que a máquina faz)_
- De nenhuma: void * anda de um em um, como qualquer ponteiro _(é o que a crença espera)_

O compilador reclama:

```
pointer of type 'void *' used in arithmetic
```

_Mensagem do gcc 16.2 com o aviso de aritmética de ponteiro ligado (-Wpointer-arith). Sem esse aviso, o gcc aceita v + 1 por uma extensão própria, andando 1 byte; o padrão do C não define essa conta._

O que isto mostra: O compilador aceita c + 1 e reclama de v + 1. O void * não sabe o tamanho do destino, e sem tamanho não há quanto andar. Quem quer andar byte a byte dá o tipo antes: (char *)v + 1.

## I3 — Como o compilador sabe o tamanho da caixa, ele mesmo faz a conta. Você escreve p + 1; ele anda uma caixa inteira. Se você multiplicar por sizeof também, o ponteiro pula longe demais.

### Degrau 1 — guiado, escolher

> p + 1 anda um elemento do tipo de p, e não um byte: com int *p, uma caixa de int inteira.
> Quem faz a conta do tamanho é o compilador.

**Versão 1.** p aponta para notas[0]. Para onde aponta p + 1?

Já está escrito:

```c
int notas[3];
int *p = notas;
```

Opções: `Para notas[1], a caixa seguinte`  `Para o byte seguinte: a aritmética de ponteiro conta bytes, e é preciso multiplicar por sizeof na mão`  `Para notas[0] de novo`

Resposta certa: `Para notas[1], a caixa seguinte`

Se errar:

- respondeu `Para o byte seguinte: a aritmética de ponteiro conta bytes, e é preciso multiplicar por sizeof na mão` → A soma não conta bytes: p + 1 anda um int inteiro, e o compilador faz a conta do tamanho sozinho. Chega em notas[1]. _(aponta a crença `ptr_arith_is_bytes`)_
- respondeu `Para notas[0] de novo` → p + 1 não fica onde p está: anda uma caixa. Chega em notas[1].
- qualquer outro erro → p + 1 anda uma caixa de int inteira: notas[1].

**Versão 2.** q aponta para pontos[1]. Para onde aponta q + 2?

Já está escrito:

```c
int pontos[4];
int *q = pontos + 1;
```

Opções: `Para pontos[1] de novo`  `Para dois bytes adiante: a aritmética de ponteiro conta bytes, e é preciso multiplicar por sizeof na mão`  `Para pontos[3], duas caixas adiante`

Resposta certa: `Para pontos[3], duas caixas adiante`

Se errar:

- respondeu `Para dois bytes adiante: a aritmética de ponteiro conta bytes, e é preciso multiplicar por sizeof na mão` → A soma não conta bytes: q + 2 anda dois ints inteiros, e o compilador faz a conta do tamanho sozinho. Chega em pontos[3]. _(aponta a crença `ptr_arith_is_bytes`)_
- respondeu `Para pontos[1] de novo` → q + 2 não fica onde q está: anda duas caixas. Chega em pontos[3].
- qualquer outro erro → q + 2 anda duas caixas de int a partir de pontos[1]: pontos[3].

### Degrau 2 — guiado, completar

> Multiplicar por sizeof na mão escala duas vezes: p + 3 * sizeof(int) não é notas[3], é muito mais longe.

**Versão 1.** Complete para q apontar para notas[3].

Já está escrito:

```c
int notas[8];
int *p = notas;
```

```c
int *q = p + ___;
```

Peças: `3`  `3 * sizeof(int)`  `sizeof(int)`

Resposta certa: `int *q = p + 3;`

Se errar:

- respondeu `int *q = p + 3 * sizeof(int);` → O compilador já multiplica pelo tamanho do int. Multiplicar de novo escala duas vezes, e q passa longe de notas[3]. O certo é p + 3. _(aponta a crença `ptr_arith_is_bytes`)_
- respondeu `int *q = p + sizeof(int);` → p + sizeof(int) anda tantas caixas quanto o tamanho de um int, e não três. Para notas[3], p + 3.
- qualquer outro erro → A escala já está feita: q = p + 3 chega em notas[3].

**Versão 2.** Complete para q apontar para pontos[2].

Já está escrito:

```c
int pontos[8];
int *p = pontos;
```

```c
int *q = p + ___;
```

Peças: `sizeof(int)`  `2`  `2 * sizeof(int)`

Resposta certa: `int *q = p + 2;`

Se errar:

- respondeu `int *q = p + 2 * sizeof(int);` → O compilador já multiplica pelo tamanho do int. Multiplicar de novo escala duas vezes, e q passa longe de pontos[2]. O certo é p + 2. _(aponta a crença `ptr_arith_is_bytes`)_
- respondeu `int *q = p + sizeof(int);` → p + sizeof(int) anda tantas caixas quanto o tamanho de um int, e não duas. Para pontos[2], p + 2.
- qualquer outro erro → A escala já está feita: q = p + 2 chega em pontos[2].

### Degrau 3 — guiado, digitar

> Com a escala feita pelo compilador, a soma conta caixas: de notas[1], p + 2 chega em notas[3].

**Versão 1.** p começa em notas[1]. Que número aparece?

```c
int notas[4] = {2, 4, 6, 8};
int *p = notas + 1;

printf("%d\n", *(p + 2));
```

Resposta certa: `8`

Se errar:

- digitou `6` → 6 está em notas[2]. p começa em notas[1], e p + 2 anda duas caixas a partir dali: notas[3], que guarda 8.
- digitou `4` → 4 está em notas[1], onde p aponta. p + 2 anda duas caixas: 8.
- qualquer outro erro → p + 2 anda duas caixas a partir de notas[1]: notas[3], que guarda 8.

**Versão 2.** q começa em pontos[2]. Que número aparece?

```c
int pontos[5] = {1, 2, 3, 4, 5};
int *q = pontos + 2;

printf("%d\n", *(q + 2));
```

Resposta certa: `5`

Se errar:

- digitou `3` → 3 está em pontos[2], onde q aponta. q + 2 anda duas caixas: pontos[4], que guarda 5.
- digitou `4` → 4 está em pontos[3], uma caixa adiante. q + 2 anda duas: 5.
- qualquer outro erro → q + 2 anda duas caixas a partir de pontos[2]: pontos[4], que guarda 5.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: O compilador escala a soma sozinho_

**Versão 1.** Quem multiplica pelo tamanho do int em p + 2?

Já está escrito:

```c
int *p;
```

Opções: `O compilador`  `Você, escrevendo p + 2 * sizeof(int)`  `Ninguém: p + 2 anda dois bytes`

Resposta certa: `O compilador`

Se errar:

- respondeu `Você, escrevendo p + 2 * sizeof(int)` → Escrever 2 * sizeof(int) escala duas vezes: o compilador já multiplica pelo tamanho do int. Basta p + 2.
- respondeu `Ninguém: p + 2 anda dois bytes` → p + 2 não anda bytes: anda dois ints inteiros. Quem multiplica pelo tamanho é o compilador.
- qualquer outro erro → O compilador multiplica sozinho: p + 2 anda dois ints.

**Versão 2.** Quem multiplica pelo tamanho do int em q + 5?

Já está escrito:

```c
int *q;
```

Opções: `Ninguém: q + 5 anda cinco bytes`  `O compilador`  `Você, escrevendo q + 5 * sizeof(int)`

Resposta certa: `O compilador`

Se errar:

- respondeu `Você, escrevendo q + 5 * sizeof(int)` → Escrever 5 * sizeof(int) escala duas vezes: o compilador já multiplica pelo tamanho do int. Basta q + 5.
- respondeu `Ninguém: q + 5 anda cinco bytes` → q + 5 não anda bytes: anda cinco ints inteiros. Quem multiplica pelo tamanho é o compilador.
- qualquer outro erro → O compilador multiplica sozinho: q + 5 anda cinco ints.

### Degrau 5 — prática, digitar

**Versão 1.** Que número aparece?

```c
int pontos[5] = {1, 3, 5, 7, 9};
int *q = pontos;

printf("%d\n", *(q + 4));
```

Resposta certa: `9`

Se errar:

- digitou `7` → 7 está em pontos[3]. q + 4 anda quatro caixas de int a partir de pontos[0]: pontos[4], que guarda 9.
- digitou `1` → 1 está em pontos[0], onde q aponta. q + 4 anda quatro caixas inteiras: 9.
- qualquer outro erro → q + 4 anda quatro caixas de int: pontos[4], que guarda 9.

**Versão 2.** Que número aparece?

```c
int dias[3] = {28, 30, 31};
int *p = dias + 1;

printf("%d\n", *(p + 1));
```

Resposta certa: `31`

Se errar:

- digitou `30` → 30 está em dias[1], onde p aponta. p + 1 anda uma caixa de int: dias[2], que guarda 31.
- digitou `28` → 28 está em dias[0], antes de p. p + 1 anda para a frente, uma caixa: 31.
- qualquer outro erro → p + 1 anda uma caixa a partir de dias[1]: dias[2], que guarda 31.

### Se errar a pergunta do topo: a revisão

> O compilador sabe o tamanho da caixa e faz a conta sozinho: p + 1 anda uma caixa de int inteira.
> Multiplicar por sizeof na mão escala duas vezes, e o ponteiro pula longe demais.

```c
int pontos[3] = {10, 20, 30};
int *p = pontos;

printf("%d\n", *(p + 1));
```

A máquina imprime:

```
20
```

### Se a pessoa disser a crença: a prova

Você disse:

> A aritmética de ponteiro conta bytes; é preciso multiplicar por sizeof na mão.

```c
int notas[4] = {5, 15, 25, 35};
int *p = notas;

printf("%d\n", *(p + 3));
```

**p aponta para notas[0]. O trecho soma 3 a p, sem multiplicar por sizeof. O que aparece?**

- 35 _(é o que a máquina faz)_
- Lixo: p + 3 anda três bytes, e faltou multiplicar por sizeof _(é o que a crença espera)_

A máquina imprime:

```
35
```

O que isto mostra: Saiu 35, que está em notas[3]. p + 3 andou três caixas de int inteiras: o compilador sabe o tamanho do int e faz a conta sozinho. Multiplicar por sizeof na mão andaria longe demais.
