# -*- coding: utf-8 -*-
"""As seis descidas do kc_02, o tópico do piloto.

O kc_07 tem uma cadeia, de propósito: é o protótipo que provou o
mecanismo. O kc_02 é onde a pessoa vai atravessar no ensaio, e deixá-lo
com refutação afirmativa faria o ensaio medir explicação bem escrita, e
não a refutação interrogativa que o trabalho propõe.

O QUE ESTA SUÍTE FAZ DE DIFERENTE DA DO kc_07: ela **roda o compilador**.

O teste de evidência do kc_07 confere fragmentos de texto — que a saída
contém "array type", que o `onde` diz "gcc". Isso prova que alguém
escreveu aquilo, não que o compilador escreveu. Aqui `origem: gravada`
passa a ser uma afirmação VERIFICÁVEL: cada programa é compilado e
executado, e a saída é comparada com a que está no YAML. Onde não houver
compilador, os testes são PULADOS e dizem isso — evidência não conferida
não pode sair igual a evidência conferida.

O RISCO QUE ESTAS CADEIAS CARREGAM está declarado no cabeçalho do YAML e
vale repetir: pedir que alguém raciocine A PARTIR da própria crença pode
REFORÇÁ-LA se a cadeia não fechar. Nenhum teste aqui mede isso. O que
eles medem é que a cadeia existe, que ela não é circular, e que o fato
no fim dela é fato.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

from mvp import motor
from mvp.dominio import carrega

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import oraculo  # noqa: E402

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


# --------------------------------------------------------------------------
# Cobertura: o tópico do piloto não pode ter crença sem cadeia
# --------------------------------------------------------------------------

def test_as_seis_crencas_do_piloto_tem_descida(d):
    """Crença sem cadeia cai na refutação afirmativa, e aí metade do
    ensaio mediria um mecanismo e metade mediria outro — sem como saber
    qual parte do resultado veio de qual."""
    assert set(d.descidas) == set(d.crencas), (
        set(d.crencas) - set(d.descidas))


def test_toda_cadeia_tem_pelo_menos_tres_degraus(d):
    """Duas é o mínimo que o carregador aceita. Três é o mínimo que faz
    sentido: um passo para levar a crença a sério, um para esticá-la, e
    um para bater na parede."""
    for cid, de in d.descidas.items():
        assert len(de.passos) >= 3, (cid, len(de.passos))


# --------------------------------------------------------------------------
# Circularidade: a colisão não pode ser com a própria premissa negada
# --------------------------------------------------------------------------

def test_a_colisao_nao_e_a_premissa_que_a_crenca_nega(d):
    """O passo final tem de bater numa premissa DIFERENTE da que a crença
    nega.

    Se colidisse com a negada, a cadeia diria "sua ideia contradiz a
    ideia que ela contradiz" — verdadeiro, circular, e sem força nenhuma
    para quem acredita. A força vem de a contradição ser entre duas
    coisas que a PESSOA sustenta.
    """
    for cid, de in d.descidas.items():
        negada = d.crencas[cid].nega.split(":")[-1]
        assert de.colide_com != negada, (cid, negada)


def test_a_colisao_e_um_no_que_existe_no_topico(d):
    for cid, de in d.descidas.items():
        assert de.colide_com in d.nos, (cid, de.colide_com)


def test_nenhum_degrau_diz_a_pessoa_o_que_ela_disse(d):
    """Quem decide se a premissa foi confirmada é o MOTOR, que sabe o que
    esta sessão viu. Texto fixo dizendo "você disse" mentiria para quem
    não disse — e é a mesma classe do defeito da caixa de contraste, que
    alegava confirmação inexistente em 46% das refutações."""
    for cid, de in d.descidas.items():
        for i, p in enumerate(de.passos):
            junto = " ".join((p.pergunta, p.porque)).lower()
            for frase in ("você disse", "voce disse", "você afirmou",
                          "você confirmou", "como você já disse"):
                assert frase not in junto, (cid, i, frase)


# --------------------------------------------------------------------------
# O limite declarado do tópico
# --------------------------------------------------------------------------

def test_nenhuma_cadeia_usa_aritmetica_de_ponteiro(d):
    """`p + 1` é kc_11, e o cabeçalho do grafo deste tópico declara que
    ali a metáfora da rua CALA — endereços andam do tamanho do objeto,
    não de um em um. Refutar uma crença com uma ideia que o tópico não
    sustenta seria trocar um mal-entendido por outro."""
    import re

    proibido = re.compile(r"\bp\s*\+\s*1\b|\bp\+\+|\baritmética de ponteiro")
    for cid, de in d.descidas.items():
        for i, p in enumerate(de.passos):
            texto = " ".join((p.pergunta, p.decorre, p.verdade, p.porque))
            assert not proibido.search(texto), (cid, i)


# --------------------------------------------------------------------------
# A EVIDÊNCIA É RODADA, e é isto que separa esta suíte da do kc_07
# --------------------------------------------------------------------------

def test_toda_evidencia_se_declara_gravada(d):
    """Pendente é honesto quando não há compilador. Há um nesta máquina,
    então pendente aqui seria preguiça com nome de honestidade."""
    for cid, de in d.descidas.items():
        assert de.evidencia.origem == "gravada", (cid, de.evidencia.origem)


@tem_gcc
@pytest.mark.parametrize("cid", [
    "memory_is_by_name", "pointer_has_no_address", "pointer_is_data",
    "pointer_and_target_are_one", "pointer_is_pointless",
])
def test_a_saida_gravada_e_a_que_o_compilador_produz(d, cid):
    """O teste que torna `gravada` verificável.

    Compila e executa o programa que está no YAML e compara com a saída
    que o YAML promete. Se alguém editar o texto da tela sem rodar de
    novo, é aqui que cai — e a tela deixa de poder mostrar um terminal
    que nunca existiu.
    """
    ev = d.descidas[cid].evidencia
    passou, nota = oraculo.roda(ev.fonte, ev.saida)
    assert passou, (cid, nota)


@tem_gcc
def test_a_evidencia_de_erro_realmente_nao_compila(d):
    """`erro_de_compilacao` é a afirmação mais forte das três, e a mais
    fácil de errar: basta o compilador rebaixar para aviso e a tela passa
    a mostrar um erro que não acontece."""
    ev = d.descidas["pointer_is_integer"].evidencia
    assert ev.tipo == "erro_de_compilacao"
    passou, nota = oraculo.roda(ev.fonte, "", nao_compila=True)
    assert passou, nota
    assert "error:" in ev.saida, ev.saida


def test_a_evidencia_de_erro_guarda_a_garantia_do_padrao(d):
    """A mensagem é de cada compilador; a recusa é do padrão. Sem a
    garantia, a tela afirmaria o comportamento de um gcc específico como
    se fosse C — e o `onde` deste YAML registra que versões antigas
    rebaixam a mesma linha para aviso."""
    ev = d.descidas["pointer_is_integer"].evidencia
    assert "6.5.16.1" in ev.garantia, ev.garantia
    assert "aviso" in ev.onde, ev.onde


def test_o_programa_da_evidencia_compila_sozinho(d):
    """Excerto não é evidência de compilação: o que a tela mostra tem de
    ser o que foi compilado, inteiro."""
    for cid, de in d.descidas.items():
        assert "int main(void)" in de.evidencia.fonte, cid


# --------------------------------------------------------------------------
# A sessão inteira, com as seis ligadas
# --------------------------------------------------------------------------

@pytest.fixture
def ligada(monkeypatch):
    monkeypatch.setattr(motor, "DESCIDA_LIGADA", True)


def test_cada_crenca_entra_na_propria_descida(d, ligada):
    """Seis cadeias escritas e uma só alcançável seria pior que nenhuma:
    o ensaio mediria refutações de dois tipos sem saber qual foi qual."""
    for cid in d.crencas:
        no = d.crencas[cid].nega.split(":")[-1]
        e = motor.inicia(d, semente="P01").estado.com(no, crenca=cid)
        t = motor._inicia_descida(d, e, no, d.descida(cid))
        assert t.tela.tipo == "descida", cid
        assert t.tela.texto == d.descidas[cid].passos[0].pergunta, cid


# --------------------------------------------------------------------------
# O CORTE POR PREMISSA, e a lacuna que estas seis cadeias expuseram
# --------------------------------------------------------------------------
#
# `STRUCTURA_PREMISSAS` corta o tópico nos N PRIMEIROS nós, para rodar
# sessão curta. O carregador já descartava a descida cuja CRENÇA saiu no
# corte — mas não a que sobrevive apontando `colide_com` para um nó que
# saiu. Nesse caso o domínio inteiro deixava de carregar, com
# "colide_com não é nó deste tópico".
#
# A lacuna estava invisível porque a única cadeia que existia, a do
# kc_07, nega I3 e colide com B1: qualquer corte que a preserve preserva
# o B1 junto, por ele ser o primeiro. A primeira cadeia que nega o
# PRIMEIRO nó de um tópico derruba a carga — e `memory_is_by_name` nega
# o B1 do kc_02.
#
# Descartar é o conserto certo, e não "cortar menos": numa sessão que não
# tem a premissa da colisão, o último degrau não teria onde bater. A
# descida degrada para a refutação afirmativa, que é o que ela já faz em
# todo tópico sem cadeia.

@pytest.mark.parametrize("quantas", range(1, 7))
def test_cortar_o_topico_nao_derruba_a_carga(quantas):
    """A invariante que o `test_o_escopo_vale_para_todo_topico_e_todo_n`
    cobra, aqui com o motivo escrito ao lado."""
    dd = carrega(topico="kc_02", premissas=quantas)
    assert len(dd.nos) == quantas


@pytest.mark.parametrize("quantas", range(1, 7))
def test_a_descida_que_colide_fora_do_corte_e_descartada(quantas):
    """E descartada em silêncio não: descartada de verdade, de modo que
    `d.descida(crenca)` devolva None e o motor caia na refutação
    afirmativa."""
    dd = carrega(topico="kc_02", premissas=quantas)
    for cid, de in dd.descidas.items():
        assert de.colide_com in dd.nos, (quantas, cid, de.colide_com)


def test_no_topico_inteiro_as_seis_sobrevivem():
    """O conserto não pode descartar demais: sem corte, as seis ficam."""
    assert len(carrega(topico="kc_02").descidas) == 6
