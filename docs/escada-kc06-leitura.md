# A escada do kc_06 — Passagem por referência

Texto para leitura, gerado de `mvp/dominio/escada_kc06.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — A função ganha uma casa nova, só dela, para o parâmetro.

### Degrau 1 — guiado, tocar

> O que fica entre os parênteses da função é o parâmetro.
> Em void zera(int n) o parâmetro se chama n: é uma variável local, só da função.

**Versão 1.** Toque no nome do parâmetro.

```c
void zera(int n) { n = 0; }
```

Peças: `void zera(`  `int`  `n`  `) { n = 0; }`

Resposta certa: `n`

Se errar:

- respondeu `int` → int é o tipo do parâmetro. O nome dele é a palavra seguinte: n.
- respondeu `void zera(` → zera é o nome da função. O parâmetro é a variável que fica entre os parênteses: n.
- respondeu `) { n = 0; }` → Esse é o corpo da função: o que ela faz. O parâmetro é a variável entre os parênteses: n.
- qualquer outro erro → O parâmetro é a variável entre os parênteses da função: n.

**Versão 2.** Toque no nome do parâmetro.

```c
void marca(int v) { v = 9; }
```

Peças: `void marca(`  `int`  `v`  `) { v = 9; }`

Resposta certa: `v`

Se errar:

- respondeu `int` → int é o tipo do parâmetro. O nome dele é a palavra seguinte: v.
- respondeu `void marca(` → marca é o nome da função. O parâmetro é a variável que fica entre os parênteses: v.
- respondeu `) { v = 9; }` → Esse é o corpo da função: o que ela faz. O parâmetro é a variável entre os parênteses: v.
- qualquer outro erro → O parâmetro é a variável entre os parênteses da função: v.

### Degrau 2 — guiado, escolher

> Na chamada zera(idade); o que vai entre os parênteses é o argumento.
> O parâmetro não é o argumento: é uma variável nova, criada na chamada, com o seu próprio lugar.

**Versão 1.** Durante a chamada da última linha, quantas variáveis existem?

Já está escrito:

```c
void zera(int n) { n = 0; }

int idade;

idade = 15;
zera(idade);
```

Opções: `Duas: idade, de quem chamou, e n, da função`  `Uma: a função usa a própria idade, e n não é variável nova`  `Nenhuma: a função só usa o valor`

Resposta certa: `Duas: idade, de quem chamou, e n, da função`

Se errar:

- respondeu `Uma: a função usa a própria idade, e n não é variável nova` → A função não usa a idade: ela ganha uma variável nova, n, com o lugar dela. São duas variáveis. _(aponta a crença `funcao_usa_a_variavel_do_chamador`)_
- respondeu `Nenhuma: a função só usa o valor` → O valor precisa de onde ficar, dentro da função: é o parâmetro n, uma variável nova. Com idade, são duas.
- qualquer outro erro → São duas variáveis: idade, de quem chamou, e o parâmetro n, que é da função.

**Versão 2.** Durante a chamada da última linha, quantas variáveis existem?

Já está escrito:

```c
void marca(int v) { v = 9; }

int nota;

nota = 7;
marca(nota);
```

Opções: `Duas: nota, de quem chamou, e v, da função`  `Uma: a função usa a própria nota, e v não é variável nova`  `Nenhuma: a função só usa o valor`

Resposta certa: `Duas: nota, de quem chamou, e v, da função`

Se errar:

- respondeu `Uma: a função usa a própria nota, e v não é variável nova` → A função não usa a nota: ela ganha uma variável nova, v, com o lugar dela. São duas variáveis. _(aponta a crença `funcao_usa_a_variavel_do_chamador`)_
- respondeu `Nenhuma: a função só usa o valor` → O valor precisa de onde ficar, dentro da função: é o parâmetro v, uma variável nova. Com nota, são duas.
- qualquer outro erro → São duas variáveis: nota, de quem chamou, e o parâmetro v, que é da função.

### Degrau 3 — guiado, digitar

> Como o parâmetro é outra variável, o que a função escreve nele fica nele.

**Versão 1.** Que número este trecho mostra na tela?

```c
void zera(int n) { n = 0; }

int idade;

idade = 15;
zera(idade);
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → A função escreveu 0 em n, que é a variável dela. idade é outra variável, e continua com 15.
- qualquer outro erro → O 0 foi para o parâmetro n. idade, de quem chamou, continua com 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
void marca(int v) { v = 9; }

int nota;

nota = 7;
marca(nota);
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `9` → A função escreveu 9 em v, que é a variável dela. nota é outra variável, e continua com 7.
- qualquer outro erro → O 9 foi para o parâmetro v. nota, de quem chamou, continua com 7.

### Degrau 4 — guiado, digitar

> A função pode ter mais de um parâmetro, separados por vírgula.
> E pode declarar variáveis dentro das chaves. Todas são locais: só dela.

**Versão 1.** A função soma os dois parâmetros numa variável dela, t, e mostra t. Que número aparece?

```c
void soma(int a, int b) { int t = a + b; printf("%d\n", t); }

int idade;
int nota;

idade = 15;
nota = 7;
soma(idade, nota);
```

Resposta certa: `22`

Se errar:

- digitou `15` → 15 é o que entrou em a. A função soma a com b, 15 mais 7, guarda em t e mostra t: 22.
- digitou `7` → 7 é o que entrou em b. A função soma a com b, 15 mais 7, guarda em t e mostra t: 22.
- qualquer outro erro → a nasce com 15 e b com 7. t, declarada dentro da função, recebe a soma: 22.

**Versão 2.** A função soma os dois parâmetros numa variável dela, t, e mostra t. Que número aparece?

```c
void soma(int a, int b) { int t = a + b; printf("%d\n", t); }

int pontos;
int nota;

pontos = 3;
nota = 7;
soma(pontos, nota);
```

Resposta certa: `10`

Se errar:

- digitou `3` → 3 é o que entrou em a. A função soma a com b, 3 mais 7, guarda em t e mostra t: 10.
- digitou `7` → 7 é o que entrou em b. A função soma a com b, 3 mais 7, guarda em t e mostra t: 10.
- qualquer outro erro → a nasce com 3 e b com 7. t, declarada dentro da função, recebe a soma: 10.

### Degrau 5 — prática, digitar

_Nome do passo, no fechamento: Mesmo nome, e ainda assim duas variáveis_

**Versão 1.** Aqui o parâmetro tem o mesmo nome da variável de quem chamou. Que número este trecho mostra na tela?

```c
void zera(int idade) { idade = 0; }

int idade;

idade = 15;
zera(idade);
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → O nome é igual, mas são duas variáveis. O 0 foi para a idade da função; a de quem chamou continua com 15.
- qualquer outro erro → São duas variáveis com o mesmo nome. A função zerou a dela; a de quem chamou continua com 15.

**Versão 2.** Aqui o parâmetro tem o mesmo nome da variável de quem chamou. Que número este trecho mostra na tela?

```c
void marca(int nota) { nota = 9; }

int nota;

nota = 7;
marca(nota);
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `9` → O nome é igual, mas são duas variáveis. O 9 foi para a nota da função; a de quem chamou continua com 7.
- qualquer outro erro → São duas variáveis com o mesmo nome. A função escreveu na dela; a de quem chamou continua com 7.

### Degrau 6 — prática, digitar

**Versão 1.** Aqui a chamada entrega o número 15 direto, sem variável nenhuma. Que número aparece?

```c
void conta(int n) { n = n + 1; printf("%d\n", n); }

conta(15);
```

Resposta certa: `16`

Se errar:

- digitou `15` → O 15 foi copiado para n, e n é uma variável da função: ela soma 1 em n, e mostra 16.
- qualquer outro erro → n é uma variável da função, mesmo quando o argumento é só um número. Ela nasce com 15, vira 16, e é o 16 que aparece.

**Versão 2.** Aqui a chamada entrega o número 7 direto, sem variável nenhuma. Que número aparece?

```c
void conta(int n) { n = n + 2; printf("%d\n", n); }

conta(7);
```

Resposta certa: `9`

Se errar:

- digitou `7` → O 7 foi copiado para n, e n é uma variável da função: ela soma 2 em n, e mostra 9.
- qualquer outro erro → n é uma variável da função, mesmo quando o argumento é só um número. Ela nasce com 7, vira 9, e é o 9 que aparece.

### Se errar a pergunta do topo: a revisão

> O parâmetro é uma variável da função: nasce quando ela é chamada, e é só dela.
> Em zera(idade); existem duas variáveis: idade, de quem chamou, e n, da função.

```c
void zera(int n) { n = 0; }

int idade;

idade = 15;
zera(idade);
printf("%d\n", idade);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> A função usa a variável de quem chamou: o parâmetro não é caixa nova.

```c
void mostra(int n) { printf("%p\n", (void *)&n); }

int idade;

idade = 15;
printf("%p\n", (void *)&idade);
mostra(idade);
```

**O primeiro printf mostra o endereço de idade. O de dentro da função mostra o endereço do parâmetro n. O que os dois mostram?**

- O mesmo endereço: n é a própria idade _(é o que a crença espera)_
- Dois endereços diferentes _(é o que a máquina faz)_

A máquina imprime:

```
0x1000
0x2A00
```

_Os números dos lugares mudam de máquina para máquina; aqui eles aparecem como números de exemplo. O que foi conferido é que as duas linhas saem com endereços diferentes._

O que isto mostra: Saíram dois endereços diferentes. O parâmetro n tem o lugar dele: é uma variável nova, da função, e não a idade de quem chamou.

## B2 — O que está na casa de x é copiado para dentro da casa nova. É cópia, e o que se copia é o valor.

### Degrau 1 — guiado, digitar

> Chamar a função copia o valor para o parâmetro.
> Em mostra(idade); o parâmetro v nasce com o valor que idade tem naquele momento.

**Versão 1.** A função mostra na tela o parâmetro dela. Que número aparece?

```c
void mostra(int v) { printf("%d\n", v); }

int idade;

idade = 15;
mostra(idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → O parâmetro não nasce zerado: nasce com a cópia do valor que foi na chamada, o 15 de idade.
- qualquer outro erro → v nasce com uma cópia do valor de idade: 15.

**Versão 2.** A função mostra na tela o parâmetro dela. Que número aparece?

```c
void mostra(int v) { printf("%d\n", v); }

int nota;

nota = 7;
mostra(nota);
```

Resposta certa: `7`

Se errar:

- digitou `0` → O parâmetro não nasce zerado: nasce com a cópia do valor que foi na chamada, o 7 de nota.
- qualquer outro erro → v nasce com uma cópia do valor de nota: 7.

### Degrau 2 — guiado, digitar

> A chamada pode trazer uma conta: mostra(idade + 1);
> A conta é feita ANTES, e o que entra no parâmetro é o resultado: um valor.

**Versão 1.** Que número aparece?

```c
void mostra(int v) { printf("%d\n", v); }

int idade;

idade = 15;
mostra(idade + 1);
```

Resposta certa: `16`

Se errar:

- digitou `15` → A conta idade + 1 é feita antes da chamada, e o que entra em v é o resultado: 16.
- qualquer outro erro → A conta é feita antes: idade + 1 dá 16, e é o 16 que entra em v.

**Versão 2.** Que número aparece?

```c
void mostra(int v) { printf("%d\n", v); }

int nota;

nota = 7;
mostra(nota + 2);
```

Resposta certa: `9`

Se errar:

- digitou `7` → A conta nota + 2 é feita antes da chamada, e o que entra em v é o resultado: 9.
- qualquer outro erro → A conta é feita antes: nota + 2 dá 9, e é o 9 que entra em v.

### Degrau 3 — guiado, escolher

> O que chega à função é sempre um valor pronto.
> Ela não recebe a conta, nem a variável: recebe o número que a conta deu.

**Versão 1.** Na última linha, o que entra em v?

Já está escrito:

```c
void mostra(int v) { printf("%d\n", v); }

int idade;

idade = 15;
mostra(idade + 1);
```

Opções: `O número 16, já calculado`  `A conta idade + 1: o que se passa é o que está escrito na chamada`  `A variável idade`

Resposta certa: `O número 16, já calculado`

Se errar:

- respondeu `A conta idade + 1: o que se passa é o que está escrito na chamada` → A função não recebe a conta para resolver lá dentro. A conta é feita na chamada, e entra o resultado: 16. _(aponta a crença `passa_a_expressao`)_
- respondeu `A variável idade` → A variável idade fica com quem chamou. O que entra em v é um valor: o 16 que a conta deu.
- qualquer outro erro → Entra o valor que a conta deu, já calculado: 16.

**Versão 2.** Na última linha, o que entra em v?

Já está escrito:

```c
void mostra(int v) { printf("%d\n", v); }

int nota;

nota = 7;
mostra(nota + 2);
```

Opções: `O número 9, já calculado`  `A conta nota + 2: o que se passa é o que está escrito na chamada`  `A variável nota`

Resposta certa: `O número 9, já calculado`

Se errar:

- respondeu `A conta nota + 2: o que se passa é o que está escrito na chamada` → A função não recebe a conta para resolver lá dentro. A conta é feita na chamada, e entra o resultado: 9. _(aponta a crença `passa_a_expressao`)_
- respondeu `A variável nota` → A variável nota fica com quem chamou. O que entra em v é um valor: o 9 que a conta deu.
- qualquer outro erro → Entra o valor que a conta deu, já calculado: 9.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A conta da chamada é feita antes, uma vez só_

**Versão 1.** A função recebe duas coisas: um valor e um endereço. Ela muda idade para 100 e só depois mostra v. Que número aparece?

```c
void mostra(int v, int *p) { *p = 100; printf("%d\n", v); }

int idade;

idade = 15;
mostra(idade + 1, &idade);
```

Resposta certa: `16`

Se errar:

- digitou `101` → A conta foi feita na chamada, quando idade valia 15, e entrou 16. Mudar idade depois não muda o que já foi copiado.
- digitou `100` → O 100 foi para idade, pelo endereço. O printf mostra v, que tinha recebido o resultado da conta: 16.
- qualquer outro erro → A conta é feita na chamada: entra 16. O que a função faz depois com idade não muda v.

**Versão 2.** A função recebe duas coisas: um valor e um endereço. Ela muda pontos para 50 e só depois mostra v. Que número aparece?

```c
void mostra(int v, int *p) { *p = 50; printf("%d\n", v); }

int pontos;

pontos = 3;
mostra(pontos + 2, &pontos);
```

Resposta certa: `5`

Se errar:

- digitou `52` → A conta foi feita na chamada, quando pontos valia 3, e entrou 5. Mudar pontos depois não muda o que já foi copiado.
- digitou `50` → O 50 foi para pontos, pelo endereço. O printf mostra v, que tinha recebido o resultado da conta: 5.
- qualquer outro erro → A conta é feita na chamada: entra 5. O que a função faz depois com pontos não muda v.

### Degrau 5 — prática, escolher

**Versão 1.** O que a função recebe nesta chamada?

Já está escrito:

```c
mostra(2 + 3);
```

Opções: `O número 5`  `A conta 2 + 3, para resolver lá dentro`  `Os números 2 e 3, um de cada vez`

Resposta certa: `O número 5`

Se errar:

- respondeu `A conta 2 + 3, para resolver lá dentro` → A conta é feita antes da chamada. O que a função recebe é o resultado, um valor só: 5.
- respondeu `Os números 2 e 3, um de cada vez` → A função tem um parâmetro, e recebe um valor só: o resultado da conta, 5.
- qualquer outro erro → A conta é feita antes, e entra o resultado: 5.

**Versão 2.** O que a função recebe nesta chamada?

Já está escrito:

```c
mostra(10 + 4);
```

Opções: `O número 14`  `A conta 10 + 4, para resolver lá dentro`  `Os números 10 e 4, um de cada vez`

Resposta certa: `O número 14`

Se errar:

- respondeu `A conta 10 + 4, para resolver lá dentro` → A conta é feita antes da chamada. O que a função recebe é o resultado, um valor só: 14.
- respondeu `Os números 10 e 4, um de cada vez` → A função tem um parâmetro, e recebe um valor só: o resultado da conta, 14.
- qualquer outro erro → A conta é feita antes, e entra o resultado: 14.

### Se errar a pergunta do topo: a revisão

> Na chamada, o valor é calculado e copiado para o parâmetro.
> Se a chamada tem uma conta, como mostra(idade + 1);, a conta é feita antes, e entra o resultado.

```c
void mostra(int v) { printf("%d\n", v); }

int idade;

idade = 15;
mostra(idade + 1);
```

A máquina imprime:

```
16
```

### Se a pessoa disser a crença: a prova

Você disse:

> O que se passa é a expressão escrita na chamada, não o valor dela.

```c
void mostra(int v, int *p) { *p = 100; printf("%d\n", v); }

int nota;

nota = 7;
mostra(nota + 1, &nota);
```

**A chamada entrega nota + 1 e o endereço de nota. Lá dentro, a função muda nota para 100 e só depois mostra v. O que aparece?**

- 8 _(é o que a máquina faz)_
- 101 _(é o que a crença espera)_

A máquina imprime:

```
8
```

O que isto mostra: Saiu 8. A conta nota + 1 foi feita na chamada, quando nota valia 7, e o que entrou em v foi o resultado. Mudar nota depois não muda o que já tinha sido copiado: o que se passa é o valor, e não a conta.

## I1 — Então mexer na casa nova não mexe na casa de x: são duas casas, em lugares diferentes.

### Degrau 1 — guiado, escolher

> São duas variáveis, em dois lugares: a de quem chamou e o parâmetro.
> O parâmetro começa com uma cópia do valor. Daí em diante, cada uma segue a sua vida.

**Versão 1.** Dentro da função, o que a linha n = 0; muda?

Já está escrito:

```c
void zera(int n) { n = 0; }

int idade;

idade = 15;
zera(idade);
```

Opções: `Só n, o parâmetro da função`  `idade: a função recebe a variável original, e não uma cópia`  `As duas: n e idade passam a valer 0`

Resposta certa: `Só n, o parâmetro da função`

Se errar:

- respondeu `idade: a função recebe a variável original, e não uma cópia` → A função recebe uma cópia do valor, guardada em n. A linha escreve em n; idade está em outro lugar, e fica com 15. _(aponta a crença `function_gets_original`)_
- respondeu `As duas: n e idade passam a valer 0` → São duas variáveis, e a linha escreve numa só: n. idade está em outro lugar, e fica com 15.
- qualquer outro erro → A linha muda só n, o parâmetro. idade fica como estava.

**Versão 2.** Dentro da função, o que a linha v = 9; muda?

Já está escrito:

```c
void marca(int v) { v = 9; }

int nota;

nota = 7;
marca(nota);
```

Opções: `Só v, o parâmetro da função`  `nota: a função recebe a variável original, e não uma cópia`  `As duas: v e nota passam a valer 9`

Resposta certa: `Só v, o parâmetro da função`

Se errar:

- respondeu `nota: a função recebe a variável original, e não uma cópia` → A função recebe uma cópia do valor, guardada em v. A linha escreve em v; nota está em outro lugar, e fica com 7. _(aponta a crença `function_gets_original`)_
- respondeu `As duas: v e nota passam a valer 9` → São duas variáveis, e a linha escreve numa só: v. nota está em outro lugar, e fica com 7.
- qualquer outro erro → A linha muda só v, o parâmetro. nota fica como estava.

### Degrau 2 — guiado, digitar

> Por isso, depois da chamada, a variável de quem chamou continua como estava.

**Versão 1.** Que número este trecho mostra na tela?

```c
void soma(int n) { n = n + 10; }

int idade;

idade = 15;
soma(idade);
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `25` → O 10 foi somado em n, a cópia. idade está em outro lugar, e continua com 15.
- qualquer outro erro → A função somou na cópia. idade continua com 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
void soma(int n) { n = n + 10; }

int pontos;

pontos = 3;
soma(pontos);
printf("%d\n", pontos);
```

Resposta certa: `3`

Se errar:

- digitou `13` → O 10 foi somado em n, a cópia. pontos está em outro lugar, e continua com 3.
- qualquer outro erro → A função somou na cópia. pontos continua com 3.

### Degrau 3 — guiado, escolher

> Recebendo só o valor, a função não tem como chegar na variável de quem chamou.
> Para chegar lá, ela precisa do endereço — e é a próxima ideia.

**Versão 1.** Qual destas funções consegue zerar a variável de quem chama?

Opções: `void zera(int *n) { *n = 0; }`  `void zera(int n) { n = 0; }`  `void zera(int n) { n = n; }`

Resposta certa: `void zera(int *n) { *n = 0; }`

Se errar:

- respondeu `void zera(int n) { n = 0; }` → Essa recebe uma cópia do valor, e zera a cópia. Para chegar na variável de quem chama, a função recebe o endereço: int *n.
- respondeu `void zera(int n) { n = n; }` → Essa só copia n para ele mesmo, e nem a cópia muda. Para chegar na variável de quem chama, a função recebe o endereço: int *n.
- qualquer outro erro → Só a que recebe o endereço chega na variável de quem chama: void zera(int *n) { *n = 0; }

**Versão 2.** Qual destas funções consegue escrever 9 na variável de quem chama?

Opções: `void marca(int v) { v = 9; }`  `void marca(int *v) { *v = 9; }`  `void marca(int v) { v = v; }`

Resposta certa: `void marca(int *v) { *v = 9; }`

Se errar:

- respondeu `void marca(int v) { v = 9; }` → Essa recebe uma cópia do valor, e escreve na cópia. Para chegar na variável de quem chama, a função recebe o endereço: int *v.
- respondeu `void marca(int v) { v = v; }` → Essa só copia v para ele mesmo, e nem a cópia muda. Para chegar na variável de quem chama, a função recebe o endereço: int *v.
- qualquer outro erro → Só a que recebe o endereço chega na variável de quem chama: void marca(int *v) { *v = 9; }

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Mexer na cópia não mexe na variável de fora_

**Versão 1.** Que número este trecho mostra na tela?

```c
void dobra(int n) { n = n + n; }

int idade;

idade = 4;
dobra(idade);
dobra(idade);
printf("%d\n", idade);
```

Resposta certa: `4`

Se errar:

- digitou `16` → Cada chamada dobrou a cópia dela, e a cópia acabou junto com a chamada. idade nunca foi tocada: 4.
- digitou `8` → A função dobrou n, a cópia, e não idade. Nas duas chamadas idade ficou como estava: 4.
- qualquer outro erro → As duas chamadas mexeram em cópias. idade continua com 4.

**Versão 2.** Que número este trecho mostra na tela?

```c
void dobra(int n) { n = n + n; }

int pontos;

pontos = 3;
dobra(pontos);
dobra(pontos);
printf("%d\n", pontos);
```

Resposta certa: `3`

Se errar:

- digitou `12` → Cada chamada dobrou a cópia dela, e a cópia acabou junto com a chamada. pontos nunca foi tocada: 3.
- digitou `6` → A função dobrou n, a cópia, e não pontos. Nas duas chamadas pontos ficou como estava: 3.
- qualquer outro erro → As duas chamadas mexeram em cópias. pontos continua com 3.

### Degrau 5 — prática, escolher

**Versão 1.** Por que nota continua valendo 7 depois da chamada?

Já está escrito:

```c
void zera(int n) { n = 0; }

int nota;

nota = 7;
zera(nota);
```

Opções: `Porque a função zerou n, que é outra variável`  `Porque a função não chegou a rodar`  `Porque um 7 não pode ser zerado`

Resposta certa: `Porque a função zerou n, que é outra variável`

Se errar:

- respondeu `Porque a função não chegou a rodar` → A função rodou, e escreveu 0. Só que escreveu em n, a cópia dela; nota está em outro lugar.
- respondeu `Porque um 7 não pode ser zerado` → Qualquer variável inteira pode receber 0. A função escreveu 0, mas em n, a cópia dela; nota está em outro lugar.
- qualquer outro erro → A função zerou o parâmetro dela. nota é outra variável, em outro lugar.

**Versão 2.** Por que idade continua valendo 15 depois da chamada?

Já está escrito:

```c
void marca(int v) { v = 9; }

int idade;

idade = 15;
marca(idade);
```

Opções: `Porque a função escreveu em v, que é outra variável`  `Porque a função não chegou a rodar`  `Porque um 15 não pode virar 9`

Resposta certa: `Porque a função escreveu em v, que é outra variável`

Se errar:

- respondeu `Porque a função não chegou a rodar` → A função rodou, e escreveu 9. Só que escreveu em v, a cópia dela; idade está em outro lugar.
- respondeu `Porque um 15 não pode virar 9` → Qualquer variável inteira pode receber 9. A função escreveu 9, mas em v, a cópia dela; idade está em outro lugar.
- qualquer outro erro → A função escreveu no parâmetro dela. idade é outra variável, em outro lugar.

### Se errar a pergunta do topo: a revisão

> A função mexe no parâmetro dela, que é uma cópia.
> A variável de quem chamou está em outro lugar, e fica como estava.

```c
void zera(int n) { n = 0; }

int nota;

nota = 7;
zera(nota);
printf("%d\n", nota);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> A função recebe a variável original, não uma cópia.

```c
void zera(int n) { n = 0; }

int pontos;

pontos = 3;
zera(pontos);
printf("%d\n", pontos);
```

**A função escreve 0 no que recebeu. O que o trecho imprime?**

- 0 _(é o que a crença espera)_
- 3 _(é o que a máquina faz)_

A máquina imprime:

```
3
```

O que isto mostra: Saiu 3. A função recebeu uma cópia do valor e zerou a cópia. Se ela recebesse a variável original, pontos teria virado 0.

## I2 — Se o que foi copiado é um número de casa, a cópia do número leva à mesma casa — e lá você mexe de verdade.

### Degrau 1 — guiado, escolher

> Numa chamada, o parâmetro recebe uma cópia do que vai entre os parênteses.
> A cópia de um endereço aponta para o mesmo lugar que o original.

**Versão 1.** Na última linha, o que o parâmetro p recebe?

Já está escrito:

```c
void poe(int *p) { *p = 42; }

int idade;

idade = 15;
poe(&idade);
```

Opções: `Uma cópia do endereço de idade`  `Uma cópia do valor de idade: &idade entrega o 15`  `A própria variável idade`

Resposta certa: `Uma cópia do endereço de idade`

Se errar:

- respondeu `Uma cópia do valor de idade: &idade entrega o 15` → &idade não é o valor: é o endereço. É ele que é copiado para p, e a cópia de um endereço leva ao mesmo lugar. _(aponta a crença `ampersand_copies`)_
- respondeu `A própria variável idade` → A variável idade fica onde está. O que vai para p é o endereço dela — uma cópia do endereço.
- qualquer outro erro → p recebe uma cópia do endereço de idade.

**Versão 2.** Na última linha, o que o parâmetro p recebe?

Já está escrito:

```c
void poe(int *p) { *p = 42; }

int nota;

nota = 7;
poe(&nota);
```

Opções: `Uma cópia do endereço de nota`  `Uma cópia do valor de nota: &nota entrega o 7`  `A própria variável nota`

Resposta certa: `Uma cópia do endereço de nota`

Se errar:

- respondeu `Uma cópia do valor de nota: &nota entrega o 7` → &nota não é o valor: é o endereço. É ele que é copiado para p, e a cópia de um endereço leva ao mesmo lugar. _(aponta a crença `ampersand_copies`)_
- respondeu `A própria variável nota` → A variável nota fica onde está. O que vai para p é o endereço dela — uma cópia do endereço.
- qualquer outro erro → p recebe uma cópia do endereço de nota.

### Degrau 2 — guiado, digitar

> Com o endereço, *p = 42; vai até a variável de quem chamou e escreve nela.

**Versão 1.** Que número este trecho mostra na tela?

```c
void poe(int *p) { *p = 42; }

int idade;

idade = 15;
poe(&idade);
printf("%d\n", idade);
```

Resposta certa: `42`

Se errar:

- digitou `15` → Desta vez o que foi copiado é o endereço. *p = 42; foi até idade e escreveu nela.
- qualquer outro erro → A função recebeu o endereço de idade e escreveu lá: 42.

**Versão 2.** Que número este trecho mostra na tela?

```c
void poe(int *p) { *p = 42; }

int pontos;

pontos = 3;
poe(&pontos);
printf("%d\n", pontos);
```

Resposta certa: `42`

Se errar:

- digitou `3` → Desta vez o que foi copiado é o endereço. *p = 42; foi até pontos e escreveu nela.
- qualquer outro erro → A função recebeu o endereço de pontos e escreveu lá: 42.

### Degrau 3 — guiado, completar

> Na chamada vai o endereço, com o &. Sem ele, iria uma cópia do valor.

**Versão 1.** Complete a chamada para a função escrever em nota.

Já está escrito:

```c
void poe(int *p) { *p = 42; }

int nota;

nota = 7;
```

```c
poe(___);
```

Peças: `&nota`  `nota`  `*nota`

Resposta certa: `poe(&nota);`

Se errar:

- respondeu `poe(nota);` → nota, sem o &, entrega uma cópia do valor, e a função espera um endereço. O compilador reclama. O certo é poe(&nota);
- respondeu `poe(*nota);` → O * serve a ponteiro, e nota não é um. O endereço dela se pede com o &: poe(&nota);
- qualquer outro erro → A função espera um endereço, e o de nota é &nota: poe(&nota);

**Versão 2.** Complete a chamada para a função escrever em idade.

Já está escrito:

```c
void poe(int *p) { *p = 42; }

int idade;

idade = 15;
```

```c
poe(___);
```

Peças: `&idade`  `idade`  `*idade`

Resposta certa: `poe(&idade);`

Se errar:

- respondeu `poe(idade);` → idade, sem o &, entrega uma cópia do valor, e a função espera um endereço. O compilador reclama. O certo é poe(&idade);
- respondeu `poe(*idade);` → O * serve a ponteiro, e idade não é um. O endereço dela se pede com o &: poe(&idade);
- qualquer outro erro → A função espera um endereço, e o de idade é &idade: poe(&idade);

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A cópia do endereço leva à variável de fora_

**Versão 1.** Que número este trecho mostra na tela?

```c
void soma(int *d) { *d = *d + 10; }

int pontos;

pontos = 3;
soma(&pontos);
soma(&pontos);
printf("%d\n", pontos);
```

Resposta certa: `23`

Se errar:

- digitou `3` → A função recebeu o endereço de pontos nas duas chamadas, e somou 10 na própria pontos em cada uma: 23.
- digitou `13` → Foram duas chamadas, e as duas chegaram em pontos pelo endereço: 3, depois 13, depois 23.
- qualquer outro erro → As duas chamadas somaram 10 na própria pontos, pelo endereço: 23.

**Versão 2.** Que número este trecho mostra na tela?

```c
void soma(int *d) { *d = *d + 5; }

int idade;

idade = 15;
soma(&idade);
soma(&idade);
printf("%d\n", idade);
```

Resposta certa: `25`

Se errar:

- digitou `15` → A função recebeu o endereço de idade nas duas chamadas, e somou 5 na própria idade em cada uma: 25.
- digitou `20` → Foram duas chamadas, e as duas chegaram em idade pelo endereço: 15, depois 20, depois 25.
- qualquer outro erro → As duas chamadas somaram 5 na própria idade, pelo endereço: 25.

### Degrau 5 — prática, escolher

**Versão 1.** Qual chamada faz a função escrever em idade?

Já está escrito:

```c
void poe(int *p) { *p = 42; }

int idade;

idade = 15;
```

Opções: `poe(&idade);`  `poe(idade);`  `poe(*idade);`

Resposta certa: `poe(&idade);`

Se errar:

- respondeu `poe(idade);` → Sem o &, a chamada entregaria uma cópia do valor, e a função espera um endereço. O compilador reclama. O certo é poe(&idade);
- respondeu `poe(*idade);` → O * serve a ponteiro, e idade não é um. O endereço se pede com o &: poe(&idade);
- qualquer outro erro → A função recebe o endereço: poe(&idade);

**Versão 2.** Qual chamada faz a função escrever em pontos?

Já está escrito:

```c
void poe(int *p) { *p = 42; }

int pontos;

pontos = 3;
```

Opções: `poe(pontos);`  `poe(&pontos);`  `poe(*pontos);`

Resposta certa: `poe(&pontos);`

Se errar:

- respondeu `poe(pontos);` → Sem o &, a chamada entregaria uma cópia do valor, e a função espera um endereço. O compilador reclama. O certo é poe(&pontos);
- respondeu `poe(*pontos);` → O * serve a ponteiro, e pontos não é um. O endereço se pede com o &: poe(&pontos);
- qualquer outro erro → A função recebe o endereço: poe(&pontos);

### Se errar a pergunta do topo: a revisão

> Passar &idade copia o endereço para o parâmetro.
> A cópia de um endereço leva ao mesmo lugar: *p = 42; escreve na idade de quem chamou.

```c
void poe(int *p) { *p = 42; }

int idade;

idade = 15;
poe(&idade);
printf("%d\n", idade);
```

A máquina imprime:

```
42
```

### Se a pessoa disser a crença: a prova

Você disse:

> &x entrega uma cópia de x, e é a cópia que a função recebe.

```c
void poe(int *p) { *p = 42; }

int nota;

nota = 7;
poe(&nota);
printf("%d\n", nota);
```

**A chamada entrega &nota, e a função escreve 42 pelo que recebeu. O que o trecho imprime?**

- 42 _(é o que a máquina faz)_
- 7 _(é o que a crença espera)_

A máquina imprime:

```
42
```

O que isto mostra: Saiu 42. Se &nota entregasse uma cópia do valor, a função teria escrito na cópia, e nota continuaria com 7. O que foi copiado é o endereço — e a cópia do endereço leva à própria nota.

## I3 — Mas trocar o número copiado só troca o bilhete da casa nova. O ponteiro de quem chamou fica como estava.

### Degrau 1 — guiado, escolher

> Quando a chamada entrega um ponteiro, solta(q);, o parâmetro recebe uma cópia do endereço guardado em q.
> São dois ponteiros: q, de quem chamou, e p, da função.

**Versão 1.** Dentro da função, o que a linha p = NULL; muda?

Já está escrito:

```c
void solta(int *p) { p = NULL; }

int idade;
int *q;

q = &idade;
solta(q);
```

Opções: `Só p, o ponteiro da função`  `q também: trocar o parâmetro troca o ponteiro de quem chamou`  `idade, que deixa de existir`

Resposta certa: `Só p, o ponteiro da função`

Se errar:

- respondeu `q também: trocar o parâmetro troca o ponteiro de quem chamou` → p é uma cópia do endereço que estava em q. A linha escreve em p; q é outro ponteiro, e continua apontando para idade. _(aponta a crença `modify_pp_changes_p`)_
- respondeu `idade, que deixa de existir` → Ninguém mexeu em idade: a linha escreve em p, o ponteiro da função, e mais nada.
- qualquer outro erro → A linha muda só p. q, de quem chamou, continua apontando para idade.

**Versão 2.** Dentro da função, o que a linha p = NULL; muda?

Já está escrito:

```c
void solta(int *p) { p = NULL; }

int nota;
int *r;

r = &nota;
solta(r);
```

Opções: `Só p, o ponteiro da função`  `r também: trocar o parâmetro troca o ponteiro de quem chamou`  `nota, que deixa de existir`

Resposta certa: `Só p, o ponteiro da função`

Se errar:

- respondeu `r também: trocar o parâmetro troca o ponteiro de quem chamou` → p é uma cópia do endereço que estava em r. A linha escreve em p; r é outro ponteiro, e continua apontando para nota. _(aponta a crença `modify_pp_changes_p`)_
- respondeu `nota, que deixa de existir` → Ninguém mexeu em nota: a linha escreve em p, o ponteiro da função, e mais nada.
- qualquer outro erro → A linha muda só p. r, de quem chamou, continua apontando para nota.

### Degrau 2 — guiado, digitar

> Por isso q continua apontando para idade depois da chamada.
> Para trocar o ponteiro de quem chamou, a função precisaria do endereço dele.

**Versão 1.** Que número este trecho mostra na tela?

```c
void solta(int *p) { p = NULL; }

int idade;
int *q;

idade = 15;
q = &idade;
solta(q);
printf("%d\n", *q);
```

Resposta certa: `15`

Se errar:

- digitou `0` → A função escreveu NULL em p, a cópia dela. q continua com o endereço de idade, e *q acha 15.
- qualquer outro erro → q não mudou: continua apontando para idade, e *q é 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
void solta(int *p) { p = NULL; }

int nota;
int *r;

nota = 7;
r = &nota;
solta(r);
printf("%d\n", *r);
```

Resposta certa: `7`

Se errar:

- digitou `0` → A função escreveu NULL em p, a cópia dela. r continua com o endereço de nota, e *r acha 7.
- qualquer outro erro → r não mudou: continua apontando para nota, e *r é 7.

### Degrau 3 — guiado, digitar

> A diferença está no *: *p = 0; vai ao lugar apontado, que é de quem chamou.
> Sem o *, p = NULL; mexe só na cópia do ponteiro.

**Versão 1.** Que número este trecho mostra na tela?

```c
void zera(int *p) { *p = 0; p = NULL; }

int idade;
int *q;

idade = 15;
q = &idade;
zera(q);
printf("%d\n", idade);
```

Resposta certa: `0`

Se errar:

- digitou `15` → *p = 0; rodou primeiro, e escreveu em idade pelo endereço. Depois p = NULL; mexeu só na cópia do ponteiro.
- qualquer outro erro → *p = 0; chegou em idade pelo endereço. p = NULL; só mexeu na cópia. idade vale 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
void marca(int *p) { *p = 9; p = NULL; }

int nota;
int *r;

nota = 7;
r = &nota;
marca(r);
printf("%d\n", nota);
```

Resposta certa: `9`

Se errar:

- digitou `7` → *p = 9; rodou primeiro, e escreveu em nota pelo endereço. Depois p = NULL; mexeu só na cópia do ponteiro.
- qualquer outro erro → *p = 9; chegou em nota pelo endereço. p = NULL; só mexeu na cópia. nota vale 9.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O ponteiro de quem chamou não muda_

**Versão 1.** A última linha pergunta se q vale NULL. Que número aparece?

```c
void solta(int *p) { p = NULL; }

int idade;
int *q;

q = &idade;
solta(q);
printf("%d\n", q == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → p = NULL; mexeu na cópia. q continua guardando o endereço de idade: a pergunta é falsa, e a resposta é 0.
- qualquer outro erro → q não vale NULL: a função só mexeu na cópia dela. A resposta é 0.

**Versão 2.** A última linha pergunta se r vale NULL. Que número aparece?

```c
void solta(int *p) { p = NULL; }

int pontos;
int *r;

r = &pontos;
solta(r);
printf("%d\n", r == NULL);
```

Resposta certa: `0`

Se errar:

- digitou `1` → p = NULL; mexeu na cópia. r continua guardando o endereço de pontos: a pergunta é falsa, e a resposta é 0.
- qualquer outro erro → r não vale NULL: a função só mexeu na cópia dela. A resposta é 0.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas funções muda a variável apontada por quem chama?

Opções: `void f(int *p) { *p = 0; }`  `void f(int *p) { p = NULL; }`  `void f(int *p) { p = p; }`

Resposta certa: `void f(int *p) { *p = 0; }`

Se errar:

- respondeu `void f(int *p) { p = NULL; }` → p = NULL; troca só a cópia do ponteiro. Para escrever na variável apontada, a linha leva o *: *p = 0;
- respondeu `void f(int *p) { p = p; }` → p = p; não muda nada. Para escrever na variável apontada, a linha leva o *: *p = 0;
- qualquer outro erro → Com o *, a função escreve na variável apontada: void f(int *p) { *p = 0; }

**Versão 2.** Qual destas funções muda a variável apontada por quem chama?

Opções: `void g(int *p) { p = NULL; }`  `void g(int *p) { *p = 9; }`  `void g(int *p) { p = p; }`

Resposta certa: `void g(int *p) { *p = 9; }`

Se errar:

- respondeu `void g(int *p) { p = NULL; }` → p = NULL; troca só a cópia do ponteiro. Para escrever na variável apontada, a linha leva o *: *p = 9;
- respondeu `void g(int *p) { p = p; }` → p = p; não muda nada. Para escrever na variável apontada, a linha leva o *: *p = 9;
- qualquer outro erro → Com o *, a função escreve na variável apontada: void g(int *p) { *p = 9; }

### Se errar a pergunta do topo: a revisão

> O parâmetro ponteiro também é uma cópia: a cópia de um endereço.
> p = NULL; dentro da função troca só essa cópia. O ponteiro de quem chamou continua apontando para onde apontava.

```c
void solta(int *p) { p = NULL; }

int idade;
int *q;

idade = 15;
q = &idade;
solta(q);
printf("%d\n", *q);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> Trocar o parâmetro ponteiro dentro da função altera o ponteiro de quem chamou.

```c
void solta(int *p) { p = NULL; }

int nota;
int *q;

q = &nota;
solta(q);
printf("%d\n", q == NULL);
```

**A função recebe q e escreve NULL no parâmetro dela. Depois da chamada, o trecho pergunta se q vale NULL. O que aparece?**

- 1: q passou a valer NULL _(é o que a crença espera)_
- 0: q continua com o endereço de nota _(é o que a máquina faz)_

A máquina imprime:

```
0
```

O que isto mostra: Saiu 0. A função escreveu NULL em p, que é a cópia dela. O ponteiro de quem chamou é outra variável, e continua guardando o endereço de nota.

## I4 — C copia o que você passa. Passar um endereço é copiar o endereço — e é a cópia que dá acesso ao original.

### Degrau 1 — guiado, escolher

> Em C a chamada sempre copia o argumento: é a passagem por valor.
> Passar o endereço, que muita gente chama de passagem por referência, também é cópia: a do endereço.

**Versão 1.** As duas chamadas copiam alguma coisa. O que cada uma copia?

Já está escrito:

```c
void muda(int v) { v = 9; }
void alcanca(int *p) { *p = 9; }

int idade;

idade = 15;
muda(idade);
alcanca(&idade);
```

Opções: `muda copia o valor de idade; alcanca copia o endereço`  `Só muda copia; alcanca recebe a própria idade`  `Nenhuma copia: as duas recebem a idade`

Resposta certa: `muda copia o valor de idade; alcanca copia o endereço`

Se errar:

- respondeu `Só muda copia; alcanca recebe a própria idade` → alcanca também recebe uma cópia: a do endereço de idade. É por essa cópia que ela chega na variável.
- respondeu `Nenhuma copia: as duas recebem a idade` → Em C toda chamada copia. muda recebe uma cópia do valor; alcanca, uma cópia do endereço.
- qualquer outro erro → As duas copiam: uma o valor, a outra o endereço.

**Versão 2.** As duas chamadas copiam alguma coisa. O que cada uma copia?

Já está escrito:

```c
void muda(int v) { v = 9; }
void alcanca(int *p) { *p = 9; }

int nota;

nota = 7;
alcanca(&nota);
muda(nota);
```

Opções: `alcanca copia o endereço de nota; muda copia o valor`  `Só muda copia; alcanca recebe a própria nota`  `Nenhuma copia: as duas recebem a nota`

Resposta certa: `alcanca copia o endereço de nota; muda copia o valor`

Se errar:

- respondeu `Só muda copia; alcanca recebe a própria nota` → alcanca também recebe uma cópia: a do endereço de nota. É por essa cópia que ela chega na variável.
- respondeu `Nenhuma copia: as duas recebem a nota` → Em C toda chamada copia. muda recebe uma cópia do valor; alcanca, uma cópia do endereço.
- qualquer outro erro → As duas copiam: uma o endereço, a outra o valor.

### Degrau 2 — guiado, escolher

> O parâmetro ponteiro e o ponteiro de quem chamou são duas variáveis.
> Guardam o mesmo endereço, e por isso levam ao mesmo lugar — mas cada um fica no seu.

**Versão 1.** Durante a chamada, p e q são a mesma variável?

Já está escrito:

```c
void alcanca(int *p) { *p = 9; }

int idade;
int *q;

q = &idade;
alcanca(q);
```

Opções: `Não: são dois ponteiros, guardando o mesmo endereço`  `São: a cópia do ponteiro e o original são a mesma variável`  `Não: p guarda uma cópia do valor de idade`

Resposta certa: `Não: são dois ponteiros, guardando o mesmo endereço`

Se errar:

- respondeu `São: a cópia do ponteiro e o original são a mesma variável` → p é uma variável nova, da função, com o lugar dela. Ela recebeu uma cópia do endereço que está em q: são dois ponteiros. _(aponta a crença `pointer_copy_is_alias`)_
- respondeu `Não: p guarda uma cópia do valor de idade` → O que foi copiado para p é o endereço que estava em q, e não o valor de idade. São dois ponteiros, com o mesmo endereço.
- qualquer outro erro → São dois ponteiros, p e q, guardando o mesmo endereço: o de idade.

**Versão 2.** Durante a chamada, p e r são a mesma variável?

Já está escrito:

```c
void alcanca(int *p) { *p = 9; }

int nota;
int *r;

r = &nota;
alcanca(r);
```

Opções: `Não: são dois ponteiros, guardando o mesmo endereço`  `São: a cópia do ponteiro e o original são a mesma variável`  `Não: p guarda uma cópia do valor de nota`

Resposta certa: `Não: são dois ponteiros, guardando o mesmo endereço`

Se errar:

- respondeu `São: a cópia do ponteiro e o original são a mesma variável` → p é uma variável nova, da função, com o lugar dela. Ela recebeu uma cópia do endereço que está em r: são dois ponteiros. _(aponta a crença `pointer_copy_is_alias`)_
- respondeu `Não: p guarda uma cópia do valor de nota` → O que foi copiado para p é o endereço que estava em r, e não o valor de nota. São dois ponteiros, com o mesmo endereço.
- qualquer outro erro → São dois ponteiros, p e r, guardando o mesmo endereço: o de nota.

### Degrau 3 — guiado, digitar

> Por guardarem o mesmo endereço, *p chega em idade.
> Por serem dois, mexer em p não mexe em q.

**Versão 1.** Que número este trecho mostra na tela?

```c
void f(int *p) { *p = 9; p = NULL; }

int idade;
int *q;

idade = 15;
q = &idade;
f(q);
printf("%d\n", *q);
```

Resposta certa: `9`

Se errar:

- digitou `15` → *p = 9; chegou em idade pelo endereço, que p e q guardam igual. idade passou a valer 9.
- digitou `0` → p = NULL; mexeu só em p. q continua apontando para idade, que agora vale 9.
- qualquer outro erro → *p = 9; mudou idade. p = NULL; só mexeu na cópia. *q acha 9.

**Versão 2.** Que número este trecho mostra na tela?

```c
void f(int *p) { *p = 4; p = NULL; }

int nota;
int *r;

nota = 7;
r = &nota;
f(r);
printf("%d\n", *r);
```

Resposta certa: `4`

Se errar:

- digitou `7` → *p = 4; chegou em nota pelo endereço, que p e r guardam igual. nota passou a valer 4.
- digitou `0` → p = NULL; mexeu só em p. r continua apontando para nota, que agora vale 4.
- qualquer outro erro → *p = 4; mudou nota. p = NULL; só mexeu na cópia. *r acha 4.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Toda chamada copia: o valor, ou o endereço_

**Versão 1.** Que número este trecho mostra na tela?

```c
void muda(int v) { v = 9; }
void alcanca(int *p) { *p = 9; }

int idade;
int nota;

idade = 15;
nota = 7;
muda(idade);
alcanca(&nota);
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `9` → muda recebeu uma cópia do VALOR de idade, e escreveu na cópia. Quem recebeu um endereço foi alcanca, e era o de nota.
- digitou `7` → O 7 era de nota, que virou 9. O printf mostra idade, que só teve o valor copiado: 15.
- qualquer outro erro → idade só teve o valor copiado, e continua com 15. Quem mudou foi nota, pelo endereço.

**Versão 2.** Que número este trecho mostra na tela?

```c
void muda(int v) { v = 9; }
void alcanca(int *p) { *p = 9; }

int pontos;
int ano;

pontos = 3;
ano = 2026;
alcanca(&pontos);
muda(ano);
printf("%d\n", ano);
```

Resposta certa: `2026`

Se errar:

- digitou `9` → muda recebeu uma cópia do VALOR de ano, e escreveu na cópia. Quem recebeu um endereço foi alcanca, e era o de pontos.
- digitou `3` → O 3 era de pontos, que virou 9. O printf mostra ano, que só teve o valor copiado: 2026.
- qualquer outro erro → ano só teve o valor copiado, e continua com 2026. Quem mudou foi pontos, pelo endereço.

### Degrau 5 — prática, escolher

**Versão 1.** Como o C entrega um endereço a uma função?

Opções: `Copiando o endereço para o parâmetro`  `Ligando o ponteiro da função ao de quem chamou`  `Entregando a própria variável`

Resposta certa: `Copiando o endereço para o parâmetro`

Se errar:

- respondeu `Ligando o ponteiro da função ao de quem chamou` → Não há ligação entre os dois ponteiros: o da função recebe uma cópia do endereço, e segue por conta própria.
- respondeu `Entregando a própria variável` → A variável fica com quem chamou. O que vai para a função é uma cópia do endereço dela.
- qualquer outro erro → O C copia o endereço para o parâmetro, como copia qualquer valor.

**Versão 2.** Por que uma função que recebe um endereço consegue mudar a variável de quem chamou?

Opções: `Porque a cópia do endereço leva ao mesmo lugar`  `Porque, com endereço, o C não copia nada`  `Porque o parâmetro e a variável passam a ser a mesma`

Resposta certa: `Porque a cópia do endereço leva ao mesmo lugar`

Se errar:

- respondeu `Porque, com endereço, o C não copia nada` → O C copia sempre. Aqui o que ele copia é o endereço — e a cópia de um endereço leva ao mesmo lugar.
- respondeu `Porque o parâmetro e a variável passam a ser a mesma` → O parâmetro é outra variável. Ele guarda uma cópia do endereço, e é por ela que a função chega lá.
- qualquer outro erro → O endereço é copiado, e a cópia leva ao mesmo lugar.

### Se errar a pergunta do topo: a revisão

> Em C toda chamada copia: muda(idade); copia o valor, e alcanca(&idade); copia o endereço.
> É a mesma regra nas duas: passagem por valor. A cópia do endereço é o que dá acesso à variável de quem chamou.

```c
void muda(int v) { v = 9; }
void alcanca(int *p) { *p = 9; }

int idade;

idade = 15;
muda(idade);
printf("%d\n", idade);
alcanca(&idade);
printf("%d\n", idade);
```

A máquina imprime:

```
15
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> A cópia do ponteiro e o original são a mesma variável.

```c
void mostra(int *p) { printf("%p\n", (void *)&p); }

int idade;
int *q;

q = &idade;
printf("%p\n", (void *)&q);
mostra(q);
```

**O primeiro printf mostra o endereço do ponteiro q. O de dentro da função mostra o endereço do parâmetro p, que recebeu q. O que os dois mostram?**

- Dois endereços diferentes _(é o que a máquina faz)_
- O mesmo endereço: p e q são a mesma variável _(é o que a crença espera)_

A máquina imprime:

```
0x1000
0x2A00
```

_Os números dos lugares mudam de máquina para máquina; aqui eles aparecem como números de exemplo. O que foi conferido é que as duas linhas saem com endereços diferentes._

O que isto mostra: Saíram dois endereços diferentes: p e q são dois ponteiros, cada um no seu lugar. Guardam o mesmo endereço, o de idade, e é por isso que os dois levam a ela.
