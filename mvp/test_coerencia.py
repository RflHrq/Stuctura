# -*- coding: utf-8 -*-
"""Coerência curricular: nenhum item cobra o que o percurso não ensinou.

A OCORRÊNCIA QUE PEDIU ESTE ARQUIVO. O cartão do I2 do kc_02 deixou de
falar de aritmética de ponteiro — corretamente, porque isso é kc_11 e o
cabeçalho do grafo manda a metáfora calar ali. Mas **três itens do mesmo
nó continuaram cobrando `p + 1`**. O defeito não apareceu em teste
nenhum; apareceu porque alguém foi conferir à mão.

É o mesmo defeito que a auditoria de 05/11 já tinha nomeado, com outras
palavras: *"a pessoa é testada num construto que o sistema não
apresentou"*. Duas vezes a mesma coisa, achada do mesmo jeito — lendo.
Da terceira, o programa acha.

COMO ELE FUNCIONA, e por que é uma CATRACA e não um portão absoluto.
Varrido o domínio inteiro, há **67 itens** cujo código usa construto que
o inventário marca como não introduzido — quase todos
`funcao_com_parametro`, que é dívida antiga e declarada. Exigir zero
hoje reprovaria a suíte sem ninguém poder consertar, e teste que não se
pode fazer passar é teste que alguém desliga.

Então ele pina o número POR TÓPICO e falha quando ele CRESCE. Dívida
antiga não trava o trabalho; dívida nova não entra calada. Quando um
tópico for consertado, o número desce e a linha dele desce junto — e aí
a catraca segura o conserto.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest
import yaml

from mvp.dominio import carrega, topicos

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "scripts"))
from revisa_material import (CONSTRUTOS, cobrancas_sem_ensino,  # noqa: E402
                             contexto)

# Quantos itens de cada tópico cobram construto não introduzido, HOJE.
#
# Medido em 08/11/2026, depois de o kc_02 ter os três itens de
# aritmética resolvidos. Baixar um número é melhoria e exige baixar a
# linha; subir é regressão e o teste acusa.
#
# O kc_02 fica em 3 por uma razão escrita em `conceitos.yaml`: a
# ampliação do I3 EXPLICA passagem por valor, mas o I3 é nó de
# inferência e a abertura só ensina os observáveis — então a explicação
# chega a quem declara lacuna, e os itens cobram de todos. Dívida
# declarada, não escondida.
TETO = {
    "kc_00": 0, "kc_01": 0, "kc_02": 0, "kc_03": 2, "kc_04": 0,
    "kc_05": 0, "kc_06": 1, "kc_07": 0, "kc_08": 0, "kc_09": 0,
    "kc_10": 0, "kc_11": 0, "kc_12": 0,
}
# Total: 3 itens, e os três são `scanf`.
#
# ERAM 65, EM 11 DOS 13 TÓPICOS, até 12/11/2026. Sessenta e dois eram
# `funcao_com_parametro`, e todos saíram de uma vez — não por item
# movido nem por detector consertado, mas porque o construto passou a
# ter CARTÃO: a assinatura dos seis materiais do kc_06 liberou
# `funcao_com_parametro`, com `kc_06:B1` como evidência. É a baixa mais
# funda que esta catraca já registrou, e a única que veio de material
# novo.
#
# O que sobra é de outra natureza: `scanf` não tem cartão em tópico
# nenhum, e os três itens que o cobram continuam cobrando o que o
# sistema não apresentou.
#
# A LEITURA ANTIGA FICA, porque ela explicava por que o número do kc_06
# era 24: "ele se chama Passagem por referência, e cobrar função com
# parâmetro ali é inevitável — o tópico É sobre isso. O que falta é o
# conceito ter sido ensinado antes." Era isso mesmo, e foi isso que o
# cartão do B1 resolveu.
#
# A PRIMEIRA VERSÃO DESTES NÚMEROS FOI CHUTADA, e os doze testes que
# caíram foram quem avisou. Medidos em 08/11/2026.
#
# O KC_08 CAIU DE 3 PARA 1 EM 11/11/2026, e NÃO porque alguém ensinou
# alguma coisa: o padrão de `funcao_com_parametro` foi corrigido, e os
# dois itens que saíram eram FALSOS POSITIVOS. As linhas acusadas eram
#
#     ciu_kc08_008   for (int i = 0; i < 5; i++) *soma += i;
#     ciu_kc08_017   for (int i = 0; i < 1000; i++) guarda();
#
# O padrão antigo pedia UM nome antes do parêntese, e lia `for` como
# nome de função e `int i` como parâmetro. Definição tem tipo E nome —
# dois nomes; chamada e `for` têm um só. Está contado em
# `mvp/test_construto.py`.
#
# BAIXAR UM TETO POR CONSERTO DO DETECTOR é a única baixa que não é
# melhoria de material, e por isso ela vem com as duas linhas escritas
# aqui: baixar sem dizer qual item saiu seria afrouxar a catraca com
# cara de progresso.

_INVENTARIO = yaml.safe_load(
    (pathlib.Path(__file__).resolve().parent / "dominio" / "conceitos.yaml")
    .read_text(encoding="utf-8"))["conceitos"]

NAO_ENSINADO = ("nao_introduzido",)


def _descobertos(topico: str) -> list[tuple[str, str]]:
    """(item, conceito) de cada cobrança sem ensino naquele tópico."""
    d = carrega(topico=topico)
    fora = []
    for a in d.atividades:
        for padrao, cid in CONSTRUTOS:
            if not padrao.search(a.codigo or ""):
                continue
            estado = (_INVENTARIO.get(cid) or {}).get("status", "ausente")
            if estado in NAO_ENSINADO or cid not in _INVENTARIO:
                fora.append((a.id, cid))
    return fora


def _contexto_de(topico: str) -> str:
    """O contexto curricular de cada grupo, para a mensagem de falha.

    O NÚMERO SOZINHO NÃO DECIDE NADA. Medido: os seis achados do kc_02
    estão todos no I3, cuja premissa é "alcançar a caixa de outro ponto
    do programa"; e o kc_06, que se chama "Passagem por referência", tem
    quatro em CADA um dos seis nós, e as premissas dos seis falam de
    função e cópia. Nos dois o construto é inerente à premissa, e mover
    item não conserta nada. É a proporção que mostra isso.
    """
    dom = carrega(topico=topico)
    linhas = []
    for (no, cid), ids in sorted(cobrancas_sem_ensino(dom,
                                                      _INVENTARIO).items()):
        linhas.append("   " + contexto(dom, no, cid, ids))
        linhas.append("      " + ", ".join(sorted(ids)))
    return chr(10).join(linhas) or "   (nenhum)"


@pytest.mark.parametrize("topico", topicos())
def test_a_cobranca_sem_ensino_nao_cresce(topico):
    """A catraca."""
    achados = _descobertos(topico)
    teto = TETO.get(topico)
    assert teto is not None, (
        "%s não está em TETO: tópico novo entra com o número medido, e "
        "não sem linha" % topico)
    assert len(achados) <= teto, (
        "%s: %d itens cobram construto não introduzido, e o teto é %d.\n"
        "%s\n"
        "LEIA A PROPORÇÃO antes de decidir. Construto que aparece em "
        "quase todos os itens de um nó é INERENTE à premissa dele — "
        "mover o item não resolve, porque o nó depende do conceito, e o "
        "que falta é oportunidade anterior de aprendê-lo. Construto num "
        "item isolado é incidental, e aí o item muda ou sai."
        % (topico, len(achados), teto, _contexto_de(topico)))


@pytest.mark.parametrize("topico", topicos())
def test_o_teto_nao_esta_folgado(topico):
    """A outra metade da catraca.

    Teto acima do real deixa espaço para dívida nova entrar sem o
    primeiro teste acusar. Quando alguém conserta e não baixa a linha, a
    catraca para de segurar — e é aqui que isso aparece.
    """
    achados = _descobertos(topico)
    teto = TETO[topico]
    assert len(achados) == teto, (
        "%s: o teto diz %d e o real é %d. Se você consertou, baixe a "
        "linha em TETO; senão a catraca deixa de segurar." % (
            topico, teto, len(achados)))


def test_o_kc_02_nao_cobra_mais_aritmetica_de_ponteiro():
    """A ocorrência que originou este arquivo, pinada.

    O cartão do I2 não fala de aritmética, e três itens cobravam. Dois
    saíram (o kc_11 já os cobre, melhor colocados: `ciu_kc11_003` e
    `ciu_kc11_016`); o terceiro era pergunta do I2 cujo GABARITO se
    apoiava em `p + 1`, e o gabarito foi reescrito.
    """
    d = carrega(topico="kc_02")
    aritmetica = re.compile(r"[a-z]\s*\+\s*1\b|anda quantos bytes|"
                            r"andar uma posi", re.I)
    sujos = []
    for a in d.atividades:
        tudo = " ".join([a.codigo or "", a.enunciado]
                        + [o.texto for o in a.opcoes])
        if aritmetica.search(tudo):
            sujos.append(a.id)
    assert sujos == [], (
        "o kc_02 voltou a cobrar aritmética de ponteiro, que é kc_11: %s"
        % sujos)
