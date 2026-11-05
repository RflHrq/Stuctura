# -*- coding: utf-8 -*-
"""A aprovação pedagógica de cada cadeia, separada do inventário.

O PRINCÍPIO:

    A disponibilidade de um conceito autoriza seu uso potencial. Não
    autoriza, por si só, a utilização de qualquer cadeia que o contenha.

A MEDIÇÃO QUE O OBRIGOU. Com `comparacao_de_ponteiros` bloqueado, uma
simulação mostrou que liberá-lo abriria **duas** cadeias de uma vez —
`pointer_and_target_are_one` e `pointer_is_data`. E a primeira reprova
em três das cinco perguntas da revisão pedagógica, incluindo o degrau
de abertura, que exige declaração múltipla e reatribuição de ponteiro,
nenhuma das duas ensinada.

Uma decisão CURRICULAR estava decidindo uma questão PEDAGÓGICA:

    o conceito foi ensinado?      -> inventário, `conceitos.py`
    esta sequência confronta?     -> aprovação, aqui

São perguntas diferentes, com evidências diferentes e aprovadores
diferentes. O motor exige as duas.

POR QUE O ARQUIVO É SEPARADO do das cadeias: quem escreve a cadeia não
pode ser a mesma instância que a certifica. O autor declara `requer` no
YAML da descida; o aprovador escreve em `aprovacoes.yaml`. Misturar os
dois no mesmo arquivo convida a escrever os dois na mesma passada, que
é o defeito que esta separação existe para impedir.
"""
from __future__ import annotations

import os
import pathlib

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent / "dominio"
ARQUIVO = RAIZ / "aprovacoes.yaml"

# Os estados. O padrão é SEM_REVISAO: cadeia nova nasce bloqueada, e
# esquecer de revisar não vira autorização.
APROVADA = "aprovada"          # passou na revisão pedagógica
EM_REVISAO = "em_revisao"      # sendo revisada: não roda
REPROVADA = "reprovada"        # revisada e recusada, com motivo
SEM_REVISAO = "sem_revisao"    # ninguém olhou — o padrão
ESTADOS = (APROVADA, EM_REVISAO, REPROVADA, SEM_REVISAO)

_cache: tuple[str, dict] | None = None


def caminho() -> pathlib.Path:
    """O arquivo em uso. `STRUCTURA_APROVACOES` troca, para teste.

    Mesmo princípio do inventário de conceitos: um teste pode criar um
    mundo explícito para exercitar o mecanismo, e nunca pode transformar
    esse mundo em evidência de que alguém revisou a cadeia.
    """
    return pathlib.Path(os.environ.get("STRUCTURA_APROVACOES") or ARQUIVO)


def recarrega() -> dict:
    global _cache
    _cache = None
    return carrega()


def carrega(onde: pathlib.Path | None = None) -> dict:
    global _cache
    p = pathlib.Path(onde) if onde else caminho()
    if onde is None and _cache is not None and _cache[0] == str(p):
        return _cache[1]
    cru = {}
    if p.exists():
        cru = (yaml.safe_load(p.read_text(encoding="utf-8")) or {})
        cru = cru.get("aprovacoes") or {}
    inv = {}
    for cid, a in cru.items():
        a = a or {}
        inv[str(cid)] = {
            "status": a.get("status") or SEM_REVISAO,
            "em": a.get("em") or "",
            "por": a.get("por") or "",
            "nota": a.get("nota") or "",
        }
    if onde is None:
        _cache = (str(p), inv)
    return inv


def status(crenca: str) -> str:
    return carrega().get(crenca, {}).get("status", SEM_REVISAO)


def aprovada(crenca: str) -> bool:
    return status(crenca) == APROVADA


def relatorio(dominio) -> list[str]:
    """Uma linha por cadeia, com AS DUAS autorizações.

    Quem lê precisa saber qual das duas falta: são consertos diferentes,
    feitos por gente diferente. Faltar conceito é trabalho de material;
    faltar aprovação é trabalho de revisão da sequência.
    """
    from mvp import conceitos

    linhas = []
    for cid in sorted(dominio.descidas):
        de = dominio.descidas[cid]
        falta = conceitos.faltando(de)
        linhas.append(
            "%-28s liberada=%-5s aprovada=%-11s %s"
            % (cid, de.liberada, status(cid),
               ("falta: " + ", ".join(falta)) if falta else ""))
    return linhas
