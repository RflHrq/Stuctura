# Revisão dos candidatos — kc_04

**18 itens**, em 6 nós.

Leia item a item. Para aprovar, escreva seu nome em `revisado_por`
no arquivo `.yaml` do nó e rode:

```bash
python scripts/gerar.py --topico kc_04 --aprovar
```

Só entra no domínio o que tiver `revisado_por` preenchido.

**O que conferir em cada item** (docs/linguagem.md):

- a resposta certa está certa, e as erradas estão erradas;
- cada distrator é a crença **dita bem** — alguém escolheria aquilo;
- o enunciado não entrega a resposta;
- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue;
- o código compila e faz o que o enunciado diz.

---

## B1 — Só tem número de casa o que ocupa uma casa. Um valor escrito no código não ocupa nenhuma.

### kc04_gb1_n1_1 · degrau 1 · comparar_casos · teorica

Dois pedidos ao carteiro: entregar na casa de x, e entregar na conta 2+3. Qual deles ele cumpre?

- **[certa]** O primeiro: só a casa de x é da rua
- [ampersand_takes_value → nega B1] Os dois: toda coisa tem um lugar
- [ampersand_copies → nega B2] O primeiro, e ele leva uma cópia

> b é a crença do próprio nó dita na analogia: se toda coisa tem lugar, o 5 do código teria endereço. c traz o vizinho B2.

`revisado_por:` ________

### kc04_gb1_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int n = 3;
int *p = &n;
printf("%d %d\n", *p, p == &n);
```

- **[certa]** 3 1: n tem lugar e p tem o número
- [ampersand_takes_value → nega B1] 3 0: &n muda a cada uso
- [ampersand_copies → nega B2] 3 1, e p guarda uma cópia do 3

> b nega que o endereço seja propriedade estável do lugar; c troca endereço por cópia, que é o vizinho B2.

`revisado_por:` ________

### kc04_gb1_n3_3 · degrau 3 · achar_o_erro · codigo

O que impede a chamada, e como corrigir?

```c
int troca(int *a, int *b);
int x = 1;
troca(&x, &2);
```

- **[certa]** &2: crie uma variável e passe o dela
- [ampersand_takes_value → nega B1] Nada impede: &2 é o endereço do 2
- [ampersand_copies → nega B2] &x: devia ser x, que já é o valor

> A resposta certa é a do próprio FAQ 4.10, que é a fonte da crença: declarar uma temporária e passar o endereço dela.

`revisado_por:` ________

---

## B2 — &x responde o número da casa de x. Nada é copiado: você recebe o número, não o que está guardado.

### kc04_gb2_n1_1 · degrau 1 · comparar_casos · teorica

Você pede o número da casa de x; seu vizinho pede emprestado o que está dentro dela. Qual dos dois mexe na casa?

- **[certa]** O segundo: o número não tira nada
- [ampersand_copies → nega B2] Os dois: pedir o número já copia
- [pointer_is_just_a_name → nega I1] Nenhum: a casa é só um apelido

> b é a crença do nó na analogia: perguntar o número levaria uma cópia. c traz o vizinho I1.

`revisado_por:` ________

### kc04_gb2_n2_2 · degrau 2 · achar_o_erro · codigo

O que está errado na chamada?

```c
void soma_um(int *n) { *n = *n + 1; }
int x = 5;
soma_um(x);
```

- **[certa]** Falta &: a função quer o endereço
- [ampersand_copies → nega B2] Nada: a cópia de x já serve à função
- [star_assigns_pointer → nega I3] Falta *: seria soma_um(*x)

> b é a crença do nó; c traz o vizinho I3, de quem acha que o * da expressão designa o ponteiro.

`revisado_por:` ________

### kc04_gb2_n3_3 · degrau 3 · prever_saida · codigo

O que sai?

```c
void f(int *n) { *n = 100; }
int x = 1;
int y = x;
f(&x);
printf("%d %d\n", x, y);
```

- **[certa]** 100 1: só x foi alcançada
- [pointer_is_just_a_name → nega I1] 100 100: y é outro nome de x
- [ampersand_copies → nega B2] 1 1: f recebeu uma cópia de x

> c é a crença do nó: se &x entregasse cópia, f não alcançaria x. b traz o vizinho I1.

`revisado_por:` ________

---

## B3 — O que está escrito no papel dentro de p é um número de casa.

### kc04_gb3_n1_1 · degrau 1 · comparar_casos · teorica

Dois papéis: um com 42 escrito, outro com o número de uma casa. Qual deles está dentro de p?

- **[certa]** O segundo: um número de casa
- [pointer_is_data → nega B3] O primeiro: p guarda o 42
- [pointer_is_just_a_name → nega I1] Nenhum: p não guarda papel

> b é a crença do nó dita na analogia; c traz o vizinho I1, de quem acha que p é só um nome.

`revisado_por:` ________

### kc04_gb3_n2_2 · degrau 2 · achar_o_erro · codigo

Por que o compilador avisa nesta linha?

```c
int x = 5;
int *p = &x;
printf("%d\n", p);
```

- **[certa]** p é endereço, e %d espera um int
- [pointer_is_data → nega B3] Não avisa: dentro de p está o 5
- [ampersand_takes_value → nega B1] Falta o &: seria &p

> b é a crença do nó; c traz o vizinho B1.

`revisado_por:` ________

### kc04_gb3_n3_3 · degrau 3 · prever_saida · codigo

O que sai?

```c
int x = 1, y = 2;
int *p = &x;
int *q = &y;
printf("%d\n", *p + *q);
```

- **[certa]** 3: *p é 1 e *q é 2
- [pointer_is_data → nega B3] a soma dos dois endereços
- [pointer_is_just_a_name → nega I1] 3, e p e q são x e y

> b é a crença do nó com o sinal trocado: quem acha que o ponteiro é o dado não separa somar conteúdo de somar endereço. c traz o I1.

`revisado_por:` ________

---

## I1 — Então *p é a viagem: vai até o número do papel e mexe no que tem naquela casa.

### kc04_gi1_n1_1 · degrau 1 · comparar_casos · teorica

Ler o número no papel de p, e ir até a casa daquele número. São a mesma coisa?

- **[certa]** Não: a segunda é a viagem
- [pointer_is_just_a_name → nega I1] São: p e a viagem são um só
- [pointer_is_data → nega B3] São: as duas devolvem o número

> b é a crença do nó na analogia; c traz o vizinho B3.

`revisado_por:` ________

### kc04_gi1_n2_2 · degrau 2 · achar_o_erro · codigo

O que falta para imprimir o valor apontado?

```c
void mostra(int *p) { printf("%d\n", p); }
```

- **[certa]** O *: printf com *p
- [pointer_is_just_a_name → nega I1] Nada: p já é o valor
- [ampersand_takes_value → nega B1] O &: printf com &p

> b é a crença do nó; c traz o vizinho B1.

`revisado_por:` ________

### kc04_gi1_n3_3 · degrau 3 · comparar_casos · codigo

Qual dos dois virou 9, e por quê?

```c
int a = 1, b = 1;
int *p = &a;
*p = 9;
/* A */  a
/* B */  b
```

- **[certa]** A: p tinha o endereço de a
- [pointer_is_just_a_name → nega I1] Os dois: *p é o nome dos dois
- [star_binds_to_the_pointer → nega I2] B: *p andou para a casa seguinte

> b é a crença do nó; c traz o vizinho I2, de quem confunde agir através de p com andar com p.

`revisado_por:` ________

---

## I2 — *p = 7 troca o que tem dentro da casa visitada. O papel de p não muda.

### kc04_gi2_n1_1 · degrau 1 · comparar_casos · teorica

Trocar o que tem dentro da casa visitada, e reescrever o papel de p. Qual das duas *p = 7 faz?

- **[certa]** A primeira: troca o conteúdo
- [star_binds_to_the_pointer → nega I2] A segunda: reescreve o papel
- [star_assigns_pointer → nega I3] Nenhuma: quem recebe valor é p

> b é a crença do nó na analogia; c traz o vizinho I3.

`revisado_por:` ________

### kc04_gi2_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int x = 4;
int *p = &x;
*p += 3;
printf("%d %d\n", x, p == &x);
```

- **[certa]** 7 1: o += somou no conteúdo
- [star_binds_to_the_pointer → nega I2] 4 0: o += somou no endereço
- [pointer_is_data → nega B3] 7 0: p passou a guardar o 7

> b é a crença do nó com a superfície do FAQ 4.3; c traz o vizinho B3.

`revisado_por:` ________

### kc04_gi2_n3_3 · degrau 3 · achar_o_erro · codigo

Por que a terceira linha não compila?

```c
int a = 1, b = 2;
int *p = &a;
*p = &b;
```

- **[certa]** *p é um int, e &b é um endereço
- [star_assigns_pointer → nega I3] Compila: *p é onde o endereço vai
- [star_binds_to_the_pointer → nega I2] Compila: *p = &b só move p

> c é a crença do nó; b traz o vizinho I3, que é a conclusão do tópico e a pergunta 4.2 do FAQ.

`revisado_por:` ________

---

## I3 — & pergunta onde está, * vai até lá. Um desfaz o outro, e *(&x) é a própria x.

### kc04_gi3_n1_1 · degrau 1 · comparar_casos · teorica

Você pergunta o número da casa de x e vai até ele. E se fizer na ordem contrária?

- **[certa]** Volta ao mesmo lugar: x
- [star_assigns_pointer → nega I3] Dá outra casa, parecida
- [ampersand_copies → nega B2] Dá uma cópia da casa de x

> b é a crença do nó na analogia: se * e & não fossem inversos, a ida e a volta não fechariam. c traz o vizinho B2.

`revisado_por:` ________

### kc04_gi3_n2_2 · degrau 2 · prever_saida · codigo

O que sai?

```c
int x = 2;
int *p = &x;
printf("%d %d\n", *(&x), *p);
```

- **[certa]** 2 2: as duas chegam em x
- [star_assigns_pointer → nega I3] o endereço de x, duas vezes
- [ampersand_copies → nega B2] 2 2, mas o segundo é uma cópia

> b é a crença do nó; c traz o vizinho B2.

`revisado_por:` ________

### kc04_gi3_n3_3 · degrau 3 · achar_o_erro · codigo

Por que a terceira linha não compila?

```c
int *p;
int x = 3;
&p = &x;
```

- **[certa]** &p não é um nome que recebe
- [star_assigns_pointer → nega I3] Compila: &p é onde p guarda
- [pointer_is_just_a_name → nega I1] Compila: &p e p dão no mesmo

> b é a crença do nó; c traz o vizinho I1.

`revisado_por:` ________

