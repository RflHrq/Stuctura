"""O PDF de reserva dos slides da defesa (docs/apresentacao.md).

    python scripts/apresentacao_pdf.py   # escreve entrega/apresentacao.pdf

Abre apresentacao/index.html?pdf=1 DIRETO DO ARQUIVO (file://), como o
Rafael vai abrir no notebook, e confere antes de imprimir que as fontes
do sistema carregaram e que são 22 slides: o modo ?pdf=1 revela todos os
passos e põe um slide por página. O navegador é o de
scripts/figuras_monografia.py.
"""

from __future__ import annotations

import base64
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from figuras_monografia import Navegador  # noqa: E402

DESTINO = RAIZ / "entrega" / "apresentacao.pdf"


def main() -> int:
    url = (RAIZ / "apresentacao" / "index.html").as_uri() + "?pdf=1"
    n = Navegador()
    try:
        n.cdp("Emulation.setDeviceMetricsOverride", width=1280, height=720,
              deviceScaleFactor=1, mobile=False)
        n.cdp("Page.navigate", url=url)
        n.espera("document.readyState === 'complete'", "a página")
        # O tema.css declara as mesmas famílias em /web/fontes/, que no
        # file:// falha; o que vale é a declaração embutida (fontes.css)
        # estar carregada. `document.fonts.check` daria falso por causa da
        # outra, então a conferência olha cada face.
        n.js("Promise.allSettled(Array.from(document.fonts).map("
             "function (f) { return f.load(); }))"
             ".then(function () { return true; })")
        fontes = n.js(
            "['Nunito', 'JetBrains Mono'].map(function (f) {"
            " return Array.from(document.fonts).some(function (x) {"
            " return x.family.replace(/\"/g, '') === f && x.status === 'loaded'"
            " && x.style === 'normal'; }); })")
        if fontes != [True, True]:
            raise RuntimeError("as fontes não carregaram: %r" % fontes)
        total = n.js("document.querySelectorAll('section.slide').length")
        if total != 22:
            raise RuntimeError("são %r slides, e não 22" % total)
        r = n.cdp("Page.printToPDF", printBackground=True,
                  preferCSSPageSize=True, marginTop=0, marginBottom=0,
                  marginLeft=0, marginRight=0)
    finally:
        n.fecha()
    DESTINO.parent.mkdir(exist_ok=True)
    DESTINO.write_bytes(base64.b64decode(r["data"]))
    print("escrito: %s" % DESTINO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
