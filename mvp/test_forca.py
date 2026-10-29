"""A força da premissa, e o item que ela escolhe.

`docs/problema.md` define força sem modelo probabilístico e sem parâmetro
estimado. A pergunta não é *quando esta pessoa vai esquecer* — essa exige
medir retenção ao longo de dias — e sim **quão sustentada está esta
premissa agora**. A resposta sai do que já aconteceu com o nó, e de mais
nada: por isso é função pura, e por isso a banca confere linha a linha.

Dois cuidados que a tabela faz questão de distinguir, e que estes testes
defendem um a um:

- **acerto pela razão errada não conta** — não fortalece, e também não
  enfraquece: é evidência sobre outra coisa;
- **erro pela razão certa não enfraquece** — quem errou explicando direito
  escorregou, e escorregão não é premissa bamba.
"""

from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import EstadoNo, Resposta
from mvp.test_motor import _politica, roda

D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


# --------------------------------------------------------------------------
# A função, linha a linha da tabela
# --------------------------------------------------------------------------

def test_o_no_intocado_vale_zero():
    assert motor.forca(EstadoNo()) == 0


def test_cada_superficie_distinta_fortalece():
    uma = EstadoNo(superficies=("reconhecer_conceito",))
    duas = EstadoNo(superficies=("reconhecer_conceito", "prever_resultado"))
    assert motor.forca(uma) > motor.forca(EstadoNo())
    assert motor.forca(duas) > motor.forca(uma)


def test_a_mesma_superficie_duas_vezes_nao_fortalece_duas_vezes():
    """É a regra do CS-5 dita em números: acertar duas vezes o mesmo molde
    de pergunta pode ser reconhecer o molde, não a ideia."""
    uma = EstadoNo(superficies=("reconhecer_conceito",))
    repetida = EstadoNo(superficies=("reconhecer_conceito", "reconhecer_conceito"))
    assert motor.forca(repetida) == motor.forca(uma)


def test_o_acerto_pela_razao_errada_nao_conta():
    """Nem a favor nem contra. O falso positivo é evidência sobre a crença,
    não sobre a premissa do item — tratá-lo como erro puniria o nó pelo
    que aconteceu com outro."""
    nada = EstadoNo()
    falso = EstadoNo(falsos_positivos=2)
    assert motor.forca(falso) == motor.forca(nada)


def test_o_erro_pela_razao_certa_nao_enfraquece():
    """O vacilo: errou a resposta e explicou direito. Quem enuncia a
    premissa corretamente não tem a premissa bamba."""
    assert motor.forca(EstadoNo(erros=1, vacilou=True)) == motor.forca(EstadoNo())


def test_pedir_reexplicacao_enfraquece():
    assert motor.forca(EstadoNo(reexplicacoes=1)) < motor.forca(EstadoNo())


def test_tropecar_no_treino_enfraquece():
    assert motor.forca(EstadoNo(tropecos=1)) < motor.forca(EstadoNo())


def test_acertar_no_treino_fortalece():
    assert motor.forca(EstadoNo(streak=2)) > motor.forca(EstadoNo(streak=0))


def test_o_no_que_veio_de_refutacao_fica_fragil():
    """'Frágil até o reteste', diz a tabela. Uma premissa reconstruída
    depois de uma crença não vale o mesmo que uma que nunca caiu — e o
    reteste da pesquisa é outra medida, longe daqui."""
    limpo = EstadoNo(superficies=("reconhecer_conceito", "prever_resultado"))
    de_refutacao = EstadoNo(superficies=("reconhecer_conceito", "prever_resultado"),
                            crenca="no_value_no_memory")
    assert motor.forca(de_refutacao) < motor.forca(limpo)


def test_a_forca_e_pura(d):
    """Mesma entrada, mesma saída, sem relógio e sem sorteio."""
    en = EstadoNo(superficies=("a", "b"), streak=1, reexplicacoes=1)
    assert len({motor.forca(en) for _ in range(5)}) == 1


# --------------------------------------------------------------------------
# O seletor: a mais fraca que ainda não está de pé
# --------------------------------------------------------------------------

def _estado(**por_no) -> motor.Estado:
    return motor.Estado(fase=motor.DIAGNOSTICO,
                        nos={k: v for k, v in por_no.items()})


def test_o_seletor_escolhe_o_no_mais_fraco(d):
    """Estado montado à mão: B1 e B2 já têm uma superfície, B3 não tem
    nenhuma. O próximo item tem de ser de B3."""
    e = _estado(B1=EstadoNo(superficies=("reconhecer_conceito",)),
                B2=EstadoNo(superficies=("prever_resultado",)))
    t = motor._proxima_diagnostica(d, e)
    assert t.tela.no == "B3"


def test_entre_nos_de_mesma_forca_vale_a_ordem_do_grafo(d):
    """Empate não pode virar sorteio: o motor é puro, e premissa que vem
    antes no grafo sustenta as de depois."""
    t = motor._proxima_diagnostica(d, _estado())
    assert t.tela.no == D.ordem[0]


def test_o_no_mais_forte_so_vem_depois(d):
    e = _estado(B1=EstadoNo(reexplicacoes=2),
                B2=EstadoNo(superficies=("reconhecer_conceito",)))
    assert motor._proxima_diagnostica(d, e).tela.no == "B1"


def test_o_falso_positivo_ainda_passa_na_frente(d):
    """A T6 continua valendo: a pergunta em aberto é sobre AQUELA
    premissa, e adiar não a responde. A preferência vence a força."""
    e = _estado(B4=EstadoNo(falsos_positivos=1))
    t = motor._proxima_diagnostica(d, e, preferir="B4")
    assert t.tela.no == "B4"


def test_o_no_de_pe_nao_e_escolhido_mesmo_sendo_o_mais_fraco(d):
    """Confirmado e em aberto saem da fila: num caso não há o que
    fortalecer, no outro não há com o quê."""
    forte = EstadoNo(estado=motor.CONFIRMADO, crenca="x", reexplicacoes=3)
    e = _estado(B1=forte, B2=EstadoNo(estado=motor.EM_ABERTO, reexplicacoes=3))
    assert motor._proxima_diagnostica(d, e).tela.no == "B3"


# --------------------------------------------------------------------------
# O que isso muda numa unidade inteira
# --------------------------------------------------------------------------

def _diagnosticas(eventos):
    return [e.dados for e in eventos if e.tipo == "atividade_apresentada"
            and e.dados["fase"] == motor.DIAGNOSTICO]


def test_a_unidade_nao_pergunta_duas_vezes_seguidas_sobre_a_mesma_premissa(d):
    """O teste que a tarefa pede. Perguntar de novo sobre o que a pessoa
    acabou de discutir mede o que ela ainda tem na cabeça do item
    anterior, não a premissa.

    Vale quando ninguém força a fila. O falso positivo força (T6), e aí
    duas do mesmo nó em seguida são o comportamento desejado — por isso
    esta política acerta tudo.
    """
    _, eventos = roda(d, _politica())
    nos = [x["no"] for x in _diagnosticas(eventos)]
    assert len(nos) > 5
    assert all(a != b for a, b in zip(nos, nos[1:])), nos


def test_a_primeira_rodada_passa_por_todas_as_premissas_antes_de_repetir(d):
    """O efeito direto de escolher sempre a mais fraca: a unidade varre o
    grafo em largura em vez de esgotar um nó de cada vez."""
    _, eventos = roda(d, _politica())
    nos = [x["no"] for x in _diagnosticas(eventos)]
    assert sorted(nos[:len(D.ordem)]) == sorted(D.ordem)


def test_dentro_do_no_a_teorica_continua_vindo_antes_da_de_codigo(d):
    """A ordem ENTRE os nós mudou; a de dentro, não — é o par que fornece
    as duas superfícies do CS-5."""
    _, eventos = roda(d, _politica())
    for nid in D.ordem:
        itens = [x["item"] for x in _diagnosticas(eventos) if x["no"] == nid]
        assert itens[:2] == ["teorica", "codigo"], (nid, itens)


def test_o_encerramento_registra_a_forca_de_cada_premissa(d):
    """'A unidade termina quando a mais fraca está de pé.' Com duas
    atividades por nó nem sempre dá para chegar lá — então o log diz onde
    cada premissa parou, em vez de o critério ficar sendo afirmado."""
    _, eventos = roda(d, _politica())
    fim = next(e for e in eventos if e.tipo == "unidade_encerrada")
    assert set(fim.dados["forcas"]) == set(D.ordem)
    assert fim.dados["mais_fraca"] in D.ordem
    assert isinstance(fim.dados["mais_fraca_de_pe"], bool)


def test_a_forca_chega_a_tela(d):
    """O painel do pesquisador precisa poder dizer qual premissa está mais
    fraca agora — é a leitura que o número existe para dar."""
    t, _ = roda(d, _politica())
    nos = motor.estado_dos_nos(d, t.estado)
    assert all("forca" in n for n in nos)
    assert any(n["forca"] > 0 for n in nos)


def test_errar_num_no_nao_mexe_na_forca_dos_vizinhos(d):
    """RF35 dito em força: domínio de um conceito não empresta nem tira
    domínio de outro."""
    t, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=2, d=d))
    forcas = {n["no"]: n["forca"] for n in motor.estado_dos_nos(d, t.estado)}
    assert forcas["B3"] < forcas["B1"]
    assert forcas["B1"] == forcas["B2"]


# --------------------------------------------------------------------------
# As duas evidências que enfraquecem precisam ser REGISTRADAS, não só
# sabidas: testar `forca(EstadoNo(tropecos=1))` prova a função e não prova
# que alguma coisa alguma vez escreve naquele campo.
# --------------------------------------------------------------------------

def test_errar_no_treino_registra_o_tropeco_no_no(d):
    t, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=2, erra_treino=1, d=d))
    assert t.estado.no("B3").tropecos == 1
    assert t.estado.no("B1").tropecos == 0


def test_pedir_a_premissa_de_novo_registra_a_reexplicacao_no_no(d):
    """O "ainda não entendi" da refutação. Enfraquece a premissa que a
    pessoa pediu de novo — não o alvo da refutação, quando são outros."""
    t = motor.inicia(d, semente="r")
    pol = _politica(erra_no="B2", erra_diagnostico=2, d=d)
    pedido = False
    for _ in range(120):
        if t.tela.tipo == "refutacao" and not pedido:
            nid = t.tela.no
            t = motor.avanca(d, t.estado, Resposta(repetir=True))
            pedido = True
            en = t.estado.no(nid)
            assert en.reexplicacoes == 1
            from dataclasses import replace
            assert motor.forca(en) == motor.forca(replace(en, reexplicacoes=0)) - 1
            continue
        if t.tela.tipo == "mapa":
            break
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    assert pedido, "nenhuma tela de refutação apareceu"
    assert sum(n.reexplicacoes for n in t.estado.nos.values()) == 1


def test_um_no_confirmado_depois_de_refutacao_tem_forca_baixa(d):
    """O que parece contradição na tela — "✓ confirmada · força −2" — é a
    tabela funcionando. São duas medidas diferentes de propósito:

    `CONFIRMADO` é mecanismo de PRODUTO: decide o que o mapa mostra ao
    aluno, e o streak do treino basta para chegar lá. A força é medida de
    PESQUISA, e nela uma premissa reconstruída depois de uma crença vale
    menos do que uma que nunca caiu — "frágil até o reteste".

    Misturar as duas faria o treino virar uma segunda forma de medir o
    reteste, que é justamente o que o documento separa.
    """
    t, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=2, d=d))
    nos = {n["no"]: n for n in motor.estado_dos_nos(d, t.estado)}
    assert nos["B3"]["estado"] == motor.CONFIRMADO
    assert nos["B3"]["forca"] < nos["B1"]["forca"]
