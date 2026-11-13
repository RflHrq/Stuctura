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
    # "De produzir" e de produzir: montar, completar ou digitar. O ultimo
    # degrau de pratica de tres das cinco escadas e de ESCOLHER, que e
    # marcar outra vez -- e a decisao 16 pede uma segunda resposta de
    # outra natureza.
    assert all(t.dados["forma"] in trilha.PRODUZEM for t in produzir)
    assert [t.dados["degrau"] for t in produzir] == [
        "esc_kc00_B1_4", "esc_kc00_B2_4", "esc_kc00_B3_4", "esc_kc00_B4_5",
        "esc_kc00_I1_7"]
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


def test_o_degrau_diz_se_as_pecas_sao_codigo():
    """Para a tela desenhar codigo com cara de codigo. Opcao de `escolher`
    pode ser uma linha de C ou uma frase, e o cliente nao adivinha."""
    c = caminha(D, ESC, "nao_sabe_aprende")
    vistos = set()
    for t in (t for t in c.telas if t.tipo == "degrau"):
        g = next(x for x in ESC[t.dados["premissa"]].degraus
                 if x.id == t.dados["degrau"])
        assert t.dados["em_codigo"] is g.codigo
        vistos.add(g.codigo)
    assert vistos == {True, False}


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


# --------------------------------------------------------------------------
# Parte 3: reforço e crença
# --------------------------------------------------------------------------

def _ate_a_abertura(no, modo="direto", ritmo="rapido", semente="s1"):
    """Uma sessão levada, acertando firme, até a abertura de `no`."""
    t = _comeca(modo, ritmo, semente)
    for _ in range(200):
        if (t.tela.tipo == "pergunta" and t.tela.dados["premissa"] == no
                and t.tela.dados["papel"] == "abertura"):
            return t
        t = _anda(t.estado, "sabe")
    raise AssertionError("a abertura de %s não chegou" % no)


def _marca(estado, crenca=None, certa=False, razao_certa=False,
           confianca="tenho certeza"):
    """Uma resposta montada à mão para a pergunta que está na tela.

    A alternativa é a certa ou a que aponta `crenca`; a razão é a certa
    ou a que diz `crenca`.
    """
    dados = estado.tela.dados
    a = next(x for x in D.atividades if x.id == dados["atividade"])
    opcoes = motor.opcoes_na_tela(estado.semente, a)
    brutas = motor.razoes_de(D, a)
    razoes = [brutas[i] for i in motor.ordem_das_razoes(
        estado.semente, a.id, len(brutas))]
    if certa:
        escolha = next(i for i, o in enumerate(opcoes) if o.correta)
    else:
        escolha = next((i for i, o in enumerate(opcoes) if o.crenca == crenca),
                       next(i for i, o in enumerate(opcoes) if not o.correta))
    if razao_certa:
        razao = next(i for i, z in enumerate(razoes) if z.correta)
    else:
        razao = next(i for i, z in enumerate(razoes) if z.crenca == crenca)
    return trilha.Entrada(
        acao="responder", escolha=escolha, razao=razao,
        confianca=confianca if dados["pede_certeza"] else "")


def _crenca_de(no):
    return next(c.id for c in D.crencas.values() if c.nega == no)


def _tela_voce_disse_de(no):
    t = _ate_a_abertura(no)
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca=_crenca_de(no)))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", no)
    return t


def _tela_maquina_de(no, previsao=0):
    t = _tela_voce_disse_de(no)
    entrada = (trilha.Entrada(acao="responder", escolha=previsao)
               if t.tela.dados["previsao"] else trilha.Entrada(acao="continuar"))
    t = trilha.avanca(D, ESC, t.estado, entrada)
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("maquina", no)
    return t


def _tipos(c, tipo):
    return [e.dados for e in c.eventos if e.tipo == tipo]


def test_inseguro_ganha_uma_pergunta_de_outro_formato_e_firma():
    c = caminha(D, ESC, "inseguro")
    b1 = _da_premissa(c, "B1", "pergunta")
    assert [t.dados["papel"] for t in b1] == ["abertura", "reforco"]
    assert b1[0].dados["formato"] != b1[1].dados["formato"]
    assert b1[1].dados["pede_certeza"]
    assert c.estado.premissa("B1").resultado == "firmou"
    assert c.estado.premissa("B1").telas == 2
    assert {c.estado.premissa(n).resultado for n in D.ordem} == {"firmou"}
    assert not [t for t in c.telas if t.tipo in ("degrau", "voce_disse")]


def test_o_inseguro_le_o_retorno_antes_da_segunda_pergunta():
    t = _anda(_comeca("direto").estado, "inseguro")
    assert (t.tela.tipo, t.tela.dados["veredito"]) == ("retorno", "inseguro")
    assert t.tela.dados["premissa_texto"] == D.nos["B1"].simples
    t = _anda(t.estado, "inseguro")
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("pergunta", "reforco")


def test_escorregao_vai_para_o_reforco_e_nao_para_a_prova():
    t = _anda(_comeca("direto").estado, "escorrega")
    assert (t.tela.tipo, t.tela.dados["veredito"]) == ("retorno", "escorregao")
    c = caminha(D, ESC, "escorrega")
    assert not any(t.tipo == "voce_disse" for t in c.telas)
    assert c.estado.premissa("B1").resultado == "firmou"
    assert not _tipos(c, "prova_apresentada")


def test_acertar_pela_razao_errada_mostra_o_contraste():
    e = _comeca("direto").estado
    t = trilha.avanca(D, ESC, e, _marca(e, crenca="type_is_a_hint", certa=True))
    assert (t.tela.tipo, t.tela.dados["veredito"]) == ("retorno", "razao_errada")
    assert t.tela.dados["escolheu"] == D.crencas["type_is_a_hint"].afirma
    assert t.tela.dados["contradiz"] is True
    assert t.tela.dados["premissa_texto"] == D.nos["B1"].simples

    de_outra = trilha.avanca(D, ESC, e, _marca(
        e, crenca="no_value_no_memory", certa=True))
    assert de_outra.tela.dados["contradiz"] is False
    seguinte = _anda(de_outra.estado)
    assert (seguinte.tela.tipo, seguinte.tela.dados["papel"]) == (
        "pergunta", "reforco")


def test_razao_errada_duas_vezes_na_mesma_ideia_vai_para_a_prova():
    """6.7: uma vez pode ser tropeço de alternativa; duas, é a ideia."""
    e = _comeca("direto").estado
    t = trilha.avanca(D, ESC, e, _marca(
        e, crenca="no_value_no_memory", certa=True))
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="continuar"))
    assert t.tela.dados["papel"] == "reforco"
    t = trilha.avanca(D, ESC, t.estado, _marca(
        t.estado, crenca="no_value_no_memory", certa=True))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", "B2")
    assert t.tela.dados["crenca"] == D.crencas["no_value_no_memory"].afirma


def test_errar_o_degrau_de_produzir_leva_ao_reforco():
    t = _anda(_comeca("direto").estado)                 # abertura firme
    t = _anda(t.estado)                                 # continuar
    assert t.tela.dados["papel"] == "produzir"
    t = _anda(t.estado, "nao_sabe_erra")                # escreve errado
    assert (t.tela.tipo, t.tela.dados["veredito"]) == ("retorno", "errada")
    assert t.tela.dados["mostra_certa"]
    t = _anda(t.estado)
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("pergunta", "reforco")
    t = _anda(t.estado)
    assert t.estado.premissa("B1").resultado == "firmou"
    assert t.estado.premissa("B1").telas == 3


def test_nao_sei_no_reforco_leva_a_escada():
    t = _anda(_comeca("direto").estado, "inseguro")
    t = _anda(t.estado, "inseguro")
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="nao_sei"))
    assert (t.tela.tipo, t.tela.dados["papel"], t.tela.dados["indice"]) == (
        "degrau", "subida", 1)
    assert t.estado.premissa("B1").trabalho == "lacuna"


def test_crenca_leva_a_prova_da_premissa_que_ela_nega():
    c = caminha(D, ESC, "crente_aprende")
    provas = _tipos(c, "prova_apresentada")
    assert [p["no"] for p in provas] == list(D.ordem)
    assert all(D.crencas[p["crenca"]].nega == p["no"] for p in provas)
    disse = next(t for t in c.telas if t.tipo == "voce_disse")
    assert disse.dados["crenca"] == D.crencas[provas[0]["crenca"]].afirma
    assert all(c.estado.premissa(n).trabalho == "crenca" for n in D.ordem)


def test_a_prova_vem_de_motor_prova_e_nao_de_copia():
    assert trilha.provas_exibiveis is motor._prova
    c = caminha(D, ESC, "crente_aprende")
    maquinas = [t for t in c.telas if t.tipo == "maquina"]
    assert len(maquinas) == 5
    for t in maquinas:
        esperado = motor._prova(D, t.dados["premissa"])
        assert t.dados["tem_prova"] == bool(esperado)
        for chave in ("programa", "afirma", "espera", "nao_compila", "avisa",
                      "ambiente"):
            assert t.dados[chave] == esperado[0][chave], chave
        assert t.dados["premissa_texto"] == D.nos[t.dados["premissa"]].simples


def test_prova_que_nao_compila_pede_a_previsao():
    t = _tela_voce_disse_de("B2").tela
    assert t.dados["previsao"] == {
        "pergunta": "Este programa compila?", "opcoes": ["Sim", "Não"]}
    assert t.dados["programa"] == motor._prova(D, "B2")[0]["programa"]


def test_prova_que_avisa_pede_a_previsao_do_aviso():
    t = _tela_voce_disse_de("B3").tela
    assert t.dados["previsao"] == {
        "pergunta": "O compilador reclama de alguma coisa aqui?",
        "opcoes": ["Sim", "Não"]}


def test_prova_com_saida_nao_tem_previsao():
    t = _tela_voce_disse_de("B1").tela
    assert t.dados["previsao"] is None and t.dados["programa"] == ""


def test_a_previsao_e_obrigatoria_e_volta_na_tela_da_maquina():
    t = _tela_voce_disse_de("B2")
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="continuar"))
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, t.estado,
                      trilha.Entrada(acao="responder", escolha=2))
    assert _tela_maquina_de("B2", previsao=0).tela.dados["previu"] == "Sim"
    assert _tela_maquina_de("B2", previsao=1).tela.dados["previu"] == "Não"
    assert _tela_maquina_de("B1").tela.dados["previu"] is None


def test_a_premissa_de_inferencia_mostra_o_apoio():
    t = _tela_maquina_de("I1").tela
    assert t.dados["apoio"] == [
        {"no": n, "texto": D.nos[n].simples} for n in ("B1", "B2", "B3", "B4")]
    assert _tela_maquina_de("B1").tela.dados["apoio"] == []


def test_sem_prova_exibivel_a_tela_nao_diz_que_a_maquina_respondeu(monkeypatch):
    monkeypatch.setattr(trilha, "provas_exibiveis", lambda d, no: [])
    voce = _tela_voce_disse_de("B2").tela
    assert voce.dados["previsao"] is None
    t = _tela_maquina_de("B2").tela
    assert t.dados["tem_prova"] is False
    assert t.dados["programa"] == ESC["B2"].revisao.codigo
    assert t.dados["espera"] == "" and t.dados["afirma"] == ""
    assert t.dados["nao_compila"] is False and t.dados["avisa"] == ""


def test_o_treino_fecha_com_duas_certas_seguidas():
    c = caminha(D, ESC, "crente_aprende")
    for no in D.ordem:
        treino = [t for t in c.telas if t.tipo == "degrau"
                  and t.dados["papel"] == "treino" and t.dados["premissa"] == no]
        assert [t.dados["degrau"] for t in treino] == [
            g.id for g in ESC[no].pratica[:2]]
        assert c.estado.premissa(no).resultado == "corrigiu"
        assert c.estado.premissa(no).telas == 5   # abertura, 2 da prova, 2 de treino


def test_o_treino_para_em_tres_e_fecha_em_aberto():
    c = caminha(D, ESC, "crente_teimoso")
    for n in D.ordem:
        treino = [t for t in c.telas if t.tipo == "degrau"
                  and t.dados["papel"] == "treino" and t.dados["premissa"] == n]
        assert len(treino) == 3
        chaves = [(t.dados["degrau"], tuple(t.dados["pecas"]), t.dados["mostra"])
                  for t in treino]
        assert len(set(chaves)) == 3
        assert c.estado.premissa(n).resultado == "em_aberto"


def test_erro_no_treino_zera_a_sequencia():
    t = _tela_maquina_de("B1")
    t = _anda(t.estado)                                  # continuar: 1º treino
    assert t.tela.dados["papel"] == "treino"
    t = _anda(t.estado)                                  # certa
    t = _anda(t.estado, "nao_sabe_erra")                 # errada: zera
    assert (t.tela.tipo, t.tela.dados["veredito"]) == ("retorno", "errada")
    assert t.tela.dados["mostra_certa"]
    t = _anda(t.estado)                                  # continuar: 3º treino
    assert t.tela.dados["papel"] == "treino"
    t = _anda(t.estado)                                  # certa, mas uma só
    assert t.estado.premissa("B1").resultado == "em_aberto"


def test_cada_premissa_recebe_no_maximo_uma_prova():
    for persona in PERSONAS:
        for modo in trilha.MODOS:
            c = caminha(D, ESC, persona, modo)
            nos = [p["no"] for p in _tipos(c, "prova_apresentada")]
            assert len(nos) == len(set(nos)), (persona, modo)


def test_crenca_sobre_outra_premissa_prova_a_outra_e_volta():
    """6.8. A abertura do B1 oferece uma crença que nega o B2."""
    e = _comeca("direto").estado
    crenca = "no_value_no_memory"
    assert D.crencas[crenca].nega == "B2"
    t = trilha.avanca(D, ESC, e, _marca(e, crenca=crenca))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", "B2")
    assert [x.dados for x in t.eventos if x.tipo == "prova_apresentada"] == [
        {"no": "B2", "crenca": crenca, "veio_de": "B1"}]
    assert t.estado.premissa("B2").trabalho == "crenca"
    assert t.estado.premissa("B1").trabalho == ""

    vistas = []
    for _ in range(40):                                  # prova e treino do B2
        t = _anda(t.estado)
        vistas.append(t.tela)
        if t.tela.dados.get("premissa") == "B1":
            break
    assert t.estado.premissa("B2").resultado == "corrigiu"
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("pergunta", "reforco")

    resto = []
    while t.tela.tipo != "mapa":
        t = _anda(t.estado)
        resto.append(t.tela)
    assert t.estado.premissa("B1").resultado == "firmou"
    assert not [x for x in resto if x.dados.get("premissa") == "B2"
                and x.dados.get("papel") == "abertura"]
    assert t.estado.premissa("B2").telas <= trilha.TETO_TELAS


def test_premissa_ja_fechada_como_ja_sabia_e_reaberta_pela_prova():
    """6.8: a prova acontece mesmo que a premissa negada já estivesse fechada."""
    t = _ate_a_abertura("B3")
    assert t.estado.premissa("B2").resultado == "ja_sabia"
    # A pergunta de reforço do B3 oferece a crença que nega o B2.
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca="declaration_zeroes",
                                               razao_certa=True))
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="continuar"))
    assert t.tela.dados["papel"] == "reforco"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca="no_value_no_memory"))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", "B2")
    assert t.estado.premissa("B2").resultado == ""
    assert [x.dados for x in t.eventos if x.tipo == "premissa_reaberta"] == [
        {"no": "B2", "era": "ja_sabia"}]


def test_premissa_ja_trabalhada_nao_recebe_segunda_prova():
    e = _comeca("direto").estado
    t = trilha.avanca(D, ESC, e, _marca(e, crenca="no_value_no_memory"))
    while t.tela.dados.get("premissa") != "B1":          # a prova do B2, inteira
        t = _anda(t.estado)
    assert t.tela.dados["papel"] == "reforco"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca="no_value_no_memory"))
    assert [x.dados for x in t.eventos if x.tipo == "prova_dispensada"] == [
        {"no": "B2", "crenca": "no_value_no_memory", "veio_de": "B1"}]
    assert not [x for x in t.eventos if x.tipo == "prova_apresentada"]
    assert (t.tela.tipo, t.tela.dados["premissa"], t.tela.dados["papel"]) == (
        "degrau", "B1", "subida")


def test_a_mesma_crenca_duas_vezes_vai_para_a_prova_mesmo_com_chutei():
    """6.6 e 6.14: o que a pessoa faz vale mais do que o que ela diz."""
    t = _ate_a_abertura("B2")
    crenca = "no_value_no_memory"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca=crenca,
                                               confianca="chutei"))
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("degrau", "subida")
    assert t.estado.premissa("B2").trabalho == "lacuna"
    while t.tela.tipo != "pergunta":                     # sobe a escada, certo
        t = _anda(t.estado)
    assert t.tela.dados["papel"] == "topo" and not t.tela.dados["pede_certeza"]
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca=crenca))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", "B2")
    assert t.estado.premissa("B2").trabalho == "crenca"
    while t.estado.premissa("B2").resultado == "":
        t = _anda(t.estado)
    assert t.estado.premissa("B2").resultado == "corrigiu"
    assert t.estado.premissa("B2").telas <= trilha.TETO_TELAS


def test_crenca_dentro_de_um_trabalho_so_e_registrada():
    t = _ate_a_abertura("B3")
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="nao_sei"))
    while t.tela.tipo != "pergunta":
        t = _anda(t.estado)
    assert t.tela.dados["papel"] == "topo"
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca="declaration_zeroes"))
    assert t.tela.tipo == "revisao"
    assert [x.dados for x in t.eventos if x.tipo == "crenca_registrada"] == [
        {"no": "B3", "crenca": "declaration_zeroes"}]
    assert not [x for x in t.eventos if x.tipo == "prova_apresentada"]
    assert t.estado.premissa("B3").trabalho == "lacuna"


def test_no_modo_explique_crenca_no_topo_leva_a_prova():
    t = _comeca("explique")
    while t.tela.tipo != "pergunta":
        t = _anda(t.estado)
    assert t.tela.dados["papel"] == "topo" and t.tela.dados["pede_certeza"]
    t = trilha.avanca(D, ESC, t.estado, _marca(t.estado, crenca="type_is_a_hint"))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", "B1")
    assert t.estado.premissa("B1").trabalho == "crenca"
    while t.estado.premissa("B1").resultado == "":
        t = _anda(t.estado)
    assert t.estado.premissa("B1").resultado == "corrigiu"
    assert t.estado.premissa("B1").telas <= trilha.TETO_TELAS


# --------------------------------------------------------------------------
# Parte 4: reconferência e mapa
# --------------------------------------------------------------------------

def _reconferencias(c):
    return [t for t in c.telas if t.dados.get("papel") == "reconferencia"]


def test_toda_premissa_trabalhada_e_reconferida_e_as_outras_nao():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert [t.dados["premissa"] for t in _reconferencias(c)] == list(D.ordem)
    assert not _reconferencias(caminha(D, ESC, "sabe"))
    assert not _reconferencias(caminha(D, ESC, "inseguro"))
    assert {caminha(D, ESC, "sabe").estado.premissa(n).reconferencia
            for n in D.ordem} == {""}


def test_a_reconferencia_vem_depois_de_todas_as_premissas():
    c = caminha(D, ESC, "nao_sabe_aprende")
    papeis = [t.dados.get("papel") for t in c.telas if t.tipo != "retorno"]
    primeira = papeis.index("reconferencia")
    assert set(papeis[primeira:-1]) == {"reconferencia"}
    fechos = [e.tipo for e in c.eventos].count("premissa_fechada")
    assert fechos == 5


def test_a_reconferencia_e_de_produzir_e_nao_repete_exercicio():
    c = caminha(D, ESC, "nao_sabe_aprende")
    vistos = set()
    for t in (t for t in c.telas if t.tipo == "degrau"):
        chave = (t.dados["degrau"], tuple(t.dados["pecas"]), t.dados["mostra"])
        if t.dados["papel"] == "reconferencia":
            assert chave not in vistos
            assert t.dados["forma"] in trilha.PRODUZEM
            assert t.dados["frases"] == []
        vistos.add(chave)
    assert len(_reconferencias(c)) == 5
    assert {t.tipo for t in _reconferencias(c)} == {"degrau"}


def test_a_reconferencia_nao_conta_nas_telas_da_premissa():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert all(c.estado.premissa(n).telas == 3 for n in D.ordem)
    assert [e.dados["telas"] for e in c.eventos
            if e.tipo == "premissa_fechada"] == [3] * 5


def test_quem_aprendeu_e_acerta_no_fim_assimilou():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert {c.estado.premissa(n).reconferencia for n in D.ordem} == {"assimilou"}
    assert _tipos(c, "reconferencia_respondida") == [
        {"no": n, "resultado": "assimilou"} for n in D.ordem]


def test_quem_corrigiu_a_crenca_e_acerta_no_fim_assimilou():
    c = caminha(D, ESC, "crente_aprende")
    assert {c.estado.premissa(n).resultado for n in D.ordem} == {"corrigiu"}
    assert {c.estado.premissa(n).reconferencia for n in D.ordem} == {"assimilou"}


def test_quem_erra_no_fim_nao_se_manteve_e_nao_abre_laco():
    c = caminha(D, ESC, "crente_teimoso")
    assert {c.estado.premissa(n).reconferencia for n in D.ordem} == {
        "nao_se_manteve"}
    rec = _reconferencias(c)
    assert len(rec) == 5
    depois = c.telas[c.telas.index(rec[0]):]
    assert {t.tipo for t in depois} <= {"degrau", "pergunta", "retorno", "mapa"}
    assert not [t for t in depois if t.dados.get("papel") in (
        "subida", "treino", "abertura", "reforco", "topo")]


def test_sem_exercicio_de_produzir_a_reconferencia_e_de_marcar():
    """`nao_sabe_erra` vê as duas versões de todo degrau ao subir: não
    sobra exercício de produzir, e a reconferência cai numa questão de
    marcar ainda não usada — com razão, sem certeza."""
    c = caminha(D, ESC, "nao_sabe_erra")
    marcar = [t for t in _reconferencias(c) if t.tipo == "pergunta"]
    assert marcar and not [t for t in _reconferencias(c) if t.tipo == "degrau"]
    assert all(t.dados["pede_razao"] and not t.dados["pede_certeza"]
               for t in marcar)
    for t in marcar:
        antes = [x.dados["atividade"] for x in c.telas[:c.telas.index(t)]
                 if x.tipo == "pergunta"]
        assert t.dados["atividade"] not in antes


def test_sem_questao_nenhuma_o_mapa_diz_que_nao_deu_para_reconferir():
    """O B1 do kc_00 tem três questões de marcar com razão. Quem gasta as
    três e todos os exercícios fica sem reconferência — e o mapa diz."""
    c = caminha(D, ESC, "nao_sabe_erra")
    assert c.estado.premissa("B1").reconferencia == "sem_questao"
    assert not [t for t in _reconferencias(c) if t.dados["premissa"] == "B1"]
    assert {c.estado.premissa(n).reconferencia for n in D.ordem[1:]} == {
        "nao_se_manteve"}


def _com_crenca_na_pratica(no):
    """A escada de `no` com a crença dele ligada aos erros do último
    degrau de prática. O conteúdo do kc_00 não faz isso (só liga crença
    onde ela é dita com todas as letras), então a regra é testada aqui
    com uma escada montada de propósito."""
    from dataclasses import replace
    crenca = _crenca_de(no)
    escada = ESC[no]
    ultimo = escada.pratica[-1]
    novo = replace(ultimo, versoes=tuple(
        replace(v, erros=tuple(replace(x, crenca=crenca) for x in v.erros))
        for v in ultimo.versoes))
    return {**ESC, no: replace(escada, degraus=tuple(
        novo if g.id == ultimo.id else g for g in escada.degraus))}


def test_a_crenca_de_novo_no_fim_e_a_ideia_voltou():
    escadas = _com_crenca_na_pratica("B1")
    c = caminha(D, escadas, "crente_teimoso")
    assert c.estado.premissa("B1").reconferencia == "a_ideia_voltou"
    assert c.estado.premissa("B2").reconferencia == "nao_se_manteve"


def _com_uma_versao_so():
    """Escadas com UMA versão por degrau: o treino gasta os exercícios de
    produzir, e a reconferência tem de ser de marcar."""
    from dataclasses import replace
    return {no: replace(e, degraus=tuple(
        replace(g, versoes=g.versoes[:1]) for g in e.degraus))
        for no, e in ESC.items()}


def test_na_reconferencia_de_marcar_a_razao_da_crenca_e_a_ideia_voltou():
    escadas = _com_uma_versao_so()
    t = trilha.inicia(D, escadas, "s1")
    t = trilha.avanca(D, escadas, t.estado, trilha.Entrada(
        acao="comecar", modo="direto", ritmo="rapido"))

    def anda(t, persona="sabe"):
        return trilha.avanca(D, escadas, t.estado, trilha_alunos.responde(
            D, escadas, t.tela, persona, t.estado))

    t = anda(t)                                       # B1 firme
    t = anda(t)
    assert t.tela.dados["premissa"] == "B2"
    t = trilha.avanca(D, escadas, t.estado,
                      _marca(t.estado, crenca="no_value_no_memory"))
    while t.tela.dados.get("papel") != "reconferencia":
        t = anda(t)                                   # prova, treino, resto
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("pergunta", "B2")
    assert t.estado.premissa("B2").resultado == "corrigiu"
    volta = trilha.avanca(D, escadas, t.estado,
                          _marca(t.estado, crenca="no_value_no_memory"))
    assert volta.estado.premissa("B2").reconferencia == "a_ideia_voltou"
    assert volta.tela.tipo == "retorno"
    certa = anda(t)
    assert certa.estado.premissa("B2").reconferencia == "assimilou"


def test_o_mapa_traz_resultado_degrau_e_reconferencia():
    c = caminha(D, ESC, "nao_sabe_aprende")
    p = c.telas[-1].dados["premissas"][0]
    assert set(p) == {"no", "texto", "resultado", "trabalho", "degrau",
                      "degraus", "reconferencia", "telas", "crenca",
                      "apareceu", "frases", "codigo"}
    assert p["degrau"] == p["degraus"] == len(ESC["B1"].degraus)
    assert (p["resultado"], p["trabalho"], p["reconferencia"]) == (
        "aprendeu_agora", "lacuna", "assimilou")
    assert p["texto"] == D.nos["B1"].simples
    assert p["frases"] == [f for g in ESC["B1"].guiados for f in g.frases]
    assert p["codigo"] == ESC["B1"].revisao.codigo


def test_no_mapa_quem_fechou_pelo_topo_tem_a_escada_inteira():
    for p in caminha(D, ESC, "sabe").telas[-1].dados["premissas"]:
        assert p["degrau"] == p["degraus"] and p["resultado"] == "ja_sabia"
    for p in caminha(D, ESC, "nao_sabe_erra").telas[-1].dados["premissas"]:
        assert p["degrau"] == 0 and p["resultado"] == "em_aberto"


def test_o_mapa_diz_a_crenca_corrigida_e_as_que_so_apareceram():
    c = caminha(D, ESC, "crente_aprende")
    premissas = c.telas[-1].dados["premissas"]
    assert [p["crenca"] for p in premissas] == [
        D.crencas[_crenca_de(n)].afirma for n in D.ordem]
    assert all(p["apareceu"] == [] for p in premissas)


def test_o_motor_nao_importa_relogio_disco_nem_sorteio():
    fonte = (RAIZ / "trilha.py").read_text(encoding="utf-8")
    for proibido in ("import random", "import time", "datetime", "open(",
                     "import os", "prerequisites"):
        assert proibido not in fonte
