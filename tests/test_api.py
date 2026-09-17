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


PRIOR_C = "cursei uma disciplina com C"


def abre(client, participante="P01", arm="socratic", kcs=None):
    r = client.post("/sessions", json={
        "participant": participante, "arm": arm,
        "kc_sequence": kcs or ["kc_09"],
        "consented": True, "prior_c": PRIOR_C,
    })
    assert r.status_code == 200, r.text
    return atravessa_intro(client, r.json())


def atravessa_intro(client, j):
    """Confirma os cartões da introdução e devolve a sessão na 1ª atividade."""
    for _ in range(20):
        if j["next_action"]["kind"] != "intro":
            return j
        j = client.post("/sessions/%s/ack" % j["session_id"],
                        json={"elapsed_ms": 800}).json()
    raise AssertionError("a introdução não terminou")


def responde(client, sid, acao, domain, *, errando=None, conf="tenho certeza"):
    """Responde a CIU que a ação aponta, pela API.

    Escolhe pelo TEXTO, não pelo índice do YAML: as alternativas chegam
    embaralhadas por sessão, e o cliente manda a POSIÇÃO em que o aluno
    clicou. Um teste que mandasse o índice canônico estaria falando uma
    língua que a interface real não fala.
    """
    ciu = domain.cius[acao["ciu_id"]]
    corpo = {"ciu_id": ciu.id, "confidence": conf, "elapsed_ms": 4000}
    if ciu.is_choice:
        def escolhe(o):
            return o.misconception == errando if errando else o.correct
        alvo = next((o for o in ciu.options if escolhe(o)), ciu.options[0])
        exibidas = [x["text"] for x in acao.get("options", [])]
        corpo["option_idx"] = exibidas.index(alvo.text)
    elif ciu.type == "fill_blank":
        corpo["text"] = ciu.answer if errando is None else "sei la"
    elif ciu.type == "parsons":
        corpo["text"] = list(ciu.steps_correct)
    else:
        corpo["text"] = next(p.label for p in ciu.paths if p.correct)
    r = client.post("/sessions/%s/answer" % sid, json=corpo)
    assert r.status_code == 200, r.text
    return r.json()


def posicao(acao, domain, *, misconception=None, correta=False):
    """Em que POSIÇÃO a alternativa pedida está sendo exibida.

    As alternativas vêm embaralhadas por sessão, então nenhum teste pode
    fixar um índice: teria de ser atualizado a cada mudança de id de
    sessão, e passaria ou falharia por sorte.
    """
    ciu = domain.cius[acao["ciu_id"]]
    alvo = next(o for o in ciu.options
                if (o.correct if correta else o.misconception == misconception))
    return [x["text"] for x in acao["options"]].index(alvo.text)


def avanca_ate_o_fim(client, sid, j, domain, limite=200):
    for _ in range(limite):
        a = j["next_action"]
        if a["kind"] == "done":
            return j
        if a["kind"] == "ciu":
            j = responde(client, sid, a, domain)
        elif a["kind"] == "probe":
            j = post(client, "/sessions/%s/probe" % sid,
                     {"option_idx": 0, "elapsed_ms": 900,
                      "kc": a.get("kc"), "node": a.get("node")})
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
    from engine.loader import load
    d = load()
    # Contra o domínio carregado, não contra um número escrito à mão: o
    # número de atividades muda quando o conteúdo muda, e o que este teste
    # afirma é que o /health EXPÕE o tamanho, não qual é.
    assert j["kcs"] == len(d.kcs) and j["cius"] == len(d.cius)


def test_criar_sessao_devolve_a_primeira_acao(client):
    j = abre(client)
    assert j["session_id"] and j["arm"] == "socratic"
    assert j["next_action"]["kind"] == "ciu"
    assert "options" in j["next_action"]
    assert j["cognitive_state"] == "desconhecimento"


def test_responder_devolve_outcome_e_deteccao(client):
    from engine.loader import load
    j = abre(client)
    r = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": j["next_action"]["ciu_id"], "confidence": "tenho certeza",
        "elapsed_ms": 8000,
        "option_idx": posicao(j["next_action"], load(),
                              misconception="free_nullifies")})
    assert r.status_code == 200
    saida = r.json()
    assert saida["outcome"] == "incorrect"
    assert saida["detected"] == "free_nullifies"
    assert saida["vector"]["I1"] == "wrong"


def test_chutar_nao_reporta_crenca_detectada(client):
    """A mesma alternativa, chutada, não é evidência de sustentar a crença."""
    from engine.loader import load
    j = abre(client)
    d = load()
    ciu = d.cius[j["next_action"]["ciu_id"]]
    saida = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": ciu.id, "confidence": "chutei", "elapsed_ms": 8000,
        "option_idx": posicao(j["next_action"], d,
                              misconception="free_nullifies")}).json()
    assert saida["outcome"] == "incorrect"
    assert saida["detected"] is None
    # chutar marca AUSENTE o que a atividade mirava, e não acusa a crença
    for alvo in ciu.targets:
        assert saida["vector"][alvo] == "absent"
    assert saida["vector"]["I1"] != "wrong"


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
    from engine.loader import load
    j = abre(client)
    sid = j["session_id"]
    acao = j["next_action"]
    corpo = {"ciu_id": acao["ciu_id"], "confidence": "chutei", "elapsed_ms": 100,
             "option_idx": posicao(acao, load(), correta=True)}
    primeira = client.post("/sessions/%s/answer" % sid, json=corpo)
    assert primeira.status_code == 200, primeira.text
    r = client.post("/sessions/%s/answer" % sid, json=corpo)
    assert r.status_code == 409


def test_passo_no_momento_errado_da_409(client):
    j = abre(client)
    r = client.post("/sessions/%s/step" % j["session_id"],
                    json={"accepted": True, "elapsed_ms": 10})
    assert r.status_code == 409


def test_confianca_fora_da_escala_da_400(client):
    j = abre(client)
    r = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": j["next_action"]["ciu_id"], "confidence": "mais ou menos",
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
        elif a["kind"] == "probe":
            j = post(client, "/sessions/%s/probe" % sid,
                     {"option_idx": 0, "elapsed_ms": 900,
                      "kc": a.get("kc"), "node": a.get("node")})
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
            if a["kind"] == "probe":
                j = client.post("/sessions/%s/probe" % sid, json={
                    "option_idx": 0, "elapsed_ms": 1000,
                    "kc": a["kc"], "node": a["node"]}).json()
            elif a["kind"] in ("ask", "explain"):
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
        elif a["kind"] == "probe":
            j = post(client, "/sessions/%s/probe" % sid,
                     {"option_idx": 0, "elapsed_ms": 900,
                      "kc": a.get("kc"), "node": a.get("node")})
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


def test_reabrir_com_o_mesmo_codigo_retoma_em_vez_de_criar_outra(client):
    """RNF06 na forma em que o aluno a usa: ele digita o código, não o id."""
    from engine.loader import load
    d = load()
    primeira = abre(client, "P22")
    sid = primeira["session_id"]
    j = responde(client, sid, primeira["next_action"], d)

    # aba fechada; o aluno digita o mesmo código de novo
    segunda = abre(client, "P22")
    assert segunda["session_id"] == sid, "criou uma segunda sessão do mesmo participante"
    assert segunda["next_action"] == j["next_action"]


def test_sessao_encerrada_nao_e_retomada(client):
    """Depois de terminar, o mesmo código abre uma sessão nova — não revive
    a antiga, que já foi para a análise."""
    from engine.loader import load
    d = load()
    primeira = abre(client, "P23")
    avanca_ate_o_fim(client, primeira["session_id"], primeira, d)
    segunda = abre(client, "P23")
    assert segunda["session_id"] != primeira["session_id"]


# --------------------------------------------------------------------------
# Consentimento, estratificação e alocação — o que o §4.3 exige
# --------------------------------------------------------------------------

def test_sem_consentimento_nada_e_gravado(client):
    """O banco tem `consent_at NOT NULL` desde o §5.1. Gravar o carimbo
    porque o participante digitou um código seria afirmar consentimento
    que ninguém deu — e é o primeiro item que um comitê de ética verifica.
    """
    r = client.post("/sessions", json={
        "participant": "PSC", "arm": "socratic", "prior_c": PRIOR_C})
    assert r.status_code == 400
    assert "consent" in r.text.lower()

    conn = store_events.connect(client.app.state.db_path)
    try:
        linhas = conn.execute(
            "SELECT * FROM participants WHERE code = 'PSC'").fetchall()
        assert linhas == []
    finally:
        conn.close()


def test_experiencia_previa_e_obrigatoria_e_validada(client):
    """É a variável de estratificação do §4.3: sem ela não se mostra que
    os grupos ficaram equilibrados."""
    r = client.post("/sessions", json={
        "participant": "PEX", "arm": "socratic", "consented": True})
    assert r.status_code == 400

    r = client.post("/sessions", json={
        "participant": "PEX", "arm": "socratic", "consented": True,
        "prior_c": "sei tudo"})
    assert r.status_code == 400


def test_experiencia_previa_chega_ao_banco(client):
    abre(client, "PEV")
    conn = store_events.connect(client.app.state.db_path)
    try:
        linha = conn.execute(
            "SELECT prior_c, consent_at FROM participants WHERE code = 'PEV'"
        ).fetchone()
        assert linha["prior_c"] == PRIOR_C
        assert linha["consent_at"]
    finally:
        conn.close()


def test_braco_tem_de_ser_explicito(client):
    """A alocação é decisão do pesquisador. Um padrão silencioso alocaria
    o participante sem que ninguém tivesse decidido."""
    for arm in ("", "socratico", "A", None):
        r = client.post("/sessions", json={
            "participant": "PBR", "arm": arm, "consented": True,
            "prior_c": PRIOR_C})
        assert r.status_code in (400, 422), arm


def test_health_expoe_o_instrumento_para_a_interface(client):
    j = client.get("/health").json()
    assert j["confidence_scale"] and j["prior_c_options"] and j["consent_text"]


def test_total_ms_da_sessao_nao_e_zero(client):
    """`session_ended.total_ms` era zero fixo: o log afirmava que toda
    sessão durou nada."""
    from engine.loader import load
    d = load()
    j = abre(client, "PTM")
    sid = j["session_id"]
    avanca_ate_o_fim(client, sid, j, d)

    conn = store_events.connect(client.app.state.db_path)
    try:
        fim = store_events.read(conn, sid, types=["session_ended"])[0]
        gastos = sum(
            int(e.payload.get("elapsed_ms") or 0)
            for e in store_events.read(conn, sid)
            if e.type in ("answer_submitted", "socratic_step_answered",
                          "explanation_acknowledged", "stage_acknowledged")
        )
        assert fim.payload["total_ms"] > 0
        assert fim.payload["total_ms"] == gastos
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Ordem das alternativas
# --------------------------------------------------------------------------

def test_participantes_diferentes_veem_ordens_diferentes(client):
    """No catálogo a correta é a PRIMEIRA nas 40 CIUs de escolha. Sem
    embaralhar, quem perceber acerta tudo sem ler — e a validação da
    Q-matrix mede outra coisa."""
    ordens = set()
    for i in range(8):
        j = abre(client, "PO%d" % i, kcs=["kc_09"])
        ordens.add(tuple(o["text"] for o in j["next_action"]["options"]))
    assert len(ordens) > 1, "todas as sessões viram a mesma ordem"


def test_a_mesma_sessao_ve_sempre_a_mesma_ordem(client):
    """Se a ordem fosse sorteada a cada apresentação, na retomada o aluno
    veria outra — e o `option_idx` já gravado passaria a apontar para outra
    alternativa. O dado se corromperia sem sinal nenhum."""
    j = abre(client, "PORD", kcs=["kc_09"])
    primeira = [o["text"] for o in j["next_action"]["options"]]
    for _ in range(3):
        r = client.get("/sessions/%s" % j["session_id"]).json()
        assert [o["text"] for o in r["next_action"]["options"]] == primeira


def test_a_crenca_detectada_e_a_do_texto_escolhido(client):
    """O invariante que a tradução protege: o aluno clica numa POSIÇÃO, e o
    sistema tem de diagnosticar a crença do TEXTO que estava ali."""
    from engine.loader import load
    d = load()
    j = abre(client, "PTRAD", kcs=["kc_09"])
    acao = j["next_action"]
    ciu = d.cius[acao["ciu_id"]]

    escolhida, crenca = None, None
    for i, o in enumerate(acao["options"]):
        alvo = next(x for x in ciu.options if x.text == o["text"])
        if alvo.misconception:
            escolhida, crenca = i, alvo.misconception
            break
    assert escolhida is not None, "%s não tem distrator com crença" % ciu.id

    saida = client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": ciu.id, "confidence": "tenho certeza",
        "elapsed_ms": 1000, "option_idx": escolhida}).json()
    assert saida["detected"] == crenca


def test_o_log_guarda_a_posicao_exibida_e_o_indice_canonico(client):
    """Os dois, e são coisas diferentes: `option_idx` é o que o catálogo e a
    análise falam; `displayed_idx` permite medir viés de posição em vez de
    apenas eliminá-lo."""
    from engine.loader import load
    d = load()
    j = abre(client, "PLOG", kcs=["kc_09"])
    ciu = d.cius[j["next_action"]["ciu_id"]]
    pos = posicao(j["next_action"], d, misconception="free_nullifies")
    client.post("/sessions/%s/answer" % j["session_id"], json={
        "ciu_id": ciu.id, "confidence": "tenho certeza",
        "elapsed_ms": 1000, "option_idx": pos})

    conn = store_events.connect(client.app.state.db_path)
    try:
        ev = store_events.read(conn, j["session_id"], types=["answer_submitted"])[0]
        canonico = next(i for i, o in enumerate(ciu.options)
                        if o.misconception == "free_nullifies")
        assert ev.payload["option_idx"] == canonico
        assert ev.payload["displayed_idx"] == pos
        assert ev.payload["option_order"][pos] == canonico
    finally:
        conn.close()
