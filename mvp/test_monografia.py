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
            "80 demonstrações com previsão — uma para cada concepção errônea "
            "em cada tópico em que ela aparece — e 402 passos",
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
            "deixa 93 questões do banco fora da trilha"],
        "08-conclusao.md": ["Os 13 tópicos, com 79 premissas, 402 passos e 80 demonstrações"],
    }
    for nome, trechos in afirmado.items():
        texto = _texto(nome)
        for trecho in trechos:
            assert trecho in texto, (nome, trecho)
    assert (c["topicos"], c["premissas"], c["crencas"], c["questoes"]) == (13, 79, 61, 560)
    assert (c["passos"], c["guiados"], c["pratica"], c["versoes"]) == (402, 244, 158, 804)
    assert (c["provas"], c["saidas"], c["do_compilador"]) == (80, 41, 39)
    assert c["fora"] == 93


def test_por_que_61_concepcoes_dao_80_demonstracoes():
    """Uma demonstração por concepção em cada tópico em que ela aparece:
    14 das 61 aparecem em mais de um, e a soma por tópico é 80."""
    vezes = collections.Counter()
    provas = set()
    for t in topicos():
        d, escadas = _escadas(t)
        vezes.update(set(d.crencas))
        provas |= {(t, p.crenca) for e in escadas.values() for p in e.provas}
    repetidas = sum(1 for n in vezes.values() if n > 1)
    assert (len(vezes), repetidas, sum(vezes.values()), len(provas)) == (
        61, 14, 80, 80)
    texto = _texto("03-sistema.md")
    assert "As 61 concepções do catálogo dão 80 demonstrações" in texto
    assert "14 delas aparecem em mais de um tópico" in texto


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


def test_a_conferencia_do_banco_no_texto():
    """O que `confere_banco.py` cobre: 321 questões com código; 69 de
    prever a saída comparadas com o que o programa imprime. Que todas
    batem é `test_banco_compilador` que prende."""
    import confere_banco
    com_codigo = conferidas = 0
    for t in topicos():
        for a in carrega(topico=t).atividades:
            com_codigo += bool(a.codigo.strip())
            if (a.formato == "prever_saida" and confere_banco.imprime(a.codigo)
                    and confere_banco.valor(next(o.texto for o in a.opcoes
                                                 if o.correta))):
                conferidas += 1
    assert (com_codigo, conferidas) == (321, 69)
    assert "Nas 321 questões que têm código" in _texto(
        "05-construcao-e-verificacao.md")
    assert "das 69 questões de prever a saída conferidas, todas" in _texto(
        "06-resultados-da-verificacao.md")


def test_os_trechos_de_codigo_do_realce():
    from mvp import test_interface
    n = len(test_interface._todos_os_trechos())
    assert n == 1762
    assert "| Trechos de código das escadas | 1 762 |" in _texto(
        "06-resultados-da-verificacao.md")


def _secao(texto: str, titulo: str) -> str:
    """O corpo da seção '## titulo', até a próxima seção do mesmo nível."""
    m = re.search(r"^## %s\n(.*?)(?=^## |\Z)" % re.escape(titulo), texto,
                  re.M | re.S)
    assert m, titulo
    return m.group(1)


def _chaves(secao: str) -> list:
    """'### POSNER et al. (1982)' -> ('posner', '1982')."""
    return [(m.group(1).lower(), m.group(2)) for m in re.finditer(
        r"^### ([A-Z][\w-]*)\b[^\n]*\((\d{4})\)", secao, re.M)]


def test_so_a_referencia_nao_aberta_continua_marcada():
    """A regra do README: nenhuma referência entra sem ter sido aberta na obra.
    A conferência de 18/11/2026 abriu todas, menos uma, que segue marcada."""
    marcadas = {}
    for arq in sorted(CAPITULOS.glob("*.md")):
        for m in re.finditer(r"\[conferir[^\]]*\]", arq.read_text(encoding="utf-8")):
            marcadas.setdefault(arq.name, []).append(" ".join(m.group(0).split()))
    assert marcadas == {"apendice-protocolo.md": ["[conferir: Brooke, 1996]"],
                        "referencias.md": ["[conferir: Brooke, 1996]"]}


def test_cada_referencia_da_lista_foi_aberta_e_e_citada():
    """A lista (referencias.md) e o registro da conferência dizem as mesmas
    obras; cada obra aberta é citada no texto; a única não aberta é Brooke."""
    registro = (CAPITULOS / "conferencia-das-referencias.md").read_text(
        encoding="utf-8")
    conferidas = _chaves(_secao(registro, "Conferidas"))
    pendentes = _chaves(_secao(registro, "Ainda não abertas"))
    assert pendentes == [("brooke", "1996")]
    lista = (CAPITULOS / "referencias.md").read_text(encoding="utf-8")
    entradas = [p for p in re.split(r"\n\s*\n", lista)
                if re.match(r"[A-Z][\w-]*[,.]", p.strip())]
    assert len(entradas) == len(conferidas) + len(pendentes)
    for nome, ano in conferidas + pendentes:
        assert any(re.match(re.escape(nome) + "[,.]", e.strip().lower())
                   and ano in e for e in entradas), (nome, ano)
    texto = " ".join(_texto(a.name) for a in sorted(CAPITULOS.glob("0*.md")))
    texto += " " + _texto("apendice-protocolo.md")
    for nome, ano in conferidas:
        assert re.search(re.escape(nome) + r".{0,80}?" + ano, texto,
                         re.I | re.S), (nome, ano)


def test_o_limiar_antigo_da_wcag_da_o_mesmo_contraste_em_8_bits():
    """test_interface usa 0,03928 (WCAG 2.0); a WCAG 2.1, na versão de 2025,
    diz 0,04045. Nenhum valor c/255 cai entre os dois, então o contraste
    calculado é o mesmo — e o capítulo 5 diz isso."""
    assert all((c / 255 <= 0.03928) == (c / 255 <= 0.04045) for c in range(256))
    assert "0,03928" in _texto("05-construcao-e-verificacao.md")


def test_os_capitulos_do_roteiro_existem():
    roteiro = (CAPITULOS / "README.md").read_text(encoding="utf-8")
    for nome in re.findall(r"\]\(([\w.-]+\.md)\)", roteiro):
        assert (CAPITULOS / nome).exists(), nome
    for nome in re.findall(r"`(figuras/[\w.-]+\.jpg)`", roteiro):
        assert (CAPITULOS / nome).exists(), nome
