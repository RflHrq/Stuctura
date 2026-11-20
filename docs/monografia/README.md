# A monografia — roteiro e estado

O texto do TCC, um arquivo por capítulo. Os `.md` são a fonte; o PDF no
modelo da UFV (abnTeX2) sai deles:

    python -P -E scripts/gera_curadoria.py docs/monografia/fontes/sorva2012/isbn9789526046266.pdf.txt
    python scripts/monografia_latex.py
    cd docs/monografia/latex
    pdflatex TCC_STRUCTURA && bibtex TCC_STRUCTURA && pdflatex TCC_STRUCTURA && pdflatex TCC_STRUCTURA

O primeiro comando gera o Apêndice B (`apendice-curadoria.md`) e a
auditoria `docs/curadoria-crencas.md` a partir do catálogo, conferindo
cada citação do Sorva no texto integral da tese, baixado em `fontes/`. O
segundo gera `latex/gerado/` (capítulos, resumo, abstract e declaração de
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
| — | [00-pre-textuais.md](00-pre-textuais.md) | capa com os dados do arquivo do autor; resumo, abstract e declaração de uso de IA, que o autor tem de confirmar frase por frase |
| — | `latex/TCC_STRUCTURA.tex` | o PDF no modelo da UFV, gerado dos `.md` (73 páginas em 20/11/2026) |
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
| B | [apendice-curadoria.md](apendice-curadoria.md) | as 61 concepções do catálogo e a procedência de cada uma; **gerado**, não editar à mão (ver abaixo) |

## O que falta, e de quem é

- **O que o modelo da UFV ainda pede e não está no PDF:** a folha de
  aprovação (comentada em `TCC_STRUCTURA.tex` até a banca ser definida) e
  a ficha catalográfica, se o curso a exigir (é feita pela biblioteca).
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
  nenhum. Qian e Lehman (2017), VanLehn (2011), Schmellenkamp, Latys e Zeume
  (2023) e Sorva (2013), que a editora bloqueia para download
  automatizado, foram baixados pelo autor e conferidos; o texto integral
  do Iltis corrigiu a 2.8.2. CERT C, CWE e Hermans et al. (2018), que a
  curadoria menciona, foram abertos e entraram nas referências; a regra
  MEM52-C que o catálogo citava não existe no padrão de C e virou ERR33-C.
  `mvp/test_monografia.py` falha se aparecer uma marca de "conferir" nova
  no texto, ou se a lista e o registro discordarem. As duas listas (esta e
  a do capítulo de curadoria) estão juntas em `latex/referencias.bib`.
- **A revisão de escrita e de norma de 20/11/2026.** O texto inteiro foi
  reescrito em registro acadêmico e conferido contra o manual
  "Normalização de trabalhos acadêmicos" da Biblioteca Central da UFV
  (2026), baixado em `fontes/ufv-manual-2026/`, que aplica a NBR
  14724/2025, a NBR 6023/2025 e a NBR 10520/2023. O que mudou por causa
  dele: (1) citações com o sobrenome só com a inicial maiúscula, também
  entre parênteses, e "et al." e "apud" em itálico; (2) a lista de
  referências traz só as obras consultadas, de modo que as nove obras
  citadas apud Sorva (2012) saíram dela; (3) referências na forma de
  2025: "(ed.)", "[s. l.]" nos periódicos, evento com número, ano e
  local, tese com o ano depois do título, endereço sem os sinais < >;
  (4) o FAQ do comp.lang.c é referenciado pela versão on-line, que foi a
  consultada (Summit, c2005), e não pelo livro; (5) o trabalho se divide
  em seções, e não em capítulos; (6) figuras e quadros numerados em
  sequência única no PDF (os rótulos por seção do `.md` viram referências
  cruzadas do LaTeX);
  (7) sigla por extenso na primeira ocorrência, com a forma completa
  antes da sigla; (8) resumo na voz ativa. Entraram na Introdução a
  justificativa (1.3), os objetivos em subseções (1.4), os procedimentos
  metodológicos (1.6) e a citação da frase de abertura. Ficaram para o
  autor decidir: uma obra de metodologia para a classificação da pesquisa
  em 1.6; o que quer dizer "kc" nos códigos dos tópicos; e se o
  orientador quer o método antes da descrição do sistema.
- **O parecer externo de 20/11/2026.** O autor submeteu o PDF a uma
  leitura crítica e trouxe o parecer. O que mudou por causa dele: (1) a
  declaração de uso de IA perdeu os campos a preencher e passou a dizer o
  que foi feito com o modelo (o código, o conteúdo didático, o texto, a
  conferência das referências, a auditoria do catálogo e a leitura das
  perguntas), o que foi conferido e como, e o que ainda não foi revisado;
  (2) o texto deixou de chamar de "leitura humana" a leitura dos 244
  passos guiados: o autor achou o defeito no primeiro passo do kc_02, e a
  leitura dos demais foi feita com o modelo, como o histórico registra;
  (3) o diagnóstico é apresentado como hipótese diagnóstica, e não como
  constatação do que o estudante pensa; (4) o compilador é instrumento de
  verificação do comportamento observado no ambiente especificado, e não
  árbitro; (5) o FAQ sustenta confusões formuladas por quem programa em
  C, e não a frequência entre estudantes iniciantes, e o critério de
  inclusão deixou de dizer "em primeira pessoa"; (6) os dez perfis
  simulados aparecem nos resultados (Quadros 6.2 e 6.3, presos por
  teste); (7) "extensão" da sessão, em número de telas, no lugar de
  "duração"; (8) o caminho de reforço explica os sinais divergentes;
  (9) as providências éticas do Apêndice A antecedem qualquer coleta.
  Ficaram para o autor decidir: a grade de `heap_dies_with_function`
  (T sem obra citada), a referência normativa do padrão C e o termo
  "misconceptions" no título.
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

As figuras são numeradas na ordem em que aparecem na Seção 3, como a
ABNT pede, e cada uma está no texto, logo depois do parágrafo que a cita.
