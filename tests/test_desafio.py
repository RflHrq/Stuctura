"""O desafio: começar pela mão, subir para quem sabe, descer para quem tropeça.

Decisão do autor depois de usar o sistema: a sessão começa leve, praticamente
pegando na mão; quem vem acertando com "tenho certeza" é desafiado com
atividades mais difíceis; quem erra ou hesita volta ao degrau básico.

A regra, em `selector.nivel_minimo`: a cada `desafio_sequencia` acertos
SEGUIDOS com a confiança mais alta, o nível mínimo das diagnósticas sobe um
degrau (até o 3). Qualquer outra resposta zera a sequência. Todo KC recebe
pelo menos uma atividade.

Três perfis percorrem a sessão inteira do piloto, e cada um afirma o que a
regra promete para ele.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import selector
from engine import session as S
from engine.loader import load


@pytest.fixture(scope="module")
def d():
    return load()


def _responde(d, t, certo, conf):
    ciu = d.cius[t.action.ciu_id]
    if ciu.is_choice:
        if certo:
            idx = next(i for i, o in enumerate(ciu.options) if o.correct)
        else:
            er = [i for i, o in enumerate(ciu.options) if not o.correct]
            cc = [i for i in er if ciu.options[i].misconception]
            idx = (cc or er)[0]
        return S.advance(d, t.state, S.Answer(ciu.id, conf, 5000, option_idx=idx))
    return S.advance(d, t.state, S.Answer(ciu.id, conf, 5000,
                                          text=ciu.answer if certo else "nao sei"))


def sessao(d, politica, arm="socratic"):
    """Roda o piloto inteiro. Devolve {kc: [payload de cada ciu_presented]}
    e se a sessão terminou."""
    t = S.start(d, arm, list(d.pilot_sequence))
    apresentadas: dict[str, list[dict]] = {}
    for _ in range(3000):
        for e in t.events:
            if e.type == "ciu_presented":
                apresentadas.setdefault(e.payload["kc"], []).append(dict(e.payload))
        a = t.action
        if a.kind == "done":
            return apresentadas, True
        if a.kind == "intro":
            t = S.advance(d, t.state, S.Acknowledge(10))
        elif a.kind == "ciu":
            t = _responde(d, t, *politica(d, t))
        elif a.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 10))
        else:
            t = S.advance(d, t.state, S.Acknowledge(10))
    return apresentadas, False


def diagnosticas(apresentadas, kc):
    return [p for p in apresentadas.get(kc, []) if p["phase"] == "diagnostic"]


def _quantas(d, kc):
    """Quantas atividades um KC apresenta a quem não é desafiado.

    O pool do KC é maior do que o teto do estudo: o teto existe para o
    tempo da sessão, e sobra atividade de propósito, para o seletor ter
    de onde escolher a que cobre crença ainda não perguntada.
    """
    return min(d.study.max_diagnostics_per_kc, len(d.cius_of(kc, "diagnostic")))


FORTE = lambda d, t: (True, d.study.certain)
HESITANTE = lambda d, t: (True, "acho que sei")


# --------------------------------------------------------------------------
# A regra
# --------------------------------------------------------------------------

def test_o_piso_sobe_a_cada_passo_e_para_no_3(d):
    passo = d.study.desafio_sequencia
    assert passo > 0
    assert selector.nivel_minimo(d, 0) == 1
    assert selector.nivel_minimo(d, passo - 1) == 1
    assert selector.nivel_minimo(d, passo) == 2
    assert selector.nivel_minimo(d, 2 * passo) == 3
    assert selector.nivel_minimo(d, 50 * passo) == 3


def test_desligado_o_piso_fica_no_1(d):
    sem = replace(d, study=replace(d.study, desafio_sequencia=0))
    assert selector.nivel_minimo(sem, 99) == 1


def test_so_acerto_com_a_confianca_mais_alta_soma(d):
    t = S.start(d, "socratic", ["kc_07"])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    t = _responde(d, t, True, d.study.certain)
    assert t.state.sequencia_certa == 1
    t = _responde(d, t, True, "acho que sei")
    assert t.state.sequencia_certa == 0, "acerto hesitante tem de zerar"


def test_erro_zera_a_sequencia(d):
    t = S.start(d, "socratic", ["kc_07"])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    t = _responde(d, t, True, d.study.certain)
    t = _responde(d, t, False, d.study.certain)
    assert t.state.sequencia_certa == 0


# --------------------------------------------------------------------------
# Os três perfis
# --------------------------------------------------------------------------

def test_todo_mundo_comeca_pelo_nivel_1(d):
    for politica in (FORTE, HESITANTE):
        apresentadas, _ = sessao(d, politica)
        primeiro_kc = d.pilot_sequence[0]
        assert diagnosticas(apresentadas, primeiro_kc)[0]["nivel"] == 1


def test_quem_acerta_com_certeza_e_desafiado(d):
    apresentadas, terminou = sessao(d, FORTE)
    assert terminou
    # depois do primeiro KC ele já vem com sequência: pula o nível 1
    for kc in d.pilot_sequence[1:]:
        diag = diagnosticas(apresentadas, kc)
        assert diag, "%s ficou sem atividade diagnóstica" % kc
        assert all(p["nivel"] >= 2 for p in diag), \
            "%s apresentou nível 1 a quem vinha acertando com certeza" % kc


def test_quem_hesita_ve_todos_os_degraus(d):
    """Acertar com "acho que sei" não sobe o piso: é levado pela mão até o fim."""
    apresentadas, terminou = sessao(d, HESITANTE)
    assert terminou
    for kc in d.pilot_sequence:
        diag = diagnosticas(apresentadas, kc)
        assert [p["ciu_id"] for p in diag] and diag[0]["nivel"] == 1, kc
        assert len(diag) == _quantas(d, kc), \
            "%s pulou atividade de quem não acertou com certeza" % kc
        assert all(p["nivel_minimo"] == 1 for p in diag)


def test_quem_tropeca_volta_ao_degrau_basico(d):
    """Chega desafiado a um KC, erra com certeza, e a atividade básica que
    tinha sido pulada é a próxima."""
    kc_alvo = d.pilot_sequence[1]
    ja = set()

    def tropeca(d, t):
        c = d.cius[t.action.ciu_id]
        if c.kc == kc_alvo and kc_alvo not in ja and t.state.phase == S.DIAGNOSTICO:
            ja.add(kc_alvo)
            return (False, d.study.certain)
        return (True, d.study.certain)

    apresentadas, terminou = sessao(d, tropeca)
    assert terminou
    diag = diagnosticas(apresentadas, kc_alvo)
    assert diag[0]["nivel"] >= 2, "o perfil devia chegar desafiado a %s" % kc_alvo
    assert diag[1]["nivel_minimo"] == 1, "o erro não devolveu o piso ao nível 1"
    assert diag[1]["nivel"] == 1, "depois do erro, veio %s e não a básica" % diag[1]["ciu_id"]


def test_todo_kc_recebe_ao_menos_uma_diagnostica_mesmo_no_piso_mais_alto(d):
    apresentadas, _ = sessao(d, FORTE)
    for kc in d.pilot_sequence:
        assert len(diagnosticas(apresentadas, kc)) >= 1, kc


# --------------------------------------------------------------------------
# Garantias do desenho do estudo
# --------------------------------------------------------------------------

def test_os_dois_bracos_sao_desafiados_igual(d):
    """O desafio depende só das respostas, que vêm antes de os braços
    divergirem. Mesmas respostas, mesmas atividades."""
    a, _ = sessao(d, FORTE, "socratic")
    b, _ = sessao(d, FORTE, "direct")
    ids = lambda ap: {kc: [p["ciu_id"] for p in v] for kc, v in ap.items()}
    assert ids(a) == ids(b)


def test_desligado_todos_veem_todas_as_atividades(d):
    sem = replace(d, study=replace(d.study, desafio_sequencia=0))
    apresentadas, terminou = sessao(sem, FORTE)
    assert terminou
    for kc in sem.pilot_sequence:
        assert len(diagnosticas(apresentadas, kc)) == _quantas(sem, kc)


def test_o_log_diz_por_que_cada_atividade_foi_escolhida(d):
    apresentadas, _ = sessao(d, FORTE)
    for v in apresentadas.values():
        for p in v:
            assert {"nivel", "nivel_minimo", "sequencia_certa"} <= set(p)
            assert p["nivel_minimo"] == selector.nivel_minimo(d, p["sequencia_certa"])
