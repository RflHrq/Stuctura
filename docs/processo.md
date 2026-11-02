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
| Domínio da unidade, por tópico | `mvp/dominio/` | 4 tópicos: kc_00 (5 nós, 20 itens), kc_01 (5, 35), kc_02 (6, 60), kc_03 (6, 42) |
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
