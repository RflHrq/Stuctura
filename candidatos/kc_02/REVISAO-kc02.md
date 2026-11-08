# Revisão do material do kc_02 — os seis nós

**Segunda versão.** A primeira foi reprovada numa revisão independente,
e esta folha substitui as duas anteriores (`REVISAO-B2_material_1.md` e
`REVISAO-kc02-cinco.md`), cujas assinaturas estão vencidas.

| nó | assinatura |
| --- | --- |
| B1 | `df2b72b820cd` |
| B2 | `e26c16ff9fc9` |
| B3 | `f7124cc09e9d` |
| I1 | `abe7758e2007` |
| I2 | `ae61ca7435d0` |
| I3 | `1dc8026b0325` |

Para aprovar, escreva no cabeçalho do YAML correspondente:

```yaml
revisado_por: <seu nome>
revisado_sha: <a assinatura da linha acima>
```

## O que mudou da primeira versão para esta

### Seis itens saíram, porque eram duplicatas

Eu escrevi **doze** itens novos — dois por nó. Lendo o degrau 1 de cada
nó contra eles, **seis repetiam pergunta que já é domínio**:

| item que eu escrevi | o que já existia |
| --- | --- |
| B1: duas casas, mesmo móvel | `kc02_gb1_n1_1`: duas casas, sofás idênticos |
| B2: o papel e a casa 1000 | `kc02_gb2_n1_1`: quantas casas nessa história |
| B3: abrir o papel e ler 1000 | `kc02_gb3_n1_1`: basta ler o papel? |
| B3: o que há dentro de p | `ciu_kc02_007`: o que está guardado dentro de um ponteiro |
| I1: apagar o papel | `ciu_kc02_e4`: **o próprio item de entrada do nó** |
| I3: o vizinho e a planta | `ciu_kc02_e6`: **o próprio item de entrada do nó** |

Nos dois últimos eu reescrevi o item de entrada que já existia.

**A causa:** cada nó do kc_02 já tem **quatro** itens no degrau 1. Eu
tentei encaixar mais dois em cada, e num banco saturado o que sai é
paráfrase. Agora é **um por nó**, e o cabeçalho de cada arquivo diz qual
ângulo o banco não cobria.

**E um aviso sobre conferir isso:** medi a semelhança por trigramas e
ela **não serve**. O par mais grave — o meu item do I2 contra o
`ciu_kc02_014`, que é a mesma pergunta com a atribuição invertida — deu
**0.08**. Reuso de cenário é julgamento, não regex.

### As correções do I2, que foi reescrito por inteiro

1. **`atribuicao_entre_tipos` agora está declarado.** Ele está
   `nao_introduzido` no inventário e era a espinha do material, e eu
   tinha declarado só `tipo_do_ponteiro` e `sizeof`. A explicação que o
   libera foi movida do `caso_resolvido` para a **ampliação**, que é o
   único campo que entra no esquema de hoje.
2. **O `sizeof` saiu do I2.** Eu afirmava no cabeçalho que o arquivo o
   explicava, e não explicava — aparecia só como rótulo de número já
   medido. Quem o explica é o B2, e é lá que a promoção dele se
   justifica. A ampliação do B2 agora diz o que `sizeof` faz.
3. **O limite do kc_11 foi respeitado.** Eu dava "4 e 1 byte, que é
   exatamente sizeof(int) e sizeof(char)" e na frase seguinte dizia que
   o quanto era de outro tópico. Agora a aritmética aparece só como
   menção de que o comportamento difere, sem número.
4. **A evidência principal mudou** por causa disso: não é mais `p + 1`,
   é `int *p` recebendo um `char *`. Dois ponteiros, os dois guardando
   endereço, e o compilador recusando trocar um pelo outro — evidência
   de tipo sem tocar em aritmética.
5. **"Não é aviso, é erro" virou "reclama".** Medido nesta máquina:

   ```
   gcc -std=c17 -Wall                             -> error,   sem .exe
   gcc ... -Wno-error=int-conversion              -> warning, com .exe
   gcc ... -Wno-error=incompatible-pointer-types  -> warning, com .exe
   ```

   É erro porque o gcc ≥ 14 promoveu esses avisos. Num laboratório com
   compilador mais antigo o programa compila, e quem responder lá não
   teria alternativa certa para marcar. O verbo "reclama" é o que o
   próprio `ciu_kc02_014` já usa.

### Prosa e código viraram blocos separados

`caso_resolvido` e `reexplicacao` eram texto corrido com código no meio.
A única tubulação de texto de ensino do projeto é `_paragrafos`
(`mvp/dominio.py`), que preserva linha em branco e **colapsa o resto** —
rodei o texto por ela e as linhas de código saíram grudadas numa só.
Agora cada campo é uma lista de blocos `prosa:`, `codigo:` ou `saida:`,
e a tela desenha cada um do seu jeito.

### A reexplicação do I2 foi trocada

A primeira estreava, **na tela de quem acabou de dizer que não
entendeu**: array, decaimento de array para ponteiro, dois casts para
`char *`, subtração de ponteiros e `%td` — nenhum deles disponível no
inventário. A nova usa só o que o tópico já tem.

## O tamanho, agora

| nó | palavras de ensino | itens de entrada |
| --- | --- | --- |
| B1 | 207 → **419** | 1 → 2 |
| B2 | 86 → **500** | 1 → 2 |
| B3 | 248 → **569** | 1 → 2 |
| I1 | 86 → **512** | 1 → 2 |
| I2 | 99 → **558** | 1 → 2 |
| I3 | 85 → **595** | 1 → 2 |
| **kc_02** | **811 → 3.465** | **6 → 12** |

## O que a máquina conferiu

**Oráculo (gcc 16.2.0, `-std=c17 -Wall -Wextra`):**

```
B1  &idade == &outra -> 0        a=20, b=20, &a==&b -> 0
B2  &x != &p    sizeof(p)=8, sizeof(x)=4, 8 para int*/char*/double*
B3  *p -> 42                     x depois de *p = 7 -> 7
I1  q=&b; *q=99  ->  a = 42, b = 99        &a == &b -> 0
I2  int *p = x;   -> "makes pointer from integer without a cast"
I2  p = q (int*, char*) -> "incompatible pointer type 'char *'"
I3  dobra(&n) -> n = 20          dobra_valor(m) -> m = 10
```

**Conferidor, nos seis itens:** três alternativas, a certa não é a mais
longa, todo distrator aponta crença existente, nenhum id colide com os
60 do domínio, nenhum enunciado afirma severidade de compilador, e
`caso_resolvido`/`reexplicacao` são blocos em todos os seis. **Nenhum
problema.**

## As três decisões que continuam suas

1. **O I3 depende de `funcao_com_parametro`**, que está
   `nao_introduzido`. O material introduz o conceito pelo contraste
   valor/endereço. Aprovar isso destrava também o degrau do `scanf`.
2. **As inferências não têm cartão de ensino.** A abertura ensina três;
   I1, I2 e I3 só aparecem para quem declara lacuna. Com este material
   poderiam ser seis — muda o desenho e o comprimento da unidade.
3. **Quatro conceitos mudariam de status** se os arquivos forem
   aprovados: `atribuicao_entre_tipos` e `funcao_com_parametro` saem de
   `nao_introduzido`; `sizeof` e `tipo_do_ponteiro`, de `so_avaliado`. O
   inventário tem de ser atualizado junto, com a evidência apontando
   para os arquivos.

## O que fica para a sua leitura

- A **regra da seta** em cada linha dos seis.
- **No B1, nenhum ponteiro** pode aparecer.
- **No B2, nenhuma derreferência** (`*p` é o B3).
- **No I2, a metáfora cala** sobre aritmética de ponteiro. Veja se o
  limite ficou claro agora.
- Cada distrator é a crença **dita bem**? Alguém escolheria aquilo?
- E a pergunta que o conferidor não responde: algum dos seis itens novos
  repete, em outras palavras, pergunta que a pessoa já vai ter visto?

## O que entra sem mexer em código

**Entra hoje:** as três ampliações novas (I1, I2, I3) e os seis itens.

**Não entra:** `narracao`, `caso_resolvido` e `reexplicacao`. Agora que
são blocos, a mudança é menor do que era — o carregador precisa aceitar
a lista e a tela precisa desenhar código como código.

## As descidas

As seis crenças do kc_02 têm descida escrita. Mas **ter passos não é
poder rodar**: a de `pointer_and_target_are_one` está **reprovada** em
`aprovacoes.yaml`, e a de `pointer_is_integer` declara
`requer: [atribuicao_entre_tipos, compilacao]` — os dois conceitos que
este material introduziria. E nenhuma delas está aprovada; o padrão é
`sem_revisao`.
