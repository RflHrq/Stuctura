"""O caminho dos treze tópicos (docs/interface.md, seção 7).

A ordem é SUGERIDA — todos os tópicos ficam abertos — e mora num arquivo
do domínio, não no HTML. Quem confere que cada tópico vem depois dos
pré-requisitos é este teste, que lê o campo direto do YAML: o módulo do
caminho não o cita (só o `conceitos.py` cita, e há teste guardando).
"""

from __future__ import annotations

import pathlib

import yaml

from mvp import caminho
from mvp.dominio import topicos

DOMINIO = pathlib.Path(__file__).resolve().parent / "dominio"


def _requisitos():
    return {t: list(yaml.safe_load(
        (DOMINIO / ("topic_%s.yaml" % t.replace("_", ""))).read_text(
            encoding="utf-8")).get("prerequisites") or [])
        for t in topicos()}


def test_a_ordem_e_a_do_desenho():
    assert caminho.ordem() == [
        "kc_00", "kc_02", "kc_03", "kc_04", "kc_05", "kc_06", "kc_07",
        "kc_01", "kc_08", "kc_09", "kc_10", "kc_11", "kc_12"]


def test_todo_topico_aparece_uma_vez():
    assert sorted(caminho.ordem()) == sorted(topicos())
    assert len(set(caminho.ordem())) == len(caminho.ordem())


def test_cada_topico_vem_depois_dos_seus_requisitos():
    posicao = {t: i for i, t in enumerate(caminho.ordem())}
    fora = [(t, r) for t, rs in _requisitos().items() for r in rs
            if posicao[r] > posicao[t]]
    assert fora == []


def test_os_tres_do_fim_nao_dependem_um_do_outro():
    """No fim o caminho se abre em três: kc_10, kc_11 e kc_12."""
    fim = set(caminho.ordem()[-3:])
    req = _requisitos()
    assert not [(t, r) for t in fim for r in req[t] if r in fim]
    assert caminho.fim() == ["kc_10", "kc_11", "kc_12"]


def test_cada_topico_tem_um_rotulo_curto():
    rotulos = caminho.rotulos()
    assert set(rotulos) == set(topicos())
    assert all(0 < len(r) <= 24 for r in rotulos.values()), rotulos


def test_o_portal_manda_a_ordem_do_caminho_e_os_rotulos(tmp_path):
    from fastapi.testclient import TestClient

    from mvp import portal
    """A lista continua na ordem numérica — é o que o teste do portal de
    12/11/2026 (test_portal.py, anterior a este ramo) afirma — e a ordem do
    caminho vai num campo à parte, que a página usa para ordenar."""
    j = TestClient(portal.cria_portal(tmp_path)).get("/topicos").json()
    lista = j["topicos"]
    assert [t["id"] for t in lista] == list(topicos())
    assert j["caminho"] == caminho.ordem()
    assert {t["id"]: t["rotulo"] for t in lista} == caminho.rotulos()
    assert {t["id"] for t in lista if t["fim"]} == set(caminho.fim())


def test_a_pagina_inicial_ordena_pelo_caminho():
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    assert "j.caminho" in html


# --------------------------------------------------------------------------
# O caminho desenhado (mvp/web/caminho.js e portal.html)
# --------------------------------------------------------------------------

from mvp.test_interface import (_roda_node, contraste, cores_do_tema,  # noqa: E402
                                tem_node)

WEB = pathlib.Path(__file__).resolve().parent / "web"

_TOPICOS = [{"id": t, "fim": t in ("kc_10", "kc_11", "kc_12")}
            for t in ["kc_00", "kc_02", "kc_03", "kc_04", "kc_05", "kc_06",
                      "kc_07", "kc_01", "kc_08", "kc_09", "kc_10", "kc_11",
                      "kc_12"]]


def _estados(guardados: dict):
    import json
    programa = """
    global.window = global;
    require(require("path").join(WEB, "caminho.js"));
    console.log(JSON.stringify(global.Caminho.estados(%s, %s)));
    """ % (json.dumps(_TOPICOS), json.dumps(guardados))
    return json.loads(_roda_node(programa))


@tem_node
def test_sem_nada_feito_o_primeiro_e_o_proximo():
    e = _estados({})
    assert e["proximo"] == "kc_00"
    assert {v["estado"] for v in e["porId"].values()} == {"aberto"}


@tem_node
def test_o_feito_o_andamento_e_o_proximo():
    e = _estados({"kc_00": {"feitas": 5, "total": 5, "fim": True},
                  "kc_03": {"feitas": 2, "total": 6, "fim": False}})
    assert e["porId"]["kc_00"]["estado"] == "feito"
    assert e["porId"]["kc_03"]["estado"] == "andamento"
    assert (e["porId"]["kc_03"]["feitas"], e["porId"]["kc_03"]["total"]) == (2, 6)
    # o próximo é o primeiro da ordem ainda não feito — o kc_02, que vem
    # antes do kc_03 no caminho, mesmo sem ter começado
    assert e["proximo"] == "kc_02"
    assert e["porId"]["kc_02"]["estado"] == "aberto"


@tem_node
def test_o_proximo_pode_estar_em_andamento():
    e = _estados({"kc_00": {"feitas": 3, "total": 5, "fim": False}})
    assert e["proximo"] == "kc_00"
    assert e["porId"]["kc_00"]["estado"] == "andamento"


@tem_node
def test_com_tudo_feito_nao_ha_proximo():
    e = _estados({t["id"]: {"feitas": 6, "total": 6, "fim": True} for t in _TOPICOS})
    assert e["proximo"] is None


@tem_node
def test_as_paradas_nao_se_atropelam():
    import json
    programa = """
    global.window = global;
    require(require("path").join(WEB, "caminho.js"));
    console.log(JSON.stringify(global.Caminho.posicoes(10, 3)));
    """
    p = json.loads(_roda_node(programa))
    assert len(p["tronco"]) == 10 and len(p["fim"]) == 3
    todos = p["tronco"] + p["fim"]
    assert all(20 <= x <= 310 and 20 <= y <= 410 for x, y in todos)
    pertos = [(a, b) for i, a in enumerate(todos) for b in todos[i + 1:]
              if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** .5 < 34]
    assert pertos == []


def test_as_cores_da_trilha_passam_no_contraste():
    for tema in ("claro", "escuro"):
        c = cores_do_tema(tema)
        for frente, fundo in (("tinta", "trilha-fundo"), ("tinta2", "trilha-fundo"),
                              ("destaque", "trilha-fundo"), ("tinta2", "cartao"),
                              ("destaque", "cartao")):
            assert contraste(c[frente], c[fundo]) >= 4.5, (tema, frente, fundo)


def test_a_pagina_inicial_desenha_o_caminho():
    html = (WEB / "portal.html").read_text(encoding="utf-8")
    for js in ("progresso.js", "caminho.js"):
        assert "/web/%s?v=" % js in html, js
    assert "Próximo sugerido" in html
    for legenda in ("já feito", "próximo", "em andamento", "aberto"):
        assert legenda in html, legenda
    assert 'aria-label="O caminho dos tópicos"' in html
    assert "Caminho.desenha" in html and "Progresso.le" in html
    # a pulsação do próximo só anda com movimento permitido
    assert "prefers-reduced-motion: no-preference" in html
