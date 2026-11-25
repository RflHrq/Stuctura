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
            "80 demonstrações com previsão (uma para cada concepção errônea "
            "em cada tópico em que ela aparece) e 402 passos",
            "em 13 tópicos de ponteiros em C"],
        "03-sistema.md": [
            "organizado em 13 tópicos", "somam 79 premissas",
            "O catálogo tem 61 concepções", "tem 560 questões",
            "somam 402 passos (244 guiados e 158 de prática) e 804 versões",
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
    assert "As 61 concepções do catálogo resultam em 80 demonstrações" in texto
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
    assert c["com_opcao"] == 9 and "nove requerem opções adicionais" in texto
    assert avisos["-fanalyzer"] == 7 and "sete, o analisador de fluxo" in texto
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


def test_o_quadro_dos_demais_perfis():
    """O Quadro 6.3: os outros cinco perfis, no ritmo completo. Com o
    Quadro 6.2, os dez perfis da Seção 5.4 aparecem nos resultados."""
    perfis = ("inseguro", "escorrega", "chuta_com_certeza",
              "tropeca_na_pratica", "abre_a_explicacao")
    do_6_2 = ("sabe", "nao_sabe_aprende", "nao_sabe_erra",
              "crente_aprende", "crente_teimoso")
    assert sorted(perfis + do_6_2) == sorted(trilha_alunos.PERSONAS)
    texto = _texto("06-resultados-da-verificacao.md")
    for t in topicos():
        d, escadas = _escadas(t)
        celulas = []
        for p in perfis:
            cam = trilha_alunos.caminha(d, escadas, p, "direto", "completo")
            celulas.append("%d / %d" % (trilha_alunos.conta(cam),
                                        trilha_alunos.toques(cam)))
        assert "| %s | %s |" % (t, " | ".join(celulas)) in texto, (t, celulas)


def test_as_faixas_de_telas_que_o_texto_afirma():
    """A primeira observação de 6.3, num tópico de seis premissas: 14 telas
    para quem não recebe intervenção, 26 a 44 para quem recebe ensino ou
    demonstração em todas as premissas, 41 a 48 para quem responde ao
    acaso com certeza."""
    telas = collections.defaultdict(set)
    for t in topicos():
        d, escadas = _escadas(t)
        if len(d.nos) != 6:
            continue
        for p in trilha_alunos.PERSONAS:
            cam = trilha_alunos.caminha(d, escadas, p, "direto", "completo")
            telas[p].add(trilha_alunos.conta(cam))
    for p in ("sabe", "inseguro", "escorrega", "abre_a_explicacao"):
        assert telas[p] == {14}, (p, telas[p])
    com_trabalho = set().union(*(telas[p] for p in (
        "nao_sabe_aprende", "nao_sabe_erra", "crente_aprende",
        "crente_teimoso", "tropeca_na_pratica")))
    assert (min(com_trabalho), max(com_trabalho)) == (26, 44)
    acaso = telas["chuta_com_certeza"]
    assert (min(acaso), max(acaso)) == (41, 48)
    texto = _texto("06-resultados-da-verificacao.md")
    assert "em 14 telas" in texto
    assert "em 26 a 44 telas" in texto
    assert "em 41 a 48 telas" in texto


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
    # As que têm código e a saída não confere foram LIDAS, uma vez, com a
    # ferramenta (commit de 18/11/2026), e o texto diz quantas são.
    assert ("A leitura das %d questões com código que a saída não confere"
            % (com_codigo - conferidas)) in _texto(
        "05-construcao-e-verificacao.md")
    assert com_codigo - conferidas == 252


def test_as_cenas_no_texto():
    """As 79 cenas (docs/plano-cenas.md), contadas nos dados: quantas
    passam por função, por array e por bloco do malloc, e quais chamam a
    mesma função duas vezes. O texto do Capítulo 6 diz esses números."""
    import collections
    n = funcao = array = bloco = 0
    duas = []
    for t in topicos():
        _, escadas = _escadas(t)
        for no, e in escadas.items():
            if e.cena is None:
                continue
            n += 1
            tipos = {a.tipo for a in e.cena.atores}
            funcao += "bancada" in tipos
            array += "fileira" in tipos
            bloco += "bloco" in tipos
            chamadas = collections.Counter(arg for p in e.cena.passos
                                           for acao, arg in p.faz if acao == "chama")
            duas += [(t, f) for f, k in chamadas.items() if k > 1]
    assert (n, funcao, array, bloco) == (79, 20, 13, 17)
    assert duas == [("kc_01", "conta"), ("kc_12", "dobra")]
    texto = _texto("06-resultados-da-verificacao.md")
    assert "| Cenas da revisão | 79 |" in texto
    assert "Das 79, 20 passam por dentro de funções" in texto
    assert "13 por arrays e 17 por blocos do `malloc`" in texto
    assert "São 79 cenas, uma por premissa" in _texto("03-sistema.md")


def test_a_leitura_das_perguntas_no_texto():
    """Os números do pente (6.4) saem do registro dele,
    docs/pente-dos-degraus.md: uma entrada por passo reescrito, a do
    passo que o autor leu e as 46 da primeira passada antes de "Segunda
    passada", as 54 da segunda depois."""
    registro = (RAIZ.parent / "docs" / "pente-dos-degraus.md").read_text(
        encoding="utf-8")
    primeira, segunda = registro.split("## Segunda passada")
    assert (primeira.count("\n### "), segunda.count("\n### ")) == (47, 54)
    assert "### esc_kc02_B1_1" in primeira
    guiados = sum(len(e.guiados) for t in topicos() for e in _escadas(t)[1].values())
    assert guiados == 244
    texto = _texto("06-resultados-da-verificacao.md")
    assert ("Dos 244 passos guiados, 101 tiveram a frase reescrita: o passo "
            "lido inicialmente pelo autor, 46 dos marcados pelo programa e "
            "54 que o programa não marcou") in texto


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
    """'### POSNER et al. (1982)' -> ('posner', '1982'). A barra entra por
    causa do nome de entidade: '### ISO/IEC (2011)' -> ('iso/iec', '2011')."""
    return [(m.group(1).lower(), m.group(2)) for m in re.finditer(
        r"^### ([A-Z][\w/-]*)\b[^\n]*\((\d{4})\)", secao, re.M)]


def test_nenhuma_referencia_segue_marcada():
    """A regra do README: nenhuma referência entra sem ter sido aberta na obra.
    A conferência de 18/11/2026 abriu todas menos Brooke (1996), que ficou
    marcada; a segunda, de 19/11/2026, abriu Brooke, e nenhuma marca fica."""
    marcadas = {}
    for arq in sorted(CAPITULOS.glob("*.md")):
        for m in re.finditer(r"\[conferir[^\]]*\]", arq.read_text(encoding="utf-8")):
            marcadas.setdefault(arq.name, []).append(" ".join(m.group(0).split()))
    assert marcadas == {}


def test_cada_referencia_da_lista_foi_aberta_e_e_citada():
    """A lista (referencias.md) e o registro da conferência dizem as mesmas
    obras; cada obra aberta é citada no texto; depois da segunda conferência
    (19/11/2026), nenhuma fica sem abrir."""
    registro = (CAPITULOS / "conferencia-das-referencias.md").read_text(
        encoding="utf-8")
    conferidas = _chaves(_secao(registro, "Conferidas"))
    pendentes = _chaves(_secao(registro, "Ainda não abertas"))
    assert pendentes == []
    lista = (CAPITULOS / "referencias.md").read_text(encoding="utf-8")
    entradas = [p for p in re.split(r"\n\s*\n", lista)
                if re.match(r"[A-Z][\w/-]*[,.]", p.strip())]
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


# --------------------------------------------------------------------------
# O LaTeX (modelo da UFV) é gerado dos .md: não pode envelhecer em silêncio
# --------------------------------------------------------------------------

LATEX = CAPITULOS / "latex"


def test_o_latex_gerado_esta_em_dia_com_o_texto():
    """docs/monografia/latex/gerado/ sai dos .md por
    scripts/monografia_latex.py. Se um .md mudou e o LaTeX não foi gerado
    de novo, o PDF mostra um texto que os testes acima não conferem."""
    import monografia_latex
    assert monografia_latex.main(["--confere"]) == 0, (
        "rode: python scripts/monografia_latex.py")


def test_toda_citacao_do_latex_esta_na_lista_e_toda_obra_e_citada():
    gerado = " ".join(p.read_text(encoding="utf-8")
                      for p in (LATEX / "gerado").glob("*.tex"))
    citadas = set()
    for m in re.finditer(r"\\cite(?:online|year)?(?:\[[^\]]*\])?\{([^}]+)\}",
                         gerado):
        citadas |= {k.strip() for k in m.group(1).split(",")}
    bib = (LATEX / "referencias.bib").read_text(encoding="utf-8")
    na_lista = set(re.findall(r"^@\w+\{([^,]+),", bib, re.M))
    assert citadas - na_lista == set(), "citadas sem entrada no .bib"
    assert na_lista - citadas == set(), "entradas do .bib que ninguém cita"


def test_as_figuras_do_latex_existem_em_ordem():
    """A ABNT numera as figuras na ordem em que aparecem; o Capítulo 3
    as traz de 3.1 a 3.6, cada uma com o arquivo que existe."""
    cap3 = (LATEX / "gerado" / "03-sistema.tex").read_text(encoding="utf-8")
    rotulos = re.findall(r"\\label\{fig:(3-\d)\}", cap3)
    assert rotulos == ["3-%d" % n for n in range(1, 7)]
    for arq in re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", cap3):
        assert (CAPITULOS / "figuras" / arq).exists(), arq


def test_a_figura_em_colunas_ocupa_a_largura_do_texto():
    """A tela comprida (o fechamento, a página inicial) é capturada inteira
    e vai em colunas, numa imagem larga. Na meia largura das capturas de
    celular cada coluna ficaria com um terço do tamanho, e não se leria:
    a imagem larga ocupa a largura do texto, e a de celular segue como
    estava."""
    import monografia_latex
    cap3 = (LATEX / "gerado" / "03-sistema.tex").read_text(encoding="utf-8")
    opcoes = {arq: op for op, arq in re.findall(
        r"\\includegraphics\[([^\]]*)\]\{([^}]+)\}", cap3)}
    largas = set()
    for arq in opcoes:
        largura, altura = monografia_latex.tamanho_jpeg(
            CAPITULOS / "figuras" / arq)
        if largura > 0.7 * altura:
            largas.add(arq)
    assert largas == {"fig-3-3-fechamento.jpg", "fig-3-6-inicio-escuro.jpg"}
    for arq in largas:
        assert opcoes[arq].startswith("width=\\textwidth,"), arq
    assert opcoes["fig-3-1-pergunta.jpg"].startswith("width=.5\\textwidth,")


def test_o_apendice_b_traz_cada_concepcao_do_catalogo_uma_vez():
    """O Apêndice B sai do catálogo por scripts/gera_curadoria.py: cada
    concepção aparece uma vez, com o grau que o catálogo lhe dá. Se o
    catálogo mudar e o apêndice não for gerado de novo, este teste cai."""
    import yaml
    catalogo = {}
    for p in sorted((RAIZ / "dominio").glob("beliefs_kc*.yaml")):
        for b in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            catalogo.setdefault(b["id"], b["provenance"])
    linhas = [l for l in (CAPITULOS / "apendice-curadoria.md").read_text(
        encoding="utf-8").splitlines() if l.startswith("| `")]
    no_apendice = {}
    for l in linhas:
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        no_apendice[c[0].strip("`")] = c[4].strip("`")
    assert len(linhas) == len(no_apendice) == len(catalogo) == 61
    assert no_apendice == catalogo


def test_o_apendice_c_traz_as_colunas_da_exportacao():
    """O Apêndice C descreve as três tabelas do exportador da trilha. Cada
    coluna que o código gera está no quadro da sua tabela, e o quadro não
    tem coluna que o código não gere: se a exportação mudar e o apêndice
    não, este teste falha."""
    from mvp import exporta_trilha
    texto = (CAPITULOS / "apendice-exportacao.md").read_text(encoding="utf-8")
    quadros = {"sessoes.csv": "C.1", "premissas.csv": "C.2",
               "respostas.csv": "C.3"}
    for tabela, quadro in quadros.items():
        m = re.search(r"\*\*Quadro %s — Colunas de `%s`\*\*\s*\n\n(.*?)(?:\n\n|\Z)"
                      % (re.escape(quadro), re.escape(tabela)), texto, re.S)
        assert m, "falta o Quadro %s de %s" % (quadro, tabela)
        colunas = re.findall(r"^\| `([a-z_]+)` \|", m.group(1), re.M)
        assert colunas == exporta_trilha.COLUNAS[tabela], tabela
