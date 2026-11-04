# A posição da alternativa certa — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a alternativa certa deixa de estar na primeira posição em 98,4%
dos itens, por uma permutação estável derivada do código da sessão.

**Architecture:** uma função pura no motor, irmã da `ordem_das_razoes` que
já existe, lida nas seis pontas que hoje dependem da posição em `opcoes` —
duas que escrevem a tela e quatro que leem o que voltou dela. Nenhum estado
novo: a ordem é função de (semente, item). `Atividade.indice_correto` é
renomeada antes de qualquer mudança de comportamento, para que as 22
chamadas que a usam virem erro em voz alta em vez de responder outra coisa
em silêncio.

**Tech Stack:** Python 3.14, `hashlib.sha256`, pytest, FastAPI (as rotas
já existem).

**Spec:** [posicao.md](posicao.md)

## Global Constraints

- O motor é **puro**: nada de `random`. A ordem sai de `sha256`, e a mesma
  (semente, item) devolve a mesma ordem sempre.
- O separador do digest é `"%s|opcoes|%s"`, e nunca `|razoes|`: as duas
  camadas não podem receber a mesma permutação para o mesmo item.
- `Resposta.escolha` **é a posição na tela** — o docstring já diz isso em
  `mvp/motor.py:186`. Esta fatia faz a camada 1 cumprir.
- Nenhum arquivo de `mvp/dominio/` é tocado. Os 562 itens não se movem, e a
  assinatura de quem revisou molde continua valendo.
- Nunca apagar, pular, enfraquecer ou alterar um teste existente para
  ficar verde. Teste que cai por motivo certo é achado: pare e avise.
- O validador `_indice` roda **antes** da permutação. Índice inválido é
  `EscolhaInvalida`, nunca `IndexError` dentro de uma permutação.

## Review Focus

- **Item com duas alternativas** (13 dos 562): `n=2` tem duas permutações
  e metade das sementes devolve a identidade. Isso não é defeito, e um
  teste de distribuição plana *entre itens* acusaria errado. Pinado na
  Tarefa 5.
- **Semente vazia** (sessão sem código): a permutação roda e é estável,
  mas toda sessão sem código vê a mesma ordem. É o comportamento das
  razões hoje; o que não pode é a ordem ser a do arquivo. Pinado na
  Tarefa 1.
- **`escolha` negativa ou fora de faixa**: `opcoes[-1]` é válido em
  Python, e já foi defeito aqui (`mvp/test_entrada.py:4`). Com permutação
  há um segundo índice no caminho. Pinado na Tarefa 3.
- **Linha de log sem o campo `v`** (`VERSAO_ZERO`, do ciclo 1): é um caso
  distinto de `v1`, e cai no mesmo ramo da reexecução. Pinado na Tarefa 4.
- **Dois itens com a mesma permutação por colisão de digest**: inofensivo
  e esperado. Nenhum teste pode afirmar que ordens de itens diferentes
  diferem. Pinado na Tarefa 1 como contraprova.

---

### Tarefa 1: as duas funções puras

**Files:**
- Modify: `mvp/motor.py` (ao lado de `ordem_das_razoes`, linha 730)
- Test: `mvp/test_posicao.py` (criar)

**Interfaces:**
- Consumes: `ordem_das_razoes(semente, atividade, n)`, que já existe.
- Produces:
  - `ordem_das_opcoes(semente: str, atividade: str, n: int) -> tuple[int, ...]`
    — a permutação, como índices do arquivo na ordem da tela.
  - `indice_correto_na_tela(semente: str, a: Atividade) -> int`

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_a_ordem_e_estavel(d):
    a = d.atividades[0]
    assert (motor.ordem_das_opcoes("P01", a.id, 3)
            == motor.ordem_das_opcoes("P01", a.id, 3))

def test_a_ordem_e_uma_permutacao(d):
    for n in (2, 3, 4):
        assert sorted(motor.ordem_das_opcoes("P01", "x", n)) == list(range(n))

def test_sementes_diferentes_dao_ordens_diferentes(d):
    """O que mata o vazamento entre participantes: o P03 contar ao P04
    que "a do array e a terceira" nao transfere."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    ordens = {motor.ordem_das_opcoes("P%02d" % i, a.id, 3) for i in range(1, 41)}
    assert len(ordens) > 1, ordens

def test_a_semente_vazia_nao_devolve_a_ordem_do_arquivo(d):
    """Sessao sem codigo nao e desculpa para o vies voltar."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    assert motor.ordem_das_opcoes("", a.id, 3) != (0, 1, 2)

def test_as_duas_camadas_nao_recebem_a_mesma_permutacao(d):
    """Se recebessem, a posicao da resposta prediria a posicao da razao —
    um segundo vies no lugar do primeiro. Medido no banco inteiro: duas
    funcoes iguais dariam 100%."""
    tres = [x for x in d.atividades if len(x.opcoes) == 3]
    iguais = sum(motor.ordem_das_opcoes("P01", x.id, 3)
                 == motor.ordem_das_razoes("P01", x.id, 3) for x in tres)
    assert iguais < len(tres) * 0.5, (iguais, len(tres))

def test_itens_diferentes_podem_coincidir(d):
    """Contraprova: colisao de digest entre itens e esperada e inofensiva.
    Nenhum teste pode exigir que ordens de itens diferentes difiram."""
    tres = [x for x in d.atividades if len(x.opcoes) == 3]
    ordens = [motor.ordem_das_opcoes("P01", x.id, 3) for x in tres]
    assert len(set(ordens)) <= 6, "sao 6 permutacoes possiveis para n=3"

def test_o_indice_certo_na_tela_aponta_a_alternativa_certa(d):
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    ordem = motor.ordem_das_opcoes("P01", a.id, 3)
    i = motor.indice_correto_na_tela("P01", a)
    assert a.opcoes[ordem[i]].correta

def test_a_escala_de_confianca_nao_e_embaralhada():
    """Fronteira de escopo, pinada. CONFIANCAS e ORDINAL: a ordem dela E
    a escala, e embaralhar destruiria a leitura. Alem disso o vies nem
    existe ali, porque nenhuma das tres e a certa."""
    assert motor.CONFIANCAS == ("chutei", "acho que sei", "tenho certeza")
```

- [ ] **Passo 2: rodar e ver falhar**

Run: `python -m pytest mvp/test_posicao.py -q`
Expected: FAIL — `module 'mvp.motor' has no attribute 'ordem_das_opcoes'`

- [ ] **Passo 3: implementar as duas em `mvp/motor.py`**

`ordem_das_opcoes` é a `ordem_das_razoes` com `|opcoes|` no lugar de
`|razoes|`. `indice_correto_na_tela` devolve a posição, **na ordem
mostrada**, do índice de arquivo cuja opção é a correta.

- [ ] **Passo 4: rodar e ver passar**

Run: `python -m pytest mvp/test_posicao.py -q`
Expected: PASS, 8 testes

- [ ] **Passo 5: commitar**

```bash
git add mvp/motor.py mvp/test_posicao.py
git commit -m "A permutacao das alternativas, irma da que ja existe"
```

---

### Tarefa 2: o rename, antes de qualquer mudança de comportamento

**Files:**
- Modify: `mvp/dominio.py:180-182`
- Modify: `scripts/caminhante.py:140`
- Modify: os 10 arquivos de teste que chamam `indice_correto`
- Test: `mvp/test_posicao.py`

**Interfaces:**
- Produces: `Atividade.indice_correto_no_arquivo` (a propriedade de antes,
  com o nome que diz o que ela significa). `Atividade.indice_correto`
  **deixa de existir**.

Esta tarefa não muda comportamento nenhum: a suíte fica verde antes e
depois. Ela existe para que a Tarefa 3 não possa falhar em silêncio.

- [ ] **Passo 1: escrever o teste que falha**

```python
def test_nao_existe_mais_indice_correto_sem_qualificacao(d):
    """A trava desta fatia. O nome antigo dizia "a posicao da certa", e
    passou a ter duas respostas: no arquivo e na tela. Enquanto ele
    existir, 22 chamadas continuam executando e querendo dizer a
    errada — sem erro, com estado plausivel e errado."""
    a = d.atividades[0]
    assert not hasattr(a, "indice_correto")
    assert isinstance(a.indice_correto_no_arquivo, int)
```

- [ ] **Passo 2: rodar e ver falhar**

Run: `python -m pytest mvp/test_posicao.py -k indice_correto_sem -q`
Expected: FAIL no primeiro `assert`

- [ ] **Passo 3: renomear a propriedade e cada chamada**

22 sítios. `grep -rn "indice_correto" mvp/ scripts/ --include=*.py` lista
todos; nenhum fica com o nome antigo. Ainda é `_no_arquivo` em todos — a
troca para `_na_tela` é da Tarefa 3.

- [ ] **Passo 4: rodar a suíte inteira**

Run: `bash scripts/verify.sh`
Expected: verde, com os mesmos números de antes (715 + 252). Qualquer
mudança de número aqui é defeito: esta tarefa não muda comportamento.

- [ ] **Passo 5: commitar**

```bash
git add -A mvp scripts
git commit -m "indice_correto vira indice_correto_no_arquivo"
```

---

### Tarefa 3: a permutação ligada, nas seis pontas de uma vez

**Files:**
- Modify: `mvp/motor.py` — `_apresenta` (671), `_entrada` (1108),
  `_responde_diagnostico` (747), `_responde_treino` (1526),
  `_responde_entrada` (1129), `_pede_confianca` (852)
- Modify: `scripts/caminhante.py` — `escolhe` precisa da semente
- Modify: os testes que respondem certo, de `_no_arquivo` para `_na_tela`
- Test: `mvp/test_posicao.py`

**Interfaces:**
- Consumes: `ordem_das_opcoes`, `indice_correto_na_tela` (Tarefa 1);
  `indice_correto_no_arquivo` (Tarefa 2).
- Produces: `escolhe(tela, persona, chaves, sessao)` no caminhante — a
  assinatura ganha a sessão, porque sem ela o andarilho não sabe mais
  qual índice é o certo.

As duas escritas e as quatro leituras **landam juntas**. Separá-las
produziria o estado em que a tela mostra uma ordem e o motor lê outra, que
é justamente o defeito.

- [ ] **Passo 1: escrever o teste de ponta a ponta que falha**

Pelas rotas HTTP, com `TestClient`, porque um teste que chama a permutação
dos dois lados concorda consigo mesmo mesmo quando está errado.

Um auxiliar, usado pelos quatro testes — abre a sessão e avança até a
primeira tela de atividade, respondendo `{"ms": 100}` em tudo que não é
atividade (abertura, frase, ensino):

```python
def _ate_a_atividade(cliente, codigo=""):
    """Devolve (sessao, tela da primeira atividade)."""
```

```python
def test_o_indice_clicado_julga_o_texto_que_estava_ali(cliente, d):
    """O unico teste que pega o desencontro entre o que foi mostrado e o
    que foi lido. A tela entrega TEXTOS; a pessoa clica numa POSICAO."""
    sessao, tela = _ate_a_atividade(cliente, "P01")
    textos = [o["texto"] for o in tela["opcoes"]]
    a = next(x for x in d.atividades if x.id == tela["atividade"])
    i = motor.indice_correto_na_tela("P01", a)
    depois = cliente.post("/sessoes/%s/responder" % sessao,
                          json={"escolha": i, "ms": 100}).json()["tela"]
    # `trancada` repete o texto da alternativa escolhida: e ali que o
    # desencontro aparece, porque sai de `_pede_confianca`.
    assert depois["dados"]["trancada"] == textos[i]
    assert a.opcoes[a.indice_correto_no_arquivo].texto == textos[i]

def test_a_certa_nao_fica_sempre_na_primeira(cliente, d):
    """A prova, pela tela, de que a fatia resolveu o que a motivou."""
    posicoes = set()
    for codigo in ("P01", "P02", "P03", "P04", "P05", "P06"):
        _, tela = _ate_a_atividade(cliente, codigo)
        a = next(x for x in d.atividades if x.id == tela["atividade"])
        posicoes.add(motor.indice_correto_na_tela(codigo, a))
    assert len(posicoes) > 1, posicoes

def test_escolha_fora_de_faixa_continua_recusada(cliente):
    """`opcoes[-1]` e valido em Python, e ja foi defeito aqui
    (test_entrada.py:4). Agora ha um segundo indice no caminho: a
    validacao vem ANTES da permutacao, ou o erro vira IndexError."""
    sessao, _ = _ate_a_atividade(cliente, "P01")
    for ruim in (-1, 3, 99):
        r = cliente.post("/sessoes/%s/responder" % sessao,
                         json={"escolha": ruim, "ms": 100})
        assert r.status_code == 400, (ruim, r.status_code)

def test_o_item_reapresentado_volta_na_mesma_ordem(cliente, d):
    """E a mesma pergunta: a pessoa pode raciocinar "a primeira eu ja
    descartei". Erra de proposito, segue ate o item voltar, e compara os
    textos na ordem."""
    sessao, tela = _ate_a_atividade(cliente, "P01")
    antes = [o["texto"] for o in tela["opcoes"]]
    # ... erra, atravessa a refutacao, ate `atividade` com o mesmo id
    assert [o["texto"] for o in volta["opcoes"]] == antes
```

- [ ] **Passo 2: rodar e ver falhar**

Run: `python -m pytest mvp/test_posicao.py -q`
Expected: FAIL — `test_a_certa_nao_fica_sempre_na_primeira` com uma
posição só no conjunto, porque a tela ainda entrega a ordem do arquivo.

- [ ] **Passo 3: ligar as seis pontas**

As duas escritas emitem `opcoes` na ordem de `ordem_das_opcoes(e.semente,
a.id, len(a.opcoes))`. As quatro leituras traduzem o índice da tela para o
índice do arquivo pela mesma ordem, **depois** de `_indice` validar.
`_pede_confianca` lê `p.escolha`, que é posição de tela, e traduz igual.

- [ ] **Passo 4: trocar os sítios de teste que respondem certo**

De `indice_correto_no_arquivo` para
`motor.indice_correto_na_tela(t.estado.semente, a)`. Os que respondem
**errado** (`_errada` em `test_classificacao.py:63` e
`test_motor.py:41`) também: eles escolhem por crença, e a posição dela
agora é a da tela.

- [ ] **Passo 5: consertar o caminhante**

`escolhe` recebe `sessao` e calcula o índice certo com
`indice_correto_na_tela`. Hoje ele monta `{a.id: a.indice_correto}` fora
da sessão, e esse mapa deixa de fazer sentido.

- [ ] **Passo 6: rodar a suíte inteira, e o caminhante**

Run: `bash scripts/verify.sh`
Expected: verde.

Run: `python -m mvp.app` noutro terminal, e
`python scripts/caminhante.py --persona sabido`
Expected: a persona `sabido` termina com **nenhuma** premissa sem medida.
Se ela errar, a tradução está invertida em alguma das seis pontas.

- [ ] **Passo 7: commitar**

```bash
git add -A mvp scripts
git commit -m "A camada 1 passa a cumprir o que o Resposta.escolha promete"
```

---

### Tarefa 4: o log, e a versão

**Files:**
- Modify: `mvp/log.py:69` (`VERSAO`), `reconstroi` (210)
- Modify: `mvp/motor.py` — o evento `atividade_apresentada` (676 e 1111)
- Test: `mvp/test_reconstrucao.py`, `mvp/test_posicao.py`

**Interfaces:**
- Consumes: `ordem_das_opcoes` (Tarefa 1).
- Produces: `log.VERSAO == 2`; `atividade_apresentada` com a chave
  `ordem: list[int]`.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_a_ordem_mostrada_vai_para_o_log(d, caminho):
    """Redundante para o CS-6 e nao para a analise: com o campo, o vies
    residual e medivel no proprio dado, e uma mudanca futura na funcao
    nao reescreve o que os participantes viram."""
    t = motor.inicia(d, semente="P01")
    # ... avanca ate a primeira atividade, gravando os eventos
    linha = next(x for x in log.le("P01", caminho)
                 if x["tipo"] == "atividade_apresentada")
    a = next(x for x in d.atividades if x.id == linha["atividade"])
    assert linha["ordem"] == list(
        motor.ordem_das_opcoes("P01", a.id, len(a.opcoes)))

def test_a_versao_subiu_porque_o_indice_mudou_de_significado():
    assert log.VERSAO == 2

def test_sessao_v1_ainda_reexecuta(d, caminho):
    """Gravada sem permutacao na camada 1: o indice dela e posicao de
    ARQUIVO. Reexecutar com semente devolveria OUTRA resposta — acerto
    virando erro, e o estado saindo plausivel e errado.

    O log v1 e escrito a mao aqui, porque gravar um com o codigo de hoje
    e impossivel: ele grava v2."""
    _escreve_log(caminho, "S1", v=1, entradas=[{"escolha": 0, "ms": 100}])
    t = log.reconstroi(d, "S1", caminho)
    assert t is not None
    # com semente="" a escolha 0 e a alternativa 0 DO ARQUIVO
    a = next(x for x in d.atividades if x.id == t.estado.atividade)
    assert t.estado.pendente.correta is a.opcoes[0].correta

def test_linha_sem_campo_v_reexecuta_como_v1(d, caminho):
    """VERSAO_ZERO, do ciclo 1: caso distinto de v1, mesmo ramo. Linha
    sem o campo nao pode cair no ramo da permutacao por omissao."""
    _escreve_log(caminho, "S0", v=None, entradas=[{"escolha": 0, "ms": 100}])
    assert log.reconstroi(d, "S0", caminho) is not None
```

`_escreve_log(caminho, sessao, *, v, entradas)` escreve as linhas à mão —
`unidade_iniciada` com o tópico de `d`, e uma `entrada_recebida` por
entrada —, omitindo a chave `v` quando `v is None`.

- [ ] **Passo 2: rodar e ver falhar**

Run: `python -m pytest mvp/test_posicao.py mvp/test_reconstrucao.py -q`
Expected: FAIL — `KeyError: 'ordem'` e `assert 1 == 2`

- [ ] **Passo 3: implementar**

`VERSAO = 2`, com a entrada nova no comentário que lista as versões — o
arquivo já pede isso. Os dois `atividade_apresentada` ganham `ordem`.
`reconstroi` lê o `v` da abertura e chama
`motor.inicia(d, semente="" if versao < 2 else sessao)`.

- [ ] **Passo 4: rodar e ver passar**

Run: `python -m pytest mvp/test_posicao.py mvp/test_reconstrucao.py -q`
Expected: PASS

- [ ] **Passo 5: commitar**

```bash
git add mvp/log.py mvp/motor.py mvp/test_reconstrucao.py mvp/test_posicao.py
git commit -m "O log grava a ordem mostrada, e a VERSAO sobe para 2"
```

---

### Tarefa 5: a medida do viés, como teste

**Files:**
- Test: `mvp/test_posicao.py`
- Modify: `docs/posicao.md`, `docs/processo.md`

**Interfaces:**
- Consumes: tudo das tarefas anteriores.

A prova direta de que a fatia resolveu o problema que a motivou. As outras
provam o mecanismo.

- [ ] **Passo 1: escrever o teste**

A medida é **por item, ao longo das sementes** — e não entre itens. É o
que importa (o confundimento é entre participantes) e é o que funciona
para os 13 itens de duas alternativas, onde `n=2` tem só duas
permutações e metade das sementes devolve a identidade:

```python
def test_o_vies_de_posicao_acabou(d):
    """Antes: 553 de 562 com a certa na primeira. A medida e por item, ao
    longo de 40 sementes — uma por participante do piloto —, porque o
    confundimento e ENTRE participantes.

    O limite, e nao o numero: numero cravado e a quinta recorrencia de um
    defeito que este projeto ja catalogou quatro vezes."""
    sementes = ["P%02d" % i for i in range(1, 41)]
    for a in d.atividades:
        k = len(a.opcoes)
        c = collections.Counter(motor.indice_correto_na_tela(s, a) for s in sementes)
        assert set(c) == set(range(k)), (a.id, c)
        assert max(c.values()) <= len(sementes) / k * 1.8, (a.id, c)

def test_o_banco_inteiro_numa_sessao_nao_concentra(d):
    """A visao de UM participante: na sessao dele, a certa nao fica na
    primeira posicao mais do que o acaso. E a medida que estava em
    98,4%, agora pela tela.

    So os de tres alternativas: nos 13 de duas, metade das sementes
    devolve a identidade, e misturar os dois grupos mede ruido."""
    tres = [a for a in d.atividades if len(a.opcoes) == 3]
    c = collections.Counter(motor.indice_correto_na_tela("P01", a) for a in tres)
    assert set(c) == {0, 1, 2}, c
    assert max(c.values()) <= len(tres) / 3 * 1.3, c
```

- [ ] **Passo 2: rodar e ver passar**

Run: `python -m pytest mvp/test_posicao.py -q`
Expected: PASS. Se falhar em algum item de duas alternativas, o limite
está apertado demais para `n=2` — corrija o limite, nunca a medida.

- [ ] **Passo 3: medir o antes e o depois, e escrever**

Run: o mesmo levantamento que achou os 553/562, agora pela tela.
Expected: o número entra em `docs/posicao.md` (o cabeçalho sai de "ainda
não implementado") e em `docs/processo.md`, com o que a fatia achou.

- [ ] **Passo 4: a suíte inteira**

Run: `bash scripts/verify.sh`
Expected: verde.

- [ ] **Passo 5: commitar**

```bash
git add -A mvp docs
git commit -m "O vies de posicao, medido como teste"
```
