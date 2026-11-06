# -*- coding: utf-8 -*-
"""O erro que explica: o retorno do veredito `errada`.

MEDIDO antes de escrever uma linha, atravessando os treze tópicos como
quem erra duas vezes em cada premissa:

    erradas de diagnóstico   79   →  79 viram refutação, e a refutação ensina
    erradas de treino        79   →  ZERO explicam. "Ainda não. Olhe de novo
                                     com calma" é tudo que a pessoa recebe

E o material para explicar já estava no domínio: das 1.111 alternativas
erradas dos treze tópicos, **1.101 têm crença cadastrada**, todo nó tem
`simples` e toda crença tem `afirma`. Não faltava texto; faltava montar.

A REGRA DO DONO, e é ela que estes testes guardam: o sistema **não redige**
a justificativa do erro. Ele usa a crença que a alternativa escolhida
afirma e o enunciado da premissa que ela nega — texto cadastrado, palavra
por palavra. `test_o_retorno_nao_carrega_prosa` é o guarda disso, e
`test_a_crenca_e_a_que_foi_CLICADA` é o guarda de que a crença nomeada é a
que a pessoa escolheu, e não a que o item pretendia medir: em **48 itens do
kc_02** as duas são diferentes.

POR QUE SÓ TREINO E ENTRADA. Erro de diagnóstico e de reteste é
EVIDÊNCIA — é dele que saem a crença e a medida de transferência.
Explicar ali ensina no meio da medição e contamina os itens seguintes da
mesma sessão. As duas fases que ENSINAM recebem explicação; as duas que
MEDEM continuam caladas.

E NADA DISSO MEXEU NO LOG. O `resposta_registrada` já grava `atividade` e
`escolha`, e `opcoes_na_tela` é determinística desde a fatia da posição:
a alternativa clicada se **recupera** do que já estava gravado. A versão
do log continua 3.
"""
from __future__ import annotations

import collections

import pytest

from mvp import app as aplicacao
from mvp import log, motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

# As fases em que o sistema ENSINA, e só elas explicam.
ENSINA = ("treino", "entrada")
MEDE = ("diagnostico", "reteste")

KC02 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d():
    return KC02


@pytest.fixture(autouse=True)
def log_em_tmp(tmp_path, monkeypatch):
    """O log destes testes não encosta no da coleta."""
    monkeypatch.setattr(log, "DESTINO", tmp_path / "eventos.jsonl")
    aplicacao.sessoes.clear()


# --------------------------------------------------------------------------
# A montagem, item por item: função pura do que o log grava
# --------------------------------------------------------------------------

def _dados(d, semente, atividade, escolha):
    """O `resposta_registrada` de uma errada, como o log o grava."""
    a = next(x for x in d.atividades if x.id == atividade)
    return {"atividade": a.id, "no": a.no, "fase": "treino", "item": a.tipo,
            "escolha": escolha, "correta": False,
            "crenca_em_jogo": a.crenca, "confianca": "tenho certeza", "ms": 1}


def _uma_errada(d, a, semente="P01"):
    """O índice NA TELA de uma alternativa errada com crença."""
    na_tela = motor.opcoes_na_tela(semente, a)
    return next(i for i, o in enumerate(na_tela)
                if not o.correta and o.crenca)


def test_explica_devolve_o_enunciado_da_premissa(d):
    a = next(x for x in d.atividades if x.no == "B1")
    i = _uma_errada(d, a)
    r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
    assert r["premissa"] == d.nos[a.no].simples


def test_explica_devolve_a_fala_da_crenca_escolhida(d):
    a = next(x for x in d.atividades if x.no == "B1")
    i = _uma_errada(d, a)
    cid = motor.opcoes_na_tela("P01", a)[i].crenca
    r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
    assert r["escolheu"] == d.crencas[cid].afirma


def test_a_crenca_e_a_que_foi_CLICADA(d):
    """O teste que cai se alguém trocar isto pelo `crenca_em_jogo`.

    `crenca_em_jogo` é a crença que o ITEM pretende medir. Em 48 itens do
    kc_02 há alternativa errada de OUTRA crença, e usar a do item faria o
    sistema dizer "você escolheu X" para quem escolheu Y — invenção com
    cara de dado, que é exactamente o que a regra proíbe.
    """
    divergentes = sem_crenca_no_item = 0
    for a in d.atividades:
        na_tela = motor.opcoes_na_tela("P01", a)
        for i, o in enumerate(na_tela):
            if o.correta or not o.crenca or o.crenca == a.crenca:
                continue
            r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
            assert r["escolheu"] == d.crencas[o.crenca].afirma
            # `a.crenca` pode ser None — item sem crença própria. Usar o
            # `crenca_em_jogo` ali deixaria a tela MUDA, que é o defeito
            # que esta fatia conserta.
            if a.crenca is None:
                sem_crenca_no_item += 1
                assert r["escolheu"].strip()
            else:
                divergentes += 1
                assert r["escolheu"] != d.crencas[a.crenca].afirma
    assert divergentes >= 40, (
        "o kc_02 tinha itens com crença divergente entre as erradas; achei "
        "%d, e sem eles este teste não prova nada" % divergentes)


def test_alternativa_sem_crenca_explica_so_a_premissa(d):
    """As 10 alternativas erradas sem crença dos treze tópicos.

    São distratores plausíveis que ninguém catalogou como crença. O
    sistema diz o que a premissa afirma e CALA sobre o raciocínio da
    pessoa — porque não sabe qual é, e inventar seria a regra quebrada.
    """
    achados = 0
    for a in d.atividades:
        na_tela = motor.opcoes_na_tela("P01", a)
        for i, o in enumerate(na_tela):
            if o.correta or o.crenca:
                continue
            achados += 1
            r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
            assert r["escolheu"] == ""
            assert r["premissa"] == d.nos[a.no].simples
    assert achados >= 6, "o kc_02 tinha 6 dessas; achei %d" % achados


def test_o_retorno_nao_carrega_prosa(d):
    """A REGRA DO DONO, como teste.

    Cinco chaves: três de texto, que são string do domínio palavra por
    palavra, um booleano e um id de nó. Campo novo com frase escrita por
    mim cai aqui — é o único jeito de a proibição ter dente.

    E ELE CAIU, na fatia do erro desenhado: o retorno passou a levar `no`
    e `resgate`. O teste não foi afrouxado para passar — as duas chaves
    novas entraram com a MESMA exigência das antigas (a analogia tem de
    ser string cadastrada do nó; o `no` tem de ser nó deste domínio) e a
    igualdade exata do conjunto de chaves continua aqui. Frase redigida
    por mim em qualquer das cinco continua caindo.
    """
    textos = {n.simples for n in d.nos.values()}
    textos |= {c.afirma for c in d.crencas.values()}
    textos |= set(d.resgates.values())
    textos.add("")
    for a in d.atividades:
        na_tela = motor.opcoes_na_tela("P01", a)
        for i, o in enumerate(na_tela):
            if o.correta:
                continue
            r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
            assert set(r) == {"premissa", "escolheu", "contradiz",
                              "no", "resgate"}, (
                "chave nova em %s: %s" % (a.id, sorted(r)))
            assert r["premissa"] in textos
            assert r["escolheu"] in textos
            assert r["resgate"] in textos
            assert isinstance(r["contradiz"], bool)
            assert r["no"] in d.nos


def test_contradiz_so_quando_a_crenca_nega_ESTA_premissa(d):
    """O defeito da caixa de contraste, não repetido.

    MEDIDO nos treze tópicos: das 1.101 alternativas erradas com crença,
    **512 — 46% — carregam crença que nega OUTRO nó**, não o da pergunta.
    Um rótulo fixo dizendo "e isso contradiz" seria falso em quase metade
    das telas, que é precisamente o tamanho do defeito que a refutação já
    teve. Então o servidor manda o FATO, e o cliente escolhe o rótulo.

    As duas assertivas finais são o sabotador: com `contradiz` fixo em
    True ou em False, uma das duas cai.
    """
    nega_este = outro = 0
    for a in d.atividades:
        na_tela = motor.opcoes_na_tela("P01", a)
        for i, o in enumerate(na_tela):
            if o.correta or not o.crenca:
                continue
            r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
            esperado = d.crencas[o.crenca].nega == a.no
            assert r["contradiz"] is esperado, (
                "%s alternativa %d: crença %s nega %s, e o nó é %s"
                % (a.id, i, o.crenca, d.crencas[o.crenca].nega, a.no))
            if esperado:
                nega_este += 1
            else:
                outro += 1
    assert nega_este and outro, (
        "o kc_02 tem os dois casos (49 negam outro nó); achei %d e %d"
        % (nega_este, outro))


def test_sem_crenca_nao_contradiz(d):
    """Distrator sem crença: o sistema não sabe o que ela nega, e não diz."""
    for a in d.atividades:
        na_tela = motor.opcoes_na_tela("P01", a)
        for i, o in enumerate(na_tela):
            if o.correta or o.crenca:
                continue
            r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, i))
            assert r["contradiz"] is False


def test_sem_escolha_nao_explica(d):
    """Quem não respondeu não escolheu nada: nada a montar."""
    a = d.atividades[0]
    assert aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id, None)) is None


def test_no_fora_do_dominio_nao_explica(d):
    a = d.atividades[0]
    dados = _dados(d, "P01", a.id, _uma_errada(d, a))
    dados["no"] = "ZZ"
    assert aplicacao._explica_erro(d, "P01", dados) is None


# --------------------------------------------------------------------------
# A sessão inteira, pelas rotas: a invariante
# --------------------------------------------------------------------------

def _politica(d, m):
    """Erra `m["ate"]` vezes por nó; opcionalmente erra o reteste.

    `escorregao`: erra a camada 1 e acerta a razão. A T4 decidiu que o
    sistema NÃO contesta isso — e é a única trilha que produz veredito
    `errada` no diagnóstico, porque nenhuma crença é detectada. Sem ela,
    todo teste sobre "o diagnóstico não explica" fica vazio.
    """
    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="uma frase de " + tela.dados["momento"])
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            if not m["errou"] or m["escorregao"]:
                return Resposta(escolha=next(i for i, z in enumerate(razoes)
                                             if z.correta))
            i = next((i for i, z in enumerate(razoes)
                      if z.crenca and z.crenca == m["crenca"]), None)
            if i is None:
                i = next(i for i, z in enumerate(razoes) if not z.correta)
            return Resposta(escolha=i)
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        na_tela = motor.opcoes_na_tela(estado.semente, a)
        no_reteste = estado.fase == motor.RETESTE
        erra = (m["erros"][a.no] < m["ate"]
                or (no_reteste and m["erra_reteste"]))
        if erra:
            if not no_reteste:
                m["erros"][a.no] += 1
            i = next((i for i, o in enumerate(na_tela)
                      if o.crenca is not None and o.crenca == a.crenca),
                     next((i for i, o in enumerate(na_tela)
                           if not o.correta and o.crenca is not None), None))
            if i is None:
                i = next(i for i, o in enumerate(na_tela) if not o.correta)
            m["errou"] = True
            m["crenca"] = na_tela[i].crenca
            return Resposta(escolha=i)
        m["errou"] = False
        m["crenca"] = None
        return Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                     if o.correta))
    return politica


def percorre(d, monkeypatch, ate=2, erra_reteste=False, escorregao=False,
             limite=1500):
    """Atravessa a unidade e devolve (payload, eventos) de cada passo.

    Chama o MESMO `_resposta` que a rota chama: é o retorno de verdade,
    não uma reconstrução dele.
    """
    monkeypatch.setattr(aplicacao, "dominio", d)
    m = {"erros": collections.Counter(), "ate": ate, "errou": False,
         "crenca": None, "erra_reteste": erra_reteste,
         "escorregao": escorregao}
    politica = _politica(d, m)
    t = motor.inicia(d)
    passos = [(aplicacao._resposta("S", t, None), list(t.eventos))]
    for _ in range(limite):
        if t.tela.tipo == "mapa":
            return passos
        r = politica(t.tela, t.estado)
        t = motor.avanca(d, t.estado, r)
        passos.append((aplicacao._resposta("S", t, r), list(t.eventos)))
    raise AssertionError("a unidade não terminou em %d passos" % limite)


def _erradas(passos):
    """(payload, fase, no) de cada resposta errada do percurso."""
    fora = []
    for payload, eventos in passos:
        if payload["veredito"] != "errada":
            continue
        reg = next(e for e in eventos if e.tipo == "resposta_registrada")
        fora.append((payload, reg.dados["fase"], reg.dados["no"]))
    return fora


@pytest.mark.parametrize("topico", topicos())
def test_nenhuma_errada_de_ensino_fica_sem_explicacao(topico, monkeypatch):
    """A invariante, nos treze tópicos.

    Era aqui que o sistema calava: 79 erradas de treino na varredura, todas
    com "Ainda não" e nada mais.
    """
    d = carrega(topico=topico)
    erradas = _erradas(percorre(d, monkeypatch))
    de_ensino = [(p, f, n) for p, f, n in erradas if f in ENSINA]
    assert de_ensino, "%s não produziu errada de ensino nenhuma" % topico
    for payload, fase, no in de_ensino:
        r = payload["retorno"]
        assert r is not None, "%s: errada de %s sem retorno" % (topico, fase)
        assert r["premissa"].strip(), (
            "%s: retorno de %s sem o enunciado da premissa" % (topico, fase))
        assert r["premissa"] == d.nos[no].simples, (
            "%s: a premissa devolvida nao e a do no %s" % (topico, no))


@pytest.mark.parametrize("topico", topicos())
def test_a_medicao_continua_calada(topico, monkeypatch):
    """Diagnóstico não explica: ali o erro é EVIDÊNCIA.

    Quem detecta crença já ganha a refutação, que é o mecanismo da tese.
    O ESCORREGÃO — errar a camada 1 e acertar a razão — não detecta nada, e
    é a trilha que produz veredito `errada` no diagnóstico: **158 nos treze
    tópicos, zero refutações**. Essas telas continuam sem explicação DE
    PROPÓSITO, e isso está medido e registrado como pendência, não
    escondido aqui.

    A primeira assertiva existe porque a versão anterior deste teste era
    VAZIA: com a política coerente, todo erro de diagnóstico virava
    refutação, e o laço não conferia nada. Removido o portão, ele passava.
    """
    d = carrega(topico=topico)
    erradas = _erradas(percorre(d, monkeypatch, escorregao=True))
    de_medicao = [(p, f) for p, f, _ in erradas if f in MEDE]
    assert de_medicao, (
        "%s não produziu errada de medição nenhuma: o teste ficaria vazio"
        % topico)
    for payload, fase in de_medicao:
        assert payload["retorno"] is None, (
            "%s: a fase %s explicou, e ela MEDE" % (topico, fase))


def test_o_reteste_errado_nao_explica(monkeypatch):
    """O reteste é a medida de transferência: explicar ali a destrói."""
    d = carrega(topico="kc_02")
    erradas = _erradas(percorre(d, monkeypatch, ate=1, erra_reteste=True))
    de_reteste = [(p, f) for p, f, _ in erradas if f == "reteste"]
    assert de_reteste, "o percurso não produziu reteste errado nenhum"
    for payload, _ in de_reteste:
        assert payload["retorno"] is None


# --------------------------------------------------------------------------
# Entre artefatos: o servidor e o cliente concordando
#
# A suíte já passou verde uma vez com o `app.js` sintaticamente quebrado, e
# já pegou uma figura que desenhava `x` num cartão que falava de `idade`.
# Campo novo no servidor que o cliente não lê é a mesma classe de defeito.
# --------------------------------------------------------------------------

def _web(arquivo):
    """O arquivo da interface, SEM comentários.

    Tirar os comentários antes de conferir é lição paga: a primeira versão
    de um teste destes caiu no comentário que explicava por que a frase
    fixa tinha ido embora — proibia falar da coisa em vez de proibir usá-la.
    """
    import pathlib
    import re

    texto = (pathlib.Path(__file__).resolve().parent / "web" / arquivo
             ).read_text(encoding="utf-8")
    if arquivo.endswith(".html"):
        return re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", texto, flags=re.S)


def test_o_cliente_le_todos_os_campos_que_o_servidor_monta(d):
    """Campo novo no `_explica_erro` que o cliente ignora cai aqui.

    É o teste que impede a explicação de existir no JSON e não na tela.
    """
    a = next(x for x in d.atividades if x.no == "B1")
    r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id,
                                                 _uma_errada(d, a)))
    js = _web("app.js")
    for campo in r:
        assert ("retorno." + campo) in js, (
            "o servidor manda `%s` e o cliente não lê" % campo)


def test_os_rotulos_do_erro_nao_estao_fixos_no_html():
    """A caixa de contraste serve dois vereditos com relações diferentes.

    Com rótulo fixo no markup, um dos dois mente — foi assim que
    "AS PREMISSAS QUE VOCÊ ACABOU DE CONFIRMAR LEVAM A" apareceu em 46%
    das refutações sem nenhuma premissa confirmada.
    """
    import re

    html = _web("index.html")
    caixa = re.search(r'id="ret-contraste"(.*?)id="btn-retorno"',
                      html, flags=re.S)
    assert caixa, "a caixa de contraste do retorno mudou de forma"
    for rotulo in re.findall(r'class="rotulo"[^>]*>(.*?)</p>',
                             caixa.group(1), flags=re.S):
        assert not rotulo.strip(), (
            "rótulo fixo de volta no markup: %r" % rotulo.strip())
    for ident in ("ret-par-crenca", "ret-rotulo-crenca", "ret-rotulo-certo"):
        assert ('id="%s"' % ident) in html, "falta o id %s" % ident


def test_todo_id_que_o_retorno_toca_existe_no_html():
    """Erro de digitação em `$("ret-...")` é tela muda, e muda em silêncio."""
    import re

    js = _web("app.js")
    html = _web("index.html")
    tocados = {m for m in re.findall(r'\$\("(ret-[a-z-]+)"\)', js)}
    assert len(tocados) >= 6, "achei só %d ids de retorno no JS" % len(tocados)
    for ident in sorted(tocados):
        assert ('id="%s"' % ident) in html, (
            "o JS escreve em #%s, que não existe no HTML" % ident)


def test_o_cliente_esconde_o_par_sem_ideia():
    """As alternativas sem crença: rótulo "Você escolheu" sobre texto vazio
    afirmaria uma escolha que o sistema não sabe qual foi."""
    js = _web("app.js")
    assert 'ret-par-crenca").classList.toggle("oculto"' in js, (
        "o par da ideia deixou de ser escondido quando não há crença")


def test_o_falso_positivo_nao_virou_errada(monkeypatch):
    """O retorno do falso positivo tem forma PRÓPRIA, e continua a dele.

    As duas montagens usam os mesmos dois ingredientes do domínio com
    relações diferentes — "você explicou por" não é "você escolheu" —, e
    confundi-las repetiria o defeito da caixa de contraste.
    """
    d = carrega(topico="kc_02")
    passos = percorre(d, monkeypatch, ate=2)
    falsos = [p for p, _ev in passos if p["veredito"] == "falso_positivo"
              and p["retorno"]]
    for payload in falsos:
        assert set(payload["retorno"]) == {"crenca", "contradiz", "no", "vezes"}


# --------------------------------------------------------------------------
# O ERRO DESENHADO: a figura e a analogia na mesma tela da premissa
#
# MEDIDO antes de escrever uma linha, nos treze tópicos:
#
#     telas de erro de treino/entrada por varredura     79
#     premissas com figura no banco de `figuras.js`     79 de 79
#     premissas com analogia PRÓPRIA (`resgates[no]`)   79 de 79
#     materiais que a tela do erro mostrava              2 de 4
#
# Os quatro materiais do cartão de ensino — enunciado, exemplo, figura e
# analogia — já se encontram na tela de ensino e na de construção. Onde
# eles não se encontravam é aqui: a tela do erro mostrava o enunciado da
# premissa e a fala da ideia marcada, e nenhum desenho.
#
# E A ANALOGIA NÃO É `d.resgate(no)`. Esse acessador cai no RESUMO do
# tópico quando o nó não tem versão própria, e o resumo mapeia as cinco
# premissas de uma vez — na tela de um erro de treino ele entregaria a
# resposta de atividade que ainda não foi feita. Aqui se manda a do nó, ou
# nada. Hoje são 79 de 79 com versão própria, então o caso não acontece em
# nenhum tópico; o teste existe para o nó que alguém cadastrar amanhã.
# --------------------------------------------------------------------------

def test_o_retorno_do_erro_diz_de_que_premissa_desenhar(d):
    """O banco de figuras é do CLIENTE e é indexado por nó.

    O `no` já tinha sido tirado deste retorno de propósito, com a
    justificativa de que campo que ninguém lê é campo que ninguém confere.
    Ele volta com uso: é por ele que o desenho é escolhido. E
    `test_o_cliente_le_todos_os_campos_que_o_servidor_monta` é o que
    garante que o uso existe de fato na tela.
    """
    a = next(x for x in d.atividades if x.no == "B1")
    r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id,
                                                 _uma_errada(d, a)))
    assert r["no"] == a.no


def test_o_retorno_do_erro_leva_a_analogia_do_no(d):
    """Palavra por palavra do domínio, como os outros dois textos."""
    a = next(x for x in d.atividades if x.no == "B1")
    r = aplicacao._explica_erro(d, "P01", _dados(d, "P01", a.id,
                                                 _uma_errada(d, a)))
    assert r["resgate"] == d.resgates[a.no]
    assert r["resgate"].strip(), "a analogia do B1 do kc_02 veio vazia"


def test_a_analogia_do_erro_nao_cai_no_resumo_do_topico(d):
    """O sabotador: trocar isto por `d.resgate(no)` cai aqui.

    Um nó sem versão própria faria o acessador devolver o resumo do
    tópico, que mapeia as cinco premissas de uma vez. Numa tela de erro de
    treino isso entrega a resposta de atividade ainda não feita — e é por
    isso que a validação usa a do nó, não o resumo.
    """
    import dataclasses

    assert d.analogia.strip(), "o kc_02 perdeu o resumo: o teste fica vazio"
    sem = dataclasses.replace(d, resgates={})
    a = next(x for x in d.atividades if x.no == "B1")
    r = aplicacao._explica_erro(sem, "P01", _dados(sem, "P01", a.id,
                                                   _uma_errada(sem, a)))
    assert r["resgate"] == "", (
        "nó sem analogia própria recebeu o resumo do tópico: %r"
        % r["resgate"])


@pytest.mark.parametrize("topico", topicos())
def test_toda_premissa_tem_analogia_propria(topico):
    """A medida virada teste: 79 de 79.

    Como a tela do erro CALA quando o nó não tem versão própria, nó novo
    sem analogia sai sem ela e ninguém percebe. Este teste é o aviso para
    quem cadastrar o próximo: escreva a analogia do nó.
    """
    dd = carrega(topico=topico)
    faltam = [n for n in dd.ordem if not dd.resgates.get(n, "").strip()]
    assert faltam == [], "%s: premissa sem analogia própria: %s" % (
        topico, faltam)


@pytest.mark.parametrize("topico", topicos())
def test_a_errada_de_ensino_vem_com_figura_e_analogia(topico, monkeypatch):
    """A invariante desta fatia, nos treze tópicos.

    Toda errada de treino ou de entrada chega à tela com os quatro
    ingredientes: o enunciado da premissa, a ideia marcada, de que
    premissa é o desenho, e a analogia daquela premissa.
    """
    d = carrega(topico=topico)
    erradas = _erradas(percorre(d, monkeypatch))
    de_ensino = [(p, f, n) for p, f, n in erradas if f in ENSINA]
    assert de_ensino, "%s não produziu errada de ensino nenhuma" % topico
    for payload, fase, no in de_ensino:
        r = payload["retorno"]
        assert r["no"] == no, (
            "%s: o retorno manda desenhar %r e a pergunta é do nó %r"
            % (topico, r["no"], no))
        assert r["resgate"] == d.resgates.get(no, ""), (
            "%s: a analogia do retorno não é a cadastrada do nó %s"
            % (topico, no))
        assert r["resgate"].strip(), (
            "%s: errada de %s no nó %s sem analogia" % (topico, fase, no))


# --------------------------------------------------------------------------
# Entre artefatos: o desenho na tela
# --------------------------------------------------------------------------

def test_o_cliente_desenha_a_figura_do_erro():
    """`Figuras.dentro` é quem troca o SVG e esconde o elemento vazio.

    O cliente já desenhava no cartão de ensino, na validação e na
    refutação. A tela do erro era a única das quatro sem desenho.
    """
    js = _web("app.js")
    # COM O NÓ DO RETORNO, e a primeira versão deste teste não exigia isso:
    # ela procurava só `Figuras.dentro($("ret-figura")`, e a linha que LIMPA
    # o elemento no alto de `mostraRetorno` já casava com isso. Apagada a
    # linha que desenha, o teste continuava verde. Sabotagem é o que
    # descobre assertiva frouxa; lê-la de novo, não.
    assert 'Figuras.dentro($("ret-figura"), j.retorno.no)' in js, (
        "a tela do erro continua sem desenhar a premissa da pergunta")


def test_o_cliente_limpa_o_desenho_antes_de_escolher_o_veredito():
    """Cinco vereditos dividem a MESMA tela de retorno.

    A caixa de contraste é escondida no alto de `mostraRetorno` por este
    motivo exato: sem isso, o desenho do erro anterior fica na tela do
    acerto seguinte. Figura de premissa errada é pior que figura nenhuma.
    """
    import re

    js = _web("app.js")
    abre = re.search(r"function mostraRetorno\(.*?if \(j\.veredito",
                     js, flags=re.S)
    assert abre, "`mostraRetorno` mudou de forma"
    for ident in ("ret-figura", "ret-resgate"):
        assert ident in abre.group(0), (
            "#%s não é limpo antes do veredito ser escolhido" % ident)
