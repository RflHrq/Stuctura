"""O oráculo: compila o programa do molde, roda, e compara com o prometido.

    ok, nota = roda(programa, espera)

É o que transforma "confie no modelo" em "a máquina conferiu, uma por
uma", e é por isso que a revisão humana pode passar do item para o
molde. Sem ele, um molde escrito por modelo é texto sem conferência
nenhuma — e um molde errado erra em todas as variações de uma vez.

O caso que justifica tudo isto apareceu na sonda: um molde que afirmava
`sizeof a == n`, verdadeiro para `char` e falso para todo o resto. A
máquina reprovou 18 de 20 e aceitou exatamente as duas de `char`. É o
tipo de erro que passa batido numa revisão humana lendo o molde, e que o
compilador pega em três décimos de segundo.

DUAS ARMADILHAS DE AMBIENTE, as duas custaram uma rodada da sonda:

1. O `ld` do MinGW **não resolve o próprio prefixo quando há espaço no
   caminho**. O winget instala em `C:\\Users\\<nome>\\AppData\\...`, e aqui
   o nome tem espaço: nada linkava, com a mensagem *"cannot find
   C:/Users/Satya"*. Daí o padrão ser `C:\\Users\\Public\\gcc`.
2. Compilar com caminho ABSOLUTO de origem e destino esbarra no mesmo
   problema. Por isso tudo roda em pasta temporária, com nomes
   relativos e `cwd` na pasta.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile

# Onde procurar o compilador. `STRUCTURA_GCC` troca, para a máquina da
# coleta não precisar ter a mesma instalação desta.
GCC = pathlib.Path(os.environ.get("STRUCTURA_GCC")
                   or r"C:\Users\Public\gcc\mingw64\bin\gcc.exe")

# Programa que não termina não pode pendurar o gerador. Dez segundos é
# muito para um programa de dez linhas e pouco para a paciência de quem
# está esperando a expansão.
TEMPO = 10


class SemCompilador(Exception):
    """Não há gcc onde se procurou.

    Exceção e não reprovação: molde sem oráculo rodado não é molde
    reprovado, é molde não conferido, e os dois não podem sair iguais no
    relatório.
    """


def roda(programa: str, espera: str, gcc: pathlib.Path | None = None,
         timeout: int = TEMPO) -> tuple[bool, str]:
    """Compila, executa e compara a saída com `espera`.

    Devolve `(passou, nota)`. A nota existe para quem vai consertar o
    molde: ela diz o que saiu e o que o molde prometia, ou a primeira
    linha do compilador.
    """
    gcc = pathlib.Path(gcc) if gcc else GCC
    if not gcc.exists():
        raise SemCompilador(
            "não achei o compilador em %s — instale um gcc num caminho SEM "
            "espaço, ou aponte STRUCTURA_GCC para ele" % gcc)

    with tempfile.TemporaryDirectory() as tmp:
        pasta = pathlib.Path(tmp)
        (pasta / "o.c").write_text(programa, encoding="utf-8")
        # Timeout na compilação também: a restrição é "todo programa do
        # oráculo roda com timeout", e um gcc que não volta pendura o
        # gerador do mesmo jeito que um programa que não termina.
        try:
            compilou = subprocess.run(
                [str(gcc), "-std=c17", "-Wall", "-o", "o.exe", "o.c"],
                capture_output=True, text=True, timeout=timeout,
                cwd=str(pasta))
        except subprocess.TimeoutExpired:
            return False, "o compilador não voltou em %ds" % timeout
        if compilou.returncode != 0:
            # A primeira linha do gcc costuma ser contexto ("o.c: In
            # function 'main':"), e não o defeito. Quem conserta o molde
            # precisa da linha do `error:`.
            linhas = [l.strip() for l in compilou.stderr.splitlines() if l.strip()]
            dura = next((l for l in linhas if "error:" in l),
                        linhas[0] if linhas else "sem mensagem")
            return False, "não compilou: %s" % dura

        try:
            rodou = subprocess.run([str(pasta / "o.exe")], capture_output=True,
                                   text=True, timeout=timeout, cwd=str(pasta))
        except subprocess.TimeoutExpired:
            return False, ("não terminou em %ds — programa de oráculo que não "
                           "para não confere nada" % timeout)

        saiu = rodou.stdout.strip()
        if saiu == espera.strip():
            return True, saiu
        return False, "saiu %r, e o molde promete %r" % (saiu, espera.strip())
