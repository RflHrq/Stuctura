# -*- coding: utf-8 -*-
"""A aprovação por cadeia, separada da disponibilidade do conceito.

O PRINCÍPIO, decidido pelo dono:

    A disponibilidade de um conceito autoriza seu uso potencial. Não
    autoriza, por si só, a utilização de qualquer cadeia que o contenha.

A MEDIÇÃO QUE O OBRIGOU. Com `comparacao_de_ponteiros` ainda bloqueado,
simulei liberá-lo: **duas** cadeias passariam a `liberada=True` de uma
vez — `pointer_and_target_are_one` e `pointer_is_data`. E a primeira
reprova em três das cinco perguntas da revisão pedagógica, incluindo
o degrau de abertura, que exige declaração múltipla e reatribuição de
ponteiro, nenhuma das duas ensinada.

Uma decisão CURRICULAR (este conceito foi ensinado?) estava decidindo
uma questão PEDAGÓGICA (esta sequência confronta a crença?). São
perguntas diferentes, com evidências diferentes e aprovadores
diferentes.

AS DUAS AUTORIZAÇÕES, e o motor exige as duas:

    liberada   todo conceito que a cadeia exige está ensinado
    aprovada   aquela cadeia específica passou na revisão pedagógica

POR QUE O ARQUIVO É SEPARADO do das cadeias: quem escreve a cadeia não
pode ser a mesma instância que a certifica. O autor declara `requer`;
o aprovador escreve em `aprovacoes.yaml`. Misturar os dois no mesmo
arquivo convida a escrever os dois na mesma passada.
"""
from __future__ import annotations

import pathlib

import pytest

from mvp import aprovacao, conceitos, motor
from mvp.dominio import carrega, topicos


@pytest.fixture(autouse=True)
def _restaura():
    yield
    conceitos.recarrega()
    aprovacao.recarrega()


def _arquivo(tmp_path, **cadeias):
    linhas = ["aprovacoes:"]
    for cid, st in cadeias.items():
        linhas += ["  %s:" % cid, "    status: %s" % st,
                   "    em: 2026-11-05", "    por: teste",
                   "    nota: mundo de teste"]
    p = tmp_path / "aprovacoes.yaml"
    p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return p


def _tudo_disponivel(tmp_path):
    """Um inventário que libera tudo, para isolar a OUTRA dimensão."""
    ids = sorted(conceitos.carrega())
    linhas = ["conceitos:"]
    for c in ids:
        linhas += ["  %s:" % c, "    status: disponivel",
                   "    introduzido_em: teste", "    evidencia: teste"]
    p = tmp_path / "conceitos.yaml"
    p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return p


# --------------------------------------------------------------------------
# Os estados, e o padrão é NÃO
# --------------------------------------------------------------------------

def test_os_estados_sao_os_quatro():
    assert set(aprovacao.ESTADOS) == {
        aprovacao.APROVADA, aprovacao.EM_REVISAO,
        aprovacao.REPROVADA, aprovacao.SEM_REVISAO}


def test_cadeia_que_ninguem_revisou_nao_esta_aprovada():
    """O padrão é NÃO, como no inventário: cadeia nova nasce bloqueada,
    e esquecer de revisar não vira autorização."""
    assert not aprovacao.aprovada("cadeia_que_nao_existe")
    assert aprovacao.status("cadeia_que_nao_existe") == aprovacao.SEM_REVISAO


@pytest.mark.parametrize("estado", ["em_revisao", "reprovada", "sem_revisao"])
def test_so_aprovada_autoriza(tmp_path, monkeypatch, estado):
    monkeypatch.setenv("STRUCTURA_APROVACOES",
                       str(_arquivo(tmp_path, alguma=estado)))
    aprovacao.recarrega()
    assert not aprovacao.aprovada("alguma"), estado


def test_aprovada_exige_dizer_quem_e_quando():
    """Rastreabilidade, igual à do inventário: aprovação sem autor e sem
    data é alguém afirmando que revisou."""
    for cid, a in aprovacao.carrega().items():
        if a["status"] != aprovacao.APROVADA:
            continue
        assert a.get("por"), (cid, "aprovada sem dizer por quem")
        assert a.get("em"), (cid, "aprovada sem dizer quando")


def test_reprovada_exige_dizer_o_motivo():
    """Reprovar sem motivo não ajuda quem vai consertar, e perde a razão
    assim que a memória da conversa some."""
    for cid, a in aprovacao.carrega().items():
        if a["status"] == aprovacao.REPROVADA:
            assert a.get("nota"), (cid, "reprovada sem motivo")


# --------------------------------------------------------------------------
# AS DUAS AUTORIZAÇÕES SÃO INDEPENDENTES
# --------------------------------------------------------------------------

def test_conceito_disponivel_nao_aprova_cadeia(tmp_path, monkeypatch):
    """O princípio, em um teste.

    Com TODO conceito disponível e nenhuma cadeia aprovada, o motor não
    entrega nenhuma: a decisão curricular não decide a pedagógica.
    """
    monkeypatch.setenv("STRUCTURA_CONCEITOS", str(_tudo_disponivel(tmp_path)))
    monkeypatch.setenv("STRUCTURA_APROVACOES", str(_arquivo(tmp_path)))
    conceitos.recarrega(); aprovacao.recarrega()
    d = carrega(topico="kc_02")
    assert all(de.liberada for de in d.descidas.values()), "o inventário não abriu"
    assert [c for c in d.descidas if d.descida(c)] == []


def test_cadeia_aprovada_sem_conceito_tambem_nao_roda(tmp_path, monkeypatch):
    """A outra metade: aprovar a pedagogia não inventa o ensino.

    A CADEIA DE EXEMPLO É ESCOLHIDA EM TEMPO DE EXECUÇÃO, e não está
    escrita aqui. Era a `pointer_is_data`, e em 11/11/2026 ela passou a
    `liberada` — o `comparacao_de_ponteiros` que lhe faltava foi
    promovido quando o inventário parou de negar o que o cartão do B1
    ensina. O teste caiu por uma razão que não é a dele: o nome tinha
    virado parte do contrato sem precisar ser.

    O que ele cobra é a REGRA, e a regra precisa de uma cadeia que
    ainda não esteja liberada. Se um dia nenhuma estiver, o `skip` diz
    isso em vez de passar calado — teste vazio que passa é pior que
    teste que não roda.
    """
    d0 = carrega(topico="kc_02")
    alvo = next((c for c, de_ in sorted(d0.descidas.items())
                 if not de_.liberada), None)
    if alvo is None:
        pytest.skip("toda cadeia do kc_02 está liberada — a regra ficou "
                    "sem caso, e é preciso escolher outro tópico")
    monkeypatch.setenv("STRUCTURA_APROVACOES", str(_arquivo(
        tmp_path, **{alvo: aprovacao.APROVADA})))
    aprovacao.recarrega()
    d = carrega(topico="kc_02")
    assert not d.descidas[alvo].liberada, alvo
    assert d.descida(alvo) is None, alvo


def test_APROVAR_UMA_NAO_APROVA_A_OUTRA(tmp_path, monkeypatch):
    """O item que motivou esta fatia.

    As duas cadeias exigiam `comparacao_de_ponteiros` e mais nada que
    faltasse: liberar aquele conceito abriria AS DUAS de uma vez, e uma
    delas reprova em três das cinco perguntas da revisão.

    E FOI O QUE ACONTECEU em 11/11/2026 — o conceito foi promovido, e as
    duas ficaram `liberada=True` no mesmo instante. Nenhuma das duas
    roda, e quem as segura agora é só o portão pedagógico. É o caso que
    esta fatia existia para antecipar, acontecido.
    """
    monkeypatch.setenv("STRUCTURA_CONCEITOS", str(_tudo_disponivel(tmp_path)))
    monkeypatch.setenv("STRUCTURA_APROVACOES", str(_arquivo(
        tmp_path,
        pointer_is_data=aprovacao.APROVADA,
        pointer_and_target_are_one=aprovacao.REPROVADA)))
    conceitos.recarrega(); aprovacao.recarrega()
    d = carrega(topico="kc_02")

    assert d.descida("pointer_is_data") is not None
    assert d.descida("pointer_and_target_are_one") is None
    # e as outras quatro, que ninguém revisou, continuam fora
    rodando = sorted(c for c in d.descidas if d.descida(c))
    assert rodando == ["pointer_is_data"], rodando


# --------------------------------------------------------------------------
# O estado de hoje: nenhuma das duas autorizada
# --------------------------------------------------------------------------

def test_hoje_nenhuma_cadeia_esta_aprovada():
    """Durante esta fatia as duas ficam sem liberação, por decisão do
    dono. A `pointer_is_data` está `em_revisao` e a
    `pointer_and_target_are_one` está `reprovada`, com motivo."""
    inv = aprovacao.carrega()
    assert inv["pointer_is_data"]["status"] == aprovacao.EM_REVISAO
    assert inv["pointer_and_target_are_one"]["status"] == aprovacao.REPROVADA
    assert not any(aprovacao.aprovada(c) for c in inv)


@pytest.mark.parametrize("topico", topicos())
def test_o_motor_nao_entrega_cadeia_nenhuma_hoje(topico):
    d = carrega(topico=topico)
    assert [c for c in d.descidas if d.descida(c)] == []


def test_o_relatorio_mostra_as_DUAS_dimensoes():
    """Quem lê precisa saber qual das duas autorizações falta — são
    consertos diferentes, com aprovadores diferentes."""
    linhas = aprovacao.relatorio(carrega(topico="kc_02"))
    assert len(linhas) == 6, linhas
    for linha in linhas:
        assert "liberada" in linha and "aprovada" in linha, linha
