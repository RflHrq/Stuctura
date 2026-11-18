/* O desenhista das cenas (docs/interface.md, seção 8; docs/plano-cenas.md).

   Uma cena anima o código da revisão: a linha que roda fica marcada no
   código, e o palco mostra o que ela fez — a caixa que nasce, o valor que
   entra (e o que sai), o ponteiro com o seu bilhete, o NULL, o que vai
   para a tela. A cena vem do servidor em dados (`cena_json`) e foi
   conferida contra o compilador: o palco nunca mostra o que o código não
   faz.

   Personagens desta leva: caixa (a variável: etiqueta com o nome, o tipo
   em cima, o valor como uma bolinha dentro, e "?" quando ainda não há
   valor), ponteiro (a caixa com o bilhete "→ nome" e a seta até a caixa
   apontada) e NULL (o bilhete em branco, com um traço).

   Movimento: um passo por segundo e pouco, com Pausar, Passo e Rever.
   Com "reduzir movimento" no sistema, a cena aparece já no estado final,
   e o passo a passo fica nos botões. Cada passo tem uma frase, que vai
   para leitor de tela (aria-live) e fica escrita embaixo do palco.

   `Cena.estados` é puro e carrega no Node, para os testes
   (mvp/test_cena.py). */
(function (global) {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var PASSO_MS = 1300;

  /* ------------------------------------------------------- os estados */

  function copia(caixas) {
    return caixas.map(function (c) {
      return { nome: c.nome, tipo: c.tipo, de: c.de, valor: c.valor,
               aponta: c.aponta, ativa: false };
    });
  }

  function frase(acao, caixa, antes) {
    switch (acao.acao) {
      case "cria":
        return "cria a caixa " + acao.nome + (caixa && caixa.de ? ", de " + caixa.de : "") +
               ", ainda sem valor";
      case "guarda":
        return "guarda " + acao.valor + " em " + acao.em +
               (antes !== null && antes !== undefined ? "; o " + antes + " que estava lá sai" : "");
      case "le": return "lê o valor de " + acao.nome;
      case "mostra": return "mostra " + acao.texto + " na tela";
      case "aponta": return "guarda em " + acao.de + " o endereço de " + acao.para;
      case "nulo": return "guarda NULL em " + acao.nome;
      case "segue": return "segue o bilhete de " + acao.nome;
      case "some": return "a caixa " + acao.nome + " some";
      default: return acao.acao;
    }
  }

  /* Os estados da cena: o começo (palco vazio) e um depois de cada passo. */
  function estados(cena) {
    var atores = {};
    (cena.atores || []).forEach(function (a) { atores[a.nome] = a; });
    var caixas = [], saida = [];
    var lista = [{ linha: 0, caixas: [], saida: [], descricao: "Antes da primeira linha." }];
    (cena.passos || []).forEach(function (p) {
      caixas = copia(caixas);
      var achar = function (nome) {
        for (var i = 0; i < caixas.length; i++) if (caixas[i].nome === nome) return caixas[i];
        return null;
      };
      var partes = [];
      p.faz.forEach(function (a) {
        var alvo = a.nome || a.em || a.de;
        var c = achar(alvo);
        var antes = c ? c.valor : null;
        if (a.acao === "cria" && !c) {
          var at = atores[a.nome] || { tipo: "caixa", de: "" };
          c = { nome: a.nome, tipo: at.tipo, de: at.de, valor: null, aponta: null, ativa: false };
          caixas.push(c);
        } else if (a.acao === "guarda" && c) {
          c.valor = String(a.valor);
        } else if (a.acao === "aponta" && c) {
          c.aponta = a.para;
        } else if (a.acao === "nulo" && c) {
          c.aponta = "";
        } else if (a.acao === "mostra") {
          saida = saida.concat([a.texto]);
        } else if (a.acao === "some" && c) {
          caixas = caixas.filter(function (x) { return x !== c; });
          c = null;
        }
        if (c) c.ativa = true;
        partes.push(frase(a, c || atores[alvo], antes));
      });
      lista.push({ linha: p.linha, caixas: caixas, saida: saida,
                   descricao: "Linha " + p.linha + ": " + partes.join(", e ") + "." });
    });
    return lista;
  }

  /* ------------------------------------------------------- o desenho */

  function el(nome, atributos, filhos) {
    var n = global.document.createElement(nome);
    Object.keys(atributos || {}).forEach(function (k) {
      if (k === "texto") n.textContent = atributos[k];
      else n.setAttribute(k, atributos[k]);
    });
    (filhos || []).forEach(function (f) { if (f) n.appendChild(f); });
    return n;
  }

  function sv(nome, atributos, filhos) {
    var n = global.document.createElementNS(NS, nome);
    Object.keys(atributos || {}).forEach(function (k) {
      if (k === "texto") n.textContent = atributos[k];
      else n.setAttribute(k, atributos[k]);
    });
    (filhos || []).forEach(function (f) { if (f) n.appendChild(f); });
    return n;
  }

  var LARG = 104, ALT = 132, TOPO = 26;

  /* Uma caixa de papelão, aberta em cima, com a etiqueta do nome na frente
   * e o tipo escrito em cima. Dentro, a bolinha do valor, o "?" de quando
   * não há valor, ou o bilhete do ponteiro. */
  function caixa(c, x) {
    var g = sv("g", { "class": "cn-caixa" + (c.ativa ? " cn-ativa" : ""),
                      transform: "translate(" + x + " 0)" });
    if (c.de) g.appendChild(sv("text", { "class": "cn-tipo", x: LARG / 2, y: TOPO - 8,
                                         "text-anchor": "middle", texto: c.de }));
    g.appendChild(sv("path", { "class": "cn-aba", d: "M8 " + TOPO + " L20 " + (TOPO - 6) +
                               " L" + (LARG - 20) + " " + (TOPO - 6) + " L" + (LARG - 8) + " " + TOPO + " Z" }));
    g.appendChild(sv("rect", { "class": "cn-corpo", x: 8, y: TOPO, width: LARG - 16,
                               height: 78, rx: 6 }));
    var meio = TOPO + 34;
    if (c.tipo === "ponteiro" && c.aponta !== null && c.aponta !== undefined) {
      g.appendChild(sv("rect", { "class": "cn-bilhete", x: 20, y: meio - 15, width: LARG - 40,
                                 height: 28, rx: 3, transform: "rotate(-3 " + LARG / 2 + " " + meio + ")" }));
      g.appendChild(sv("text", { "class": "cn-bilhete-txt", x: LARG / 2, y: meio + 4,
                                 "text-anchor": "middle",
                                 texto: c.aponta === "" ? "NULL" : "→ " + c.aponta }));
    } else if (c.valor !== null && c.valor !== undefined) {
      g.appendChild(sv("circle", { "class": "cn-bola", cx: LARG / 2, cy: meio, r: 19 }));
      g.appendChild(sv("text", { "class": "cn-valor", x: LARG / 2, y: meio + 5,
                                 "text-anchor": "middle", texto: c.valor }));
    } else {
      g.appendChild(sv("text", { "class": "cn-sobra", x: LARG / 2, y: meio + 7,
                                 "text-anchor": "middle", texto: "?" }));
    }
    g.appendChild(sv("rect", { "class": "cn-etiqueta", x: 18, y: TOPO + 82, width: LARG - 36,
                               height: 22, rx: 5 }));
    g.appendChild(sv("text", { "class": "cn-nome", x: LARG / 2, y: TOPO + 97,
                               "text-anchor": "middle", texto: c.nome }));
    return g;
  }

  function palco(svg, estado) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var n = Math.max(estado.caixas.length, 1);
    var largura = Math.max(320, n * (LARG + 10) + 20);
    svg.setAttribute("viewBox", "0 0 " + largura + " " + ALT);
    var x0 = (largura - estado.caixas.length * (LARG + 10) + 10) / 2;
    var onde = {};
    estado.caixas.forEach(function (c, i) {
      onde[c.nome] = x0 + i * (LARG + 10);
      svg.appendChild(caixa(c, onde[c.nome]));
    });
    /* As setas dos ponteiros, por cima: do bilhete até a caixa apontada. */
    estado.caixas.forEach(function (c) {
      if (c.tipo !== "ponteiro" || !c.aponta || onde[c.aponta] === undefined) return;
      /* A ponta cai à direita do tipo escrito em cima da caixa apontada,
       * para a seta não riscar o "int". */
      var x1 = onde[c.nome] + LARG / 2, x2 = onde[c.aponta] + LARG - 24;
      var alto = 6;
      svg.appendChild(sv("path", { "class": "cn-seta",
        d: "M" + x1 + " " + (TOPO + 18) + " C " + x1 + " " + alto + ", " + x2 + " " + alto +
           ", " + x2 + " " + (TOPO - 2) }));
    });
    if (!estado.caixas.length) {
      svg.appendChild(sv("text", { "class": "cn-vazio", x: largura / 2, y: ALT / 2,
                                   "text-anchor": "middle", texto: "(nenhuma caixa ainda)" }));
    }
  }

  /* A cena inteira: o código com a linha marcada, o palco, a tela do
   * programa, a frase do passo e os botões. Devolve o elemento. */
  function desenha(cena, codigo) {
    var lista = estados(cena);
    var raiz = el("figure", { "class": "cena", "aria-label": "Cena: o código rodando, linha a linha" });

    var linhas = String(codigo || "").replace(/\n+$/, "").split("\n");
    var pre = el("pre", { "class": "codigo cn-codigo" });
    var spans = linhas.map(function (l, i) {
      var s = el("span", { "class": "cn-linha", "data-linha": String(i + 1) });
      if (global.Realce) global.Realce.preenche(s, l); else s.textContent = l;
      pre.appendChild(s);
      if (i < linhas.length - 1) pre.appendChild(global.document.createTextNode("\n"));
      return s;
    });
    raiz.appendChild(pre);

    var svg = sv("svg", { "class": "cn-palco", role: "img",
                          "aria-label": "O palco da cena" });
    raiz.appendChild(svg);
    var tela = el("pre", { "class": "terminal cn-tela", "aria-label": "O que o programa mostra" });
    raiz.appendChild(tela);
    var legenda = el("p", { "class": "cn-frase", "aria-live": "polite" });
    raiz.appendChild(legenda);

    var bPausa = el("button", { type: "button", "class": "btn-topo", texto: "Pausar" });
    var bPasso = el("button", { type: "button", "class": "btn-topo", texto: "Passo" });
    var bRever = el("button", { type: "button", "class": "btn-topo", texto: "Rever" });
    raiz.appendChild(el("div", { "class": "cn-botoes" }, [bPausa, bPasso, bRever]));

    var i = 0, relogio = null;
    var calmo = !!(global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches);

    function mostra(k) {
      i = k;
      var e = lista[k];
      spans.forEach(function (s, j) { s.classList.toggle("cn-agora", j + 1 === e.linha); });
      palco(svg, e);
      tela.textContent = e.saida.join("\n");
      tela.hidden = !e.saida.length;
      legenda.textContent = e.descricao;
      bPasso.disabled = k >= lista.length - 1;
    }
    /* Retomar, e não Continuar: Continuar é o botão da sessão, logo
     * abaixo da cena, e os dois não podem ter o mesmo nome. */
    function para() {
      if (relogio) global.clearTimeout(relogio);
      relogio = null;
      bPausa.textContent = "Retomar";
    }
    function anda() {
      bPausa.textContent = "Pausar";
      relogio = global.setTimeout(function tique() {
        /* A tela mudou e a cena saiu da página: o relógio para sozinho. */
        if (!raiz.isConnected) { relogio = null; return; }
        if (i >= lista.length - 1) {
          para();
          bPausa.textContent = "Pausar";
          bPausa.disabled = true;
          return;
        }
        mostra(i + 1);
        relogio = global.setTimeout(tique, PASSO_MS);
      }, PASSO_MS);
    }
    bPausa.addEventListener("click", function () {
      if (relogio) para(); else anda();
    });
    bPasso.addEventListener("click", function () {
      para();
      if (i < lista.length - 1) mostra(i + 1);
    });
    bRever.addEventListener("click", function () {
      para();
      bPausa.disabled = false;
      mostra(0);
      if (!calmo) anda();
    });

    if (calmo) {
      /* Reduzir movimento: o estado final, e o passo a passo nos botões. */
      mostra(lista.length - 1);
      bPausa.disabled = true;
      bPausa.textContent = "Pausar";
    } else {
      mostra(0);
      anda();
    }
    return raiz;
  }

  global.Cena = { estados: estados, desenha: desenha };
})(typeof window !== "undefined" ? window : this);
