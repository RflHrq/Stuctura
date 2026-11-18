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
    lista = TestClient(portal.cria_portal(tmp_path)).get("/topicos").json()["topicos"]
    assert [t["id"] for t in lista] == caminho.ordem()
    assert {t["id"]: t["rotulo"] for t in lista} == caminho.rotulos()
    assert {t["id"] for t in lista if t["fim"]} == set(caminho.fim())
