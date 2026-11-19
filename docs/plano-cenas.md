# Plano — as cenas (fatia 3 do desenho da interface)

Desenho: `docs/interface.md`, seção 8 (aprovado pelo Rafael em 14 e
16/11/2026; a escolha 2: cena em dados, um desenhista que anima todas, e
a conferência contra o compilador). Esta fatia é a 3 da seção 9: o
formato, a conferência, o desenhista com os personagens da primeira leva
e **as cinco cenas do kc_00 — o Rafael olha antes de seguir** para os
outros doze tópicos (fatia 4) e para as cenas das provas (fatia 5).

## O formato (decisão minha, como a seção 8.3 deixa ao construtor)

No bloco da premissa, ao lado de `revisao`:

```yaml
cena:
  atores:
    - {nome: idade, tipo: caixa, de: int}
  passos:
    - {linha: 1, faz: [{cria: idade}]}
    - {linha: 2, faz: [{guarda: {em: idade, valor: 20}}]}
    - {linha: 3, faz: [{le: idade}, {mostra: "20"}]}
```

Ações: `cria`, `guarda {em, valor}`, `le`, `mostra`, `aponta {de, para}`,
`nulo`, `segue`, `some`. O valor é escrito como no C (`20`, `'A'`).

## A conferência (seção 8.3)

`scripts/confere_escada.py` monta um segundo programa com o código da
revisão e, depois de cada linha, as afirmações da cena naquele passo, em
C: `idade == 20`, `p == &x`, `p == NULL`. O que falha sai em stderr e
vira problema; a saída do programa tem de ser a da revisão e a soma dos
`mostra`. Mais: toda linha tem passo, nenhum passo aponta para linha que
não existe, todo ator citado existe, `le` não lê caixa sem valor, e
endereço nunca é conferido pelo número. Código com função fica para a
fatia 4 (a bancada), e a conferência acusa em vez de calar.

## Decisões minhas, para o Rafael conferir

- **A cena não entra na assinatura do conteúdo.** A assinatura existe
  para não refazer uma sessão contra outra escada (as entradas são
  posições de peças); a cena não muda entrada nenhuma. Sem isso, cada
  cena nova tornaria impossível retomar as sessões já gravadas.
- **Onde aparece:** na revisão (que é também o que vem depois do erro na
  pergunta de topo) e no painel "Ver a explicação". A cena traz o código
  com a linha que roda marcada, e por isso toma o lugar do bloco de
  código ali; no painel, toma o lugar da figura antiga.
- **Personagens desta fatia:** caixa, bilhete (ponteiro) e NULL, que o
  kc_00 e os próximos tópicos usam. Fileira, bancada e bloco alugado
  entram na fatia 4, com o retorno do Rafael sobre as do kc_00.

## Tarefas

1. Formato e leitura (`trilha_escada`: `Cena`, `Ator`, `PassoCena`), com
   as conferências de estrutura; a cena fora da assinatura.
2. A conferência contra o compilador (`confere_escada`).
3. O servidor manda a cena na revisão e na explicação.
4. O desenhista (`mvp/web/cena.js`): os estados passo a passo (puro,
   testado no Node), o desenho em SVG, os controles (pausar, passo a
   passo, rever), o texto para leitor de tela, e reduzir movimento.
5. As cinco cenas do kc_00, conferidas.
6. Conferência no navegador (ensaio, 8013), nos dois temas e em 360 px.

## Estado

- [x] 1 · [x] 2 · [x] 3 · [x] 4 · [x] 5 · [x] 6 — feito em 18/11/2026. As
  cinco cenas do kc_00 conferem contra o compilador; a conferência no
  navegador passou nos dois temas e em 360 px, com o ponteiro e o NULL
  vistos numa cena de teste. O Rafael olhou e pediu a fatia 4 (abaixo).

## Fatia 4 — as cenas dos outros doze tópicos

Pedido do Rafael em 18/11/2026, depois de ver as do kc_00 ("pode seguir
com as cenas dos outros tópicos"; a cena maior no computador já entrou).

### O que as 74 revisões pedem

- **bancada** (função): a execução entra na função, linha a linha, e
  volta. O passo pode repetir linha e voltar no código (é o rastro da
  execução). Ator `{tipo: bancada, de: "void zera(int n)"}`; ações
  `chama` e `volta`; quem nasce entre as duas é da bancada e some na
  volta, menos o ator com `fica: true` (o `static` do kc_12).
- **fileira** (array): `{tipo: fileira, tamanho: 3}` ou `tamanho: [2, 3]`
  (a matriz); `guarda {em: "notas[2]", ...}` e `aponta {para:
  "notas[1]"}`. Texto entra como fileira de char, com `'\0'` no fim.
- **bloco alugado** (`malloc`): `{tipo: bloco, de: int}` (ou com
  `tamanho`); `aluga {nome: bloco, para: p}` cria o bloco no monte e põe
  o endereço em p; `devolve: bloco` (o `free`) tira a placa. Depois do
  `free` nada do bloco é lido nem comparado (seria o que o kc_09 ensina a
  não fazer).
- **diz**: uma frase a mais no passo, para o que não é estado de caixa
  (o `if` que não entra, o `sizeof`, a conta de ponteiro). Não afirma
  nada que precise de conferência.

### A conferência com função (seção 8.3)

Cada ator tem o endereço guardado numa variável global do programa da
conferência logo que nasce (`cena_e_x`; a do bloco, logo depois do
`malloc`), e TODA afirmação passa por esse endereço, a de valor também:
`*(int *)cena_e_idade == 15`, `*(int **)cena_e_p == (int *)cena_e_idade`.
Assim ela vale dentro da bancada e fora dela, e no monte, onde a caixa
não tem nome.

Onde a afirmação entra: depois da linha, no `main` e na função de várias
linhas (antes, se a linha é `return` ou o `}` do fim); na função de uma
linha, antes do `return` ou do `}` final — e aí a cena afirma o estado
final daquela chamada; e no começo do corpo, o estado de quando a bancada
abre (os parâmetros com a cópia). A mesma linha roda de novo quando a
função é chamada de novo: cada passagem é uma VISITA, com um contador no
programa, e cada visita confere o seu estado — é assim que a segunda
chamada do `conta` é conferida à parte da primeira. No fim do `main`, o
programa confere quantas vezes passou por cada ponto: a cena que conta
outra história de chamadas (a função que não roda, a que roda duas
vezes) é acusada.

O que a estrutura da cena já recusa, antes do compilador
(`trilha_escada.toca`): citar caixa que já sumiu, ler caixa sem valor,
seguir bilhete de NULL, de caixa que sumiu ou de bloco devolvido, voltar
de bancada que não é a aberta, a linha de uma função rodando fora da
bancada dela, e terminar com bancada aberta.

### Progresso, tópico a tópico

Todas escritas e conferidas em 18/11/2026 (`python
scripts/confere_escada.py kc_XX`, 0 problemas em cada um):

| tópico | ideias | personagens novos |
| --- | --- | --- |
| kc_01 | 5 | bancada (o `conta` chamado duas vezes), bloco |
| kc_02 | 6 | bancada (`zera(&idade)`) |
| kc_03 | 6 | — |
| kc_04 | 6 | — |
| kc_05 | 6 | `diz` (o `if` que não entra) |
| kc_06 | 6 | bancada: a cópia muda, o original não |
| kc_07 | 7 | fileira, e a bancada que recebe o endereço da primeira caixa |
| kc_08 | 6 | bloco, e o bloco que sobrevive à volta da função |
| kc_09 | 8 | bloco devolvido; dois aluguéis seguidos |
| kc_10 | 6 | ponteiro para ponteiro, `void *`, matriz 2 × 3 |
| kc_11 | 6 | fileira de char com o `'\0'` |
| kc_12 | 6 | função de várias linhas; o `static` que fica |
