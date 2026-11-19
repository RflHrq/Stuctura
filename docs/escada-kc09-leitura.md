# A escada do kc_09 — free() e ponteiro pendente

Texto para leitura, gerado de `mvp/dominio/escada_kc09.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — free recebe o endereço do pedaço que você quer devolver. O tamanho quem guardou foi o alocador, quando entregou.

### Degrau 1 — guiado, escolher

> Quem anota o tamanho do bloco é o alocador, na hora de entregá-lo.
> Por isso free(p) funciona recebendo só o endereço.

**Versão 1.** Depois da última linha, o que está guardado em p?

Já está escrito:

```c
int *p;

p = malloc(10 * sizeof(int));
```

Opções: `Só o endereço do bloco`  `O endereço e o tamanho: o ponteiro carrega o tamanho do bloco`  `Os dez ints`

Resposta certa: `Só o endereço do bloco`

Se errar:

- respondeu `O endereço e o tamanho: o ponteiro carrega o tamanho do bloco` → Em p cabe um endereço, e mais nada. Quantos bytes o bloco tem ficou anotado com o alocador, que foi quem entregou. _(aponta a crença `pointer_knows_block_size`)_
- respondeu `Os dez ints` → Os dez ints ficam no bloco, no monte. Em p fica só o endereço dele.
- qualquer outro erro → p guarda só o endereço do bloco. O tamanho ficou com o alocador.

**Versão 2.** Depois da última linha, o que está guardado em q?

Já está escrito:

```c
int *q;

q = malloc(6 * sizeof(int));
```

Opções: `Os seis ints`  `Só o endereço do bloco`  `O endereço e o tamanho: o ponteiro carrega o tamanho do bloco`

Resposta certa: `Só o endereço do bloco`

Se errar:

- respondeu `O endereço e o tamanho: o ponteiro carrega o tamanho do bloco` → Em q cabe um endereço, e mais nada. Quantos bytes o bloco tem ficou anotado com o alocador, que foi quem entregou. _(aponta a crença `pointer_knows_block_size`)_
- respondeu `Os seis ints` → Os seis ints ficam no bloco, no monte. Em q fica só o endereço dele.
- qualquer outro erro → q guarda só o endereço do bloco. O tamanho ficou com o alocador.

### Degrau 2 — guiado, escolher

> sizeof de um array mede o conjunto inteiro das caixas.
> sizeof de um ponteiro mede só a caixa do ponteiro: quantas caixas há no bloco, ele não sabe.

**Versão 1.** v é um array de dez; p aponta para um bloco de dez. Qual dos dois sizeof dá 10?

Já está escrito:

```c
char v[10];
char *p;

p = malloc(10);
```

Opções: `Só sizeof v: v é o conjunto; p é um endereço`  `Os dois: p também sabe o tamanho do bloco`  `Só sizeof p: é ele que aponta para o bloco`

Resposta certa: `Só sizeof v: v é o conjunto; p é um endereço`

Se errar:

- respondeu `Os dois: p também sabe o tamanho do bloco` → p guarda um endereço, e sizeof p mede o ponteiro, e não o bloco. Só v, que é o conjunto das dez caixas, dá 10.
- respondeu `Só sizeof p: é ele que aponta para o bloco` → Apontar para o bloco não é saber o tamanho dele: sizeof p mede o ponteiro. Quem dá 10 é sizeof v.
- qualquer outro erro → sizeof v dá 10, as dez caixas. sizeof p mede só o ponteiro.

**Versão 2.** letras é um array de seis; q aponta para um bloco de seis. Qual dos dois sizeof dá 6?

Já está escrito:

```c
char *q;
char letras[6];

q = malloc(6);
```

Opções: `Os dois: q também sabe o tamanho do bloco`  `Só sizeof q: é ele que aponta para o bloco`  `Só sizeof letras: letras é o conjunto; q é um endereço`

Resposta certa: `Só sizeof letras: letras é o conjunto; q é um endereço`

Se errar:

- respondeu `Os dois: q também sabe o tamanho do bloco` → q guarda um endereço, e sizeof q mede o ponteiro, e não o bloco. Só letras, que é o conjunto das seis caixas, dá 6.
- respondeu `Só sizeof q: é ele que aponta para o bloco` → Apontar para o bloco não é saber o tamanho dele: sizeof q mede o ponteiro. Quem dá 6 é sizeof letras.
- qualquer outro erro → sizeof letras dá 6, as seis caixas. sizeof q mede só o ponteiro.

### Degrau 3 — guiado, completar

> Por isso free recebe uma coisa só, o endereço. O tamanho não se diz: o alocador já tem.

**Versão 1.** Complete a chamada que devolve o bloco de dez ints.

Já está escrito:

```c
int *p;

p = malloc(10 * sizeof(int));
```

```c
free(___);
```

Peças: `p`  `p, 10`  `10`

Resposta certa: `free(p);`

Se errar:

- respondeu `free(p, 10);` → free recebe uma coisa só, o endereço: com dois valores o compilador reclama. O tamanho o alocador já anotou: free(p);
- respondeu `free(10);` → 10 é quantos ints foram pedidos, e não um endereço: o compilador reclama. free recebe o endereço do bloco: free(p);
- qualquer outro erro → free recebe só o endereço do bloco: free(p);

**Versão 2.** Complete a chamada que devolve o bloco de seis ints.

Já está escrito:

```c
int *q;

q = malloc(6 * sizeof(int));
```

```c
free(___);
```

Peças: `6`  `q`  `q, 6`

Resposta certa: `free(q);`

Se errar:

- respondeu `free(q, 6);` → free recebe uma coisa só, o endereço: com dois valores o compilador reclama. O tamanho o alocador já anotou: free(q);
- respondeu `free(6);` → 6 é quantos ints foram pedidos, e não um endereço: o compilador reclama. free recebe o endereço do bloco: free(q);
- qualquer outro erro → free recebe só o endereço do bloco: free(q);

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: O ponteiro guarda o endereço, não o tamanho_

**Versão 1.** A função recebe p. Ela consegue descobrir quantos ints o bloco tem?

Já está escrito:

```c
void usa(int *p) { p[0] = 7; }
```

Opções: `Não: p é só um endereço, e o número tem de vir em outro parâmetro`  `Consegue: o ponteiro carrega o tamanho do bloco`  `Consegue, com sizeof p`

Resposta certa: `Não: p é só um endereço, e o número tem de vir em outro parâmetro`

Se errar:

- respondeu `Consegue: o ponteiro carrega o tamanho do bloco` → Em p cabe um endereço, e mais nada. O tamanho ficou com o alocador, e a função não tem como perguntar a ele.
- respondeu `Consegue, com sizeof p` → sizeof p mede o ponteiro, e não o bloco. Quantos ints há, só quem pediu sabe: o número vai em outro parâmetro.
- qualquer outro erro → p é só um endereço. Quantos ints o bloco tem, a função recebe em outro parâmetro.

**Versão 2.** A função recebe q. Ela consegue descobrir quantos ints o bloco tem?

Já está escrito:

```c
void zera(int *q) { q[0] = 0; }
```

Opções: `Consegue, com sizeof q`  `Não: q é só um endereço, e o número tem de vir em outro parâmetro`  `Consegue: o ponteiro carrega o tamanho do bloco`

Resposta certa: `Não: q é só um endereço, e o número tem de vir em outro parâmetro`

Se errar:

- respondeu `Consegue: o ponteiro carrega o tamanho do bloco` → Em q cabe um endereço, e mais nada. O tamanho ficou com o alocador, e a função não tem como perguntar a ele.
- respondeu `Consegue, com sizeof q` → sizeof q mede o ponteiro, e não o bloco. Quantos ints há, só quem pediu sabe: o número vai em outro parâmetro.
- qualquer outro erro → q é só um endereço. Quantos ints o bloco tem, a função recebe em outro parâmetro.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas devolve o bloco de p?

Já está escrito:

```c
int *p;

p = malloc(5 * sizeof(int));
```

Opções: `free(p);`  `free(p, 5);`  `free(5 * sizeof(int));`

Resposta certa: `free(p);`

Se errar:

- respondeu `free(p, 5);` → free recebe uma coisa só: com dois valores o compilador reclama. O tamanho não se diz, porque o alocador anotou: free(p);
- respondeu `free(5 * sizeof(int));` → Essa conta é um tamanho, e free recebe um endereço: o compilador reclama. O endereço do bloco está em p: free(p);
- qualquer outro erro → free recebe o endereço do bloco, e só: free(p);

**Versão 2.** Qual destas linhas devolve o bloco de q?

Já está escrito:

```c
int *q;

q = malloc(8 * sizeof(int));
```

Opções: `free(8 * sizeof(int));`  `free(q, 8);`  `free(q);`

Resposta certa: `free(q);`

Se errar:

- respondeu `free(q, 8);` → free recebe uma coisa só: com dois valores o compilador reclama. O tamanho não se diz, porque o alocador anotou: free(q);
- respondeu `free(8 * sizeof(int));` → Essa conta é um tamanho, e free recebe um endereço: o compilador reclama. O endereço do bloco está em q: free(q);
- qualquer outro erro → free recebe o endereço do bloco, e só: free(q);

### Se errar a pergunta do topo: a revisão

> free(p) recebe só o endereço do bloco. O tamanho, quem anotou foi o alocador, quando entregou.
> O ponteiro não carrega tamanho: guarda um endereço, e mais nada.

```c
int *p;

p = malloc(3 * sizeof(int));
p[2] = 9;
printf("%d\n", p[2]);
free(p);
```

A máquina imprime:

```
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro carrega o tamanho do bloco que ele aponta.

```c
int *p;

p = malloc(10 * sizeof(int));
printf("%zu\n", sizeof p / sizeof p[0]);
free(p);
```

**Com um array, a conta sizeof v / sizeof v[0] dá o número de itens. Aqui ela é feita com p, um ponteiro para um bloco de dez ints. O compilador reclama de alguma coisa?**

- Não: o ponteiro carrega o tamanho do bloco, e a conta dá 10 _(é o que a crença espera)_
- Sim: avisa que essa conta não dá o número de itens _(é o que a máquina faz)_

O compilador reclama:

```
does not compute the number of array elements
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall): a divisão "não calcula o número de elementos". O programa não é executado._

O que isto mostra: O compilador avisa que a conta não dá o número de itens: sizeof p mede o ponteiro, e não o bloco. p guarda só um endereço. O tamanho do bloco ficou anotado com o alocador, e é por isso que free(p) não precisa que você diga.

## B2 — Ao chamar free(p), o que entra na função é uma cópia de p — como em qualquer chamada de C.

### Degrau 1 — guiado, escolher

> free é uma função como as outras: na chamada, o que entra nela é uma cópia do valor do argumento.
> O valor de p é um endereço. A variável p fica com quem chamou.

**Versão 1.** Na última linha, o que entra na função free?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

Opções: `Uma cópia do endereço que está em p`  `A própria variável p: a função recebe a original, e não uma cópia`  `O bloco inteiro`

Resposta certa: `Uma cópia do endereço que está em p`

Se errar:

- respondeu `A própria variável p: a função recebe a original, e não uma cópia` → Em C toda chamada copia, e free não é exceção. O que entra nela é uma cópia do endereço guardado em p; a variável p fica com quem chamou. _(aponta a crença `function_gets_original`)_
- respondeu `O bloco inteiro` → O bloco fica no monte, onde estava. O que viaja na chamada é um endereço: uma cópia do que está em p.
- qualquer outro erro → Em free(p) entra uma cópia do endereço que está em p.

**Versão 2.** Na última linha, o que entra na função free?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

Opções: `O bloco inteiro`  `Uma cópia do endereço que está em q`  `A própria variável q: a função recebe a original, e não uma cópia`

Resposta certa: `Uma cópia do endereço que está em q`

Se errar:

- respondeu `A própria variável q: a função recebe a original, e não uma cópia` → Em C toda chamada copia, e free não é exceção. O que entra nela é uma cópia do endereço guardado em q; a variável q fica com quem chamou. _(aponta a crença `function_gets_original`)_
- respondeu `O bloco inteiro` → O bloco fica no monte, onde estava. O que viaja na chamada é um endereço: uma cópia do que está em q.
- qualquer outro erro → Em free(q) entra uma cópia do endereço que está em q.

### Degrau 2 — guiado, digitar

> A cópia do endereço leva ao mesmo bloco: é por ela que a função chega lá.
> Mas apagar a cópia, x = NULL;, não mexe no p de quem chamou.

**Versão 1.** A função escreve 9 no bloco e depois apaga o parâmetro dela. Que número aparece?

```c
void marca(int *x) { *x = 9; x = NULL; }

int *p;

p = malloc(sizeof(int));
*p = 7;
marca(p);
printf("%d\n", *p);
free(p);
```

Resposta certa: `9`

Se errar:

- digitou `7` → A função recebeu uma cópia do endereço, e por ela chegou ao bloco: o 9 foi escrito lá.
- digitou `0` → x = NULL; apagou só a cópia. O p de quem chamou continua com o endereço do bloco, que agora guarda 9.
- qualquer outro erro → O 9 chegou ao bloco pela cópia do endereço. Apagar a cópia não mexeu em p.

**Versão 2.** A função escreve 20 no bloco e depois apaga o parâmetro dela. Que número aparece?

```c
void marca(int *x) { *x = 20; x = NULL; }

int *q;

q = malloc(sizeof(int));
*q = 15;
marca(q);
printf("%d\n", *q);
free(q);
```

Resposta certa: `20`

Se errar:

- digitou `15` → A função recebeu uma cópia do endereço, e por ela chegou ao bloco: o 20 foi escrito lá.
- digitou `0` → x = NULL; apagou só a cópia. O q de quem chamou continua com o endereço do bloco, que agora guarda 20.
- qualquer outro erro → O 20 chegou ao bloco pela cópia do endereço. Apagar a cópia não mexeu em q.

### Degrau 3 — guiado, escolher

> free recebe uma cópia do endereço guardado em p, como toda função recebe cópias.
> Com a cópia do endereço ela chega ao bloco; o p de quem chamou é outra caixa.

**Versão 1.** O que free consegue fazer com a cópia que recebeu?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

Opções: `Achar o bloco e devolvê-lo`  `Mudar o que está guardado em p`  `Apagar a variável p`

Resposta certa: `Achar o bloco e devolvê-lo`

Se errar:

- respondeu `Mudar o que está guardado em p` → free recebeu uma cópia do endereço, e não a variável p. Com a cópia ela acha o bloco; em p, ela não escreve.
- respondeu `Apagar a variável p` → A variável p é de quem chamou, e free nem sabe onde ela fica: recebeu só uma cópia do endereço. Com ela, acha o bloco e o devolve.
- qualquer outro erro → Com a cópia do endereço, free acha o bloco e o devolve. Em p ela não toca.

**Versão 2.** O que free consegue fazer com a cópia que recebeu?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

Opções: `Apagar a variável q`  `Mudar o que está guardado em q`  `Achar o bloco e devolvê-lo`

Resposta certa: `Achar o bloco e devolvê-lo`

Se errar:

- respondeu `Mudar o que está guardado em q` → free recebeu uma cópia do endereço, e não a variável q. Com a cópia ela acha o bloco; em q, ela não escreve.
- respondeu `Apagar a variável q` → A variável q é de quem chamou, e free nem sabe onde ela fica: recebeu só uma cópia do endereço. Com ela, acha o bloco e o devolve.
- qualquer outro erro → Com a cópia do endereço, free acha o bloco e o devolve. Em q ela não toca.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A função recebe uma cópia do ponteiro_

**Versão 1.** A função apaga o parâmetro dela. Depois, o trecho lê o bloco por p. Que número aparece?

```c
void larga(int *x) { x = NULL; }

int *p;

p = malloc(sizeof(int));
*p = 7;
larga(p);
printf("%d\n", *p);
free(p);
```

Resposta certa: `7`

Se errar:

- digitou `0` → x é uma cópia do endereço. Apagar x não apaga p: p continua apontando para o bloco, que guarda 7.
- qualquer outro erro → A função apagou a cópia. p continua com o endereço, e o bloco com 7.

**Versão 2.** A função apaga o parâmetro dela. Depois, o trecho lê o bloco por q. Que número aparece?

```c
void larga(int *x) { x = NULL; }

int *q;

q = malloc(sizeof(int));
*q = 15;
larga(q);
printf("%d\n", *q);
free(q);
```

Resposta certa: `15`

Se errar:

- digitou `0` → x é uma cópia do endereço. Apagar x não apaga q: q continua apontando para o bloco, que guarda 15.
- qualquer outro erro → A função apagou a cópia. q continua com o endereço, e o bloco com 15.

### Degrau 5 — prática, escolher

**Versão 1.** Qual das duas funções consegue mudar o que está no bloco de quem chamou?

Já está escrito:

```c
void a(int *x) { *x = 0; }
void b(int *x) { x = NULL; }
```

Opções: `A a: pela cópia do endereço ela chega ao bloco`  `A b: ela apaga o ponteiro de quem chamou`  `Nenhuma: as duas só têm uma cópia`

Resposta certa: `A a: pela cópia do endereço ela chega ao bloco`

Se errar:

- respondeu `A b: ela apaga o ponteiro de quem chamou` → A b escreve NULL em x, a cópia dela, e mais nada: nem o bloco nem o ponteiro de quem chamou mudam. Quem chega ao bloco é a a, com *x.
- respondeu `Nenhuma: as duas só têm uma cópia` → A cópia é de um endereço, e endereço copiado leva ao mesmo bloco. Com *x = 0; a função a escreve lá.
- qualquer outro erro → Com *x a função chega ao bloco, pela cópia do endereço. x = NULL; só apaga a cópia.

**Versão 2.** Qual das duas funções consegue mudar o que está no bloco de quem chamou?

Já está escrito:

```c
void a(int *x) { x = NULL; }
void b(int *x) { *x = 9; }
```

Opções: `Nenhuma: as duas só têm uma cópia`  `A a: ela apaga o ponteiro de quem chamou`  `A b: pela cópia do endereço ela chega ao bloco`

Resposta certa: `A b: pela cópia do endereço ela chega ao bloco`

Se errar:

- respondeu `A a: ela apaga o ponteiro de quem chamou` → A a escreve NULL em x, a cópia dela, e mais nada: nem o bloco nem o ponteiro de quem chamou mudam. Quem chega ao bloco é a b, com *x.
- respondeu `Nenhuma: as duas só têm uma cópia` → A cópia é de um endereço, e endereço copiado leva ao mesmo bloco. Com *x = 9; a função b escreve lá.
- qualquer outro erro → Com *x a função chega ao bloco, pela cópia do endereço. x = NULL; só apaga a cópia.

### Se errar a pergunta do topo: a revisão

> free é uma função como as outras: em free(p) o que entra é uma cópia do valor de p.
> A variável p fica com quem chamou. A função não tem como escrever nela.

```c
void esvazia(int *x) { x = NULL; }

int *p;

p = malloc(sizeof(int));
*p = 7;
esvazia(p);
printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> A função recebe a variável original, não uma cópia.

```c
void esvazia(int *x) { x = NULL; }

int *p;

p = malloc(sizeof(int));
esvazia(p);
printf("%d\n", p == NULL);
free(p);
```

**A função escreve NULL no parâmetro dela. Depois da chamada, o trecho pergunta se p vale NULL. O que aparece?**

- 1: a função recebeu o próprio p, e o apagou _(é o que a crença espera)_
- 0 _(é o que a máquina faz)_

A máquina imprime:

```
0
```

O que isto mostra: Saiu 0. A função recebeu uma cópia do endereço e escreveu NULL na cópia. O p de quem chamou é outra variável, e continua com o endereço do bloco. Com free(p) é igual: entra uma cópia.

## B3 — A caixa p é sua, de quem chamou. Ela não pertence à função free, e não fica dentro do bloco que ela aponta.

### Degrau 1 — guiado, escolher

> São duas coisas: o bloco, no monte, e a caixa do ponteiro, que fica onde foi declarada.
> free devolve só o bloco.

**Versão 1.** A última linha devolve o bloco. O que acontece com a caixa de p?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

Opções: `Continua onde estava: é uma variável de quem chamou`  `Vai junto: o ponteiro mora no monte, dentro do bloco que aponta`  `Passa a ser da função free`

Resposta certa: `Continua onde estava: é uma variável de quem chamou`

Se errar:

- respondeu `Vai junto: o ponteiro mora no monte, dentro do bloco que aponta` → Apontar para o monte não é morar nele. A caixa de p foi declarada como qualquer variável, e fica onde estava; o que voltou ao alocador foi só o bloco. _(aponta a crença `pointer_lives_in_heap`)_
- respondeu `Passa a ser da função free` → free recebeu uma cópia do endereço, e não a caixa. A caixa de p continua sendo de quem a declarou.
- qualquer outro erro → O bloco voltou ao alocador. A caixa de p continua onde foi declarada.

**Versão 2.** A última linha devolve o bloco. O que acontece com a caixa de q?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

Opções: `Passa a ser da função free`  `Continua onde estava: é uma variável de quem chamou`  `Vai junto: o ponteiro mora no monte, dentro do bloco que aponta`

Resposta certa: `Continua onde estava: é uma variável de quem chamou`

Se errar:

- respondeu `Vai junto: o ponteiro mora no monte, dentro do bloco que aponta` → Apontar para o monte não é morar nele. A caixa de q foi declarada como qualquer variável, e fica onde estava; o que voltou ao alocador foi só o bloco. _(aponta a crença `pointer_lives_in_heap`)_
- respondeu `Passa a ser da função free` → free recebeu uma cópia do endereço, e não a caixa. A caixa de q continua sendo de quem a declarou.
- qualquer outro erro → O bloco voltou ao alocador. A caixa de q continua onde foi declarada.

### Degrau 2 — guiado, escolher

> Toda variável local acaba no fim da função em que foi declarada, seja ponteiro ou não.
> O free devolve o bloco, e não mexe na caixa do ponteiro.

**Versão 1.** Quando a caixa de p deixa de existir?

Já está escrito:

```c
void usa(void) { int *p = malloc(sizeof(int)); free(p); }
```

Opções: `No fim de usa, como toda variável local`  `No free, junto com o bloco`  `Nunca: ela é do monte`

Resposta certa: `No fim de usa, como toda variável local`

Se errar:

- respondeu `No free, junto com o bloco` → O free devolve o bloco, e só. A caixa de p é variável local de usa: existe até a função terminar.
- respondeu `Nunca: ela é do monte` → A caixa de p não é do monte: foi declarada dentro de usa, e acaba quando usa termina.
- qualquer outro erro → p é variável local de usa: a caixa dela acaba no fim da função.

**Versão 2.** Quando a caixa de q deixa de existir?

Já está escrito:

```c
void anota(void) { int *q = malloc(sizeof(int)); free(q); }
```

Opções: `Nunca: ela é do monte`  `No free, junto com o bloco`  `No fim de anota, como toda variável local`

Resposta certa: `No fim de anota, como toda variável local`

Se errar:

- respondeu `No free, junto com o bloco` → O free devolve o bloco, e só. A caixa de q é variável local de anota: existe até a função terminar.
- respondeu `Nunca: ela é do monte` → A caixa de q não é do monte: foi declarada dentro de anota, e acaba quando anota termina.
- qualquer outro erro → q é variável local de anota: a caixa dela acaba no fim da função.

### Degrau 3 — guiado, digitar

> Como a caixa continua sendo sua, você escreve nela quando quiser — inclusive depois do free.

**Versão 1.** Depois do free, o trecho escreve NULL em p e pergunta se p vale NULL. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
printf("%d\n", p == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → A caixa de p continuou existindo depois do free, e recebeu NULL na linha seguinte. A pergunta é verdadeira: 1.
- qualquer outro erro → A caixa de p é sua: recebeu NULL depois do free, e a pergunta dá 1.

**Versão 2.** Depois do free, o trecho escreve NULL em q e pergunta se q é diferente de NULL. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
free(q);
q = NULL;
printf("%d\n", q != NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → A caixa de q continuou existindo depois do free, e recebeu NULL na linha seguinte. q não é diferente de NULL: 0.
- qualquer outro erro → A caixa de q é sua: recebeu NULL depois do free, e a pergunta dá 0.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A caixa de p não vai embora com o bloco_

**Versão 1.** Depois de devolver o bloco, o trecho usa a mesma caixa para outro. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
free(p);
p = malloc(sizeof(int));
*p = 15;
printf("%d\n", *p);
free(p);
```

Resposta certa: `15`

Se errar:

- digitou `7` → O bloco do 7 foi devolvido. A caixa de p continuou, recebeu o endereço de outro bloco, e nele foi escrito 15.
- qualquer outro erro → A caixa de p sobreviveu ao free e guardou outro endereço: o do bloco com 15.

**Versão 2.** Depois de devolver o bloco, o trecho usa a mesma caixa para outro. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
*q = 9;
free(q);
q = malloc(sizeof(int));
*q = 20;
printf("%d\n", *q);
free(q);
```

Resposta certa: `20`

Se errar:

- digitou `9` → O bloco do 9 foi devolvido. A caixa de q continuou, recebeu o endereço de outro bloco, e nele foi escrito 20.
- qualquer outro erro → A caixa de q sobreviveu ao free e guardou outro endereço: o do bloco com 20.

### Degrau 5 — prática, escolher

**Versão 1.** No fim deste trecho, o que ainda existe?

Já está escrito:

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
free(p);
```

Opções: `As caixas de p e de q; o bloco foi devolvido`  `Só a caixa de q: a de p foi junto com o bloco`  `Nada: free levou tudo`

Resposta certa: `As caixas de p e de q; o bloco foi devolvido`

Se errar:

- respondeu `Só a caixa de q: a de p foi junto com o bloco` → A caixa de p não fica dentro do bloco, e não vai junto com ele. As duas caixas continuam; só o bloco voltou ao alocador.
- respondeu `Nada: free levou tudo` → free devolve o bloco, e mais nada. As caixas de p e de q são variáveis de quem as declarou, e continuam lá.
- qualquer outro erro → O bloco foi devolvido. As duas caixas, p e q, continuam existindo.

**Versão 2.** No fim deste trecho, o que ainda existe?

Já está escrito:

```c
int *a;
int *b;

a = malloc(sizeof(int));
b = malloc(sizeof(int));
free(a);
```

Opções: `Só a caixa de b e o bloco dela`  `Nada: free levou tudo`  `As caixas de a e de b, e o bloco de b`

Resposta certa: `As caixas de a e de b, e o bloco de b`

Se errar:

- respondeu `Só a caixa de b e o bloco dela` → A caixa de a não foi junto com o bloco: continua onde foi declarada. Sobram as duas caixas, e o bloco de b.
- respondeu `Nada: free levou tudo` → free devolveu um bloco só, o de a. As duas caixas continuam, e o bloco de b também.
- qualquer outro erro → free devolveu o bloco de a. Continuam as duas caixas, e o bloco de b.

### Se errar a pergunta do topo: a revisão

> São duas coisas: o bloco, no monte, e a caixa de p, que é uma variável sua.
> free devolve o bloco. A caixa de p não está dentro dele, e fica onde foi declarada.

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
printf("%d\n", p == NULL);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro mora no heap porque aponta para lá.

```c
int *p;

p = malloc(sizeof(int));
printf("%p\n", (void *)&p);
printf("%p\n", (void *)p);
free(p);
```

**O primeiro printf mostra o endereço da caixa p. O segundo mostra o endereço do bloco, que é o que p guarda. O que aparece?**

- Dois endereços diferentes _(é o que a máquina faz)_
- O mesmo endereço: a caixa de p fica dentro do bloco _(é o que a crença espera)_

A máquina imprime:

```
0x1000
0x2A00
```

_Os números dos lugares mudam de máquina para máquina; aqui eles aparecem como números de exemplo. O que foi conferido é que as duas linhas saem com endereços diferentes._

O que isto mostra: Saíram dois endereços diferentes. A caixa de p está num lugar; o bloco, em outro. p aponta para o monte, mas não mora nele — e é por isso que devolver o bloco não leva a caixa junto.

## B4 — Devolvido, o pedaço deixa de ser seu. Pode ser entregue a outro pedido a qualquer momento.

### Degrau 1 — guiado, escolher

> malloc aluga um lugar do alocador; free devolve o aluguel.
> Lugar devolvido volta para o alocador, junto com os que ainda não foram alugados.

**Versão 1.** Depois da última linha, o bloco é de quem?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
free(p);
```

Opções: `Do alocador, que pode entregá-lo a outro pedido`  `Seu ainda: o bloco continua válido depois do free, com o 7`  `De ninguém: aquele lugar deixa de existir`

Resposta certa: `Do alocador, que pode entregá-lo a outro pedido`

Se errar:

- respondeu `Seu ainda: o bloco continua válido depois do free, com o 7` → free é devolver: dali em diante o bloco é do alocador, que pode entregá-lo ao próximo malloc. O 7 não fica guardado para você. _(aponta a crença `heap_persists`)_
- respondeu `De ninguém: aquele lugar deixa de existir` → O lugar continua existindo na memória; o que mudou é o dono. Ele voltou ao alocador, que pode entregá-lo a outro pedido.
- qualquer outro erro → Depois do free o bloco é do alocador, que pode entregá-lo a outro pedido.

**Versão 2.** Depois da última linha, o bloco é de quem?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
*q = 15;
free(q);
```

Opções: `De ninguém: aquele lugar deixa de existir`  `Do alocador, que pode entregá-lo a outro pedido`  `Seu ainda: o bloco continua válido depois do free, com o 15`

Resposta certa: `Do alocador, que pode entregá-lo a outro pedido`

Se errar:

- respondeu `Seu ainda: o bloco continua válido depois do free, com o 15` → free é devolver: dali em diante o bloco é do alocador, que pode entregá-lo ao próximo malloc. O 15 não fica guardado para você. _(aponta a crença `heap_persists`)_
- respondeu `De ninguém: aquele lugar deixa de existir` → O lugar continua existindo na memória; o que mudou é o dono. Ele voltou ao alocador, que pode entregá-lo a outro pedido.
- qualquer outro erro → Depois do free o bloco é do alocador, que pode entregá-lo a outro pedido.

### Degrau 2 — guiado, escolher

> Usar o bloco depois do free — ler ou escrever — é usar o que não é seu.
> O compilador reclama quando consegue ver.

**Versão 1.** Qual linha deste trecho usa um bloco que já não é seu?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
free(p);
*p = 9;
```

Opções: `A última: escreve no bloco depois de devolvê-lo`  `A que escreve 7: o bloco ainda não tinha valor`  `Nenhuma: o bloco continua lá`

Resposta certa: `A última: escreve no bloco depois de devolvê-lo`

Se errar:

- respondeu `A que escreve 7: o bloco ainda não tinha valor` → Escrever num bloco que é seu sempre vale, com ou sem valor antes. O problema é a última linha, que escreve depois do free.
- respondeu `Nenhuma: o bloco continua lá` → O lugar continua lá, mas já não é seu: voltou ao alocador no free. A última linha escreve no que é de outro.
- qualquer outro erro → Depois do free o bloco não é seu. A última linha escreve nele mesmo assim.

**Versão 2.** Qual linha deste trecho usa um bloco que já não é seu?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
*q = 15;
free(q);
printf("%d\n", *q);
```

Opções: `Nenhuma: o bloco continua lá`  `A que escreve 15: o bloco ainda não tinha valor`  `A última: lê o bloco depois de devolvê-lo`

Resposta certa: `A última: lê o bloco depois de devolvê-lo`

Se errar:

- respondeu `A que escreve 15: o bloco ainda não tinha valor` → Escrever num bloco que é seu sempre vale, com ou sem valor antes. O problema é a última linha, que lê depois do free.
- respondeu `Nenhuma: o bloco continua lá` → O lugar continua lá, mas já não é seu: voltou ao alocador no free. A última linha lê o que é de outro.
- qualquer outro erro → Depois do free o bloco não é seu. A última linha lê nele mesmo assim.

### Degrau 3 — guiado, montar

> O último uso do bloco vem antes do free. Depois dele, não há mais uso.

**Versão 1.** Ponha as duas linhas na ordem certa: primeiro usa, depois devolve.

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
```

Peças: `printf("%d\n", *p);`  `free(p);`

Resposta certa: `printf("%d\n", *p); free(p);`

Se errar:

- respondeu `free(p); printf("%d\n", *p);` → Nessa ordem o printf lê o bloco depois de devolvido, quando ele já não é seu. Primeiro se usa, depois se devolve.
- qualquer outro erro → Primeiro o uso, depois o free: o printf vem antes.

**Versão 2.** Ponha as duas linhas na ordem certa: primeiro usa, depois devolve.

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
```

Peças: `free(q);`  `*q = 15;`

Resposta certa: `*q = 15; free(q);`

Se errar:

- respondeu `free(q); *q = 15;` → Nessa ordem a escrita vai para o bloco depois de devolvido, quando ele já não é seu. Primeiro se usa, depois se devolve.
- qualquer outro erro → Primeiro o uso, depois o free: a escrita vem antes.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Depois do free, o bloco não é mais seu_

**Versão 1.** O valor do bloco é copiado para nota antes do free. Que número aparece?

```c
int *p;
int nota;

p = malloc(sizeof(int));
*p = 7;
nota = *p;
free(p);
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `0` → O free devolveu o bloco, mas nota é uma variável sua, e já tinha recebido o 7 antes. Ela continua com ele.
- qualquer outro erro → O 7 foi copiado para nota antes do free. nota é sua, e continua com 7.

**Versão 2.** O valor do bloco é copiado para idade antes do free. Que número aparece?

```c
int *q;
int idade;

q = malloc(sizeof(int));
*q = 15;
idade = *q;
free(q);
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → O free devolveu o bloco, mas idade é uma variável sua, e já tinha recebido o 15 antes. Ela continua com ele.
- qualquer outro erro → O 15 foi copiado para idade antes do free. idade é sua, e continua com 15.

### Degrau 5 — prática, escolher

**Versão 1.** Depois do free, o trecho pede outro bloco, para q. O que pode acontecer?

Já está escrito:

```c
int *p;
int *q;

p = malloc(sizeof(int));
free(p);
q = malloc(sizeof(int));
```

Opções: `q pode receber o mesmo lugar que era de p`  `Nada: o lugar de p fica reservado para p`  `O malloc falha: aquele lugar ainda está ocupado`

Resposta certa: `q pode receber o mesmo lugar que era de p`

Se errar:

- respondeu `Nada: o lugar de p fica reservado para p` → Depois do free o lugar não é mais de p: voltou ao alocador, que pode entregá-lo a qualquer pedido — inclusive ao de q.
- respondeu `O malloc falha: aquele lugar ainda está ocupado` → O free desocupou o lugar: ele está livre para o alocador entregar de novo. Pode até ser o que q recebe.
- qualquer outro erro → O lugar voltou ao alocador, que pode entregá-lo ao malloc seguinte: o de q.

**Versão 2.** Depois do free, o trecho pede outro bloco, para b. O que pode acontecer?

Já está escrito:

```c
int *a;
int *b;

a = malloc(sizeof(int));
free(a);
b = malloc(sizeof(int));
```

Opções: `O malloc falha: aquele lugar ainda está ocupado`  `b pode receber o mesmo lugar que era de a`  `Nada: o lugar de a fica reservado para a`

Resposta certa: `b pode receber o mesmo lugar que era de a`

Se errar:

- respondeu `Nada: o lugar de a fica reservado para a` → Depois do free o lugar não é mais de a: voltou ao alocador, que pode entregá-lo a qualquer pedido — inclusive ao de b.
- respondeu `O malloc falha: aquele lugar ainda está ocupado` → O free desocupou o lugar: ele está livre para o alocador entregar de novo. Pode até ser o que b recebe.
- qualquer outro erro → O lugar voltou ao alocador, que pode entregá-lo ao malloc seguinte: o de b.

### Se errar a pergunta do topo: a revisão

> Devolvido, o bloco deixa de ser seu: o alocador pode entregá-lo ao próximo malloc.
> O último uso do bloco vem antes do free. Depois dele, não se lê nem se escreve ali.

```c
int *p;
int nota;

p = malloc(sizeof(int));
*p = 7;
nota = *p;
free(p);
printf("%d\n", nota);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> O bloco ainda é válido depois de free().

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
free(p);
printf("%d\n", *p);
```

**O trecho escreve 7 no bloco, devolve o bloco, e depois lê o que há nele. O compilador reclama de alguma coisa?**

- Não: o 7 continua no bloco, que ainda é válido _(é o que a crença espera)_
- Sim: o bloco é usado depois de devolvido _(é o que a máquina faz)_

O compilador reclama:

```
pointer 'p' used after 'free'
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall): "used after free" é "usado depois do free". O programa não é executado: o que apareceria, ninguém sabe._

O que isto mostra: O compilador reclama da última linha: p é usado depois do free. O bloco voltou ao alocador, que pode entregá-lo a outro pedido a qualquer momento. O 7 não está guardado para você.

## I1 — Então free não tem como mudar o que está dentro de p: ela só recebeu uma cópia do valor, e a caixa não é dela.

### Degrau 1 — guiado, escolher

> free recebe só uma cópia do endereço guardado em p.
> No p de quem chamou ela não tem como escrever.

**Versão 1.** Depois da última linha, o que está guardado em p?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

Opções: `O mesmo endereço de antes`  `NULL: p vira NULL depois do free`  `Nada: p fica vazio`

Resposta certa: `O mesmo endereço de antes`

Se errar:

- respondeu `NULL: p vira NULL depois do free` → Para pôr NULL em p, free teria de escrever na variável de quem chamou — e ela só recebeu uma cópia do endereço. p continua como estava. _(aponta a crença `free_nullifies`)_
- respondeu `Nada: p fica vazio` → Variável não fica vazia: p continua guardando o que tinha, o endereço de antes. free só recebeu uma cópia dele.
- qualquer outro erro → free não escreve em p. Depois dela, p guarda o mesmo endereço de antes.

**Versão 2.** Depois da última linha, o que está guardado em q?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

Opções: `Nada: q fica vazio`  `O mesmo endereço de antes`  `NULL: q vira NULL depois do free`

Resposta certa: `O mesmo endereço de antes`

Se errar:

- respondeu `NULL: q vira NULL depois do free` → Para pôr NULL em q, free teria de escrever na variável de quem chamou — e ela só recebeu uma cópia do endereço. q continua como estava. _(aponta a crença `free_nullifies`)_
- respondeu `Nada: q fica vazio` → Variável não fica vazia: q continua guardando o que tinha, o endereço de antes. free só recebeu uma cópia dele.
- qualquer outro erro → free não escreve em q. Depois dela, q guarda o mesmo endereço de antes.

### Degrau 2 — guiado, digitar

> Dá para ver: guardando uma cópia de p antes do free, as duas continuam iguais depois.

**Versão 1.** q guarda uma cópia do endereço, feita antes do free. A última linha pergunta se p e q são iguais. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
free(p);
printf("%d\n", p == q);
```

Resposta certa: `1`

Se errar:

- digitou `0` → free não mudou o que está em p: ela só recebeu uma cópia. p continua com o endereço que q copiou, e os dois são iguais.
- qualquer outro erro → free não escreveu em p. p e q continuam com o mesmo endereço: 1.

**Versão 2.** p guarda uma cópia do endereço, feita antes do free. A última linha pergunta se p e q são diferentes. Que número aparece?

```c
int *p;
int *q;

q = malloc(sizeof(int));
p = q;
free(q);
printf("%d\n", p != q);
```

Resposta certa: `0`

Se errar:

- digitou `1` → free não mudou o que está em q: ela só recebeu uma cópia. q continua com o endereço que p copiou, e os dois não são diferentes.
- qualquer outro erro → free não escreveu em q. p e q continuam com o mesmo endereço: a resposta é 0.

### Degrau 3 — guiado, escolher

> Depois do free, p continua com o endereço antigo, e nada no programa o troca sozinho.
> Uma variável só muda quando uma linha escreve nela.

**Versão 1.** Depois do free(p);, quem pode pôr NULL em p?

Opções: `Você, com a linha p = NULL;`  `O próprio free, um instante depois`  `Ninguém: p não aceita mais valor`

Resposta certa: `Você, com a linha p = NULL;`

Se errar:

- respondeu `O próprio free, um instante depois` → free não tem como escrever em p, nem na hora nem depois: recebeu só uma cópia do endereço. O NULL é uma linha sua.
- respondeu `Ninguém: p não aceita mais valor` → p é uma variável sua, e aceita valor como sempre. Quem quiser NULL nela escreve: p = NULL;
- qualquer outro erro → free não escreve em p. O NULL é você que escreve: p = NULL;

**Versão 2.** Depois do free(q);, quem pode pôr NULL em q?

Opções: `Ninguém: q não aceita mais valor`  `O próprio free, um instante depois`  `Você, com a linha q = NULL;`

Resposta certa: `Você, com a linha q = NULL;`

Se errar:

- respondeu `O próprio free, um instante depois` → free não tem como escrever em q, nem na hora nem depois: recebeu só uma cópia do endereço. O NULL é uma linha sua.
- respondeu `Ninguém: q não aceita mais valor` → q é uma variável sua, e aceita valor como sempre. Quem quiser NULL nela escreve: q = NULL;
- qualquer outro erro → free não escreve em q. O NULL é você que escreve: q = NULL;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: free não muda o valor de p_

**Versão 1.** Depois do free, a última linha pergunta se p é diferente de NULL. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
free(p);
printf("%d\n", p != NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → free não pôs NULL em p: ela só recebeu uma cópia do endereço. p continua com o endereço de antes, que é diferente de NULL.
- qualquer outro erro → p continua com o endereço de antes, que não é NULL: 1.

**Versão 2.** A função só chama free. Depois dela, a última linha pergunta se q é diferente de NULL. Que número aparece?

```c
void libera(int *x) { free(x); }

int *q;

q = malloc(sizeof(int));
libera(q);
printf("%d\n", q != NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → Nem libera nem free escreveram em q: as duas receberam cópias do endereço. q continua com o endereço de antes, diferente de NULL.
- qualquer outro erro → q continua com o endereço de antes, que não é NULL: 1.

### Degrau 5 — prática, escolher

**Versão 1.** Qual dos dois trechos deixa p valendo NULL?

Já está escrito:

```c
/* A */  free(p);
/* B */  free(p);  p = NULL;
```

Opções: `O B: é a linha p = NULL; que escreve`  `Os dois: free já deixa p em NULL`  `Nenhum: depois do free, p não aceita valor`

Resposta certa: `O B: é a linha p = NULL; que escreve`

Se errar:

- respondeu `Os dois: free já deixa p em NULL` → free recebe só uma cópia do endereço, e não escreve em p. No A, p fica com o endereço antigo; no B, quem escreve o NULL é a sua linha.
- respondeu `Nenhum: depois do free, p não aceita valor` → p continua sendo uma variável sua, e aceita valor. No B ela recebe NULL, pela linha que você escreveu.
- qualquer outro erro → free não escreve em p. Só no B há uma linha que põe NULL: p = NULL;

**Versão 2.** Qual dos dois trechos deixa q valendo NULL?

Já está escrito:

```c
/* A */  free(q);  q = NULL;
/* B */  free(q);
```

Opções: `Nenhum: depois do free, q não aceita valor`  `Os dois: free já deixa q em NULL`  `O A: é a linha q = NULL; que escreve`

Resposta certa: `O A: é a linha q = NULL; que escreve`

Se errar:

- respondeu `Os dois: free já deixa q em NULL` → free recebe só uma cópia do endereço, e não escreve em q. No B, q fica com o endereço antigo; no A, quem escreve o NULL é a sua linha.
- respondeu `Nenhum: depois do free, q não aceita valor` → q continua sendo uma variável sua, e aceita valor. No A ela recebe NULL, pela linha que você escreveu.
- qualquer outro erro → free não escreve em q. Só no A há uma linha que põe NULL: q = NULL;

### Se errar a pergunta do topo: a revisão

> free recebeu só uma cópia do endereço. No p de quem chamou ela não tem como escrever.
> Por isso, depois do free, p não vira NULL: continua com o endereço de antes.

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
free(p);
printf("%d\n", p == q);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> p vira NULL depois de free().

```c
int *p;

p = malloc(sizeof(int));
free(p);
printf("%d\n", p == NULL);
```

**O trecho devolve o bloco e, logo depois, pergunta se p vale NULL. O que aparece?**

- 1: p vira NULL depois do free _(é o que a crença espera)_
- 0: p continua com o endereço de antes _(é o que a máquina faz)_

A máquina imprime:

```
0
```

_Foi o que saiu nesta máquina. O padrão do C não garante nem essa comparação depois do free — é a última ideia deste tópico. Aqui ela foi feita para mostrar que free não escreveu NULL._

O que isto mostra: Saiu 0. free não escreveu NULL em p, e nem teria como: recebeu só uma cópia do endereço. p continua com o endereço de antes — de um bloco que já não é seu.

## I2 — Depois do free, a caixa p continua ali, com o mesmo endereço escrito dentro.

### Degrau 1 — guiado, escolher

> free devolve o bloco, e só: não mexe em variável nenhuma de quem chamou.
> Um ponteiro que guarda o endereço de um lugar que já não é seu se chama pendente.

**Versão 1.** Depois da última linha, o que é verdade sobre a variável p?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

Opções: `Continua existindo, com o endereço antigo`  `Foi apagada: free(p) apaga a variável p`  `Continua existindo, e sem valor nenhum`

Resposta certa: `Continua existindo, com o endereço antigo`

Se errar:

- respondeu `Foi apagada: free(p) apaga a variável p` → free devolve o bloco, e não apaga variável nenhuma. p continua declarada, guardando o endereço antigo — agora de um lugar que não é seu. _(aponta a crença `free_kills_pointer`)_
- respondeu `Continua existindo, e sem valor nenhum` → Variável não fica sem valor: p guarda o que tinha, o endereço antigo. Ela ficou pendente, apontando para um lugar que não é seu.
- qualquer outro erro → p continua existindo, com o endereço antigo: é um ponteiro pendente.

**Versão 2.** Depois da última linha, o que é verdade sobre a variável q?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

Opções: `Continua existindo, e sem valor nenhum`  `Continua existindo, com o endereço antigo`  `Foi apagada: free(q) apaga a variável q`

Resposta certa: `Continua existindo, com o endereço antigo`

Se errar:

- respondeu `Foi apagada: free(q) apaga a variável q` → free devolve o bloco, e não apaga variável nenhuma. q continua declarada, guardando o endereço antigo — agora de um lugar que não é seu. _(aponta a crença `free_kills_pointer`)_
- respondeu `Continua existindo, e sem valor nenhum` → Variável não fica sem valor: q guarda o que tinha, o endereço antigo. Ela ficou pendente, apontando para um lugar que não é seu.
- qualquer outro erro → q continua existindo, com o endereço antigo: é um ponteiro pendente.

### Degrau 2 — guiado, escolher

> Como p continua declarada, dá para usá-la de novo.
> E não dá para declará-la outra vez: o nome já existe.

**Versão 1.** Depois do free(p);, qual destas linhas o compilador aceita?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

Opções: `p = malloc(sizeof(int));`  `int *p = malloc(sizeof(int));`  `int p;`

Resposta certa: `p = malloc(sizeof(int));`

Se errar:

- respondeu `int *p = malloc(sizeof(int));` → Essa linha declara p outra vez, e p nunca deixou de existir: o compilador reclama. Para dar outro bloco a ela, basta p = malloc(sizeof(int));
- respondeu `int p;` → O nome p continua em uso: free não apagou a variável. Declarar outro p faz o compilador reclamar.
- qualquer outro erro → p continua declarada. Usa-se de novo, sem declarar outra vez: p = malloc(sizeof(int));

**Versão 2.** Depois do free(q);, qual destas linhas o compilador aceita?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

Opções: `int q;`  `q = malloc(sizeof(int));`  `int *q = malloc(sizeof(int));`

Resposta certa: `q = malloc(sizeof(int));`

Se errar:

- respondeu `int *q = malloc(sizeof(int));` → Essa linha declara q outra vez, e q nunca deixou de existir: o compilador reclama. Para dar outro bloco a ela, basta q = malloc(sizeof(int));
- respondeu `int q;` → O nome q continua em uso: free não apagou a variável. Declarar outro q faz o compilador reclamar.
- qualquer outro erro → q continua declarada. Usa-se de novo, sem declarar outra vez: q = malloc(sizeof(int));

### Degrau 3 — guiado, digitar

> A mesma variável pode receber o endereço de outro bloco, e voltar a servir.

**Versão 1.** Depois do free, p recebe outro bloco. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = malloc(sizeof(int));
*p = 15;
printf("%d\n", *p);
free(p);
```

Resposta certa: `15`

Se errar:

- digitou `0` → p não foi apagada no free: recebeu o endereço de outro bloco, e nele foi escrito 15.
- qualquer outro erro → p continuou existindo, recebeu outro bloco, e nele está o 15.

**Versão 2.** Depois do free, q recebe outro bloco. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
free(q);
q = malloc(sizeof(int));
*q = 20;
printf("%d\n", *q);
free(q);
```

Resposta certa: `20`

Se errar:

- digitou `0` → q não foi apagada no free: recebeu o endereço de outro bloco, e nele foi escrito 20.
- qualquer outro erro → q continuou existindo, recebeu outro bloco, e nele está o 20.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Depois do free, p continua existindo_

**Versão 1.** O trecho devolve o bloco, escreve NULL em p e pergunta se p vale NULL. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
free(p);
p = NULL;
printf("%d\n", p == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → A variável p continuou existindo depois do free, e recebeu NULL na linha seguinte. A pergunta é verdadeira: 1.
- digitou `7` → 7 estava no bloco, que foi devolvido. O printf mostra a resposta da pergunta p == NULL, e p recebeu NULL: 1.
- qualquer outro erro → p continua existindo: recebeu NULL depois do free, e a pergunta dá 1.

**Versão 2.** O trecho devolve o bloco, escreve NULL em q e pergunta se q é diferente de NULL. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
*q = 15;
free(q);
q = NULL;
printf("%d\n", q != NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → A variável q continuou existindo depois do free, e recebeu NULL na linha seguinte. Ela não é diferente de NULL: 0.
- digitou `15` → 15 estava no bloco, que foi devolvido. O printf mostra a resposta da pergunta q != NULL, e q recebeu NULL: 0.
- qualquer outro erro → q continua existindo: recebeu NULL depois do free, e a pergunta dá 0.

### Degrau 5 — prática, escolher

**Versão 1.** p e q apontam para dois blocos do malloc, e a última linha foi free(p);. Qual dos dois está pendente?

Opções: `p`  `q`  `Nenhum dos dois`

Resposta certa: `p`

Se errar:

- respondeu `q` → O bloco de q ainda é seu: nenhum free o devolveu. Pendente é p, que guarda o endereço de um bloco já devolvido.
- respondeu `Nenhum dos dois` → free(p) não apaga p: devolve o bloco. p continua lá, com o endereço antigo — é isso que o deixa pendente.
- qualquer outro erro → p está pendente: guarda o endereço de um bloco que free(p) já devolveu.

**Versão 2.** Depois de qual destas linhas p fica pendente?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
```

Opções: `p = NULL;`  `free(p);`  `*p = 0;`

Resposta certa: `free(p);`

Se errar:

- respondeu `p = NULL;` → Com p = NULL; o ponteiro passa a dizer que não aponta para nada. Pendente ele fica depois de free(p);, guardando o endereço de um bloco devolvido.
- respondeu `*p = 0;` → *p = 0; escreve no bloco, que ainda é seu. Pendente p fica depois de free(p);, guardando o endereço de um bloco devolvido.
- qualquer outro erro → Depois de free(p); p continua com o endereço de um bloco devolvido: pendente.

### Se errar a pergunta do topo: a revisão

> free devolve o bloco, e só. A variável p continua declarada, com o mesmo endereço dentro.
> Esse endereço leva agora a um lugar que não é seu: p ficou pendente.

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = malloc(sizeof(int));
*p = 15;
printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> free(p) apaga a variável p.

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = malloc(sizeof(int));
*p = 9;
printf("%d\n", *p);
free(p);
```

**Depois do free, o trecho usa a variável p de novo: guarda nela o endereço de outro bloco, e escreve 9 nele. O que aparece?**

- 9 _(é o que a máquina faz)_
- Nada: free apagou a variável p, e ela não pode mais ser usada _(é o que a crença espera)_

A máquina imprime:

```
9
```

O que isto mostra: Saiu 9. free devolveu o bloco, e a variável p continuou existindo: recebeu o endereço de outro bloco e serviu de novo. Quem acaba no free é o bloco, e não o ponteiro.

## I3 — Nada no programa avisa que aquele endereço ficou ruim. Escrever NULL em p logo depois do free deixa registrado que ela não aponta mais para nada.

### Degrau 1 — guiado, escolher

> Depois do free, nada no programa avisa que o endereço em p ficou ruim: ele tem a mesma cara de antes.
> Já o NULL diz, com todas as letras: não aponta para lugar nenhum.

**Versão 1.** Para que serve a última linha?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
```

Opções: `Para registrar que p não aponta mais para nada`  `Para nada: é redundante, porque free já cuida disso`  `Para devolver o bloco de vez`

Resposta certa: `Para registrar que p não aponta mais para nada`

Se errar:

- respondeu `Para nada: é redundante, porque free já cuida disso` → free não escreve em p: depois dela p continua com o endereço antigo, e nada avisa que ele ficou ruim. O NULL é o único registro, e é você que escreve. _(aponta a crença `null_after_free_redundant`)_
- respondeu `Para devolver o bloco de vez` → O bloco já foi devolvido no free, inteiro. A linha p = NULL; não devolve nada: só registra que p não aponta mais para lá.
- qualquer outro erro → p = NULL; registra que p não aponta mais para nada. free não faz isso.

**Versão 2.** Para que serve a última linha?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
q = NULL;
```

Opções: `Para devolver o bloco de vez`  `Para registrar que q não aponta mais para nada`  `Para nada: é redundante, porque free já cuida disso`

Resposta certa: `Para registrar que q não aponta mais para nada`

Se errar:

- respondeu `Para nada: é redundante, porque free já cuida disso` → free não escreve em q: depois dela q continua com o endereço antigo, e nada avisa que ele ficou ruim. O NULL é o único registro, e é você que escreve. _(aponta a crença `null_after_free_redundant`)_
- respondeu `Para devolver o bloco de vez` → O bloco já foi devolvido no free, inteiro. A linha q = NULL; não devolve nada: só registra que q não aponta mais para lá.
- qualquer outro erro → q = NULL; registra que q não aponta mais para nada. free não faz isso.

### Degrau 2 — guiado, digitar

> Com o NULL escrito, a pergunta de sempre volta a funcionar: if (p != NULL) ...

**Versão 1.** Depois do free e do NULL, a escrita só acontece se p não for NULL. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
if (p != NULL) *p = 7;
printf("%d\n", p == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → p recebeu NULL depois do free. A pergunta if (p != NULL) deu não, a escrita foi pulada, e p == NULL é verdade: 1.
- digitou `7` → A escrita do 7 não aconteceu: p vale NULL, e a pergunta do if deu não. O printf mostra que p == NULL é verdade: 1.
- qualquer outro erro → p vale NULL: o if pula a escrita, e p == NULL dá 1.

**Versão 2.** Depois do free e do NULL, a escrita só acontece se q não for NULL. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
free(q);
q = NULL;
if (q != NULL) *q = 9;
printf("%d\n", q != NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → q recebeu NULL depois do free. A pergunta if (q != NULL) deu não, a escrita foi pulada, e q != NULL é falso: 0.
- digitou `9` → A escrita do 9 não aconteceu: q vale NULL, e a pergunta do if deu não. O printf mostra que q != NULL é falso: 0.
- qualquer outro erro → q vale NULL: o if pula a escrita, e q != NULL dá 0.

### Degrau 3 — guiado, completar

> O costume é uma linha só, logo depois do free, escrevendo NULL no próprio ponteiro.

**Versão 1.** Complete com a linha que deixa registrado que p não aponta mais para nada.

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
```

```c
___;
```

Peças: `p = NULL`  `*p = NULL`  `free(p)`

Resposta certa: `p = NULL;`

Se errar:

- respondeu `*p = NULL;` → *p é o bloco, que já foi devolvido — e NULL é um endereço, não um int: o compilador reclama. O registro vai no ponteiro: p = NULL;
- respondeu `free(p);` → Um segundo free devolveria de novo um bloco que já não é seu. O que falta é o registro, no ponteiro: p = NULL;
- qualquer outro erro → O registro vai no ponteiro, logo depois do free: p = NULL;

**Versão 2.** Complete com a linha que deixa registrado que q não aponta mais para nada.

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
```

```c
___;
```

Peças: `free(q)`  `q = NULL`  `*q = NULL`

Resposta certa: `q = NULL;`

Se errar:

- respondeu `*q = NULL;` → *q é o bloco, que já foi devolvido — e NULL é um endereço, não um int: o compilador reclama. O registro vai no ponteiro: q = NULL;
- respondeu `free(q);` → Um segundo free devolveria de novo um bloco que já não é seu. O que falta é o registro, no ponteiro: q = NULL;
- qualquer outro erro → O registro vai no ponteiro, logo depois do free: q = NULL;

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Escrever NULL depois do free_

**Versão 1.** Depois de qual dos dois trechos a pergunta p == NULL diz a verdade sobre p?

Já está escrito:

```c
/* A */  free(p);
/* B */  free(p);  p = NULL;
```

Opções: `Do B: nele você escreveu o NULL`  `Dos dois: free já deixa o registro`  `Do A: free deixa p em NULL`

Resposta certa: `Do B: nele você escreveu o NULL`

Se errar:

- respondeu `Dos dois: free já deixa o registro` → free não deixa registro nenhum em p. No A, p continua com o endereço antigo, e a pergunta responde que ele não é NULL — embora não aponte para nada seu.
- respondeu `Do A: free deixa p em NULL` → free não escreve em p. No A a pergunta diria que p não é NULL, com p apontando para um bloco devolvido. Só o B registra.
- qualquer outro erro → Só no B há o registro: a linha p = NULL; é sua.

**Versão 2.** Depois de qual dos dois trechos a pergunta q == NULL diz a verdade sobre q?

Já está escrito:

```c
/* A */  free(q);  q = NULL;
/* B */  free(q);
```

Opções: `Do B: free deixa q em NULL`  `Dos dois: free já deixa o registro`  `Do A: nele você escreveu o NULL`

Resposta certa: `Do A: nele você escreveu o NULL`

Se errar:

- respondeu `Dos dois: free já deixa o registro` → free não deixa registro nenhum em q. No B, q continua com o endereço antigo, e a pergunta responde que ele não é NULL — embora não aponte para nada seu.
- respondeu `Do B: free deixa q em NULL` → free não escreve em q. No B a pergunta diria que q não é NULL, com q apontando para um bloco devolvido. Só o A registra.
- qualquer outro erro → Só no A há o registro: a linha q = NULL; é sua.

### Degrau 5 — prática, digitar

**Versão 1.** Os dois blocos são devolvidos, e só p recebe NULL. A última linha pergunta se q vale NULL. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = malloc(sizeof(int));
free(p);
p = NULL;
free(q);
printf("%d\n", q == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → Quem recebeu NULL foi p, pela linha p = NULL;. Em q ninguém escreveu: ele continua com o endereço antigo, e q == NULL é falso.
- qualquer outro erro → Só p recebeu NULL. q continua com o endereço antigo: a resposta é 0.

**Versão 2.** Os dois blocos são devolvidos, e só q recebe NULL. A última linha pergunta se p é diferente de NULL. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = malloc(sizeof(int));
free(q);
q = NULL;
free(p);
printf("%d\n", p != NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → Quem recebeu NULL foi q, pela linha q = NULL;. Em p ninguém escreveu: ele continua com o endereço antigo, diferente de NULL.
- qualquer outro erro → Só q recebeu NULL. p continua com o endereço antigo: a resposta é 1.

### Se errar a pergunta do topo: a revisão

> Depois do free, nada avisa que o endereço em p ficou ruim: ele tem a mesma cara de antes.
> Escrever p = NULL; logo depois é o registro de que p não aponta mais para nada.

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
if (p != NULL) *p = 7;
printf("%d\n", p == NULL);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> Atribuir NULL após free() é redundante, porque free já cuida disso.

```c
int *p = malloc(sizeof(int));
int *q = malloc(sizeof(int));

free(p);
p = NULL;
free(q);
printf("%d\n", p == NULL);
printf("%d\n", q == NULL);
```

**Os dois blocos são devolvidos, e só p recebe NULL depois. O trecho pergunta, de cada um, se vale NULL. O que aparece?**

- 1 e 1: free já deixa os dois em NULL, e a linha p = NULL; é redundante _(é o que a crença espera)_
- 1 e 0 _(é o que a máquina faz)_

A máquina imprime:

```
1
0
```

_Foi o que saiu nesta máquina. O padrão do C não garante a comparação de q, que ficou pendente — é a última ideia deste tópico. Aqui ela foi feita para mostrar a diferença que a linha p = NULL; faz._

O que isto mostra: Saíram 1 e 0. Só o ponteiro em que você escreveu NULL responde "sim, não aponto para nada". O outro continua com um endereço de cara boa. A linha não é redundante: é o único registro.

## I4 — Juntando: p continua com um endereço bom de aparência, apontando para um lugar que já não guarda nada seu. Até copiar ou comparar p já é território sem garantia.

### Degrau 1 — guiado, escolher

> Depois do free, p guarda um endereço com cara de bom, de um lugar que já não é seu.
> Um bloco só pode ser devolvido uma vez, e o compilador reclama quando vê.

**Versão 1.** O que a última linha faz?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
free(p);
```

Opções: `Devolve de novo um bloco que já não é seu: é inválido`  `Nada: chamar free duas vezes no mesmo ponteiro é seguro`  `Devolve a variável p`

Resposta certa: `Devolve de novo um bloco que já não é seu: é inválido`

Se errar:

- respondeu `Nada: chamar free duas vezes no mesmo ponteiro é seguro` → Depois do primeiro free, p continua com o endereço antigo. O segundo recebe esse endereço e devolve de novo um lugar que pode até já ser de outro pedido. _(aponta a crença `double_free_is_safe`)_
- respondeu `Devolve a variável p` → free nunca devolve variável: recebe um endereço e devolve o bloco de lá. Aqui é o mesmo bloco, pela segunda vez.
- qualquer outro erro → O segundo free devolve de novo um bloco que já não é seu: é inválido.

**Versão 2.** O que a última linha faz?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
free(q);
```

Opções: `Devolve a variável q`  `Devolve de novo um bloco que já não é seu: é inválido`  `Nada: chamar free duas vezes no mesmo ponteiro é seguro`

Resposta certa: `Devolve de novo um bloco que já não é seu: é inválido`

Se errar:

- respondeu `Nada: chamar free duas vezes no mesmo ponteiro é seguro` → Depois do primeiro free, q continua com o endereço antigo. O segundo recebe esse endereço e devolve de novo um lugar que pode até já ser de outro pedido. _(aponta a crença `double_free_is_safe`)_
- respondeu `Devolve a variável q` → free nunca devolve variável: recebe um endereço e devolve o bloco de lá. Aqui é o mesmo bloco, pela segunda vez.
- qualquer outro erro → O segundo free devolve de novo um bloco que já não é seu: é inválido.

### Degrau 2 — guiado, escolher

> A exceção é o NULL: free(NULL) não faz nada, e não é erro.

**Versão 1.** Qual dos dois trechos é válido?

Já está escrito:

```c
/* A */  free(p);  free(p);
/* B */  free(p);  p = NULL;  free(p);
```

Opções: `O B: o segundo free recebe NULL, e não faz nada`  `O A: o segundo free não acha nada para devolver`  `Os dois`

Resposta certa: `O B: o segundo free recebe NULL, e não faz nada`

Se errar:

- respondeu `O A: o segundo free não acha nada para devolver` → No A, p continua com o endereço antigo, e o segundo free devolve de novo o mesmo bloco. No B, p vale NULL, e free(NULL) não faz nada.
- respondeu `Os dois` → No A o mesmo bloco é devolvido duas vezes, e isso é inválido. Só o B é válido: o segundo free recebe NULL.
- qualquer outro erro → free(NULL) não faz nada. No B o segundo free recebe NULL, e o trecho é válido.

**Versão 2.** Qual dos dois trechos é válido?

Já está escrito:

```c
/* A */  free(q);  q = NULL;  free(q);
/* B */  free(q);  free(q);
```

Opções: `Os dois`  `O B: o segundo free não acha nada para devolver`  `O A: o segundo free recebe NULL, e não faz nada`

Resposta certa: `O A: o segundo free recebe NULL, e não faz nada`

Se errar:

- respondeu `O B: o segundo free não acha nada para devolver` → No B, q continua com o endereço antigo, e o segundo free devolve de novo o mesmo bloco. No A, q vale NULL, e free(NULL) não faz nada.
- respondeu `Os dois` → No B o mesmo bloco é devolvido duas vezes, e isso é inválido. Só o A é válido: o segundo free recebe NULL.
- qualquer outro erro → free(NULL) não faz nada. No A o segundo free recebe NULL, e o trecho é válido.

### Degrau 3 — guiado, escolher

> Com p pendente, o padrão do C não garante nem copiar nem comparar o valor dele: as comparações que você viu aqui valem nesta máquina.
> Ler p, para copiar ou comparar, já é usar o valor dele.

**Versão 1.** Depois do free(p);, qual destas linhas é segura?

Opções: `p = NULL;`  `q = p;`  `*p = 0;`

Resposta certa: `p = NULL;`

Se errar:

- respondeu `q = p;` → Copiar p é ler um endereço que não vale mais, e o padrão do C não garante o que acontece. Seguro é dar a p um valor novo: p = NULL;
- respondeu `*p = 0;` → *p = 0; escreve num bloco que já foi devolvido, e pode ser de outro pedido. Seguro é dar a p um valor novo: p = NULL;
- qualquer outro erro → Com p pendente, o seguro é dar a ele um valor novo: p = NULL;

**Versão 2.** Depois do free(q);, qual destas linhas é segura?

Opções: `*q = 0;`  `q = malloc(sizeof(int));`  `p = q;`

Resposta certa: `q = malloc(sizeof(int));`

Se errar:

- respondeu `p = q;` → Copiar q é ler um endereço que não vale mais, e o padrão do C não garante o que acontece. Seguro é dar a q um valor novo, como o de outro bloco.
- respondeu `*q = 0;` → *q = 0; escreve num bloco que já foi devolvido, e pode ser de outro pedido. Seguro é dar a q um valor novo, como o de outro bloco.
- qualquer outro erro → Com q pendente, o seguro é dar a ele um valor novo: q = malloc(sizeof(int));

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Depois do free, só resta dar outro valor a p_

**Versão 1.** O trecho chama free duas vezes, com um p = NULL; no meio. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
free(p);
printf("%d\n", p == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → p recebeu NULL depois do primeiro free. O segundo recebeu NULL e não fez nada; p continua valendo NULL, e a pergunta dá 1.
- qualquer outro erro → O segundo free recebeu NULL e não fez nada. p vale NULL: 1.

**Versão 2.** O trecho chama free duas vezes, com um q = NULL; no meio. A última linha pergunta se q é diferente de NULL. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
free(q);
q = NULL;
free(q);
printf("%d\n", q != NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → q recebeu NULL depois do primeiro free. O segundo recebeu NULL e não fez nada; q continua valendo NULL, e não é diferente dele.
- qualquer outro erro → O segundo free recebeu NULL e não fez nada. q vale NULL: a resposta é 0.

### Degrau 5 — prática, escolher

**Versão 1.** Quantas das duas últimas linhas são inválidas?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
free(p);
free(p);
*p = 1;
```

Opções: `As duas`  `Uma: o segundo free é seguro`  `Uma: só o segundo free; a escrita ainda vale`

Resposta certa: `As duas`

Se errar:

- respondeu `Uma: o segundo free é seguro` → O segundo free devolve de novo um bloco que já não é seu, e isso é inválido. A escrita também: são as duas.
- respondeu `Uma: só o segundo free; a escrita ainda vale` → Depois do primeiro free o bloco não é mais seu: escrever nele é tão inválido quanto devolvê-lo de novo. São as duas.
- qualquer outro erro → Depois do primeiro free, p está pendente: devolver de novo e escrever são os dois inválidos.

**Versão 2.** Quantas das duas últimas linhas são inválidas?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
free(q);
printf("%d\n", *q);
free(q);
```

Opções: `Uma: só a leitura; o segundo free é seguro`  `Uma: só o segundo free; a leitura ainda vale`  `As duas`

Resposta certa: `As duas`

Se errar:

- respondeu `Uma: só a leitura; o segundo free é seguro` → O segundo free devolve de novo um bloco que já não é seu, e isso é inválido. A leitura também: são as duas.
- respondeu `Uma: só o segundo free; a leitura ainda vale` → Depois do primeiro free o bloco não é mais seu: ler dele é tão inválido quanto devolvê-lo de novo. São as duas.
- qualquer outro erro → Depois do primeiro free, q está pendente: ler e devolver de novo são os dois inválidos.

### Se errar a pergunta do topo: a revisão

> Depois do free, p guarda um endereço com cara de bom, de um lugar que já não é seu.
> Devolver de novo, ler, escrever, até copiar ou comparar: nada disso tem garantia. O seguro é dar a p um valor novo.

```c
int *p;

p = malloc(sizeof(int));
free(p);
p = NULL;
free(p);
printf("%d\n", p == NULL);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> Chamar free() duas vezes no mesmo ponteiro é seguro.

```c
int *p;

p = malloc(sizeof(int));
free(p);
free(p);
```

**O trecho chama free duas vezes, com o mesmo ponteiro. Seguindo o programa, o compilador reclama de alguma coisa?**

- Não: o segundo free não acha nada para devolver, e é seguro _(é o que a crença espera)_
- Sim: o mesmo bloco é devolvido duas vezes _(é o que a máquina faz)_

O compilador reclama:

```
double-'free' of 'p'
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer): "double-free" é "free duas vezes". O programa não é executado: devolver duas vezes não tem resultado definido._

O que isto mostra: O compilador reclama do segundo free: o bloco de p é devolvido duas vezes ("double-free"). Depois do primeiro, p continuou com o endereço antigo, e o segundo free devolve o que já não é seu.
