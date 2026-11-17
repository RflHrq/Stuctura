"""O diagnóstico dentro dos passos.

O Rafael jogou o kc_00 em 13/11/2026 e disse o que faltava: os
exercícios passo a passo ficaram bons, mas com eles a sessão saiu do
escopo do sistema. O Structura existe para DETECTAR a misconception e a
lacuna de cada pessoa — e quem escolhia "nunca vi" na primeira tela ia
direto para os passos, sem a pergunta de resposta, razão e certeza, e
quase nunca chegava à refutação. Ele viu também questão repetida
demais, e pediu um fechamento que resuma o que foi achado.

Cinco mudanças, e os testes delas:

  1. TODA IDEIA ABRE COM A PERGUNTA DE DIAGNÓSTICO. A primeira tela não
     pergunta mais se a pessoa quer a explicação antes: quem não sabe
     toca em "Não sei", e a pergunta dele também é dado.
  2. O PASSO TAMBÉM DETECTA A MISCONCEPTION. Cada escada tem um passo
     guiado em que uma alternativa É a crença, dita com todas as letras.
     Esse passo pede a certeza; marcada com convicção, a alternativa
     abre a refutação na hora — antes ela só ficava anotada.
  3. O PASSO LOCALIZA A LACUNA. O passo errado fica registrado, com o
     nome dele, e vai para o fechamento.
  4. MENOS REPETIÇÃO. Passo errado mostra a correção e segue: não volta o
     mesmo passo com outros valores. A subida são os passos guiados e UM
     de prática. O passo errado volta uma vez, na reconferência do fim.
  5. O FECHAMENTO RESUME: as ideias erradas encontradas, as lacunas e em
     que passos, e o que já estava firme.

O motor guarda o caminho "começar pelos passos" (`modo="explique"`):
ele não é mais oferecido, e continua sendo o jeito de um teste chegar a
um passo sem atravessar a pergunta de abertura.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import trilha_alunos  # noqa: E402
from trilha_alunos import PERSONAS, caminha  # noqa: E402

from mvp import motor, trilha, trilha_escada  # noqa: E402
from mvp.test_trilha import D, ESC, _anda, _comeca  # noqa: E402

WEB = RAIZ / "web"

# O passo guiado do B1 em que uma alternativa é a crença do tópico.
DA_CRENCA = "esc_kc00_B1_3"


def _ate_o_passo(degrau, modo="explique"):
    """Uma sessão levada, acertando, até aquele passo aparecer."""
    t = _comeca(modo)
    for _ in range(60):
        if t.tela.tipo == "degrau" and t.tela.dados["degrau"] == degrau:
            return t
        t = _anda(t.estado, "sabe")
    raise AssertionError("o passo %s não chegou" % degrau)


def _diz_a_crenca(estado, certeza):
    """A alternativa que é a crença, no passo que está na tela."""
    p = estado.passo
    g = next(x for x in ESC[p.premissa].degraus if x.id == p.degrau)
    v = g.versoes[p.versao]
    erro = next(x for x in v.erros if x.crenca)
    ordem = trilha_escada.ordem_das_pecas(estado.semente, g.id, p.versao,
                                          g.forma, len(v.pecas))
    entrada = trilha.Entrada(acao="responder", confianca=certeza,
                             pecas=tuple(ordem.index(i) for i in erro.exata))
    return entrada, erro.crenca


def _erra(estado):
    return trilha_alunos.responde(D, ESC, estado.tela, "nao_sabe_erra", estado)


def _subida(c, no):
    return [t for t in c.telas if t.tipo == "degrau"
            and t.dados["papel"] == "subida" and t.dados["premissa"] == no]


# --------------------------------------------------------------------------
# 1. Toda ideia abre com a pergunta de diagnóstico
# --------------------------------------------------------------------------

def test_a_entrada_nao_pergunta_mais_como_comecar():
    entrada = trilha.inicia(D, ESC, "s1").tela
    assert "modos" not in entrada.dados
    assert entrada.dados["ritmos"] == list(trilha.RITMOS)


def test_comecar_sem_dizer_o_modo_abre_pela_pergunta():
    t = trilha.inicia(D, ESC, "s1")
    t = trilha.avanca(D, ESC, t.estado,
                      trilha.Entrada(acao="comecar", ritmo="completo"))
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("pergunta", "abertura")
    assert t.tela.dados["pede_certeza"] and t.tela.dados["pede_razao"]
    assert t.estado.modo == "direto"


def test_quem_nao_sabe_chega_aos_passos_com_um_toque():
    t = _comeca("direto")
    t = trilha.avanca(D, ESC, t.estado, trilha.Entrada(acao="nao_sei"))
    assert (t.tela.tipo, t.tela.dados["papel"]) == ("degrau", "subida")
    assert t.estado.premissa("B1").trabalho == "lacuna"


def test_a_pagina_nao_oferece_mais_a_escolha_do_modo():
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    html = (WEB / "trilha.html").read_text(encoding="utf-8")
    assert "nunca vi" not in js and "já vi isso antes" not in js
    assert "ajuste-modo" not in js and "ajuste-modo" not in html
    # A sessão começa por um botão só, e o modo não viaja no pedido.
    assert re.search(r'acao: "comecar", ritmo: ritmo', js)
    assert "explique" not in js


# --------------------------------------------------------------------------
# 2. O passo também detecta a misconception
# --------------------------------------------------------------------------

def test_o_passo_que_oferece_a_crenca_pede_a_certeza():
    da_crenca = _ate_o_passo(DA_CRENCA).tela.dados
    assert da_crenca["pede_certeza"] is True
    assert da_crenca["escala"] == list(motor.CONFIANCAS)
    comum = _ate_o_passo("esc_kc00_B1_1").tela.dados
    assert comum["pede_certeza"] is False and comum["escala"] == []


def test_toda_escada_do_kc_00_tem_um_passo_que_pede_a_certeza():
    c = caminha(D, ESC, "nao_sabe_aprende")
    for no in D.ordem:
        assert sum(1 for t in _subida(c, no) if t.dados["pede_certeza"]) == 1


def test_sem_a_certeza_o_passo_da_crenca_nao_aceita_a_resposta():
    t = _ate_o_passo(DA_CRENCA)
    entrada, _ = _diz_a_crenca(t.estado, "")
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, ESC, t.estado, entrada)


@pytest.mark.parametrize("certeza", ["acho que sei", "tenho certeza"])
def test_a_crenca_dita_num_passo_com_conviccao_abre_a_refutacao(certeza):
    t = _ate_o_passo(DA_CRENCA)
    entrada, crenca = _diz_a_crenca(t.estado, certeza)
    r = trilha.avanca(D, ESC, t.estado, entrada)
    assert (r.tela.tipo, r.tela.dados["premissa"]) == ("voce_disse", "B1")
    assert r.tela.dados["crenca"] == D.crencas[crenca].afirma
    assert r.estado.premissa("B1").trabalho == "crenca"
    assert r.estado.premissa("B1").crenca == crenca
    tipos = [e.tipo for e in r.eventos]
    assert tipos.index("degrau_respondido") < tipos.index("prova_apresentada")
    classificado = next(e.dados for e in r.eventos
                        if e.tipo == "episodio_classificado")
    assert classificado == {"no": "B1", "estado": motor.CRENCA_EP,
                            "degrau": DA_CRENCA, "papel": "subida"}
    respondido = next(e.dados for e in r.eventos
                      if e.tipo == "degrau_respondido")
    assert respondido["confianca"] == certeza and respondido["certa"] is False


def test_a_refutacao_aberta_no_passo_fecha_a_ideia_pelo_treino():
    t = _ate_o_passo(DA_CRENCA)
    entrada, _ = _diz_a_crenca(t.estado, "tenho certeza")
    t = trilha.avanca(D, ESC, t.estado, entrada)
    vistas = []
    for _ in range(20):
        if t.estado.premissa("B1").resultado:
            break
        vistas.append((t.tela.tipo, t.tela.dados.get("papel")))
        t = _anda(t.estado, "sabe")
    assert vistas[:2] == [("voce_disse", None), ("maquina", None)]
    assert all(v == ("degrau", "treino") for v in vistas[2:]) and vistas[2:]
    assert t.estado.premissa("B1").resultado == trilha.CORRIGIU
    # Os passos que faltavam da subida não voltam: o trabalho da ideia
    # passou a ser o da crença.
    assert t.tela.dados.get("premissa") == "B2"


def test_a_crenca_dita_como_chute_fica_anotada_e_a_subida_segue():
    t = _ate_o_passo(DA_CRENCA)
    entrada, crenca = _diz_a_crenca(t.estado, "chutei")
    r = trilha.avanca(D, ESC, t.estado, entrada)
    assert (r.tela.tipo, r.tela.dados["veredito"]) == ("retorno", "errada")
    ep = r.estado.premissa("B1")
    assert ep.trabalho == "lacuna" and ep.apareceu == (crenca,)
    assert ep.tropecos == (DA_CRENCA,)
    assert "prova_apresentada" not in [e.tipo for e in r.eventos]
    seguinte = trilha.avanca(D, ESC, r.estado, trilha.Entrada(acao="continuar"))
    assert seguinte.tela.dados["degrau"] == "esc_kc00_B1_4"


def test_acertar_o_passo_da_crenca_registra_a_certeza_e_segue():
    t = _ate_o_passo(DA_CRENCA)
    r = _anda(t.estado, "sabe")
    respondido = next(e.dados for e in r.eventos
                      if e.tipo == "degrau_respondido")
    assert respondido["certa"] is True and respondido["confianca"]
    assert r.tela.dados["degrau"] == "esc_kc00_B1_4"


# --------------------------------------------------------------------------
# 3 e 4. O passo localiza a lacuna, e não se repete
# --------------------------------------------------------------------------

def test_passo_errado_mostra_a_correcao_e_segue_para_o_proximo():
    t = _ate_o_passo("esc_kc00_B1_1")
    r = trilha.avanca(D, ESC, t.estado, _erra(t.estado))
    assert (r.tela.tipo, r.tela.dados["veredito"]) == ("retorno", "errada")
    assert r.tela.dados["mostra_certa"] and r.tela.texto
    assert r.estado.premissa("B1").tropecos == ("esc_kc00_B1_1",)
    seguinte = trilha.avanca(D, ESC, r.estado, trilha.Entrada(acao="continuar"))
    assert (seguinte.tela.tipo, seguinte.tela.dados["degrau"]) == (
        "degrau", "esc_kc00_B1_2")
    assert seguinte.tela.dados["tentativa"] == 1


@pytest.mark.parametrize("persona", PERSONAS)
def test_ninguem_ve_o_mesmo_passo_duas_vezes_na_subida(persona):
    for modo in trilha.MODOS:
        c = caminha(D, ESC, persona, modo)
        for no in D.ordem:
            ids = [t.dados["degrau"] for t in _subida(c, no)]
            assert len(ids) == len(set(ids)), (modo, no, ids)


def test_a_subida_sao_os_passos_guiados_e_um_de_pratica():
    c = caminha(D, ESC, "nao_sabe_aprende")
    for no in D.ordem:
        esperado = [g.id for g in ESC[no].guiados] + [ESC[no].pratica[0].id]
        telas = _subida(c, no)
        assert [t.dados["degrau"] for t in telas] == esperado
        assert [t.dados["indice"] for t in telas] == list(
            range(1, len(esperado) + 1))
        assert {t.dados["total"] for t in telas} == {len(esperado)}


def test_o_kc_00_sobe_em_22_passos_e_nao_mais_em_27():
    c = caminha(D, ESC, "nao_sabe_aprende")
    assert sum(len(_subida(c, no)) for no in D.ordem) == 22


def test_o_resumo_diz_em_que_passos_a_pessoa_tropecou():
    c = caminha(D, ESC, "tropeca_na_pratica", "explique")
    for linha in trilha.resumo(D, ESC, c.estado):
        g = ESC[linha["no"]].pratica[0]
        assert linha["tropecos"] == [{"degrau": g.id, "texto": g.nome}]
        assert linha["degraus"] == len(ESC[linha["no"]].guiados) + 1
        assert linha["degrau"] == linha["degraus"] - 1


def test_o_tropeco_num_passo_guiado_leva_a_frase_do_passo():
    t = _ate_o_passo("esc_kc00_B1_1")
    r = trilha.avanca(D, ESC, t.estado, _erra(t.estado))
    b1 = trilha.resumo(D, ESC, r.estado)[0]
    assert b1["tropecos"] == [{
        "degrau": "esc_kc00_B1_1",
        "texto": ESC["B1"].degraus[0].frases[0]}]


def test_a_reconferencia_volta_ao_passo_em_que_a_pessoa_tropecou():
    c = caminha(D, ESC, "tropeca_na_pratica", "explique")
    for no in D.ordem:
        errado = ESC[no].pratica[0].id
        vista = next(t for t in _subida(c, no) if t.dados["degrau"] == errado)
        volta = next(t for t in c.telas if t.tipo == "degrau"
                     and t.dados["papel"] == "reconferencia"
                     and t.dados["premissa"] == no)
        assert volta.dados["degrau"] == errado
        # O mesmo passo, com OUTROS valores: é a segunda versão dele.
        assert (volta.dados["pede"], volta.dados["pecas"],
                volta.dados["mostra"]) != (vista.dados["pede"],
                                           vista.dados["pecas"],
                                           vista.dados["mostra"])


# --------------------------------------------------------------------------
# 4b. A reconferência não repete o que a pessoa acabou de fazer (16/11/2026)
# --------------------------------------------------------------------------
#
# O ensaio do kc_08 mostrou: quem diz a crença faz os dois passos de
# prática como treino, e no fim a reconferência trazia um deles de novo,
# com outros valores. O Rafael pediu menos repetição, e aprovou a regra:
# o passo do tropeço; um passo de produzir ainda não visto; uma questão do
# banco ainda não vista; só então um passo já visto, com outros valores.

def _vistos_antes(c, tela):
    antes = c.telas[:c.telas.index(tela)]
    passos = {t.dados["degrau"] for t in antes if t.tipo == "degrau"}
    questoes = {t.dados["atividade"] for t in antes if t.tipo == "pergunta"}
    return passos, questoes


def _escadas_de(topico):
    from mvp.dominio import carrega
    d = carrega(topico=topico)
    return d, trilha_escada.le(
        RAIZ / "dominio" / ("escada_%s.yaml" % topico.replace("_", "")), d)


def test_quem_corrigiu_a_ideia_e_reconferido_por_questao_nova():
    """O treino da refutação gasta os dois passos de prática: a
    reconferência é uma questão do banco que a pessoa ainda não viu —
    com razão, que é o que mostra se a ideia errada voltou."""
    c = caminha(D, ESC, "crente_aprende")
    rec = [t for t in c.telas if t.dados.get("papel") == "reconferencia"]
    assert len(rec) == len(D.ordem)
    for t in rec:
        assert t.tipo == "pergunta", t.dados["premissa"]
        assert t.dados["pede_razao"] and not t.dados["pede_certeza"]
        _, questoes = _vistos_antes(c, t)
        assert t.dados["atividade"] not in questoes


@pytest.mark.parametrize("topico", ["kc_00", "kc_06", "kc_09"])
@pytest.mark.parametrize("persona", ["nao_sabe_aprende", "crente_aprende",
                                     "nao_sabe_erra", "chuta_com_certeza"])
def test_a_reconferencia_so_repete_passo_quando_e_o_do_tropeco(topico, persona):
    """Passo já visto, na reconferência, só o do tropeço — ou quando o
    banco da ideia não tem mais questão nova. É o caso do B2 do kc_06,
    que fica com duas questões de marcar (as outras usam variável
    global), e as duas já saíram."""
    d, escadas = _escadas_de(topico)
    c = caminha(d, escadas, persona)
    for t in (t for t in c.telas if t.dados.get("papel") == "reconferencia"):
        if t.tipo != "degrau":
            continue
        no = t.dados["premissa"]
        passos, questoes = _vistos_antes(c, t)
        tropecou = t.dados["degrau"] in c.estado.premissa(no).tropecos
        servidas = {a.id for uso in ("diagnostico", "treino")
                    for a in d.atividades_do_no(no, uso)
                    if a.id not in escadas[no].fora
                    and len(motor.razoes_de(d, a)) >= 2}
        banco_acabou = servidas <= questoes
        assert tropecou or banco_acabou or t.dados["degrau"] not in passos, (
            no, t.dados["degrau"])


def test_sem_questao_nova_a_reconferencia_volta_a_um_passo_visto():
    """Quando o banco da ideia acabou, vale a regra de antes: um passo já
    visto, na versão que a pessoa ainda não viu — é melhor que deixar a
    ideia sem reconferência."""
    import dataclasses
    sem_banco = dataclasses.replace(D, atividades=tuple(
        a for a in D.atividades if a.nivel == 2 and a.uso == "diagnostico"
        and a.codigo))
    c = caminha(sem_banco, ESC, "crente_aprende")
    rec = [t for t in c.telas if t.dados.get("papel") == "reconferencia"]
    assert rec and all(t.tipo == "degrau" for t in rec)


# --------------------------------------------------------------------------
# 5. O fechamento resume
# --------------------------------------------------------------------------

def _sumario(persona, modo="direto"):
    c = caminha(D, ESC, persona, modo)
    return c, c.telas[-1].dados["sumario"]


def test_o_fechamento_de_quem_sabia_tudo():
    _, s = _sumario("sabe")
    assert s["firmes"] == [{"no": no, "texto": D.nos[no].simples}
                           for no in D.ordem]
    assert s["ideias_erradas"] == [] and s["lacunas"] == []


def test_o_fechamento_diz_cada_ideia_errada_e_se_foi_corrigida():
    c, s = _sumario("crente_aprende")
    assert [x["no"] for x in s["ideias_erradas"]] == list(D.ordem)
    for x in s["ideias_erradas"]:
        crenca = c.estado.premissa(x["no"]).crenca
        assert x["crenca"] == D.crencas[crenca].afirma
        assert x["corrigida"] is True and x["voltou"] is False
        assert x["texto"] == D.nos[x["no"]].simples
    assert s["lacunas"] == [] and s["firmes"] == []

    _, teimoso = _sumario("crente_teimoso")
    assert teimoso["ideias_erradas"]
    assert all(x["corrigida"] is False for x in teimoso["ideias_erradas"])


def test_o_fechamento_diz_cada_lacuna_e_em_que_passos():
    c, s = _sumario("tropeca_na_pratica", "explique")
    assert [x["no"] for x in s["lacunas"]] == list(D.ordem)
    for x in s["lacunas"]:
        g = ESC[x["no"]].pratica[0]
        assert x["passos"] == [g.nome] and g.nome
        assert x["fechou"] is True          # aprendeu pelos passos
    assert s["ideias_erradas"] == [] and s["firmes"] == []

    _, erra = _sumario("nao_sabe_erra")
    assert erra["lacunas"] and all(x["fechou"] is False for x in erra["lacunas"])
    assert all(x["passos"] for x in erra["lacunas"])


def test_cada_ideia_aparece_num_lugar_so_do_fechamento():
    for persona in PERSONAS:
        _, s = _sumario(persona)
        nos = [x["no"] for chave in ("firmes", "ideias_erradas", "lacunas",
                                     "em_aberto")
               for x in s[chave]]
        assert sorted(nos) == sorted(D.ordem), persona


def test_a_pagina_desenha_o_fechamento():
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    for chave in ("sumario", "ideias_erradas", "lacunas", "firmes",
                  "em_aberto", "passos", "corrigida", "voltou", "fechou",
                  "tropecos"):
        assert re.search(r"\b%s\b" % chave, js), chave
    # E o passo que pede a certeza a desenha, e a manda.
    assert re.search(r"t\.pede_certeza", js)


# --------------------------------------------------------------------------
# A sessão começada pelas regras antigas não é refeita pelas novas
# --------------------------------------------------------------------------

def test_sessao_de_antes_da_mudanca_das_regras_nao_e_refeita(tmp_path):
    """O registro refaz uma sessão reexecutando as respostas gravadas. As
    regras mudaram em 13/11/2026 — o passo errado não se repete mais, e a
    subida ficou mais curta —, e as mesmas respostas cairiam em telas
    diferentes: sairia um estado plausível e errado. A linha de abertura
    diz sob que regras a sessão começou, e a de outras regras é
    recusada, com a frase de quem está na tela."""
    import json

    from mvp import trilha_log

    destino = tmp_path / "t.jsonl"
    abertura = trilha.inicia(D, ESC, "P40")
    trilha_log.grava(destino, "P40", abertura.eventos)
    assert trilha_log.VERSAO >= 2
    # De hoje: refaz.
    assert trilha_log.reconstroi(D, ESC, destino, "P40").tela.tipo == "entrada"

    linhas = [json.loads(l) for l in
              destino.read_text(encoding="utf-8").splitlines()]
    for l in linhas:
        l["v"] = 1
    destino.write_text("".join(json.dumps(l, ensure_ascii=False) + chr(10)
                               for l in linhas), encoding="utf-8")
    with pytest.raises(trilha_log.RegistroNaoReexecutavel) as erro:
        trilha_log.reconstroi(D, ESC, destino, "P40")
    assert "mudou" in str(erro.value) and "P40" in str(erro.value)


# --------------------------------------------------------------------------
# O nome do passo
# --------------------------------------------------------------------------

def test_o_passo_pode_ter_nome_e_o_fechamento_usa_o_nome(tmp_path):
    """O fechamento diz em que passo a pessoa tropeçou. O enunciado de um
    exercício de prever a saída — "Que número este trecho mostra na
    tela?" — não diz QUAL ideia foi; o nome curto do passo, sim."""
    from mvp.test_trilha_escada import _escreve, _valida
    bloco = _valida()
    bloco["degraus"][1]["nome"] = "Achar a declaração inválida"
    e = trilha_escada.le(_escreve(tmp_path, {"B1": bloco}), D)["B1"]
    assert e.degraus[1].nome == "Achar a declaração inválida"
    assert e.degraus[0].nome == ""
    assert trilha._rotulo(e.degraus[1]) == "Achar a declaração inválida"
    # Sem nome: a frase do passo guiado, ou o que o exercício pede.
    assert trilha._rotulo(e.degraus[0]) == e.degraus[0].frases[0]
    assert trilha._rotulo(e.degraus[2]) == e.degraus[2].versoes[0].pede


def test_nome_de_passo_e_curto(tmp_path):
    from mvp.test_trilha_escada import _escreve, _valida
    bloco = _valida()
    bloco["degraus"][1]["nome"] = " ".join(["palavra"] * 13)
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        trilha_escada.le(_escreve(tmp_path, {"B1": bloco}), D)
    assert any("nome" in p and "12" in p for p in erro.value.problemas)


def test_o_passo_de_pratica_do_kc_00_aparece_pelo_nome_no_fechamento():
    c = caminha(D, ESC, "tropeca_na_pratica", "explique")
    lacunas = c.telas[-1].dados["sumario"]["lacunas"]
    assert [x["passos"] for x in lacunas] == [
        ["Declarar cada variável com o tipo certo"],
        ["Declarar e depois guardar um valor"],
        ["Escrever na variável antes de ler"],
        ["Ficar só com o último valor escrito"],
        ["Declarar já com o valor, numa linha"],
    ]
