"""O reteste: a crença refutada volta, noutra superfície.

Até aqui a sessão sabia dizer que o aluno PERCORREU uma refutação. Não
sabia dizer se ele mudou de ideia. A atividade que fechava o KC era
qualquer uma da fase de variação — no KC 07, a crença detectada podia ser
`array_is_pointer` e o fechamento perguntar sobre literais de string. O
percurso era medido; a correção, não.

Agora, havendo crença refutada, quem fecha o KC é outra atividade que
ofereça A MESMA crença. A superfície é nova por construção — é outro
item —, e a escolha do aluno tem significado direto: pegar de novo o mesmo
distrator é a refutação não ter pegado.

O evento `belief_retested` carrega esse desfecho pronto. Ele é derivável de
`answer_submitted` + `misconception_detected`, mas derivar significa cada
análise refazer a mesma junção e errar de um jeito diferente.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import selector
from engine import session as S
from engine.loader import load


@pytest.fixture(scope="module")
def d():
    return load()


def _roda(d, kc, crenca, reteste_correto=True, arm="socratic",
          confianca_reteste="tenho certeza"):
    """Erra a primeira diagnóstica com `crenca` e CERTEZA — chute não vira
    crença detectada, de propósito (§7.3) —, confirma todo o percurso e
    responde o fechamento. Devolve (transição final, eventos, ids vistos)."""
    t = S.start(d, arm, [kc])
    eventos: list = []
    vistos: list[str] = []
    errou = False
    for _ in range(600):
        eventos.extend(t.events)
        a = t.action
        if a.kind == "done":
            break
        if a.kind == "intro":
            t = S.advance(d, t.state, S.Acknowledge(10))
            continue
        if a.kind == "ciu":
            c = d.cius[a.ciu_id]
            vistos.append(c.id)
            e_reteste = errou and crenca in selector.beliefs_of(c) and c.id != vistos[0]
            if not errou and crenca in selector.beliefs_of(c):
                idx = next(i for i, o in enumerate(c.options)
                           if o.misconception == crenca)
                errou = True
            elif e_reteste and not reteste_correto:
                idx = next(i for i, o in enumerate(c.options)
                           if o.misconception == crenca)
            elif c.is_choice:
                idx = next(i for i, o in enumerate(c.options) if o.correct)
            else:
                idx = None
            conf = confianca_reteste if e_reteste else "tenho certeza"
            if idx is None:
                t = S.advance(d, t.state, S.Answer(c.id, conf, 10, text=c.answer))
            else:
                t = S.advance(d, t.state, S.Answer(c.id, conf, 10, option_idx=idx))
            continue
        if a.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 10))
            continue
        t = S.advance(d, t.state, S.Acknowledge(10))
    eventos.extend(t.events)
    return t, eventos, vistos


def _retestes(eventos):
    return [e for e in eventos if e.type == "belief_retested"]


# --------------------------------------------------------------------------
# A atividade que fecha o KC
# --------------------------------------------------------------------------

def test_o_fechamento_repergunta_a_crenca_refutada(d):
    _, eventos, _ = _roda(d, "kc_07", "array_is_pointer")
    fechamento = [e for e in eventos if e.type == "ciu_presented"
                  and e.payload["session_phase"] == S.VARIACAO]
    assert fechamento, "o KC não chegou à atividade de fechamento"
    assert fechamento[0].payload["retest_of"] == "array_is_pointer", \
        fechamento[0].payload["ciu_id"]
    # A fase do CATÁLOGO pode ser outra: o kc_07 não tem atividade de
    # variação que ofereça array_is_pointer, então quem fecha é uma
    # diagnóstica que a ofereça — a de nível mais alto ainda não usada.
    assert d.cius[fechamento[0].payload["ciu_id"]].nivel >= 2


def test_a_superficie_do_reteste_e_outra(d):
    """Reperguntar o MESMO item não mede correção: mede memória da tela."""
    _, eventos, vistos = _roda(d, "kc_09", "free_nullifies")
    apresentadas = [e.payload["ciu_id"] for e in eventos if e.type == "ciu_presented"]
    reteste = [e.payload["ciu_id"] for e in eventos
               if e.type == "ciu_presented" and e.payload.get("retest_of")]
    assert reteste, "nenhuma atividade foi marcada como reteste"
    primeira = apresentadas[0]
    assert all(r != primeira for r in reteste), \
        "o reteste repetiu a atividade em que a crença foi detectada"


def test_toda_crenca_do_piloto_tem_com_que_ser_retestada(d):
    """Não adianta a regra existir se o domínio não tem o segundo item."""
    onde: dict[str, list[str]] = {}
    for c in d.cius.values():
        for m in selector.beliefs_of(c):
            onde.setdefault(m, []).append(c.id)
    faltando = sorted(m.id for m in d.misconceptions.values()
                      if m.kc in d.pilot_sequence and len(onde.get(m.id, [])) < 2)
    assert faltando == [], "crenças do piloto sem segunda atividade: %s" % faltando


# --------------------------------------------------------------------------
# O desfecho
# --------------------------------------------------------------------------

def test_acertar_o_reteste_registra_correcao(d):
    _, eventos, _ = _roda(d, "kc_07", "array_is_pointer", reteste_correto=True)
    r = _retestes(eventos)
    assert r, "o log não registrou o reteste"
    assert r[0].payload["misconception_id"] == "array_is_pointer"
    assert r[0].payload["correct"] is True
    assert r[0].payload["still_held"] is False


def test_repetir_a_crenca_no_reteste_fica_registrado(d):
    """O caso que interessa quando a refutação não pega."""
    _, eventos, _ = _roda(d, "kc_07", "array_is_pointer", reteste_correto=False)
    r = _retestes(eventos)
    assert r, "o log não registrou o reteste"
    assert r[0].payload["still_held"] is True
    assert r[0].payload["chose"] == "array_is_pointer"


def test_o_reteste_guarda_a_confianca(d):
    """Acerto chutado não é correção, e a análise precisa poder separar."""
    _, eventos, _ = _roda(d, "kc_07", "array_is_pointer", confianca_reteste="chutei")
    r = _retestes(eventos)
    assert r and r[0].payload["confidence"] == "chutei"


def test_sem_crenca_detectada_nao_ha_reteste(d):
    """Quem não trouxe crença nenhuma fecha o KC como sempre fechou."""
    t = S.start(d, "socratic", ["kc_11"])
    eventos: list = []
    for _ in range(600):
        eventos.extend(t.events)
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
    eventos.extend(t.events)
    assert _retestes(eventos) == []
    assert all(e.payload.get("retest_of") is None
               for e in eventos if e.type == "ciu_presented")


def test_os_dois_bracos_retestam_igual(d):
    """O reteste depende da crença detectada, não do braço. Se dependesse,
    a medida de correção não seria comparável entre A e B."""
    def ids(arm):
        _, eventos, _ = _roda(d, "kc_07", "array_is_pointer", arm=arm)
        return [(e.payload["ciu_id"], e.payload.get("retest_of"))
                for e in eventos if e.type == "ciu_presented"]
    assert ids("socratic") == ids("direct")
