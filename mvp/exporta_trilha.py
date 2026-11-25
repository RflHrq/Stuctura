# -*- coding: utf-8 -*-
"""Exportação das sessões da trilha para análise: três tabelas em CSV.

    python -m mvp.exporta_trilha --pasta coleta/portal --out analise/trilha

    sessoes.csv     uma linha por sessão (participante e tópico)
    premissas.csv   uma linha por premissa aberta numa sessão: a situação
                    diagnosticada na abertura, o trabalho feito, a crença,
                    se a previsão seguiu a crença, o resultado e a
                    reconferência
    respostas.csv   uma linha por resposta: pergunta, passo da escada ou
                    previsão, com a razão, a certeza e o tempo

A trilha grava um registro por tópico, `<pasta>/trilha/kc_NN.jsonl`, com
um evento por linha (`mvp/trilha_log.py`). O `mvp/exporta.py` exporta o
registro do fluxo anterior, que tem outro formato; este lê o da trilha. É
o que faltava para o estudo com estudantes (Apêndice A da monografia):
sem ele, uma coleta bem-feita produziria um registro de onde ninguém tira
tabela.

TUDO SAI DO REGISTRO, E O MOTOR NÃO É IMPORTADO. Reexecutar o motor para
preencher coluna mediria as regras de HOJE contra o dado de ONTEM. Há
teste lendo este arquivo para garantir que o import não aparece.

AS TRAVAS SÃO AS DO EXPORTADOR ANTERIOR, reaproveitadas, e não copiadas:
o destino que o git não ignora é recusado antes de escrever, toda célula
passa pelo neutralizador de fórmula, linha ilegível é contada e
reportada, e o CSV sai em UTF-8 com BOM, para o Excel abrir os acentos.

ANONIMIZAÇÃO NA ORIGEM. O participante sai pelo código com que entrou
(P01, P02...); nome e matrícula ficam em papel, fora do sistema. Sessão
aberta sem código sai pelo número da sessão.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
from collections import defaultdict

from mvp.exporta import _confere_destino, _rank, escreve, le

# As respostas da pessoa, e como cada uma aparece na tabela.
RESPOSTAS = {
    "resposta_registrada": "pergunta",
    "degrau_respondido": "passo",
    "previsao_registrada": "previsao",
}

COLUNAS = {
    "sessoes.csv": [
        "participante", "topico", "iniciada_em", "ultima_em", "ritmo",
        "encerrada", "cancelada", "retomadas",
        "n_premissas", "n_fechadas", "n_respostas", "n_corretas",
        "ja_sabia", "firmou", "aprendeu_agora", "corrigiu", "em_aberto",
        "ms_total",
    ],
    "premissas.csv": [
        "participante", "topico", "premissa", "ordem",
        "situacao_na_abertura", "confianca_na_abertura", "trabalho",
        "crenca", "previsao_como_a_crenca", "resultado", "telas",
        "reconferencia",
    ],
    "respostas.csv": [
        "participante", "topico", "seq", "ts", "premissa", "tela", "papel",
        "item", "versao", "tentativa", "escolha", "razao", "resposta",
        "correta", "razao_correta", "nao_sei", "confianca", "confianca_rank",
        "crenca", "como_a_crenca", "situacao", "ms",
    ],
}

TABELAS = tuple(COLUNAS)

PASTA_PADRAO = pathlib.Path(os.environ.get("STRUCTURA_PASTA") or "coleta/portal")


def _sim(valor):
    if valor is None or valor == "":
        return ""
    return "sim" if valor else "não"


def _topico(eventos, arquivo):
    inicio = next((e for e in eventos if e.get("tipo") == "trilha_iniciada"), None)
    return (inicio or {}).get("topico") or arquivo.stem


def le_pasta(pasta):
    """As sessões de todos os tópicos: [(topico, participante, eventos)]."""
    sessoes, ilegiveis = [], 0
    for arquivo in sorted((pathlib.Path(pasta) / "trilha").glob("*.jsonl")):
        por_sessao, ruins = le(arquivo)
        ilegiveis += ruins
        for participante, eventos in por_sessao.items():
            sessoes.append((_topico(eventos, arquivo), participante, eventos))
    return sessoes, ilegiveis


def respostas(sessoes):
    for topico, participante, eventos in sessoes:
        for seq, e in enumerate(eventos, 1):
            tela = RESPOSTAS.get(e.get("tipo"))
            if not tela:
                continue
            situacao = ""
            if tela == "pergunta":
                # A classificação vem logo depois da resposta que a provocou.
                prox = next((x for x in eventos[seq:]
                             if x.get("tipo") in ("episodio_classificado",)
                             + tuple(RESPOSTAS)), None)
                if prox and prox.get("tipo") == "episodio_classificado":
                    situacao = prox.get("estado", "")
            correta = e.get("certa") if tela != "pergunta" else e.get("correta")
            yield {
                "participante": participante, "topico": topico, "seq": seq,
                "ts": e.get("ts", ""), "premissa": e.get("no", ""),
                "tela": tela, "papel": e.get("papel", ""),
                "item": e.get("atividade") or e.get("degrau") or "",
                "versao": e.get("versao", ""),
                "tentativa": e.get("tentativa", ""),
                "escolha": e.get("escolha", ""), "razao": e.get("razao", ""),
                "resposta": e.get("resposta") or e.get("previu") or "",
                "correta": _sim(correta),
                "razao_correta": _sim(e.get("razao_correta")),
                "nao_sei": _sim(e.get("nao_sei")),
                "confianca": e.get("confianca", ""),
                "confianca_rank": _rank(e.get("confianca", "")),
                "crenca": e.get("crenca", ""),
                "como_a_crenca": _sim(e.get("como_a_crenca")),
                "situacao": situacao, "ms": e.get("ms", ""),
            }


def premissas(sessoes):
    for topico, participante, eventos in sessoes:
        linhas, ordem = {}, []
        for e in eventos:
            no = e.get("no")
            tipo = e.get("tipo")
            if not no:
                continue
            if tipo == "premissa_aberta" and no not in linhas:
                ordem.append(no)
                linhas[no] = {"participante": participante, "topico": topico,
                              "premissa": no, "ordem": len(ordem)}
            p = linhas.get(no)
            if p is None:
                continue
            if (tipo == "resposta_registrada" and e.get("papel") == "abertura"
                    and "confianca_na_abertura" not in p):
                p["confianca_na_abertura"] = e.get("confianca", "")
            elif (tipo == "episodio_classificado"
                    and e.get("papel") == "abertura"
                    and "situacao_na_abertura" not in p):
                p["situacao_na_abertura"] = e.get("estado", "")
            elif tipo == "trabalho_iniciado":
                p["trabalho"] = e.get("trabalho", "")
            elif tipo in ("prova_apresentada", "crenca_registrada"):
                p.setdefault("crenca", e.get("crenca", ""))
            elif tipo == "previsao_registrada":
                p["previsao_como_a_crenca"] = _sim(e.get("como_a_crenca"))
            elif tipo == "premissa_fechada":
                p["resultado"] = e.get("resultado", "")
                p["telas"] = e.get("telas", "")
            elif tipo == "reconferencia_respondida":
                p["reconferencia"] = e.get("resultado", "")
        for no in ordem:
            yield linhas[no]


def sessoes_tabela(sessoes):
    for topico, participante, eventos in sessoes:
        tipos = [e.get("tipo") for e in eventos]
        inicio = next((e for e in eventos if e.get("tipo") == "trilha_iniciada"), {})
        comeco = next((e for e in eventos if e.get("tipo") == "trilha_comecada"), {})
        fechadas = [e for e in eventos if e.get("tipo") == "premissa_fechada"]
        resps = [e for e in eventos if e.get("tipo") in RESPOSTAS]
        resultados = defaultdict(int)
        for e in fechadas:
            resultados[e.get("resultado", "")] += 1
        yield {
            "participante": participante, "topico": topico,
            "iniciada_em": eventos[0].get("ts", ""),
            "ultima_em": eventos[-1].get("ts", ""),
            "ritmo": comeco.get("ritmo", ""),
            "encerrada": _sim("trilha_encerrada" in tipos),
            "cancelada": _sim("sessao_cancelada" in tipos),
            "retomadas": tipos.count("sessao_retomada")
                         + tipos.count("sessao_reconstruida"),
            "n_premissas": inicio.get("premissas", ""),
            "n_fechadas": len(fechadas),
            "n_respostas": len(resps),
            "n_corretas": sum(bool(e.get("correta") if e.get("tipo")
                                   == "resposta_registrada" else e.get("certa"))
                              for e in resps),
            "ja_sabia": resultados["ja_sabia"],
            "firmou": resultados["firmou"],
            "aprendeu_agora": resultados["aprendeu_agora"],
            "corrigiu": resultados["corrigiu"],
            "em_aberto": resultados["em_aberto"],
            "ms_total": sum(int(e.get("ms") or 0) for e in resps),
        }


def exporta(pasta=None, destino=None):
    """As três tabelas, e o relatório de quantas linhas cada uma teve."""
    pasta = pathlib.Path(pasta or PASTA_PADRAO)
    destino = pathlib.Path(destino or "analise/trilha")
    # ANTES de ler e antes de qualquer mkdir (ver mvp/exporta.py).
    _confere_destino(destino)
    sessoes, ilegiveis = le_pasta(pasta)
    fontes = {"sessoes.csv": sessoes_tabela, "premissas.csv": premissas,
              "respostas.csv": respostas}
    r = {"pasta": str(pasta), "sessoes": len(sessoes), "ilegiveis": ilegiveis}
    for nome in TABELAS:
        r[nome] = escreve(destino / nome, COLUNAS[nome], fontes[nome](sessoes))
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--pasta", default=None,
                   help="a pasta do portal, com a subpasta trilha/ "
                        "(STRUCTURA_PASTA; padrão: coleta/portal)")
    p.add_argument("--out", default="analise/trilha",
                   help="a pasta de destino")
    a = p.parse_args(argv)
    r = exporta(a.pasta, a.out)
    print("pasta: %s" % r["pasta"])
    print("%d sessões" % r["sessoes"])
    for nome in TABELAS:
        print("  %-16s %6d linhas" % (nome, r[nome]))
    if r["ilegiveis"]:
        print("ATENÇÃO: %d linha(s) ilegível(eis) no registro" % r["ilegiveis"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
