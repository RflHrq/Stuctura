# Elementos pré-textuais

Rascunho, até o modelo da UFV chegar: a ordem e a forma (capa, folha de
rosto, ficha catalográfica, folha de aprovação) são as do modelo. O que
está entre colchetes é para o autor preencher.

## Capa e folha de rosto

UNIVERSIDADE FEDERAL DE VIÇOSA
[preencher: campus, centro e departamento]
[preencher: curso]

RAFAEL H. S. SIMÃO [preencher: nome completo]

**STRUCTURA: DIAGNÓSTICO E CONFRONTO DE CONCEPÇÕES ERRÔNEAS SOBRE
PONTEIROS EM C, COM CONTEÚDO VERIFICADO POR COMPILADOR**
[preencher: título — este é uma proposta]

Trabalho de Conclusão de Curso apresentado ao [preencher: curso] da
Universidade Federal de Viçosa, como requisito parcial para a obtenção do
título de [preencher: grau].

Orientador: [preencher: nome do orientador]

[preencher: cidade]
2026

## Resumo

Ponteiros estão entre os pontos mais difíceis do ensino de programação
em C, e parte da dificuldade não é falta de conhecimento, mas concepções
errôneas: ideias estáveis e coerentes para quem as tem, que resistem à
explicação correta. Uma resposta errada, sozinha, não distingue quem não
sabe de quem sabe errado, e os dois casos pedem intervenções diferentes.
Este trabalho apresenta o Structura, um sistema de ensino de ponteiros
em C que diagnostica cada premissa do conteúdo cruzando três sinais que o
estudante fornece numa mesma tela — a resposta, a razão que a sustenta e
a certeza declarada — e conduz cada caso por um percurso próprio: a quem
não sabe, uma escada de passos curtos com retorno imediato; a quem
sustenta uma concepção errônea, uma demonstração em que ele prevê o que um
programa faz e vê o que a máquina fez; a quem erra depois da escada, uma
revisão com o código animado linha a linha. O conteúdo cobre 13 tópicos,
com 79 premissas, um catálogo de 61 concepções errôneas com procedência
declarada, 402 passos, 80 demonstrações e 79 cenas animadas. A
verificação foi feita sem depender da opinião de quem escreveu o
material: um conferidor compila e executa cada trecho de código e confere
o que o texto afirma, inclusive o estado que cada cena mostra, e dez
perfis de estudante simulado atravessam todos os tópicos para conferir o
comportamento descrito. O trabalho não avalia o sistema com estudantes; o
estudo com participantes está desenhado e documentado como trabalho
futuro. Conclui-se que é possível construir um sistema desse tipo com
conteúdo e comportamento conferíveis, e que a verificação mecânica e a
leitura humana encontram defeitos de natureza diferente e se completam.

**Palavras-chave:** ponteiros em C; concepções errôneas; diagnóstico;
ensino de programação; verificação por compilador.

## Abstract

Pointers are among the hardest topics in teaching C programming, and part
of the difficulty is not a lack of knowledge but misconceptions: ideas
that are stable and coherent to those who hold them, and that resist the
correct explanation. A wrong answer alone does not tell apart a student
who does not know from one who knows wrongly, and the two cases call for
different interventions. This work presents Structura, a system for
teaching pointers in C that diagnoses each premise of the content by
crossing three signals the student provides on a single screen — the
answer, the reason behind it and the declared confidence — and leads each
case along its own path: to the student who does not know, a ladder of
short steps with immediate feedback; to the student who holds a
misconception, a demonstration in which they predict what a program does
and then see what the machine did; to the student who still errs after
the ladder, a review with the code animated line by line. The content
covers 13 topics, with 79 premises, a catalog of 61 misconceptions with
declared provenance, 402 steps, 80 demonstrations and 79 animated scenes.
Verification did not rely on the opinion of whoever wrote the material: a
checker compiles and runs every code snippet and checks what the text
claims, including the state each scene shows, and ten simulated student
profiles go through every topic to check the described behavior. The
work does not evaluate the system with students; the study with
participants is designed and documented as future work. It concludes
that such a system can be built with checkable content and behavior, and
that mechanical verification and human reading find defects of different
kinds and complement each other.

**Keywords:** pointers in C; misconceptions; diagnosis; programming
education; compiler-based verification.

## Declaração de uso de inteligência artificial

[preencher: ajustar à norma da UFV, se houver uma, e ao que o autor
quiser declarar]

Este trabalho foi desenvolvido com assistência de um modelo de linguagem
(Claude, da Anthropic), sob a direção e a revisão do autor. O modelo foi
usado para escrever parte do código do sistema, para rascunhar o
conteúdo didático — as escadas de passos, as demonstrações e as cenas — e
o texto desta monografia, e para localizar e conferir as referências.

Três cuidados limitam o que o modelo pôde afirmar sem conferência. Todo
conteúdo que diz o que um programa em C faz foi conferido por compilador,
pelos conferidores automáticos descritos no Capítulo 5, e o sistema não
aceita conteúdo que não passe por eles. Toda referência citada foi aberta
na obra, com a página do que ela sustenta registrada à parte; a única que
não pôde ser aberta segue marcada no texto. E as decisões de recorte, de
desenho e de método são do autor, registradas por escrito ao longo do
projeto. A revisão do conteúdo didático pelo autor [preencher: feita em
(data) / em andamento].
