"""As seis rotas do §9. Tradução HTTP ⇄ motor, sem regra de negócio.

`next_action` é o coração do contrato: o servidor devolve o que apresentar
em seguida e o navegador apenas renderiza. Nenhuma regra de fluxo no
cliente — é o que mantém o determinismo verificável e impede que o braço
de controle divirja do socrático por acidente de implementação no front.
"""

from __future__ import annotations

import csv
import io
import json
import os
import secrets
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api import service
from store import events as store_events

router = APIRouter()


# --------------------------------------------------------------------------
# Corpos de requisição
# --------------------------------------------------------------------------

class NewSession(BaseModel):
    participant: str = Field(min_length=1, max_length=32)
    arm: str
    kc_sequence: list[str] | None = None


class AnswerBody(BaseModel):
    ciu_id: str
    confidence: str
    elapsed_ms: int = Field(ge=0)
    option_idx: int | None = None
    text: Any = None


class StepBody(BaseModel):
    accepted: bool
    elapsed_ms: int = Field(ge=0)
    kc: str | None = None
    node: str | None = None


class AckBody(BaseModel):
    elapsed_ms: int = Field(default=0, ge=0)


class TelemetryBody(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------
# Dependências
# --------------------------------------------------------------------------

def ctx(request: Request):
    """Domínio do app; conexão nova por requisição, fechada ao fim.

    Uma conexão por requisição é o que torna o serviço seguro sob o
    threadpool do FastAPI sem introduzir lock. O custo é desprezível
    para SQLite local, e o RNF03 (≤200 ms) continua folgado.
    """
    conn = store_events.connect(request.app.state.db_path)
    try:
        yield request.app.state.domain, conn
    finally:
        conn.close()


def _erro(exc: Exception) -> HTTPException:
    if isinstance(exc, service.SessionNotFound):
        return HTTPException(404, "sessão não encontrada")
    if isinstance(exc, service.OutOfSync):
        return HTTPException(409, str(exc))
    return HTTPException(400, str(exc))


# --------------------------------------------------------------------------
# §9 — as seis rotas
# --------------------------------------------------------------------------

@router.post("/sessions")
def criar_sessao(body: NewSession, dep=Depends(ctx)):
    domain, conn = dep
    try:
        vista = service.create_session(
            conn, domain, body.participant, body.arm, body.kc_sequence
        )
    except Exception as exc:
        raise _erro(exc) from exc
    return vista.as_json(domain)


@router.get("/sessions/{session_id}")
def ler_sessao(session_id: str, dep=Depends(ctx)):
    """Retomada (RNF06): reconstrói tudo do log e devolve onde parou."""
    domain, conn = dep
    try:
        return service.load_session(conn, domain, session_id).as_json(domain)
    except Exception as exc:
        raise _erro(exc) from exc


@router.post("/sessions/{session_id}/answer")
def responder(session_id: str, body: AnswerBody, dep=Depends(ctx)):
    domain, conn = dep
    try:
        vista = service.submit_answer(
            conn, domain, session_id, body.ciu_id, body.confidence,
            body.elapsed_ms, body.option_idx, body.text,
        )
    except Exception as exc:
        raise _erro(exc) from exc

    saida = vista.as_json(domain)
    resposta = vista.emitted_of("answer_submitted") or {}
    saida["outcome"] = "correct" if resposta.get("correct") else "incorrect"

    # `detected` significa CRENÇA ATIVA, não distrator escolhido. Um
    # distrator marcado no chute vai para o log — é dado cru da Q-matrix —
    # mas não é crença detectada, e reportá-lo como tal faria a interface
    # anunciar ao aluno uma convicção que ele não declarou ter.
    ativa = vista.emitted_of("misconception_detected")
    saida["detected"] = ativa["misconception_id"] if ativa else None
    saida["chosen_distractor"] = resposta.get("misconception_id")
    return saida


@router.post("/sessions/{session_id}/step")
def passo(session_id: str, body: StepBody, dep=Depends(ctx)):
    """Um passo socrático (braço A) ou uma confirmação de leitura (braço B)."""
    domain, conn = dep
    try:
        vista = service.submit_step(
            conn, domain, session_id, body.accepted, body.elapsed_ms, body.kc, body.node
        )
    except Exception as exc:
        raise _erro(exc) from exc
    return vista.as_json(domain)


@router.post("/sessions/{session_id}/ack")
def confirmar(session_id: str, body: AckBody, dep=Depends(ctx)):
    """Fecha o confronto visual ou a conclusão nomeada."""
    domain, conn = dep
    try:
        return service.acknowledge(conn, domain, session_id, body.elapsed_ms).as_json(domain)
    except Exception as exc:
        raise _erro(exc) from exc


@router.post("/sessions/{session_id}/telemetry")
def telemetria(session_id: str, body: TelemetryBody, dep=Depends(ctx)):
    """Eventos sem decisão de fluxo, como `diagram_toggled` (§5.2).

    É o dado que transforma o apelo visual em evidência: quantas vezes o
    aluno alternou entre os estados antes de responder.
    """
    _, conn = dep
    try:
        service.record_telemetry(conn, session_id, body.type, body.payload)
    except Exception as exc:
        raise _erro(exc) from exc
    return {"ok": True}


# --------------------------------------------------------------------------
# Exportação
# --------------------------------------------------------------------------

def _confere_token(request: Request, token: str | None, header: str | None) -> None:
    esperado = request.app.state.export_token
    fornecido = token or header
    if not fornecido or not secrets.compare_digest(str(fornecido), str(esperado)):
        raise HTTPException(401, "token de exportação inválido")


@router.get("/export/events.csv")
def exportar_eventos(
    request: Request,
    token: str | None = Query(default=None),
    x_export_token: str | None = Header(default=None),
    dep=Depends(ctx),
):
    """O log inteiro em CSV. Protegido por token local (§9).

    O `payload` sai como JSON numa coluna só: achatá-lo aqui perderia
    estrutura, e as três tabelas de análise do §12 são item separado.
    """
    _confere_token(request, token, x_export_token)
    _, conn = dep

    buffer = io.StringIO()
    w = csv.writer(buffer)
    w.writerow(["session_id", "participant", "arm", "seq", "ts", "type", "payload"])

    sessoes = {
        r["id"]: (r["participant"], r["arm"])
        for r in conn.execute("SELECT id, participant, arm FROM sessions")
    }
    for e in store_events.read_all(conn):
        participante, braco = sessoes.get(e.session_id, ("", ""))
        w.writerow([e.session_id, participante, braco, e.seq, e.ts, e.type,
                    json.dumps(e.payload, ensure_ascii=False, sort_keys=True)])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="events.csv"'},
    )


# --------------------------------------------------------------------------
# Diagnóstico do próprio serviço
# --------------------------------------------------------------------------

@router.get("/health")
def health(dep=Depends(ctx)):
    """O hash do domínio aparece aqui para conferência antes de cada sessão.

    É a resposta operacional ao risco do §15: se este hash mudar no meio
    da coleta, os participantes não viram o mesmo conteúdo.
    """
    domain, conn = dep
    total = conn.execute("SELECT COUNT(*) AS n FROM sessions").fetchone()["n"]
    return {
        "ok": True,
        "domain": domain.id,
        "domain_hash": domain.hash,
        "kcs": len(domain.kcs),
        "cius": len(domain.cius),
        "pilot_sequence": list(domain.pilot_sequence),
        "sessions": total,
    }


def gerar_token() -> str:
    """Token de exportação: do ambiente, ou gerado e guardado em disco.

    Fica em `data/`, junto do banco, para que reiniciar o servidor no meio
    da coleta não invalide o token que o pesquisador já anotou.
    """
    do_ambiente = os.environ.get("STRUCTURA_EXPORT_TOKEN")
    if do_ambiente:
        return do_ambiente
    caminho = store_events.DEFAULT_DB.parent / "export_token.txt"
    if caminho.exists():
        return caminho.read_text(encoding="utf-8").strip()
    novo = secrets.token_urlsafe(24)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(novo + "\n", encoding="utf-8")
    return novo
