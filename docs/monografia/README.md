# A monografia — roteiro e estado

O texto do TCC, um arquivo por capítulo. A formatação no modelo da UFV
(ABNT, em Word ou LaTeX) vem por último, quando o modelo estiver em mãos:
o conteúdo não depende dele.

**O recorte (decidido pelo Rafael em 18/11/2026):** o trabalho descreve a
construção e a verificação do sistema, sem estudo com estudantes. A
pergunta "estudantes conseguem e querem completar a sessão?" vai para
trabalhos futuros, com o protocolo do estudo pronto em apêndice. Se a
coleta acontecer depois, os resultados entram num capítulo próprio.

**A versão descrita** é a do ramo `trilha` em 19/11/2026 (commit
`2a549a2`): os treze tópicos na trilha, com a conferência do banco contra
o compilador, as 79 cenas que animam a revisão de cada premissa
(`b8a02bc`), as duas passadas da leitura das perguntas (`0e4f522` e
`ebb0b82`, registro em `docs/pente-dos-degraus.md`), o caminho na página
inicial, a volta sem código, o sair da sessão (guardar ou cancelar) e o
"Confirmar resposta" antes do porquê (`2a549a2`). Os números do texto
foram tirados do sistema por script, e não de memória, e
`mvp/test_monografia.py` falha se o sistema e o texto discordarem.

## Os capítulos

| # | Arquivo | Estado |
| --- | --- | --- |
| — | [00-pre-textuais.md](00-pre-textuais.md) | rascunho: capa, resumo, abstract e declaração de uso de IA, com os campos do autor marcados "[preencher]" |
| 1 | [01-introducao.md](01-introducao.md) | rascunho completo |
| 2 | [02-fundamentacao.md](02-fundamentacao.md) | rascunho completo; referências conferidas em 18/11/2026 |
| 3 | [03-sistema.md](03-sistema.md) | rascunho completo; faltam as figuras finais |
| 4 | [curadoria.md](curadoria.md) | escrito antes; números presos ao catálogo por teste |
| 5 | [05-construcao-e-verificacao.md](05-construcao-e-verificacao.md) | rascunho completo |
| 6 | [06-resultados-da-verificacao.md](06-resultados-da-verificacao.md) | rascunho completo |
| 7 | [07-limitacoes-e-trabalhos-futuros.md](07-limitacoes-e-trabalhos-futuros.md) | rascunho completo |
| 8 | [08-conclusao.md](08-conclusao.md) | rascunho completo |
| — | [referencias.md](referencias.md) | a lista, na NBR 6023, dos capítulos 1 a 3, 5 a 8 e do apêndice |
| — | [conferencia-das-referencias.md](conferencia-das-referencias.md) | onde cada obra foi aberta e o que sustenta, com página |
| A | [apendice-protocolo.md](apendice-protocolo.md) | o estudo com estudantes, pronto para quando houver participantes |

## O que falta, e de quem é

- **O modelo da UFV** (e as seções obrigatórias que ainda faltam:
  agradecimentos, ficha, folha de aprovação, listas). É do Rafael trazer.
  Resumo e abstract estão em rascunho em `00-pre-textuais.md`.
- **As referências.** Nenhuma referência entra sem ter sido aberta na
  obra: é a regra do projeto (`docs/linguagem.md`: "fonte que você só
  consegue parafrasear de memória não é fonte"). A conferência de
  18/11/2026, feita com assistência de IA, abriu todas as do texto menos
  Brooke (1996), que só o Apêndice A usa e segue marcada; três foram
  retiradas e duas trocadas por obras que puderam ser abertas
  ([conferencia-das-referencias.md](conferencia-das-referencias.md)). O
  autor pode refazer a conferência pelos endereços registrados.
  `mvp/test_monografia.py` falha se aparecer uma marca de "conferir" nova
  no texto, ou se a lista e o registro discordarem. Falta juntar a lista à do
  capítulo de curadoria na formatação final.
- **A revisão do conteúdo das escadas pelo autor.** As treze escadas
  estão com `revisado_por` em branco. O texto diz como o material foi
  escrito e conferido; dizer "revisado pelo autor" depende dessa leitura.
- **Declaração de uso de IA**, se a norma da UFV pedir: o texto e boa
  parte do código foram produzidos com assistência de um modelo de
  linguagem, sob direção e revisão do autor.
- **As figuras.** As capturas de tela estão em `figuras/`, tiradas do
  servidor de ensaio (porta 8013, nunca do sistema no ar), no tamanho de
  celular. A numeração e as legendas finais seguem o modelo.

## As figuras

| Figura | Arquivo | O que mostra |
| --- | --- | --- |
| 3.1 | `figuras/fig-3-1-pergunta.jpg` | a pergunta de diagnóstico, com a resposta confirmada e as razões (kc_07, tema claro; 19/11) |
| 3.2a | `figuras/fig-3-2a-voce-disse.jpg` | "Você disse": a concepção da pessoa e a previsão pedida (18/11, antes do botão Sair) |
| 3.2b | `figuras/fig-3-2b-maquina.jpg` | "A máquina respondeu": o que o compilador disse, a previsão, e a ideia que fica de pé (18/11, antes do botão Sair) |
| 3.3 | `figuras/fig-3-3-passo.jpg` | um passo guiado da escada, com a concepção errônea entre as alternativas e a certeza (kc_07 B2, com a frase da leitura das perguntas; 19/11) |
| 3.4 | `figuras/fig-3-4-fechamento.jpg` | o fechamento: as ideias erradas encontradas e a situação de cada uma (18/11) |
| 3.5 | `figuras/fig-3-5-inicio-escuro.jpg` | a página inicial no tema escuro: o próximo sugerido e o caminho dos 13 tópicos, com um feito e um em andamento (19/11) |
| 3.6 | `figuras/fig-3-6-cena.jpg` | a cena da revisão do kc_06 B1, dentro da bancada de `zera`: a cópia `n` vira 0, e `idade` continua 15 (19/11) |
