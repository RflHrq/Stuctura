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


def test_so_o_kc_00_tem_trilha(cliente):
    lista = cliente.get("/topicos").json()["topicos"]
    assert {t["id"]: t["trilha"] for t in lista} == {
        t: ("/trilha/kc_00/" if t == "kc_00" else None) for t in topicos()}


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


def test_topico_sem_escada_nao_tem_trilha(cliente):
    assert cliente.get("/trilha/kc_02/saude").status_code == 404
    assert cliente.post("/trilha/kc_02/sessoes", json={}).status_code in (404, 405)


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


def test_a_pagina_inicial_abre_a_trilha_e_guarda_a_versao_anterior():
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    assert "t.trilha" in html
    assert "versão anterior" in html
    # O link de sempre continua sendo montado, para quem não tem trilha.
    assert "t.caminho" in html


def test_a_pagina_inicial_nao_ganha_etiqueta_nenhuma():
    """A trilha do kc_00 não é anunciada com selo: o que distingue o
    tópico na página é só o link discreto para a versão anterior."""
    html = (WEB / "portal.html").read_text(encoding="utf-8").lower()
    for palavra in ("piloto", "pilot", "beta", "novo formato"):
        assert palavra not in html, palavra
