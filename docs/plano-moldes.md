# Moldes paramétricos — plano de implementação

> **Para quem executa:** use `superpowers:subagent-driven-development` ou
> `superpowers:executing-plans` para implementar tarefa a tarefa. Os passos
> usam caixa (`- [ ]`) para marcação.

**Objetivo:** multiplicar o banco de itens a partir de moldes com parâmetros,
com um compilador C conferindo cada variação, e registrar de qual molde e
com quais parâmetros veio cada item respondido.

**Arquitetura:** o molde vive fora do domínio (`mvp/dominio/moldes_*.yaml`) e
é lido só pelo gerador. `mvp/molde.py` tem a parte pura — formato, validação
e expansão determinística; `scripts/oraculo.py` compila e roda; o
`scripts/gerar.py` orquestra os quatro portões e escreve candidatos. O que
chega à sessão é um item de YAML como qualquer outro, com dois campos a mais
de procedência.

**Stack:** Python 3.14, PyYAML, pytest, gcc (MinGW-W64) 16.2.0 em
`C:\Users\Public\gcc`.

**Spec:** [docs/moldes.md](moldes.md)

## Restrições globais

- O caminho do gcc **não pode ter espaço**: o `ld` do MinGW não resolve o
  próprio prefixo quando há um. Nesta máquina, `C:\Users\Public\gcc\mingw64\bin\gcc.exe`.
- Compilar e rodar sempre em pasta temporária, com **caminhos relativos** e
  `cwd` na pasta.
- Todo programa do oráculo roda com `timeout=10` segundos.
- Nenhuma mudança no critério de domínio: `CONFIRMADO` continua como está.
- O motor nunca instancia molde: a expansão é offline.
- Disciplina do projeto: cada regra nova ganha uma sabotagem que derruba o
  teste dela. Teste que não cai quando a regra sai não defende nada.
- Mensagem de commit em português, sem acento, no estilo das que já existem.

## Foco da revisão

Cinco entradas que a spec implica e que nenhuma tarefa exercita por acaso.
Cada uma tem o teste indicado na tarefa que é dona do código.

1. **Buraco no texto que não existe nos parâmetros** (`{tamanho}` quando o
   parâmetro é `n`): tem de virar erro de validação com o nome do buraco, e
   não `KeyError` na expansão. — Tarefa 5.
2. **Menos combinações do que variações pedidas** (dois parâmetros de um
   valor só, e `quantas=6`): a expansão devolve o que existe, sem repetir
   nem estourar. — Tarefa 6.
3. **gcc ausente ou no caminho errado**: mensagem dizendo onde ele foi
   procurado, e não traceback de `FileNotFoundError`. — Tarefa 8.
4. **Programa que não termina**: o `timeout` corta e a variação é reprovada
   com o motivo, sem pendurar o gerador. — Tarefa 8.
5. **Variação que viola o contrato** (gabarito vira o texto mais longo em
   `n=8`): o portão recusa o molde dizendo **qual** variação quebrou. —
   Tarefa 9.

---

### Tarefa 1: O item sabe de que molde veio

**Arquivos:**
- Modificar: `mvp/dominio.py` (dataclass `Atividade`, lista ~160; parse ~503)
- Testar: `mvp/test_dominio.py`

**Interfaces:**
- Produz: `Atividade.do_molde: str = ""` e
  `Atividade.parametros: Mapping[str, Any]` (vazio por omissão).

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_item_sem_molde_continua_valendo(d):
    a = next(x for x in d.atividades if x.id == "ciu_kc00_001")
    assert a.do_molde == ""
    assert a.parametros == {}


def test_item_de_molde_carrega_a_procedencia(tmp_path):
    def muda(cru):
        atividade(cru, "ciu_kc00_002").update(
            do_molde="mol_teste", parametros={"tipo": "int", "n": 5})
    d = carrega(monta(tmp_path / "m1", muda))
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    assert a.do_molde == "mol_teste"
    assert a.parametros == {"tipo": "int", "n": 5}


def test_meia_procedencia_nao_carrega(tmp_path):
    """Molde sem parâmetros, ou o contrário, PARECE procedência."""
    for i, campo in enumerate(("do_molde", "parametros")):
        def muda(cru, campo=campo):
            atividade(cru, "ciu_kc00_002")[campo] = (
                "mol_teste" if campo == "do_molde" else {"n": 5})
        with pytest.raises(DominioInvalido) as erro:
            carrega(monta(tmp_path / ("m2_%d" % i), muda))
        assert any("procedência" in p and "ciu_kc00_002" in p
                   for p in erro.value.problemas), erro.value.problemas
```

- [ ] **Passo 2: rodar e ver falhar**

Roda: `python -m pytest mvp/test_dominio.py -k procedencia -v`
Espera: FAIL — `Atividade` não tem `do_molde`.

- [ ] **Passo 3: acrescentar os dois campos a `Atividade` e lê-los no parse**

Opcionais, porque item escrito à mão não tem molde. No parse, acrescentar à
lista `problemas` quando só um dos dois estiver presente, com a palavra
`procedência` e o id do item na mensagem.

- [ ] **Passo 4: rodar e ver passar**

Roda: `python -m pytest mvp/test_dominio.py -q`

- [ ] **Passo 5: sabotar** — tirar a checagem de meia procedência e conferir
que `test_meia_procedencia_nao_carrega` cai.

- [ ] **Passo 6: commit**

```bash
git add mvp/dominio.py mvp/test_dominio.py
git commit -m "O item de atividade carrega de que molde veio"
```

---

### Tarefa 2: O log grava a procedência

**Arquivos:**
- Modificar: `mvp/motor.py` (os dois sítios de `atividade_apresentada`: ~643 e ~1075)
- Testar: `mvp/test_motor.py`

**Interfaces:**
- Consome: `Atividade.do_molde`, `Atividade.parametros` (Tarefa 1).
- Produz: o evento `atividade_apresentada` com `do_molde` e `parametros`
  **apenas quando `a.do_molde` não é vazio**.

- [ ] **Passo 1: escrever o teste que falha**

```python
def test_o_log_diz_de_que_molde_veio_o_item(d, tmp_path):
    """Sem isto, nada do resto é mensurável."""
    # domínio com um item de molde, montado como em test_dominio.monta
    ...
    apresentadas = _dos(eventos, "atividade_apresentada")
    de_molde = [x for x in apresentadas if x.get("do_molde")]
    assert de_molde and de_molde[0]["parametros"] == {"tipo": "int", "n": 5}


def test_item_escrito_a_mao_nao_polui_o_log(d):
    """O log dos 556 itens de hoje não muda: campo vazio não entra."""
    t, eventos = roda(d, _politica())
    for x in _dos(eventos, "atividade_apresentada"):
        assert "do_molde" not in x and "parametros" not in x
```

- [ ] **Passo 2: rodar e ver falhar**

Roda: `python -m pytest mvp/test_motor.py -k molde -v`

- [ ] **Passo 3: acrescentar os dois campos aos dois eventos**

Condicional ao `do_molde` não vazio, nos dois sítios.

- [ ] **Passo 4: rodar a suíte inteira do MVP**

Roda: `python -m pytest mvp -q`
Espera: 582 + 2 passando, nenhuma quebra nos testes de log e reexecução.

- [ ] **Passo 5: sabotar** — gravar os campos sempre, inclusive vazios, e
conferir que `test_item_escrito_a_mao_nao_polui_o_log` cai.

- [ ] **Passo 6: commit**

---

### Tarefa 3: A tabela do painel ganha as duas colunas

**Arquivos:**
- Modificar: `mvp/painel.py` (`episodios`, ~54-120)
- Testar: `mvp/test_painel.py`

**Interfaces:**
- Consome: o evento da Tarefa 2.
- Produz: cada linha de `episodios()` com as chaves `do_molde` (str) e
  `parametros` (dict), vazias para item escrito à mão.

- [ ] **Passo 1: escrever o teste que falha**

```python
def test_a_tabela_diz_de_que_molde_veio_cada_episodio():
    linhas = [
        {"tipo": "atividade_apresentada", "atividade": "t_1", "no": "B1",
         "do_molde": "mol_x", "parametros": {"n": 5}},
        {"tipo": "camada1_respondida", "atividade": "t_1", "no": "B1",
         "correta": True},
        {"tipo": "unidade_encerrada"},
    ]
    linha = episodios(linhas)[0]
    assert linha["do_molde"] == "mol_x"
    assert linha["parametros"] == {"n": 5}
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

`episodios` passa a guardar, num dicionário por id de atividade, o
`do_molde` e os `parametros` vistos em `atividade_apresentada`, e a
preencher as duas chaves ao abrir o episódio em `camada1_respondida`. As
chaves existem em toda linha, vazias quando não houver molde.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: commit**

---

### Tarefa 4: A marca da generalização, no mapa

**Arquivos:**
- Modificar: `mvp/motor.py` (`EstadoNo`, ~245; ramos `CONFIRMADA` e
  `FRAGIL_EP` em `_responde_confianca`, ~896-926; `estado_dos_nos`, ~1744)
- Modificar: `mvp/web/app.js` (`telaMapa`), `mvp/web/index.html` (legenda)
- Testar: `mvp/test_motor.py`

**Interfaces:**
- Consome: `Atividade.do_molde`, `Atividade.parametros`.
- Produz: `EstadoNo.instancias: tuple[str, ...]` — assinaturas
  `"<molde>|<k=v,k=v ordenado>"` dos acertos **pela razão certa**; e a chave
  `generalizou: bool` em cada nó de `estado_dos_nos`, verdadeira quando
  algum molde aparece com duas assinaturas distintas.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_acertar_duas_instancias_do_mesmo_molde_e_generalizar():
    # dois acertos, mesmo molde, parâmetros distintos
    assert estado_dos_nos(d, e)[0]["generalizou"] is True


def test_acertar_a_mesma_instancia_duas_vezes_nao_e_generalizar():
    """Repetir a mesma pergunta mede memória, não generalização."""
    assert estado_dos_nos(d, e)[0]["generalizou"] is False


def test_no_sem_item_de_molde_nunca_generaliza():
    """Os 556 itens de hoje não têm molde: a marca fica falsa, não some."""
    t, eventos = roda(d, _politica())
    assert all(n["generalizou"] is False for n in estado_dos_nos(d, t.estado))
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Assinatura: `"%s|%s" % (a.do_molde, ",".join("%s=%s" % kv for kv in sorted(a.parametros.items())))`.
Gravar nos dois ramos de acerto pela razão certa (`CONFIRMADA` e
`FRAGIL_EP`), e só quando `a.do_molde` não for vazio.

- [ ] **Passo 4: mostrar no mapa**

Em `telaMapa`, acrescentar à nota da premissa o texto
`"e sustentou a troca de superfície"` quando `n.generalizou`; uma linha na
legenda do `index.html`.

- [ ] **Passo 5: rodar a suíte e conferir na tela**

Roda: `python -m pytest mvp -q`, depois o servidor e uma sessão até o mapa.

- [ ] **Passo 6: sabotar** — gravar a assinatura sem os parâmetros (só o id
do molde) e conferir que `test_acertar_a_mesma_instancia...` cai.

- [ ] **Passo 7: commit**

---

### Tarefa 5: O formato do molde, lido e validado

**Arquivos:**
- Criar: `mvp/molde.py`
- Criar: `mvp/test_molde.py`

**Interfaces:**
- Produz:
  - `class MoldeInvalido(Exception)` com `.problemas: list[str]`, no mesmo
    molde de `DominioInvalido`
  - `@dataclass(frozen=True) class Molde` com `id, no, formato, nivel, uso,
    parametros: Mapping[str, tuple], enunciado, gabarito,
    distratores: tuple[tuple[str, str], ...], oraculo, espera, revisado_por`
  - `le(caminho: Path, d: Dominio) -> dict[str, Molde]`

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_le_um_molde_valido(tmp_path, d7)
def test_molde_sem_oraculo_nao_carrega(tmp_path, d7)          # é obrigatório
def test_buraco_que_nao_e_parametro_nao_carrega(tmp_path, d7) # Foco 1
def test_crenca_de_distrator_tem_de_existir(tmp_path, d7)
def test_formato_nivel_e_uso_tem_de_ser_dos_catalogos(tmp_path, d7)
def test_no_tem_de_ser_do_topico(tmp_path, d7)
```

A asserção de cada um: `MoldeInvalido` levantado e `any(<palavra> in p ...)`
com a palavra que identifica o defeito (`"oráculo"`, `"buraco"`, `"crença"`,
`"formato"`, `"nó"`).

O buraco: todo `{nome}` que aparecer em `enunciado`, `gabarito`, nos textos
dos distratores, no `oraculo` e no `espera` tem de estar em `parametros` ou
ser `extenso` (derivado de `n`). Qualquer outro é erro de validação.

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar `le` e a validação**

Os catálogos vêm de `mvp.dominio`: `FORMATOS`, `NIVEIS`, `TIPOS`, `USOS`. O
`d: Dominio` entra para conferir nó e crença contra o tópico.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** cada invariante, uma por vez, e conferir que o
teste dela cai.

- [ ] **Passo 6: commit**

---

### Tarefa 6: A expansão determinística

**Arquivos:**
- Modificar: `mvp/molde.py`
- Testar: `mvp/test_molde.py`

**Interfaces:**
- Produz: `expande(molde: Molde, quantas: int = 6) -> list[dict]` — os
  dicionários de parâmetros, com `extenso` já preenchido quando houver `n`.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_a_expansao_e_estavel(m):
    """Mesma entrada, mesma saída: o candidato tem de ser reprodutível."""
    assert expande(m, 6) == expande(m, 6)


def test_as_variacoes_sao_distantes(m):
    """Trocar de item tem de trocar de superfície."""
    saiu = expande(m, 6)
    assert all(_hamming(a, b) >= 2 for a, b in itertools.combinations(saiu, 2))


def test_menos_combinacoes_do_que_o_pedido(m_pequeno):   # Foco 2
    """Dois parâmetros de um valor só dão duas variações, não seis."""
    assert len(expande(m_pequeno, 6)) == 2


def test_extenso_acompanha_o_n(m):
    assert {p["extenso"] for p in expande(m, 6)} <= {"duas", "tres", "quatro",
                                                     "cinco", "seis", "sete",
                                                     "oito"}
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Guloso: começa pela combinação de índices mais baixos e, a cada passo,
acrescenta aquela cuja distância de Hamming mínima às já escolhidas é a
maior; empate pela ordem de escrita do YAML. Sem `random`.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — trocar o guloso por "as `quantas` primeiras
combinações" e conferir que `test_as_variacoes_sao_distantes` cai.

- [ ] **Passo 6: commit**

---

### Tarefa 7: O item expandido

**Arquivos:**
- Modificar: `mvp/molde.py`
- Testar: `mvp/test_molde.py`

**Interfaces:**
- Produz: `item_de(molde: Molde, parametros: dict, i: int) -> dict` — o
  dicionário no formato de `activities_*.yaml`, com as chaves em português
  (`id, node, nivel, formato, tipo, uso, enunciado, alternativas, gabarito,
  crencas, do_molde, parametros, gerado_por, revisado_por`).

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_o_item_sai_no_formato_do_dominio(m)
    # node == "kc07:B1" (prefixo sem underscore), gabarito == "a",
    # crencas aponta as letras dos distratores
def test_o_id_do_item_diz_o_molde_e_a_variacao(m)
    # id == "mol_kc07_B1_reconhecer_03"
def test_o_revisado_por_vem_do_molde(m)
    # molde revisado -> item sai com o mesmo nome; molde em branco -> ""
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

A ordem das alternativas é `a` = gabarito, depois os distratores na ordem do
molde. O `revisado_por` do item é **cópia do molde**: é assim que o
`gerar.py --aprovar` de hoje continua valendo sem saber o que é molde.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: commit**

---

### Tarefa 8: O oráculo

**Arquivos:**
- Criar: `scripts/oraculo.py`
- Criar: `mvp/test_oraculo.py`

**Interfaces:**
- Produz:
  - `GCC: Path` — lido de `STRUCTURA_GCC`, com
    `C:\Users\Public\gcc\mingw64\bin\gcc.exe` por omissão
  - `class SemCompilador(Exception)`
  - `roda(programa: str, espera: str, gcc: Path = GCC, timeout: int = 10) -> tuple[bool, str]`
    — **não** `confere`: `scripts/gerar.py` já tem uma `confere(topico,
    novas)`, que é o portão do contrato. Dois nomes iguais em portões
    vizinhos é defeito esperando acontecer.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_programa_que_imprime_o_esperado_passa()
def test_programa_que_imprime_outra_coisa_reprova()   # a nota diz os dois
def test_programa_que_nao_compila_reprova()           # a nota traz a 1a linha do gcc
def test_sem_compilador_a_mensagem_diz_onde_procurou() # Foco 3: SemCompilador
def test_programa_que_nao_termina_e_cortado()          # Foco 4: while(1), timeout
```

Os três primeiros e o quinto exigem gcc: marcar com
`@pytest.mark.skipif(not GCC.exists(), reason="sem compilador")`. O quarto
roda sempre, apontando `gcc` para um caminho que não existe.

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Pasta temporária, nomes relativos (`o.c`, `o.exe`), `cwd` na pasta,
`capture_output=True`. Comparar `stdout.strip()` com `espera`. `timeout`
estoura → reprovado, com a palavra `timeout` na nota.

- [ ] **Passo 4: rodar e ver passar**

Roda: `python -m pytest mvp/test_oraculo.py -v`
Espera: 5 passando; nenhum pulado nesta máquina.

- [ ] **Passo 5: sabotar** — tirar o `timeout` da chamada e conferir que
`test_programa_que_nao_termina_e_cortado` pendura (interromper e registrar).

- [ ] **Passo 6: commit**

---

### Tarefa 9: Os quatro portões no gerador

**Arquivos:**
- Modificar: `scripts/gerar.py` (`main`, ~402; `confere`, ~238)
- Testar: `mvp/test_gerador.py`

**Interfaces:**
- Consome: `mvp.molde.le/expande/item_de`, `scripts.oraculo.roda`.
- Produz: `expande_molde(d, topico, molde_id) -> tuple[list[dict], list[str]]`
  — os itens e os problemas; lista vazia de itens quando houver problema.
  CLI: `--molde <id> --expandir`.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_molde_certo_expande_e_passa_nos_quatro_portoes(tmp_path, monkeypatch)
def test_uma_variacao_reprovada_derruba_o_molde_inteiro(tmp_path, monkeypatch)
    """A regra da spec: o oráculo reprova o MOLDE, não a variação.
    Ficar com as que passaram é como se esconde uma generalização indevida."""
    itens, problemas = expande_molde(...)
    assert itens == []
    assert any("sizeof" in p or "variação" in p for p in problemas)
def test_o_portao_do_contrato_diz_qual_variacao_quebrou(tmp_path, monkeypatch):
    """Foco 5: o gabarito vira o texto mais longo em n=8."""
    itens, problemas = expande_molde(...)
    assert itens == []
    assert any("_08" in p and "mais longa" in p for p in problemas), problemas


def test_variacao_igual_a_item_que_ja_existe_e_recusada(tmp_path, monkeypatch):
    """O molde reproduz, palavra por palavra, um item escrito à mão."""
    itens, problemas = expande_molde(...)
    assert itens == []
    assert any("ciu_kc07_001" in p for p in problemas), problemas
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar os portões, nesta ordem**

1. expansão (`mvp.molde.expande`)
2. oráculo (`scripts.oraculo.roda` em cada variação) — qualquer reprovação
   derruba o molde, e a mensagem nomeia os parâmetros da variação
3. contrato (`confere(topico, itens)`, que já existe e usa o carregador de
   verdade) — a mensagem de erro nomeia o id da variação
4. variedade — nenhum enunciado repetido entre as variações nem igual a um
   item já presente em `activities_<topico>.yaml`

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — fazer o portão 2 descartar as variações
reprovadas em vez de derrubar o molde, e conferir que
`test_uma_variacao_reprovada_derruba_o_molde_inteiro` cai.

- [ ] **Passo 6: commit**

---

### Tarefa 10: A folha de revisão do molde

**Arquivos:**
- Modificar: `scripts/gerar.py` (`folha`, ~292)
- Testar: `mvp/test_gerador.py`

**Interfaces:**
- Consome: `mvp.molde.Molde`, `mvp.molde.expande`.
- Produz: `folha_do_molde(d, molde: Molde) -> str` — o markdown que a pessoa
  lê para preencher o `revisado_por`.

- [ ] **Passo 1: escrever o teste que falha**

```python
def test_a_folha_do_molde_mostra_o_texto_e_os_extremos(d7, m):
    """A máquina confere o C; o português é da pessoa, e ela o lê nos
    extremos do espaço de parâmetros, que é onde a concordância quebra."""
    texto = folha_do_molde(d7, m)
    assert "{tipo} {nome}[{n}]" in texto          # o molde, com os buracos
    assert texto.count("### variação") == 3       # nem 6, nem 150
    assert "n=3" in texto and "n=8" in texto      # o menor e o maior
    assert "revisado_por" in texto
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

As três variações são escolhidas, não sorteadas: a do menor `n`, a do maior
`n`, e a do nome mais longo. Quando não houver `n`, o primeiro parâmetro
numérico; não havendo nenhum, as três primeiras da expansão.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: commit**

---

### Tarefa 11: O molde escrito pelo modelo

**Arquivos:**
- Modificar: `scripts/gerar.py` (`prompt`, ~85; `esquema`, ~139; `main`)
- Testar: `mvp/test_gerador.py`

**Interfaces:**
- Produz: `esquema_de_molde(d) -> dict` e `prompt_de_molde(d, no, degrau) -> tuple[str, str]`;
  CLI `--molde --no B1 --degrau 1` (sem `--expandir`), e `--prompt` junto
  para escrever o pedido num arquivo em vez de chamar a API.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_o_esquema_de_molde_so_aceita_crenca_que_existe(d7):
    """A mesma coleira do gerador de itens: enum dos ids do catálogo."""
    enum = esquema_de_molde(d7)["properties"]["distratores"]["items"][
        "properties"]["crenca"]["enum"]
    assert set(enum) == set(d7.crencas)


def test_o_pedido_manda_escrever_o_oraculo(d7):
    sistema, pedido = prompt_de_molde(d7, "B1", 1)
    assert "oraculo" in (sistema + pedido) and "espera" in (sistema + pedido)
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

O esquema é o de `esquema(d)` com os campos do molde no lugar dos do item, e
o enum das crenças igual. O pedido acrescenta uma instrução que os itens não
têm: **o programa-oráculo e o que ele imprime**, e que o gabarito é regra,
não texto.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — tirar o enum do esquema e conferir que
`test_o_esquema_de_molde_so_aceita_crenca_que_existe` cai.

- [ ] **Passo 6: commit**

---

### Tarefa 12: O primeiro molde de verdade

**Arquivos:**
- Criar: `mvp/dominio/moldes_kc07.yaml`
- Modificar: `docs/moldes.md` (estado), `docs/processo.md` (seção do ciclo)
- Testar: `mvp/test_molde.py`

- [ ] **Passo 1: escrever o molde** para um nó de **treino** do kc_07,
seguindo o exemplo da spec, com `revisado_por` em branco.

- [ ] **Passo 2: rodar os portões de verdade**

Roda: `python scripts/gerar.py --topico kc_07 --molde <id> --expandir`
Espera: 6 variações, oráculo verde, contrato verde.

- [ ] **Passo 3: teste de contrato sobre os moldes que existem**

```python
@pytest.mark.parametrize("topico", topicos())
def test_todo_molde_do_disco_carrega(topico):
    """O mesmo que `test_a_lista_de_topicos_sai_dos_arquivos` faz com os
    tópicos: se alguém escrever um molde quebrado, cai aqui — não na hora
    de gerar."""
```

- [ ] **Passo 4: ler as três variações dos extremos** e preencher o
`revisado_por` (passo humano — **parar e pedir**).

- [ ] **Passo 5: aprovar e conferir a sessão**

Roda: `python scripts/gerar.py --topico kc_07 --aprovar`, depois
`bash scripts/verify.sh`, depois uma sessão no navegador até ver um item do
molde e o campo `do_molde` no log.

- [ ] **Passo 6: commit**

---

## Fora deste plano

- Caminhante com persona de crença.
- Escolha adaptativa do próximo item.
- Qualquer mudança no critério de domínio.
- Moldes para os outros 64 nós: este plano cobre o primeiro, e o segundo em
  diante é repetição do ciclo da Tarefa 10.
