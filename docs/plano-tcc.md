# Plano do TCC

## A pergunta de pesquisa

É viável diagnosticar concepções errôneas sobre ponteiros em C a partir da
resposta **e da confiança declarada**, e refutá-las conduzindo o aluno por um
grafo de premissas, numa sessão que estudantes de graduação consigam e
queiram completar?

Quatro subperguntas dividem essa pergunta em coisas que 10 a 15
participantes conseguem responder:

1. **V1 — Viabilidade da sessão.** Os estudantes concluem as unidades sem
   ajuda de conteúdo do pesquisador, e em quanto tempo?
2. **V2 — Coerência da hipótese.** As hipóteses de concepção errônea que o
   sistema gera são compatíveis com as explicações que o participante produz
   pensando em voz alta?
3. **V3 — Mudança imediata.** Depois do percurso de refutação, o
   participante responde de outro jeito a um item novo sobre a mesma
   concepção?
4. **V4 — Aceitação.** Como a pessoa percebe clareza, dificuldade e
   utilidade, e ela faria outra unidade?

A unidade de análise de V2 e V3 **não é o participante**: é o episódio de
crença detectada. Dez pessoas podem gerar 25 episódios ou 4, e o denominador
de cada resultado é esse número.

O estudo **não** compara o método socrático com explicação direta. Essa
comparação exige 30 a 40 participantes e obriga o sistema a esconder do
aluno se ele acertou — foi o que tornou a versão atual desagradável de usar.

## O que muda na sessão, e por quê

A sessão atual mede bem e ensina mal. Estes são os números de uma sessão
completa, contados no sistema em 18/09/2026:

| O que a pessoa atravessa | Hoje | Depois |
| --- | --- | --- |
| Telas na sessão | 49, de uma vez | 8 a 10 por unidade |
| Duração | ~40 minutos | 5 a 7 minutos por unidade |
| Telas de "Confirme comigo…, certo?" | 22, uma sequência de 11 seguidas | no máximo 5, com escolha real |
| Telas que dizem se ela acertou | **0** | toda atividade |
| Telas que ensinam antes de cobrar | 0 | 2 por unidade |

O zero da quarta linha não é defeito de implementação: está escrito no
código que o diagnóstico não dá retorno, para não contaminar a medida do
experimento de dois braços. A pessoa responde 16 atividades e nunca descobre
se acertou uma. Sem comparação entre braços, essa restrição cai.

**A unidade nova, do tamanho de uma lição de Duolingo:**

1. **Ensina** (2 telas) — a premissa em linguagem simples, com a figura.
   Esse material já existe para os 93 nós e hoje nunca é usado para ensinar.
2. **Pratica com retorno imediato** (4 a 6 telas) — responde, vê na hora se
   acertou e uma linha de porquê, segue. Formatos variados: reconhecer o
   conceito, achar o erro, comparar dois casos — não só prever a saída.
3. **Refuta, só se houver hipótese de crença** (3 a 5 telas) — o percurso
   socrático, curto.
4. **Fecha mostrando o que ela construiu** (1 tela) — o mapa das premissas
   que acenderam, o nome técnico e o progresso.

**Uma exceção deliberada ao retorno imediato.** Quando a resposta errada
levanta hipótese de crença, a tela não explica o porquê: diz "vamos olhar
isso com calma" e entra na refutação. Se explicasse, a refutação viraria
repetição — e V3 passaria a medir explicação e refutação juntas, sem poder
separá-las.

**O reteste sai de perto da refutação.** Hoje ele vem na tela seguinte, logo
depois de o aluno afirmar a negação da crença: acertar ali é quase
automático. Ele passa para o fim da sessão, depois de outra unidade.

## O estudo

De 10 a 15 estudantes que já cursaram ou cursam a disciplina com C, um de
cada vez, presencialmente, em cerca de 30 minutos cada.

**O que acontece na sessão:**

1. Consentimento e código anônimo (P01…P15). Nome e matrícula ficam em
   papel, fora do banco.
2. Três perguntas rápidas sobre experiência com C.
3. **Duas unidades**, pensando em voz alta. O pesquisador usa apenas
   lembretes padronizados ("continue pensando em voz alta"), definidos antes
   da coleta: nenhuma pista sobre o conteúdo, nenhuma correção, nenhum
   direcionamento.
4. Entrevista curta: o que achou, o que confundiu, faria outra unidade.

**O que cada subpergunta mede:**

| Subpergunta | Medida | De onde vem |
| --- | --- | --- |
| V1 funciona | conclui sem intervenção (sim/não); minutos por unidade; onde parou se parou | log de eventos |
| V2 diagnóstico | a crença detectada bate com a verbalizada (concorda / discorda / inconclusivo), por ocorrência | gravação de áudio × evento `misconception_detected` |
| V3 refutação | escolheu de novo a mesma ideia errada no item de reteste (sim/não) | evento `belief_retested` |
| V4 aceitação | SUS (10 itens) + três perguntas abertas | questionário ao fim |

**Como cada episódio de V2 é classificado.** Sem regra escrita, V2 vira
opinião do pesquisador sobre a fala dos outros. São três categorias, e elas
entram no TCC como codebook:

| Classificação | Critério |
| --- | --- |
| Compatível | a fala traz explicitamente a mesma relação conceitual que a crença afirma |
| Incompatível | a fala apresenta explicação que contradiz a crença detectada (inclusive "li errado o enunciado") |
| Inconclusiva | a fala não traz evidência suficiente para decidir |

Uma segunda pessoa classifica pelo menos um terço dos episódios, às cegas.
Divergiu, os dois discutem e a regra de decisão é registrada. Com poucos
episódios, o que se reporta é a contagem e os casos — não um coeficiente de
concordância, que seria instável nesse tamanho.

Com 10 a 15 pessoas não há teste de hipótese: os números são descritivos e o
que sustenta as conclusões são os casos. Cada divergência entre a hipótese
do sistema e a fala vira um achado, com transcrição — e um episódio
incompatível vale mais para o trabalho do que dez compatíveis, porque mostra
onde a regra falha.

O pensar em voz alta é o instrumento principal de V2, e é ele que transforma
este estudo de "testei com uns colegas" em método defensável.

Todo o dado bruto já sai do sistema hoje: o log é append-only, a sessão
inteira é reconstruível a partir dele, e a exportação gera três tabelas
(respostas, sessões, calibração).

## Ameaças à validade

Seis, e cada uma tem uma contramedida no desenho — não só um parágrafo de
ressalva no fim do texto.

| Ameaça | Contramedida |
| --- | --- |
| O aluno acerta o reteste porque acabou de afirmar a negação da crença | reteste no fim da sessão, depois de outra unidade |
| O retorno imediato ensina, e V3 não consegue separar isso da refutação | retorno neutro quando há hipótese de crença |
| Ninguém erra com convicção, e V2/V3 ficam sem episódios | recrutar quem está cursando agora; usar os tópicos com mais crenças mapeadas; medir a taxa no ensaio antes de marcar a coleta |
| Pensar em voz alta muda o próprio raciocínio | tratado como evidência qualitativa, nunca como leitura do que a pessoa pensa |
| O pesquisador contamina a sessão | lembretes padronizados, escritos antes |
| A hipótese está certa mas a fala não revela | existe a categoria "inconclusiva", e ela é reportada |

A ameaça mais provável é a terceira. Se o ensaio com dois colegas produzir
zero episódios, o desenho muda antes da coleta, não depois.

## Onde isto se apoia

A contribuição precisa ser posicionada contra quatro literaturas, e nenhuma
delas foi lida com cuidado ainda — esta lista é o que **falta verificar**,
não o que já está citado.

- **Avaliação com certeza declarada.** Pedir confiança junto com a resposta
  não é novo; é usado em avaliação há décadas. O texto precisa dizer o que
  faz de diferente: usar esse sinal para **escolher o percurso**, não para
  pontuar.
- **Teoria dos espaços de conhecimento.** A função que escolhe onde intervir
  é a fronteira entre o que está confirmado e o que ainda não está — o
  *fringe*. Isso tem nome e literatura.
- **Mudança conceitual e textos de refutação.** Confrontar a concepção antes
  de apresentar a correta é uma linha estabelecida em ensino de ciências.
- **Sistemas tutores inteligentes.** O laço avaliar → modelar o aluno →
  adaptar → verificar é a arquitetura clássica da área. Apresentá-lo como
  novidade seria o erro mais fácil de cometer aqui.

O que sobra como contribuição depois desse desconto: **o grafo de premissas
como esboço de prova, com o percurso de refutação montado a partir dele** —
nenhuma das perguntas do percurso existe escrita no domínio —, aplicado a um
catálogo de 34 concepções errôneas de ponteiros em C.

## O que fica de fora

Cada item aqui foi cortado por um motivo, e o motivo entra na seção de
limitações do TCC — não é lacuna, é recorte.

- **Comparação entre socrático e explicação direta.** Exige 30 a 40
  participantes e força o sistema a esconder o acerto do aluno. O braço de
  controle continua implementado e testado; só não é usado nesta coleta.
- **Retenção.** Não há reteste uma semana depois. O que se mede é correção
  dentro da sessão, e o texto precisa dizer isso com essas palavras.
- **Ganho de aprendizagem com pré e pós-teste.** Exigiria um instrumento
  validado que ainda não existe. Fica como trabalho futuro, junto com a
  retenção.
- **Os 12 tópicos.** A coleta usa 2 ou 3 unidades. As outras continuam no
  domínio, prontas.
- **Uso fora de laboratório.** Ninguém usa sozinho em casa nesta fase: sem o
  pensar em voz alta, V2 não tem como ser respondida.

## Cronograma proposto

Seis semanas até os dados na mão, começando em 18/09/2026. **Ajustar à data
de defesa e ao parecer do comitê de ética**, que hoje não se sabe em que
estado está.

| Até | O quê |
| --- | --- |
| 02/10 | Uma unidade reconstruída, funcionando ponta a ponta: ensina, pratica com retorno, refuta, fecha |
| 09/10 | Roteiro da sessão, termo de consentimento, questionário de percepção, ficha de observação |
| 09/10 | Ensaio com 2 colegas: cronometrar, achar o que trava, ajustar |
| 23/10 | Coleta com 10 a 15 participantes |
| 30/10 | Transcrição dos trechos que importam e análise das quatro subperguntas |
| a definir | Escrita |

O risco de prazo aqui é o comitê de ética, não o software. Se o projeto
precisar de submissão e ela ainda não foi feita, o caminho crítico passa a
ser esse.

## Decisões pendentes

São seis, e nenhuma pode ser respondida sem você. As três primeiras mudam o
cronograma.

- [ ] **Comitê de ética:** o projeto precisa de submissão? Já foi feita? Em
      que estado está?
- [ ] **Data da defesa**, e portanto a data-limite real da coleta.
- [ ] **De onde vêm os participantes:** qual turma, qual período, quem faz o
      convite. Preferência por quem está cursando C agora: quem já passou e
      foi bem pode não disparar crença nenhuma.
- [ ] **Quais tópicos entram na coleta.** Sugestão: KC 07 (ponteiro e array)
      e KC 09 (`free` e ponteiro pendente) — são os que têm mais crenças
      mapeadas e onde a refutação atravessa outros tópicos.
- [ ] **Gravação de áudio:** o termo de consentimento vai autorizá-la? Sem
      áudio, V2 vira anotação do observador — mais fraca, mas ainda possível.
- [ ] **Revisão das 12 atividades novas** escritas nas últimas sessões. Elas
      alimentam a medição.
