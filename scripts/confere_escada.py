"""O compilador como juiz da escada, e a escada em texto corrido.

    python scripts/confere_escada.py kc_00            # confere; sai com 1 se houver problema
    python scripts/confere_escada.py kc_00 --leitura  # imprime a escada para leitura

A sessão da trilha corrige uma resposta produzida SEM compilador: a
sequência de peças bate, ou não, com o que o conteúdo previu
(`mvp/trilha_escada.corrige`). Então o que o conteúdo previu tem de
estar certo antes de chegar a alguém:

  - toda linha que um degrau chama de certa COMPILA;
  - toda linha que um retorno chama de inválida é RECUSADA;
  - todo valor que um degrau de `digitar` espera é o que o programa
    IMPRIME.

É a mesma regra das provas da refutação — nada é afirmado sobre código
que a máquina não conferiu —, levada aos exercícios.

E ÀS PROVAS DA ESCADA, que são a refutação escrita para quem está
aprendendo: o que a prova diz que o programa imprime, ele imprime; o que
ela diz que o compilador reclama, ele reclama.

SÓ O `digitar`, A REVISÃO COM SAÍDA E A PROVA QUE IMPRIME SÃO
EXECUTADOS. Todo o resto é só compilado, e isso é decisão: o kc_00
mostra, para a pessoa escolher o que NÃO fazer, trechos que leem
variável sem valor — e a prova de duas das crenças dele É o aviso do
compilador sobre um trecho desses. Compilá-los prova o que o conteúdo
afirma; rodá-los seria o comportamento indefinido que o tópico ensina a
evitar.

A LEITURA existe porque o conteúdo só entra depois de alguém ler, e ler
YAML não é ler texto: ela põe frases, exercício, resposta certa e
retornos na ordem em que a pessoa os encontra.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Mapping

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import oraculo  # noqa: E402

from mvp import trilha_escada  # noqa: E402
from mvp.dominio import Dominio, carrega  # noqa: E402
from mvp.trilha_escada import (  # noqa: E402
    ENDERECO_DE_EXEMPLO, LACUNA, Degrau, Escada, Prova, Versao, faltando, le)

DOMINIO = RAIZ / "mvp" / "dominio"

# O limite de cada processo que o conferidor abre: compilar, só compilar,
# rodar — inclusive os que ele abre pelo `oraculo.roda`. É próprio, e
# mais folgado que os 10 s do oráculo: na suíte inteira, com a máquina
# carregada, um programa de três linhas (`malloc`, `printf`, `free`)
# passou dos 10 s no kc_01 e no kc_06, e não era laço — era o Windows
# olhando o executável novo. O conferidor é verificação de autoria, não
# espera de ninguém; 60 s ainda acusa o programa que não para.
TEMPO_CONFERE = 60


def arquivo_da_escada(topico: str) -> pathlib.Path:
    """`kc_00` -> `mvp/dominio/escada_kc00.yaml`."""
    return DOMINIO / ("escada_%s.yaml" % topico.replace("_", ""))


# Uma função inteira numa linha só: `void zera(int *q) { *q = 0; }`. Foi
# a única forma de função da escada até o kc_07.
FUNCAO = re.compile(r"^\s*(void|int|char)\s+\*?\s*\w+\s*\([^;{]*\)\s*\{.*\}\s*$")

# A mesma função escrita em várias linhas, que entrou com o kc_01: vai da
# linha que começa na margem com o tipo e termina em `{` até o `}`
# sozinho, também na margem. O `if` e o que mais abrir chave dentro do
# trecho não casa: não começa com tipo e nome de função.
ABRE_FUNCAO = re.compile(r"^(void|int|char)\s+\*?\s*\w+\s*\([^;{]*\)\s*\{\s*$")
FECHA_FUNCAO = re.compile(r"^\}\s*$")


def programa_de(antes: str, linhas: str) -> str:
    """As linhas, dentro de um `main` que o compilador aceita.

    A LINHA DE FUNÇÃO FICA FORA DO `main`. O trecho que a pessoa lê traz
    a função em cima e o resto embaixo, sem `main` nenhum; em C, função
    não se define dentro de outra — o gcc aceita por extensão, e conferir
    o conteúdo contra uma extensão seria conferir outra linguagem.
    """
    corpo = "\n".join(parte.strip("\n") for parte in (antes, linhas)
                      if parte and parte.strip())
    fora, dentro, aberta = [], [], False
    for l in corpo.split("\n"):
        if aberta:
            fora.append(l)
            aberta = not FECHA_FUNCAO.match(l)
        elif FUNCAO.match(l):
            fora.append(l)
        elif ABRE_FUNCAO.match(l):
            fora.append(l)
            aberta = True
        else:
            dentro.append(l)
    # <stdlib.h> entrou com o kc_01: é onde moram `malloc` e `free`. O
    # trecho que a pessoa lê não traz `#include` nenhum, nem este.
    return ("#include <stdio.h>\n#include <stdlib.h>\n"
            "%sint main(void) {\n%s\nreturn 0;\n}\n"
            % ("".join(l + "\n" for l in fora), "\n".join(dentro)))


def compila(programa: str) -> tuple[bool, str]:
    """Só compila. NUNCA executa: ver o cabeçalho do módulo."""
    gcc = oraculo.GCC
    if not gcc.exists():
        raise oraculo.SemCompilador(
            "não achei o compilador em %s — aponte STRUCTURA_GCC para ele"
            % gcc)
    with tempfile.TemporaryDirectory() as tmp:
        pasta = pathlib.Path(tmp)
        (pasta / "o.c").write_text(programa, encoding="utf-8")
        try:
            saiu = subprocess.run(
                [str(gcc), "-std=c17", "-Wall", "-fsyntax-only", "o.c"],
                capture_output=True, text=True, timeout=TEMPO_CONFERE,
                cwd=str(pasta))
        except subprocess.TimeoutExpired:
            return False, "o compilador não voltou em %ds" % TEMPO_CONFERE
    linhas = [l.strip() for l in saiu.stderr.splitlines() if l.strip()]
    nota = next((l for l in linhas if "error:" in l),
                linhas[0] if linhas else "")
    return saiu.returncode == 0, nota


def diz(programa: str, avisos: tuple[str, ...] = ()) -> str:
    """O que o compilador DIZ do programa. Compila, e NUNCA executa.

    Não é `-fsyntax-only`: o aviso de variável lida sem valor só sai
    quando o compilador analisa o fluxo, e para isso ele precisa gerar o
    objeto (`-c`). O objeto fica na pasta temporária e ninguém o roda.

    `avisos` são opções a mais, para o aviso que só sai com elas. Quem
    lê a escada já recusou o que não está na lista permitida.
    """
    gcc = oraculo.GCC
    if not gcc.exists():
        raise oraculo.SemCompilador(
            "não achei o compilador em %s — aponte STRUCTURA_GCC para ele"
            % gcc)
    with tempfile.TemporaryDirectory() as tmp:
        pasta = pathlib.Path(tmp)
        (pasta / "o.c").write_text(programa, encoding="utf-8")
        try:
            # A saída é lida como UTF-8, e não na codificação da máquina: o
            # analisador de fluxo desenha o caminho do programa com
            # caracteres que o cp1252 do Windows não tem.
            saiu = subprocess.run(
                [str(gcc), "-std=c17", "-Wall", *avisos,
                 "-c", "-o", "o.o", "o.c"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=TEMPO_CONFERE, cwd=str(pasta))
        except subprocess.TimeoutExpired:
            return ""
    return saiu.stderr


def _saida(programa: str) -> tuple[bool, str]:
    """Compila e executa, e devolve o que saiu. Com timeout nas duas."""
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
                capture_output=True, text=True, timeout=TEMPO_CONFERE,
                cwd=str(pasta))
            if compilou.returncode != 0:
                return False, "não compilou"
            rodou = subprocess.run(
                [str(pasta / "o.exe")], capture_output=True, text=True,
                timeout=TEMPO_CONFERE, cwd=str(pasta))
        except subprocess.TimeoutExpired:
            return False, "não terminou em %ds" % TEMPO_CONFERE
    return True, rodou.stdout.strip()


def mesma_forma(espera: str, saiu: str) -> bool:
    """A saída tem a forma da esperada, a menos dos endereços?

    Na esperada, `0x1000` e `0x2A00` são endereços DE EXEMPLO: o número
    de um lugar muda a cada máquina. O que tem de bater é o resto do
    texto, e a relação entre os endereços — exemplo repetido é o mesmo
    endereço na saída, exemplos diferentes são endereços diferentes.
    """
    pedacos, grupos, ultimo = [], {}, 0
    for achado in ENDERECO_DE_EXEMPLO.finditer(espera):
        pedacos.append(re.escape(espera[ultimo:achado.start()]))
        nome = grupos.get(achado.group(0))
        if nome is None:
            nome = grupos[achado.group(0)] = "e%d" % len(grupos)
            pedacos.append(r"(?P<%s>(?:0x)?[0-9A-Fa-f]+)" % nome)
        else:
            pedacos.append("(?P=%s)" % nome)
        ultimo = achado.end()
    pedacos.append(re.escape(espera[ultimo:]))
    casou = re.fullmatch("".join(pedacos), saiu)
    if casou is None:
        return False
    valores = [casou.group(nome).lower() for nome in grupos.values()]
    return len(set(valores)) == len(valores)


def _confere_prova(onde: str, p: Prova, problemas: list[str]) -> None:
    programa = programa_de("", p.programa)
    if p.espera and ENDERECO_DE_EXEMPLO.search(p.espera):
        ok, saiu = _saida(programa)
        if not ok or not mesma_forma(p.espera, saiu):
            problemas.append("%s: o programa não imprime o que a prova diz "
                             "— saiu %r, e a forma esperada é %r"
                             % (onde, saiu, p.espera))
        return
    if p.espera:
        ok, nota = oraculo.roda(programa, p.espera,
                                timeout=TEMPO_CONFERE)
        if not ok:
            problemas.append("%s: o programa não imprime o que a prova diz "
                             "— %s" % (onde, nota))
        return
    # A prova é o que o compilador diz. O programa não é executado: pode
    # ser justamente o que o tópico ensina a não fazer.
    reclamacoes = [l for l in diz(programa, p.avisos).splitlines()
                   if "warning:" in l or "error:" in l]
    # DE UMA LINHA SÓ. A tela diz "o compilador reclama desta linha"; a
    # mesma mensagem saindo de duas seria a prova dizer menos do que
    # aconteceu.
    com_ela = [l for l in reclamacoes if p.reclama in l]
    if not com_ela:
        problemas.append("%s: o compilador não reclama com %r"
                         % (onde, p.reclama))
    elif len(com_ela) > 1:
        problemas.append("%s: o compilador reclama com %r de %d linhas, e a "
                         "prova fala de uma" % (onde, p.reclama, len(com_ela)))
    if p.cala and any(p.cala in l for l in reclamacoes):
        problemas.append("%s: o compilador diz %r, e a prova afirma que ele "
                         "deveria calar isso" % (onde, p.cala))


def linha_de(v: Versao, sequencia: tuple[int, ...]) -> str:
    """A linha que uma resposta forma.

    Em `completar`, a peça entra no lugar da lacuna. Nas outras formas as
    peças são unidas por espaço — `int nota ;` é o mesmo C que
    `int nota;`, e o compilador é quem decide.
    """
    if LACUNA in v.mostra:
        return v.mostra.replace(LACUNA, v.pecas[sequencia[0]])
    return " ".join(v.pecas[i] for i in sequencia)


def programa_do_digitar(v: Versao) -> str:
    """O programa que um degrau de `digitar` roda.

    Vindo só o trecho em `mostra`, ele é embrulhado aqui: o que a pessoa
    lê e o que o compilador roda saem do mesmo texto.
    """
    return v.programa if v.programa.strip() else programa_de(v.antes, v.mostra)


def _deve(compilar: bool, onde: str, v: Versao, linha: str,
          problemas: list[str]) -> None:
    ok, nota = compila(programa_de(v.antes, linha))
    if compilar and not ok:
        problemas.append("%s: dita certa e não compila: %r — %s"
                         % (onde, linha, nota))
    if not compilar and ok:
        problemas.append("%s: dita inválida e compila: %r" % (onde, linha))


def _confere_versao(onde: str, g: Degrau, v: Versao,
                    problemas: list[str]) -> None:
    if g.forma == "digitar":
        ok, nota = oraculo.roda(programa_do_digitar(v), v.aceitas[0],
                                timeout=TEMPO_CONFERE)
        if not ok:
            problemas.append("%s: a resposta aceita não é o que o programa "
                             "imprime — %s" % (onde, nota))
        return
    if g.forma == "tocar":
        _deve(True, onde, v, v.mostra or " ".join(v.pecas), problemas)
        return
    if g.forma == "escolher":
        for i, opcao in enumerate(v.pecas):
            _deve(i not in v.invalidas, onde, v, opcao, problemas)
        return
    # montar e completar: as respostas aceitas compilam, e os erros
    # marcados como inválidos não.
    for s in v.certa:
        _deve(True, onde, v, linha_de(v, s), problemas)
    for x in v.erros:
        if x.invalida and x.exata:
            _deve(False, onde, v, linha_de(v, x.exata), problemas)


def confere(escadas: Mapping[str, Escada]) -> list[str]:
    """Os problemas que o compilador achou. Lista vazia: passou."""
    problemas: list[str] = []
    for premissa, e in escadas.items():
        for g in e.degraus:
            if not g.codigo:
                continue
            for k, v in enumerate(g.versoes):
                _confere_versao("%s/%s/versão %d" % (premissa, g.id, k + 1),
                                g, v, problemas)
        r = e.revisao
        programa = programa_de("", r.codigo)
        if r.saida:
            ok, nota = oraculo.roda(programa, r.saida,
                                    timeout=TEMPO_CONFERE)
            if not ok:
                problemas.append("%s: a revisão não imprime o que diz — %s"
                                 % (premissa, nota))
        else:
            ok, nota = compila(programa)
            if not ok:
                problemas.append("%s: o código da revisão não compila — %s"
                                 % (premissa, nota))
        for p in e.provas:
            _confere_prova("%s/prova de %s" % (premissa, p.crenca), p,
                           problemas)
        if e.cena is not None:
            _confere_cena("%s/cena" % premissa, r, e.cena, problemas)
    return problemas


def _texto_c(texto: str) -> str:
    """O texto dentro das aspas de um fprintf: sem quebrar a string."""
    return (texto.replace("\\", "\\\\").replace('"', '\\"')
            .replace("%", "%%"))


def _indices(plano: int, tamanho: tuple[int, ...]) -> str:
    """O índice achatado de volta em `[i]` ou `[i][j]`."""
    if len(tamanho) == 2:
        return "[%d][%d]" % divmod(plano, tamanho[1])
    return "[%d]" % plano


def _endereco(vivos: dict, texto: str) -> str | None:
    """O endereço de um alvo, pelo endereço guardado do ator. None: o alvo
    não existe mais ou o bloco foi devolvido (e aí nada é comparado)."""
    nome, idx = trilha_escada.ref(texto)
    v = vivos.get(nome)
    if v is None or v.devolvido:
        return None
    if not idx:
        return "cena_e_%s" % nome
    plano = 0
    for i, k in zip(idx, v.ator.tamanho):
        plano = plano * k + i
    return "(void *)(((%s *)cena_e_%s) + %d)" % (v.ator.tipo_c, nome, plano)


def _afirmacoes(vivos: dict, pode) -> list[tuple[str, str]]:
    """O que a cena afirma naquele ponto, em C: (condição, como se lê).

    Tudo pelo ENDEREÇO GUARDADO do ator (`cena_e_x`), e não pelo nome: a
    conferência vale dentro da bancada e fora dela, e no monte, onde a
    caixa não tem nome. `pode(nome)` diz se o endereço já foi guardado
    quando aquele ponto roda.

    Valor de caixa que tem valor, ponteiro apontando para quem, NULL.
    Caixa sem valor não é lida (ler seria o que o tópico ensina a não
    fazer), bloco devolvido não é lido nem comparado, e endereço nunca é
    conferido pelo número."""
    saida = []
    for nome, v in vivos.items():
        a = v.ator
        if not pode(nome) or v.devolvido:
            continue
        if a.tipo == "ponteiro":
            if v.aponta is None or v.solto:
                continue
            onde = "*(%s *)cena_e_%s" % (a.tipo_c, nome)
            if v.aponta == "":
                saida.append(("%s == NULL" % onde, "%s == NULL" % nome))
                continue
            alvo = _endereco(vivos, v.aponta)
            if alvo is None or not pode(trilha_escada.ref(v.aponta)[0]):
                continue
            saida.append(("%s == (%s)(%s)" % (onde, a.tipo_c, alvo),
                          "%s == &%s" % (nome, v.aponta)))
            continue
        for i, valor in enumerate(v.valor):
            if valor is None:
                continue
            if a.tamanho:
                saida.append(("((%s *)cena_e_%s)[%d] == (%s)" % (a.tipo_c, nome, i, valor),
                              "%s%s == %s" % (nome, _indices(i, a.tamanho), valor)))
            else:
                saida.append(("*(%s *)cena_e_%s == (%s)" % (a.tipo_c, nome, valor),
                              "%s == %s" % (nome, valor)))
    return saida


def _visitas(cena, momentos) -> dict:
    """Onde cada passo da cena cai no programa, e quantas vezes.

    Um PONTO é ("linha", n) — logo depois da linha n (antes, se ela é um
    `return` ou o fecho da função; na função de uma linha, antes do
    `return` ou do `}`) — ou ("entra", f), o começo do corpo de f. A
    mesma linha roda de novo quando a função é chamada de novo: cada
    passagem é uma VISITA, e cada visita confere o seu estado.

    Devolve {(ponto, k): {"passos": [s...], "ultimo": s | None,
    "linha": n, "acoes": [(s, acao, arg)...]}}."""
    contagem: dict = {}
    ultimo_ponto: dict[int, tuple] = {}
    visitas: dict = {}

    def visita(ponto, profundidade):
        if ultimo_ponto.get(profundidade) != ponto:
            contagem[ponto] = contagem.get(ponto, 0) + 1
            ultimo_ponto[profundidade] = ponto
        chave = (ponto, contagem[ponto])
        return visitas.setdefault(chave, {"passos": [], "ultimo": None,
                                          "linha": 0, "acoes": []})

    for s, p in enumerate(cena.passos):
        antes = len(momentos[s - 1].pilha) if s else 0
        chama = next((i for i, (a, _) in enumerate(p.faz) if a == "chama"), None)
        if chama is None:
            v = visita(("linha", p.linha), len(momentos[s].pilha))
            v["passos"].append(s)
            v["ultimo"], v["linha"] = s, p.linha
            v["acoes"] += [(s, a, x) for a, x in p.faz]
            continue
        # O passo que chama: o que vem antes do `chama` é da linha de quem
        # chama, e o resto já é da bancada. O estado deste passo não é
        # conferido na linha de quem chama — lá ele roda depois da volta.
        v = visita(("linha", p.linha), antes)
        v["passos"].append(s)
        v["linha"] = p.linha
        v["acoes"] += [(s, a, x) for a, x in p.faz[:chama]]
        ponto = ("entra", p.faz[chama][1])
        contagem[ponto] = contagem.get(ponto, 0) + 1
        ultimo_ponto[antes + 1] = ponto
        visitas[(ponto, contagem[ponto])] = {
            "passos": [s], "ultimo": s, "linha": p.linha,
            "acoes": [(s, a, x) for a, x in p.faz[chama + 1:]]}
    return visitas


def _nome_do_ponto(ponto) -> str:
    return "cena_v_%s" % ("l%d" % ponto[1] if ponto[0] == "linha" else "e_" + ponto[1])


def programa_da_cena(r, cena) -> str:
    """O código da revisão com, em cada ponto por onde a cena passa, o que
    ela afirma ali. A afirmação que falha sai em stderr, com a linha e o
    que a cena dizia; e no fim do `main`, quantas vezes o programa passou
    por cada ponto — a cena que conta outra história de chamadas (a
    função que não roda, a que roda duas vezes) também é acusada."""
    codigo = r.codigo.rstrip("\n")
    linhas = codigo.split("\n")
    papeis = trilha_escada.estrutura(codigo)
    momentos = trilha_escada.toca(cena, codigo)
    visitas = _visitas(cena, momentos)
    atores = {a.nome: a for a in cena.atores}

    # Quando roda cada visita (o último passo dela), e quando o endereço
    # de cada encarnação de cada ator é guardado.
    roda = {chave: max(v["passos"]) for chave, v in visitas.items()}
    guardado: dict[str, list[tuple[int, int]]] = {}   # nome -> [(passo, roda)]
    for chave, v in visitas.items():
        for s0, acao, arg in v["acoes"]:
            nome = arg if acao == "cria" else (arg[0] if acao == "aluga" else None)
            if nome:
                guardado.setdefault(nome, []).append((s0, roda[chave]))

    def codigo_do_ponto(ponto) -> list[str]:
        chaves = sorted(k for k in visitas if k[0] == ponto)
        if not chaves:
            return []
        saida = ["%s++;" % _nome_do_ponto(ponto)]
        for chave in chaves:
            v = visitas[chave]
            corpo = []
            for _, acao, arg in v["acoes"]:
                if acao == "cria":
                    corpo.append("cena_e_%s = (void *)&%s;" % (arg, arg))
                elif acao == "aluga":
                    corpo.append("cena_e_%s = (void *)*(%s *)cena_e_%s;"
                                 % (arg[0], atores[arg[1]].tipo_c, arg[1]))
            if v["ultimo"] is not None:
                s, quando = v["ultimo"], roda[chave]

                def pode(nome, s=s, quando=quando):
                    feitos = [q for p0, q in guardado.get(nome, ()) if p0 <= s]
                    return bool(feitos) and feitos[-1] <= quando

                for cond, diz in _afirmacoes(momentos[s].vivos, pode):
                    corpo.append(
                        'if (!(%s)) fprintf(stderr, "@@ linha %d: a cena diz %s, '
                        'e o programa não\\n");' % (cond, v["linha"], _texto_c(diz)))
            saida.append("if (%s == %d) {" % (_nome_do_ponto(ponto), chave[1]))
            saida += corpo
            saida.append("}")
        return saida

    fora, dentro = [], []
    for i, (l, papel) in enumerate(zip(linhas, papeis), 1):
        ponto = codigo_do_ponto(("linha", i))
        if papel.papel == "main":
            dentro += [l] + ponto
        elif papel.papel == "uma":
            a, b = l.index("{"), l.rindex("}")
            corpo = l[a + 1:b]
            ret = list(re.finditer(r"\breturn\b", corpo))
            corte = ret[-1].start() if ret else len(corpo)
            fora += ([l[:a + 1]] + codigo_do_ponto(("entra", papel.funcao))
                     + [corpo[:corte]] + ponto + [corpo[corte:], l[b:]])
        elif papel.papel == "abre":
            fora += [l] + codigo_do_ponto(("entra", papel.funcao))
        elif papel.papel == "fecha" or l.strip().startswith("return"):
            fora += ponto + [l]
        else:
            fora += [l] + ponto

    contagem: dict = {}
    for ponto, k in visitas:
        contagem[ponto] = max(contagem.get(ponto, 0), k)
    fim = []
    for ponto, k in sorted(contagem.items()):
        nome = _nome_do_ponto(ponto)
        lugar = ("linha %d" % ponto[1] if ponto[0] == "linha"
                 else "a entrada de %s" % ponto[1])
        fim.append('if (%s != %d) fprintf(stderr, "@@ %s: a cena passa %d vez(es) '
                   'por aqui, e o programa passou %%d\\n", %s);'
                   % (nome, k, lugar, k, nome))

    globais = ["static void *cena_e_%s;" % a.nome for a in cena.atores
               if a.tipo != "bancada"]
    globais += ["static int %s;" % _nome_do_ponto(p) for p in sorted(contagem)]
    return ("#include <stdio.h>\n#include <stdlib.h>\n%s\n%s\n"
            "int main(void) {\n%s\n%s\nreturn 0;\n}\n"
            % ("\n".join(globais), "\n".join(fora), "\n".join(dentro),
               "\n".join(fim)))


def _confere_cena(onde: str, r, cena, problemas: list[str]) -> None:
    """A cena contra o compilador (docs/interface.md, seção 8.3)."""
    mostra ="\n".join(arg for p in cena.passos for acao, arg in p.faz
                       if acao == "mostra")
    if mostra.strip() != r.saida.strip():
        problemas.append("%s: o que a cena mostra (%r) não é a saída da "
                         "revisão (%r)" % (onde, mostra, r.saida))
    gcc = oraculo.GCC
    if not gcc.exists():
        raise oraculo.SemCompilador(
            "não achei o compilador em %s — aponte STRUCTURA_GCC para ele"
            % gcc)
    with tempfile.TemporaryDirectory() as tmp:
        pasta = pathlib.Path(tmp)
        (pasta / "o.c").write_text(programa_da_cena(r, cena), encoding="utf-8")
        try:
            compilou = subprocess.run(
                [str(gcc), "-std=c17", "-Wall", "-o", "o.exe", "o.c"],
                capture_output=True, text=True, timeout=TEMPO_CONFERE,
                cwd=str(pasta))
            if compilou.returncode != 0:
                problemas.append("%s: o programa da cena não compila — %s"
                                 % (onde, compilou.stderr.strip()[:200]))
                return
            # As mensagens "@@" foram escritas em UTF-8 no programa: lidas
            # na codificação da máquina, o "não" chegava estragado.
            rodou = subprocess.run(
                [str(pasta / "o.exe")], capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=TEMPO_CONFERE, cwd=str(pasta))
        except subprocess.TimeoutExpired:
            problemas.append("%s: o programa da cena não terminou" % onde)
            return
    for l in rodou.stderr.splitlines():
        if l.startswith("@@ "):
            problemas.append("%s: %s" % (onde, l[3:]))
    if rodou.stdout.strip() != r.saida.strip():
        problemas.append("%s: com as afirmações no meio, a saída mudou: %r"
                         % (onde, rodou.stdout))


# --------------------------------------------------------------------------
# A leitura
# --------------------------------------------------------------------------

def _bloco(codigo: str) -> list[str]:
    return ["```c"] + codigo.strip("\n").split("\n") + ["```"]


def _resposta(g: Degrau, v: Versao, x) -> str:
    if g.forma == "digitar":
        return "digitou `%s`" % x.texto
    if x.exata:
        return "respondeu `%s`" % linha_de(v, x.exata)
    return "não usou %s" % " nem ".join("`%s`" % v.pecas[i] for i in x.sem)


def _versao_em_texto(g: Degrau, k: int, v: Versao) -> list[str]:
    saida = ["", "**Versão %d.** %s" % (k + 1, v.pede), ""]
    if v.antes.strip():
        saida += ["Já está escrito:", ""] + _bloco(v.antes) + [""]
    if g.forma == "digitar":
        saida += _bloco(v.mostra if v.mostra.strip() else v.programa) + [""]
    elif v.mostra.strip():
        saida += _bloco(v.mostra) + [""]
    if v.pecas:
        uma, varias = (("Opção", "Opções") if g.forma == "escolher"
                       else ("Peça", "Peças"))
        if any("\n" in p for p in v.pecas):
            for i, p in enumerate(v.pecas):
                saida += ["%s %d:" % (uma, i + 1), ""] + _bloco(p) + [""]
        else:
            saida += ["%s: %s" % (varias, "  ".join("`%s`" % p
                                                    for p in v.pecas)), ""]
    saida += ["Resposta certa: `%s`" % v.certa_texto.replace("\n", " ⏎ "), "",
              "Se errar:", ""]
    for x in v.erros:
        marca = " _(aponta a crença `%s`)_" % x.crenca if x.crenca else ""
        saida.append("- %s → %s%s" % (_resposta(g, v, x), x.retorno, marca))
    saida.append("- qualquer outro erro → %s" % v.retorno_geral)
    return saida


def leitura(d: Dominio, escadas: Mapping[str, Escada]) -> str:
    """A escada em Markdown, na ordem em que a pessoa a encontra."""
    saida = [
        "# A escada do %s — %s" % (d.id, d.titulo), "",
        "Texto para leitura, gerado de `mvp/dominio/%s`. Cada degrau tem "
        "duas versões: a segunda, com outros valores, aparece quando o mesmo "
        "passo volta, como no treino e na reconferência do fim."
        % arquivo_da_escada(d.id).name,
    ]
    for premissa in d.ordem:
        if premissa not in escadas:
            continue
        e = escadas[premissa]
        saida += ["", "## %s — %s" % (premissa, d.nos[premissa].simples)]
        for i, g in enumerate(e.degraus):
            saida += ["", "### Degrau %d — %s, %s"
                      % (i + 1, "guiado" if g.guiado else "prática", g.forma)]
            if g.nome:
                saida += ["", "_Nome do passo, no fechamento: %s_" % g.nome]
            if g.frases:
                saida += [""] + ["> %s" % f for f in g.frases]
            for k, v in enumerate(g.versoes):
                saida += _versao_em_texto(g, k, v)
        saida += ["", "### Se errar a pergunta do topo: a revisão", ""]
        saida += ["> %s" % f for f in e.revisao.frases] + [""]
        saida += _bloco(e.revisao.codigo)
        if e.revisao.saida:
            saida += ["", "A máquina imprime:", "", "```",
                      e.revisao.saida, "```"]
        for p in e.provas:
            saida += _prova_em_texto(d, p)
    return "\n".join(saida) + "\n"


def _prova_em_texto(d: Dominio, p: Prova) -> list[str]:
    """A prova, na ordem das duas telas: o que a pessoa disse, o trecho,
    a previsão; depois o que a máquina respondeu e o que isso mostra."""
    saida = ["", "### Se a pessoa disser a crença: a prova", "",
             "Você disse:", "", "> %s" % d.crencas[p.crenca].afirma, ""]
    saida += _bloco(p.programa) + ["", "**%s**" % p.previsao.pergunta, ""]
    for i, opcao in enumerate(p.previsao.opcoes):
        marca = (" _(é o que a máquina faz)_" if i == p.previsao.real
                 else " _(é o que a crença espera)_" if i == p.previsao.crenca
                 else "")
        saida.append("- %s%s" % (opcao, marca))
    if p.espera:
        saida += ["", "A máquina imprime:", "", "```", p.espera, "```"]
    else:
        saida += ["", "O compilador reclama:", "", "```", p.reclama, "```"]
        if p.cala:
            saida += ["", "E não diz:", "", "```", p.cala, "```"]
    if p.ambiente:
        saida += ["", "_%s_" % p.ambiente]
    saida += ["", "O que isto mostra: %s" % p.afirma]
    return saida


def main(args: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if args is None else args)
    quer_leitura = "--leitura" in args
    topicos = [a for a in args if not a.startswith("--")]
    if len(topicos) != 1:
        print("uso: python scripts/confere_escada.py <topico> [--leitura]",
              file=sys.stderr)
        return 2
    d = carrega(topico=topicos[0])
    escadas = le(arquivo_da_escada(d.id), d)

    if quer_leitura:
        # No Windows a saída redirecionada sai em cp1252 e quebra os
        # acentos do arquivo. O texto é UTF-8, sempre.
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stdout.write(leitura(d, escadas))
        return 0

    sem = faltando(d, escadas)
    problemas = confere(escadas)
    for p in problemas:
        print("PROBLEMA  %s" % p)
    if sem:
        print("SEM ESCADA  %s" % ", ".join(sem))
    degraus = sum(len(e.degraus) for e in escadas.values())
    print("%s: %d premissas com escada, %d degraus, %d problemas"
          % (d.id, len(escadas), degraus, len(problemas)))
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
