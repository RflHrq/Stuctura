"""A exportação das sessões da trilha para análise.

O que estes testes guardam:

  - as três tabelas saem, uma linha por sessão, por premissa e por
    resposta, e nada da sessão fica de fora;
  - o participante sai pelo código com que entrou, e nenhuma coluna é
    identificador direto;
  - a situação diagnosticada na abertura, o trabalho feito e o resultado
    de cada premissa saem lado a lado, que é a unidade de análise do
    estudo (Apêndice A da monografia);
  - a sessão cancelada sai marcada, e não misturada com as outras;
  - o destino que o git não ignora é recusado, antes de escrever;
  - a exportação lê só o registro: não importa o motor da trilha.

As sessões daqui são de alunos simulados, em `tmp_path`.
"""

from __future__ import annotations

import csv
import dataclasses
import json
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import trilha_alunos  # noqa: E402

from mvp import exporta, exporta_trilha, trilha, trilha_app, trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402


def _escadas(topico):
    d = carrega(topico=topico)
    return d, trilha_escada.le(
        RAIZ / "dominio" / ("escada_%s.yaml" % topico.replace("_", "")), d)


def _sessao(pasta, topico, codigo, persona, ate_o_fim=True, cancela=False):
    """Uma sessão de aluno simulado pelo HTTP, gravada em pasta/trilha/."""
    d, esc = _escadas(topico)
    cliente = TestClient(trilha_app.cria_app(
        d, esc, pasta / "trilha" / ("%s.jsonl" % topico)))
    j = cliente.post("/sessoes", json={"codigo": codigo}).json()
    t = trilha.inicia(d, esc, semente=codigo)

    def manda(entrada):
        nonlocal j, t
        corpo = {k: v for k, v in dataclasses.asdict(entrada).items()
                 if k != "passo"}
        corpo["pecas"] = list(corpo["pecas"])
        corpo["passo"] = j["passo"]
        r = cliente.post("/sessoes/%s/agir" % codigo, json=corpo)
        assert r.status_code == 200, r.text
        j = r.json()
        t = trilha.avanca(d, esc, t.estado,
                          dataclasses.replace(entrada, passo=t.estado.n))

    manda(trilha.Entrada(acao="comecar", ritmo="completo"))
    passos = 0
    while t.tela.tipo != "mapa":
        if not ate_o_fim and passos == 6:
            break
        manda(trilha_alunos.responde(d, esc, t.tela, persona, t.estado))
        passos += 1
    if cancela:
        assert cliente.post("/sessoes/%s/cancela" % codigo).status_code == 200


def _linhas(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _registro(pasta, topico):
    with open(pasta / "trilha" / ("%s.jsonl" % topico), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


@pytest.fixture(scope="module")
def coleta(tmp_path_factory):
    """Três participantes: um que sustenta concepções no kc_07, um que sabe
    o kc_00 e um que desiste do kc_00 no meio."""
    pasta = tmp_path_factory.mktemp("coleta")
    _sessao(pasta, "kc_07", "P01", "crente_aprende")
    _sessao(pasta, "kc_00", "P02", "sabe")
    _sessao(pasta, "kc_00", "P03", "nao_sabe_aprende", ate_o_fim=False,
            cancela=True)
    saida = tmp_path_factory.mktemp("analise")
    relatorio = exporta_trilha.exporta(pasta, saida)
    return pasta, saida, relatorio


def test_as_tres_tabelas_saem(coleta):
    _, saida, r = coleta
    for nome in exporta_trilha.TABELAS:
        assert (saida / nome).exists(), nome
        assert r[nome] > 0, nome
    assert r["sessoes"] == 3
    assert r["ilegiveis"] == 0


def test_uma_linha_por_sessao_com_o_codigo_do_participante(coleta):
    _, saida, _ = coleta
    linhas = {(l["participante"], l["topico"]): l
              for l in _linhas(saida / "sessoes.csv")}
    assert set(linhas) == {("P01", "kc_07"), ("P02", "kc_00"), ("P03", "kc_00")}
    assert linhas[("P01", "kc_07")]["encerrada"] == "sim"
    assert linhas[("P01", "kc_07")]["n_premissas"] == "7"
    assert linhas[("P01", "kc_07")]["n_fechadas"] == "7"
    assert linhas[("P02", "kc_00")]["encerrada"] == "sim"


def test_a_sessao_cancelada_sai_marcada(coleta):
    _, saida, _ = coleta
    linhas = {l["participante"]: l for l in _linhas(saida / "sessoes.csv")}
    assert linhas["P03"]["cancelada"] == "sim"
    assert linhas["P03"]["encerrada"] == "não"
    assert linhas["P01"]["cancelada"] == "não"


def test_cada_resposta_do_registro_vira_uma_linha(coleta):
    pasta, saida, _ = coleta
    respostas = _linhas(saida / "respostas.csv")
    for topico in ("kc_00", "kc_07"):
        ev = _registro(pasta, topico)
        esperado = sum(e["tipo"] in exporta_trilha.RESPOSTAS for e in ev)
        assert esperado > 0
        assert sum(r["topico"] == topico for r in respostas) == esperado


def test_a_resposta_traz_razao_certeza_e_crenca(coleta):
    _, saida, _ = coleta
    aberturas = [r for r in _linhas(saida / "respostas.csv")
                 if r["participante"] == "P01" and r["papel"] == "abertura"]
    assert len(aberturas) == 7
    for r in aberturas:
        assert r["tela"] == "pergunta"
        assert r["confianca"] == "tenho certeza"
        assert r["confianca_rank"] == "3"
        assert r["correta"] == "não"
        assert r["crenca"], r
        assert r["situacao"] == "crenca", r


def test_a_previsao_diz_se_seguiu_a_crenca(coleta):
    _, saida, _ = coleta
    previsoes = [r for r in _linhas(saida / "respostas.csv")
                 if r["participante"] == "P01" and r["tela"] == "previsao"]
    assert previsoes
    assert all(r["como_a_crenca"] == "sim" for r in previsoes)


def test_uma_linha_por_premissa_com_diagnostico_trabalho_e_resultado(coleta):
    _, saida, _ = coleta
    premissas = [p for p in _linhas(saida / "premissas.csv")
                 if p["participante"] == "P01"]
    assert len(premissas) == 7
    b1 = next(p for p in premissas if p["premissa"] == "B1")
    assert b1["situacao_na_abertura"] == "crenca"
    assert b1["trabalho"] == "crenca"
    assert b1["crenca"]
    assert b1["previsao_como_a_crenca"] == "sim"
    assert b1["resultado"] == "corrigiu"
    sabe = [p for p in _linhas(saida / "premissas.csv")
            if p["participante"] == "P02"]
    assert len(sabe) == 5
    assert {p["resultado"] for p in sabe} == {"ja_sabia"}


def test_nenhuma_coluna_e_identificador_direto():
    proibidas = ("nome", "matricula", "matrícula", "email", "e-mail", "cpf",
                 "telefone")
    for nome, colunas in exporta_trilha.COLUNAS.items():
        for c in colunas:
            assert not any(p in c.lower() for p in proibidas), (nome, c)


def test_destino_versionado_e_recusado(coleta, tmp_path):
    pasta, _, _ = coleta
    dentro = RAIZ / "exportacao-de-teste-que-nao-pode-existir"
    with pytest.raises(exporta.DestinoVersionado):
        exporta_trilha.exporta(pasta, dentro)
    assert not dentro.exists()


def test_a_exportacao_nao_importa_o_motor():
    fonte = (RAIZ / "exporta_trilha.py").read_text(encoding="utf-8")
    imports = [l for l in fonte.splitlines()
               if l.startswith(("import ", "from "))]
    assert imports, "não achei as linhas de import"
    for linha in imports:
        for proibido in ("trilha_app", "trilha_log", "trilha_escada",
                         "motor", "mvp.trilha", "mvp import trilha"):
            assert proibido not in linha, linha


def test_pasta_sem_sessoes_da_tabelas_vazias(tmp_path):
    vazia = tmp_path / "vazia"
    (vazia / "trilha").mkdir(parents=True)
    r = exporta_trilha.exporta(vazia, tmp_path / "saida")
    assert r["sessoes"] == 0
    for nome in exporta_trilha.TABELAS:
        assert _linhas(tmp_path / "saida" / nome) == []


def test_o_comando_roda(coleta, tmp_path, capsys):
    pasta, _, _ = coleta
    assert exporta_trilha.main(["--pasta", str(pasta),
                                "--out", str(tmp_path / "cli")]) == 0
    saida = capsys.readouterr().out
    assert "3 sessões" in saida
    assert (tmp_path / "cli" / "respostas.csv").exists()
