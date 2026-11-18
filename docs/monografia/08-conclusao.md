# 8. Conclusão

Este trabalho partiu de uma dificuldade conhecida do ensino de ponteiros
em C: o estudante que sabe errado não se distingue, por uma resposta
errada, do estudante que não sabe, e não se corrige com mais explicação.
O Structura responde a isso com dois mecanismos. O diagnóstico cruza a
resposta, a razão e a certeza declarada, e com isso separa quem sabe,
quem não sabe e quem sustenta uma concepção errônea. A intervenção segue
o diagnóstico: a quem não sabe, uma escada de passos curtos; a quem acha
que sabe, uma demonstração em que ele prevê o que um programa faz e vê o
que a máquina fez.

A pergunta que o trabalho se propôs foi se é possível construir esse
sistema de modo que o conteúdo e o comportamento possam ser conferidos
sem depender da opinião de quem o escreveu. A resposta, nos limites do
que foi feito, é sim. Os 13 tópicos, com 79 premissas, 402 passos e 80
demonstrações, foram conferidos contra o compilador: o que cada passo e
cada demonstração afirma sobre um programa é o que o programa faz. No
banco, a conferência alcança as 70 questões de prever a saída com
resposta em valor; o resto depende de leitura (7.1). O comportamento foi
conferido com dez perfis de estudante simulado em todos os tópicos: cada
caso segue o percurso que o desenho promete, e a sessão tem teto. E a
verificação mostrou o seu valor no caminho, encontrando defeitos que a
leitura humana deixara passar — entre eles, uma questão cuja resposta
certa não vale no compilador do laboratório, e oito questões cujo código
aparecia partido na tela.

O que o trabalho não responde é se o sistema ensina. Essa pergunta exige
estudantes, e é o primeiro trabalho futuro: o estudo está desenhado, e o
sistema já registra tudo o que ele precisa. Até lá, a contribuição é um
sistema verificável, um catálogo de concepções errôneas com procedência
declarada e um método em que o compilador, e não o autor, é o árbitro do
que o material de ensino afirma.
