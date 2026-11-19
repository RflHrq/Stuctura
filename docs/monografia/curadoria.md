# Curadoria do catálogo de concepções errôneas

> Capítulo da monografia. A numeração depende da estrutura final; aqui o
> capítulo é identificado pelo nome.
>
> **Os números deste texto estão presos ao catálogo.** O apêndice de
> curadoria (`docs/curadoria-crencas.md`) é gerado de
> `mvp/dominio/beliefs_kc*.yaml` por `scripts/gera_curadoria.py`, e o teste
> `test_o_capitulo_existe_e_afirma_o_que_o_catalogo_diz`, em
> `mvp/test_procedencia.py`, confere **frase por frase** os números que este
> capítulo afirma contra o que o catálogo sustenta. Se o catálogo mudar e o
> capítulo não, a suíte falha e aponta a frase a reescrever.

## O problema que este capítulo resolve

O sistema descrito nos capítulos anteriores faz uma afirmação forte a cada
atividade respondida: *esta pessoa provavelmente sustenta esta concepção
errônea*. A afirmação tem consequência imediata: ela escolhe o percurso de
refutação que a pessoa vai atravessar.

Toda a validade dessa afirmação depende de uma pergunta anterior, que o
software não responde: **de onde vem cada concepção do catálogo?**

Se uma delas foi escrita pelo autor porque lhe pareceu plausível, o sistema
não está diagnosticando uma concepção errônea documentada. Está produzindo
dado sobre uma ficção, e produzindo-o com a mesma aparência de rigor que
produz o resto. O projeto registrou isso como regra, em `docs/linguagem.md`:

> Uma crença sem procedência é uma invenção sua que vai virar dado.

Este capítulo é a resposta a essa pergunta, e ela é verificável sem
participante nenhum. O instrumento não foi avaliado com estudantes; essa limitação está declarada no capítulo de limitações. O que se pode afirmar, e
é o que aqui se sustenta, é mais modesto e inteiramente conferível: **o
sistema afirma sobre concepções errôneas só o que a literatura registra, e
recusa afirmar o resto.**

## A régua: cinco graus de procedência

Cada concepção do catálogo carrega um campo `provenance`, com um de cinco
valores. O grau não descreve a importância da concepção nem a confiança do
autor nela: descreve **que tipo de obra a sustenta**.

**Quadro 4.1 — Os cinco graus de procedência**

| grau | o que afirma |
| --- | --- |
| `D` | documentada: achado empírico, com fonte e posição localizável |
| `L` | registrada como erro comum em obra técnica |
| `T` | transposta de outra linguagem, **com a analogia declarada** |
| `N` | o erro está em norma, como o CERT C (SEI, 2025) e a CWE (MITRE, 2026); a concepção, não |
| `E` | elaborada a partir do modelo de máquina: **hipótese a testar** |

Duas propriedades desse campo importam para o método, e não são
decorativas.

A primeira: **o grau é afirmação sobre a literatura, não sobre o uso.** A
mesma concepção aparece em mais de um tópico do domínio (quatorze delas aparecem), e o texto que a contextualiza muda de tópico para tópico, como
deve. O grau não muda. Se uma concepção é `D` num tópico e `L` noutro, uma
das duas afirmações é falsa, e num trabalho acadêmico essa é a diferença
entre citar e alegar. A auditoria descrita adiante encontrou três casos
desses e os corrigiu; um teste passou a proibi-los.

A segunda: **`E` é legítimo, e só vale declarado.** Uma hipótese do autor
pode entrar no catálogo; o que não pode é entrar com cara de achado. As
três hipóteses atuais dizem no próprio campo de fonte que são hipóteses, e
há dois testes independentes garantindo que nenhuma delas apareça nos
tópicos escolhidos para coleta.

## As duas classes de fonte

O catálogo se apoia em dois tipos de obra. A diferença entre eles não é de
qualidade: é de **que tipo de afirmação cada um sustenta**. Confundi-los
seria o defeito metodológico; declará-los, linha por linha, é o que torna o
catálogo auditável.

### Classe 1: literatura de concepções errôneas (23 concepções)

Estudo empírico com estudantes, ou revisão que os agrega. A obra principal é
o **Apêndice A de Sorva (2012)**: a Tabela A.1 arrola 162 concepções
errôneas levantadas da literatura de ensino de programação introdutória,
cada uma com tópico, descrição e fonte. Ao lado dela entram os estudos que
ela própria atribui: du Boulay (1986), Soloway et al. (1982), Putnam et al.
(1986), Sleeman et al. (1986), Samurçay (1989), Holland et al. (1997), Ma
(2007), Doukakis et al. (2007), Kaczmarczyk et al. (2010).

**O que esta classe sustenta:** que a concepção foi *observada em
estudantes*, por alguém que a estudou.

### Classe 2: corpus de praticante (34 concepções)

O **FAQ do comp.lang.c**, composto em 1990 a partir do grupo de Usenet de
mesmo nome e refinado episodicamente desde então, publicado em forma de
livro por Summit (1996).

A inclusão dessa classe exige justificar por que um FAQ de linguagem é
evidência sobre *concepção errônea*, e não apenas sobre C. A justificativa é
o critério de inclusão adotado, e ele é conferível por qualquer leitor:
**só entra a pergunta cujo título é a concepção dita por quem a sustenta**,
em primeira pessoa.

**Quadro 4.2 — Perguntas do FAQ cujo título é a concepção dita por quem a sustenta (exemplos)**

| pergunta | título |
| --- | --- |
| 6.2 | *"But I heard that `char a[]` was identical to `char *a`."* |
| 6.9 | *"Someone explained to me that arrays were really just constant pointers."* |
| 6.4b | *"So arrays are passed by reference, even though the rest of C uses pass by value?"* |
| 4.11 | *"Does C even have ``pass by reference''?"* |

*Fonte: elaborado pelo autor, com títulos de perguntas de Summit (1996).*

O catálogo não **infere** a concepção a partir de uma explicação técnica:
ele **lê a frase de quem a sustenta**. Quem quiser conferir abre a pergunta
e julga se o título é a concepção ou apenas o assunto.

Em termos de método, isso faz do FAQ uma **fonte documental**: um corpus de
confusões auto-relatadas, ocorridas naturalmente e curadas por *recorrência*
ao longo de mais de três décadas. O tratamento dado aqui é análise
documental desse corpus.

**O que esta classe sustenta, e o que ela não sustenta:**

- sustenta que a confusão **ocorre e recorre** entre quem aprende C;
- **não** sustenta prevalência. A população é auto-selecionada (quem escreve para um grupo de Usenet), e a frequência é juízo do editor, não
  medida. Nenhuma afirmação de proporção sai desta fonte, e nenhuma é feita.

### Por que a segunda classe é necessária, e isso é um achado

A exigência razoável seria: ancore tudo na classe 1, que é empírica, e
dispense a classe 2. Essa exigência foi testada contra o catálogo do Sorva,
item por item, e **ela não é satisfazível**.

A Tabela A.1 tem um tópico dedicado a referências (`Refs`, com 17 dos 162 itens) e itens sobre memória e tempo de vida espalhados por `VarAssign`,
`ObjState` e `Misc`. O que ela não tem é o que importa aqui, e a contagem
abaixo é reprodutível por busca de termo no texto da tabela:

**Quadro 4.3 — Ocorrências de termos de memória na Tabela A.1**

| termo buscado na Tabela A.1 | ocorrências |
| --- | --- |
| `malloc`, `free`, `deallocat`, `garbage` | **0** |
| `heap`, `stack` | **0** |
| `arithmetic`, `decay`, `dangling`, `sizeof` | **0** |
| `null` | **1**, e é *"Null model of recursion"* (item 54, p. 362), que não trata de ponteiro nulo |
| `lifetime` | **1**: item 5, p. 359, *"Difficulties understanding the lifetime of values"* |
| `memory` | 7 |

*Fonte: elaborado pelo autor, por busca no texto de Sorva (2012).*

Ou seja: **nenhum item sobre `NULL`, nenhum sobre `malloc`/`free`, nenhum
sobre aritmética de ponteiro, nenhum sobre decaimento de array, nenhum sobre
a distinção entre pilha e monte.**

A razão não é descuido da obra: aquele catálogo é de programação
introdutória em **Java, Python e BASIC**, onde esses construtos não existem.
A literatura de concepções errôneas **não pode** documentar confusões sobre
exatamente o que distingue C das linguagens em que ela foi produzida.

A conclusão, então, não é que as 34 concepções da classe 2 sejam fracas. É
que **um catálogo de concepções errôneas para C exige uma segunda classe de
fonte, e ela tem de ser declarada como segunda classe**, com o que sustenta
e o que não sustenta escrito ao lado. É o que a coluna de classe do
apêndice de curadoria faz, linha por linha.

## O procedimento de conferência

O padrão fixado pelo projeto é explícito, e está escrito no cabeçalho do
primeiro catálogo de tópico: *as fontes foram conferidas na obra primária,
não de memória*. O que isso significou, concepção por concepção, está na
tabela abaixo.

Ela é **exaustiva e exclusiva**: cada uma das 61 concepções
aparece em exatamente uma linha, e a linha registra **a verificação mais
forte alcançada** para ela. A soma é 61, de propósito: um quadro de "quantas
concepções citam cada obra" somaria mais, porque uma concepção pode citar
duas, e não permitiria dizer quantas ficaram sem conferência.

**Quadro 4.4 — Como cada uma das 61 concepções foi conferida**

| como foi conferida | concepções |
| --- | --- |
| **conferida no texto integral de Sorva (2012)**, obtido do repositório aberto da Aalto (handle `123456789/3534`, bundle TEXT); a frase em inglês entre aspas da citação foi localizada no texto da obra | 21 |
| **conferida no índice do FAQ comp.lang.c**: seções 1, 4, 5, 6 e 7 abertas em `c-faq.com`; as perguntas citadas existem e os títulos conferem com o que o catálogo cita | 32 |
| citação abreviada no catálogo; forma íntegra localizada na obra | 1 |
| cita o Sorva com página e item, mas **sem frase entre aspas**, logo não verificável pelo procedimento mecânico | 1 |
| conferência **parcial**: a seção 11 do FAQ ficou fora desta passada | 1 |
| **não conferida**: fonte pública (CWE), não reaberta aqui | 1 |
| **sem item na literatura**, com a busca declarada em campo próprio | 2 |
| **sem fonte, por desenho**: hipótese declarada como tal | 2 |
| | **61** |

As duas primeiras linhas somam as **53 conferidas na obra primária**. As
seis últimas são o que este capítulo não afirma ter conferido, e cada uma
diz por quê.

Não aparecem como linha própria, porque não foram abertos, os estudos que o Apêndice A do Sorva agrega: du Boulay (1986), Samurçay
(1989), Sleeman et al. (1986), Soloway et al. (1982), Putnam et al. (1986),
Doukakis et al. (2007), Ma (2007), Kaczmarczyk et al. (2010). As cinco concepções que
os citam fazem-no **`apud` Sorva (2012)**, com página e item, e caem na
primeira linha da tabela. A seção de integridade adiante detalha isso.

A conferência é **mecânica onde pode ser**: o programa que gera o apêndice
de curadoria extrai a frase entre aspas de cada citação e a procura no texto
da obra. Ele não confia no campo de fonte: ele confere. Rodado sem o texto
da obra, o número de conferidas cai de 53 para 32 e o documento passa a
dizer, linha por linha, que não conferiu. Um programa que mente quando lhe
falta insumo seria pior que um programa que não roda.

## O resultado

**Quadro 4.5 — O resultado da curadoria**

| | |
| --- | --- |
| concepções distintas no catálogo | **61** |
| conferidas na obra primária | **53** |
| graus | `D` 6, `L` 33, `T` 16, `N` 3, `E` 3 |
| hipóteses `E` | **3**, todas fora dos tópicos escolhidos para coleta |

## O que a auditoria encontrou

Os achados abaixo valem mais que a tabela, porque são sobre **o método de
construir catálogo a partir da literatura**, e não sobre C.

### 1. Três vezes a busca errou de vocabulário ou de item, e as três vezes o certo estava lá

**Quadro 4.6 — As três buscas que erraram, e o que estava na obra**

| concepção | o que a nota dizia | o que estava lá |
| --- | --- | --- |
| `pointer_has_no_address` | *"procurei no catálogo do Sorva e não está lá: nenhum dos 162 itens afirma que a referência não ocupa espaço"* | item 14, p. 360, **segunda frase**: *"It is not stored inside the computer."* A busca procurou REFERÊNCIA e ESPAÇO; o item fala de VARIÁVEL |
| `array_confused_with_cell` | *"não tem fonte empírica, entra como hipótese"* | item 151, p. 367: *"Confusion between an array and its cell"*, e item 9, p. 359: *"A variable can hold multiple values at a time."* A busca procurou ARRAY; o item 9 fala de VARIÁVEL e o 151 está no tópico `Misc` |
| `assignment_symmetric` | citava o item 11, com a aproximação declarada: *"o 11 é sobre a direção invertida, e esta concepção é sobre os dois lados"* | item 12, p. 359, **logo abaixo do 11**: *"Primitive assignment works both directions (swaps)."* É a frase do rótulo, traduzida |

*Fonte: elaborado pelo autor, com trechos de Sorva (2012).*

Nos três casos o grau subiu (`E`→`T`, `E`→`D` e `L`→`D`) **porque a busca
foi refeita com outro vocabulário**, e não porque se decidiu confiar na
intuição.

Daí sai uma recomendação de método, replicável: **buscar pelo fenômeno, não
pelo termo da própria linguagem.** Num catálogo de concepções errôneas da
linguagem X, o item procurado pode estar escrito no vocabulário da linguagem Y, e estará, se o catálogo foi produzido em Y.

O terceiro caso acrescenta um segundo princípio, e ele é sobre honestidade
de citação: **foi a aproximação declarada que tornou o erro achável.** A
citação dizia em que o item diferia da concepção, e foi essa diferença que
apontou para o item vizinho. Uma citação que esconde a folga não dá esse aviso: ela fica errada em silêncio.

### 2. Uma citação estava no item errado, e a concepção estava certa

`pointer_is_data` apontava o item 14 do Sorva, que trata de variável ser par nome-valor: **não é sobre ponteiro**. A concepção está no catálogo, mas no
item 65, p. 362: *"A (non-primitive Java) variable does not hold a reference
but a set of object properties."* A obra estava certa; o item, não. Não há
como encontrar isso sem abrir a obra.

Um segundo caso do mesmo tipo apareceu ao montar a lista de referências
deste capítulo. A Tabela A.1 atribui quatorze dos itens usados a
"Ma (2007)", e o catálogo registrava essa obra como um artigo de SIGCSE
assinado por quatro autores. A bibliografia de Sorva (2012) identifica
"Ma (2007)" como uma **tese de doutorado** de autor único, de outra
instituição. Citar uma obra mediada exige ler a bibliografia da obra mediadora; não basta reconhecer o sobrenome e o ano.

### 3. Uma resposta de FAQ costuma responder a duas confusões

`memory_is_by_name` e `pointer_has_no_address` saem das duas frases do
**mesmo item 14** do Sorva. No FAQ, a pergunta 7.21 sustenta três concepções de um
tópico, a 7.22 duas de outro, a 4.9 duas de um terceiro.

Isso não é economia de fonte: é que uma resposta de FAQ costuma responder a
**duas confusões diferentes**, e separá-las é trabalho de curadoria, não de
leitura.

### 4. Seis citações não se sustentavam, e foram reescritas ou removidas

A regra aplicada foi: se a fonte não pode ser verificada, procura-se o
correspondente; se não houver, **remove-se**.

- **Hermans et al. (2018) foi removida.** A citação de `variable_remembers`
  a trazia, e a obra não aparece em item nenhum da Tabela A.1 nem na bibliografia do
  Sorva: zero ocorrências no texto integral. Sem a obra aberta e sem
  corroboração, a citação não se sustentava. Aberta depois, na conferência
  das referências deste trabalho (19/11/2026), a obra registra essa
  concepção, a de que a variável guarda vários valores ou "lembra" os
  anteriores, e a estuda num experimento com 496 iniciantes; a citação
  pode voltar ao catálogo na próxima revisão dele.
- **Uma atribuição estava trocada.** `declaration_allocates` citava
  *"Kaczmarczyk et al. (2010), p. 109, Tabela 2, MMR4"*. O item do Sorva que
  registra essa concepção (item 92, p. 364) atribui a **Ma (2007)**.
  A afirmação sobre a página 109 e o código da tabela não era verificável por
  quem a escreveu, e saiu. A concepção vive num dos tópicos escolhidos para
  coleta, o que torna a correção material.
- **Uma concepção desceu de grau.** `memory_is_uniform` era `T` com citação
  de página e tabela de um artigo sem cópia de acesso aberto. Procurada item
  por item no Apêndice A, não há item sobre a memória ser região única sem
  distinção de regras de tempo de vida; o mais próximo, item 5, p. 359, é
  *dificuldade* com tempo de vida, que é outra coisa. Passou a `E`,
  declarada como hipótese.
- **Uma obra técnica estava no campo errado.** `declaration_zeroes` citava
  Kernighan e Ritchie como fonte. K&R é a obra que diz que a concepção é **falsa**: é a refutação, não o registro de que alguém a sustenta. Os dois
  papéis passaram a ficar separados, e a fonte passou a ser o item 10, p. 359.
- **Um código interno de artigo saiu da citação.** `no_value_no_memory`
  citava Kaczmarczyk et al. (2010) trazendo o código "(PVR2)" com que o
  artigo nomeia o achado. O código é verificável só por quem abriu o artigo,
  e saiu; ficou a citação `apud`, com item 22, p. 360.
- **Uma aproximação declarada virou citação exata.** `assignment_symmetric`
  mudou de item e subiu de grau; o caso está contado na subseção 4.6.1, acima,
  porque é também um resultado de método.

### 5. A mesma concepção tinha procedência divergente entre tópicos

Quatorze concepções aparecem em mais de um tópico, e cada cópia tem seu
próprio campo de fonte, escrito à mão. Três divergiam no **grau**, e, em dois desses três casos, **uma das cópias estava certa**: citava página e
item, enquanto a cópia do outro tópico citava o estudo original sem declarar
a mediação. O trabalho havia sido feito num tópico e não propagado ao outro,
e nada no sistema avisava.

O achado aqui não é sobre as três linhas: é sobre **catálogo mantido à mão
em arquivos paralelos derivar em silêncio**. A correção foi alinhar as três;
a contramedida foi um teste que recusa a divergência.

## A integridade das citações: o que foi lido no original

Esta seção existe para que o leitor não tenha de inferir nada, e é a
contrapartida de apoiar um catálogo numa obra que, ela mesma, agrega dezenas
de outras.

**Lido no original:** o texto integral de Sorva (2012), obtido do
repositório institucional aberto da Universidade Aalto; e as perguntas
citadas do FAQ do comp.lang.c, em `c-faq.com`. As citações dessas duas obras
são de primeira mão, e a frase citada foi localizada no texto.

**Citado `apud`:** os estudos que o Apêndice A agrega, a saber, du Boulay (1986),
Samurçay (1989), Sleeman et al. (1986), Soloway et al. (1982), Putnam et al.
(1986), Doukakis et al. (2007), Ma (2007) e Kaczmarczyk et al. (2010), são citados **pela mediação de Sorva (2012)**, com página e item. Os
artigos originais não foram abertos: estão em acervos de acesso restrito, e
a verificação de existência que se fez foi a do registro bibliográfico, não
a do texto. Cinco concepções do catálogo citam esses estudos, e cada uma
declara a mediação no próprio campo de fonte.

A consequência, dita de uma vez: **nenhuma afirmação deste trabalho atribui
a esses artigos conteúdo que não esteja no item do Apêndice A que os cita.**
Onde a citação anterior ia além disso (uma página e um código de tabela de um artigo não aberto), ela foi removida, e o caso está contado na seção
anterior.

**Não reaberto:** CERT C e CWE, que sustentam três concepções de grau `N`,
são fontes públicas e não foram reabertas nesta passada; a seção 11 do
FAQ ficou fora dela. Na conferência das referências deste trabalho
(19/11/2026), as duas foram abertas: os três itens da CWE (476, 252 e
415) e três das quatro regras do CERT C (EXP34-C, MEM30-C e MEM31-C)
conferem com o que o catálogo cita. A quarta, citada como MEM52-C, não
existe no padrão de C: é o número de uma regra do padrão de C++, sobre o
operador `new`. A citação passou à regra ERR33-C, que trata do erro
devolvido pelas funções da biblioteca, `malloc` entre elas. Os números
de 4.4 e 4.5 são os da passada de curadoria, e não mudam com isso.

Duas observações de forma, que mudam o que se pode afirmar. Primeira: a versão on-line do FAQ é **mais curta** que o livro de Summit (1996), como o próprio autor diz na página do FAQ; as citações deste trabalho são da versão on-line, por número de
pergunta, que é o que foi consultado, e não do livro. Segunda: os números
de página do Apêndice A referem-se ao texto extraído do PDF disponível
naquele repositório, e foram calibrados contra os marcadores de página do
próprio texto.

## O que esta curadoria não sustenta

Declarar o alcance é parte do método, não ressalva de rodapé.

1. **Nenhuma afirmação de prevalência.** Nem a classe 1 nem a classe 2
   autorizam dizer que tantos por cento dos estudantes sustentam uma dada
   concepção. O catálogo afirma que a concepção **existe e recorre**.
2. **Nenhuma afirmação sobre eficácia do instrumento.** Que as concepções
   estejam documentadas não diz que o sistema as detecte bem, nem que a
   refutação funcione. Isso exigiria coleta com participantes.
3. **Três hipóteses seguem hipóteses.** `type_is_a_hint`,
   `memoria_e_do_computador` e `memory_is_uniform` entram declaradas como
   tais, fora dos tópicos de coleta. O precedente desta auditoria diz o que
   tentar antes de aceitá-las: refazer a busca com outro vocabulário, que foi o que fez duas outras subirem de grau, e o que confirmou que para estas não
   há item.
4. **Uma concepção de grau `T` não cita obra nenhuma.**
   `heap_dies_with_function` tem apenas a analogia, declarada: em Java e
   Python, o que a função alocou e ninguém mais alcança desaparece sozinho.
   A busca foi refeita pelo vocabulário do fenômeno e registrada; não há
   item. O próprio campo de fonte diz que ela precisa de fonte ou desce para
   `E`.
5. **Uma citação do Sorva não traz frase entre aspas**, a de `uninitialized_is_null`, o que a torna não verificável pelo
   procedimento mecânico descrito acima, embora traga página e item.
6. **Três concepções de grau `N` citam CERT C e CWE**, e essas fontes não
   foram reabertas nesta passada; de cinco concepções que as citam, quatro foram conferidas pela citação do FAQ que trazem ao lado, e uma
   ficou sem conferência. Elas foram abertas depois, na conferência das
   referências (4.7).

## O catálogo é verificável por máquina, e é isso que se oferece

O apêndice de curadoria não foi digitado: é **gerado** do catálogo, por um
comando. Digitar 61 linhas à mão seria convidar justamente a divergência
entre documento e dado que este capítulo existe para medir; e a subseção
4.6.5, acima, mostra que essa divergência acontece mesmo quando quem mantém os
arquivos sabe do risco.

Sobre o catálogo correm travas automatizadas, que falham a suíte se a
propriedade deixar de valer. As principais:

**Quadro 4.7 — As principais travas automatizadas sobre o catálogo**

| trava | o que recusa |
| --- | --- |
| grau não diverge entre tópicos | a mesma concepção `D` num tópico e `L` noutro |
| `D` cita posição | grau `D` sem página nem item na fonte |
| `E` se declara | hipótese que não se anuncia como hipótese |
| `E` fora do piloto | hipótese em tópico escolhido para coleta (por dois caminhos independentes) |
| busca que falhou não vira conferência | linha que diga "conferida" para concepção que declara, em campo próprio, que não há item na literatura |
| a busca que falhou está declarada nas duas cópias | o campo que a declara presente num tópico e ausente no outro |
| sem chave duplicada no YAML | campo sobrescrito em silêncio por repetição |
| o capítulo não diverge do catálogo | número afirmado neste capítulo que o catálogo deixou de sustentar |

Três dessas travas nasceram de defeitos reais encontrados durante esta auditoria (a busca que falhou lida como conferência, o campo declarado em só uma cópia, a chave duplicada), e é por isso que estão aqui. Uma trava
escrita depois do erro que ela impede custa menos a justificar que uma
escrita por antecipação: sabe-se que o erro é possível, porque aconteceu.

A reprodução é um comando:

```
python scripts/gera_curadoria.py CAMINHO/DO/sorva2012.txt
```

O argumento é o texto integral da obra, baixado do repositório da Aalto. O
arquivo não entra no repositório do projeto porque é obra de terceiro; sem
ele o programa roda igual e o apêndice passa a declarar, linha por linha,
que não conferiu.

É essa verificabilidade, e não a quantidade de concepções, que o trabalho
oferece como contribuição deste capítulo. Um catálogo de 61 concepções
errôneas de ponteiros em C, com duas classes de fonte declaradas, posição
localizável onde o grau a exige, mediação de citação declarada onde ela
existe, e o todo conferível por um comando.

## Referências deste capítulo

Marcadas com ★ as obras lidas no original para esta curadoria. As demais são
citadas pela mediação de Sorva (2012), com página e item, conforme declarado
acima; os dados bibliográficos abaixo são os que constam da bibliografia daquela obra, com duas correções, anotadas nas entradas de Samurçay e de Sleeman et al.

★ SORVA, J. **Visual Program Simulation in Introductory Programming
Education.** Tese de doutorado — Aalto University School of Science,
Espoo, 2012. Disponível no repositório institucional da Universidade Aalto,
handle 123456789/3534.

★ SUMMIT, S. **C Programming FAQs: Frequently Asked Questions.** Reading:
Addison-Wesley, 1996. ISBN 0-201-84519-9. Versão on-line consultada em `c-faq.com`, mais curta que o livro.

★ KERNIGHAN, B. W.; RITCHIE, D. M. **The C Programming Language.** 2. ed.
Englewood Cliffs: Prentice Hall, 1988. *(citada como refutação, não como
fonte de concepção)*

DOUKAKIS, D.; GRIGORIADOU, M.; TSAGANOU, G. Understanding the Programming
Variable Concept with Animated Interactive Analogies. In: **Proceedings of
the 8th Hellenic European Research on Computer Mathematics & its
Applications Conference (HERCMA '07)**, 2007.

DU BOULAY, B. Some Difficulties of Learning to Program. **Journal of
Educational Computing Research**, v. 2, n. 1, p. 57–73, 1986.

★ HERMANS, F.; SWIDAN, A.; AIVALOGLOU, E.; SMIT, M. Thinking out of the
Box: Comparing Metaphors for Variables in Programming Education. In:
**Proceedings of the 13th Workshop in Primary and Secondary Computing
Education (WiPSCE '18)**. ACM, 2018. Art. 8, p. 1–8. DOI:
10.1145/3265757.3265765.

HOLLAND, S.; GRIFFITHS, R.; WOODMAN, M. Avoiding Object Misconceptions.
**SIGCSE Bulletin**, v. 29, n. 1, p. 131–134, 1997.

KACZMARCZYK, L. C.; PETRICK, E. R.; EAST, J. P.; HERMAN, G. L. Identifying
Student Misconceptions of Programming. In: **Proceedings of the 41st ACM
Technical Symposium on Computer Science Education (SIGCSE '10)**. ACM, 2010.
p. 107–111.

MA, L. **Investigating and Improving Novice Programmers' Mental Models of
Programming Concepts.** Tese de doutorado — Department of Computer &
Information Sciences, University of Strathclyde, 2007.

> **Nota de conferência.** A Tabela A.1 atribui 14 dos itens aqui usados a
> "Ma (2007)", e a bibliografia de Sorva (2012) identifica essa obra como a
> **tese de doutorado** acima — não como o artigo de SIGCSE de mesmo ano e
> tema assinado por Ma, Ferguson, Roper e Wood. O catálogo deste trabalho
> registrou a referência errada numa de suas versões, e a correção veio de
> ler a bibliografia da obra mediadora, não a memória de quem citava.

★ MITRE. **CWE: Common Weakness Enumeration.** Versão 5.0, 28 out. 2026.
Entradas CWE-252, CWE-415 e CWE-476. Disponível em:
`https://cwe.mitre.org`. Acesso em: 19 nov. 2026.

PUTNAM, R. T.; SLEEMAN, D.; BAXTER, J. A.; KUSPA, L. K. A Summary of
Misconceptions of High School BASIC Programmers. **Journal of Educational
Computing Research**, v. 2, n. 4, p. 459–472, 1986.

SAMURÇAY, R. The Concept of Variable in Programming: Its Meaning and Use in
Problem-Solving by Novice Programmers. In: SOLOWAY, E.; SPOHRER, J. C. (ed.). **Studying the Novice Programmer.** Hillsdale: Lawrence Erlbaum Associates, 1989. p. 161–178. *(A bibliografia de Sorva (2012) dá R. E. Mayer como organizador; o registro do livro na Open Library dá Soloway e Spohrer.)*

★ SEI. **SEI CERT C Coding Standard.** Pittsburgh: Software Engineering
Institute, Carnegie Mellon University, 2025. Regras ERR33-C, EXP34-C,
MEM30-C e MEM31-C. Disponível em:
`https://wiki.sei.cmu.edu/confluence/display/c`. Acesso em: 19 nov. 2026.

SLEEMAN, D.; PUTNAM, R. T.; BAXTER, J.; KUSPA, L. Pascal and High School Students: A Study of Errors. **Journal of Educational Computing Research**, v. 2, n. 1, p. 5–23, 1986. *(A bibliografia de Sorva (2012) traz duas entradas de Sleeman em 1986; uma repete título e dados de Putnam et al. (1986). Esta é a outra, a que o registro da Crossref confirma.)*

SOLOWAY, E.; EHRLICH, K.; BONAR, J.; GREENSPAN, J. What Do Novices Know
About Programming? In: BADRE, A.; SHNEIDERMAN, B. (eds.). **Directions in
Human–Computer Interaction.** Norwood: Ablex Publishing, 1982. p. 27–54.
