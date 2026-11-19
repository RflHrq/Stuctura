# A monografia — roteiro e estado

O texto do TCC, um arquivo por capítulo. Os `.md` são a fonte; o PDF no
modelo da UFV (abnTeX2) sai deles:

    python scripts/monografia_latex.py
    cd docs/monografia/latex
    pdflatex TCC_STRUCTURA && bibtex TCC_STRUCTURA && pdflatex TCC_STRUCTURA && pdflatex TCC_STRUCTURA

O script gera `latex/gerado/` (capítulos, resumo, abstract e declaração de
uso de IA) e recusa o que não sabe traduzir: citação fora da tabela dele,
figura ou quadro citado que não existe, seção cujo número não bate com o
que o LaTeX numera. `latex/TCC_STRUCTURA.tex` (capa, dedicatória,
agradecimentos, listas) é à mão, a partir do arquivo do autor;
`latex/referencias.bib` junta as duas listas de referências. Um teste
falha se o LaTeX gerado envelhecer em relação aos `.md`, ou se uma
citação não tiver entrada no `.bib`.

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
| — | [00-pre-textuais.md](00-pre-textuais.md) | capa com os dados do arquivo do autor; resumo, abstract e declaração de uso de IA, esta com dois campos "[preencher]" |
| — | `latex/TCC_STRUCTURA.tex` | o PDF no modelo da UFV, gerado dos `.md` (58 páginas em 19/11/2026) |
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

- **O que o modelo da UFV ainda pede e não está no PDF:** a folha de
  aprovação (comentada em `TCC_STRUCTURA.tex` até a banca ser definida) e
  a ficha catalográfica, se o curso a exigir (é feita pela biblioteca).
- **Três pontos de referência para o autor decidir:** o ano do livro de
  Summit (1995 na página do FAQ, 1996 no texto; conferir na página de
  direitos do livro); Hermans et al. (2018) é mencionada na curadoria,
  como citação removida, sem entrada na lista; e a curadoria fala de um
  "apêndice de curadoria" (`docs/curadoria-crencas.md`) que não está no
  PDF. Com o texto do Sorva agora em `fontes/sorva2012/`, ele pode ser
  gerado de novo e entrar como apêndice.
- **As referências.** Nenhuma referência entra sem ter sido aberta na
  obra: é a regra do projeto (`docs/linguagem.md`: "fonte que você só
  consegue parafrasear de memória não é fonte"). A conferência de
  18/11/2026, feita com assistência de IA, leu as obras no navegador; três
  foram retiradas e duas trocadas por obras que puderam ser abertas. A
  segunda, de 19/11/2026, a pedido do autor, **baixou** as obras para
  `fontes/` (fora do repositório) e conferiu cada frase de novo no
  arquivo: abriu Brooke (1996), que faltava, e corrigiu uma página de
  Posner, uma contagem em 2.5, uma frase sobre Gardner-Medwin, uma sobre o
  FAQ e duas entradas da curadoria (Sleeman et al. e Samurçay), herdadas
  da bibliografia do Sorva
  ([conferencia-das-referencias.md](conferencia-das-referencias.md)).
  Os trabalhos relacionados (2.8) voltaram, a partir do relatório
  anterior, só com o que as obras sustentam: saíram três afirmações sem
  apoio e a tese de Mazumder (2024), que não foi encontrada em catálogo
  nenhum. Ficam para o autor baixar pelo acesso da UFV, porque a editora
  bloqueia download automatizado: Qian e Lehman (2017), VanLehn (2011),
  Schmellenkamp, Latys e Zeume (2023) e Sorva (2013); dos dois últimos,
  o texto só afirma o que está no resumo.
  `mvp/test_monografia.py` falha se aparecer uma marca de "conferir" nova
  no texto, ou se a lista e o registro discordarem. As duas listas (esta e
  a do capítulo de curadoria) estão juntas em `latex/referencias.bib`.
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
| 3.2 | `figuras/fig-3-2-passo.jpg` | um passo guiado da escada, com a concepção errônea entre as alternativas e a certeza (kc_07 B2, com a frase da leitura das perguntas; 19/11) |
| 3.3 | `figuras/fig-3-3-fechamento.jpg` | o fechamento: as ideias erradas encontradas e a situação de cada uma (18/11) |
| 3.4a | `figuras/fig-3-4a-voce-disse.jpg` | "Você disse": a concepção da pessoa e a previsão pedida (18/11, antes do botão Sair) |
| 3.4b | `figuras/fig-3-4b-maquina.jpg` | "A máquina respondeu": o que o compilador disse, a previsão, e a ideia que fica de pé (18/11, antes do botão Sair) |
| 3.5 | `figuras/fig-3-5-cena.jpg` | a cena da revisão do kc_06 B1, dentro da bancada de `zera`: a cópia `n` vira 0, e `idade` continua 15 (19/11) |
| 3.6 | `figuras/fig-3-6-inicio-escuro.jpg` | a página inicial no tema escuro: o próximo sugerido e o caminho dos 13 tópicos, com um feito e um em andamento (19/11) |

As figuras são numeradas na ordem em que aparecem no Capítulo 3, como a
ABNT pede, e cada uma está no texto, logo depois do parágrafo que a cita.
