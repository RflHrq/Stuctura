"""Sessões simuladas, para exercitar a análise antes de haver participantes.

O piloto é em setembro de 2026. Até lá o visualizador de percurso não tem o
que mostrar, e uma ferramenta de análise que ninguém consegue abrir não é
conferível — nem por você, nem pelo orientador.

Este módulo escreve sessões COMPLETAS no log, pelo caminho normal: chama o
mesmo `api.service` que a interface chama, e o motor grava os mesmos eventos.
Não há atalho, não há evento fabricado à mão. Por isso o que o visualizador
lê aqui é exatamente da forma que ele lerá o dado real.

DUAS GUARDAS, e as duas importam:

  banco separado   O padrão é `data/simulado.db`, NUNCA o banco do piloto.
                   Participante simulado misturado ao real contaminaria o
                   export do §12, e o erro seria descoberto tarde demais.

  código marcado   Os participantes são `SIM01`, `SIM02`… O piloto usa
                   `P01`–`P40`. Se algum dia os dois se encontrarem, dá
                   para separá-los com um filtro de uma linha.

    python -m tools.simular                    # 6 sessões em data/simulado.db
    python -m tools.simular --n 12 --seed 7
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import service
from engine.loader import load
from engine.session import option_order
from store import events as store_events

DB_PADRAO = Path("data/simulado.db")

# Perfis de resposta. Não são "níveis de aluno": são padrões de comportamento
# que o motor trata de maneira DIFERENTE, e é essa diferença que a análise
# precisa conseguir mostrar.
PERFIS = {
    "convicto": {
        "rotulo": "erra com convicção",
        "p_acerta": 0.15,          # quase sempre escolhe o distrator
        "confianca": "tenho certeza",
        "p_passo": 0.80,           # e sustenta bem a cadeia depois
    },
    "chutador": {
        "rotulo": "erra chutando",
        "p_acerta": 0.25,
        "confianca": "chutei",     # vira LACUNA, não crença
        "p_passo": 0.55,
    },
    "hesitante": {
        "rotulo": "acerta com pouca confiança",
        "p_acerta": 0.70,
        "confianca": "acho que sei",
        "p_passo": 0.70,
    },
    "solido": {
        "rotulo": "acerta com confiança",
        "p_acerta": 0.90,
        "confianca": "tenho certeza",
        "p_passo": 0.92,
    },
}


def uma_sessao(conn, domain, codigo: str, arm: str, perfil: str,
               rng: random.Random, kcs: list[str] | None = None) -> str:
    p = PERFIS[perfil]
    vista = service.create_session(
        conn, domain, codigo, arm, kcs,
        consented=True,
        prior_c=rng.choice(list(domain.study.prior_c_options)),
    )
    sid = vista.session_id

    for _ in range(600):
        acao = vista.action
        k = acao.kind

        if k == "intro":
            vista = service.acknowledge(conn, domain, sid, rng.randint(3000, 14000))

        elif k == "ciu":
            ciu = domain.cius[acao.ciu_id]
            ms = rng.randint(6000, 40000)
            if ciu.is_choice:
                # A ordem EXIBIDA é embaralhada por sessão: o índice que a
                # API espera é a POSIÇÃO na tela, não o índice do YAML.
                # Mandar o índice canônico registraria a alternativa errada
                # — foi exatamente esse o bug de dupla tradução do replay.
                ordem = option_order(domain, sid, ciu)
                certas = [i for i, c in enumerate(ordem) if ciu.options[c].correct]
                erradas = [i for i in range(len(ordem)) if i not in certas]
                quer = rng.random() < p["p_acerta"]
                pool = (certas if quer else erradas) or certas or erradas
                vista = service.submit_answer(
                    conn, domain, sid, acao.ciu_id, p["confianca"], ms,
                    option_idx=rng.choice(pool))
            else:
                texto = (ciu.answer or "não sei") if rng.random() < p["p_acerta"] \
                        else "não sei"
                vista = service.submit_answer(
                    conn, domain, sid, acao.ciu_id, p["confianca"], ms, text=texto)

        elif k == "diagram":
            vista = service.acknowledge(conn, domain, sid, rng.randint(4000, 25000))

        elif k == "ask":
            vista = service.submit_step(
                conn, domain, sid, rng.random() < p["p_passo"],
                rng.randint(2500, 22000), acao.kc, acao.node)

        elif k == "explain":
            vista = service.submit_step(
                conn, domain, sid, True, rng.randint(3000, 18000),
                acao.kc, acao.node)

        elif k == "conclude":
            vista = service.acknowledge(conn, domain, sid, rng.randint(5000, 30000))

        elif k == "done":
            return sid

        else:
            raise RuntimeError("ação inesperada: %r" % k)

    raise RuntimeError("sessão %s não terminou" % sid)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default=str(DB_PADRAO),
                   help="banco de saída (padrão: data/simulado.db)")
    p.add_argument("--n", type=int, default=6, help="quantas sessões")
    p.add_argument("--seed", type=int, default=20260930,
                   help="semente; a mesma semente dá as mesmas sessões")
    p.add_argument("--kcs", nargs="*", default=None,
                   help="sequência de KCs (padrão: o piloto)")
    args = p.parse_args(argv)

    if Path(args.db).name.startswith("structura"):
        print("recusado: %s parece ser o banco do piloto.\n"
              "Sessões simuladas em banco de coleta contaminam o export do §12."
              % args.db, file=sys.stderr)
        return 1

    domain = load()
    store_events.set_confidence_scale(domain.study.confidence_scale)
    conn = store_events.open_db(args.db)
    rng = random.Random(args.seed)

    perfis = list(PERFIS)
    print("domínio %s\nbanco   %s\n" % (domain.hash[:19], args.db))
    for i in range(args.n):
        codigo = "SIM%02d" % (i + 1)
        arm = "socratic" if i % 2 == 0 else "direct"
        perfil = perfis[i % len(perfis)]
        sid = uma_sessao(conn, domain, codigo, arm, perfil, rng, args.kcs)
        print("  %-6s %-9s %-28s %s" % (
            codigo, arm, PERFIS[perfil]["rotulo"], sid[:8]))

    conn.close()
    print("\n%d sessões escritas. Agora:\n"
          "  python -m tools.percurso --db %s -o analise/percursos.html"
          % (args.n, args.db))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
