"""O MVP no ar: três rotas e a interface.

    python -m mvp.app     →  http://127.0.0.1:8010

A interface não decide nada: ela recebe a próxima tela e desenha. Toda
transição acontece no motor, e o que acontece vira evento no log.

O estado da sessão vive em memória, num dicionário por sessão. É o que um
MVP precisa: a coleta de verdade vai querer reconstrução do log, e o log já
guarda tudo para isso.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from mvp import log, motor
from mvp.dominio import carrega

AQUI = Path(__file__).resolve().parent

app = FastAPI(title="Structura MVP — treino até domínio")
dominio = carrega()
sessoes: dict[str, motor.Estado] = {}


class RespostaBody(BaseModel):
    escolha: int | None = None
    confianca: str = ""
    ms: int = 0
    # "ainda não entendi" num passo da refutação: pede a premissa de novo.
    repetir: bool = False
    # "não sei", em qualquer das três camadas.
    nao_sei: bool = False
    # Texto livre do teach-back. DADO PESSOAL: vai para o log com o código
    # da sessão, nunca com nome.
    texto: str = ""


def _resposta(sessao: str, t: motor.Transicao) -> dict:
    """A transição, pronta para desenhar.

    `veredito` vem daqui, e não do cliente: quem decide se a resposta foi
    certa, e se o retorno deve ser neutro, é o motor. O front não pode
    inferir isso de tipos de evento — seria regra no lugar errado.
    """
    sessoes[sessao] = t.estado
    log.grava(sessao, t.eventos)

    resposta = next((e for e in t.eventos if e.tipo == "resposta_registrada"), None)
    crenca = next((e for e in t.eventos if e.tipo == "crenca_detectada"), None)
    lacuna = next((e for e in t.eventos if e.tipo == "lacuna_registrada"
                   and e.dados.get("declarada")), None)
    falso = next((e for e in t.eventos if e.tipo == "falso_positivo"), None)
    veredito = None
    if crenca is not None:
        veredito = "crenca"        # retorno NEUTRO: a refutação é que ensina
    elif falso is not None:
        # Decisão 13: contar. Calar desperdiça o único momento em que a
        # pessoa percebe que acertou por um caminho que não leva ali.
        veredito = "falso_positivo"
    elif lacuna is not None:
        veredito = "lacuna"        # ela DISSE que não sabe: não é erro
    elif resposta is not None:
        veredito = "certa" if resposta.dados.get("correta") else "errada"

    # O contraste do falso positivo vem montado do domínio, não do cliente:
    # a frase da crença e o enunciado do nó que ela nega.
    retorno = None
    if falso is not None:
        cid = falso.dados.get("crenca")
        alvo = falso.dados.get("fala_do_no")
        if cid in dominio.crencas and alvo in dominio.nos:
            retorno = {
                "crenca": dominio.crencas[cid].afirma,
                "contradiz": dominio.nos[alvo].simples,
                "no": alvo,
                "vezes": falso.dados.get("vezes"),
            }

    return {
        "sessao": sessao,
        "tela": t.tela.json(),
        "veredito": veredito,
        "retorno": retorno,
        # O grafo vai em TODA resposta, não só no fim: ele fica à vista
        # durante a unidade, e o aluno acompanha a cadeia se erguendo.
        "grafo": {"nos": motor.estado_dos_nos(dominio, t.estado),
                  "foco": t.tela.no or t.estado.alvo},
        "eventos": [e.tipo for e in t.eventos],
    }


@app.post("/sessoes")
def cria_sessao() -> dict:
    sessao = uuid.uuid4().hex[:12]
    # A sessão é a semente da ordem das razões: o motor continua puro, e
    # recarregar a página não reembaralha as alternativas debaixo da pessoa.
    return _resposta(sessao, motor.inicia(dominio, semente=sessao))


@app.post("/sessoes/{sessao}/responder")
def responde(sessao: str, body: RespostaBody) -> dict:
    estado = sessoes.get(sessao)
    if estado is None:
        raise HTTPException(status_code=404, detail="sessão desconhecida")
    if body.confianca and body.confianca not in motor.CONFIANCAS:
        raise HTTPException(status_code=400, detail="confiança fora da escala")
    r = motor.Resposta(escolha=body.escolha, confianca=body.confianca, ms=body.ms,
                       repetir=body.repetir, nao_sei=body.nao_sei,
                       texto=body.texto)
    return _resposta(sessao, motor.avanca(dominio, estado, r))


@app.get("/saude")
def saude() -> dict:
    return {
        "ok": True,
        "topico": dominio.id,
        "titulo": dominio.titulo,
        "nos": len(dominio.nos),
        "crencas": len(dominio.crencas),
        "atividades": len(dominio.atividades),
        "streak_alvo": motor.STREAK_ALVO,
        "teto_tentativas": motor.TETO_TENTATIVAS,
    }


@app.get("/")
def raiz() -> FileResponse:
    return FileResponse(AQUI / "web" / "index.html")


app.mount("/web", StaticFiles(directory=AQUI / "web"), name="web")


def main() -> None:
    import uvicorn

    print("Structura MVP — %s (%s)" % (dominio.titulo, dominio.id))
    print("  nós %d · crenças %d · atividades %d"
          % (len(dominio.nos), len(dominio.crencas), len(dominio.atividades)))
    print("  streak para confirmar: %d · teto de tentativas: %d"
          % (motor.STREAK_ALVO, motor.TETO_TENTATIVAS))
    print("  http://127.0.0.1:8010")
    uvicorn.run(app, host="127.0.0.1", port=8010, log_level="warning")


if __name__ == "__main__":
    main()
