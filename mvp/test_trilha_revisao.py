"""O que a revisão independente do ramo achou, um teste por achado.

O ramo `trilha` passou por um revisor de contexto novo antes de ser
integrado. Ele não achou nada crítico, e achou dez pontos importantes —
todos de caminhos que nenhum dos alunos simulados fazia. Cada teste
daqui reproduz um deles, e foi visto falhar antes do conserto.

Os números entre parênteses são os do relatório da revisão.
"""

from __future__ import annotations

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
from trilha_alunos import caminha  # noqa: E402

from mvp import (  # noqa: E402
    motor, portal, trilha, trilha_app, trilha_escada, trilha_log)
from mvp.test_trilha import (  # noqa: E402
    D, ESC, SEM_PROVA, _anda, _ate_a_abertura, _com_uma_versao_so, _comeca,
    _marca, _tela_voce_disse_de)
from mvp.test_trilha_app import _abre, _age, _tela  # noqa: E402


def _como(estado, persona):
    return trilha_alunos.responde(D, ESC, estado.tela, persona, estado)


def _sobe(t, erra=()):
    """Sobe a escada até a pergunta do topo. Erra a primeira tentativa dos
    degraus cujo id está em `erra`; o resto, acerta."""
    while t.tela.tipo != "pergunta":
        dados = t.tela.dados
        persona = "sabe"
        if (t.tela.tipo == "degrau" and dados["degrau"] in erra
                and dados["tentativa"] == 1):
            persona = "nao_sabe_erra"
        t = _anda(t.estado, persona)
    return t


def _ate_o_treino(t):
    """Da tela "você disse" até a primeira tela depois da máquina."""
    while t.tela.tipo in ("voce_disse", "maquina"):
        t = _anda(t.estado)
    return t


# --------------------------------------------------------------------------
# (1) O pedido tem de dizer de que tela é
# --------------------------------------------------------------------------

def test_cada_tela_tem_um_numero_e_ele_so_anda_quando_a_tela_muda():
    t0 = trilha.inicia(D, ESC, "s1")
    assert t0.estado.n == 1
    t1 = _comeca("explique")
    assert t1.estado.n == 2
    mesma = trilha.avanca(D, ESC, t1.estado, trilha.Entrada(acao="explicacao"))
    assert mesma.estado.n == 2                    # a explicação não troca a tela
    troca = trilha.avanca(D, ESC, t1.estado,
                          trilha.Entrada(acao="ritmo", ritmo="rapido"))
    assert troca.estado.n == 2
    assert _anda(t1.estado).estado.n == 3


def test_resposta_de_um_degrau_nao_vale_para_o_degrau_seguinte():
    """Degrau depois de degrau: o pedido repetido CABE na forma da tela
    nova. Sem o número, a resposta certa do primeiro virava a primeira
    tentativa errada do segundo — uma resposta que a pessoa não deu, a
    uma pergunta que ela não viu."""
    t1 = _comeca("explique")
    resposta = dataclasses.replace(_como(t1.estado, "sabe"), passo=t1.estado.n)
    t2 = trilha.avanca(D, ESC, t1.estado, resposta)
    assert (t2.tela.tipo, t2.tela.dados["indice"]) == ("degrau", 2)
    with pytest.raises(trilha.EntradaVelha):
        trilha.avanca(D, ESC, t2.estado, resposta)


def test_dois_continuar_nao_pulam_a_tela_da_maquina():
    # A prova do GRAFO para o B1 tem saída, e por isso não tem previsão: é
    # o caso em que a tela só continua. Com a prova da escada a tela pede
    # a previsão, e o mesmo é conferido em `mvp/test_trilha_prova.py`.
    t = _tela_voce_disse_de("B1", SEM_PROVA)
    segue = trilha.Entrada(acao="continuar", passo=t.estado.n)
    maquina = trilha.avanca(D, SEM_PROVA, t.estado, segue)
    assert maquina.tela.tipo == "maquina"
    with pytest.raises(trilha.EntradaVelha):
        trilha.avanca(D, SEM_PROVA, maquina.estado, segue)


def test_a_entrada_velha_e_uma_entrada_invalida():
    """Quem já tratava `EntradaInvalida` continua tratando."""
    assert issubclass(trilha.EntradaVelha, trilha.EntradaInvalida)


def test_sem_numero_o_motor_nao_confere():
    """Os alunos simulados e a reexecução do registro não mandam número."""
    t1 = _comeca("explique")
    assert _como(t1.estado, "sabe").passo is None
    assert _anda(t1.estado).tela.dados["indice"] == 2


@pytest.fixture
def destino(tmp_path):
    return tmp_path / "trilha" / "kc_00.jsonl"


@pytest.fixture
def app(destino):
    return trilha_app.cria_app(D, ESC, destino)


@pytest.fixture
def cliente(app):
    return TestClient(app)


def test_a_rota_exige_o_numero_da_tela(cliente):
    sessao, j = _abre(cliente, modo="explique")
    assert j["passo"] == 2
    r = cliente.post("/sessoes/%s/agir" % sessao, json={"acao": "explicacao"})
    assert r.status_code == 422


def test_pedido_de_tela_velha_da_409_com_a_tela_atual_e_nao_grava(
        app, cliente, destino):
    sessao, j = _abre(cliente, modo="explique")
    resposta = _como(app.state.sessoes[sessao], "sabe")
    primeira = _age(cliente, sessao, resposta, passo=j["passo"])
    assert primeira.status_code == 200
    atual = primeira.json()
    assert atual["passo"] == j["passo"] + 1

    antes, estado = len(trilha_log.le(destino)), app.state.sessoes[sessao]
    repetida = _age(cliente, sessao, resposta, passo=j["passo"])
    assert repetida.status_code == 409
    corpo = repetida.json()
    # A tela atual vem junto: o cliente redesenha em vez de adivinhar.
    assert corpo["tela"] == atual["tela"] and corpo["passo"] == atual["passo"]
    assert len(trilha_log.le(destino)) == antes
    assert app.state.sessoes[sessao] is estado


# --------------------------------------------------------------------------
# (2) O treino depois da escada tem de poder fechar
# --------------------------------------------------------------------------

def _prova_depois_da_escada(erra):
    """Modo "explique" no B1: sobe a escada, e no topo diz a crença."""
    t = _sobe(_comeca("explique"), erra=erra)
    assert t.tela.dados["papel"] == "topo"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca="type_is_a_hint"))
    assert t.tela.tipo == "voce_disse"
    return _ate_o_treino(t)


def _treina_certo(t, no="B1"):
    telas = []
    while not t.estado.premissa(no).resultado:
        telas.append(t.tela)
        t = _anda(t.estado)
    return t, [x for x in telas if x.tipo != "retorno"]


def test_com_um_erro_na_pratica_o_treino_ainda_fecha():
    """O treino depois da escada tem de poder fechar.

    Quando este teste nasceu, um erro na subida gastava as duas versões
    daquele degrau, sobrava UM exercício, e o treino caía numa questão de
    marcar para fechar. Desde 13/11/2026 a subida não repete passo: o
    erro gasta uma versão só, e sobram exercícios para o treino inteiro.
    """
    t = _prova_depois_da_escada(erra=(ESC["B1"].pratica[0].id,))
    fim, treinos = _treina_certo(t)
    assert [x.dados["papel"] for x in treinos] == ["treino", "treino"]
    assert [x.tipo for x in treinos] == ["degrau", "degrau"]
    assert fim.estado.premissa("B1").resultado == "corrigiu"


def _anda_em(esc, t, persona="sabe"):
    return trilha.avanca(D, esc, t.estado,
                         trilha_alunos.responde(D, esc, t.tela, persona,
                                                t.estado))


def _prova_no_topo(esc):
    """Com as escadas `esc`: sobe o B1 acertando, diz a crença no topo, e
    devolve a primeira tela depois da máquina."""
    t = trilha.inicia(D, esc, "s1")
    t = trilha.avanca(D, esc, t.estado,
                      trilha.Entrada(acao="comecar", modo="explique"))
    while t.tela.tipo != "pergunta":
        t = _anda_em(esc, t)
    t = trilha.avanca(D, esc, t.estado,
                      _marca(t.estado, crenca="type_is_a_hint"))
    assert t.tela.tipo == "voce_disse"
    while t.tela.tipo in ("voce_disse", "maquina"):
        t = _anda_em(esc, t)
    return t


def test_sem_exercicio_livre_o_treino_cai_nas_questoes_de_marcar():
    """Acabaram os exercícios: o botão "Treinar esta ideia" levava direto
    à premissa seguinte, sem treino nenhum. A spec 6.5 manda cair nas
    questões de marcar.

    O cenário era errar os dois degraus de prática na subida. A subida
    não gasta mais as duas versões, e o caso em que os exercícios acabam
    é o de escadas com uma versão por degrau: sobra um exercício para o
    treino, e a segunda resposta tem de vir de uma questão."""
    esc = _com_uma_versao_so()
    t = _prova_no_topo(esc)
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("degrau", "treino")
    t = _anda_em(esc, t)
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("pergunta", "treino")
    assert t.tela.dados["pede_razao"] and not t.tela.dados["pede_certeza"]
    t = _anda_em(esc, t)
    ep = t.estado.premissa("B1")
    assert (ep.resultado, ep.treinos) == ("corrigiu", 2)


def test_errar_a_questao_de_treino_zera_a_sequencia_e_traz_o_retorno():
    esc = _com_uma_versao_so()
    t = _anda_em(esc, _prova_no_topo(esc))        # o exercício, certo
    assert t.tela.tipo == "pergunta" and t.estado.premissa("B1").streak == 1
    errada = trilha.avanca(D, esc, t.estado, trilha.Entrada(acao="nao_sei"))
    assert (errada.tela.tipo, errada.tela.dados["veredito"]) == ("retorno", "errada")
    assert errada.estado.premissa("B1").streak == 0
    assert errada.estado.premissa("B1").treinos == 2


# --------------------------------------------------------------------------
# (3) O teto de oito telas é do motor, não do conteúdo
# --------------------------------------------------------------------------

def test_o_caminho_mais_longo_nao_passa_de_oito_telas():
    """Abertura certa pela razão da crença, reforço "não sei", escada,
    topo com a mesma crença, prova, treino. Com o treino podendo cair nas
    questões de marcar, esse caminho dava nove."""
    t = _ate_a_abertura("B2")
    crenca = "no_value_no_memory"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca=crenca, certa=True))
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="continuar"))
    assert t.tela.dados["papel"] == "reforco"
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="nao_sei"))
    t = _sobe(t)
    assert t.tela.dados["papel"] == "topo"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca=crenca))
    assert t.tela.tipo == "voce_disse"
    t = _ate_o_treino(t)
    assert t.estado.premissa("B2").telas == 7     # falta uma para o teto
    t = _anda(t.estado, "nao_sabe_erra")          # erra o primeiro treino
    while not t.estado.premissa("B2").resultado:
        t = _anda(t.estado)
    assert t.estado.premissa("B2").telas <= trilha.TETO_TELAS
    assert t.estado.premissa("B2").resultado == "em_aberto"


# --------------------------------------------------------------------------
# (4) A explicação não abre dentro da reconferência
# --------------------------------------------------------------------------

def test_na_reconferencia_a_explicacao_nao_abre():
    """A reconferência existe para separar "acertou logo depois de ler"
    de "assimilou". Ler de novo e acertar não é assimilar."""
    t = _comeca("explique", ritmo="rapido")
    while t.tela.dados.get("papel") != "reconferencia":
        t = _anda(t.estado, "nao_sabe_aprende")
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="explicacao"))
    assert not t.estado.premissa(t.tela.dados["premissa"]).reconferencia


# --------------------------------------------------------------------------
# (5) A crença dita num degrau é registrada
# --------------------------------------------------------------------------

def _escolhe_no_degrau(estado, arquivo, confianca=""):
    """A entrada que toca a peça de índice `arquivo` (do YAML) no degrau."""
    g = next(x for x in ESC[estado.tela.dados["premissa"]].degraus
             if x.id == estado.tela.dados["degrau"])
    v = g.versoes[estado.passo.versao]
    ordem = trilha_escada.ordem_das_pecas(estado.semente, g.id,
                                          estado.passo.versao, g.forma,
                                          len(v.pecas))
    return trilha.Entrada(acao="responder", pecas=(ordem.index(arquivo),),
                          confianca=confianca)


def test_a_crenca_dita_num_degrau_guiado_vai_para_o_registro_e_para_o_mapa():
    """O B1_3 oferece "Tanto faz: o tipo é só um aviso". O YAML liga essa
    alternativa à crença, e o motor jogava a ligação fora.

    Desde 13/11/2026 esse passo pede a certeza. Dita como CHUTE, a crença
    fica anotada, que é o que este teste guarda; dita com convicção, ela
    abre a refutação ali mesmo (mvp/test_trilha_diagnostico.py)."""
    t = _comeca("explique")
    while t.tela.dados["degrau"] != "esc_kc00_B1_3":
        t = _anda(t.estado)
    t = trilha.avanca(D, ESC, t.estado,
                      _escolhe_no_degrau(t.estado, 2, "chutei"))
    assert [e.dados for e in t.eventos if e.tipo == "crenca_registrada"] == [
        {"no": "B1", "crenca": "type_is_a_hint"}]
    assert t.estado.premissa("B1").apareceu == ("type_is_a_hint",)
    assert trilha.resumo(D, ESC, t.estado)[0]["apareceu"] == [
        D.crencas["type_is_a_hint"].afirma]


def test_a_crenca_corrigida_nao_aparece_duas_vezes_no_mapa():
    """Quem já teve a crença CORRIGIDA numa premissa e volta a dizê-la não
    ganha a mesma frase em "também apareceu"."""
    c = caminha(D, ESC, "crente_teimoso")
    for p in c.telas[-1].dados["premissas"]:
        assert p["crenca"] not in p["apareceu"]


# --------------------------------------------------------------------------
# (6) O registro diz que conteúdo a pessoa viu, e aguenta linha quebrada
# --------------------------------------------------------------------------

def test_a_escada_tem_assinatura_e_ela_muda_com_o_conteudo():
    a = trilha_escada.assinatura(ESC)
    assert len(a) == 12 and a == trilha_escada.assinatura(dict(ESC))
    g = ESC["B1"].degraus[0]
    outra = dataclasses.replace(ESC["B1"], degraus=(
        dataclasses.replace(g, frases=("Outra frase.",)),) + ESC["B1"].degraus[1:])
    assert trilha_escada.assinatura({**ESC, "B1": outra}) != a


def test_a_abertura_da_trilha_registra_a_assinatura_do_conteudo():
    t = trilha.inicia(D, ESC, "s1")
    assert t.eventos[0].dados["escada"] == trilha_escada.assinatura(ESC)


def test_o_degrau_respondido_guarda_a_resposta_em_indices_do_arquivo():
    """As peças vão para a tela embaralhadas pela semente. O registro
    guarda a resposta na ordem do ARQUIVO, que é a que se consegue ler
    sem refazer o embaralhamento."""
    t = _comeca("explique")
    while t.tela.dados["forma"] != "montar":
        t = _anda(t.estado)
    g = next(x for x in ESC["B1"].degraus if x.id == t.tela.dados["degrau"])
    depois = _anda(t.estado)
    evento = next(e for e in depois.eventos if e.tipo == "degrau_respondido")
    assert tuple(evento.dados["resposta"]) == g.versoes[0].certa[0]

    while depois.tela.tipo != "degrau" or depois.tela.dados["forma"] != "digitar":
        depois = _anda(depois.estado)
    g = next(x for x in ESC[depois.tela.dados["premissa"]].degraus
             if x.id == depois.tela.dados["degrau"])
    esperado = g.versoes[depois.estado.passo.versao].aceitas[0]
    digitou = _anda(depois.estado)
    evento = next(e for e in digitou.eventos if e.tipo == "degrau_respondido")
    assert evento.dados["resposta"] == esperado


def test_linha_quebrada_no_registro_nao_derruba_a_abertura(cliente, destino):
    """Uma queda no meio de uma gravação deixa meia linha no arquivo. Sem
    tolerância, toda sessão com código dava 500 dali em diante."""
    _abre(cliente, codigo="P20")
    with destino.open("a", encoding="utf-8") as f:
        f.write('{"v": 1, "ts": "2026-11-13T00:00:00", "sessao": "P2\n')
    r = cliente.post("/sessoes", json={"codigo": "P21"})
    assert r.status_code == 200 and r.json()["sessao"] == "P21"


# --------------------------------------------------------------------------
# (7) Uma pausa longa não trava a sessão
# --------------------------------------------------------------------------

def test_tempo_absurdo_e_cortado_e_a_sessao_segue(app, cliente, destino):
    """Quem deixava a página aberta por mais de duas horas recebia 422
    para sempre: cada nova tentativa mandava um tempo ainda maior."""
    sessao, j = _abre(cliente)
    corpo = {"acao": "nao_sei", "passo": j["passo"], "ms": 5 * 60 * 60 * 1000}
    r = cliente.post("/sessoes/%s/agir" % sessao, json=corpo)
    assert r.status_code == 200
    gravada = [l for l in trilha_log.le(destino, sessao)
               if l["tipo"] == "entrada_recebida"][-1]
    assert gravada["ms"] == trilha_app.LIMITE_MS


# --------------------------------------------------------------------------
# (8) O código do participante sobrevive a um reinício
# --------------------------------------------------------------------------

def test_depois_de_um_reinicio_o_codigo_retoma_a_sessao(destino):
    """O servidor reinicia toda vez que o sistema é religado. O código
    dava 409 dali em diante, e a pessoa seguia anônima, sem vínculo com
    o que já tinha feito. O motor é puro e o registro guarda as entradas:
    a sessão é refeita."""
    antes_app = trilha_app.cria_app(D, ESC, destino)
    antes = TestClient(antes_app)
    sessao, j = _abre(antes, modo="explique", ritmo="rapido", codigo="P30")
    for _ in range(7):
        j = _age(antes, sessao, _como(antes_app.state.sessoes[sessao],
                                      "nao_sabe_aprende")).json()

    depois = TestClient(trilha_app.cria_app(D, ESC, destino))
    r = depois.post("/sessoes", json={"codigo": "P30"})
    assert r.status_code == 200
    volta = r.json()
    for chave in ("tela", "passo", "progresso", "modo", "ritmo"):
        assert volta[chave] == j[chave], chave
    tipos = [l["tipo"] for l in trilha_log.le(destino, "P30")]
    assert tipos[-1] == "sessao_reconstruida"
    # E dali ela segue como qualquer outra.
    segue = _age(depois, "P30", _como(depois.app.state.sessoes["P30"],
                                      "nao_sabe_aprende"))
    assert segue.status_code == 200 and segue.json()["passo"] == j["passo"] + 1


def test_a_sessao_reconstruida_chega_ao_mapa(destino):
    primeiro_app = trilha_app.cria_app(D, ESC, destino)
    primeiro = TestClient(primeiro_app)
    sessao, j = _abre(primeiro, codigo="P31")
    for _ in range(5):
        j = _age(primeiro, sessao, _como(primeiro_app.state.sessoes[sessao],
                                         "crente_aprende")).json()
    segundo_app = trilha_app.cria_app(D, ESC, destino)
    segundo = TestClient(segundo_app)
    j = segundo.post("/sessoes", json={"codigo": "P31"}).json()
    for _ in range(300):
        if j["tela"]["tipo"] == "mapa":
            break
        j = _age(segundo, "P31", _como(segundo_app.state.sessoes["P31"],
                                       "crente_aprende")).json()
    assert j["tela"]["tipo"] == "mapa"
    inteira = caminha(D, ESC, "crente_aprende", semente="P31")
    assert j["tela"] == inteira.telas[-1].json()


def test_se_o_conteudo_mudou_a_sessao_nao_e_refeita_e_a_mensagem_diz(destino):
    """Reexecutar entradas contra outra escada daria um estado plausível
    e errado. A assinatura gravada na abertura é o que impede."""
    _abre(TestClient(trilha_app.cria_app(D, ESC, destino)), codigo="P32")
    g = ESC["B1"].degraus[0]
    mudada = {**ESC, "B1": dataclasses.replace(ESC["B1"], degraus=(
        dataclasses.replace(g, frases=("Outra frase.",)),) + ESC["B1"].degraus[1:])}
    r = TestClient(trilha_app.cria_app(D, mudada, destino)).post(
        "/sessoes", json={"codigo": "P32"})
    assert r.status_code == 409
    detalhe = r.json()["detail"]
    assert "P32" in detalhe and "conteúdo" in detalhe
    assert "memória" not in detalhe and "construída" not in detalhe


def test_linha_quebrada_da_propria_sessao_impede_a_retomada(destino):
    _abre(TestClient(trilha_app.cria_app(D, ESC, destino)), codigo="P33")
    with destino.open("a", encoding="utf-8") as f:
        f.write('{"v": 1, "sessao": "P33", "tipo": "entrada_rece\n')
    r = TestClient(trilha_app.cria_app(D, ESC, destino)).post(
        "/sessoes", json={"codigo": "P33"})
    assert r.status_code == 409 and "P33" in r.json()["detail"]


# --------------------------------------------------------------------------
# Regraduados de "menor": o que vai para o disco tem teto, e uma escada
# quebrada não derruba os treze tópicos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("campo", ["acao", "confianca", "modo", "ritmo"])
def test_campo_de_texto_longo_demais_da_422(cliente, campo):
    sessao, j = _abre(cliente)
    corpo = {"acao": "continuar", "passo": j["passo"], campo: "x" * 33}
    r = cliente.post("/sessoes/%s/agir" % sessao, json=corpo)
    assert r.status_code == 422


def test_escada_invalida_nao_derruba_o_portal(tmp_path, monkeypatch, capsys):
    def quebrada(caminho, d):
        raise trilha_escada.EscadaInvalida(["B1: degrau sem versão"])

    monkeypatch.setattr(trilha_escada, "le", quebrada)
    cliente = TestClient(portal.cria_portal(tmp_path))
    lista = cliente.get("/topicos").json()["topicos"]
    assert len(lista) == 13 and all(t["trilha"] is None for t in lista)
    assert cliente.get("/kc/kc_00/saude").status_code == 200
    assert "escada" in capsys.readouterr().err.lower()


# --------------------------------------------------------------------------
# (9) e (10) O conteúdo e os alunos que faltavam
# --------------------------------------------------------------------------

def test_copiar_de_outra_variavel_e_ensinado_antes_de_ser_cobrado():
    """O último degrau do I1 usa `nota = pontos;`. Era a primeira vez que
    uma variável aparecia do lado direito, num degrau de PRÁTICA, sem
    frase — e esse degrau é o "de produzir" de quem acerta firme."""
    degraus = ESC["I1"].degraus
    usa = [i for i, g in enumerate(degraus)
           if any("= pontos;" in (v.mostra + v.certa_texto) or
                  "= ano;" in (v.mostra + v.certa_texto) for v in g.versoes)]
    assert usa, "nenhum degrau do I1 copia de outra variável"
    primeiro = degraus[usa[0]]
    assert primeiro.guiado and primeiro.frases
    assert any("outra variável" in f for f in primeiro.frases)


def test_a_leitura_no_repositorio_e_a_do_conteudo_de_hoje():
    sys.path.insert(0, str(RAIZ.parent / "scripts"))
    import confere_escada
    arquivo = RAIZ.parent / "docs" / "escada-kc00-leitura.md"
    assert arquivo.read_text(encoding="utf-8") == confere_escada.leitura(D, ESC)


def test_ha_aluno_que_tropeca_na_pratica_e_aluno_que_abre_a_explicacao():
    assert {"tropeca_na_pratica", "abre_a_explicacao"} <= set(trilha_alunos.PERSONAS)
    tropeca = caminha(D, ESC, "tropeca_na_pratica")
    # Tropeçar ERA ganhar uma segunda tentativa. Sem ela, é o passo de
    # prática da subida ficar registrado como a lacuna da ideia.
    assert tropeca.estado.fim
    assert all(tropeca.estado.premissa(n).tropecos == (ESC[n].pratica[0].id,)
               for n in D.ordem)
    abre = caminha(D, ESC, "abre_a_explicacao")
    assert {abre.estado.premissa(n).resultado for n in D.ordem} == {
        "aprendeu_agora"}
    assert [e.tipo for e in abre.eventos].count("explicacao_aberta") == 5
