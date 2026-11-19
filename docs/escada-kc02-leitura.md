# A escada do kc_02 — O que é um ponteiro

Texto para leitura, gerado de `mvp/dominio/escada_kc02.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — A memória é uma rua de lugares numerados. O número do lugar é o endereço — não o que está guardado nele.

### Degrau 1 — guiado, escolher

> Toda variável fica num lugar da memória, e cada lugar tem um número: o endereço.
> É como uma casa: o endereço diz onde ela fica, e não o que tem dentro.

**Versão 1.** Neste exemplo, idade ficou no lugar de número 1000 e guarda 15. Qual é o endereço de idade?

Já está escrito:

```c
int idade;
idade = 15;
```

Opções: `1000`  `15`  `idade não tem endereço: o computador a acha pelo nome`

Resposta certa: `1000`

Se errar:

- respondeu `15` → 15 é o que está guardado dentro de idade. O endereço é o número do lugar onde ela fica: 1000.
- respondeu `idade não tem endereço: o computador a acha pelo nome` → O nome é para quem escreve o código. Para a máquina, idade é o lugar 1000: é por esse número que ela chega lá. _(aponta a crença `memory_is_by_name`)_
- qualquer outro erro → O endereço de idade é 1000, o número do lugar. O 15 é o que está guardado lá dentro.

**Versão 2.** Neste exemplo, nota ficou no lugar de número 2000 e guarda 7. Qual é o endereço de nota?

Já está escrito:

```c
int nota;
nota = 7;
```

Opções: `2000`  `7`  `nota não tem endereço: o computador a acha pelo nome`

Resposta certa: `2000`

Se errar:

- respondeu `7` → 7 é o que está guardado dentro de nota. O endereço é o número do lugar onde ela fica: 2000.
- respondeu `nota não tem endereço: o computador a acha pelo nome` → O nome é para quem escreve o código. Para a máquina, nota é o lugar 2000: é por esse número que ela chega lá. _(aponta a crença `memory_is_by_name`)_
- qualquer outro erro → O endereço de nota é 2000, o número do lugar. O 7 é o que está guardado lá dentro.

### Degrau 2 — guiado, escolher

> Em C, o & antes do nome pede o endereço da variável.
> idade é o valor guardado. &idade é o endereço de idade.

**Versão 1.** Qual destas é o endereço de idade?

Já está escrito:

```c
int idade;
idade = 15;
```

Opções: `&idade`  `idade`  `15`

Resposta certa: `&idade`

Se errar:

- respondeu `idade` → idade, sem o &, é o valor guardado: 15. O endereço se pede com o & na frente: &idade
- respondeu `15` → 15 é o valor guardado. O endereço se pede com o & antes do nome: &idade
- qualquer outro erro → O endereço de idade se escreve &idade.

**Versão 2.** Qual destas é o endereço de nota?

Já está escrito:

```c
int nota;
nota = 7;
```

Opções: `&nota`  `nota`  `7`

Resposta certa: `&nota`

Se errar:

- respondeu `nota` → nota, sem o &, é o valor guardado: 7. O endereço se pede com o & na frente: &nota
- respondeu `7` → 7 é o valor guardado. O endereço se pede com o & antes do nome: &nota
- qualquer outro erro → O endereço de nota se escreve &nota.

### Degrau 3 — guiado, completar

> Para mostrar um endereço na tela, o printf usa %p no lugar do %d.
> O (void *) antes do endereço é o jeito de entregá-lo ao %p: escreva sempre assim.

**Versão 1.** Complete para mostrar o endereço de idade.

Já está escrito:

```c
int idade;
idade = 15;
```

```c
printf("%p\n", (void *)___);
```

Peças: `&idade`  `idade`  `15`

Resposta certa: `printf("%p\n", (void *)&idade);`

Se errar:

- respondeu `printf("%p\n", (void *)idade);` → idade, sem o &, é o valor guardado. Para o endereço falta o &: (void *)&idade
- respondeu `printf("%p\n", (void *)15);` → 15 é o valor guardado em idade. O endereço dela é &idade.
- qualquer outro erro → O endereço de idade é &idade: printf("%p\n", (void *)&idade);

**Versão 2.** Complete para mostrar o endereço de nota.

Já está escrito:

```c
int nota;
nota = 7;
```

```c
printf("%p\n", (void *)___);
```

Peças: `&nota`  `nota`  `7`

Resposta certa: `printf("%p\n", (void *)&nota);`

Se errar:

- respondeu `printf("%p\n", (void *)nota);` → nota, sem o &, é o valor guardado. Para o endereço falta o &: (void *)&nota
- respondeu `printf("%p\n", (void *)7);` → 7 é o valor guardado em nota. O endereço dela é &nota.
- qualquer outro erro → O endereço de nota é &nota: printf("%p\n", (void *)&nota);

### Degrau 4 — prática, montar

_Nome do passo, no fechamento: Mostrar na tela o endereço de uma variável_

**Versão 1.** Monte a linha que mostra na tela o endereço de nota.

Já está escrito:

```c
int nota;
nota = 7;
```

Peças: `printf("%p\n",`  `(void *)`  `&nota`  `);`  `nota`

Resposta certa: `printf("%p\n", (void *)&nota);`

Se errar:

- respondeu `printf("%p\n", (void *) nota );` → nota, sem o &, é o valor guardado. O endereço é &nota.
- respondeu `printf("%p\n", &nota );` → Faltou o (void *) antes do endereço: é assim que o %p o recebe.
- respondeu `printf("%p\n", nota );` → nota, sem o &, é o valor guardado, e faltou o (void *). O endereço vai assim: (void *)&nota
- qualquer outro erro → A linha é o printf com %p, o (void *) e o endereço: printf("%p\n", (void *)&nota);

**Versão 2.** Monte a linha que mostra na tela o endereço de idade.

Já está escrito:

```c
int idade;
idade = 15;
```

Peças: `printf("%p\n",`  `(void *)`  `&idade`  `);`  `idade`

Resposta certa: `printf("%p\n", (void *)&idade);`

Se errar:

- respondeu `printf("%p\n", (void *) idade );` → idade, sem o &, é o valor guardado. O endereço é &idade.
- respondeu `printf("%p\n", &idade );` → Faltou o (void *) antes do endereço: é assim que o %p o recebe.
- respondeu `printf("%p\n", idade );` → idade, sem o &, é o valor guardado, e faltou o (void *). O endereço vai assim: (void *)&idade
- qualquer outro erro → A linha é o printf com %p, o (void *) e o endereço: printf("%p\n", (void *)&idade);

### Degrau 5 — prática, escolher

**Versão 1.** A última linha troca o valor de idade. O que acontece com o endereço dela?

Já está escrito:

```c
int idade;

idade = 15;
idade = 16;
```

Opções: `Continua o mesmo: mudou o que está guardado, e não o lugar`  `Muda também: valor novo, endereço novo`  `Some: o endereço era do 15`

Resposta certa: `Continua o mesmo: mudou o que está guardado, e não o lugar`

Se errar:

- respondeu `Muda também: valor novo, endereço novo` → O endereço é do lugar, e não do valor. idade continua no mesmo lugar; só o que está guardado mudou.
- respondeu `Some: o endereço era do 15` → O endereço é do lugar onde idade fica, e não do 15. O lugar continua lá, agora guardando 16.
- qualquer outro erro → O endereço é o número do lugar. Trocar o valor guardado não muda o lugar.

**Versão 2.** A última linha troca o valor de nota. O que acontece com o endereço dela?

Já está escrito:

```c
int nota;

nota = 7;
nota = 9;
```

Opções: `Continua o mesmo: mudou o que está guardado, e não o lugar`  `Muda também: valor novo, endereço novo`  `Some: o endereço era do 7`

Resposta certa: `Continua o mesmo: mudou o que está guardado, e não o lugar`

Se errar:

- respondeu `Muda também: valor novo, endereço novo` → O endereço é do lugar, e não do valor. nota continua no mesmo lugar; só o que está guardado mudou.
- respondeu `Some: o endereço era do 7` → O endereço é do lugar onde nota fica, e não do 7. O lugar continua lá, agora guardando 9.
- qualquer outro erro → O endereço é o número do lugar. Trocar o valor guardado não muda o lugar.

### Se errar a pergunta do topo: a revisão

> Toda variável fica num lugar da memória, e todo lugar tem um número: o endereço.
> idade é o valor guardado. &idade é o endereço: o número do lugar.

```c
int idade;

idade = 15;
printf("%d\n", idade);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> O computador acha a variável pelo nome dela; número de lugar é detalhe do compilador.

```c
int idade;
int *p;

idade = 15;
p = &idade;
*p = 16;
printf("%d\n", idade);
```

**p guarda o endereço de idade, e a linha *p = 16; escreve 16 no lugar que tem esse endereço. Ela não cita o nome idade. O que o trecho imprime?**

- 15 _(é o que a crença espera)_
- 16 _(é o que a máquina faz)_

A máquina imprime:

```
16
```

O que isto mostra: Saiu 16. A linha que mudou o valor não cita o nome idade: chegou lá pelo endereço. O nome é do código que você escreve; a máquina acha a variável pelo número do lugar.

## B2 — p é uma caixa como as outras: ocupa espaço, e a caixa p também tem um endereço, que é dela.

### Degrau 1 — guiado, tocar

> Um endereço também pode ser guardado numa variável.
> A variável que guarda endereço se chama ponteiro, e se declara com um * antes do nome: int *p;

**Versão 1.** Toque no sinal que faz de p um ponteiro.

```c
int *p;
```

Peças: `int`  `*`  `p`  `;`

Resposta certa: `*`

Se errar:

- respondeu `int` → int diz o que mora no endereço guardado: um inteiro. Quem faz de p um ponteiro é o * antes do nome.
- respondeu `p` → p é o nome. Quem faz dele um ponteiro é o * que vem antes.
- respondeu `;` → O ponto e vírgula só fecha a linha. Quem faz de p um ponteiro é o * antes do nome.
- qualquer outro erro → É o * antes do nome que faz de p um ponteiro: int *p;

**Versão 2.** Toque no sinal que faz de q um ponteiro.

```c
int *q;
```

Peças: `int`  `*`  `q`  `;`

Resposta certa: `*`

Se errar:

- respondeu `int` → int diz o que mora no endereço guardado: um inteiro. Quem faz de q um ponteiro é o * antes do nome.
- respondeu `q` → q é o nome. Quem faz dele um ponteiro é o * que vem antes.
- respondeu `;` → O ponto e vírgula só fecha a linha. Quem faz de q um ponteiro é o * antes do nome.
- qualquer outro erro → É o * antes do nome que faz de q um ponteiro: int *q;

### Degrau 2 — guiado, montar

> Declarar um ponteiro é declarar uma variável: tipo, nome e ponto e vírgula.
> A diferença é o * antes do nome.

**Versão 1.** Declare um ponteiro para inteiro chamado p.

Peças: `int`  `*`  `p`  `;`  `&`

Resposta certa: `int *p;`

Se errar:

- respondeu `int p ;` → Sem o *, p é um inteiro comum, e não um ponteiro. Com ele: int *p;
- respondeu `int & p ;` → O & pede o endereço de uma variável que já existe. Na declaração do ponteiro o sinal é o *: int *p;
- respondeu `* int p ;` → O tipo vem primeiro, e o * fica colado no nome: int *p;
- qualquer outro erro → A declaração é o tipo, o *, o nome e o ponto e vírgula: int *p;

**Versão 2.** Declare um ponteiro para inteiro chamado q.

Peças: `int`  `*`  `q`  `;`  `&`

Resposta certa: `int *q;`

Se errar:

- respondeu `int q ;` → Sem o *, q é um inteiro comum, e não um ponteiro. Com ele: int *q;
- respondeu `int & q ;` → O & pede o endereço de uma variável que já existe. Na declaração do ponteiro o sinal é o *: int *q;
- respondeu `* int q ;` → O tipo vem primeiro, e o * fica colado no nome: int *q;
- qualquer outro erro → A declaração é o tipo, o *, o nome e o ponto e vírgula: int *q;

### Degrau 3 — guiado, escolher

> O ponteiro é uma variável como as outras: ocupa um lugar da memória.
> Por isso ele também tem endereço. O de p é &p.

**Versão 1.** Depois dessas duas linhas, quantos lugares da memória estão reservados?

Já está escrito:

```c
int idade;
int *p;
```

Opções: `Dois: o de idade e o de p`  `Um: o de idade. O ponteiro é só uma seta, não ocupa lugar`  `Nenhum: nenhuma das duas recebeu valor`

Resposta certa: `Dois: o de idade e o de p`

Se errar:

- respondeu `Um: o de idade. O ponteiro é só uma seta, não ocupa lugar` → O ponteiro não é só uma seta: é uma variável, e ocupa o lugar dela. São dois lugares, o de idade e o de p. _(aponta a crença `pointer_has_no_address`)_
- respondeu `Nenhum: nenhuma das duas recebeu valor` → Declarar já reserva o lugar, com valor ou sem. São dois lugares: o de idade e o de p.
- qualquer outro erro → São dois lugares: o de idade e o de p. O ponteiro é uma variável, e ocupa o dele.

**Versão 2.** Depois dessas duas linhas, quantos lugares da memória estão reservados?

Já está escrito:

```c
int nota;
int *q;
```

Opções: `Dois: o de nota e o de q`  `Um: o de nota. O ponteiro é só uma seta, não ocupa lugar`  `Nenhum: nenhuma das duas recebeu valor`

Resposta certa: `Dois: o de nota e o de q`

Se errar:

- respondeu `Um: o de nota. O ponteiro é só uma seta, não ocupa lugar` → O ponteiro não é só uma seta: é uma variável, e ocupa o lugar dela. São dois lugares, o de nota e o de q. _(aponta a crença `pointer_has_no_address`)_
- respondeu `Nenhum: nenhuma das duas recebeu valor` → Declarar já reserva o lugar, com valor ou sem. São dois lugares: o de nota e o de q.
- qualquer outro erro → São dois lugares: o de nota e o de q. O ponteiro é uma variável, e ocupa o dele.

### Degrau 4 — prática, completar

_Nome do passo, no fechamento: Pedir o endereço do próprio ponteiro_

**Versão 1.** Complete para mostrar o endereço do próprio ponteiro.

Já está escrito:

```c
int idade;
int *p;
```

```c
printf("%p\n", (void *)___);
```

Peças: `&p`  `&idade`  `*p`

Resposta certa: `printf("%p\n", (void *)&p);`

Se errar:

- respondeu `printf("%p\n", (void *)&idade);` → &idade é o endereço de idade. O ponteiro é outra variável, com o endereço dela: &p
- respondeu `printf("%p\n", (void *)*p);` → O * é da declaração do ponteiro. O endereço de qualquer variável se pede com o &: &p
- qualquer outro erro → O ponteiro é uma variável, e o endereço dele é &p: printf("%p\n", (void *)&p);

**Versão 2.** Complete para mostrar o endereço do próprio ponteiro.

Já está escrito:

```c
int nota;
int *q;
```

```c
printf("%p\n", (void *)___);
```

Peças: `&q`  `&nota`  `*q`

Resposta certa: `printf("%p\n", (void *)&q);`

Se errar:

- respondeu `printf("%p\n", (void *)&nota);` → &nota é o endereço de nota. O ponteiro é outra variável, com o endereço dela: &q
- respondeu `printf("%p\n", (void *)*q);` → O * é da declaração do ponteiro. O endereço de qualquer variável se pede com o &: &q
- qualquer outro erro → O ponteiro é uma variável, e o endereço dele é &q: printf("%p\n", (void *)&q);

### Degrau 5 — prática, montar

**Versão 1.** Declare um inteiro chamado nota e um ponteiro para inteiro chamado q.

Peças: `int nota;`  `int *q;`  `int q;`  `nota *q;`

Resposta certa: `int nota; int *q;`

Se errar:

- respondeu `int nota; int q;` → Sem o *, q é um inteiro comum. O ponteiro se declara com o * antes do nome: int *q;
- respondeu `int nota; nota *q;` → nota é o nome de uma variável, e não um tipo. O ponteiro para inteiro é int *q;
- qualquer outro erro → São duas declarações: int nota; e int *q;

**Versão 2.** Declare um inteiro chamado idade e um ponteiro para inteiro chamado p.

Peças: `int idade;`  `int *p;`  `int p;`  `idade *p;`

Resposta certa: `int idade; int *p;`

Se errar:

- respondeu `int idade; int p;` → Sem o *, p é um inteiro comum. O ponteiro se declara com o * antes do nome: int *p;
- respondeu `int idade; idade *p;` → idade é o nome de uma variável, e não um tipo. O ponteiro para inteiro é int *p;
- qualquer outro erro → São duas declarações: int idade; e int *p;

### Se errar a pergunta do topo: a revisão

> Um ponteiro é uma variável como as outras: tem tipo, nome e um lugar na memória.
> Por ser variável, o ponteiro também tem endereço. O de p é &p.

```c
int idade;
int *p;
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro não ocupa lugar nenhum: ele é só a seta que liga uma caixa à outra.

```c
int idade;
int *p;

p = &idade;
printf("%p\n", (void *)&idade);
printf("%p\n", (void *)&p);
```

**A primeira linha de printf mostra o endereço de idade. A segunda pede o endereço do próprio ponteiro. O que as duas mostram?**

- Dois endereços diferentes _(é o que a máquina faz)_
- O mesmo endereço, duas vezes
- Só a primeira mostra: ponteiro não tem endereço _(é o que a crença espera)_

A máquina imprime:

```
0x1000
0x2A00
```

_Os números dos lugares mudam de máquina para máquina; aqui eles aparecem como números de exemplo. O que foi conferido é que as duas linhas saem, e com endereços diferentes._

O que isto mostra: Saíram dois endereços, e diferentes: um é o lugar de idade, o outro é o lugar do próprio p. O ponteiro não é só uma seta — é uma variável, e ocupa o lugar dela.

## B3 — O que está dentro de p é um endereço: o número do lugar onde outra caixa fica.

### Degrau 1 — guiado, montar

> O ponteiro guarda um endereço.
> Para guardar em p o endereço de idade, escreva p = &idade;

**Versão 1.** Guarde em p o endereço de idade.

Já está escrito:

```c
int idade;
int *p;
```

Peças: `p`  `=`  `&idade`  `;`  `idade`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = idade ;` → idade, sem o &, é o valor guardado, e o ponteiro guarda endereço. O compilador reclama. O certo é p = &idade;
- respondeu `&idade = p ;` → Quem recebe fica à esquerda do sinal de igual. É p que recebe o endereço: p = &idade;
- qualquer outro erro → O ponteiro recebe o endereço: p = &idade;

**Versão 2.** Guarde em q o endereço de nota.

Já está escrito:

```c
int nota;
int *q;
```

Peças: `q`  `=`  `&nota`  `;`  `nota`

Resposta certa: `q = &nota;`

Se errar:

- respondeu `q = nota ;` → nota, sem o &, é o valor guardado, e o ponteiro guarda endereço. O compilador reclama. O certo é q = &nota;
- respondeu `&nota = q ;` → Quem recebe fica à esquerda do sinal de igual. É q que recebe o endereço: q = &nota;
- qualquer outro erro → O ponteiro recebe o endereço: q = &nota;

### Degrau 2 — guiado, escolher

> Depois de p = &idade;, o que está guardado em p é o endereço de idade.
> O valor de idade continua guardado em idade, e não em p.

**Versão 1.** idade guarda 15. O que está guardado em p?

Já está escrito:

```c
int idade;
int *p;

idade = 15;
p = &idade;
```

Opções: `O endereço de idade`  `O valor 15: o ponteiro é o próprio dado`  `O nome idade`

Resposta certa: `O endereço de idade`

Se errar:

- respondeu `O valor 15: o ponteiro é o próprio dado` → O 15 está guardado em idade. O que p guarda é o endereço: o número do lugar onde idade fica. _(aponta a crença `pointer_is_data`)_
- respondeu `O nome idade` → Ponteiro não guarda nome. Guarda o endereço: o número do lugar onde idade fica.
- qualquer outro erro → p guarda o endereço de idade. O 15 fica em idade.

**Versão 2.** nota guarda 7. O que está guardado em q?

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = &nota;
```

Opções: `O endereço de nota`  `O valor 7: o ponteiro é o próprio dado`  `O nome nota`

Resposta certa: `O endereço de nota`

Se errar:

- respondeu `O valor 7: o ponteiro é o próprio dado` → O 7 está guardado em nota. O que q guarda é o endereço: o número do lugar onde nota fica. _(aponta a crença `pointer_is_data`)_
- respondeu `O nome nota` → Ponteiro não guarda nome. Guarda o endereço: o número do lugar onde nota fica.
- qualquer outro erro → q guarda o endereço de nota. O 7 fica em nota.

### Degrau 3 — guiado, completar

> Para chegar ao valor que mora no endereço guardado, usa-se o * antes do nome: *p.
> Na declaração, o * só diz que p é ponteiro. Nas outras linhas, *p vai até o lugar apontado.

**Versão 1.** Complete para mostrar o valor de idade, chegando nele pelo ponteiro.

Já está escrito:

```c
int idade;
int *p;

idade = 15;
p = &idade;
```

```c
printf("%d\n", ___);
```

Peças: `*p`  `p`  `&p`

Resposta certa: `printf("%d\n", *p);`

Se errar:

- respondeu `printf("%d\n", p);` → p, sem o *, é o endereço guardado. Para o valor que mora lá, falta o *: *p
- respondeu `printf("%d\n", &p);` → &p é o endereço do próprio ponteiro. O valor de idade se alcança com *p.
- qualquer outro erro → O valor que mora no endereço guardado é *p: printf("%d\n", *p);

**Versão 2.** Complete para mostrar o valor de nota, chegando nele pelo ponteiro.

Já está escrito:

```c
int nota;
int *q;

nota = 7;
q = &nota;
```

```c
printf("%d\n", ___);
```

Peças: `*q`  `q`  `&q`

Resposta certa: `printf("%d\n", *q);`

Se errar:

- respondeu `printf("%d\n", q);` → q, sem o *, é o endereço guardado. Para o valor que mora lá, falta o *: *q
- respondeu `printf("%d\n", &q);` → &q é o endereço do próprio ponteiro. O valor de nota se alcança com *q.
- qualquer outro erro → O valor que mora no endereço guardado é *q: printf("%d\n", *q);

### Degrau 4 — guiado, digitar

> O * também serve para escrever.
> *p = 20; guarda 20 no lugar que tem o endereço guardado em p.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int *p;

idade = 15;
p = &idade;
*p = 20;
printf("%d\n", idade);
```

Resposta certa: `20`

Se errar:

- digitou `15` → *p = 20; escreveu no lugar apontado por p, que é o lugar de idade. idade passou a guardar 20.
- qualquer outro erro → *p = 20; escreve em idade, pelo endereço. O trecho mostra 20.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int *q;

nota = 7;
q = &nota;
*q = 9;
printf("%d\n", nota);
```

Resposta certa: `9`

Se errar:

- digitou `7` → *q = 9; escreveu no lugar apontado por q, que é o lugar de nota. nota passou a guardar 9.
- qualquer outro erro → *q = 9; escreve em nota, pelo endereço. O trecho mostra 9.

### Degrau 5 — prática, digitar

_Nome do passo, no fechamento: Ler o valor pelo endereço guardado no ponteiro_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &nota;
printf("%d\n", *p);
```

Resposta certa: `7`

Se errar:

- digitou `15` → p guarda o endereço de nota, e não o de idade. *p vai até nota e acha 7.
- qualquer outro erro → p guarda o endereço de nota. *p é o valor que mora lá: 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &ano;
printf("%d\n", *q);
```

Resposta certa: `2026`

Se errar:

- digitou `3` → q guarda o endereço de ano, e não o de pontos. *q vai até ano e acha 2026.
- qualquer outro erro → q guarda o endereço de ano. *q é o valor que mora lá: 2026.

### Degrau 6 — prática, montar

**Versão 1.** Escreva 9 em nota sem usar o nome nota: vá pelo ponteiro.

Já está escrito:

```c
int nota;
int *q;

q = &nota;
```

Peças: `*q`  `=`  `9`  `;`  `q`  `&nota`

Resposta certa: `*q = 9;`

Se errar:

- respondeu `q = 9 ;` → q = 9; tentaria guardar 9 no próprio ponteiro, no lugar do endereço. Para escrever em nota, é *q = 9;
- respondeu `&nota = 9 ;` → &nota é um endereço, e não um lugar onde se escreve. Pelo ponteiro, a linha é *q = 9;
- qualquer outro erro → Para escrever no lugar apontado, o ponteiro leva o *: *q = 9;

**Versão 2.** Escreva 30 em idade sem usar o nome idade: vá pelo ponteiro.

Já está escrito:

```c
int idade;
int *p;

p = &idade;
```

Peças: `*p`  `=`  `30`  `;`  `p`  `&idade`

Resposta certa: `*p = 30;`

Se errar:

- respondeu `p = 30 ;` → p = 30; tentaria guardar 30 no próprio ponteiro, no lugar do endereço. Para escrever em idade, é *p = 30;
- respondeu `&idade = 30 ;` → &idade é um endereço, e não um lugar onde se escreve. Pelo ponteiro, a linha é *p = 30;
- qualquer outro erro → Para escrever no lugar apontado, o ponteiro leva o *: *p = 30;

### Se errar a pergunta do topo: a revisão

> O que um ponteiro guarda é um endereço: p = &idade; põe em p o endereço de idade.
> Para chegar ao valor que mora naquele endereço, usa-se o * antes do nome: *p.

```c
int idade;
int *p;

idade = 15;
p = &idade;
printf("%d\n", *p);
```

A máquina imprime:

```
15
```

### Se a pessoa disser a crença: a prova

Você disse:

> O ponteiro é o próprio dado: o que está dentro dele é o valor, não o endereço.

```c
int idade;
int *p;

idade = 15;
p = &idade;
idade = 16;
printf("%d\n", *p);
```

**Quando a linha p = &idade; rodou, idade guardava 15. Depois idade mudou para 16, e ninguém mexeu em p. O que o trecho imprime?**

- 15 _(é o que a crença espera)_
- 16 _(é o que a máquina faz)_

A máquina imprime:

```
16
```

O que isto mostra: Saiu 16. Se p guardasse o valor, teria ficado com o 15. O que p guarda é o endereço: *p foi até o lugar de idade e achou o que está lá agora.

## I1 — Então p e a caixa apontada são duas caixas diferentes, em dois lugares diferentes.

### Degrau 1 — guiado, escolher

> São duas variáveis: idade guarda um número, e p guarda o endereço de idade.
> Cada uma fica no seu lugar. Mexer numa não é mexer na outra.

**Versão 1.** O que a última linha muda?

Já está escrito:

```c
int idade;
int nota;
int *p;

p = &idade;
p = &nota;
```

Opções: `Só p: ele passa a guardar o endereço de nota`  `idade também: mexer no ponteiro é mexer na variável apontada`  `nota: ela vai para o lugar de idade`

Resposta certa: `Só p: ele passa a guardar o endereço de nota`

Se errar:

- respondeu `idade também: mexer no ponteiro é mexer na variável apontada` → p = &nota; escreve no ponteiro, e só nele. idade é outra variável, em outro lugar, e fica como estava. _(aponta a crença `pointer_and_target_are_one`)_
- respondeu `nota: ela vai para o lugar de idade` → Nenhuma variável muda de lugar. A linha escreve em p, que passa a guardar o endereço de nota.
- qualquer outro erro → A linha muda só o ponteiro: p passa a guardar o endereço de nota.

**Versão 2.** O que a última linha muda?

Já está escrito:

```c
int pontos;
int ano;
int *q;

q = &pontos;
q = &ano;
```

Opções: `Só q: ele passa a guardar o endereço de ano`  `pontos também: mexer no ponteiro é mexer na variável apontada`  `ano: ela vai para o lugar de pontos`

Resposta certa: `Só q: ele passa a guardar o endereço de ano`

Se errar:

- respondeu `pontos também: mexer no ponteiro é mexer na variável apontada` → q = &ano; escreve no ponteiro, e só nele. pontos é outra variável, em outro lugar, e fica como estava. _(aponta a crença `pointer_and_target_are_one`)_
- respondeu `ano: ela vai para o lugar de pontos` → Nenhuma variável muda de lugar. A linha escreve em q, que passa a guardar o endereço de ano.
- qualquer outro erro → A linha muda só o ponteiro: q passa a guardar o endereço de ano.

### Degrau 2 — guiado, digitar

> Com o *, é o contrário: *p = 9; não mexe no ponteiro.
> Ela escreve na variável apontada, e p continua guardando o mesmo endereço.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &nota;
*p = 9;
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `9` → *p = 9; escreveu no lugar apontado por p, que é nota, e não idade. idade continua guardando 15.
- digitou `7` → O 7 é de nota, que virou 9. O printf mostra idade, que ninguém tocou: 15.
- qualquer outro erro → p aponta para nota. *p = 9; escreveu em nota; idade continua com 15.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &ano;
*q = 2027;
printf("%d\n", pontos);
```

Resposta certa: `3`

Se errar:

- digitou `2027` → *q = 2027; escreveu no lugar apontado por q, que é ano, e não pontos. pontos continua guardando 3.
- digitou `2026` → O 2026 é de ano, que virou 2027. O printf mostra pontos, que ninguém tocou: 3.
- qualquer outro erro → q aponta para ano. *q = 2027; escreveu em ano; pontos continua com 3.

### Degrau 3 — guiado, escolher

> Sem o *, a linha mexe no ponteiro. Com o *, mexe na variável apontada.

**Versão 1.** Qual linha faz nota passar a guardar 9?

Já está escrito:

```c
int nota;
int *p;

nota = 7;
p = &nota;
```

Opções: `*p = 9;`  `p = 9;`  `&p = 9;`

Resposta certa: `*p = 9;`

Se errar:

- respondeu `p = 9;` → p = 9; tentaria trocar o endereço guardado por 9, e o compilador reclama. Para escrever em nota: *p = 9;
- respondeu `&p = 9;` → &p é o endereço do ponteiro, e não um lugar onde se escreve. Para escrever em nota: *p = 9;
- qualquer outro erro → Com o *, a linha escreve na variável apontada: *p = 9;

**Versão 2.** Qual linha faz idade passar a guardar 16?

Já está escrito:

```c
int idade;
int *q;

idade = 15;
q = &idade;
```

Opções: `*q = 16;`  `q = 16;`  `&q = 16;`

Resposta certa: `*q = 16;`

Se errar:

- respondeu `q = 16;` → q = 16; tentaria trocar o endereço guardado por 16, e o compilador reclama. Para escrever em idade: *q = 16;
- respondeu `&q = 16;` → &q é o endereço do ponteiro, e não um lugar onde se escreve. Para escrever em idade: *q = 16;
- qualquer outro erro → Com o *, a linha escreve na variável apontada: *q = 16;

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: Separar mexer no ponteiro de mexer no alvo_

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &idade;
*p = 20;
p = &nota;
printf("%d\n", idade);
```

Resposta certa: `20`

Se errar:

- digitou `15` → *p = 20; rodou enquanto p apontava para idade, e escreveu 20 nela. Depois p mudou de alvo; idade ficou com 20.
- digitou `7` → Trocar o alvo de p não copia nada para idade. Ela ficou com o 20 que *p = 20; escreveu.
- qualquer outro erro → *p = 20; escreveu em idade. Depois, p = &nota; mudou só o ponteiro. idade guarda 20.

**Versão 2.** Que número este trecho mostra na tela?

```c
int pontos;
int ano;
int *q;

pontos = 3;
ano = 2026;
q = &pontos;
*q = 8;
q = &ano;
printf("%d\n", pontos);
```

Resposta certa: `8`

Se errar:

- digitou `3` → *q = 8; rodou enquanto q apontava para pontos, e escreveu 8 nela. Depois q mudou de alvo; pontos ficou com 8.
- digitou `2026` → Trocar o alvo de q não copia nada para pontos. Ela ficou com o 8 que *q = 8; escreveu.
- qualquer outro erro → *q = 8; escreveu em pontos. Depois, q = &ano; mudou só o ponteiro. pontos guarda 8.

### Degrau 5 — prática, montar

**Versão 1.** p aponta para idade. Faça p apontar para nota, sem mexer em idade.

Já está escrito:

```c
int idade;
int nota;
int *p;

p = &idade;
```

Peças: `p`  `=`  `&nota`  `;`  `*p`  `nota`

Resposta certa: `p = &nota;`

Se errar:

- respondeu `*p = nota ;` → *p = nota; copiaria o valor de nota para dentro de idade. Para trocar o alvo do ponteiro, a linha é p = &nota;
- respondeu `p = nota ;` → nota, sem o &, é o valor guardado, e o ponteiro recebe endereço. O compilador reclama. O certo é p = &nota;
- respondeu `*p = &nota ;` → *p = &nota; tentaria guardar um endereço dentro de idade. Quem recebe o endereço é o ponteiro: p = &nota;
- qualquer outro erro → Trocar o alvo é escrever no ponteiro, sem o *: p = &nota;

**Versão 2.** q aponta para pontos. Faça q apontar para ano, sem mexer em pontos.

Já está escrito:

```c
int pontos;
int ano;
int *q;

q = &pontos;
```

Peças: `q`  `=`  `&ano`  `;`  `*q`  `ano`

Resposta certa: `q = &ano;`

Se errar:

- respondeu `*q = ano ;` → *q = ano; copiaria o valor de ano para dentro de pontos. Para trocar o alvo do ponteiro, a linha é q = &ano;
- respondeu `q = ano ;` → ano, sem o &, é o valor guardado, e o ponteiro recebe endereço. O compilador reclama. O certo é q = &ano;
- respondeu `*q = &ano ;` → *q = &ano; tentaria guardar um endereço dentro de pontos. Quem recebe o endereço é o ponteiro: q = &ano;
- qualquer outro erro → Trocar o alvo é escrever no ponteiro, sem o *: q = &ano;

### Se errar a pergunta do topo: a revisão

> O ponteiro e a variável apontada são duas variáveis, cada uma no seu lugar.
> p = &nota; muda o ponteiro. *p = 9; muda a variável apontada.

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &nota;
*p = 9;
printf("%d\n", idade);
printf("%d\n", nota);
```

A máquina imprime:

```
15
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> Mexer no ponteiro é mexer na variável apontada: os dois são a mesma coisa.

```c
int idade;
int nota;
int *p;

idade = 15;
nota = 7;
p = &idade;
p = &nota;
printf("%d\n", idade);
```

**p guardava o endereço de idade. A linha p = &nota; mexe no ponteiro. O que o trecho imprime?**

- 15 _(é o que a máquina faz)_
- 7 _(é o que a crença espera)_

A máquina imprime:

```
15
```

O que isto mostra: Saiu 15. p = &nota; mexeu só no ponteiro, que passou a guardar outro endereço. idade é outra variável, em outro lugar, e ninguém escreveu nela.

## I2 — Quem sabe o tipo de p é o compilador, que leu int *p. Por isso p não é só um número solto.

### Degrau 1 — guiado, escolher

> O tipo antes do * diz o que mora no endereço guardado.
> int *p guarda endereço de int. char *c guarda endereço de char.

**Versão 1.** Qual declaração serve para guardar o endereço de turma?

Já está escrito:

```c
char turma;
```

Opções: `char *c;`  `int *c;`  `char c;`

Resposta certa: `char *c;`

Se errar:

- respondeu `int *c;` → int *c guardaria endereço de int. turma é char, e o ponteiro dela é char *c;
- respondeu `char c;` → Sem o *, c é um char comum, e não um ponteiro. Para guardar endereço de char: char *c;
- qualquer outro erro → turma é char, e o ponteiro que guarda o endereço dela é char *c;

**Versão 2.** Qual declaração serve para guardar o endereço de idade?

Já está escrito:

```c
int idade;
```

Opções: `int *p;`  `char *p;`  `int p;`

Resposta certa: `int *p;`

Se errar:

- respondeu `char *p;` → char *p guardaria endereço de char. idade é int, e o ponteiro dela é int *p;
- respondeu `int p;` → Sem o *, p é um int comum, e não um ponteiro. Para guardar endereço de int: int *p;
- qualquer outro erro → idade é int, e o ponteiro que guarda o endereço dela é int *p;

### Degrau 2 — guiado, completar

> O endereço tem de combinar com o tipo do ponteiro.
> Um int *p recebe &idade, que é endereço de int, e não &turma, que é endereço de char.

**Versão 1.** Complete com o endereço que combina com p.

Já está escrito:

```c
int idade;
char turma;
int *p;
```

```c
p = ___;
```

Peças: `&idade`  `&turma`  `idade`

Resposta certa: `p = &idade;`

Se errar:

- respondeu `p = &turma;` → &turma é endereço de char, e p guarda endereço de int. O compilador reclama. O que combina é &idade.
- respondeu `p = idade;` → idade, sem o &, é um inteiro, e não um endereço. O compilador reclama. O certo é &idade.
- qualquer outro erro → p é int *, e recebe endereço de int: p = &idade;

**Versão 2.** Complete com o endereço que combina com c.

Já está escrito:

```c
int idade;
char turma;
char *c;
```

```c
c = ___;
```

Peças: `&turma`  `&idade`  `turma`

Resposta certa: `c = &turma;`

Se errar:

- respondeu `c = &idade;` → &idade é endereço de int, e c guarda endereço de char. O compilador reclama. O que combina é &turma.
- respondeu `c = turma;` → turma, sem o &, é um caractere, e não um endereço. O compilador reclama. O certo é &turma.
- qualquer outro erro → c é char *, e recebe endereço de char: c = &turma;

### Degrau 3 — guiado, escolher

> Um endereço não é um número inteiro comum.
> Por isso o compilador reclama de n = p; quando n é int e p é ponteiro.

**Versão 1.** Por que o compilador reclama da última linha?

Já está escrito:

```c
int idade;
int n;
int *p;

p = &idade;
n = p;
```

Opções: `Porque n é int e p é ponteiro: são tipos diferentes`  `Ele não deveria: ponteiro é só um número inteiro`  `Porque p ainda não recebeu valor`

Resposta certa: `Porque n é int e p é ponteiro: são tipos diferentes`

Se errar:

- respondeu `Ele não deveria: ponteiro é só um número inteiro` → Para o C, endereço não é inteiro comum: o ponteiro tem tipo próprio. É por isso que ele reclama de n = p; _(aponta a crença `pointer_is_integer`)_
- respondeu `Porque p ainda não recebeu valor` → p recebeu valor na linha anterior: o endereço de idade. A reclamação é de tipo: n é int, e p é ponteiro.
- qualquer outro erro → n é int e p é ponteiro. São tipos diferentes, e o compilador reclama de quem troca um pelo outro.

**Versão 2.** Por que o compilador reclama da última linha?

Já está escrito:

```c
int nota;
int n;
int *q;

q = &nota;
n = q;
```

Opções: `Porque n é int e q é ponteiro: são tipos diferentes`  `Ele não deveria: ponteiro é só um número inteiro`  `Porque q ainda não recebeu valor`

Resposta certa: `Porque n é int e q é ponteiro: são tipos diferentes`

Se errar:

- respondeu `Ele não deveria: ponteiro é só um número inteiro` → Para o C, endereço não é inteiro comum: o ponteiro tem tipo próprio. É por isso que ele reclama de n = q; _(aponta a crença `pointer_is_integer`)_
- respondeu `Porque q ainda não recebeu valor` → q recebeu valor na linha anterior: o endereço de nota. A reclamação é de tipo: n é int, e q é ponteiro.
- qualquer outro erro → n é int e q é ponteiro. São tipos diferentes, e o compilador reclama de quem troca um pelo outro.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Combinar o tipo do ponteiro com o do endereço_

**Versão 1.** Uma destas linhas faz o compilador reclamar. Qual?

Já está escrito:

```c
int idade;
char turma;
int *p;
char *c;
```

Opções: `p = &idade;`  `c = &turma;`  `p = &turma;`

Resposta certa: `p = &turma;`

Se errar:

- respondeu `p = &idade;` → Essa combina: p é int *, e &idade é endereço de int. A que não combina é p = &turma;
- respondeu `c = &turma;` → Essa combina: c é char *, e &turma é endereço de char. A que não combina é p = &turma;
- qualquer outro erro → p é int *, e &turma é endereço de char: p = &turma; não combina.

**Versão 2.** Uma destas linhas faz o compilador reclamar. Qual?

Já está escrito:

```c
int idade;
char turma;
int *p;
char *c;
```

Opções: `c = &turma;`  `c = &idade;`  `p = &idade;`

Resposta certa: `c = &idade;`

Se errar:

- respondeu `c = &turma;` → Essa combina: c é char *, e &turma é endereço de char. A que não combina é c = &idade;
- respondeu `p = &idade;` → Essa combina: p é int *, e &idade é endereço de int. A que não combina é c = &idade;
- qualquer outro erro → c é char *, e &idade é endereço de int: c = &idade; não combina.

### Degrau 5 — prática, montar

**Versão 1.** Declare o ponteiro certo para o endereço de turma, e guarde o endereço nele.

Já está escrito:

```c
char turma;
```

Peças: `char *c;`  `c = &turma;`  `int *c;`  `c = turma;`

Resposta certa: `char *c; c = &turma;`

Se errar:

- respondeu `int *c; c = &turma;` → int *c guarda endereço de int, e turma é char. O ponteiro dela é char *c;
- respondeu `char *c; c = turma;` → turma, sem o &, é o valor guardado. O ponteiro recebe o endereço: c = &turma;
- respondeu `c = &turma; char *c;` → Primeiro a declaração, depois o uso: char *c; e só então c = &turma;
- qualquer outro erro → O ponteiro de um char é char *: char *c; e depois c = &turma;

**Versão 2.** Declare o ponteiro certo para o endereço de idade, e guarde o endereço nele.

Já está escrito:

```c
int idade;
```

Peças: `int *p;`  `p = &idade;`  `char *p;`  `p = idade;`

Resposta certa: `int *p; p = &idade;`

Se errar:

- respondeu `char *p; p = &idade;` → char *p guarda endereço de char, e idade é int. O ponteiro dela é int *p;
- respondeu `int *p; p = idade;` → idade, sem o &, é o valor guardado. O ponteiro recebe o endereço: p = &idade;
- respondeu `p = &idade; int *p;` → Primeiro a declaração, depois o uso: int *p; e só então p = &idade;
- qualquer outro erro → O ponteiro de um int é int *: int *p; e depois p = &idade;

### Se errar a pergunta do topo: a revisão

> O ponteiro tem tipo: int *p guarda endereço de int, e char *c guarda endereço de char.
> Por isso um endereço não é um inteiro comum: o compilador reclama de quem troca um pelo outro.

```c
int idade;
char turma;
int *p;
char *c;

p = &idade;
c = &turma;
```

### Se a pessoa disser a crença: a prova

Você disse:

> Ponteiro é só um número inteiro; dá para trocar um pelo outro.

```c
int idade;
int *p;

p = &idade;
p = 1000;
```

**O compilador reclama da última linha?**

- Não: endereço é um número, e 1000 é um número _(é o que a crença espera)_
- Sim: ele não aceita um inteiro comum no lugar do endereço _(é o que a máquina faz)_

O compilador reclama:

```
makes pointer from integer without a cast
```

_Mensagem do gcc 16.2. Todo compilador de C tem de reclamar desta linha, cada um com as suas palavras._

O que isto mostra: O compilador reclama: p guarda endereço de int, e 1000 é um inteiro comum. Para o C são tipos diferentes — o ponteiro não é um número solto.

## I3 — Com o endereço na mão, dá para chegar naquela caixa de qualquer ponto do programa, sem copiar o conteúdo.

### Degrau 1 — guiado, digitar

> Uma função é um trecho com nome, que roda quando é chamado: zera(idade);
> O que vai nos parênteses chega à função como cópia. Ela mexe na cópia, e não na variável de fora.

**Versão 1.** A primeira linha é a função: void diz que ela não devolve nada, e int v é a cópia que ela recebe. Que número este trecho mostra na tela?

```c
void zera(int v) { v = 0; }

int idade;

idade = 15;
zera(idade);
printf("%d\n", idade);
```

Resposta certa: `15`

Se errar:

- digitou `0` → A função recebeu uma cópia do 15 e zerou a cópia. idade, a variável de fora, continua com 15.
- qualquer outro erro → zera(idade); entrega uma cópia do valor. A função zera a cópia, e idade continua com 15.

**Versão 2.** A primeira linha é a função: void diz que ela não devolve nada, e int v é a cópia que ela recebe. Que número este trecho mostra na tela?

```c
void zera(int v) { v = 0; }

int pontos;

pontos = 3;
zera(pontos);
printf("%d\n", pontos);
```

Resposta certa: `3`

Se errar:

- digitou `0` → A função recebeu uma cópia do 3 e zerou a cópia. pontos, a variável de fora, continua com 3.
- qualquer outro erro → zera(pontos); entrega uma cópia do valor. A função zera a cópia, e pontos continua com 3.

### Degrau 2 — guiado, completar

> Para mexer na variável de fora, a função precisa do endereço dela.
> Na chamada vai &idade. Na função, quem recebe é um ponteiro: int *q.

**Versão 1.** Complete a chamada para a função receber o endereço de idade.

Já está escrito:

```c
void zera(int *q) { *q = 0; }

int idade;

idade = 15;
```

```c
zera(___);
```

Peças: `&idade`  `idade`  `*idade`

Resposta certa: `zera(&idade);`

Se errar:

- respondeu `zera(idade);` → idade, sem o &, entrega uma cópia do valor, e a função espera um endereço. O compilador reclama. O certo é zera(&idade);
- respondeu `zera(*idade);` → O * serve a ponteiro, e idade não é um. O endereço dela se pede com o &: zera(&idade);
- qualquer outro erro → A função espera um endereço, e o de idade é &idade: zera(&idade);

**Versão 2.** Complete a chamada para a função receber o endereço de pontos.

Já está escrito:

```c
void zera(int *q) { *q = 0; }

int pontos;

pontos = 3;
```

```c
zera(___);
```

Peças: `&pontos`  `pontos`  `*pontos`

Resposta certa: `zera(&pontos);`

Se errar:

- respondeu `zera(pontos);` → pontos, sem o &, entrega uma cópia do valor, e a função espera um endereço. O compilador reclama. O certo é zera(&pontos);
- respondeu `zera(*pontos);` → O * serve a ponteiro, e pontos não é um. O endereço dela se pede com o &: zera(&pontos);
- qualquer outro erro → A função espera um endereço, e o de pontos é &pontos: zera(&pontos);

### Degrau 3 — guiado, digitar

> Com o endereço na mão, a função escreve direto na variável de fora.
> Dentro dela, *q = 0; vai até o lugar de idade e guarda 0.

**Versão 1.** Que número este trecho mostra na tela?

```c
void zera(int *q) { *q = 0; }

int idade;

idade = 15;
zera(&idade);
printf("%d\n", idade);
```

Resposta certa: `0`

Se errar:

- digitou `15` → Desta vez a função recebeu o endereço de idade. *q = 0; foi até lá e escreveu: idade passou a guardar 0.
- qualquer outro erro → A função recebeu o endereço e escreveu na própria idade. O trecho mostra 0.

**Versão 2.** Que número este trecho mostra na tela?

```c
void zera(int *q) { *q = 0; }

int pontos;

pontos = 3;
zera(&pontos);
printf("%d\n", pontos);
```

Resposta certa: `0`

Se errar:

- digitou `3` → Desta vez a função recebeu o endereço de pontos. *q = 0; foi até lá e escreveu: pontos passou a guardar 0.
- qualquer outro erro → A função recebeu o endereço e escreveu na própria pontos. O trecho mostra 0.

### Degrau 4 — guiado, escolher

> É isso que o ponteiro dá, e a variável comum não: alcançar a mesma variável de outro ponto do programa.
> Só o endereço viaja. O conteúdo não é copiado.

**Versão 1.** Por que esta função recebe um ponteiro, e não um int comum?

Já está escrito:

```c
void zera(int *q) { *q = 0; }
```

Opções: `Para chegar na variável de fora e escrever nela`  `Por nada: é só um jeito complicado de fazer o que um int comum faz`  `Porque função só aceita ponteiro`

Resposta certa: `Para chegar na variável de fora e escrever nela`

Se errar:

- respondeu `Por nada: é só um jeito complicado de fazer o que um int comum faz` → Com um int comum a função recebe uma cópia, e a variável de fora não muda. Com o ponteiro ela chega lá e escreve. _(aponta a crença `pointer_is_pointless`)_
- respondeu `Porque função só aceita ponteiro` → Função aceita int comum também, e aí recebe uma cópia. O ponteiro é para chegar na variável de fora.
- qualquer outro erro → Com o endereço, a função alcança a variável de fora e escreve nela.

**Versão 2.** Por que esta função recebe um ponteiro, e não um int comum?

Já está escrito:

```c
void dobra(int *q) { *q = *q + *q; }
```

Opções: `Para chegar na variável de fora e escrever nela`  `Por nada: é só um jeito complicado de fazer o que um int comum faz`  `Porque função só aceita ponteiro`

Resposta certa: `Para chegar na variável de fora e escrever nela`

Se errar:

- respondeu `Por nada: é só um jeito complicado de fazer o que um int comum faz` → Com um int comum a função recebe uma cópia, e a variável de fora não muda. Com o ponteiro ela chega lá e escreve. _(aponta a crença `pointer_is_pointless`)_
- respondeu `Porque função só aceita ponteiro` → Função aceita int comum também, e aí recebe uma cópia. O ponteiro é para chegar na variável de fora.
- qualquer outro erro → Com o endereço, a função alcança a variável de fora e escreve nela.

### Degrau 5 — prática, digitar

_Nome do passo, no fechamento: Saber qual variável a função alcança pelo endereço_

**Versão 1.** Que número este trecho mostra na tela?

```c
void marca(int *q) { *q = 9; }

int nota;
int pontos;

nota = 7;
pontos = 3;
marca(&pontos);
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `9` → A função recebeu o endereço de pontos, e escreveu lá. nota não foi tocada: continua com 7.
- digitou `3` → O 3 era de pontos, que virou 9. O printf mostra nota, que ninguém tocou: 7.
- qualquer outro erro → A função escreve no lugar cujo endereço recebeu: pontos. nota continua com 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
void marca(int *q) { *q = 9; }

int idade;
int ano;

idade = 15;
ano = 2026;
marca(&idade);
printf("%d\n", ano);
```

Resposta certa: `2026`

Se errar:

- digitou `9` → A função recebeu o endereço de idade, e escreveu lá. ano não foi tocada: continua com 2026.
- digitou `15` → O 15 era de idade, que virou 9. O printf mostra ano, que ninguém tocou: 2026.
- qualquer outro erro → A função escreve no lugar cujo endereço recebeu: idade. ano continua com 2026.

### Degrau 6 — prática, montar

**Versão 1.** Chame a função para que ela zere nota.

Já está escrito:

```c
void zera(int *q) { *q = 0; }

int nota;

nota = 7;
```

Peças: `zera(`  `&nota`  `);`  `nota`  `*nota`

Resposta certa: `zera(&nota);`

Se errar:

- respondeu `zera( nota );` → nota, sem o &, entrega uma cópia do 7, e a função espera um endereço. O compilador reclama. O certo é zera(&nota);
- respondeu `zera( *nota );` → O * serve a ponteiro, e nota não é um. O endereço dela se pede com o &: zera(&nota);
- qualquer outro erro → A função espera o endereço da variável que vai mudar: zera(&nota);

**Versão 2.** Chame a função para que ela zere ano.

Já está escrito:

```c
void zera(int *q) { *q = 0; }

int ano;

ano = 2026;
```

Peças: `zera(`  `&ano`  `);`  `ano`  `*ano`

Resposta certa: `zera(&ano);`

Se errar:

- respondeu `zera( ano );` → ano, sem o &, entrega uma cópia do 2026, e a função espera um endereço. O compilador reclama. O certo é zera(&ano);
- respondeu `zera( *ano );` → O * serve a ponteiro, e ano não é um. O endereço dela se pede com o &: zera(&ano);
- qualquer outro erro → A função espera o endereço da variável que vai mudar: zera(&ano);

### Se errar a pergunta do topo: a revisão

> Uma função recebe cópias: mexer na cópia não muda a variável de fora.
> Recebendo o endereço, a função chega na própria variável e escreve nela.

```c
void zera(int *q) { *q = 0; }

int idade;

idade = 15;
zera(&idade);
printf("%d\n", idade);
```

A máquina imprime:

```
0
```

### Se a pessoa disser a crença: a prova

Você disse:

> Ponteiro é um jeito complicado de fazer o que uma variável comum já faz.

```c
void zera(int v) { v = 0; }

int nota;

nota = 7;
zera(nota);
printf("%d\n", nota);
```

**A função zera recebe uma variável comum, e não um ponteiro, e escreve 0 nela. O que o trecho imprime?**

- 0 _(é o que a crença espera)_
- 7 _(é o que a máquina faz)_

A máquina imprime:

```
7
```

O que isto mostra: Saiu 7. A função recebeu uma cópia do valor e zerou a cópia; a variável de fora ficou como estava. Com uma variável comum ela não alcança nota. Com o endereço, alcança — e isso só o ponteiro faz.
