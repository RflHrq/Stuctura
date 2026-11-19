# 2. Fundamentação

As ideias que sustentam o Structura, e o que cada uma obriga o sistema a
fazer. Cada obra citada foi aberta, e onde e como está registrado em
[conferencia-das-referencias.md](conferencia-das-referencias.md).

## 2.1 Saber errado não é não saber

Uma concepção errônea é uma ideia estável e coerente para quem a tem, que
produz respostas erradas de forma sistemática. Não é esquecimento nem
distração. Quem acredita que "array e ponteiro são a mesma coisa" acerta várias questões com essa ideia (`a[i]` e `p[i]` funcionam igual, os dois podem ser passados para uma função) e só tropeça em `sizeof`. A ideia se
sustenta porque quase sempre funciona.

A literatura de mudança conceitual descreve por que informação nova não
basta. Posner et al. (1982, p. 212-213) distinguem dois modos de mudança:
lidar com o novo usando os conceitos que se tem, e substituir ou
reorganizar os conceitos centrais, o que chamam de acomodação. Diante de
uma informação que contradiz o que pensa, a pessoa raramente acomoda: é
mais comum encaixar a informação na concepção que já tem, ou guardá-la num
compartimento à parte, onde ela não entra em conflito com a antiga
(POSNER et al., 1982, p. 221). Para que a acomodação aconteça, os autores
propõem quatro condições: a pessoa precisa estar insatisfeita com a
concepção que tem, e a nova precisa ser inteligível, parecer plausível
desde o início e mostrar-se frutífera (p. 214). A insatisfação vem da
anomalia levada a sério, que produz o conflito cognitivo (p. 224), e por
isso os autores recomendam demonstrações e problemas que o criem (p. 225).
É esse o papel do confronto no Structura.

Uma nota de vocabulário: Posner et al. chamam de assimilação o primeiro
modo, o de encaixar o novo no que já se tinha. Neste texto, como no
sistema, "assimilou" quer dizer outra coisa: que a pessoa acertou de novo, com outras premissas no meio (Capítulo 3).

Em programação, o estudo das concepções errôneas começa nos anos 1980,
com nomes variados (dificuldades, erros, *bugs*, concepções errôneas) e sem uma definição aceita por todos (QIAN; LEHMAN, 2017, p. 1:2-1:3). Na
revisão de Qian e Lehman (2017, p. 1:1), as dificuldades dos iniciantes
aparecem no conhecimento sintático, no conceitual e no estratégico, e os
autores recomendam que a pesquisa vá além de documentá-las e incorpore as
teorias de mudança conceitual. A dissertação de Sorva (2012) organiza boa
parte dessa literatura em torno do modelo de máquina que o estudante constrói, a "máquina nocional", e é a fonte de que o catálogo do
sistema mais se serve (Capítulo 4).

## 2.2 Perguntar a certeza

Uma resposta errada, sozinha, não diz se a pessoa não sabe ou se sabe
errado. A certeza declarada é o sinal mais barato que separa os dois:
custa um toque e vem da própria pessoa. Pedir a confiança junto com a
resposta não é novo. A marcação pela certeza foi muito pesquisada antes
mesmo da avaliação por computador, e Gardner-Medwin (2006) relata dez anos de uso na University College London, sobretudo em cursos de medicina, com três níveis de certeza e penalidade
crescente para o erro convicto. O argumento dele é o deste trabalho: um
acerto por sorte não é conhecimento, e uma concepção errônea firme é
muito pior do que a ignorância reconhecida. O que o Structura faz de
diferente é usar esse sinal para **escolher o percurso**, e não para
pontuar: o erro com "chutei" leva ao ensino; o erro com convicção, pela
razão de uma concepção mapeada, leva à demonstração.

Três cuidados decorrem disso. A certeza não mede o estado mental da pessoa: ela roteia a intervenção, e uma marcação por hábito gera uma
hipótese errada. A escala tem três pontos, como a de Gardner-Medwin
(2006), porque precisa caber num toque dentro do ritmo da atividade; mas
ele nomeia os níveis com números ou termos neutros, porque palavras como
"certeza" e "chute" querem dizer coisas diferentes para pessoas
diferentes, e o Structura usa palavras ("chutei", "acho que sei", "tenho certeza"); o custo disso está no Capítulo 7. E a razão escolhida pesa
tanto quanto a certeza: sem ela, o sistema não saberia **qual** ideia
sustenta o erro.

## 2.3 O grafo de premissas e a fronteira

O conteúdo de cada tópico é um grafo de premissas que vai de fatos
observáveis a uma conclusão, e cada concepção errônea nega exatamente uma
premissa. A escolha de onde intervir (a premissa em que a pessoa está, e não a lição seguinte do livro) aproxima-se da noção de fronteira da
teoria dos espaços de conhecimento. Ali, o estado de conhecimento de uma
pessoa é o conjunto de problemas que ela resolve, e a fronteira externa
reúne os problemas que, acrescentados ao estado, formam outro estado: é o
que a pessoa está pronta para aprender, e onde o progresso acontece
(FALMAGNE et al., 2006). O Structura não estima o estado de conhecimento
por um modelo probabilístico, como faz o sistema descrito pelos autores:
com poucos dados, os parâmetros seriam inventados e deixariam de ser
inspecionáveis. Ele usa o que a pessoa acabou de responder, premissa por
premissa.

## 2.4 Prever, observar, explicar

A demonstração do sistema segue a sequência prever-observar-explicar, que
White e Gunstone (1992, cap. 3) descrevem como três tarefas: prever o
resultado de um acontecimento, justificando a previsão; descrever o que se
vê acontecer; e reconciliar o conflito entre o previsto e o observado. No
Structura, a justificativa já veio antes: é a razão escolhida na pergunta
de diagnóstico. A previsão é o que dá força ao confronto: a contradição
deixa de ser entre o estudante e o sistema, em quem ele poderia simplesmente não acreditar, e passa a ser entre o que **ele** previu e o
que a máquina fez.

É também a lógica dos textos de refutação, que ativam a concepção
errônea, refutam-na explicitamente e só então enunciam a correta
(NUSSBAUM; CORDOVA; REHMAT, 2017, p. 23): a tela "Você disse" repete a
ideia da pessoa, como razoável, antes de mostrar a máquina. Três décadas
de pesquisa comparam esses textos com os expositivos, a favor dos
primeiros (p. 23), e a revisão de Tippett observa que a refutação tende a
funcionar melhor quando a concepção errônea é uma ideia única, e não um
conceito complexo (TIPPETT, 2010, p. 965 apud NUSSBAUM; CORDOVA; REHMAT,
2017, p. 31). É o desenho do grafo de premissas, em que cada concepção
nega uma premissa só.

Em programação há uma vantagem que outras áreas não têm: o fenômeno é
reproduzível e verificável. O que um programa faz não depende de quem
conta. Por isso as demonstrações do Structura são conferidas por
compilador, e a tela pode dizer, sem exagero, "a máquina respondeu".

## 2.5 Ensinar por passos

A quem não sabe, o sistema não mostra a ideia inteira de uma vez:
oferece uma escada de passos, dos guiados aos de prática, com retorno a
cada passo e uma ideia nova por passo. O desenho segue quatro efeitos que a
teoria da carga cognitiva descreve (SWELLER; VAN MERRIËNBOER; PAAS, 2019).
Os passos guiados mostram o programa e pedem uma parte dele, perto do
exemplo resolvido (p. 265) e do problema de completar, este proposto justamente para a programação introdutória, em que o estudante recebe um
programa incompleto para terminar (p. 268). A orientação esmaece ao longo
da escada, dos passos guiados aos de prática, porque o que ajuda o novato
fica redundante para quem já avançou (p. 277). E cada passo muda uma coisa
só em relação ao anterior, como no efeito dos elementos isolados, em que
as partes vêm antes das relações entre elas (p. 279). O tópico inteiro
trabalha as mesmas duas ou três variáveis.

## 2.6 Tutores inteligentes

O laço perguntar → inferir o que a pessoa pensa → escolher a intervenção
→ reconferir é a arquitetura clássica dos sistemas tutores inteligentes,
e apresentá-lo como novidade seria um erro. VanLehn (2006) descreve esses
sistemas por dois laços: o externo escolhe a próxima tarefa, com base num
modelo do estudante; o interno acompanha cada passo da tarefa, com retorno
e dicas, e atualiza esse modelo. No Structura, o laço externo escolhe a
premissa e o caminho; o interno é a escada, com retorno a cada passo. Na
classificação de VanLehn (2011, p. 197), é um tutor por passo; e os tutores inteligentes, quase todos por passo ou subpasso, ficaram, na
revisão dele, perto da tutoria humana em efeito (0,76 contra 0,79 desvio
padrão, contra nenhuma tutoria).

O que este trabalho acrescenta, depois desse desconto, é a combinação de
um catálogo de concepções errôneas com procedência declarada, ligado a um
grafo de premissas, com demonstrações verificadas por compilador. Acrescenta, ainda, um método de verificação em que o material de ensino é testado contra o
programa que ele descreve.

## 2.7 Desempenho não é aprendizagem

O que se observa durante a instrução é desempenho, e desempenho é, muitas
vezes, índice pouco confiável de que a aprendizagem (a mudança relativamente permanente, que se mede por retenção de longo prazo ou por transferência) aconteceu (SODERSTROM; BJORK, 2015, p. 176). Acertar logo
depois de ver a resposta não garante que a ideia ficou. Por isso o sistema
reconfere, no fim do tópico, cada premissa trabalhada, com outras premissas no meio; e por isso o fechamento fala de assimilação **nesta
sessão**, e não de aprendizagem.

## 2.8 Trabalhos relacionados

Os trabalhos abaixo foram escolhidos por compartilharem com o Structura
pelo menos um destes elementos: o domínio de ponteiros em C, o estudo de
concepções errôneas com dados de um sistema, a modelagem formal do estado
de conhecimento, ou o modelo de máquina que o estudante precisa construir.
Para cada um, diz-se o que ele faz e onde o Structura se põe em relação a
ele; o Quadro 2.1, ao fim, resume a comparação.

### 2.8.1 TEDViT: a memória e o mundo do problema, lado a lado

Yamashita et al. (2017) descrevem o TEDViT, um sistema de visualização de
programas, e uma prática em sala com ele no ensino de ponteiros em C. O
sistema mostra, ao mesmo tempo e em sincronia, a imagem da memória, com o
valor concreto de cada variável, e o mundo do domínio, com as estruturas de
dados que o programa manipula; o que aparece no mundo do domínio segue uma
política de visualização definida pelo professor. Nos questionários de
autoavaliação aplicados depois das aulas, a dispersão das respostas sobre o
grau de compreensão, o ritmo e a dificuldade foi menor na turma de 2015,
que usou o sistema, do que nas de 2013 e 2014, o que os autores leem como
redução da desigualdade de compreensão entre os participantes (p. 12).

O artigo não descreve modelo do estudante nem diagnóstico individual: a
adaptação que o sistema oferece é a que o professor configura. O Structura
trabalha no mesmo domínio e também mostra a memória em funcionamento (as
cenas, 3.6), mas parte do diagnóstico de cada premissa, pessoa por pessoa,
e escolhe a intervenção a partir dele.

### 2.8.2 Iltis: medir e descobrir concepções errôneas com dados de um tutor

Schmellenkamp, Latys e Zeume (2023) defendem estudar as concepções
errôneas em métodos formais combinando métodos quantitativos e
qualitativos: até ali, elas tinham sido estudadas sobretudo de forma
qualitativa, em geral com entrevistas de menos de 20 pessoas. Os autores
propõem dois fluxos de trabalho, um para medir quão comum é uma concepção
já descrita qualitativamente e outro para descobrir candidatas nos dados e
examiná-las depois, e aplicam partes deles aos exercícios de modelagem
lógica do tutor inteligente Iltis, com mais de 250 respostas em muitos dos
exercícios.

O trabalho mostra o que um tutor pode dar à pesquisa de concepções
errôneas, que é escala, mas fica na medida: trata de encontrar e contar as
concepções, e não de intervir sobre elas, e é de outro domínio. O Structura
faz o caminho inverso: parte de concepções já registradas na literatura
(Capítulo 4) e as usa para diagnosticar e intervir. O registro que ele
grava de cada sessão (3.7) poderia servir à medida que o Iltis propõe,
quando houver estudantes usando o sistema.

### 2.8.3 ALEKS e a teoria dos espaços de conhecimento

A teoria dos espaços de conhecimento, cujo primeiro artigo foi publicado
por Doignon e Falmagne em 1985 (DOIGNON; FALMAGNE, 1985 apud FALMAGNE et
al., 2006), define o estado de conhecimento como o conjunto de problemas
que a pessoa sabe resolver num tópico, e a avaliação como a busca desse
estado entre todos os possíveis (2.3). Falmagne et al. (2006) descrevem a
implementação da teoria num sistema disponível pela internet, o ALEKS (dois
dos autores são da empresa que o mantém): cada pergunta é escolhida por ser
a mais informativa, aquela que a pessoa tem cerca de 50% de chance de
acertar segundo o estado provável; a avaliação para quando a incerteza
sobre o estado fica baixa; e o resultado são duas listas, o que o estudante
sabe fazer e o que está pronto para aprender. Uma avaliação de Aritmética
mostrada no artigo levou 24 perguntas, perto da média.

O estado, ali, é feito de problemas: diz o que falta aprender, e não que
ideia errada produz o erro. O Structura toma da teoria a ideia de
fronteira, intervindo na premissa em que a pessoa está, mas registra, além
de saber e não saber, a concepção errônea que a pessoa sustenta, e é ela
que decide a intervenção.

### 2.8.4 Máquinas nocionais

Sorva (2013) reúne e comenta as linhas de pesquisa que explicam a
dificuldade do iniciante com a dinâmica de execução dos programas: as
concepções errôneas de programação, a teoria dos modelos mentais, o
construtivismo, a fenomenografia e os conceitos-limiar, examinadas em
relação à máquina nocional, o computador abstrato que executa programas de
certo tipo. Conclui que a máquina nocional é um dos grandes desafios do
ensino introdutório de programação e que deve ser objetivo explícito do
ensino. É uma revisão, e não propõe um sistema; a tese de Sorva (2012), que
é a fonte principal do catálogo do Structura (Capítulo 4), trata do mesmo
tema.

O Structura segue essa recomendação para ponteiros em C: o modelo de
memória é ensinado em premissas próprias (o kc_01 e as premissas de base de
cada tópico), e as cenas da revisão (3.6) mostram a máquina executando o
código, linha a linha.

### 2.8.5 Uma nota sobre tutores com modelos de linguagem

Uma alternativa hoje possível é gerar o retorno e as explicações de um
tutor com um modelo de linguagem de grande escala. O Structura não faz isso
durante a sessão: todo texto que a pessoa vê foi escrito antes, foi
conferido por compilador quando afirma algo sobre um programa (Capítulo 5),
e cada resposta é ligada a uma premissa e a uma concepção do catálogo. Com
isso, o comportamento é determinístico e pode ser auditado, e o que o
sistema afirma sobre C é conferido antes de chegar ao estudante. O preço é
a flexibilidade: o sistema só reconhece as concepções que o catálogo tem
(7.1). O uso de um modelo de linguagem na construção do conteúdo, e não na
sessão, está registrado na declaração de uso de inteligência artificial.

### 2.8.6 Síntese

**Quadro 2.1 — Os trabalhos relacionados e o Structura**

| Trabalho | Domínio | Diagnóstico de concepção errônea | Intervenção conforme o diagnóstico | Mostra a máquina em funcionamento |
| --- | --- | --- | --- | --- |
| TEDViT (YAMASHITA et al., 2017) | ponteiros em C | não | não | sim: memória e mundo do domínio |
| Iltis (SCHMELLENKAMP; LATYS; ZEUME, 2023) | métodos formais | mede e descobre, nos dados agregados | não | não |
| ALEKS (FALMAGNE et al., 2006) | matemática | não: avalia o que se sabe e o que falta | indica o que aprender em seguida | não |
| Sorva (2013) | programação introdutória | não se aplica: é uma revisão | não se aplica | recomenda ensinar a máquina nocional |
| Structura | ponteiros em C | sim: resposta, razão e certeza, por premissa | sim: escada, demonstração ou revisão | sim: as cenas da revisão |

*Fonte: elaborado pelo autor, a partir das obras citadas.*

Entre os trabalhos analisados, nenhum reúne, para ponteiros em C, o
diagnóstico da concepção errônea pela resposta, pela razão e pela certeza,
a intervenção escolhida por esse diagnóstico e a máquina mostrada em
funcionamento. Essa combinação, com o conteúdo conferido por compilador, é
o que o Structura acrescenta.

As obras citadas estão em [Referências](referencias.md).
