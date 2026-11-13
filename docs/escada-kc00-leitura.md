# A escada do kc_00 — Declaração de variáveis

Texto para leitura, gerado de `mvp/dominio/escada_kc00.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — Toda variável tem um nome e um tipo — o tipo diz que espécie de valor cabe ali.

### Degrau 1 — guiado, tocar

> Para guardar um valor, o programa pede ao C uma variável.
> O pedido tem três partes: o tipo, o nome e um ponto e vírgula no fim.

**Versão 1.** Toque no nome da variável.

```c
int idade;
```

Peças: `int`  `idade`  `;`

Resposta certa: `idade`

Se errar:

- respondeu `int` → int é o tipo: diz que ali vai um número inteiro. O nome é a palavra que você escolhe: idade.
- respondeu `;` → O ponto e vírgula só fecha a linha. O nome é a palavra que você escolhe: idade.
- qualquer outro erro → O nome é a palavra do meio, a que você escolhe: idade.

**Versão 2.** Toque no nome da variável.

```c
int ano;
```

Peças: `int`  `ano`  `;`

Resposta certa: `ano`

Se errar:

- respondeu `int` → int é o tipo: diz que ali vai um número inteiro. O nome é a palavra que você escolhe: ano.
- respondeu `;` → O ponto e vírgula só fecha a linha. O nome é a palavra que você escolhe: ano.
- qualquer outro erro → O nome é a palavra do meio, a que você escolhe: ano.

### Degrau 2 — guiado, montar

> Agora é você quem escreve o pedido.
> A ordem é sempre a mesma: primeiro o tipo, depois o nome, e o ponto e vírgula fecha.

**Versão 1.** Declare uma variável inteira chamada nota.

Peças: `int`  `nota`  `;`  `idade`

Resposta certa: `int nota;`

Se errar:

- respondeu `nota int ;` → Em C o tipo vem primeiro e o nome depois: int nota;
- respondeu `int idade ;` → Essa linha declara idade. O nome pedido era nota: int nota;
- não usou `;` → Faltou o ponto e vírgula. Toda declaração termina com ele: int nota;
- qualquer outro erro → A declaração é o tipo, o nome e o ponto e vírgula: int nota;

**Versão 2.** Declare uma variável inteira chamada ano.

Peças: `int`  `ano`  `;`  `nota`

Resposta certa: `int ano;`

Se errar:

- respondeu `ano int ;` → Em C o tipo vem primeiro e o nome depois: int ano;
- respondeu `int nota ;` → Essa linha declara nota. O nome pedido era ano: int ano;
- não usou `;` → Faltou o ponto e vírgula. Toda declaração termina com ele: int ano;
- qualquer outro erro → A declaração é o tipo, o nome e o ponto e vírgula: int ano;

### Degrau 3 — guiado, escolher

> O tipo diz que espécie de valor cabe na variável.
> int guarda um número inteiro, como 20. char guarda um caractere, como 'B'.

**Versão 1.** Qual declaração serve para guardar a letra de uma turma, como 'B'?

Opções: `char turma;`  `int turma;`  `Tanto faz: o tipo é só um aviso`

Resposta certa: `char turma;`

Se errar:

- respondeu `int turma;` → int é para número inteiro. Uma letra pede char: char turma;
- respondeu `Tanto faz: o tipo é só um aviso` → O tipo não é só um aviso: é ele que decide o que cabe na variável. Uma letra pede char: char turma; _(aponta a crença `type_is_a_hint`)_
- qualquer outro erro → Para guardar uma letra, o tipo é char: char turma;

**Versão 2.** Qual declaração serve para guardar a idade de uma pessoa, como 20?

Opções: `int idade;`  `char idade;`  `Tanto faz: o tipo é só um aviso`

Resposta certa: `int idade;`

Se errar:

- respondeu `char idade;` → char é para um caractere, como uma letra. Um número inteiro pede int: int idade;
- respondeu `Tanto faz: o tipo é só um aviso` → O tipo não é só um aviso: é ele que decide o que cabe na variável. Um número inteiro pede int: int idade; _(aponta a crença `type_is_a_hint`)_
- qualquer outro erro → Para guardar um número inteiro, o tipo é int: int idade;

### Degrau 4 — prática, montar

**Versão 1.** Declare duas variáveis: um inteiro chamado idade e um caractere chamado turma.

Peças: `int`  `idade;`  `char`  `turma;`

Resposta certa: `int idade; ⏎ char turma;`

Se errar:

- respondeu `char idade; int turma;` → Os tipos ficaram trocados: idade é um número inteiro (int) e turma é uma letra (char).
- respondeu `int turma; char idade;` → Os tipos ficaram trocados: idade é um número inteiro (int) e turma é uma letra (char).
- respondeu `idade; int turma; char` → O tipo vem antes do nome, nas duas declarações: int idade; char turma;
- qualquer outro erro → São duas declarações, cada uma com o tipo antes do nome: int idade; char turma;

**Versão 2.** Declare duas variáveis: um inteiro chamado ano e um caractere chamado inicial.

Peças: `int`  `ano;`  `char`  `inicial;`

Resposta certa: `int ano; ⏎ char inicial;`

Se errar:

- respondeu `char ano; int inicial;` → Os tipos ficaram trocados: ano é um número inteiro (int) e inicial é uma letra (char).
- respondeu `int inicial; char ano;` → Os tipos ficaram trocados: ano é um número inteiro (int) e inicial é uma letra (char).
- respondeu `ano; int inicial; char` → O tipo vem antes do nome, nas duas declarações: int ano; char inicial;
- qualquer outro erro → São duas declarações, cada uma com o tipo antes do nome: int ano; char inicial;

### Degrau 5 — prática, escolher

**Versão 1.** Uma destas linhas não é uma declaração válida. Qual?

Opções: `int idade;`  `idade int;`  `char turma;`

Resposta certa: `idade int;`

Se errar:

- respondeu `int idade;` → Essa é válida: tem o tipo, o nome e o ponto e vírgula, nessa ordem.
- respondeu `char turma;` → Essa é válida: char é o tipo e turma é o nome.
- qualquer outro erro → A inválida é a que põe o nome antes do tipo: idade int;

**Versão 2.** Uma destas linhas não é uma declaração válida. Qual?

Opções: `char inicial;`  `inicial char;`  `int ano;`

Resposta certa: `inicial char;`

Se errar:

- respondeu `char inicial;` → Essa é válida: char é o tipo e inicial é o nome.
- respondeu `int ano;` → Essa é válida: tem o tipo, o nome e o ponto e vírgula, nessa ordem.
- qualquer outro erro → A inválida é a que põe o nome antes do tipo: inicial char;

### Se errar a pergunta do topo: a revisão

> Toda declaração tem o tipo, o nome e o ponto e vírgula, nessa ordem.
> O tipo decide o que cabe: int para número inteiro, char para um caractere.

```c
int idade;
char turma;
```

## B2 — Quando você escreve int x;, a caixa de x já existe — só o que tem dentro ainda não está definido.

### Degrau 1 — guiado, montar

> Uma variável declarada já pode receber um valor.
> Para guardar, escreva o nome, o sinal de igual, o valor e o ponto e vírgula.

**Versão 1.** Guarde 20 em idade.

Já está escrito:

```c
int idade;
```

Peças: `idade`  `=`  `20`  `;`  `int`

Resposta certa: `idade = 20;`

Se errar:

- respondeu `int idade = 20 ;` → idade já foi declarada na linha de cima. Declarar de novo é pedir outra variável com o mesmo nome, e o compilador reclama. Basta idade = 20;
- respondeu `20 = idade ;` → A variável que recebe fica antes do sinal de igual, e o valor depois: idade = 20;
- não usou `;` → Faltou o ponto e vírgula no fim da linha: idade = 20;
- qualquer outro erro → A linha é o nome, o sinal de igual, o valor e o ponto e vírgula: idade = 20;

**Versão 2.** Guarde 2026 em ano.

Já está escrito:

```c
int ano;
```

Peças: `ano`  `=`  `2026`  `;`  `int`

Resposta certa: `ano = 2026;`

Se errar:

- respondeu `int ano = 2026 ;` → ano já foi declarada na linha de cima. Declarar de novo é pedir outra variável com o mesmo nome, e o compilador reclama. Basta ano = 2026;
- respondeu `2026 = ano ;` → A variável que recebe fica antes do sinal de igual, e o valor depois: ano = 2026;
- não usou `;` → Faltou o ponto e vírgula no fim da linha: ano = 2026;
- qualquer outro erro → A linha é o nome, o sinal de igual, o valor e o ponto e vírgula: ano = 2026;

### Degrau 2 — guiado, escolher

> Repare: você escreveu na variável sem declarar de novo.
> Ela existe desde a linha da declaração, mesmo antes de receber qualquer valor.

**Versão 1.** Logo depois de int idade; e antes de qualquer valor, a variável idade já existe?

Opções: `Sim: a declaração já reservou o lugar dela`  `Não: ela só existe depois de receber um valor`

Resposta certa: `Sim: a declaração já reservou o lugar dela`

Se errar:

- respondeu `Não: ela só existe depois de receber um valor` → Ela já existe. Quem reserva o lugar é a declaração; o valor entra depois, num lugar que já está lá. _(aponta a crença `no_value_no_memory`)_
- qualquer outro erro → A variável existe desde a declaração; o valor só vem depois.

**Versão 2.** Logo depois de char turma; e antes de qualquer valor, a variável turma já existe?

Opções: `Sim: a declaração já reservou o lugar dela`  `Não: ela só existe depois de receber um valor`

Resposta certa: `Sim: a declaração já reservou o lugar dela`

Se errar:

- respondeu `Não: ela só existe depois de receber um valor` → Ela já existe. Quem reserva o lugar é a declaração; o valor entra depois, num lugar que já está lá. _(aponta a crença `no_value_no_memory`)_
- qualquer outro erro → A variável existe desde a declaração; o valor só vem depois.

### Degrau 3 — guiado, completar

> Só dá para guardar valor numa variável que já foi declarada.

**Versão 1.** Complete com a variável que já existe.

Já está escrito:

```c
int nota;
```

```c
___ = 7;
```

Peças: `nota`  `idade`  `int`

Resposta certa: `nota = 7;`

Se errar:

- respondeu `idade = 7;` → idade não foi declarada neste trecho. A variável que existe aqui é nota: nota = 7;
- respondeu `int = 7;` → int é um tipo, não uma variável. Quem recebe o valor é nota: nota = 7;
- qualquer outro erro → A variável declarada neste trecho é nota: nota = 7;

**Versão 2.** Complete com a variável que já existe.

Já está escrito:

```c
int pontos;
```

```c
___ = 10;
```

Peças: `pontos`  `nota`  `int`

Resposta certa: `pontos = 10;`

Se errar:

- respondeu `nota = 10;` → nota não foi declarada neste trecho. A variável que existe aqui é pontos: pontos = 10;
- respondeu `int = 10;` → int é um tipo, não uma variável. Quem recebe o valor é pontos: pontos = 10;
- qualquer outro erro → A variável declarada neste trecho é pontos: pontos = 10;

### Degrau 4 — prática, montar

**Versão 1.** Monte o trecho: declare um inteiro chamado nota e depois guarde 7 nele.

Peças: `int nota;`  `nota = 7;`  `idade = 7;`

Resposta certa: `int nota; ⏎ nota = 7;`

Se errar:

- respondeu `nota = 7; int nota;` → A declaração vem primeiro: antes dela a variável não existe, e não há onde guardar o 7.
- respondeu `int nota; idade = 7;` → idade não foi declarada neste trecho. A variável que existe é nota: nota = 7;
- não usou `int nota;` → Faltou declarar. Sem int nota; a variável não existe.
- qualquer outro erro → Primeiro a declaração, depois o valor: int nota; e então nota = 7;

**Versão 2.** Monte o trecho: declare um inteiro chamado pontos e depois guarde 10 nele.

Peças: `int pontos;`  `pontos = 10;`  `nota = 10;`

Resposta certa: `int pontos; ⏎ pontos = 10;`

Se errar:

- respondeu `pontos = 10; int pontos;` → A declaração vem primeiro: antes dela a variável não existe, e não há onde guardar o 10.
- respondeu `int pontos; nota = 10;` → nota não foi declarada neste trecho. A variável que existe é pontos: pontos = 10;
- não usou `int pontos;` → Faltou declarar. Sem int pontos; a variável não existe.
- qualquer outro erro → Primeiro a declaração, depois o valor: int pontos; e então pontos = 10;

### Degrau 5 — prática, escolher

**Versão 1.** Um destes trechos usa uma variável que não foi declarada. Qual?

Opção 1:

```c
int idade;
idade = 20;
```

Opção 2:

```c
nota = 7;
```

Opção 3:

```c
int ano;
ano = 2026;
```

Resposta certa: `nota = 7;`

Se errar:

- respondeu `int idade;
idade = 20;` → Aqui idade foi declarada na primeira linha, então já existe quando recebe o 20.
- respondeu `int ano;
ano = 2026;` → Aqui ano foi declarada na primeira linha, então já existe quando recebe o valor.
- qualquer outro erro → O trecho sem declaração é nota = 7; — ali a variável nota não existe.

**Versão 2.** Um destes trechos usa uma variável que não foi declarada. Qual?

Opção 1:

```c
int pontos;
pontos = 10;
```

Opção 2:

```c
int nota;
nota = 7;
```

Opção 3:

```c
turma = 'B';
```

Resposta certa: `turma = 'B';`

Se errar:

- respondeu `int pontos;
pontos = 10;` → Aqui pontos foi declarada na primeira linha, então já existe quando recebe o 10.
- respondeu `int nota;
nota = 7;` → Aqui nota foi declarada na primeira linha, então já existe quando recebe o 7.
- qualquer outro erro → O trecho sem declaração é turma = 'B'; — ali a variável turma não existe.

### Se errar a pergunta do topo: a revisão

> A declaração reserva o lugar: a partir dela a variável existe.
> O valor é outra coisa: só entra quando uma linha escreve nele.

```c
int idade;
idade = 20;
```

## B3 — C não limpa a caixa para você. O que estava lá antes continua lá até você escrever algo.

### Degrau 1 — guiado, completar

> Para ver o que uma variável guarda, o programa usa printf.
> Em printf("%d\n", idade); o %d marca onde o número aparece, e idade é a variável lida.

**Versão 1.** Complete para mostrar o valor de idade.

Já está escrito:

```c
int idade;
idade = 20;
```

```c
printf("%d\n", ___);
```

Peças: `idade`  `int`  `20`

Resposta certa: `printf("%d\n", idade);`

Se errar:

- respondeu `printf("%d\n", int);` → int é o tipo. Depois da vírgula vai a variável que você quer ler: idade.
- respondeu `printf("%d\n", 20);` → Assim o programa mostraria o número 20 escrito à mão, e não o que está guardado. Para ler a variável, use o nome: idade.
- qualquer outro erro → Depois da vírgula vai o nome da variável que você quer ler: idade.

**Versão 2.** Complete para mostrar o valor de nota.

Já está escrito:

```c
int nota;
nota = 7;
```

```c
printf("%d\n", ___);
```

Peças: `nota`  `int`  `7`

Resposta certa: `printf("%d\n", nota);`

Se errar:

- respondeu `printf("%d\n", int);` → int é o tipo. Depois da vírgula vai a variável que você quer ler: nota.
- respondeu `printf("%d\n", 7);` → Assim o programa mostraria o número 7 escrito à mão, e não o que está guardado. Para ler a variável, use o nome: nota.
- qualquer outro erro → Depois da vírgula vai o nome da variável que você quer ler: nota.

### Degrau 2 — guiado, escolher

> Declarar reserva o lugar, mas não escreve nada nele.
> O C não põe zero para você: logo depois de int idade; ninguém sabe o que há ali.

**Versão 1.** Logo depois de int idade; que valor está guardado em idade?

Opções: `Não dá para saber: ninguém escreveu nada ali`  `0: declarar já zera a variável`

Resposta certa: `Não dá para saber: ninguém escreveu nada ali`

Se errar:

- respondeu `0: declarar já zera a variável` → O C não zera a variável. A declaração só reserva o lugar, e o valor só passa a ser conhecido quando uma linha escreve nele. _(aponta a crença `declaration_zeroes`)_
- qualquer outro erro → Sem ninguém ter escrito, o valor não é conhecido.

**Versão 2.** Logo depois de int nota; que valor está guardado em nota?

Opções: `Não dá para saber: ninguém escreveu nada ali`  `0: declarar já zera a variável`

Resposta certa: `Não dá para saber: ninguém escreveu nada ali`

Se errar:

- respondeu `0: declarar já zera a variável` → O C não zera a variável. A declaração só reserva o lugar, e o valor só passa a ser conhecido quando uma linha escreve nele. _(aponta a crença `declaration_zeroes`)_
- qualquer outro erro → Sem ninguém ter escrito, o valor não é conhecido.

### Degrau 3 — guiado, escolher

> Por isso a regra é: escreva na variável antes de ler.

**Versão 1.** Qual trecho escreve em idade antes de ler?

Opção 1:

```c
int idade;
idade = 20;
printf("%d\n", idade);
```

Opção 2:

```c
int idade;
printf("%d\n", idade);
idade = 20;
```

Resposta certa: `int idade; ⏎ idade = 20; ⏎ printf("%d\n", idade);`

Se errar:

- respondeu `int idade;
printf("%d\n", idade);
idade = 20;` → Aqui o printf vem antes de idade = 20; — ele lê a variável quando ninguém escreveu nela ainda.
- qualquer outro erro → O trecho certo é o que tem idade = 20; antes do printf.

**Versão 2.** Qual trecho escreve em nota antes de ler?

Opção 1:

```c
int nota;
nota = 7;
printf("%d\n", nota);
```

Opção 2:

```c
int nota;
printf("%d\n", nota);
nota = 7;
```

Resposta certa: `int nota; ⏎ nota = 7; ⏎ printf("%d\n", nota);`

Se errar:

- respondeu `int nota;
printf("%d\n", nota);
nota = 7;` → Aqui o printf vem antes de nota = 7; — ele lê a variável quando ninguém escreveu nela ainda.
- qualquer outro erro → O trecho certo é o que tem nota = 7; antes do printf.

### Degrau 4 — prática, montar

**Versão 1.** Ponha as linhas em ordem, para que nota tenha valor quando for lida.

Peças: `int nota;`  `nota = 7;`  `printf("%d\n", nota);`

Resposta certa: `int nota; ⏎ nota = 7; ⏎ printf("%d\n", nota);`

Se errar:

- respondeu `int nota; printf("%d\n", nota); nota = 7;` → Assim o printf lê nota antes de ela receber o 7, e o que aparece não é confiável. A escrita vem antes da leitura.
- respondeu `nota = 7; int nota; printf("%d\n", nota);` → A declaração vem primeiro: antes dela a variável não existe.
- não usou `nota = 7;` → Faltou escrever o valor. Sem nota = 7; o printf lê uma variável em que ninguém escreveu.
- qualquer outro erro → A ordem é declarar, escrever e só então ler: int nota; nota = 7; e o printf.

**Versão 2.** Ponha as linhas em ordem, para que pontos tenha valor quando for lida.

Peças: `int pontos;`  `pontos = 10;`  `printf("%d\n", pontos);`

Resposta certa: `int pontos; ⏎ pontos = 10; ⏎ printf("%d\n", pontos);`

Se errar:

- respondeu `int pontos; printf("%d\n", pontos); pontos = 10;` → Assim o printf lê pontos antes de ela receber o 10, e o que aparece não é confiável. A escrita vem antes da leitura.
- respondeu `pontos = 10; int pontos; printf("%d\n", pontos);` → A declaração vem primeiro: antes dela a variável não existe.
- não usou `pontos = 10;` → Faltou escrever o valor. Sem pontos = 10; o printf lê uma variável em que ninguém escreveu.
- qualquer outro erro → A ordem é declarar, escrever e só então ler: int pontos; pontos = 10; e o printf.

### Degrau 5 — prática, escolher

**Versão 1.** Qual trecho lê uma variável em que ninguém escreveu ainda?

Opção 1:

```c
int pontos;
pontos = 10;
printf("%d\n", pontos);
```

Opção 2:

```c
int pontos;
printf("%d\n", pontos);
```

Opção 3:

```c
int pontos;
pontos = 10;
pontos = 12;
printf("%d\n", pontos);
```

Resposta certa: `int pontos; ⏎ printf("%d\n", pontos);`

Se errar:

- respondeu `int pontos;
pontos = 10;
printf("%d\n", pontos);` → Aqui pontos recebe 10 antes do printf, então a leitura é segura.
- respondeu `int pontos;
pontos = 10;
pontos = 12;
printf("%d\n", pontos);` → Aqui pontos recebe valor duas vezes antes do printf, então a leitura é segura.
- qualquer outro erro → É o trecho em que o printf vem logo depois da declaração, sem nenhuma escrita antes.

**Versão 2.** Qual trecho lê uma variável em que ninguém escreveu ainda?

Opção 1:

```c
int idade;
idade = 20;
idade = 21;
printf("%d\n", idade);
```

Opção 2:

```c
int idade;
idade = 20;
printf("%d\n", idade);
```

Opção 3:

```c
int idade;
printf("%d\n", idade);
```

Resposta certa: `int idade; ⏎ printf("%d\n", idade);`

Se errar:

- respondeu `int idade;
idade = 20;
idade = 21;
printf("%d\n", idade);` → Aqui idade recebe valor duas vezes antes do printf, então a leitura é segura.
- respondeu `int idade;
idade = 20;
printf("%d\n", idade);` → Aqui idade recebe 20 antes do printf, então a leitura é segura.
- qualquer outro erro → É o trecho em que o printf vem logo depois da declaração, sem nenhuma escrita antes.

### Se errar a pergunta do topo: a revisão

> O C não escreve nada na variável quando você declara.
> Por isso o programa escreve antes de ler: primeiro idade = 20; e só depois o printf.

```c
int idade;
idade = 20;
printf("%d\n", idade);
```

A máquina imprime:

```
20
```

## B4 — Escrever um valor novo apaga o antigo. A caixa nunca guarda dois valores ao mesmo tempo.

### Degrau 1 — guiado, digitar

> Uma variável guarda um valor só.
> Quando uma linha escreve um valor novo, ele entra no lugar do antigo.

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
idade = 20;
idade = 21;
printf("%d\n", idade);
```

Resposta certa: `21`

Se errar:

- digitou `20` → O 20 foi apagado quando o 21 entrou. Vale o último valor escrito: 21.
- digitou `41` → Os valores não se somam: o 21 entra no lugar do 20. Vale o último valor escrito: 21.
- qualquer outro erro → A variável fica com o último valor escrito nela: 21.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
nota = 7;
nota = 9;
printf("%d\n", nota);
```

Resposta certa: `9`

Se errar:

- digitou `7` → O 7 foi apagado quando o 9 entrou. Vale o último valor escrito: 9.
- digitou `16` → Os valores não se somam: o 9 entra no lugar do 7. Vale o último valor escrito: 9.
- qualquer outro erro → A variável fica com o último valor escrito nela: 9.

### Degrau 2 — guiado, escolher

> O valor antigo não fica guardado em outro canto da variável.
> Depois de idade = 21; não existe mais 20 nenhum ali.

**Versão 1.** Depois de idade = 20; e idade = 21; onde ficou o 20?

Opções: `Em lugar nenhum: foi apagado`  `Continua guardado, junto com o 21`

Resposta certa: `Em lugar nenhum: foi apagado`

Se errar:

- respondeu `Continua guardado, junto com o 21` → A variável não lembra os valores antigos. Ela guarda um só, e o 21 entrou no lugar do 20. _(aponta a crença `variable_remembers`)_
- qualquer outro erro → O valor antigo é apagado quando o novo entra.

**Versão 2.** Depois de nota = 7; e nota = 9; onde ficou o 7?

Opções: `Em lugar nenhum: foi apagado`  `Continua guardado, junto com o 9`

Resposta certa: `Em lugar nenhum: foi apagado`

Se errar:

- respondeu `Continua guardado, junto com o 9` → A variável não lembra os valores antigos. Ela guarda um só, e o 9 entrou no lugar do 7. _(aponta a crença `variable_remembers`)_
- qualquer outro erro → O valor antigo é apagado quando o novo entra.

### Degrau 3 — guiado, montar

> Para trocar o valor, basta escrever de novo no mesmo nome.

**Versão 1.** A turma mudou de 'A' para 'B'. Escreva a linha que troca o valor.

Já está escrito:

```c
char turma;
turma = 'A';
```

Peças: `turma`  `=`  `'B'`  `;`  `char`

Resposta certa: `turma = 'B';`

Se errar:

- respondeu `char turma = 'B' ;` → turma já existe. Para trocar o valor não se declara de novo, só se escreve: turma = 'B';
- não usou `;` → Faltou o ponto e vírgula no fim da linha: turma = 'B';
- qualquer outro erro → Trocar o valor é escrever de novo no mesmo nome: turma = 'B';

**Versão 2.** A nota subiu de 7 para 9. Escreva a linha que troca o valor.

Já está escrito:

```c
int nota;
nota = 7;
```

Peças: `nota`  `=`  `9`  `;`  `int`

Resposta certa: `nota = 9;`

Se errar:

- respondeu `int nota = 9 ;` → nota já existe. Para trocar o valor não se declara de novo, só se escreve: nota = 9;
- não usou `;` → Faltou o ponto e vírgula no fim da linha: nota = 9;
- qualquer outro erro → Trocar o valor é escrever de novo no mesmo nome: nota = 9;

### Degrau 4 — prática, digitar

**Versão 1.** Que número este trecho mostra na tela?

```c
int pontos;
pontos = 3;
pontos = 5;
pontos = 8;
printf("%d\n", pontos);
```

Resposta certa: `8`

Se errar:

- digitou `3` → O 3 foi o primeiro valor, e já foi apagado. Vale o último escrito: 8.
- digitou `5` → O 5 foi apagado quando o 8 entrou. Vale o último escrito: 8.
- digitou `16` → Os valores não se somam: cada escrita apaga a anterior. Vale o último: 8.
- qualquer outro erro → Vale o último valor escrito na variável: 8.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
idade = 18;
idade = 19;
idade = 20;
printf("%d\n", idade);
```

Resposta certa: `20`

Se errar:

- digitou `18` → O 18 foi o primeiro valor, e já foi apagado. Vale o último escrito: 20.
- digitou `19` → O 19 foi apagado quando o 20 entrou. Vale o último escrito: 20.
- digitou `57` → Os valores não se somam: cada escrita apaga a anterior. Vale o último: 20.
- qualquer outro erro → Vale o último valor escrito na variável: 20.

### Degrau 5 — prática, digitar

**Versão 1.** Que número este trecho mostra na tela?

```c
int idade;
int nota;
idade = 20;
nota = 7;
nota = 9;
printf("%d\n", nota);
```

Resposta certa: `9`

Se errar:

- digitou `7` → O 7 foi apagado quando o 9 entrou em nota. Vale o último escrito: 9.
- digitou `20` → O 20 está em idade. O printf lê nota, e nela vale o último valor escrito: 9.
- qualquer outro erro → O printf lê nota, e nela vale o último valor escrito: 9.

**Versão 2.** Que número este trecho mostra na tela?

```c
int ano;
int pontos;
ano = 2026;
pontos = 10;
pontos = 12;
printf("%d\n", pontos);
```

Resposta certa: `12`

Se errar:

- digitou `10` → O 10 foi apagado quando o 12 entrou em pontos. Vale o último escrito: 12.
- digitou `2026` → O 2026 está em ano. O printf lê pontos, e nela vale o último valor escrito: 12.
- qualquer outro erro → O printf lê pontos, e nela vale o último valor escrito: 12.

### Se errar a pergunta do topo: a revisão

> Cada escrita apaga o valor que estava antes.
> A variável fica só com o último valor escrito nela.

```c
int idade;
idade = 20;
idade = 21;
printf("%d\n", idade);
```

A máquina imprime:

```
21
```

## I1 — No fim das contas, dar o valor na hora de declarar ou declarar e só depois atribuir chegam no mesmo lugar: uma variável pronta.

### Degrau 1 — guiado, tocar

> Dá para declarar e dar o valor na mesma linha.
> Em int idade = 20; a variável já nasce guardando 20.

**Versão 1.** Toque no valor que a variável recebe.

```c
int idade = 20;
```

Peças: `int`  `idade`  `=`  `20`  `;`

Resposta certa: `20`

Se errar:

- respondeu `idade` → idade é o nome da variável. O valor é o que vem depois do sinal de igual: 20.
- respondeu `int` → int é o tipo. O valor é o que vem depois do sinal de igual: 20.
- qualquer outro erro → O valor é o que vem depois do sinal de igual: 20.

**Versão 2.** Toque no valor que a variável recebe.

```c
int nota = 7;
```

Peças: `int`  `nota`  `=`  `7`  `;`

Resposta certa: `7`

Se errar:

- respondeu `nota` → nota é o nome da variável. O valor é o que vem depois do sinal de igual: 7.
- respondeu `int` → int é o tipo. O valor é o que vem depois do sinal de igual: 7.
- qualquer outro erro → O valor é o que vem depois do sinal de igual: 7.

### Degrau 2 — guiado, montar

> A ordem é: tipo, nome, sinal de igual, valor e ponto e vírgula.

**Versão 1.** Declare um inteiro chamado nota que já comece valendo 7.

Peças: `int`  `nota`  `=`  `7`  `;`

Resposta certa: `int nota = 7;`

Se errar:

- respondeu `int 7 = nota ;` → O nome fica antes do sinal de igual e o valor depois: int nota = 7;
- respondeu `nota = 7 ;` → Faltou o tipo. Sem ele a variável não é declarada: int nota = 7;
- não usou `;` → Faltou o ponto e vírgula no fim da linha: int nota = 7;
- qualquer outro erro → A linha é o tipo, o nome, o sinal de igual, o valor e o ponto e vírgula: int nota = 7;

**Versão 2.** Declare um inteiro chamado pontos que já comece valendo 10.

Peças: `int`  `pontos`  `=`  `10`  `;`

Resposta certa: `int pontos = 10;`

Se errar:

- respondeu `int 10 = pontos ;` → O nome fica antes do sinal de igual e o valor depois: int pontos = 10;
- respondeu `pontos = 10 ;` → Faltou o tipo. Sem ele a variável não é declarada: int pontos = 10;
- não usou `;` → Faltou o ponto e vírgula no fim da linha: int pontos = 10;
- qualquer outro erro → A linha é o tipo, o nome, o sinal de igual, o valor e o ponto e vírgula: int pontos = 10;

### Degrau 3 — guiado, escolher

> Declarar com valor faz, numa linha só, o mesmo que declarar e depois guardar.

**Versão 1.** Estes dois trechos deixam idade com o mesmo valor?

```c
Trecho 1:
int idade;
idade = 20;

Trecho 2:
int idade = 20;
```

Opções: `Sim: nos dois idade termina guardando 20`  `Não: só o de uma linha deixa a variável pronta`

Resposta certa: `Sim: nos dois idade termina guardando 20`

Se errar:

- respondeu `Não: só o de uma linha deixa a variável pronta` → Os dois chegam ao mesmo lugar: uma variável idade guardando 20. A linha única só junta os dois passos.
- qualquer outro erro → Os dois trechos terminam com idade guardando 20.

**Versão 2.** Estes dois trechos deixam turma com o mesmo valor?

```c
Trecho 1:
char turma;
turma = 'B';

Trecho 2:
char turma = 'B';
```

Opções: `Sim: nos dois turma termina guardando 'B'`  `Não: só o de uma linha deixa a variável pronta`

Resposta certa: `Sim: nos dois turma termina guardando 'B'`

Se errar:

- respondeu `Não: só o de uma linha deixa a variável pronta` → Os dois chegam ao mesmo lugar: uma variável turma guardando 'B'. A linha única só junta os dois passos.
- qualquer outro erro → Os dois trechos terminam com turma guardando 'B'.

### Degrau 4 — guiado, escolher

> O sinal de igual do C não é o da matemática: ele manda guardar.
> O valor da direita vai para a variável da esquerda, nunca o contrário.

**Versão 1.** Qual linha guarda 7 em nota?

Já está escrito:

```c
int nota;
```

Opções: `nota = 7;`  `7 = nota;`

Resposta certa: `nota = 7;`

Se errar:

- respondeu `7 = nota;` → O sinal de igual não funciona dos dois lados. À esquerda fica a variável que recebe, e por isso o compilador reclama de 7 = nota; _(aponta a crença `assignment_symmetric`)_
- qualquer outro erro → A variável que recebe fica à esquerda do sinal de igual: nota = 7;

**Versão 2.** Qual linha guarda 20 em idade?

Já está escrito:

```c
int idade;
```

Opções: `idade = 20;`  `20 = idade;`

Resposta certa: `idade = 20;`

Se errar:

- respondeu `20 = idade;` → O sinal de igual não funciona dos dois lados. À esquerda fica a variável que recebe, e por isso o compilador reclama de 20 = idade; _(aponta a crença `assignment_symmetric`)_
- qualquer outro erro → A variável que recebe fica à esquerda do sinal de igual: idade = 20;

### Degrau 5 — guiado, completar

> O valor da direita também pode vir de outra variável.
> Em nota = pontos; o que está guardado em pontos é copiado para nota.

**Versão 1.** Complete para que nota receba o valor que está em pontos.

Já está escrito:

```c
int pontos = 3;
int nota;
```

```c
nota = ___;
```

Peças: `pontos`  `nota`  `int`

Resposta certa: `nota = pontos;`

Se errar:

- respondeu `nota = nota;` → Assim nota receberia o próprio valor, e nela ninguém escreveu ainda. Quem tem o valor a copiar é pontos: nota = pontos;
- respondeu `nota = int;` → int é um tipo, não um valor. À direita vai a variável de onde o valor vem: nota = pontos;
- qualquer outro erro → À direita vai a variável de onde o valor vem: nota = pontos;

**Versão 2.** Complete para que idade receba o valor que está em ano.

Já está escrito:

```c
int ano = 5;
int idade;
```

```c
idade = ___;
```

Peças: `ano`  `idade`  `int`

Resposta certa: `idade = ano;`

Se errar:

- respondeu `idade = idade;` → Assim idade receberia o próprio valor, e nela ninguém escreveu ainda. Quem tem o valor a copiar é ano: idade = ano;
- respondeu `idade = int;` → int é um tipo, não um valor. À direita vai a variável de onde o valor vem: idade = ano;
- qualquer outro erro → À direita vai a variável de onde o valor vem: idade = ano;

### Degrau 6 — prática, montar

**Versão 1.** Escreva em uma linha só o que este trecho faz em duas.

```c
char turma;
turma = 'B';
```

Peças: `char`  `turma`  `=`  `'B'`  `;`

Resposta certa: `char turma = 'B';`

Se errar:

- respondeu `turma = 'B' ;` → Assim falta o tipo, e sem ele a variável não é declarada: char turma = 'B';
- respondeu `char 'B' = turma ;` → O nome fica antes do sinal de igual e o valor depois: char turma = 'B';
- não usou `;` → Faltou o ponto e vírgula no fim da linha: char turma = 'B';
- qualquer outro erro → Em uma linha: o tipo, o nome, o sinal de igual, o valor e o ponto e vírgula.

**Versão 2.** Escreva em uma linha só o que este trecho faz em duas.

```c
int ano;
ano = 2026;
```

Peças: `int`  `ano`  `=`  `2026`  `;`

Resposta certa: `int ano = 2026;`

Se errar:

- respondeu `ano = 2026 ;` → Assim falta o tipo, e sem ele a variável não é declarada: int ano = 2026;
- respondeu `int 2026 = ano ;` → O nome fica antes do sinal de igual e o valor depois: int ano = 2026;
- não usou `;` → Faltou o ponto e vírgula no fim da linha: int ano = 2026;
- qualquer outro erro → Em uma linha: o tipo, o nome, o sinal de igual, o valor e o ponto e vírgula.

### Degrau 7 — prática, digitar

**Versão 1.** Que número este trecho mostra na tela?

```c
int nota = 7;
int pontos = 3;
nota = pontos;
printf("%d\n", nota);
```

Resposta certa: `3`

Se errar:

- digitou `7` → nota = pontos; copia o valor da direita para a variável da esquerda. O 7 de nota foi apagado, e entrou o 3.
- digitou `10` → Os valores não se somam: nota recebe o valor que está em pontos, que é 3.
- qualquer outro erro → nota recebe o valor que está em pontos: 3.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade = 20;
int ano = 5;
idade = ano;
printf("%d\n", idade);
```

Resposta certa: `5`

Se errar:

- digitou `20` → idade = ano; copia o valor da direita para a variável da esquerda. O 20 de idade foi apagado, e entrou o 5.
- digitou `25` → Os valores não se somam: idade recebe o valor que está em ano, que é 5.
- qualquer outro erro → idade recebe o valor que está em ano: 5.

### Se errar a pergunta do topo: a revisão

> Declarar com valor e declarar para depois guardar dão no mesmo: a variável fica pronta, com o valor dentro.
> Em toda escrita, a variável que recebe fica à esquerda do sinal de igual.

```c
int nota;
nota = 7;
int pontos = 7;
printf("%d\n", nota);
printf("%d\n", pontos);
```

A máquina imprime:

```
7
7
```
