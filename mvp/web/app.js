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
  var TELAS = ["frase", "ensino", "atividade", "razao", "confianca",
             "retorno", "validacao", "refutacao", "descida", "descida-fim",
             "evidencia", "mapa"];

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

  /* O codigo do participante vem da URL: ?codigo=P07. Fica fora da tela
   * de proposito — quem responde nao precisa ver, e um campo a mais na
   * abertura e uma pergunta a mais antes da pergunta que importa. Quem
   * abre a pagina com o codigo e o pesquisador, pelo scripts/ensaio.sh. */
  function codigoDaURL() {
    var m = /[?&]codigo=([^&]+)/.exec(window.location.search);
    return m ? decodeURIComponent(m[1]) : "";
  }

  /* ------------------------------------------------------------- grafo */

  /* Desenhado a cada resposta, com o estado que o servidor manda. Os nos
   * observaveis ficam na linha de cima; a conclusao, embaixo, ligada a
   * todos eles. A aresta acende quando as duas pontas estao de pe. */
  var NS = "http://www.w3.org/2000/svg";

  function el(nome, atributos, texto) {
    var n = document.createElementNS(NS, nome);
    Object.keys(atributos || {}).forEach(function (k) {
      if (atributos[k] !== null) n.setAttribute(k, atributos[k]);
    });
    if (texto !== undefined) n.textContent = texto;
    return n;
  }

  function desenhaGrafo(g) {
    if (!g || !g.nos || !g.nos.length) return;
    var svg = $("grafo-svg");
    svg.innerHTML = "";
    $("grafo").hidden = false;

    var base = g.nos.filter(function (n) { return n.tipo === "observavel"; });
    var topo = g.nos.filter(function (n) { return n.tipo !== "observavel"; });
    var L = 92, A = 34, gap = 16, y0 = 14, y1 = 96;
    var larguraBase = base.length * L + (base.length - 1) * gap;
    var x0 = (520 - larguraBase) / 2;
    var pos = {};

    base.forEach(function (n, i) { pos[n.no] = { x: x0 + i * (L + gap), y: y0 }; });
    topo.forEach(function (n, i) {
      pos[n.no] = { x: (520 - L) / 2 + i * (L + gap), y: y1 };
    });

    /* arestas primeiro, para ficarem atras das caixas */
    g.nos.forEach(function (n) {
      (n.suporte || []).forEach(function (s) {
        if (!pos[s] || !pos[n.no]) return;
        var de = pos[s], para = pos[n.no];
        var viva = sustentado(porId(g, s)) && sustentado(n);
        svg.appendChild(el("path", {
          "class": "g-aresta" + (viva ? " viva" : ""),
          d: "M" + (de.x + L / 2) + "," + (de.y + A) +
             " C" + (de.x + L / 2) + "," + (de.y + A + 24) +
             " " + (para.x + L / 2) + "," + (para.y - 24) +
             " " + (para.x + L / 2) + "," + para.y
        }));
      });
    });

    g.nos.forEach(function (n) {
      var p = pos[n.no];
      if (!p) return;
      var classe = "g-no " + classeDe(n) + (n.no === g.foco ? " foco" : "");
      svg.appendChild(el("rect", {
        "class": classe, x: p.x, y: p.y, width: L, height: A, rx: 8
      }));
      svg.appendChild(el("text", {
        "class": "g-rot", x: p.x + L / 2, y: p.y + A / 2
      }, n.no + rotuloEstado(n)));
    });

    $("grafo-nota").textContent = notaGrafo(g);
  }

  function porId(g, id) {
    return g.nos.filter(function (n) { return n.no === id; })[0];
  }

  function sustentado(n) { return !!n && n.estado === "confirmado"; }

  function classeDe(n) {
    if (n.estado === "confirmado") return n.via_treino ? "treino" : "confirmado";
    return n.estado;
  }

  /* Simbolo antes de cor: daltonismo e impressao em preto e branco nao
   * podem apagar a diferenca entre "de pe" e "crenca ativa". */
  function rotuloEstado(n) {
    if (n.estado === "confirmado") return " ✓";
    if (n.estado === "fragil") return " ✓?";
    if (n.estado === "falso_positivo") return " !";
    if (n.estado === "refutado") return " ✗";
    if (n.estado === "lacuna") return " ?";
    if (n.estado === "em_treino") return " " + n.streak + "/2";
    if (n.estado === "em_aberto") return " —";
    /* Construida: a lacuna foi tratada e a pessoa acertou o degrau de
     * entrada. Nao e verde — a CS-5 continua exigindo duas superficies. */
    if (n.estado === "construido") return " ↑";
    /* Nao medida: a unidade acabou sem nenhuma resposta atribuida a esta
     * premissa. Nao e o mesmo que "em aberto", onde houve treino e ele nao
     * fechou — e nao pode ficar com a mesma cara de quem nem comecou. */
    if (n.estado === "nao_medido") return " ?!";
    return "";
  }

  var NOME_ESTADO = {
    confirmado: "premissa confirmada",
    fragil: "de pé, mas numa superfície só",
    falso_positivo: "acertou por outro motivo",
    refutado: "crença detectada",
    lacuna: "disse que não sabe",
    em_treino: "em treino",
    em_aberto: "ficou em aberto",
    construido: "construída agora, ainda não demonstrada",
    nao_medido: "esta unidade não chegou a medir"
  };

  /* O caso cruzado precisa de texto: um no pode ficar vermelho sem a pessoa
   * ter respondido NADA sobre ele — porque ela explicou outra pergunta por
   * uma crenca que nega este no. Sem esta frase, o grafo parece um bug. */
  function porqueDe(n) {
    if (n.origem_crenca && n.crenca_afirma) {
      return "Você explicou a pergunta de " + n.origem_crenca + " por: “" +
             n.crenca_afirma + "” — e isso é uma afirmação sobre " + n.no + ".";
    }
    if (n.estado === "falso_positivo") {
      return "A resposta estava certa, mas por outro motivo. Esta premissa" +
             " volta de outro jeito.";
    }
    if (n.estado === "fragil") {
      return "Falta ver a mesma ideia noutra forma de pergunta.";
    }
    return "";
  }

  function notaGrafo(g) {
    var prontos = g.nos.filter(sustentado).length;
    var treinando = g.nos.filter(function (n) { return n.estado === "em_treino"; })[0];
    if (treinando) {
      return "Treinando " + treinando.no + ": " + treinando.streak +
             " de 2 acertos seguidos para confirmar.";
    }
    /* O cruzado manda na nota: e a informacao mais surpreendente da tela. */
    var cruzado = g.nos.filter(function (n) { return !!n.origem_crenca; })[0];
    if (cruzado) {
      return "A ideia que você usou na pergunta de " + cruzado.origem_crenca +
             " é uma afirmação sobre " + cruzado.no + " — é lá que ela ficou" +
             " registrada.";
    }
    return prontos + " de " + g.nos.length + " premissas de pé.";
  }

  /* ---------------------------------------------------------- despacho */

  function aplica(j) {
    S.sessao = j.sessao;
    S.tela = j.tela;
    desenhaGrafo(j.grafo);
    var t = j.tela;
    if (t.tipo === "frase") return telaFrase(t);
    if (t.tipo === "ensino") return telaEnsino(t);
    if (t.tipo === "atividade") return telaAtividade(t);
    if (t.tipo === "razao") return telaRazao(t);
    if (t.tipo === "confianca") return telaConfianca(t);
    if (t.tipo === "validacao") return telaValidacao(t);
    if (t.tipo === "refutacao") return telaRefutacao(t);
    if (t.tipo === "descida") return telaDescida(t);
    if (t.tipo === "descida_fim") return telaDescidaFim(t);
    if (t.tipo === "evidencia") return telaEvidencia(t);
    if (t.tipo === "mapa") return telaMapa(t);
  }

  /* -------------------------------------------------------- teach-back */

  /* A mesma pergunta duas vezes. Ninguem corrige esta frase: o sistema
   * guarda e devolve, e quem classifica e o pesquisador, com codebook.
   * No fim, a de antes NAO aparece aqui — escrever olhando a propria
   * frase antiga e copia-la ou corrigi-la, nao reformula-la. */
  function telaFrase(t) {
    var fim = t.momento === "fim";
    $("trilha").textContent = fim ? "Para fechar" : "Antes de começar";
    $("frase-etiqueta").textContent = fim ? "A mesma pergunta do começo"
                                          : "Antes de começar";
    $("frase-pergunta").textContent = "Em uma frase, com suas palavras: " +
      t.texto + "?";
    $("frase-aviso").textContent = t.aviso || "";
    var caixa = $("frase-texto");
    caixa.value = "";
    caixa.placeholder = fim ? "Escreva de novo, sem olhar a de antes."
                            : "Escreva como você explicaria para alguém.";
    /* O limite dito antes de a pessoa esbarrar nele. O maxlength ja
     * impede de passar; sem o contador, ela digita e o texto simplesmente
     * para de aparecer, o que parece defeito. */
    var limite = caixa.getAttribute("maxlength") | 0;
    var contagem = $("frase-contagem");
    function conta() {
      var usados = caixa.value.length;
      var sobra = limite - usados;
      contagem.textContent = sobra > 200 ? ""
        : sobra + " caracteres restantes de " + limite;
      contagem.classList.toggle("perto", sobra <= 200);
    }
    caixa.oninput = conta;
    conta();

    $("btn-frase").onclick = function () {
      responde({ texto: caixa.value.slice(0, limite), ms: decorrido() });
    };
    var pular = $("btn-frase-pular");
    pular.textContent = fim ? "Prefiro não escrever" : "Não sei dizer ainda";
    pular.onclick = function () { responde({ texto: "", ms: decorrido() }); };
    mostra("frase");
    caixa.focus();
  }

  /* ------------------------------------------------------------ ensino */

  function telaEnsino(t) {
    $("trilha").textContent = "Aprendendo";
    /* A MESMA tela serve a dois momentos. Na abertura e a sequencia de
     * ideias; depois de um "nao sei" ela volta para UM no, e tem de dizer
     * por que apareceu — senao parece que o sistema se repetiu. */
    var daLacuna = t.motivo === "lacuna";
    var primeiraVez = t.motivo === "primeiro_contato";
    var etiqueta = "Ideia " + t.indice + " de " + t.total;
    if (daLacuna) etiqueta = "Vamos construir esta ideia";
    if (primeiraVez) etiqueta = "Antes da próxima pergunta";
    $("ensino-passo").textContent = etiqueta;
    /* O resgate vai junto nos dois casos em que a tela volta para UM no:
     * e a analogia daquela premissa, e a abertura nao a tem. */
    $("ensino-resgate").textContent = t.resgate || "";
    $("ensino-resgate").hidden = !(daLacuna || primeiraVez) || !t.resgate;
    $("btn-ensino").textContent = daLacuna || primeiraVez
      ? "Entendi, quero tentar" : "Entendi";
    $("ensino-texto").textContent = t.texto;
    // A frase, o código e o desenho: a mesma ideia em três registros.
    $("ensino-codigo").textContent = t.codigo || "";
    $("ensino-codigo").hidden = !t.codigo;
    Figuras.dentro($("ensino-figura"), t.no);

    /* A AMPLIACAO EXPLICATIVA, depois do exemplo e do desenho.
     *
     * A ordem e deliberada: o codigo demonstra, o desenho ancora, e este
     * texto interpreta o que acabou de ser mostrado. Cartao sem
     * ampliacao nao desenha a secao — doze dos treze topicos nao tem
     * nenhuma, e uma caixa vazia parece defeito.
     *
     * Paragrafo por paragrafo, e nao um bloco so: a ampliacao do B3 tem
     * quatro partes (ler, escrever, e a distincao entre as tres
     * expressoes), e espremidas num paragrafo elas se perdem. */
    var caixa = $("ensino-interpretacao");
    caixa.textContent = "";
    var partes = (t.interpretacao || "").split(/\n\s*\n/)
                   .map(function (s) { return s.trim(); })
                   .filter(Boolean);
    partes.forEach(function (s) {
      var par = document.createElement("p");
      par.textContent = s;
      caixa.appendChild(par);
    });
    caixa.classList.toggle("oculto", partes.length === 0);

    $("btn-ensino").onclick = function () { responde({}); };
    mostra("ensino");
  }

  /* --------------------------------------------------------- atividade */

  function telaAtividade(t) {
    S.escolha = null;
    S.confianca = null;
    // `fase` vem do motor em maiúsculas (TREINO / DIAGNOSTICO): é o mesmo
    // nome que o log grava, e comparar com minúsculas quebrava em silêncio.
    var emTreino = t.fase === "TREINO";
    $("trilha").textContent = emTreino
      ? "Treinando · premissa " + t.no
      : "Praticando";
    $("atv-etiqueta").textContent = emTreino
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

    botaoNaoSei(caixa, "Não sei", function () {
      $("btn-responder").disabled = true;
      responde({ nao_sei: true, ms: decorrido() },
               { texto: "Você disse que não sabe", fase: t.fase });
    });

    $("btn-responder").disabled = true;
    $("btn-responder").onclick = function () {
      $("btn-responder").disabled = true;
      var escolhida = t.opcoes[S.escolha].texto;
      responde({ escolha: S.escolha, ms: decorrido() },
               { texto: escolhida, fase: t.fase });
    };
    mostra("atividade");
  }

  /* --------------------------------------------------- camada 2: razao */

  /* A resposta ja esta trancada no servidor: esta tela nao tem como
   * mudar a camada 1, e o cadeado diz isso. As razoes vem prontas do
   * motor, montadas do grafo — o cliente nao sabe qual e a certa. */
  function telaRazao(t) {
    S.escolha = null;
    $("trilha").textContent = "Praticando · por quê";
    $("raz-trancada").textContent = t.trancada || "";
    $("raz-pergunta").textContent = t.texto;

    var caixa = $("raz-opcoes");
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
        $("btn-razao").disabled = false;
      };
      caixa.appendChild(b);
    });

    botaoNaoSei(caixa, "Não sei dizer por quê", function () {
      $("btn-razao").disabled = true;
      responde({ nao_sei: true, ms: decorrido() },
               { texto: "Você disse que não sabe explicar", fase: "DIAGNOSTICO" });
    });

    $("btn-razao").disabled = true;
    $("btn-razao").onclick = function () {
      $("btn-razao").disabled = true;
      responde({ escolha: S.escolha, ms: decorrido() });
    };
    mostra("razao");
  }

  /* ----------------------------------------------- camada 3: confianca */

  /* Tela propria, e nao no pe da tela da razao: a pergunta e sobre as DUAS
   * escolhas juntas, e declarar confianca antes de ver o par formado mede
   * outra coisa. Vale no treino tambem — o criterio fala em "sem queda de
   * confianca", e queda exige duas medidas. */
  function telaConfianca(t) {
    S.confianca = null;
    $("trilha").textContent = "Praticando · confiança";
    $("conf-resposta").textContent = t.resposta || "";
    var temRazao = !!t.razao;
    $("conf-rotulo-razao").hidden = !temRazao;
    $("conf-razao").hidden = !temRazao;
    $("conf-razao").textContent = t.razao || "";
    $("conf-pergunta").textContent = t.texto;

    var caixa = $("conf-escala");
    caixa.innerHTML = "";
    t.escala.forEach(function (nome) {
      var b = document.createElement("button");
      b.className = "conf";
      b.type = "button";
      b.textContent = nome;
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () {
        S.confianca = nome;
        Array.prototype.forEach.call(caixa.children, function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        $("btn-confianca").disabled = false;
      };
      caixa.appendChild(b);
    });

    botaoNaoSei(caixa, "Não sei dizer", function () {
      $("btn-confianca").disabled = true;
      responde({ nao_sei: true, ms: decorrido() },
               { texto: t.resposta, fase: "DIAGNOSTICO" });
    });

    $("btn-confianca").disabled = true;
    $("btn-confianca").onclick = function () {
      $("btn-confianca").disabled = true;
      responde({ confianca: S.confianca, ms: decorrido() },
               { texto: t.resposta, fase: "DIAGNOSTICO" });
    };
    mostra("confianca");
  }

  /* "Nao sei" entra nas tres camadas. Responder por ela encerra o
   * episodio: quem nao sabe nao tem o que justificar nem convicção a
   * declarar, e a tabela ja decidiu que isso e lacuna. */
  function botaoNaoSei(caixa, texto, aoClicar) {
    var b = document.createElement("button");
    b.className = (caixa.id === "conf-escala" ? "conf nao-sei" : "opcao nao-sei");
    b.type = "button";
    b.textContent = texto;
    b.onclick = aoClicar;
    caixa.appendChild(b);
    return b;
  }

  function habilita(t) {
    $("btn-responder").disabled =
      S.escolha === null || (t.pede_confianca && !S.confianca);
  }

  function rotuloFormato(f) {
    return { reconhecer_conceito: "reconhecer o conceito",
             achar_o_erro: "achar o erro",
             comparar_casos: "comparar casos",
             prever_saida: "prever o resultado" }[f] || f;
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
    $("trilha").textContent = contexto.fase === "TREINO" ? "Treinando" : "Praticando";
    $("ret-contraste").classList.add("oculto");
    var v = $("ret-veredito");
    if (j.veredito === "crenca") {
      v.textContent = "Vamos olhar isso com calma";
      v.className = "veredito neutro";
      $("ret-texto").textContent =
        "Sua resposta não foi aleatória: ela segue de uma ideia. Vamos" +
        " examinar de onde ela vem, passo a passo.";
    } else if (j.veredito === "falso_positivo") {
      /* Decisao 13: contar. A resposta esta certa — dizer o contrario
       * seria mentira — mas a explicacao escolhida leva a outro lugar, e e
       * dela que o sistema vai cuidar. */
      v.textContent = "A resposta está certa.";
      v.className = "veredito neutro";
      $("ret-texto").textContent =
        "Mas a explicação que você escolheu leva a outro lugar — e é dela" +
        " que eu quero cuidar agora.";
      if (j.retorno) {
        $("ret-contraste").classList.remove("oculto");
        $("ret-par-crenca").classList.remove("oculto");
        $("ret-rotulo-crenca").textContent = "Você explicou por";
        $("ret-crenca").textContent = j.retorno.crenca;
        $("ret-rotulo-certo").textContent = "E isso contradiz";
        $("ret-certo").textContent = j.retorno.contradiz;
      }
    } else if (j.veredito === "lacuna") {
      v.textContent = "Você disse que não sabe";
      v.className = "veredito neutro";
      $("ret-texto").textContent =
        "Isso é informação, não erro: aqui não há nada para corrigir, há" +
        " algo para construir.";
    } else if (j.veredito === "certa") {
      v.textContent = "Isso mesmo";
      v.className = "veredito certo";
      $("ret-texto").textContent = contexto.texto;
    } else {
      v.textContent = "Ainda não";
      v.className = "veredito errado";
      /* O ERRO QUE EXPLICA. Os dois textos vem do dominio; a frase de
       * ligacao e do cliente e NAO varia com o conteudo — e por isso que
       * nao existe lugar por onde uma justificativa inventada entre.
       *
       * Sem `retorno` fica a fala antiga: e o diagnostico e o reteste, que
       * MEDEM, e onde o silencio e proposito e nao esquecimento. */
      if (j.retorno && j.retorno.premissa) {
        var temIdeia = Boolean(j.retorno.escolheu);
        $("ret-texto").textContent = !temIdeia
          ? "Olhe o que a premissa afirma — a próxima pergunta volta ao" +
            " mesmo ponto de outro jeito."
          : j.retorno.contradiz
            ? "A ideia que você marcou nega esta premissa: as duas não" +
              " podem valer juntas."
            : "A ideia que você marcou é sobre outro ponto do mapa. Esta" +
              " pergunta é sobre a premissa abaixo.";
        $("ret-contraste").classList.remove("oculto");
        /* Alternativa sem crenca catalogada: o sistema nao sabe por onde a
         * pessoa foi, e o par da ideia SAI da tela em vez de aparecer
         * vazio com rotulo afirmando que ela escolheu algo. */
        $("ret-par-crenca").classList.toggle("oculto", !temIdeia);
        $("ret-rotulo-crenca").textContent = "Você escolheu";
        $("ret-crenca").textContent = j.retorno.escolheu;
        $("ret-rotulo-certo").textContent = !temIdeia
          ? "A premissa diz"
          : j.retorno.contradiz ? "E isso contradiz" : "E a premissa diz";
        $("ret-certo").textContent = j.retorno.premissa;
      } else {
        $("ret-texto").textContent =
          "Olhe de novo com calma — a próxima pergunta volta ao mesmo" +
          " ponto de outro jeito.";
      }
    }
    $("btn-retorno").onclick = function () { aplica(S.pendente); };
    mostra("retorno");
  }

  /* -------------------------------------------------------- validação */

  /* Antes de refutar, reconhecer. A analogia é a mesma do começo ao fim do
   * tópico: uma consistente se lembra melhor do que uma por conceito. */
  function telaValidacao(t) {
    $("trilha").textContent = "Vamos com calma";
    $("val-crenca").textContent = t.crenca || "";
    Figuras.dentro($("val-figura"), t.no);
    $("val-analogia").textContent = t.texto;
    $("btn-validacao").onclick = function () { responde({}); };
    mostra("validacao");
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

      /* O QUE A CAIXA PODE AFIRMAR vem do motor, em `apoio`, e não daqui.
       *
       * O rótulo era fixo no HTML — "as premissas que você acabou de
       * confirmar levam a" — e em 46% das refutações não havia premissa
       * nenhuma: o nó de base não tem suporte, e o plano tem um passo só.
       * Alegar a condução sem conduzir é afirmar o mecanismo da tese em
       * vez de executá-lo.
       *
       * Três casos, três frases, e nenhuma delas inventa percurso:
       *   confirmada por resposta  -> "que você confirmou respondendo"
       *   só percorrida agora      -> "que você acabou de aceitar"
       *   nada                     -> a premissa entra sozinha, sem alegar
       */
      var apoio = t.apoio || [];
      var lista = $("ref-apoio");
      lista.textContent = "";
      lista.classList.toggle("oculto", apoio.length === 0);
      apoio.forEach(function (p) {
        var li = document.createElement("li");
        li.textContent = p.texto;
        if (p.confirmada) { li.className = "confirmada"; }
        lista.appendChild(li);
      });
      var confirmadas = apoio.some(function (p) { return p.confirmada; });
      $("ref-rotulo-apoio").textContent =
        apoio.length === 0 ? "Mas a premissa diz"
        : confirmadas ? "As premissas que você confirmou respondendo levam a"
        : "As premissas que você acabou de aceitar levam a";
    }

    /* A figura entra sempre; a reexplicação, só quando ele pediu. A mesma
     * premissa volta dita pela analogia — não é conteúdo novo, é outro
     * caminho para a mesma afirmação. */
    Figuras.dentro($("ref-figura"), t.no);
    var caixa = $("ref-reexplicacao");
    caixa.textContent = t.reexplicacao || "";
    caixa.classList.toggle("oculto", !t.reexplicacao);

    $("btn-refutacao").onclick = function () { responde({}); };
    var naoEntendi = $("btn-refutacao-nao");
    naoEntendi.hidden = !t.pode_repetir;
    naoEntendi.textContent = t.repeticoes ? "Ainda assim não entendi"
                                          : "Ainda não entendi";
    naoEntendi.onclick = function () { responde({ repetir: true }); };
    mostra("refutacao");
  }

  /* ----------------------------------------------- descida interrogativa */

  /* A INVERSAO que esta tela tem, e e unica no sistema: a alternativa que
   * faz a cadeia ANDAR e a FALSA — e a previsao da crenca. O cliente nao
   * sabe qual e qual, e e melhor assim: nao ha gabarito a destacar aqui,
   * nao ha certo e errado na tela, so a pergunta e as duas saidas. O que o
   * servidor mede e qual delas a pessoa escolhe, e em que degrau. */
  function telaDescida(t) {
    S.escolha = null;
    $("trilha").textContent = "Descendo · passo " + t.passo + " de " + t.total;
    $("des-passo").textContent = "Passo " + t.passo + " de " + t.total;
    $("des-crenca").textContent = t.crenca || "";
    $("des-pergunta").textContent = t.texto;

    /* No ultimo degrau a cadeia bate numa premissa. Se a pessoa confirmou
     * essa premissa nesta sessao, a tela diz isso — e e o ponto todo da
     * descida: a contradicao e entre duas coisas que ela mesma disse. Se
     * nao confirmou, a tela afirma a premissa sem atribui-la a ela. */
    var temColisao = !!t.premissa;
    $("des-colisao").classList.toggle("oculto", !temColisao);
    if (temColisao) {
      $("des-colisao-rotulo").textContent = t.voce_disse
        ? "Você confirmou, nesta sessão"
        : "Esta unidade afirma";
      $("des-premissa").textContent = t.premissa;
    }

    var caixa = $("des-opcoes");
    caixa.innerHTML = "";
    t.opcoes.forEach(function (texto, i) {
      var b = document.createElement("button");
      b.className = "opcao";
      b.type = "button";
      b.textContent = texto;
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () {
        S.escolha = i;
        Array.prototype.forEach.call(caixa.children, function (x, k) {
          x.setAttribute("aria-pressed", String(k === i));
        });
        $("btn-descida").disabled = false;
      };
      caixa.appendChild(b);
    });

    botaoNaoSei(caixa, "Não sei dizer", function () {
      $("btn-descida").disabled = true;
      responde({ nao_sei: true, ms: decorrido() });
    });

    $("btn-descida").disabled = true;
    $("btn-descida").onclick = function () {
      $("btn-descida").disabled = true;
      responde({ escolha: S.escolha, ms: decorrido() });
    };
    mostra("descida");
  }

  /* Ela recusou a consequencia: a descida acaba AQUI. Insistir depois
   * disto e argumentar com quem ja concordou. */
  function telaDescidaFim(t) {
    $("trilha").textContent = "Descendo · passo " + t.passo + " de " + t.total;
    $("fim-crenca").textContent = t.crenca || "";
    $("fim-resposta").textContent = t.voce_disse || "";
    $("fim-texto").textContent = t.texto;
    $("btn-descida-fim").onclick = function () { responde({}); };
    mostra("descida-fim");
  }

  /* Sustentou a crenca pelos degraus todos. O sistema para de perguntar e
   * mostra o fato — e `gravada` decide se houve terminal de verdade. Sem
   * saida gravada esta tela NAO desenha terminal: ela mostra o programa e
   * a garantia do padrao, e diz que ninguem rodou. Evidencia inventada e
   * pior que evidencia nenhuma. */
  function telaEvidencia(t) {
    $("trilha").textContent = "A evidência";
    $("evi-programa").textContent = t.programa || "";
    $("evi-comando").textContent = t.comando ? "$ " + t.comando : "";
    var saida = $("evi-saida");
    saida.textContent = t.gravada ? t.saida : "";
    saida.classList.toggle("oculto", !t.gravada);
    $("evi-afirmacao").textContent = t.texto;
    $("evi-garantia").textContent = t.garantia || "";
    $("evi-origem").textContent = t.gravada
      ? "Saída registrada em: " + t.onde
      : "Ninguém rodou este programa aqui, então não há terminal para" +
        " mostrar — o que está acima é o que a norma da linguagem obriga.";
    $("btn-evidencia").onclick = function () { responde({}); };
    mostra("evidencia");
  }

  /* -------------------------------------------------------------- mapa */

  function telaMapa(t) {
    $("trilha").textContent = "Unidade concluída";
    /* As duas frases so aparecem se houver pelo menos uma: quem preferiu
     * nao escrever nao precisa ver dois cartoes vazios. */
    var temPar = !!(t.frase_inicial || t.frase_final);
    $("mapa-par").classList.toggle("oculto", !temPar);
    if (temPar) {
      $("mapa-antes").textContent = t.frase_inicial ||
        "(você preferiu não escrever)";
      $("mapa-depois").textContent = t.frase_final ||
        "(você preferiu não escrever)";
    }
    var caixa = $("mapa");
    caixa.innerHTML = "";
    t.nos.forEach(function (n) {
      var div = document.createElement("div");
      var classe = n.estado === "confirmado"
        ? (n.via_treino ? "treino" : "confirmado")
        : (n.estado === "em_aberto" ? "aberto" : n.estado);
      div.className = "premissa " + classe;
      var id = document.createElement("span");
      id.className = "id";
      id.textContent = n.no;
      var corpo = document.createElement("div");
      var frase = document.createElement("p");
      frase.className = "frase";
      frase.textContent = n.texto;
      corpo.appendChild(frase);
      /* O simbolo e o nome do estado andam juntos: quem imprime o mapa em
       * preto e branco continua lendo o que aconteceu. */
      var marca = document.createElement("p");
      marca.className = "marca";
      marca.textContent = rotuloEstado(n).trim() + " " + (NOME_ESTADO[n.estado] || "");
      corpo.appendChild(marca);
      var nota = notaDe(n);
      /* A troca de superficie: a mesma ideia perguntada com outro nome,
       * outro tamanho, outro tipo. E o que separa generalizar de ter
       * decorado aquela pergunta, e por isso vem depois do estado, nao
       * no lugar dele. */
      if (n.generalizou) {
        /* Sem antecedente, o "e" fica solto: no fragil ou refutado a
         * notaDe devolve vazio, e o mapa imprimia a frase comecando por
         * conjuncao. */
        nota = nota ? nota + ", e sustentou a troca de superfície"
                    : "sustentou a troca de superfície";
      }
      if (nota) {
        var p = document.createElement("p");
        p.className = "nota";
        p.textContent = nota;
        corpo.appendChild(p);
      }
      var porque = porqueDe(n);
      if (porque) {
        var q = document.createElement("p");
        q.className = "porque";
        q.textContent = porque;
        corpo.appendChild(q);
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
    if (n.estado === "confirmado") {
      return "confirmada em " + n.superficies + " formas de pergunta";
    }
    if (n.estado === "lacuna") {
      return "nada para corrigir aqui: há algo para construir";
    }
    return "";
  }

  /* ------------------------------------------------------------ enviar */

  async function responde(corpo, contexto) {
    var j = await api("/sessoes/" + S.sessao + "/responder", corpo);
    /* Sem veredito nao ha o que devolver ainda: e o caso da camada 1 de
     * uma diagnostica, que agora tranca e chama a tela da razao. O
     * retorno imediato so faz sentido quando o episodio fechou. */
    if (contexto && j.veredito) {
      S.pendente = j;
      desenhaGrafo(j.grafo);     // o grafo acompanha já no retorno
      return mostraRetorno(j, contexto);
    }
    aplica(j);
  }

  /* ------------------------------------------------------------ início */

  /* Recomeçar abre uma SESSÃO NOVA, não desfaz a atual: o percurso que
   * acabou de acontecer continua inteiro no log, e é isso que permite
   * rodar o mesmo caso várias vezes e comparar depois. */
  function recomeca() {
    var b = $("btn-recomecar");
    b.disabled = true;
    /* Recomecar NAO reusa o codigo: ele ja tem sessao, e o servidor
     * recusaria. A sessao nova sai anonima, e o log liga as duas pelo
     * horario. */
    api("/sessoes").then(function (j) {
      b.disabled = false;
      aplica(j);
    }).catch(function (e) {
      b.disabled = false;
      erro(e);
    });
  }

  function erro(e) {
    document.body.innerHTML =
      '<p style="padding:24px">Não consegui falar com o servidor: ' + e.message + "</p>";
  }

  $("btn-recomecar").onclick = recomeca;

  /* O titulo da aba vem do dominio carregado, nao do HTML: com dois
   * topicos, um titulo fixo mente — a aba dizia "declaracao de variaveis"
   * numa sessao de ponteiros. */
  fetch("/saude").then(function (r) { return r.json(); }).then(function (s) {
    if (s && s.titulo) document.title = "Structura — " + s.titulo;
    /* As figuras sao por topico: id de no se repete entre topicos. */
    if (s && s.topico) Figuras.topico(s.topico);
  }).catch(function () { /* o titulo e enfeite; falhar nele nao para nada */ });

  api("/sessoes", { codigo: codigoDaURL() }).then(aplica).catch(function (e) {
    document.body.innerHTML =
      '<p style="padding:24px">Não consegui falar com o servidor: ' + e.message + "</p>";
  });
})();
