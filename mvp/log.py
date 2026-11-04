"""Log append-only, um arquivo JSON Lines por execução.

Sem banco: o MVP precisa guardar o que aconteceu, não gerenciar coleta. Cada
linha é um evento com carimbo de tempo, e a sessão inteira é legível com
`cat`. Trocar isto por SQLite depois não muda o motor, que só devolve
eventos.

O estado da sessão NÃO é gravado: ele é reconstruído reexecutando as
respostas do log (`reconstroi`). É o que mantém o log como fonte única.

DUAS COISAS DIFERENTES NO MESMO ARQUIVO
---------------------------------------
**As entradas** (`entrada_recebida`) são o que a pessoa fez: uma linha por
chamada ao motor. São o registro de recuperação, e só elas são reexecutadas.

**Os eventos** são o que aquilo significou. São o registro de pesquisa, e
mudam de forma conforme o instrumento evolui.

Separá-los é o que permite reconstruir uma sessão sem reimplementar as
regras: a reexecução não lê nenhum evento, e por isso não pode divergir do
motor. O preço é que o texto do teach-back aparece duas vezes na mesma
linha de sessão — uma como entrada, outra como evento. Apagar um
participante continua sendo apagar as linhas com o código dele.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from mvp import motor
from mvp.motor import Evento

# Onde a sessão é escrita.
#
#   STRUCTURA_LOG=ensaios/e01.jsonl python -m mvp.app
#
# `scripts/copia.sh` e `scripts/participante.sh` já liam esta variável, e o
# servidor não: quem apontasse os procedimentos para outro arquivo copiaria
# e apagaria num log que a sessão não estava usando. Dado de ensaio junto
# com dado de desenvolvimento no mesmo arquivo é o que esta variável
# existe para evitar.
DESTINO = Path(os.environ.get("STRUCTURA_LOG")
               or Path(__file__).resolve().parent / "dados" / "eventos.jsonl")

# O tipo da linha de entrada. Não é um evento do motor: o motor não sabe
# que existe log.
ENTRADA = "entrada_recebida"

# Versão do formato, em toda linha gravada.
#
# O formato já mudou duas vezes no primeiro ciclo — a T10 acrescentou
# `entrada_recebida`, a T12 acrescentou `belief_retested` — e a única
# pista era a ausência de campos. Com coleta em andamento e código
# evoluindo, é o caminho curto para uma análise que mistura formatos sem
# perceber qual participante foi medido com qual instrumento.
#
# Sobe quando o significado de uma linha muda, não quando o código muda.
#
#   1  primeiro formato versionado (ciclo 2). As três camadas, o
#      teach-back, a entrada para reexecução e o reteste já estão aqui.
#   2  a camada 1 passou a ser permutada. O índice de `entrada_recebida`
#      deixou de querer dizer "posição no YAML" e passou a querer dizer
#      "posição na tela" — o mesmo número, outra alternativa. E
#      `atividade_apresentada` ganhou `ordem`, a permutação mostrada.
#
# Linha sem o campo é anterior a isto: veio do ciclo 1, e `VERSAO_ZERO`
# é como ela aparece na leitura.
VERSAO = 2
VERSAO_ZERO = 0

CAMPOS_DA_ENTRADA = tuple(f.name for f in fields(motor.Resposta))


class LogIncompleto(Exception):
    """O log existe e não dá para reexecutar o que está nele.

    Devolver um estado parcial seria pior do que falhar: uma sessão em
    branco tem a mesma cara de uma sessão que acabou de começar.
    """


class LinhaCorrompida(LogIncompleto):
    """Uma linha do meio do arquivo não é JSON.

    A última linha tem desculpa — o processo pode ter morrido no meio da
    escrita. Uma do meio, não: pular em silêncio significaria reexecutar a
    sessão sem uma das respostas, e o estado sairia plausível e errado.
    """


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# Os campos da casa: quem lê o log se orienta por eles, e a reexecução
# depende deles. Nenhum dado de evento pode ocupá-los.
RESERVADOS = ("v", "ts", "sessao", "tipo")


def _linha(sessao: str, tipo: str, dados) -> dict:
    """Uma linha do log, com os campos da casa protegidos.

    A linha era montada com `{..., "tipo": e.tipo, **dados}`, e `**dados`
    vem DEPOIS: um evento que trouxesse um dado chamado `tipo` trocava o
    nome do próprio evento, sem erro nenhum. Não é hipótese — aconteceu:
    `evidencia_apresentada` levava o tipo da evidência num campo `tipo` e
    saiu no log como uma linha `erro_de_compilacao`, que a reexecução não
    sabe ler e que a análise contaria como outro evento.

    Perder a sessão por causa disto seria pior que a colisão: quem está na
    frente da tela não tem culpa de um nome de campo. Então o campo da
    casa fica, o dado é escrito ao lado com sufixo, e nada se perde — e o
    sufixo é o sinal, visível na análise, de que alguém precisa renomear
    aquele campo.
    """
    linha = {"v": VERSAO, "ts": agora(), "sessao": sessao, "tipo": tipo}
    for chave, valor in dict(dados).items():
        linha[chave + "_do_evento" if chave in RESERVADOS else chave] = valor
    return linha


def grava(sessao: str, eventos: Iterable[Evento], destino: Path | None = None,
          entrada: motor.Resposta | None = None) -> None:
    """Uma chamada ao motor, gravada: a entrada e o que ela provocou.

    A entrada vem primeiro, na ordem em que aconteceu — quem lê o arquivo
    direto vê causa e efeito, e a reexecução não precisa reordenar nada.
    """
    caminho = Path(destino) if destino else DESTINO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8") as f:
        if entrada is not None:
            f.write(json.dumps(_linha(sessao, ENTRADA, asdict(entrada)),
                               ensure_ascii=False) + "\n")
        for e in eventos:
            f.write(json.dumps(_linha(sessao, e.tipo, e.dados),
                               ensure_ascii=False) + "\n")


def le_tolerante(destino: Path | None = None) -> tuple[list[dict], int]:
    """O arquivo inteiro, pulando linhas ilegíveis, e quantas pulou.

    Modo da LISTA do painel, e só dela. O painel existe para funcionar
    **depois** de um travamento, e perder trinta e cinco sessões por causa
    de uma linha é o oposto disso. Contar as puladas é o que separa
    tolerar de esconder — a tela diz quantas.

    A reexecução nunca passa por aqui: pular uma entrada produziria uma
    sessão sem uma das respostas, e o estado sairia plausível e errado.
    Isso é garantia da T10, e não se abre mão dela.
    """
    return _le(None, destino, estrito=False)


def le(sessao: str | None = None, destino: Path | None = None) -> list[dict]:
    """As linhas do log, na ordem em que foram escritas. Estrito."""
    return _le(sessao, destino, estrito=True)[0]


def _le(sessao: str | None, destino: Path | None,
        *, estrito: bool) -> tuple[list[dict], int]:
    """A leitura de verdade. Devolve as linhas e quantas foram puladas.

    A ÚLTIMA linha pode estar pela metade: o processo morre no meio de uma
    escrita, e é justamente a queda que a retomada existe para atender.
    Perder o arquivo inteiro por causa dela seria o pior desfecho
    possível, então ela é descartada — nos dois modos.

    Qualquer OUTRA linha quebrada é corrupção, e só o modo tolerante a
    pula.
    """
    caminho = Path(destino) if destino else DESTINO
    if not caminho.exists():
        return [], 0
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    saida: list[dict] = []
    ilegiveis = 0
    for i, linha in enumerate(linhas):
        if not linha.strip():
            continue
        try:
            dado = json.loads(linha)
        except json.JSONDecodeError as erro:
            if i == len(linhas) - 1:
                continue
            if estrito:
                raise LinhaCorrompida(
                    "linha %d de %s não é JSON: %s" % (i + 1, caminho.name, erro)
                ) from erro
            ilegiveis += 1
            continue
        # Linha sem versão veio do ciclo 1. Preencher na leitura é o que
        # permite ao resto do código comparar números em vez de testar a
        # ausência de um campo em cada lugar.
        dado.setdefault("v", VERSAO_ZERO)
        if sessao is None or dado.get("sessao") == sessao:
            saida.append(dado)
    return saida, ilegiveis


def _entrada_de(linha: dict) -> motor.Resposta:
    """Campo que o log não tem assume o padrão; campo que o motor não
    conhece é ignorado. É o que faz um log de ontem rodar no motor de hoje.
    """
    return motor.Resposta(**{c: linha[c] for c in CAMPOS_DA_ENTRADA
                             if c in linha})


def reconstroi(d: motor.Dominio, sessao: str,
               destino: Path | None = None) -> motor.Transicao | None:
    """A sessão de volta, reexecutando o log no motor.

    Devolve a transição inteira — estado e tela —, porque quem retoma
    precisa saber não só em que ponto a pessoa parou, mas o que estava na
    frente dela: a ordem das alternativas vem da semente, que é o código
    da sessão.

    Não grava nada. Reexecutar produz os mesmos eventos outra vez, e
    gravá-los duplicaria a sessão no arquivo que a análise vai ler.

    `None` quando a sessão não está no log. `LogIncompleto` quando ela
    está e não é reexecutável.
    """
    linhas = le(sessao, destino)
    if not linhas:
        return None

    abertura = next((x for x in linhas if x["tipo"] == "unidade_iniciada"), None)
    if abertura is None:
        raise LogIncompleto(
            "a sessão %r não tem abertura no log" % sessao)
    if abertura.get("topico") != d.id:
        # As entradas são posições de alternativas. Aplicadas a outro banco
        # de atividades elas apontam para outras opções, e o estado sai
        # plausível e errado.
        raise LogIncompleto(
            "a sessão %r é do tópico %r, e o domínio carregado é %r"
            % (sessao, abertura.get("topico"), d.id))

    entradas = [x for x in linhas if x["tipo"] == ENTRADA]
    if not entradas and len(linhas) > 1:
        raise LogIncompleto(
            "a sessão %r tem %d linhas e nenhuma entrada: log gravado antes "
            "de as entradas existirem, não é reexecutável"
            % (sessao, len(linhas)))

    # A SEMENTE DEPENDE DA VERSÃO. Numa sessão `v1` a camada 1 não era
    # permutada, e o índice gravado é posição de arquivo: reexecutar com
    # a semente leria outra alternativa, e um acerto viraria erro — o
    # estado sairia plausível e errado, que é o que esta classe inteira
    # existe para impedir. Semente vazia devolve a ordem de quem gravou.
    #
    # É remendo com prazo: funciona porque a camada 1 não era permutada
    # no `v1`. No dia em que a permutação mudar de novo, nem isso serve,
    # e aí a resposta é a versão RECUSAR em vez de reexecutar.
    versao = int(abertura.get("v") or VERSAO_ZERO)
    t = motor.inicia(d, semente=sessao if versao >= 2 else "")
    for i, linha in enumerate(entradas, 1):
        try:
            t = motor.avanca(d, t.estado, _entrada_de(linha))
        except motor.EscolhaInvalida as erro:
            # Entrada que o motor de HOJE recusa. Acontece com log escrito
            # antes de a R1 fechar o buraco: `{"escolha": -1}` era aceito e
            # virava um episódio. Reexecutar agora daria outro resultado —
            # então esta sessão não é reexecutável, e isso é dito em voz
            # alta em vez de virar erro de servidor.
            raise LogIncompleto(
                "a sessão %r tem na entrada %d algo que o motor não aceita "
                "mais (%s): log escrito por uma versão anterior"
                % (sessao, i, erro)) from erro
    return t
