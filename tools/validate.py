"""Validador estrutural do domínio. Porta de CI: saída 0 obrigatória.

    python -m tools.validate            # valida domain/c_pointers
    python -m tools.validate --stats     # com o resumo quantitativo

O `loader` já faz as verificações que impedem o sistema de subir (refs
pendurados, ciclo, tipos). Aqui vão as de POLÍTICA — as que não quebram o
motor, mas quebram o estudo:

  cobertura        todo nó de inferência deve ser alcançável a partir da
                   conclusão do seu KC; nó órfão é nó que nunca é
                   percorrido, e portanto peso morto no catálogo
  proveniência     toda crença declara grau e fonte (§1.3)
  classe           `kind` bate com o tipo do nó negado — é o que decide se
                   o confronto visual é obrigatório (RF08)
  diagrama         todo KC com crença fundacional exige socratic: diagram
  nomeação tardia  nenhum texto de nó contém o nome técnico do KC (RF10)
  golden           o tamanho real do plano bate com `plan_length`
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic  # noqa: E402
from engine.loader import Domain, DomainError, load  # noqa: E402


def _norm(s: str) -> str:
    """minúsculas sem acento, para comparar termos técnicos com folga."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s.lower())
        if unicodedata.category(c) != "Mn"
    )


# --------------------------------------------------------------------------
# Verificações de política
# --------------------------------------------------------------------------

def check_coverage(d: Domain) -> list[str]:
    """Todo nó deve ser percorrido por algum traversal do domínio.

    A alcançabilidade é GLOBAL, não por KC: um nó do KC 5 pode existir só
    para ser importado pelo KC 9, e continua sendo peso útil.

    Isto é AVISO, não erro. Um nó fora de todo traversal cai em dois casos,
    e só o pesquisador distingue:

      corolário       tem dependentes; decorre da conclusão em vez de levar
                      a ela. Legítimo — é o que o KC ensina DEPOIS de o
                      aluno construir a conclusão.
      sem dependentes ninguém o usa. Ou é peso morto a remover, ou falta
                      uma aresta que deveria existir.
    """
    alcancaveis: set = set()
    for kc in d.kcs.values():
        if kc.conclusion_node in kc.nodes:
            alcancaveis |= set(socratic.full_plan(d, kc.id, kc.conclusion_node))
    for m in d.misconceptions.values():
        alcancaveis |= set(socratic.full_plan(d, m.kc, m.node))
        for alvo in m.also_negates:
            alcancaveis |= set(socratic.full_plan(d, *alvo))

    out = []
    for kc in d.kcs.values():
        for n in kc.nodes:
            ref = (kc.id, n)
            if ref in alcancaveis:
                continue
            # Corolário: o nó se apoia NA conclusão do KC, em vez de levar
            # a ela. Decorre do que o aluno acabou de construir — legítimo.
            apoia_se_em = set(socratic.full_plan(d, kc.id, n))
            if kc.conclusion_ref in apoia_se_em and (kc.id, n) != kc.conclusion_ref:
                out.append(
                    "%s:%s é corolário da conclusão (%s) — nunca percorrido porque "
                    "vem depois dela. Confirmar se é intencional"
                    % (kc.id, n, kc.conclusion_node)
                )
            else:
                out.append(
                    "%s:%s fora de todo traversal e não decorre da conclusão — "
                    "peso morto ou aresta faltando" % (kc.id, n)
                )
    return out


def check_diagram_requirement(d: Domain) -> list[str]:
    """KC com crença fundacional precisa de diagrama antes do traversal."""
    out = []
    for kc in d.kcs.values():
        fundacionais = [
            m.id for m in d.misconceptions.values()
            if m.kind == "foundational" and m.kc == kc.id
        ]
        if fundacionais and kc.socratic != "diagram":
            out.append(
                "%s tem crença fundacional (%s) mas socratic=%r; RF08 exige "
                "confronto visual" % (kc.id, ", ".join(fundacionais), kc.socratic)
            )
    return out


def check_late_naming(d: Domain) -> list[str]:
    """RF10: o nome técnico não pode aparecer antes da conclusão.

    O nó de conclusão é isento: é exatamente onde o termo deve aparecer.
    KC sem termo a reter deixa `technical_name` vazio e não é verificado —
    nem todo KC esconde uma palavra.
    """
    out = []
    for kc in d.kcs.values():
        termo = _norm(kc.technical_name).strip()
        if not termo or len(termo) < 4:
            continue
        for node in kc.nodes.values():
            if node.id == kc.conclusion_node:
                continue
            if termo in _norm(node.text):
                out.append(
                    "%s:%s vaza o nome técnico %r antes da conclusão (RF10)"
                    % (kc.id, node.id, kc.technical_name)
                )
        for ciu in d.cius_of(kc.id):
            campos = [ciu.stem] + [o.text for o in ciu.options]
            for texto in campos:
                if termo in _norm(texto):
                    out.append(
                        "CIU %s vaza o nome técnico %r (RF10)" % (ciu.id, kc.technical_name)
                    )
                    break
    return out


def check_golden_plans(d: Domain) -> list[str]:
    """O tamanho real do plano tem de bater com o congelado no catálogo.

    Itens marcados `disputed: true` saem daqui e viram aviso: são os
    pontos onde as fontes do próprio projeto discordam entre si, e a
    decisão é do pesquisador, não do validador.
    """
    out = []
    for m in sorted(d.misconceptions.values(), key=lambda x: x.id):
        if m.disputed:
            continue
        if not m.plan_length:
            out.append("crença %s sem plan_length congelado" % m.id)
            continue
        real = len(socratic.full_plan(d, m.kc, m.node))
        if real != m.plan_length:
            out.append(
                "crença %s: plano tem %d passos, plan_length diz %d "
                "(o grafo mudou ou o número está errado)" % (m.id, real, m.plan_length)
            )
    return out


def check_disputed(d: Domain) -> list[str]:
    """Discrepâncias entre documentos do projeto, ainda não resolvidas."""
    out = []
    for m in sorted(d.misconceptions.values(), key=lambda x: x.id):
        if not m.disputed:
            continue
        real = len(socratic.full_plan(d, m.kc, m.node))
        detalhe = " plano real=%d, catálogo=%d." % (real, m.plan_length) \
            if m.plan_length and real != m.plan_length else ""
        out.append(
            "crença %s em disputa.%s %s"
            % (m.id, detalhe, (m.note or "").strip().replace("\n", " "))
        )
    return out


def check_ordering_shape(d: Domain) -> list[str]:
    """CIU de ordenação cujo distrator não é permutação exige outra interface.

    Um widget de arrastar-e-soltar só produz permutações dos mesmos passos.
    Quando a sequência errada tem passos diferentes, é escolha entre dois
    caminhos — e renderizar como reordenação tornaria o distrator inatingível.
    """
    out = []
    for c in d.cius.values():
        for w in c.wrong_orders:
            if not c.is_permutation(w):
                out.append(
                    "%s: a sequência errada não é permutação dos passos; render "
                    "como escolha entre caminhos, não como reordenação" % c.id
                )
    return out


def check_ciu_coverage(d: Domain) -> list[str]:
    """Cada KC do piloto precisa de CIU diagnóstica e de variação.

    O §6 diz "ATÉ 3 CIUs diagnósticas por KC": é teto, não piso. O que o
    piloto exige de fato é ao menos uma para diagnosticar e uma de
    variação para encerrar o KC (RF11). Ter só uma diagnóstica não
    impede a sessão, mas tira do seletor a regra de variar o tipo (§7.5)
    — vale registrar.
    """
    out = []
    for kc_id in d.pilot_sequence:
        cius = d.cius_of(kc_id)
        diag = [c for c in cius if c.phase == "diagnostic"]
        var = [c for c in cius if c.phase == "variation"]
        if not diag:
            out.append("%s sem CIU diagnóstica: a sessão não tem por onde começar" % kc_id)
        elif len(diag) == 1:
            out.append(
                "%s tem 1 CIU diagnóstica; com uma só, o seletor não consegue "
                "variar o tipo entre itens (§7.5)" % kc_id
            )
        if not var:
            out.append(
                "%s sem CIU de variação: RF11 exige acerto em código novo para "
                "encerrar o KC" % kc_id
            )
    return out


def check_distractor_mapping(d: Domain) -> list[str]:
    """Toda crença do catálogo precisa ser detectável por alguma CIU.

    Detectável por qualquer via: distrator de múltipla escolha, padrão de
    resposta livre ou sequência errada de ordenação. Crença que nenhuma
    atividade alcança é crença que o estudo não pode observar.
    """
    usadas = {m for c in d.cius.values() for m in c.misconception_ids()}
    ausentes = sorted(set(d.misconceptions) - usadas)
    if ausentes:
        return [
            "%d crença(s) que nenhuma CIU detecta: %s"
            % (len(ausentes), ", ".join(ausentes))
        ]
    return []


# --------------------------------------------------------------------------
# Relatório
# --------------------------------------------------------------------------

BLOQUEANTES = (
    ("exigência de diagrama (RF08)", check_diagram_requirement),
    ("nomeação tardia (RF10)", check_late_naming),
    ("golden dos planos", check_golden_plans),
)

AVISOS = (
    ("cobertura do grafo", check_coverage),
    ("discrepâncias em aberto", check_disputed),
    ("forma das CIUs de ordenação", check_ordering_shape),
    ("cobertura de CIUs", check_ciu_coverage),
    ("mapeamento de distratores", check_distractor_mapping),
)


def stats(d: Domain) -> str:
    nos = sum(len(k.nodes) for k in d.kcs.values())
    base = sum(1 for k in d.kcs.values() for n in k.nodes.values() if n.is_base)
    graus: dict[str, int] = {}
    for m in d.misconceptions.values():
        graus[m.grade] = graus.get(m.grade, 0) + 1
    fund = sum(1 for m in d.misconceptions.values() if m.kind == "foundational")
    planos = [len(socratic.full_plan(d, m.kc, m.node)) for m in d.misconceptions.values()]
    media = sum(planos) / len(planos) if planos else 0.0

    linhas = [
        "domínio        %s (%s)" % (d.id, d.name),
        "hash           %s" % d.hash,
        "KCs            %d" % len(d.kcs),
        "nós            %d  (%d base, %d inferência)" % (nos, base, nos - base),
        "crenças        %d  (%d fundacionais, %d derivacionais)"
        % (len(d.misconceptions), fund, len(d.misconceptions) - fund),
        "proveniência   %s" % "  ".join(
            "%s=%d" % (g, graus.get(g, 0)) for g in ("D", "T", "L", "N", "E")
        ),
        "CIUs           %d" % len(d.cius),
        "plano médio    %.1f passos  (mín %d, máx %d)"
        % (media, min(planos, default=0), max(planos, default=0)),
        "piloto         %s" % ", ".join(d.pilot_sequence),
    ]
    return "\n".join("  " + l for l in linhas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Valida o domínio declarativo do Structura.")
    p.add_argument("path", nargs="?", default=None, help="diretório do domínio")
    p.add_argument("--stats", action="store_true", help="mostra o resumo quantitativo")
    p.add_argument("--strict", action="store_true", help="trata avisos como erro")
    args = p.parse_args(argv)

    try:
        d = load(args.path)
    except DomainError as exc:
        print("CARGA FALHOU — o sistema não subiria.\n")
        for prob in exc.problemas:
            print("  ERRO  %s" % prob)
        print("\n%d problema(s) estrutural(is)." % len(exc.problemas))
        return 1

    print("Carga OK: %d KCs, %d crenças, %d CIUs.\n" % (
        len(d.kcs), len(d.misconceptions), len(d.cius)))

    erros: list[str] = []
    for nome, fn in BLOQUEANTES:
        achados = fn(d)
        marca = "ok " if not achados else "FALHA"
        print("  [%s] %s" % (marca, nome))
        for a in achados:
            print("         %s" % a)
        erros.extend(achados)

    avisos: list[str] = []
    for nome, fn in AVISOS:
        achados = fn(d)
        marca = "ok " if not achados else "aviso"
        print("  [%s] %s" % (marca, nome))
        for a in achados:
            print("         %s" % a)
        avisos.extend(achados)

    if args.stats:
        print("\n" + stats(d))

    print()
    if erros:
        print("%d erro(s) bloqueante(s), %d aviso(s)." % (len(erros), len(avisos)))
        return 1
    if avisos and args.strict:
        print("%d aviso(s), --strict ativo." % len(avisos))
        return 1
    print("Domínio válido. %d aviso(s)." % len(avisos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
