"""As rotas da trilha.

    app = cria_app(dominio, escadas, destino)

Uma FÁBRICA, e não um módulo com variáveis: o estado das sessões mora
dentro de `cria_app`. O `mvp/app.py` guarda o domínio e as sessões em
variáveis do módulo, e por isso o portal precisa carregar o mesmo
arquivo treze vezes; aqui dois tópicos são duas chamadas.

A interface não decide nada. Ela manda o que a pessoa fez e desenha a
tela que volta; toda transição acontece em `mvp/trilha.py`, e o que
acontece vira linha em `mvp/trilha_log.py`.

    POST /sessoes                  abre; com um código que já tem sessão,
                                   devolve a tela em que ela estava —
                                   da memória, ou refeita pelo registro
    POST /sessoes/{sessao}/agir    uma entrada, uma transição. O pedido
                                   diz de que tela é (`passo`); se a
                                   tela já mudou, 409 com a tela atual
    POST /sessoes/{sessao}/retoma  a tela em que a sessão estava, pelo
                                   número — voltar sem código
    GET  /saude
    GET  /                         a página
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Mapping

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from mvp import motor, trilha, trilha_log
from mvp.dominio import Dominio
from mvp.motor import Evento
from mvp.trilha_escada import Escada, RespostaInvalida, faltando

AQUI = Path(__file__).resolve().parent

# O código do participante, quando quem abre informa um: o mesmo formato
# estreito do fluxo atual. Ele vai para toda linha do registro.
CODIGO = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,15}$")
# O número de uma sessão: o código, ou os doze caracteres sorteados de
# quem abriu sem código. Só o que tem essa forma vai buscar no registro.
SESSAO = re.compile(r"^(?:[0-9a-f]{12}|[A-Za-z][A-Za-z0-9_-]{0,15})$")

# Um episódio leva minutos, não horas.
LIMITE_MS = 2 * 60 * 60 * 1000
# O que se digita num degrau é um valor curto. O teto existe porque isto
# é escrito em disco: sem ele uma colagem acidental vira meio megabyte.
LIMITE_DO_TEXTO = 200
LIMITE_DE_PECAS = 40


class SessaoBody(BaseModel):
    codigo: str = ""


# Ação, certeza, modo e ritmo são palavras de uma lista fechada, e a mais
# longa tem treze letras. O teto existe porque a entrada aceita vai
# inteira para o registro: sem ele, um campo que o motor nem lê levaria
# o que viesse para o disco.
LIMITE_DA_PALAVRA = 32


class AcaoBody(BaseModel):
    acao: str = Field(default="responder", max_length=LIMITE_DA_PALAVRA)
    # De que tela o pedido é. Obrigatório: é o que impede uma resposta
    # repetida, reenviada ou de outra aba de valer para a tela seguinte.
    passo: int
    escolha: int | None = None
    razao: int | None = None
    confianca: str = Field(default="", max_length=LIMITE_DA_PALAVRA)
    pecas: list[int] = Field(default_factory=list, max_length=LIMITE_DE_PECAS)
    texto: str = Field(default="", max_length=LIMITE_DO_TEXTO)
    modo: str = Field(default="", max_length=LIMITE_DA_PALAVRA)
    ritmo: str = Field(default="", max_length=LIMITE_DA_PALAVRA)
    ms: int = Field(default=0, ge=0)


def _veredito(eventos) -> str | None:
    """Se a entrada foi uma resposta, e se estava certa.

    É para a tela piscar o acerto quando não há retorno a ler — um degrau
    certo segue direto para o seguinte. Quem decide o que é certo é o
    motor; o cliente não infere isso de tela nenhuma.
    """
    for e in eventos:
        if e.tipo == "degrau_respondido":
            return "certa" if e.dados["certa"] else "errada"
        if e.tipo == "episodio_classificado":
            bem = e.dados["estado"] in (motor.CONFIRMADA, motor.FRAGIL_EP)
            return "certa" if bem else "errada"
    return None


def cria_app(d: Dominio, escadas: Mapping[str, Escada],
             destino: Path) -> FastAPI:
    """A trilha de um tópico, sobre um arquivo de registro."""
    sem = faltando(d, escadas)
    if sem:
        raise ValueError(
            "o tópico %s não tem escada para %s — a trilha só sobe com "
            "todas as premissas cobertas" % (d.id, ", ".join(sem)))
    destino = Path(destino)

    app = FastAPI(title="Structura — trilha de %s" % d.id)
    sessoes: dict[str, trilha.Estado] = {}
    # Às vistas de quem testa: é por aqui que um teste confere que um
    # pedido recusado não moveu o estado.
    app.state.sessoes = sessoes

    def progresso(e: trilha.Estado) -> dict:
        premissas = [{"no": no, "resultado": e.premissa(no).resultado}
                     for no in d.ordem]
        return {"feitas": sum(1 for p in premissas if p["resultado"]),
                "total": len(premissas), "premissas": premissas}

    def corpo(sessao: str, e: trilha.Estado, explicacao=None,
              veredito=None) -> dict:
        return {"sessao": sessao, "tela": e.tela.json(),
                "explicacao": explicacao, "veredito": veredito,
                "progresso": progresso(e),
                # O número da tela. O cliente o devolve em todo pedido.
                "passo": e.n,
                # A escolha da pessoa, que ela pode ter trocado. Quem
                # reabre a página com o código não passou pela tela de
                # entrada, e é por aqui que os ajustes sabem o que marcar.
                "modo": e.modo, "ritmo": e.ritmo}

    def refaz(sessao: str) -> trilha.Estado:
        """A sessão refeita pelo registro, de volta à memória.

        Levanta `RegistroNaoReexecutavel` se o conteúdo mudou desde que
        ela começou; quem chama decide o status (409 ao abrir com código,
        410 com a página aberta ou ao retomar pelo número).
        """
        t = trilha_log.reconstroi(d, escadas, destino, sessao)
        sessoes[sessao] = t.estado
        trilha_log.grava(destino, sessao, [Evento(
            "sessao_reconstruida", {"tela": t.tela.tipo,
                                    "passo": t.estado.n})])
        return t.estado

    def resposta(sessao: str, t: trilha.Transicao, entrada=None) -> dict:
        sessoes[sessao] = t.estado
        # A entrada vai antes dos eventos que ela provocou: é o que
        # permite reexecutar a sessão.
        trilha_log.grava(destino, sessao, t.eventos, entrada)
        return corpo(sessao, t.estado, t.explicacao, _veredito(t.eventos))

    @app.post("/sessoes")
    def abre(body: SessaoBody | None = None) -> dict:
        codigo = (body.codigo if body else "").strip()
        if not codigo:
            sessao = uuid.uuid4().hex[:12]
        elif not CODIGO.match(codigo):
            raise HTTPException(
                status_code=400,
                detail="código fora do formato: letra, depois letras, "
                       "números, hífen ou _, até 16")
        elif codigo in sessoes:
            # A mesma pessoa voltando: a tela em que ela estava. Na trilha
            # o código RETOMA, em vez de recusar (docs/trilha.md, 6.12).
            e = sessoes[codigo]
            trilha_log.grava(destino, codigo, [Evento(
                "sessao_retomada", {"tela": e.tela.tipo})])
            return corpo(codigo, e)
        elif trilha_log.existe(destino, codigo):
            # Está no registro e não na memória: o servidor reiniciou —
            # e ele reinicia toda vez que o sistema é religado. Abrir
            # outra sessão com o mesmo código misturaria duas no mesmo
            # registro; recusar queimava o código para sempre. O motor é
            # puro e o registro guarda as entradas: a sessão é REFEITA.
            try:
                return corpo(codigo, refaz(codigo))
            except trilha_log.RegistroNaoReexecutavel as erro:
                # 409: a sessão existe, e este servidor não consegue
                # continuá-la. A mensagem é para quem está na tela.
                raise HTTPException(status_code=409, detail=str(erro)) from erro
        else:
            sessao = codigo
        # A sessão é a semente: a ordem das alternativas e das peças sai
        # dela, e recarregar a página não reembaralha nada.
        return resposta(sessao, trilha.inicia(d, escadas, semente=sessao))

    @app.post("/sessoes/{sessao}/agir")
    def age(sessao: str, body: AcaoBody):
        estado = sessoes.get(sessao)
        if estado is None and trilha_log.existe(destino, sessao):
            # Está no registro e não na memória: o servidor reiniciou com a
            # página aberta. Vale também para a sessão aberta SEM código,
            # cujo número só a página conhece — foi o que se perdeu em
            # 14/11/2026, quando o Docker caiu no meio de uma sessão. Ela
            # é refeita como a de código, em `abre`.
            try:
                estado = refaz(sessao)
            except trilha_log.RegistroNaoReexecutavel as erro:
                # 410: a sessão existiu e não dá para continuar. A página
                # mostra a frase, que é para quem está na tela.
                raise HTTPException(status_code=410, detail=str(erro)) from erro
        if estado is None:
            raise HTTPException(status_code=404, detail="sessão desconhecida")
        entrada = trilha.Entrada(
            acao=body.acao, escolha=body.escolha, razao=body.razao,
            confianca=body.confianca, pecas=tuple(body.pecas),
            texto=body.texto, modo=body.modo, ritmo=body.ritmo,
            # Tempo absurdo é CORTADO, não recusado. Recusar travava a
            # sessão de quem deixou a página aberta: cada nova tentativa
            # mandava um tempo ainda maior, e o 422 não acabava.
            ms=min(body.ms, LIMITE_MS), passo=body.passo)
        try:
            t = trilha.avanca(d, escadas, estado, entrada)
        except trilha.EntradaVelha:
            # 409, com a tela ATUAL: o pedido é de uma tela que já
            # passou — reenvio depois de uma resposta perdida na rede,
            # outra aba, duplo clique. Nada é gravado, o estado não anda,
            # e o cliente redesenha em vez de adivinhar onde está.
            return JSONResponse(status_code=409, content={
                **corpo(sessao, estado),
                "detail": "esta tela já mudou"})
        except (trilha.EntradaInvalida, RespostaInvalida) as erro:
            # 400, e nada gravado: a tentativa inválida não é dado, e o
            # estado não anda.
            raise HTTPException(status_code=400, detail=str(erro)) from erro
        return resposta(sessao, t, entrada)

    @app.post("/sessoes/{sessao}/retoma")
    def retoma(sessao: str) -> dict:
        """A tela em que a sessão estava, pelo número dela.

        É o que faz voltar sem código (docs/trilha.md, 6.12): o navegador
        guardou o número, a página fechou, e a pessoa reabriu o tópico.
        """
        if not SESSAO.match(sessao):
            raise HTTPException(status_code=404, detail="sessão desconhecida")
        estado = sessoes.get(sessao)
        if estado is not None:
            trilha_log.grava(destino, sessao, [Evento(
                "sessao_retomada", {"tela": estado.tela.tipo})])
            return corpo(sessao, estado)
        if not trilha_log.existe(destino, sessao):
            raise HTTPException(status_code=404, detail="sessão desconhecida")
        try:
            return corpo(sessao, refaz(sessao))
        except trilha_log.RegistroNaoReexecutavel as erro:
            raise HTTPException(status_code=410, detail=str(erro)) from erro

    @app.get("/saude")
    def saude() -> dict:
        return {"ok": True, "topico": d.id, "titulo": d.titulo,
                "premissas": len(d.ordem),
                "degraus": sum(len(e.degraus) for e in escadas.values())}

    @app.get("/")
    def raiz() -> FileResponse:
        return FileResponse(AQUI / "web" / "trilha.html")

    app.mount("/web", StaticFiles(directory=AQUI / "web"), name="web")
    return app
