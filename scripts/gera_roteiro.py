"""Gera docs/monografia/roteiro-de-conferencia.md.

O roteiro lista cada citação do texto da monografia, na ordem de leitura,
com a obra, a página e o arquivo a abrir em docs/monografia/fontes/. Serve
à leitura do autor: abrir a obra na página e ver se ela diz o que a frase
diz que ela diz.

    python scripts/gera_roteiro.py

As obras e a forma das citações vêm da mesma tabela que o conversor para
LaTeX usa (monografia_latex.OBRAS), de modo que uma citação que o
conversor traduz aparece aqui, e nenhuma outra.
"""

from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import monografia_latex as ml  # noqa: E402

MONO = RAIZ / "docs" / "monografia"
SAIDA = MONO / "roteiro-de-conferencia.md"

# (arquivo, título no roteiro, numeração das seções quando o .md não traz)
ARQUIVOS = [
    ("00-pre-textuais.md", "Pré-textuais: uso de IAG nesta pesquisa", None),
    ("01-introducao.md", "Seção 1: Introdução", None),
    ("02-fundamentacao.md", "Seção 2: Fundamentação teórica", None),
    ("03-sistema.md", "Seção 3: O sistema Structura", None),
    ("curadoria.md", "Seção 4: Curadoria do catálogo", 4),
    ("05-construcao-e-verificacao.md", "Seção 5: Construção e verificação", None),
    ("06-resultados-da-verificacao.md", "Seção 6: Resultados da verificação", None),
    ("07-limitacoes-e-trabalhos-futuros.md",
     "Seção 7: Limitações e trabalhos futuros", None),
    ("08-conclusao.md", "Seção 8: Conclusão", None),
    ("apendice-protocolo.md", "Apêndice A: Protocolo do estudo", None),
]

# Onde está o arquivo de cada obra, dentro de docs/monografia/fontes/.
ONDE = {
    "brooke1996": "brooke1996/sus_ahrq_wayback.pdf",
    "falmagne2006": "falmagne2006/Science_Behind_ALEKS.pdf",
    "gardnermedwin2006": "gardnermedwin2006/innovass7.pdf",
    "hermans2018": "hermans2018/hermans2018.pdf",
    "isoiec2011": "c11-n1570/n1570.pdf",
    "mitre2026": "cwe/ (CWE-252, CWE-415 e CWE-476, em HTML)",
    "nussbaum2017": "nussbaum2017/EJ1135295.pdf",
    "posner1982": "posner1982/Posner_Strike_Hewson_Gertzog.pdf",
    "qian2017": "qian2017/3077618.pdf",
    "schmellenkamp2023": "schmellenkamp2023/3545945.3569806.pdf",
    "sei2025": "certc/ (regras ERR33-C, EXP34-C, MEM30-C e MEM31-C, em HTML)",
    "soderstrom2015": "soderstrom2015/soderstrom_bjork_2015.pdf",
    "sorva2012": "sorva2012/isbn9789526046266.pdf",
    "sorva2013": "sorva2013/2483710.2483713.pdf",
    "summit2005": "cfaq/ (índices e perguntas do FAQ, em HTML)",
    "sweller2019": "sweller2019/sweller2019.pdf",
    "ufv2026": "ufv-diretrizes-ia/DIRETRIZES-IA.pdf",
    "vanlehn2006": "vanlehn2006/vanlehn2006behavior.pdf",
    "vanlehn2011": "vanlehn2011/EffectivenessOfTutoring_Vanlehn.pdf",
    "w3c2025": "w3c2025/WCAG21.html",
    "white1992": "white1992/capitulo3.html",
    "yamashita2017": "yamashita2017/yamashita2017.pdf",
}

ABREVIATURAS = ("et al.", "p.", "cap.", "n.", "v.", "art.", "S. l.", "s. l.",
                "ed.", "apud.")
MARCA = "\x00"


def _frases(paragrafo: str) -> list:
    """Parte o parágrafo em frases, sem partir em 'et al.' nem em 'p. 12'."""
    t = paragrafo
    for a in ABREVIATURAS:
        t = t.replace(a + " ", a[:-1] + MARCA + " ")
    partes = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"`*(])", t)
    return [p.replace(MARCA, ".") for p in partes]


def _citacoes(frase: str) -> list:
    """As citações da frase: (texto da citação, chave ou None, observação)."""
    achadas = []
    ocupado = []

    def livre(m):
        return not any(a < m.end() and m.start() < b for a, b in ocupado)

    def guarda(m, chave, obs=""):
        ocupado.append((m.start(), m.end()))
        achadas.append((m.start(), m.group(0), chave, obs))

    # 1. citação de citação: a obra aberta é a segunda
    for chave, ano, _, par in ml.OBRAS:
        # "(Tippett, 2010, p. 965 apud Nussbaum...)" ou "Ma (2007 apud ...)"
        padrao = (r"(?:[A-ZÀ-Ý][\wÀ-ÿ\-]+(?: et al\.)? )?\([^()]{1,80}? apud "
                  + re.escape(par) + ", " + re.escape(ano)
                  + ml.LOCALIZADOR + r"\)")
        for m in re.finditer(padrao, frase):
            if livre(m):
                guarda(m, chave, "citação indireta: a obra de dentro não "
                       "foi aberta; conferir na obra que a cita")
    # 2. autoria entre parênteses e autoria na frase
    for chave, ano, txt, par in ml.OBRAS:
        for padrao in (r"\(" + re.escape(par) + ", " + re.escape(ano)
                       + ml.LOCALIZADOR + r"\)",
                       re.escape(txt) + r" \(" + re.escape(ano)
                       + ml.LOCALIZADOR + r"\)"):
            for m in re.finditer(padrao, frase):
                if livre(m):
                    guarda(m, chave)
    # 3. estudos citados só por intermédio de Sorva (2012)
    for nome in sorted(ml.SEM_REFERENCIA):
        for m in re.finditer(re.escape(nome) + r" \(\d{4}\)", frase):
            if livre(m):
                guarda(m, None, "estudo não aberto, citado por intermédio "
                       "de Sorva (2012): conferir na Tabela A.1 da tese")
    return [a[1:] for a in sorted(achadas)]


def _linhas_do_pdf(nome: str, texto: str) -> list:
    """Só o que vai para o PDF: (título da seção, parágrafo)."""
    linhas = texto.splitlines()
    saida, secao = [], ""
    n2 = n3 = 0
    numero = dict((a, n) for a, _, n in ARQUIVOS)[nome]
    dentro = nome != "00-pre-textuais.md"
    for ln in linhas:
        if ln.startswith("#"):
            titulo = ln.lstrip("#").strip()
            if nome == "00-pre-textuais.md":
                dentro = titulo.startswith("Declaração de uso")
            if titulo.startswith("Referências deste capítulo"):
                break
            if numero and ln.startswith("## "):
                n2, n3 = n2 + 1, 0
                titulo = "%d.%d %s" % (numero, n2, titulo)
            elif numero and ln.startswith("### "):
                n3 += 1
                titulo = "%d.%d.%d %s" % (
                    numero, n2, n3, re.sub(r"^\d+\.\s*", "", titulo))
            if not ln.startswith("# "):
                secao = titulo
            continue
        if not dentro or ln.startswith(">") or not ln.strip():
            continue
        saida.append((secao, ln.strip()))
    return saida


def gera() -> str:
    blocos = []
    conta = {}
    sem_arquivo = 0
    for nome, titulo, _ in ARQUIVOS:
        texto = (MONO / nome).read_text(encoding="utf-8")
        itens = []
        ultima = None
        for secao, paragrafo in _linhas_do_pdf(nome, texto):
            for frase in _frases(paragrafo):
                for cit, chave, obs in _citacoes(frase):
                    if secao != ultima:
                        itens.append("")
                        itens.append("### %s" % (secao or "(abertura)"))
                        itens.append("")
                        ultima = secao
                    if chave:
                        conta[chave] = conta.get(chave, 0) + 1
                        onde = "abrir `fontes/%s`" % ONDE[chave]
                    else:
                        sem_arquivo += 1
                        onde = "sem arquivo"
                    if obs:
                        onde += " · " + obs
                    itens.append("- [ ] **%s** · %s" % (cit.strip(), onde))
                    itens.append("  > %s" % frase.strip())
        if itens:
            blocos.append("## %s" % titulo)
            blocos.extend(itens)
            blocos.append("")
    total = sum(conta.values())
    cab = [
        "# Roteiro de conferência das citações",
        "",
        "Gerado por `python scripts/gera_roteiro.py`. Não editar à mão: se o",
        "texto mudar, gerar de novo. Arquivo de trabalho, que não vai para o",
        "PDF.",
        "",
        "Cada item é uma citação do texto, na ordem de leitura: a obra e a",
        "página, o arquivo a abrir em `docs/monografia/fontes/` e a frase em",
        "que a citação aparece. A conferência é abrir a obra na página e ver",
        "se ela diz o que a frase diz que ela diz. O que cada obra sustenta,",
        "segundo a conferência anterior, está em",
        "[conferencia-das-referencias.md](conferencia-das-referencias.md).",
        "",
        "São %d itens: %d citações de %d obras abertas e %d menções a"
        % (total + sem_arquivo, total, len(conta), sem_arquivo),
        "estudos que não foram abertos, citados por intermédio de outra",
        "obra.",
        "",
        "| Obra (chave) | Citações | Arquivo em `fontes/` |",
        "| --- | --- | --- |",
    ]
    for chave, _, txt, _ in ml.OBRAS:
        cab.append("| %s (`%s`) | %d | `%s` |" % (
            txt, chave, conta.get(chave, 0), ONDE[chave]))
    cab.append("")
    return "\n".join(cab + blocos) + "\n"


def main() -> int:
    faltam = [c for c, _, _, _ in ml.OBRAS if c not in ONDE]
    if faltam:
        print("obra sem arquivo declarado em ONDE: %s" % faltam)
        return 1
    SAIDA.write_text(gera(), encoding="utf-8", newline="\n")
    print("escrito: %s" % SAIDA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
