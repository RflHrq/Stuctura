# A escada do kc_07 — Ponteiro e array

Texto para leitura, gerado de `mvp/dominio/escada_kc07.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — int a[5] cria cinco caixas de inteiro grudadas uma na outra. O nome a vale para o conjunto inteiro, não para uma caixa só.

### Degrau 1 — guiado, escolher

> int notas[3]; cria três caixas de int, grudadas uma na outra. Cada caixa é uma variável.
> O nome notas vale para o conjunto das três, e não para uma caixa só.

**Versão 1.** O que esta linha cria?

Já está escrito:

```c
int notas[3];
```

Opções: `Três caixas de int, lado a lado`  `Uma caixa só, com os três valores dentro`  `Um ponteiro, que depois aponta para três valores`

Resposta certa: `Três caixas de int, lado a lado`

Se errar:

- respondeu `Uma caixa só, com os três valores dentro` → Não é uma caixa com três valores: são três caixas, cada uma com o seu lugar e o seu valor. notas é o nome do conjunto. _(aponta a crença `array_confused_with_cell`)_
- respondeu `Um ponteiro, que depois aponta para três valores` → Ponteiro nenhum nasce aqui. A linha cria as três caixas de int, e notas é o nome do conjunto delas.
- qualquer outro erro → A linha cria três caixas de int, lado a lado. notas é o nome do conjunto.

**Versão 2.** O que esta linha cria?

Já está escrito:

```c
int idades[5];
```

Opções: `Cinco caixas de int, lado a lado`  `Uma caixa só, com os cinco valores dentro`  `Um ponteiro, que depois aponta para cinco valores`

Resposta certa: `Cinco caixas de int, lado a lado`

Se errar:

- respondeu `Uma caixa só, com os cinco valores dentro` → Não é uma caixa com cinco valores: são cinco caixas, cada uma com o seu lugar e o seu valor. idades é o nome do conjunto. _(aponta a crença `array_confused_with_cell`)_
- respondeu `Um ponteiro, que depois aponta para cinco valores` → Ponteiro nenhum nasce aqui. A linha cria as cinco caixas de int, e idades é o nome do conjunto delas.
- qualquer outro erro → A linha cria cinco caixas de int, lado a lado. idades é o nome do conjunto.

### Degrau 2 — guiado, digitar

> int notas[3] = {10, 20, 30}; cria as três caixas já com um valor em cada uma.
> Cada caixa, ou item, tem um número, e a contagem começa em 0: notas[0] é a primeira.

**Versão 1.** Que número este trecho mostra na tela?

```c
int notas[3] = {10, 20, 30};

notas[0] = 7;
printf("%d\n", notas[1]);
```

Resposta certa: `20`

Se errar:

- digitou `7` → A contagem começa em 0: o 7 foi para notas[0], a primeira caixa. notas[1] é a segunda, e continua com 20.
- digitou `10` → notas[1] é a segunda caixa, e não a primeira: a contagem começa em 0. Ela guarda 20.
- qualquer outro erro → notas[0] é a primeira caixa e notas[1] a segunda. A segunda guarda 20.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idades[3] = {15, 16, 17};

idades[0] = 9;
printf("%d\n", idades[1]);
```

Resposta certa: `16`

Se errar:

- digitou `9` → A contagem começa em 0: o 9 foi para idades[0], a primeira caixa. idades[1] é a segunda, e continua com 16.
- digitou `15` → idades[1] é a segunda caixa, e não a primeira: a contagem começa em 0. Ela guarda 16.
- qualquer outro erro → idades[0] é a primeira caixa e idades[1] a segunda. A segunda guarda 16.

### Degrau 3 — guiado, digitar

> sizeof diz quanto espaço uma variável ocupa, contado em caixas de char.
> No printf, o formato desse número é %zu.

**Versão 1.** v tem cinco caixas de char. Que número aparece?

```c
char v[5];

printf("%zu\n", sizeof v);
```

Resposta certa: `5`

Se errar:

- digitou `1` → sizeof v não mede uma caixa: mede v inteiro, que é o conjunto das cinco. Aparece 5.
- qualquer outro erro → v é o conjunto das cinco caixas de char, e sizeof v mede o conjunto: 5.

**Versão 2.** letras tem oito caixas de char. Que número aparece?

```c
char letras[8];

printf("%zu\n", sizeof letras);
```

Resposta certa: `8`

Se errar:

- digitou `1` → sizeof letras não mede uma caixa: mede letras inteiro, que é o conjunto das oito. Aparece 8.
- qualquer outro erro → letras é o conjunto das oito caixas de char, e sizeof letras mede o conjunto: 8.

### Degrau 4 — guiado, escolher

> char nome[] = "ana"; cria quatro caixas de char: a, n, a e uma marca de fim, o terminador.
> char *p = "ana"; cria só a caixa de p, com o endereço de letras guardadas em outro lugar.

**Versão 1.** As duas linhas guardam as letras do mesmo jeito?

Já está escrito:

```c
char nome[] = "ana";
char *p = "ana";
```

Opções: `Não: nome tem as quatro caixas, e p só um endereço`  `Sim: char nome[] e char *p guardam as letras do mesmo jeito`  `Não: p tem as quatro caixas, e nome só um endereço`

Resposta certa: `Não: nome tem as quatro caixas, e p só um endereço`

Se errar:

- respondeu `Sim: char nome[] e char *p guardam as letras do mesmo jeito` → A escrita é parecida, mas o que nasce é diferente: nome é o conjunto das quatro caixas, com as letras dentro; p é uma caixa só, que guarda um endereço. _(aponta a crença `string_literal_is_array`)_
- respondeu `Não: p tem as quatro caixas, e nome só um endereço` → É o contrário: quem tem as caixas com as letras é nome. p é um ponteiro: uma caixa só, com o endereço das letras.
- qualquer outro erro → nome é o conjunto das quatro caixas, com as letras dentro. p é uma caixa só, com um endereço.

**Versão 2.** As duas linhas guardam as letras do mesmo jeito?

Já está escrito:

```c
char *q = "ufv";
char sigla[] = "ufv";
```

Opções: `Sim: char *q e char sigla[] guardam as letras do mesmo jeito`  `Não: sigla tem as quatro caixas, e q só um endereço`  `Não: q tem as quatro caixas, e sigla só um endereço`

Resposta certa: `Não: sigla tem as quatro caixas, e q só um endereço`

Se errar:

- respondeu `Sim: char *q e char sigla[] guardam as letras do mesmo jeito` → A escrita é parecida, mas o que nasce é diferente: sigla é o conjunto das quatro caixas, com as letras dentro; q é uma caixa só, que guarda um endereço. _(aponta a crença `string_literal_is_array`)_
- respondeu `Não: q tem as quatro caixas, e sigla só um endereço` → É o contrário: quem tem as caixas com as letras é sigla. q é um ponteiro: uma caixa só, com o endereço das letras.
- qualquer outro erro → sigla é o conjunto das quatro caixas, com as letras dentro. q é uma caixa só, com um endereço.

### Degrau 5 — prática, digitar

_Nome do passo, no fechamento: Mexer numa caixa não mexe nas outras_

**Versão 1.** O trecho zera uma das caixas e depois soma as três. Que número aparece?

```c
int notas[3] = {7, 8, 9};

notas[1] = 0;
printf("%d\n", notas[0] + notas[1] + notas[2]);
```

Resposta certa: `16`

Se errar:

- digitou `0` → O 0 foi para uma caixa só, notas[1]. As outras duas continuam com 7 e 9, e a soma dá 16.
- digitou `24` → notas[1] deixou de valer 8: recebeu 0 na linha de cima. A soma é 7 mais 0 mais 9: 16.
- qualquer outro erro → Só notas[1] mudou. A soma é 7 mais 0 mais 9: 16.

**Versão 2.** O trecho zera uma das caixas e depois soma as três. Que número aparece?

```c
int idades[3] = {15, 16, 17};

idades[0] = 0;
printf("%d\n", idades[0] + idades[1] + idades[2]);
```

Resposta certa: `33`

Se errar:

- digitou `0` → O 0 foi para uma caixa só, idades[0]. As outras duas continuam com 16 e 17, e a soma dá 33.
- digitou `48` → idades[0] deixou de valer 15: recebeu 0 na linha de cima. A soma é 0 mais 16 mais 17: 33.
- qualquer outro erro → Só idades[0] mudou. A soma é 0 mais 16 mais 17: 33.

### Degrau 6 — prática, escolher

**Versão 1.** Quantas caixas de char esta linha cria?

Já está escrito:

```c
char nome[] = "sol";
```

Opções: `Quatro: as três letras e a marca de fim`  `Três: uma para cada letra`  `Uma: a de nome, com as letras dentro`

Resposta certa: `Quatro: as três letras e a marca de fim`

Se errar:

- respondeu `Três: uma para cada letra` → As letras são três, mas o texto entre aspas ganha uma caixa a mais, a da marca de fim. São quatro.
- respondeu `Uma: a de nome, com as letras dentro` → Um array não é uma caixa com tudo dentro: cada letra tem a sua caixa, e a marca de fim também. São quatro.
- qualquer outro erro → Uma caixa para cada letra, e mais a da marca de fim: quatro.

**Versão 2.** Quantas caixas de char esta linha cria?

Já está escrito:

```c
char cidade[] = "minas";
```

Opções: `Cinco: uma para cada letra`  `Seis: as cinco letras e a marca de fim`  `Uma: a de cidade, com as letras dentro`

Resposta certa: `Seis: as cinco letras e a marca de fim`

Se errar:

- respondeu `Cinco: uma para cada letra` → As letras são cinco, mas o texto entre aspas ganha uma caixa a mais, a da marca de fim. São seis.
- respondeu `Uma: a de cidade, com as letras dentro` → Um array não é uma caixa com tudo dentro: cada letra tem a sua caixa, e a marca de fim também. São seis.
- qualquer outro erro → Uma caixa para cada letra, e mais a da marca de fim: seis.

### Se errar a pergunta do topo: a revisão

> int notas[3]; cria três caixas de int, grudadas uma na outra.
> O nome notas vale para o conjunto. Cada caixa se alcança pelo número: notas[0], notas[1], notas[2].

```c
int notas[3] = {7, 8, 9};

printf("%d\n", notas[2]);
```

A máquina imprime:

```
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> Uma variável guarda vários valores de uma vez: int a[5] é uma caixa com os cinco dentro, e int *p guarda do mesmo jeito.

```c
int notas[3] = {7, 8, 9};

printf("%p\n", (void *)&notas[0]);
printf("%p\n", (void *)&notas[1]);
```

**Os dois printf mostram o endereço de notas[0] e o de notas[1]. O que aparece?**

- O mesmo endereço: os valores ficam todos numa caixa só _(é o que a crença espera)_
- Dois endereços diferentes _(é o que a máquina faz)_

A máquina imprime:

```
0x1000
0x1004
```

_Os números dos lugares mudam de máquina para máquina; aqui eles aparecem como números de exemplo. O que foi conferido é que as duas linhas saem com endereços diferentes._

O que isto mostra: Saíram dois endereços diferentes. Cada valor do array tem a sua caixa, com o seu lugar: são três caixas, lado a lado, e não uma caixa com três valores dentro.

### Se a pessoa disser a crença: a prova

Você disse:

> char *s = "abc" e char s[] = "abc" guardam do mesmo jeito.

```c
char nome[] = "maria";
char *p = "maria";

printf("%zu\n", sizeof nome);
printf("%zu\n", sizeof p);
```

**sizeof diz quanto espaço cada variável ocupa, contado em caixas de char. O que os dois printf mostram?**

- Dois números diferentes _(é o que a máquina faz)_
- O mesmo número: as duas guardam as letras do mesmo jeito _(é o que a crença espera)_

A máquina imprime:

```
6
8
```

_O 8 é o tamanho de um ponteiro nesta máquina; em outra pode ser 4. O 6 não muda: são as cinco letras e a marca de fim._

O que isto mostra: Saíram 6 e 8. nome é o conjunto das seis caixas, com as letras dentro. p é uma caixa só, do tamanho de um endereço: as letras dele estão guardadas em outro lugar.

## B2 — int *p cria uma caixa só: a de p. Nenhuma caixa de inteiro nasce junto.

### Degrau 1 — guiado, escolher

> int notas[3]; cria três caixas de int. int *p; cria uma caixa só: a de p.
> Com o ponteiro não nasce caixa de int nenhuma.

**Versão 1.** Depois destas duas linhas, quantas caixas de int existem?

Já está escrito:

```c
int notas[3];
int *p;
```

Opções: `Três: as de notas`  `Quatro: as três de notas, e uma que nasceu para p apontar`  `Seis: p também ganha três`

Resposta certa: `Três: as de notas`

Se errar:

- respondeu `Quatro: as três de notas, e uma que nasceu para p apontar` → int *p; cria só a caixa do ponteiro, que guarda um endereço. Caixa de int para ele apontar não nasce: são só as três de notas. _(aponta a crença `declaration_allocates`)_
- respondeu `Seis: p também ganha três` → p não é um array: é uma caixa só, a do ponteiro. Caixas de int, só as três de notas.
- qualquer outro erro → As caixas de int são as três de notas. Com p nasce só a caixa do ponteiro.

**Versão 2.** Depois destas duas linhas, quantas caixas de int existem?

Já está escrito:

```c
int *q;
int idades[5];
```

Opções: `Seis: as cinco de idades, e uma que nasceu para q apontar`  `Cinco: as de idades`  `Dez: q também ganha cinco`

Resposta certa: `Cinco: as de idades`

Se errar:

- respondeu `Seis: as cinco de idades, e uma que nasceu para q apontar` → int *q; cria só a caixa do ponteiro, que guarda um endereço. Caixa de int para ele apontar não nasce: são só as cinco de idades. _(aponta a crença `declaration_allocates`)_
- respondeu `Dez: q também ganha cinco` → q não é um array: é uma caixa só, a do ponteiro. Caixas de int, só as cinco de idades.
- qualquer outro erro → As caixas de int são as cinco de idades. Com q nasce só a caixa do ponteiro.

### Degrau 2 — guiado, digitar

> Para servir, o ponteiro recebe o endereço de uma caixa que já existe: p = &notas[0];
> Daí *p chega nela.

**Versão 1.** Que número este trecho mostra na tela?

```c
int notas[3] = {7, 8, 9};
int *p;

p = &notas[0];
printf("%d\n", *p);
```

Resposta certa: `7`

Se errar:

- digitou `0` → p não ficou vazio: recebeu o endereço de notas[0], a primeira caixa. *p chega nela, e acha 7.
- digitou `8` → A contagem começa em 0: notas[0] é a primeira caixa, a do 7. É o endereço dela que p recebeu.
- qualquer outro erro → p recebeu o endereço da primeira caixa de notas, e *p chega nela: 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idades[3] = {15, 16, 17};
int *q;

q = &idades[0];
printf("%d\n", *q);
```

Resposta certa: `15`

Se errar:

- digitou `0` → q não ficou vazio: recebeu o endereço de idades[0], a primeira caixa. *q chega nela, e acha 15.
- digitou `16` → A contagem começa em 0: idades[0] é a primeira caixa, a do 15. É o endereço dela que q recebeu.
- qualquer outro erro → q recebeu o endereço da primeira caixa de idades, e *q chega nela: 15.

### Degrau 3 — guiado, digitar

> No ponteiro também se escreve o índice: p[0] é a caixa apontada, e p[1] a seguinte.

**Versão 1.** Que número este trecho mostra na tela?

```c
int notas[3] = {7, 8, 9};
int *p;

p = &notas[0];
printf("%d\n", p[1]);
```

Resposta certa: `8`

Se errar:

- digitou `7` → p[0] é a caixa que p aponta, a do 7. p[1] é a seguinte: 8.
- qualquer outro erro → p aponta para a primeira caixa de notas. p[1] é a caixa seguinte: 8.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idades[3] = {15, 16, 17};
int *q;

q = &idades[0];
printf("%d\n", q[1]);
```

Resposta certa: `16`

Se errar:

- digitou `15` → q[0] é a caixa que q aponta, a do 15. q[1] é a seguinte: 16.
- qualquer outro erro → q aponta para a primeira caixa de idades. q[1] é a caixa seguinte: 16.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O ponteiro não tem caixas: usa as do array_

**Versão 1.** O trecho escreve 0 por p, e depois mostra uma caixa de notas. Que número aparece?

```c
int notas[3] = {7, 8, 9};
int *p;

p = &notas[0];
p[2] = 0;
printf("%d\n", notas[2]);
```

Resposta certa: `0`

Se errar:

- digitou `9` → p não tem caixas próprias: p[2] é a terceira caixa de notas. O 0 foi escrito nela.
- qualquer outro erro → p[2] e notas[2] são a mesma caixa: p só guarda o endereço. Aparece 0.

**Versão 2.** O trecho escreve 0 por q, e depois mostra uma caixa de idades. Que número aparece?

```c
int idades[3] = {15, 16, 17};
int *q;

q = &idades[0];
q[1] = 0;
printf("%d\n", idades[1]);
```

Resposta certa: `0`

Se errar:

- digitou `16` → q não tem caixas próprias: q[1] é a segunda caixa de idades. O 0 foi escrito nela.
- qualquer outro erro → q[1] e idades[1] são a mesma caixa: q só guarda o endereço. Aparece 0.

### Degrau 5 — prática, escolher

**Versão 1.** A última linha escreve numa caixa que existe?

Já está escrito:

```c
int *p;

p[0] = 7;
```

Opções: `Não: p ainda não recebeu endereço nenhum`  `Sim: a caixa de int nasceu junto com p`  `Sim: p[0] é a própria caixa de p`

Resposta certa: `Não: p ainda não recebeu endereço nenhum`

Se errar:

- respondeu `Sim: a caixa de int nasceu junto com p` → Com int *p; nasce só a caixa do ponteiro. Caixa de int para p[0] escrever não existe, enquanto p não receber o endereço de uma.
- respondeu `Sim: p[0] é a própria caixa de p` → p[0] não é a caixa de p: é a caixa que p APONTA. E p ainda não aponta para nenhuma.
- qualquer outro erro → p foi declarado e mais nada: ainda não aponta para caixa nenhuma.

**Versão 2.** A última linha escreve numa caixa que existe?

Já está escrito:

```c
int *q;

q[1] = 3;
```

Opções: `Sim: as caixas de int nasceram junto com q`  `Sim: q[1] é a própria caixa de q`  `Não: q ainda não recebeu endereço nenhum`

Resposta certa: `Não: q ainda não recebeu endereço nenhum`

Se errar:

- respondeu `Sim: as caixas de int nasceram junto com q` → Com int *q; nasce só a caixa do ponteiro. Caixa de int para q[1] escrever não existe, enquanto q não receber o endereço de uma.
- respondeu `Sim: q[1] é a própria caixa de q` → q[1] não é a caixa de q: é a caixa seguinte à que q APONTA. E q ainda não aponta para nenhuma.
- qualquer outro erro → q foi declarado e mais nada: ainda não aponta para caixa nenhuma.

### Se errar a pergunta do topo: a revisão

> int *p; cria uma caixa só, a de p. Caixa de int, nenhuma.
> Para usar p[0], p recebe antes o endereço de caixas que existem: p = &notas[0];

```c
int notas[3] = {7, 8, 9};
int *p;

p = &notas[0];
printf("%d\n", p[0]);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> int *p já cria o dado apontado automaticamente.

```c
int notas[3];
int *p;

notas[0] = 1;
p[0] = 1;
```

**As duas últimas linhas escrevem 1: uma em notas[0], a outra em p[0]. De qual delas o compilador reclama?**

- De nenhuma: int *p; já criou a caixa em que p[0] escreve _(é o que a crença espera)_
- Da última: p não aponta para caixa nenhuma _(é o que a máquina faz)_

O compilador reclama:

```
'p' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: onde esse 1 iria parar, ninguém sabe._

O que isto mostra: O compilador reclama da última linha: p é usado sem ter recebido endereço ("used uninitialized"). int *p; criou a caixa do ponteiro, e mais nenhuma — não há caixa de int para p[0] escrever.

## B3 — Quando você usa a numa conta, C troca a pelo endereço da primeira caixa. O que viaja é esse endereço, e não o conjunto.

### Degrau 1 — guiado, digitar

> Usado numa conta — numa expressão —, o nome do array vira o endereço da primeira caixa.
> Por isso p = notas; faz o mesmo que p = &notas[0];

**Versão 1.** Que número este trecho mostra na tela?

```c
int notas[3] = {7, 8, 9};
int *p;

p = notas;
printf("%d\n", *p);
```

Resposta certa: `7`

Se errar:

- digitou `9` → notas, usado ali, vira o endereço da PRIMEIRA caixa, e não da última. *p chega nela: 7.
- digitou `3` → 3 é o número de caixas. O que p recebe é o endereço da primeira, e *p acha o valor dela: 7.
- qualquer outro erro → notas virou o endereço da primeira caixa, p o recebeu, e *p chega nela: 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idades[3] = {15, 16, 17};
int *q;

q = idades;
printf("%d\n", *q);
```

Resposta certa: `15`

Se errar:

- digitou `17` → idades, usado ali, vira o endereço da PRIMEIRA caixa, e não da última. *q chega nela: 15.
- digitou `3` → 3 é o número de caixas. O que q recebe é o endereço da primeira, e *q acha o valor dela: 15.
- qualquer outro erro → idades virou o endereço da primeira caixa, q o recebeu, e *q chega nela: 15.

### Degrau 2 — guiado, digitar

> A troca acontece em toda conta em que o nome aparece.
> Em *notas, notas vira o endereço da primeira caixa, e o * chega nela.

**Versão 1.** Que número este trecho mostra na tela?

```c
int notas[3] = {7, 8, 9};

*notas = 5;
printf("%d\n", notas[0]);
```

Resposta certa: `5`

Se errar:

- digitou `7` → *notas é a primeira caixa: notas virou o endereço dela, e o * chegou lá. O 5 foi escrito em notas[0].
- qualquer outro erro → *notas e notas[0] são a mesma caixa. Ela recebeu 5.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idades[3] = {15, 16, 17};

*idades = 20;
printf("%d\n", idades[0]);
```

Resposta certa: `20`

Se errar:

- digitou `15` → *idades é a primeira caixa: idades virou o endereço dela, e o * chegou lá. O 20 foi escrito em idades[0].
- qualquer outro erro → *idades e idades[0] são a mesma caixa. Ela recebeu 20.

### Degrau 3 — guiado, escolher

> Na chamada zera(notas); acontece a mesma troca: o que é copiado para o parâmetro é o endereço da primeira caixa.
> O parâmetro int v[] é um ponteiro, como int *v.

**Versão 1.** Na última linha, o que a função recebe?

Já está escrito:

```c
void zera(int v[]) { v[0] = 0; }

int notas[3] = {7, 8, 9};

zera(notas);
```

Opções: `Uma cópia do endereço da primeira caixa`  `O array inteiro, por referência: com array o C não copia`  `Uma cópia das três caixas`

Resposta certa: `Uma cópia do endereço da primeira caixa`

Se errar:

- respondeu `O array inteiro, por referência: com array o C não copia` → Com array o C faz o de sempre: copia um valor para o parâmetro. O valor é o endereço da primeira caixa, porque notas, usado na chamada, virou esse endereço. _(aponta a crença `array_passed_by_reference`)_
- respondeu `Uma cópia das três caixas` → As caixas não são copiadas: notas, usado na chamada, vira o endereço da primeira, e é esse endereço que é copiado.
- qualquer outro erro → A função recebe uma cópia do endereço da primeira caixa de notas.

**Versão 2.** Na última linha, o que a função recebe?

Já está escrito:

```c
void marca(int v[]) { v[0] = 1; }

int idades[3] = {15, 16, 17};

marca(idades);
```

Opções: `O array inteiro, por referência: com array o C não copia`  `Uma cópia das três caixas`  `Uma cópia do endereço da primeira caixa`

Resposta certa: `Uma cópia do endereço da primeira caixa`

Se errar:

- respondeu `O array inteiro, por referência: com array o C não copia` → Com array o C faz o de sempre: copia um valor para o parâmetro. O valor é o endereço da primeira caixa, porque idades, usado na chamada, virou esse endereço. _(aponta a crença `array_passed_by_reference`)_
- respondeu `Uma cópia das três caixas` → As caixas não são copiadas: idades, usado na chamada, vira o endereço da primeira, e é esse endereço que é copiado.
- qualquer outro erro → A função recebe uma cópia do endereço da primeira caixa de idades.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A função escreve nas caixas de quem chamou_

**Versão 1.** Que número este trecho mostra na tela?

```c
void marca(int v[]) { v[1] = 0; }

int notas[3] = {7, 8, 9};

marca(notas);
printf("%d\n", notas[1]);
```

Resposta certa: `0`

Se errar:

- digitou `8` → A função recebeu o endereço da primeira caixa de notas. v[1] é a segunda caixa DELA, de notas: o 0 foi escrito ali.
- qualquer outro erro → v guarda o endereço das caixas de notas. v[1] é notas[1], que recebeu 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
void marca(int v[]) { v[2] = 1; }

int idades[3] = {15, 16, 17};

marca(idades);
printf("%d\n", idades[2]);
```

Resposta certa: `1`

Se errar:

- digitou `17` → A função recebeu o endereço da primeira caixa de idades. v[2] é a terceira caixa DELA, de idades: o 1 foi escrito ali.
- qualquer outro erro → v guarda o endereço das caixas de idades. v[2] é idades[2], que recebeu 1.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas faz o mesmo que p = notas;?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int *p;
```

Opções: `p = &notas[0];`  `p = notas[0];`  `p = &notas[1];`

Resposta certa: `p = &notas[0];`

Se errar:

- respondeu `p = notas[0];` → notas[0] é o valor da primeira caixa, o 7, e não o endereço dela: o compilador reclama. O endereço é &notas[0].
- respondeu `p = &notas[1];` → &notas[1] é o endereço da segunda caixa. notas, sozinho numa conta, vira o endereço da primeira: &notas[0].
- qualquer outro erro → notas, numa conta, vira o endereço da primeira caixa: p = &notas[0];

**Versão 2.** Qual destas linhas faz o mesmo que q = idades;?

Já está escrito:

```c
int idades[3] = {15, 16, 17};
int *q;
```

Opções: `q = idades[0];`  `q = &idades[2];`  `q = &idades[0];`

Resposta certa: `q = &idades[0];`

Se errar:

- respondeu `q = idades[0];` → idades[0] é o valor da primeira caixa, o 15, e não o endereço dela: o compilador reclama. O endereço é &idades[0].
- respondeu `q = &idades[2];` → &idades[2] é o endereço da terceira caixa. idades, sozinho numa conta, vira o endereço da primeira: &idades[0].
- qualquer outro erro → idades, numa conta, vira o endereço da primeira caixa: q = &idades[0];

### Se errar a pergunta do topo: a revisão

> Usado numa conta, o nome do array vira o endereço da primeira caixa: p = notas; é p = &notas[0];
> Na chamada é igual: zera(notas); copia esse endereço para o parâmetro. O array não viaja.

```c
void zera(int v[]) { v[0] = 0; }

int notas[3] = {7, 8, 9};

zera(notas);
printf("%d\n", notas[0]);
```

A máquina imprime:

```
0
```

### Se a pessoa disser a crença: a prova

Você disse:

> Arrays são passados por referência, diferente do resto de C.

```c
void solta(int v[]) { v = NULL; }

int notas[3] = {7, 8, 9};

solta(notas);
printf("%d\n", notas[0]);
```

**Dentro da função, v recebe NULL. Depois da chamada, o trecho mostra notas[0]. O que aparece?**

- 7 _(é o que a máquina faz)_
- Não dá para saber: v é o próprio notas, e ele foi apagado _(é o que a crença espera)_

A máquina imprime:

```
7
```

O que isto mostra: Saiu 7. Se o array viajasse por referência, v seria o próprio notas, e apagar v mexeria nele. O que viajou foi uma cópia do endereço da primeira caixa — a mesma regra do resto de C —, e a função só apagou a cópia.

## B4 — Essa troca acontece quase em todo lugar. Em dois ela não acontece: sizeof(a) mede as caixas, e &a dá o endereço do conjunto.

### Degrau 1 — guiado, escolher

> Em sizeof v, o nome não vira endereço: ali v é o conjunto inteiro.
> É por isso que sizeof v mede as dez caixas, e não um ponteiro.

**Versão 1.** Em qual destes lugares v continua sendo o conjunto das dez caixas?

Já está escrito:

```c
char v[10];
char *p;
```

Opções: `Em sizeof v`  `Em p = v;`  `Em *v`

Resposta certa: `Em sizeof v`

Se errar:

- respondeu `Em p = v;` → Em p = v; o nome vira o endereço da primeira caixa, e é esse endereço que p recebe. Quem fica com o conjunto inteiro é sizeof v.
- respondeu `Em *v` → Em *v o nome vira o endereço da primeira caixa, e o * chega nela. Quem fica com o conjunto inteiro é sizeof v.
- qualquer outro erro → Em sizeof v o nome não vira endereço: é o conjunto das dez caixas.

**Versão 2.** Em qual destes lugares letras continua sendo o conjunto das oito caixas?

Já está escrito:

```c
char letras[8];
char *q;
```

Opções: `Em q = letras;`  `Em *letras`  `Em sizeof letras`

Resposta certa: `Em sizeof letras`

Se errar:

- respondeu `Em q = letras;` → Em q = letras; o nome vira o endereço da primeira caixa, e é esse endereço que q recebe. Quem fica com o conjunto inteiro é sizeof letras.
- respondeu `Em *letras` → Em *letras o nome vira o endereço da primeira caixa, e o * chega nela. Quem fica com o conjunto inteiro é sizeof letras.
- qualquer outro erro → Em sizeof letras o nome não vira endereço: é o conjunto das oito caixas.

### Degrau 2 — guiado, escolher

> O outro lugar é o &: &v é o endereço do conjunto inteiro, e não o de uma caixa.
> v e &v marcam o mesmo ponto da memória, mas têm tipos diferentes: um aponta uma caixa, o outro o conjunto.

**Versão 1.** v e &v são a mesma coisa?

Já está escrito:

```c
char v[10];
```

Opções: `Não: v vira o endereço de uma caixa; &v é o do conjunto`  `São: v e &v são a mesma coisa`  `Não: &v é o valor da primeira caixa`

Resposta certa: `Não: v vira o endereço de uma caixa; &v é o do conjunto`

Se errar:

- respondeu `São: v e &v são a mesma coisa` → Marcam o mesmo ponto, e por isso parecem iguais. Mas v, numa conta, é o endereço de UMA caixa de char; &v é o endereço do conjunto das dez. São endereços de coisas diferentes. _(aponta a crença `arr_equals_addr_of_arr`)_
- respondeu `Não: &v é o valor da primeira caixa` → O & nunca dá o valor de uma caixa: dá um endereço. &v é o endereço do conjunto inteiro.
- qualquer outro erro → v vira o endereço de uma caixa; &v é o endereço do conjunto das dez.

**Versão 2.** letras e &letras são a mesma coisa?

Já está escrito:

```c
char letras[8];
```

Opções: `São: letras e &letras são a mesma coisa`  `Não: &letras é o valor da primeira caixa`  `Não: letras vira o endereço de uma caixa; &letras é o do conjunto`

Resposta certa: `Não: letras vira o endereço de uma caixa; &letras é o do conjunto`

Se errar:

- respondeu `São: letras e &letras são a mesma coisa` → Marcam o mesmo ponto, e por isso parecem iguais. Mas letras, numa conta, é o endereço de UMA caixa de char; &letras é o endereço do conjunto das oito. São endereços de coisas diferentes. _(aponta a crença `arr_equals_addr_of_arr`)_
- respondeu `Não: &letras é o valor da primeira caixa` → O & nunca dá o valor de uma caixa: dá um endereço. &letras é o endereço do conjunto inteiro.
- qualquer outro erro → letras vira o endereço de uma caixa; &letras é o endereço do conjunto das oito.

### Degrau 3 — guiado, escolher

> Como são endereços de tipos diferentes, o compilador não aceita um no lugar do outro.

**Versão 1.** p aponta para um char. Qual destas linhas o compilador aceita?

Já está escrito:

```c
char v[10];
char *p;
```

Opções: `p = v;`  `p = &v;`  `p = *v;`

Resposta certa: `p = v;`

Se errar:

- respondeu `p = &v;` → &v é o endereço do conjunto inteiro, e p aponta para UM char: o compilador reclama. v, sozinho, vira o endereço da primeira caixa: p = v;
- respondeu `p = *v;` → *v é o valor da primeira caixa, uma letra, e não um endereço: o compilador reclama. O endereço da primeira caixa é o que v vira sozinho: p = v;
- qualquer outro erro → v, sozinho, vira o endereço de uma caixa de char, que é o que p guarda: p = v;

**Versão 2.** q aponta para um char. Qual destas linhas o compilador aceita?

Já está escrito:

```c
char letras[8];
char *q;
```

Opções: `q = &letras;`  `q = letras;`  `q = *letras;`

Resposta certa: `q = letras;`

Se errar:

- respondeu `q = &letras;` → &letras é o endereço do conjunto inteiro, e q aponta para UM char: o compilador reclama. letras, sozinho, vira o endereço da primeira caixa: q = letras;
- respondeu `q = *letras;` → *letras é o valor da primeira caixa, uma letra, e não um endereço: o compilador reclama. O endereço da primeira caixa é o que letras vira sozinho: q = letras;
- qualquer outro erro → letras, sozinho, vira o endereço de uma caixa de char, que é o que q guarda: q = letras;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Em sizeof, o nome do array é o conjunto_

**Versão 1.** p recebeu o endereço da primeira caixa de v. Que número aparece?

```c
char v[10];
char *p;

p = v;
printf("%zu\n", sizeof v);
```

Resposta certa: `10`

Se errar:

- digitou `1` → sizeof v não mede uma caixa nem um endereço: em sizeof o nome continua sendo o conjunto. São as dez caixas: 10.
- digitou `8` → 8 seria o tamanho de um ponteiro nesta máquina. Em sizeof v o nome não vira endereço: mede o conjunto das dez caixas, 10.
- qualquer outro erro → Em sizeof v o nome é o conjunto inteiro: dez caixas de char, 10.

**Versão 2.** q recebeu o endereço da primeira caixa de letras. Que número aparece?

```c
char letras[6];
char *q;

q = letras;
printf("%zu\n", sizeof letras);
```

Resposta certa: `6`

Se errar:

- digitou `1` → sizeof letras não mede uma caixa nem um endereço: em sizeof o nome continua sendo o conjunto. São as seis caixas: 6.
- digitou `8` → 8 seria o tamanho de um ponteiro nesta máquina. Em sizeof letras o nome não vira endereço: mede o conjunto das seis caixas, 6.
- qualquer outro erro → Em sizeof letras o nome é o conjunto inteiro: seis caixas de char, 6.

### Degrau 5 — prática, digitar

**Versão 1.** sizeof notas mede o conjunto; sizeof notas[0], uma caixa só. O trecho divide um pelo outro. Que número aparece?

```c
int notas[5];

printf("%zu\n", sizeof notas / sizeof notas[0]);
```

Resposta certa: `5`

Se errar:

- digitou `1` → Daria 1 se sizeof notas medisse uma caixa só. Ele mede o conjunto das cinco: cinco caixas dividido por uma caixa dá 5.
- qualquer outro erro → O conjunto dividido por uma caixa dá o número de caixas: 5.

**Versão 2.** sizeof idades mede o conjunto; sizeof idades[0], uma caixa só. O trecho divide um pelo outro. Que número aparece?

```c
int idades[8];

printf("%zu\n", sizeof idades / sizeof idades[0]);
```

Resposta certa: `8`

Se errar:

- digitou `1` → Daria 1 se sizeof idades medisse uma caixa só. Ele mede o conjunto das oito: oito caixas dividido por uma caixa dá 8.
- qualquer outro erro → O conjunto dividido por uma caixa dá o número de caixas: 8.

### Se errar a pergunta do topo: a revisão

> Em quase toda conta, v vira o endereço da primeira caixa. Em dois lugares, não.
> sizeof v mede o conjunto inteiro, e &v é o endereço do conjunto: outro tipo de endereço.

```c
char v[10];

printf("%zu\n", sizeof v);
```

A máquina imprime:

```
10
```

### Se a pessoa disser a crença: a prova

Você disse:

> arr e &arr são a mesma coisa.

```c
char v[10];
char *p;
char *q;

p = v;
q = &v;
```

**p e q apontam para char. Uma linha entrega v, a outra entrega &v. De qual delas o compilador reclama?**

- Da última: &v não é o mesmo que v _(é o que a máquina faz)_
- De nenhuma: v e &v são a mesma coisa _(é o que a crença espera)_

O compilador reclama:

```
incompatible pointer type
```

_Mensagem do gcc 16.2. Nele a reclamação é um erro; em versões mais antigas, um aviso. Nos dois casos ele reclama da última linha, e só dela._

O que isto mostra: O compilador aceita p = v; e reclama de q = &v;. Se v e &v fossem a mesma coisa, as duas linhas valeriam. v vira o endereço de uma caixa de char; &v é o endereço do conjunto das dez.

## I1 — Dá para trocar o que está dentro de cada caixa. Não dá para trocar o conjunto inteiro por outro.

### Degrau 1 — guiado, completar

> Cada caixa do array é uma variável: recebe valor quando você quiser.

**Versão 1.** Complete para a segunda caixa passar a valer 10.

Já está escrito:

```c
int notas[3] = {7, 8, 9};
```

```c
___ = 10;
```

Peças: `notas[1]`  `notas`  `notas[3]`

Resposta certa: `notas[1] = 10;`

Se errar:

- respondeu `notas = 10;` → notas é o nome do conjunto inteiro, e o conjunto não recebe atribuição: o compilador reclama. A segunda caixa é notas[1].
- respondeu `notas[3] = 10;` → A contagem começa em 0 e vai até 2: notas[3] seria uma quarta caixa, que não existe. A segunda é notas[1].
- qualquer outro erro → A contagem começa em 0: a segunda caixa é notas[1].

**Versão 2.** Complete para a primeira caixa passar a valer 20.

Já está escrito:

```c
int idades[3] = {15, 16, 17};
```

```c
___ = 20;
```

Peças: `idades`  `idades[1]`  `idades[0]`

Resposta certa: `idades[0] = 20;`

Se errar:

- respondeu `idades = 20;` → idades é o nome do conjunto inteiro, e o conjunto não recebe atribuição: o compilador reclama. A primeira caixa é idades[0].
- respondeu `idades[1] = 20;` → A contagem começa em 0: idades[1] é a segunda caixa. A primeira é idades[0].
- qualquer outro erro → A contagem começa em 0: a primeira caixa é idades[0].

### Degrau 2 — guiado, escolher

> O nome do array não recebe atribuição: de copia = notas; o compilador reclama.
> As caixas não mudam de lugar, e o conjunto não é trocado por outro.

**Versão 1.** O que o compilador faz com a última linha?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int copia[3];

copia = notas;
```

Opções: `Reclama: o nome de um array não recebe atribuição`  `Aceita: dá para atribuir ao nome de um array, e copia fica igual a notas`  `Aceita: copia passa a apontar para notas`

Resposta certa: `Reclama: o nome de um array não recebe atribuição`

Se errar:

- respondeu `Aceita: dá para atribuir ao nome de um array, e copia fica igual a notas` → O nome do array vale para o conjunto, e o conjunto não é trocado por outro: o compilador reclama da linha. O que recebe valor é cada caixa, uma por vez. _(aponta a crença `array_is_assignable`)_
- respondeu `Aceita: copia passa a apontar para notas` → copia não é um ponteiro: é o conjunto das três caixas dela, que não muda de lugar. O compilador reclama da linha.
- qualquer outro erro → O compilador reclama: o nome de um array não recebe atribuição.

**Versão 2.** O que o compilador faz com a última linha?

Já está escrito:

```c
int idades[3] = {15, 16, 17};
int outra[3];

outra = idades;
```

Opções: `Aceita: outra passa a apontar para idades`  `Aceita: dá para atribuir ao nome de um array, e outra fica igual a idades`  `Reclama: o nome de um array não recebe atribuição`

Resposta certa: `Reclama: o nome de um array não recebe atribuição`

Se errar:

- respondeu `Aceita: dá para atribuir ao nome de um array, e outra fica igual a idades` → O nome do array vale para o conjunto, e o conjunto não é trocado por outro: o compilador reclama da linha. O que recebe valor é cada caixa, uma por vez. _(aponta a crença `array_is_assignable`)_
- respondeu `Aceita: outra passa a apontar para idades` → outra não é um ponteiro: é o conjunto das três caixas dela, que não muda de lugar. O compilador reclama da linha.
- qualquer outro erro → O compilador reclama: o nome de um array não recebe atribuição.

### Degrau 3 — guiado, montar

> Para copiar, é caixa por caixa: copia[0] = notas[0]; e assim por diante.

**Versão 1.** Monte a linha que copia a primeira caixa de notas para a primeira de copia.

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int copia[3];
```

Peças: `copia[0]`  `=`  `notas[0]`  `;`  `copia`  `notas`

Resposta certa: `copia[0] = notas[0];`

Se errar:

- respondeu `copia = notas ;` → De copia = notas; o compilador reclama: o nome do array não recebe atribuição. A cópia é de caixa para caixa: copia[0] = notas[0];
- respondeu `notas[0] = copia[0] ;` → Essa linha copia ao contrário, de copia para notas. Quem recebe fica à esquerda do sinal de igual: copia[0] = notas[0];
- qualquer outro erro → Quem recebe fica à esquerda, e é uma caixa de cada vez: copia[0] = notas[0];

**Versão 2.** Monte a linha que copia a segunda caixa de idades para a segunda de outra.

Já está escrito:

```c
int idades[3] = {15, 16, 17};
int outra[3];
```

Peças: `outra[1]`  `=`  `idades[1]`  `;`  `outra`  `idades`

Resposta certa: `outra[1] = idades[1];`

Se errar:

- respondeu `outra = idades ;` → De outra = idades; o compilador reclama: o nome do array não recebe atribuição. A cópia é de caixa para caixa: outra[1] = idades[1];
- respondeu `idades[1] = outra[1] ;` → Essa linha copia ao contrário, de outra para idades. Quem recebe fica à esquerda do sinal de igual: outra[1] = idades[1];
- qualquer outro erro → Quem recebe fica à esquerda, e é uma caixa de cada vez: outra[1] = idades[1];

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Copiar é caixa por caixa, e são dois conjuntos_

**Versão 1.** O trecho copia uma caixa de notas para copia, e depois muda a cópia. Que número aparece?

```c
int notas[3] = {7, 8, 9};
int copia[3];

copia[0] = notas[0];
copia[0] = 1;
printf("%d\n", notas[0]);
```

Resposta certa: `7`

Se errar:

- digitou `1` → copia tem as caixas dela. O 1 foi para copia[0]; notas[0] é outra caixa, e continua com 7.
- qualquer outro erro → São dois conjuntos de caixas. Mudar copia[0] não muda notas[0], que vale 7.

**Versão 2.** O trecho copia uma caixa de idades para outra, e depois muda a cópia. Que número aparece?

```c
int idades[3] = {15, 16, 17};
int outra[3];

outra[2] = idades[2];
outra[2] = 0;
printf("%d\n", idades[2]);
```

Resposta certa: `17`

Se errar:

- digitou `0` → outra tem as caixas dela. O 0 foi para outra[2]; idades[2] é outra caixa, e continua com 17.
- qualquer outro erro → São dois conjuntos de caixas. Mudar outra[2] não muda idades[2], que vale 17.

### Degrau 5 — prática, escolher

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int copia[3];
```

Opções: `copia[1] = notas[1];`  `copia = notas;`  `copia = {7, 8, 9};`

Resposta certa: `copia[1] = notas[1];`

Se errar:

- respondeu `copia = notas;` → O nome do array não recebe atribuição: o compilador reclama. O que recebe valor é a caixa: copia[1] = notas[1];
- respondeu `copia = {7, 8, 9};` → A lista entre chaves só vale na declaração. Depois dela, o nome do array não recebe atribuição: é caixa por caixa.
- qualquer outro erro → O que recebe valor é a caixa, e não o conjunto: copia[1] = notas[1];

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int idades[3] = {15, 16, 17};
int outra[3];
```

Opções: `outra = idades;`  `outra[2] = idades[2];`  `outra = {15, 16, 17};`

Resposta certa: `outra[2] = idades[2];`

Se errar:

- respondeu `outra = idades;` → O nome do array não recebe atribuição: o compilador reclama. O que recebe valor é a caixa: outra[2] = idades[2];
- respondeu `outra = {15, 16, 17};` → A lista entre chaves só vale na declaração. Depois dela, o nome do array não recebe atribuição: é caixa por caixa.
- qualquer outro erro → O que recebe valor é a caixa, e não o conjunto: outra[2] = idades[2];

### Se errar a pergunta do topo: a revisão

> Cada caixa do array recebe valor quando você quiser: notas[1] = 10; vale.
> O conjunto, não: de copia = notas; o compilador reclama. Copiar é caixa por caixa.

```c
int notas[3] = {7, 8, 9};
int copia[3];

copia[0] = notas[0];
printf("%d\n", copia[0]);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Dá para atribuir ao nome de um array, como em str = f().

```c
int notas[3] = {7, 8, 9};
int copia[3];

copia = notas;
```

**A última linha tenta passar notas para copia de uma vez. O que o compilador faz?**

- Aceita, e copia fica com 7, 8 e 9 _(é o que a crença espera)_
- Reclama: o nome de um array não recebe atribuição _(é o que a máquina faz)_

O compilador reclama:

```
assignment to expression with array type
```

_Mensagem do gcc 16.2. O programa não chega a existir: com essa linha, o compilador não o monta._

O que isto mostra: O compilador reclama da última linha: copia é um array, e o nome de um array não recebe atribuição. O que recebe valor é cada caixa, uma por vez.

## I2 — Ao passar um array para uma função, só o endereço da primeira caixa viaja. Lá dentro não dá mais para saber quantas caixas eram.

### Degrau 1 — guiado, escolher

> O parâmetro escrito char v[10] é um ponteiro: o mesmo que char *v.
> O 10 dali não cria caixa nenhuma, e a função não fica sabendo dele.

**Versão 1.** Dentro desta função, o que v é?

Já está escrito:

```c
void marca(char v[10]) { v[0] = 'a'; }
```

Opções: `Um ponteiro para char`  `Um array de dez caixas de char`  `Uma cópia das dez caixas`

Resposta certa: `Um ponteiro para char`

Se errar:

- respondeu `Um array de dez caixas de char` → No parâmetro, char v[10] é só outro jeito de escrever char *v. As dez caixas ficam com quem chamou; a função recebe o endereço da primeira.
- respondeu `Uma cópia das dez caixas` → As caixas não são copiadas na chamada: o que chega é o endereço da primeira. v é um ponteiro.
- qualquer outro erro → No parâmetro, char v[10] é um ponteiro para char.

**Versão 2.** Dentro desta função, o que v é?

Já está escrito:

```c
void zera(int v[5]) { v[0] = 0; }
```

Opções: `Um array de cinco caixas de int`  `Um ponteiro para int`  `Uma cópia das cinco caixas`

Resposta certa: `Um ponteiro para int`

Se errar:

- respondeu `Um array de cinco caixas de int` → No parâmetro, int v[5] é só outro jeito de escrever int *v. As cinco caixas ficam com quem chamou; a função recebe o endereço da primeira.
- respondeu `Uma cópia das cinco caixas` → As caixas não são copiadas na chamada: o que chega é o endereço da primeira. v é um ponteiro.
- qualquer outro erro → No parâmetro, int v[5] é um ponteiro para int.

### Degrau 2 — guiado, escolher

> Fora da função, sizeof notas mede as cinco caixas. Dentro dela, sizeof v mede o ponteiro.
> Quantas caixas havia, lá dentro não dá mais para saber.

**Versão 1.** notas tem cinco caixas. O que o sizeof v de dentro da função mede?

Já está escrito:

```c
void mede(int v[]) { printf("%zu\n", sizeof v); }

int notas[5];

mede(notas);
```

Opções: `O tamanho de um ponteiro`  `As cinco caixas: dentro da função, sizeof ainda mede o array inteiro`  `Uma caixa de int`

Resposta certa: `O tamanho de um ponteiro`

Se errar:

- respondeu `As cinco caixas: dentro da função, sizeof ainda mede o array inteiro` → Dentro da função não há array: v é um ponteiro, com o endereço da primeira caixa. sizeof v mede esse ponteiro. As cinco caixas ficaram com quem chamou. _(aponta a crença `sizeof_array_via_pointer`)_
- respondeu `Uma caixa de int` → v não é uma caixa de int: é um ponteiro, que guarda um endereço. sizeof v mede o ponteiro.
- qualquer outro erro → Dentro da função v é um ponteiro, e sizeof v mede o ponteiro.

**Versão 2.** idades tem oito caixas. O que o sizeof v de dentro da função mede?

Já está escrito:

```c
void mede(int v[]) { printf("%zu\n", sizeof v); }

int idades[8];

mede(idades);
```

Opções: `As oito caixas: dentro da função, sizeof ainda mede o array inteiro`  `Uma caixa de int`  `O tamanho de um ponteiro`

Resposta certa: `O tamanho de um ponteiro`

Se errar:

- respondeu `As oito caixas: dentro da função, sizeof ainda mede o array inteiro` → Dentro da função não há array: v é um ponteiro, com o endereço da primeira caixa. sizeof v mede esse ponteiro. As oito caixas ficaram com quem chamou. _(aponta a crença `sizeof_array_via_pointer`)_
- respondeu `Uma caixa de int` → v não é uma caixa de int: é um ponteiro, que guarda um endereço. sizeof v mede o ponteiro.
- qualquer outro erro → Dentro da função v é um ponteiro, e sizeof v mede o ponteiro.

### Degrau 3 — guiado, digitar

> A saída é mandar o número de caixas junto, em outro parâmetro.

**Versão 1.** A função recebe o endereço e o número de caixas, e mostra a última. Que número aparece?

```c
void ultimo(int v[], int n) { printf("%d\n", v[n - 1]); }

int notas[3] = {7, 8, 9};

ultimo(notas, 3);
```

Resposta certa: `9`

Se errar:

- digitou `3` → 3 é o número de caixas, que foi em n. A função mostra v[n - 1], que é v[2]: a última caixa, 9.
- digitou `8` → Com n valendo 3, v[n - 1] é v[2]. A contagem começa em 0, e v[2] é a terceira caixa: 9.
- qualquer outro erro → Com n valendo 3, v[n - 1] é v[2], a última caixa de notas: 9.

**Versão 2.** A função recebe o endereço e o número de caixas, e mostra a última. Que número aparece?

```c
void ultimo(int v[], int n) { printf("%d\n", v[n - 1]); }

int idades[4] = {15, 16, 17, 18};

ultimo(idades, 4);
```

Resposta certa: `18`

Se errar:

- digitou `4` → 4 é o número de caixas, que foi em n. A função mostra v[n - 1], que é v[3]: a última caixa, 18.
- digitou `17` → Com n valendo 4, v[n - 1] é v[3]. A contagem começa em 0, e v[3] é a quarta caixa: 18.
- qualquer outro erro → Com n valendo 4, v[n - 1] é v[3], a última caixa de idades: 18.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O tamanho não viaja: vai em outro parâmetro_

**Versão 1.** notas tem três caixas, mas a chamada diz que são 2. Que número aparece?

```c
void ultimo(int v[], int n) { printf("%d\n", v[n - 1]); }

int notas[3] = {7, 8, 9};

ultimo(notas, 2);
```

Resposta certa: `8`

Se errar:

- digitou `9` → A função não sabe quantas caixas notas tem: só sabe o n que recebeu. Com n valendo 2, ela mostra v[1]: 8.
- qualquer outro erro → A função só conhece o n que recebeu. Com 2, a última para ela é v[1]: 8.

**Versão 2.** idades tem quatro caixas, mas a chamada diz que são 3. Que número aparece?

```c
void ultimo(int v[], int n) { printf("%d\n", v[n - 1]); }

int idades[4] = {15, 16, 17, 18};

ultimo(idades, 3);
```

Resposta certa: `17`

Se errar:

- digitou `18` → A função não sabe quantas caixas idades tem: só sabe o n que recebeu. Com n valendo 3, ela mostra v[2]: 17.
- qualquer outro erro → A função só conhece o n que recebeu. Com 3, a última para ela é v[2]: 17.

### Degrau 5 — prática, escolher

**Versão 1.** O que uma função precisa receber para ir até a última caixa de um array?

Opções: `O endereço da primeira caixa e o número de caixas`  `Só o array: o tamanho viaja junto`  `Só o array: ela mede com sizeof lá dentro`

Resposta certa: `O endereço da primeira caixa e o número de caixas`

Se errar:

- respondeu `Só o array: o tamanho viaja junto` → O tamanho não viaja: o que chega é só o endereço da primeira caixa. O número de caixas vai em outro parâmetro.
- respondeu `Só o array: ela mede com sizeof lá dentro` → Lá dentro, sizeof mede o ponteiro, e não o array. O número de caixas tem de ir em outro parâmetro.
- qualquer outro erro → O endereço da primeira caixa, e o número de caixas em outro parâmetro.

**Versão 2.** Uma função recebe um array. Como ela fica sabendo quantas caixas ele tem?

Opções: `Pelo sizeof, lá dentro`  `Por outro parâmetro, com o número`  `Não precisa: o array chega inteiro`

Resposta certa: `Por outro parâmetro, com o número`

Se errar:

- respondeu `Pelo sizeof, lá dentro` → Lá dentro, sizeof mede o ponteiro, e não o array. O número de caixas tem de ir em outro parâmetro.
- respondeu `Não precisa: o array chega inteiro` → O array não chega inteiro: o que chega é só o endereço da primeira caixa. O número de caixas vai em outro parâmetro.
- qualquer outro erro → O número de caixas vai em outro parâmetro: a função não tem como medir.

### Se errar a pergunta do topo: a revisão

> O parâmetro int v[] é um ponteiro: recebe o endereço da primeira caixa, e mais nada.
> Lá dentro, sizeof v mede o ponteiro. O número de caixas tem de ir junto, em outro parâmetro.

```c
void ultimo(int v[], int n) { printf("%d\n", v[n - 1]); }

int notas[3] = {7, 8, 9};

ultimo(notas, 3);
```

A máquina imprime:

```
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> Dentro da função, sizeof ainda mede o array inteiro.

```c
void mede(char v[10]) { printf("%zu\n", sizeof v); }

char nome[10];

mede(nome);
```

**nome tem dez caixas de char, e o parâmetro está escrito char v[10]. O que o sizeof de dentro da função mostra?**

- 10 _(é o que a crença espera)_
- Outro número: o tamanho de um ponteiro _(é o que a máquina faz)_

A máquina imprime:

```
8
```

_O 8 é o tamanho de um ponteiro nesta máquina; em outra pode ser 4. Em nenhuma sai 10. O próprio compilador avisa, ao ler a função, que esse sizeof devolve o tamanho de um ponteiro._

O que isto mostra: Saiu 8, e não 10. Dentro da função, v é um ponteiro: o que chegou foi o endereço da primeira caixa, e sizeof mede esse ponteiro. As dez caixas ficaram com quem chamou.

## I3 — a e p são coisas diferentes, mesmo que a[i] e p[i] se escrevam do mesmo jeito.

### Degrau 1 — guiado, digitar

> Com p = notas; as duas escritas chegam na mesma caixa: notas[1] e p[1].

**Versão 1.** O trecho escreve por notas e lê por p. Que número aparece?

```c
int notas[3] = {7, 8, 9};
int *p;

p = notas;
notas[1] = 0;
printf("%d\n", p[1]);
```

Resposta certa: `0`

Se errar:

- digitou `8` → p guarda o endereço da primeira caixa de notas, e p[1] é a segunda caixa DELA. O 0 escrito em notas[1] é o que p[1] encontra.
- qualquer outro erro → notas[1] e p[1] são a mesma caixa, que recebeu 0.

**Versão 2.** O trecho escreve por idades e lê por q. Que número aparece?

```c
int idades[3] = {15, 16, 17};
int *q;

q = idades;
idades[2] = 1;
printf("%d\n", q[2]);
```

Resposta certa: `1`

Se errar:

- digitou `17` → q guarda o endereço da primeira caixa de idades, e q[2] é a terceira caixa DELA. O 1 escrito em idades[2] é o que q[2] encontra.
- qualquer outro erro → idades[2] e q[2] são a mesma caixa, que recebeu 1.

### Degrau 2 — guiado, escolher

> A escrita é igual, mas os tipos são diferentes: notas é o conjunto das três caixas de int.
> p é uma caixa só, que guarda um endereço.

**Versão 1.** notas e p são a mesma coisa?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int *p;

p = notas;
```

Opções: `Não: notas são três caixas; p é uma só, com um endereço`  `São: array e ponteiro são a mesma coisa`  `Não: p é uma cópia das três caixas`

Resposta certa: `Não: notas são três caixas; p é uma só, com um endereço`

Se errar:

- respondeu `São: array e ponteiro são a mesma coisa` → Parecem a mesma coisa porque notas[1] e p[1] se escrevem igual. Mas notas é o conjunto das três caixas de int; p é outra caixa, que guarda o endereço da primeira. _(aponta a crença `array_is_pointer`)_
- respondeu `Não: p é uma cópia das três caixas` → p = notas; não copia caixa nenhuma: p recebe o endereço da primeira. p é uma caixa só, com esse endereço.
- qualquer outro erro → notas é o conjunto das três caixas. p é uma caixa só, com o endereço da primeira.

**Versão 2.** idades e q são a mesma coisa?

Já está escrito:

```c
int idades[3] = {15, 16, 17};
int *q;

q = idades;
```

Opções: `São: array e ponteiro são a mesma coisa`  `Não: q é uma cópia das três caixas`  `Não: idades são três caixas; q é uma só, com um endereço`

Resposta certa: `Não: idades são três caixas; q é uma só, com um endereço`

Se errar:

- respondeu `São: array e ponteiro são a mesma coisa` → Parecem a mesma coisa porque idades[1] e q[1] se escrevem igual. Mas idades é o conjunto das três caixas de int; q é outra caixa, que guarda o endereço da primeira. _(aponta a crença `array_is_pointer`)_
- respondeu `Não: q é uma cópia das três caixas` → q = idades; não copia caixa nenhuma: q recebe o endereço da primeira. q é uma caixa só, com esse endereço.
- qualquer outro erro → idades é o conjunto das três caixas. q é uma caixa só, com o endereço da primeira.

### Degrau 3 — guiado, escolher

> p pode receber outro endereço quando você quiser.
> notas não: o conjunto das caixas não muda de lugar.

**Versão 1.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int idades[3] = {15, 16, 17};
int *p;

p = notas;
```

Opções: `p = idades;`  `notas = idades;`  `notas = p;`

Resposta certa: `p = idades;`

Se errar:

- respondeu `notas = idades;` → notas é um array, e o nome dele não recebe atribuição: o conjunto não muda de lugar, e o compilador reclama. Quem pode receber outro endereço é p.
- respondeu `notas = p;` → notas não é um ponteiro: não dá para guardar nele o endereço que está em p, e o compilador reclama. Quem pode receber outro endereço é p.
- qualquer outro erro → O ponteiro pode receber outro endereço: p = idades;

**Versão 2.** Qual destas linhas o compilador aceita?

Já está escrito:

```c
int notas[3] = {7, 8, 9};
int idades[3] = {15, 16, 17};
int *q;

q = idades;
```

Opções: `idades = notas;`  `idades = q;`  `q = notas;`

Resposta certa: `q = notas;`

Se errar:

- respondeu `idades = notas;` → idades é um array, e o nome dele não recebe atribuição: o conjunto não muda de lugar, e o compilador reclama. Quem pode receber outro endereço é q.
- respondeu `idades = q;` → idades não é um ponteiro: não dá para guardar nele o endereço que está em q, e o compilador reclama. Quem pode receber outro endereço é q.
- qualquer outro erro → O ponteiro pode receber outro endereço: q = notas;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O ponteiro muda de endereço; o array não_

**Versão 1.** p começa na primeira caixa e depois recebe outro endereço. Que número aparece?

```c
int notas[3] = {7, 8, 9};
int *p;

p = notas;
p = &notas[1];
printf("%d\n", p[0]);
```

Resposta certa: `8`

Se errar:

- digitou `7` → p trocou de endereço: passou a apontar para notas[1]. p[0] é a caixa que p aponta agora: 8.
- qualquer outro erro → p agora aponta para notas[1], e p[0] é essa caixa: 8.

**Versão 2.** q começa na primeira caixa e depois recebe outro endereço. Que número aparece?

```c
int idades[3] = {15, 16, 17};
int *q;

q = idades;
q = &idades[2];
printf("%d\n", q[0]);
```

Resposta certa: `17`

Se errar:

- digitou `15` → q trocou de endereço: passou a apontar para idades[2]. q[0] é a caixa que q aponta agora: 17.
- qualquer outro erro → q agora aponta para idades[2], e q[0] é essa caixa: 17.

### Degrau 5 — prática, escolher

**Versão 1.** Qual das duas variáveis ocupa mais espaço na memória?

Já está escrito:

```c
char v[10];
char *p;
```

Opções: `v: são dez caixas de char`  `As duas ocupam o mesmo: array e ponteiro são iguais`  `p: ele guarda as dez caixas e mais o endereço`

Resposta certa: `v: são dez caixas de char`

Se errar:

- respondeu `As duas ocupam o mesmo: array e ponteiro são iguais` → v é o conjunto das dez caixas; p é uma caixa só, do tamanho de um endereço. Não ocupam o mesmo espaço, e v ocupa mais.
- respondeu `p: ele guarda as dez caixas e mais o endereço` → p não guarda caixa de char nenhuma: é uma caixa só, do tamanho de um endereço. Quem tem as dez caixas é v.
- qualquer outro erro → v é o conjunto das dez caixas, e ocupa mais que p, que é uma caixa só.

**Versão 2.** Qual das duas variáveis ocupa mais espaço na memória?

Já está escrito:

```c
char *q;
char letras[12];
```

Opções: `As duas ocupam o mesmo: array e ponteiro são iguais`  `q: ele guarda as doze caixas e mais o endereço`  `letras: são doze caixas de char`

Resposta certa: `letras: são doze caixas de char`

Se errar:

- respondeu `As duas ocupam o mesmo: array e ponteiro são iguais` → letras é o conjunto das doze caixas; q é uma caixa só, do tamanho de um endereço. Não ocupam o mesmo espaço, e letras ocupa mais.
- respondeu `q: ele guarda as doze caixas e mais o endereço` → q não guarda caixa de char nenhuma: é uma caixa só, do tamanho de um endereço. Quem tem as doze caixas é letras.
- qualquer outro erro → letras é o conjunto das doze caixas, e ocupa mais que q, que é uma caixa só.

### Se errar a pergunta do topo: a revisão

> notas[1] e p[1] se escrevem igual, mas notas e p não são a mesma coisa.
> notas é o conjunto das caixas, e não muda de lugar. p é uma caixa só, com um endereço que pode ser trocado.

```c
int notas[3] = {7, 8, 9};
int *p;

p = notas;
printf("%d\n", p[1]);
```

A máquina imprime:

```
8
```

### Se a pessoa disser a crença: a prova

Você disse:

> Array e ponteiro são a mesma coisa.

```c
char v[10];
char *p;

p = v;
printf("%zu\n", sizeof v);
printf("%zu\n", sizeof p);
```

**p recebeu o endereço da primeira caixa de v. sizeof diz quanto espaço cada um ocupa. O que os dois printf mostram?**

- O mesmo número: array e ponteiro são a mesma coisa _(é o que a crença espera)_
- Dois números diferentes _(é o que a máquina faz)_

A máquina imprime:

```
10
8
```

_O 8 é o tamanho de um ponteiro nesta máquina; em outra pode ser 4. O 10 não muda: são as dez caixas de v._

O que isto mostra: Saíram 10 e 8. v é o conjunto das dez caixas; p é uma caixa só, do tamanho de um endereço. p[1] e v[1] chegam na mesma caixa, mas v e p não são a mesma coisa.
