"""O registro da trilha: uma linha por entrada e por evento.

    grava(destino, sessao, eventos, entrada)
    linhas = le(destino, sessao)

É outro registro, em outro arquivo, com vocabulário e versão próprios —
não é o `mvp/log.py`, e nada daqui escreve lá. O painel do pesquisador e
a exportação leem o registro do fluxo atual, e continuam lendo só ele
(docs/trilha.md, seção 3).

O formato é o mesmo, de propósito: JSON por linha, com os quatro campos
da casa (`v`, `ts`, `sessao`, `tipo`), e a ENTRADA gravada antes dos
eventos que ela provocou. O motor da trilha é puro, então a entrada é
tudo o que é preciso para refazer a sessão — a retomada depois de um
reinício do servidor é reexecutar estas linhas, e fica para a fatia 3.

A pasta do arquivo nasce na PRIMEIRA gravação, e não quando o app é
criado: montar a trilha num portal não pode fazer aparecer uma pasta
vazia ao lado dos registros de quem nunca abriu a trilha.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from mvp.log import agora
from mvp.motor import Evento

VERSAO = 1

# O tipo da linha de entrada. Não é evento do motor: o motor não sabe que
# existe registro.
ENTRADA = "entrada_recebida"

# Os campos da casa. Nenhum dado de evento pode ocupá-los.
RESERVADOS = ("v", "ts", "sessao", "tipo")


def _linha(sessao: str, tipo: str, dados) -> dict:
    """Uma linha, com os campos da casa protegidos.

    Um dado chamado `tipo` trocaria o nome do próprio evento sem erro
    nenhum — o registro do fluxo atual já passou por isso. O campo da
    casa fica, e o dado é escrito ao lado, com sufixo.
    """
    linha = {"v": VERSAO, "ts": agora(), "sessao": sessao, "tipo": tipo}
    for chave, valor in dict(dados).items():
        linha[chave + "_do_evento" if chave in RESERVADOS else chave] = valor
    return linha


def grava(destino: Path, sessao: str, eventos: Iterable[Evento],
          entrada=None) -> None:
    """Uma chamada ao motor, gravada: a entrada e o que ela provocou."""
    caminho = Path(destino)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8") as f:
        if entrada is not None:
            f.write(json.dumps(_linha(sessao, ENTRADA, asdict(entrada)),
                               ensure_ascii=False) + "\n")
        for e in eventos:
            f.write(json.dumps(_linha(sessao, e.tipo, e.dados),
                               ensure_ascii=False) + "\n")


def le(destino: Path, sessao: str | None = None) -> list[dict]:
    """As linhas, na ordem em que foram escritas. Sem arquivo, lista vazia."""
    caminho = Path(destino)
    if not caminho.exists():
        return []
    linhas = []
    with caminho.open(encoding="utf-8") as f:
        for bruta in f:
            if not bruta.strip():
                continue
            linha = json.loads(bruta)
            if sessao is None or linha.get("sessao") == sessao:
                linhas.append(linha)
    return linhas
