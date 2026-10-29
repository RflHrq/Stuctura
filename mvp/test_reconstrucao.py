"""CS-6: o estado da sessão é reconstruível só pelo log.

O MVP guarda o estado em memória ([mvp/app.py](app.py)). Se o servidor
reinicia no meio de uma sessão, ela se perde — e numa coleta de 10 a 15
pessoas, perder uma é perder 7%. Como a pessoa não volta para repetir, a
perda é irreparável.

A reconstrução aqui é **reexecução**, não leitura de resumo: o motor é
puro, então reaplicar as mesmas entradas ao mesmo domínio devolve o mesmo
estado, campo a campo. Isso exige que o log guarde as ENTRADAS, e não só o
que elas provocaram — é a linha `entrada_recebida` que a T10 acrescenta.

A alternativa seria projetar o estado a partir dos eventos semânticos
(`no_confirmado`, `crenca_detectada`...). Seria uma segunda implementação
das regras, livre para divergir da primeira sem ninguém perceber. Esta não
pode divergir: é a mesma.
"""

from __future__ import annotations

import json

import pytest

from mvp import log, motor
from mvp.dominio import carrega
from mvp.motor import Resposta
from mvp.test_motor import _politica

D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


@pytest.fixture
def caminho(tmp_path):
    return tmp_path / "eventos.jsonl"


def percorre(d, caminho, sessao, politica, parar_em=None, limite=300):
    """Roda a unidade gravando como o servidor grava: entrada e eventos.

    É de propósito que este laço imite [mvp/app.py](app.py) em vez de
    chamá-lo: se a gravação do servidor divergir desta, o teste de rota lá
    embaixo acusa.
    """
    t = motor.inicia(d, semente=sessao)
    log.grava(sessao, t.eventos, destino=caminho)
    for _ in range(limite):
        if t.tela.tipo == "mapa" or t.tela.tipo == parar_em:
            return t
        r = politica(t.tela, t.estado)
        t = motor.avanca(d, t.estado, r)
        log.grava(sessao, t.eventos, destino=caminho, entrada=r)
    raise AssertionError("a unidade não terminou em %d passos" % limite)


# --------------------------------------------------------------------------
# O coração do CS-6
# --------------------------------------------------------------------------

def test_o_estado_reconstruido_e_identico_ao_da_memoria_em_cada_passo(d, caminho):
    """Não só no fim: em TODO passo.

    Comparar apenas o estado final deixaria passar uma reconstrução que
    erra no meio e acerta por acaso na soma.
    """
    t = motor.inicia(d, semente="s1")
    log.grava("s1", t.eventos, destino=caminho)
    politica = _politica(erra_no="B2", erra_diagnostico=2, d=d)
    passos = 0
    for _ in range(300):
        assert log.reconstroi(d, "s1", caminho).estado == t.estado, passos
        if t.tela.tipo == "mapa":
            break
        r = politica(t.tela, t.estado)
        t = motor.avanca(d, t.estado, r)
        log.grava("s1", t.eventos, destino=caminho, entrada=r)
        passos += 1
    assert passos > 20, "a sessão foi curta demais para dizer alguma coisa"


def test_a_tela_tambem_volta_igual(d, caminho):
    """Quem retoma precisa saber o que estava na frente da pessoa.

    O estado sozinho diria em que fase ela parou, mas não com quais
    alternativas na tela — e elas são embaralhadas pela semente.
    """
    t = percorre(d, caminho, "s2", _politica(d=d))
    volta = log.reconstroi(d, "s2", caminho)
    assert volta.tela == t.tela


def test_a_resposta_trancada_sobrevive_a_queda(d, caminho):
    """O pior momento para cair: a camada 1 respondida, a razão ainda não.

    Se a trancada se perdesse, a pessoa responderia a camada 1 de novo
    depois de já ter visto as razões — e o par resposta-razão, que a
    classificação pressupõe independente, estaria contaminado.
    """
    t = percorre(d, caminho, "s3", _politica(d=d), parar_em="razao")
    volta = log.reconstroi(d, "s3", caminho)
    assert t.estado.fase == motor.RAZAO
    assert volta.estado.pendente == t.estado.pendente
    assert volta.estado.pendente.escolha is not None


def test_a_frase_do_teachback_volta_inteira(d, caminho):
    t = percorre(d, caminho, "s4", _politica(d=d))
    volta = log.reconstroi(d, "s4", caminho)
    assert volta.estado.frase_inicial == t.estado.frase_inicial
    assert volta.estado.frase_inicial != ""
    assert volta.estado.frase_final == t.estado.frase_final


def test_cada_resposta_deixa_uma_linha_de_entrada_no_log(d, caminho):
    """A entrada é gravada ANTES do que ela provocou.

    Quem lê o arquivo com `cat` vê causa e efeito na ordem em que
    aconteceram, e a reexecução não depende de reordenar nada.
    """
    log.grava("s5", (motor.Evento("unidade_iniciada", {"topico": d.id}),),
              destino=caminho)
    log.grava("s5", (motor.Evento("teachback_inicial", {"texto": "oi"}),),
              destino=caminho, entrada=Resposta(texto="oi", ms=7))
    linhas = [json.loads(x) for x in
              caminho.read_text(encoding="utf-8").splitlines()]
    assert [x["tipo"] for x in linhas] == [
        "unidade_iniciada", "entrada_recebida", "teachback_inicial"]
    assert linhas[1]["texto"] == "oi"
    assert linhas[1]["ms"] == 7
    assert linhas[1]["sessao"] == "s5"


def test_reconstruir_nao_escreve_no_log(d, caminho):
    """Reexecutar produz os mesmos eventos de novo. Gravá-los duplicaria a
    sessão inteira no arquivo que a análise vai ler."""
    percorre(d, caminho, "s6", _politica(d=d))
    antes = caminho.read_text(encoding="utf-8")
    log.reconstroi(d, "s6", caminho)
    log.reconstroi(d, "s6", caminho)
    assert caminho.read_text(encoding="utf-8") == antes


def test_uma_sessao_nao_e_reconstruida_com_as_respostas_de_outra(d, caminho):
    """Duas pessoas gravam no MESMO arquivo. Se o filtro por sessão
    falhasse, a resposta de uma entraria no estado da outra."""
    percorre(d, caminho, "a1", _politica(erra_no="B2", erra_diagnostico=2, d=d))
    t = percorre(d, caminho, "b2", _politica(d=d), parar_em="razao")
    assert log.reconstroi(d, "b2", caminho).estado == t.estado


# --------------------------------------------------------------------------
# Os limites: quando NÃO dá para reconstruir, isso tem de aparecer
# --------------------------------------------------------------------------

def test_sessao_que_nao_esta_no_log_nao_existe(d, caminho):
    percorre(d, caminho, "s7", _politica(d=d))
    assert log.reconstroi(d, "outra", caminho) is None


def test_um_log_sem_as_entradas_falha_alto(d, caminho):
    """Portão M: logs gravados antes desta tarefa têm os eventos e não têm
    as entradas. Reexecutá-los devolveria a tela de abertura — uma sessão
    em branco com cara de sessão válida. Isso precisa estourar."""
    t = motor.inicia(d, semente="velha")
    log.grava("velha", t.eventos, destino=caminho)
    t = motor.avanca(d, t.estado, Resposta(texto="frase"))
    log.grava("velha", t.eventos, destino=caminho)        # sem entrada=
    with pytest.raises(log.LogIncompleto):
        log.reconstroi(d, "velha", caminho)


def test_um_log_de_outro_topico_nao_entra_neste_dominio(d, caminho):
    """As entradas são índices de alternativas. Aplicadas a outro banco de
    atividades elas apontam para outras opções, e o estado sai plausível e
    errado."""
    caminho.write_text(json.dumps({
        "ts": "2026-10-28T00:00:00.000+00:00", "sessao": "x",
        "tipo": "unidade_iniciada", "topico": "kc_99"}) + "\n",
        encoding="utf-8")
    with pytest.raises(log.LogIncompleto):
        log.reconstroi(d, "x", caminho)


def test_uma_sessao_que_so_comecou_reconstroi_sem_erro(d, caminho):
    """Zero entradas é um estado legítimo: a pessoa abriu e não respondeu
    nada. Não pode ser confundido com log velho."""
    t = motor.inicia(d, semente="nova")
    log.grava("nova", t.eventos, destino=caminho)
    assert log.reconstroi(d, "nova", caminho).estado == t.estado


# --------------------------------------------------------------------------
# A rota: o servidor reiniciado continua a sessão
# --------------------------------------------------------------------------

@pytest.fixture
def cliente(tmp_path, monkeypatch):
    """Um servidor com log próprio, para o teste não escrever na coleta."""
    from fastapi.testclient import TestClient

    from mvp import app as aplicacao

    monkeypatch.setattr(log, "DESTINO", tmp_path / "eventos.jsonl")
    aplicacao.sessoes.clear()
    with TestClient(aplicacao.app) as c:
        yield c, aplicacao, tmp_path / "eventos.jsonl"


def test_o_servidor_reiniciado_continua_a_sessao(cliente):
    """O caso real: o processo morre, a página de quem responde continua
    aberta, e a próxima resposta chega a um servidor sem memória."""
    c, aplicacao, _ = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    antes = c.post("/sessoes/%s/responder" % sessao,
                   json={"texto": "minha frase"}).json()["tela"]
    assert antes["tipo"] == "ensino"

    aplicacao.sessoes.clear()                      # caiu e voltou

    r = c.post("/sessoes/%s/responder" % sessao, json={})
    assert r.status_code == 200
    assert r.json()["tela"]["tipo"] == "ensino"
    assert r.json()["tela"]["indice"] == antes["indice"] + 1


def test_a_sessao_retomada_nao_perde_a_frase_de_abertura(cliente):
    c, aplicacao, _ = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    c.post("/sessoes/%s/responder" % sessao, json={"texto": "antes de tudo"})
    aplicacao.sessoes.clear()
    assert aplicacao.sessoes.get(sessao) is None
    c.post("/sessoes/%s/responder" % sessao, json={})
    assert aplicacao.sessoes[sessao].frase_inicial == "antes de tudo"


def test_a_retomada_fica_registrada_no_log(cliente):
    """Para a análise: uma sessão com queda no meio não é igual às outras,
    e isso tem de ser visível sem perguntar a ninguém."""
    c, aplicacao, arquivo = cliente
    sessao = c.post("/sessoes").json()["sessao"]
    c.post("/sessoes/%s/responder" % sessao, json={"texto": "x"})
    aplicacao.sessoes.clear()
    c.post("/sessoes/%s/responder" % sessao, json={})
    tipos = [x["tipo"] for x in log.le(sessao, arquivo)]
    assert tipos.count("sessao_retomada") == 1


def test_uma_sessao_que_nunca_existiu_continua_dando_404(cliente):
    c, _, _ = cliente
    r = c.post("/sessoes/naoexiste/responder", json={})
    assert r.status_code == 404


def test_entrada_que_o_motor_nao_aceita_mais_falha_alto(d, caminho):
    """Consequência direta da R1, e ela apareceu sozinha.

    `{"escolha": -1}` era aceito e virava um episódio. Logs gravados
    antes disso têm entradas que o motor de hoje recusa — e reexecutá-las
    daria outro resultado. A sessão não é reexecutável, e dizer isso é
    melhor do que estourar um erro de servidor no painel.
    """
    t = motor.inicia(d, semente="antiga")
    log.grava("antiga", t.eventos, destino=caminho)
    t = motor.avanca(d, t.estado, Resposta(texto="f"))
    log.grava("antiga", t.eventos, destino=caminho, entrada=Resposta(texto="f"))
    for _ in range(5):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d, t.estado, Resposta())
        log.grava("antiga", t.eventos, destino=caminho, entrada=Resposta())
    # A entrada que a versão antiga gravava e a de hoje recusa.
    log.grava("antiga", (), destino=caminho, entrada=Resposta(escolha=-1))

    with pytest.raises(log.LogIncompleto) as erro:
        log.reconstroi(d, "antiga", caminho)
    assert "não aceita mais" in str(erro.value)


# --------------------------------------------------------------------------
# R5: o log diz em que versão foi escrito (P2-D da revisão do ciclo 1)
# --------------------------------------------------------------------------

def test_toda_linha_gravada_carrega_a_versao(d, caminho):
    """O formato já mudou duas vezes no primeiro ciclo e a única pista
    era a ausência de campos. Com coleta em andamento e código
    evoluindo, é o caminho curto para uma análise que mistura formatos
    sem perceber qual participante foi medido com qual instrumento."""
    t = motor.inicia(d, semente="v1")
    log.grava("v1", t.eventos, destino=caminho)
    log.grava("v1", motor.avanca(d, t.estado, Resposta(texto="f")).eventos,
              destino=caminho, entrada=Resposta(texto="f"))
    cruas = [json.loads(x) for x in
             caminho.read_text(encoding="utf-8").splitlines()]
    assert cruas, "nada foi gravado"
    assert all(x["v"] == log.VERSAO for x in cruas)
    # A entrada também: ela é o registro de recuperação, e envelhece junto.
    assert any(x["tipo"] == log.ENTRADA for x in cruas)


def test_linha_do_ciclo_1_e_lida_como_versao_zero(d, caminho):
    """Log antigo continua legível, e aparece como o que é: anterior ao
    versionamento. Preencher na leitura evita testar a ausência de um
    campo em cada lugar do código."""
    caminho.write_text(json.dumps({
        "ts": "2026-10-28T00:00:00.000+00:00", "sessao": "antiga",
        "tipo": "unidade_iniciada", "topico": d.id}) + "\n", encoding="utf-8")
    linhas = log.le("antiga", caminho)
    assert linhas[0]["v"] == log.VERSAO_ZERO
    assert log.VERSAO_ZERO < log.VERSAO


def test_um_log_misto_distingue_as_duas_origens(d, caminho):
    """O caso real: o arquivo de desenvolvimento tem sessões dos dois
    ciclos, e a análise precisa poder separá-las sem adivinhar."""
    caminho.write_text(json.dumps({
        "ts": "2026-10-28T00:00:00.000+00:00", "sessao": "antiga",
        "tipo": "unidade_iniciada", "topico": d.id}) + "\n", encoding="utf-8")
    t = motor.inicia(d, semente="nova")
    log.grava("nova", t.eventos, destino=caminho)

    por_versao = {}
    for x in log.le(None, caminho):
        por_versao.setdefault(x["v"], set()).add(x["sessao"])
    assert por_versao == {log.VERSAO_ZERO: {"antiga"}, log.VERSAO: {"nova"}}
