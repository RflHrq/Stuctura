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
import tempfile

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
WEB = RAIZ / "web"
FONTES = WEB / "fontes"

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
         ("sx-texto", "editor"), ("sx-comentario", "editor")]


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
