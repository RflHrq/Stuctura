"""Cobertura do diagnóstico: o sistema só encontra o que pergunta.

Havia 20 atividades escritas na fase `traversal`, que a máquina de estados
nunca apresentava — o percurso é feito de passos montados do grafo, não de
atividades. Na prática eram diagnósticas guardadas numa gaveta: de 34
crenças do domínio, só 23 chegavam a ser perguntadas. Quem entrasse
achando que `sizeof(p)` mede o array saía do KC 07 sem que ninguém tivesse
perguntado isso.

Elas entraram no diagnóstico. Como o KC apresenta no máximo
`max_diagnostics_per_kc` atividades, o pool passou a ser maior do que o que
cabe numa sessão — e isso é de propósito: o seletor escolhe, e escolhe pela
LARGURA, preferindo a atividade que oferece uma crença ainda não
perguntada. Sem essa regra, as três atividades de um KC podiam cair todas
na mesma ideia errada.

Com o pool maior apareceu um buraco que o teto de nível fecha: a fronteira
do conhecimento vem antes do nível na escolha, e uma atividade difícil que
toca a fronteira passava na frente da fácil que não tocava — o KC pulava do
nível 1 para o 3. O piso diz de onde o aluno parte; o teto diz que ele sobe
um degrau por vez.
"""

from __future__ import annotations

import sys

from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import model, selector
from engine import session as S
from engine.loader import CIU_PHASES, load


@pytest.fixture(scope="module")
def d():
    return load()


def _diagnosticas_do_kc(d, kc, arm="socratic"):
    """Os ids apresentados no KC a quem acerta sem certeza (vê o KC inteiro)."""
    t = S.start(d, arm, [kc])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    ids = []
    while t.action.kind == "ciu" and t.state.phase == S.DIAGNOSTICO:
        c = d.cius[t.action.ciu_id]
        ids.append(c.id)
        if c.is_choice:
            idx = next(i for i, o in enumerate(c.options) if o.correct)
            t = S.advance(d, t.state, S.Answer(c.id, "acho que sei", 10, option_idx=idx))
        else:
            t = S.advance(d, t.state, S.Answer(c.id, "acho que sei", 10, text=c.answer))
    return ids


# --------------------------------------------------------------------------
# A gaveta fechou
# --------------------------------------------------------------------------

def test_toda_crenca_do_dominio_pode_ser_perguntada(d):
    """Uma crença que nenhuma atividade oferece é uma crença que o sistema
    nunca vai encontrar, por mais bem descrita que esteja no YAML."""
    oferecidas = set()
    for c in d.cius.values():
        if c.phase == "diagnostic":
            oferecidas |= selector.beliefs_of(c)
    faltando = sorted(set(d.misconceptions) - oferecidas)
    assert faltando == [], \
        "crenças sem atividade diagnóstica que as ofereça: %s" % faltando


def test_a_fase_traversal_nao_existe_mais(d, tmp_path):
    assert "traversal" not in CIU_PHASES
    assert all(c.phase in CIU_PHASES for c in d.cius.values())

    destino = tmp_path / "dom"
    destino.mkdir()
    for f in d.source.glob("*.yaml"):
        (destino / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    alvo = destino / "cius.yaml"
    texto = alvo.read_text(encoding="utf-8")
    alvo.write_text(texto.replace("    phase: diagnostic\n",
                                  "    phase: traversal\n", 1), encoding="utf-8")
    with pytest.raises(Exception, match="phase inválida"):
        load(destino)


# --------------------------------------------------------------------------
# Largura: o KC não gasta as três atividades na mesma ideia
# --------------------------------------------------------------------------

def test_o_kc_pergunta_crencas_diferentes(d):
    for kc in d.pilot_sequence:
        ids = _diagnosticas_do_kc(d, kc)
        crencas = [selector.beliefs_of(d.cius[i]) for i in ids]
        com_crenca = [c for c in crencas if c]
        disponiveis = {m for c in d.cius_of(kc, "diagnostic")
                       for m in selector.beliefs_of(c)}
        # Repetir só é aceitável quando o KC não tem crenças suficientes.
        esperado = min(len(com_crenca), len(disponiveis))
        assert len({frozenset(c) for c in com_crenca}) == esperado, \
            "%s repetiu crença tendo %d disponíveis: %s" % (kc, len(disponiveis), ids)


def test_a_largura_prefere_crenca_nova(d):
    """Unitário: com duas candidatas do mesmo nível, ganha a que traz crença
    que a sessão ainda não ofereceu."""
    kc = "kc_07"
    vazio: dict = {}
    primeira = selector.next_diagnostic(d, vazio, kc)
    assert primeira is not None
    ja = selector.beliefs_of(primeira)
    segunda = selector.next_diagnostic(d, vazio, kc, used=[primeira.id])
    assert segunda is not None
    assert selector.beliefs_of(segunda) - ja, \
        "a segunda atividade do KC repetiu a crença da primeira (%s)" % segunda.id


# --------------------------------------------------------------------------
# Teto: um degrau por vez
# --------------------------------------------------------------------------

def test_sem_teto_o_kc_pularia_degrau(d):
    """A guarda tem de PEGAR: é o caso real que apareceu quando o pool
    cresceu. Procura, nos KCs do piloto, um estado em que o seletor SEM teto
    saltaria um degrau, e afirma que com teto ele não salta."""
    achou = []
    for kc in d.pilot_sequence:
        vetor: dict = {}
        usadas: list[str] = []
        ultimo = 0
        for _ in range(len(d.cius_of(kc, "diagnostic"))):
            sem = selector.next_diagnostic(d, vetor, kc, used=usadas)
            if sem is None:
                break
            com = selector.next_diagnostic(d, vetor, kc, used=usadas,
                                           nivel_maximo=ultimo + 1)
            if sem.nivel > ultimo + 1:
                achou.append((kc, ultimo, sem.id, sem.nivel, com.id, com.nivel))
                assert com.nivel <= ultimo + 1, (
                    "%s: o teto deixou passar %s (nível %d)"
                    % (kc, com.id, com.nivel))
            escolhida = com
            usadas.append(escolhida.id)
            ultimo = max(ultimo, escolhida.nivel)
            vetor = model.apply(vetor, model.ingest(d, vetor, escolhida, True,
                                                    "acho que sei", None))
    assert achou, "nenhum KC tenta saltar degrau: este teste não guarda mais nada"


def test_o_teto_nao_impede_o_desafio_de_abrir_mais_alto(d):
    """Piso e teto são coisas diferentes: quem chega desafiado ENTRA no
    nível 2, e o teto não o puxa de volta para o 1."""
    kc = "kc_07"
    c = selector.next_diagnostic(d, {}, kc, nivel_minimo=2, nivel_maximo=2)
    assert c is not None and c.nivel == 2, c


def test_o_teto_cede_quando_so_sobrou_atividade_alta(d):
    """Melhor saltar um degrau do que deixar o KC sem atividade nenhuma."""
    kc = "kc_09"
    altas = [c.id for c in d.cius_of(kc, "diagnostic") if c.nivel <= 2]
    resta = selector.next_diagnostic(d, {}, kc, used=altas, nivel_maximo=1)
    assert resta is not None and resta.nivel == 3, resta


def test_o_teto_zera_a_cada_kc(d):
    """Subir ao nível 3 num KC não faz o seguinte começar por cima — quem
    manda na entrada do KC é o piso do desafio, não o degrau que já foi."""
    t = S.start(d, "socratic", list(d.pilot_sequence))
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(10))
    vistos = []
    for _ in range(3000):
        a = t.action
        if a.kind == "done":
            break
        if a.kind == "ciu":
            c = d.cius[a.ciu_id]
            if c.phase == "diagnostic":
                vistos.append((c.kc, c.nivel, t.state.nivel_visto))
            # hesitante: o piso fica no 1 e o teto é o único limitador
            if c.is_choice:
                idx = next(i for i, o in enumerate(c.options) if o.correct)
                t = S.advance(d, t.state, S.Answer(c.id, "acho que sei", 10, option_idx=idx))
            else:
                t = S.advance(d, t.state, S.Answer(c.id, "acho que sei", 10, text=c.answer))
        elif a.kind == "probe":
            t = S.advance(d, t.state, S.Answer("", "", 10, option_idx=0))
        elif a.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 10))
        else:
            t = S.advance(d, t.state, S.Acknowledge(10))
    primeiro_de_cada_kc = {}
    for kc, nivel, _ in vistos:
        primeiro_de_cada_kc.setdefault(kc, nivel)
    assert set(primeiro_de_cada_kc.values()) == {1}, primeiro_de_cada_kc
