# -*- coding: utf-8 -*-
"""O percurso de um participante, lido dos logs. LEITURA, nada mais.

A verificação de entrada do histórico individual: antes de uma pessoa
começar um tópico, dizer o que ele vai cobrar e o que ela teve chance de
aprender.

É DE TERMINAL, e não de tela, porque hoje quem escolhe o tópico é quem
sobe o servidor, não o estudante — está medido em
`docs/auditoria-travessia.md`. Quando o estudante escolher, isto vira
rota; o módulo `mvp/historico.py` já está pronto para as duas.

E NÃO É CADEADO. A decisão do dono foi explícita: só recomenda. Este
script não devolve código de erro por falta de oportunidade e não diz a
ninguém que não pode entrar.

    python scripts/percurso.py P20 --topico kc_06
    python scripts/percurso.py P20 --topico kc_06 --log ensaios/*.jsonl
    python scripts/percurso.py --lista --log ensaios/coleta.jsonl
"""
from __future__ import annotations

import argparse
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))

from mvp import historico, log                        # noqa: E402
from mvp.dominio import carrega, topicos              # noqa: E402


def _logs(dados) -> list[pathlib.Path]:
    return [pathlib.Path(x) for x in dados] or [log.DESTINO]


def _lista(caminhos) -> int:
    """Quem está nos logs, e que tópicos cada um atravessou."""
    codigos: dict[str, list] = {}
    for caminho in caminhos:
        if not caminho.exists():
            print("não achei %s" % caminho)
            continue
        pares, ilegiveis = log.aberturas(caminho)
        for codigo, topico in sorted(pares):
            codigos.setdefault(codigo, []).append(topico)
        if ilegiveis:
            print("%s: %d linha(s) ilegível(eis)"
                  % (caminho.name, len(ilegiveis)))
    if not codigos:
        print("nenhum participante nos logs lidos")
        return 0
    print("%-14s %s" % ("código", "tópicos abertos"))
    for codigo, lista in sorted(codigos.items()):
        p = historico.percurso(codigo, caminhos)
        confirmados = len(p.confirmados())
        print("%-14s %-28s %d conceito(s) confirmado(s)"
              % (codigo, ", ".join(sorted(set(lista))), confirmados))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("codigo", nargs="?",
                    help="o código do participante, como P20")
    ap.add_argument("--topico", default=None,
                    help="o tópico em que ele vai entrar (%s)"
                         % ", ".join(topicos()))
    ap.add_argument("--log", nargs="*", default=[],
                    help="um ou mais arquivos de log; o padrão é o de "
                         "STRUCTURA_LOG")
    ap.add_argument("--lista", action="store_true",
                    help="lista os participantes dos logs, em vez de um")
    args = ap.parse_args(argv)

    caminhos = _logs(args.log)

    if args.lista:
        return _lista(caminhos)

    if not args.codigo:
        ap.error("informe um código, ou use --lista")

    p = historico.percurso(args.codigo, caminhos)

    if args.topico is None:
        # Sem tópico escolhido, o relatório é só o percurso: dizer o que
        # falta exige saber para onde a pessoa vai.
        print("percurso de %s" % p.codigo)
        if p.unidades:
            for u in p.unidades:
                print("  %s%s" % (u.topico,
                                  "" if u.encerrada else "  (abriu e parou)"))
        else:
            print("  nenhum tópico — primeira sessão deste código")
        if p.puladas:
            print("  ATENÇÃO: %d linha(s) ilegível(eis) nos logs"
                  % p.puladas)
        for rotulo, mapa in (("apresentados", p.apresentados()),
                             ("diagnosticados", p.diagnosticados()),
                             ("revisitados", p.revisitados()),
                             ("confirmados", p.confirmados())):
            print("  %-16s %s" % (rotulo,
                                  ", ".join(sorted(mapa)) or "nenhum"))
        print()
        print("  para ver o que um tópico vai cobrar, use --topico")
        return 0

    if args.topico not in topicos():
        ap.error("tópico desconhecido: %r" % args.topico)
    print(historico.relatorio(p, carrega(topico=args.topico)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
