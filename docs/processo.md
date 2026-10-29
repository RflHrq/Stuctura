# Processo — da ideia ao código

**Ideia em uma frase:** um sistema que trata conhecimento como um grafo de
premissas, descobre em qual premissa a pessoa está errada e a conduz, pelo
grafo, até a premissa correta.

**Fase atual:** 6 — Implement. Uma tarefa por commit, com sabotagem antes
de acreditar em teste verde.

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
| Grafo do kc_00 (declaração de variáveis) | `mvp/dominio/` | 5 nós, 4 crenças, 20 atividades |
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
| 6/T11 | U (interface) | **não executada** | o painel tem um usuário só, que é quem construiu; a skill entra na revisão final, junto das telas de quem responde |

## Linha de base da fase 2

280 testes passando (28 no MVP, 252 no sistema antigo), 13.788 linhas de
Python. Qualquer mudança futura é comparada com isto.

## Orçamento

Fase 1: 4 iterações. Fase 2: 2 iterações. Fase 3: 1 iteração. Fase 4: 1
iteração. Fase 5: 1 iteração. Fase 6: 1 iteração por tarefa, nas treze —
nenhuma precisou de uma segunda.
