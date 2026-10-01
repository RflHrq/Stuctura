"""O laço: identifica, confirma a suspeita, refuta, treina, confirma.

Duas regras governam o laço, e cada uma existe para evitar um erro de leitura
sobre o aluno:

  um erro isolado não é crença    → a segunda pergunta do nó decide
  um acerto isolado não é domínio → a sequência de acertos decide

Os quatro requisitos do documento (RF33 a RF36) têm teste cada, e cada um
falha se a regra for removida.
"""

from __future__ import annotations

from dataclasses import replace

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import Resposta

# O domínio é imutável e a carga é barata: uma vez por módulo basta.
D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


# --------------------------------------------------------------------------
# Roteiros
# --------------------------------------------------------------------------

def _errada(a):
    return next(i for i, o in enumerate(a.opcoes) if not o.correta)


def roda(d, politica, limite=300):
    """Percorre a unidade inteira. `politica(tela, estado) -> Resposta`."""
    t = motor.inicia(d)
    eventos = list(t.eventos)
    for _ in range(limite):
        if t.tela.tipo == "mapa":
            return t, eventos
        t = motor.avanca(d, t.estado, politica(t.tela, t.estado))
        eventos.extend(t.eventos)
    raise AssertionError("a unidade não terminou em %d passos" % limite)


def _politica(*, erra_no=None, erra_diagnostico=99, erra_treino=0,
              confianca="tenho certeza", d=D):
    """Acerta tudo, menos no nó pedido.

    `erra_diagnostico`: quantas atividades de diagnóstico daquele nó errar.
    `erra_treino`: quantas tentativas de treino daquele nó errar.
    """
    feitos = {"diagnostico": 0, "treino": 0}

    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        treino = tela.dados["fase"] == motor.TREINO
        chave = "treino" if treino else "diagnostico"
        limite = erra_treino if treino else erra_diagnostico
        if a.no == erra_no and feitos[chave] < limite:
            feitos[chave] += 1
            return Resposta(escolha=_errada(a), confianca=confianca)
        return Resposta(escolha=a.indice_correto, confianca=confianca)

    return politica


def _tipos(eventos):
    return [e.tipo for e in eventos]


def _dos(eventos, tipo, no=None):
    return [e.dados for e in eventos
            if e.tipo == tipo and (no is None or e.dados.get("no") == no)]


# --------------------------------------------------------------------------
# Um erro isolado é vacilo, não crença
# --------------------------------------------------------------------------

def test_errar_uma_vez_leva_a_segunda_pergunta_do_no_e_nao_a_refutacao(d):
    t, eventos = roda(d, _politica(erra_no="B3", erra_diagnostico=1))
    assert _dos(eventos, "suspeita_de_crenca", "B3"), "não houve segunda checagem"
    assert not _dos(eventos, "crenca_detectada", "B3"), "refutou com um erro só"
    assert _dos(eventos, "vacilo_detectado", "B3")
    assert _dos(eventos, "no_confirmado", "B3")[0]["via"] == "vacilo"


def test_errar_as_duas_perguntas_do_no_dispara_a_refutacao(d):
    t, eventos = roda(d, _politica(erra_no="B3", erra_diagnostico=2))
    detectadas = _dos(eventos, "crenca_detectada", "B3")
    assert detectadas and detectadas[0]["crenca"] == "declaration_zeroes"
    assert detectadas[0]["erros"] == motor.ERROS_PARA_CRENCA


def test_a_segunda_pergunta_e_de_outro_formato(d):
    """O par teórica + código existe para isso: a segunda checagem não pode
    ser o mesmo molde da primeira."""
    t, eventos = roda(d, _politica(erra_no="B4", erra_diagnostico=2))
    vistas = [e.dados for e in eventos if e.tipo == "atividade_apresentada"
              and e.dados["no"] == "B4" and e.dados["fase"] == motor.DIAGNOSTICO]
    assert len(vistas) == 2
    assert vistas[0]["item"] == "teorica"
    assert vistas[1]["item"] == "codigo"
    assert vistas[0]["formato"] != vistas[1]["formato"]


def test_errar_chutando_nunca_vira_suspeita(d):
    t, eventos = roda(d, _politica(erra_no="B2", erra_diagnostico=2,
                                   confianca="chutei"))
    assert _dos(eventos, "lacuna_registrada", "B2")
    assert not _dos(eventos, "suspeita_de_crenca", "B2")
    assert not _dos(eventos, "crenca_detectada", "B2")


def test_a_validacao_traz_a_analogia_antes_da_refutacao(d):
    t = motor.inicia(d)
    pol = _politica(erra_no="B2", erra_diagnostico=2)
    telas = []
    for _ in range(80):
        telas.append(t.tela)
        if t.tela.tipo == "mapa":
            break
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    tipos = [x.tipo for x in telas]
    assert "validacao" in tipos
    assert tipos.index("validacao") < tipos.index("refutacao")
    validacao = next(x for x in telas if x.tipo == "validacao")
    assert "quarto" in validacao.texto.lower(), "a analogia não chegou à tela"
    assert "memoria" in validacao.dados["crenca"].lower()

    # A analogia é a DO NÓ, não o resumo do tópico: o resumo mapeia os cinco
    # nós de uma vez e entregaria a resposta das atividades seguintes.
    assert validacao.texto == d.resgate("B2")
    assert validacao.texto != d.analogia
    assert "atribuir =" not in validacao.texto


# --------------------------------------------------------------------------
# RF33 — depois da refutação, treino; nunca confirmado direto
# --------------------------------------------------------------------------

def test_rf33_nenhum_no_vai_de_refutado_a_confirmado_sem_treino(d):
    t, eventos = roda(d, _politica(erra_no="B3", erra_diagnostico=2))
    ordem = _tipos(eventos)
    assert "refutacao_concluida" in ordem

    depois = eventos[ordem.index("refutacao_concluida"):]
    confirmados = [e.dados for e in depois
                   if e.tipo == "no_confirmado" and e.dados["no"] == "B3"]
    assert confirmados and confirmados[0]["via"] == "treino"
    assert _dos(eventos, "treino_tentativa", "B3"), "confirmou sem nenhuma tentativa"


def test_rf33_o_streak_exigido_e_o_do_documento(d):
    assert motor.STREAK_ALVO == 2
    t, eventos = roda(d, _politica(erra_no="B3", erra_diagnostico=2))
    fechou = _dos(eventos, "training_streak_completed", "B3")
    assert fechou and fechou[0]["streak"] == motor.STREAK_ALVO


# --------------------------------------------------------------------------
# RF34 — formato diferente a cada tentativa, item anterior nunca repetido
# --------------------------------------------------------------------------

def test_rf34_o_treino_nao_repete_o_item_anterior_nem_o_formato(d):
    t, eventos = roda(d, _politica(erra_no="B4", erra_diagnostico=2, erra_treino=1))
    tentativas = _dos(eventos, "treino_tentativa", "B4")
    assert len(tentativas) >= 2
    for anterior, seguinte in zip(tentativas, tentativas[1:]):
        assert anterior["atividade"] != seguinte["atividade"]
        assert anterior["formato"] != seguinte["formato"]


def test_rf34_o_seletor_recusa_o_item_e_o_formato_anteriores(d):
    itens = d.atividades_do_no("B4")
    e = motor.Estado().com("B4", estado=motor.EM_TREINO,
                           ultima_atividade=itens[0].id,
                           ultimo_formato=itens[0].formato)
    escolhido, _ = motor.proximo_item(d, e, "B4")
    assert escolhido is not None
    assert escolhido.id != itens[0].id
    assert escolhido.formato != itens[0].formato


def test_rf34_a_regra_de_formato_vale_mesmo_havendo_item_inedito(d):
    """O teste acima não distingue as duas metades da regra.

    Com dois itens por nó — um de cada formato —, "não repetir o item
    anterior" e "não repetir o formato anterior" selecionam a mesma coisa:
    tirar qualquer uma das duas do motor não muda nada, e nenhum teste sobre
    este domínio consegue pegar. Aqui o nó recebe um TERCEIRO item, do mesmo
    formato do anterior, e aí as duas regras se separam: sem a de formato, o
    seletor escolheria o item novo do mesmo molde.
    """
    extra = replace(d.atividades_do_no("B4")[1], id="a_b4_extra")
    tres = replace(d, atividades=d.atividades + (extra,))
    itens = tres.atividades_do_no("B4")
    assert len({a.formato for a in itens}) == 2, "o cenário do teste mudou"

    anterior = itens[1]                       # comparar_casos, já apresentado
    e = motor.Estado().com("B4", estado=motor.EM_TREINO,
                           usadas=(itens[0].id, anterior.id),
                           ultima_atividade=anterior.id,
                           ultimo_formato=anterior.formato)
    escolhido, _ = motor.proximo_item(tres, e, "B4")
    assert escolhido is not None
    assert escolhido.formato != anterior.formato, \
        "o seletor pegou o item inédito do mesmo formato (%s)" % escolhido.id


def test_a_reapresentacao_de_item_fica_registrada(d):
    """Com dois itens por nó, o treino reusa o que o diagnóstico já mostrou.
    Isso é aceitável — nunca em sequência —, mas tem de aparecer no log."""
    t, eventos = roda(d, _politica(erra_no="B2", erra_diagnostico=2))
    assert _dos(eventos, "item_reapresentado", "B2"), \
        "o treino usou item inédito: o banco cresceu?"


# --------------------------------------------------------------------------
# RF35 — errar zera a sequência daquele nó, e só dele
# --------------------------------------------------------------------------

def test_rf35_errar_zera_o_streak_do_no(d):
    t, eventos = roda(d, _politica(erra_no="B3", erra_diagnostico=2, erra_treino=1))
    tentativas = _dos(eventos, "treino_tentativa", "B3")
    assert tentativas[0]["correta"] is False
    assert tentativas[0]["streak"] == 0
    assert tentativas[1]["streak"] == 1, "o acerto seguinte não recomeçou a contagem"


def test_rf35_zerar_um_no_nao_mexe_nos_vizinhos(d):
    e = motor.Estado()
    e = e.com("B2", estado=motor.CONFIRMADO, streak=2)
    e = e.com("B3", estado=motor.EM_TREINO, streak=1)
    depois = e.com("B3", streak=0, tentativas=1)
    assert depois.no("B2").estado == motor.CONFIRMADO
    assert depois.no("B2").streak == 2
    assert depois.no("B3").streak == 0


def test_rf35_o_treino_de_um_no_nao_confirma_outro(d):
    t, eventos = roda(d, _politica(erra_no="B2", erra_diagnostico=2))
    por_treino = [c["no"] for c in _dos(eventos, "no_confirmado")
                  if c["via"] == "treino"]
    assert por_treino == ["B2"], por_treino


# --------------------------------------------------------------------------
# RF36 — esgotar o banco encerra em aberto, e a sessão segue
# --------------------------------------------------------------------------

def test_rf36_errar_sempre_no_treino_encerra_o_no_em_aberto(d):
    t, eventos = roda(d, _politica(erra_no="I1", erra_diagnostico=2, erra_treino=99))
    abertos = _dos(eventos, "no_em_aberto", "I1")
    assert abertos, "errar todo o treino não encerrou o nó"
    assert abertos[0]["motivo"] in ("banco esgotado", "teto de tentativas")
    assert t.tela.tipo == "mapa", "a sessão travou em vez de seguir"
    estado_i1 = next(n for n in t.tela.dados["nos"] if n["no"] == "I1")
    assert estado_i1["estado"] == motor.EM_ABERTO


def test_rf36_o_teto_de_tentativas_e_o_do_documento(d):
    assert motor.TETO_TENTATIVAS == 4
    t, eventos = roda(d, _politica(erra_no="I1", erra_diagnostico=2, erra_treino=99))
    assert len(_dos(eventos, "treino_tentativa", "I1")) <= motor.TETO_TENTATIVAS


# --------------------------------------------------------------------------
# O resto do laço
# --------------------------------------------------------------------------

def test_acertar_de_primeira_confirma_sem_treino(d):
    t, eventos = roda(d, _politica())
    assert all(e["via"] == "diagnostico" for e in _dos(eventos, "no_confirmado"))
    assert not _dos(eventos, "treino_tentativa")
    assert all(n["estado"] == motor.CONFIRMADO for n in t.tela.dados["nos"])


def test_a_refutacao_passa_pelas_premissas_que_sustentam_o_no(d):
    """A conclusão I1 se apoia em B1..B4: o percurso é derivado do grafo."""
    t, eventos = roda(d, _politica(erra_no="I1", erra_diagnostico=2))
    inicio = _dos(eventos, "refutacao_iniciada", "I1")[0]
    assert inicio["passos"] == ["B1", "B2", "B3", "B4", "I1"]


def test_a_contradicao_aparece_no_no_que_a_crenca_nega(d):
    t = motor.inicia(d)
    pol = _politica(erra_no="B4", erra_diagnostico=2)
    telas = []
    for _ in range(80):
        telas.append(t.tela)
        if t.tela.tipo == "mapa":
            break
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    com_contradicao = [x for x in telas
                       if x.tipo == "refutacao" and x.dados.get("contradiz")]
    assert len(com_contradicao) == 1
    assert com_contradicao[0].no == "B4"
    assert "lembra" in com_contradicao[0].dados["contradiz"].lower()


def test_a_unidade_sempre_termina(d):
    for no in list(D.nos) + [None]:
        for diag in (0, 1, 2):
            for treino in (0, 1, 99):
                t, _ = roda(d, _politica(erra_no=no, erra_diagnostico=diag,
                                         erra_treino=treino))
                assert t.tela.tipo == "mapa", (no, diag, treino)


def test_o_mapa_distingue_os_tres_caminhos_ate_o_verde(d):
    direto, _ = roda(d, _politica())
    assert all(not n["via_treino"] and not n["vacilou"]
               for n in direto.tela.dados["nos"])

    vacilo, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=1))
    b3 = next(n for n in vacilo.tela.dados["nos"] if n["no"] == "B3")
    assert b3["vacilou"] is True and b3["via_treino"] is False

    treino, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=2))
    b3 = next(n for n in treino.tela.dados["nos"] if n["no"] == "B3")
    assert b3["via_treino"] is True and b3["crenca"] == "declaration_zeroes"


def test_o_streak_nao_escreve_no_reteste_da_pesquisa(d):
    t, eventos = roda(d, _politica(erra_no="B4", erra_diagnostico=2))
    assert "training_streak_completed" in _tipos(eventos)
    assert "belief_retested" not in _tipos(eventos)
