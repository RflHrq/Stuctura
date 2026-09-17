"""O KC que fica em aberto fecha com a frase certa.

Havia três saídas por desistência — três recusas no mesmo nó, limite de
rodadas de correção, e domínio sem atividade de variação — e as três
pulavam direto para o KC seguinte. Quem travasse saía do tópico com a
crença com que entrou, sem nunca ler o que a cadeia sustenta. Num estudo
com alunos de verdade isso é o pior desfecho possível: a pessoa doou 40
minutos e recebeu a confirmação da própria confusão.

Agora as três passam por `_fecha_em_aberto`: uma tela com a conclusão do
KC, e, se havia crença detectada, as duas frases lado a lado. O que a tela
NÃO faz é revelar o nome técnico — nomear é o fecho de quem construiu
(RF10) — nem dizer "você acabou de construir isto".

O evento `kc_incomplete` continua saindo, com o motivo: a análise não perde
a diferença entre concluir e receber.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import feedback as fb
from engine import session as S
from engine.loader import load


@pytest.fixture(scope="module")
def d():
    return load()


def _ate_o_primeiro_passo(d, kc="kc_07", crenca="array_is_pointer"):
    """Erra com certeza até a correção começar, e devolve a transição."""
    t = S.start(d, "socratic", [kc])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    while t.action.kind == "ciu":
        c = d.cius[t.action.ciu_id]
        alvo = next((i for i, o in enumerate(c.options)
                     if o.misconception == crenca), None)
        if alvo is None:
            alvo = next(i for i, o in enumerate(c.options) if not o.correct)
        t = S.advance(d, t.state, S.Answer(c.id, "tenho certeza", 10, option_idx=alvo))
    return t


def _recusa_ate_fechar(d, t, limite=40):
    """Recusa todo passo. Devolve (transição, eventos acumulados)."""
    eventos = []
    for _ in range(limite):
        eventos.extend(t.events)
        if t.action.kind in ("conclude", "done"):
            return t, eventos
        if t.action.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(False, 10))
        elif t.action.kind == "diagram":
            t = S.advance(d, t.state, S.Acknowledge(10))
        else:
            break
    raise AssertionError("a sessão não fechou o KC depois de %d recusas" % limite)


# --------------------------------------------------------------------------
# A tela existe
# --------------------------------------------------------------------------

def test_quem_recusa_tres_vezes_recebe_a_conclusao(d):
    t = _ate_o_primeiro_passo(d)
    t, eventos = _recusa_ate_fechar(d, t)

    assert t.action.kind == "conclude", t.action.kind
    j = t.action.as_json()
    assert j["incomplete"] is True
    assert j["conclusion_text"], "a tela de fechamento veio sem a conclusão"
    assert d.kcs["kc_07"].conclusion[:40] in j["conclusion_text"]


def test_o_fechamento_nomeia_a_crenca_que_ficou_de_pe(d):
    t = _ate_o_primeiro_passo(d)
    t, _ = _recusa_ate_fechar(d, t)
    texto = (t.action.as_json().get("feedback") or {}).get("text", "")
    assert texto, "o fechamento veio sem feedback"
    crenca = d.misconceptions["array_is_pointer"].belief.rstrip(".")
    assert crenca[:30] in texto, texto


def test_o_fechamento_nao_revela_o_nome_tecnico(d):
    """RF10: quem não construiu não recebe o termo. É o que separa a
    nomeação tardia de um glossário no fim da tela."""
    t = _ate_o_primeiro_passo(d, kc="kc_09", crenca="free_nullifies")
    t, _ = _recusa_ate_fechar(d, t)
    j = t.action.as_json()
    assert j.get("incomplete") is True
    assert "technical_name" not in j, j.get("technical_name")
    termo = d.study.reveal_names.get("kc_09", "")
    assert termo and termo.lower() not in j["conclusion_text"].lower()


def test_o_evento_kc_incomplete_continua_saindo_com_motivo(d):
    t = _ate_o_primeiro_passo(d)
    t, eventos = _recusa_ate_fechar(d, t)
    incompletos = [e for e in eventos if e.type == "kc_incomplete"]
    assert len(incompletos) == 1, [e.type for e in eventos]
    assert incompletos[0].payload["reason"] == "tentativas no mesmo no"
    assert incompletos[0].payload["node"], "o log não diz em que nó travou"


def test_depois_do_fechamento_a_sessao_segue(d):
    """A tela é um passo a mais, não um beco: confirmar leva ao próximo KC."""
    t = S.start(d, "socratic", ["kc_07", "kc_11"])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    while t.action.kind == "ciu":
        c = d.cius[t.action.ciu_id]
        idx = next((i for i, o in enumerate(c.options)
                    if o.misconception == "array_is_pointer"),
                   next(i for i, o in enumerate(c.options) if not o.correct))
        t = S.advance(d, t.state, S.Answer(c.id, "tenho certeza", 10, option_idx=idx))
    t, _ = _recusa_ate_fechar(d, t)
    assert t.state.phase == S.FECHAMENTO
    assert t.state.kc_status["kc_07"] == S.EM_PROGRESSO

    t = S.advance(d, t.state, S.Acknowledge(10))
    assert t.state.kc == "kc_11", t.state.kc
    assert any(e.type == "stage_acknowledged"
               and e.payload["stage"] == "closure" for e in t.events)


def test_o_fechamento_tambem_vale_sem_crenca(d):
    """Sem crença detectada o texto é outro: não há o que contrastar."""
    f = fb.closure(d, "kc_11", None)
    assert f and f.stage == fb.CLOSURE
    com = fb.closure(d, "kc_11", "ptr_arith_is_bytes")
    assert com and com.text != f.text
    assert d.misconceptions["ptr_arith_is_bytes"].belief.rstrip(".")[:30] in com.text


def test_o_fechamento_nao_repete_a_conclusao(d):
    """A conclusão já está no quadro logo acima; repeti-la na prosa fazia o
    participante ler a mesma frase duas vezes na mesma tela."""
    for crenca in (None, "ptr_arith_is_bytes"):
        f = fb.closure(d, "kc_11", crenca)
        assert f and d.kcs["kc_11"].conclusion[:30] not in f.text, f.text


# --------------------------------------------------------------------------
# A guarda pega
# --------------------------------------------------------------------------

def test_sem_o_molde_a_sessao_nao_quebra(d, tmp_path):
    """Molde ausente não pode derrubar uma coleta: a tela vai sem o texto
    de fechamento, e a conclusão continua aparecendo."""
    destino = tmp_path / "dom"
    destino.mkdir()
    for f in d.source.glob("*.yaml"):
        (destino / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    alvo = destino / "feedback.yaml"
    texto = alvo.read_text(encoding="utf-8")
    ini = texto.index("  closure:")
    fim = texto.index("# ---", ini)
    alvo.write_text(texto[:ini] + texto[fim:], encoding="utf-8")

    sem = load(destino)
    assert fb.closure(sem, "kc_07", "array_is_pointer") is None
    t = _ate_o_primeiro_passo(sem)
    t, _ = _recusa_ate_fechar(sem, t)
    assert t.action.kind == "conclude"
    assert t.action.as_json()["conclusion_text"]
