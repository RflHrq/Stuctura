# Revisão dos candidatos — kc_01

**15 itens**, em 5 nós.

Leia item a item. Para aprovar, escreva seu nome em `revisado_por`
no arquivo `.yaml` do nó e rode:

```bash
python scripts/gerar.py --topico kc_01 --aprovar
```

Só entra no domínio o que tiver `revisado_por` preenchido.

**O que conferir em cada item** (docs/linguagem.md):

- a resposta certa está certa, e as erradas estão erradas;
- cada distrator é a crença **dita bem** — alguém escolheria aquilo;
- o enunciado não entrega a resposta;
- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue;
- o código compila e faz o que o enunciado diz.

---

## B1 — Enquanto o programa roda, ele tem uma rua só dele. Outro programa não mexe nessa rua.

### kc01_gb1_n1_1 · degrau 1 · comparar_casos · teorica

Duas ruas: uma que o seu programa recebe só para ele, e uma que todos os programas dividem. Qual é a sua, enquanto o programa roda?

- **[certa]** A primeira: a rua é dele
- [memoria_e_do_computador → nega B1] A segunda: a rua é da cidade
- [memory_is_uniform → nega I2] A segunda, e por isso somem casas

> b é a crença do nó na analogia; c traz o vizinho I2.

`revisado_por:` ________

### kc01_gb1_n2_2 · degrau 2 · achar_o_erro · codigo

B copiou o endereço que A imprimiu. Por que não funciona?

```c
/* programa A */  int x = 42;  printf("%p\n", (void *)&x);
/* programa B */  int *p = (int *)0x7ffd1234;  printf("%d\n", *p);
```

- **[certa]** O endereço de A não vale na rua de B
- [memoria_e_do_computador → nega B1] Funciona: o endereço é o mesmo lugar
- [memory_is_uniform → nega I2] Funciona: memória é uma só região

> b é a crença do nó na forma mais direta que ela tem; c traz o I2.

`revisado_por:` ________

### kc01_gb1_n3_3 · degrau 3 · achar_o_erro · codigo

Um colega diz que isso imprime o que o programa anterior deixou. Onde ele erra?

```c
int x;
printf("%d\n", x);
```

- **[certa]** O lixo é da rua deste programa
- [memoria_e_do_computador → nega B1] Não erra: é o que o anterior deixou
- [local_sobrevive → nega B2] Erra: x guarda o que outra função deixou

> b é a crença do nó; c traz o vizinho B2, de quem acha que o que uma função deixou continua alcançável.

`revisado_por:` ________

---

## B2 — As casas criadas dentro de uma função aparecem quando ela começa e somem quando ela termina.

### kc01_gb2_n1_1 · degrau 1 · comparar_casos · teorica

Duas coisas na rua: uma casa da rua lateral, desmontada quando a função sai, e um terreno alugado que fica. Qual é a variável local?

- **[certa]** A primeira: desmontada na saída
- [local_sobrevive → nega B2] A segunda: ela continua lá
- [memory_is_uniform → nega I2] As duas ficam: a rua não muda

> b é a crença do nó na analogia; c traz o vizinho I2.

`revisado_por:` ________

### kc01_gb2_n2_2 · degrau 2 · achar_o_erro · codigo

O que o chamador recebe?

```c
int *conta(void) {
    int total = 10;
    return &total;
}
```

- **[certa]** Um endereço que deixou de valer
- [local_sobrevive → nega B2] O endereço de total, que continua lá
- [memory_is_uniform → nega I2] Um endereço como outro: a rua é uma

> b é a crença do nó; c traz o vizinho I2.

`revisado_por:` ________

### kc01_gb2_n3_3 · degrau 3 · comparar_casos · codigo

Qual das duas devolve algo que ainda vale?

```c
/* A */  int *f(void) { int n = 1;                    return &n; }
/* B */  int *g(void) { int *q = malloc(sizeof(int)); return q;  }
```

- **[certa]** B: o terreno fica até o free
- [local_sobrevive → nega B2] As duas: nada é desmontado
- [heap_dies_with_function → nega I1] Nenhuma: as duas somem na saída

> O par separa as duas quadras. b é a crença do nó; c traz o I1, que é a crença espelhada — a do monte.

`revisado_por:` ________

---

## B3 — O terreno que você aluga com malloc continua seu depois que a função acaba.

### kc01_gb3_n1_1 · degrau 1 · comparar_casos · teorica

Dois jeitos de o terreno alugado voltar para a prefeitura: você devolver, ou ela tomar de volta sozinha. Qual acontece em C?

- **[certa]** O primeiro: você devolve
- [system_frees_auto → nega B3] O segundo: ela toma sozinha
- [memory_is_uniform → nega I2] Nenhum: o terreno fica como está

> b é a crença do nó na analogia; c traz o vizinho I2.

`revisado_por:` ________

### kc01_gb3_n2_2 · degrau 2 · achar_o_erro · codigo

O que essa função deixa para trás a cada chamada?

```c
void guarda(void) {
    int *p = malloc(1000000);
}
```

- **[certa]** Um bloco alugado e sem dono
- [system_frees_auto → nega B3] Nada: o sistema devolve na saída
- [heap_dies_with_function → nega I1] Nada: o bloco morre com a função

> b é a crença do nó (FAQ 7.24 e 7.25); c traz o vizinho I1.

`revisado_por:` ________

### kc01_gb3_n3_3 · degrau 3 · comparar_casos · codigo

Depois de mil chamadas de cada uma, qual delas acumulou memória?

```c
/* A */  void f(void) { int v[100];               }
/* B */  void g(void) { int *v = malloc(100 * 4); }
```

- **[certa]** B: cada bloco ficou lá
- [system_frees_auto → nega B3] Nenhuma: o sistema limpa as duas
- [memory_is_uniform → nega I2] As duas, no mesmo lugar da rua

> b é a crença do nó; c traz o vizinho I2.

`revisado_por:` ________

---

## I1 — Então há dois jeitos: a casa some sozinha, e o terreno fica até você devolver.

### kc01_gi1_n1_1 · degrau 1 · comparar_casos · teorica

A casa da rua lateral e o terreno alugado, depois que a função termina. O que sobrou?

- **[certa]** Só o terreno alugado
- [heap_dies_with_function → nega I1] Nenhum dos dois
- [local_sobrevive → nega B2] Os dois, como antes

> b é a crença do nó na analogia; c traz o vizinho B2. As duas erradas são as duas formas de achatar a diferença entre as quadras.

`revisado_por:` ________

### kc01_gi1_n2_2 · degrau 2 · achar_o_erro · codigo

Um colega diz que isso lê memória morta. Onde ele erra?

```c
int *faz(void) {
    int *p = malloc(sizeof(int));
    *p = 7;
    return p;
}
int main(void) { printf("%d\n", *faz()); }
```

- **[certa]** O bloco do malloc sobrevive à função
- [heap_dies_with_function → nega I1] Não erra: o bloco sai com a função
- [local_sobrevive → nega B2] Não erra: p era local, e o bloco é p

> c é a confusão que sustenta a crença: p morre, o bloco não. b é a crença do nó dita direto.

`revisado_por:` ________

### kc01_gi1_n3_3 · degrau 3 · comparar_casos · codigo

Uma das três devolve endereço inválido. Qual?

```c
int *a(void) { static int n = 1;             return &n; }
int *b(void) { int *q = malloc(4); *q = 1;   return q;  }
int *c(void) { int n = 1;                    return &n; }
```

- **[certa]** A terceira: n é local e comum
- [heap_dies_with_function → nega I1] A segunda: o malloc sai com a função
- [local_sobrevive → nega B2] A primeira: static não muda nada

> Três casos quase iguais na escrita e diferentes na vida. b é a crença do nó; c traz o vizinho B2.

`revisado_por:` ________

---

## I2 — Logo a rua tem duas quadras, com regras de arrumação diferentes.

### kc01_gi2_n1_1 · degrau 1 · comparar_casos · teorica

Uma rua com uma regra de arrumação só, e uma rua com duas quadras e duas regras. Qual é a memória do programa?

- **[certa]** A segunda: duas quadras
- [memory_is_uniform → nega I2] A primeira: uma regra só
- [system_frees_auto → nega B3] A primeira, e quem arruma é você

> b é a crença do nó na analogia; c traz o vizinho B3.

`revisado_por:` ________

### kc01_gi2_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int a = 1;
int *b = malloc(sizeof(int));
printf("%d\n", (void *)&a == (void *)b);
```

- **[certa]** 0: são áreas diferentes da rua
- [memory_is_uniform → nega I2] 1: memória é uma região só
- [system_frees_auto → nega B3] 0, e o bloco de b já foi devolvido

> b é a crença do nó; c traz o vizinho B3.

`revisado_por:` ________

### kc01_gi2_n3_3 · degrau 3 · prever_saida · codigo

Depois que f termina, o que ainda ocupa memória?

```c
void f(void) {
    int n = 1;
    int *p = malloc(sizeof(int));
    *p = 2;
}
```

- **[certa]** O bloco de p, sem ninguém apontando
- [memory_is_uniform → nega I2] Nada: as duas seguem a mesma regra
- [system_frees_auto → nega B3] Nada: o sistema recolheu o bloco

> b é a crença do nó; c traz o vizinho B3. O item é o vazamento visto pela premissa que o explica.

`revisado_por:` ________

