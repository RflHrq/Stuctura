"""Explorador dos grafos de premissas: a organização e a travessia.

Para DEMONSTRAR o mecanismo — na qualificação, para o orientador, na banca.
Não é ferramenta de análise (não lê o banco) nem tela do participante (não
entra na sessão). É o grafo desenhado, com a caminhada por cima.

O que a página deixa fazer:

  escolher um KC          -> o grafo aparece, camada por camada
  escolher uma crença     -> o nó que ela nega acende
  percorrer               -> os passos na ordem real do `socratic.plan()`
  errar de propósito      -> a regressão controlada, tentativa a tentativa

Os textos das perguntas vêm de `socratic.question()`, os mesmos que o
participante lê. O plano vem de `socratic.plan()`. Nada aqui reimplementa
o motor — exceto a regra das três tentativas, que é reproduzida no
JavaScript porque a página precisa reagir a um clique; a versão que vale
é `engine.socratic.on_wrong`, e a página diz isso.

    python -m tools.grafo -o analise/grafos.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import socratic
from engine.loader import Domain, Ref, load

WEB = Path(__file__).resolve().parent.parent / "web"

# Geometria da caixa de nó. A largura é fixa para que camadas diferentes
# fiquem alinhadas — o desalinhamento é o que faz um grafo desenhado
# parecer rascunho.
CAIXA_W = 132
CAIXA_H = 50
GAP_X = 20
GAP_Y = 78
MARGEM = 22


def alcancaveis(d: Domain, kc_id: str) -> list[Ref]:
    """Os nós do KC mais todo nó de outro KC que o suporte alcança.

    É o *fecho* do KC, e não a lista dele: kc_09 tem 10 nós próprios e
    percorre 19. Desenhar só os próprios esconderia metade da cadeia que
    o participante de fato caminha.
    """
    vistos: list[Ref] = []
    pilha = [(kc_id, n) for n in d.kcs[kc_id].nodes]

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

    for ref in pilha:
        visitar(ref)
    return vistos


def camadas(d: Domain, refs: list[Ref]) -> dict[Ref, int]:
    """Camada de cada nó: 0 para os sem suporte, senão 1 + a maior do suporte.

    Termina porque o grafo é acíclico — propriedade que o validador
    garante. A memoização evita recalcular o suporte compartilhado, que em
    kc_09 é a maior parte do trabalho.
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


def posicionar(d: Domain, kc_id: str, refs: list[Ref],
               nivel: dict[Ref, int]) -> tuple[dict[Ref, tuple[int, int]], int, int]:
    """Coordenadas de cada caixa. Camada 0 embaixo, conclusão em cima.

    Dentro de uma camada, os nós são ordenados pelo *baricentro* dos seus
    suportes — a média das posições de quem os sustenta. Duas passagens
    bastam para desembaraçar a maioria dos cruzamentos; mais que isso não
    muda nada visível e só torna o resultado difícil de prever.
    """
    por_camada: dict[int, list[Ref]] = {}
    for r in refs:
        por_camada.setdefault(nivel[r], []).append(r)

    # Camada 0 numa ordem estável: os nós do próprio KC antes dos importados.
    por_camada[0].sort(key=lambda r: (r[0] != kc_id, r[0], r[1]))

    ordem: dict[Ref, int] = {r: i for i, r in enumerate(por_camada[0])}
    for c in sorted(por_camada)[1:]:
        for _ in range(2):
            def baricentro(r: Ref) -> float:
                sup = [s for s in d.node(*r).support if s in ordem]
                if not sup:
                    return 0.0
                return sum(ordem[s] for s in sup) / len(sup)
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

    return pos, total_w + 2 * MARGEM, total_h + 2 * MARGEM + 26


def curto(texto: str, cols: int = 24, linhas: int = 2) -> list[str]:
    """O rótulo dentro da caixa, quebrado em PALAVRAS.

    Cortar por número de caracteres parte a palavra ao meio e o rótulo
    passa a mentir sobre o enunciado. O texto inteiro vai para o painel e
    para o `title` da caixa, então aqui só cabe a etiqueta.
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


def dados(d: Domain) -> dict:
    saida: dict = {"kcs": [], "attempts": d.study.max_attempts_per_node}

    for kc_id in d.teaching_sequence():
        kc = d.kcs[kc_id]
        refs = alcancaveis(d, kc_id)
        nivel = camadas(d, refs)
        pos, W, H = posicionar(d, kc_id, refs, nivel)

        nos = []
        for r in refs:
            no = d.node(*r)
            x, y = pos[r]
            nos.append({
                "id": "%s:%s" % r,
                "kc": r[0], "node": r[1],
                "tipo": no.type,
                "fora": r[0] != kc_id,
                "conclusao": r[0] == kc_id and r[1] == kc.conclusion_node,
                "curto": curto(no.plain or no.text),
                "plain": no.plain or no.text,
                "canon": no.text,
                "pergunta": socratic.question(d, *r),
                "retry": socratic.reformulate(
                    d, socratic.steps_from(d, [r])[0]),
                "sup": ["%s:%s" % s for s in no.support if s in set(refs)],
                "x": x, "y": y,
            })

        crencas = []
        for m in d.misconceptions_of(kc_id):
            crencas.append({
                "id": m.id, "belief": m.belief, "grade": m.grade,
                "nega": "%s:%s" % (m.kc, m.node),
                "fundacional": m.is_foundational,
                "plano": ["%s:%s" % r for r in socratic.full_plan(d, m.kc, m.node)],
            })

        saida["kcs"].append({
            "id": kc_id,
            "nome": kc.name,
            "conclusao": "%s:%s" % (kc_id, kc.conclusion_node),
            "conclusao_texto": kc.conclusion,
            "proprios": len(kc.nodes),
            "fecho": len(refs),
            "W": W, "H": H,
            "nos": nos,
            "crencas": crencas,
            "espinha": ["%s:%s" % r
                        for r in socratic.full_plan(d, kc_id, kc.conclusion_node)],
        })
    return saida


def pagina(path: str | None = None) -> str:
    d = load(path)
    return TEMPLATE.replace("__DADOS__", json.dumps(dados(d), ensure_ascii=False)) \
                   .replace("__HASH__", d.hash.replace("sha256:", "")[:8])


TEMPLATE = r"""<title>Os Grafos de Premissas</title>
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
     font-size:16px; line-height:1.55; margin:0; padding:26px 20px 70px}
.wrap{max-width:1180px; margin:0 auto}
h1{font-family:var(--serif); font-size:30px; line-height:1.15; margin:0 0 6px;
   font-weight:600; letter-spacing:-.01em}
.sub{color:var(--mute); font-size:14.5px; margin:0 0 24px; max-width:70ch}
.eyebrow{font-family:var(--mono); font-size:11px; letter-spacing:.13em;
         text-transform:uppercase; color:var(--mute); margin:0 0 8px}
code{font-family:var(--mono); font-size:.88em; background:var(--sunk);
     padding:1px 5px; border-radius:4px; border:1px solid var(--rule)}

/* ------------------------------------------------------------- controles */
.barra{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px; align-items:center}
.rot{font-family:var(--mono); font-size:11px; letter-spacing:.1em;
     text-transform:uppercase; color:var(--mute); margin-right:2px}
button{font:inherit; font-size:13.5px; cursor:pointer; border-radius:7px;
       border:1px solid var(--rule-2); background:var(--card); color:var(--ink);
       padding:6px 12px; transition:background .12s, border-color .12s}
button:hover{border-color:var(--accent)}
button:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
button[aria-pressed="true"]{background:var(--accent); border-color:var(--accent);
       color:var(--card); font-weight:500}
button.kc{font-family:var(--mono); font-size:12.5px; padding:5px 9px}
button.acao{font-weight:500}
button.acao.err{border-color:var(--bad); color:var(--bad)}
button.acao.err:hover{background:var(--bad-bg)}
button:disabled{opacity:.42; cursor:default}
button:disabled:hover{border-color:var(--rule-2)}
select{font:inherit; font-size:13.5px; padding:6px 10px; border-radius:7px;
       border:1px solid var(--rule-2); background:var(--card); color:var(--ink);
       max-width:100%}

/* ------------------------------------------------------------- disposição */
.painel{display:grid; grid-template-columns:minmax(0,1fr) 336px; gap:18px;
        align-items:start}
@media (max-width:940px){.painel{grid-template-columns:minmax(0,1fr)}}

.tela{background:var(--card); border:1px solid var(--rule); border-radius:11px;
      box-shadow:var(--shadow); padding:16px; overflow-x:auto}
/* sem max-width: o grafo do kc_09 tem 1392px de largura, e encolhê-lo
   para caber deixaria os rótulos ilegíveis. Ele rola dentro de .tela, e
   o corpo da página nunca rola de lado. */
.tela svg{display:block; height:auto}

.lado{display:flex; flex-direction:column; gap:14px; position:sticky; top:18px}
@media (max-width:940px){.lado{position:static}}
.bloco{background:var(--card); border:1px solid var(--rule); border-radius:11px;
       padding:15px 17px; box-shadow:var(--shadow)}
.bloco h2{font-family:var(--sans); font-size:11px; letter-spacing:.11em;
          text-transform:uppercase; color:var(--mute); margin:0 0 10px; font-weight:600}
.bloco p{margin:0 0 9px; font-size:14.5px}
.bloco p:last-child{margin-bottom:0}

.pergunta{font-size:15px; line-height:1.5; white-space:pre-line; color:var(--ink)}
.pergunta .lista{color:var(--ink-2)}
.vazio{color:var(--mute); font-size:14px; font-style:italic}
.passo-c{font-family:var(--mono); font-size:11.5px; color:var(--accent);
         letter-spacing:.06em; margin-bottom:8px}
.aviso{font-size:13.5px; color:var(--bad); margin-top:10px; line-height:1.45}
.aviso.ok{color:var(--ok)}
.aviso.warn{color:var(--warn)}

.legenda{display:flex; flex-wrap:wrap; gap:6px 16px; margin-top:12px;
         font-size:12.5px; color:var(--mute)}
.legenda span{display:flex; align-items:center; gap:6px}
.sw{width:13px; height:13px; border-radius:3px; flex:none}

table{border-collapse:collapse; width:100%; font-size:13px}
td{padding:4px 8px 4px 0; border-bottom:1px solid var(--rule); vertical-align:top}
tr:last-child td{border-bottom:none}
td.k{font-family:var(--mono); color:var(--mute); white-space:nowrap; width:1%}
.cifra{font-family:var(--mono); font-variant-numeric:tabular-nums}

/* --------------------------------------------------------------- desenho */
.n-box{stroke-width:1.5; transition:fill .2s, stroke .2s, stroke-width .2s}
.n-id{font-family:var(--mono); font-size:11px; font-weight:500}
.n-t{font-family:var(--sans); font-size:10.5px}
/* --mute e não --rule-2: a estrutura é o assunto da página, e no tom das
   réguas as arestas desapareciam contra o fundo do cartão. */
.e{fill:none; stroke:var(--mute); stroke-width:1.5; opacity:.62;
   transition:stroke .2s, stroke-width .2s, opacity .2s}
.e.viva{opacity:1}
.e.viva{stroke:var(--accent); stroke-width:2.2}
.e.fora{stroke-dasharray:5 4}
.cam{font-family:var(--mono); font-size:10px; fill:var(--mute)}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
</style>

<div class="wrap">
  <p class="eyebrow">Structura · domínio c_pointers · __HASH__</p>
  <h1>Os grafos de premissas</h1>
  <p class="sub">
    Como cada componente de conhecimento está organizado, e como a travessia
    caminha por ele. Escolha um KC, escolha uma crença, e percorra — errando
    de propósito, se quiser ver a regressão controlada.
  </p>

  <div class="barra" id="barra-kc"><span class="rot">KC</span></div>
  <div class="barra">
    <span class="rot">Percurso</span>
    <select id="sel-crenca"></select>
  </div>

  <div class="painel">
    <div class="tela"><svg id="svg" role="img" aria-label="Grafo de premissas do KC selecionado"></svg>
      <div class="legenda">
        <span><i class="sw" style="background:var(--card); border:1.5px solid var(--rule-2)"></i>ainda não visto</span>
        <span><i class="sw" style="background:var(--base-bg); border:1.5px solid var(--base)"></i>premissa observável</span>
        <span><i class="sw" style="background:var(--ok-bg); border:1.5px solid var(--ok)"></i>confirmado pelo aluno</span>
        <span><i class="sw" style="background:var(--bad-bg); border:1.5px solid var(--bad)"></i>a crença nega este</span>
        <span><i class="sw" style="background:var(--warn-bg); border:1.5px solid var(--warn)"></i>tentando agora</span>
      </div>
    </div>

    <div class="lado">
      <div class="bloco">
        <h2>Na tela do aluno</h2>
        <div id="passo-c" class="passo-c"></div>
        <div id="pergunta" class="pergunta"></div>
        <div id="aviso" class="aviso"></div>
        <div class="barra" style="margin:14px 0 0">
          <button class="acao" id="b-ok" disabled>Confirma</button>
          <button class="acao err" id="b-err" disabled>Erra</button>
          <button id="b-reset">Recomeçar</button>
        </div>
      </div>

      <div class="bloco">
        <h2>Este KC</h2>
        <table id="tab-kc"></table>
      </div>

      <div class="bloco">
        <h2>A regra da regressão</h2>
        <p style="font-size:13.5px; color:var(--ink-2); margin:0">
          1ª vez que erra um nó, ele é reformulado com o suporte por extenso.
          2ª vez, o traversal <strong>volta um passo</strong> — sem descartar nada
          do que já foi confirmado. 3ª vez, o KC é encerrado como “em progresso”
          e a sessão segue.
        </p>
        <p style="font-size:12.5px; color:var(--mute); margin:9px 0 0">
          A versão que vale é <code>engine.socratic.on_wrong</code>; esta página
          a reproduz para poder reagir ao clique.
        </p>
      </div>
    </div>
  </div>
</div>

<script>
var D = __DADOS__;

var S = { kc:null, crenca:null, plano:[], cursor:0, attempts:{}, estado:{},
          fim:null, msg:null, msgTipo:"" };

var $ = function(id){ return document.getElementById(id); };
var NS = "http://www.w3.org/2000/svg";
function el(n, a, t){
  var e = document.createElementNS(NS, n);
  for (var k in a) if (a[k] !== null && a[k] !== undefined) e.setAttribute(k, a[k]);
  if (t !== undefined) e.textContent = t;
  return e;
}
function kcAtual(){ return D.kcs.filter(function(k){ return k.id === S.kc; })[0]; }
function noPor(id){ return kcAtual().nos.filter(function(n){ return n.id === id; })[0]; }

/* ------------------------------------------------------------- controles */
function montaKCs(){
  var b = $("barra-kc");
  D.kcs.forEach(function(k){
    var t = document.createElement("button");
    t.className = "kc"; t.textContent = k.id.replace("kc_", "KC ");
    t.title = k.nome;
    t.onclick = function(){ escolheKC(k.id); };
    b.appendChild(t);
  });
}

function escolheKC(id){
  S.kc = id;
  [].forEach.call($("barra-kc").querySelectorAll("button"), function(b, i){
    b.setAttribute("aria-pressed", D.kcs[i].id === id ? "true" : "false");
  });
  var k = kcAtual(), sel = $("sel-crenca");
  sel.innerHTML = "";
  var o = document.createElement("option");
  o.value = ""; o.textContent = "Construir até a conclusão (sem crença detectada)";
  sel.appendChild(o);
  k.crencas.forEach(function(c){
    var x = document.createElement("option");
    x.value = c.id;
    x.textContent = c.belief + "  [nega " + c.nega.split(":")[1] + "]";
    sel.appendChild(x);
  });
  sel.onchange = function(){ escolhePercurso(sel.value); };
  escolhePercurso(k.crencas.length ? k.crencas[0].id : "");
}

function escolhePercurso(id){
  var k = kcAtual();
  S.crenca = k.crencas.filter(function(c){ return c.id === id; })[0] || null;
  $("sel-crenca").value = id || "";
  reset();
}

function reset(){
  var k = kcAtual();
  S.plano = S.crenca ? S.crenca.plano.slice() : k.espinha.slice();
  S.cursor = 0; S.attempts = {}; S.estado = {}; S.fim = null;
  S.msg = null; S.msgTipo = "";
  if (S.crenca) S.estado[S.crenca.nega] = "wrong";
  desenha(); painel(); tabela();
}

/* ---------------------------------------------------------------- ações */
function confirma(){
  if (S.fim) return;
  var ref = S.plano[S.cursor];
  S.estado[ref] = "confirmed";
  S.cursor++;
  S.msg = null; S.msgTipo = "";
  if (S.cursor >= S.plano.length){
    S.fim = "completo";
    S.msg = "Cadeia fechada. A conclusão saiu das respostas do aluno — "
          + "nada disso lhe foi dito.";
    S.msgTipo = "ok";
  }
  desenha(); painel();
}

/* Mesma decisão de engine.socratic.on_wrong, reproduzida aqui porque a
   página precisa reagir ao clique. Três saídas, e só três. */
function erra(){
  if (S.fim) return;
  var ref = S.plano[S.cursor];
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
  desenha(); painel();
}

/* --------------------------------------------------------------- desenho */
function desenha(){
  var k = kcAtual(), s = $("svg");
  s.innerHTML = "";
  s.setAttribute("viewBox", "0 0 " + k.W + " " + k.H);
  s.setAttribute("width", k.W);
  s.setAttribute("aria-label", "Grafo de premissas do " + k.id + ", " + k.nome);

  var defs = el("defs");
  [["seta","var(--mute)"],["seta-v","var(--accent)"]].forEach(function(p){
    var m = el("marker", {id:p[0], markerWidth:8, markerHeight:8,
                          refX:7, refY:3.5, orient:"auto"});
    m.appendChild(el("path", {d:"M0,0 L8,3.5 L0,7 z", fill:p[1]}));
    defs.appendChild(m);
  });
  s.appendChild(defs);

  var atual = S.fim ? null : S.plano[S.cursor];
  var feitos = {};
  for (var i = 0; i < S.cursor; i++) feitos[S.plano[i]] = true;

  /* arestas primeiro, para ficarem atrás das caixas */
  k.nos.forEach(function(n){
    n.sup.forEach(function(sid){
      var a = noPor(sid);
      if (!a) return;
      var x1 = a.x + 132/2, y1 = a.y;
      var x2 = n.x + 132/2, y2 = n.y + 50;
      var viva = S.estado[sid] === "confirmed" &&
                 (feitos[n.id] || n.id === atual);
      var cl = "e" + (viva ? " viva" : "") + (a.fora ? " fora" : "");
      s.appendChild(el("path", {
        "class": cl,
        d: "M" + x1 + "," + y1 + " C" + x1 + "," + (y1 - 26) + " "
           + x2 + "," + (y2 + 26) + " " + x2 + "," + y2,
        "marker-end": "url(#" + (viva ? "seta-v" : "seta") + ")"
      }));
    });
  });

  k.nos.forEach(function(n){
    var est = S.estado[n.id];
    var fill = "var(--card)", stroke = "var(--rule-2)", w = 1.5, idcor = "var(--mute)";

    if (n.tipo === "base" && !est){ fill = "var(--base-bg)"; stroke = "var(--base)"; idcor = "var(--base)"; }
    if (est === "confirmed"){ fill = "var(--ok-bg)"; stroke = "var(--ok)"; idcor = "var(--ok)"; }
    if (est === "wrong"){ fill = "var(--bad-bg)"; stroke = "var(--bad)"; w = 2; idcor = "var(--bad)"; }
    if (n.id === atual){ fill = "var(--warn-bg)"; stroke = "var(--warn)"; w = 2.4; idcor = "var(--warn)"; }

    var g = el("g");
    g.appendChild(el("rect", {x:n.x, y:n.y, width:132, height:50, rx:6,
      "class":"n-box", fill:fill, stroke:stroke, "stroke-width":w,
      "stroke-dasharray": n.fora ? "5 4" : null}));
    g.appendChild(el("text", {x:n.x + 8, y:n.y + 17, "class":"n-id", fill:idcor},
      (n.fora ? n.kc.replace("kc_","") + "·" : "") + n.node));
    if (n.conclusao){
      g.appendChild(el("text", {x:n.x + 124, y:n.y + 17, "class":"n-id",
        "text-anchor":"end", fill:"var(--accent)"}, "conclusão"));
    }
    n.curto.forEach(function(linha, i){
      g.appendChild(el("text", {x:n.x + 8, y:n.y + 34 + i * 11, "class":"n-t",
        fill:"var(--ink-2)"}, linha));
    });
    var t = el("title"); t.textContent = n.plain; g.appendChild(t);
    s.appendChild(g);
  });

  s.appendChild(el("text", {x:22, y:k.H - 8, "class":"cam"},
    "camada 0 embaixo · as setas leem-se “sustenta” · tracejado = nó de outro KC"));
}

/* --------------------------------------------------------------- painéis */
function painel(){
  var k = kcAtual();
  var pc = $("passo-c"), pg = $("pergunta"), av = $("aviso");

  if (S.fim === "completo"){
    pc.textContent = "Cadeia completa · " + S.plano.length + " passos";
    pg.innerHTML = "<b>" + esc(noPor(S.plano[S.plano.length-1]).plain) + "</b>";
  } else if (S.fim === "abandonado"){
    pc.textContent = "Encerrado em progresso";
    pg.innerHTML = "<span class='vazio'>O aluno não sustentou este nó em três "
                 + "tentativas. A sessão segue para o próximo KC.</span>";
  } else {
    var ref = S.plano[S.cursor];
    var n = noPor(ref), tent = S.attempts[ref] || 0;
    pc.textContent = "Passo " + (S.cursor + 1) + " de " + S.plano.length
                   + " · " + (n.tipo === "base" ? "premissa observável"
                                                : "decorre do que foi confirmado")
                   + (tent ? " · tentativa " + (tent + 1) : "");
    pg.textContent = tent ? n.retry : n.pergunta;
  }

  av.textContent = S.msg || "";
  av.className = "aviso " + S.msgTipo;
  $("b-ok").disabled = !!S.fim;
  $("b-err").disabled = !!S.fim;
}

function tabela(){
  var k = kcAtual();
  var linhas = [
    ["nome", k.nome],
    ["nós próprios", "<span class='cifra'>" + k.proprios + "</span>"],
    ["fecho alcançável", "<span class='cifra'>" + k.fecho + "</span>"
      + (k.fecho > k.proprios
         ? " <span style='color:var(--mute)'>(+" + (k.fecho - k.proprios)
           + " de outros KCs)</span>" : "")],
    ["crenças", "<span class='cifra'>" + k.crencas.length + "</span>"],
    ["conclusão", "<code>" + k.conclusao.split(":")[1] + "</code> — "
      + esc(k.conclusao_texto)]
  ];
  if (S.crenca){
    linhas.push(["crença", "<span style='color:var(--bad)'>"
      + esc(S.crenca.belief) + "</span>"]);
    linhas.push(["proveniência", "grau " + S.crenca.grade
      + (S.crenca.fundacional
         ? " · <span style='color:var(--bad)'>fundacional: nega um nó-base, "
           + "então exige confronto visual</span>" : "")]);
  }
  $("tab-kc").innerHTML = linhas.map(function(l){
    return "<tr><td class='k'>" + l[0] + "</td><td>" + l[1] + "</td></tr>";
  }).join("");
}

function esc(t){
  return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

$("b-ok").onclick = confirma;
$("b-err").onclick = erra;
$("b-reset").onclick = reset;
montaKCs();
escolheKC("kc_07");
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
