# A monografia — roteiro e estado

O texto do TCC, um arquivo por capítulo. A formatação no modelo da UFV
(ABNT, em Word ou LaTeX) vem por último, quando o modelo estiver em mãos:
o conteúdo não depende dele.

**O recorte (decidido pelo Rafael em 18/11/2026):** o trabalho descreve a
construção e a verificação do sistema, sem estudo com estudantes. A
pergunta "estudantes conseguem e querem completar a sessão?" vai para
trabalhos futuros, com o protocolo do estudo pronto em apêndice. Se a
coleta acontecer depois, os resultados entram num capítulo próprio.

**A versão descrita** é a do ramo `trilha` em 18/11/2026: os treze
tópicos abrem na trilha (commit `5d2b2bc`), com a conferência do banco
contra o compilador, o conserto das oito questões do kc_02 e a correção
das citações de `pointer_is_data` (commit `579e89c` e seguintes). Os
números do texto foram tirados do sistema por script, e não de memória.

## Os capítulos

| # | Arquivo | Estado |
| --- | --- | --- |
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

- **O modelo da UFV** (e as seções obrigatórias: resumo, abstract,
  agradecimentos, listas). É do Rafael trazer.
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
| 3.1 | `figuras/fig-3-1-pergunta.jpg` | a pergunta de diagnóstico, com a resposta marcada e as razões (kc_07, tema claro) |
| 3.2a | `figuras/fig-3-2a-voce-disse.jpg` | "Você disse": a concepção da pessoa e a previsão pedida |
| 3.2b | `figuras/fig-3-2b-maquina.jpg` | "A máquina respondeu": o que o compilador disse, a previsão, e a ideia que fica de pé |
| 3.3 | `figuras/fig-3-3-passo.jpg` | um passo guiado da escada, com a concepção errônea entre as alternativas e a certeza |
| 3.4 | `figuras/fig-3-4-fechamento.jpg` | o fechamento: as ideias erradas encontradas e a situação de cada uma |
| 3.5 | `figuras/fig-3-5-inicio-escuro.jpg` | a página inicial no tema escuro |
