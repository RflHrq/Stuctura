"""As rotas da trilha.

    app = cria_app(dominio, escadas, destino)

Uma FÁBRICA, e não um módulo com variáveis: o estado das sessões mora
dentro de `cria_app`. O `mvp/app.py` guarda o domínio e as sessões em
variáveis do módulo, e por isso o portal precisa carregar o mesmo
arquivo treze vezes; aqui dois tópicos são duas chamadas.

A interface não decide nada. Ela manda o que a pessoa fez e desenha a
tela que volta; toda transição acontece em `mvp/trilha.py`, e o que
acontece vira linha em `mvp/trilha_log.py`.

    POST /sessoes                  abre (ou devolve a que está aberta)
    POST /sessoes/{sessao}/agir    uma entrada, uma transição
    GET  /saude
    GET  /                         a página
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Mapping

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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

# Um episódio leva minutos, não horas.
LIMITE_MS = 2 * 60 * 60 * 1000
# O que se digita num degrau é um valor curto. O teto existe porque isto
# é escrito em disco: sem ele uma colagem acidental vira meio megabyte.
LIMITE_DO_TEXTO = 200
LIMITE_DE_PECAS = 40


class SessaoBody(BaseModel):
    codigo: str = ""


class AcaoBody(BaseModel):
    acao: str = "responder"
    escolha: int | None = None
    razao: int | None = None
    confianca: str = ""
    pecas: list[int] = Field(default_factory=list, max_length=LIMITE_DE_PECAS)
    texto: str = Field(default="", max_length=LIMITE_DO_TEXTO)
    modo: str = ""
    ritmo: str = ""
    ms: int = Field(default=0, ge=0, le=LIMITE_MS)


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

    def resposta(sessao: str, t: trilha.Transicao, entrada=None) -> dict:
        sessoes[sessao] = t.estado
        # A entrada vai antes dos eventos que ela provocou: é o que
        # permite reexecutar a sessão.
        trilha_log.grava(destino, sessao, t.eventos, entrada)
        return {"sessao": sessao, "tela": t.tela.json(),
                "explicacao": t.explicacao, "veredito": _veredito(t.eventos),
                "progresso": progresso(t.estado)}

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
            return {"sessao": codigo, "tela": e.tela.json(),
                    "explicacao": None, "veredito": None,
                    "progresso": progresso(e)}
        elif trilha_log.le(destino, codigo):
            # Está no registro e não na memória: o servidor reiniciou.
            # Abrir outra sessão com o mesmo código misturaria duas no
            # mesmo registro; refazer a antiga pelo registro é a fatia 3.
            raise HTTPException(
                status_code=409,
                detail="a sessão %r existe no registro e não está mais na "
                       "memória deste servidor. A retomada depois de um "
                       "reinício ainda não foi construída; use outro código."
                       % codigo)
        else:
            sessao = codigo
        # A sessão é a semente: a ordem das alternativas e das peças sai
        # dela, e recarregar a página não reembaralha nada.
        return resposta(sessao, trilha.inicia(d, escadas, semente=sessao))

    @app.post("/sessoes/{sessao}/agir")
    def age(sessao: str, body: AcaoBody) -> dict:
        estado = sessoes.get(sessao)
        if estado is None:
            raise HTTPException(status_code=404, detail="sessão desconhecida")
        entrada = trilha.Entrada(
            acao=body.acao, escolha=body.escolha, razao=body.razao,
            confianca=body.confianca, pecas=tuple(body.pecas),
            texto=body.texto, modo=body.modo, ritmo=body.ritmo, ms=body.ms)
        try:
            t = trilha.avanca(d, escadas, estado, entrada)
        except (trilha.EntradaInvalida, RespostaInvalida) as erro:
            # 400, e nada gravado: a tentativa inválida não é dado, e o
            # estado não anda. É o que segura o duplo clique.
            raise HTTPException(status_code=400, detail=str(erro)) from erro
        return resposta(sessao, t, entrada)

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
