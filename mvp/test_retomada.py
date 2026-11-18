"""Voltar sem código (docs/trilha.md, 6.12).

Quem abriu a trilha sem código e fechou a página volta à tela em que
estava: o navegador guarda o número da sessão, e a página o manda a
`POST /sessoes/{sessao}/retoma`. Com código, a retomada já existia
(`POST /sessoes` com o código).
"""

from __future__ import annotations

import dataclasses
import pathlib

import pytest
from fastapi.testclient import TestClient

from mvp import trilha_app, trilha_escada, trilha_log
from mvp.dominio import carrega

RAIZ = pathlib.Path(__file__).resolve().parent
D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "dominio" / "escada_kc00.yaml", D)


@pytest.fixture
def destino(tmp_path):
    return tmp_path / "trilha.jsonl"


def _abre_e_anda(cliente):
    j = cliente.post("/sessoes", json={"codigo": ""}).json()
    sessao = j["sessao"]
    j = cliente.post("/sessoes/%s/agir" % sessao,
                     json={"acao": "comecar", "ritmo": "completo",
                           "passo": j["passo"]}).json()
    return sessao, j


def test_retoma_da_memoria_na_mesma_tela(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, j = _abre_e_anda(cliente)
    r = cliente.post("/sessoes/%s/retoma" % sessao)
    assert r.status_code == 200, r.text
    assert r.json()["tela"] == j["tela"] and r.json()["passo"] == j["passo"]
    assert r.json()["sessao"] == sessao
    tipos = [l["tipo"] for l in trilha_log.le(destino, sessao)]
    assert tipos[-1] == "sessao_retomada"


def test_retoma_depois_de_o_servidor_reiniciar(destino):
    antes = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, j = _abre_e_anda(antes)
    depois = TestClient(trilha_app.cria_app(D, ESC, destino))
    r = depois.post("/sessoes/%s/retoma" % sessao)
    assert r.status_code == 200, r.text
    assert r.json()["tela"] == j["tela"] and r.json()["passo"] == j["passo"]
    tipos = [l["tipo"] for l in trilha_log.le(destino, sessao)]
    assert tipos[-1] == "sessao_reconstruida"


def test_sessao_que_nunca_existiu_da_404_e_nao_grava(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    r = cliente.post("/sessoes/abc123def456/retoma")
    assert r.status_code == 404
    assert trilha_log.le(destino) == []


def test_sessao_de_outro_conteudo_da_410_com_a_frase(destino):
    antes = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, _ = _abre_e_anda(antes)
    outra = dict(ESC)
    no = next(iter(outra))
    outra[no] = dataclasses.replace(
        outra[no], revisao=dataclasses.replace(
            outra[no].revisao, frases=outra[no].revisao.frases + ("mudou",)))
    depois = TestClient(trilha_app.cria_app(D, outra, destino))
    r = depois.post("/sessoes/%s/retoma" % sessao)
    assert r.status_code == 410
    assert "mudou" in r.json()["detail"]


def test_numero_fora_do_formato_nem_chega_ao_registro(destino):
    """O número vai para o nome de nada, mas vai para a busca no registro:
    o que não tem a forma de um número de sessão ou de um código é 404."""
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    for ruim in ("a" * 40, "..%2f..", "x y"):
        assert cliente.post("/sessoes/%s/retoma" % ruim).status_code == 404
