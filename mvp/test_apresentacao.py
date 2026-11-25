"""Os slides da defesa, conferidos contra a monografia (docs/apresentacao.md).

Tudo o que um slide explica está na monografia entregue, e o slide diz
onde, na numeração do PDF. Estes testes acusam a referência que o PDF não
tem, o número que o texto não traz e a frase entre aspas que o texto não
contém.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import confere_apresentacao as ca  # noqa: E402

LATEX = RAIZ / "docs" / "monografia" / "latex"
DECK = RAIZ / "apresentacao"


@pytest.fixture(scope="module")
def refs():
    if not (LATEX / "TCC_STRUCTURA.loq").exists():
        pytest.fail("compile a monografia: o deck cita a numeração do PDF")
    return ca.referencias_do_pdf(LATEX)


@pytest.fixture(scope="module")
def monografia():
    return ca.texto_da_monografia(RAIZ / "docs" / "monografia")


def _deck(corpo, ref="Seção 1.1"):
    return ('<html><body><section class="slide" data-ref="%s">%s'
            '</section></body></html>' % (ref, corpo))


def test_as_referencias_do_pdf(refs):
    assert refs["Quadro 3"] == 30
    assert refs["Figura 1"] == 29
    assert refs["Seção 1.1"] == 14
    assert refs["Seção 1"] == 14
    assert refs["Apêndice C"] == 80
    assert "Quadro 24" in refs and "Quadro 25" not in refs


def test_a_referencia_que_o_pdf_nao_tem_e_acusada(refs, monografia):
    p = ca.problemas(_deck("<p>texto</p>", "Quadro 30"), refs, monografia)
    assert len(p) == 1 and "Quadro 30" in p[0]
    assert ca.problemas(_deck("<p>texto</p>", "Quadro 3 · Seção 3.2"),
                        refs, monografia) == []


def test_o_numero_que_a_monografia_nao_tem_e_acusado(refs, monografia):
    p = ca.problemas(_deck("<p>4 321 testes</p>"), refs, monografia)
    assert len(p) == 1 and "4 321" in p[0]
    assert ca.problemas(_deck("<p>7 568 testes</p>"), refs, monografia) == []


def test_a_frase_entre_aspas_que_a_monografia_nao_tem_e_acusada(
        refs, monografia):
    p = ca.problemas(_deck("<p>“o sistema ensina tudo sozinho”</p>"),
                     refs, monografia)
    assert len(p) == 1 and "ensina tudo" in p[0]
    assert ca.problemas(_deck("<p>“a máquina respondeu”</p>"),
                        refs, monografia) == []


def test_notas_codigo_e_rodape_ficam_fora_da_conferencia(refs, monografia):
    corpo = ('<pre>int idade = 4321;</pre>'
             '<aside class="notas">diga 4321</aside>'
             '<footer>p. 999</footer>')
    assert ca.problemas(_deck(corpo), refs, monografia) == []


def test_a_cena_do_deck_e_a_do_sistema():
    from mvp import trilha
    from mvp.dominio import carrega
    from mvp.trilha_escada import le
    d = carrega(topico="kc_06")
    e = le(RAIZ / "mvp" / "dominio" / "escada_kc06.yaml", d)["B1"]
    texto = (DECK / "cena.js").read_text(encoding="utf-8")
    dados = json.loads(re.search(r"window\.CENA = (\{.*\});", texto,
                                 re.S).group(1))
    assert dados == {"cena": trilha.cena_json(e.cena),
                     "codigo": e.revisao.codigo}
