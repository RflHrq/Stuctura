# Revisão dos candidatos — kc_02

**18 itens**, em 6 nós.

Leia item a item. Para aprovar, escreva seu nome em `revisado_por`
no arquivo `.yaml` do nó e rode:

```bash
python scripts/gerar.py --topico kc_02 --aprovar
```

Só entra no domínio o que tiver `revisado_por` preenchido.

**O que conferir em cada item** (docs/linguagem.md):

- a resposta certa está certa, e as erradas estão erradas;
- cada distrator é a crença **dita bem** — alguém escolheria aquilo;
- o enunciado não entrega a resposta;
- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue;
- o código compila e faz o que o enunciado diz.

---

## B1 — A memória é uma rua de lugares numerados. O número do lugar é o endereço — não o que está guardado nele.

### kc02_gb1_n1_1 · degrau 1 · comparar_casos · teorica

Duas casas da mesma rua têm sofás idênticos. O que distingue uma da outra?

- **[certa]** O número de cada porta
- [pointer_is_data → nega B3] Nada: com o mesmo conteúdo, são a mesma casa
- [memory_is_by_name → nega B1] O nome de quem mora em cada uma

> confundir o lugar com o conteúdo é a raiz de B1

`revisado_por:` ________

### kc02_gb1_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int a = 5;
int b = 5;
printf("%d
", &a == &b);
```

- **[certa]** 0, porque são dois lugares diferentes
- [pointer_is_data → nega B3] 1, porque guardam o mesmo valor
- [memory_is_by_name → nega B1] 1: o que identifica é o nome, não o lugar

> mesmo valor, mesmo lugar: a confusão de B1 em C

`revisado_por:` ________

### kc02_gb1_n3_3 · degrau 3 · achar_o_erro · codigo

Um colega esperava que essa impressão mudasse depois de x = 20. Por que ele está errado?

```c
int x = 10;
int *p = &x;
x = 20;
printf("%p
", (void *)p);
```

- **[certa]** p guarda o lugar de x, e o lugar não mudou
- [pointer_is_data → nega B3] p guarda o valor de x, e o valor mudou
- [memory_is_by_name → nega B1] p guarda o nome x, e o nome não muda

> o endereço é do lugar, e o lugar não muda com o valor

`revisado_por:` ________

---

## B2 — p é uma caixa como as outras: ocupa espaço, e a caixa p também tem um endereço, que é dela.

### kc02_gb2_n1_1 · degrau 1 · reconhecer_conceito · teorica

Você guarda um papel com o número 1000 escrito dentro da casa 2A00. Quantas casas existem nessa história?

- **[certa]** Duas: a 1000 e a 2A00
- [pointer_has_no_address → nega B2] Uma: o papel não é casa, é só a ligação
- [pointer_and_target_are_one → nega I1] Uma: o papel e a casa 1000 são a mesma

> o papel não flutua: ele está numa casa, que tem número

`revisado_por:` ________

### kc02_gb2_n2_2 · degrau 2 · reconhecer_conceito · codigo

O que esse sizeof mede?

```c
int x = 42;
int *p = &x;
printf("%zu
", sizeof p);
```

- **[certa]** O tamanho da variável p
- [pointer_and_target_are_one → nega I1] O tamanho de x, que é para onde p aponta
- [pointer_has_no_address → nega B2] Nada: p não ocupa espaço para medir

> medir p só faz sentido se p ocupar espaço

`revisado_por:` ________

### kc02_gb2_n3_3 · degrau 3 · comparar_casos · codigo

A terceira linha só faz sentido por quê?

```c
int x = 42;
int *p = &x;
int **pp = &p;
```

- **[certa]** Porque p é variável e tem endereço
- [pointer_and_target_are_one → nega I1] Porque &p devolve o endereço de x
- [pointer_has_no_address → nega B2] Ela não faz sentido: p não tem endereço

> &p exige que p tenha endereço próprio

`revisado_por:` ________

---

## B3 — O que está dentro de p é um endereço: o número do lugar onde outra caixa fica.

### kc02_gb3_n1_1 · degrau 1 · reconhecer_conceito · teorica

Você quer saber o que tem na sala da casa cujo número está escrito no papel. Basta ler o papel?

- **[certa]** Não: o papel dá o número, e é preciso ir lá
- [pointer_is_data → nega B3] Sim: o papel já traz o que tem na sala
- [pointer_and_target_are_one → nega I1] Sim: o papel e a sala são a mesma coisa

> ler o papel dá o lugar, não o conteúdo

`revisado_por:` ________

### kc02_gb3_n2_2 · degrau 2 · achar_o_erro · codigo

Por que o compilador reclama dessa linha?

```c
int x = 42;
int *p = &x;
printf("%d
", p);
```

- **[certa]** %d espera um int, e p é um endereço
- [pointer_is_data → nega B3] Não deveria: p vale 42, que é int
- [pointer_is_integer → nega I2] Por nada: endereço é um int qualquer

> quem acha que p vale 42 não vê problema nenhum aqui

`revisado_por:` ________

### kc02_gb3_n3_3 · degrau 3 · prever_saida · codigo

Depois dessas linhas, o que sai?

```c
int x = 42, y = 7;
int *p = &x;
*p = y;
printf("%d
", x);
```

- **[certa]** 7, porque *p escreve no lugar de x
- [pointer_and_target_are_one → nega I1] 42, porque *p = y muda só o ponteiro
- [pointer_is_data → nega B3] 7, e p agora guarda 7

> *p escreve no lugar guardado em p, não em p

`revisado_por:` ________

---

## I1 — Então p e a caixa apontada são duas caixas diferentes, em dois lugares diferentes.

### kc02_gi1_n1_1 · degrau 1 · reconhecer_conceito · teorica

Duas pessoas têm papéis com o mesmo número de casa. Quantas casas esse número indica?

- **[certa]** Uma: os dois levam à mesma casa
- [pointer_and_target_are_one → nega I1] Duas: cada papel aponta a sua
- [pointer_has_no_address → nega B2] Nenhuma: o papel é a casa

> o papel não é a casa, e dois papéis não fazem duas casas

`revisado_por:` ________

### kc02_gi1_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int x = 1;
int *p = &x;
int *q = p;
*q = 9;
printf("%d
", x);
```

- **[certa]** 9: p e q levam ao mesmo x
- [pointer_and_target_are_one → nega I1] 1: q é cópia, e mexer nela não muda x
- [pointer_is_data → nega B3] 9, e p também passou a valer 9

> copiar o ponteiro não copia a caixa apontada

`revisado_por:` ________

### kc02_gi1_n3_3 · degrau 3 · comparar_casos · codigo

Que diferença há entre A e B?

```c
/* A */  int *p = &x;  int *q = &x;
/* B */  int *p = &x;  int *q = p;
```

- **[certa]** Nenhuma: nos dois p e q levam a x
- [pointer_and_target_are_one → nega I1] Em B, q e p viram a mesma variável
- [pointer_is_data → nega B3] Em A, x fica com dois valores

> nos dois casos são dois ponteiros e uma caixa

`revisado_por:` ________

---

## I2 — Quem sabe o tipo de p é o compilador, que leu int *p. Por isso p não é só um número solto.

### kc02_gi2_n1_1 · degrau 1 · reconhecer_conceito · teorica

Um papel diz apenas 1000. Isso basta para você saber o que vai encontrar lá?

- **[certa]** Não: falta saber do que é esse 1000
- [pointer_is_integer → nega I2] Sim: 1000 é 1000, e pronto
- [pointer_is_data → nega B3] Sim: o próprio 1000 diz o que tem lá

> o número sozinho não diz de que é o lugar

`revisado_por:` ________

### kc02_gi2_n2_2 · degrau 2 · prever_saida · codigo

Os dois sizeof medem coisas diferentes. Quais?

```c
int x = 42;
int *p = &x;
printf("%zu %zu
", sizeof p, sizeof *p);
```

- **[certa]** O do ponteiro e o do int apontado
- [pointer_is_data → nega B3] Os dois medem o int, de jeitos diferentes
- [pointer_is_integer → nega I2] Os dois medem o mesmo número guardado

> só mede os dois quem distingue o ponteiro do apontado

`revisado_por:` ________

### kc02_gi2_n3_3 · degrau 3 · achar_o_erro · codigo

O que esse programa mostra?

```c
double d = 3.5;
int *p = (int *)&d;
printf("%d
", *p);
```

- **[certa]** Lixo: o tipo do ponteiro não bate
- [pointer_is_integer → nega I2] 3, porque o 3.5 vira int na leitura
- [pointer_is_data → nega B3] 3.5, porque o endereço leva ao double

> o tipo do ponteiro decide como os bytes são lidos

`revisado_por:` ________

---

## I3 — Com o endereço na mão, dá para chegar naquela caixa de qualquer ponto do programa, sem copiar o conteúdo.

### kc02_gi3_n1_1 · degrau 1 · reconhecer_conceito · teorica

Um vizinho tem o número da sua casa. O que ele consegue fazer que não conseguiria sem o número?

- **[certa]** Chegar até a sua casa sem você levar nada
- [pointer_is_pointless → nega I3] Nada que uma cópia da planta não resolva
- [pointer_and_target_are_one → nega I1] Entrar na casa dele achando que é a sua

> sem o endereço só dá para trabalhar numa cópia

`revisado_por:` ________

### kc02_gi3_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
void soma(int *total, int valor) { *total += valor; }

int t = 0;
soma(&t, 5);
soma(&t, 3);
printf("%d
", t);
```

- **[certa]** 8: as duas chamadas somaram no mesmo t
- [pointer_is_pointless → nega I3] 0: a função soma numa cópia
- [pointer_is_data → nega B3] 8, e t passou a guardar um endereço

> as duas chamadas escrevem no mesmo t de fora

`revisado_por:` ________

### kc02_gi3_n3_3 · degrau 3 · achar_o_erro · codigo

Depois disso x e y não trocaram. O que falta?

```c
void troca(int a, int b) { int t = a; a = b; b = t; }

int x = 1, y = 2;
troca(x, y);
```

- **[certa]** Passar os endereços, e usar *a e *b
- [pointer_is_pointless → nega I3] Nada: trocar dentro da função basta
- [pointer_and_target_are_one → nega I1] Nada: a e b são apelidos de x e y

> sem endereço a função mexe em cópias e nada sai dali

`revisado_por:` ________

