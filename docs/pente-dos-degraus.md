# O pente dos degraus (19/11/2026)

O Rafael leu o primeiro degrau do kc_02 e achou a pergunta confusa: ela
perguntava "o que é o endereço de idade?" logo depois de dizer o que é,
e a alternativa certa era a frase copiada. O pente procurou o mesmo
defeito nos treze tópicos.

**O critério.** Defeito: a frase do degrau diz a conclusão sobre o próprio
caso da pergunta (o mesmo código, os mesmos nomes), ou a última frase é a
alternativa certa — responder vira achar palavras. Fica como está: a frase
dá uma regra geral, e a pergunta obriga a reconhecer no código qual coisa
é qual antes de aplicar.

**Como achou.** Um programa marcou os degraus de escolher e completar em
que as palavras da alternativa certa já estavam nas frases (56 degraus), e
cada um foi lido. A marca é pista, e não prova: degrau com pouca
sobreposição de palavras pode ter o mesmo defeito, e esse só a leitura acha.

**O conserto.** A frase passa a dar a regra (ou um exemplo diferente do da
pergunta), e a conclusão fica para a pessoa. As alternativas e os retornos
não mudaram, menos três trocas: o degrau 1 do kc_02 B1 (endereço de
exemplo, 1000, contra o valor 15), a crença do kc_11 B3_2 (que citava
`char *s = "abc"`, nomes que não estavam na tela) e a versão 1 do kc_09
I2_5 (um degrau de prática que pedia a definição de pendente; agora pede
para achar o ponteiro pendente, com a situação dita no enunciado: "p e q
apontam para dois blocos do malloc, e a última linha foi free(p);. Qual
dos dois está pendente?").

**Ficaram como estavam**, por serem regra geral aplicada a um caso:
esc_kc01_I1_1, esc_kc02_B1_3, esc_kc06_I3_1, esc_kc08_I2_1, esc_kc10_B3_3,
esc_kc11_B2_3, esc_kc12_B1_3, esc_kc12_B3_5 e esc_kc12_I3_1.

## Antes e depois

### esc_kc02_B1_1 (o que o Rafael leu)

- antes: Toda variável fica guardada num lugar da memória.
- antes: Cada lugar tem um número. Esse número é o endereço da variável.
- antes, a pergunta: "idade guarda 15. O que é o endereço de idade?" — "O número do lugar onde idade fica" / "O valor guardado nela: 15" / "Nada disso: o computador acha idade pelo nome"
- depois: Toda variável fica num lugar da memória, e cada lugar tem um número: o endereço.
- depois: É como uma casa: o endereço diz onde ela fica, e não o que tem dentro.
- depois, a pergunta: "Neste exemplo, idade ficou no lugar de número 1000 e guarda 15. Qual é o endereço de idade?" — "1000" / "15" / "idade não tem endereço: o computador a acha pelo nome"

### esc_kc00_B3_2

- antes: Declarar reserva o lugar, mas não escreve nada nele.
- antes: O C não põe zero para você: logo depois de int idade; ninguém sabe o que há ali.
- depois: Declarar reserva o lugar, mas não escreve nada nele.
- depois: E o C não põe zero para você: o lugar fica com o que já estava lá.

### esc_kc01_B3_3

- antes: A função terminar não devolve o bloco: quem acaba é a variável p, e o bloco continua alugado.
- antes: O sistema também não recolhe sozinho. Sem free, o bloco fica ocupado até o programa terminar.
- depois: Quando a função termina, acabam as variáveis locais dela, e o bloco do malloc não é uma delas.
- depois: O sistema também não recolhe bloco sozinho: só o free devolve.

### esc_kc03_B2_2

- antes: Dá para declarar dois nomes numa linha, separados por vírgula.
- antes: O * vale só para o nome em que está colado: em int *p, q; p é ponteiro, e q é um int comum.
- depois: Dá para declarar dois nomes numa linha, separados por vírgula.
- depois: O * vale só para o nome em que está colado: em int *a, b; só a é ponteiro.

### esc_kc03_B3_1

- antes: Declarar reserva o lugar, mas não escreve nada nele.
- antes: O que estava naquele lugar antes continua lá: um valor que ninguém escolheu.
- depois: Declarar reserva o lugar, mas não escreve nada nele.
- depois: E a memória nunca fica vazia: todo lugar guarda algum valor, deixado por quem o usou antes.

### esc_kc03_B3_2

- antes: Com o ponteiro é igual: int *p; reserva o lugar de p e não escreve nada nele.
- antes: O que p guarda nesse momento é um valor que ninguém escolheu.
- depois: Com o ponteiro, declarar faz o mesmo que com a variável comum.
- depois: Reserva o lugar, e não escreve nada nele.

### esc_kc03_I3_1

- antes: *p vai ao lugar cujo endereço está guardado em p.
- antes: Se p ainda não recebeu endereço, esse lugar é um que ninguém escolheu.
- depois: *p vai ao lugar cujo endereço está guardado em p.
- depois: Declarar o ponteiro não escreve endereço nenhum nele: o que ele guarda é um valor que ninguém escolheu.

### esc_kc04_B1_1

- antes: O endereço é o número de um lugar da memória.
- antes: Só tem endereço o que ocupa um lugar: uma variável ocupa; um número escrito no código não.
- depois: O endereço é o número de um lugar da memória.
- depois: Só tem endereço o que ocupa um lugar na memória.

### esc_kc04_I3_1

- antes: O & pergunta: onde está esta variável? O * diz: vá até este endereço.
- antes: Um desfaz o outro: *(&idade) vai até o endereço de idade, e chega na própria idade.
- depois: O & pergunta: onde está esta variável?
- depois: O * diz: vá até este endereço, e veja o que mora lá.

### esc_kc05_B1_1

- antes: NULL é um valor que se guarda num ponteiro. Ele quer dizer: não aponta para lugar nenhum.
- antes: É um valor escolhido, escrito por uma linha, e não o ponteiro estar vazio.
- depois: NULL é um valor que se guarda num ponteiro, como 15 se guarda num int.
- depois: Ele quer dizer: este ponteiro não aponta para lugar nenhum.

### esc_kc05_B3_1

- antes: O valor NULL não é o endereço de variável nenhuma.
- antes: Ele é reservado: existe só para dizer que o ponteiro não aponta para lugar nenhum.
- depois: O valor NULL é reservado: nenhuma variável fica no endereço que ele representa.
- depois: Mesmo escrito como 0, ele não é um lugar da memória como os outros.

### esc_kc05_I2_3

- antes: E o ponteiro nulo não é um número inteiro: é um valor de ponteiro.
- antes: Uma variável inteira que guarda 0 guarda um número. Um ponteiro que vale NULL guarda 'nenhum lugar'.
- depois: O ponteiro nulo não é um número inteiro: é um valor de ponteiro, que quer dizer nenhum lugar.
- depois: O mesmo 0 escrito no código vira coisas diferentes, conforme o tipo de quem o recebe.

### esc_kc05_I3_1

- antes: *p vai ao lugar cujo endereço está em p.
- antes: Com p valendo NULL não há lugar: o que o programa faz aí não é definido. Pode parar, pode seguir errado.
- depois: *p vai ao lugar cujo endereço está em p.
- depois: Quando esse lugar não existe, o padrão do C não diz o que acontece: o programa pode parar, ou seguir errado.

### esc_kc06_I2_1

- antes: Na chamada poe(&idade); o que é copiado para o parâmetro é o endereço de idade.
- antes: A cópia de um endereço aponta para o mesmo lugar que o original.
- depois: Numa chamada, o parâmetro recebe uma cópia do que vai entre os parênteses.
- depois: A cópia de um endereço aponta para o mesmo lugar que o original.

### esc_kc07_B1_1

- antes: int notas[3]; cria três caixas de int, grudadas uma na outra. Cada caixa é uma variável.
- antes: O nome notas vale para o conjunto das três, e não para uma caixa só.
- depois: int pesos[4]; cria quatro caixas de int, grudadas uma na outra, e cada caixa é uma variável.
- depois: O nome do array vale para o conjunto das caixas, e não para uma caixa só.

### esc_kc07_B1_4

- antes: char nome[] = "ana"; cria quatro caixas de char: a, n, a e uma marca de fim, o terminador.
- antes: char *p = "ana"; cria só a caixa de p, com o endereço de letras guardadas em outro lugar.
- depois: char a[] = "oi"; cria três caixas de char: o, i e uma marca de fim, o terminador.
- depois: char *b = "oi"; cria só a caixa de b, com o endereço de letras guardadas em outro lugar.

### esc_kc07_B3_3

- antes: Na chamada zera(notas); acontece a mesma troca: o que é copiado para o parâmetro é o endereço da primeira caixa.
- antes: O parâmetro int v[] é um ponteiro, como int *v.
- depois: Na chamada, o nome do array faz a troca de sempre: vira o endereço da primeira caixa.
- depois: E o parâmetro int v[] é um ponteiro, como int *v: recebe uma cópia, como todo parâmetro.

### esc_kc07_B4_2

- antes: O outro lugar é o &: &v é o endereço do conjunto inteiro, e não o de uma caixa.
- antes: v e &v marcam o mesmo ponto da memória, mas têm tipos diferentes: um aponta uma caixa, o outro o conjunto.
- depois: O outro lugar é o &: com ele na frente, o nome do array dá o endereço do conjunto inteiro, e não o de uma caixa.
- depois: Os dois endereços marcam o mesmo ponto da memória, mas têm tipos diferentes.

### esc_kc07_I1_2

- antes: O nome do array não recebe atribuição: de copia = notas; o compilador reclama.
- antes: As caixas não mudam de lugar, e o conjunto não é trocado por outro.
- depois: O nome de um array não recebe atribuição, e o compilador reclama de quem tenta.
- depois: As caixas não mudam de lugar, e o conjunto não é trocado por outro.

### esc_kc07_I3_2

- antes: A escrita é igual, mas os tipos são diferentes: notas é o conjunto das três caixas de int.
- antes: p é uma caixa só, que guarda um endereço.
- depois: Um array e um ponteiro podem se escrever igual, com os colchetes, e mesmo assim são coisas diferentes.
- depois: O array é o conjunto das caixas; o ponteiro é uma caixa só, que guarda um endereço.

### esc_kc08_B1_1

- antes: O número entre os parênteses de malloc é um tamanho em bytes. Um byte é o espaço de uma caixa de char.
- antes: malloc(10) pede dez bytes. Ele não sabe o que você vai guardar ali.
- depois: O número entre os parênteses de malloc é um tamanho em bytes, e um byte é o espaço de uma caixa de char.
- depois: malloc não sabe o que você vai guardar ali: nem olha o tipo do ponteiro.

### esc_kc08_B2_1

- antes: malloc devolve o endereço do bloco que conseguiu, e é esse endereço que fica guardado em p.
- antes: Se não conseguir bloco nenhum, devolve NULL.
- depois: malloc não entrega o bloco em si: devolve o endereço dele.
- depois: Se não conseguir bloco nenhum, devolve NULL.

### esc_kc08_B3_1

- antes: O bloco chega do jeito que estava: malloc não limpa nada antes de entregar.
- antes: O que há nele é sobra, um valor que ninguém escolheu.
- depois: malloc entrega o bloco do jeito que estava: não limpa nada antes.
- depois: É como declarar uma variável e não dar valor a ela.

### esc_kc08_I1_1

- antes: São duas coisas: a caixa de p, que é uma variável local e fica na pilha, e o bloco, que fica no monte.
- antes: p aponta para o monte, mas não mora lá.
- depois: Variável local mora na pilha; bloco de malloc mora no monte.
- depois: Apontar para um lugar não é morar nele.

### esc_kc09_B1_1

- antes: free(p) recebe só o endereço do bloco. O tamanho, quem anotou foi o alocador, na hora de entregar.
- antes: O ponteiro não carrega tamanho nenhum: guarda um endereço, e mais nada.
- depois: Quem anota o tamanho do bloco é o alocador, na hora de entregá-lo.
- depois: Por isso free(p) funciona recebendo só o endereço.

### esc_kc09_B1_2

- antes: sizeof v mede o array inteiro, porque v é o conjunto das caixas.
- antes: sizeof p mede só o ponteiro: quantas caixas há no bloco, p não sabe.
- depois: sizeof de um array mede o conjunto inteiro das caixas.
- depois: sizeof de um ponteiro mede só a caixa do ponteiro: quantas caixas há no bloco, ele não sabe.

### esc_kc09_B2_3

- antes: Com free é igual: ela usa a cópia para achar o bloco e devolvê-lo.
- antes: No p de quem chamou ela não tem como tocar.
- depois: free recebe uma cópia do endereço guardado em p, como toda função recebe cópias.
- depois: Com a cópia do endereço ela chega ao bloco; o p de quem chamou é outra caixa.

### esc_kc09_B3_2

- antes: A caixa de p acaba como toda variável local: no fim da função em que foi declarada.
- antes: O free não tem nada com isso.
- depois: Toda variável local acaba no fim da função em que foi declarada, seja ponteiro ou não.
- depois: O free devolve o bloco, e não mexe na caixa do ponteiro.

### esc_kc09_B4_1

- antes: Devolvido, o bloco deixa de ser seu: free(p); entrega o lugar de volta ao alocador.
- antes: O alocador pode dá-lo ao próximo malloc. O que você deixou lá não está guardado para você.
- depois: malloc aluga um lugar do alocador; free devolve o aluguel.
- depois: Lugar devolvido volta para o alocador, junto com os que ainda não foram alugados.

### esc_kc09_I1_1

- antes: free recebeu só uma cópia do endereço. No p de quem chamou ela não tem como escrever.
- antes: Por isso, depois do free, p não vira NULL: continua com o endereço de antes.
- depois: free recebe só uma cópia do endereço guardado em p.
- depois: No p de quem chamou ela não tem como escrever.

### esc_kc09_I1_3

- antes: Se alguém vai escrever NULL em p, é você, numa linha sua: p = NULL;
- depois: Depois do free, p continua com o endereço antigo, e nada no programa o troca sozinho.
- depois: Uma variável só muda quando uma linha escreve nela.

### esc_kc09_I2_1

- antes: free devolve o bloco, e só. A variável p não é apagada: continua declarada, com o mesmo endereço dentro.
- antes: Esse endereço leva agora a um lugar que não é mais seu. Um ponteiro assim se chama pendente.
- depois: free devolve o bloco, e só: não mexe em variável nenhuma de quem chamou.
- depois: Um ponteiro que guarda o endereço de um lugar que já não é seu se chama pendente.

### esc_kc09_I3_1

- antes: Depois do free, nada no programa avisa que o endereço em p ficou ruim: ele tem a mesma cara de antes.
- antes: Escrever p = NULL; logo depois é o registro de que p não aponta mais para nada.
- depois: Depois do free, nada no programa avisa que o endereço em p ficou ruim: ele tem a mesma cara de antes.
- depois: Já o NULL diz, com todas as letras: não aponta para lugar nenhum.

### esc_kc09_I4_2

- antes: A exceção é o NULL: free(NULL) não faz nada.
- antes: Por isso p = NULL; depois do free protege também de um segundo free.
- depois: A exceção é o NULL: free(NULL) não faz nada, e não é erro.

### esc_kc10_B2_1

- antes: p não é outro nome de idade: é uma caixa, que guarda o endereço de idade.
- antes: O * é um passo: sai da caixa p e vai até a caixa cujo endereço está lá.
- depois: Um ponteiro não é outro nome da variável: é uma caixa à parte, que guarda um endereço.
- depois: O * é um passo: sai da caixa do ponteiro e vai até a caixa cujo endereço está lá.

### esc_kc10_B3_1

- antes: O tipo diz quantos passos há até o valor: int * é um nível, int ** são dois.
- antes: As estrelas da declaração fixam isso. Não dá para dar um passo que o tipo não tem.
- depois: O tipo diz quantos passos há até o valor: cada estrela da declaração é um nível, um passo.
- depois: Não dá para dar um passo que o tipo não tem.

### esc_kc10_I1_1

- antes: A função que recebe p recebe uma cópia do endereço que estava no ponteiro de quem chamou.
- antes: Trocar a cópia não troca o ponteiro de quem chamou.
- depois: Um parâmetro ponteiro recebe uma cópia do endereço que estava no ponteiro de quem chamou.
- depois: São duas caixas: a do parâmetro, que é da função, e a de quem chamou.

### esc_kc10_I2_1

- antes: int a[3][4]; cria doze caixas de int, grudadas: três fileiras de quatro.
- antes: Não há ponteiro nenhum ali: nem três, nem um.
- depois: int a[3][4]; cria doze caixas de int, grudadas: três fileiras de quatro.
- e a versão 1 da pergunta passou de int a[3][4]; para int c[4][2];, para a frase não responder por ela.
- depois: Não há ponteiro nenhum ali dentro: só as caixas.

### esc_kc11_B1_1

- antes: Um ponteiro guarda um endereço e sabe o tipo do que está lá: int *p aponta para um int, char *c para um char.
- antes: O tipo vem escrito na declaração. Ponteiro não é um número solto.
- depois: Um ponteiro guarda um endereço, e a declaração diz o tipo do que mora lá: é o que vem antes do *.
- depois: Ponteiro não é um número solto.

### esc_kc11_B2_1

- antes: O tamanho de um tipo é fixo: todo char ocupa 1 byte, e todo int ocupa o mesmo tanto, numa mesma máquina.
- antes: O compilador sabe esse tamanho pela declaração, antes de o programa rodar.
- depois: O tamanho de um tipo é fixo: todo char ocupa 1 byte, e todo int ocupa o mesmo tanto, numa mesma máquina.
- depois: E o tipo do que mora no endereço vem escrito na declaração do ponteiro.

### esc_kc11_B3_2

- antes: char s[] = "pai"; cria quatro caixas de char grudadas, cópia do texto, e elas são de s.
- antes: char *t = "pai"; cria uma caixa só, um ponteiro para letras grudadas que não são de t.
- depois: char s[] = "oi"; cria as caixas do texto, uma cópia dele, e elas são de s.
- depois: char *t = "oi"; cria uma caixa só: um ponteiro para letras que não são de t.
- e a versão 1 da pergunta passou a usar os nomes x e y no lugar de s e t, para a frase não responder por ela.

### esc_kc11_I2_1

- antes: Para andar, o ponteiro precisa saber o tamanho da caixa do destino. O void * não sabe: não tem tipo nenhum.
- antes: Por isso o padrão do C não define v + 1: não há quanto andar.
- depois: Para andar, o ponteiro precisa saber o tamanho da caixa do destino, e quem diz esse tamanho é o tipo.
- depois: O void * não tem tipo nenhum.

### esc_kc12_B2_1

- antes: Enquanto a função roda, &n é o endereço da caixa n: um endereço como outro qualquer.
- antes: &n não é uma cópia de n: é onde a própria n está.
- depois: Uma variável local tem endereço como qualquer outra, enquanto a função roda.
- depois: O & dá o lugar onde a variável está, e não uma cópia dela.

### esc_kc12_B3_1

- antes: O valor do return é copiado para o lugar da chamada. int x = dobro(3); guarda essa cópia em x.
- antes: Se ninguém guardar, a cópia se perde.
- depois: O valor do return é copiado para o lugar da chamada.
- depois: Ele só fica guardado se a linha o guardar numa variável, como em int x = f();

### esc_kc12_I1_1

- antes: return &n copia o endereço de n. A caixa n não vai junto: fica para trás e sai no retorno.
- antes: Retornar &local devolve um endereço, e não a variável.
- depois: O return copia o valor da expressão para quem chamou: o que viaja é sempre uma cópia.
- depois: As caixas da função ficam para trás, e saem quando ela termina.

### esc_kc12_I2_1

- antes: static muda a duração: a caixa dura o programa inteiro, e o endereço dela vale depois do retorno.
- antes: O nome não muda de lugar: n continua sendo um nome só de dentro da função.
- depois: Uma variável tem duas coisas: até quando a caixa dura (a duração) e de onde o nome é visto (o escopo).
- depois: static mexe só na primeira: a caixa passa a durar o programa inteiro.

### esc_kc12_I2_3

- antes: Sem static, o erro às vezes parece funcionar: o lugar onde a caixa ficava pode ainda guardar o valor antigo. Parecer funcionar não é funcionar.
- depois: Sem static, o erro às vezes parece funcionar: quando a caixa sai, o lugar dela não é apagado, e pode guardar o valor antigo.
- depois: Ler esse lugar é ler o que sobrou, e não a variável.
