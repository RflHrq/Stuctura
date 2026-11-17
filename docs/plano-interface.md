# Interface — fatia 1: identidade e telas — Plano de construção

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** As telas da trilha e a página inicial ganham a identidade aprovada — logo, modo escuro "noite de editor", modo claro "moldura de terminal", fontes, topo com paradas e troca de tema, código em cores — sem mudar o que a sessão faz.

**Architecture:** Uma folha de estilo nova (`tema.css`) redefine as variáveis de cor que `style.css` e `trilha.css` já usam, por tema (`html[data-tema="escuro"|"claro"]`), e acrescenta as peças novas; `style.css` não é tocado, e o fluxo anterior não muda. Um script pequeno no `<head>` (`tema.js`) escolhe o tema antes de a página aparecer. Um realce de código próprio (`realce.js`) só envolve pedaços do texto em `<span>`, e é testado pelo Node contra todos os trechos das escadas.

**Tech Stack:** HTML, CSS e JavaScript sem framework (como o resto de `mvp/web/`); Python/pytest para os testes; Node (já instalado, v24) para rodar `tema.js` e `realce.js` nos testes, com `skip` se faltar.

**Spec:** `docs/interface.md` (seções 3, 5, 6 e 9.1), com os esboços em `docs/esbocos/` (o 3 é o logo; o 5, os dois temas; o 4, as telas).

## Global Constraints

- Nenhum arquivo carregado de outro endereço: sem `http://`/`https://` em `src`, `href` ou `url(` em `mvp/web/`.
- Fontes guardadas em `mvp/web/fontes/`, licença OFL, com o arquivo de licença ao lado. Baixar foi autorizado pelo Rafael em 16/11/2026.
- Contraste AA: 4,5:1 para texto comum, nos dois temas.
- `@media (prefers-reduced-motion: reduce)` desliga animação e transição.
- Funciona a partir de 360 px de largura, sem rolagem lateral da página.
- `style.css`, `index.html`, `app.js`, `figuras.js`, `painel.html` não mudam.
- Motor, escadas, rotas e o que se grava em `coleta/` não mudam.
- Assets com versão no endereço; a desta fatia é `?v=20261116`.
- Teste anterior ao ramo `trilha` não é tocado. Teste do ramo que mude por mudança deliberada é listado no commit, com o porquê.
- Ensaio no servidor da porta 8013 (`ensaios/`); nunca na 8010, nunca em `coleta/`.
- Commits com `git -c user.name="Rafael H. S. Simao" -c user.email="15497616+RflHrq@users.noreply.github.com"` e a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Tema piscando ao abrir:** a página aparece clara e vira escura um instante depois. `tema.js` roda no `<head>`, antes de qualquer folha de estilo pintar — conferido no navegador (Task 2).
2. **Navegador sem `localStorage`** (janela anônima, dados bloqueados): a página abre com o tema do sistema e a troca funciona na sessão, sem erro — teste com Node (Task 2).
3. **Linha de código comprida em 360 px:** rola dentro da moldura do editor, e nunca a página inteira — conferido no navegador (Task 5).
4. **Trechos com `"%d\n"`, `//` dentro de aspas, `/* */`, `'a'`:** o realce devolve o texto idêntico — teste com todos os trechos de todas as escadas (Task 3).
5. **Saída da máquina e mensagem do compilador** (`bloco(texto, "terminal")`) não são coloridas como C — teste (Task 3).

---

### Task 1: Fontes e ícone

**Files:**
- Create: `mvp/web/fontes/nunito.woff2`, `mvp/web/fontes/jetbrains-mono.woff2`, `mvp/web/fontes/LICENCA-nunito.txt`, `mvp/web/fontes/LICENCA-jetbrains-mono.txt`, `mvp/web/marca.svg`
- Test: `mvp/test_interface.py` (novo)

**Interfaces:**
- Produces: `/web/fontes/nunito.woff2`, `/web/fontes/jetbrains-mono.woff2` (servidos pelo `StaticFiles` que já monta `/web`); `/web/marca.svg` (ícone da aba).

- [ ] **Step 1: Write the failing tests** em `mvp/test_interface.py`

```python
FONTES = WEB / "fontes"

def test_as_fontes_estao_no_projeto_com_licenca():
    for nome in ("nunito", "jetbrains-mono"):
        dados = (FONTES / f"{nome}.woff2").read_bytes()
        assert dados[:4] == b"wOF2", nome
        assert 10_000 < len(dados) < 400_000, nome
        licenca = (FONTES / f"LICENCA-{nome}.txt").read_text(encoding="utf-8")
        assert "SIL OPEN FONT LICENSE" in licenca.upper(), nome

def test_o_icone_da_aba_e_o_s_que_e_um_ponteiro():
    svg = (WEB / "marca.svg").read_text(encoding="utf-8")
    assert svg.lstrip().startswith("<svg") and "viewBox" in svg
    assert "http" not in svg.replace('xmlns="http://www.w3.org/2000/svg"', "")
```

- [ ] **Step 2: Run** `python -m pytest mvp/test_interface.py -q` — Expected: 2 FAIL (arquivos não existem).
- [ ] **Step 3: Baixar as fontes.** Fonte: os pacotes `@fontsource-variable/nunito` e `@fontsource-variable/jetbrains-mono` do npm (o projeto Fontsource redistribui as fontes do Google Fonts, OFL), pela CDN `cdn.jsdelivr.net/npm/`. Fixar a versão consultando `https://registry.npmjs.org/<pacote>` (campo `dist-tags.latest`). Arquivos: `files/nunito-latin-wght-normal.woff2`, `files/jetbrains-mono-latin-wght-normal.woff2` e o `LICENSE` de cada pacote. Baixar para uma pasta nova e vazia no scratchpad, conferir os 4 bytes `wOF2` e o tamanho, e só então copiar com os nomes de cima. Registrar no commit a versão, o endereço e o tamanho de cada arquivo.
- [ ] **Step 4: Criar `mvp/web/marca.svg`** — o logo B do esboço 3: quadrado 32×32 de cantos 8, fundo `#1f5668`, o S branco em traço (o `path` do esboço), caixinha `#f2a541`; com `<title>Structura</title>`.
- [ ] **Step 5: Run** `python -m pytest mvp/test_interface.py -q` — Expected: 2 PASS.
- [ ] **Step 6: Commit** `mvp/web/fontes/ mvp/web/marca.svg mvp/test_interface.py` — "A interface ganha as fontes livres e o icone".

### Task 2: Os dois temas e a troca

**Files:**
- Create: `mvp/web/tema.css`, `mvp/web/tema.js`
- Modify: `mvp/web/trilha.html` (head e topo), `mvp/web/portal.html` (head e topo)
- Modify: `mvp/test_trilha_telas.py:44-60` (versão dos assets — mudança deliberada)
- Test: `mvp/test_interface.py`

**Interfaces:**
- Consumes: Task 1 (fontes, `marca.svg`).
- Produces: `window.Tema = { atual() -> "escuro"|"claro", liga(botao: HTMLButtonElement) -> void }`; atributo `data-tema` em `<html>`; chave `structura-tema` no `localStorage`; as variáveis de CSS abaixo, por tema.

Variáveis em `tema.css` — as que `style.css`/`trilha.css` já usam (`--papel --cartao --tinta --tinta2 --linha --linha2 --acento --acento-fundo --ok --ok-fundo --erro --erro-fundo --aviso --aviso-fundo`) e as novas: `--destaque --destaque-fundo --bilhete --editor --editor-tinta --sx-palavra --sx-numero --sx-funcao --sx-texto --sx-comentario --topo --topo-tinta --botao --botao-tinta --brilho --marca-fundo --marca-traco --marca-caixa`. Valores de partida: os dos esboços (escuro: fundo `#0d1520`, cartão `#152233`, acento `#38bdf8`, destaque `#fb923c`; claro: fundo `#e9eff1` quadriculado, cartão `#fff`, topo `#12303a`, botão laranja). **Se um par falhar no contraste, escurece-se ou clareia-se a cor; a régua não baixa.**

Seletores: `html[data-tema="claro"]` e `html[data-tema="escuro"]`; sem atributo (sem JavaScript), `@media (prefers-color-scheme: dark)` aplica o escuro. Fontes por `@font-face` (`font-display: swap`), Nunito no corpo e JetBrains Mono em código e rótulos, com a pilha do sistema como reserva.

- [ ] **Step 1: Write the failing tests** em `mvp/test_interface.py`:

```python
PARES = [("tinta", "papel"), ("tinta", "cartao"), ("tinta2", "cartao"),
         ("acento", "cartao"), ("ok", "ok-fundo"), ("erro", "erro-fundo"),
         ("aviso", "aviso-fundo"), ("botao-tinta", "botao"),
         ("topo-tinta", "topo"), ("editor-tinta", "editor"),
         ("sx-palavra", "editor"), ("sx-numero", "editor"), ("sx-funcao", "editor"),
         ("sx-texto", "editor"), ("sx-comentario", "editor")]

@pytest.mark.parametrize("tema", ["claro", "escuro"])
def test_os_dois_temas_passam_no_contraste(tema):
    cores = cores_do_tema(tema)            # lê tema.css; cada valor é #rrggbb
    for frente, fundo in PARES:
        assert contraste(cores[frente], cores[fundo]) >= 4.5, (tema, frente, fundo)

def test_nada_e_carregado_de_outro_endereco():
    for f in WEB.glob("*.*"):
        if f.suffix in (".html", ".css", ".js"):
            txt = f.read_text(encoding="utf-8")
            assert not re.search(r'(?:src|href)\s*=\s*"https?://|url\(\s*["\']?https?://', txt), f.name

def test_reduzir_movimento_desliga_animacao():
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    bloco = re.search(r"prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\n\}", css, re.S)
    assert bloco and "animation: none" in bloco.group(1) and "transition: none" in bloco.group(1)

@tem_node
@pytest.mark.parametrize("guardado, sistema_escuro, armazenamento, esperado", [
    (None, True, "ok", "escuro"), (None, False, "ok", "claro"),
    ("claro", True, "ok", "claro"), ("escuro", False, "ok", "escuro"),
    (None, True, "quebrado", "escuro"),     # localStorage que lança erro
])
def test_o_tema_e_escolhido_antes_da_pagina(guardado, sistema_escuro, armazenamento, esperado):
    assert roda_tema_js(guardado, sistema_escuro, armazenamento) == esperado

def test_as_duas_paginas_carregam_o_tema_no_head():
    for pagina in ("trilha.html", "portal.html"):
        html = (WEB / pagina).read_text(encoding="utf-8")
        cabeca = html.split("</head>")[0]
        assert '/web/tema.js?v=20261116' in cabeca and '/web/tema.css?v=20261116' in cabeca
        assert cabeca.index("tema.js") < cabeca.index("style.css")
        assert 'rel="icon"' in cabeca and "/web/marca.svg?v=20261116" in cabeca
        assert 'id="btn-tema"' in html
```

`cores_do_tema`, `contraste` (fórmula WCAG 2.x de luminância relativa), `tem_node` (`skipif` sem `node`) e `roda_tema_js` (escreve um stub de `window`, `document.documentElement`, `matchMedia` e `localStorage` num `.js` temporário, faz `require` de `tema.js` e imprime o `data-tema`) moram no próprio `test_interface.py`. `tema.js` precisa funcionar como script de página e ser carregável pelo Node: `(function (global) { … })(typeof window !== "undefined" ? window : this)`.

- [ ] **Step 2: Run** `python -m pytest mvp/test_interface.py -q` — Expected: os novos FAIL.
- [ ] **Step 3: Implement** `tema.js` (escolha: valor guardado → `matchMedia("(prefers-color-scheme: dark)")` → claro; todo acesso a `localStorage` em `try/catch`; `liga` põe o texto "Tema escuro"/"Tema claro", `aria-pressed`, troca e guarda), `tema.css` (variáveis dos dois temas, `@font-face`, fundo pontilhado no escuro e quadriculado no claro, o bloco de reduzir movimento), e as duas páginas (no `<head>`: `tema.js` antes das folhas, `tema.css` depois delas, o ícone; no topo: `<button id="btn-tema" class="btn-topo" type="button">`). Versão de todos os assets das duas páginas: `?v=20261116`.
- [ ] **Step 4: Update os dois testes do ramo que fixam versão** (`test_a_raiz_serve_a_pagina_da_trilha`, `test_os_assets_da_pagina_sao_versionados`): a versão nova é `20261116`, e a lista de assets versionados passa a incluir `tema.js`, `tema.css` e `marca.svg`. A regra "nenhum asset sem versão" continua igual.
- [ ] **Step 5: Run** `python -m pytest mvp/test_interface.py mvp/test_trilha_telas.py mvp/test_trilha_portal.py mvp/test_portal.py -q` — Expected: PASS.
- [ ] **Step 6: Conferir no navegador** (servidor de ensaio, `preview_start portal-ensaio`): abrir `/trilha/kc_00/` com o sistema em escuro e em claro (`resize_window colorScheme`), recarregar e ver que não pisca; trocar pelo botão e recarregar — a escolha fica.
- [ ] **Step 7: Commit** — "Os dois temas: noite de editor e moldura de terminal", listando os dois testes do ramo alterados e por quê.

### Task 3: O realce de código

**Files:**
- Create: `mvp/web/realce.js`
- Modify: `mvp/web/trilha.js:104-106` (`bloco`), `mvp/web/trilha.html` (carregar `realce.js?v=20261116` antes de `trilha.js`)
- Test: `mvp/test_interface.py`

**Interfaces:**
- Produces: `window.Realce = { pedacos(texto: string) -> Array<{tipo: "palavra"|"numero"|"texto"|"comentario"|"funcao"|"", texto: string}>, preenche(pre: HTMLElement, texto: string) -> void }`; classes CSS `sx-palavra sx-numero sx-texto sx-comentario sx-funcao`.
- Consumes: Task 2 (as variáveis `--sx-*`).

Regras: comentário `//…` até o fim da linha e `/*…*/`; texto entre `"…"` e `'…'` com `\` escapando; número decimal e `0x…`; palavras-chave do C que o conteúdo usa (`int char void return if else for while sizeof const static struct double float long unsigned NULL`); nome seguido de `(` (com espaços) é `funcao`. Nada é reconhecido dentro de texto ou de comentário.

- [ ] **Step 1: Write the failing tests:**

```python
def _todos_os_trechos():
    """Todo código que a trilha mostra: revisão, passos e provas, nos tópicos com escada."""
    ...  # varre mvp/dominio/escada_*.yaml com trilha_escada.le

@tem_node
def test_o_realce_devolve_o_texto_identico():
    trechos = _todos_os_trechos()
    assert len(trechos) > 500
    assert roda_realce_js(trechos) == trechos      # junta os pedaços de cada um

@tem_node
def test_o_realce_reconhece_cada_peca():
    pedacos = roda_pedacos('void f(int n) { n = 99; printf("%d\\n", n); } // fim')
    assert ("palavra", "void") in pedacos and ("funcao", "f") in pedacos
    assert ("numero", "99") in pedacos and ("texto", '"%d\\n"') in pedacos
    assert ("funcao", "printf") in pedacos and ("comentario", "// fim") in pedacos
    assert roda_pedacos('"a // b"') == [("texto", '"a // b"')]

def test_so_o_codigo_e_colorido_e_a_saida_nao():
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    corpo = re.search(r"function bloco\(texto, classe\) \{(.*?)\n  \}", js, re.S).group(1)
    assert "Realce.preenche" in corpo          # o código é colorido
    assert "textContent" in corpo              # a saída, e a falta do realce, não
    assert '"codigo"' in corpo                 # quem decide é a classe do bloco
    # e as saídas continuam chegando com a classe delas
    assert js.count('bloco(t.espera, "terminal")') == 1
    assert js.count('bloco(t.saida, "terminal")') == 1
```

`roda_realce_js(trechos) -> list[str]` e `roda_pedacos(texto) -> list[tuple[str, str]]` moram em `test_interface.py`, como os de `tema.js`: escrevem a entrada num JSON temporário, fazem `require` de `realce.js` pelo Node e leem a resposta (pedaços de tipo `""` ficam fora de `roda_pedacos`).

- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** `realce.js` (carregável pelo Node como `tema.js`) e o `bloco` novo: classe ausente ou `"codigo"` → `pre.codigo` com `Realce.preenche`; qualquer outra classe (`"terminal"`) → `textContent`, como hoje. Sem `window.Realce`, `textContent`.
- [ ] **Step 4: Run** `python -m pytest mvp/test_interface.py mvp/test_trilha_telas.py -q` — Expected: PASS.
- [ ] **Step 5: Commit** — "O codigo aparece em cores, e o texto continua identico".

### Task 4: O topo da trilha

**Files:**
- Modify: `mvp/web/trilha.html:13-20` (topo), `mvp/web/trilha.js:253-271` (`desenhaProgresso`) e a carga inicial
- Test: `mvp/test_interface.py`

**Interfaces:**
- Consumes: Task 2 (`Tema.liga`, `--marca-*`).
- Produces: no topo, `a.t-marca` (logo em SVG inline, `href="/"`, `aria-label="Structura — voltar aos tópicos"`), `span#topico-nome`, `ol#progresso` com um `li` por ideia, e `button#btn-tema`.

O link "← tópicos" vira o logo (que leva ao mesmo lugar). O nome do tópico vem de `GET BASE + "/saude"` (campo `titulo`), uma vez, ao abrir. Cada `li` das paradas tem o número da ideia como texto e `aria-label="Ideia N: <estado>"`, com estado `feita`, `em aberto`, `agora` ou `ainda não`; as classes `t-bem`, `t-aberto`, `t-atual` continuam (os testes do ramo leem `progresso`).

- [ ] **Step 1: Write the failing test:**

```python
def test_o_topo_tem_o_logo_o_topico_as_paradas_e_o_tema():
    html, js = (WEB / "trilha.html").read_text(encoding="utf-8"), (WEB / "trilha.js").read_text(encoding="utf-8")
    assert 'class="t-marca"' in html and 'href="/"' in html and "<svg" in html
    assert 'id="topico-nome"' in html and 'id="btn-tema"' in html
    assert '"/saude"' in js and "Tema.liga" in js
    progresso = re.search(r"function desenhaProgresso\(.*?\n  \}", js, re.S).group(0)
    for estado in ("feita", "em aberto", "agora", "ainda não"):
        assert estado in progresso, estado
    assert "aria-label" in progresso and "Ideia " in progresso
```

- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** o topo e as paradas (círculos numerados ligados por fio, como no esboço 5; o `li` atual com brilho no escuro).
- [ ] **Step 4: Run** `python -m pytest mvp/test_interface.py mvp/test_trilha_telas.py mvp/test_trilha_diagnostico.py -q` — Expected: PASS.
- [ ] **Step 5: Commit** — "O topo da trilha: logo, topico, paradas e tema".

### Task 5: As telas da trilha na roupa nova

**Files:**
- Modify: `mvp/web/tema.css` (peças), `mvp/web/trilha.css` só se uma regra dele impedir o tema (preferir sobrescrever em `tema.css`)
- Test: `mvp/test_interface.py`

**Interfaces:**
- Consumes: Tasks 2–4.

O que cada peça ganha, nos dois temas (esboços 4 e 5): cartão com cantos 18 e sombra; `.etiqueta` em JetBrains Mono, sem caixa alta, com `// ` antes no escuro e `/* ` … ` */` em volta no claro (pseudo-elementos — o texto do elemento não muda); `.codigo` como moldura de editor (fundo `--editor`, três pontinhos num `::before` posicionado, rolagem horizontal dentro); `.terminal` como saída de terminal; `.opcao`, `.conf`, `.t-peca` com borda de 2 px e o marcado com brilho no escuro; `.btn` com `--botao`/`--botao-tinta` (degradê e brilho no escuro, laranja com sombra embaixo no claro); `.t-retorno.certo` com o sinal de certo entrando numa animação curta (só com movimento permitido); `.t-previu`, `.t-sumario`, `.t-fala`, `.t-caixa`, `.t-fundo`/`.t-painel`, `.t-aviso` com as cores do tema.

- [ ] **Step 1: Write the failing test:**

```python
def test_o_tema_veste_cada_peca_das_telas():
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    for seletor in (".cartao", ".etiqueta", ".codigo", ".terminal", ".opcao", ".conf",
                    ".t-peca", ".btn", ".t-retorno", ".t-previu", ".t-sumario", ".t-painel"):
        assert seletor in css, seletor
    assert re.search(r'data-tema="escuro"\][^{]*\.etiqueta::before\s*\{[^}]*content:\s*"// "', css)
```

- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** as peças em `tema.css`.
- [ ] **Step 4: Run** `python -m pytest mvp/test_interface.py mvp/test_trilha_telas.py -q` — Expected: PASS.
- [ ] **Step 5: Conferir no navegador** (ensaio, 8013), nos dois temas, em 360 px e em 1280 px, levando uma sessão do kc_06 com `scratchpad/mostra_sessao.py` até cada tipo de tela — entrada, pergunta, degrau (tocar, montar, completar, digitar), retorno, você disse, máquina, revisão, mapa — e o painel de explicação; uma captura de cada. Conferir o item 3 do Review Focus (linha longa rola dentro da moldura) e `resize_window` de volta ao normal no fim.
- [ ] **Step 6: Commit** — "As telas da trilha na identidade nova".

### Task 6: A página inicial na roupa nova (ainda em lista)

**Files:**
- Modify: `mvp/web/portal.html`
- Test: `mvp/test_interface.py`

**Interfaces:**
- Consumes: Tasks 1–2.

O topo ganha o logo, o campo do código do participante (o mesmo `input#codigo`, mesma validação e a mesma nota) e a troca de tema; abaixo, o título "Ponteiros em C, uma ideia de cada vez" e uma frase do que o sistema faz (texto do esboço 4, tela 1); a lista de tópicos vira cartões no estilo novo, com o mesmo comportamento de hoje (`t.trilha`, `t.caminho`, "versão anterior", "já aberto"). O caminho desenhado é a fatia 2.

- [ ] **Step 1: Write the failing test:**

```python
def test_a_pagina_inicial_tem_o_logo_o_titulo_e_o_tema():
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    assert "<svg" in html and 'id="btn-tema"' in html and 'id="codigo"' in html
    assert "Ponteiros em C, uma ideia de cada vez" in html
```

- [ ] **Step 2: Run** — Expected: FAIL. (Os testes de `test_trilha_portal.py` e `test_portal.py` continuam passando antes e depois.)
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `python -m pytest mvp/test_interface.py mvp/test_trilha_portal.py mvp/test_portal.py -q` — Expected: PASS.
- [ ] **Step 5: Conferir no navegador** nos dois temas, em 360 px e em 1280 px; o link de um tópico com código preenchido leva a `?codigo=…` como antes.
- [ ] **Step 6: Commit** — "A pagina inicial na identidade nova".

### Task 7: Fechar a fatia

**Files:**
- Modify: `docs/interface.md` (seção 9: fatia 1 feita, com o que mudou do plano), `docs/trilha.md` só se algo da sessão tiver mudado (não deve)

- [ ] **Step 1: Run** a suíte inteira em segundo plano: `python -m pytest -q -p no:cacheprovider > <scratchpad>/suite_interface.txt`. Expected: tudo passa, exceto os dois testes de `mvp/test_procedimentos.py` que precisam da porta 8010 livre, se o contêiner estiver no ar.
- [ ] **Step 2:** conferir a hora da última escrita em `coleta/portal/trilha/`; se ninguém está jogando, parar o contêiner, rodar `python -m pytest mvp/test_procedimentos.py -q` (Expected: 27 passed) e reconstruir: `docker compose up -d --build`. Conferir só `GET /saude` e `GET /`.
- [ ] **Step 3: Commit** — "Interface, fatia 1: a identidade e as telas", com o resultado da suíte e a lista de testes do ramo alterados.
- [ ] **Step 4:** mandar ao Rafael capturas das telas nos dois temas, e dizer o que ele pode olhar no sistema no ar.
