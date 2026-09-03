# Structura

Sistema de refutação socrática para o domínio de ponteiros em C.
Implementação da especificação técnica v1.0 (Rafael H. S. Simão, UFV–CRP).

Piloto alvo: **30 de setembro de 2026**.

## Rodar

Testado em Python 3.14.7 (mínimo 3.11).

```bash
python -m pip install -r requirements.txt
python -m api.main
```

Abra `http://127.0.0.1:8000`. O servidor imprime o **hash do domínio** e o
**token de exportação** no arranque — anote os dois.

Se um YAML estiver inconsistente, o processo **não sobe** e lista o que está
errado (§1: falha na carga, não em sessão).

### Entre uma demonstração e a seguinte

```bash
rm data/structura.db data/structura.db-wal data/structura.db-shm
```

O token em `data/export_token.txt` sobrevive — reiniciar o servidor no meio
da coleta não invalida o token já anotado.

### Ao fim de cada sessão de coleta

```bash
python -m tools.replay --verify
python -m tools.export --out analise/
```

O primeiro confere que o estado de toda sessão é reconstruível do log
(RNF04). O segundo escreve as três tabelas e **sai com código 1** se as
sessões viram hashes de domínio diferentes (§15). Depois disso, copie
`data/structura.db` para duas mídias.

### Conferir que está tudo de pé

```bash
python -m pytest tests/ -q && python -m tools.validate --stats
```

150 testes; o validador tem de sair 0.

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
| 5 | `api/`: as seis rotas do §9 + retomada por replay | **feito** |
| 6 | `web/`: interface e `diagram.js` | **feito** |
| 7 | `feedback.yaml` + `feedback.py` (RF17, SHOULD) | **feito** |
| 8 | `export.py` + os três CSVs | **feito** |
| — | CIU de variação para os 8 KCs fora do piloto | não bloqueia |
| — | `visual:` estruturado por estado (ver abaixo) | **limita RF08** |

## Porta de CI

```bash
python -m tools.validate --stats   # domínio: sai 0 obrigatoriamente
python -m pytest tests/ -q         # motor e store
python -m tools.replay --verify    # RNF04 sobre o banco de coleta
python -m tools.freeze_golden      # só após mudança DELIBERADA no grafo
python -m tools.export --out analise/   # as três tabelas do §12
```

### As três tabelas

| Arquivo | Grão | Sustenta |
|---|---|---|
| `answers.csv` | uma resposta a CIU | Validação da Q-matrix — desfecho **primário** |
| `sessions.csv` | uma sessão | Tempo por braço, taxa de conclusão, ponto de abandono |
| `calibration.csv` | (participante, nível de confiança) | Calibração metacognitiva |

Tudo sai de `events`. **Nenhuma análise lê `node_state`** — se a projeção
estivesse errada, o erro entraria nos resultados sem deixar rastro; há teste
apagando a projeção e conferindo que o export não muda.

Duas colunas de `answers.csv` carregam a distinção do §7.3 e não podem virar
uma só: `chosen_misconception` é o distrator escolhido, **sempre**;
`belief_counted_active` é se aquilo contou como crença ativa, o que exige
errar com confiança declarada. Somadas, a frequência de cada crença na
população vem inflada por chutes.

`tools/export.py` sai com código 1 se as sessões viram hashes de domínio
diferentes (§15). É a pergunta que precisa ser respondida **antes** da
análise, não depois.

## Rodar o servidor

```bash
python -m api.main
```

Sobe em `127.0.0.1:8000`. O domínio é validado no arranque: YAML inconsistente
e o processo não sobe (§1). O hash do domínio é impresso e exposto em
`/health` — confira antes de cada sessão (§15). O token de exportação fica em
`data/export_token.txt`, ou vem de `STRUCTURA_EXPORT_TOKEN`.

### Por que a retomada é por replay

O estado da sessão **não existe em memória**. A cada requisição ele é
reconstruído replicando as entradas do log através da FSM. Custa ~10 ms
(medido; RNF03 pede ≤ 200) e compra: a sessão sobrevive a fechar a aba e a
reiniciar o servidor; o estado nunca diverge do log, porque não há estado; e
RNF04 passa a valer para o fluxo, não só para o vetor de premissas.

Só funciona porque a FSM é pura e determinística. Se entrar aleatoriedade ou
relógio no motor, a retomada quebra em silêncio — por isso
`test_sessao_retomada_termina_igual_a_que_nao_caiu` compara as duas.

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


## O que a interface exige antes de começar

Quatro campos, nenhum com padrão: **código**, **experiência prévia**,
**consentimento** e **braço**. O botão fica travado até os quatro existirem, e
o servidor recusa se algum faltar.

Não é atrito gratuito. Cada um é um dado que ninguém pode assumir por outro:
a alocação é decisão do pesquisador, o consentimento é ato do participante, e
a experiência prévia é a variável de estratificação do §4.3 — sem ela não se
mostra que os grupos ficaram equilibrados. Um participante que não consente
**não entra no banco**.

## Limite conhecido: o `visual:` não sustenta a comparação de dois estados

O RF08 existe para um caso específico: quando a crença nega um nó-base, não
há premissa anterior para confrontá-la, e só a observação direta reintroduz
o fato. A observação é **comparar dois estados** — antes e depois.

Os blocos `visual:` do domínio descrevem o diagrama em prosa:

```yaml
visual:
  kind: memory_diagram
  regions: [stack, literais]
  show:
    - "t: 4 caixas de char na stack, com copia de a b c  "
    - "s: uma caixa de ponteiro na stack, com seta para o literal"
```

Disso o renderizador desenha regiões nomeadas com as frases dentro — e é o
que ele faz. **Não** dá para desenhar o par antes/depois, porque não existe
conteúdo por estado: os dois desenhariam a mesma figura.

Por isso a alternância só aparece quando há conteúdo por estado. Um botão que
não muda nada geraria `diagram_toggled` sem significado, e é justamente esse
evento que transforma o apelo visual em dado (§5.2).

`web/diagram.js` **já implementa** o modo estruturado. Ele espera:

```yaml
visual:
  kind: memory_diagram
  states:
    antes_do_free:
      stack: [{name: p, value: "0x7ffd21a0"}]
      heap:  [{name: bloco, value: "int 42", note: "bloco valido"}]
      arrow: {from: p, to: bloco}
    depois_do_free:
      stack: [{name: p, value: "0x7ffd21a0"}]
      heap:  [{name: bloco, value: liberado, note: "nao mais valido", invalid: true}]
      arrow: {from: p, to: bloco, invalid: true}
  caption: "Alterne entre antes e depois. O que mudou? O que nao mudou?"
```

São 5 CIUs com `visual:` no catálogo. Converter as 3 que declaram `states:`
destrava o RF08 por inteiro; as outras 2 são estáticas e já funcionam.
