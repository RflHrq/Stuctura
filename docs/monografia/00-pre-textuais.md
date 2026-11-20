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

Monografia apresentada ao Curso de Sistemas de Informação da Universidade
Federal de Viçosa, *Campus* Rio Paranaíba, como requisito para obtenção do
título de bacharel em Sistemas de Informação.

Orientador: Pedro Henrique Aparecido Damaso de Melo

RIO PARANAÍBA
2026

## Resumo

Ponteiros constituem um dos conteúdos de mais difícil aprendizagem no ensino de programação em C, e parte dessa dificuldade não decorre da falta de conhecimento, mas de concepções errôneas: ideias estáveis e coerentes para quem as sustenta, que resistem à explicação correta. Uma resposta incorreta, isoladamente, não distingue o estudante que desconhece o conteúdo daquele que sustenta uma concepção errônea, e os dois casos demandam intervenções diferentes. Este trabalho apresenta o Structura, um sistema de ensino de ponteiros em C que formula, para cada premissa do conteúdo, uma hipótese diagnóstica a partir de três sinais fornecidos pelo estudante em uma mesma tela (a resposta, a razão que a sustenta e a certeza declarada) e conduz cada caso por um percurso próprio: ao estudante que não sabe, uma sequência de passos curtos com retorno imediato; ao que sustenta uma concepção errônea, uma demonstração na qual ele prevê o comportamento de um programa e observa o resultado da execução; ao que erra após os passos, uma revisão com o código animado linha a linha. O conteúdo abrange 13 tópicos, com 79 premissas, um catálogo de 61 concepções errôneas com procedência declarada, 402 passos, 80 demonstrações e 79 cenas animadas. A verificação das afirmações sobre o comportamento dos programas não depende do julgamento de quem elaborou o material: um conferidor automático compila e executa cada trecho de código, no ambiente especificado, e confere o que o texto afirma, inclusive o estado representado em cada cena, e dez perfis de estudante simulado percorrem todos os tópicos para conferir o comportamento especificado. O trabalho não avalia o sistema com estudantes: a correspondência entre a hipótese diagnóstica e a concepção que o estudante de fato sustenta e a adequação pedagógica do conteúdo, ainda não revisado por especialistas, dependem de validação com pessoas, documentada como trabalho futuro. Conclui que é possível construir um sistema desse tipo com conteúdo e comportamento verificáveis e que a verificação automatizada e a leitura do conteúdo identificam defeitos de natureza distinta e são complementares.

**Palavras-chave:** ponteiros em C; concepções errôneas; diagnóstico;
ensino de programação; verificação por compilador.

## Abstract

Pointers are among the most difficult topics for novices learning C programming, and part of the difficulty stems not from a lack of knowledge but from misconceptions: ideas that are stable and coherent to those who hold them and that resist the correct explanation. A wrong answer alone does not distinguish a student who lacks the knowledge from one who holds a misconception, and the two cases call for different interventions. This work presents Structura, a system for teaching pointers in C that formulates, for each premise of the content, a diagnostic hypothesis from three signals provided by the student on a single screen (the answer, the reason behind it and the declared confidence) and leads each case along its own path: for the student who does not know, a sequence of short steps with immediate feedback; for the student who holds a misconception, a demonstration in which the student predicts the behavior of a program and then observes the result of its execution; for the student who still errs after the steps, a review with the code animated line by line. The content covers 13 topics, with 79 premises, a catalog of 61 misconceptions with declared provenance, 402 steps, 80 demonstrations and 79 animated scenes. Verification of the claims about program behavior does not rely on the judgment of those who wrote the material: an automatic checker compiles and runs every code snippet, in the specified environment, and checks what the text claims, including the state represented in each scene, and ten simulated student profiles go through every topic to check the specified behavior. The work does not evaluate the system with students: whether the diagnostic hypothesis matches the misconception a student actually holds, and whether the content, not yet reviewed by specialists, is pedagogically adequate, depend on validation with people, documented as future work. It concludes that such a system can be built with verifiable content and behavior and that automated verification and the reading of the content identify defects of different kinds and are complementary.

**Keywords:** pointers in C; misconceptions; diagnosis; programming
education; compiler-based verification.

## Declaração de uso de inteligência artificial

Este trabalho foi desenvolvido com assistência de um modelo de linguagem (Claude, da Anthropic), sob a direção do autor, a quem couberam as decisões de escopo, de projeto e de método, registradas por escrito ao longo do projeto. Esta declaração discrimina o que foi produzido com essa assistência, o que foi conferido e por qual meio, e o que ainda não foi revisado.

Foram produzidos com assistência do modelo: o código do sistema; o conteúdo didático (as escadas de passos, as demonstrações e as cenas), na versão inicial e nas reescritas posteriores; o texto desta monografia; a localização e a conferência das referências; a auditoria da procedência do catálogo de concepções errôneas (Seção 4); e a leitura dos passos guiados em busca de perguntas pouco claras (Seção 5.7), iniciada pelo autor e estendida aos demais passos pelo modelo, segundo critério registrado por escrito.

Duas medidas restringem o que o modelo pôde afirmar sem conferência. Primeiro, toda afirmação sobre o comportamento de um programa em C foi conferida por compilador, no ambiente especificado, por meio dos conferidores automáticos descritos na Seção 5, e o sistema não aceita conteúdo que não seja aprovado por eles; essa conferência não depende do modelo nem do julgamento de quem redigiu o conteúdo. Segundo, nenhuma obra foi citada de memória: cada obra relacionada na lista de referências foi aberta e consultada diretamente, com assistência do modelo, e o que cada uma sustenta está registrado à parte, com a indicação da página; as obras de acesso restrito foram obtidas pelo autor por meio do acesso institucional da universidade. Os estudos citados por intermédio de Sorva (2012) não foram consultados: estão identificados no texto como citação indireta (*apud*) e não constam da lista de referências (Seção 4.7).

O autor utilizou o sistema, leu as versões desta monografia e determinou as correções decorrentes. O conteúdo didático, entretanto, ainda não foi integralmente revisado pelo autor nem por especialista no domínio, e o sistema não foi avaliado com estudantes (Seções 5.8 e 7.1). A conferência por compilador atesta o comportamento dos programas, e não a adequação pedagógica do conteúdo.
