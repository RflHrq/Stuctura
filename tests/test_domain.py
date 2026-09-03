"""Invariantes do domínio que sustentam o estudo, não só o código.

Estes testes não protegem o motor de exceções — protegem os desfechos da
§12. Uma CIU cujo distrator aponta para crença de outro KC, por exemplo,
não quebra nada em execução: só produz uma Q-matrix que não valida.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic
from engine.loader import load


@pytest.fixture(scope="module")
def d():
    return load()


# --------------------------------------------------------------------------
# Números publicados (§ sumário executivo do dossiê)
# --------------------------------------------------------------------------

def test_numeros_do_dossie(d):
    """O domínio tem de reproduzir o que o dossiê afirma publicamente."""
    assert len(d.kcs) == 12
    assert sum(len(k.nodes) for k in d.kcs.values()) == 93
    assert len(d.misconceptions) == 34
    assert len(d.cius) == 47


def test_proveniencia_declarada_por_toda_crenca(d):
    graus = {}
    for m in d.misconceptions.values():
        assert m.provenance, "%s sem proveniência" % m.id
        graus[m.grade] = graus.get(m.grade, 0) + 1
    assert graus == {"D": 1, "T": 7, "L": 23, "N": 3}
    assert "E" not in graus, "o dossiê declara E=0: nenhuma crença sem fonte"


def test_plano_medio_e_o_numero_reportado(d):
    planos = [len(socratic.full_plan(d, m.kc, m.node)) for m in d.misconceptions.values()]
    assert round(sum(planos) / len(planos), 1) == 4.7


def test_tres_kcs_exigem_diagrama(d):
    """Cai da estrutura: são exatamente os KCs com ataque em nó-base."""
    com_diagrama = {k.id for k in d.kcs.values() if k.socratic == "diagram"}
    com_fundacional = {m.kc for m in d.misconceptions.values() if m.kind == "foundational"}
    assert com_diagrama == com_fundacional == {"kc_01", "kc_04", "kc_07"}


# --------------------------------------------------------------------------
# Coerência da Q-matrix — o desfecho primário do estudo
# --------------------------------------------------------------------------

def test_toda_crenca_e_detectavel_por_alguma_ciu(d):
    """Crença que nenhuma atividade alcança é crença que o estudo não observa."""
    detectaveis = {m for c in d.cius.values() for m in c.misconception_ids()}
    assert set(d.misconceptions) - detectaveis == set()


def test_distrator_aponta_para_crenca_do_mesmo_kc(d):
    """Um distrator de outro KC produz Q-matrix incoerente.

    Vale para o ataque primário OU secundário: a crença tem de tocar o KC
    da atividade por alguma via.
    """
    problemas = []
    for c in d.cius.values():
        for mid in c.misconception_ids():
            m = d.misconceptions[mid]
            kcs_da_crenca = {m.kc} | {a[0] for a in m.also_negates}
            if c.kc not in kcs_da_crenca:
                problemas.append("%s (%s) -> %s nega %s" % (c.id, c.kc, mid, kcs_da_crenca))
    assert not problemas, "\n".join(problemas)


def test_targets_pertencem_ao_kc_da_ciu(d):
    for c in d.cius.values():
        for t in c.targets:
            assert t in d.kcs[c.kc].nodes, "%s: target %s fora do %s" % (c.id, t, c.kc)


def test_toda_ciu_tem_forma_de_resposta(d):
    for c in d.cius.values():
        assert c.options or c.steps or c.answer, "%s não mede nada" % c.id


def test_ciu_de_escolha_tem_uma_correta_e_distrator_mapeado(d):
    for c in d.cius.values():
        if not c.is_choice:
            continue
        assert sum(1 for o in c.options if o.correct) == 1, c.id
        assert any(o.misconception for o in c.options if not o.correct), c.id


# --------------------------------------------------------------------------
# Recorte do piloto
# --------------------------------------------------------------------------

def test_piloto_respeita_a_ordem_de_ensino(d):
    ordens = [d.kcs[k].teaching_order for k in d.pilot_sequence]
    assert ordens == sorted(ordens)


def test_piloto_cobre_os_dois_regimes(d):
    """Um KC com diagrama obrigatório e outros com socrático puro."""
    modos = {d.kcs[k].socratic for k in d.pilot_sequence}
    assert modos == {"diagram", "pure"}


def test_todo_kc_do_piloto_tem_ciu_diagnostica(d):
    for k in d.pilot_sequence:
        assert [c for c in d.cius_of(k) if c.phase == "diagnostic"], k


# --------------------------------------------------------------------------
# Hash do domínio (§15)
# --------------------------------------------------------------------------

def test_hash_e_estavel_e_muda_com_o_conteudo(d, tmp_path):
    assert d.hash == load().hash
    assert d.hash.startswith("sha256:")

    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.iterdir():
        (copia / f.name).write_bytes(f.read_bytes())
    assert load(copia).hash == d.hash

    alvo = copia / "kcs.yaml"
    alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# tocado\n", encoding="utf-8")
    assert load(copia).hash != d.hash
