# Structura

Sistema de refutação socrática para o domínio de ponteiros em C.
Implementação da especificação técnica v1.0 (Rafael H. S. Simão, UFV–CRP).

Piloto alvo: **30 de setembro de 2026**.

## Rodar

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -q
```

## Estado da construção

Ordem do §13 da spec. Marcos 1 a 3 são o caminho crítico.

| # | Entrega | Estado |
|---|---------|--------|
| — | `domain/c_pointers/*.yaml` — canônicos, do autor. 12 KCs, 93 nós, 34 crenças, 48 CIUs | **completo** |
| — | `engine/loader.py`, `socratic.py`, `tools/validate.py` | **feito** |
| 1 | Regressão controlada (RF09) — `socratic.on_wrong()` | **feito**, falta a FSM chamar |
| 2 | `store/`: esquema, append, projeção, `replay.py` | **feito** |
| 3 | `strategy.py` + teste de paridade dos braços | **feito · marco crítico verde** |
| 4 | `session.py`: FSM do §6 + `model.py` + `selector.py` | **feito** |
| 5 | `api/`: as seis rotas do §9 | pendente |
| 6 | `web/`: interface e `diagram.js` | pendente |
| 7 | `feedback.yaml` + `feedback.py` (RF17, SHOULD) | pendente |
| 8 | `export.py` + os três CSVs | pendente |
| — | CIU de variação para os 8 KCs fora do piloto | não bloqueia |

## Porta de CI

```bash
python -m tools.validate --stats   # domínio: sai 0 obrigatoriamente
python -m pytest tests/ -q         # motor e store
python -m tools.replay --verify    # RNF04 sobre o banco de coleta
python -m tools.freeze_golden      # só após mudança DELIBERADA no grafo
```

## Fronteira domínio / estudo

`domain/c_pointers/*.yaml` é **fonte**: o loader se adapta a ele, nunca o
contrário. Propriedades que o motor precisa e que os YAMLs não declaram são
**derivadas** — se uma crença é fundacional sai do tipo do nó que ela nega;
se um KC exige diagrama sai de ter uma crença fundacional. Nada disso é
acrescentado ao domínio.

`study.yaml` é outra coisa: recorte do piloto, termos de nomeação tardia,
limite de tentativas, escala de confiança. São decisões do experimento, não
do conteúdo — e por isso **ficam fora do hash do domínio** (§15). Mudar o
recorte não muda o que o participante viu.

## `store/` — o que esta camada decide

Nada sobre pedagogia. Ela decide **o que é verdade e o que é cache**.

- `events` é a fonte. Append-only garantido por *trigger* SQLite: `UPDATE` e
  `DELETE` abortam a transação, inclusive vindos de um `sqlite3` aberto à mão.
- `node_state` é cache. Pode ser apagada a qualquer momento e reconstruída
  do log (RNF04). Nenhuma análise deve lê-la.
- O `seq` é alocado dentro de `BEGIN IMMEDIATE`, com `UNIQUE(session_id, seq)`
  como rede de segurança. Sessões não têm buraco na numeração.
- Payload inválido falha **na escrita**, nunca na análise (§1: falha na carga,
  não em sessão). O catálogo do §5.2 vive em `EVENT_SCHEMA`.

### Decisão de projeto: `node_updates`

Qualquer evento pode carregar um campo `node_updates`:

```json
{"node_updates": [{"kc": "kc_07", "node": "n3", "state": "wrong"}]}
```

**Por quê.** O §5.2 define, por exemplo, `answer_submitted` com
`{ciu_id, option_idx, confidence, elapsed_ms}`. Esse payload não diz se a
resposta estava certa nem que nós foram afetados — para descobrir isso a
projeção teria de consultar os YAMLs e reexecutar a regra do §7.3. Isso
transformaria a projeção num segundo motor, que poderia divergir do primeiro,
e violaria a Definition of Done: *"toda decisão do motor emite evento
suficiente para reconstruir o que aconteceu"*.

Com `node_updates`, o motor registra **a decisão que tomou**, e a projeção
vira um *fold* sem política nenhuma. Consequências práticas:

- `projections.verify()` compara os dois caminhos (aplicação incremental
  durante a sessão × fold do zero) e acusa qualquer divergência.
- `kc_completed.vector` funciona como *checkpoint*: se o vetor no payload não
  bate com o que o log projeta naquele ponto, o motor decidiu sem registrar.
  `checkpoint_mismatches()` acusa.
- Se o parâmetro do §7.3 mudar **depois da coleta**, os `node_updates` gravados
  preservam o que o aluno de fato viu. Para reanalisar sob outra regra, use os
  campos crus (`option_idx`, `confidence`) — que continuam todos no log.

Campos crus e decisão convivem no mesmo evento de propósito: um serve à
reprodução da sessão, o outro à reanálise.

### Ferramenta de conferência

```bash
python -m tools.replay --verify            # sai 1 se alguma sessão divergir
python -m tools.replay --rebuild           # apaga node_state e reconstrói
python -m tools.replay --print S1          # linha do tempo legível de uma sessão
```

Rode `--verify` ao fim de cada coleta, antes de copiar o `.db` para as duas
mídias (§15).

## Convenções

- `data/structura.db` está fora do controle de versão.
- Nenhum termo do domínio de C fora de `domain/` (RNF01). Vale para testes.
- Nenhuma chamada de rede em tempo de sessão (RNF05).
