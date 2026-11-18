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

OS TREZE SÃO O SISTEMA, e o portal não distingue nenhum. A primeira
versão marcava quatro com a etiqueta "piloto", lida do campo `pilot` dos
`topic_kcXX.yaml`; ela saiu em 12/11/2026, por decisão do Rafael. O campo
continua nos arquivos de tópico, como registro de uma decisão de
pesquisa — o portal é que não o lê.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mvp import caminho, log, trilha_app, trilha_escada
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


def _monta_a_trilha(portal: FastAPI, d, pasta: Path) -> str | None:
    """A trilha daquele tópico, se ele tiver escada para tudo.

    A TRILHA É O SEGUNDO JEITO DE ATRAVESSAR UM TÓPICO (docs/trilha.md):
    premissa por premissa, perguntando primeiro, com a escada passo a
    passo. Ela precisa de conteúdo próprio — `escada_kcNN.yaml` —, e só
    sobe quando TODAS as premissas do tópico têm escada: meia trilha
    deixaria a pessoa sem caminho no meio. Hoje, só o kc_00.

    Aqui ela é uma fábrica (`trilha_app.cria_app`), e não uma cópia de
    módulo: é a refatoração que o cabeçalho deste arquivo pede para o
    `mvp.app`, já feita onde o código nasceu novo.

    O registro dela é outro arquivo, em `<pasta>/trilha/`, e a pasta só
    nasce na primeira gravação — montar a trilha não pode fazer aparecer
    uma pasta vazia ao lado dos registros de quem nunca a abriu.

    Devolve o caminho da trilha, ou `None` quando o tópico não tem uma.
    """
    arquivo = AQUI / "dominio" / ("escada_%s.yaml" % d.id.replace("_", ""))
    if not arquivo.exists():
        return None
    try:
        escadas = trilha_escada.le(arquivo, d)
    except (trilha_escada.EscadaInvalida, ValueError) as erro:
        # UMA ESCADA QUEBRADA NÃO DERRUBA OS TREZE TÓPICOS. O arquivo é
        # conteúdo em edição, e o portal fica ligado sozinho: sem isto,
        # um erro de digitação num YAML tirava o sistema inteiro do ar.
        # O tópico continua pelo fluxo de sempre, e o aviso vai para
        # quem olha a saída do servidor.
        print("AVISO: a escada de %s não carregou, e o tópico ficou sem "
              "trilha — %s" % (d.id, erro), file=sys.stderr)
        return None
    if trilha_escada.faltando(d, escadas):
        return None
    portal.mount("/trilha/%s" % d.id, trilha_app.cria_app(
        d, escadas, pasta / "trilha" / ("%s.jsonl" % d.id)))
    return "/trilha/%s/" % d.id


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
    rotulos, do_fim = caminho.rotulos(), set(caminho.fim())
    # Na ORDEM DO CAMINHO (docs/interface.md, seção 7), que é sugestão:
    # todos os tópicos continuam abertos. O rótulo é o nome curto que a
    # trilha desenhada escreve ao lado da parada; `fim` marca os três em
    # que o caminho se abre.
    for topico in caminho.ordem():
        mod = _app_do_topico(topico, pasta / ("%s.jsonl" % topico))
        portal.mount("/kc/%s" % topico, mod.app)
        d = mod.dominio
        lista.append({
            "id": topico,
            "titulo": d.titulo,
            "rotulo": rotulos[topico],
            "fim": topico in do_fim,
            "nos": len(d.nos),
            "atividades": len(d.atividades),
            "caminho": "/kc/%s/" % topico,
            # `None` em quem não tem. A página abre a trilha quando ela
            # existe, e guarda o caminho de sempre atrás de um link.
            "trilha": _monta_a_trilha(portal, d, pasta),
        })

    @portal.get("/topicos")
    def lista_os_topicos() -> dict:
        return {"topicos": lista, "pasta": str(pasta)}

    @portal.get("/")
    def entrada() -> FileResponse:
        return FileResponse(AQUI / "web" / "portal.html")

    portal.mount("/web", StaticFiles(directory=AQUI / "web"), name="web")
    return portal


def endereco() -> tuple[str, int]:
    """Onde o portal escuta. Sem configuração, só nesta máquina.

    `STRUCTURA_HOST` e `STRUCTURA_PORTA` existem por causa do contêiner:
    dentro dele, 127.0.0.1 é o próprio contêiner, e ninguém de fora
    chega. Lá o portal escuta em 0.0.0.0, e quem decide até onde a porta
    vai é o `docker-compose.yml` — que a publica só em 127.0.0.1 da
    máquina, e há teste guardando isso.

    O padrão não muda: rodando direto com `python -m mvp.portal`, o
    sistema continua invisível para a rede. Ele não tem login.
    """
    host = os.environ.get("STRUCTURA_HOST") or "127.0.0.1"
    bruta = os.environ.get("STRUCTURA_PORTA") or "8010"
    try:
        porta = int(bruta)
    except ValueError:
        raise SystemExit(
            "STRUCTURA_PORTA tem de ser um número, e veio %r" % bruta)
    return host, porta


def main() -> None:
    import uvicorn

    host, porta = endereco()
    app = cria_portal()
    print("Structura — portal dos tópicos")
    print("  %d tópicos · logs em %s" % (len(topicos()), PASTA_PADRAO))
    print("  http://%s:%d" % (host, porta))
    uvicorn.run(app, host=host, port=porta, log_level="warning")


if __name__ == "__main__":
    main()
