"""O portal abre a trilha.

A trilha de um tópico é montada pelo portal em `/trilha/<tópico>/`,
quando o tópico tem escada escrita para todas as premissas — hoje, só o
kc_00. A página inicial passa a abrir a trilha desse tópico, e o fluxo
de sempre continua no lugar, atrás de um link discreto (docs/trilha.md,
6.13 e decisão 8).

O que estes testes guardam:

  - só o tópico com escada completa ganha trilha, e os outros doze
    ficam exatamente como estavam;
  - o fluxo atual do kc_00 não some;
  - o registro da trilha é outro arquivo, em outra pasta, e essa pasta
    só nasce quando alguém abre a trilha.

`mvp/test_portal.py` não foi tocado, e continua valendo inteiro.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))

from mvp import portal, trilha_log  # noqa: E402
from mvp.dominio import topicos  # noqa: E402

WEB = RAIZ / "web"


@pytest.fixture(scope="module")
def pasta(tmp_path_factory):
    return tmp_path_factory.mktemp("portal_trilha")


@pytest.fixture(scope="module")
def cliente(pasta):
    return TestClient(portal.cria_portal(pasta))


# Os tópicos que têm escada escrita. Este teste nasceu como "só o kc_00
# tem trilha", que era verdade na primeira fatia; desde 13/11/2026 o
# kc_02 também tem, e a lista vai crescer um tópico de cada vez. O que se
# confere continua o mesmo: tem trilha quem tem escada, e só quem tem.
COM_ESCADA = {t for t in topicos()
              if (RAIZ / "dominio" / ("escada_%s.yaml" % t.replace("_", ""))
                  ).exists()}


def test_so_tem_trilha_o_topico_que_tem_escada(cliente):
    assert "kc_00" in COM_ESCADA
    lista = cliente.get("/topicos").json()["topicos"]
    assert {t["id"]: t["trilha"] for t in lista} == {
        t: ("/trilha/%s/" % t if t in COM_ESCADA else None) for t in topicos()}


def test_o_caminho_de_sempre_nao_muda(cliente):
    for t in cliente.get("/topicos").json()["topicos"]:
        assert t["caminho"] == "/kc/%s/" % t["id"]


def test_a_trilha_responde_no_caminho_dela(cliente):
    saude = cliente.get("/trilha/kc_00/saude").json()
    assert (saude["topico"], saude["premissas"]) == ("kc_00", 5)
    j = cliente.post("/trilha/kc_00/sessoes", json={}).json()
    assert j["tela"]["tipo"] == "entrada"
    r = cliente.post("/trilha/kc_00/sessoes/%s/agir" % j["sessao"],
                     json={"acao": "comecar", "modo": "explique",
                           "passo": j["passo"]})
    assert r.status_code == 200 and r.json()["tela"]["tipo"] == "degrau"


def test_a_trilha_serve_a_pagina_e_os_assets(cliente):
    r = cliente.get("/trilha/kc_00/")
    assert r.status_code == 200 and "/web/trilha.js?v=" in r.text
    assert cliente.get("/web/trilha.js").status_code == 200
    assert cliente.get("/web/trilha.css").status_code == 200


def test_topico_sem_escada_nao_tem_trilha(monkeypatch, tmp_path):
    """ERA: escolhia um tópico de verdade ainda sem escada
    (`SEM_ESCADA = next(t for t in topicos() if t not in COM_ESCADA)`).
    Desde 18/11/2026 os treze têm escada, e aquele `next` quebrava este
    arquivo inteiro já na importação. Agora o teste esconde do portal a
    escada de um tópico — o arquivo existe, mas o portal não o vê — e
    confere o mesmo de antes: sem escada não há trilha, e o tópico
    continua pelo caminho de sempre."""
    escondida = portal.AQUI / "dominio" / "escada_kc12.yaml"
    existe = Path.exists
    monkeypatch.setattr(
        Path, "exists", lambda self: False if self == escondida else existe(self))
    cliente = TestClient(portal.cria_portal(tmp_path))
    assert cliente.get("/trilha/kc_12/saude").status_code == 404
    assert cliente.post("/trilha/kc_12/sessoes",
                        json={}).status_code in (404, 405)
    trilhas = {t["id"]: t["trilha"]
               for t in cliente.get("/topicos").json()["topicos"]}
    assert trilhas["kc_12"] is None and trilhas["kc_11"] == "/trilha/kc_11/"
    assert cliente.get("/kc/kc_12/saude").json()["topico"] == "kc_12"


def test_o_fluxo_atual_do_kc_00_continua_no_lugar(cliente):
    assert cliente.get("/kc/kc_00/saude").json()["topico"] == "kc_00"
    assert cliente.get("/kc/kc_00/").status_code == 200
    j = cliente.post("/kc/kc_00/sessoes", json={}).json()
    assert j["tela"]["tipo"] == "frase"


def test_o_registro_da_trilha_fica_separado(tmp_path):
    so_este = TestClient(portal.cria_portal(tmp_path))
    j = so_este.post("/trilha/kc_00/sessoes", json={}).json()
    arquivo = tmp_path / "trilha" / "kc_00.jsonl"
    assert arquivo.exists()
    assert not (tmp_path / "kc_00.jsonl").exists()
    assert {l["sessao"] for l in trilha_log.le(arquivo)} == {j["sessao"]}

    so_este.post("/kc/kc_00/sessoes", json={})
    assert (tmp_path / "kc_00.jsonl").exists()
    assert "trilha_iniciada" not in (tmp_path / "kc_00.jsonl").read_text("utf-8")
    assert "unidade_iniciada" not in arquivo.read_text("utf-8")


def test_criar_o_portal_nao_cria_a_pasta_da_trilha(tmp_path):
    portal.cria_portal(tmp_path)
    assert not (tmp_path / "trilha").exists()
    assert list(tmp_path.iterdir()) == []


def test_a_trilha_tambem_responde_sem_cache(cliente):
    for rota in ("/trilha/kc_00/", "/trilha/kc_00/saude"):
        r = cliente.get(rota)
        assert r.status_code == 200, rota
        assert r.headers["Cache-Control"] == "no-cache", rota


def test_a_pagina_inicial_abre_a_trilha_sem_a_versao_anterior():
    """ERA ..._e_guarda_a_versao_anterior: um link discreto para o fluxo
    de sempre ficava sob cada tópico. Em 18/11/2026 o Rafael pediu que ele
    saísse — os treze tópicos abrem pela trilha. As rotas /kc/<tópico>/
    continuam montadas (o painel do pesquisador e a exportação leem o
    registro delas), só sem link na página."""
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    assert "t.trilha" in html
    assert "versão anterior" not in html
    # O caminho de sempre ainda é o destino de quem não tem trilha.
    assert "t.caminho" in html


def test_a_pagina_inicial_nao_ganha_etiqueta_nenhuma():
    """A trilha do kc_00 não é anunciada com selo: o que distingue o
    tópico na página é só o link discreto para a versão anterior."""
    html = (WEB / "portal.html").read_text(encoding="utf-8").lower()
    for palavra in ("piloto", "pilot", "beta", "novo formato"):
        assert palavra not in html, palavra
