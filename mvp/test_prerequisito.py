# -*- coding: utf-8 -*-
"""O portão de pré-requisito: uma cadeia só roda com o que já foi ensinado.

O PRINCÍPIO, decidido pelo dono: *uma cadeia só pode ser acionada se
todos os seus degraus forem respondíveis com conhecimentos que o aluno já
teve oportunidade de aprender.*

E A MEDIÇÃO QUE O TORNOU NECESSÁRIO, não a intuição: nas 180 detecções da
varredura do kc_02, **135 acontecem no nível 1** e 99 delas depois de um
único erro. Mas a cadeia `pointer_has_no_address` pergunta sobre
`sizeof p`, que só aparece em item de **nível 2**, e sobre `int **pp`,
que só aparece em item de **nível 3**. A pessoa cai na descida antes de
encontrar qualquer um dos dois.

"Está no material" era o critério errado. O certo tem duas partes, e a
segunda é a que este módulo guarda:

1. o recurso aparece no tópico; e
2. aparece em ENSINO, não só em avaliação — porque item de prova não
   autoriza o uso numa cadeia de recuperação.

A LISTA COMEÇA VAZIA, de propósito. Com ela vazia nenhuma cadeia roda, e
o sistema cai na refutação afirmativa em todo lugar — conservador do jeito
certo. A liberação é progressiva, uma entrada por vez, e cada uma carrega
a evidência de ONDE foi ensinada. Uma lista preenchida por suposição
mediria a suposição.

O QUE ESTE MÓDULO NÃO FAZ, e está na fila: distinguir, na resposta da
pessoa, "não conheço este recurso" de "continuo acreditando". Hoje as
duas viram o mesmo registro, e são diagnósticos opostos — um pede ensino,
o outro pede refutação.
"""
from __future__ import annotations

import pytest

from mvp import conceitos, motor
from mvp.dominio import carrega, topicos


# --------------------------------------------------------------------------
# O inventário: cada conceito diz quando entrou e com que evidência
# --------------------------------------------------------------------------

def test_o_inventario_carrega():
    assert isinstance(conceitos.carrega(), dict)


def test_todo_conceito_disponivel_tem_evidencia_de_ONDE():
    """A rastreabilidade é o que separa isto de uma lista de desejos.

    `disponivel` sem dizer onde foi ensinado é alguém afirmando que o
    curso cobre aquilo — que é exatamente a suposição que este portão
    existe para não fazer.
    """
    for cid, c in conceitos.carrega().items():
        if c["status"] != conceitos.DISPONIVEL:
            continue
        assert c.get("evidencia"), (cid, "disponível sem dizer onde")
        assert c.get("introduzido_em"), (cid, "disponível sem dizer quando")


def test_so_avaliado_nao_e_disponivel():
    """A distinção que a medição do kc_02 produziu: `sizeof` e `int **`
    aparecem no tópico, mas só em item de avaliação. Item de prova não
    autoriza o uso numa cadeia de recuperação."""
    assert conceitos.SO_AVALIADO != conceitos.DISPONIVEL
    for cid, c in conceitos.carrega().items():
        if c["status"] == conceitos.SO_AVALIADO:
            assert not conceitos.disponivel(cid), cid


def test_conceito_que_ninguem_declarou_nao_e_disponivel():
    """O padrão é NÃO. Um id que não está no inventário é desconhecido, e
    desconhecido não libera nada — senão errar o nome do conceito viraria
    autorização."""
    assert not conceitos.disponivel("conceito_que_nao_existe")
    assert conceitos.status("conceito_que_nao_existe") == conceitos.DESCONHECIDO


def test_os_quatro_estados_sao_os_quatro():
    assert set(conceitos.ESTADOS) == {
        conceitos.DISPONIVEL, conceitos.SO_AVALIADO,
        conceitos.NAO_INTRODUZIDO, conceitos.DESCONHECIDO}


# --------------------------------------------------------------------------
# O esquema do degrau: função pedagógica e requisitos declarados
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_todo_degrau_declara_a_funcao_pedagogica(topico):
    """Explicitar, confrontar ou reconstruir. Um degrau que não faz
    nenhuma das três provavelmente é dispensável — e declarar obriga a
    responder qual é antes de escrever."""
    d = carrega(topico=topico)
    for cid, de in d.descidas.items():
        for i, p in enumerate(de.passos, 1):
            assert p.funcao in conceitos.FUNCOES, (topico, cid, i, p.funcao)


@pytest.mark.parametrize("topico", topicos())
def test_a_ultima_pergunta_reconstroi(topico):
    """A cadeia não pode terminar na contradição.

    Confrontar sem reconstruir deixa a pessoa sabendo que a ideia dela
    não fecha e sem nenhuma no lugar — que é o estado em que uma crença
    volta, não o estado em que ela é trocada.
    """
    d = carrega(topico=topico)
    for cid, de in d.descidas.items():
        assert de.passos[-1].funcao == conceitos.RECONSTRUIR, (topico, cid)


@pytest.mark.parametrize("topico", topicos())
def test_toda_cadeia_confronta_em_algum_degrau(topico):
    """Só explicitar e reconstruir seria uma aula, não uma refutação."""
    d = carrega(topico=topico)
    for cid, de in d.descidas.items():
        assert any(p.funcao == conceitos.CONFRONTAR for p in de.passos), (
            topico, cid)


@pytest.mark.parametrize("topico", topicos())
def test_todo_degrau_declara_o_que_exige(topico):
    """Lista vazia é declaração válida — quer dizer "não exige recurso
    nenhum além do que o tópico ensina". O que não vale é o campo não
    existir, porque aí ninguém decidiu."""
    d = carrega(topico=topico)
    for cid, de in d.descidas.items():
        for i, p in enumerate(de.passos, 1):
            assert isinstance(p.requer, tuple), (topico, cid, i)


# --------------------------------------------------------------------------
# O PORTÃO: a cadeia bloqueada não é acionada
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_a_cadeia_com_requisito_indisponivel_fica_bloqueada(topico):
    """A regra, aplicada: se um degrau exige o que não está disponível, a
    cadeia inteira não roda."""
    d = carrega(topico=topico)
    for cid, de in d.descidas.items():
        falta = conceitos.faltando(de)
        assert de.liberada == (not falta), (topico, cid, falta)


def test_o_motor_nao_entrega_cadeia_bloqueada():
    """O portão tem de estar no caminho, e não só no relatório: uma
    cadeia bloqueada que ainda assim fosse entregue não seria portão."""
    d = carrega(topico="kc_02")
    for cid, de in d.descidas.items():
        if de.liberada:
            continue
        assert d.descida(cid) is None, cid


def test_bloquear_faz_cair_na_refutacao_afirmativa_e_nao_quebrar():
    """A degradação é a mesma que um tópico sem cadeia já tem. Nenhuma
    sessão pode morrer porque o inventário está vazio."""
    d = carrega(topico="kc_02")
    assert d.descida("crenca_inexistente") is None


def test_o_relatorio_diz_o_que_falta_para_cada_cadeia():
    """Bloqueio silencioso seria pior que bloqueio nenhum: com a lista
    vazia TUDO para, e quem lê precisa saber exatamente qual conceito
    liberar para destravar qual cadeia."""
    linhas = conceitos.relatorio(carrega(topico="kc_02"))
    assert len(linhas) == 6, linhas
    for linha in linhas:
        assert "crenca" in linha and "falta" in linha and "liberada" in linha


# --------------------------------------------------------------------------
# O PORTÃO, contra inventários montados de propósito
# --------------------------------------------------------------------------
#
# A fixture de `test_descida.py` cria um mundo artificial para exercitar o
# mecanismo. Estes testes existem para que esse mundo não vire liberação
# implícita: eles montam inventários e cobram o portão caso a caso.

def _inventario(tmp_path, **entradas):
    """Um inventário no disco, com os estados que o teste quiser."""
    linhas = ["conceitos:"]
    for cid, st in entradas.items():
        linhas += ["  %s:" % cid, "    status: %s" % st,
                   "    introduzido_em: teste", "    evidencia: teste"]
    p = tmp_path / "conceitos.yaml"
    p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return p


def _com(monkeypatch, caminho):
    monkeypatch.setenv("STRUCTURA_CONCEITOS", str(caminho))
    conceitos.recarrega()


@pytest.fixture(autouse=True)
def _restaura():
    yield
    conceitos.recarrega()


def test_inventario_vazio_bloqueia_as_seis(tmp_path, monkeypatch):
    _com(monkeypatch, _inventario(tmp_path))
    d = carrega(topico="kc_02")
    assert [c for c, de in d.descidas.items() if de.liberada] == []


def test_conceito_so_avaliado_nao_libera(tmp_path, monkeypatch):
    """`sizeof` e `int **` aparecem no kc_02 só em item de avaliação. Item
    de prova não autoriza o uso numa cadeia de recuperação."""
    _com(monkeypatch, _inventario(
        tmp_path, sizeof=conceitos.SO_AVALIADO,
        operador_endereco=conceitos.SO_AVALIADO,
        ponteiro_de_ponteiro=conceitos.SO_AVALIADO,
        endereco=conceitos.SO_AVALIADO))
    d = carrega(topico="kc_02")
    assert not d.descidas["pointer_has_no_address"].liberada


def test_conceito_nao_introduzido_bloqueia(tmp_path, monkeypatch):
    _com(monkeypatch, _inventario(
        tmp_path, funcao_com_parametro=conceitos.DISPONIVEL,
        operador_endereco=conceitos.DISPONIVEL,
        endereco=conceitos.DISPONIVEL, ponteiro=conceitos.DISPONIVEL,
        scanf=conceitos.NAO_INTRODUZIDO))
    d = carrega(topico="kc_02")
    de = d.descidas["pointer_is_pointless"]
    assert not de.liberada
    assert conceitos.faltando(de) == ("scanf",), conceitos.faltando(de)


def test_inventario_incompleto_nao_libera(tmp_path, monkeypatch):
    """Faltando UM conceito de UM degrau, a cadeia inteira fica parada.
    Liberar por maioria seria pôr a pessoa num degrau que ela não tem
    como responder, que é o defeito que o portão existe para impedir."""
    _com(monkeypatch, _inventario(
        tmp_path, funcao_com_parametro=conceitos.DISPONIVEL,
        scanf=conceitos.DISPONIVEL, operador_endereco=conceitos.DISPONIVEL,
        endereco=conceitos.DISPONIVEL))   # falta `ponteiro`
    d = carrega(topico="kc_02")
    de = d.descidas["pointer_is_pointless"]
    assert not de.liberada
    assert "ponteiro" in conceitos.faltando(de)


def test_inventario_completo_libera_SO_a_cadeia_autorizada(tmp_path, monkeypatch):
    """Liberar o que uma cadeia precisa não pode destravar as outras."""
    _com(monkeypatch, _inventario(
        tmp_path, funcao_com_parametro=conceitos.DISPONIVEL,
        scanf=conceitos.DISPONIVEL, operador_endereco=conceitos.DISPONIVEL,
        endereco=conceitos.DISPONIVEL, ponteiro=conceitos.DISPONIVEL))
    d = carrega(topico="kc_02")
    liberadas = sorted(c for c, de in d.descidas.items() if de.liberada)
    assert liberadas == ["pointer_is_pointless"], liberadas


# --------------------------------------------------------------------------
# INTEGRAÇÃO: o fluxo real, com o inventário de VERDADE
# --------------------------------------------------------------------------

def test_com_o_inventario_real_a_descida_nao_e_acionada(monkeypatch):
    """A decisão arquitetural, protegida de ponta a ponta.

    Percorre uma sessão inteira do kc_02 com a descida LIGADA e com o
    inventário de verdade. Nenhum evento de descida pode aparecer, e a
    refutação afirmativa tem de acontecer no lugar.

    Este teste não usa inventário de teste nenhum de propósito: é ele que
    garante que a fixture do `test_descida.py` não virou liberação
    implícita em algum lugar do caminho.

    DUAS VEZES ESTE TESTE PRECISOU SER REPENSADO, e as duas estão aqui
    porque a forma dele conta a história do portão.

    A primeira versão afirmava `inventario == {}` — atalho válido
    enquanto o inventário estava vazio, e letra errada depois da
    auditoria, que o encheu de 14 entradas sem liberar nada.

    A segunda afirmava que NENHUMA cadeia estava liberada, e caiu no dia
    em que a primeira foi — a `pointer_and_target_are_one`, depois de o
    cartão B3 passar a ensinar desreferência e o dono aprovar a
    liberação. Cair ali era o trabalho dela: liberação sem ninguém
    perceber é exatamente o que o portão existe para impedir.

    A terceira forma é a que resiste às duas: o conjunto liberado é
    EXATAMENTE o auditado. Liberar outra sem passar pela auditoria
    derruba este teste, e bloquear uma que já passou também.
    """
    conceitos.recarrega()
    monkeypatch.setattr(motor, "DESCIDA_LIGADA", True)
    d = carrega(topico="kc_02")

    # O CONJUNTO LIBERADO PELO INVENTARIO, que nao e o conjunto que roda.
    #
    # Era vazio ate 12/11/2026, e encheu em duas etapas no mesmo dia: o
    # `comparacao_de_ponteiros` abriu duas cadeias, e o
    # `ponteiro_de_ponteiro` -- com os seis materiais do kc_10 -- abriu
    # a terceira.
    #
    # E NENHUMA DAS DUAS RODA, que e o que o nome deste teste afirma.
    # `liberada` e so a primeira das duas autorizacoes; a segunda e
    # `aprovada`, da revisao pedagogica, e `Dominio.descida` exige as
    # duas. A `pointer_and_target_are_one` esta reprovada e a
    # `pointer_is_data` esta em revisao.
    #
    # A QUARTA FORMA DESTE TESTE, entao: o conjunto liberado e o medido,
    # E nenhuma cadeia liberada atravessa o segundo portao. A terceira
    # forma comparava liberado contra auditado como se fossem a mesma
    # pergunta, e hoje elas se separaram.
    liberadas_pelo_inventario = {"pointer_is_data",
                                 "pointer_and_target_are_one",
                                 "pointer_has_no_address"}
    liberadas = {c for c, de in d.descidas.items() if de.liberada}
    assert liberadas == liberadas_pelo_inventario, (
        "liberadas a mais: %s · fechadas que deveriam abrir: %s"
        % (sorted(liberadas - liberadas_pelo_inventario),
           sorted(liberadas_pelo_inventario - liberadas)))
    for c in liberadas:
        assert d.descida(c) is None, (
            "a cadeia %s atravessou os DOIS portoes: ela vai rodar" % c)

    def politica(tela, estado):
        if tela.tipo == "frase":
            return motor.Resposta(texto="x", ms=10)
        if tela.tipo == "confianca":
            return motor.Resposta(confianca="tenho certeza", ms=10)
        if tela.tipo in ("ensino", "validacao", "refutacao"):
            return motor.Resposta(ms=10)
        a = next((x for x in d.atividades
                  if x.id == tela.dados.get("atividade")), None)
        if a is None:
            return motor.Resposta(escolha=0, ms=10)
        na = motor.opcoes_na_tela(estado.semente, a)
        i = next((k for k, o in enumerate(na) if o.crenca),
                 next((k for k, o in enumerate(na) if not o.correta), 0))
        return motor.Resposta(escolha=i, ms=10)

    t = motor.inicia(d, semente="P01")
    eventos = list(t.eventos)
    for _ in range(400):
        if t.tela.tipo == "mapa":
            break
        t = motor.avanca(d, t.estado, politica(t.tela, t.estado))
        eventos += list(t.eventos)
    else:
        raise AssertionError("a unidade não terminou")
    tipos = [e.tipo for e in eventos]

    # A sessão tem de produzir refutação. Qual das duas — a afirmativa
    # ou a descida — depende de qual crença foi detectada, e isso varia
    # com a semente; o que não pode é não haver nenhuma.
    assert "refutacao_iniciada" in tipos or "descida_iniciada" in tipos, (
        "a sessão não refutou de jeito nenhum")

    # E TODA descida que aconteceu tem de ser de cadeia liberada.
    #
    # A conferência é pelo NÓ do evento, e não pelo tipo: o tipo é
    # sempre `descida_iniciada`, e comparar tipos não distinguiria uma
    # cadeia liberada de uma bloqueada. A primeira versão desta checagem
    # comparava contra uma string que nunca existe — passava sempre, e
    # não testava nada.
    por_no = {d.crencas[c].nega.split(":")[-1]: c for c in d.descidas}
    for ev in eventos:
        if ev.tipo != "descida_iniciada":
            continue
        cid = por_no.get(ev.dados.get("no"))
        assert cid and d.descidas[cid].liberada, (
            "desceu numa cadeia bloqueada: %s" % ev.dados)
