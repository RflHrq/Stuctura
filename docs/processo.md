# Processo — da ideia ao código

**Ideia em uma frase:** um sistema que trata conhecimento como um grafo de
premissas, descobre em qual premissa a pessoa está errada e a conduz, pelo
grafo, até a premissa correta.

**Fase atual:** 1 — Grill (alinhar a ideia). Nenhum código é alterado nas
fases 1 a 5.

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

## Perguntas em aberto

Nenhuma bloqueia a fase 2.

1. Quantos tópicos a coleta usa, e em que ordem.
2. Onde fica o reteste do fim da sessão enquanto só o kc_00 existe.
3. Quem classifica as frases abertas do teach-back, e com que codebook.

## Artefatos

| Fase | Artefato | Estado |
| --- | --- | --- |
| 1 Grill | `docs/context.md` | **pronto** — glossário fechado |
| 1 Grill | `docs/problema.md` | **pronto** — critério, instrumento e escopo do 1º ciclo |

**Fase 1 fechada.** Próxima: fase 2 (Research) — leitura do que existe
hoje contra este conceito, sem alterar código.

## Orçamento

Fase 1: 4 iterações.
