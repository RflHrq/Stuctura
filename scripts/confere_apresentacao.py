"""Os slides da defesa contra a monografia entregue (docs/apresentacao.md).

    python scripts/confere_apresentacao.py          # confere; sai com 1 se houver problema
    python scripts/confere_apresentacao.py --gera   # escreve referencias.js e cena.js

A regra do deck é a da monografia: nada é afirmado que o texto não diga.
Cada slide declara em `data-ref` onde o que ele explica está, na
numeração do PDF (Quadro 1 a 24, Figura 1 a 6, Seções e Apêndices). O
conferidor acusa:

  - a referência que o PDF não tem (lida dos .toc, .lof e .loq do LaTeX,
    que também dão a página do rodapé);
  - o número que o texto da monografia não traz;
  - a frase entre aspas que o texto da monografia não contém.

Ficam fora: o rodapé (que o deck monta das referências), as notas do
apresentador (`<aside class="notas">`, fala de quem apresenta, e não
tela) e os blocos `<pre>` (código que vem do sistema).
"""

from __future__ import annotations

import html.parser
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MONOGRAFIA = RAIZ / "docs" / "monografia"
LATEX = MONOGRAFIA / "latex"
DECK = RAIZ / "apresentacao"

_LINHA = re.compile(
    r"\\contentsline \{(?P<tipo>chapter|section|subsection|appendix|figure|quadro)\}"
    r"\{(?:\\chapternumberline|\\numberline) \{(?P<num>[^}]+)\}"
    r".*\}\{(?P<pag>\d+)\}\{[^}]*\}%\s*$")


def referencias_do_pdf(pasta: pathlib.Path) -> dict[str, int]:
    """"Seção 3.3", "Quadro 3", "Figura 1", "Apêndice C" -> página."""
    refs: dict[str, int] = {}
    for sufixo in ("toc", "lof", "loq"):
        arquivo = pasta / ("TCC_STRUCTURA." + sufixo)
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            m = _LINHA.search(linha)
            if not m:
                continue
            tipo, num, pag = m.group("tipo"), m.group("num"), int(m.group("pag"))
            nome = {"figure": "Figura", "quadro": "Quadro",
                    "appendix": "Apêndice"}.get(tipo, "Seção")
            refs.setdefault("%s %s" % (nome, num), pag)
    return refs


def _normaliza(t: str) -> str:
    t = t.replace("“", '"').replace("”", '"').replace("’", "'")
    t = re.sub(r"[*`]", "", t)
    return " ".join(t.split())


def texto_da_monografia(pasta: pathlib.Path) -> str:
    partes = sorted(pasta.glob("0*.md")) + [pasta / "curadoria.md"] + sorted(
        pasta.glob("apendice*.md"))
    return _normaliza(" ".join(p.read_text(encoding="utf-8") for p in partes))


@dataclass
class Slide:
    numero: int
    refs: list[str]
    texto: str = ""
    aspas: list[str] = field(default_factory=list)


class _Leitor(html.parser.HTMLParser):
    FORA = {"pre", "footer", "script", "style"}
    BLOCO = {"p", "li", "td", "th", "tr", "div", "h1", "h2", "h3", "small",
             "blockquote", "cite", "br", "figure", "table", "ul"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides: list[Slide] = []
        self._pilha: list[tuple[str, bool]] = []
        self._fora = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "section" and "slide" in classes:
            refs = [r.strip() for r in (a.get("data-ref") or "").split("·")
                    if r.strip()]
            self.slides.append(Slide(len(self.slides) + 1, refs))
        fora = tag in self.FORA or (tag == "aside" and "notas" in classes)
        # Bloco novo, linha nova: o "5" de uma célula e o "402" do parágrafo
        # seguinte não podem virar o milhar "5 402".
        if self.slides and tag in self.BLOCO:
            self.slides[-1].texto += "\n"
        if tag in ("br", "img", "meta", "link", "input"):
            return
        self._pilha.append((tag, fora))
        if fora:
            self._fora += 1

    def handle_endtag(self, tag):
        while self._pilha:
            t, fora = self._pilha.pop()
            if fora:
                self._fora -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if self.slides and not self._fora:
            self.slides[-1].texto += data + " "


def slides(html_deck: str) -> list[Slide]:
    leitor = _Leitor()
    leitor.feed(html_deck)
    for s in leitor.slides:
        linhas = [_normaliza(l) for l in s.texto.split("\n")]
        s.texto = "\n".join(l for l in linhas if l)
        s.aspas = re.findall(r'"([^"\n]+)"', s.texto)
    return leitor.slides


_NUMERO = re.compile(r"(?<![\w,.])\d{1,3}(?: \d{3})+(?![\d,])|(?<![\w,.])\d+(?:,\d+)?(?![\d,])")


def _tem_numero(monografia: str, n: str) -> bool:
    # A vírgula só faz parte do número quando vem dígito depois ("0,76");
    # "(1992, cap. 3)" tem o 1992.
    return re.search(r"(?<!\w)(?<!\d,)" + re.escape(n) + r"(?!\d|,\d| \d{3}\b)",
                     monografia) is not None


def problemas(html_deck: str, refs_pdf: dict[str, int],
              monografia: str) -> list[str]:
    achados = []
    mono_min = monografia.lower()
    for s in slides(html_deck):
        for r in s.refs:
            if r not in refs_pdf:
                achados.append("slide %d: a referência %r não existe no PDF"
                               % (s.numero, r))
        sem_aspas = re.sub(r'"[^"]+"', " ", s.texto)
        for n in _NUMERO.findall(sem_aspas):
            if not _tem_numero(monografia, n):
                achados.append("slide %d: o número %r não está na monografia"
                               % (s.numero, n))
        for frase in s.aspas:
            if frase.strip().lower() not in mono_min:
                achados.append("slide %d: a frase \"%s\" não está na monografia"
                               % (s.numero, frase))
    return achados


def gera() -> None:
    sys.path.insert(0, str(RAIZ))
    from mvp import trilha
    from mvp.dominio import carrega
    from mvp.trilha_escada import le

    DECK.mkdir(exist_ok=True)
    refs = referencias_do_pdf(LATEX)
    (DECK / "referencias.js").write_text(
        "/* Gerado por scripts/confere_apresentacao.py --gera: a numeração e a\n"
        "   página de cada seção, quadro e figura do PDF entregue. */\n"
        "window.REFS = %s;\n" % json.dumps(refs, ensure_ascii=False, indent=1),
        encoding="utf-8")
    d = carrega(topico="kc_06")
    e = le(RAIZ / "mvp" / "dominio" / "escada_kc06.yaml", d)["B1"]
    dados = {"cena": trilha.cena_json(e.cena), "codigo": e.revisao.codigo}
    (DECK / "cena.js").write_text(
        "/* Gerado por scripts/confere_apresentacao.py --gera: a cena da\n"
        "   revisão do kc_06, premissa B1 (Figura 5), tirada do domínio. */\n"
        "window.CENA = %s;\n" % json.dumps(dados, ensure_ascii=False),
        encoding="utf-8")


def main(args: list[str] | None = None) -> int:
    args = sys.argv[1:] if args is None else args
    if "--gera" in args:
        gera()
        print("escrito: apresentacao/referencias.js e apresentacao/cena.js")
        return 0
    achados = problemas((DECK / "index.html").read_text(encoding="utf-8"),
                        referencias_do_pdf(LATEX),
                        texto_da_monografia(MONOGRAFIA))
    for a in achados:
        print(a)
    print("%d problema(s)" % len(achados))
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
