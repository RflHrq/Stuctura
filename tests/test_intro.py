"""A introdução apresentada antes da primeira atividade.

O teste que mais importa é `test_a_introducao_nao_ensina_o_que_o_piloto_mede`.
A introdução existe para orientar; se ela ensinar a conclusão de um KC do
recorte, o diagnóstico deixa de medir a crença PRÉVIA do aluno — que é o
desfecho primário do estudo. É contaminação, e é silenciosa.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import session as S
from engine.loader import load
from tools import validate


@pytest.fixture(scope="module")
def d():
    return load()


def copia_dominio(d, destino: Path) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    for f in d.source.glob("*.yaml"):
        shutil.copy(f, destino / f.name)
    return destino


# --------------------------------------------------------------------------
# Escopo: o que a introdução pode e não pode dizer
# --------------------------------------------------------------------------

def test_a_introducao_nao_ensina_o_que_o_piloto_mede(d):
    assert validate.check_intro_scope(d) == []


def test_contaminacao_e_detectada(d, tmp_path):
    """A guarda tem de PEGAR. Um teste que não falha quando deveria não vale."""
    copia = copia_dominio(d, tmp_path / "dominio")
    alvo = copia / "intro.yaml"
    alvo.write_text(
        alvo.read_text(encoding="utf-8").replace(
            "Guarde só isto:",
            "Lembre que array e ponteiro sao tipos distintos. Guarde só isto:"),
        encoding="utf-8")

    achados = validate.check_intro_scope(load(copia))
    assert achados, "a introdução ensinou a resposta e ninguém reclamou"
    assert "kc_07" in achados[0]


def test_a_introducao_estabelece_o_vocabulario_que_pode(d):
    """Endereço, caixa e região são prerequisitos FORA do recorte: podem —
    e precisam — ser estabelecidos, senão o aluno começa sem vocabulário."""
    texto = " ".join(c.title + " " + c.lead + " " + " ".join(c.body)
                     for c in d.intro).lower()
    # radicais, não palavras inteiras: "regiões" e "região" contam igual, e
    # a verificação é sobre o vocabulário existir, não sobre a flexão.
    for radical in ("endereç", "caixa", "regi"):
        assert radical in texto, radical


# --------------------------------------------------------------------------
# Fluxo
# --------------------------------------------------------------------------

def test_a_sessao_comeca_pela_introducao(d):
    t = S.start(d, "socratic", ["kc_09"])
    assert t.action.kind == "intro"
    assert t.action.data["index"] == 1
    assert t.action.data["total"] == len(d.intro)
    assert t.events == (), "apresentar não gera evento; confirmar é que gera"


def test_a_introducao_entrega_no_diagnostico(d):
    t = S.start(d, "socratic", ["kc_09"])
    vistos = []
    for _ in range(len(d.intro) + 2):
        if t.action.kind != "intro":
            break
        vistos.append(t.action.data["id"])
        t = S.advance(d, t.state, S.Acknowledge(700))
    assert vistos == [c.id for c in d.intro]
    assert t.action.kind == "ciu"
    assert t.state.phase == S.DIAGNOSTICO


def test_cada_cartao_registra_o_tempo_de_leitura(d):
    t = S.start(d, "socratic", ["kc_09"])
    eventos = []
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(1500))
        eventos.extend(t.events)

    intro = [e for e in eventos if e.payload.get("stage") == "intro"]
    assert len(intro) == len(d.intro)
    assert [e.payload["card"] for e in intro] == [c.id for c in d.intro]
    assert all(e.payload["elapsed_ms"] == 1500 for e in intro)


def test_os_dois_bracos_veem_a_mesma_introducao(d):
    """§8.1: ela vem ANTES de os braços divergirem, então a simetria é
    estrutural — mas afirmar é barato e o dia em que deixar de valer é o
    dia em que a introdução vira variável confundida."""
    def cartoes(arm):
        t = S.start(d, arm, ["kc_09"])
        out = []
        while t.action.kind == "intro":
            out.append((t.action.data["id"], t.action.text,
                        tuple(t.action.data["body"])))
            t = S.advance(d, t.state, S.Acknowledge(100))
        return out
    assert cartoes("socratic") == cartoes("direct")


def test_evento_do_tipo_errado_na_introducao_falha_alto(d):
    t = S.start(d, "socratic", ["kc_09"])
    with pytest.raises(ValueError, match="INTRO espera Acknowledge"):
        S.advance(d, t.state, S.StepAnswer(True, 0))


def test_a_retomada_volta_ao_mesmo_cartao(d):
    """RNF06 vale desde o primeiro cartão: fechar a aba na orientação não
    pode devolver o aluno ao começo."""
    t = S.start(d, "socratic", ["kc_09"])
    for _ in range(2):
        t = S.advance(d, t.state, S.Acknowledge(500))
    esperado = t.action.data["id"]

    # replay das mesmas entradas, como faz api/service.load_session
    r = S.start(d, "socratic", ["kc_09"])
    for _ in range(2):
        r = S.advance(d, r.state, S.Acknowledge(500))
    assert r.action.data["id"] == esperado
    assert r.state.intro_index == t.state.intro_index


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------

def test_todo_cartao_tem_id_titulo_e_figura(d):
    ids = [c.id for c in d.intro]
    assert len(ids) == len(set(ids)) > 0
    for c in d.intro:
        assert c.id and c.title and c.lead
        assert c.figure and c.figure.get("kind"), c.id


def test_as_figuras_usam_tipos_que_o_renderizador_conhece(d):
    """Os tipos vivem em web/intro.js. Um `kind` desconhecido renderiza
    NADA e o cartão fica sem a ilustração, em silêncio."""
    conhecidos = set()
    fonte = (Path(__file__).resolve().parent.parent / "web" / "intro.js").read_text(
        encoding="utf-8")
    bloco = fonte[fonte.index("var TIPOS = {"):fonte.index("};", fonte.index("var TIPOS = {"))]
    for linha in bloco.splitlines()[1:]:
        nome = linha.strip().split(":")[0].strip()
        if nome:
            conhecidos.add(nome)

    for c in d.intro:
        assert c.figure["kind"] in conhecidos, \
            "%s usa figura %r, que web/intro.js não desenha" % (c.id, c.figure["kind"])


def test_dominio_sem_introducao_ainda_sobe(d, tmp_path):
    """A introdução é orientação, não requisito. Faltar não derruba coleta."""
    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        if f.name != "intro.yaml":
            shutil.copy(f, copia / f.name)
    sem = load(copia)
    assert sem.intro == ()
    assert S.start(sem, "socratic", ["kc_09"]).action.kind == "ciu"


def test_a_introducao_entra_no_hash_do_dominio(d, tmp_path):
    """É texto que o participante lê antes de responder. Mudá-lo no meio da
    coleta faria os participantes serem preparados de formas diferentes."""
    copia = copia_dominio(d, tmp_path / "dominio")
    assert load(copia).hash == d.hash

    alvo = copia / "intro.yaml"
    alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# tocado\n", encoding="utf-8")
    assert load(copia).hash != d.hash
