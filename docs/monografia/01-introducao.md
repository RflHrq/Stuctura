# 1. Introdução

## 1.1 O problema

Ponteiros são, há décadas, um dos pontos em que o ensino de programação
em C mais tropeça. A dificuldade não está só em não saber: está em saber
errado. Um estudante pode atravessar um material inteiro sobre ponteiros,
acertar boa parte dos exercícios e sair com a mesma ideia errada com que entrou: por exemplo, a de que um array e um ponteiro são a mesma coisa,
ideia que funciona em quase todos os casos e só falha diante de `sizeof`.
Uma concepção errônea desse tipo (*misconception*, na literatura em inglês, o termo do título) é estável e coerente para quem a tem, e
por isso resiste à informação nova: a explicação correta é lida e
encaixada na ideia antiga, ou guardada à parte, sem entrar em conflito com
ela (POSNER et al., 1982, p. 221).

Daí decorrem duas dificuldades práticas. A primeira é de diagnóstico: uma
resposta errada, sozinha, não distingue quem não sabe de quem sabe errado,
e os dois casos pedem intervenções diferentes: a quem não sabe, é preciso
construir a ideia; a quem sabe errado, é preciso desmontar a ideia que
está no lugar. A segunda é de intervenção: dizer ao estudante qual é a
resposta certa não basta quando ele tem razões para acreditar em outra.

## 1.2 A proposta

Este trabalho apresenta o Structura, um sistema de ensino de ponteiros
em C que trata as duas dificuldades com dois mecanismos.

O diagnóstico cruza três sinais que o próprio estudante fornece numa
única tela: a resposta, a razão que a sustenta e a certeza declarada
("tenho certeza", "acho que sei", "chutei"). Cada alternativa errada de
cada questão está ligada a uma concepção errônea de um catálogo com
procedência declarada; a razão escolhida diz qual ideia sustenta a
resposta, e a certeza separa o chute da convicção. Desse cruzamento saem
quatro situações: o estudante sabe, não sabe, acha que sabe (sustenta uma
concepção errônea) ou acertou sem firmeza.

A intervenção depende da situação. A quem não sabe, o sistema oferece
uma escada de passos curtos, do mais mecânico até a ideia, com retorno
imediato a cada passo. A quem acha que sabe, o sistema não explica:
mostra um programa pequeno, pede que o estudante preveja o que ele faz e,
em seguida, mostra o que a máquina de fato fez: a saída do programa, ou
o que o compilador disse dele. E quem erra depois de subir a escada recebe
uma revisão curta, com o código da ideia animado linha a linha numa cena: a caixa que nasce, o valor que entra, o ponteiro com o seu bilhete.
Todas essas demonstrações e cenas foram compiladas e executadas por um
conferidor automático antes de entrar no sistema: o que a tela afirma
que a máquina faz, a máquina faz.

## 1.3 Objetivos

**Objetivo geral.** Construir e verificar um sistema que diagnostique, em
treze tópicos de ponteiros em C, se o estudante sabe, não sabe ou sustenta
uma concepção errônea, e que conduza cada caso por um percurso próprio,
com demonstrações conferidas por compilador.

**Objetivos específicos.**

1. Organizar o conteúdo de ponteiros em C em premissas encadeadas, com
   cada concepção errônea do catálogo ligada à premissa que ela nega.
2. Implementar o diagnóstico que combina resposta, razão e certeza
   declarada, e a escolha do percurso a partir dele.
3. Escrever, para cada premissa, uma escada de passos para quem não sabe,
   uma demonstração com previsão para cada concepção errônea e uma cena
   que anima a revisão.
4. Verificar mecanicamente que todo trecho de código das escadas e das
   demonstrações compila e faz o que o texto afirma, e que cada cena
   mostra o que o programa faz.
5. Verificar o comportamento do sistema com estudantes simulados, que
   respondem segundo perfis definidos, em todos os tópicos.

## 1.4 A pergunta, e o recorte

A pergunta que este trabalho responde é de construção e verificação:

> É possível construir um sistema que diagnostique concepções errôneas
> sobre ponteiros em C a partir da resposta, da razão e da certeza
> declarada, e que as confronte com demonstrações verificadas por
> compilador, de modo que o conteúdo e o comportamento possam ser
> conferidos sem depender da opinião de quem o escreveu?

O trabalho não avalia o sistema com estudantes. A pergunta sobre se
estudantes de graduação conseguem e querem completar a sessão, e se a
hipótese de concepção errônea gerada pelo sistema coincide com o que eles
pensam, exige um estudo com participantes que não coube no prazo. Esse
estudo está desenhado e documentado (Apêndice A) e é o primeiro dos
trabalhos futuros (Capítulo 7). O que se afirma aqui, portanto, é mais
modesto e inteiramente conferível: o sistema faz o que diz fazer, o
conteúdo que ele mostra está correto segundo o compilador, e cada
concepção errônea que ele afirma diagnosticar tem procedência declarada.

## 1.5 Contribuições

1. Um catálogo de 61 concepções errôneas sobre ponteiros em C, cada uma
   com procedência declarada e ligada à premissa que nega (Capítulo 4).
2. Um diagnóstico que usa a certeza declarada para escolher o
   percurso, e não para pontuar.
3. Um conjunto de 80 demonstrações com previsão (uma para cada concepção errônea em cada tópico em que ela aparece) e 402 passos de
   escada, além de 79 cenas animadas, todos conferidos por compilador.
4. Um método de verificação de conteúdo didático de programação em que o
   compilador é o árbitro: o texto que afirma o que um programa faz é
   testado contra o programa.

## 1.6 Organização do texto

O Capítulo 2 apresenta as ideias que sustentam o sistema e os trabalhos
relacionados. O Capítulo 3
descreve o Structura: o domínio, o diagnóstico, a trilha e a interface. O
Capítulo 4 trata da procedência do catálogo de concepções errôneas. O
Capítulo 5 descreve como o sistema foi construído e verificado, e o
Capítulo 6 apresenta os resultados dessa verificação. O Capítulo 7
discute as limitações e os trabalhos futuros, e o Capítulo 8 conclui.
