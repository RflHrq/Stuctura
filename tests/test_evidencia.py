"""Clicar em "Sim, confirmo" não é a mesma coisa que demonstrar.

O percurso ergue a cadeia premissa por premissa, e cada passo pedia do
aluno um "Sim, confirmo" (braço A) ou um "Entendi" (braço B). Os dois
gravavam `confirmed` no vetor — a mesma palavra que uma atividade acertada
grava. No log, no mapa e na Q-matrix, um clique ficava indistinguível de
conhecimento demonstrado, e numa sessão simulada isso é quatro quintos do
vetor: 231 nós aceitos contra 57 confirmados.

Agora são dois estados. `accepted` sustenta a cadeia — o fluxo da sessão é
exatamente o de antes, e estes testes afirmam isso — mas não se confunde
com `confirmed`, que exige acertar uma atividade que mira o nó.

O que esta separação NÃO faz é criar evidência onde não havia: ela só para
de chamar as duas coisas pelo mesmo nome. Transformar passos em
micro-checagens é outra decisão, com custo em telas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import model
from engine import session as S
from engine.loader import load
from store import events as store_events


@pytest.fixture(scope="module")
def d():
    return load()


def _ate_o_percurso(d, arm="socratic", kc="kc_09", crenca="free_nullifies"):
    t = S.start(d, arm, [kc])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    while t.action.kind == "ciu":
        c = d.cius[t.action.ciu_id]
        alvo = next((i for i, o in enumerate(c.options) if o.misconception == crenca),
                    None)
        if alvo is None:
            alvo = next(i for i, o in enumerate(c.options) if not o.correct)
        t = S.advance(d, t.state, S.Answer(c.id, "tenho certeza", 10, option_idx=alvo))
    while t.action.kind == "diagram":
        t = S.advance(d, t.state, S.Acknowledge(10))
    return t


# --------------------------------------------------------------------------
# Os dois estados
# --------------------------------------------------------------------------

@pytest.mark.parametrize("arm", ["socratic", "direct"])
def test_o_passo_do_percurso_grava_aceito(d, arm):
    t = _ate_o_percurso(d, arm)
    assert t.action.kind in ("ask", "explain")
    ref = (t.action.kc, t.action.node)
    t = S.advance(d, t.state, S.StepAnswer(True, 10))
    assert t.state.vector[ref] == model.ACCEPTED


def test_acertar_uma_atividade_grava_confirmado(d):
    t = S.start(d, "socratic", ["kc_11"])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    c = d.cius[t.action.ciu_id]
    idx = next(i for i, o in enumerate(c.options) if o.correct)
    t = S.advance(d, t.state, S.Answer(c.id, "tenho certeza", 10, option_idx=idx))
    alvos = [(c.kc, alvo) for alvo in c.targets]
    assert [t.state.vector[r] for r in alvos] == [model.CONFIRMED] * len(alvos)


def test_o_log_distingue_os_dois(d):
    """A diferença tem de chegar à análise, não ficar só na memória."""
    t = S.start(d, "socratic", ["kc_09"])
    estados: list[str] = []
    for _ in range(400):
        for e in t.events:
            estados.extend(u["state"] for u in e.payload.get("node_updates", ()))
        a = t.action
        if a.kind == "done":
            break
        if a.kind == "ciu":
            c = d.cius[a.ciu_id]
            if c.is_choice:
                idx = next(i for i, o in enumerate(c.options) if o.correct)
                t = S.advance(d, t.state, S.Answer(c.id, "tenho certeza", 10, option_idx=idx))
            else:
                t = S.advance(d, t.state, S.Answer(c.id, "tenho certeza", 10, text=c.answer))
        elif a.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 10))
        else:
            t = S.advance(d, t.state, S.Acknowledge(10))
    assert model.ACCEPTED in estados and model.CONFIRMED in estados


def test_o_store_aceita_o_estado_novo(d):
    assert model.ACCEPTED in store_events.NODE_STATES
    esquema = (Path(__file__).resolve().parent.parent
               / "store" / "schema.sql").read_text(encoding="utf-8")
    assert "'accepted'" in esquema, \
        "o CHECK do schema recusaria a escrita do estado novo"


# --------------------------------------------------------------------------
# O fluxo não muda
# --------------------------------------------------------------------------

def test_aceito_sustenta_a_cadeia(d):
    """Se `accepted` não sustentasse, o KC nunca fecharia e a sessão
    entraria em laço — a mudança seria de comportamento, não de rótulo."""
    assert model.sustentado(model.ACCEPTED)
    assert model.sustentado(model.CONFIRMED)
    assert not model.sustentado(model.ABSENT)
    assert not model.sustentado(model.WRONG)

    t = S.start(d, "socratic", list(d.pilot_sequence))
    for _ in range(3000):
        a = t.action
        if a.kind == "done":
            break
        if a.kind == "ciu":
            c = d.cius[a.ciu_id]
            if c.is_choice:
                idx = next(i for i, o in enumerate(c.options) if o.correct)
                t = S.advance(d, t.state, S.Answer(c.id, "acho que sei", 10, option_idx=idx))
            else:
                t = S.advance(d, t.state, S.Answer(c.id, "acho que sei", 10, text=c.answer))
        elif a.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 10))
        else:
            t = S.advance(d, t.state, S.Acknowledge(10))
    assert t.state.done
    assert all(v == S.COMPLETO for v in t.state.kc_status.values()), t.state.kc_status


def test_um_kc_so_de_aceitos_conta_como_dominado(d):
    """Decisão explícita: o critério de encerramento do KC (RF11) não mudou.
    Quem quiser exigir evidência de atividade tem o vetor para distinguir."""
    vetor = {("kc_11", n): model.ACCEPTED for n in d.kcs["kc_11"].nodes}
    assert model.cognitive_state(d, vetor, "kc_11") == model.DOMINADO
    assert model.is_complete(d, vetor, "kc_11")


def test_o_confirmado_nao_e_rebaixado_por_um_passo(d):
    """A evidência mais forte não se perde por ordem de eventos."""
    t = _ate_o_percurso(d)
    ref = (t.action.kc, t.action.node)
    forte = {**t.state.vector, ref: model.CONFIRMED}
    t2 = S.advance(d, S.replace(t.state, vector=forte), S.StepAnswer(True, 10))
    assert t2.state.vector[ref] == model.CONFIRMED
