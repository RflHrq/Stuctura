# -*- coding: utf-8 -*-
"""A oportunidade de aprendizagem, por CONCEITO e não por nó.

O PRIMEIRO MECANISMO do histórico individual, de
`docs/historico-individual.md`: o log passar a dizer que CONCEITO um
cartão apresentou, e não só qual nó. Hoje `ensino_apresentado {no: B2}`
não diz que aquele cartão ensina `ponteiro` e `sizeof` — isso é verdade
do `conceitos.yaml`, e o log não a tem.

Este módulo guarda as duas peças que faltavam antes de qualquer evento:

    a DECLARAÇÃO    que cartão apresenta que conceito, legível por
                    máquina, derivada de onde a auditoria já escreveu
    a ASSINATURA    a versão do material daquele cartão, para o
                    histórico não mentir quando o material evoluir

POR QUE A DECLARAÇÃO É UM CAMPO NOVO e não uma varredura. A auditoria de
05/11 escreveu em `evidencia.onde` qual cartão ensina cada conceito — em
PROSA, porque quem aprova lê prosa. E ela achou TRÊS FALSOS POSITIVOS de
varredura por padrão (`derreferencia`, `sizeof`, `funcao_com_parametro`):
o construto estava num exemplo que ensina outra coisa. Varrer código
voltaria a achar os mesmos três. O campo estruturado fica ao LADO da
prosa, e a prosa continua sendo a evidência.

POR QUE A ASSINATURA É POR CARTÃO e não por arquivo. O cartão do B2 mora
em dois arquivos — a ampliação no `graph_`, a narração e o teste de mesa
no `activities_` —, e um sha do arquivo mudaria quando um item de outro
nó mudasse. A assinatura cobre o que a TELA mostra, e só isso: muda
quando o que a pessoa viu muda. Este projeto reescreveu dois cartões
inteiros numa noite; sem isso o histórico mente em silêncio.
"""
from __future__ import annotations

import pathlib

import pytest
import yaml
from dataclasses import replace

from mvp import conceitos
from mvp.dominio import carrega, topicos

DOMINIO = pathlib.Path(__file__).resolve().parent / "dominio"
_CRU = yaml.safe_load(
    (DOMINIO / "conceitos.yaml").read_text(encoding="utf-8"))["conceitos"]

# O que a auditoria de 05/11 e a de 08/11 escreveram em prosa, agora em
# forma de mapa. São os cinco conceitos `disponivel`, todos do kc_02.
CARTOES_ESPERADOS = {
    "endereco": ("kc_02:B1",),
    "ponteiro": ("kc_02:B2",),
    "operador_endereco": ("kc_02:B1", "kc_02:B2", "kc_02:B3"),
    "derreferencia": ("kc_02:B3",),
    "sizeof": ("kc_02:B2",),
}

# O mapa inverso, que é o que o evento vai consultar.
CONCEITOS_POR_CARTAO = {
    ("kc_02", "B1"): ("endereco", "operador_endereco"),
    ("kc_02", "B2"): ("operador_endereco", "ponteiro", "sizeof"),
    ("kc_02", "B3"): ("derreferencia", "operador_endereco"),
}

# `tipo` da evidência que significa ENSINO, e não menção. A auditoria usa
# cinco valores, e só estes dois autorizam declarar cartão.
ENSINA = ("explicacao_com_exemplo", "explicacao_com_leitura_e_escrita")


# --------------------------------------------------------------------------
# A declaração
# --------------------------------------------------------------------------

def test_todo_conceito_disponivel_declara_o_cartao_que_o_apresenta():
    """Sem isto o evento não tem de onde sair.

    A regra de liberação do inventário já exige que a explicação esteja
    no material; o que faltava era dizer EM QUE CARTÃO, de um jeito que
    o motor consiga ler.
    """
    sem = [cid for cid, v in _CRU.items()
           if v.get("status") == conceitos.DISPONIVEL
           and not ((v.get("evidencia") or {}).get("cartoes") or ())]
    assert not sem, (
        "conceito `disponivel` sem `evidencia.cartoes`: %s. A prosa de "
        "`onde` diz qual cartão é; o campo estruturado é o que o motor "
        "lê." % sem)


def test_os_cartoes_declarados_sao_os_que_a_auditoria_escreveu():
    medido = {cid: tuple((v.get("evidencia") or {}).get("cartoes") or ())
              for cid, v in _CRU.items()
              if (v.get("evidencia") or {}).get("cartoes")}
    assert medido == CARTOES_ESPERADOS, (
        "agora: %s" % sorted(medido.items()))


def test_todo_cartao_declarado_existe_de_verdade():
    """`kc_02:B2` tem de ser um nó de um tópico, não uma string plausível.

    Um id errado aqui faria o evento conceitual sair vazio em silêncio —
    e silêncio num log de pesquisa é dado perdido.
    """
    validos = set(topicos())
    nos = {t: set(carrega(topico=t).nos) for t in validos}
    fora = []
    for cid, v in _CRU.items():
        for cartao in (v.get("evidencia") or {}).get("cartoes") or ():
            if cartao.count(":") != 1:
                fora.append((cid, cartao, "formato"))
                continue
            topico, no = cartao.split(":")
            if topico not in validos:
                fora.append((cid, cartao, "tópico"))
            elif no not in nos[topico]:
                fora.append((cid, cartao, "nó"))
    assert not fora, fora


def test_so_quem_tem_explicacao_declara_cartao():
    """Usar não é ensinar, e o inventário já separava os dois.

    `printf_ponteiro` aparece nos três exemplos do kc_02 e não é
    explicado em lugar nenhum — `usado_sem_explicacao`. Se ele ganhasse
    `cartoes`, o histórico diria que a pessoa teve oportunidade de
    aprender o que ninguém lhe ensinou.
    """
    erradas = []
    for cid, v in _CRU.items():
        ev = v.get("evidencia") or {}
        tem = bool(ev.get("cartoes"))
        ensina = ev.get("tipo") in ENSINA
        if tem != ensina:
            erradas.append((cid, ev.get("tipo"), tem))
    assert not erradas, (
        "cartão declarado sem explicação, ou explicação sem cartão: %s"
        % erradas)


def test_o_cartao_declarado_bate_com_o_topico_que_introduziu():
    """`introduzido_em: kc_02` e `cartoes: [kc_07:B1]` seria contradição."""
    for cid, v in _CRU.items():
        cartoes = (v.get("evidencia") or {}).get("cartoes") or ()
        if not cartoes:
            continue
        de = {c.split(":")[0] for c in cartoes}
        assert de == {v.get("introduzido_em")}, (cid, de,
                                                 v.get("introduzido_em"))


# --------------------------------------------------------------------------
# O mapa inverso: o que o evento vai consultar
# --------------------------------------------------------------------------

def test_do_cartao_devolve_os_conceitos_daquele_cartao():
    for (topico, no), esperado in CONCEITOS_POR_CARTAO.items():
        assert conceitos.do_cartao(topico, no) == esperado, (topico, no)


def test_cartao_sem_conceito_declarado_devolve_vazio():
    """Doze dos treze tópicos não têm declaração nenhuma, e é verdade.

    A auditoria cobriu kc_00, kc_01 e kc_02. O evento conceitual vai sair
    VAZIO nos outros — e isso é o diagnóstico que a tese quer, não um
    defeito a esconder.
    """
    assert conceitos.do_cartao("kc_07", "B1") == ()
    assert conceitos.do_cartao("kc_02", "I3") == ()
    assert conceitos.do_cartao("kc_99", "B1") == ()


def test_cartoes_de_um_conceito_sai_do_inventario():
    assert conceitos.cartoes("operador_endereco") == ("kc_02:B1",
                                                      "kc_02:B2",
                                                      "kc_02:B3")
    assert conceitos.cartoes("scanf") == ()
    assert conceitos.cartoes("nao_existe") == ()


def test_o_mapa_inverso_cobre_todo_cartao_declarado():
    """Nenhum conceito declarado pode ficar fora do mapa que o motor lê."""
    do_inventario = {c for v in _CRU.values()
                     for c in (v.get("evidencia") or {}).get("cartoes") or ()}
    do_mapa = set()
    for cartao in do_inventario:
        topico, no = cartao.split(":")
        assert conceitos.do_cartao(topico, no), cartao
        do_mapa.add(cartao)
    assert do_mapa == do_inventario


# --------------------------------------------------------------------------
# A assinatura do material
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


def test_a_assinatura_tem_doze_caracteres_hex(d):
    """A mesma convenção do `revisado_sha` dos candidatos."""
    a = d.assinatura("B2")
    assert len(a) == 12, a
    assert all(c in "0123456789abcdef" for c in a), a


def test_a_assinatura_e_estavel(d):
    """Duas cargas do mesmo material dão a mesma assinatura.

    Sem isto a assinatura seria ruído: cada sessão gravaria um valor
    diferente para o mesmo cartão.
    """
    outra = carrega(topico="kc_02")
    for no in d.nos:
        assert d.assinatura(no) == outra.assinatura(no), no


@pytest.mark.parametrize("topico", topicos())
def test_cartoes_diferentes_tem_assinaturas_diferentes(topico):
    """E isto vale porque o ID DO NÓ NÃO entra na assinatura.

    A primeira versão punha o id no corpo do hash, e a sabotagem mostrou
    que era pior que inútil: com o id dentro, dois cartões de material
    idêntico sairiam com assinaturas diferentes e a duplicação ficaria
    escondida. Sem ele, este teste passa a afirmar algo sobre o
    MATERIAL — que nos treze tópicos não há dois cartões iguais.
    """
    dom = carrega(topico=topico)
    assinaturas = {no: dom.assinatura(no) for no in dom.nos}
    repetidas = {}
    for no, a in assinaturas.items():
        repetidas.setdefault(a, []).append(no)
    iguais = [v for v in repetidas.values() if len(v) > 1]
    assert not iguais, (
        "%s: estes cartões têm material IDÊNTICO: %s. Dois nós com o "
        "mesmo cartão é defeito de conteúdo, e a assinatura é o que o "
        "mostra." % (topico, iguais))


def test_a_assinatura_cobre_tudo_o_que_a_tela_do_cartao_mostra(d):
    """O teste que mantém a assinatura honesta quando o cartão crescer.

    As duas telas de ensino mandam sete campos de CONTEÚDO: a frase, a
    ampliação, o exemplo, o resgate, a narração, o teste de mesa e o
    material da segunda vez. Mexer em qualquer um muda o que a pessoa vê
    — e tem de mudar a assinatura. Campo novo no cartão sem entrar aqui
    é histórico mentindo em silêncio, que é o defeito que a assinatura
    existe para impedir.
    """
    antes = d.assinatura("B2")
    no = d.nos["B2"]

    mudancas = {
        "simples": replace(d, nos={**d.nos,
                                   "B2": replace(no, simples="outra frase")}),
        "interpretacao": replace(
            d, nos={**d.nos, "B2": replace(no, interpretacao="outra")}),
        "texto": replace(d, nos={**d.nos,
                                 "B2": replace(no, texto="outro texto")}),
        "exemplo": replace(d, exemplos={**d.exemplos, "B2": "int z = 1;"}),
        "resgate": replace(d, resgates={**d.resgates, "B2": "outra analogia"}),
        "narracao": replace(d, narracoes={**d.narracoes,
                                          "B2": ({"prosa": "outra"},)}),
        "caso_resolvido": replace(
            d, casos_resolvidos={**d.casos_resolvidos,
                                 "B2": ({"prosa": "outro caso"},)}),
        "outra_rota": replace(d, outras_rotas={**d.outras_rotas,
                                               "B2": ({"prosa": "outra"},)}),
        "teste_de_mesa": replace(
            d, testes_de_mesa={**d.testes_de_mesa,
                               "B2": {"colunas": ["x"],
                                      "linhas": [{"codigo": "int x;",
                                                  "valores": {"x": "?"}}]}}),
    }
    for campo, mexido in mudancas.items():
        assert mexido.assinatura("B2") != antes, (
            "mexer em `%s` não mudou a assinatura do cartão: o histórico "
            "não saberia que a pessoa viu outra coisa" % campo)


def test_mexer_em_outro_no_nao_muda_a_assinatura(d):
    """É por isso que a assinatura é do CARTÃO, e não do arquivo.

    Reescrever o B1 não pode mudar a assinatura do B2: quem viu o B2
    ontem viu o mesmo B2.
    """
    antes = d.assinatura("B2")
    mexido = replace(d, nos={**d.nos,
                             "B1": replace(d.nos["B1"], simples="outra")})
    assert mexido.assinatura("B2") == antes


def test_a_assinatura_nao_depende_do_momento_nem_da_repeticao(d):
    """O que a tela manda em `reexplicacao` depende de quantas vezes a
    pessoa pediu de novo. A assinatura cobre TODAS as rotas do cartão, e
    não a mostrada agora — senão o mesmo cartão teria três assinaturas
    na mesma sessão."""
    a = d.assinatura("B2")
    for _ in range(3):
        assert d.assinatura("B2") == a


@pytest.mark.parametrize("topico", topicos())
def test_todo_no_dos_treze_topicos_tem_assinatura(topico):
    """Inclusive os cartões rasos: assinatura vazia esconderia o caso em
    que o material não existe, que é justo o que precisa aparecer."""
    dom = carrega(topico=topico)
    for no in dom.nos:
        assert len(dom.assinatura(no)) == 12, (topico, no)
