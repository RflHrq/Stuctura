/* Cliente do MVP.
 *
 * Nenhuma regra aqui. O servidor devolve a próxima tela e este arquivo
 * desenha. A única coisa que o cliente decide é QUANDO mostrar o retorno
 * imediato: ele vem da resposta do servidor (certa/errada), e a tela de
 * retorno é um passo de apresentação, não de fluxo.
 */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var TELAS = ["ensino", "atividade", "retorno", "refutacao", "mapa"];

  var S = {
    sessao: null,
    tela: null,
    escolha: null,
    confianca: null,
    inicio: 0,
    pendente: null      // tela que vem depois do retorno imediato
  };

  function mostra(nome) {
    TELAS.forEach(function (t) {
      $("tela-" + t).classList.toggle("oculto", t !== nome);
    });
    S.inicio = performance.now();
  }

  function decorrido() {
    return Math.max(0, Math.round(performance.now() - S.inicio));
  }

  async function api(rota, corpo) {
    var r = await fetch(rota, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo || {})
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }

  /* ---------------------------------------------------------- despacho */

  function aplica(j) {
    S.sessao = j.sessao;
    S.tela = j.tela;
    var t = j.tela;
    if (t.tipo === "ensino") return telaEnsino(t);
    if (t.tipo === "atividade") return telaAtividade(t);
    if (t.tipo === "refutacao") return telaRefutacao(t);
    if (t.tipo === "mapa") return telaMapa(t);
  }

  /* ------------------------------------------------------------ ensino */

  function telaEnsino(t) {
    $("trilha").textContent = "Aprendendo";
    $("ensino-passo").textContent = "Ideia " + t.indice + " de " + t.total;
    $("ensino-texto").textContent = t.texto;
    $("btn-ensino").onclick = function () { responde({}); };
    mostra("ensino");
  }

  /* --------------------------------------------------------- atividade */

  function telaAtividade(t) {
    S.escolha = null;
    S.confianca = null;
    $("trilha").textContent = t.fase === "treino"
      ? "Treinando · premissa " + t.no
      : "Praticando";
    $("atv-etiqueta").textContent = t.fase === "treino"
      ? "Treino · " + rotuloFormato(t.formato)
      : "Atividade";
    $("atv-enunciado").textContent = t.texto;

    var caixa = $("atv-opcoes");
    caixa.innerHTML = "";
    t.opcoes.forEach(function (o, i) {
      var b = document.createElement("button");
      b.className = "opcao";
      b.type = "button";
      b.textContent = o.texto;
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () {
        S.escolha = i;
        Array.prototype.forEach.call(caixa.children, function (x, k) {
          x.setAttribute("aria-pressed", String(k === i));
        });
        habilita(t);
      };
      caixa.appendChild(b);
    });

    /* A confiança só é pedida no diagnóstico: é lá que ela decide se o erro
     * vira lacuna ou hipótese de crença. No treino ela não roteia nada, e
     * pedir de novo a cada item cobraria duas decisões por tela. */
    $("atv-confianca-bloco").classList.toggle("oculto", !t.pede_confianca);
    var conf = $("atv-confianca");
    conf.innerHTML = "";
    if (t.pede_confianca) {
      ["chutei", "acho que sei", "tenho certeza"].forEach(function (nome) {
        var b = document.createElement("button");
        b.className = "conf";
        b.type = "button";
        b.textContent = nome;
        b.setAttribute("aria-pressed", "false");
        b.onclick = function () {
          S.confianca = nome;
          Array.prototype.forEach.call(conf.children, function (x) {
            x.setAttribute("aria-pressed", String(x === b));
          });
          habilita(t);
        };
        conf.appendChild(b);
      });
    }

    $("btn-responder").disabled = true;
    $("btn-responder").onclick = function () {
      $("btn-responder").disabled = true;
      var escolhida = t.opcoes[S.escolha].texto;
      responde({ escolha: S.escolha, confianca: S.confianca || "", ms: decorrido() },
               { texto: escolhida, fase: t.fase });
    };
    mostra("atividade");
  }

  function habilita(t) {
    $("btn-responder").disabled =
      S.escolha === null || (t.pede_confianca && !S.confianca);
  }

  function rotuloFormato(f) {
    return { reconhecer: "reconhecer o conceito", achar_erro: "achar o erro",
             comparar: "comparar casos", prever: "prever o resultado" }[f] || f;
  }

  /* -------------------------------------------------- retorno imediato */

  /* O retorno é imediato — menos quando o sistema levantou hipótese de
   * crença. Aí ele é NEUTRO de propósito: explicar aqui tornaria a
   * refutação uma repetição, e não daria para saber qual das duas coisas
   * mudou a resposta do aluno. Quem decide isso é o servidor, em
   * `veredito`. */
  function mostraRetorno(j, contexto) {
    // A trilha do topo descreve a tela que está no ar. Sem isto ela ficava
    // congelada no passo anterior enquanto o retorno estava visível.
    $("trilha").textContent = contexto.fase === "treino" ? "Treinando" : "Praticando";
    var v = $("ret-veredito");
    if (j.veredito === "crenca") {
      v.textContent = "Vamos olhar isso com calma";
      v.className = "veredito neutro";
      $("ret-texto").textContent =
        "Sua resposta não foi aleatória: ela segue de uma ideia. Vamos" +
        " examinar de onde ela vem, passo a passo.";
    } else if (j.veredito === "certa") {
      v.textContent = "Isso mesmo";
      v.className = "veredito certo";
      $("ret-texto").textContent = contexto.texto;
    } else {
      v.textContent = "Ainda não";
      v.className = "veredito errado";
      $("ret-texto").textContent =
        "Olhe de novo com calma — a próxima pergunta volta ao mesmo ponto" +
        " de outro jeito.";
    }
    $("btn-retorno").onclick = function () { aplica(S.pendente); };
    mostra("retorno");
  }

  /* -------------------------------------------------------- refutação */

  function telaRefutacao(t) {
    $("trilha").textContent = "Refutando · passo " + t.passo + " de " + t.total;
    $("ref-passo").textContent = "Premissa " + t.no;
    $("ref-texto").textContent = t.texto;
    var temContraste = !!t.contradiz;
    $("ref-contraste").classList.toggle("oculto", !temContraste);
    if (temContraste) {
      $("ref-crenca").textContent = t.contradiz;
      $("ref-certo").textContent = t.texto;
    }
    $("btn-refutacao").onclick = function () { responde({}); };
    mostra("refutacao");
  }

  /* -------------------------------------------------------------- mapa */

  function telaMapa(t) {
    $("trilha").textContent = "Unidade concluída";
    var caixa = $("mapa");
    caixa.innerHTML = "";
    t.nos.forEach(function (n) {
      var div = document.createElement("div");
      var classe = n.estado === "confirmado"
        ? (n.via_treino ? "treino" : "confirmado")
        : (n.estado === "em_aberto" ? "aberto" : "");
      div.className = "premissa " + classe;
      var id = document.createElement("span");
      id.className = "id";
      id.textContent = n.no;
      var corpo = document.createElement("div");
      var frase = document.createElement("p");
      frase.className = "frase";
      frase.textContent = n.texto;
      corpo.appendChild(frase);
      var nota = notaDe(n);
      if (nota) {
        var p = document.createElement("p");
        p.className = "nota";
        p.textContent = nota;
        corpo.appendChild(p);
      }
      div.appendChild(id);
      div.appendChild(corpo);
      caixa.appendChild(div);
    });
    mostra("mapa");
  }

  function notaDe(n) {
    if (n.estado === "confirmado" && n.via_treino) {
      return "confirmada depois de " + n.tentativas + " tentativa(s) de treino";
    }
    if (n.estado === "em_aberto") {
      return "ficou em aberto: o treino não fechou a sequência";
    }
    if (n.estado === "confirmado") return "confirmada de primeira";
    return "";
  }

  /* ------------------------------------------------------------ enviar */

  async function responde(corpo, contexto) {
    var j = await api("/sessoes/" + S.sessao + "/responder", corpo);
    if (contexto) {
      S.pendente = j;
      return mostraRetorno(j, contexto);
    }
    aplica(j);
  }

  /* ------------------------------------------------------------ início */

  api("/sessoes").then(aplica).catch(function (e) {
    document.body.innerHTML =
      '<p style="padding:24px">Não consegui falar com o servidor: ' + e.message + "</p>";
  });
})();
