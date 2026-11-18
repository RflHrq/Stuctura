# A escada do kc_12 — Ponteiro pendente por escopo

Texto para leitura, gerado de `mvp/dominio/escada_kc12.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — As caixas criadas dentro de uma função existem enquanto ela está rodando. Quando ela retorna, elas deixam de existir — e ninguém precisa mandar apagar.

### Degrau 1 — guiado, escolher

> As caixas criadas dentro de uma função existem enquanto ela roda.
> Quando a função retorna, essas caixas deixam de existir, sozinhas: ninguém precisa mandar apagar.

**Versão 1.** conta terminou. O que aconteceu com a caixa n?

Já está escrito:

```c
int conta(void) { int n = 7; return n; }

conta();
```

Opções: `Deixou de existir, sozinha, no retorno`  `Nada: memória é uma região única, sem distinção de regras de vida`  `Continua lá até alguém chamar free`

Resposta certa: `Deixou de existir, sozinha, no retorno`

Se errar:

- respondeu `Nada: memória é uma região única, sem distinção de regras de vida` → A memória tem regras de vida diferentes: uma caixa criada dentro da função dura só enquanto ela roda. n saiu, sozinha, no retorno. _(aponta a crença `memory_is_uniform`)_
- respondeu `Continua lá até alguém chamar free` → free é para blocos de malloc. n é uma caixa da função: sai sozinha no retorno, sem ninguém mandar.
- qualquer outro erro → n é uma caixa da função: deixou de existir, sozinha, quando conta retornou.

**Versão 2.** soma terminou. O que aconteceu com a caixa total?

Já está escrito:

```c
int soma(void) { int total = 4; return total; }

soma();
```

Opções: `Continua lá até alguém chamar free`  `Deixou de existir, sozinha, no retorno`  `Nada: memória é uma região única, sem distinção de regras de vida`

Resposta certa: `Deixou de existir, sozinha, no retorno`

Se errar:

- respondeu `Nada: memória é uma região única, sem distinção de regras de vida` → A memória tem regras de vida diferentes: uma caixa criada dentro da função dura só enquanto ela roda. total saiu, sozinha, no retorno. _(aponta a crença `memory_is_uniform`)_
- respondeu `Continua lá até alguém chamar free` → free é para blocos de malloc. total é uma caixa da função: sai sozinha no retorno, sem ninguém mandar.
- qualquer outro erro → total é uma caixa da função: deixou de existir, sozinha, quando soma retornou.

### Degrau 2 — guiado, digitar

> Cada chamada cria caixas novas. O que a chamada anterior deixou nas dela não está mais lá.

**Versão 1.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int passo(void) {
    int n = 1;
    n = n + 1;
    return n;
}

passo();
printf("%d\n", passo());
```

Resposta certa: `2`

Se errar:

- digitou `3` → A primeira chamada levou o seu n a 2, mas essa caixa saiu no retorno. A segunda cria outro n, que começa em 1: 2.
- digitou `1` → Dentro de passo, n começa em 1 e vira 2 antes do return. A chamada mostrada devolve 2.
- qualquer outro erro → Cada chamada cria o seu n, que começa em 1 e vira 2. A segunda devolve 2.

**Versão 2.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int soma(void) {
    int total = 5;
    total = total + 5;
    return total;
}

soma();
printf("%d\n", soma());
```

Resposta certa: `10`

Se errar:

- digitou `15` → A primeira chamada levou o seu total a 10, mas essa caixa saiu no retorno. A segunda cria outro total, que começa em 5: 10.
- digitou `5` → Dentro de soma, total começa em 5 e vira 10 antes do return. A chamada mostrada devolve 10.
- qualquer outro erro → Cada chamada cria o seu total, que começa em 5 e vira 10. A segunda devolve 10.

### Degrau 3 — guiado, escolher

> Um bloco de malloc segue outra regra: fica até o free. Uma local marcada static também: dura o programa inteiro.

**Versão 1.** Qual das duas devolve um endereço que ainda vale depois do retorno?

Já está escrito:

```c
int *a(void) { int *p = malloc(sizeof(int)); return p; }
int *b(void) { int n = 1; return &n; }
```

Opções: `a: o bloco de malloc fica até o free`  `b: n continua lá depois do retorno`  `As duas: memória é uma região única, sem distinção de regras de vida`

Resposta certa: `a: o bloco de malloc fica até o free`

Se errar:

- respondeu `As duas: memória é uma região única, sem distinção de regras de vida` → As duas caixas seguem regras diferentes: o bloco de malloc fica até o free; a local n sai no retorno de b. Só o endereço de a ainda vale. _(aponta a crença `memory_is_uniform`)_
- respondeu `b: n continua lá depois do retorno` → n é local de b: sai no retorno. O endereço que b devolve leva a uma caixa que não existe mais.
- qualquer outro erro → Só o bloco de malloc dura depois do retorno: a devolve um endereço que vale.

**Versão 2.** Qual das duas devolve um endereço que ainda vale depois do retorno?

Já está escrito:

```c
int *a(void) { int n = 2; return &n; }
int *b(void) { static int n = 2; return &n; }
```

Opções: `a: o n dela continua lá depois do retorno`  `As duas: memória é uma região única, sem distinção de regras de vida`  `b: o n marcado static dura o programa inteiro`

Resposta certa: `b: o n marcado static dura o programa inteiro`

Se errar:

- respondeu `As duas: memória é uma região única, sem distinção de regras de vida` → As duas caixas seguem regras diferentes: a local comum sai no retorno; a marcada static dura o programa. Só o endereço de b ainda vale. _(aponta a crença `memory_is_uniform`)_
- respondeu `a: o n dela continua lá depois do retorno` → O n de a é uma local comum: sai no retorno. O endereço que a devolve leva a uma caixa que não existe mais.
- qualquer outro erro → Só a local marcada static dura depois do retorno: b devolve um endereço que vale.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: As locais saem sozinhas no retorno_

**Versão 1.** A função é chamada três vezes, e só a terceira é mostrada. Que número aparece?

```c
int marca(void) {
    int pontos = 10;
    pontos = pontos + 1;
    return pontos;
}

marca();
marca();
printf("%d\n", marca());
```

Resposta certa: `11`

Se errar:

- digitou `13` → Cada chamada cria o seu pontos, que começa em 10. O das chamadas anteriores saiu no retorno: a terceira devolve 11.
- digitou `10` → Dentro de marca, pontos começa em 10 e vira 11 antes do return: 11.
- qualquer outro erro → Cada chamada cria o seu pontos, que começa em 10 e vira 11. A terceira devolve 11.

**Versão 2.** A função é chamada três vezes, e só a terceira é mostrada. Que número aparece?

```c
int vez(void) {
    int n = 0;
    n = n + 2;
    return n;
}

vez();
vez();
printf("%d\n", vez());
```

Resposta certa: `2`

Se errar:

- digitou `6` → Cada chamada cria o seu n, que começa em 0. O das chamadas anteriores saiu no retorno: a terceira devolve 2.
- digitou `0` → Dentro de vez, n começa em 0 e vira 2 antes do return: 2.
- qualquer outro erro → Cada chamada cria o seu n, que começa em 0 e vira 2. A terceira devolve 2.

### Degrau 5 — prática, escolher

**Versão 1.** É preciso chamar free para a caixa n deixar de existir?

Já está escrito:

```c
void f(void) { int n = 7; }
```

Opções: `Não: n sai sozinha quando f retorna`  `Sim: sem free, n fica para sempre`  `Sim: toda caixa segue a mesma regra`

Resposta certa: `Não: n sai sozinha quando f retorna`

Se errar:

- respondeu `Sim: sem free, n fica para sempre` → free é para blocos de malloc. n é uma caixa de f: sai sozinha quando f retorna.
- respondeu `Sim: toda caixa segue a mesma regra` → As caixas não seguem todas a mesma regra: a local sai no retorno, e o bloco de malloc fica até o free.
- qualquer outro erro → n é uma caixa de f: sai sozinha no retorno, sem free.

**Versão 2.** É preciso chamar free para a caixa total deixar de existir?

Já está escrito:

```c
int g(void) { int total = 0; return total; }
```

Opções: `Sim: toda caixa segue a mesma regra`  `Sim: sem free, total fica para sempre`  `Não: total sai sozinha quando g retorna`

Resposta certa: `Não: total sai sozinha quando g retorna`

Se errar:

- respondeu `Sim: sem free, total fica para sempre` → free é para blocos de malloc. total é uma caixa de g: sai sozinha quando g retorna.
- respondeu `Sim: toda caixa segue a mesma regra` → As caixas não seguem todas a mesma regra: a local sai no retorno, e o bloco de malloc fica até o free.
- qualquer outro erro → total é uma caixa de g: sai sozinha no retorno, sem free.

### Se errar a pergunta do topo: a revisão

> As caixas criadas dentro de uma função existem enquanto ela roda. Quando ela retorna, deixam de existir, sozinhas.
> Cada chamada cria caixas novas: a anterior não deixa nada para a seguinte.

```c
int dobra(void) {
    int n = 3;
    n = n + n;
    return n;
}

dobra();
printf("%d\n", dobra());
```

A máquina imprime:

```
6
```

### Se a pessoa disser a crença: a prova

Você disse:

> Memória é uma região única, sem distinção de regras de vida.

```c
int *a(void) { int *p = malloc(sizeof(int)); return p; }
int *b(void) { int n = 1; return &n; }

free(a());
b();
```

**a devolve o endereço de um bloco de malloc, e b o endereço da sua local n. De qual das duas o compilador reclama?**

- De b: n sai no retorno, e o bloco de malloc fica _(é o que a máquina faz)_
- De nenhuma: memória é uma só, e as duas devolvem um endereço _(é o que a crença espera)_

O compilador reclama:

```
function returns address of local variable
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado._

O que isto mostra: O compilador aceita a, que devolve o endereço do bloco, e reclama de b, que devolve &n. As duas caixas seguem regras de vida diferentes: o bloco de malloc fica até o free; a local sai, sozinha, no retorno.

## B2 — Enquanto a função roda, o endereço de uma caixa dela é um endereço perfeitamente bom, como qualquer outro.

### Degrau 1 — guiado, escolher

> Enquanto a função roda, &n é o endereço da caixa n: um endereço como outro qualquer.
> &n não é uma cópia de n: é onde a própria n está.

**Versão 1.** f está rodando. O que &n dá?

Já está escrito:

```c
void f(void) {
    int n = 7;
    int *p = &n;
}
```

Opções: `O endereço da caixa n, que vale enquanto f roda`  `Uma cópia de n: &x entrega uma cópia de x, e é a cópia que viaja`  `Um endereço que vale para sempre`

Resposta certa: `O endereço da caixa n, que vale enquanto f roda`

Se errar:

- respondeu `Uma cópia de n: &x entrega uma cópia de x, e é a cópia que viaja` → O & nunca copia: &n é o endereço da própria caixa n. Enquanto f roda, ele vale como qualquer outro endereço. _(aponta a crença `ampersand_copies`)_
- respondeu `Um endereço que vale para sempre` → Vale enquanto f roda: quando f retorna, a caixa n sai, e o endereço fica sem caixa.
- qualquer outro erro → &n é o endereço da caixa n, e vale enquanto f roda.

**Versão 2.** g está rodando. O que &total dá?

Já está escrito:

```c
void g(void) {
    int total = 3;
    int *q = &total;
}
```

Opções: `Um endereço que vale para sempre`  `O endereço da caixa total, que vale enquanto g roda`  `Uma cópia de total: &x entrega uma cópia de x, e é a cópia que viaja`

Resposta certa: `O endereço da caixa total, que vale enquanto g roda`

Se errar:

- respondeu `Uma cópia de total: &x entrega uma cópia de x, e é a cópia que viaja` → O & nunca copia: &total é o endereço da própria caixa total. Enquanto g roda, ele vale como qualquer outro endereço. _(aponta a crença `ampersand_copies`)_
- respondeu `Um endereço que vale para sempre` → Vale enquanto g roda: quando g retorna, a caixa total sai, e o endereço fica sem caixa.
- qualquer outro erro → &total é o endereço da caixa total, e vale enquanto g roda.

### Degrau 2 — guiado, digitar

> Por p, dá para escrever na própria n enquanto f roda.

**Versão 1.** Que número aparece?

```c
void f(void) {
    int n = 1;
    int *p = &n;
    *p = 4;
    printf("%d\n", n);
}

f();
```

Resposta certa: `4`

Se errar:

- digitou `1` → p guarda o endereço da própria n, e não de uma cópia. *p = 4 escreveu em n: 4.
- qualquer outro erro → *p = 4 escreveu na própria n, pelo endereço: 4.

**Versão 2.** Que número aparece?

```c
void g(void) {
    int total = 2;
    int *q = &total;
    *q = 6;
    printf("%d\n", total);
}

g();
```

Resposta certa: `6`

Se errar:

- digitou `2` → q guarda o endereço da própria total, e não de uma cópia. *q = 6 escreveu em total: 6.
- qualquer outro erro → *q = 6 escreveu na própria total, pelo endereço: 6.

### Degrau 3 — guiado, completar

> Esse endereço pode ir para outra função enquanto a dona da caixa roda: zera(&n) entrega a caixa n, e zera escreve nela.

**Versão 1.** Complete a chamada para zera escrever em n.

Já está escrito:

```c
void zera(int *d) { *d = 0; }

int n = 7;
```

```c
zera(___);
```

Peças: `&n`  `n`  `*n`

Resposta certa: `zera(&n);`

Se errar:

- respondeu `zera(n);` → n é um int, e zera quer um endereço: o compilador reclama. A caixa n vai pelo endereço: zera(&n).
- respondeu `zera(*n);` → *n não existe: n é um int, e não um ponteiro. O compilador reclama. O que serve é zera(&n).
- qualquer outro erro → zera recebe o endereço da caixa: zera(&n);

**Versão 2.** Complete a chamada para zera escrever em total.

Já está escrito:

```c
void zera(int *d) { *d = 0; }

int total = 3;
```

```c
zera(___);
```

Peças: `*total`  `&total`  `total`

Resposta certa: `zera(&total);`

Se errar:

- respondeu `zera(total);` → total é um int, e zera quer um endereço: o compilador reclama. A caixa total vai pelo endereço: zera(&total).
- respondeu `zera(*total);` → *total não existe: total é um int, e não um ponteiro. O compilador reclama. O que serve é zera(&total).
- qualquer outro erro → zera recebe o endereço da caixa: zera(&total);

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Enquanto a função roda, o endereço da local vale_

**Versão 1.** Que número aparece?

```c
void soma1(int *d) { *d = *d + 1; }
void f(void) { int n = 4; soma1(&n); printf("%d\n", n); }

f();
```

Resposta certa: `5`

Se errar:

- digitou `4` → f entregou &n, o endereço da própria n. soma1 escreveu por ele: n passou a 5.
- qualquer outro erro → soma1 escreveu na n de f, pelo endereço: 5.

**Versão 2.** Que número aparece?

```c
void dobra(int *d) { *d = *d + *d; }
void g(void) { int total = 3; dobra(&total); printf("%d\n", total); }

g();
```

Resposta certa: `6`

Se errar:

- digitou `3` → g entregou &total, o endereço da própria total. dobra escreveu por ele: total passou a 6.
- qualquer outro erro → dobra escreveu na total de g, pelo endereço: 6.

### Degrau 5 — prática, escolher

**Versão 1.** f entrega &n a zera, enquanto roda. O que viaja?

Já está escrito:

```c
void f(void) { int n = 7; zera(&n); }
```

Opções: `O endereço da caixa n`  `Uma cópia de n`  `A caixa n inteira`

Resposta certa: `O endereço da caixa n`

Se errar:

- respondeu `Uma cópia de n` → O & não copia: o que viaja é o endereço da própria n. Por ele, zera chega na caixa de f.
- respondeu `A caixa n inteira` → A caixa fica onde está, em f. O que viaja é o endereço dela.
- qualquer outro erro → Viaja o endereço da caixa n; a caixa fica em f.

**Versão 2.** g entrega &total a dobra, enquanto roda. O que viaja?

Já está escrito:

```c
void g(void) { int total = 3; dobra(&total); }
```

Opções: `A caixa total inteira`  `Uma cópia de total`  `O endereço da caixa total`

Resposta certa: `O endereço da caixa total`

Se errar:

- respondeu `Uma cópia de total` → O & não copia: o que viaja é o endereço da própria total. Por ele, dobra chega na caixa de g.
- respondeu `A caixa total inteira` → A caixa fica onde está, em g. O que viaja é o endereço dela.
- qualquer outro erro → Viaja o endereço da caixa total; a caixa fica em g.

### Se errar a pergunta do topo: a revisão

> Enquanto a função roda, o endereço de uma caixa dela é um endereço como outro qualquer.
> Por ele dá para escrever na própria caixa, ali dentro ou em outra função.

```c
void f(void) {
    int n = 5;
    int *p = &n;
    *p = 8;
    printf("%d\n", n);
}

f();
```

A máquina imprime:

```
8
```

### Se a pessoa disser a crença: a prova

Você disse:

> &x entrega uma cópia de x, e é a cópia que viaja.

```c
void poe(int *d) { *d = 9; }
void f(void) { int n = 7; poe(&n); printf("%d\n", n); }

f();
```

**f entrega &n a poe, que escreve 9 pelo endereço recebido. Depois f mostra n. O que aparece?**

- 7: &n entregou uma cópia de n, e poe escreveu na cópia _(é o que a crença espera)_
- 9 _(é o que a máquina faz)_

A máquina imprime:

```
9
```

O que isto mostra: Saiu 9. &n não é uma cópia de n: é o endereço da própria caixa n, e enquanto f roda ele vale como qualquer outro. Por ele, poe escreveu na n de f.

## B3 — O que a função retorna é copiado para quem chamou. Se você não guardar numa variável, ele se perde.

### Degrau 1 — guiado, escolher

> O valor do return é copiado para o lugar da chamada. int x = dobro(3); guarda essa cópia em x.
> Se ninguém guardar, a cópia se perde.

**Versão 1.** O que acontece com o 6 que dobro(3) retorna, na última linha?

Já está escrito:

```c
int dobro(int n) { return n + n; }

dobro(3);
```

Opções: `Se perde: ninguém guardou`  `O valor retornado fica guardado em algum lugar; não é preciso copiá-lo`  `Vai para a caixa n de dobro`

Resposta certa: `Se perde: ninguém guardou`

Se errar:

- respondeu `O valor retornado fica guardado em algum lugar; não é preciso copiá-lo` → O retorno não fica guardado em lugar nenhum: é copiado para o lugar da chamada, e ali ninguém o guardou. O 6 se perdeu. _(aponta a crença `retorno_fica_guardado`)_
- respondeu `Vai para a caixa n de dobro` → n é local de dobro e saiu no retorno. O 6 foi copiado para o lugar da chamada, e ninguém o guardou.
- qualquer outro erro → Ninguém guardou o 6: ele se perdeu.

**Versão 2.** O que acontece com o 6 que triplo(2) retorna, na última linha?

Já está escrito:

```c
int triplo(int n) { return n + n + n; }

triplo(2);
```

Opções: `Vai para a caixa n de triplo`  `Se perde: ninguém guardou`  `O valor retornado fica guardado em algum lugar; não é preciso copiá-lo`

Resposta certa: `Se perde: ninguém guardou`

Se errar:

- respondeu `O valor retornado fica guardado em algum lugar; não é preciso copiá-lo` → O retorno não fica guardado em lugar nenhum: é copiado para o lugar da chamada, e ali ninguém o guardou. O 6 se perdeu. _(aponta a crença `retorno_fica_guardado`)_
- respondeu `Vai para a caixa n de triplo` → n é local de triplo e saiu no retorno. O 6 foi copiado para o lugar da chamada, e ninguém o guardou.
- qualquer outro erro → Ninguém guardou o 6: ele se perdeu.

### Degrau 2 — guiado, completar

> Para usar depois o que a função retornou, guarde numa variável: int x = dobro(3);

**Versão 1.** Complete para x guardar o que dobro(3) retorna.

Já está escrito:

```c
int dobro(int n) { return n + n; }
```

```c
int x = ___;
```

Peças: `dobro(3)`  `dobro`  `n`

Resposta certa: `int x = dobro(3);`

Se errar:

- respondeu `int x = dobro;` → dobro sozinho é a função, e não o que ela retorna: o compilador reclama. O valor vem da chamada: dobro(3).
- respondeu `int x = n;` → n é local de dobro: fora dela esse nome não existe, e o compilador reclama. O valor vem da chamada: dobro(3).
- qualquer outro erro → O valor vem da chamada, e x guarda a cópia: int x = dobro(3);

**Versão 2.** Complete para y guardar o que triplo(2) retorna.

Já está escrito:

```c
int triplo(int n) { return n + n + n; }
```

```c
int y = ___;
```

Peças: `n`  `triplo(2)`  `triplo`

Resposta certa: `int y = triplo(2);`

Se errar:

- respondeu `int y = triplo;` → triplo sozinho é a função, e não o que ela retorna: o compilador reclama. O valor vem da chamada: triplo(2).
- respondeu `int y = n;` → n é local de triplo: fora dela esse nome não existe, e o compilador reclama. O valor vem da chamada: triplo(2).
- qualquer outro erro → O valor vem da chamada, e y guarda a cópia: int y = triplo(2);

### Degrau 3 — guiado, digitar

> Cada chamada devolve uma cópia nova. A que não foi guardada se perde, e a variável fica com o que recebeu.

**Versão 1.** Que número aparece?

```c
int mais1(int n) { return n + 1; }

int x = mais1(5);
mais1(20);
printf("%d\n", x);
```

Resposta certa: `6`

Se errar:

- digitou `21` → mais1(20) devolveu 21, mas ninguém guardou: o valor se perdeu. x ficou com o 6 da primeira chamada.
- digitou `5` → x guardou o que mais1(5) retornou, e não o 5 que foi passado: 6.
- qualquer outro erro → x guardou o 6 da primeira chamada; o 21 da segunda se perdeu.

**Versão 2.** Que número aparece?

```c
int mais1(int n) { return n + 1; }

int y = mais1(8);
mais1(1);
printf("%d\n", y);
```

Resposta certa: `9`

Se errar:

- digitou `2` → mais1(1) devolveu 2, mas ninguém guardou: o valor se perdeu. y ficou com o 9 da primeira chamada.
- digitou `8` → y guardou o que mais1(8) retornou, e não o 8 que foi passado: 9.
- qualquer outro erro → y guardou o 9 da primeira chamada; o 2 da segunda se perdeu.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O que ninguém guardou se perde_

**Versão 1.** Que número aparece?

```c
int triplo(int n) { return n + n + n; }

int t = triplo(2);
triplo(3);
printf("%d\n", t);
```

Resposta certa: `6`

Se errar:

- digitou `9` → triplo(3) devolveu 9, mas ninguém guardou: o valor se perdeu. t ficou com o 6 de triplo(2).
- digitou `2` → t guardou o que triplo(2) retornou, e não o 2 que foi passado: 6.
- qualquer outro erro → t guardou o 6 de triplo(2); o 9 de triplo(3) se perdeu.

**Versão 2.** Que número aparece?

```c
int menos1(int n) { return n - 1; }

int r = menos1(9);
menos1(4);
printf("%d\n", r);
```

Resposta certa: `8`

Se errar:

- digitou `3` → menos1(4) devolveu 3, mas ninguém guardou: o valor se perdeu. r ficou com o 8 de menos1(9).
- digitou `9` → r guardou o que menos1(9) retornou, e não o 9 que foi passado: 8.
- qualquer outro erro → r guardou o 8 de menos1(9); o 3 de menos1(4) se perdeu.

### Degrau 5 — prática, escolher

**Versão 1.** Para usar depois o que conta() retorna, o que é preciso?

Já está escrito:

```c
int conta(void) { int n = 3; return n; }
```

Opções: `Guardar numa variável: int x = conta();`  `Nada: o valor fica guardado em conta`  `Nada: a caixa n continua com ele`

Resposta certa: `Guardar numa variável: int x = conta();`

Se errar:

- respondeu `Nada: o valor fica guardado em conta` → O retorno não fica guardado em conta: é copiado para o lugar da chamada. Sem uma variável ali, ele se perde.
- respondeu `Nada: a caixa n continua com ele` → n é local de conta e saiu no retorno. O valor foi copiado para quem chamou: é preciso guardar a cópia.
- qualquer outro erro → É preciso guardar a cópia: int x = conta();

**Versão 2.** Para usar depois o que quadrado(5) retorna, o que é preciso?

Já está escrito:

```c
int quadrado(int n) { return n * n; }
```

Opções: `Nada: a caixa n continua com ele`  `Guardar numa variável: int x = quadrado(5);`  `Nada: o valor fica guardado em quadrado`

Resposta certa: `Guardar numa variável: int x = quadrado(5);`

Se errar:

- respondeu `Nada: o valor fica guardado em quadrado` → O retorno não fica guardado em quadrado: é copiado para o lugar da chamada. Sem uma variável ali, ele se perde.
- respondeu `Nada: a caixa n continua com ele` → n é local de quadrado e saiu no retorno. O valor foi copiado para quem chamou: é preciso guardar a cópia.
- qualquer outro erro → É preciso guardar a cópia: int x = quadrado(5);

### Se errar a pergunta do topo: a revisão

> O que a função retorna é copiado para quem chamou, no lugar da chamada.
> Se ninguém guardar numa variável, o valor se perde.

```c
int dobro(int n) { return n + n; }

int x = dobro(3);
printf("%d\n", x);
```

A máquina imprime:

```
6
```

### Se a pessoa disser a crença: a prova

Você disse:

> O valor retornado fica guardado em algum lugar; não é preciso copiá-lo.

```c
int dobro(int n) { return n + n; }

int x = dobro(2);
dobro(10);
printf("%d\n", x);
```

**x guarda o que dobro(2) retornou. Depois dobro(10) é chamada, e ninguém guarda o retorno dela. O que aparece?**

- 4 _(é o que a máquina faz)_
- 20: o último retorno fica guardado, e x mostra ele _(é o que a crença espera)_

A máquina imprime:

```
4
```

O que isto mostra: Saiu 4. O 20 de dobro(10) foi copiado para o lugar da chamada, e ali ninguém o guardou: perdeu-se. O retorno não fica guardado em lugar nenhum; x tem o que recebeu, e só isso.

## I1 — Então retornar &local copia o endereço, e a caixa fica para trás. Quando quem chamou recebe esse endereço, a caixa já sumiu — ela sumiu no mesmo instante do retorno.

### Degrau 1 — guiado, escolher

> return &n copia o endereço de n. A caixa n não vai junto: fica para trás e sai no retorno.
> Retornar &local devolve um endereço, e não a variável.

**Versão 1.** O que f entrega a quem chamou?

Já está escrito:

```c
int *f(void) {
    int n = 7;
    return &n;
}
```

Opções: `Uma cópia do endereço de n; a caixa n fica para trás`  `A variável n, com o 7: o ponteiro é o próprio dado, e retornar &local devolve a variável`  `Uma cópia do 7`

Resposta certa: `Uma cópia do endereço de n; a caixa n fica para trás`

Se errar:

- respondeu `A variável n, com o 7: o ponteiro é o próprio dado, e retornar &local devolve a variável` → O ponteiro não é o dado: é o endereço dele. return &n copia o endereço, e a caixa n fica para trás, saindo no retorno. _(aponta a crença `pointer_is_data`)_
- respondeu `Uma cópia do 7` → Quem devolve uma cópia do 7 é return n;. return &n devolve o endereço de n, e a caixa fica para trás.
- qualquer outro erro → f entrega o endereço de n; a caixa n fica para trás e sai no retorno.

**Versão 2.** O que g entrega a quem chamou?

Já está escrito:

```c
int *g(void) {
    int total = 3;
    return &total;
}
```

Opções: `Uma cópia do 3`  `A variável total, com o 3: o ponteiro é o próprio dado, e retornar &local devolve a variável`  `Uma cópia do endereço de total; a caixa total fica para trás`

Resposta certa: `Uma cópia do endereço de total; a caixa total fica para trás`

Se errar:

- respondeu `A variável total, com o 3: o ponteiro é o próprio dado, e retornar &local devolve a variável` → O ponteiro não é o dado: é o endereço dele. return &total copia o endereço, e a caixa total fica para trás, saindo no retorno. _(aponta a crença `pointer_is_data`)_
- respondeu `Uma cópia do 3` → Quem devolve uma cópia do 3 é return total;. return &total devolve o endereço de total, e a caixa fica para trás.
- qualquer outro erro → g entrega o endereço de total; a caixa total fica para trás e sai no retorno.

### Degrau 2 — guiado, escolher

> Quando quem chamou recebe esse endereço, a caixa n já sumiu: sumiu no mesmo instante do retorno.

**Versão 1.** Na última linha, p recebe o endereço de n. Onde está a caixa n nesse momento?

Já está escrito:

```c
int *f(void) { int n = 7; return &n; }

int *p = f();
```

Opções: `Não existe mais: saiu no retorno de f`  `Em p: retornar &local devolve a variável, e p é a própria n`  `Ainda em f, esperando o free`

Resposta certa: `Não existe mais: saiu no retorno de f`

Se errar:

- respondeu `Em p: retornar &local devolve a variável, e p é a própria n` → p não é a variável: guarda um endereço. A caixa n ficou em f e saiu no mesmo instante do retorno. _(aponta a crença `pointer_is_data`)_
- respondeu `Ainda em f, esperando o free` → free é para blocos de malloc. n é local de f: saiu sozinha no retorno.
- qualquer outro erro → Quando p recebe o endereço, a caixa n já saiu: sumiu no retorno de f.

**Versão 2.** Na última linha, q recebe o endereço de total. Onde está a caixa total nesse momento?

Já está escrito:

```c
int *g(void) { int total = 3; return &total; }

int *q = g();
```

Opções: `Ainda em g, esperando o free`  `Não existe mais: saiu no retorno de g`  `Em q: retornar &local devolve a variável, e q é a própria total`

Resposta certa: `Não existe mais: saiu no retorno de g`

Se errar:

- respondeu `Em q: retornar &local devolve a variável, e q é a própria total` → q não é a variável: guarda um endereço. A caixa total ficou em g e saiu no mesmo instante do retorno. _(aponta a crença `pointer_is_data`)_
- respondeu `Ainda em g, esperando o free` → free é para blocos de malloc. total é local de g: saiu sozinha no retorno.
- qualquer outro erro → Quando q recebe o endereço, a caixa total já saiu: sumiu no retorno de g.

### Degrau 3 — guiado, digitar

> Para entregar o valor, devolva o valor: com return n; a cópia do 7 chega inteira a quem chamou.

**Versão 1.** Que número aparece?

```c
int f(void) { int n = 7; return n; }

int x = f();
printf("%d\n", x);
```

Resposta certa: `7`

Se errar:

- digitou `0` → return n; copia o 7 para quem chamou. A caixa n sai, mas a cópia já está em x: 7.
- qualquer outro erro → return n; entregou uma cópia do 7, que x guardou: 7.

**Versão 2.** Que número aparece?

```c
int g(void) { int total = 12; return total; }

int y = g();
printf("%d\n", y);
```

Resposta certa: `12`

Se errar:

- digitou `0` → return total; copia o 12 para quem chamou. A caixa total sai, mas a cópia já está em y: 12.
- qualquer outro erro → return total; entregou uma cópia do 12, que y guardou: 12.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Retornar &n devolve um endereço, e não n_

**Versão 1.** Depois da última linha, o que p tem?

Já está escrito:

```c
int *f(void) { int n = 5; return &n; }

int *p = f();
```

Opções: `Um endereço que não leva a caixa nenhuma`  `A variável n, com o 5`  `Uma cópia do 5`

Resposta certa: `Um endereço que não leva a caixa nenhuma`

Se errar:

- respondeu `A variável n, com o 5` → p não recebe a variável: recebe um endereço. E a caixa n saiu no retorno de f, então esse endereço não leva a lugar nenhum.
- respondeu `Uma cópia do 5` → Uma cópia do 5 viria de return n;. f devolve &n: um endereço, de uma caixa que já saiu.
- qualquer outro erro → p tem um endereço, e a caixa dele já saiu: não leva a lugar nenhum.

**Versão 2.** Depois da última linha, o que q tem?

Já está escrito:

```c
int *g(void) { int m = 8; return &m; }

int *q = g();
```

Opções: `Uma cópia do 8`  `Um endereço que não leva a caixa nenhuma`  `A variável m, com o 8`

Resposta certa: `Um endereço que não leva a caixa nenhuma`

Se errar:

- respondeu `A variável m, com o 8` → q não recebe a variável: recebe um endereço. E a caixa m saiu no retorno de g, então esse endereço não leva a lugar nenhum.
- respondeu `Uma cópia do 8` → Uma cópia do 8 viria de return m;. g devolve &m: um endereço, de uma caixa que já saiu.
- qualquer outro erro → q tem um endereço, e a caixa dele já saiu: não leva a lugar nenhum.

### Degrau 5 — prática, digitar

**Versão 1.** Que número aparece?

```c
int g(void) { int total = 3; total = total + 4; return total; }

int x = g();
printf("%d\n", x);
```

Resposta certa: `7`

Se errar:

- digitou `3` → Dentro de g, total começa em 3 e vira 7 antes do return. return total; copia o 7: x guarda 7.
- qualquer outro erro → return total; copiou o 7 para quem chamou, e x guardou: 7.

**Versão 2.** Que número aparece?

```c
int h(void) { int n = 2; n = n + n; return n; }

int y = h();
printf("%d\n", y);
```

Resposta certa: `4`

Se errar:

- digitou `2` → Dentro de h, n começa em 2 e vira 4 antes do return. return n; copia o 4: y guarda 4.
- qualquer outro erro → return n; copiou o 4 para quem chamou, e y guardou: 4.

### Se errar a pergunta do topo: a revisão

> return n; copia o valor de n para quem chamou, e a cópia chega inteira.
> return &n; copia só o endereço: a caixa n fica para trás e sai no retorno.

```c
int f(void) {
    int n = 7;
    return n;
}

printf("%d\n", f());
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro é o próprio dado: retornar &local devolve a variável.

```c
int *f(void) { int n = 7; return &n; }

int *p = f();
printf("%d\n", p == NULL);
```

**f devolve &n, e p recebe o que voltou. A última linha pergunta se p é NULL. O que aparece?**

- 0: p trouxe a própria variável n, com o 7 dentro _(é o que a crença espera)_
- 1 _(é o que a máquina faz)_

A máquina imprime:

```
1
```

_Resultado do gcc 16.2. Ao ver return &n, ele avisa ("function returns address of local variable") e devolve NULL no lugar do endereço da caixa que vai sair. O padrão do C não diz o que esse endereço vale depois do retorno; o gcc escolheu NULL._

O que isto mostra: Saiu 1. O que f devolveu foi um endereço, e não a variável: neste gcc, NULL, porque a caixa de n saiu no retorno e o endereço dela de nada serviria. A variável não viaja; só o endereço.

## I2 — Marcar a caixa como static faz ela durar o programa inteiro, mas o nome continua só de dentro da função. E sem static o lugar pode ainda guardar o valor antigo — e aí o erro parece funcionar.

### Degrau 1 — guiado, escolher

> static muda a duração: a caixa dura o programa inteiro, e o endereço dela vale depois do retorno.
> O nome não muda de lugar: n continua sendo um nome só de dentro da função.

**Versão 1.** O que static muda em n?

Já está escrito:

```c
int *f(void) { static int n = 7; return &n; }
```

Opções: `A duração: a caixa dura o programa, e o nome segue só de dentro de f`  `O escopo: static muda o escopo da variável, e por isso retornar o endereço passa a valer`  `Nada: sem static seria igual`

Resposta certa: `A duração: a caixa dura o programa, e o nome segue só de dentro de f`

Se errar:

- respondeu `O escopo: static muda o escopo da variável, e por isso retornar o endereço passa a valer` → static não mexe no escopo: o nome n continua só de dentro de f. O que muda é a duração — a caixa dura o programa, e por isso &n vale depois do retorno. _(aponta a crença `static_is_scope`)_
- respondeu `Nada: sem static seria igual` → Sem static, n sairia no retorno, e &n levaria a lugar nenhum. Com static, a caixa dura o programa.
- qualquer outro erro → static muda a duração da caixa, e não o escopo do nome.

**Versão 2.** O que static muda em total?

Já está escrito:

```c
int *g(void) { static int total = 3; return &total; }
```

Opções: `Nada: sem static seria igual`  `A duração: a caixa dura o programa, e o nome segue só de dentro de g`  `O escopo: static muda o escopo da variável, e por isso retornar o endereço passa a valer`

Resposta certa: `A duração: a caixa dura o programa, e o nome segue só de dentro de g`

Se errar:

- respondeu `O escopo: static muda o escopo da variável, e por isso retornar o endereço passa a valer` → static não mexe no escopo: o nome total continua só de dentro de g. O que muda é a duração — a caixa dura o programa, e por isso &total vale depois do retorno. _(aponta a crença `static_is_scope`)_
- respondeu `Nada: sem static seria igual` → Sem static, total sairia no retorno, e &total levaria a lugar nenhum. Com static, a caixa dura o programa.
- qualquer outro erro → static muda a duração da caixa, e não o escopo do nome.

### Degrau 2 — guiado, digitar

> Com static, a caixa não é criada de novo a cada chamada: o valor que a chamada anterior deixou continua lá.

**Versão 1.** A função é chamada três vezes, e só a terceira é mostrada. Que número aparece?

```c
int conta(void) { static int n = 0; n = n + 1; return n; }

conta();
conta();
printf("%d\n", conta());
```

Resposta certa: `3`

Se errar:

- digitou `1` → Sem static seria 1. Com static, a caixa n dura entre as chamadas: 1, depois 2, e a terceira devolve 3.
- digitou `0` → n começa em 0 uma vez só, e cada chamada soma 1 antes do return. A terceira devolve 3.
- qualquer outro erro → Com static, n dura entre as chamadas: a terceira devolve 3.

**Versão 2.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int soma(void) { static int total = 10; total = total + 5; return total; }

soma();
printf("%d\n", soma());
```

Resposta certa: `20`

Se errar:

- digitou `15` → Sem static seria 15. Com static, a caixa total dura entre as chamadas: a primeira deixou 15, e a segunda soma mais 5: 20.
- digitou `10` → total começa em 10 uma vez só, e cada chamada soma 5 antes do return. A segunda devolve 20.
- qualquer outro erro → Com static, total dura entre as chamadas: a segunda devolve 20.

### Degrau 3 — guiado, escolher

> Sem static, o erro às vezes parece funcionar: o lugar onde a caixa ficava pode ainda guardar o valor antigo. Parecer funcionar não é funcionar.

**Versão 1.** Um colega diz: retornei &n sem static e o programa mostrou o 7, então está certo. O que dizer a ele?

Já está escrito:

```c
int *f(void) { int n = 7; return &n; }
```

Opções: `Parecer funcionar não é funcionar: o lugar só ainda guardava o valor`  `Está certo: static muda o escopo da variável, e sem ele dá no mesmo`  `Está certo: se mostrou o 7, a caixa n estava lá`

Resposta certa: `Parecer funcionar não é funcionar: o lugar só ainda guardava o valor`

Se errar:

- respondeu `Está certo: static muda o escopo da variável, e sem ele dá no mesmo` → static não muda o escopo: muda a duração. Sem ele, n sai no retorno, e o 7 que apareceu era só o que o lugar ainda guardava. _(aponta a crença `static_is_scope`)_
- respondeu `Está certo: se mostrou o 7, a caixa n estava lá` → A caixa n saiu no retorno. O 7 que apareceu era o que o lugar ainda guardava, por acaso: parecer funcionar não é funcionar.
- qualquer outro erro → Sem static, n saiu no retorno: o 7 era só o que o lugar ainda guardava.

**Versão 2.** Uma colega diz: retornei &total sem static e o programa mostrou o 3, então está certo. O que dizer a ela?

Já está escrito:

```c
int *g(void) { int total = 3; return &total; }
```

Opções: `Está certo: se mostrou o 3, a caixa total estava lá`  `Está certo: static muda o escopo da variável, e sem ele dá no mesmo`  `Parecer funcionar não é funcionar: o lugar só ainda guardava o valor`

Resposta certa: `Parecer funcionar não é funcionar: o lugar só ainda guardava o valor`

Se errar:

- respondeu `Está certo: static muda o escopo da variável, e sem ele dá no mesmo` → static não muda o escopo: muda a duração. Sem ele, total sai no retorno, e o 3 que apareceu era só o que o lugar ainda guardava. _(aponta a crença `static_is_scope`)_
- respondeu `Está certo: se mostrou o 3, a caixa total estava lá` → A caixa total saiu no retorno. O 3 que apareceu era o que o lugar ainda guardava, por acaso: parecer funcionar não é funcionar.
- qualquer outro erro → Sem static, total saiu no retorno: o 3 era só o que o lugar ainda guardava.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: static muda a duração, e não o escopo_

**Versão 1.** Depois de h ter rodado, o nome vezes vale fora de h?

Já está escrito:

```c
void h(void) { static int vezes = 0; }
```

Opções: `Não: o nome continua só de dentro de h`  `Vale: o static levou o nome para fora`  `Vale, porque a caixa durou`

Resposta certa: `Não: o nome continua só de dentro de h`

Se errar:

- respondeu `Vale: o static levou o nome para fora` → static não leva o nome para fora: muda só a duração da caixa. Fora de h, vezes não existe, e o compilador reclama.
- respondeu `Vale, porque a caixa durou` → A caixa dura o programa, mas o nome não sai de h. Durar e ter nome fora são coisas diferentes.
- qualquer outro erro → O nome vezes continua só de dentro de h, mesmo com static.

**Versão 2.** Depois de g ter rodado, o nome total vale fora de g?

Já está escrito:

```c
void g(void) { static int total = 3; }
```

Opções: `Vale, porque a caixa durou`  `Vale: o static levou o nome para fora`  `Não: o nome continua só de dentro de g`

Resposta certa: `Não: o nome continua só de dentro de g`

Se errar:

- respondeu `Vale: o static levou o nome para fora` → static não leva o nome para fora: muda só a duração da caixa. Fora de g, total não existe, e o compilador reclama.
- respondeu `Vale, porque a caixa durou` → A caixa dura o programa, mas o nome não sai de g. Durar e ter nome fora são coisas diferentes.
- qualquer outro erro → O nome total continua só de dentro de g, mesmo com static.

### Degrau 5 — prática, digitar

**Versão 1.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int vez(void) { static int n = 0; n = n + 2; return n; }

vez();
printf("%d\n", vez());
```

Resposta certa: `4`

Se errar:

- digitou `2` → Com static, a caixa n dura entre as chamadas: a primeira deixou 2, e a segunda soma mais 2: 4.
- digitou `0` → n começa em 0 uma vez só, e cada chamada soma 2 antes do return. A segunda devolve 4.
- qualquer outro erro → Com static, n dura entre as chamadas: a segunda devolve 4.

**Versão 2.** A função é chamada três vezes, e só a terceira é mostrada. Que número aparece?

```c
int marca(void) { static int pontos = 1; pontos = pontos + pontos; return pontos; }

marca();
marca();
printf("%d\n", marca());
```

Resposta certa: `8`

Se errar:

- digitou `2` → Sem static seria 2. Com static, pontos dura entre as chamadas e dobra a cada uma: 2, 4 e a terceira devolve 8.
- digitou `4` → 4 é o que a segunda chamada devolve. A terceira dobra de novo: 8.
- qualquer outro erro → Com static, pontos dobra a cada chamada: a terceira devolve 8.

### Se errar a pergunta do topo: a revisão

> static faz a caixa durar o programa inteiro, e o endereço dela vale depois do retorno.
> Mas o nome continua só de dentro da função: fora dela, n não existe.

```c
int *f(void) { static int n = 7; return &n; }

int *p = f();
printf("%d\n", *p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> static muda o escopo da variável, e por isso retornar o endereço passa a valer.

```c
void f(void) { static int n = 7; }

f();
printf("%d\n", n);
```

**n é uma local de f marcada static. Depois de chamar f, a última linha usa n fora de f. O que o compilador faz?**

- Aceita: static muda o escopo, e o nome n passa a valer fora de f _(é o que a crença espera)_
- Reclama: o nome n continua só de dentro de f _(é o que a máquina faz)_

O compilador reclama:

```
'n' undeclared
```

_Mensagem do gcc 16.2. É um erro: o nome não existe ali. O programa não é executado._

O que isto mostra: O compilador reclama: fora de f, n não existe ("undeclared"). static muda a duração da caixa — ela dura o programa inteiro —, e não o escopo do nome. Por isso f pode devolver &n e o endereço vale, mas o nome n continua sendo só de dentro de f.

## I3 — Juntando: dá para acabar com um ponteiro apontando para o nada sem ter chamado free uma única vez. O jeito certo é quem chama criar a caixa e passar o endereço dela para a função preencher.

### Degrau 1 — guiado, escolher

> Ponteiro pendente não vem só do free: o endereço de uma local, guardado depois do retorno, também aponta para o nada.

**Versão 1.** Nenhum free foi chamado. p aponta para uma caixa viva?

Já está escrito:

```c
int *f(void) { int n = 7; return &n; }

int *p = f();
```

Opções: `Não: n saiu no retorno, e p ficou pendente`  `Sim: retornar o endereço de uma variável local funciona; ela continua lá`  `Sim: sem free, nada se perde`

Resposta certa: `Não: n saiu no retorno, e p ficou pendente`

Se errar:

- respondeu `Sim: retornar o endereço de uma variável local funciona; ela continua lá` → A local não continua lá: n saiu no retorno de f. O endereço que voltou leva a lugar nenhum, e p ficou pendente. _(aponta a crença `local_survives_return`)_
- respondeu `Sim: sem free, nada se perde` → free não é o único jeito de perder uma caixa: a local sai sozinha no retorno. p ficou pendente sem free nenhum.
- qualquer outro erro → n saiu no retorno: p ficou pendente, sem free nenhum.

**Versão 2.** Nenhum free foi chamado. q aponta para uma caixa viva?

Já está escrito:

```c
int *g(void) { int total = 3; return &total; }

int *q = g();
```

Opções: `Sim: sem free, nada se perde`  `Sim: retornar o endereço de uma variável local funciona; ela continua lá`  `Não: total saiu no retorno, e q ficou pendente`

Resposta certa: `Não: total saiu no retorno, e q ficou pendente`

Se errar:

- respondeu `Sim: retornar o endereço de uma variável local funciona; ela continua lá` → A local não continua lá: total saiu no retorno de g. O endereço que voltou leva a lugar nenhum, e q ficou pendente. _(aponta a crença `local_survives_return`)_
- respondeu `Sim: sem free, nada se perde` → free não é o único jeito de perder uma caixa: a local sai sozinha no retorno. q ficou pendente sem free nenhum.
- qualquer outro erro → total saiu no retorno: q ficou pendente, sem free nenhum.

### Degrau 2 — guiado, digitar

> O jeito certo: quem chama cria a caixa e passa o endereço dela; a função preenche por ele, e a caixa continua viva.

**Versão 1.** Que número aparece?

```c
void enche(int *destino) { *destino = 42; }

int total = 0;
enche(&total);
printf("%d\n", total);
```

Resposta certa: `42`

Se errar:

- digitou `0` → enche recebeu o endereço de total e escreveu 42 nela. total é de quem chamou, e continua viva: 42.
- qualquer outro erro → Quem chamou deu a caixa, e enche preencheu: 42.

**Versão 2.** Que número aparece?

```c
void poe(int *destino) { *destino = 5; }

int n = 1;
poe(&n);
printf("%d\n", n);
```

Resposta certa: `5`

Se errar:

- digitou `1` → poe recebeu o endereço de n e escreveu 5 nela. n é de quem chamou, e continua viva: 5.
- qualquer outro erro → Quem chamou deu a caixa, e poe preencheu: 5.

### Degrau 3 — guiado, escolher

> Para consertar sem malloc, entregue o valor, ou receba de quem chama a caixa para preencher.

**Versão 1.** Como consertar f para quem chama receber o 7, sem malloc?

Já está escrito:

```c
int *f(void) { int n = 7; return &n; }
```

Opções: `Devolver o valor: int f(void) { int n = 7; return n; }`  `Nada: retornar o endereço de uma variável local funciona; ela continua lá`  `Chamar free(&n) antes do return`

Resposta certa: `Devolver o valor: int f(void) { int n = 7; return n; }`

Se errar:

- respondeu `Nada: retornar o endereço de uma variável local funciona; ela continua lá` → A local não continua lá: sai no retorno. Devolver o valor copia o 7, e a cópia chega inteira a quem chamou. _(aponta a crença `local_survives_return`)_
- respondeu `Chamar free(&n) antes do return` → free é para blocos de malloc, e n não é um. O conserto é devolver o valor: return n;
- qualquer outro erro → Devolva o valor: return n; copia o 7 para quem chamou.

**Versão 2.** Como consertar g para quem chama receber o 3, sem malloc?

Já está escrito:

```c
int *g(void) { int total = 3; return &total; }
```

Opções: `Chamar free(&total) antes do return`  `Receber a caixa de quem chama: void g(int *destino) { *destino = 3; }`  `Nada: retornar o endereço de uma variável local funciona; ela continua lá`

Resposta certa: `Receber a caixa de quem chama: void g(int *destino) { *destino = 3; }`

Se errar:

- respondeu `Nada: retornar o endereço de uma variável local funciona; ela continua lá` → A local não continua lá: sai no retorno. Com a caixa de quem chama, g preenche algo que continua vivo. _(aponta a crença `local_survives_return`)_
- respondeu `Chamar free(&total) antes do return` → free é para blocos de malloc, e total não é um. O conserto é quem chama dar a caixa.
- qualquer outro erro → Quem chama dá a caixa, e g preenche: void g(int *destino).

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Quem chama dá a caixa para a função preencher_

**Versão 1.** Que número aparece?

```c
void preenche(int *d) { *d = 10; }

int x = 3;
preenche(&x);
printf("%d\n", x + 1);
```

Resposta certa: `11`

Se errar:

- digitou `4` → preenche escreveu 10 em x, pelo endereço. Depois disso, x + 1 é 11.
- digitou `10` → x vale 10 depois de preenche, mas o printf mostra x + 1: 11.
- qualquer outro erro → preenche escreveu 10 em x; o printf mostra x + 1: 11.

**Versão 2.** Que número aparece?

```c
void zera(int *d) { *d = 0; }

int y = 8;
zera(&y);
printf("%d\n", y);
```

Resposta certa: `0`

Se errar:

- digitou `8` → zera recebeu o endereço de y e escreveu 0 nela. y é de quem chamou, e continua viva: 0.
- qualquer outro erro → zera escreveu na caixa de quem chamou: 0.

### Degrau 5 — prática, escolher

**Versão 1.** Nenhum free aparece. Qual destes ponteiros fica pendente?

Já está escrito:

```c
int *a(void) { static int n = 1; return &n; }
int *b(void) { int n = 1; return &n; }

int *p = a();
int *q = b();
```

Opções: `q, que veio de b`  `p, que veio de a`  `Nenhum: sem free não há pendente`

Resposta certa: `q, que veio de b`

Se errar:

- respondeu `p, que veio de a` → O n de a é static: dura o programa, e p aponta para uma caixa viva. O de b saiu no retorno: q ficou pendente.
- respondeu `Nenhum: sem free não há pendente` → Há pendente sem free: o n de b saiu no retorno, e q ficou apontando para o nada.
- qualquer outro erro → q ficou pendente: o n de b saiu no retorno.

**Versão 2.** Nenhum free aparece. Qual destes ponteiros fica pendente?

Já está escrito:

```c
int *c(void) { int *b = malloc(sizeof(int)); return b; }
int *d(void) { int m = 2; return &m; }

int *p = c();
int *q = d();
```

Opções: `Nenhum: sem free não há pendente`  `p, que veio de c`  `q, que veio de d`

Resposta certa: `q, que veio de d`

Se errar:

- respondeu `p, que veio de c` → O bloco de malloc fica até o free: p aponta para uma caixa viva. O m de d saiu no retorno: q ficou pendente.
- respondeu `Nenhum: sem free não há pendente` → Há pendente sem free: o m de d saiu no retorno, e q ficou apontando para o nada.
- qualquer outro erro → q ficou pendente: o m de d saiu no retorno.

### Se errar a pergunta do topo: a revisão

> Dá para ficar com um ponteiro apontando para o nada sem chamar free nenhuma vez: basta guardar o endereço de uma local.
> O jeito certo é quem chama criar a caixa e passar o endereço dela para a função preencher.

```c
void poe(int *destino) { *destino = 7; }

int n;
poe(&n);
printf("%d\n", n);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Retornar o endereço de uma variável local funciona; ela continua lá.

```c
int *f(void) { int n = 7; return &n; }

int *p = f();
printf("%d\n", *p);
```

**f devolve o endereço da sua local n, e o trecho lê o que p alcança. O que acontece?**

- O compilador reclama: n saiu no retorno, e p não leva a caixa nenhuma _(é o que a máquina faz)_
- 7: retornar o endereço de uma local funciona, e n continua lá _(é o que a crença espera)_

O compilador reclama:

```
dereference of NULL 'p'
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer). Ao ver return &n, o gcc avisa e devolve NULL no lugar do endereço da caixa que vai sair; por isso o analisador fala em NULL. O padrão do C não diz o que esse endereço vale depois do retorno. O programa não é executado._

O que isto mostra: O compilador reclama: *p iria a lugar nenhum. n saiu no retorno de f, e o endereço dela não leva a caixa junto — p ficou pendente sem free nenhum. O jeito certo é quem chama dar a caixa.
