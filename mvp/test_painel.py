"""CS-7: o painel observa a sessão sem poder atrapalhá-la.

O risco que estes testes defendem é concreto: alguém está pensando em voz
alta, e o pesquisador abre o painel para acompanhar. Se essa leitura puder
derrubar, travar ou alterar a sessão, o custo é um participante — e numa
coleta de 10 a 15 pessoas não há como repor.

A garantia não é cuidado: é ausência de caminho. O painel não importa
`mvp.app`, não conhece o dicionário de sessões e não escreve em lugar
nenhum. O que ele sabe, ele leu do log.
"""

from __future__ import annotations

import ast
import json
import pathlib

import pytest
from fastapi.testclient import TestClient

from mvp import log, motor, painel
from mvp.dominio import carrega
from mvp.motor import Resposta
from mvp.test_motor import _politica
from mvp.test_reconstrucao import percorre

D = carrega()
FONTE = pathlib.Path(painel.__file__)


@pytest.fixture(scope="module")
def d():
    return D


@pytest.fixture
def arquivo(tmp_path, monkeypatch):
    caminho = tmp_path / "eventos.jsonl"
    monkeypatch.setattr(log, "DESTINO", caminho)
    return caminho


@pytest.fixture
def cliente(arquivo):
    with TestClient(painel.app) as c:
        yield c, arquivo


# --------------------------------------------------------------------------
# CS-7: não há caminho daqui até a sessão viva
# --------------------------------------------------------------------------

def test_o_painel_nao_importa_o_servidor_da_sessao():
    """A garantia mais forte que existe: não dá para tocar no que não se
    conhece. Lida da árvore sintática, não do texto — comentário que
    mencione `mvp.app` não quebra o teste, e `import` disfarçado quebra."""
    arvore = ast.parse(FONTE.read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(a.name for a in no.names)
        elif isinstance(no, ast.ImportFrom):
            importados.add(no.module or "")
            importados.update("%s.%s" % (no.module or "", a.name)
                              for a in no.names)
    assert "mvp.app" not in importados
    assert not any(x.endswith(".app") and x.startswith("mvp") for x in importados)


def test_todas_as_rotas_do_painel_sao_de_leitura():
    for rota in painel.app.routes:
        metodos = getattr(rota, "methods", set())
        assert metodos <= {"GET", "HEAD"}, (rota.path, metodos)


def test_ler_o_painel_inteiro_nao_muda_um_byte_do_log(cliente, d):
    c, arquivo = cliente
    percorre(d, arquivo, "s1", _politica(erra_no="B2", erra_diagnostico=2, d=d))
    antes = arquivo.read_bytes()

    c.get("/saude")
    c.get("/sessoes")
    c.get("/sessoes/s1")
    c.get("/sessoes/naoexiste")

    assert arquivo.read_bytes() == antes


def test_o_painel_nao_atrapalha_uma_sessao_em_andamento(arquivo):
    """O caso real: o pesquisador fica atualizando o painel enquanto a
    pessoa responde. As duas coisas no mesmo arquivo, ao mesmo tempo."""
    from mvp import app as servidor

    servidor.sessoes.clear()
    with TestClient(servidor.app) as quem_responde, TestClient(painel.app) as quem_olha:
        sessao = quem_responde.post("/sessoes").json()["sessao"]
        quem_olha.get("/sessoes")
        r = quem_responde.post("/sessoes/%s/responder" % sessao,
                               json={"texto": "primeira frase"})
        assert r.status_code == 200
        quem_olha.get("/sessoes/%s" % sessao)
        r = quem_responde.post("/sessoes/%s/responder" % sessao, json={})
        assert r.status_code == 200
        assert r.json()["tela"]["tipo"] == "ensino"
        # E o painel enxergou a sessão que ainda está acontecendo.
        visto = quem_olha.get("/sessoes/%s" % sessao).json()
        assert visto["frases"]["inicial"] == "primeira frase"
        assert visto["encerrada"] is False


def test_o_codigo_da_sessao_nunca_vira_caminho_de_arquivo(cliente, d, tmp_path,
                                                         monkeypatch):
    """O painel lê UM arquivo, escolhido aqui dentro. Se o código da
    sessão entrasse no caminho, bastaria pedir a sessão certa para ler
    qualquer arquivo da máquina."""
    c, arquivo = cliente
    percorre(d, arquivo, "s2", _politica(d=d))
    espiao = tmp_path / "segredo.jsonl"
    espiao.write_text('{"sessao": "x", "tipo": "unidade_iniciada",'
                      ' "texto": "NAO-PODE-APARECER"}\n', encoding="utf-8")
    abertos = []
    original = log.le
    monkeypatch.setattr(log, "le",
                        lambda s=None, d=None: abertos.append(d) or original(s, d))

    for tentativa in ("../segredo", "../segredo.jsonl", str(espiao),
                      "..%2F..%2Fsegredo", "%2E%2E%2Fsegredo.jsonl"):
        r = c.get("/sessoes/" + tentativa)
        assert r.status_code != 200, tentativa
        assert "NAO-PODE-APARECER" not in r.text, tentativa

    # A prova direta: nenhuma leitura escolheu o arquivo a partir do que
    # veio do cliente. O painel abre um arquivo só, decidido no servidor.
    assert all(x is None for x in abertos), abertos


# --------------------------------------------------------------------------
# Portão G: a lista não é uma tela com o texto de todo mundo
# --------------------------------------------------------------------------

def test_a_lista_de_sessoes_nao_traz_texto_livre(cliente, d):
    """Minimização com regra concreta: as frases aparecem na tela de UMA
    sessão, nunca na lista. Uma tela com o que quarenta pessoas
    escreveram não serve a nada que este estudo precise."""
    c, arquivo = cliente
    percorre(d, arquivo, "s3", _politica(d=d))
    bruto = json.dumps(c.get("/sessoes").json(), ensure_ascii=False)
    assert "uma frase de" not in bruto, "a frase do participante vazou na lista"
    assert "s3" in bruto


def test_a_tela_de_uma_sessao_mostra_as_duas_frases(cliente, d):
    c, arquivo = cliente
    percorre(d, arquivo, "s4", _politica(d=d))
    j = c.get("/sessoes/s4").json()
    assert j["frases"]["inicial"] == "uma frase de inicio"
    assert j["frases"]["final"] == "uma frase de fim"
    assert j["pergunta"] == D.teachback


# --------------------------------------------------------------------------
# O que o painel mostra, e que é o dado do TCC
# --------------------------------------------------------------------------

def test_cada_episodio_traz_as_tres_camadas_e_os_tres_tempos(cliente, d):
    c, arquivo = cliente
    percorre(d, arquivo, "s5", _politica(d=d))
    episodios = c.get("/sessoes/s5").json()["episodios"]
    assert episodios
    primeiro = episodios[0]
    assert primeiro["correta"] is True
    assert primeiro["razao_correta"] is True
    assert primeiro["confianca"] == "tenho certeza"
    assert primeiro["estado"] == motor.CONFIRMADA
    for campo in ("ms_resposta", "ms_razao", "ms_confianca"):
        assert primeiro[campo] is not None, campo


def test_a_tabela_mostra_diagnostico_e_treino(cliente, d):
    c, arquivo = cliente
    percorre(d, arquivo, "s6", _politica(erra_no="B3", erra_diagnostico=2, d=d))
    episodios = c.get("/sessoes/s6").json()["episodios"]
    fases = {e["fase"] for e in episodios}
    assert fases == {"diagnostico", "treino"}
    treino = [e for e in episodios if e["fase"] == "treino"]
    assert all(e["streak"] is not None for e in treino)
    assert [e["ordem"] for e in episodios] == list(range(1, len(episodios) + 1))


def test_o_episodio_guarda_a_crenca_e_o_no_de_que_ela_fala(cliente, d):
    """O caso cruzado (CS-2) tem de aparecer na tabela, senão o painel
    esconde justamente o achado mais difícil de ver à mão."""
    c, arquivo = cliente
    percorre(d, arquivo, "s7", _politica(erra_no="B2", erra_diagnostico=2, d=d))
    episodios = c.get("/sessoes/s7").json()["episodios"]
    com_crenca = [e for e in episodios if e["crenca"] and e["fala_do_no"]]
    assert com_crenca
    assert any(e["estado"] == motor.CRENCA_EP for e in episodios)


def test_o_painel_desenha_os_cinco_nos_do_grafo(cliente, d):
    c, arquivo = cliente
    percorre(d, arquivo, "s8", _politica(d=d))
    nos = c.get("/sessoes/s8").json()["nos"]
    assert [n["no"] for n in nos] == list(D.ordem)
    assert all(n["estado"] != motor.DESCONHECIDO for n in nos)


def test_a_sessao_retomada_aparece_contada(cliente, d):
    c, arquivo = cliente
    percorre(d, arquivo, "s9", _politica(d=d), parar_em="razao")
    log.grava("s9", (motor.Evento("sessao_retomada", {"fase": "RAZAO"}),),
              destino=arquivo)
    linha = next(x for x in c.get("/sessoes").json()["sessoes"]
                 if x["codigo"] == "s9")
    assert linha["retomadas"] == 1
    assert linha["encerrada"] is False


def test_uma_sessao_que_nao_reexecuta_aparece_dizendo_por_que(cliente, d):
    """Esconder a sessão seria esconder dado: ela existiu, e o pesquisador
    precisa saber que aquele log não volta."""
    c, arquivo = cliente
    percorre(d, arquivo, "boa", _politica(d=d))
    t = motor.inicia(d, semente="velha")
    log.grava("velha", t.eventos, destino=arquivo)
    log.grava("velha", motor.avanca(d, t.estado, Resposta(texto="x")).eventos,
              destino=arquivo)                      # sem entrada: log antigo

    lista = {x["codigo"]: x for x in c.get("/sessoes").json()["sessoes"]}
    assert lista["boa"]["reexecutavel"] is True
    assert lista["velha"]["reexecutavel"] is False
    assert "entrada" in lista["velha"]["motivo"]
    assert c.get("/sessoes/velha").status_code == 409


# --------------------------------------------------------------------------
# O log depois de uma queda: é quando o painel mais importa
# --------------------------------------------------------------------------

def test_a_ultima_linha_pela_metade_nao_derruba_a_leitura(d, arquivo):
    """O processo morreu no meio de uma escrita. Perder o arquivo inteiro
    por causa da última linha seria o pior desfecho possível."""
    percorre(d, arquivo, "s10", _politica(d=d))
    inteiro = arquivo.read_text(encoding="utf-8")
    arquivo.write_text(inteiro + '{"ts": "2026-10-29T00:00:00.000+00:00", "ses',
                       encoding="utf-8")
    assert log.reconstroi(d, "s10", arquivo) is not None
    assert painel.detalhe("s10", arquivo)["episodios"]


def test_uma_linha_quebrada_no_meio_estoura(d, arquivo):
    """Pular em silêncio significaria reexecutar a sessão sem uma das
    respostas — e o estado sairia plausível e errado."""
    percorre(d, arquivo, "s11", _politica(d=d))
    linhas = arquivo.read_text(encoding="utf-8").splitlines()
    linhas[3] = '{"ts": "2026-'
    arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    with pytest.raises(log.LinhaCorrompida):
        log.le("s11", arquivo)


def test_o_painel_le_o_arquivo_que_o_servidor_escreve():
    """Os dois processos combinam pelo caminho do arquivo, e por nada
    mais. Se divergirem, o painel mostra uma coleta vazia e ninguém
    percebe até ser tarde."""
    from mvp import app as servidor

    assert painel.log.DESTINO == servidor.log.DESTINO
