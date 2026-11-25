# A escada do kc_04 — Dereferência: & e *

Texto para leitura, gerado de `mvp/dominio/escada_kc04.yaml`. Cada degrau tem duas versões: a segunda, com outros valores, aparece quando o mesmo passo volta, como no treino e na reconferência do fim.

## B1 — Só tem número de casa o que ocupa uma casa. Um valor escrito no código não ocupa nenhuma.

### Degrau 1 — guiado, escolher

> O endereço é o número de um lugar da memória.
> Só tem endereço o que ocupa um lugar na memória.

**Versão 1.** De qual destes dá para pedir o endereço?

Já está escrito:

```c
int idade;
idade = 15;
```

Opções: `De idade: ela ocupa um lugar`  `Do 15: é o valor que está guardado`  `Dos dois: o & funciona em qualquer coisa`

Resposta certa: `De idade: ela ocupa um lugar`

Se errar:

- respondeu `Do 15: é o valor que está guardado` → 15 é um valor escrito no código: não ocupa lugar nenhum. Quem ocupa é a variável idade, e é dela o endereço.
- respondeu `Dos dois: o & funciona em qualquer coisa` → O & só funciona no que ocupa um lugar. idade ocupa; o 15 escrito no código, não. _(aponta a crença `ampersand_takes_value`)_
- qualquer outro erro → Só a variável ocupa um lugar. O endereço é de idade, e não do 15.

**Versão 2.** De qual destes dá para pedir o endereço?

Já está escrito:

```c
int nota;
nota = 7;
```

Opções: `De nota: ela ocupa um lugar`  `Do 7: é o valor que está guardado`  `Dos dois: o & funciona em qualquer coisa`

Resposta certa: `De nota: ela ocupa um lugar`

Se errar:

- respondeu `Do 7: é o valor que está guardado` → 7 é um valor escrito no código: não ocupa lugar nenhum. Quem ocupa é a variável nota, e é dela o endereço.
- respondeu `Dos dois: o & funciona em qualquer coisa` → O & só funciona no que ocupa um lugar. nota ocupa; o 7 escrito no código, não. _(aponta a crença `ampersand_takes_value`)_
- qualquer outro erro → Só a variável ocupa um lugar. O endereço é de nota, e não do 7.

### Degrau 2 — guiado, escolher

> Por isso o & só é aceito antes do nome de uma variável.
> Antes de um número escrito no código, o compilador reclama.

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idade;
int *p;
```

Opções: `p = &idade;`  `p = &5;`  `p = &15;`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = &5;` → 5 é um número escrito no código: não ocupa lugar, e não tem endereço. O compilador reclama. Aceita: p = &idade;
- respondeu `p = &15;` → 15 é um número escrito no código: não ocupa lugar, e não tem endereço. O compilador reclama. Aceita: p = &idade;
- qualquer outro erro → O & vai antes de uma variável, que ocupa um lugar: p = &idade;

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int nota;
int *q;
```

Opções: `q = &7;`  `q = &nota;`  `q = &0;`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = &7;` → 7 é um número escrito no código: não ocupa lugar, e não tem endereço. O compilador reclama. Aceita: q = &nota;
- respondeu `q = &0;` → 0 é um número escrito no código: não ocupa lugar, e não tem endereço. O compilador reclama. Aceita: q = &nota;
- qualquer outro erro → O & vai antes de uma variável, que ocupa um lugar: q = &nota;

### Degrau 3 — guiado, montar

> Quando uma função espera um endereço, o que vai na chamada é o endereço de uma variável.
> Para entregar o endereço de um valor, o valor tem de morar numa variável.

**Versão 1.** A função espera um endereço. Chame-a para ela zerar idade.

Já está escrito:

```c
void zera(int *q) { *q = 0; }

int idade;

idade = 15;
```

Peças: `zera(`  `&idade`  `);`  `&15`  `15`

Resposta certa: `zera(&idade);`

Se errar:

- respondeu `zera( &15 );` → 15 é um valor escrito no código, e não tem endereço. Quem tem é a variável onde ele mora: zera(&idade);
- respondeu `zera( 15 );` → 15 é um valor, e a função espera um endereço. O endereço é o da variável: zera(&idade);
- qualquer outro erro → O endereço que existe é o da variável: zera(&idade);

**Versão 2.** A função espera um endereço. Chame-a para ela zerar nota.

Já está escrito:

```c
void zera(int *q) { *q = 0; }

int nota;

nota = 7;
```

Peças: `zera(`  `&nota`  `);`  `&7`  `7`

Resposta certa: `zera(&nota);`

Se errar:

- respondeu `zera( &7 );` → 7 é um valor escrito no código, e não tem endereço. Quem tem é a variável onde ele mora: zera(&nota);
- respondeu `zera( 7 );` → 7 é um valor, e a função espera um endereço. O endereço é o da variável: zera(&nota);
- qualquer outro erro → O endereço que existe é o da variável: zera(&nota);

### Degrau 4 — prática, completar

_Nome do passo, no fechamento: Pedir endereço só do que ocupa um lugar_

**Versão 1.** Complete com algo que tem endereço.

Já está escrito:

```c
int nota;
int *q;

nota = 7;
```

```c
q = &___;
```

Peças: `nota`  `7`  `0`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = &7;` → 7 é um valor escrito no código: não ocupa lugar. Quem ocupa é nota: q = &nota;
- respondeu `q = &0;` → 0 é um valor escrito no código: não ocupa lugar. Quem ocupa é nota: q = &nota;
- qualquer outro erro → Tem endereço o que ocupa um lugar: a variável nota. q = &nota;

**Versão 2.** Complete com algo que tem endereço.

Já está escrito:

```c
int idade;
int *p;

idade = 15;
```

```c
p = &___;
```

Peças: `15`  `idade`  `20`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = &15;` → 15 é um valor escrito no código: não ocupa lugar. Quem ocupa é idade: p = &idade;
- respondeu `p = &20;` → 20 é um valor escrito no código: não ocupa lugar. Quem ocupa é idade: p = &idade;
- qualquer outro erro → Tem endereço o que ocupa um lugar: a variável idade. p = &idade;

### Degrau 5 — prática, escolher

**Versão 1.** Por que o compilador reclama da última linha?

Já está escrito:

```c
int *p;

p = &20;
```

Opções: `Porque 20 não ocupa lugar na memória, e não tem endereço`  `Porque p ainda não recebeu valor`  `Porque faltou o * antes de p`

Resposta certa: `Porque 20 não ocupa lugar na memória, e não tem endereço`

Se errar:

- respondeu `Porque p ainda não recebeu valor` → p estar sem valor não impede de escrever nele. O problema é o &20: um número escrito no código não tem endereço.
- respondeu `Porque faltou o * antes de p` → Para guardar um endereço no ponteiro é p, sem o *, mesmo. O problema é o &20: um número escrito no código não tem endereço.
- qualquer outro erro → O problema é o &20: um número escrito no código não ocupa lugar, e não tem endereço.

**Versão 2.** Por que o compilador reclama da última linha?

Já está escrito:

```c
int *q;

q = &3;
```

Opções: `Porque 3 não ocupa lugar na memória, e não tem endereço`  `Porque q ainda não recebeu valor`  `Porque faltou o * antes de q`

Resposta certa: `Porque 3 não ocupa lugar na memória, e não tem endereço`

Se errar:

- respondeu `Porque q ainda não recebeu valor` → q estar sem valor não impede de escrever nele. O problema é o &3: um número escrito no código não tem endereço.
- respondeu `Porque faltou o * antes de q` → Para guardar um endereço no ponteiro é q, sem o *, mesmo. O problema é o &3: um número escrito no código não tem endereço.
- qualquer outro erro → O problema é o &3: um número escrito no código não ocupa lugar, e não tem endereço.

### Se errar a pergunta do topo: a revisão

> Endereço é de lugar: só tem endereço o que ocupa um lugar na memória.
> Uma variável ocupa. Um número escrito no código, como 5, não: por isso &idade existe, e &5 não.

```c
int idade;
int *p;

p = &idade;
```

### Se a pessoa disser a crença: a prova

Você disse:

> O & funciona em qualquer coisa: dá para pedir o endereço de um número escrito no código.

```c
int *p;

p = &5;
```

**O compilador reclama da última linha?**

- Não: o & dá o endereço do 5 _(é o que a crença espera)_
- Sim: o 5 não ocupa lugar nenhum, e não tem endereço _(é o que a máquina faz)_

O compilador reclama:

```
lvalue required as unary '&' operand
```

_Mensagem do gcc 16.2. Todo compilador de C tem de reclamar desta linha, cada um com as suas palavras._

O que isto mostra: O compilador reclama: o & pede algo que ocupe um lugar, e um número escrito no código não ocupa nenhum. Endereço é de lugar, e não de valor.

## B2 — &x responde o número da casa de x. Nada é copiado: você recebe o número, não o que está guardado.

### Degrau 1 — guiado, escolher

> &idade é o endereço de idade: o número do lugar dela.
> Pedir o endereço de uma variável não copia o que ela guarda.

**Versão 1.** Depois da última linha, em quantos lugares o 15 está guardado?

Já está escrito:

```c
int idade;
int *p;

idade = 15;
p = &idade;
```

Opções: `Em um só: idade`  `Em dois: &idade entregou uma cópia do valor a p`  `Em nenhum: o 15 saiu de idade e foi para p`

Resposta certa: `Em um só: idade`

Se errar:

- respondeu `Em dois: &idade entregou uma cópia do valor a p` → &idade não copia o valor: entrega o endereço. p guarda o número do lugar, e o 15 continua só em idade. _(aponta a crença `ampersand_copies`)_
- respondeu `Em nenhum: o 15 saiu de idade e foi para p` → Nada sai de idade. p recebe o endereço, e o 15 continua onde estava.
- qualquer outro erro → p recebeu o endereço, e não o valor. O 15 está guardado só em idade.

**Versão 2.** Depois da última linha, em quantos lugares o 7 está guardado?

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = &nota;
```

Opções: `Em um só: nota`  `Em dois: &nota entregou uma cópia do valor a q`  `Em nenhum: o 7 saiu de nota e foi para q`

Resposta certa: `Em um só: nota`

Se errar:

- respondeu `Em dois: &nota entregou uma cópia do valor a q` → &nota não copia o valor: entrega o endereço. q guarda o número do lugar, e o 7 continua só em nota. _(aponta a crença `ampersand_copies`)_
- respondeu `Em nenhum: o 7 saiu de nota e foi para q` → Nada sai de nota. q recebe o endereço, e o 7 continua onde estava.
- qualquer outro erro → q recebeu o endereço, e não o valor. O 7 está guardado só em nota.

### Degrau 2 — guiado, digitar

> Como p tem o endereço, e não uma cópia, o que muda em idade aparece por *p.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = &idade;
idade = 16;
printf("%d\n", *p);
```

Resposta certa: `16`

Se errar:

- digitou `15` → p não guardou uma cópia do 15: guardou o endereço. *p foi até idade e achou o que está lá agora, 16.
- qualquer outro erro → p tem o endereço de idade. *p acha o valor de agora: 16.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

nota = 7;
q = &nota;
nota = 9;
printf("%d\n", *q);
```

Resposta certa: `9`

Se errar:

- digitou `7` → q não guardou uma cópia do 7: guardou o endereço. *q foi até nota e achou o que está lá agora, 9.
- qualquer outro erro → q tem o endereço de nota. *q acha o valor de agora: 9.

### Degrau 3 — guiado, digitar

> Com a função é igual: zera(&idade); entrega o endereço, e não uma cópia.
> Por isso o que a função escreve em *q fica na própria idade.

**Versão 1.** Que número este trecho mostra na tela?

```c
void zera(int *q) { *q = 0; }

int idade;

idade = 15;
zera(&idade);
printf("%d\n", idade);
```

Resposta certa: `0`

Se errar:

- digitou `15` → A função não recebeu uma cópia: recebeu o endereço de idade. *q = 0; escreveu na própria idade.
- qualquer outro erro → &idade entrega o endereço. A função escreveu na própria idade: o trecho mostra 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
void zera(int *q) { *q = 0; }

int pontos;

pontos = 3;
zera(&pontos);
printf("%d\n", pontos);
```

Resposta certa: `0`

Se errar:

- digitou `3` → A função não recebeu uma cópia: recebeu o endereço de pontos. *q = 0; escreveu na própria pontos.
- qualquer outro erro → &pontos entrega o endereço. A função escreveu na própria pontos: o trecho mostra 0.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Distinguir a cópia do valor do endereço_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
p = &idade;
nota = *p;
*p = 20;
printf("%d\n", nota);
```

Resposta certa: `15`

Se errar:

- digitou `20` → nota = *p; copiou o valor que estava em idade naquele momento: 15. Depois *p = 20; mudou idade, e a cópia em nota ficou como estava.
- qualquer outro erro → nota recebeu uma cópia do valor, 15. Quem tem o endereço é p; nota não muda quando idade muda.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
q = &pontos;
ano = *q;
*q = 8;
printf("%d\n", ano);
```

Resposta certa: `3`

Se errar:

- digitou `8` → ano = *q; copiou o valor que estava em pontos naquele momento: 3. Depois *q = 8; mudou pontos, e a cópia em ano ficou como estava.
- qualquer outro erro → ano recebeu uma cópia do valor, 3. Quem tem o endereço é q; ano não muda quando pontos muda.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas, posta no fim, mudaria idade?

Já está escrito:

```c
int idade;
int nota;
int *p;

idade = 15;
nota = idade;
p = &idade;
```

Opções: `*p = 99; — p tem o endereço de idade`  `nota = 99; — nota recebeu o valor de idade`  `Qualquer uma: nota e p vieram de idade`

Resposta certa: `*p = 99; — p tem o endereço de idade`

Se errar:

- respondeu `nota = 99; — nota recebeu o valor de idade` → nota recebeu uma cópia do valor, e é outra variável: mexer nela não mexe em idade. Quem chega em idade é *p.
- respondeu `Qualquer uma: nota e p vieram de idade` → nota guarda uma cópia do valor; p guarda o endereço. Só pelo endereço se chega na própria idade: *p = 99;
- qualquer outro erro → nota tem uma cópia; p tem o endereço. Quem muda idade é *p = 99;

**Versão 2.** Qual destas linhas, posta no fim, mudaria pontos?

Já está escrito:

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = pontos;
q = &pontos;
```

Opções: `ano = 99; — ano recebeu o valor de pontos`  `*q = 99; — q tem o endereço de pontos`  `Qualquer uma: ano e q vieram de pontos`

Resposta certa: `*q = 99; — q tem o endereço de pontos`

Se errar:

- respondeu `ano = 99; — ano recebeu o valor de pontos` → ano recebeu uma cópia do valor, e é outra variável: mexer nela não mexe em pontos. Quem chega em pontos é *q.
- respondeu `Qualquer uma: ano e q vieram de pontos` → ano guarda uma cópia do valor; q guarda o endereço. Só pelo endereço se chega na própria pontos: *q = 99;
- qualquer outro erro → ano tem uma cópia; q tem o endereço. Quem muda pontos é *q = 99;

### Se errar a pergunta do topo: a revisão

> &idade é o endereço de idade. Pedir o endereço não copia o valor.
> Quem recebe &idade recebe o caminho até a própria idade: o que escrever por ele fica nela.

```c
int idade;
int *p;

idade = 15;
p = &idade;
*p = 16;
printf("%d\n", idade);
```

A máquina imprime:

```
16
```

### Se a pessoa disser a crença: a prova

Você disse:

> &x entrega uma cópia de x, e é a cópia que a função recebe.

```c
void marca(int *q) { *q = 9; }

int nota;

nota = 7;
marca(&nota);
printf("%d\n", nota);
```

**A chamada entrega &nota à função, e a função escreve 9 no que recebeu. O que o trecho imprime?**

- 7 _(é o que a crença espera)_
- 9 _(é o que a máquina faz)_

A máquina imprime:

```
9
```

O que isto mostra: Saiu 9. Se &nota entregasse uma cópia, a função teria escrito na cópia, e nota continuaria com 7. O & entrega o endereço: a função chegou na própria nota.

## B3 — O que está escrito no papel dentro de p é um número de casa.

### Degrau 1 — guiado, escolher

> O que um ponteiro guarda é um endereço: o número de um lugar.
> O valor que mora naquele lugar não está dentro do ponteiro.

**Versão 1.** idade guarda 42. O que está guardado em p?

Já está escrito:

```c
int idade;
int *p;

idade = 42;
p = &idade;
```

Opções: `O endereço de idade`  `O 42: o ponteiro é o próprio dado`  `O nome idade`

Resposta certa: `O endereço de idade`

Se errar:

- respondeu `O 42: o ponteiro é o próprio dado` → O 42 está guardado em idade. Dentro de p há o endereço: o número do lugar onde idade fica. _(aponta a crença `pointer_is_data`)_
- respondeu `O nome idade` → Ponteiro não guarda nome. Guarda o endereço: o número do lugar onde idade fica.
- qualquer outro erro → p guarda o endereço de idade. O 42 fica em idade.

**Versão 2.** nota guarda 9. O que está guardado em q?

Já está escrito:

```c
int nota;
int *q;

nota = 9;
q = &nota;
```

Opções: `O endereço de nota`  `O 9: o ponteiro é o próprio dado`  `O nome nota`

Resposta certa: `O endereço de nota`

Se errar:

- respondeu `O 9: o ponteiro é o próprio dado` → O 9 está guardado em nota. Dentro de q há o endereço: o número do lugar onde nota fica. _(aponta a crença `pointer_is_data`)_
- respondeu `O nome nota` → Ponteiro não guarda nome. Guarda o endereço: o número do lugar onde nota fica.
- qualquer outro erro → q guarda o endereço de nota. O 9 fica em nota.

### Degrau 2 — guiado, escolher

> São duas coisas diferentes: o nome do ponteiro dá o endereço guardado.
> Com o * na frente, ele dá o valor que mora lá.

**Versão 1.** Qual destas vale 42?

Já está escrito:

```c
int idade;
int *p;

idade = 42;
p = &idade;
```

Opções: `*p`  `p`  `&p`

Resposta certa: `*p`

Se errar:

- respondeu `p` → p, sem o *, é o endereço guardado. O 42 é o valor que mora lá: *p
- respondeu `&p` → &p é o endereço do próprio ponteiro. O 42 é o valor que mora no endereço guardado: *p
- qualquer outro erro → p é o endereço; *p é o valor que mora lá, 42.

**Versão 2.** Qual destas vale 9?

Já está escrito:

```c
int nota;
int *q;

nota = 9;
q = &nota;
```

Opções: `q`  `*q`  `&q`

Resposta certa: `*q`

Se errar:

- respondeu `q` → q, sem o *, é o endereço guardado. O 9 é o valor que mora lá: *q
- respondeu `&q` → &q é o endereço do próprio ponteiro. O 9 é o valor que mora no endereço guardado: *q
- qualquer outro erro → q é o endereço; *q é o valor que mora lá, 9.

### Degrau 3 — guiado, completar

> Por isso o que se guarda num ponteiro é um endereço, e não um valor.

**Versão 1.** Complete para p receber o que um ponteiro guarda.

Já está escrito:

```c
int idade;
int *p;

idade = 42;
```

```c
p = ___;
```

Peças: `&idade`  `idade`  `42`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = idade;` → idade, sem o &, é o valor guardado, e um ponteiro guarda endereço. O compilador reclama. O certo é p = &idade;
- respondeu `p = 42;` → 42 é um valor, e um ponteiro guarda endereço. O compilador reclama. O certo é p = &idade;
- qualquer outro erro → Um ponteiro guarda endereço: p = &idade;

**Versão 2.** Complete para q receber o que um ponteiro guarda.

Já está escrito:

```c
int nota;
int *q;

nota = 9;
```

```c
q = ___;
```

Peças: `&nota`  `nota`  `9`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = nota;` → nota, sem o &, é o valor guardado, e um ponteiro guarda endereço. O compilador reclama. O certo é q = &nota;
- respondeu `q = 9;` → 9 é um valor, e um ponteiro guarda endereço. O compilador reclama. O certo é q = &nota;
- qualquer outro erro → Um ponteiro guarda endereço: q = &nota;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Copiar um ponteiro é copiar o endereço_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;
int *q;

idade = 42;
p = &idade;
q = p;
*q = 50;
printf("%d\n", *p);
```

Resposta certa: `50`

Se errar:

- digitou `42` → q = p; copiou o endereço, e não o 42. Os dois ponteiros guardam o endereço de idade: *q = 50; mudou idade, e *p acha 50.
- qualquer outro erro → q = p; copia o endereço guardado. Os dois apontam para idade, que passou a guardar 50.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *p;
int *q;

nota = 9;
q = &nota;
p = q;
*p = 4;
printf("%d\n", *q);
```

Resposta certa: `4`

Se errar:

- digitou `9` → p = q; copiou o endereço, e não o 9. Os dois ponteiros guardam o endereço de nota: *p = 4; mudou nota, e *q acha 4.
- qualquer outro erro → p = q; copia o endereço guardado. Os dois apontam para nota, que passou a guardar 4.

### Degrau 5 — prática, montar

**Versão 1.** Faça q guardar o endereço de nota, e mostre na tela o valor que mora lá.

Já está escrito:

```c
int nota;
int *q;

nota = 9;
```

Peças: `q = &nota;`  `printf("%d\n", *q);`  `printf("%d\n", q);`  `q = nota;`

Resposta certa: `q = &nota; printf("%d\n", *q);`

Se errar:

- respondeu `q = &nota; printf("%d\n", q);` → q, sem o *, é o endereço guardado, e o %d espera um número inteiro. O valor que mora lá é *q.
- respondeu `q = nota; printf("%d\n", *q);` → nota, sem o &, é o valor, e um ponteiro guarda endereço. O certo é q = &nota;
- respondeu `printf("%d\n", *q); q = &nota;` → Nessa ordem o printf usa *q antes de q receber o endereço. Primeiro q = &nota;
- qualquer outro erro → O ponteiro recebe o endereço, e o valor se lê com o *: q = &nota; e printf("%d\n", *q);

**Versão 2.** Faça p guardar o endereço de idade, e mostre na tela o valor que mora lá.

Já está escrito:

```c
int idade;
int *p;

idade = 42;
```

Peças: `p = &idade;`  `printf("%d\n", *p);`  `printf("%d\n", p);`  `p = idade;`

Resposta certa: `p = &idade; printf("%d\n", *p);`

Se errar:

- respondeu `p = &idade; printf("%d\n", p);` → p, sem o *, é o endereço guardado, e o %d espera um número inteiro. O valor que mora lá é *p.
- respondeu `p = idade; printf("%d\n", *p);` → idade, sem o &, é o valor, e um ponteiro guarda endereço. O certo é p = &idade;
- respondeu `printf("%d\n", *p); p = &idade;` → Nessa ordem o printf usa *p antes de p receber o endereço. Primeiro p = &idade;
- qualquer outro erro → O ponteiro recebe o endereço, e o valor se lê com o *: p = &idade; e printf("%d\n", *p);

### Se errar a pergunta do topo: a revisão

> Dentro de um ponteiro há um endereço, e não o valor apontado.
> p é o endereço guardado. *p é o valor que mora naquele endereço.

```c
int idade;
int *p;

idade = 42;
p = &idade;
printf("%d\n", *p);
```

A máquina imprime:

```
42
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro é o próprio dado: o que está dentro dele é o valor, não o endereço.

```c
int nota;
int *q;

nota = 7;
q = &nota;
nota = 9;
printf("%d\n", *q);
```

**Quando a linha q = &nota; rodou, nota guardava 7. Depois nota mudou para 9, e ninguém mexeu em q. O que o trecho imprime?**

- 9 _(é o que a máquina faz)_
- 7 _(é o que a crença espera)_

A máquina imprime:

```
9
```

O que isto mostra: Saiu 9. Se o ponteiro fosse o próprio dado, q teria ficado com o 7. O que está dentro de q é o endereço: *q foi até nota e achou o que está lá agora.

## I1 — Então *p é a viagem: vai até o número do papel e mexe no que tem naquela casa.

### Degrau 1 — guiado, escolher

> O * diante de um ponteiro quer dizer: vá até o endereço guardado nele.
> Não é outro nome da variável: é um caminho, e o destino é o endereço guardado naquele momento.

**Versão 1.** O que o *p da última linha faz?

Já está escrito:

```c
int idade;
int *p;

idade = 15;
p = &idade;
printf("%d\n", *p);
```

Opções: `Vai até o endereço guardado em p, e lê o que está lá`  `Nada: *p é só outro nome de idade`  `Entrega o endereço guardado em p`

Resposta certa: `Vai até o endereço guardado em p, e lê o que está lá`

Se errar:

- respondeu `Nada: *p é só outro nome de idade` → *p não é um nome: é um caminho. Ele vai ao endereço que estiver em p, e se p mudar de endereço, *p vai a outro lugar. _(aponta a crença `pointer_is_just_a_name`)_
- respondeu `Entrega o endereço guardado em p` → Quem é o endereço guardado é p, sem o *. Com o *, a linha vai até lá e lê o valor.
- qualquer outro erro → *p vai até o endereço guardado em p e lê o que está lá: o valor de idade.

**Versão 2.** O que o *q da última linha faz?

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = &nota;
printf("%d\n", *q);
```

Opções: `Vai até o endereço guardado em q, e lê o que está lá`  `Nada: *q é só outro nome de nota`  `Entrega o endereço guardado em q`

Resposta certa: `Vai até o endereço guardado em q, e lê o que está lá`

Se errar:

- respondeu `Nada: *q é só outro nome de nota` → *q não é um nome: é um caminho. Ele vai ao endereço que estiver em q, e se q mudar de endereço, *q vai a outro lugar. _(aponta a crença `pointer_is_just_a_name`)_
- respondeu `Entrega o endereço guardado em q` → Quem é o endereço guardado é q, sem o *. Com o *, a linha vai até lá e lê o valor.
- qualquer outro erro → *q vai até o endereço guardado em q e lê o que está lá: o valor de nota.

### Degrau 2 — guiado, digitar

> A prova de que é um caminho: troque o endereço em p, e o mesmo *p vai a outro lugar.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &idade;
p = &nota;
printf("%d\n", *p);
```

Resposta certa: `7`

Se errar:

- digitou `15` → p deixou de guardar o endereço de idade e passou a guardar o de nota. *p vai aonde p manda agora: 7.
- qualquer outro erro → p guarda agora o endereço de nota. *p vai até lá: 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &ano;
q = &pontos;
printf("%d\n", *q);
```

Resposta certa: `3`

Se errar:

- digitou `2026` → q deixou de guardar o endereço de ano e passou a guardar o de pontos. *q vai aonde q manda agora: 3.
- qualquer outro erro → q guarda agora o endereço de pontos. *q vai até lá: 3.

### Degrau 3 — guiado, digitar

> O caminho também serve para escrever: *p = 20; vai até o endereço guardado e escreve lá.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &nota;
*p = 20;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `20` → *p foi aonde p mandava: nota. idade não foi tocada, e continua com 15.
- digitou `7` → O 7 era de nota, que virou 20. O printf mostra idade, que ninguém tocou: 15.
- qualquer outro erro → p guarda o endereço de nota. *p = 20; escreveu lá, e idade continua com 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &pontos;
*q = 8;
printf("%d\n", ano);
```

Resposta certa: `2026`

Se errar:

- digitou `8` → *q foi aonde q mandava: pontos. ano não foi tocada, e continua com 2026.
- digitou `3` → O 3 era de pontos, que virou 8. O printf mostra ano, que ninguém tocou: 2026.
- qualquer outro erro → q guarda o endereço de pontos. *q = 8; escreveu lá, e ano continua com 2026.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Seguir *p quando o ponteiro troca de alvo_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &idade;
*p = 30;
p = &nota;
*p = 40;
printf("%d\n", idade);
```

Resposta certa: `30`

Se errar:

- digitou `40` → O segundo *p foi para nota: p tinha trocado de endereço. idade ficou com o 30 da primeira viagem.
- digitou `15` → *p = 30; rodou enquanto p guardava o endereço de idade, e escreveu 30 nela.
- qualquer outro erro → O primeiro *p foi a idade e escreveu 30. O segundo foi a nota. idade guarda 30.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &ano;
*q = 2027;
q = &pontos;
*q = 8;
printf("%d\n", ano);
```

Resposta certa: `2027`

Se errar:

- digitou `8` → O segundo *q foi para pontos: q tinha trocado de endereço. ano ficou com o 2027 da primeira viagem.
- digitou `2026` → *q = 2027; rodou enquanto q guardava o endereço de ano, e escreveu 2027 nela.
- qualquer outro erro → O primeiro *q foi a ano e escreveu 2027. O segundo foi a pontos. ano guarda 2027.

### Degrau 5 — prática, montar

**Versão 1.** Sem usar o nome nota, escreva 9 nela e depois mostre o valor na tela.

Já está escrito:

```c
int nota;
int *p;

nota = 7;
p = &nota;
```

Peças: `*p = 9;`  `printf("%d\n", *p);`  `p = 9;`  `printf("%d\n", p);`

Resposta certa: `*p = 9; printf("%d\n", *p);`

Se errar:

- respondeu `p = 9; printf("%d\n", *p);` → p = 9; tentaria trocar o endereço guardado. Para ir até nota e escrever, é *p = 9;
- respondeu `*p = 9; printf("%d\n", p);` → p, sem o *, é o endereço. Para ler o que mora lá, a viagem é *p.
- respondeu `printf("%d\n", *p); *p = 9;` → Nessa ordem o printf lê nota antes de o 9 entrar. Primeiro *p = 9; depois o printf.
- qualquer outro erro → As duas linhas vão até nota pelo ponteiro: *p = 9; e printf("%d\n", *p);

**Versão 2.** Sem usar o nome idade, escreva 16 nela e depois mostre o valor na tela.

Já está escrito:

```c
int idade;
int *q;

idade = 15;
q = &idade;
```

Peças: `*q = 16;`  `printf("%d\n", *q);`  `q = 16;`  `printf("%d\n", q);`

Resposta certa: `*q = 16; printf("%d\n", *q);`

Se errar:

- respondeu `q = 16; printf("%d\n", *q);` → q = 16; tentaria trocar o endereço guardado. Para ir até idade e escrever, é *q = 16;
- respondeu `*q = 16; printf("%d\n", q);` → q, sem o *, é o endereço. Para ler o que mora lá, a viagem é *q.
- respondeu `printf("%d\n", *q); *q = 16;` → Nessa ordem o printf lê idade antes de o 16 entrar. Primeiro *q = 16; depois o printf.
- qualquer outro erro → As duas linhas vão até idade pelo ponteiro: *q = 16; e printf("%d\n", *q);

### Se errar a pergunta do topo: a revisão

> *p não é outro nome da variável: é ir até o endereço guardado em p.
> Se p passa a guardar outro endereço, o mesmo *p vai a outro lugar.

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &idade;
p = &nota;
printf("%d\n", *p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> p é só outro nome da variável apontada: *p não vai a lugar nenhum, é o mesmo nome escrito diferente.

```c
int idade;
int nota;
int *p;

idade = 15;
p = &idade;
p = &nota;
*p = 9;
printf("%d\n", idade);
```

**p guardou o endereço de idade, e depois o de nota. A linha *p = 9; vem por último. O que o trecho imprime?**

- 9 _(é o que a crença espera)_
- 15 _(é o que a máquina faz)_

A máquina imprime:

```
15
```

O que isto mostra: Saiu 15. Se *p fosse outro nome de idade, o 9 teria ido para ela. *p é um caminho: foi aonde o endereço guardado em p mandava naquele momento, que era nota.

## I2 — *p = 7 troca o que tem dentro da casa visitada. O papel de p não muda.

### Degrau 1 — guiado, escolher

> Com o * na frente, a escrita vai para o lugar apontado.
> O ponteiro em si não é escrito: continua guardando o mesmo endereço.

**Versão 1.** Depois da última linha, o que mudou?

Já está escrito:

```c
int idade;
int *p;

idade = 15;
p = &idade;
*p = 7;
```

Opções: `idade, que passou a guardar 7. p continua igual`  `p, que passou a guardar 7: mexer em *p mexe no ponteiro`  `Os dois: idade e p passaram a guardar 7`

Resposta certa: `idade, que passou a guardar 7. p continua igual`

Se errar:

- respondeu `p, que passou a guardar 7: mexer em *p mexe no ponteiro` → *p = 7; escreve no lugar apontado, que é idade. O ponteiro continua guardando o endereço de idade, como antes. _(aponta a crença `star_binds_to_the_pointer`)_
- respondeu `Os dois: idade e p passaram a guardar 7` → Só um lugar recebeu o 7: o apontado, que é idade. p continua guardando o endereço, e não um 7.
- qualquer outro erro → *p = 7; mudou idade. O ponteiro continua guardando o mesmo endereço.

**Versão 2.** Depois da última linha, o que mudou?

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = &nota;
*q = 9;
```

Opções: `nota, que passou a guardar 9. q continua igual`  `q, que passou a guardar 9: mexer em *q mexe no ponteiro`  `Os dois: nota e q passaram a guardar 9`

Resposta certa: `nota, que passou a guardar 9. q continua igual`

Se errar:

- respondeu `q, que passou a guardar 9: mexer em *q mexe no ponteiro` → *q = 9; escreve no lugar apontado, que é nota. O ponteiro continua guardando o endereço de nota, como antes. _(aponta a crença `star_binds_to_the_pointer`)_
- respondeu `Os dois: nota e q passaram a guardar 9` → Só um lugar recebeu o 9: o apontado, que é nota. q continua guardando o endereço, e não um 9.
- qualquer outro erro → *q = 9; mudou nota. O ponteiro continua guardando o mesmo endereço.

### Degrau 2 — guiado, digitar

> Como o ponteiro não mudou, um segundo *p vai ao mesmo lugar do primeiro.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = &idade;
*p = 7;
*p = 8;
printf("%d\n", idade);
```

Resposta certa: `8`

Se errar:

- digitou `7` → O segundo *p foi ao mesmo lugar do primeiro: p não tinha mudado. O 8 entrou por cima do 7.
- digitou `15` → As duas escritas foram em idade, pelo ponteiro. Ficou a última: 8.
- qualquer outro erro → As duas escritas vão ao mesmo lugar, idade. Fica a última: 8.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

nota = 7;
q = &nota;
*q = 5;
*q = 6;
printf("%d\n", nota);
```

Resposta certa: `6`

Se errar:

- digitou `5` → O segundo *q foi ao mesmo lugar do primeiro: q não tinha mudado. O 6 entrou por cima do 5.
- digitou `7` → As duas escritas foram em nota, pelo ponteiro. Ficou a última: 6.
- qualquer outro erro → As duas escritas vão ao mesmo lugar, nota. Fica a última: 6.

### Degrau 3 — guiado, escolher

> Quem muda o ponteiro é a escrita sem o *, com um endereço novo do lado direito.

**Versão 1.** Qual linha faz p passar a apontar para nota?

Já está escrito:

```c
int idade;
int nota;
int *p;

p = &idade;
```

Opções: `p = &nota;`  `*p = nota;`  `*p = &nota;`

Resposta certa: `p = &nota;`

Se errar:

- respondeu `*p = nota;` → *p = nota; copia o valor de nota para dentro de idade, e p continua apontando para idade. Para trocar o alvo: p = &nota;
- respondeu `*p = &nota;` → *p é o lugar apontado, que guarda um int, e não um endereço. O compilador reclama. Para trocar o alvo: p = &nota;
- qualquer outro erro → O ponteiro muda quando a escrita é nele, sem o *: p = &nota;

**Versão 2.** Qual linha faz q passar a apontar para ano?

Já está escrito:

```c
int pontos;
int ano;
int *q;

q = &pontos;
```

Opções: `*q = ano;`  `q = &ano;`  `*q = &ano;`

Resposta certa: `q = &ano;`

Se errar:

- respondeu `*q = ano;` → *q = ano; copia o valor de ano para dentro de pontos, e q continua apontando para pontos. Para trocar o alvo: q = &ano;
- respondeu `*q = &ano;` → *q é o lugar apontado, que guarda um int, e não um endereço. O compilador reclama. Para trocar o alvo: q = &ano;
- qualquer outro erro → O ponteiro muda quando a escrita é nele, sem o *: q = &ano;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Escrever em *p sem mexer no ponteiro_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &idade;
*p = nota;
printf("%d\n", idade);
```

Resposta certa: `7`

Se errar:

- digitou `15` → *p = nota; escreveu em idade o valor que estava em nota: 7. O ponteiro continuou apontando para idade.
- qualquer outro erro → *p = nota; copia o valor de nota para o lugar apontado, que é idade: 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &ano;
*q = pontos;
printf("%d\n", ano);
```

Resposta certa: `3`

Se errar:

- digitou `2026` → *q = pontos; escreveu em ano o valor que estava em pontos: 3. O ponteiro continuou apontando para ano.
- qualquer outro erro → *q = pontos; copia o valor de pontos para o lugar apontado, que é ano: 3.

### Degrau 5 — prática, montar

**Versão 1.** p aponta para idade. Escreva 30 em idade pelo ponteiro e, depois, faça p apontar para nota.

Já está escrito:

```c
int idade;
int nota;
int *p;

p = &idade;
```

Peças: `*p = 30;`  `p = &nota;`  `p = 30;`  `*p = &nota;`

Resposta certa: `*p = 30; p = &nota;`

Se errar:

- respondeu `p = &nota; *p = 30;` → Nessa ordem p troca de alvo primeiro, e o 30 vai parar em nota. Primeiro *p = 30; depois p = &nota;
- respondeu `p = 30; p = &nota;` → p = 30; mexeria no ponteiro, e não em idade. Escrever no lugar apontado é com o *: *p = 30;
- respondeu `*p = 30; *p = &nota;` → *p = &nota; tentaria guardar um endereço dentro de idade. Quem recebe o endereço é o ponteiro: p = &nota;
- qualquer outro erro → Com o * se escreve no lugar apontado; sem o *, no ponteiro: *p = 30; e p = &nota;

**Versão 2.** q aponta para pontos. Escreva 8 em pontos pelo ponteiro e, depois, faça q apontar para ano.

Já está escrito:

```c
int pontos;
int ano;
int *q;

q = &pontos;
```

Peças: `*q = 8;`  `q = &ano;`  `q = 8;`  `*q = &ano;`

Resposta certa: `*q = 8; q = &ano;`

Se errar:

- respondeu `q = &ano; *q = 8;` → Nessa ordem q troca de alvo primeiro, e o 8 vai parar em ano. Primeiro *q = 8; depois q = &ano;
- respondeu `q = 8; q = &ano;` → q = 8; mexeria no ponteiro, e não em pontos. Escrever no lugar apontado é com o *: *q = 8;
- respondeu `*q = 8; *q = &ano;` → *q = &ano; tentaria guardar um endereço dentro de pontos. Quem recebe o endereço é o ponteiro: q = &ano;
- qualquer outro erro → Com o * se escreve no lugar apontado; sem o *, no ponteiro: *q = 8; e q = &ano;

### Se errar a pergunta do topo: a revisão

> *p = 7; escreve no lugar apontado. O ponteiro continua guardando o mesmo endereço.
> Para o ponteiro mudar, a escrita tem de ser nele, sem o *: p = &nota;

```c
int idade;
int *p;

p = &idade;
*p = 7;
*p = 8;
printf("%d\n", idade);
```

A máquina imprime:

```
8
```

### Se a pessoa disser a crença: a prova

Você disse:

> Mexer em *p mexe no ponteiro: *p++ anda com o que está dentro da casa.

```c
int idade;
int *p;

p = &idade;
printf("%p\n", (void *)p);
*p = 20;
printf("%p\n", (void *)p);
```

**Os dois printf mostram o endereço guardado em p: um antes e um depois da linha *p = 20;. O que eles mostram?**

- O mesmo endereço, duas vezes _(é o que a máquina faz)_
- Dois endereços diferentes: *p = 20; mexeu no ponteiro _(é o que a crença espera)_

A máquina imprime:

```
0x1000
0x1000
```

_O número do lugar muda de máquina para máquina; aqui ele aparece como um número de exemplo. O que foi conferido é que as duas linhas saem com o mesmo endereço._

O que isto mostra: O endereço guardado em p é o mesmo antes e depois. *p = 20; escreveu no lugar apontado, que é idade; no ponteiro, ninguém mexeu.

## I3 — & pergunta onde está, * vai até lá. Um desfaz o outro, e *(&x) é a própria x.

### Degrau 1 — guiado, escolher

> O & pergunta: onde está esta variável?
> O * diz: vá até este endereço, e veja o que mora lá.

**Versão 1.** O que é *(&idade)?

Já está escrito:

```c
int idade;
idade = 7;
```

Opções: `A própria idade`  `O endereço de idade`  `Uma cópia de idade`

Resposta certa: `A própria idade`

Se errar:

- respondeu `O endereço de idade` → O endereço é só o &idade. O * na frente vai até esse endereço, e o que está lá é a própria idade.
- respondeu `Uma cópia de idade` → Nada foi copiado: o & deu o endereço, e o * foi até ele. Chega-se na própria idade.
- qualquer outro erro → O & dá o endereço, e o * vai até ele: *(&idade) é a própria idade.

**Versão 2.** O que é *(&nota)?

Já está escrito:

```c
int nota;
nota = 4;
```

Opções: `A própria nota`  `O endereço de nota`  `Uma cópia de nota`

Resposta certa: `A própria nota`

Se errar:

- respondeu `O endereço de nota` → O endereço é só o &nota. O * na frente vai até esse endereço, e o que está lá é a própria nota.
- respondeu `Uma cópia de nota` → Nada foi copiado: o & deu o endereço, e o * foi até ele. Chega-se na própria nota.
- qualquer outro erro → O & dá o endereço, e o * vai até ele: *(&nota) é a própria nota.

### Degrau 2 — guiado, digitar

> Como *(&idade) é a própria idade, escrever ali é escrever em idade.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;

idade = 7;
*(&idade) = 9;
printf("%d\n", idade);
```

Resposta certa: `9`

Se errar:

- digitou `7` → *(&idade) é a própria idade: o * desfez o &. A linha escreveu 9 em idade.
- qualquer outro erro → *(&idade) = 9; é o mesmo que idade = 9; O trecho mostra 9.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;

nota = 4;
*(&nota) = 6;
printf("%d\n", nota);
```

Resposta certa: `6`

Se errar:

- digitou `4` → *(&nota) é a própria nota: o * desfez o &. A linha escreveu 6 em nota.
- qualquer outro erro → *(&nota) = 6; é o mesmo que nota = 6; O trecho mostra 6.

### Degrau 3 — guiado, escolher

> Cada coisa tem o seu lugar: o endereço se guarda no ponteiro, e o valor se escreve no lugar apontado.
> Sem o *, a linha mexe no ponteiro; com o *, no lugar apontado.

**Versão 1.** Em qual destes o endereço de idade fica guardado?

Já está escrito:

```c
int idade;
int *p;

p = &idade;
```

Opções: `Em p: o ponteiro é quem guarda o endereço`  `Em *p: é em *p que se guarda o endereço`  `Em &p`

Resposta certa: `Em p: o ponteiro é quem guarda o endereço`

Se errar:

- respondeu `Em *p: é em *p que se guarda o endereço` → *p é o lugar apontado, que guarda um int. O endereço fica no próprio ponteiro, sem o *: p = &idade; _(aponta a crença `star_assigns_pointer`)_
- respondeu `Em &p` → &p é o endereço do ponteiro, e não um lugar onde se guarda. O endereço de idade fica em p.
- qualquer outro erro → O endereço fica guardado no ponteiro, sem o *: em p.

**Versão 2.** Em qual destes o endereço de nota fica guardado?

Já está escrito:

```c
int nota;
int *q;

q = &nota;
```

Opções: `Em q: o ponteiro é quem guarda o endereço`  `Em *q: é em *q que se guarda o endereço`  `Em &q`

Resposta certa: `Em q: o ponteiro é quem guarda o endereço`

Se errar:

- respondeu `Em *q: é em *q que se guarda o endereço` → *q é o lugar apontado, que guarda um int. O endereço fica no próprio ponteiro, sem o *: q = &nota; _(aponta a crença `star_assigns_pointer`)_
- respondeu `Em &q` → &q é o endereço do ponteiro, e não um lugar onde se guarda. O endereço de nota fica em q.
- qualquer outro erro → O endereço fica guardado no ponteiro, sem o *: em q.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Guardar o endereço no ponteiro, e não em *p_

**Versão 1.** Uma destas linhas faz o compilador reclamar. Qual?

Já está escrito:

```c
int idade;
int *p;

p = &idade;
```

Opções: `*p = &idade;`  `*p = 9;`  `p = &idade;`

Resposta certa: `*p = &idade;`

Se errar:

- respondeu `*p = 9;` → *p = 9; escreve um int no lugar apontado, que é de int: combina. A que não combina é *p = &idade;
- respondeu `p = &idade;` → p = &idade; guarda um endereço no ponteiro: combina. A que não combina é *p = &idade;
- qualquer outro erro → *p é lugar de int, e &idade é um endereço: *p = &idade; não combina.

**Versão 2.** Uma destas linhas faz o compilador reclamar. Qual?

Já está escrito:

```c
int nota;
int *q;

q = &nota;
```

Opções: `q = &nota;`  `*q = 6;`  `*q = &nota;`

Resposta certa: `*q = &nota;`

Se errar:

- respondeu `q = &nota;` → q = &nota; guarda um endereço no ponteiro: combina. A que não combina é *q = &nota;
- respondeu `*q = 6;` → *q = 6; escreve um int no lugar apontado, que é de int: combina. A que não combina é *q = &nota;
- qualquer outro erro → *q é lugar de int, e &nota é um endereço: *q = &nota; não combina.

### Degrau 5 — prática, montar

**Versão 1.** Faça p apontar para nota e, pelo ponteiro, escreva 5 nela.

Já está escrito:

```c
int nota;
int *p;
```

Peças: `p = &nota;`  `*p = 5;`  `*p = &nota;`  `p = 5;`

Resposta certa: `p = &nota; *p = 5;`

Se errar:

- respondeu `*p = &nota; *p = 5;` → O endereço se guarda no ponteiro, sem o *. *p é o lugar apontado, que guarda um int: p = &nota;
- respondeu `*p = 5; p = &nota;` → Nessa ordem *p = 5; roda antes de p receber o endereço. Primeiro p = &nota;
- respondeu `p = &nota; p = 5;` → p = 5; trocaria o endereço guardado por 5. Para escrever em nota pelo ponteiro: *p = 5;
- qualquer outro erro → O endereço vai em p, e o valor vai em *p: p = &nota; e *p = 5;

**Versão 2.** Faça q apontar para idade e, pelo ponteiro, escreva 16 nela.

Já está escrito:

```c
int idade;
int *q;
```

Peças: `q = &idade;`  `*q = 16;`  `*q = &idade;`  `q = 16;`

Resposta certa: `q = &idade; *q = 16;`

Se errar:

- respondeu `*q = &idade; *q = 16;` → O endereço se guarda no ponteiro, sem o *. *q é o lugar apontado, que guarda um int: q = &idade;
- respondeu `*q = 16; q = &idade;` → Nessa ordem *q = 16; roda antes de q receber o endereço. Primeiro q = &idade;
- respondeu `q = &idade; q = 16;` → q = 16; trocaria o endereço guardado por 16. Para escrever em idade pelo ponteiro: *q = 16;
- qualquer outro erro → O endereço vai em q, e o valor vai em *q: q = &idade; e *q = 16;

### Se errar a pergunta do topo: a revisão

> O & pergunta onde a variável está. O * vai até um endereço. Um desfaz o outro.
> Por isso *(&idade) é a própria idade — e o endereço se guarda em p, nunca em *p.

```c
int idade;

idade = 7;
printf("%d\n", *(&idade));
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Na expressão, *p designa o próprio ponteiro — é em *p que se guarda o endereço.

```c
int idade;
int *p;

*p = &idade;
```

**O compilador reclama da última linha?**

- Sim: *p é o lugar apontado, que guarda um int, e não um endereço _(é o que a máquina faz)_
- Não: é em *p que o endereço fica guardado _(é o que a crença espera)_

O compilador reclama:

```
makes integer from pointer without a cast
```

_Mensagem do gcc 16.2. Todo compilador de C tem de reclamar desta linha, cada um com as suas palavras._

O que isto mostra: O compilador reclama: *p é o lugar apontado, feito para um int, e &idade é um endereço. Quem guarda o endereço é o ponteiro, sem o *: p = &idade;
