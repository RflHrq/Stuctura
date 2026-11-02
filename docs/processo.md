# Processo — da ideia ao código

**Ideia em uma frase:** um sistema que trata conhecimento como um grafo de
premissas, descobre em qual premissa a pessoa está errada e a conduz, pelo
grafo, até a premissa correta.

**Fase atual:** **ensaio com uma pessoa** — roteiro e ambiente prontos
([roteiro](ensaio-roteiro.md), `scripts/ensaio.sh`). É o próximo passo
porque o software deixou de ser o gargalo: dos quatro P1 da revisão final,
o único que era de código está fechado, e CS-11 nunca teve evidência.

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
revisão final achou um **P0** (fechado nela, `d34f12c`) e quatro P1, dois
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
| T0 | `a45cb7b` | `scripts/verify.sh`: segredos antes dos testes | 28 | segredo plantado faz falhar |
| T1 | `8e5be7f` | a crença desce da atividade para a alternativa | 42 | sim |
| T2 | `ce0d44d` | a camada da razão; a resposta tranca | 54 | sim |
| T3 | `16efa89` | a confiança em tela própria, em toda atividade | 60 | sim |
| T4 | `a8ac020` | os cinco estados; a crença no nó que ELA nega | 70 | sim — **2 testes aposentados e 2 reescritos**, com aprovação |
| T7 | `9ae992d` | o mapa com os cinco estados e o caso cruzado | 74 | sim |
| T5 | `72233e8` | "não sei" nas três camadas | 80 | **fraca**, declarada: o curto-circuito da lacuna derruba 1 teste só |
| T6 | `8a7447d` | o falso positivo traz outra superfície | 86 | sim — o primeiro teste **não mordia**, reescrito |
| T9 | `33f16c0` | o teach-back do começo e do fim | 95 | sim |
| T10 | `6ffd6d9` | a sessão reconstruída pelo log (CS-6) | 110 | sim — 6 de 6 |
| T11 | `b4bb73c` | o painel do pesquisador, só leitura (CS-7) | 126 | sim — 7 de 7 |
| T8 | `3c7204c` | a força da premissa escolhe o próximo item | 150 | sim — 11 de 11, **uma não mordia** e foi corrigida |
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
| R1 | `8ebafb0` | P1-A, P2-A | 185 | sim — 6 de 6 |
| R2 | `3f0023e` | P1-B | 191 | sim — 4 de 4 |
| R3 | `d500edd` | P2-B | 194 | sim — 4 de 4, **uma não mordia** |
| R4 | `4fb254d` | P2-C | 197 | sim — 5 de 5 |
| R5 | `5489db2` | P2-D | 200 | sim — 4 de 4 |
| R6 | `15cd3c3` | P2-E, P2-F | 214 | sim — 9 de 9, **duas não mordiam** |

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
| `9242f47` | `docs/linguagem.md`: o contrato, e três formatos de atividade propostos com o custo de cada um |
| `be1175c` | grafo e crenças do kc_02, sob o contrato |
| `2c32717` | crenças conferidas na obra primária; relatório em `docs/revisao-crencas-kc02.md` |
| `6d0c4f6` | as 36 atividades, e o carregador aceitando mais de um tópico |

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
| C1 | `23de1e5` | a crença de nó sustentado sai do cardápio; `nao_medido` com motivo |
| C2 | `23de1e5` | a confiança do treino só no item que fecha a sequência |
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
