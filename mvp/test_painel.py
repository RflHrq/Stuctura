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
    # Três desde a T12: o reteste do fim é uma linha da tabela como as
    # outras, e tem de chegar ao painel junto com elas.
    assert fases == {"diagnostico", "treino", "reteste"}
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


def test_a_linha_do_reteste_aparece_marcada_na_tabela(cliente, d):
    """A terceira condição do critério não pode sair com cara de
    diagnóstico qualquer: é a linha que o TCC vai ler primeiro."""
    from mvp.test_reteste import _erra_em

    c, arquivo = cliente
    percorre(d, arquivo, "r1", _erra_em(d, {"B3"}))
    episodios = c.get("/sessoes/r1").json()["episodios"]
    reteste = [e for e in episodios if e["fase"] == "reteste"]
    assert len(reteste) == 1
    assert reteste[0]["voltou"] is False
    assert reteste[0]["superficie_nova"] in (True, False)
    assert reteste[0] is episodios[-1] or reteste[0]["ordem"] == len(episodios)


def test_o_painel_mostra_quantas_crencas_ficaram_sem_reteste(cliente, d):
    """A terceira condição do critério que esta sessão NÃO conseguiu
    medir. Um reteste que não aconteceu tem de aparecer, não sumir."""
    from mvp.test_motor import _politica as pol

    c, arquivo = cliente
    percorre(d, arquivo, "r2", pol(erra_no="B3", erra_diagnostico=2,
                                   erra_treino=9, d=d))
    j = c.get("/sessoes/r2").json()
    assert j["refutadas"] == 1
    assert j["retestadas"] == 0
    assert j["sem_item"] == 1


# --------------------------------------------------------------------------
# R2: a lista não reexecuta (P1-B da revisão do ciclo 1)
# --------------------------------------------------------------------------

def test_a_lista_nao_reexecuta_nenhuma_sessao(cliente, d, monkeypatch):
    """A prova direta, e não uma medida de tempo que varia de máquina.

    Com `reconstroi` sabotado para estourar, a lista continua
    respondendo — porque não chama. A tela pede esta rota de três em três
    segundos, no mesmo computador que atende quem está respondendo.
    """
    c, arquivo = cliente
    percorre(d, arquivo, "p1", _politica(d=d))
    percorre(d, arquivo, "p2", _politica(erra_no="B2", erra_diagnostico=2, d=d))

    def explode(*_a, **_k):
        raise AssertionError("a lista reexecutou uma sessão")

    monkeypatch.setattr(log, "reconstroi", explode)
    j = c.get("/sessoes").json()
    assert {x["codigo"] for x in j["sessoes"]} == {"p1", "p2"}
    assert all(x["reexecutavel"] for x in j["sessoes"])


def test_a_lista_le_o_arquivo_uma_vez_so(cliente, d, monkeypatch):
    """Antes eram 1 + N leituras completas: uma para agrupar, e mais uma
    dentro de cada reconstrução."""
    c, arquivo = cliente
    for codigo in ("a", "b", "c"):
        percorre(d, arquivo, codigo, _politica(d=d))

    leituras = []
    estrita, tolerante = log.le, log.le_tolerante
    # As DUAS portas de leitura, para a conta não escapar por uma delas
    # quando o modo tolerante da R4 entrou em cena.
    monkeypatch.setattr(log, "le",
                        lambda s=None, dst=None: leituras.append("estrita") or estrita(s, dst))
    monkeypatch.setattr(log, "le_tolerante",
                        lambda dst=None: leituras.append("tolerante") or tolerante(dst))
    c.get("/sessoes")
    assert leituras == ["tolerante"], leituras


def test_a_lista_ainda_marca_a_sessao_que_nao_reexecuta(cliente, d):
    """A recusa continua a mesma, só que apurada sem refazer a sessão."""
    c, arquivo = cliente
    percorre(d, arquivo, "boa2", _politica(d=d))
    t = motor.inicia(d, semente="velha2")
    log.grava("velha2", t.eventos, destino=arquivo)
    log.grava("velha2", motor.avanca(d, t.estado, Resposta(texto="x")).eventos,
              destino=arquivo)                       # sem entrada: log antigo

    lista = {x["codigo"]: x for x in c.get("/sessoes").json()["sessoes"]}
    assert lista["boa2"]["reexecutavel"] is True
    assert lista["velha2"]["reexecutavel"] is False
    assert "entrada" in lista["velha2"]["motivo"]
    # E o detalhe, que reexecuta de verdade, concorda com a lista.
    assert c.get("/sessoes/velha2").status_code == 409
    assert c.get("/sessoes/boa2").status_code == 200


def test_a_lista_recusa_o_log_de_outro_topico_sem_reexecutar(cliente):
    c, arquivo = cliente
    arquivo.write_text(json.dumps({
        "ts": "2026-10-29T00:00:00.000+00:00", "sessao": "x",
        "tipo": "unidade_iniciada", "topico": "kc_99"}) + "\n", encoding="utf-8")
    linha = c.get("/sessoes").json()["sessoes"][0]
    assert linha["reexecutavel"] is False
    assert "kc_99" in linha["motivo"]


def test_a_lista_adianta_e_o_detalhe_decide(cliente, d):
    """A checagem barata da lista é uma APROXIMAÇÃO, e isto fixa isso.

    Uma sessão pode passar na lista e falhar ao ser aberta — log antigo
    com uma entrada que o motor de hoje recusa só aparece reexecutando.
    O painel tem de dizer o motivo, não estourar erro de servidor.
    """
    c, arquivo = cliente
    t = motor.inicia(d, semente="z1")
    log.grava("z1", t.eventos, destino=arquivo)
    t = motor.avanca(d, t.estado, Resposta(texto="f"))
    log.grava("z1", t.eventos, destino=arquivo, entrada=Resposta(texto="f"))
    for _ in range(6):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d, t.estado, Resposta())
        log.grava("z1", t.eventos, destino=arquivo, entrada=Resposta())
    log.grava("z1", (), destino=arquivo, entrada=Resposta(escolha=-1))

    linha = next(x for x in c.get("/sessoes").json()["sessoes"]
                 if x["codigo"] == "z1")
    assert linha["reexecutavel"] is True, "a lista não tem como saber"

    r = c.get("/sessoes/z1")
    assert r.status_code == 409
    assert "não aceita mais" in r.json()["detail"]


# --------------------------------------------------------------------------
# R4: uma linha corrompida não esconde as outras sessões (P2-C)
# --------------------------------------------------------------------------

def _corrompe(arquivo, indice):
    linhas = arquivo.read_text(encoding="utf-8").splitlines()
    linhas[indice] = '{"ts": "2026-'
    arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def test_uma_linha_ilegivel_nao_esconde_as_outras_sessoes(cliente, d):
    """O painel existe, entre outras razões, para funcionar DEPOIS de um
    travamento. Perder todas as sessões por causa de uma linha é o
    oposto disso — e era o que acontecia."""
    c, arquivo = cliente
    for codigo in ("c1", "c2", "c3"):
        percorre(d, arquivo, codigo, _politica(d=d))
    _corrompe(arquivo, 3)

    r = c.get("/sessoes")
    assert r.status_code == 200
    assert {x["codigo"] for x in r.json()["sessoes"]} == {"c1", "c2", "c3"}


def test_a_linha_ilegivel_e_contada_e_dita(cliente, d):
    """Contar é o que separa tolerar de esconder."""
    c, arquivo = cliente
    percorre(d, arquivo, "c4", _politica(d=d))
    assert c.get("/sessoes").json()["ilegiveis"] == 0
    _corrompe(arquivo, 2)
    _corrompe(arquivo, 4)
    assert c.get("/sessoes").json()["ilegiveis"] == 2


def test_a_reconstrucao_continua_estrita(cliente, d):
    """A tolerância é da lista, e só dela. Pular uma entrada aqui
    produziria uma sessão sem uma das respostas — estado plausível e
    errado, que é exatamente o que a T10 existe para impedir."""
    c, arquivo = cliente
    percorre(d, arquivo, "c5", _politica(d=d))
    _corrompe(arquivo, 2)
    assert c.get("/sessoes").status_code == 200
    with pytest.raises(log.LinhaCorrompida):
        log.reconstroi(d, "c5", arquivo)
    assert c.get("/sessoes/c5").status_code == 409


def test_a_tabela_diz_de_que_molde_veio_cada_episodio():
    """A coluna que separa generalizar de decorar.

    Duas variações do mesmo molde têm ids diferentes e são a mesma
    pergunta com a roupa trocada: sem os parâmetros na tabela, a análise
    não consegue dizer qual foi qual.
    """
    linhas = [
        {"tipo": "atividade_apresentada", "atividade": "t_1", "no": "B1",
         "do_molde": "mol_x", "parametros": {"n": 5}},
        {"tipo": "camada1_respondida", "atividade": "t_1", "no": "B1",
         "correta": True},
        {"tipo": "unidade_encerrada"},
    ]
    linha = painel.episodios(linhas)[0]
    assert linha["do_molde"] == "mol_x"
    assert linha["parametros"] == {"n": 5}


def test_item_escrito_a_mao_tem_as_colunas_vazias():
    """As colunas existem em toda linha: tabela com coluna que aparece e
    some não vira CSV."""
    linhas = [
        {"tipo": "atividade_apresentada", "atividade": "t_2", "no": "B1"},
        {"tipo": "camada1_respondida", "atividade": "t_2", "no": "B1",
         "correta": True},
        {"tipo": "unidade_encerrada"},
    ]
    linha = painel.episodios(linhas)[0]
    assert linha["do_molde"] == ""
    assert linha["parametros"] == {}
