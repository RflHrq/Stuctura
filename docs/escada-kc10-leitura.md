# A escada do kc_10 — Ponteiro para ponteiro

Texto para leitura, gerado de `mvp/dominio/escada_kc10.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — Um ponteiro é uma caixa, e toda caixa tem endereço próprio. &p dá o endereço da caixa p — e guardar esse endereço exige uma caixa de mais um nível.

### Degrau 1 — guiado, escolher

> p é uma caixa como as outras, e toda caixa tem endereço: &p é o endereço da caixa p.
> &p não é o que p guarda, nem uma cópia de p: é onde a caixa p fica.

**Versão 1.** O que &p dá, neste trecho?

Já está escrito:

```c
int idade = 15;
int *p = &idade;
```

Opções: `O endereço da caixa p`  `Uma cópia de p: o & entrega uma cópia do ponteiro`  `O endereço de idade, que é o que p guarda`

Resposta certa: `O endereço da caixa p`

Se errar:

- respondeu `Uma cópia de p: o & entrega uma cópia do ponteiro` → O & nunca copia: ele diz ONDE a caixa fica. &p é o endereço da caixa p, e quem tiver esse endereço chega na própria p. _(aponta a crença `ampersand_copies`)_
- respondeu `O endereço de idade, que é o que p guarda` → O endereço de idade é o que está guardado DENTRO de p. &p é outra coisa: o endereço da caixa p.
- qualquer outro erro → &p é o endereço da caixa p — onde ela fica, e não o que ela guarda.

**Versão 2.** O que &q dá, neste trecho?

Já está escrito:

```c
int nota = 7;
int *q = &nota;
```

Opções: `O endereço de nota, que é o que q guarda`  `O endereço da caixa q`  `Uma cópia de q: o & entrega uma cópia do ponteiro`

Resposta certa: `O endereço da caixa q`

Se errar:

- respondeu `Uma cópia de q: o & entrega uma cópia do ponteiro` → O & nunca copia: ele diz ONDE a caixa fica. &q é o endereço da caixa q, e quem tiver esse endereço chega na própria q. _(aponta a crença `ampersand_copies`)_
- respondeu `O endereço de nota, que é o que q guarda` → O endereço de nota é o que está guardado DENTRO de q. &q é outra coisa: o endereço da caixa q.
- qualquer outro erro → &q é o endereço da caixa q — onde ela fica, e não o que ela guarda.

### Degrau 2 — guiado, completar

> Para guardar o endereço de um int *, a caixa tem uma estrela a mais: int **pp;
> pp = &p; guarda nela o endereço da caixa p.

**Versão 1.** Complete com a caixa que guarda o endereço de p.

Já está escrito:

```c
int idade;
int *p;
int **pp;

p = &idade;
```

```c
___ = &p;
```

Peças: `pp`  `p`  `idade`

Resposta certa: `pp = &p;`

Se errar:

- respondeu `p = &p;` → p guarda o endereço de um int, e &p é o endereço de um ponteiro: o compilador reclama. Quem guarda o endereço de p é a caixa de duas estrelas: pp = &p;
- respondeu `idade = &p;` → idade guarda um número, e não um endereço: o compilador reclama. Quem guarda o endereço de p é pp: pp = &p;
- qualquer outro erro → O endereço de um int * se guarda num int **: pp = &p;

**Versão 2.** Complete com a caixa que guarda o endereço de q.

Já está escrito:

```c
int nota;
int *q;
int **qq;

q = &nota;
```

```c
___ = &q;
```

Peças: `nota`  `qq`  `q`

Resposta certa: `qq = &q;`

Se errar:

- respondeu `q = &q;` → q guarda o endereço de um int, e &q é o endereço de um ponteiro: o compilador reclama. Quem guarda o endereço de q é a caixa de duas estrelas: qq = &q;
- respondeu `nota = &q;` → nota guarda um número, e não um endereço: o compilador reclama. Quem guarda o endereço de q é qq: qq = &q;
- qualquer outro erro → O endereço de um int * se guarda num int **: qq = &q;

### Degrau 3 — guiado, digitar

> Com o endereço de p guardado em pp, *pp chega na própria caixa p.

**Versão 1.** A última linha pergunta se o que *pp alcança é igual a p. Que número aparece?

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

printf("%d\n", *pp == p);
```

Resposta certa: `1`

Se errar:

- digitou `0` → pp guarda o endereço da caixa p, e *pp chega nela: o que *pp encontra é o próprio p. A pergunta é verdadeira: 1.
- digitou `15` → 15 está em idade, a dois passos de pp. O printf mostra a resposta da pergunta *pp == p, que é verdadeira: 1.
- qualquer outro erro → *pp chega na caixa p. O que ele encontra é o próprio p: 1.

**Versão 2.** A última linha pergunta se o que *qq alcança é diferente de q. Que número aparece?

```c
int nota = 7;
int *q = &nota;
int **qq = &q;

printf("%d\n", *qq != q);
```

Resposta certa: `0`

Se errar:

- digitou `1` → qq guarda o endereço da caixa q, e *qq chega nela: o que *qq encontra é o próprio q. Não é diferente: 0.
- digitou `7` → 7 está em nota, a dois passos de qq. O printf mostra a resposta da pergunta *qq != q, que é falsa: 0.
- qualquer outro erro → *qq chega na caixa q. O que ele encontra é o próprio q: a resposta é 0.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: &p é o endereço da caixa p_

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idade;
int *p;
int **pp;

p = &idade;
```

Opções: `pp = &p;`  `pp = p;`  `pp = &idade;`

Resposta certa: `pp = &p;`

Se errar:

- respondeu `pp = p;` → p guarda o endereço de um int, e pp espera o endereço de um ponteiro: o compilador reclama. O endereço da caixa p é &p.
- respondeu `pp = &idade;` → &idade é o endereço de um int. pp guarda o endereço de um ponteiro para int, e o compilador reclama. O que serve é &p.
- qualquer outro erro → pp guarda o endereço de um ponteiro: pp = &p;

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int nota;
int *q;
int **qq;

q = &nota;
```

Opções: `qq = &nota;`  `qq = q;`  `qq = &q;`

Resposta certa: `qq = &q;`

Se errar:

- respondeu `qq = q;` → q guarda o endereço de um int, e qq espera o endereço de um ponteiro: o compilador reclama. O endereço da caixa q é &q.
- respondeu `qq = &nota;` → &nota é o endereço de um int. qq guarda o endereço de um ponteiro para int, e o compilador reclama. O que serve é &q.
- qualquer outro erro → qq guarda o endereço de um ponteiro: qq = &q;

### Degrau 5 — prática, digitar

**Versão 1.** p começa apontando para nota. O trecho escreve outro endereço em p, por *pp. Que número aparece?

```c
int idade = 15;
int nota = 7;
int *p = &nota;
int **pp = &p;

*pp = &idade;
printf("%d\n", *p);
```

Resposta certa: `15`

Se errar:

- digitou `7` → *pp é a própria caixa p: a linha *pp = &idade; trocou o endereço que p guardava. Agora *p chega em idade: 15.
- qualquer outro erro → Por *pp o trecho escreveu na caixa p, que passou a apontar para idade: 15.

**Versão 2.** q começa apontando para idade. O trecho escreve outro endereço em q, por *qq. Que número aparece?

```c
int idade = 20;
int nota = 9;
int *q = &idade;
int **qq = &q;

*qq = &nota;
printf("%d\n", *q);
```

Resposta certa: `9`

Se errar:

- digitou `20` → *qq é a própria caixa q: a linha *qq = &nota; trocou o endereço que q guardava. Agora *q chega em nota: 9.
- qualquer outro erro → Por *qq o trecho escreveu na caixa q, que passou a apontar para nota: 9.

### Se errar a pergunta do topo: a revisão

> p é uma caixa, e toda caixa tem endereço: &p é o endereço da caixa p.
> Para guardar esse endereço, a caixa tem uma estrela a mais: int **pp = &p;

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

printf("%d\n", *pp == p);
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> &x entrega uma cópia de x, e é a cópia que a função recebe.

```c
int idade = 15;
int nota = 7;
int *p = &idade;
int **pp = &p;

*pp = &nota;
printf("%d\n", *p);
```

**pp guarda &p. O trecho escreve &nota por *pp, e depois mostra o que p alcança. O que aparece?**

- 15: &p entregou uma cópia de p, e o p de verdade não mudou _(é o que a crença espera)_
- 7 _(é o que a máquina faz)_

A máquina imprime:

```
7
```

O que isto mostra: Saiu 7. &p não é uma cópia de p: é o endereço da própria caixa p. Por ele, *pp chegou nessa caixa e trocou o que estava lá — e p passou a apontar para nota.

## B2 — Cada * dá um passo: vai de uma caixa até a caixa cujo endereço ela guarda. Um passo por estrela, nem mais nem menos.

### Degrau 1 — guiado, escolher

> p não é outro nome de idade: é uma caixa, que guarda o endereço de idade.
> O * é um passo: sai da caixa p e vai até a caixa cujo endereço está lá.

**Versão 1.** O que p é, neste trecho?

Já está escrito:

```c
int idade = 15;
int *p = &idade;
```

Opções: `Uma caixa que guarda o endereço de idade`  `Outro nome da variável idade: o * não é um passo`  `Uma cópia de idade`

Resposta certa: `Uma caixa que guarda o endereço de idade`

Se errar:

- respondeu `Outro nome da variável idade: o * não é um passo` → Um nome não tem lugar próprio, e p tem: é uma caixa, com o endereço de idade dentro. É por isso que *p é um passo, de p até idade. _(aponta a crença `pointer_is_just_a_name`)_
- respondeu `Uma cópia de idade` → p não guarda o 15: guarda o endereço de idade. Para chegar ao 15 dá-se um passo, com *p.
- qualquer outro erro → p é uma caixa com o endereço de idade. *p é o passo até lá.

**Versão 2.** O que q é, neste trecho?

Já está escrito:

```c
int nota = 7;
int *q = &nota;
```

Opções: `Uma cópia de nota`  `Uma caixa que guarda o endereço de nota`  `Outro nome da variável nota: o * não é um passo`

Resposta certa: `Uma caixa que guarda o endereço de nota`

Se errar:

- respondeu `Outro nome da variável nota: o * não é um passo` → Um nome não tem lugar próprio, e q tem: é uma caixa, com o endereço de nota dentro. É por isso que *q é um passo, de q até nota. _(aponta a crença `pointer_is_just_a_name`)_
- respondeu `Uma cópia de nota` → q não guarda o 7: guarda o endereço de nota. Para chegar ao 7 dá-se um passo, com *q.
- qualquer outro erro → q é uma caixa com o endereço de nota. *q é o passo até lá.

### Degrau 2 — guiado, digitar

> Com duas estrelas são dois passos: **pp vai de pp a p, e de p a idade.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

printf("%d\n", **pp);
```

Resposta certa: `15`

Se errar:

- digitou `0` → O primeiro * vai de pp até p; o segundo, de p até idade. Dois passos, e o que se acha lá é 15.
- qualquer outro erro → Dois passos: de pp a p, de p a idade. Lá está o 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota = 7;
int *q = &nota;
int **qq = &q;

printf("%d\n", **qq);
```

Resposta certa: `7`

Se errar:

- digitou `0` → O primeiro * vai de qq até q; o segundo, de q até nota. Dois passos, e o que se acha lá é 7.
- qualquer outro erro → Dois passos: de qq a q, de q a nota. Lá está o 7.

### Degrau 3 — guiado, escolher

> Um passo chega num ponteiro; dois passos chegam num int.
> O que cada um aceita receber é diferente: *pp recebe endereço, **pp recebe número.

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idade = 15;
int nota = 7;
int *p = &idade;
int **pp = &p;
```

Opções: `*pp = &nota;`  `*pp = 9;`  `**pp = &nota;`

Resposta certa: `*pp = &nota;`

Se errar:

- respondeu `*pp = 9;` → *pp é a caixa p, que guarda endereço — e 9 é um número: o compilador reclama. Ali cabe um endereço: *pp = &nota;
- respondeu `**pp = &nota;` → **pp é a caixa idade, que guarda número — e &nota é um endereço: o compilador reclama. Endereço se escreve a um passo: *pp = &nota;
- qualquer outro erro → A um passo está p, que recebe endereço: *pp = &nota;

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idade = 15;
int nota = 7;
int *q = &nota;
int **qq = &q;
```

Opções: `**qq = &idade;`  `**qq = 9;`  `*qq = 9;`

Resposta certa: `**qq = 9;`

Se errar:

- respondeu `**qq = &idade;` → **qq é a caixa nota, que guarda número — e &idade é um endereço: o compilador reclama. A dois passos cabe um número: **qq = 9;
- respondeu `*qq = 9;` → *qq é a caixa q, que guarda endereço — e 9 é um número: o compilador reclama. O número se escreve a dois passos: **qq = 9;
- qualquer outro erro → A dois passos está nota, que recebe número: **qq = 9;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Um passo por estrela_

**Versão 1.** O trecho escreve 9 a dois passos de pp. Que número aparece?

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

**pp = 9;
printf("%d\n", idade);
```

Resposta certa: `9`

Se errar:

- digitou `15` → Dois passos a partir de pp: o primeiro chega em p, o segundo em idade. O 9 foi escrito em idade.
- qualquer outro erro → **pp chega em idade em dois passos, e escreveu 9 lá.

**Versão 2.** O trecho escreve 0 a dois passos de qq. Que número aparece?

```c
int nota = 7;
int *q = &nota;
int **qq = &q;

**qq = 0;
printf("%d\n", nota);
```

Resposta certa: `0`

Se errar:

- digitou `7` → Dois passos a partir de qq: o primeiro chega em q, o segundo em nota. O 0 foi escrito em nota.
- qualquer outro erro → **qq chega em nota em dois passos, e escreveu 0 lá.

### Degrau 5 — prática, digitar

**Versão 1.** A um passo o trecho troca o endereço em p; a dois, escreve 0. Que número aparece?

```c
int idade = 15;
int nota = 7;
int *p = &idade;
int **pp = &p;

*pp = &nota;
**pp = 0;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → A primeira linha trocou o endereço em p, que passou a apontar para nota. O 0, a dois passos, foi para nota; idade continua com 15.
- qualquer outro erro → p passou a apontar para nota, e foi nota que recebeu o 0. idade continua 15.

**Versão 2.** A um passo o trecho troca o endereço em q; a dois, escreve 0. Que número aparece?

```c
int idade = 15;
int nota = 7;
int *q = &nota;
int **qq = &q;

*qq = &idade;
**qq = 0;
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `0` → A primeira linha trocou o endereço em q, que passou a apontar para idade. O 0, a dois passos, foi para idade; nota continua com 7.
- qualquer outro erro → q passou a apontar para idade, e foi idade que recebeu o 0. nota continua 7.

### Se errar a pergunta do topo: a revisão

> Cada * dá um passo: de uma caixa até a caixa cujo endereço ela guarda.
> *pp chega em p. **pp dá mais um passo, e chega em idade.

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

printf("%d\n", **pp);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> p é só outro nome da variável apontada: o * não é um passo.

```c
int idade = 15;
int nota = 7;
int *p = &idade;

p = &nota;
*p = 0;
printf("%d\n", idade);
```

**p começa apontando para idade, e depois recebe o endereço de nota. O trecho escreve 0 por *p e mostra idade. O que aparece?**

- 0: p é outro nome de idade, e escrever por ele muda idade _(é o que a crença espera)_
- 15 _(é o que a máquina faz)_

A máquina imprime:

```
15
```

O que isto mostra: Saiu 15. p não é outro nome de idade: é uma caixa com um endereço, e o endereço foi trocado. O * deu um passo até onde p aponta AGORA, que é nota — e idade ficou como estava.

## B3 — O tipo é que diz quantos passos existem até o valor. Não dá para chutar nem descobrir depois, e não há um ponteiro-para-ponteiro genérico.

### Degrau 1 — guiado, escolher

> O tipo diz quantos passos há até o valor: int * é um nível, int ** são dois.
> As estrelas da declaração fixam isso. Não dá para dar um passo que o tipo não tem.

**Versão 1.** Quantos passos há de pp até o int?

Já está escrito:

```c
int **pp;
```

Opções: `Dois: o tipo tem duas estrelas`  `Um: todo ponteiro chega direto no valor`  `Depende de quantas estrelas você usar depois`

Resposta certa: `Dois: o tipo tem duas estrelas`

Se errar:

- respondeu `Um: todo ponteiro chega direto no valor` → Cada estrela do tipo é um nível, e cada nível é um passo. int ** tem duas: de pp a um ponteiro, e dele ao int.
- respondeu `Depende de quantas estrelas você usar depois` → Quem decide é a declaração, e não o uso: int ** tem dois níveis, e é só isso que se pode percorrer.
- qualquer outro erro → int ** tem dois níveis: são dois passos até o int.

**Versão 2.** Quantos passos há de q até o int?

Já está escrito:

```c
int *q;
```

Opções: `Depende de quantas estrelas você usar depois`  `Dois: todo ponteiro passa por outro ponteiro`  `Um: o tipo tem uma estrela`

Resposta certa: `Um: o tipo tem uma estrela`

Se errar:

- respondeu `Dois: todo ponteiro passa por outro ponteiro` → Cada estrela do tipo é um nível, e cada nível é um passo. int * tem uma só: de q direto ao int.
- respondeu `Depende de quantas estrelas você usar depois` → Quem decide é a declaração, e não o uso: int * tem um nível, e é só isso que se pode percorrer.
- qualquer outro erro → int * tem um nível: é um passo até o int.

### Degrau 2 — guiado, digitar

> void * é um ponteiro que guarda qualquer endereço, sem saber o tipo do que há lá.
> Para usar o que ele aponta, converte-se de volta: *(int *)v.

**Versão 1.** v recebe o endereço que está em p, e é convertido de volta para int *. Que número aparece?

```c
int idade = 15;
int *p = &idade;
void *v;

v = p;
printf("%d\n", *(int *)v);
```

Resposta certa: `15`

Se errar:

- digitou `0` → v guarda o mesmo endereço que está em p, o de idade. Convertido de volta para int *, o * chega em idade: 15.
- qualquer outro erro → v guarda o endereço de idade. Convertido para int *, chega no 15.

**Versão 2.** v recebe o endereço que está em q, e é convertido de volta para int *. Que número aparece?

```c
int nota = 7;
int *q = &nota;
void *v;

v = q;
printf("%d\n", *(int *)v);
```

Resposta certa: `7`

Se errar:

- digitou `0` → v guarda o mesmo endereço que está em q, o de nota. Convertido de volta para int *, o * chega em nota: 7.
- qualquer outro erro → v guarda o endereço de nota. Convertido para int *, chega no 7.

### Degrau 3 — guiado, escolher

> O void * guarda qualquer endereço, de qualquer nível.
> O void ** não é um genérico de dois níveis: é o endereço de um void *, e só disso.

**Versão 1.** v é um void *, e vv é um void **. Qual dos dois pode guardar &p, o endereço de um int *?

Já está escrito:

```c
int idade;
int *p;
void *v;
void **vv;
```

Opções: `Só v: void * guarda qualquer endereço`  `Os dois: void * aceita qualquer coisa, e void ** serve a qualquer nível`  `Só vv: &p tem dois níveis, e vv também`

Resposta certa: `Só v: void * guarda qualquer endereço`

Se errar:

- respondeu `Os dois: void * aceita qualquer coisa, e void ** serve a qualquer nível` → O void * serve a qualquer endereço. O void ** não: ele é o endereço de um void *, e &p é o endereço de um int *. O compilador reclama. _(aponta a crença `voidptr_is_universal`)_
- respondeu `Só vv: &p tem dois níveis, e vv também` → Não basta o número de estrelas bater: vv é o endereço de um void *, e &p é o endereço de um int *. Quem aceita qualquer endereço é v.
- qualquer outro erro → v, um void *, guarda qualquer endereço. vv só guarda o endereço de um void *.

**Versão 2.** v é um void *, e vv é um void **. Qual dos dois pode guardar &q, o endereço de um char *?

Já está escrito:

```c
char letra;
char *q;
void **vv;
void *v;
```

Opções: `Só vv: &q tem dois níveis, e vv também`  `Os dois: void * aceita qualquer coisa, e void ** serve a qualquer nível`  `Só v: void * guarda qualquer endereço`

Resposta certa: `Só v: void * guarda qualquer endereço`

Se errar:

- respondeu `Os dois: void * aceita qualquer coisa, e void ** serve a qualquer nível` → O void * serve a qualquer endereço. O void ** não: ele é o endereço de um void *, e &q é o endereço de um char *. O compilador reclama. _(aponta a crença `voidptr_is_universal`)_
- respondeu `Só vv: &q tem dois níveis, e vv também` → Não basta o número de estrelas bater: vv é o endereço de um void *, e &q é o endereço de um char *. Quem aceita qualquer endereço é v.
- qualquer outro erro → v, um void *, guarda qualquer endereço. vv só guarda o endereço de um void *.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: O tipo fixa os níveis_

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
char letra;
char *cp;
char **cc;
int **pp;

cp = &letra;
```

Opções: `cc = &cp;`  `pp = &cp;`  `pp = cp;`

Resposta certa: `cc = &cp;`

Se errar:

- respondeu `pp = &cp;` → &cp é o endereço de um char *, e pp guarda o endereço de um int *: os dois níveis batem, o tipo do fim não. O compilador reclama.
- respondeu `pp = cp;` → cp tem um nível, e pp tem dois: o compilador reclama. O endereço de cp, que é um char *, se guarda num char **: cc = &cp;
- qualquer outro erro → O endereço de um char * se guarda num char **: cc = &cp;

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idade;
int *p;
int **pp;
char **cc;

p = &idade;
```

Opções: `cc = &p;`  `pp = p;`  `pp = &p;`

Resposta certa: `pp = &p;`

Se errar:

- respondeu `cc = &p;` → &p é o endereço de um int *, e cc guarda o endereço de um char *: os dois níveis batem, o tipo do fim não. O compilador reclama.
- respondeu `pp = p;` → p tem um nível, e pp tem dois: o compilador reclama. O endereço de p, que é um int *, se guarda num int **: pp = &p;
- qualquer outro erro → O endereço de um int * se guarda num int **: pp = &p;

### Degrau 5 — prática, digitar

**Versão 1.** v guarda o endereço de nota. O trecho o converte para int * e escreve 0 por ele. Que número aparece?

```c
int nota = 7;
void *v;

v = &nota;
*(int *)v = 0;
printf("%d\n", nota);
```

Resposta certa: `0`

Se errar:

- digitou `7` → v guarda o endereço de nota. Convertido para int *, o * chega em nota, e o 0 foi escrito lá.
- qualquer outro erro → Convertido para int *, v chega em nota, que recebeu 0.

**Versão 2.** v guarda o endereço de idade. O trecho o converte para int * e soma 1 por ele. Que número aparece?

```c
int idade = 15;
void *v;

v = &idade;
*(int *)v = *(int *)v + 1;
printf("%d\n", idade);
```

Resposta certa: `16`

Se errar:

- digitou `15` → v guarda o endereço de idade. Convertido para int *, o * chega em idade, e foi nela que o 1 foi somado.
- qualquer outro erro → Convertido para int *, v chega em idade, que passou a valer 16.

### Se errar a pergunta do topo: a revisão

> O tipo diz quantos passos há até o valor: int * é um nível, int ** são dois.
> void * guarda qualquer endereço. void ** não é um genérico de dois níveis: é o endereço de um void *.

```c
int idade = 15;
int *p = &idade;
void *v;

v = p;
printf("%d\n", *(int *)v);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> void * aceita qualquer coisa, e void ** serve a qualquer nível.

```c
int idade;
int *p;
void *v;
void **vv;

p = &idade;
v = &p;
vv = &p;
```

**v é um void *, e vv é um void **. As duas últimas linhas guardam &p em cada um. De qual delas o compilador reclama?**

- De nenhuma: void ** serve a qualquer nível _(é o que a crença espera)_
- Da última: &p não é o endereço de um void * _(é o que a máquina faz)_

O compilador reclama:

```
incompatible pointer type
```

_Mensagem do gcc 16.2. Nele a reclamação é um erro; em versões mais antigas, um aviso. Nos dois casos ele reclama da última linha, e só dela._

O que isto mostra: O compilador aceita v = &p; e reclama de vv = &p;. O void * guarda qualquer endereço, até o de um ponteiro. O void ** não é um genérico de dois níveis: é o endereço de um void *, e &p é o endereço de um int *.

## I1 — Para uma função mudar o p de quem chamou, ela precisa receber o endereço de p — não o p.

### Degrau 1 — guiado, escolher

> A função que recebe p recebe uma cópia do endereço que estava no ponteiro de quem chamou.
> Trocar a cópia não troca o ponteiro de quem chamou.

**Versão 1.** A função troca o parâmetro dela. O q de quem chamou muda?

Já está escrito:

```c
void troca(int *p, int *novo) { p = novo; }

int idade = 15;
int nota = 7;
int *q = &idade;

troca(q, &nota);
```

Opções: `Não: p é uma cópia do endereço que estava em q`  `Muda: trocar o parâmetro ponteiro troca o ponteiro de quem chamou`  `Muda, mas volta quando a função termina`

Resposta certa: `Não: p é uma cópia do endereço que estava em q`

Se errar:

- respondeu `Muda: trocar o parâmetro ponteiro troca o ponteiro de quem chamou` → p é uma caixa da função, com uma cópia do endereço que estava em q. A linha p = novo; escreve em p; q é outra caixa, e fica como estava. _(aponta a crença `modify_pp_changes_p`)_
- respondeu `Muda, mas volta quando a função termina` → q não muda nem por um instante: a função só escreve em p, a cópia dela. q continua apontando para idade o tempo todo.
- qualquer outro erro → A função trocou a cópia. q continua apontando para idade.

**Versão 2.** A função apaga o parâmetro dela. O q de quem chamou muda?

Já está escrito:

```c
void larga(int *p) { p = NULL; }

int nota = 7;
int *q = &nota;

larga(q);
```

Opções: `Muda: trocar o parâmetro ponteiro troca o ponteiro de quem chamou`  `Muda, mas volta quando a função termina`  `Não: p é uma cópia do endereço que estava em q`

Resposta certa: `Não: p é uma cópia do endereço que estava em q`

Se errar:

- respondeu `Muda: trocar o parâmetro ponteiro troca o ponteiro de quem chamou` → p é uma caixa da função, com uma cópia do endereço que estava em q. A linha p = NULL; escreve em p; q é outra caixa, e fica como estava. _(aponta a crença `modify_pp_changes_p`)_
- respondeu `Muda, mas volta quando a função termina` → q não muda nem por um instante: a função só escreve em p, a cópia dela. q continua apontando para nota o tempo todo.
- qualquer outro erro → A função apagou a cópia. q continua apontando para nota.

### Degrau 2 — guiado, digitar

> Para trocar o ponteiro de quem chamou, a função recebe o endereço dele, num int **.
> Com *pp ela chega na caixa q, e escreve nela.

**Versão 1.** A função recebe o endereço de q. Que número aparece?

```c
void troca(int **pp, int *novo) { *pp = novo; }

int idade = 15;
int nota = 7;
int *q = &idade;

troca(&q, &nota);
printf("%d\n", *q);
```

Resposta certa: `7`

Se errar:

- digitou `15` → Desta vez a função recebeu o endereço da caixa q. Com *pp ela escreveu em q, que passou a apontar para nota: 7.
- qualquer outro erro → Com o endereço de q, a função trocou o que q guardava: agora aponta para nota, 7.

**Versão 2.** A função recebe o endereço de q. Que número aparece?

```c
void troca(int **pp, int *novo) { *pp = novo; }

int idade = 15;
int nota = 7;
int *q = &nota;

troca(&q, &idade);
printf("%d\n", *q);
```

Resposta certa: `15`

Se errar:

- digitou `7` → Desta vez a função recebeu o endereço da caixa q. Com *pp ela escreveu em q, que passou a apontar para idade: 15.
- qualquer outro erro → Com o endereço de q, a função trocou o que q guardava: agora aponta para idade, 15.

### Degrau 3 — guiado, completar

> Na chamada vai o endereço do ponteiro, com o &: troca(&q, ...).

**Versão 1.** Complete a chamada para a função trocar o que q guarda.

Já está escrito:

```c
void troca(int **pp, int *novo) { *pp = novo; }

int idade = 15;
int nota = 7;
int *q = &idade;
```

```c
troca(___, &nota);
```

Peças: `&q`  `q`  `*q`

Resposta certa: `troca(&q, &nota);`

Se errar:

- respondeu `troca(q, &nota);` → q entrega uma cópia do endereço de idade, e a função espera o endereço de um ponteiro: o compilador reclama. O endereço da caixa q é &q.
- respondeu `troca(*q, &nota);` → *q é o número guardado em idade, e a função espera o endereço de um ponteiro: o compilador reclama. O endereço da caixa q é &q.
- qualquer outro erro → A função espera o endereço do ponteiro: troca(&q, &nota);

**Versão 2.** Complete a chamada para a função trocar o que p guarda.

Já está escrito:

```c
void troca(int **pp, int *novo) { *pp = novo; }

int idade = 15;
int nota = 7;
int *p = &nota;
```

```c
troca(___, &idade);
```

Peças: `*p`  `&p`  `p`

Resposta certa: `troca(&p, &idade);`

Se errar:

- respondeu `troca(p, &idade);` → p entrega uma cópia do endereço de nota, e a função espera o endereço de um ponteiro: o compilador reclama. O endereço da caixa p é &p.
- respondeu `troca(*p, &idade);` → *p é o número guardado em nota, e a função espera o endereço de um ponteiro: o compilador reclama. O endereço da caixa p é &p.
- qualquer outro erro → A função espera o endereço do ponteiro: troca(&p, &idade);

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Para mudar o ponteiro de fora, a função recebe &p_

**Versão 1.** A função recebe o endereço de q e escreve NULL por ele. A última linha pergunta se q vale NULL. Que número aparece?

```c
void solta(int **pp) { *pp = NULL; }

int idade = 15;
int *q = &idade;

solta(&q);
printf("%d\n", q == NULL);
```

Resposta certa: `1`

Se errar:

- digitou `0` → A função recebeu o endereço da caixa q, e *pp é a própria q: o NULL foi escrito nela. A pergunta é verdadeira: 1.
- qualquer outro erro → Com o endereço de q, a função escreveu NULL na própria q: 1.

**Versão 2.** A função recebe uma cópia de q e escreve NULL nela. A última linha pergunta se q vale NULL. Que número aparece?

```c
void solta(int *p) { p = NULL; }

int nota = 7;
int *q = &nota;

solta(q);
printf("%d\n", q == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → A função recebeu uma cópia do endereço, e o NULL foi para a cópia. q é outra caixa, e continua apontando para nota: 0.
- qualquer outro erro → A função só tinha uma cópia: q continua apontando para nota, e a resposta é 0.

### Degrau 5 — prática, digitar

**Versão 1.** A função faz q apontar para nota, e depois o trecho escreve 0 por q. Que número aparece?

```c
void aponta(int **pp, int *alvo) { *pp = alvo; }

int idade = 15;
int nota = 7;
int *q = &idade;

aponta(&q, &nota);
*q = 0;
printf("%d\n", nota);
```

Resposta certa: `0`

Se errar:

- digitou `7` → A função recebeu o endereço de q e trocou o que q guardava: q passou a apontar para nota. O 0 escrito por *q foi para nota.
- qualquer outro erro → q passou a apontar para nota, e o 0 foi escrito nela.

**Versão 2.** A função faz q apontar para nota, e depois o trecho escreve 0 por q. Que número aparece?

```c
void aponta(int **pp, int *alvo) { *pp = alvo; }

int idade = 15;
int nota = 7;
int *q = &idade;

aponta(&q, &nota);
*q = 0;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → A função trocou o que q guardava: q passou a apontar para nota, e foi nota que recebeu o 0. idade continua com 15.
- qualquer outro erro → q passou a apontar para nota. idade não foi tocada: 15.

### Se errar a pergunta do topo: a revisão

> A função que recebe p recebe uma cópia do endereço. Trocar a cópia não troca o p de quem chamou.
> Para trocar o p de quem chamou, ela recebe o endereço dele, &p, num int **.

```c
void troca(int **pp, int *novo) { *pp = novo; }

int idade = 15;
int nota = 7;
int *q = &idade;

troca(&q, &nota);
printf("%d\n", *q);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Trocar o parâmetro ponteiro dentro da função altera o ponteiro de quem chamou.

```c
void troca(int *p, int *novo) { p = novo; }

int idade = 15;
int nota = 7;
int *q = &idade;

troca(q, &nota);
printf("%d\n", *q);
```

**A função troca o parâmetro p dela pelo endereço de nota. Depois da chamada, o trecho mostra o que q alcança. O que aparece?**

- 15 _(é o que a máquina faz)_
- 7: trocar o parâmetro trocou o ponteiro de quem chamou _(é o que a crença espera)_

A máquina imprime:

```
15
```

O que isto mostra: Saiu 15. A função trocou p, a cópia dela. O q de quem chamou é outra caixa, e continua apontando para idade. Para trocar q, ela teria de receber o endereço de q.

## I2 — int a[3][4] é um bloco de doze caixas grudadas. Não são três caixas apontando para fileiras separadas.

### Degrau 1 — guiado, escolher

> int a[3][4]; cria doze caixas de int, grudadas: três fileiras de quatro.
> Não há ponteiro nenhum ali: nem três, nem um.

**Versão 1.** O que esta linha cria?

Já está escrito:

```c
int a[3][4];
```

Opções: `Doze caixas de int, grudadas`  `Três ponteiros para fileiras: por isso a serve onde se espera int **`  `Um ponteiro para ponteiro, com tudo dentro`

Resposta certa: `Doze caixas de int, grudadas`

Se errar:

- respondeu `Três ponteiros para fileiras: por isso a serve onde se espera int **` → Não há ponteiro nenhum ali: são doze caixas de int, uma depois da outra. Por não haver ponteiro, a não serve onde se espera um int **. _(aponta a crença `array2d_is_double_pointer`)_
- respondeu `Um ponteiro para ponteiro, com tudo dentro` → Um ponteiro para ponteiro é uma caixa só, com um endereço. A linha cria outra coisa: doze caixas de int, grudadas.
- qualquer outro erro → São doze caixas de int grudadas, em três fileiras de quatro. Ponteiro, nenhum.

**Versão 2.** O que esta linha cria?

Já está escrito:

```c
int b[2][5];
```

Opções: `Um ponteiro para ponteiro, com tudo dentro`  `Dez caixas de int, grudadas`  `Dois ponteiros para fileiras: por isso b serve onde se espera int **`

Resposta certa: `Dez caixas de int, grudadas`

Se errar:

- respondeu `Dois ponteiros para fileiras: por isso b serve onde se espera int **` → Não há ponteiro nenhum ali: são dez caixas de int, uma depois da outra. Por não haver ponteiro, b não serve onde se espera um int **. _(aponta a crença `array2d_is_double_pointer`)_
- respondeu `Um ponteiro para ponteiro, com tudo dentro` → Um ponteiro para ponteiro é uma caixa só, com um endereço. A linha cria outra coisa: dez caixas de int, grudadas.
- qualquer outro erro → São dez caixas de int grudadas, em duas fileiras de cinco. Ponteiro, nenhum.

### Degrau 2 — guiado, digitar

> a[1][0] é a fileira 1, posição 0. As duas contagens começam em 0.
> A lista entre chaves vem fileira por fileira.

**Versão 1.** Que número este trecho mostra na tela?

```c
int a[2][3] = {{1, 2, 3}, {4, 5, 6}};

printf("%d\n", a[1][0]);
```

Resposta certa: `4`

Se errar:

- digitou `1` → a[0] é a primeira fileira, a do 1, 2 e 3. a[1] é a segunda, e a posição 0 dela guarda 4.
- digitou `2` → O primeiro número escolhe a fileira, e o segundo a posição nela. a[1][0] é a segunda fileira, primeira posição: 4.
- qualquer outro erro → a[1] é a segunda fileira, e a posição 0 dela guarda 4.

**Versão 2.** Que número este trecho mostra na tela?

```c
int b[2][3] = {{7, 8, 9}, {15, 16, 17}};

printf("%d\n", b[0][2]);
```

Resposta certa: `9`

Se errar:

- digitou `17` → b[0] é a primeira fileira, a do 7, 8 e 9. A posição 2 dela é a terceira: 9. O 17 está na outra fileira.
- digitou `8` → A contagem começa em 0: a posição 2 é a terceira da fileira. Em b[0], é o 9.
- qualquer outro erro → b[0] é a primeira fileira, e a posição 2 dela guarda 9.

### Degrau 3 — guiado, digitar

> sizeof m mede as caixas todas; sizeof m[0] mede uma fileira.
> Uma fileira é um array, e não um ponteiro.

**Versão 1.** m tem três fileiras de quatro chars. Que número aparece?

```c
char m[3][4];

printf("%zu\n", sizeof m);
```

Resposta certa: `12`

Se errar:

- digitou `3` → 3 é o número de fileiras. sizeof m mede as caixas todas: três fileiras de quatro, 12.
- digitou `4` → 4 é o tamanho de uma fileira. sizeof m mede as caixas todas: três fileiras de quatro, 12.
- qualquer outro erro → sizeof m mede as doze caixas: três fileiras de quatro.

**Versão 2.** t tem duas fileiras de cinco chars. Que número aparece?

```c
char t[2][5];

printf("%zu\n", sizeof t);
```

Resposta certa: `10`

Se errar:

- digitou `2` → 2 é o número de fileiras. sizeof t mede as caixas todas: duas fileiras de cinco, 10.
- digitou `5` → 5 é o tamanho de uma fileira. sizeof t mede as caixas todas: duas fileiras de cinco, 10.
- qualquer outro erro → sizeof t mede as dez caixas: duas fileiras de cinco.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A matriz é um bloco só de caixas_

**Versão 1.** t tem duas fileiras de cinco chars. O trecho mostra o tamanho de UMA fileira. Que número aparece?

```c
char t[2][5];

printf("%zu\n", sizeof t[0]);
```

Resposta certa: `5`

Se errar:

- digitou `10` → 10 são as caixas todas. t[0] é uma fileira só, de cinco caixas: 5.
- digitou `8` → 8 seria o tamanho de um ponteiro nesta máquina. t[0] não é um ponteiro: é uma fileira de cinco caixas de char, 5.
- qualquer outro erro → t[0] é uma fileira, um array de cinco chars: 5.

**Versão 2.** g tem quatro fileiras de três chars. O trecho mostra o tamanho de UMA fileira. Que número aparece?

```c
char g[4][3];

printf("%zu\n", sizeof g[0]);
```

Resposta certa: `3`

Se errar:

- digitou `12` → 12 são as caixas todas. g[0] é uma fileira só, de três caixas: 3.
- digitou `8` → 8 seria o tamanho de um ponteiro nesta máquina. g[0] não é um ponteiro: é uma fileira de três caixas de char, 3.
- qualquer outro erro → g[0] é uma fileira, um array de três chars: 3.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int a[3][4];
int *p;
int **pp;
```

Opções: `p = a[0];`  `pp = a;`  `pp = a[0];`

Resposta certa: `p = a[0];`

Se errar:

- respondeu `pp = a;` → a não é um ponteiro para ponteiro: é o bloco das doze caixas, e numa conta vira o endereço de uma fileira. O compilador reclama.
- respondeu `pp = a[0];` → a[0] é uma fileira de ints, e numa conta vira o endereço de um int — não o de um ponteiro: o compilador reclama. Quem aponta para int é p.
- qualquer outro erro → a[0] é uma fileira de ints, e vira o endereço do primeiro: p = a[0];

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int b[2][5];
int **qq;
int *q;
```

Opções: `qq = b;`  `qq = b[1];`  `q = b[1];`

Resposta certa: `q = b[1];`

Se errar:

- respondeu `qq = b;` → b não é um ponteiro para ponteiro: é o bloco das dez caixas, e numa conta vira o endereço de uma fileira. O compilador reclama.
- respondeu `qq = b[1];` → b[1] é uma fileira de ints, e numa conta vira o endereço de um int — não o de um ponteiro: o compilador reclama. Quem aponta para int é q.
- qualquer outro erro → b[1] é uma fileira de ints, e vira o endereço do primeiro dela: q = b[1];

### Se errar a pergunta do topo: a revisão

> int a[3][4]; cria doze caixas de int, grudadas: três fileiras de quatro.
> Não há ponteiro nenhum ali. Uma fileira, a[0], é um array de quatro, e não um ponteiro.

```c
int a[2][3] = {{1, 2, 3}, {4, 5, 6}};

printf("%d\n", a[1][0]);
```

A máquina imprime:

```
4
```

### Se a pessoa disser a crença: a prova

Você disse:

> int a[N][M] pode ser passado onde se espera int **.

```c
char m[3][4];

printf("%zu\n", sizeof m);
printf("%zu\n", sizeof m[0]);
```

**m tem três fileiras de quatro chars. O trecho mostra sizeof m, e depois sizeof m[0], o tamanho de uma fileira. O que aparece?**

- 12 e 4: doze caixas, e uma fileira de quatro _(é o que a máquina faz)_
- Tamanhos de ponteiro: m são três ponteiros para fileiras _(é o que a crença espera)_

A máquina imprime:

```
12
4
```

O que isto mostra: Saíram 12 e 4. m é um bloco só, de doze caixas, e uma fileira são quatro caixas — não um ponteiro. Como não há ponteiro nenhum ali, m não serve onde se espera um ponteiro para ponteiro.

## I3 — pp e p são duas caixas diferentes, uma guardando o endereço da outra. *pp chega em p; **pp dá mais um passo e chega no número.

### Degrau 1 — guiado, escolher

> pp e p são duas caixas: pp guarda o endereço de p, e p guarda o endereço de idade.
> **pp não pula direto para o número: passa por p, e só então chega em idade.

**Versão 1.** Como **pp chega no 15?

Já está escrito:

```c
int idade = 15;
int *p = &idade;
int **pp = &p;
```

Opções: `Em dois passos: de pp a p, e de p a idade`  `Direto: **pp acessa o dado final, e o nível a mais se resolve sozinho`  `Em um passo: pp já guarda o endereço de idade`

Resposta certa: `Em dois passos: de pp a p, e de p a idade`

Se errar:

- respondeu `Direto: **pp acessa o dado final, e o nível a mais se resolve sozinho` → Não há atalho: o primeiro * sai de pp e chega em p; o segundo sai de p e chega em idade. Se p mudar de endereço, **pp muda junto. _(aponta a crença `double_deref_is_data`)_
- respondeu `Em um passo: pp já guarda o endereço de idade` → pp guarda o endereço de p, e não o de idade. Até idade são dois passos: de pp a p, e de p a idade.
- qualquer outro erro → São dois passos, e o do meio passa por p.

**Versão 2.** Como **qq chega no 7?

Já está escrito:

```c
int nota = 7;
int *q = &nota;
int **qq = &q;
```

Opções: `Em um passo: qq já guarda o endereço de nota`  `Em dois passos: de qq a q, e de q a nota`  `Direto: **qq acessa o dado final, e o nível a mais se resolve sozinho`

Resposta certa: `Em dois passos: de qq a q, e de q a nota`

Se errar:

- respondeu `Direto: **qq acessa o dado final, e o nível a mais se resolve sozinho` → Não há atalho: o primeiro * sai de qq e chega em q; o segundo sai de q e chega em nota. Se q mudar de endereço, **qq muda junto. _(aponta a crença `double_deref_is_data`)_
- respondeu `Em um passo: qq já guarda o endereço de nota` → qq guarda o endereço de q, e não o de nota. Até nota são dois passos: de qq a q, e de q a nota.
- qualquer outro erro → São dois passos, e o do meio passa por q.

### Degrau 2 — guiado, digitar

> O que **pp escreve é o que *p lê: os dois chegam na mesma caixa.

**Versão 1.** O trecho escreve por **pp e lê por *p. Que número aparece?

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

**pp = 9;
printf("%d\n", *p);
```

Resposta certa: `9`

Se errar:

- digitou `15` → **pp passa por p e chega em idade — a mesma caixa em que *p chega. O 9 escrito por um é o que o outro lê.
- qualquer outro erro → **pp e *p chegam em idade, que recebeu 9.

**Versão 2.** O trecho escreve por *q e lê por **qq. Que número aparece?

```c
int nota = 7;
int *q = &nota;
int **qq = &q;

*q = 20;
printf("%d\n", **qq);
```

Resposta certa: `20`

Se errar:

- digitou `7` → **qq passa por q e chega em nota — a mesma caixa em que *q chega. O 20 escrito por um é o que o outro lê.
- qualquer outro erro → *q e **qq chegam em nota, que recebeu 20.

### Degrau 3 — guiado, completar

> *pp é a caixa p: o que se escreve ali é um endereço.
> **pp é a caixa idade: o que se escreve ali é um número.

**Versão 1.** Complete para trocar o que p guarda, sem escrever o nome p.

Já está escrito:

```c
int idade = 15;
int nota = 7;
int *p = &idade;
int **pp = &p;
```

```c
___ = &nota;
```

Peças: `*pp`  `**pp`  `pp`

Resposta certa: `*pp = &nota;`

Se errar:

- respondeu `**pp = &nota;` → **pp é a caixa idade, que guarda número — e &nota é um endereço: o compilador reclama. A caixa p está a um passo: *pp = &nota;
- respondeu `pp = &nota;` → pp guarda o endereço de um ponteiro, e &nota é o endereço de um int: o compilador reclama. A caixa p está a um passo: *pp = &nota;
- qualquer outro erro → A um passo de pp está a caixa p: *pp = &nota;

**Versão 2.** Complete para escrever 0 em nota, sem escrever nem nota nem q.

Já está escrito:

```c
int nota = 7;
int *q = &nota;
int **qq = &q;
```

```c
___ = 0;
```

Peças: `qq`  `**qq`  `&qq`

Resposta certa: `**qq = 0;`

Se errar:

- respondeu `qq = 0;` → qq = 0; apaga o endereço que qq guardava, e mais nada: nota fica como estava. A caixa nota está a dois passos: **qq = 0;
- respondeu `&qq = 0;` → &qq é o endereço da caixa qq, e não um lugar que recebe valor: o compilador reclama. A caixa nota está a dois passos: **qq = 0;
- qualquer outro erro → A dois passos de qq está a caixa nota: **qq = 0;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: *pp chega em p; **pp, no número_

**Versão 1.** p começa apontando para nota, e depois recebe o endereço de idade. Que número **pp mostra?

```c
int idade = 15;
int nota = 7;
int *p = &nota;
int **pp = &p;

p = &idade;
printf("%d\n", **pp);
```

Resposta certa: `15`

Se errar:

- digitou `7` → **pp passa por p. Quando p trocou de endereço, o segundo passo passou a dar em idade: 15.
- qualquer outro erro → **pp passa por p, que agora aponta para idade: 15.

**Versão 2.** q começa apontando para idade, e depois recebe o endereço de nota. Que número **qq mostra?

```c
int idade = 20;
int nota = 9;
int *q = &idade;
int **qq = &q;

q = &nota;
printf("%d\n", **qq);
```

Resposta certa: `9`

Se errar:

- digitou `20` → **qq passa por q. Quando q trocou de endereço, o segundo passo passou a dar em nota: 9.
- qualquer outro erro → **qq passa por q, que agora aponta para nota: 9.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas mostra 15 na tela?

Já está escrito:

```c
int idade = 15;
int *p = &idade;
int **pp = &p;
```

Opções: `printf("%d\n", **pp);`  `printf("%d\n", *pp);`  `printf("%d\n", pp);`

Resposta certa: `printf("%d\n", **pp);`

Se errar:

- respondeu `printf("%d\n", *pp);` → *pp dá um passo só, e chega em p, que guarda um endereço — e não o 15. O compilador reclama do %d. Até o número são dois passos: **pp.
- respondeu `printf("%d\n", pp);` → pp guarda o endereço de p, e não o 15: o compilador reclama do %d. Até o número são dois passos: **pp.
- qualquer outro erro → O 15 está a dois passos de pp: **pp.

**Versão 2.** Qual destas linhas mostra 7 na tela?

Já está escrito:

```c
int nota = 7;
int *q = &nota;
int **qq = &q;
```

Opções: `printf("%d\n", qq);`  `printf("%d\n", *qq);`  `printf("%d\n", **qq);`

Resposta certa: `printf("%d\n", **qq);`

Se errar:

- respondeu `printf("%d\n", *qq);` → *qq dá um passo só, e chega em q, que guarda um endereço — e não o 7. O compilador reclama do %d. Até o número são dois passos: **qq.
- respondeu `printf("%d\n", qq);` → qq guarda o endereço de q, e não o 7: o compilador reclama do %d. Até o número são dois passos: **qq.
- qualquer outro erro → O 7 está a dois passos de qq: **qq.

### Se errar a pergunta do topo: a revisão

> pp e p são duas caixas: pp guarda o endereço de p, e p guarda o endereço de idade.
> *pp chega em p. **pp passa por p, e só então chega no número.

```c
int idade = 15;
int *p = &idade;
int **pp = &p;

**pp = 9;
printf("%d\n", *p);
```

A máquina imprime:

```
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> **pp acessa o dado final diretamente; um nível a mais resolve sozinho.

```c
int idade = 15;
int nota = 7;
int *p = &idade;
int **pp = &p;

p = &nota;
printf("%d\n", **pp);
```

**pp guarda &p. Depois, p passa a guardar o endereço de nota. O que **pp mostra?**

- 7 _(é o que a máquina faz)_
- 15: **pp vai direto ao dado final, que era idade _(é o que a crença espera)_

A máquina imprime:

```
7
```

O que isto mostra: Saiu 7. **pp não vai direto a lugar nenhum: dá um passo até p, e outro até onde p aponta. Quando p trocou de endereço, o segundo passo passou a dar em nota.
