"""O banco de questões contra o compilador.

    python scripts/confere_banco.py            # os treze tópicos
    python scripts/confere_banco.py kc_12      # um tópico

O conferidor das escadas (`confere_escada.py`) confere passos, exemplos e
demonstrações. Este confere a parte do banco que dá para conferir por
programa: as questões de PREVER A SAÍDA cuja alternativa certa começa por
um valor ("30: só o último valor escrito"). O código da questão é montado
num programa, compilado com o gcc do oráculo (`-std=c17 -Wall`), rodado
com limite de tempo, e a saída tem de ser aquele valor.

O QUE FICA DE FORA, e por quê: a alternativa certa que não é um valor
("Não dá para saber", "Talvez 7", "O endereço da própria variável p") não
se confere comparando texto — é leitura. E as questões de achar o erro e
de comparar casos são, muitas vezes, fragmentos que não formam programa
("caso 1" e "caso 2" lado a lado).

Também aqui mora a conferência de string partida: uma linha com aspas
ímpares é uma string que continua na linha de baixo. No kc_02, oito
questões tinham o `\\n` do `printf` virado quebra de linha de verdade.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import oraculo  # noqa: E402

TEMPO_COMPILA = 60
TEMPO_RODA = 10

_TIPO = (r"(?:static\s+)?(?:const\s+)?(?:unsigned\s+)?"
         r"(?:void|int|char|double|float|long|short|size_t|struct\s+\w+)")
_DEFINICAO = re.compile(r"^" + _TIPO + r"\s*\**\s*(\w+)\s*\(([^;]*)\)\s*\{")
_VOID_SEM_PARAMETRO = re.compile(r"^(?:static\s+)?void\s+(\w+)\s*\(\s*(?:void)?\s*\)")
_IMPRIME = re.compile(r"\b(?:printf|puts|putchar)\s*\(")

# O valor no começo da alternativa vem antes de ": ", de um travessão ou
# de ", porque". "15 e depois 16" é a saída de dois printf.
_SEPARADOR = re.compile(r"\s*(?::\s|—|–|,\s+porque\s|\s+porque\s)")
_NUMEROS = re.compile(r"-?\d+(?: -?\d+)*")


def linhas_com_string_partida(codigo: str) -> list[int]:
    """As linhas (contadas de 1) com um número ímpar de aspas duplas, fora
    de escape (`\\"`) e de literal de caractere (`'"'`)."""
    ruins = []
    for n, linha in enumerate(codigo.split("\n"), 1):
        limpa = re.sub(r"\\.", "", linha)
        limpa = re.sub(r"'[^'\\]'", "", limpa)
        if limpa.count('"') % 2:
            ruins.append(n)
    return ruins


def valor(texto: str) -> str | None:
    """O valor que a alternativa diz que sai, ou None se ela não começa
    por um valor numérico."""
    t = _SEPARADOR.split(texto.strip(), 1)[0]
    t = re.sub(r"\s+e depois\s+|,\s*depois\s+|\s+e\s+", " ", t)
    t = re.sub(r"\s+", " ", t.strip().strip("`").strip())
    return t if _NUMEROS.fullmatch(t) else None


def monta(codigo: str) -> str:
    """O trecho, dentro de um programa.

    As funções ficam fora do `main` — contando chaves, porque no banco a
    chave que fecha a função pode vir recuada. Um trecho que é só
    funções, sem nada para o `main` fazer, pressupõe a chamada ("O que
    sai?" de uma `void f(void)`): o `main` chama, na ordem, cada função
    `void` sem parâmetros. A que devolve valor fica de fora, porque é a
    outra que a chama — chamá-la também contaria uma vez a mais. Trecho
    que já traz o `main` entra como está.
    """
    cabeca = "#include <stdio.h>\n#include <stdlib.h>\n"
    if re.search(r"\bint\s+main\s*\(", codigo):
        return cabeca + codigo + "\n"
    fora, dentro, prof, sem_parametro = [], [], 0, []
    for linha in codigo.split("\n"):
        if prof > 0:
            fora.append(linha)
            prof += linha.count("{") - linha.count("}")
            continue
        definicao = _DEFINICAO.match(linha)
        if definicao:
            fora.append(linha)
            prof = linha.count("{") - linha.count("}")
            chamavel = _VOID_SEM_PARAMETRO.match(linha)
            if chamavel:
                sem_parametro.append(chamavel.group(1))
        else:
            dentro.append(linha)
    if not any(l.strip() for l in dentro):
        dentro = ["%s();" % nome for nome in sem_parametro]
    return (cabeca + "".join(l + "\n" for l in fora) + "int main(void) {\n"
            + "\n".join(dentro) + "\nreturn 0;\n}\n")


# As palavras que afirmam o que o compilador FAZ com o código. O verbo do
# projeto é "reclama" (docs/linguagem.md): a severidade muda entre versões.
_SEVERIDADE = re.compile(r"\b(recusa|recusam|não compila|nao compila|"
                         r"nem compila|é erro de compilação)\b", re.I)


def afirma_severidade(texto: str) -> bool:
    """O texto diz que o compilador recusa, ou que o código não compila?"""
    return bool(_SEVERIDADE.search(texto))


def falha_mesmo_permissivo(codigo: str) -> bool:
    """O trecho falha até com `-fpermissive -w`?

    O gcc 14 passou a tratar como erro conversões que antes eram aviso
    (`-Wint-conversion`, `-Wincompatible-pointer-types`), e `-fpermissive`
    as devolve a aviso. O que falha mesmo assim — atribuir a array, `&` de
    um número, nome não declarado — falha em qualquer gcc, e aí dizer
    "recusa" é verdade.
    """
    gcc = oraculo.GCC
    if not gcc.exists():
        raise oraculo.SemCompilador(
            "não achei o compilador em %s — aponte STRUCTURA_GCC para ele"
            % gcc)
    with tempfile.TemporaryDirectory() as tmp:
        pasta = pathlib.Path(tmp)
        (pasta / "o.c").write_text(monta(codigo), encoding="utf-8")
        r = subprocess.run(
            [str(gcc), "-std=c17", "-fpermissive", "-w", "-fsyntax-only",
             "o.c"], capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=TEMPO_COMPILA, cwd=str(pasta))
    return r.returncode != 0


def imprime(codigo: str) -> bool:
    """O trecho escreve na tela? Só então a saída diz alguma coisa."""
    return bool(_IMPRIME.search(codigo))


def roda(programa: str) -> tuple[bool, str]:
    """Compila e roda. (False, motivo) se não compilou ou não terminou."""
    gcc = oraculo.GCC
    if not gcc.exists():
        raise oraculo.SemCompilador(
            "não achei o compilador em %s — aponte STRUCTURA_GCC para ele"
            % gcc)
    with tempfile.TemporaryDirectory() as tmp:
        pasta = pathlib.Path(tmp)
        (pasta / "o.c").write_text(programa, encoding="utf-8")
        try:
            compilou = subprocess.run(
                [str(gcc), "-std=c17", "-Wall", "-o", "o.exe", "o.c"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=TEMPO_COMPILA, cwd=str(pasta))
            if compilou.returncode != 0:
                erro = next((l for l in compilou.stderr.splitlines()
                             if "error" in l), "não compilou")
                return False, erro.strip()
            rodou = subprocess.run(
                [str(pasta / "o.exe")], capture_output=True, text=True,
                timeout=TEMPO_RODA, cwd=str(pasta))
        except subprocess.TimeoutExpired:
            return False, "não terminou no tempo"
    return True, re.sub(r"\s+", " ", rodou.stdout).strip()


@dataclass(frozen=True)
class Problema:
    id: str
    certa: str
    saiu: str


def confere(d) -> list[Problema]:
    """As questões de prever a saída cuja alternativa certa é um valor e
    não sai esse valor."""
    problemas = []
    for a in d.atividades:
        if a.formato != "prever_saida" or not imprime(a.codigo):
            continue
        certa = next(o.texto for o in a.opcoes if o.correta)
        esperado = valor(certa)
        if esperado is None:
            continue
        ok, saiu = roda(monta(a.codigo))
        if not ok or saiu != esperado:
            problemas.append(Problema(a.id, certa, saiu))
    return problemas


def main(args: list[str] | None = None) -> int:
    from mvp.dominio import carrega, topicos
    alvos = (args if args else sys.argv[1:]) or list(topicos())
    total = 0
    for t in alvos:
        d = carrega(topico=t)
        partidas = [a.id for a in d.atividades
                    if linhas_com_string_partida(a.codigo)]
        problemas = confere(d)
        total += len(partidas) + len(problemas)
        print("== %s: %d string(s) partida(s), %d saída(s) que não batem"
              % (t, len(partidas), len(problemas)))
        for i in partidas:
            print("   string partida: %s" % i)
        for p in problemas:
            print("   %s: a certa diz %r, saiu %r" % (p.id, p.certa, p.saiu))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
