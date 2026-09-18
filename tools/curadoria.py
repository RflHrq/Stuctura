"""Levantamento dos grafos de premissas, para curadoria.

    python -m tools.curadoria -o docs/curadoria-grafos.md

Não é uma página bonita: é uma FOLHA DE TRABALHO. Ela lista, nó por nó,
tudo o que o domínio afirma hoje e tudo o que falta — para que a decisão de
onde aprofundar seja tomada olhando o grafo inteiro, e não de memória.

O que cada nó carrega aqui, e por que importa na curadoria:

  suporte      de quem ele decorre. Nó de inferência sem suporte é erro; nó
               com suporte de outro KC é onde o percurso atravessa tópicos.
  nega         quais crenças o negam. Nó sem crença nenhuma é nó que o
               diagnóstico nunca vai alcançar por erro do aluno — ele só
               aparece como passo do percurso.
  atividades   quais atividades o miram. Nó sem atividade não tem como ser
               medido: só pode ser aceito no percurso.
  caminhos     em quantos percursos do domínio ele entra. Nó em muitos
               caminhos é premissa de carga; se ele estiver mal escrito, o
               estrago é grande.
  papel        se está na cadeia até a conclusão do KC (espinha), se é
               corolário dela, ou se é órfão.

A seção final junta o que precisa de decisão humana: nós sem atividade, nós
sem crença, KCs sem cobertura de nível, e granularidade — nó cujo enunciado
junta mais de uma afirmação, que é onde o grafo está raso e o aluno pode
concordar com metade da frase.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import model, selector, socratic  # noqa: E402
from engine.loader import Domain, Ref, load  # noqa: E402

# Marcas de que um enunciado carrega mais de uma afirmação. Não é regra de
# língua: é heurística de curadoria, e o que ela devolve é uma sugestão de
# onde olhar — a decisão de dividir o nó é do autor do domínio.
#
# " e " sozinho NÃO entra: o texto canônico é sem acento, e ali "e" é quase
# sempre o verbo "é" ("o valor guardado em p e um endereco"). Com ele, a
# heurística marcava 40 dos 93 nós e não servia para nada.
EMENDAS = ("; ", " mas ", " porque ", ", e ", " alem de ", " tambem ")

# Enunciado longo costuma ser enunciado composto. O corte é arbitrário e
# existe só para ordenar a leitura: 16 palavras é o ponto em que os nós
# deste domínio começam a juntar duas afirmações.
PALAVRAS_LONGO = 16


def _fecho(d: Domain, kc_id: str) -> list[Ref]:
    """Nós do KC mais todo nó de outro KC que o suporte alcança."""
    vistos: list[Ref] = []

    def visitar(ref: Ref) -> None:
        if ref in vistos:
            return
        try:
            no = d.node(*ref)
        except KeyError:
            return
        vistos.append(ref)
        for s in no.support:
            visitar(s)

    for n in d.kcs[kc_id].nodes:
        visitar((kc_id, n))
    return vistos


def _caminhos(d: Domain) -> Counter:
    """Quantos percursos do domínio cruzam cada nó.

    Um percurso por conclusão de KC, mais um por crença — que é exatamente
    o conjunto de caminhos que uma sessão pode andar.
    """
    cruz: Counter = Counter()
    for kc in d.kcs.values():
        if kc.conclusion_node in kc.nodes:
            for ref in set(socratic.full_plan(d, kc.id, kc.conclusion_node)):
                cruz[ref] += 1
    for m in d.misconceptions.values():
        for ref in set(socratic.full_plan(d, m.kc, m.node)):
            cruz[ref] += 1
    return cruz


def _papel(d: Domain, kc_id: str, node: str, espinha: set[str]) -> str:
    if node in espinha:
        return "espinha"
    apoia = set(socratic.full_plan(d, kc_id, node))
    if d.kcs[kc_id].conclusion_ref in apoia:
        return "corolário"
    return "órfão"


def _emendas(texto: str) -> str:
    """Por que este enunciado parece carregar mais de uma afirmação."""
    baixo = " " + texto.lower() + " "
    sinais = [m.strip() or ";" for m in EMENDAS if m in baixo]
    if len(texto.split()) > PALAVRAS_LONGO:
        sinais.append("%d palavras" % len(texto.split()))
    return ", ".join(sinais)


def _linha(texto: str, limite: int = 88) -> str:
    """Uma célula de tabela não pode ter quebra nem barra vertical."""
    t = " ".join((texto or "").split()).replace("|", "/")
    return t if len(t) <= limite else t[: limite - 1] + "…"


def relatorio(d: Domain) -> str:
    cruz = _caminhos(d)
    nega: dict[Ref, list[str]] = defaultdict(list)
    for m in d.misconceptions.values():
        nega[m.negates].append("%s (%s)" % (m.id, m.grade))
    mira: dict[Ref, list[str]] = defaultdict(list)
    for c in d.cius.values():
        for t in c.targets:
            mira[(c.kc, t)].append("%s n%d" % (c.id, c.nivel))

    out: list[str] = []
    w = out.append

    w("# Curadoria dos grafos de premissas")
    w("")
    w("Gerado por `python -m tools.curadoria`. Não editar à mão: mexa nos")
    w("YAMLs e gere de novo.")
    w("")
    w("Domínio `%s`, hash `%s`." % (d.id, d.hash.replace("sha256:", "")[:12]))
    w("")

    piloto = list(d.pilot_sequence)
    base = sum(1 for kc in d.kcs.values() for n in kc.nodes.values() if n.is_base)
    w("| | |")
    w("| --- | --- |")
    w("| Tópicos | %d (%d no piloto: %s) |"
      % (len(d.kcs), len(piloto), ", ".join(piloto)))
    w("| Nós | %d (%d observáveis, %d de inferência) |"
      % (sum(len(kc.nodes) for kc in d.kcs.values()), base,
         sum(len(kc.nodes) for kc in d.kcs.values()) - base))
    w("| Crenças | %d |" % len(d.misconceptions))
    w("| Atividades | %d |" % len(d.cius))
    w("")

    # ------------------------------------------------------------------ KCs
    for kc_id, kc in sorted(d.kcs.items(), key=lambda x: x[1].teaching_order):
        marca = " · **piloto**" if kc_id in piloto else ""
        w("## %s — %s%s" % (kc_id, kc.name, marca))
        w("")
        w("Conclusão (`%s`): %s" % (kc.conclusion_node, _linha(kc.conclusion, 200)))
        w("")
        prereq = ", ".join(kc.prerequisites) or "nenhum"
        fecho = _fecho(d, kc_id)
        fora = [r for r in fecho if r[0] != kc_id]
        w("Prerequisitos declarados: %s. O percurso deste tópico alcança %d nós, "
          "sendo %d de outros tópicos." % (prereq, len(fecho), len(fora)))
        w("")

        espinha = set(model.core_nodes(d, kc_id))
        w("| Nó | Tipo | Papel | Suporte | Caminhos | Crenças que o negam | Atividades |")
        w("| --- | --- | --- | --- | --- | --- | --- |")
        for nid, node in kc.nodes.items():
            sup = ", ".join(
                ("%s:%s" % s) if s[0] != kc_id else s[1] for s in node.support
            ) or "—"
            w("| `%s` | %s | %s | %s | %d | %s | %s |" % (
                nid,
                "observável" if node.is_base else "inferência",
                _papel(d, kc_id, nid, espinha),
                sup,
                cruz.get((kc_id, nid), 0),
                ", ".join(nega.get((kc_id, nid), [])) or "—",
                ", ".join(mira.get((kc_id, nid), [])) or "—",
            ))
        w("")
        w("**O que cada nó afirma**")
        w("")
        for nid, node in kc.nodes.items():
            w("- `%s` — %s" % (nid, _linha(node.text, 200)))
            if node.plain and node.plain != node.text:
                w("    - em linguagem corrente: %s" % _linha(node.plain, 200))
            if node.imported_from:
                w("    - importado de `%s:%s`" % node.imported_from)
        w("")

    # -------------------------------------------------- o que pede decisão
    w("## O que pede decisão sua")
    w("")

    sem_atividade = [(kc.id, n) for kc in d.kcs.values() for n in kc.nodes
                     if not mira.get((kc.id, n))]
    sem_crenca = [(kc.id, n) for kc in d.kcs.values() for n in kc.nodes
                  if not nega.get((kc.id, n))]
    emendados = [(kc.id, n, node.text, _emendas(node.text))
                 for kc in d.kcs.values() for n, node in kc.nodes.items()
                 if _emendas(node.text)]

    w("### Nós que nenhuma atividade mede (%d de %d)"
      % (len(sem_atividade), sum(len(kc.nodes) for kc in d.kcs.values())))
    w("")
    w("Estes nós só podem ser ACEITOS no percurso, nunca demonstrados. Se um")
    w("deles é premissa de carga (muitos caminhos), vale escrever atividade.")
    w("")
    w("| Nó | Caminhos | Enunciado |")
    w("| --- | --- | --- |")
    for kc_id, n in sorted(sem_atividade, key=lambda r: -cruz.get(r, 0))[:25]:
        w("| `%s:%s` | %d | %s |"
          % (kc_id, n, cruz.get((kc_id, n), 0), _linha(d.node(kc_id, n).text)))
    w("")

    w("### Nós que nenhuma crença nega (%d)" % len(sem_crenca))
    w("")
    w("O diagnóstico nunca chega a eles por erro do aluno: eles existem como")
    w("degrau do percurso. Isso é legítimo — mas um nó de inferência com muitos")
    w("caminhos e nenhuma crença costuma ser lugar onde falta mapear erro.")
    w("")
    w("| Nó | Tipo | Caminhos | Enunciado |")
    w("| --- | --- | --- | --- |")
    candidatos = [(k, n) for k, n in sem_crenca
                  if not d.node(k, n).is_base and cruz.get((k, n), 0) >= 2]
    for kc_id, n in sorted(candidatos, key=lambda r: -cruz.get(r, 0))[:20]:
        w("| `%s:%s` | inferência | %d | %s |"
          % (kc_id, n, cruz.get((kc_id, n), 0), _linha(d.node(kc_id, n).text)))
    w("")

    w("### Nós que talvez precisem ser divididos (%d)" % len(emendados))
    w("")
    w("Heurística, não regra: o enunciado tem ponto e vírgula, \"mas\" ou")
    w("\"porque\" ligando duas afirmações, ou passa de %d palavras. O aluno pode"
      % PALAVRAS_LONGO)
    w("concordar com metade da frase e o sistema registra que ele concordou com")
    w("tudo — é aqui que o grafo está raso e a granularidade precisa aumentar.")
    w("")
    w("| Nó | Sinal | Enunciado |")
    w("| --- | --- | --- |")
    for kc_id, n, texto, sinal in emendados[:30]:
        w("| `%s:%s` | %s | %s |" % (kc_id, n, sinal, _linha(texto, 110)))
    w("")

    w("### Cobertura de nível por tópico")
    w("")
    w("A sessão começa no nível 1 e sobe um degrau por vez. Tópico sem algum")
    w("degrau não consegue oferecer a escada inteira.")
    w("")
    w("| Tópico | n1 | n2 | n3 | Atividades | Crenças |")
    w("| --- | --- | --- | --- | --- | --- |")
    for kc_id, kc in sorted(d.kcs.items(), key=lambda x: x[1].teaching_order):
        its = [c for c in d.cius.values() if c.kc == kc_id]
        por_nivel = Counter(c.nivel for c in its)
        falta = [str(n) for n in (1, 2, 3) if not por_nivel.get(n)]
        aviso = " ⚠ falta n%s" % ", n".join(falta) if falta else ""
        w("| %s%s | %d | %d | %d | %d | %d |" % (
            kc_id, aviso, por_nivel.get(1, 0), por_nivel.get(2, 0),
            por_nivel.get(3, 0), len(its),
            sum(1 for m in d.misconceptions.values() if m.kc == kc_id)))
    w("")

    w("### Crenças por procedência")
    w("")
    w("| Procedência | O que significa | Quantas |")
    w("| --- | --- | --- |")
    sentido = {
        "D": "documentada: achado empírico com fonte e página",
        "T": "transposta de outra linguagem, com analogia declarada",
        "L": "registrada como erro comum em obra técnica de C",
        "N": "o erro está em norma (CERT C, CWE); a crença, não",
        "E": "elaborada a partir do modelo de máquina; hipótese a testar",
    }
    graus = Counter(m.grade for m in d.misconceptions.values())
    for g in ("D", "T", "L", "N", "E"):
        w("| %s | %s | %d |" % (g, sentido[g], graus.get(g, 0)))
    w("")

    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("-o", "--out", default="docs/curadoria-grafos.md")
    p.add_argument("--domain", default=None)
    args = p.parse_args(argv)

    d = load(Path(args.domain)) if args.domain else load()
    destino = Path(args.out)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(relatorio(d), encoding="utf-8", newline="\n")
    print("escrito em %s" % destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
