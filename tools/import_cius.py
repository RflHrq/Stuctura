"""Extrai o catálogo de atividades do HTML publicado para cius.yaml.

    python -m tools.import_cius CAMINHO_DO_HTML [--out domain/c_pointers/cius.yaml]

Por que um extrator e não transcrição à mão: são 47 atividades com
distratores mapeados, e cada erro de digitação num `misconception_id`
corromperia a validação da Q-matrix — o desfecho primário do estudo. O
extrator é determinístico e re-executável: se o catálogo for republicado,
roda de novo e compara.

O HTML de origem é gerado a partir de um cius.yaml. Este script faz o
caminho de volta. Se os dois divergirem, o de origem é que manda.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FASES = {
    "fase diagnóstica": "diagnostic",
    "fase traversal": "traversal",
    "fase variação": "variation",
}

TIPOS = {
    "múltipla escolha": "multiple_choice",
    "predição de comportamento": "prediction",
    "lacuna guiada": "fill_in",
    "ordenação causal": "ordering",
    "contraste": "contrast",
}


class ImportError_(Exception):
    pass


# --------------------------------------------------------------------------
# Utilitários de texto
# --------------------------------------------------------------------------

def _texto(fragmento: str) -> str:
    """Remove tags e desescapa entidades, preservando o texto verbatim."""
    sem_tags = re.sub(r"<[^>]+>", "", fragmento)
    return html.unescape(sem_tags).strip()


def _bloco(artigo: str, padrao: str) -> str | None:
    m = re.search(padrao, artigo, re.S)
    return m.group(1) if m else None


def _yaml_str(s: str) -> str:
    """Escapa uma string para YAML entre aspas duplas."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# --------------------------------------------------------------------------
# Extração de uma atividade
# --------------------------------------------------------------------------

def parse_article(artigo: str) -> dict:
    cid = _bloco(artigo, r'<span class="cid">([^<]+)</span>')
    if not cid:
        raise ImportError_("artigo sem id")
    tipo_br = _texto(_bloco(artigo, r'<span class="tp">([^<]*)</span>') or "")
    fase_br = _texto(_bloco(artigo, r'<span class="ph">([^<]*)</span>') or "")
    if tipo_br not in TIPOS:
        raise ImportError_("%s: tipo desconhecido %r" % (cid, tipo_br))
    if fase_br not in FASES:
        raise ImportError_("%s: fase desconhecida %r" % (cid, fase_br))

    kc = "kc_" + cid.split("_")[1][2:]  # ciu_kc09_001 -> kc_09

    # Os alvos vivem no cabeçalho. Delimitar pelo <div class="chead">, e não
    # pelo </span> do próprio tgt: o HTML quebra linha antes do </div>, e
    # casar "</span></div>" adjacentes devolve lista vazia em silêncio.
    chead = _bloco(artigo, r'<div class="chead">(.*?)</div>')
    alvos = re.findall(r'<span class="nd [bi]"[^>]*>([^<]+)</span>', chead or "")
    if not alvos:
        raise ImportError_("%s: nenhum nó-alvo extraído do cabeçalho" % cid)

    ciu: dict = {
        "id": cid,
        "kc": kc,
        "targets": alvos,
        "phase": FASES[fase_br],
        "kind": TIPOS[tipo_br],
        "stem": _texto(_bloco(artigo, r'<p class="q">(.*?)</p>') or ""),
    }

    codigo = _bloco(artigo, r"<pre>(.*?)</pre>")
    if codigo:
        ciu["code"] = html.unescape(re.sub(r"<[^>]+>", "", codigo))

    # --- alternativas de múltipla escolha ---------------------------
    opcoes = []
    for li in re.findall(r'<li class="(ok|ds)">(.*?)</li>', artigo, re.S):
        classe, corpo = li
        mapa = _bloco(corpo, r'<span class="map">(.*?)</span></span>')
        texto = _texto(re.sub(r'<span class="map">.*?</span></span>', "", corpo, flags=re.S)
                       .replace('<span class="mk">correta</span>', "")
                       .replace('<span class="mk">distrator</span>', ""))
        op = {"text": texto}
        if classe == "ok":
            op["correct"] = True
        else:
            mid = _bloco(mapa or "", r"<code>([^<]+)</code>")
            if mid:
                op["misconception"] = mid
        opcoes.append(op)
    if opcoes:
        ciu["options"] = opcoes

    # --- ordenação causal --------------------------------------------
    passos_html = _bloco(artigo, r'<ol class="steps">(.*?)</ol>')
    if passos_html:
        ciu["steps"] = [_texto(x) for x in re.findall(r"<li>(.*?)</li>", passos_html, re.S)]
        erradas = []
        for corpo in re.findall(r'<div class="ds"><span class="mk">ordem errada</span>(.*?)</div>',
                                artigo, re.S):
            mapa = _bloco(corpo, r'<span class="map">(.*?)</span>')
            texto = _texto(re.sub(r'<span class="map">.*?</span>', "", corpo, flags=re.S))
            item = {"order": [p.strip() for p in texto.split("\u2192")]}
            mid = _bloco(mapa or "", r"<code>([^<]+)</code>")
            if mid:
                item["misconception"] = mid
            erradas.append(item)
        if erradas:
            ciu["wrong_orders"] = erradas

    # --- resposta livre -----------------------------------------------
    ans = _bloco(artigo, r'<div class="ans">(.*?)</div>')
    if ans:
        esperada = _texto(_bloco(ans, r"<code>([^<]+)</code>") or "")
        aceita_html = _bloco(ans, r'<span class="map">(.*?)</span>') or ""
        aceita = _texto(aceita_html).replace("também aceita:", "").strip()
        ciu["answer"] = {
            "expected": esperada,
            "also_accepts": [a.strip() for a in aceita.split(",") if a.strip()],
        }

    padroes = []
    for corpo in re.findall(r'<div class="ds pat">(.*?)</div>', artigo, re.S):
        mapa = _bloco(corpo, r'<span class="map">(.*?)</span>')
        texto = _texto(re.sub(r'<span class="map">.*?</span>', "", corpo, flags=re.S)
                       .replace('<span class="mk">padrão</span>', ""))
        item = {"match": [t.strip().strip('"') for t in texto.split('", "')]}
        item["match"] = [t.strip('"') for t in item["match"] if t.strip('"')]
        mid = _bloco(mapa or "", r"<code>([^<]+)</code>")
        if mid:
            item["misconception"] = mid
        padroes.append(item)
    if padroes:
        ciu["patterns"] = padroes

    # --- diagrama ------------------------------------------------------
    vis = _bloco(artigo, r'<div class="vis">(.*?)</div>')
    if vis:
        visual = {}
        for chave, valor in re.findall(r"<b>([^<]+)</b>\s*([^<]*)", vis):
            v = html.unescape(valor).strip()
            if v:
                visual[chave.strip()] = v
        if visual:
            ciu["visual"] = visual

    return ciu


def parse(html_texto: str) -> list[dict]:
    corpo = html_texto[html_texto.index("</style>"):]
    artigos = re.findall(r'<article class="ciu">.*?</article>', corpo, re.S)
    if not artigos:
        raise ImportError_("nenhuma atividade encontrada no HTML")
    return [parse_article(a) for a in artigos]


# --------------------------------------------------------------------------
# Emissão do YAML
# --------------------------------------------------------------------------

CABECALHO = '''# CIUs — atividades diagnósticas, de traversal e de variação.
#
# GERADO por tools/import_cius.py a partir do "Catálogo de Atividades do
# Structura" (artefato 38ed442a). Não editar à mão sem reconciliar com a
# origem: rode o extrator de novo e compare.
#
# `phase`:
#   diagnostic  até 3 por KC, sem feedback (§6)
#   traversal   usada durante a correção
#   variation   mesmo invariante, código novo; encerra o KC (RF11)
#
# `kind` varia entre CIUs consecutivas por regra do seletor (§7.5).
#
# Um distrator SEM `misconception` é deliberado: se for escolhido com
# frequência, é crença fora do catálogo — achado, não falha (§4.4).
#
# PENDÊNCIA DE REDAÇÃO: o texto veio sem acentuação do catálogo publicado
# ("memoria", "variavel", "e" por "é"). Precisa de revisão ortográfica
# antes do congelamento — é o item 9 do cronograma, não uma correção que
# o extrator deva fazer sozinho.

cius:
'''


def emit(cius: list[dict]) -> str:
    linhas = [CABECALHO]
    kc_atual = None
    for c in cius:
        if c["kc"] != kc_atual:
            kc_atual = c["kc"]
            linhas.append("\n  # ---- %s %s\n" % (kc_atual, "-" * (58 - len(kc_atual))))
        linhas.append("  %s:\n" % c["id"])
        linhas.append("    kc: %s\n" % c["kc"])
        linhas.append("    targets: [%s]\n" % ", ".join(c["targets"]))
        linhas.append("    phase: %s\n" % c["phase"])
        linhas.append("    kind: %s\n" % c["kind"])
        linhas.append("    stem: %s\n" % _yaml_str(c["stem"]))

        if "code" in c:
            linhas.append("    code: |\n")
            for l in c["code"].splitlines():
                linhas.append("      %s\n" % l)

        if "options" in c:
            linhas.append("    options:\n")
            for o in c["options"]:
                linhas.append("      - text: %s\n" % _yaml_str(o["text"]))
                if o.get("correct"):
                    linhas.append("        correct: true\n")
                if o.get("misconception"):
                    linhas.append("        misconception: %s\n" % o["misconception"])

        if "steps" in c:
            linhas.append("    steps:\n")
            for p in c["steps"]:
                linhas.append("      - %s\n" % _yaml_str(p))
        if "wrong_orders" in c:
            linhas.append("    wrong_orders:\n")
            for w in c["wrong_orders"]:
                linhas.append("      - order: [%s]\n" % ", ".join(_yaml_str(x) for x in w["order"]))
                if w.get("misconception"):
                    linhas.append("        misconception: %s\n" % w["misconception"])

        if "answer" in c:
            linhas.append("    answer:\n")
            linhas.append("      expected: %s\n" % _yaml_str(c["answer"]["expected"]))
            if c["answer"]["also_accepts"]:
                linhas.append("      also_accepts: [%s]\n"
                              % ", ".join(_yaml_str(x) for x in c["answer"]["also_accepts"]))
        if "patterns" in c:
            linhas.append("    patterns:\n")
            for p in c["patterns"]:
                linhas.append("      - match: [%s]\n" % ", ".join(_yaml_str(x) for x in p["match"]))
                if p.get("misconception"):
                    linhas.append("        misconception: %s\n" % p["misconception"])

        if "visual" in c:
            linhas.append("    visual:\n")
            for k, v in c["visual"].items():
                linhas.append("      %s: %s\n" % (k, _yaml_str(v)))
        linhas.append("\n")
    return "".join(linhas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Extrai cius.yaml do catálogo HTML.")
    p.add_argument("html", help="arquivo HTML do catálogo publicado")
    p.add_argument("--out", default="domain/c_pointers/cius.yaml")
    p.add_argument("--dry-run", action="store_true", help="só relata, não escreve")
    args = p.parse_args(argv)

    texto = Path(args.html).read_text(encoding="utf-8")
    cius = parse(texto)

    por_fase: dict[str, int] = {}
    por_kc: dict[str, int] = {}
    distratores = mapeados = 0
    for c in cius:
        por_fase[c["phase"]] = por_fase.get(c["phase"], 0) + 1
        por_kc[c["kc"]] = por_kc.get(c["kc"], 0) + 1
        for o in c.get("options", []):
            if not o.get("correct"):
                distratores += 1
                mapeados += bool(o.get("misconception"))

    print("%d atividades em %d KCs" % (len(cius), len(por_kc)))
    print("  por fase: %s" % ", ".join("%s=%d" % kv for kv in sorted(por_fase.items())))
    print("  distratores: %d, dos quais %d mapeados" % (distratores, mapeados))

    if args.dry_run:
        return 0
    Path(args.out).write_text(emit(cius), encoding="utf-8")
    print("escrito: %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
