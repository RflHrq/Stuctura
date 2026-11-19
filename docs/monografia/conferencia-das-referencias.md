# Conferência das referências

A regra do projeto é que nenhuma referência entra no texto sem ter sido
aberta na obra (`docs/linguagem.md`: "fonte que você só consegue
parafrasear de memória não é fonte"). Este arquivo registra, para cada obra
citada nos capítulos 1 a 3, 5 a 8 e no Apêndice A, **onde ela foi aberta**
e **o que, nela, sustenta cada frase**, com a página. O capítulo de
curadoria tem o próprio registro.

**Como foi feita.** Em 18/11/2026, com assistência de IA e sob a direção
do autor: cada obra foi aberta no navegador, no endereço indicado, e o
texto foi lido na própria cópia (o texto dos PDFs foi extraído no
navegador, sem baixar arquivo). O que se registra aqui é paráfrase e
página, e não citação. Quem quiser refazer a conferência abre os mesmos
endereços. Cópias de procedência duvidosa (sites de compartilhamento de
arquivos) não foram usadas, e nenhum bloqueio de acesso foi contornado.

**Páginas.** Onde a cópia aberta é a versão publicada, a página é a da
revista. Onde é um manuscrito do autor, as páginas não coincidem com as do
livro ou da revista, e o texto cita sem página, o que a NBR 10520 permite
na citação indireta.

**Segunda conferência, 19/11/2026, a pedido do autor.** Desta vez as obras
foram **baixadas**, cada uma na sua pasta em `docs/monografia/fontes/`
(fora do repositório, porque são obras de terceiros), e cada frase do
texto que cita uma delas foi conferida de novo no arquivo, na página
citada, por busca no texto extraído do PDF. Só se baixou de fonte
legítima: editora em acesso aberto, repositório institucional, página do
autor ou de agência pública, ERIC, e o Internet Archive para páginas que
saíram do ar. Onde a editora bloqueia acesso automatizado (verificação
anti-robô), o bloqueio não foi contornado, e a obra fica para o autor
baixar pelo acesso institucional. O resultado está na seção "Segunda
conferência", ao fim, e as correções que ela pediu já estão no texto.

## Conferidas

### POSNER et al. (1982)

- **Aberta em:** cópia com texto de um curso da Universidade de Atenas,
  `eclass.uoa.gr/modules/document/file.php/PHS122/Αρθρα/Posner_Strike_Hewson_Gertzog.pdf`
  (a cópia da Weber State é digitalização sem texto). É a versão publicada:
  *Science Education* 66(2), p. 211-227.
- **p. 212-213:** distingue dois modos de mudança: usar os conceitos que se
  tem para lidar com o novo (o que os autores chamam de assimilação, p. 212)
  e substituir ou reorganizar os conceitos centrais (p. 212), mudança que
  eles chamam de acomodação no alto da p. 213. O texto citava só a p. 212;
  passou a citar 212-213 na segunda conferência.
- **p. 214:** as quatro condições da acomodação: insatisfação com a
  concepção existente; a nova precisa ser inteligível; parecer plausível
  desde o início; e sugerir um programa frutífero.
- **p. 221:** diante de uma anomalia, a acomodação é o caminho mais difícil
  e menos provável; as alternativas incluem rejeitar a observação, julgá-la
  irrelevante, compartimentalizar o conhecimento para que a informação nova
  não entre em conflito com a crença, e assimilá-la às concepções
  existentes.
- **p. 224:** a anomalia levada a sério produz o conflito cognitivo que
  prepara a acomodação.
- **p. 225:** entre as implicações, desenvolver aulas, demonstrações,
  problemas e laboratórios que criem conflito cognitivo.
- **Sustenta:** Capítulo 1 (1.1); Capítulo 2 (2.1).
- **Ajuste no texto:** o rascunho dizia que a pessoa "encaixa a explicação
  correta dentro da ideia antiga, e sai com as duas" — o que mistura duas
  das alternativas da p. 221 (assimilar e compartimentalizar). O texto
  agora diz as duas.
- **Atenção ao termo:** "assimilação", em Posner et al., é encaixar o novo
  na concepção antiga — o contrário do que o sistema chama de "assimilou"
  no fechamento (acertar de novo, com outras premissas no meio). O
  Capítulo 2 avisa isso uma vez. O autor decidiu, em 18/11/2026, manter o
  rótulo do sistema como está.

### QIAN e LEHMAN (2017)

- **Aberta em:** `https://dl.acm.org/doi/pdf/10.1145/3077618` (ACM, acesso
  aberto). Paginação por artigo: 1:1 a 1:24.
- **p. 1:1 (resumo):** as dificuldades dos iniciantes aparecem no
  conhecimento sintático, no conceitual e no estratégico; os autores
  recomendam que a pesquisa vá além de documentar concepções errôneas e
  integre as teorias de mudança conceitual.
- **p. 1:2:** os primeiros trabalhos sobre concepções errôneas em
  programação são dos anos 1980 (Bayman e Mayer; du Boulay; Pea; Sleeman et
  al.); a área usa termos variados (dificuldades, concepções errôneas,
  erros, *bugs*).
- **p. 1:3:** não há definição comumente aceita na computação.
- **p. 1:13:** a seção sobre mudança conceitual parte de Posner et al.
  (1982) e do conflito cognitivo.
- **Sustenta:** Capítulo 2 (2.1).

### SORVA (2012)

- **Aberta em:** texto integral, repositório institucional da Universidade
  Aalto (handle 123456789/3534), conforme o Capítulo 4.
- **Sustenta:** Capítulo 2 (2.1), que só remete ao Capítulo 4.
- **Reaberta em 18/11/2026**, para uma divergência achada na revisão: o
  texto extraído pelo próprio repositório (bundle TEXT,
  `isbn9789526046266.pdf.txt`), lido no navegador pela API do DSpace. Na
  Tabela A.1, o item 14 (p. 360) é sobre variável ser um par nome-valor
  que não fica guardado no computador; o item 65 (p. 362) é sobre a
  variável de objeto guardar as propriedades do objeto, e não a
  referência. A concepção `pointer_is_data` é a do item 65: o catálogo do
  kc_02 já dizia isso; os do kc_04, kc_08 e kc_12 ainda citavam o 14, e
  foram corrigidos, com a seção 3 dos achados do Capítulo 4.

### GARDNER-MEDWIN (2006)

- **Aberta em:** manuscrito final do autor,
  `http://www.tmedwin.net/~ucgbarg/tea/innovass7.pdf`, que se identifica
  como o capítulo 12 (p. 141-149) do livro organizado por Bryan e Clegg.
  As páginas do manuscrito não são as do livro.
- **ms p. 1:** a marcação pela certeza foi muito pesquisada antes de a
  avaliação por computador ser viável (Ahlgren, 1969; Good, 1979); o autor
  relata dez anos de uso na UCL, num protocolo nascido entre escolas de
  medicina e usado, desde 2001, nas provas de medicina. O texto dizia "dez
  anos de uso em cursos de medicina"; passou a dizer "na University College
  London, sobretudo em cursos de medicina".
- **ms p. 2:** três níveis de certeza (C = 1, 2, 3), com acerto valendo
  1, 2 ou 3 e erro valendo 0, -2 ou -6; os níveis são nomeados por números
  ou descritores neutros, e não por palavras como "certeza" ou "chute",
  porque essas palavras significam coisas diferentes para pessoas
  diferentes.
- **ms p. 6:** um acerto por sorte não é conhecimento, e uma concepção
  errônea firme é muito pior do que a ignorância reconhecida.
- **ms p. 7:** a estratégia é conhecida e pesquisada há muitas décadas.
- **Sustenta:** Capítulo 2 (2.2); Capítulo 7 (a certeza como sinal
  ruidoso).
- **O que a conferência trouxe:** o Structura nomeia os níveis com palavras
  ("chutei", "acho que sei", "tenho certeza", `mvp/motor.py`). O texto
  agora diz isso e põe o custo nas limitações.

### FALMAGNE et al. (2006)

- **Aberta em:** `https://www.aleks.com/about_aleks/Science_Behind_ALEKS.pdf`,
  versão de 15 páginas do capítulo publicado nas p. 61-79 do volume 3874
  das *Lecture Notes in Computer Science* (dados conferidos na página da
  Springer). Páginas da versão aberta não são as do livro.
- **p. 1:** o resultado da avaliação são duas listas: o que o estudante
  sabe fazer e o que ele está pronto para aprender.
- **p. 9:** a fronteira externa de um estado de conhecimento é o conjunto
  dos problemas que, acrescentados ao estado, formam outro estado; é onde
  o progresso acontece.
- **p. 10:** fronteira interna = o que o estudante sabe fazer; fronteira
  externa = o que está pronto para aprender.
- **p. 13:** a avaliação é estocástica: o sistema escolhe o estado mais
  provável.
- **p. 15:** os resultados da teoria estão reunidos na monografia de
  Doignon e Falmagne (1999).
- **Sustenta:** Capítulo 2 (2.3).
- **Troca:** o rascunho citava a monografia de 1999, que não foi aberta;
  o texto passou a citar este capítulo, que foi.

### WHITE e GUNSTONE (1992)

- **Aberta em:** a página do capítulo na editora,
  `https://www.taylorfrancis.com/chapters/mono/10.4324/9780203761342-3/prediction-observation-explanation-richard-white-richard-gunstone`
  — o capítulo 3, "Prediction — Observation — Explanation", 21 páginas.
  Foi lida a abertura do capítulo, que a editora publica; o restante do
  livro não está aberto (as cópias integrais encontradas eram de sites de
  compartilhamento, e não foram usadas).
- **Abertura do cap. 3:** o POE pede três tarefas: prever o resultado de um
  acontecimento e justificar a previsão; descrever o que se vê acontecer; e
  reconciliar o conflito entre previsão e observação.
- **Sustenta:** Capítulo 2 (2.4), citado pelo capítulo, sem página.

### NUSSBAUM, CORDOVA e REHMAT (2017)

- **Aberta em:** `https://files.eric.ed.gov/fulltext/EJ1135295.pdf` (ERIC,
  texto integral). Versão publicada: *Journal of Geoscience Education*
  65(1), p. 23-34.
- **p. 23:** textos de refutação ativam a concepção errônea, refutam-na
  explicitamente e então enunciam a concepção correta; três décadas de
  pesquisa os mostram mais eficazes que textos expositivos (entre as
  fontes, Tippett, 2010).
- **p. 31:** recomendações: ativar o conhecimento prévio antes da leitura,
  por perguntas ou por uma demonstração; avisar que o conhecimento ativado
  pode estar errado; e, citando Tippett (2010, p. 965), a refutação tende a
  funcionar melhor quando a concepção errônea é uma ideia única, e não um
  conceito complexo.
- **Sustenta:** Capítulo 2 (2.4).
- **Troca:** o rascunho citava Tippett (2010), que não foi aberto (ver
  abaixo); o texto passou a citar este artigo, e Tippett por meio dele.

### SWELLER, VAN MERRIËNBOER e PAAS (2019)

- **Aberta em:** `https://link.springer.com/article/10.1007/s10648-019-09465-5`
  (acesso aberto) e o PDF da mesma página, para a paginação.
- **p. 265:** o efeito do exemplo resolvido.
- **p. 268:** os problemas de completar, propostos por van Merriënboer e
  Krammer (1987) justamente para a programação introdutória: o estudante
  recebe um programa incompleto para terminar; são uma ponte entre o
  exemplo resolvido e o problema convencional.
- **p. 277:** o efeito do esmaecimento da orientação: o que é essencial
  para o novato fica redundante com a experiência, e os exemplos devem dar
  lugar a problemas.
- **p. 279:** o efeito dos elementos isolados: apresentar primeiro os
  elementos e só depois a informação inteira, com as interações entre
  eles.
- **Sustenta:** Capítulo 2 (2.5), no lugar de "literatura de carga
  cognitiva e de exemplos resolvidos, a escolher".
- **Segunda conferência:** o parágrafo de 2.5 cita os quatro efeitos acima,
  mas dizia "três efeitos"; passou a dizer quatro.

### VANLEHN (2006)

- **Aberta em:** manuscrito do autor,
  `https://cs.uky.edu/~sgware/reading/papers/vanlehn2006behavior.pdf`
  (material de leitura de um curso da Universidade de Kentucky). Versão
  publicada: *IJAIED* 16(3), p. 227-265.
- **Resumo:** os tutores têm dois laços; o externo roda uma vez por tarefa,
  o interno uma vez por passo; o interno dá retorno e dicas a cada passo e
  pode avaliar a competência do estudante e atualizar o modelo que o laço
  externo usa para escolher a próxima tarefa.
- **ms p. 5:** o dever do laço externo é escolher a tarefa; o do interno,
  eliciar os passos e ajudar a aprender; o sistema mais simples dá retorno
  depois de cada passo.
- **Sustenta:** Capítulo 2 (2.6), no lugar de VanLehn (2011) e Woolf
  (2009) para a arquitetura.

### VANLEHN (2011)

- **Aberta em:**
  `https://www.emergingedtech.com/-kvanlehn/Stringent/PDF/EffectivenessOfTutoring_Vanlehn.pdf`
  — o PDF da editora, com a marca de download da Arizona State University,
  num espelho da página do autor (o endereço `public.asu.edu` deu erro).
- **p. 197:** os tutores por computador se dividem pela granularidade da
  interação: por resposta, por passo e por subpasso; os tutores
  inteligentes são quase todos por passo ou subpasso. Efeito, contra
  nenhuma tutoria: tutoria humana d = 0,79; tutores inteligentes d = 0,76.
- **O que não sustenta:** a frase do rascunho sobre a "arquitetura
  clássica" — o artigo compara efeitos, não descreve arquitetura. A frase
  passou para VanLehn (2006).
- **Sustenta:** Capítulo 2 (2.6), a classificação e os efeitos.

### SODERSTROM e BJORK (2015)

- **Aberta em:** cópia do laboratório dos autores,
  `https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/11/soderstorm_ra_learningvsperformance.pdf`
  — a versão publicada, *Perspectives on Psychological Science* 10(2),
  p. 176-199.
- **p. 176:** a aprendizagem é a mudança relativamente permanente, que
  sustenta retenção de longo prazo e transferência; o que se observa
  durante a instrução é o desempenho, muitas vezes índice pouco confiável
  de que ela aconteceu.
- **p. 188:** o desempenho durante a aquisição é índice muito imperfeito
  da aprendizagem de longo prazo.
- **Sustenta:** Capítulo 2 (2.7); Capítulo 7.

### W3C (2025)

- **Aberta em:** `https://www.w3.org/TR/WCAG21/` — W3C Recommendation de 6
  de maio de 2025 (a versão original é de 5 de junho de 2018).
- **Critério 1.4.3, Contraste (Mínimo), nível AA:** texto com razão de
  contraste de pelo menos 4,5:1; texto grande, 3:1; sem exigência para
  texto decorativo, de componente inativo e de logotipo.
- **Definição de razão de contraste:** (L1 + 0,05) / (L2 + 0,05), com L1 a
  luminância relativa da cor mais clara.
- **Definição de luminância relativa:** linearização sRGB com limiar
  0,04045; a nota 2 diz que, antes de maio de 2021, o valor era 0,03928, e
  que a troca não tem efeito prático.
- **O que a conferência trouxe:** `mvp/test_interface.py` usa 0,03928. Em
  cores de 8 bits nenhum valor c/255 fica entre os dois limiares (10/255 ≈
  0,0392 e 11/255 ≈ 0,0431), então o contraste calculado é o mesmo;
  `mvp/test_monografia.py` confere isso, e o Capítulo 5 o diz.
- **Sustenta:** Capítulo 3 (3.7); Capítulo 5 (5.5).

### BROOKE (1996)

- **Tentativas em 18/11/2026,** sem sucesso: a cópia do capítulo no site
  da AHRQ não existia mais, o PDF da retrospectiva de 2013 dava 404 e o
  Internet Archive estava fora do ar.
- **Aberta em 19/11/2026:** a cópia que a AHRQ (agência do governo dos
  EUA) publicava, recuperada no Internet Archive
  (`web.archive.org/web/2015/https://www.digital.ahrq.gov/...systemusabilityscale(sus)_comp[1].pdf`),
  em `fontes/brooke1996/`. É o manuscrito do capítulo, "SUS - A quick and
  dirty usability scale", com a escala no fim.
- **O que sustenta:** o SUS é uma escala Likert simples, de dez itens, que
  dá uma visão global da usabilidade percebida. Sustenta o Apêndice A
  (A.1, V4: "SUS, de 10 itens").
- **Os dados da entrada:** autor, título, organizadores, livro e editora
  conferem com a citação que o próprio Brooke faz do capítulo na
  retrospectiva de 2013 (*Journal of Usability Studies* 8(2), p. 29-40,
  também do Internet Archive, em `fontes/brooke2013/`) e com a página do
  livro na editora (Jordan, Thomas, McClelland, Weerdmeester; o prenome de
  McClelland é Ian Lyall, e a retrospectiva grafa "A. L."). As páginas
  **p. 189-194**, como estavam, não foram achadas em fonte aberta; o
  registro do capítulo na Crossref, da editora, dá **p. 207-212** e o DOI
  10.1201/9781498710411-35, e é o que a lista passou a trazer.

### YAMASHITA et al. (2017)

- **Aberta em 19/11/2026:** texto integral, SpringerOpen (acesso aberto,
  licença Creative Commons), em `fontes/yamashita2017/`. *Research and
  Practice in Technology Enhanced Learning* 12, art. 17, 16 p.
- **Resumo (p. 1):** o TEDViT mostra, em sincronia, a imagem da memória
  (o valor concreto das variáveis) e o mundo do domínio (as estruturas de
  dados, de forma lógica); o que o mundo do domínio mostra segue uma
  política definida pelo professor.
- **p. 11-12:** nos questionários aplicados depois das aulas, o desvio
  padrão das respostas sobre compreensão, ritmo e dificuldade foi menor em
  2015, com o TEDViT, do que em 2013 e 2014; os autores leem isso como
  redução da desigualdade de compreensão. A medida é de autoavaliação, e o
  texto diz isso.
- **O que não está:** nenhuma ocorrência de modelo do estudante,
  diagnóstico ou concepção errônea; o texto diz que o artigo "não
  descreve" modelo do estudante, e não que o sistema não o tenha.
- **Sustenta:** Capítulo 2 (2.8.1 e Quadro 2.1).

### SCHMELLENKAMP, LATYS e ZEUME (2023)

- **Aberta em 19/11/2026 só no resumo,** no registro aberto do Semantic
  Scholar; os dados de publicação, no registro da Crossref (*Proceedings
  of the 54th ACM Technical Symposium on Computer Science Education V. 1*,
  p. 465-471). O texto integral está na ACM (acesso aberto, mas com
  bloqueio anti-robô) e numa cópia do repositório da Universidade de
  Bochum que deu erro no servidor; fica para o autor baixar.
- **Resumo:** estudar concepções errôneas em métodos formais integrando
  métodos quantitativos e qualitativos; até então, estudos sobretudo
  qualitativos, em geral entrevistas com menos de 20 pessoas; dois fluxos
  de trabalho (medir quão comum é uma concepção já descrita; descobrir
  candidatas nos dados); aplicação a exercícios de modelagem lógica do
  Iltis, com mais de 250 respostas em muitos exercícios.
- **O que saiu do relatório anterior:** a frase de que o Iltis usa
  "questões de múltipla escolha com distratores mapeados a concepções
  errôneas" não está no resumo (os exercícios são de modelagem lógica) e
  foi retirada.
- **Sustenta:** Capítulo 2 (2.8.2 e Quadro 2.1), só com o que está no
  resumo.

### SORVA (2013)

- **Aberta em 19/11/2026 só no resumo,** no registro aberto da Crossref,
  com os dados de publicação (*ACM Transactions on Computing Education*
  13(2), p. 1-31). O texto integral está na ACM; fica para o autor baixar.
- **Resumo:** revisão que reúne a literatura de concepções errôneas de
  programação, modelos mentais, construtivismo, fenomenografia e
  conceitos-limiar, examinada em relação à máquina nocional; a literatura
  aponta a máquina nocional como grande desafio do ensino introdutório, e
  o autor defende que ela seja objetivo explícito do ensino.
- **O que mudou em relação ao relatório anterior:** ele dizia que o artigo
  "estabeleceu formalmente o conceito" de máquina nocional e "integrou
  misconceptions, modelos mentais e visualização". O resumo diz que o
  artigo reúne e comenta essas linhas (e cita outras, sem visualização); o
  conceito é anterior ao artigo. O texto passou a dizer o que o resumo
  diz.
- **Sustenta:** Capítulo 2 (2.8.4 e Quadro 2.1).

**Também conferido para 2.8, em Falmagne et al.:**

- **p. 12-14 da versão aberta:** a primeira pergunta é a mais informativa
  (cerca de 50% de chance de acerto, pelo estado provável); a avaliação
  para quando a entropia fica baixa e não há pergunta útil; uma avaliação
  completa de Aritmética levou 24 perguntas, perto da média. **p. 15:** o
  primeiro artigo da teoria é de Doignon e Falmagne, de 1985 (citado
  `apud`, por isso fora da lista). Dois dos autores são da ALEKS
  Corporation, e a cópia aberta é publicada pela própria ALEKS.
- **O que saiu do relatório anterior:** "diagnóstico por meio de 25 a 30
  questões" e "utilizado por milhões de estudantes" não estão no artigo e
  foram retirados; ficou o número que o artigo dá (24 perguntas).

## Trabalhos relacionados: o que do relatório anterior ficou de fora

- **MAZUMDER (2024),** tese de doutorado na UNC Charlotte, "Investigating
  Novice Programmers' Mental Models": não foi encontrada no OpenAlex, no
  Semantic Scholar nem na busca do repositório da universidade; o OpenAlex
  lista artigos da autora sobre modelos mentais de arrays (2021, 2023,
  2024), mas nenhuma tese. Sem poder confirmar que a obra existe com esses
  dados, ela não entrou. Se o autor tiver o arquivo, ela volta.
- **A busca nas bases** (ACM, Google Scholar, Springer, 2013 a 2024) que o
  relatório anterior descrevia não pôde ser confirmada nesta conferência,
  e incluía obras fora do período (2006). O texto de 2.8 diz só o critério
  de escolha.

## Ainda não abertas

Nenhuma, depois da segunda conferência (19/11/2026).

## Citadas por outra obra (apud)

### TIPPETT (2010)

- *International Journal of Science and Mathematics Education* 8(6),
  p. 951-970. Na Springer, só o resumo é aberto; a cópia do ResearchGate
  ficou bloqueada. O texto cita a p. 965 por meio de Nussbaum, Cordova e
  Rehmat (2017, p. 31), como apud, e por isso ela não entra na lista.

## Retiradas

- **HUNT (2003)**, *Journal of Intellectual Capital* 4(1): só o resumo na
  editora; as cópias integrais encontradas eram de sites de
  compartilhamento. Gardner-Medwin (2006) sustenta sozinho a frase.
- **DOIGNON e FALMAGNE (1999)**, *Knowledge Spaces*: o livro não foi
  aberto; trocado por Falmagne et al. (2006).
- **WOOLF (2009)**, *Building Intelligent Interactive Tutors*: o livro não
  foi aberto; VanLehn (2006) sustenta a frase.

## Segunda conferência, 19/11/2026: as obras baixadas

Cada arquivo está em `docs/monografia/fontes/<pasta>/`, fora do
repositório. O hash (os 12 primeiros caracteres do SHA-256) permite a quem
refizer a conferência saber que tem o mesmo arquivo. "Confere" quer dizer
que o que a frase do texto afirma está na página citada do arquivo.

| obra | arquivo (pasta) | origem | tamanho, hash | resultado |
| --- | --- | --- | --- | --- |
| Posner et al. (1982) | `posner1982` | curso da Universidade de Atenas (eclass.uoa.gr), versão publicada | 1149 KB, 3bff2d0dc0fb | p. 214, 221, 224 e 225 conferem; a p. 212 passou a 212-213 |
| Qian e Lehman (2017) | não baixada | ACM: verificação anti-robô | | a p. 1:1 (resumo) confere com o registro da Crossref; as p. 1:2-1:3 ficam com a leitura de 18/11 |
| Sorva (2012) | `sorva2012` | repositório da Aalto, PDF e texto integral | 16040 KB, a3a7d20b7b4d; texto 1363 KB, 8a259439d0a2 | confere (ver a seção seguinte) |
| Gardner-Medwin (2006) | `gardnermedwin2006` | página do autor | 147 KB, 9fd215fddbbe | confere; o "cursos de medicina" foi ajustado |
| Falmagne et al. (2006) | `falmagne2006` | página da ALEKS | 353 KB, 5dec432b6073 | p. 1, 9 e 10 conferem; volume e páginas da LNCS conferem com a Crossref |
| White e Gunstone (1992) | `white1992` | página do capítulo na editora | 43 KB, 9fdca855e57e | confere (as três tarefas do POE); o capítulo é o das p. 44-64; o livro inteiro não é aberto |
| Nussbaum, Cordova e Rehmat (2017) | `nussbaum2017` | ERIC | 441 KB, f5bc0602b36b | p. 23 e 31 conferem, inclusive a citação de Tippett (2010, p. 965) |
| Sweller, van Merriënboer e Paas (2019) | `sweller2019` | Springer, acesso aberto | 808 KB, 47ce1d814f9b | p. 265, 268, 277 e 279 conferem; "três efeitos" passou a quatro |
| VanLehn (2006) | `vanlehn2006` | material de curso da Universidade de Kentucky (manuscrito) | 630 KB, 0fc27a20c46b | confere; volume e páginas conferem com a Crossref |
| VanLehn (2011) | não baixada | a editora e a página do autor bloqueiam acesso automatizado | | fica com a leitura de 18/11 |
| Soderstrom e Bjork (2015) | `soderstrom2015` | página do laboratório dos autores | 672 KB, f143e20a1d87 | p. 176 confere |
| W3C (2025) | `w3c2025` | w3.org | 465 KB, 233ac31974ce | 4,5:1 no nível AA, o limiar 0,04045 e a nota sobre 0,03928 conferem |
| Brooke (1996) | `brooke1996`, `brooke2013`, `brooke1996-livro` | AHRQ e JUS pelo Internet Archive; página do livro na editora | 164 KB, fc03554a8a27; 538 KB, 4249de64fad1 | aberta pela primeira vez; confere; páginas trocadas para as da editora |

**Para o autor baixar pelo acesso da UFV (CAPES):** Qian e Lehman (2017),
DOI 10.1145/3077618 (a ACM é de acesso aberto, mas bloqueia download
automatizado), e VanLehn (2011), DOI 10.1080/00461520.2011.611369. Com os
dois arquivos em `fontes/`, as frases das p. 1:2-1:3 e da p. 197 podem ser
conferidas como as outras.

## Segunda conferência: as obras do capítulo de curadoria

- **Sorva (2012), Tabela A.1.** Os onze itens que o capítulo cita conferem
  no texto da tese: número, página e frase (itens 5, 9, 10 e 12 na
  p. 359; 14 e 22 na p. 360, com a segunda frase do 14; 54 e 65 na p. 362;
  92 na p. 364, atribuído a Ma, 2007; 151 na p. 367). A tabela tem 162
  itens, 17 no tópico `Refs`, e a contagem de termos do Quadro 4.3 confere
  exatamente (0, 0, 0, 1 para `null`, 1 para `lifetime`, 7 para `memory`).
  Hermans et al. (2018) não aparece nenhuma vez no texto integral.
- **FAQ do comp.lang.c.** As sete perguntas citadas (4.9, 4.11, 6.2, 6.4b,
  6.9, 7.21 e 7.22) existem, e os quatro títulos do Quadro 4.2 conferem
  palavra por palavra. O prefácio do livro, publicado pelo autor, diz que a
  lista começou a ser postada em maio de 1990. A página do FAQ diz que o
  livro é "mais longo" que a versão on-line, e não que ela é "cerca de
  metade" dele: o texto passou a dizer "mais curta".
- **O ano do livro de Summit:** a página do FAQ e o prefácio dizem
  Addison-Wesley, **1995**; o registro na Open Library traz o lançamento em
  7 de novembro de 1995 e a data de 1996. O texto usa 1996. **Conferir na
  página de direitos do livro** antes de mudar.
- **Duas entradas da lista estavam erradas, e o erro vinha da própria
  bibliografia de Sorva (2012), que a curadoria copiou.**
  - *Sleeman et al. (1986):* a bibliografia do Sorva traz duas entradas de
    Sleeman em 1986; uma repete o título e os dados de Putnam et al.
    (1986). O texto do Sorva cita "Putnam et al. (1986) e Sleeman et al.
    (1986)" como estudos distintos, e o registro da Crossref confirma o
    outro: "Pascal and high school students: a study of errors", *Journal
    of Educational Computing Research* 2(1), p. 5-23. A lista passou a
    trazê-lo.
  - *Samurçay (1989):* o Sorva dá R. E. Mayer como organizador de *Studying
    the novice programmer*; o registro do livro na Open Library dá Soloway
    e Spohrer. A lista passou a trazê-los.
- **Os demais dados** de du Boulay (1986), Holland et al. (1997),
  Kaczmarczyk et al. (2010), Doukakis et al. (2007), Ma (2007) e Soloway
  et al. (1982) conferem com a bibliografia do Sorva e, onde há registro,
  com a Crossref e a Open Library. Os artigos em si continuam não abertos
  (acervos pagos), como o capítulo declara: a citação é `apud` Sorva.
- **Kernighan e Ritchie (1988)** é livro e não foi baixado; a frase que o
  cita (K&R diz que a variável declarada não é zerada) fica com a leitura
  original.
