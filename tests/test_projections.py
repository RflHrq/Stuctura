"""Testes da camada store/ - log append-only e projecao (§11, RNF04).

Nenhum termo do dominio aparece aqui: os ids sao de brinquedo ("kc_x", "n1").
Se um dia este arquivo precisar nomear um conceito de C para testar a camada
store/, e porque store/ vazou dominio - e isso e bug (RNF01).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from store import events as ev
from store import projections as pr
from tools import replay


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture()
def conn(tmp_path):
    c = ev.open_db(tmp_path / "teste.db")
    yield c
    c.close()


@pytest.fixture()
def sid(conn):
    ev.add_participant(conn, "P01", "socratic", prior_c="1 semestre")
    return ev.start_session(conn, "P01", "socratic", ["kc_x"], "sha256:abc", session_id="S1")


def roteiro_socratico(conn, sid):
    """Uma sessao scriptada: diagnostico, crenca detectada, traversal, conclusao."""
    ev.append(conn, sid, "ciu_presented",
              {"ciu_id": "ciu_1", "kc": "kc_x", "targets": ["n1", "n2", "n3"], "phase": "diag"})
    ev.append(conn, sid, "answer_submitted",
              {"ciu_id": "ciu_1", "option_idx": 2, "confidence": "tenho certeza", "elapsed_ms": 8400,
               "correct": False,
               "node_updates": [{"kc": "kc_x", "node": "n3", "state": "wrong"},
                                {"kc": "kc_x", "node": "n1", "state": "absent"},
                                {"kc": "kc_x", "node": "n2", "state": "absent"}]})
    ev.append(conn, sid, "misconception_detected",
              {"misconception_id": "mc_1", "node": "n3", "kc": "kc_x"})
    for i, no in enumerate(["n1", "n2", "n3"], start=1):
        ev.append(conn, sid, "socratic_step_shown",
                  {"kc": "kc_x", "node": no, "kind": "ask", "step_idx": i, "total": 3})
        ev.append(conn, sid, "socratic_step_answered",
                  {"kc": "kc_x", "node": no, "accepted": True, "elapsed_ms": 5000 + i,
                   "node_updates": [{"kc": "kc_x", "node": no, "state": "confirmed"}]})
    ev.append(conn, sid, "kc_completed",
              {"kc": "kc_x", "elapsed_ms": 120000,
               "vector": {"n1": "confirmed", "n2": "confirmed", "n3": "confirmed"}})
    return ev.read(conn, sid)


# --------------------------------------------------------------------------
# Append-only (RF13)
# --------------------------------------------------------------------------

def test_seq_comeca_em_1_e_nao_tem_buraco(conn, sid):
    roteiro_socratico(conn, sid)
    seqs = [e.seq for e in ev.read(conn, sid)]
    assert seqs == list(range(1, len(seqs) + 1))


def test_session_started_e_o_primeiro_evento(conn, sid):
    primeiro = ev.read(conn, sid)[0]
    assert primeiro.seq == 1
    assert primeiro.type == "session_started"
    assert primeiro.payload["domain_hash"] == "sha256:abc"  # §15


def test_update_em_events_e_bloqueado(conn, sid):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("UPDATE events SET type = 'adulterado' WHERE session_id = ?", (sid,))


def test_delete_em_events_e_bloqueado(conn, sid):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("DELETE FROM events WHERE session_id = ?", (sid,))


def test_seq_duplicado_e_rejeitado(conn, sid):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO events (session_id, seq, ts, type, payload) VALUES (?,?,?,?,?)",
            (sid, 1, "2026-09-02T00:00:00Z", "session_started", "{}"),
        )


def test_append_many_e_atomico(conn, sid):
    antes = ev.last_seq(conn, sid)
    with pytest.raises(ev.EventError):
        ev.append_many(conn, sid, [
            ("regression_triggered", {"from_node": "n3", "to_node": "n2"}),
            ("regression_triggered", {"from_node": "n2"}),  # falta to_node
        ])
    assert ev.last_seq(conn, sid) == antes


# --------------------------------------------------------------------------
# Validacao na escrita
# --------------------------------------------------------------------------

def test_tipo_desconhecido_falha(conn, sid):
    with pytest.raises(ev.EventError, match="desconhecido"):
        ev.append(conn, sid, "aluno_bocejou", {})


def test_campo_obrigatorio_faltando_falha(conn, sid):
    with pytest.raises(ev.EventError, match="obrigatorio"):
        ev.append(conn, sid, "kc_completed", {"kc": "kc_x", "elapsed_ms": 1})


def test_a_escala_de_confianca_pode_ser_alinhada_ao_estudo(conn, sid):
    """A escala vem de study.yaml; o store só a valida. Trocar a escala do
    instrumento não pode exigir edição do log."""
    original = ev.CONFIDENCE_VALUES
    try:
        ev.set_confidence_scale(["baixa", "alta"])
        ev.append(conn, sid, "answer_submitted",
                  {"ciu_id": "c", "option_idx": 0, "confidence": "alta", "elapsed_ms": 1})
        with pytest.raises(ev.EventError, match="confidence"):
            ev.append(conn, sid, "answer_submitted",
                      {"ciu_id": "c", "option_idx": 0, "confidence": "chutei",
                       "elapsed_ms": 1})
    finally:
        ev.set_confidence_scale(original)


def test_confianca_fora_da_escala_falha(conn, sid):
    with pytest.raises(ev.EventError, match="confidence"):
        ev.append(conn, sid, "answer_submitted",
                  {"ciu_id": "c", "option_idx": 0, "confidence": "talvez", "elapsed_ms": 1})


def test_state_invalido_em_node_updates_falha(conn, sid):
    with pytest.raises(ev.EventError, match="state"):
        ev.append(conn, sid, "socratic_step_answered",
                  {"kc": "kc_x", "node": "n1", "accepted": True, "elapsed_ms": 1,
                   "node_updates": [{"kc": "kc_x", "node": "n1", "state": "quase"}]})


def test_arm_invalido_falha(conn):
    with pytest.raises(ev.EventError, match="arm"):
        ev.add_participant(conn, "P99", "hibrido")


# --------------------------------------------------------------------------
# Fold (RNF02: determinismo)
# --------------------------------------------------------------------------

def test_projecao_e_deterministica(conn, sid):
    eventos = roteiro_socratico(conn, sid)
    resultados = {tuple(sorted(pr.project(eventos).items())) for _ in range(100)}
    assert len(resultados) == 1


def test_ultimo_update_vence(conn, sid):
    roteiro_socratico(conn, sid)
    proj = pr.project(ev.read(conn, sid))
    # n3 entrou como wrong no seq 3 e virou confirmed no traversal.
    assert pr.vector(proj, "kc_x")["n3"] == "confirmed"
    assert proj[("kc_x", "n3")][1] > 3


def test_fold_rejeita_eventos_fora_de_ordem(conn, sid):
    eventos = roteiro_socratico(conn, sid)
    with pytest.raises(ValueError, match="fora de ordem"):
        pr.project(list(reversed(eventos)))


def test_evento_sem_node_updates_nao_altera_vetor(conn, sid):
    roteiro_socratico(conn, sid)
    antes = pr.project(ev.read(conn, sid))
    ev.append(conn, sid, "diagram_toggled",
              {"from_state": "a", "to_state": "b", "elapsed_ms": 900})
    assert pr.project(ev.read(conn, sid)) == antes


# --------------------------------------------------------------------------
# RNF04: derruba o derivado, reprojeta, compara
# --------------------------------------------------------------------------

def test_apply_event_e_rebuild_concordam(conn, sid):
    for e in roteiro_socratico(conn, sid):
        pr.apply_event(conn, e)
    ao_vivo = pr.snapshot(conn, sid)
    assert pr.rebuild(conn, sid) == ao_vivo
    assert pr.snapshot(conn, sid) == ao_vivo


def test_derrubar_node_state_e_reconstruir_da_o_mesmo_resultado(conn, sid):
    for e in roteiro_socratico(conn, sid):
        pr.apply_event(conn, e)
    antes = pr.snapshot(conn, sid)
    conn.execute("DELETE FROM node_state")
    assert pr.snapshot(conn, sid) == {}
    pr.rebuild(conn, sid)
    assert pr.snapshot(conn, sid) == antes  # igualdade exata (RNF04)


def test_rebuild_e_idempotente(conn, sid):
    roteiro_socratico(conn, sid)
    primeiro = pr.rebuild(conn, sid)
    assert pr.rebuild(conn, sid) == primeiro


def test_verify_acusa_adulteracao_do_derivado(conn, sid):
    roteiro_socratico(conn, sid)
    pr.rebuild(conn, sid)
    assert pr.verify(conn, sid) == []
    conn.execute(
        "UPDATE node_state SET state = 'wrong' WHERE session_id = ? AND node = 'n1'", (sid,)
    )
    divergencias = pr.verify(conn, sid)
    assert len(divergencias) == 1
    assert divergencias[0].node == "n1"


def test_checkpoint_kc_completed_confere_com_a_projecao(conn, sid):
    roteiro_socratico(conn, sid)
    assert pr.checkpoint_mismatches(conn, sid) == []


def test_checkpoint_acusa_motor_que_decidiu_sem_registrar(conn, sid):
    ev.append(conn, sid, "kc_completed",
              {"kc": "kc_y", "elapsed_ms": 10, "vector": {"n9": "confirmed"}})
    problemas = pr.checkpoint_mismatches(conn, sid)
    assert len(problemas) == 1 and "kc_y" in problemas[0]


def test_sessoes_nao_se_contaminam(conn, sid):
    roteiro_socratico(conn, sid)
    ev.add_participant(conn, "P02", "direct")
    outra = ev.start_session(conn, "P02", "direct", ["kc_x"], "sha256:abc", session_id="S2")
    ev.append(conn, outra, "direct_explanation_shown",
              {"kc": "kc_x", "node": "n1", "elapsed_ms": 4000,
               "node_updates": [{"kc": "kc_x", "node": "n1", "state": "confirmed"}]})
    pr.rebuild_all(conn)
    assert len(pr.snapshot(conn, outra)) == 1
    assert len(pr.snapshot(conn, sid)) == 3


# --------------------------------------------------------------------------
# Retomada (RNF06) e CLI
# --------------------------------------------------------------------------

def test_estado_sobrevive_a_reabertura_do_banco(tmp_path):
    caminho = tmp_path / "retomada.db"
    c1 = ev.open_db(caminho)
    ev.add_participant(c1, "P07", "socratic")
    s = ev.start_session(c1, "P07", "socratic", ["kc_x"], "sha256:abc", session_id="S7")
    for e in roteiro_socratico(c1, s):
        pr.apply_event(c1, e)
    esperado = pr.snapshot(c1, s)
    c1.close()

    c2 = ev.open_db(caminho)  # aba fechada, aluno volta com o mesmo codigo
    try:
        assert pr.snapshot(c2, s) == esperado
        assert pr.verify(c2, s) == []
    finally:
        c2.close()


def test_replay_verify_sai_zero_quando_consistente(tmp_path, capsys):
    caminho = tmp_path / "cli.db"
    c = ev.open_db(caminho)
    ev.add_participant(c, "P01", "socratic")
    s = ev.start_session(c, "P01", "socratic", ["kc_x"], "sha256:abc", session_id="S1")
    for e in roteiro_socratico(c, s):
        pr.apply_event(c, e)
    c.close()

    assert replay.main(["--db", str(caminho), "--verify"]) == 0
    assert "RNF04 satisfeito" in capsys.readouterr().out


def test_replay_verify_sai_um_quando_divergente(tmp_path, capsys):
    caminho = tmp_path / "cli2.db"
    c = ev.open_db(caminho)
    ev.add_participant(c, "P01", "socratic")
    s = ev.start_session(c, "P01", "socratic", ["kc_x"], "sha256:abc", session_id="S1")
    roteiro_socratico(c, s)
    c.execute(
        "INSERT INTO node_state (session_id, kc, node, state, updated_seq)"
        " VALUES (?,?,?,?,?)", (s, "kc_x", "fantasma", "confirmed", 99))
    c.close()

    assert replay.main(["--db", str(caminho), "--verify"]) == 1
    assert "NAO satisfeito" in capsys.readouterr().out
