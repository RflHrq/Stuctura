"""R1: a entrada inválida para de virar dado.

A revisão do ciclo 1 achou isto, e é o pior defeito que este sistema pode
ter: `{"escolha": -1}` devolvia **200**. Em Python, `opcoes[-1]` é a
última alternativa — então o episódio era classificado, a crença daquela
opção entrava no registro, e a sessão seguia para a tela de confiança
como se a pessoa tivesse escolhido. Nada no log distinguia isso de uma
resposta de verdade.

Um 500 aparece. Um dado inventado não. Numa coleta de 10 a 15 pessoas um
episódio falso é irreparável, porque a pessoa não volta para refazer.

A CAMADA 2 TINHA O MESMO DEFEITO, POR OUTRO CAMINHO
---------------------------------------------------
Lá o índice fora da faixa virava `None`, que é como o motor representa
"não escolheu razão" — e `classifica` devolve **lacuna** para isso. Um
erro de cliente virava uma lacuna declarada. Menos visível que a camada
1, e igualmente contaminante.

O QUE É E O QUE NÃO É ENTRADA VÁLIDA
------------------------------------
`None` continua sendo legítimo: é como "não sei" chega. Um índice que
existe é legítimo. Qualquer outra coisa é defeito de quem chamou, e o
motor estoura alto em vez de escolher por conta própria.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from mvp import log, motor
from mvp.dominio import carrega
from mvp.motor import Resposta

D = carrega()
FORA_DA_FAIXA = (-1, -99, 999, 3.0, 1.5)


@pytest.fixture(scope="module")
def d():
    return D


def ate(d, tipo, semente="s"):
    t = motor.inicia(d, semente=semente)
    for _ in range(60):
        if t.tela.tipo == tipo:
            return t
        if t.tela.tipo == "frase":
            t = motor.avanca(d, t.estado, Resposta(texto="x"))
            continue
        if t.tela.tipo == "atividade":
            a = next(x for x in d.atividades if x.id == t.tela.dados["atividade"])
            t = motor.avanca(d, t.estado, Resposta(escolha=a.indice_correto))
            continue
        if t.tela.tipo in ("razao", "confianca"):
            t = motor.avanca(d, t.estado, Resposta(
                escolha=0, confianca="tenho certeza"))
            continue
        t = motor.avanca(d, t.estado, Resposta())
    raise AssertionError("não cheguei a %r" % tipo)


# --------------------------------------------------------------------------
# O motor estoura em vez de escolher por conta própria
# --------------------------------------------------------------------------

def test_a_camada_1_recusa_indice_fora_da_faixa(d):
    t = ate(d, "atividade")
    for escolha in FORA_DA_FAIXA:
        with pytest.raises(motor.EscolhaInvalida):
            motor.avanca(d, t.estado, Resposta(escolha=escolha))


def test_o_menos_um_nao_pega_mais_a_ultima_alternativa(d):
    """O caso exato que a revisão achou, escrito como teste para não
    voltar: em Python `opcoes[-1]` é válido, e era isso o defeito."""
    t = ate(d, "atividade")
    a = next(x for x in d.atividades if x.id == t.tela.dados["atividade"])
    ultima = len(a.opcoes) - 1
    # O índice da última alternativa continua valendo pelo nome dela.
    assert motor.avanca(d, t.estado, Resposta(escolha=ultima)).eventos
    with pytest.raises(motor.EscolhaInvalida):
        motor.avanca(d, t.estado, Resposta(escolha=-1))


def test_a_camada_2_recusa_em_vez_de_virar_lacuna(d):
    """Antes isto virava `None`, e `None` na razão é LACUNA. Um erro de
    cliente entrava na base como uma pessoa declarando que não sabe."""
    t = ate(d, "razao")
    for escolha in FORA_DA_FAIXA:
        with pytest.raises(motor.EscolhaInvalida):
            motor.avanca(d, t.estado, Resposta(escolha=escolha))


def test_o_treino_recusa_do_mesmo_jeito(d):
    """Mesma indexação, mesma correção. O treino alimenta a sequência que
    decide o que o mapa mostra."""
    from mvp.test_motor import _politica

    t = motor.inicia(d, semente="t")
    pol = _politica(erra_no="B3", erra_diagnostico=2, d=d)
    for _ in range(120):
        if (t.tela.tipo == "atividade"
                and t.tela.dados["fase"] == motor.TREINO):
            break
        if t.tela.tipo == "mapa":
            raise AssertionError("o treino não apareceu")
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    for escolha in FORA_DA_FAIXA:
        with pytest.raises(motor.EscolhaInvalida):
            motor.avanca(d, t.estado, Resposta(escolha=escolha))


def test_nao_escolher_nada_continua_valendo(d):
    """`None` é como "não sei" chega, e não pode ser confundido com erro
    de cliente."""
    t = ate(d, "atividade")
    depois = motor.avanca(d, t.estado, Resposta(escolha=None, nao_sei=True))
    assert depois.eventos
    assert any(e.tipo == "camada1_respondida" for e in depois.eventos)


def test_todo_indice_que_existe_continua_valendo(d):
    t = ate(d, "atividade")
    a = next(x for x in d.atividades if x.id == t.tela.dados["atividade"])
    for i in range(len(a.opcoes)):
        assert motor.avanca(d, t.estado, Resposta(escolha=i)).eventos


# --------------------------------------------------------------------------
# A rota devolve 400, e o log não ganha nada
# --------------------------------------------------------------------------

@pytest.fixture
def cliente(tmp_path, monkeypatch):
    from mvp import app as aplicacao

    monkeypatch.setattr(log, "DESTINO", tmp_path / "eventos.jsonl")
    aplicacao.sessoes.clear()
    with TestClient(aplicacao.app) as c:
        yield c, tmp_path / "eventos.jsonl"


def _ate_a_atividade(c, sessao):
    for _ in range(12):
        j = c.post("/sessoes/%s/responder" % sessao,
                   json={"texto": "x"}).json()
        if j["tela"]["tipo"] == "atividade":
            return j
    raise AssertionError("não cheguei à atividade")


def test_a_rota_devolve_400_e_nao_grava_episodio(cliente):
    """Devolver 500 esconderia que o pedido é que estava errado; devolver
    200 era o defeito. 400 diz de quem é o problema."""
    c, arquivo = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    _ate_a_atividade(c, sessao)
    antes = arquivo.read_bytes()

    for escolha in (-1, 999):
        r = c.post("/sessoes/%s/responder" % sessao, json={"escolha": escolha})
        assert r.status_code == 400, escolha
        assert "alternativa" in r.json()["detail"].lower()

    assert arquivo.read_bytes() == antes, "a tentativa inválida escreveu no log"


def test_depois_de_uma_entrada_invalida_a_sessao_continua(cliente):
    """Recusar não pode custar a sessão: a pessoa está no meio da
    unidade, e o episódio dela ainda está aberto."""
    c, _ = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    j = _ate_a_atividade(c, sessao)
    quantas = len(j["tela"]["opcoes"])

    assert c.post("/sessoes/%s/responder" % sessao,
                  json={"escolha": -1}).status_code == 400
    r = c.post("/sessoes/%s/responder" % sessao, json={"escolha": quantas - 1})
    assert r.status_code == 200
    assert r.json()["tela"]["tipo"] in ("razao", "confianca")


def test_o_corpo_recusa_tipo_errado_antes_de_chegar_ao_motor(cliente):
    c, _ = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    _ate_a_atividade(c, sessao)
    r = c.post("/sessoes/%s/responder" % sessao, json={"escolha": 1.5})
    assert r.status_code == 422, "pydantic devia recusar float em int"


# --------------------------------------------------------------------------
# R3: limite no que entra (P2-B da revisão do ciclo 1)
# --------------------------------------------------------------------------

def _no_limite(c, sessao, tamanho):
    return c.post("/sessoes/%s/responder" % sessao,
                  json={"texto": "a" * tamanho, "ms": 1000})


def test_a_frase_no_limite_passa_e_um_caractere_acima_nao(cliente):
    """O teach-back é dado pessoal escrito em disco. Sem teto, uma
    colagem acidental põe meio megabyte de sabe-se lá o quê no log da
    coleta — a revisão achou 200.000 caracteres sendo aceitos."""
    from mvp.app import LIMITE_DA_FRASE

    c, arquivo = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    assert _no_limite(c, sessao, LIMITE_DA_FRASE).status_code == 200

    sessao = c.post("/sessoes").json()["sessao"]
    r = _no_limite(c, sessao, LIMITE_DA_FRASE + 1)
    assert r.status_code == 422
    assert not any(x.get("texto") for x in log.le(sessao, arquivo))


def test_o_tempo_negativo_e_o_impossivel_nao_entram_na_base(cliente):
    """`ms: -5` era aceito. Tempo negativo não é tempo, e duas horas num
    episódio não é alguém pensando."""
    from mvp.app import LIMITE_MS

    c, _ = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    for ms in (-1, LIMITE_MS + 1):
        r = c.post("/sessoes/%s/responder" % sessao, json={"texto": "x", "ms": ms})
        assert r.status_code == 422, ms
    assert c.post("/sessoes/%s/responder" % sessao,
                  json={"texto": "x", "ms": 0}).status_code == 200


def test_a_tela_diz_o_limite_e_impede_de_passar():
    """Sem o `maxlength`, o servidor recusaria 2.001 caracteres depois de
    a pessoa ter escrito tudo — e ela perderia o texto."""
    from mvp.app import LIMITE_DA_FRASE

    import pathlib
    import re

    html = pathlib.Path("mvp/web/index.html").read_text(encoding="utf-8")
    campo = re.search(r"<textarea[^>]*id=\"frase-texto\"[^>]*>", html)
    assert campo, "a caixa do teach-back sumiu"
    # O atributo de verdade, não uma substring dele: `data-maxlength`
    # contém `maxlength` e não limita nada. A primeira versão deste teste
    # caía nessa, e a sabotagem pegou.
    assert re.search(r"(^|\s)maxlength=\"%d\"" % LIMITE_DA_FRASE, campo.group())
    assert 'id="frase-contagem"' in html
