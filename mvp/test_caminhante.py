# -*- coding: utf-8 -*-
"""A quarta persona do caminhante — a que diz "não sei".

A varredura dos treze tópicos mediu 390 sessões e, em 12 deles, o
`aprende` terminou 100% `confirmado` e o `crente` 100% `em_aberto`.
Nenhum `lacuna` em tópico nenhum. A causa tem uma linha: **nenhuma das
três personas dizia "não sei"** — zero ocorrências de `nao_sei` em
`scripts/caminhante.py`.

A consequência é que a **CS-4** ("não sei" em qualquer camada produz
lacuna, nunca crença) tem 31 asserções na suíte de unidade e nunca rodava
pela TELA. O portão de ponta a ponta produzia os dois extremos do espaço
de estados e nada do meio.

POR QUE A PERSONA ALTERNA entre as camadas, em vez de dizer "não sei"
sempre: um "não sei" na camada 1 ENCERRA o episódio, e as camadas 2 e 3
não são perguntadas. Uma persona que dissesse sempre exercitaria só a
camada 1 — e a camada 2 continuaria sem cobertura pela tela, que é
exatamente o buraco que ela existe para tapar.

A alternância é pelo id da atividade, não por sorteio: o caminhante é um
portão, e portão que muda de resultado sem o código mudar não serve de
portão.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def _caminhante():
    """Carrega `scripts/caminhante.py` como módulo.

    `scripts/` não é pacote, e não vai virar um por causa de um teste.
    """
    spec = importlib.util.spec_from_file_location(
        "caminhante_sob_teste", RAIZ / "scripts" / "caminhante.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cam():
    return _caminhante()


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


@pytest.fixture(scope="module")
def chaves(d):
    return ({a.id: a for a in d.atividades},
            {c.afirma for c in d.crencas.values()},
            {n.texto for n in d.nos.values()}
            | {n.simples for n in d.nos.values()})


def _tela_atividade(d, a, sessao):
    from mvp.motor import opcoes_na_tela
    return {"tipo": "atividade", "atividade": a.id, "fase": "DIAGNOSTICO",
            "opcoes": [{"texto": o.texto} for o in opcoes_na_tela(sessao, a)]}


def _tela_razao(d, a):
    """A camada 2: uma razão é a fala do nó, as outras são crenças."""
    textos = ([d.nos[a.no].texto]
              + [c.afirma for c in d.crencas.values()][:2])
    return {"tipo": "razao", "atividade": a.id,
            "opcoes": [{"texto": x} for x in textos]}


# --------------------------------------------------------------------------
# A persona existe, e as três antigas não mudaram
# --------------------------------------------------------------------------

def test_a_quarta_persona_entra_na_lista(cam):
    assert "nao_sabe" in cam.PERSONAS, cam.PERSONAS


def test_as_tres_personas_antigas_continuam_na_lista(cam):
    """Persona nova não pode custar persona velha: os números da varredura
    dos treze foram medidos com estas três, e comparar depois exige que
    elas respondam igual."""
    for p in ("sabido", "aprende", "crente"):
        assert p in cam.PERSONAS, p


def test_a_persona_nova_tem_frase_de_teachback(cam):
    """`caminha` indexa `FRASES[persona]` — persona sem frase estoura com
    KeyError no meio da sessão, e não na lista."""
    assert "nao_sabe" in cam.FRASES
    assert set(cam.FRASES["nao_sabe"]) == {"inicio", "fim"}


def test_as_antigas_continuam_devolvendo_indice(cam, d, chaves):
    """A trava da regressão: nenhuma das três antigas pode passar a
    devolver o sinal de "não sei"."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    for persona in ("sabido", "aprende", "crente"):
        for tela in (_tela_atividade(d, a, "P01"), _tela_razao(d, a)):
            i = cam.escolhe(tela, persona, chaves, "P01")
            assert isinstance(i, int), (persona, tela["tipo"], i)


# --------------------------------------------------------------------------
# O "não sei", nas duas camadas
# --------------------------------------------------------------------------

def test_nao_sabe_diz_nao_sei_na_camada_2_sempre(cam, d, chaves):
    """A camada 2 é a que estava descoberta pela tela, e é onde a razão
    errada seria lida como CRENÇA. A CS-4 manda produzir lacuna."""
    for a in d.atividades:
        tela = _tela_razao(d, a)
        assert cam.escolhe(tela, "nao_sabe", chaves, "P01") == cam.NAO_SEI, a.id


def test_nao_sabe_diz_nao_sei_na_camada_1_em_parte_dos_itens(cam, d, chaves):
    """E responde na outra parte, de propósito.

    Se dissesse "não sei" em toda camada 1, o episódio encerraria ali
    sempre e a camada 2 nunca seria alcançada — a persona não cobriria o
    buraco que justifica a existência dela.
    """
    disse, respondeu = [], []
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        r = cam.escolhe(tela, "nao_sabe", chaves, "P01")
        (disse if r == cam.NAO_SEI else respondeu).append(a.id)
    assert disse, "nenhum item leva nao_sei na camada 1"
    assert respondeu, "todo item leva nao_sei: a camada 2 fica inalcancavel"


def test_a_alternancia_e_estavel_e_nao_sorteada(cam, d, chaves):
    """Portão que muda de resultado sem o código mudar não é portão.

    A primeira versão deste teste fixava UM item e repetia a chamada — e
    passava **antes** da persona existir, porque `escolhe` já era
    determinístico para qualquer persona desconhecida. Teste que passa sem
    a implementação não prova a implementação.

    O que prende de verdade é o CONJUNTO: quais itens levam "não sei" tem
    de ser o mesmo conjunto a cada rodada, e não pode ser vazio nem
    completo — as duas pontas que tornariam a camada 1 ou a camada 2
    inalcançável.
    """
    def conjunto():
        return frozenset(
            a.id for a in d.atividades
            if cam.escolhe(_tela_atividade(d, a, "P01"), "nao_sabe",
                           chaves, "P01") == cam.NAO_SEI)

    primeiro = conjunto()
    assert primeiro, "nenhum item leva nao_sei"
    assert len(primeiro) < len(d.atividades), "todos levam nao_sei"
    for _ in range(5):
        assert conjunto() == primeiro


def test_quando_responde_a_camada_1_ela_erra(cam, d, chaves):
    """Quem não sabe não acerta por sorte.

    Se a persona acertasse a camada 1 e só titubeasse na razão, ela
    produziria falso positivo e não o `lacuna` que falta.
    """
    from mvp.motor import indice_correto_na_tela
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        r = cam.escolhe(tela, "nao_sabe", chaves, "P01")
        if r != cam.NAO_SEI:
            assert r != indice_correto_na_tela("P01", a), a.id


# --------------------------------------------------------------------------
# O defeito que a quarta persona descobriu, e que é das TRÊS ANTIGAS
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_nenhuma_persona_que_deve_errar_escolhe_a_certa(cam, topico):
    """`None == None`, e a persona que devia errar acertava.

    O caminho de quem não está convencido procurava a alternativa cuja
    crença é a do item:

        next(i for i, o in enumerate(na_tela) if o.crenca == a.crenca)

    Quando `a.crenca` é `None` — e três itens dos 562 são assim — a
    comparação casa a alternativa cuja crença também é `None`, que é
    justamente **a certa**. A persona que existe para errar acertava, de
    propósito nenhum.

    Por que isso não é detalhe: um dos três é item de DIAGNÓSTICO
    (`ciu_kc00_001`). Ali o `crente` acerta, nenhuma crença é detectada,
    a refutação não acontece — e se ele depois escolhe uma crença como
    razão, o episódio sai `falso_positivo`. Foi exatamente o que a
    varredura dos treze mediu no kc_00, e eu li como propriedade do
    tópico. Era artefato do portão.

    É a classe de defeito que este projeto chama de plausível e errado: o
    portão rodava verde e media outra coisa.
    """
    d = carrega(topico=topico)
    chaves = ({a.id: a for a in d.atividades},
              {c.afirma for c in d.crencas.values()},
              {n.texto for n in d.nos.values()}
              | {n.simples for n in d.nos.values()})
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        certo = motor.indice_correto_na_tela("P01", a)
        for persona in ("aprende", "crente", "nao_sabe"):
            r = cam.escolhe(tela, persona, chaves, "P01")
            if r == cam.NAO_SEI:
                continue
            assert r != certo, (topico, a.id, persona, a.crenca)


# --------------------------------------------------------------------------
# O `sem_medida` do portão passa a contar os estados não-terminais
# --------------------------------------------------------------------------

def test_sem_medida_conta_refutado_e_em_treino(cam):
    """O defeito que a varredura expôs sem ser mordida por ele.

    `sem_medida` contava `desconhecido` e `nao_medido`. Mas `refutado`
    (crença detectada, ainda não trabalhada) e `em_treino` (falta fechar
    a sequência) também são fim de sessão QUEBRADO: a premissa não chegou
    a nenhum dos estados que a CS-10 promete. Um portão que diz "0 sem
    medida" numa sessão parada no meio da refutação mente com a verdade.
    """
    nos = [{"no": "B1", "estado": "confirmado"},
           {"no": "B2", "estado": "refutado"},
           {"no": "B3", "estado": "em_treino"},
           {"no": "I1", "estado": "desconhecido"},
           {"no": "I2", "estado": "nao_medido"},
           {"no": "I3", "estado": "em_aberto"}]
    assert cam.sem_medida(nos) == ["B2", "B3", "I1", "I2"]


def test_em_aberto_e_confirmado_nao_contam_como_sem_medida(cam):
    """`em_aberto` É medida — o banco acabou, e o projeto decidiu que isso
    é um estado, não uma lacuna de instrumento (ver `test_medida.py`).
    Contá-lo aqui faria o portão acusar o pior caso roteirizado."""
    nos = [{"no": "B1", "estado": "em_aberto"},
           {"no": "B2", "estado": "confirmado"},
           {"no": "B3", "estado": "lacuna"},
           {"no": "I1", "estado": "fragil"},
           {"no": "I2", "estado": "falso_positivo"}]
    assert cam.sem_medida(nos) == []
