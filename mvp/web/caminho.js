/* O caminho dos tópicos na página inicial (docs/interface.md, seção 7).

   Uma trilha de jogo, de cima para baixo: uma parada por tópico, na ordem
   sugerida que o portal manda em /topicos, e no fim o caminho se abre em
   três. A ordem é sugestão — toda parada é um link, e nenhum tópico fica
   trancado.

   O estado de cada parada sai do que o navegador lembra (progresso.js):
     feito       a pessoa chegou ao fechamento do tópico, neste navegador;
     andamento   começou e não terminou ("3 de 6");
     aberto      o resto.
   E o PRÓXIMO SUGERIDO é o primeiro da ordem ainda não feito — pode estar
   em andamento, e aí o cartão diz "Continuar".

   O desenho é SVG feito aqui, sem biblioteca, com as cores do tema por
   classe (portal.html). A cor nunca é a única informação: a parada feita
   tem o sinal de certo, e cada link diz o estado em texto para leitor de
   tela. A pulsação do próximo só anda com movimento permitido.

   Também carrega no Node, para os testes (mvp/test_caminho.py). */
(function (global) {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var LARGURA = 330, ALTURA = 420;

  /* As posições do esboço aprovado (docs/esbocos/4-interface.html): dez
   * paradas no tronco, o ponto onde o caminho se abre, e três no fim. */
  var TRONCO = [[70, 36], [170, 52], [262, 82], [205, 130], [105, 152],
                [58, 200], [150, 232], [250, 250], [270, 298], [172, 320]];
  var GALHO = [172, 346];
  var FIM = [[80, 378], [172, 390], [264, 378]];
  /* Onde fica o rótulo de cada parada do tronco, em relação a ela, como no
   * esboço: [dx, dy, âncora]. Cada um escolhido para não cair no chão nem
   * na parada vizinha. */
  var ROTULO = [[22, -12, "start"], [-20, 28, "start"], [-26, 30, "start"],
                [17, 28, "start"], [19, 24, "start"], [24, 4, "start"],
                [20, 4, "start"], [-54, 24, "start"], [20, 22, "end"],
                [22, 4, "start"]];

  function posicoes(nTronco, nFim) {
    if (nTronco === TRONCO.length && nFim === FIM.length) {
      return { tronco: TRONCO.slice(), galho: GALHO.slice(), fim: FIM.slice() };
    }
    /* Outra quantidade de tópicos: o mesmo zigue-zague, recalculado. */
    var tronco = [];
    var passo = nTronco > 1 ? 290 / (nTronco - 1) : 0;
    for (var i = 0; i < nTronco; i++) {
      tronco.push([Math.round(165 + 105 * Math.sin(i * 1.15)),
                   Math.round(36 + i * passo)]);
    }
    var fim = [];
    for (var j = 0; j < nFim; j++) {
      fim.push([Math.round(LARGURA * (j + 1) / (nFim + 1)), 390]);
    }
    return { tronco: tronco, galho: [165, 358], fim: fim };
  }

  function estados(topicos, guardados) {
    var porId = {}, proximo = null;
    topicos.forEach(function (t) {
      var g = guardados && guardados[t.id];
      var estado = !g ? "aberto" : (g.fim ? "feito" : "andamento");
      porId[t.id] = { estado: estado, feitas: g ? (g.feitas || 0) : 0,
                      total: g ? (g.total || 0) : 0 };
      if (proximo === null && estado !== "feito") proximo = t.id;
    });
    return { porId: porId, proximo: proximo };
  }

  function el(nome, atributos, filhos) {
    var n = global.document.createElementNS(NS, nome);
    Object.keys(atributos || {}).forEach(function (k) {
      n.setAttribute(k, atributos[k]);
    });
    (filhos || []).forEach(function (f) { if (f) n.appendChild(f); });
    return n;
  }

  function texto(conteudo, atributos) {
    var t = el("text", atributos);
    t.textContent = conteudo;
    return t;
  }

  function pontos(lista) {
    return lista.map(function (p) { return p[0] + "," + p[1]; }).join(" ");
  }

  function numero(id) {
    return id.replace(/^kc_/, "");
  }

  function frase(t, e, proximo) {
    var s = { feito: "feito", andamento: "em andamento, " + e.feitas +
              " de " + e.total + " ideias", aberto: "aberto" }[e.estado];
    return "Tópico " + numero(t.id) + ", " + t.titulo + ": " + s +
           (t.id === proximo ? " — próximo sugerido" : "");
  }

  /* `alvo` é o <svg>; `opcoes.href(t)` dá o endereço de cada tópico, e
   * `opcoes.aoClicar(ev, t)`, se houver, decide o clique (o código do
   * participante vai junto). */
  function desenha(alvo, topicos, est, opcoes) {
    opcoes = opcoes || {};
    while (alvo.firstChild) alvo.removeChild(alvo.firstChild);
    alvo.setAttribute("viewBox", "0 0 " + LARGURA + " " + ALTURA);

    var tronco = topicos.filter(function (t) { return !t.fim; });
    var fim = topicos.filter(function (t) { return t.fim; });
    var pos = posicoes(tronco.length, fim.length);
    var onde = {}, indice = {};
    tronco.forEach(function (t, i) { onde[t.id] = pos.tronco[i]; indice[t.id] = i; });
    fim.forEach(function (t, i) { onde[t.id] = pos.fim[i]; });
    var doEsboco = pos.tronco.length === TRONCO.length;

    alvo.appendChild(el("rect", { "class": "c-fundo", width: LARGURA,
                                  height: ALTURA, rx: 18 }));
    alvo.appendChild(el("g", { "class": "c-enfeite", "aria-hidden": "true" }, [
      el("circle", { cx: 300, cy: 40, r: 10 }), el("circle", { cx: 24, cy: 150, r: 9 }),
      el("circle", { cx: 306, cy: 250, r: 11 }), el("circle", { cx: 22, cy: 330, r: 8 })
    ]));

    /* O chão, e o pedaço já andado: até o próximo sugerido (ou o tronco
     * inteiro, se o próximo é um dos três do fim ou se tudo foi feito). */
    var chao = pos.tronco.concat([pos.galho]);
    alvo.appendChild(el("polyline", { "class": "c-chao", points: pontos(chao) }));
    pos.fim.forEach(function (p) {
      alvo.appendChild(el("path", { "class": "c-chao", d: "M" + pos.galho.join(" ") +
                                    " L" + p.join(" ") }));
    });
    var ate = tronco.map(function (t) { return t.id; }).indexOf(est.proximo);
    var andado = pos.tronco.slice(0, ate < 0 ? pos.tronco.length : ate + 1);
    if (andado.length > 1) {
      alvo.appendChild(el("polyline", { "class": "c-andado", points: pontos(andado) }));
    }

    topicos.forEach(function (t) {
      var p = onde[t.id], e = est.porId[t.id];
      var proximo = t.id === est.proximo;
      var classe = "c-parada " + e.estado + (proximo ? " proximo" : "");
      var filhos = [];
      if (proximo) filhos.push(el("circle", { "class": "c-pulso", cx: p[0], cy: p[1], r: 21 }));
      filhos.push(el("circle", { "class": "c-bola", cx: p[0], cy: p[1],
                                 r: proximo ? 16 : 15 }));
      if (e.estado === "feito") {
        filhos.push(el("path", { "class": "c-certo", d: "M" + (p[0] - 7) + " " + p[1] +
                                 " l5 5 l9 -10" }));
      } else {
        filhos.push(texto(numero(t.id), { "class": "c-num", x: p[0], y: p[1] + 3.6 }));
      }
      /* O rótulo: no lugar do esboço, no tronco; embaixo, nos três do fim. */
      var rotulo = t.rotulo || t.titulo;
      var la, lx, ly;
      if (t.fim) { la = "middle"; lx = p[0]; ly = p[1] + 28; }
      else if (doEsboco) {
        var r = ROTULO[indice[t.id]];
        la = r[2]; lx = p[0] + r[0]; ly = p[1] + r[1];
      }
      else if (p[0] < LARGURA / 2) { la = "start"; lx = p[0] + 22; ly = p[1] + 4; }
      else { la = "end"; lx = p[0] - 22; ly = p[1] + 4; }
      filhos.push(texto(rotulo, { "class": "c-rotulo", x: lx, y: ly, "text-anchor": la }));
      if (e.estado === "andamento") {
        filhos.push(texto(e.feitas + " de " + e.total, {
          "class": "c-andamento", x: lx, y: ly + 12, "text-anchor": la }));
      }
      var a = el("a", { "class": classe, href: opcoes.href ? opcoes.href(t) : "#",
                        "aria-label": frase(t, e, est.proximo) }, filhos);
      if (opcoes.aoClicar) {
        a.addEventListener("click", function (ev) { opcoes.aoClicar(ev, t); });
      }
      alvo.appendChild(a);
    });
  }

  global.Caminho = { posicoes: posicoes, estados: estados, desenha: desenha };
})(typeof window !== "undefined" ? window : this);
