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

> **No Windows PowerShell**, `&&` não existe (é erro de parser no 5.1) e `rm -f`
> é ambíguo entre `-Force` e `-Filter`. Os comandos deste README estão em uma
> linha cada por isso; onde houver encadeamento, a versão PowerShell vem junto.

Abra `http://127.0.0.1:8000`. O servidor imprime o **hash do domínio** e o
**token de exportação** no arranque — anote os dois.

Se um YAML estiver inconsistente, o processo **não sobe** e lista o que está
errado (§1: falha na carga, não em sessão).

### Entre uma demonstração e a seguinte

```bash
rm -f data/structura.db*
```

PowerShell:

```powershell
Remove-Item data\structura.db* -Force -ErrorAction Ignore
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

PowerShell:

```powershell
python -m pytest tests/ -q; if ($?) { python -m tools.validate --stats }
```

150 testes; o validador tem de sair 0. Ele imprime avisos — 21 hoje, todos
documentados e nenhum bloqueante. Erro é o que sai com código diferente de 0.

## Como demonstrar o sistema

Quatro páginas, geradas do próprio domínio e do próprio log. Nenhuma delas
é o sistema — todas são **leituras** dele, e por isso nenhuma pode
dessincronizar: regenere depois de qualquer mudança e o que aparece é o que
o piloto vai rodar.

```
python -m tools.figuras  -o analise/premissas.html    # os 93 enunciados e figuras
python -m tools.grafo    -o analise/mapa.html         # os 12 grafos e os 46 caminhos
python -m tools.simular                               # 6 sessões, em banco separado
python -m tools.percurso -o analise/percursos.html    # o caminho de cada participante
```

### A ordem que funciona numa conversa de 20 minutos

**1 · O mapa** (`mapa.html`, nível de cima) — os 12 KCs, da esquerda para a
direita por prerequisito. Estabelece o tamanho do domínio e onde o piloto
corta: o KC 02 de aquecimento e os três KCs medidos, marcados. O número `9 +1` em cada caixa já introduz o
fecho alcançável, que volta depois.

**2 · Um grafo, no modo “todos os caminhos”** (abra o KC 07) — mostra que a
estrutura não é um mapa conceitual: as premissas de carga aparecem com
borda grossa e `6×`, as folhas com `1×`. É aqui que se explica base contra
inferência, e por que uma crença que nega um nó-base exige diagrama.

**3 · Um caminho, percorrido** (modo “um caminho”, escolha
`array_is_pointer`) — clique *Confirma* quatro vezes. O ponto é o passo 4:
o aluno afirma o contrário da crença com que entrou, e as três premissas
foram respostas dele. Depois clique *Erra* duas vezes para mostrar a
regressão.

**4 · Os enunciados** (`premissas.html`) — só se perguntarem o que o aluno
lê de fato. Cada nó com o enunciado do grafo, a versão simples, a pergunta
montada e a ilustração.

**5 · Um percurso real** (`percursos.html`) — fecha o ciclo: o mesmo grafo,
agora com o caminho que uma pessoa andou, reconstruído do log. Abra o
`SIM01` no KC 09 e mostre os passos que caem em nós de **outros KCs** — é o
fecho do item 1, aparecendo num percurso.

### Sobre os dados simulados

`tools/simular.py` grava sessões pelo caminho normal: chama o mesmo
`api.service` que a interface chama, e o motor emite os mesmos eventos. Não
há evento fabricado à mão — por isso a tela de percurso lê o dado simulado
exatamente como lerá o real.

Duas guardas, e as duas importam:

- **banco separado.** O padrão é `data/simulado.db`, e o script **recusa**
  gravar em algo chamado `structura*.db`. Participante simulado misturado ao
  real contaminaria o export do §12, e o erro só apareceria na análise.
- **código marcado.** `SIM01`, `SIM02`… O piloto usa `P01`–`P40`. A página
  de percurso mostra um aviso enquanto houver qualquer `SIM…` no banco.

Quando a coleta começar, é a mesma ferramenta apontada para o outro banco:

```
python -m tools.percurso --db data/structura.db -o analise/percursos.html
```

### O que a análise lê, e o que ela não lê

Só a tabela `events`, que é append-only e é a **fonte**. Nunca `node_state`,
que é projeção descartável (§4). Uma leitura de análise que dependesse do
cache deixaria de valer como prova na defesa — e o estado cognitivo
mostrado é calculado por `model.cognitive_state`, a mesma função que o motor
usa em sessão, e não por uma segunda regra escrita na ferramenta.


## Estado da construção

Ordem do §13 da spec. Marcos 1 a 3 são o caminho crítico.

| # | Entrega | Estado |
|---|---------|--------|
| — | `domain/c_pointers/*.yaml` — canônicos, do autor. 12 KCs, 93 nós, 34 crenças, 57 CIUs | **completo** |
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


## A introdução, e por que ela não pode ensinar

Antes da primeira atividade o participante lê seis cartões ilustrados:
o percurso da sessão, endereço, caixa, ponteiro, as duas regiões, e a escala
de confiança. Cada um tem uma figura em SVG, montada de `intro.yaml` — o tipo
de figura é vocabulário de apresentação (`web/figures.js`), o conteúdo é domínio.

**A introdução cobre a mobília, nunca as conclusões dos KCs que o piloto mede.**
Se ela dissesse "array e ponteiro são tipos distintos", teria ensinado a
resposta da primeira atividade, e o diagnóstico deixaria de medir a crença
prévia do aluno — que é o desfecho primário. `tools/validate.py` recusa o
domínio se um cartão mencionar termo distintivo de `kc_07`, `kc_11` ou `kc_09`.

É idêntica nos dois braços: acontece antes de eles divergirem. Cada cartão
confirmado emite `stage_acknowledged` com o tempo de leitura, então a retomada
volta ao cartão certo e o tempo de orientação entra na análise separado do
tempo de tarefa.


## Duas versões de cada premissa

Um nó do grafo pode declarar, além de `text`, dois campos opcionais:

```yaml
B1:
  type: base
  text:  "int a[5] reserva 5 ints contiguos e nomeados."
  plain: "int a[5] cria 5 caixas de inteiro grudadas uma na outra. O nome a
          vale para o conjunto inteiro, não para uma caixa só."
  figure: {kind: array_row, ...}
```

`text` é a proposição do grafo de premissas — a que tem proveniência, a que
os planos golden congelam, a que a banca cobra. `plain` é **apresentação**:
a mesma proposição dita a quem ainda não tem o vocabulário. Os dois convivem
porque servem a leitores diferentes, e nenhum deve ser derivado do outro por
heurística. Sem `plain`, o nó é apresentado pelo `text`, como sempre.

Quem lê `plain` lê em **todo lugar**: a pergunta do traversal, a citação do
suporte nas inferências, o texto do braço direto e a contradição do RF17. Se
a contradição devolvesse o enunciado canônico depois de o aluno ter
confirmado a versão simples, ele não reconheceria como sua uma frase que
nunca leu — e a etapa 2 do RF17 vale justamente por dizer *"repare no que
você confirmou"*.

Os dois braços leem sempre a mesma versão (§8.1). Simplificar um braço só
seria dar-lhe um apoio que o outro não tem, e a variável isolada deixaria de
ser a geração ativa. `tests/test_plain.py` afirma isso.

**Os 93 nós dos 12 KCs estão simplificados e ilustrados.** O `kc_07` foi
feito primeiro, sozinho, para o registro ser julgado antes de valer para o
resto — e o resto seguiu esse registro.

O conector de discurso ("Então…", "Por isso…", "Mas…") pertence ao
enunciado do nó, não ao molde da pergunta. O braço direto apresenta o
mesmo texto **sem molde nenhum**: sem o conector, a frase chegaria solta.
Com um conector no molde também, o participante lia "Juntando: Então p e a
caixa…".

Dois avisos do validador guardam a uniformidade — e continuam valendo para
quem trocar o domínio:

- **registro uniforme por KC** — um KC com metade dos nós simplificados
  misturaria os dois registros no mesmo traversal.
- **pergunta com registro misto** — mais preciso: nomeia a pergunta em que
  parte das premissas citadas tem `plain` e parte não. Pega o caso que a
  conferência por KC não pega, o do suporte que vem de outro KC. Foi ele
  que mostrou que simplificar não custa por KC, e sim por **fecho
  alcançável**: o `kc_07` puxa um nó do `kc_06`; o `kc_09` puxa nove, de
  `kc_04`, `kc_05` e `kc_06`.

Para julgar o registro:

```
python -m tools.figuras -o analise/premissas.html
```

Sem argumentos, o domínio inteiro na ordem de ensino; com ids (`kc_07
kc_11`), só esses. A página põe lado a lado, para cada nó e na ordem do
traversal, o enunciado do grafo, a versão simples, a pergunta montada e a
ilustração — renderizada pelo mesmo `web/figures.js` do piloto.

### Os tipos de figura

O tipo é vocabulário de apresentação e vive em `web/figures.js`; o
conteúdo — rótulos, valores, legendas — vem do YAML. Nenhuma frase sobre C
mora no renderizador, que é o que o §1 pede.

| tipo | o que mostra |
|---|---|
| `street` | memória como posições numeradas |
| `boxes` | variáveis como caixas com nome, valor e endereço |
| `pointer_pair` | duas caixas, uma guardando o endereço da outra; `target.gone` desenha o destino que já não vale |
| `chain` | caixas em fila, cada uma guardando a seguinte — a indireção |
| `regions` | duas áreas com regras de arrumação diferentes |
| `array_row` | caixas **grudadas**, com índice |
| `array_decay` | a fileira mais o nome trocado pelo endereço da 1ª caixa |
| `stride` | um salto sobre caixas de largura proporcional |
| `sizes` | barras em escala, para comparar medida |
| `call_frame` | o que atravessa a fronteira de uma chamada |
| `two_cases` | dois painéis: o caso que vale e o que não vale |
| `session_map`, `confidence` | só a introdução |

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
    - "t: 4 caixas de char na stack, com copia de a b c \0"
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
