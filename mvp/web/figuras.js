/* Ilustrações da analogia, uma por premissa.
 *
 * A analogia é a mesma do começo ao fim — quarto de hotel reservado —, e o
 * desenho segue a mesma regra: o QUARTO é a variável, o HÓSPEDE é o valor,
 * a PLACA é o nome, e a categoria do quarto é o tipo. Trocar de metáfora a
 * cada nó obrigaria a pessoa a aprender a metáfora junto com o conceito.
 *
 * Sem dependência externa (RNF05 do sistema antigo, e bom senso aqui): SVG
 * montado no DOM, cores vindas das variáveis do tema, então o desenho
 * acompanha claro e escuro sem segunda folha de estilo.
 */
(function (global) {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  function el(nome, attrs, texto) {
    var n = document.createElementNS(NS, nome);
    Object.keys(attrs || {}).forEach(function (k) {
      if (attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]);
    });
    if (texto !== undefined) n.textContent = texto;
    return n;
  }

  function svg(largura, altura) {
    var s = el("svg", {
      viewBox: "0 0 " + largura + " " + altura,
      "class": "fig", role: "img"
    });
    return s;
  }

  /* Um quarto: a caixa, a placa com o número, e o que estiver dentro. */
  function quarto(x, y, opcoes) {
    var o = opcoes || {};
    var g = el("g", {});
    var L = o.largura || 108, A = o.altura || 76;
    g.appendChild(el("rect", {
      x: x, y: y, width: L, height: A, rx: 8,
      "class": "fig-quarto" + (o.vazio ? " vazio" : "") + (o.sujo ? " sujo" : "")
    }));
    // a placa do número fica na porta, como num hotel
    g.appendChild(el("rect", {
      x: x + L / 2 - 26, y: y - 11, width: 52, height: 22, rx: 11,
      "class": "fig-placa"
    }));
    g.appendChild(el("text", {
      x: x + L / 2, y: y, "class": "fig-placa-txt"
    }, o.placa || ""));

    if (o.hospede) {
      g.appendChild(el("circle", {
        cx: x + L / 2, cy: y + A / 2 + 2, r: 19, "class": "fig-hospede"
      }));
      g.appendChild(el("text", {
        x: x + L / 2, y: y + A / 2 + 2, "class": "fig-hospede-txt"
      }, o.hospede));
    } else if (o.sujo) {
      // lençol bagunçado do hóspede anterior: o lixo que C não limpa
      g.appendChild(el("path", {
        "class": "fig-sujeira",
        d: "M" + (x + 22) + "," + (y + A - 26) +
           " q 14,-14 28,0 q 14,14 28,0 q 14,-14 24,4"
      }));
      g.appendChild(el("text", {
        x: x + L / 2, y: y + 26, "class": "fig-nota"
      }, o.textoDentro || "?"));
    } else if (o.vazio) {
      g.appendChild(el("text", {
        x: x + L / 2, y: y + A / 2 + 2, "class": "fig-nota"
      }, o.textoDentro || "vazio"));
    }

    if (o.rodape) {
      g.appendChild(el("text", {
        x: x + L / 2, y: y + A + 20, "class": "fig-rodape"
      }, o.rodape));
    }
    return g;
  }

  function seta(x1, y1, x2, y2, classe) {
    return el("path", {
      "class": "fig-seta" + (classe ? " " + classe : ""),
      d: "M" + x1 + "," + y1 + " L" + x2 + "," + y2,
      "marker-end": "url(#fig-ponta)"
    });
  }

  function defs() {
    var d = el("defs", {});
    var m = el("marker", {
      id: "fig-ponta", viewBox: "0 0 10 10", refX: 9, refY: 5,
      markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse"
    });
    m.appendChild(el("path", { d: "M0,0 L10,5 L0,10 z", "class": "fig-ponta" }));
    d.appendChild(m);
    return d;
  }

  /* ------------------------------------------------------------ as cinco */

  /* POR TOPICO, e nao so pelo id do no.
   *
   * Os ids se repetem entre topicos — todo topico tem um B1 —, e enquanto
   * havia um topico so isso nao aparecia. Com o kc_02 no ar, a tela que
   * ensina "a memoria e uma rua de lugares numerados" desenhava os quartos
   * de hotel do kc_00. Figura do topico errado confunde mais que figura
   * nenhuma: ela ensina uma analogia que o texto nao usa.
   *
   * Topico sem desenho fica SEM desenho, e isso e visivel de proposito. */
  var POR_TOPICO = {};

  POR_TOPICO.kc_00 = {

    /* B1 — a variável é um espaço com NOME e TIPO: dois quartos de
     * categorias diferentes, cada um com sua placa. */
    B1: function () {
      var s = svg(360, 132);
      s.appendChild(defs());
      s.appendChild(quarto(30, 26, { placa: "idade", vazio: true,
                                     textoDentro: "int", rodape: "cabe um inteiro" }));
      s.appendChild(quarto(196, 42, { placa: "letra", vazio: true, altura: 44,
                                      textoDentro: "char",
                                      rodape: "cabe um caractere" }));
      return s;
    },

    /* B2 — declarar JÁ reserva: o quarto existe antes do hóspede. */
    B2: function () {
      var s = svg(360, 152);
      s.appendChild(defs());
      s.appendChild(quarto(126, 30, { placa: "x", vazio: true,
                                      textoDentro: "reservado",
                                      rodape: "o quarto já existe" }));
      s.appendChild(el("text", { x: 180, y: 142, "class": "fig-legenda" },
                       "falta só o hóspede (o valor)"));
      return s;
    },

    /* B3 — ninguém limpa sozinho: o quarto vem com a bagunça anterior. */
    B3: function () {
      var s = svg(360, 152);
      s.appendChild(defs());
      s.appendChild(quarto(126, 30, { placa: "x", sujo: true,
                                      textoDentro: "lixo",
                                      rodape: "C não manda limpeza" }));
      s.appendChild(el("text", { x: 180, y: 142, "class": "fig-legenda" },
                       "int x = 0; é você arrumando o quarto"));
      return s;
    },

    /* B4 — o hóspede novo SUBSTITUI: nunca dois no mesmo quarto. */
    B4: function () {
      var s = svg(360, 132);
      s.appendChild(defs());
      s.appendChild(quarto(126, 30, { placa: "x", hospede: "20",
                                      rodape: "um hóspede por vez" }));
      s.appendChild(el("text", { x: 60, y: 60, "class": "fig-saindo" }, "10"));
      s.appendChild(seta(76, 64, 118, 64, "saindo"));
      s.appendChild(el("text", { x: 60, y: 84, "class": "fig-legenda" }, "sai"));
      return s;
    },

    /* I1 — a atribuição tem direção: hóspede vai para o quarto, não o
     * contrário. */
    I1: function () {
      var s = svg(360, 150);
      s.appendChild(defs());
      s.appendChild(quarto(196, 22, { placa: "x", hospede: "7" }));
      s.appendChild(el("circle", { cx: 70, cy: 60, r: 19, "class": "fig-hospede" }));
      s.appendChild(el("text", { x: 70, y: 60, "class": "fig-hospede-txt" }, "7"));
      s.appendChild(seta(96, 60, 190, 60));
      s.appendChild(el("text", { x: 143, y: 44, "class": "fig-legenda" }, "x = 7"));

      s.appendChild(seta(190, 116, 96, 116, "proibida"));
      s.appendChild(el("text", { x: 143, y: 100, "class": "fig-legenda erro" },
                       "7 = x"));
      s.appendChild(el("text", { x: 143, y: 138, "class": "fig-legenda" },
                       "número não é lugar que recebe"));
      return s;
    }
  };

  /* O kc_02 ainda nao tem desenho proprio. Fica vazio, e a tela mostra so
   * texto e codigo ate alguem desenhar a rua das casas numeradas. */
  POR_TOPICO.kc_02 = {};

  var topicoAtual = "kc_00";

  function doNo(no) {
    var banco = POR_TOPICO[topicoAtual] || {};
    return banco[no] || null;
  }

  global.Figuras = {
    /* Quem carrega o dominio diz qual topico esta no ar. */
    topico: function (id) { if (id) topicoAtual = id; },
    /* Devolve o desenho daquela premissa, ou null quando não há. */
    desenha: function (no) {
      var f = doNo(no);
      return f ? f() : null;
    },
    /* Põe o desenho dentro de um elemento, trocando o que estiver lá. */
    dentro: function (elemento, no) {
      elemento.innerHTML = "";
      var f = doNo(no);
      var fig = f ? f() : null;
      if (fig) elemento.appendChild(fig);
      elemento.hidden = !fig;
      return !!fig;
    }
  };
})(window);
