"""Log append-only, um arquivo JSON Lines por execução.

Sem banco: o MVP precisa guardar o que aconteceu, não gerenciar coleta. Cada
linha é um evento com carimbo de tempo, e a sessão inteira é legível com
`cat`. Trocar isto por SQLite depois não muda o motor, que só devolve
eventos.

O estado da sessão NÃO é gravado: ele é reconstruído reexecutando as
respostas do log. É o que mantém o log como fonte única.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from mvp.motor import Evento

DESTINO = Path(__file__).resolve().parent / "dados" / "eventos.jsonl"


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def grava(sessao: str, eventos: Iterable[Evento], destino: Path | None = None) -> None:
    caminho = Path(destino) if destino else DESTINO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8") as f:
        for e in eventos:
            linha = {"ts": agora(), "sessao": sessao, "tipo": e.tipo, **dict(e.dados)}
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def le(sessao: str | None = None, destino: Path | None = None) -> list[dict]:
    caminho = Path(destino) if destino else DESTINO
    if not caminho.exists():
        return []
    saida = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        dado = json.loads(linha)
        if sessao is None or dado.get("sessao") == sessao:
            saida.append(dado)
    return saida
