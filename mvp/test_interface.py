"""A interface nova da trilha e da página inicial (docs/interface.md).

O que dá para conferir lendo os arquivos e rodando os scripts da página
no Node: as fontes e o ícone estão no projeto, com licença; nada é
carregado de outro endereço; os dois temas passam no contraste; o tema é
escolhido antes de a página aparecer, mesmo sem `localStorage`; o realce
de código devolve o texto idêntico; e cada peça das telas está vestida.

O resto — se o desenho ficou como nos esboços — é conferência no
navegador, nos passos do plano (docs/plano-interface.md).
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
WEB = RAIZ / "web"
FONTES = WEB / "fontes"
sys.path.insert(0, str(RAIZ.parent))

from mvp import trilha_escada  # noqa: E402
from mvp.dominio import carrega, topicos  # noqa: E402

NODE = shutil.which("node")
tem_node = pytest.mark.skipif(NODE is None, reason="sem node para rodar o JavaScript")


def _roda_node(programa: str) -> str:
    """Roda um programa no Node, de uma pasta temporária, e devolve o que
    ele imprimiu. O programa recebe o caminho de `mvp/web` em `WEB`."""
    with tempfile.TemporaryDirectory() as tmp:
        arquivo = pathlib.Path(tmp) / "roda.js"
        arquivo.write_text("const WEB = %s;\n%s" % (json.dumps(str(WEB)), programa),
                           encoding="utf-8")
        saiu = subprocess.run([NODE, str(arquivo)], capture_output=True,
                              text=True, encoding="utf-8", timeout=60)
    assert saiu.returncode == 0, saiu.stderr
    return saiu.stdout.strip()


# --------------------------------------------------------------------------
# As fontes e o ícone
# --------------------------------------------------------------------------

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


# --------------------------------------------------------------------------
# Os dois temas e a troca
# --------------------------------------------------------------------------

PARES = [("tinta", "papel"), ("tinta", "cartao"), ("tinta2", "cartao"),
         ("acento", "cartao"), ("ok", "ok-fundo"), ("erro", "erro-fundo"),
         ("aviso", "aviso-fundo"), ("botao-tinta", "botao"),
         ("topo-tinta", "topo"), ("editor-tinta", "editor"),
         ("sx-palavra", "editor"), ("sx-numero", "editor"), ("sx-funcao", "editor"),
         ("sx-texto", "editor"), ("sx-comentario", "editor"),
         # o topo e as paradas (Task 4)
         ("topo-tinta2", "topo"), ("parada-ok-tinta", "parada-ok"),
         ("parada-agora-tinta", "parada-agora"),
         ("parada-aberta-tinta", "parada-aberta"),
         # as peças das telas (Task 5)
         ("etiqueta", "cartao"), ("etiqueta", "cartao-baixo"), ("tinta", "campo"),
         ("tinta", "acento-fundo"), ("tinta", "destaque-fundo"),
         ("terminal-tinta", "terminal"), ("botao-tinta", "botao-fim")]


def cores_do_tema(tema: str) -> dict[str, str]:
    """As variáveis `--nome: #rrggbb` do bloco `html[data-tema="<tema>"]`
    de tema.css (o primeiro bloco com esse seletor)."""
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    m = re.search(r'html\[data-tema="%s"\][^{]*\{([^}]*)\}' % tema, css)
    assert m, "tema.css não tem o bloco do tema %s" % tema
    return dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\b", m.group(1)))


def contraste(frente: str, fundo: str) -> float:
    """A razão de contraste da WCAG 2.x, entre duas cores #rrggbb."""
    def luminancia(cor):
        canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
               for c in canais]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    a, b = sorted((luminancia(frente), luminancia(fundo)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def test_a_formula_do_contraste_e_a_da_wcag():
    assert round(contraste("#000000", "#ffffff"), 1) == 21.0
    assert round(contraste("#777777", "#ffffff"), 2) == 4.48


@pytest.mark.parametrize("tema", ["claro", "escuro"])
def test_os_dois_temas_passam_no_contraste(tema):
    cores = cores_do_tema(tema)
    for frente, fundo in PARES:
        assert frente in cores and fundo in cores, (tema, frente, fundo)
        assert contraste(cores[frente], cores[fundo]) >= 4.5, (
            tema, frente, fundo, round(contraste(cores[frente], cores[fundo]), 2))


def test_sem_javascript_o_sistema_escuro_usa_o_mesmo_escuro():
    """Sem JavaScript não há `data-tema`, e o escuro do sistema entra por
    `@media`. O CSS obriga a repetir as cores ali; este teste não deixa
    a cópia ficar diferente do original."""
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    m = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*"
                  r"html:not\(\[data-tema\]\)\s*\{([^}]*)\}", css)
    assert m, "tema.css não tem o escuro para quem está sem JavaScript"
    sem_js = dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\b", m.group(1)))
    assert sem_js == cores_do_tema("escuro")


def test_nada_e_carregado_de_outro_endereco():
    for f in WEB.glob("*.*"):
        if f.suffix in (".html", ".css", ".js"):
            txt = f.read_text(encoding="utf-8")
            assert not re.search(
                r'(?:src|href)\s*=\s*"https?://|url\(\s*["\']?https?://', txt), f.name


def test_reduzir_movimento_desliga_animacao():
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    bloco = re.search(r"prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\n\}", css, re.S)
    assert bloco, "tema.css não tem o bloco de reduzir movimento"
    assert "animation: none" in bloco.group(1)
    assert "transition: none" in bloco.group(1)


def roda_tema_js(guardado, sistema_escuro: bool, armazenamento: str) -> str:
    """Carrega tema.js no Node, com uma página de mentira, e devolve o
    `data-tema` que ele pôs em <html>."""
    programa = """
    const atributos = {};
    const guardado = %s;
    const quebrado = %s;
    global.window = global;
    global.document = { documentElement: {
        setAttribute(k, v) { atributos[k] = v; },
        getAttribute(k) { return atributos[k]; } } };
    global.matchMedia = (q) => ({ matches: %s && q.includes("dark") });
    Object.defineProperty(global, "localStorage", { get() {
        if (quebrado) throw new Error("bloqueado");
        return { getItem: () => guardado, setItem: () => {} }; } });
    require(require("path").join(WEB, "tema.js"));
    console.log(atributos["data-tema"]);
    """ % (json.dumps(guardado), json.dumps(armazenamento == "quebrado"),
           "true" if sistema_escuro else "false")
    return _roda_node(programa)


@tem_node
@pytest.mark.parametrize("guardado, sistema_escuro, armazenamento, esperado", [
    (None, True, "ok", "escuro"), (None, False, "ok", "claro"),
    ("claro", True, "ok", "claro"), ("escuro", False, "ok", "escuro"),
    (None, True, "quebrado", "escuro"),     # localStorage que lança erro
    ("roxo", False, "ok", "claro"),         # valor guardado que não é tema
])
def test_o_tema_e_escolhido_antes_da_pagina(guardado, sistema_escuro,
                                            armazenamento, esperado):
    assert roda_tema_js(guardado, sistema_escuro, armazenamento) == esperado


@tem_node
def test_o_botao_de_tema_troca_uma_vez_por_clique():
    """tema.js liga #btn-tema sozinho quando a página chega. Ligar de novo
    o mesmo botão não pode pôr um segundo ouvinte: com dois, cada clique
    trocaria duas vezes e o tema não mudaria. E o texto do botão, que a
    página escreve, fica como está."""
    programa = """
    const atributos = {};
    const ouvintes = {};
    const guardados = [];
    global.window = global;
    const botao = { atributos: {}, textContent: "Tema escuro", cliques: [],
        setAttribute(k, v) { this.atributos[k] = v; },
        getAttribute(k) { return this.atributos[k]; },
        addEventListener(e, f) { if (e === "click") this.cliques.push(f); } };
    global.document = {
        documentElement: { setAttribute(k, v) { atributos[k] = v; },
                           getAttribute(k) { return atributos[k]; } },
        addEventListener(e, f) { ouvintes[e] = f; },
        getElementById: (id) => (id === "btn-tema" ? botao : null) };
    global.matchMedia = () => ({ matches: false });
    Object.defineProperty(global, "localStorage", { configurable: true, get() {
        return { getItem: () => null, setItem: (k, v) => guardados.push([k, v]) }; } });
    require(require("path").join(WEB, "tema.js"));
    ouvintes.DOMContentLoaded();
    window.Tema.liga(botao);
    const antes = [atributos["data-tema"], botao.atributos["aria-pressed"]];
    botao.cliques.forEach((f) => f());
    console.log(JSON.stringify({ antes, ouvintes: botao.cliques.length, guardados,
        depois: [atributos["data-tema"], botao.atributos["aria-pressed"]],
        texto: botao.textContent }));
    """
    r = json.loads(_roda_node(programa))
    assert r["antes"] == ["claro", "false"]
    assert r["ouvintes"] == 1
    assert r["depois"] == ["escuro", "true"]
    assert r["guardados"] == [["structura-tema", "escuro"]]
    assert r["texto"] == "Tema escuro"


def test_as_duas_paginas_carregam_o_tema_no_head():
    for pagina in ("trilha.html", "portal.html"):
        html = (WEB / pagina).read_text(encoding="utf-8")
        cabeca = html.split("</head>")[0]
        assert "/web/tema.js?v=20261116" in cabeca, pagina
        assert "/web/tema.css?v=20261116" in cabeca, pagina
        assert cabeca.index("tema.js") < cabeca.index("style.css"), pagina
        assert cabeca.index("tema.css") > cabeca.index("style.css"), pagina
        assert 'rel="icon"' in cabeca and "/web/marca.svg?v=20261116" in cabeca, pagina
        assert 'id="btn-tema"' in html, pagina


# --------------------------------------------------------------------------
# O realce de código
# --------------------------------------------------------------------------

def _todos_os_trechos() -> list[str]:
    """Todo código que a trilha mostra: revisão, passos e provas, nos
    tópicos com escada."""
    trechos: list[str] = []
    for topico in topicos():
        arquivo = RAIZ / "dominio" / ("escada_%s.yaml" % topico.replace("_", ""))
        if not arquivo.exists():
            continue
        for esc in trilha_escada.le(arquivo, carrega(topico=topico)).values():
            trechos.append(esc.revisao.codigo)
            for degrau in esc.degraus:
                for v in degrau.versoes:
                    trechos += [v.mostra, v.antes, v.programa, v.certa_texto]
            trechos += [prova.programa for prova in esc.provas]
    return [t for t in trechos if t.strip()]


def roda_realce_js(trechos: list[str]) -> list[str]:
    """Passa cada trecho por `Realce.pedacos` no Node e devolve os pedaços
    de cada um juntados de volta."""
    programa = """
    global.window = global;
    require(require("path").join(WEB, "realce.js"));
    const entrada = %s;
    console.log(JSON.stringify(entrada.map(
        (t) => window.Realce.pedacos(t).map((p) => p.texto).join(""))));
    """ % json.dumps(trechos)
    return json.loads(_roda_node(programa))


def roda_pedacos(texto: str) -> list[tuple[str, str]]:
    """Os pedaços com tipo de um trecho; os de tipo "" ficam de fora."""
    programa = """
    global.window = global;
    require(require("path").join(WEB, "realce.js"));
    console.log(JSON.stringify(window.Realce.pedacos(%s)
        .filter((p) => p.tipo).map((p) => [p.tipo, p.texto])));
    """ % json.dumps(texto)
    return [tuple(p) for p in json.loads(_roda_node(programa))]


@tem_node
def test_o_realce_devolve_o_texto_identico():
    trechos = _todos_os_trechos()
    assert len(trechos) > 500
    assert roda_realce_js(trechos) == trechos


@tem_node
def test_o_realce_reconhece_cada_peca():
    pedacos = roda_pedacos('void f(int n) { n = 99; printf("%d\\n", n); } // fim')
    assert ("palavra", "void") in pedacos and ("funcao", "f") in pedacos
    assert ("numero", "99") in pedacos and ("texto", '"%d\\n"') in pedacos
    assert ("funcao", "printf") in pedacos and ("comentario", "// fim") in pedacos
    assert roda_pedacos('"a // b"') == [("texto", '"a // b"')]


@tem_node
def test_o_realce_nao_ve_nada_dentro_de_comentario_nem_de_texto():
    assert roda_pedacos("/* int 5 f() */ x") == [("comentario", "/* int 5 f() */")]
    assert roda_pedacos("'\\''") == [("texto", "'\\''")]
    assert roda_pedacos('"a\\"b" 0x1F') == [("texto", '"a\\"b"'), ("numero", "0x1F")]
    # palavra-chave dentro de um nome maior não é palavra-chave
    assert roda_pedacos("inteiro = sizeof (x);") == [("palavra", "sizeof")]
    assert roda_pedacos("print (x)") == [("funcao", "print")]


@tem_node
def test_preenche_monta_o_bloco_com_nos_de_texto():
    """Código tem `<` e `&`: o bloco é montado com nós, nunca com HTML."""
    js = (WEB / "realce.js").read_text(encoding="utf-8")
    assert "innerHTML" not in js
    programa = """
    global.window = global;
    const no = (tag) => ({ tag, className: "", textContent: "", filhos: [],
        appendChild(f) { this.filhos.push(f); return f; } });
    global.document = { createElement: no,
        createTextNode: (t) => ({ tag: "#texto", textContent: t }) };
    require(require("path").join(WEB, "realce.js"));
    const pre = no("pre");
    pre.textContent = "velho";
    window.Realce.preenche(pre, %s);
    console.log(JSON.stringify(pre.filhos.map((f) => [f.tag, f.className || "", f.textContent])));
    """ % json.dumps("int *p = &x; // a<b")
    filhos = json.loads(_roda_node(programa))
    assert "".join(f[2] for f in filhos) == "int *p = &x; // a<b"
    assert ["span", "sx-palavra", "int"] in filhos
    assert ["span", "sx-comentario", "// a<b"] in filhos
    assert all(f[0] in ("span", "#texto") for f in filhos)


def test_o_codigo_colorido_fica_no_fundo_de_editor():
    """O contraste das cores do realce foi medido contra --editor; então
    todo bloco de código, inclusive o do retorno, fica nesse fundo."""
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    regra = re.search(r"\.codigo, \.t-retorno \.codigo \{([^}]*)\}", css)
    assert regra, "tema.css não põe o código no fundo de editor"
    assert "background: var(--editor)" in regra.group(1)
    assert "color: var(--editor-tinta)" in regra.group(1)
    for tipo in ("palavra", "numero", "funcao", "texto", "comentario"):
        assert re.search(r"\.sx-%s \{[^}]*color: var\(--sx-%s\)" % (tipo, tipo), css), tipo


def test_so_o_codigo_e_colorido_e_a_saida_nao():
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    corpo = re.search(r"function bloco\(texto, classe\) \{(.*?)\n  \}", js, re.S).group(1)
    assert "Realce.preenche" in corpo          # o código é colorido
    assert "textContent" in corpo              # a saída, e a falta do realce, não
    assert '"codigo"' in corpo                 # quem decide é a classe do bloco
    # e as saídas continuam chegando com a classe delas
    assert js.count('bloco(t.espera, "terminal")') == 1
    assert js.count('bloco(t.saida, "terminal")') == 1


def test_a_trilha_carrega_o_realce_antes_do_proprio_script():
    html = (WEB / "trilha.html").read_text(encoding="utf-8")
    assert "/web/realce.js?v=20261116" in html
    assert html.index("realce.js") < html.index("trilha.js")


# --------------------------------------------------------------------------
# O topo da trilha
# --------------------------------------------------------------------------

def test_o_topo_tem_o_logo_o_topico_as_paradas_e_o_tema():
    html = (WEB / "trilha.html").read_text(encoding="utf-8")
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    topo = re.search(r'<header class="topo t-topo">(.*?)</header>', html, re.S).group(1)
    assert 'class="t-marca"' in topo and 'href="/"' in topo and "<svg" in topo
    assert 'aria-label="Structura — voltar aos tópicos"' in topo
    assert 'id="topico-nome"' in topo and 'id="btn-tema"' in topo
    assert "← tópicos" not in html
    # O botão de tema é ligado por tema.js (test_o_botao_de_tema_troca_uma_vez_por_clique).
    assert '"/saude"' in js and '$("topico-nome")' in js
    progresso = re.search(r"function desenhaProgresso\(.*?\n  \}", js, re.S).group(0)
    for estado in ("feita", "em aberto", "agora", "ainda não"):
        assert estado in progresso, estado
    assert "aria-label" in progresso and "Ideia " in progresso
    # as classes de antes continuam: os testes do ramo e trilha.css as usam
    for classe in ("t-bem", "t-aberto", "t-atual"):
        assert classe in progresso, classe


def test_em_tela_estreita_o_topo_cabe_ate_com_oito_paradas():
    """O kc_09 tem 8 ideias. Em 360 px, com o botão Ajustes à mostra, o
    topo só cabe se os dois botões ficarem só com o desenho — o texto
    continua neles, escondido da vista, para o leitor de tela."""
    html = (WEB / "trilha.html").read_text(encoding="utf-8")
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    for id_ in ("btn-tema", "btn-ajustes"):
        botao = re.search(r'<button[^>]*id="%s"[^>]*>(.*?)</button>' % id_, html, re.S)
        assert botao, id_
        assert 'class="t-btn-icone" aria-hidden="true"' in botao.group(1), id_
        assert 'class="t-btn-texto"' in botao.group(1), id_
    estreita = re.search(r"@media \(max-width: 560px\) \{(.*?)\n\}", css, re.S).group(1)
    assert re.search(r"\.t-btn-texto \{[^}]*clip-path: inset\(50%\)", estreita)


# --------------------------------------------------------------------------
# As telas da trilha na roupa nova
# --------------------------------------------------------------------------

def test_o_tema_veste_cada_peca_das_telas():
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    for seletor in (".cartao", ".etiqueta", ".codigo", ".terminal", ".opcao", ".conf",
                    ".t-peca", ".btn", ".t-retorno", ".t-previu", ".t-sumario", ".t-painel"):
        assert seletor in css, seletor
    assert re.search(r'data-tema="escuro"\][^{]*\.etiqueta::before\s*\{[^}]*content:\s*"// "', css)
    assert re.search(r'data-tema="claro"\][^{]*\.etiqueta::before\s*\{[^}]*content:\s*"/\* "', css)
    assert re.search(r'data-tema="claro"\][^{]*\.etiqueta::after\s*\{[^}]*content:\s*" \*/"', css)
    # O cabeçalho do cartão era flex com space-between: o "/* " e o " */"
    # iriam parar nas pontas do cartão.
    assert re.search(r"\.t-cartao > \.etiqueta \{[^}]*display: block", css)


@pytest.mark.parametrize("tema", ["claro", "escuro"])
def test_o_buraco_do_completar_se_le_dentro_do_editor(tema):
    """O buraco fica dentro do bloco de código, no fundo de editor; com a
    cor do acento, no claro, ele quase sumia (#17708a sobre #1b2630)."""
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    regra = re.search(r"\.codigo \.t-buraco \{([^}]*)\}", css)
    assert regra, "tema.css não dá cor ao buraco dentro do código"
    cor = re.search(r"(?<!-)color: var\(--([a-z0-9-]+)\)", regra.group(1)).group(1)
    cores = cores_do_tema(tema)
    assert contraste(cores[cor], cores["editor"]) >= 4.5, (tema, cor)


def test_a_pagina_inicial_tem_o_logo_o_titulo_e_o_tema():
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    assert "<svg" in html and 'id="btn-tema"' in html and 'id="codigo"' in html
    assert "Ponteiros em C, uma ideia de cada vez" in html
    # o campo do código vai para o topo, com o rótulo e a nota de antes
    topo = re.search(r'<header class="topo[^"]*">(.*?)</header>', html, re.S).group(1)
    assert 'id="codigo"' in topo and 'for="codigo"' in topo
    assert 'aria-describedby="nota"' in topo and 'id="nota"' in html
    # a ordem sugerida é a fatia 2: a frase não promete o que a lista não faz
    assert "ordem sugerida" not in html


def test_o_sinal_de_certo_so_anima_com_movimento_permitido():
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    assert "@keyframes" in css
    fora = re.sub(r"@media \(prefers-reduced-motion: no-preference\) \{.*?\n\}", "", css,
                  flags=re.S)
    fora = re.sub(r"@media \(prefers-reduced-motion: reduce\) \{.*?\n\}", "", fora, flags=re.S)
    assert not re.search(r"animation(-name)?\s*:", fora), "animação fora do bloco permitido"
    assert re.search(r"no-preference\) \{.*?\.t-retorno\.certo .*?animation:", css, re.S)
