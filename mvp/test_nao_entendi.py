# -*- coding: utf-8 -*-
"""O cartão de ensino ganha "ainda não entendi".

O DEFEITO, achado lendo o markup: o cartão de ensino tinha UM botão.

    <button class="btn" id="btn-ensino">Entendi</button>

O único lugar do sistema onde alguém podia dizer que não entendeu era a
refutação (`btn-refutacao-nao`) — e a refutação só acontece para quem
**tem uma crença**. Quem não sabe nada lê o cartão e a única coisa que
pode fazer é afirmar que entendeu.

Isso é pior do que falta de recurso: é o sistema colhendo "Entendi" de
gente que não entendeu, e `forca()` descontando ponto por reexplicação
(`pontos -= en.reexplicacoes`) de um contador que, para esse público,
nunca saía de zero.

O MECANISMO JÁ EXISTIA INTEIRO: `Resposta.repetir`, `LIMITE_REEXPLICACAO
= 2`, `EstadoNo.reexplicacoes`, `Estado.repeticoes` e o evento
`premissa_reapresentada`. Esta fatia não inventa nada — liga o que a
refutação já usava na tela de ensino, com o mesmo teto e o mesmo log.

O QUE MUDA NA SEGUNDA VEZ, e é pouco de propósito: no cartão de ABERTURA
a analogia de resgate não é mostrada, e passa a ser. No cartão de lacuna
ela já aparece de primeira, junto com figura, exemplo e ampliação — ali
repetir reapresenta o mesmo. Fazer a segunda vez ser DIFERENTE é a fatia
seguinte (segunda construção com material diferente); misturar as duas
faria esta prometer o que não entrega.
"""
from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos
from mvp.motor import LIMITE_REEXPLICACAO, Resposta

D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d2():
    return D2


def _ate_a_construcao(d, semente="NE"):
    """Uma sessão até a tela de construção, que é a de quem disse que não
    sabe. Declara lacuna na primeira atividade."""
    t = motor.inicia(d, semente=semente)
    for _ in range(60):
        tela = t.tela
        if tela.tipo == "ensino" and tela.dados.get("motivo") == "lacuna":
            return t
        if tela.tipo == "frase":
            r = Resposta(texto="nao sei")
        elif tela.tipo == "atividade":
            r = Resposta(nao_sei=True)
        elif tela.tipo == "confianca":
            r = Resposta(confianca="chutei")
        elif tela.tipo == "razao":
            r = Resposta(nao_sei=True)
        else:
            r = Resposta()
        t = motor.avanca(d, t.estado, r)
    raise AssertionError("não cheguei à construção")


# --------------------------------------------------------------------------
# O recurso existe
# --------------------------------------------------------------------------

def test_o_cartao_diz_que_da_para_nao_entender(d2):
    """Sem este campo o cliente não tem como saber se pode oferecer o
    botão — e a refutação já manda o mesmo campo."""
    t = _ate_a_construcao(d2)
    assert t.tela.dados.get("pode_repetir") is True


def test_o_cartao_de_abertura_tambem_oferece(d2):
    """A abertura ensina três cartões em sequência, e também não tinha
    como dizer que não entendeu."""
    t = motor.inicia(d2)
    t = motor.avanca(d2, t.estado, Resposta(texto="uma frase"))
    assert t.tela.tipo == "ensino"
    assert t.tela.dados.get("pode_repetir") is True


# --------------------------------------------------------------------------
# O que repetir faz
# --------------------------------------------------------------------------

def test_nao_entendi_reapresenta_a_mesma_premissa(d2):
    t = _ate_a_construcao(d2)
    no = t.tela.no
    depois = motor.avanca(d2, t.estado, Resposta(repetir=True))
    assert depois.tela.tipo == "ensino" and depois.tela.no == no, (
        "o percurso andou: pedir de novo não é responder")
    assert any(ev.tipo == "premissa_reapresentada" for ev in depois.eventos)


def test_a_reexplicacao_fica_registrada_no_no(d2):
    """`forca()` desconta ponto por reexplicação. O contador precisa subir,
    senão a premissa parece mais firme do que está."""
    t = _ate_a_construcao(d2)
    no = t.tela.no
    antes = t.estado.no(no).reexplicacoes
    depois = motor.avanca(d2, t.estado, Resposta(repetir=True))
    assert depois.estado.no(no).reexplicacoes == antes + 1


def test_a_abertura_revela_a_analogia_na_segunda_vez(d2):
    """No cartão de abertura o resgate não aparece; pedir de novo traz a
    mesma afirmação por outro caminho. É o que a refutação já faz."""
    t = motor.inicia(d2)
    t = motor.avanca(d2, t.estado, Resposta(texto="uma frase"))
    assert not t.tela.dados.get("reexplicacao")
    depois = motor.avanca(d2, t.estado, Resposta(repetir=True))
    assert depois.tela.dados.get("reexplicacao"), (
        "a segunda vez não trouxe nada novo")
    # O CAMPO QUE FALTAVA, e a primeira versão desta fatia não o mandava:
    # o cliente desenha UM elemento para a analogia, e sem `resgate` ele
    # não tinha texto para pôr nele. O motor passava no teste e a tela
    # não mudava nada — conferido no navegador, não aqui.
    assert depois.tela.dados.get("resgate"), (
        "o cartão não manda a analogia: o cliente não tem o que desenhar")


# --------------------------------------------------------------------------
# O teto, e a unidade continuar terminando
# --------------------------------------------------------------------------

def test_o_teto_e_respeitado(d2):
    t = _ate_a_construcao(d2)
    for _ in range(LIMITE_REEXPLICACAO):
        t = motor.avanca(d2, t.estado, Resposta(repetir=True))
    assert t.tela.dados.get("pode_repetir") is False, (
        "ofereceu repetir além do teto de %d" % LIMITE_REEXPLICACAO)


def test_estourar_o_teto_segue_e_o_log_diz(d2):
    """Insistir uma terceira vez na mesma frase não ensina. O percurso
    anda, e o log registra que aquela premissa ficou sem fechar."""
    t = _ate_a_construcao(d2)
    no = t.tela.no
    for _ in range(LIMITE_REEXPLICACAO):
        t = motor.avanca(d2, t.estado, Resposta(repetir=True))
    depois = motor.avanca(d2, t.estado, Resposta(repetir=True))
    assert any(ev.tipo == "premissa_nao_fechou" and ev.dados.get("no") == no
               for ev in depois.eventos), [ev.tipo for ev in depois.eventos]
    assert not (depois.tela.tipo == "ensino" and depois.tela.no == no), (
        "estourou o teto e continuou na mesma tela: a unidade não termina")


def test_o_contador_zera_ao_mudar_de_cartao(d2):
    """Senão o teto do primeiro nó fecha a porta do segundo."""
    t = motor.inicia(d2)
    t = motor.avanca(d2, t.estado, Resposta(texto="uma frase"))
    t = motor.avanca(d2, t.estado, Resposta(repetir=True))
    assert t.estado.repeticoes == 1
    seguinte = motor.avanca(d2, t.estado, Resposta())     # "Entendi"
    assert seguinte.estado.repeticoes == 0


@pytest.mark.parametrize("topico", topicos())
def test_quem_nunca_entende_termina_a_unidade(topico):
    """A trava de segurança desta fatia.

    Uma persona que responde "ainda não entendi" em TODA tela de ensino e
    "não sei" em toda atividade tem de chegar ao mapa. Sem o teto, este
    teste roda para sempre — e é por isso que ele existe.
    """
    d = carrega(topico=topico)
    t = motor.inicia(d)
    vistos = 0
    for _ in range(1200):
        tela = t.tela
        if tela.tipo == "mapa":
            assert vistos, "%s: nunca pediu reexplicação" % topico
            return
        if tela.tipo == "ensino":
            vistos += 1
            r = Resposta(repetir=True)
        elif tela.tipo == "frase":
            r = Resposta(texto="nao sei")
        elif tela.tipo == "atividade":
            r = Resposta(nao_sei=True)
        elif tela.tipo == "confianca":
            r = Resposta(confianca="chutei")
        elif tela.tipo == "razao":
            r = Resposta(nao_sei=True)
        else:
            r = Resposta()
        t = motor.avanca(d, t.estado, r)
    raise AssertionError("%s: a unidade não terminou — teto furado" % topico)


# --------------------------------------------------------------------------
# Entre artefatos: o botão existe e está ligado
# --------------------------------------------------------------------------

def _web(arquivo):
    import pathlib
    import re

    texto = (pathlib.Path(__file__).resolve().parent / "web" / arquivo
             ).read_text(encoding="utf-8")
    if arquivo.endswith(".html"):
        return re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", texto, flags=re.S)


def test_o_botao_esta_no_cartao():
    html = _web("index.html")
    assert 'id="btn-ensino-nao"' in html, (
        "o cartão de ensino continua com um botão só")


def test_o_cliente_respeita_o_teto():
    """Oferecer o botão depois do teto faria a pessoa clicar e o percurso
    andar sem explicação nenhuma — pior que não ter o botão."""
    js = _web("app.js")
    assert "pode_repetir" in js, "o cliente não lê o teto que o motor manda"
    assert "btn-ensino-nao" in js, "o botão não está ligado"
    assert "repetir: true" in js or "repetir:true" in js, (
        "o cliente não manda `repetir` ao motor")
