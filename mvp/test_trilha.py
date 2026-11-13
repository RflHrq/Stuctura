"""O motor da trilha: o tópico em sequência, com o trabalho que cada
premissa pede (docs/trilha.md).

O motor atual percorre o tópico inteiro para todo mundo: cartões antes
da primeira pergunta, duas respostas certas por premissa, três telas por
pergunta — 45 telas para quem acerta tudo. A trilha pergunta primeiro e
faz em cada premissa só o trabalho que AQUELA pessoa precisa.

Os testes daqui atravessam o kc_00 de verdade, com a escada escrita
dele, e usam os alunos simulados de `scripts/trilha_alunos.py`. Nenhuma
sessão toca disco: o motor é puro, e o teste do fim deste arquivo guarda
isso.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import trilha_alunos  # noqa: E402
from trilha_alunos import PERSONAS, caminha  # noqa: E402

from mvp import motor, trilha, trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "dominio" / "escada_kc00.yaml", D)


# --------------------------------------------------------------------------
# Auxiliares
# --------------------------------------------------------------------------

def _comeca(modo, ritmo="completo", semente="s1"):
    t = trilha.inicia(D, ESC, semente)
    return trilha.avanca(D, ESC, t.estado,
                         trilha.Entrada(acao="comecar", modo=modo, ritmo=ritmo))


def _anda(estado, persona="sabe"):
    """Um passo, respondendo como a persona."""
    entrada = trilha_alunos.responde(D, ESC, estado.tela, persona, estado)
    return trilha.avanca(D, ESC, estado, entrada)


def _fecha_a_premissa_atual(estado, persona="sabe"):
    """Responde até a premissa da tela atual fechar e a próxima abrir."""
    no = estado.tela.dados["premissa"]
    t = None
    for _ in range(60):
        t = _anda(estado, persona)
        estado = t.estado
        if estado.premissa(no).resultado and (
                t.tela.tipo == "mapa" or t.tela.dados.get("premissa") != no):
            return t
    raise AssertionError("a premissa %s não fechou" % no)


def _responde_firme_ate_fechar(estado, no):
    for _ in range(60):
        if estado.premissa(no).resultado:
            return estado
        estado = _anda(estado, "sabe").estado
    raise AssertionError("a premissa %s não fechou" % no)


def _conta(c):
    """As telas de uma caminhada, do jeito que a spec conta: sem `retorno`."""
    return sum(1 for t in c.telas if t.tipo != "retorno")


def _da_premissa(c, no, tipo=None):
    return [t for t in c.telas if t.dados.get("premissa") == no
            and t.tipo != "retorno" and (tipo is None or t.tipo == tipo)]


# --------------------------------------------------------------------------
# Parte 1: entrada, sequência, abertura, caminho firme, mapa
# --------------------------------------------------------------------------

def test_a_primeira_tela_e_a_entrada():
    t = trilha.inicia(D, ESC, "s1")
    assert t.tela.tipo == "entrada" and t.tela.dados["premissas"] == 5
    assert t.tela.dados["titulo"] == D.titulo
    assert t.tela.dados["modos"] == ["direto", "explique"]
    assert t.tela.dados["ritmos"] == ["completo", "rapido"]
    assert t.tela.dados["ritmo_padrao"] == "completo"
    assert [e.tipo for e in t.eventos] == ["trilha_iniciada"]
    assert t.eventos[0].dados["topico"] == "kc_00"


def test_comecar_direto_abre_a_primeira_premissa_com_a_pergunta_de_codigo():
    t = _comeca("direto").tela
    assert (t.tipo, t.dados["premissa"], t.dados["papel"]) == (
        "pergunta", "B1", "abertura")
    assert t.dados["atividade"] == trilha.abertura(D, "B1").id == "ciu_kc00_002"
    assert t.dados["pede_razao"] and t.dados["pede_certeza"]
    assert t.dados["escala"] == list(motor.CONFIANCAS)
    assert len(t.dados["opcoes"]) == 3 and len(t.dados["razoes"]) == 3
    assert t.texto == trilha.abertura(D, "B1").enunciado


def test_a_abertura_e_sempre_de_degrau_2_com_duas_razoes():
    for no in D.ordem:
        a = trilha.abertura(D, no)
        assert a.no == no and a.uso == "diagnostico" and a.nivel == 2
        assert len(motor.razoes_de(D, a)) >= 2


def test_a_tela_mostra_alternativas_e_razoes_na_ordem_da_semente():
    t = _comeca("direto", semente="s7")
    a = trilha.abertura(D, "B1")
    assert [o["texto"] for o in t.tela.dados["opcoes"]] == [
        o.texto for o in motor.opcoes_na_tela("s7", a)]
    razoes = motor.razoes_de(D, a)
    ordem = motor.ordem_das_razoes("s7", a.id, len(razoes))
    assert [r["texto"] for r in t.tela.dados["razoes"]] == [
        razoes[i].texto for i in ordem]


def test_firme_no_ritmo_rapido_fecha_com_uma_tela():
    c = caminha(D, ESC, "sabe", ritmo="rapido")
    assert [c.estado.premissa(n).resultado for n in D.ordem] == ["ja_sabia"] * 5
    assert all(c.estado.premissa(n).telas == 1 for n in D.ordem)
    assert not [t for t in c.telas if t.tipo == "degrau"]


def test_quem_acerta_firme_recebe_o_porque_antes_de_seguir():
    """Decisão 5 do Rafael: quem acerta recebe uma explicação breve."""
    c = caminha(D, ESC, "sabe", ritmo="rapido")
    retornos = [t for t in c.telas if t.tipo == "retorno"]
    assert [t.dados["premissa"] for t in retornos] == list(D.ordem)
    assert all(t.dados["veredito"] == "firme" for t in retornos)
    assert [t.dados["premissa_texto"] for t in retornos] == [
        D.nos[n].simples for n in D.ordem]


def test_firme_no_ritmo_completo_escreve_antes_de_fechar():
    c = caminha(D, ESC, "sabe")
    produzir = [t for t in c.telas if t.tipo == "degrau"]
    assert len(produzir) == 5
    assert {t.dados["papel"] for t in produzir} == {"produzir"}
    assert all(t.dados["degrau"] == ESC[t.dados["premissa"]].pratica[-1].id
               for t in produzir)
    assert [c.estado.premissa(n).resultado for n in D.ordem] == ["ja_sabia"] * 5
    assert all(c.estado.premissa(n).telas == 2 for n in D.ordem)


def test_quem_sabe_tudo_termina_em_doze_telas_ou_sete():
    assert _conta(caminha(D, ESC, "sabe")) <= 2 * 5 + 2
    assert _conta(caminha(D, ESC, "sabe", ritmo="rapido")) <= 5 + 2


def test_as_premissas_vem_na_ordem_do_grafo():
    c = caminha(D, ESC, "sabe", ritmo="rapido")
    aberturas = [t.dados["premissa"] for t in c.telas if t.tipo == "pergunta"]
    assert aberturas == list(D.ordem)


def test_a_trilha_termina_no_mapa_com_as_cinco_premissas():
    c = caminha(D, ESC, "sabe")
    assert c.telas[-1].tipo == "mapa" and c.estado.fim
    assert [p["no"] for p in c.telas[-1].dados["premissas"]] == list(D.ordem)
    assert [e.tipo for e in c.eventos][-1] == "trilha_encerrada"


def test_cada_premissa_que_fecha_vira_evento():
    c = caminha(D, ESC, "sabe", ritmo="rapido")
    fechos = [e.dados for e in c.eventos if e.tipo == "premissa_fechada"]
    assert fechos == [{"no": n, "resultado": "ja_sabia", "telas": 1}
                      for n in D.ordem]


def test_a_mesma_semente_redesenha_a_mesma_tela():
    assert _comeca("direto", semente="x").tela == _comeca("direto", semente="x").tela
    a = _comeca("direto", semente="x").tela.dados["opcoes"]
    outras = [_comeca("direto", semente=s).tela.dados["opcoes"]
              for s in ("y", "z", "w", "k")]
    assert any(o != a for o in outras)


def test_entrada_que_nao_cabe_na_tela_e_recusada_e_nada_muda():
    """Review Focus 1: a segunda resposta de um duplo clique não cabe."""
    e = _comeca("direto").estado
    for ruim in (
            trilha.Entrada(acao="continuar"),
            trilha.Entrada(acao="comecar", modo="direto"),
            trilha.Entrada(acao="responder", escolha=9, razao=0,
                           confianca="tenho certeza"),
            trilha.Entrada(acao="responder", escolha=0, razao=9,
                           confianca="tenho certeza"),
            trilha.Entrada(acao="responder", escolha=0, razao=0,
                           confianca="talvez"),
            trilha.Entrada(acao="responder", escolha=0,
                           confianca="tenho certeza"),
            trilha.Entrada(acao="responder", escolha=True, razao=0,
                           confianca="tenho certeza"),
            trilha.Entrada(acao="dancar")):
        with pytest.raises(trilha.EntradaInvalida):
            trilha.avanca(D, ESC, e, ruim)

    depois = _anda(e).estado          # respondeu: a pergunta ficou para trás
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, depois, trilha_alunos.responde(
            D, ESC, e.tela, "sabe", e))


def test_comecar_pede_um_modo_que_existe():
    e = trilha.inicia(D, ESC, "s1").estado
    for ruim in (trilha.Entrada(acao="comecar"),
                 trilha.Entrada(acao="comecar", modo="devagar"),
                 trilha.Entrada(acao="comecar", modo="direto", ritmo="lento"),
                 trilha.Entrada(acao="responder", escolha=0)):
        with pytest.raises(trilha.EntradaInvalida):
            trilha.avanca(D, ESC, e, ruim)
    t = trilha.avanca(D, ESC, e, trilha.Entrada(acao="comecar", modo="direto"))
    assert t.estado.ritmo == "completo"


def test_depois_do_mapa_nada_e_aceito():
    c = caminha(D, ESC, "sabe", ritmo="rapido")
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, c.estado, trilha.Entrada(acao="continuar"))


def test_o_motor_nao_importa_relogio_disco_nem_sorteio():
    fonte = (RAIZ / "trilha.py").read_text(encoding="utf-8")
    for proibido in ("import random", "import time", "datetime", "open(",
                     "import os", "prerequisites"):
        assert proibido not in fonte
