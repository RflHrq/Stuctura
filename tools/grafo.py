"""O mapa das premissas: os 12 grafos, e todos os caminhos por eles.

Para DEMONSTRAR o mecanismo — na qualificação, para o orientador, na banca.
Não lê o banco (não é análise de participante) e não entra na sessão (não é
tela do aluno). É o domínio inteiro desenhado, com as caminhadas por cima.

A página tem dois níveis:

  o MAPA        os 12 KCs na ordem de prerequisito, com o tamanho de cada
                grafo e quanto ele puxa de fora. Clicar expande.

  o GRAFO       um KC aberto, com dois modos de leitura:
                  todos os caminhos  — quantas caminhadas cruzam cada nó
                  um caminho         — a espinha até a conclusão, ou o plano
                                       de refutação de uma crença

  a CAMINHADA   sobre o caminho escolhido, passo a passo, com a opção de
                errar e ver a regressão controlada.

Os textos vêm de `socratic.question()`, os planos de `socratic.plan()`.
Nada aqui reimplementa o motor — exceto a regra das três tentativas,
reproduzida no JavaScript porque a página precisa reagir a um clique; a
versão que vale é `engine.socratic.on_wrong`, e a página diz isso.

    python -m tools.grafo -o analise/mapa.html
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic
from engine.loader import Domain, Ref, load

# Geometria. Largura fixa da caixa para que camadas diferentes fiquem
# alinhadas — desalinhamento é o que faz um grafo desenhado parecer rascunho.
CAIXA_W, CAIXA_H = 132, 50
GAP_X, GAP_Y = 20, 78
MARGEM = 22

KC_W, KC_H = 150, 62
KC_GX, KC_GY = 46, 26


# --------------------------------------------------------------------------
# Grafo de um KC
# --------------------------------------------------------------------------

def alcancaveis(d: Domain, kc_id: str) -> list[Ref]:
    """Os nós do KC mais todo nó de outro KC que o suporte alcança.

    É o *fecho* do KC, não a lista dele: kc_09 tem 10 nós e percorre 19.
    Desenhar só os próprios esconderia metade da cadeia que o participante
    de fato caminha.
    """
    vistos: list[Ref] = []

    def visitar(ref: Ref) -> None:
        if ref in vistos:
            return
        try:
            no = d.node(*ref)
        except KeyError:
            return
        vistos.append(ref)
        for s in no.support:
            visitar(s)

    for n in d.kcs[kc_id].nodes:
        visitar((kc_id, n))
    return vistos


def camadas(d: Domain, refs: list[Ref]) -> dict[Ref, int]:
    """0 para os nós sem suporte, senão 1 + a maior camada do suporte.

    Termina porque o grafo é acíclico — propriedade que o validador
    garante, não que este código presuma.
    """
    dentro = set(refs)
    memo: dict[Ref, int] = {}

    def nivel(ref: Ref) -> int:
        if ref in memo:
            return memo[ref]
        memo[ref] = 0                       # guarda contra ciclo inesperado
        try:
            no = d.node(*ref)
        except KeyError:
            return 0
        sup = [s for s in no.support if s in dentro]
        memo[ref] = 1 + max((nivel(s) for s in sup), default=-1)
        return memo[ref]

    return {r: nivel(r) for r in refs}


def posicionar(d: Domain, kc_id: str, refs: list[Ref], nivel: dict[Ref, int]):
    """Camada 0 embaixo, conclusão em cima.

    Dentro de uma camada os nós são ordenados pelo *baricentro* dos seus
    suportes — a média das posições de quem os sustenta. Duas passagens
    desembaraçam a maioria dos cruzamentos; mais que isso não muda nada
    visível e torna o resultado difícil de prever.
    """
    por_camada: dict[int, list[Ref]] = {}
    for r in refs:
        por_camada.setdefault(nivel[r], []).append(r)
    por_camada[0].sort(key=lambda r: (r[0] != kc_id, r[0], r[1]))

    ordem: dict[Ref, int] = {r: i for i, r in enumerate(por_camada[0])}
    for c in sorted(por_camada)[1:]:
        for _ in range(2):
            def baricentro(r: Ref) -> float:
                sup = [s for s in d.node(*r).support if s in ordem]
                return sum(ordem[s] for s in sup) / len(sup) if sup else 0.0
            por_camada[c].sort(key=baricentro)
            for i, r in enumerate(por_camada[c]):
                ordem[r] = i

    largura = max(len(v) for v in por_camada.values())
    total_w = largura * CAIXA_W + (largura - 1) * GAP_X
    altura = max(por_camada)
    total_h = (altura + 1) * CAIXA_H + altura * GAP_Y

    pos: dict[Ref, tuple[int, int]] = {}
    for c, lista in por_camada.items():
        faixa = len(lista) * CAIXA_W + (len(lista) - 1) * GAP_X
        x0 = MARGEM + (total_w - faixa) / 2
        y = MARGEM + (altura - c) * (CAIXA_H + GAP_Y)
        for i, r in enumerate(lista):
            pos[r] = (int(x0 + i * (CAIXA_W + GAP_X)), int(y))

    return pos, total_w + 2 * MARGEM, total_h + 2 * MARGEM + 24


def curto(texto: str, cols: int = 24, linhas: int = 2) -> list[str]:
    """O rótulo dentro da caixa, quebrado em PALAVRAS.

    Cortar por número de caracteres parte a palavra ao meio, e o rótulo
    passa a mentir sobre o enunciado. O texto inteiro vai para o painel.
    """
    out: list[str] = [""]
    for palavra in texto.strip().rstrip(".").split():
        if not out[-1]:
            out[-1] = palavra
        elif len(out[-1]) + 1 + len(palavra) <= cols:
            out[-1] += " " + palavra
        elif len(out) < linhas:
            out.append(palavra)
        else:
            out[-1] = out[-1][:cols - 1].rstrip() + "…"
            return out
    return out


# --------------------------------------------------------------------------
# Mapa do domínio
# --------------------------------------------------------------------------

def mapa(d: Domain) -> dict:
    """Os 12 KCs posicionados pela profundidade de prerequisito.

    Da esquerda para a direita: cada coluna só pode ser cursada depois das
    anteriores de que ela depende. É a mesma relação que `teaching_order`
    codifica em número — aqui, desenhada.
    """
    niv: dict[str, int] = {}

    def profundidade(k: str) -> int:
        if k in niv:
            return niv[k]
        niv[k] = 0
        pre = [p for p in d.kcs[k].prerequisites if p in d.kcs]
        niv[k] = 1 + max((profundidade(p) for p in pre), default=-1)
        return niv[k]

    for k in d.kcs:
        profundidade(k)

    colunas: dict[int, list[str]] = {}
    for k in d.teaching_sequence():
        colunas.setdefault(niv[k], []).append(k)

    ncol = max(colunas) + 1
    nlin = max(len(v) for v in colunas.values())
    faixa_total = nlin * KC_H + (nlin - 1) * KC_GY
    W = MARGEM * 2 + ncol * KC_W + (ncol - 1) * KC_GX
    H = MARGEM * 2 + faixa_total + 26

    pos: dict[str, tuple[int, int]] = {}
    for c, lista in colunas.items():
        faixa = len(lista) * KC_H + (len(lista) - 1) * KC_GY
        y0 = MARGEM + (faixa_total - faixa) / 2
        for i, k in enumerate(lista):
            pos[k] = (MARGEM + c * (KC_W + KC_GX), int(y0 + i * (KC_H + KC_GY)))

    caixas = []
    for k in d.teaching_sequence():
        kc = d.kcs[k]
        refs = alcancaveis(d, k)
        x, y = pos[k]
        caixas.append({
            "id": k, "nome": kc.name,
            "proprios": len(kc.nodes), "fecho": len(refs),
            "fora": len(refs) - len(kc.nodes),
            "crencas": len(list(d.misconceptions_of(k))),
            "piloto": k in d.pilot_sequence,
            "x": x, "y": y,
        })

    arestas = [{"de": p, "para": k}
               for k in d.teaching_sequence()
               for p in d.kcs[k].prerequisites if p in pos]

    return {"W": W, "H": H, "kcs": caixas, "arestas": arestas}


# --------------------------------------------------------------------------
# Tudo junto
# --------------------------------------------------------------------------

def dados(d: Domain) -> dict:
    saida: dict = {
        "attempts": d.study.max_attempts_per_node,
        "mapa": mapa(d),
        "grafos": {},
        "totais": {
            "nos": sum(len(k.nodes) for k in d.kcs.values()),
            "crencas": len(d.misconceptions),
            "caminhos": len(d.misconceptions) + len(d.kcs),
        },
    }

    for kc_id in d.teaching_sequence():
        kc = d.kcs[kc_id]
        refs = alcancaveis(d, kc_id)
        pos, W, H = posicionar(d, kc_id, refs, camadas(d, refs))

        caminhos = [{
            "id": "__espinha__",
            "rotulo": "o caminho perfeito",
            "detalhe": "a espinha até a conclusão, sem crença no meio",
            "passos": ["%s:%s" % r for r in
                       socratic.full_plan(d, kc_id, kc.conclusion_node)],
            "alvo": "%s:%s" % (kc_id, kc.conclusion_node),
        }]
        for m in d.misconceptions_of(kc_id):
            caminhos.append({
                "id": m.id,
                "rotulo": m.belief,
                "detalhe": "grau %s · nega %s%s" % (
                    m.grade, m.node,
                    " · fundacional" if m.is_foundational else ""),
                "passos": ["%s:%s" % r for r in
                           socratic.full_plan(d, m.kc, m.node)],
                "alvo": "%s:%s" % (m.kc, m.node),
            })

        # Quantos caminhos cruzam cada nó: é o que separa a premissa que
        # sustenta quase tudo da que é folha de um ramo só.
        cruz = Counter(p for c in caminhos for p in set(c["passos"]))
        dentro = set(refs)

        nos = []
        for r in refs:
            no = d.node(*r)
            x, y = pos[r]
            nos.append({
                "id": "%s:%s" % r,
                "kc": r[0], "node": r[1], "tipo": no.type,
                "fora": r[0] != kc_id,
                "conclusao": r[0] == kc_id and r[1] == kc.conclusion_node,
                "curto": curto(no.plain or no.text),
                "plain": no.plain or no.text,
                "pergunta": socratic.question(d, *r),
                "retry": socratic.reformulate(d, socratic.steps_from(d, [r])[0]),
                "sup": ["%s:%s" % s for s in no.support if s in dentro],
                "cruz": cruz.get("%s:%s" % r, 0),
                "x": x, "y": y,
            })

        saida["grafos"][kc_id] = {
            "id": kc_id, "nome": kc.name,
            "conclusao_texto": kc.conclusion,
            "proprios": len(kc.nodes), "fecho": len(refs),
            "W": W, "H": H, "nos": nos, "caminhos": caminhos,
            "maxcruz": max(cruz.values()) if cruz else 1,
        }
    return saida


def pagina(path: str | None = None) -> str:
    d = load(path)
    return (TEMPLATE
            .replace("__DADOS__", json.dumps(dados(d), ensure_ascii=False))
            .replace("__HASH__", d.hash.replace("sha256:", "")[:8]))


TEMPLATE = r"""<title>O Mapa das Premissas</title>
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
h2{font-family:var(--serif); font-size:21px; margin:0; font-weight:600}
.sub{color:var(--mute); font-size:14.5px; margin:0 0 22px; max-width:78ch}
.eyebrow{font-family:var(--mono); font-size:11px; letter-spacing:.13em;
         text-transform:uppercase; color:var(--mute); margin:0 0 8px}
code{font-family:var(--mono); font-size:.88em; background:var(--sunk);
     padding:1px 5px; border-radius:4px; border:1px solid var(--rule)}

.cartao{background:var(--card); border:1px solid var(--rule); border-radius:12px;
        box-shadow:var(--shadow); padding:18px 20px; margin-bottom:20px}
.rolar{overflow-x:auto; margin:0 -4px; padding:0 4px}
.rolar svg{display:block; height:auto}

.barra{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px}

button{font:inherit; font-size:13.5px; cursor:pointer; border-radius:7px;
       border:1px solid var(--rule-2); background:var(--card); color:var(--ink);
       padding:6px 12px; transition:background .12s, border-color .12s}
button:hover{border-color:var(--accent)}
button:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
button[aria-pressed="true"]{background:var(--accent); border-color:var(--accent);
       color:var(--card); font-weight:500}
button.err{border-color:var(--bad); color:var(--bad)}
button.err:hover{background:var(--bad-bg)}
button:disabled{opacity:.42; cursor:default}
button:disabled:hover{border-color:var(--rule-2)}

.duas{display:grid; grid-template-columns:minmax(0,1fr) 352px; gap:20px;
      align-items:start}
@media (max-width:1000px){.duas{grid-template-columns:minmax(0,1fr)}}
.lado{display:flex; flex-direction:column; gap:20px}
.bloco h3{font-family:var(--sans); font-size:11px; letter-spacing:.11em;
          text-transform:uppercase; color:var(--mute); margin:0 0 10px;
          font-weight:600}

.caminhos{display:flex; flex-direction:column; gap:5px; max-height:300px;
          overflow-y:auto; margin:0 -6px; padding:2px 6px}
.cam{text-align:left; padding:9px 11px; border-radius:8px; line-height:1.35;
     border:1px solid var(--rule); background:var(--card); width:100%}
.cam:hover{border-color:var(--accent); background:var(--sunk)}
.cam[aria-pressed="true"]{background:var(--accent-bg); border-color:var(--accent)}
.cam .t{font-size:13.5px; color:var(--ink); display:block}
.cam .d{font-size:11.5px; color:var(--mute); font-family:var(--mono);
        display:block; margin-top:3px}
.cam .n{float:right; font-family:var(--mono); font-size:11.5px;
        color:var(--accent); margin-left:8px}
.cam.perfeito{border-color:var(--ok)}
.cam.perfeito .t{font-weight:600; color:var(--ok)}
.cam.perfeito .n{color:var(--ok)}

.pergunta{font-size:15px; line-height:1.5; white-space:pre-line}
.vazio{color:var(--mute); font-size:14px; font-style:italic}
.passo-c{font-family:var(--mono); font-size:11.5px; color:var(--accent);
         letter-spacing:.05em; margin-bottom:8px}
.aviso{font-size:13.5px; color:var(--bad); margin-top:10px; line-height:1.45}
.aviso.ok{color:var(--ok)} .aviso.warn{color:var(--warn)}

.legenda{display:flex; flex-wrap:wrap; gap:6px 15px; margin-top:12px;
         font-size:12.5px; color:var(--mute)}
.legenda span{display:flex; align-items:center; gap:6px}
.sw{width:13px; height:13px; border-radius:3px; flex:none}

table{border-collapse:collapse; width:100%; font-size:13px}
td{padding:4px 8px 4px 0; border-bottom:1px solid var(--rule); vertical-align:top}
tr:last-child td{border-bottom:none}
td.k{font-family:var(--mono); color:var(--mute); white-space:nowrap; width:1%}
.cifra{font-family:var(--mono); font-variant-numeric:tabular-nums}

.n-box{stroke-width:1.5; transition:fill .18s, stroke .18s, stroke-width .18s}
.n-id{font-family:var(--mono); font-size:11px; font-weight:500}
.n-t{font-family:var(--sans); font-size:10.5px}
.kc-box{cursor:pointer}
.kc-box:hover .kc-r{stroke:var(--accent); stroke-width:2.2}
/* --mute e não --rule-2: no tom das réguas as arestas sumiam contra o
   cartão, e a estrutura é justamente o assunto da página. */
.e{fill:none; stroke:var(--mute); stroke-width:1.5; opacity:.5;
   transition:stroke .18s, stroke-width .18s, opacity .18s}
.e.viva{stroke:var(--accent); stroke-width:2.4; opacity:1}
.e.fora{stroke-dasharray:5 4}
.rodape{font-family:var(--mono); font-size:10px; fill:var(--mute)}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
</style>

<div class="wrap">
  <p class="eyebrow">Structura · domínio c_pointers · __HASH__</p>
  <h1>O mapa das premissas</h1>
  <p class="sub">
    Os 12 componentes de conhecimento, os <b id="t-nos"></b> nós que os compõem,
    e as <b id="t-cam"></b> caminhadas possíveis por eles — o caminho perfeito de
    cada KC, e um caminho de refutação para cada crença catalogada.
    Clique num KC do mapa para abri-lo.
  </p>

  <!-- ======================= nível 1: o mapa ======================= -->
  <div class="cartao">
    <div class="barra"><h2>Os 12 KCs, na ordem em que podem ser cursados</h2></div>
    <div class="rolar"><svg id="svg-mapa" role="img"
      aria-label="Os doze componentes de conhecimento, da esquerda para a direita por profundidade de prerequisito."></svg></div>
    <div class="legenda">
      <span><i class="sw" style="background:var(--accent-bg); border:1.5px solid var(--accent)"></i>no piloto</span>
      <span><i class="sw" style="background:var(--card); border:1.5px solid var(--rule-2)"></i>fora do piloto</span>
      <span>as setas leem-se “é prerequisito de”</span>
      <span><b>n +m</b> = nós próprios, mais os que o KC puxa de fora ao ser percorrido</span>
    </div>
  </div>

  <!-- ======================= nível 2: um grafo ======================= -->
  <div class="duas">
    <div class="cartao" style="margin:0">
      <div class="barra"><h2 id="g-titulo"></h2></div>
      <p class="sub" id="g-concl" style="margin:0 0 14px; font-size:13.5px"></p>
      <div class="rolar"><svg id="svg-grafo" role="img"></svg></div>
      <div class="legenda" id="g-legenda"></div>
    </div>

    <div class="lado">
      <div class="cartao bloco" style="margin:0">
        <h3>Modo de leitura</h3>
        <div class="barra">
          <button id="m-todos" aria-pressed="true">Todos os caminhos</button>
          <button id="m-um" aria-pressed="false">Um caminho</button>
        </div>
        <div id="caminhos" class="caminhos"></div>
      </div>

      <div class="cartao bloco" style="margin:0">
        <h3>Na tela do aluno</h3>
        <div id="passo-c" class="passo-c"></div>
        <div id="pergunta" class="pergunta"></div>
        <div id="aviso" class="aviso"></div>
        <div class="barra" style="margin:14px 0 0">
          <button id="b-ok">Confirma</button>
          <button class="err" id="b-err">Erra</button>
          <button id="b-reset">Recomeçar</button>
        </div>
        <p style="font-size:12px; color:var(--mute); margin:11px 0 0; line-height:1.45">
          1º erro num nó reformula com o suporte por extenso. 2º volta um passo,
          sem descartar o que já foi confirmado. 3º encerra o KC como “em
          progresso”. A versão que vale é <code>engine.socratic.on_wrong</code>.
        </p>
      </div>

      <div class="cartao bloco" style="margin:0">
        <h3>Este KC</h3>
        <table id="tab-kc"></table>
      </div>
    </div>
  </div>
</div>

<script>
var D = __DADOS__;
var S = { kc:"kc_07", modo:"todos", caminho:null,
          cursor:0, attempts:{}, estado:{}, fim:null, msg:null, msgTipo:"" };

function $(id){ return document.getElementById(id); }
var NS = "http://www.w3.org/2000/svg";
function el(n, a, t){
  var e = document.createElementNS(NS, n);
  for (var k in a) if (a[k] !== null && a[k] !== undefined) e.setAttribute(k, a[k]);
  if (t !== undefined) e.textContent = t;
  return e;
}
function esc(t){
  return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
function G(){ return D.grafos[S.kc]; }
function noPor(id){
  var ns = G().nos;
  for (var i = 0; i < ns.length; i++) if (ns[i].id === id) return ns[i];
  return null;
}
function defsSetas(s){
  var defs = el("defs");
  [["st","var(--mute)"],["st-v","var(--accent)"],["st-k","var(--rule-2)"]]
    .forEach(function(p){
      var m = el("marker", {id:p[0], markerWidth:8, markerHeight:8,
                            refX:7, refY:3.5, orient:"auto"});
      m.appendChild(el("path", {d:"M0,0 L8,3.5 L0,7 z", fill:p[1]}));
      defs.appendChild(m);
    });
  s.appendChild(defs);
}
function duasLinhas(t, cols){
  if (t.length <= cols) return [t, ""];
  var corte = t.slice(0, cols).replace(/\s+\S*$/, "");
  return [corte, t.slice(corte.length).trim()];
}

/* ======================= nível 1: o mapa ======================= */
function desenhaMapa(){
  var m = D.mapa, s = $("svg-mapa");
  s.innerHTML = "";
  s.setAttribute("viewBox", "0 0 " + m.W + " " + m.H);
  s.setAttribute("width", m.W);
  defsSetas(s);

  var pos = {};
  m.kcs.forEach(function(k){ pos[k.id] = k; });

  m.arestas.forEach(function(a){
    var p = pos[a.de], q = pos[a.para];
    if (!p || !q) return;
    var x1 = p.x + 150, y1 = p.y + 31, x2 = q.x, y2 = q.y + 31;
    s.appendChild(el("path", {"class":"e",
      d:"M" + x1 + "," + y1 + " C" + (x1 + 26) + "," + y1 + " "
        + (x2 - 26) + "," + y2 + " " + x2 + "," + y2,
      "marker-end":"url(#st-k)"}));
  });

  m.kcs.forEach(function(k){
    var sel = k.id === S.kc;
    var g = el("g", {"class":"kc-box", tabindex:"0", role:"button"});
    g.appendChild(el("rect", {"class":"kc-r", x:k.x, y:k.y, width:150, height:62,
      rx:8, fill: k.piloto ? "var(--accent-bg)" : "var(--card)",
      stroke: sel || k.piloto ? "var(--accent)" : "var(--rule-2)",
      "stroke-width": sel ? 2.8 : 1.5}));
    g.appendChild(el("text", {x:k.x + 10, y:k.y + 19, "class":"n-id",
      fill: k.piloto ? "var(--accent)" : "var(--mute)"}, k.id.replace("kc_","KC ")));
    g.appendChild(el("text", {x:k.x + 140, y:k.y + 19, "class":"n-id",
      "text-anchor":"end", fill:"var(--mute)"},
      k.proprios + (k.fora ? " +" + k.fora : "")));
    var ln = duasLinhas(k.nome, 21);
    g.appendChild(el("text", {x:k.x + 10, y:k.y + 37, "class":"n-t",
      fill:"var(--ink)"}, ln[0]));
    g.appendChild(el("text", {x:k.x + 10, y:k.y + 48, "class":"n-t",
      fill:"var(--ink)"}, ln[1]));
    g.appendChild(el("text", {x:k.x + 140, y:k.y + 54, "class":"n-t",
      "text-anchor":"end", fill:"var(--mute)"}, k.crencas + " crenças"));
    var t = el("title");
    t.textContent = k.nome + " — " + k.proprios + " nós próprios, " + k.fecho
                  + " no fecho, " + k.crencas + " crenças";
    g.appendChild(t);
    g.onclick = function(){ abre(k.id); };
    g.onkeydown = function(e){
      if (e.key === "Enter" || e.key === " "){ e.preventDefault(); abre(k.id); }
    };
    s.appendChild(g);
  });

  s.appendChild(el("text", {x:22, y:m.H - 8, "class":"rodape"},
    "da esquerda para a direita: cada KC só pode ser cursado depois dos que o sustentam"));
}

/* ======================= nível 2: um grafo ======================= */
function abre(id){
  S.kc = id; S.modo = "todos"; S.caminho = null;
  zera(); desenhaMapa(); montaCaminhos(); tudo();
  $("g-titulo").scrollIntoView({block:"nearest", behavior:"smooth"});
}

function zera(){
  S.cursor = 0; S.attempts = {}; S.estado = {}; S.fim = null;
  S.msg = null; S.msgTipo = "";
  if (S.caminho && S.caminho.id !== "__espinha__") S.estado[S.caminho.alvo] = "wrong";
}

function montaCaminhos(){
  var g = G(), c = $("caminhos");
  c.innerHTML = "";
  g.caminhos.forEach(function(cm){
    var b = document.createElement("button");
    b.className = "cam" + (cm.id === "__espinha__" ? " perfeito" : "");
    b.setAttribute("aria-pressed", "false");
    b.innerHTML = "<span class='n'>" + cm.passos.length + " passos</span>"
                + "<span class='t'>" + esc(cm.rotulo) + "</span>"
                + "<span class='d'>" + esc(cm.detalhe) + "</span>";
    b.onclick = function(){ S.modo = "um"; S.caminho = cm; zera(); tudo(); };
    c.appendChild(b);
  });
}

function tudo(){ desenhaGrafo(); painel(); tabela(); botoes(); }

function botoes(){
  $("m-todos").setAttribute("aria-pressed", S.modo === "todos" ? "true" : "false");
  $("m-um").setAttribute("aria-pressed", S.modo === "um" ? "true" : "false");
  var g = G();
  [].forEach.call($("caminhos").querySelectorAll(".cam"), function(b, i){
    b.setAttribute("aria-pressed",
      S.modo === "um" && S.caminho && g.caminhos[i].id === S.caminho.id
        ? "true" : "false");
  });
  var andando = S.modo === "um" && !!S.caminho && !S.fim;
  $("b-ok").disabled = !andando;
  $("b-err").disabled = !andando;
  $("b-reset").disabled = S.modo !== "um" || !S.caminho;
}

function desenhaGrafo(){
  var g = G(), s = $("svg-grafo");
  s.innerHTML = "";
  s.setAttribute("viewBox", "0 0 " + g.W + " " + g.H);
  s.setAttribute("width", g.W);
  s.setAttribute("aria-label", "Grafo de premissas do " + g.id + ", " + g.nome);
  defsSetas(s);

  var passos = S.modo === "um" && S.caminho ? S.caminho.passos : null;
  var ordem = {};
  if (passos) passos.forEach(function(p, i){ ordem[p] = i + 1; });
  var atual = passos && !S.fim ? passos[S.cursor] : null;
  var feitos = {};
  if (passos) for (var i = 0; i < S.cursor; i++) feitos[passos[i]] = true;

  /* arestas primeiro, para ficarem atrás das caixas */
  g.nos.forEach(function(n){
    n.sup.forEach(function(sid){
      var a = noPor(sid);
      if (!a) return;
      var x1 = a.x + 66, y1 = a.y, x2 = n.x + 66, y2 = n.y + 50;
      var viva = !!passos && S.estado[sid] === "confirmed"
                 && (feitos[n.id] || n.id === atual);
      var apaga = !!passos && !(ordem[sid] && ordem[n.id]);
      s.appendChild(el("path", {
        "class":"e" + (viva ? " viva" : "") + (a.fora ? " fora" : ""),
        opacity: apaga ? 0.13 : null,
        d:"M" + x1 + "," + y1 + " C" + x1 + "," + (y1 - 26) + " "
          + x2 + "," + (y2 + 26) + " " + x2 + "," + y2,
        "marker-end":"url(#" + (viva ? "st-v" : "st") + ")"}));
    });
  });

  g.nos.forEach(function(n){
    var fill = "var(--card)", stroke = "var(--rule-2)", w = 1.5,
        idcor = "var(--mute)", op = 1;

    if (S.modo === "todos"){
      /* espessura e tinta pela CARGA: quantos caminhos cruzam este nó. É o
         que separa a premissa que sustenta quase tudo da folha de um ramo. */
      var f = n.cruz / g.maxcruz;
      if (n.cruz > 0){
        fill = n.tipo === "base" ? "var(--base-bg)" : "var(--accent-bg)";
        stroke = n.tipo === "base" ? "var(--base)" : "var(--accent)";
        idcor = stroke; w = 1.2 + f * 2.8; op = 0.5 + f * 0.5;
      } else { op = 0.5; }
    } else {
      if (!ordem[n.id]) op = 0.22;
      if (n.tipo === "base" && ordem[n.id]){
        fill = "var(--base-bg)"; stroke = "var(--base)"; idcor = "var(--base)";
      }
      if (S.estado[n.id] === "confirmed"){
        fill = "var(--ok-bg)"; stroke = "var(--ok)"; idcor = "var(--ok)";
      }
      if (S.estado[n.id] === "wrong"){
        fill = "var(--bad-bg)"; stroke = "var(--bad)"; w = 2; idcor = "var(--bad)";
      }
      if (n.id === atual){
        fill = "var(--warn-bg)"; stroke = "var(--warn)"; w = 2.4; idcor = "var(--warn)";
      }
    }

    var grp = el("g", {opacity: op});
    grp.appendChild(el("rect", {x:n.x, y:n.y, width:132, height:50, rx:6,
      "class":"n-box", fill:fill, stroke:stroke, "stroke-width":w,
      "stroke-dasharray": n.fora ? "5 4" : null}));
    grp.appendChild(el("text", {x:n.x + 8, y:n.y + 17, "class":"n-id", fill:idcor},
      (n.fora ? n.kc.replace("kc_","") + "·" : "") + n.node));

    if (S.modo === "todos" && n.cruz > 0){
      grp.appendChild(el("text", {x:n.x + 124, y:n.y + 17, "class":"n-id",
        "text-anchor":"end", fill:idcor}, n.cruz + "×"));
    } else if (ordem[n.id]){
      grp.appendChild(el("circle", {cx:n.x + 116, cy:n.y + 13, r:10,
        fill: feitos[n.id] ? "var(--ok)"
             : (n.id === atual ? "var(--warn)" : "var(--accent)")}));
      grp.appendChild(el("text", {x:n.x + 116, y:n.y + 17, "class":"n-id",
        "text-anchor":"middle", fill:"var(--card)"}, ordem[n.id]));
    } else if (n.conclusao){
      grp.appendChild(el("text", {x:n.x + 124, y:n.y + 17, "class":"n-id",
        "text-anchor":"end", fill:"var(--accent)"}, "fim"));
    }

    n.curto.forEach(function(linha, i){
      grp.appendChild(el("text", {x:n.x + 8, y:n.y + 34 + i * 11, "class":"n-t",
        fill:"var(--ink-2)"}, linha));
    });
    var t = el("title");
    t.textContent = n.plain + (S.modo === "todos"
      ? "   [" + n.cruz + " de " + g.caminhos.length + " caminhos passam aqui]"
      : "");
    grp.appendChild(t);
    s.appendChild(grp);
  });

  s.appendChild(el("text", {x:22, y:g.H - 8, "class":"rodape"},
    "camada 0 embaixo · as setas leem-se “sustenta” · tracejado = nó de outro KC"));

  $("g-legenda").innerHTML = S.modo === "todos"
    ? "<span><i class='sw' style='background:var(--base-bg);border:1.5px solid var(--base)'></i>premissa observável</span>"
      + "<span><i class='sw' style='background:var(--accent-bg);border:1.5px solid var(--accent)'></i>inferência</span>"
      + "<span>a espessura da borda e o <b>n×</b> dizem por quantos caminhos o nó é cruzado</span>"
    : "<span><i class='sw' style='background:var(--base-bg);border:1.5px solid var(--base)'></i>ainda não visto</span>"
      + "<span><i class='sw' style='background:var(--ok-bg);border:1.5px solid var(--ok)'></i>confirmado</span>"
      + "<span><i class='sw' style='background:var(--warn-bg);border:1.5px solid var(--warn)'></i>perguntando agora</span>"
      + "<span><i class='sw' style='background:var(--bad-bg);border:1.5px solid var(--bad)'></i>a crença nega este</span>"
      + "<span>os números são a ordem da caminhada</span>";
}

/* ---------------------------------------------------------------- ações */
function confirma(){
  if (S.fim || !S.caminho) return;
  var p = S.caminho.passos;
  S.estado[p[S.cursor]] = "confirmed";
  S.cursor++; S.msg = null; S.msgTipo = "";
  if (S.cursor >= p.length){
    S.fim = "completo";
    S.msg = S.caminho.id === "__espinha__"
      ? "Cadeia completa. É este o caminho perfeito: nenhuma crença no meio."
      : "Cadeia fechada. A conclusão saiu das respostas do aluno — nada disso "
        + "lhe foi dito, e ela contradiz a crença com que ele entrou.";
    S.msgTipo = "ok";
  }
  tudo();
}

/* Mesma decisão de engine.socratic.on_wrong, reproduzida aqui porque a
   página precisa reagir ao clique. Três saídas, e só três. */
function erra(){
  if (S.fim || !S.caminho) return;
  var ref = S.caminho.passos[S.cursor];
  var n = (S.attempts[ref] || 0) + 1;
  S.attempts[ref] = n;

  if (n >= D.attempts){
    S.fim = "abandonado";
    S.msg = "3ª tentativa neste nó: o KC é encerrado como “em progresso” e a "
          + "sessão segue. O que já foi confirmado continua valendo.";
    S.msgTipo = "warn";
  } else if (n === 1){
    S.msg = "1ª tentativa: o nó é reformulado, com o suporte por extenso.";
    S.msgTipo = "";
  } else if (S.cursor === 0){
    S.msg = "2ª tentativa, mas este é o primeiro passo — não há para onde "
          + "voltar. Reformula de novo em vez de sair do traversal.";
    S.msgTipo = "";
  } else {
    S.cursor--;
    S.msg = "2ª tentativa: o traversal volta um passo. Nada do que já foi "
          + "confirmado é descartado — só o cursor anda para trás.";
    S.msgTipo = "";
  }
  tudo();
}

/* --------------------------------------------------------------- painéis */
function painel(){
  var g = G();
  $("g-titulo").textContent = g.id.replace("kc_","KC ") + " — " + g.nome;
  $("g-concl").innerHTML = "<b>conclusão:</b> " + esc(g.conclusao_texto);

  var pc = $("passo-c"), pg = $("pergunta"), av = $("aviso");
  if (S.modo !== "um" || !S.caminho){
    pc.textContent = "";
    pg.innerHTML = "<span class='vazio'>Escolha um caminho ao lado para "
                 + "percorrê-lo passo a passo.</span>";
    av.textContent = "";
    return;
  }
  var p = S.caminho.passos;
  if (S.fim === "completo"){
    pc.textContent = "Cadeia completa · " + p.length + " passos";
    pg.innerHTML = "<b>" + esc(noPor(p[p.length - 1]).plain) + "</b>";
  } else if (S.fim === "abandonado"){
    pc.textContent = "Encerrado em progresso";
    pg.innerHTML = "<span class='vazio'>O aluno não sustentou este nó em três "
                 + "tentativas. A sessão segue para o próximo KC.</span>";
  } else {
    var ref = p[S.cursor], n = noPor(ref), tent = S.attempts[ref] || 0;
    pc.textContent = "Passo " + (S.cursor + 1) + " de " + p.length + " · "
      + (n.tipo === "base" ? "premissa observável" : "decorre do que foi confirmado")
      + (tent ? " · tentativa " + (tent + 1) : "");
    pg.textContent = tent ? n.retry : n.pergunta;
  }
  av.textContent = S.msg || "";
  av.className = "aviso " + S.msgTipo;
}

function tabela(){
  var g = G();
  var l = [
    ["nós próprios", "<span class='cifra'>" + g.proprios + "</span>"],
    ["fecho alcançável", "<span class='cifra'>" + g.fecho + "</span>"
      + (g.fecho > g.proprios ? " <span style='color:var(--mute)'>(+"
        + (g.fecho - g.proprios) + " de outros KCs)</span>" : "")],
    ["caminhos", "<span class='cifra'>" + g.caminhos.length + "</span>"
      + " <span style='color:var(--mute)'>(1 perfeito + "
      + (g.caminhos.length - 1) + " de refutação)</span>"]
  ];
  if (S.modo === "um" && S.caminho){
    l.push(["percorrendo", "<span style='color:"
      + (S.caminho.id === "__espinha__" ? "var(--ok)" : "var(--bad)") + "'>"
      + esc(S.caminho.rotulo) + "</span>"]);
  }
  $("tab-kc").innerHTML = l.map(function(x){
    return "<tr><td class='k'>" + x[0] + "</td><td>" + x[1] + "</td></tr>";
  }).join("");
}

$("m-todos").onclick = function(){ S.modo = "todos"; zera(); tudo(); };
$("m-um").onclick = function(){
  if (!S.caminho) S.caminho = G().caminhos[0];
  S.modo = "um"; zera(); tudo();
};
$("b-ok").onclick = confirma;
$("b-err").onclick = erra;
$("b-reset").onclick = function(){ zera(); tudo(); };

$("t-nos").textContent = D.totais.nos;
$("t-cam").textContent = D.totais.caminhos;
desenhaMapa(); montaCaminhos(); tudo();
</script>
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--path", default=None, help="diretório do domínio")
    p.add_argument("-o", "--out", default=None, help="arquivo de saída")
    args = p.parse_args(argv)

    saida = pagina(args.path)
    if args.out:
        Path(args.out).write_text(saida, encoding="utf-8")
        print("escrito em %s" % args.out)
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
