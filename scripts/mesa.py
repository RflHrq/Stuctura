"""O teste de mesa, GERADO pela execução — não escrito à mão.

    python scripts/mesa.py --topico kc_02 --no B2
    python scripts/mesa.py --topico kc_02            # os seis nós

POR QUE ISTO EXISTE. O dono usou o sistema e disse três coisas sobre o
cartão de ensino: que está verborrágico, que é pouco ilustrado, e que
`printf("%p", (void *)&x)` é elaborado demais para quem está aprendendo
o que é um ponteiro. As três se resolvem com a mesma peça.

Uma tabela com o valor de cada variável depois de cada linha ensina,
sem uma palavra de prosa, o que o cartão do B2 gastava 565 palavras
tentando dizer: que `&x` e `&p` são números diferentes, que `p` vale o
mesmo que `&x`, e que `*p = 7` muda o x sem o nome x aparecer.

E O `(void *)` SAI DA TELA. Ele continua existindo — no programa
instrumentado que este script compila —, mas o aluno vê a tabela, não a
tubulação.

A TABELA NÃO É INVENTADA. Ela sai de um programa compilado e executado
pelo mesmo gcc que o projeto já usa como oráculo. É o padrão da casa: o
que a máquina não puder conferir não entra.

O QUE ELE RECUSA, e recusa alto: código com construto fora do subconjunto
que ele sabe sondar. Tabela errada é pior que tabela nenhuma, e um
gerador que chuta numa linha chuta em todas as variações dela.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI / "scripts"))

from mvp.dominio import carrega                      # noqa: E402

NL = chr(10)

# Tipos que o gerador sabe imprimir. Fora daqui ele recusa.
FORMATO = {"int": "%d", "char": "%c", "long": "%ld", "double": "%g",
           "float": "%g", "unsigned": "%u", "size_t": "%zu"}

# `int x = 42;` / `int x = 42, y = 7;` / `int *p = &x;` / `char *q;`
DECLARACAO = re.compile(
    r"^\s*(?P<tipo>unsigned\s+\w+|[A-Za-z_]\w*)\s+(?P<resto>[^;]+);\s*$")
# `x = 7;` / `*p = 9;` / `p = &y;`
ATRIBUICAO = re.compile(r"^\s*\*?\s*[A-Za-z_]\w*\s*=\s*[^;]+;\s*$")


# NOS QUE NAO LEVAM TABELA, e o motivo de cada um.
#
# A REGRA, achada gerando: a tabela serve ao no cujo ponto e o ESTADO
# mudando linha a linha. Nao serve ao no cujo ponto e o que SAI. Forcar
# uma tabela onde ela nao ensina e verborragia em forma de tabela, que e
# exatamente a reclamacao que fez esta peca existir.
SEM_TABELA = {
    ("kc_02", "I2"): "o ponto do I2 e o TIPO, e o que o ensina sao os dois "
                     "sizeof -- que sao saida, nao estado. A tabela gerada "
                     "tem 8 colunas e mostra quatro variaveis em enderecos "
                     "diferentes, que e o ponto do B2.",
}


class NaoSeiSondar(Exception):
    """O gerador achou construto que não sabe acompanhar."""


def _e_declaracao(linha: str):
    """A linha declara? `p = &y;` casava no padrao de declaracao com
    tipo `p`, e o gerador recusava o I1 inteiro por isso. Declaracao
    exige tipo CONHECIDO."""
    m = DECLARACAO.match(linha)
    if m and m.group("tipo") in FORMATO:
        return m
    return None


def _variaveis(linhas: list[str]) -> list[tuple[str, str, bool]]:
    """(nome, tipo, é_ponteiro) de cada variável declarada, na ordem."""
    achadas: list[tuple[str, str, bool]] = []
    for l in linhas:
        m = _e_declaracao(l)
        if not m:
            continue
        tipo = m.group("tipo")
        for parte in m.group("resto").split(","):
            parte = parte.strip()
            nome = re.match(r"\**\s*([A-Za-z_]\w*)", parte)
            if not nome:
                raise NaoSeiSondar("não achei o nome em %r" % parte)
            achadas.append((nome.group(1), tipo, parte.lstrip().startswith("*")))
    if not achadas:
        raise NaoSeiSondar("nenhuma variável declarada neste trecho")
    return achadas


def _executaveis(codigo: str) -> list[str]:
    """As linhas que MUDAM estado. `printf` sai: ele é saída, não estado,
    e é justamente o que a tabela vem substituir."""
    fora = []
    for l in codigo.splitlines():
        limpa = re.sub(r"/\*.*?\*/", "", l).strip()
        if not limpa or limpa.startswith("//"):
            continue
        # POR INSTRUCAO, nao por linha. O exemplo do I2 poe duas
        # declaracoes na mesma linha, em duas colunas, e isso se le bem
        # no cartao -- mas a tabela traca INSTRUCAO, e a primeira versao
        # do gerador recusava a linha inteira por causa disso.
        for pedaco in limpa.split(";"):
            s = pedaco.strip()
            if not s:
                continue
            s += ";"
            if s.startswith("printf") or s.startswith("puts"):
                continue
            if not (_e_declaracao(s) or ATRIBUICAO.match(s)):
                raise NaoSeiSondar("não sei sondar: %s" % s)
            fora.append(s)
    return fora


def _programa(linhas: list[str], vars_: list[tuple[str, str, bool]]) -> str:
    """O codigo do cartao, com uma sonda depois de cada linha.

    A SONDA SO CITA O QUE JA EXISTE. A primeira versao emitia a sonda
    completa depois de toda linha, e o programa nao compilava: na linha
    1 ela ja citava a variavel declarada na linha 2. Agora cada sonda
    imprime so as variaveis vivas naquele ponto, e a coluna das outras
    sai vazia -- que e o certo tambem para quem le a tabela: a variavel
    aparece quando passa a existir.
    """
    nomes = [n for n, _, _ in vars_]
    corpo = []
    vivas: list[str] = []
    for l in linhas:
        corpo.append("    " + l)
        m = _e_declaracao(l)
        if m:
            for parte in m.group("resto").split(","):
                n = re.match(r"\**\s*([A-Za-z_]\w*)", parte.strip())
                if n:
                    vivas.append(n.group(1))
        campos, args = [], []
        for nome, tipo, ponteiro in vars_:
            if nome not in vivas:
                campos.append("")
                campos.append("")
                continue
            campos.append("%p" if ponteiro else FORMATO[tipo])
            args.append("(void *)%s" % nome if ponteiro else nome)
            campos.append("%p")
            args.append("(void *)&%s" % nome)
        # `chr(92) + "n"` e a sequencia que vai para DENTRO da string de
        # C. Escrever a contrabarra direto aqui ja me custou tres
        # arquivos quebrados nesta sessao.
        fmt = "|".join(campos) + chr(92) + "n"
        if args:
            corpo.append('    printf("' + fmt + '", ' + ", ".join(args) + ");")
        else:
            corpo.append('    printf("' + fmt + '");')
    return ("#include <stdio.h>" + NL + "int main(void)" + NL + "{" + NL
            + NL.join(corpo) + NL + "    return 0;" + NL + "}" + NL)


def _gcc() -> pathlib.Path:
    from oraculo import GCC                          # type: ignore
    return pathlib.Path(GCC)


def gera(codigo: str) -> dict:
    """{colunas: [...], linhas: [{codigo, valores: [...]}]}"""
    linhas = _executaveis(codigo)
    vars_ = _variaveis(linhas)
    prog = _programa(linhas, vars_)
    gcc = _gcc()
    if not gcc.exists():
        raise NaoSeiSondar("não achei o compilador em %s" % gcc)
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "m.c").write_text(prog, encoding="utf-8")
        r = subprocess.run([str(gcc), "-std=c17", "-Wall", "-o", "m.exe",
                            "m.c"], capture_output=True, text=True,
                           timeout=10, cwd=str(p))
        if r.returncode != 0:
            dura = next((x for x in r.stderr.splitlines() if "error:" in x),
                        r.stderr.strip()[:120])
            raise NaoSeiSondar("o programa sondado não compila: %s" % dura)
        run = subprocess.run([str(p / "m.exe")], capture_output=True,
                             text=True, timeout=10, cwd=str(p))
    saidas = [l for l in run.stdout.splitlines() if l.strip()]
    if len(saidas) != len(linhas):
        raise NaoSeiSondar("sondei %d linhas e saíram %d"
                           % (len(linhas), len(saidas)))

    colunas = []
    for nome, _tipo, _pt in vars_:
        colunas.append(nome)
        colunas.append("&" + nome)
    tabela = []
    for l, saida in zip(linhas, saidas):
        tabela.append({"codigo": l, "valores": saida.split("|")})
    return {"colunas": colunas, "linhas": tabela}


def _curto(valor: str) -> str:
    """Endereço inteiro é ruído: o que ensina é QUAIS são iguais."""
    v = valor.strip()
    if re.fullmatch(r"0?[0-9A-Fa-f]{8,}", v) and len(v) > 6:
        return "…" + v[-4:].upper()
    return v


def imprime(no: str, t: dict) -> None:
    larg = [max(len(c), 8) for c in t["colunas"]]
    cab = max(len(l["codigo"]) for l in t["linhas"])
    print(NL + "== %s" % no)
    print("  %-*s  %s" % (cab, "linha",
                          "  ".join("%-*s" % (w, c)
                                    for w, c in zip(larg, t["colunas"]))))
    for l in t["linhas"]:
        print("  %-*s  %s" % (cab, l["codigo"],
                              "  ".join("%-*s" % (w, _curto(v))
                                        for w, v in zip(larg, l["valores"]))))


def escreve(topico: str, tabelas: dict) -> None:
    """Grava `testes_de_mesa` no activities do topico.

    INSERE texto, nao reescreve com yaml.dump: um round-trip apagaria
    todos os comentarios, que neste projeto sao a documentacao.
    """
    import json

    alvo = (AQUI / "mvp" / "dominio"
            / ("activities_%s.yaml" % topico.replace("_", "")))
    s = alvo.read_text(encoding="utf-8")
    fora = ["# ---------------------------------------------------------------------",
            "# O TESTE DE MESA, GERADO por scripts/mesa.py -- nao edite a mao.",
            "#",
            "# Cada linha e uma instrucao do exemplo do cartao, e cada coluna e uma",
            "# variavel ou o endereco dela. Os valores sairam de um programa",
            "# instrumentado, compilado e executado pelo gcc do projeto.",
            "#",
            "# `mvp/test_mesa.py` regenera e compara: se alguem mexer no exemplo e",
            "# nao regerar a tabela, a suite acusa. Tabela errada e pior que tabela",
            "# nenhuma, porque ela parece medida.",
            "#",
            "# E e ela que tira o (void *) da tela: o cast fica no programa",
            "# instrumentado, e o aluno ve o valor.",
            "# ---------------------------------------------------------------------",
            "", "testes_de_mesa:", ""]
    for no, t in tabelas.items():
        fora.append("  %s:" % no)
        fora.append("    colunas: %s" % json.dumps(t["colunas"],
                                                   ensure_ascii=False))
        fora.append("    linhas:")
        for l in t["linhas"]:
            fora.append("      - codigo: %s" % json.dumps(l["codigo"],
                                                          ensure_ascii=False))
            fora.append("        valores: %s" % json.dumps(l["valores"],
                                                           ensure_ascii=False))
        fora.append("")
    marca = NL + "activities:"
    assert s.count(marca) == 1, "nao achei `activities:`"
    i = s.index(marca)
    # Tira uma versao anterior, se houver -- E SO ELA.
    #
    # A primeira versao fatiava do comentario ate `activities:`, e comeu
    # o material de ensino que outro script tinha acabado de inserir
    # entre os dois. Agora o bloco termina na proxima CHAVE DE TOPO.
    antigo = s.find(NL + "testes_de_mesa:")
    if antigo != -1:
        cab = s.rfind("# ------", 0, antigo)
        ini = cab if cab != -1 else antigo + 1
        resto = s[antigo + 1:]
        m = re.search(r"^[a-z_]+:", resto[len("testes_de_mesa:"):], re.M)
        fim = (antigo + 1 + len("testes_de_mesa:") + m.start()) if m else len(s)
        s = s[:ini] + s[fim:]
        i = s.index(marca)
    alvo.write_text(s[:i + 1] + NL.join(fora) + NL + s[i + 1:],
                    encoding="utf-8")
    print("escrito em %s" % alvo.name)


def main() -> int:
    ap = argparse.ArgumentParser(description="teste de mesa gerado")
    ap.add_argument("--topico", required=True)
    ap.add_argument("--no", help="um nó; sem isto, todos do tópico")
    ap.add_argument("--escreve", action="store_true",
                    help="grava as tabelas no activities do tópico")
    args = ap.parse_args()
    d = carrega(topico=args.topico)
    alvos = [args.no] if args.no else list(d.ordem)
    falhou = 0
    tabelas: dict = {}
    for nid in alvos:
        if (args.topico, nid) in SEM_TABELA:
            print(NL + "== %s: SEM TABELA de propósito — %s"
                  % (nid, SEM_TABELA[(args.topico, nid)]))
            continue
        codigo = d.exemplo(nid)
        if not codigo.strip():
            print(NL + "== %s: sem exemplo" % nid)
            continue
        try:
            t = gera(codigo)
        except NaoSeiSondar as e:
            falhou += 1
            print(NL + "== %s: RECUSADO — %s" % (nid, e))
            continue
        imprime(nid, t)
        tabelas[nid] = t
    print(NL + "%d de %d recusados." % (falhou, len(alvos)))
    if args.escreve and tabelas:
        escreve(args.topico, tabelas)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
