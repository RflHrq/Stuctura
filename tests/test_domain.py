"""Invariantes do domínio que sustentam o estudo, não só o código.

Estes testes não protegem o motor de exceções — protegem os desfechos da
§12. Uma CIU cujo distrator aponta para crença de um KC que ela nem exige,
por exemplo, não quebra nada em execução: só produz uma Q-matrix que não
valida.

O domínio é a fonte; o loader se adapta a ele. Por isso os testes afirmam
propriedades DERIVADAS (quantos KCs exigem diagrama, quais crenças são
fundacionais) em vez de campos declarados: se elas caem da estrutura, a
estrutura está certa.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic
from engine.loader import load
from tools import validate

GOLDEN = Path(__file__).with_name("golden_plans.json")


@pytest.fixture(scope="module")
def d():
    return load()


# --------------------------------------------------------------------------
# Números publicados no dossiê
# --------------------------------------------------------------------------

def test_numeros_do_dossie(d):
    assert len(d.kcs) == 12
    assert sum(len(k.nodes) for k in d.kcs.values()) == 93
    assert len(d.misconceptions) == 34


def test_proveniencia_declarada_por_toda_crenca(d):
    graus: dict[str, int] = {}
    for m in d.misconceptions.values():
        assert m.sources, "%s sem fonte" % m.id
        graus[m.grade] = graus.get(m.grade, 0) + 1
    assert graus == {"D": 1, "T": 7, "L": 23, "N": 3}
    assert "E" not in graus, "o dossiê declara E=0: nenhuma crença sem fonte"


def test_plano_medio_e_o_numero_reportado(d):
    planos = [len(socratic.full_plan(d, m.kc, m.node)) for m in d.misconceptions.values()]
    assert round(sum(planos) / len(planos), 1) == 4.7


def test_grau_n_declara_que_a_crenca_e_hipotese(d):
    """Grau N documenta o ERRO em norma, não a crença que o produz.

    A monografia precisa dizer isso, e o YAML tem de registrar onde.
    """
    for m in d.misconceptions.values():
        if m.grade == "N":
            assert m.notes, "%s é grau N e não explica o limite da fonte" % m.id


# --------------------------------------------------------------------------
# O que CAI da estrutura (§2.1) — derivado, não declarado
# --------------------------------------------------------------------------

def test_classe_da_crenca_deriva_do_tipo_do_no(d):
    for m in d.misconceptions.values():
        negado = d.node(m.kc, m.node)
        assert m.is_foundational == negado.is_base, m.id


def test_tres_kcs_exigem_diagrama_e_sao_os_de_ataque_em_base(d):
    com_diagrama = {k for k in d.kcs if d.requires_diagram(k)}
    com_fundacional = {m.kc for m in d.misconceptions.values() if m.is_foundational}
    assert com_diagrama == com_fundacional == {"kc_01", "kc_04", "kc_07"}


def test_kc_que_exige_diagrama_tem_ciu_com_diagrama(d):
    """RF08 precisa ser cumprível: o confronto visual tem de existir."""
    for kc_id in d.kcs:
        if d.requires_diagram(kc_id):
            assert any(c.visual for c in d.cius_of(kc_id)), kc_id


# --------------------------------------------------------------------------
# Golden dos planos de refutação
# --------------------------------------------------------------------------

def test_golden_dos_34_planos(d):
    """Qualquer mudança no grafo que altere um plano quebra aqui — de propósito.

    Para recongelar depois de uma mudança deliberada, rode:
        python -m tools.freeze_golden
    """
    esperado = json.loads(GOLDEN.read_text(encoding="utf-8"))
    obtido = {
        m.id: ["%s:%s" % r for r in socratic.full_plan(d, m.kc, m.node)]
        for m in d.misconceptions.values()
    }
    assert obtido == esperado


def test_o_plano_de_local_survives_return_tem_seis_passos(d):
    """A aresta kc_12:I2 <- B1 existe no YAML e o planner a percorre.

    Esteve em disputa enquanto o documento de grafos publicado estava
    desatualizado; o YAML sempre teve a aresta.
    """
    plano = socratic.full_plan(d, "kc_12", "I2")
    assert len(plano) == 6
    assert ("kc_12", "B1") in plano


# --------------------------------------------------------------------------
# Coerência da Q-matrix — o desfecho primário
# --------------------------------------------------------------------------

def test_toda_crenca_e_detectavel_por_alguma_ciu(d):
    assert validate.check_detectability(d) == []


def test_distrator_so_aponta_para_o_kc_ou_um_prerequisito(d):
    assert validate.check_qmatrix_coherence(d) == []


def test_targets_pertencem_ao_kc_da_ciu(d):
    for c in d.cius.values():
        for t in c.targets:
            assert t in d.kcs[c.kc].nodes, "%s: target %s fora do %s" % (c.id, t, c.kc)


def test_toda_ciu_tem_forma_de_resposta(d):
    for c in d.cius.values():
        assert c.options or c.steps_correct or c.answer or c.paths, "%s não mede nada" % c.id


def test_parsons_so_tem_permutacao_e_path_choice_so_tem_caminhos(d):
    """A distinção que a interface precisa honrar.

    `parsons` é reordenação dos mesmos passos: um widget de arrastar dá
    conta. `path_choice` são caminhos com passos distintos: renderizar
    como reordenação tornaria o distrator inatingível.
    """
    for c in d.cius.values():
        if c.type == "parsons":
            for w in c.common_wrong_orders:
                assert sorted(w.order) == sorted(c.steps_correct), c.id
            assert not c.paths, c.id
        if c.type == "path_choice":
            assert not c.common_wrong_orders, c.id
            assert sum(1 for p in c.paths if p.correct) == 1, c.id
            for p in c.paths:
                assert p.correct or p.misconception, "%s: caminho %s solto" % (c.id, p.label)


def test_prompt_de_fill_blank_tem_lacuna(d):
    for c in d.cius.values():
        if c.type == "fill_blank":
            assert "___" in c.prompt, c.id
            assert c.answer, c.id


def test_prompt_de_escolha_pergunta_alguma_coisa(d):
    """CIU de escolha sem interrogação no prompt não pede nada ao aluno.

    Não se afirma ONDE a pergunta está: a ordem varia entre itens — em
    ciu_kc09_003 a pergunta vem antes dos trechos comparados. Por isso o
    loader não separa código de enunciado (ver comentário em CIU).
    """
    for c in d.cius.values():
        if c.is_choice:
            assert "?" in c.prompt, c.id


# --------------------------------------------------------------------------
# RF10 e RF11
# --------------------------------------------------------------------------

def test_nomeacao_tardia(d):
    assert validate.check_late_naming(d) == []


def test_termo_tardio_aparece_no_no_de_conclusao(d):
    """A regra não é só proibir antes: o termo tem de existir em algum
    lugar, ou a nomeação nunca acontece."""
    for termo in d.study.late_named_terms:
        conclusoes = [
            d.node(k.id, k.conclusion_node).text for k in d.kcs.values()
            if k.conclusion_node in k.nodes
        ]
        assert any(termo in t.lower() for t in conclusoes), termo


def test_todo_kc_do_piloto_pode_ser_encerrado(d):
    """RF11: sem CIU de variação o KC fica aberto.

    Vale só para o recorte; fora dele é aviso, não bloqueio.
    """
    for kc_id in d.pilot_sequence:
        assert d.cius_of(kc_id, "variation"), "%s sem CIU de variação (RF11)" % kc_id
        assert d.cius_of(kc_id, "diagnostic"), "%s sem CIU diagnóstica" % kc_id


def test_piloto_respeita_ordem_e_cobre_os_dois_regimes(d):
    ordens = [d.kcs[k].teaching_order for k in d.pilot_sequence]
    assert ordens == sorted(ordens)
    regimes = {d.requires_diagram(k) for k in d.pilot_sequence}
    assert regimes == {True, False}


# --------------------------------------------------------------------------
# Hash do domínio (§15)
# --------------------------------------------------------------------------

def test_hash_e_estavel_e_muda_com_o_conteudo(d, tmp_path):
    assert d.hash == load().hash and d.hash.startswith("sha256:")

    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        (copia / f.name).write_bytes(f.read_bytes())
    assert load(copia).hash == d.hash

    alvo = copia / "kcs.yaml"
    alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# tocado\n", encoding="utf-8")
    assert load(copia).hash != d.hash


def test_study_nao_entra_no_hash(d, tmp_path):
    """Mudar o recorte do piloto não muda o conteúdo que o aluno viu."""
    outro = tmp_path / "study.yaml"
    outro.write_text("pilot_sequence: [kc_09]\n", encoding="utf-8")
    assert load(study_path=outro).hash == d.hash
