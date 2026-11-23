# Processo — da ideia ao código

**Ideia em uma frase:** um sistema que trata conhecimento como um grafo de
premissas, descobre em qual premissa a pessoa está errada e a conduz, pelo
grafo, até a premissa correta.

**Fase atual:** **fechar o instrumento antes de ensaiar com gente** —
decisão do dono, e ela inverte a ordem que este documento vinha
propondo. O ensaio continua preparado ([roteiro](ensaio-roteiro.md),
`scripts/ensaio.sh`, seis portões verdes), e continua sendo a única fonte
de evidência da CS-11 e da CS-12 — mas não é o próximo passo: o próximo
passo é o sistema ficar redondo.

O que a [varredura dos treze](#a-varredura-dos-treze--o-portão-de-conteúdo-fora-do-kc_02)
disse que falta, em ordem: a **quarta persona** (o portão de ponta a ponta
nunca diz "não sei", e a CS-4 nunca roda pela tela), e depois os dois P1
de software que a revisão final deixou abertos — a exclusão que não
alcança as cópias (P1-2, LGPD) e os dois commits que não restauram no
Windows (P1-4). A **descida** segue sendo o maior buraco conceitual
(1 cadeia de 79 crenças, desligada por padrão), e é conteúdo de curadoria,
não etapa de engenharia.

Antes disso, **ciclo 3 fechado** ([tarefas](tasks-ciclo-3.md)). As três
decisões que a medição do kc_02 deixou em aberto eram de motor, e foram
resolvidas: a crença já tratada sai da cédula, a premissa não medida diz o
nome, e a confiança ficou onde decide alguma coisa. Quem erra e aprende
agora termina com **todas** as premissas medidas — era 4 em 10 sem medida.

Antes disso, o **ciclo de conteúdo**: o kc_02 ganhou grafo, crenças
conferidas na fonte e banco de 36 atividades, e a
[medição com o caminhante](#o-que-a-medição-do-kc_02-mostrou) derrubou a
hipótese de que mais itens fechariam o buraco da CS-10.

Antes disso: **revisão final total feita**, veredito
[**NO-GO para a coleta com participantes**](revisao-final.md) — GO para
seguir o desenvolvimento e ensaiar com você mesmo. O ciclo 1 fechou com
treze tarefas; a [revisão](revisao-ciclo-1.md) deu **parcial**, com dois P1
e seis P2; o [ciclo 2](tasks-ciclo-2.md) fechou os oito em seis tarefas; a
revisão final achou um **P0** (fechado nela, `d19f03b`) e quatro P1, dois
dos quais não são software.

**Reformulação, não recomeço:** o motor atual (`mvp/`) e o antigo (`engine/`)
ficam onde estão, versionados. O que está em reconstrução é o CONCEITO de
aprendizagem — o que conta como aprender, como o material é feito e que
formas de exercício existem.

## Perfil do projeto

Montado do código e do histórico; só o que o código não responde virou
pergunta.

| Item | Resposta | Auxiliar |
| --- | --- | --- |
| Tipo | aplicativo web local de aprendizagem, instrumento de um TCC | — |
| Tem telas? Quem usa | sim: estudantes de graduação (participantes) e o pesquisador | **U** |
| Dados pessoais | respostas de participantes sob código anônimo (P01…); áudio de pensar em voz alta, previsto | **G**, **P** |
| Dinheiro | não | — |
| Consultas ou relatórios grandes | não: dezenas de registros por sessão | D não aplicável |
| Identidade visual a criar | não: uso em laboratório, sem vitrine | direção de arte mínima |
| Banco de dados | SQLite (sistema antigo) e JSONL append-only (MVP) | **M**, leve |
| Integrações externas | nenhuma | X não aplicável |
| Onde roda e quem opera | máquina do pesquisador, offline, ele mesmo opera | **I**, leve |
| Páginas públicas | não | W não aplicável |
| Quem mais usa ou opera | participantes; o orientador acompanha | **T** |
| Usuários reais depois da entrega | só durante a coleta; não é produto em produção | **E**, leve |

**Auxiliares que entram:** S (sempre), U, G, P, M, I, T, E.
**Não aplicáveis:** D (sem operação crítica de volume), X, W.

**Arquivo de lições do usuário:** não existe. Ofereço criar no fechamento
(L — licoes-entre-projetos).

## O que já existe, e que não se joga fora

| Ativo | Onde | Estado |
| --- | --- | --- |
| Grafo de premissas de ponteiros em C | `domain/c_pointers/` | 12 tópicos, 93 nós, 34 crenças com procedência |
| Domínio da unidade, por tópico | `mvp/dominio/` | 5 tópicos: kc_00 (5 nós, 20 itens), kc_01 (5, 35), kc_02 (6, 60), kc_03 (6, 42), kc_04 (6, 42) |
| Motor do laço identifica → refuta → treina → confirma | `mvp/motor.py` | 28 testes |
| Motor antigo (dois braços, nomeação tardia, log reconstruível) | `engine/`, `store/`, `api/` | 252 testes |
| Documentação do TCC | `docs/` | plano, fundamentação, requisitos, arquitetura, curadoria |

## Decisões

| # | Decisão | Quando | Por quê |
| --- | --- | --- | --- |
| 1 | O alvo da medição deixa de ser "aprendizagem" e passa a ser **mudança conceitual observada** dentro da sessão | Grill, rodada 2 | dentro de uma sessão o que se observa é desempenho, não aprendizagem (Soderstrom & Bjork, 2015) |
| 2 | Entra a **camada de razão**: cada atividade pergunta o que acontece E por quê | Grill, rodada 3 | é o que separa chute, vacilo e crença — instrumento de camadas, literatura de diagnóstico de concepções |
| 3 | Os estados de uma premissa passam de 3 para **5** (confirmada, lacuna, crença, falso positivo, falso negativo) | Grill, rodada 3 | consequência direta da decisão 2 |
| 4 | Adaptação ao estilo Duolingo entra como **força da premissa** dentro da sessão, não como repetição espaçada entre dias | Grill, rodada 3 | repetição espaçada exige medir retenção, que o desenho do estudo exclui |
| 5 | O instrumento tem **três camadas** (resposta, razão, confiança uma vez no fim), não quatro | Grill, rodada 4 | duas confianças cansam e não separam nenhum estado a mais |
| 6 | O **teach-back** entra, no fim da unidade, emparelhado com uma frase escrita antes de começar | Grill, rodada 4 | é o antes-e-depois nas palavras da própria pessoa — o dado mais forte que um estudo deste tamanho produz |
| 7 | Primeiro ciclo leva **"não sei", frase do começo/fim e painel do pesquisador**; **montar a cadeia** fica para o segundo | Grill, rodada 4 | as três primeiras mexem na qualidade do dado e são baratas; a quarta é formato novo de exercício e custa interface |
| 8 | A **razão é uma segunda tela**: a resposta tranca antes de as razões aparecerem; a confiança vem uma vez, no fim | Research | razão errada é enunciado de crença — lida antes, dá a pista e muda a resposta de quem ia acertar |
| 9 | A razão errada é **qualquer crença do grafo**, e a crença ativa é registrada **no nó que ela nega**, não no nó do item | Research | os distratores de B1 já apontam para `no_value_no_memory`, que nega B2; atribuir ao nó certo é diagnóstico melhor |
| 10 | O **painel do pesquisador lê o log**, em processo separado, nunca a sessão viva | Research | não pode derrubar a sessão de um participante, e força o log a bastar — a mesma tarefa da reconstrução do estado |
| 11 | *Acho que sei*, o meio da escala, puxa para o **lado conservador de cada linha**: não confirma acerto, e não livra erro de refutação | Prototype | a tabela tinha dois níveis e a escala tem três; o protótipo obrigou a decidir |
| 12 | A confiança fica em **tela própria**, não no pé da tela da razão | PRD | o passo a mais compra independência entre as camadas, que é o que sustenta a classificação na banca |
| 13 | O falso positivo é **contado** à pessoa: "a resposta está certa, a explicação leva a outro lugar" | PRD | calar desperdiça o único momento em que ela percebe a própria rota torta; trocar custa uma linha depois do ensaio |
| 14 | Parâmetros aceitos como propostos: 2 superfícies, 2 falsos positivos até virar crença, treino 2/4/2, 2+2 itens por nó | Issues | nenhum deles muda arquitetura; são constantes no topo do motor, e o ensaio ajusta |
| 15 | O conhecimento tem **dois níveis de grafo**: premissas dentro de uma KC (interno) e KCs ligadas por pré-requisito (externo) | Issues | é a tese do usuário, e o grafo externo já existe em `kcs.yaml` com 12 KCs |
| 16 | O **reteste de uma crença acontece na abertura da KC seguinte**, como checagem de pré-requisito | Issues | a KC seguinte depende das premissas da anterior; a mesma pergunta serve ao reteste e ao pré-requisito, sem tela extra |
| 17 | O domínio do TCC é **ponteiros em C**; o kc_00 (declaração de variáveis) é pré-requisito, não o objeto da medida | ciclo de conteúdo | medir mudança conceitual sobre variáveis não responde a pergunta do trabalho |
| 18 | A coleta usa **um KC por sessão** | ciclo de conteúdo | medido: um tópico consome de 37 a 149 passos, e o orçamento do PRD é de 20 a 30 min. Como corolário, a decisão 16 não se aplica a um estudo de sessão única, e o reteste de fim de sessão da T12 é o desenho certo |
| 19 | **Uma crença por nó, sem exceção** | ciclo de conteúdo | a atribuição vem da camada 2, então nó sem crença própria nunca recebe atribuição. O kc_02 antigo tinha três nós de base sem crença |
| 20 | **Um laço por premissa por sessão** (`tratado()`): o nó que confirmou ou fechou `em_aberto` não volta ao laço, nem pela atribuição cruzada | ciclo da cauda | o motor já tinha três tetos com esse argumento escrito; faltava o quarto. Sem ele um nó levava 16 telas de treino numa sessão, e com ele a cauda desaparece e o pior caso deixa de ter premissa sem medida |
| 20 | Em todo item de diagnóstico, **um distrator aponta a crença do próprio nó e outro a de um vizinho** | ciclo de conteúdo | `motor.razoes_de` monta as razões das alternativas do próprio item: item sem crença do nó manda toda razão errada para outro lugar |
| 21 | O carregador aceita **mais de um tópico** (`carrega(topico=...)`, `STRUCTURA_TOPICO`) | ciclo de conteúdo | os nomes `*_kc00.yaml` estavam fixos no código |

## Perguntas em aberto

Nenhuma bloqueia a fase 4.

1. Quantos tópicos a coleta usa, e em que ordem.
2. Onde fica o reteste do fim da sessão enquanto só o kc_00 existe.
3. Quem classifica as frases abertas do teach-back, e com que codebook.
4. A crença nova de B1 (procedência E) fica como hipótese a testar, ou você
   quer procurar fonte empírica antes da coleta.
5. Quais premissas de uma KC sustentam quais premissas da seguinte (a
   aresta fina do grafo externo). Curadoria de domínio, com o usuário.
6. ~~O que encerra a unidade quando a pessoa não muda de ideia em nenhuma
   premissa.~~ **Fechada**: virou o quarto teto, `tratado()` — um laço por
   premissa por sessão. Ver "O quarto teto", no fim deste documento.
7. Se o kc_04 fica com 6 nós ou volta aos 8 da curadoria. Voltar custa
   quatro crenças (que seriam `E`) e 14 atividades.
8. ~~O kc_08 (alocação dinâmica) não existe, e o kc_09 o declara como
   pré-requisito.~~ **Fechada**: o kc_08 foi construído. Ver "Ciclo de
   conteúdo — o kc_08", no fim deste documento.
9. ~~113 passos cabem na sessão de coleta?~~ **Fechada**: a pergunta
   comparava objetos diferentes. A unidade do plano é UMA premissa, custa
   14 telas (10 dos quatro estágios dele), e o que faltava era poder rodar
   uma sessão de duas premissas em vez do tópico inteiro —
   `STRUCTURA_PREMISSAS`. Ver "A pergunta 9 resolvida", no fim deste
   documento.
10. ~~As duas `E` do kc_02.~~ **Fechada**: as duas tinham fonte, e a
   busca anterior errou — uma de vocabulário, a outra de catálogo. Os
   quatro pilotos ficaram sem nenhuma `E`. Ver "A pergunta 10 resolvida",
   no fim deste documento.
11. ~~A suíte do MVP leva 3 minutos.~~ **Fechada, e era erro de
   medição meu.** A suíte roda em **30 segundos**, e a varredura de
   tópicos custa 6. Ver "A pergunta 11 era um erro de medição", no fim
   deste documento.

## Artefatos

| Fase | Artefato | Estado |
| --- | --- | --- |
| 1 Grill | `docs/context.md` | **pronto** — glossário fechado |
| 1 Grill | `docs/problema.md` | **pronto** — critério, instrumento e escopo do 1º ciclo |
| 2 Research | `docs/research.md` | **pronto** — linha de base, 6 achados, o que serve e o que muda |
| 3 Prototype | `prototipo/telas-novas.html` | **pronto** — fluxo clicável, descartável, fora de `mvp/` |
| 4 PRD | `docs/PRD.md` | **pronto** — 12 critérios de sucesso, parâmetros aceitos |
| 5 Issues | `docs/tasks.md` | **pronto** — 13 tarefas, da T0 à T12 |
| 7 Review | `docs/revisao-ciclo-1.md` | **pronto** — parcial, 2 P1 e 6 P2 |
| 5 Issues (2º ciclo) | `docs/tasks-ciclo-2.md` | **pronto** — 6 tarefas, R1 a R6 |
| 7 Revisão final | `docs/revisao-final.md` | **pronto** — NO-GO para a coleta, com a lista do que o levanta |
| conteúdo | `docs/linguagem.md` | **pronto** — contrato de linguagem e três formatos propostos |
| conteúdo | `docs/revisao-crencas-kc02.md` | **pronto** — crenças conferidas na obra primária |
| conteúdo | `mvp/dominio/*_kc02.yaml` | **pronto** — 6 nós, 6 crenças, 36 atividades |
| 5 Issues (3º ciclo) | `docs/tasks-ciclo-3.md` | **pronto** — 3 tarefas, C1 a C3 |
| ensaio | `docs/ensaio-roteiro.md` | **pronto** — roteiro, folha de observação, o que não dizer |

## Fase 6 — as tarefas, uma por commit

Cada linha é um commit. "Sabotagem" é a conferência de que o teste morde:
quebrar de propósito a regra que ele defende tem de derrubá-lo.

| Tarefa | Commit | O que entregou | Testes do MVP | Sabotagem |
| --- | --- | --- | --- | --- |
| T0 | `e11cc51` | `scripts/verify.sh`: segredos antes dos testes | 28 | segredo plantado faz falhar |
| T1 | `26d281b` | a crença desce da atividade para a alternativa | 42 | sim |
| T2 | `6608de0` | a camada da razão; a resposta tranca | 54 | sim |
| T3 | `2905f99` | a confiança em tela própria, em toda atividade | 60 | sim |
| T4 | `d4aaa95` | os cinco estados; a crença no nó que ELA nega | 70 | sim — **2 testes aposentados e 2 reescritos**, com aprovação |
| T7 | `398564b` | o mapa com os cinco estados e o caso cruzado | 74 | sim |
| T5 | `0ebf464` | "não sei" nas três camadas | 80 | **fraca**, declarada: o curto-circuito da lacuna derruba 1 teste só |
| T6 | `4a61caa` | o falso positivo traz outra superfície | 86 | sim — o primeiro teste **não mordia**, reescrito |
| T9 | `85c3d42` | o teach-back do começo e do fim | 95 | sim |
| T10 | `53ef20b` | a sessão reconstruída pelo log (CS-6) | 110 | sim — 6 de 6 |
| T11 | `97a1efd` | o painel do pesquisador, só leitura (CS-7) | 126 | sim — 7 de 7 |
| T8 | `b73269d` | a força da premissa escolhe o próximo item | 150 | sim — 11 de 11, **uma não mordia** e foi corrigida |
| T12 | — | o reteste do fim da sessão | 167 | sim — 11 de 11, **uma não mordia** e foi corrigida |

A coluna conta funções `def test_` em `mvp/`, apuradas com `git grep` em
cada commit. O pytest coleta mais do que isso porque quatro testes são
parametrizados: hoje são 110 funções e **119 casos**, mais 252 da suíte
antiga.

**A fase 6 fechou:** T0 a T12, treze tarefas, treze commits. Fica em
aberto uma lacuna de escopo registrada e **não** transformada em tarefa
por conta própria: o caminho "lacuna → constrói" aparece no fluxo do PRD
e não tem tarefa de T1 a T12. E fica a decisão de conteúdo que a T12
levantou: o banco de itens não alimenta o reteste. E uma lacuna de escopo
registrada e **não** transformada em tarefa por conta própria: o caminho
"lacuna → constrói" aparece no fluxo do PRD e não tem tarefa de T1 a T12.

## Ciclo 2 — os oito achados da revisão

| Tarefa | Commit | Fecha | Testes do MVP | Sabotagem |
| --- | --- | --- | --- | --- |
| R1 | `d74cff7` | P1-A, P2-A | 185 | sim — 6 de 6 |
| R2 | `f88458c` | P1-B | 191 | sim — 4 de 4 |
| R3 | `bd70bfc` | P2-B | 194 | sim — 4 de 4, **uma não mordia** |
| R4 | `47b0526` | P2-C | 197 | sim — 5 de 5 |
| R5 | `da92f9a` | P2-D | 200 | sim — 4 de 4 |
| R6 | `75ac709` | P2-E, P2-F | 214 | sim — 9 de 9, **duas não mordiam** |

Em três das seis tarefas a sabotagem pegou um teste que passava sem
morder. É a conta que justifica a prática.

## Vereditos das auxiliares

| Fase | Auxiliar | Modo | Veredito |
| --- | --- | --- | --- |
| 2 | S (segurança, camadas 1 e 2) | focada, método aplicado direto | **passou** — nenhum segredo em arquivo versionado; token e logs fora do versionamento |
| 2 | U (interface) | **não executada** | as telas mudam na próxima fase; auditar o que será redesenhado é trabalho jogado fora |
| 2 | G (privacidade) e M (dados) | **não executadas** | adiadas para o PRD, onde o teach-back entra e cria dado pessoal novo (texto livre) |
| 2 | T (documentação) e E (pós-entrega) | **não executadas** | sem usuários reais antes do piloto |
| 2 | D (desempenho) | não aplicável | perfil do projeto |
| 4 | S, P, U, I, M, G, T, E | consulta, método aplicado direto | requisitos escritos no PRD; as skills não foram invocadas, para não gastar o orçamento em oito saídas longas numa fase de texto |
| 4 | G (privacidade) | **atenção** | o teach-back cria dado pessoal novo (texto livre); termo e aviso entram como **rascunho**, para o orientador e o comitê de ética |
| 4 | D, X, W | não aplicáveis | perfil do projeto |
| 6/T11 | S (segurança) | focada, método aplicado direto | **passou** — painel só leitura, em 127.0.0.1, sem rota de escrita; o código da sessão nunca entra num caminho de arquivo, com teste da propriedade |
| 6/T11 | G (privacidade) | focada, método aplicado direto | **passou com regra** — texto livre do participante só na tela de uma sessão, nunca na lista; identificação só pelo código |
| 7 | S (segurança, camadas 0 a 3) | focada, método aplicado direto | **parcial** — camadas 0 e 1 limpas; P1-A e P2-A na validação de entrada, P2-C em disponibilidade |
| 7 | D (desempenho) | focada, método aplicado direto | **falhou** — P1-B: a lista do painel custa 966 ms com 36 sessões e é pedida de 3 em 3 segundos |
| 7 | U (interface) | focada, método aplicado direto | **parcial** — teclado e símbolo-antes-de-cor em ordem; sem teste com pessoas, P3 de acessibilidade abertos |
| 7 | M (dados) | focada, método aplicado direto | **parcial** — P2-B (entrada sem limite) e P2-D (log sem versão de formato) |
| 7 | G (privacidade) | focada, método aplicado direto | **parcial** — P2-B e P2-E: o direito de exclusão está declarado no PRD e não tem mecanismo |
| 7 | T (documentação) | focada, método aplicado direto | **parcial** — o README acompanha as tarefas; faltam os procedimentos de cópia e exclusão |
| 7 | I (operação) | focada, método aplicado direto | **parcial** — P2-F: a cópia depois de cada sessão que o PRD exige não existe |
| 6/T11 | U (interface) | **não executada** | o painel tem um usuário só, que é quem construiu; a skill entra na revisão final, junto das telas de quem responde |
| final | S (camadas 0 a 4) | completa, método aplicado direto | **parcial** — P0 do log versionado, fechado na própria revisão; P2 do hook de pré-commit e do token no histórico |
| final | D (desempenho) | completa, método aplicado direto | **passou** — p50 6,3 ms e p95 28,2 ms em 1.832 chamadas; painel de 966 ms para 36–67 ms |
| final | M (dados) | completa, método aplicado direto | **passou** — invariantes de pé, CS-9 coberto, restauração com impressão digital idêntica |
| final | G (privacidade) | completa, método aplicado direto | **falhou** — a exclusão não alcança as cópias; termo de consentimento e plano de incidente não existem |
| final | U (interface) | completa, método aplicado direto | **parcial** — teclado e contraste medidos e em ordem; CS-11 sem evidência |
| final | I (operação) | completa, quatro ensaios executados | **parcial** — subida do zero, queda, restauração e reversão passaram; dois commits não restauram no Windows |
| final | T (documentação) | completa, comandos executados | **parcial** — README corrigido; guia nunca testado com pessoa de fora |
| final | E (pós-entrega) | completa | **não aplicável como canal** — não há usuários depois da entrega |

## Correções do perfil

| Quando | O que mudou | Por quê |
| --- | --- | --- |
| fase 7 | **D (desempenho) deixou de ser "não aplicável"** | o painel introduziu uma consulta repetida sobre um arquivo que cresce (P1-B). É a primeira vez neste processo que um "não aplicável" se mostrou errado, e fica registrado em vez de corrigido em silêncio |
| revisão final | **o ensaio de subida do zero virou obrigatório, e não formalidade** | foi o primeiro comando da revisão e falhou, e a falha revelou 2,8 MB de log de desenvolvimento versionados por dois commits. Nada no projeto — nem a varredura de segredos, nem os 214 testes — tinha percebido, porque ninguém tinha tentado clonar |

## Linha de base da fase 2

280 testes passando (28 no MVP, 252 no sistema antigo), 13.788 linhas de
Python. Qualquer mudança futura é comparada com isto.

## Orçamento

Fase 1: 4 iterações. Fase 2: 2 iterações. Fase 3: 1 iteração. Fase 4: 1
iteração. Fase 5: 1 iteração. Fase 6: 1 iteração por tarefa, nas treze —
nenhuma precisou de uma segunda.


## Ciclo de conteúdo — o kc_02

| Commit | O que entregou |
| --- | --- |
| `380c707` | `docs/linguagem.md`: o contrato, e três formatos de atividade propostos com o custo de cada um |
| `6cf0a24` | grafo e crenças do kc_02, sob o contrato |
| `6c99909` | crenças conferidas na obra primária; relatório em `docs/revisao-crencas-kc02.md` |
| `c9aec94` | as 36 atividades, e o carregador aceitando mais de um tópico |

### A conferência das fontes

Quatro das seis crenças têm fonte verificável; antes eram duas. Feita
baixando as obras, não de memória: o texto integral de Sorva (2012) no
repositório da Aalto e o FAQ do comp.lang.c. Achou uma **citação errada na
curadoria antiga** (`pointer_is_data` apontava o item 14, que não é sobre
ponteiro; é o 65) e três melhorias para o kc_00 — entre elas, a única
hipótese `E` do catálogo (`type_is_a_hint`) está documentada no item 123.

### O banco, medido contra o kc_00 pela mesma régua

| | kc_00 | kc_02 |
| --- | --- | --- |
| itens binários | 13 de 20 | **0 de 36** |
| distratores sem crença | 4 de 27 | 0 em diagnóstico (6 em treino) |
| a certa é a mais longa, com folga | 9 de 20 | **0 de 36** |
| camada 2 com 3 opções | 2 de 10 | **14 de 18** |
| item de diagnóstico sem a crença do próprio nó | 1 | **0** |

### O que a medição do kc_02 mostrou

Trinta sessões atravessadas pelo caminhante, três personas, antes de
qualquer pessoa ver a tela.

| Persona | kc_00 (5 nós, 2+2) | kc_02 (6 nós, 3+3) |
| --- | --- | --- |
| acerta tudo | 37 passos · 0/10 sem estado | 42 passos · 0/10 |
| erra e aprende | 65–71 · **3/10** | 84–123 · **4/10** |
| erra e não muda | 76–89 · **6/10** | 110–149 · **6/10** |

**A hipótese caiu.** Eu propus triplicar o banco para fechar o buraco da
CS-10, construí, e a medição diz que não fecha. O rastro de uma sessão
mostra por quê:

```
nó B2 — itens apresentados:   004, 005, 006   (os três que ele tem)
razão escolhida em 004 -> crença pointer_and_target_are_one -> nó I1
razão escolhida em 005 -> crença pointer_is_data            -> nó B3
razão escolhida em 006 -> crença pointer_and_target_are_one -> nó I1
estado final de B2: desconhecido
```

A crença do próprio B2 estava na cédula nas três vezes e não foi escolhida.
**Com N itens por nó, quem erra sempre pela razão do vizinho gasta os N.**
É estrutural: conteúdo não resolve, e mais itens só alonga a sessão.

E a sessão alongou: de 89 para **149 passos** no caminho difícil. A
composição mostra onde:

| | acerta e aprende | erra e não muda |
| --- | --- | --- |
| atividade | 26,6 | 44,8 |
| **confiança** | **26,6** | **44,8** |
| refutação | 16,4 | 18,2 |
| razão | 12,6 | 11,2 |

Uma tela de confiança por item, inclusive no treino — e no treino a
classificação não roda (`_resolve_treino` só olha certo/errado). São ~33
telas de confiança por sessão que não alimentam nenhuma decisão.

### O que precisa de decisão, e é de motor, não de conteúdo

1. **O nó que fica sem estado.** `desconhecido` não distingue "não foi
   perguntado" de "o banco acabou sem medir". O mínimo é nomear
   (`sem_item`, como o reteste já faz). O conserto de verdade é não gastar
   o item do nó quando a atribuição foi para o vizinho — com teto, para
   não repetir para sempre.
2. **A confiança no treino** é dado que você quer, ou tela a menos?
3. **O tamanho do tópico.** Seis nós com 3+3 estoura o orçamento de
   sessão. Cinco nós, ou 2+3, ou sessão mais longa — é escolha sua.


## Ciclo 3 — o que a medição mandou consertar

| Tarefa | Commit | O que entregou |
| --- | --- | --- |
| C1 | `6b6c8d0` | a crença de nó sustentado sai do cardápio; `nao_medido` com motivo |
| C2 | `6b6c8d0` | a confiança do treino só no item que fecha a sequência |
| C3 | — | medição: seis nós com 3+3 cabem na sessão |

### O caminhante, antes e depois

| Persona | antes | depois | sem medida |
| --- | --- | --- | --- |
| acerta tudo | 42 passos | 42 | 0/10 → 0/10 |
| erra e aprende | 84–123 | **81** | 4/10 → **0/10** |
| erra e não muda | 110–149 | **90–118** | 6/10 → 4/10, agora **nomeadas** |

A confiança caiu de 44,8 para 12,0 telas por sessão de quem erra muito —
de 34% para 12% da sessão.

### O que a sabotagem pegou neste ciclo

Duas de sete não mordiam:

- apagar a marcação do `nao_medido` passava limpo, porque nenhuma sessão
  normal deixava nó sem estado. Entrou uma **política de pior caso**, que
  explica sempre pela crença do vizinho e produz o caso de forma
  determinística;
- renomear `nao_medido` para `nao_medidoX` na tela passava, porque o teste
  procurava **substring** e o nome novo contém o antigo. É a terceira vez
  que a mesma armadilha aparece neste projeto (R3, R6 e agora). Virou
  checagem com fronteira de palavra.

## Ciclo de conteúdo — os outros KCs (kc_01 e kc_03)

O orientador pediu uma coisa: **automatizar a criação de questões**. O
gerador (`scripts/gerar.py`) atende isso, e o portão humano continua onde
estava — só entra no domínio o que tem `revisado_por` preenchido. Com o
gerador no ar, o que faltava era o conteúdo: a unidade existia para um
tópico de medida (kc_02) e um de pré-requisito (kc_00).

| Tópico | Título | Nós | Crenças | Atividades | Procedência |
| --- | --- | --- | --- | --- | --- |
| `kc_00` | Declaração de variáveis (pré-requisito) | 5 | 4 | 20 | anterior ao contrato |
| `kc_01` | Pilha e monte | 5 | 5 | 35 | 2 `E` |
| `kc_02` | O que é um ponteiro (tópico-piloto) | 6 | 6 | 60 | 1 `E` |
| `kc_03` | Declaração e inicialização | 6 | 6 | 42 | **nenhuma `E`** |

O kc_03 é o tópico com a melhor procedência dos quatro: duas crenças vêm
do catálogo do Sorva (2012), duas do FAQ do comp.lang.c com o texto
conferido em c-faq.com, uma do Kaczmarczyk et al. (2010) e uma do
cruzamento das duas últimas. Nenhuma ficou como `E` (estimada).

Cada tópico tem a **sua** analogia, declarada no YAML do grafo com os
pontos onde ela quebra, como `docs/linguagem.md` manda:

| Tópico | Analogia | Onde ela cala |
| --- | --- | --- |
| `kc_00` | o quarto de hotel | — |
| `kc_01` | a rua, com duas quadras | o monte não tem ordem de chegada |
| `kc_02` | a rua de casas numeradas | a casa não "contém" o nome |
| `kc_03` | o papel que já vem rabiscado | rabisco não é endereço de alguém; e ela não diz nada sobre a casa apontada, de propósito |

### O banco do kc_03

Seis nós × sete itens: um de `entrada` (o degrau mais baixo, respondido na
analogia depois do ensino), três de `diagnostico` (um por degrau, com o
par teórica + código) e três de `treino`. Passa o contrato inteiro: zero
item binário, zero distrator sem crença, zero item sem a crença do próprio
nó, zero item em que a resposta certa é a mais longa com folga.

### A medição, nas três personas, com o código de hoje

Uma rodada só, 10 sessões por persona, para os números serem comparáveis
entre si (os do ciclo 3 são anteriores à escada de nível e ao item de
entrada, e por isso não servem de base):

| Persona | `kc_01` (5 nós) | `kc_02` (6 nós) | `kc_03` (6 nós) |
| --- | --- | --- | --- |
| acerta tudo | 38 passos, 0/10 sem medida | 45, 0/10 | 45, 0/10 |
| erra e aprende | 68, 0/10 | 83, 0/10 | 86, 0/10 |
| erra e não muda | 81, **3/10** | 115, **1/10** | 102, **3/10** |

A leitura: o caminho que o laço foi desenhado para produzir — errar e
aprender — mede **todas** as premissas nos três tópicos. O pior caso
(quem erra e nunca muda de ideia) deixa premissa sem medida em 3 de 10
sessões no kc_01 e no kc_03, e em 1 de 10 no kc_02 — e a diferença entre
eles é o tamanho do banco: o kc_02 tem **dois** itens por degrau, os
outros dois têm **um**. É a mesma dívida de sempre, agora com número: o
segundo item por degrau do kc_01 (15 itens) e do kc_03 (18) é o que
compra essa queda, e é exatamente o que o gerador serve para produzir.

### Onde os tópicos novos passaram a ser cobrados

As quatro checagens de contrato em `mvp/test_dominio.py` eram do kc_02 e
agora são **parametrizadas** por `POS_CONTRATO = ("kc_01", "kc_02",
"kc_03")`: tópico novo entra nessa lista e passa a ser cobrado por elas.
Entraram mais duas, para os tópicos que têm a escada completa:

- a escada de diagnóstico não tem buraco (nó com item de nível 3 e sem o
  de nível 2 faz o motor pular um degrau);
- todo nó tem item de `entrada` (sem ele a construção ensina e não mede —
  dívida aberta do kc_00 e do kc_02).

Três sabotagens, três mordidas: degrau 2 virado em 3 derrubou a primeira;
`uso: entrada` virado em `treino` derrubou a segunda; apagar a crença de
um distrator de diagnóstico derrubou a terceira. A quarta, apagar o nome
de uma figura do kc_03, derrubou
`test_todo_no_de_todo_topico_tem_figura` — que agora exige os quatro
tópicos, não três.

## Ciclo de conteúdo — o kc_04 (dereferência: & e *)

Quarto tópico, e o primeiro em que a curadoria e a regra do processo
discordaram. Fica registrado porque é decisão de dono.

### A discordância: oito nós curados, seis crenças possíveis

`docs/curadoria-grafos.md` lista oito nós para o kc_04 (B1–B4, I1–I4) e
**duas** crenças, uma em B4 e uma em I1. A decisão 19 manda uma crença por
nó, sem exceção, porque a atribuição vem da camada 2: nó sem crença
própria nunca recebe atribuição e termina `nao_medido`. Para oito nós
faltariam seis crenças, e a literatura desta área sustenta seis **no
total**.

Dois pares foram dobrados, e os dois eram premissa-e-aplicação da mesma
ideia:

| Curado | Virou | Crença que ficou |
| --- | --- | --- |
| B1 (só o que ocupa memória tem endereço) + I1 (&5 é inválido) | `B1` | `ampersand_takes_value` |
| B4 (o `*` muda de papel) + I3 (`*` e `&` são inversos) | `I3`, a conclusão | `star_assigns_pointer` |

A alternativa era inventar quatro crenças `E` (estimadas, sem fonte) para
encher oito nós — o oposto da direção dos dois tópicos anteriores. Voltar
para oito custa escrever quatro crenças e 14 atividades; está escrito no
cabeçalho de `graph_kc04.yaml` para quem quiser desfazer.

### As fontes, conferidas na obra primária nesta sessão

Zero `E`, como o kc_03. Três crenças vieram do catálogo curado com a fonte
dele; três são novas, e as três foram lidas no original:

| Crença | Nó | Proc. | Fonte |
| --- | --- | --- | --- |
| `ampersand_takes_value` | B1 | L | FAQ comp.lang.c 4.10 (`f(&5)`) |
| `ampersand_copies` | B2 | T | Sorva (2012) p. 362 item 66 (Ma 2007) |
| `pointer_is_data` | B3 | T | Sorva (2012) p. 360 item 14 — também no kc_02 |
| `pointer_is_just_a_name` | I1 | T | Sorva (2012) p. 362 item 64 (Sorva 2008; Ma 2007) |
| `star_binds_to_the_pointer` | I2 | L | FAQ comp.lang.c 4.3 (`*p++`) |
| `star_assigns_pointer` | I3 | L | FAQ comp.lang.c 4.2 (`*p = malloc(10)`) |

A Tabela A.1 do Sorva foi baixada do repositório da Aalto e lida item a
item. A convenção de página do catálogo antigo confere: o rodapé 362
fecha o bloco dos itens 49 a 66, e o 363 começa no 67 — que é onde
`function_gets_original` já citava. As três entradas do FAQ foram lidas
inteiras em c-faq.com, e a de 4.2 diz a conclusão do tópico com outras
palavras: *"The pointer you declared is p, not \*p."*

### A medição, e as duas hipóteses sobre o pior caso

| Persona | `kc_01` | `kc_02` | `kc_03` | `kc_04` |
| --- | --- | --- | --- | --- |
| acerta tudo | 38, 0/10 | 45, 0/10 | 45, 0/10 | 45, 0/12 |
| erra e aprende | 68, 0/10 | 83, 0/10 | 86, 0/10 | 83, 0/12 |
| erra e não muda | 81, 3/10 | 115, 1/10 | 102, 3/10 | 103, **5/12** |

O caminho que o laço foi desenhado para produzir mede **todas** as
premissas nos quatro tópicos. O pior caso do kc_04 é o pior dos quatro, e
o motor diz por quê quando fecha: em **todas** as sessões o motivo foi
`os itens do nó foram gastos e toda razão errada escolhida neles apontou
outro nó` — nunca `nenhum item deste nó chegou a ser apresentado`.

**Hipótese 1, rejeitada: a ordem da cédula.** `motor.razoes_de` monta a
camada 2 na ordem das alternativas, então a primeira crença da cédula é a
da alternativa `b`. Dois itens do kc_04 abriam com a crença do vizinho.
Reordenados, o pior caso foi de 6/12 para 5/12 — ou seja, nada. A
reordenação ficou (primazia não custa), mas **não é o conserto**, e por
isso não virou teste: teste de propriedade que não compra nada é teatro.

**Hipótese 2, confirmada: a fração de vizinho na cédula.**

| Tópico | Distratores de diagnóstico | Do vizinho | Itens por degrau | Pior caso |
| --- | --- | --- | --- | --- |
| `kc_01` | 30 | 37% | 1 | 3/10 |
| `kc_02` | 72 | 47% | **2** | **1/10** |
| `kc_03` | 36 | 36% | 1 | 3/10 |
| `kc_04` | 36 | **50%** | 1 | 5/12 |

Medido direto: com o banco do kc_04 reescrito para **0% de vizinho** (todo
distrator apontando a crença do próprio nó), o pior caso foi para **0/12**,
e a sessão virou um tamanho fixo de 90 passos. O experimento foi feito
numa cópia, medido e desfeito — o banco real continua em 50%.

E é por isso que **0% não é o conserto**: o distrator do vizinho é
justamente o que deixa a camada 2 atribuir ao nó certo quando o erro da
pessoa é de outra premissa. Tirá-lo apaga a atribuição cruzada, que é o
desenho do instrumento (CS-2). O conserto é o outro: **mais itens por
degrau**, para que ao menos um dos itens do nó caia na crença dele. O
kc_02 é a evidência — tem a segunda pior fração e o melhor pior caso, e é
o único com dois itens por degrau.

Então a dívida tem agora mecanismo, número e ordem de prioridade: 18 itens
para o kc_04, 18 para o kc_03 e 15 para o kc_01, nessa ordem, pelo
gerador.

## O segundo item por degrau — 51 candidatos, e a medição que fecha a conta

A hipótese 2 do ciclo do kc_04 dizia que o conserto do pior caso é **mais
itens por degrau**, e não menos distrator de vizinho. Agora está medido
nos três tópicos, e não só inferido do kc_02.

### O que foi gerado

51 itens, pelo `scripts/gerar.py --importar`, um arquivo por nó e três
itens por arquivo (um por degrau). O `--importar` existe porque a
credencial desta máquina é token de sessão, não chave de API: quem
escreveu o item foi o modelo, por conversa, e **a conferência é a mesma** —
é ela que decide se o item serve, não quem o escreveu.

| Tópico | Nós | Itens novos | Banco fica em | Forma do degrau |
| --- | --- | --- | --- | --- |
| `kc_04` | 6 | 18 | 60 | `[1,1,2,2,3,3]` por nó |
| `kc_03` | 6 | 18 | 60 | `[1,1,2,2,3,3]` por nó |
| `kc_01` | 5 | 15 | 50 | `[1,1,2,2,3,3]` por nó |

Os 51 passaram pelo `confere()`: carregam no domínio pelo carregador de
verdade — o mesmo que roda em sessão — e passam nas regras de
`docs/linguagem.md`. Nenhum precisou de correção, o que era esperado:
o contrato inteiro vai no prompt do sistema, e o enum fechado de crenças
impede a invenção de concepção errônea.

**Os 51 continuam em `candidatos/`.** `revisado_por` está vazio em todos,
e `aprova()` recusa o que não tem o campo preenchido. O portão é do dono
do trabalho, não meu, e a folha de revisão de cada tópico está em
`candidatos/<topico>/REVISAO.md`.

### A medição, antes e depois

Para medir sem mexer no portão, os candidatos foram juntados ao domínio
numa cópia de trabalho, medidos, e os arquivos restaurados do backup —
`revisado_por` nunca foi tocado. 12 sessões por persona:

| Persona | `kc_01` | `kc_03` | `kc_04` |
| --- | --- | --- | --- |
| acerta tudo | 38 → 38, 0 → 0 | 45 → 45, 0 → 0 | 45 → 45, 0 → 0 |
| erra e aprende | 68 → 67, 0 → 0 | 86 → 86, 0 → 0 | 83 → 83, 0 → 0 |
| erra e não muda | 81 → 83, **3/10 → 1/12** | 102 → 119, **3/10 → 0/12** | 103 → 121, **5/12 → 2/12** |

A hipótese se confirma nos três, e com a ordem certa: quem estava pior
melhorou mais. O kc_03 zerou.

### O preço, e ele é real

A sessão de quem erra e não muda de ideia **ficou mais longa**, e a cauda
ficou pior:

| Tópico | pior sessão antes | pior sessão depois |
| --- | --- | --- |
| `kc_01` | 94 passos | 135 |
| `kc_03` | 123 passos | **207** |
| `kc_04` | 121 passos | 159 |

207 passos é mais do que uma pessoa real atravessa numa sessão de coleta.
A mediana continua perto de 120, então o caso típico está bem — mas a
cauda é a pergunta que fica, e é de **motor**, não de conteúdo: o que
encerra a unidade quando a pessoa não muda de ideia em nenhuma premissa.
Entra em perguntas em aberto, com o número medido.

## O quarto teto — a cauda, e o que ela estava escondendo

A cauda foi atacada antes da revisão dos 51 candidatos, por decisão do
dono. O diagnóstico veio primeiro, e ele mudou a conta toda.

### De que a cauda era feita

A sessão mais longa do kc_03 com dois itens por degrau tinha 136 telas,
assim distribuídas: 61 de atividade, 22 de refutação, 17 de razão, 17 de
confiança, 11 de validação, 6 de ensino, 2 de frase. E o treino por nó era
**desigual de um jeito que não se explica por acaso**:

| Nó | telas de treino |
| --- | --- |
| B1 | **16** |
| B3 | **12** |
| B2, I1, I2, I3 | 4 cada |

Quatro telas é um laço de treino: as quatro tentativas de `TETO_TENTATIVAS`.
B1 levou quatro laços; B3, três.

### A causa: uma regra que o código enunciava e não cumpria

O motor já tinha três tetos, cada um com o motivo escrito ao lado:

| Teto | Onde | O motivo, nas palavras do código |
| --- | --- | --- |
| `TETO_TENTATIVAS = 4` | treino | "se não bastou, não é falta de repetição" |
| `LIMITE_REEXPLICACAO = 2` | ensino | "insistir uma quarta vez na mesma frase não ensina" |
| uma construção por nó | lacuna | "sem teto a unidade não termina" |

E `_proxima_diagnostica` já pulava o nó `confirmado` ou `em_aberto`: o nó
que fechou não recebe mais item próprio. **Mas a atribuição cruzada passava
por cima.** A crença escolhida num item de OUTRO nó aponta aquele nó
(`alvo = p.razao.no`), e o caminho da refutação setava `estado=REFUTADO`
sem olhar o estado anterior. O nó voltava do `em_aberto` para o laço, com
validação, refutação e mais quatro tentativas de treino — uma vez por item
de vizinho que oferecesse a crença dele. B1 e B3 são os vizinhos mais
citados nas cédulas do kc_03, e é por isso que foram eles.

### A mudança: `tratado()`, em quatro lugares

`sustentado()` continua valendo só para o confirmado — `em_aberto` **não**
é uma premissa de pé, e misturar as duas coisas seria mentir no dado. O que
as duas têm em comum é outra coisa: a sessão já rodou o laço nelas. Isso
virou `tratado(estado)`, usado em quatro lugares:

1. a fila do diagnóstico (onde o par já estava escrito à mão);
2. o cardápio da camada 2 — a crença do nó fechado sai do menu, exatamente
   como a do nó confirmado saiu no C1;
3. a promoção do falso positivo repetido;
4. **o portão novo**: o caminho da refutação registra
   `refutacao_dispensada` e segue. A evidência não se perde —
   `crenca_detectada` já foi para o log, porque a pessoa disse a crença de
   novo e isso é dado. O que não acontece é o laço rodar outra vez.

Regra confirmada pelo dono: **um laço por premissa por sessão.**

### O que isso comprou — e aqui está a surpresa

Persona que erra e nunca muda de ideia, 12 sessões por célula:

| Tópico | antes do teto | **com o teto, no banco de hoje** | com o teto e 2 itens/degrau |
| --- | --- | --- | --- |
| `kc_01` | 72–94, 3/10 sem medida | **72–74, 0/12** | — |
| `kc_03` | 92–207, 3/10 → 0/12 | **92–92, 0/12** | 92–92, 0/12 |
| `kc_04` | 86–159, 5/12 sem medida | **86–90, 0/12** | 89–90, 0/12 |

As outras duas personas não mudaram **nada** (45 e 86 passos, idênticos):
o teto só toca o caminho de quem não muda de ideia.

**O teto faz, sozinho, o que os 51 itens faziam.** Com um item por degrau
— o banco de hoje, sem aprovar candidato nenhum — os três tópicos vão a
zero premissa sem medida, e a cauda desaparece junto: a sessão passa a ter
tamanho praticamente fixo.

Isso não joga os 51 no lixo, mas **muda o motivo de eles existirem**. O
argumento de medição acabou; ficam os outros, que são reais e menores:
item repetido entre o diagnóstico e o reteste de uma mesma pessoa, variedade
para quem atravessa o tópico duas vezes, e folga no degrau. A revisão deles
deixou de ser urgente.

### O teste que caiu, e como ficou

`test_a_premissa_nao_medida_diz_por_que` rodava a sessão inteira com
`_pior_caso` e cobrava o motivo do `nao_medido` que aquela política
produzia. Com o teto, o pior caso roteirizado fecha **todos** os nós como
`em_aberto` nos cinco tópicos — não sobra nó sem medida para o teste
examinar. A asserção de mordida que o ciclo 3 mandou pôr (`"o pior caso
parou de produzir nó sem medida; o teste não morde"`) foi exatamente o que
avisou.

Decisão do dono: testar no **fechamento**, direto no estado. A propriedade
que vale a pena guardar nunca foi "o pior caso esfomeia um nó" — é "quando
um nó fica sem medida, o fechamento o marca e diz por quê". O teste novo
monta os dois estados que distinguem os dois motivos (`itens_gastos` maior
que zero, e igual a zero) e cobra os dois, nos cinco tópicos. E entrou um
segundo teste, que cobra o que o teto comprou: no pior caso, nenhuma
premissa fica sem medida e todas terminam `em_aberto`. Se alguém desfizer o
teto, é esse que cai.

O `nao_medido` fica sendo a rede de segurança que sempre foi, agora
declarada como tal: existe para o caso que o laço não alcançou, inclusive
um banco mal formado que nenhuma política de sessão produz de propósito.

### As quatro sabotagens

| Corte | Mordeu? |
| --- | --- |
| o portão da refutação sai | 1 teste cai |
| o cardápio volta a filtrar só o confirmado | 6 caem |
| `tratado` passa a ser só o confirmado | 8 caem |
| a fila do diagnóstico deixa de pular o fechado | 1 cai |

As quatro mordem. 601 testes verdes (349 MVP + 252 antigo).

## Ciclo de conteúdo — o kc_05 (ponteiro NULL)

Quinto tópico. Mesmo desenho dos anteriores, mais duas coisas: a lista de
tópicos deixou de ser escrita à mão, e o quarto teto já estava no lugar
quando o tópico nasceu — foi o primeiro que não precisou de medição de
resgate.

### A discordância com a curadoria, outra vez

A curadoria lista **oito nós** para o kc_05 (B1–B4, I1–I4) e **duas**
crenças, em I3 e I4. É o mesmo caso do kc_04, e a mesma razão: a decisão
19 manda uma crença por nó, e a literatura desta área documenta seis
ideias, não oito. Dobras, todas registradas no cabeçalho de
`graph_kc05.yaml`:

| Curado | Virou | Por quê |
| --- | --- | --- |
| B1 + I1 (ausência de destino; NULL é valor, não não-valor) | `B1` | premissa e aplicação da mesma ideia |
| B4 + I4 (representação interna; NULL == 0 na fonte) | `I2` | idem |
| I2 (p == NULL é teste) | `I1`, **mantido** | a curadoria registra **zero caminhos** nele, mas ele é o que separa testar de desreferenciar, e a conclusão depende dessa separação |

O I1 ganhou crença de fora: `pointer_is_just_a_name`, do kc_04, que é
pré-requisito declarado deste tópico. Se p fosse apenas um nome do
apontado, `p == NULL` seria uma pergunta sobre o apontado — que é
exatamente o que a premissa nega.

### As fontes

Zero `E`. A seção 5 do FAQ do comp.lang.c é inteira sobre ponteiro nulo,
tem vinte entradas, e a 5.14 pergunta com essas palavras por que há tanta
confusão aqui. Textos de 5.1, 5.3, 5.18 e 5.19 lidos no original em
c-faq.com nesta sessão.

| Crença | Nó | Proc. | Fonte |
| --- | --- | --- | --- |
| `null_is_absence` | B1 | L | FAQ 5.1 ("a special value… distinguishable from all other pointer values"), 5.14, 5.15 |
| `any_zero_is_null` | B2 | L | FAQ 5.18 ("Only constant integral expressions with value 0 are guaranteed") |
| `null_points_to_zero` | B3 | L | FAQ 5.1 ("points definitively nowhere"), 5.19 (o vetor de interrupção na posição 0) |
| `pointer_is_just_a_name` | I1 | T | Sorva (2012) p. 362 item 64 — do kc_04 |
| `null_is_zero_always` | I2 | L | FAQ 5.13, 5.16, 5.3 (curada) |
| `null_is_safe_to_deref` | I3 | N | CERT C EXP34-C, CWE-476 (curada) |

`null_is_safe_to_deref` é a **única `N` dos cinco tópicos construídos**, e
é a procedência mais fraca do catálogo: a norma catalogou o erro, não a
crença. Fica declarada assim.

### A medição

| Persona | kc_05 |
| --- | --- |
| acerta tudo | 45 passos, 0/12 sem medida |
| erra e aprende | 82, 0/12 |
| erra e não muda | **88, 0/12** |

Em linha com o kc_03 (92) e o kc_04 (89) depois do quarto teto. **Nenhuma
medição de resgate foi necessária** — foi o primeiro tópico a nascer num
motor que já bota teto na cauda, e a fração de vizinho de 50% (a mais alta,
empatada com o kc_04) não cobrou nada.

### A lista de tópicos saiu da mão

Registrar um tópico novo exigia editar **seis** listas espalhadas pelos
testes, e duas estavam defasadas: o kc_03 e o kc_04 **nunca** tinham sido
varridos pelos testes de construção e de escada. Entrou
`dominio.topicos()`, que lê os `topic_*.yaml` do disco, e as seis listas
passaram a sair dela. A suíte do MVP foi de 349 para 383 testes **sem
nenhuma falha nova** — ou seja, a cobertura que faltava já estava passando,
só não estava sendo rodada.

### O estado dos seis tópicos

| Tópico | Nós | Itens | Distratores de vizinho | Procedências |
| --- | --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 31% | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 37% | 3 T, 1 L, **1 E** |
| `kc_02` | 6 | 60 | 47% | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 36% | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 50% | 3 L, 3 T |
| `kc_05` | 6 | 42 | 50% | 4 L, 1 T, 1 N |

As quatro `E` que restam estão nos três tópicos mais antigos, e são a
dívida de procedência do projeto. Os três construídos depois do contrato de
linguagem fecharam sem nenhuma.

### As quatro sabotagens

Buraco na escada do kc_05, nó sem item de entrada, nó sem figura, e
`topicos()` voltando a ser lista escrita à mão. As quatro mordem.

## Ciclo de conteúdo — o kc_06 (passagem por referência)

Sexto tópico, e o primeiro que **não exigiu editar teste nenhum**: a
`dominio.topicos()` do ciclo anterior varreu o kc_06 sozinha, e a suíte foi
de 383 para 399 testes sem uma linha de registro manual. Era exatamente o
que aquela mudança existia para comprar.

### A discordância com a curadoria, terceira vez

Sete nós curados (B1, B2, I1–I5), **duas** crenças (I1 e I4). A dobra foi
uma só, e era premissa e aplicação da mesma ideia:

| Curado | Virou |
| --- | --- |
| I2 (se o argumento é &x, f recebe cópia do endereço) + I3 (`*p = v` dentro de f altera x) | `I2` |

O segundo é o que o primeiro permite, e a crença que nega um nega o outro.

### As fontes

Zero `E`. A seção **"Calls"** da Tabela A.1 do Sorva (itens 41 a 53) é a
parte mais farta da tabela para este tópico — e nunca tinha sido usada. Os
três itens novos foram lidos no original:

| Crença | Nó | Proc. | Fonte |
| --- | --- | --- | --- |
| `funcao_usa_a_variavel_do_chamador` | B1 | T | Sorva p. 361 item 47 (Fleury 1991) + itens 44–45 (Madison & Gifford 1997) |
| `passa_a_expressao` | B2 | T | Sorva p. 362 item 51 + item 52 (George 2000a) |
| `function_gets_original` | I1 | T | Sorva p. 363 item 67 (Ma 2007) + FAQ 4.11 (curada) |
| `ampersand_copies` | I2 | T | Sorva p. 362 item 66 (Ma 2007) — do kc_04 |
| `modify_pp_changes_p` | I3 | L | FAQ comp.lang.c 4.8 — do kc_10 |
| `pointer_copy_is_alias` | I4 | T | Sorva p. 363 itens 74–75 (Holland et al. 1997) (curada) |

**Uma ressalva declarada:** o item 51 ("Expressions (not their values) are
passed as parameters") é marcado `local` na tabela do Sorva — é adição do
próprio autor, sem estudo citado. É a base mais fraca entre as seis, e por
isso a crença vem acompanhada do item 52, que tem citação. Fica escrito no
YAML.

### A medição

| Persona | kc_06 |
| --- | --- |
| acerta tudo | 45 passos, 0/12 sem medida |
| erra e aprende | 85, 0/12 |
| erra e não muda | **91, 0/12** |

Em linha com kc_03 (92), kc_04 (89) e kc_05 (88). Segundo tópico a nascer
depois do quarto teto, e também sem precisar de medição de resgate.

### Os sete tópicos

| Tópico | Nós | Itens | Vizinho na cédula | Procedências |
| --- | --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 31% | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 37% | 3 T, 1 L, **1 E** |
| `kc_02` | 6 | 60 | 47% | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 36% | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 50% | 3 L, 3 T |
| `kc_05` | 6 | 42 | 50% | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 50% | 5 T, 1 L |

Quatro tópicos construídos depois do contrato de linguagem, quatro sem
nenhuma `E`. As quatro `E` que restam continuam nos três mais antigos.

### As quatro sabotagens

Buraco na escada, nó sem item de entrada, nó sem figura, e a crença do
próprio nó saindo de um item de diagnóstico. As quatro mordem.

## Ciclo de conteúdo — o kc_07 (ponteiro e array) · **tópico-piloto**

Sétimo tópico, e o segundo **piloto** a ficar pronto (o kc_02 era o único
até aqui). Dos quatro que a coleta usa de verdade — kc_02, kc_07, kc_11,
kc_09 — metade está construída.

### A curadoria, pela primeira vez, quase não discorda

Este é o tópico em que a curadoria mais contribui: ela tem **seis**
crenças, todas grade L, todas com entrada do FAQ do comp.lang.c. **As seis
estão aqui**, cada uma no nó cuja afirmação ela nega de fato. A sétima
(`declaration_allocates`) vem do kc_03, e a própria curadoria registra que
aquele nó é "importado de `kc_03:I1`".

Nove nós curados, sete aqui, duas dobras de premissa-e-aplicação:

| Curado | Virou |
| --- | --- |
| B4 (`sizeof` e `&` não convertem) + I3 (`sizeof(a)` dá o array) | `B4` |
| I5 (`arr` e `&arr`, tipos diferentes) | a crença de `B4` |

**Sete nós, e não seis.** Custa ~7 passos a mais por sessão que os quatro
tópicos anteriores. Por ser piloto, vale: é onde a medida tem de ser fina,
e cortar um nó aqui seria cortar uma premissa que a coleta vai medir.

### Uma correção à curadoria

`string_literal_is_array` estava citada como **FAQ 6.6b** ("Isn't this an
array assignment? `char a[] = ...`"). A entrada que trata exatamente da
crença é a **1.32**: *"What is the difference between these
initializations? `char a[] = "string literal"; char *p = "string
literal";` My program crashes if I try to assign a new value to p[i]."* As
duas ficam citadas no YAML, a 1.32 primeiro. É a segunda correção de
citação que este projeto encontra conferindo a fonte primária.

### As fontes

| Crença | Nó | Proc. | Fonte |
| --- | --- | --- | --- |
| `string_literal_is_array` | B1 | L | FAQ 1.32 (+6.6b) |
| `declaration_allocates` | B2 | T | Kaczmarczyk MMR4 + FAQ 7.10 — do kc_03 |
| `array_passed_by_reference` | B3 | L | FAQ 6.4b |
| `arr_equals_addr_of_arr` | B4 | L | FAQ 6.12 |
| `array_is_assignable` | I1 | L | FAQ 6.5, 6.6, 6.7 |
| `sizeof_array_via_pointer` | I2 | L | FAQ 6.21 (o `sizeof` que imprime 4, não 10) |
| `array_is_pointer` | I3 | L | FAQ 6.2, 6.9, 6.10 |

**Seis `L` e uma `T`** — a distribuição mais forte dos oito tópicos, e a
única em que a maioria vem de literatura técnica de C em vez de
transposição de outra linguagem. Faz sentido: array-versus-ponteiro é o
assunto em que o FAQ de C é mais farto (24 entradas na seção 6, três delas
para a mesma crença).

### Uma regra a mais no banco, e ela é de piloto

Nenhum item depende de tamanho de ponteiro nem de tamanho de int.
`sizeof p` dá 8 nesta máquina e não no padrão: quem acertasse por saber o
número da máquina dele acertaria **por fora da premissa**. Onde o tamanho
aparece, a resposta certa é relativa — "o tamanho de um ponteiro", "mede
as cinco caixas" — nunca um número absoluto. Está escrita no cabeçalho do
banco.

### A figura ganhou primitiva nova

`quarteirao()`: casas que **se tocam**, sem canto arredondado, com o
número na porta só da primeira e o nome por baixo valendo pelo conjunto. A
disciplina do desenho é a própria conclusão do tópico: o quarteirão nunca
aparece como uma caixa com número dentro, e o ponteiro nunca aparece como
um quarteirão. Desenhar `a` como bilhete seria desenhar `array_is_pointer`.

### A medição

| Persona | kc_07 |
| --- | --- |
| acerta tudo | 52 passos, 0/12 sem medida |
| erra e aprende | 95, 0/12 |
| erra e não muda | **99, 0/12** |

O sétimo nó custou +7 no caminho curto e +11 no pior caso, contra os
tópicos de seis. Dentro do esperado, e o pior caso continua em zero.

### Os oito tópicos, 332 itens

| Tópico | Nós | Itens | Vizinho | Procedências |
| --- | --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 31% | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 37% | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 6 | 60 | 47% | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 36% | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 50% | 3 L, 3 T |
| `kc_05` | 6 | 42 | 50% | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 50% | 5 T, 1 L |
| `kc_07` · piloto | 7 | 49 | 50% | **6 L**, 1 T |

Cinco tópicos construídos depois do contrato de linguagem, cinco sem
nenhuma `E`.

### As quatro sabotagens

Buraco na escada, nó sem item de entrada, nó sem figura, e um item binário
entrando no banco. As quatro mordem.

## Ciclo de conteúdo — o kc_09 (free e ponteiro pendente) · **tópico-piloto**

Nono tópico, e o **terceiro piloto** dos quatro que a coleta usa. Falta só
o kc_11.

### A curadoria tinha um defeito, e o carregador o pega

A curadoria tem cinco crenças para o kc_09 — a segunda melhor cobertura
depois do kc_07 —, mas **duas delas negavam o MESMO nó**: `heap_persists`
e `double_free_is_safe`, as duas em I3. A decisão 19 não admite isso, e o
carregador também não: apontar duas crenças para um nó faz **sete testes
caírem**, porque o grafo e o catálogo passam a discordar e a invariante
"crença X nega A no catálogo e B no grafo" dispara. Foi a quarta
sabotagem deste ciclo, e ela mordeu forte.

As duas ficaram, em nós diferentes: `heap_persists` em **B4** (devolver
marca como inválido) e `double_free_is_safe` na **conclusão**.

Dez nós curados, oito aqui — a menor distância de todas, e de propósito,
por ser piloto:

| Nó | Crença | Proc. | De onde |
| --- | --- | --- | --- |
| B1 | `pointer_knows_block_size` | L | **nova** — FAQ 7.26, 7.27, 7.28 |
| B2 | `function_gets_original` | T | kc_06 (a curadoria registra a importação) |
| B3 | `pointer_lives_in_heap` | L | kc_02 (idem) |
| B4 | `heap_persists` | L | curada, movida de I3 |
| I1 | `free_nullifies` | L | curada |
| I2 | `free_kills_pointer` | L | curada |
| I3 | `null_after_free_redundant` | L | curada |
| I4 · conclusão | `double_free_is_safe` | N | curada, movida de I3 |

O curado I5 ("usar p depois, mesmo sem desreferenciar, é indefinido")
dobrou na conclusão: a curadoria registra **zero caminhos** nele, e a
mesma entrada que sustenta a conclusão — a **FAQ 7.21** — pergunta
exatamente isso: *"How unsafe is it to use (assign, compare) a pointer
value after it's been freed?"*

### A 7.21 sozinha sustenta três crenças

Porque é ela que explica **por quê** o ponteiro não vira NULL, e a
explicação é a premissa de todo o tópico:

> *"the value of the pointer in the caller probably remains unchanged,
> because C's pass-by-value semantics mean that called functions never
> permanently change the values of their arguments."*

As quatro entradas usadas foram lidas no original: **7.20** (*"You can't
use dynamically-allocated memory after you free it, can you?"* — resposta:
"No.", com a origem histórica da crença), **7.21**, **7.22** (*"Remember
that a pointer is different from what it points to"*) e **7.26** (*"The
malloc/free implementation remembers the size of each block"*).

### Duas regras a mais no banco, as duas de piloto

1. **Nenhum item pergunta o que acontece** ao usar um ponteiro pendente.
   Não há resposta — é comportamento indefinido —, e um item que premiasse
   "trava" ou "imprime lixo" ensinaria que existe resultado previsível.
   Onde o caso aparece, o que se pergunta é se é **válido**.
2. **`free(NULL)` é legal, e há um item de treino que ensina isso**
   (`ciu_kc09_t24`). Calar faria a pessoa sair daqui achando que todo free
   depois de um free é erro — e aí ela escreveria um `if` que não precisa.

### A figura faz uma coisa diferente do kc_05, de propósito

No kc_09 o fim da seta proibida **tem** caixa, com a classe `sujo` e um
`?` dentro. No kc_05 não tinha, porque no endereço nulo não existe objeto
algum. Aqui o lugar **existe** — ele só não é mais seu, e pode ter outro
dono com as coisas dele dentro. Desenhá-lo como inexistente contaria outra
história, e a premissa B4 é justamente essa.

### A medição, e o aviso que vem com ela

| Persona | kc_09 |
| --- | --- |
| acerta tudo | 59 passos, 0/12 sem medida |
| erra e aprende | **113**, 0/12 |
| erra e não muda | **120**, 0/12 |

**É o tópico mais longo dos nove**, e por uma razão simples: oito nós. A
conta por nó é estável — cada nó custa ~14 passos no caminho realista — e
dá para ler a série inteira: 6 nós → 85, 7 nós → 95, 8 nós → 113.

Isso é decisão de dono, e entra em perguntas em aberto: **113 passos cabem
na sessão de coleta?** Se não couberem, o caminho não é cortar nó (cada um
é uma premissa que a coleta mede) — é dividir o kc_09 em dois tópicos, ou
aceitar que a sessão dele é mais longa que as outras.

### Os nove tópicos, 388 itens

| Tópico | Nós | Itens | Vizinho | Procedências |
| --- | --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 31% | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 37% | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 6 | 60 | 47% | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 36% | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 50% | 3 L, 3 T |
| `kc_05` | 6 | 42 | 50% | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 50% | 5 T, 1 L |
| `kc_07` · piloto | 7 | 49 | 50% | 6 L, 1 T |
| `kc_09` · piloto | 8 | 56 | 50% | 6 L, 1 T, 1 N |

Seis tópicos construídos depois do contrato de linguagem, seis sem nenhuma
`E`. Três dos quatro pilotos prontos.

### As quatro sabotagens

Buraco na escada, nó sem item de entrada, nó sem figura, e **duas crenças
negando o mesmo nó** — a última derrubou sete testes, e é exatamente o
defeito que o catálogo curado tinha.

## Ciclo de conteúdo — o kc_11 (aritmética de ponteiros) · **o quarto piloto**

Décimo tópico, e com ele **os quatro pilotos estão construídos**: kc_02,
kc_07, kc_09 e kc_11. A coleta tem todos os tópicos que ela usa.

### Nove nós curados, seis aqui — três dobras, e uma fonte só explica as três

A curadoria tem duas crenças (em I2 e I5). Três dobras, todas de
premissa-e-aplicação:

| Curado | Virou | Por quê |
| --- | --- | --- |
| B2 (tamanho fixo) + B4 (o compilador conhece o tipo) | `B2` | a mesma afirmação por dois lados: é fixo **e** sabido antes de rodar |
| I1 (p+1 chega ao próximo objeto) + I2 (o compilador multiplica por sizeof) + I3 (na mão escala duas vezes) | `I3`, a conclusão | **a FAQ 4.4 é uma pergunta só, e contém as três** |
| I4 (`a[i]` é `*(a + i)`) | `I1`, mantido | zero caminhos na curadoria, mas é a identidade que liga índice e aritmética — e ganhou crença própria |

A 4.4 merece ser citada inteira, porque é o tópico em miniatura. O código
do questionador **é** a crença:

> *"int array[5], i, \*ip; ... printf("%d\n", \*(ip + 3 \* sizeof(int)));
> I expected the last line to print 3, but it printed garbage."*

E a resposta é a conclusão:

> *"Pointer arithmetic in C is always automatically scaled by the size of
> the objects pointed to. What you want to say is simply printf("%d\n",
> \*(ip + 3));"*

O item `ciu_kc11_017` é esse código **literal**, de propósito: é o
enunciado em que a crença foi registrada pela primeira vez, escrito por
quem a tinha.

### Todas as seis crenças são grade L

Primeiro tópico com procedência **uniforme**, e faz sentido: aritmética de
ponteiro é assunto de FAQ de C, não de estudo empírico em outra linguagem.

| Crença | Nó | Fonte |
| --- | --- | --- |
| `pointer_is_integer` | B1 | FAQ 4.14, 4.15 — do kc_02 |
| `pointer_knows_block_size` | B2 | FAQ 7.26, 7.28 — do kc_09 |
| `string_literal_is_array` | B3 | FAQ 1.32 — do kc_07 (a curadoria registra a importação) |
| `indice_nao_e_soma` | I1 | **nova** — FAQ 6.11 (`5["abcdef"]`) + 6.3 |
| `voidptr_arith_ok` | I2 | FAQ 4.6 → **11.24** (curada) |
| `ptr_arith_is_bytes` | I3 | FAQ 4.4 (curada) |

### Terceira precisão de citação

`voidptr_arith_ok` está citada na curadoria como FAQ 4.6 — e a 4.6 inteira
é *"Why can't I perform arithmetic on a void \* pointer? A: See question
11.24."* A resposta está na **11.24**, e é ela que dá a razão: *"The
compiler doesn't know the size of the pointed-to objects... Therefore,
arithmetic on void \*'s is disallowed."* As duas ficam citadas.

É a terceira precisão que o projeto encontra conferindo a fonte primária —
depois do Sorva no kc_02 e da 6.6b/1.32 no kc_07. Nenhuma delas muda uma
crença; todas mudam **onde a crença está escrita**, que é o que a
procedência promete.

### A medição

| Persona | kc_11 |
| --- | --- |
| acerta tudo | 45 passos, 0/12 sem medida |
| erra e aprende | 82, 0/12 |
| erra e não muda | 85, 0/12 |

Seis nós, e a sessão mais curta dos pilotos. A série por nó continua
estável: 6 → 82-86, 7 → 95, 8 → 113.

### Os dez tópicos, 430 itens

| Tópico | Nós | Itens | Vizinho | Procedências |
| --- | --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 31% | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 37% | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 6 | 60 | 47% | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 36% | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 50% | 3 L, 3 T |
| `kc_05` | 6 | 42 | 50% | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 50% | 5 T, 1 L |
| `kc_07` · piloto | 7 | 49 | 50% | 6 L, 1 T |
| `kc_09` · piloto | 8 | 56 | 50% | 6 L, 1 T, 1 N |
| `kc_11` · piloto | 6 | 42 | 50% | **6 L** |

Sete tópicos construídos depois do contrato de linguagem, sete sem nenhuma
`E`. As quatro `E` restantes estão todas nos três mais antigos — e dois
deles (kc_00 e kc_01) não são piloto. **O kc_02 é o único piloto com `E`
no catálogo: duas.** Isso vira dívida de procedência com nome e endereço.

### Uma dívida nova, de ferramenta — que depois se mostrou inexistente

A suíte do MVP mediu **3 minutos** neste ciclo, contra 30 segundos antes,
e eu atribuí isso aos testes que varrem todos os tópicos rodando sessões
inteiras. **A atribuição estava errada, e o número também.** Medida
sozinha, a suíte roda em 30 segundos e a varredura custa 6. A correção
está em "A pergunta 11 era um erro de medição", no fim deste documento.

## Ciclo de conteúdo — o kc_08 (alocação dinâmica)

Décimo primeiro tópico, e ele **fecha a pergunta em aberto 8**: o kc_08
era pré-requisito declarado do kc_09 e não existia. Agora existe.

### A quarta precisão de citação, e a mais séria

As três anteriores eram do tipo "a citação aponta para a entrada vizinha".
Esta é diferente: **as entradas citadas não sustentam a crença como ela
está escrita.**

`system_frees_auto` ("o sistema libera a memória do heap
automaticamente") estava citada como **FAQ 7.24 e 7.25**. Lidas no
original:

- **7.24** — *"Must I free allocated memory before the program exits? A:
  You shouldn't have to. A real operating system definitively reclaims all
  memory and other resources when a program exits."*
- **7.25** — é sobre o `free` **não** devolver memória ao sistema
  operacional, e sim guardá-la para os próximos malloc do mesmo programa.

Nenhuma das duas fala do bloco sobreviver ao **retorno da função**, que é
o que a premissa afirma e o que a crença nega. Pior: a 7.24 diz que no
**encerramento do programa** o sistema de fato recolhe — e isso é
**verdade**, não crença. Citá-la como fonte fazia a crença parecer
refutada por um texto que, na parte que ele trata, concorda com ela.

A entrada que sustenta a premissa é a **7.22**: *"When I call malloc to
allocate memory for a pointer which is local to a function, do I have to
explicitly free it? A: Yes. ... **Memory allocated with malloc always
persists until you explicitly free it.**"*

A citação foi corrigida nos **dois** catálogos que usam a crença — o do
kc_08 e o do kc_01, que a usa desde antes. A 7.24 e a 7.25 ficam citadas
**pelo contraste**, porque a distinção é o que a premissa precisa: o
sistema recolhe no fim do **programa**, e não no fim da **função**. A
figura I3 do kc_08 ensina exatamente essa distinção, em três linhas de
legenda.

### A 7.22 sustenta duas crenças, e são duas mesmo

A resposta dela tem duas metades, e cada uma nega uma coisa diferente:

| Metade | Crença | Nega |
| --- | --- | --- |
| *"Remember that a pointer is different from what it points to"* | `pointer_lives_in_heap` | que p e o bloco sejam a mesma coisa |
| *"Memory allocated with malloc always persists until you explicitly free it"* | `system_frees_auto` | que o bloco morra com a função |

### Oito nós curados, seis aqui

A curadoria tem duas crenças (I2 e I3), e **seis dos oito nós são marcados
"órfão"** — é o tópico com a estrutura mais solta de todos. Duas dobras de
premissa-e-aplicação:

| Curado | Virou |
| --- | --- |
| B3 (o bloco não tem conteúdo definido) + I3 (escrever antes de ler) | `B3` |
| B4 (o bloco não morre com a função) + I4 (ninguém libera por você) | `I3`, a conclusão |

| Crença | Nó | Proc. | De onde |
| --- | --- | --- | --- |
| `malloc_conta_elementos` | B1 | L | **nova** — FAQ 7.19b (`malloc(nints)`) + 7.8 |
| `pointer_is_data` | B2 | T | Sorva p. 360 item 14 — kc_02 |
| `malloc_initializes_zero` | B3 | L | FAQ 7.31 + Sorva p. 359 item 10 (curada) |
| `pointer_lives_in_heap` | I1 | L | FAQ 7.22 — kc_02, kc_09 |
| `malloc_always_succeeds` | I2 | N | CERT MEM52-C, CWE-252 (curada) |
| `system_frees_auto` | I3 | L | **FAQ 7.22** (corrigida) + 7.24, 7.25 por contraste |

A nova vem da 7.19b, e o código do questionador **é** a crença: *"int
\*iarray = (int \*)malloc(nints); malloc isn't returning NULL, but the
code isn't working."* A resposta é a premissa: *"malloc is a low-level,
typeless allocator. It doesn't know how you're going to use the memory;
all it does is to allocate as many bytes of memory as you ask it."*

### A medição

| Persona | kc_08 |
| --- | --- |
| acerta tudo | 45 passos, 0/12 sem medida |
| erra e aprende | 81, 0/12 |
| erra e não muda | 88, 0/12 |

### Os onze tópicos, 472 itens

| Tópico | Nós | Itens | Vizinho | Procedências |
| --- | --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 31% | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 37% | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 6 | 60 | 47% | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 36% | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 50% | 3 L, 3 T |
| `kc_05` | 6 | 42 | 50% | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 50% | 5 T, 1 L |
| `kc_07` · piloto | 7 | 49 | 50% | 6 L, 1 T |
| `kc_08` | 6 | 42 | 50% | 4 L, 1 T, 1 N |
| `kc_09` · piloto | 8 | 56 | 50% | 6 L, 1 T, 1 N |
| `kc_11` · piloto | 6 | 42 | 50% | 6 L |

Oito tópicos construídos depois do contrato de linguagem, oito sem nenhuma
`E`. **Faltam dois: kc_10 e kc_12.** Nenhum dos dois é piloto.

### As quatro sabotagens

Buraco na escada, nó sem item de entrada, nó sem figura, e uma crença
ficando órfã no catálogo — esta última derruba dois testes, inclusive a
carga do domínio.

## Ciclo de conteúdo — o kc_10 (ponteiro para ponteiro)

Décimo segundo tópico. **Falta um: o kc_12.**

### Oito nós curados, seis aqui

A curadoria tem **três** crenças (I2, I3, I4) — a terceira melhor
cobertura do projeto, depois do kc_07 (seis) e do kc_09 (cinco). Duas
dobras de premissa-e-aplicação:

| Curado | Virou | Por quê |
| --- | --- | --- |
| B1 (um ponteiro tem endereço) + B2 (`&p` produz esse endereço) | `B1` | as duas metades de uma coisa só, e é por isso que `&p` existe |
| I1 (pp e p são distintas) + I2 (`*pp` é p; `**pp` é o int) | `I3`, a conclusão | o segundo é o primeiro dito em código |

| Crença | Nó | Proc. | De onde |
| --- | --- | --- | --- |
| `ampersand_copies` | B1 | T | Sorva p. 362 item 66 — kc_04, kc_06 |
| `pointer_is_just_a_name` | B2 | T | Sorva p. 362 item 64 — kc_04, kc_05 |
| `voidptr_is_universal` | B3 | L | FAQ 4.13, 4.6 + **4.9** — kc_02 |
| `modify_pp_changes_p` | I1 | L | FAQ 4.8 (curada) |
| `array2d_is_double_pointer` | I2 | L | FAQ 6.18 (curada) |
| `double_deref_is_data` | I3 | L | FAQ 4.9 (curada) |

A **4.9** sustenta duas crenças, e são duas mesmo: uma metade da resposta
diz que *"There is no generic pointer-to-pointer type in C"* (→ `B3`, o
tipo fixa os níveis) e a outra trata do número de estrelas como algo
ajustável (→ a conclusão). É o mesmo padrão da 7.22 no kc_08 e da 7.21 no
kc_09.

A **6.18** é a melhor das três curadas, porque a resposta é a premissa com
todas as letras: *"The rule by which arrays decay into pointers is not
applied recursively. (Once the rule has been applied once, the result is a
pointer to which the rule no longer applies.) An array of arrays decays
into a pointer to an array, not a pointer to a pointer."*

Dois itens trazem o código **literal** do FAQ: o `ciu_kc10_011` é a
pergunta 4.8 (`ip = &dummy` dentro de f), e o `ciu_kc10_008` é a 4.9
(`f((void **)&dp)`).

### Uma regra a mais no banco

Todo item de código declara os níveis inteiros, de `x` até `pp`, mesmo
quando o item só pergunta sobre um deles. Dois níveis é o limite do que
uma pessoa segue de cabeça, e omitir uma linha faria a pessoa errar por
ter perdido a conta — o que mede **atenção**, não premissa.

### A medição

| Persona | kc_10 |
| --- | --- |
| acerta tudo | 45 passos, 0/12 sem medida |
| erra e aprende | 82, 0/12 |
| erra e não muda | 86, 0/12 |

### Os doze tópicos, 514 itens

| Tópico | Nós | Itens | Procedências |
| --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 6 | 60 | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 3 L, 3 T |
| `kc_05` | 6 | 42 | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 5 T, 1 L |
| `kc_07` · piloto | 7 | 49 | 6 L, 1 T |
| `kc_08` | 6 | 42 | 4 L, 1 T, 1 N |
| `kc_09` · piloto | 8 | 56 | 6 L, 1 T, 1 N |
| `kc_10` | 6 | 42 | 4 L, 2 T |
| `kc_11` · piloto | 6 | 42 | 6 L |

Nove tópicos construídos depois do contrato de linguagem, nove sem nenhuma
`E`. As quatro `E` continuam nos três mais antigos.

### Uma pista para a pergunta 10, achada de passagem

Procurando fonte para o nó B1 deste tópico — "um ponteiro é variável e tem
endereço próprio", que a curadoria importa de `kc_02:B2` —, apareceu a
**FAQ 7.3c**:

> *"How much memory does a pointer variable allocate? A: That's a pretty
> misleading question. When you declare a pointer variable, as in char
> \*p; you (or, more properly, the compiler) have allocated only enough
> memory to hold the pointer itself; that is, in this case you have
> allocated sizeof(char \*) bytes of memory. But you have not yet
> allocated any memory for the pointer to point to."*

Essa é a premissa `kc_02:B2` afirmada diretamente por uma obra técnica
revisada, e a crença que a nega é `pointer_has_no_address` — **uma das
duas `E` do kc_02**, que é o único piloto com crença estimada (pergunta em
aberto 10).

**Não mexi no catálogo do kc_02.** A entrada documenta a *pergunta* ("quanto
um ponteiro aloca?"), e a crença é a forma afiada dela ("não aloca nada,
é só a seta") — chamar isso de `L` é uma decisão de dono, não minha, e o
kc_02 é o que vai para a monografia. O que fica registrado é que **a fonte
existe e foi lida**: se você aceitar a 7.3c, a mudança é de dois campos
num arquivo, e o kc_02 passa de duas `E` para uma.

E para o B1 deste tópico usei outra crença (`ampersand_copies`), justamente
para não espalhar uma `E` nem criar uma crença com duas procedências
diferentes em dois catálogos.

### As quatro sabotagens

Buraco na escada, nó sem item de entrada, nó sem figura, e um nó de
diagnóstico perdendo o par teórica+código — esta última derruba a carga do
domínio.

## Ciclo de conteúdo — o kc_12 (ponteiro pendente por escopo) · **o último**

Décimo terceiro tópico, e com ele **os doze da curadoria estão
construídos**, mais o kc_00 de pré-requisito. 79 nós, 556 itens.

### Nove nós curados, seis aqui

A curadoria tem duas crenças (I2 e I4), e **seis dos nove nós não têm
crença nenhuma**. Três dobras:

| Curado | Virou | Por quê |
| --- | --- | --- |
| B1 (locais existem durante a execução) + B2 (o retorno encerra) | `B1` | o antes e o depois de uma coisa só |
| I1 (retornar `&local` copia um endereço) + I2 (quando o chamador recebe, o objeto já saiu) | `I1` | o segundo é o instante do primeiro |
| I3 (dangling sem free) + I5 (o chamador fornece o armazenamento) | `I3`, a conclusão | o I5 tem **zero caminhos** e é o conserto da conclusão, não premissa |

### Todas as seis crenças são grade T

É a **imagem espelhada do kc_11**, que fechou com seis `L`. As duas coisas
fazem sentido juntas: escopo e tempo de vida são estudados empiricamente
em outras linguagens (du Boulay, Kaczmarczyk, Kumar, Hristova), enquanto
aritmética de ponteiro é assunto de FAQ de C.

| Crença | Nó | De onde |
| --- | --- | --- |
| `memory_is_uniform` | B1 | Kaczmarczyk p. 109 Tabela 1 tema T1 — kc_01 |
| `ampersand_copies` | B2 | Sorva p. 362 item 66 — kc_04, kc_06, kc_10 |
| `retorno_fica_guardado` | B3 | **nova** — Sorva p. 361 item 38 (Hristova et al. 2003) |
| `pointer_is_data` | I1 | Sorva p. 360 item 14 — kc_02, kc_04, kc_08 |
| `static_is_scope` | I2 | Sorva p. 114 (curada) |
| `local_survives_return` | I3 | Kumar (2001) ITiCSE + Sorva p. 359 item 5 (curada) |

A nova vem do item 38, e a frase está no original com o plural trocado:
*"A return values does not need to be stored (even if one needs it
later)"* (Hristova et al. 2003). Fica citada assim, como está.

### A quinta observação de citação: existe, mas é fina

`static_is_scope` está citada como **Sorva (2012), p. 114**. Conferida: a
página traz, numa lista das distinções que o autor diz que confundem quem
está começando, o par **"scope vs. lifetime"** — que é exatamente a
confusão que a crença nomeia. A fonte **existe e diz a coisa certa**.

Mas é **um item de lista no texto corrido**, não uma entrada da Tabela A.1
com estudo atrás. É a mais fina das seis crenças deste tópico, e por isso
veio acompanhada do item 5 da tabela (*"Difficulties understanding the
lifetime of values"*, du Boulay 1986), que sustenta a metade do tempo de
vida com citação própria. A ressalva está escrita no YAML.

Esta é a quinta observação de citação do projeto, e a mais branda: as três
primeiras apontavam para a entrada vizinha, a quarta (no kc_08) apontava
para entradas que **não sustentavam** a crença, e esta aponta para uma
fonte **certa mas magra**.

### Duas regras a mais no banco

1. **Nenhum item depende de ordem de avaliação não especificada.** O
   `printf("%d %d\n", conta(), conta())` é tentador para medir o `static`,
   e o padrão não diz qual chamada roda primeiro — quem acertasse
   acertaria por sorte. Onde duas chamadas precisam aparecer, elas vão em
   duas linhas (`ciu_kc12_t15`).
2. **Nenhum item pergunta o que sai** ao usar o ponteiro pendente. É a
   mesma regra do kc_09, e aqui ela pesa mais: premiar "o valor antigo"
   ensinaria justamente o que faz o erro **parecer funcionar**.

### A figura faz o contrário do kc_09, de propósito

No kc_09 o lote devolvido aparece com `sujo` e `?`: ele **existe** e pode
ter outro dono. Aqui a casa aparece **tracejada e vazia**: ela foi
**desmontada**, e o que o desenho tem de dizer é que não está mais lá.
Desenhá-la com conteúdo diria que o valor antigo é confiável — e é
exatamente isso que faz o erro parecer funcionar, o que o nó I2 trata em
palavras, e não em figura.

### A medição

| Persona | kc_12 |
| --- | --- |
| acerta tudo | 45 passos, 0/12 sem medida |
| erra e aprende | 82, 0/12 |
| erra e não muda | 88, 0/12 |

### Os treze tópicos, 79 nós, 556 itens

| Tópico | Nós | Itens | Procedências |
| --- | --- | --- | --- |
| `kc_00` | 5 | 20 | 3 L, 1 T, **1 E** |
| `kc_01` | 5 | 35 | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 6 | 60 | 2 T, 1 D, 1 L, **2 E** |
| `kc_03` | 6 | 42 | 3 D, 2 L, 1 T |
| `kc_04` | 6 | 42 | 3 L, 3 T |
| `kc_05` | 6 | 42 | 4 L, 1 T, 1 N |
| `kc_06` | 6 | 42 | 5 T, 1 L |
| `kc_07` · piloto | 7 | 49 | 6 L, 1 T |
| `kc_08` | 6 | 42 | 4 L, 1 T, 1 N |
| `kc_09` · piloto | 8 | 56 | 6 L, 1 T, 1 N |
| `kc_10` | 6 | 42 | 4 L, 2 T |
| `kc_11` · piloto | 6 | 42 | 6 L |
| `kc_12` | 6 | 42 | **6 T** |

**Dez tópicos construídos depois do contrato de linguagem, dez sem nenhuma
`E`.** As quatro `E` restantes estão todas nos três mais antigos — e das
quatro, só duas estão num piloto (o kc_02), que é a pergunta em aberto 10.

Em todos os treze, nas três personas, **nenhuma premissa fica sem medida**.

### O que o ciclo de conteúdo deixa para trás

| O que | Onde está registrado |
| --- | --- |
| As duas `E` do kc_02, com a fonte candidata já lida (FAQ 7.3c) | pergunta 10 |
| Os 51 candidatos de segundo item por degrau, sem revisão | `candidatos/`, e a revisão deixou de ser urgente |
| A suíte do MVP em 4 minutos | pergunta 11 |
| Os 6 ou 8 nós do kc_04 | pergunta 7 |
| 113 passos no kc_09 | pergunta 9 |

### As quatro sabotagens

Buraco na escada, nó sem item de entrada, nó sem figura, e o treino
perdendo a variedade de formato — a última derruba a carga do domínio.

## A pergunta 11 era um erro de medição

A pergunta 11 dizia que a suíte do MVP tinha passado de 30 segundos para 3
ou 4 minutos, e apontava a causa: os testes que varrem todos os tópicos
rodando sessões inteiras. **As duas coisas estavam erradas** — o número e
a causa —, e as duas eram minhas.

### O número

Medida sozinha, com nada mais rodando, três vezes seguidas:

| | |
| --- | --- |
| execução 1 | 495 testes em **30,6 s** |
| execução 2 | 495 testes em **33,4 s** |
| execução 3 | 495 testes em **32,9 s** |

As leituras de 102 s, 118 s e 264 s que entraram neste documento foram
tomadas **logo depois de escrever muitos arquivos e com outra coisa
rodando na máquina** — em alguns casos a suíte antiga em paralelo, em
outros um servidor de medição ainda no ar. A de 264 s não se reproduz, e
eu não sei dizer o que a causou; o que sei é que ela não se repete em
medição limpa.

O mesmo erro já tinha aparecido uma vez, com a suíte antiga: 849 s medidos
em paralelo, 56 s medidos sozinha. Eu escrevi na hora que "isso não é só
carga de máquina", e era.

### A causa

A varredura de tópicos, que eu acusei, custa **6,2 segundos no total** —
78 testes que rodam sessão inteira, o mais lento deles em 0,07 s. Não é
ela.

Onde o tempo realmente está, por arquivo, medido isoladamente:

| Arquivo | Tempo | Testes | O que ele faz de caro |
| --- | --- | --- | --- |
| `test_procedimentos.py` | 10,3 s | 23 | roda os scripts de shell em subprocesso |
| `test_dominio.py` | 7,2 s | 89 | recarrega os 13 tópicos do disco, muitas vezes |
| `test_medida.py` | 6,5 s | 91 | idem, mais as sessões |
| `test_gerador.py` | 5,0 s | 18 | copia o domínio inteiro para pastas temporárias |
| `test_escada.py` | 3,1 s | 35 | recarrega os tópicos |
| os outros 10 | 0,2–2,7 s | 210 | — |

A soma dos arquivos medidos um a um dá 60 s, e a suíte inteira dá 31: a
diferença é o custo de subir o interpretador quinze vezes.

### E por isso não há nada a consertar

Trinta segundos cabe na disciplina de uma verificação por mudança. O
conserto que a pergunta 11 propunha — marcar os testes de sessão inteira
como lentos e tirá-los do caminho normal — teria **reduzido a cobertura de
toda mudança** para resolver um problema que não existe, e teria tirado do
caminho exatamente os testes que custam 6 dos 31 segundos.

Há uma folga real a tomar se algum dia fizer falta: `test_dominio`,
`test_medida` e `test_escada` somam 17 s recarregando os mesmos 13 tópicos
do disco a cada teste parametrizado, e um cache por tópico cortaria a
maior parte disso. **Não foi feito**, por dois motivos: 31 s não incomoda,
e um cache de domínio é precisamente onde mora o bug de leitura velha —
o `test_gerador` escreve num espelho temporário e carrega em seguida, e um
cache ingênuo devolveria o arquivo antigo. Fica registrado como folga
disponível, não como dívida.

### A regra que faltava, e agora está escrita

**Medida de tempo se toma com a máquina quieta.** Nada de servidor de
medição no ar, nada de segunda suíte em paralelo, e não logo depois de
escrever dezenas de arquivos. Duas vezes neste projeto eu registrei um
número tomado sob contenção e expliquei a causa com confiança — e nas duas
a explicação estava errada. Número medido sob contenção não é medida: é
palpite com casa decimal.

## A pergunta 10 resolvida: os quatro pilotos ficaram sem nenhuma `E`

O kc_02 era o único tópico-piloto com crença estimada, e tinha duas. As
duas tinham fonte, e a busca anterior não achou por dois motivos
diferentes — os dois instrutivos.

### `pointer_has_no_address`: a busca errou de vocabulário

A nota que estava no catálogo dizia, em maiúsculas:

> *"PROCUREI no catálogo do Sorva (2012) e NÃO ESTÁ LÁ: nenhum dos 162
> itens afirma que a referência não ocupa espaço."*

Está no item **14**, e estava citado **neste mesmo catálogo** desde o
começo — para outra crença, usando a **primeira** frase dele. O item tem
duas:

> *"A variable is (merely) a pairing of a name to a changeable value (with
> a type). **It is not stored inside the computer.**"* (Sorva 2008;
> Doukakis et al. 2007)

A primeira frase é `pointer_is_data` ("o ponteiro é o próprio dado"). A
segunda é `pointer_has_no_address` ("não ocupa lugar nenhum") — dita com
outras palavras, mas dita. A busca procurava por **referência** e por
**espaço**; o item fala de **variável** e de **"not stored inside the
computer"**. Passou batido por vocabulário, não por ausência.

É o mesmo padrão de fonte com duas metades que já tinha aparecido três
vezes: a FAQ 7.21 sustenta três crenças do kc_09, a 7.22 duas do kc_08, e
a 4.9 duas do kc_10. Procurar pela metade que falta virou hábito — mas
virou depois de escrever esta nota.

**`E` → `T`**, com a transposição declarada: os estudos são sobre
variáveis em linguagens onde o aluno não vê o armazenamento, e em C há o
agravante de que o endereço da própria caixa é observável (`&p`).

### `pointer_is_pointless`: a busca olhou no catálogo errado

A nota dizia que o catálogo do Sorva é sobre **mecanismo** e esta crença é
sobre **finalidade**, e concluía que por isso ela não estaria em catálogo
nenhum. A primeira metade continua certa. A segunda não:

> **FAQ comp.lang.c 4.1** — *"What are pointers really good for,
> anyway?"*

A pergunta **é** a crença, e o "anyway" carrega o tom de quem não vê para
quê. A resposta é uma lista de finalidades. E o lugar dela importa: é a
**primeira** pergunta da seção de ponteiros. Quem manteve a lista achou
que, antes de qualquer mecanismo, era preciso responder por que a coisa
existe — e isso é testemunho de especialista sobre erro comum, que é
exatamente o que a procedência `L` afirma.

**`E` → `L`**.

### As duas `E` que ficam, e o que foi procurado para elas

| Crença | Tópico | Candidata considerada | Por que ficou `E` |
| --- | --- | --- | --- |
| `type_is_a_hint` | `kc_00` | Sorva p. 360 item 19, *"There is no size or precision limit to the values we can store in a programming variable"* (Doukakis et al. 2007) | **Recusada.** "Sem limite" é outro modelo errado, não "todas do mesmo tamanho". Citá-la seria o mesmo falso amigo que o projeto pegou no kc_08 |
| `memoria_e_do_computador` | `kc_01` | nada encontrado | A crença é sobre **isolamento entre processos**; o catálogo do Sorva trata de máquina notional sem processos, e o FAQ de C não trata do assunto |

Nenhum dos dois é piloto, e o que foi procurado está escrito no
`beliefs_kc02.yaml` para a busca não ser repetida.

### A procedência do projeto, depois

| Tópico | Procedências |
| --- | --- |
| `kc_00` | 3 L, 1 T, **1 E** |
| `kc_01` | 3 T, 1 L, **1 E** |
| `kc_02` · piloto | 3 T, 2 L, 1 D |
| `kc_03` | 3 D, 2 L, 1 T |
| `kc_04` | 3 L, 3 T |
| `kc_05` | 4 L, 1 T, 1 N |
| `kc_06` | 5 T, 1 L |
| `kc_07` · piloto | 6 L, 1 T |
| `kc_08` | 4 L, 1 T, 1 N |
| `kc_09` · piloto | 6 L, 1 T, 1 N |
| `kc_10` | 4 L, 2 T |
| `kc_11` · piloto | 6 L |
| `kc_12` | 6 T |

**79 crenças: 42 L, 28 T, 4 D, 3 N, 2 E.** As duas `E` estão fora dos
pilotos.

### Dois testes novos, e o que eles guardam

```
test_piloto_nao_tem_crenca_estimada          nenhum piloto com `E`
test_toda_crenca_de_piloto_tem_fonte_escrita nenhuma com `source` vazio
```

O segundo existe porque o primeiro, sozinho, seria fácil de burlar sem
querer: trocar a procedência de `E` para `T` é uma letra, e uma letra sem
fonte escrita não vale nada. As duas sabotagens mordem — devolver uma
crença de piloto para `E`, e deixar uma com `source` de uma linha.

## A pergunta 9 resolvida: a unidade do plano é UMA premissa, e o escopo existe

A pergunta 9 perguntava se 113 telas cabem na sessão de coleta. **Ela
comparava objetos diferentes**, e a resolução é a medida que faltava.

### O que o plano pede, lido com cuidado

`docs/plano-tcc.md` define a unidade nova "do tamanho de uma lição de
Duolingo", em quatro estágios:

| Estágio | Telas |
| --- | --- |
| 1. Ensina | 2 |
| 2. Pratica com retorno imediato | 4 a 6 |
| 3. Refuta, só se houver hipótese de crença | 3 a 5 |
| 4. Fecha mostrando o que ela construiu | 1 |

Soma: **10 a 14**. A tabela-resumo do mesmo documento diz "8 a 10 telas
por unidade" — o resumo é que está apertado em relação à composição, não o
sistema. E o estudo roda **duas unidades** em cerca de 30 minutos.

Duas telas de ensino, quatro a seis de prática, três a cinco de refutação:
isso é o ciclo de **uma premissa**, não de um tópico com seis.

### A medida que faltava: telas por premissa

Sessão inteira rodada em processo, sem servidor, com a persona realista
(erra no diagnóstico, acerta no treino e no reteste), sobre domínios do
kc_12 cortados em n premissas:

| Premissas | Telas | Por premissa |
| --- | --- | --- |
| 1 | **14** | 14,0 |
| 2 | 26 | 13,0 |
| 3 | 38 | 12,7 |
| 4 | 52 | 13,0 |
| 5 | 65 | 13,0 |
| 6 | 81 | 13,5 |

**Treze telas por premissa, e custo fixo quase nenhum.** O 81 confere com
o 82 que o caminhante media pelo HTTP (ele conta um POST a mais).

E a sequência das 14 de uma premissa, tela por tela:

| # | Tela | Estágio do plano |
| --- | --- | --- |
| 1 | frase / abertura | — **de sessão** |
| 2 | ensino | 1. Ensina (plano: 2) |
| 3 | atividade / diagnóstico | 2. Pratica |
| 4 | razão | 2. Pratica — camada 2 |
| 5 | confiança | 2. Pratica — camada 3 |
| 6 | validação | 3. Refuta |
| 7 | refutação | 3. Refuta |
| 8 | atividade / treino | 2. Pratica |
| 9 | atividade / treino | 2. Pratica |
| 10 | confiança | 2. Pratica |
| 11 | atividade / reteste | — **de sessão** |
| 12 | razão | — **de sessão** |
| 13 | confiança | — **de sessão** |
| 14 | frase / fecho | 4. Fecha (plano: 1) |

Os quatro estágios do plano somam **10 telas**: ensino 1 (plano pede 2),
prática 6 (plano pede 4 a 6), refutação 2 (plano pede 3 a 5), fecho 1. As
outras quatro são **de sessão, não de unidade** — e é o próprio plano que
diz isso do reteste: *"O reteste sai de perto da refutação… Ele passa para
o fim da sessão, depois de outra unidade."*

**A unidade está dentro do orçamento.** O que estava fora era a
comparação.

### O que faltava de verdade, e entrou

O motor sempre rodou o **tópico inteiro**. Não havia como rodar uma sessão
de duas premissas, que é o que o estudo descreve. Agora há:

```bash
STRUCTURA_TOPICO=kc_12 STRUCTURA_PREMISSAS=2 python -m mvp.app
```

Medido ponta a ponta, com o servidor no ar e o caminhante: `/saude` diz 2
nós, 2 crenças, 14 atividades, e a sessão dá **17 passos** para quem
acerta tudo, **27** para quem erra e aprende, **29** para quem não muda de
ideia. As duas unidades do plano, em 27 telas.

### Três decisões de desenho, e o motivo de cada uma

**O corte é no CARREGADOR, não no motor.** O dado cru é cortado antes de
qualquer parse, e por isso **todas as invariantes da carga valem para o
domínio cortado** — crença que nenhuma alternativa aponta, nó sem o par
teórica+código, nó sem item de nível 1. Um corte que produzisse domínio
inválido falha na carga, que é onde este projeto falha.

**O corte é por PREFIXO da ordem do grafo, não por nome.** Prefixo garante
que nenhuma inferência fique sem a premissa que a sustenta — e isso está
conferido nos treze tópicos: não há N em que alguma referência de suporte
caia fora, nem total nem parcial. Um subconjunto por nome permitiria pedir
a conclusão sem as premissas dela. Se fizer falta, entra depois, com a
checagem de fechamento.

**O padrão não muda.** Sem a variável e sem o argumento, a sessão é o
tópico inteiro — é o que o motor sempre fez e o que a suíte mede.

### Uma sabotagem passou limpa, e endureceu um teste

Tirar a checagem de suporte do corte **não derrubou nada**: a invariante
geral do carregador dispara de qualquer jeito, com a mensagem *"nó I1:
suporte 'I2' não existe"*. A asserção antiga procurava só por "I1" e "I2"
na mensagem, e as duas a satisfaziam.

A mensagem genérica, porém, está **errada** no caso do corte: o suporte
existe no tópico, e foi o corte que o tirou — quem lesse "não existe" iria
procurar erro no YAML. A checagem ganha o lugar pela mensagem, então o
teste passou a cobrar a mensagem: `"corta"`, `"sustenta"` e
`"premissas=2"`. Aí a sabotagem morde.

### E um teste meu derrubou seis do gerador

A primeira versão do teste da variável de ambiente usava
`importlib.reload(mvp.dominio)`. Seis testes do `test_gerador.py` caíram:
o `scripts/gerar.py` faz `from mvp.dominio import carrega,
DominioInvalido`, e depois do reload ele continua apontando para a função
e a **classe** antigas — então o `pytest.raises` com a classe nova deixa de
pegar a exceção da antiga. Recarregar módulo no meio da suíte é efeito
colateral em todo mundo que importou dele. O teste virou **subprocesso**,
que é como o servidor recebe a variável de verdade.

## A descida interrogativa — o protótipo de uma crença

O pedido foi de ESTRUTURA, e não de mais conteúdo: o sistema mede a
crença, mas não testa a **profundidade** dela. A descida é essa peça.
Fica atrás de `STRUCTURA_DESCIDA=1`, com o fluxo de hoje intacto no
padrão, e o desenho inteiro está em [docs/descida.md](descida.md).

Em uma frase: em vez de AFIRMAR as premissas corretas e exibir a
contradição no fim, o sistema PERGUNTA o que decorre de tomar a crença
como verdadeira, até a consequência que a própria pessoa recusa.

### A inversão, e o cuidado que ela exige

Em toda atividade deste projeto a alternativa certa é a verdadeira. Num
degrau da descida, a que faz a cadeia **andar** é a falsa — é a previsão
da crença. Está escrito no cabeçalho do YAML e na docstring de `Passo`,
porque quem mexer nisso depois precisa saber antes de ler o arquivo.

### Três decisões que mudaram o desenho enquanto ele era escrito

**O "você confirmou" é do motor, não do texto.** A primeira versão do
último degrau dizia, no YAML, *"no começo desta unidade você afirmou
que..."*. O YAML não sabe o que aconteceu na sessão: se a premissa da
colisão não tiver fechado, essa frase é falsa, e atribuir a alguém o que
ela não afirmou derruba a única coisa que faz a descida funcionar. O
texto ficou neutro e o motor passou a decidir o rótulo — `VOCÊ
CONFIRMOU, NESTA SESSÃO` ou `ESTA UNIDADE AFIRMA`. Rodando a sessão de
verdade, a tela mostrou o segundo: `B1` tinha ficado frágil, numa
superfície só.

**A evidência diz de onde veio, ou não finge que veio.** Não há
compilador C nesta máquina. Em vez de inventar a mensagem do gcc, o
formato ganhou `origem: gravada | citada | pendente`, e a tela não
desenha terminal nenhum quando a origem é pendente: mostra o programa e a
garantia do padrão (ISO C 6.3.2.1p1), e diz que ninguém rodou. Uma tela
que promete evidência e mostra evidência inventada é pior que nenhuma
tela.

**"Não sei dizer" não fecha a conta pela pessoa.** Quem nem seguiu nem
contradisse não se convenceu de nada; o log registra
`descida_sem_resposta` e a tela vai para o fato, e não para o "você
mesmo acabou de dizer".

### O custo, medido

Mesma sessão do kc_07, mesma crença, mesma política:

| caminho | telas da sessão | telas do laço |
|---|---|---|
| refutação de hoje | 61 | 7 |
| descida, recua no 1º degrau | 56 | 2 |
| descida, recua no último | 59 | 5 |
| descida, sustenta até o fim | 59 | 5 |

### Dez sabotagens, dez testes caídos

Chave que não vale, descer sem cadeia escrita, dizer "você disse" sem
conferir, mostrar saída que ninguém gravou, a verdade não encerrando a
descida, o "não sei" perdendo para a alternativa marcada, índice fora da
cédula virando resposta, e três invariantes do carregador. Nenhuma passou
limpa.

### Um defeito do log, achado por acidente

A linha do log era montada com `{..., "tipo": e.tipo, **dados}`, e
`**dados` vem **depois**: um evento que trouxesse um dado chamado `tipo`
trocava o nome do próprio evento, sem erro nenhum. Aconteceu na primeira
sessão rodada: `evidencia_apresentada` levava o tipo da evidência num
campo `tipo` e saiu no log como uma linha `erro_de_compilacao` — nome que
a reexecução não conhece e que a análise contaria como outro evento.

Duas correções. O evento passou a chamar aquele campo de `evidencia`; e
`log._linha` passou a proteger os quatro campos da casa (`v`, `ts`,
`sessao`, `tipo`), escrevendo o dado colidente ao lado, com sufixo
`_do_evento`. Perder a sessão por causa de um nome de campo seria pior
que a colisão — quem está na frente da tela não tem culpa disso —, então
nada se perde e o sufixo é o sinal, visível na análise, de que alguém
precisa renomear aquele campo. Dois testes em `test_reconstrucao.py`.

Esse era o único evento do sistema com colisão; a varredura dos outros
não achou nenhum.

### Um erro de conteúdo, achado rodando

A figura do `B4` do kc_07 desenhava **quatro** casas e dizia *"sizeof a
mede as quatro"*, logo abaixo de um `int a[5]` que fala em cinco. Virou
cinco.

### O que não está provado

Nenhuma pessoa real passou pela descida. O que está medido é o custo em
telas e o comportamento do motor — não o efeito em quem aprende. E a
evidência continua pendente até alguém rodar o programa e gravar a saída.

## A crase saiu dos textos de tela, nos treze tópicos

Achado na tela, rodando a descida: o cliente escreve com `textContent` e
não interpreta marcação nenhuma, então a crase do YAML aparece como
crase na cara da pessoa. A pergunta do primeiro degrau saiu com os
acentos graves no meio da frase.

A varredura do domínio inteiro — os YAMLs carregados pelo PyYAML, que já
descarta comentário — achou **108 crases em valores**, em dois lugares:

| onde | quantas | vai para tela? |
|---|---|---|
| `analogy` e `resgates` do kc_03, kc_04 e kc_10 | 28 | **sim** |
| `source` das crenças, nos doze tópicos | 80 | não |

As 28 saíram. As 80 ficaram: `source` é a citação da procedência, lida no
YAML e nos docs por quem pesquisa, e nenhuma tela a mostra — nem o
painel. Marcação em texto que se lê como texto é marcação útil, e é por
isso que a regra escrita é *"o que vai para a TELA"*, e não *"o domínio
inteiro"*.

Nenhum texto precisou de reescrita: eles já nomeavam os símbolos por
inteiro (`int *p;`, `&x`, `*pp`), e tirar o acento não deixou letra solta
— ao contrário da descida, onde duas frases ganharam "o nome a" e "o
ponteiro p" porque "a" sozinho vira artigo.

A regra virou teste: `test_nenhum_texto_de_tela_usa_crase` varre, por
tópico, título, teach-back, analogia, texto e enunciado simples dos nós,
afirmação das crenças, enunciado/código/alternativas de toda atividade,
resgates, exemplos e os degraus e a evidência das descidas. Treze
tópicos, um caso cada. Sabotado em dois lugares diferentes — um resgate
do kc_04 e a primeira pergunta do kc_07 —, o teste cai nos dois.

## A evidência da descida deixou de ser pendente

Entrou um compilador na máquina — `winget install BrechtSanders.WinLibs.POSIX.UCRT`,
gcc 16.2.0 — e o programa da descida foi compilado de verdade. O campo
`saida` tinha ficado vazio semanas de propósito: a tela promete evidência,
e evidência inventada é pior que evidência nenhuma.

```
exemplo.c: In function 'main':
exemplo.c:6:7: error: assignment to expression with array type
    6 |     a = p;    /* esta nao     */
      |       ^
```

**O programa da tela mudou junto.** O que estava lá era um excerto que
*não compilava sozinho* — `p = a;` fora de função não é sentença. Evidência
de compilação tem de ser do programa que foi compilado, então virou um
`main` completo.

### Uma armadilha de instalação, que vale para a coleta

O `ld` do MinGW **não resolve o próprio prefixo quando há espaço no
caminho**, e o winget instalou em `C:\Users\Satya Pass\...`. Nada linkava:
*"cannot find C:/Users/Satya"*. Reinstalado em `C:\Users\Public\gcc`,
funciona. Se outra máquina entrar na coleta, isto é uma linha do
procedimento.

### Quatro testes caíram, e nenhuma regra tinha quebrado

Os quatro partiam do kc_07 real e **presumiam que a evidência dele era
pendente** — dois liam isso direto, dois montavam um domínio temporário
contando que o resto continuasse pendente. Gravar a evidência tornou a
premissa deles falsa.

O defeito era dos testes: eles amarraram uma regra de tela a um fato de
conteúdo que tinha todo o direito de mudar, e que mudou exatamente como o
formato previa. Cada um passou a **declarar a origem de que trata** na
própria fixture, com as asserções idênticas, e o fato novo ganhou teste
próprio (`test_a_evidencia_do_kc07_foi_rodada`).

### E a mudança revelou uma lacuna

A `afirmacao` era cobrada **só** quando a origem era pendente — mas a tela
a escreve nos três casos. Uma evidência gravada sem afirmação passava na
carga e chegaria à tela com a ideia em branco. Agora é obrigatória sempre,
e a `garantia` continua obrigatória só no pendente. Quatro sabotagens,
quatro testes caídos.

## Os moldes paramétricos — a fábrica do item, e o compilador como juiz

O pedido não foi mais conteúdo: foi **estrutura**. O sistema media a
crença e não testava a profundidade dela, e o que incomodava era a
escassez — sete itens por nó, rodar duas vezes é ver as mesmas
perguntas, e nenhum eixo para perguntar a MESMA ideia com a roupa
trocada.

Spec em [moldes.md](moldes.md), plano em [plano-moldes.md](plano-moldes.md),
doze tarefas, ramo `moldes`.

### O que ficou de pé

Um molde é a regra que produz o item: parâmetros, enunciado com buracos,
gabarito como **regra** e não como texto, cada distrator amarrado à sua
crença por id, e um **programa-oráculo** que, compilado e rodado com os
mesmos parâmetros, prova a afirmação em cada variação. Quatro portões de
máquina antes do humano, e a revisão passa do item para o molde: uma
leitura vale por todas as variações.

O log ganhou `do_molde` e `parametros`, e com eles três coisas que eram
invisíveis: generalizou, memorizou aquela pergunta, ou a crença é
robusta. O critério de domínio **não** mudou — é medida, não portão.

### O que a sonda mediu, antes de qualquer código

| | passaram | tempo |
| --- | --- | --- |
| molde certo | 20 de 20 | 0,34 s por variação |
| molde errado (`sizeof a == n`) | **2 de 20** | — |

As duas que passaram no molde errado foram as de `char`, onde a
afirmação é verdadeira. É o erro que passa batido numa revisão humana e
que o compilador pega em três décimos de segundo.

### A revisão do ramo achou o que eu não tinha achado

Um revisor de contexto fresco leu as treze commits. O achado **Critical**
era este: o `revisado_por` sobrevivia a qualquer edição do molde.
Preencher o nome, aprovar, e depois acrescentar um valor em `n:` — saíam
variações inéditas estampadas com o nome de quem nunca as leu. E não era
uso torto: a própria spec prescreve **editar** como conserto de molde
reprovado. Agora o nome vem com assinatura do conteúdo lido, e a carga
recusa quando ela não bate.

Mais quatro caminhos pelos quais item errado atravessava os quatro
portões: oráculo constante (que não confere nada e fica com cara de
conferido), `{extenso}` fora da faixa (o buraco literal na tela da
pessoa), `prever_saida` com o gabarito desatrelado do oráculo, e a certa
sendo a única alternativa em minúscula — pista de superfície que, num
molde, se repete em toda variação.

E a marca da generalização **nunca acendia**: a instância só era contada
no diagnóstico, e os moldes começam pelos itens de treino, que nunca
chegam lá.

### Um achado do revisor que não se confirmou

O relato dizia que aprovar item com id repetido descartava tudo em
silêncio. Medido: o `confere` roda antes e devolve *"atividade X
duplicada"*. A mensagem já existia; o teste é que não existia, e agora
existe. Relatório de agente também se confere.

### A armadilha do `no:`

Em YAML 1.1, `no` é o booleano **falso** — o problema da Noruega. O
campo sumia, e a mensagem natural mandava procurar no lugar errado. Os
arquivos do domínio nunca esbarraram nisso porque sempre usaram `node`.
O carregador agora reconhece a armadilha e diz o que escrever.

### E a quarta vez do mesmo defeito de teste

Um teste que mede CONTEÚDO em vez de REGRA. Já tinha acontecido com a
evidência da descida, com a folha dos candidatos, e com a sabotagem dos
extremos que passou limpa porque o fixture era pequeno demais. Desta vez
foram três de uma vez, e a regra está escrita aqui agora: **teste de
regra não se amarra a conteúdo que tem o direito de mudar.** Se o
conteúdo é o que importa, o teste é de conteúdo, e vive junto dele.

### O que não está feito

O primeiro molde espera a assinatura: **nenhum item de molde entrou no
domínio**. Os outros 64 nós não têm molde. E ninguém de carne e osso
respondeu a um item gerado.

## A família de formatos — a mesma afirmação, perguntada de três jeitos

A primeira fatia dos moldes multiplicou o eixo do **conteúdo** e deixou
o do **formato** como estava. O número apareceu na primeira sessão de
verdade: o banco de treino do `B1` foi de 3 para 9 itens, e **sete deles
do mesmo formato**. O motor prefere formato diferente a cada tentativa, e
confirmar exige duas superfícies — a regra ficou sem com que morder.

Spec na seção *A família de formatos* de [moldes.md](moldes.md), plano em
[plano-familia.md](plano-familia.md), dez tarefas.

### O que ficou de pé

O molde deixou de ser uma pergunta com buracos e passou a ser uma
**afirmação** perguntada de vários jeitos. Compartilhado: nó, parâmetros,
crenças e oráculo. Por formato: a redação, o código, e o oráculo quando
ele precisa ser outro.

A primeira família, no `B1`, pergunta a mesma coisa de três maneiras — e
a primeira variação é a **mesma nas três**, `int a[3]`, para que a troca
de formato seja a única coisa que mudou:

| formato | a pergunta |
| --- | --- |
| reconhecer_conceito | "o que existe na memória?" |
| achar_o_erro | "qual destas três linhas não compila?" |
| comparar_casos | "o que existe depois de `int a[3]; int *p;`?" |

Resultado medido: o banco de treino do `B1` passou de 7–1–1 em três
formatos para **3–3–2–1 em quatro**.

### Três decisões de conteúdo

**`prever_saida` ficou de fora desta família**, e não por custo: as duas
crenças do `B1` levariam à **mesma previsão** num item de prever a saída,
e dois distratores indistinguíveis não diagnosticam nada. O
`gabarito: do_oraculo` está implementado e testado; só não é este nó que
o estreia.

**Os seis itens da geração anterior saíram do domínio.** Eram saída de
uma versão anterior do mesmo molde, todos `reconhecer_conceito`, e mantê-
los ao lado dos novos era guardar a pergunta repetida — justamente o que
a fatia veio desfazer.

**A assinatura caiu, e isso foi a trava funcionando.** Converter o molde
em família é conteúdo novo: o `revisado_sha` deixou de bater e a carga
recusou, até a folha nova ser lida e assinada.

### O portão pegou um erro meu, e o oráculo pegou outro

O gabarito do `comparar_casos` começava por `{extenso}`, e a alternativa
certa virava a única em minúscula — em todas as variações daquele
formato. É a regra que eu tinha escrito na fatia anterior, mordendo o
meu próprio conteúdo na primeira expansão.

E o portão da variedade tinha um defeito que só a família revelou: ele
comparava o **enunciado**, e num formato de código o enunciado é fixo
enquanto o código varia. Duas variações legítimas de `achar_o_erro` eram
acusadas de duplicata uma da outra. Agora ele compara a pergunta inteira,
código mais enunciado, que é o que a pessoa lê.

### E a quinta vez do mesmo defeito de teste

Um teste que mede conteúdo em vez de regra — desta vez um que eu mesmo
escrevi na Tarefa 1 para proteger a assinatura do molde, e que a Tarefa
10 derrubou ao quebrar a assinatura **de propósito**. A regra que ele
defendia (família de um carrega como uma redação) já tinha teste próprio;
o que restou virou teste de conteúdo, onde fatos de conteúdo pertencem.

### Uma medida que não era medida

Numa rodada da suíte com a máquina carregada — 28 minutos contra os 75
segundos de sempre — um teste caiu, e passava sozinho. Com a máquina
quieta, 702 verdes. O oráculo tem timeout de dez segundos por programa, e
sob carga um `gcc` estoura isso. Vale a mesma regra que já está escrita
aqui: **medida de tempo se toma com a máquina quieta** — e agora também
medida de teste que depende de compilador.

### A revisão do ramo achou o defeito que a camada do oráculo existe para impedir

Quatro Critical, oito Important, dez Minor — e o revisor produziu os itens
defeituosos de verdade, em vez de os descrever.

**Os três primeiros Critical são um só esquecimento.** A fatia moveu
`codigo`, `oraculo` e `espera` para dentro de `formatos:`, e as
validações continuaram olhando os campos de topo. Resultado: um molde com
`int a[{tamanho_errado}]` na tela da pessoa, um oráculo constante que roda
o mesmo programa para `n=3` e `n=8`, e um "qual destas duas linhas não
compila?" sobre duas linhas corretas, com a resposta certa apontando uma
terceira que a pessoa não vê. **Os três passavam com a suíte inteira
verde.**

Agora há um lugar só onde essas regras moram — uma varredura por redação,
sobre o oráculo e o `espera` *efetivos* — e sete regras nela, cada uma
sabotada em separado para ver o teste dela cair.

**O quarto Critical é o que importa mais, e é sobre a minha camada de
prova.** O portão do oráculo rodava o compilador nas seis variações
*sorteadas* e declarava o molde provado para as sessenta e quatro. O
`comparar_casos` do `B1` afirmava `sizeof {nome} != sizeof p`, e isso é
**falso** para `char {nome}[8]`: oito bytes dos dois lados. Uma em
dezesseis, e a expansão não a sorteava.

Isto é exatamente o defeito que a camada do oráculo foi escrita para
impedir — um molde errado erra em todas as variações de uma vez —, e ele
passou pela própria camada, porque a camada amostrava. O portão agora
varre o produto dos parâmetros: 64 combinações por formato, 192
compilações para este molde.

E a folha, que é o que a pessoa lê antes de assinar, dizia "em TODA
variação". Era verdade sobre as sorteadas e mentira sobre o molde: a
assinatura dela passava a cobrir uma garantia que ninguém tinha dado.
Agora sai o número da varredura.

#### O que a varredura custou, e por que não dá para cobrar barato

A suíte foi de 87 segundos para **doze horas e meia**. Não é a conta das
compilações (seriam uns cinco minutos): sob carga sustentada o `gcc`
começa a estourar o timeout de dez segundos do oráculo, e aí a lentidão
vira *falha*. É a mesma armadilha que já está escrita aqui — medida de
tempo se toma com a máquina quieta —, agora mordendo o próprio gate.

Os testes que chamam o compilador ganharam um domínio de oito
combinações; o que precisa de domínio grande declara o seu. A suíte fechou
em **183 segundos**, e a varredura continua inteira onde ela vale: no
molde de verdade.

#### Uma suspeita minha que não se confirmou

Consertando o portão da variedade do `aprova`, li
`novos = [a for a in aprovados if a["id"] not in ja]` e concluí que um id
já presente era descartado em silêncio — o que importaria muito, porque
reexpandir um molde corrigido devolve os **mesmos ids** com texto novo.
Não é o que acontece: `confere` carrega o domínio com os candidatos
dentro, e o carregador recusa id duplicado antes de qualquer filtro. A
suspeita virou teste, para o dia em que alguém trocar a ordem das duas
coisas.

O que fica dela, e é operacional: **reexpandir e aprovar não substitui os
itens velhos.** Corrigir um molde exige apagá-los do domínio de propósito,
num commit que se vê.

#### A assinatura caiu pela segunda vez no mesmo ramo

Converter o molde em família quebrou a assinatura; corrigir o oráculo e os
distratores quebrou de novo. As duas vezes a trava funcionando, e as duas
vezes com o mesmo preço: os itens que já estavam no banco saíram de um
molde que não existe mais, e têm de ser reexpandidos.

É o segundo lugar onde este ramo encontra o mesmo problema — o primeiro
está em [moldes.md](moldes.md), no risco em aberto do CS-6: o log não
grava impressão digital do banco, e corrigir um molde reescreve itens com
os mesmos ids.

## A posição da alternativa certa — 98,4% num canto do gabarito

Medida antes de qualquer código: nos 562 itens dos treze tópicos, a
resposta certa estava na **primeira** alternativa em 553 — 98,4%, e
nenhuma em terceira.

Isso não é detalhe de apresentação. Um participante que repare no padrão
acerta sem saber o conteúdo, e o instrumento passa a medir, em parte,
quem reparou. Como o viés é **sistemático**, ele não some na média de 40
pessoas. E ele contamina justo a medida central do trabalho: quem acerta
por posição ainda escolhe uma razão, e o par sai "acerto com razão
errada" — que o CS-1 lê como falso positivo. O viés produziria falsos
positivos em massa, e eles pareceriam achado.

Spec em [posicao.md](posicao.md), plano em
[plano-posicao.md](plano-posicao.md), cinco tarefas.

### O achado do desenho: a permutação já existia

Não houve decisão nenhuma por trás dos 98,4%. O motor **já tinha** a
permutação estável — `ordem_das_razoes`, escrita no ciclo 1 —, e ela
cobria a camada 2. A camada 1 ficou de fora, e a tela entregava
`a.opcoes` na ordem crua do YAML, que escreve a certa em primeiro porque
é assim que um humano escreve um gabarito.

A promessa estava escrita e não cumprida em dois lugares: no docstring de
`Resposta` (*"`escolha` é a posição na tela"*) e no de `log.reconstroi`
(*"a ordem das alternativas vem da semente, que é o código da sessão"*).

| | antes | depois |
| --- | --- | --- |
| certa em `a` | 553 (98,4%) | 182 (32,4%) |
| certa em `b` | 9 (1,6%) | 186 (33,1%) |
| certa em `c` | 0 | 194 (34,5%) |

Como a semente é o código da sessão, cada participante vê uma ordem
diferente: o que o P03 contar ao P04 não transfere.

### O risco de verdade não era o embaralhamento

Era `Atividade.indice_correto`, usado por 22 chamadas. No dia em que a
permutação existisse, aquele índice apontaria outra alternativa — e o
motor **aceita**: não é erro de programa, é uma resposta errada. A escada
desce em vez de subir, a crença errada é registrada, e a suíte fica verde
contando outra história.

Por isso a renomeação para `indice_correto_no_arquivo` foi uma tarefa
inteira, **antes** de qualquer mudança de comportamento: ela troca 22
erros silenciosos por 22 `AttributeError`.

Funcionou: ligar a permutação derrubou **61 testes** de uma vez. E eles
mostraram que o problema era maior do que o nome — quem escolhe a
**errada** também escolhia por posição de arquivo, e com a tela permutada
aquela posição às vezes é a certa. O pior caso virava acerto, e os nós
saíam `confirmado` num teste chamado *"nenhuma premissa fica sem
medida"*.

### Duas políticas que diziam uma coisa e faziam outra

Errar "por este nó" estava escrito como *"a primeira errada do arquivo"*.
Dava no mesmo por convenção de escrita — o YAML põe o distrator da crença
do próprio nó em primeiro. Com a tela permutada, a primeira da tela é
outra crença, e a refutação caía no **vizinho**: comportamento correto do
CS-2 sobre uma entrada que o teste não queria dar.

Agora as duas escolhem a crença **do item**. Não é afrouxar teste; é
escrever a intenção que o docstring já declarava.

### A renomeação em massa comeu o próprio teste da trava

`hasattr(a, "indice_correto")` virou `hasattr(a, "indice_correto_no_arquivo")`
— que passa e afirma o contrário. O nome velho agora está escrito por
partes, com o motivo ao lado. A fatia demonstrou em si mesma o defeito
que ela existe para impedir.

### E um portão que rodou contra ontem

O caminhante é o portão de ponta a ponta, e por duas rodadas ele mediu um
servidor que subira **no dia anterior**, com código velho, e continuava
na porta 8010 — o `pkill` do Git Bash não o matou. A comparação
master-contra-ramo ficou inválida e parecia regressão: o cliente novo
calculava posição de tela contra um servidor que não permutava.

Com servidor novo: 52 passos, tudo confirmado, igual ao master. Fica a
regra, do mesmo tamanho da que já está escrita sobre medir tempo com a
máquina quieta: **conferir `/saude` e o PID antes de usar o caminhante
como portão.**

### O que esta fatia não fez

A escala de confiança **não** é embaralhada, e tem teste pinando isso:
`("chutei", "acho que sei", "tenho certeza")` é ordinal, a ordem dela *é*
a escala, e o viés nem existe ali porque nenhuma das três é a certa.

O YAML não se mexeu, nem os 562 itens: a certa continua escrita em
primeiro, a folha de revisão continua mostrando `**[certa]**` em
primeiro, e a assinatura de quem revisou molde continua valendo. A
permutação não é conteúdo.

## A varredura dos treze — o portão de conteúdo fora do kc_02

390 sessões: treze tópicos, três personas, dez sessões cada, oito minutos
de parede. **Nenhuma quebra, e nenhuma premissa sem medida em nenhuma
sessão.** A superfície HTTP se comporta como a suíte de unidade dizia.

Um servidor por tópico, porque `dominio = carrega()` roda no import. O log
foi para fora da árvore (`STRUCTURA_LOG`), que é a regra de sempre: sessão
simulada não entra no banco do piloto. E o portão conferiu `/saude` antes
de medir e a morte do servidor antes do próximo subir — a regra que a
fatia da posição deixou escrita, aplicada treze vezes.

### Uma correção minha, antes dos números

Eu tinha dito, ao propor a varredura, que o portão de conteúdo só havia
rodado em dois dos treze tópicos. **Isso está errado para a suíte.**
`dominio.topicos()` descobre os treze no disco, e **16 funções de teste
são parametrizadas sobre todos eles**, em cinco arquivos — incluindo as
três de `test_medida.py` que cobram a CS-10. Nenhum tópico estava fora, e
a frase "os cinco tópicos" num comentário de lá é texto de quando havia
cinco.

O que a varredura compra, então, não é cobertura da CS-10: é a **superfície
HTTP** (telas, rotas e log de verdade, onde a medição do kc_02 achou o que
virou o ciclo 3), a **semente por sessão** (cada código permuta as duas
camadas de outro jeito, enquanto os testes usam política fixa) e o **custo
em passos por tópico**, que só o kc_02 tinha.

### O custo em passos, e ele é função do número de nós

| kc | nós | acerta tudo | erra e aprende | não muda de ideia |
| --- | --- | --- | --- | --- |
| kc_00 | 5 | 38 | 63 | 60 |
| kc_01 | 5 | 38 | 68 | 72 |
| kc_02 | 6 | 45 | 84 | 89 |
| kc_03 | 6 | 45 | 86 | 92 |
| kc_04 | 6 | 45 | 83 | 87 |
| kc_05 | 6 | 45 | 82 | 88 |
| kc_06 | 6 | 45 | 85 | 91 |
| kc_07 | 7 | 52 | 95 | 102 |
| kc_08 | 6 | 45 | 82 | 88 |
| kc_09 | 8 | 59 | 113 | 120 |
| kc_10 | 6 | 45 | 82 | 88 |
| kc_11 | 6 | 45 | 82 | 88 |
| kc_12 | 6 | 45 | 82 | 88 |

Medianas de dez sessões. Os dez tópicos de 6 nós são indistinguíveis entre
si — **o custo não depende do conteúdo, depende da forma**: ~15 passos por
nó no caminho difícil. O kc_09, com 8 nós, custa **35% mais que o piloto**.
Isso reformula a pergunta do orçamento do PRD: não é "o tópico cabe em 30
minutos", é "**quantos nós** cabem em 30 minutos" — e a resposta continua
sendo de pessoa, não de medição em cliques.

### Os números do roteiro do ensaio envelheceram

[ensaio-roteiro.md](ensaio-roteiro.md) diz *42 / 81 / 118* para o kc_02.
Hoje: **45 / 84 / 89**. O caminho difícil encurtou um quarto, que é o
quarto teto cortando a cauda — consistente com o que o ciclo 3 prometeu.

O `+3` uniforme nas três personas eu **não rastreei**. Pode ser tela nova
de alguma fatia posterior, pode ser outra coisa; não atribuí, e não vou
escrever palpite aqui como se fosse medida.

### O kc_00 trunca, e era previsível na aritmética

`em_aberto` em 10 de 10 sessões do `crente`. A causa estava nas constantes
antes de qualquer corrida: `STREAK_ALVO = 2` no diagnóstico e
`TETO_TENTATIVAS = 4` no treino pedem até **6 itens** por nó, e o kc_00 tem
**4** — contra 7 a 13 de todos os outros.

> **Corrigido depois.** Esta seção dizia também que o kc_00 era o único
> tópico onde o `aprende` terminava com `falso_positivo`, e eu li isso
> como propriedade do conteúdo dele. **Era artefato do portão** — ver "O
> defeito que a quarta persona desenterrou", abaixo. Com o defeito
> consertado, `falso_positivo` não aparece em tópico nenhum. O que
> continua de pé é o truncamento, que é aritmética das constantes e não
> depende daquele defeito.

Como o kc_00 é pré-requisito e não objeto da medida (decisão 17), isso pode
ser aceitável. É decisão do dono, não constatação: ou o banco dele cresce,
ou fica registrado que aquele tópico mede menos do que os outros.

### O achado que paga a varredura: as personas são limpas demais

Em **12 dos 13 tópicos** o `aprende` termina 100% `confirmado` e o `crente`
termina 100% `em_aberto`. Nenhum `lacuna` em tópico nenhum, nenhum `fragil`
em tópico nenhum.

O motivo é de uma linha: **nenhuma das três personas diz "não sei"** — zero
ocorrências de `nao_sei` em `scripts/caminhante.py`. A **CS-4** (*"não sei"
em qualquer camada produz lacuna, nunca crença*) tem 31 asserções na suíte
de unidade e **nunca roda pela tela**. O portão de ponta a ponta produz os
dois extremos do espaço de estados e nada do meio.

E um defeito pequeno do próprio portão, do mesmo lado: o `sem_medida` dele
só conta `desconhecido` e `nao_medido`. Nesta varredura não escondeu nada —
mas `refutado` e `em_treino` também ficam de fora, e esses dois **são** fim
de sessão quebrado. Um portão que diz "0 sem medida" numa sessão que parou
no meio da refutação está mentindo com a verdade.

### O que a varredura NÃO estabeleceu

Nada sobre minutos: tudo aqui é clique. Nada sobre o efeito em quem
aprende. Nada sobre o meio do espaço de estados, que é justamente o que a
quarta persona existe para alcançar. E nada sobre a descida — ela está
desligada por padrão, e estas 390 sessões passaram todas pela refutação
afirmativa.

## A quarta persona, e o que ela desenterrou

A varredura mandou construir uma persona que diz "não sei", e ela entrou
com 23 testes (`mvp/test_caminhante.py`); a suíte foi de **737 para 760**.

Ela diz "não sei" na **camada 2 sempre** e na **camada 1 em metade dos
itens**, decidida pelo sha256 do id do item — não sorteada, porque portão
que muda de resultado sem o código mudar não é portão. E a metade existe
por um motivo de motor: um "não sei" na camada 1 **encerra o episódio**, e
uma persona que dissesse sempre cobriria só a camada 1, deixando a camada 2
— o buraco de verdade — descoberta.

Junto, dois consertos no próprio portão: `sem_medida` passou a contar
`refutado` e `em_treino` (ambos são sessão parada no meio), mantendo
`em_aberto` fora, porque o projeto já decidiu que ele é medida.

### O defeito que a quarta persona desenterrou, e ele era das antigas

O teste "quem deve errar não acerta" caiu, e não pela persona nova. O
caminho de quem não está convencido fazia:

```python
next(i for i, o in enumerate(na_tela) if o.crenca == a.crenca)
```

Com `a.crenca` nulo, isso é `None == None`, e casa a alternativa cuja
crença também é nula — **a certa**. Três itens dos 562:

```
kc_00  ciu_kc00_001   B1   diagnostico
kc_00  ciu_kc00_t02   B1   treino
kc_02  ciu_kc02_t12   I1   treino
```

O de **diagnóstico** é o que importa: ali o `crente` acertava, nenhuma
crença era detectada, a refutação não acontecia — e escolhendo uma crença
como razão em seguida, o episódio saía `falso_positivo`. Era a origem do
`falso_positivo` do kc_00 que a primeira varredura mediu e que eu li como
conteúdo. Plausível e errado, na própria ferramenta de medir: o portão
rodava verde e media outra coisa.

Consertado com `a.crenca is not None` na condição, e preso por um teste
parametrizado nos treze tópicos sobre as **três** personas que erram.

### Os números com as quatro personas, e o defeito fora

| kc | nós | acerta tudo | erra e aprende | não muda | não sabe |
| --- | --- | --- | --- | --- | --- |
| kc_00 | 5 | 38 | 64 | 57 | 27 |
| kc_01 | 5 | 38 | 68 | 72 | 37 |
| kc_02 | 6 | 45 | 84 | 89 | 78 |
| kc_03 | 6 | 45 | 86 | 92 | 45 |
| kc_04 | 6 | 45 | 83 | 87 | 50 |
| kc_05 | 6 | 45 | 82 | 88 | 49 |
| kc_06 | 6 | 45 | 85 | 91 | 52 |
| kc_07 | 7 | 52 | 95 | 102 | 55 |
| kc_08 | 6 | 45 | 82 | 88 | 46 |
| kc_09 | 8 | 59 | 113 | 120 | 62 |
| kc_10 | 6 | 45 | 82 | 88 | 49 |
| kc_11 | 6 | 45 | 82 | 86 | 48 |
| kc_12 | 6 | 45 | 82 | 88 | 47 |

520 sessões, nenhuma sem medida. O kc_00 mudou com o conserto (`crente` de
60 para 57), que é o esperado de um tópico que tinha dois dos três itens
defeituosos.

### E o achado novo é maior que o que mandou fazer a persona

A CS-4 passou a rodar pela tela: `lacuna` em 130 de 130 sessões da persona
nova, nos treze tópicos. Mas o quadro inteiro ficou assim:

| persona | o que ela produz |
| --- | --- |
| `sabido` | `confirmado` — 130 de 130 |
| `aprende` | `confirmado` — 130 de 130 |
| `crente` | `em_aberto` — 130 de 130 |
| `nao_sabe` | `lacuna` — 130 de 130 |

**Quatro personas, quatro extremos puros.** Cada uma produz um estado só,
uniforme nos treze tópicos. O espaço alcançado pela tela é de três estados
dos oito do motor: `confirmado`, `em_aberto` e `lacuna`.

E o que falta é o pior possível: **`falso_positivo` não é produzido por
persona nenhuma**. Esse é o estado da **CS-1** — *um acerto com razão
errada não confirma a premissa* —, que é a medida central do trabalho
inteiro. Para produzi-lo é preciso **acertar a camada 1 e errar a camada
2**, e as quatro personas são internamente consistentes: quem acerta a
resposta acerta a razão, quem erra erra as duas. Nenhuma é incoerente, e a
incoerência é exatamente o fenômeno que o instrumento existe para medir.

`fragil` também não aparece, e por outro motivo: ele é uma premissa
confirmada numa superfície só, isto é, sessão truncada — não há política
que o produza de propósito.

**A quinta persona, então, não é opcional:** é a que acerta pela razão
errada, e ela é a única que exercita pela tela o critério número um. A
CS-4 estava descoberta; a CS-1 está descoberta, e vale mais.

## A quinta persona e o portão que passou a ver o meio

A varredura com quatro personas concluiu que `falso_positivo` não era
produzido por nenhuma — e a conclusão estava **certa pelo motivo errado**.
As duas coisas foram consertadas juntas.

### A quinta persona: a única incoerente das cinco

`explica_mal` acerta a camada 1 e escolhe crença na camada 2. É a única
persona internamente **incoerente**, e a incoerência é exatamente o
fenômeno que o instrumento existe para medir: as quatro anteriores
acertavam as duas camadas ou erravam as duas, e por isso nenhuma produzia
o estado da CS-1.

Vai com `tenho certeza` de propósito. `classifica` devolve
`falso_positivo` em qualquer confiança, e alguém **convicto** de uma
explicação torta é o caso que mais exige do instrumento.

O teste dela amarra a persona ao **critério**, não à intenção: passa a
razão escolhida pela própria `motor.classifica` e cobra
`FALSO_POSITIVO_EP` — a função que a banca lê linha a linha —, com a tela
de razão montada como o motor monta (`razoes_de` do grafo, permutada por
`ordem_das_razoes`), parametrizado nos treze tópicos.

### O limite do portão, que ela expôs

No kc_02 a sessão do `explica_mal` termina com todos os nós
`confirmado`, e está **correto**: dois falsos positivos na mesma crença
disparam `crenca_detectada`, vem refutação, vem treino, e o treino
confirma. `falso_positivo` é transitório por desenho.

Olhando só o estado final, o portão nunca poderia tê-lo visto — nem
quando ele acontece 36 vezes em três sessões. O instrumento trabalha no
meio, e o portão fotografava só o fim.

A fonte do conserto é o `veredito` que o servidor manda em **toda**
resposta: quem classifica é o motor, não o cliente, e é a mesma decisão
que a tela mostra à pessoa. De propósito **não** fui ler o log, mesmo
tendo usado o log como prova: o veredito da resposta é o que o
participante vê, e ler o log faria o portão medir uma segunda fonte
deixando a primeira sem verificação.

`VEREDITO DESCONHECIDO NÃO É CALADO`: vem depois dos conhecidos em vez de
ser filtrado fora. Filtrar pela lista que o portão conhece faria um
veredito novo do motor sumir do relatório sem ninguém notar — o mesmo
defeito que esta mudança conserta, um nível acima.

### Os episódios dos treze tópicos, 130 sessões por persona

| persona | episódios |
| --- | --- |
| `sabido` | `certa=1580` |
| `aprende` | `certa=2360` `crenca=790` |
| `crente` | `errada=3882` `crenca=790` |
| `nao_sabe` | `lacuna=2500` `errada=740` |
| `explica_mal` | `certa=2040` **`falso_positivo=781`** `crenca=690` |

E os estados finais, que é onde a leitura anterior se enganou:

| persona | estado final dos nós |
| --- | --- |
| `sabido` | `confirmado` — 130/130 |
| `aprende` | `confirmado` — 130/130 |
| `crente` | `em_aberto` — 130/130 |
| `nao_sabe` | `lacuna` — 130/130 |
| `explica_mal` | `confirmado` 130/130 e **`falso_positivo` em 82/130** |

**Duas correções de leitura minha ficam registradas.** A primeira: "quatro
extremos puros" era verdade dos estados FINAIS, não dos episódios — o
`nao_sabe` produz 740 episódios `errada` e o `aprende` mistura 790
`crenca`. A segunda: o `explica_mal` **termina** em `falso_positivo` em 82
das 130 sessões; o "todos `confirmado`" que eu observei era específico do
kc_02, e eu generalizei de um tópico.

E a porta de refutação que só ela atravessa, medida no log do kc_02:

```
explica_mal   36 eventos falso_positivo   18 crenca_detectada, TODAS por
                                          "falso positivo repetido"
aprende        0 eventos falso_positivo   18 crenca_detectada, pelo
                                          caminho comum
```

### O custo em passos, com as cinco

| kc | nós | sabido | aprende | crente | não sabe | explica mal |
| --- | --- | --- | --- | --- | --- | --- |
| kc_00 | 5 | 38 | 64 | 57 | 27 | 62 |
| kc_01 | 5 | 38 | 68 | 72 | 37 | 72 |
| kc_02 | 6 | 45 | 84 | 89 | 78 | 102 |
| kc_03 | 6 | 45 | 86 | 92 | 45 | 104 |
| kc_04 | 6 | 45 | 83 | 87 | 50 | 90 |
| kc_05 | 6 | 45 | 82 | 88 | 49 | 100 |
| kc_06 | 6 | 45 | 85 | 91 | 52 | 80 |
| kc_07 | 7 | 52 | 95 | 102 | 55 | 105 |
| kc_08 | 6 | 45 | 82 | 88 | 46 | 89 |
| kc_09 | 8 | 59 | 113 | 120 | 62 | 120 |
| kc_10 | 6 | 45 | 82 | 88 | 49 | 90 |
| kc_11 | 6 | 45 | 82 | 86 | 48 | 89 |
| kc_12 | 6 | 45 | 82 | 88 | 47 | 89 |

650 sessões, nenhuma sem medida. O `explica_mal` é o caminho **mais
caro** do instrumento — 104 passos no kc_03 contra 92 do `crente` —, e
faz sentido: ele passa pela refutação como quem erra, mas chega lá depois
de gastar itens acertando.

### O que ainda falta, e o que a suíte não protege

O espaço alcançado pela tela subiu de três para **quatro** dos oito
estados: `confirmado`, `em_aberto`, `lacuna` e `falso_positivo`.

`fragil` continua fora, e agora o motivo é nomeável: ele é acerto com
razão certa e confiança **abaixo** de certeza (`classifica`). Nenhuma das
cinco personas duvida enquanto acerta. Uma sexta — *acerta mas duvida* —
é o que falta, e ela não é cosmética: `fragil` é o estado que sustenta a
CS-5, porque uma premissa frágil é a que foi confirmada numa superfície
só.

E um achado de ferramenta: **a suíte e o portão de ponta a ponta não são
seguros em paralelo**, e nada avisa. O teste
`test_o_ensaio_imprime_os_comandos_com_o_ambiente_montado` roda
`scripts/ensaio.sh` como subprocesso, e o portão de porta do `ensaio.sh`
recusa quando alguém atende na 8010 — então uma varredura em andamento faz
a suíte dar **vermelho sem defeito**. É a mesma classe do servidor-de-ontem
que já está escrita aqui, na direção contrária: antes um servidor velho
fez o portão mentir verde; aqui um servidor legítimo faz a suíte mentir
vermelho.

## A sexta persona fecha `fragil` — e eu errei o motivo de ela ser visível

`duvida` acerta as duas camadas e marca `acho que sei`, o meio da escala.
Pela decisão 11 o meio puxa para o lado conservador de cada linha, e
`classifica` devolve `FRAGIL_EP` em vez de `CONFIRMADA`. É a **única
persona cuja diferença não está em escolha nenhuma** — ela escolhe igual
ao `sabido`, e o que a separa é a camada 3.

O teste tem o contraste embutido, e é ele que prova que a persona é o que
diz ser: as **mesmas** duas escolhas, com `tenho certeza`, dão
`CONFIRMADA`. Escolha disfarçada dentro dela faria esse par cair.

### A correção: `no_fragil` não identifica esta persona

Eu afirmei, ao commitar (`75ed38e`), que sem `no_fragil` nos transitórios
a sexta persona seria invisível ao portão. **Está errado**, e a varredura
dos treze mostrou isso no mesmo dia. O evento tem **duas** causas no
motor:

```
"uma superfície só"            <- a causa da CS-5
"confiança abaixo de certeza"  <- a causa da decisão 11
```

O `sabido` emite **790** `no_fragil` — pela primeira causa, no primeiro
acerto de cada nó, antes de a segunda superfície confirmar. É o
comportamento normal da CS-5, não fragilidade de ninguém.

O que identifica a `duvida` é o **estado final**: `fragil` em 130 de 130,
e ela é a única persona que termina ali. O transitório continua útil para
ver passagens de fragilidade, mas não distingue as duas causas — e **não
pode**, porque a resposta HTTP manda só o *tipo* do evento, não o
`motivo`. Separá-las exigiria mudar o que o servidor devolve, e isso é
decisão de interface que não tomei.

### Os números das seis, 130 sessões cada, 780 no total

| persona | episódios | estado final | no meio |
| --- | --- | --- | --- |
| `sabido` | `certa=1580` | `confirmado` 130 | `no_fragil=790` |
| `aprende` | `certa=2360` `crenca=790` | `confirmado` 130 | `crenca_detectada=790` |
| `crente` | `errada=3882` `crenca=790` | `em_aberto` 130 | `crenca_detectada=790` |
| `nao_sabe` | `lacuna=2500` `errada=740` | `lacuna` 130 | — |
| `explica_mal` | `certa=2040` `falso_positivo=781` `crenca=690` | `confirmado` 130, `falso_positivo` 82 | `crenca_detectada=690` `falso_positivo=1471` |
| `duvida` | `certa=2500` | **`fragil` 130** | `no_fragil=2500` |

**Episódio e evento não são a mesma medida, e a tabela não os mistura por
descuido.** O `explica_mal` tem 781 episódios `falso_positivo` e 1.471
eventos: o episódio é um por passo, pelo `veredito`, e o evento é cada
emissão — um passo pode emitir mais de um, e o `veredito` reporta o
primeiro. Quem for comparar os dois números precisa saber disso.

E o `duvida` tem `certa=2500` em episódio: o veredito de um acerto frágil
é **`certa`**, porque `fragil` não é veredito. A assimetria com
`falso_positivo`, que **é** veredito, fica registrada abaixo.

### O custo em passos, com as seis

| kc | nós | sabido | aprende | crente | não sabe | explica mal | duvida |
| --- | --- | --- | --- | --- | --- | --- | --- |
| kc_00 | 5 | 38 | 64 | 57 | 27 | 62 | 38 |
| kc_01 | 5 | 38 | 68 | 72 | 37 | 72 | 53 |
| kc_02 | 6 | 45 | 84 | 89 | 78 | 102 | **117** |
| kc_03 | 6 | 45 | 86 | 92 | 45 | 104 | 63 |
| kc_04 | 6 | 45 | 83 | 87 | 50 | 90 | 63 |
| kc_05 | 6 | 45 | 82 | 88 | 49 | 100 | 63 |
| kc_06 | 6 | 45 | 85 | 91 | 52 | 80 | 63 |
| kc_07 | 7 | 52 | 95 | 102 | 55 | 105 | 73 |
| kc_08 | 6 | 45 | 82 | 88 | 46 | 89 | 63 |
| kc_09 | 8 | 59 | 113 | 120 | 62 | 120 | 83 |
| kc_10 | 6 | 45 | 82 | 88 | 49 | 90 | 63 |
| kc_11 | 6 | 45 | 82 | 86 | 48 | 89 | 63 |
| kc_12 | 6 | 45 | 82 | 88 | 47 | 89 | 63 |

O `duvida` custa 63 passos em dez tópicos e **117 no kc_02** — o maior
número do instrumento inteiro. A causa é o banco: o kc_02 tem 10 itens
por nó contra 7 dos outros, e uma persona que nunca confirma gasta
superfícies até o teto. O kc_02 é o tópico do piloto, e isso quer dizer
que **o caminho mais caro da coleta é o de quem sabe e duvida**, não o de
quem não sabe.

### O placar do espaço de estados

Cinco dos oito estados do motor são alcançados pela tela:
`confirmado`, `em_aberto`, `lacuna`, `falso_positivo` e `fragil`.

Os três que faltam são de outra natureza, e nenhum é persona:
`desconhecido` e `nao_medido` existem para o caso que o laço não alcançou
— produzi-los de propósito seria fabricar defeito —, e `refutado` e
`em_treino` são estados de meio de caminho que só apareceriam numa sessão
interrompida. Uma persona que abandona a sessão no meio é o que falta
para esses dois, e ela mede **queda**, não aprendizagem.

### Uma pergunta que é do dono

**`fragil` deveria ser um veredito?** A pessoa que acerta duvidando vê a
tela dizer "certa", e o sistema por dentro **não confirmou** a premissa
dela. Pela decisão 13 — *o falso positivo é contado à pessoa, porque
calar desperdiça o único momento em que ela percebe a própria rota
torta* — o argumento simétrico diria que a fragilidade também deveria
ser contada. Não mexi: é regra de interface e de instrumento.

## O portão de pré-requisito, e um princípio sobre o que um teste pode criar

**O princípio, e ele vale para o projeto inteiro:**

> Um teste pode criar mundos pedagógicos explícitos para exercitar o
> mecanismo, mas nunca pode transformar esses mundos artificiais em
> evidência de que o conteúdo foi ensinado na disciplina real.

### A medição que obrigou o portão

Atravessando o kc_02 como participante, e depois medindo nas 180
detecções de crença da varredura:

| | |
| --- | --- |
| Detecções no **nível 1** | **135 de 180** |
| Depois de **um erro só** | 99 |
| `sizeof`, no tópico | só em item de **nível 2** |
| `int **`, no tópico | só em item de **nível 3** |
| `scanf` | **em lugar nenhum** |

A pessoa cai na descida antes de encontrar qualquer um dos três, e
responde no chute um degrau que deveria medir a crença dela.

**"Está no material" era o critério errado, e era o meu.** O certo tem
duas partes: o recurso aparece no tópico, **e** aparece em ENSINO. Item
de prova não autoriza o uso numa cadeia de recuperação — é por isso que
`so_avaliado` é um estado próprio e não um sinônimo de disponível.

### Os quatro estados, e a lista que começa vazia

`disponivel` · `so_avaliado` · `nao_introduzido` · `desconhecido`

O padrão é **desconhecido**: id que ninguém declarou não libera nada,
senão errar o nome do conceito viraria autorização. E
`mvp/dominio/conceitos.yaml` começa **vazio**, de propósito — com ele
vazio as sete cadeias ficam bloqueadas e o sistema cai na refutação
afirmativa em todo lugar. Uma lista preenchida por suposição faria o
portão medir a suposição de quem a escreveu sobre a ementa da
disciplina.

Cada entrada liberada carrega `introduzido_em` e `evidencia`: a
rastreabilidade é o que separa isto de uma lista de desejos, e há teste
cobrando as duas.

### O esquema do degrau

Cada degrau declara a **função pedagógica** — `explicitar`, `confrontar`
ou `reconstruir` — e os conceitos que **requer**. A carga recusa o que
não declarar, e cobra duas coisas de cada cadeia: o último degrau tem de
ser `reconstruir`, e algum degrau tem de `confrontar`.

As duas regras têm motivo. Terminar na contradição deixa a pessoa
sabendo que a ideia dela não fecha e sem nenhuma no lugar — que é o
estado em que uma crença volta, não o estado em que ela é trocada. E só
explicitar e reconstruir é uma aula, não uma refutação.

`requer: []` é declaração válida; `requer` ausente é erro. A diferença
importa: lista vazia diz "nada além do que o tópico ensina", campo
ausente diz que ninguém decidiu.

### O que isso custou, e por que não foi afrouxado

Ligar o portão derrubou **20 dos 31 testes de `test_descida.py`** — todos
de MECANISMO, nenhum por defeito. Eles exercitam fechamento,
profundidade, retomada e o "não sei", e ficaram reféns da
disponibilidade de conteúdo, que é outra responsabilidade.

A saída **não** foi afrouxar o portão nem preencher o inventário. Foi dar
aos testes de mecanismo um inventário próprio, por
`STRUCTURA_CONCEITOS`, declarado numa fixture rotulada como mundo
artificial, com o aviso de que não é evidência curricular. **Nenhuma
asserção existente mudou.**

E o portão continua cobrado contra o inventário de verdade, em
`mvp/test_prerequisito.py`: inventário vazio bloqueia as seis, conceito
só avaliado não libera, conceito não introduzido bloqueia, inventário
incompleto não libera, e inventário completo libera **só** a cadeia
autorizada. Mais um teste de integração que percorre uma sessão inteira
com a descida ligada e o inventário real vazio, e confirma que nenhum
evento de descida aparece — é ele que garante que a fixture não virou
liberação implícita em algum ponto do caminho.

### O que o ciclo de recuperação JÁ fazia, medido

A pergunta era se o sistema faz: erro → cadeia de confronto → **questão
de transferência** → desfecho. Faz, e o reteste é transferência de
verdade:

| | |
| --- | --- |
| Retestes medidos | 180 |
| Com o **mesmo item** que disparou o erro | **0** |
| Com **formato diferente** | 173 |
| Nível | sempre **sobe**: 1→2 (87), 1→3 (67), 2→3 (26) |
| Distância do erro | 96 a 316 eventos, mediana 186 |

E os três desfechos já são distinguíveis no log, pelos campos `correta`,
`razao_correta` e `voltou`: acertou, errou pela mesma crença, errou por
outro motivo.

### O que falta, e é o próximo

Distinguir, **na resposta da pessoa**, "não conheço este recurso" de
"continuo acreditando". Hoje as duas viram o mesmo registro, e são
diagnósticos opostos: um pede ensino, o outro pede refutação. O `não
sei` da descida existe, mas conflata as duas.

E o degrau do `scanf` continua escrito. A decisão do dono foi substituí-lo
por uma situação feita com recurso já ensinado — o que exige o inventário
preenchido, que ainda não existe. Até lá o portão o bloqueia junto com o
resto.

## Duas autorizações: disponibilidade curricular e aprovação pedagógica

**O princípio, e ele é do projeto inteiro:**

> A disponibilidade de um conceito autoriza seu uso potencial. Não
> autoriza, por si só, a utilização de qualquer cadeia que o contenha.

### A simulação que o obrigou

Com `comparacao_de_ponteiros` ainda bloqueado, simulei liberá-lo. **Duas**
cadeias passariam a disponíveis de uma vez — e uma delas reprova em três
das cinco perguntas da revisão pedagógica, incluindo o degrau de
abertura, que exige declaração múltipla e reatribuição de ponteiro, sem
nenhuma das duas ensinada nem declarada.

Uma decisão **curricular** (este conceito foi ensinado?) estava decidindo
uma questão **pedagógica** (esta sequência confronta a crença?).

### As duas, e o motor exige as duas

| | pergunta | onde mora | quem decide |
| --- | --- | --- | --- |
| `liberada` | todo conceito exigido foi ensinado? | `conceitos.yaml` | auditoria do material |
| `aprovada` | **esta** sequência confronta? | `aprovacoes.yaml` | revisão pedagógica |

`Dominio.descida()` só entrega com as duas. Faltando qualquer uma, o
motor cai na refutação afirmativa — a mesma degradação de um tópico sem
cadeia escrita.

Os estados da aprovação são `aprovada`, `em_revisao`, `reprovada` e
`sem_revisao`, e o padrão é o último: cadeia que ninguém revisou não
roda, e esquecer de revisar não vira autorização. `aprovada` exige dizer
**quem e quando**; `reprovada` exige **o motivo** — as duas cobradas por
teste.

### Por que o arquivo é separado do das cadeias

Quem escreve a cadeia declara `requer` no YAML dela. Quem aprova escreve
noutro arquivo. No mesmo lugar, os dois seriam escritos na mesma passada
— e foi exatamente isso que produziu o problema que esta fatia conserta:
a `pointer_and_target_are_one` passou no portão porque **eu** declarei
os requisitos dela, e declarei menos do que ela exige.

### O que a revisão das duas cadeias achou

| pergunta | `pointer_is_data` | `pointer_and_target_are_one` |
| --- | --- | --- |
| Confronta em todos os degraus? | sim | **não** — o 3 é verificação, o 4 é repetição |
| Confunde endereço com conteúdo? | quase não — "p acompanha x" é vago | não |
| Só exige o apresentado? | sim | **não** — o degrau 1, de abertura |
| O último reconstrói? | **sim** | **não** |
| Distingue desconhecer de persistir? | **não** | **não** |

A última linha é a mesma para as duas, e é lacuna de arquitetura, não de
redação: escolher a alternativa da crença grava "continua acreditando",
e pode ser "não conheço o recurso". São diagnósticos opostos — um pede
ensino, o outro pede refutação.

### O estado, e ele é o conservador

Nenhuma cadeia roda. O inventário tem quatro conceitos disponíveis e
`comparacao_de_ponteiros` ainda não; as duas cadeias estão `em_revisao` e
`reprovada`, com motivo escrito. O ensaio continua sem a descida.

## O erro que explica

A primeira fatia pedagógica. O dono pediu a prioridade 1 assim: *corrigir
as ocorrências de erro simples sem explicação, aproveitando a fala
correta da premissa e a crença identificada*. E pôs a regra que governa
tudo o que vier depois:

> a IA não deve inventar a justificativa do erro. Ela precisa usar a
> crença, a premissa negada e a explicação acadêmica cadastrada no seu
> domínio.

### O que estava acontecendo, medido

Atravessando os treze tópicos como quem erra duas vezes em cada premissa:

| | erradas | explicam |
| --- | --- | --- |
| diagnóstico | 79 | 79 — todas viram refutação |
| treino | 79 | **0** |

A tela do treino dizia "Ainda não. Olhe de novo com calma" e nada mais.

E o material para explicar já estava no domínio: das **1.111**
alternativas erradas dos treze tópicos, **1.101 têm crença cadastrada**,
todo nó tem `simples`, toda crença tem `afirma`. Não faltava texto;
faltava montar.

### Por que só treino e entrada

Erro de diagnóstico e de reteste é **evidência**: é dele que sai a
crença, e é dele que sai a medida de transferência. Explicar ali ensina
no meio da medição e contamina os itens seguintes da mesma sessão. As
duas fases que ENSINAM explicam; as duas que MEDEM continuam caladas.

### O terceiro ingrediente, que a caixa de contraste ensinou

A crença da alternativa clicada **nem sempre nega a premissa da
pergunta**: medido, **512 das 1.101 — 46%** — negam outro nó. Um rótulo
fixo dizendo "e isso contradiz" seria falso em quase metade das telas,
que é exatamente o tamanho do defeito que a refutação já teve. Então o
servidor manda o FATO (`contradiz`) e o cliente escolhe o rótulo:

| caso | rótulo | medida |
| --- | --- | --- |
| a crença nega esta premissa | "E isso contradiz" | 589 |
| a crença nega outro nó | "E a premissa diz" | 512 |
| alternativa sem crença | o par da ideia SAI da tela | 10 |

### Sem campo novo no log, e a versão continua 3

O `resposta_registrada` já gravava `atividade` e `escolha`, e
`opcoes_na_tela` é determinística desde a fatia da posição: a
alternativa clicada se **recupera** do que já está gravado. A CS-6
pagando juros.

### O que o retorno NÃO tem

Três chaves: `premissa`, `escolheu`, `contradiz`. As duas de texto são
string do domínio palavra por palavra, e `test_o_retorno_nao_carrega_prosa`
cai se aparecer uma quarta. A frase de ligação é do cliente e não varia
com o conteúdo — é por isso que não existe lugar por onde uma
justificativa redigida possa entrar.

O campo `no` foi **tirado** do retorno: o cliente não o lia, o grafo já
recebe `foco` em toda resposta, e campo que ninguém usa é campo que
ninguém confere.

### Oito sabotagens

Portão de fase removido (14 testes caem), crença do item no lugar da
clicada (5), `contradiz` fixo em `True` e em `False`, explicação
desligada, campo de prosa acrescentado, rótulo fixo de volta no HTML, id
errado no JS. Todas falham contra o caso que devem pegar.

E uma assertiva que **não podia falhar** foi achada no caminho, a quarta
da sessão: `test_a_medicao_continua_calada` era vazio, porque na
política coerente todo erro de diagnóstico vira refutação e não existe
veredito `errada` para conferir. O caso real é o **escorregão** — errar
a camada 1 e acertar a razão —, e com ele o teste cobre os treze
tópicos.

### Duas pendências que a medição abriu

**O escorregão não explica, e é o buraco maior.** Errar a camada 1 e
acertar a razão produz **158 erradas nos treze tópicos e ZERO
refutações**: o sistema não diz nada, nem "Ainda não" com caixa, porque
é diagnóstico. A T4 decidiu não contestar o escorregão, e isso continua
certo — contestá-lo seria o erro simétrico ao falso positivo. Mas *não
contestar* não precisa ser *não dizer nada*, e a decisão é do dono.

**Onze das 79 premissas começam por conectivo** ("Então", "Logo", "Por
isso"), todas em nós de inferência. Na refutação isso lê bem, porque vem
depois da cadeia. Sozinha na caixa de contraste, "E isso contradiz →
Então p e a caixa apontada são duas caixas diferentes" tropeça. É
conteúdo do domínio, e conteúdo não se reescreve sem o orientador.

1.159 + 252 verdes.

## O caminho de quem não sabe, medido

A fatia do erro que explica cobriu quem **erra**. Esta medição olha quem
**não sabe** — e o dono apontou para ela antes de mim: *"se a pessoa não
sabe ou não tem certeza, quer dizer que ela precisa saber... cai uma
questão e a pessoa não entende o processo que está na tela"*.

Persona `nao_sabe` atravessando os treze tópicos, em processo. **A
replicação foi validada contra o HTTP**: kc_02 deu 36 lacunas, 6
construções e 30 dispensadas pelos dois caminhos, número por número.

| | |
| --- | --- |
| "não sei" declarados | **250** |
| momentos de ensino | **79** |
| construções dispensadas | **171** |
| perguntas feitas depois do "não sei" naquele nó | **245** |
| dessas, com nível MAIS ALTO do que onde ela declarou | **153 (62%)** |

**De cada 10 "não sei", 3,2 recebem ensino.**

### 79 construções para 79 nós

Exatamente uma por nó, em todo o conjunto. O teto de
`construcoes == 0` não é um limite que às vezes é atingido — é o
comportamento normal. O motivo escrito ao lado dele é honesto ("ensinar
de novo a mesma coisa não ensina mais, e sem teto a unidade não
termina"), mas a premissa só vale se o ensino for **o mesmo**, e é o que
acontece: dos quatro materiais explicativos do sistema, a construção
gasta um.

| material | cobertura | onde aparece |
| --- | --- | --- |
| `figura` | **79 de 79** | cartão de ensino |
| `resgate` (analogia) | todos | **só** na validação — só para quem teve crença |
| `simples` | 79 de 79 | cartão, e no erro de treino |
| `interpretacao` | **2 de 79** | cartão de ensino |

Quem declara lacuna nunca vê a analogia: a validação só acontece quando
há crença. E o cartão de ensino tem **um** botão, "Entendi" — o único
"ainda não entendi" do sistema está na refutação, que também só acontece
para quem tem crença.

### O instrumento foi desenhado para quem erra, não para quem não sabe

Quem tem crença recebe validação, refutação, treino e reteste. Quem não
tem ideia nenhuma recebe um cartão, um item de entrada, e depois mais
perguntas — **subindo de nível em 62% das vezes**. A pessoa que mais
precisa do sistema é a que recebe menos dele, e em ponteiros em C ela é
provavelmente a maioria.

### A ordem decidida

1. parar de subir o nível depois de lacuna declarada — 153 ocorrências
2. botão "não entendi" no cartão, com o `LIMITE_REEXPLICACAO` que existe
3. segunda construção por nó, com material DIFERENTE da primeira — 171
4. juntar figura + analogia + premissa na construção

### Item 1 feito: a pergunta não endurece contra quem disse que não sabe

O defeito **não era a escada**. Ela está certa, e `test_escada.py` já
guardava: o nível de um nó só sobe em acerto. Era o `_no_degrau`. Cada
"não sei" **consome um item** daquele degrau; quando os do degrau atual
acabam, o seletor subia. Esgotamento de banco lido como progressão.

A regra nova: enquanto o nó estiver em lacuna declarada, o seletor não
sobe. Aceita degrau mais BAIXO, se houver, e devolve nada se não houver —
e nada é honesto, porque `lacuna` já é terminal legítimo e conta como
medida no portão da CS-10.

| | antes | depois |
| --- | --- | --- |
| "não sei" declarados | 250 | **85** |
| momentos de ensino | 79 | 79 |
| construções dispensadas | 171 | **6** |
| perguntas após o "não sei" | 245 | **80** |
| dessas, com nível MAIS ALTO | **153** | **0** |

**A ressalva, e ela importa para não se contar vantagem:** a razão
"de cada 10 'não sei', 9,3 recebem ensino" (era 3,2) melhorou porque o
DENOMINADOR caiu. Continuam 79 momentos de ensino. A pessoa não recebe
mais ensino — deixa de receber 165 perguntas inúteis. É parar de
machucar, não passar a ensinar. Isso são os itens 3 e 4.

Três sabotagens: subir sempre (16 testes caem), nunca subir (2, incluindo
o `test_degrau_vazio_no_banco_vira_evento` antigo, que é o guarda de não
ter quebrado o caso normal) e pegar o item mais alto (16).

E a QUINTA assertiva vazia da sessão, pega antes de rodar: o guarda
anti-vacuidade estava por tópico, e zero perguntas depois de um "não sei"
é resultado legítimo da fatia — no kc_00 o nó acaba ali. O guarda passou
a ser do conjunto.

1.190 + 252 verdes.

### Item 2 feito: o cartão de ensino ganha "ainda não entendi"

O cartão tinha UM botão, `Entendi`. O único "ainda não entendi" do
sistema estava na refutação — que só acontece para quem **tem uma
crença**. Quem não sabe nada lia o cartão e só podia afirmar que
entendeu. Pior que falta de recurso: o sistema colhia "Entendi" de quem
não entendeu, e `forca()` descontava ponto por um contador
(`reexplicacoes`) que para esse público nunca saía de zero.

O mecanismo já existia inteiro — `Resposta.repetir`,
`LIMITE_REEXPLICACAO = 2`, `EstadoNo.reexplicacoes`, `Estado.repeticoes`
e o evento `premissa_reapresentada`. Esta fatia ligou o que a refutação
já usava, nas três telas de ensino (abertura, primeiro contato e
construção), com o mesmo teto e o mesmo log.

**O que muda na segunda vez, e é pouco de propósito:** no cartão de
abertura a analogia de resgate não aparecia, e passa a aparecer. No
cartão de lacuna ela já vem de primeira — ali repetir reapresenta o
mesmo. Fazer a segunda vez ser DIFERENTE é o item 3.

### Duas correções de afirmações minhas

**A analogia não some para quem declara lacuna.** Eu disse que sim, com
base no comentário do YAML ("é ela que aparece no passo de validação"), e
não conferi o cliente: `telaEnsino` já desenhava `ensino-resgate` quando
o motivo é `lacuna` ou `primeiro_contato`. Na tela de construção os
quatro materiais JÁ se encontram. Onde eles não se encontram é na tela de
ERRO do treino, que mostra dois dos quatro.

**E o `interpretacao` não chega à tela de construção.** `_tela_ensino`
manda o campo; `_tela_construcao` não manda. Quem declara lacuna em B1 ou
B3 — os dois únicos nós com ampliação — não recebe a ampliação. Uma
linha, achada ao mexer na função, NÃO corrigida aqui: é material de
ensino na construção, que é o item 3. Registrada para não se perder.

### A fatia quase passou verde sem mudar a tela

A primeira versão mandava só `reexplicacao` e não `resgate`. O motor
passou nos 23 testes, e no navegador **nada acontecia**: o cliente desenha
um elemento só para a analogia e não tinha texto para pôr nele. Pego
olhando a tela, não a suíte — o mesmo motivo pelo qual a regra de ver no
navegador existe.

Três sabotagens: sem teto (14 caem, inclusive os 13 de "a unidade
termina"), não zerar o contador ao mudar de cartão (1) e ignorar o
`repetir` no despacho (2).

1.213 + 252 verdes.

### Item 3: a segunda construção NÃO foi feita, e o motivo é conteúdo

Medido antes de escrever uma linha, nos treze tópicos:

| material | nós que têm |
| --- | --- |
| enunciado, exemplo, figura, analogia | **79 de 79** |
| ampliação (`interpretacao`) | **2 de 79** |
| itens de entrada por nó | **1** em 74 nós, **0** em 5 |

Os quatro primeiros já aparecem **na primeira** construção. Uma segunda
mostraria o mesmo cartão, o mesmo exemplo, a mesma figura e a mesma
analogia — e sem item de entrada, porque o único já foi gasto. Seria
exatamente o que o comentário do teto recusa: *"ensinar de novo a mesma
coisa não ensina mais"*. Construir isso entregaria uma casca com cara de
funcionalidade.

**O item 3 está bloqueado em conteúdo, não em mecanismo.** Ele fica
possível quando houver `interpretacao` nos outros 77 nós — e esse texto
passa pelo orientador.

### O que foi feito: a ampliação chega à tela de construção

`_tela_ensino` mandava o campo e `_tela_construcao` não, e o cliente
desenha o mesmo elemento nas duas. Quem declarava lacuna em B1 ou B3 —
os dois únicos nós com ampliação — recebia o cartão sem ela. Justo quem
mais precisava.

Conferido na tela: o cartão de lacuna do B1 agora traz os cinco
materiais, com a ampliação em três parágrafos.

### E uma armadilha de demonstração, descoberta aqui

O servidor de pré-visualização **não recarrega o Python**. Os arquivos
estáticos (`app.js`, `index.html`) vêm do disco a cada pedido, então
mudança de cliente aparece ao recarregar a página; mudança de motor, não.
A primeira conferência desta fatia mostrou a ampliação ausente porque o
processo era o de antes da edição. Depois de mexer em `mvp/`, reinicie o
servidor antes de mostrar a alguém.

1.215 + 252 verdes.

## Item 4: o erro que DESENHA

A tela de erro do treino era a única das quatro telas de ensino sem
desenho. Medido antes de escrever uma linha, nos treze tópicos:

| o que | quanto |
| --- | --- |
| telas de erro de treino/entrada por varredura | **79** |
| premissas com figura no banco de `figuras.js` | **79 de 79** |
| premissas com analogia própria (`resgates[no]`) | **79 de 79** |
| materiais que a tela do erro mostrava | **2 de 4** |

Os quatro materiais do cartão — enunciado, exemplo, figura, analogia —
já se encontravam no ensino, na construção, na validação e na refutação.
A tela do erro mostrava o enunciado da premissa e a fala da ideia
marcada, e mais nada. Agora mostra os quatro.

### O `no` volta ao retorno, com uso

Na fatia do feedback explicativo o `no` tinha sido **tirado** deste
retorno, com a justificativa de que campo que ninguém lê é campo que
ninguém confere. Ele volta porque agora tem uso: o banco de figuras é do
cliente e é indexado por nó, e é por este campo que o desenho é
escolhido. Quem garante que o uso existe na tela, e não só no JSON, é o
`test_o_cliente_le_todos_os_campos_que_o_servidor_monta`, que já existia.

### A analogia não é `d.resgate(no)`, e isso importa

Esse acessador cai no **resumo do tópico** quando o nó não tem versão
própria — e o resumo mapeia as cinco premissas de uma vez. Na tela de um
erro de treino ele entregaria a resposta de atividade que ainda não foi
feita. O retorno manda `d.resgates.get(no, "")`: a do nó, ou nada, e a
tela esconde a linha vazia. Hoje são 79 de 79 com versão própria, então
o caso não acontece em tópico nenhum; `test_toda_premissa_tem_analogia_propria`
existe para o nó que alguém cadastrar amanhã.

### O teste que caiu, e não foi afrouxado

`test_o_retorno_nao_carrega_prosa` guarda a regra do dono — o sistema não
redige a justificativa do erro — e o faz exigindo **igualdade exata** do
conjunto de chaves, para que campo novo com frase escrita pela IA caia
ali. Ele caiu, como projetado. Foi **estendido**, não relaxado: as duas
chaves novas entraram com a mesma exigência das antigas (a analogia tem
de ser string cadastrada; o `no` tem de ser nó do domínio) e a igualdade
exata continua. Cinco chaves pinadas em vez de três.

### Uma assertiva frouxa, achada pela sabotagem

A primeira versão de `test_o_cliente_desenha_a_figura_do_erro` procurava
`Figuras.dentro($("ret-figura")` — e a linha que **limpa** o elemento no
alto de `mostraRetorno` já casava com isso. Apagada a linha que desenha,
o teste continuava verde. Corrigido para exigir a chamada com
`j.retorno.no`. Foi a sabotagem que mostrou; reler o teste não mostrou.

### O que ficou de fora, de propósito

O **falso positivo** divide a mesma tela e já recebe um `no` do servidor
(o nó que a crença nega), e o cliente o ignora. Pôr o desenho ali é outra
fatia: a relação é diferente — "você explicou por" não é "você escolheu"
— e misturar as duas repetiria o defeito do rótulo fixo.

Conferido na tela, numa sessão de kc_02: erro no item de entrada do B1
traz os quatro — "Você escolheu / o ponteiro não ocupa lugar nenhum",
"E isso contradiz / p é uma caixa como as outras", o desenho das duas
casas com dois números de porta, e a analogia do papel que não flutua.
No retorno seguinte, de outro veredito, o desenho sumiu.

## O escorregão deixa de ser invisível

Errar a resposta e acertar a razão. A tabela de classificação chama isso
de `falso_negativo`, o motor grava `vacilo_detectado`, marca o nó e leva
o dado no payload do mapa. **Nenhuma tela mostrava.**

Medido antes de escrever uma linha, nos treze tópicos, com a persona que
erra a camada 1 e marca sempre a razão correta:

| o que | quanto |
| --- | --- |
| escorregões (1 erro por nó) | **79** — payload `errada`, retorno `None`, 79 de 79 |
| escorregões (2 erros por nó) | **158** — idem, 158 de 158 |
| o nó volta a ser perguntado | **153 de 158**, mediana de **3 passos** |
| como o nó termina (1 erro) | 74 `confirmado`, 5 `fragil` |
| telas que mostravam `vacilou` | **nenhuma** |

**O fluxo não estava quebrado** — isso corrige o que eu havia afirmado.
Quem escorrega recebe o mesmo nó na pergunta seguinte e quase sempre o
confirma. Quebrada estava a TELA: a pessoa que acabou de enunciar a
premissa corretamente lia *"Ainda não. Olhe de novo com calma — a
próxima pergunta volta ao mesmo ponto de outro jeito"*, o mesmo texto de
quem tem um mal-entendido.

### Por que falar numa fase que mede

A regra do projeto é que o diagnóstico e o reteste ficam calados, e a
justificativa dela é literal: *explicar ali **ensina** no meio da
medição*. Nomear um escorregão não ensina. O servidor **não manda
`retorno`** neste veredito — então não existe caminho por onde premissa,
crença ou figura cheguem à tela, e a frase é do cliente e não varia com
o conteúdo. É menos do que o falso positivo já diz na mesma fase desde a
Decisão 13, que mostra texto do domínio.

**O custo, e é decisão metodológica:** a pessoa fica sabendo que a razão
marcada era a correta, três passos antes de o mesmo nó voltar, em 153 de
158 casos. Isto vai ao orientador, e é um commit para desfazer.

### Três superfícies

1. **A tela do instante**: veredito próprio, neutro, sem conteúdo.
2. **O mapa final**: parágrafo próprio, depois do estado. Ali não custa
   medida nenhuma — o mapa acontece depois de tudo medido.
3. **O painel do pesquisador**: a coluna do estado do episódio imprimia
   `falso_negativo` cru, porque o dicionário de nomes só traduzia estado
   de NÓ. Traduzidos também `confirmada` e `crenca`, que estavam crus
   pelo mesmo motivo.

### `escorregou` não é `vacilou`, e uma correção minha

`vacilou` é posto no ramo CONFIRMADA a partir de `bool(en.erros)`:
"errou uma vez e corrigiu sozinho", **qualquer** que tenha sido o erro.
A primeira versão desta fatia pôs a frase do escorregão atrás dele, e eu
afirmei que isso faria o mapa mentir para quem errou por crença.

Fui medir: treze tópicos × dezesseis personas (escorregar em todos / em
B1 / em B2 / em nenhum × um ou dois erros por nó × duas confianças) e
achei **zero** nós com `vacilou` e sem escorregão — a crença manda o nó
para a refutação, e ele não volta pelo ramo CONFIRMADA do diagnóstico.
Então o campo novo não conserta um defeito observado: ele impede um. O
teste que separa os dois não finge uma persona que não existe — ele
constrói o estado pela API do motor.

Foi o navegador que levantou isso, não a suíte: o teste só procurava a
palavra `vacilou` no arquivo.

### O teste que cresceu

`test_a_medicao_continua_calada` disparou a própria trava de vacuidade
pela segunda vez: o escorregão era a **única** trilha que produzia
veredito `errada` numa fase que mede, e ao ganhar veredito próprio
deixou o teste sem nada para olhar. A correção foi **alargar**: o laço
passa agora por toda resposta das fases que medem, qualquer que seja o
veredito, e exige retorno nenhum. A exceção é o falso positivo, nomeada
em vez de ser um buraco no filtro.
