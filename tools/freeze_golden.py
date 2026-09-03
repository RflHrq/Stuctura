"""Recongela o golden dos planos de refutacao.

    python -m tools.freeze_golden

So rodar depois de uma mudanca DELIBERADA no grafo. O teste
`test_golden_dos_34_planos` existe para que uma mudanca acidental quebre;
recongelar sem olhar o diff derrota o proposito.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic
from engine.loader import load

DESTINO = Path(__file__).resolve().parent.parent / "tests" / "golden_plans.json"


def main() -> int:
    d = load()
    novo = {
        m.id: ["%s:%s" % r for r in socratic.full_plan(d, m.kc, m.node)]
        for m in sorted(d.misconceptions.values(), key=lambda x: x.id)
    }
    antigo = json.loads(DESTINO.read_text(encoding="utf-8")) if DESTINO.exists() else {}
    mudou = [k for k in set(novo) | set(antigo) if novo.get(k) != antigo.get(k)]
    DESTINO.write_text(json.dumps(novo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("%d planos congelados; %d mudaram: %s"
          % (len(novo), len(mudou), ", ".join(sorted(mudou)) or "-"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
