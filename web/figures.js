/* Ilustrações: as da introdução e as das premissas do traversal.
 *
 * Todas em SVG inline e sem biblioteca. O tipo é vocabulário de
 * APRESENTAÇÃO; o conteúdo — rótulos, valores, legendas — vem do YAML
 * (intro.yaml, ou o bloco `figure` do nó em premise_graphs.yaml). Trocar
 * o domínio troca as figuras sem tocar aqui: nenhuma frase sobre C mora
 * neste arquivo, e é isso que o §1 pede.
 *
 *   session_map    o percurso da sessão, em quatro etapas
 *   street         memória como posições numeradas
 *   boxes          variáveis como caixas com nome, valor e endereço
 *   pointer_pair   duas caixas, uma guardando o endereço da outra
 *   regions        duas áreas com regras de arrumação diferentes
 *   confidence     a escala, e o que cada nível significa
 *   array_row      caixas GRUDADAS, com índice — a analogia do array
 *   array_decay    a fileira mais o nome trocado pelo endereço da 1ª caixa
 *   sizes          duas barras de larguras diferentes, para comparar medida
 *   call_frame     o que atravessa a fronteira de uma chamada de função
 *   two_cases      dois painéis: o caso que vale e o que não vale
 *
 * Por que SVG e não imagem: as cores vêm dos tokens do tema, então a
 * ilustração acompanha claro e escuro; e o texto é texto — selecionável,
 * legível por leitor de tela, e nítido em qualquer zoom.
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

  function svg(w, h, rotulo) {
    return el("svg", {
      viewBox: "0 0 " + w + " " + h, class: "fig",
      role: "img", "aria-label": rotulo || ""
    });
  }

  var MONO = "ui-monospace, 'Cascadia Mono', Menlo, Consolas, monospace";
  var SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";

  /* Caixa com nome em cima, valor dentro e endereço embaixo. É a unidade
   * visual que se repete em três das cinco figuras — desenhada uma vez
   * para que uma variável tenha sempre a mesma aparência. */
  function caixa(g, x, y, w, h, dados) {
    var destaque = dados.tone === "pointer";
    g.appendChild(el("rect", {
      x: x, y: y, width: w, height: h, rx: 5,
      fill: destaque ? "var(--accent-soft)" : "var(--card)",
      stroke: destaque ? "var(--accent)" : "var(--rule-2)", "stroke-width": 1.6
    }));
    if (dados.name) {
      g.appendChild(el("text", {
        x: x + w / 2, y: y - 9, "text-anchor": "middle",
        "font-family": MONO, "font-size": 13, "font-weight": 600,
        fill: destaque ? "var(--accent)" : "var(--ink)"
      }, dados.name));
    }
    g.appendChild(el("text", {
      x: x + w / 2, y: y + h / 2 + 5, "text-anchor": "middle",
      "font-family": MONO, "font-size": 14, fill: "var(--ink)"
    }, dados.value !== undefined ? String(dados.value) : ""));
    if (dados.addr) {
      g.appendChild(el("text", {
        x: x + w / 2, y: y + h + 15, "text-anchor": "middle",
        "font-family": MONO, "font-size": 10.5, fill: "var(--mute)"
      }, dados.addr));
    }
    return { x: x, y: y, w: w, h: h };
  }

  function seta(g, x1, y1, x2, y2, id, cor) {
    var defs = el("defs");
    var mk = el("marker", {
      id: id, markerWidth: 8, markerHeight: 8, refX: 7, refY: 3.5, orient: "auto"
    });
    mk.appendChild(el("path", { d: "M0,0 L8,3.5 L0,7 z", fill: cor }));
    defs.appendChild(mk);
    g.appendChild(defs);
    g.appendChild(el("line", {
      x1: x1, y1: y1, x2: x2, y2: y2, stroke: cor,
      "stroke-width": 1.8, "marker-end": "url(#" + id + ")"
    }));
  }

  /* ------------------------------------------------------ session_map */

  function sessionMap(f) {
    var passos = f.steps || [];
    var W = 640, H = 62 + passos.length * 56;
    var s = svg(W, H, "O percurso da sessão");
    passos.forEach(function (p, i) {
      var y = 26 + i * 56;
      s.appendChild(el("circle", {
        cx: 26, cy: y + 14, r: 13,
        fill: "var(--accent-soft)", stroke: "var(--accent)", "stroke-width": 1.4
      }));
      s.appendChild(el("text", {
        x: 26, y: y + 19, "text-anchor": "middle", "font-family": MONO,
        "font-size": 12, "font-weight": 600, fill: "var(--accent)"
      }, String(i + 1)));
      if (i < passos.length - 1) {
        s.appendChild(el("line", {
          x1: 26, y1: y + 29, x2: 26, y2: y + 54,
          stroke: "var(--rule-2)", "stroke-width": 1.4, "stroke-dasharray": "3 3"
        }));
      }
      s.appendChild(el("text", {
        x: 52, y: y + 12, "font-family": SANS, "font-size": 14.5,
        "font-weight": 600, fill: "var(--ink)"
      }, p.label || ""));
      s.appendChild(el("text", {
        x: 52, y: y + 30, "font-family": SANS, "font-size": 12.5,
        fill: "var(--mute)"
      }, p.note || ""));
    });
    return s;
  }

  /* ----------------------------------------------------------- street */

  function street(f) {
    var casas = f.houses || [];
    var W = 640, H = 168;
    var s = svg(W, H, "Posições de memória numeradas");
    // 112 e não 128: o rótulo "endereço" fica à esquerda da fileira, e com
    // casas mais largas ele saía do viewBox — texto cortado, silenciosamente.
    var larg = 112, gap = 14;
    var x0 = (W - (casas.length * larg + (casas.length - 1) * gap)) / 2;

    casas.forEach(function (c, i) {
      var x = x0 + i * (larg + gap);
      var alvo = !!c.highlight;
      /* telhado: a analogia é uma rua de casas, e a silhueta é o que faz
       * a figura ser lida como rua e não como tabela */
      s.appendChild(el("path", {
        d: "M" + x + ",62 L" + (x + larg / 2) + ",34 L" + (x + larg) + ",62 Z",
        fill: alvo ? "var(--accent-soft)" : "var(--sunk)",
        stroke: alvo ? "var(--accent)" : "var(--rule-2)", "stroke-width": 1.4
      }));
      s.appendChild(el("rect", {
        x: x, y: 62, width: larg, height: 52, rx: 3,
        fill: alvo ? "var(--accent-soft)" : "var(--card)",
        stroke: alvo ? "var(--accent)" : "var(--rule-2)",
        "stroke-width": alvo ? 1.8 : 1.3
      }));
      s.appendChild(el("text", {
        x: x + larg / 2, y: 94, "text-anchor": "middle", "font-family": MONO,
        "font-size": 16, "font-weight": alvo ? 600 : 400,
        fill: alvo ? "var(--accent)" : "var(--ink-2)"
      }, c.content !== undefined ? String(c.content) : ""));
      s.appendChild(el("text", {
        x: x + larg / 2, y: 132, "text-anchor": "middle", "font-family": MONO,
        "font-size": 11.5, fill: "var(--mute)"
      }, c.addr || ""));
    });

    if (f.pin && casas[f.pin.at]) {
      var px = x0 + f.pin.at * (larg + gap) + larg / 2;
      s.appendChild(el("text", {
        x: px, y: 156, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12.5, fill: "var(--accent)"
      }, f.pin.label || ""));
    }
    s.appendChild(el("text", {
      x: x0 - 4, y: 132, "text-anchor": "end", "font-family": SANS,
      "font-size": 11, fill: "var(--mute)"
    }, "endereço"));
    return s;
  }

  /* ------------------------------------------------------------ boxes */

  function boxes(f) {
    var itens = f.items || [];
    var W = 640, H = 150;
    var s = svg(W, H, "Variáveis como caixas");
    var larg = 132, gap = 40;
    var x0 = (W - (itens.length * larg + (itens.length - 1) * gap)) / 2;
    itens.forEach(function (it, i) {
      caixa(s, x0 + i * (larg + gap), 46, larg, 56, it);
    });
    /* Os dois rótulos de eixo só com MAIS DE UMA caixa: com uma só,
     * centrada, o "nome" caía exatamente em cima do nome dela. */
    if (itens.length > 1) {
      s.appendChild(el("text", {
        x: W / 2, y: 26, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12, fill: "var(--mute)"
      }, "nome"));
      s.appendChild(el("text", {
        x: W / 2, y: 138, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12, fill: "var(--mute)"
      }, "endereço — onde a caixa está"));
    }
    return s;
  }

  /* ---------------------------------------------------- pointer_pair */

  function pointerPair(f) {
    var W = 640, H = 176;
    var s = svg(W, H, "Um ponteiro guarda o endereço de outra variável");
    var p = f.pointer || {}, t = f.target || {};

    var a = caixa(s, 78, 58, 148, 58, {
      name: p.name, value: p.value, addr: p.addr, tone: "pointer"
    });
    var b = caixa(s, 410, 58, 148, 58, {
      name: t.name, value: t.value, addr: t.addr
    });
    seta(s, a.x + a.w + 6, a.y + a.h / 2, b.x - 8, b.y + b.h / 2,
         "pp", "var(--accent)");

    s.appendChild(el("text", {
      x: (a.x + a.w + b.x) / 2, y: a.y + a.h / 2 - 12, "text-anchor": "middle",
      "font-family": SANS, "font-size": 12.5, fill: "var(--accent)"
    }, "o conteúdo de p é o endereço de x"));

    s.appendChild(el("text", {
      x: a.x + a.w / 2, y: 150, "text-anchor": "middle",
      "font-family": SANS, "font-size": 12, fill: "var(--mute)"
    }, "uma caixa"));
    s.appendChild(el("text", {
      x: b.x + b.w / 2, y: 150, "text-anchor": "middle",
      "font-family": SANS, "font-size": 12, fill: "var(--mute)"
    }, "outra caixa"));
    return s;
  }

  /* ---------------------------------------------------------- regions */

  function regions(f) {
    var W = 640, H = 196;
    var s = svg(W, H, "Duas regiões de memória com regras diferentes");
    var lados = [
      { d: f.left || {}, x: 24, cor: "var(--base)", fundo: "var(--base-soft)" },
      { d: f.right || {}, x: 336, cor: "var(--warn)", fundo: "var(--warn-soft)" }
    ];
    lados.forEach(function (L, i) {
      s.appendChild(el("rect", {
        x: L.x, y: 22, width: 280, height: 132, rx: 7,
        fill: L.fundo, stroke: L.cor, "stroke-width": 1.5
      }));
      s.appendChild(el("text", {
        x: L.x + 140, y: 52, "text-anchor": "middle", "font-family": SANS,
        "font-size": 16, "font-weight": 600, fill: L.cor
      }, L.d.title || ""));
      s.appendChild(el("text", {
        x: L.x + 140, y: 76, "text-anchor": "middle", "font-family": SANS,
        "font-size": 13, fill: "var(--ink-2)"
      }, L.d.note || ""));

      /* três caixinhas ilustram "o que fica guardado"; no lado da esquerda
       * elas se apagam, no da direita permanecem */
      for (var k = 0; k < 3; k++) {
        s.appendChild(el("rect", {
          x: L.x + 62 + k * 56, y: 98, width: 44, height: 32, rx: 3,
          fill: "var(--card)", stroke: L.cor, "stroke-width": 1.2,
          "stroke-dasharray": i === 0 ? "4 3" : null,
          opacity: i === 0 ? 0.55 : 1
        }));
      }
      /* o rodapé vem do YAML: era texto sobre C escrito dentro do
       * renderizador, e o §1 não permite que o motor saiba de C */
      s.appendChild(el("text", {
        x: L.x + 140, y: 146, "text-anchor": "middle", "font-family": SANS,
        "font-size": 11.5, fill: "var(--mute)"
      }, L.d.foot || ""));
    });
    return s;
  }

  /* ------------------------------------------------------- confidence */

  function confidence(f) {
    var niveis = f.levels || [];
    var W = 640, H = 44 + niveis.length * 54;
    var s = svg(W, H, "A escala de confiança");
    var tons = { cool: "var(--base)", mid: "var(--mute)", hot: "var(--accent)" };
    niveis.forEach(function (n, i) {
      var y = 20 + i * 54;
      var cor = tons[n.tone] || "var(--mute)";
      s.appendChild(el("rect", {
        x: 20, y: y, width: 190, height: 38, rx: 19,
        fill: "var(--card)", stroke: cor, "stroke-width": 1.6
      }));
      s.appendChild(el("text", {
        x: 115, y: y + 24, "text-anchor": "middle", "font-family": SANS,
        "font-size": 14.5, "font-weight": 600, fill: cor
      }, n.label || ""));
      s.appendChild(el("text", {
        x: 232, y: y + 24, "font-family": SANS, "font-size": 14,
        fill: "var(--ink-2)"
      }, n.meaning || ""));
    });
    return s;
  }


  /* -------------------------------------------------------- array_row */

  /* Caixas GRUDADAS, nao separadas: a contiguidade e a coisa que a figura
   * precisa dizer, e um espaco entre elas diria o contrario. */
  function arrayRow(f) {
    var cels = f.cells || [];
    var W = 640, H = f.name ? 158 : 132;
    var s = svg(W, H, f.alt || "");
    var larg = Math.min(88, Math.floor(520 / Math.max(cels.length, 1)));
    var alt = 52, y = f.name ? 62 : 40;
    var x0 = (W - cels.length * larg) / 2;

    cels.forEach(function (c, i) {
      var alvo = f.highlight === i;
      s.appendChild(el("rect", {
        x: x0 + i * larg, y: y, width: larg, height: alt,
        fill: alvo ? "var(--accent-soft)" : "var(--card)",
        stroke: alvo ? "var(--accent)" : "var(--rule-2)",
        "stroke-width": alvo ? 1.8 : 1.3
      }));
      s.appendChild(el("text", {
        x: x0 + i * larg + larg / 2, y: y + alt / 2 + 5, "text-anchor": "middle",
        "font-family": MONO, "font-size": 14,
        fill: alvo ? "var(--accent)" : "var(--ink)"
      }, c.value !== undefined ? String(c.value) : ""));
      if (c.label) {
        s.appendChild(el("text", {
          x: x0 + i * larg + larg / 2, y: y + alt + 17, "text-anchor": "middle",
          "font-family": MONO, "font-size": 11, fill: "var(--mute)"
        }, c.label));
      }
    });

    if (f.name) {
      /* colchete por cima de TODAS as caixas: o nome vale para o conjunto,
       * e e exatamente esse o ponto que a premissa afirma */
      var x1 = x0, x2 = x0 + cels.length * larg;
      s.appendChild(el("path", {
        d: "M" + x1 + ",46 L" + x1 + ",38 L" + x2 + ",38 L" + x2 + ",46",
        fill: "none", stroke: "var(--accent)", "stroke-width": 1.6
      }));
      s.appendChild(el("text", {
        x: (x1 + x2) / 2, y: 28, "text-anchor": "middle", "font-family": MONO,
        "font-size": 14, "font-weight": 600, fill: "var(--accent)"
      }, f.name));
    }
    if (f.note) {
      s.appendChild(el("text", {
        x: W / 2, y: H - 8, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12.5, fill: "var(--mute)"
      }, f.note));
    }
    return s;
  }

  /* ------------------------------------------------------ array_decay */

  /* A fileira, e ao lado o nome sendo trocado pelo endereco da primeira
   * caixa. E a figura de uma SUBSTITUICAO, nao de uma igualdade. */
  function arrayDecay(f) {
    var cels = f.cells || [];
    var W = 640, H = 186;
    var s = svg(W, H, f.alt || "");
    var larg = 62, alt = 46, y = 96;
    var x0 = W - cels.length * larg - 40;

    cels.forEach(function (c, i) {
      s.appendChild(el("rect", {
        x: x0 + i * larg, y: y, width: larg, height: alt,
        fill: i === 0 ? "var(--accent-soft)" : "var(--card)",
        stroke: i === 0 ? "var(--accent)" : "var(--rule-2)",
        "stroke-width": i === 0 ? 1.8 : 1.3
      }));
      s.appendChild(el("text", {
        x: x0 + i * larg + larg / 2, y: y + alt / 2 + 5, "text-anchor": "middle",
        "font-family": MONO, "font-size": 13, fill: "var(--ink)"
      }, c.value !== undefined ? String(c.value) : ""));
      if (c.label) {
        s.appendChild(el("text", {
          x: x0 + i * larg + larg / 2, y: y + alt + 15, "text-anchor": "middle",
          "font-family": MONO, "font-size": 10.5, fill: "var(--mute)"
        }, c.label));
      }
    });

    var tk = caixa(s, 40, y, 120, alt,
                   { name: f.written_label, value: f.written, tone: "pointer" });
    seta(s, tk.x + tk.w + 6, y + alt / 2, x0 - 8, y + alt / 2,
         "decay", "var(--accent)");
    s.appendChild(el("text", {
      x: (tk.x + tk.w + x0) / 2, y: y + alt / 2 - 12, "text-anchor": "middle",
      "font-family": SANS, "font-size": 12, fill: "var(--accent)"
    }, f.arrow_label || ""));
    if (f.note) {
      s.appendChild(el("text", {
        x: W / 2, y: 176, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12.5, fill: "var(--mute)"
      }, f.note));
    }
    return s;
  }

  /* ------------------------------------------------------------ sizes */

  /* Barras de largura proporcional. Comparar MEDIDA e a unica coisa que
   * esta figura faz - por isso a escala e literal, nao decorativa. */
  function sizes(f) {
    var bars = f.bars || [];
    var W = 640, H = 40 + bars.length * 62;
    var s = svg(W, H, f.alt || "");
    var max = bars.reduce(function (m, b) { return Math.max(m, +b.units || 1); }, 1);
    bars.forEach(function (b, i) {
      var y = 24 + i * 62;
      /* 260 e não 380: a nota vai à DIREITA da barra, e com a barra mais
       * larga ela saía do viewBox — texto cortado, sem aviso nenhum. */
      var w = Math.max(28, Math.round((+b.units || 1) / max * 260));
      s.appendChild(el("text", {
        x: 20, y: y + 22, "font-family": MONO, "font-size": 13.5,
        fill: "var(--ink)"
      }, b.label || ""));
      s.appendChild(el("rect", {
        x: 184, y: y, width: w, height: 34, rx: 4,
        fill: i === 0 ? "var(--accent-soft)" : "var(--sunk)",
        stroke: i === 0 ? "var(--accent)" : "var(--rule-2)", "stroke-width": 1.5
      }));
      s.appendChild(el("text", {
        x: 184 + w + 12, y: y + 22, "font-family": SANS, "font-size": 13,
        fill: "var(--mute)"
      }, b.note || ""));
    });
    return s;
  }

  /* ------------------------------------------------------- call_frame */

  /* A fronteira de uma chamada. O que atravessa esta escrito na seta; o
   * que fica para tras esta do lado de fora. */
  function callFrame(f) {
    var W = 640, H = 196;
    var s = svg(W, H, f.alt || "");
    var lados = [
      { d: f.caller || {}, x: 24 },
      { d: f.callee || {}, x: 348 }
    ];
    lados.forEach(function (L, i) {
      s.appendChild(el("rect", {
        x: L.x, y: 30, width: 268, height: 124, rx: 7,
        fill: "var(--card)", stroke: "var(--rule-2)", "stroke-width": 1.4,
        "stroke-dasharray": i === 1 ? "5 4" : null
      }));
      s.appendChild(el("text", {
        x: L.x + 134, y: 22, "text-anchor": "middle", "font-family": MONO,
        "font-size": 13, "font-weight": 600, fill: "var(--ink-2)"
      }, L.d.title || ""));
      s.appendChild(el("text", {
        x: L.x + 134, y: 62, "text-anchor": "middle", "font-family": SANS,
        "font-size": 13.5, fill: "var(--ink)"
      }, L.d.has || ""));
      s.appendChild(el("text", {
        x: L.x + 134, y: 88, "text-anchor": "middle", "font-family": MONO,
        "font-size": 13, fill: "var(--accent)"
      }, L.d.value || ""));
      s.appendChild(el("text", {
        x: L.x + 134, y: 126, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12, fill: "var(--mute)"
      }, L.d.lost || ""));
    });
    seta(s, 296, 92, 342, 92, "cf", "var(--accent)");
    s.appendChild(el("text", {
      x: 319, y: 78, "text-anchor": "middle", "font-family": SANS,
      "font-size": 11.5, fill: "var(--accent)"
    }, f.crosses || ""));
    if (f.note) {
      s.appendChild(el("text", {
        x: W / 2, y: 180, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12.5, fill: "var(--mute)"
      }, f.note));
    }
    return s;
  }

  /* -------------------------------------------------------- two_cases */

  /* Dois painéis: o que se escreve, e o que resulta. Serve quando a
   * premissa e uma DISTINCAO — o caso que vale e o caso que nao vale —
   * e nao ha nada de espacial para desenhar. */
  function twoCases(f) {
    var W = 640, H = 166;
    var s = svg(W, H, f.alt || "");
    var lados = [
      { d: f.left || {}, x: 24, cor: "var(--base)", fundo: "var(--base-soft)" },
      { d: f.right || {}, x: 336, cor: "var(--accent)", fundo: "var(--accent-soft)" }
    ];
    lados.forEach(function (L) {
      s.appendChild(el("rect", {
        x: L.x, y: 22, width: 280, height: 108, rx: 7,
        fill: L.fundo, stroke: L.cor, "stroke-width": 1.5
      }));
      s.appendChild(el("text", {
        x: L.x + 140, y: 46, "text-anchor": "middle", "font-family": SANS,
        "font-size": 14.5, "font-weight": 600, fill: L.cor
      }, L.d.title || ""));
      s.appendChild(el("rect", {
        x: L.x + 16, y: 58, width: 248, height: 30, rx: 4,
        fill: "var(--card)", stroke: "var(--rule-2)", "stroke-width": 1.1
      }));
      s.appendChild(el("text", {
        x: L.x + 140, y: 78, "text-anchor": "middle", "font-family": MONO,
        "font-size": 13.5, fill: "var(--ink)"
      }, L.d.code || ""));
      s.appendChild(el("text", {
        x: L.x + 140, y: 110, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12.5, fill: "var(--ink-2)"
      }, L.d.result || ""));
    });
    if (f.note) {
      s.appendChild(el("text", {
        x: W / 2, y: 152, "text-anchor": "middle", "font-family": SANS,
        "font-size": 12.5, fill: "var(--mute)"
      }, f.note));
    }
    return s;
  }

  var TIPOS = {
    session_map: sessionMap,
    street: street,
    boxes: boxes,
    pointer_pair: pointerPair,
    regions: regions,
    confidence: confidence,
    array_row: arrayRow,
    array_decay: arrayDecay,
    sizes: sizes,
    call_frame: callFrame,
    two_cases: twoCases
  };

  /**
   * Monta uma figura a partir do seu bloco `figure` no YAML.
   * @param f o bloco `figure` (do cartão da introdução ou do nó)
   * @param cls classe CSS do <figure>; "intro-fig" se omitida
   * @returns HTMLElement, ou null se o tipo não for conhecido
   */
  function render(f, cls) {
    if (!f || !TIPOS[f.kind]) return null;
    var caixa = document.createElement("figure");
    caixa.className = cls || "intro-fig";
    var desenho = TIPOS[f.kind](f);
    /* `alt` do YAML tem precedência sobre o rótulo genérico do tipo: quem
     * escreve a figura sabe o que ELA mostra; o tipo só sabe o formato.
     * Sem isto, um leitor de tela anunciava "Variáveis como caixas" em
     * toda figura desse tipo, qualquer que fosse o conteúdo. */
    if (f.alt) desenho.setAttribute("aria-label", f.alt);
    caixa.appendChild(desenho);
    if (f.caption) {
      var cap = document.createElement("figcaption");
      cap.textContent = f.caption;
      caixa.appendChild(cap);
    }
    return caixa;
  }

  global.Fig = { render: render, tipos: Object.keys(TIPOS) };
})(window);
