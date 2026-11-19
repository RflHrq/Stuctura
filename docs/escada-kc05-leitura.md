# A escada do kc_05 — Ponteiro NULL

Texto para leitura, gerado de `mvp/dominio/escada_kc05.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — NULL é um valor de verdade, escrito dentro do ponteiro. Não é a caixa de p estar vazia.

### Degrau 1 — guiado, escolher

> NULL é um valor que se guarda num ponteiro, como 15 se guarda num int.
> Ele quer dizer: este ponteiro não aponta para lugar nenhum.

**Versão 1.** Depois da última linha, p tem valor?

Já está escrito:

```c
int *p;

p = NULL;
```

Opções: `Tem: o valor NULL, que a linha escreveu`  `Não: NULL quer dizer que p está vazio, sem valor dentro`  `Tem: o endereço de uma variável`

Resposta certa: `Tem: o valor NULL, que a linha escreveu`

Se errar:

- respondeu `Não: NULL quer dizer que p está vazio, sem valor dentro` → NULL não é falta de valor: é um valor, e a linha o escreveu em p. Ele diz uma coisa certa: p não aponta para lugar nenhum. _(aponta a crença `null_is_absence`)_
- respondeu `Tem: o endereço de uma variável` → Nenhuma variável teve o endereço guardado em p. O valor que a linha escreveu é NULL: não aponta para lugar nenhum.
- qualquer outro erro → p tem valor: NULL, que a última linha escreveu.

**Versão 2.** Depois dessa linha, q tem valor?

Já está escrito:

```c
int *q = NULL;
```

Opções: `Tem: o valor NULL, que a linha escreveu`  `Não: NULL quer dizer que q está vazio, sem valor dentro`  `Tem: o endereço de uma variável`

Resposta certa: `Tem: o valor NULL, que a linha escreveu`

Se errar:

- respondeu `Não: NULL quer dizer que q está vazio, sem valor dentro` → NULL não é falta de valor: é um valor, e a linha o escreveu em q. Ele diz uma coisa certa: q não aponta para lugar nenhum. _(aponta a crença `null_is_absence`)_
- respondeu `Tem: o endereço de uma variável` → Nenhuma variável teve o endereço guardado em q. O valor que a linha escreveu é NULL: não aponta para lugar nenhum.
- qualquer outro erro → q tem valor: NULL, que a linha escreveu.

### Degrau 2 — guiado, digitar

> Dá para perguntar se um ponteiro vale NULL: p == NULL.
> A resposta é um número: 1 quando é verdade, 0 quando não é. O printf com %d mostra.

**Versão 1.** Que número este trecho mostra na tela?

```c
int *p;

p = NULL;
printf("%d\n", p == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → p recebeu NULL na linha anterior. A pergunta p == NULL é verdadeira, e a resposta é 1.
- qualquer outro erro → p vale NULL: a pergunta p == NULL é verdadeira, e a resposta é 1.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *q;

q = &idade;
printf("%d\n", q == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → q recebeu o endereço de idade, e não NULL. A pergunta q == NULL é falsa, e a resposta é 0.
- qualquer outro erro → q guarda o endereço de idade: a pergunta q == NULL é falsa, e a resposta é 0.

### Degrau 3 — guiado, digitar

> Com if, uma linha só roda quando a resposta é sim.
> Em if (p == NULL) idade = 20; a escrita em idade só acontece se p valer NULL.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = NULL;
if (p == NULL) idade = 20;
printf("%d\n", idade);
```

Resposta certa: `20`

Se errar:

- digitou `15` → p vale NULL, então a pergunta é verdadeira e a linha do if rodou: idade passou a guardar 20.
- qualquer outro erro → p vale NULL. A pergunta do if é verdadeira, e idade recebe 20.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = &idade;
if (p == NULL) idade = 20;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `20` → p guarda o endereço de idade, e não NULL. A pergunta é falsa, e a linha do if não rodou: idade continua com 15.
- qualquer outro erro → p não vale NULL. A pergunta do if é falsa, e idade continua com 15.

### Degrau 4 — guiado, montar

> Como NULL é um valor, ele se copia como qualquer outro.

**Versão 1.** p vale NULL. Faça q valer NULL também, copiando de p.

Já está escrito:

```c
int *p;
int *q;

p = NULL;
```

Peças: `q`  `=`  `p`  `;`  `*p`

Resposta certa: `q = p;`

Se errar:

- respondeu `q = *p ;` → *p iria ao lugar apontado, e p não aponta para lugar nenhum. O valor de p se copia sem o *: q = p;
- respondeu `p = q ;` → Assim é p que recebe o que está em q, e q não tem valor escolhido. Quem recebe fica à esquerda: q = p;
- qualquer outro erro → O valor guardado em p se copia sem o *: q = p;

**Versão 2.** c vale NULL. Faça d valer NULL também, copiando de c.

Já está escrito:

```c
char *c;
char *d;

c = NULL;
```

Peças: `d`  `=`  `c`  `;`  `*c`

Resposta certa: `d = c;`

Se errar:

- respondeu `d = *c ;` → *c iria ao lugar apontado, e c não aponta para lugar nenhum. O valor de c se copia sem o *: d = c;
- respondeu `c = d ;` → Assim é c que recebe o que está em d, e d não tem valor escolhido. Quem recebe fica à esquerda: d = c;
- qualquer outro erro → O valor guardado em c se copia sem o *: d = c;

### Degrau 5 — prática, digitar

_Nome do passo, no fechamento: Copiar NULL de um ponteiro para outro_

**Versão 1.** Que número este trecho mostra na tela?

```c
int *p;
int *q;

p = NULL;
q = p;
printf("%d\n", q == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → q = p; copiou o valor de p, que era NULL. q passou a valer NULL também, e a resposta é 1.
- qualquer outro erro → NULL é um valor, e foi copiado de p para q. A pergunta q == NULL dá 1.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *p;
int *q;

p = &idade;
q = p;
printf("%d\n", q == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → q = p; copiou o endereço de idade. q não vale NULL, e a resposta é 0.
- qualquer outro erro → q recebeu o endereço de idade, copiado de p. A pergunta q == NULL dá 0.

### Degrau 6 — prática, montar

**Versão 1.** Declare um ponteiro para inteiro chamado p e, na linha seguinte, escreva nele o valor que diz: não aponta para lugar nenhum.

Peças: `int *p;`  `p = NULL;`  `*p = NULL;`  `int p;`

Resposta certa: `int *p; p = NULL;`

Se errar:

- respondeu `int *p; *p = NULL;` → *p é o lugar apontado, e p ainda não aponta para lugar nenhum. O NULL vai no próprio ponteiro: p = NULL;
- respondeu `int p; p = NULL;` → Sem o *, p é um int comum, e NULL é valor de ponteiro. A declaração é int *p;
- respondeu `p = NULL; int *p;` → Primeiro a declaração, depois a escrita: int *p; e então p = NULL;
- qualquer outro erro → São duas linhas: int *p; e p = NULL;

**Versão 2.** Declare um ponteiro para caractere chamado c e, na linha seguinte, escreva nele o valor que diz: não aponta para lugar nenhum.

Peças: `char *c;`  `c = NULL;`  `*c = NULL;`  `char c;`

Resposta certa: `char *c; c = NULL;`

Se errar:

- respondeu `char *c; *c = NULL;` → *c é o lugar apontado, e c ainda não aponta para lugar nenhum. O NULL vai no próprio ponteiro: c = NULL;
- respondeu `char c; c = NULL;` → Sem o *, c é um char comum, e NULL é valor de ponteiro. A declaração é char *c;
- respondeu `c = NULL; char *c;` → Primeiro a declaração, depois a escrita: char *c; e então c = NULL;
- qualquer outro erro → São duas linhas: char *c; e c = NULL;

### Se errar a pergunta do topo: a revisão

> NULL é um valor: o que se guarda num ponteiro para dizer que ele não aponta para lugar nenhum.
> Um ponteiro que vale NULL tem valor. Sem valor escolhido está o ponteiro em que ninguém escreveu.

```c
int *p;

p = NULL;
printf("%d\n", p == NULL);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> NULL quer dizer que o ponteiro está vazio, sem valor dentro.

```c
int *p;
int *q;
int *r;

p = NULL;
r = p;
r = q;
```

**p recebeu NULL, e q não recebeu nada. As duas últimas linhas copiam de p e de q. De qual delas o compilador reclama?**

- Das duas: p e q estão sem valor _(é o que a crença espera)_
- Só de r = q; _(é o que a máquina faz)_
- De nenhuma

O compilador reclama:

```
'q' is used uninitialized
```

E não diz:

```
'p' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o que ele copiaria de q, ninguém sabe._

O que isto mostra: O compilador reclama só de q, que está sem valor. De p ele não diz nada: NULL é um valor como os outros, e copiar de p é copiar um valor.

## B2 — Escrever 0 onde se espera ponteiro dá o ponteiro nulo. Um zero que chega em tempo de execução não tem essa garantia.

### Degrau 1 — guiado, digitar

> O 0 escrito no código, posto num ponteiro, é o ponteiro nulo.
> p = 0; faz o mesmo que p = NULL;

**Versão 1.** Que número este trecho mostra na tela?

```c
int *p;

p = 0;
printf("%d\n", p == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → O 0 escrito no código vira o ponteiro nulo: p = 0; deixa p valendo NULL, e a resposta é 1.
- qualquer outro erro → p = 0; põe o ponteiro nulo em p. A pergunta p == NULL dá 1.

**Versão 2.** Que número este trecho mostra na tela?

```c
int *q = 0;

printf("%d\n", q == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → O 0 escrito no código vira o ponteiro nulo: q nasce valendo NULL, e a resposta é 1.
- qualquer outro erro → int *q = 0; faz q nascer com o ponteiro nulo. A pergunta q == NULL dá 1.

### Degrau 2 — guiado, escolher

> Isso vale para o 0 escrito ali, na linha.
> Um zero guardado numa variável inteira é um número comum: o compilador reclama de p = n;

**Versão 1.** n guarda zero. Qual destas linhas o compilador aceita?

Já está escrito:

```c
int n;
int *p;

n = 0;
```

Opções: `p = 0;`  `p = n;`  `p = &0;`

Resposta certa: `p = 0;`

Se errar:

- respondeu `p = n;` → n é uma variável inteira: o que ela guarda é um número comum, mesmo sendo zero. O compilador reclama. Aceita: p = 0;
- respondeu `p = &0;` → 0 é um número escrito no código, e não tem endereço. Para o ponteiro nulo basta o próprio 0: p = 0;
- qualquer outro erro → Só o 0 escrito na linha vira o ponteiro nulo: p = 0;

**Versão 2.** pontos guarda zero. Qual destas linhas o compilador aceita?

Já está escrito:

```c
int pontos;
int *q;

pontos = 0;
```

Opções: `q = pontos;`  `q = 0;`  `q = &0;`

Resposta certa: `q = 0;`

Se errar:

- respondeu `q = pontos;` → pontos é uma variável inteira: o que ela guarda é um número comum, mesmo sendo zero. O compilador reclama. Aceita: q = 0;
- respondeu `q = &0;` → 0 é um número escrito no código, e não tem endereço. Para o ponteiro nulo basta o próprio 0: q = 0;
- qualquer outro erro → Só o 0 escrito na linha vira o ponteiro nulo: q = 0;

### Degrau 3 — guiado, escolher

> Dá para forçar: q = (int *)n; manda o compilador tratar o número de n como endereço, e ele aceita.
> Mas a linguagem não promete que saia dali o ponteiro nulo, mesmo com n valendo zero.

**Versão 1.** Qual dos dois é o ponteiro nulo com certeza?

Já está escrito:

```c
int n;
int *p;
int *q;

n = 0;
p = 0;
q = (int *)n;
```

Opções: `Só p: recebeu o 0 escrito no código`  `Os dois: qualquer zero vira o ponteiro nulo`  `Só q: recebeu o zero da variável, que é o de verdade`

Resposta certa: `Só p: recebeu o 0 escrito no código`

Se errar:

- respondeu `Os dois: qualquer zero vira o ponteiro nulo` → A garantia é do 0 escrito no código. O zero que chega dentro de n é um número comum: forçado para dentro de q, não tem promessa nenhuma. _(aponta a crença `any_zero_is_null`)_
- respondeu `Só q: recebeu o zero da variável, que é o de verdade` → É o contrário: a garantia é do 0 escrito na linha. O zero que vem de n foi forçado para dentro de q, sem promessa nenhuma.
- qualquer outro erro → Com certeza, só p: a garantia é do 0 escrito no código.

**Versão 2.** Qual dos dois é o ponteiro nulo com certeza?

Já está escrito:

```c
int pontos;
int *p;
int *q;

pontos = 0;
p = (int *)pontos;
q = 0;
```

Opções: `Só q: recebeu o 0 escrito no código`  `Os dois: qualquer zero vira o ponteiro nulo`  `Só p: recebeu o zero da variável, que é o de verdade`

Resposta certa: `Só q: recebeu o 0 escrito no código`

Se errar:

- respondeu `Os dois: qualquer zero vira o ponteiro nulo` → A garantia é do 0 escrito no código. O zero que chega dentro de pontos é um número comum: forçado para dentro de p, não tem promessa nenhuma. _(aponta a crença `any_zero_is_null`)_
- respondeu `Só p: recebeu o zero da variável, que é o de verdade` → É o contrário: a garantia é do 0 escrito na linha. O zero que vem de pontos foi forçado para dentro de p, sem promessa nenhuma.
- qualquer outro erro → Com certeza, só q: a garantia é do 0 escrito no código.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Aceitar no ponteiro só o 0 escrito no código_

**Versão 1.** Uma destas linhas faz o compilador reclamar. Qual?

Já está escrito:

```c
int idade;
int *p;

idade = 0;
```

Opções: `p = NULL;`  `p = 0;`  `p = idade;`

Resposta certa: `p = idade;`

Se errar:

- respondeu `p = NULL;` → p = NULL; escreve o ponteiro nulo, e é aceita. A que não é: p = idade;, que põe um inteiro comum num ponteiro.
- respondeu `p = 0;` → p = 0; usa o 0 escrito no código, que vira o ponteiro nulo. A que não é aceita: p = idade;
- qualquer outro erro → idade é um inteiro comum, mesmo valendo zero: p = idade; faz o compilador reclamar.

**Versão 2.** Uma destas linhas faz o compilador reclamar. Qual?

Já está escrito:

```c
int pontos;
int *q;

pontos = 0;
```

Opções: `q = pontos;`  `q = 0;`  `q = NULL;`

Resposta certa: `q = pontos;`

Se errar:

- respondeu `q = 0;` → q = 0; usa o 0 escrito no código, que vira o ponteiro nulo. A que não é aceita: q = pontos;
- respondeu `q = NULL;` → q = NULL; escreve o ponteiro nulo, e é aceita. A que não é: q = pontos;, que põe um inteiro comum num ponteiro.
- qualquer outro erro → pontos é um inteiro comum, mesmo valendo zero: q = pontos; faz o compilador reclamar.

### Degrau 5 — prática, montar

**Versão 1.** Sem escrever a palavra NULL, faça q virar o ponteiro nulo.

Já está escrito:

```c
int *q;
```

Peças: `q`  `=`  `0`  `;`  `*q`  `&0`

Resposta certa: `q = 0;`

Se errar:

- respondeu `*q = 0 ;` → *q = 0; escreveria zero no lugar apontado, e q não aponta para lugar escolhido. O ponteiro nulo é q = 0;
- respondeu `q = &0 ;` → 0 é um número escrito no código, e não tem endereço. Basta o próprio 0: q = 0;
- qualquer outro erro → O 0 escrito no código, posto no ponteiro, é o ponteiro nulo: q = 0;

**Versão 2.** Sem escrever a palavra NULL, faça p virar o ponteiro nulo.

Já está escrito:

```c
int *p;
```

Peças: `p`  `=`  `0`  `;`  `*p`  `&0`

Resposta certa: `p = 0;`

Se errar:

- respondeu `*p = 0 ;` → *p = 0; escreveria zero no lugar apontado, e p não aponta para lugar escolhido. O ponteiro nulo é p = 0;
- respondeu `p = &0 ;` → 0 é um número escrito no código, e não tem endereço. Basta o próprio 0: p = 0;
- qualquer outro erro → O 0 escrito no código, posto no ponteiro, é o ponteiro nulo: p = 0;

### Se errar a pergunta do topo: a revisão

> O 0 escrito no código, posto num ponteiro, é o ponteiro nulo: p = 0; faz o mesmo que p = NULL;
> Vale para o 0 escrito ali. Um zero guardado numa variável inteira é só um número, e o compilador não o aceita num ponteiro.

```c
int *p;

p = 0;
printf("%d\n", p == NULL);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> Qualquer zero vira ponteiro nulo, inclusive um que chegue em tempo de execução.

```c
int n;
int *p;

n = 0;
p = 0;
p = n;
```

**As duas últimas linhas põem um zero em p: o 0 escrito no código, e o zero guardado em n. De qual delas o compilador reclama?**

- De nenhuma: zero é zero, e qualquer zero vira o ponteiro nulo _(é o que a crença espera)_
- Só de p = n; _(é o que a máquina faz)_
- Das duas

O compilador reclama:

```
makes pointer from integer without a cast
```

_Mensagem do gcc 16.2, para a linha p = n;. Todo compilador de C tem de reclamar dela, cada um com as suas palavras._

O que isto mostra: O compilador aceita p = 0; e reclama de p = n;, mesmo com n valendo zero. O que vira ponteiro nulo é o 0 escrito no código, e não qualquer zero.

## B3 — Nenhuma caixa mora nesse endereço. Ele é reservado justamente para significar "nenhum lugar".

### Degrau 1 — guiado, escolher

> O valor NULL é reservado: nenhuma variável fica no endereço que ele representa.
> Mesmo escrito como 0, ele não é um lugar da memória como os outros.

**Versão 1.** Para onde p aponta?

Já está escrito:

```c
int *p;

p = NULL;
```

Opções: `Para lugar nenhum: não há variável nesse endereço`  `Para o endereço 0, onde há memória como em qualquer outro lugar`  `Para o próprio p`

Resposta certa: `Para lugar nenhum: não há variável nesse endereço`

Se errar:

- respondeu `Para o endereço 0, onde há memória como em qualquer outro lugar` → O valor do ponteiro nulo não é um lugar como os outros: é reservado, e nenhuma variável mora ali. p não aponta para lugar nenhum. _(aponta a crença `null_points_to_zero`)_
- respondeu `Para o próprio p` → Um ponteiro que aponta para si mesmo guardaria o próprio endereço. p guarda NULL: não aponta para lugar nenhum.
- qualquer outro erro → p vale NULL: não aponta para lugar nenhum.

**Versão 2.** Para onde q aponta?

Já está escrito:

```c
int *q = NULL;
```

Opções: `Para lugar nenhum: não há variável nesse endereço`  `Para o endereço 0, onde há memória como em qualquer outro lugar`  `Para o próprio q`

Resposta certa: `Para lugar nenhum: não há variável nesse endereço`

Se errar:

- respondeu `Para o endereço 0, onde há memória como em qualquer outro lugar` → O valor do ponteiro nulo não é um lugar como os outros: é reservado, e nenhuma variável mora ali. q não aponta para lugar nenhum. _(aponta a crença `null_points_to_zero`)_
- respondeu `Para o próprio q` → Um ponteiro que aponta para si mesmo guardaria o próprio endereço. q guarda NULL: não aponta para lugar nenhum.
- qualquer outro erro → q vale NULL: não aponta para lugar nenhum.

### Degrau 2 — guiado, digitar

> Por isso o endereço de uma variável nunca é NULL.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

p = &idade;
printf("%d\n", p == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → p guarda o endereço de idade, e endereço de variável nunca é NULL. A pergunta é falsa: a resposta é 0.
- qualquer outro erro → O endereço de idade nunca é NULL. A pergunta p == NULL dá 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

nota = 0;
q = &nota;
printf("%d\n", q == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → Quem guarda zero é nota. q guarda o endereço dela, e endereço de variável nunca é NULL: a resposta é 0.
- qualquer outro erro → O endereço de nota nunca é NULL, valha nota o que valer. A pergunta q == NULL dá 0.

### Degrau 3 — guiado, digitar

> É o que torna NULL útil: ele separa o ponteiro que aponta para uma variável do que não aponta para nada.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;
int *q;

p = &idade;
q = NULL;
printf("%d\n", p == q);
```

Resposta certa: `0`

Se errar:

- digitou `1` → p guarda o endereço de idade, e q guarda NULL. Endereço de variável nunca é NULL: os dois são diferentes, e a resposta é 0.
- qualquer outro erro → Um guarda o endereço de idade, o outro guarda NULL. São diferentes: a resposta é 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
int *p;
int *q;

p = NULL;
q = NULL;
printf("%d\n", p == q);
```

Resposta certa: `1`

Se errar:

- digitou `0` → Os dois guardam o mesmo valor, NULL. A pergunta p == q é verdadeira, e a resposta é 1.
- qualquer outro erro → p e q guardam o mesmo valor, NULL. A pergunta p == q dá 1.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Endereço de variável nunca é NULL_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = &idade;
if (p == NULL) idade = 0;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → p guarda o endereço de idade, que nunca é NULL. A pergunta é falsa, e a linha do if não rodou.
- qualquer outro erro → O endereço de idade nunca é NULL: o if não roda, e idade continua com 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

nota = 7;
q = &nota;
if (q == NULL) nota = 0;
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `0` → q guarda o endereço de nota, que nunca é NULL. A pergunta é falsa, e a linha do if não rodou.
- qualquer outro erro → O endereço de nota nunca é NULL: o if não roda, e nota continua com 7.

### Degrau 5 — prática, escolher

**Versão 1.** Depois destas linhas, qual ponteiro vale NULL?

Já está escrito:

```c
int idade;
int nota;
int *p;
int *q;

p = &idade;
q = &nota;
```

Opções: `Nenhum: endereço de variável nunca é NULL`  `p, se idade estiver no começo da memória`  `Os dois, até idade e nota receberem valor`

Resposta certa: `Nenhum: endereço de variável nunca é NULL`

Se errar:

- respondeu `p, se idade estiver no começo da memória` → Nenhuma variável mora no endereço do ponteiro nulo, esteja onde estiver. p guarda o endereço de idade, que não é NULL.
- respondeu `Os dois, até idade e nota receberem valor` → O endereço existe desde a declaração, com valor ou sem, e nunca é NULL. Nenhum dos dois ponteiros vale NULL.
- qualquer outro erro → p e q guardam endereços de variáveis, e endereço de variável nunca é NULL.

**Versão 2.** Depois destas linhas, qual ponteiro vale NULL?

Já está escrito:

```c
int idade;
int *p;
int *q;

p = &idade;
q = NULL;
```

Opções: `Só q: uma linha escreveu NULL nele`  `Os dois, se idade estiver no começo da memória`  `Nenhum: NULL não é valor que se guarde`

Resposta certa: `Só q: uma linha escreveu NULL nele`

Se errar:

- respondeu `Os dois, se idade estiver no começo da memória` → Nenhuma variável mora no endereço do ponteiro nulo, esteja onde estiver. p guarda o endereço de idade; só q vale NULL.
- respondeu `Nenhum: NULL não é valor que se guarde` → NULL é um valor, e a última linha o escreveu em q. Só q vale NULL.
- qualquer outro erro → q recebeu NULL; p recebeu o endereço de idade, que nunca é NULL.

### Se errar a pergunta do topo: a revisão

> Nenhuma variável mora no endereço do ponteiro nulo: ele é reservado para dizer 'nenhum lugar'.
> Por isso o endereço de uma variável nunca é NULL.

```c
int idade;
int *p;

p = &idade;
printf("%d\n", p == NULL);
```

A máquina imprime:

```
0
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro nulo aponta para o endereço 0, e lá há memória como em qualquer outro lugar.

```c
int idade;

if (&idade == NULL) printf("igual\n");
```

**O if compara o endereço de idade com NULL. O que o compilador diz dessa comparação?**

- Nada: idade pode estar no endereço do ponteiro nulo, como em qualquer outro _(é o que a crença espera)_
- Que ela nunca vai dar verdadeiro _(é o que a máquina faz)_

O compilador reclama:

```
will never be NULL
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall)._

O que isto mostra: O próprio compilador avisa: o endereço de idade nunca vai ser NULL. Esse valor é reservado para dizer "nenhum lugar", e variável nenhuma mora ali.

## I1 — Comparar p com NULL só lê o valor de p. Não é uma ida à memória apontada.

### Degrau 1 — guiado, escolher

> p == NULL lê o valor guardado em p, e compara.
> Ela não vai ao lugar apontado: quem vai é o *p.

**Versão 1.** O que a comparação da última linha lê?

Já está escrito:

```c
int idade;
int *p;

p = NULL;
if (p == NULL) idade = 0;
```

Opções: `O valor guardado em p`  `O que está no lugar apontado: olhar p é olhar o que está lá`  `O endereço do próprio p`

Resposta certa: `O valor guardado em p`

Se errar:

- respondeu `O que está no lugar apontado: olhar p é olhar o que está lá` → p é uma variável, com o valor dela: um endereço, ou NULL. A comparação lê esse valor e para aí. Ir ao lugar apontado é com o *p. _(aponta a crença `pointer_is_just_a_name`)_
- respondeu `O endereço do próprio p` → O endereço do próprio ponteiro seria &p. A comparação lê o valor guardado em p, que aqui é NULL.
- qualquer outro erro → A comparação lê o valor guardado em p, e não vai a lugar nenhum.

**Versão 2.** O que a comparação da última linha lê?

Já está escrito:

```c
int nota;
int *q;

q = NULL;
if (q == NULL) nota = 0;
```

Opções: `O valor guardado em q`  `O que está no lugar apontado: olhar q é olhar o que está lá`  `O endereço do próprio q`

Resposta certa: `O valor guardado em q`

Se errar:

- respondeu `O que está no lugar apontado: olhar q é olhar o que está lá` → q é uma variável, com o valor dela: um endereço, ou NULL. A comparação lê esse valor e para aí. Ir ao lugar apontado é com o *q. _(aponta a crença `pointer_is_just_a_name`)_
- respondeu `O endereço do próprio q` → O endereço do próprio ponteiro seria &q. A comparação lê o valor guardado em q, que aqui é NULL.
- qualquer outro erro → A comparação lê o valor guardado em q, e não vai a lugar nenhum.

### Degrau 2 — guiado, escolher

> São duas perguntas diferentes: p == NULL pergunta do ponteiro; *p == 0 pergunta do lugar apontado.
> Com p valendo NULL, só a primeira pode ser feita.

**Versão 1.** p vale NULL. Qual destas linhas é segura?

Já está escrito:

```c
int idade;
int *p;

idade = 15;
p = NULL;
```

Opções: `if (p == NULL) idade = 0;`  `if (*p == 0) idade = 0;`  `idade = *p;`

Resposta certa: `if (p == NULL) idade = 0;`

Se errar:

- respondeu `if (*p == 0) idade = 0;` → *p == 0 vai ao lugar apontado para ler, e p não aponta para lugar nenhum. A pergunta segura é sobre o ponteiro: p == NULL
- respondeu `idade = *p;` → idade = *p; vai ao lugar apontado, e p não aponta para lugar nenhum. Segura é a que só lê o ponteiro: if (p == NULL) idade = 0;
- qualquer outro erro → Segura é a que só lê o ponteiro: if (p == NULL) idade = 0;

**Versão 2.** q vale NULL. Qual destas linhas é segura?

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = NULL;
```

Opções: `nota = *q;`  `if (*q == 0) nota = 0;`  `if (q == NULL) nota = 0;`

Resposta certa: `if (q == NULL) nota = 0;`

Se errar:

- respondeu `nota = *q;` → nota = *q; vai ao lugar apontado, e q não aponta para lugar nenhum. Segura é a que só lê o ponteiro: if (q == NULL) nota = 0;
- respondeu `if (*q == 0) nota = 0;` → *q == 0 vai ao lugar apontado para ler, e q não aponta para lugar nenhum. A pergunta segura é sobre o ponteiro: q == NULL
- qualquer outro erro → Segura é a que só lê o ponteiro: if (q == NULL) nota = 0;

### Degrau 3 — guiado, digitar

> A pergunta ao contrário é p != NULL: 'p aponta para algum lugar?'
> Posta antes do *p, ela garante que só se vai aonde há lugar.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &nota;
if (p != NULL) idade = *p;
printf("%d\n", idade);
```

Resposta certa: `7`

Se errar:

- digitou `15` → p guarda o endereço de nota, então p != NULL é verdade e a linha rodou: idade recebeu o valor de nota, 7.
- qualquer outro erro → p aponta para nota. A pergunta é verdadeira, e idade recebe o valor que mora lá: 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = NULL;
if (p != NULL) idade = *p;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → p vale NULL, então p != NULL é falso, e a linha do if não rodou. idade continua com 15.
- qualquer outro erro → p vale NULL. A pergunta é falsa, o *p não é usado, e idade continua com 15.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Perguntar pelo ponteiro antes de usar *p_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = NULL;
if (p == NULL) p = &idade;
*p = 20;
printf("%d\n", idade);
```

Resposta certa: `20`

Se errar:

- digitou `15` → A pergunta p == NULL era verdadeira, e o if deu a p o endereço de idade. Depois *p = 20; escreveu nela.
- qualquer outro erro → O if deu a p o endereço de idade antes do uso. *p = 20; escreveu em idade.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int pontos;
int *q;

nota = 7;
pontos = 3;
q = &pontos;
if (q == NULL) q = &nota;
*q = 9;
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `9` → q já guardava o endereço de pontos: a pergunta q == NULL era falsa, e o if não trocou nada. O 9 foi para pontos; nota continua com 7.
- qualquer outro erro → q apontava para pontos, e o if não rodou. *q = 9; escreveu em pontos; nota continua com 7.

### Degrau 5 — prática, escolher

**Versão 1.** p vale NULL. Qual destas perguntas o programa pode fazer sem ir a lugar nenhum?

Já está escrito:

```c
int *p;

p = NULL;
```

Opções: `p == NULL — lê só o valor guardado em p`  `*p == 0 — lê o lugar apontado`  `As duas: p e *p olham a mesma coisa`

Resposta certa: `p == NULL — lê só o valor guardado em p`

Se errar:

- respondeu `*p == 0 — lê o lugar apontado` → *p == 0 precisa ir ao lugar apontado para ler, e p não aponta para lugar nenhum. A que não sai de p é p == NULL.
- respondeu `As duas: p e *p olham a mesma coisa` → p é o valor guardado no ponteiro; *p é o que mora no lugar apontado. Só p == NULL fica dentro de p.
- qualquer outro erro → p == NULL lê só o ponteiro. *p == 0 iria ao lugar apontado.

**Versão 2.** q vale NULL. Qual destas perguntas o programa pode fazer sem ir a lugar nenhum?

Já está escrito:

```c
int *q = NULL;
```

Opções: `*q != 0 — lê o lugar apontado`  `q != NULL — lê só o valor guardado em q`  `As duas: q e *q olham a mesma coisa`

Resposta certa: `q != NULL — lê só o valor guardado em q`

Se errar:

- respondeu `*q != 0 — lê o lugar apontado` → *q != 0 precisa ir ao lugar apontado para ler, e q não aponta para lugar nenhum. A que não sai de q é q != NULL.
- respondeu `As duas: q e *q olham a mesma coisa` → q é o valor guardado no ponteiro; *q é o que mora no lugar apontado. Só q != NULL fica dentro de q.
- qualquer outro erro → q != NULL lê só o ponteiro. *q != 0 iria ao lugar apontado.

### Se errar a pergunta do topo: a revisão

> p == NULL olha só o que está guardado em p. Não vai ao lugar apontado.
> Por isso é seguro perguntar mesmo quando p vale NULL — e é assim que se evita ir aonde não há lugar.

```c
int idade;
int *p;

idade = 15;
p = NULL;
if (p != NULL) idade = *p;
printf("%d\n", idade);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> p é só outro nome da variável apontada: olhar p é olhar o que está lá.

```c
int *p;

p = NULL;
if (p == NULL) printf("1\n");
```

**p vale NULL: não aponta para lugar nenhum. O que o trecho faz?**

- Mostra 1: a comparação só lê o valor guardado em p _(é o que a máquina faz)_
- Não mostra nada: para comparar, o programa vai até o lugar apontado, e não há lugar _(é o que a crença espera)_

A máquina imprime:

```
1
```

O que isto mostra: Saiu 1, e nada parou. A comparação leu o valor guardado em p, e mais nada: se ela fosse até o lugar apontado, não haveria lugar para ir.

## I2 — p == 0 funciona no código. Isso não quer dizer que os bits guardados em p sejam zeros.

### Degrau 1 — guiado, digitar

> No código, comparar um ponteiro com 0 é perguntar se ele é o ponteiro nulo.
> p == 0 e p == NULL dão a mesma resposta.

**Versão 1.** Que número este trecho mostra na tela?

```c
int *p;

p = NULL;
printf("%d\n", p == 0);
```

Resposta certa: `1`

Se errar:

- digitou `0` → Ao lado de um ponteiro, o 0 do código quer dizer 'o ponteiro nulo'. p vale NULL, e a resposta é 1.
- qualquer outro erro → p == 0 pergunta se p é o ponteiro nulo. p vale NULL: a resposta é 1.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

q = &nota;
printf("%d\n", q == 0);
```

Resposta certa: `0`

Se errar:

- digitou `1` → q == 0 pergunta se q é o ponteiro nulo. q guarda o endereço de nota, que nunca é: a resposta é 0.
- qualquer outro erro → q guarda o endereço de nota, e não o ponteiro nulo. A resposta é 0.

### Degrau 2 — guiado, escolher

> Essa é uma regra de escrita: no código, o 0 ao lado de um ponteiro quer dizer 'o ponteiro nulo'.
> Ela não diz o que a máquina guarda dentro de p. Isso é assunto de cada máquina.

**Versão 1.** p == 0 dá 1. O que isso garante sobre o que a máquina guarda dentro de p?

Já está escrito:

```c
int *p;

p = NULL;
```

Opções: `Nada: a regra é da linguagem, e não da memória`  `Que lá só há zeros: NULL é o número 0 em todo lugar`  `Que p aponta para o endereço 0`

Resposta certa: `Nada: a regra é da linguagem, e não da memória`

Se errar:

- respondeu `Que lá só há zeros: NULL é o número 0 em todo lugar` → A igualdade com 0 vale no código que você escreve. O que a máquina guarda para representar o ponteiro nulo, a linguagem não diz. _(aponta a crença `null_is_zero_always`)_
- respondeu `Que p aponta para o endereço 0` → O ponteiro nulo não aponta para lugar nenhum. A comparação com 0 é só o jeito de perguntar isso no código.
- qualquer outro erro → A regra é da linguagem: ela não diz o que a máquina guarda dentro de p.

**Versão 2.** q == 0 dá 1. O que isso garante sobre o que a máquina guarda dentro de q?

Já está escrito:

```c
int *q = 0;
```

Opções: `Nada: a regra é da linguagem, e não da memória`  `Que lá só há zeros: NULL é o número 0 em todo lugar`  `Que q aponta para o endereço 0`

Resposta certa: `Nada: a regra é da linguagem, e não da memória`

Se errar:

- respondeu `Que lá só há zeros: NULL é o número 0 em todo lugar` → A igualdade com 0 vale no código que você escreve. O que a máquina guarda para representar o ponteiro nulo, a linguagem não diz. _(aponta a crença `null_is_zero_always`)_
- respondeu `Que q aponta para o endereço 0` → O ponteiro nulo não aponta para lugar nenhum. A comparação com 0 é só o jeito de perguntar isso no código.
- qualquer outro erro → A regra é da linguagem: ela não diz o que a máquina guarda dentro de q.

### Degrau 3 — guiado, escolher

> O ponteiro nulo não é um número inteiro: é um valor de ponteiro, que quer dizer nenhum lugar.
> O mesmo 0 escrito no código vira coisas diferentes, conforme o tipo de quem o recebe.

**Versão 1.** n e p receberam um 0 escrito no código. O que cada um guarda?

Já está escrito:

```c
int n;
int *p;

n = 0;
p = 0;
```

Opções: `n guarda o número zero; p guarda o ponteiro nulo`  `Os dois guardam o número zero`  `Os dois guardam o ponteiro nulo`

Resposta certa: `n guarda o número zero; p guarda o ponteiro nulo`

Se errar:

- respondeu `Os dois guardam o número zero` → Em p, que é ponteiro, o 0 do código vira o ponteiro nulo: 'nenhum lugar'. Número zero, só n guarda.
- respondeu `Os dois guardam o ponteiro nulo` → n é uma variável inteira, e guarda o número zero. Só em p, que é ponteiro, o 0 do código vira o ponteiro nulo.
- qualquer outro erro → O mesmo 0 do código vira coisas diferentes: número zero em n, ponteiro nulo em p.

**Versão 2.** pontos e q receberam um 0 escrito no código. O que cada um guarda?

Já está escrito:

```c
int pontos;
int *q;

pontos = 0;
q = 0;
```

Opções: `pontos guarda o número zero; q guarda o ponteiro nulo`  `Os dois guardam o número zero`  `Os dois guardam o ponteiro nulo`

Resposta certa: `pontos guarda o número zero; q guarda o ponteiro nulo`

Se errar:

- respondeu `Os dois guardam o número zero` → Em q, que é ponteiro, o 0 do código vira o ponteiro nulo: 'nenhum lugar'. Número zero, só pontos guarda.
- respondeu `Os dois guardam o ponteiro nulo` → pontos é uma variável inteira, e guarda o número zero. Só em q, que é ponteiro, o 0 do código vira o ponteiro nulo.
- qualquer outro erro → O mesmo 0 do código vira coisas diferentes: número zero em pontos, ponteiro nulo em q.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Comparar com 0 o ponteiro, e não o valor apontado_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 0;
p = &idade;
printf("%d\n", p == 0);
```

Resposta certa: `0`

Se errar:

- digitou `1` → Quem guarda zero é idade. p guarda o endereço dela, e endereço de variável nunca é o ponteiro nulo: a resposta é 0.
- qualquer outro erro → p == 0 pergunta do ponteiro, e não do que está em idade. p guarda um endereço: a resposta é 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

nota = 0;
q = NULL;
printf("%d\n", q == 0);
```

Resposta certa: `1`

Se errar:

- digitou `0` → q == 0 pergunta se q é o ponteiro nulo, e q recebeu NULL: a resposta é 1. O zero em nota não entra na pergunta.
- qualquer outro erro → q vale NULL, e q == 0 pergunta exatamente isso: a resposta é 1.

### Degrau 5 — prática, montar

**Versão 1.** Monte a linha que mostra na tela se p é o ponteiro nulo, sem escrever a palavra NULL.

Já está escrito:

```c
int *p;

p = NULL;
```

Peças: `printf("%d\n",`  `p == 0`  `);`  `*p == 0`  `p`

Resposta certa: `printf("%d\n", p == 0);`

Se errar:

- respondeu `printf("%d\n", *p == 0 );` → *p == 0 iria ao lugar apontado para ler, e p não aponta para lugar nenhum. A pergunta é sobre o ponteiro: p == 0
- respondeu `printf("%d\n", p );` → p sozinho é o valor guardado no ponteiro, e não uma pergunta. Para perguntar se é o nulo: p == 0
- qualquer outro erro → A pergunta é p == 0, e o printf mostra a resposta: printf("%d\n", p == 0);

**Versão 2.** Monte a linha que mostra na tela se q é o ponteiro nulo, sem escrever a palavra NULL.

Já está escrito:

```c
int *q = NULL;
```

Peças: `printf("%d\n",`  `q == 0`  `);`  `*q == 0`  `q`

Resposta certa: `printf("%d\n", q == 0);`

Se errar:

- respondeu `printf("%d\n", *q == 0 );` → *q == 0 iria ao lugar apontado para ler, e q não aponta para lugar nenhum. A pergunta é sobre o ponteiro: q == 0
- respondeu `printf("%d\n", q );` → q sozinho é o valor guardado no ponteiro, e não uma pergunta. Para perguntar se é o nulo: q == 0
- qualquer outro erro → A pergunta é q == 0, e o printf mostra a resposta: printf("%d\n", q == 0);

### Se errar a pergunta do topo: a revisão

> No código, comparar um ponteiro com 0 é perguntar se ele é o ponteiro nulo: p == 0 e p == NULL dizem o mesmo.
> É uma regra da linguagem. Ela não diz que NULL é o número zero, nem o que fica guardado na memória.

```c
int *p;

p = NULL;
printf("%d\n", p == 0);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> NULL é o inteiro 0 em todos os contextos, inclusive no que está guardado na memória.

```c
int n;

n = NULL;
```

**O compilador reclama de guardar NULL numa variável inteira?**

- Sim: NULL é valor de ponteiro, e n é um int _(é o que a máquina faz)_
- Não: NULL é o número 0, em qualquer lugar _(é o que a crença espera)_

O compilador reclama:

```
makes integer from pointer without a cast
```

_Mensagem do gcc 16.2, em que NULL é escrito como um ponteiro. A linguagem deixa cada compilador escrevê-lo do seu jeito, e outro pode aceitar esta linha._

O que isto mostra: Aqui o compilador reclama: para ele NULL é um ponteiro, e n é um inteiro. No código, 0 e NULL se comparam igual com um ponteiro — e isso não faz de NULL o número zero.

## I3 — Então *p com p em NULL manda o programa a um endereço onde não existe caixa nenhuma. O que acontece daí não é definido.

### Degrau 1 — guiado, escolher

> *p vai ao lugar cujo endereço está em p.
> Quando esse lugar não existe, o padrão do C não diz o que acontece: o programa pode parar, ou seguir errado.

**Versão 1.** O que a última linha faz?

Já está escrito:

```c
int *p;

p = NULL;
*p = 1;
```

Opções: `Não dá para dizer: ela vai a um lugar que não existe`  `Nada de mais: *p com p nulo vale 0, como um lugar vazio`  `Escreve 1 dentro do próprio p`

Resposta certa: `Não dá para dizer: ela vai a um lugar que não existe`

Se errar:

- respondeu `Nada de mais: *p com p nulo vale 0, como um lugar vazio` → Não há lugar vazio ali: não há lugar nenhum. A linguagem não define o que acontece — o programa pode parar, ou seguir errado. _(aponta a crença `null_is_safe_to_deref`)_
- respondeu `Escreve 1 dentro do próprio p` → Escrever no próprio ponteiro seria p = ...; sem o *. Com o *, a linha vai ao lugar apontado, e p não aponta para nenhum.
- qualquer outro erro → p não aponta para lugar nenhum. O que *p = 1; faz não é definido.

**Versão 2.** O que a última linha faz?

Já está escrito:

```c
int nota;
int *q;

q = NULL;
nota = *q;
```

Opções: `Não dá para dizer: ela vai a um lugar que não existe`  `Nada de mais: *q com q nulo vale 0, como um lugar vazio`  `Copia o NULL para nota`

Resposta certa: `Não dá para dizer: ela vai a um lugar que não existe`

Se errar:

- respondeu `Nada de mais: *q com q nulo vale 0, como um lugar vazio` → Não há lugar vazio ali: não há lugar nenhum. A linguagem não define o que acontece — o programa pode parar, ou seguir errado. _(aponta a crença `null_is_safe_to_deref`)_
- respondeu `Copia o NULL para nota` → Copiar o valor do ponteiro seria sem o *. Com o *, a linha vai ao lugar apontado, e q não aponta para nenhum.
- qualquer outro erro → q não aponta para lugar nenhum. O que nota = *q; faz não é definido.

### Degrau 2 — guiado, escolher

> Por isso, antes de usar *p, pergunta-se ao ponteiro: if (p != NULL)
> Escrever só if (p) quer dizer a mesma coisa: 'se p não é o ponteiro nulo'.

**Versão 1.** Qual linha só escreve em *p quando há lugar?

Já está escrito:

```c
int *p;

p = NULL;
```

Opções: `if (p != NULL) *p = 1;`  `if (p == NULL) *p = 1;`  `*p = 1;`

Resposta certa: `if (p != NULL) *p = 1;`

Se errar:

- respondeu `if (p == NULL) *p = 1;` → Com p == NULL a escrita roda justamente quando não há lugar. A pergunta certa é p != NULL.
- respondeu `*p = 1;` → Sem pergunta nenhuma, a linha vai ao lugar apontado mesmo com p nulo. Antes dela: if (p != NULL)
- qualquer outro erro → A escrita fica guardada pela pergunta: if (p != NULL) *p = 1;

**Versão 2.** Qual linha só escreve em *q quando há lugar?

Já está escrito:

```c
int *q = NULL;
```

Opções: `if (q == NULL) *q = 1;`  `if (q) *q = 1;`  `*q = 1;`

Resposta certa: `if (q) *q = 1;`

Se errar:

- respondeu `if (q == NULL) *q = 1;` → Com q == NULL a escrita roda justamente quando não há lugar. if (q) é que quer dizer 'se q não é o ponteiro nulo'.
- respondeu `*q = 1;` → Sem pergunta nenhuma, a linha vai ao lugar apontado mesmo com q nulo. Antes dela: if (q)
- qualquer outro erro → if (q) quer dizer 'se q não é o ponteiro nulo': if (q) *q = 1;

### Degrau 3 — guiado, digitar

> Com a pergunta antes, o programa não vai aonde não há lugar, e segue.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = NULL;
if (p != NULL) *p = 20;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `20` → p vale NULL, então p != NULL é falso, e a escrita não rodou. idade continua com 15.
- digitou `0` → Nada escreveu zero em idade: a pergunta era falsa, e a linha do if não rodou. idade continua com 15.
- qualquer outro erro → p vale NULL: a pergunta é falsa, *p não é usado, e idade continua com 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = &idade;
if (p != NULL) *p = 20;
printf("%d\n", idade);
```

Resposta certa: `20`

Se errar:

- digitou `15` → p guarda o endereço de idade, então p != NULL é verdade e a escrita rodou: idade passou a guardar 20.
- qualquer outro erro → p aponta para idade: a pergunta é verdadeira, e *p = 20; escreve nela.

### Degrau 4 — prática, montar

_Nome do passo, no fechamento: Só ir a *q quando q aponta para algum lugar_

**Versão 1.** Monte a linha que só lê *q quando q aponta para algum lugar.

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = NULL;
```

Peças: `if (q != NULL)`  `nota = *q;`  `if (q == NULL)`  `if (*q != 0)`

Resposta certa: `if (q != NULL) nota = *q;`

Se errar:

- respondeu `if (*q != 0) nota = *q;` → *q != 0 já vai ao lugar apontado para perguntar. A pergunta tem de ser sobre o ponteiro: if (q != NULL)
- respondeu `if (q == NULL) nota = *q;` → Com q == NULL, a leitura roda justamente quando não há lugar. A pergunta certa é q != NULL.
- respondeu `nota = *q;` → Sem pergunta, a linha vai ao lugar apontado mesmo com q nulo. Antes dela: if (q != NULL)
- qualquer outro erro → A leitura fica guardada pela pergunta sobre o ponteiro: if (q != NULL) nota = *q;

**Versão 2.** Monte a linha que só escreve em *p quando p aponta para algum lugar.

Já está escrito:

```c
int *p;

p = NULL;
```

Peças: `if (p != NULL)`  `*p = 9;`  `if (p == NULL)`  `if (*p != 0)`

Resposta certa: `if (p != NULL) *p = 9;`

Se errar:

- respondeu `if (*p != 0) *p = 9;` → *p != 0 já vai ao lugar apontado para perguntar. A pergunta tem de ser sobre o ponteiro: if (p != NULL)
- respondeu `if (p == NULL) *p = 9;` → Com p == NULL, a escrita roda justamente quando não há lugar. A pergunta certa é p != NULL.
- respondeu `*p = 9;` → Sem pergunta, a linha vai ao lugar apontado mesmo com p nulo. Antes dela: if (p != NULL)
- qualquer outro erro → A escrita fica guardada pela pergunta sobre o ponteiro: if (p != NULL) *p = 9;

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas, posta no fim, iria a um lugar que não existe?

Já está escrito:

```c
int idade;
int *p;
int *q;

p = &idade;
q = NULL;
```

Opções: `*q = 20; — q vale NULL`  `*p = 10; — idade ainda não tinha valor`  `q = p; — copia um endereço`

Resposta certa: `*q = 20; — q vale NULL`

Se errar:

- respondeu `*p = 10; — idade ainda não tinha valor` → p guarda o endereço de idade, que existe desde a declaração: *p = 10; vai a um lugar de verdade. A que não tem para onde ir é *q = 20;
- respondeu `q = p; — copia um endereço` → q = p; só copia o valor de um ponteiro para outro, sem ir a lugar nenhum. A que iria aonde não há lugar é *q = 20;
- qualquer outro erro → q vale NULL: *q = 20; iria a um lugar que não existe.

**Versão 2.** Qual destas linhas, posta no fim, iria a um lugar que não existe?

Já está escrito:

```c
int nota;
int *p;
int *q;

p = NULL;
q = &nota;
```

Opções: `*q = 7; — nota ainda não tinha valor`  `*p = 4; — p vale NULL`  `p = q; — copia um endereço`

Resposta certa: `*p = 4; — p vale NULL`

Se errar:

- respondeu `*q = 7; — nota ainda não tinha valor` → q guarda o endereço de nota, que existe desde a declaração: *q = 7; vai a um lugar de verdade. A que não tem para onde ir é *p = 4;
- respondeu `p = q; — copia um endereço` → p = q; só copia o valor de um ponteiro para outro, sem ir a lugar nenhum. A que iria aonde não há lugar é *p = 4;
- qualquer outro erro → p vale NULL: *p = 4; iria a um lugar que não existe.

### Se errar a pergunta do topo: a revisão

> *p com p valendo NULL manda o programa a um lugar que não existe.
> O que acontece ali não é definido. Por isso se pergunta antes: if (p != NULL)

```c
int idade;
int *p;

idade = 15;
p = NULL;
if (p != NULL) *p = 20;
printf("%d\n", idade);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> Acessar *p com p igual a NULL devolve 0, como se fosse um lugar vazio.

```c
int *p;

p = NULL;
printf("%d\n", *p);
```

**p vale NULL, e o printf pede o valor que mora no lugar apontado. O que o compilador diz dessa linha?**

- Nada: *p com p nulo devolve 0, como um lugar vazio _(é o que a crença espera)_
- Que ela vai a um ponteiro nulo _(é o que a máquina faz)_

O compilador reclama:

```
null pointer dereference
```

_Mensagem do gcc 16.2 com os avisos de fluxo ligados (-O2 -Wnull-dereference). O programa não é executado: o que ele faria nessa linha não é definido._

O que isto mostra: O compilador aponta a linha: ela vai ao lugar apontado por um ponteiro nulo ("null pointer dereference"). Lá não há lugar que devolva 0. O que o programa faz nesse ponto não é definido.
