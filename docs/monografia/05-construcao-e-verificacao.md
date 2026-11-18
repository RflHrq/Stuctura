# 5. Construção e verificação

Um sistema de ensino faz afirmações em dois planos. No plano do
**conteúdo**, cada tela afirma algo sobre C: que este trecho imprime 9,
que o compilador reclama daquela linha, que esta alternativa é a certa.
No plano do **comportamento**, o sistema afirma que trata cada estudante
de um jeito: que quem erra com convicção vê a demonstração, que quem não
sabe sobe a escada, que a sessão tem teto. Este capítulo descreve como
cada plano foi verificado sem depender da opinião de quem escreveu o
conteúdo ou o código — e diz, ao fim, o que essa verificação não cobre.

## 5.1 O processo

Cada parte do sistema foi desenhada por escrito antes de ser construída:
um documento de desenho com a intenção, as restrições, as alternativas
consideradas e as decisões tomadas, e um plano em tarefas pequenas, cada
uma com os testes que a provam. As decisões tomadas durante a construção,
quando o plano não respondia, foram registradas com o motivo e o custo de
estarem erradas.

O código foi escrito com **testes antes do código**: o teste de cada
comportamento novo foi escrito e visto falhar antes de a implementação
existir, e só então a implementação foi feita até o teste passar. Um
teste que passa antes da implementação não prova nada — pode estar
testando outra coisa —, e por isso vê-lo falhar é parte do método, e não
formalidade. Testes existentes nunca foram alterados para passar; quando
uma mudança deliberada de comportamento exigiu mudar um teste, a mudança
foi declarada no registro do controle de versão, com o motivo.

## 5.2 O compilador como árbitro do conteúdo

Todo trecho de código que o sistema mostra passa por um **conferidor**
automático antes de entrar no sistema. O conferidor monta cada trecho
dentro de um programa completo — com as bibliotecas padrão de entrada e
saída e de alocação, e com as funções do trecho levadas para fora do
`main` —, compila com o gcc 16.2 (`-std=c17 -Wall`) e confere o que o
texto afirma:

- nos passos de **digitar**, roda o programa e compara a saída inteira
  com a resposta aceita;
- nos passos de **completar** e **escolher** com código, monta cada linha
  possível e exige que as marcadas como inválidas sejam recusadas pelo
  compilador e as demais aceitas;
- nos exemplos resolvidos com saída, roda e compara;
- nas **demonstrações**, roda e compara a saída, ou, quando a
  demonstração é o que o compilador diz, exige que a mensagem afirmada
  saia, e de uma linha só.

As opções de compilador que uma demonstração pode pedir a mais formam uma
lista fechada (`-O1`, `-O2`, `-Wextra`, `-Wnull-dereference`,
`-fanalyzer`, `-Wpointer-arith`): o que está ali vira argumento de
comando, e cada opção entrou na lista com um teste que mostra a
demonstração que ela confirma e que, sem ela, a mesma demonstração não se
confirma. Endereços de memória, que mudam a cada máquina e a cada
execução, aparecem nas demonstrações como números de exemplo, e o
conferidor compara a forma da saída, não o número. Cada processo tem um
limite de tempo, para que um programa que não termina não confira nada.

O conferidor roda dentro da suíte de testes, sobre os 13 tópicos: uma
escada cujo texto deixou de corresponder ao que o compilador faz derruba
a suíte.

## 5.3 A régua do texto, em teste

As regras de escrita da escada (3.4) que podem ser decididas por programa
foram transformadas em testes, que rodam sobre todos os tópicos:

- de três a sete passos por premissa, com os guiados antes dos de
  prática, e pelo menos dois de prática;
- no máximo duas frases de até 30 palavras por passo guiado, e nenhuma
  nos de prática;
- duas versões diferentes por passo, e todo exercício com erro previsto
  e retorno de pelo menos cinco palavras;
- o verbo "reclama" para o que o compilador diz, nunca "não compila" nem
  "recusa", porque a severidade de uma mensagem muda entre versões do
  compilador;
- nenhum passo de digitar cuja resposta seja um endereço;
- demonstrações de até nove linhas, sem pergunta embutida, uma por
  concepção errônea, com a previsão em posições variadas;
- a concepção errônea dita, numa alternativa marcada, só em passo guiado
  da premissa que ela nega;
- todo primeiro passo de prática com um nome curto, que é o que o
  fechamento mostra;
- o treino depois da demonstração não repete o trecho que a
  demonstração acabou de mostrar;
- as questões servidas pela trilha não usam construções que nenhum
  tópico ensinou até ali, e cada premissa abre com questão de código.

Para cada tópico, há ainda testes do que ele apresenta e onde: em que
passo guiado cada construção nova aparece pela primeira vez (`static`, a
conversão `(char *)`, o ponteiro para ponteiro), e quais questões do
banco ficam fora da trilha, com o motivo de cada uma.

## 5.4 Os estudantes simulados

O comportamento foi verificado com **dez estudantes simulados**, cada um
um perfil de resposta definido por programa: o que sabe tudo; o inseguro,
que acerta sem certeza; o que não sabe e aprende com os passos; o que não
sabe e erra todos os passos; o que sustenta a concepção errônea de cada
premissa e muda de ideia depois da demonstração; o que sustenta e não
muda; o que escorrega, errando com a razão certa; o que chuta com
certeza; o que tropeça na prática; e o que abre a explicação antes de
responder.

Cada perfil atravessa cada tópico do começo ao fim, nos dois ritmos, pelo
mesmo motor que atende as pessoas. Os testes conferem, nessas
travessias, as propriedades que o desenho afirma: toda premissa termina
com um dos cinco resultados; nenhuma premissa recebe mais de um trabalho;
a sessão tem teto; quem sustenta uma concepção errônea vê a demonstração
dela; a sessão inteira pode ser reconstruída a partir do registro; e
perfis diferentes terminam com resultados diferentes. A mesma travessia
produz a **medida** de cada tópico — telas e toques por perfil —, que o
Capítulo 6 apresenta.

## 5.5 A interface

Também a interface foi verificada por teste onde isso foi possível: a
razão de contraste de cada par de cores de texto e fundo, nos dois temas,
calculada pela fórmula da WCAG 2.x **[conferir]**; que o realce de código
devolve exatamente o texto original, em todos os trechos de código das
escadas; que nenhuma página carrega nada de outro endereço; que o tema é
escolhido antes de a página aparecer, inclusive em navegador sem
armazenamento local; e que a saída do programa nunca recebe cores de
código. O resto — o desenho de cada tela, o comportamento em celular
(360 px de largura) e em tela larga — foi conferido no navegador, tela a
tela, nos dois temas.

## 5.6 O ensaio

Cada tópico foi atravessado também por sessões de ensaio, num servidor
separado do que está no ar e gravando numa pasta separada da de coleta,
para que nenhuma sessão simulada se misturasse a dados de pessoas. As
sessões foram levadas pelo protocolo HTTP, pelos mesmos perfis simulados,
até cada tipo de tela, e conferidas na página.

## 5.7 O que esta verificação não cobre

O compilador garante que o que a tela afirma sobre um programa é verdade.
Ele não garante que a ideia ensinada é a ideia certa, que a escada está na
ordem mais fácil para um iniciante, que a analogia ajuda, ou que a
concepção errônea do catálogo é a que um estudante de fato tem. Os testes
garantem que o sistema se comporta como o desenho diz; não garantem que o
desenho ensina. A primeira lacuna é preenchida pela revisão do conteúdo
por quem conhece o domínio — o conteúdo das escadas foi escrito com
assistência de um modelo de linguagem e ainda aguarda a revisão do
autor **[atualizar quando a revisão for feita]** —; a segunda, só por um
estudo com estudantes, que é o primeiro dos trabalhos futuros
(Capítulo 7).
