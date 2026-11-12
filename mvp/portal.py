"""O portal: os treze tópicos num processo só, um por vez.

    python -m mvp.portal     →  http://127.0.0.1:8010

A página inicial lista os tópicos; cada um abre no seu caminho
(`/kc/kc_07/`), com a interface de sempre. Entra-se num, volta-se,
entra-se no próximo — sem derrubar o servidor entre um e outro.

O PORTAL NÃO REESCREVE O APP. Cada tópico é servido pelo `mvp.app` de
verdade, com as mesmas rotas, o mesmo motor e as mesmas travas. O que o
portal faz é montar treze instâncias dele lado a lado.

POR QUE CÓPIAS DO MÓDULO, E NÃO UMA FÁBRICA. O `mvp.app` guarda o
domínio e o estado das sessões em variáveis do módulo, e as rotas as
leem na hora da chamada. O caminho limpo seria transformá-lo numa fábrica
`cria_app(dominio, log)`; o caminho seguro, com a suíte que o cerca e uma
entrega no mesmo dia, é carregar o MESMO arquivo uma vez por tópico e
trocar, em cada cópia, as duas coisas que o distinguem — o domínio e o
arquivo de log. Nada no `app.py` muda, e tudo o que os testes dele
garantem continua garantido para cada tópico. A fábrica fica como
refatoração a fazer com calma, e este docstring é o lembrete.

UM ARQUIVO DE LOG POR TÓPICO, na pasta do portal. É o arranjo que o
`scripts/ensaio.sh` já recomenda, e ele resolve de graça o que um log
único complicaria: o mesmo código de participante entra em cada tópico
uma vez, e a retomada de uma sessão procura no arquivo certo.

A pasta padrão é `ensaios/portal/`, fora do git e longe do log de coleta
de um tópico só. `STRUCTURA_PASTA` troca.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mvp import log
from mvp.dominio import carrega, topicos

AQUI = Path(__file__).resolve().parent
PASTA_PADRAO = Path(os.environ.get("STRUCTURA_PASTA")
                    or AQUI.parent / "ensaios" / "portal")


class _LogDoTopico:
    """O que o `app.py` pede ao log, preso ao arquivo de um tópico.

    São quatro nomes — `grava`, `aberturas`, `reconstroi` e a exceção
    `LogIncompleto` —, e todos já aceitavam um destino. Esta classe só o
    fixa. Se o `app.py` passar a pedir um quinto nome ao log, a cópia do
    tópico falha com `AttributeError` na primeira chamada, que é falha
    alta e imediata, e não gravação no arquivo errado.
    """

    LogIncompleto = log.LogIncompleto

    def __init__(self, destino: Path) -> None:
        self.destino = Path(destino)

    def grava(self, sessao, eventos, entrada=None) -> None:
        log.grava(sessao, eventos, destino=self.destino, entrada=entrada)

    def aberturas(self):
        return log.aberturas(self.destino)

    def reconstroi(self, d, sessao):
        return log.reconstroi(d, sessao, self.destino)


def _app_do_topico(topico: str, destino: Path):
    """Uma instância do `mvp.app` para aquele tópico e aquele arquivo."""
    spec = importlib.util.spec_from_file_location(
        "mvp._app_%s" % topico, AQUI / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.dominio = carrega(topico=topico)
    mod.log = _LogDoTopico(destino)
    return mod


def _e_do_piloto(topico: str) -> bool:
    arquivo = AQUI / "dominio" / ("topic_%s.yaml" % topico.replace("_", ""))
    try:
        cru = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return False
    return bool(cru.get("pilot"))


def cria_portal(pasta: Path | None = None) -> FastAPI:
    """O portal sobre uma pasta de logs. Um arquivo por tópico, lá dentro."""
    pasta = Path(pasta) if pasta else PASTA_PADRAO
    pasta.mkdir(parents=True, exist_ok=True)

    portal = FastAPI(title="Structura — os tópicos")

    @portal.middleware("http")
    async def sem_cache_velho(request, chama):
        # A porta 8010 já serviu o app de um tópico só, e o navegador
        # guarda a página daquela época: sem isto, a raiz do portal abria
        # o `index.html` antigo. `no-cache` obriga o navegador a
        # perguntar antes de usar o que tem; o ETag torna a pergunta
        # barata. Vale para os tópicos montados também — o middleware
        # envolve o portal inteiro.
        resposta = await chama(request)
        resposta.headers["Cache-Control"] = "no-cache"
        return resposta

    lista = []
    for topico in topicos():
        mod = _app_do_topico(topico, pasta / ("%s.jsonl" % topico))
        portal.mount("/kc/%s" % topico, mod.app)
        d = mod.dominio
        lista.append({
            "id": topico,
            "titulo": d.titulo,
            "nos": len(d.nos),
            "atividades": len(d.atividades),
            "piloto": _e_do_piloto(topico),
            "caminho": "/kc/%s/" % topico,
        })

    @portal.get("/topicos")
    def lista_os_topicos() -> dict:
        return {"topicos": lista, "pasta": str(pasta)}

    @portal.get("/")
    def entrada() -> FileResponse:
        return FileResponse(AQUI / "web" / "portal.html")

    portal.mount("/web", StaticFiles(directory=AQUI / "web"), name="web")
    return portal


def main() -> None:
    import uvicorn

    app = cria_portal()
    print("Structura — portal dos tópicos")
    print("  %d tópicos · logs em %s" % (len(topicos()), PASTA_PADRAO))
    print("  http://127.0.0.1:8010")
    uvicorn.run(app, host="127.0.0.1", port=8010, log_level="warning")


if __name__ == "__main__":
    main()
