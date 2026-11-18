"""Os números da monografia, conferidos contra o sistema.

Como `test_procedencia.py` faz com o capítulo de curadoria: cada número
que os capítulos 1, 3, 6 e 8 afirmam é recalculado aqui, a partir do
domínio e das escadas. Se o sistema mudar e o texto não, a suíte falha e
diz a frase a reescrever (docs/monografia/README.md).
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import trilha_alunos  # noqa: E402
from mvp import trilha_escada  # noqa: E402
from mvp.dominio import carrega, topicos  # noqa: E402

CAPITULOS = RAIZ.parent / "docs" / "monografia"


def _texto(nome: str) -> str:
    return " ".join((CAPITULOS / nome).read_text(encoding="utf-8").split())


def _escadas(topico):
    d = carrega(topico=topico)
    arquivo = RAIZ / "dominio" / ("escada_%s.yaml" % topico.replace("_", ""))
    return d, trilha_escada.le(arquivo, d)


@pytest.fixture(scope="module")
def contagens():
    c = collections.Counter()
    formas = collections.Counter()
    avisos = collections.Counter()
    titulos = {}
    for t in topicos():
        d, escadas = _escadas(t)
        titulos[t] = (d.titulo, len(d.ordem))
        c["topicos"] += 1
        c["premissas"] += len(d.ordem)
        c["questoes"] += len(d.atividades)
        for e in escadas.values():
            c["fora"] += len(e.fora)
            for g in e.degraus:
                c["passos"] += 1
                c["versoes"] += len(g.versoes)
                c["guiados" if g.guiado else "pratica"] += 1
                formas[g.forma] += 1
            for p in e.provas:
                c["provas"] += 1
                c["do_compilador" if p.reclama else "saidas"] += 1
                if p.avisos:
                    c["com_opcao"] += 1
                for a in p.avisos:
                    avisos[a] += 1
    crencas = set()
    for t in topicos():
        crencas |= set(carrega(topico=t).crencas)
    c["crencas"] = len(crencas)
    return c, formas, avisos, titulos


def test_os_numeros_do_sistema_estao_no_texto(contagens):
    c, _, _, _ = contagens
    afirmado = {
        "01-introducao.md": [
            "catálogo de 61 concepções errôneas",
            "80 demonstrações com previsão, uma por concepção errônea, e 402 passos",
            "treze tópicos de ponteiros em C"],
        "03-sistema.md": [
            "organizado em **13 tópicos**", "somam **79 premissas**",
            "O catálogo tem 61 concepções", "tem 560 questões",
            "somam **402 passos** (244 guiados e 158 de prática) e 804 versões",
            "Em 41 das 80 demonstrações", "Nas outras 39"],
        "06-resultados-da-verificacao.md": [
            "| Premissas | 79 |", "| Concepções errôneas no catálogo | 61 |",
            "| Questões no banco | 560 |", "| Passos de escada (versões) | 402 (804) |",
            "| Demonstrações com previsão | 80 (41 saídas, 39 do compilador) |",
            "deixa 94 questões do banco fora da trilha"],
        "08-conclusao.md": ["Os 13 tópicos, com 79 premissas, 402 passos e 80 demonstrações"],
    }
    for nome, trechos in afirmado.items():
        texto = _texto(nome)
        for trecho in trechos:
            assert trecho in texto, (nome, trecho)
    assert (c["topicos"], c["premissas"], c["crencas"], c["questoes"]) == (13, 79, 61, 560)
    assert (c["passos"], c["guiados"], c["pratica"], c["versoes"]) == (402, 244, 158, 804)
    assert (c["provas"], c["saidas"], c["do_compilador"]) == (80, 41, 39)
    assert c["fora"] == 94


def test_o_quadro_dos_topicos_e_o_das_formas(contagens):
    _, formas, _, titulos = contagens
    texto = _texto("03-sistema.md")
    for t, (titulo, n) in titulos.items():
        assert "| %s | %s | %d |" % (t, titulo, n) in texto, t
    for forma, n in formas.items():
        assert "| %s | %d |" % (forma, n) in texto, forma


def test_as_opcoes_de_compilador_das_demonstracoes(contagens):
    c, _, avisos, _ = contagens
    texto = _texto("06-resultados-da-verificacao.md")
    assert c["com_opcao"] == 9 and "nove pedem opções a mais" in texto
    assert avisos["-fanalyzer"] == 7 and "sete o analisador de fluxo" in texto
    assert "`-O2` com `-Wnull-dereference`" in texto
    assert avisos == {"-fanalyzer": 7, "-O2": 1, "-Wnull-dereference": 1,
                      "-Wpointer-arith": 1}


def test_o_quadro_da_medida(contagens):
    """O Quadro 6.2: telas e toques de cinco perfis, no ritmo completo."""
    perfis = ("sabe", "nao_sabe_aprende", "nao_sabe_erra",
              "crente_aprende", "crente_teimoso")
    texto = _texto("06-resultados-da-verificacao.md")
    for t in topicos():
        d, escadas = _escadas(t)
        celulas = []
        for p in perfis:
            cam = trilha_alunos.caminha(d, escadas, p, "direto", "completo")
            celulas.append("%d / %d" % (trilha_alunos.conta(cam),
                                        trilha_alunos.toques(cam)))
        assert "| %s | %s |" % (t, " | ".join(celulas)) in texto, (t, celulas)


def test_os_trechos_de_codigo_do_realce():
    from mvp import test_interface
    n = len(test_interface._todos_os_trechos())
    assert n == 1762
    assert "| Trechos de código das escadas | 1 762 |" in _texto(
        "06-resultados-da-verificacao.md")


def test_os_capitulos_do_roteiro_existem():
    roteiro = (CAPITULOS / "README.md").read_text(encoding="utf-8")
    for nome in re.findall(r"\]\(([\w.-]+\.md)\)", roteiro):
        assert (CAPITULOS / nome).exists(), nome
    for nome in re.findall(r"`(figuras/[\w.-]+\.jpg)`", roteiro):
        assert (CAPITULOS / nome).exists(), nome
