# -*- coding: utf-8 -*-
"""A versão 3 do log: separar desconhecimento de persistência na crença.

ESTES TESTES ESTÃO VERMELHOS DE PROPÓSITO. O dono pediu para ver os
testes e o esquema antes da implementação, e é isto. Nada do que eles
cobram existe ainda.

O PROBLEMA. Hoje a descida tem duas alternativas e um "não sei".
Escolher a alternativa da crença grava `escolha: "decorre"`, que quer
dizer "seguiu a crença, motivo desconhecido" — e o motivo pode ser
"continuo acreditando" ou "não conheço `sizeof`". São diagnósticos
OPOSTOS: um pede refutação, o outro pede ensino. O log não os separa, e
nenhum caminho indireto resolve: o banco de itens não é etiquetado por
recurso, então não dá para perguntar se a pessoa já demonstrou conhecer
aquilo.

POR QUE v3 E NÃO UM CAMPO NOVO. A regra do projeto: *a versão sobe
quando o significado de uma linha muda, não quando o código muda*. Hoje
`escolha: "decorre"` quer dizer "seguiu a crença, motivo desconhecido";
depois passa a querer dizer "seguiu a crença E NÃO declarou
desconhecer". Mesmo valor, outra leitura — que é exatamente o caso da
v2, quando um índice deixou de ser posição no arquivo e passou a ser
posição na tela.

                       O ESQUEMA DA v3

  descida_iniciada   ganha `cadeia`, `versao_cadeia` e `requer` de cada
                     degrau. A informação já existe no domínio desde a
                     fatia do portão e se perdia na hora de medir: quem
                     analisar passa a saber o que cada degrau EXIGIA,
                     não só o que a pessoa respondeu.

  descida_passo      `escolha: "decorre"` vira `declarado: "mantenho"`,
                     e ganha o `requer` daquele degrau.

  descida_fechou     ganha `declarado: "verdade"`.

  descida_sem_recurso   EVENTO NOVO. `declarado: "nao_conheco"`, com o
                     `requer` do degrau: a análise vê os candidatos do
                     que ela diz não conhecer.

  descida_sem_resposta  continua, com `declarado: "nao_sei"`.

DECLARADO NÃO É DIAGNÓSTICO, e o log não guarda diagnóstico nenhum.
Dizer "não conheço" é dado, não prova: a pessoa pode estar enganada
sobre si mesma nas duas direções. O campo se chama `declarado` por isso,
e a inferência fica com quem analisa, depois de confrontar com o
desempenho posterior.

TRÊS RESPOSTAS, E NÃO QUATRO. "Conheço mas não sei aplicar" ficou de
fora: exige que a pessoa distinga, sobre si mesma, reconhecer de
aplicar — e essa é a metacognição que o instrumento tenta medir. Pedir
que ela a reporte produziria o dado mais ruidoso dos quatro.
"""
from __future__ import annotations

import json

import pytest

from mvp import log, motor
from mvp.dominio import carrega


@pytest.fixture(scope="module", autouse=True)
def mundo_de_teste(tmp_path_factory):
    """UM MUNDO ARTIFICIAL, so para este arquivo.

    Estes testes exercitam o REGISTRO da descida — que evento sai, com
    que campos — e nao medem disponibilidade curricular nem aprovacao
    pedagogica. Sem declarar as duas, `Dominio.descida()` nao entrega
    cadeia nenhuma e o handler nem e alcancado.

    Nada daqui e evidencia de que a disciplina ensinou nada, nem de que
    alguem revisou a cadeia. As duas respostas reais ficam em
    `conceitos.yaml` e `aprovacoes.yaml`, e hoje nao liberam nada.
    """
    from mvp import aprovacao, conceitos

    pasta = tmp_path_factory.mktemp("mundo")
    cs = ["conceitos:"]
    for c in ("array", "ponteiro", "sizeof", "atribuicao_entre_tipos",
              "compilacao"):
        cs += ["  %s:" % c, "    status: disponivel",
               "    introduzido_em: teste", "    evidencia: mundo de teste"]
    pc = pasta / "conceitos.yaml"
    pc.write_text("\n".join(cs) + "\n", encoding="utf-8")

    ap = ["aprovacoes:", "  array_is_pointer:", "    status: aprovada",
          "    em: teste", "    por: fixture de mvp/test_v3.py",
          "    nota: mundo de teste — NAO e revisao pedagogica"]
    pa = pasta / "aprovacoes.yaml"
    pa.write_text("\n".join(ap) + "\n", encoding="utf-8")

    mp = pytest.MonkeyPatch()
    mp.setenv("STRUCTURA_CONCEITOS", str(pc))
    mp.setenv("STRUCTURA_APROVACOES", str(pa))
    conceitos.recarrega(); aprovacao.recarrega()
    yield
    mp.undo()
    conceitos.recarrega(); aprovacao.recarrega()


@pytest.fixture(scope="module")
def d(mundo_de_teste):
    return carrega(topico="kc_07")


def _escreve(caminho, sessao, v, linhas):
    with caminho.open("w", encoding="utf-8") as f:
        for ln in linhas:
            f.write(json.dumps(dict(ln, v=v, sessao=sessao,
                                    ts="2026-11-05T12:00:00+00:00"),
                               ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# A VERSÃO SOBE, E A v2 PASSA A SER RECUSADA
# --------------------------------------------------------------------------

def test_a_versao_do_log_e_3():
    assert log.VERSAO == 3


def test_sessao_v2_e_recusada_para_reexecucao(d, tmp_path):
    """Mesma recusa que a v1 recebeu, pelo mesmo motivo.

    Reexecutar uma sessão v2 com o motor de hoje leria
    `escolha: "decorre"` como "manteve a crença e não declarou
    desconhecer" — uma afirmação que aquela sessão não tem como
    sustentar, porque na v2 não havia como declarar.
    """
    caminho = tmp_path / "v2.jsonl"
    _escreve(caminho, "S2", 2, [
        {"tipo": "unidade_iniciada", "topico": d.id},
        {"tipo": "entrada_recebida", "escolha": 0, "ms": 100},
    ])
    with pytest.raises(log.LogIncompleto) as erro:
        log.reconstroi(d, "S2", caminho)
    assert "2" in str(erro.value) and "3" in str(erro.value), str(erro.value)


def test_a_recusa_diz_que_o_log_continua_LEGIVEL(d, tmp_path):
    """Recusar reexecução não é recusar o dado. A mensagem da v2 já
    dizia isso, e a da v3 tem de dizer igual: quem for analisar as
    sessões antigas continua podendo."""
    caminho = tmp_path / "v2.jsonl"
    _escreve(caminho, "S2", 2, [{"tipo": "unidade_iniciada", "topico": d.id}])
    with pytest.raises(log.LogIncompleto) as erro:
        log.reconstroi(d, "S2", caminho)
    assert "legível" in str(erro.value) or "legivel" in str(erro.value)


def test_os_arquivos_historicos_nao_foram_tocados():
    """Condição do dono: preservar os arquivos. Subir a versão não apaga
    nem reescreve nada — as sessões de ensaio continuam onde estavam."""
    import pathlib

    pasta = pathlib.Path(__file__).resolve().parent.parent / "ensaios"
    if not pasta.exists():
        pytest.skip("sem pasta de ensaios nesta máquina")
    for f in pasta.glob("*.jsonl"):
        primeira = f.read_text(encoding="utf-8").splitlines()[:1]
        if not primeira:
            continue
        assert json.loads(primeira[0]).get("v") in (1, 2, 3, None), f.name


# --------------------------------------------------------------------------
# O QUE O `descida_iniciada` PASSA A GRAVAR
# --------------------------------------------------------------------------

def _inicia_descida(d, cid):
    no = d.crencas[cid].nega.split(":")[-1]
    e = motor.inicia(d, semente="P01").estado.com(no, crenca=cid)
    return motor._inicia_descida(d, e, no, d.descidas[cid])


def test_a_descida_iniciada_grava_os_requisitos_de_cada_degrau(d):
    """A informação existe no domínio desde a fatia do portão e se
    perdia na hora de medir. Sem ela, a análise sabe o que a pessoa
    respondeu e não sabe o que lhe foi exigido."""
    t = _inicia_descida(d, "array_is_pointer")
    ev = next(x for x in t.eventos if x.tipo == "descida_iniciada")
    de = d.descidas["array_is_pointer"]
    assert ev.dados["requer"] == [list(p.requer) for p in de.passos]


def test_a_descida_iniciada_identifica_a_cadeia_e_a_versao_dela(d):
    """`versao_cadeia` é derivada do conteúdo, e não escrita à mão: um
    número que alguém precisa lembrar de subir é um número que fica
    para trás. Mudou o texto de um degrau, muda o resumo."""
    t = _inicia_descida(d, "array_is_pointer")
    ev = next(x for x in t.eventos if x.tipo == "descida_iniciada")
    assert ev.dados["cadeia"] == "array_is_pointer"
    assert len(ev.dados["versao_cadeia"]) >= 8
    assert ev.dados["versao_cadeia"] == motor.versao_da_cadeia(
        d.descidas["array_is_pointer"])


def test_mudar_um_degrau_muda_a_versao_da_cadeia(d):
    """A trava do teste acima: se o resumo não mudar quando o texto
    mudar, ele não identifica nada."""
    de = d.descidas["array_is_pointer"]
    antes = motor.versao_da_cadeia(de)
    outro = motor.replace(de, passos=de.passos[:-1])
    assert motor.versao_da_cadeia(outro) != antes


# --------------------------------------------------------------------------
# OS TRÊS CAMINHOS DE RESPOSTA
# --------------------------------------------------------------------------

def _responde(d, cid, **resposta):
    t = _inicia_descida(d, cid)
    return motor.avanca(d, t.estado, motor.Resposta(**resposta))


def test_manter_a_crenca_grava_declarado_mantenho(d):
    """Era `escolha: "decorre"`. O nome muda porque o significado muda:
    agora quer dizer "seguiu a crença E NÃO declarou desconhecer"."""
    t = _responde(d, "array_is_pointer", escolha=0, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "descida_passo")
    assert ev.dados["declarado"] == "mantenho"
    assert "escolha" not in ev.dados, "o campo velho ficou para trás"
    assert ev.dados["requer"] == list(
        d.descidas["array_is_pointer"].passos[0].requer)


def test_contradizer_a_propria_crenca_grava_declarado_verdade(d):
    t = _responde(d, "array_is_pointer", escolha=1, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "descida_fechou")
    assert ev.dados["declarado"] == "verdade"


def test_declarar_que_NAO_CONHECE_grava_evento_proprio(d):
    """O caminho novo, e a razão desta fatia.

    Tipo próprio e não um valor a mais em `descida_sem_resposta`: as
    duas declarações pedem ações OPOSTAS — uma pede ensino, a outra
    pede investigação — e o projeto usa tipo distinto para significado
    distinto.
    """
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "descida_sem_recurso")
    assert ev.dados["declarado"] == "nao_conheco"
    # os candidatos do que ela diz nao conhecer
    assert ev.dados["requer"] == list(
        d.descidas["array_is_pointer"].passos[0].requer)


def test_declarar_que_NAO_SABE_continua_sendo_outro_evento(d):
    t = _responde(d, "array_is_pointer", nao_sei=True, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "descida_sem_resposta")
    assert ev.dados["declarado"] == "nao_sei"


def test_os_tres_caminhos_produzem_eventos_DIFERENTES(d):
    """Se dois deles caíssem no mesmo evento, a fatia não teria feito
    nada."""
    tipos = set()
    for resposta in ({"escolha": 0}, {"nao_conheco": True}, {"nao_sei": True}):
        t = _responde(d, "array_is_pointer", ms=100, **resposta)
        tipos |= {x.tipo for x in t.eventos if x.tipo.startswith("descida_")}
    assert len(tipos) >= 3, tipos


# --------------------------------------------------------------------------
# DECLARADO NÃO É DIAGNÓSTICO
# --------------------------------------------------------------------------

def test_o_log_nao_grava_diagnostico_nenhum(d):
    """Condição do dono: separar resposta declarada de diagnóstico
    inferido.

    Dizer "não conheço" é dado, não prova — a pessoa pode estar enganada
    sobre si mesma nas duas direções. Um campo `diagnostico` no log
    transformaria a autodeclaração em conclusão, e a conclusão viajaria
    para a análise sem ninguém a ter conferido.
    """
    for resposta in ({"escolha": 0}, {"nao_conheco": True}, {"nao_sei": True}):
        t = _responde(d, "array_is_pointer", ms=100, **resposta)
        for ev in t.eventos:
            for proibido in ("diagnostico", "persistencia", "desconhecimento"):
                assert proibido not in ev.dados, (ev.tipo, proibido)


def test_nao_conheco_nao_encerra_a_crenca_como_refutada(d):
    """Quem diz não conhecer o recurso não refutou nada, e não manteve
    nada. O nó não pode sair dali com a crença dada como tratada."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    no = d.crencas["array_is_pointer"].nega.split(":")[-1]
    assert t.estado.no(no).estado != motor.CONFIRMADO


# --------------------------------------------------------------------------
# DESCONHECIMENTO DECLARADO INTERROMPE — nao avanca, nao fecha, nao refuta
# --------------------------------------------------------------------------
#
# O PRINCIPIO, do dono:
#
#   Quando o participante declara desconhecer um recurso exigido, o
#   sistema nao pode interpretar a ausencia de resposta como
#   persistencia da crenca. Deve reconhecer a lacuna de oportunidade de
#   aprendizagem e criar condicoes para uma demonstracao posterior.
#
# Os testes abaixo cobram as quatro coisas que `nao_conheco` NAO pode
# produzir, e a unica que ele tem de produzir.

def test_nao_conheco_NAO_fecha_a_cadeia(d):
    """Fechar e o que acontece quando a pessoa contradiz a propria
    crenca. Quem diz nao conhecer o recurso nao contradisse nada."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    tipos = {x.tipo for x in t.eventos}
    assert "descida_fechou" not in tipos, tipos
    assert "descida_sustentada" not in tipos, tipos


def test_nao_conheco_NAO_refuta_a_crenca(d):
    """E nem a deixa como tratada: a crenca continua de pe, por falta de
    medida e nao por teimosia."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    no = d.crencas["array_is_pointer"].nega.split(":")[-1]
    assert t.estado.no(no).estado not in (motor.CONFIRMADO, motor.REFUTADO)
    assert "refutacao_concluida" not in {x.tipo for x in t.eventos}


def test_nao_conheco_NAO_avanca_a_profundidade(d):
    """Avancar contaria o degrau como percorrido. Nao foi: a pessoa
    parou nele porque nao tinha como responder."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "descida_sem_recurso")
    assert ev.dados["profundidade"] == 1
    assert t.estado.passo == 0, t.estado.passo


def test_nao_conheco_NAO_registra_persistencia(d):
    """O evento de manter a crenca nao pode sair junto. Se saisse, a
    analise contaria a mesma resposta como as duas coisas."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    assert "descida_passo" not in {x.tipo for x in t.eventos}


def test_nao_conheco_LEVA_A_UMA_OPORTUNIDADE_DE_APRENDER(d):
    """A unica coisa que ele TEM de produzir.

    Interromper sem oferecer nada deixaria a pessoa parada numa pergunta
    que ela disse nao ter como responder. A tela seguinte e de ENSINO —
    nao o proximo degrau, e nao a evidencia, que e o que o "nao sei"
    recebe.
    """
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    assert t.tela.tipo == "ensino", t.tela.tipo


def test_nao_sei_e_nao_conheco_vao_para_lugares_DIFERENTES(d):
    """A diferenca de tratamento e a fatia inteira: um pede
    investigacao e recebe o fato; o outro pede ensino e recebe ensino.
    Se fossem para o mesmo lugar, separar os eventos nao teria
    servido para nada."""
    sem_recurso = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    sem_resposta = _responde(d, "array_is_pointer", nao_sei=True, ms=100)
    assert sem_recurso.tela.tipo != sem_resposta.tela.tipo


def test_o_evento_diz_qual_degrau_e_qual_cadeia(d):
    """Contexto do degrau interrompido, para quem for analisar depois."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "descida_sem_recurso")
    for campo in ("no", "crenca", "cadeia", "versao_cadeia",
                  "profundidade", "total", "requer", "declarado"):
        assert campo in ev.dados, (campo, sorted(ev.dados))


# --------------------------------------------------------------------------
# A VERSAO DA CADEIA OLHA A ESTRUTURA, e nao so os textos
# --------------------------------------------------------------------------

def test_mudar_o_REQUER_de_um_degrau_muda_a_versao(d):
    """Ressalva do dono. Duas cadeias com o mesmo texto e requisitos
    diferentes sao cadeias diferentes para a analise: uma rodou com um
    conceito exigido que a outra nao exigia."""
    de = d.descidas["array_is_pointer"]
    antes = motor.versao_da_cadeia(de)
    p0 = motor.replace(de.passos[0], requer=de.passos[0].requer + ("novo",))
    outro = motor.replace(de, passos=(p0,) + de.passos[1:])
    assert motor.versao_da_cadeia(outro) != antes


def test_mudar_a_FUNCAO_de_um_degrau_muda_a_versao(d):
    de = d.descidas["array_is_pointer"]
    antes = motor.versao_da_cadeia(de)
    p0 = motor.replace(de.passos[0], funcao="reconstruir")
    outro = motor.replace(de, passos=(p0,) + de.passos[1:])
    assert motor.versao_da_cadeia(outro) != antes


def test_mudar_a_COLISAO_muda_a_versao(d):
    de = d.descidas["array_is_pointer"]
    antes = motor.versao_da_cadeia(de)
    assert motor.versao_da_cadeia(motor.replace(de, colide_com="B2")) != antes


# --------------------------------------------------------------------------
# O HISTORICO CONTINUA INTERPRETAVEL, sem reclassificacao
# --------------------------------------------------------------------------

def test_o_log_v2_continua_LEGIVEL_para_analise(d, tmp_path):
    """Recusar reexecucao nao e recusar o dado. As linhas antigas
    continuam sendo lidas como estao, e `escolha: "decorre"` continua
    querendo dizer o que queria dizer na v2 — sem virar `declarado`."""
    caminho = tmp_path / "v2.jsonl"
    _escreve(caminho, "S2", 2, [
        {"tipo": "unidade_iniciada", "topico": d.id},
        {"tipo": "descida_passo", "no": "I3", "crenca": "array_is_pointer",
         "profundidade": 1, "total": 4, "escolha": "decorre", "ms": 100},
    ])
    linhas, _ = log.le_tolerante(caminho)
    passo = next(l for l in linhas if l.get("tipo") == "descida_passo")
    assert passo["escolha"] == "decorre"
    assert "declarado" not in passo, "a leitura reclassificou a linha antiga"


# --------------------------------------------------------------------------
# A CADEIA E ABANDONADA, e nao retomada
# --------------------------------------------------------------------------
#
# A DECISAO, do dono, e a medicao que a sustenta: em 6 das 7 cadeias
# ZERO conceitos sao comuns a todos os degraus, e declarar
# desconhecimento no degrau 1 deixa de 2 a 5 conceitos NOVOS adiante.
# Uma demonstracao devolveria a pessoa a um degrau, nao a cadeia — e o
# caminho de volta pediria ate cinco ciclos de ensino-e-demonstracao
# dentro de uma refutacao, num sistema que tem teto em tudo.
#
# Entao: declara, registra, ABANDONA aquela cadeia naquela sessao,
# ensina, e o laco comum assume — com o reteste de transferencia que ja
# existe e ja foi medido.
#
# TRES INFORMACOES SEPARADAS, e elas nao sao a mesma coisa:
#
#   declarado: nao_conheco   o RELATO do participante
#   cadeia_abandonada        a DECISAO OPERACIONAL do motor
#   resultado do reteste     a EVIDENCIA posterior
#
# Nao existe `conceito_desconhecido: true` em lugar nenhum: a pessoa
# declarou, e o sistema nao provou.

def test_o_abandono_e_evento_PROPRIO_e_nao_o_relato(d):
    """A decisao do motor e o relato da pessoa sao registros
    diferentes. Misturar os dois faria a decisao operacional herdar a
    autoridade de um relato que ninguem conferiu."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    tipos = [x.tipo for x in t.eventos]
    assert "descida_sem_recurso" in tipos, tipos
    assert "cadeia_abandonada" in tipos, tipos
    ev = next(x for x in t.eventos if x.tipo == "cadeia_abandonada")
    assert ev.dados["motivo"] == "desconhecimento_declarado"
    assert ev.dados["cadeia"] == "array_is_pointer"


def test_o_abandono_NAO_e_erro_nem_desistencia(d):
    """Condicao do dono. Quem diz nao conhecer um recurso nao errou nada
    e nao desistiu de nada — e se o log chamar isso de erro, a analise
    conta como resistencia o que foi falta de oportunidade."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    for ev in t.eventos:
        junto = " ".join(str(v) for v in ev.dados.values()).lower()
        for palavra in ("erro", "errou", "desistiu", "desistencia",
                        "abandonou", "resistencia"):
            assert palavra not in junto, (ev.tipo, palavra, ev.dados)


def test_a_analise_consegue_ver_que_a_crenca_SAIU_DA_AMOSTRA(d):
    """O ponto que o dono chamou de mais importante para a validade.

    Quem declara desconhecimento nao pode simplesmente sumir dos
    resultados: tem de aparecer numa categoria propria — excluida da
    analise de recuperacao interrogativa por ausencia DECLARADA de
    oportunidade de aprendizagem.
    """
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    ev = next(x for x in t.eventos if x.tipo == "cadeia_abandonada")
    for campo in ("cadeia", "crenca", "no", "versao_cadeia",
                  "profundidade", "requer", "motivo"):
        assert campo in ev.dados, (campo, sorted(ev.dados))


def test_a_cadeia_NAO_retoma_depois_do_ensino(d):
    """Depois do ensino, o fluxo comum assume. A descida nao volta nem
    se a pessoa demonstrar o conceito logo em seguida."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    assert t.tela.tipo == "ensino"
    # segue o ensino: o que vem e construcao, nao degrau de descida
    t = motor.avanca(d, t.estado, motor.Resposta(ms=100))
    assert t.tela.tipo != "descida", t.tela.tipo
    assert "descida_iniciada" not in {x.tipo for x in t.eventos}


def test_a_MESMA_crenca_nao_recebe_segunda_descida_na_sessao(d):
    """Mesmo que a crenca seja detectada de novo adiante. Abandonar e
    para a sessao, nao para o momento — senao a pessoa cairia na mesma
    pergunta que ela ja disse nao ter como responder."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    no = d.crencas["array_is_pointer"].nega.split(":")[-1]
    assert t.estado.no(no).descida_abandonada is True
    # e uma nova deteccao da mesma crenca nao reabre a descida
    e2 = motor.replace(t.estado, alvo=no)
    t2 = motor._segue_validacao(d, e2)
    assert t2.tela.tipo != "descida", t2.tela.tipo
    assert t2.tela.tipo == "refutacao", "nem descida nem refutacao afirmativa"


def test_o_ensino_NAO_conta_como_refutacao(d):
    """O ensino que vem depois do abandono e oportunidade de aprender,
    nao refutacao da crenca. Conta-lo como refutacao inflaria a medida
    central do trabalho com episodios que nao refutaram nada."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    tipos = {x.tipo for x in t.eventos}
    assert "refutacao_iniciada" not in tipos, tipos
    assert "refutacao_concluida" not in tipos, tipos


def test_o_reteste_continua_sendo_do_fluxo_comum(d):
    """Abandonar a descida nao tira o no do laco: o reteste de
    transferencia continua acontecendo, e e ele que traz a evidencia
    posterior de aprendizagem."""
    t = _responde(d, "array_is_pointer", nao_conheco=True, ms=100)
    no = d.crencas["array_is_pointer"].nega.split(":")[-1]
    # a crenca continua registrada no no, para o laco comum trabalhar
    assert t.estado.no(no).crenca == "array_is_pointer"
    assert t.estado.no(no).estado != motor.CONFIRMADO


def test_o_separador_da_versao_IMPEDE_colisao_por_concatenacao(d):
    """A sabotagem que faltava, cobrada pela regra do dono: guarda novo
    tem de ser testado contra o caso que ele deveria detectar.

    Sem separador entre os campos, duas cadeias DIFERENTES cujos textos
    concatenados dao a mesma sequencia produziriam o mesmo resumo — e a
    analise leria duas estruturas pedagogicas distintas como se fossem
    a mesma. O caso abaixo e exatamente esse: "ab"+"c" e "a"+"bc".
    """
    de = d.descidas["array_is_pointer"]
    p0, p1 = de.passos[0], de.passos[1]

    uma = motor.replace(de, passos=(
        motor.replace(p0, pergunta="ab", decorre="c"), p1))
    outra = motor.replace(de, passos=(
        motor.replace(p0, pergunta="a", decorre="bc"), p1))

    assert motor.versao_da_cadeia(uma) != motor.versao_da_cadeia(outra), (
        "o resumo nao separa os campos: duas cadeias diferentes "
        "produziram a mesma versao")


def test_o_separador_nao_aparece_em_texto_de_tela(d):
    """E a outra metade: se o separador PUDESSE aparecer num texto, ele
    nao separaria nada. 0x1F nao e digitavel e nao esta em texto nenhum
    do dominio — ha guarda de bytes de controle no fonte, e aqui o
    mesmo para o conteudo."""
    sep = chr(31)
    for cid, de in d.descidas.items():
        for i, p in enumerate(de.passos, 1):
            for campo in (p.pergunta, p.decorre, p.verdade, p.porque):
                assert sep not in campo, (cid, i)
