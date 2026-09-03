"""As seis rotas do §9 e a retomada por replay (RNF06). Item 5 do §13.

O teste que mais importa aqui é `test_retomada_...`: derruba o cliente no
meio da sessão, reabre com o mesmo código e afirma que o aluno volta
exatamente onde parou. Numa coleta presencial, uma aba fechada por engano
significa um participante perdido — 6,7% da amostra por ocorrência.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api.main as main
from store import events as store_events


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Cliente com banco isolado: nunca toca o `data/structura.db` da coleta."""
    banco = tmp_path / "teste.db"
    monkeypatch.setattr(store_events, "DEFAULT_DB", banco)
    monkeypatch.setenv("STRUCTURA_EXPORT_TOKEN", "token-de-teste")
    with TestClient(main.app) as c:
        c.app.state.db_path = banco
        yield c


def abre(client, participante="P01", arm="socratic", kcs=None):
    r = client.post("/sessions", json={
        "participant": participante, "arm": arm,
        "kc_sequence": kcs or ["kc_09"],
    })
    assert r.status_code == 200, r.text
    return r.json()


def responde(client, sid, acao, domain, *, errando=None, conf="tenho certeza"):
    """Responde a CIU que a ação aponta, pela API."""
    ciu = domain.cius[acao["ciu_id"]]
    corpo = {"ciu_id": ciu.id, "confidence": conf, "elapsed_ms": 4000}
    if ciu.is_choice:
        def escolhe(o):
            return o.misconception == errando if errando else o.correct
        corpo["option_idx"] = next(
            (i for i, o in enumerate(ciu.options) if escolhe(o)), 0
        )
    elif ciu.type == "fill_blank":
        corpo["text"] = ciu.answer if errando is None else "sei la"
    elif ciu.type == "parsons":
        corpo["text"] = list(ciu.steps_correct)
    else:
        corpo["text"] = next(p.label for p in ciu.paths if p.correct)
    r = client.post("/sessions/%s/answer" % sid, json=corpo)
    assert r.status_code == 200, r.text
    return r.json()


def avanca_ate_o_fim(client, sid, j, domain, limite=200):
    for _ in range(limite):
        a = j["next_action"]
        if a["kind"] == "done":
            return j
        if a["kind"] == "ciu":
            j = responde(client, sid, a, domain)
        elif a["kind"] in ("ask", "explain"):
            r = client.post("/sessions/%s/step" % sid, json={
                "accepted": True, "elapsed_ms": 2000,
                "kc": a.get("kc"), "node": a.get("node")})
            assert r.status_code == 200, r.text
            j = r.json()
        else:
            r = client.post("/sessions/%s/ack" % sid, json={"elapsed_ms": 900})
            assert r.status_code == 200, r.text
            j = r.json()
    raise AssertionError("a sessão não terminou pela API")


# --------------------------------------------------------------------------
# Contrato do §9
# --------------------------------------------------------------------------

def test_health_expoe_o_hash_do_dominio(client):
    """§15: conferir o hash antes de cada sessão responde "viram o mesmo?"."""
    j = client.get("/health").json()
    assert j["ok"] and j["domain_hash"].startswith("sha256:")
    assert j["kcs"] == 12 and j["cius"] == 48


def test_criar_sessao_devolve_a_primeira_acao(client):
    j = abre(client)
    assert j["session_id"] and j["arm"] == "socratic"
    assert j["next_action"]["kind"] == "ciu"
    assert "options" in j["next_action"]
    assert j["cognitive_state"] == "desconhecimento"


def test_responder_devolve_outcome_e_deteccao(client):
    j = abre(client)
    r = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": "ciu_kc09_001", "confidence": "tenho certeza",
        "elapsed_ms": 8000, "option_idx": 2})
    assert r.status_code == 200
    saida = r.json()
    assert saida["outcome"] == "incorrect"
    assert saida["detected"] == "free_nullifies"
    assert saida["vector"]["I1"] == "wrong"


def test_chutar_nao_reporta_crenca_detectada(client):
    """A mesma alternativa, chutada, não é evidência de sustentar a crença."""
    j = abre(client)
    saida = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": "ciu_kc09_001", "confidence": "chutei",
        "elapsed_ms": 8000, "option_idx": 2}).json()
    assert saida["outcome"] == "incorrect"
    assert saida["detected"] is None
    assert saida["vector"]["I1"] == "absent"


def test_sessao_completa_por_http(client):
    from engine.loader import load
    d = load()
    j = abre(client)
    final = avanca_ate_o_fim(client, j["session_id"], j, d)
    assert final["done"] is True
    assert final["kc_status"]["kc_09"] == "completed"


def test_sessao_desconhecida_da_404(client):
    assert client.get("/sessions/nao-existe").status_code == 404


def test_resposta_fora_de_ordem_da_409(client):
    """Botão voltar do navegador não pode gravar evento fora de ordem."""
    j = abre(client)
    sid = j["session_id"]
    client.post("/sessions/%s/answer" % sid, json={
        "ciu_id": "ciu_kc09_001", "confidence": "chutei",
        "elapsed_ms": 100, "option_idx": 2})
    r = client.post("/sessions/%s/answer" % sid, json={
        "ciu_id": "ciu_kc09_001", "confidence": "chutei",
        "elapsed_ms": 100, "option_idx": 2})
    assert r.status_code == 409


def test_passo_no_momento_errado_da_409(client):
    j = abre(client)
    r = client.post("/sessions/%s/step" % j["session_id"],
                    json={"accepted": True, "elapsed_ms": 10})
    assert r.status_code == 409


def test_confianca_fora_da_escala_da_400(client):
    j = abre(client)
    r = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": "ciu_kc09_001", "confidence": "mais ou menos",
        "elapsed_ms": 100, "option_idx": 0})
    assert r.status_code == 400


def test_participante_nao_troca_de_braco(client):
    """A alocação é feita uma vez: trocar contaminaria a comparação."""
    abre(client, "P07", "socratic")
    r = client.post("/sessions", json={"participant": "P07", "arm": "direct"})
    assert r.status_code == 400


# --------------------------------------------------------------------------
# RNF06 — retomada
# --------------------------------------------------------------------------

def test_retomada_devolve_o_aluno_exatamente_onde_parou(client):
    from engine.loader import load
    d = load()
    j = abre(client)
    sid = j["session_id"]

    # anda até o meio de um traversal socrático
    for _ in range(40):
        a = j["next_action"]
        if a["kind"] == "ask" and a.get("step", {}).get("idx", 0) >= 3:
            break
        if a["kind"] == "ciu":
            j = responde(client, sid, a, d,
                         errando="free_nullifies" if a["ciu_id"] == "ciu_kc09_001" else None)
        elif a["kind"] in ("ask", "explain"):
            j = client.post("/sessions/%s/step" % sid, json={
                "accepted": True, "elapsed_ms": 1000,
                "kc": a.get("kc"), "node": a.get("node")}).json()
        else:
            j = client.post("/sessions/%s/ack" % sid, json={"elapsed_ms": 100}).json()

    antes = j
    assert antes["next_action"]["kind"] == "ask"

    # "o aluno fechou a aba": nada em memória, só o log
    retomada = client.get("/sessions/%s" % sid).json()

    assert retomada["phase"] == antes["phase"]
    assert retomada["kc"] == antes["kc"]
    assert retomada["vector"] == antes["vector"]
    assert retomada["next_action"] == antes["next_action"]


def test_sessao_retomada_termina_igual_a_que_nao_caiu(client):
    """A retomada não pode mudar o caminho: mesmo vetor final, mesmo status."""
    from engine.loader import load
    d = load()

    a = abre(client, "P10")
    fim_direto = avanca_ate_o_fim(client, a["session_id"], a, d)

    b = abre(client, "P11")
    sid = b["session_id"]
    j = responde(client, sid, b["next_action"], d)
    j = client.get("/sessions/%s" % sid).json()      # queda no meio
    fim_retomado = avanca_ate_o_fim(client, sid, j, d)

    assert fim_retomado["vector"] == fim_direto["vector"]
    assert fim_retomado["kc_status"] == fim_direto["kc_status"]


def test_o_estado_derivado_bate_com_o_log_depois_da_sessao(client):
    """RNF04 ponta a ponta: apaga node_state, reprojeta, compara."""
    from engine.loader import load
    from store import projections
    d = load()
    j = abre(client)
    sid = j["session_id"]
    avanca_ate_o_fim(client, sid, j, d)

    conn = store_events.connect(client.app.state.db_path)
    try:
        assert projections.verify(conn, sid) == []
        assert projections.checkpoint_mismatches(conn, sid) == []
        antes = projections.snapshot(conn, sid)
        conn.execute("DELETE FROM node_state WHERE session_id = ?", (sid,))
        projections.rebuild(conn, sid)
        assert projections.snapshot(conn, sid) == antes
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Telemetria e exportação
# --------------------------------------------------------------------------

def test_telemetria_grava_diagram_toggled(client):
    j = abre(client)
    sid = j["session_id"]
    r = client.post("/sessions/%s/telemetry" % sid, json={
        "type": "diagram_toggled",
        "payload": {"from_state": "antes", "to_state": "depois", "elapsed_ms": 1200}})
    assert r.status_code == 200

    conn = store_events.connect(client.app.state.db_path)
    try:
        eventos = store_events.read(conn, sid, types=["diagram_toggled"])
        assert len(eventos) == 1 and eventos[0].payload["to_state"] == "depois"
    finally:
        conn.close()


def test_telemetria_nao_aceita_evento_de_fluxo(client):
    """Um cliente não pode injetar `kc_completed` no log."""
    j = abre(client)
    r = client.post("/sessions/%s/telemetry" % j["session_id"], json={
        "type": "kc_completed",
        "payload": {"kc": "kc_09", "vector": {}, "elapsed_ms": 1}})
    assert r.status_code == 400


def test_export_exige_token(client):
    assert client.get("/export/events.csv").status_code == 401
    assert client.get("/export/events.csv?token=errado").status_code == 401


def test_export_devolve_o_log_em_csv(client):
    from engine.loader import load
    d = load()
    j = abre(client)
    avanca_ate_o_fim(client, j["session_id"], j, d)

    r = client.get("/export/events.csv?token=token-de-teste")
    assert r.status_code == 200
    linhas = r.text.strip().splitlines()
    assert linhas[0].startswith("session_id,participant,arm,seq,ts,type,payload")
    assert len(linhas) > 10
    assert "answer_submitted" in r.text and "kc_completed" in r.text


# --------------------------------------------------------------------------
# Paridade dos braços, agora pelo HTTP
# --------------------------------------------------------------------------

def test_os_dois_bracos_percorrem_os_mesmos_nos_pela_api(client):
    """§8: falha aqui invalida o experimento, mesmo com o motor correto."""
    from engine.loader import load
    d = load()

    def roteiro(participante, arm):
        j = abre(client, participante, arm)
        sid = j["session_id"]
        nos = []
        for _ in range(200):
            a = j["next_action"]
            if a["kind"] == "done":
                break
            if a["kind"] in ("ask", "explain"):
                nos.append((a["kc"], a["node"]))
                j = client.post("/sessions/%s/step" % sid, json={
                    "accepted": True, "elapsed_ms": 1000,
                    "kc": a["kc"], "node": a["node"]}).json()
            elif a["kind"] == "ciu":
                j = responde(client, sid, a, d,
                             errando="free_nullifies"
                             if a["ciu_id"] == "ciu_kc09_001" else None)
            else:
                j = client.post("/sessions/%s/ack" % sid, json={"elapsed_ms": 100}).json()
        return nos

    assert roteiro("PA", "socratic") == roteiro("PB", "direct")


# --------------------------------------------------------------------------
# RNF03 — resposta ≤ 200 ms por interação
# --------------------------------------------------------------------------

def test_latencia_por_interacao_respeita_o_rnf03(client):
    """A retomada por replay refaz a sessão a cada requisição. Este teste
    existe para que o custo disso continue visível: se um dia o replay
    ficar caro, é aqui que aparece, e não no laboratório."""
    import time
    from engine.loader import load
    d = load()

    j = abre(client, "PLAT", "socratic", list(d.pilot_sequence))
    sid = j["session_id"]
    tempos = []
    for _ in range(300):
        a = j["next_action"]
        if a["kind"] == "done":
            break
        t0 = time.perf_counter()
        if a["kind"] == "ciu":
            j = responde(client, sid, a, d)
        elif a["kind"] in ("ask", "explain"):
            j = client.post("/sessions/%s/step" % sid, json={
                "accepted": True, "elapsed_ms": 500,
                "kc": a["kc"], "node": a["node"]}).json()
        else:
            j = client.post("/sessions/%s/ack" % sid, json={"elapsed_ms": 100}).json()
        tempos.append((time.perf_counter() - t0) * 1000)

    assert len(tempos) > 20, "sessão curta demais para medir"
    tempos.sort()
    p95 = tempos[int(len(tempos) * 0.95)]
    assert p95 < 200, "p95 = %.1f ms, acima do RNF03" % p95
