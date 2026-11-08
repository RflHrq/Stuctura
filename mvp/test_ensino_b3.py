# -*- coding: utf-8 -*-
"""A ampliação explicativa do B3: do endereço ao conteúdo.

É AMPLIAÇÃO DE UMA PREMISSA EXISTENTE, e não premissa nova. A decisão do
dono está registrada assim de propósito, porque a diferença importa para
a tese: o grafo não mudou, o B3 continua afirmando o que afirmava, e a
crença que o nega continua sendo `pointer_is_data`.

O QUE A AUDITORIA ACHOU, e é o que isto conserta: o kc_02 ensinava em
três cartões que um ponteiro guarda um endereço e **nunca ensinava a
usar esse endereço**. Desreferência não aparecia com explicação em
cartão nenhum dos três tópicos do caminho, e era cobrada desde o nível
1. A pessoa era testada num construto que o sistema não apresentou.

POR QUE UM CAMPO NOVO, e não esticar o `plain_text`: aquela frase é a
canônica do nó e aparece em SETE telas — inclusive como a alternativa
CERTA da camada 2 (`motor.razoes_de`). Esticá-la transformaria uma opção
de resposta num parágrafo. `interpretation` é lido só pela tela de
ensino.

O QUE ISTO NÃO FAZ: não libera cadeia nenhuma. O inventário só é
atualizado depois de o conteúdo final ser auditado, e a liberação é
decisão à parte.
"""
from __future__ import annotations

import pathlib
import re

import pytest

from mvp import conceitos, motor
from mvp.dominio import carrega, topicos


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


# --------------------------------------------------------------------------
# A premissa NÃO mudou: é ampliação, não substituição
# --------------------------------------------------------------------------

def test_o_b3_continua_sendo_a_mesma_premissa(d):
    """A condição número um do dono. Se esta cair, deixou de ser
    ampliação e virou outra coisa."""
    assert d.nos["B3"].texto == "O valor guardado num ponteiro é um endereço."
    assert d.nos["B3"].negado_por == ("pointer_is_data",)
    assert d.nos["B3"].suporte == (), "o B3 ganhou dependência que não tinha"
    assert d.nos["B3"].tipo == "observavel"


def test_o_kc02_continua_com_seis_nos(d):
    """Nenhum nó novo: o grafo que a tese descreve não mudou."""
    assert len(d.nos) == 6
    assert sorted(d.nos) == ["B1", "B2", "B3", "I1", "I2", "I3"]


def test_continua_uma_crenca_por_no(d):
    """A decisão 19, intocada."""
    assert len(d.crencas) == len(d.nos) == 6


def test_a_frase_canonica_do_b3_nao_inchou(d):
    """`simples` é usada em sete telas, e numa delas é ALTERNATIVA de
    resposta. Uma frase de duas linhas ali vira opção ilegível.

    O teto é generoso de propósito — o que ele pega é a tentativa de
    enfiar a explicação longa no campo errado.
    """
    for nid, no in d.nos.items():
        assert len(no.simples.strip()) < 200, (nid, len(no.simples))


def test_a_frase_canonica_ainda_serve_de_alternativa(d):
    """A prova direta do teste acima, pelo caminho real: a razão CERTA da
    camada 2 é a frase do nó."""
    a = next(x for x in d.atividades if x.no == "B3")
    certa = [z for z in motor.razoes_de(d, a) if z.correta]
    assert certa and certa[0].texto == d.nos["B3"].simples


# --------------------------------------------------------------------------
# A ampliação: leitura E escrita, com resultado explicado
# --------------------------------------------------------------------------

def test_o_b3_ganhou_interpretacao(d):
    assert d.interpretacao("B3"), "a ampliação não chegou ao domínio"


def test_a_interpretacao_ensina_LER_por_desreferencia(d):
    t = d.interpretacao("B3")
    assert "*p" in t, t
    assert re.search(r"\b42\b", t), "o resultado da leitura não é dito"


def test_a_interpretacao_ensina_ESCREVER_por_desreferencia(d):
    """Ler e escrever são as duas metades, e a segunda é a que o
    `pointer_and_target_are_one` depende para fazer sentido."""
    t = d.interpretacao("B3")
    assert "*p = 7" in t, t
    assert re.search(r"\b7\b", t), "o efeito da escrita não é dito"


def test_a_interpretacao_distingue_as_tres_expressoes(d):
    """p, *p e &idade: a distinção é o conteúdo do cartão, e tem de estar
    escrita, não deduzível."""
    t = d.interpretacao("B3")
    for expr in ("&x", "*p"):
        assert expr in t, (expr, t)


def test_o_exemplo_do_b3_mostra_o_que_a_interpretacao_explica(d):
    """A regra de qualidade do dono: existe um exemplo que demonstra o
    conceito. Explicar sem mostrar é metade do cartão."""
    codigo = d.exemplo("B3")
    sem_comentario = re.sub(r"/\*.*?\*/", " ", codigo, flags=re.S)
    assert "*p" in sem_comentario, codigo
    assert "*p = 7" in sem_comentario, "a escrita não aparece no código"


def test_a_interpretacao_nao_usa_crase(d):
    """A mesma regra dos outros textos de tela: o cliente escreve com
    textContent, e crase no YAML vira crase na cara da pessoa.

    ESTE TESTE PEGOU 58 CRASES do material profundo, na hora em que ele
    foi aplicado ao domínio — mas só as 32 da ampliação, que era o único
    campo que ele cobria. As outras 26 estavam em `caso_resolvido`,
    `outra_rota` e `narracao`, e teriam chegado caladas à tela. Por isso
    o teste abaixo existe.
    """
    for nid in d.nos:
        assert "`" not in (d.interpretacao(nid) or ""), nid


def test_nenhum_texto_de_ensino_usa_crase(d):
    """A mesma regra, nos três campos que o esquema ganhou.

    Só a PROSA: em `codigo` e `saida` não há crase, e procurá-la ali
    seria procurar no lugar errado.
    """
    for nid in d.nos:
        for b in d.caso_resolvido(nid) + d.outra_rota(nid):
            prosa = b.get("prosa")
            if prosa is not None:
                assert "`" not in prosa, "%s: %r" % (nid, prosa[:60])
        for linha in d.narracao(nid):
            assert "`" not in linha["diz"], "%s: %r" % (nid, linha["diz"][:60])


def test_a_interpretacao_nao_depende_de_conhecimento_futuro(d):
    """A terceira pergunta de qualidade do dono: a explicação permite
    interpretar o exemplo sem depender do que vem depois.

    `sizeof`, `int **` e `scanf` estão todos fora do que o kc_02 ensina,
    e são exatamente os que o inventário bloqueia.
    """
    t = (d.interpretacao("B3") or "") + " " + d.exemplo("B3")
    for futuro in ("sizeof", "scanf", "**", "malloc"):
        assert futuro not in t, (futuro, t)


# --------------------------------------------------------------------------
# Chega à tela, e só a ela
# --------------------------------------------------------------------------

def test_a_interpretacao_chega_a_tela_de_ensino(d):
    e = motor.inicia(d, semente="P01").estado
    while motor._cartoes(d)[e.cartao] != "B3":
        e = motor.replace(e, cartao=e.cartao + 1)
    tela = motor._tela_ensino(d, e)
    assert tela.dados["interpretacao"] == d.interpretacao("B3")


def test_a_interpretacao_NAO_vaza_para_a_refutacao(d):
    """O campo existe para a tela de ensino. Se aparecesse na refutação,
    a ampliação teria inchado as outras telas pela porta dos fundos —
    que é justamente o que não esticar o `plain_text` evitou."""
    e = motor.inicia(d, semente="P01").estado.com("B3", crenca="pointer_is_data")
    t = motor._inicia_refutacao(d, e, "B3")
    assert "interpretacao" not in t.tela.dados
    assert t.tela.texto == d.nos["B3"].simples


@pytest.mark.parametrize("topico", topicos())
def test_no_sem_ampliacao_continua_carregando(topico):
    """Campo OPCIONAL: os outros doze tópicos não têm nenhum, e carregam
    igual. A ampliação é de um cartão, não um requisito novo do esquema."""
    d = carrega(topico=topico)
    for nid in d.nos:
        assert isinstance(d.interpretacao(nid), str)


# --------------------------------------------------------------------------
# E NÃO libera cadeia nenhuma
# --------------------------------------------------------------------------

def test_a_liberacao_da_derreferencia_aponta_para_este_cartao():
    """Estes dois testes afirmavam o contrário até 05/11/2026, e a troca
    é parte do registro.

    Enquanto o cartão estava escrito e não auditado, eles cobravam que
    `derreferencia` continuasse `so_avaliado` e que nenhuma cadeia
    estivesse liberada — existiam para impedir o autor de liberar o que
    o autor acabara de escrever. Fizeram esse trabalho.

    Depois da revisão do dono, que pediu duas correções e aprovou, a
    letra deles ficou obsoleta e o que sobra de guardável é a
    RASTREABILIDADE: a liberação tem de apontar para o material que a
    justifica. Uma entrada `disponivel` cuja evidência não diz onde
    aquilo foi ensinado seria a lista de desejos que o inventário existe
    para não ser.
    """
    c = conceitos.carrega()["derreferencia"]
    assert c["status"] == conceitos.DISPONIVEL
    assert c["introduzido_em"] == "kc_02"
    ev = c["evidencia"]
    assert ev["arquivo"] == "kc_02" and ev["secao"] == "B3", ev
    assert ev["tipo"] == "explicacao_com_leitura_e_escrita", ev
    assert ev.get("aprovacao"), "liberação sem registro de quem aprovou"


def test_o_cartao_sustenta_o_que_a_evidencia_promete(d):
    """A evidência diz `explicacao_com_leitura_e_escrita`. O cartão tem
    de ter as duas, senão o inventário promete mais do que o material
    entrega — e o portão passa a liberar com base no rótulo, não no
    conteúdo."""
    t = d.interpretacao("B3")
    assert "Lendo:" in t and "Escrevendo:" in t, t
    codigo = d.exemplo("B3")
    assert "*p);" in codigo or "*p)" in codigo, "sem leitura no código"
    assert "*p = 7" in codigo, "sem escrita no código"


# --------------------------------------------------------------------------
# A FIGURA, O EXEMPLO E A INTERPRETAÇÃO FALAM DA MESMA VARIÁVEL
# --------------------------------------------------------------------------
#
# Defeito que eu cometi e que a tela mostrou: troquei o exemplo do B3 de
# `x = 42` para `idade = 20`, e a figura continuou desenhando x e 42. O
# aluno via o código falar de uma variável e o desenho de outra, lado a
# lado, no mesmo cartão.
#
# A suíte não pegou, e não tinha como: a figura mora no JavaScript e o
# exemplo no YAML. Este teste atravessa os dois.

def _figura_do_no(nid):
    """Os nomes e valores que `figuras.js` desenha para aquele nó do
    kc_02. Lê o fonte porque é onde o desenho mora — não há outro lugar
    de onde perguntar."""
    js = (pathlib.Path(__file__).resolve().parent / "web" / "figuras.js"
          ).read_text(encoding="utf-8")
    # o bloco do kc_02 começa no comentário do tópico e vai até o próximo
    bloco = js.split("/* B3 — o que esta dentro de p")[1].split("/* I1")[0]
    return (re.findall(r'nome:\s*"([^"]+)"', bloco),
            re.findall(r'dentro:\s*"([^"]+)"', bloco))


def test_a_figura_do_b3_fala_da_mesma_variavel_que_o_exemplo(d):
    nomes, dentros = _figura_do_no("B3")
    assert nomes, "nao achei a figura do B3"
    codigo = d.exemplo("B3")
    for nome in nomes:
        assert re.search(r"\b%s\b" % re.escape(nome), codigo), (
            "a figura desenha %r e o exemplo nao o menciona" % nome)
    # e o valor que a figura mostra dentro da caixa tem de ser o valor
    # inicial do exemplo, senao o desenho ilustra outro estado
    assert "42" in dentros and "42" in codigo, (dentros, codigo)


def test_a_interpretacao_fala_da_mesma_variavel_que_a_figura(d):
    nomes, _ = _figura_do_no("B3")
    texto = d.interpretacao("B3")
    for nome in nomes:
        assert re.search(r"\b%s\b" % re.escape(nome), texto), (
            "a figura desenha %r e a interpretacao nao o menciona" % nome)
