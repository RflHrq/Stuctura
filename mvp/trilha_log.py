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
tudo o que é preciso para refazer a sessão: `reconstroi` reexecuta estas
linhas, e é assim que o código de um participante sobrevive a um
reinício do servidor. A abertura grava a assinatura do conteúdo, e uma
sessão só é refeita sobre a MESMA escada em que começou.

A pasta do arquivo nasce na PRIMEIRA gravação, e não quando o app é
criado: montar a trilha num portal não pode fazer aparecer uma pasta
vazia ao lado dos registros de quem nunca abriu a trilha.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from pathlib import Path
from typing import Iterable

from mvp import trilha
from mvp.log import agora
from mvp.motor import Evento
from mvp.trilha_escada import assinatura

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


class RegistroNaoReexecutavel(Exception):
    """A sessão está no registro e não dá para refazê-la a partir dele.

    A mensagem é para a pessoa que está na frente da tela, ou para quem
    organiza a sessão: diz o que houve em palavras de quem usa, não de
    quem programa.
    """


def _bruto(destino: Path):
    """Cada linha do arquivo: `(linha, None)`, ou `(None, texto)` se ela
    não é JSON — o que uma queda no meio de uma gravação deixa para trás."""
    caminho = Path(destino)
    if not caminho.exists():
        return
    with caminho.open(encoding="utf-8") as f:
        for bruta in f:
            if not bruta.strip():
                continue
            try:
                linha = json.loads(bruta)
            except ValueError:
                yield None, bruta
                continue
            if isinstance(linha, dict):
                yield linha, None
            else:
                yield None, bruta


def le(destino: Path, sessao: str | None = None) -> list[dict]:
    """As linhas legíveis, na ordem em que foram escritas.

    Sem arquivo, lista vazia. Linha quebrada é PULADA: uma queda no meio
    de uma gravação não pode tirar do ar todas as sessões seguintes. Quem
    precisa saber se a linha quebrada era de uma sessão específica —
    `existe` e `reconstroi` — olha o texto dela.
    """
    return [linha for linha, _ in _bruto(destino)
            if linha is not None
            and (sessao is None or linha.get("sessao") == sessao)]


def quebradas_de(destino: Path, sessao: str) -> list[str]:
    """As linhas ilegíveis que trazem o código daquela sessão."""
    return [texto for linha, texto in _bruto(destino)
            if linha is None and sessao in texto]


def existe(destino: Path, sessao: str) -> bool:
    """Se há no registro alguma linha daquela sessão — legível ou não.

    Conservador de propósito: uma linha quebrada que traga o código conta
    como da sessão. Tratar como livre um código que já tem linha no
    arquivo é o que juntaria duas pessoas num registro só.
    """
    return any((linha is not None and linha.get("sessao") == sessao)
               or (linha is None and sessao in texto)
               for linha, texto in _bruto(destino))


CAMPOS_DA_ENTRADA = tuple(f.name for f in fields(trilha.Entrada))


def reconstroi(d, escadas, destino: Path, sessao: str) -> "trilha.Transicao":
    """A sessão de volta, reexecutando as entradas gravadas no motor.

    O motor é puro: as mesmas entradas, sobre o mesmo conteúdo, dão o
    mesmo estado e a mesma tela. É o que faz o código do participante
    sobreviver a um reinício do servidor.

    Não grava nada: reexecutar produz os mesmos eventos outra vez.

    Três coisas impedem, e as três levantam `RegistroNaoReexecutavel`:
    uma linha quebrada da própria sessão (falta uma entrada, e o estado
    sairia plausível e errado); o conteúdo ter mudado desde que a sessão
    começou; e uma entrada que o motor de hoje não aceita.
    """
    if quebradas_de(destino, sessao):
        raise RegistroNaoReexecutavel(
            "Não foi possível retomar a sessão %s: o registro dela ficou "
            "incompleto. Use outro código e avise quem organiza a sessão."
            % sessao)
    linhas = le(destino, sessao)
    abertura = next((l for l in linhas if l["tipo"] == "trilha_iniciada"), None)
    if abertura is None or abertura.get("escada") != assinatura(escadas):
        raise RegistroNaoReexecutavel(
            "Não foi possível retomar a sessão %s: o conteúdo deste tópico "
            "mudou desde que ela começou. Use outro código para começar de "
            "novo." % sessao)
    t = trilha.inicia(d, escadas, semente=sessao)
    for l in linhas:
        if l["tipo"] != ENTRADA:
            continue
        campos = {c: l[c] for c in CAMPOS_DA_ENTRADA if c in l}
        campos["pecas"] = tuple(campos.get("pecas") or ())
        # O número da tela não é conferido de novo: o registro só guarda
        # entrada que foi aceita, e a reexecução anda uma por tela.
        campos["passo"] = None
        try:
            t = trilha.avanca(d, escadas, t.estado, trilha.Entrada(**campos))
        except (trilha.EntradaInvalida, ValueError) as erro:
            raise RegistroNaoReexecutavel(
                "Não foi possível retomar a sessão %s: uma resposta "
                "gravada não cabe mais na trilha de hoje. Use outro "
                "código para começar de novo." % sessao) from erro
    return t
