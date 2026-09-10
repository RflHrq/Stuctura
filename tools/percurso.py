"""O percurso de cada participante, desenhado sobre o grafo.

Lê o log e reconstrói, para cada sessão e cada KC, o caminho que a pessoa
de fato andou: em que ordem os nós foram perguntados, quais ela sustentou,
onde errou, para onde o traversal voltou, e em que estado o KC terminou.

Só lê `events`, que é append-only e é a FONTE. Nunca lê `node_state`, que é
projeção descartável (§4): uma leitura de análise que dependesse dela
passaria a depender de um cache, e a reconstrução deixaria de valer como
prova na defesa.

    python -m tools.simular                                   # se não houver dados
    python -m tools.percurso --db data/simulado.db -o analise/percursos.html
    python -m tools.percurso --db data/structura.db -o analise/percursos.html
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import model, socratic
from engine.loader import Domain, load
from store import events as store_events
from tools.grafo import alcancaveis, camadas, curto, posicionar


def sessoes(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute(
        "SELECT s.id, s.participant, s.arm, s.kc_sequence, s.started_at,"
        "       s.ended_at, p.prior_c "
        "FROM sessions s JOIN participants p ON p.code = s.participant "
        "ORDER BY s.participant, s.started_at"))


def percurso(conn: sqlite3.Connection, domain: Domain, sid: str) -> dict:
    """Reconstrói uma sessão a partir dos eventos, em ordem de `seq`.

    A ordem do log É a ordem em que aconteceu: `seq` é 1..n sem buraco, e a
    tabela é append-only. Não há o que reordenar nem o que interpretar.
    """
    linhas = list(conn.execute(
        "SELECT seq, type, payload FROM events WHERE session_id = ? ORDER BY seq",
        (sid,)))
    cabecalho = conn.execute(
        "SELECT kc_sequence FROM sessions WHERE id = ?", (sid,)).fetchone()

    kcs: dict[str, dict] = {}
    atividades: list[dict] = []
    vetor: dict[tuple[str, str], str] = {}
    total_ms = 0
    ordem_kcs: list[str] = []

    # O KC DA SESSÃO, que não é o mesmo que o KC do nó perguntado. Um passo
    # de traversal do kc_09 pode cair em kc_06:B1, porque o suporte
    # atravessa KCs — e atribuir esse passo ao kc_06 inventaria um KC que
    # a sessão nunca percorreu. A fronteira certa é `kc_completed` /
    # `kc_incomplete`, que é onde a FSM de fato vira a página.
    sequencia = list(json.loads(cabecalho["kc_sequence"])) if cabecalho else []
    idx_kc = 0

    def kc_sessao() -> str:
        return sequencia[idx_kc] if idx_kc < len(sequencia) else (
            sequencia[-1] if sequencia else "?")

    def bloco(kc: str) -> dict:
        if kc not in kcs:
            kcs[kc] = {"kc": kc, "visitas": [], "regressoes": [],
                       "crenca": None, "desfecho": None, "ms": 0,
                       "atividades": 0, "acertos": 0}
            ordem_kcs.append(kc)
        return kcs[kc]

    for seq, tipo, bruto in linhas:
        p = json.loads(bruto)
        for u in p.get("node_updates") or ():
            vetor[(u["kc"], u["node"])] = u["state"]

        if tipo == "ciu_presented":
            bloco(kc_sessao())

        elif tipo == "answer_submitted":
            ciu = domain.cius.get(p["ciu_id"])
            kc = kc_sessao()
            b = bloco(kc)
            b["atividades"] += 1
            b["ms"] += p.get("elapsed_ms", 0)
            if p.get("correct"):
                b["acertos"] += 1
            atividades.append({
                "seq": seq, "kc": kc, "ciu": p["ciu_id"],
                "fase": ciu.phase if ciu else "?",
                "tipo": ciu.type if ciu else "?",
                "correct": bool(p.get("correct")),
                "confianca": p.get("confidence"),
                "distrator": p.get("misconception_id"),
                "ms": p.get("elapsed_ms", 0),
                "exibido": p.get("displayed_idx"),
                "canonico": p.get("option_idx"),
            })

        elif tipo == "misconception_detected":
            b = bloco(kc_sessao())
            b["crenca"] = p["misconception_id"]

        elif tipo in ("socratic_step_answered", "explanation_acknowledged"):
            b = bloco(kc_sessao())
            b["ms"] += p.get("elapsed_ms", 0)
            b["visitas"].append({
                "seq": seq, "node": "%s:%s" % (p["kc"], p["node"]),
                # No braço direto não há como errar: a confirmação é de
                # leitura. Registrar `accepted` ali seria inventar um dado.
                "aceito": bool(p.get("accepted")) if tipo.startswith("socratic")
                          else None,
                "ms": p.get("elapsed_ms", 0),
            })

        elif tipo == "regression_triggered":
            bloco(kc_sessao())["regressoes"].append(
                {"seq": seq, "de": p["from_node"], "para": p["to_node"]})

        elif tipo == "kc_completed":
            bloco(p["kc"])["desfecho"] = "completo"
            idx_kc += 1
        elif tipo == "kc_incomplete":
            b = bloco(p["kc"])
            b["desfecho"] = "em progresso"
            b["travou"] = p.get("node")
            idx_kc += 1
        elif tipo == "session_ended":
            total_ms = p.get("total_ms", 0)

    # O estado cognitivo é LIDO do vetor reconstruído, pela mesma função que
    # o motor usa em sessão — não recalculado com outra regra aqui.
    for kc in ordem_kcs:
        kcs[kc]["estado"] = model.cognitive_state(domain, vetor, kc)
        kcs[kc]["vetor"] = {n: model.state_of(vetor, kc, n)
                            for n in domain.kcs[kc].nodes}

    return {"kcs": [kcs[k] for k in ordem_kcs], "atividades": atividades,
            "total_ms": total_ms}


def grafo_de(domain: Domain, kc_id: str) -> dict:
    refs = alcancaveis(domain, kc_id)
    pos, W, H = posicionar(domain, kc_id, refs, camadas(domain, refs))
    kc = domain.kcs[kc_id]
    dentro = set(refs)
    return {
        "id": kc_id, "nome": kc.name, "W": W, "H": H,
        "nos": [{
            "id": "%s:%s" % r, "kc": r[0], "node": r[1],
            "tipo": domain.node(*r).type,
            "fora": r[0] != kc_id,
            "conclusao": r[0] == kc_id and r[1] == kc.conclusion_node,
            "curto": curto(domain.node(*r).plain or domain.node(*r).text),
            "plain": domain.node(*r).plain or domain.node(*r).text,
            "sup": ["%s:%s" % s for s in domain.node(*r).support if s in dentro],
            "x": pos[r][0], "y": pos[r][1],
        } for r in refs],
    }


def dados(conn: sqlite3.Connection, domain: Domain) -> dict:
    rows = sessoes(conn)
    usados: set[str] = set()
    saida_s = []
    for r in rows:
        pc = percurso(conn, domain, r["id"])
        for b in pc["kcs"]:
            if b["kc"] in domain.kcs:
                usados.add(b["kc"])
        saida_s.append({
            "id": r["id"], "code": r["participant"], "arm": r["arm"],
            "prior_c": r["prior_c"], "inicio": r["started_at"],
            "fim": r["ended_at"], "simulado": r["participant"].startswith("SIM"),
            **pc,
        })
    return {
        "hash": domain.hash.replace("sha256:", "")[:8],
        "sessoes": saida_s,
        "grafos": {k: grafo_de(domain, k) for k in sorted(usados)},
        "crencas": {m.id: {"belief": m.belief, "nega": "%s:%s" % (m.kc, m.node),
                           "grade": m.grade}
                    for m in domain.misconceptions.values()},
        "conclusoes": {k: domain.kcs[k].conclusion for k in sorted(usados)},
    }


def pagina(db: str, path: str | None = None) -> str:
    domain = load(path)
    conn = store_events.connect(db)
    try:
        d = dados(conn, domain)
    finally:
        conn.close()
    if not d["sessoes"]:
        raise SystemExit(
            "nenhuma sessão em %s.\n"
            "Se ainda não há coleta: python -m tools.simular" % db)
    return TEMPLATE.replace("__DADOS__", json.dumps(d, ensure_ascii=False))


TEMPLATE = r"""<meta charset="utf-8">
<title>Percursos dos Participantes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@600&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  --paper:#f7f7f4; --card:#ffffff; --sunk:#eeeeea;
  --ink:#16181a; --ink-2:#414850; --mute:#6b737b;
  --rule:#e0e0da; --rule-2:#c3c6c0;
  --accent:#22566e; --accent-bg:#dfeaef;
  --base:#4c5a63;  --base-bg:#e8ecee;
  --bad:#94372a;   --bad-bg:#f7e5e1;
  --ok:#1b6647;    --ok-bg:#dfefe7;
  --warn:#8a6212;  --warn-bg:#f6eddb;
  --shadow:0 1px 2px rgba(22,24,26,.05), 0 12px 30px -24px rgba(22,24,26,.5);
  --serif:"Spectral",Georgia,serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#111315; --card:#191c1e; --sunk:#212427;
  --ink:#eaecee; --ink-2:#bdc4c9; --mute:#889197;
  --rule:#282c2f; --rule-2:#3b4146;
  --accent:#79b8ce; --accent-bg:#132831;
  --base:#9aa8b1;  --base-bg:#1d2124;
  --bad:#e08c7c;   --bad-bg:#31201c;
  --ok:#61c398;    --ok-bg:#112a20;
  --warn:#d9ae5b;  --warn-bg:#2e2313;
  --shadow:0 1px 2px rgba(0,0,0,.5), 0 12px 30px -24px rgba(0,0,0,.95);
}}
:root[data-theme="dark"]{
  --paper:#111315; --card:#191c1e; --sunk:#212427;
  --ink:#eaecee; --ink-2:#bdc4c9; --mute:#889197;
  --rule:#282c2f; --rule-2:#3b4146;
  --accent:#79b8ce; --accent-bg:#132831;
  --base:#9aa8b1;  --base-bg:#1d2124;
  --bad:#e08c7c;   --bad-bg:#31201c;
  --ok:#61c398;    --ok-bg:#112a20;
  --warn:#d9ae5b;  --warn-bg:#2e2313;
  --shadow:0 1px 2px rgba(0,0,0,.5), 0 12px 30px -24px rgba(0,0,0,.95);
}
*{box-sizing:border-box}
body{background:var(--paper); color:var(--ink); font-family:var(--sans);
     font-size:16px; line-height:1.55; margin:0; padding:26px 20px 72px}
.wrap{max-width:1280px; margin:0 auto}
h1{font-family:var(--serif); font-size:31px; line-height:1.14; margin:0 0 6px;
   font-weight:600; letter-spacing:-.012em}
h2{font-family:var(--serif); font-size:20px; margin:0; font-weight:600}
.sub{color:var(--mute); font-size:14.5px; margin:0 0 20px; max-width:78ch}
.eyebrow{font-family:var(--mono); font-size:11px; letter-spacing:.13em;
         text-transform:uppercase; color:var(--mute); margin:0 0 8px}
code{font-family:var(--mono); font-size:.88em; background:var(--sunk);
     padding:1px 5px; border-radius:4px; border:1px solid var(--rule)}

.cartao{background:var(--card); border:1px solid var(--rule); border-radius:12px;
        box-shadow:var(--shadow); padding:18px 20px; margin-bottom:20px}
.rolar{overflow-x:auto; margin:0 -4px; padding:0 4px}
.rolar svg{display:block; height:auto}
.barra{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px}
.rot{font-family:var(--mono); font-size:11px; letter-spacing:.1em;
     text-transform:uppercase; color:var(--mute)}

button{font:inherit; font-size:13.5px; cursor:pointer; border-radius:7px;
       border:1px solid var(--rule-2); background:var(--card); color:var(--ink);
       padding:6px 12px; transition:background .12s, border-color .12s}
button:hover{border-color:var(--accent)}
button:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
button[aria-pressed="true"]{background:var(--accent); border-color:var(--accent);
       color:var(--card); font-weight:500}
button.p{font-family:var(--mono); font-size:12.5px; padding:5px 10px}

.aviso-sim{background:var(--warn-bg); border:1px solid var(--warn);
  border-radius:9px; padding:11px 15px; margin-bottom:20px;
  font-size:14px; color:var(--ink-2)}
.aviso-sim b{color:var(--warn)}

.duas{display:grid; grid-template-columns:minmax(0,1fr) 348px; gap:20px;
      align-items:start}
@media (max-width:1000px){.duas{grid-template-columns:minmax(0,1fr)}}
.lado{display:flex; flex-direction:column; gap:20px}
.bloco h3{font-family:var(--sans); font-size:11px; letter-spacing:.11em;
          text-transform:uppercase; color:var(--mute); margin:0 0 10px;
          font-weight:600}

.pills{display:flex; flex-wrap:wrap; gap:7px; margin-bottom:14px}
.pill{font-size:12.5px; padding:4px 10px; border-radius:20px;
      border:1px solid var(--rule-2); background:var(--sunk); color:var(--ink-2)}
.pill b{font-family:var(--mono); font-weight:500}
.pill.est-misconception{background:var(--bad-bg); border-color:var(--bad); color:var(--bad)}
.pill.est-dominado{background:var(--ok-bg); border-color:var(--ok); color:var(--ok)}
.pill.est-lacuna{background:var(--warn-bg); border-color:var(--warn); color:var(--warn)}
.pill.est-desconhecimento{background:var(--sunk); border-color:var(--rule-2); color:var(--mute)}

table{border-collapse:collapse; width:100%; font-size:13px}
th{text-align:left; font-family:var(--mono); font-size:10.5px; font-weight:500;
   letter-spacing:.08em; text-transform:uppercase; color:var(--mute);
   padding:0 8px 7px 0; border-bottom:1px solid var(--rule-2); white-space:nowrap}
td{padding:6px 8px 6px 0; border-bottom:1px solid var(--rule); vertical-align:top}
tr:last-child td{border-bottom:none}
td.k{font-family:var(--mono); color:var(--mute); white-space:nowrap; width:1%}
td.n{font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap}
.cifra{font-family:var(--mono); font-variant-numeric:tabular-nums}
.sim{color:var(--ok); font-weight:600}
.nao{color:var(--bad); font-weight:600}
.leitura{color:var(--mute)}

.trilha{display:flex; flex-direction:column; gap:2px; max-height:340px;
        overflow-y:auto; margin:0 -4px; padding:2px 4px}
.tv{display:flex; gap:9px; align-items:baseline; font-size:13px;
    padding:4px 8px; border-radius:6px}
.tv:nth-child(odd){background:var(--sunk)}
.tv .o{font-family:var(--mono); font-size:11px; color:var(--mute); width:22px;
       flex:none; text-align:right}
.tv .no{font-family:var(--mono); font-size:12px; width:62px; flex:none}
.tv .t{flex:1; color:var(--ink-2); font-size:12.5px}
.tv .ms{font-family:var(--mono); font-size:11px; color:var(--mute); flex:none}
.tv.err{background:var(--bad-bg)}
.tv.reg{background:var(--warn-bg); font-style:italic; color:var(--warn)}

.legenda{display:flex; flex-wrap:wrap; gap:6px 15px; margin-top:12px;
         font-size:12.5px; color:var(--mute)}
.legenda span{display:flex; align-items:center; gap:6px}
.sw{width:13px; height:13px; border-radius:3px; flex:none}

.n-id{font-family:var(--mono); font-size:11px; font-weight:500}
.n-t{font-family:var(--sans); font-size:10.5px}
.e{fill:none; stroke:var(--mute); stroke-width:1.5; opacity:.42}
.e.andada{stroke:var(--accent); stroke-width:2.4; opacity:1}
.e.fora{stroke-dasharray:5 4}
.rodape{font-family:var(--mono); font-size:10px; fill:var(--mute)}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
</style>

<div class="wrap">
  <p class="eyebrow">Structura · análise de percurso · domínio <span id="h"></span></p>
  <h1>Percursos dos participantes</h1>
  <p class="sub">
    O caminho que cada pessoa andou pelo grafo, reconstruído do log de eventos.
    Só a tabela <code>events</code> é lida — que é append-only e é a fonte.
    <code>node_state</code> é projeção descartável e não entra aqui.
  </p>

  <div id="aviso" class="aviso-sim" hidden></div>

  <div class="cartao">
    <div class="barra"><span class="rot">Participante</span><span id="bp"></span></div>
    <div class="pills" id="resumo"></div>
    <div class="barra" style="margin:0"><span class="rot">KC</span><span id="bk"></span></div>
  </div>

  <div class="duas">
    <div class="cartao" style="margin:0">
      <div class="barra"><h2 id="g-tit"></h2></div>
      <div class="rolar"><svg id="svg" role="img"></svg></div>
      <div class="legenda">
        <span><i class="sw" style="background:var(--ok-bg);border:1.5px solid var(--ok)"></i>confirmado</span>
        <span><i class="sw" style="background:var(--bad-bg);border:1.5px solid var(--bad)"></i>crença ativa</span>
        <span><i class="sw" style="background:var(--warn-bg);border:1.5px solid var(--warn)"></i>ausente (ele sabe que não sabe)</span>
        <span><i class="sw" style="background:var(--card);border:1.5px solid var(--rule-2)"></i>nunca visitado</span>
        <span>o número é a ordem em que o nó foi perguntado</span>
      </div>
    </div>

    <div class="lado">
      <div class="cartao bloco" style="margin:0">
        <h3>Este KC</h3>
        <table id="t-kc"></table>
      </div>
      <div class="cartao bloco" style="margin:0">
        <h3>A trilha, passo a passo</h3>
        <div id="trilha" class="trilha"></div>
      </div>
      <div class="cartao bloco" style="margin:0">
        <h3>Atividades respondidas</h3>
        <table id="t-ciu"></table>
      </div>
    </div>
  </div>
</div>

<script>
var D = __DADOS__;
var S = { s:0, kc:null };

function $(id){ return document.getElementById(id); }
var NS = "http://www.w3.org/2000/svg";
function el(n,a,t){
  var e = document.createElementNS(NS,n);
  for (var k in a) if (a[k] !== null && a[k] !== undefined) e.setAttribute(k,a[k]);
  if (t !== undefined) e.textContent = t;
  return e;
}
function esc(t){
  return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
function seg(ms){
  if (!ms) return "—";
  var s = Math.round(ms/1000);
  return s < 90 ? s + "s" : Math.floor(s/60) + "m" + ("0"+(s%60)).slice(-2);
}
function sessao(){ return D.sessoes[S.s]; }
function blocoKC(){
  var b = sessao().kcs.filter(function(x){ return x.kc === S.kc; });
  return b[0] || null;
}

/* ------------------------------------------------------------- controles */
function montaParticipantes(){
  var c = $("bp"); c.innerHTML = "";
  D.sessoes.forEach(function(s, i){
    var b = document.createElement("button");
    b.className = "p"; b.textContent = s.code;
    b.title = s.arm + " · " + (s.prior_c || "");
    b.onclick = function(){ S.s = i; S.kc = null; tudo(); };
    c.appendChild(b);
  });
}

function montaKCs(){
  var c = $("bk"); c.innerHTML = "";
  var ks = sessao().kcs.filter(function(b){ return D.grafos[b.kc]; });
  if (!S.kc || !ks.filter(function(b){ return b.kc === S.kc; }).length)
    S.kc = ks.length ? ks[0].kc : null;
  ks.forEach(function(b){
    var t = document.createElement("button");
    t.className = "p";
    t.textContent = b.kc.replace("kc_","KC ");
    t.setAttribute("aria-pressed", b.kc === S.kc ? "true" : "false");
    t.onclick = function(){ S.kc = b.kc; tudo(); };
    c.appendChild(t);
  });
}

/* ---------------------------------------------------------------- resumo */
function resumo(){
  var s = sessao();
  var p = [
    ["participante", s.code],
    ["braço", s.arm === "socratic" ? "socrático" : "direto"],
    ["experiência", s.prior_c || "—"],
    ["duração", seg(s.total_ms)],
    ["atividades", s.atividades.length]
  ].map(function(x){
    return "<span class='pill'>" + x[0] + " <b>" + esc(x[1]) + "</b></span>";
  });
  s.kcs.forEach(function(b){
    p.push("<span class='pill est-" + b.estado + "'>"
      + b.kc.replace("kc_","KC ") + " <b>" + b.estado + "</b></span>");
  });
  $("resumo").innerHTML = p.join("");

  var sim = D.sessoes.filter(function(x){ return x.simulado; }).length;
  var av = $("aviso");
  if (sim){
    av.hidden = false;
    av.innerHTML = "<b>Dados simulados.</b> " + sim + " das " + D.sessoes.length
      + " sessões têm código <code>SIM…</code> — foram geradas por "
      + "<code>tools/simular.py</code> para exercitar esta tela antes do piloto. "
      + "Elas passaram pelo mesmo motor e gravaram os mesmos eventos que uma "
      + "sessão real, mas as respostas são sorteadas: <b>não interprete os "
      + "números como resultado</b>.";
  } else { av.hidden = true; }
}

/* --------------------------------------------------------------- desenho */
function desenha(){
  var g = D.grafos[S.kc], b = blocoKC(), s = $("svg");
  s.innerHTML = "";
  if (!g || !b){ return; }
  s.setAttribute("viewBox", "0 0 " + g.W + " " + g.H);
  s.setAttribute("width", g.W);
  s.setAttribute("aria-label", "Percurso de " + sessao().code + " pelo "
    + g.id + ", " + g.nome);

  var defs = el("defs");
  [["st","var(--mute)"],["st-a","var(--accent)"]].forEach(function(pp){
    var m = el("marker",{id:pp[0],markerWidth:8,markerHeight:8,
                         refX:7,refY:3.5,orient:"auto"});
    m.appendChild(el("path",{d:"M0,0 L8,3.5 L0,7 z", fill:pp[1]}));
    defs.appendChild(m);
  });
  s.appendChild(defs);

  /* Um nó pode ter sido perguntado mais de uma vez — é o que a regressão
     faz. A ordem mostrada é a da PRIMEIRA vez; o contador de visitas fica
     ao lado, porque repetir é informação. */
  var primeira = {}, vezes = {}, errou = {};
  b.visitas.forEach(function(v, i){
    if (primeira[v.node] === undefined) primeira[v.node] = Object.keys(primeira).length + 1;
    vezes[v.node] = (vezes[v.node] || 0) + 1;
    if (v.aceito === false) errou[v.node] = (errou[v.node] || 0) + 1;
  });

  var nomes = {};
  g.nos.forEach(function(n){ nomes[n.id] = n; });

  g.nos.forEach(function(n){
    n.sup.forEach(function(sid){
      var a = nomes[sid]; if (!a) return;
      var andada = primeira[sid] && primeira[n.id];
      s.appendChild(el("path",{
        "class":"e" + (andada ? " andada" : "") + (a.fora ? " fora" : ""),
        d:"M" + (a.x+66) + "," + a.y + " C" + (a.x+66) + "," + (a.y-26) + " "
          + (n.x+66) + "," + (n.y+50+26) + " " + (n.x+66) + "," + (n.y+50),
        "marker-end":"url(#" + (andada ? "st-a" : "st") + ")"}));
    });
  });

  g.nos.forEach(function(n){
    var est = b.vetor[n.node];              // só os nós do próprio KC têm estado
    var fill="var(--card)", stroke="var(--rule-2)", w=1.5, idc="var(--mute)", op=1;
    if (est === "confirmed"){ fill="var(--ok-bg)"; stroke="var(--ok)"; idc="var(--ok)"; }
    else if (est === "wrong"){ fill="var(--bad-bg)"; stroke="var(--bad)"; w=2.2; idc="var(--bad)"; }
    else if (est === "absent"){ fill="var(--warn-bg)"; stroke="var(--warn)"; idc="var(--warn)"; }
    else if (!primeira[n.id]) op = 0.4;

    var grp = el("g",{opacity:op});
    grp.appendChild(el("rect",{x:n.x,y:n.y,width:132,height:50,rx:6,
      fill:fill, stroke:stroke, "stroke-width":w,
      "stroke-dasharray": n.fora ? "5 4" : null}));
    grp.appendChild(el("text",{x:n.x+8,y:n.y+17,"class":"n-id",fill:idc},
      (n.fora ? n.kc.replace("kc_","")+"·" : "") + n.node));

    if (primeira[n.id]){
      grp.appendChild(el("circle",{cx:n.x+116,cy:n.y+13,r:10,
        fill: errou[n.id] ? "var(--bad)" : "var(--accent)"}));
      grp.appendChild(el("text",{x:n.x+116,y:n.y+17,"class":"n-id",
        "text-anchor":"middle",fill:"var(--card)"}, primeira[n.id]));
      if (vezes[n.id] > 1){
        grp.appendChild(el("text",{x:n.x+124,y:n.y+46,"class":"n-t",
          "text-anchor":"end",fill:"var(--bad)"}, vezes[n.id] + " visitas"));
      }
    }
    n.curto.forEach(function(linha,i){
      grp.appendChild(el("text",{x:n.x+8,y:n.y+34+i*11,"class":"n-t",
        fill:"var(--ink-2)"}, linha));
    });
    var t = el("title");
    t.textContent = n.plain + (primeira[n.id]
      ? "   [perguntado em " + primeira[n.id] + "º lugar"
        + (vezes[n.id] > 1 ? ", " + vezes[n.id] + " vezes" : "") + "]"
      : "   [nunca perguntado nesta sessão]");
    grp.appendChild(t);
    s.appendChild(grp);
  });

  s.appendChild(el("text",{x:22,y:g.H-8,"class":"rodape"},
    "o número é a ordem da caminhada · vermelho = houve erro neste nó · tracejado = nó de outro KC"));
}

/* --------------------------------------------------------------- painéis */
function painel(){
  var g = D.grafos[S.kc], b = blocoKC();
  $("g-tit").textContent = g ? (g.id.replace("kc_","KC ") + " — " + g.nome) : "—";
  if (!b){ $("t-kc").innerHTML = ""; $("trilha").innerHTML = ""; return; }

  var cr = b.crenca ? D.crencas[b.crenca] : null;
  var l = [
    ["estado final", "<span class='pill est-" + b.estado + "' style='padding:2px 8px'>"
      + b.estado + "</span>"],
    ["desfecho", b.desfecho === "completo"
      ? "<span class='sim'>completo</span>"
      : "<span class='nao'>" + (b.desfecho || "—") + "</span>"
        + (b.travou ? " <span class='leitura'>(travou em " + b.travou + ")</span>" : "")],
    ["crença detectada", cr
      ? "<span style='color:var(--bad)'>" + esc(cr.belief) + "</span>"
        + "<br><span class='leitura'>nega " + cr.nega.split(":")[1]
        + " · grau " + cr.grade + "</span>"
      : "<span class='leitura'>nenhuma</span>"],
    ["passos andados", "<span class='cifra'>" + b.visitas.length + "</span>"],
    ["regressões", "<span class='cifra'>" + b.regressoes.length + "</span>"],
    ["tempo no KC", "<span class='cifra'>" + seg(b.ms) + "</span>"],
    ["atividades", "<span class='cifra'>" + b.acertos + "/" + b.atividades
      + "</span> <span class='leitura'>certas</span>"]
  ];
  $("t-kc").innerHTML = l.map(function(x){
    return "<tr><td class='k'>" + x[0] + "</td><td>" + x[1] + "</td></tr>";
  }).join("");

  var reg = {};
  b.regressoes.forEach(function(r){ reg[r.seq] = r; });
  var linhas = [], n = 0;
  b.visitas.forEach(function(v){
    n++;
    var marca = v.aceito === null
      ? "<span class='leitura'>leu e confirmou</span>"
      : (v.aceito ? "<span class='sim'>sustentou</span>"
                  : "<span class='nao'>não sustentou</span>");
    linhas.push("<div class='tv" + (v.aceito === false ? " err" : "") + "'>"
      + "<span class='o'>" + n + "</span>"
      + "<span class='no'>" + esc(v.node.split(":")[1]) + "</span>"
      + "<span class='t'>" + marca + "</span>"
      + "<span class='ms'>" + seg(v.ms) + "</span></div>");
    var r = reg[v.seq + 1] || reg[v.seq + 2];
    if (r){
      linhas.push("<div class='tv reg'><span class='o'>↰</span>"
        + "<span class='no'></span><span class='t'>regressão: voltou de "
        + esc(r.de) + " para " + esc(r.para) + "</span><span class='ms'></span></div>");
      delete reg[r.seq];
    }
  });
  $("trilha").innerHTML = linhas.join("")
    || "<span class='leitura'>nenhum passo de traversal neste KC</span>";

  var ats = sessao().atividades.filter(function(a){ return a.kc === S.kc; });
  $("t-ciu").innerHTML =
    "<tr><th>atividade</th><th>fase</th><th>resp.</th><th>confiança</th><th>tempo</th></tr>"
    + ats.map(function(a){
        return "<tr><td class='k'>" + esc(a.ciu.replace("ciu_","")) + "</td>"
          + "<td class='leitura'>" + esc(a.fase) + "</td>"
          + "<td>" + (a.correct ? "<span class='sim'>✓</span>"
                                : "<span class='nao'>✗</span>"
                                  + (a.distrator ? " <span class='leitura'>"
                                     + esc(a.distrator) + "</span>" : "")) + "</td>"
          + "<td class='leitura'>" + esc(a.confianca || "") + "</td>"
          + "<td class='n'>" + seg(a.ms) + "</td></tr>";
      }).join("");
}

function tudo(){
  [].forEach.call($("bp").querySelectorAll("button"), function(b,i){
    b.setAttribute("aria-pressed", i === S.s ? "true" : "false");
  });
  montaKCs(); resumo(); desenha(); painel();
}

$("h").textContent = D.hash;
montaParticipantes();
tudo();
</script>
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default="data/simulado.db", help="banco a ler")
    p.add_argument("--path", default=None, help="diretório do domínio")
    p.add_argument("-o", "--out", default=None, help="arquivo de saída")
    args = p.parse_args(argv)

    saida = pagina(args.db, args.path)
    if args.out:
        Path(args.out).write_text(saida, encoding="utf-8")
        print("escrito em %s" % args.out)
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
