"""O porquê do acerto (docs/trilha.md, seção 7, "Novo, e opcional", item 2).

Só a pergunta de ABERTURA de cada premissa mostra retorno a quem acerta —
nas outras, o acerto segue direto. Por isso o porquê foi escrito para as
79 questões de abertura: com ele, o retorno de quem acerta diz uma frase
sobre AQUELA questão, e não a premissa genérica. Questão sem porquê usa o
que existe e não finge o resto.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from mvp import trilha, trilha_escada
from mvp.dominio import Atividade, carrega, topicos

RAIZ = pathlib.Path(__file__).resolve().parent


def _escadas(t, d):
    return trilha_escada.le(RAIZ / "dominio" / ("escada_%s.yaml" % t.replace("_", "")), d)


def _aberturas():
    """As questões de abertura, como a trilha as escolhe."""
    for t in topicos():
        d = carrega(topico=t)
        esc = _escadas(t, d)
        antes = ""
        for no in d.ordem:
            a = trilha.abertura(d, no, antes, esc[no].fora)
            antes = a.formato
            yield t, no, a


def test_a_questao_tem_onde_guardar_o_porque():
    campos = {f.name: f.default for f in Atividade.__dataclass_fields__.values()}
    assert campos.get("porque") == ""


def test_toda_questao_de_abertura_tem_o_porque():
    sem = [a.id for _, _, a in _aberturas() if not a.porque]
    assert sem == []
    assert len(list(_aberturas())) == 79


@pytest.mark.parametrize("t, no, a", list(_aberturas()),
                         ids=lambda x: getattr(x, "id", str(x)))
def test_o_porque_segue_a_regua(t, no, a):
    """Curto, sobre o código da questão, e no vocabulário do projeto."""
    palavras = len(a.porque.split())
    assert 6 <= palavras <= 32, (a.id, palavras)
    assert len(re.findall(r"[.!?](\s|$)", a.porque)) <= 2, a.id
    assert "`" not in a.porque, a.id
    assert not re.search(r"\b(recusa|não compila|nem compila)\b", a.porque, re.I), a.id


def test_quem_acerta_firme_ve_o_porque_daquela_questao():
    d = carrega(topico="kc_00")
    esc = _escadas("kc_00", d)
    t = trilha.inicia(d, esc, semente="porque")
    t = trilha.avanca(d, esc, t.estado, trilha.Entrada(
        acao="comecar", ritmo="completo", passo=t.estado.n))
    tela = t.estado.tela
    a = {x.id: x for x in d.atividades}[tela.dados["atividade"]]
    opcoes = trilha.motor.opcoes_na_tela(t.estado.semente, a)
    razoes = trilha._razoes_na_tela(d, t.estado.semente, a)
    t = trilha.avanca(d, esc, t.estado, trilha.Entrada(
        acao="responder", escolha=next(i for i, o in enumerate(opcoes) if o.correta),
        razao=next(i for i, r in enumerate(razoes) if r.correta),
        confianca="tenho certeza", passo=t.estado.n))
    assert t.estado.tela.tipo == "retorno"
    assert t.estado.tela.dados["veredito"] == "firme"
    assert t.estado.tela.dados["porque"] == a.porque != ""


def test_a_tela_mostra_o_porque():
    js = (RAIZ / "web" / "trilha.js").read_text(encoding="utf-8")
    assert "t.porque" in js and "Por que está certa:" in js
