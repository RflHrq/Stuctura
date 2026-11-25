# Apresentação da defesa — plano

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** os 22 slides da defesa em HTML, com os passos do sistema interativos, cada slide referenciado na numeração do PDF e conferido contra a monografia por teste.

**Architecture:** um deck estático em `apresentacao/` (HTML, CSS e JS próprios, sem biblioteca), que usa por caminho relativo a identidade e a cena de `mvp/web/`. Dois arquivos de dados gerados por script: as referências do PDF (lidas dos `.toc`, `.lof` e `.loq` do LaTeX) e a cena da Figura 5. Um conferidor em Python lê o deck e acusa referência, número ou frase que a monografia não tem.

**Tech Stack:** HTML, CSS e JavaScript puros; Python 3 e pytest; Chrome sem janela (CDP, como `scripts/figuras_monografia.py`) para o PDF.

**Spec:** `docs/apresentacao.md`

## Global Constraints

- Tudo o que o slide explica está na monografia do commit `cf51987`, com a referência na numeração do PDF: Quadro 1 a 24, Figura 1 a 6, Seções 1 a 8, Apêndices A a C.
- Número ou frase entre aspas do texto aparece como o texto diz.
- Nenhuma afirmação nova sobre o sistema, nenhum resultado com estudantes, nenhum número medido depois da entrega.
- 22 slides, para 30 minutos.
- Abre sem internet: nenhum recurso de endereço externo.
- Teclas: → e espaço avançam, ← volta, F tela cheia.

## Review Focus

1. Passador de slides (controle remoto): manda PageDown/PageUp, e não seta. Avança e volta como → e ←.
2. Projetor em 1366×768 ou 1024×768: o slide é 16:9 e encolhe para caber, sem cortar nada.
3. Aberto direto do arquivo (`file://`), sem servidor: scripts e imagens por caminho relativo carregam.
4. Voltar (←) num slide interativo desfaz o último passo revelado, e não pula o slide.
5. Monografia recompilada com outra numeração: o teste falha, em vez de o slide citar uma página errada.

---

### Task 1: O conferidor e os dados gerados

**Files:**
- Create: `scripts/confere_apresentacao.py`
- Create: `mvp/test_apresentacao.py`
- Create (gerados pelo script): `apresentacao/referencias.js`, `apresentacao/cena.js`

**Interfaces:**
- Produces:
  - `referencias_do_pdf(pasta_latex: Path) -> dict[str, int]`: chaves "Seção 3.3", "Seção 3", "Quadro 3", "Figura 1", "Apêndice C"; valor é a página.
  - `slides(html: str) -> list[Slide]`, `Slide(numero: int, refs: list[str], texto: str, aspas: list[str])`. A referência vem do atributo `data-ref` do `<section class="slide">`, separada por " · ".
  - `problemas(html: str, refs_pdf: dict, monografia: str) -> list[str]`; vazia = passou.
  - `main(["--gera"])` escreve `apresentacao/referencias.js` (`window.REFS = {...}`) e `apresentacao/cena.js` (`window.CENA = {cena, codigo}`, da escada do kc_06, premissa B1, por `trilha.cena_json`).

- [ ] **Step 1: testes que falham**, em `mvp/test_apresentacao.py`, com um deck mínimo montado no próprio teste:
  - `test_a_referencia_que_o_pdf_nao_tem_e_acusada`: `data-ref="Quadro 30"` dá um problema que cita "Quadro 30".
  - `test_o_numero_que_a_monografia_nao_tem_e_acusado`: "4 321 testes" dá problema; "7 568 testes" não.
  - `test_a_frase_entre_aspas_que_a_monografia_nao_tem_e_acusada`: idem com uma frase inventada e com "A máquina respondeu".
  - `test_as_referencias_do_pdf`: `refs["Quadro 3"] == 30`, `refs["Figura 1"] == 29`, `refs["Seção 1.1"] == 14`, `refs["Apêndice C"] == 80`.
  - `test_a_cena_do_deck_e_a_do_sistema`: o JSON em `apresentacao/cena.js` é igual a `trilha.cena_json` da escada do kc_06, B1.
- [ ] **Step 2:** rodar `python -m pytest mvp/test_apresentacao.py -q -p no:cacheprovider`; falham por falta do módulo.
- [ ] **Step 3:** implementar. Monografia = o texto dos `.md` de `docs/monografia/` (00 a 08, curadoria e apêndices), com espaços normalizados. Número = sequência de dígitos com espaço de milhar ("1 098"); aceito se aparece, como palavra, no texto. Aspas = trechos entre “ ” ou " " no texto visível do slide. Ficam fora da conferência o rodapé, as notas do apresentador (`<aside class="notas">`) e os blocos `<pre>` de código, que vêm do sistema.
- [ ] **Step 4:** testes passam; rodar `python scripts/confere_apresentacao.py --gera`.
- [ ] **Step 5:** commit.

### Task 2: O deck

**Files:**
- Create: `apresentacao/index.html`, `apresentacao/deck.css`, `apresentacao/deck.js`
- Test: `mvp/test_apresentacao.py`

**Interfaces:**
- Consumes: `window.REFS`, `window.CENA`, `Cena.desenha(cena, codigo)` e `Realce` de `mvp/web/`.
- Produces: `<section class="slide" data-ref="...">`; elementos com `data-passo="N"` são revelados em ordem; `?pdf=1` revela tudo e põe um slide por página.

- [ ] **Step 1: testes que falham**:
  - `test_sao_22_slides`
  - `test_todo_slide_tem_referencia_menos_capa_e_fim` (slides 1 e 22 sem `data-ref`)
  - `test_o_deck_nao_carrega_nada_de_fora` (nenhum `src`/`href` com `http`)
  - `test_toda_imagem_e_script_do_deck_existe` (caminhos relativos resolvidos a partir de `apresentacao/`)
  - `test_o_deck_passa_no_conferidor` (`problemas(...) == []` no deck real)
- [ ] **Step 2:** falham.
- [ ] **Step 3:** escrever o deck pelo roteiro de `docs/apresentacao.md`. Texto tirado da monografia; rodapé "Seção 3.3 · Quadro 3, p. 30" montado de `data-ref` e `REFS`. Navegação: → espaço PageDown avançam; ← PageUp voltam (desfazendo o último passo revelado); Home/End; F tela cheia; N mostra as notas. Slide 16:9 escalado para caber na janela. Interativos: 8 (pergunta, razão e certeza aparecem uma por vez sobre a Figura 1), 9 (as linhas do Quadro 3 acendem uma a uma), 10, 11 e 13 (figuras em etapas), 12 (a cena viva).
- [ ] **Step 4:** testes passam; abrir no navegador interno, percorrer os 22 slides e conferir na tela, inclusive em 1366×768.
- [ ] **Step 5:** commit.

### Task 3: O PDF de reserva

**Files:**
- Create: `scripts/apresentacao_pdf.py`
- Create (gerado, fora do git): `entrega/apresentacao.pdf`

- [ ] **Step 1:** imprimir `apresentacao/index.html?pdf=1` por Chrome sem janela (CDP `Page.printToPDF`, paisagem 16:9).
- [ ] **Step 2:** conferir: 22 páginas, cada uma com o rodapé de referência.
- [ ] **Step 3:** commit do script; varredura de segredos; `git push origin trilha`.
