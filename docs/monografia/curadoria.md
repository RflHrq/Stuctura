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

## Problema da procedência

O sistema descrito nas seções anteriores formula, a cada pergunta respondida, uma hipótese diagnóstica com consequência imediata. Uma das hipóteses possíveis é a de que a pessoa sustenta determinada concepção errônea do catálogo, e é ela que seleciona a demonstração a ser apresentada.

A validade da hipótese depende de uma questão anterior, que o software não responde: a origem de cada concepção do catálogo. Se uma concepção tiver sido incluída apenas por parecer plausível ao autor, o sistema não estará diagnosticando uma concepção errônea documentada, e sim produzindo dados sobre uma suposição, com a mesma aparência de rigor do restante. Por essa razão, o projeto adota a seguinte regra: uma concepção sem procedência é tratada como hipótese do autor e não é incluída no catálogo como achado.

Esta seção trata dessa questão, que pode ser verificada sem a participação de estudantes. O instrumento não foi avaliado com estudantes, limitação declarada na Seção 7. O que se sustenta aqui é mais restrito e inteiramente verificável: o sistema afirma sobre concepções errôneas apenas o que a literatura registra e identifica explicitamente os casos em que não há registro.

## Graus de procedência

Cada concepção do catálogo possui um campo de procedência (`provenance`), que assume um de cinco valores. O grau não descreve a importância da concepção nem a confiança do autor nela: descreve o tipo de obra que a sustenta (Quadro 4.1).

**Quadro 4.1 — Graus de procedência**

| Grau | Significado |
| --- | --- |
| `D` | documentada: achado empírico, com fonte e posição localizável |
| `L` | registrada como erro comum em obra técnica |
| `T` | transposta de outra linguagem, com a analogia declarada |
| `N` | o erro consta de norma, como o padrão de codificação CERT C (SEI, 2025) e a *Common Weakness Enumeration* (CWE), da MITRE (2026), mas a concepção não |
| `E` | elaborada a partir do modelo de máquina: hipótese a testar |

Duas propriedades desse campo são relevantes para o método.

A primeira é que o grau constitui uma afirmação sobre a literatura, e não sobre o uso da concepção no sistema. Uma mesma concepção pode aparecer em mais de um tópico do domínio (o que ocorre com 14 delas), e o texto que a contextualiza varia de um tópico para outro; o grau, porém, deve ser o mesmo. Se uma concepção tem grau `D` em um tópico e `L` em outro, uma das duas afirmações é falsa, e essa diferença corresponde, em um trabalho acadêmico, à diferença entre citar e alegar. A auditoria encontrou três casos desse tipo (Seção 4.6.5), e um teste automatizado impede a divergência (Quadro 4.7).

A segunda é que o grau `E` é legítimo, desde que declarado. Uma hipótese do autor pode integrar o catálogo, mas não pode ser apresentada como achado. As quatro hipóteses do catálogo são identificadas como tais no próprio campo de fonte, e dois testes independentes asseguram que nenhuma delas apareça nos quatro tópicos selecionados para a futura coleta de dados com estudantes (kc_02, kc_07, kc_09 e kc_11), entre os quais estão os dois que o protocolo do estudo sugere para cada sessão (Apêndice A).

## Classes de fonte

O catálogo apoia-se em dois tipos de obra, aos quais se somam normas de codificação segura (Seção 4.7). A diferença entre eles não é de qualidade, mas do tipo de afirmação que cada um sustenta. Tratá-los como equivalentes constituiria um defeito metodológico; a declaração da classe, concepção por concepção, é o que torna o catálogo auditável.

### Classe 1: literatura de concepções errôneas (22 concepções)

A primeira classe compreende estudos empíricos com estudantes e revisões que os agregam. A obra principal é o Apêndice A de Sorva (2012), cuja Tabela A.1 relaciona 162 concepções errôneas levantadas na literatura de ensino de programação introdutória, cada uma com tópico, descrição e fonte. A ela se somam os estudos aos quais a própria tabela atribui os itens utilizados, citados neste trabalho por intermédio dela: du Boulay (1986), Soloway et al. (1982), Putnam et al. (1986), Sleeman et al. (1986), Samurçay (1989), Holland et al. (1997), Ma (2007), Doukakis et al. (2007) e Kaczmarczyk et al. (2010), todos *apud* Sorva (2012). Uma obra externa à Tabela A.1 também sustenta uma das concepções: Hermans et al. (2018) registram a ideia de que a variável armazena vários valores ou "lembra" os anteriores e a investigam em um experimento com 496 iniciantes.

Essa classe sustenta que a concepção foi observada em estudantes por pesquisadores que a investigaram.

### Classe 2: corpus de praticante (35 concepções)

A segunda classe é constituída pela lista de perguntas frequentes, ou *Frequently Asked Questions* (FAQ), do grupo comp.lang.c, que Steve Summit passou a publicar em 1990 no grupo de Usenet de mesmo nome (Summit, c2005). Uma versão ampliada da lista foi publicada em livro pelo próprio Summit; este trabalho utiliza a versão on-line. Uma das 35 concepções da classe, `malloc_always_succeeds`, não provém do FAQ: apoia-se apenas em uma regra do CERT C e em uma entrada da CWE, que registram o erro de utilizar o resultado de `malloc` sem conferi-lo, e tem por isso o grau `N` (Quadro 4.1); outras quatro citam essas normas junto com a pergunta do FAQ.

A inclusão dessa classe requer justificar por que um FAQ de linguagem constitui evidência sobre concepções errôneas, e não apenas sobre a linguagem C. A justificativa está no critério de inclusão adotado, que pode ser conferido por qualquer leitor: é incluída somente a pergunta cujo título formula, na voz de quem pergunta, a concepção ou a dúvida que a revela, de modo que a ideia que motivou a pergunta possa ser identificada no próprio título (Quadro 4.2).

**Quadro 4.2 — Exemplos de perguntas do FAQ cujo título formula a concepção na voz de quem pergunta**

| Pergunta | Título |
| --- | --- |
| 6.2 | "But I heard that `char a[]` was identical to `char *a`." |
| 6.9 | "Someone explained to me that arrays were really just constant pointers." |
| 6.4b | "So arrays are passed by reference, even though the rest of C uses pass by value?" |
| 4.11 | "Does C even have ``pass by reference''?" |

*Fonte: elaborado pelo autor, com títulos de perguntas de Summit (c2005).*

O catálogo, portanto, não infere a concepção a partir de uma explicação técnica: registra a formulação de quem pergunta. Para conferir a inclusão, basta consultar a pergunta e avaliar se o título formula a concepção ou apenas indica o assunto.

Do ponto de vista metodológico, o FAQ é tratado como fonte documental: um corpus de confusões autorrelatadas, de ocorrência natural, reunidas pelo editor desde 1990. O tratamento dado a esse corpus é o da análise documental.

Para as 34 concepções apoiadas no FAQ, essa classe sustenta que a confusão foi formulada por pessoas que programam em C e que consta de uma lista de perguntas frequentes do grupo. Não sustenta que a confusão seja frequente entre estudantes iniciantes, nem afirmações de prevalência: a população é autosselecionada (pessoas que escrevem para um grupo de Usenet, cuja experiência com a linguagem não é conhecida), e a seleção das perguntas reflete o julgamento do editor, e não uma medição. Por isso, nenhuma afirmação de proporção é extraída dessa fonte, e a ocorrência dessas concepções entre estudantes é uma das questões a verificar no estudo com participantes (Apêndice A).

### Necessidade da segunda classe

Seria razoável exigir que todo o catálogo se apoiasse na classe 1, de natureza empírica, e que a classe 2 fosse dispensada. Essa exigência foi testada contra a Tabela A.1 de Sorva (2012), item por item, e verificou-se que não pode ser satisfeita.

A Tabela A.1 possui um tópico dedicado a referências (`Refs`, com 17 dos 162 itens) e itens sobre memória e tempo de vida distribuídos por seis tópicos (`General`, `VarAssign`, `ObjClass`, `ObjState`, `OtherOOP` e `Misc`). Faltam-lhe, contudo, itens sobre os construtos próprios de C, como a alocação dinâmica, como mostra a contagem do Quadro 4.3, reprodutível por busca de termos no texto da tabela.

**Quadro 4.3 — Ocorrências de termos relativos à memória na Tabela A.1**

| Termo buscado na Tabela A.1 | Ocorrências |
| --- | --- |
| `malloc`, `free`, `deallocat`, `garbage` | 0 |
| `heap`, `stack` | 0 |
| `arithmetic`, `decay`, `dangling`, `sizeof` | 0 |
| `null` | 1: o item 54, "Null model of recursion" (Sorva, 2012, p. 362), que não trata de ponteiro nulo |
| `lifetime` | 1: o item 5, "Difficulties understanding the lifetime of values" (Sorva, 2012, p. 359) |
| `memory` | 7 |

*Fonte: elaborado pelo autor, por busca no texto de Sorva (2012).*

Não há, portanto, nenhum item sobre `NULL`, sobre `malloc` e `free`, sobre aritmética de ponteiros, sobre decaimento de array ou sobre a distinção entre pilha e monte.

Essa ausência não decorre de descuido da obra. A Tabela A.1 reúne concepções sobre o conteúdo comumente abordado em disciplinas introdutórias de programação e deixa de fora, por decisão declarada, as questões muito específicas de uma linguagem ou de uma ferramenta (Sorva, 2012, p. 358). Na revisão dos estudos em que o catálogo se baseia, os que nomeiam a linguagem tratam de BASIC e de Java (Sorva, 2012, p. 29-30). Um catálogo com esse recorte não documenta as confusões relativas justamente ao que distingue a linguagem C.

Conclui-se, assim, não que as 35 concepções da classe 2 sejam frágeis, mas que um catálogo de concepções errôneas para C requer uma segunda classe de fonte, a qual deve ser declarada como tal, com a indicação do que sustenta e do que não sustenta. Essa declaração é feita, concepção por concepção, na coluna de classe do Apêndice B.

## Procedimento de conferência

O padrão adotado pelo projeto, registrado no cabeçalho do primeiro catálogo de tópico, é o de que as fontes sejam conferidas na obra primária, e não citadas de memória. O resultado da aplicação desse padrão a cada concepção é apresentado no Quadro 4.4.

O quadro é exaustivo e mutuamente exclusivo: cada uma das 61 concepções figura em exatamente uma linha, que registra a verificação mais forte obtida para ela. A soma é, por construção, igual a 61. Um quadro que contasse as concepções que citam cada obra teria soma maior, pois uma concepção pode citar mais de uma obra, e não permitiria determinar quantas ficaram sem conferência.

**Quadro 4.4 — Forma de conferência de cada uma das 61 concepções**

| Forma de conferência | Concepções |
| --- | --- |
| conferida no texto integral de Sorva (2012), obtido do repositório aberto da Universidade Aalto (handle `123456789/3534`, bundle TEXT); a frase em inglês citada entre aspas foi localizada no texto da obra | 22 |
| conferida no índice do FAQ comp.lang.c: as seções 1, 4, 5, 6, 7 e 11 foram consultadas em `c-faq.com`; as perguntas citadas existem, e os títulos coincidem com os citados no catálogo; da pergunta 11.24, cuja resposta é citada, foi consultada também a página da resposta | 34 |
| conferida na página das normas: cita apenas uma regra do CERT C e uma entrada da CWE, cujas páginas foram consultadas (Seção 4.7) | 1 |
| sem item correspondente na literatura, com a busca declarada em campo próprio | 2 |
| sem fonte, por definição: hipótese declarada como tal | 2 |
| total | 61 |

As três primeiras linhas somam as 57 concepções conferidas na obra primária. As duas últimas correspondem às quatro hipóteses, para as quais a curadoria não afirma haver fonte. Quatro das 57 foram conferidas em uma segunda conferência, em 23/11/2026 (Seção 4.6.6).

Os estudos agregados pelo Apêndice A de Sorva (2012), relacionados na Seção 4.3.1, não figuram em linha própria porque não foram consultados diretamente. As concepções que os indicam como fonte o fazem pelo item de Sorva (2012) que os cita, com página e item, e estão contadas na primeira linha do quadro. A Seção 4.7 detalha esse ponto.

A conferência é automatizada sempre que possível: o programa que gera o Apêndice B extrai a frase entre aspas de cada citação e a procura no texto da obra, de modo que o resultado não depende do que está declarado no campo de fonte. Quando o programa é executado sem o texto da obra, o número de concepções conferidas cai de 57 para 35, e o apêndice passa a indicar, linha por linha, que a conferência não foi realizada.

## Resultado da curadoria

O Quadro 4.5 sintetiza o resultado da curadoria.

**Quadro 4.5 — Resultado da curadoria**

| Indicador | Valor |
| --- | --- |
| concepções distintas no catálogo | 61 |
| conferidas na obra primária | 57 |
| graus | `D` 6, `L` 33, `T` 15, `N` 3, `E` 4 |
| hipóteses `E` | 4, todas fora dos tópicos selecionados para a coleta |

## Achados da auditoria

Os achados descritos nesta seção têm interesse que ultrapassa o catálogo, pois dizem respeito ao método de construção de um catálogo a partir da literatura, e não à linguagem C.

### 1. Buscas realizadas com vocabulário ou item inadequado

Em três concepções, a busca inicial na obra não localizou o item correspondente, embora ele existisse (Quadro 4.6).

**Quadro 4.6 — Buscas que não localizaram o item e o item existente na obra**

| Concepção | Registro anterior no catálogo | Item existente na obra |
| --- | --- | --- |
| `pointer_has_no_address` | "procurei no catálogo do Sorva e não está lá: nenhum dos 162 itens afirma que a referência não ocupa espaço" | a segunda frase do item 14: "It is not stored inside the computer" (Sorva, 2012, p. 360). A busca utilizou os termos "referência" e "espaço", ao passo que o item trata de variável |
| `array_confused_with_cell` | "não tem fonte empírica, entra como hipótese" | o item 151, "Confusion between an array and its cell" (Sorva, 2012, p. 367), e o item 9, "A variable can hold multiple values at a time" (Sorva, 2012, p. 359). A busca utilizou o termo "array", ao passo que o item 9 trata de variável e o item 151 pertence ao tópico `Misc` |
| `assignment_symmetric` | citava o item 11, com a aproximação declarada: "o 11 é sobre a direção invertida, e esta concepção é sobre os dois lados" | o item 12, imediatamente posterior ao 11: "Primitive assignment works both directions (swaps)" (Sorva, 2012, p. 359). O item corresponde ao rótulo da concepção |

*Fonte: elaborado pelo autor, com trechos de Sorva (2012).*

Nos três casos, a busca refeita com outro vocabulário localizou o item, e é esse o item citado no catálogo, com o grau que ele sustenta: `T` para a primeira concepção e `D` para as outras duas. Nenhuma das três classificações depende de julgamento intuitivo.

Desses casos decorre uma recomendação de método, que pode ser replicada: a busca deve ser orientada pelo fenômeno, e não pelo termo da linguagem em estudo. Quando se procura, em uma fonte, uma concepção errônea da linguagem X, o item pode estar redigido no vocabulário da linguagem Y, o que necessariamente ocorre quando a fonte foi produzida a partir de estudos em Y.

O terceiro caso acrescenta um segundo princípio, relativo à transparência da citação: foi a aproximação declarada que permitiu localizar o erro. A citação indicava em que o item diferia da concepção, e essa diferença apontou para o item vizinho. Uma citação que omite a discrepância não oferece esse indício e permanece incorreta sem que se perceba.

### 2. Citação associada a item incorreto

A citação da concepção `pointer_is_data` remetia ao item 14 de Sorva (2012, p. 360), que trata de a variável ser um par de nome e valor, e não de ponteiros. A concepção consta do item 65: "A (non-primitive Java) variable does not hold a reference but a set of object properties" (Sorva, 2012, p. 362). A obra citada estava correta, mas o item não, e esse tipo de erro somente pode ser identificado com a consulta à obra.

O mesmo tipo de erro ocorre na identificação das obras mediadas. A Tabela A.1 atribui nove de seus itens a "Ma (2007)", e a bibliografia de Sorva (2012) traz duas obras cujo primeiro autor tem esse sobrenome: uma tese de doutorado de 2007, de autoria única, e um artigo de 2011, com três coautores. É a bibliografia que identifica "Ma (2007)" como a tese. A citação de uma obra mediada exige, portanto, a consulta à bibliografia da obra mediadora, não bastando o reconhecimento do sobrenome e do ano.

### 3. Fontes que sustentam mais de uma concepção

As concepções `memory_is_by_name` e `pointer_has_no_address` derivam das duas frases do mesmo item 14 de Sorva (2012, p. 360). No FAQ (Summit, c2005), a pergunta 7.21 sustenta três concepções de um tópico; a 7.22, duas de outro; e a 4.9, duas de um terceiro.

Não se trata de economia de fontes: uma resposta de FAQ frequentemente trata de mais de uma confusão, e separá-las constitui trabalho de curadoria, e não apenas de leitura.

### 4. Citações não sustentadas pela obra citada

A regra aplicada é a seguinte: se a fonte não pode ser verificada, procura-se o item correspondente na obra; se ele não existir, a citação não permanece no catálogo. Cinco casos foram identificados:

- Atribuição incorreta. A citação de `declaration_allocates` atribuía a concepção a Kaczmarczyk et al. (2010), com página e código de tabela que somente poderiam ser conferidos com a consulta ao artigo. O item que registra essa concepção, o de número 92, atribui-a a Ma (2007 apud Sorva, 2012, p. 364), e é essa a atribuição citada no catálogo. Como a concepção pertence a um dos tópicos selecionados para a coleta de dados, a atribuição tem consequência prática.
- Concepção sem item na obra. Para `memory_is_uniform`, a citação indicava página e tabela de um artigo sem cópia de acesso aberto. Na busca item por item no Apêndice A, não se encontrou item sobre a memória como região única, sem regras distintas de tempo de vida; o mais próximo, o item 5 (Sorva, 2012, p. 359), refere-se à *dificuldade* com o tempo de vida, que é outro fenômeno. No catálogo, a concepção é uma hipótese declarada, de grau `E`.
- Refutação no lugar da fonte. Para `declaration_zeroes`, o campo de fonte trazia a citação de um livro-texto da linguagem C, apresentado no próprio campo como a obra que contradiz a concepção; tratava-se, portanto, da refutação, e não do registro de que alguém a sustenta. O catálogo distingue os dois papéis: a fonte é o item 10 (Sorva, 2012, p. 359), e a refutação registrada é o padrão da linguagem, segundo o qual o valor de um objeto de duração automática não inicializado explicitamente é indeterminado (ISO/IEC, 2011, p. 140).
- Código interno de artigo não consultado. A citação de `no_value_no_memory` continha o código "(PVR2)", pelo qual Kaczmarczyk et al. (2010) identificam o achado e que somente pode ser verificado com a consulta ao artigo. O catálogo cita o item 22 (Sorva, 2012, p. 360).
- Aproximação declarada que indicou o item correto. É o caso de `assignment_symmetric`, descrito na Seção 4.6.1 por constituir também um resultado de método.

### 5. Procedência divergente entre tópicos

Quatorze concepções aparecem em mais de um tópico, e cada ocorrência possui campo de fonte próprio, preenchido manualmente. Três delas divergiam quanto ao grau e, em dois desses três casos, uma das ocorrências estava correta: citava página e item, ao passo que a ocorrência do outro tópico citava o estudo original sem declarar a mediação. A conferência havia sido realizada em um tópico e não fora propagada ao outro, sem que o sistema acusasse a inconsistência.

O achado relevante não se restringe a essas três concepções: um catálogo mantido manualmente em arquivos paralelos tende a divergir sem que isso seja percebido. As ocorrências estão uniformizadas, e um teste automatizado impede novas divergências (Quadro 4.7).

### 6. Defeitos de registro identificados na segunda conferência

Em uma segunda conferência, realizada em 23/11/2026 sobre as quatro concepções que a curadoria inicial não havia conferido integralmente, foram identificados dois defeitos de registro, ambos corrigidos.

O primeiro é uma menção contada como citação. O campo de fonte de `pointer_is_pointless` menciona Sorva (2012) para registrar que a concepção não consta daquela obra; a fonte da concepção é a pergunta 4.1 do FAQ (Summit, c2005). O programa que gera o Apêndice B classificava a fonte pela presença do nome da obra no campo e, por essa razão, incluía a concepção na classe 1 e procurava no texto de Sorva (2012) uma frase que pertence ao FAQ. O programa passou a considerar aquela obra como fonte somente quando a citação indica página ou item, e a contagem das classes foi corrigida de 23 e 34 para 22 e 35 concepções.

O segundo é uma citação encurtada sem indicação de corte. A frase da pergunta 11.24 do FAQ citada em `voidptr_arith_ok` omitia um trecho interno da resposta; a citação passou a reproduzir o texto integral da página.

As outras duas concepções exigiram apenas completar o registro: `uninitialized_is_null` passou a trazer a frase do item 10 (Sorva, 2012, p. 359), que o programa localiza no texto da obra, e `malloc_always_succeeds`, que cita apenas normas, foi conferida nas páginas da regra ERR33-C do CERT C e da entrada 252 da CWE.

## Integridade das citações

Esta seção explicita o que foi lido no original, em contrapartida ao fato de o catálogo se apoiar em uma obra que, por sua vez, agrega dezenas de outras.

Foram lidos no original o texto integral de Sorva (2012), obtido do repositório institucional aberto da Universidade Aalto; as perguntas citadas do FAQ do comp.lang.c, consultadas em `c-faq.com`; e o artigo de Hermans et al. (2018). As citações dessas obras são diretas, e a frase citada foi localizada no texto.

Os estudos agregados pelo Apêndice A (Seção 4.3.1) são citados *apud* Sorva (2012), com página e item, e por essa razão não constam da lista de referências, que relaciona apenas as obras consultadas. Os documentos originais não foram consultados, por se encontrarem em acervos de acesso restrito; a verificação realizada limitou-se à existência do registro bibliográfico, sem acesso ao texto. Cada concepção que indica um desses estudos como fonte o faz pelo item de Sorva (2012) que o cita, com página e item, de modo que a mediação fica registrada no próprio campo de fonte.

Em consequência, nenhuma afirmação deste trabalho atribui a esses estudos conteúdo que não conste do item do Apêndice A que os cita.

As normas CERT C (SEI, 2025) e CWE (MITRE, 2026), citadas pelas três concepções de grau `N` e por duas de grau `L`, foram conferidas separadamente da curadoria, na conferência das referências deste trabalho: as três entradas da CWE (252, 415 e 476) e as quatro regras do CERT C (ERR33-C, EXP34-C, MEM30-C e MEM31-C) correspondem ao que o catálogo cita. Na curadoria inicial, a concepção que cita apenas normas havia ficado sem conferência, e a seção 11 do FAQ não havia sido incluída; as duas lacunas foram fechadas na segunda conferência, de 23/11/2026 (Seção 4.6.6), e os Quadros 4.4 e 4.5 apresentam o resultado posterior a ela.

Duas observações de forma delimitam o que se pode afirmar. A primeira é que a versão on-line do FAQ (Summit, c2005) é mais curta do que o livro publicado pelo mesmo autor, como ele próprio informa na página do FAQ; as citações deste trabalho referem-se à versão on-line, por número de pergunta, que foi a versão consultada. A segunda é que os números de página do Apêndice A referem-se ao texto extraído do arquivo em *Portable Document Format* (PDF) disponível no repositório mencionado e foram calibrados com base nos marcadores de página do próprio texto.

## Limites da curadoria

A delimitação do alcance da curadoria integra o método. Três limites devem ser considerados:

1. Não há afirmação de prevalência. Nem a classe 1 nem a classe 2 autorizam afirmar que determinada proporção dos estudantes sustenta uma dada concepção. O catálogo afirma que a concepção está registrada na literatura ou no corpus de praticantes, e não que seja frequente entre estudantes.
2. Não há afirmação sobre a eficácia do instrumento. O fato de as concepções estarem documentadas não implica que o sistema as detecte adequadamente nem que a refutação produza efeito, o que exigiria coleta de dados com participantes.
3. Quatro concepções permanecem como hipóteses. São elas `memory_is_uniform`, `type_is_a_hint`, `memoria_e_do_computador` e `heap_dies_with_function`, declaradas como tais e ausentes dos tópicos de coleta. A última apoia-se em uma analogia declarada (em Java e em Python, a memória alocada por uma função e que deixa de ser alcançável é liberada automaticamente), mas nenhuma obra consultada registra a concepção; por essa razão, é classificada como hipótese, e não como transposição. A auditoria indica o procedimento a adotar antes de aceitá-las: refazer a busca com outro vocabulário, procedimento que localizou o item de duas concepções antes consideradas hipóteses (Seção 4.6.1). Para duas das quatro, a busca sem resultado está declarada em campo próprio; as outras duas foram elaboradas a partir do modelo de máquina e não têm busca declarada.

## Verificação automatizada do catálogo

O Apêndice B não foi redigido manualmente: é gerado a partir do catálogo por um comando. A digitação de 61 linhas favoreceria exatamente a divergência entre documento e dado que esta seção se propõe a controlar, e a Seção 4.6.5 mostra que essa divergência ocorreu.

O catálogo é submetido a verificações automatizadas, que fazem a suíte de testes falhar caso a propriedade correspondente deixe de valer. As principais são apresentadas no Quadro 4.7.

**Quadro 4.7 — Principais verificações automatizadas do catálogo**

| Verificação | Situação rejeitada |
| --- | --- |
| grau uniforme entre tópicos | a mesma concepção com grau `D` em um tópico e `L` em outro |
| grau `D` com posição | grau `D` sem página nem item na fonte |
| grau `E` declarado | hipótese que não se identifica como hipótese |
| grau `E` fora dos tópicos de coleta | hipótese em tópico selecionado para a coleta (verificado por dois caminhos independentes) |
| busca sem resultado não conta como conferência | linha que indique "conferida" para concepção que declara, em campo próprio, não haver item na literatura |
| busca sem resultado declarada em todas as ocorrências | campo que a declara presente em um tópico e ausente em outro |
| ausência de chave duplicada no YAML | campo sobrescrito por repetição, sem aviso |
| consistência entre o texto e o catálogo | número afirmado nesta seção que o catálogo deixou de sustentar |

A reprodução da curadoria requer um único comando:

```
python scripts/gera_curadoria.py CAMINHO/DO/sorva2012.txt
```

O argumento é o texto integral da obra, obtido do repositório da Universidade Aalto. O arquivo não integra o repositório do projeto por se tratar de obra de terceiro; na sua ausência, o programa é executado normalmente, e o apêndice passa a indicar, linha por linha, que a conferência não foi realizada.

A contribuição desta seção reside nessa verificabilidade, e não no número de concepções: um catálogo de 61 concepções errôneas sobre ponteiros em C, com duas classes de fonte declaradas, posição localizável sempre que o grau a exige, mediação de citação declarada onde existe, e conferível em seu conjunto por um único comando.

## Referências deste capítulo

Lista de trabalho, que não vai para o PDF. Marcadas com ★ as obras consultadas, que constam da lista de referências do trabalho. As demais são citadas *apud* Sorva (2012), com página e item, e por isso não entram na lista de referências (NBR 10520/2023; manual de normalização da UFV, 2026); os dados bibliográficos abaixo são os que constam da bibliografia daquela obra, com duas correções, anotadas nas entradas de Samurçay e de Sleeman et al.

★ SORVA, J. **Visual Program Simulation in Introductory Programming
Education.** Tese (Doutorado) – Aalto University School of Science,
Espoo, 2012. Disponível no repositório institucional da Universidade Aalto,
handle 123456789/3534.

★ SUMMIT, S. **comp.lang.c frequently asked questions.** [S. l.], c2005. Versão em hipertexto da lista de perguntas frequentes do grupo comp.lang.c, mais curta que o livro *C programming FAQs*, do mesmo autor (Addison-Wesley, ISBN 0-201-84519-9). Disponível em: `https://c-faq.com/`. Acesso em: 19 nov. 2026.

★ ISO/IEC. **Programming languages**: C. [S. l.], 2011. Committee draft N1570. *(citada como refutação da concepção `declaration_zeroes`, p. 140, e não como fonte de concepção)*

KERNIGHAN, B. W.; RITCHIE, D. M. **The C Programming Language.** 2. ed.
Englewood Cliffs: Prentice Hall, 1988. *(era a refutação registrada no
catálogo; não foi aberta na conferência das referências, e por isso saiu
do texto e da lista de referências em 23/11/2026)*

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
Programming Concepts.** Tese (Doutorado) – Department of Computer &
Information Sciences, University of Strathclyde, 2007.

> Nota de conferência: a Tabela A.1 atribui nove itens a "Ma (2007)"
> (11, 64 a 68, 80, 92 e 148), e a bibliografia de Sorva (2012) identifica
> essa obra como a tese de doutorado acima. A outra obra de Ma na
> bibliografia é um artigo de 2011, com Ferguson, Roper e Wood. Até
> 23/11/2026 esta nota dizia "14 itens" e falava de um artigo de 2007 no
> SIGCSE, que não foi aberto nem consta da bibliografia da tese.

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
