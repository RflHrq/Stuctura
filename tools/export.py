"""Exportação para análise: as três tabelas do §12.

    python -m tools.export --out analise/
    python -m tools.export --db data/structura.db --out analise/ --sessions S1 S2

    answers.csv       uma linha por resposta a CIU
    sessions.csv      uma linha por sessão
    calibration.csv   uma linha por (participante, confiança)

TUDO SAI DO LOG, NADA DA PROJEÇÃO. `node_state` é cache reconstruível e
nenhuma análise deve lê-la (§5.1): se a projeção estivesse errada, o erro
entraria nos resultados sem deixar rastro. O que estas tabelas leem é
`events`, que é append-only, mais o domínio congelado para resolver
metadados de CIU.

ANONIMIZAÇÃO NA ORIGEM (§12). O código do participante é P01…P40, gerado
na alocação. Nome, matrícula e e-mail ficam em papel sob guarda do
pesquisador, fora do banco. Nenhuma destas colunas carrega identificador
direto — o que simplifica a submissão ética e elimina risco de vazamento.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.loader import Domain, load  # noqa: E402
from store import events as store_events  # noqa: E402

# Eventos que marcam tempo em cada fase. É o que permite parear tempo em
# tarefa entre os braços (§8): se A leva 8 min e B leva 2, uma diferença
# de aprendizado pode ser efeito de exposição, não do método.
TEMPO_CORRECAO = ("socratic_step_answered", "explanation_acknowledged")


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

def sessoes(conn: sqlite3.Connection, apenas: Sequence[str] | None = None) -> list[dict]:
    sql = ("SELECT s.id, s.participant, s.arm, s.kc_sequence, s.started_at,"
           " s.ended_at, p.prior_c, p.consent_at"
           " FROM sessions s LEFT JOIN participants p ON p.code = s.participant")
    args: list[Any] = []
    if apenas:
        sql += " WHERE s.id IN (%s)" % ",".join("?" * len(apenas))
        args = list(apenas)
    sql += " ORDER BY s.started_at, s.id"
    return [dict(r) for r in conn.execute(sql, args)]


def _hash_do_dominio(eventos: Sequence[store_events.Event]) -> str:
    for e in eventos:
        if e.type == "session_started":
            return e.payload.get("domain_hash", "")
    return ""


# --------------------------------------------------------------------------
# answers.csv — desfecho PRIMÁRIO: validação da Q-matrix
# --------------------------------------------------------------------------

COLUNAS_ANSWERS = [
    "participant", "arm", "session_id", "seq", "ts",
    "kc", "ciu_id", "ciu_type", "ciu_phase", "targets",
    "option_idx", "displayed_idx", "n_options", "option_text", "response_text",
    "correct", "confidence", "elapsed_ms",
    "chosen_misconception", "distractor_is_mapped",
    "belief_counted_active", "answer_index_in_kc",
    "session_phase", "retest_of", "retest_still_held",
]


def linhas_answers(d: Domain, sessao: dict, eventos: Sequence[store_events.Event]):
    """Uma linha por resposta.

    Duas colunas carregam a distinção que o §7.3 faz e que a análise não
    pode perder:

      chosen_misconception   a crença do distrator escolhido, SEMPRE que
                             houver — é o dado cru da Q-matrix;
      belief_counted_active  se aquela escolha CONTOU como crença ativa,
                             o que exige errar com confiança declarada.

    Sem as duas separadas, a frequência de cada crença na população fica
    inflada por chutes, e a validação do catálogo mede outra coisa.

    `distractor_is_mapped` = 0 é o achado do §4.4: distrator sem
    `misconception_id` escolhido com frequência é crença fora do catálogo.
    """
    ativas = {
        (e.seq, e.payload.get("misconception_id"))
        for e in eventos if e.type == "misconception_detected"
    }
    seqs_ativas = {s for s, _ in ativas}
    por_kc: dict[str, int] = defaultdict(int)

    # RETESTE: a atividade que fecha o KC repergunta a crença refutada. O
    # desfecho já vem pronto no evento `belief_retested`, que segue a
    # resposta — ler dali evita que a análise refaça a regra e discorde do
    # motor, que é o mesmo cuidado de `belief_counted_active`.
    retestes = {
        e.payload.get("ciu_id"): e.payload
        for e in eventos if e.type == "belief_retested"
    }

    for e in eventos:
        if e.type != "answer_submitted":
            continue
        p = e.payload
        ciu = d.cius.get(p.get("ciu_id"))
        kc = p.get("kc") or (ciu.kc if ciu else "")
        por_kc[kc] += 1

        idx = p.get("option_idx")
        opcao = None
        if ciu and ciu.is_choice and isinstance(idx, int) and 0 <= idx < len(ciu.options):
            opcao = ciu.options[idx]

        # A crença é dada por ativa se o evento `misconception_detected`
        # veio logo depois desta resposta. Ler do LOG, e não recalcular a
        # regra aqui, impede que a análise e o motor discordem.
        ativa = any(s in (e.seq + 1, e.seq + 2) for s in seqs_ativas)

        texto = p.get("text")
        yield {
            "participant": sessao["participant"],
            "arm": sessao["arm"],
            "session_id": sessao["id"],
            "seq": e.seq,
            "ts": e.ts,
            "kc": kc,
            "ciu_id": p.get("ciu_id", ""),
            "ciu_type": ciu.type if ciu else "",
            "ciu_phase": ciu.phase if ciu else p.get("phase", ""),
            "targets": "|".join(ciu.targets) if ciu else "",
            "option_idx": "" if idx is None else idx,
            # A POSIÇÃO em que a alternativa apareceu. As alternativas são
            # embaralhadas por sessão, e guardar isto permite testar se a
            # posição influenciou a escolha — em vez de só supor que não.
            "displayed_idx": (
                "" if p.get("displayed_idx") is None else p["displayed_idx"]
            ),
            "n_options": len(ciu.options) if ciu and ciu.is_choice else "",
            "option_text": opcao.text if opcao else "",
            # Texto cru, não JSON. `json.dumps` embrulhava a resposta em
            # aspas — o analista veria `"*(a + i)"` em vez de `*(a + i)` —
            # e, pior, escondia o `=` inicial de `neutraliza`, que então
            # deixava passar uma fórmula. Só a ordenação (uma lista) vira
            # JSON, porque não tem representação plana.
            "response_text": (
                texto if isinstance(texto, str)
                else json.dumps(texto, ensure_ascii=False) if texto else ""
            ),
            "correct": 1 if p.get("correct") else 0,
            "confidence": p.get("confidence", ""),
            "elapsed_ms": p.get("elapsed_ms", ""),
            "chosen_misconception": p.get("misconception_id") or "",
            "distractor_is_mapped": (
                "" if (opcao is None or opcao.correct)
                else (1 if opcao.misconception else 0)
            ),
            "belief_counted_active": 1 if ativa else 0,
            "answer_index_in_kc": por_kc[kc],
            # A fase do CATÁLOGO está em `ciu_phase`; esta é a da SESSÃO.
            # Divergem no reteste, quando uma atividade declarada como
            # diagnóstica é usada para fechar o KC.
            "session_phase": p.get("session_phase", ""),
            "retest_of": p.get("retest_of") or "",
            "retest_still_held": (
                1 if retestes.get(p.get("ciu_id"), {}).get("still_held")
                else (0 if p.get("retest_of") else "")
            ),
        }


# --------------------------------------------------------------------------
# sessions.csv — tempo por braço, conclusão, abandono
# --------------------------------------------------------------------------

COLUNAS_SESSIONS = [
    "participant", "arm", "session_id", "domain_hash", "prior_c",
    "started_at", "ended_at", "end_reason", "completed",
    "kc_sequence", "kcs_completed", "kcs_in_progress",
    "n_answers", "n_correct", "n_beliefs_detected",
    # O DESFECHO DE CORRECAO, por sessao: de quantas crencas refutadas o
    # aluno foi reperguntado, em quantas ele escolheu a resposta certa e em
    # quantas voltou a escolher a mesma ideia.
    "n_beliefs_retested", "n_beliefs_corrected", "n_beliefs_still_held",
    "n_socratic_steps", "n_explanations", "n_regressions", "n_diagram_toggles",
    "ms_diagnostic", "ms_variation", "ms_correction", "ms_diagram", "ms_conclusion",
    "ms_total_recorded", "last_kc", "last_event",
]


def linha_sessions(d: Domain, sessao: dict, eventos: Sequence[store_events.Event]) -> dict:
    """Uma linha por sessão.

    Os `ms_*` são a base do pareamento do §8. Somam o `elapsed_ms` que o
    aluno de fato gastou em cada tipo de tela, não a diferença entre
    carimbos de tempo: uma pausa para o pesquisador falar não entra.
    """
    tempos: dict[str, int] = defaultdict(int)
    contagem: dict[str, int] = defaultdict(int)
    completos, em_progresso = [], []
    fim = {}

    for e in eventos:
        contagem[e.type] += 1
        p = e.payload
        ms = int(p.get("elapsed_ms") or 0)

        if e.type == "answer_submitted":
            ciu = d.cius.get(p.get("ciu_id"))
            fase = ciu.phase if ciu else p.get("phase", "diagnostic")
            tempos["variation" if fase == "variation" else "diagnostic"] += ms
        elif e.type in TEMPO_CORRECAO:
            tempos["correction"] += ms
        elif e.type == "stage_acknowledged":
            tempos[p.get("stage", "diagram")] += ms
        elif e.type == "kc_completed":
            completos.append(p.get("kc", ""))
        elif e.type == "kc_incomplete":
            em_progresso.append(p.get("kc", ""))
        elif e.type == "session_ended":
            fim = p

    sequencia = json.loads(sessao["kc_sequence"])
    ultimo_kc = ""
    for e in reversed(eventos):
        if e.payload.get("kc"):
            ultimo_kc = e.payload["kc"]
            break

    return {
        "participant": sessao["participant"],
        "arm": sessao["arm"],
        "session_id": sessao["id"],
        "domain_hash": _hash_do_dominio(eventos),
        "prior_c": sessao.get("prior_c") or "",
        "started_at": sessao["started_at"],
        "ended_at": sessao["ended_at"] or "",
        "end_reason": fim.get("reason", ""),
        # `completed` só é 1 quando TODO KC da sequência fechou. Uma sessão
        # que terminou com um KC "em progresso" conta como parcial: é o
        # numerador da taxa de conclusão do §4.3.
        "completed": 1 if (fim.get("reason") == "concluida") else 0,
        "kc_sequence": "|".join(sequencia),
        "kcs_completed": "|".join(completos),
        "kcs_in_progress": "|".join(em_progresso),
        "n_answers": contagem["answer_submitted"],
        "n_correct": sum(
            1 for e in eventos
            if e.type == "answer_submitted" and e.payload.get("correct")
        ),
        "n_beliefs_detected": contagem["misconception_detected"],
        "n_beliefs_retested": contagem["belief_retested"],
        "n_beliefs_corrected": sum(
            1 for e in eventos
            if e.type == "belief_retested" and e.payload.get("correct")),
        "n_beliefs_still_held": sum(
            1 for e in eventos
            if e.type == "belief_retested" and e.payload.get("still_held")),
        "n_socratic_steps": contagem["socratic_step_answered"],
        "n_explanations": contagem["explanation_acknowledged"],
        "n_regressions": contagem["regression_triggered"],
        "n_diagram_toggles": contagem["diagram_toggled"],
        "ms_diagnostic": tempos["diagnostic"],
        "ms_variation": tempos["variation"],
        "ms_correction": tempos["correction"],
        "ms_diagram": tempos["diagram"],
        "ms_conclusion": tempos["conclusion"],
        "ms_total_recorded": sum(tempos.values()),
        "last_kc": ultimo_kc,
        "last_event": eventos[-1].type if eventos else "",
    }


# --------------------------------------------------------------------------
# calibration.csv — calibração metacognitiva
# --------------------------------------------------------------------------

COLUNAS_CALIBRATION = [
    "participant", "arm", "confidence", "confidence_rank",
    "n", "n_correct", "prop_correct", "mean_elapsed_ms",
]


def linhas_calibration(d: Domain, sessao: dict, eventos: Sequence[store_events.Event]):
    """Uma linha por (participante, nível de confiança).

    O §12 pede "uma linha por par (confiança, acerto)". A tabela de
    contingência pura teria 3×2 = 6 linhas para o estudo inteiro e
    perderia a variância entre participantes — que é justamente o que uma
    correlação de calibração precisa. Este grão agrega o par por
    participante: dá a tabela de contingência somando, e dá a curva de
    calibração individual sem somar.

    `confidence_rank` é a posição na escala de study.yaml, para que a
    análise ordene sem depender do texto do rótulo.
    """
    escala = list(d.study.confidence_scale)
    baldes: dict[str, list] = defaultdict(list)

    for e in eventos:
        if e.type != "answer_submitted":
            continue
        p = e.payload
        baldes[p.get("confidence", "")].append(
            (1 if p.get("correct") else 0, int(p.get("elapsed_ms") or 0))
        )

    for nivel in escala:
        respostas = baldes.get(nivel, [])
        n = len(respostas)
        acertos = sum(c for c, _ in respostas)
        yield {
            "participant": sessao["participant"],
            "arm": sessao["arm"],
            "confidence": nivel,
            "confidence_rank": escala.index(nivel) + 1,
            "n": n,
            "n_correct": acertos,
            "prop_correct": round(acertos / n, 4) if n else "",
            "mean_elapsed_ms": round(sum(m for _, m in respostas) / n) if n else "",
        }


# --------------------------------------------------------------------------
# Escrita
# --------------------------------------------------------------------------

# Caracteres com que uma celula NAO pode comecar num CSV que sera aberto
# em planilha. Excel e LibreOffice tratam esses inicios como formula.
_PERIGOSOS = ("=", "+", "-", "@", chr(9), chr(13))


def neutraliza(valor: Any) -> Any:
    """Impede que uma resposta livre vire formula na planilha.

    As CIUs de lacuna aceitam texto do participante. Um aluno que escreva
    `=1+1` — ou algo pior — teria isso EXECUTADO quando o pesquisador
    abrisse answers.csv. Nao e hipotetico: e o vetor de injecao de formula
    em CSV, e aqui o texto livre vai direto do teclado dele para a planilha.

    O prefixo apostrofo e a mitigacao padrao: a planilha mostra o texto e
    nao o avalia. O dado original continua intacto no log, que e a fonte.
    """
    if isinstance(valor, str) and valor.startswith(_PERIGOSOS):
        return "'" + valor
    return valor


def escreve(caminho: Path, colunas: Sequence[str], linhas: Iterable[dict]) -> int:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: o Excel em português abre acento certo sem perguntar nada.
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(colunas))
        w.writeheader()
        total = 0
        for linha in linhas:
            w.writerow({k: neutraliza(v) for k, v in linha.items()})
            total += 1
    return total


def exporta(
    conn: sqlite3.Connection, d: Domain, destino: Path,
    apenas: Sequence[str] | None = None,
) -> dict[str, int]:
    alvo = sessoes(conn, apenas)
    dados = [(s, store_events.read(conn, s["id"])) for s in alvo]

    return {
        "answers.csv": escreve(
            destino / "answers.csv", COLUNAS_ANSWERS,
            (l for s, ev in dados for l in linhas_answers(d, s, ev))),
        "sessions.csv": escreve(
            destino / "sessions.csv", COLUNAS_SESSIONS,
            (linha_sessions(d, s, ev) for s, ev in dados)),
        "calibration.csv": escreve(
            destino / "calibration.csv", COLUNAS_CALIBRATION,
            (l for s, ev in dados for l in linhas_calibration(d, s, ev))),
    }


def hashes_divergentes(conn: sqlite3.Connection,
                       apenas: Sequence[str] | None = None) -> dict[str, list[str]]:
    """Sessões agrupadas pelo hash do domínio que viram (§15).

    Mais de um grupo significa que o conteúdo mudou no meio da coleta e os
    dados não são comparáveis sem ressalva. É a primeira pergunta quando
    os resultados surpreendem, e ela tem de ser respondida ANTES da
    análise, não depois.
    """
    grupos: dict[str, list[str]] = defaultdict(list)
    for s in sessoes(conn, apenas):
        grupos[_hash_do_dominio(store_events.read(conn, s["id"]))].append(s["id"])
    return dict(grupos)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Exporta as três tabelas de análise (§12).")
    p.add_argument("--db", default=None, help="banco (padrão: data/structura.db)")
    p.add_argument("--out", default="analise", help="diretório de saída")
    p.add_argument("--sessions", nargs="*", default=None, help="ids; vazio = todas")
    args = p.parse_args(argv)

    d = load()
    conn = store_events.open_db(args.db)
    try:
        grupos = hashes_divergentes(conn, args.sessions)
        if not grupos:
            print("nenhuma sessão no banco.")
            return 0

        contagens = exporta(conn, d, Path(args.out), args.sessions)
    finally:
        conn.close()

    for nome, n in contagens.items():
        print("  %-18s %4d linha(s)" % (nome, n))
    print("\nescrito em: %s" % Path(args.out).resolve())

    if len(grupos) > 1:
        print("\nATENÇÃO — o domínio mudou durante a coleta (§15).")
        print("Os participantes NÃO viram o mesmo conteúdo. Grupos:")
        for h, ids in sorted(grupos.items()):
            print("  %s  %d sessão(ões): %s" % (h[:23] or "(sem hash)", len(ids),
                                                ", ".join(ids[:6])))
        return 1

    hash_unico = next(iter(grupos))
    print("domínio único em toda a coleta: %s" % (hash_unico or "(sem hash)"))
    if hash_unico != d.hash:
        print("AVISO: o domínio no disco AGORA (%s) não é o que foi coletado."
              % d.hash[:23])
        print("       As colunas de metadado de CIU vieram do domínio atual.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
