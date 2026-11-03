# Família de formatos — plano de implementação

> **Para quem executa:** use `superpowers:subagent-driven-development` ou
> `superpowers:executing-plans` para implementar tarefa a tarefa. Os passos
> usam caixa (`- [ ]`) para marcação.

**Objetivo:** um molde deixa de ser uma pergunta com buracos e passa a ser
uma **afirmação** perguntada em vários formatos, para que multiplicar o
banco multiplique também o eixo da superfície.

**Arquitetura:** o bloco compartilhado do molde (nó, parâmetros, crenças,
oráculo) ganha um mapa `formatos:`, e cada formato traz a redação e, quando
precisa, o seu próprio oráculo. Nada disso chega à sessão: a expansão
continua offline e o que entra em `activities_*.yaml` é item de YAML como
sempre. Molde sem `formatos:` continua valendo como família de um.

**Stack:** Python 3.14, PyYAML, pytest, gcc (MinGW-W64) 16.2.0 em
`C:\Users\Public\gcc`.

**Spec:** [docs/moldes.md](moldes.md), seção *A família de formatos*.

## Restrições globais

- O caminho do gcc não pode ter espaço (`C:\Users\Public\gcc`); tudo roda
  em pasta temporária, com caminhos relativos e `cwd` na pasta, e todo
  programa do oráculo com `timeout=10`.
- **Compatibilidade:** `mol_kc07_B1_treino_1` está assinado e os seis itens
  dele estão no domínio. Nenhuma tarefa pode exigir reescrita dele nem
  invalidar a assinatura — molde sem `formatos:` é família de um.
- O critério de domínio não muda, e o motor não aprende o que é molde.
- Disciplina da casa: cada regra nova tem uma sabotagem que derruba o teste
  dela; o comentário diz POR QUE a regra existe; nunca enfraquecer teste
  para ficar verde. **Teste de regra não se amarra a conteúdo que tem o
  direito de mudar** — isto já custou quatro consertos neste projeto.
- Mensagem de commit em português, sem acento, no estilo das que existem.

## Foco da revisão

Cinco entradas que a spec implica e que nenhuma tarefa exercita por acaso.
Cada uma tem o teste indicado na tarefa dona.

1. **Família com um formato só** — tem de se comportar exatamente como o
   molde de hoje, inclusive no id dos itens e na assinatura. — Tarefa 1.
2. **Distratores em número diferente do de `crencas`** num dos formatos: a
   correspondência posicional quebra em silêncio se ninguém cobrar. —
   Tarefa 2.
3. **`nao_compila: true` num programa que COMPILA** — o item não tem erro
   para achar, e o oráculo tem de reprovar em vez de aprovar. — Tarefa 4.
4. **`gabarito: do_oraculo` num formato que não é `prever_saida`**, ou um
   oráculo cuja saída não serve como alternativa (vazia, ou com quebra de
   linha). — Tarefa 5.
5. **`quantas` menor que o número de formatos** (três formatos, duas
   variações pedidas): alguém fica sem nenhuma, e isso tem de ser decidido,
   não sorteado. — Tarefa 6.

---

### Tarefa 1: O molde lê a família

**Arquivos:**
- Modificar: `mvp/molde.py` (`Molde`, `le`)
- Testar: `mvp/test_molde.py`

**Interfaces:**
- Produz: `@dataclass(frozen=True) class Redacao` com
  `formato, tipo, enunciado, codigo, gabarito, distratores: tuple[str, ...],
  oraculo, espera, nao_compila: bool`
- Produz: `Molde.redacoes: tuple[Redacao, ...]` e `Molde.crencas: tuple[str, ...]`
- Mantém: `le(caminho, d) -> dict[str, Molde]`, mesma assinatura.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_familia_de_tres_formatos_carrega(tmp_path, d7):
    m = _le_familia(tmp_path, "f1")["mol_teste"]
    assert [r.formato for r in m.redacoes] == [
        "reconhecer_conceito", "achar_o_erro", "prever_saida"]
    assert m.crencas == ("string_literal_is_array", "array_is_pointer")


def test_molde_sem_formatos_e_familia_de_um(tmp_path, d7):
    """Foco 1: o que está no domínio hoje não pode precisar de reescrita."""
    m = _le(tmp_path, d7, "velho")["mol_teste"]
    assert len(m.redacoes) == 1
    assert m.redacoes[0].formato == m.formato
    assert m.redacoes[0].enunciado == m.enunciado


def test_o_molde_de_verdade_continua_assinado():
    """O mol_kc07_B1_treino_1 está assinado e no domínio: a assinatura
    dele não pode mudar por causa desta fatia."""
    d = carrega(topico="kc_07")
    m = le(RAIZ_DOMINIO / "moldes_kc07.yaml", d)["mol_kc07_B1_treino_1"]
    assert m.revisado is True


def test_formato_repetido_na_familia_nao_carrega(tmp_path, d7):
    """Dois `achar_o_erro` no mesmo molde não são duas superfícies."""
    p = _recusa_familia(tmp_path, d7, "c0", repete="achar_o_erro")
    assert any("achar_o_erro" in x and "duas vezes" in x for x in p), p


def test_familia_sem_crencas_nao_carrega(tmp_path, d7):
    p = _recusa_familia(tmp_path, d7, "c0b", crencas=[])
    assert any("sem crença" in x for x in p), p
```

- [ ] **Passo 2: rodar e ver falhar**

Roda: `python -m pytest mvp/test_molde.py -k familia -v`

- [ ] **Passo 3: implementar**

`le` passa a aceitar as duas formas. Sem `formatos:`, monta uma `Redacao`
com os campos de topo e `crencas` derivadas dos distratores, **nesta
ordem**, para a família de um ser idêntica ao molde de hoje. Com
`formatos:`, os campos de topo que sobrarem (`oraculo`, `espera`) são o
padrão de cada redação.

A `assinatura` continua sendo do dicionário cru menos os dois campos de
revisão — então o molde que já está assinado não muda de digest.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — fazer a família de um perder o `formato` do
topo e conferir que `test_molde_sem_formatos_e_familia_de_um` cai.

- [ ] **Passo 6: commit**

---

### Tarefa 2: As crenças são da afirmação

**Arquivos:**
- Modificar: `mvp/molde.py` (validação em `le`)
- Testar: `mvp/test_molde.py`

**Interfaces:**
- Consome: `Molde.crencas`, `Redacao.distratores` (Tarefa 1).

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_cada_formato_tem_um_distrator_por_crenca(tmp_path, d7):
    """Foco 2: a correspondência é POSICIONAL, e quebra em silêncio.

    Se um formato trouxesse dois distratores e outro três, as crenças
    deixariam de ser as mesmas — e aí os dois formatos não são duas
    superfícies da mesma afirmação, são duas perguntas.
    """
    p = _recusa_familia(tmp_path, d7, "c1", formato_com_menos="achar_o_erro")
    assert any("achar_o_erro" in x and "2 crença" in x for x in p), p


def test_crenca_da_familia_tem_de_existir(tmp_path, d7):
    p = _recusa_familia(tmp_path, d7, "c2", crencas=["nao_existe"])
    assert any("nao_existe" in x for x in p), p


def test_a_familia_precisa_da_crenca_do_proprio_no(tmp_path, d7):
    """A regra do contrato, cobrada UMA vez na família em vez de uma por
    redação: sem ela o nó nunca recebe atribuição."""
    p = _recusa_familia(tmp_path, d7, "c3", crencas=["array_is_pointer"])
    assert any("próprio nó" in x for x in p), p
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Em `le`: `crencas` existe, todos os ids estão no catálogo do tópico, pelo
menos um nega o nó do molde, e **cada redação tem exatamente
`len(crencas)` distratores**.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** cada uma das três e conferir que cai a sua.

- [ ] **Passo 6: commit**

---

### Tarefa 3: O item sai de uma redação

**Arquivos:**
- Modificar: `mvp/molde.py` (`item_de`)
- Testar: `mvp/test_molde.py`

**Interfaces:**
- Produz: `item_de(molde: Molde, redacao: Redacao, parametros: dict, i: int) -> dict`
  — **muda a assinatura**: ganha a redação como segundo argumento.
- O id passa a ser `"%s__%s_%02d" % (molde.id, redacao.formato, i)`; o
  `do_molde` continua sendo o da **família**.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_o_id_do_item_diz_a_familia_e_o_formato(m):
    it = item_de(m, m.redacoes[1], expande(m, 6)[0], 2)
    assert it["id"] == "mol_teste__achar_o_erro_02"
    assert it["do_molde"] == "mol_teste"     # a FAMÍLIA, não a redação


def test_as_crencas_do_item_saem_da_familia(m):
    it = item_de(m, m.redacoes[0], expande(m, 6)[0], 1)
    assert list(it["crencas"].values()) == list(m.crencas)


def test_o_codigo_da_redacao_vai_para_o_item(m):
    it = item_de(m, m.redacoes[1], expande(m, 6)[0], 1)
    assert "{" not in it["codigo"] and it["codigo"].strip()
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Os chamadores de hoje (`expande_molde`, `folha_do_molde`) passam
`m.redacoes[0]` enquanto a Tarefa 6 não os atualiza — a mudança de
assinatura é a razão de esta tarefa vir antes.

- [ ] **Passo 4: rodar a suíte inteira**

Roda: `python -m pytest mvp -q`
Espera: verde. Os seis itens do molde que está no domínio **não** mudam de
id: eles já estão em `activities_kc07.yaml`, e nada os reexpande.

- [ ] **Passo 5: commit**

---

### Tarefa 4: O oráculo que espera a recusa

**Arquivos:**
- Modificar: `scripts/oraculo.py`
- Testar: `mvp/test_oraculo.py`

**Interfaces:**
- Produz: `roda(programa, espera, gcc=None, timeout=TEMPO, nao_compila=False)`
  — quando `nao_compila`, passa se o compilador recusar **com diagnóstico**
  e reprova se compilar; `espera` é ignorado.

- [ ] **Passo 1: escrever os testes que falham**

```python
@tem_gcc
def test_nao_compila_passa_quando_o_compilador_recusa():
    ok, nota = oraculo.roda("int main(void){int a[5];int *p;a=p;return 0;}",
                            "", nao_compila=True)
    assert ok
    assert "error:" in nota          # a nota traz a fala do compilador


@tem_gcc
def test_nao_compila_reprova_quando_o_programa_compila():
    """Foco 3: um "ache o erro" num programa que compila é item sem erro."""
    ok, nota = oraculo.roda("int main(void){return 0;}", "", nao_compila=True)
    assert not ok
    assert "compilou" in nota
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — fazer `nao_compila` aceitar qualquer resultado
e conferir que o segundo teste cai.

- [ ] **Passo 6: commit**

---

### Tarefa 5: O gabarito que sai do oráculo

**Arquivos:**
- Modificar: `mvp/molde.py` (validação), `scripts/gerar.py` (`expande_molde`)
- Testar: `mvp/test_molde.py`, `mvp/test_gerador.py`

**Interfaces:**
- `Redacao.gabarito == "do_oraculo"` é marcador, não texto: a expansão
  substitui pelo que o programa imprimiu.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_do_oraculo_so_vale_em_prever_saida(tmp_path, d7):
    """Foco 4."""
    p = _recusa_familia(tmp_path, d7, "g1",
                        gabarito_do_oraculo_em="reconhecer_conceito")
    assert any("do_oraculo" in x and "prever_saida" in x for x in p), p


def test_prever_saida_sozinho_continua_recusado(tmp_path, d7):
    """Fora da família, gabarito e espera são campos independentes."""
    p = _recusa(tmp_path, d7, "g2", formato="prever_saida")
    assert any("prever_saida" in x for x in p), p


@tem_gcc
def test_o_gabarito_do_prever_saida_vem_do_programa(tmp_path):
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste",
                                           raiz=_familia(tmp_path, "g3"))
    assert problemas == []
    prev = [i for i in itens if i["formato"] == "prever_saida"]
    assert prev and prev[0]["alternativas"]["a"] == "3"   # sizeof a / sizeof a[0]


@tem_gcc
def test_saida_que_nao_serve_de_alternativa_reprova(tmp_path):
    """Foco 4: saída vazia, ou com quebra de linha, não é alternativa."""
    itens, problemas = gerar.expande_molde(
        D7, "kc_07", "mol_teste", raiz=_familia(tmp_path, "g4", saida_feia=True))
    assert itens == []
    assert any("não serve como alternativa" in x for x in problemas), problemas
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Na carga: `do_oraculo` só em `prever_saida`, e `prever_saida` sem ele
continua recusado. Na expansão: depois do oráculo passar, a saída vira a
alternativa certa; saída vazia, com quebra de linha, ou maior que a maior
alternativa errada reprova o molde.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** as duas regras, uma por vez.

- [ ] **Passo 6: commit**

---

### Tarefa 6: A expansão se reparte entre os formatos

**Arquivos:**
- Modificar: `mvp/molde.py` (`expande`), `scripts/gerar.py` (`expande_molde`)
- Testar: `mvp/test_molde.py`, `mvp/test_gerador.py`

**Interfaces:**
- Produz: `expande_familia(molde: Molde, quantas: int = 6) -> list[tuple[Redacao, dict]]`
  — as variações já casadas com a redação de cada uma.

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_a_expansao_se_reparte_entre_os_formatos(m):
    pares = expande_familia(m, 6)
    assert len(pares) == 6
    assert collections.Counter(r.formato for r, _ in pares) == {
        "reconhecer_conceito": 2, "achar_o_erro": 2, "prever_saida": 2}


def test_a_primeira_variacao_e_a_mesma_em_todos_os_formatos(m):
    """É isso que torna a troca de formato a única coisa que mudou."""
    pares = expande_familia(m, 6)
    por_formato = collections.defaultdict(list)
    for r, p in pares:
        por_formato[r.formato].append(p)
    assert len({tuple(sorted(v[0].items())) for v in por_formato.values()}) == 1


def test_menos_variacoes_do_que_formatos(m):
    """Foco 5: três formatos, duas variações — a ordem do YAML decide,
    e nenhum formato recebe duas antes de todos terem uma."""
    pares = expande_familia(m, 2)
    assert [r.formato for r, _ in pares] == [
        "reconhecer_conceito", "achar_o_erro"]
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Rodízio: a primeira volta dá uma variação a cada formato, **a mesma**; as
voltas seguintes seguem a escolha gulosa de sempre, por formato, a partir
do que aquele formato já usou.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — dar todas as variações ao primeiro formato e
conferir que `test_a_expansao_se_reparte_entre_os_formatos` cai.

- [ ] **Passo 6: commit**

---

### Tarefa 7: Os portões, por redação

**Arquivos:**
- Modificar: `scripts/gerar.py` (`expande_molde`)
- Testar: `mvp/test_gerador.py`

**Interfaces:**
- Consome: `expande_familia` (Tarefa 6), `roda(..., nao_compila=)` (Tarefa 4).

- [ ] **Passo 1: escrever os testes que falham**

```python
@tem_gcc
def test_a_familia_inteira_passa_nos_quatro_portoes(tmp_path):
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste",
                                           raiz=_familia(tmp_path, "ok"))
    assert problemas == []
    assert len({i["formato"] for i in itens}) == 3


@tem_gcc
def test_uma_redacao_reprovada_derruba_a_familia(tmp_path):
    """A mesma regra da fatia anterior, um nível acima: ficar com os
    formatos que passaram esconde a afirmação errada."""
    itens, problemas = gerar.expande_molde(
        D7, "kc_07", "mol_teste", raiz=_familia(tmp_path, "ruim", quebra="achar_o_erro"))
    assert itens == []
    assert any("achar_o_erro" in p for p in problemas), problemas
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Cada par (redação, parâmetros) roda o oráculo **daquela redação** — o da
família quando ela não tiver o seu —, e as regras de contrato, buraco e
minúscula valem item a item como já valem.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — descartar a redação reprovada e seguir com as
outras; o segundo teste cai.

- [ ] **Passo 6: commit**

---

### Tarefa 8: A folha da família

**Arquivos:**
- Modificar: `scripts/gerar.py` (`folha_do_molde`, `extremos`)
- Testar: `mvp/test_gerador.py`

- [ ] **Passo 1: escrever o teste que falha**

```python
def test_a_folha_mostra_os_extremos_de_um_formato_e_um_de_cada_outro(tmp_path):
    m = _le_familia_molde(tmp_path, "folha")
    texto = gerar.folha_do_molde(D7, m)
    assert texto.count("### variação") == 5        # 3 + 1 + 1
    assert texto.count("## formato") == 3
    assert "revisado_sha: %s" % m.digest in texto
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Três extremos do primeiro formato, uma variação de cada um dos outros, e a
afirmação e as crenças impressas **uma vez** no topo — é o que a pessoa
está validando.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: commit**

---

### Tarefa 9: O prompt pede a família

**Arquivos:**
- Modificar: `scripts/gerar.py` (`esquema_de_molde`, `prompt_de_molde`)
- Testar: `mvp/test_gerador.py`

- [ ] **Passo 1: escrever os testes que falham**

```python
def test_o_esquema_pede_um_mapa_de_formatos():
    e = gerar.esquema_de_molde(D7)
    assert "formatos" in e["required"]
    assert "crencas" in e["required"]


def test_o_pedido_explica_a_correspondencia_posicional():
    sistema, pedido = gerar.prompt_de_molde(D7, "B1", 1)
    assert "mesma ordem" in (sistema + pedido).lower()
```

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

O esquema ganha `crencas` (enum, como já é) e `formatos`; o pedido explica
que os distratores vão **na ordem das crenças**, que o gabarito tem de sair
certo em toda combinação, e que `achar_o_erro` precisa de um programa que
não compile.

- [ ] **Passo 4: rodar e ver passar**

- [ ] **Passo 5: sabotar** — tirar `crencas` do `required`; o primeiro cai.

- [ ] **Passo 6: commit**

---

### Tarefa 10: A primeira família de verdade

**Arquivos:**
- Modificar: `mvp/dominio/moldes_kc07.yaml`, `docs/moldes.md`, `docs/processo.md`
- Testar: `mvp/test_molde.py`

- [ ] **Passo 1: escrever a família** para o `B1` do kc_07, com três
formatos — `reconhecer_conceito`, `achar_o_erro`, `prever_saida` — e
`revisado_por`/`revisado_sha` em branco.

**Decisão a tomar e registrar:** o `mol_kc07_B1_treino_1` que já está no
domínio vira o primeiro formato desta família, ou a família nasce com outro
id e os dois convivem? Os seis itens antigos continuam válidos nos dois
caminhos; o que muda é se o banco do `B1` fica com 9 ou com 15 itens.

- [ ] **Passo 2: rodar os portões de verdade**

Roda: `python scripts/gerar.py --topico kc_07 --molde <id> --expandir`
Espera: 6 variações, dois por formato, oráculo verde nos três.

- [ ] **Passo 3: ler a folha e preencher o `revisado_por`** — passo humano,
**parar e pedir**.

- [ ] **Passo 4: aprovar e conferir na sessão**

Roda: `--aprovar`, depois `bash scripts/verify.sh`, depois uma sessão no
navegador até ver dois formatos do mesmo molde no treino do mesmo nó.

- [ ] **Passo 5: medir o que a fatia prometia**

O banco de treino do `B1`, por formato, antes e depois. O número que
motivou a fatia era 7–1–1.

- [ ] **Passo 6: docs e commit**

---

## Fora deste plano

- Os formatos **autocompletar** e **apontar a linha**: entram como conteúdo
  dentro desta estrutura, depois dela existir.
- **Ordenar os passos** e **marcar as caixas da memória**: pedem tela nova.
- **Prever a saída digitando**: fora por decisão, não por custo.
- O fecho visível da premissa, e qualquer mudança no critério de domínio.
