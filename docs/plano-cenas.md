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
  vistos numa cena de teste. **Aguarda o Rafael olhar** antes da fatia 4.
