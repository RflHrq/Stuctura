"""O portal: os treze tópicos num processo só, um por vez, sem reiniciar.

ATÉ 12/11/2026 o sistema servia UM tópico por processo — `mvp.app` lê
`STRUCTURA_TOPICO` na subida —, e percorrer os tópicos pedia derrubar e
subir o servidor a cada um. Para uma coleta com roteiro isso é um passo
manual; para mostrar o sistema a alguém, é o que impede a pessoa de ver
que ele é um só.

O PORTAL NÃO É UM SEGUNDO APP. Cada tópico continua sendo servido pelo
`mvp.app` de sempre, com as mesmas rotas e o mesmo motor; o portal só os
põe lado a lado, cada um num caminho (`/kc/kc_07/`), cada um com o seu
estado e o SEU arquivo de log. É o mesmo arranjo que o `scripts/
ensaio.sh` já recomenda — um log por tópico —, sem a troca de processo.

O que estes testes guardam é o isolamento: o que se faz num tópico não
pode aparecer em outro, nem na memória nem no log.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp import log, portal
from mvp.dominio import topicos


@pytest.fixture(scope="module")
def pasta(tmp_path_factory):
    return tmp_path_factory.mktemp("portal")


@pytest.fixture(scope="module")
def cliente(pasta):
    return TestClient(portal.cria_portal(pasta))


# --------------------------------------------------------------------------
# A entrada
# --------------------------------------------------------------------------

def test_a_lista_traz_os_treze_topicos_na_ordem(cliente):
    r = cliente.get("/topicos")
    assert r.status_code == 200
    lista = r.json()["topicos"]
    assert [t["id"] for t in lista] == list(topicos())
    um = lista[0]
    assert set(um) >= {"id", "titulo", "nos", "atividades", "piloto",
                       "caminho"}
    assert um["caminho"] == "/kc/%s/" % um["id"]


def test_a_lista_marca_os_quatro_do_piloto(cliente):
    lista = cliente.get("/topicos").json()["topicos"]
    assert [t["id"] for t in lista if t["piloto"]] == [
        "kc_02", "kc_07", "kc_09", "kc_11"]


def test_a_pagina_inicial_leva_a_cada_topico(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    # A página monta a lista pelo /topicos; o que ela precisa trazer é o
    # pedido dessa lista e o lugar onde ela é desenhada.
    assert "/topicos" in r.text
    assert 'id="lista"' in r.text


def test_cada_topico_responde_no_seu_caminho(cliente):
    for t in topicos():
        r = cliente.get("/kc/%s/saude" % t)
        assert r.status_code == 200, t
        assert r.json()["topico"] == t


def test_cada_topico_serve_a_interface_no_seu_caminho(cliente):
    r = cliente.get("/kc/kc_11/")
    assert r.status_code == 200
    assert "/web/app.js" in r.text


def test_os_arquivos_da_interface_saem_da_raiz(cliente):
    """O `index.html` pede `/web/app.js` com caminho absoluto."""
    assert cliente.get("/web/app.js").status_code == 200
    assert cliente.get("/web/style.css").status_code == 200


def test_nada_do_portal_fica_preso_no_cache_do_navegador(cliente):
    """A porta 8010 já serviu outra coisa, e o navegador lembra.

    Visto em 12/11/2026, no primeiro acesso ao portal: a raiz abriu a
    página ANTIGA — o `index.html` do app de um tópico só, guardado pelo
    navegador de quando essa porta era dele — e a tela dizia "não
    consegui falar com o servidor". O servidor estava certo; quem
    respondeu foi o cache.

    `no-cache` não proíbe guardar: obriga a perguntar antes de usar. Com
    o ETag que os arquivos já mandam, a pergunta custa quase nada, e uma
    interface trocada no servidor chega à pessoa na mesma hora — que é o
    que importa numa demonstração e numa coleta.
    """
    for caminho in ("/", "/web/app.js", "/kc/kc_11/", "/topicos"):
        r = cliente.get(caminho)
        assert r.status_code == 200, caminho
        assert r.headers.get("cache-control") == "no-cache", caminho


def test_a_interface_pede_os_arquivos_com_versao(cliente):
    """O que desfaz o cache que JÁ estava guardado.

    `no-cache` vale daqui para a frente; ele não alcança o `app.js` que
    um navegador guardou antes de o cabeçalho existir. Naquele mesmo
    12/11/2026, depois de a raiz abrir certa, o tópico abriu com o
    `app.js` ANTIGO — sem o caminho-base — e a página disse "HTTP 404".
    A versão na referência muda o endereço do arquivo, e endereço novo
    não tem cópia velha em navegador nenhum. Quem mexer na interface de
    um jeito que o navegador não possa misturar com a anterior sobe a
    versão no `index.html`.
    """
    r = cliente.get("/kc/kc_02/")
    for arquivo in ("style.css", "figuras.js", "app.js"):
        assert "/web/%s?v=" % arquivo in r.text, arquivo


def test_topico_que_nao_existe_e_404(cliente):
    assert cliente.get("/kc/kc_99/saude").status_code == 404


# --------------------------------------------------------------------------
# O isolamento
# --------------------------------------------------------------------------

def test_a_sessao_de_um_topico_e_daquele_topico(cliente):
    a = cliente.post("/kc/kc_11/sessoes", json={}).json()
    b = cliente.post("/kc/kc_09/sessoes", json={}).json()
    assert a["sessao"] != b["sessao"]
    # A primeira tela é a do teach-back, e a pergunta é de cada tópico.
    assert a["tela"]["texto"] != b["tela"]["texto"]


def test_o_mesmo_codigo_entra_em_dois_topicos(cliente):
    """É o que faz uma pessoa percorrer os KCs com um código só."""
    um = cliente.post("/kc/kc_02/sessoes", json={"codigo": "P70"})
    dois = cliente.post("/kc/kc_07/sessoes", json={"codigo": "P70"})
    assert um.status_code == 200 and dois.status_code == 200
    assert um.json()["sessao"] == dois.json()["sessao"] == "P70"


def test_o_mesmo_codigo_nao_abre_duas_vezes_o_mesmo_topico(cliente):
    """O guarda de identidade continua de pé dentro de cada tópico."""
    assert cliente.post("/kc/kc_03/sessoes",
                        json={"codigo": "P71"}).status_code == 200
    assert cliente.post("/kc/kc_03/sessoes",
                        json={"codigo": "P71"}).status_code == 409


def test_responder_num_topico_nao_anda_o_outro(cliente):
    cliente.post("/kc/kc_04/sessoes", json={"codigo": "P72"})
    antes = cliente.post("/kc/kc_05/sessoes", json={"codigo": "P72"}).json()

    r = cliente.post("/kc/kc_04/sessoes/P72/responder",
                     json={"nao_sei": True, "ms": 10})
    assert r.status_code == 200

    # No kc_05 a mesma pessoa continua na primeira tela: responder a
    # primeira coisa lá leva à MESMA segunda tela que levaria sem o kc_04.
    depois = cliente.post("/kc/kc_05/sessoes/P72/responder",
                          json={"nao_sei": True, "ms": 10}).json()
    assert antes["tela"]["tipo"] != "ensino"
    assert depois["tela"]["tipo"] == "ensino"
    assert depois["tela"]["no"] in ("B1", "B2", "B3")


def test_cada_topico_grava_no_seu_arquivo(cliente, pasta):
    cliente.post("/kc/kc_06/sessoes", json={"codigo": "P73"})
    arquivo = pasta / "kc_06.jsonl"
    assert arquivo.exists()
    linhas = [json.loads(x) for x in
              arquivo.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert {x["sessao"] for x in linhas} >= {"P73"}
    abertura = next(x for x in linhas if x["tipo"] == "unidade_iniciada"
                    and x["sessao"] == "P73")
    assert abertura["topico"] == "kc_06"
    # e o P73 não aparece no arquivo de nenhum outro tópico
    for outro in pasta.glob("*.jsonl"):
        if outro.name == "kc_06.jsonl":
            continue
        assert "P73" not in outro.read_text(encoding="utf-8"), outro.name


def test_o_portal_nao_escreve_no_log_padrao(cliente):
    """O log padrão é o da coleta de um tópico só. O portal tem o dele."""
    antes = log.DESTINO.read_text(encoding="utf-8") if log.DESTINO.exists() else ""
    cliente.post("/kc/kc_08/sessoes", json={"codigo": "P74"})
    depois = log.DESTINO.read_text(encoding="utf-8") if log.DESTINO.exists() else ""
    assert antes == depois


def test_a_sessao_volta_do_log_depois_de_uma_queda(pasta):
    """A retomada do `mvp.app` continua valendo dentro do portal.

    Dois portais sobre a mesma pasta são o servidor antes e depois de
    cair: o segundo não tem nada na memória, e a resposta seguinte tem
    de encontrar a sessão no arquivo do tópico.
    """
    um = TestClient(portal.cria_portal(pasta))
    um.post("/kc/kc_10/sessoes", json={"codigo": "P75"})
    dois = TestClient(portal.cria_portal(pasta))
    r = dois.post("/kc/kc_10/sessoes/P75/responder",
                  json={"nao_sei": True, "ms": 10})
    assert r.status_code == 200
    assert "sessao_retomada" in (pasta / "kc_10.jsonl").read_text(
        encoding="utf-8")
