"""Reprojeta sessoes a partir do log e confere o estado derivado (RNF04).

Tres usos, todos sobre o mesmo banco:

    python -m tools.replay --verify              # nao escreve nada; sai 1 se divergir
    python -m tools.replay --rebuild             # apaga node_state e reconstroi
    python -m tools.replay --print SESSION_ID    # linha do tempo legivel da sessao

`--verify` e a porta que fecha a Definition of Done: se ela sai 0, o estado
de qualquer sessao e reconstruivel do log. Rode depois de cada coleta, antes
de copiar o .db para as duas midias (§15).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from store import events as ev  # noqa: E402
from store import projections as pr  # noqa: E402


def cmd_verify(conn, sessoes: list[str]) -> int:
    falhas = 0
    for sid in sessoes:
        divergencias = pr.verify(conn, sid)
        checkpoints = pr.checkpoint_mismatches(conn, sid)
        if not divergencias and not checkpoints:
            print("OK   %s  (%d eventos)" % (sid, ev.last_seq(conn, sid)))
            continue
        falhas += 1
        print("FALHA %s" % sid)
        for d in divergencias:
            print("      estado derivado != log -> %s" % d)
        for c in checkpoints:
            print("      checkpoint kc_completed -> %s" % c)
    if falhas:
        print("\n%d sessao(oes) divergente(s). RNF04 NAO satisfeito." % falhas)
        return 1
    print("\n%d sessao(oes) conferida(s). RNF04 satisfeito." % len(sessoes))
    return 0


def cmd_rebuild(conn, sessoes: list[str]) -> int:
    for sid in sessoes:
        proj = pr.rebuild(conn, sid)
        print("reconstruido %s: %d no(s) em %d KC(s)"
              % (sid, len(proj), len(pr.kcs_tocados(proj))))
    return 0


def cmd_print(conn, sessoes: list[str]) -> int:
    for sid in sessoes:
        linhas = ev.read(conn, sid)
        print("=== %s  (%d eventos) ===" % (sid, len(linhas)))
        for e in linhas:
            corpo = {k: v for k, v in e.payload.items() if k != "node_updates"}
            print("  %4d  %-24s %s" % (e.seq, e.type, json.dumps(corpo, ensure_ascii=False)))
            for u in e.node_updates:
                print("        -> %s/%s = %s" % (u["kc"], u["node"], u["state"]))
        proj = pr.project(linhas)
        for kc in pr.kcs_tocados(proj):
            print("  vetor %s: %s" % (kc, json.dumps(pr.vector(proj, kc), ensure_ascii=False)))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Reprojeta e confere sessoes do Structura.")
    p.add_argument("--db", default=None, help="caminho do banco (padrao: data/structura.db)")
    p.add_argument("sessions", nargs="*", help="ids de sessao; vazio = todas")
    modo = p.add_mutually_exclusive_group()
    modo.add_argument("--verify", action="store_true", help="so confere, nao escreve (padrao)")
    modo.add_argument("--rebuild", action="store_true", help="apaga e reconstroi node_state")
    modo.add_argument("--print", dest="printar", action="store_true", help="linha do tempo")
    args = p.parse_args(argv)

    conn = ev.open_db(args.db)
    try:
        sessoes = args.sessions or ev.session_ids(conn)
        if not sessoes:
            print("nenhuma sessao no banco.")
            return 0
        if args.rebuild:
            return cmd_rebuild(conn, sessoes)
        if args.printar:
            return cmd_print(conn, sessoes)
        return cmd_verify(conn, sessoes)
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
