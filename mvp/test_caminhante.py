# -*- coding: utf-8 -*-
"""A quarta persona do caminhante — a que diz "não sei".

A varredura dos treze tópicos mediu 390 sessões e, em 12 deles, o
`aprende` terminou 100% `confirmado` e o `crente` 100% `em_aberto`.
Nenhum `lacuna` em tópico nenhum. A causa tem uma linha: **nenhuma das
três personas dizia "não sei"** — zero ocorrências de `nao_sei` em
`scripts/caminhante.py`.

A consequência é que a **CS-4** ("não sei" em qualquer camada produz
lacuna, nunca crença) tem 31 asserções na suíte de unidade e nunca rodava
pela TELA. O portão de ponta a ponta produzia os dois extremos do espaço
de estados e nada do meio.

POR QUE A PERSONA ALTERNA entre as camadas, em vez de dizer "não sei"
sempre: um "não sei" na camada 1 ENCERRA o episódio, e as camadas 2 e 3
não são perguntadas. Uma persona que dissesse sempre exercitaria só a
camada 1 — e a camada 2 continuaria sem cobertura pela tela, que é
exatamente o buraco que ela existe para tapar.

A alternância é pelo id da atividade, não por sorteio: o caminhante é um
portão, e portão que muda de resultado sem o código mudar não serve de
portão.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def _caminhante():
    """Carrega `scripts/caminhante.py` como módulo.

    `scripts/` não é pacote, e não vai virar um por causa de um teste.
    """
    spec = importlib.util.spec_from_file_location(
        "caminhante_sob_teste", RAIZ / "scripts" / "caminhante.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cam():
    return _caminhante()


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


@pytest.fixture(scope="module")
def chaves(d):
    return ({a.id: a for a in d.atividades},
            {c.afirma for c in d.crencas.values()},
            {n.texto for n in d.nos.values()}
            | {n.simples for n in d.nos.values()})


def _tela_atividade(d, a, sessao):
    from mvp.motor import opcoes_na_tela
    return {"tipo": "atividade", "atividade": a.id, "fase": "DIAGNOSTICO",
            "opcoes": [{"texto": o.texto} for o in opcoes_na_tela(sessao, a)]}


def _tela_razao(d, a):
    """A camada 2: uma razão é a fala do nó, as outras são crenças."""
    textos = ([d.nos[a.no].texto]
              + [c.afirma for c in d.crencas.values()][:2])
    return {"tipo": "razao", "atividade": a.id,
            "opcoes": [{"texto": x} for x in textos]}


def _razao_de_verdade(d, a, sessao="P01"):
    """A tela de razão montada COMO O MOTOR MONTA, e as razões na ordem.

    O fixture sintético acima serve para checar que a persona devolve um
    índice; não serve para amarrar a persona a um critério. Para isso a
    tela tem de ser a real: `razoes_de` do grafo, permutadas por
    `ordem_das_razoes` com a sessão de semente — igual a `motor.py`.

    Devolve `(tela, razoes)` com `razoes[i]` correspondendo ao índice `i`
    da tela, que é o que a persona devolve.
    """
    razoes = motor.razoes_de(d, a)
    if len(razoes) < 2:
        return None, None
    ordem = motor.ordem_das_razoes(sessao, a.id, len(razoes))
    na_tela = tuple(razoes[i] for i in ordem)
    tela = {"tipo": "razao", "atividade": a.id,
            "opcoes": [{"texto": z.texto} for z in na_tela]}
    return tela, na_tela


# --------------------------------------------------------------------------
# A persona existe, e as três antigas não mudaram
# --------------------------------------------------------------------------

def test_a_quarta_persona_entra_na_lista(cam):
    assert "nao_sabe" in cam.PERSONAS, cam.PERSONAS


def test_as_tres_personas_antigas_continuam_na_lista(cam):
    """Persona nova não pode custar persona velha: os números da varredura
    dos treze foram medidos com estas três, e comparar depois exige que
    elas respondam igual."""
    for p in ("sabido", "aprende", "crente"):
        assert p in cam.PERSONAS, p


def test_a_persona_nova_tem_frase_de_teachback(cam):
    """`caminha` indexa `FRASES[persona]` — persona sem frase estoura com
    KeyError no meio da sessão, e não na lista."""
    assert "nao_sabe" in cam.FRASES
    assert set(cam.FRASES["nao_sabe"]) == {"inicio", "fim"}


def test_as_antigas_continuam_devolvendo_indice(cam, d, chaves):
    """A trava da regressão: nenhuma das três antigas pode passar a
    devolver o sinal de "não sei"."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    for persona in ("sabido", "aprende", "crente"):
        for tela in (_tela_atividade(d, a, "P01"), _tela_razao(d, a)):
            i = cam.escolhe(tela, persona, chaves, "P01")
            assert isinstance(i, int), (persona, tela["tipo"], i)


# --------------------------------------------------------------------------
# O "não sei", nas duas camadas
# --------------------------------------------------------------------------

def test_nao_sabe_diz_nao_sei_na_camada_2_sempre(cam, d, chaves):
    """A camada 2 é a que estava descoberta pela tela, e é onde a razão
    errada seria lida como CRENÇA. A CS-4 manda produzir lacuna."""
    for a in d.atividades:
        tela = _tela_razao(d, a)
        assert cam.escolhe(tela, "nao_sabe", chaves, "P01") == cam.NAO_SEI, a.id


def test_nao_sabe_diz_nao_sei_na_camada_1_em_parte_dos_itens(cam, d, chaves):
    """E responde na outra parte, de propósito.

    Se dissesse "não sei" em toda camada 1, o episódio encerraria ali
    sempre e a camada 2 nunca seria alcançada — a persona não cobriria o
    buraco que justifica a existência dela.
    """
    disse, respondeu = [], []
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        r = cam.escolhe(tela, "nao_sabe", chaves, "P01")
        (disse if r == cam.NAO_SEI else respondeu).append(a.id)
    assert disse, "nenhum item leva nao_sei na camada 1"
    assert respondeu, "todo item leva nao_sei: a camada 2 fica inalcancavel"


def test_a_alternancia_e_estavel_e_nao_sorteada(cam, d, chaves):
    """Portão que muda de resultado sem o código mudar não é portão.

    A primeira versão deste teste fixava UM item e repetia a chamada — e
    passava **antes** da persona existir, porque `escolhe` já era
    determinístico para qualquer persona desconhecida. Teste que passa sem
    a implementação não prova a implementação.

    O que prende de verdade é o CONJUNTO: quais itens levam "não sei" tem
    de ser o mesmo conjunto a cada rodada, e não pode ser vazio nem
    completo — as duas pontas que tornariam a camada 1 ou a camada 2
    inalcançável.
    """
    def conjunto():
        return frozenset(
            a.id for a in d.atividades
            if cam.escolhe(_tela_atividade(d, a, "P01"), "nao_sabe",
                           chaves, "P01") == cam.NAO_SEI)

    primeiro = conjunto()
    assert primeiro, "nenhum item leva nao_sei"
    assert len(primeiro) < len(d.atividades), "todos levam nao_sei"
    for _ in range(5):
        assert conjunto() == primeiro


def test_quando_responde_a_camada_1_ela_erra(cam, d, chaves):
    """Quem não sabe não acerta por sorte.

    Se a persona acertasse a camada 1 e só titubeasse na razão, ela
    produziria falso positivo e não o `lacuna` que falta.
    """
    from mvp.motor import indice_correto_na_tela
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        r = cam.escolhe(tela, "nao_sabe", chaves, "P01")
        if r != cam.NAO_SEI:
            assert r != indice_correto_na_tela("P01", a), a.id


# --------------------------------------------------------------------------
# O defeito que a quarta persona descobriu, e que é das TRÊS ANTIGAS
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_nenhuma_persona_que_deve_errar_escolhe_a_certa(cam, topico):
    """`None == None`, e a persona que devia errar acertava.

    O caminho de quem não está convencido procurava a alternativa cuja
    crença é a do item:

        next(i for i, o in enumerate(na_tela) if o.crenca == a.crenca)

    Quando `a.crenca` é `None` — e três itens dos 562 são assim — a
    comparação casa a alternativa cuja crença também é `None`, que é
    justamente **a certa**. A persona que existe para errar acertava, de
    propósito nenhum.

    Por que isso não é detalhe: um dos três é item de DIAGNÓSTICO
    (`ciu_kc00_001`). Ali o `crente` acerta, nenhuma crença é detectada,
    a refutação não acontece — e se ele depois escolhe uma crença como
    razão, o episódio sai `falso_positivo`. Foi exatamente o que a
    varredura dos treze mediu no kc_00, e eu li como propriedade do
    tópico. Era artefato do portão.

    É a classe de defeito que este projeto chama de plausível e errado: o
    portão rodava verde e media outra coisa.
    """
    d = carrega(topico=topico)
    chaves = ({a.id: a for a in d.atividades},
              {c.afirma for c in d.crencas.values()},
              {n.texto for n in d.nos.values()}
              | {n.simples for n in d.nos.values()})
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        certo = motor.indice_correto_na_tela("P01", a)
        for persona in ("aprende", "crente", "nao_sabe"):
            r = cam.escolhe(tela, persona, chaves, "P01")
            if r == cam.NAO_SEI:
                continue
            assert r != certo, (topico, a.id, persona, a.crenca)


# --------------------------------------------------------------------------
# O `sem_medida` do portão passa a contar os estados não-terminais
# --------------------------------------------------------------------------

def test_sem_medida_conta_refutado_e_em_treino(cam):
    """O defeito que a varredura expôs sem ser mordida por ele.

    `sem_medida` contava `desconhecido` e `nao_medido`. Mas `refutado`
    (crença detectada, ainda não trabalhada) e `em_treino` (falta fechar
    a sequência) também são fim de sessão QUEBRADO: a premissa não chegou
    a nenhum dos estados que a CS-10 promete. Um portão que diz "0 sem
    medida" numa sessão parada no meio da refutação mente com a verdade.
    """
    nos = [{"no": "B1", "estado": "confirmado"},
           {"no": "B2", "estado": "refutado"},
           {"no": "B3", "estado": "em_treino"},
           {"no": "I1", "estado": "desconhecido"},
           {"no": "I2", "estado": "nao_medido"},
           {"no": "I3", "estado": "em_aberto"}]
    assert cam.sem_medida(nos) == ["B2", "B3", "I1", "I2"]


def test_em_aberto_e_confirmado_nao_contam_como_sem_medida(cam):
    """`em_aberto` É medida — o banco acabou, e o projeto decidiu que isso
    é um estado, não uma lacuna de instrumento (ver `test_medida.py`).
    Contá-lo aqui faria o portão acusar o pior caso roteirizado."""
    nos = [{"no": "B1", "estado": "em_aberto"},
           {"no": "B2", "estado": "confirmado"},
           {"no": "B3", "estado": "lacuna"},
           {"no": "I1", "estado": "fragil"},
           {"no": "I2", "estado": "falso_positivo"}]
    assert cam.sem_medida(nos) == []


# --------------------------------------------------------------------------
# A QUINTA PERSONA: a que acerta pela razão errada — a CS-1
# --------------------------------------------------------------------------
#
# A varredura com quatro personas mediu quatro extremos puros: cada uma
# produzia um estado só, 130 de 130, igual nos treze tópicos. O espaço
# alcançado pela tela era `confirmado`, `em_aberto` e `lacuna` — três dos
# oito estados do motor.
#
# E `falso_positivo` não era produzido por nenhuma. Esse é o estado da
# CS-1 — *um acerto com razão errada não confirma a premissa* —, que é a
# medida central do trabalho inteiro. As quatro personas eram internamente
# coerentes: quem acertava a resposta acertava a razão, quem errava errava
# as duas. A INCOERÊNCIA é exatamente o fenômeno que o instrumento existe
# para medir, e nenhuma persona era incoerente.
#
# Por que ela importa mais que a quarta: `falso_positivo` tem um caminho de
# detecção PRÓPRIO. Um acerto mal explicado marca o nó e traz outra
# superfície; **dois na mesma crença** emitem `crenca_detectada` com
# `via="falso positivo repetido"` (`FALSOS_POSITIVOS_PARA_CRENCA`), que é
# uma porta de entrada da refutação que a tela nunca atravessou.

def test_a_quinta_persona_entra_na_lista(cam):
    assert "explica_mal" in cam.PERSONAS, cam.PERSONAS


def test_a_quinta_persona_tem_frase_de_teachback(cam):
    assert "explica_mal" in cam.FRASES
    assert set(cam.FRASES["explica_mal"]) == {"inicio", "fim"}


def test_a_quinta_persona_tem_confianca(cam):
    """Sem entrada no mapa de confiança, `caminha` estoura com KeyError na
    camada 3 — no meio da sessão, e não na lista."""
    assert "explica_mal" in cam.CONFIANCA


@pytest.mark.parametrize("topico", topicos())
def test_explica_mal_acerta_a_camada_1_em_todo_item(cam, topico):
    """A metade de cima do falso positivo: a resposta é a CERTA.

    Em todo item dos treze tópicos, porque uma persona que acertasse só
    em alguns misturaria `crenca` no resultado e a medida deixaria de
    isolar a CS-1.
    """
    d = carrega(topico=topico)
    chaves = ({a.id: a for a in d.atividades},
              {c.afirma for c in d.crencas.values()},
              {n.texto for n in d.nos.values()}
              | {n.simples for n in d.nos.values()})
    for a in d.atividades:
        tela = _tela_atividade(d, a, "P01")
        assert (cam.escolhe(tela, "explica_mal", chaves, "P01")
                == motor.indice_correto_na_tela("P01", a)), (topico, a.id)


@pytest.mark.parametrize("topico", topicos())
def test_explica_mal_erra_a_camada_2_e_isso_da_falso_positivo(cam, topico):
    """A metade de baixo, amarrada ao critério e não à intenção.

    Não basta "a persona escolhe uma razão errada": o teste passa a razão
    que ela escolheu pela tabela de `motor.classifica` e cobra
    `FALSO_POSITIVO_EP`. É a própria função que a banca vai ler, e é o que
    faz deste teste uma afirmação sobre a CS-1 em vez de uma afirmação
    sobre o caminhante.
    """
    d = carrega(topico=topico)
    chaves = ({a.id: a for a in d.atividades},
              {c.afirma for c in d.crencas.values()},
              {n.texto for n in d.nos.values()}
              | {n.simples for n in d.nos.values()})
    vistos = 0
    for a in d.atividades:
        tela, razoes = _razao_de_verdade(d, a)
        if tela is None:
            continue
        i = cam.escolhe(tela, "explica_mal", chaves, "P01")
        assert isinstance(i, int), (topico, a.id, i)
        escolhida = razoes[i]
        assert not escolhida.correta, (topico, a.id, escolhida.texto)
        assert escolhida.crenca, (topico, a.id, "razão errada sem crença")
        assert (motor.classifica(True, escolhida, "tenho certeza")
                == motor.FALSO_POSITIVO_EP), (topico, a.id)
        vistos += 1
    assert vistos, topico


def test_a_quinta_nao_mexeu_nas_outras_quatro(cam, d, chaves):
    """Trava de regressão: os números das quatro já estão gravados em
    `docs/processo.md`, e comparar depois exige que elas não mudem."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    certo = motor.indice_correto_na_tela("P01", a)
    tela = _tela_atividade(d, a, "P01")
    assert cam.escolhe(tela, "sabido", chaves, "P01") == certo
    for persona in ("aprende", "crente"):
        assert cam.escolhe(tela, persona, chaves, "P01") != certo, persona
    assert cam.escolhe(_tela_razao(d, a), "nao_sabe", chaves, "P01") == cam.NAO_SEI


# --------------------------------------------------------------------------
# O PORTÃO PASSA A RELATAR EPISÓDIOS, e não só o estado final
# --------------------------------------------------------------------------
#
# O limite que a quinta persona expôs: a sessão do `explica_mal` termina
# com todos os nós `confirmado`, e está CORRETO — dois falsos positivos na
# mesma crença disparam `crenca_detectada`, vem refutação, vem treino, e o
# treino confirma. `falso_positivo` é transitório por desenho.
#
# Isto quer dizer que o portão, olhando só o estado final, nunca poderia
# ter visto `falso_positivo` — mesmo quando ele acontece 36 vezes em três
# sessões. A conclusão "nenhuma persona produz falso_positivo" estava
# certa pelo motivo errado, e o instrumento trabalha justamente no meio.
#
# A fonte é o `veredito` que o servidor manda em toda resposta: quem
# classifica é o MOTOR, não o cliente, e é a mesma decisão que a tela
# mostra à pessoa.

def test_episodios_conta_na_ordem_de_leitura(cam):
    vereditos = ["certa", "errada", "certa", "falso_positivo", "lacuna",
                 "certa", "crenca"]
    assert cam.episodios(vereditos) == {
        "certa": 3, "errada": 1, "falso_positivo": 1,
        "crenca": 1, "lacuna": 1}
    assert list(cam.episodios(vereditos)) == list(cam.VEREDITOS)


def test_episodios_ignora_passo_sem_veredito(cam):
    """Tela de ensino e de refutação não classificam nada: o servidor
    manda `veredito: null`, e isso não é episódio."""
    assert cam.episodios([None, "certa", None, None]) == {"certa": 1}
    assert cam.episodios([]) == {}
    assert cam.episodios([None, None]) == {}


def test_um_veredito_que_o_portao_nao_conhece_NAO_e_calado(cam):
    """A trava contra a próxima versão deste defeito.

    Se o motor passar a emitir um veredito novo e este portão filtrasse
    pela lista que conhece, o episódio novo sairia do relatório sem
    ninguém notar — exatamente o buraco que esta seção existe para
    fechar, repetido um nível acima.
    """
    r = cam.episodios(["certa", "veredito_que_nao_existe_ainda"])
    assert r.get("veredito_que_nao_existe_ainda") == 1, r
    # e os conhecidos continuam vindo primeiro, para a leitura não mudar
    assert list(r)[0] == "certa"


def test_falso_positivo_aparece_no_resumo(cam):
    """O episódio que motivou tudo isto."""
    assert cam.episodios(["falso_positivo"] * 12) == {"falso_positivo": 12}


def test_os_eventos_transitorios_sao_contados(cam):
    """`falso_positivo` e `crenca_detectada` são os dois que o estado
    final apaga, e são os que dizem por qual PORTA a refutação entrou."""
    passos = [["resposta_registrada"],
              ["resposta_registrada", "falso_positivo"],
              ["resposta_registrada", "falso_positivo", "crenca_detectada"],
              []]
    assert cam.transitorios(passos) == {"falso_positivo": 2,
                                        "crenca_detectada": 1}


def test_sem_evento_transitorio_o_resumo_fica_vazio(cam):
    """Sessão do `sabido` não tem nenhum dos dois, e o relatório não deve
    inventar zeros para encher linha."""
    assert cam.transitorios([["resposta_registrada"], ["razoes_apresentadas"]]) == {}


def test_conta_formata_na_ordem_recebida(cam):
    """O resumo é lido por gente, e a ordem é a de `episodios` — os
    conhecidos antes dos desconhecidos. `_conta` não pode reordenar."""
    assert cam._conta({"certa": 30, "falso_positivo": 12}) == "certa=30 falso_positivo=12"


def test_conta_de_vazio_e_string_vazia(cam):
    """`main` imprime "nenhum" quando vem vazio, e para isso precisa de
    string vazia e não de "{}"."""
    assert cam._conta({}) == ""


def test_conta_aceita_counter(cam):
    """No agregado vem um `Counter`, não um dict — e `Counter` vazio é
    falsy do mesmo jeito."""
    import collections
    assert cam._conta(collections.Counter(["certa", "certa"])) == "certa=2"
