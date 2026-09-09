"""Validador estrutural do domínio. Porta de CI: saída 0 obrigatória.

    python -m tools.validate           # valida domain/c_pointers
    python -m tools.validate --stats   # com o resumo quantitativo
    python -m tools.validate --strict  # avisos também derrubam a saída

O `loader` já faz o que impede o sistema de subir: referência pendurada,
ciclo no grafo, forma de CIU incoerente com o `type`. Aqui vão as
verificações de POLÍTICA — as que não quebram o motor, mas quebram o
estudo:

  RF08   KC com crença fundacional precisa de CIU com diagrama
  RF10   nenhum termo de nomeação tardia fora do nó de conclusão
  RF11   todo KC precisa de CIU de variação para poder ser encerrado
  §12    toda crença tem de ser detectável por alguma atividade
  §7.1   todo nó tem de ser percorrido por algum traversal
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
    """minúsculas sem acento: o domínio está sem acentuação e a comparação
    não pode depender disso."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s.lower())
        if unicodedata.category(c) != "Mn"
    )


# --------------------------------------------------------------------------
# Bloqueantes
# --------------------------------------------------------------------------

def check_diagram_requirement(d: Domain) -> list[str]:
    """RF08: KC com crença que nega nó-base precisa de confronto visual.

    Não há premissa anterior para confrontar uma crença fundacional: só a
    observação direta reintroduz o fato. Um KC assim sem nenhuma CIU com
    `visual` não tem como cumprir o RF08 em sessão.
    """
    out = []
    for kc_id in d.teaching_sequence():
        if not d.requires_diagram(kc_id):
            continue
        fundacionais = [m.id for m in d.misconceptions_of(kc_id) if m.is_foundational]
        if not any(c.visual for c in d.cius_of(kc_id)):
            out.append(
                "%s tem crença fundacional (%s) e nenhuma CIU com diagrama; "
                "RF08 não pode ser cumprido" % (kc_id, ", ".join(fundacionais))
            )
    return out


def check_late_naming(d: Domain) -> list[str]:
    """RF10: o termo técnico só pode aparecer no nó de conclusão.

    Os termos vêm de study.yaml, não do domínio: é regra de apresentação
    do experimento, e o mesmo grafo poderia ser usado sem ela.
    """
    out = []
    termos = [(_norm(t), t) for t in d.study.late_named_terms]
    if not termos:
        return out
    for kc in d.kcs.values():
        for node in kc.nodes.values():
            if node.id == kc.conclusion_node:
                continue
            for norm, orig in termos:
                # `plain` é o que o participante REALMENTE lê quando existe.
                # Verificar só `text` deixaria o vazamento passar justamente
                # pelo campo novo — e RF10 é sobre o que chega aos olhos.
                for campo, valor in (("text", node.text), ("plain", node.plain)):
                    if valor and norm in _norm(valor):
                        out.append(
                            "%s:%s usa %r em `%s`, antes da conclusão (%s) — RF10"
                            % (kc.id, node.id, orig, campo, kc.conclusion_node)
                        )
    for c in d.cius.values():
        for norm, orig in termos:
            if norm in _norm(c.prompt) or any(norm in _norm(o.text) for o in c.options):
                out.append("CIU %s usa %r; a nomeação é tardia (RF10)" % (c.id, orig))
    return out


def check_intro_scope(d: Domain) -> list[str]:
    """A introdução não pode ensinar as conclusões dos KCs que o piloto MEDE.

    Se ela dissesse "array e ponteiro são tipos distintos", teria ensinado
    a resposta da primeira atividade — e o diagnóstico deixaria de medir a
    crença prévia do aluno, que é o desfecho PRIMÁRIO do estudo.

    A verificação é por termo distintivo do nome de cada KC do piloto.
    Grosseira de propósito: prefere acusar demais a deixar passar.
    """
    if not d.intro:
        return []

    # "ponteiro" aparece no nome de quase todo KC e no vocabulário que a
    # introdução PRECISA estabelecer; não é termo distintivo de nenhum.
    generico = {"ponteiro", "ponteiros", "dereferencia"}
    proibidos: dict[str, str] = {}
    for kc_id in d.pilot_sequence:
        kc = d.kcs[kc_id]
        nome_tecnico = d.study.reveal_names.get(kc_id, "")
        for termo in list(kc.name.split()) + list(nome_tecnico.split()):
            t = _norm(termo).strip(":()")
            if len(t) >= 5 and t not in generico:
                proibidos[t] = kc_id

    out = []
    for c in d.intro:
        texto = _norm(" ".join([c.title, c.lead] + list(c.body)))
        for termo, kc_id in sorted(proibidos.items()):
            if termo in texto:
                out.append(
                    "intro '%s' menciona %r, termo do %s — um KC que o piloto "
                    "MEDE. A introdução contaminaria o diagnóstico"
                    % (c.id, termo, kc_id)
                )
    return out


def check_detectability(d: Domain) -> list[str]:
    """Toda crença precisa ser detectável por alguma CIU.

    Crença que nenhuma atividade alcança é crença que o estudo não pode
    observar — e o desfecho primário é justamente a validação da Q-matrix.
    """
    usadas = {m for c in d.cius.values() for m in c.misconception_ids()}
    ausentes = sorted(set(d.misconceptions) - usadas)
    if ausentes:
        return ["%d crença(s) que nenhuma CIU detecta: %s"
                % (len(ausentes), ", ".join(ausentes))]
    return []


def _prereq_closure(d: Domain, kc_id: str) -> set:
    """Todos os KCs que este exige, direta ou transitivamente."""
    vistos: set = set()
    pilha = list(d.kcs[kc_id].prerequisites)
    while pilha:
        atual = pilha.pop()
        if atual in vistos or atual not in d.kcs:
            continue
        vistos.add(atual)
        pilha.extend(d.kcs[atual].prerequisites)
    return vistos


def check_qmatrix_coherence(d: Domain) -> list[str]:
    """Distrator só pode apontar para crença do próprio KC ou de prerequisito.

    Mapear para outro KC não é erro por si: os grafos se importam, e um
    aluno pode revelar no KC 8 uma crença ancorada no KC 2 — é falha de
    prerequisito, e detectá-la é justamente o que a estrutura permite.

    O que seria incoerente é mapear para um KC que este nem exige: aí a
    resposta seria atribuída, na análise, a uma crença que o participante
    não tinha por que ter exercitado ali.
    """
    out = []
    for c in sorted(d.cius.values(), key=lambda x: x.id):
        permitidos = {c.kc} | _prereq_closure(d, c.kc)
        for mid in c.misconception_ids():
            m = d.misconceptions[mid]
            if m.kc not in permitidos:
                out.append(
                    "CIU %s (%s) mapeia %s, que nega nó de %s — e %s não é "
                    "prerequisito de %s" % (c.id, c.kc, mid, m.kc, m.kc, c.kc)
                )
    return out


def check_cross_kc_mapping(d: Domain) -> list[str]:
    """Distratores que diagnosticam crença de um KC anterior.

    Legítimo, mas precisa aparecer na análise: a resposta a uma CIU do
    KC 8 será atribuída a uma crença do KC 2, e o `answers.csv` tem de
    deixar isso legível em vez de parecer erro de mapeamento.
    """
    out = []
    for c in sorted(d.cius.values(), key=lambda x: x.id):
        for mid in c.misconception_ids():
            m = d.misconceptions[mid]
            if m.kc != c.kc:
                out.append(
                    "CIU %s (%s) detecta %s, ancorada em %s:%s — falha de "
                    "prerequisito, não do KC da atividade"
                    % (c.id, c.kc, mid, m.kc, m.node)
                )
    return out


# --------------------------------------------------------------------------
# Avisos
# --------------------------------------------------------------------------

def check_variation_coverage(d: Domain) -> list[str]:
    """RF11: sem CIU de variação, o KC não tem como ser encerrado.

    Bloqueia de verdade só dentro do recorte do piloto; fora dele, fica
    visível para a expansão em vez de ser descoberto no meio de uma sessão.
    """
    out = []
    for kc_id in d.teaching_sequence():
        if d.cius_of(kc_id, "variation"):
            continue
        dentro = kc_id in d.pilot_sequence
        out.append(
            "%s: nenhuma CIU de fase 'variation'. A RF11 não pode ser satisfeita: "
            "o KC não tem como ser encerrado%s"
            % (kc_id, " — E ELE ESTÁ NO PILOTO" if dentro else " (fora do piloto)")
        )
    return out


def check_diagnostic_coverage(d: Domain) -> list[str]:
    """O §6 diz "ATÉ 3 CIUs diagnósticas": é teto, não piso.

    Com uma só, porém, o seletor perde a regra de variar o tipo (§7.5).
    """
    out = []
    for kc_id in d.pilot_sequence:
        diag = d.cius_of(kc_id, "diagnostic")
        if not diag:
            out.append("%s sem CIU diagnóstica: a sessão não tem por onde começar" % kc_id)
        elif len(diag) == 1:
            out.append(
                "%s tem 1 CIU diagnóstica; com uma só o seletor não varia o tipo (§7.5)"
                % kc_id
            )
    return out


def check_node_coverage(d: Domain) -> list[str]:
    """Todo nó deve ser percorrido por algum traversal do domínio.

    A alcançabilidade é GLOBAL: um nó do KC 5 pode existir só para ser
    importado pelo KC 9 e continuar sendo peso útil. Fora de todo
    traversal, cai em dois casos que só o pesquisador distingue:

      corolário  apoia-se NA conclusão em vez de levar a ela. Legítimo:
                 é o que o KC ensina depois de o aluno construí-la.
      órfão      ninguém o alcança. Peso morto, ou aresta faltando.
    """
    alcancaveis: set = set()
    for kc in d.kcs.values():
        if kc.conclusion_node in kc.nodes:
            alcancaveis |= set(socratic.full_plan(d, kc.id, kc.conclusion_node))
    for m in d.misconceptions.values():
        alcancaveis |= set(socratic.full_plan(d, m.kc, m.node))

    out = []
    for kc in d.kcs.values():
        for n in kc.nodes:
            if (kc.id, n) in alcancaveis:
                continue
            apoia = set(socratic.full_plan(d, kc.id, n))
            if kc.conclusion_ref in apoia:
                out.append(
                    "%s:%s é corolário da conclusão (%s): vem depois dela, por isso "
                    "nenhum traversal o percorre" % (kc.id, n, kc.conclusion_node)
                )
            else:
                out.append(
                    "%s:%s fora de todo traversal e não decorre da conclusão — "
                    "peso morto ou aresta faltando" % (kc.id, n)
                )
    return out


def check_plain_consistency(d: Domain) -> list[str]:
    """Um KC não deveria misturar os dois registros no mesmo traversal.

    `plain` é opcional por KC — reescrever os 93 nós é trabalho de conteúdo,
    e o domínio tem de continuar carregando enquanto ele não acontece. Mas
    DENTRO de um KC a mistura é visível: o aluno confirma três premissas em
    linguagem corrente e a quarta chega em linguagem técnica, no meio da
    mesma pergunta. Ou o KC inteiro tem, ou nenhum nó tem.

    É aviso, não erro: um KC pela metade ainda coleta dado válido. Só não
    deve chegar assim ao piloto.
    """
    out = []
    for kc in d.kcs.values():
        com = [n.id for n in kc.nodes.values() if n.plain]
        sem = [n.id for n in kc.nodes.values() if not n.plain]
        if com and sem:
            out.append(
                "%s tem %d nó(s) com `plain` e %d sem (%s): o traversal "
                "misturaria os dois registros%s"
                % (kc.id, len(com), len(sem), ", ".join(sorted(sem)),
                   "" if kc.id in d.pilot_sequence else " (fora do piloto)")
            )
    return out


def check_mixed_question(d: Domain) -> list[str]:
    """Uma pergunta que cita metade das premissas em cada registro.

    A pergunta de uma inferência cita o nó e cada um dos seus suportes. Se
    parte deles tem `plain` e parte não, o aluno lê, na MESMA frase, uma
    premissa em linguagem corrente e outra em linguagem técnica — e não há
    como ele saber que são o mesmo tipo de coisa.

    Isto acontece calado quando o suporte vem de outro KC: kc_07:I4 se
    apoia em kc_06.B2, e simplificar o kc_07 sem tocar no kc_06 produziria
    exatamente essa frase. A conferência por KC não pegaria — o nó
    estrangeiro não pertence ao KC simplificado.
    """
    out = []
    for kc in d.kcs.values():
        for node in kc.nodes.values():
            if not node.support:
                continue
            citados = [node]
            for ref in node.support:
                try:
                    citados.append(d.node(*ref))
                except KeyError:
                    pass
            com = [n for n in citados if n.plain]
            sem = [n for n in citados if not n.plain]
            if com and sem:
                out.append(
                    "a pergunta de %s:%s mistura os registros: %s com "
                    "`plain`, %s não" % (
                        kc.id, node.id,
                        ", ".join("%s:%s" % (n.kc, n.id) for n in com),
                        ", ".join("%s:%s" % (n.kc, n.id) for n in sem)))
    return out


def check_hypotheses(d: Domain) -> list[str]:
    """Crenças cuja formulação ainda é hipótese, não achado.

    Grau N documenta o ERRO em norma, não a crença; grau E não tem fonte.
    Nos dois casos, o texto da monografia precisa dizer isso — e a Q-matrix
    do piloto é o que confirma ou descarta.
    """
    return [
        "%s (grau %s, %s): a formulação da crença é hipótese a testar na Q-matrix"
        % (m.id, m.grade, m.kc)
        for m in sorted(d.misconceptions.values(), key=lambda x: x.id)
        if m.grade in ("N", "E")
    ]


# --------------------------------------------------------------------------
# Relatório
# --------------------------------------------------------------------------

BLOQUEANTES = (
    ("exigência de diagrama (RF08)", check_diagram_requirement),
    ("nomeação tardia (RF10)", check_late_naming),
    ("escopo da introdução", check_intro_scope),
    ("detectabilidade das crenças (§12)", check_detectability),
    ("coerência da Q-matrix", check_qmatrix_coherence),
)

AVISOS = (
    ("mapeamento cross-KC", check_cross_kc_mapping),
    ("CIU de variação (RF11)", check_variation_coverage),
    ("CIUs diagnósticas", check_diagnostic_coverage),
    ("cobertura do grafo", check_node_coverage),
    ("crenças ainda hipotéticas", check_hypotheses),
    ("registro uniforme por KC", check_plain_consistency),
    ("pergunta com registro misto", check_mixed_question),
)


def stats(d: Domain) -> str:
    nos = sum(len(k.nodes) for k in d.kcs.values())
    base = sum(1 for k in d.kcs.values() for n in k.nodes.values() if n.is_base)
    graus: dict[str, int] = {}
    for m in d.misconceptions.values():
        graus[m.grade] = graus.get(m.grade, 0) + 1
    fund = sum(1 for m in d.misconceptions.values() if m.is_foundational)
    planos = [len(socratic.full_plan(d, m.kc, m.node)) for m in d.misconceptions.values()]
    fases: dict[str, int] = {}
    tipos: dict[str, int] = {}
    for c in d.cius.values():
        fases[c.phase] = fases.get(c.phase, 0) + 1
        tipos[c.type] = tipos.get(c.type, 0) + 1
    mapeados = sum(len(c.misconception_ids()) for c in d.cius.values())

    linhas = [
        "domínio        %s" % d.id,
        "hash           %s" % d.hash,
        "KCs            %d  (%d exigem diagrama: %s)"
        % (len(d.kcs), sum(1 for k in d.kcs if d.requires_diagram(k)),
           ", ".join(k for k in d.teaching_sequence() if d.requires_diagram(k))),
        "nós            %d  (%d base, %d inferência)" % (nos, base, nos - base),
        "simplificados  %d/%d com `plain`, %d com figura  (KCs: %s)" % (
            sum(1 for k in d.kcs.values() for n in k.nodes.values() if n.plain),
            nos,
            sum(1 for k in d.kcs.values() for n in k.nodes.values() if n.figure),
            ", ".join(sorted(k.id for k in d.kcs.values()
                             if any(n.plain for n in k.nodes.values()))) or "nenhum"),
        "crenças        %d  (%d fundacionais, %d derivacionais)"
        % (len(d.misconceptions), fund, len(d.misconceptions) - fund),
        "proveniência   %s" % "  ".join(
            "%s=%d" % (g, graus.get(g, 0)) for g in ("D", "T", "L", "N", "E")),
        "CIUs           %d  (%s)" % (
            len(d.cius), ", ".join("%s=%d" % kv for kv in sorted(fases.items()))),
        "tipos          %s" % ", ".join("%s=%d" % kv for kv in sorted(tipos.items())),
        "mapeamentos    %d  (%d/%d crenças detectáveis)" % (
            mapeados,
            len({m for c in d.cius.values() for m in c.misconception_ids()}),
            len(d.misconceptions)),
        "plano médio    %.1f passos  (mín %d, máx %d)"
        % (sum(planos) / len(planos), min(planos), max(planos)),
        "piloto         %s" % ", ".join(d.pilot_sequence),
    ]
    return "\n".join("  " + l for l in linhas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Valida o domínio declarativo do Structura.")
    p.add_argument("path", nargs="?", default=None, help="diretório do domínio")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--strict", action="store_true", help="avisos também derrubam a saída")
    args = p.parse_args(argv)

    try:
        d = load(args.path)
    except DomainError as exc:
        print("CARGA FALHOU — o sistema não subiria.\n")
        for prob in exc.problemas:
            print("  ERRO  %s" % prob)
        print("\n%d problema(s) estrutural(is)." % len(exc.problemas))
        return 1

    print("Carga OK: %d KCs, %d crenças, %d CIUs.\n"
          % (len(d.kcs), len(d.misconceptions), len(d.cius)))

    erros: list[str] = []
    for nome, fn in BLOQUEANTES:
        achados = fn(d)
        print("  [%s] %s" % ("ok   " if not achados else "FALHA", nome))
        for a in achados:
            print("         %s" % a)
        erros.extend(achados)

    avisos: list[str] = []
    for nome, fn in AVISOS:
        achados = fn(d)
        print("  [%s] %s" % ("ok   " if not achados else "AVISO", nome))
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
