# Revisão dos candidatos — kc_03

**18 itens**, em 6 nós.

Leia item a item. Para aprovar, escreva seu nome em `revisado_por`
no arquivo `.yaml` do nó e rode:

```bash
python scripts/gerar.py --topico kc_03 --aprovar
```

Só entra no domínio o que tiver `revisado_por` preenchido.

**O que conferir em cada item** (docs/linguagem.md):

- a resposta certa está certa, e as erradas estão erradas;
- cada distrator é a crença **dita bem** — alguém escolheria aquilo;
- o enunciado não entrega a resposta;
- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue;
- o código compila e faz o que o enunciado diz.

---

## B1 — Declarar uma variável cria a caixa dela. Uma caixa: a que você nomeou.

### kc03_gb1_n1_1 · degrau 1 · comparar_casos · teorica

Duas casas na rua: uma com morador, outra recém-entregue e sem ninguém. Qual delas existe?

- **[certa]** As duas: as duas têm número
- [no_value_no_memory → nega B1] Só a primeira: a outra espera
- [declaration_zeroes → nega B3] As duas, e a vazia vem limpa

> b é a crença do nó na analogia: sem morador, sem casa. c traz o vizinho B3.

`revisado_por:` ________

### kc03_gb1_n2_2 · degrau 2 · achar_o_erro · codigo

Por que a segunda linha vale, se nenhuma posição recebeu valor?

```c
int v[4];
int *p = v + 2;
```

- **[certa]** As quatro posições já têm lugar
- [no_value_no_memory → nega B1] Não vale: sem valor não há posição
- [declaration_zeroes → nega B3] Vale porque as posições estão em zero

> b é a crença do nó; c traz o vizinho B3, de quem acha que declarar zera.

`revisado_por:` ________

### kc03_gb1_n3_3 · degrau 3 · comparar_casos · codigo

As duas imprimem o mesmo número?

```c
/* A */  int a;      printf("%zu\n", sizeof a);
/* B */  int b = 0;  printf("%zu\n", sizeof b);
```

- **[certa]** Sim: o tamanho não depende do valor
- [no_value_no_memory → nega B1] Não: a ainda não tem tamanho
- [declaration_zeroes → nega B3] Sim, porque a também começa em 0

> b é a crença do nó medida pelo sizeof, que é a forma observável dela. c traz o vizinho B3.

`revisado_por:` ________

---

## B2 — Em int *p, quem é criado é p. O asterisco faz parte do que p é, e não é uma segunda caixa.

### kc03_gb2_n1_1 · degrau 1 · comparar_casos · teorica

Duas descrições de int *p;: ganhei a casa de p, e dentro dela cabe um papel com número; ou ganhei duas casas. Qual vale?

- **[certa]** A primeira: uma casa, a de p
- [estrela_e_do_tipo → nega B2] A segunda: p e o papel
- [declaration_allocates → nega I1] A segunda: p e a casa apontada

> b é a crença do nó na analogia, de quem lê o * como uma segunda coisa declarada. c traz o vizinho I1.

`revisado_por:` ________

### kc03_gb2_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int x = 1;
int* p, q;
p = &x;
q = 5;
printf("%d %d\n", *p, q);
```

- **[certa]** 1 5: q é int, e p é ponteiro
- [estrela_e_do_tipo → nega B2] não compila: q = 5 é inválido
- [declaration_allocates → nega I1] 1 5, e q também aponta para algo

> b é exatamente o que quem lê int* como tipo espera: se q fosse ponteiro, q = 5 não compilaria. c traz o vizinho I1.

`revisado_por:` ________

### kc03_gb2_n3_3 · degrau 3 · achar_o_erro · codigo

Um colega diz que o segundo * é desnecessário. O que acontece sem ele?

```c
int a = 1, b = 2;
int* p, * q;
p = &a;
q = &b;
```

- **[certa]** q deixa de ser ponteiro e q = &b falha
- [estrela_e_do_tipo → nega B2] Nada: int* já vale para os dois
- [declaration_allocates → nega I1] q fica sem o apontado, e &b resolve

> É a pergunta 4.16 do FAQ, que é a fonte da crença. c traz o I1.

`revisado_por:` ________

---

## B3 — C não limpa a caixa nova. O que estava naquele lugar antes continua lá.

### kc03_gb3_n1_1 · degrau 1 · comparar_casos · teorica

Duas casas recém-entregues: numa a prefeitura passou para limpar, na outra não. Qual é a sua, em C?

- **[certa]** A segunda: ninguém passou
- [declaration_zeroes → nega B3] A primeira: vem limpa
- [uninitialized_is_null → nega I2] A primeira, com o papel em branco

> b é a crença do nó na analogia; c traz o vizinho I2, que é a mesma ideia na forma que ela toma num ponteiro.

`revisado_por:` ________

### kc03_gb3_n2_2 · degrau 2 · achar_o_erro · codigo

Por que o retorno é imprevisível?

```c
int conta(void) {
    int n;
    n++;
    return n;
}
```

- **[certa]** n começou com lixo, e o ++ soma nele
- [declaration_zeroes → nega B3] Não é: n começa em 0, e volta 1
- [uninitialized_is_null → nega I2] Não é: n começa em NULL, e vira 1

> b é a crença do nó; c traz o vizinho I2.

`revisado_por:` ________

### kc03_gb3_n3_3 · degrau 3 · prever_saida · codigo

Qual das duas saídas é previsível?

```c
static int g;
void f(void) { int n; printf("%d %d\n", g, n); }
```

- **[certa]** A primeira: g é estática
- [declaration_zeroes → nega B3] As duas: C zera o que declara
- [uninitialized_is_null → nega I2] A segunda: n vem em branco

> O contraste estática/automática é o que separa o caso em que o zero existe do caso em que não. b é a crença do nó; c traz o I2.

`revisado_por:` ________

---

## I1 — Então declarar p não cria a caixa apontada. Até aqui existe uma caixa só.

### kc03_gi1_n1_1 · degrau 1 · comparar_casos · teorica

Ganhar a casa de p com um papel dentro, e construir a casa que o papel aponta. int *p; faz quantas dessas?

- **[certa]** Uma: só a casa de p
- [declaration_allocates → nega I1] As duas, de uma vez
- [no_value_no_memory → nega B1] Nenhuma: falta o valor

> b é a crença do nó na analogia; c traz o vizinho B1.

`revisado_por:` ________

### kc03_gi1_n2_2 · degrau 2 · prever_saida · codigo

O que sai, e por que a mesma linha com p não funcionaria?

```c
int *p;
int *q = malloc(sizeof(int));
*q = 4;
printf("%d\n", *q);
```

- **[certa]** 4: só q ganhou uma caixa apontada
- [declaration_allocates → nega I1] 4, e com p funcionaria igual
- [declaration_zeroes → nega B3] 4, e p funcionaria por começar em 0

> O par p/q põe lado a lado o que tem caixa apontada e o que não tem. b é a crença do nó; c traz o vizinho B3.

`revisado_por:` ________

### kc03_gi1_n3_3 · degrau 3 · achar_o_erro · codigo

O que falta antes da segunda linha?

```c
char *nome;
strcpy(nome, "ana");
```

- **[certa]** Dar a nome um espaço que exista
- [declaration_allocates → nega I1] Nada: declarar nome já deu o espaço
- [declaration_zeroes → nega B3] Zerar nome, para o strcpy ter onde ir

> É a superfície do FAQ 7.10, que é a fonte da crença. c traz o B3.

`revisado_por:` ________

---

## I2 — Nesse ponto p guarda um valor qualquer, sobra do que estava ali. Não é NULL.

### kc03_gi2_n1_1 · degrau 1 · comparar_casos · teorica

Dois papéis dentro da casa nova: um em branco, outro com o rabisco do morador anterior. Qual é o seu?

- **[certa]** O do rabisco
- [uninitialized_is_null → nega I2] O em branco
- [declaration_zeroes → nega B3] Os dois, dependendo do dia

> b é a crença do nó na analogia; c traz o vizinho B3 na forma de quem acha que há um padrão garantido.

`revisado_por:` ________

### kc03_gi2_n2_2 · degrau 2 · prever_saida · codigo

Qual das duas comparações dá uma resposta em que se pode confiar?

```c
int *p;
int *q = NULL;
printf("%d %d\n", p == NULL, q == NULL);
```

- **[certa]** A segunda: você escreveu o NULL
- [uninitialized_is_null → nega I2] As duas: p também começa em NULL
- [declaration_zeroes → nega B3] As duas: C zera tudo que declara

> O par p/q separa o NULL escrito do NULL suposto. b é a crença do nó; c traz o vizinho B3.

`revisado_por:` ________

### kc03_gi2_n3_3 · degrau 3 · achar_o_erro · codigo

Por que o = NULL da segunda linha não é enfeite?

```c
int *acha(int v) {
    int *r = NULL;
    if (v > 0) r = malloc(sizeof(int));
    return r;
}
```

- **[certa]** Sem ele, r voltaria com lixo
- [uninitialized_is_null → nega I2] É enfeite: r já nasce NULL
- [declaration_zeroes → nega B3] É enfeite: r já nasce em zero

> b é a crença do nó; c traz o vizinho B3. O item mede a premissa pela utilidade de uma linha que só faz sentido se a crença for falsa.

`revisado_por:` ________

---

## I3 — Por isso usar *p antes de dar um endereço a p vai a um lugar que ninguém escolheu.

### kc03_gi3_n1_1 · degrau 1 · comparar_casos · teorica

Dois caminhos: seguir o rabisco do papel, ou primeiro escrever no papel o número de uma casa que existe. Qual é o válido?

- **[certa]** O segundo: o número foi escolhido
- [pode_usar_logo → nega I3] Os dois: o rabisco também leva
- [declaration_zeroes → nega B3] Nenhum: falta limpar o papel

> b é a crença do nó na analogia; c traz o vizinho B3.

`revisado_por:` ________

### kc03_gi3_n2_2 · degrau 2 · prever_saida · codigo

O que esse programa imprime?

```c
int *p;
printf("%d\n", *p);
```

- **[certa]** Não dá para dizer: p não aponta nada
- [pode_usar_logo → nega I3] O lixo de p, que é um valor como outro
- [uninitialized_is_null → nega I2] Zero: p ainda não foi usado

> b é a crença do nó: quem acha que já dá para usar espera uma saída definida. c traz o vizinho I2.

`revisado_por:` ________

### kc03_gi3_n3_3 · degrau 3 · achar_o_erro · codigo

Qual é a primeira linha inválida, e por quê?

```c
int *p;
int x = 5;
if (*p == 0) p = &x;
```

- **[certa]** A terceira: *p sem p ter endereço
- [pode_usar_logo → nega I3] Nenhuma: o if só lê, não escreve
- [declaration_zeroes → nega B3] A terceira: faltou zerar p antes

> b é a crença do nó na forma mais comum dela: ler pareceria inofensivo. c traz o vizinho B3.

`revisado_por:` ________

