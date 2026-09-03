/* Renderizador do bloco `visual` das CIUs (§10).
 *
 * SVG inline, sem biblioteca: os diagramas são caixas, setas e rótulos.
 *
 * REGRAS DE APRESENTAÇÃO (§10.1), aplicadas aqui e não deixadas ao autor
 * da CIU:
 *   - o aluno controla a alternância; nunca animação automática. O evento
 *     `diagram_toggled` só significa alguma coisa se a ação for dele.
 *   - o nome técnico não aparece em rótulo nenhum antes da conclusão.
 *   - no máximo duas frases de texto junto ao diagrama.
 *
 * ------------------------------------------------------------------------
 * SOBRE O QUE O SCHEMA ATUAL PERMITE DESENHAR
 *
 * Os blocos `visual` do domínio descrevem o diagrama em PROSA:
 *
 *     visual:
 *       kind: memory_diagram
 *       regions: [stack, heap]
 *       states: [antes_do_free, depois_do_free]
 *       show: ["p na stack com seta", "bloco no heap"]
 *
 * Disso dá para desenhar regiões nomeadas com as frases dentro — e é o que
 * o modo `prosa` faz. NÃO dá para desenhar o par antes/depois, porque não
 * há conteúdo por estado: os dois estados desenhariam a mesma figura.
 *
 * Por isso a alternância só é oferecida quando existe conteúdo por estado.
 * Um botão que não muda nada produziria eventos `diagram_toggled` sem
 * significado, e esse evento é justamente o que transforma o apelo visual
 * em dado (§5.2).
 *
 * O modo `estruturado` abaixo já está implementado e espera esta forma:
 *
 *     visual:
 *       kind: memory_diagram
 *       states:
 *         antes_do_free:
 *           stack: [{name: p, value: "0x7ffd21a0"}]
 *           heap:  [{name: bloco, value: "int 42", note: "bloco valido"}]
 *           arrow: {from: p, to: bloco}
 *         depois_do_free:
 *           stack: [{name: p, value: "0x7ffd21a0"}]
 *           heap:  [{name: bloco, value: liberado, note: "nao mais valido",
 *                    invalid: true}]
 *           arrow: {from: p, to: bloco, invalid: true}
 *       caption: "..."
 */

(function (global) {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  function el(nome, attrs, texto) {
    var n = document.createElementNS(NS, nome);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) {
      n.setAttribute(k, attrs[k]);
    }
    if (texto !== undefined) n.textContent = texto;
    return n;
  }

  function div(cls, texto) {
    var d = document.createElement("div");
    if (cls) d.className = cls;
    if (texto !== undefined) d.textContent = texto;
    return d;
  }

  /* Quais estados têm conteúdo próprio? Só nesse caso há o que comparar. */
  function estadosComConteudo(spec) {
    var s = spec && spec.states;
    if (!s || Array.isArray(s)) return [];       // lista de nomes: prosa
    return Object.keys(s);
  }

  /* ------------------------------------------------------------ estruturado */

  function desenhaEstado(spec, nomeEstado) {
    var dados = spec.states[nomeEstado] || {};
    var regioes = (spec.regions || Object.keys(dados).filter(function (k) {
      return k !== "arrow";
    }));

    var W = 640, H = 240, pad = 14;
    var larguraRegiao = (W - pad * (regioes.length + 1)) / regioes.length;
    var svg = el("svg", {
      viewBox: "0 0 " + W + " " + H, class: "mem",
      role: "img", "aria-label": "Diagrama de memória, estado " + nomeEstado
    });

    var caixas = {};   // nome da célula -> {x, y, w, h}

    regioes.forEach(function (regiao, i) {
      var x = pad + i * (larguraRegiao + pad);
      svg.appendChild(el("rect", {
        x: x, y: 26, width: larguraRegiao, height: H - 40, rx: 6,
        fill: "var(--sunk)", stroke: "var(--rule-2)"
      }));
      svg.appendChild(el("text", {
        x: x + larguraRegiao / 2, y: 18, "text-anchor": "middle",
        "font-size": 12, "font-family": "ui-monospace, monospace",
        fill: "var(--mute)"
      }, regiao));

      (dados[regiao] || []).forEach(function (celula, j) {
        var cy = 48 + j * 62;
        var invalida = !!celula.invalid;
        var cx = x + 16, cw = larguraRegiao - 32;
        svg.appendChild(el("rect", {
          x: cx, y: cy, width: cw, height: 46, rx: 4,
          fill: invalida ? "var(--bad-bg)" : "var(--card)",
          stroke: invalida ? "var(--bad)" : "var(--rule-2)",
          "stroke-width": 1.5,
          "stroke-dasharray": invalida ? "4 3" : null
        }));
        svg.appendChild(el("text", {
          x: cx + cw / 2, y: cy + 19, "text-anchor": "middle",
          "font-size": 13, "font-weight": 600,
          "font-family": "ui-monospace, monospace",
          fill: invalida ? "var(--bad)" : "var(--ink)"
        }, celula.name || ""));
        if (celula.value !== undefined) {
          svg.appendChild(el("text", {
            x: cx + cw / 2, y: cy + 34, "text-anchor": "middle",
            "font-size": 11, "font-family": "ui-monospace, monospace",
            fill: "var(--mute)"
          }, String(celula.value)));
        }
        if (celula.note) {
          svg.appendChild(el("text", {
            x: cx + cw / 2, y: cy + 58, "text-anchor": "middle",
            "font-size": 10.5, fill: "var(--mute)"
          }, celula.note));
        }
        caixas[celula.name] = { x: cx, y: cy, w: cw, h: 46 };
      });
    });

    var seta = dados.arrow;
    if (seta && caixas[seta.from] && caixas[seta.to]) {
      var a = caixas[seta.from], b = caixas[seta.to];
      var cor = seta.invalid ? "var(--bad)" : "var(--accent)";
      var mid = "m" + nomeEstado;
      var defs = el("defs");
      var marker = el("marker", {
        id: mid, markerWidth: 8, markerHeight: 8, refX: 7, refY: 3.5,
        orient: "auto"
      });
      marker.appendChild(el("path", { d: "M0,0 L8,3.5 L0,7 z", fill: cor }));
      defs.appendChild(marker);
      svg.appendChild(defs);
      svg.appendChild(el("line", {
        x1: a.x + a.w, y1: a.y + a.h / 2, x2: b.x - 6, y2: b.y + b.h / 2,
        stroke: cor, "stroke-width": 1.8,
        "stroke-dasharray": seta.invalid ? "4 3" : null,
        "marker-end": "url(#" + mid + ")"
      }));
    }
    return svg;
  }

  /* ------------------------------------------------------------------ prosa */

  function desenhaProsa(spec) {
    var regioes = spec.regions || [];
    var frases = [].concat(spec.show || []);

    if (!regioes.length) {
      var caixa = div("banner");
      frases.forEach(function (f) { caixa.appendChild(div(null, f)); });
      return caixa;
    }

    /* Cada frase vai para a região que ela nomeia; o resto fica embaixo. */
    var porRegiao = {}, soltas = [];
    regioes.forEach(function (r) { porRegiao[r] = []; });
    frases.forEach(function (f) {
      var achou = regioes.filter(function (r) {
        return f.toLowerCase().indexOf(r.toLowerCase()) >= 0;
      });
      if (achou.length) porRegiao[achou[0]].push(f); else soltas.push(f);
    });

    var W = 640, pad = 14;
    var alturaMax = Math.max.apply(null, regioes.map(function (r) {
      return porRegiao[r].length;
    }).concat([1]));
    var H = 46 + alturaMax * 34;
    var larguraRegiao = (W - pad * (regioes.length + 1)) / regioes.length;
    var svg = el("svg", {
      viewBox: "0 0 " + W + " " + H, class: "mem", role: "img",
      "aria-label": "Diagrama: " + regioes.join(" e ")
    });

    regioes.forEach(function (regiao, i) {
      var x = pad + i * (larguraRegiao + pad);
      svg.appendChild(el("rect", {
        x: x, y: 26, width: larguraRegiao, height: H - 36, rx: 6,
        fill: "var(--sunk)", stroke: "var(--rule-2)"
      }));
      svg.appendChild(el("text", {
        x: x + larguraRegiao / 2, y: 18, "text-anchor": "middle",
        "font-size": 12, "font-family": "ui-monospace, monospace",
        fill: "var(--mute)"
      }, regiao));
      porRegiao[regiao].forEach(function (frase, j) {
        svg.appendChild(el("text", {
          x: x + larguraRegiao / 2, y: 52 + j * 34, "text-anchor": "middle",
          "font-size": 13, fill: "var(--ink)"
        }, frase));
      });
    });

    var caixa2 = document.createElement("div");
    caixa2.appendChild(svg);
    soltas.forEach(function (f) { caixa2.appendChild(div("diagram-caption", f)); });
    return caixa2;
  }

  /* ------------------------------------------------- declaração anotada */

  function desenhaDeclaracao(spec) {
    var caixa = document.createElement("div");
    [].concat(spec.show || []).forEach(function (linha) {
      var p = document.createElement("pre");
      p.className = "code";
      p.style.marginBottom = "8px";
      p.textContent = linha;
      caixa.appendChild(p);
    });
    return caixa;
  }

  /* ------------------------------------------------------------- público */

  /**
   * Monta o diagrama.
   * @param spec     o bloco `visual` da CIU
   * @param onToggle (de, para) -> void, chamado quando o ALUNO alterna
   * @returns HTMLElement pronto para inserir
   */
  function render(spec, onToggle) {
    var raiz = div("diagram-card card");
    if (!spec) { raiz.appendChild(div("diagram-caption", "(sem diagrama)")); return raiz; }

    if (spec.kind === "annotated_declaration") {
      raiz.appendChild(desenhaDeclaracao(spec));
      if (spec.caption) raiz.appendChild(div("diagram-caption", spec.caption));
      return raiz;
    }

    var estados = estadosComConteudo(spec);

    if (estados.length < 2) {
      /* Sem conteúdo por estado não há comparação a fazer. Não se oferece
       * alternância: um botão que não muda nada geraria `diagram_toggled`
       * sem significado, e é esse evento que sustenta o argumento visual. */
      raiz.appendChild(desenhaProsa(spec));
      if (spec.caption) raiz.appendChild(div("diagram-caption", spec.caption));
      return raiz;
    }

    var barra = div("diagram-toggle");
    var palco = document.createElement("div");
    var atual = estados[0];

    function mostra(novo) {
      var anterior = atual;
      atual = novo;
      palco.innerHTML = "";
      palco.appendChild(desenhaEstado(spec, novo));
      Array.prototype.forEach.call(barra.children, function (b) {
        b.setAttribute("aria-pressed", String(b.dataset.estado === novo));
      });
      if (anterior !== novo && typeof onToggle === "function") {
        onToggle(anterior, novo);
      }
    }

    estados.forEach(function (nome) {
      var b = document.createElement("button");
      b.className = "state-btn";
      b.dataset.estado = nome;
      b.textContent = nome.replace(/_/g, " ");
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () { mostra(nome); };
      barra.appendChild(b);
    });

    raiz.appendChild(barra);
    raiz.appendChild(palco);
    if (spec.caption) raiz.appendChild(div("diagram-caption", spec.caption));
    mostra(atual);
    return raiz;
  }

  global.Diagram = { render: render, estadosComConteudo: estadosComConteudo };
})(window);
