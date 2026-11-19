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

## Segunda passada (19/11/2026)

A marca do programa era pista, e não prova. Os 189 degraus guiados que
ela não marcou foram lidos um a um, com o mesmo critério, mais uma
distinção: o passo que MOSTRA uma construção nova e pede para imitá-la
uma vez (montar, completar, tocar ou digitar o que a frase acabou de
mostrar) é assim de propósito, e ficou; os traços de programa ("que
número aparece?") também. O conserto foi nas perguntas de entender —
o que p guarda, por quê, qual destas — em que a frase já dava a
conclusão para o mesmo caso: 54 degraus. Nenhuma alternativa nem retorno
mudou, e os trechos que os testes exigem em cada passo ficaram.

### esc_kc00_B1_3

- antes: O tipo diz que espécie de valor cabe na variável.
- antes: int guarda um número inteiro, como 20. char guarda um caractere, como 'B'.
- depois: O tipo diz que espécie de valor cabe na variável.
- depois: int guarda um número inteiro, como 20. char guarda um caractere, como 'x'.

### esc_kc00_B2_2

- antes: Repare: você escreveu na variável sem declarar de novo.
- antes: Ela existe desde a linha da declaração, mesmo antes de receber qualquer valor.
- depois: Repare: você escreveu na variável sem declarar de novo.
- depois: Quem reserva o lugar da variável é a declaração, e não o primeiro valor.

### esc_kc00_B4_2

- antes: O valor antigo não fica guardado em outro canto da variável.
- antes: Depois de idade = 21; não existe mais 20 nenhum ali.
- depois: O valor antigo não fica guardado em outro canto da variável.
- depois: Uma variável tem lugar para um valor só, e o valor novo ocupa esse lugar inteiro.

### esc_kc01_B1_2

- antes: Quando o programa termina, a memória dele volta para o sistema.
- antes: Na próxima vez que rodar, ele recebe outra: o que a execução anterior guardou não está lá.
- depois: Quando o programa termina, a memória dele volta para o sistema.
- depois: Na próxima vez que rodar, ele recebe outra memória, que pode ter sido de qualquer programa.

### esc_kc01_I1_3

- antes: A variável que guarda o endereço e o bloco são duas coisas, com dois fins diferentes.
- antes: q acaba sozinha, como toda variável local; o bloco, só com free(q);
- depois: A variável que guarda o endereço e o bloco são duas coisas, com dois fins diferentes.
- depois: Variável local acaba sozinha; bloco do malloc, só com free.

### esc_kc02_B1_2

- antes: Em C, o & antes do nome pede o endereço da variável.
- antes: idade é o valor guardado. &idade é o endereço de idade.
- depois: Em C, o & antes do nome pede o endereço da variável.
- depois: Sem o &, o nome dá o valor guardado nela.

### esc_kc02_B3_2

- antes: Depois de p = &idade;, o que está guardado em p é o endereço de idade.
- antes: O valor de idade continua guardado em idade, e não em p.
- depois: Um ponteiro guarda o endereço que recebeu, e só isso.
- depois: O valor da variável apontada continua guardado nela, e não no ponteiro.

### esc_kc02_I2_1

- antes: O tipo antes do * diz o que mora no endereço guardado.
- antes: int *p guarda endereço de int. char *c guarda endereço de char.
- depois: O tipo antes do * diz o que mora no endereço guardado.
- depois: int *p guarda endereço de int; para outro tipo, troca-se o tipo antes do *.

### esc_kc02_I2_2

- antes: O endereço tem de combinar com o tipo do ponteiro.
- antes: Um int *p recebe &idade, que é endereço de int, e não &turma, que é endereço de char.
- depois: O endereço tem de combinar com o tipo do ponteiro.
- depois: Um ponteiro para int recebe endereço de int; um ponteiro para char, endereço de char.

### esc_kc02_I2_3

- antes: Um endereço não é um número inteiro comum.
- antes: Por isso o compilador reclama de n = p; quando n é int e p é ponteiro.
- depois: Um endereço não é um número inteiro comum.
- depois: Ponteiro e int são tipos diferentes, e o compilador confere o tipo de cada lado do =.

### esc_kc02_I3_4

- antes: É isso que o ponteiro dá, e a variável comum não: alcançar a mesma variável de outro ponto do programa.
- antes: Só o endereço viaja. O conteúdo não é copiado.
- depois: A variável comum chega na função como cópia; o ponteiro leva o endereço dela.
- depois: Só o endereço viaja. O conteúdo não é copiado.

### esc_kc03_B1_1

- antes: Declarar uma variável já reserva o lugar dela na memória.
- antes: O valor vem depois. O lugar existe desde a declaração.
- depois: Uma variável precisa de um lugar na memória antes de poder receber valor.
- depois: Quem reserva esse lugar é a declaração.

### esc_kc03_I1_1

- antes: int *p; declara uma variável só: o ponteiro.
- antes: O lugar para onde ele vai apontar não nasce junto. Quem cria esse lugar é outra declaração.
- depois: Declarar cria a variável declarada, e só ela.
- depois: O lugar para onde um ponteiro vai apontar não nasce junto: quem cria esse lugar é outra declaração.

### esc_kc03_I2_3

- antes: O ponteiro também pode já nascer com NULL: int *p = NULL;
- antes: É declarar e dar o valor na mesma linha, como em int idade = 15;
- depois: O ponteiro também pode já nascer valendo NULL, numa declaração com valor.
- depois: É declarar e dar o valor na mesma linha, como em int idade = 15;

### esc_kc04_B1_2

- antes: Por isso &idade é aceito, e &5 faz o compilador reclamar.
- depois: Por isso o & só é aceito antes do nome de uma variável.
- depois: Antes de um número escrito no código, o compilador reclama.

### esc_kc04_B2_1

- antes: &idade é o endereço de idade: o número do lugar dela.
- antes: Pedir o endereço não copia nada. O valor continua guardado em idade, e só lá.
- depois: &idade é o endereço de idade: o número do lugar dela.
- depois: Pedir o endereço de uma variável não copia o que ela guarda.

### esc_kc04_B3_2

- antes: São duas coisas diferentes: p é o endereço guardado, e *p é o valor que mora lá.
- depois: São duas coisas diferentes: o nome do ponteiro dá o endereço guardado.
- depois: Com o * na frente, ele dá o valor que mora lá.

### esc_kc04_B3_3

- antes: Por isso um ponteiro recebe endereço, e não valor: p = &idade; e nunca p = idade;
- depois: Por isso o que se guarda num ponteiro é um endereço, e não um valor.

### esc_kc04_I1_1

- antes: *p quer dizer: vá até o endereço guardado em p.
- antes: Não é outro nome da variável. É um caminho, e o destino é o endereço que estiver em p naquele momento.
- depois: O * diante de um ponteiro quer dizer: vá até o endereço guardado nele.
- depois: Não é outro nome da variável: é um caminho, e o destino é o endereço guardado naquele momento.

### esc_kc04_I2_1

- antes: *p = 7; escreve 7 no lugar apontado por p.
- antes: O ponteiro não muda: continua guardando o mesmo endereço de antes.
- depois: Com o * na frente, a escrita vai para o lugar apontado.
- depois: O ponteiro em si não é escrito: continua guardando o mesmo endereço.

### esc_kc04_I2_3

- antes: Quem muda o ponteiro é a escrita sem o *: p = &nota;
- depois: Quem muda o ponteiro é a escrita sem o *, com um endereço novo do lado direito.

### esc_kc04_I3_3

- antes: Cada coisa tem o seu lugar: o endereço se guarda em p, e o valor se escreve em *p.
- antes: p = &idade; guarda o endereço. *p = 9; escreve no lugar apontado.
- depois: Cada coisa tem o seu lugar: o endereço se guarda no ponteiro, e o valor se escreve no lugar apontado.
- depois: Sem o *, a linha mexe no ponteiro; com o *, no lugar apontado.

### esc_kc05_B2_2

- antes: Isso vale para o 0 escrito ali, na linha.
- antes: Um zero guardado numa variável inteira é um número comum: o compilador reclama de p = n;
- depois: Isso vale para o 0 escrito ali, na linha.
- depois: Um zero guardado numa variável inteira é um número comum, e o compilador reclama de guardá-lo num ponteiro.

### esc_kc05_B2_3

- antes: Dá para forçar: q = (int *)n; manda o compilador tratar o número de n como endereço, e ele aceita.
- antes: Mas a linguagem não promete que saia dali o ponteiro nulo, mesmo com n valendo zero.
- depois: Dá para forçar com um cast: (int *)n manda o compilador tratar o número de n como endereço, e ele aceita.
- depois: Mas só o 0 escrito no código tem a promessa de virar o ponteiro nulo.

### esc_kc05_I1_1

- antes: p == NULL lê o valor guardado em p, e compara.
- antes: Ela não vai ao lugar apontado: quem vai é o *p.
- depois: Comparar um ponteiro lê o que está guardado nele, como em qualquer variável.
- depois: Quem vai ao lugar apontado é o *.

### esc_kc05_I1_2

- antes: São duas perguntas diferentes: p == NULL pergunta do ponteiro; *p == 0 pergunta do lugar apontado.
- antes: Com p valendo NULL, só a primeira pode ser feita.
- depois: São duas perguntas diferentes: p == NULL pergunta do ponteiro; *p == 0 pergunta do lugar apontado.
- depois: Com p valendo NULL, não há lugar apontado para perguntar nada.

### esc_kc05_I2_2

- antes: Essa é uma regra de escrita: no código, o 0 ao lado de um ponteiro quer dizer 'o ponteiro nulo'.
- antes: Ela não diz o que a máquina guarda dentro de p. Isso é assunto de cada máquina.
- depois: Essa é uma regra de escrita: no código, o 0 ao lado de um ponteiro quer dizer 'o ponteiro nulo'.
- depois: Por dentro, cada máquina representa o ponteiro nulo do seu jeito.

### esc_kc05_I3_2

- antes: Por isso, antes de usar *p, pergunta-se ao ponteiro: if (p != NULL)
- antes: Escrever só if (p) quer dizer a mesma coisa: 'se p não é o ponteiro nulo'.
- depois: Por isso, antes de usar *p, pergunta-se ao ponteiro se ele aponta para algum lugar.
- depois: A pergunta se escreve p != NULL, ou só p: if (p) quer dizer 'se p não é o ponteiro nulo'.

### esc_kc06_B1_2

- antes: Na chamada zera(idade); o que vai entre os parênteses é o argumento.
- antes: O parâmetro não é o argumento: é uma variável nova, criada na chamada, com o seu próprio lugar.
- depois: Na chamada, o que vai entre os parênteses é o argumento.
- depois: O parâmetro não é o argumento: é uma variável nova, criada na chamada, com o seu próprio lugar.

### esc_kc07_B2_1

- antes: int notas[3]; cria três caixas de int. int *p; cria uma caixa só: a de p.
- antes: Com o ponteiro não nasce caixa de int nenhuma.
- depois: Declarar um array cria as caixas dele; declarar um ponteiro cria só a caixa do ponteiro.
- depois: Com o ponteiro não nasce caixa de int nenhuma.

### esc_kc07_B4_1

- antes: Em sizeof v, o nome não vira endereço: ali v é o conjunto inteiro.
- antes: É por isso que sizeof v mede as dez caixas, e não um ponteiro.
- depois: Dentro do sizeof, o nome do array não vira endereço: ali ele é o conjunto inteiro.
- depois: É por isso que o sizeof de um array mede todas as caixas, e não um ponteiro.

### esc_kc07_I2_1

- antes: O parâmetro escrito char v[10] é um ponteiro: o mesmo que char *v.
- antes: O 10 dali não cria caixa nenhuma, e a função não fica sabendo dele.
- depois: Um parâmetro escrito com colchetes, como int v[5], é um ponteiro: o mesmo que int *v.
- depois: O número dali não cria caixa nenhuma, e a função não fica sabendo dele.

### esc_kc07_I2_2

- antes: Fora da função, sizeof notas mede as cinco caixas. Dentro dela, sizeof v mede o ponteiro.
- antes: Quantas caixas havia, lá dentro não dá mais para saber.
- depois: Fora da função, o sizeof do array mede todas as caixas; dentro, o parâmetro já é um ponteiro.
- depois: Quantas caixas havia, lá dentro não dá mais para saber.

### esc_kc07_I3_3

- antes: p pode receber outro endereço quando você quiser.
- antes: notas não: o conjunto das caixas não muda de lugar.
- depois: Um ponteiro pode receber outro endereço quando você quiser.
- depois: O nome de um array não: o conjunto das caixas não muda de lugar.

### esc_kc08_B2_2

- antes: O endereço que malloc devolve se guarda no ponteiro: p = malloc(...);
- antes: *p é o que está NO bloco, e só serve depois de p ter o endereço.
- depois: O endereço que malloc devolve se guarda num ponteiro, como todo endereço.
- depois: *p é o que está NO bloco, e só serve depois de p ter o endereço.

### esc_kc08_I1_2

- antes: Quando a função termina, a caixa de p acaba, como toda variável local.
- antes: O bloco continua no monte — e, se p era o único com o endereço, ninguém mais chega nele.
- depois: Quando a função termina, as variáveis locais dela acabam, ponteiro ou não.
- depois: O bloco do malloc fica no monte — e, se só uma variável local tinha o endereço, ninguém mais chega nele.

### esc_kc08_I2_2

- antes: Conferir é perguntar se o ponteiro não é NULL, antes de usar: if (p != NULL) ...
- depois: Conferir é perguntar, antes de usar, se o ponteiro não é NULL.

### esc_kc08_I3_2

- antes: Quem pediu devolve: free(p); antes de a função terminar, enquanto p ainda guarda o endereço.
- depois: Quem pediu devolve, com free, antes de a função terminar e enquanto o ponteiro ainda guarda o endereço.

### esc_kc09_B2_1

- antes: free é uma função como as outras: na chamada free(p), o que entra nela é uma cópia do valor de p.
- antes: O valor de p é um endereço. A variável p fica com quem chamou.
- depois: free é uma função como as outras: na chamada, o que entra nela é uma cópia do valor do argumento.
- depois: O valor de p é um endereço. A variável p fica com quem chamou.

### esc_kc09_B3_1

- antes: São duas coisas: o bloco, no monte, e a caixa de p, que é uma variável sua e fica onde foi declarada.
- antes: free devolve o bloco. A caixa de p não está dentro dele, e não vai junto.
- depois: São duas coisas: o bloco, no monte, e a caixa do ponteiro, que fica onde foi declarada.
- depois: free devolve só o bloco.

### esc_kc09_I3_3

- antes: O costume é uma linha só, logo depois do free: p = NULL;
- depois: O costume é uma linha só, logo depois do free, escrevendo NULL no próprio ponteiro.

### esc_kc09_I4_1

- antes: Depois do free, p guarda um endereço com cara de bom, de um lugar que já não é seu.
- antes: Chamar free(p) de novo é devolver o que não é seu: não é seguro, e o compilador reclama quando vê.
- depois: Depois do free, p guarda um endereço com cara de bom, de um lugar que já não é seu.
- depois: Um bloco só pode ser devolvido uma vez, e o compilador reclama quando vê.

### esc_kc09_I4_3

- antes: Com p pendente, o padrão do C não garante nem copiar nem comparar o valor dele: as comparações que você viu aqui valem nesta máquina.
- antes: O único uso seguro é dar a p um valor novo.
- depois: Com p pendente, o padrão do C não garante nem copiar nem comparar o valor dele: as comparações que você viu aqui valem nesta máquina.
- depois: Ler p, para copiar ou comparar, já é usar o valor dele.

### esc_kc10_B1_1

- antes: p é uma caixa como as outras, e toda caixa tem endereço: &p é o endereço da caixa p.
- antes: &p não é o que p guarda, nem uma cópia de p: é onde a caixa p fica.
- depois: Um ponteiro é uma caixa como as outras, e toda caixa tem endereço.
- depois: O & dá onde a caixa fica, e não o que ela guarda.

### esc_kc10_I1_3

- antes: Na chamada vai o endereço do ponteiro, com o &: troca(&q, ...).
- depois: Na chamada vai o endereço do ponteiro, com o &.

### esc_kc10_I3_1

- antes: pp e p são duas caixas: pp guarda o endereço de p, e p guarda o endereço de idade.
- antes: **pp não pula direto para o número: passa por p, e só então chega em idade.
- depois: Cada estrela é um passo, e cada passo para numa caixa.
- depois: Um ponteiro para ponteiro guarda o endereço de outro ponteiro, e não o do número.

### esc_kc10_I3_3

- antes: *pp é a caixa p: o que se escreve ali é um endereço.
- antes: **pp é a caixa idade: o que se escreve ali é um número.
- depois: Com uma estrela, pp chega na caixa cujo endereço ele guarda; com duas, na caixa seguinte.
- depois: Em cada caixa se escreve o que ela guarda: endereço no ponteiro, número no int.

### esc_kc11_B1_2

- antes: Por isso o compilador reclama de p = 1000;: 1000 é um int, e p quer o endereço de um int.
- depois: Por isso o compilador reclama de guardar um número qualquer num ponteiro: ele quer o endereço de uma caixa do tipo dele.

### esc_kc11_B3_1

- antes: Os elementos de um array ficam grudados, um logo depois do outro, sem buraco entre eles.
- antes: Por isso a distância de &notas[0] a &notas[2] é de duas caixas: &notas[2] - &notas[0] dá 2.
- depois: Os elementos de um array ficam grudados, um logo depois do outro, sem buraco entre eles.
- depois: Por isso a distância entre dois endereços do mesmo array se conta em caixas: é o que mede a conta &notas[2] - &notas[0].

### esc_kc11_I1_2

- antes: Com um ponteiro vale o mesmo: p[1] é *(p + 1). A soma vem antes do *.
- antes: E dá para andar para trás: *(p - 1) é a caixa de trás, que também se escreve p[-1].
- depois: Com um ponteiro vale o mesmo: p[i] é *(p + i). A soma vem antes do *.
- depois: E dá para andar para trás: *(p - 1) é a caixa de trás, que também se escreve p[-1].

### esc_kc11_I3_1

- antes: p + 1 anda um elemento do tipo de p, e não um byte: com int *p, uma caixa de int inteira.
- antes: Quem faz a conta do tamanho é o compilador.
- depois: Somar 1 a um ponteiro anda um elemento do tipo dele, e não um byte.
- depois: Quem faz a conta do tamanho é o compilador.

### esc_kc12_B2_3

- antes: Esse endereço pode ir para outra função enquanto a dona da caixa roda: zera(&n) entrega a caixa n, e zera escreve nela.
- depois: Esse endereço pode ir para outra função enquanto a dona da caixa roda: com ele, a outra função escreve na caixa.

### esc_kc12_B3_2

- antes: Para usar depois o que a função retornou, guarde numa variável: int x = dobro(3);
- depois: Para usar depois o que a função retornou, guarde numa variável, com a chamada do lado direito do =.

### esc_kc12_I1_2

- antes: Quando quem chamou recebe esse endereço, a caixa n já sumiu: sumiu no mesmo instante do retorno.
- depois: Quando quem chamou recebe o endereço de uma local, a caixa dela já sumiu, no mesmo instante do retorno.
