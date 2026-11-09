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

# O evento que abre uma unidade, e o único que diz o TÓPICO dela. É por
# ele que `aberturas` e `mvp/historico.py` descobrem o que uma pessoa
# atravessou — e é por ele estar sozinho nessa função que uma linha
# ilegível de abertura é tratada com cuidado especial.
ABERTURA_DA_UNIDADE = "unidade_iniciada"
FECHO_DA_UNIDADE = "unidade_encerrada"

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
#   3  a descida passou a distinguir DESCONHECER de MANTER.
#      `descida_passo` gravava `escolha: "decorre"`, que queria dizer
#      "seguiu a crença, motivo desconhecido"; passou a gravar
#      `declarado: "mantenho"`, que quer dizer "seguiu a crença E NÃO
#      declarou desconhecer o recurso". Mesmo gesto, outra leitura — e
#      sessão v2 não tem como sustentar a segunda, porque nela não havia
#      como declarar. Entrou `descida_sem_recurso`, e o
#      `descida_iniciada` passou a gravar os requisitos de cada degrau.
#
# Linha sem o campo é anterior a isto: veio do ciclo 1, e `VERSAO_ZERO`
# é como ela aparece na leitura.
#
# 09/11/2026 -- `conceito_apresentado` ENTROU E A VERSAO NAO SUBIU, e o
# motivo precisa ficar escrito porque a decisão não é óbvia.
#
# O que o gate de `reconstroi` protege é a REEXECUÇÃO: a v2 mudou o
# significado do índice de `escolha` e a v3 o da resposta na descida —
# nos dois casos um campo de ENTRADA passou a querer dizer outra coisa, e
# reexecutar devolveria afirmação que a sessão não sustenta. O evento
# conceitual não toca entrada nenhuma: ele é linha nova, aditiva, e
# reexecutar um log v3 de ontem com o código de hoje dá o mesmo estado.
# Subir para 4 faria `reconstroi` RECUSAR todos os logs já gravados, o
# que é regressão de verdade em troca de nada.
#
# O QUE SE PERDE, e é honesto registrar: a ausência de
# `conceito_apresentado` numa linha v3 fica ambígua — pode ser "nenhum
# conceito declarado naquele cartão" (doze dos treze tópicos, hoje) ou
# "gravada antes de o evento existir". Isso é tolerável porque NÃO HÁ
# COLETA GRAVADA: os logs de hoje são de desenvolvimento, e toda sessão
# de piloto terá o evento. Com coleta em andamento, esta mesma mudança
# exigiria o número novo.
VERSAO = 3
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


def aberturas(destino: Path | None = None) -> tuple[frozenset, tuple[str, ...]]:
    """Os pares `(código, tópico)` abertos no log, e as linhas ilegíveis.

    O que o guarda de identidade de `app.py` consulta. Ele recusava pelo
    CÓDIGO sozinho, e passou a recusar pelo PAR em 09/11/2026: num log
    único — que é o que um histórico individual quer — recusar pelo
    código impediria o participante de entrar no segundo tópico, e o
    guarda que protege a identidade seria o mesmo que impede o histórico.

    AS LINHAS ILEGÍVEIS VOLTAM CRUAS, e não só contadas, porque o tópico
    está SÓ no `unidade_iniciada`. Se justamente essa linha sair pela
    metade — o caso documentado em `VERSAO`, o processo morrendo no meio
    de uma escrita —, o guarda não tem como saber de que tópico era
    aquela sessão, e quem chama precisa poder procurar o código no texto
    cru para decidir. Tolerante no resto: uma linha quebrada de OUTRO
    participante não pode impedir o começo de uma sessão.
    """
    caminho = Path(destino) if destino else DESTINO
    if not caminho.exists():
        return frozenset(), ()
    pares, ilegiveis = set(), []
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    for i, linha in enumerate(linhas):
        if not linha.strip():
            continue
        try:
            dado = json.loads(linha)
        except json.JSONDecodeError:
            # A última tem desculpa, como em `_le` — mas aqui ela entra
            # na lista mesmo assim: descartá-la é seguro para reexecutar
            # e perigoso para decidir identidade.
            ilegiveis.append(linha)
            continue
        if dado.get("tipo") == ABERTURA_DA_UNIDADE:
            pares.add((str(dado.get("sessao", "")),
                       str(dado.get("topico", ""))))
    return frozenset(pares), tuple(ilegiveis)


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

    # UMA SESSÃO ANTERIOR À VERSÃO 2 NÃO É REEXECUTÁVEL, e não há
    # semente que a salve. Eu tentei `semente=""`, raciocinando que a
    # camada 1 não era permutada no `v1`. Está errado por dois lados:
    #
    #   - semente vazia NÃO é a identidade. Ela devolve a ordem do
    #     arquivo em 18% dos itens; nos outros 82% o índice gravado é
    #     lido contra uma permutação que ninguém viu, e um acerto vira
    #     erro COM uma crença atribuída que a pessoa nunca escolheu;
    #   - no `v1` as razões já eram permutadas, com a sessão como
    #     semente. Passar `""` conserta uma camada que não estava
    #     quebrada e quebra outra que estava certa.
    #
    # Nenhuma semente serve para as duas ao mesmo tempo. Devolver um
    # estado assim é exatamente o "plausível e errado" que esta classe
    # existe para impedir, e num instrumento de pesquisa isso é pior do
    # que não devolver nada.
    versao = int(abertura.get("v") or VERSAO_ZERO)
    if versao < VERSAO:
        raise LogIncompleto(
            "a sessão %r foi gravada na versão %d do log, e a %d não a "
            "reexecuta. A v2 mudou o significado do índice de `escolha` "
            "(era posição no arquivo, passou a ser posição na tela) e a "
            "v3 mudou o da resposta na descida (seguir a crença deixou "
            "de querer dizer 'motivo desconhecido' e passou a querer "
            "dizer 'não declarou desconhecer'). Reexecutar devolveria "
            "afirmações que a sessão não tem como sustentar. O log "
            "continua legível para análise; reexecutável, não."
            % (sessao, versao, VERSAO))
    t = motor.inicia(d, semente=sessao)
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
