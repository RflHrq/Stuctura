/* O realce do código da trilha: as cores de editor (variáveis --sx-* de
   tema.css). Feito aqui, sem biblioteca, porque o código da trilha é C
   pequeno e o que importa é uma garantia: juntar os pedaços devolve o
   texto IDÊNTICO ao que veio — nem um espaço a mais ou a menos. O teste
   test_o_realce_devolve_o_texto_identico passa todo código das escadas
   por aqui.

   Reconhece: comentário (// até o fim da linha, e o de barra-asterisco
   até o asterisco-barra que fecha); texto
   entre "..." e '...', com \ escapando; número (decimal e 0x...);
   palavra-chave do C que o conteúdo usa; e nome seguido de "(" (com ou
   sem espaço) como função. Nada é reconhecido dentro de texto ou de
   comentário. O resto sai com tipo "", sem cor.

   O bloco é montado com nós de texto, nunca com HTML: código tem < e &.
   Também carrega no Node, para os testes (mvp/test_interface.py). */
(function (global) {
  "use strict";
  var PALAVRAS = {};
  ("int char void return if else for while sizeof const static struct " +
   "double float long unsigned NULL").split(" ").forEach(function (p) {
    PALAVRAS[p] = true;
  });

  var NOME = /[A-Za-z_][A-Za-z0-9_]*/y;
  var NUMERO = /0[xX][0-9a-fA-F]+[uUlL]*|[0-9]+(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?[uUlLfF]*/y;
  var ANTES_DO_PARENTESE = /[ \t]*\(/y;

  function casa(regra, texto, i) {
    regra.lastIndex = i;
    var m = regra.exec(texto);
    return m ? m[0] : "";
  }

  /* Onde termina o texto aberto por `aspas` em i: na aspa que fecha, ou
     no fim da linha, se ninguém fechar (C não deixa o texto seguir). */
  function fimDoTexto(texto, i, aspas) {
    var j = i + 1;
    while (j < texto.length) {
      var c = texto.charAt(j);
      if (c === "\\" && j + 1 < texto.length && texto.charAt(j + 1) !== "\n") { j += 2; continue; }
      if (c === aspas) return j + 1;
      if (c === "\n") return j;
      j++;
    }
    return j;
  }

  function pedacos(texto) {
    var saida = [];
    function poe(tipo, pedaco) {
      var ultimo = saida[saida.length - 1];
      if (tipo === "" && ultimo && ultimo.tipo === "") ultimo.texto += pedaco;
      else saida.push({ tipo: tipo, texto: pedaco });
    }
    var i = 0;
    while (i < texto.length) {
      var c = texto.charAt(i);
      var dois = texto.substr(i, 2);
      var fim, achou;
      if (dois === "//") {
        fim = texto.indexOf("\n", i);
        if (fim < 0) fim = texto.length;
        poe("comentario", texto.slice(i, fim));
      } else if (dois === "/*") {
        fim = texto.indexOf("*/", i + 2);
        fim = fim < 0 ? texto.length : fim + 2;
        poe("comentario", texto.slice(i, fim));
      } else if (c === "\"" || c === "'") {
        fim = fimDoTexto(texto, i, c);
        poe("texto", texto.slice(i, fim));
      } else if ((achou = casa(NOME, texto, i))) {
        fim = i + achou.length;
        if (PALAVRAS[achou]) poe("palavra", achou);
        else if (casa(ANTES_DO_PARENTESE, texto, fim)) poe("funcao", achou);
        else poe("", achou);
      } else if (/[0-9]/.test(c) && (achou = casa(NUMERO, texto, i))) {
        fim = i + achou.length;
        poe("numero", achou);
      } else {
        fim = i + 1;
        poe("", c);
      }
      i = fim;
    }
    return saida;
  }

  /* Troca o conteúdo de `pre` pelo código em cores. */
  function preenche(pre, texto) {
    var doc = global.document;
    pre.textContent = "";
    pedacos(texto).forEach(function (p) {
      if (p.tipo) {
        var span = doc.createElement("span");
        span.className = "sx-" + p.tipo;
        span.textContent = p.texto;
        pre.appendChild(span);
      } else {
        pre.appendChild(doc.createTextNode(p.texto));
      }
    });
  }

  global.Realce = { pedacos: pedacos, preenche: preenche };
})(typeof window !== "undefined" ? window : this);
