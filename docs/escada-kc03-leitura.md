# A escada do kc_03 — Declaração e inicialização

Texto para leitura, gerado de `mvp/dominio/escada_kc03.yaml`. Cada degrau tem duas versões: a segunda, com outros valores, aparece quando o mesmo passo volta, como no treino e na reconferência do fim.

## B1 — Declarar uma variável cria a caixa dela. Uma caixa: a que você nomeou.

### Degrau 1 — guiado, escolher

> Uma variável precisa de um lugar na memória antes de poder receber valor.
> Quem reserva esse lugar é a declaração.

**Versão 1.** Depois dessa linha, o que já existe?

Já está escrito:

```c
int idade;
```

Opções: `O lugar de idade, reservado`  `Nada ainda: sem valor, a variável não existe`  `O lugar de idade, com zero dentro`

Resposta certa: `O lugar de idade, reservado`

Se errar:

- respondeu `Nada ainda: sem valor, a variável não existe` → A declaração já reserva o lugar, com valor ou sem. O que falta a idade é o valor, e não a existência. _(aponta a crença `no_value_no_memory`)_
- respondeu `O lugar de idade, com zero dentro` → O lugar existe, mas ninguém escreveu zero nele. Declarar reserva; não escreve.
- qualquer outro erro → A declaração reserva o lugar de idade. O valor vem depois.

**Versão 2.** Depois dessa linha, o que já existe?

Já está escrito:

```c
int nota;
```

Opções: `O lugar de nota, reservado`  `Nada ainda: sem valor, a variável não existe`  `O lugar de nota, com zero dentro`

Resposta certa: `O lugar de nota, reservado`

Se errar:

- respondeu `Nada ainda: sem valor, a variável não existe` → A declaração já reserva o lugar, com valor ou sem. O que falta a nota é o valor, e não a existência. _(aponta a crença `no_value_no_memory`)_
- respondeu `O lugar de nota, com zero dentro` → O lugar existe, mas ninguém escreveu zero nele. Declarar reserva; não escreve.
- qualquer outro erro → A declaração reserva o lugar de nota. O valor vem depois.

### Degrau 2 — guiado, montar

> Como o lugar já existe, ele já tem endereço.
> Dá para guardar o endereço de idade num ponteiro antes de idade receber qualquer valor.

**Versão 1.** idade ainda não tem valor. Guarde o endereço dela em p.

Já está escrito:

```c
int idade;
int *p;
```

Peças: `p`  `=`  `&idade`  `;`  `idade`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = idade ;` → idade, sem o &, seria o valor guardado, e ela ainda nem tem valor. O que já existe é o lugar: p = &idade;
- respondeu `&idade = p ;` → Quem recebe fica à esquerda do sinal de igual. É p que recebe o endereço: p = &idade;
- qualquer outro erro → O lugar de idade já existe, e o endereço dele é &idade: p = &idade;

**Versão 2.** nota ainda não tem valor. Guarde o endereço dela em q.

Já está escrito:

```c
int nota;
int *q;
```

Peças: `q`  `=`  `&nota`  `;`  `nota`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = nota ;` → nota, sem o &, seria o valor guardado, e ela ainda nem tem valor. O que já existe é o lugar: q = &nota;
- respondeu `&nota = q ;` → Quem recebe fica à esquerda do sinal de igual. É q que recebe o endereço: q = &nota;
- qualquer outro erro → O lugar de nota já existe, e o endereço dele é &nota: q = &nota;

### Degrau 3 — guiado, digitar

> Com o endereço na mão, dá para escrever no lugar de idade pelo ponteiro.
> É a primeira escrita em idade, e ela encontra o lugar pronto.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

p = &idade;
*p = 15;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → Ninguém pôs zero em idade. A linha *p = 15; escreveu 15 no lugar dela, que existia desde a declaração.
- qualquer outro erro → O lugar de idade existe desde a declaração. *p = 15; escreveu nele: o trecho mostra 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int *q;

q = &pontos;
*q = 3;
printf("%d\n", pontos);
```

Resposta certa: `3`

Se errar:

- digitou `0` → Ninguém pôs zero em pontos. A linha *q = 3; escreveu 3 no lugar dela, que existia desde a declaração.
- qualquer outro erro → O lugar de pontos existe desde a declaração. *q = 3; escreveu nele: o trecho mostra 3.

### Degrau 4 — prática, montar

_Nome do passo, no fechamento: Pegar o endereço de uma variável ainda sem valor_

**Versão 1.** Declare um inteiro chamado nota e, sem dar valor a ele, guarde o endereço dele em q.

Já está escrito:

```c
int *q;
```

Peças: `int nota;`  `q = &nota;`  `nota = 0;`  `q = nota;`

Resposta certa: `int nota; q = &nota;`

Se errar:

- respondeu `q = &nota; int nota;` → Primeiro a declaração, que cria o lugar. Só depois o endereço: int nota; e então q = &nota;
- respondeu `int nota; q = nota;` → nota, sem o &, é o valor guardado, e o ponteiro recebe endereço. O compilador reclama. O certo é q = &nota;
- respondeu `int nota; nota = 0; q = &nota;` → Não precisava do valor: o lugar de nota existe desde a declaração. Bastam int nota; e q = &nota;
- qualquer outro erro → São duas linhas: int nota; cria o lugar, e q = &nota; guarda o endereço dele.

**Versão 2.** Declare um inteiro chamado idade e, sem dar valor a ele, guarde o endereço dele em p.

Já está escrito:

```c
int *p;
```

Peças: `int idade;`  `p = &idade;`  `idade = 0;`  `p = idade;`

Resposta certa: `int idade; p = &idade;`

Se errar:

- respondeu `p = &idade; int idade;` → Primeiro a declaração, que cria o lugar. Só depois o endereço: int idade; e então p = &idade;
- respondeu `int idade; p = idade;` → idade, sem o &, é o valor guardado, e o ponteiro recebe endereço. O compilador reclama. O certo é p = &idade;
- respondeu `int idade; idade = 0; p = &idade;` → Não precisava do valor: o lugar de idade existe desde a declaração. Bastam int idade; e p = &idade;
- qualquer outro erro → São duas linhas: int idade; cria o lugar, e p = &idade; guarda o endereço dele.

### Degrau 5 — prática, escolher

**Versão 1.** Quantos lugares da memória estas três linhas reservam?

Já está escrito:

```c
int idade;
int nota;
int *p;
```

Opções: `Três: um para cada nome declarado`  `Dois: o ponteiro não conta`  `Nenhum: nada recebeu valor`

Resposta certa: `Três: um para cada nome declarado`

Se errar:

- respondeu `Dois: o ponteiro não conta` → O ponteiro é uma variável como as outras, e a declaração reserva o lugar dele também. São três.
- respondeu `Nenhum: nada recebeu valor` → Declarar já reserva o lugar, com valor ou sem. São três nomes declarados, e três lugares.
- qualquer outro erro → Cada declaração reserva um lugar: o de idade, o de nota e o de p.

**Versão 2.** Quantos lugares da memória estas três linhas reservam?

Já está escrito:

```c
char turma;
int *q;
int pontos;
```

Opções: `Três: um para cada nome declarado`  `Dois: o ponteiro não conta`  `Nenhum: nada recebeu valor`

Resposta certa: `Três: um para cada nome declarado`

Se errar:

- respondeu `Dois: o ponteiro não conta` → O ponteiro é uma variável como as outras, e a declaração reserva o lugar dele também. São três.
- respondeu `Nenhum: nada recebeu valor` → Declarar já reserva o lugar, com valor ou sem. São três nomes declarados, e três lugares.
- qualquer outro erro → Cada declaração reserva um lugar: o de turma, o de q e o de pontos.

### Se errar a pergunta do topo: a revisão

> Declarar cria o lugar da variável, antes de qualquer valor.
> Vale para toda variável: int idade; cria o lugar de idade, e int *p; cria o lugar de p.

```c
int idade;
int *p;
```

### Se a pessoa disser a crença: a prova

Você disse:

> Se eu não dei valor, a variável ainda não existe na memória.

```c
int nota;
int *q;

q = &nota;
*q = 7;
printf("%d\n", nota);
```

**Quando a linha q = &nota; roda, nota ainda não recebeu valor nenhum. O que o trecho imprime?**

- 7 _(é o que a máquina faz)_
- Nada: sem valor, nota ainda não existe, e não tem endereço _(é o que a crença espera)_

A máquina imprime:

```
7
```

O que isto mostra: Saiu 7. O endereço de nota foi pego antes de ela ter valor, e o 7 entrou por ele. O lugar existe desde a declaração; o valor só chega depois.

## B2 — Em int *p, quem é criado é p. O asterisco faz parte do que p é, e não é uma segunda caixa.

### Degrau 1 — guiado, tocar

> Em int *p; a variável que nasce se chama p.
> O * não é outra variável: ele faz parte do que p é.

**Versão 1.** Toque no nome da variável declarada.

```c
int *p;
```

Peças: `int`  `*`  `p`  `;`

Resposta certa: `p`

Se errar:

- respondeu `*` → O * não é nome nem variável: ele diz que p é um ponteiro. O nome é p.
- respondeu `int` → int é o tipo do que fica no endereço guardado. O nome da variável é p.
- respondeu `;` → O ponto e vírgula só fecha a linha. O nome da variável é p.
- qualquer outro erro → A variável declarada se chama p. O * diz que ela é um ponteiro.

**Versão 2.** Toque no nome da variável declarada.

```c
char *c;
```

Peças: `char`  `*`  `c`  `;`

Resposta certa: `c`

Se errar:

- respondeu `*` → O * não é nome nem variável: ele diz que c é um ponteiro. O nome é c.
- respondeu `char` → char é o tipo do que fica no endereço guardado. O nome da variável é c.
- respondeu `;` → O ponto e vírgula só fecha a linha. O nome da variável é c.
- qualquer outro erro → A variável declarada se chama c. O * diz que ela é um ponteiro.

### Degrau 2 — guiado, escolher

> Dá para declarar dois nomes numa linha, separados por vírgula.
> O * vale só para o nome em que está colado: em int *a, b; só a é ponteiro.

**Versão 1.** O que esta linha declara?

Já está escrito:

```c
int *p, q;
```

Opções: `Um ponteiro, p, e um int comum, q`  `Dois ponteiros: o * é do tipo, e vale para os dois`  `Dois ints comuns`

Resposta certa: `Um ponteiro, p, e um int comum, q`

Se errar:

- respondeu `Dois ponteiros: o * é do tipo, e vale para os dois` → O * não pertence ao tipo: pertence ao nome em que está colado. Aqui só p é ponteiro; q é um int comum. _(aponta a crença `estrela_e_do_tipo`)_
- respondeu `Dois ints comuns` → p tem o * na frente, e é ponteiro. q não tem, e é um int comum.
- qualquer outro erro → p, que leva o *, é ponteiro. q, que não leva, é um int comum.

**Versão 2.** O que esta linha declara?

Já está escrito:

```c
char *c, d;
```

Opções: `Um ponteiro, c, e um char comum, d`  `Dois ponteiros: o * é do tipo, e vale para os dois`  `Dois chars comuns`

Resposta certa: `Um ponteiro, c, e um char comum, d`

Se errar:

- respondeu `Dois ponteiros: o * é do tipo, e vale para os dois` → O * não pertence ao tipo: pertence ao nome em que está colado. Aqui só c é ponteiro; d é um char comum. _(aponta a crença `estrela_e_do_tipo`)_
- respondeu `Dois chars comuns` → c tem o * na frente, e é ponteiro. d não tem, e é um char comum.
- qualquer outro erro → c, que leva o *, é ponteiro. d, que não leva, é um char comum.

### Degrau 3 — guiado, montar

> Para declarar dois ponteiros na mesma linha, ponha um * em cada nome.

**Versão 1.** Declare, numa linha só, dois ponteiros para inteiro: p e q.

Peças: `int`  `*p`  `,`  `*q`  `;`  `q`

Resposta certa: `int *p, *q;`

Se errar:

- respondeu `int *p , q ;` → Assim q fica um int comum: o * de p não vale para ele. Cada ponteiro leva o seu: int *p, *q;
- qualquer outro erro → Cada nome leva o seu *: int *p, *q;

**Versão 2.** Declare, numa linha só, dois ponteiros para caractere: c e d.

Peças: `char`  `*c`  `,`  `*d`  `;`  `d`

Resposta certa: `char *c, *d;`

Se errar:

- respondeu `char *c , d ;` → Assim d fica um char comum: o * de c não vale para ele. Cada ponteiro leva o seu: char *c, *d;
- qualquer outro erro → Cada nome leva o seu *: char *c, *d;

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Declarar dois ponteiros na mesma linha_

**Versão 1.** Qual linha declara dois ponteiros?

Opções: `int *p, *q;`  `int* p, q;`  `int p, q;`

Resposta certa: `int *p, *q;`

Se errar:

- respondeu `int* p, q;` → Mudar o espaço de lugar não muda nada: o * continua valendo só para p, e q fica um int comum. Dois ponteiros: int *p, *q;
- respondeu `int p, q;` → Sem * nenhum, os dois são ints comuns. Dois ponteiros: int *p, *q;
- qualquer outro erro → Dois ponteiros pedem dois asteriscos, um em cada nome: int *p, *q;

**Versão 2.** Qual linha declara dois ponteiros?

Opções: `char* c, d;`  `char *c, *d;`  `char c, d;`

Resposta certa: `char *c, *d;`

Se errar:

- respondeu `char* c, d;` → Mudar o espaço de lugar não muda nada: o * continua valendo só para c, e d fica um char comum. Dois ponteiros: char *c, *d;
- respondeu `char c, d;` → Sem * nenhum, os dois são chars comuns. Dois ponteiros: char *c, *d;
- qualquer outro erro → Dois ponteiros pedem dois asteriscos, um em cada nome: char *c, *d;

### Degrau 5 — prática, completar

**Versão 1.** q foi declarada na segunda linha. Complete com o que q pode receber.

Já está escrito:

```c
int idade;
int *p, q;
```

```c
q = ___;
```

Peças: `15`  `&idade`  `p`

Resposta certa: `q = 15;`

Se errar:

- respondeu `q = &idade;` → q não é ponteiro: o * da segunda linha é só de p. q é um int comum, e recebe um número: q = 15;
- respondeu `q = p;` → p é ponteiro, e q é um int comum: o * não valeu para ele. q recebe um número: q = 15;
- qualquer outro erro → Em int *p, q; só p é ponteiro. q é um int comum: q = 15;

**Versão 2.** n foi declarada na segunda linha. Complete com o que n pode receber.

Já está escrito:

```c
int nota;
int *q, n;
```

```c
n = ___;
```

Peças: `7`  `&nota`  `q`

Resposta certa: `n = 7;`

Se errar:

- respondeu `n = &nota;` → n não é ponteiro: o * da segunda linha é só de q. n é um int comum, e recebe um número: n = 7;
- respondeu `n = q;` → q é ponteiro, e n é um int comum: o * não valeu para ele. n recebe um número: n = 7;
- qualquer outro erro → Em int *q, n; só q é ponteiro. n é um int comum: n = 7;

### Se errar a pergunta do topo: a revisão

> Em int *p; a variável criada se chama p. O * diz o que p é: um ponteiro.
> Cada nome leva o seu *: int *p, *q; declara dois ponteiros, e int *p, q; um ponteiro e um int.

```c
int *p, *q;
```

### Se a pessoa disser a crença: a prova

Você disse:

> O asterisco pertence ao tipo, então int* a, b; declara dois ponteiros.

```c
int idade;
int* p, q;

p = &idade;
q = &idade;
```

**A segunda linha escreve o * junto do tipo e declara p e q. O compilador reclama de alguma das duas últimas linhas?**

- Não: int* vale para os dois, e p e q são ponteiros _(é o que a crença espera)_
- Sim, de p = &idade;
- Sim, de q = &idade; _(é o que a máquina faz)_

O compilador reclama:

```
makes integer from pointer without a cast
```

_Mensagem do gcc 16.2 para a linha de q. Todo compilador de C tem de reclamar dela, cada um com as suas palavras._

O que isto mostra: O compilador reclama só de q: ele é um int comum, e &idade é um endereço. O * não pertence ao tipo — pertence ao nome em que está colado, e ali só p ficou ponteiro.

## B3 — C não limpa a caixa nova. O que estava naquele lugar antes continua lá.

### Degrau 1 — guiado, escolher

> Declarar reserva o lugar, mas não escreve nada nele.
> E a memória nunca fica vazia: todo lugar guarda algum valor, deixado por quem o usou antes.

**Versão 1.** Logo depois dessa linha, o que está guardado em nota?

Já está escrito:

```c
int nota;
```

Opções: `O que já estava naquele lugar: ninguém escolheu`  `Zero: declarar já zera a variável`  `Nada: o lugar está vazio`

Resposta certa: `O que já estava naquele lugar: ninguém escolheu`

Se errar:

- respondeu `Zero: declarar já zera a variável` → O C não zera o que você declara. O lugar fica com o que já estava nele, e ninguém escolheu esse valor. _(aponta a crença `declaration_zeroes`)_
- respondeu `Nada: o lugar está vazio` → Lugar da memória não fica vazio: sempre há alguma coisa guardada. Aqui, o que já estava lá antes.
- qualquer outro erro → Declarar não escreve nada. nota fica com o que já estava naquele lugar.

**Versão 2.** Logo depois dessa linha, o que está guardado em idade?

Já está escrito:

```c
int idade;
```

Opções: `O que já estava naquele lugar: ninguém escolheu`  `Zero: declarar já zera a variável`  `Nada: o lugar está vazio`

Resposta certa: `O que já estava naquele lugar: ninguém escolheu`

Se errar:

- respondeu `Zero: declarar já zera a variável` → O C não zera o que você declara. O lugar fica com o que já estava nele, e ninguém escolheu esse valor. _(aponta a crença `declaration_zeroes`)_
- respondeu `Nada: o lugar está vazio` → Lugar da memória não fica vazio: sempre há alguma coisa guardada. Aqui, o que já estava lá antes.
- qualquer outro erro → Declarar não escreve nada. idade fica com o que já estava naquele lugar.

### Degrau 2 — guiado, escolher

> Com o ponteiro, declarar faz o mesmo que com a variável comum.
> Reserva o lugar, e não escreve nada nele.

**Versão 1.** Logo depois dessa linha, o que está guardado em p?

Já está escrito:

```c
int *p;
```

Opções: `Um valor que ninguém escolheu`  `O endereço de um int que acabou de ser criado`  `Zero: ponteiro novo vem zerado`

Resposta certa: `Um valor que ninguém escolheu`

Se errar:

- respondeu `O endereço de um int que acabou de ser criado` → A linha cria só o ponteiro. Ninguém escreveu endereço nenhum em p: ele guarda o que já estava naquele lugar.
- respondeu `Zero: ponteiro novo vem zerado` → O C não zera o que você declara, e ponteiro não é exceção. p guarda o que já estava naquele lugar.
- qualquer outro erro → p foi declarado e ninguém escreveu nele: guarda um valor que ninguém escolheu.

**Versão 2.** Logo depois dessa linha, o que está guardado em c?

Já está escrito:

```c
char *c;
```

Opções: `Um valor que ninguém escolheu`  `O endereço de um char que acabou de ser criado`  `Zero: ponteiro novo vem zerado`

Resposta certa: `Um valor que ninguém escolheu`

Se errar:

- respondeu `O endereço de um char que acabou de ser criado` → A linha cria só o ponteiro. Ninguém escreveu endereço nenhum em c: ele guarda o que já estava naquele lugar.
- respondeu `Zero: ponteiro novo vem zerado` → O C não zera o que você declara, e ponteiro não é exceção. c guarda o que já estava naquele lugar.
- qualquer outro erro → c foi declarado e ninguém escreveu nele: guarda um valor que ninguém escolheu.

### Degrau 3 — guiado, montar

> Por isso a regra do começo continua valendo: escreva antes de ler.
> Para a variável começar em zero, o zero tem de ser escrito por uma linha sua.

**Versão 1.** Faça nota começar valendo zero.

Já está escrito:

```c
int nota;
```

Peças: `nota`  `=`  `0`  `;`  `int`

Resposta certa: `nota = 0;`

Se errar:

- respondeu `int nota ;` → Declarar de novo não zera nada, e o compilador reclama da repetição. O zero entra por uma escrita: nota = 0;
- respondeu `0 = nota ;` → Quem recebe fica à esquerda do sinal de igual. É nota que recebe o zero: nota = 0;
- qualquer outro erro → O zero entra por uma linha que escreve: nota = 0;

**Versão 2.** Faça idade começar valendo zero.

Já está escrito:

```c
int idade;
```

Peças: `idade`  `=`  `0`  `;`  `int`

Resposta certa: `idade = 0;`

Se errar:

- respondeu `int idade ;` → Declarar de novo não zera nada, e o compilador reclama da repetição. O zero entra por uma escrita: idade = 0;
- respondeu `0 = idade ;` → Quem recebe fica à esquerda do sinal de igual. É idade que recebe o zero: idade = 0;
- qualquer outro erro → O zero entra por uma linha que escreve: idade = 0;

### Degrau 4 — prática, montar

_Nome do passo, no fechamento: Escrever na variável antes de ler_

**Versão 1.** Ponha as linhas na ordem em que nota só é lida depois de receber valor.

Peças: `int nota;`  `printf("%d\n", nota);`  `nota = 7;`

Resposta certa: `int nota; nota = 7; printf("%d\n", nota);`

Se errar:

- respondeu `int nota; printf("%d\n", nota); nota = 7;` → Nessa ordem o printf lê nota antes de alguém escrever nela. Primeiro nota = 7; e só depois o printf.
- respondeu `nota = 7; int nota; printf("%d\n", nota);` → nota = 7; não pode vir antes da declaração: a variável ainda não existe. Declarar, escrever, ler.
- qualquer outro erro → A ordem é declarar, escrever e só então ler.

**Versão 2.** Ponha as linhas na ordem em que idade só é lida depois de receber valor.

Peças: `int idade;`  `printf("%d\n", idade);`  `idade = 15;`

Resposta certa: `int idade; idade = 15; printf("%d\n", idade);`

Se errar:

- respondeu `int idade; printf("%d\n", idade); idade = 15;` → Nessa ordem o printf lê idade antes de alguém escrever nela. Primeiro idade = 15; e só depois o printf.
- respondeu `idade = 15; int idade; printf("%d\n", idade);` → idade = 15; não pode vir antes da declaração: a variável ainda não existe. Declarar, escrever, ler.
- qualquer outro erro → A ordem é declarar, escrever e só então ler.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas variáveis ainda não pode ser lida?

Já está escrito:

```c
int idade;
int nota;
int *p;

nota = 0;
p = &nota;
```

Opções: `idade: foi declarada, e ninguém escreveu nela`  `nota: zero não conta como valor`  `p: ponteiro não pode ser lido`

Resposta certa: `idade: foi declarada, e ninguém escreveu nela`

Se errar:

- respondeu `nota: zero não conta como valor` → Zero é um valor como outro qualquer, e foi escrito por uma linha. A que ninguém escreveu é idade.
- respondeu `p: ponteiro não pode ser lido` → p recebeu o endereço de nota, e pode ser lido. A que ninguém escreveu é idade.
- qualquer outro erro → idade foi declarada e não recebeu valor: é a que ainda não pode ser lida.

**Versão 2.** Qual destas variáveis ainda não pode ser lida?

Já está escrito:

```c
int pontos;
int ano;
int *q;

ano = 0;
q = &pontos;
```

Opções: `pontos: foi declarada, e ninguém escreveu nela`  `ano: zero não conta como valor`  `q: ponteiro não pode ser lido`

Resposta certa: `pontos: foi declarada, e ninguém escreveu nela`

Se errar:

- respondeu `ano: zero não conta como valor` → Zero é um valor como outro qualquer, e foi escrito por uma linha. A que ninguém escreveu é pontos.
- respondeu `q: ponteiro não pode ser lido` → q recebeu o endereço de pontos, e pode ser lido. A que ninguém escreveu é pontos.
- qualquer outro erro → pontos foi declarada e não recebeu valor: é a que ainda não pode ser lida.

### Se errar a pergunta do topo: a revisão

> O C não escreve nada na variável quando você declara: nem zero.
> Vale para o ponteiro também: logo depois de int *p; ninguém escolheu o que p guarda.

```c
int nota;
int *p;

nota = 0;
p = &nota;
```

### Se a pessoa disser a crença: a prova

Você disse:

> Declarar já zera a variável, como em outras linguagens.

```c
int nota;

printf("%d\n", nota);
```

**O compilador reclama de alguma coisa neste trecho?**

- Não: nota foi declarada, e começa valendo 0 _(é o que a crença espera)_
- Sim: nota está sendo lida sem ter recebido valor _(é o que a máquina faz)_

O compilador reclama:

```
'nota' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o que ele imprimiria, ninguém sabe._

O que isto mostra: Se declarar zerasse a variável, não haveria do que reclamar. O compilador avisa que nota é lida sem valor ("used uninitialized"): o C não escreveu nada ali, nem zero.

## I1 — Então declarar p não cria a caixa apontada. Até aqui existe uma caixa só.

### Degrau 1 — guiado, escolher

> Declarar cria a variável declarada, e só ela.
> O lugar para onde um ponteiro vai apontar não nasce junto: quem cria esse lugar é outra declaração.

**Versão 1.** Quantos lugares da memória essa linha reserva?

Já está escrito:

```c
int *p;
```

Opções: `Um: o de p`  `Dois: o de p e o do int apontado, que já vem criado`  `Nenhum: p não recebeu valor`

Resposta certa: `Um: o de p`

Se errar:

- respondeu `Dois: o de p e o do int apontado, que já vem criado` → A linha declara um nome só, p, e reserva um lugar só. O int apontado não vem junto: precisa de uma declaração dele. _(aponta a crença `declaration_allocates`)_
- respondeu `Nenhum: p não recebeu valor` → Declarar já reserva o lugar, com valor ou sem. A linha reserva um: o de p.
- qualquer outro erro → A linha reserva um lugar só: o do ponteiro p.

**Versão 2.** Quantos lugares da memória essa linha reserva?

Já está escrito:

```c
char *c;
```

Opções: `Um: o de c`  `Dois: o de c e o do char apontado, que já vem criado`  `Nenhum: c não recebeu valor`

Resposta certa: `Um: o de c`

Se errar:

- respondeu `Dois: o de c e o do char apontado, que já vem criado` → A linha declara um nome só, c, e reserva um lugar só. O char apontado não vem junto: precisa de uma declaração dele. _(aponta a crença `declaration_allocates`)_
- respondeu `Nenhum: c não recebeu valor` → Declarar já reserva o lugar, com valor ou sem. A linha reserva um: o de c.
- qualquer outro erro → A linha reserva um lugar só: o do ponteiro c.

### Degrau 2 — guiado, completar

> Para o ponteiro ter para onde apontar, declare a variável e entregue o endereço dela.

**Versão 1.** Complete para p apontar para um lugar que existe.

Já está escrito:

```c
int idade;
int *p;
```

```c
p = ___;
```

Peças: `&idade`  `*p`  `10`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = *p;` → *p é o lugar apontado, e p ainda não aponta para lugar nenhum. O lugar que existe é o de idade: p = &idade;
- respondeu `p = 10;` → 10 é um valor, e não um endereço. p precisa do endereço de uma variável que exista: p = &idade;
- qualquer outro erro → O lugar que existe é o de idade, e o endereço dele é &idade: p = &idade;

**Versão 2.** Complete para q apontar para um lugar que existe.

Já está escrito:

```c
int nota;
int *q;
```

```c
q = ___;
```

Peças: `&nota`  `*q`  `7`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = *q;` → *q é o lugar apontado, e q ainda não aponta para lugar nenhum. O lugar que existe é o de nota: q = &nota;
- respondeu `q = 7;` → 7 é um valor, e não um endereço. q precisa do endereço de uma variável que exista: q = &nota;
- qualquer outro erro → O lugar que existe é o de nota, e o endereço dele é &nota: q = &nota;

### Degrau 3 — guiado, digitar

> Agora *p tem dono: é o lugar de idade.
> Escrever em *p é escrever em idade.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

p = &idade;
*p = 10;
printf("%d\n", idade);
```

Resposta certa: `10`

Se errar:

- digitou `0` → Ninguém zerou idade. A linha *p = 10; escreveu 10 no lugar dela, que é para onde p aponta.
- qualquer outro erro → p aponta para idade. *p = 10; escreveu em idade: o trecho mostra 10.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

q = &nota;
*q = 4;
printf("%d\n", nota);
```

Resposta certa: `4`

Se errar:

- digitou `0` → Ninguém zerou nota. A linha *q = 4; escreveu 4 no lugar dela, que é para onde q aponta.
- qualquer outro erro → q aponta para nota. *q = 4; escreveu em nota: o trecho mostra 4.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Dar ao ponteiro um lugar de verdade para apontar_

**Versão 1.** Em qual trecho *p tem um lugar de verdade?

Opção 1:

```c
int idade;
int *p;
p = &idade;
```

Opção 2:

```c
int *p;
```

Opção 3:

```c
int idade;
int *p;
```

Resposta certa: `int idade; int *p; p = &idade;`

Se errar:

- respondeu `int *p;` → Aqui só existe o lugar de p. O lugar apontado não nasce com a declaração do ponteiro.
- respondeu `int idade;
int *p;` → idade existe, mas p não recebeu o endereço dela. Falta a linha p = &idade;
- qualquer outro erro → *p só tem lugar quando existe uma variável e p recebeu o endereço dela.

**Versão 2.** Em qual trecho *q tem um lugar de verdade?

Opção 1:

```c
int nota;
int *q;
```

Opção 2:

```c
int nota;
int *q;
q = &nota;
```

Opção 3:

```c
int *q;
```

Resposta certa: `int nota; int *q; q = &nota;`

Se errar:

- respondeu `int nota;
int *q;` → nota existe, mas q não recebeu o endereço dela. Falta a linha q = &nota;
- respondeu `int *q;` → Aqui só existe o lugar de q. O lugar apontado não nasce com a declaração do ponteiro.
- qualquer outro erro → *q só tem lugar quando existe uma variável e q recebeu o endereço dela.

### Degrau 5 — prática, montar

**Versão 1.** Monte, em três linhas, um ponteiro q com um lugar de verdade para apontar.

Peças: `int nota;`  `int *q;`  `q = &nota;`  `int *nota;`

Resposta certa: `int nota; int *q; q = &nota;`

Se errar:

- respondeu `int *nota; int *q; q = &nota;` → int *nota; cria outro ponteiro, e não o int para onde q vai apontar. O lugar apontado é int nota;
- respondeu `int nota; int *q;` → Faltou entregar o endereço: sem q = &nota; o ponteiro não aponta para o lugar que você criou.
- respondeu `int *q; q = &nota;` → Faltou criar o lugar apontado. Sem int nota; não existe nota nenhuma para dar o endereço.
- qualquer outro erro → São três linhas: int nota; cria o lugar, int *q; cria o ponteiro, e q = &nota; liga um ao outro.

**Versão 2.** Monte, em três linhas, um ponteiro p com um lugar de verdade para apontar.

Peças: `int idade;`  `int *p;`  `p = &idade;`  `int *idade;`

Resposta certa: `int idade; int *p; p = &idade;`

Se errar:

- respondeu `int *idade; int *p; p = &idade;` → int *idade; cria outro ponteiro, e não o int para onde p vai apontar. O lugar apontado é int idade;
- respondeu `int idade; int *p;` → Faltou entregar o endereço: sem p = &idade; o ponteiro não aponta para o lugar que você criou.
- respondeu `int *p; p = &idade;` → Faltou criar o lugar apontado. Sem int idade; não existe idade nenhuma para dar o endereço.
- qualquer outro erro → São três linhas: int idade; cria o lugar, int *p; cria o ponteiro, e p = &idade; liga um ao outro.

### Se errar a pergunta do topo: a revisão

> int *p; cria uma variável só: p. O lugar apontado não vem junto.
> Para p ter para onde apontar, é preciso existir outra variável, e p receber o endereço dela.

```c
int idade;
int *p;

p = &idade;
*p = 10;
printf("%d\n", idade);
```

A máquina imprime:

```
10
```

### Se a pessoa disser a crença: a prova

Você disse:

> int *p já cria o dado apontado automaticamente.

```c
int *p;

printf("%d\n", *p);
```

**O printf pede o valor que mora no lugar apontado por p. O compilador reclama de alguma coisa?**

- Sim: p não recebeu o endereço de lugar nenhum _(é o que a máquina faz)_
- Não: int *p; já criou o int para onde p aponta _(é o que a crença espera)_

O compilador reclama:

```
'p' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o lugar que ele leria, ninguém escolheu._

O que isto mostra: O compilador avisa que p é usado sem ter recebido valor. A declaração criou só o ponteiro: não há int nenhum esperando do outro lado.

## I2 — Nesse ponto p guarda um valor qualquer, sobra do que estava ali. Não é NULL.

### Degrau 1 — guiado, escolher

> Existe um valor especial para ponteiro: NULL. Ele quer dizer: não aponta para lugar nenhum.
> NULL não aparece sozinho. Um ponteiro só vale NULL se uma linha escreveu NULL nele.

**Versão 1.** Logo depois dessa linha, p vale NULL?

Já está escrito:

```c
int *p;
```

Opções: `Não: p guarda um valor que ninguém escolheu`  `Sim: ponteiro que não recebeu valor vale NULL`  `Sim: declarar já zera, e zero é NULL`

Resposta certa: `Não: p guarda um valor que ninguém escolheu`

Se errar:

- respondeu `Sim: ponteiro que não recebeu valor vale NULL` → NULL é um valor, e ninguém o escreveu em p. O ponteiro recém-declarado guarda o que já estava naquele lugar. _(aponta a crença `uninitialized_is_null`)_
- respondeu `Sim: declarar já zera, e zero é NULL` → O C não zera o que você declara. p guarda o que já estava naquele lugar, e não NULL.
- qualquer outro erro → Ninguém escreveu NULL em p. Ele guarda um valor que ninguém escolheu.

**Versão 2.** Logo depois dessa linha, c vale NULL?

Já está escrito:

```c
char *c;
```

Opções: `Não: c guarda um valor que ninguém escolheu`  `Sim: ponteiro que não recebeu valor vale NULL`  `Sim: declarar já zera, e zero é NULL`

Resposta certa: `Não: c guarda um valor que ninguém escolheu`

Se errar:

- respondeu `Sim: ponteiro que não recebeu valor vale NULL` → NULL é um valor, e ninguém o escreveu em c. O ponteiro recém-declarado guarda o que já estava naquele lugar. _(aponta a crença `uninitialized_is_null`)_
- respondeu `Sim: declarar já zera, e zero é NULL` → O C não zera o que você declara. c guarda o que já estava naquele lugar, e não NULL.
- qualquer outro erro → Ninguém escreveu NULL em c. Ele guarda um valor que ninguém escolheu.

### Degrau 2 — guiado, montar

> Para um ponteiro valer NULL, escreva NULL nele.

**Versão 1.** Faça p valer NULL.

Já está escrito:

```c
int *p;
```

Peças: `p`  `=`  `NULL`  `;`  `*p`

Resposta certa: `p = NULL;`

Se errar:

- respondeu `*p = NULL ;` → *p é o lugar apontado, e p ainda não aponta para lugar nenhum. O NULL vai no próprio ponteiro: p = NULL;
- respondeu `NULL = p ;` → Quem recebe fica à esquerda do sinal de igual. É p que recebe o NULL: p = NULL;
- qualquer outro erro → O NULL é escrito no próprio ponteiro: p = NULL;

**Versão 2.** Faça q valer NULL.

Já está escrito:

```c
int *q;
```

Peças: `q`  `=`  `NULL`  `;`  `*q`

Resposta certa: `q = NULL;`

Se errar:

- respondeu `*q = NULL ;` → *q é o lugar apontado, e q ainda não aponta para lugar nenhum. O NULL vai no próprio ponteiro: q = NULL;
- respondeu `NULL = q ;` → Quem recebe fica à esquerda do sinal de igual. É q que recebe o NULL: q = NULL;
- qualquer outro erro → O NULL é escrito no próprio ponteiro: q = NULL;

### Degrau 3 — guiado, escolher

> O ponteiro também pode já nascer valendo NULL, numa declaração com valor.
> É declarar e dar o valor na mesma linha, como em int idade = 15;

**Versão 1.** Em qual linha p vale NULL com certeza?

Opções: `int *p = NULL;`  `int *p;`  `int *p, *q;`

Resposta certa: `int *p = NULL;`

Se errar:

- respondeu `int *p;` → Aqui ninguém escreveu NULL em p: ele guarda um valor que ninguém escolheu. Com certeza, só em int *p = NULL;
- respondeu `int *p, *q;` → Declarar dois ponteiros não escreve nada em nenhum deles. Com certeza, só em int *p = NULL;
- qualquer outro erro → p só vale NULL com certeza onde uma linha escreveu: int *p = NULL;

**Versão 2.** Em qual linha c vale NULL com certeza?

Opções: `char *c;`  `char *c = NULL;`  `char *c, *d;`

Resposta certa: `char *c = NULL;`

Se errar:

- respondeu `char *c;` → Aqui ninguém escreveu NULL em c: ele guarda um valor que ninguém escolheu. Com certeza, só em char *c = NULL;
- respondeu `char *c, *d;` → Declarar dois ponteiros não escreve nada em nenhum deles. Com certeza, só em char *c = NULL;
- qualquer outro erro → c só vale NULL com certeza onde uma linha escreveu: char *c = NULL;

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Saber qual ponteiro vale NULL_

**Versão 1.** Depois destas linhas, qual ponteiro vale NULL?

Já está escrito:

```c
int *p;
int *q;

q = NULL;
```

Opções: `Só q: foi o único em que uma linha escreveu NULL`  `Os dois: ponteiro sem endereço vale NULL`  `Nenhum: p ainda não foi usado`

Resposta certa: `Só q: foi o único em que uma linha escreveu NULL`

Se errar:

- respondeu `Os dois: ponteiro sem endereço vale NULL` → p não recebeu nada: guarda um valor que ninguém escolheu, e não NULL. Só q vale NULL, porque uma linha escreveu.
- respondeu `Nenhum: p ainda não foi usado` → q recebeu NULL na última linha, e vale NULL. p é que ficou sem valor escolhido.
- qualquer outro erro → Vale NULL o ponteiro em que uma linha escreveu NULL: só q.

**Versão 2.** Depois destas linhas, qual ponteiro vale NULL?

Já está escrito:

```c
char *c = NULL;
char *d;
```

Opções: `Só c: foi o único em que uma linha escreveu NULL`  `Os dois: ponteiro sem endereço vale NULL`  `Nenhum: c ainda não foi usado`

Resposta certa: `Só c: foi o único em que uma linha escreveu NULL`

Se errar:

- respondeu `Os dois: ponteiro sem endereço vale NULL` → d não recebeu nada: guarda um valor que ninguém escolheu, e não NULL. Só c vale NULL, porque uma linha escreveu.
- respondeu `Nenhum: c ainda não foi usado` → c nasceu com NULL, e vale NULL. d é que ficou sem valor escolhido.
- qualquer outro erro → Vale NULL o ponteiro em que uma linha escreveu NULL: só c.

### Degrau 5 — prática, montar

**Versão 1.** Declare um ponteiro para inteiro chamado q que já nasça valendo NULL.

Peças: `int`  `*q`  `=`  `NULL`  `;`  `q`

Resposta certa: `int *q = NULL;`

Se errar:

- respondeu `int *q ;` → Assim q nasce com um valor que ninguém escolheu, e não com NULL. O NULL tem de ser escrito: int *q = NULL;
- respondeu `int q = NULL ;` → Sem o *, q é um int comum, e NULL é valor de ponteiro. O certo é int *q = NULL;
- qualquer outro erro → É declarar o ponteiro e dar o valor na mesma linha: int *q = NULL;

**Versão 2.** Declare um ponteiro para inteiro chamado p que já nasça valendo NULL.

Peças: `int`  `*p`  `=`  `NULL`  `;`  `p`

Resposta certa: `int *p = NULL;`

Se errar:

- respondeu `int *p ;` → Assim p nasce com um valor que ninguém escolheu, e não com NULL. O NULL tem de ser escrito: int *p = NULL;
- respondeu `int p = NULL ;` → Sem o *, p é um int comum, e NULL é valor de ponteiro. O certo é int *p = NULL;
- qualquer outro erro → É declarar o ponteiro e dar o valor na mesma linha: int *p = NULL;

### Se errar a pergunta do topo: a revisão

> NULL é o valor que se escreve num ponteiro para dizer: não aponta para lugar nenhum.
> Um ponteiro só vale NULL se uma linha escreveu NULL nele. Sem isso, guarda um valor que ninguém escolheu.

```c
int *p;

p = NULL;
```

### Se a pessoa disser a crença: a prova

Você disse:

> Ponteiro não inicializado vale NULL.

```c
int *p;
int *q;

q = p;
```

**A última linha copia para q o que está guardado em p. O que o compilador diz dela?**

- Nada: p vale NULL, e copiar NULL é permitido _(é o que a crença espera)_
- Que p está sendo usado sem ter recebido valor _(é o que a máquina faz)_

O compilador reclama:

```
'p' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o que ele copiaria de p, ninguém sabe._

O que isto mostra: Para o compilador, p não vale NULL: está sem valor ("used uninitialized"). NULL é um valor como os outros — só está no ponteiro em que uma linha o escreveu.

## I3 — Por isso usar *p antes de dar um endereço a p vai a um lugar que ninguém escolheu.

### Degrau 1 — guiado, escolher

> *p vai ao lugar cujo endereço está guardado em p.
> Declarar o ponteiro não escreve endereço nenhum nele: o que ele guarda é um valor que ninguém escolheu.

**Versão 1.** Para onde a última linha manda o 10?

Já está escrito:

```c
int *p;

*p = 10;
```

Opções: `Para um lugar que ninguém escolheu: p não recebeu endereço`  `Para o lugar de p: depois de declarar, já dá para escrever em *p`  `Para lugar nenhum: a linha não faz nada`

Resposta certa: `Para um lugar que ninguém escolheu: p não recebeu endereço`

Se errar:

- respondeu `Para o lugar de p: depois de declarar, já dá para escrever em *p` → Declarar p não dá a ele um endereço. *p vai aonde o valor guardado em p mandar, e esse valor ninguém escolheu. _(aponta a crença `pode_usar_logo`)_
- respondeu `Para lugar nenhum: a linha não faz nada` → A linha faz, e é esse o problema: ela escreve no lugar que o valor guardado em p indicar. Ninguém escolheu esse lugar.
- qualquer outro erro → p não recebeu endereço. *p = 10; escreveria num lugar que ninguém escolheu.

**Versão 2.** Para onde a última linha manda o 'B'?

Já está escrito:

```c
char *c;

*c = 'B';
```

Opções: `Para um lugar que ninguém escolheu: c não recebeu endereço`  `Para o lugar de c: depois de declarar, já dá para escrever em *c`  `Para lugar nenhum: a linha não faz nada`

Resposta certa: `Para um lugar que ninguém escolheu: c não recebeu endereço`

Se errar:

- respondeu `Para o lugar de c: depois de declarar, já dá para escrever em *c` → Declarar c não dá a ele um endereço. *c vai aonde o valor guardado em c mandar, e esse valor ninguém escolheu. _(aponta a crença `pode_usar_logo`)_
- respondeu `Para lugar nenhum: a linha não faz nada` → A linha faz, e é esse o problema: ela escreve no lugar que o valor guardado em c indicar. Ninguém escolheu esse lugar.
- qualquer outro erro → c não recebeu endereço. *c = 'B'; escreveria num lugar que ninguém escolheu.

### Degrau 2 — guiado, escolher

> Por isso a ordem importa: primeiro o ponteiro recebe um endereço, e só depois vem o *p.

**Versão 1.** Qual linha tem de vir antes de *p = 10; ?

Já está escrito:

```c
int idade;
int *p;
```

Opções: `p = &idade;`  `idade = 10;`  `*p = 0;`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `idade = 10;` → idade = 10; escreve em idade, mas p continua sem endereço. O que falta antes do *p é p = &idade;
- respondeu `*p = 0;` → *p = 0; já usa o lugar apontado, e p ainda não aponta para um lugar escolhido. Antes vem p = &idade;
- qualquer outro erro → Antes de usar *p, o ponteiro recebe um endereço: p = &idade;

**Versão 2.** Qual linha tem de vir antes de *q = 7; ?

Já está escrito:

```c
int nota;
int *q;
```

Opções: `nota = 7;`  `q = &nota;`  `*q = 0;`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `nota = 7;` → nota = 7; escreve em nota, mas q continua sem endereço. O que falta antes do *q é q = &nota;
- respondeu `*q = 0;` → *q = 0; já usa o lugar apontado, e q ainda não aponta para um lugar escolhido. Antes vem q = &nota;
- qualquer outro erro → Antes de usar *q, o ponteiro recebe um endereço: q = &nota;

### Degrau 3 — guiado, digitar

> Com o endereço dado antes, *p é seguro: é o lugar de nota.

**Versão 1.** Que número este trecho mostra na tela?

```c
int nota;
int *p;

nota = 0;
p = &nota;
*p = 9;
printf("%d\n", nota);
```

Resposta certa: `9`

Se errar:

- digitou `0` → p recebeu o endereço de nota antes do uso. *p = 9; escreveu em nota, por cima do 0.
- qualquer outro erro → p aponta para nota desde a linha p = &nota;. *p = 9; escreveu nela: o trecho mostra 9.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *q;

idade = 15;
q = &idade;
*q = 16;
printf("%d\n", idade);
```

Resposta certa: `16`

Se errar:

- digitou `15` → q recebeu o endereço de idade antes do uso. *q = 16; escreveu em idade, por cima do 15.
- qualquer outro erro → q aponta para idade desde a linha q = &idade;. *q = 16; escreveu nela: o trecho mostra 16.

### Degrau 4 — prática, montar

_Nome do passo, no fechamento: Dar o endereço ao ponteiro antes de usar *p_

**Versão 1.** Ponha as quatro linhas numa ordem em que *q não é usado cedo demais.

Peças: `int nota;`  `int *q;`  `*q = 7;`  `q = &nota;`

Resposta certa: `int nota; int *q; q = &nota; *q = 7;`

Se errar:

- respondeu `int nota; int *q; *q = 7; q = &nota;` → Nessa ordem *q = 7; roda antes de q receber o endereço, e vai a um lugar que ninguém escolheu. Troque as duas últimas.
- respondeu `int *q; int nota; *q = 7; q = &nota;` → Nessa ordem *q = 7; roda antes de q receber o endereço, e vai a um lugar que ninguém escolheu. Troque as duas últimas.
- qualquer outro erro → As declarações primeiro; depois q = &nota; e só então *q = 7;

**Versão 2.** Ponha as quatro linhas numa ordem em que *p não é usado cedo demais.

Peças: `int idade;`  `int *p;`  `*p = 20;`  `p = &idade;`

Resposta certa: `int idade; int *p; p = &idade; *p = 20;`

Se errar:

- respondeu `int idade; int *p; *p = 20; p = &idade;` → Nessa ordem *p = 20; roda antes de p receber o endereço, e vai a um lugar que ninguém escolheu. Troque as duas últimas.
- respondeu `int *p; int idade; *p = 20; p = &idade;` → Nessa ordem *p = 20; roda antes de p receber o endereço, e vai a um lugar que ninguém escolheu. Troque as duas últimas.
- qualquer outro erro → As declarações primeiro; depois p = &idade; e só então *p = 20;

### Degrau 5 — prática, escolher

**Versão 1.** Uma das três últimas linhas usa um ponteiro cedo demais. Qual?

Já está escrito:

```c
int idade;
int *p;
int *q;

p = &idade;
*p = 10;
*q = 20;
```

Opções: `*q = 20; — q não recebeu endereço`  `*p = 10; — idade não tinha valor`  `p = &idade; — idade não tinha valor`

Resposta certa: `*q = 20; — q não recebeu endereço`

Se errar:

- respondeu `*p = 10; — idade não tinha valor` → p recebeu o endereço de idade na linha anterior: *p = 10; escreve num lugar escolhido. A que usa cedo demais é *q = 20;
- respondeu `p = &idade; — idade não tinha valor` → O lugar de idade existe desde a declaração, com valor ou sem, e tem endereço. A que usa cedo demais é *q = 20;
- qualquer outro erro → q foi declarado e não recebeu endereço: *q = 20; iria a um lugar que ninguém escolheu.

**Versão 2.** Uma das três últimas linhas usa um ponteiro cedo demais. Qual?

Já está escrito:

```c
int nota;
int *p;
int *q;

*p = 4;
q = &nota;
*q = 7;
```

Opções: `*p = 4; — p não recebeu endereço`  `*q = 7; — nota não tinha valor`  `q = &nota; — nota não tinha valor`

Resposta certa: `*p = 4; — p não recebeu endereço`

Se errar:

- respondeu `*q = 7; — nota não tinha valor` → q recebeu o endereço de nota na linha anterior: *q = 7; escreve num lugar escolhido. A que usa cedo demais é *p = 4;
- respondeu `q = &nota; — nota não tinha valor` → O lugar de nota existe desde a declaração, com valor ou sem, e tem endereço. A que usa cedo demais é *p = 4;
- qualquer outro erro → p foi declarado e não recebeu endereço: *p = 4; iria a um lugar que ninguém escolheu.

### Se errar a pergunta do topo: a revisão

> Um ponteiro recém-declarado guarda um valor que ninguém escolheu.
> Usar *p nesse momento é ir a um lugar que ninguém escolheu. Primeiro p recebe um endereço; só depois vem o *p.

```c
int nota;
int *p;

p = &nota;
*p = 7;
printf("%d\n", nota);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Depois de int *p; já dá para escrever em *p.

```c
int *p;

*p = 10;
```

**O compilador reclama da última linha?**

- Não: depois de int *p; já dá para escrever em *p _(é o que a crença espera)_
- Sim: p ainda não recebeu endereço nenhum _(é o que a máquina faz)_

O compilador reclama:

```
'p' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o lugar onde o 10 cairia, ninguém escolheu._

O que isto mostra: O compilador avisa que p é usado sem ter recebido valor. *p vai ao lugar cujo endereço está em p — e em p, por enquanto, há um número que ninguém escolheu.
