# -*- coding: utf-8 -*-
"""A prova da premissa na tela de refutação, e o portão que ela atravessa.

O QUE ENTRA. A premissa de cada nó do kc_02 passou a ter `evidencia`: um
programa em C que o oráculo compila, roda e confere. A tela de refutação
AFIRMA a premissa; agora ela pode mostrar o que a sustenta.

E É NA REFUTAÇÃO QUE ISSO PESA MAIS, por uma medida: em 42 das 80
ocorrências de crença do projeto — 52,5% — a cadeia de refutação tem UM
PASSO, porque a crença nega um nó observável e nó observável não tem
suporte. Nessas, não há grafo a percorrer: a tela afirma a premissa e põe
a crença ao lado. É exatamente ali que um programa que demonstra a
premissa troca "acredite nesta frase" por "a máquina conferiu".

O PORTÃO, E POR QUE ELE NÃO É ZELO EXCESSIVO. O programa de evidência foi
escrito para o examinador: ele usa `int **pp`, função com parâmetro,
array. Mostrá-lo a quem está no kc_02 repetiria, letra por letra, o
defeito que REPROVOU a cadeia do `pointer_and_target_are_one` na revisão
pedagógica de 05/11/2026:

    O degrau 1 exige declaracao multipla (int x = 1, y = 2;) e
    reatribuicao de ponteiro (p = &y), nenhuma das duas ensinada em
    cartao nenhum do caminho [...] — e e o degrau de ABERTURA.

Então a evidência atravessa o MESMO portão que todo o resto: só chega à
pessoa a demonstração cujos construtos têm cartão que os ensine neste
tópico. Quem decide é `conceitos.construtos_de`, que já existia, e não
uma declaração à mão de quem escreveu o programa.

A demonstração bloqueada **continua existindo e continua conferida pelo
oráculo** — ela só não vai para a tela da pessoa. Validar e exibir são
duas perguntas, e confundi-las faria uma das duas mentir.
"""
from __future__ import annotations

import pytest

from mvp import conceitos, motor
from mvp.dominio import carrega


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


def _refutando(d, no):
    """O estado no ÚLTIMO passo da refutação de `no`."""
    e = motor.inicia(d, semente="P01").estado
    e = e.com(no, crenca=next(iter(d.nos[no].negado_por), None)
              or next(iter(d.crencas)))
    e = motor._inicia_refutacao(d, e, no).estado
    while e.passo < len(e.plano) - 1:
        e = motor.replace(e, passo=e.passo + 1)
    return e


# --------------------------------------------------------------------------
# O domínio carrega a evidência
# --------------------------------------------------------------------------

def test_o_no_carrega_a_evidencia(d):
    """Sem isto o campo existe no YAML e morre ali."""
    for nid in d.ordem:
        no = d.nos[nid]
        assert no.evidencia, ("o nó %s não trouxe evidência do YAML" % nid)
        for dem in no.evidencia:
            assert dem.programa.strip().startswith("#include"), (nid, dem)
            assert dem.afirma, (nid, "demonstração sem `afirma`")


def test_a_evidencia_do_i2_tem_as_duas_metades(d):
    """A lista é lista porque o I2 pediu, e é aqui que isso se cobra."""
    dems = d.nos["I2"].evidencia
    assert len(dems) >= 2, [x.afirma[:40] for x in dems]
    assert any(not x.nao_compila for x in dems), "nenhuma roda"
    assert any(x.nao_compila for x in dems), "nenhuma prova por recusa"
    for dem in dems:
        if dem.nao_compila:
            assert dem.ambiente, "recusa sem ambiente declarado"


# --------------------------------------------------------------------------
# O portão
# --------------------------------------------------------------------------

def test_o_portao_recusa_programa_com_construto_nao_ensinado(d):
    """A trava, e ela tem de recusar casos reais — não só existir.

    Em 11/11/2026, cinco das oito demonstrações do kc_02 usam construto
    sem cartão que o ensine neste tópico: `funcao_com_parametro` (B1, I3),
    `ponteiro_de_ponteiro` (B2), `array` (I2, ensinado em kc_07:B1, um
    tópico POSTERIOR) e `comparacao_de_ponteiros` (a segunda do B1).

    A ÚLTIMA É A QUE ESTÁ A UMA ASSINATURA DE DISTÂNCIA, e é por isso
    que ela está nomeada aqui: o cartão do `kc_02:B1` ENSINA comparação
    de endereços desde 05/11, e o que a barra não é falta de material —
    é o inventário segurar o conceito em `so_avaliado` até o dono
    auditar. Escrevi aquela demonstração contando com uma promoção que
    eu mesmo tinha feito sem autoridade para fazer; ela fica, conferida
    pelo oráculo, esperando a decisão.

    Se este teste parar de recusar, ou alguém ensinou o construto — e aí
    o número desce declarado — ou o portão quebrou.
    """
    bloqueadas = []
    for nid in d.ordem:
        for i, dem in enumerate(d.nos[nid].evidencia):
            if not conceitos.exibivel(dem.programa, "kc_02"):
                bloqueadas.append("%s[%d]" % (nid, i))
    assert bloqueadas, (
        "o portão não recusou nenhuma demonstração. Ou todo construto "
        "passou a ser ensinado, ou `exibivel` parou de olhar.")
    assert bloqueadas == ["B1[0]", "B1[1]", "B2[0]", "I2[0]", "I3[0]"], (
        bloqueadas)


def test_o_portao_aceita_programa_sem_construto_novo(d):
    """E tem de ACEITAR, senão a tela nunca mostra nada.

    O B3 e o I1 não usam construto nenhum além do que o tópico ensina:
    `&x`, `*p`, atribuição, `printf` de `%d`.
    """
    for nid in ("B3", "I1"):
        dems = [dem for dem in d.nos[nid].evidencia
                if conceitos.exibivel(dem.programa, "kc_02")]
        assert dems, ("nenhuma demonstração de %s passa o portão" % nid)


def test_o_portao_nao_depende_de_declaracao_de_quem_escreveu(d):
    """Quem decide é a varredura do código, não um campo de confiança.

    Um campo `exibir: true` escrito por quem escreveu o programa seria a
    mesma passada de quem o escreveu — que é o defeito que a separação
    entre `liberada` e `aprovada` já existe para impedir no domínio.
    """
    for nid in d.ordem:
        for dem in d.nos[nid].evidencia:
            assert not hasattr(dem, "exibir"), (
                "a demonstração declara se pode ser exibida: %s" % nid)


# --------------------------------------------------------------------------
# A tela
# --------------------------------------------------------------------------

def test_a_tela_de_refutacao_traz_a_prova_do_no_do_passo(d):
    """A prova é da premissa do PASSO, e não do alvo da refutação.

    Num plano de três passos a tela mostra B2, depois B3, depois I1. A
    prova que aparece em cada uma é a daquele nó — mostrar a do alvo nos
    três seria afirmar que a premissa do passo foi demonstrada quando o
    que se demonstrou foi outra coisa.
    """
    no = "I1"                       # plano: B2 -> B3 -> I1
    e = motor._inicia_refutacao(
        d, motor.inicia(d, semente="P01").estado.com(
            no, crenca="pointer_and_target_are_one"), no).estado
    assert len(e.plano) == 3, e.plano
    vistos = []
    for passo in range(3):
        tela = motor._tela_refutacao(d, motor.replace(e, passo=passo))
        prova = tela.dados["prova"]
        vistos.append((e.plano[passo], [p["afirma"][:18] for p in prova]))
        for p in prova:
            assert p["afirma"] and p["programa"], p
            # a prova exibida é de um nó cuja evidência contém aquele texto
            assert any(dem.afirma == p["afirma"]
                       for dem in d.nos[e.plano[passo]].evidencia), (
                "a tela do passo %s mostrou prova de outro nó" % e.plano[passo])
    # Os TRÊS passos mostram prova, e o do B2 só porque uma segunda
    # demonstração foi escrita para passar o portão: a primeira dele usa
    # `int **pp` e fica barrada. Antes dessa segunda, este número era
    # [0, 1, 1] — o primeiro passo do plano, o de ABERTURA, era o que
    # não tinha nada a mostrar.
    assert [len(v[1]) for v in vistos] == [1, 1, 1], vistos


def test_a_tela_esconde_a_prova_bloqueada(d):
    """O I3 tem evidência, e ela não chega à pessoa.

    A tela não mostra prova nenhuma ali — e não mostra um aviso dizendo
    que existe uma prova que ela não pode ver, que seria pior que o
    silêncio.

    ERA O B1 ATÉ 11/11/2026, e deixou de servir porque o B1 ganhou uma
    segunda demonstração que passa o portão. O I3 é o caso que RESTA, e
    ele não tem conserto por reescrita: a premissa dele é "alcançar a
    mesma caixa de OUTRO PONTO DO PROGRAMA", e outro ponto do programa é
    uma chamada de função. Um bloco aninhado não serve — ali o nome `x`
    ainda está à vista, e escrever por `&x` não prova nada que `x = 99`
    não provasse. Enquanto `funcao_com_parametro` não tiver cartão, a
    conclusão do tópico é a única premissa sem prova na tela.
    """
    tela = motor._tela_refutacao(d, _refutando(d, "I3"))
    assert tela.dados["prova"] == [], tela.dados["prova"]
    assert d.nos["I3"].evidencia, "o I3 perdeu a evidência"


def test_a_prova_nao_promete_saida_de_programa_que_nao_compila(d):
    """A demonstração por recusa não tem saída, e a tela não pode inventar."""
    for nid in d.ordem:
        for passo in range(len(motor._plano(d, nid))):
            e = motor._inicia_refutacao(
                d, motor.inicia(d, semente="P01").estado.com(
                    nid, crenca=next(iter(d.crencas))), nid).estado
            tela = motor._tela_refutacao(d, motor.replace(e, passo=passo))
            for p in tela.dados["prova"]:
                if p["nao_compila"]:
                    assert not p.get("espera"), (nid, p)
                else:
                    assert p.get("espera"), (nid, p)


def test_todo_topico_tem_a_chave_prova(d):
    """Chave que às vezes existe é armadilha para o cliente.

    É o mesmo erro que o projeto já pegou na `reexplicacao`, que
    carregava string numa tela e lista na outra. Aqui: lista sempre,
    vazia quando não há nada a mostrar.
    """
    for topico in ("kc_00", "kc_02", "kc_07"):
        dd = carrega(topico=topico)
        no = dd.ordem[0]
        e = motor._inicia_refutacao(
            dd, motor.inicia(dd, semente="P01").estado.com(
                no, crenca=next(iter(dd.crencas))), no).estado
        prova = motor._tela_refutacao(dd, e).dados["prova"]
        assert isinstance(prova, list), (topico, type(prova))


# --------------------------------------------------------------------------
# Entre artefatos: o servidor monta `prova` e o cliente tem de mostrar
#
# A suíte deste projeto já passou verde com o `app.js` sintaticamente
# quebrado. Campo novo no servidor que o cliente não lê é a mesma classe
# de defeito, e aqui ele seria invisível: a tela ficaria igual à de
# antes, e nada acusaria.
# --------------------------------------------------------------------------

def _web(arquivo):
    """O arquivo da interface, SEM comentários.

    Tirar os comentários antes de conferir é lição paga neste projeto:
    um teste destes já caiu no comentário que explicava a mudança, em
    vez de no código — proibia falar da coisa em vez de proibir usá-la.
    """
    import pathlib
    import re

    texto = (pathlib.Path(__file__).resolve().parent / "web" / arquivo
             ).read_text(encoding="utf-8")
    if arquivo.endswith(".html"):
        return re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", texto, flags=re.S)


def test_o_cliente_le_a_prova_e_todos_os_campos_dela(d):
    """Cada chave que o motor manda em `prova` tem de ser lida."""
    tela = motor._tela_refutacao(d, _refutando(d, "B3"))
    prova = tela.dados["prova"]
    assert prova, "o B3 deixou de ter prova exibível, e o teste ficou vazio"
    js = _web("app.js")
    assert "t.prova" in js, "o cliente não lê `prova`"
    for campo in prova[0]:
        assert ("." + campo) in js, (
            "o motor manda `prova.%s` e o cliente não lê" % campo)


def test_o_html_tem_onde_por_a_prova():
    """E o alvo existe no HTML, dentro da seção de refutação."""
    import re

    html = _web("index.html")
    sec = re.search(r'<section id="tela-refutacao".*?</section>', html, re.S)
    assert sec, "não achei a seção da refutação"
    assert 'id="ref-prova"' in sec.group(0), (
        "a seção de refutação não tem o alvo `ref-prova`")


def test_a_prova_entra_recolhida():
    """A tela não vira parede de C, e quem quiser ver abre.

    A refutação tem trabalho a fazer na tela — a premissa, a figura, o
    contraste com a crença. A prova é apoio: ela confirma a premissa
    para quem desconfiar dela, e não substitui o argumento. Entrar
    aberta empurraria o contraste para fora do primeiro olhar.
    """
    js = _web("app.js")
    assert "details" in js, (
        "a prova não entra recolhida: nenhum `details` no cliente")


def test_o_cliente_nao_promete_saida_de_quem_nao_compila():
    """A demonstração por recusa não tem `espera`, e o cliente sabe.

    Sem a condição, a tela mostraria o rótulo da saída esperada com
    nada embaixo — e quem lesse concluiria que o programa roda e não
    imprime, que é o contrário do que se está demonstrando.
    """
    js = _web("app.js")
    assert "nao_compila" in js, (
        "o cliente não distingue prova por recusa de prova por saída")


def test_a_prova_por_recusa_leva_o_ambiente_para_a_tela(d):
    """"Este programa não compila" é fato sobre UM compilador.

    Eu mesmo escrevi a tela afirmando a recusa sem dizer onde — a mesma
    frase que o histórico do nó I2 registra que o projeto já afirmou uma
    vez, no material antigo, e teve de retirar: `int n = p;` é `error:`
    no gcc 16 e AVISO no gcc 13. O que o padrão exige de todo compilador
    conforme é o diagnóstico, não a recusa de traduzir.

    Então o `ambiente` viaja com a prova, e quem lê vê em que compilador
    aquilo foi observado.
    """
    achou = False
    for nid in d.ordem:
        for passo in range(len(motor._plano(d, nid))):
            e = motor._inicia_refutacao(
                d, motor.inicia(d, semente="P01").estado.com(
                    nid, crenca=next(iter(d.crencas))), nid).estado
            tela = motor._tela_refutacao(d, motor.replace(e, passo=passo))
            for p in tela.dados["prova"]:
                if p["nao_compila"]:
                    achou = True
                    assert p.get("ambiente"), (
                        "prova por recusa chegou à tela sem dizer em que "
                        "compilador: %s" % nid)
                    assert "gcc" in p["ambiente"].lower(), p["ambiente"]
    assert achou, (
        "nenhuma prova por recusa chega à tela, e o teste ficou vazio")


def test_o_cliente_mostra_o_ambiente():
    js = _web("app.js")
    assert ".ambiente" in js, "o cliente não lê `prova.ambiente`"
