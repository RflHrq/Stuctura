"""A frase do começo e a do fim.

É a resposta direta ao "não estou sentindo melhora": a pessoa escreve o
que pensa antes de começar, escreve de novo no fim, e **vê as duas lado a
lado**. Para o TCC é o dado mais forte que um estudo deste tamanho produz
— mudança nas palavras da própria pessoa. Para quem está respondendo, é o
momento em que a mudança fica visível.

O sistema **não corrige e não classifica** o texto. Quem classifica é o
pesquisador, depois, com codebook. Aqui ele só guarda e devolve.

Portão G: texto livre escrito por participante é dado pessoal. A tela diz
que fica guardado, e nunca pede nada que identifique.
"""

from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import Resposta

D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


def ate_o_fim(d, inicial="antes eu achava que nao existia", final="agora sei que o espaco existe"):
    """Atravessa a unidade inteira acertando o que der, e devolve o mapa."""
    t = motor.inicia(d, semente="s")
    eventos = list(t.eventos)
    for _ in range(300):
        if t.tela.tipo == "mapa":
            return t, eventos
        tela = t.tela
        if tela.tipo == "frase":
            texto = inicial if tela.dados["momento"] == "inicio" else final
            t = motor.avanca(d, t.estado, Resposta(texto=texto, ms=5))
        elif tela.tipo == "atividade":
            a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
            t = motor.avanca(d, t.estado, Resposta(
                escolha=motor.indice_correto_na_tela(t.estado.semente, a)))
        elif tela.tipo == "razao":
            i = next(k for k, z in enumerate(t.estado.pendente.razoes) if z.correta)
            t = motor.avanca(d, t.estado, Resposta(escolha=i))
        elif tela.tipo == "confianca":
            t = motor.avanca(d, t.estado, Resposta(confianca="tenho certeza"))
        else:
            t = motor.avanca(d, t.estado, Resposta())
        eventos.extend(t.eventos)
    raise AssertionError("a unidade não terminou")


# --------------------------------------------------------------------------
# A pergunta, e de onde ela vem
# --------------------------------------------------------------------------

def test_a_unidade_comeca_pela_frase(d):
    t = motor.inicia(d)
    assert t.tela.tipo == "frase"
    assert t.tela.dados["momento"] == "inicio"
    assert t.estado.fase == motor.ABERTURA


def test_a_pergunta_vem_do_dominio_e_nao_do_motor(d):
    """Pelo mesmo motivo que as razões vêm do grafo: o motor não escreve
    conteúdo. Trocar de tópico troca a pergunta, sem tocar no código."""
    t = motor.inicia(d)
    assert t.tela.texto == d.teachback
    assert d.teachback


def test_a_mesma_pergunta_volta_no_fim(d):
    t, _ = ate_o_fim(d)
    perguntas = []
    t2 = motor.inicia(d, semente="s")
    for _ in range(300):
        if t2.tela.tipo == "frase":
            perguntas.append(t2.tela.texto)
        if t2.tela.tipo == "mapa":
            break
        t2 = _responde_qualquer(d, t2)
    assert len(perguntas) == 2
    assert perguntas[0] == perguntas[1]


def _responde_qualquer(d, t):
    tela = t.tela
    if tela.tipo == "frase":
        return motor.avanca(d, t.estado, Resposta(texto="x"))
    if tela.tipo == "atividade":
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        return motor.avanca(d, t.estado, Resposta(
            escolha=motor.indice_correto_na_tela(t.estado.semente, a)))
    if tela.tipo == "razao":
        i = next(k for k, z in enumerate(t.estado.pendente.razoes) if z.correta)
        return motor.avanca(d, t.estado, Resposta(escolha=i))
    if tela.tipo == "confianca":
        return motor.avanca(d, t.estado, Resposta(confianca="tenho certeza"))
    return motor.avanca(d, t.estado, Resposta())


# --------------------------------------------------------------------------
# CS-8 — as duas frases no log, e lado a lado no fim
# --------------------------------------------------------------------------

def test_cs8_as_duas_frases_entram_no_log(d):
    _, eventos = ate_o_fim(d)
    inicial = next(e for e in eventos if e.tipo == "teachback_inicial")
    final = next(e for e in eventos if e.tipo == "teachback_final")
    assert inicial.dados["texto"] == "antes eu achava que nao existia"
    assert final.dados["texto"] == "agora sei que o espaco existe"
    assert inicial.dados["em_branco"] is False


def test_cs8_o_mapa_devolve_as_duas_lado_a_lado(d):
    t, _ = ate_o_fim(d)
    assert t.tela.dados["frase_inicial"] == "antes eu achava que nao existia"
    assert t.tela.dados["frase_final"] == "agora sei que o espaco existe"


def test_a_frase_do_fim_e_escrita_sem_a_do_comeco_a_vista(d):
    """Escrever olhando a própria frase antiga é copiá-la ou corrigi-la,
    não reformulá-la. As duas só aparecem juntas depois, no mapa."""
    t = motor.inicia(d, semente="s")
    for _ in range(300):
        if t.tela.tipo == "frase" and t.tela.dados["momento"] == "fim":
            assert t.tela.dados["antes"] == ""
            return
        if t.tela.tipo == "mapa":
            break
        t = _responde_qualquer(d, t)
    raise AssertionError("a tela do fim não apareceu")


# --------------------------------------------------------------------------
# O sistema não corrige, e não exige
# --------------------------------------------------------------------------

def test_a_frase_em_branco_e_aceita_e_fica_registrada(d):
    """Quem não sabe dizer não pode ficar preso na primeira tela. O log
    guarda que estava em branco — isso também é dado."""
    t = motor.inicia(d)
    t = motor.avanca(d, t.estado, Resposta(texto="   "))
    evento = next(e for e in t.eventos if e.tipo == "teachback_inicial")
    assert evento.dados["em_branco"] is True
    assert t.tela.tipo == "ensino"


def test_nenhum_veredito_e_emitido_sobre_a_frase(d):
    """O sistema guarda, não julga: nada no log diz se a frase está certa."""
    _, eventos = ate_o_fim(d)
    dos_teachbacks = [e for e in eventos if e.tipo.startswith("teachback")]
    for e in dos_teachbacks:
        assert "correta" not in e.dados
        assert "estado" not in e.dados


def test_a_tela_avisa_que_a_frase_fica_guardada(d):
    """Portão G: texto livre é dado pessoal, e a pessoa precisa saber."""
    t = motor.inicia(d)
    assert "guardado" in t.tela.dados["aviso"]
    assert "sem nome" in t.tela.dados["aviso"]
