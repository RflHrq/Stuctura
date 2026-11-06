# -*- coding: utf-8 -*-
"""O escorregão: errar a resposta e acertar a razão.

MEDIDO antes de escrever uma linha, nos treze tópicos, com a persona que
erra a camada 1 e marca SEMPRE a razão correta:

    escorregões (1 erro por nó)        79  → payload `errada`, retorno None,
    escorregões (2 erros por nó)      158    79 de 79 e 158 de 158
    o nó volta a ser perguntado      153 de 158, mediana de 3 passos
    como o nó termina (1 erro)        74 `confirmado`, 5 `fragil`
    telas que mostram `vacilou`       NENHUMA

O fluxo não estava quebrado: quem escorrega recebe o mesmo nó na pergunta
seguinte e quase sempre o confirma. Quebrada estava a TELA. A pessoa que
acabou de enunciar a premissa corretamente lia, palavra por palavra:

    "Ainda não. Olhe de novo com calma — a próxima pergunta volta ao
     mesmo ponto de outro jeito."

O mesmo texto de quem tem um mal-entendido. E o `vacilou`, que o motor
calcula, o log grava e o payload do mapa carrega, não era desenhado em
lugar nenhum — nem para o aluno, nem para o pesquisador.

POR QUE FALAR NUMA FASE QUE MEDE. A regra desta suíte é que o diagnóstico
e o reteste ficam calados, e a justificativa dela é literal: *explicar ali
ENSINA no meio da medição*. Nomear um escorregão não ensina — não leva
premissa, não leva crença, não leva figura. O retorno continua `None`, e é
por isso que `test_o_escorregao_nao_leva_texto_do_dominio` é o guarda
estrutural desta fatia: sem retorno, não existe por onde conteúdo passar.

O PRECEDENTE já estava na mesma fase: o falso positivo fala no
diagnóstico desde a Decisão 13, e fala MOSTRANDO texto do domínio. Esta
fatia diz estritamente menos do que aquela.

O CUSTO, medido e registrado: a pessoa fica sabendo que a razão marcada
era a correta, e o mesmo nó volta três passos depois em 153 de 158 casos.
Isso é decisão metodológica, está em `docs/processo.md`, e é um commit
para desfazer.
"""
from __future__ import annotations

import collections

import pytest

from mvp import app as aplicacao
from mvp import log, motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

MEDE = ("diagnostico", "reteste")


@pytest.fixture(autouse=True)
def log_em_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(log, "DESTINO", tmp_path / "eventos.jsonl")
    aplicacao.sessoes.clear()


def _politica(d, mem):
    """Erra a camada 1; a razão decide se aquilo é escorregão ou crença.

    `escorrega_em` é o conjunto de nós em que a razão marcada é a CERTA —
    o escorregão. Nos outros a razão é errada, e aí o diagnóstico detecta
    crença, refuta e leva ao treino. Sem essa mistura não há treino nenhum
    no percurso: quem acerta toda razão nunca produz crença, e um teste
    sobre "o treino continua `errada`" ficaria sem errada de treino para
    olhar. `None` significa "escorrega em todos".
    """
    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa",
                         "descida-fim", "evidencia"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="uma frase")
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "descida":
            return Resposta(escolha=0)
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            alvo = mem["escorrega_em"]
            if alvo is None or mem["no_em_jogo"] in alvo:
                return Resposta(escolha=next(i for i, z in enumerate(razoes)
                                             if z.correta))
            i = next((i for i, z in enumerate(razoes)
                      if not z.correta and z.crenca), None)
            if i is None:
                i = next(i for i, z in enumerate(razoes) if not z.correta)
            return Resposta(escolha=i)
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        mem["no_em_jogo"] = a.no
        na_tela = motor.opcoes_na_tela(estado.semente, a)
        if mem["erros"][a.no] < mem["ate"]:
            mem["erros"][a.no] += 1
            return Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                         if not o.correta))
        return Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                     if o.correta))
    return politica


def percorre(d, monkeypatch, ate=1, escorrega_em=None, limite=1500):
    """A unidade inteira pelo MESMO `_resposta` que a rota chama."""
    monkeypatch.setattr(aplicacao, "dominio", d)
    mem = {"erros": collections.Counter(), "ate": ate,
           "escorrega_em": escorrega_em, "no_em_jogo": ""}
    politica = _politica(d, mem)
    t = motor.inicia(d)
    passos = [(aplicacao._resposta("S", t, None), list(t.eventos))]
    for _ in range(limite):
        if t.tela.tipo == "mapa":
            return passos
        r = politica(t.tela, t.estado)
        t = motor.avanca(d, t.estado, r)
        passos.append((aplicacao._resposta("S", t, r), list(t.eventos)))
    raise AssertionError("a unidade não terminou em %d passos" % limite)


def _escorregoes(passos):
    """(payload, nó) de cada passo em que o motor detectou vacilo."""
    fora = []
    for payload, eventos in passos:
        vac = next((e for e in eventos if e.tipo == "vacilo_detectado"), None)
        if vac is not None:
            fora.append((payload, vac.dados["no"]))
    return fora


# --------------------------------------------------------------------------
# A tela do instante para de dizer a coisa errada
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_todo_escorregao_e_nomeado(topico, monkeypatch):
    """A invariante, nos treze tópicos: 79 de 79 diziam `errada`."""
    d = carrega(topico=topico)
    passos = percorre(d, monkeypatch)
    escorregoes = _escorregoes(passos)
    assert escorregoes, "%s não produziu escorregão nenhum" % topico
    for payload, no in escorregoes:
        assert payload["veredito"] == "escorregao", (
            "%s: o nó %s escorregou e o veredito veio %r"
            % (topico, no, payload["veredito"]))


@pytest.mark.parametrize("topico", topicos())
def test_o_escorregao_nao_leva_texto_do_dominio(topico, monkeypatch):
    """O GUARDA ESTRUTURAL desta fatia.

    O que a regra proíbe na fase que mede é ENSINAR. Sem `retorno` não
    existe caminho por onde premissa, crença ou figura cheguem à tela — a
    frase que o cliente escreve não varia com o conteúdo. Ganhar um
    retorno aqui é a fatia virar outra coisa, e cai neste teste.
    """
    d = carrega(topico=topico)
    for payload, no in _escorregoes(percorre(d, monkeypatch)):
        assert payload["retorno"] is None, (
            "%s: o escorregão do nó %s ganhou retorno: %r"
            % (topico, no, payload["retorno"]))


def test_o_erro_do_treino_continua_errada(monkeypatch):
    """Só o escorregão muda de veredito.

    O escorregão é do DIAGNÓSTICO — é lá que a camada 2 separa vacilo de
    crença. Errar no treino continua sendo `errada`, com a explicação que
    a fatia anterior montou.
    """
    d = carrega(topico="kc_02")
    # Escorrega SÓ no B1: os outros nós produzem crença, refutação e
    # treino, que é onde este teste precisa olhar.
    passos = percorre(d, monkeypatch, ate=2, escorrega_em={"B1"})
    erradas = []
    for payload, eventos in passos:
        reg = next((e for e in eventos if e.tipo == "resposta_registrada"),
                   None)
        if reg and reg.dados["fase"] == "treino" and not reg.dados["correta"]:
            erradas.append(payload)
    assert erradas, "o percurso não produziu errada de treino nenhuma"
    for payload in erradas:
        assert payload["veredito"] == "errada"
        assert payload["retorno"] is not None


def test_o_escorregao_nao_dispara_refutacao(monkeypatch):
    """CS-3, de novo e aqui: o sistema não contesta uma ideia que a pessoa
    acabou de enunciar direito. Nomear o escorregão não pode ter virado
    uma porta para a validação."""
    d = carrega(topico="kc_02")
    passos = percorre(d, monkeypatch)
    for payload, eventos in passos:
        if any(e.tipo == "vacilo_detectado" for e in eventos):
            assert not any(e.tipo == "crenca_detectada" for e in eventos)
            assert payload["tela"]["tipo"] != "validacao"


# --------------------------------------------------------------------------
# Entre artefatos: as três telas
# --------------------------------------------------------------------------

def _web(arquivo):
    import pathlib
    import re

    texto = (pathlib.Path(__file__).resolve().parent / "web" / arquivo
             ).read_text(encoding="utf-8")
    if arquivo.endswith(".html"):
        return re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", texto, flags=re.S)


def test_o_cliente_tem_o_ramo_do_escorregao():
    """Veredito novo que o cliente não conhece cai no `else`, e o `else`
    é justamente a frase que esta fatia veio tirar da frente dessa
    pessoa."""
    js = _web("app.js")
    assert '"escorregao"' in js, (
        "o cliente não conhece o veredito `escorregao`: cai no Ainda não")


def test_o_mapa_final_conta_o_escorregao():
    """O mapa lê `escorregou`, e NÃO `vacilou`.

    A primeira versão desta fatia pôs no mapa o texto "errou a resposta e
    explicou certo" atrás de `vacilou` — e `vacilou` não quer dizer isso.
    Ele é posto no ramo CONFIRMADA, a partir de `bool(en.erros)`: vale
    para quem errou por QUALQUER motivo e depois acertou, inclusive por
    crença. O mapa afirmaria "você explicou certo" a quem explicou
    errado. É o defeito do rótulo fixo, de novo, e foi o navegador que o
    mostrou — este teste não mostrava, porque só procurava a palavra.
    """
    js = _web("app.js")
    assert "n.escorregou" in js, (
        "o mapa continua sem dizer que a pessoa escorregou")


# --------------------------------------------------------------------------
# `escorregou` não é `vacilou`
# --------------------------------------------------------------------------

def _no_do_mapa(payload, no):
    return next(x for x in payload["grafo"]["nos"] if x["no"] == no)


def test_o_no_que_escorregou_fica_marcado(monkeypatch):
    d = carrega(topico="kc_02")
    passos = percorre(d, monkeypatch)
    escorregoes = _escorregoes(passos)
    assert escorregoes
    for payload, no in escorregoes:
        assert _no_do_mapa(payload, no)["escorregou"] is True, (
            "o nó %s escorregou e o mapa não sabe" % no)


def test_confirmar_depois_de_erro_nao_e_escorregao():
    """O teste que separa os dois campos, e por que ele é assim.

    `vacilou` é posto no ramo CONFIRMADA a partir de `bool(en.erros)`:
    "errou uma vez e corrigiu sozinho", qualquer que tenha sido o erro.
    `escorregou` é posto só no ramo FALSO_NEGATIVO. São coisas
    diferentes, e a frase do mapa só pode sair da segunda.

    E AQUI VAI UMA CORREÇÃO MINHA, registrada porque ela muda o que esta
    fatia afirma. Eu disse que o mapa, lendo `vacilou`, mentiria para
    quem errou por crença. Fui medir: varri os treze tópicos com
    dezesseis personas (escorregar em todos / em B1 / em B2 / em nenhum ×
    um ou dois erros por nó × duas confianças) e achei **zero** nós com
    `vacilou` sem escorregão. A crença manda o nó para a refutação, e ele
    não volta pelo ramo CONFIRMADA do diagnóstico.

    Então o campo separado não conserta um defeito observado: ele impede
    um. Por isso este teste não tenta produzir o caso por uma persona que
    não existe — ele CONSTRÓI o estado pela API do próprio motor, põe um
    erro no nó e faz a pessoa acertar. É a única forma honesta de provar
    que os dois campos não são o mesmo campo.
    """
    d = carrega(topico="kc_02")
    t = motor.inicia(d)
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d, t.estado,
                         Resposta(texto="x") if t.tela.tipo == "frase"
                         else Resposta())
    assert t.tela.tipo == "atividade"
    a = next(x for x in d.atividades if x.id == t.tela.dados["atividade"])
    # Um erro anterior naquele nó, sem escorregão nenhum: é o estado que
    # a atribuição cruzada de crença pode deixar para trás.
    e = t.estado.com(a.no, erros=1)
    assert e.no(a.no).escorregou is False

    na_tela = motor.opcoes_na_tela(e.semente, a)
    certa = next(i for i, o in enumerate(na_tela) if o.correta)
    t = motor.avanca(d, e, Resposta(escolha=certa))
    if t.tela.tipo == "razao":
        zs = t.estado.pendente.razoes
        t = motor.avanca(d, t.estado, Resposta(
            escolha=next(i for i, z in enumerate(zs) if z.correta)))
    if t.tela.tipo == "confianca":
        t = motor.avanca(d, t.estado, Resposta(confianca="tenho certeza"))

    en = t.estado.no(a.no)
    assert en.vacilou is True, (
        "o nó tinha erro anterior e confirmou: `vacilou` é o campo disso")
    assert en.escorregou is False, (
        "confirmar depois de um erro virou escorregão: o mapa diria a "
        "essa pessoa que ela explicou certo")


def test_o_painel_nomeia_o_escorregao():
    """A coluna do estado do episódio imprimia a string crua
    `falso_negativo`: o dicionário de nomes do painel só traduzia estado
    de NÓ, e estado de episódio tem vocabulário próprio."""
    html = _web("painel.html")
    assert "falso_negativo:" in html, (
        "o painel continua imprimindo `falso_negativo` cru")
