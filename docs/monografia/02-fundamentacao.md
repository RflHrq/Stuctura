# 2. Fundamentação

As ideias que sustentam o Structura, e o que cada uma obriga o sistema a
fazer. As referências marcadas **[conferir]** precisam ser abertas na
obra antes da versão final: é a regra do projeto, e a lista completa está
no fim do capítulo.

## 2.1 Saber errado não é não saber

Uma concepção errônea é uma ideia estável e coerente para quem a tem, que
produz respostas erradas de forma sistemática. Não é esquecimento nem
distração. Quem acredita que "array e ponteiro são a mesma coisa" acerta
várias questões com essa ideia — `a[i]` e `p[i]` funcionam igual, os dois
podem ser passados para uma função — e só tropeça em `sizeof`. A ideia se
sustenta porque quase sempre funciona.

A literatura de mudança conceitual descreve por que informação nova não
basta: a pessoa encaixa a explicação correta dentro da ideia antiga, e
sai com as duas **[conferir: Posner et al., 1982]**. Para substituir uma
concepção, a nova ideia precisa ser inteligível, plausível e mais
frutífera do que a antiga — e a pessoa precisa, antes, estar insatisfeita
com a que tem. É esse o papel do confronto.

Em programação, o fenômeno está documentado de longa data, e há revisões
que catalogam as dificuldades de estudantes iniciantes **[conferir: Qian
e Lehman, 2017]**. A dissertação de Sorva (2012) organiza boa parte dessa
literatura em torno do modelo de máquina que o estudante constrói — a
"máquina nocional" —, e é a fonte de que o catálogo do sistema mais se
serve (Capítulo 4).

## 2.2 Perguntar a certeza

Uma resposta errada, sozinha, não diz se a pessoa não sabe ou se sabe
errado. A certeza declarada é o sinal mais barato que separa os dois:
custa um toque e vem da própria pessoa. Pedir a confiança junto com a
resposta não é novo — é usado em avaliação há décadas, em esquemas que
pontuam a resposta segundo a certeza declarada **[conferir:
Gardner-Medwin, 2006; Hunt, 2003]**. O que o Structura faz de diferente é
usar esse sinal para **escolher o percurso**, e não para pontuar: o erro
com "chutei" leva ao ensino; o erro com convicção, pela razão de uma
concepção mapeada, leva à demonstração.

Três cuidados decorrem disso. A certeza não mede o estado mental da
pessoa — ela roteia a intervenção, e uma marcação por hábito gera uma
hipótese errada. A escala tem três pontos porque precisa caber num toque
dentro do ritmo da atividade. E a razão escolhida pesa tanto quanto a
certeza: sem ela, o sistema não saberia **qual** ideia sustenta o erro.

## 2.3 O grafo de premissas e a fronteira

O conteúdo de cada tópico é um grafo de premissas que vai de fatos
observáveis a uma conclusão, e cada concepção errônea nega exatamente uma
premissa. A escolha de onde intervir — a premissa em que a pessoa está, e
não a lição seguinte do livro — aproxima-se da noção de fronteira da
teoria dos espaços de conhecimento, em que o estado de conhecimento de
uma pessoa determina o que ela está pronta para aprender **[conferir:
Doignon e Falmagne, 1999]**. O Structura não estima o estado de
conhecimento por um modelo probabilístico: com poucos dados, os
parâmetros seriam inventados e deixariam de ser inspecionáveis. Ele usa
o que a pessoa acabou de responder, premissa por premissa.

## 2.4 Prever, observar, explicar

A demonstração do sistema segue a sequência conhecida como
prever-observar-explicar: a pessoa compromete-se com uma previsão antes de
ver o fenômeno, observa o que acontece e, diante da discrepância, revê a
explicação **[conferir: White e Gunstone, 1992]**. A previsão é o que dá
força ao confronto: a contradição deixa de ser entre o estudante e o
sistema — em quem ele poderia simplesmente não acreditar — e passa a ser
entre o que **ele** previu e o que a máquina fez. É também a lógica dos
textos de refutação, que enunciam a concepção errônea antes de
apresentar a correta **[conferir: Tippett, 2010]**: a tela "Você disse"
repete a ideia da pessoa, como razoável, antes de mostrar a máquina.

Em programação há uma vantagem que outras áreas não têm: o fenômeno é
reproduzível e verificável. O que um programa faz não depende de quem
conta. Por isso as demonstrações do Structura são conferidas por
compilador, e a tela pode dizer, sem exagero, "a máquina respondeu".

## 2.5 Ensinar por passos

A quem não sabe, o sistema não mostra a ideia inteira de uma vez:
oferece uma escada de passos, do mais mecânico até a ideia, com retorno
imediato a cada passo e uma ideia nova por passo. É o princípio do
exemplo que cresce e da carga controlada **[conferir: literatura de
carga cognitiva e de exemplos resolvidos]**: cada passo muda uma coisa
só em relação ao anterior, e o tópico inteiro trabalha as mesmas duas ou
três variáveis.

## 2.6 Tutores inteligentes

O laço avaliar → modelar o estudante → adaptar → verificar é a
arquitetura clássica dos sistemas tutores inteligentes **[conferir:
VanLehn, 2011; Woolf, 2009]**. Apresentá-lo como novidade seria um erro.
O que este trabalho acrescenta, depois desse desconto, é a combinação de
um catálogo de concepções errôneas com procedência declarada, ligado a
um grafo de premissas, com demonstrações verificadas por compilador — e
um método de verificação em que o material de ensino é testado contra o
programa que ele descreve.

## 2.7 Desempenho não é aprendizagem

O que se observa dentro de uma sessão é desempenho, e desempenho é índice
ruim de aprendizagem: acertar logo depois de ver a resposta não garante
que a ideia ficou **[conferir: Soderstrom e Bjork, 2015]**. Por isso o
sistema reconfere, no fim do tópico, cada premissa trabalhada, com outras
premissas no meio — e por isso o fechamento fala de assimilação **nesta
sessão**, e não de aprendizagem.

## Referências a conferir

Nenhuma destas entra na versão final sem ter sido aberta na obra, com a
página citada quando for o caso:

- BROOKE, J. SUS: a quick and dirty usability scale. 1996. (Apêndice A)
- DOIGNON, J.-P.; FALMAGNE, J.-C. *Knowledge Spaces*. Springer, 1999.
- GARDNER-MEDWIN, A. R. Confidence-based marking. 2006.
- HUNT, D. P. The concept of knowledge and how to measure it. 2003.
- POSNER, G. J. et al. Accommodation of a scientific conception: toward a
  theory of conceptual change. *Science Education*, 1982.
- QIAN, Y.; LEHMAN, J. Students' misconceptions and other difficulties
  in introductory programming: a literature review. *ACM TOCE*, 2017.
- SODERSTROM, N. C.; BJORK, R. A. Learning versus performance: an
  integrative review. *Perspectives on Psychological Science*, 2015.
- TIPPETT, C. D. Refutation text in science education: a review of two
  decades of research. 2010.
- VANLEHN, K. The relative effectiveness of human tutoring, intelligent
  tutoring systems, and other tutoring systems. *Educational
  Psychologist*, 2011.
- WHITE, R.; GUNSTONE, R. *Probing Understanding*. 1992.
- WOOLF, B. P. *Building Intelligent Interactive Tutors*. 2009.
- W3C. *Web Content Accessibility Guidelines (WCAG) 2.1*, 2018. (3.7)
- Literatura de carga cognitiva e de exemplos resolvidos, a escolher.

A referência já conferida no projeto, com página, é Sorva (2012); ela e
as demais fontes do catálogo estão no Capítulo 4.
