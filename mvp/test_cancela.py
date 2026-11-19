"""Sair da sessão: guardar para depois, ou cancelar e começar do zero.

O Rafael, em 19/11/2026: no meio da sessão, poder encerrar e sair, com a
escolha de guardar o que fez ou de cancelar. Guardar já existia (cada
resposta vai para o registro, e o navegador lembra a sessão). Cancelar é
`POST /sessoes/{sessao}/cancela`.

CANCELAR NÃO APAGA NADA. O registro é só de acréscimo: a sessão
cancelada continua lá, com uma linha a mais dizendo que foi cancelada, e
deixa de poder ser retomada — nem da memória, nem refeita pelo registro
depois de o servidor reiniciar.
"""

from __future__ import annotations

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


def _abre_e_anda(cliente, codigo=""):
    j = cliente.post("/sessoes", json={"codigo": codigo}).json()
    sessao = j["sessao"]
    j = cliente.post("/sessoes/%s/agir" % sessao,
                     json={"acao": "comecar", "ritmo": "completo",
                           "passo": j["passo"]}).json()
    return sessao, j


def test_cancelar_marca_a_sessao_e_nao_apaga_linha_nenhuma(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, _ = _abre_e_anda(cliente)
    antes = trilha_log.le(destino, sessao)
    r = cliente.post("/sessoes/%s/cancela" % sessao)
    assert r.status_code == 200, r.text
    depois = trilha_log.le(destino, sessao)
    assert depois[:len(antes)] == antes
    assert [l["tipo"] for l in depois[len(antes):]] == ["sessao_cancelada"]


def test_a_sessao_cancelada_nao_anda_nem_volta(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, j = _abre_e_anda(cliente)
    cliente.post("/sessoes/%s/cancela" % sessao)
    r = cliente.post("/sessoes/%s/agir" % sessao,
                     json={"acao": "nao_sei", "passo": j["passo"]})
    assert r.status_code == 410 and "cancelada" in r.json()["detail"]
    r = cliente.post("/sessoes/%s/retoma" % sessao)
    assert r.status_code == 410 and "cancelada" in r.json()["detail"]


def test_nem_depois_de_o_servidor_reiniciar(destino):
    antes = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, _ = _abre_e_anda(antes)
    antes.post("/sessoes/%s/cancela" % sessao)
    depois = TestClient(trilha_app.cria_app(D, ESC, destino))
    r = depois.post("/sessoes/%s/retoma" % sessao)
    assert r.status_code == 410 and "cancelada" in r.json()["detail"]


def test_o_codigo_da_sessao_cancelada_nao_reabre_a_mesma_sessao(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, _ = _abre_e_anda(cliente, codigo="R01")
    cliente.post("/sessoes/%s/cancela" % sessao)
    r = cliente.post("/sessoes", json={"codigo": "R01"})
    assert r.status_code == 409 and "cancelada" in r.json()["detail"]
    # e um servidor novo, que só tem o registro, diz o mesmo
    r = TestClient(trilha_app.cria_app(D, ESC, destino)).post(
        "/sessoes", json={"codigo": "R01"})
    assert r.status_code == 409 and "cancelada" in r.json()["detail"]


def test_cancelar_sessao_desconhecida_e_404(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    assert cliente.post("/sessoes/abc123abc123/cancela").status_code == 404
    assert cliente.post("/sessoes/..%2F..%2Fx/cancela").status_code == 404


def test_cancelar_duas_vezes_nao_grava_duas_linhas(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, _ = _abre_e_anda(cliente)
    cliente.post("/sessoes/%s/cancela" % sessao)
    r = cliente.post("/sessoes/%s/cancela" % sessao)
    assert r.status_code == 410
    tipos = [l["tipo"] for l in trilha_log.le(destino, sessao)]
    assert tipos.count("sessao_cancelada") == 1


def test_a_rota_nova_esta_na_lista_do_cabecalho():
    assert "/cancela" in trilha_app.__doc__


# --------------------------------------------------------------------------
# A página (mvp/web/trilha.html e trilha.js). O comportamento na tela é
# conferido no navegador; aqui, que o caminho existe.
# --------------------------------------------------------------------------

import re  # noqa: E402

WEB = RAIZ / "web"


def _js():
    return (WEB / "trilha.js").read_text(encoding="utf-8")


def _html():
    return (WEB / "trilha.html").read_text(encoding="utf-8")


def test_o_topo_tem_o_botao_de_sair_e_a_escolha():
    html = _html()
    topo = html[html.index("<header"):html.index("</header>")]
    assert 'id="btn-sair"' in topo
    caixa = html[html.index('id="sair"'):]
    assert 'role="dialog"' in html[html.index('id="sair"') - 120:html.index('id="sair"') + 120]
    for rotulo in ("Guardar e sair", "Cancelar a sessão", "Voltar à sessão",
                   "Sim, cancelar"):
        assert rotulo in caixa, rotulo


def test_cancelar_chama_a_rota_e_esquece_o_andamento():
    js = _js()
    m = re.search(r"async function cancelaSessao\(\) \{(.*?)\n  \}", js, re.S)
    assert m, "trilha.js não tem cancelaSessao"
    corpo = m.group(1)
    assert '"/cancela"' in corpo and "Progresso.apaga(TOPICO)" in corpo


def test_guardar_e_sair_nao_esquece_o_andamento():
    js = _js()
    m = re.search(r"function guardaESai\(\) \{(.*?)\n  \}", js, re.S)
    assert m, "trilha.js não tem guardaESai"
    assert "Progresso.apaga" not in m.group(1) and "/cancela" not in m.group(1)


def test_a_resposta_so_trava_depois_de_confirmar():
    """O Rafael, em 19/11/2026: marcou errado e não conseguia voltar. A
    escolha dele (das três propostas): tocar na alternativa só a marca, e
    ela trava num "Confirmar resposta" — antes de o porquê aparecer, para
    quem viu as razões não trocar a resposta para combinar com elas."""
    js = _js()
    m = re.search(r'DESENHA\["pergunta"\] = function \(c, t\) \{(.*?)\n  \};', js, re.S)
    corpo = m.group(1)
    assert '"Confirmar resposta"' in corpo
    escolher = corpo[corpo.index('grupo("opcoes", "opcao",\n                       t.opcoes'):]
    escolher = escolher[:escolher.index("});")]
    assert "t-travada" not in escolher and "disabled = true" not in escolher
    confirmar = corpo[corpo.index('botao("Confirmar resposta"'):]
    confirmar = confirmar[:confirmar.index("confirma.disabled = true;")]
    assert "t-travada" in confirmar and "etapaRazao" in confirmar


def test_depois_de_cancelar_uma_sessao_nova_comeca_do_zero(destino):
    cliente = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, _ = _abre_e_anda(cliente)
    cliente.post("/sessoes/%s/cancela" % sessao)
    j = cliente.post("/sessoes", json={"codigo": ""}).json()
    assert j["sessao"] != sessao and j["tela"]["tipo"] == "entrada"
