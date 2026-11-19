# A escada do kc_08 — Alocação dinâmica

Texto para leitura, gerado de `mvp/dominio/escada_kc08.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — malloc(n) pede emprestado um pedaço de memória com n BYTES. Quantos bytes cada elemento ocupa é conta sua.

### Degrau 1 — guiado, escolher

> O número entre os parênteses de malloc é um tamanho em bytes, e um byte é o espaço de uma caixa de char.
> malloc não sabe o que você vai guardar ali: nem olha o tipo do ponteiro.

**Versão 1.** O que a última linha pede ao sistema?

Já está escrito:

```c
int *p;

p = malloc(10);
```

Opções: `Um bloco de dez bytes`  `Lugar para dez ints: malloc conta elementos do tipo de p`  `Dez ints, já com zero`

Resposta certa: `Um bloco de dez bytes`

Se errar:

- respondeu `Lugar para dez ints: malloc conta elementos do tipo de p` → malloc não olha o tipo de p, e não conta ints: o número dele é um tamanho em bytes. malloc(10) pede dez bytes. _(aponta a crença `malloc_conta_elementos`)_
- respondeu `Dez ints, já com zero` → malloc não conta ints nem escreve zero em nada: o número dele é um tamanho em bytes. malloc(10) pede dez bytes.
- qualquer outro erro → O número de malloc é um tamanho em bytes: dez bytes.

**Versão 2.** O que a última linha pede ao sistema?

Já está escrito:

```c
int *q;

q = malloc(6);
```

Opções: `Lugar para seis ints: malloc conta elementos do tipo de q`  `Seis ints, já com zero`  `Um bloco de seis bytes`

Resposta certa: `Um bloco de seis bytes`

Se errar:

- respondeu `Lugar para seis ints: malloc conta elementos do tipo de q` → malloc não olha o tipo de q, e não conta ints: o número dele é um tamanho em bytes. malloc(6) pede seis bytes. _(aponta a crença `malloc_conta_elementos`)_
- respondeu `Seis ints, já com zero` → malloc não conta ints nem escreve zero em nada: o número dele é um tamanho em bytes. malloc(6) pede seis bytes.
- qualquer outro erro → O número de malloc é um tamanho em bytes: seis bytes.

### Degrau 2 — guiado, digitar

> Para vários ints, a conta dos bytes é sua: quantos, vezes o tamanho de um. O sinal de vezes é o *.
> malloc(3 * sizeof(int)) pede lugar para três ints: p[0], p[1] e p[2].

**Versão 1.** O bloco tem lugar para três ints. Que número aparece?

```c
int *p;

p = malloc(3 * sizeof(int));
p[0] = 7;
p[1] = 8;
p[2] = 9;
printf("%d\n", p[2]);
free(p);
```

Resposta certa: `9`

Se errar:

- digitou `7` → 7 foi para p[0], a primeira posição do bloco. O printf mostra p[2], a terceira: 9.
- digitou `3` → 3 é quantos ints cabem no bloco. O printf mostra o que está em p[2], a terceira posição: 9.
- qualquer outro erro → O bloco tem três posições, e p[2] é a terceira: 9.

**Versão 2.** O bloco tem lugar para dois ints. Que número aparece?

```c
int *q;

q = malloc(2 * sizeof(int));
q[0] = 15;
q[1] = 16;
printf("%d\n", q[1]);
free(q);
```

Resposta certa: `16`

Se errar:

- digitou `15` → 15 foi para q[0], a primeira posição do bloco. O printf mostra q[1], a segunda: 16.
- digitou `2` → 2 é quantos ints cabem no bloco. O printf mostra o que está em q[1], a segunda posição: 16.
- qualquer outro erro → O bloco tem duas posições, e q[1] é a segunda: 16.

### Degrau 3 — guiado, escolher

> malloc não faz a conta por você: quem multiplica é quem pede.

**Versão 1.** Qual destas linhas pede lugar para cinco ints?

Já está escrito:

```c
int *p;
```

Opções: `p = malloc(5 * sizeof(int));`  `p = malloc(5);`  `p = malloc(sizeof(int));`

Resposta certa: `p = malloc(5 * sizeof(int));`

Se errar:

- respondeu `p = malloc(5);` → malloc(5) pede cinco bytes, e um int ocupa mais que um. Para cinco ints, a conta é 5 * sizeof(int).
- respondeu `p = malloc(sizeof(int));` → sizeof(int) é o tamanho de um int só. Para cinco, multiplica-se: 5 * sizeof(int).
- qualquer outro erro → Cinco vezes o tamanho de um int: p = malloc(5 * sizeof(int));

**Versão 2.** Qual destas linhas pede lugar para oito ints?

Já está escrito:

```c
int *q;
```

Opções: `q = malloc(sizeof(int));`  `q = malloc(8 * sizeof(int));`  `q = malloc(8);`

Resposta certa: `q = malloc(8 * sizeof(int));`

Se errar:

- respondeu `q = malloc(8);` → malloc(8) pede oito bytes, e um int ocupa mais que um. Para oito ints, a conta é 8 * sizeof(int).
- respondeu `q = malloc(sizeof(int));` → sizeof(int) é o tamanho de um int só. Para oito, multiplica-se: 8 * sizeof(int).
- qualquer outro erro → Oito vezes o tamanho de um int: q = malloc(8 * sizeof(int));

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: malloc conta bytes: a multiplicação é sua_

**Versão 1.** A última linha quer lugar para três ints. Qual é o problema dela?

Já está escrito:

```c
int *p;

p = malloc(3);
```

Opções: `Pede 3 bytes, e três ints ocupam mais que isso`  `Nenhum: malloc(3) reserva três ints`  `Falta o tipo: tinha de ser malloc(int, 3)`

Resposta certa: `Pede 3 bytes, e três ints ocupam mais que isso`

Se errar:

- respondeu `Nenhum: malloc(3) reserva três ints` → malloc conta bytes, e não ints: malloc(3) entrega três bytes. Para três ints, a conta é 3 * sizeof(int).
- respondeu `Falta o tipo: tinha de ser malloc(int, 3)` → malloc recebe um número só, o tamanho em bytes. Quem põe o tipo na conta é você: 3 * sizeof(int).
- qualquer outro erro → malloc(3) pede três bytes. Para três ints: malloc(3 * sizeof(int)).

**Versão 2.** A última linha quer lugar para seis ints. Qual é o problema dela?

Já está escrito:

```c
int *q;

q = malloc(6);
```

Opções: `Falta o tipo: tinha de ser malloc(int, 6)`  `Pede 6 bytes, e seis ints ocupam mais que isso`  `Nenhum: malloc(6) reserva seis ints`

Resposta certa: `Pede 6 bytes, e seis ints ocupam mais que isso`

Se errar:

- respondeu `Nenhum: malloc(6) reserva seis ints` → malloc conta bytes, e não ints: malloc(6) entrega seis bytes. Para seis ints, a conta é 6 * sizeof(int).
- respondeu `Falta o tipo: tinha de ser malloc(int, 6)` → malloc recebe um número só, o tamanho em bytes. Quem põe o tipo na conta é você: 6 * sizeof(int).
- qualquer outro erro → malloc(6) pede seis bytes. Para seis ints: malloc(6 * sizeof(int)).

### Degrau 5 — prática, digitar

**Versão 1.** O bloco tem lugar para dois ints. Que número aparece?

```c
int *p;

p = malloc(2 * sizeof(int));
p[0] = 15;
p[1] = p[0] + 1;
printf("%d\n", p[1]);
free(p);
```

Resposta certa: `16`

Se errar:

- digitou `15` → 15 está em p[0]. p[1], a segunda posição, recebeu p[0] + 1: 16.
- qualquer outro erro → p[1] recebeu o valor de p[0] mais 1: 16.

**Versão 2.** O bloco tem lugar para dois ints. Que número aparece?

```c
int *q;

q = malloc(2 * sizeof(int));
q[0] = 7;
q[1] = q[0] + 2;
printf("%d\n", q[1]);
free(q);
```

Resposta certa: `9`

Se errar:

- digitou `7` → 7 está em q[0]. q[1], a segunda posição, recebeu q[0] + 2: 9.
- qualquer outro erro → q[1] recebeu o valor de q[0] mais 2: 9.

### Se errar a pergunta do topo: a revisão

> O número de malloc é um tamanho em bytes, e um byte é o espaço de uma caixa de char.
> Para três ints a conta é sua: malloc(3 * sizeof(int)).

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

> malloc(n) reserva n elementos do tipo, e não n bytes.

```c
int *p;
int *q;

p = malloc(5 * sizeof(int));
q = malloc(5);
free(p);
free(q);
```

**As duas linhas querem lugar para ints. Uma faz a conta dos bytes, a outra pede só 5. Seguindo o programa, de qual delas o compilador reclama?**

- De nenhuma: malloc(5) já reserva cinco ints _(é o que a crença espera)_
- Da segunda: 5 bytes não é tamanho de int nenhum _(é o que a máquina faz)_

O compilador reclama:

```
allocated buffer size is not a multiple of the pointee's size
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer). Ela diz que o tamanho pedido não é múltiplo do tamanho do que o ponteiro aponta: nesta máquina um int ocupa 4 bytes, e 5 não dá um número inteiro de ints. O programa não é executado._

O que isto mostra: O compilador aceita malloc(5 * sizeof(int)) e reclama de malloc(5): cinco bytes não formam um número inteiro de ints. malloc conta bytes; quem conta os ints é a multiplicação.

## B2 — Ele devolve o endereço do pedaço que arrumou — ou NULL, se não conseguiu arrumar.

### Degrau 1 — guiado, escolher

> malloc não entrega o bloco em si: devolve o endereço dele.
> Se não conseguir bloco nenhum, devolve NULL.

**Versão 1.** Depois da última linha, o que fica guardado em p?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
```

Opções: `O endereço do bloco, ou NULL`  `O próprio bloco: o que malloc devolve é o dado`  `O valor que estava no bloco`

Resposta certa: `O endereço do bloco, ou NULL`

Se errar:

- respondeu `O próprio bloco: o que malloc devolve é o dado` → O bloco fica no monte, e não cabe em p. O que malloc devolve, e p guarda, é o endereço do bloco — ou NULL. _(aponta a crença `pointer_is_data`)_
- respondeu `O valor que estava no bloco` → O valor do bloco se lê com *p. Em p fica o endereço que malloc devolveu, ou NULL.
- qualquer outro erro → p guarda o endereço do bloco, ou NULL se malloc não conseguiu.

**Versão 2.** Depois da última linha, o que fica guardado em q?

Já está escrito:

```c
int *q;

q = malloc(2 * sizeof(int));
```

Opções: `O valor que estava no bloco`  `O endereço do bloco, ou NULL`  `O próprio bloco: o que malloc devolve é o dado`

Resposta certa: `O endereço do bloco, ou NULL`

Se errar:

- respondeu `O próprio bloco: o que malloc devolve é o dado` → O bloco fica no monte, e não cabe em q. O que malloc devolve, e q guarda, é o endereço do bloco — ou NULL. _(aponta a crença `pointer_is_data`)_
- respondeu `O valor que estava no bloco` → O valor do bloco se lê com q[0] ou *q. Em q fica o endereço que malloc devolveu, ou NULL.
- qualquer outro erro → q guarda o endereço do bloco, ou NULL se malloc não conseguiu.

### Degrau 2 — guiado, completar

> O endereço que malloc devolve se guarda num ponteiro, como todo endereço.
> *p é o que está NO bloco, e só serve depois de p ter o endereço.

**Versão 1.** Complete com quem recebe o que malloc devolve.

Já está escrito:

```c
int *p;
```

```c
___ = malloc(sizeof(int));
```

Peças: `p`  `*p`  `&p`

Resposta certa: `p = malloc(sizeof(int));`

Se errar:

- respondeu `*p = malloc(sizeof(int));` → *p é lugar de int, e malloc devolve um endereço: o compilador reclama. Quem guarda endereço é o ponteiro: p = malloc(sizeof(int));
- respondeu `&p = malloc(sizeof(int));` → &p é o endereço de p, e não um lugar que recebe valor: o compilador reclama. Quem recebe é o ponteiro: p = malloc(sizeof(int));
- qualquer outro erro → malloc devolve um endereço, e quem guarda endereço é o ponteiro: p = malloc(sizeof(int));

**Versão 2.** Complete com quem recebe o que malloc devolve.

Já está escrito:

```c
int *q;
```

```c
___ = malloc(sizeof(int));
```

Peças: `&q`  `q`  `*q`

Resposta certa: `q = malloc(sizeof(int));`

Se errar:

- respondeu `*q = malloc(sizeof(int));` → *q é lugar de int, e malloc devolve um endereço: o compilador reclama. Quem guarda endereço é o ponteiro: q = malloc(sizeof(int));
- respondeu `&q = malloc(sizeof(int));` → &q é o endereço de q, e não um lugar que recebe valor: o compilador reclama. Quem recebe é o ponteiro: q = malloc(sizeof(int));
- qualquer outro erro → malloc devolve um endereço, e quem guarda endereço é o ponteiro: q = malloc(sizeof(int));

### Degrau 3 — guiado, digitar

> p guarda um endereço, e não o bloco.
> Copiar p para q copia o endereço: os dois passam a apontar para o mesmo bloco.

**Versão 1.** O trecho escreve por q e lê por p. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
*q = 7;
printf("%d\n", *p);
free(p);
```

Resposta certa: `7`

Se errar:

- digitou `0` → q = p; copiou o endereço, e não o bloco: há um bloco só. O 7 escrito por q é o que *p encontra.
- qualquer outro erro → p e q guardam o mesmo endereço: o 7 escrito por q está no bloco que p lê.

**Versão 2.** O trecho escreve por p e lê por q. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
*p = 15;
printf("%d\n", *q);
free(q);
```

Resposta certa: `15`

Se errar:

- digitou `0` → q = p; copiou o endereço, e não o bloco: há um bloco só. O 15 escrito por p é o que *q encontra.
- qualquer outro erro → p e q guardam o mesmo endereço: o 15 escrito por p está no bloco que q lê.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O ponteiro guarda o endereço, e não o bloco_

**Versão 1.** q recebe o que está em p, e soma 1 no bloco. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
*p = 7;
q = p;
*q = *q + 1;
printf("%d\n", *p);
free(p);
```

Resposta certa: `8`

Se errar:

- digitou `7` → q recebeu o endereço que estava em p: os dois apontam para o mesmo bloco. O 1 somado por q está no bloco que p lê.
- qualquer outro erro → Há um bloco só, com dois ponteiros. O 7 virou 8 por q, e é 8 que p lê.

**Versão 2.** q recebe o que está em p, e soma 5 no bloco. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
*p = 15;
q = p;
*q = *q + 5;
printf("%d\n", *p);
free(p);
```

Resposta certa: `20`

Se errar:

- digitou `15` → q recebeu o endereço que estava em p: os dois apontam para o mesmo bloco. O 5 somado por q está no bloco que p lê.
- qualquer outro erro → Há um bloco só, com dois ponteiros. O 15 virou 20 por q, e é 20 que p lê.

### Degrau 5 — prática, escolher

**Versão 1.** No fim deste trecho, quantos blocos existem?

Já está escrito:

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
```

Opções: `Um: p e q guardam o mesmo endereço`  `Dois: q = p; copiou o bloco`  `Nenhum: bloco só existe depois de escrever nele`

Resposta certa: `Um: p e q guardam o mesmo endereço`

Se errar:

- respondeu `Dois: q = p; copiou o bloco` → q = p; copia o que está em p, que é um endereço. O bloco não é copiado: continua sendo um só, com dois ponteiros.
- respondeu `Nenhum: bloco só existe depois de escrever nele` → O bloco existe desde que malloc o entregou, com ou sem valor escrito. É um só, e os dois ponteiros apontam para ele.
- qualquer outro erro → Um bloco só: foi um malloc só. p e q guardam o mesmo endereço.

**Versão 2.** No fim deste trecho, quantos blocos existem?

Já está escrito:

```c
int *a;
int *b;
int *c;

a = malloc(sizeof(int));
b = malloc(sizeof(int));
c = a;
```

Opções: `Três: cada ponteiro tem o seu`  `Dois: foram dois malloc; c guarda o endereço que está em a`  `Um: os três apontam para o mesmo`

Resposta certa: `Dois: foram dois malloc; c guarda o endereço que está em a`

Se errar:

- respondeu `Três: cada ponteiro tem o seu` → c = a; copia um endereço, e não cria bloco. Bloco só nasce de malloc, e foram dois.
- respondeu `Um: os três apontam para o mesmo` → a e b receberam, cada um, o bloco do seu malloc: são dois blocos. Só c repete um endereço, o de a.
- qualquer outro erro → Bloco nasce de malloc, e foram dois. c só guarda o endereço que está em a.

### Se errar a pergunta do topo: a revisão

> malloc devolve o endereço do bloco que conseguiu, ou NULL se não conseguiu.
> O endereço se guarda no ponteiro: p = malloc(...). O bloco é outra coisa, e chega-se nele com *p.

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro é o próprio dado: o que malloc devolve é o bloco, não o endereço.

```c
int *p;
int *q;

p = malloc(sizeof(int));
*p = 1;
q = p;
*q = 5;
printf("%d\n", *p);
free(p);
```

**q = p; copia o que está guardado em p. Depois o trecho escreve 5 por q, e mostra o que p alcança. O que aparece?**

- 1: q ficou com uma cópia do dado, e o de p não mudou _(é o que a crença espera)_
- 5 _(é o que a máquina faz)_

A máquina imprime:

```
5
```

O que isto mostra: Saiu 5. q = p; copiou um endereço, e não o dado: os dois ponteiros apontam para o mesmo bloco, e o que q escreveu é o que p lê. O ponteiro guarda ONDE o dado está; o dado fica no bloco.

## B3 — O que está dentro desse pedaço é sobra: ninguém limpou antes de entregar. É preciso escrever ali antes de ler.

### Degrau 1 — guiado, escolher

> malloc entrega o bloco do jeito que estava: não limpa nada antes.
> É como declarar uma variável e não dar valor a ela.

**Versão 1.** Logo depois da última linha, o que há dentro do bloco?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
```

Opções: `Sobra: um valor que ninguém escolheu`  `Zero: malloc limpa o bloco antes de entregar`  `Nada: o bloco está vazio`

Resposta certa: `Sobra: um valor que ninguém escolheu`

Se errar:

- respondeu `Zero: malloc limpa o bloco antes de entregar` → malloc só arruma o lugar: não escreve nada nele. O que está no bloco é o que já estava naquela memória — sobra. _(aponta a crença `malloc_initializes_zero`)_
- respondeu `Nada: o bloco está vazio` → Memória não fica vazia: sempre há algum valor ali. No bloco recém-entregue é sobra, um valor que ninguém escolheu.
- qualquer outro erro → malloc não limpa o bloco: o que há nele é sobra.

**Versão 2.** Logo depois da última linha, o que há dentro do bloco?

Já está escrito:

```c
int *q;

q = malloc(2 * sizeof(int));
```

Opções: `Zero: malloc limpa o bloco antes de entregar`  `Nada: o bloco está vazio`  `Sobra: valores que ninguém escolheu`

Resposta certa: `Sobra: valores que ninguém escolheu`

Se errar:

- respondeu `Zero: malloc limpa o bloco antes de entregar` → malloc só arruma o lugar: não escreve nada nele. O que está no bloco é o que já estava naquela memória — sobra. _(aponta a crença `malloc_initializes_zero`)_
- respondeu `Nada: o bloco está vazio` → Memória não fica vazia: sempre há algum valor ali. No bloco recém-entregue é sobra, valores que ninguém escolheu.
- qualquer outro erro → malloc não limpa o bloco: o que há nele é sobra.

### Degrau 2 — guiado, digitar

> Por isso se escreve antes de ler. Para somar no bloco, ele começa de um valor seu: *p = 0;

**Versão 1.** O bloco recebe 0 e depois a soma. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
*p = 0;
*p = *p + 5;
printf("%d\n", *p);
free(p);
```

Resposta certa: `5`

Se errar:

- digitou `0` → O bloco começou em 0 porque a linha *p = 0; escreveu. Depois recebeu mais 5: aparece 5.
- qualquer outro erro → O bloco recebeu 0, e depois 0 mais 5: 5.

**Versão 2.** O bloco recebe 10 e depois a soma. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
*q = 10;
*q = *q + 5;
printf("%d\n", *q);
free(q);
```

Resposta certa: `15`

Se errar:

- digitou `10` → O bloco começou em 10 porque a linha *q = 10; escreveu. Depois recebeu mais 5: aparece 15.
- qualquer outro erro → O bloco recebeu 10, e depois 10 mais 5: 15.

### Degrau 3 — guiado, escolher

> Cada posição do bloco é sobra até receber valor: escrever numa não arruma as outras.
> Quem quer tudo em zero escreve o zero, ou pede com calloc(2, sizeof(int)), que entrega as duas posições zeradas.

**Versão 1.** Em qual linha este trecho lê um valor que ninguém escolheu?

Já está escrito:

```c
int *p;

p = malloc(2 * sizeof(int));
p[0] = 7;
printf("%d\n", p[0]);
printf("%d\n", p[1]);
```

Opções: `Na última: p[1] nunca recebeu valor`  `Em nenhuma: o que não foi escrito vale zero`  `Nas duas: o bloco inteiro é sobra`

Resposta certa: `Na última: p[1] nunca recebeu valor`

Se errar:

- respondeu `Em nenhuma: o que não foi escrito vale zero` → malloc não escreve zero em nada. p[1] nunca recebeu valor: o que a última linha lê é sobra.
- respondeu `Nas duas: o bloco inteiro é sobra` → p[0] deixou de ser sobra quando recebeu 7. Quem continua sem valor é p[1], lido na última linha.
- qualquer outro erro → p[0] recebeu 7; p[1] não recebeu nada. A última linha lê sobra.

**Versão 2.** Em qual linha este trecho lê um valor que ninguém escolheu?

Já está escrito:

```c
int *q;

q = malloc(2 * sizeof(int));
q[1] = 9;
printf("%d\n", q[0]);
printf("%d\n", q[1]);
```

Opções: `Em nenhuma: o que não foi escrito vale zero`  `Na primeira das duas: q[0] nunca recebeu valor`  `Nas duas: o bloco inteiro é sobra`

Resposta certa: `Na primeira das duas: q[0] nunca recebeu valor`

Se errar:

- respondeu `Em nenhuma: o que não foi escrito vale zero` → malloc não escreve zero em nada. q[0] nunca recebeu valor: o que a primeira das duas linhas lê é sobra.
- respondeu `Nas duas: o bloco inteiro é sobra` → q[1] deixou de ser sobra quando recebeu 9. Quem continua sem valor é q[0], lido na primeira das duas linhas.
- qualquer outro erro → q[1] recebeu 9; q[0] não recebeu nada. A linha que lê q[0] lê sobra.

### Degrau 4 — prática, completar

_Nome do passo, no fechamento: Escrever no bloco antes de ler_

**Versão 1.** A linha seguinte vai ser *soma = *soma + 5;. Complete com o que tem de vir antes dela.

Já está escrito:

```c
int *soma;

soma = malloc(sizeof(int));
```

```c
___;
```

Peças: `*soma = 0`  `soma = 0`  `free(soma)`

Resposta certa: `*soma = 0;`

Se errar:

- respondeu `soma = 0;` → soma = 0; apaga o endereço: o ponteiro vira nulo, e o bloco se perde. Quem precisa de um valor é o bloco: *soma = 0;
- respondeu `free(soma);` → free devolve o bloco, e depois dele o bloco não é mais seu. O que falta é dar um valor ao bloco: *soma = 0;
- qualquer outro erro → A soma lê o bloco, e o bloco chega com sobra. Antes vem um valor seu: *soma = 0;

**Versão 2.** A linha seguinte vai ser *total = *total + 1;. Complete com o que tem de vir antes dela.

Já está escrito:

```c
int *total;

total = malloc(sizeof(int));
```

```c
___;
```

Peças: `free(total)`  `*total = 0`  `total = 0`

Resposta certa: `*total = 0;`

Se errar:

- respondeu `total = 0;` → total = 0; apaga o endereço: o ponteiro vira nulo, e o bloco se perde. Quem precisa de um valor é o bloco: *total = 0;
- respondeu `free(total);` → free devolve o bloco, e depois dele o bloco não é mais seu. O que falta é dar um valor ao bloco: *total = 0;
- qualquer outro erro → A soma lê o bloco, e o bloco chega com sobra. Antes vem um valor seu: *total = 0;

### Degrau 5 — prática, digitar

**Versão 1.** As duas posições recebem valor antes de serem lidas. Que número aparece?

```c
int *p;

p = malloc(2 * sizeof(int));
p[0] = 7;
p[1] = p[0];
p[0] = 0;
printf("%d\n", p[1]);
free(p);
```

Resposta certa: `7`

Se errar:

- digitou `0` → p[1] recebeu o 7 antes de p[0] virar 0, e ficou com ele. São duas posições, cada uma com o seu valor.
- qualquer outro erro → p[1] recebeu 7 de p[0]. Depois só p[0] mudou: p[1] continua 7.

**Versão 2.** As duas posições recebem valor antes de serem lidas. Que número aparece?

```c
int *q;

q = malloc(2 * sizeof(int));
q[0] = 15;
q[1] = q[0];
q[0] = 1;
printf("%d\n", q[1]);
free(q);
```

Resposta certa: `15`

Se errar:

- digitou `1` → q[1] recebeu o 15 antes de q[0] virar 1, e ficou com ele. São duas posições, cada uma com o seu valor.
- qualquer outro erro → q[1] recebeu 15 de q[0]. Depois só q[0] mudou: q[1] continua 15.

### Se errar a pergunta do topo: a revisão

> O bloco chega como estava: malloc não limpa nada. O que há nele é sobra.
> Antes de ler, é preciso escrever: *p = 0;

```c
int *p;

p = malloc(sizeof(int));
*p = 0;
*p = *p + 5;
printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
5
```

### Se a pessoa disser a crença: a prova

Você disse:

> malloc inicializa a memória com zero.

```c
int *p;

p = malloc(sizeof(int));
printf("%d\n", *p);
free(p);
```

**O trecho pede um bloco e lê o que há nele, sem escrever antes. O compilador reclama de alguma coisa?**

- Não: malloc entrega o bloco zerado _(é o que a crença espera)_
- Sim: o bloco é lido sem ter recebido valor _(é o que a máquina faz)_

O compilador reclama:

```
'*p' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o que apareceria, ninguém sabe._

O que isto mostra: O compilador reclama: *p é lido sem ter recebido valor ("used uninitialized"). Se malloc zerasse o bloco, não haveria do que reclamar. O que há ali é sobra.

## I1 — A caixa do ponteiro e o pedaço emprestado são duas coisas diferentes, em áreas diferentes.

### Degrau 1 — guiado, escolher

> Variável local mora na pilha; bloco de malloc mora no monte.
> Apontar para um lugar não é morar nele.

**Versão 1.** Onde mora a variável p?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
```

Opções: `Na pilha: p é uma variável local`  `No monte: o ponteiro mora no monte porque aponta para lá`  `Dentro do bloco que ela aponta`

Resposta certa: `Na pilha: p é uma variável local`

Se errar:

- respondeu `No monte: o ponteiro mora no monte porque aponta para lá` → Apontar para o monte não leva ninguém para lá. p foi declarada como qualquer variável local, e fica na pilha; no monte está só o bloco. _(aponta a crença `pointer_lives_in_heap`)_
- respondeu `Dentro do bloco que ela aponta` → O bloco guarda o int. p é outra coisa: uma variável local, na pilha, que guarda o endereço do bloco.
- qualquer outro erro → p é uma variável local, na pilha. No monte está o bloco.

**Versão 2.** Onde mora a variável q?

Já está escrito:

```c
int *q;

q = malloc(2 * sizeof(int));
```

Opções: `Dentro do bloco que ela aponta`  `Na pilha: q é uma variável local`  `No monte: o ponteiro mora no monte porque aponta para lá`

Resposta certa: `Na pilha: q é uma variável local`

Se errar:

- respondeu `No monte: o ponteiro mora no monte porque aponta para lá` → Apontar para o monte não leva ninguém para lá. q foi declarada como qualquer variável local, e fica na pilha; no monte está só o bloco. _(aponta a crença `pointer_lives_in_heap`)_
- respondeu `Dentro do bloco que ela aponta` → O bloco guarda os ints. q é outra coisa: uma variável local, na pilha, que guarda o endereço do bloco.
- qualquer outro erro → q é uma variável local, na pilha. No monte está o bloco.

### Degrau 2 — guiado, escolher

> Quando a função termina, as variáveis locais dela acabam, ponteiro ou não.
> O bloco do malloc fica no monte — e, se só uma variável local tinha o endereço, ninguém mais chega nele.

**Versão 1.** A função termina sem chamar free. O que sobrou, e o que se perdeu?

Já está escrito:

```c
void usa(void) { int *p = malloc(sizeof(int)); *p = 7; }
```

Opções: `O bloco ficou; p, que guardava o endereço, acabou`  `Nada ficou: p levou o bloco junto`  `Ficaram os dois`

Resposta certa: `O bloco ficou; p, que guardava o endereço, acabou`

Se errar:

- respondeu `Nada ficou: p levou o bloco junto` → p e o bloco são duas coisas, em duas áreas. p, na pilha, acabou com a função; o bloco, no monte, continua — sem ninguém que saiba o endereço.
- respondeu `Ficaram os dois` → p é variável local, e acaba quando a função termina. Só o bloco, que está no monte, continua.
- qualquer outro erro → p acabou com a função. O bloco continua no monte, e o endereço dele se perdeu.

**Versão 2.** A função termina sem chamar free. O que sobrou, e o que se perdeu?

Já está escrito:

```c
void anota(void) { int *q = malloc(sizeof(int)); *q = 9; }
```

Opções: `Ficaram os dois`  `Nada ficou: q levou o bloco junto`  `O bloco ficou; q, que guardava o endereço, acabou`

Resposta certa: `O bloco ficou; q, que guardava o endereço, acabou`

Se errar:

- respondeu `Nada ficou: q levou o bloco junto` → q e o bloco são duas coisas, em duas áreas. q, na pilha, acabou com a função; o bloco, no monte, continua — sem ninguém que saiba o endereço.
- respondeu `Ficaram os dois` → q é variável local, e acaba quando a função termina. Só o bloco, que está no monte, continua.
- qualquer outro erro → q acabou com a função. O bloco continua no monte, e o endereço dele se perdeu.

### Degrau 3 — guiado, digitar

> A caixa de p pode trocar de endereço quando você quiser.
> O bloco que ela apontava continua no monte, à espera do free.

**Versão 1.** p passa a guardar o endereço que está em q. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = malloc(sizeof(int));
*p = 7;
*q = 9;
free(p);
p = q;
printf("%d\n", *p);
free(q);
```

Resposta certa: `9`

Se errar:

- digitou `7` → O 7 ficou no primeiro bloco, que foi devolvido. A caixa de p trocou de endereço: agora guarda o de q, e *p acha 9.
- qualquer outro erro → p trocou de endereço: aponta agora para o bloco de q, que guarda 9.

**Versão 2.** q passa a guardar o endereço que está em p. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = malloc(sizeof(int));
*p = 15;
*q = 20;
free(q);
q = p;
printf("%d\n", *q);
free(p);
```

Resposta certa: `15`

Se errar:

- digitou `20` → O 20 ficou no segundo bloco, que foi devolvido. A caixa de q trocou de endereço: agora guarda o de p, e *q acha 15.
- qualquer outro erro → q trocou de endereço: aponta agora para o bloco de p, que guarda 15.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A caixa do ponteiro e o bloco são duas coisas_

**Versão 1.** O trecho apaga p, e depois lê o bloco por q. Que número aparece?

```c
int *p;
int *q;

p = malloc(sizeof(int));
*p = 7;
q = p;
p = NULL;
printf("%d\n", *q);
free(q);
```

Resposta certa: `7`

Se errar:

- digitou `0` → p = NULL; mudou a caixa de p, e não o bloco. O bloco continua no monte, com o 7, e q ainda guarda o endereço dele.
- qualquer outro erro → Apagar p não apaga o bloco: q ainda guarda o endereço, e lê 7.

**Versão 2.** O trecho apaga q, e depois lê o bloco por p. Que número aparece?

```c
int *p;
int *q;

q = malloc(sizeof(int));
*q = 15;
p = q;
q = NULL;
printf("%d\n", *p);
free(p);
```

Resposta certa: `15`

Se errar:

- digitou `0` → q = NULL; mudou a caixa de q, e não o bloco. O bloco continua no monte, com o 15, e p ainda guarda o endereço dele.
- qualquer outro erro → Apagar q não apaga o bloco: p ainda guarda o endereço, e lê 15.

### Degrau 5 — prática, escolher

**Versão 1.** No fim deste trecho, quantas caixas de ponteiro e quantos blocos existem?

Já está escrito:

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = p;
```

Opções: `Duas caixas, na pilha, e um bloco, no monte`  `Duas caixas e dois blocos`  `Uma coisa só: p, q e o bloco são o mesmo`

Resposta certa: `Duas caixas, na pilha, e um bloco, no monte`

Se errar:

- respondeu `Duas caixas e dois blocos` → Bloco só nasce de malloc, e houve um. q = p; copiou o endereço para a caixa de q: duas caixas, um bloco.
- respondeu `Uma coisa só: p, q e o bloco são o mesmo` → p e q são duas variáveis, cada uma com a sua caixa, na pilha. O bloco é outra coisa, no monte. Três coisas ao todo.
- qualquer outro erro → p e q são duas caixas, na pilha. O bloco é um, no monte.

**Versão 2.** No fim deste trecho, quantas caixas de ponteiro e quantos blocos existem?

Já está escrito:

```c
int *a;
int *b;

a = malloc(sizeof(int));
b = malloc(sizeof(int));
```

Opções: `Duas coisas só: cada ponteiro é o seu bloco`  `Duas caixas, na pilha, e um bloco, no monte`  `Duas caixas, na pilha, e dois blocos, no monte`

Resposta certa: `Duas caixas, na pilha, e dois blocos, no monte`

Se errar:

- respondeu `Duas coisas só: cada ponteiro é o seu bloco` → O ponteiro não é o bloco: é uma caixa, na pilha, com o endereço do bloco. São duas caixas e dois blocos.
- respondeu `Duas caixas, na pilha, e um bloco, no monte` → Cada malloc entregou um bloco, e foram dois. São duas caixas, na pilha, e dois blocos, no monte.
- qualquer outro erro → a e b são duas caixas, na pilha. Cada malloc entregou um bloco: dois, no monte.

### Se errar a pergunta do topo: a revisão

> São duas coisas: a caixa de p, uma variável local, na pilha; e o bloco, no monte.
> p aponta para o monte, mas não mora lá.

```c
int *p;
int *q;

p = malloc(sizeof(int));
*p = 7;
q = p;
p = NULL;
printf("%d\n", *q);
free(q);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro mora no heap porque aponta para lá.

```c
int *p;

p = malloc(sizeof(int));
free(p);
free(&p);
```

**free devolve o que foi pedido com malloc. O trecho chama free para o bloco, e depois para a própria variável p. De qual das duas o compilador reclama?**

- Da última: p não é do monte _(é o que a máquina faz)_
- De nenhuma: p mora no monte, junto com o bloco _(é o que a crença espera)_

O compilador reclama:

```
'free' called on unallocated object 'p'
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: devolver o que não foi pedido não tem resultado definido._

O que isto mostra: O compilador aceita free(p); e reclama de free(&p);: a variável p não foi pedida com malloc ("unallocated object"). Ela é uma variável local, na pilha. No monte está o bloco que ela apontava.

## I2 — Como NULL é uma das respostas possíveis, é preciso conferir antes de usar o que veio.

### Degrau 1 — guiado, escolher

> malloc pode não conseguir o bloco. Quando não consegue, devolve NULL.
> Por isso o que ele devolve é conferido antes de qualquer uso.

**Versão 1.** O que pode estar guardado em p depois da última linha?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
```

Opções: `O endereço de um bloco, ou NULL`  `Sempre o endereço de um bloco: malloc sempre funciona, e conferir é desnecessário`  `Sempre NULL, até a primeira escrita`

Resposta certa: `O endereço de um bloco, ou NULL`

Se errar:

- respondeu `Sempre o endereço de um bloco: malloc sempre funciona, e conferir é desnecessário` → malloc pede memória ao sistema, e o sistema pode não ter. Quando não tem, a resposta é NULL — e é por isso que se confere. _(aponta a crença `malloc_always_succeeds`)_
- respondeu `Sempre NULL, até a primeira escrita` → Quando malloc consegue, p já recebe o endereço do bloco, sem esperar escrita nenhuma. NULL é a resposta de quando ele não consegue.
- qualquer outro erro → malloc devolve o endereço de um bloco, ou NULL quando não consegue.

**Versão 2.** O que pode estar guardado em q depois da última linha?

Já está escrito:

```c
int *q;

q = malloc(3 * sizeof(int));
```

Opções: `Sempre NULL, até a primeira escrita`  `O endereço de um bloco, ou NULL`  `Sempre o endereço de um bloco: malloc sempre funciona, e conferir é desnecessário`

Resposta certa: `O endereço de um bloco, ou NULL`

Se errar:

- respondeu `Sempre o endereço de um bloco: malloc sempre funciona, e conferir é desnecessário` → malloc pede memória ao sistema, e o sistema pode não ter. Quando não tem, a resposta é NULL — e é por isso que se confere. _(aponta a crença `malloc_always_succeeds`)_
- respondeu `Sempre NULL, até a primeira escrita` → Quando malloc consegue, q já recebe o endereço do bloco, sem esperar escrita nenhuma. NULL é a resposta de quando ele não consegue.
- qualquer outro erro → malloc devolve o endereço de um bloco, ou NULL quando não consegue.

### Degrau 2 — guiado, completar

> Conferir é perguntar, antes de usar, se o ponteiro não é NULL.

**Versão 1.** Complete a pergunta para a escrita só acontecer quando o bloco existe.

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
```

```c
if (___) *p = 7;
```

Peças: `p != NULL`  `p == NULL`  `*p != 7`

Resposta certa: `if (p != NULL) *p = 7;`

Se errar:

- respondeu `if (p == NULL) *p = 7;` → Com p == NULL a escrita aconteceria justamente quando NÃO há bloco. Escreve-se quando p não é NULL: if (p != NULL) *p = 7;
- respondeu `if (*p != 7) *p = 7;` → *p já é ir ao bloco — e é isso que não se pode fazer sem saber se ele existe. A pergunta é sobre p: if (p != NULL) *p = 7;
- qualquer outro erro → A pergunta é se p não é NULL: if (p != NULL) *p = 7;

**Versão 2.** Complete a pergunta para a escrita só acontecer quando o bloco existe.

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
```

```c
if (___) *q = 9;
```

Peças: `q == NULL`  `*q != 9`  `q != NULL`

Resposta certa: `if (q != NULL) *q = 9;`

Se errar:

- respondeu `if (q == NULL) *q = 9;` → Com q == NULL a escrita aconteceria justamente quando NÃO há bloco. Escreve-se quando q não é NULL: if (q != NULL) *q = 9;
- respondeu `if (*q != 9) *q = 9;` → *q já é ir ao bloco — e é isso que não se pode fazer sem saber se ele existe. A pergunta é sobre q: if (q != NULL) *q = 9;
- qualquer outro erro → A pergunta é se q não é NULL: if (q != NULL) *q = 9;

### Degrau 3 — guiado, digitar

> Com a pergunta antes de cada uso, o trecho só toca no bloco quando ele existe.

**Versão 1.** Neste computador malloc consegue o bloco. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
if (p != NULL) *p = 7;
if (p != NULL) printf("%d\n", *p);
free(p);
```

Resposta certa: `7`

Se errar:

- digitou `0` → malloc conseguiu o bloco, então p não é NULL: as duas perguntas dão sim. O bloco recebe 7, e o 7 é mostrado.
- qualquer outro erro → p não é NULL: o bloco recebe 7, e o 7 aparece.

**Versão 2.** Neste computador malloc consegue o bloco. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
if (q != NULL) *q = 15;
if (q != NULL) printf("%d\n", *q);
free(q);
```

Resposta certa: `15`

Se errar:

- digitou `0` → malloc conseguiu o bloco, então q não é NULL: as duas perguntas dão sim. O bloco recebe 15, e o 15 é mostrado.
- qualquer outro erro → q não é NULL: o bloco recebe 15, e o 15 aparece.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Conferir o NULL antes de usar o bloco_

**Versão 1.** Qual dos dois trechos continua seguro se malloc não conseguir o bloco?

Já está escrito:

```c
/* A */  p = malloc(sizeof(int));  *p = 1;
/* B */  q = malloc(sizeof(int));  if (q != NULL) *q = 1;
```

Opções: `O B: ele confere antes de escrever`  `Os dois: malloc não falha`  `Os dois: escrever em NULL não faz mal`

Resposta certa: `O B: ele confere antes de escrever`

Se errar:

- respondeu `Os dois: malloc não falha` → malloc pode devolver NULL, quando o sistema não tem a memória. No A, a escrita iria para NULL; o B confere antes.
- respondeu `Os dois: escrever em NULL não faz mal` → Em NULL não mora bloco nenhum: escrever ali não é definido (kc_05). O B confere antes, e só escreve quando há bloco.
- qualquer outro erro → O B confere se q não é NULL antes de escrever. O A escreveria em NULL.

**Versão 2.** Qual dos dois trechos continua seguro se malloc não conseguir o bloco?

Já está escrito:

```c
/* A */  p = malloc(sizeof(int));  if (p != NULL) *p = 5;
/* B */  q = malloc(sizeof(int));  *q = 5;
```

Opções: `Os dois: escrever em NULL não faz mal`  `Os dois: malloc não falha`  `O A: ele confere antes de escrever`

Resposta certa: `O A: ele confere antes de escrever`

Se errar:

- respondeu `Os dois: malloc não falha` → malloc pode devolver NULL, quando o sistema não tem a memória. No B, a escrita iria para NULL; o A confere antes.
- respondeu `Os dois: escrever em NULL não faz mal` → Em NULL não mora bloco nenhum: escrever ali não é definido (kc_05). O A confere antes, e só escreve quando há bloco.
- qualquer outro erro → O A confere se p não é NULL antes de escrever. O B escreveria em NULL.

### Degrau 5 — prática, digitar

**Versão 1.** Neste computador malloc consegue o bloco. A última linha pergunta se p vale NULL. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
printf("%d\n", p == NULL);
free(p);
```

Resposta certa: `0`

Se errar:

- digitou `1` → malloc conseguiu o bloco, e p guarda o endereço dele: p não vale NULL. A pergunta é falsa, e a resposta é 0.
- qualquer outro erro → p guarda o endereço do bloco, e não NULL: a resposta é 0.

**Versão 2.** Neste computador malloc consegue o bloco. A última linha pergunta se q é diferente de NULL. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
printf("%d\n", q != NULL);
free(q);
```

Resposta certa: `1`

Se errar:

- digitou `0` → malloc conseguiu o bloco, e q guarda o endereço dele: q é diferente de NULL. A pergunta é verdadeira, e a resposta é 1.
- qualquer outro erro → q guarda o endereço do bloco, que é diferente de NULL: a resposta é 1.

### Se errar a pergunta do topo: a revisão

> malloc pode não conseguir o bloco, e aí devolve NULL.
> Por isso se confere antes de usar: if (p != NULL) *p = 7;

```c
int *p;

p = malloc(sizeof(int));
if (p != NULL) *p = 7;
if (p != NULL) printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Verificar NULL após malloc é desnecessário, porque malloc sempre funciona.

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = malloc(sizeof(int));
if (p != NULL) *p = 7;
*q = 7;
free(p);
free(q);
```

**Os dois ponteiros recebem um bloco. Antes de escrever, o trecho confere p, e não confere q. Seguindo o programa, de qual escrita o compilador reclama?**

- De nenhuma: malloc sempre devolve um bloco _(é o que a crença espera)_
- Da de q: ele pode ter vindo NULL _(é o que a máquina faz)_

O compilador reclama:

```
dereference of possibly-NULL 'q'
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer): "possibly-NULL" é "pode ser NULL". O programa não é executado._

O que isto mostra: O compilador reclama da escrita em q: malloc pode devolver NULL, e q foi usado sem conferir ("possibly-NULL"). Da escrita em p, conferida antes, ele não reclama.

## I3 — Esse pedaço não some quando a função que o pediu termina, e ninguém o devolve por você. Enquanto não devolver, ele continua ocupado.

### Degrau 1 — guiado, escolher

> O bloco não acaba com a função que o pediu, e ninguém o devolve por você.
> Enquanto não houver free, ele continua ocupado — mesmo sem ponteiro nenhum guardando o endereço.

**Versão 1.** A função é chamada três vezes. Quantos blocos continuam ocupados depois?

Já está escrito:

```c
void guarda(void) { int *p = malloc(sizeof(int)); *p = 7; }

guarda();
guarda();
guarda();
```

Opções: `Três: nenhum foi devolvido`  `Nenhum: o sistema devolve cada bloco quando a função termina`  `Um: cada chamada reusa o bloco da anterior`

Resposta certa: `Três: nenhum foi devolvido`

Se errar:

- respondeu `Nenhum: o sistema devolve cada bloco quando a função termina` → O que acaba com a função é p, a variável. O bloco só volta com free, e ninguém chamou: cada chamada deixou um ocupado. _(aponta a crença `system_frees_auto`)_
- respondeu `Um: cada chamada reusa o bloco da anterior` → Cada malloc entrega outro bloco: o da chamada anterior continua ocupado, e nem há mais quem saiba o endereço dele. São três.
- qualquer outro erro → Cada chamada pediu um bloco e não devolveu: três ocupados.

**Versão 2.** A função é chamada duas vezes. Quantos blocos continuam ocupados depois?

Já está escrito:

```c
void anota(void) { int *q = malloc(sizeof(int)); *q = 9; }

anota();
anota();
```

Opções: `Um: cada chamada reusa o bloco da anterior`  `Dois: nenhum foi devolvido`  `Nenhum: o sistema devolve cada bloco quando a função termina`

Resposta certa: `Dois: nenhum foi devolvido`

Se errar:

- respondeu `Nenhum: o sistema devolve cada bloco quando a função termina` → O que acaba com a função é q, a variável. O bloco só volta com free, e ninguém chamou: cada chamada deixou um ocupado. _(aponta a crença `system_frees_auto`)_
- respondeu `Um: cada chamada reusa o bloco da anterior` → Cada malloc entrega outro bloco: o da chamada anterior continua ocupado, e nem há mais quem saiba o endereço dele. São dois.
- qualquer outro erro → Cada chamada pediu um bloco e não devolveu: dois ocupados.

### Degrau 2 — guiado, completar

> Quem pediu devolve, com free, antes de a função terminar e enquanto o ponteiro ainda guarda o endereço.

**Versão 1.** Complete para a função devolver o bloco antes de terminar.

```c
void guarda(void) { int *p = malloc(sizeof(int)); ___; }
```

Peças: `free(p)`  `p = NULL`  `free(&p)`

Resposta certa: `void guarda(void) { int *p = malloc(sizeof(int)); free(p); }`

Se errar:

- respondeu `void guarda(void) { int *p = malloc(sizeof(int)); p = NULL; }` → p = NULL; só apaga o endereço que estava em p: o bloco continua ocupado. Quem devolve é free(p);
- respondeu `void guarda(void) { int *p = malloc(sizeof(int)); free(&p); }` → &p é o endereço da variável p, que está na pilha. free recebe o endereço do bloco, que está guardado em p: free(p);
- qualquer outro erro → free recebe o endereço do bloco, que está em p: free(p);

**Versão 2.** Complete para a função devolver o bloco antes de terminar.

```c
void anota(void) { int *q = malloc(sizeof(int)); ___; }
```

Peças: `free(&q)`  `free(q)`  `q = NULL`

Resposta certa: `void anota(void) { int *q = malloc(sizeof(int)); free(q); }`

Se errar:

- respondeu `void anota(void) { int *q = malloc(sizeof(int)); q = NULL; }` → q = NULL; só apaga o endereço que estava em q: o bloco continua ocupado. Quem devolve é free(q);
- respondeu `void anota(void) { int *q = malloc(sizeof(int)); free(&q); }` → &q é o endereço da variável q, que está na pilha. free recebe o endereço do bloco, que está guardado em q: free(q);
- qualquer outro erro → free recebe o endereço do bloco, que está em q: free(q);

### Degrau 3 — guiado, digitar

> Se a função devolve o endereço, o bloco passa para quem recebeu — junto com a obrigação de chamar free.

**Versão 1.** A função devolve o endereço do bloco, e quem recebe soma 1 nele. Que número aparece?

```c
int *novo(void) { int *p = malloc(sizeof(int)); *p = 7; return p; }

int *q;

q = novo();
*q = *q + 1;
printf("%d\n", *q);
free(q);
```

Resposta certa: `8`

Se errar:

- digitou `7` → O bloco continuou valendo depois da função, com o 7. Quem recebeu o endereço somou 1 nele: 8.
- qualquer outro erro → O bloco sobreviveu à função com 7, e recebeu mais 1: 8.

**Versão 2.** A função devolve o endereço do bloco, e quem recebe soma 5 nele. Que número aparece?

```c
int *novo(void) { int *p = malloc(sizeof(int)); *p = 15; return p; }

int *q;

q = novo();
*q = *q + 5;
printf("%d\n", *q);
free(q);
```

Resposta certa: `20`

Se errar:

- digitou `15` → O bloco continuou valendo depois da função, com o 15. Quem recebeu o endereço somou 5 nele: 20.
- qualquer outro erro → O bloco sobreviveu à função com 15, e recebeu mais 5: 20.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Ninguém devolve o bloco por você_

**Versão 1.** No fim deste trecho, quantos blocos continuam ocupados?

Já está escrito:

```c
int *novo(void) { int *p = malloc(sizeof(int)); return p; }

int *a;
int *b;

a = novo();
b = novo();
free(a);
```

Opções: `Um: o de b`  `Nenhum: os blocos acabaram com a função`  `Dois: free não vale para bloco vindo de função`

Resposta certa: `Um: o de b`

Se errar:

- respondeu `Nenhum: os blocos acabaram com a função` → O bloco não acaba com a função que o pediu: os dois continuaram depois dela. Com free voltou o de a; o de b continua ocupado.
- respondeu `Dois: free não vale para bloco vindo de função` → free devolve qualquer bloco de malloc, venha de onde vier o endereço. O de a voltou; sobra o de b.
- qualquer outro erro → Os dois blocos sobreviveram à função. O de a voltou com free; o de b continua ocupado.

**Versão 2.** No fim deste trecho, quantos blocos continuam ocupados?

Já está escrito:

```c
int *novo(void) { int *p = malloc(sizeof(int)); return p; }

int *a;
int *b;
int *c;

a = novo();
b = novo();
c = novo();
free(b);
```

Opções: `Nenhum: os blocos acabaram com a função`  `Três: free não vale para bloco vindo de função`  `Dois: o de a e o de c`

Resposta certa: `Dois: o de a e o de c`

Se errar:

- respondeu `Nenhum: os blocos acabaram com a função` → O bloco não acaba com a função que o pediu: os três continuaram depois dela. Com free voltou o de b; os de a e c continuam ocupados.
- respondeu `Três: free não vale para bloco vindo de função` → free devolve qualquer bloco de malloc, venha de onde vier o endereço. O de b voltou; sobram o de a e o de c.
- qualquer outro erro → Os três blocos sobreviveram à função. O de b voltou com free; os de a e c continuam ocupados.

### Degrau 5 — prática, escolher

**Versão 1.** Até quando o bloco deste trecho fica ocupado?

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
p = NULL;
```

Opções: `Até o programa terminar: o endereço se perdeu, e não dá mais para chamar free`  `Até a linha p = NULL;, que o devolve`  `Até o sistema perceber que ninguém usa`

Resposta certa: `Até o programa terminar: o endereço se perdeu, e não dá mais para chamar free`

Se errar:

- respondeu `Até a linha p = NULL;, que o devolve` → p = NULL; só apaga o endereço guardado em p. O bloco continua ocupado — e, sem o endereço, ninguém mais consegue chamar free para ele.
- respondeu `Até o sistema perceber que ninguém usa` → Enquanto o programa roda, ninguém recolhe por você. O bloco fica ocupado até o fim, porque o endereço dele se perdeu.
- qualquer outro erro → Sem free o bloco não volta, e o endereço se perdeu: fica ocupado até o programa terminar.

**Versão 2.** Até quando o primeiro bloco deste trecho fica ocupado?

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
q = malloc(sizeof(int));
free(q);
```

Opções: `Até o free(q);, que devolve os dois`  `Até o sistema perceber que ninguém usa`  `Até o programa terminar: q trocou de endereço, e o do primeiro bloco se perdeu`

Resposta certa: `Até o programa terminar: q trocou de endereço, e o do primeiro bloco se perdeu`

Se errar:

- respondeu `Até o free(q);, que devolve os dois` → free(q); devolve um bloco só: aquele cujo endereço está em q, o segundo. O endereço do primeiro foi perdido na segunda linha de malloc.
- respondeu `Até o sistema perceber que ninguém usa` → Enquanto o programa roda, ninguém recolhe por você. O primeiro bloco fica ocupado até o fim, porque o endereço dele se perdeu.
- qualquer outro erro → free(q); devolve o segundo bloco. O endereço do primeiro se perdeu: ele fica ocupado até o programa terminar.

### Se errar a pergunta do topo: a revisão

> O bloco não acaba com a função que o pediu, e ninguém o devolve por você.
> Enquanto não houver free, ele continua ocupado.

```c
int *novo(void) { int *p = malloc(sizeof(int)); *p = 7; return p; }

int *q;

q = novo();
printf("%d\n", *q);
free(q);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> O sistema libera a memória do heap automaticamente.

```c
void guarda(void) { int *p = malloc(sizeof(int)); if (p != NULL) *p = 7; }

guarda();
guarda();
```

**A função pede um bloco, escreve nele e termina. Ela é chamada duas vezes. Seguindo o programa, o compilador reclama de alguma coisa?**

- Sim: o bloco vaza quando a função termina _(é o que a máquina faz)_
- Não: o bloco é devolvido sozinho no fim da função _(é o que a crença espera)_

O compilador reclama:

```
leak of 'p'
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer). "leak" é vazamento: memória pedida e nunca devolvida. O programa não é executado._

O que isto mostra: O compilador reclama: o bloco de p vaza ("leak of 'p'"). A função termina, p acaba, e o bloco fica ocupado sem ninguém que saiba o endereço. Se o fim da função o devolvesse, não haveria vazamento para apontar.
