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
