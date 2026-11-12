# -*- coding: utf-8 -*-
"""O percurso de uma PESSOA, lido dos logs dela.

O TERCEIRO MECANISMO do histórico individual, e o mais barato dos três:
é LEITURA, não estado novo. O log já guarda tudo por sessão, e o código
do participante já é o id da sessão. O que faltava era algo que lesse os
vários logs de um mesmo código — e isso não existia porque, até aqui, uma
pessoa fazia uma sessão.

O QUE ELE RESPONDE, e nenhuma destas perguntas tinha resposta antes:

    que tópicos esta pessoa atravessou, e quais ela encerrou
    que conceitos ela teve OPORTUNIDADE de aprender, e em que cartão
    quais ela confirmou, quais só foram diagnosticados, quais revisitou
    e, dado um tópico novo, o que ele vai cobrar que ela não teve
    chance de aprender

A FORMA DA RESPOSTA importa, e foi decidida pelo dono: *não "você não
pode", mas "isto aqui vai cobrar o que você não teve chance de
aprender"*. Então isto não é portão: é relatório. Nada aqui bloqueia
sessão, e nada aqui escreve no log.

E É SÓ LEITURA, no sentido forte: nenhuma função deste módulo abre
arquivo para escrita, e há teste conferindo que o arquivo não muda.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from mvp import historico, log, motor
from mvp.dominio import carrega


# --------------------------------------------------------------------------
# Um log de verdade, com três tópicos do mesmo código
# --------------------------------------------------------------------------

def _joga(c, d, codigo, limite=500):
    """Uma sessão inteira, acertando tudo, pela rota."""
    r = c.post("/sessoes", json={"codigo": codigo})
    assert r.status_code == 200, r.json()
    r = r.json()
    falas = ({n.texto for n in d.nos.values()}
             | {n.simples for n in d.nos.values()})
    for _ in range(limite):
        tela = r.get("tela") or {}
        if tela.get("tipo") == "mapa":
            return
        corpo: dict = {}
        if tela.get("tipo") == "frase":
            corpo = {"texto": "uma frase"}
        elif tela.get("tipo") == "confianca":
            corpo = {"confianca": "tenho certeza"}
        elif tela.get("tipo") == "razao":
            corpo = {"escolha": next(
                (i for i, o in enumerate(tela["opcoes"])
                 if o["texto"] in falas), 0)}
        elif tela.get("tipo") == "atividade":
            a = next(x for x in d.atividades if x.id == tela["atividade"])
            corpo = {"escolha": motor.indice_correto_na_tela(codigo, a)}
        r = c.post("/sessoes/%s/responder" % codigo, json=corpo).json()
    raise AssertionError("a unidade de %s não terminou" % codigo)


def _cala(aid: str) -> bool:
    """A alternância da persona que diz "não sei", pelo id do item."""
    import hashlib

    return hashlib.sha256(aid.encode("utf-8")).digest()[0] % 2 == 0


def _nao_sabe(c, d, codigo, limite=900):
    """Uma sessão de quem declara lacuna: apresenta, nunca confirma.

    ESTE PARTICIPANTE ENTROU por causa de uma sabotagem que não caiu.
    Com só o P20 no arquivo — que acerta tudo —, todo conceito
    apresentado também era confirmado, e os dois conjuntos ficavam
    IGUAIS: trocar `confirmados()` por `apresentados()` passava em todos
    os testes. Quem diz "não sei" tem os cinco apresentados e zero
    confirmados, e é ele que separa as duas listas.
    """
    r = c.post("/sessoes", json={"codigo": codigo})
    assert r.status_code == 200, r.json()
    r = r.json()
    for _ in range(limite):
        tela = r.get("tela") or {}
        if tela.get("tipo") == "mapa":
            return
        corpo: dict = {}
        if tela.get("tipo") == "frase":
            corpo = {"texto": "nao sei dizer"}
        elif tela.get("tipo") == "confianca":
            corpo = {"confianca": "chutei"}
        elif tela.get("tipo") == "razao":
            corpo = {"nao_sei": True}
        elif tela.get("tipo") == "atividade":
            aid = tela["atividade"]
            if _cala(aid):
                corpo = {"nao_sei": True}
            else:
                a = next(x for x in d.atividades if x.id == aid)
                na_tela = motor.opcoes_na_tela(codigo, a)
                corpo = {"escolha": next(
                    (i for i, o in enumerate(na_tela) if not o.correta), 0)}
        r = c.post("/sessoes/%s/responder" % codigo, json=corpo).json()
    raise AssertionError("a unidade de %s não terminou" % codigo)


@pytest.fixture(scope="module")
def coleta(tmp_path_factory):
    """P20 faz o kc_02 inteiro e abre o kc_07; P21 faz só o kc_02;
    P22 atravessa o kc_02 dizendo "não sei".

    UM arquivo para todos, que é o que o guarda `(código, tópico)` passou
    a permitir e o que um histórico individual quer.
    """
    from mvp import app as aplicacao

    arquivo = tmp_path_factory.mktemp("percurso") / "coleta.jsonl"
    antigo_destino, antigo_dominio = log.DESTINO, aplicacao.dominio
    try:
        log.DESTINO = arquivo
        kc02 = carrega(topico="kc_02")
        aplicacao.dominio = kc02
        aplicacao.sessoes.clear()
        with TestClient(aplicacao.app) as c:
            _joga(c, kc02, "P20")
            _joga(c, kc02, "P21")
            _nao_sabe(c, kc02, "P22")
        kc07 = carrega(topico="kc_07")
        aplicacao.dominio = kc07
        aplicacao.sessoes.clear()
        with TestClient(aplicacao.app) as c:
            assert c.post("/sessoes",
                          json={"codigo": "P20"}).status_code == 200
        yield arquivo
    finally:
        log.DESTINO, aplicacao.dominio = antigo_destino, antigo_dominio
        aplicacao.sessoes.clear()


# --------------------------------------------------------------------------
# As unidades
# --------------------------------------------------------------------------

def test_o_percurso_lista_os_topicos_que_a_pessoa_abriu(coleta):
    p = historico.percurso("P20", [coleta])
    assert [u.topico for u in p.unidades] == ["kc_02", "kc_07"]


def test_o_percurso_diz_qual_unidade_foi_ENCERRADA(coleta):
    """Abrir e encerrar são coisas diferentes, e o histórico não pode
    confundi-las: quem abriu o kc_07 e parou na primeira tela não teve o
    percurso daquele tópico."""
    p = historico.percurso("P20", [coleta])
    por_topico = {u.topico: u.encerrada for u in p.unidades}
    assert por_topico == {"kc_02": True, "kc_07": False}


def test_o_percurso_de_outro_codigo_nao_entra(coleta):
    """O log é um só, e o percurso é de UMA pessoa."""
    p = historico.percurso("P21", [coleta])
    assert [u.topico for u in p.unidades] == ["kc_02"]
    assert all(e["sessao"] == "P21" for e in p.eventos)


def test_codigo_que_nao_existe_devolve_percurso_vazio(coleta):
    p = historico.percurso("P99", [coleta])
    assert p.unidades == ()
    assert p.eventos == ()


# --------------------------------------------------------------------------
# Os conceitos
# --------------------------------------------------------------------------

def test_o_percurso_diz_que_conceitos_a_pessoa_teve_oportunidade(coleta):
    """As cinco liberações do inventário, todas do kc_02."""
    p = historico.percurso("P20", [coleta])
    assert set(p.apresentados()) == {"endereco", "ponteiro",
                                     "operador_endereco", "derreferencia",
                                     "sizeof"}


def test_a_oportunidade_vem_com_o_cartao_e_a_versao_do_material(coleta):
    """Sem o cartão, "teve oportunidade" não é conferível; sem a versão,
    não dá para saber o que a pessoa viu quando o material mudar."""
    p = historico.percurso("P20", [coleta])
    for cid, ocorrencias in p.apresentados().items():
        assert ocorrencias, cid
        for o in ocorrencias:
            assert o["no"].startswith("kc_02:"), o
            assert len(o["material"]) == 12, o
            assert o["momento"] == "abertura", o


def test_o_percurso_separa_apresentado_de_confirmado(coleta):
    """A distinção que o inventário já fazia, agora por PESSOA.

    Apresentação não é compreensão: as duas listas existem separadas, e
    confundi-las transformaria o histórico em declaração falsa de
    domínio.

    A PRIMEIRA VERSÃO DESTE TESTE NÃO PEGAVA ISSO. Com só o P20 no
    arquivo, todo apresentado também era confirmado e os dois conjuntos
    eram iguais — trocar uma função pela outra passava. Quem achou foi
    uma sabotagem; quem conserta é o P22.
    """
    p = historico.percurso("P20", [coleta])
    assert set(p.confirmados()) <= set(p.apresentados())
    assert p.confirmados(), "quem acertou tudo não confirmou nada?"

    q = historico.percurso("P22", [coleta])
    assert set(q.confirmados()) < set(q.apresentados()), (
        "as duas listas ficaram iguais para quem declara lacuna: elas "
        "não estão lendo eventos diferentes")


def test_quem_declara_lacuna_tem_oportunidade_e_nao_tem_confirmacao(coleta):
    """O caso que mais importa para a tese, legível por conceito.

    O P22 recebeu as CINCO oportunidades do kc_02, foi diagnosticado,
    revisitou na construção — e não confirmou nenhuma. Antes disto o log
    dizia isso por NÓ, e saber qual CONCEITO ficou sem confirmação
    exigia reler o `conceitos.yaml` e cruzar à mão.
    """
    q = historico.percurso("P22", [coleta])
    assert len(q.apresentados()) == 5, sorted(q.apresentados())
    assert q.diagnosticados(), "não foi diagnosticado em nada"
    assert q.revisitados(), "declarou lacuna e não revisitou nada"
    assert q.confirmados() == {}, sorted(q.confirmados())
    assert q.teve_oportunidade("sizeof")
    assert not q.confirmou("sizeof")


def test_a_revisita_do_percurso_diz_o_momento(coleta):
    """Construção, e não treino: o P22 nunca teve crença refutada."""
    q = historico.percurso("P22", [coleta])
    momentos = {e["momento"] for ocorr in q.revisitados().values()
                for e in ocorr}
    assert momentos == {"construcao"}, sorted(momentos)


def test_o_percurso_conta_diagnostico_e_revisita(coleta):
    p = historico.percurso("P20", [coleta])
    assert set(p.diagnosticados()) <= set(p.apresentados())
    # Quem acerta tudo não revisita: está medido em test_arquitetura.
    assert p.revisitados() == {}


def test_teve_oportunidade_e_confirmou_respondem_por_conceito(coleta):
    p = historico.percurso("P20", [coleta])
    assert p.teve_oportunidade("sizeof")
    assert p.confirmou("sizeof")
    assert not p.teve_oportunidade("funcao_com_parametro")
    assert not p.confirmou("funcao_com_parametro")


def test_quem_so_abriu_o_topico_nao_tem_conceito_do_kc07(coleta):
    """P20 abriu o kc_07 e parou: nenhum conceito dali, porque o kc_07
    não declara cartão nenhum — e porque ele nem viu a abertura."""
    p = historico.percurso("P20", [coleta])
    for ocorrencias in p.apresentados().values():
        for o in ocorrencias:
            assert not o["no"].startswith("kc_07:"), o


# --------------------------------------------------------------------------
# A verificação de entrada: o que o tópico novo vai cobrar
# --------------------------------------------------------------------------

def test_a_verificacao_lista_o_que_o_topico_cobra_sem_oportunidade(coleta):
    """A pergunta que o dono fez: começar pelo kc_06 cobra o quê?

    `funcao_com_parametro` aparece em 23 itens do kc_06 e não está no
    percurso do P20.

    E DESDE 12/11/2026 ELE ESTÁ `disponivel`: o cartão do `kc_06:B1` o
    ensina. A linha continua na lista mesmo assim, e é isso que este
    teste guarda — a lista mede a PESSOA, não o inventário. P20 fez o
    kc_02 e nunca entrou no kc_06; o conceito existir no currículo não
    põe a explicação na frente dele.
    """
    p = historico.percurso("P20", [coleta])
    faltam = historico.sem_oportunidade(p, carrega(topico="kc_06"))
    por_conceito = {c.conceito: c for c in faltam}
    assert "funcao_com_parametro" in por_conceito
    achado = por_conceito["funcao_com_parametro"]
    assert achado.itens == 23, achado
    assert achado.status == "disponivel", achado
    assert achado.oportunidade is False


def test_a_verificacao_nao_reclama_do_que_a_pessoa_viu(coleta):
    """O que ela teve oportunidade de aprender não entra na lista.

    É o que faz do relatório uma medida da PESSOA e não do currículo: se
    a lista fosse igual para todo mundo, ela seria o `test_coerencia`
    outra vez.
    """
    p = historico.percurso("P20", [coleta])
    faltam = historico.sem_oportunidade(p, carrega(topico="kc_02"))
    assert "sizeof" not in {c.conceito for c in faltam}
    assert "derreferencia" not in {c.conceito for c in faltam}


def test_a_verificacao_muda_de_pessoa_para_pessoa(coleta):
    """P20 fez o kc_02; um código novo não fez nada.

    Para o segundo, os conceitos do kc_02 passam a aparecer como sem
    oportunidade — e é exatamente a diferença que o histórico existe
    para mostrar.
    """
    feito = historico.percurso("P20", [coleta])
    zerado = historico.percurso("P98", [coleta])
    d = carrega(topico="kc_11")
    de_quem_fez = {c.conceito for c in historico.sem_oportunidade(feito, d)}
    de_quem_nao = {c.conceito for c in historico.sem_oportunidade(zerado, d)}
    assert de_quem_fez < de_quem_nao, (sorted(de_quem_fez),
                                       sorted(de_quem_nao))
    # `sizeof` é o conceito que o kc_11 cobra e que o kc_02 ensinou. A
    # primeira versão deste teste esperava `derreferencia` aqui e caiu:
    # não existe padrão de varredura para ele, então item nenhum o
    # "cobra" aos olhos de `cobrancas_do_topico`. É limite real da
    # varredura, e o relatório passou a declará-lo.
    assert "sizeof" in de_quem_nao - de_quem_fez


def test_a_verificacao_nao_bloqueia_nada(coleta):
    """Só recomenda, sem cadeado — foi a decisão do dono.

    O relatório não tem veredito: ele devolve uma lista, e quem decide é
    quem conduz. Um campo tipo `pode_entrar` aqui seria o cadeado
    entrando pela porta de trás.
    """
    p = historico.percurso("P98", [coleta])
    faltam = historico.sem_oportunidade(p, carrega(topico="kc_06"))
    assert faltam
    for c in faltam:
        campos = set(c.__dataclass_fields__)
        assert campos == {"conceito", "itens", "status", "oportunidade",
                          "onde"}, campos


# --------------------------------------------------------------------------
# É leitura, e nada mais
# --------------------------------------------------------------------------

def test_a_leitura_nao_toca_o_arquivo(coleta):
    antes = coleta.read_bytes()
    p = historico.percurso("P20", [coleta])
    historico.sem_oportunidade(p, carrega(topico="kc_06"))
    historico.sem_oportunidade(p, carrega(topico="kc_02"))
    assert coleta.read_bytes() == antes


def test_vários_arquivos_somam_no_mesmo_percurso(coleta, tmp_path):
    """Os logs de hoje são um por configuração de lançamento, e o
    percurso de uma pessoa pode estar espalhado entre eles."""
    copia = tmp_path / "outro.jsonl"
    copia.write_text(coleta.read_text(encoding="utf-8"), encoding="utf-8")
    um = historico.percurso("P20", [coleta])
    dois = historico.percurso("P20", [coleta, copia])
    assert len(dois.eventos) == 2 * len(um.eventos)
    assert [u.topico for u in dois.unidades] == ["kc_02", "kc_07"] * 2


def test_linha_ilegivel_nao_derruba_a_leitura(coleta, tmp_path):
    """Mesma tolerância do painel, e pelo mesmo motivo: o relatório
    existe para funcionar depois de um travamento. E ele CONTA as
    puladas, que é o que separa tolerar de esconder."""
    estragado = tmp_path / "estragado.jsonl"
    estragado.write_text(
        coleta.read_text(encoding="utf-8").replace(
            '{"v": 3', '{quebrado', 1) + '{"v": 3, "fim": true}\n',
        encoding="utf-8")
    p = historico.percurso("P20", [estragado])
    assert p.puladas >= 1
    assert p.eventos


def test_arquivo_que_nao_existe_nao_estoura(tmp_path):
    p = historico.percurso("P20", [tmp_path / "nao_existe.jsonl"])
    assert p.unidades == ()
    assert p.puladas == 0


# --------------------------------------------------------------------------
# E o que ele NÃO afirma
# --------------------------------------------------------------------------

def test_o_percurso_nao_inventa_conceito_fora_do_inventario(coleta):
    from mvp import conceitos

    p = historico.percurso("P20", [coleta])
    for mapa in (p.apresentados(), p.diagnosticados(), p.confirmados(),
                 p.revisitados()):
        for cid in mapa:
            assert conceitos.disponivel(cid), cid


def test_o_percurso_guarda_a_sessao_de_cada_evento(coleta):
    """Sem isso o histórico perderia QUANDO: três sessões do mesmo código
    viram uma massa só, e a ordem é o que torna o percurso um percurso."""
    p = historico.percurso("P20", [coleta])
    for e in p.eventos:
        assert e["sessao"] == "P20"
        assert e["tipo"].startswith("conceito_")


def test_o_relatorio_em_texto_diz_o_que_falta(coleta):
    """Uma linha por conceito, para quem conduz a coleta ler no terminal.

    Quem escolhe o tópico hoje é quem sobe o servidor, não o estudante —
    está em `docs/auditoria-travessia.md`. Então a saída é de terminal,
    e não de tela.
    """
    p = historico.percurso("P98", [coleta])
    texto = historico.relatorio(p, carrega(topico="kc_06"))
    assert "P98" in texto
    assert "kc_06" in texto
    assert "funcao_com_parametro" in texto
    # E não promete nada sobre poder ou não entrar.
    for proibido in ("bloqueado", "não pode", "nao pode", "proibido"):
        assert proibido not in texto.lower()


def test_o_relatorio_declara_o_que_a_varredura_nao_ve():
    """Sete dos catorze conceitos não têm padrão de varredura.

    Então para eles a lista de cobranças não diz nada — nem que o tópico
    cobra, nem que não. Omitir isso faria o relatório parecer completo, e
    dizer menos do que se sabe é tolerável; calar que se está dizendo
    menos, não.
    """
    cegos = historico.sem_detector()
    assert "derreferencia" in cegos
    assert "sizeof" not in cegos
    assert len(cegos) == 7, cegos
    texto = historico.relatorio(historico.percurso("P98", []),
                                carrega(topico="kc_06"))
    assert "derreferencia" in texto
    assert "não vê" in texto.lower()
