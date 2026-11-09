# -*- coding: utf-8 -*-
"""O percurso de uma PESSOA, lido dos logs dela.

O TERCEIRO MECANISMO do histórico individual
(`docs/historico-individual.md`), e o mais barato dos três: é LEITURA,
não estado novo. O log já guardava tudo por sessão, e o código do
participante já era o id da sessão. O que faltava era algo que lesse os
vários logs de um mesmo código — e isso não existia porque, até aqui, uma
pessoa fazia uma sessão.

ESTE MÓDULO NÃO ESCREVE NADA, e não é figura de linguagem: nenhuma função
aqui abre arquivo para escrita, e há teste conferindo que o arquivo não
muda depois de uma leitura. Ele também não decide nada — a decisão do
dono foi explícita: *só recomenda, sem cadeado*. `sem_oportunidade`
devolve uma lista, nunca um veredito, e de propósito não existe campo
`pode_entrar`: seria o cadeado entrando pela porta de trás.

A FORMA DA RESPOSTA, também decidida por ele: não *"você não pode"*, mas
*"isto aqui vai cobrar o que você não teve chance de aprender"*.

E QUEM LÊ ISSO, hoje, é quem conduz a coleta — não o estudante. Quem
escolhe o tópico é quem sobe o servidor (`docs/auditoria-travessia.md`),
então a saída é de terminal, por `scripts/percurso.py`, e não de tela.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from mvp import conceitos, log
from mvp.dominio import Dominio

# Os quatro eventos conceituais, na ordem em que uma aprendizagem os
# produz. É o vocabulário inteiro deste módulo.
APRESENTADO = "conceito_apresentado"
DIAGNOSTICADO = "conceito_diagnosticado"
CONFIRMADO = "conceito_confirmado"
REVISITADO = "conceito_revisitado"
CONCEITUAIS = (APRESENTADO, DIAGNOSTICADO, CONFIRMADO, REVISITADO)


@dataclass(frozen=True)
class Unidade:
    """Um tópico que a pessoa abriu, e se ela chegou ao fim dele.

    Abrir e encerrar são coisas diferentes, e o histórico não pode
    confundi-las: quem abriu o kc_07 e parou na primeira tela não teve o
    percurso daquele tópico.
    """
    topico: str
    encerrada: bool = False


@dataclass(frozen=True)
class Cobranca:
    """Um conceito que o tópico escolhido COBRA, e o que a pessoa teve.

    `itens` é quantos itens daquele tópico usam o construto; `status` é o
    que o inventário diz dele; `oportunidade` é se ESTA pessoa tem
    `conceito_apresentado` registrado; `onde` são os cartões em que teve.

    Não há campo de veredito. Quem decide é quem conduz.
    """
    conceito: str
    itens: int
    status: str
    oportunidade: bool
    onde: tuple[str, ...] = ()


@dataclass(frozen=True)
class Percurso:
    """O que os logs dizem sobre uma pessoa.

    `eventos` são as linhas conceituais dela, na ordem dos arquivos.
    `puladas` conta as linhas ilegíveis — contar é o que separa tolerar
    de esconder, e é a mesma escolha que o painel já fazia.
    """
    codigo: str
    unidades: tuple[Unidade, ...] = ()
    eventos: tuple[dict, ...] = ()
    puladas: int = 0

    def _por_conceito(self, tipo: str) -> Mapping[str, tuple[dict, ...]]:
        fora: dict[str, list] = {}
        for e in self.eventos:
            if e.get("tipo") == tipo:
                fora.setdefault(e.get("conceito", ""), []).append(e)
        return {cid: tuple(v) for cid, v in sorted(fora.items()) if cid}

    def apresentados(self) -> Mapping[str, tuple[dict, ...]]:
        """Os conceitos que ela teve OPORTUNIDADE de aprender."""
        return self._por_conceito(APRESENTADO)

    def diagnosticados(self) -> Mapping[str, tuple[dict, ...]]:
        return self._por_conceito(DIAGNOSTICADO)

    def confirmados(self) -> Mapping[str, tuple[dict, ...]]:
        """Os conceitos cujo nó fechou pela regra do sistema.

        NÃO quer dizer que ela domina o conceito — a atribuição é pelo
        cartão do nó, e o próprio evento diz isso em `atribuicao`.
        """
        return self._por_conceito(CONFIRMADO)

    def revisitados(self) -> Mapping[str, tuple[dict, ...]]:
        return self._por_conceito(REVISITADO)

    def teve_oportunidade(self, cid: str) -> bool:
        return cid in self.apresentados()

    def confirmou(self, cid: str) -> bool:
        return cid in self.confirmados()

    def cartoes_de(self, cid: str) -> tuple[str, ...]:
        """Em que cartões ela teve a oportunidade, sem repetir."""
        vistos = []
        for e in self.apresentados().get(cid, ()):
            onde = e.get("no", "")
            if onde and onde not in vistos:
                vistos.append(onde)
        return tuple(vistos)


def percurso(codigo: str,
             destinos: Iterable[Path] | None = None) -> Percurso:
    """Lê os logs e devolve o percurso daquele código.

    VÁRIOS ARQUIVOS porque os logs de hoje são um por configuração de
    lançamento: o percurso de uma pessoa pode estar espalhado entre eles.
    Com o guarda `(código, tópico)` isso deixou de ser necessário, mas os
    ensaios já gravados continuam separados.

    Tolerante a linha ilegível, pelo mesmo motivo do painel: o relatório
    existe para funcionar depois de um travamento.
    """
    alvos = [Path(x) for x in (destinos if destinos is not None
                               else [log.DESTINO])]
    unidades: list[Unidade] = []
    eventos: list[dict] = []
    encerrados: set[str] = set()
    puladas = 0

    for caminho in alvos:
        if not caminho.exists():
            continue
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            try:
                dado = json.loads(linha)
            except json.JSONDecodeError:
                puladas += 1
                continue
            if dado.get("sessao") != codigo:
                continue
            tipo = dado.get("tipo")
            if tipo == log.ABERTURA_DA_UNIDADE:
                unidades.append(Unidade(topico=str(dado.get("topico", ""))))
            elif tipo == log.FECHO_DA_UNIDADE and unidades:
                encerrados.add(str(len(unidades) - 1))
                unidades[-1] = Unidade(unidades[-1].topico, encerrada=True)
            elif tipo in CONCEITUAIS:
                eventos.append(dado)

    return Percurso(codigo=codigo, unidades=tuple(unidades),
                    eventos=tuple(eventos), puladas=puladas)


def sem_detector() -> tuple[str, ...]:
    """Conceitos do inventário para os quais NÃO há padrão de varredura.

    São sete de catorze, e isso limita tudo o que `cobrancas_do_topico`
    pode dizer: um conceito sem padrão nunca aparece como cobrado, mesmo
    que os itens o exijam. `derreferencia` é o caso que achou isto — um
    teste esperava vê-lo na lista do kc_11 e caiu.

    O relatório DECLARA esta lista, em vez de deixar a omissão passar por
    "o tópico não cobra". Dizer menos do que se sabe é melhor do que
    dizer mais; calar que se está dizendo menos, não.
    """
    com_padrao = {cid for _, cid in conceitos.CONSTRUTOS}
    return tuple(sorted(set(conceitos.carrega()) - com_padrao))


def cobrancas_do_topico(dominio: Dominio) -> Mapping[str, int]:
    """Quantos itens daquele tópico usam cada construto.

    Varredura do CÓDIGO dos itens, pelo mapa de `mvp/conceitos.py`. Aqui
    varredura serve: o construto está no código ou não está. É o oposto
    de dizer o que um cartão ENSINA, onde ela não serve — e as duas
    coisas moram em funções diferentes por causa disso.

    PARCIAL, e `sem_detector()` diz o quanto: sete conceitos do
    inventário não têm padrão nenhum, e para eles esta função é cega.
    """
    conta: dict[str, int] = {}
    for a in dominio.atividades:
        for cid in conceitos.construtos_de(a.codigo):
            conta[cid] = conta.get(cid, 0) + 1
    return dict(sorted(conta.items()))


def sem_oportunidade(p: Percurso, dominio: Dominio) -> tuple[Cobranca, ...]:
    """O que o tópico escolhido vai cobrar que ESTA pessoa não teve chance
    de aprender.

    A pergunta do dono: *começar pelo kc_06 cobra o quê?* A resposta é
    uma lista, por conceito, com quantos itens o cobram e o que o
    inventário diz dele — e ela muda de pessoa para pessoa, que é o que a
    torna uma medida do percurso e não do currículo.

    Ordenada pelo número de itens, decrescente: quem lê precisa ver
    primeiro o que mais aparece.
    """
    fora = []
    for cid, itens in cobrancas_do_topico(dominio).items():
        if p.teve_oportunidade(cid):
            continue
        fora.append(Cobranca(conceito=cid, itens=itens,
                             status=conceitos.status(cid),
                             oportunidade=False))
    return tuple(sorted(fora, key=lambda c: (-c.itens, c.conceito)))


def com_oportunidade(p: Percurso, dominio: Dominio) -> tuple[Cobranca, ...]:
    """O outro lado da mesma lista: o que ela cobra e a pessoa teve.

    Existe para o relatório poder mostrar os dois — uma lista só do que
    falta não deixa ver se o percurso está servindo para algo.
    """
    fora = []
    for cid, itens in cobrancas_do_topico(dominio).items():
        if not p.teve_oportunidade(cid):
            continue
        fora.append(Cobranca(conceito=cid, itens=itens,
                             status=conceitos.status(cid),
                             oportunidade=True, onde=p.cartoes_de(cid)))
    return tuple(sorted(fora, key=lambda c: (-c.itens, c.conceito)))


def relatorio(p: Percurso, dominio: Dominio) -> str:
    """O relatório de entrada, em texto, para quem conduz a coleta.

    Não dá veredito e não usa a palavra bloqueado: ele diz o que o tópico
    vai cobrar e o que a pessoa teve chance de aprender, e quem decide é
    quem está conduzindo.
    """
    linhas = ["percurso de %s, entrando em %s (%s)"
              % (p.codigo, dominio.id, dominio.titulo)]

    if p.unidades:
        feitas = ", ".join(
            "%s%s" % (u.topico, "" if u.encerrada else " (abriu e parou)")
            for u in p.unidades)
        linhas.append("  tópicos antes: " + feitas)
    else:
        linhas.append("  tópicos antes: nenhum — primeira sessão deste "
                      "código")
    if p.puladas:
        linhas.append("  ATENÇÃO: %d linha(s) ilegível(eis) nos logs; o "
                      "percurso abaixo pode estar incompleto" % p.puladas)

    teve = com_oportunidade(p, dominio)
    linhas.append("")
    linhas.append("  com oportunidade registrada (%d)" % len(teve))
    for c in teve:
        linhas.append("    %-24s %3d itens  %-16s em %s"
                      % (c.conceito, c.itens, c.status, ", ".join(c.onde)))
    if not teve:
        linhas.append("    (nenhum)")

    falta = sem_oportunidade(p, dominio)
    linhas.append("")
    linhas.append("  este tópico vai cobrar, sem oportunidade "
                  "registrada (%d)" % len(falta))
    for c in falta:
        linhas.append("    %-24s %3d itens  %s"
                      % (c.conceito, c.itens, c.status))
    if not falta:
        linhas.append("    (nenhum)")

    cegos = sem_detector()
    if cegos:
        linhas.append("")
        linhas.append("  o que esta leitura NÃO vê (%d conceitos sem padrão"
                      " de varredura):" % len(cegos))
        linhas.append("    " + ", ".join(cegos))
        linhas.append("    para esses, a lista acima não diz nada — nem "
                      "que o tópico cobra, nem que não.")

    confirmados = p.confirmados()
    linhas.append("")
    linhas.append("  conceitos confirmados no percurso (%d): %s"
                  % (len(confirmados),
                     ", ".join(sorted(confirmados)) or "nenhum"))
    linhas.append("  — confirmado quer dizer que o NÓ fechou pela regra do")
    linhas.append("    sistema, com o conceito atribuído pelo cartão. Não")
    linhas.append("    é afirmação de domínio.")
    return chr(10).join(linhas)
