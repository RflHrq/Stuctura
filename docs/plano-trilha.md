# A trilha, fatia 1 — o kc_00 inteiro no formato novo: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Servir o tópico kc_00 (declaração de variáveis) pela trilha — sequência de premissas, pergunta primeiro, escada passo a passo, prova da máquina, reconferência e mapa —, com o conteúdo novo das cinco premissas, sem tocar no fluxo atual.

**Architecture:** Um motor novo e puro (`mvp/trilha.py`) ao lado do atual, com o mesmo contrato — estado e entrada entram, estado, tela e eventos saem. O conteúdo passo a passo mora num arquivo novo por tópico (`mvp/dominio/escada_kc00.yaml`), lido e corrigido por `mvp/trilha_escada.py` e conferido pelo compilador fora da sessão. Um app-fábrica (`mvp/trilha_app.py`) é montado pelo portal em `/trilha/kc_00/`, com telas próprias.

**Tech Stack:** Python 3.14.7, FastAPI 0.141.1, PyYAML 6.0.3, pydantic 2.13.5, pytest; JavaScript sem dependência; gcc (MinGW-W64 16.2.0) só fora da sessão, via `scripts/oraculo.py`.

**Spec:** [docs/trilha.md](trilha.md) — aprovada pelo Rafael em 13/11/2026. Este plano cobre o item 1 da seção 9.

## Global Constraints

- `mvp/motor.py`, `mvp/app.py` e **todo** `mvp/test_*.py` que existe hoje não mudam. Nenhum teste existente é apagado, pulado, enfraquecido ou alterado para ficar verde: se um falhar, **parar e avisar o Rafael**.
- A suíte de hoje dá `2334 passed, 8 skipped`. Ela pede a porta 8010 livre (contêiner `structura-portal` parado: `docker compose down`) e nada competindo por CPU — gcc, servidor ou navegador rodando junto dão falha falsa.
- O motor da trilha é puro: não toca disco, não sorteia, não consulta relógio.
- Todo texto de conteúdo na tela vem do domínio ou da escada. O cliente só escreve frases fixas de ligação.
- A regra de exibição dos programas não é copiada: a trilha chama `motor._prova`. Só `mvp/conceitos.py` lê `prerequisites`.
- Sessão simulada nunca vai para `coleta/`: testes usam `tmp_path`; ensaio manual usa `ensaios/`.
- Nada em `mvp/` importa de `scripts/` (a imagem Docker não leva `scripts/`).
- YAML: nunca uma chave chamada `no` (vira `False`). A chave da premissa é o próprio id (`B1:`).
- Arquivo com `\n` dentro de string se escreve com a ferramenta de escrita, nunca com heredoc de Python no Bash.
- Nenhum programa mostrado como executado lê variável sem valor. Código que faria isso aparece sem saída, e o conferidor só o compila (`-fsyntax-only`), nunca o roda.
- Números da spec: teto de **8** telas por premissa (a subida da escada conta como uma; `retorno` não conta); escada com **3 a 7** degraus, **2** ou mais de prática; **2** versões ou mais por degrau; degrau guiado com **1 ou 2** frases de até **30** palavras; treino fecha com **2** certas seguidas em no máximo **3** perguntas; **um** trabalho por premissa; ritmo padrão `completo`.
- Assets da página nova com `?v=20261113`.
- Ramo `trilha`. Commit com `git -c user.name="Rafael H. S. Simao" -c user.email="15497616+RflHrq@users.noreply.github.com" commit`, mensagem terminando em `Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>`. Sem push: não há remoto.
- Fora desta fatia: os outros doze tópicos, retomada por reexecução do registro, progresso na página inicial, previsão escrita, porquê por questão, a chave do pesquisador para as frases escritas, moldes, Praticar.

## Review Focus

1. **A mesma resposta enviada duas vezes** (duplo clique): a segunda não cabe na tela atual; a pessoa espera que nada mude. Teste na Task 4 (`EntradaInvalida`) e na Task 8 (400, nada gravado).
2. **Sessão que o servidor não conhece mais** (reinício com a página aberta): a pessoa espera uma mensagem e um botão de recomeçar, não tela em branco. Teste na Task 8 (404) e conferência no navegador na Task 9.
3. **Resposta de montar com peça repetida ou índice fora da faixa**: é pedido malformado, não resposta errada. Teste na Task 1 (`RespostaInvalida`) e na Task 8 (400).
4. **Valor digitado com espaço nas pontas** (`" 21 "`): a pessoa espera acertar. Teste na Task 1.
5. **Trocar modo ou ritmo no meio de uma pergunta**: a pergunta na tela não muda; a troca vale na premissa seguinte. Teste na Task 5.

---

## Estrutura de arquivos

| arquivo | responsabilidade |
| --- | --- |
| `mvp/trilha_escada.py` (novo) | O modelo da escada, a leitura com validação, e a correção de uma resposta produzida. Puro. |
| `mvp/dominio/escada_kc00.yaml` (novo) | O conteúdo: a escada das cinco premissas do kc_00. |
| `scripts/confere_escada.py` (novo) | O compilador como juiz do conteúdo, e o texto corrido para o Rafael ler. |
| `mvp/trilha.py` (novo) | O motor: sequência, classificação, os quatro caminhos, reconferência, mapa. Puro. |
| `scripts/trilha_alunos.py` (novo) | Alunos simulados, para os testes e para a medida. |
| `mvp/trilha_log.py` (novo) | O registro da trilha: uma linha por entrada e por evento. |
| `mvp/trilha_app.py` (novo) | As rotas, numa fábrica `cria_app`. |
| `mvp/web/trilha.html`, `trilha.js`, `trilha.css` (novos) | As telas. |
| `mvp/portal.py`, `mvp/web/portal.html` (modificados) | O portal monta a trilha e a página inicial a abre. |
| `mvp/test_trilha_*.py`, `mvp/test_trilha.py` (novos) | Os testes de cada peça. |

---

### Task 1: A escada — modelo, leitura e correção

**Files:**
- Create: `mvp/trilha_escada.py`
- Test: `mvp/test_trilha_escada.py`

**Interfaces:**
- Consumes: `mvp.dominio.Dominio` (`.nos`, `.crencas`).
- Produces:

```python
FORMAS = ("tocar", "montar", "escolher", "completar", "digitar")
MIN_DEGRAUS, MAX_DEGRAUS, MIN_PRATICA, MIN_VERSOES = 3, 7, 2, 2
MAX_FRASES, MAX_PALAVRAS = 2, 30
LACUNA = "___"

class EscadaInvalida(Exception): problemas: list[str]
class RespostaInvalida(ValueError): ...

@dataclass(frozen=True)
class Erro:
    retorno: str
    exata: tuple[int, ...] = ()   # a resposta, em índices do ARQUIVO
    sem: tuple[int, ...] = ()     # montar: qualquer sequência que não use estas peças
    texto: str = ""               # digitar
    invalida: bool = False        # a linha formada não compila
    crenca: str = ""              # id de crença do tópico

@dataclass(frozen=True)
class Versao:
    pede: str
    mostra: str = ""              # em `completar`, contém LACUNA uma vez
    antes: str = ""               # linhas de C que vêm antes
    pecas: tuple[str, ...] = ()
    certa: tuple[tuple[int, ...], ...] = ()   # sequências aceitas
    aceitas: tuple[str, ...] = () # digitar
    certa_texto: str = ""
    invalidas: tuple[int, ...] = ()  # escolher: opções que não compilam
    programa: str = ""            # digitar: o programa cuja saída é a resposta
    erros: tuple[Erro, ...] = ()
    retorno_geral: str = ""

@dataclass(frozen=True)
class Degrau:
    id: str; guiado: bool; forma: str; codigo: bool
    frases: tuple[str, ...]; versoes: tuple[Versao, ...]

@dataclass(frozen=True)
class Revisao:
    frases: tuple[str, ...]; codigo: str; saida: str = ""   # saida vazia: não se executa

@dataclass(frozen=True)
class Escada:
    premissa: str; degraus: tuple[Degrau, ...]; revisao: Revisao
    @property
    def pratica(self) -> tuple[Degrau, ...]: ...
    @property
    def guiados(self) -> tuple[Degrau, ...]: ...

@dataclass(frozen=True)
class Correcao:
    certa: bool; retorno: str = ""; mostra_certa: str = ""; crenca: str = ""

def le(caminho: Path, d: Dominio) -> dict[str, Escada]
def faltando(d: Dominio, escadas: Mapping[str, Escada]) -> tuple[str, ...]
def ordem_das_pecas(semente: str, degrau: str, versao: int, forma: str, n: int) -> tuple[int, ...]
def corrige(v: Versao, forma: str, pecas: tuple[int, ...] = (), texto: str = "") -> Correcao
```

Formato do YAML (o mesmo que a Task 3 escreve):

```yaml
B1:
  revisao:
    frases: ["…"]
    codigo: |
      int idade;
    saida: ""
  degraus:
    - id: esc_kc00_B1_2
      guiado: true
      forma: montar
      codigo: true
      frases: ["Agora você.", "Declare uma variável inteira chamada nota."]
      versoes:
        - pede: "Monte a linha com as peças."
          pecas: ["int", "nota", ";", "="]
          certa: [[0, 1, 2]]
          certa_texto: "int nota;"
          erros:
            - exata: [1, 0, 2]
              invalida: true
              retorno: "Em C o tipo vem primeiro, depois o nome: int nota;"
            - sem: [2]
              invalida: true
              retorno: "Toda declaração termina com ;"
          retorno_geral: "A declaração é o tipo, o nome e o ponto e vírgula: int nota;"
        - …segunda versão, outros valores…
```

- `tocar`, `escolher`, `completar`: a resposta é **uma** peça; `certa` é `[[i]]`.
- `corrige` recebe `pecas` em índices do **arquivo** (quem desfaz a ordem da tela é o motor). Primeiro erro que casar vence; nenhum casando, `retorno_geral`.
- `digitar` compara `texto.strip()` com cada item de `aceitas`.
- `ordem_das_pecas`: permutação estável por SHA-256 de `semente|pecas|degrau|versao`; em `tocar` e `completar` com `mostra`, e em `digitar`, é a identidade.

- [ ] **Step 1: Escrever os testes que falham** em `mvp/test_trilha_escada.py`. Um auxiliar `_escreve(tmp_path, dados)` grava um YAML e devolve o caminho; `_valida()` devolve o dicionário de uma escada válida de `B1` com três degraus (um guiado `montar`, dois de prática `escolher` e `digitar`).

```python
D = carrega(topico="kc_00")

def test_uma_escada_valida_carrega(tmp_path):
    e = trilha_escada.le(_escreve(tmp_path, {"B1": _valida()}), D)["B1"]
    assert [g.forma for g in e.degraus] == ["montar", "escolher", "digitar"]
    assert len(e.guiados) == 1 and len(e.pratica) == 2

@pytest.mark.parametrize("estraga, diz", [
    (lambda b: b["degraus"].__delitem__(slice(1, None)), "ao menos 3 degraus"),
    (lambda b: b["degraus"].extend([b["degraus"][1]] * 5), "no máximo 7 degraus"),
    (lambda b: b["degraus"][0]["versoes"].pop(), "ao menos 2 versões"),
    (lambda b: b["degraus"][0]["frases"].extend(["a", "b"]), "no máximo 2 frases"),
    (lambda b: b["degraus"][0]["frases"].__setitem__(0, "palavra " * 31), "30 palavras"),
    (lambda b: b["degraus"][1].__setitem__("guiado", True) or
               b["degraus"][0].__setitem__("guiado", False), "guiado depois de prática"),
    (lambda b: b["degraus"][1].__setitem__("frases", ["x"]), "degrau de prática não tem frase"),
    (lambda b: b["degraus"][0].__setitem__("forma", "arrastar"), "forma desconhecida"),
    (lambda b: b["degraus"][0]["versoes"][0].__setitem__("certa", [[9]]), "peça fora da faixa"),
    (lambda b: b["degraus"][0]["versoes"][0]["erros"][0].__setitem__("exata", [0, 1, 2]),
     "erro previsto é uma resposta aceita"),
    (lambda b: b["degraus"][0]["versoes"][0]["erros"][0].__setitem__("crenca", "nao_existe"),
     "crença desconhecida"),
    (lambda b: b["degraus"][0]["versoes"][0].__setitem__("certa_texto", ""), "sem certa_texto"),
])
def test_a_leitura_recusa_e_diz_por_que(tmp_path, estraga, diz):
    b = _valida(); estraga(b)
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        trilha_escada.le(_escreve(tmp_path, {"B1": b}), D)
    assert any(diz in p for p in erro.value.problemas)

def test_premissa_que_o_topico_nao_tem_e_recusada(tmp_path): ...   # {"Z9": _valida()} -> "premissa desconhecida"
def test_id_de_degrau_repetido_e_recusado(tmp_path): ...
def test_completar_pede_a_lacuna_uma_vez(tmp_path): ...            # mostra sem "___" -> problema
def test_faltando_lista_as_premissas_sem_escada(tmp_path):
    escadas = trilha_escada.le(_escreve(tmp_path, {"B1": _valida()}), D)
    assert trilha_escada.faltando(D, escadas) == ("B2", "B3", "B4", "I1")

def test_montar_certo():        # corrige(v, "montar", pecas=(0, 1, 2)).certa is True
def test_montar_erro_exato():   # (1, 0, 2) -> retorno "Em C o tipo vem primeiro…", mostra_certa "int nota;"
def test_montar_erro_por_falta_de_peca():   # (0, 1) -> "Toda declaração termina com ;"
def test_montar_erro_nao_previsto_cai_no_retorno_geral():   # (0, 3, 1, 2)
def test_peca_repetida_ou_fora_da_faixa_e_pedido_invalido():
    for ruim in ((0, 0, 2), (0, 1, 7), (-1,)):
        with pytest.raises(trilha_escada.RespostaInvalida):
            trilha_escada.corrige(V, "montar", pecas=ruim)
def test_tocar_com_duas_pecas_e_pedido_invalido(): ...
def test_digitar_ignora_espaco_nas_pontas():   # texto=" 21 " com aceitas ("21",) -> certa
def test_digitar_errado_previsto_traz_o_retorno_e_a_crenca(): ...
def test_a_ordem_das_pecas_e_estavel_e_e_permutacao():
    a = trilha_escada.ordem_das_pecas("s1", "esc_kc00_B1_2", 0, "montar", 4)
    assert a == trilha_escada.ordem_das_pecas("s1", "esc_kc00_B1_2", 0, "montar", 4)
    assert sorted(a) == [0, 1, 2, 3]
def test_tocar_nao_embaralha():   # ordem_das_pecas(..., "tocar", 3) == (0, 1, 2)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest mvp/test_trilha_escada.py -q`
Expected: erro de coleta, `No module named 'mvp.trilha_escada'`.

- [ ] **Step 3: Implementar `mvp/trilha_escada.py`** com as assinaturas acima. `le` junta **todos** os problemas antes de levantar `EscadaInvalida`, como o carregador do domínio faz; as mensagens trazem os trechos que o teste procura.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest mvp/test_trilha_escada.py -q`
Expected: todos passam.

- [ ] **Step 5: Commit** — `mvp/trilha_escada.py`, `mvp/test_trilha_escada.py`.

---

### Task 2: O compilador como juiz da escada

**Files:**
- Create: `scripts/confere_escada.py`
- Test: `mvp/test_trilha_oraculo.py`

**Interfaces:**
- Consumes: `trilha_escada.le`, `Escada`, `Degrau`, `Versao`; `scripts/oraculo.py` (`GCC`, `roda(programa, espera) -> (bool, str)`, `SemCompilador`).
- Produces:

```python
def programa_de(antes: str, linhas: str) -> str      # "#include <stdio.h>\nint main(void) {\n…\nreturn 0;\n}\n"
def compila(programa: str) -> tuple[bool, str]       # gcc -std=c17 -Wall -fsyntax-only; NUNCA executa
def linha_de(v: Versao, sequencia: tuple[int, ...]) -> str   # peças unidas por espaço; em `completar`, a peça no lugar da lacuna
def confere(escadas: Mapping[str, Escada]) -> list[str]      # problemas; lista vazia = passou
def leitura(d: Dominio, escadas: Mapping[str, Escada]) -> str  # Markdown para leitura humana
# CLI: python scripts/confere_escada.py kc_00 [--leitura]   (sai com 1 se houver problema)
```

O que `confere` exige, por degrau com `codigo: true`:

| forma | exigência |
| --- | --- |
| `montar` | toda sequência de `certa` compila (com `antes`); todo erro `invalida` com `exata` **não** compila |
| `escolher` | toda opção em `invalidas` não compila; as outras compilam |
| `completar` | a `mostra` com a peça certa compila; com a peça de um erro `invalida`, não |
| `tocar` | a `mostra` compila |
| `digitar` | `oraculo.roda(v.programa, v.aceitas[0])` passa (aqui o programa roda) |

E a `revisao`: com `saida`, `oraculo.roda(programa_de("", codigo), saida)` passa; sem `saida`, só `compila`.

- [ ] **Step 1: Escrever os testes que falham.** Marcador `tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(), …)`, como em `mvp/test_oraculo.py`.

```python
def test_o_programa_embrulha_as_linhas():
    p = confere_escada.programa_de("int idade;", "idade = 20;")
    assert "#include <stdio.h>" in p and "int main(void)" in p
    assert p.index("int idade;") < p.index("idade = 20;")

@tem_gcc
def test_declaracao_valida_compila():        assert confere_escada.compila(programa_de("", "int nota ;"))[0]
@tem_gcc
def test_tipo_depois_do_nome_nao_compila():  assert not confere_escada.compila(programa_de("", "nota int ;"))[0]
@tem_gcc
def test_ler_sem_valor_compila_e_nao_e_executado(monkeypatch):
    monkeypatch.setattr(oraculo, "roda", lambda *a, **k: pytest.fail("executou"))
    assert confere_escada.compila(programa_de("", 'int n;\nprintf("%d\\n", n);'))[0]

@tem_gcc
def test_o_conferidor_acusa_resposta_certa_que_nao_compila(tmp_path): ...
    # escada com certa [[1, 0, 2]] ("nota int ;") -> um problema citando o id do degrau
@tem_gcc
def test_o_conferidor_acusa_erro_dito_invalido_que_compila(tmp_path): ...
@tem_gcc
def test_o_conferidor_acusa_saida_que_nao_bate(tmp_path): ...   # digitar com aceitas ["9"] e programa que imprime 8
def test_a_leitura_traz_frases_exercicio_e_retornos(tmp_path):
    texto = confere_escada.leitura(D, escadas)
    assert "## B1" in texto and "Monte a linha" in texto and "Em C o tipo vem primeiro" in texto
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest mvp/test_trilha_oraculo.py -q` → `No module named 'confere_escada'`.

- [ ] **Step 3: Implementar `scripts/confere_escada.py`.** `compila` usa `subprocess.run([str(oraculo.GCC), "-std=c17", "-Wall", "-fsyntax-only", "o.c"], timeout=oraculo.TEMPO)` numa pasta temporária.

- [ ] **Step 4: Rodar e ver passar** — mesmo comando; todos passam (ou são pulados dizendo "sem compilador").

- [ ] **Step 5: Commit** — `scripts/confere_escada.py`, `mvp/test_trilha_oraculo.py`.

---

### Task 3: O conteúdo — a escada do kc_00

**Files:**
- Create: `mvp/dominio/escada_kc00.yaml`
- Create: `docs/escada-kc00-leitura.md` (saída de `--leitura`, para o Rafael ler)
- Test: `mvp/test_trilha_conteudo.py`

**Interfaces:**
- Consumes: `trilha_escada.le`, `faltando`; `confere_escada.confere`, `leitura`.
- Produces: `mvp/dominio/escada_kc00.yaml` com as chaves `B1`, `B2`, `B3`, `B4`, `I1`; ids de degrau `esc_kc00_<premissa>_<n>`.

O roteiro de cada escada. O cenário é um só no tópico inteiro — `idade` (int), `turma` (char), `nota` (int) —, e a segunda versão de cada degrau troca nomes e valores (`ano`, `inicial`, `pontos`).

| premissa | degraus (g = guiado, p = prática) |
| --- | --- |
| **B1** nome e tipo | g `tocar` o nome em `int idade;` · g `montar` `int nota;` · g `escolher` a declaração que guarda `'B'` · p `montar` duas declarações, um int e um char · p `escolher` a linha que não é declaração válida |
| **B2** a caixa já existe | g `escolher`: depois de `int idade;`, a variável já existe? · g `montar` `idade = 20;` com `int idade;` em `antes` (erro previsto: declarar de novo, `invalida`) · g `completar` `___ = 7;` com a variável que foi declarada · p `montar` declarar `nota` e guardar 7, em duas linhas · p `escolher` o trecho que usa variável que não foi declarada |
| **B3** C não limpa a caixa | g `escolher`: que valor há em `idade` logo depois de `int idade;` ("não dá para saber" / "0") · g apresenta `printf("%d\n", idade);` como o jeito de ler, e `montar` a linha que falta antes dele · g `escolher` o trecho que escreve antes de ler · p `montar` o trecho completo: declarar, escrever, ler · p `escolher` o trecho que lê antes de escrever |
| **B4** escrever apaga o antigo | g `digitar` o valor de `idade` depois de `idade = 20; idade = 21;` · g `escolher`: onde ficou o 20? ("em lugar nenhum") · g `montar` a troca de `turma` de `'A'` para `'B'` · p `digitar` o que imprime depois de três escritas · p `digitar` o que imprime com duas variáveis, uma só reescrita |
| **I1** declarar com valor | g `tocar` o valor em `int idade = 20;` · g `montar` `int nota = 7;` · g `escolher`: os dois trechos (uma linha / duas linhas) terminam iguais? · p `montar` em uma linha o que estava em duas · p `digitar` o que imprime `int a = 4; int b; b = a; printf("%d\n", b);` |

Regras do texto, da seção 6.16 da spec, conferidas à mão antes do commit: um degrau, uma ideia; só usa o que um degrau anterior ensinou (nada de `sizeof`, conversão, `(char)`, ponteiro); primeiro o que se faz, depois a ideia; código de iniciante; cada degrau muda uma coisa; todo erro previsto tem retorno próprio; sem analogia no lugar do passo. Em B3 nenhum trecho que lê antes de escrever tem saída, e nenhum é `programa` de `digitar`.

Onde um erro previsto corresponde a uma crença do tópico (`type_is_a_hint`, `no_value_no_memory`, `declaration_zeroes`, `variable_remembers`, `assignment_symmetric`), o `Erro` leva `crenca`.

- [ ] **Step 1: Escrever os testes que falham** em `mvp/test_trilha_conteudo.py`:

```python
D = carrega(topico="kc_00")
CAMINHO = DOMINIO / "escada_kc00.yaml"

def test_as_cinco_premissas_tem_escada():
    escadas = trilha_escada.le(CAMINHO, D)
    assert trilha_escada.faltando(D, escadas) == ()
    assert set(escadas) == set(D.ordem)

def test_cada_escada_tem_de_cinco_a_sete_degraus_e_duas_versoes():
    for e in trilha_escada.le(CAMINHO, D).values():
        assert 5 <= len(e.degraus) <= 7
        assert all(len(g.versoes) >= 2 for g in e.degraus)

PROIBIDOS = ("sizeof", "(char)", "(int)", "*", "&", "[")
def test_nenhum_degrau_usa_o_que_o_topico_nao_ensina():
    for e in trilha_escada.le(CAMINHO, D).values():
        for g in e.degraus:
            for v in g.versoes:
                texto = " ".join((v.mostra, v.antes, v.programa) + v.pecas)
                assert not [p for p in PROIBIDOS if p in texto], g.id

def test_as_duas_versoes_de_um_degrau_nao_sao_a_mesma():
    # v[0].pecas != v[1].pecas ou v[0].mostra != v[1].mostra ou v[0].programa != v[1].programa

def test_todo_degrau_tem_ao_menos_um_erro_previsto_ou_e_de_tocar(): ...

def test_os_cinco_erros_de_crenca_estao_ligados():
    ligadas = {x.crenca for e in escadas.values() for g in e.degraus
               for v in g.versoes for x in v.erros if x.crenca}
    assert ligadas == set(D.crencas)

def test_o_b3_nao_executa_leitura_sem_valor():
    for g in escadas["B3"].degraus:
        assert g.forma != "digitar"
    assert escadas["B3"].revisao.saida == "" or "idade =" in escadas["B3"].revisao.codigo

@tem_gcc
def test_o_compilador_aprova_a_escada_inteira():
    assert confere_escada.confere(trilha_escada.le(CAMINHO, D)) == []
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest mvp/test_trilha_conteudo.py -q` → falha por arquivo inexistente.

- [ ] **Step 3: Escrever `mvp/dominio/escada_kc00.yaml`** seguindo o roteiro e as regras acima, com um cabeçalho de comentário dizendo: o que é, que foi gerado por Claude Fable 5.2 em 13/11/2026, e `# revisado_por:` em branco até o Rafael ler.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest mvp/test_trilha_conteudo.py mvp/test_yaml_duplicado.py -q`
Expected: todos passam.

- [ ] **Step 5: Gerar a leitura**

Run: `python scripts/confere_escada.py kc_00 --leitura > docs/escada-kc00-leitura.md`
Expected: sai com 0; o arquivo traz as cinco premissas com frases, exercícios e retornos.

- [ ] **Step 6: Rodar a suíte inteira** — `python -m pytest mvp -q` (porta 8010 livre).
Expected: `2334 passed, 8 skipped` mais os testes novos; nenhum teste antigo falha por causa do arquivo novo em `mvp/dominio/`. Se algum falhar, parar e avisar o Rafael.

- [ ] **Step 7: Commit** — o YAML, a leitura e o teste.

---

### Task 4: O motor, parte 1 — entrada, sequência, abertura, caminho firme, mapa

**Files:**
- Create: `mvp/trilha.py`
- Create: `scripts/trilha_alunos.py`
- Test: `mvp/test_trilha.py`

**Interfaces:**
- Consumes: `motor.classifica`, `motor.razoes_de(d, a)`, `motor.opcoes_na_tela(semente, a)`, `motor.ordem_das_razoes(semente, id, n)`, `motor.CONFIANCAS`, `motor.Tela`, `motor.Evento`; `trilha_escada.corrige`, `ordem_das_pecas`, `Escada`.
- Produces:

```python
MODOS = ("direto", "explique"); RITMOS = ("completo", "rapido")
JA_SABIA, FIRMOU, APRENDEU, CORRIGIU, EM_ABERTO = "ja_sabia", "firmou", "aprendeu_agora", "corrigiu", "em_aberto"
RESULTADOS = (JA_SABIA, FIRMOU, APRENDEU, CORRIGIU, EM_ABERTO)
ASSIMILOU, NAO_SE_MANTEVE, A_IDEIA_VOLTOU, SEM_QUESTAO = "assimilou", "nao_se_manteve", "a_ideia_voltou", "sem_questao"
TETO_TELAS, TREINO_ALVO, TREINO_MAX = 8, 2, 3
ACOES = ("comecar", "responder", "nao_sei", "continuar", "explicacao", "modo", "ritmo")

@dataclass(frozen=True)
class Entrada:
    acao: str = "responder"
    escolha: int | None = None; razao: int | None = None; confianca: str = ""
    pecas: tuple[int, ...] = (); texto: str = ""        # pecas em índices da TELA
    modo: str = ""; ritmo: str = ""
    ms: int = 0

class EntradaInvalida(ValueError): ...

@dataclass(frozen=True)
class Transicao:
    estado: "Estado"; tela: Tela; eventos: tuple[Evento, ...] = (); explicacao: dict | None = None

def inicia(d: Dominio, escadas: Mapping[str, Escada], semente: str = "") -> Transicao
def avanca(d: Dominio, escadas: Mapping[str, Escada], e: "Estado", entrada: Entrada) -> Transicao
def abertura(d: Dominio, no: str, evita_formato: str = "") -> Atividade
def resumo(d: Dominio, escadas: Mapping[str, Escada], e: "Estado") -> list[dict]
```

`abertura`: entre as questões de diagnóstico da premissa com `nivel == 2` e 2 ou mais razões, a primeira cujo formato difere de `evita_formato`; não havendo, a primeira. O motor passa em `evita_formato` o formato da abertura da premissa anterior.

`Estado` é congelado, e a forma é de quem implementa — menos o que os testes leem: `e.fim: bool`, `e.modo`, `e.ritmo`, `e.premissa(no)` com `.resultado: str` (`""` enquanto aberta), `.telas: int`, `.trabalho: str` (`""`, `"lacuna"`, `"crenca"`), `.degrau: int`, `.reconferencia: str`, `.abriu_explicacao: bool`.

As telas (`Tela.tipo` e as chaves de `dados`) — o cliente e os testes dependem destes nomes:

| tipo | dados | responde-se com |
| --- | --- | --- |
| `entrada` | `titulo`, `premissas`, `modos`, `ritmos`, `ritmo_padrao` | `comecar` + `modo` (+ `ritmo`) |
| `pergunta` | `premissa`, `papel`, `atividade`, `codigo`, `formato`, `opcoes`, `razoes`, `escala`, `pede_razao`, `pede_certeza` (`texto` = enunciado) | `responder` (`escolha`, `razao`, `confianca`) ou `nao_sei` |
| `degrau` | `premissa`, `papel`, `degrau`, `indice`, `total`, `guiado`, `frases`, `forma`, `pede`, `mostra`, `antes`, `pecas`, `tentativa` | `responder` (`pecas` ou `texto`) |
| `retorno` | `premissa`, `veredito`, `mostra_certa`, `premissa_texto`, `escolheu`, `contradiz`, `sobre` (`texto` = o retorno) | `continuar` |
| `voce_disse` | `premissa`, `crenca`, `previsao`, `programa` | `continuar`, ou `responder` (`escolha`) se há `previsao` |
| `maquina` | `premissa`, `tem_prova`, `programa`, `espera`, `nao_compila`, `avisa`, `ambiente`, `afirma`, `premissa_texto`, `apoio`, `previu` | `continuar` |
| `revisao` | `premissa`, `frases`, `codigo`, `saida` | `continuar` |
| `mapa` | `premissas` (= `resumo`) | — |

`papel` de `pergunta`: `abertura`, `reforco`, `topo`, `confirmacao`, `reconferencia`. `papel` de `degrau`: `subida`, `produzir`, `treino`, `reconferencia`. `veredito`: `firme`, `certa`, `errada`, `inseguro`, `escorregao`, `razao_errada`, `lacuna`, `crenca`.

Contagem de telas da premissa: cada `pergunta`, cada `degrau` de papel `produzir` ou `treino`, `voce_disse`, `maquina` e `revisao` contam **uma**; a subida inteira da escada conta **uma**; `retorno` não conta; a reconferência é contada à parte.

Desta task: `inicia`; `comecar`; a sequência por `d.ordem`; a `pergunta` de abertura no modo `direto` (com `pede_razao` e `pede_certeza`); a classificação por `motor.classifica`; o caminho **firme** — no ritmo `rapido` fecha `JA_SABIA`; no `completo` serve o último degrau de prática (versão 0, papel `produzir`) e, certo, fecha `JA_SABIA`. Todo outro episódio, por enquanto, fecha `EM_ABERTO` (as Tasks 5 e 6 trocam isso). Depois da última premissa, `mapa`. Evento `premissa_fechada` com `{"no", "resultado", "telas"}`.

`scripts/trilha_alunos.py`:

```python
PERSONAS = ("sabe", "inseguro", "nao_sabe_aprende", "nao_sabe_erra", "crente_aprende",
            "crente_teimoso", "escorrega", "chuta_com_certeza")

@dataclass
class Caminhada:
    estado: "trilha.Estado"; telas: list[Tela]; eventos: list[Evento]

def responde(d, escadas, tela: Tela, persona: str, estado) -> trilha.Entrada
def caminha(d, escadas, persona: str, modo: str = "direto", ritmo: str = "completo",
            semente: str = "s1", limite: int = 400) -> Caminhada
```

Como cada persona responde: `sabe` — alternativa certa, razão certa, "tenho certeza", degrau certo, previsão certa. `inseguro` — o mesmo com "acho que sei". `nao_sabe_aprende` — `nao_sei` em pergunta de abertura e reforço; degrau certo; depois da escada, certa pela razão certa. `nao_sabe_erra` — `nao_sei` em toda pergunta, degrau sempre errado. `crente_aprende` — na abertura, a alternativa errada cuja crença nega a **própria** premissa (não havendo, a primeira com crença), a razão dessa crença, "tenho certeza"; depois tudo certo. `crente_teimoso` — sempre a alternativa e a razão de crença, com certeza; degrau errado. `escorrega` — na abertura, alternativa errada com a razão certa; depois tudo certo. `chuta_com_certeza` — escolhas tiradas do SHA-256 de `semente|id da tela`, sempre "tenho certeza". `caminha` para no `mapa` ou levanta `AssertionError` ao passar de `limite` entradas.

- [ ] **Step 1: Escrever os testes que falham** em `mvp/test_trilha.py`. Auxiliares do arquivo de teste, usados aqui e nas Tasks 5 a 7: `_comeca(modo, ritmo="completo", semente="s1") -> Transicao` (inicia e manda `comecar`); `_fecha_a_premissa_atual(estado) -> Transicao` e `_responde_firme_ate_fechar(estado, no) -> Estado` (respondem como a persona `sabe` até a premissa fechar); `_tela_voce_disse_de(no)` e `_tela_maquina_de(no)` (levam uma sessão até a prova daquela premissa, escolhendo na abertura dela a alternativa cuja crença a nega, e devolvem a tela).

```python
D = carrega(topico="kc_00"); ESC = trilha_escada.le(DOMINIO / "escada_kc00.yaml", D)

def test_a_primeira_tela_e_a_entrada():
    t = trilha.inicia(D, ESC, "s1").tela
    assert t.tipo == "entrada" and t.dados["premissas"] == 5
    assert t.dados["modos"] == ["direto", "explique"] and t.dados["ritmo_padrao"] == "completo"

def test_comecar_direto_abre_a_primeira_premissa_com_a_pergunta_de_codigo():
    t = _comeca("direto").tela
    assert (t.tipo, t.dados["premissa"], t.dados["papel"]) == ("pergunta", "B1", "abertura")
    assert t.dados["atividade"] == trilha.abertura(D, "B1").id == "ciu_kc00_002"
    assert t.dados["pede_razao"] and t.dados["pede_certeza"]

def test_a_abertura_e_sempre_de_degrau_2_com_duas_razoes():
    for no in D.ordem:
        a = trilha.abertura(D, no)
        assert a.uso == "diagnostico" and a.nivel == 2 and len(motor.razoes_de(D, a)) >= 2

def test_firme_no_ritmo_rapido_fecha_com_uma_tela():
    c = caminha(D, ESC, "sabe", ritmo="rapido")
    assert [c.estado.premissa(n).resultado for n in D.ordem] == ["ja_sabia"] * 5
    assert all(c.estado.premissa(n).telas == 1 for n in D.ordem)

def test_firme_no_ritmo_completo_escreve_antes_de_fechar():
    c = caminha(D, ESC, "sabe")
    produzir = [t for t in c.telas if t.tipo == "degrau"]
    assert len(produzir) == 5 and {t.dados["papel"] for t in produzir} == {"produzir"}
    assert all(t.dados["degrau"] == ESC[t.dados["premissa"]].pratica[-1].id for t in produzir)
    assert all(c.estado.premissa(n).telas == 2 for n in D.ordem)

def test_quem_sabe_tudo_termina_em_doze_telas_ou_sete():
    conta = lambda c: sum(1 for t in c.telas if t.tipo != "retorno")
    assert conta(caminha(D, ESC, "sabe")) <= 2 * 5 + 2
    assert conta(caminha(D, ESC, "sabe", ritmo="rapido")) <= 5 + 2

def test_a_trilha_termina_no_mapa_com_as_cinco_premissas():
    c = caminha(D, ESC, "sabe")
    assert c.telas[-1].tipo == "mapa" and c.estado.fim
    assert [p["no"] for p in c.telas[-1].dados["premissas"]] == list(D.ordem)

def test_a_mesma_semente_redesenha_a_mesma_tela():
    assert _comeca("direto", semente="x").tela == _comeca("direto", semente="x").tela

def test_entrada_que_nao_cabe_na_tela_e_recusada_e_nada_muda():      # Review Focus 1
    e = _comeca("direto").estado
    for ruim in (trilha.Entrada(acao="continuar"), trilha.Entrada(acao="comecar", modo="direto"),
                 trilha.Entrada(acao="responder", escolha=9, razao=0, confianca="tenho certeza"),
                 trilha.Entrada(acao="responder", escolha=0, razao=0, confianca="talvez"),
                 trilha.Entrada(acao="dancar")):
        with pytest.raises(trilha.EntradaInvalida):
            trilha.avanca(D, ESC, e, ruim)

def test_o_motor_nao_importa_relogio_disco_nem_sorteio():
    fonte = (RAIZ / "trilha.py").read_text(encoding="utf-8")
    for proibido in ("import random", "import time", "datetime", "open(", "import os"):
        assert proibido not in fonte
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest mvp/test_trilha.py -q` → `No module named 'mvp.trilha'`.

- [ ] **Step 3: Implementar `scripts/trilha_alunos.py` e a parte 1 de `mvp/trilha.py`.** As alternativas e as razões vão para a tela na ordem de `motor.opcoes_na_tela` e `motor.ordem_das_razoes`; as peças, na de `trilha_escada.ordem_das_pecas`, e o motor desfaz essa ordem antes de chamar `corrige`.

- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha.py -q`.

- [ ] **Step 5: Commit** — `mvp/trilha.py`, `scripts/trilha_alunos.py`, `mvp/test_trilha.py`.

---

### Task 5: O motor, parte 2 — subir a escada

**Files:**
- Modify: `mvp/trilha.py`
- Test: `mvp/test_trilha.py`

**Interfaces:**
- Consumes: tudo da Task 4; `Escada.guiados`, `.pratica`, `.revisao`; `Dominio.exemplo(no)`.
- Produces: o caminho da **lacuna** e o modo `explique`; `Transicao.explicacao` = `{"premissa", "simples", "frases", "codigo", "no"}`; as ações `explicacao`, `modo`, `ritmo`.

Regras (spec 6.2, 6.6, 6.16):

- Lacuna (`nao_sei`, ou errada com "chutei"): `trabalho = "lacuna"`; a pessoa sobe a escada do degrau 1 ao último, versão 0, papel `subida`.
- Degrau errado: `retorno` com o texto do erro, e o **mesmo degrau na versão 1** (`tentativa == 2`). Errado de novo: `retorno` com `mostra_certa`, e a escada segue. `.degrau` conta os degraus certos na primeira tentativa.
- Depois do último degrau: `pergunta` de papel `topo` — a questão de `abertura` se ainda não foi usada na sessão; senão a primeira não usada entre as de diagnóstico e depois as de treino, com 2 ou mais razões, preferindo formato diferente da pergunta anterior da premissa. A mesma preferência vale para a `confirmacao`. Certa pela razão certa: `APRENDEU`. Senão: `revisao`, e **mais uma** `pergunta` (papel `confirmacao`, a próxima não usada); certa pela razão certa: `APRENDEU`; senão `EM_ABERTO`.
- No `topo` da lacuna e na `confirmacao`, `pede_certeza` é falso.
- Modo `explique`: a premissa abre direto na subida. O `topo` dela decide o caminho e tem `pede_certeza` verdadeiro: certa pela razão certa (qualquer confiança) → `APRENDEU`; crença → por enquanto `EM_ABERTO` (a Task 6 liga a prova); o resto → `revisao` e mais uma pergunta.
- `explicacao`: aceita em `pergunta` e `degrau`; devolve a mesma tela, marca `abriu_explicacao` e emite `explicacao_aberta`. `frases` são as dos degraus guiados, em ordem. Uma premissa com `abriu_explicacao` que fecharia `JA_SABIA` fecha `APRENDEU`.
- `modo` e `ritmo`: aceitas em qualquer tela menos `entrada` e `mapa`; devolvem a mesma tela; valem quando a **próxima** premissa abrir.

- [ ] **Step 1: Escrever os testes que falham:**

```python
def test_quem_nao_sabe_sobe_a_escada_do_primeiro_degrau():
    c = caminha(D, ESC, "nao_sabe_aprende")
    b1 = [t for t in c.telas if t.dados.get("premissa") == "B1" and t.tipo != "retorno"]
    assert [t.tipo for t in b1[:2]] == ["pergunta", "degrau"]
    subida = [t for t in b1 if t.tipo == "degrau"]
    assert [t.dados["indice"] for t in subida] == list(range(1, len(ESC["B1"].degraus) + 1))
    assert {t.dados["papel"] for t in subida} == {"subida"}

def test_quem_aprende_fecha_como_aprendeu_agora_em_tres_telas():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert all(c.estado.premissa(n).resultado == "aprendeu_agora" for n in D.ordem)
    assert all(c.estado.premissa(n).telas == 3 for n in D.ordem)     # abertura, subida, topo

def test_o_topo_depois_da_escada_nao_repete_a_abertura():
    c = caminha(D, ESC, "nao_sabe_aprende")
    perguntas = [t.dados["atividade"] for t in c.telas if t.tipo == "pergunta"
                 and t.dados["premissa"] == "B1"]
    assert len(perguntas) == len(set(perguntas))

def test_degrau_errado_volta_com_outros_valores_uma_vez_e_segue():
    c = caminha(D, ESC, "nao_sabe_erra")
    b1 = [t for t in c.telas if t.tipo == "degrau" and t.dados["premissa"] == "B1"]
    assert [t.dados["tentativa"] for t in b1[:2]] == [1, 2]
    assert b1[0].dados["degrau"] == b1[1].dados["degrau"]
    cara = lambda t: (sorted(t.dados["pecas"]), t.dados["mostra"], t.dados["pede"])
    assert cara(b1[0]) != cara(b1[1])
    assert b1[2].dados["indice"] == 2

def test_quem_nao_aprende_ve_a_revisao_e_fecha_em_aberto_em_cinco_telas():
    c = caminha(D, ESC, "nao_sabe_erra")
    assert any(t.tipo == "revisao" for t in c.telas)
    assert all(c.estado.premissa(n).resultado == "em_aberto" for n in D.ordem)
    assert all(c.estado.premissa(n).telas <= 5 for n in D.ordem)

def test_no_modo_explique_a_premissa_abre_na_escada():
    t = _comeca("explique").tela
    assert (t.tipo, t.dados["papel"], t.dados["indice"]) == ("degrau", "subida", 1)

def test_no_modo_explique_ninguem_fecha_como_ja_sabia():
    c = caminha(D, ESC, "sabe", modo="explique")
    assert {c.estado.premissa(n).resultado for n in D.ordem} == {"aprendeu_agora"}

def test_abrir_a_explicacao_devolve_a_mesma_tela_e_tira_o_ja_sabia():
    t0 = _comeca("direto")
    t1 = trilha.avanca(D, ESC, t0.estado, trilha.Entrada(acao="explicacao"))
    assert t1.tela == t0.tela and t1.explicacao["premissa"] == "B1"
    assert t1.explicacao["frases"] == [f for g in ESC["B1"].guiados for f in g.frases]
    assert [e.tipo for e in t1.eventos] == ["explicacao_aberta"]
    fim = _responde_firme_ate_fechar(t1.estado, "B1")
    assert fim.premissa("B1").resultado == "aprendeu_agora"

def test_trocar_o_modo_no_meio_vale_na_premissa_seguinte():          # Review Focus 5
    t0 = _comeca("direto")
    t1 = trilha.avanca(D, ESC, t0.estado, trilha.Entrada(acao="modo", modo="explique"))
    assert t1.tela == t0.tela
    seguinte = _fecha_a_premissa_atual(t1.estado)          # responde firme até abrir B2
    assert (seguinte.tela.tipo, seguinte.tela.dados["premissa"]) == ("degrau", "B2")

def test_trocar_o_ritmo_no_meio_vale_na_premissa_seguinte(): ...
```

- [ ] **Step 2: Rodar e ver falhar** — os testes novos falham (a lacuna ainda fecha `em_aberto` com uma tela).
- [ ] **Step 3: Implementar a parte 2** em `mvp/trilha.py`.
- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha.py -q`, os da Task 4 inclusive.
- [ ] **Step 5: Commit.**

---

### Task 6: O motor, parte 3 — reforço e crença

**Files:**
- Modify: `mvp/trilha.py`
- Test: `mvp/test_trilha.py`

**Interfaces:**
- Consumes: `motor._prova(d, no) -> list[dict]` (chaves `afirma`, `programa`, `espera`, `nao_compila`, `avisa`, `ambiente`); `d.crencas[id].afirma`, `.nega`; `d.nos[no].suporte`, `.simples`.
- Produces: os caminhos **reforço** e **crença**; evento `prova_apresentada` com `{"no", "crenca", "veio_de"}`; evento `prova_dispensada`.

Regras (spec 6.4, 6.5, 6.7, 6.8):

- **Reforço** — episódios `fragil`, `falso_negativo`, `falso_positivo`, e o caminho firme que erra o degrau de produzir. `retorno` (veredito `inseguro`, `escorregao` ou `razao_errada`; no último, `escolheu` = a fala da crença, `contradiz`, `premissa_texto`), e **uma** `pergunta` de papel `reforco`: a primeira não usada das de diagnóstico de formato diferente da abertura, depois as de treino, sempre com 2 ou mais razões; `pede_certeza` verdadeiro. Certa pela razão certa, qualquer confiança: `FIRMOU`. Lacuna: o caminho da Task 5. Crença, ou razão errada pela segunda vez com a mesma crença: a prova. Escorregão pela segunda vez: lacuna.
- **Crença** — errada, razão errada, confiança diferente de "chutei". A prova é da premissa que a crença **nega** (`alvo = d.crencas[c].nega`), na hora:
  1. `voce_disse` com `crenca` = a fala. Se a primeira prova de `motor._prova(d, alvo)` é `nao_compila`: `previsao = {"pergunta": "Este programa compila?", "opcoes": ["Sim", "Não"]}` e `programa` preenchido; se é `avisa`: `"O compilador reclama de alguma coisa aqui?"`; se é `espera`, ou não há prova: `previsao = None`.
  2. `maquina` com a primeira prova; `tem_prova` é falso quando `_prova` volta vazia — aí `programa` é `d.exemplo(alvo)` e não há `espera`. `apoio` = `[{"no", "texto"}]` das premissas de `d.nos[alvo].suporte`. `previu` = o texto da opção escolhida, ou `None`.
  3. Treino no alvo: degraus de prática, papel `treino`, na ordem `p1v0, p2v0, p1v1`. Fecha `CORRIGIU` com `TREINO_ALVO` certas seguidas; ao chegar a `TREINO_MAX` sem isso, `EM_ABERTO`.
- `trabalho = "crenca"` no **alvo**. Se o alvo não é a premissa atual, a trilha volta à atual com a pergunta de reforço; quando a sequência chegar a uma premissa já fechada por prova, pula.
- Se o alvo já tem `trabalho`, não há prova: evento `prova_dispensada`, e a premissa atual segue pelo reforço.
- Um trabalho por premissa: durante um trabalho, uma resposta que pediria outro fecha `EM_ABERTO` — com **uma** exceção (spec 6.6): no `topo` da lacuna, razão errada que é a mesma crença marcada na abertura leva à prova, e o trabalho passa a ser `crenca`.
- Crença que aparece **dentro** de um trabalho (treino, `confirmacao`, reconferência) só é registrada — evento `crenca_registrada` com `{"no", "crenca"}` — e vai para o mapa; não abre prova.
- No modo `explique`, crença no `topo` leva à prova (troca o `EM_ABERTO` provisório da Task 5).

- [ ] **Step 1: Escrever os testes que falham:**

```python
def test_inseguro_ganha_uma_pergunta_de_outro_formato_e_firma():
    c = caminha(D, ESC, "inseguro")
    b1 = [t for t in c.telas if t.tipo == "pergunta" and t.dados["premissa"] == "B1"]
    assert [t.dados["papel"] for t in b1] == ["abertura", "reforco"]
    assert b1[0].dados["formato"] != b1[1].dados["formato"]
    assert c.estado.premissa("B1").resultado == "firmou" and c.estado.premissa("B1").telas == 2

def test_escorregao_vai_para_o_reforco_e_nao_para_a_prova():
    c = caminha(D, ESC, "escorrega")
    assert not any(t.tipo == "voce_disse" for t in c.telas)
    assert c.estado.premissa("B1").resultado == "firmou"

def test_crenca_leva_a_prova_da_premissa_que_ela_nega():
    c = caminha(D, ESC, "crente_aprende")
    provas = [e.dados for e in c.eventos if e.tipo == "prova_apresentada"]
    assert provas and all(D.crencas[p["crenca"]].nega == p["no"] for p in provas)
    disse = next(t for t in c.telas if t.tipo == "voce_disse")
    assert disse.dados["crenca"] == D.crencas[provas[0]["crenca"]].afirma

def test_a_prova_vem_de_motor_prova_e_nao_de_copia():
    c = caminha(D, ESC, "crente_aprende")
    for t in (t for t in c.telas if t.tipo == "maquina"):
        esperado = motor._prova(D, t.dados["premissa"])
        assert t.dados["tem_prova"] == bool(esperado)
        if esperado:
            assert t.dados["programa"] == esperado[0]["programa"]
            assert t.dados["afirma"] == esperado[0]["afirma"]

def test_prova_que_nao_compila_pede_a_previsao():           # a primeira exibível do B2 é nao_compila
    t = _tela_voce_disse_de("B2")
    assert t.dados["previsao"] == {"pergunta": "Este programa compila?", "opcoes": ["Sim", "Não"]}
    assert t.dados["programa"] == motor._prova(D, "B2")[0]["programa"]

def test_prova_que_avisa_pede_a_previsao_do_aviso():        # B3
    assert _tela_voce_disse_de("B3").dados["previsao"]["pergunta"] == \
        "O compilador reclama de alguma coisa aqui?"

def test_prova_com_saida_nao_tem_previsao():                # B1
    assert _tela_voce_disse_de("B1").dados["previsao"] is None

def test_a_premissa_de_inferencia_mostra_o_apoio():
    t = _tela_maquina_de("I1")
    assert [a["no"] for a in t.dados["apoio"]] == ["B1", "B2", "B3", "B4"]

def test_o_treino_fecha_com_duas_certas_seguidas():
    c = caminha(D, ESC, "crente_aprende")
    provadas = [e.dados["no"] for e in c.eventos if e.tipo == "prova_apresentada"]
    assert provadas
    for no in provadas:
        treino = [t for t in c.telas if t.tipo == "degrau" and t.dados["papel"] == "treino"
                  and t.dados["premissa"] == no]
        assert len(treino) == 2 and c.estado.premissa(no).resultado == "corrigiu"

def test_o_treino_para_em_tres_e_fecha_em_aberto():
    c = caminha(D, ESC, "crente_teimoso")
    for n in D.ordem:
        treino = [t for t in c.telas if t.tipo == "degrau" and t.dados["papel"] == "treino"
                  and t.dados["premissa"] == n]
        assert len(treino) <= 3
    assert "corrigiu" not in {c.estado.premissa(n).resultado for n in D.ordem}

def test_cada_premissa_recebe_no_maximo_uma_prova():
    for persona in PERSONAS:
        c = caminha(D, ESC, persona)
        nos = [e.dados["no"] for e in c.eventos if e.tipo == "prova_apresentada"]
        assert len(nos) == len(set(nos)), persona

def test_crenca_sobre_outra_premissa_prova_a_outra_e_volta():
    # monta à mão: na abertura do B1, escolhe a alternativa cuja crença nega OUTRA premissa
    # (a abertura do B1 tem três razões, e as cinco crenças do kc_00 negam premissas
    # distintas: ao menos uma das duas erradas é de outro nó — o teste a procura pela regra,
    # não pelo id). Espera: voce_disse/maquina com premissa == o nó negado; depois pergunta
    # de papel "reforco" com premissa == "B1"; e, quando a sequência chega ao nó negado,
    # ele já tem resultado e nenhuma tela de abertura dele aparece.

def test_premissa_ja_trabalhada_nao_recebe_segunda_prova(): ...   # evento prova_dispensada

def test_a_mesma_crenca_duas_vezes_vai_para_a_prova_mesmo_com_chutei():
    # abertura do B1: errada + razão da crença + "chutei" -> lacuna (sobe a escada);
    # no topo: razão = a mesma crença -> voce_disse; trabalho passa a "crenca".

def test_no_modo_explique_crenca_no_topo_leva_a_prova(): ...
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar a parte 3.** Importar com `from mvp.motor import _prova as provas_exibiveis`, com um comentário dizendo por que o nome privado: o motor atual não muda, e a regra de exibição não pode ter cópia.
- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha.py mvp/test_arquitetura.py -q`.
- [ ] **Step 5: Commit.**

---

### Task 7: O motor, parte 4 — reconferência, mapa e invariantes

**Files:**
- Modify: `mvp/trilha.py`
- Test: `mvp/test_trilha.py`, `mvp/test_trilha_invariantes.py` (novo)

**Interfaces:**
- Produces: a fase de reconferência; `resumo` completo; evento `reconferencia_respondida` com `{"no", "resultado"}`; evento `trilha_encerrada`.

Regras (spec 6.11, 6.16):

- Depois da última premissa, uma questão por premissa com `trabalho != ""`, na ordem de `d.ordem`.
- A questão: o último degrau de prática numa versão ainda não mostrada; senão qualquer versão de prática não mostrada, do degrau mais alto para o mais baixo (papel `reconferencia`); senão uma atividade de marcar não usada, com 2 ou mais razões (`pede_razao` verdadeiro, `pede_certeza` falso); senão `SEM_QUESTAO`, sem tela.
- Certa (e, em pergunta de marcar, pela razão certa): `ASSIMILOU`. Errada apontando a crença corrigida da premissa (`Correcao.crenca` ou a razão marcada): `A_IDEIA_VOLTOU`. Senão: `NAO_SE_MANTEVE`. Sem laço novo.
- `resumo` devolve, por premissa: `no`, `texto` (`simples`), `resultado`, `trabalho`, `degrau`, `degraus`, `reconferencia`, `telas`, `crenca` (a fala, ou `""`), e a explicação para o mapa abrir no lugar — `frases` (as dos degraus guiados) e `codigo` (`d.exemplo(no)`). Para `JA_SABIA` e `FIRMOU`, `degrau == degraus`.

- [ ] **Step 1: Escrever os testes que falham.** Em `mvp/test_trilha.py`:

```python
def test_toda_premissa_trabalhada_e_reconferida_e_as_outras_nao():
    c = caminha(D, ESC, "nao_sabe_aprende")
    rec = [t.dados["premissa"] for t in c.telas if t.dados.get("papel") == "reconferencia"]
    assert rec == list(D.ordem)
    assert not [t for t in caminha(D, ESC, "sabe").telas if t.dados.get("papel") == "reconferencia"]

def test_a_reconferencia_e_de_produzir_e_nao_repete_exercicio():
    c = caminha(D, ESC, "nao_sabe_aprende")
    vistos = set()
    for t in (t for t in c.telas if t.tipo == "degrau"):
        chave = (t.dados["degrau"], tuple(t.dados["pecas"]), t.dados["mostra"])
        if t.dados["papel"] == "reconferencia":
            assert chave not in vistos
        vistos.add(chave)

def test_quem_aprendeu_e_acerta_no_fim_assimilou():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert {c.estado.premissa(n).reconferencia for n in D.ordem} == {"assimilou"}

def test_quem_erra_no_fim_nao_se_manteve_e_nao_abre_laco(): ...   # "nao_sabe_erra"
def test_a_crenca_de_novo_no_fim_e_a_ideia_voltou(): ...          # "crente_teimoso"
def test_o_mapa_traz_resultado_degrau_e_reconferencia():
    p = caminha(D, ESC, "nao_sabe_aprende").telas[-1].dados["premissas"][0]
    assert set(p) == {"no", "texto", "resultado", "trabalho", "degrau", "degraus",
                      "reconferencia", "telas", "crenca", "frases", "codigo"}
    assert p["degrau"] == p["degraus"] == len(ESC["B1"].degraus)
```

Em `mvp/test_trilha_invariantes.py`, sobre `PERSONAS × MODOS × RITMOS` e as sementes `("s1", "s2", "s3")`:

```python
TODAS = [(p, m, r, s) for p in PERSONAS for m in trilha.MODOS for r in trilha.RITMOS for s in ("s1", "s2", "s3")]

@pytest.mark.parametrize("persona, modo, ritmo, semente", TODAS)
def test_toda_sessao_termina_e_toda_premissa_tem_resultado(persona, modo, ritmo, semente):
    c = caminha(D, ESC, persona, modo, ritmo, semente)
    assert c.estado.fim and c.telas[-1].tipo == "mapa"
    assert all(c.estado.premissa(n).resultado in trilha.RESULTADOS for n in D.ordem)

def test_ninguem_passa_de_oito_telas_numa_premissa(...):      # .telas <= trilha.TETO_TELAS

def test_nenhuma_premissa_fecha_bem_sem_resposta_certa_pela_razao_certa(...):
    # para cada premissa com resultado != "em_aberto": existe evento do tipo
    # "episodio_classificado" com estado em ("confirmada", "fragil") OU "degrau_respondido"
    # com certa == True e papel em ("produzir", "treino"), daquela premissa.

def test_a_maquina_so_respondeu_onde_ha_prova(...):           # tem_prova == bool(motor._prova(...))
def test_ninguem_fica_preso_num_degrau(...):                   # nenhum degrau com tentativa > 2
def test_a_mesma_sessao_reexecutada_da_as_mesmas_telas(...):   # duas caminhadas iguais -> telas iguais
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar a parte 4.** O motor emite `episodio_classificado` (`{"no", "estado", "atividade", "papel"}`) e `degrau_respondido` (`{"no", "degrau", "versao", "papel", "certa", "tentativa"}`) em toda resposta.
- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha.py mvp/test_trilha_invariantes.py -q`.
- [ ] **Step 5: Commit.**

---

### Task 8: O registro e as rotas

**Files:**
- Create: `mvp/trilha_log.py`, `mvp/trilha_app.py`
- Test: `mvp/test_trilha_app.py`

**Interfaces:**
- Consumes: `trilha.inicia`, `avanca`, `Entrada`, `EntradaInvalida`, `resumo`; `trilha_escada.RespostaInvalida`, `faltando`; `mvp.log.agora`.
- Produces:

```python
# mvp/trilha_log.py
VERSAO = 1
ENTRADA = "entrada_recebida"
def grava(destino: Path, sessao: str, eventos: Iterable[Evento], entrada: Entrada | None = None) -> None
def le(destino: Path, sessao: str | None = None) -> list[dict]

# mvp/trilha_app.py
CODIGO = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,15}$")
LIMITE_MS = 2 * 60 * 60 * 1000
def cria_app(d: Dominio, escadas: Mapping[str, Escada], destino: Path) -> FastAPI
```

Cada linha do registro: `{"v": 1, "ts", "sessao", "tipo", …dados}`, a entrada antes dos eventos que ela provocou; um dado chamado `v`, `ts`, `sessao` ou `tipo` é gravado com o sufixo `_do_evento`. A pasta do arquivo nasce **na primeira gravação**, não na criação do app.

Rotas:

| rota | resposta |
| --- | --- |
| `POST /sessoes` `{"codigo": ""}` | `{"sessao", "tela", "progresso"}`. Sem código: 12 hex aleatórios. Código fora de `CODIGO`: 400. Código de sessão que está na memória: devolve a tela atual dela. |
| `POST /sessoes/{sessao}/agir` (campos de `Entrada`; `ms` entre 0 e `LIMITE_MS`) | `{"sessao", "tela", "explicacao", "progresso"}`. Sessão desconhecida: 404. `EntradaInvalida` ou `RespostaInvalida`: 400, **nada gravado, estado igual**. |
| `GET /saude` | `{"ok": true, "topico", "titulo", "premissas", "degraus"}` |
| `GET /` | `mvp/web/trilha.html` |
| `/web` | os estáticos de `mvp/web` |

`progresso` = `{"feitas", "total", "premissas": [{"no", "resultado"}]}`. `cria_app` levanta `ValueError` se `faltando(d, escadas)` não for vazio.

- [ ] **Step 1: Escrever os testes que falham** (`TestClient`, `destino = tmp_path / "trilha" / "kc_00.jsonl"`):

```python
def test_abrir_devolve_a_tela_de_entrada_e_o_progresso(cliente):
    j = cliente.post("/sessoes", json={}).json()
    assert j["tela"]["tipo"] == "entrada" and j["progresso"] == {
        "feitas": 0, "total": 5, "premissas": [{"no": n, "resultado": ""} for n in D.ordem]}

def test_a_pasta_do_registro_so_nasce_na_primeira_gravacao(tmp_path):
    trilha_app.cria_app(D, ESC, tmp_path / "trilha" / "kc_00.jsonl")
    assert not (tmp_path / "trilha").exists()

def test_uma_sessao_inteira_pelo_http_chega_ao_mapa(cliente): ...
    # caminha com responde() de scripts/trilha_alunos, convertendo Tela <-> JSON; termina em "mapa"

def test_o_registro_traz_a_entrada_antes_do_que_ela_provocou(cliente, destino):
    linhas = trilha_log.le(destino, sessao)
    assert linhas[0]["tipo"] == "trilha_iniciada" and all(l["v"] == 1 for l in linhas)
    i = next(k for k, l in enumerate(linhas) if l["tipo"] == "entrada_recebida")
    assert linhas[i]["acao"] == "comecar" and linhas[i + 1]["tipo"] != "entrada_recebida"

def test_resposta_repetida_da_400_e_nao_grava(cliente, destino):        # Review Focus 1
    antes = len(trilha_log.le(destino)); r = cliente.post(agir, json=mesma_resposta)
    assert r.status_code == 400 and len(trilha_log.le(destino)) == antes

def test_peca_repetida_da_400(cliente): ...                              # Review Focus 3
def test_sessao_desconhecida_da_404(cliente):                             # Review Focus 2
    assert cliente.post("/sessoes/nao_existe/agir", json={"acao": "continuar"}).status_code == 404
def test_codigo_fora_do_formato_da_400(cliente): ...                      # {"codigo": "9abc"}, {"codigo": "a b"}
def test_o_mesmo_codigo_devolve_a_tela_em_que_a_sessao_estava(cliente): ...
def test_ms_negativo_ou_absurdo_da_422(cliente): ...
def test_topico_sem_escada_completa_nao_sobe():
    with pytest.raises(ValueError):
        trilha_app.cria_app(D, {"B1": ESC["B1"]}, tmp_path / "x.jsonl")
def test_o_app_nao_escreve_no_registro_do_fluxo_atual(cliente): ...       # mvp.log.DESTINO intocado
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar os dois módulos.** O estado das sessões fica num dicionário dentro de `cria_app`, não em variável de módulo. A rota `GET /` é escrita aqui, e o teste dela vem na Task 9, com a página.
- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha_app.py -q`.
- [ ] **Step 5: Commit.**

---

### Task 9: As telas

**Files:**
- Create: `mvp/web/trilha.html`, `mvp/web/trilha.js`, `mvp/web/trilha.css`
- Test: `mvp/test_trilha_telas.py`

**Interfaces:**
- Consumes: as rotas da Task 8; `Figuras.topico(id)`, `Figuras.dentro(elemento, no)` de `mvp/web/figuras.js`; as variáveis de cor de `mvp/web/style.css`.
- Produces: a página servida em `/trilha/kc_00/`.

O que a página faz:

- Descobre a base pelo caminho (`/trilha/kc_XX`), como `mvp/web/app.js` faz com `/kc/kc_XX`; lê `?codigo=`.
- Cabeçalho fixo: "← todos os tópicos", a barra de progresso (uma marca por premissa, pela chave `progresso`), e os dois controles de modo e ritmo.
- `entrada`: os dois botões de modo e os dois de ritmo, `completo` marcado.
- `pergunta`: enunciado, código, alternativas. As razões só aparecem depois de escolhida a alternativa, e nesse momento as alternativas travam; a certeza só depois da razão. Um envio só. Botões "Não sei" e "Ver a explicação".
- `degrau`: as frases (se guiado), "passo `indice` de `total`", e a forma — `tocar`: as peças em linha, como código; `montar`: banco de peças e a linha sendo montada, tocar põe e tira; `escolher`: lista; `completar`: a `mostra` com a lacuna e o banco; `digitar`: um campo curto, monoespaçado.
- `retorno`: aparece **abaixo** do que estava na tela, sem limpá-la, com "Continuar". Frases fixas por `veredito`; `mostra_certa` como código.
- `voce_disse`, `maquina` (programa aberto, saída ou a fala do compilador, `afirma`, a premissa, o apoio; sem `tem_prova`, o título não diz "a máquina respondeu"), `revisao`, `mapa` (resultado e reconferência em palavras, degrau alcançado, e a nota fixa "isto é o que você assimilou nesta sessão").
- `explicacao`: painel por cima, com `simples`, as frases, o código e a figura.
- 404 em `agir`: mensagem "esta sessão não existe mais" e botão "Recomeçar".
- Botões desabilitados entre o envio e a resposta (o duplo clique não manda duas vezes).

- [ ] **Step 1: Escrever os testes que falham** em `mvp/test_trilha_telas.py`:

```python
JS = (WEB / "trilha.js").read_text(encoding="utf-8")
HTML = (WEB / "trilha.html").read_text(encoding="utf-8")

def test_a_raiz_serve_a_pagina_da_trilha(tmp_path):
    cliente = TestClient(trilha_app.cria_app(D, ESC, tmp_path / "t.jsonl"))
    r = cliente.get("/")
    assert r.status_code == 200 and "/web/trilha.js?v=20261113" in r.text

def test_os_assets_da_pagina_sao_versionados():
    for nome in ("trilha.js", "trilha.css", "figuras.js", "style.css"):
        assert "/web/%s?v=20261113" % nome in HTML or "/web/%s?v=20261112" % nome in HTML

def test_o_cliente_le_todos_os_campos_que_o_servidor_monta():
    chaves = {"tipo", "texto"}
    for persona in PERSONAS:
        for modo in trilha.MODOS:
            for t in caminha(D, ESC, persona, modo).telas:
                chaves |= set(t.json())
    assert not sorted(k for k in chaves if k not in JS)

def test_o_cliente_desenha_as_cinco_formas_e_os_oito_tipos_de_tela():
    for nome in trilha_escada.FORMAS + ("entrada", "pergunta", "degrau", "retorno",
                                         "voce_disse", "maquina", "revisao", "mapa"):
        assert '"%s"' % nome in JS

def test_o_cliente_trata_a_sessao_perdida():
    assert "404" in JS and "Recomeçar" in HTML

def test_o_cliente_nao_escreve_conteudo():
    # nenhuma frase de premissa ou de crença do kc_00 aparece em trilha.js nem em trilha.html
    for texto in [n.simples for n in D.nos.values()] + [c.afirma for c in D.crencas.values()]:
        assert texto not in JS and texto not in HTML
```

- [ ] **Step 2: Rodar e ver falhar** — arquivo inexistente.
- [ ] **Step 3: Escrever os três arquivos.**
- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha_telas.py mvp/test_trilha_app.py -q`.
- [ ] **Step 5: Commit** (a conferência no navegador é da Task 11, com o portal montado).

---

### Task 10: O portal abre a trilha do kc_00

**Files:**
- Modify: `mvp/portal.py` (`cria_portal`), `mvp/web/portal.html`
- Test: `mvp/test_trilha_portal.py`

**Interfaces:**
- Consumes: `trilha_app.cria_app`, `trilha_escada.le`, `faltando`.
- Produces: `GET /topicos` com a chave nova `trilha` em cada item (`"/trilha/kc_00/"` ou `None`); a trilha montada em `/trilha/<topico>`; o registro em `<pasta>/trilha/<topico>.jsonl`.

Regras: o portal monta a trilha de todo tópico que tenha `mvp/dominio/escada_<kcNN>.yaml` com escada para todas as premissas — hoje, só o kc_00. A chave `caminho` não muda. Em `portal.html`, o item de um tópico com `trilha` abre a trilha, e ganha um link discreto "versão anterior" para `caminho`; os outros ficam como estão. Nenhuma pasta nova nasce na criação do portal.

- [ ] **Step 1: Escrever os testes que falham:**

```python
def test_so_o_kc_00_tem_trilha(cliente):
    lista = cliente.get("/topicos").json()["topicos"]
    assert {t["id"]: t["trilha"] for t in lista} == {
        t: ("/trilha/kc_00/" if t == "kc_00" else None) for t in topicos()}

def test_a_trilha_responde_no_caminho_dela(cliente):
    assert cliente.get("/trilha/kc_00/saude").json()["topico"] == "kc_00"
    assert cliente.post("/trilha/kc_00/sessoes", json={}).json()["tela"]["tipo"] == "entrada"

def test_o_fluxo_atual_do_kc_00_continua_no_lugar(cliente):
    assert cliente.get("/kc/kc_00/saude").json()["topico"] == "kc_00"

def test_o_registro_da_trilha_fica_separado(tmp_path):
    so_este = TestClient(portal.cria_portal(tmp_path))
    so_este.post("/trilha/kc_00/sessoes", json={})
    assert (tmp_path / "trilha" / "kc_00.jsonl").exists()
    assert not (tmp_path / "kc_00.jsonl").exists()

def test_criar_o_portal_nao_cria_a_pasta_da_trilha(tmp_path):
    portal.cria_portal(tmp_path)
    assert not (tmp_path / "trilha").exists()

def test_a_pagina_inicial_abre_a_trilha_e_guarda_a_versao_anterior():
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    assert "t.trilha" in html and "versão anterior" in html

def test_a_trilha_tambem_responde_sem_cache(cliente):
    assert cliente.get("/trilha/kc_00/").headers["Cache-Control"] == "no-cache"
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** em `cria_portal` e em `portal.html`.
- [ ] **Step 4: Rodar e ver passar** — `python -m pytest mvp/test_trilha_portal.py mvp/test_portal.py mvp/test_docker.py -q`. `test_portal.py` e `test_docker.py` passam **sem terem sido tocados**.
- [ ] **Step 5: Commit.**

---

### Task 11: Verificação de ponta a ponta, e a medida

**Files:**
- Modify: `scripts/trilha_alunos.py` (um `main` que imprime a medida)
- Modify: `docs/trilha.md` (seção 6.10: a medida do kc_00 ao lado da estimativa)
- Test: a suíte inteira.

**Interfaces:**
- Produces: `python scripts/trilha_alunos.py kc_00` imprime, por persona × modo × ritmo: telas no total (sem `retorno`), a maior contagem numa premissa, e os resultados.

- [ ] **Step 1: Escrever o teste que falha** em `mvp/test_trilha_invariantes.py`:

```python
def test_a_medida_sai_para_todas_as_personas(capsys):
    trilha_alunos.main(["kc_00"])
    saida = capsys.readouterr().out
    assert all(p in saida for p in PERSONAS) and "completo" in saida and "rapido" in saida
```

- [ ] **Step 2: Rodar e ver falhar; implementar `main`; rodar e ver passar.**

- [ ] **Step 3: Rodar a suíte inteira**, com a porta 8010 livre e nada mais rodando.

Run: `python -m pytest mvp -q`
Expected: `2334 passed, 8 skipped` **mais** os testes novos, zero falhas. Qualquer teste antigo vermelho: parar e avisar o Rafael.

- [ ] **Step 4: Conferir no navegador.** Subir o portal pela configuração `portal` de `.claude/launch.json` (pasta `ensaios/portal`, nunca `coleta/`), abrir `/trilha/kc_00/` e atravessar à mão: uma sessão "Me pergunte direto" acertando tudo; uma "Me explique antes" errando um degrau de propósito; uma com crença no B2 (a previsão "Este programa compila?"); abrir "Ver a explicação"; trocar o ritmo no meio; recarregar a página com `?codigo=` e voltar na mesma tela; derrubar o servidor e ver a mensagem de sessão perdida. Console sem erro. Conferir em largura de celular.
Expected: cada tela desenha, nenhuma fica em branco, e o mapa fecha as três sessões.

- [ ] **Step 5: Registrar a medida.** Rodar `python scripts/trilha_alunos.py kc_00` e pôr a tabela em `docs/trilha.md`, seção 6.10, dizendo que é medida do kc_00 (cinco premissas) e mantendo a estimativa ao lado.

- [ ] **Step 6: Commit**, e entregar ao Rafael `docs/escada-kc00-leitura.md` para leitura: o conteúdo só vai para o ramo principal depois que ele ler.
