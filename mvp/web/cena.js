/* O desenhista das cenas (docs/interface.md, seção 8; docs/plano-cenas.md).

   Uma cena anima o código da revisão: a linha que roda fica marcada no
   código, e o palco mostra o que ela fez — a caixa que nasce, o valor que
   entra (e o que sai), o ponteiro com o seu bilhete, o NULL, o que vai
   para a tela. A cena vem do servidor em dados (`cena_json`) e foi
   conferida contra o compilador: o palco nunca mostra o que o código não
   faz.

   Personagens: caixa (a variável: etiqueta com o nome, o tipo em cima, o
   valor como uma bolinha dentro, e "?" quando ainda não há valor),
   ponteiro (a caixa com o bilhete "→ nome" e a seta até a caixa apontada),
   NULL (o bilhete com NULL), fileira (o array: as caixas lado a lado, ou
   em linhas e colunas), bancada (a função enquanto roda: um andar com a
   primeira linha dela por título, onde nascem as caixas dela, que somem
   na volta) e o bloco alugado (o que o malloc pede: mora no andar do
   monte, com a placa "alugado", e o free o deixa apagado, "devolvido").

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
               valores: c.valores ? c.valores.slice() : null,
               tamanho: c.tamanho, aponta: c.aponta, solto: c.solto,
               dono: c.dono, devolvido: c.devolvido, fica: c.fica, ativa: false,
               foco: null };
    });
  }

  /* `notas[2]` -> {nome: "notas", idx: [2]} */
  function ref(texto) {
    var m = /^([A-Za-z_]\w*)((?:\[\d+\])*)$/.exec(String(texto || ""));
    if (!m) return { nome: texto, idx: [] };
    var idx = [];
    m[2].replace(/\[(\d+)\]/g, function (tudo, d) { idx.push(Number(d)); return tudo; });
    return { nome: m[1], idx: idx };
  }

  function plano(idx, tamanho) {
    var k = 0;
    for (var i = 0; i < idx.length; i++) k = k * tamanho[i] + idx[i];
    return k;
  }

  function quantas(tamanho) {
    var n = 1;
    (tamanho || []).forEach(function (t) { n *= t; });
    return n;
  }

  function nova(nome, at, dono) {
    var tem = !!(at.tamanho && at.tamanho.length);
    var valores = null;
    if (tem) {
      valores = [];
      for (var i = 0; i < quantas(at.tamanho); i++) valores.push(null);
    }
    return { nome: nome, tipo: at.tipo || "caixa", de: at.de || "", valor: null,
             valores: valores, tamanho: tem ? at.tamanho.slice() : null,
             aponta: null, solto: false, dono: dono, devolvido: false,
             fica: !!at.fica, ativa: false, foco: null };
  }

  function medida(at) {
    var t = at && at.tamanho;
    if (!t || !t.length) return "";
    return t.length === 2 ? t[0] + " por " + t[1] : String(t[0]);
  }

  function frase(acao, caixa, antes, foram, ficaram) {
    switch (acao.acao) {
      case "cria":
        if (caixa && caixa.tipo === "fileira") {
          return "cria a fileira " + acao.nome + ", de " + medida(caixa) + " " + caixa.de +
                 ", ainda sem valor";
        }
        return "cria a caixa " + acao.nome + (caixa && caixa.de ? ", de " + caixa.de : "") +
               ", ainda sem valor";
      case "guarda":
        if (Array.isArray(acao.valor)) return "guarda " + acao.valor.join(", ") + " em " + acao.em;
        return "guarda " + acao.valor + " em " + acao.em +
               (antes !== null && antes !== undefined ? "; o " + antes + " que estava lá sai" : "");
      case "le": return "lê o valor de " + acao.nome;
      case "mostra": return "mostra " + acao.texto + " na tela";
      case "aponta": return "guarda em " + acao.de + " o endereço de " + acao.para;
      case "nulo": return "guarda NULL em " + acao.nome;
      case "segue": return "segue o bilhete de " + acao.nome;
      case "some": return "a caixa " + acao.nome + " some";
      case "chama": return "chama " + acao.nome + ": a bancada de " + acao.nome + " abre";
      case "volta":
        return acao.nome + " termina: a bancada fecha" +
               (foram && foram.length ? ", e " + foram.join(" e ") +
                (foram.length > 1 ? " somem com ela" : " some com ela") : "") +
               (ficaram && ficaram.length ? ", e " + ficaram.join(" e ") +
                (ficaram.length > 1 ? " ficam" : " fica") + ": é static" : "");
      case "aluga":
        return "aluga no monte um bloco " +
               (caixa && caixa.tamanho ? "de " + medida(caixa) + " " + caixa.de
                                       : "de um " + (caixa ? caixa.de : "")) +
               ", e guarda em " + acao.para + " o endereço dele";
      case "devolve":
        return "devolve o bloco " + acao.nome + " (o free): ele já não é do programa";
      case "diz": return acao.texto;
      default: return acao.acao;
    }
  }

  /* Os estados da cena: o começo (palco vazio) e um depois de cada passo. */
  function estados(cena) {
    var atores = {};
    (cena.atores || []).forEach(function (a) { atores[a.nome] = a; });
    var caixas = [], saida = [], bancadas = [];
    var lista = [{ linha: 0, caixas: [], bancadas: [], saida: [],
                   descricao: "Antes da primeira linha." }];
    (cena.passos || []).forEach(function (p) {
      caixas = copia(caixas);
      bancadas = bancadas.slice();
      var achar = function (nome) {
        for (var i = 0; i < caixas.length; i++) if (caixas[i].nome === nome) return caixas[i];
        return null;
      };
      var solta = function (nome) {
        caixas.forEach(function (x) { if (x.aponta && ref(x.aponta).nome === nome) x.solto = true; });
      };
      var partes = [];
      p.faz.forEach(function (a) {
        var r = ref(a.nome || a.em || a.de);
        var c = achar(r.nome);
        var antes = null, foram = null, ficaram = null;
        if (c && a.acao === "guarda" && !Array.isArray(a.valor)) {
          antes = c.valores && r.idx.length ? c.valores[plano(r.idx, c.tamanho)] : c.valor;
        }
        switch (a.acao) {
          case "cria":
            if (!c) {
              c = nova(a.nome, atores[a.nome] || {},
                       bancadas.length ? bancadas[bancadas.length - 1].nome : null);
              caixas.push(c);
            }
            break;
          case "guarda":
            if (!c) break;
            if (Array.isArray(a.valor)) c.valores = a.valor.map(String);
            else if (c.valores && r.idx.length) c.valores[plano(r.idx, c.tamanho)] = String(a.valor);
            else c.valor = String(a.valor);
            break;
          case "aponta":
            if (c) { c.aponta = a.para; c.solto = false; }
            break;
          case "nulo":
            if (c) { c.aponta = ""; c.solto = false; }
            break;
          case "mostra":
            saida = saida.concat([a.texto]);
            break;
          case "some":
            if (c) {
              caixas = caixas.filter(function (x) { return x !== c; });
              solta(a.nome);
              c = null;
            }
            break;
          case "chama":
            bancadas.push({ nome: a.nome, de: (atores[a.nome] || {}).de || "" });
            c = null;
            break;
          case "volta":
            if (bancadas.length && bancadas[bancadas.length - 1].nome === a.nome) bancadas.pop();
            foram = [];
            ficaram = [];
            caixas = caixas.filter(function (x) {
              if (x.dono !== a.nome) return true;
              if (x.fica) { x.dono = null; ficaram.push(x.nome); return true; }
              foram.push(x.nome);
              return false;
            });
            foram.forEach(solta);
            c = null;
            break;
          case "aluga":
            c = nova(a.nome, atores[a.nome] || { tipo: "bloco" }, null);
            caixas.push(c);
            var dono = achar(a.para);
            if (dono) { dono.aponta = a.nome; dono.solto = false; dono.ativa = true; }
            break;
          case "devolve":
            if (c) {
              c.devolvido = true;
              c.valor = null;
              if (c.valores) c.valores = c.valores.map(function () { return null; });
            }
            break;
        }
        if (c) c.ativa = true;
        /* A caixinha que a linha lê ou escreve (a[1][0]) fica marcada. */
        if (c && c.valores && r.idx.length && (a.acao === "le" || a.acao === "guarda")) {
          c.foco = plano(r.idx, c.tamanho);
        }
        partes.push(frase(a, c || atores[r.nome], antes, foram, ficaram));
      });
      lista.push({ linha: p.linha, caixas: caixas, bancadas: bancadas, saida: saida,
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

  var LARG = 104, ALT = 132, TOPO = 26, CEL = 36, TITULO = 22;

  function largura(c) {
    if (!c.tamanho) return LARG;
    return Math.max(LARG, c.tamanho[c.tamanho.length - 1] * CEL + 24);
  }

  /* A grade de uma fileira (ou bloco com várias caixas): onde fica cada
   * caixinha dentro da caixa grande. */
  function grade(c) {
    var linhas = c.tamanho.length === 2 ? c.tamanho[0] : 1;
    var colunas = c.tamanho[c.tamanho.length - 1];
    var alto = linhas === 1 ? 34 : 32;
    return { linhas: linhas, colunas: colunas, alto: alto,
             x0: (largura(c) - colunas * CEL) / 2,
             y0: linhas === 1 ? TOPO + 12 : TOPO + 7 };
  }

  function rotuloDoTipo(c) {
    if (c.tipo === "fileira") return c.de + c.tamanho.map(function (t) { return "[" + t + "]"; }).join("");
    return c.de;
  }

  /* Uma caixa de papelão, aberta em cima, com a etiqueta do nome na frente
   * e o tipo escrito em cima. Dentro, a bolinha do valor, o "?" de quando
   * não há valor, o bilhete do ponteiro, ou as caixinhas da fileira. */
  function caixa(c, x, y) {
    var w = largura(c);
    var g = sv("g", { "class": "cn-caixa" + (c.ativa ? " cn-ativa" : "") +
                               (c.devolvido ? " cn-devolvido" : "") +
                               (c.solto ? " cn-solto" : ""),
                      transform: "translate(" + x + " " + y + ")" });
    var tipo = rotuloDoTipo(c);
    if (tipo) g.appendChild(sv("text", { "class": "cn-tipo", x: w / 2, y: TOPO - 8,
                                         "text-anchor": "middle", texto: tipo }));
    g.appendChild(sv("path", { "class": "cn-aba", d: "M8 " + TOPO + " L20 " + (TOPO - 6) +
                               " L" + (w - 20) + " " + (TOPO - 6) + " L" + (w - 8) + " " + TOPO + " Z" }));
    g.appendChild(sv("rect", { "class": "cn-corpo", x: 8, y: TOPO, width: w - 16,
                               height: 78, rx: 6 }));
    var meio = TOPO + 34;
    if (c.tipo === "ponteiro" && c.aponta !== null && c.aponta !== undefined) {
      g.appendChild(sv("rect", { "class": "cn-bilhete", x: 20, y: meio - 15, width: w - 40,
                                 height: 28, rx: 3, transform: "rotate(-3 " + w / 2 + " " + meio + ")" }));
      var bilhete = c.aponta === "" ? "NULL" : "→ " + c.aponta;
      var txt = { "class": "cn-bilhete-txt", x: w / 2, y: meio + 4,
                  "text-anchor": "middle", texto: bilhete };
      /* "→ notas[0]" não cabe no bilhete: o texto encolhe para caber. */
      if (bilhete.length > 8) {
        txt.textLength = w - 48;
        txt.lengthAdjust = "spacingAndGlyphs";
      }
      g.appendChild(sv("text", txt));
    } else if (c.valores) {
      var q = grade(c);
      c.valores.forEach(function (v, k) {
        var col = k % q.colunas, lin = Math.floor(k / q.colunas);
        var cx = q.x0 + col * CEL, cy = q.y0 + lin * q.alto;
        g.appendChild(sv("rect", { "class": "cn-cel" + (v === null ? "" : " cn-cel-cheia") +
                                            (k === c.foco ? " cn-cel-foco" : ""),
                                   x: cx + 2, y: cy, width: CEL - 4, height: q.alto - 4, rx: 4 }));
        g.appendChild(sv("text", { "class": v === null ? "cn-cel-sobra" : "cn-cel-txt",
                                   x: cx + CEL / 2, y: cy + q.alto / 2 + 3,
                                   "text-anchor": "middle", texto: v === null ? "?" : v }));
        if (q.linhas === 1) {
          g.appendChild(sv("text", { "class": "cn-indice", x: cx + CEL / 2, y: cy + q.alto + 9,
                                     "text-anchor": "middle", texto: "[" + k + "]" }));
        }
      });
    } else if (c.valor !== null && c.valor !== undefined) {
      g.appendChild(sv("circle", { "class": "cn-bola", cx: w / 2, cy: meio, r: 19 }));
      g.appendChild(sv("text", { "class": "cn-valor", x: w / 2, y: meio + 5,
                                 "text-anchor": "middle", texto: c.valor }));
    } else {
      g.appendChild(sv("text", { "class": "cn-sobra", x: w / 2, y: meio + 7,
                                 "text-anchor": "middle", texto: "?" }));
    }
    /* A placa do bloco, dentro da caixa, embaixo do valor: em cima ela
     * ficava no caminho da seta que desce até o monte. */
    if (c.tipo === "bloco") {
      g.appendChild(sv("text", { "class": "cn-placa", x: w / 2, y: TOPO + 71,
                                 "text-anchor": "middle",
                                 texto: c.devolvido ? "devolvido" : "alugado" }));
    }
    /* A etiqueta do nome tem o tamanho do nome, e não da fileira inteira. */
    var le = Math.min(w - 36, Math.max(68, c.nome.length * 8 + 24));
    g.appendChild(sv("rect", { "class": "cn-etiqueta", x: (w - le) / 2, y: TOPO + 82, width: le,
                               height: 22, rx: 5 }));
    g.appendChild(sv("text", { "class": "cn-nome", x: w / 2, y: TOPO + 97,
                               "text-anchor": "middle", texto: c.nome }));
    return g;
  }

  /* Os andares do palco: o main em cima, uma bancada por função aberta
   * (a última chamada embaixo), e o monte, onde moram os blocos. */
  function andares(estado) {
    var main = [], monte = [], porBancada = {};
    estado.caixas.forEach(function (c) {
      if (c.tipo === "bloco") monte.push(c);
      else if (c.dono) (porBancada[c.dono] = porBancada[c.dono] || []).push(c);
      else main.push(c);
    });
    var lista = [{ tipo: "main", titulo: "", caixas: main }];
    (estado.bancadas || []).forEach(function (b) {
      lista.push({ tipo: "bancada", titulo: b.de || b.nome, caixas: porBancada[b.nome] || [] });
    });
    if (monte.length) lista.push({ tipo: "monte", titulo: "o monte: o que o malloc aluga", caixas: monte });
    if (lista.length > 1) lista[0].titulo = "main";
    return lista;
  }

  function palco(svg, estado) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var lista = andares(estado);
    var total = 320;
    lista.forEach(function (a) {
      a.w = a.caixas.reduce(function (s, c) { return s + largura(c); }, 0) +
            10 * Math.max(a.caixas.length - 1, 0);
      total = Math.max(total, a.w + 40);
    });
    var y = 0, onde = {};
    lista.forEach(function (a) {
      /* O título da bancada e do monte fica embaixo, à esquerda: as setas
       * entram e saem por cima desses andares, e não riscam o texto. */
      var main = a.tipo === "main";
      var alto = main ? (a.titulo ? TITULO : 0) + ALT : TITULO + ALT + 6;
      if (!main) {
        svg.appendChild(sv("rect", { "class": "cn-moldura cn-" + a.tipo, x: 6, y: y + 3,
                                     width: total - 12, height: alto - 6, rx: 10 }));
      }
      if (a.titulo) {
        svg.appendChild(sv("text", { "class": "cn-andar", x: 16, y: main ? y + 17 : y + alto - 10,
                                     texto: a.titulo }));
      }
      var y0 = main ? y + (a.titulo ? TITULO : 0) : y + 6, x = (total - a.w) / 2;
      a.caixas.forEach(function (c) {
        onde[c.nome] = { x: x, y: y0, c: c };
        svg.appendChild(caixa(c, x, y0));
        x += largura(c) + 10;
      });
      if (!a.caixas.length && a.tipo === "bancada") {
        svg.appendChild(sv("text", { "class": "cn-vazio", x: total / 2, y: y0 + ALT / 2,
                                     "text-anchor": "middle", texto: "(ainda sem caixas)" }));
      }
      y += alto;
    });
    svg.setAttribute("viewBox", "0 0 " + total + " " + y);
    /* Com mais de um andar, o palco cresce em altura em vez de encolher. */
    if (svg.style) svg.style.maxHeight = (lista.length > 1 ? 170 * lista.length : 220) + "px";

    /* As setas dos ponteiros, por cima: do bilhete até a caixa apontada (ou
     * a caixinha da fileira). Para o que sumiu, seta nenhuma. */
    estado.caixas.forEach(function (c) {
      if (c.tipo !== "ponteiro" || !c.aponta || c.solto) return;
      var r = ref(c.aponta), de = onde[c.nome], para = onde[r.nome];
      if (!de || !para) return;
      var celula = null;
      if (r.idx.length && para.c.tamanho) {
        var q = grade(para.c), k = plano(r.idx, para.c.tamanho);
        celula = { x: para.x + q.x0 + (k % q.colunas) * CEL + CEL / 2,
                   y: para.y + q.y0 + Math.floor(k / q.colunas) * q.alto };
      }
      var d;
      if (para.y < de.y) {
        /* O alvo num andar de cima (a bancada apontando para o main): a
         * seta sai do canto de cima do ponteiro, à direita do tipo, e
         * entra por baixo da caixa apontada — sem atravessar caixa. */
        var xa = de.x + largura(de.c) - 16, ya = de.y + TOPO - 4;
        var xb = celula ? celula.x : para.x + largura(para.c) / 2;
        var yb = para.y + TOPO + 106, ym = (ya + yb) / 2;
        d = "M" + xa + " " + ya + " C " + xa + " " + ym + ", " + xb + " " +
            ym + ", " + xb + " " + yb;
      } else {
        /* No mesmo andar, por cima; num andar de baixo (o monte), saindo de
         * baixo da etiqueta. A ponta cai à direita do tipo escrito em cima
         * da caixa apontada, para a seta não riscar o "int". */
        var mesmo = para.y === de.y;
        var x1 = de.x + LARG / 2, y1 = mesmo ? de.y + TOPO + 18 : de.y + TOPO + 106;
        var lp = largura(para.c), tipo = rotuloDoTipo(para.c) || "";
        var x2 = celula ? celula.x
                        : para.x + Math.min(lp - 8, Math.max(lp - 24, lp / 2 + tipo.length * 3.4 + 6));
        var y2 = celula ? celula.y : para.y + TOPO - 2;
        var c1 = mesmo ? de.y + 6 : (y1 + y2) / 2, c2 = mesmo ? de.y + 6 : (y1 + y2) / 2;
        d = "M" + x1 + " " + y1 + " C " + x1 + " " + c1 + ", " + x2 + " " + c2 +
            ", " + x2 + " " + y2;
      }
      svg.appendChild(sv("path", { "class": "cn-seta" + (para.c.devolvido ? " cn-seta-morta" : ""),
                                   d: d }));
    });
    if (!estado.caixas.length && lista.length === 1) {
      svg.appendChild(sv("text", { "class": "cn-vazio", x: total / 2, y: ALT / 2,
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
