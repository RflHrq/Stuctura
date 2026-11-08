# -*- coding: utf-8 -*-
"""Os três campos de ensino que o esquema não tinha.

A MEDIÇÃO QUE PEDIU ISTO. A unidade do kc_02 oferece **811 palavras de
ensino para seis premissas** sobre ponteiros, e a refutação — que é o
mecanismo da tese — tem **24 palavras por tela**, com 41 das 79 cadeias
em um passo só. O dono usou o sistema e disse: *"eu não consigo
aprender"*.

O material que falta foi escrito (3.465 palavras para o kc_02) e não
cabia em campo nenhum. Entram três:

    narracao        o exemplo explicado LINHA A LINHA. O exemplo já
                    existia; o que faltava era dizer, de cada linha, o
                    que ela faz e o que muda na memória.
    caso_resolvido  um caso trabalhado do começo ao fim ANTES de pedir
                    qualquer coisa. Hoje quem diz "não sei" recebe um
                    cartão e cai direto numa pergunta.
    outra_rota      o que o botão "Ainda não entendi" mostra na segunda
                    vez. Hoje ele remostra o mesmo cartão — dívida que
                    eu registrei quando o construí.

POR QUE LISTA DE BLOCOS, e não texto corrido: `_paragrafos` preserva
linha em branco e **cola o resto**. Rodei o texto da primeira versão do
material por ela e as linhas de código saíram grudadas numa só. Prosa e
código são blocos separados, e a tela desenha cada um do seu jeito.

E A CHAVE `reexplicacao` MUDA DE TIPO, de propósito. Ela já existia na
tela, preenchida com `d.resgate(nid)` como paliativo. Agora ela é
sempre uma LISTA DE BLOCOS: o material próprio do nó quando há, e o
resgate embrulhado num bloco de prosa quando não há. Uma chave, um
renderizador, nenhum `if` de tipo no cliente.
"""
from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d():
    return D2


# --------------------------------------------------------------------------
# O domínio carrega os três
# --------------------------------------------------------------------------

def test_o_dominio_tem_os_tres_acessadores(d):
    """Sem eles o material fica no YAML e não chega a lugar nenhum."""
    for nome in ("narracao", "caso_resolvido", "outra_rota"):
        assert hasattr(d, nome), "falta o acessador `%s`" % nome


def test_no_sem_material_devolve_vazio(d):
    """Campo opcional: nó sem o material não inventa nada, e a tela não
    desenha a seção. É o mesmo contrato da ampliação."""
    for nome in ("narracao", "caso_resolvido", "outra_rota"):
        assert getattr(d, nome)("ZZ") == []


@pytest.mark.parametrize("topico", topicos())
def test_os_tres_sao_sempre_lista(topico):
    """Tipo único: o cliente não pode precisar de um `if` de tipo."""
    dd = carrega(topico=topico)
    for nid in dd.ordem:
        for nome in ("narracao", "caso_resolvido", "outra_rota"):
            v = getattr(dd, nome)(nid)
            assert isinstance(v, list), "%s/%s: %r" % (nid, nome, type(v))


@pytest.mark.parametrize("topico", topicos())
def test_todo_bloco_tem_uma_chave_conhecida(topico):
    """Bloco com chave desconhecida é material que a tela não desenha —
    e que ninguém percebe até alguém atravessar a unidade."""
    dd = carrega(topico=topico)
    for nid in dd.ordem:
        for b in dd.caso_resolvido(nid) + dd.outra_rota(nid):
            assert isinstance(b, dict), "%s: bloco %r" % (nid, b)
            assert set(b) <= {"prosa", "codigo", "saida"}, (
                "%s: bloco com chave fora do contrato: %s" % (nid, sorted(b)))
            assert len(b) == 1, "%s: bloco com %d chaves" % (nid, len(b))
        for linha in dd.narracao(nid):
            assert set(linha) == {"linha", "diz"}, (
                "%s: linha de narração com %s" % (nid, sorted(linha)))


# --------------------------------------------------------------------------
# As duas telas de ensino mandam os três
# --------------------------------------------------------------------------

def _ate_a_construcao(d):
    t = motor.inicia(d, semente="MAT")
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


def test_o_cartao_de_abertura_leva_a_narracao(d):
    t = motor.inicia(d)
    t = motor.avanca(d, t.estado, Resposta(texto="uma frase"))
    assert t.tela.tipo == "ensino"
    assert "narracao" in t.tela.dados


def test_o_cartao_de_lacuna_leva_a_narracao(d):
    """A fatia da ampliação existiu porque `_tela_construcao` não mandava
    o que `_tela_ensino` mandava. Não repetir."""
    t = _ate_a_construcao(d)
    assert "narracao" in t.tela.dados


def test_o_caso_resolvido_NAO_vem_na_primeira_tela(d):
    """Ele é uma SEGUNDA explicação, e mostrá-lo antes de alguém pedir é
    o princípio da coerência violado: material extra, mesmo correto,
    atrapalha. Medido, o cartão do B2 tinha 392 palavras numa tela só.

    Ele agora é a segunda rota de quem diz que não entendeu.
    """
    abertura = motor.avanca(d, motor.inicia(d).estado,
                            Resposta(texto="uma frase")).tela
    lacuna = _ate_a_construcao(d).tela
    for tela, nome in ((abertura, "abertura"), (lacuna, "construção")):
        assert "caso_resolvido" not in tela.dados, (
            "a %s voltou a despejar o caso resolvido de saída" % nome)


def test_as_duas_chances_trazem_coisas_DIFERENTES(d):
    """O teto de reexplicação parecia política e era fim de material.

    Agora a primeira vez que a pessoa pede traz `outra_rota` e a segunda
    traz `caso_resolvido`. Se as duas trouxerem o mesmo, o botão vira
    enfeite — que é o defeito que ele tinha antes de existir material
    próprio.
    """
    t = _ate_a_construcao(d)
    no = t.tela.no
    if not (d.outra_rota(no) and d.caso_resolvido(no)):
        pytest.skip("o nó %s não tem as duas rotas" % no)
    um = motor.avanca(d, t.estado, Resposta(repetir=True))
    dois = motor.avanca(d, um.estado, Resposta(repetir=True))
    a = um.tela.dados["reexplicacao"]
    b = dois.tela.dados["reexplicacao"]
    assert a and b, "alguma das duas chances veio vazia"
    assert a != b, "as duas chances mostram a mesma coisa"


def test_as_duas_telas_mandam_os_mesmos_campos(d):
    """O cliente desenha o MESMO elemento nas duas. Campo que só uma
    manda é seção que some sem ninguém perceber — já aconteceu com a
    ampliação, e o nó que mais precisava foi o que ficou sem."""
    abertura = motor.avanca(d, motor.inicia(d).estado,
                            Resposta(texto="uma frase")).tela
    lacuna = _ate_a_construcao(d).tela
    so_numa = set(abertura.dados) ^ set(lacuna.dados)
    assert so_numa <= {"indice", "total", "motivo"}, (
        "campo em só uma das telas de ensino: %s" % sorted(so_numa))


# --------------------------------------------------------------------------
# `reexplicacao` passa a ser lista de blocos
# --------------------------------------------------------------------------

def test_a_reexplicacao_e_sempre_lista(d):
    t = _ate_a_construcao(d)
    assert isinstance(t.tela.dados["reexplicacao"], list)
    depois = motor.avanca(d, t.estado, Resposta(repetir=True))
    assert isinstance(depois.tela.dados["reexplicacao"], list)


def test_sem_material_proprio_a_segunda_vez_cai_no_resgate(d):
    """O fallback tem de existir: hoje nenhum nó tem `outra_rota`, e
    mesmo assim quem pede de novo precisa receber alguma coisa."""
    t = _ate_a_construcao(d)
    no = t.tela.no
    depois = motor.avanca(d, t.estado, Resposta(repetir=True))
    blocos = depois.tela.dados["reexplicacao"]
    assert blocos, "pediu de novo e não veio nada"
    if not d.outra_rota(no):
        assert blocos == [{"prosa": d.resgate(no)}], (
            "sem material próprio, a segunda vez tem de trazer o resgate")


def test_a_primeira_vez_nao_traz_reexplicacao(d):
    """Ela é o que a SEGUNDA vez mostra. Trazer de primeira gasta o
    material e tira o sentido do botão."""
    t = _ate_a_construcao(d)
    assert t.tela.dados["reexplicacao"] == []


# --------------------------------------------------------------------------
# Entre artefatos: o cliente desenha blocos
# --------------------------------------------------------------------------

def _web(arquivo):
    import pathlib
    import re

    texto = (pathlib.Path(__file__).resolve().parent / "web" / arquivo
             ).read_text(encoding="utf-8")
    if arquivo.endswith(".html"):
        return re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", texto, flags=re.S)


def test_o_cliente_desenha_os_tres():
    js = _web("app.js")
    for campo in ("narracao", "caso_resolvido"):
        assert ("t." + campo) in js, "o cliente não lê `%s`" % campo


def test_o_cliente_distingue_prosa_de_codigo():
    """É a razão de os campos serem blocos. Se o cliente puser tudo como
    texto, o código sai colado e a mudança não serviu para nada.

    A primeira versão deste teste procurava as strings `"codigo"` e
    `"saida"` no arquivo — estava presa à forma da implementação, não ao
    contrato. O que importa é que o cliente LEIA os três tipos.
    """
    js = _web("app.js")
    for tipo in ("b.codigo", "b.saida", "b.prosa"):
        assert tipo in js, "o cliente não distingue o bloco `%s`" % tipo
    assert "<pre" in js or 'createElement("pre")' in js, (
        "nenhum bloco vira <pre>: o código sairia como parágrafo")


def test_os_elementos_existem_no_html():
    html = _web("index.html")
    for ident in ("ensino-narracao", "ensino-caso", "ensino-reexplicacao"):
        assert ('id="%s"' % ident) in html, "falta #%s" % ident
