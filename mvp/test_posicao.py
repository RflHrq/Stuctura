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
