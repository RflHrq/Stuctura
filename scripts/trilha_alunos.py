"""Alunos simulados da trilha, para os testes e para a medida.

    python scripts/trilha_alunos.py kc_00

NÃO SÃO PESSOAS, e nada daqui vai para `coleta/`: as caminhadas rodam o
motor em processo, sem servidor e sem disco. Servem para duas coisas — os
testes de invariante (toda sessão termina, ninguém passa do teto de
telas) e a contagem de telas por tipo de aluno, que substitui a
estimativa da spec por medida.

Cada persona é um jeito FIXO de responder, e nenhuma sorteia: a que
"chuta" tira a escolha do SHA-256 da semente com a tela, para a mesma
caminhada dar sempre as mesmas telas.

    sabe               tudo certo, com certeza
    inseguro           tudo certo, sem certeza
    nao_sabe_aprende   "não sei" nas perguntas que decidem o caminho;
                       degraus certos; depois da escada, acerta
    nao_sabe_erra      "não sei" em toda pergunta; degrau sempre errado
    crente_aprende     na abertura, a crença com certeza; depois acerta
    crente_teimoso     sempre a crença com certeza; degrau errado
    escorrega          na abertura, erra a resposta e acerta a razão
    chuta_com_certeza  escolhas sem critério, sempre "tenho certeza"
    tropeca_na_pratica como o que não sabe e aprende, mas erra a primeira
                       tentativa de todo degrau de PRÁTICA
    abre_a_explicacao  acerta tudo, depois de abrir a explicação em cada
                       pergunta de abertura

As duas últimas entraram com a revisão do ramo: os caminhos em que ela
achou defeito eram os que nenhuma das oito primeiras fazia.
"""

from __future__ import annotations

import hashlib
import pathlib
import sys
from dataclasses import dataclass, field

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mvp import motor, trilha  # noqa: E402
from mvp.dominio import carrega  # noqa: E402
from mvp.trilha_escada import le, ordem_das_pecas  # noqa: E402

PERSONAS = ("sabe", "inseguro", "nao_sabe_aprende", "nao_sabe_erra",
            "crente_aprende", "crente_teimoso", "escorrega",
            "chuta_com_certeza", "tropeca_na_pratica", "abre_a_explicacao")

CERTEZA = "tenho certeza"
MEIA = "acho que sei"

# As perguntas que decidem o caminho. É nelas que as personas diferem.
DECIDEM = ("abertura", "reforco")


@dataclass
class Caminhada:
    estado: "trilha.Estado"
    telas: list = field(default_factory=list)
    eventos: list = field(default_factory=list)


def _sorte(semente: str, *partes) -> int:
    texto = "|".join([semente] + [str(p) for p in partes])
    return int.from_bytes(hashlib.sha256(texto.encode()).digest()[:4], "big")


def _atividade(d, aid: str):
    return next(a for a in d.atividades if a.id == aid)


def _pergunta(d, tela, persona: str, estado) -> "trilha.Entrada":
    dados = tela.dados
    a = _atividade(d, dados["atividade"])
    opcoes = motor.opcoes_na_tela(estado.semente, a)
    brutas = motor.razoes_de(d, a)
    razoes = [brutas[i] for i in motor.ordem_das_razoes(
        estado.semente, a.id, len(brutas))]
    papel, no = dados["papel"], dados["premissa"]
    pede_razao, pede_certeza = dados["pede_razao"], dados["pede_certeza"]

    certa = next(i for i, o in enumerate(opcoes) if o.correta)
    razao_certa = next(i for i, z in enumerate(razoes) if z.correta)

    def monta(escolha, razao, confianca):
        return trilha.Entrada(acao="responder", escolha=escolha,
                              razao=razao if pede_razao else None,
                              confianca=confianca if pede_certeza else "")

    def com_crenca():
        """A alternativa errada com crença — de preferência a que nega
        ESTA premissa — e a razão que diz essa crença."""
        erradas = [(i, o) for i, o in enumerate(opcoes)
                   if not o.correta and o.crenca in d.crencas]
        erradas.sort(key=lambda par: d.crencas[par[1].crenca].nega != no)
        if not erradas:
            return None
        i, o = erradas[0]
        j = next((k for k, z in enumerate(razoes) if z.crenca == o.crenca),
                 None)
        return None if j is None else (i, j)

    if persona == "abre_a_explicacao":
        if papel == "abertura" and not estado.premissa(no).abriu_explicacao:
            return trilha.Entrada(acao="explicacao")
        return monta(certa, razao_certa, CERTEZA)
    if persona == "sabe":
        return monta(certa, razao_certa, CERTEZA)
    if persona == "inseguro":
        return monta(certa, razao_certa, MEIA)
    if persona in ("nao_sabe_aprende", "tropeca_na_pratica"):
        if papel in DECIDEM:
            return trilha.Entrada(acao="nao_sei")
        return monta(certa, razao_certa, MEIA)
    if persona == "nao_sabe_erra":
        return trilha.Entrada(acao="nao_sei")
    if persona in ("crente_aprende", "crente_teimoso"):
        if persona == "crente_teimoso" or papel == "abertura":
            par = com_crenca()
            if par is not None:
                return monta(par[0], par[1], CERTEZA)
            errada = next(i for i, o in enumerate(opcoes) if not o.correta)
            return monta(errada, razao_certa, CERTEZA)
        return monta(certa, razao_certa, CERTEZA)
    if persona == "escorrega":
        if papel == "abertura":
            errada = next(i for i, o in enumerate(opcoes) if not o.correta)
            return monta(errada, razao_certa, CERTEZA)
        return monta(certa, razao_certa, CERTEZA)
    # chuta_com_certeza
    return monta(_sorte(estado.semente, a.id, "o") % len(opcoes),
                 _sorte(estado.semente, a.id, "z") % len(razoes), CERTEZA)


ACERTAM_DEGRAU = ("sabe", "inseguro", "nao_sabe_aprende", "crente_aprende",
                  "escorrega", "abre_a_explicacao")


def _degrau(escadas, tela, persona: str, estado) -> "trilha.Entrada":
    dados = tela.dados
    escada = escadas[dados["premissa"]]
    g = next(x for x in escada.degraus if x.id == dados["degrau"])
    k = estado.passo.versao
    v = g.versoes[k]
    n = len(v.pecas)
    ordem = ordem_das_pecas(estado.semente, g.id, k, g.forma, n)

    def na_tela(seq):
        return tuple(ordem.index(i) for i in seq)

    # Erra a primeira tentativa de todo degrau de prática, na subida; no
    # resto, acerta.
    tropeca = (persona == "tropeca_na_pratica" and not g.guiado
               and dados["papel"] == "subida" and dados["tentativa"] == 1)
    if persona in ACERTAM_DEGRAU or (persona == "tropeca_na_pratica"
                                     and not tropeca):
        if g.forma == "digitar":
            return trilha.Entrada(acao="responder", texto=v.aceitas[0])
        return trilha.Entrada(acao="responder", pecas=na_tela(v.certa[0]))

    if persona == "chuta_com_certeza":
        s = _sorte(estado.semente, g.id, k)
        if g.forma == "digitar":
            return trilha.Entrada(acao="responder", texto=str(s % 50))
        if g.forma == "montar":
            giro = s % n
            return trilha.Entrada(acao="responder", pecas=tuple(
                (i + giro) % n for i in range(n)))
        return trilha.Entrada(acao="responder", pecas=(s % n,))

    # nao_sabe_erra e crente_teimoso: sempre errado.
    if g.forma == "digitar":
        previsto = next((x.texto for x in v.erros if x.texto), "nao sei")
        return trilha.Entrada(acao="responder", texto=previsto)
    previsto = next((x.exata for x in v.erros if x.exata), None)
    if previsto is not None:
        return trilha.Entrada(acao="responder", pecas=na_tela(previsto))
    errada = next(i for i in range(n) if (i,) not in v.certa)
    return trilha.Entrada(acao="responder", pecas=na_tela((errada,)))


def responde(d, escadas, tela, persona: str, estado) -> "trilha.Entrada":
    """A entrada daquela persona para aquela tela."""
    if persona not in PERSONAS:
        raise ValueError("persona desconhecida: %r" % persona)
    if tela.tipo == "pergunta":
        return _pergunta(d, tela, persona, estado)
    if tela.tipo == "degrau":
        return _degrau(escadas, tela, persona, estado)
    if tela.tipo == "voce_disse" and tela.dados.get("previsao"):
        return trilha.Entrada(acao="responder",
                              escolha=_previsao(d, escadas, tela, persona))
    return trilha.Entrada(acao="continuar")


def _previsao(d, escadas, tela, persona: str) -> int:
    """O que a persona prevê antes de ver a máquina.

    Com a prova da escada, quem ACREDITA prevê o que a crença espera — é
    o que faz da previsão um dado. Quem só erra, erra; os outros acertam.
    """
    propria = next(
        (p for p in escadas[tela.dados["premissa"]].provas
         if d.crencas[p.crenca].afirma == tela.dados["crenca"]), None)
    if propria is not None:
        pv = propria.previsao
        if persona in ("crente_aprende", "crente_teimoso"):
            return pv.crenca
        if persona == "nao_sabe_erra":
            return next(i for i in range(len(pv.opcoes)) if i != pv.real)
        return pv.real
    # A prova do grafo: a pergunta é "compila?" ou "o compilador
    # reclama?", e a resposta certa é o que a prova mostra — não compila
    # (índice 1) ou reclama (índice 0).
    certa = 1 if "compila" in tela.dados["previsao"]["pergunta"] else 0
    if persona in ("crente_teimoso", "nao_sabe_erra"):
        certa = 1 - certa
    return certa


def caminha(d, escadas, persona: str, modo: str = "direto",
            ritmo: str = "completo", semente: str = "s1",
            limite: int = 400) -> Caminhada:
    """Uma sessão inteira, da entrada ao mapa."""
    t = trilha.inicia(d, escadas, semente)
    c = Caminhada(t.estado, [t.tela], list(t.eventos))
    t = trilha.avanca(d, escadas, t.estado, trilha.Entrada(
        acao="comecar", modo=modo, ritmo=ritmo))
    passos = 0
    while True:
        c.estado = t.estado
        c.telas.append(t.tela)
        c.eventos.extend(t.eventos)
        if t.tela.tipo == "mapa":
            return c
        passos += 1
        assert passos <= limite, (
            "a sessão de %s/%s/%s não terminou em %d entradas"
            % (persona, modo, ritmo, limite))
        t = trilha.avanca(d, escadas, t.estado,
                          responde(d, escadas, t.tela, persona, t.estado))


def reconferencias(c: Caminhada) -> int:
    return sum(1 for t in c.telas if t.dados.get("papel") == "reconferencia")


def conta(c: Caminhada) -> int:
    """As telas de uma caminhada, como a spec conta (docs/trilha.md, 6.10).

    A entrada e o mapa, o que cada premissa somou — onde a subida inteira
    da escada vale UMA, e o retorno não conta —, e a reconferência.
    """
    por_premissa = sum(p.telas for p in c.estado.premissas.values())
    return 2 + por_premissa + reconferencias(c)


def toques(c: Caminhada) -> int:
    """Quantas vezes a pessoa respondeu ou seguiu: a medida do esforço,
    em que cada degrau da escada conta."""
    return len(c.telas) - 1


ABREVIA = {"ja_sabia": "sabia", "firmou": "firmou", "aprendeu_agora": "aprendeu",
           "corrigiu": "corrigiu", "em_aberto": "aberto"}


def main(args: list[str] | None = None) -> int:
    """A medida: telas por aluno simulado, modo e ritmo.

    `telas` é a conta da spec (a subida inteira da escada vale uma, o
    retorno não conta, a reconferência entra); `maior` é a premissa que
    mais custou; `toques` é o esforço de verdade, cada degrau contando.
    """
    args = list(sys.argv[1:] if args is None else args)
    if len(args) != 1:
        print("uso: python scripts/trilha_alunos.py <topico>", file=sys.stderr)
        return 2
    d = carrega(topico=args[0])
    arquivo = (RAIZ / "mvp" / "dominio"
               / ("escada_%s.yaml" % d.id.replace("_", "")))
    if not arquivo.exists():
        print("o tópico %s não tem escada escrita (%s)" % (d.id, arquivo.name),
              file=sys.stderr)
        return 2
    escadas = le(arquivo, d)

    print("%s - %s (%d premissas)" % (d.id, d.titulo, len(d.ordem)))
    print("%-18s %-9s %-9s %5s %5s %6s %6s  %s" % (
        "aluno", "modo", "ritmo", "telas", "maior", "reconf", "toques",
        "resultados"))
    for persona in PERSONAS:
        for modo in trilha.MODOS:
            for ritmo in trilha.RITMOS:
                c = caminha(d, escadas, persona, modo, ritmo)
                resultados = [c.estado.premissa(n).resultado for n in d.ordem]
                print("%-18s %-9s %-9s %5d %5d %6d %6d  %s" % (
                    persona, modo, ritmo, conta(c),
                    max(c.estado.premissa(n).telas for n in d.ordem),
                    reconferencias(c), toques(c),
                    " ".join(ABREVIA[r] for r in resultados)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
