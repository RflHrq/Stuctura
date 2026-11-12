# -*- coding: utf-8 -*-
"""Cada premissa do grafo é conferida pelo compilador, não pela prosa.

A LACUNA QUE PEDIU ESTE ARQUIVO, 11/11/2026. O catálogo de crenças tem
campo de procedência, cinco graus e dez travas — e os **79 nós do grafo
não têm campo de fonte nenhum**. Um nó tem `type`, `role`, `support`,
`text`, `plain_text`, `negated_by`, e nada mais.

Isso deixa a tese do projeto validada pela metade: o que o sistema
REFUTA está ancorado na literatura, e o que ele refuta COM é prosa
escrita à mão. O carregador confere a ESTRUTURA — nó de inferência tem
de ter suporte, crença tem de negar um nó que existe — e nunca a
verdade.

E A VALIDAÇÃO DA PREMISSA NÃO É LITERATURA. Uma crença é afirmação
sobre o que estudantes pensam, e quem a sustenta é o estudo empírico.
Uma premissa é afirmação sobre C, e quem a sustenta é o compilador.
Procurar premissa no Sorva seria a mesma confusão de categoria que
procurar concepção errônea no padrão da linguagem.

O CAMPO É `evidencia`, uma LISTA de demonstrações, cada uma com a forma
que o oráculo já conhece dos moldes: `programa` mais `espera`, ou
`programa` mais `nao_compila` quando a demonstração é o compilador
RECUSAR. O oráculo não mudou para isto — ele já provava as duas coisas.

E É LISTA, E NÃO UMA SÓ, porque o I2 pediu. A premissa dele tem duas
metades — "um ponteiro TEM TIPO, e por isso NÃO É um inteiro qualquer"
—, e elas se demonstram por caminhos opostos: a primeira por saída de
programa (somar 1 anda um tamanho diferente em cada tipo), a segunda
pela RECUSA do compilador (`int n = p;` não compila). Com campo único,
uma das duas metades ficaria de fora, e seria a segunda — a que dá nome
à premissa.

E O PROGRAMA AFIRMA A PREMISSA EM PALAVRAS. A saída esperada não é um
número solto: é a frase da premissa, que o programa imprime se, e
somente se, a comparação for verdadeira; caso contrário imprime
"FALHOU". Assim a evidência é legível por quem lê a monografia, e a
reprovação do oráculo é legível por quem for consertar.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOMINIO = RAIZ / "mvp" / "dominio"
sys.path.insert(0, str(RAIZ / "scripts"))

# Os tópicos cujos nós já têm evidência. A lista cresce um tópico por
# vez, e é ela que impede que "ainda não chegou neste" se confunda com
# "este não precisa".
#
# O kc_06 ENTROU EM 12/11/2026, e com ele o primeiro tópico cujas seis
# premissas têm demonstração que CHEGA à tela: treze programas, sete
# barrados pelo portão de exibição — todos pelo mesmo construto,
# `funcao_com_parametro` — e seis exibíveis, um por nó.
#
# E NO MESMO DIA OS OUTROS ONZE TÓPICOS, e depois a terceira forma do
# contrato — a do compilador que DIAGNOSTICA sem recusar, que destravou
# oito nós de comportamento indefinido. São 93 demonstrações em 78 dos
# 79 nós, e doze dos treze tópicos ficam COMPLETOS.
#
# O ÚNICO DE FORA É O kc_05, pelo I3 dele: `*p` com p nulo. O gcc não
# diagnostica isso com -std=c17 -Wall -c (`-Wnull-dereference` pede
# otimização), e as outras duas formas não alcançam a premissa. Esta
# lista é o que impede "ainda não chegou neste" de se confundir com
# "este não precisa".
COM_EVIDENCIA = ("kc_00", "kc_01", "kc_02", "kc_03", "kc_04", "kc_06",
                 "kc_07", "kc_08", "kc_09", "kc_10", "kc_11", "kc_12")


def _nos(topico):
    arq = DOMINIO / ("graph_%s.yaml" % topico.replace("_", ""))
    return yaml.safe_load(arq.read_text(encoding="utf-8"))["nodes"]


def _evidencias(topico, nid):
    """A lista de demonstrações do nó, sempre lista.

    Um mapeamento solto é recusado em vez de embrulhado: aceitar as duas
    formas faria um arquivo escrito de um jeito e outro de outro, e a
    próxima pessoa teria de descobrir qual lendo o código.
    """
    ev = _nos(topico)[nid].get("evidencia")
    assert ev is None or isinstance(ev, list), (
        "a `evidencia` de %s:%s não é lista. Mesmo com uma demonstração "
        "só, o campo é lista — foi o I2 que mostrou por quê." % (topico, nid))
    return ev or []


def _casos():
    for t in COM_EVIDENCIA:
        for nid in _nos(t):
            yield t, nid


def _demonstracoes():
    for t, nid in _casos():
        for i, dem in enumerate(_evidencias(t, nid)):
            yield t, nid, i, dem


@pytest.mark.parametrize("topico,nid", list(_casos()))
def test_a_premissa_tem_evidencia(topico, nid):
    """Sem o campo, não há o que conferir — e o silêncio pareceria aprovação."""
    no = _nos(topico)[nid]
    dems = _evidencias(topico, nid)
    assert dems, (
        "o nó %s:%s não tem `evidencia`. A premissa dele é uma afirmação "
        "sobre C que ninguém conferiu: %r"
        % (topico, nid, " ".join(no["text"].split())))
    for i, dem in enumerate(dems):
        assert dem.get("programa"), (topico, nid, i, "demonstração sem programa")
        assert dem.get("afirma"), (
            topico, nid, i,
            "demonstração sem `afirma`: qual metade da premissa ela prova? "
            "Sem isso, duas demonstrações do mesmo nó ficam indistinguíveis "
            "para quem lê.")
        if dem.get("avisa"):
            # A TERCEIRA FORMA tem travas próprias, logo abaixo:
            # `test_a_terceira_forma_...` compila e confere o
            # diagnóstico, e `test_a_demonstracao_por_aviso_nunca_...`
            # cobra `ambiente` e proíbe `espera`. Exigir saída aqui
            # seria exigir que ela rodasse, que é o que ela não pode.
            continue
        if dem.get("nao_compila"):
            assert not dem.get("espera"), (
                topico, nid, i,
                "demonstração por recusa do compilador não tem saída a "
                "esperar — e prometer uma esconderia o que se está provando")
        else:
            assert dem.get("espera"), (
                topico, nid, i,
                "demonstração sem `espera`: programa que roda e não diz o "
                "que tem de sair não confere nada")


@pytest.mark.parametrize("topico,nid,i,dem", list(_demonstracoes()))
def test_o_compilador_confirma_a_premissa(topico, nid, i, dem):
    """A trava. O oráculo compila, roda, e compara com o prometido.

    Se o compilador contradisser a premissa, este teste cai — e é o
    único jeito de descobrir que uma premissa do grafo é falsa sem que
    um participante descubra primeiro.

    A TERCEIRA FORMA NÃO PASSA POR AQUI, e não por conveniência: o
    oráculo RODA o programa, e o programa dela existe porque executá-lo
    é o comportamento indefinido que a premissa descreve. Quem a confere
    é `test_a_terceira_forma_o_compilador_diagnostica_sem_recusar`, que
    compila e lê o diagnóstico sem executar nada.
    """
    if dem.get("avisa"):
        pytest.skip("prova por aviso: conferida sem executar, logo abaixo")
    import oraculo

    try:
        passou, nota = oraculo.roda(
            dem["programa"], dem.get("espera") or "",
            nao_compila=bool(dem.get("nao_compila")))
    except oraculo.SemCompilador as e:
        pytest.skip(str(e))
    assert passou, (
        "o compilador NÃO confirma a premissa do nó %s:%s (demonstração %d).\n"
        "  premissa: %s\n  afirma:   %s\n  oráculo:  %s"
        % (topico, nid, i, " ".join(_nos(topico)[nid]["text"].split()),
           " ".join(str(dem.get("afirma")).split()), nota))


@pytest.mark.parametrize("topico,nid,i,dem", list(_demonstracoes()))
def test_a_saida_esperada_afirma_a_premissa_e_nao_falha(topico, nid, i, dem):
    """"FALHOU" na saída esperada seria prometer a premissa falsa.

    O programa imprime a frase se a comparação for verdadeira e
    "FALHOU" se não for. Se `espera` trouxesse "FALHOU", o oráculo
    aprovaria um programa que demonstra o CONTRÁRIO da premissa — e
    aprovaria em silêncio, que é o pior jeito de errar.
    """
    espera = dem.get("espera") or ""
    assert "FALHOU" not in espera, (
        topico, nid, i, "a saída esperada contém FALHOU: %r" % espera)
    if not dem.get("nao_compila") and not dem.get("avisa"):
        assert "FALHOU" in dem["programa"], (
            topico, nid, i,
            "o programa não tem ramo FALHOU. Sem ele, uma premissa falsa "
            "sairia como saída diferente — e a nota do oráculo diria "
            "'saiu X, e o molde promete Y' em vez de dizer que a premissa "
            "não se sustenta.")


def _avisos():
    for t, nid, i, dem in _demonstracoes():
        if dem.get("avisa"):
            yield t, nid, i, dem


@pytest.mark.parametrize("topico,nid,i,dem", list(_avisos()) or [(None,) * 4])
def test_a_terceira_forma_o_compilador_diagnostica_sem_recusar(topico, nid, i, dem):
    """A forma que os nove nós de comportamento indefinido pediram.

    NOVE PREMISSAS DO PROJETO não se demonstram por nenhuma das duas
    formas antigas — kc_00:B3, kc_03:B3/I2/I3, kc_05:I3, kc_08:B3,
    kc_09:B4/I4, kc_12:I1. Todas falam de valor indeterminado ou de
    comportamento indefinido: "contém lixo", "usar p depois do free",
    "retornar &local". Rodar o programa exibiria o próprio UB como
    prova, que é o contrário de ensinar; e o compilador não RECUSA,
    porque o padrão não exige recusa — exige diagnóstico.

    ENTÃO A TERCEIRA FORMA É O DIAGNÓSTICO: o programa compila, o
    compilador avisa, e o programa NÃO É EXECUTADO. Não executar não é
    economia: é a premissa. Este teste compila e confere a mensagem; se
    algum dia ele rodasse o programa, estaria fazendo o que o nó ensina
    a não fazer.
    """
    if topico is None:
        pytest.skip("nenhuma demonstração por aviso ainda")
    import subprocess
    import tempfile

    import oraculo

    if not oraculo.GCC.exists():
        pytest.skip("sem compilador")
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "o.c").write_text(dem["programa"], encoding="utf-8")
        r = subprocess.run(
            [str(oraculo.GCC), "-std=c17", "-Wall", "-c", "-o", "o.obj", "o.c"],
            capture_output=True, text=True, timeout=oraculo.TEMPO, cwd=str(p))
    assert r.returncode == 0, (
        "a demonstração por aviso de %s:%s[%d] NÃO COMPILA — e aí ela é "
        "prova por recusa, que é a outra forma:\n%s"
        % (topico, nid, i, r.stderr[-400:]))
    # O YAML lido CRU traz o bloco `>` com quebra no fim; a carga
    # normaliza, este teste não passa pela carga.
    promete = " ".join(str(dem["avisa"]).split())
    assert promete.lower() in r.stderr.lower(), (
        "o compilador NÃO disse o que %s:%s[%d] promete.\n"
        "  promete: %s\n  disse:   %s"
        % (topico, nid, i, promete, r.stderr.strip()[-400:] or "(nada)"))


def test_a_demonstracao_por_aviso_nunca_promete_saida():
    """Prometer saída seria dizer que o programa pode rodar.

    É a trava que separa a terceira forma da primeira: o programa da
    terceira existe porque executá-lo é comportamento indefinido.
    """
    for topico, nid, i, dem in _avisos():
        assert not dem.get("espera"), (topico, nid, i)
        assert not dem.get("nao_compila"), (topico, nid, i)
        assert dem.get("ambiente"), (
            topico, nid, i,
            "aviso sem `ambiente`: diagnóstico é fato sobre um compilador")


def test_a_carga_recusa_aviso_malformado():
    """A carga é onde isto falha, e não o teste.

    Mesma razão do resto da `evidencia`: a prova vai para a tela de quem
    está sendo refutado, e uma prova que promete saída de um programa
    que não pode rodar mostraria à pessoa uma demonstração que não
    demonstra.
    """
    from mvp import dominio

    def problemas_de(dem):
        p = []
        dominio._demonstracoes("X", [dict(afirma="a", programa="int main(void){}",
                                          **dem)], p)
        return " ".join(p)

    assert "ambiente" in problemas_de({"avisa": "uninitialized"})
    assert "saída" in problemas_de({"avisa": "uninitialized", "ambiente": "gcc",
                                    "espera": "oi"})
    assert "recusa" in problemas_de({"avisa": "uninitialized", "ambiente": "gcc",
                                     "nao_compila": True})
    assert not problemas_de({"avisa": "uninitialized", "ambiente": "gcc 16"})


def test_demonstracao_por_recusa_declara_o_ambiente():
    """Recusa é fato sobre um COMPILADOR, não sobre a linguagem.

    O caso é o `int n = p;` do I2. Com o gcc desta máquina ele é
    `error:` e não compila. Em gcc anterior ao 14 a mesma linha é só
    AVISO, e o programa compila — a conversão implícita entre inteiro e
    ponteiro é violação de restrição da linguagem, e o que o padrão
    exige de todo compilador conforme é um DIAGNÓSTICO, não a recusa de
    traduzir.

    Então uma demonstração por recusa que não diga em que compilador
    recusou afirma sobre C o que só vale ali. O campo `ambiente` é o
    conserto, e esta trava existe porque o próprio histórico deste nó
    registra que o projeto já afirmou "o compilador recusa" uma vez e
    teve de voltar atrás.
    """
    fora = []
    for topico, nid, i, dem in _demonstracoes():
        if not dem.get("nao_compila"):
            continue
        amb = " ".join(str(dem.get("ambiente") or "").split())
        if len(amb) < 20:
            fora.append((topico, nid, i, amb))
    assert not fora, (
        "demonstração por recusa sem `ambiente` que a situe: %s" % fora)


# Quantos nós do projeto ainda não têm evidência. Medido em 11/11/2026:
# 79 nós nos treze tópicos, 6 com evidência (o kc_02 inteiro), 73 sem.
#
# O NÚMERO ESTÁ AQUI para que o progresso seja visível e a regressão
# impossível: quem acrescentar um tópico baixa o número, e quem tirar
# uma evidência faz o teste cair. Sem ele, "nenhum nó tem evidência" e
# "todos têm" passariam igual.
SEM_EVIDENCIA = 1


def test_quantos_nos_ainda_nao_tem_evidencia():
    """A lacuna, contada — e é ela que define o escopo defensável.

    ERA "UM TÓPICO DE TREZE" ATÉ 12/11/2026, e deixou de ser duas vezes
    no mesmo dia: primeiro com as demonstrações dos onze tópicos que
    faltavam, depois com a TERCEIRA FORMA do contrato. São 78 dos 79
    nós.

    SOBRA UM, e ele diz o limite do método: o I3 do kc_05, `*p` com p
    nulo. Rodar é o próprio comportamento indefinido; o compilador não
    recusa; e não diagnostica com `-std=c17 -Wall -c`, porque
    `-Wnull-dereference` precisa de otimização ligada. Mudar os flags
    do oráculo para alcançá-lo mudaria o que TODAS as outras
    demonstrações significam, e isso custa mais do que o nó vale.
    """
    todos = sem = 0
    for p in sorted(DOMINIO.glob("graph_kc*.yaml")):
        for nid, no in (yaml.safe_load(p.read_text(encoding="utf-8"))["nodes"]
                        or {}).items():
            todos += 1
            if not no.get("evidencia"):
                sem += 1
    assert todos == 79, ("mudou o número de nós do projeto: %d" % todos)
    assert sem == SEM_EVIDENCIA, (
        "nós sem evidência: %d (a constante diz %d).\n"
        "Subiu? Alguma evidência saiu. Caiu? Atualize a constante e o "
        "capítulo que cita este número." % (sem, SEM_EVIDENCIA))


def test_o_programa_de_evidencia_compila_sem_aviso():
    """Aviso do compilador invalida a evidência, e um caso provou por quê.

    A primeira demonstração do B1 comparava `&x == &x`, e o gcc disse
    `warning: self-comparison always evaluates to true
    [-Wtautological-compare]`. O oráculo aprovou, porque aviso não muda
    o código de saída — e a aprovação era vazia: a comparação é
    verdadeira por SINTAXE, dobrada em tempo de compilação. O programa
    não media nada sobre memória.

    É o pior tipo de evidência possível: circular, e com aparência de
    conferida. O comentário do próprio nó B1 já registrava que
    `&idade == &idade` avisa, e por isso ficava fora do cartão — eu
    escrevi a evidência sem ler o comentário.

    Esta trava fica no teste e não no oráculo de propósito: o oráculo
    serve também a moldes de item, onde um aviso pode ser aceitável. A
    premissa é mais exigente que o item.
    """
    import subprocess
    import tempfile

    import oraculo

    if not oraculo.GCC.exists():
        pytest.skip("sem compilador")
    fora = []
    for topico, nid, i, dem in _demonstracoes():
        # A PROVA POR AVISO FICA DE FORA PORQUE O AVISO É A PROVA. As
        # duas outras formas não podem avisar — aviso ali costuma
        # significar que o programa não mede o que diz medir —, e a
        # terceira existe justamente para os nós em que o diagnóstico
        # do compilador é a única demonstração possível.
        if dem.get("nao_compila") or dem.get("avisa"):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp)
            (p / "o.c").write_text(dem["programa"], encoding="utf-8")
            r = subprocess.run(
                [str(oraculo.GCC), "-std=c17", "-Wall", "-o", "o.exe", "o.c"],
                capture_output=True, text=True, timeout=oraculo.TEMPO,
                cwd=str(p))
        avisos = [l.strip() for l in r.stderr.splitlines() if "warning:" in l]
        if avisos:
            fora.append((topico, nid, i, avisos))
    assert not fora, (
        "programa de evidência com aviso do compilador: %s\n"
        "Aviso aqui costuma significar que o programa não mede o que diz "
        "medir." % fora)
