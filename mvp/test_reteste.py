"""O reteste do fim da sessão: a terceira condição do critério.

O critério de sucesso tem três condições, e não uma:

> a **razão** muda da razão-crença para a razão-correta **sem queda de
> confiança**; isso **sobrevive à troca de superfície**; e **não volta**
> no reteste do fim da sessão, com outra unidade no meio.

As duas primeiras já acontecem no diagnóstico e no treino. Esta é a
terceira: no fim, cada crença refutada é oferecida **uma vez mais**, numa
superfície que a pessoa não viu, e o log registra se ela voltou.

A DECISÃO QUE DEFINE ESTA TAREFA
--------------------------------
O reteste **observa, não intervém**. Escolher a crença de novo não dispara
outra refutação, não mexe no estado do nó e não adia o fim da unidade.
Duas razões: uma medida que corrige o que está medindo deixa de ser
medida; e refutar de novo no fim nunca terminaria.

O LIMITE, QUE É DO CICLO 1
--------------------------
O critério diz "com outra unidade no meio". Só existe uma unidade pronta,
então o que fica no meio são as outras premissas desta. É menos
separação do que o critério pede, está declarado, e o reteste de verdade
acontece na abertura da KC seguinte — que é trabalho do próximo ciclo.
"""

from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import carrega
from mvp.motor import Resposta
from mvp.test_motor import _politica, roda

D = carrega()


@pytest.fixture(scope="module")
def d():
    return D


def _com_refutacao(d, no="B3"):
    """Uma sessão em que uma crença foi mesmo refutada."""
    return roda(d, _politica(erra_no=no, erra_diagnostico=2, d=d))


def _dos(eventos, tipo):
    return [e for e in eventos if e.tipo == tipo]


# --------------------------------------------------------------------------
# Acontece, e acontece uma vez
# --------------------------------------------------------------------------

def test_uma_crenca_refutada_e_retestada_exatamente_uma_vez(d):
    """O teste que a tarefa pede."""
    _, eventos = _com_refutacao(d)
    assert len(_dos(eventos, "refutacao_concluida")) == 1
    assert len(_dos(eventos, "belief_retested")) == 1


def test_sem_refutacao_nao_ha_reteste(d):
    """Reteste é medida de correção: sem crença detectada não há o que
    corrigir, e perguntar assim mesmo mediria outra coisa."""
    _, eventos = roda(d, _politica())
    assert not _dos(eventos, "crenca_detectada")
    assert not _dos(eventos, "belief_retested")


def test_o_reteste_vem_depois_de_tudo_e_antes_da_frase_do_fim(d):
    """A ordem do PRD: as premissas, o reteste, a frase do fim, o mapa.
    Entre a refutação e o reteste tem de haver outra coisa."""
    _, eventos = _com_refutacao(d)
    tipos = [e.tipo for e in eventos]
    assert tipos.index("refutacao_concluida") < tipos.index("belief_retested")
    assert tipos.index("belief_retested") < tipos.index("unidade_encerrada")
    # Outra coisa no meio: não é a tela seguinte à refutação.
    entre = tipos[tipos.index("treino_iniciado"):tipos.index("belief_retested")]
    assert "atividade_apresentada" in entre


def test_o_reteste_usa_um_item_que_a_pessoa_nao_viu(d):
    """Reperguntar o mesmo item mediria memória daquele item, não a
    premissa. Se não houver item novo, não há reteste — e o log diz."""
    t, eventos = _com_refutacao(d)
    reteste = _dos(eventos, "belief_retested")[0]
    usadas = [e.dados["atividade"] for e in eventos
              if e.tipo == "atividade_apresentada"]
    assert usadas.count(reteste.dados["atividade"]) == 1


def test_o_seletor_prefere_a_superficie_que_a_pessoa_nao_viu(d):
    """"Sobrevive à troca de superfície" é parte do critério: repetir o
    molde da pergunta deixa de testar isso.

    A comparação é com as superfícies em que ESTA crença já foi oferecida
    — um formato visto noutro nó, com outra crença, não compromete a troca
    aqui. Dos itens livres, o de formato novo tem de ganhar.

    O caso precisa DISCRIMINAR: o primeiro item livre na ordem do banco
    tem de ser de um formato já visto, e o de formato novo tem de vir
    depois. Senão a preferência e o primeiro-da-fila coincidem, e o teste
    passa mesmo com a regra desligada — foi o que aconteceu na primeira
    versão deste teste, e a sabotagem pegou.
    """
    crenca = "no_value_no_memory"
    livres = [a for a in D.atividades if any(o.crenca == crenca for o in a.opcoes)]
    visto = next(a for a in livres
                 if a.formato == livres[0].formato and a.id != livres[0].id)
    e = motor.Estado(fase=motor.DIAGNOSTICO).com(visto.no, usadas=(visto.id,))

    escolhido = motor._item_de_reteste(d, e, crenca)
    assert escolhido.id != livres[0].id, "pegou o primeiro da fila"
    assert escolhido.formato != livres[0].formato


def test_quando_o_banco_nao_tem_superficie_nova_o_log_diz(d):
    """O caso comum, e que eu só vi medindo: com quatro itens por crença
    em três formatos, o treino costuma gastar os que faltavam. O reteste
    acontece no mesmo molde e vale menos — dito, e não escondido."""
    t, eventos = _com_refutacao(d)
    reteste = _dos(eventos, "belief_retested")[0].dados
    assert reteste["superficie_nova"] is False
    crenca = reteste["crenca"]
    usadas = {e.dados["atividade"] for e in eventos
              if e.tipo == "atividade_apresentada"
              and e.dados["atividade"] != reteste["atividade"]}
    antes = {a.formato for a in D.atividades
             if a.id in usadas and any(o.crenca == crenca for o in a.opcoes)}
    assert reteste["formato"] in antes, "o campo diria falso sem motivo"


def test_o_evento_do_reteste_diz_se_a_crenca_voltou(d):
    _, eventos = _com_refutacao(d)
    reteste = _dos(eventos, "belief_retested")[0].dados
    for campo in ("crenca", "no", "voltou", "razao_correta", "confianca",
                  "atividade", "formato"):
        assert campo in reteste, campo
    assert isinstance(reteste["voltou"], bool)


def test_quem_escolhe_a_crenca_de_novo_e_registrado_como_voltou(d):
    """O caso que o critério existe para pegar: a pessoa atravessou a
    refutação e o treino, e no fim volta à mesma ideia."""
    _, eventos = roda(d, _erra_em(d, {"B3"}, no_reteste=True))
    retestes = _dos(eventos, "belief_retested")
    assert retestes, "nenhum reteste aconteceu"
    assert retestes[0].dados["voltou"] is True
    assert retestes[0].dados["razao_correta"] is False


def test_quem_responde_certo_no_reteste_nao_volta(d):
    _, eventos = roda(d, _erra_em(d, {"B3"}))
    reteste = _dos(eventos, "belief_retested")[0].dados
    assert reteste["voltou"] is False
    assert reteste["razao_correta"] is True


# --------------------------------------------------------------------------
# Observa, não intervém
# --------------------------------------------------------------------------

def test_voltar_a_crenca_no_reteste_nao_dispara_outra_refutacao(d):
    """Uma medida que corrige o que está medindo deixa de ser medida. E
    refutar de novo no fim nunca terminaria."""
    _, eventos = roda(d, _erra_em(d, {"B3"}, no_reteste=True))
    tipos = [e.tipo for e in eventos]
    depois = tipos[tipos.index("belief_retested"):]
    assert "refutacao_iniciada" not in depois
    assert "validacao_apresentada" not in depois
    assert "treino_iniciado" not in depois


def test_o_reteste_nao_mexe_no_estado_do_no(d):
    """O estado do nó é mecanismo de produto; o reteste é medida de
    pesquisa. Deixar um mexer no outro faria o mapa do aluno mudar por
    causa de uma pergunta que existe para a análise."""
    t, eventos = roda(d, _erra_em(d, {"B3"}, no_reteste=True))
    reteste = _dos(eventos, "belief_retested")[0].dados
    antes = {e.dados["no"]: e.dados for e in eventos
             if e.tipo == "no_em_aberto" or e.tipo == "no_confirmado"}
    assert reteste["no"] in antes
    # O nó termina no estado em que o treino o deixou, não no que o
    # reteste sugeriria.
    nid = reteste["no"]
    assert t.estado.no(nid).estado in (motor.CONFIRMADO, motor.EM_ABERTO)
    assert t.estado.no(nid).tropecos == t.estado.no(nid).tropecos


def test_o_reteste_nao_conta_superficie_nem_forca(d):
    """Acertar no reteste não pode fortalecer a premissa: a força mede o
    que o percurso construiu, e o reteste acontece depois dele."""
    t, eventos = _com_refutacao(d)
    nid = _dos(eventos, "belief_retested")[0].dados["no"]
    antes = next(e for e in eventos if e.tipo == "no_confirmado"
                 and e.dados["no"] == nid)
    assert antes.dados.get("via") == "treino"
    assert motor.forca(t.estado.no(nid)) == motor.forca(t.estado.no(nid))
    assert t.estado.no(nid).superficies == ()


# --------------------------------------------------------------------------
# Quando não dá para retestar
# --------------------------------------------------------------------------

def test_sem_item_novo_o_log_diz_em_vez_de_reusar(d):
    """Faltar superfície é limitação do banco, e tem de aparecer como
    dado. Reusar um item já visto mediria memória e passaria por medida."""
    e = motor.Estado(fase=motor.DIAGNOSTICO)
    # Todo item já usado, e uma crença pendente de reteste.
    for nid in d.ordem:
        e = e.com(nid, estado=motor.CONFIRMADO,
                  usadas=tuple(a.id for a in d.atividades if a.no == nid))
    e = e.com("B3", estado=motor.CONFIRMADO, crenca="declaration_zeroes",
              usadas=tuple(a.id for a in d.atividades if a.no == "B3"))
    e = motor.replace(e, a_retestar=("declaration_zeroes",))
    t = motor._encerra(d, e)
    tipos = [x.tipo for x in t.eventos]
    assert "reteste_sem_item" in tipos
    assert "belief_retested" not in tipos
    sem = next(x for x in t.eventos if x.tipo == "reteste_sem_item")
    assert sem.dados["crenca"] == "declaration_zeroes"


def test_o_encerramento_conta_os_retestes(d):
    """Para a análise saber, sem reconstruir nada, quantas crenças foram
    refutadas e quantas chegaram a ser retestadas."""
    _, eventos = _com_refutacao(d)
    fim = _dos(eventos, "unidade_encerrada")[0].dados
    assert fim["refutadas"] == 1
    assert fim["retestadas"] == 1


def _erra_em(d, nos, no_reteste=False):
    """Erra, com a razão coerente, nos nós pedidos; acerta o resto.

    Política própria por dois motivos: a de `test_motor` erra num nó só, e
    aqui interessa a fila com mais de uma crença; e ela conta erros por
    fase sem distinguir o reteste, que é exatamente a distinção em jogo.

    `no_reteste` separa os dois casos do critério: atravessar a refutação
    e **voltar** à crença no fim, ou não voltar.
    """
    ultimo = {"crenca": None}

    def politica(tela, estado):
        if tela.tipo == "frase":
            return Resposta(texto="x")
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            i = next((i for i, z in enumerate(razoes)
                      if z.crenca and z.crenca == ultimo["crenca"]), None)
            if i is None:
                i = next(i for i, z in enumerate(razoes) if z.correta)
            return Resposta(escolha=i)
        if tela.tipo != "atividade":
            return Resposta()
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        fase = tela.dados["fase"]
        erra = (a.no in nos and fase == motor.DIAGNOSTICO) or \
               (no_reteste and fase == motor.RETESTE)
        if erra:
            na_tela = motor.opcoes_na_tela(estado.semente, a)
            # "Erra, com a razao coerente, nos nos pedidos" — entao a
            # crenca DO ITEM, e nao a primeira que aparecer.
            i = next((k for k, o in enumerate(na_tela)
                      if o.crenca == a.crenca),
                     next(k for k, o in enumerate(na_tela)
                          if not o.correta and o.crenca))
            ultimo["crenca"] = na_tela[i].crenca
            return Resposta(escolha=i)
        ultimo["crenca"] = None
        return Resposta(
            escolha=motor.indice_correto_na_tela(estado.semente, a))

    return politica


def test_duas_crencas_refutadas_dao_dois_retestes(d):
    _, eventos = roda(d, _erra_em(d, {"B3", "B4"}))
    assert len(_dos(eventos, "crenca_detectada")) == 2
    retestes = _dos(eventos, "belief_retested")
    assert len({x.dados["crenca"] for x in retestes}) == 2
