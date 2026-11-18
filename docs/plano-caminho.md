# Plano — o caminho na página inicial e o voltar sem código

Desenho: `docs/interface.md` seção 7 (o caminho, decidido pelo Rafael em
14 e 16/11/2026) e `docs/trilha.md` seção 6.12 (parar e voltar). Pedido
do Rafael em 18/11/2026: o sistema completo para apresentar ao
orientador. Execução inline, tarefa por tarefa, teste antes do código.

## Restrições que vêm de testes antigos

- Só `mvp/conceitos.py` cita o campo `prerequisites`
  (`test_so_o_portao_de_exibicao_le_o_prerequisito`), e o domínio
  carregado não o guarda. Por isso a ordem mora em
  `mvp/dominio/caminho.yaml`, lida por `mvp/caminho.py`, e quem confere
  que cada tópico vem depois dos pré-requisitos é o **teste**.
- O cartão "Próximo sugerido" não diz "depende de" (estava no esboço, não
  no texto do desenho): dizer exigiria um segundo leitor do grafo.
- `portal.html` continua montando a lista com `t.trilha`, `t.caminho` e
  o link "versão anterior" (`test_trilha_portal`).
- `test_interface::test_a_pagina_inicial_tem_o_logo_o_titulo_e_o_tema`
  (deste ramo) proibia "ordem sugerida" enquanto o caminho não existia;
  muda de propósito, e o commit diz.

## Tarefas

1. **A ordem.** `mvp/dominio/caminho.yaml` (a ordem da seção 7, com um
   rótulo curto por tópico, que é o que a trilha desenhada escreve ao lado
   de cada parada) e `mvp/caminho.py` (`ordem()`, `rotulos()`). Teste:
   todo tópico uma vez, cada um depois de todos os pré-requisitos.
2. **`/topicos` na ordem do caminho**, com `rotulo` em cada tópico.
3. **Retomar pelo número.** `POST /trilha/<t>/sessoes/<sessao>/retoma`:
   da memória (grava `sessao_retomada`), refeita pelo registro (grava
   `sessao_reconstruida`), 404 se não existe, 410 se não dá para refazer.
4. **O navegador lembra.** `mvp/web/progresso.js` (`Progresso.le/grava/
   apaga`, por tópico, com `localStorage` protegido): a trilha grava a
   sessão de quem não informou código, quantas ideias fechou e se chegou
   ao fechamento; ao abrir sem código, retoma; 404 abre outra; 410 mostra
   a frase. "Fazer de novo" e "Recomeçar" apagam o guardado.
5. **O caminho desenhado.** `mvp/web/caminho.js`: `estados(ordem,
   guardados)` (feito, andamento "3 de 6", próximo, aberto — puro, com
   teste em Node) e o desenho em SVG com as cores do tema; `portal.html`
   com o cartão "Próximo sugerido" (Começar ou Continuar), a legenda, a
   trilha, e a lista de todos os tópicos abaixo, com "versão anterior".
   Movimento só com "reduzir movimento" desligado.
6. **Conferência no navegador** (servidor de ensaio, 8013): tela larga e
   360 px, os dois temas; um tópico começado sem código, a página
   fechada, o tópico reaberto na mesma tela; a página inicial mostrando
   o andamento.

## Estado

- [x] 1 · [x] 2 · [x] 3 · [x] 4 · [x] 5 · [x] 6 — feito em 18/11/2026; a
  conferência no navegador (servidor de ensaio) passou em tela larga, em
  360 px e nos dois temas, e a sessão sem código voltou no mesmo passo,
  inclusive depois de o servidor reiniciar.
