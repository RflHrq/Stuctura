# Apresentação da defesa — desenho

Aprovado pelo Rafael em 25/11/2026 ("Tá bom assim, pode começar a
montar"), depois de escolher a opção 1 entre três.

## Para que serve

A defesa do TCC tem 30 minutos de apresentação. A banca precisa entender
o Structura funcionando: a pergunta com resposta, razão e certeza, o
diagnóstico, a escada, a demonstração e a cena. O Rafael quer slides, e
não o sistema ao vivo ("na hora de apresentar vai dar uns problemas"),
no próprio notebook.

## A regra que manda em tudo

Tudo o que um slide explica está na monografia entregue (commit
`cf51987`), e o slide diz onde, **na numeração do PDF** (Quadro 1 a 24,
Figura 1 a 6, Seções 1 a 8, apêndices A a C), que é a que a banca tem na
mão. Número ou frase do texto aparece no slide como o texto diz, sem
arredondar nem simplificar. Isso é conferido por programa, como os
números da monografia: um teste falha se o slide citar uma referência
que o PDF não tem, um número que o texto não traz ou uma frase entre
aspas que o texto não contém.

Fica de fora: qualquer afirmação nova sobre o sistema, qualquer resultado
com estudantes (não houve coleta) e qualquer número medido depois da
entrega.

## Abordagens consideradas

1. **Slides em HTML no navegador, com PDF de reserva** — escolhida. Um
   arquivo que abre sem internet, em tela cheia, avançado pela seta. Os
   slides do sistema são interativos: a tela se monta aos poucos, e a
   cena roda com o `cena.js` do próprio Structura.
2. PowerPoint com telas e vídeos gravados — abre em qualquer lugar, mas
   a cena vira vídeo, sem passo a passo.
3. Slides do claude.ai baixados como PowerPoint ou PDF — rápidos e
   limpos, mas estáticos.

## O roteiro (22 slides)

| # | Slide | Onde está |
|---|---|---|
| 1 | Capa | folha de rosto |
| 2 | O problema: errar não diz por quê | Seção 1.1 |
| 3 | Pergunta de pesquisa e escopo | Seção 1.5 |
| 4 | Objetivos | Seção 1.4 |
| 5 | Fundamentação | Seção 2 |
| 6 | Trabalhos relacionados | Quadro 1 |
| 7 | O domínio: 13 tópicos, 79 premissas | Seção 3.1, Quadro 2 |
| 8 | ▶ A pergunta: resposta, razão e certeza | Figura 1 |
| 9 | ▶ O diagnóstico escolhe o caminho | Quadro 3 |
| 10 | ▶ A escada | Seção 3.4, Figura 2 |
| 11 | ▶ "Você disse" / "A máquina respondeu" | Figura 4 |
| 12 | ▶ A cena, animada linha a linha | Figura 5 |
| 13 | ▶ O fechamento | Figura 3 |
| 14 | Curadoria: de onde vem cada concepção | Seção 4 |
| 15 | Como foi verificado | Seção 5 |
| 16 | Resultados: o compilador e os perfis | Seções 6.2 e 6.3 |
| 17 | Defeitos que a verificação achou | Seção 6.4 |
| 18 | Limitações | Seção 7.1 |
| 19 | Trabalhos futuros | Seção 7.2 |
| 20 | Conclusão | Seção 8 |
| 21 | Repositório e uso de IA | declaração de uso de IA |
| 22 | Obrigado / perguntas | — |

▶ = interativo: cada toque na seta revela o próximo elemento da tela.

## Como se faz (decisões do construtor, para o Rafael conferir)

- Pasta `apresentacao/` no repositório: `index.html`, um CSS e um JS do
  próprio deck. O deck usa, por caminho relativo, as fontes, o
  `tema.css`, o `realce.js` e o `cena.js` de `mvp/web/`, de modo que a
  identidade visual e a cena são as do sistema, sem cópia que possa
  divergir.
- As imagens são as figuras da monografia (`docs/monografia/figuras/`).
  A cena do slide 12 é a da Figura 5 (kc_06, premissa B1), exportada do
  domínio por um script para um arquivo de dados do deck.
- Cada slide traz no rodapé a referência ao PDF ("Seção 3.3 · Quadro 3").
- Teclas: → e espaço avançam, ← volta, F tela cheia. Funciona sem
  internet.
- O PDF de reserva sai do próprio HTML, por Chrome sem janela, com cada
  passo dos slides interativos já revelado.
- Notas do apresentador: um texto curto por slide, fora da tela, com o
  que dizer e a resposta das perguntas da banca que aquele slide puxa.
- Conferência: `scripts/confere_apresentacao.py` e
  `mvp/test_apresentacao.py` leem os slides e conferem referências
  (contra os `.toc`, `.lof` e `.lot` do LaTeX), números e frases entre
  aspas (contra o texto da monografia).
