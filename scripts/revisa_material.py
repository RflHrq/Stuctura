"""Os portões mecânicos da revisão de material candidato.

    python scripts/revisa_material.py candidatos/kc_02/I2_material_1.yaml
    python scripts/revisa_material.py candidatos/kc_02/        # a pasta toda

POR QUE ISTO É UM PROGRAMA, E NÃO UM TEXTO PEDINDO ATENÇÃO. Cada portão
aqui pegou defeito real, e vários passaram por uma leitura humana e por
uma revisão de agente antes de cair aqui:

    YAML que não parseia      `no:` virou o booleano falso; duas
                              alternativas começadas por "nada:"
                              quebraram o arquivo
    id repetido               `ciu_kc02_e3` já era o item de entrada do
                              B3 — a sequência e1..e6 é uma por nó
    a certa é a mais longa    num item do I3, pista de formato
    distrator sem crença      terceiro distrator que não mapeava em
                              concepção nenhuma do catálogo
    conceito não disponível   `funcao_com_parametro` está
                              `nao_introduzido`, e o nó que fecha o
                              kc_02 se apoia nele
    severidade afirmada       "o compilador recusa" é verdade no
                              gcc >= 14 e falso num gcc mais antigo
    código em texto corrido   `_paragrafos` cola linha que não esteja
                              separada por linha em branco

O QUE ESTE PROGRAMA NÃO DECIDE, e por isso existe a skill
`revisar-material`: se o item repete, em outras palavras, pergunta que
já está no banco. A semelhança léxica daqui é PISTA, não veredito —
medido, o par mais grave do projeto (o mesmo item com a atribuição
invertida) deu 0.08.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import unicodedata

import yaml

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))

from mvp.dominio import carrega                      # noqa: E402

NL = chr(10)

# Os campos de ensino que, por levarem código, TÊM de ser lista de
# blocos. Texto corrido passa por `_paragrafos`, que cola as linhas.
CAMPOS_EM_BLOCO = ("caso_resolvido", "reexplicacao")
BLOCOS_VALIDOS = ("prosa", "codigo", "saida")

# Palavras que afirmam o que o compilador FAZ. A severidade de
# -Wint-conversion e -Wincompatible-pointer-types mudou no gcc 14: o que
# aqui é erro, num laboratório com compilador mais antigo é aviso, e o
# programa compila. O domínio já resolveu isso usando "reclama".
SEVERIDADE = re.compile(r"\b(recusa|recusam|não compila|nao compila|"
                        r"é erro|e erro|nem compila)\b", re.I)

# A lista de `docs/linguagem.md`: o enunciado não tem absoluto nem NOME
# DE PESSOA. O segundo faltava aqui, e a auditoria do domínio achou um:
# `ciu_kc00_003` começa com "Rafael diz:".
PROIBIDAS = re.compile(r"\b(sempre|nunca|jamais)\b", re.I)
NOME_DE_PESSOA = re.compile(
    r"\b(Rafael|Ana|João|Joao|Maria|Pedro|Lucas|Bruno|Carla|José|Jose|"
    r"Paulo|Júlia|Julia|Marcos|Clara|Thiago|Tiago)\b")

# Construto no CÓDIGO -> conceito do inventário. Nunca aplicado à prosa:
# a primeira versão varria tudo junto, e o padrão de "função com
# parâmetro" casou com a frase "...de b / (a não foi tocado...".
CONSTRUTOS = (
    (re.compile(r"\bsizeof\b"), "sizeof"),
    (re.compile(r"\bscanf\b"), "scanf"),
    (re.compile(r"%p"), "printf_ponteiro"),
    (re.compile(r"\*\s*\*"), "ponteiro_de_ponteiro"),
    (re.compile(r"\w+\s*\[\s*\d"), "array"),
    (re.compile(r"&\w+\s*==\s*&?\w+"), "comparacao_de_ponteiros"),
    (re.compile(r"^\s*[A-Za-z_][\w \*]*\w\s*\(\s*(?!void\s*\))"
                r"[A-Za-z_]\w*\s+\**\w+", re.M), "funcao_com_parametro"),
)

# Conceitos que padrão nenhum denuncia: quando a PROSA fala de o
# compilador reclamar, os dois estão em jogo.
FALA_DO_COMPILADOR = re.compile(
    r"compilador|error:|warning:|reclama|incompatible|conversion", re.I)
POR_FALA = ("atribuicao_entre_tipos", "compilacao")

# Assinatura de função, para separar escopo de arquivo de statements.
ASSINATURA = re.compile(r"^\s*[A-Za-z_][\w \*]*\w\s*\([^;]*\)\s*\{")


def _recusa_obrigatoria(codigo: str | None) -> bool:
    """O compilador recusa este código mesmo com `-w`?

    É o que separa violação de restrição — que todo compilador conforme
    tem de diagnosticar — de aviso promovido a erro por versão ou flag.
    Sem esta distinção, o portão de severidade acusa os dois.
    """
    if not (codigo or "").strip():
        return False
    try:
        from scripts.oraculo import GCC
    except ImportError:
        sys.path.insert(0, str(AQUI / "scripts"))
        from oraculo import GCC                          # type: ignore
    if not pathlib.Path(GCC).exists():
        return True          # sem compilador, não acusa por suposição
    import subprocess
    import tempfile
    arquivo, dentro = [], []
    for linha in codigo.splitlines():
        (arquivo if ASSINATURA.match(linha) else dentro).append(
            linha if ASSINATURA.match(linha) else "    " + linha)
    prog = ("#include <stdio.h>" + NL + NL.join(arquivo) + NL
            + "int main(void)" + NL + "{" + NL + NL.join(dentro) + NL
            + "    return 0;" + NL + "}" + NL)
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "o.c").write_text(prog, encoding="utf-8")
        try:
            r = subprocess.run([str(GCC), "-std=c17", "-w", "-o", "o.exe",
                                "o.c"], capture_output=True, text=True,
                               timeout=10, cwd=str(p))
        except (subprocess.TimeoutExpired, OSError):
            return True
        return r.returncode != 0


def _pista_de_tamanho(certa, opcoes) -> bool:
    """A certa é VISIVELMENTE a mais longa?

    CALIBRAGEM, e ela é o conserto de um erro meu que quase custou caro.
    A primeira versão marcava qualquer diferença de um caractere, e
    acusou 153 dos 562 itens do domínio — 27%. Fui medir se a pista era
    explorável:

        persona que sempre marca a mais longa ..... 35% de acerto
        acaso numa cédula de três ................. 33%
        itens cuja folga é de 1 a 5 caracteres .... 133 dos 153

    Dois pontos acima do acaso não é pista: é ruído. Reescrever 153
    gabaritos do instrumento por causa disso seria estragá-lo de graça.

    A regra de `docs/linguagem.md` fala do defeito clássico de redação —
    a certa conspicuamente mais longa —, e é isso que este portão mede:
    pelo menos 10 caracteres a mais E 40% mais longa. Com esse corte
    sobram 9 itens, e oito deles são binários do kc_00, onde a folga vem
    de "Certo" contra "Errado — <explicação>".
    """
    outras = [len(o.texto) for o in opcoes if o is not certa]
    if not outras:
        return False
    maior = max(outras)
    return len(certa.texto) - maior >= 10 and len(certa.texto) >= 1.4 * maior


def _sem_acento(s: str) -> list[str]:
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def _trigramas(s: str) -> set[str]:
    p = _sem_acento(s)
    return {" ".join(p[i:i + 3]) for i in range(max(len(p) - 2, 1))}


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0.0


def _codigo_todo(d: dict) -> str:
    partes = [str(x.get("linha", "")) for x in d.get("narracao") or []]
    for campo in CAMPOS_EM_BLOCO:
        for b in d.get(campo) or []:
            if isinstance(b, dict) and "codigo" in b:
                partes.append(str(b["codigo"]))
    for a in d.get("activities") or []:
        partes.append(str(a.get("codigo", "")))
    return NL.join(partes)


def _prosa_toda(d: dict) -> str:
    partes = []
    for campo in ("ampliacao", "premissa"):
        v = d.get(campo)
        if isinstance(v, str) and v != "ja_existe_no_dominio":
            partes.append(v)
    partes.extend(str(x.get("diz", "")) for x in d.get("narracao") or [])
    for campo in CAMPOS_EM_BLOCO:
        v = d.get(campo)
        if isinstance(v, list):
            partes.extend(str(b.get("prosa", "")) for b in v
                          if isinstance(b, dict))
        elif isinstance(v, str):
            partes.append(v)
    for a in d.get("activities") or []:
        partes.append(str(a.get("enunciado", "")))
        partes.extend(str(x) for x in (a.get("alternativas") or {}).values())
    return NL.join(partes)


def _mostra_recusa(d: dict) -> bool:
    """O material exibe o compilador recusando alguma coisa?"""
    for campo in CAMPOS_EM_BLOCO:
        for b in d.get(campo) or []:
            if not isinstance(b, dict):
                continue
            if b.get("recusa"):
                return True
            if FALA_DO_COMPILADOR.search(str(b.get("saida", ""))):
                return True
    return any(a.get("recusa") for a in d.get("activities") or [])


def _conceitos(d: dict, inventario: dict, achados: list) -> None:
    codigo, prosa = _codigo_todo(d), _prosa_toda(d)
    declarados = set(d.get("exige_conceitos") or [])
    for cid in declarados:
        if cid not in inventario:
            achados.append(("ERRO", "exige_conceitos cita %r, que não existe "
                                    "no inventário" % cid))

    usados = {cid for padrao, cid in CONSTRUTOS if padrao.search(codigo)}
    # `atribuicao_entre_tipos` e `compilacao` nao tem construto que os
    # denuncie. O gatilho e o material MOSTRAR uma recusa: um bloco
    # marcado `recusa`, ou uma saida com a mensagem do compilador. A
    # primeira versao disparava na palavra "reclama", e acusava o B2 por
    # dizer "o compilador responde sem reclamar".
    if _mostra_recusa(d):
        usados |= set(POR_FALA)
    for cid in sorted(usados):
        estado = (inventario.get(cid) or {}).get("status", "ausente")
        if estado == "disponivel" or cid in declarados:
            continue
        nivel = "ERRO" if estado in ("nao_introduzido", "ausente") else "AVISO"
        achados.append((nivel, "usa %r, que está %r no inventário e não "
                               "aparece em `exige_conceitos`" % (cid, estado)))


def _itens(d: dict, dom, achados: list) -> None:
    usados = {x.id for x in dom.atividades}
    no = (d.get("node") or "").split(":")[-1]
    for a in d.get("activities") or []:
        aid = a.get("id", "(sem id)")
        if aid in usados:
            achados.append(("ERRO", "%s: id já existe no domínio" % aid))
        alts = a.get("alternativas") or {}
        crencas = a.get("crencas") or {}
        gab = a.get("gabarito")
        if len(alts) < 3:
            achados.append(("ERRO", "%s: menos de três alternativas" % aid))
        if gab not in alts:
            achados.append(("ERRO", "%s: gabarito %r não é alternativa"
                            % (aid, gab)))
            continue
        outras = [len(v) for k, v in alts.items() if k != gab]
        if outras and (len(alts[gab]) - max(outras) >= 10
                       and len(alts[gab]) >= 1.4 * max(outras)):
            achados.append(("ERRO", "%s: a alternativa certa é visivelmente "
                                    "a mais longa — é pista de formato"
                            % aid))
        if gab in crencas:
            achados.append(("ERRO", "%s: o gabarito está marcado como crença"
                            % aid))
        for letra in alts:
            if letra == gab:
                continue
            cid = crencas.get(letra)
            if not cid:
                achados.append(("ERRO", "%s: distrator %s não aponta crença"
                                % (aid, letra)))
            elif cid not in dom.crencas:
                achados.append(("ERRO", "%s: distrator %s aponta %r, fora do "
                                        "catálogo" % (aid, letra, cid)))
        enun = a.get("enunciado", "")
        if PROIBIDAS.search(enun):
            achados.append(("ERRO", "%s: enunciado tem absoluto proibido"
                            % aid))
        if NOME_DE_PESSOA.search(enun):
            achados.append(("ERRO", "%s: enunciado tem nome de pessoa" % aid))
        if SEVERIDADE.search(enun):
            achados.append(("ERRO", "%s: o enunciado afirma a severidade do "
                                    "compilador; use 'reclama'" % aid))
        if no in dom.nos:
            meu = _trigramas(enun + " " + alts[gab])
            for x in dom.atividades_do_no(no):
                certa = next((o.texto for o in x.opcoes if o.correta), "")
                s = _jaccard(meu, _trigramas(x.enunciado + " " + certa))
                if s >= 0.25:
                    achados.append(("PISTA", "%s parece com %s (%.2f) — leia "
                                             "os dois" % (aid, x.id, s)))


def _forma(d: dict, achados: list) -> None:
    for campo in CAMPOS_EM_BLOCO:
        v = d.get(campo)
        if v is None:
            continue
        if isinstance(v, str):
            achados.append(("ERRO", "%s é texto corrido; `_paragrafos` cola "
                                    "as linhas de código. Use lista de blocos"
                            % campo))
            continue
        for i, b in enumerate(v, 1):
            if not isinstance(b, dict):
                achados.append(("ERRO", "%s bloco %d: não é um mapa"
                                % (campo, i)))
                continue
            chaves = set(b) - {"recusa"}
            if len(chaves) != 1 or not chaves <= set(BLOCOS_VALIDOS):
                achados.append(("ERRO", "%s bloco %d: chaves %s; use uma de "
                                        "%s (mais `recusa`, opcional)"
                                % (campo, i, sorted(b),
                                   "/".join(BLOCOS_VALIDOS))))
    if SEVERIDADE.search(_prosa_toda(d)):
        achados.append(("AVISO", "o texto afirma a severidade do compilador. "
                                 "No gcc >= 14 é erro; antes, aviso"))


def _monta(fragmentos: list[str]) -> str:
    """Um programa a partir de vários fragmentos, na ordem.

    DOIS CONSERTOS, os dois achados pelo próprio validador reprovando
    material que estava certo:

    1. Blocos do mesmo campo CONTINUAM uns aos outros. Compilado
       isolado, o segundo bloco da reexplicação do B2 acusava
       "x undeclared" — o `int x` estava no bloco anterior.
    2. Definição de função vai para ESCOPO DE ARQUIVO, e o resto para
       dentro de main. Pondo tudo em main, `void dobra(int *q){...}`
       compila do mesmo jeito, porque função aninhada é extensão do GNU
       e o gcc a aceita calado sem -pedantic. Pondo tudo fora,
       `dobra(&n);` vira declaração implícita.
    """
    arquivo: list[str] = []
    dentro: list[str] = []
    for frag in fragmentos:
        linhas = frag.rstrip().splitlines()
        k = 0
        while k < len(linhas):
            linha = linhas[k]
            if ASSINATURA.match(linha):
                nivel = linha.count("{") - linha.count("}")
                arquivo.append(linha)
                while nivel > 0 and k + 1 < len(linhas):
                    k += 1
                    arquivo.append(linhas[k])
                    nivel += linhas[k].count("{") - linhas[k].count("}")
            elif linha.strip():
                dentro.append("    " + linha)
            k += 1
    return ("#include <stdio.h>" + NL
            + NL.join(arquivo) + NL
            + "int main(void)" + NL + "{" + NL
            + NL.join(dentro) + NL
            + "    return 0;" + NL + "}" + NL)


def _oraculo(d: dict, achados: list) -> None:
    """Compila o código de cada campo, em sequência.

    Um bloco marcado `recusa: true` é o contrário: ele existe para
    PROVAR que o compilador reclama, e o oráculo reprova se compilar.
    Sem isso o validador acusava os três blocos do I2 que são, eles
    mesmos, a evidência do nó.
    """
    try:
        from scripts.oraculo import SemCompilador, roda
    except ImportError:
        sys.path.insert(0, str(AQUI / "scripts"))
        from oraculo import SemCompilador, roda          # type: ignore

    grupos: list[tuple[str, list]] = []
    for campo in CAMPOS_EM_BLOCO:
        blocos = [b for b in (d.get(campo) or [])
                  if isinstance(b, dict) and "codigo" in b]
        if blocos:
            grupos.append((campo, blocos))
    for a in d.get("activities") or []:
        if a.get("codigo"):
            grupos.append((a["id"], [{"codigo": a["codigo"],
                                      "recusa": a.get("recusa", False)}]))

    for onde, blocos in grupos:
        acumulado: list[str] = []
        for n, b in enumerate(blocos, 1):
            frag = b["codigo"]
            quer_recusa = bool(b.get("recusa"))
            try:
                recusou, nota = roda(_monta(acumulado + [frag]), "",
                                     nao_compila=True)
            except SemCompilador as e:
                achados.append(("AVISO", "oráculo não rodou: %s" % e))
                return
            if quer_recusa and not recusou:
                achados.append(("ERRO", "%s bloco %d: marcado `recusa`, e o "
                                        "compilador aceitou" % (onde, n)))
            elif recusou and not quer_recusa:
                achados.append(("ERRO", "%s bloco %d: não compila — %s"
                                % (onde, n, nota)))
            if not quer_recusa:
                acumulado.append(frag)


def revisa(caminho: pathlib.Path) -> list[tuple[str, str]]:
    achados: list[tuple[str, str]] = []
    try:
        d = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [("ERRO", "o YAML não parseia: %s" % str(e).splitlines()[0])]
    if not isinstance(d, dict):
        return [("ERRO", "o arquivo não é um mapa YAML")]
    if "no" in d:
        achados.append(("ERRO", "a chave `no` vira o booleano falso em YAML; "
                                "use `node`"))
    for campo in ("topico", "node", "premissa"):
        if not d.get(campo):
            achados.append(("ERRO", "falta o campo `%s`" % campo))
    if achados:
        return achados

    inv = yaml.safe_load((AQUI / "mvp" / "dominio" / "conceitos.yaml")
                         .read_text(encoding="utf-8"))["conceitos"]
    dom = carrega(topico=d["topico"])
    _forma(d, achados)
    _itens(d, dom, achados)
    _conceitos(d, inv, achados)
    _oraculo(d, achados)
    return achados


def cobrancas_sem_ensino(dom, inventario) -> dict:
    """{(no, conceito): [ids]} -- quem cobra construto nao introduzido.

    AGRUPADO POR NO, e nao item a item, porque e o agrupamento que da o
    CONTEXTO CURRICULAR. Medido no kc_02: os sete achados estao todos no
    I3, cuja premissa e "alcancar a caixa de outro ponto do programa" --
    o no inteiro e sobre atravessar a fronteira de uma funcao. E o kc_06
    tem 24, quatro em CADA um dos seis nos, e se chama "Passagem por
    referencia".

    Nos dois casos o construto e INERENTE a premissa, e aí mover o item
    nao resolve: o no depende dele. Diferente de um exemplo que por
    acaso usa o construto, onde o item muda ou sai.

    A proporcao `k de n itens do no` e o que separa os dois casos, e ela
    vai no relatorio em vez de uma classificacao minha -- quem le julga
    com o numero na mao.
    """
    fora: dict = {}
    for a in dom.atividades:
        for padrao, cid in CONSTRUTOS:
            if not padrao.search(a.codigo or ""):
                continue
            estado = (inventario.get(cid) or {}).get("status", "ausente")
            if estado in ("nao_introduzido", "ausente"):
                fora.setdefault((a.no, cid), []).append(a.id)
    return fora


def contexto(dom, no: str, cid: str, ids: list) -> str:
    """Uma linha de contexto curricular para um grupo de achados."""
    total = len(dom.atividades_do_no(no))
    premissa = dom.nos[no].simples if no in dom.nos else "(nó desconhecido)"
    return ("%s: %d de %d itens do nó usam %r — \"%s\""
            % (no, len(ids), total, cid, premissa[:72]))


def audita_dominio(topico: str) -> list[tuple[str, str]]:
    """Os mesmos portoes, aplicados ao dominio que JA ESTA NO AR.

    O modo candidato confere material que ainda nao entrou. Este confere
    o que ja entrou -- e existe porque a auditoria do kc_02 achou, num
    item ja revisado e em producao (`kc02_gi2_n3_3`), a mesma afirmacao
    de severidade pela qual um candidato tinha sido reprovado: "por que
    o compilador RECUSA a terceira linha".

    Portao que so faz sentido aqui: item contra item DENTRO do no. No
    candidato a comparacao e contra o banco; aqui o banco e o alvo.
    """
    achados: list[tuple[str, str]] = []
    inv = yaml.safe_load((AQUI / "mvp" / "dominio" / "conceitos.yaml")
                         .read_text(encoding="utf-8"))["conceitos"]
    dom = carrega(topico=topico)

    for a in dom.atividades:
        certa = next((o for o in a.opcoes if o.correta), None)
        if certa is None:
            achados.append(("ERRO", "%s: nenhuma alternativa correta" % a.id))
            continue
        if len(a.opcoes) < 3:
            achados.append(("AVISO", "%s: menos de tres alternativas (%d)"
                            % (a.id, len(a.opcoes))))
        if _pista_de_tamanho(certa, a.opcoes):
            maior = max(len(o.texto) for o in a.opcoes if o is not certa)
            achados.append(("ERRO", "%s: a certa e VISIVELMENTE a mais longa "
                                    "(%d contra %d)"
                            % (a.id, len(certa.texto), maior)))
        for o in a.opcoes:
            if o.correta:
                continue
            if not o.crenca:
                achados.append(("AVISO", "%s: distrator sem crenca: %r"
                                % (a.id, o.texto[:50])))
            elif o.crenca not in dom.crencas:
                achados.append(("ERRO", "%s: distrator aponta %r, fora do "
                                        "catalogo" % (a.id, o.crenca)))
        if PROIBIDAS.search(a.enunciado):
            achados.append(("ERRO", "%s: enunciado tem absoluto proibido"
                            % a.id))
        if NOME_DE_PESSOA.search(a.enunciado):
            achados.append(("ERRO", "%s: enunciado tem nome de pessoa"
                            % a.id))
        # Severidade só é defeito quando o diagnóstico é CONFIGURÁVEL.
        # `3 = x;` e `a = p;` com array são violação de restrição: falham
        # até com `-w`, e aí dizer "o compilador recusa" é verdade em
        # qualquer compilador. `int *p = x;` não é: `-Wno-error=int-
        # conversion` o rebaixa a aviso e o executável existe.
        #
        # A primeira versão deste portão não distinguia, e acusou os dez
        # itens do domínio que afirmam severidade. Medido com `-w`: os
        # dez são obrigatórios, e os dez estavam certos.
        if SEVERIDADE.search(a.enunciado) and not _recusa_obrigatoria(a.codigo):
            achados.append(("ERRO", "%s: o enunciado afirma a severidade do "
                                    "compilador, e o diagnóstico é "
                                    "configurável: %r"
                            % (a.id, a.enunciado[:60])))

    # COBRANCA SEM ENSINO, agrupada por no: e o agrupamento que da o
    # contexto curricular. Ver `cobrancas_sem_ensino`.
    for (no, cid), ids in sorted(cobrancas_sem_ensino(dom, inv).items()):
        achados.append(("ERRO", contexto(dom, no, cid, ids)))
        achados.append(("", "      itens: %s" % ", ".join(sorted(ids))))

    # Item contra item, dentro do no.
    for nid in dom.ordem:
        itens = list(dom.atividades_do_no(nid))
        for i in range(len(itens)):
            for j in range(i + 1, len(itens)):
                x, y = itens[i], itens[j]
                cx = next((o.texto for o in x.opcoes if o.correta), "")
                cy = next((o.texto for o in y.opcoes if o.correta), "")
                sim = _jaccard(_trigramas(x.enunciado + " " + cx),
                               _trigramas(y.enunciado + " " + cy))
                if sim >= 0.30:
                    achados.append(("PISTA", "%s e %s (%.2f, n%d e n%d) — "
                                             "leia os dois"
                                    % (x.id, y.id, sim, x.nivel, y.nivel)))

    # O texto de ensino do topico.
    for nid in dom.ordem:
        for campo, texto in (("simples", dom.nos[nid].simples),
                             ("resgate", dom.resgates.get(nid, "")),
                             ("ampliacao", dom.interpretacao(nid))):
            if texto and SEVERIDADE.search(texto):
                achados.append(("AVISO", "%s/%s afirma severidade de "
                                         "compilador" % (nid, campo)))
        usados = {cid for padrao, cid in CONSTRUTOS
                  if padrao.search(dom.exemplo(nid) or "")}
        for cid in sorted(usados):
            estado = (inv.get(cid) or {}).get("status", "ausente")
            if estado in ("nao_introduzido", "ausente"):
                achados.append(("ERRO", "%s: o exemplo do cartao usa %r, que "
                                        "esta %r" % (nid, cid, estado)))
    return achados


def main() -> int:
    ap = argparse.ArgumentParser(description="portões mecânicos da revisão")
    ap.add_argument("alvo", nargs="?", help="arquivo candidato ou pasta")
    ap.add_argument("--dominio", metavar="TOPICO",
                    help="audita o domínio que já está no ar; `todos` varre "
                         "os treze tópicos")
    args = ap.parse_args()

    if args.dominio:
        from mvp.dominio import topicos
        alvos = topicos() if args.dominio == "todos" else [args.dominio]
        erros = 0
        for t in alvos:
            achados = audita_dominio(t)
            duros = [x for x in achados if x[0] == "ERRO"]
            erros += len(duros)
            marca = "ERRO" if duros else ("aviso" if achados else "ok")
            print(NL + "== %s  [%s]" % (t, marca))
            for nivel, msg in achados:
                print("   %-5s %s" % (nivel, msg))
            if not achados:
                print("   nenhum achado mecânico")
        print(NL + "%d erro(s) em %d tópico(s)." % (erros, len(alvos)))
        return 1 if erros else 0

    if not args.alvo:
        ap.error("informe um candidato, ou use --dominio")
    alvo = pathlib.Path(args.alvo)
    arquivos = (sorted(alvo.glob("*_material_*.yaml")) if alvo.is_dir()
                else [alvo])
    if not arquivos:
        print("nenhum candidato em %s" % alvo)
        return 2

    erros = 0
    for f in arquivos:
        achados = revisa(f)
        duros = [x for x in achados if x[0] == "ERRO"]
        erros += len(duros)
        marca = "ERRO" if duros else ("aviso" if achados else "ok")
        print(NL + "== %s  [%s]" % (f.name, marca))
        for nivel, msg in achados:
            print("   %-5s %s" % (nivel, msg))
        if not achados:
            print("   nenhum achado mecânico")

    print(NL + "%d erro(s) em %d arquivo(s)." % (erros, len(arquivos)))
    print("Os portões de JULGAMENTO não estão aqui: use a skill "
          "`revisar-material`.")
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
