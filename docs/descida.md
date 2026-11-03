# A descida interrogativa

> Protótipo de **uma** crença, atrás de `STRUCTURA_DESCIDA=1`. O fluxo de
> hoje continua intacto com a chave desligada, que é o padrão.

## O que muda

A refutação de hoje **afirma**. Ela percorre as premissas que sustentam o
nó, uma por tela, e no último passo põe a crença e a premissa lado a
lado. Quem conduz o argumento é o sistema; quem assiste é a pessoa.

A descida **pergunta**. Ela toma a crença como verdadeira — de propósito —
e vai perguntando o que decorre dela, degrau por degrau, até a
consequência que a própria pessoa recusa. Quem conduz o argumento continua
sendo o sistema; quem o **assina** passa a ser a pessoa.

É a diferença entre ouvir "você está errado, e olha por quê" e descobrir,
em quatro perguntas que você mesmo respondeu, que as suas respostas não
cabem juntas.

## A inversão, que é única no sistema

Em toda atividade deste projeto a alternativa certa é a **verdadeira**.
Num degrau da descida, a alternativa que faz a cadeia **andar** é a falsa:
é a previsão da crença. Estamos pedindo consistência com o erro.

```yaml
- pergunta: "...então o nome `a` guarda um endereço dentro dele?"
  decorre: "Guarda: a aponta para a primeira casa"   # o que a CRENÇA prevê
  verdade: "Não guarda: a é o conjunto das casas"    # o que de fato é
  porque:  "Então `a` não é uma caixa com endereço dentro, e `p` é..."
```

`decorre` **não é a resposta certa**. Quem for escrever outra cadeia
precisa saber disso antes de olhar o arquivo, e por isso está escrito
duas vezes: no cabeçalho do YAML e na docstring de `Passo`.

## As três saídas, e os três dados

| a pessoa… | a tela | o log | o que isso mede |
|---|---|---|---|
| recua num degrau do meio | `descida_fim` | `descida_fechou`, `profundidade: k` | a crença era rasa |
| recua no último degrau | `descida_fim`, `no_fim: true` | `descida_fechou`, `profundidade: N` | era funda, mas fechou pela boca dela |
| sustenta até o fim | `evidencia` | `descida_sustentada` | a cadeia não bastou |
| diz "não sei dizer" | `evidencia` | `descida_sem_resposta` | nem seguiu nem contradisse |

A **profundidade** é o dado que a descida existe para produzir: quantos
degraus a pessoa desce antes de largar a própria crença. Hoje o sistema
sabe *que* alguém acredita em algo; a descida mede *quanto*.

Os quatro caminhos terminam no mesmo lugar: **treino**. RF33 vale igual
aqui — ter dito "não é assim" com as próprias palavras é melhor evidência
do que ter ouvido, e continua não sendo prova de que a pessoa resolve o
próximo item.

## O último degrau: "você confirmou" só se ela confirmou

A cadeia termina colidindo com uma premissa do grafo (`colide_com`). Se a
pessoa **confirmou aquela premissa nesta sessão**, a tela diz isso, e a
contradição passa a ser entre duas coisas que ela mesma afirmou. Se não
confirmou — declarou que não sabia, ou o teto de tentativas estourou —, a
tela afirma a premissa sem atribuí-la a ela:

```
VOCÊ CONFIRMOU, NESTA SESSÃO          ESTA UNIDADE AFIRMA
int a[5] cria cinco caixas…           int a[5] cria cinco caixas…
```

Quem decide é o motor, que viu a sessão; o YAML não sabe o que aconteceu
e por isso nenhum texto dele pode dizer "você disse". Atribuir a alguém o
que ela não afirmou derruba a única coisa que faz a descida funcionar, que
é cada passo ser reconhecido como seu. Há teste dos dois lados, e um
terceiro que varre os textos da cadeia atrás de "você afirmou".

## A evidência, e por que ela pode estar pendente

Quem sustenta a crença pelos degraus todos não recebe mais um argumento:
recebe o fato. A tela mostra o programa, o comando, e então:

- `origem: gravada` — rodamos, e `saida` traz o que saiu; `onde` diz em
  que máquina e com que compilador
- `origem: citada` — a saída está publicada, e `onde` traz a citação
- `origem: pendente` — ninguém rodou. A tela mostra o programa e a
  **garantia** (o que a norma obriga), e diz que não houve execução

A cadeia do `array_is_pointer` esteve **pendente** por semanas: não havia
compilador C na máquina. Inventar a mensagem do gcc seria exatamente a
mentira que esta tela existe para não contar — uma tela que promete
evidência e mostra evidência inventada é pior que nenhuma tela. O campo
ficou vazio até **03/11/2026**, quando o gcc entrou e o programa foi
compilado de verdade:

```
exemplo.c: In function 'main':
exemplo.c:6:7: error: assignment to expression with array type
    6 |     a = p;    /* esta nao     */
      |       ^
```

`onde:` gcc (MinGW-W64 x86_64-ucrt-posix-seh) 16.2.0, Windows 11 — código
de saída 1, e a linha apontada é a sexta. A de cima, `p = a`, passa sem
uma palavra. O programa que a tela mostra é o que foi compilado: o
excerto anterior não compilava sozinho, e evidência de compilação tem de
ser do programa inteiro.

O carregador cobra os três lados: a `afirmacao` é **sempre** obrigatória,
porque é ela que a tela escreve; origem gravada ou citada **exige** `saida`
e `onde`; origem pendente **exige** `garantia`. E a tela não desenha
terminal quando a origem é pendente, mesmo que uma saída tenha sobrado no
arquivo — tem teste.

## O custo, medido

Mesma sessão do kc_07, mesma crença, mesma política; muda só o caminho
depois da validação:

| caminho | telas da sessão | telas do laço | profundidade |
|---|---|---|---|
| refutação de hoje | 61 | 7 | — |
| descida, recua no 1º degrau | 56 | 2 | 1 |
| descida, recua no último | 59 | 5 | 4 |
| descida, sustenta até o fim | 59 | 5 | 4 |

A descida **não é mais cara** que a refutação para esta crença: o
percurso de hoje tem sete passos (as sete premissas que sustentam `I3`), e
a cadeia tem quatro degraus mais a tela do fim. Quem recua cedo gasta
duas telas onde gastaria sete.

## Por que uma crença só

Pedir que alguém raciocine **a partir** da crença dela pode reforçá-la, se
a cadeia não fechar. Isso é risco pedagógico de verdade, e não se resolve
escrevendo setenta e nove cadeias no escuro. Uma cadeia escrita, rodada e
testada com gente vale mais.

A chave existe pelo mesmo motivo, e por mais um: a coleta em andamento
mede o fluxo de hoje, e trocá-lo no meio invalidaria a comparação entre
participantes. Quem decide correr o risco é quem conduz a coleta.

```bash
STRUCTURA_TOPICO=kc_07 STRUCTURA_DESCIDA=1 python -m mvp.app
```

Tópico sem cadeia escrita, ou crença sem cadeia, seguem pela refutação de
sempre, com a chave ligada ou não. As outras setenta e oito crenças não
sentem diferença nenhuma.

## O que não está feito

- **Nenhuma pessoa real passou por isto.** O que está medido é o custo em
  telas e o comportamento do motor, não o efeito em quem aprende.
- Só `array_is_pointer` (kc_07) tem cadeia.
- A descida não atende ao "ainda não entendi" da refutação. Lá a premissa
  volta pela analogia; aqui a saída é a alternativa `verdade` ou o "não
  sei dizer", e a reexplicação ainda não tem lugar.
