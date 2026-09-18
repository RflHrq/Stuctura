# Fundamentação teórica

As cinco ideias que sustentam o Structura, e o que cada uma obriga o
software a fazer. Quem lê este documento deve terminar sabendo **por que** o
sistema é assim, sem abrir código.

## O problema: saber errado não é não saber

Uma concepção errônea é uma ideia **estável e coerente para quem a tem**,
que produz respostas erradas de forma sistemática. Não é esquecimento nem
distração. Quem acredita que "array e ponteiro são a mesma coisa" acerta
várias questões com essa ideia — `a[i]` e `p[i]` funcionam igual, os dois
podem ser passados para uma função — e só tropeça em `sizeof`. A ideia se
sustenta porque quase sempre funciona.

A consequência prática é dura: **informação nova não corrige**. O aluno lê a
explicação certa e a encaixa dentro da ideia antiga, saindo com as duas na
cabeça. É por isso que este trabalho não é sobre "explicar melhor".

No domínio de ponteiros em C, o catálogo tem 34 concepções errôneas, cada
uma com procedência declarada — e a própria distribuição é um achado a
reportar:

| Procedência | O que significa | Quantas |
| --- | --- | --- |
| D | documentada: achado empírico com fonte e página | 1 |
| T | transposta de outra linguagem, com analogia declarada | 7 |
| L | registrada como erro comum em obra técnica de C | 23 |
| N | o erro está em norma (CERT C, CWE); a crença, não | 3 |
| E | elaborada a partir do modelo de máquina; hipótese a testar | 0 |

Só **uma** das 34 vem de medição empírica direta em C. Isso não é defeito do
catálogo — é o estado da literatura, e é um dos motivos de o estudo existir:
cada crença que aparecer na fala de um participante ganha evidência que hoje
ela não tem.

## Por que perguntar a confiança

Uma resposta errada, sozinha, não diz de qual dos dois casos se trata. A
confiança declarada é o sinal mais barato que separa os dois: custa um
clique e vem da própria pessoa.

| Respondeu | Confiança | O sistema conclui | O que faz |
| --- | --- | --- | --- |
| certo | qualquer | premissa sustentada | segue |
| errado | "chutei" | lacuna: ela sabe que não sabe | constrói a premissa |
| errado | "acho que sei" ou "tenho certeza", em distrator mapeado | **hipótese** de crença ativa | conduz a refutação daquela crença |
| errado | qualquer, em distrator não mapeado | erro fora do catálogo | registra como achado |

Três pontos que o texto do TCC precisa sustentar com essas palavras:

- A confiança **não mede** o estado mental da pessoa. Ela roteia a
  intervenção. Se a pessoa marcou "tenho certeza" por hábito, a hipótese
  nasce errada — e é exatamente isso que V2 vai flagrar.
- A escala tem **três níveis** porque precisa caber num clique dentro do
  ritmo da atividade. Escalas de 5 ou 7 pontos medem melhor e atrapalham
  mais.
- A confiança também produz um dado secundário de graça: **calibração**.
  Quem acerta dizendo "chutei" e erra dizendo "tenho certeza" está mal
  calibrado, e o sistema já exporta isso por participante.

## O grafo de premissas é um esboço de prova

Não é mapa conceitual. Num mapa conceitual as arestas ligam ideias
relacionadas; aqui elas vão de **fatos observáveis** até uma **conclusão**,
e cada nó é uma proposição que o aluno pode afirmar ou negar.

- **Nó-base**: fato que se verifica olhando. *"`int a[5]` cria 5 caixas de
  inteiro grudadas uma na outra."*
- **Nó de inferência**: decorre de outros nós, que são o seu **suporte**.
  *"Então `a` e `p` são coisas diferentes."*
- **Conclusão do tópico**: o nó que fecha a cadeia. É o "teorema".

Duas consequências fazem esse desenho valer a pena:

**1. Uma crença nega exatamente um nó.** É isso que transforma "o aluno tem
uma ideia errada" em endereço: `array_is_pointer` nega `kc_07:I1`. Se uma
crença não ancora em nó nenhum, falta um nó no grafo; se ancora em dois, são
duas crenças. O próprio catálogo diz isso, e o validador recusa o domínio
quando acontece.

**2. O caminho da refutação é derivado, não escrito.** O sistema faz uma
busca em pós-ordem do nó negado até os fatos observáveis e apresenta o que
falta, um nó por tela. **Nenhuma das perguntas do percurso existe escrita no
domínio** — elas são montadas de dois moldes e do enunciado dos nós.
Acrescentar uma crença nova custa apontar o nó que ela nega; acrescentar um
tópico custa escrever um grafo.

O suporte atravessa tópicos. Para refutar uma crença sobre `free`, o
percurso passa por passagem de parâmetro: `free(p)` recebe uma **cópia** de
`p`, e por isso não tem como mudá-la. O KC 09 tem 10 nós próprios e puxa
outros 9 de KCs anteriores quando é percorrido — o caminho segue a cadeia de
causa, não a ordem das aulas.

## Refutar é conduzir, não explicar

A diferença entre as duas coisas cabe numa frase: na explicação, quem afirma
é o sistema; na refutação, quem afirma é o aluno — e no fim ele descobre que
afirmou o contrário do que pensava.

O percurso tem três momentos, e cada um tem uma razão:

1. **Validação**, ao entrar. O sistema diz qual é a ideia do aluno e a trata
   como razoável: *"sua resposta não foi aleatória; ela segue de uma ideia
   coerente"*. Não é cortesia. Quem se sente corrigido defende a posição;
   quem se sente ouvido examina a própria premissa.
2. **Contradição**, no nó que a crença nega, e só nele. *"Antes você partiu
   de X. Mas as premissas que você acabou de confirmar levam a outro lugar.
   Qual das duas você sustenta?"* A tensão é entre coisas que **ele** afirmou
   — não entre ele e o sistema, que ele poderia simplesmente não acreditar.
3. **Reconstrução**, no fecho. Não repete a conclusão: diz de onde ela veio.
   É a diferença entre "a resposta certa é X" e "você chegou a X, e foi por
   aqui".

**O ponto frágil, e o que fizemos com ele.** Um percurso feito de "confirme
comigo: …, certo?" aceita quem clica em "sim" sem pensar — e aí a
contradição final não tem com que trabalhar. Por isso, no nó que a crença
nega, o aluno não confirma: ele **escolhe** entre a frase do nó e a frase da
própria crença, antes de o sistema dizer qualquer coisa. É o único ponto do
percurso em que ele produz a conclusão, e é o ponto que decide se há
refutação ou só concordância.

## O que o sistema assume

Seis suposições sustentam o mecanismo. Nenhuma delas é óbvia, e o estudo
existe para pôr as três primeiras à prova.

| Suposição | Se estiver errada | Como a gente descobre |
| --- | --- | --- |
| O erro sistemático revela uma ideia estável | as hipóteses viram ruído, e a refutação ataca o que ninguém pensa | V2: a fala não traz a relação que a crença afirma |
| A confiança declarada informa alguma coisa | o roteamento erra, e lacuna vira refutação | V2 + calibração por participante |
| Contradição entre as próprias afirmações provoca revisão | o aluno atravessa o percurso e continua com a ideia | V3: escolhe a mesma ideia no item novo |
| O aluno concorda com as premissas honestamente | a cadeia se ergue sem nada por baixo | a sondagem no nó da crença, e o tempo por tela no log |
| O grafo é uma cadeia válida do domínio | o sistema conduz a uma conclusão mal fundamentada | revisão do orientador; o validador só confere forma, não verdade |
| Cada crença nega exatamente um nó | falta nó no grafo, ou são duas crenças | a carga do domínio recusa o caso |

A quinta linha merece atenção: **nenhum software verifica se o conteúdo está
certo**. O validador confere que todo nó tem suporte resolvível, que nenhuma
crença fica sem âncora, que a escada de níveis não pula degrau. Que
`int a[5]` de fato cria cinco caixas, quem garante é você e o seu orientador.
