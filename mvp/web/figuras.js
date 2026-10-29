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

  /* ------------------------------------------------- kc_02: a rua */

  /* A analogia do kc_02 e OUTRA, e o desenho acompanha: a rua de casas
   * numeradas. O NUMERO NA PORTA e o endereco, o que esta DENTRO e o
   * valor, e o nome da variavel e a etiqueta de fora.
   *
   * Uma regra que o desenho respeita, e que o contrato de linguagem
   * cobra: um endereco e um VALOR como qualquer outro. Por isso 42 e
   * 0x1000 aparecem com a MESMA forma dentro da casa — o que os distingue
   * e a seta, que mostra que aquele numero e a porta de outra casa. Dar
   * forma especial ao endereco ensinaria que ponteiro e outra especie de
   * coisa, e e exatamente a crenca que o topico refuta.
   *
   * E nunca se desenha o ponteiro COMO a seta: a seta sai de dentro da
   * casa de p, que tem numero proprio na porta. "Ponteiro e a flecha" e a
   * frase que fabrica pointer_has_no_address. */
  function casa(x, y, o) {
    o = o || {};
    var g = el("g", {});
    var L = o.largura || 92, A = o.altura || 64;
    g.appendChild(el("rect", {
      x: x, y: y, width: L, height: A, rx: 8,
      "class": "fig-quarto" + (o.vazia ? " vazio" : "")
    }));
    /* o numero na porta: o endereco */
    g.appendChild(el("rect", {
      x: x + L / 2 - 30, y: y - 11, width: 60, height: 22, rx: 11,
      "class": "fig-placa"
    }));
    g.appendChild(el("text", {
      x: x + L / 2, y: y, "class": "fig-placa-txt"
    }, o.endereco || ""));
    /* o que esta guardado */
    if (o.dentro !== undefined) {
      g.appendChild(el("text", {
        x: x + L / 2, y: y + A / 2 + 3, "class": "fig-hospede-txt"
      }, o.dentro));
    }
    /* o nome da variavel, fora da casa */
    if (o.nome) {
      g.appendChild(el("text", {
        x: x + L / 2, y: y + A + 19, "class": "fig-rodape"
      }, o.nome));
    }
    return g;
  }

  function legenda(s, y, texto, classe) {
    s.appendChild(el("text", {
      x: 180, y: y, "class": "fig-legenda" + (classe ? " " + classe : "")
    }, texto));
  }

  POR_TOPICO.kc_02 = {

    /* B1 — cada lugar tem um numero que o identifica. */
    B1: function () {
      var s = svg(360, 146);
      s.appendChild(defs());
      s.appendChild(casa(14, 40, { endereco: "0x1000", dentro: "42", largura: 100 }));
      s.appendChild(casa(130, 40, { endereco: "0x1004", dentro: "7", largura: 100 }));
      s.appendChild(casa(246, 40, { endereco: "0x1008", dentro: "0", largura: 100 }));
      legenda(s, 20, "o número na porta é o LUGAR");
      legenda(s, 138, "o que está dentro é outra coisa");
      return s;
    },

    /* B2 — o ponteiro e uma casa, e tem numero proprio na porta. */
    B2: function () {
      var s = svg(360, 156);
      s.appendChild(defs());
      s.appendChild(casa(28, 40, { endereco: "0x1000", dentro: "42", nome: "x" }));
      s.appendChild(casa(224, 40, { endereco: "0x2A00", dentro: "0x1000", nome: "p" }));
      legenda(s, 22, "duas casas, dois números de porta");
      legenda(s, 146, "p guarda um número — e p também TEM um");
      return s;
    },

    /* B3 — o que esta dentro de p e o numero da porta de x. */
    B3: function () {
      var s = svg(360, 160);
      s.appendChild(defs());
      s.appendChild(casa(28, 46, { endereco: "0x1000", dentro: "42", nome: "x" }));
      s.appendChild(casa(224, 46, { endereco: "0x2A00", dentro: "0x1000", nome: "p" }));
      /* Horizontal, na altura do VALOR e pelo vao entre as casas: seta por
       * cima cruzaria as placas, e a placa e o que o desenho esta
       * ensinando a ler. */
      s.appendChild(seta(218, 78, 126, 78));
      legenda(s, 24, "o 0x1000 guardado em p é a porta de x");
      legenda(s, 152, "para ver o 42, é preciso ir até lá");
      return s;
    },

    /* I1 — mexer em p nao mexe em x: sao duas casas. */
    I1: function () {
      /* p fica EMBAIXO, e as setas sobem pelo vao entre as duas casas de
       * cima. Numa linha so elas cruzariam a casa do meio. */
      var s = svg(360, 284);
      s.appendChild(defs());
      s.appendChild(casa(46, 42, { endereco: "0x1000", dentro: "42", nome: "x", largura: 96 }));
      s.appendChild(casa(214, 42, { endereco: "0x1004", dentro: "7", nome: "y", largura: 96 }));
      s.appendChild(casa(130, 166, { endereco: "0x2A00", dentro: "0x1004", nome: "p", largura: 100 }));
      /* a de agora: sobe para y */
      s.appendChild(seta(196, 162, 250, 110));
      /* a de antes: tracejada, para x */
      s.appendChild(seta(164, 162, 110, 110, "saindo"));
      legenda(s, 22, "p apontava para x; agora aponta para y");
      legenda(s, 276, "x continua com 42 — mudou p, não mudou x");
      return s;
    },

    /* I2 — o tipo decide o tamanho do passo.
     *
     * As casas vao VAZIAS de proposito: aqui o que importa e o numero da
     * porta, nao o que mora nela. E o rotulo do tipo fica A ESQUERDA da
     * linha — embaixo da casa ele colidia com a linha de baixo. */
    I2: function () {
      var s = svg(360, 180);
      s.appendChild(defs());

      function passo(y, tipo, de, para, nota) {
        s.appendChild(el("text", {
          x: 34, y: y + 26, "class": "fig-rodape"
        }, tipo));
        s.appendChild(casa(66, y, { endereco: de, vazia: true,
                                    largura: 92, altura: 44 }));
        s.appendChild(seta(164, y + 22, 230, y + 22));
        s.appendChild(el("text", {
          x: 197, y: y + 10, "class": "fig-nota"
        }, nota));
        s.appendChild(casa(236, y, { endereco: para, vazia: true,
                                     largura: 92, altura: 44 }));
      }

      passo(50, "int *p", "0x1000", "0x1004", "p + 1");
      passo(124, "char *c", "0x1000", "0x1001", "c + 1");
      legenda(s, 24, "mesmo número guardado, passos de tamanhos diferentes");
      return s;
    },

    /* I3 — com o endereco na mao, a funcao alcanca a casa original. */
    I3: function () {
      var s = svg(360, 190);
      s.appendChild(defs());
      s.appendChild(casa(24, 56, { endereco: "0x1000", dentro: "10", nome: "n, aqui" }));
      s.appendChild(casa(224, 56, { endereco: "0x2A10", dentro: "0x1000", nome: "lá na função" }));
      s.appendChild(seta(218, 88, 122, 88));
      legenda(s, 24, "a função recebeu o NÚMERO da porta de n");
      legenda(s, 174, "e por isso escreve na mesma casa, não numa cópia");
      return s;
    }
  };

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
