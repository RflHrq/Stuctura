"""Os cinco estados, e o nó em que cada um é registrado.

A tabela de `docs/problema.md`, virada teste. É aqui que moram CS-1, CS-2,
CS-3 e CS-5 do PRD — os quatro critérios que separam este sistema de um
questionário de múltipla escolha.

O que a camada 2 mudou, e que estes testes defendem: **a razão é a prova**.
Antes, um erro isolado era "vacilo até prova em contrário" e o sistema
fazia uma segunda pergunta para decidir. Agora quem erra pelo motivo certo
escorregou, e quem erra pelo motivo errado com confiança nomeou a própria
crença — não há o que descobrir numa segunda pergunta.
"""

from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import Razao, Resposta

D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


def episodio(d, item: str, *, certa: bool, razao_certa: bool,
             confianca: str, crenca: str | None = None,
             estado: motor.Estado | None = None):
    """Um episódio inteiro num item escolhido, com as três camadas."""
    a = next(x for x in d.atividades if x.id == item)
    base = estado or motor.Estado()
    # O que uma sessão de verdade já teria feito, e que este atalho precisa
    # imitar:
    #   `_apresenta` marca o item como visto — sem isto o seletor
    #   ofereceria a MESMA pergunta de novo, e o teste mediria o atalho em
    #   vez da regra;
    #   a abertura marca o nó como ENSINADO — sem isto o primeiro contato
    #   dispara e a tela seguinte é a premissa, não o item.
    en = base.no(a.no)
    base = base.com(a.no, usadas=en.usadas + (a.id,), ensinado=True,
                    ultimo_formato=a.formato, ultima_atividade=a.id)
    t = motor.avanca(
        d, motor.replace(base, fase=motor.DIAGNOSTICO, atividade=a.id, alvo=a.no),
        Resposta(escolha=(a.indice_correto if certa else _errada(a, crenca)),
                 ms=1))
    eventos = list(t.eventos)
    if t.tela.tipo == "razao":
        razoes = t.estado.pendente.razoes
        i = (next(k for k, z in enumerate(razoes) if z.correta) if razao_certa
             else next(k for k, z in enumerate(razoes)
                       if not z.correta and (crenca is None or z.crenca == crenca)))
        t = motor.avanca(d, t.estado, Resposta(escolha=i, ms=1))
        eventos.extend(t.eventos)
    t = motor.avanca(d, t.estado, Resposta(confianca=confianca, ms=1))
    eventos.extend(t.eventos)
    return t, eventos


def _errada(a, crenca=None):
    if crenca:
        return next(i for i, o in enumerate(a.opcoes) if o.crenca == crenca)
    return next(i for i, o in enumerate(a.opcoes) if not o.correta)


def classificado(eventos):
    return next(e for e in eventos if e.tipo == "episodio_classificado").dados["estado"]


# --------------------------------------------------------------------------
# A tabela, linha por linha — função pura, sem motor
# --------------------------------------------------------------------------

CERTA = Razao(texto="x", correta=True, no="B1")
ERRADA = Razao(texto="y", crenca="c", no="B2")

TABELA = [
    (True,  CERTA,  "tenho certeza", motor.CONFIRMADA),
    (True,  CERTA,  "acho que sei",  motor.FRAGIL_EP),
    (True,  CERTA,  "chutei",        motor.FRAGIL_EP),
    (True,  ERRADA, "tenho certeza", motor.FALSO_POSITIVO_EP),
    (True,  ERRADA, "chutei",        motor.FALSO_POSITIVO_EP),
    (False, CERTA,  "tenho certeza", motor.FALSO_NEGATIVO_EP),
    (False, CERTA,  "chutei",        motor.FALSO_NEGATIVO_EP),
    (False, ERRADA, "tenho certeza", motor.CRENCA_EP),
    (False, ERRADA, "acho que sei",  motor.CRENCA_EP),
    (False, ERRADA, "chutei",        motor.LACUNA_EP),
]


@pytest.mark.parametrize("certa,razao,confianca,esperado", TABELA)
def test_a_tabela_de_classificacao(certa, razao, confianca, esperado):
    assert motor.classifica(certa, razao, confianca) == esperado


def test_o_meio_da_escala_puxa_para_o_lado_conservador():
    """Decisão 11, escrita como teste: *acho que sei* não confirma um
    acerto, e não livra um erro de refutação."""
    assert motor.classifica(True, CERTA, "acho que sei") == motor.FRAGIL_EP
    assert motor.classifica(False, ERRADA, "acho que sei") == motor.CRENCA_EP


# --------------------------------------------------------------------------
# CS-1 — acerto com razão errada não confirma
# --------------------------------------------------------------------------

def test_cs1_acertar_pela_razao_errada_nao_confirma_a_premissa(d):
    t, eventos = episodio(d, "ciu_kc00_002", certa=True, razao_certa=False,
                          confianca="tenho certeza", crenca="type_is_a_hint")
    assert classificado(eventos) == motor.FALSO_POSITIVO_EP
    assert t.estado.no("B1").estado == motor.FALSO_POSITIVO
    assert not any(e.tipo == "no_confirmado" for e in eventos)


def test_cs1_o_falso_positivo_fica_contado_na_crenca(d):
    """Contado no nó que a crença nega: é lá que ele vai virar refutação
    quando acontecer de novo (T6)."""
    t, _ = episodio(d, "ciu_kc00_002", certa=True, razao_certa=False,
                    confianca="tenho certeza", crenca="no_value_no_memory")
    assert t.estado.no("B2").falsos_positivos == 1
    assert t.estado.no("B1").falsos_positivos == 0


# --------------------------------------------------------------------------
# CS-2 — a crença é registrada no nó que ELA nega
# --------------------------------------------------------------------------

def test_cs2_a_crenca_vai_para_o_no_que_ela_nega_e_so_para_ele(d):
    """O item mira B1; a razão escolhida nega B2. Quem fica vermelho é B2."""
    t, eventos = episodio(d, "ciu_kc00_002", certa=False, razao_certa=False,
                          confianca="tenho certeza", crenca="no_value_no_memory")
    assert classificado(eventos) == motor.CRENCA_EP
    detectada = next(e for e in eventos if e.tipo == "crenca_detectada").dados
    assert detectada["no"] == "B2"
    assert detectada["veio_do_item_de"] == "B1"
    assert t.estado.no("B2").estado == motor.REFUTADO
    assert t.estado.no("B1").estado != motor.REFUTADO


def test_cs2_a_refutacao_percorre_o_no_negado_nao_o_do_item(d):
    t, _ = episodio(d, "ciu_kc00_002", certa=False, razao_certa=False,
                    confianca="tenho certeza", crenca="no_value_no_memory")
    assert t.tela.tipo == "validacao"
    assert t.tela.no == "B2"
    assert t.estado.alvo == "B2"


def test_cs2_uma_crenca_do_proprio_no_continua_indo_para_ele(d):
    t, eventos = episodio(d, "ciu_kc00_002", certa=False, razao_certa=False,
                          confianca="tenho certeza", crenca="type_is_a_hint")
    assert next(e for e in eventos
                if e.tipo == "crenca_detectada").dados["no"] == "B1"
    assert t.estado.no("B1").estado == motor.REFUTADO


# --------------------------------------------------------------------------
# CS-3 — erro pelo motivo certo não refuta
# --------------------------------------------------------------------------

def test_cs3_errar_pela_razao_certa_nao_dispara_refutacao(d):
    t, eventos = episodio(d, "ciu_kc00_002", certa=False, razao_certa=True,
                          confianca="tenho certeza")
    assert classificado(eventos) == motor.FALSO_NEGATIVO_EP
    tipos = [e.tipo for e in eventos]
    assert "crenca_detectada" not in tipos
    assert "refutacao_iniciada" not in tipos
    assert t.tela.tipo != "validacao"


def test_cs3_o_vacilo_fica_registrado_mesmo_sem_refutar(d):
    """Não contestar não é ignorar: o pesquisador quer saber quão direto
    foi o caminho até o verde."""
    t, eventos = episodio(d, "ciu_kc00_002", certa=False, razao_certa=True,
                          confianca="tenho certeza")
    assert any(e.tipo == "vacilo_detectado" for e in eventos)
    assert t.estado.no("B1").vacilou is True


# --------------------------------------------------------------------------
# CS-5 — duas superfícies para confirmar
# --------------------------------------------------------------------------

def test_cs5_um_acerto_so_deixa_a_premissa_fragil(d):
    t, eventos = episodio(d, "ciu_kc00_002", certa=True, razao_certa=True,
                          confianca="tenho certeza")
    assert classificado(eventos) == motor.CONFIRMADA
    assert t.estado.no("B1").estado == motor.FRAGIL
    assert any(e.tipo == "no_fragil" for e in eventos)


def test_cs5_duas_superficies_diferentes_confirmam(d):
    t, _ = episodio(d, "ciu_kc00_002", certa=True, razao_certa=True,
                    confianca="tenho certeza")
    t2, eventos = episodio(d, "ciu_kc00_001", certa=True, razao_certa=True,
                           confianca="tenho certeza", estado=t.estado)
    assert t2.estado.no("B1").estado == motor.CONFIRMADO
    confirmado = next(e for e in eventos if e.tipo == "no_confirmado").dados
    assert len(confirmado["superficies"]) == 2


def test_cs5_acerto_sem_conviccao_nao_conta_superficie(d):
    t, _ = episodio(d, "ciu_kc00_002", certa=True, razao_certa=True,
                    confianca="acho que sei")
    assert t.estado.no("B1").estado == motor.FRAGIL
    assert t.estado.no("B1").superficies == ()


# --------------------------------------------------------------------------
# T7 — o que a tela recebe para desenhar os cinco estados
# --------------------------------------------------------------------------

def test_estado_dos_nos_entrega_os_cinco_estados(d):
    """O motor conhece cinco estados; a projeção que vai para a tela tem de
    saber dizer os cinco, ou o mapa mostra menos do que o sistema sabe."""
    e = motor.Estado()
    for no, estado in (("B1", motor.FRAGIL), ("B2", motor.FALSO_POSITIVO),
                       ("B3", motor.REFUTADO), ("B4", motor.LACUNA),
                       ("I1", motor.CONFIRMADO)):
        e = e.com(no, estado=estado)
    vistos = {n["no"]: n["estado"] for n in motor.estado_dos_nos(d, e)}
    assert vistos == {"B1": motor.FRAGIL, "B2": motor.FALSO_POSITIVO,
                      "B3": motor.REFUTADO, "B4": motor.LACUNA,
                      "I1": motor.CONFIRMADO}


def test_a_projecao_diz_de_onde_a_crenca_veio(d):
    """O caso cruzado precisa de explicação na tela: um nó fica vermelho sem
    a pessoa ter respondido nada sobre ele."""
    t, _ = episodio(d, "ciu_kc00_002", certa=False, razao_certa=False,
                    confianca="tenho certeza", crenca="no_value_no_memory")
    b2 = next(n for n in motor.estado_dos_nos(d, t.estado) if n["no"] == "B2")
    assert b2["origem_crenca"] == "B1"
    assert b2["crenca_afirma"].startswith("Se eu nao dei valor")


def test_uma_crenca_do_proprio_no_nao_tem_origem_cruzada(d):
    t, _ = episodio(d, "ciu_kc00_002", certa=False, razao_certa=False,
                    confianca="tenho certeza", crenca="type_is_a_hint")
    b1 = next(n for n in motor.estado_dos_nos(d, t.estado) if n["no"] == "B1")
    assert b1["origem_crenca"] == ""


def test_a_projecao_conta_as_superficies(d):
    t, _ = episodio(d, "ciu_kc00_002", certa=True, razao_certa=True,
                    confianca="tenho certeza")
    b1 = next(n for n in motor.estado_dos_nos(d, t.estado) if n["no"] == "B1")
    assert b1["estado"] == motor.FRAGIL and b1["superficies"] == 1


# --------------------------------------------------------------------------
# CS-4 — "não sei" nas três camadas, e nunca vira crença
# --------------------------------------------------------------------------

def _no_item(d, item):
    a = next(x for x in d.atividades if x.id == item)
    return motor.replace(motor.Estado(), fase=motor.DIAGNOSTICO,
                         atividade=a.id, alvo=a.no), a


def test_cs4_nao_sei_na_camada_1_e_lacuna_declarada(d):
    """Obrigar a escolher FABRICA chute: o sistema cria o falso positivo
    que depois tenta detectar. Com a opção disponível, a lacuna vira dado
    observado em vez de inferido de confiança baixa."""
    estado, a = _no_item(d, "ciu_kc00_002")
    t = motor.avanca(d, estado, Resposta(nao_sei=True, ms=1))
    ep = next(e for e in t.eventos if e.tipo == "episodio_classificado").dados
    assert ep["estado"] == motor.LACUNA_EP
    assert ep["nao_sei"] == "camada1"
    assert t.estado.no(a.no).estado == motor.LACUNA


def test_cs4_nao_sei_na_camada_1_nao_pergunta_as_outras_duas(d):
    """Quem não respondeu não tem o que justificar nem convicção a
    declarar. Perguntar assim mesmo seria teatro."""
    estado, _ = _no_item(d, "ciu_kc00_002")
    t = motor.avanca(d, estado, Resposta(nao_sei=True, ms=1))
    tipos = [e.tipo for e in t.eventos]
    assert "camada2_respondida" not in tipos
    assert "camada3_respondida" not in tipos
    assert t.tela.tipo not in ("razao", "confianca")


def test_cs4_nao_sei_na_camada_2_e_lacuna(d):
    estado, _ = _no_item(d, "ciu_kc00_002")
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    t = motor.avanca(d, estado, Resposta(escolha=a.indice_correto, ms=1))
    t = motor.avanca(d, t.estado, Resposta(nao_sei=True, ms=1))
    ep = next(e for e in t.eventos if e.tipo == "episodio_classificado").dados
    assert ep["estado"] == motor.LACUNA_EP
    assert ep["nao_sei"] == "camada2"


def test_cs4_nao_sei_na_camada_3_e_lacuna(d):
    estado, _ = _no_item(d, "ciu_kc00_002")
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    t = motor.avanca(d, estado, Resposta(escolha=a.indice_correto, ms=1))
    certa = next(i for i, z in enumerate(t.estado.pendente.razoes) if z.correta)
    t = motor.avanca(d, t.estado, Resposta(escolha=certa, ms=1))
    t = motor.avanca(d, t.estado, Resposta(nao_sei=True, ms=1))
    ep = next(e for e in t.eventos if e.tipo == "episodio_classificado").dados
    assert ep["estado"] == motor.LACUNA_EP
    assert ep["nao_sei"] == "camada3"


def test_cs4_nao_sei_nunca_vira_crenca(d):
    """A regra que protege a pessoa: o sistema não refuta o que ela não
    pensa. Errar e dizer que não sabe o porquê não é sustentar uma ideia."""
    estado, _ = _no_item(d, "ciu_kc00_002")
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    errada = next(i for i, o in enumerate(a.opcoes) if not o.correta)
    for camada in range(3):
        t = motor.avanca(d, estado, Resposta(nao_sei=(camada == 0),
                                             escolha=None if camada == 0 else errada,
                                             ms=1))
        if camada >= 1 and t.tela.tipo == "razao":
            t = motor.avanca(d, t.estado, Resposta(nao_sei=True, ms=1))
        tipos = [e.tipo for e in t.eventos]
        assert "crenca_detectada" not in tipos, camada
        assert "refutacao_iniciada" not in tipos, camada


def test_cs4_nao_sei_no_treino_zera_a_sequencia(d):
    """A sequência mede premissa de pé; quem não sabe não a tem de pé."""
    e = motor.Estado(fase=motor.TREINO, atividade="ciu_kc00_t03", alvo="B2")
    e = e.com("B2", estado=motor.EM_TREINO, streak=1)
    t = motor.avanca(d, e, Resposta(nao_sei=True, ms=1))
    assert t.estado.no("B2").streak == 0
    tentativa = next(ev for ev in t.eventos if ev.tipo == "treino_tentativa")
    assert tentativa.dados["correta"] is False


# --------------------------------------------------------------------------
# T6 — o falso positivo deixa de ficar parado
# --------------------------------------------------------------------------

def _falso_positivo(d, item, crenca, estado=None):
    return episodio(d, item, certa=True, razao_certa=False,
                    confianca="tenho certeza", crenca=crenca, estado=estado)


def test_t6_um_falso_positivo_traz_outra_superficie_do_mesmo_no(d):
    """A pergunta em aberto é sobre AQUELA premissa. Seguir adiante não a
    responde — e o item seguinte sai do mesmo nó, noutro formato.

    O item é de **B3**, e não de B1, de propósito: B1 é o primeiro da ordem
    do grafo, e um teste em B1 passaria mesmo sem a regra, porque a fila
    normal já voltaria para lá. O teste tem de morder.
    """
    t, _ = _falso_positivo(d, "ciu_kc00_005", "declaration_zeroes")
    assert t.tela.tipo == "atividade"
    assert t.tela.no == "B3", "seguiu adiante em vez de insistir no nó"
    seguinte = next(x for x in d.atividades if x.id == t.tela.dados["atividade"])
    assert seguinte.id != "ciu_kc00_005"
    assert seguinte.tipo == "codigo"


def test_t6_um_falso_positivo_nao_refuta(d):
    t, eventos = _falso_positivo(d, "ciu_kc00_002", "no_value_no_memory")
    assert not any(e.tipo == "crenca_detectada" for e in eventos)
    assert t.estado.no("B2").estado != motor.REFUTADO


def test_t6_dois_na_mesma_crenca_refutam_o_no_que_ela_nega(d):
    """Uma vez pode ser acidente de alternativa; duas, na mesma ideia, é a
    ideia. E quem é refutado é B2 — o nó que a crença nega —, não B1."""
    t, _ = _falso_positivo(d, "ciu_kc00_002", "no_value_no_memory")
    t2, eventos = _falso_positivo(d, "ciu_kc00_001", "no_value_no_memory",
                                  estado=t.estado)
    detectada = next(e for e in eventos if e.tipo == "crenca_detectada").dados
    assert detectada["no"] == "B2"
    assert detectada["via"] == "falso positivo repetido"
    assert detectada["vezes"] == 2
    assert t2.estado.no("B2").estado == motor.REFUTADO
    assert t2.tela.tipo == "validacao" and t2.tela.no == "B2"


def test_t6_o_limiar_e_o_parametro_aceito(d):
    assert motor.FALSOS_POSITIVOS_PARA_CRENCA == 2


def test_t6_dois_falsos_positivos_de_crencas_diferentes_nao_refutam(d):
    """A conta é por crença, não por pessoa: explicar mal duas perguntas
    por ideias diferentes não é sustentar nenhuma delas."""
    t, _ = _falso_positivo(d, "ciu_kc00_002", "no_value_no_memory")
    t2, eventos = _falso_positivo(d, "ciu_kc00_002", "type_is_a_hint",
                                  estado=t.estado)
    assert not any(e.tipo == "crenca_detectada" for e in eventos)
    assert t2.estado.no("B2").falsos_positivos == 1
    assert t2.estado.no("B1").falsos_positivos == 1


def _b2_confirmado():
    return motor.Estado().com(
        "B2", estado=motor.CONFIRMADO,
        superficies=("reconhecer_conceito", "comparar_casos"))


def test_t6_a_crenca_de_um_no_confirmado_sai_do_cardapio(d):
    """A cena que o T6 testava deixou de ser alcançável, e é de propósito.

    Era assim: B2 confirmado, e a pessoa escolhendo `no_value_no_memory`
    — que nega B2 — como razão num item de B1. A unidade já tratou aquela
    ideia; continuar oferecendo-a em toda cédula é o que gasta os itens do
    nó hospedeiro sem nunca medi-lo (C1). Quem checa se ela voltou é o
    reteste, que tem fase própria.
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    sem_estado = {z.crenca for z in motor.razoes_de(d, a)}
    com_estado = {z.crenca for z in motor.razoes_de(d, a, _b2_confirmado())}
    assert "no_value_no_memory" in sem_estado
    assert "no_value_no_memory" not in com_estado
    assert len(com_estado) >= 1, "sobrou razão errada nenhuma"


def test_t6_nao_refuta_um_no_ja_confirmado(d):
    """A garantia original, viva onde a cena ainda acontece.

    Em `ciu_kc00_001` os DOIS distratores apontam a mesma crença: filtrar
    deixaria uma razão só, então o fallback devolve a lista inteira e a
    explicação ruim continua podendo ser dada. É exatamente aí que a regra
    precisa valer — se a premissa já está de pé por duas superfícies, uma
    explicação ruim noutra pergunta não derruba o que foi demonstrado.
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_001")
    oferecidas = {z.crenca for z in motor.razoes_de(d, a, _b2_confirmado())}
    assert "no_value_no_memory" in oferecidas, "o fallback não valeu; o teste perdeu a cena"

    t, eventos = _falso_positivo(d, "ciu_kc00_001", "no_value_no_memory",
                                 estado=_b2_confirmado())
    assert not any(ev.tipo == "crenca_detectada" for ev in eventos)
    assert t.estado.no("B2").estado == motor.CONFIRMADO
