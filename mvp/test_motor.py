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
              confianca="tenho certeza", so_a_resposta=False, d=D):
    """Acerta tudo, menos no nó pedido.

    `erra_diagnostico`: quantas atividades de diagnóstico daquele nó errar.
    `erra_treino`: quantas tentativas de treino daquele nó errar.
    `so_a_resposta`: erra a camada 1 mas acerta a razão — o escorregão, que
    desde a T4 é o que o sistema NÃO contesta.
    """
    feitos = {"diagnostico": 0, "treino": 0}
    ultimo = {"errou": False, "crenca": None}

    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()

        # Teach-back (T9): a mesma pergunta no começo e no fim.
        if tela.tipo == "frase":
            return Resposta(texto="uma frase de " + tela.dados["momento"])

        # Camada 3 (T3): tela própria, em toda atividade.
        if tela.tipo == "confianca":
            return Resposta(confianca=confianca)

        # Camada 2 (T2): escolhe a razão COERENTE com a resposta que acabou
        # de dar — quem errou de propósito explica pela crença daquela
        # alternativa. Sem isso, a política erraria a camada 1 e acertaria a
        # camada 2, que é um caso diferente (falso negativo) e tem teste
        # próprio.
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            if not ultimo["errou"] or so_a_resposta:
                return Resposta(escolha=next(i for i, z in enumerate(razoes)
                                             if z.correta))
            i = next((i for i, z in enumerate(razoes)
                      if z.crenca and z.crenca == ultimo["crenca"]), None)
            if i is None:
                i = next(i for i, z in enumerate(razoes) if not z.correta)
            return Resposta(escolha=i)

        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        treino = tela.dados["fase"] == motor.TREINO
        chave = "treino" if treino else "diagnostico"
        limite = erra_treino if treino else erra_diagnostico
        if a.no == erra_no and feitos[chave] < limite:
            feitos[chave] += 1
            i = _errada(a)
            ultimo.update(errou=True, crenca=a.opcoes[i].crenca)
            return Resposta(escolha=i, confianca=confianca)
        ultimo.update(errou=False, crenca=None)
        return Resposta(escolha=a.indice_correto_no_arquivo, confianca=confianca)

    return politica


def _tipos(eventos):
    return [e.tipo for e in eventos]


def _dos(eventos, tipo, no=None):
    return [e.dados for e in eventos
            if e.tipo == tipo and (no is None or e.dados.get("no") == no)]


# --------------------------------------------------------------------------
# Um erro isolado é vacilo, não crença
# --------------------------------------------------------------------------

# APOSENTADOS NA T4 — `test_errar_uma_vez_leva_a_segunda_pergunta_do_no...`
# e `test_errar_as_duas_perguntas_do_no_dispara_a_refutacao`.
#
# Os dois afirmavam a regra dos DOIS ERROS: um erro isolado era "vacilo até
# prova em contrário", e o sistema fazia uma segunda pergunta do mesmo nó
# para decidir. Essa regra existia porque não havia como saber POR QUE a
# pessoa errou — o segundo erro era um proxy.
#
# A camada 2 substituiu o proxy pela coisa. Quem erra pelo motivo certo
# escorregou; quem erra pelo motivo errado, com confiança, nomeou a própria
# crença, e não há o que descobrir numa segunda pergunta. A intenção dos
# dois sobrevive, mais forte, em `test_classificacao.py`:
#
#   um erro isolado não refuta  ->  test_cs3_errar_pela_razao_certa_nao_dispara_refutacao
#   o erro com crença refuta    ->  test_cs2_a_crenca_vai_para_o_no_que_ela_nega_e_so_para_ele


def test_a_segunda_pergunta_e_de_outro_formato(d):
    """O par teórica + código existe para isso: a segunda checagem não pode
    ser o mesmo molde da primeira.

    Até a T3 o par sustentava a checagem de vacilo. Desde a T4 ele sustenta
    CS-5: confirmar exige duas superfícies DIFERENTES, e é esse par que as
    fornece. A asserção é a mesma; o roteiro que a alcança é que mudou —
    quem erra agora é refutado no primeiro item, e a segunda pergunta não
    chega a aparecer."""
    t, eventos = roda(d, _politica())
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
# "Ainda não entendi": a premissa volta, com a analogia
# --------------------------------------------------------------------------

def _ate_a_refutacao(d, no="B3"):
    """Erra as duas perguntas do nó e passa da validação."""
    t = motor.inicia(d)
    pol = _politica(erra_no=no, erra_diagnostico=2)
    for _ in range(40):
        if t.tela.tipo == "refutacao":
            return t
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    raise AssertionError("não chegou à refutação")


def test_pedir_de_novo_repete_a_premissa_com_a_analogia(d):
    t = _ate_a_refutacao(d)
    premissa = t.tela.no
    assert not t.tela.dados["reexplicacao"], "a analogia apareceu sem ser pedida"

    t2 = motor.avanca(d, t.estado, Resposta(repetir=True))
    assert t2.tela.no == premissa, "o percurso andou em vez de repetir"
    assert t2.tela.dados["reexplicacao"] == d.resgate(premissa)
    assert [e.tipo for e in t2.eventos] == ["premissa_reapresentada"]
    assert t2.eventos[0].dados["vez"] == 1


def test_o_percurso_nao_anda_enquanto_ele_pede_de_novo(d):
    t = _ate_a_refutacao(d)
    passo = t.tela.dados["passo"]
    for vez in (1, 2):
        t = motor.avanca(d, t.estado, Resposta(repetir=True))
        assert t.tela.dados["passo"] == passo
        assert t.tela.dados["repeticoes"] == vez


def test_depois_do_limite_o_percurso_segue_e_o_log_diz(d):
    t = _ate_a_refutacao(d)
    for _ in range(motor.LIMITE_REEXPLICACAO):
        t = motor.avanca(d, t.estado, Resposta(repetir=True))
    assert t.tela.dados["pode_repetir"] is False

    t = motor.avanca(d, t.estado, Resposta(repetir=True))
    tipos = [e.tipo for e in t.eventos]
    assert "premissa_nao_fechou" in tipos, tipos
    assert t.tela.tipo != "refutacao" or t.tela.dados["passo"] > 1,         "insistiu numa quarta vez na mesma premissa"


def test_a_contagem_de_reexplicacao_zera_a_cada_premissa(d):
    """Pedir de novo numa premissa não gasta a cota da seguinte."""
    t = _ate_a_refutacao(d, no="I1")        # percurso de cinco passos
    t = motor.avanca(d, t.estado, Resposta(repetir=True))
    assert t.tela.dados["repeticoes"] == 1
    t = motor.avanca(d, t.estado, Resposta())      # entendeu, segue
    assert t.tela.dados["passo"] == 2
    assert t.tela.dados["repeticoes"] == 0
    assert t.tela.dados["pode_repetir"] is True


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
    """A regra de formato precisa valer mesmo quando há item inédito.

    Monta um terceiro item de treino, do MESMO formato do que acabou de
    aparecer, e põe-no na frente da fila. Sem a regra de formato o seletor
    pegaria esse; com ela, pula para o de formato diferente.
    """
    treino = d.atividades_do_no("B2", "treino")
    assert len({a.formato for a in treino}) >= 2, "o cenário do teste mudou"
    repetido, outro = treino[1], treino[0]
    extra = replace(repetido, id="a_b2_extra")
    tres = replace(d, atividades=(extra,) + d.atividades)

    e = motor.Estado().com("B2", estado=motor.EM_TREINO,
                           usadas=(repetido.id,),
                           ultima_atividade=repetido.id,
                           ultimo_formato=repetido.formato)
    escolhido, _ = motor.proximo_item(tres, e, "B2")
    assert escolhido is not None
    assert escolhido.formato != repetido.formato,         "o seletor pegou o item inédito do mesmo formato (%s)" % escolhido.id
    assert escolhido.id == outro.id


def test_o_treino_tem_banco_proprio(d):
    """A sequência de acertos não é feita das perguntas que o aluno acabou
    de responder: isso seria reapresentar a pergunta logo depois de ela ter
    sido discutida, e provaria pouco."""
    t, eventos = roda(d, _politica(erra_no="B2", erra_diagnostico=2))
    usados = [x["atividade"] for x in _dos(eventos, "treino_tentativa", "B2")]
    do_treino = {a.id for a in d.atividades_do_no("B2", "treino")}
    assert usados, "não houve treino"
    assert set(usados) <= do_treino, usados
    assert not _dos(eventos, "item_reapresentado", "B2")


def test_o_treino_prefere_o_banco_proprio_a_uma_diagnostica_inedita(d):
    """Se a segunda pergunta do diagnóstico não chegou a ser usada, ela
    continua sendo pergunta de diagnóstico: o treino não a toma emprestada
    enquanto tiver item próprio."""
    diag = d.atividades_do_no("B2", "diagnostico")
    e = motor.Estado().com("B2", estado=motor.EM_TREINO,
                           usadas=(diag[0].id,),
                           ultima_atividade=diag[0].id,
                           ultimo_formato=diag[0].formato)
    escolhido, reapresentada = motor.proximo_item(d, e, "B2")
    assert escolhido is not None and not reapresentada
    assert escolhido.uso == "treino", escolhido.id


def test_esgotado_o_banco_de_treino_o_item_volta_e_fica_registrado(d):
    """Melhor repetir um item do que deixar o nó sem como fechar — mas a
    reapresentação tem de aparecer no log."""
    t, eventos = roda(d, _politica(erra_no="B2", erra_diagnostico=2, erra_treino=99))
    tentativas = _dos(eventos, "treino_tentativa", "B2")
    assert len(tentativas) > len(d.atividades_do_no("B2", "treino")),         "o teto parou antes de o banco de treino acabar"
    assert _dos(eventos, "item_reapresentado", "B2")


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
    """Três caminhos até o verde, e o mapa guarda qual foi.

    O do meio mudou de nome na T4. Era "errou e corrigiu sozinho na
    pergunta seguinte"; agora é o **escorregão**: errou a resposta e
    acertou a razão, no mesmo item. É a mesma distinção — chegar ao verde
    tropeçando não é a mesma coisa que chegar direto — medida de um jeito
    que não precisa de uma segunda pergunta para ser descoberta.
    """
    direto, _ = roda(d, _politica())
    assert all(not n["via_treino"] and not n["vacilou"]
               for n in direto.tela.dados["nos"])

    vacilo, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=1,
                                  so_a_resposta=True))
    b3 = next(n for n in vacilo.tela.dados["nos"] if n["no"] == "B3")
    assert b3["vacilou"] is True and b3["via_treino"] is False

    treino, _ = roda(d, _politica(erra_no="B3", erra_diagnostico=1))
    b3 = next(n for n in treino.tela.dados["nos"] if n["no"] == "B3")
    assert b3["via_treino"] is True and b3["crenca"] == "declaration_zeroes"


def test_o_streak_nao_escreve_no_reteste_da_pesquisa(d):
    """O streak é mecanismo de PRODUTO: decide o que o mapa mostra ao
    aluno. O reteste é medida de PESQUISA. Misturar os dois faria o treino
    virar uma segunda forma de medir correção de crença.

    Até a T12 este teste dizia isso do jeito mais curto possível —
    `belief_retested` não aparecia em lugar nenhum, porque o reteste ainda
    não existia. Agora ele existe, e vem da fase RETESTE, depois de tudo.
    A asserção passou a ser a afirmação de verdade: entre o início do
    treino e o fim da sequência, nada escreve na medida.
    """
    t, eventos = roda(d, _politica(erra_no="B4", erra_diagnostico=2))
    tipos = _tipos(eventos)
    assert "training_streak_completed" in tipos
    durante_o_treino = tipos[tipos.index("treino_iniciado"):
                             tipos.index("training_streak_completed") + 1]
    assert "belief_retested" not in durante_o_treino
    # E o reteste acontece — depois, e uma vez só.
    assert tipos.count("belief_retested") == 1
    assert tipos.index("belief_retested") > tipos.index("training_streak_completed")


# --------------------------------------------------------------------------
# A procedência no log: de que molde veio o item respondido
# --------------------------------------------------------------------------

def test_o_log_diz_de_que_molde_veio_o_item(tmp_path):
    """Sem isto, nada do resto é mensurável.

    Generalizar e decorar só se distinguem se o log disser QUAL variação
    foi apresentada — o id do item não basta, porque duas variações do
    mesmo molde são a mesma pergunta com a roupa trocada.
    """
    from mvp.test_dominio import atividade, monta

    def muda(cru):
        atividade(cru, "ciu_kc00_001").update(
            do_molde="mol_teste", parametros={"tipo": "int", "n": 5})
    d2 = carrega(monta(tmp_path / "log1", muda))
    t, eventos = roda(d2, _politica(d=d2))

    de_molde = [x for x in _dos(eventos, "atividade_apresentada")
                if x.get("do_molde")]
    assert de_molde, "o item de molde não deixou rastro no log"
    assert de_molde[0]["do_molde"] == "mol_teste"
    assert de_molde[0]["parametros"] == {"tipo": "int", "n": 5}


def test_item_escrito_a_mao_nao_polui_o_log(d):
    """O log dos 556 itens de hoje não muda: campo vazio não entra.

    Um campo vazio em toda linha é ruído que a análise precisa aprender a
    ignorar, e um log que muda de forma sem mudar de conteúdo estraga a
    comparação com as sessões já gravadas.
    """
    t, eventos = roda(d, _politica())
    for x in _dos(eventos, "atividade_apresentada"):
        assert "do_molde" not in x and "parametros" not in x


# --------------------------------------------------------------------------
# Generalizar e decorar: a mesma ideia com a roupa trocada
# --------------------------------------------------------------------------

def test_acertar_um_item_de_molde_guarda_a_instancia(tmp_path):
    """A assinatura traz os PARÂMETROS, não só o id do molde.

    Sem eles, dois acertos na mesma variação ficam indistinguíveis de dois
    acertos em variações diferentes — que é exatamente o que separa
    generalizar de decorar.
    """
    from mvp.test_dominio import atividade, monta

    def muda(cru):
        atividade(cru, "ciu_kc00_001").update(
            do_molde="mol_teste", parametros={"tipo": "int", "n": 5})
    d2 = carrega(monta(tmp_path / "g1", muda))
    alvo = next(x for x in d2.atividades if x.id == "ciu_kc00_001").no
    t, eventos = roda(d2, _politica(d=d2))
    assert "mol_teste|n=5,tipo=int" in t.estado.no(alvo).instancias


def test_duas_instancias_do_mesmo_molde_e_generalizar(d):
    e = motor.Estado(nos={"B1": motor.EstadoNo(
        instancias=("mol_x|n=3", "mol_x|n=8"))})
    b1 = next(n for n in motor.estado_dos_nos(d, e) if n["no"] == "B1")
    assert b1["generalizou"] is True


def test_a_mesma_instancia_duas_vezes_nao_e_generalizar(d):
    """Repetir a mesma pergunta mede memória, não generalização."""
    e = motor.Estado(nos={"B1": motor.EstadoNo(
        instancias=("mol_x|n=3", "mol_x|n=3"))})
    b1 = next(n for n in motor.estado_dos_nos(d, e) if n["no"] == "B1")
    assert b1["generalizou"] is False


def test_duas_instancias_de_moldes_diferentes_nao_e_generalizar(d):
    """A troca de superfície é DENTRO do molde: moldes diferentes são
    perguntas diferentes, e isso o critério de hoje já mede."""
    e = motor.Estado(nos={"B1": motor.EstadoNo(
        instancias=("mol_x|n=3", "mol_y|n=8"))})
    b1 = next(n for n in motor.estado_dos_nos(d, e) if n["no"] == "B1")
    assert b1["generalizou"] is False


def test_no_sem_item_de_molde_nunca_generaliza(d):
    """Os 556 itens de hoje não têm molde: a marca fica falsa, não some."""
    t, eventos = roda(d, _politica())
    assert all(n["generalizou"] is False
               for n in motor.estado_dos_nos(d, t.estado))


def test_acertar_no_treino_tambem_guarda_a_instancia(tmp_path):
    """O caminho que a coleta vai usar de verdade, e que não contava.

    A decisão da spec é que os moldes começam pelos itens de TREINO — é
    lá que o banco esgota. Mas a instância só era somada nos dois ramos
    de acerto do DIAGNÓSTICO, e `atividades_do_no(no, "diagnostico")`
    garante que item de treino nunca chega lá. Resultado: para o corpus
    que o plano constrói, `generalizou` era um falso constante.
    """
    from mvp.test_dominio import atividade, monta

    def muda(cru):
        for aid, params in (("ciu_kc00_t01", {"tipo": "int", "n": 3}),
                            ("ciu_kc00_t02", {"tipo": "char", "n": 8})):
            atividade(cru, aid).update(do_molde="mol_t", parametros=params)
    d2 = carrega(monta(tmp_path / "tr1", muda))
    alvo = next(x for x in d2.atividades if x.id == "ciu_kc00_t01").no

    # erra o diagnóstico daquele nó para cair no treino, e acerta o treino
    t, eventos = roda(d2, _politica(erra_no=alvo, erra_diagnostico=2, d=d2))

    assinaturas = set(t.estado.no(alvo).instancias)
    assert assinaturas >= {"mol_t|n=3,tipo=int", "mol_t|n=8,tipo=char"}, \
        t.estado.no(alvo).instancias
    marca = next(n for n in motor.estado_dos_nos(d2, t.estado)
                 if n["no"] == alvo)
    assert marca["generalizou"] is True
