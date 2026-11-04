# -*- coding: utf-8 -*-
"""Exportação do log do MVP para análise: quatro tabelas em CSV.

    python -m mvp.exporta --out analise/
    python -m mvp.exporta --log mvp/dados/eventos.jsonl --out analise/

    respostas.csv    uma linha por EPISÓDIO classificado
    sessoes.csv      uma linha por sessão
    calibracao.csv   uma linha por (participante, confiança)
    crencas.csv      uma linha por crença detectada, com o reteste ao lado

POR QUE ISTO EXISTE. O `plano-tcc.md` afirma que "a exportação gera três
tabelas", e o `tools/export.py` que as gera lê **SQLite**. O MVP grava
**JSONL**. Não havia exportação nenhuma aqui, e sem ela uma coleta
bem-feita produz um log de onde ninguém tira tabela. Ver
`docs/divergencia-texto-sistema.md`, P1-A.

QUATRO E NÃO TRÊS. A unidade de análise de V2 e V3 é o episódio de crença
detectada, e isso não cabe numa linha de resposta. `crencas.csv` é essa
unidade. Copiar o número três de um documento que descreve o sistema
antigo seria guardar a forma e perder a função.

TUDO SAI DO LOG, E O MOTOR NÃO É IMPORTADO. Não é só a regra do exportador
antigo ("nenhuma análise lê projeção"): aqui é mais forte. Reexecutar o
motor para preencher coluna faria a exportação medir o motor de HOJE
contra dado de ONTEM, e o `log.reconstroi` recusa sessão de versão
anterior exatamente por isso. Um exportador que importasse o motor
contornaria essa recusa por acidente. Há teste lendo este arquivo para
garantir que o import não aparece.

ANONIMIZAÇÃO NA ORIGEM. O código do participante é o código da sessão,
P01…P40. Nome, matrícula e e-mail ficam em papel, fora do log. Nenhuma
coluna aqui carrega identificador direto, e há teste sobre os NOMES das
colunas — porque a submissão ética fala sobre o que o arquivo pode ter, e
não só sobre o que ele tem hoje.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
from collections import Counter, defaultdict

# Os prefixos que o Excel avalia como fórmula. Tab, CR e LF entram porque
# a planilha os trata como espaço e avalia o que vem depois — uma lista
# que só olhasse `=+-@` deixaria passar "\t=1+1".
PERIGOSOS = ("=", "+", "-", "@", "\t", "\r", "\n")

# A escala de confiança é ORDINAL, e ordenar por texto daria alfabético.
ESCALA = ("chutei", "acho que sei", "tenho certeza")

PADRAO_LOG = (pathlib.Path(os.environ.get("STRUCTURA_LOG"))
              if os.environ.get("STRUCTURA_LOG")
              else pathlib.Path(__file__).resolve().parent / "dados"
              / "eventos.jsonl")

COLUNAS = {
    "respostas.csv": [
        "participante", "topico", "seq", "ts",
        "no", "atividade", "tipo", "formato", "do_molde", "nivel", "fase",
        "escolha", "ordem", "n_opcoes", "correta", "razao_correta", "nao_sei",
        "confianca", "confianca_rank", "crenca", "estado",
        "ms", "ms_razao", "ms_confianca",
    ],
    "sessoes.csv": [
        "participante", "topico", "iniciada_em", "ultima_em", "completou",
        "n_eventos", "n_episodios", "n_corretas",
        "n_crencas_detectadas", "n_falsos_positivos", "n_fragil", "n_lacuna",
        "n_retestadas", "n_voltaram",
        "confirmados", "em_aberto", "nao_medidos", "refutadas", "retestadas",
        "mais_fraca", "mais_fraca_de_pe",
        "teachback_inicial", "teachback_final",
        "teachback_inicial_em_branco", "teachback_final_em_branco",
        "ms_total",
    ],
    "calibracao.csv": [
        "participante", "confianca", "confianca_rank",
        "n", "n_corretas", "prop_corretas", "ms_medio",
    ],
    "crencas.csv": [
        "participante", "topico", "crenca", "no", "veio_do_item_de",
        "via", "vezes", "erros", "confianca_na_deteccao",
        "retestada", "voltou", "reteste_correta", "reteste_razao_correta",
        "reteste_superficie_nova", "reteste_formato", "motivo_sem_reteste",
    ],
}

TABELAS = tuple(COLUNAS)


class DestinoVersionado(Exception):
    """O destino da exportação está num lugar que o git NÃO ignora."""


def _confere_destino(destino):
    """Recusa escrever dado de participante em pasta versionada.

    A exportação carrega TEXTO LIVRE: os dois teach-backs vão para
    `sessoes.csv`. O P0 da revisão final foi exatamente isto — três cópias
    do log de desenvolvimento entraram no git por um caminho que o
    `.gitignore` não casava, e a varredura de segredos passou por cima
    delas porque o nome não batia com a regra.

    O comando irmão já decidiu a questão: o `copia.sh` recusa destino
    dentro do repositório. Um exportador sem a mesma trava seria
    incoerente com o padrão da casa.

    A REGRA NÃO É "fora do repositório", é "o git tem de ignorar".
    `analise/` está no `.gitignore` por decisão declarada e é o destino
    padrão. Fora do repositório a decisão é do pesquisador — a segunda
    mídia da cópia fica fora, e exigir git lá impediria o uso legítimo.

    A conferência vem ANTES de qualquer `mkdir`: recusar depois de criar a
    pasta e escrever o primeiro arquivo seria pior que não recusar, porque
    o dado já estaria lá e o erro na tela diria que não.
    """
    import subprocess

    raiz = pathlib.Path(__file__).resolve().parent.parent
    alvo = pathlib.Path(destino).resolve()
    if alvo != raiz and raiz not in alvo.parents:
        return
    try:
        r = subprocess.run(["git", "check-ignore", "-q", str(alvo)],
                           cwd=str(raiz), capture_output=True)
    except (OSError, ValueError):
        # Sem git não há como saber, e na dúvida sobre dado de
        # participante a resposta é não.
        raise DestinoVersionado(
            "não consegui perguntar ao git se %s é ignorada, e exportação "
            "de dado de participante não vai para dentro do repositório "
            "sem essa resposta. Use uma pasta fora, ou `analise/`." % alvo)
    if r.returncode != 0:
        raise DestinoVersionado(
            "%s está dentro do repositório e o git NÃO a ignora. A "
            "exportação carrega o texto livre do teach-back, e dado de "
            "participante em pasta versionada foi o P0 da revisão final. "
            "Use `analise/`, que está no .gitignore, ou uma pasta fora do "
            "repositório." % alvo)


def neutraliza(valor):
    """Impede que uma resposta livre vire fórmula na planilha.

    O teach-back é texto livre: vai do teclado do participante direto
    para o CSV. Um aluno que escreva `=1+1` — ou algo pior — teria isso
    EXECUTADO quando o pesquisador abrisse o arquivo no Excel. Não é
    hipotético: é o vetor de injeção de fórmula em CSV.

    O prefixo apóstrofo é a mitigação padrão: a planilha mostra o texto e
    não o avalia. O dado original continua intacto no log, que é a fonte.
    """
    if isinstance(valor, str) and valor.startswith(PERIGOSOS):
        return "'" + valor
    return valor


def _texto(valor):
    """Lista vira "a b c", None vira vazio, dict vira JSON.

    `ordem` e `confirmados` são listas no log, e `str(lista)` sairia como
    "['B1']" — com colchetes e aspas dentro da célula.
    """
    if valor is None:
        return ""
    if isinstance(valor, (list, tuple)):
        return " ".join(str(x) for x in valor)
    if isinstance(valor, dict):
        return json.dumps(valor, ensure_ascii=False, sort_keys=True)
    return valor


def _rank(confianca):
    return ESCALA.index(confianca) + 1 if confianca in ESCALA else ""


def le(caminho):
    """O log, em sessões, na ordem em que cada uma aparece.

    Devolve `(sessoes, ilegiveis)`. Linha ilegível não derruba a
    exportação — o log é append-only e a última linha pode estar truncada
    por queda no meio da escrita —, mas é CONTADA e reportada: perda
    silenciosa de evento é pior que erro.
    """
    sessoes, ilegiveis = defaultdict(list), 0
    with pathlib.Path(caminho).open(encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                ev = json.loads(linha)
            except (ValueError, TypeError):
                ilegiveis += 1
                continue
            if not isinstance(ev, dict) or not ev.get("sessao"):
                ilegiveis += 1
                continue
            sessoes[ev["sessao"]].append(ev)
    return sessoes, ilegiveis


def _por_tipo(eventos, tipo):
    return [e for e in eventos if e.get("tipo") == tipo]


def _primeiro(eventos, tipo):
    return next((e for e in eventos if e.get("tipo") == tipo), None)


def _topico(eventos):
    inicio = _primeiro(eventos, "unidade_iniciada")
    return (inicio or {}).get("topico", "")


def respostas(sessoes):
    """Uma linha por `episodio_classificado`, com as três camadas ao lado.

    QUATRO EVENTOS ALIMENTAM UMA LINHA, e saber qual carrega o quê foi o
    defeito que os fixtures escondiam:

        atividade_apresentada   formato, nivel, fase, ORDEM da tela, tipo
        resposta_registrada     ESCOLHA e MS da camada 1
        camada2_respondida      o ms da razão
        camada3_respondida      o ms da confiança
        episodio_classificado   correta, razao_correta, crença, ESTADO

    A primeira versão lia `escolha` e `ms` de `atividade_apresentada`, que
    não os tem — e as duas colunas saíam vazias em toda a coleta, com 29
    testes verdes. Sem `escolha` a análise não sabe o que a pessoa marcou,
    e sem `ordem` o índice não se interpreta: as duas juntas são o que a
    fatia da posição tornou legível.

    `tipo` se chamava `item` e carregava "teorica" — nome de coluna que
    mente é pior que coluna ausente, porque quem analisa não desconfia.
    """
    for sessao, eventos in sessoes.items():
        topico = _topico(eventos)
        apresentada, resposta, c2, c3 = {}, {}, {}, {}
        seq = 0
        for ev in eventos:
            tipo = ev.get("tipo")
            chave = ev.get("atividade")
            if tipo == "atividade_apresentada":
                apresentada[chave] = ev
                continue
            if tipo == "resposta_registrada":
                resposta[chave] = ev
                continue
            if tipo == "camada2_respondida":
                c2[chave] = ev
                continue
            if tipo == "camada3_respondida":
                c3[chave] = ev
                continue
            if tipo != "episodio_classificado":
                continue
            seq += 1
            a = apresentada.get(chave, {})
            r = resposta.get(chave, {})
            conf = ev.get("confianca")
            yield {
                "participante": sessao,
                "topico": topico,
                "seq": seq,
                "ts": ev.get("ts", ""),
                "no": ev.get("no", ""),
                "atividade": chave or "",
                "tipo": a.get("item", r.get("item", "")),
                "formato": a.get("formato", ""),
                "do_molde": a.get("do_molde", ""),
                "nivel": a.get("nivel", ""),
                "fase": a.get("fase", r.get("fase", "")),
                "escolha": r.get("escolha", ""),
                "ordem": _texto(a.get("ordem")),
                "n_opcoes": len(a["ordem"]) if isinstance(a.get("ordem"), list) else "",
                "correta": ev.get("correta", ""),
                "razao_correta": ev.get("razao_correta", ""),
                "nao_sei": ev.get("nao_sei", ""),
                "confianca": _texto(conf),
                "confianca_rank": _rank(conf),
                "crenca": _texto(ev.get("crenca")),
                "estado": ev.get("estado", ""),
                "ms": r.get("ms", ""),
                "ms_razao": c2.get(chave, {}).get("ms", ""),
                "ms_confianca": c3.get(chave, {}).get("ms", ""),
            }


def sessoes_tabela(sessoes):
    """Uma linha por sessão, inclusive a que NÃO foi encerrada.

    A sessão que cai no meio é o caso que o CS-6 existe para cobrir, e o
    PRD orça perder 1 em 10 a 15 participantes por queda. Um exportador
    que só emitisse linha ao ver `unidade_encerrada` apagaria em silêncio
    o participante mais interessante do estudo.
    """
    for sessao, eventos in sessoes.items():
        fim = _primeiro(eventos, "unidade_encerrada") or {}
        eps = _por_tipo(eventos, "episodio_classificado")
        estados = Counter(e.get("estado") for e in eps)
        retestes = _por_tipo(eventos, "belief_retested")
        ti = _primeiro(eventos, "teachback_inicial") or {}
        tf = _primeiro(eventos, "teachback_final") or {}
        yield {
            "participante": sessao,
            "topico": _topico(eventos),
            "iniciada_em": eventos[0].get("ts", ""),
            "ultima_em": eventos[-1].get("ts", ""),
            "completou": bool(fim),
            "n_eventos": len(eventos),
            "n_episodios": len(eps),
            "n_corretas": sum(1 for e in eps if e.get("correta")),
            "n_crencas_detectadas": len(_por_tipo(eventos, "crenca_detectada")),
            "n_falsos_positivos": estados.get("falso_positivo", 0),
            "n_fragil": estados.get("fragil", 0),
            "n_lacuna": estados.get("lacuna", 0),
            "n_retestadas": len(retestes),
            "n_voltaram": sum(1 for e in retestes if e.get("voltou")),
            "confirmados": _texto(fim.get("confirmados")),
            "em_aberto": _texto(fim.get("em_aberto")),
            "nao_medidos": _texto(fim.get("nao_medidos")),
            "refutadas": _texto(fim.get("refutadas")),
            "retestadas": _texto(fim.get("retestadas")),
            "mais_fraca": _texto(fim.get("mais_fraca")),
            "mais_fraca_de_pe": _texto(fim.get("mais_fraca_de_pe")),
            "teachback_inicial": _texto(ti.get("texto")),
            "teachback_final": _texto(tf.get("texto")),
            "teachback_inicial_em_branco": _texto(ti.get("em_branco")),
            "teachback_final_em_branco": _texto(tf.get("em_branco")),
            "ms_total": sum(e.get("ms") or 0 for e in eventos
                            if isinstance(e.get("ms"), (int, float))),
        }


def calibracao(sessoes):
    """Uma linha por (participante, confiança): a calibração
    metacognitiva. É o que diz se "tenho certeza" quer dizer alguma coisa.
    """
    for sessao, eventos in sessoes.items():
        por_conf = defaultdict(list)
        for e in _por_tipo(eventos, "episodio_classificado"):
            if e.get("confianca"):
                por_conf[e["confianca"]].append(e)
        for conf in sorted(por_conf, key=lambda c: _rank(c) or 99):
            grupo = por_conf[conf]
            tempos = [e["ms"] for e in grupo
                      if isinstance(e.get("ms"), (int, float))]
            yield {
                "participante": sessao,
                "confianca": conf,
                "confianca_rank": _rank(conf),
                "n": len(grupo),
                "n_corretas": sum(1 for e in grupo if e.get("correta")),
                "prop_corretas": round(
                    sum(1 for e in grupo if e.get("correta")) / len(grupo), 4),
                "ms_medio": round(sum(tempos) / len(tempos), 1) if tempos else "",
            }


def crencas(sessoes):
    """Uma linha por crença detectada, com o desfecho do reteste ao lado.

    É a unidade de análise de V2 e V3, e a razão de serem quatro tabelas.

    CRENÇA SEM RETESTE NÃO É `voltou=False`. São afirmações diferentes:
    uma diz "ela não voltou à ideia errada", a outra diz "ninguém
    perguntou". Confundi-las inventaria sucesso de refutação que nenhuma
    medida produziu. Sem reteste, `voltou` sai VAZIO, e
    `motivo_sem_reteste` diz por quê quando o log soube dizer.
    """
    for sessao, eventos in sessoes.items():
        topico = _topico(eventos)
        retestes = {}
        for e in _por_tipo(eventos, "belief_retested"):
            retestes.setdefault((e.get("crenca"), e.get("no")), e)
        semi = {}
        for e in _por_tipo(eventos, "reteste_sem_item"):
            semi.setdefault((e.get("crenca"), e.get("no")), e)

        vistas = set()
        for ev in _por_tipo(eventos, "crenca_detectada"):
            chave = (ev.get("crenca"), ev.get("no"))
            if chave in vistas:
                continue
            vistas.add(chave)
            r = retestes.get(chave)
            s = semi.get(chave, {})
            yield {
                "participante": sessao,
                "topico": topico,
                "crenca": _texto(ev.get("crenca")),
                "no": ev.get("no", ""),
                "veio_do_item_de": ev.get("veio_do_item_de", ""),
                "via": _texto(ev.get("via")),
                "vezes": ev.get("vezes", ""),
                "erros": ev.get("erros", ""),
                "confianca_na_deteccao": _texto(ev.get("confianca")),
                "retestada": bool(r),
                "voltou": r.get("voltou", "") if r else "",
                "reteste_correta": r.get("correta", "") if r else "",
                "reteste_razao_correta": r.get("razao_correta", "") if r else "",
                "reteste_superficie_nova": (r.get("superficie_nova", "")
                                            if r else ""),
                "reteste_formato": r.get("formato", "") if r else "",
                "motivo_sem_reteste": "" if r else _texto(s.get("motivo")),
            }


def escreve(caminho, colunas, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: o Excel em português abre acento certo sem perguntar. Sem
    # o BOM ele assume a codificação do sistema e come os acentos — e
    # ninguém repara numa planilha de 200 linhas.
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(colunas), extrasaction="ignore")
        w.writeheader()
        total = 0
        for linha in linhas:
            # TODA célula passa pelo neutralizador, não só as que eu
            # lembrei de passar: coluna de texto livre acrescentada
            # depois fica coberta por omissão, e não descoberta.
            w.writerow({c: neutraliza(_texto(linha.get(c, ""))) for c in colunas})
            total += 1
    return total


def exporta(log=None, destino=None):
    """As quatro tabelas, e o relatório de quantas linhas cada uma teve."""
    log = pathlib.Path(log or PADRAO_LOG)
    destino = pathlib.Path(destino or "analise")
    # ANTES de ler e antes de qualquer mkdir: ver o docstring de
    # `_confere_destino` sobre por que a ordem importa.
    _confere_destino(destino)
    sessoes, ilegiveis = le(log)
    fontes = {
        "respostas.csv": respostas,
        "sessoes.csv": sessoes_tabela,
        "calibracao.csv": calibracao,
        "crencas.csv": crencas,
    }
    r = {"log": str(log), "sessoes": len(sessoes), "ilegiveis": ilegiveis}
    for nome in TABELAS:
        r[nome] = escreve(destino / nome, COLUNAS[nome], fontes[nome](sessoes))
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--log", default=None, help="o log JSONL (STRUCTURA_LOG)")
    p.add_argument("--out", default="analise", help="a pasta de destino")
    a = p.parse_args(argv)
    r = exporta(a.log, a.out)
    print("log: %s" % r["log"])
    print("%d sessões" % r["sessoes"])
    for nome in TABELAS:
        print("  %-16s %6d linhas" % (nome, r[nome]))
    if r["ilegiveis"]:
        # Nunca em silêncio: linha ilegível é evento perdido.
        print("ATENÇÃO: %d linha(s) ilegível(eis) no log" % r["ilegiveis"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
