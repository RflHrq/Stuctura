"""Feedback em três etapas (RF17). Item 7 do §13.

O teste que mais importa é `test_os_dois_bracos_recebem_o_mesmo_feedback`.
O §8.1 lista o que é idêntico entre socrático e direto, e feedback não está
na lista — porque não existia quando a lista foi escrita. Se um braço
recebesse elaboração verbal que o outro não recebe, a variável isolada
deixaria de ser a geração ativa, e o experimento mediria duas coisas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import feedback as fb, model, session as S
from engine.loader import DomainError, load
from tests.test_session import comeca, responde


@pytest.fixture(scope="module")
def d():
    return load()


def roteiro(d, arm, kc="kc_09", crenca="free_nullifies", limite=120):
    """Roda uma sessão coletando (ação, feedback) de cada tela."""
    t = comeca(d, arm, [kc])
    passos = []
    for _ in range(limite):
        a = t.action
        passos.append((a.kind, a.kc, a.node, (a.data or {}).get("feedback")))
        if a.kind == "done":
            break
        if a.kind == "ciu":
            ciu = d.cius[a.ciu_id]
            # Quem TEM a crença a sustenta em toda atividade diagnóstica que a
            # oferece, não só na primeira — é o perfil realista. (O modelo já
            # não deixa uma resposta certa posterior apagar a crença; ver
            # tests/test_rampa.py. Este roteiro não depende disso.) Fora do
            # diagnóstico responde certo: errar na variação impediria o KC
            # de fechar.
            erro = crenca if (t.state.phase == S.DIAGNOSTICO and any(
                o.misconception == crenca for o in ciu.options)) else None
            t = responde(d, t, errando=erro)
        elif a.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 1000))
        else:
            t = S.advance(d, t.state, S.Acknowledge(500))
    return passos


# --------------------------------------------------------------------------
# As três etapas acontecem, nos pontos certos
# --------------------------------------------------------------------------

def test_as_tres_etapas_aparecem_na_sessao(d):
    etapas = [f["stage"] for _, _, _, f in roteiro(d, "socratic") if f]
    assert fb.VALIDATION in etapas
    assert fb.CONTRADICTION in etapas
    assert fb.RECONSTRUCTION in etapas


def test_validacao_vem_antes_da_contradicao(d):
    """Reconhecer antes de refutar. Invertido, o aluno defende a posição
    em vez de examiná-la — e o socrático deixa de morder."""
    etapas = [f["stage"] for _, _, _, f in roteiro(d, "socratic") if f]
    assert etapas.index(fb.VALIDATION) < etapas.index(fb.CONTRADICTION)
    assert etapas.index(fb.CONTRADICTION) < etapas.index(fb.RECONSTRUCTION)


def test_contradicao_so_no_no_que_a_crenca_nega(d):
    """Em qualquer outro passo seria ruído: a contradição só se fecha
    quando o traversal chega ao nó negado."""
    passos = roteiro(d, "socratic")
    com_contra = [(kc, no) for _, kc, no, f in passos
                  if f and f["stage"] == fb.CONTRADICTION]
    assert com_contra == [("kc_09", "I1")]
    assert d.misconceptions["free_nullifies"].negates == ("kc_09", "I1")


def test_sem_crenca_detectada_nao_ha_contradicao(d):
    """Quem só tem lacuna não tem contradição a resolver."""
    passos = roteiro(d, "socratic", crenca=None)
    assert not [f for _, _, _, f in passos
                if f and f["stage"] == fb.CONTRADICTION]


def test_validacao_muda_conforme_o_estado_cognitivo(d):
    com_crenca = fb.validation(d, {}, "kc_09", "free_nullifies")
    sem_crenca = fb.validation(d, {}, "kc_09", None)
    assert com_crenca.text != sem_crenca.text
    assert d.misconceptions["free_nullifies"].belief.rstrip(".") in com_crenca.text


# --------------------------------------------------------------------------
# O invariante crítico: simetria entre os braços
# --------------------------------------------------------------------------

def test_os_dois_bracos_recebem_o_mesmo_feedback(d):
    """Mesmas etapas, nos mesmos nós, na mesma ordem.

    Falha aqui é do mesmo tipo que falha na paridade do traversal: o
    controle passa a receber algo que o socrático não recebe, ou o
    contrário, e a diferença de aprendizado deixa de ser atribuível.
    """
    def marcas(arm):
        return [(kind, kc, no, f["stage"]) for kind, kc, no, f in roteiro(d, arm) if f]

    a, b = marcas("socratic"), marcas("direct")
    # `kind` difere (ask × explain) porque é a variável isolada; o resto não.
    assert [(kc, no, st) for _, kc, no, st in a] == \
           [(kc, no, st) for _, kc, no, st in b]


def test_validacao_e_contradicao_tem_texto_identico_nos_dois_bracos(d):
    def textos(arm, etapa):
        return [f["text"] for _, _, _, f in roteiro(d, arm)
                if f and f["stage"] == etapa]
    for etapa in (fb.VALIDATION, fb.CONTRADICTION):
        assert textos("socratic", etapa) == textos("direct", etapa), etapa


def test_so_a_reconstrucao_difere_e_so_no_verbo(d):
    """Afirmar que o aluno respondeu quando ele apenas leu seria falso —
    e o participante notaria. O conteúdo (a conclusão) é o mesmo."""
    def texto(arm):
        return next(f["text"] for _, _, _, f in roteiro(d, arm)
                    if f and f["stage"] == fb.RECONSTRUCTION)
    a, b = texto("socratic"), texto("direct")
    assert a != b
    conclusao = d.kcs["kc_09"].conclusion.strip()
    assert conclusao in a and conclusao in b


# --------------------------------------------------------------------------
# RF10 e carga
# --------------------------------------------------------------------------

def test_o_feedback_nao_vaza_o_nome_tecnico_antes_da_conclusao(d):
    termos = d.study.late_named_terms
    for kind, _, _, f in roteiro(d, "socratic"):
        if not f or kind == "conclude":
            continue
        for termo in termos:
            assert termo not in f["text"].lower(), \
                "%s vazou %r antes da conclusão" % (f["stage"], termo)


def test_marcador_desconhecido_derruba_a_carga(d, tmp_path):
    """Um `{premisa}` digitado errado apareceria CRU na tela do
    participante, no meio de uma coleta. Falha na carga, não em sessão."""
    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        (copia / f.name).write_bytes(f.read_bytes())
    (copia / "feedback.yaml").write_text(
        "schema_version: 1\nfeedback:\n  validation:\n"
        "    gap: \"antes de {premisa} seguir\"\n", encoding="utf-8")

    with pytest.raises(DomainError, match="marcador"):
        load(copia)


def test_dominio_sem_feedback_ainda_sobe(d, tmp_path):
    """RF17 é SHOULD (§2.1). Faltar os moldes não pode derrubar coleta."""
    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        if f.name != "feedback.yaml":
            (copia / f.name).write_bytes(f.read_bytes())
    sem = load(copia)
    assert sem.feedback == {}
    assert fb.validation(sem, {}, "kc_09", "free_nullifies") is None


def test_o_feedback_entra_no_hash_do_dominio(d, tmp_path):
    """É texto que o participante lê: mudá-lo no meio da coleta faz os
    participantes verem coisas diferentes (§15)."""
    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        (copia / f.name).write_bytes(f.read_bytes())
    assert load(copia).hash == d.hash

    alvo = copia / "feedback.yaml"
    alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# tocado\n", encoding="utf-8")
    assert load(copia).hash != d.hash


def test_chave_de_texto_com_chaves_nao_quebra(d):
    """O texto do domínio pode conter `{`. `str.format` explodiria; a
    substituição por regex não."""
    assert fb._preenche("valor {belief} e {desconhecido} e { literal }",
                        belief="X") == "valor X e {desconhecido} e { literal }"
