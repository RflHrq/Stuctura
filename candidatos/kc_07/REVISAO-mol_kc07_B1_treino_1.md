# Revisão do molde — mol_kc07_B1_treino_1

Uma revisão deste arquivo vale por todas as variações dele, em
todos os formatos. Para aprovar, escreva no molde as DUAS linhas
abaixo — o nome diz quem leu, e a assinatura diz O QUE foi lido:

```yaml
  revisado_por: <seu nome>
  revisado_sha: 89a6e44c4662
```

A assinatura é do conteúdo que está nesta folha. Se o molde mudar
depois, ela deixa de bater e a carga recusa, em vez de estampar o
seu nome em variações que você não leu. Depois:

```bash
python scripts/gerar.py --topico kc_07 --molde mol_kc07_B1_treino_1 --expandir
python scripts/gerar.py --topico kc_07 --aprovar
```

**O que a máquina já conferiu:** que o programa do oráculo de cada
formato compila, roda e diz o que o molde promete — em 64
combinações de parâmetro por formato, que é o domínio inteiro.
O que fica para você é o resto:

- a frase fecha em português em todas elas (plural, gênero, acento);
- cada distrator é a crença **dita bem** — alguém escolheria aquilo;
- o enunciado não entrega a resposta;
- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue.

---

## A afirmação

**nó B1** · degrau 1 · uso treino

As crenças são da afirmação, e valem para todos os formatos — em
cada um, os distratores vêm nesta ordem:

- `array_confused_with_cell` → nega B1
- `array_is_pointer` → nega I3

parâmetros:

- `tipo`: int, char, double, long
- `nome`: a, v, dados, lista
- `n`: 3, 4, 6, 8

oráculo da família, que espera `{n} 1`:

```c
#include <stdio.h>
int main(void) {
    {tipo} {nome}[{n}];
    printf("%zu %td\n",
           sizeof {nome} / sizeof {nome}[0],
           &{nome}[1] - &{nome}[0]);
    return 0;
}
```

---

## formato: reconhecer_conceito

### variação 1 — n=3, nome=a, tipo=int

Depois de int a[3]; e nada mais, o que existe na memória?

- **[certa]** São três caixas de int, grudadas
- [array_confused_with_cell] É uma caixa só, com três valores de int guardados dentro
- [array_is_pointer] É um ponteiro, que depois aponta para três valores de int

### variação 2 — n=8, nome=a, tipo=int

Depois de int a[8]; e nada mais, o que existe na memória?

- **[certa]** São oito caixas de int, grudadas
- [array_confused_with_cell] É uma caixa só, com oito valores de int guardados dentro
- [array_is_pointer] É um ponteiro, que depois aponta para oito valores de int

### variação 3 — n=3, nome=a, tipo=double

Depois de double a[3]; e nada mais, o que existe na memória?

- **[certa]** São três caixas de double, grudadas
- [array_confused_with_cell] É uma caixa só, com três valores de double guardados dentro
- [array_is_pointer] É um ponteiro, que depois aponta para três valores de double


---

## formato: achar_o_erro

oráculo próprio, que espera a RECUSA do compilador:

```c
int main(void) {
    {tipo} {nome}[{n}];
    {tipo} *p = {nome};
    {nome} = p;
    return 0;
}
```

### variação 1 — n=3, nome=a, tipo=int

```c
int a[3];
int *p = a;
a = p;
```

Uma destas linhas não compila. Qual, e por quê?

- **[certa]** A terceira: o nome de um array não recebe atribuição
- [array_confused_with_cell] A segunda: a e p guardam do mesmo jeito, e é ali que está o erro
- [array_is_pointer] Nenhuma delas: a já é um ponteiro, e as três linhas valem


---

## formato: comparar_casos

oráculo próprio, que espera `{n} 1`:

```c
#include <stdio.h>
int main(void) {
    {tipo} {nome}[{n}];
    {tipo} *p;
    printf("%zu %d\n",
           sizeof {nome} / sizeof {nome}[0],
           (int)(sizeof p == sizeof(void *)));
    return 0;
}
```

### variação 1 — n=3, nome=a, tipo=int

```c
int a[3];
int *p;
```

O que existe na memória depois destas duas linhas?

- **[certa]** São três caixas de int, e uma caixa de ponteiro
- [array_confused_with_cell] São três valores nos dois casos, guardados do mesmo jeito
- [array_is_pointer] São duas caixas de ponteiro: a também é um ponteiro

