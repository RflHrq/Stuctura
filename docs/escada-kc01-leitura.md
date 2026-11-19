# A escada do kc_01 — Modelo de memória

Texto para leitura, gerado de `mvp/dominio/escada_kc01.yaml`. Cada degrau tem duas versões: a segunda aparece quando a pessoa erra a primeira.

## B1 — Enquanto o programa roda, ele tem uma rua só dele. Outro programa não mexe nessa rua.

### Degrau 1 — guiado, digitar

> Enquanto o programa roda, a memória que ele recebeu é só dele.
> Ninguém de fora mexe nela: o que ele escreveu continua lá.

**Versão 1.** Que número este trecho mostra na tela?

```c
int nota;
int idade;

nota = 7;
idade = 15;
idade = idade + 1;
printf("%d\n", nota);
```

Resposta certa: `7`

Se errar:

- digitou `16` → 16 é o que ficou em idade. nota recebeu 7, e ninguém mais escreveu nela: continua 7.
- digitou `8` → A soma foi feita em idade, que é outra variável. nota recebeu 7, e ninguém mais escreveu nela.
- qualquer outro erro → nota recebeu 7, e ninguém mais escreveu nela: continua 7.

**Versão 2.** Que número este trecho mostra na tela?

```c
int nota;
int idade;

nota = 9;
idade = 20;
idade = idade + 5;
printf("%d\n", nota);
```

Resposta certa: `9`

Se errar:

- digitou `25` → 25 é o que ficou em idade. nota recebeu 9, e ninguém mais escreveu nela: continua 9.
- digitou `14` → A soma foi feita em idade, que é outra variável. nota recebeu 9, e ninguém mais escreveu nela.
- qualquer outro erro → nota recebeu 9, e ninguém mais escreveu nela: continua 9.

### Degrau 2 — guiado, escolher

> Quando o programa termina, a memória dele volta para o sistema.
> Na próxima vez que rodar, ele recebe outra memória, que pode ter sido de qualquer programa.

**Versão 1.** O programa roda, guarda 7 em nota e termina. Depois roda de novo. O que a segunda execução encontra em nota, antes de escrever nela?

Já está escrito:

```c
int nota;

nota = 7;
```

Opções: `Um valor sem garantia: a memória da outra execução não é a dela`  `O 7: a memória é do computador, e guarda o que o último programa deixou`  `Zero: toda memória começa zerada`

Resposta certa: `Um valor sem garantia: a memória da outra execução não é a dela`

Se errar:

- respondeu `O 7: a memória é do computador, e guarda o que o último programa deixou` → A memória não fica guardando o que um programa deixou. Cada execução recebe a dela, e a da execução anterior voltou para o sistema. O 7 não está lá. _(aponta a crença `memoria_e_do_computador`)_
- respondeu `Zero: toda memória começa zerada` → O C não promete zero numa variável em que ninguém escreveu: o valor não tem garantia. O que é certo é que o 7 da outra execução não está lá.
- qualquer outro erro → Cada execução recebe a memória dela. O que a anterior guardou não está lá, e nota começa sem valor garantido.

**Versão 2.** O programa roda, guarda 42 em pontos e termina. Depois roda de novo. O que a segunda execução encontra em pontos, antes de escrever nela?

Já está escrito:

```c
int pontos;

pontos = 42;
```

Opções: `O 42: a memória é do computador, e guarda o que o último programa deixou`  `Zero: toda memória começa zerada`  `Um valor sem garantia: a memória da outra execução não é a dela`

Resposta certa: `Um valor sem garantia: a memória da outra execução não é a dela`

Se errar:

- respondeu `O 42: a memória é do computador, e guarda o que o último programa deixou` → A memória não fica guardando o que um programa deixou. Cada execução recebe a dela, e a da execução anterior voltou para o sistema. O 42 não está lá. _(aponta a crença `memoria_e_do_computador`)_
- respondeu `Zero: toda memória começa zerada` → O C não promete zero numa variável em que ninguém escreveu: o valor não tem garantia. O que é certo é que o 42 da outra execução não está lá.
- qualquer outro erro → Cada execução recebe a memória dela. O que a anterior guardou não está lá, e pontos começa sem valor garantido.

### Degrau 3 — guiado, escolher

> Dois programas rodando ao mesmo tempo têm, cada um, a sua memória e a sua numeração de endereços.
> Um não lê nem muda a do outro, mesmo que as variáveis tenham o mesmo nome.

**Versão 1.** Os dois programas rodam ao mesmo tempo, e cada um tem uma variável idade. O programa B escreve 0 na dele. Quanto vale a idade do programa A?

Já está escrito:

```c
/* programa A */  int idade = 15;
/* programa B */  int idade = 0;
```

Opções: `15: a memória de A é só de A`  `0: o nome é o mesmo, e a memória é uma só`  `Não dá para saber: um programa bagunça o outro`

Resposta certa: `15: a memória de A é só de A`

Se errar:

- respondeu `0: o nome é o mesmo, e a memória é uma só` → O nome igual não junta as duas: cada programa tem a memória dele, e a idade de B fica na de B. A de A continua com 15.
- respondeu `Não dá para saber: um programa bagunça o outro` → Um programa não alcança a memória do outro: nada que B faça muda a idade de A. Ela continua com 15.
- qualquer outro erro → A idade de A fica na memória de A, que B não alcança: 15.

**Versão 2.** Os dois programas rodam ao mesmo tempo, e cada um tem uma variável nota. O programa B escreve 10 na dele. Quanto vale a nota do programa A?

Já está escrito:

```c
/* programa A */  int nota = 7;
/* programa B */  int nota = 10;
```

Opções: `10: o nome é o mesmo, e a memória é uma só`  `Não dá para saber: um programa bagunça o outro`  `7: a memória de A é só de A`

Resposta certa: `7: a memória de A é só de A`

Se errar:

- respondeu `10: o nome é o mesmo, e a memória é uma só` → O nome igual não junta as duas: cada programa tem a memória dele, e a nota de B fica na de B. A de A continua com 7.
- respondeu `Não dá para saber: um programa bagunça o outro` → Um programa não alcança a memória do outro: nada que B faça muda a nota de A. Ela continua com 7.
- qualquer outro erro → A nota de A fica na memória de A, que B não alcança: 7.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Cada execução começa com a memória dela_

**Versão 1.** O programa quer contar quantas vezes já foi rodado, somando 1 numa variável a cada execução. Funciona?

Já está escrito:

```c
int vezes;

vezes = vezes + 1;
printf("%d\n", vezes);
```

Opções: `Não: cada execução recebe outra memória, e vezes começa sem valor garantido`  `Funciona: vezes guarda o que a execução anterior deixou`  `Funciona, enquanto o computador não for desligado`

Resposta certa: `Não: cada execução recebe outra memória, e vezes começa sem valor garantido`

Se errar:

- respondeu `Funciona: vezes guarda o que a execução anterior deixou` → A variável não guarda nada entre uma execução e outra: a memória da execução anterior voltou para o sistema. vezes começa sem valor garantido.
- respondeu `Funciona, enquanto o computador não for desligado` → Desligar não é a questão: basta o programa terminar. A memória dele volta para o sistema, e a execução seguinte recebe outra.
- qualquer outro erro → Cada execução recebe outra memória: vezes não traz nada da execução anterior.

**Versão 2.** O jogo guarda os pontos numa variável. Você fecha o jogo e abre de novo. Os pontos da partida anterior estão lá?

Já está escrito:

```c
int pontos;
```

Opções: `Estão: ficam na memória do computador até outro programa usar`  `Não: a memória daquela execução voltou para o sistema`  `Estão, se a variável tiver o mesmo nome`

Resposta certa: `Não: a memória daquela execução voltou para o sistema`

Se errar:

- respondeu `Estão: ficam na memória do computador até outro programa usar` → A memória não fica guardando o que um programa deixou: quando o jogo fechou, a dele voltou para o sistema. A nova execução recebe outra.
- respondeu `Estão, se a variável tiver o mesmo nome` → O nome da variável não segura valor nenhum. A memória da execução anterior voltou para o sistema, e a nova começa com outra.
- qualquer outro erro → Quando o jogo fechou, a memória dele voltou para o sistema. A nova execução recebe outra.

### Degrau 5 — prática, escolher

**Versão 1.** Os programas A e B rodam ao mesmo tempo. A termina. O que muda na memória de B?

Opções: `Nada: a memória de B é só de B`  `B passa a enxergar o que A tinha guardado`  `B perde o que tinha: a memória foi devolvida`

Resposta certa: `Nada: a memória de B é só de B`

Se errar:

- respondeu `B passa a enxergar o que A tinha guardado` → O que A guardou estava na memória de A, que voltou para o sistema. B continua só com a dele, e não enxerga a de mais ninguém.
- respondeu `B perde o que tinha: a memória foi devolvida` → Quem devolveu a memória foi A, e a memória devolvida era a de A. A de B continua com B, como estava.
- qualquer outro erro → Cada programa tem a sua memória. O fim de A não muda nada na de B.

**Versão 2.** O programa A tem um erro, e escreve sem parar em todas as variáveis dele. O que acontece com as variáveis do programa B, que roda ao mesmo tempo?

Opções: `São sobrescritas: a memória é do computador, e os dois dividem`  `Somem quando A terminar`  `Nada: A não alcança a memória de B`

Resposta certa: `Nada: A não alcança a memória de B`

Se errar:

- respondeu `São sobrescritas: a memória é do computador, e os dois dividem` → Os dois não dividem a memória: cada programa tem a dele. O que A escreve fica na de A, e não chega nas variáveis de B.
- respondeu `Somem quando A terminar` → Quando A termina, o que volta para o sistema é a memória de A. As variáveis de B estão na de B, e continuam lá.
- qualquer outro erro → Cada programa tem a sua memória. A não alcança as variáveis de B.

### Se errar a pergunta do topo: a revisão

> Cada vez que o programa roda, ele recebe uma memória só dele.
> Quando termina, ela volta para o sistema: o que ele guardou não fica esperando a próxima execução.

```c
int nota;

nota = 7;
printf("%d\n", nota);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> A memória é do computador, não do programa: o que está lá é o que o último programa deixou.

```c
int nota;

printf("%d\n", nota);
```

**O programa só lê nota: não escreve nada nela. O compilador reclama de alguma coisa?**

- Não: nota tem o que ficou na memória do computador _(é o que a crença espera)_
- Sim: nota é lida sem valor garantido _(é o que a máquina faz)_

O compilador reclama:

```
'nota' is used uninitialized
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado. Isto é o que se vê de dentro de um programa; que um não alcança a memória do outro, programa nenhum mostra sozinho._

O que isto mostra: O compilador reclama: nota é lida sem ter recebido valor ("used uninitialized"). Para o C não existe o que ficou do último programa: a memória que a execução recebe é só dela, e o que há num lugar em que ela não escreveu não tem garantia nenhuma.

## B2 — As casas criadas dentro de uma função aparecem quando ela começa e somem quando ela termina.

### Degrau 1 — guiado, digitar

> Uma função pode devolver um valor, com return. O tipo antes do nome diz o que ela devolve.
> Com int dobro(int n) { return n + n; } a chamada dobro(4) vale 8.

**Versão 1.** Que número este trecho mostra na tela?

```c
int dobro(int n) { return n + n; }

printf("%d\n", dobro(5));
```

Resposta certa: `10`

Se errar:

- digitou `5` → 5 é o que entrou em n. A função devolve n + n, e é esse valor que a chamada passa a valer: 10.
- qualquer outro erro → A chamada dobro(5) vale o que a função devolve: 5 mais 5, 10.

**Versão 2.** Que número este trecho mostra na tela?

```c
int mais3(int n) { return n + 3; }

printf("%d\n", mais3(4));
```

Resposta certa: `7`

Se errar:

- digitou `4` → 4 é o que entrou em n. A função devolve n + 3, e é esse valor que a chamada passa a valer: 7.
- qualquer outro erro → A chamada mais3(4) vale o que a função devolve: 4 mais 3, 7.

### Degrau 2 — guiado, escolher

> A variável declarada dentro da função é local: nasce quando a chamada começa e acaba quando ela termina.
> (void) nos parênteses quer dizer que a função não tem parâmetro.

**Versão 1.** A função é chamada duas vezes. Quando a segunda chamada começa, o que há com o n da primeira?

Já está escrito:

```c
int conta(void) { int n = 0; n = n + 1; return n; }

conta();
conta();
```

Opções: `Acabou: a segunda chamada cria outro n`  `Continua lá, com o 1 que tinha: a variável da função não some`  `Continua lá, mas zerado`

Resposta certa: `Acabou: a segunda chamada cria outro n`

Se errar:

- respondeu `Continua lá, com o 1 que tinha: a variável da função não some` → A variável local acaba quando a chamada termina. O n da primeira chamada não existe mais; a segunda cria outro, que começa do zero. _(aponta a crença `local_sobrevive`)_
- respondeu `Continua lá, mas zerado` → Não é o mesmo n, zerado: o da primeira chamada acabou. A segunda cria outro, e a linha int n = 0; dá o valor dele.
- qualquer outro erro → O n da primeira chamada acabou com ela. A segunda cria outro.

**Versão 2.** A função é chamada duas vezes. Quando a segunda chamada começa, o que há com o t da primeira?

Já está escrito:

```c
int soma(int v) { int t = 10; t = t + v; return t; }

soma(5);
soma(1);
```

Opções: `Continua lá, com o 15 que tinha: a variável da função não some`  `Continua lá, mas de volta em 10`  `Acabou: a segunda chamada cria outro t`

Resposta certa: `Acabou: a segunda chamada cria outro t`

Se errar:

- respondeu `Continua lá, com o 15 que tinha: a variável da função não some` → A variável local acaba quando a chamada termina. O t da primeira chamada não existe mais; a segunda cria outro, que começa do zero. _(aponta a crença `local_sobrevive`)_
- respondeu `Continua lá, mas de volta em 10` → Não é o mesmo t, de volta em 10: o da primeira chamada acabou. A segunda cria outro, e a linha int t = 10; dá o valor dele.
- qualquer outro erro → O t da primeira chamada acabou com ela. A segunda cria outro.

### Degrau 3 — guiado, digitar

> Por isso a função não lembra de nada entre uma chamada e outra.
> Ela pode ser escrita em várias linhas, entre as chaves: é a mesma função.

**Versão 1.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int conta(void) {
    int n = 0;
    n = n + 1;
    return n;
}

conta();
printf("%d\n", conta());
```

Resposta certa: `1`

Se errar:

- digitou `2` → O n da primeira chamada acabou junto com ela. A segunda cria outro n, que começa em 0 e vira 1.
- qualquer outro erro → Cada chamada cria o seu n, que começa em 0 e vira 1. A segunda devolve 1.

**Versão 2.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int passo(void) {
    int n = 5;
    n = n + 5;
    return n;
}

passo();
printf("%d\n", passo());
```

Resposta certa: `10`

Se errar:

- digitou `15` → O n da primeira chamada acabou junto com ela. A segunda cria outro n, que começa em 5 e vira 10.
- qualquer outro erro → Cada chamada cria o seu n, que começa em 5 e vira 10. A segunda devolve 10.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A variável local acaba com a chamada_

**Versão 1.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int soma(int v) { int t = 10; t = t + v; return t; }

soma(5);
printf("%d\n", soma(1));
```

Resposta certa: `11`

Se errar:

- digitou `16` → O t da primeira chamada acabou com ela. Na segunda nasce outro t, com 10, que soma 1: 11.
- digitou `15` → 15 foi o que a primeira chamada devolveu, e ninguém guardou. O printf mostra a segunda: 10 mais 1, 11.
- qualquer outro erro → A segunda chamada cria outro t, com 10, e soma 1: 11.

**Versão 2.** A função é chamada duas vezes, e só a segunda é mostrada. Que número aparece?

```c
int junta(int v) { int t = 100; t = t + v; return t; }

junta(20);
printf("%d\n", junta(3));
```

Resposta certa: `103`

Se errar:

- digitou `123` → O t da primeira chamada acabou com ela. Na segunda nasce outro t, com 100, que soma 3: 103.
- digitou `120` → 120 foi o que a primeira chamada devolveu, e ninguém guardou. O printf mostra a segunda: 100 mais 3, 103.
- qualquer outro erro → A segunda chamada cria outro t, com 100, e soma 3: 103.

### Degrau 5 — prática, escolher

**Versão 1.** A função devolve o endereço da variável dela. Quem recebe pode usar esse endereço?

Já está escrito:

```c
int *onde(void) { int idade = 15; return &idade; }
```

Opções: `Não: idade acabou com a chamada, e o endereço não aponta mais para ela`  `Pode: idade continua lá depois do return`  `Pode: o endereço foi devolvido, e leva a idade junto`

Resposta certa: `Não: idade acabou com a chamada, e o endereço não aponta mais para ela`

Se errar:

- respondeu `Pode: idade continua lá depois do return` → idade é local: acaba quando a chamada termina. O endereço devolvido fica apontando para um lugar que não é mais de idade.
- respondeu `Pode: o endereço foi devolvido, e leva a idade junto` → O return devolve só o endereço, que é um número. A variável não viaja com ele: acaba quando a chamada termina.
- qualquer outro erro → idade acaba quando a chamada termina. O endereço devolvido não aponta mais para uma variável.

**Versão 2.** A função devolve o endereço da variável dela. Quem recebe pode usar esse endereço?

Já está escrito:

```c
int *lugar(void) { int nota = 9; return &nota; }
```

Opções: `Pode: o endereço foi devolvido, e leva a nota junto`  `Pode: nota continua lá depois do return`  `Não: nota acabou com a chamada, e o endereço não aponta mais para ela`

Resposta certa: `Não: nota acabou com a chamada, e o endereço não aponta mais para ela`

Se errar:

- respondeu `Pode: nota continua lá depois do return` → nota é local: acaba quando a chamada termina. O endereço devolvido fica apontando para um lugar que não é mais de nota.
- respondeu `Pode: o endereço foi devolvido, e leva a nota junto` → O return devolve só o endereço, que é um número. A variável não viaja com ele: acaba quando a chamada termina.
- qualquer outro erro → nota acaba quando a chamada termina. O endereço devolvido não aponta mais para uma variável.

### Se errar a pergunta do topo: a revisão

> A variável declarada dentro da função é local: nasce quando a chamada começa e acaba quando a chamada termina.
> Na chamada seguinte nasce outra, do zero: a função não lembra de nada.

```c
int conta(void) { int n = 0; n = n + 1; return n; }

conta();
printf("%d\n", conta());
```

A máquina imprime:

```
1
```

### Se a pessoa disser a crença: a prova

Você disse:

> A variável que a função criou continua lá depois que a função termina.

```c
int *valor(void) { int n = 7; return &n; }

int *p;

p = valor();
```

**A função devolve o endereço de n, a variável dela, e p guarda esse endereço. O compilador reclama de alguma coisa?**

- Não: n continua lá depois que a função termina _(é o que a crença espera)_
- Sim: reclama de devolver o endereço de uma variável da função _(é o que a máquina faz)_

O compilador reclama:

```
function returns address of local variable
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: o que haveria naquele lugar, ninguém sabe._

O que isto mostra: O compilador reclama do return: a função devolve o endereço de uma variável local ("address of local variable"). n acaba quando a chamada termina, e o endereço fica apontando para um lugar que não é mais de n.

## B3 — O terreno que você aluga com malloc continua seu depois que a função acaba.

### Degrau 1 — guiado, digitar

> malloc(sizeof(int)) pede ao sistema um bloco do tamanho de um int, e devolve o endereço dele.
> O bloco não tem nome: chega-se nele pelo ponteiro que guardou o endereço.

**Versão 1.** Que número este trecho mostra na tela?

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
*p = *p + 1;
printf("%d\n", *p);
```

Resposta certa: `8`

Se errar:

- digitou `7` → O bloco recebeu 7, e a linha seguinte somou 1 nele, pelo mesmo endereço. *p acha 8.
- qualquer outro erro → O bloco recebeu 7 e depois mais 1, sempre pelo endereço guardado em p: 8.

**Versão 2.** Que número este trecho mostra na tela?

```c
int *q;

q = malloc(sizeof(int));
*q = 15;
*q = *q + 5;
printf("%d\n", *q);
```

Resposta certa: `20`

Se errar:

- digitou `15` → O bloco recebeu 15, e a linha seguinte somou 5 nele, pelo mesmo endereço. *q acha 20.
- qualquer outro erro → O bloco recebeu 15 e depois mais 5, sempre pelo endereço guardado em q: 20.

### Degrau 2 — guiado, completar

> O bloco é seu até você devolver, com free(p);
> free recebe o endereço do bloco. Dali em diante o bloco não é mais seu.

**Versão 1.** Complete com a linha que devolve o bloco.

Já está escrito:

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
```

```c
___;
```

Peças: `free(p)`  `free(*p)`  `p = NULL`

Resposta certa: `free(p);`

Se errar:

- respondeu `free(*p);` → *p é o valor guardado no bloco, o 7. free recebe o endereço do bloco, que está em p: o compilador reclama. O certo é free(p);
- respondeu `p = NULL;` → p = NULL; só apaga o endereço que estava em p. O bloco continua alugado, e agora ninguém sabe onde ele está. Quem devolve é free(p);
- qualquer outro erro → Quem devolve o bloco é free, com o endereço dele: free(p);

**Versão 2.** Complete com a linha que devolve o bloco.

Já está escrito:

```c
int *q;

q = malloc(sizeof(int));
*q = 15;
```

```c
___;
```

Peças: `q = NULL`  `free(q)`  `free(*q)`

Resposta certa: `free(q);`

Se errar:

- respondeu `free(*q);` → *q é o valor guardado no bloco, o 15. free recebe o endereço do bloco, que está em q: o compilador reclama. O certo é free(q);
- respondeu `q = NULL;` → q = NULL; só apaga o endereço que estava em q. O bloco continua alugado, e agora ninguém sabe onde ele está. Quem devolve é free(q);
- qualquer outro erro → Quem devolve o bloco é free, com o endereço dele: free(q);

### Degrau 3 — guiado, escolher

> Quando a função termina, acabam as variáveis locais dela, e o bloco do malloc não é uma delas.
> O sistema também não recolhe bloco sozinho: só o free devolve.

**Versão 1.** A função pede um bloco e termina sem chamar free. O que acontece com o bloco?

Já está escrito:

```c
void usa(void) { int *p = malloc(sizeof(int)); *p = 7; }

usa();
```

Opções: `Continua alugado: ninguém chamou free`  `O sistema recolhe sozinho, quando vê que ninguém usa mais`  `Some junto com a variável p`

Resposta certa: `Continua alugado: ninguém chamou free`

Se errar:

- respondeu `O sistema recolhe sozinho, quando vê que ninguém usa mais` → Em C ninguém recolhe por você: o bloco só volta com free. Como a função terminou sem chamar, ele continua alugado — e o endereço, que estava em p, se perdeu. _(aponta a crença `system_frees_auto`)_
- respondeu `Some junto com a variável p` → Quem some é p, a variável da função. O bloco é outra coisa: foi pedido com malloc, e só volta com free.
- qualquer outro erro → O bloco continua alugado: só free devolve, e ninguém chamou.

**Versão 2.** A função pede um bloco e termina sem chamar free. O que acontece com o bloco?

Já está escrito:

```c
void anota(void) { int *q = malloc(sizeof(int)); *q = 9; }

anota();
```

Opções: `Some junto com a variável q`  `Continua alugado: ninguém chamou free`  `O sistema recolhe sozinho, quando vê que ninguém usa mais`

Resposta certa: `Continua alugado: ninguém chamou free`

Se errar:

- respondeu `O sistema recolhe sozinho, quando vê que ninguém usa mais` → Em C ninguém recolhe por você: o bloco só volta com free. Como a função terminou sem chamar, ele continua alugado — e o endereço, que estava em q, se perdeu. _(aponta a crença `system_frees_auto`)_
- respondeu `Some junto com a variável q` → Quem some é q, a variável da função. O bloco é outra coisa: foi pedido com malloc, e só volta com free.
- qualquer outro erro → O bloco continua alugado: só free devolve, e ninguém chamou.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: O bloco continua seu depois que a função acaba_

**Versão 1.** A função pede um bloco, guarda nele o valor que recebeu e devolve o endereço. Ela é chamada duas vezes. Que número aparece?

```c
int *novo(int v) { int *p = malloc(sizeof(int)); *p = v; return p; }

int *a;
int *b;

a = novo(7);
b = novo(9);
printf("%d\n", *a);
free(a);
free(b);
```

Resposta certa: `7`

Se errar:

- digitou `9` → Cada chamada pede outro bloco. O de a continua com 7, mesmo depois de a função terminar; o 9 foi para o bloco de b.
- qualquer outro erro → O bloco de a continua valendo depois da função, com o 7 que recebeu.

**Versão 2.** A função pede um bloco, guarda nele o valor que recebeu e devolve o endereço. Ela é chamada duas vezes. Que número aparece?

```c
int *novo(int v) { int *p = malloc(sizeof(int)); *p = v; return p; }

int *a;
int *b;

a = novo(15);
b = novo(20);
printf("%d\n", *b);
free(a);
free(b);
```

Resposta certa: `20`

Se errar:

- digitou `15` → Cada chamada pede outro bloco. O de b recebeu 20, e continua valendo depois de a função terminar; o 15 está no bloco de a.
- qualquer outro erro → O bloco de b continua valendo depois da função, com o 20 que recebeu.

### Degrau 5 — prática, escolher

**Versão 1.** No fim deste trecho, quantos blocos continuam alugados?

Já está escrito:

```c
int *p;
int *q;

p = malloc(sizeof(int));
q = malloc(sizeof(int));
free(p);
```

Opções: `Um: o de q`  `Nenhum: o sistema recolhe o que sobrou`  `Dois: free só avisa o sistema`

Resposta certa: `Um: o de q`

Se errar:

- respondeu `Nenhum: o sistema recolhe o que sobrou` → Enquanto o programa roda, ninguém recolhe por você. O bloco de p voltou com free; o de q continua alugado.
- respondeu `Dois: free só avisa o sistema` → free devolve o bloco na hora: o de p não é mais seu. Sobra um alugado, o de q.
- qualquer outro erro → O bloco de p foi devolvido com free. O de q continua alugado: um.

**Versão 2.** No fim deste trecho, quantos blocos continuam alugados?

Já está escrito:

```c
int *a;
int *b;
int *c;

a = malloc(sizeof(int));
b = malloc(sizeof(int));
c = malloc(sizeof(int));
free(a);
free(c);
```

Opções: `Três: free só avisa o sistema`  `Nenhum: o sistema recolhe o que sobrou`  `Um: o de b`

Resposta certa: `Um: o de b`

Se errar:

- respondeu `Nenhum: o sistema recolhe o que sobrou` → Enquanto o programa roda, ninguém recolhe por você. Os blocos de a e de c voltaram com free; o de b continua alugado.
- respondeu `Três: free só avisa o sistema` → free devolve o bloco na hora: os de a e de c não são mais seus. Sobra um alugado, o de b.
- qualquer outro erro → Os blocos de a e de c foram devolvidos com free. O de b continua alugado: um.

### Se errar a pergunta do topo: a revisão

> malloc pede um bloco de memória e devolve o endereço dele. O bloco é seu até você devolver, com free.
> A função terminar não devolve o bloco, e o sistema não recolhe sozinho enquanto o programa roda.

```c
int *p;

p = malloc(sizeof(int));
*p = 7;
printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> O sistema libera a memória do heap automaticamente.

```c
void devolve(void) { int *p = malloc(sizeof(int)); free(p); }
void esquece(void) { int *p; p = malloc(sizeof(int)); }

devolve();
esquece();
```

**As duas funções pedem um bloco. Só a primeira chama free. Seguindo o caminho do programa, de qual delas o compilador reclama?**

- Da segunda: o bloco dela vazou _(é o que a máquina faz)_
- De nenhuma: o sistema recolhe sozinho o bloco da segunda _(é o que a crença espera)_

O compilador reclama:

```
leak of 'p'
```

_Mensagem do gcc 16.2 com o analisador de fluxo ligado (-fanalyzer), que segue o caminho do programa. "leak" é vazamento: memória pedida e nunca devolvida. O programa não é executado._

O que isto mostra: O compilador reclama da segunda função: o bloco de p vazou ("leak of 'p'"). Foi pedido, a função terminou, e ninguém o devolveu. Se o sistema recolhesse sozinho, não haveria vazamento para apontar.

## I1 — Então há dois jeitos: a casa some sozinha, e o terreno fica até você devolver.

### Degrau 1 — guiado, escolher

> A variável local acaba sozinha, quando a chamada termina.
> O bloco do malloc não: ele só acaba quando alguém chama free.

**Versão 1.** A função termina. O que acontece com n e com o bloco?

Já está escrito:

```c
int *guarda(void) { int n = 7; int *p = malloc(sizeof(int)); *p = n; return p; }
```

Opções: `n acaba; o bloco continua`  `Os dois acabam: o bloco do malloc também some quando a função termina`  `Os dois continuam até o programa terminar`

Resposta certa: `n acaba; o bloco continua`

Se errar:

- respondeu `Os dois acabam: o bloco do malloc também some quando a função termina` → Quem some com a função são as variáveis dela, n e p. O bloco foi pedido com malloc, e não é da função: continua valendo até alguém chamar free. _(aponta a crença `heap_dies_with_function`)_
- respondeu `Os dois continuam até o programa terminar` → n é local, e acaba quando a chamada termina. Quem continua é só o bloco, que foi pedido com malloc.
- qualquer outro erro → n é local e acaba com a chamada. O bloco continua até alguém chamar free.

**Versão 2.** A função termina. O que acontece com v e com o bloco?

Já está escrito:

```c
int *anota(void) { int v = 9; int *q = malloc(sizeof(int)); *q = v; return q; }
```

Opções: `Os dois continuam até o programa terminar`  `Os dois acabam: o bloco do malloc também some quando a função termina`  `v acaba; o bloco continua`

Resposta certa: `v acaba; o bloco continua`

Se errar:

- respondeu `Os dois acabam: o bloco do malloc também some quando a função termina` → Quem some com a função são as variáveis dela, v e q. O bloco foi pedido com malloc, e não é da função: continua valendo até alguém chamar free. _(aponta a crença `heap_dies_with_function`)_
- respondeu `Os dois continuam até o programa terminar` → v é local, e acaba quando a chamada termina. Quem continua é só o bloco, que foi pedido com malloc.
- qualquer outro erro → v é local e acaba com a chamada. O bloco continua até alguém chamar free.

### Degrau 2 — guiado, digitar

> O valor copiado para o bloco continua lá, mesmo depois de a variável local acabar.

**Versão 1.** A função copia o valor de n para o bloco e devolve o endereço. Que número aparece?

```c
int *guarda(void) { int n = 7; int *p = malloc(sizeof(int)); *p = n; return p; }

int *q;

q = guarda();
printf("%d\n", *q);
free(q);
```

Resposta certa: `7`

Se errar:

- digitou `0` → O bloco não some com a função: o 7 copiado para ele continua lá, e q guarda o endereço.
- qualquer outro erro → n acabou com a função, mas o 7 foi copiado para o bloco, que continua: 7.

**Versão 2.** A função copia o valor de v para o bloco e devolve o endereço. Que número aparece?

```c
int *anota(void) { int v = 9; int *q = malloc(sizeof(int)); *q = v; return q; }

int *p;

p = anota();
printf("%d\n", *p);
free(p);
```

Resposta certa: `9`

Se errar:

- digitou `0` → O bloco não some com a função: o 9 copiado para ele continua lá, e p guarda o endereço.
- qualquer outro erro → v acabou com a função, mas o 9 foi copiado para o bloco, que continua: 9.

### Degrau 3 — guiado, escolher

> A variável que guarda o endereço e o bloco são duas coisas, com dois fins diferentes.
> Variável local acaba sozinha; bloco do malloc, só com free.

**Versão 1.** Destas três coisas, qual só acaba quando alguém chama free?

Já está escrito:

```c
int nota;
int *q;

q = malloc(sizeof(int));
```

Opções: `O bloco que q aponta`  `A variável q`  `A variável nota`

Resposta certa: `O bloco que q aponta`

Se errar:

- respondeu `A variável q` → q é uma variável como as outras: acaba sozinha. O que só acaba com free é o bloco que ela aponta.
- respondeu `A variável nota` → nota é uma variável comum: acaba sozinha. O que só acaba com free é o bloco pedido com malloc.
- qualquer outro erro → As variáveis acabam sozinhas. Só o bloco pedido com malloc espera o free.

**Versão 2.** Destas três coisas, qual só acaba quando alguém chama free?

Já está escrito:

```c
int *p;
int idade;

p = malloc(sizeof(int));
```

Opções: `A variável idade`  `A variável p`  `O bloco que p aponta`

Resposta certa: `O bloco que p aponta`

Se errar:

- respondeu `A variável p` → p é uma variável como as outras: acaba sozinha. O que só acaba com free é o bloco que ela aponta.
- respondeu `A variável idade` → idade é uma variável comum: acaba sozinha. O que só acaba com free é o bloco pedido com malloc.
- qualquer outro erro → As variáveis acabam sozinhas. Só o bloco pedido com malloc espera o free.

### Degrau 4 — prática, digitar

_Nome do passo, no fechamento: A variável e o bloco acabam em horas diferentes_

**Versão 1.** O trecho devolve o bloco e depois pede outro, com o mesmo ponteiro. Que número aparece?

```c
int *q;

q = malloc(sizeof(int));
*q = 7;
free(q);
q = malloc(sizeof(int));
*q = 9;
printf("%d\n", *q);
free(q);
```

Resposta certa: `9`

Se errar:

- digitou `7` → O primeiro bloco foi devolvido com free. q, a variável, continuou existindo, e recebeu o endereço de outro bloco, onde foi escrito 9.
- qualquer outro erro → O primeiro bloco acabou no free; q continuou, e aponta agora para outro bloco, com 9.

**Versão 2.** O trecho devolve o bloco e depois pede outro, com o mesmo ponteiro. Que número aparece?

```c
int *p;

p = malloc(sizeof(int));
*p = 15;
free(p);
p = malloc(sizeof(int));
*p = 20;
printf("%d\n", *p);
free(p);
```

Resposta certa: `20`

Se errar:

- digitou `15` → O primeiro bloco foi devolvido com free. p, a variável, continuou existindo, e recebeu o endereço de outro bloco, onde foi escrito 20.
- qualquer outro erro → O primeiro bloco acabou no free; p continuou, e aponta agora para outro bloco, com 20.

### Degrau 5 — prática, escolher

**Versão 1.** Qual das duas funções devolve um endereço que ainda vale depois que ela termina?

Já está escrito:

```c
int *um(void) { int n = 7; return &n; }
int *dois(void) { int *p = malloc(sizeof(int)); *p = 7; return p; }
```

Opções: `dois: o bloco continua até o free`  `um: a variável n continua lá`  `Nenhuma: tudo o que a função criou acaba com ela`

Resposta certa: `dois: o bloco continua até o free`

Se errar:

- respondeu `um: a variável n continua lá` → n é local, e acaba quando um termina: o endereço dela não vale mais. Quem continua é o bloco de dois, pedido com malloc.
- respondeu `Nenhuma: tudo o que a função criou acaba com ela` → O que acaba com a função são as variáveis dela. O bloco pedido com malloc não é da função: continua até o free.
- qualquer outro erro → O endereço de n não vale depois da função. O do bloco vale, até o free.

**Versão 2.** Qual das duas funções devolve um endereço que ainda vale depois que ela termina?

Já está escrito:

```c
int *a(void) { int *q = malloc(sizeof(int)); *q = 9; return q; }
int *b(void) { int v = 9; return &v; }
```

Opções: `b: a variável v continua lá`  `Nenhuma: tudo o que a função criou acaba com ela`  `a: o bloco continua até o free`

Resposta certa: `a: o bloco continua até o free`

Se errar:

- respondeu `b: a variável v continua lá` → v é local, e acaba quando b termina: o endereço dela não vale mais. Quem continua é o bloco de a, pedido com malloc.
- respondeu `Nenhuma: tudo o que a função criou acaba com ela` → O que acaba com a função são as variáveis dela. O bloco pedido com malloc não é da função: continua até o free.
- qualquer outro erro → O endereço de v não vale depois da função. O do bloco vale, até o free.

### Se errar a pergunta do topo: a revisão

> São dois jeitos de acabar: a variável local acaba sozinha, quando a chamada termina.
> O bloco do malloc só acaba quando alguém chama free.

```c
int *faz(void) { int *p = malloc(sizeof(int)); *p = 9; return p; }

int *q;

q = faz();
printf("%d\n", *q);
free(q);
```

A máquina imprime:

```
9
```

### Se a pessoa disser a crença: a prova

Você disse:

> O bloco do malloc também some quando a função termina.

```c
int *faz(void) { int *p = malloc(sizeof(int)); *p = 7; return p; }

int *q;

q = faz();
printf("%d\n", *q);
free(q);
```

**A função pede um bloco, escreve 7 nele, devolve o endereço e termina. Depois dela, o trecho lê o bloco. O que aparece?**

- 7 _(é o que a máquina faz)_
- Um valor qualquer: o bloco sumiu junto com a função _(é o que a crença espera)_

A máquina imprime:

```
7
```

O que isto mostra: Saiu 7. A variável p acabou com a função, mas o bloco não: ele continua valendo até alguém chamar free. Foi por isso que o endereço devolvido ainda servia.

## I2 — Logo a rua tem duas quadras, com regras de arrumação diferentes.

### Degrau 1 — guiado, escolher

> As variáveis locais ficam numa área chamada pilha. Quem arruma a pilha é o compilador, a cada chamada.
> Os blocos do malloc ficam em outra área, o monte. Quem arruma o monte é você, com free.

**Versão 1.** Onde fica cada coisa?

Já está escrito:

```c
int nota;
int *p;

p = malloc(sizeof(int));
```

Opções: `nota e p na pilha; o bloco no monte`  `Tudo no mesmo lugar: memória é uma só, com uma regra só`  `nota na pilha; p e o bloco no monte`

Resposta certa: `nota e p na pilha; o bloco no monte`

Se errar:

- respondeu `Tudo no mesmo lugar: memória é uma só, com uma regra só` → A memória do programa tem duas áreas, com regras diferentes. nota e p são variáveis locais, e ficam na pilha; o bloco pedido com malloc fica no monte. _(aponta a crença `memory_is_uniform`)_
- respondeu `nota na pilha; p e o bloco no monte` → p é uma variável local como nota: fica na pilha. No monte está só o bloco que p aponta.
- qualquer outro erro → As variáveis nota e p ficam na pilha. O bloco pedido com malloc fica no monte.

**Versão 2.** Onde fica cada coisa?

Já está escrito:

```c
int *q;
int idade;

q = malloc(sizeof(int));
```

Opções: `idade na pilha; q e o bloco no monte`  `idade e q na pilha; o bloco no monte`  `Tudo no mesmo lugar: memória é uma só, com uma regra só`

Resposta certa: `idade e q na pilha; o bloco no monte`

Se errar:

- respondeu `Tudo no mesmo lugar: memória é uma só, com uma regra só` → A memória do programa tem duas áreas, com regras diferentes. idade e q são variáveis locais, e ficam na pilha; o bloco pedido com malloc fica no monte. _(aponta a crença `memory_is_uniform`)_
- respondeu `idade na pilha; q e o bloco no monte` → q é uma variável local como idade: fica na pilha. No monte está só o bloco que q aponta.
- qualquer outro erro → As variáveis idade e q ficam na pilha. O bloco pedido com malloc fica no monte.

### Degrau 2 — guiado, escolher

> As regras são diferentes: o que está na pilha acaba sozinho; o que está no monte, só com free.
> Por isso free só serve para bloco do monte.

**Versão 1.** Qual destas linhas devolve memória do jeito certo?

Já está escrito:

```c
int nota;
int *p;

p = malloc(sizeof(int));
```

Opções: `free(p);`  `free(&nota);`  `free(nota);`

Resposta certa: `free(p);`

Se errar:

- respondeu `free(&nota);` → nota fica na pilha, e acaba sozinha: não foi pedida com malloc, e free não serve para ela. O compilador reclama. Quem se devolve é o bloco: free(p);
- respondeu `free(nota);` → free recebe o endereço de um bloco do monte, e nota é um número, de uma variável da pilha: o compilador reclama. Quem se devolve é o bloco: free(p);
- qualquer outro erro → free serve para o bloco do monte, pelo endereço dele: free(p);

**Versão 2.** Qual destas linhas devolve memória do jeito certo?

Já está escrito:

```c
int *q;
int idade;

q = malloc(sizeof(int));
```

Opções: `free(&idade);`  `free(idade);`  `free(q);`

Resposta certa: `free(q);`

Se errar:

- respondeu `free(&idade);` → idade fica na pilha, e acaba sozinha: não foi pedida com malloc, e free não serve para ela. O compilador reclama. Quem se devolve é o bloco: free(q);
- respondeu `free(idade);` → free recebe o endereço de um bloco do monte, e idade é um número, de uma variável da pilha: o compilador reclama. Quem se devolve é o bloco: free(q);
- qualquer outro erro → free serve para o bloco do monte, pelo endereço dele: free(q);

### Degrau 3 — guiado, digitar

> As duas áreas trabalham juntas: a variável da pilha guarda o endereço, e o valor fica no bloco do monte.

**Versão 1.** Que número este trecho mostra na tela?

```c
int nota;
int *p;

nota = 7;
p = malloc(sizeof(int));
*p = nota + 1;
printf("%d\n", *p);
free(p);
```

Resposta certa: `8`

Se errar:

- digitou `7` → O bloco recebeu nota + 1: 7 mais 1. nota, na pilha, continua com 7; *p, no monte, vale 8.
- qualquer outro erro → nota, na pilha, vale 7. O bloco, no monte, recebeu 7 mais 1: 8.

**Versão 2.** Que número este trecho mostra na tela?

```c
int idade;
int *q;

idade = 15;
q = malloc(sizeof(int));
*q = idade + 5;
printf("%d\n", *q);
free(q);
```

Resposta certa: `20`

Se errar:

- digitou `15` → O bloco recebeu idade + 5: 15 mais 5. idade, na pilha, continua com 15; *q, no monte, vale 20.
- qualquer outro erro → idade, na pilha, vale 15. O bloco, no monte, recebeu 15 mais 5: 20.

### Degrau 4 — prática, escolher

_Nome do passo, no fechamento: Pilha e monte têm regras diferentes_

**Versão 1.** Cada função é chamada mil vezes. Em qual das duas a memória vai se enchendo?

Já está escrito:

```c
void local(void) { int n = 7; printf("%d\n", n); }
void aluga(void) { int *p = malloc(sizeof(int)); *p = 7; }
```

Opções: `Na aluga: cada chamada pede um bloco do monte e não devolve`  `Na local: cada chamada cria mais um n na pilha`  `Em nenhuma: a memória é uma só, e o sistema arruma`

Resposta certa: `Na aluga: cada chamada pede um bloco do monte e não devolve`

Se errar:

- respondeu `Na local: cada chamada cria mais um n na pilha` → O n da pilha acaba sozinho no fim de cada chamada: não sobra nada. Quem acumula é a aluga, que pede um bloco do monte a cada chamada e não devolve.
- respondeu `Em nenhuma: a memória é uma só, e o sistema arruma` → As duas áreas têm regras diferentes. A pilha se arruma sozinha a cada chamada; o monte, só com free — e a aluga nunca chama.
- qualquer outro erro → A pilha se arruma sozinha. O monte, não: os blocos da aluga vão se acumulando.

**Versão 2.** Cada função é chamada mil vezes. Em qual das duas a memória vai se enchendo?

Já está escrito:

```c
void pede(void) { int *q = malloc(sizeof(int)); *q = 9; }
void conta(void) { int v = 9; printf("%d\n", v); }
```

Opções: `Em nenhuma: a memória é uma só, e o sistema arruma`  `Na conta: cada chamada cria mais um v na pilha`  `Na pede: cada chamada pede um bloco do monte e não devolve`

Resposta certa: `Na pede: cada chamada pede um bloco do monte e não devolve`

Se errar:

- respondeu `Na conta: cada chamada cria mais um v na pilha` → O v da pilha acaba sozinho no fim de cada chamada: não sobra nada. Quem acumula é a pede, que pede um bloco do monte a cada chamada e não devolve.
- respondeu `Em nenhuma: a memória é uma só, e o sistema arruma` → As duas áreas têm regras diferentes. A pilha se arruma sozinha a cada chamada; o monte, só com free — e a pede nunca chama.
- qualquer outro erro → A pilha se arruma sozinha. O monte, não: os blocos da pede vão se acumulando.

### Degrau 5 — prática, digitar

**Versão 1.** O valor de nota é copiado para o bloco, e depois nota muda. Que número aparece?

```c
int nota;
int *p;

nota = 7;
p = malloc(sizeof(int));
*p = nota;
nota = 0;
printf("%d\n", *p);
free(p);
```

Resposta certa: `7`

Se errar:

- digitou `0` → nota e o bloco são dois lugares, em áreas diferentes. O 7 foi copiado para o bloco antes de nota mudar: *p continua 7.
- qualquer outro erro → O 7 foi copiado para o bloco, no monte. Mudar nota, na pilha, não muda o bloco.

**Versão 2.** O valor de idade é copiado para o bloco, e depois idade muda. Que número aparece?

```c
int idade;
int *q;

idade = 15;
q = malloc(sizeof(int));
*q = idade;
idade = 1;
printf("%d\n", *q);
free(q);
```

Resposta certa: `15`

Se errar:

- digitou `1` → idade e o bloco são dois lugares, em áreas diferentes. O 15 foi copiado para o bloco antes de idade mudar: *q continua 15.
- qualquer outro erro → O 15 foi copiado para o bloco, no monte. Mudar idade, na pilha, não muda o bloco.

### Se errar a pergunta do topo: a revisão

> A memória do programa tem duas áreas. A pilha guarda as variáveis locais, e o compilador a arruma sozinho.
> O monte guarda os blocos do malloc, e quem arruma é você, com free.

```c
int nota;
int *p;

nota = 7;
p = malloc(sizeof(int));
*p = nota;
printf("%d\n", *p);
free(p);
```

A máquina imprime:

```
7
```

### Se a pessoa disser a crença: a prova

Você disse:

> Memória é uma região única, sem distinção de regras de vida.

```c
int nota;
int *p;

nota = 7;
p = malloc(sizeof(int));
free(p);
free(&nota);
```

**O trecho chama free duas vezes: para o bloco que p aponta, e para a variável nota. De qual das duas o compilador reclama?**

- De nenhuma: memória é uma só, e free serve para qualquer lugar _(é o que a crença espera)_
- Da última: nota não foi pedida com malloc _(é o que a máquina faz)_

O compilador reclama:

```
'free' called on unallocated object 'nota'
```

_Mensagem do gcc 16.2 com os avisos ligados (-Wall). O programa não é executado: devolver o que não foi pedido não tem resultado definido._

O que isto mostra: O compilador aceita free(p); e reclama de free(&nota);: nota não é um bloco pedido ("unallocated object"). As duas áreas têm regras diferentes: o que é da pilha acaba sozinho, e free só serve para o que veio do monte.
