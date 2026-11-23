"""Gera os capítulos da monografia em LaTeX (abnTeX2, modelo da UFV) a
partir dos arquivos .md de docs/monografia.

Os .md continuam sendo a fonte: é neles que os testes prendem os números
ao sistema (mvp/test_monografia.py, mvp/test_procedencia.py). Este script
só traduz a forma, e recusa o que não sabe traduzir: uma citação que não
está na tabela abaixo, uma figura ou um quadro citado que não existe, um
título cujo número não bate com o que o LaTeX vai numerar.

    python scripts/monografia_latex.py            # escreve latex/gerado/
    python scripts/monografia_latex.py --confere  # falha se estiver velho

O arquivo principal, docs/monografia/latex/TCC_STRUCTURA.tex, é escrito à
mão (capa, dedicatória, agradecimentos, listas) e inclui os gerados.
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = RAIZ / "docs" / "monografia"
DESTINO = FONTE / "latex" / "gerado"

# (arquivo .md, nome do .tex gerado, número do capítulo)
CAPITULOS = [
    ("01-introducao.md", "01-introducao", "1"),
    ("02-fundamentacao.md", "02-fundamentacao", "2"),
    ("03-sistema.md", "03-sistema", "3"),
    ("curadoria.md", "04-curadoria", "4"),
    ("05-construcao-e-verificacao.md", "05-construcao-e-verificacao", "5"),
    ("06-resultados-da-verificacao.md", "06-resultados-da-verificacao", "6"),
    ("07-limitacoes-e-trabalhos-futuros.md",
     "07-limitacoes-e-trabalhos-futuros", "7"),
    ("08-conclusao.md", "08-conclusao", "8"),
]
APENDICES = [("apendice-protocolo.md", "apendice-a-protocolo", "A"),
             ("apendice-curadoria.md", "apendice-b-curadoria", "B")]

# Um quadro com mais linhas que isto não cabe numa página: vira tabela
# longa, que quebra entre páginas e repete o cabeçalho.
LINHAS_DO_QUADRO_LONGO = 25

FONTE_PADRAO_QUADRO = "Elaborado pelo autor."
FONTE_PADRAO_FIGURA = "Captura de tela do Structura, elaborada pelo autor."

# --------------------------------------------------------------------------
# Citações: NBR 10520/2023, como no manual de normalização da UFV (2026)
# --------------------------------------------------------------------------
# No .md a citação vem na forma da norma: "(Posner et al., 1982, p. 221)"
# ou "Posner et al. (1982, p. 212)". O sobrenome tem só a inicial maiúscula,
# também entre parênteses; "et al." e "apud" saem em itálico. O abntex2cite
# escreveria o sobrenome em caixa alta, e por isso a autoria é escrita aqui
# por extenso e só o ano vem de \citeyear, que liga a citação à referência.
# Uma citação que não esteja nesta tabela faz o script parar.
#
# (chave do .bib, ano, autoria no texto, autoria entre parênteses)
OBRAS = [
    ("brooke1996", "1996", "Brooke", "Brooke"),
    ("falmagne2006", "2006", "Falmagne et al.", "Falmagne et al."),
    ("gardnermedwin2006", "2006", "Gardner-Medwin", "Gardner-Medwin"),
    ("hermans2018", "2018", "Hermans et al.", "Hermans et al."),
    ("isoiec2011", "2011", "ISO/IEC", "ISO/IEC"),
    ("mitre2026", "2026", "MITRE", "MITRE"),
    ("nussbaum2017", "2017", "Nussbaum, Cordova e Rehmat",
     "Nussbaum; Cordova; Rehmat"),
    ("posner1982", "1982", "Posner et al.", "Posner et al."),
    ("qian2017", "2017", "Qian e Lehman", "Qian; Lehman"),
    ("schmellenkamp2023", "2023", "Schmellenkamp, Latys e Zeume",
     "Schmellenkamp; Latys; Zeume"),
    ("sei2025", "2025", "SEI", "SEI"),
    ("soderstrom2015", "2015", "Soderstrom e Bjork", "Soderstrom; Bjork"),
    ("sorva2012", "2012", "Sorva", "Sorva"),
    ("sorva2013", "2013", "Sorva", "Sorva"),
    ("summit2005", "c2005", "Summit", "Summit"),
    ("ufv2026", "[2026]", "UFV", "UFV"),
    ("sweller2019", "2019", "Sweller, Van Merriënboer e Paas",
     "Sweller; Van Merriënboer; Paas"),
    ("vanlehn2006", "2006", "VanLehn", "VanLehn"),
    ("vanlehn2011", "2011", "VanLehn", "VanLehn"),
    ("w3c2025", "2025", "W3C", "W3C"),
    ("white1992", "1992", "White e Gunstone", "White; Gunstone"),
    ("yamashita2017", "2017", "Yamashita et al.", "Yamashita et al."),
]
# Obras citadas por intermédio de outra (apud). A lista de referências traz
# só as obras consultadas, de modo que estas ficam como texto.
SEM_REFERENCIA = {"Boulay", "Soloway et al.", "Putnam et al.",
                  "Sleeman et al.", "Samurçay", "Holland et al.", "Ma",
                  "Doukakis et al.", "Kaczmarczyk et al."}

# Página ou outro localizador, depois do ano: ", p. 212-213" ou ", cap. 3".
LOCALIZADOR = r"(?:, ((?:p|cap)\. [\dIVXivx\-]+))?"

# O que parece citação e não foi traduzido: "(Autor, 2000...)" ou
# "Autor (2000...".
PADRAO_DE_CITACAO = re.compile(
    r"\((?P<par>[A-ZÀ-Ý][^()]{0,70}?), c?\d{4}[a-z]?(?:, [^()]{0,20})?\)"
    r"|(?P<txt>[A-ZÀ-Ý][\wÀ-ÿ\-]+(?:(?:, [A-ZÀ-Ý][\wÀ-ÿ\-]+)* e "
    r"[A-ZÀ-Ý][\wÀ-ÿ\-]+| et al\.)?) \(c?\d{4}")


def _autoria_tex(autoria: str) -> str:
    return autoria.replace("et al.", r"\textit{et al.}")


def _localizador_tex(loc) -> str:
    return ", " + loc.replace(". ", ".~") if loc else ""


def _direta(m) -> bool:
    """A citação é direta quando vem logo depois de um trecho entre aspas:
    '"Null model of recursion" (Sorva, 2012, p. 362)'."""
    return m.string[:m.start()].rstrip().endswith('"')


def _tira_repetidas(t: str) -> str:
    """Num mesmo parágrafo, a obra é citada uma vez (decisão do autor em
    23/11/2026). Sem a página, as citações indiretas de uma mesma obra
    ficaram iguais, e repeti-las a cada frase não acrescenta nada.

    Sai só a citação inteira entre parênteses, indireta, de uma obra que o
    parágrafo já citou. Ficam: a primeira citação de cada obra, toda
    citação direta (com a página), a autoria na frase ("Sorva (2012)
    afirma"), que faz parte da frase, e a citação de citação (apud). O .md
    não muda: é nele que cada afirmação continua com a sua citação e a sua
    página, para a conferência.
    """
    achados = []
    for chave, ano, txt, par in OBRAS:
        a = re.escape(ano) + LOCALIZADOR + r"\)"
        formas = (("apud", r"\([^()]{1,80}? apud " + re.escape(par) + ", " + a),
                  ("par", r" ?\(" + re.escape(par) + ", " + a),
                  ("frase", re.escape(txt) + r" \(" + a))
        for tipo, padrao in formas:
            for m in re.finditer(padrao, t):
                achados.append((m.start(), m.end(), chave, tipo, _direta(m)))
    vistas, cortes = set(), []
    for ini, fim, chave, tipo, direta in sorted(achados):
        if tipo == "par" and not direta and chave in vistas:
            cortes.append((ini, fim))
        vistas.add(chave)
    for ini, fim in reversed(cortes):
        t = t[:ini] + t[fim:]
    return t


def _traduz_citacoes(t: str, guarda) -> str:
    """Troca cada citação do texto pela forma em LaTeX, já guardada.

    A PÁGINA SÓ VAI PARA O PDF NA CITAÇÃO DIRETA (decisão do autor em
    23/11/2026: a NBR 10520 só a exige nesse caso). O .md guarda a página
    em toda citação, porque é por ela que a obra é conferida
    (docs/monografia/roteiro-de-conferencia.md); aqui, a página da citação
    indireta fica de fora do LaTeX.
    """
    t = _tira_repetidas(t)
    # 1. citação de citação: "(Tippett, 2010, p. 965 apud Nussbaum; Cordova;
    #    Rehmat, 2017, p. 31)" e "Ma (2007 apud Sorva, 2012, p. 364)"
    for chave, ano, _, par in OBRAS:
        padrao = (r"\(([^()]{1,80}?) apud " + re.escape(par) + ", "
                  + re.escape(ano) + LOCALIZADOR + r"\)")

        def apud(m, chave=chave, par=par):
            direta = _direta(m)
            original = m.group(1)
            if not direta:
                original = re.sub(r", (?:p|cap)\. [\dIVXivx\-]+", "", original)
            original = _escapa(original).replace("p. ", "p.~")
            return guarda("(%s \\textit{apud} %s, \\citeyear{%s}%s)" % (
                _autoria_tex(original), _autoria_tex(par), chave,
                _localizador_tex(m.group(2) if direta else None)))
        t = re.sub(padrao, apud, t)
    # 2. autoria entre parênteses: "(Posner et al., 1982, p. 221)"
    for chave, ano, _, par in OBRAS:
        padrao = (r"\(" + re.escape(par) + ", " + re.escape(ano)
                  + LOCALIZADOR + r"\)")

        def entre(m, chave=chave, par=par):
            return guarda("(%s, \\citeyear{%s}%s)" % (
                _autoria_tex(par), chave,
                _localizador_tex(m.group(1) if _direta(m) else None)))
        t = re.sub(padrao, entre, t)
    # 3. autoria na frase: "Posner et al. (1982, p. 212)"
    for chave, ano, txt, _ in OBRAS:
        padrao = (re.escape(txt) + r" \(" + re.escape(ano) + LOCALIZADOR
                  + r"\)")

        def frase(m, chave=chave, txt=txt):
            return guarda("%s (\\citeyear{%s}%s)" % (
                _autoria_tex(txt), chave,
                _localizador_tex(m.group(1) if _direta(m) else None)))
        t = re.sub(padrao, frase, t)
    sobra = []
    for m in PADRAO_DE_CITACAO.finditer(t):
        if m.group("txt") is not None and m.group("txt") in SEM_REFERENCIA:
            continue
        sobra.append(m.group(0))
    if sobra:
        raise Erro("citação sem tradução: %s" % sobra)
    # "et al." das obras citadas por intermédio de outra
    return re.sub(r"\bet al\.", lambda m: guarda(r"\textit{et al.}"), t)


class Erro(Exception):
    pass


# --------------------------------------------------------------------------
# Texto corrido
# --------------------------------------------------------------------------

def _escapa(t: str) -> str:
    trocas = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
              "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
              "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
              "|": r"\textbar{}", "<": r"\textless{}", ">": r"\textgreater{}"}
    return "".join(trocas.get(c, c) for c in t)


def _codigo(t: str) -> str:
    e = _escapa(t)
    # deixa quebrar caminhos e nomes longos
    if len(t) > 14:
        e = re.sub(r"(/|\\_|\.)", r"\1\\allowbreak{}", e)
    return r"\texttt{%s}" % e.replace("'", r"\textquotesingle{}").replace(
        "`", r"\textasciigrave{}").replace("-", "-{}")


class Texto:
    """Converte uma linha de texto corrido, guardando à parte o que já é
    LaTeX (código, citações, referências cruzadas) enquanto escapa o
    resto."""

    def __init__(self, rotulos: dict):
        self.rotulos = rotulos   # "fig:3.4" -> label LaTeX
        self.guardado: list[str] = []

    def _guarda(self, latex: str) -> str:
        self.guardado.append(latex)
        return "\x00%d\x00" % (len(self.guardado) - 1)

    def _ref(self, tipo: str, num: str) -> str:
        m = re.fullmatch(r"([0-9A-Z]+\.\d+)([ab]?)", num)
        if not m:
            raise Erro("referência estranha: %s %s" % (tipo, num))
        chave = "%s:%s" % (tipo, m.group(1))
        if chave not in self.rotulos:
            raise Erro("o texto cita %s %s, que não existe" % (tipo, num))
        return r"\ref{%s}%s" % (self.rotulos[chave], m.group(2))

    def converte(self, t: str) -> str:
        self.guardado = []
        # aspas do TeX que vêm do título de uma pergunta do FAQ
        t = re.sub(r"``(.+?)''",
                   lambda m: self._guarda("``%s''" % _escapa(m.group(1))), t)
        t = re.sub(r"(?<!`)`([^`]+)`(?!`)",
                   lambda m: self._guarda(_codigo(m.group(1))), t)

        def link(m):
            texto, alvo = m.group(1), m.group(2)
            if alvo.endswith(".md") and texto == alvo:
                return self._guarda(_codigo("docs/monografia/" + alvo))
            return texto
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, t)

        t = _traduz_citacoes(t, self._guarda)

        def cruzada(m):
            palavra, nums = m.group(1), m.group(2)
            tipo = "fig" if palavra.startswith("Figura") else "qua"
            partes = re.split(r"( e | a |, )", nums)
            saida = [self._ref(tipo, p) if i % 2 == 0 else p
                     for i, p in enumerate(partes)]
            return self._guarda(palavra + "~" + "".join(
                s.replace(" e ", " e~").replace(" a ", " a~")
                if i % 2 else s for i, s in enumerate(saida)))
        num = r"[0-9A-Z]+\.\d+[ab]?"
        t = re.sub(r"\b(Figuras?|Quadros?) (%s(?:(?: e | a |, )%s)*)"
                   % (num, num), cruzada, t)

        # um asterisco solto é o operador de C, como em "& e *"
        t = re.sub(r"(?<=\s)\*(?=\s|$)", lambda m: self._guarda("*"), t)
        t = _escapa(t)
        # "Seção 7" e "Apêndice A" não se partem entre o nome e o número
        t = re.sub(r"\b(Seção|Seções|Apêndice) (?=[\dA-Z])", r"\1~", t)
        t = re.sub(r'"([^"]*)"', r"``\1''", t)
        t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
        t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])",
                   r"\\textit{\1}", t)
        if "*" in t or '"' in t:
            raise Erro("marcação que sobrou: %r" % t[:120])
        # devolve o que foi guardado (pode haver guardado dentro de guardado)
        while "\x00" in t:
            t = re.sub("\x00(\\d+)\x00",
                       lambda m: self.guardado[int(m.group(1))], t)
        return t


# --------------------------------------------------------------------------
# Blocos
# --------------------------------------------------------------------------

def _blocos(md: str):
    """Quebra o .md em blocos: ('titulo', nivel, texto), ('par', texto),
    ('lista', ordenada, [itens]), ('tabela', [linhas]), ('imagem', alt,
    caminho), ('codigo', [linhas]), ('citacao', texto)."""
    L = md.split("\n")
    i = 0
    while i < len(L):
        l = L[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith("```"):
            j = i + 1
            while not L[j].startswith("```"):
                j += 1
            yield ("codigo", L[i + 1:j])
            i = j + 1
            continue
        m = re.match(r"^(#+) (.*)$", l)
        if m:
            yield ("titulo", len(m.group(1)), m.group(2).strip())
            i += 1
            continue
        if l.startswith("|"):
            j = i
            while j < len(L) and L[j].startswith("|"):
                j += 1
            yield ("tabela", L[i:j])
            i = j
            continue
        m = re.match(r"^!\[(.+)\]\((.+)\)$", l)
        if m:
            yield ("imagem", m.group(1), m.group(2))
            i += 1
            continue
        if l.startswith(">"):
            j = i
            while j < len(L) and L[j].startswith(">"):
                j += 1
            yield ("citacao", " ".join(x[1:].strip() for x in L[i:j]).strip())
            i = j
            continue
        if re.match(r"^(- |\d+\. )", l):
            ordenada = bool(re.match(r"^\d+\. ", l))
            itens = []
            j = i
            while j < len(L) and (re.match(r"^(- |\d+\. )", L[j])
                                  or (L[j].startswith("  ") and L[j].strip())):
                if re.match(r"^(- |\d+\. )", L[j]):
                    itens.append(re.sub(r"^(- |\d+\. )", "", L[j]).strip())
                else:
                    itens[-1] += " " + L[j].strip()
                j += 1
            yield ("lista", ordenada, itens)
            i = j
            continue
        j = i
        while (j < len(L) and L[j].strip() and not L[j].startswith(("|", "#",
               "```", ">")) and not re.match(r"^!\[", L[j])
               and not (j > i and re.match(r"^(- |\d+\. )", L[j]))):
            j += 1
        yield ("par", " ".join(x.strip() for x in L[i:j]))
        i = j


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def _rotulo(tipo: str, num: str) -> str:
    return "%s:%s" % (tipo, num.replace(".", "-"))


def _quadro(linhas, titulo, num, fonte, tx: Texto) -> str:
    cab = _celulas(linhas[0])
    corpo = [_celulas(l) for l in linhas[2:]]
    n = len(cab)
    if any(len(r) != n for r in corpo):
        raise Erro("Quadro %s: linha com número de colunas diferente" % num)
    if len(corpo) > LINHAS_DO_QUADRO_LONGO:
        return _quadro_longo(cab, corpo, titulo, num, fonte, tx)
    larguras = [max(len(r[k]) for r in [cab] + corpo) for k in range(n)]
    colunas = []
    for k in range(n):
        if larguras[k] <= 12:
            colunas.append(">{\\centering\\arraybackslash}p{%.1fcm}"
                           % max(1.2, 0.22 * larguras[k] + 0.4)
                           if n > 2 else "l")
        else:
            colunas.append("X")
    if "X" not in colunas:
        colunas[0] = "X"
    s = ["\\begin{quadro}[htbp]",
         "\\caption{%s}\\label{%s}" % (tx.converte(titulo),
                                        _rotulo("qua", num)),
         "\\footnotesize",
         "\\begin{tabularx}{\\textwidth}{|%s|}" % "|".join(colunas),
         "\\hline"]
    if any(cab):
        s.append(" & ".join("\\textbf{%s}" % tx.converte(c) for c in cab)
                 + " \\\\ \\hline")
    for r in corpo:
        s.append(" & ".join(tx.converte(c) for c in r) + " \\\\ \\hline")
    s += ["\\end{tabularx}",
          "\\fonte{%s}" % tx.converte(fonte),
          "\\end{quadro}"]
    return "\n".join(s)


def _quadro_longo(cab, corpo, titulo, num, fonte, tx: Texto) -> str:
    """Quadro que atravessa páginas: título e entrada na lista de quadros
    feitos à mão (o longtable não usa o contador de quadro), cabeçalho
    repetido em cada página, fonte no fim."""
    n = len(cab)
    # cada coluna tem pelo menos a largura do próprio título, em negrito
    larg = [max(min(max(len(r[k]) for r in corpo), 32),
                int(len(cab[k]) * 1.9) + 3)
            for k in range(n)]
    livre = 1 - n * 0.0145          # o espaço entre colunas (3 pt) e os fios
    fr = [livre * w / sum(larg) for w in larg]
    colunas = "|".join(">{\\raggedright\\arraybackslash}p{%.3f\\linewidth}" % f
                       for f in fr)
    cabecalho = (" & ".join("\\textbf{%s}" % tx.converte(c) for c in cab)
                 + " \\\\ \\hline")
    titulo_tex = tx.converte(titulo)
    s = ["\\begin{center}",
         "\\refstepcounter{quadro}\\label{%s}" % _rotulo("qua", num),
         "\\addcontentsline{loq}{quadro}{\\protect\\numberline{\\thequadro}"
         "%s}" % titulo_tex,
         "Quadro~\\thequadro~--~%s" % titulo_tex,
         "\\end{center}",
         "{\\scriptsize\\setlength{\\tabcolsep}{3pt}",
         "\\begin{longtable}{|%s|}" % colunas,
         "\\hline", cabecalho, "\\endfirsthead",
         "\\hline", cabecalho, "\\endhead"]
    for r in corpo:
        s.append(" & ".join(tx.converte(c) for c in r) + " \\\\ \\hline")
    s += ["\\end{longtable}}",
          "\\vspace{-\\baselineskip}",
          "\\fonte{%s}" % tx.converte(fonte)]
    return "\n".join(s)


def tamanho_jpeg(caminho) -> tuple[int, int]:
    """A largura e a altura de um JPEG, lidas do cabeçalho do arquivo."""
    dados = pathlib.Path(caminho).read_bytes()
    k = 2
    while k + 9 < len(dados):
        if dados[k] != 0xFF:
            raise Erro("JPEG fora do padrão: %s" % caminho)
        marca = dados[k + 1]
        tamanho = int.from_bytes(dados[k + 2:k + 4], "big")
        # Os quadros SOF0 a SOF15 trazem as medidas; C4, C8 e CC são
        # outras tabelas com o mesmo começo de código.
        if 0xC0 <= marca <= 0xCF and marca not in (0xC4, 0xC8, 0xCC):
            altura = int.from_bytes(dados[k + 5:k + 7], "big")
            largura = int.from_bytes(dados[k + 7:k + 9], "big")
            return largura, altura
        k += 2 + tamanho
    raise Erro("JPEG sem as medidas: %s" % caminho)


def _figura(imagens, tx: Texto) -> str:
    """Uma imagem, ou um par 'a'/'b' que vira uma figura só.

    A captura de celular ocupa meia largura do texto. A tela comprida vem
    em colunas, numa imagem larga, e ocupa a largura inteira: na meia
    largura, cada coluna ficaria pequena demais para ler.
    """
    def partes(alt):
        m = re.fullmatch(r"Figura (\d+\.\d+)([ab]?) — (.+)", alt)
        if not m:
            raise Erro("legenda de figura fora do padrão: %s" % alt)
        return m.group(1), m.group(2), m.group(3)
    num = partes(imagens[0][0])[0]
    if len(imagens) == 1:
        _, letra, leg = partes(imagens[0][0])
        arq = pathlib.PurePosixPath(imagens[0][1]).name
        largura, altura = tamanho_jpeg(FONTE / imagens[0][1])
        medidas = ("width=\\textwidth,height=.72\\textheight"
                   if largura > 0.7 * altura
                   else "width=.5\\textwidth,height=.55\\textheight")
        corpo = "\\includegraphics[%s,keepaspectratio]{%s}" % (medidas, arq)
        legenda = tx.converte(leg)
    else:
        corpo, legendas = [], []
        for alt, caminho in imagens:
            n, letra, leg = partes(alt)
            if n != num:
                raise Erro("par de figuras com números diferentes: %s" % alt)
            arq = pathlib.PurePosixPath(caminho).name
            corpo.append(
                "\\begin{minipage}[t]{.48\\textwidth}\\centering\n"
                "\\includegraphics[width=\\textwidth,height=.5\\textheight,"
                "keepaspectratio]{%s}\\\\[2pt]\n(%s)\n\\end{minipage}"
                % (arq, letra))
            legendas.append("(%s) %s" % (letra, tx.converte(leg)))
        corpo = "\\hfill\n".join(corpo)
        legenda = "; ".join(legendas)
    return "\n".join(["\\begin{figure}[htbp]", "\\centering",
                      "\\caption{%s}\\label{%s}" % (legenda,
                                                     _rotulo("fig", num)),
                      corpo,
                      "\\fonte{%s}" % FONTE_PADRAO_FIGURA,
                      "\\end{figure}"])


def _rotulos_do_texto(arquivos) -> dict:
    """Todas as figuras e quadros dos .md, para as referências cruzadas."""
    r = {}
    for nome in arquivos:
        md = (FONTE / nome).read_text(encoding="utf-8")
        for m in re.finditer(r"^!\[Figura (\d+\.\d+)[ab]? — ", md, re.M):
            r["fig:" + m.group(1)] = _rotulo("fig", m.group(1))
        for m in re.finditer(r"^\*\*Quadro ([0-9A-Z]+\.\d+) — .+\*\*$",
                             md, re.M):
            r["qua:" + m.group(1)] = _rotulo("qua", m.group(1))
    return r


def capitulo(nome: str, numero: str, rotulos: dict,
             apendice: bool = False) -> str:
    md = (FONTE / nome).read_text(encoding="utf-8")
    tx = Texto(rotulos)
    blocos = list(_blocos(md))
    saida = ["%% Gerado de docs/monografia/%s por scripts/monografia_latex.py."
             % nome, "% Não edite aqui: edite o .md e gere de novo.", ""]
    secao = subsecao = 0
    k = 0
    while k < len(blocos):
        b = blocos[k]
        tipo = b[0]
        if tipo == "titulo":
            nivel, titulo = b[1], b[2]
            if nivel == 2 and titulo == "Referências deste capítulo":
                break   # a lista vai para referencias.bib
            if nivel == 1:
                titulo = re.sub(r"^(\d+\.|Apêndice [A-Z] —)\s*", "", titulo)
                # título de capítulo não se parte com hífen
                caixas = " ".join("\\mbox{%s}" % tx.converte(p)
                                  for p in titulo.upper().split())
                saida.append("\\chapter{\\texorpdfstring{%s}{%s}}"
                             "\\label{cap:%s}"
                             % (caixas, tx.converte(titulo.upper()), numero))
            elif nivel == 2:
                secao += 1
                subsecao = 0
                m = re.match(r"^([0-9A-Z]+)\.(\d+) (.*)$", titulo)
                if m:
                    if (m.group(1), int(m.group(2))) != (numero, secao):
                        raise Erro("%s: seção %s.%s, mas o LaTeX numera "
                                   "%s.%d" % (nome, m.group(1), m.group(2),
                                              numero, secao))
                    titulo = m.group(3)
                saida.append("\\section{%s}" % tx.converte(titulo))
            elif nivel == 3:
                subsecao += 1
                m = re.match(r"^(\d+)\. (.*)$", titulo)
                completo = re.match(r"^([0-9A-Z]+)\.(\d+)\.(\d+) (.*)$",
                                    titulo)
                if m:
                    if int(m.group(1)) != subsecao:
                        raise Erro("%s: subseção %s fora de ordem"
                                   % (nome, m.group(1)))
                    titulo = m.group(2)
                elif completo:
                    num = (completo.group(1), int(completo.group(2)),
                           int(completo.group(3)))
                    if num != (numero, secao, subsecao):
                        raise Erro("%s: subseção %s.%d.%d, mas o LaTeX "
                                   "numera %s.%d.%d" % ((nome,) + num + (
                                       numero, secao, subsecao)))
                    titulo = completo.group(4)
                saida.append("\\subsection{%s}" % tx.converte(titulo))
            else:
                raise Erro("%s: título de nível %d" % (nome, nivel))
        elif tipo == "par":
            m = re.fullmatch(r"\*\*Quadro ([0-9A-Z]+\.\d+) — (.+)\*\*", b[1])
            if m:
                if k + 1 >= len(blocos) or blocos[k + 1][0] != "tabela":
                    raise Erro("Quadro %s sem tabela logo abaixo" % m.group(1))
                fonte = FONTE_PADRAO_QUADRO
                pula = 2
                if (k + 2 < len(blocos) and blocos[k + 2][0] == "par"
                        and re.fullmatch(r"\*Fonte: (.+)\*", blocos[k + 2][1])):
                    fonte = re.fullmatch(r"\*Fonte: (.+)\*",
                                         blocos[k + 2][1]).group(1)
                    fonte = fonte[0].upper() + fonte[1:]
                    pula = 3
                if not m.group(1).startswith(numero + "."):
                    raise Erro("Quadro %s no capítulo %s" % (m.group(1),
                                                              numero))
                saida.append(_quadro(blocos[k + 1][1], m.group(2), m.group(1),
                                     fonte, tx))
                saida.append("")
                k += pula
                continue
            saida.append(tx.converte(b[1]))
        elif tipo == "tabela":
            raise Erro("%s: tabela sem título de quadro: %s"
                       % (nome, b[1][0][:60]))
        elif tipo == "imagem":
            grupo = [(b[1], b[2])]
            while (k + 1 < len(blocos) and blocos[k + 1][0] == "imagem"):
                k += 1
                grupo.append((blocos[k][1], blocos[k][2]))
            saida.append(_figura(grupo, tx))
        elif tipo == "lista":
            amb = "enumerate" if b[1] else "itemize"
            saida.append("\\begin{%s}" % amb)
            saida += ["\\item %s" % tx.converte(it) for it in b[2]]
            saida.append("\\end{%s}" % amb)
        elif tipo == "codigo":
            linhas = [_escapa(l).replace("→", r"$\rightarrow$")
                      .replace(" ", "~") for l in b[1]]
            saida.append("\\begin{center}\\small\\ttfamily\n%s\n\\end{center}"
                         % "\\\\\n".join(linhas))
        elif tipo == "citacao":
            texto = b[1]
            if texto.startswith("Capítulo da monografia"):
                k += 1
                continue   # nota de trabalho, não é texto da monografia
            if len(texto) < 250:
                saida.append("``%s''" % tx.converte(texto))
            else:
                saida.append("\\begin{citacao}\n%s\n\\end{citacao}"
                             % tx.converte(texto))
        saida.append("")
        k += 1
    return "\n".join(saida).rstrip() + "\n"


def _secao_md(md: str, titulo: str) -> list:
    i = md.index("\n## %s\n" % titulo)
    fim = md.find("\n## ", i + 4)
    return list(_blocos(md[i + 4 + len(titulo):fim if fim > 0 else None]))


def pre_textuais() -> dict:
    md = (FONTE / "00-pre-textuais.md").read_text(encoding="utf-8")
    tx = Texto({})
    saida = {}

    def resumo(titulo, rotulo_chave):
        pars, chave = [], None
        for b in _secao_md(md, titulo):
            m = re.fullmatch(r"\*\*(Palavras-chave|Keywords):\*\* (.+)", b[1])
            if m:
                chave = tx.converte(m.group(2))
            else:
                pars.append(tx.converte(b[1]))
        if len(pars) != 1 or not chave:
            raise Erro("%s: um parágrafo só e as palavras-chave" % titulo)
        return ("%s\n\n\\vspace{\\onelineskip}\n\\noindent\n\\textbf{%s:} %s\n"
                % (pars[0], rotulo_chave, chave))

    saida["resumo"] = resumo("Resumo", "Palavras-chave")
    saida["abstract"] = resumo("Abstract", "Keywords")
    pars = []
    for b in _secao_md(md, "Declaração de uso de inteligência artificial"):
        t = b[1]
        t = re.sub(r"\[preencher: ([^\]]+)\]",
                   lambda m: "\x01%s\x02" % m.group(1), t)
        t = tx.converte(t)
        t = re.sub("\x01(.+?)\x02", r"\\preencher{\1}", t)
        pars.append(t)
    saida["declaracao-ia"] = "\n\n".join(pars) + "\n"
    cab = ("% Gerado de docs/monografia/00-pre-textuais.md por "
           "scripts/monografia_latex.py.\n% Não edite aqui: edite o .md e "
           "gere de novo.\n\n")
    return {k: cab + v for k, v in saida.items()}


def gera() -> dict:
    todos = [c[0] for c in CAPITULOS + APENDICES]
    rotulos = _rotulos_do_texto(todos)
    arquivos = {}
    for nome, saida, numero in CAPITULOS:
        arquivos[saida + ".tex"] = capitulo(nome, numero, rotulos)
    for nome, saida, numero in APENDICES:
        arquivos[saida + ".tex"] = capitulo(nome, numero, rotulos,
                                            apendice=True)
    for chave, texto in pre_textuais().items():
        arquivos["00-%s.tex" % chave] = texto
    return arquivos


def main(argv) -> int:
    try:
        arquivos = gera()
    except Erro as e:
        print("monografia_latex: %s" % e, file=sys.stderr)
        return 2
    if "--confere" in argv:
        velhos = [n for n, t in arquivos.items()
                  if not (DESTINO / n).exists()
                  or (DESTINO / n).read_text(encoding="utf-8") != t]
        if velhos:
            print("desatualizados: %s" % velhos, file=sys.stderr)
            return 1
        return 0
    DESTINO.mkdir(parents=True, exist_ok=True)
    for n, t in arquivos.items():
        (DESTINO / n).write_text(t, encoding="utf-8", newline="\n")
    print("%d arquivos em %s" % (len(arquivos), DESTINO))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
