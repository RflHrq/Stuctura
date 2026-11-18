"""O caminho sugerido dos tópicos, lido de `mvp/dominio/caminho.yaml`.

A ordem é sugestão (docs/interface.md, seção 7): todos os tópicos ficam
abertos. Este módulo só lê o arquivo; que a ordem respeita o que cada
tópico pede antes é conferido em `mvp/test_caminho.py`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ARQUIVO = Path(__file__).resolve().parent / "dominio" / "caminho.yaml"


@lru_cache(maxsize=1)
def _cru() -> dict:
    return yaml.safe_load(ARQUIVO.read_text(encoding="utf-8"))


def ordem() -> list[str]:
    """Os tópicos na ordem do caminho: o tronco e, por último, os do fim."""
    return [p["topico"] for p in _cru()["ordem"]] + fim()


def fim() -> list[str]:
    """Os tópicos em que o caminho se abre, lado a lado."""
    return [p["topico"] for p in _cru()["fim"]]


def rotulos() -> dict[str, str]:
    """O nome curto de cada tópico, para escrever ao lado da parada."""
    return {p["topico"]: p["rotulo"]
            for p in _cru()["ordem"] + _cru()["fim"]}
