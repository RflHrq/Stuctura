# Research — o que existe hoje, contra o conceito da fase 1

Artefato da fase 2. Análise **somente leitura**: nenhum arquivo de código
foi alterado. Conceito e critério em [problema.md](problema.md);
vocabulário em [context.md](context.md).

Rótulo de evidência em cada achado: **[verificado]** rodei e vi;
**[lido]** li o código e afirmo o que ele faz; **[hipótese]** suspeita que
ainda não provei.

## Linha de base, medida agora

| O quê | Resultado |
| --- | --- |
| `python -m pytest mvp/ -q` | **28 passaram**, 0,24 s **[verificado]** |
| `python -m pytest -q --ignore=mvp` | **252 passaram**, 66,75 s **[verificado]** |
| Segredos em arquivos versionados | nenhum; o único acerto da varredura é `import secrets` em [api/routes.py:15](api/routes.py:15) **[verificado]** |
| `data/export_token.txt`, `mvp/dados/` | fora do versionamento, por `.gitignore` **[verificado]** |
| Código Python | 13.788 linhas; maior arquivo `engine/session.py`, 1.124 **[verificado]** |

Esta é a referência contra a qual qualquer mudança futura será comparada.

## O conceito, peça por peça, contra o código

| Peça do conceito (fase 1) | Hoje | Onde |
| --- | --- | --- |
| Grafo de premissas com suporte e conclusão | **funciona** | [mvp/dominio/graph_kc00.yaml](mvp/dominio/graph_kc00.yaml), [mvp/motor.py:318](mvp/motor.py:318) `_plano` |
| Crença que nega exatamente um nó | **funciona** | [mvp/dominio.py:192](mvp/dominio.py:192) recusa a carga se `negates` não bater |
| Percurso de refutação derivado do grafo | **funciona** | `_plano`, em pós-ordem; nenhuma tela escrita à mão |
| Camada 1 — resposta | **funciona** | `_responde_diagnostico`, [mvp/motor.py:239](mvp/motor.py:239) |
| Camada 2 — **razão** | **parcial, e no lugar errado** | existe como *sondagem* no motor antigo ([engine/socratic.py:181](engine/socratic.py:181)), que dispara **dentro da refutação** ([engine/session.py:729](engine/session.py:729)), não a cada atividade |
| Camada 3 — confiança | **parcial** | só no diagnóstico: [mvp/motor.py:227](mvp/motor.py:227) |
| **"Não sei"** como opção | **inexistente** | a escala é `("chutei", "acho que sei", "tenho certeza")`, [mvp/motor.py:57](mvp/motor.py:57) — "chutei" é confissão *depois* de ter sido obrigado a escolher |
| Estado **falso positivo** (certo pela razão errada) | **inexistente** | o acerto confirma o nó direto, [mvp/motor.py:259](mvp/motor.py:259) |
| Estado **falso negativo** (errado pela razão certa) | **parcial** | aproximado por `vacilo_detectado` (dois erros em formatos diferentes), não pela razão |
| Sobrevive à troca de superfície | **funciona** | RF34: formato diferente a cada tentativa, `proximo_item`, [mvp/motor.py:402](mvp/motor.py:402) |
| Não volta no **reteste do fim** | **inexistente no MVP**, existe no antigo | `_reteste_de` e `belief_retested`, [engine/session.py:398](engine/session.py:398) e [engine/session.py:1038](engine/session.py:1038) |
| Força da premissa | **parcial** | há `streak`, `erros` e `tentativas` por nó ([mvp/motor.py:105](mvp/motor.py:105)), mas a seleção é a ordem fixa do grafo, não "o mais fraco primeiro" |
| Teach-back (frase do começo e do fim) | **inexistente** | nenhuma entrada de texto livre em nenhuma das duas interfaces |
| Painel do pesquisador | **inexistente no MVP**; peças no antigo | projeções e exportação com token, [api/routes.py:218](api/routes.py:218) |
| Reconstrução do estado pelo log | **inexistente** | ver P1-2 |

## Achados

### P1-1 — Todos os distratores de uma atividade carregam a mesma crença

O carregador do MVP etiqueta **toda** alternativa errada com a crença da
atividade inteira:

```python
# mvp/dominio.py:236
crenca=None if chave == gabarito else crenca
```

Com três alternativas, as duas erradas ficam indistinguíveis: escolher
"nada ainda, nenhuma tem valor" e escolher "um espaço só, compartilhado"
produzem o mesmo diagnóstico. **[lido]**

Isto bloqueia a camada de razão: a razão errada precisa apontar para **uma**
crença, não para "a crença que esta pergunta mira".

**O banco antigo já faz certo:** 57 das 65 atividades têm `misconception`
**por alternativa** ([domain/c_pointers/cius.yaml](domain/c_pointers/cius.yaml)),
e o validador já cobra que toda crença apareça em alguma alternativa
([tools/validate.py:140](tools/validate.py:140)). **[verificado]** O MVP é
uma regressão nesse ponto, não um avanço.

**Correção sugerida:** descer `belief_context` da atividade para a
alternativa, nos 20 itens do kc_00. Mudança de dados, não de motor.

### P1-2 — O log diz ser a fonte única; o estado vive em memória

```
# mvp/log.py:8
O estado da sessão NÃO é gravado: ele é reconstruído reexecutando as
respostas do log.
```

Não é o que acontece. O estado vive num dicionário de processo
([mvp/app.py:30](mvp/app.py:30)) e **nenhuma função reconstrói** — a busca
por `reconstr|replay|rebuild` em `mvp/` só encontra comentários. **[verificado]**

Consequência na coleta: reiniciar o servidor no meio de uma sessão perde a
sessão, e o participante recomeça. Com 10 a 15 pessoas, perder uma é perder
7% da amostra.

**Correção sugerida:** implementar o replay (o log tem o necessário) ou
corrigir a docstring. Hoje o documento afirma algo que o código não faz, que
é o pior dos dois mundos.

### P1-3 — Um nó sem crença mapeada não tem razão errada para oferecer

`B1` não é negado por nenhuma crença (`negated_by: []`), e nenhuma atividade
dele tem `belief_context`. **[verificado]** A camada de razão nesse nó teria
uma alternativa só — a certa.

Em escala o buraco é maior: no grafo grande, **61 dos 93 nós** não são
negados por crença nenhuma (34 crenças, 32 nós cobertos). **[verificado]**

**Correção sugerida:** para o primeiro teste basta cobrir o kc_00 — uma
crença para B1, ou aceitar que B1 tenha só as camadas 1 e 3, declarando isso.
Cobrir os 93 nós é decisão de escopo da coleta, não desta fase.

### P2-1 — A confiança não é pedida no treino nem no fim

`"pede_confianca": e.fase == DIAGNOSTICO` ([mvp/motor.py:227](mvp/motor.py:227)). **[lido]**

Mas o critério de sucesso diz *"a razão muda sem queda de confiança"* — isso
exige medir confiança nos **dois** momentos. Hoje só o primeiro existe.

### P2-2 — A ordem das atividades é fixa, não guiada pela força

`_proxima_diagnostica` percorre `d.ordem` ([mvp/motor.py:200](mvp/motor.py:200)):
a primeira premissa não resolvida, na ordem do grafo. **[lido]** O motor
antigo tinha seleção por fronteira e nível ([engine/selector.py](engine/selector.py)),
que é dificuldade, não força. A "força da premissa" do conceito novo não
existe em nenhum dos dois.

### P2-3 — Dois bancos de atividades, dois esquemas incompatíveis

| | MVP (`mvp/dominio/`) | Antigo (`domain/c_pointers/`) |
| --- | --- | --- |
| Nós | 5 | 93 |
| Crenças | 4 | 34 |
| Atividades | 20 | 65 |
| Chave do nó | `node: kc00:B1` | `targets: [I2]` mais `kc:` |
| Tipo de nó | `observavel` / `inferencia` | `base` / inferência |
| Crença na alternativa | não (P1-1) | **sim**, `misconception:` |
| Formatos | 4 nomeados | 6 em `type:` (inclui **`parsons`**) |

**[verificado]** Manter os dois esquemas custa dois carregadores e dois
validadores. Vale notar: o tipo `parsons` do banco antigo é exatamente a
funcionalidade 3 — *montar a cadeia* — adiada para o segundo ciclo. Há
precedente de formato no domínio, não implementação de tela.

## O que serve, o que muda, o que se joga fora

**Serve sem mudança:**

- o grafo e a regra "uma crença nega exatamente um nó", validada na carga —
  é a espinha do conceito, e está correta;
- o percurso de refutação derivado do grafo (`_plano`);
- a regra de formato e o banco de treino próprio (RF34), que é o "sobrevive
  à troca de superfície" do critério;
- o log append-only de eventos;
- a **sondagem** do motor antigo: ela já monta a escolha forçada entre a
  frase do nó e a frase da crença **a partir do grafo, sem texto escrito à
  mão** ([engine/socratic.py:181](engine/socratic.py:181)). É a camada de
  razão pronta — no lugar errado.

**Precisa mudar:**

- a sondagem sai de dentro da refutação e vira a **segunda camada de toda
  atividade** — é a mudança central desta reformulação;
- a crença desce da atividade para a **alternativa** (P1-1);
- a confiança passa a ser pedida uma vez por atividade, não só no
  diagnóstico (P2-1);
- o acerto deixa de confirmar sozinho: só confirma **com a razão certa**;
- `estado_dos_nos` ganha os dois estados novos (falso positivo e falso
  negativo), e o mapa precisa saber desenhá-los.

**Fica onde está, sem entrar no caminho:**

- nada do motor antigo precisa ser portado além da sondagem e do reteste.
  Os 252 testes continuam passando e documentam decisões — mas
  `engine/session.py`, com 1.124 linhas e nove fases, é a complexidade de
  que o orientador reclamou. **Não reconstruir o MVP em cima dele.**

## O que NÃO foi coberto nesta fase

- **Usabilidade (U).** Não houve crítica das telas atuais nem verificação de
  acessibilidade. Deliberado: as telas mudam na próxima fase, e auditar o que
  será redesenhado é trabalho jogado fora. Fica para a fase 3/4, com o
  desenho novo.
- **Privacidade (G) e dados (M) em modo focado.** O sistema não guarda
  identificador direto hoje e roda offline; a varredura de segredos passou.
  O inventário formal fica para o PRD, onde o teach-back entra — texto livre
  escrito por participante é dado novo e muda a conversa.
- **Desempenho (D).** Não aplicável ao perfil.
- **Qualidade de conteúdo das 20 atividades.** Não é leitura de código: é
  revisão sua, pendente desde o MVP.

## Decisões desta fase

As três perguntas que a leitura levantou, decididas em 28/10/2026. São
decisões de desenho: entram no PRD, e nenhuma delas alterou código aqui.

### D-8 — A razão é uma segunda tela, depois da resposta

A pessoa escolhe **o que acontece**, a resposta **tranca**, e só então
aparecem as razões. A confiança vem por último, uma vez, cobrindo as duas.

O motivo é de medição, não de interface: as razões erradas são **enunciados
de crenças**, e crença escrita em forma de alternativa é informação. Ler
"se eu não dei valor, a variável ainda não existe" antes de responder dá a
pista; e, pior, muda a resposta de quem já ia acertar. Com a resposta
trancada, o par resposta-razão é independente — é o que a tabela de
classificação pressupõe.

**Custo:** mais um passo de tela por atividade, e o `ms` passa a ser medido
por camada, não por item.

### D-9 — A razão errada é qualquer crença do grafo, e o estado vai para o nó que ela nega

Esta era a pergunta "B1 ganha uma crença?". O banco responde melhor do que
a pergunta supunha. Os distratores dos itens de B1, lidos um por um
**[verificado]**:

| Alternativa errada | A que crença ela corresponde de fato |
| --- | --- |
| "Nada — ela só existe quando é usada pela primeira vez" (`ciu_kc00_001`) | `no_value_no_memory` — que nega **B2** |
| "Nada ainda, nenhuma tem valor" (`ciu_kc00_002`) | `no_value_no_memory` — nega **B2** |
| "Decidir que valor ela vai ter" (`ciu_kc00_001`) | `no_value_no_memory` — nega **B2** |
| "Um espaço só, compartilhado pelas duas" (`ciu_kc00_002`) | **nenhuma no catálogo** |
| "Não ocupa: toda variável ocupa o mesmo" (`ciu_kc00_t01`) | **nenhuma no catálogo** |
| "Não há erro: nome é comentário" (`ciu_kc00_t02`) | **nenhuma no catálogo** |
| "Porque o nome b vem depois no alfabeto" (`ciu_kc00_t01`) | nenhuma, e nem deveria: é distrator vazio |

Daí três decisões, não uma:

1. **As razões oferecidas num item não precisam negar o nó daquele item.**
   Elas são crenças do grafo. Quando a pessoa escolhe uma, o estado de
   crença ativa vai para o nó que **aquela crença nega** — que pode ser um
   vizinho. Isso é diagnóstico melhor, não concessão: errar B1 dizendo que
   a variável não existe sem valor é uma informação sobre **B2**, e é lá
   que ela deve ser registrada.
2. **B1 ganha uma crença nova**, cobrindo as três alternativas sem dono:
   *"toda variável ocupa o mesmo espaço; o tipo é só um aviso para o
   compilador"*. Procedência **E** — elaborada a partir do modelo de
   máquina, hipótese a testar. Hoje o catálogo tem **0 crenças E em 34**
   ([fundamentacao.md](fundamentacao.md)); esta seria a primeira, e é honesto
   que seja: não tenho fonte empírica para ela, e o estudo é justamente onde
   ela ganharia ou perderia evidência.
3. **O distrator vazio sai.** "Porque o nome b vem depois no alfabeto" não
   corresponde a nenhuma ideia que alguém sustente; como razão, é alternativa
   que ninguém escolhe, e enfraquece o item.

### D-10 — O painel do pesquisador lê o log, não a sessão

Processo separado, só leitura, lendo `mvp/dados/eventos.jsonl`. **Não** uma
rota que toque o dicionário de sessões ([mvp/app.py:30](mvp/app.py:30)).

Três razões, em ordem de peso: (a) o painel não pode derrubar a sessão de
quem está respondendo — um erro meu numa consulta não pode custar um
participante; (b) o log é append-only, então ler é seguro por construção; e
(c) assim o painel funciona depois de um travamento, quando é mais
necessário.

**O efeito colateral é a melhor parte:** se o painel só lê o log, o log tem
de conter tudo. Isso é exatamente o trabalho do P1-2 — a reconstrução do
estado. **As duas coisas passam a ser a mesma tarefa**, e o painel vira o
teste de que o log basta: se é possível desenhar o estado dos nós a partir
dele, a reconstrução existe.

## O que isto deixa para o PRD

| Item | Origem |
| --- | --- |
| Camada de razão em duas telas, confiança uma vez | D-8 |
| Crença na alternativa, e atribuição ao nó que a crença nega | P1-1, D-9 |
| Uma crença E nova para B1, e um distrator a trocar | D-9 |
| Painel lendo o log, e a reconstrução do estado como a mesma tarefa | D-10, P1-2 |
| `nao_sei` em toda camada, teach-back no começo e no fim | decisão 7 da fase 1 |
