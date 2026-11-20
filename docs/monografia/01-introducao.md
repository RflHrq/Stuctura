# 1. Introdução

## 1.1 Contextualização e problema

Ponteiros são reconhecidos como um conteúdo de difícil aprendizagem para iniciantes em programação na linguagem C (YAMASHITA et al., 2017, p. 1). Parte dessa dificuldade não decorre da ausência de conhecimento, mas da presença de conhecimento incorreto. O estudante pode percorrer todo o material sobre o tema, acertar a maior parte dos exercícios e manter a concepção equivocada com que iniciou o estudo, como a de que um array e um ponteiro são a mesma coisa, ideia que produz respostas corretas em quase todos os casos e falha apenas diante do operador `sizeof`. Uma concepção errônea desse tipo (*misconception*, na literatura em língua inglesa, termo adotado no título deste trabalho) é estável e coerente para quem a sustenta e, por isso, resiste à informação nova: a explicação correta tende a ser incorporada à concepção já existente, ou mantida em um compartimento separado, sem entrar em conflito com ela (POSNER et al., 1982, p. 221).

Dessa característica decorrem duas dificuldades práticas. A primeira é de diagnóstico: uma resposta incorreta, isoladamente, não permite distinguir o estudante que desconhece o conteúdo daquele que sustenta uma concepção errônea, e os dois casos demandam intervenções distintas. No primeiro, é preciso construir o conceito; no segundo, é preciso antes confrontar a concepção existente. A segunda dificuldade é de intervenção: informar ao estudante a resposta correta não é suficiente quando ele dispõe de razões para acreditar em outra.

## 1.2 Proposta

Este trabalho apresenta o Structura, um sistema de ensino de ponteiros em C que trata as duas dificuldades por meio de dois mecanismos: um diagnóstico e uma intervenção condicionada a ele.

O diagnóstico combina três sinais fornecidos pelo próprio estudante em uma única tela: a resposta, a razão que a sustenta e a certeza declarada ("tenho certeza", "acho que sei" ou "chutei"). Cada alternativa incorreta de cada questão está associada a uma concepção errônea de um catálogo com procedência declarada. A razão escolhida indica qual ideia sustenta a resposta, e a certeza distingue a resposta dada ao acaso da resposta dada com convicção. Da combinação dos três sinais resultam quatro situações: o estudante sabe, não sabe, sustenta uma concepção errônea ou acertou sem firmeza.

A intervenção depende da situação diagnosticada. Ao estudante que não sabe, o sistema oferece uma sequência de passos curtos, denominada escada, que parte da operação mais mecânica e chega ao conceito, com retorno imediato a cada passo. Ao estudante que sustenta uma concepção errônea, o sistema não apresenta uma explicação: exibe um programa curto, solicita uma previsão do seu comportamento e, em seguida, mostra o resultado obtido na execução, isto é, a saída do programa ou a mensagem emitida pelo compilador. Ao estudante que erra depois de percorrer a escada, o sistema apresenta uma revisão breve, na qual o código relativo ao conceito é animado linha a linha em uma representação visual da memória, denominada cena. Todas as demonstrações e cenas foram compiladas e executadas por um conferidor automático antes de serem incorporadas ao sistema, de modo que as afirmações exibidas sobre o comportamento de um programa correspondem ao comportamento observado na execução.

## 1.3 Justificativa

A proposta justifica-se por três razões. A primeira é teórica. A revisão de Qian e Lehman (2017, p. 1) recomenda que a pesquisa sobre as dificuldades de iniciantes em programação vá além de documentá-las e incorpore as teorias de mudança conceitual, e Sorva (2013) conclui que o modelo de execução dos programas, a chamada máquina nocional, deve constituir objetivo explícito do ensino introdutório. Um sistema que diagnostica a concepção errônea e a confronta com o comportamento observável do programa busca atender às duas recomendações no domínio de ponteiros em C.

A segunda razão é a lacuna identificada nos trabalhos relacionados. Entre os trabalhos analisados na Seção 2.8, nenhum reúne, para ponteiros em C, o diagnóstico individual da concepção errônea, a intervenção selecionada a partir desse diagnóstico e a visualização da execução. Além disso, o catálogo de concepções errôneas de programação utilizado como fonte principal deste trabalho, o de Sorva (2012), foi produzido em contextos de ensino com Java, Python e BASIC e não registra concepções sobre construtos próprios de C, como a alocação dinâmica e a aritmética de ponteiros (Seção 4.3), o que torna necessária uma curadoria específica.

A terceira razão é metodológica. Materiais didáticos de programação fazem afirmações sobre o comportamento de programas, e essas afirmações podem ser verificadas mecanicamente. Ao submeter o conteúdo ao compilador, o trabalho reduz a dependência do julgamento de quem o redigiu, cuidado relevante em um contexto em que parte do conteúdo foi elaborada com assistência de um modelo de linguagem.

## 1.4 Objetivos

### 1.4.1 Objetivo geral

Desenvolver e verificar um sistema que diagnostique, em treze tópicos de ponteiros em C, se o estudante sabe, não sabe ou sustenta uma concepção errônea, e que conduza cada caso por um percurso próprio, com demonstrações conferidas por compilador.

### 1.4.2 Objetivos específicos

Para alcançar o objetivo geral, foram definidos os seguintes objetivos específicos:

1. organizar o conteúdo de ponteiros em C em premissas encadeadas, associando cada concepção errônea do catálogo à premissa que ela nega;
2. implementar o diagnóstico que combina resposta, razão e certeza declarada, bem como a escolha do percurso a partir dele;
3. elaborar, para cada premissa, uma escada de passos destinada a quem não sabe, uma demonstração com previsão para cada concepção errônea e uma cena que anima a revisão;
4. verificar mecanicamente que todo trecho de código das escadas e das demonstrações compila e se comporta como o texto afirma, e que cada cena representa o estado real do programa;
5. verificar o comportamento do sistema com estudantes simulados, que respondem segundo perfis definidos, em todos os tópicos.

## 1.5 Questão de pesquisa e delimitação do escopo

A questão de pesquisa que orienta este trabalho é de construção e de verificação: é possível construir um sistema que diagnostique concepções errôneas sobre ponteiros em C a partir da resposta, da razão e da certeza declarada, e que as confronte com demonstrações verificadas por compilador, de modo que o conteúdo e o comportamento do sistema possam ser conferidos sem depender do julgamento de quem os elaborou?

O trabalho não avalia o sistema com estudantes. Verificar se estudantes de graduação conseguem e desejam concluir a sessão, e se a hipótese de concepção errônea gerada pelo sistema coincide com o que eles pensam, requer um estudo com participantes que não pôde ser realizado no prazo deste trabalho. Esse estudo está planejado e documentado no Apêndice A e constitui o primeiro dos trabalhos futuros (Capítulo 7). As afirmações deste trabalho restringem-se, portanto, ao que pode ser verificado sem participantes: o sistema se comporta conforme especificado, o conteúdo que apresenta está correto segundo o compilador, e cada concepção errônea que ele se propõe a diagnosticar tem procedência declarada.

## 1.6 Procedimentos metodológicos

Trata-se de uma pesquisa aplicada, de caráter tecnológico, cujo produto é um artefato de software acompanhado da verificação de suas propriedades. O trabalho foi conduzido em quatro etapas. Na primeira, realizou-se o levantamento bibliográfico sobre concepções errôneas e mudança conceitual, certeza declarada, ensino por passos e sistemas tutores inteligentes, bem como sobre os trabalhos relacionados (Capítulo 2). Na segunda, procedeu-se à curadoria do catálogo de concepções errôneas, com a conferência das fontes nas obras primárias (Capítulo 4). Na terceira, o domínio foi modelado e o sistema foi desenvolvido, com testes automatizados escritos antes do código (Capítulo 3 e Seção 5.1). Na quarta, verificaram-se o conteúdo, por meio de compilador, e o comportamento, por meio de estudantes simulados (Capítulo 5); os resultados dessa verificação são apresentados no Capítulo 6. Não houve coleta de dados com participantes humanos.

## 1.7 Contribuições

As principais contribuições deste trabalho são:

1. um catálogo de 61 concepções errôneas sobre ponteiros em C, cada uma com procedência declarada e associada à premissa que nega (Capítulo 4);
2. um diagnóstico que utiliza a certeza declarada para selecionar o percurso de intervenção, e não para atribuir pontuação;
3. um conjunto de 80 demonstrações com previsão (uma para cada concepção errônea em cada tópico em que ela aparece) e 402 passos de escada, além de 79 cenas animadas, todos conferidos por compilador;
4. um método de verificação de conteúdo didático de programação no qual o compilador atua como árbitro: o texto que afirma o comportamento de um programa é testado contra o próprio programa.

## 1.8 Organização do texto

O restante deste trabalho está organizado como segue. O Capítulo 2 apresenta a fundamentação teórica e os trabalhos relacionados. O Capítulo 3 descreve o sistema Structura: o domínio, o diagnóstico, o percurso de aprendizagem e a interface. O Capítulo 4 trata da procedência do catálogo de concepções errôneas. O Capítulo 5 descreve o método de construção e de verificação do sistema, e o Capítulo 6 apresenta os resultados da verificação. O Capítulo 7 discute as limitações e os trabalhos futuros, e o Capítulo 8 apresenta as conclusões.
