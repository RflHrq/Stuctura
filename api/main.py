"""Aplicação FastAPI. Sobe o domínio, abre o banco e monta a interface.

    python -m api.main            # sobe em 127.0.0.1:8000
    uvicorn api.main:app          # equivalente

FALHA NA CARGA, NÃO EM SESSÃO (§1). O domínio é validado no arranque: se
um YAML estiver inconsistente, o processo não sobe. Nunca descobrir isso
com um aluno na frente.

OFFLINE (RNF05). Nenhuma dependência de rede em tempo de sessão: o
servidor é local, o banco é um arquivo, e `web/` não busca nada de CDN.
Vale rodar o ensaio com a interface de rede desligada para conferir.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from api import routes  # noqa: E402
from engine.loader import DomainError, load  # noqa: E402
from store import events as store_events  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        domain = load()
    except DomainError as exc:
        print("DOMÍNIO INVÁLIDO — o servidor não sobe.\n", file=sys.stderr)
        for p in exc.problemas:
            print("  ERRO  %s" % p, file=sys.stderr)
        raise SystemExit(1) from exc

    # A escala de confiança é declarada em study.yaml; o log só a valida.
    # Injetar aqui mantém a direção de dependência (store não conhece engine).
    store_events.set_confidence_scale(domain.study.confidence_scale)

    app.state.domain = domain
    # O esquema é criado uma vez; cada requisição abre a sua conexão.
    # SQLite prende uma conexão à thread que a criou, e o FastAPI roda
    # endpoints síncronos num threadpool — uma conexão compartilhada
    # quebraria na segunda requisição. WAL e BEGIN IMMEDIATE já dão conta
    # da concorrência, então não há estado a proteger com lock.
    store_events.open_db().close()
    app.state.db_path = store_events.DEFAULT_DB
    app.state.export_token = routes.gerar_token()

    print("Structura no ar.")
    print("  domínio     %s  (%d KCs, %d CIUs)"
          % (domain.id, len(domain.kcs), len(domain.cius)))
    print("  hash        %s" % domain.hash)
    print("  piloto      %s" % ", ".join(domain.pilot_sequence))
    print("  banco       %s" % store_events.DEFAULT_DB)
    print("  export      /export/events.csv?token=%s" % app.state.export_token)
    yield


app = FastAPI(
    title="Structura",
    description="Diagnóstico e correção de misconceptions em ponteiros na linguagem C.",
    lifespan=lifespan,
)
app.include_router(router=routes.router)

if WEB.exists():
    app.mount("/", StaticFiles(directory=str(WEB), html=True), name="web")


def main() -> int:
    import uvicorn
    # 127.0.0.1 de propósito: o laboratório não precisa expor a coleta na rede.
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
