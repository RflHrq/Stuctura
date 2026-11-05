"""A posição da alternativa certa.

Nos 562 itens dos treze tópicos, a resposta certa estava na **primeira**
alternativa em 553 deles — 98,4%. Isso não é detalhe de apresentação: o
instrumento passa a medir, em parte, quem reparou no padrão, e o viés é
sistemático, então não some na média de 40 participantes.

Pior: ele contamina a medida central do trabalho. Quem acerta por posição
ainda escolhe uma razão, e o par sai "acerto com razão errada" — que o
CS-1 lê como falso positivo. O viés produziria falsos positivos em massa,
e eles pareceriam achado.

A permutação já existia no motor, escrita para a camada das razões
(`ordem_das_razoes`). A camada 1 ficou de fora, e os 98,4% são a
consequência disso. O desenho está em [../docs/posicao.md](../docs/posicao.md).
"""

from __future__ import annotations

import collections

import pathlib

import pytest

from mvp import motor
from mvp.dominio import carrega

D = carrega(topico="kc_07")


@pytest.fixture(scope="module")
def d():
    return D


# --------------------------------------------------------------------------
# A permutação
# --------------------------------------------------------------------------

def test_a_ordem_e_estavel(d):
    a = d.atividades[0]
    assert (motor.ordem_das_opcoes("P01", a.id, 3)
            == motor.ordem_das_opcoes("P01", a.id, 3))


def test_a_ordem_e_uma_permutacao(d):
    for n in (2, 3, 4):
        assert sorted(motor.ordem_das_opcoes("P01", "x", n)) == list(range(n))


def test_sementes_diferentes_dao_ordens_diferentes(d):
    """O que mata o vazamento entre participantes: o P03 contar ao P04
    que "a do array é a terceira" não transfere."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    ordens = {motor.ordem_das_opcoes("P%02d" % i, a.id, 3) for i in range(1, 41)}
    assert len(ordens) > 1, ordens


def test_a_semente_vazia_nao_devolve_a_ordem_do_arquivo(d):
    """Sessão sem código não é desculpa para o viés voltar."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    assert motor.ordem_das_opcoes("", a.id, 3) != (0, 1, 2)


def test_as_duas_camadas_nao_recebem_a_mesma_permutacao(d):
    """Se recebessem, a posição da resposta prediria a posição da razão —
    um segundo viés no lugar do primeiro. Medido no banco inteiro: duas
    funções iguais dariam 100%."""
    tres = [x for x in d.atividades if len(x.opcoes) == 3]
    iguais = sum(motor.ordem_das_opcoes("P01", x.id, 3)
                 == motor.ordem_das_razoes("P01", x.id, 3) for x in tres)
    assert iguais < len(tres) * 0.5, (iguais, len(tres))


def test_itens_diferentes_podem_coincidir(d):
    """Contraprova: colisão de digest entre itens é esperada e inofensiva.
    Nenhum teste pode exigir que ordens de itens diferentes difiram."""
    tres = [x for x in d.atividades if len(x.opcoes) == 3]
    ordens = [motor.ordem_das_opcoes("P01", x.id, 3) for x in tres]
    assert len(set(ordens)) <= 6, "são 6 permutações possíveis para n=3"


def test_o_indice_certo_na_tela_aponta_a_alternativa_certa(d):
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    ordem = motor.ordem_das_opcoes("P01", a.id, 3)
    i = motor.indice_correto_na_tela("P01", a)
    assert a.opcoes[ordem[i]].correta


def test_a_escala_de_confianca_nao_e_embaralhada():
    """Fronteira de escopo, pinada. `CONFIANCAS` é ORDINAL: a ordem dela
    É a escala, e embaralhar destruiria a leitura. Além disso o viés nem
    existe ali, porque nenhuma das três é a certa."""
    assert motor.CONFIANCAS == ("chutei", "acho que sei", "tenho certeza")


# --------------------------------------------------------------------------
# A trava contra o erro silencioso
# --------------------------------------------------------------------------

def test_nao_existe_mais_indice_correto_sem_qualificacao(d):
    """A trava desta fatia.

    O nome antigo dizia "a posição da certa", e essa pergunta passou a
    ter duas respostas: no arquivo e na tela. Enquanto ele existir, as
    22 chamadas continuam executando e querendo dizer a errada — e o
    motor ACEITA o índice: não é erro de programa, é uma resposta
    errada. A escada desce em vez de subir, a crença errada é
    registrada, e a suíte fica verde contando outra história.

    Renomear troca 22 erros silenciosos por 22 `AttributeError`.
    """
    a = d.atividades[0]
    # O nome velho, escrito por partes: uma renomeação em massa pelo
    # arquivo inteiro já o comeu aqui uma vez, e o teste passou a dizer
    # o contrário do que foi escrito para dizer.
    velho = "indice_" + "correto"
    assert not hasattr(a, velho)
    assert isinstance(a.indice_correto_no_arquivo, int)


# --------------------------------------------------------------------------
# A permutação ligada: pelas ROTAS, porque é o único jeito de pegar o
# desencontro entre o que foi mostrado e o que foi lido
# --------------------------------------------------------------------------

@pytest.fixture
def cliente(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from mvp import app as aplicacao
    from mvp import log

    monkeypatch.setattr(log, "DESTINO", tmp_path / "eventos.jsonl")
    aplicacao.sessoes.clear()
    with TestClient(aplicacao.app) as c:
        yield c


@pytest.fixture
def dapp():
    """O domínio QUE O SERVIDOR carregou, e não o do módulo: estes testes
    falam com as rotas, e o banco delas é o do tópico configurado."""
    from mvp import app as aplicacao

    return aplicacao.dominio


def _ate_a_atividade(c, codigo=""):
    """Abre a sessão e avança até a primeira tela de atividade."""
    j = c.post("/sessoes", json={"codigo": codigo} if codigo else None).json()
    sessao = j["sessao"]
    for _ in range(12):
        if j["tela"]["tipo"] == "atividade":
            return sessao, j["tela"]
        j = c.post("/sessoes/%s/responder" % sessao,
                   json={"texto": "x", "ms": 100}).json()
    raise AssertionError("não cheguei à atividade em 12 passos")


def _posicao_da_certa_na_tela(tela, a):
    """A posição lida DA TELA, pelo texto — nunca pela permutação.

    Um teste que chama a permutação dos dois lados concorda consigo
    mesmo mesmo quando está errado. A tela entrega textos; é por eles
    que se descobre onde a certa ficou.
    """
    certa = a.opcoes[a.indice_correto_no_arquivo].texto
    return [o["texto"] for o in tela["opcoes"]].index(certa)


def test_o_indice_clicado_julga_o_texto_que_estava_ali(cliente, dapp):
    """O único teste que pega o desencontro entre o que foi mostrado e o
    que foi lido. A tela entrega TEXTOS; a pessoa clica numa POSIÇÃO."""
    sessao, tela = _ate_a_atividade(cliente, "P01")
    textos = [o["texto"] for o in tela["opcoes"]]
    a = next(x for x in dapp.atividades if x.id == tela["atividade"])
    i = _posicao_da_certa_na_tela(tela, a)

    depois = cliente.post("/sessoes/%s/responder" % sessao,
                          json={"escolha": i, "ms": 100}).json()["tela"]
    # `trancada` repete o texto da alternativa escolhida, e sai de
    # `_pede_confianca`: é ali que o desencontro aparece.
    assert depois["tipo"] in ("razao", "confianca"), depois["tipo"]
    assert depois["trancada"] == textos[i]


def test_a_certa_nao_fica_sempre_na_primeira(cliente, dapp):
    """A prova, PELA TELA, de que a fatia resolveu o que a motivou.

    A posição sai dos textos que a rota devolveu. Lê-la da permutação
    faria o teste passar sem nada ligado — ele concordaria consigo
    mesmo enquanto a tela continuasse entregando a ordem do arquivo.
    """
    posicoes = set()
    for codigo in ("P01", "P02", "P03", "P04", "P05", "P06"):
        _, tela = _ate_a_atividade(cliente, codigo)
        a = next(x for x in dapp.atividades if x.id == tela["atividade"])
        posicoes.add(_posicao_da_certa_na_tela(tela, a))
    assert len(posicoes) > 1, posicoes


def test_escolha_fora_de_faixa_continua_recusada(cliente):
    """`opcoes[-1]` é válido em Python, e já foi defeito aqui
    (test_entrada.py:4). Agora há um segundo índice no caminho: a
    validação vem ANTES da permutação, ou o erro vira `IndexError`."""
    sessao, tela = _ate_a_atividade(cliente, "P01")
    for ruim in (-1, len(tela["opcoes"]), 99):
        r = cliente.post("/sessoes/%s/responder" % sessao,
                         json={"escolha": ruim, "ms": 100})
        assert r.status_code == 400, (ruim, r.status_code)


def test_o_item_reapresentado_volta_na_mesma_ordem(d):
    """É a mesma pergunta: a pessoa pode raciocinar "a primeira eu já
    descartei".

    No MOTOR, e não pelas rotas: a reapresentação só acontece no treino,
    quando o banco do nó esgota, e chegar lá pelo HTTP custa dezenas de
    passos sem provar nada a mais. A afirmação é sobre as ENTRADAS da
    permutação — ela não depende de quantas vezes o item já apareceu —,
    e é aí que ela se prova.
    """
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    t1 = motor._apresenta(d, motor.inicia(d, semente="P01").estado, a)
    t2 = motor._apresenta(d, t1.estado, a, reapresentada=True)
    assert t2.tela.dados["opcoes"] == t1.tela.dados["opcoes"]
    assert any(e.tipo == "item_reapresentado" for e in t2.eventos)


# --------------------------------------------------------------------------
# O log, e a versão
# --------------------------------------------------------------------------

def _grava_ate_a_atividade(d, caminho, semente):
    """Roda a sessão no motor até a primeira atividade, gravando tudo."""
    from mvp import log

    t = motor.inicia(d, semente=semente)
    log.grava(semente, t.eventos, caminho)
    for _ in range(12):
        if t.tela.tipo == "atividade":
            return t
        r = motor.Resposta(texto="x", ms=100)
        t = motor.avanca(d, t.estado, r)
        log.grava(semente, t.eventos, caminho, entrada=r)
    raise AssertionError("não cheguei à atividade")


def _escreve_log(caminho, sessao, *, v, topico, entradas):
    """Um log à mão, para a versão que o código de hoje não grava mais."""
    import json

    from mvp import log

    linhas = []
    for tipo, dados in [("unidade_iniciada", {"topico": topico})] + [
            (log.ENTRADA, x) for x in entradas]:
        linha = {"ts": log.agora(), "sessao": sessao, "tipo": tipo, **dados}
        if v is not None:
            linha = {"v": v, **linha}
        linhas.append(json.dumps(linha, ensure_ascii=False))
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def test_a_ordem_mostrada_vai_para_o_log(d, tmp_path):
    """Redundante para o CS-6 e não para a análise: com o campo, o viés
    residual é medível no próprio dado, e uma mudança futura na função
    não reescreve o que os participantes viram."""
    from mvp import log

    caminho = tmp_path / "eventos.jsonl"
    _grava_ate_a_atividade(d, caminho, "P01")
    linha = next(x for x in log.le("P01", caminho)
                 if x["tipo"] == "atividade_apresentada")
    a = next(x for x in d.atividades if x.id == linha["atividade"])
    assert linha["ordem"] == list(
        motor.ordem_das_opcoes("P01", a.id, len(a.opcoes)))


def test_a_versao_subiu_porque_o_indice_mudou_de_significado():
    """A regra está escrita no próprio `log.py`: "sobe quando o
    significado de uma linha muda, não quando o código muda". Um índice
    em `entrada_recebida` deixou de querer dizer "posição no YAML" e
    passou a querer dizer "posição na tela".

    Este teste cobrava `VERSAO == 2`, e a v3 o derrubou — pelo motivo
    certo: a descida passou a distinguir declarar desconhecimento de
    manter a crença, e `escolha: "decorre"` virou `declarado:
    "mantenho"`. Fixar o número prendia a versão de UMA fatia, quando o
    que esta fatia garante é que a mudança da camada 1 TEM uma versão
    própria e que nada anterior a ela reexecuta.
    """
    from mvp import log

    assert log.VERSAO >= 2, "a versão da permutação não pode sumir"
    # e a razão dela continua escrita, para quem for ler o histórico
    fonte = pathlib.Path(log.__file__).read_text(encoding="utf-8")
    assert "posição na tela" in fonte


def test_sessao_v1_e_RECUSADA(d, tmp_path):
    """Não há semente que reexecute um `v1`, e tentar produz o estado
    plausível e errado que o `LogIncompleto` existe para impedir.

    Eu tinha escrito `semente=""` aqui, raciocinando que a camada 1 não
    era permutada no `v1`. Está errado por dois lados, e os dois foram
    medidos:

    - a semente vazia **não** é a identidade: ela devolve a ordem do
      arquivo em só 18% dos itens. Nos outros 82% o índice gravado é
      lido contra uma permutação que ninguém viu, e um acerto vira erro
      com uma crença atribuída que a pessoa nunca escolheu;
    - no `v1` as razões **já eram** permutadas, com a sessão como
      semente. Passar `""` conserta uma camada que não estava quebrada
      e quebra outra que estava certa.

    Nenhuma semente serve para as duas ao mesmo tempo. Recusar é a única
    resposta honesta, e é a que a spec já previa.
    """
    from mvp import log

    caminho = tmp_path / "v1.jsonl"
    _escreve_log(caminho, "S1", v=1, topico=d.id,
                 entradas=[{"escolha": 0, "ms": 100}])
    with pytest.raises(log.LogIncompleto) as erro:
        log.reconstroi(d, "S1", caminho)
    assert "1" in str(erro.value) and "2" in str(erro.value), str(erro.value)


def test_linha_sem_campo_v_tambem_e_recusada(d, tmp_path):
    """`VERSAO_ZERO`, do ciclo 1: caso distinto de `v1`, mesma recusa.
    Linha sem o campo não pode cair no ramo da permutação por omissão."""
    from mvp import log

    caminho = tmp_path / "v0.jsonl"
    _escreve_log(caminho, "S0", v=None, topico=d.id,
                 entradas=[{"escolha": 0, "ms": 100}])
    with pytest.raises(log.LogIncompleto):
        log.reconstroi(d, "S0", caminho)


def test_sessao_v2_reexecuta_a_RESPOSTA_e_nao_so_a_semente(d, tmp_path):
    """O teste que faltava, e que escondeu tudo isto.

    Eu tinha afirmado `t.estado.semente == "P01"` — um campo de
    implementação, que é verdade mesmo quando a reexecução devolve outra
    resposta. O que o CS-6 promete é o ESTADO: responder certo, gravar,
    reexecutar e encontrar o mesmo acerto.
    """
    from mvp import log

    caminho = tmp_path / "v2.jsonl"
    t = _grava_ate_a_atividade(d, caminho, "P01")
    a = next(x for x in d.atividades if x.id == t.estado.atividade)
    r = motor.Resposta(escolha=motor.indice_correto_na_tela("P01", a), ms=100)
    t = motor.avanca(d, t.estado, r)
    log.grava("P01", t.eventos, caminho, entrada=r)

    volta = log.reconstroi(d, "P01", caminho)
    assert volta is not None
    assert volta.estado.pendente.correta is True, "o acerto tem de voltar acerto"
    assert volta.estado == t.estado


# --------------------------------------------------------------------------
# A medida do viés — a prova direta de que a fatia resolveu o que a
# motivou. As outras provam o mecanismo.
# --------------------------------------------------------------------------

def _todos_os_itens():
    """Os 562 itens dos treze tópicos, e não só os do kc_07."""
    import pathlib
    import re

    from mvp.dominio import RAIZ

    itens = []
    for f in sorted(pathlib.Path(RAIZ).glob("activities_kc*.yaml")):
        m = re.match(r"activities_kc(\d+)", f.name)
        itens += carrega(topico="kc_%s" % m.group(1)).atividades
    return itens


def test_o_vies_de_posicao_acabou():
    """Antes: 553 de 562 com a certa na primeira — 98,4%.

    A medida é POR ITEM, ao longo de 40 sementes (uma por participante
    do piloto), porque o confundimento é ENTRE participantes. Entre
    itens não funcionaria: 13 dos 562 têm duas alternativas, `n=2` tem
    duas permutações, e metade das sementes devolve a identidade.

    O limite, e não o número: número cravado é a recorrência de um
    defeito de teste que este projeto já catalogou cinco vezes.
    """
    sementes = ["P%02d" % i for i in range(1, 41)]
    piores = []
    for a in _todos_os_itens():
        k = len(a.opcoes)
        c = collections.Counter(
            motor.indice_correto_na_tela(s, a) for s in sementes)
        assert set(c) == set(range(k)), (a.id, k, dict(c))
        piores.append(max(c.values()) / (len(sementes) / k))
    # A AFIRMAÇÃO É SOBRE O BANCO, não sobre o pior item.
    #
    # A primeira versão deste teste cobrava `max <= n/k * 1.8` por item.
    # O 1.8 não era princípio nenhum: era o menor multiplicador que o
    # banco de hoje aceita — o pior item bate EXATAMENTE no limite, com
    # zero folga, e um item novo no YAML daria vermelho sem defeito.
    # Pior, o limite é mais apertado do que o acaso permite: num sorteio
    # uniforme de verdade, com 549 itens e 40 sementes, o máximo dos
    # máximos passa de 24 em cerca de 1 de 5 vezes.
    #
    # O que o acaso NÃO produz é um banco inteiro deslocado. Então a
    # medida é a média — que concentra, e cujo limite não depende de
    # quantos itens existem.
    media = sum(piores) / len(piores)
    assert media < 1.35, media


def test_o_banco_inteiro_numa_sessao_nao_concentra():
    """A visão de UM participante: na sessão dele, a certa não fica na
    primeira posição mais do que o acaso. É a medida que estava em
    98,4%, agora pela permutação.

    Só os de três alternativas: nos 13 de duas, metade das sementes
    devolve a identidade, e misturar os dois grupos mede ruído.
    """
    tres = [a for a in _todos_os_itens() if len(a.opcoes) == 3]
    assert len(tres) > 500, len(tres)
    c = collections.Counter(
        motor.indice_correto_na_tela("P01", a) for a in tres)
    assert set(c) == {0, 1, 2}, dict(c)
    assert max(c.values()) <= len(tres) / 3 * 1.3, dict(c)



# --------------------------------------------------------------------------
# As duas pontas que a mutação atravessou: a ESCRITA da entrada e o
# `_pede_confianca`. Trocar `e.semente` por lixo nelas deixava a suíte
# inteira verde.
# --------------------------------------------------------------------------

def test_a_tela_da_entrada_sai_na_ordem_da_tela(d):
    """Ponta 2, a escrita da entrada.

    Nenhum teste lia os TEXTOS que essa tela entrega — só a leitura irmã
    era coberta, e por um teste que chama a permutação dos dois lados.
    Se a tela da entrada passasse a ser desenhada com uma ordem enquanto
    `_responde_entrada` lê com outra, a pessoa seria julgada pela
    alternativa errada com a suíte verde.
    """
    no = d.ordem[0]
    item = d.entrada(no, ())
    assert item is not None, "o nó %s não tem item de entrada" % no
    e = motor.replace(motor.inicia(d, semente="P01").estado, construindo=no)
    tela = motor._segue_construcao(d, e).tela

    assert tela.dados["atividade"] == item.id
    assert ([o["texto"] for o in tela.dados["opcoes"]]
            == [o.texto for o in motor.opcoes_na_tela("P01", item)])


def test_a_confianca_repete_a_alternativa_que_a_pessoa_marcou(d):
    """Ponta 6.

    O campo `resposta` é a última coisa que a pessoa lê antes de dizer
    quanta confiança tem "nessa dupla". Mostrar ali outra alternativa
    não corrompe log nenhum — corrompe a MEDIDA, porque a confiança
    passa a ser sobre um par que não é o dela.

    O teste que existia só conferia que o campo não estava vazio.
    """
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    e = motor.inicia(d, semente="P01").estado
    na_tela = motor.opcoes_na_tela("P01", a)
    for escolhido in range(3):
        p = motor.Pendente(atividade=a.id, escolha=escolhido,
                           correta=na_tela[escolhido].correta,
                           crenca_da_opcao=na_tela[escolhido].crenca, ms=100)
        tela = motor._pede_confianca(d, e, a, p).tela
        assert tela.dados["resposta"] == na_tela[escolhido].texto, escolhido
