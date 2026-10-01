"""O laço identifica → refuta → treina → confirma.

Os quatro requisitos do documento (RF33 a RF36) têm um teste cada, e cada um
falha se a regra for removida. Mais os casos de borda do laço: chute não vira
crença, acerto no diagnóstico não passa por treino, e a unidade sempre
termina.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import Resposta


# O domínio é imutável e a carga é barata: uma vez por módulo basta, e
# deixa os roteiros abaixo livres de passá-lo adiante o tempo todo.
D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


# --------------------------------------------------------------------------
# Utilidades de roteiro
# --------------------------------------------------------------------------

def _indice(d, atividade_id, *, correta=True, crenca=None):
    a = next(x for x in d.atividades if x.id == atividade_id)
    if crenca:
        return next(i for i, o in enumerate(a.opcoes) if o.crenca == crenca)
    if correta:
        return a.indice_correto
    return next(i for i, o in enumerate(a.opcoes) if not o.correta)


def roda(d, politica, limite=200):
    """Percorre a unidade inteira. `politica(tela, estado) -> Resposta`."""
    t = motor.inicia(d)
    eventos = list(t.eventos)
    for _ in range(limite):
        if t.tela.tipo == "mapa":
            return t, eventos
        t2 = motor.avanca(d, t.estado, politica(t.tela, t.estado))
        eventos.extend(t2.eventos)
        t = t2
    raise AssertionError("a unidade não terminou em %d passos" % limite)


def sempre_certo(tela, estado):
    return Resposta(escolha=tela.dados.get("correta_para_teste"),
                    confianca="tenho certeza")


def _politica(*, erra_crenca=None, erra_treino_ate=0, d=D):
    """Acerta tudo, menos o que for pedido.

    `erra_crenca`: escolhe o distrator daquela crença na diagnóstica dela.
    `erra_treino_ate`: erra as N primeiras tentativas de treino de cada nó.
    """
    erros_de_treino = {}

    def politica(tela, estado):
        if tela.tipo in ("ensino", "refutacao", "mapa"):
            return Resposta()
        aid = tela.dados["atividade"]
        a = next(x for x in d.atividades if x.id == aid)
        if tela.dados["fase"] == "diagnostico":
            if erra_crenca and any(o.crenca == erra_crenca for o in a.opcoes):
                return Resposta(escolha=_indice(d, aid, crenca=erra_crenca),
                                confianca="tenho certeza")
            return Resposta(escolha=a.indice_correto, confianca="tenho certeza")
        feitos = erros_de_treino.get(a.no, 0)
        if feitos < erra_treino_ate:
            erros_de_treino[a.no] = feitos + 1
            return Resposta(escolha=_indice(d, aid, correta=False),
                            confianca="acho que sei")
        return Resposta(escolha=a.indice_correto, confianca="tenho certeza")

    return politica


def _tipos(eventos):
    return [e.tipo for e in eventos]


# --------------------------------------------------------------------------
# RF33 — depois da refutação, treino; nunca confirmado direto
# --------------------------------------------------------------------------

def test_rf33_nenhum_no_vai_de_refutado_a_confirmado_sem_treino(d):
    t, eventos = roda(d, _politica(erra_crenca="declaration_zeroes"))
    ordem = _tipos(eventos)
    assert "crenca_detectada" in ordem
    assert "refutacao_concluida" in ordem

    i_refuta = ordem.index("refutacao_concluida")
    confirmados_depois = [e for e in eventos[i_refuta:]
                          if e.tipo == "no_confirmado" and e.dados["no"] == "B3"]
    assert confirmados_depois, "o nó refutado nunca foi confirmado"
    assert confirmados_depois[0].dados["via"] == "treino"

    tentativas = [e for e in eventos if e.tipo == "treino_tentativa"
                  and e.dados["no"] == "B3"]
    assert len(tentativas) >= 1, "o nó foi confirmado sem nenhuma tentativa de treino"


def test_rf33_o_streak_exigido_e_o_do_documento(d):
    assert motor.STREAK_ALVO == 2
    t, eventos = roda(d, _politica(erra_crenca="declaration_zeroes"))
    fechou = [e for e in eventos if e.tipo == "training_streak_completed"]
    assert fechou and fechou[0].dados["no"] == "B3"
    assert fechou[0].dados["streak"] == motor.STREAK_ALVO


# --------------------------------------------------------------------------
# RF34 — formato diferente a cada tentativa, e nunca o mesmo item
# --------------------------------------------------------------------------

def test_rf34_o_treino_nao_repete_item_nem_formato_seguido(d):
    t, eventos = roda(d, _politica(erra_crenca="variable_remembers",
                                   erra_treino_ate=2))
    tentativas = [e.dados for e in eventos if e.tipo == "treino_tentativa"
                  and e.dados["no"] == "B4"]
    assert len(tentativas) >= 3, "o roteiro não exercitou o suficiente o treino"

    ids = [x["atividade"] for x in tentativas]
    assert len(ids) == len(set(ids)), "o mesmo item de treino foi reapresentado"
    for anterior, seguinte in zip(tentativas, tentativas[1:]):
        assert anterior["formato"] != seguinte["formato"], \
            "duas tentativas seguidas no mesmo formato: %s" % ids


def test_rf34_o_seletor_recusa_o_formato_anterior(d):
    """Unitário, e desenhado para FALHAR se a regra sumir.

    O item que o seletor pegaria primeiro é marcado como o formato da
    tentativa anterior, SEM entrar em `usadas`: sem a regra de formato ele
    voltaria a ser escolhido, porque continua disponível.
    """
    vazio = motor.Estado().com("B4", estado=motor.EM_TREINO)
    primeiro = motor.proximo_item(d, vazio, "B4")
    assert primeiro is not None

    e = vazio.com("B4", ultimo_formato=primeiro.formato)
    escolhido = motor.proximo_item(d, e, "B4")
    assert escolhido is not None
    assert escolhido.formato != primeiro.formato,         "o seletor repetiu o formato da tentativa anterior (%s)" % escolhido.id

    # E quando só resta item do mesmo formato, ele cede: melhor repetir o
    # formato do que deixar o nó sem como fechar a sequência.
    outros = tuple(a.id for a in d.atividades_do_no("B4", "treino")
                   if a.formato != primeiro.formato)
    sobrou = vazio.com("B4", usadas=outros, ultimo_formato=primeiro.formato)
    assert motor.proximo_item(d, sobrou, "B4").formato == primeiro.formato


# --------------------------------------------------------------------------
# RF35 — errar zera a sequência daquele nó, e só dele
# --------------------------------------------------------------------------

def test_rf35_errar_zera_o_streak_do_no(d):
    t, eventos = roda(d, _politica(erra_crenca="declaration_zeroes",
                                   erra_treino_ate=1))
    tentativas = [e.dados for e in eventos if e.tipo == "treino_tentativa"
                  and e.dados["no"] == "B3"]
    assert tentativas[0]["correta"] is False
    assert tentativas[0]["streak"] == 0, "errar não zerou a sequência"
    assert tentativas[1]["streak"] == 1, "o acerto seguinte não recomeçou a contagem"


def test_rf35_zerar_um_no_nao_mexe_nos_vizinhos(d):
    e = motor.Estado()
    e = e.com("B2", estado=motor.CONFIRMADO, streak=2)
    e = e.com("B3", estado=motor.EM_TREINO, streak=1)

    # erra no B3: só o B3 muda
    depois = e.com("B3", streak=0, tentativas=1)
    assert depois.no("B2").estado == motor.CONFIRMADO
    assert depois.no("B2").streak == 2
    assert depois.no("B3").streak == 0


def test_rf35_o_treino_de_um_no_nao_confirma_outro(d):
    t, eventos = roda(d, _politica(erra_crenca="no_value_no_memory"))
    confirmados = [e.dados for e in eventos if e.tipo == "no_confirmado"]
    por_treino = [c["no"] for c in confirmados if c["via"] == "treino"]
    assert por_treino == ["B2"], por_treino


# --------------------------------------------------------------------------
# RF36 — banco esgotado encerra em aberto, e a sessão segue
# --------------------------------------------------------------------------

def test_rf36_errar_sempre_no_treino_encerra_o_no_em_aberto(d):
    t, eventos = roda(d, _politica(erra_crenca="assignment_symmetric",
                                   erra_treino_ate=99))
    abertos = [e.dados for e in eventos if e.tipo == "no_em_aberto"]
    assert abertos, "errar todo o treino não encerrou o nó"
    assert abertos[0]["no"] == "I1"
    assert abertos[0]["motivo"] in ("banco esgotado", "teto de tentativas")

    assert t.tela.tipo == "mapa", "a sessão travou em vez de seguir"
    estado_i1 = next(n for n in t.tela.dados["nos"] if n["no"] == "I1")
    assert estado_i1["estado"] == motor.EM_ABERTO


def test_rf36_o_teto_de_tentativas_e_o_do_documento(d):
    assert motor.TETO_TENTATIVAS == 4
    t, eventos = roda(d, _politica(erra_crenca="assignment_symmetric",
                                   erra_treino_ate=99))
    tentativas = [e for e in eventos if e.tipo == "treino_tentativa"
                  and e.dados["no"] == "I1"]
    assert len(tentativas) <= motor.TETO_TENTATIVAS


# --------------------------------------------------------------------------
# O resto do laço
# --------------------------------------------------------------------------

def test_acertar_o_diagnostico_confirma_sem_treino(d):
    t, eventos = roda(d, _politica())
    assert all(e.dados["via"] == "diagnostico"
               for e in eventos if e.tipo == "no_confirmado")
    assert not [e for e in eventos if e.tipo == "treino_tentativa"]
    assert all(n["estado"] == motor.CONFIRMADO for n in t.tela.dados["nos"])


def test_errar_chutando_e_lacuna_e_nao_crenca(d):
    def chuta(tela, estado):
        if tela.tipo != "atividade":
            return Resposta()
        aid = tela.dados["atividade"]
        a = next(x for x in d.atividades if x.id == aid)
        if a.id == "a_b3_diag":
            return Resposta(escolha=_indice(d, aid, crenca="declaration_zeroes"),
                            confianca="chutei")
        return Resposta(escolha=a.indice_correto, confianca="tenho certeza")

    t, eventos = roda(d, chuta)
    assert "lacuna_registrada" in _tipos(eventos)
    assert "crenca_detectada" not in _tipos(eventos)
    assert not [e for e in eventos if e.tipo == "treino_tentativa"]


def test_a_refutacao_passa_pelas_premissas_que_sustentam_o_no(d):
    """A conclusão I1 se apoia em B1..B4: o percurso é derivado do grafo."""
    t, eventos = roda(d, _politica(erra_crenca="assignment_symmetric"))
    inicio = next(e for e in eventos if e.tipo == "refutacao_iniciada")
    assert inicio.dados["passos"] == ["B1", "B2", "B3", "B4", "I1"]


def test_a_contradicao_aparece_no_no_que_a_crenca_nega(d):
    t = motor.inicia(d)
    telas = []
    pol = _politica(erra_crenca="variable_remembers")
    for _ in range(100):
        telas.append(t.tela)
        if t.tela.tipo == "mapa":
            break
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    refutacao = [x for x in telas if x.tipo == "refutacao"]
    assert refutacao, "não houve refutação"
    com_contradicao = [x for x in refutacao if x.dados.get("contradiz")]
    assert len(com_contradicao) == 1
    assert com_contradicao[0].no == "B4"
    assert "lembra" in com_contradicao[0].dados["contradiz"].lower()


def test_a_unidade_sempre_termina(d):
    """Qualquer padrão de resposta chega ao mapa."""
    for crenca in list(d.crencas) + [None]:
        for erros in (0, 1, 2, 99):
            t, _ = roda(d, _politica(erra_crenca=crenca, erra_treino_ate=erros))
            assert t.tela.tipo == "mapa", (crenca, erros)


def test_o_mapa_distingue_quem_passou_pelo_treino(d):
    t, _ = roda(d, _politica(erra_crenca="declaration_zeroes"))
    por_no = {n["no"]: n for n in t.tela.dados["nos"]}
    assert por_no["B3"]["via_treino"] is True
    assert por_no["B3"]["crenca"] == "declaration_zeroes"
    assert por_no["B2"]["via_treino"] is False


def test_o_streak_nao_escreve_no_reteste_da_pesquisa(d):
    """O streak é mecanismo de produto. V3 continua sendo outra medida."""
    t, eventos = roda(d, _politica(erra_crenca="variable_remembers"))
    assert "training_streak_completed" in _tipos(eventos)
    assert "belief_retested" not in _tipos(eventos)
