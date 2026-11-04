# Roteiro do ensaio — uma pessoa, o kc_02

O primeiro ensaio com gente. Trinta minutos, uma pessoa, e ele responde
coisas que nenhuma medição automática responde.

## O que este ensaio responde

| | |
| --- | --- |
| **CS-11** | *"uma pessoa real atravessa a unidade sozinha, sem perguntar o que a tela quer"* — o critério mais antigo sem evidência nenhuma |
| **O tempo de verdade** | tudo o que eu medi está em **cliques**: 42 passos para quem acerta tudo, 81 para quem erra e aprende, até 118 para quem não muda de ideia. Quantos minutos isso é, só uma pessoa diz |
| **A linguagem do kc_02** | 6 nós e 36 itens escritos sob um contrato que ninguém leu em voz alta ainda |
| **O "não sei"** | é usado, ou evitado por parecer desistência? |
| **O falso positivo** | a pessoa **percebe** quando o sistema diz "a resposta está certa, a explicação leva a outro lugar"? É a decisão 13 |
| **O mapa** | diz alguma coisa para quem não construiu o sistema? |
| **A ordem das alternativas** | desde 04/11 ela é embaralhada por sessão. A pessoa repara? Reclama? Procura padrão? |

## O que este ensaio **não** é

**Não é coleta.** Ninguém assina termo, nada vira dado do TCC, e o código
do participante é `E01`, não `P01` — o log do ensaio é um arquivo separado
(`ensaios/kc_02.jsonl`), fora do versionamento e fora do log do piloto.

Onde exatamente fica a linha entre "ensaio de interface" e "pesquisa com
seres humanos" **não sou eu que decido**: isso é conversa com o seu
orientador e com o comitê de ética, e vale ter essa conversa antes.

---

## Antes: quinze minutos

### 1. Prepare o ambiente

```bash
bash scripts/ensaio.sh E01
```

Ele confere o que tem de estar certo **antes** — o formato do código, o
código ainda não usado, o tópico que carrega, as portas livres, a pasta do
ensaio — e imprime os dois comandos com o ambiente montado. Descobrir
qualquer uma dessas coisas com a pessoa sentada ao lado é o pior momento
possível.

Suba os dois, cada um no seu terminal, e **abra a página de quem responde
antes de chamar a pessoa**:

```
http://127.0.0.1:8010/?codigo=E01
```

O código vai na URL, não numa tela a mais. Se a página abrir sem
`?codigo=`, a sessão sai anônima e não dá para ligá-la a ninguém depois.

Deixe o painel (`http://127.0.0.1:8011`) **na sua tela, não na dela**.

### 2. Quem convidar

Alguém que **já viu C e ainda não domina ponteiros**. Segundo período
serve melhor do que oitavo: quem já sabe não tem crença para o sistema
achar, e o ensaio vira passeio.

Não convide quem já ouviu você falar do projeto. A pessoa que quer te
ajudar a dar certo é a pior fonte de dado que existe.

### 3. O que dizer, antes de começar

Leia, não improvise:

> Obrigado por topar. Isto é um sistema que eu estou construindo para o
> meu TCC, sobre ponteiros em C. **Não é prova, e não estou avaliando
> você** — estou avaliando a tela. Se alguma coisa não fizer sentido, o
> problema é meu.
>
> Quero te pedir uma coisa que é meio estranha: **pensa em voz alta**.
> Fala o que você está lendo, o que está em dúvida, por que escolheu uma
> alternativa. Se ficar em silêncio eu vou te lembrar.
>
> Vai levar uns trinta minutos. Pode parar quando quiser, sem explicar por
> quê.

---

## Durante: a regra que é difícil

### Não socorra

É a regra inteira, e é a mais difícil de cumprir. Quando a pessoa travar,
a vontade de explicar é enorme — e explicar destrói o dado, porque o que
você quer saber é exatamente **se ela consegue sem você**.

Quando ela perguntar alguma coisa, devolva:

- *"O que você faria se eu não estivesse aqui?"*
- *"O que você acha que essa tela está pedindo?"*
- *"Pode escolher o que te parecer mais certo."*

Se ficar em silêncio por uns vinte segundos: *"o que você está pensando
agora?"* — e só isso. Nada de "repara ali em cima".

**Só interrompa de verdade** se a tela travar ou der erro. Aí o ensaio
acabou e o que você tem é um defeito, que também é resultado.

### O que anotar no papel

O log já guarda tudo o que é automático: cada tela, cada escolha, o tempo
de cada uma em milissegundos. **Não anote nada disso.** Anote só o que o
log não captura:

- **onde ela hesitou** e o que disse em voz alta ali;
- **que pergunta ela te fez** (a pergunta é o achado: cada uma é uma tela
  que não se explicou);
- **onde ela releu** a tela, ou voltou com o olho;
- **a cara** quando apareceu a refutação — convencida, irritada, perdida;
- **se o teclado foi usado** ou se ela foi toda no mouse;
- **o que ela disse do mapa**, se disse alguma coisa.

Duas coisas que eu quero especialmente que você observe, porque são
suspeitas minhas e não medições:

1. **O mapa do kc_02 tem seis nós** e eles não cabem tão bem quanto os
   cinco do kc_00: `I3` aparece na mesma linha de `I1` e `I2`, e duas
   arestas se cruzam. Repare se ela olha para o mapa ou ignora.
2. **A tela de confiança** agora aparece menos no treino (mudança do ciclo
   3). Repare se a pergunta "quanta confiança você tem nessa dupla?" é
   entendida, ou se ela responde no automático.
3. **A ordem das alternativas é embaralhada por sessão** desde 04/11.
   Antes disso a resposta certa estava na primeira posição em 553 dos 562
   itens — 98,4% —, e este ensaio seria o primeiro a medir uma pessoa
   contra esse viés. Agora não é mais.

   O que muda para quem observa: *"ela escolheu a primeira"* deixou de ser
   indício de chute por posição, porque a primeira é diferente para cada
   participante. E se ela **disser** alguma coisa como "a certa parece ser
   sempre a tal", isso é achado — vale anotar a frase inteira, porque
   significa que sobrou alguma outra pista de superfície (comprimento,
   vocabulário) que o embaralhamento não toca.

   Você não precisa anotar qual posição era a certa: o log grava a ordem
   mostrada em cada item, no campo `ordem` de `atividade_apresentada`.

---

## Depois: dez minutos, enquanto está fresco

### 1. Pergunte a ela, nesta ordem

Da mais aberta para a mais fechada, para não plantar a resposta:

1. *"Como foi?"* — e cale a boca. O silêncio é seu amigo aqui.
2. *"Teve algum momento em que você não entendeu o que a tela queria?"*
3. *"Teve alguma hora em que você mudou de ideia sobre alguma coisa?"*
4. *"Você lembra do desenho com as caixinhas? O que ele te dizia?"*
5. *"Se você fosse explicar ponteiro para um colega agora, mudaria alguma
   coisa em relação ao que você escreveu no começo?"*
6. *"Alguma tela te irritou?"*

A 5 é a mais importante: é a CS-12 em forma de conversa.

### 2. Copie o log, antes de fechar os servidores

```bash
bash scripts/copia.sh <pasta-na-outra-midia> --log ensaios/kc_02.jsonl
```

É a primeira vez que o procedimento vale para dado que importa.

### 3. Só então feche os servidores

---

## Folha de observação

Para imprimir, ou copiar para um caderno.

```
ENSAIO ____  codigo E__  data ___/___/____  inicio __:__  fim __:__

PESSOA
  periodo ____  ja viu ponteiros antes? ( ) nao ( ) pouco ( ) sim
  ja ouviu falar deste projeto? ( ) nao ( ) sim

PERGUNTAS QUE ELA FEZ  (cada uma e uma tela que nao se explicou)
  1. ____________________________________________  em que tela: _______
  2. ____________________________________________  em que tela: _______
  3. ____________________________________________  em que tela: _______

ONDE TRAVOU
  tela ____________  quanto tempo ____  o que disse: ________________
  tela ____________  quanto tempo ____  o que disse: ________________

MOMENTOS
  ( ) usou "nao sei"            quantas vezes ____  em que camada ______
  ( ) percebeu o falso positivo        o que disse: ________________
  ( ) reagiu a refutacao               como: ________________________
  ( ) olhou o mapa                     o que disse: ________________
  ( ) falou da ordem das alternativas  a frase: ____________________
  ( ) usou o teclado                   ( ) so mouse

A UNIDADE
  terminou? ( ) sim ( ) nao, parou em ______________________________
  pediu para parar? ( ) nao ( ) sim, por que: ______________________
  premissas no fim: confirmadas ___  nao medidas ___  em aberto ___

DEPOIS, NAS PALAVRAS DELA
  como foi: ________________________________________________________
  o que nao entendeu: ______________________________________________
  mudou de ideia sobre: ____________________________________________
  o mapa dizia: ____________________________________________________
  mudaria a frase do comeco? _______________________________________

MINHA IMPRESSAO (escreva antes de olhar o log)
  __________________________________________________________________
  __________________________________________________________________

DEPOIS DE OLHAR O LOG
  duracao real ____ min    telas ____    tempo na tela mais longa ____
  bateu com a impressao? ___________________________________________
```

---

## O que fazer com o resultado

Se **uma** pessoa atravessar sozinha e o tempo couber, isso não prova que
o instrumento está pronto — prova que vale fazer mais dois. A CS-11 pede
três.

Se ela travar, a tela que travou vira tarefa, e o ensaio seguinte é depois
do conserto. Um ensaio que acha um problema **valeu mais** que um ensaio
que correu liso: o liso você só descobre que era sorte no participante 7.
