# -*- coding: utf-8 -*-
"""O inventário de conceitos, e o portão que ele controla.

O PRINCÍPIO: uma cadeia de refutação só pode ser acionada se todos os
seus degraus forem respondíveis com conhecimentos que o aluno já teve
oportunidade de aprender.

A MEDIÇÃO QUE O TORNOU NECESSÁRIO. Nas 180 detecções de crença da
varredura do kc_02, **135 acontecem no nível 1**, 99 delas depois de um
erro só. E a cadeia `pointer_has_no_address` pergunta sobre `sizeof p`,
que no tópico só aparece em item de **nível 2**, e sobre `int **pp`, que
só aparece em item de **nível 3**. A pessoa cai na descida antes de
encontrar qualquer um dos dois — e responde no chute um degrau que
deveria medir a crença dela.

"ESTÁ NO MATERIAL" É O CRITÉRIO ERRADO, e foi o meu. O certo tem duas
partes: o recurso aparece no tópico, E aparece em ENSINO. Item de prova
não autoriza o uso numa cadeia de recuperação — é por isso que
`so_avaliado` é um estado próprio, e não um sinônimo de disponível.

A LISTA COMEÇA VAZIA. Com ela vazia, nenhuma cadeia roda e o sistema cai
na refutação afirmativa em todo lugar. É conservador de propósito: uma
lista preenchida por suposição faria o portão medir a suposição de quem
a escreveu sobre a ementa da disciplina. A liberação é progressiva, uma
entrada por vez, e cada uma carrega a evidência de ONDE aquilo foi
ensinado — a rastreabilidade é o que separa isto de uma lista de desejos.
"""
from __future__ import annotations

import os
import pathlib

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent / "dominio"
ARQUIVO = RAIZ / "conceitos.yaml"


def caminho() -> pathlib.Path:
    """O inventário em uso. `STRUCTURA_CONCEITOS` troca o arquivo.

    EXISTE PARA TESTE, e o princípio que o governa está escrito em
    `docs/processo.md`: um teste pode criar um mundo pedagógico explícito
    para exercitar o MECANISMO, e nunca pode transformar esse mundo
    artificial em evidência de que a disciplina ensinou aquilo. O portão
    continua rodando contra o inventário de verdade em
    `mvp/dominio/conceitos.yaml`, que começa vazio.
    """
    return pathlib.Path(os.environ.get("STRUCTURA_CONCEITOS") or ARQUIVO)

# Os quatro estados. A diferença entre os dois do meio é a que a medição
# do kc_02 produziu, e é a razão de este módulo existir.
DISPONIVEL = "disponivel"          # ensinado: pode ser exigido
SO_AVALIADO = "so_avaliado"        # cobrado em item, nunca ensinado
NAO_INTRODUZIDO = "nao_introduzido"  # não aparece ainda
DESCONHECIDO = "desconhecido"      # ninguém declarou: o padrão é NÃO
ESTADOS = (DISPONIVEL, SO_AVALIADO, NAO_INTRODUZIDO, DESCONHECIDO)

# A função pedagógica de cada degrau. Declarar obriga quem escreve a
# responder "o que esta pergunta faz?" antes de escrevê-la — e um degrau
# que não faz nenhuma das três provavelmente é dispensável.
EXPLICITAR = "explicitar"    # fazer assumir as consequências da crença
CONFRONTAR = "confrontar"    # apresentar o que não combina com ela
RECONSTRUIR = "reconstruir"  # ajudar a formular a compreensão melhor
FUNCOES = (EXPLICITAR, CONFRONTAR, RECONSTRUIR)

_cache: tuple[str, dict] | None = None


def recarrega() -> dict:
    """Esquece o inventário em memória.

    Para teste, e para quem editar o arquivo com o servidor no ar: sem
    isto, liberar um conceito exigiria reiniciar o processo.
    """
    global _cache
    _cache = None
    return carrega()


def carrega(onde: pathlib.Path | None = None) -> dict:
    """O inventário, do disco. Arquivo ausente é inventário vazio.

    O cache é guardado COM o caminho de onde veio: trocar
    `STRUCTURA_CONCEITOS` e receber o inventário anterior seria o tipo de
    silêncio que este módulo existe para não ter.
    """
    global _cache
    p = pathlib.Path(onde) if onde else caminho()
    if onde is None and _cache is not None and _cache[0] == str(p):
        return _cache[1]
    cru = {}
    if p.exists():
        cru = (yaml.safe_load(p.read_text(encoding="utf-8")) or {})
        cru = cru.get("conceitos") or {}
    inv = {}
    for cid, c in cru.items():
        c = c or {}
        inv[str(cid)] = {
            "nome": c.get("nome") or str(cid),
            "status": c.get("status") or DESCONHECIDO,
            "introduzido_em": c.get("introduzido_em") or "",
            "evidencia": c.get("evidencia") or "",
        }
    if onde is None:
        _cache = (str(p), inv)
    return inv


def status(cid: str) -> str:
    """O estado de um conceito. Id que ninguém declarou é DESCONHECIDO —
    o padrão é não, senão errar o nome do conceito viraria autorização."""
    return carrega().get(cid, {}).get("status", DESCONHECIDO)


def disponivel(cid: str) -> bool:
    return status(cid) == DISPONIVEL


def faltando(descida) -> tuple[str, ...]:
    """Os conceitos que a cadeia exige e que não estão disponíveis.

    Em ordem de primeira aparição, sem repetir: quem vai liberar precisa
    da lista, e ler a mesma entrada três vezes não ajuda.
    """
    vistos, falta = set(), []
    for p in descida.passos:
        for c in p.requer:
            if c not in vistos and not disponivel(c):
                vistos.add(c)
                falta.append(c)
    return tuple(falta)


def liberada(descida) -> bool:
    return not faltando(descida)


def relatorio(dominio) -> list[str]:
    """Uma linha por cadeia, dizendo se roda e o que falta para rodar.

    Bloqueio silencioso seria pior que bloqueio nenhum: com o inventário
    vazio TUDO para, e quem lê precisa saber qual conceito liberar para
    destravar qual cadeia.
    """
    linhas = []
    for cid in sorted(dominio.descidas):
        de = dominio.descidas[cid]
        falta = faltando(de)
        linhas.append(
            "crenca %-28s liberada=%-5s falta=%s"
            % (cid, de.liberada, ", ".join(falta) if falta else "-"))
    return linhas
