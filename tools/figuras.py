"""Folha de conferência: cada nó de um KC com as duas versões e a figura.

Para quem vai JULGAR o registro — não para o participante. Põe lado a
lado, no mesmo lugar:

  o enunciado do grafo   (`text`, a proposição com proveniência)
  a versão que o aluno lê (`plain`)
  a pergunta montada      (o que aparece de fato na tela)
  a ilustração            (renderizada por web/figures.js, a mesma do piloto)

A página é autossuficiente: embute a folha de estilo e o renderizador, e
não busca nada da rede (RNF05). Abrir o arquivo basta.

    python -m tools.figuras kc_07 > analise/figuras_kc07.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic
from engine.loader import load

WEB = Path(__file__).resolve().parent.parent / "web"


def pagina(kc_id: str, path: str | None = None) -> str:
    d = load(path)
    kc = d.kcs[kc_id]

    # A ordem da folha é a ordem do TRAVERSAL até a conclusão, não a ordem
    # do YAML: é assim que o participante encontra as premissas, e é essa
    # progressão — do mais primordial ao mais elaborado — que se julga.
    plano = socratic.plan(d, kc_id, kc.conclusion_node)
    resto = [(kc_id, n) for n in kc.nodes if (kc_id, n) not in plano]

    blocos = []
    for i, ref in enumerate(plano + resto, start=1):
        no = d.node(*ref)
        fora = ref[0] != kc_id
        na_cadeia = ref in plano
        pergunta = socratic.question(d, *ref)
        blocos.append(
            '<article class="no">'
            '<header><span class="id">%s:%s</span>'
            '<span class="tag %s">%s</span>%s%s</header>'
            '<div class="par"><b>grafo</b><p class="canon">%s</p></div>'
            '<div class="par"><b>o aluno lê</b><p class="plain">%s</p></div>'
            '<div class="par"><b>na tela</b><p class="q">%s</p></div>'
            '<div class="fig" data-figura="%s"></div>'
            '</article>' % (
                html.escape(ref[0]), html.escape(ref[1]),
                no.type, "premissa observável" if no.is_base else "decorre de outras",
                '<span class="tag fora">de outro KC</span>' if fora else "",
                "" if na_cadeia else '<span class="tag solto">fora da cadeia</span>',
                html.escape(no.text),
                html.escape(no.plain) or '<i>ainda sem versão simples</i>',
                html.escape(pergunta),
                html.escape(json.dumps(no.figure or {}, ensure_ascii=False)),
            ))

    estilo = (WEB / "style.css").read_text(encoding="utf-8")
    figuras = (WEB / "figures.js").read_text(encoding="utf-8")

    return TEMPLATE % {
        "kc": html.escape(kc_id),
        "nome": html.escape(kc.name),
        "conclusao": html.escape(kc.conclusion),
        "hash": html.escape(d.hash),
        "total": len(plano) + len(resto),
        "simples": sum(1 for r in plano + resto if d.node(*r).plain),
        "estilo": estilo,
        "figuras": figuras,
        "blocos": "\n".join(blocos),
    }


TEMPLATE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Structura — premissas do %(kc)s</title>
<style>%(estilo)s</style>
<style>
  body { padding: 28px 20px 80px; }
  .folha { max-width: 860px; margin: 0 auto; }
  .cabeca { border-bottom: 2px solid var(--rule-2); padding-bottom: 18px;
            margin-bottom: 26px; }
  .cabeca h1 { margin: 0 0 6px; font-size: 24px; }
  .cabeca .sub { color: var(--mute); font-size: 14px; }
  .cabeca .concl { margin-top: 14px; padding: 12px 14px; background: var(--sunk);
                   border-left: 3px solid var(--accent); border-radius: 0 6px 6px 0; }
  .no { background: var(--card); border: 1px solid var(--rule);
        border-radius: var(--radius); padding: 18px 20px; margin-bottom: 20px;
        box-shadow: var(--shadow); }
  .no header { display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
               margin-bottom: 14px; }
  .id { font-family: ui-monospace, Consolas, monospace; font-weight: 700;
        font-size: 14px; color: var(--accent); }
  .tag { font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase;
         padding: 3px 8px; border-radius: 20px; background: var(--sunk);
         color: var(--mute); border: 1px solid var(--rule-2); }
  .tag.fora { background: var(--warn-bg); color: var(--warn);
              border-color: var(--warn); }
  .tag.solto { background: var(--bad-bg); color: var(--bad);
               border-color: var(--bad); }
  .par { display: grid; grid-template-columns: 96px 1fr; gap: 14px;
         margin-bottom: 10px; align-items: baseline; }
  .par b { font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
           color: var(--mute); font-weight: 600; }
  .par p { margin: 0; font-size: 15px; }
  .canon { color: var(--ink-2); font-family: ui-monospace, Consolas, monospace;
           font-size: 13.5px; }
  .plain { color: var(--ink); font-weight: 500; }
  .q { color: var(--ink-2); white-space: pre-line; font-size: 14px;
       border-left: 2px solid var(--rule-2); padding-left: 12px; }
  .fig { margin-top: 16px; }
  @media (max-width: 620px) { .par { grid-template-columns: 1fr; gap: 2px; } }
</style>
</head><body>
<div class="folha">
  <div class="cabeca">
    <h1>%(kc)s — %(nome)s</h1>
    <div class="sub">%(simples)d de %(total)d nós com versão simplificada ·
      domínio %(hash)s</div>
    <div class="concl"><b>conclusão do KC:</b> %(conclusao)s</div>
    <p class="sub" style="margin-top:14px">Na ordem em que o traversal
      percorre até a conclusão — do mais primordial ao mais elaborado.
      Os nós fora dessa cadeia vêm ao final.</p>
  </div>
  %(blocos)s
</div>
<script>%(figuras)s</script>
<script>
  document.querySelectorAll(".fig").forEach(function (caixa) {
    var f = JSON.parse(caixa.dataset.figura || "{}");
    var el = f.kind ? Fig.render(f, "premissa-fig") : null;
    if (el) caixa.appendChild(el);
    else caixa.remove();
  });
</script>
</body></html>
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("kc", help="id do KC, por exemplo kc_07")
    p.add_argument("--path", default=None, help="diretório do domínio")
    p.add_argument("-o", "--out", default=None, help="arquivo de saída")
    args = p.parse_args(argv)

    saida = pagina(args.kc, args.path)
    if args.out:
        Path(args.out).write_text(saida, encoding="utf-8")
        print("escrito em %s" % args.out)
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
