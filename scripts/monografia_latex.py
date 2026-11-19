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
APENDICES = [("apendice-protocolo.md", "apendice-a-protocolo", "A")]

FONTE_PADRAO_QUADRO = "Elaborado pelo autor."
FONTE_PADRAO_FIGURA = "Captura de tela do Structura, elaborada pelo autor."

# Cada citação do texto, na forma em que está escrita, e o que ela vira.
# Uma citação fora desta tabela faz o script parar (ver _sobra_citacao).
P = r"p\. ([\d:\-]+)"
CITACOES = [
    (r"\(POSNER et al\., 1982, " + P + r"\)", r"\\cite[p.~\1]{posner1982}"),
    (r"Posner et al\. \(1982, " + P + r"\)",
     r"\\citeonline[p.~\1]{posner1982}"),
    (r"\(QIAN; LEHMAN, 2017, " + P + r"\)", r"\\cite[p.~\1]{qian2017}"),
    (r"Qian e Lehman \(2017, " + P + r"\)", r"\\citeonline[p.~\1]{qian2017}"),
    (r"\(FALMAGNE et al\., 2006\)", r"\\cite{falmagne2006}"),
    (r"VanLehn \(2011, " + P + r"\)", r"\\citeonline[p.~\1]{vanlehn2011}"),
    (r"VanLehn \(2006\)", r"\\citeonline{vanlehn2006}"),
    (r"\(TIPPETT, 2010, p\. 965 apud NUSSBAUM; CORDOVA; REHMAT, 2017, "
     r"p\. 31\)",
     r"(TIPPETT, 2010, p.~965 \\textit{apud} NUSSBAUM; CORDOVA; REHMAT, "
     r"2017, p.~31)"),
    (r"\(NUSSBAUM; CORDOVA; REHMAT, 2017, " + P + r"\)",
     r"\\cite[p.~\1]{nussbaum2017}"),
    (r"\(SODERSTROM; BJORK, 2015, " + P + r"\)",
     r"\\cite[p.~\1]{soderstrom2015}"),
    # o abntex2 corta a partícula do sobrenome nas citações (MERRIËNBOER,
    # Boulay); nestes dois casos o nome vai por extenso e só o ano é citado
    (r"\(SWELLER; VAN MERRIËNBOER; PAAS, 2019\)",
     r"(SWELLER; VAN MERRIËNBOER; PAAS, \\citeyear{sweller2019})"),
    (r"\(W3C, 2025\)", r"\\cite{w3c2025}"),
    (r"Gardner-Medwin \(2006\)", r"\\citeonline{gardnermedwin2006}"),
    (r"White e Gunstone \(1992, cap\. (\d+)\)",
     r"\\citeonline[cap.~\1]{white1992}"),
    (r"Sorva \(2012\)", r"\\citeonline{sorva2012}"),
    (r"Summit \(1996\)", r"\\citeonline{summit1996}"),
    (r"du Boulay \(1986\)", r"du Boulay (\\citeyear{duboulay1986})"),
    (r"Soloway et al\. \(1982\)", r"\\citeonline{soloway1982}"),
    (r"Putnam et al\. \(1986\)", r"\\citeonline{putnam1986}"),
    (r"Sleeman et al\. \(1986\)", r"\\citeonline{sleeman1986}"),
    (r"Samurçay \(1989\)", r"\\citeonline{samurcay1989}"),
    (r"Holland et al\. \(1997\)", r"\\citeonline{holland1997}"),
    (r"Ma \(2007\)", r"\\citeonline{ma2007}"),
    (r"Doukakis et al\. \(2007\)", r"\\citeonline{doukakis2007}"),
    (r"Kaczmarczyk et al\. \(2010\)", r"\\citeonline{kaczmarczyk2010}"),
    (r"Kernighan e Ritchie(?! \()", r"\\citeonline{kernighan1988}"),
    (r"\(BROOKE, 1996\)", r"\\cite{brooke1996}"),
]
# Menções a obras que o texto discute sem citar como fonte, e que por isso
# não têm entrada na lista: ficam como texto. Conferir com o autor.
SEM_REFERENCIA = ["Hermans et al. (2018)", "TIPPETT, 2010"]

PADRAO_DE_CITACAO = re.compile(
    r"\b[A-ZÀ-Ý][A-ZÀ-Ý\-]{2,}(?: et al\.)?(?:; [A-ZÀ-Ý][A-ZÀ-Ý \-]+)*, "
    r"\d{4}|[A-Z][a-zà-ÿ\-]+(?: et al\.| e [A-Z][a-z]+)? \(\d{4}")


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

        for padrao, latex in CITACOES:
            t = re.sub(padrao, lambda m, l=latex: self._guarda(m.expand(l)), t)
        sobra = [m.group(0) for m in PADRAO_DE_CITACAO.finditer(t)
                 if not any(s.startswith(m.group(0)[:8]) for s in SEM_REFERENCIA)]
        if sobra:
            raise Erro("citação sem tradução: %s" % sobra)

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


def _figura(imagens, tx: Texto) -> str:
    """Uma imagem, ou um par 'a'/'b' que vira uma figura só."""
    def partes(alt):
        m = re.fullmatch(r"Figura (\d+\.\d+)([ab]?) — (.+)", alt)
        if not m:
            raise Erro("legenda de figura fora do padrão: %s" % alt)
        return m.group(1), m.group(2), m.group(3)
    num = partes(imagens[0][0])[0]
    if len(imagens) == 1:
        _, letra, leg = partes(imagens[0][0])
        arq = pathlib.PurePosixPath(imagens[0][1]).name
        corpo = ("\\includegraphics[width=.5\\textwidth,height=.55\\textheight,"
                 "keepaspectratio]{%s}" % arq)
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
                if m:
                    if int(m.group(1)) != subsecao:
                        raise Erro("%s: subseção %s fora de ordem"
                                   % (nome, m.group(1)))
                    titulo = m.group(2)
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
