# Elementos pré-textuais

A ordem e a forma (capa, folha de rosto, folha de aprovação, dedicatória,
agradecimentos) são as do modelo da UFV, em `latex/TCC_STRUCTURA.tex`,
que traz também a dedicatória e os agradecimentos do autor. O resumo, o
abstract e a declaração abaixo entram no LaTeX a partir deste arquivo. A
declaração de uso de inteligência artificial é uma afirmação do autor:
cada frase dela tem de ser confirmada por ele antes da entrega.

## Capa e folha de rosto

UNIVERSIDADE FEDERAL DE VIÇOSA
*CAMPUS* RIO PARANAÍBA
SISTEMAS DE INFORMAÇÃO

RAFAEL HENRIQUE DOS SANTOS SIMÃO

**STRUCTURA: UM SISTEMA ADAPTATIVO PARA DETECÇÃO E CORREÇÃO DE
*MISCONCEPTIONS* EM PONTEIROS NA LINGUAGEM C**

Monografia apresentada à Universidade Federal de Viçosa, como parte das
exigências para a aprovação na disciplina Trabalho de Conclusão de Curso II

Orientador: Pedro Henrique Aparecido Damaso de Melo

RIO PARANAÍBA
2026

## Resumo

Ponteiros constituem um dos conteúdos de mais difícil aprendizagem no ensino de programação em C, e parte dessa dificuldade não decorre da falta de conhecimento, mas de concepções errôneas: ideias estáveis e coerentes para quem as sustenta, que resistem à explicação correta. Uma resposta incorreta, isoladamente, não distingue o estudante que desconhece o conteúdo daquele que sustenta uma concepção errônea, e os dois casos demandam intervenções diferentes. Este trabalho apresenta o Structura, um sistema de ensino de ponteiros em C que formula, para cada premissa do conteúdo, uma hipótese diagnóstica a partir de três sinais fornecidos pelo estudante em uma mesma tela (a resposta, a razão que a sustenta e a certeza declarada) e conduz cada caso por um percurso próprio: ao estudante que não sabe, uma sequência de passos curtos com retorno imediato; ao que sustenta uma concepção errônea, uma demonstração na qual ele prevê o comportamento de um programa e observa o que a máquina faz (a saída do programa ou a mensagem do compilador); ao que erra após os passos, uma revisão com o código animado linha a linha. O conteúdo abrange 13 tópicos, com 79 premissas, um catálogo de 61 concepções errôneas com procedência declarada, 402 passos, 80 demonstrações e 79 cenas animadas. Nas demonstrações, nas cenas e em 246 dos 402 passos, a verificação das afirmações sobre o comportamento dos programas não depende do julgamento de quem elaborou o material: um conferidor automático compila esse código e, quando a afirmação depende da execução, o executa, no ambiente especificado, e confere o que o texto afirma, inclusive o estado representado em cada cena; nos outros 156 passos, de escolher entre frases, o código exibido foi conferido apenas pela leitura; dez perfis de estudante simulado, definidos por regras fixas, percorrem todos os tópicos para conferir o comportamento especificado. O trabalho não avalia o sistema com estudantes: a correspondência entre a hipótese diagnóstica e a concepção que o estudante de fato sustenta e a adequação pedagógica do conteúdo dependem de validação com pessoas, cujo protocolo é apresentado como trabalho futuro. Conclui-se que é possível construir um sistema desse tipo com conteúdo e comportamento verificáveis e que a verificação automatizada e a leitura do conteúdo identificam defeitos de natureza distinta e são complementares.

**Palavras-chave:** ponteiros em C; concepções errôneas; diagnóstico;
ensino de programação; verificação por compilador.

## Abstract

Pointers are among the most difficult topics for novices learning C programming, and part of the difficulty stems not from a lack of knowledge but from misconceptions: ideas that are stable and coherent to those who hold them and that resist the correct explanation. A wrong answer alone does not distinguish a student who lacks the knowledge from one who holds a misconception, and the two cases call for different interventions. This work presents Structura, a system for teaching pointers in C that formulates, for each premise of the content, a diagnostic hypothesis from three signals provided by the student on a single screen (the answer, the reason behind it and the declared confidence) and leads each case along its own path: for the student who does not know, a sequence of short steps with immediate feedback; for the student who holds a misconception, a demonstration in which the student predicts the behavior of a program and then observes what the machine does (the program's output or the compiler's message); for the student who still errs after the steps, a review with the code animated line by line. The content covers 13 topics, with 79 premises, a catalog of 61 misconceptions with declared provenance, 402 steps, 80 demonstrations and 79 animated scenes. In the demonstrations, the scenes and 246 of the 402 steps, verification of the claims about program behavior does not rely on the judgment of those who wrote the material: an automatic checker compiles that code and, when the claim depends on execution, runs it, in the specified environment, and checks what the text claims, including the state represented in each scene; in the other 156 steps, which ask the student to choose among sentences, the code shown was checked only by reading; ten simulated student profiles, defined by fixed rules, go through every topic to check the specified behavior. The work does not evaluate the system with students: whether the diagnostic hypothesis matches the misconception a student actually holds, and whether the content is pedagogically adequate depend on validation with people, whose protocol is presented as future work. It concludes that such a system can be built with verifiable content and behavior and that automated verification and the reading of the content identify defects of different kinds and are complementary.

**Keywords:** pointers in C; misconceptions; diagnosis; programming
education; compiler-based verification.

## Declaração de uso de inteligência artificial

Esta seção atende às diretrizes institucionais da UFV, que exigem a declaração do uso de inteligência artificial generativa (IAG), com o registro da ferramenta, da versão e da finalidade (UFV, [2026], p. 7). A ferramenta utilizada foi o Claude Code, da Anthropic, com os modelos Claude Opus 5, Claude Opus 5.5 e Claude Fable 5.2, entre setembro e novembro de 2026, sob a direção do autor, a quem couberam as decisões de escopo, de projeto e de método, registradas por escrito. O histórico de versões registra essa assistência.

A ferramenta foi empregada para as seguintes finalidades: a escrita do código do sistema; a elaboração e a reescrita do conteúdo didático (questões, escadas de passos, demonstrações e cenas); a redação do texto desta monografia, com a revisão da linguagem e a adequação às normas de apresentação; a localização e a conferência das referências; a auditoria da procedência do catálogo de concepções errôneas (Seção 4); e a leitura dos passos guiados em busca de perguntas pouco claras, iniciada pelo autor e estendida pela ferramenta segundo critério escrito (Seção 5.7), e das questões que o compilador não confere (Seção 5.2).

Duas medidas restringem o que a ferramenta pôde afirmar sem conferência. Primeiro, toda afirmação sobre o comportamento de um programa em C feita nas demonstrações, nas cenas e nos passos cuja resposta é código foi conferida por compilador, pelos conferidores descritos na Seção 5, sem depender da ferramenta nem de quem redigiu o conteúdo, e conteúdo que eles não aprovem faz a suíte de testes falhar; o código exibido nos passos de escolher entre frases ficou fora dessa conferência e foi conferido pela leitura do autor. Segundo, nenhuma obra foi citada de memória: cada obra relacionada na lista de referências foi aberta e consultada, com assistência da ferramenta, e o que cada uma sustenta está registrado à parte, com a página; as de acesso restrito foram obtidas pelo autor. Os estudos citados por intermédio de Sorva (2012) não foram consultados: estão identificados no texto como citação indireta (*apud*) e não constam da lista de referências (Seção 4.7).

O autor utilizou o sistema, leu as versões desta monografia e determinou as correções; leu e validou o texto final e o conteúdo didático das 13 escadas (passos, exemplos resolvidos, demonstrações e cenas). O sistema, porém, não foi avaliado com estudantes (Seções 5.8 e 7.1). Não houve coleta de dados de participantes, e nenhum foi inserido na ferramenta. A ferramenta atuou como recurso de apoio, e não lhe é atribuída qualquer forma de autoria: o autor assume a responsabilidade integral pela originalidade, pela acurácia e pela integridade deste trabalho, como exigem as mesmas diretrizes (UFV, [2026], p. 12).
