/* A navegação dos slides da defesa (docs/apresentacao.md).

   Avançam: →, espaço, PageDown (o passador de slides manda PageDown),
   Enter e o clique. Voltam: ←, PageUp e Backspace; num slide com passos,
   voltar desfaz o último passo revelado. Home e End vão ao primeiro e ao
   último; F põe em tela cheia; N mostra as notas de quem apresenta.
   Com ?pdf=1, tudo aparece de uma vez, um slide por página. */
(function () {
  "use strict";
  var slides = Array.prototype.slice.call(document.querySelectorAll("section.slide"));
  var palco = document.getElementById("palco");
  var contador = document.getElementById("contador");
  var progresso = document.getElementById("progresso");
  var pdf = /[?&]pdf=1/.test(location.search);
  var atual = 0, cenaFeita = false;

  /* O rodapé de cada slide: a referência na numeração do PDF, com a página. */
  slides.forEach(function (s) {
    var refs = (s.getAttribute("data-ref") || "").split("·")
      .map(function (r) { return r.trim(); }).filter(Boolean);
    if (!refs.length) return;
    var pe = document.createElement("footer");
    pe.className = "ref";
    pe.innerHTML = "Monografia: " + refs.map(function (r) {
      var p = window.REFS && window.REFS[r];
      return "<b>" + r + "</b>" + (p ? ", p. " + p : "");
    }).join(" · ");
    s.appendChild(pe);
  });

  function passos(s) {
    return Array.prototype.slice.call(s.querySelectorAll("[data-passo]"))
      .sort(function (a, b) { return a.getAttribute("data-passo") - b.getAttribute("data-passo"); });
  }
  function grupos(s) {
    var vistos = [];
    passos(s).forEach(function (el) {
      var n = el.getAttribute("data-passo");
      if (vistos.indexOf(n) < 0) vistos.push(n);
    });
    return vistos;
  }
  function revelados(s) {
    return grupos(s).filter(function (n) {
      return s.querySelector('[data-passo="' + n + '"]').classList.contains("visto");
    }).length;
  }
  function revela(s, quantos) {
    var g = grupos(s);
    passos(s).forEach(function (el) {
      el.classList.toggle("visto", g.indexOf(el.getAttribute("data-passo")) < quantos);
    });
  }

  function montaCena(s) {
    var alvo = s.querySelector(".cena-viva");
    if (!alvo || cenaFeita || !window.Cena || !window.CENA) return;
    alvo.appendChild(window.Cena.desenha(window.CENA.cena, window.CENA.codigo));
    cenaFeita = true;
  }

  function mostra(i, quantos) {
    atual = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach(function (s, k) { s.classList.toggle("atual", k === atual); });
    var s = slides[atual];
    revela(s, quantos === undefined ? 0 : quantos);
    montaCena(s);
    contador.textContent = (atual + 1) + " / " + slides.length;
    progresso.style.width = ((atual + 1) / slides.length * 100) + "%";
    if (location.hash !== "#" + (atual + 1)) history.replaceState(null, "", "#" + (atual + 1));
  }

  function avanca() {
    var s = slides[atual], feitos = revelados(s);
    if (feitos < grupos(s).length) revela(s, feitos + 1);
    else if (atual < slides.length - 1) mostra(atual + 1, 0);
  }
  function volta() {
    var s = slides[atual], feitos = revelados(s);
    if (feitos > 0) revela(s, feitos - 1);
    else if (atual > 0) mostra(atual - 1, grupos(slides[atual - 1]).length);
  }

  function escala() {
    var k = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    palco.style.transform = "translate(-50%, -50%) scale(" + k + ")";
  }

  if (pdf) {
    document.body.classList.add("pdf");
    slides.forEach(function (s) { s.classList.add("atual"); revela(s, grupos(s).length); });
    return;
  }

  document.addEventListener("keydown", function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var k = e.key;
    if (k === "ArrowRight" || k === " " || k === "PageDown" || k === "Enter") { avanca(); e.preventDefault(); }
    else if (k === "ArrowLeft" || k === "PageUp" || k === "Backspace") { volta(); e.preventDefault(); }
    else if (k === "Home") mostra(0, 0);
    else if (k === "End") mostra(slides.length - 1, 0);
    else if (k === "f" || k === "F") {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    } else if (k === "n" || k === "N") document.body.classList.toggle("com-notas");
  });
  palco.addEventListener("click", function (e) {
    if (e.target.closest("button")) return; // os botões da cena
    avanca();
  });
  window.addEventListener("resize", escala);
  escala();
  var inicio = parseInt((location.hash || "#1").slice(1), 10);
  mostra(isNaN(inicio) ? 0 : inicio - 1, 0);
})();
