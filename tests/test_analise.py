"""As ferramentas de análise e o simulador.

Duas coisas aqui têm consequência fora da tela:

1. O simulador NÃO pode escrever no banco do piloto. Um participante
   simulado no meio da coleta contamina o export do §12, e o erro só
   apareceria na análise — depois de a coleta ter acabado.

2. Um passo de traversal pertence ao KC DA SESSÃO, não ao KC do nó. O
   suporte atravessa KCs: percorrer o kc_09 pergunta nós do kc_04, kc_05 e
   kc_06. Atribuir esses passos aos KCs de origem inventaria KCs que a
   sessão nunca percorreu, e o percurso mostraria seis KCs onde houve três.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.loader import load
from store import events as store_events
from tools import percurso as P
from tools import simular


@pytest.fixture(scope="module")
def d():
    return load()


@pytest.fixture(scope="module")
def banco(d, tmp_path_factory):
    """Uma sessão de verdade, escrita pelo caminho normal."""
    caminho = tmp_path_factory.mktemp("analise") / "sim.db"
    store_events.set_confidence_scale(d.study.confidence_scale)
    conn = store_events.open_db(caminho)
    sid = simular.uma_sessao(conn, d, "SIM01", "socratic", "convicto",
                             random.Random(1))
    yield conn, sid
    conn.close()


# --------------------------------------------------------------------------
# 1. O simulador não encosta no banco do piloto
# --------------------------------------------------------------------------

def test_simulador_recusa_o_banco_do_piloto(tmp_path):
    alvo = tmp_path / "structura.db"
    assert simular.main(["--db", str(alvo), "--n", "1"]) == 1
    assert not alvo.exists(), "recusou e mesmo assim criou o arquivo"


def test_simulador_aceita_um_banco_qualquer(tmp_path):
    alvo = tmp_path / "simulado.db"
    assert simular.main(["--db", str(alvo), "--n", "1"]) == 0
    assert alvo.exists()


# --------------------------------------------------------------------------
# 2. A reconstrução do percurso
# --------------------------------------------------------------------------

def test_o_percurso_tem_os_kcs_da_sessao_e_nao_os_dos_nos(d, banco):
    """O erro que este teste pega: o kc_09 puxa nós de kc_04, kc_05 e kc_06,
    e atribuir esses passos aos KCs de origem faria o percurso mostrar seis
    KCs onde a sessão percorreu três."""
    conn, sid = banco
    pc = P.percurso(conn, d, sid)
    vistos = [b["kc"] for b in pc["kcs"]]
    assert vistos == list(d.pilot_sequence), vistos


def test_os_passos_em_nos_estrangeiros_ficam_no_kc_hospedeiro(d, banco):
    """E continuam identificáveis: a visita guarda a referência completa."""
    conn, sid = banco
    pc = P.percurso(conn, d, sid)
    bloco = [b for b in pc["kcs"] if b["kc"] == "kc_09"][0]
    fora = [v for v in bloco["visitas"] if not v["node"].startswith("kc_09:")]
    assert fora, "kc_09 percorre nós de outros KCs; nenhum apareceu"
    for v in fora:
        kc, node = v["node"].split(":")
        assert kc != "kc_09"
        d.node(kc, node)        # existe mesmo, e é referenciável


def test_o_percurso_so_le_a_fonte(d, banco):
    """`node_state` é projeção descartável (§4). Apagá-la não pode mudar o
    que a análise mostra — se mudasse, a reconstrução deixaria de valer
    como prova."""
    conn, sid = banco
    antes = P.percurso(conn, d, sid)
    conn.execute("DELETE FROM node_state WHERE session_id = ?", (sid,))
    depois = P.percurso(conn, d, sid)
    assert antes == depois


def test_o_estado_cognitivo_vem_da_mesma_funcao_do_motor(d, banco):
    """Não pode haver uma segunda regra de leitura escrita na ferramenta."""
    from engine import model

    conn, sid = banco
    pc = P.percurso(conn, d, sid)
    for b in pc["kcs"]:
        vetor = {(b["kc"], n): e for n, e in b["vetor"].items()}
        assert b["estado"] == model.cognitive_state(d, vetor, b["kc"])
        assert b["estado"] in (model.DESCONHECIMENTO, model.LACUNA,
                               model.MISCONCEPTION, model.DOMINADO)


def test_a_ordem_das_visitas_e_a_ordem_do_log(d, banco):
    """`seq` é 1..n sem buraco e a tabela é append-only: a ordem do log É a
    ordem em que aconteceu, e não há o que reordenar."""
    conn, sid = banco
    pc = P.percurso(conn, d, sid)
    for b in pc["kcs"]:
        seqs = [v["seq"] for v in b["visitas"]]
        assert seqs == sorted(seqs)


def test_a_pagina_se_recusa_a_sair_vazia(d, tmp_path):
    """Uma página de análise sem sessão nenhuma parece quebrada. Melhor
    dizer o que fazer."""
    vazio = tmp_path / "vazio.db"
    store_events.open_db(vazio).close()
    with pytest.raises(SystemExit, match="tools.simular"):
        P.pagina(str(vazio))


def test_toda_sessao_simulada_e_marcada(d, banco):
    conn, _ = banco
    dados = P.dados(conn, d)
    assert dados["sessoes"]
    for s in dados["sessoes"]:
        assert s["simulado"] is True
        assert s["code"].startswith("SIM")
