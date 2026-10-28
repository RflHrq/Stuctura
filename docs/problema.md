# O problema, e o que conta como resolvido

Artefato da fase 1 (Grill). Vocabulário em [context.md](context.md);
decisões e estado em [processo.md](processo.md).

## O problema em uma frase

Uma pessoa pode atravessar um material inteiro sobre ponteiros em C, acertar
exercícios, e sair com a mesma ideia errada com que entrou — porque
informação nova não corrige concepção errônea, e porque ninguém consegue
ver, de fora, em qual premissa exatamente ela está errada.

## As duas jornadas

O sistema precisa servir às duas, e elas pedem coisas diferentes. Hoje ele
serve bem à segunda e mal à primeira.

| | Entra sem saber nada | Entra com uma premissa torta |
| --- | --- | --- |
| Estado inicial | nenhuma premissa de pé | várias de pé, uma errada |
| O que o sistema faz | **constrói** a cadeia | **acha o desvio** e corrige a rota |
| Marcador de sucesso | as premissas acendem, e sobrevivem à troca de superfície | a razão escolhida muda, e não volta |
| Risco próprio | virar leitura passiva | refutar o que a pessoa não pensa |

## O critério de sucesso observável

Definido **antes** da coleta, para não ser escolhido depois de ver os dados.

> **Mudança conceitual observada**, num nó: a **razão** escolhida muda da
> razão-crença para a razão-correta **sem queda de confiança**; isso
> **sobrevive à troca de superfície** (acerta resposta *e* razão num item que
> ela não viu); e **não volta** no reteste do fim da sessão, com outra
> unidade no meio.

Três condições, não uma. Um acerto isolado não satisfaz nenhuma.

> **Construção observada**, num nó que começou desconhecido: a pessoa passa a
> escolher resposta *e* razão corretas, com confiança, em duas superfícies
> diferentes — sem ter sido exposta à resposta antes de responder.

**O que este critério NÃO é.** Não é aprendizagem. Dentro de uma sessão o
que se observa é desempenho, e desempenho é índice ruim de aprendizagem
(Soderstrom & Bjork, 2015). Aprendizagem exigiria reteste depois de dias,
que este estudo não cobre. O texto do TCC precisa dizer isso com todas as
letras.

## O instrumento: três camadas

Cada atividade pergunta, em sequência:

1. **O que acontece** — a resposta.
2. **Por quê** — a razão. As opções saem do grafo: a razão certa é o
   enunciado da premissa; as erradas são as crenças que a negam.
3. **Quanta confiança** — uma vez, no fim.

O cruzamento classifica o episódio:

| Resposta | Razão | Confiança | Estado | O que o sistema faz |
| --- | --- | --- | --- | --- |
| certa | certa | alta | **confirmada** | segue; conta para a força |
| certa | certa | baixa | **frágil** | mais uma superfície antes de confirmar |
| certa | **errada** | qualquer | **falso positivo** | não confirma; investiga |
| errada | **certa** | qualquer | **falso negativo** (vacilo) | não refuta; segue |
| errada | errada | alta | **crença ativa** | valida, refuta, treina |
| errada | errada | baixa | **lacuna** | constrói |
| "não sei" em qualquer camada | — | — | **lacuna** | constrói |

O falso positivo é o que mais protege o dado: hoje, quem acerta por sorte
tem a premissa marcada como verde.

## O motor adaptativo: força da premissa

Sem modelo probabilístico e sem parâmetro estimado — o Duolingo estima
quando você vai esquecer, o que exige medir retenção ao longo de dias; aqui
a pergunta é outra: **quão sustentada está esta premissa agora?**

| Evidência | Efeito |
| --- | --- |
| resposta certa pela razão certa, com confiança | fortalece |
| acerto pela razão errada | não conta |
| erro pela razão certa | não enfraquece |
| sobreviveu à troca de superfície | fortalece |
| precisou de reexplicação, ou tropeçou no treino | enfraquece |
| veio de refutação de crença | frágil até o reteste |

A unidade termina quando a premissa **mais fraca** do grafo está de pé — não
quando as telas acabaram. É o "trabalhar onde está fraco" sem inventar
número.

## O que entra no primeiro teste

Decidido em 28/10/2026, no fechamento da fase 1.

| # | Funcionalidade | Por que importa | Custo | Quando |
| --- | --- | --- | --- | --- |
| 1 | **"Não sei" como opção de verdade**, em toda camada | obrigar a escolher fabrica chute; com esta opção a lacuna vira dado observado em vez de inferido | baixo | **1º ciclo** |
| 2 | **A frase do começo e a do fim**: antes da unidade, a pessoa escreve uma frase sobre o conceito; no fim, escreve de novo e vê as duas lado a lado | é o teach-back de Feynman com antes-e-depois; dá o dado mais forte do TCC e mostra a mudança à própria pessoa | baixo | **1º ciclo** |
| 4 | **Painel do pesquisador** (tela separada, só leitura): estado dos nós, classificação de cada resposta e eventos ao vivo | permite observar a sessão sem interromper quem está pensando em voz alta | baixo | **1º ciclo** |
| 3 | **Montar a cadeia**: as premissas embaralhadas, a pessoa ordena até a conclusão | é o formato que testa a tese diretamente, e é a melhor atividade para quem entra sem saber nada | médio | 2º ciclo |

**Por que a 3 fica para depois, e o que isso custa.** Ela é a única das
quatro que atende diretamente a jornada *"entra sem saber nada"* — sem ela,
o primeiro teste mede bem a correção de rota e mede pouco a construção de
cadeia. O primeiro ciclo aceita essa limitação de propósito: as três
baratas mexem na **qualidade do dado**, e dado ruim não melhora com mais
formato de exercício em cima.

O instrumento tem **três camadas** (resposta, razão, confiança uma vez no
fim), e o teach-back fica **no fim da unidade**, emparelhado com a frase do
começo.

## O que fica de fora, e por quê

- **XP, vidas, ofensiva, ranking.** Gamificação é variável concorrente: se a
  pessoa melhora, não se sabe se foi o mecanismo ou a recompensa. O progresso
  aqui é o grafo acendendo.
- **Repetição espaçada entre dias.** Exige medir retenção, que o desenho
  exclui. Fica como trabalho futuro — e é o que separa este sistema de um
  produto de uso contínuo.
- **Modelo probabilístico (BKT e afins).** Precisa de dados históricos para
  estimar parâmetros por item; com 10 a 15 participantes vira número
  inventado, e deixa de ser inspecionável na banca.
- **Dica progressiva.** Seria uma segunda intervenção, não controlada,
  competindo com a refutação pelo crédito do resultado.
- **Correção automática da resposta aberta.** O sistema guarda; quem
  classifica é o pesquisador, com codebook.

## Métrica da sessão (o que vai no TCC)

Por **episódio de premissa**, não por participante:

1. quantos episódios de cada um dos cinco estados;
2. dos episódios de crença ativa, quantos satisfazem o critério de mudança
   conceitual observada;
3. dos episódios de lacuna, quantos satisfazem o de construção observada;
4. quantas premissas terminam a sessão de pé, e por qual caminho;
5. concordância entre a classificação do sistema e o que a pessoa fala em
   voz alta.

## Perguntas em aberto

Nenhuma delas bloqueia a fase 2; todas precisam de resposta antes da coleta.

1. Quantos tópicos a coleta usa, e em que ordem.
2. Onde fica o reteste do fim da sessão quando só há uma unidade pronta —
   hoje o critério pede "outra unidade no meio", e só o kc_00 existe.
3. Quem classifica as frases abertas do teach-back, e com que codebook.
