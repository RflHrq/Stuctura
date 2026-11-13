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


# --------------------------------------------------------------------------
# Parte 2: subir a escada (lacuna e modo "explique"), explicação à mão
# --------------------------------------------------------------------------

def test_quem_nao_sabe_sobe_a_escada_do_primeiro_degrau():
    c = caminha(D, ESC, "nao_sabe_aprende")
    b1 = _da_premissa(c, "B1")
    assert [t.tipo for t in b1[:2]] == ["pergunta", "degrau"]
    subida = [t for t in b1 if t.tipo == "degrau" and t.dados["papel"] == "subida"]
    assert [t.dados["indice"] for t in subida] == list(
        range(1, len(ESC["B1"].degraus) + 1))
    assert all(t.dados["total"] == len(ESC["B1"].degraus) for t in subida)
    assert c.estado.premissa("B1").trabalho == "lacuna"


def test_o_degrau_guiado_leva_as_frases_e_o_de_pratica_nao():
    c = caminha(D, ESC, "nao_sabe_aprende")
    subidas = [t for t in c.telas if t.tipo == "degrau"
               and t.dados["papel"] == "subida"]
    assert len(subidas) == sum(len(ESC[n].degraus) for n in D.ordem)
    for t in subidas:
        g = next(x for x in ESC[t.dados["premissa"]].degraus
                 if x.id == t.dados["degrau"])
        assert t.dados["guiado"] == g.guiado
        assert t.dados["frases"] == list(g.frases)
        assert t.dados["forma"] == g.forma and t.dados["pede"]


def test_quem_aprende_fecha_como_aprendeu_agora_em_tres_telas():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert all(c.estado.premissa(n).resultado == "aprendeu_agora"
               for n in D.ordem)
    # abertura, subida, topo
    assert all(c.estado.premissa(n).telas == 3 for n in D.ordem)


def test_a_medida_da_escada_e_o_degrau_certo_de_primeira():
    sobe_bem = caminha(D, ESC, "nao_sabe_aprende")
    sobe_mal = caminha(D, ESC, "nao_sabe_erra")
    for n in D.ordem:
        assert sobe_bem.estado.premissa(n).degrau == len(ESC[n].degraus)
        assert sobe_mal.estado.premissa(n).degrau == 0


def test_o_topo_depois_da_escada_nao_repete_a_abertura():
    c = caminha(D, ESC, "nao_sabe_aprende")
    for n in D.ordem:
        perguntas = _da_premissa(c, n, "pergunta")
        assert [t.dados["papel"] for t in perguntas[:2]] == ["abertura", "topo"]
        ids = [t.dados["atividade"] for t in perguntas
               if t.dados["papel"] != "reconferencia"]
        assert len(ids) == len(set(ids))
        assert not perguntas[1].dados["pede_certeza"]
        assert perguntas[1].dados["pede_razao"]


def test_degrau_errado_volta_com_outros_valores_uma_vez_e_segue():
    c = caminha(D, ESC, "nao_sabe_erra")
    b1 = [t for t in c.telas if t.tipo == "degrau"
          and t.dados["premissa"] == "B1" and t.dados["papel"] == "subida"]
    assert [t.dados["tentativa"] for t in b1[:2]] == [1, 2]
    assert b1[0].dados["degrau"] == b1[1].dados["degrau"]

    def cara(t):
        return sorted(t.dados["pecas"]), t.dados["mostra"], t.dados["pede"]

    assert cara(b1[0]) != cara(b1[1])
    assert (b1[2].dados["indice"], b1[2].dados["tentativa"]) == (2, 1)
    assert all(t.dados["tentativa"] <= 2 for t in b1)


def test_o_primeiro_erro_traz_o_retorno_e_o_segundo_mostra_a_certa():
    e = _comeca("explique").estado
    g = ESC["B1"].degraus[0]
    t1 = _anda(e, "nao_sabe_erra")
    assert t1.tela.tipo == "retorno" and t1.tela.dados["veredito"] == "errada"
    assert t1.tela.texto in [x.retorno for x in g.versoes[0].erros]
    assert t1.tela.dados["mostra_certa"] == ""
    t2 = _anda(t1.estado, "nao_sabe_erra")          # continuar: o mesmo degrau
    assert (t2.tela.tipo, t2.tela.dados["tentativa"]) == ("degrau", 2)
    t3 = _anda(t2.estado, "nao_sabe_erra")
    assert t3.tela.dados["mostra_certa"] == g.versoes[1].certa_texto
    t4 = _anda(t3.estado, "nao_sabe_erra")          # continuar: o seguinte
    assert (t4.tela.tipo, t4.tela.dados["indice"]) == ("degrau", 2)


def test_quem_nao_aprende_ve_a_revisao_e_fecha_em_aberto_em_cinco_telas():
    c = caminha(D, ESC, "nao_sabe_erra")
    revisoes = [t for t in c.telas if t.tipo == "revisao"]
    assert [t.dados["premissa"] for t in revisoes] == list(D.ordem)
    r = revisoes[0].dados
    assert r["frases"] == list(ESC["B1"].revisao.frases)
    assert r["codigo"] == ESC["B1"].revisao.codigo
    assert r["saida"] == ESC["B1"].revisao.saida
    assert all(c.estado.premissa(n).resultado == "em_aberto" for n in D.ordem)
    assert all(c.estado.premissa(n).telas == 5 for n in D.ordem)
    for n in D.ordem:
        papeis = [t.dados["papel"] for t in _da_premissa(c, n, "pergunta")
                  if t.dados["papel"] != "reconferencia"]
        assert papeis == ["abertura", "topo", "confirmacao"]


def test_errar_com_chutei_e_lacuna_e_nao_crenca():
    """6.14: a certeza declarada decide entre a prova e o ensino."""
    e = _comeca("direto").estado
    crente = trilha_alunos.responde(D, ESC, e.tela, "crente_teimoso", e)
    chutou = trilha.Entrada(acao="responder", escolha=crente.escolha,
                            razao=crente.razao, confianca="chutei")
    t = trilha.avanca(D, ESC, e, chutou)
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("degrau", "subida")
    assert t.estado.premissa("B1").trabalho == "lacuna"


def test_no_modo_explique_a_premissa_abre_na_escada():
    t = _comeca("explique")
    assert (t.tela.tipo, t.tela.dados["papel"], t.tela.dados["indice"]) == (
        "degrau", "subida", 1)
    assert t.tela.dados["premissa"] == "B1"


def test_no_modo_explique_o_topo_decide_e_pede_a_certeza():
    c = caminha(D, ESC, "sabe", modo="explique")
    topos = [t for t in c.telas
             if t.tipo == "pergunta" and t.dados["papel"] == "topo"]
    assert [t.dados["premissa"] for t in topos] == list(D.ordem)
    assert all(t.dados["pede_certeza"] for t in topos)
    assert [t.dados["atividade"] for t in topos] == [
        t.dados["atividade"] for t in caminha(D, ESC, "sabe").telas
        if t.tipo == "pergunta"]


def test_no_modo_explique_ninguem_fecha_como_ja_sabia():
    c = caminha(D, ESC, "sabe", modo="explique")
    assert {c.estado.premissa(n).resultado for n in D.ordem} == {
        "aprendeu_agora"}
    # subida, topo
    assert all(c.estado.premissa(n).telas == 2 for n in D.ordem)
    assert not [t for t in c.telas if t.dados.get("papel") == "abertura"]


def test_abrir_a_explicacao_devolve_a_mesma_tela_e_tira_o_ja_sabia():
    t0 = _comeca("direto")
    t1 = trilha.avanca(D, ESC, t0.estado, trilha.Entrada(acao="explicacao"))
    assert t1.tela == t0.tela
    assert t1.explicacao == {
        "premissa": "B1", "no": "B1", "simples": D.nos["B1"].simples,
        "frases": [f for g in ESC["B1"].guiados for f in g.frases],
        "codigo": ESC["B1"].revisao.codigo}
    assert [e.tipo for e in t1.eventos] == ["explicacao_aberta"]
    assert t1.estado.premissa("B1").abriu_explicacao
    fim = _responde_firme_ate_fechar(t1.estado, "B1")
    assert fim.premissa("B1").resultado == "aprendeu_agora"


def test_a_explicacao_so_abre_em_pergunta_e_em_degrau():
    inicio = trilha.inicia(D, ESC, "s1").estado
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, inicio, trilha.Entrada(acao="explicacao"))
    retorno = _anda(_comeca("direto").estado).estado
    assert retorno.tela.tipo == "retorno"
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, retorno, trilha.Entrada(acao="explicacao"))
    degrau = _comeca("explique").estado
    assert trilha.avanca(D, ESC, degrau, trilha.Entrada(
        acao="explicacao")).explicacao["premissa"] == "B1"


def test_trocar_o_modo_no_meio_vale_na_premissa_seguinte():
    """Review Focus 5: a pergunta na tela não muda debaixo da pessoa."""
    t0 = _comeca("direto")
    t1 = trilha.avanca(D, ESC, t0.estado,
                       trilha.Entrada(acao="modo", modo="explique"))
    assert t1.tela == t0.tela and t1.estado.modo == "explique"
    assert t1.estado.premissa("B1").resultado == ""
    seguinte = _fecha_a_premissa_atual(t1.estado)
    assert seguinte.estado.premissa("B1").resultado == "ja_sabia"
    assert (seguinte.tela.tipo, seguinte.tela.dados["premissa"],
            seguinte.tela.dados["papel"]) == ("degrau", "B2", "subida")


def test_trocar_o_ritmo_no_meio_vale_na_premissa_seguinte():
    t0 = _comeca("direto", ritmo="completo")
    t1 = trilha.avanca(D, ESC, t0.estado,
                       trilha.Entrada(acao="ritmo", ritmo="rapido"))
    assert t1.tela == t0.tela and t1.estado.ritmo == "rapido"
    b2 = _fecha_a_premissa_atual(t1.estado)
    assert b2.estado.premissa("B1").telas == 2       # ainda escreveu
    b3 = _fecha_a_premissa_atual(b2.estado)
    assert b3.estado.premissa("B2").telas == 1       # já no rápido


def test_trocar_para_modo_ou_ritmo_que_nao_existe_e_recusado():
    e = _comeca("direto").estado
    for ruim in (trilha.Entrada(acao="modo", modo="devagar"),
                 trilha.Entrada(acao="modo"),
                 trilha.Entrada(acao="ritmo", ritmo="lento")):
        with pytest.raises(trilha.EntradaInvalida):
            trilha.avanca(D, ESC, e, ruim)
    inicio = trilha.inicia(D, ESC, "s1").estado
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, inicio,
                      trilha.Entrada(acao="modo", modo="direto"))


def test_o_motor_nao_importa_relogio_disco_nem_sorteio():
    fonte = (RAIZ / "trilha.py").read_text(encoding="utf-8")
    for proibido in ("import random", "import time", "datetime", "open(",
                     "import os", "prerequisites"):
        assert proibido not in fonte
