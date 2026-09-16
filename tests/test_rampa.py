"""A gradação das atividades: começar leve e subir devagar.

O problema que estes testes guardam foi encontrado USANDO o sistema, não
lendo o código: a primeira pergunta depois da introdução era de meio de
matéria, e a pessoa perdia a vontade de continuar antes de o mecanismo
ter qualquer chance de funcionar.

A causa era estrutural. Não havia noção de nível: a ordem de apresentação
era a ordem de declaração no YAML, e a primeira tela da sessão era
simplesmente a primeira atividade escrita.

O teste que mais importa é `test_toda_combinacao_de_resposta_sobe_devagar`.
O validador confere a gradação no papel; este confere na sessão, porque o
seletor põe a fronteira do conhecimento ANTES do nível, e uma resposta pode
mudar a fronteira. Ele percorre todas as combinações de resposta e afirma
que nenhuma embaralha os degraus.
"""

from __future__ import annotations

import itertools
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import session as S
from engine.loader import load
from tools import validate

MODOS = ("acerta", "erra_com_certeza", "chuta")


@pytest.fixture(scope="module")
def d():
    return load()


def copia(d, destino: Path) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    for f in d.source.glob("*.yaml"):
        shutil.copy(f, destino / f.name)
    return destino


def _responde(d, t, modo):
    ciu = d.cius[t.action.ciu_id]
    conf = "chutei" if modo == "chuta" else "tenho certeza"
    if ciu.is_choice:
        if modo == "acerta":
            idx = next(i for i, o in enumerate(ciu.options) if o.correct)
        else:
            erradas = [i for i, o in enumerate(ciu.options) if not o.correct]
            com_crenca = [i for i in erradas if ciu.options[i].misconception]
            idx = (com_crenca or erradas)[0]
        return S.advance(d, t.state, S.Answer(ciu.id, conf, 5000, option_idx=idx))
    texto = ciu.answer if modo == "acerta" else "nao sei"
    return S.advance(d, t.state, S.Answer(ciu.id, conf, 5000, text=texto))


def _niveis_apresentados(d, kc, combo):
    """Os níveis das atividades diagnósticas, NA ORDEM em que a sessão as
    mostrou, respondendo cada uma conforme `combo`."""
    t = S.start(d, "socratic", [kc])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(100))
    niveis = []
    for modo in combo:
        if t.action.kind != "ciu" or t.state.phase != S.DIAGNOSTICO:
            break
        niveis.append(d.cius[t.action.ciu_id].nivel)
        t = _responde(d, t, modo)
    return niveis


# --------------------------------------------------------------------------
# Na sessão
# --------------------------------------------------------------------------

def test_toda_combinacao_de_resposta_sobe_devagar(d):
    for kc in d.pilot_sequence:
        n = len(d.cius_of(kc, "diagnostic"))
        for combo in itertools.product(MODOS, repeat=n):
            niveis = _niveis_apresentados(d, kc, combo)
            motivo = validate.lacunas_de_degrau(niveis)
            assert motivo is None, "%s, respondendo %s: %s (%s)" % (
                kc, "/".join(combo[:len(niveis)]), motivo,
                "-".join(map(str, niveis)))


def test_a_primeira_atividade_da_sessao_e_de_nivel_1(d):
    """A primeira tela depois da introdução, que é a primeira impressão."""
    t = S.start(d, "socratic", list(d.pilot_sequence))
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(100))
    assert t.action.kind == "ciu"
    assert d.cius[t.action.ciu_id].nivel == 1, t.action.ciu_id


def test_os_dois_bracos_sobem_pelos_mesmos_degraus(d):
    """A ordem das atividades vem antes de os braços divergirem; se um dia
    ela depender do braço, o nível vira variável confundida."""
    for kc in d.pilot_sequence:
        def seq(arm):
            t = S.start(d, arm, [kc])
            while t.action.kind == "intro":
                t = S.advance(d, t.state, S.Acknowledge(100))
            ids = []
            while t.action.kind == "ciu" and t.state.phase == S.DIAGNOSTICO:
                ids.append(t.action.ciu_id)
                t = _responde(d, t, "acerta")
            return ids
        assert seq("socratic") == seq("direct"), kc


# --------------------------------------------------------------------------
# A guarda
# --------------------------------------------------------------------------

def test_o_dominio_do_piloto_e_gradual(d):
    assert validate.check_rampa(d) == []


def test_um_salto_de_degrau_e_detectado(d, tmp_path):
    """A guarda tem de PEGAR. Tira o degrau do meio do kc_11 e confere."""
    dominio = copia(d, tmp_path / "dom")
    alvo = dominio / "cius.yaml"
    texto = alvo.read_text(encoding="utf-8")
    antes = "  - id: ciu_kc11_007\n    kc: kc_11\n    nivel: 2\n"
    assert antes in texto
    alvo.write_text(texto.replace(antes, antes.replace("nivel: 2", "nivel: 3")),
                    encoding="utf-8")

    achados = validate.check_rampa(load(dominio))
    assert any("kc_11" in a and "pula" in a for a in achados), achados


def test_comecar_fora_do_nivel_1_e_detectado(d, tmp_path):
    dominio = copia(d, tmp_path / "dom")
    alvo = dominio / "cius.yaml"
    texto = alvo.read_text(encoding="utf-8")
    antes = "  - id: ciu_kc07_007\n    kc: kc_07\n    nivel: 1\n"
    assert antes in texto
    alvo.write_text(texto.replace(antes, antes.replace("nivel: 1", "nivel: 2")),
                    encoding="utf-8")

    achados = validate.check_rampa(load(dominio))
    assert any("kc_07" in a and "começa" in a for a in achados), achados


def test_nivel_fora_da_escala_e_recusado_na_carga(d, tmp_path):
    dominio = copia(d, tmp_path / "dom")
    alvo = dominio / "cius.yaml"
    texto = alvo.read_text(encoding="utf-8")
    antes = "  - id: ciu_kc07_007\n    kc: kc_07\n    nivel: 1\n"
    alvo.write_text(texto.replace(antes, antes.replace("nivel: 1", "nivel: 7")),
                    encoding="utf-8")
    with pytest.raises(Exception, match="fora da escala"):
        load(dominio)


def test_sem_nivel_declarado_vale_2(d, tmp_path):
    """Nem a mais fácil nem a mais difícil por acidente."""
    dominio = copia(d, tmp_path / "dom")
    alvo = dominio / "cius.yaml"
    texto = alvo.read_text(encoding="utf-8")
    antes = "  - id: ciu_kc07_001\n    kc: kc_07\n    nivel: 2\n"
    assert antes in texto
    alvo.write_text(texto.replace(antes, "  - id: ciu_kc07_001\n    kc: kc_07\n"),
                    encoding="utf-8")
    assert load(dominio).cius["ciu_kc07_001"].nivel == 2


# --------------------------------------------------------------------------
# A crença mostrada com certeza fica ativa até ser refutada
# --------------------------------------------------------------------------
#
# Consequência direta da gradação, e decisão do autor. A crença passou a
# aparecer na atividade de nível 1, e a de nível 2 que mira o mesmo nó vem
# depois. Se acertar a segunda confirmasse o nó, a evidência da primeira se
# apagaria e quem mostrou a crença COM CERTEZA sairia sem refutação.

def test_resposta_certa_nao_promove_no_errado(d):
    """No modelo: a resposta certa confirma os outros alvos, mas não o nó
    que uma crença marcou como errado."""
    from engine import model

    ciu = d.cius["ciu_kc09_001"]                     # mira I1 e I2
    assert set(ciu.targets) == {"I1", "I2"}
    vetor = {("kc_09", "I1"): model.WRONG}
    feitas = {(u.kc, u.node): u.state
              for u in model.ingest(d, vetor, ciu, True, "tenho certeza")}
    assert ("kc_09", "I1") not in feitas
    assert feitas[("kc_09", "I2")] == model.CONFIRMED


def test_acertar_depois_nao_apaga_a_crenca(d):
    """Na sessão: erra a de nível 1 com certeza, acerta todas as outras.
    A crença continua ativa e o nó que ela nega é percorrido."""
    from engine import model

    t = S.start(d, "socratic", ["kc_09"])
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(100))
    assert d.cius[t.action.ciu_id].nivel == 1
    t = _responde(d, t, "erra_com_certeza")

    negado = d.misconceptions["free_nullifies"].negates
    assert model.state_of(t.state.vector, *negado) == model.WRONG

    while t.action.kind == "ciu" and t.state.phase == S.DIAGNOSTICO:
        t = _responde(d, t, "acerta")
    assert model.state_of(t.state.vector, *negado) == model.WRONG, \
        "acertar a atividade de nível 2 apagou a crença"

    perguntados = set()
    for _ in range(400):
        a = t.action
        if a.kind == "done":
            break
        if a.kind in ("ask", "explain"):
            perguntados.add((a.kc, a.node))
            t = S.advance(d, t.state, S.StepAnswer(True, 10))
        elif a.kind == "ciu":
            t = _responde(d, t, "acerta")
        else:
            t = S.advance(d, t.state, S.Acknowledge(10))
    assert t.action.kind == "done"
    assert negado in perguntados, "a crença nunca foi refutada"


def test_toda_combinacao_fecha_e_refuta_o_que_mostrou(d):
    """O risco da regra: um nó errado que não pode mais ser apagado por
    resposta certa poderia ficar fora de todo percurso, e a sessão não
    fecharia. Aqui, para cada KC do piloto e cada combinação de resposta no
    diagnóstico, a sessão vai até o fim — e toda crença detectada tem o nó
    que ela nega percorrido."""
    for kc in d.pilot_sequence:
        n = len(d.cius_of(kc, "diagnostic"))
        for combo in itertools.product(MODOS, repeat=n):
            t = S.start(d, "socratic", [kc])
            fila = list(combo)
            crencas, perguntados = set(), set()
            for _ in range(600):
                for e in t.events:
                    if e.type == "misconception_detected":
                        crencas.add(e.payload["misconception_id"])
                a = t.action
                if a.kind == "done":
                    break
                if a.kind == "intro":
                    t = S.advance(d, t.state, S.Acknowledge(10))
                elif a.kind == "ciu":
                    diag = t.state.phase == S.DIAGNOSTICO
                    t = _responde(d, t, fila.pop(0) if (diag and fila) else "acerta")
                elif a.kind in ("ask", "explain"):
                    perguntados.add((a.kc, a.node))
                    t = S.advance(d, t.state, S.StepAnswer(True, 10))
                else:
                    t = S.advance(d, t.state, S.Acknowledge(10))
            onde = "%s respondendo %s" % (kc, "/".join(combo))
            assert t.action.kind == "done", "não fechou: " + onde
            for m in crencas:
                assert d.misconceptions[m].negates in perguntados, \
                    "%s detectada e não refutada: %s" % (m, onde)
