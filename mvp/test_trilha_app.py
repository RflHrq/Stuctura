"""As rotas da trilha, e o registro dela.

O motor é puro; quem guarda o estado, grava o registro e fala HTTP é
`mvp/trilha_app.py`, numa fábrica — `cria_app(dominio, escadas, destino)`
—, sem variável de módulo: dois tópicos são duas chamadas, e não duas
cópias do arquivo.

O que estes testes guardam:

  - uma sessão inteira atravessa o HTTP e chega ao mapa;
  - o registro traz a entrada ANTES do que ela provocou, que é o que
    deixa a sessão reexecutável;
  - pedido que não cabe (resposta repetida, peça repetida, índice fora)
    é 400, não grava nada e não move o estado;
  - nada disso toca o registro do fluxo atual.

Toda sessão daqui usa `tmp_path`. Nenhuma vai para `coleta/`.
"""

from __future__ import annotations

import dataclasses
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import trilha_alunos  # noqa: E402

from mvp import log, trilha, trilha_app, trilha_escada, trilha_log  # noqa: E402
from mvp.dominio import carrega  # noqa: E402
from mvp.motor import Tela  # noqa: E402

D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "dominio" / "escada_kc00.yaml", D)


@pytest.fixture
def destino(tmp_path):
    return tmp_path / "trilha" / "kc_00.jsonl"


@pytest.fixture
def app(destino):
    return trilha_app.cria_app(D, ESC, destino)


@pytest.fixture
def cliente(app):
    return TestClient(app)


def _tela(j: dict) -> Tela:
    return Tela(tipo=j["tipo"], texto=j.get("texto", ""),
                dados={k: v for k, v in j.items() if k not in ("tipo", "texto")})


def _corpo(entrada: trilha.Entrada) -> dict:
    corpo = dataclasses.asdict(entrada)
    corpo["pecas"] = list(corpo["pecas"])
    return corpo


def _age(cliente, sessao, entrada, passo=None):
    """Uma entrada pelo HTTP. O pedido diz de que tela é (`passo`); sem
    ser dito, vale o da tela em que a sessão está — que é o que um
    cliente em dia mandaria."""
    corpo = _corpo(entrada)
    corpo["passo"] = (cliente.app.state.sessoes[sessao].n
                      if passo is None else passo)
    return cliente.post("/sessoes/%s/agir" % sessao, json=corpo)


def _abre(cliente, modo="direto", ritmo="completo", codigo=""):
    j = cliente.post("/sessoes", json={"codigo": codigo}).json()
    r = _age(cliente, j["sessao"], trilha.Entrada(
        acao="comecar", modo=modo, ritmo=ritmo))
    assert r.status_code == 200, r.text
    return j["sessao"], r.json()


def _caminha(app, cliente, persona, modo="direto", ritmo="completo"):
    """Uma sessão inteira PELO HTTP. O aluno simulado lê a tela que veio
    na resposta; o estado só serve para ele saber a versão do degrau."""
    sessao, j = _abre(cliente, modo, ritmo)
    telas = [j["tela"]]
    for _ in range(400):
        if j["tela"]["tipo"] == "mapa":
            return sessao, telas, j
        entrada = trilha_alunos.responde(
            D, ESC, _tela(j["tela"]), persona, app.state.sessoes[sessao])
        r = _age(cliente, sessao, entrada)
        assert r.status_code == 200, r.text
        j = r.json()
        telas.append(j["tela"])
    raise AssertionError("a sessão não terminou")


# --------------------------------------------------------------------------
# Abrir
# --------------------------------------------------------------------------

def test_abrir_devolve_a_tela_de_entrada_e_o_progresso(cliente):
    r = cliente.post("/sessoes", json={})
    assert r.status_code == 200
    j = r.json()
    assert j["tela"]["tipo"] == "entrada" and len(j["sessao"]) == 12
    assert j["progresso"] == {
        "feitas": 0, "total": 5,
        "premissas": [{"no": n, "resultado": ""} for n in D.ordem]}


def test_a_semente_e_o_codigo_da_sessao(app, cliente):
    sessao, _ = _abre(cliente)
    assert app.state.sessoes[sessao].semente == sessao


def test_a_pasta_do_registro_so_nasce_na_primeira_gravacao(tmp_path):
    destino = tmp_path / "trilha" / "kc_00.jsonl"
    app = trilha_app.cria_app(D, ESC, destino)
    assert not (tmp_path / "trilha").exists()
    TestClient(app).post("/sessoes", json={})
    assert destino.exists()


def test_a_saude_diz_o_topico(cliente):
    assert cliente.get("/saude").json() == {
        "ok": True, "topico": "kc_00", "titulo": D.titulo, "premissas": 5,
        "degraus": sum(len(e.degraus) for e in ESC.values())}


def test_topico_sem_escada_completa_nao_sobe(tmp_path):
    with pytest.raises(ValueError) as erro:
        trilha_app.cria_app(D, {"B1": ESC["B1"]}, tmp_path / "x.jsonl")
    assert "B2" in str(erro.value)


# --------------------------------------------------------------------------
# A sessão inteira
# --------------------------------------------------------------------------

@pytest.mark.parametrize("persona, modo", [
    ("sabe", "direto"), ("nao_sabe_aprende", "direto"),
    ("crente_aprende", "direto"), ("nao_sabe_erra", "explique"),
    ("chuta_com_certeza", "direto")])
def test_uma_sessao_inteira_pelo_http_chega_ao_mapa(app, cliente, persona, modo):
    sessao, telas, fim = _caminha(app, cliente, persona, modo)
    assert fim["tela"]["tipo"] == "mapa"
    assert fim["progresso"]["feitas"] == fim["progresso"]["total"] == 5
    assert [p["no"] for p in fim["tela"]["premissas"]] == list(D.ordem)
    # O HTTP não muda o caminho: as mesmas telas do motor em processo.
    direto = trilha_alunos.caminha(D, ESC, persona, modo, semente=sessao)
    assert telas == [t.json() for t in direto.telas[1:]]


def test_o_progresso_anda_com_as_premissas(app, cliente):
    sessao, j = _abre(cliente, ritmo="rapido")
    assert j["progresso"]["feitas"] == 0
    for _ in range(2):                                   # responde e continua
        j = _age(cliente, sessao, trilha_alunos.responde(
            D, ESC, _tela(j["tela"]), "sabe", app.state.sessoes[sessao])).json()
    assert j["progresso"]["feitas"] == 1
    assert j["progresso"]["premissas"][0] == {"no": "B1", "resultado": "ja_sabia"}


def test_a_resposta_diz_se_acertou_para_a_tela_piscar(app, cliente):
    sessao, j = _abre(cliente, modo="explique")
    assert j["tela"]["tipo"] == "degrau" and j["veredito"] is None
    certa = _age(cliente, sessao, trilha_alunos.responde(
        D, ESC, _tela(j["tela"]), "sabe", app.state.sessoes[sessao])).json()
    assert certa["veredito"] == "certa" and certa["tela"]["tipo"] == "degrau"
    errada = _age(cliente, sessao, trilha_alunos.responde(
        D, ESC, _tela(certa["tela"]), "nao_sabe_erra",
        app.state.sessoes[sessao])).json()
    assert errada["veredito"] == "errada" and errada["tela"]["tipo"] == "retorno"


def test_a_resposta_diz_o_modo_e_o_ritmo_da_sessao(cliente):
    """Quem reabre a pagina com o codigo nao passou pela tela de entrada:
    e por aqui que os ajustes sabem o que marcar."""
    j = cliente.post("/sessoes", json={"codigo": "P10"}).json()
    assert (j["modo"], j["ritmo"]) == ("", "completo")
    sessao, j = _abre(cliente, modo="explique", ritmo="rapido", codigo="P11")
    assert (j["modo"], j["ritmo"]) == ("explique", "rapido")
    j = _age(cliente, sessao, trilha.Entrada(acao="modo", modo="direto")).json()
    assert (j["modo"], j["ritmo"]) == ("direto", "rapido")
    de_novo = cliente.post("/sessoes", json={"codigo": "P11"}).json()
    assert (de_novo["modo"], de_novo["ritmo"]) == ("direto", "rapido")


def test_a_explicacao_vem_com_a_mesma_tela(cliente):
    sessao, j = _abre(cliente)
    assert j["explicacao"] is None
    r = _age(cliente, sessao, trilha.Entrada(acao="explicacao")).json()
    assert r["tela"] == j["tela"]
    assert r["explicacao"]["premissa"] == "B1"
    assert r["explicacao"]["frases"] and r["explicacao"]["codigo"]


# --------------------------------------------------------------------------
# O registro
# --------------------------------------------------------------------------

def test_o_registro_traz_a_entrada_antes_do_que_ela_provocou(cliente, destino):
    sessao, _ = _abre(cliente)
    linhas = trilha_log.le(destino, sessao)
    assert linhas[0]["tipo"] == "trilha_iniciada"
    # A versão é também a das REGRAS da trilha: passou a 2 em 13/11/2026
    # e a 3 em 16/11/2026, quando a reconferência deixou de repetir passo
    # já visto antes de uma questão nova (mvp/test_trilha_diagnostico.py);
    # uma sessão de outra versão não é refeita.
    assert all(l["v"] == trilha_log.VERSAO == 3 for l in linhas)
    assert all(l["sessao"] == sessao and l["ts"] for l in linhas)
    i = next(k for k, l in enumerate(linhas) if l["tipo"] == "entrada_recebida")
    assert (linhas[i]["acao"], linhas[i]["modo"]) == ("comecar", "direto")
    assert [l["tipo"] for l in linhas[i + 1:]] == [
        "trilha_comecada", "premissa_aberta"]


def test_o_registro_guarda_cada_entrada_de_uma_sessao_inteira(app, cliente, destino):
    sessao, telas, _ = _caminha(app, cliente, "nao_sabe_aprende")
    linhas = trilha_log.le(destino, sessao)
    entradas = [l for l in linhas if l["tipo"] == "entrada_recebida"]
    assert len(entradas) == len(telas)           # o "comecar" e uma por tela
    assert linhas[-1]["tipo"] == "trilha_encerrada"
    assert [l["tipo"] for l in linhas].count("premissa_fechada") == 5


def test_dado_com_nome_da_casa_nao_troca_o_tipo_da_linha(destino):
    from mvp.motor import Evento
    trilha_log.grava(destino, "s", [Evento("x", {"tipo": "y", "sessao": "z", "a": 1})])
    linha = trilha_log.le(destino)[0]
    assert (linha["tipo"], linha["sessao"], linha["a"]) == ("x", "s", 1)
    assert linha["tipo_do_evento"] == "y" and linha["sessao_do_evento"] == "z"


def test_ler_um_registro_que_nao_existe_devolve_vazio(tmp_path):
    assert trilha_log.le(tmp_path / "nao_ha.jsonl") == []


def test_duas_sessoes_no_mesmo_arquivo_nao_se_misturam(cliente, destino):
    a, _ = _abre(cliente)
    b, _ = _abre(cliente, modo="explique")
    assert a != b
    assert {l["sessao"] for l in trilha_log.le(destino, a)} == {a}
    assert {l["sessao"] for l in trilha_log.le(destino)} == {a, b}


def test_o_app_nao_escreve_no_registro_do_fluxo_atual(app, cliente, tmp_path,
                                                      monkeypatch):
    atual = tmp_path / "fluxo_atual.jsonl"
    monkeypatch.setattr(log, "DESTINO", atual)
    _caminha(app, cliente, "sabe")
    assert not atual.exists()


# --------------------------------------------------------------------------
# O que não cabe
# --------------------------------------------------------------------------

def test_resposta_repetida_da_400_e_nao_grava(app, cliente, destino):
    """Review Focus 1: o segundo envio de um duplo clique."""
    sessao, j = _abre(cliente)
    resposta = trilha_alunos.responde(
        D, ESC, _tela(j["tela"]), "sabe", app.state.sessoes[sessao])
    assert _age(cliente, sessao, resposta).status_code == 200
    antes, estado = len(trilha_log.le(destino)), app.state.sessoes[sessao]
    r = _age(cliente, sessao, resposta)
    assert r.status_code == 400 and "não cabe" in r.json()["detail"]
    assert len(trilha_log.le(destino)) == antes
    assert app.state.sessoes[sessao] is estado


def test_peca_repetida_ou_fora_da_faixa_da_400(app, cliente, destino):
    """Review Focus 3: pedido malformado não é resposta errada."""
    sessao, j = _abre(cliente, modo="explique")
    while j["tela"]["forma"] != "montar":
        j = _age(cliente, sessao, trilha_alunos.responde(
            D, ESC, _tela(j["tela"]), "sabe", app.state.sessoes[sessao])).json()
    antes, estado = len(trilha_log.le(destino)), app.state.sessoes[sessao]
    for ruim in ([0, 0, 1], [0, 99], [-1], []):
        r = cliente.post("/sessoes/%s/agir" % sessao,
                         json={"acao": "responder", "pecas": ruim,
                               "passo": estado.n})
        assert r.status_code == 400, ruim
    assert len(trilha_log.le(destino)) == antes
    assert app.state.sessoes[sessao] is estado


def test_sessao_desconhecida_da_404(cliente):
    """Review Focus 2: a página aberta depois de o servidor reiniciar."""
    r = cliente.post("/sessoes/nao_existe/agir",
                     json={"acao": "continuar", "passo": 3})
    assert r.status_code == 404


def test_sessao_sem_codigo_continua_depois_de_o_servidor_reiniciar(destino):
    """O que aconteceu com o Rafael em 14/11/2026: o servidor caiu no meio
    de uma sessão aberta sem código, e a página disse que a sessão se
    perdera — com o registro inteiro dela em disco. O registro guarda as
    entradas e o motor é puro: a sessão é refeita pelo número dela, como
    já era pelo código."""
    antes = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, j = _abre(antes)
    assert len(sessao) == 12          # aberta sem código: o número sorteado
    passo = j["passo"]

    depois = TestClient(trilha_app.cria_app(D, ESC, destino))   # reiniciou
    assert sessao not in depois.app.state.sessoes
    r = depois.post("/sessoes/%s/agir" % sessao,
                    json={"acao": "nao_sei", "passo": passo})
    assert r.status_code == 200, r.text

    # A tela é a que o motor daria, a partir do estado refeito.
    refeita = trilha_log.reconstroi(D, ESC, destino, sessao)
    assert r.json()["passo"] == refeita.estado.n
    assert r.json()["tela"] == refeita.estado.tela.json()
    tipos = [l["tipo"] for l in trilha_log.le(destino, sessao)]
    assert "sessao_reconstruida" in tipos


def test_sessao_que_nao_da_para_refazer_diz_por_que(destino):
    """Se o conteúdo do tópico mudou depois de a sessão começar, as mesmas
    respostas cairiam em telas diferentes. A página recebe 410, com a
    frase de quem está na tela — e não um 404 mudo."""
    antes = TestClient(trilha_app.cria_app(D, ESC, destino))
    sessao, j = _abre(antes)
    outra = dict(ESC)
    no = next(iter(outra))
    outra[no] = dataclasses.replace(
        outra[no], revisao=dataclasses.replace(
            outra[no].revisao, frases=outra[no].revisao.frases + ("mudou",)))
    depois = TestClient(trilha_app.cria_app(D, outra, destino))
    r = depois.post("/sessoes/%s/agir" % sessao,
                    json={"acao": "nao_sei", "passo": j["passo"]})
    assert r.status_code == 410
    assert "mudou" in r.json()["detail"]
    assert sessao not in depois.app.state.sessoes


def test_a_pagina_mostra_a_frase_da_sessao_que_nao_volta():
    js = (RAIZ / "web" / "trilha.js").read_text(encoding="utf-8")
    assert "r.status === 410" in js and "perdeu(r.json && r.json.detail)" in js


@pytest.mark.parametrize("codigo", ["9abc", "a b", "a/b", "x" * 17, "ç"])
def test_codigo_fora_do_formato_da_400(cliente, codigo):
    assert cliente.post("/sessoes", json={"codigo": codigo}).status_code == 400


def test_o_mesmo_codigo_devolve_a_tela_em_que_a_sessao_estava(cliente, destino):
    sessao, j = _abre(cliente, codigo="P01")
    assert sessao == "P01"
    antes = len(trilha_log.le(destino))
    de_novo = cliente.post("/sessoes", json={"codigo": "P01"}).json()
    assert de_novo["sessao"] == "P01" and de_novo["tela"] == j["tela"]
    assert de_novo["progresso"] == j["progresso"]
    depois = trilha_log.le(destino)
    assert [l["tipo"] for l in depois[antes:]] == ["sessao_retomada"]


def test_codigo_que_esta_no_registro_e_nao_na_memoria_e_retomado(destino):
    """Depois de um reinício o servidor não tem mais a sessão na memória.

    A primeira versão recusava com 409, e a revisão do ramo mostrou o
    custo: religar o sistema queimava todos os códigos. O motor é puro e
    o registro guarda as entradas, então a sessão é refeita — os casos
    difíceis estão em `mvp/test_trilha_revisao.py`.
    """
    primeiro = TestClient(trilha_app.cria_app(D, ESC, destino))
    _, j = _abre(primeiro, codigo="P02")
    outro = TestClient(trilha_app.cria_app(D, ESC, destino))
    r = outro.post("/sessoes", json={"codigo": "P02"})
    assert r.status_code == 200 and r.json()["tela"] == j["tela"]
    assert outro.post("/sessoes", json={"codigo": "P03"}).status_code == 200


@pytest.mark.parametrize("corpo", [
    {"acao": "continuar", "ms": -1},
    {"acao": "responder", "texto": "x" * 201},
    {"acao": "responder", "pecas": list(range(41))},
    {"acao": "responder", "escolha": "a"},
    {"acao": "continuar", "passo": "dois"},
])
def test_corpo_fora_do_limite_da_422(cliente, corpo):
    sessao, j = _abre(cliente)
    corpo = {"passo": j["passo"], **corpo}
    r = cliente.post("/sessoes/%s/agir" % sessao, json=corpo)
    assert r.status_code == 422
