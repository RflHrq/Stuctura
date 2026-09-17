/* Cliente do Structura.
 *
 * NENHUMA REGRA DE FLUXO AQUI (§9). O servidor devolve `next_action` e este
 * arquivo apenas renderiza. Não existe neste código:
 *
 *   - decisão de qual CIU vem depois
 *   - avaliação de acerto ou erro
 *   - escolha entre socrático e direto
 *   - qualquer texto de domínio
 *
 * É o que impede o braço de controle de divergir do socrático por acidente
 * de implementação no front, e o que mantém o determinismo do motor
 * verificável: a interface não tem estado próprio a divergir.
 *
 * A única diferença visível entre os braços é o VERBO do botão — "Sim,
 * confirmo" contra "Entendi, continuar" —, porque o servidor manda `ask`
 * num caso e `explain` no outro. Cores, tipografia e espaçamento são os
 * mesmos (§8.1).
 */

(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var TELAS = ["abertura", "intro", "ciu", "diagrama", "passo", "conclusao", "fim"];

  var S = {
    sessao: null,
    acao: null,
    escala: [],
    prior: null,        // experiência prévia declarada (§4.3)
    escolha: null,       // índice da alternativa, texto, ordem ou rótulo
    confianca: null,
    inicio: 0,           // marca de tempo do início da tela atual
    braco: null,
    ultimoTotal: 0,      // para detectar reinício do contador entre rodadas
    trilha: []           // passos já vistos na rodada corrente
  };

  /* ------------------------------------------------------------- utilidades */

  function mostra(nome) {
    TELAS.forEach(function (t) {
      $("tela-" + t).classList.toggle("hidden", t !== nome);
    });
    S.inicio = performance.now();
  }

  function decorrido() {
    return Math.max(0, Math.round(performance.now() - S.inicio));
  }

  async function api(metodo, rota, corpo) {
    var r = await fetch(rota, {
      method: metodo,
      headers: corpo ? { "Content-Type": "application/json" } : {},
      body: corpo ? JSON.stringify(corpo) : undefined
    });
    var j = null;
    try { j = await r.json(); } catch (e) { /* corpo vazio */ }
    if (!r.ok) {
      var erro = new Error((j && j.detail) || ("HTTP " + r.status));
      erro.status = r.status;
      erro.corpo = j;
      throw erro;
    }
    return j;
  }

  function erroEm(id, msg) {
    var e = $(id);
    e.textContent = msg;
    e.classList.remove("hidden");
  }

  function limpaErro(id) { $(id).classList.add("hidden"); }

  /* --------------------------------------------------------------- abertura */

  function iniciaAbertura() {
    var salvo = null;
    try { salvo = localStorage.getItem("structura.codigo"); } catch (e) {}
    if (salvo) $("codigo").value = salvo;

    $("codigo").addEventListener("input", habilitaComecar);
    $("consent").addEventListener("change", habilitaComecar);
    habilitaComecar();

    // O braço é escolha do PESQUISADOR, não do participante: fica atrás de
    // um clique para não sugerir ao aluno que existem duas versões.
    $("btn-braco").onclick = function () {
      $("bloco-braco").classList.toggle("hidden");
    };
    Array.prototype.forEach.call($("braco-opts").children, function (b) {
      b.onclick = function () {
        S.braco = b.dataset.arm;
        Array.prototype.forEach.call($("braco-opts").children, function (o) {
          o.setAttribute("aria-pressed", String(o === b));
        });
        habilitaComecar();
      };
    });

    $("btn-comecar").onclick = comecar;
    $("codigo").addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !$("btn-comecar").disabled) comecar();
    });
  }

  /* Nada começa sem código, experiência declarada, consentimento marcado
   * E braço escolhido. Os quatro são dados que a análise precisa e que
   * ninguém pode assumir por outro: alocação é do pesquisador,
   * consentimento é do participante, experiência é a estratificação. */
  function habilitaComecar() {
    $("btn-comecar").disabled = !(
      $("codigo").value.trim() && S.prior && S.braco && $("consent").checked
    );
  }

  function montaAbertura(h) {
    $("consent-texto").textContent = h.consent_text || "";
    var caixa = $("prior-opts");
    caixa.innerHTML = "";
    (h.prior_c_options || []).forEach(function (op) {
      var b = document.createElement("button");
      b.className = "conf-opt";
      b.textContent = op;
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () {
        S.prior = op;
        Array.prototype.forEach.call(caixa.children, function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        habilitaComecar();
      };
      caixa.appendChild(b);
    });
  }

  async function comecar() {
    limpaErro("erro-abertura");
    var codigo = $("codigo").value.trim();
    $("btn-comecar").disabled = true;
    try {
      // Sem braço, o servidor recusa: a alocação é deliberada, nunca um
      // padrão silencioso. O botão já garante que os quatro campos
      // existem; mandar mesmo assim o que o usuário escolheu, sem
      // fallback, é o que impede um default de virar dado.
      var j = await api("POST", "/sessions", {
        participant: codigo,
        arm: S.braco,
        prior_c: S.prior,
        consented: $("consent").checked
      });
      try { localStorage.setItem("structura.codigo", codigo); } catch (e) {}
      aplica(j);
    } catch (e) {
      erroEm("erro-abertura", e.message);
      $("btn-comecar").disabled = false;
    }
  }

  /* ------------------------------------------------------------- despacho */

  function aplica(j) {
    S.sessao = j.session_id;
    S.acao = j.next_action;
    $("meta").innerHTML =
      "participante <b>" + j.session_id.slice(0, 8) + "</b> · " +
      (j.kc ? "KC <b>" + j.kc + "</b>" : "—");
    $("rodape").textContent =
      "Sessão em andamento. Se a aba fechar, digite o mesmo código para voltar.";

    var k = S.acao.kind;
    if (k === "intro") return telaIntro();
    if (k === "ciu") return telaCiu();
    if (k === "diagram") return telaDiagrama();
    if (k === "ask" || k === "explain") return telaPasso();
    if (k === "conclude") return telaConclusao(j);
    if (k === "done") return telaFim(j);
    erroEm("erro-abertura", "ação desconhecida: " + k);
  }

  /* ------------------------------------------------------------ introdução */

  /* A introdução estabelece VOCABULÁRIO — endereço, caixa, região — e para
   * antes das conclusões dos KCs que o piloto mede. Se ela ensinasse a
   * resposta da primeira atividade, o diagnóstico deixaria de medir a
   * crença prévia do aluno. `tools/validate.py` confere isso no domínio.
   *
   * É idêntica nos dois braços: acontece antes de eles divergirem. */
  function telaIntro() {
    var a = S.acao;
    $("intro-titulo").textContent = a.title || "";
    $("intro-lead").innerHTML = a.lead || "";

    var prog = $("intro-contagem");
    prog.textContent = a.index + " de " + a.total;
    var dots = $("intro-dots");
    dots.innerHTML = "";
    for (var i = 1; i <= a.total; i++) {
      var d = document.createElement("i");
      d.className = i < a.index ? "done" : (i === a.index ? "on" : "");
      dots.appendChild(d);
    }

    var fig = $("intro-fig");
    fig.innerHTML = "";
    var desenho = Fig.render(a.figure);
    if (desenho) fig.appendChild(desenho);

    var corpo = $("intro-corpo");
    corpo.innerHTML = "";
    (a.body || []).forEach(function (t) {
      var p = document.createElement("p");
      p.innerHTML = t;          // os moldes usam <b> para o que importa reter
      corpo.appendChild(p);
    });

    // Voltar é local: relê um cartão sem gravar evento nem mover a sessão.
    // O servidor continua sendo o único ponto que decide o fluxo (§9).
    var voltar = $("btn-intro-voltar");
    voltar.classList.toggle("hidden", a.index <= 1);
    voltar.onclick = function () {
      if (S.introCache && S.introCache[a.index - 2]) {
        S.acao = S.introCache[a.index - 2];
        telaIntro();
      }
    };
    S.introCache = S.introCache || [];
    S.introCache[a.index - 1] = a;

    var b = $("btn-intro");
    b.textContent = a.index >= a.total ? "Começar as atividades" : "Continuar";
    b.disabled = false;
    b.onclick = async function () {
      b.disabled = true;
      try {
        aplica(await api("POST", "/sessions/" + S.sessao + "/ack",
                         { elapsed_ms: decorrido() }));
      } catch (e) {
        if (e.status === 409) return realinha();
        b.disabled = false;
      }
    };
    mostra("intro");
  }

  /* ------------------------------------------------------------------ CIU */

  function telaCiu() {
    var a = S.acao;
    S.escolha = null;
    S.confianca = null;
    limpaErro("erro-ciu");

    $("ciu-fase").textContent =
      a.phase === "variation" ? "Atividade de variação" : "Atividade";

    // O prompt vem inteiro do YAML e é apresentado inteiro, em bloco
    // monoespaçado. O motor NÃO separa código de enunciado: a ordem varia
    // entre itens, e um corte automático erraria em algum — renderizando
    // código como prosa na frente do participante.
    $("ciu-code").textContent = a.prompt || "";
    $("ciu-code").classList.toggle("hidden", !a.prompt);
    $("ciu-pergunta").textContent = "";

    var corpo = $("ciu-corpo");
    corpo.innerHTML = "";
    if (a.options) corpoOpcoes(corpo, a.options);
    else if (a.paths) corpoCaminhos(corpo, a.paths);
    else if (a.steps) corpoOrdenacao(corpo, a.steps);
    else corpoTexto(corpo);

    montaConfianca();
    $("btn-responder").onclick = enviaResposta;
    atualizaBotao();
    mostra("ciu");
  }

  function corpoOpcoes(corpo, opcoes) {
    var lista = document.createElement("div");
    lista.className = "opts";
    opcoes.forEach(function (o, i) {
      var b = document.createElement("button");
      b.className = "opt";
      b.textContent = o.text;
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () {
        S.escolha = i;
        Array.prototype.forEach.call(lista.children, function (x, k) {
          x.setAttribute("aria-pressed", String(k === i));
        });
        atualizaBotao();
      };
      lista.appendChild(b);
    });
    corpo.appendChild(lista);
  }

  /* `path_choice` NÃO é arrastar-e-soltar. Os caminhos têm passos
   * diferentes entre si, não são permutação um do outro: renderizar como
   * reordenação tornaria o distrator inatingível — o aluno nunca
   * conseguiria produzir a sequência que revela a crença. */
  function corpoCaminhos(corpo, caminhos) {
    var lista = document.createElement("div");
    lista.className = "path-list";
    caminhos.forEach(function (c) {
      var b = document.createElement("button");
      b.className = "path-card";
      b.setAttribute("aria-pressed", "false");
      var t = document.createElement("div");
      t.className = "plabel";
      t.textContent = "Caminho " + c.label;
      b.appendChild(t);
      var ol = document.createElement("ol");
      c.steps.forEach(function (p) {
        var li = document.createElement("li");
        li.textContent = p;
        ol.appendChild(li);
      });
      b.appendChild(ol);
      b.onclick = function () {
        S.escolha = c.label;
        Array.prototype.forEach.call(lista.children, function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        atualizaBotao();
      };
      lista.appendChild(b);
    });
    corpo.appendChild(lista);
  }

  /* `parsons` é reordenação dos MESMOS passos. Setas em vez de arrastar:
   * funciona no teclado, não depende de precisão do mouse e não some em
   * tela pequena. Começa embaralhado de forma fixa (rotação de um), para
   * não introduzir aleatoriedade numa sessão que precisa ser determinística. */
  function corpoOrdenacao(corpo, passos) {
    var ordem = passos.slice(1).concat(passos.slice(0, 1));
    var ul = document.createElement("ul");
    ul.className = "order-list";

    function desenha() {
      ul.innerHTML = "";
      ordem.forEach(function (texto, i) {
        var li = document.createElement("li");
        li.className = "order-item";
        var sobe = document.createElement("button");
        sobe.textContent = "▲";
        sobe.title = "Subir";
        sobe.disabled = i === 0;
        sobe.onclick = function () {
          var t = ordem[i - 1]; ordem[i - 1] = ordem[i]; ordem[i] = t;
          S.escolha = ordem.slice(); desenha(); atualizaBotao();
        };
        var desce = document.createElement("button");
        desce.textContent = "▼";
        desce.title = "Descer";
        desce.disabled = i === ordem.length - 1;
        desce.onclick = function () {
          var t = ordem[i + 1]; ordem[i + 1] = ordem[i]; ordem[i] = t;
          S.escolha = ordem.slice(); desenha(); atualizaBotao();
        };
        var txt = document.createElement("span");
        txt.className = "txt";
        txt.textContent = texto;
        li.appendChild(txt); li.appendChild(sobe); li.appendChild(desce);
        ul.appendChild(li);
      });
    }
    desenha();
    S.escolha = ordem.slice();     // a ordem inicial já é uma resposta válida
    corpo.appendChild(ul);
  }

  function corpoTexto(corpo) {
    var inp = document.createElement("input");
    inp.type = "text";
    inp.autocomplete = "off";
    inp.spellcheck = false;
    inp.placeholder = "Escreva sua resposta";
    inp.oninput = function () {
      S.escolha = inp.value.trim() || null;
      atualizaBotao();
    };
    inp.onkeydown = function (e) {
      if (e.key === "Enter" && !$("btn-responder").disabled) enviaResposta();
    };
    corpo.appendChild(inp);
    setTimeout(function () { inp.focus(); }, 30);
  }

  function montaConfianca() {
    var caixa = $("ciu-conf");
    caixa.innerHTML = "";
    S.escala.forEach(function (nivel) {
      var b = document.createElement("button");
      b.className = "conf-opt";
      b.textContent = nivel;
      b.setAttribute("aria-pressed", "false");
      b.onclick = function () {
        S.confianca = nivel;
        Array.prototype.forEach.call(caixa.children, function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        atualizaBotao();
      };
      caixa.appendChild(b);
    });
  }

  /* RF02: a confiança é coletada ANTES da submissão, e sem ela a resposta
   * não distingue lacuna de crença (§7.3). O botão fica travado até as
   * duas escolhas existirem — não é atrito gratuito, é o dado. */
  function atualizaBotao() {
    var temResposta = S.escolha !== null && S.escolha !== undefined &&
      (!Array.isArray(S.escolha) || S.escolha.length > 0);
    $("btn-responder").disabled = !(temResposta && S.confianca);
  }

  async function enviaResposta() {
    limpaErro("erro-ciu");
    $("btn-responder").disabled = true;
    var corpo = {
      ciu_id: S.acao.ciu_id,
      confidence: S.confianca,
      elapsed_ms: decorrido()
    };
    if (typeof S.escolha === "number") corpo.option_idx = S.escolha;
    else corpo.text = S.escolha;

    try {
      aplica(await api("POST", "/sessions/" + S.sessao + "/answer", corpo));
    } catch (e) {
      if (e.status === 409) return realinha();
      erroEm("erro-ciu", e.message);
      $("btn-responder").disabled = false;
    }
  }

  /* ------------------------------------------------------------- diagrama */

  function telaDiagrama() {
    var a = S.acao;
    $("diag-crenca").innerHTML =
      "<b>Um momento.</b> Sua resposta anterior indica que você está " +
      "assumindo o seguinte: " + (a.text ? "<i>" + a.text + "</i>" : "algo " +
      "que o diagrama abaixo põe em questão.");

    // A instrução acompanha o que o diagrama de fato oferece. Prometer
    // "dois estados, você controla a alternância" e não mostrar botão
    // nenhum faz o aluno procurar um controle que não existe — e, pior,
    // sugere que ele deixou de fazer algo que lhe foi pedido.
    var alternavel = Diagram.estadosComConteudo(a.visual).length >= 2;
    $("diag-instrucao").textContent = alternavel
      ? "O diagrama abaixo tem dois estados e você controla a alternância. "
        + "Compare quantas vezes quiser. Não há explicação ainda."
      : "Olhe o diagrama abaixo com atenção antes de continuar. "
        + "Não há explicação ainda.";

    var alvo = $("diag-alvo");
    alvo.innerHTML = "";
    alvo.appendChild(Diagram.render(a.visual, function (de, para) {
      // Telemetria: só o que o ALUNO fez. Não move a máquina de estados.
      api("POST", "/sessions/" + S.sessao + "/telemetry", {
        type: "diagram_toggled",
        payload: { from_state: de, to_state: para, elapsed_ms: decorrido() }
      }).catch(function () { /* telemetria nunca interrompe a sessão */ });
    }));

    $("btn-diagrama").onclick = async function () {
      $("btn-diagrama").disabled = true;
      try {
        aplica(await api("POST", "/sessions/" + S.sessao + "/ack",
                         { elapsed_ms: decorrido() }));
      } catch (e) {
        if (e.status === 409) return realinha();
        $("btn-diagrama").disabled = false;
      }
    };
    $("btn-diagrama").disabled = false;
    mostra("diagrama");
  }

  /* ---------------------------------------------------------------- passo */

  function telaPasso() {
    var a = S.acao;
    var socratico = a.kind === "ask";
    var idx = (a.step && a.step.idx) || 1;
    var total = (a.step && a.step.total) || 1;

    // O contador reinicia entre rodadas de correção: refutar a crença
    // fecha a cadeia DELA, e erguer o resto do KC é outra rodada. Sem esta
    // nota o aluno acha que voltou ao começo.
    var novaRodada = idx === 1 && S.ultimoTotal && total !== S.ultimoTotal;
    $("passo-nota").textContent = novaRodada
      ? "Esta é uma nova sequência: a anterior fechou. O que você já "
        + "confirmou continua valendo."
      : "";
    $("passo-nota").classList.toggle("hidden", !novaRodada);
    if (idx === 1) S.trilha = [];
    S.ultimoTotal = total;

    $("passo-contagem").textContent = "Passo " + idx + " de " + total;
    $("passo-barra").style.width = Math.round((idx - 1) / total * 100) + "%";
    $("passo-tipo").textContent =
      a.node_kind === "base" ? "premissa observável" : "decorre do que você confirmou";
    $("passo-texto").textContent = a.text || "";

    S.trilha[idx - 1] = a.text || "";
    desenhaTrilha(idx, total);
    pintaFeedback("passo-feedback", a.feedback);

    /* Duas ilustrações possíveis, nunca as duas ao mesmo tempo — quem
     * decide é o servidor, em _dados_do_passo:
     *
     *   a.visual   o diagrama do confronto RF08 (manipulação experimental)
     *   a.figure   a analogia do próprio nó, vinda do grafo
     *
     * Sem a primeira, a pergunta dizia "olhando o diagrama" sem diagrama
     * nenhum na tela. Sem a segunda, cada premissa era só uma frase. */
    var alvo = $("passo-diagrama");
    alvo.innerHTML = "";
    if (a.visual) {
      alvo.appendChild(Diagram.render(a.visual, function (de, para) {
        api("POST", "/sessions/" + S.sessao + "/telemetry", {
          type: "diagram_toggled",
          payload: { from_state: de, to_state: para, elapsed_ms: decorrido() }
        }).catch(function () {});
      }));
    } else if (a.figure) {
      var fig = Fig.render(a.figure, "premissa-fig");
      if (fig) alvo.appendChild(fig);
    }

    var acoes = $("passo-acoes");
    acoes.innerHTML = "";
    if (socratico) {
      acoes.appendChild(botao("Sim, confirmo", "btn", function () { passo(true); }));
      acoes.appendChild(botao("Não tenho certeza", "btn ghost", function () { passo(false); }));
    } else {
      // Braço B: o aluno lê e confirma. Não há caminho de erro — é isso
      // que a variável isolada significa.
      acoes.appendChild(botao("Entendi, continuar", "btn", function () { passo(true); }));
    }
    mostra("passo");
  }

  /* RF17: o feedback vem do servidor pronto, nas tres etapas. O cliente
   * so o coloca na tela — nao decide quando aparece nem o que diz, e nao
   * o mostra diferente por braco. */
  function pintaFeedback(id, f) {
    var caixa = $(id);
    caixa.classList.toggle("hidden", !f);
    if (f) caixa.textContent = f.text;
  }

  function botao(texto, cls, fn) {
    var b = document.createElement("button");
    b.className = cls;
    b.textContent = texto;
    b.onclick = function () { b.disabled = true; fn(); };
    return b;
  }

  function desenhaTrilha(idx, total) {
    var caixa = $("passo-trilha");
    caixa.innerHTML = "";
    caixa.classList.toggle("hidden", total < 2);
    for (var i = 1; i <= total; i++) {
      var linha = document.createElement("div");
      linha.className = "step-row " + (i < idx ? "done" : i === idx ? "cur" : "");
      var n = document.createElement("span");
      n.className = "n";
      n.textContent = i < idx ? "✓" : i;
      var t = document.createElement("span");
      t.textContent = i <= idx ? (S.trilha[i - 1] || "") : "—";
      linha.appendChild(n); linha.appendChild(t);
      caixa.appendChild(linha);
    }
  }

  async function passo(aceito) {
    try {
      aplica(await api("POST", "/sessions/" + S.sessao + "/step", {
        accepted: aceito, elapsed_ms: decorrido(),
        kc: S.acao.kc, node: S.acao.node
      }));
    } catch (e) {
      if (e.status === 409) return realinha();
      telaPasso();   // reabilita os botões
    }
  }

  /* ------------------------------------------------------------ conclusão */

  function telaConclusao(j) {
    var a = S.acao;
    // KC deixado em aberto: o aluno não construiu esta conclusão, recebeu.
    // Dizer "você acabou de construir isto" seria mentira na cara dele.
    var aberto = !!a.incomplete;
    $("conc-titulo").textContent = aberto
      ? "Este tópico fica em aberto"
      : "Você acabou de construir isto";
    $("conc-texto").className = aberto ? "banner warn" : "banner ok";
    $("conc-texto").textContent = a.conclusion_text || a.text || "";
    pintaFeedback("conc-feedback", a.feedback);
    var nome = aberto ? null : a.technical_name;
    $("conc-nome-linha").classList.toggle("hidden", !nome);
    if (nome) $("conc-nome").textContent = nome;
    $("conc-nota").textContent = (!aberto && j && j.arm === "socratic")
      ? "Nada disso foi explicado antes: cada premissa veio de uma resposta sua."
      : "";
    $("btn-conclusao").disabled = false;
    $("btn-conclusao").onclick = async function () {
      $("btn-conclusao").disabled = true;
      try {
        aplica(await api("POST", "/sessions/" + S.sessao + "/ack",
                         { elapsed_ms: decorrido() }));
      } catch (e) {
        if (e.status === 409) return realinha();
        $("btn-conclusao").disabled = false;
      }
    };
    mostra("conclusao");
  }

  /* ------------------------------------------------------------------ fim */

  function telaFim(j) {
    var st = (j && j.kc_status) || {};
    var completos = Object.keys(st).filter(function (k) {
      return st[k] === "completed";
    });
    $("fim-resumo").textContent =
      completos.length + " de " + Object.keys(st).length +
      " tópicos concluídos.";
    $("rodape").textContent = "";
    try { localStorage.removeItem("structura.codigo"); } catch (e) {}
    mostra("fim");
  }

  /* --------------------------------------------------------- realinhamento */

  /* 409: o servidor e a tela discordam — botão voltar, clique duplo, aba
   * antiga. Em vez de insistir, recarrega a verdade do servidor. */
  async function realinha() {
    try {
      aplica(await api("GET", "/sessions/" + S.sessao));
    } catch (e) {
      erroEm("erro-abertura", "não foi possível retomar: " + e.message);
      mostra("abertura");
    }
  }

  /* ----------------------------------------------------------------- boot */

  async function boot() {
    iniciaAbertura();
    mostra("abertura");
    try {
      var h = await api("GET", "/health");
      S.escala = h.confidence_scale || [];
      montaAbertura(h);
      $("meta").innerHTML = "domínio <b>" + h.domain_hash.slice(7, 15) + "</b>";
    } catch (e) {
      erroEm("erro-abertura", "servidor fora do ar: " + e.message);
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
