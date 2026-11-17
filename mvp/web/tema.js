/* O tema da página: "escuro" (noite de editor) ou "claro" (moldura de
   terminal). Ver tema.css e docs/interface.md.

   Este arquivo é carregado no <head>, ANTES das folhas de estilo e sem
   `defer`: põe `data-tema` em <html> antes de a página ser desenhada,
   e por isso ela não pisca no tema errado ao abrir.

   A escolha: o que a pessoa guardou (chave "structura-tema") → o tema
   do sistema → claro. O localStorage pode não existir ou lançar erro
   (janela anônima, armazenamento bloqueado); então todo acesso a ele
   fica em try/catch, e sem ele a troca vale só para a página aberta.

   Também carrega no Node, para os testes (mvp/test_interface.py). */
(function (global) {
  "use strict";
  var CHAVE = "structura-tema";
  var TEMAS = ["escuro", "claro"];
  var doc = global.document;
  var raiz = doc && doc.documentElement;

  function guardado() {
    try {
      var valor = global.localStorage.getItem(CHAVE);
      return TEMAS.indexOf(valor) >= 0 ? valor : null;
    } catch (e) {
      return null;
    }
  }

  function guarda(tema) {
    try {
      global.localStorage.setItem(CHAVE, tema);
    } catch (e) {
      /* sem armazenamento: a troca vale só nesta página */
    }
  }

  function doSistema() {
    try {
      var escuro = global.matchMedia &&
        global.matchMedia("(prefers-color-scheme: dark)").matches;
      return escuro ? "escuro" : "claro";
    } catch (e) {
      return "claro";
    }
  }

  function aplica(tema) {
    if (raiz) raiz.setAttribute("data-tema", tema);
  }

  function atual() {
    return raiz && raiz.getAttribute("data-tema") === "escuro" ? "escuro" : "claro";
  }

  /* O botão é de alternância: o texto, que a página escreve, fica
     "Tema escuro", e `aria-pressed` diz se ele está ligado. Texto que
     mudasse junto com `aria-pressed` se contradiria para quem usa leitor
     de tela. Ligar o mesmo botão duas vezes não põe outro ouvinte: com
     dois, cada clique trocaria duas vezes e nada mudaria. */
  var ligados = [];
  function liga(botao) {
    if (!botao || ligados.indexOf(botao) >= 0) return;
    ligados.push(botao);
    function mostra() {
      botao.setAttribute("aria-pressed", atual() === "escuro" ? "true" : "false");
    }
    mostra();
    botao.addEventListener("click", function () {
      var novo = atual() === "escuro" ? "claro" : "escuro";
      aplica(novo);
      guarda(novo);
      mostra();
    });
  }

  aplica(guardado() || doSistema());
  global.Tema = { atual: atual, liga: liga };

  /* O botão ainda não existe quando este arquivo roda (está no <head>);
     liga quando a página terminar de chegar. */
  if (doc && doc.addEventListener) {
    doc.addEventListener("DOMContentLoaded", function () {
      liga(doc.getElementById("btn-tema"));
    });
  }
})(typeof window !== "undefined" ? window : this);
