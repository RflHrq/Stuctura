# 6. Resultados da verificação

## 6.1 O que foi verificado

O Quadro 6.1 resume o tamanho do que a verificação do Capítulo 5 cobre,
na versão de 19/11/2026.

**Quadro 6.1 — O sistema verificado**

| | |
| --- | --- |
| Tópicos, todos na trilha | 13 |
| Premissas | 79 |
| Concepções errôneas no catálogo | 61 |
| Questões no banco | 560 |
| Passos de escada (versões) | 402 (804) |
| Demonstrações com previsão | 80 (41 saídas, 39 do compilador) |
| Cenas da revisão | 79 |
| Trechos de código das escadas | 1 762 |
| Testes automatizados | 7 547 |

## 6.2 O conteúdo contra o compilador

O conferidor não acusa nenhum problema nos 13 tópicos: os 402 passos, os
79 exemplos resolvidos e as 80 demonstrações fazem o que o texto afirma
que fazem, no gcc 16.2. Das 80 demonstrações, nove pedem opções a mais
do compilador — sete o analisador de fluxo (`-fanalyzer`), uma
`-Wpointer-arith`, e uma, a do `NULL` no kc_05, `-O2` com
`-Wnull-dereference` —, e as que dependem do ambiente trazem nota que
diz isso.

As 79 cenas também conferem: em cada ponto por onde cada uma passa, o
programa instrumentado afirma o valor de cada caixa, para onde cada
ponteiro aponta e quantas vezes a linha rodou, e nenhuma afirmação falha.
Das 79, 20 passam por dentro de funções — duas delas, a do `conta` (kc_01)
e a do `dobra` (kc_12), pela mesma função duas vezes —, 13 por arrays e
17 por blocos do `malloc`.

No banco, das 69 questões de prever a saída conferidas, todas imprimem
o valor da alternativa certa — depois da reescrita da questão do kc_12
relatada em 6.4. Nenhum trecho das 321 questões com código parte uma
string entre duas linhas, depois do conserto das oito do kc_02 (6.4).

A seleção de questões deixa 93 questões do banco fora da trilha, por
usarem construções que nenhum tópico ensinou até ali. Com elas fora, as 79 premissas abrem com uma questão de código.

## 6.3 A medida, com os estudantes simulados

O Quadro 6.2 mostra quantas telas e quantos toques cada perfil leva para
atravessar cada tópico, no ritmo completo. Um toque é cada envio — cada
vez que a pessoa responde ou segue —: marcar a resposta, confirmá-la e
escolher a razão e a certeza, na mesma tela, contam como um.

**Quadro 6.2 — Telas e toques por tópico, no ritmo completo**

| Tópico | Sabe tudo | Não sabe, aprende | Erra todo passo | Sustenta e muda | Sustenta e não muda |
| --- | --- | --- | --- | --- | --- |
| kc_00 | 12 / 16 | 22 / 38 | 32 / 80 | 32 / 31 | 37 / 56 |
| kc_01 | 12 / 16 | 22 / 36 | 32 / 76 | 32 / 31 | 37 / 56 |
| kc_02 | 14 / 19 | 26 / 45 | 38 / 95 | 38 / 37 | 44 / 67 |
| kc_03 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_04 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_05 | 14 / 19 | 26 / 44 | 38 / 93 | 38 / 37 | 44 / 67 |
| kc_06 | 14 / 19 | 26 / 44 | 38 / 93 | 38 / 37 | 44 / 67 |
| kc_07 | 16 / 22 | 30 / 51 | 44 / 108 | 44 / 43 | 51 / 78 |
| kc_08 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_09 | 18 / 25 | 34 / 57 | 50 / 121 | 50 / 49 | 58 / 89 |
| kc_10 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_11 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_12 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |

Três leituras do quadro:

- **A sessão cresce com o que a pessoa precisa, e não com o tópico.**
  Quem sabe tudo atravessa um tópico de seis premissas em 14 telas; quem
  precisa de ensino ou de correção em todas, em 26 a 38. O tamanho do
  tópico só pesa pelo número de premissas: o kc_09, com oito, é o mais
  longo em todos os perfis.
- **O teto vale.** Mesmo o perfil que erra todos os passos termina o
  tópico, com as premissas em aberto, sem laço: o pior caso é finito e
  previsível.
- **A demonstração é curta.** Quem sustenta a concepção errônea e muda de
  ideia gasta menos toques do que quem não sabe e aprende (37 contra 43
  num tópico de seis premissas): a demonstração substitui a subida da
  escada, e não se soma a ela.

Os números são de perfis simulados, e servem para mostrar que o percurso
se comporta como o desenho diz. Não dizem quanto tempo uma pessoa leva,
nem se ela aprende — o que exigiria o estudo do Apêndice A.

## 6.4 O que a verificação encontrou

O resultado mais útil da verificação não foi o "zero problemas" final,
mas os defeitos que ela encontrou no caminho.

A primeira leitura do sistema pelo autor, já com a verificação mecânica
limpa, encontrou três defeitos que nenhum teste apontaria, porque não são
afirmações falsas, mas experiências ruins:

- **Perguntas que repetiam a frase de cima** (5.7). Dos 244 passos
  guiados, 101 tiveram a frase reescrita: o passo que o autor leu, 46 dos
  que o programa marcou e 54 que ele não marcou e só a leitura achou. O
  programa, portanto, achou menos da metade: a marca por palavras serviu
  de ponto de partida, e não de critério. Um passo de prática, que pedia
  a definição de ponteiro pendente, passou a pedir que se ache o ponteiro
  pendente num trecho. O registro de cada troca, com o antes e o depois,
  acompanha o projeto.
- **O toque errado sem volta.** A resposta travava no primeiro toque,
  para que as razões não a influenciassem, e quem tocava na alternativa
  errada não tinha como corrigir. A trava continua, mas passou para o
  "Confirmar resposta" (3.2).
- **A sessão sem saída.** Não havia como desistir de uma sessão no meio e
  começar do zero; entrou o botão Sair, com as duas saídas de 3.7. Com
  ele, o topo do tópico de oito premissas voltou a transbordar o celular
  em 4 px, o que a conferência no navegador achou.

Da verificação mecânica, alguns exemplos, todos corrigidos antes da
versão descrita:

- **Oito questões com o código partido na tela.** No kc_02, oito questões
  tinham o `\n` do `printf` gravado como quebra de linha de verdade: a
  pessoa via o `printf` cortado em duas linhas, e o código não compilava.
  Uma delas abria a premissa B3. A leitura não as tinha notado; a
  conferência do banco achou as oito na primeira rodada, e o conserto
  juntou a string de volta, sem mexer em mais nada das questões. As que
  pedem um valor passaram a imprimir o da alternativa certa.
- **Uma resposta que não vale no compilador do laboratório.** Uma questão
  do kc_12 pergunta o que imprime `p == NULL` depois de `p` receber o
  endereço de uma variável local de uma função que já retornou, e dá
  como certa a resposta 0. No gcc 16.2, o compilador avisa e devolve
  `NULL` no lugar daquele endereço, e sai 1 — e o padrão do C não define
  aquele valor. A questão ficou fora da trilha até ser reescrita sem
  depender dele; então voltou.
- **Uma afirmação que depende da versão do compilador.** Uma questão do
  kc_11 dizia que o compilador "recusa" aritmética em `void *`; o gcc
  aceita a conta por uma extensão própria, e só avisa com
  `-Wpointer-arith`. A questão já estava fora da trilha, por usar uma
  função de várias linhas; a demonstração do tópico usa a opção e diz
  isso na nota de ambiente.
- **Uma alternativa certa que usava o que não foi ensinado.** Uma questão
  do kc_10 dava como certa "a vira ponteiro para fileira", conceito que a
  escada deixa de fora de propósito; foi reescrita com o vocabulário que
  a escada ensina, com id, gabarito e concepções errôneas mantidos.
- **O treino que repetia a demonstração.** Num ensaio, o primeiro passo
  de prática depois de uma demonstração mostrava a mesma função que a
  demonstração tinha acabado de mostrar: a mesma tela duas vezes
  seguidas. A regra virou teste, e o teste encontrou o mesmo defeito em
  passos de outros três tópicos.
- **Uma nota de ambiente que afirmava o que não foi conferido** ("outros
  compiladores reclamam") foi retirada antes de entrar.
- **Na interface**, o teste de contraste e a conferência no navegador
  encontraram uma lacuna de exercício ilegível no tema claro e um topo
  que transbordava a tela do celular no tópico de oito premissas.

São defeitos que uma leitura atenta deixa passar e que a verificação
mecânica pega, porque compara o texto com o programa, e não com a
memória de quem escreveu.
