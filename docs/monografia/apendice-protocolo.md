# Apêndice A — Protocolo do estudo com estudantes

Este apêndice apresenta o protocolo do estudo com estudantes proposto como trabalho futuro (Seção 7.2), elaborado para a versão do sistema descrita na Seção 3.

## A.1 Questões do estudo

A questão geral do estudo é se é viável diagnosticar concepções errôneas sobre ponteiros em C a partir da resposta, da razão e da certeza declarada, e confrontá-las com demonstrações, em uma sessão que estudantes de graduação consigam e desejem concluir. Essa questão desdobra-se em quatro (Quadro A.1).

**Quadro A.1 — Questões do estudo**

| Questão | Enunciado | Medida | Fonte dos dados |
| --- | --- | --- | --- |
| V1 | Os estudantes concluem a sessão sem auxílio de conteúdo por parte do pesquisador, e em quanto tempo? | conclusão (sim/não); minutos por tópico; ponto de interrupção | registro da sessão |
| V2 | A concepção errônea detectada é compatível com a explicação verbalizada pelo participante? | compatível, incompatível ou inconclusiva, por episódio | gravação de áudio comparada às concepções registradas na sessão |
| V3 | Após a demonstração, o participante altera a resposta? | reconferência ao final do tópico: resposta correta pela razão correta, ou "a ideia voltou" | registro da sessão |
| V4 | Como o participante percebe a clareza, a dificuldade e a utilidade do sistema? | *System Usability Scale* (SUS), escala de usabilidade de 10 itens (Brooke, 1996), e três perguntas abertas | questionário ao final |

A unidade de análise de V2 e de V3 não é o participante, e sim o episódio de concepção errônea detectada. Dez participantes podem gerar 25 episódios ou apenas 4, e o denominador de cada resultado é esse número.

## A.2 Procedimento da sessão

O estudo prevê de 10 a 15 estudantes que cursam ou já cursaram a disciplina com a linguagem C, atendidos individualmente, de forma presencial e supervisionada, em uma sala ou em um laboratório da universidade, em sessões de cerca de 30 minutos. A aplicação presencial permite ao pesquisador acompanhar o que o participante responde e evita a consulta a outras fontes e a ajuda de terceiros, que uma aplicação remota, pela internet, não permitiria controlar. Cada sessão tem as seguintes etapas:

1. consentimento e atribuição de um código sem dado pessoal (P01 a P15), que funciona como pseudônimo; o nome e a matrícula são registrados em papel, fora do sistema;
2. três perguntas breves sobre a experiência com a linguagem C;
3. dois tópicos na trilha, com verbalização do pensamento em voz alta. O pesquisador utiliza apenas lembretes padronizados (por exemplo, "continue pensando em voz alta"), definidos antes da coleta, sem oferecer indicações sobre o conteúdo nem correções. Sugerem-se os tópicos kc_07 (ponteiro e array) e kc_09 (`free` e ponteiro pendente), que têm o maior número de concepções mapeadas;
4. aplicação do questionário SUS e entrevista breve sobre a percepção do participante, com três perguntas abertas: o que achou, o que gerou confusão e se faria outro tópico.

As respostas de cada sessão ficam gravadas no registro do sistema e são exportadas, pelo código do participante, nas três tabelas descritas na Seção 3.7 e no Apêndice C, que fornecem os dados do sistema para V1, V2 e V3 (Quadro A.1); a verbalização, que V2 compara com a concepção detectada, vem da gravação de áudio, e a percepção (V4), do questionário e da entrevista.

## A.3 Classificação dos episódios de V2

Cada episódio é classificado conforme os critérios do Quadro A.2.

**Quadro A.2 — Classificação dos episódios de V2**

| Classificação | Critério |
| --- | --- |
| Compatível | a fala apresenta explicitamente a mesma relação conceitual afirmada pela concepção |
| Incompatível | a fala apresenta explicação que contradiz a concepção detectada (inclusive "li errado o enunciado") |
| Inconclusiva | a fala não apresenta evidência suficiente para a decisão |

Um segundo avaliador classifica ao menos um terço dos episódios, sem conhecimento da classificação do primeiro. Com poucos episódios, relatam-se a contagem e os casos, e não um coeficiente de concordância. Com 10 a 15 participantes, não se aplicam testes de hipótese: os números são descritivos, e as conclusões apoiam-se nos casos. Um episódio incompatível é mais informativo do que dez compatíveis, pois indica onde a regra de diagnóstico falha.

## A.4 Ameaças à validade

O Quadro A.3 relaciona as ameaças à validade identificadas e as respectivas contramedidas.

**Quadro A.3 — Ameaças à validade e contramedidas**

| Ameaça | Contramedida |
| --- | --- |
| A reconferência ocorre logo após a demonstração | a reconferência é realizada ao final do tópico, após as demais premissas |
| Nenhum participante erra com convicção, e V2 e V3 ficam sem episódios | recrutamento de estudantes que estejam cursando a disciplina; escolha dos tópicos com mais concepções mapeadas; medição da frequência desses erros em um ensaio com dois colegas antes do agendamento da coleta |
| A verbalização em voz alta altera o próprio raciocínio | tratamento da fala como evidência qualitativa, e nunca como leitura direta do pensamento |
| O pesquisador influencia a sessão | lembretes padronizados, definidos previamente |
| O participante consulta outras fontes ou recebe ajuda durante a sessão | sessões presenciais supervisionadas, com o pesquisador presente |
| A hipótese está correta, mas a fala não a revela | a categoria "inconclusiva" existe e é relatada |

## A.5 Pendências anteriores à coleta

O estudo envolve participantes humanos e gravação de voz. Por essa razão, nenhuma coleta deve ser iniciada antes de concluídas as seguintes providências:

1. a consulta formal à instância da UFV responsável pela ética em pesquisa com seres humanos e o cumprimento dos procedimentos por ela indicados, incluída a submissão do protocolo à apreciação ética;
2. o termo de consentimento, que informe ao participante a gravação de áudio, a finalidade do estudo e o uso dos dados;
3. um plano de gestão dos dados que defina o local de armazenamento das gravações e dos registros, as pessoas com acesso a eles, o prazo de guarda, as medidas de confidencialidade (inclusive a guarda da lista em papel que associa nomes e matrículas aos códigos) e o procedimento de exclusão de dados a pedido do participante, que deve alcançar também as cópias de segurança do registro;
4. o ensaio com dois colegas.
