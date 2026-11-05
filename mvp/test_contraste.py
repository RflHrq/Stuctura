# -*- coding: utf-8 -*-
"""A caixa de contraste da refutação: o que ela pode afirmar.

O defeito, achado atravessando o kc_02 como participante: a segunda tela
da refutação traz uma caixa com o rótulo

    AS PREMISSAS QUE VOCÊ ACABOU DE CONFIRMAR LEVAM A

e o mapa logo acima dizia **0 de 6 premissas de pé**. Era a primeira
atividade; nada havia sido confirmado.

MEDIDO nas 2.270 refutações da varredura dos treze tópicos: **1.050
acontecem com zero premissa confirmada — 46%.** O rótulo estava fixo no
HTML, sem condição nenhuma.

POR QUE É A PIOR FRASE POSSÍVEL PARA ESTAR ERRADA. A tese é refutar
CONDUZINDO a pessoa pelo grafo de premissas. Essa caixa **afirma que o
mecanismo aconteceu** em vez de executá-lo — é o plausível e errado que
este projeto persegue no dado há semanas, apontado para a pessoa.

E UM SEGUNDO DEFEITO NO MESMO RÓTULO: "confirmar" tem significado preciso
aqui — estado `CONFIRMADO`, duas superfícies diferentes, CS-5. Clicar
"faz sentido, continuar" numa tela de premissa não é confirmar. O rótulo
gastava o termo do instrumento com sentido frouxo, e quem lesse o log
depois encontraria "confirmado" querendo dizer duas coisas.
"""
from __future__ import annotations

import pathlib

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


def _refutando(d, no, crenca=None, confirmados=()):
    """O estado no ÚLTIMO passo da refutação de `no`."""
    e = motor.inicia(d, semente="P01").estado
    e = e.com(no, crenca=crenca or next(iter(d.crencas)))
    for nid in confirmados:
        e = e.com(nid, estado=motor.CONFIRMADO)
    t = motor._inicia_refutacao(d, e, no)
    e = t.estado
    while e.passo < len(e.plano) - 1:
        e = motor.replace(e, passo=e.passo + 1)
    return e


# --------------------------------------------------------------------------
# O caso dos 46%: nada percorrido, nada a afirmar
# --------------------------------------------------------------------------

def test_premissa_sem_suporte_nao_afirma_derivacao(d):
    """B1 não tem suporte: o plano tem um passo só, e não houve nada
    "antes" para a pessoa ter aceitado. A tela não pode alegar que houve.
    """
    no = next(n for n in d.ordem if not d.nos[n].suporte)
    e = _refutando(d, no)
    tela = motor._tela_refutacao(d, e)
    assert tela.dados["apoio"] == [], tela.dados["apoio"]


def test_sem_apoio_a_crenca_ainda_aparece(d):
    """Não afirmar a derivação não é esconder o contraste. A pessoa
    precisa ver de onde ela partiu — isso é a decisão 13, e vale aqui
    tanto quanto no falso positivo."""
    no = next(n for n in d.ordem if not d.nos[n].suporte)
    e = _refutando(d, no)
    tela = motor._tela_refutacao(d, e)
    assert tela.dados["contradiz"], "a crença sumiu junto com a alegação"


@pytest.mark.parametrize("topico", topicos())
def test_em_nenhum_topico_um_no_de_base_alega_apoio(topico):
    """Os nós de base são a origem dos 46%: em todo tópico, refutar um
    deles acontece sem percurso anterior."""
    dd = carrega(topico=topico)
    for no in dd.ordem:
        if dd.nos[no].suporte:
            continue
        e = _refutando(dd, no)
        assert motor._tela_refutacao(dd, e).dados["apoio"] == [], (topico, no)


# --------------------------------------------------------------------------
# Quando houve percurso, ele é NOMEADO — não só alegado
# --------------------------------------------------------------------------

def test_premissa_com_suporte_lista_o_que_foi_percorrido(d):
    """Um nó de inferência traz as premissas de suporte no plano, e a
    pessoa passou por elas clicando "faz sentido". Aí há o que citar — e
    a tela cita o TEXTO de cada uma, em vez de alegar que elas existem.
    """
    no = next(n for n in d.ordem if d.nos[n].suporte)
    e = _refutando(d, no)
    tela = motor._tela_refutacao(d, e)
    apoio = tela.dados["apoio"]
    assert apoio, no
    assert [x["no"] for x in apoio] == list(e.plano[:-1])
    for x in apoio:
        assert x["texto"] == d.nos[x["no"]].simples


def test_o_apoio_distingue_aceita_de_CONFIRMADA(d):
    """A distinção que o rótulo antigo apagava.

    `CONFIRMADO` é estado do instrumento: acerto com razão certa, em duas
    superfícies, com certeza (CS-5). Clicar "faz sentido" numa tela de
    premissa é ACEITAR. Chamar as duas de confirmar gastaria o termo, e o
    log ficaria com "confirmado" querendo dizer duas coisas.
    """
    no = next(n for n in d.ordem if d.nos[n].suporte)
    e = _refutando(d, no)
    primeiro = e.plano[0]

    sem = motor._tela_refutacao(d, e).dados["apoio"]
    assert all(x["confirmada"] is False for x in sem), sem

    e2 = _refutando(d, no, confirmados=(primeiro,))
    com = motor._tela_refutacao(d, e2).dados["apoio"]
    marcadas = [x["no"] for x in com if x["confirmada"]]
    assert marcadas == [primeiro], com


def test_o_apoio_so_traz_premissa_do_proprio_plano(d):
    """Um nó confirmado que NÃO sustenta o alvo não entra: citar premissa
    irrelevante como se sustentasse a conclusão seria a mesma mentira com
    outra roupa."""
    no = next(n for n in d.ordem if d.nos[n].suporte)
    e = _refutando(d, no)
    fora = [n for n in d.ordem if n not in e.plano]
    if not fora:
        pytest.skip("o plano deste nó cobre o tópico inteiro")
    e2 = _refutando(d, no, confirmados=(fora[0],))
    assert fora[0] not in [x["no"] for x in
                           motor._tela_refutacao(d, e2).dados["apoio"]]


def test_o_apoio_so_aparece_no_ultimo_passo(d):
    """Nos passos do meio a pessoa ainda está percorrendo: afirmar a
    conclusão ali seria dar o fim antes da hora."""
    no = next(n for n in d.ordem if len(motor._plano(d, n)) > 1)
    e = motor.inicia(d, semente="P01").estado.com(no, crenca=next(iter(d.crencas)))
    t = motor._inicia_refutacao(d, e, no)
    assert t.tela.dados["apoio"] == [], "o primeiro passo já alega apoio"
    assert t.tela.dados["contradiz"] == ""


# --------------------------------------------------------------------------
# A trava no HTML: o rótulo fixo não pode voltar
# --------------------------------------------------------------------------

def test_o_rotulo_mentiroso_nao_esta_mais_no_html():
    """A frase estava fixa em `index.html`, sem condição. Enquanto ela
    existir no markup, alguém pode religá-la sem passar pelo motor.

    Os COMENTÁRIOS saem antes da conferência: a primeira versão deste
    teste caiu no comentário que explica por que a frase foi embora —
    proibindo falar da coisa em vez de proibir usá-la, que é o mesmo
    defeito que o teste de AST do exportador já tinha pegado.
    """
    import re

    html = (pathlib.Path(__file__).resolve().parent / "web" / "index.html"
            ).read_text(encoding="utf-8")
    vivo = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    assert "acabou de confirmar" not in vivo, "o rótulo fixo voltou ao HTML"
    assert 'id="ref-rotulo-apoio"' in vivo, "o rótulo deixou de ser dado"


def test_o_js_monta_o_rotulo_a_partir_do_apoio():
    """O rótulo passa a ser dado, não markup: se o JS parar de ler
    `apoio`, a caixa volta a dizer o que quiser."""
    js = (pathlib.Path(__file__).resolve().parent / "web" / "app.js"
          ).read_text(encoding="utf-8")
    assert "apoio" in js, "o JS não lê o apoio que o motor manda"
