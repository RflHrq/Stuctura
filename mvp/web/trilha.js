/* A trilha: o tópico em sequência, com o trabalho que cada ideia pede.
 *
 * ESTE ARQUIVO NÃO DECIDE NADA. Ele manda o que a pessoa fez e desenha a
 * tela que volta. Qual é a próxima pergunta, se a resposta estava certa,
 * que caminho a pessoa segue — tudo isso é do motor (mvp/trilha.py), e
 * chega pronto.
 *
 * E NÃO ESCREVE CONTEÚDO. Toda frase de premissa, de crença, de degrau e
 * de retorno vem do servidor. Daqui só saem as frases fixas de ligação
 * ("Por quê?", "Isso mesmo.", "A ideia que fica de pé:"), que não mudam
 * com o tópico. mvp/test_trilha_telas.py confere as duas coisas.
 *
 * Sem dependência externa, como o resto do projeto.
 */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  /* O CAMINHO-BASE. Dentro do portal a trilha mora em /trilha/kc_00/, e
   * as rotas dela ficam debaixo desse caminho. Sai da URL da própria
   * página: ela só fala com o tópico em que foi aberta. */
  var PARTES = window.location.pathname.split("/");
  var NO_PORTAL = PARTES[1] === "trilha" && !!PARTES[2];
  var BASE = NO_PORTAL ? "/trilha/" + PARTES[2] : "";
  /* O tópico, para o navegador lembrar a sessão e o andamento dele
   * (progresso.js). Fora do portal não há tópico na URL, e nada se
   * guarda. */
  var TOPICO = NO_PORTAL ? PARTES[2] : "";
  var GUARDA = !!(TOPICO && window.Progresso);

  /* O mesmo teto do servidor para o tempo de uma resposta. Quem deixa a
   * página aberta de um dia para o outro não pode ficar com um número
   * que só cresce. */
  var LIMITE_MS = 2 * 60 * 60 * 1000;

  var S = {
    sessao: null,
    codigo: "",         // o código com que a sessão abriu ("" sem código)
    tela: null,
    passo: 0,           // o número da tela, que volta em todo pedido
    cartao: null,       // o cartão na tela, para o retorno entrar ABAIXO dele
    inicio: 0,
    ocupado: false,     // um pedido no ar: os botões não agem de novo
    ritmo: ""
  };

  /* ------------------------------------------------------ frases fixas */

  var RITMO = {
    "completo": { nome: "Completo",
                  detalhe: "duas perguntas por ideia: uma de marcar, uma de escrever" },
    "rapido": { nome: "Rápido", detalhe: "uma pergunta por ideia" }
  };
  var PAPEL = {
    "abertura": "Pergunta",
    "reforco": "Mais uma, para firmar",
    "topo": "A pergunta desta ideia",
    "confirmacao": "Mais uma pergunta",
    "reconferencia": "Reconferência",
    "produzir": "Agora é com você",
    "treino": "Treino"
  };
  var VEREDITO = {
    "firme": { tom: "certo", titulo: "Isso mesmo." },
    "certa": { tom: "certo", titulo: "Isso mesmo." },
    "inseguro": { tom: "certo", titulo: "Está certo, e a razão também.",
                  depois: "Como você não tinha certeza, vem mais uma pergunta para firmar." },
    "escorregao": { tom: "neutro",
                    titulo: "A razão que você marcou está certa, mas a resposta não combina com ela.",
                    depois: "Vem mais uma pergunta sobre a mesma ideia." },
    "razao_errada": { tom: "neutro",
                      titulo: "A resposta está certa, mas a razão que você marcou não leva a ela.",
                      depois: "Vem mais uma pergunta sobre a mesma ideia." },
    "errada": { tom: "errado", titulo: "Ainda não." },
    "lacuna": { tom: "neutro", titulo: "Tudo bem." },
    "crenca": { tom: "neutro", titulo: "Vamos conferir." }
  };
  var RESULTADO = {
    "ja_sabia": "já sabia",
    "firmou": "firmou",
    "aprendeu_agora": "aprendeu agora",
    "corrigiu": "corrigiu uma ideia",
    "em_aberto": "ficou em aberto"
  };
  var RECONFERENCIA = {
    "assimilou": "assimilou",
    "nao_se_manteve": "não se manteve",
    "a_ideia_voltou": "a ideia voltou",
    "sem_questao": "não deu para reconferir"
  };

  /* ----------------------------------------------------------- peças */

  function el(nome, atributos, filhos) {
    var n = document.createElement(nome);
    Object.keys(atributos || {}).forEach(function (k) {
      var v = atributos[k];
      if (v === null || v === undefined || v === false) return;
      if (k === "texto") n.textContent = v;
      else if (k === "onclick") n.addEventListener("click", v);
      else n.setAttribute(k, v === true ? "" : v);
    });
    (filhos || []).forEach(function (f) { if (f) n.appendChild(f); });
    return n;
  }

  function p(classe, texto) { return el("p", { "class": classe, texto: texto }); }

  /* O código sai em cores (realce.js). A saída do programa e o que o
     compilador disse vêm com a classe "terminal" e saem como texto puro,
     assim como tudo, se o realce não tiver carregado. */
  function bloco(texto, classe) {
    var tipo = classe || "codigo";
    var pre = el("pre", { "class": tipo });
    if (tipo === "codigo" && window.Realce) window.Realce.preenche(pre, texto);
    else pre.textContent = texto;
    return pre;
  }

  function botao(texto, aoClicar, classe) {
    return el("button", { type: "button", "class": classe || "btn",
                          texto: texto, onclick: aoClicar });
  }

  function decorrido() {
    var ms = Math.max(0, Math.round(performance.now() - S.inicio));
    return Math.min(ms, LIMITE_MS);
  }

  /* Um grupo de botões em que UM fica marcado. Devolve o elemento; quem
   * chama recebe o índice escolhido. */
  function grupo(classeDoGrupo, classeDoBotao, textos, aoEscolher) {
    var caixa = el("div", { "class": classeDoGrupo });
    textos.forEach(function (texto, i) {
      var b = el("button", { type: "button", "class": classeDoBotao,
                             "aria-pressed": "false" });
      if (String(texto).indexOf("\n") >= 0) {
        b.appendChild(el("pre", { "class": "t-linhas", texto: texto }));
      } else {
        b.textContent = texto;
      }
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(caixa.children, function (x, k) {
          x.setAttribute("aria-pressed", k === i ? "true" : "false");
        });
        aoEscolher(i);
      });
      caixa.appendChild(b);
    });
    return caixa;
  }

  function cabeca(rotulo) {
    return p("etiqueta", rotulo);
  }

  var avisoRelogio = null;
  function avisa(texto, tom) {
    var a = $("aviso");
    a.textContent = texto;
    a.className = "t-aviso" + (tom ? " " + tom : "");
    window.clearTimeout(avisoRelogio);
    avisoRelogio = window.setTimeout(function () {
      a.classList.add("oculto");
    }, tom === "ok" ? 1100 : 3500);
  }

  /* ------------------------------------------------------- o servidor */

  async function pede(rota, corpo) {
    var r;
    try {
      r = await fetch(BASE + rota, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(corpo || {})
      });
    } catch (erro) {
      return { status: 0, json: null };
    }
    var json = null;
    try { json = await r.json(); } catch (erro) { json = null; }
    return { status: r.status, json: json };
  }

  /* Uma ação da pessoa. `mesmaTela` é para as três que não respondem à
   * tela — explicação, modo, ritmo —: o servidor devolve a MESMA tela, e
   * redesenhar apagaria o que a pessoa já tinha marcado. */
  async function age(corpo, mesmaTela) {
    if (S.ocupado || !S.sessao) return;
    S.ocupado = true;
    $("palco").classList.add("t-ocupado");
    corpo.ms = decorrido();
    /* De que tela este pedido é. O servidor recusa o que for de uma tela
     * que já passou — uma resposta reenviada, outra aba —, em vez de
     * aplicá-lo à tela seguinte. */
    corpo.passo = S.passo;
    var r = await pede("/sessoes/" + S.sessao + "/agir", corpo);
    S.ocupado = false;
    $("palco").classList.remove("t-ocupado");

    if (r.status === 200) { recebe(r.json, mesmaTela); return; }
    if (r.status === 404) { perdeu(); return; }
    /* A sessão existiu, mas este servidor não consegue refazê-la: o
     * conteúdo do tópico mudou. A frase vem do servidor. */
    if (r.status === 410) { perdeu(r.json && r.json.detail); return; }
    if (r.status === 409 && r.json && r.json.tela) {
      /* A tela já tinha mudado. O servidor manda a atual, e é ela que
       * passa a valer: nada de adivinhar onde a sessão está. */
      avisa("Esta tela já tinha mudado. Aqui está a atual.");
      recebe(r.json);
      return;
    }
    if (r.status === 400) {
      avisa("Essa ação não cabe mais nesta tela.");
    } else if (r.status === 0) {
      avisa("Sem resposta do servidor. Tente de novo.");
    } else {
      avisa("Algo não deu certo (" + r.status + ").");
    }
  }

  function recebe(j, mesmaTela) {
    S.tela = j.tela;
    S.passo = j.passo;
    /* O ritmo vem do servidor a cada resposta. Quem reabre a página com
     * o código não passou pela tela de entrada, e sem isto os ajustes
     * abririam vazios. */
    S.ritmo = j.ritmo || S.ritmo;
    /* O navegador lembra onde a pessoa está, e quanto do tópico fechou:
     * é o que deixa voltar sem código e a página inicial mostrar o
     * andamento. */
    if (GUARDA) Progresso.anota(TOPICO, j, S.codigo);
    desenhaAjustes();
    desenhaProgresso(j.progresso, j.tela);
    if (j.explicacao) { abrePainel(j.explicacao); return; }
    if (mesmaTela) return;
    if (j.veredito === "certa" && j.tela.tipo !== "retorno") avisa("✓ Isso!", "ok");
    desenha(j.tela);
  }

  /* A sessão que o servidor não conhece mais. O que o navegador guardava
   * dela também não serve, e é esquecido. */
  function perdeu(texto) {
    S.sessao = null;
    if (GUARDA) Progresso.apaga(TOPICO);
    $("palco").classList.add("oculto");
    $("ajustes").classList.add("oculto");
    $("btn-ajustes").hidden = true;
    $("btn-sair").hidden = true;
    if (texto) $("perdida-texto").textContent = texto;
    $("perdida").classList.remove("oculto");
    $("btn-recomecar").focus();
  }

  async function abre(codigo) {
    $("perdida").classList.add("oculto");
    $("palco").classList.remove("oculto");
    var r = await pede("/sessoes", { codigo: codigo || "" });
    if (r.status === 200) {
      S.sessao = r.json.sessao;
      S.codigo = codigo || "";
      recebe(r.json);
      return;
    }
    if (r.status === 0) {
      perdeu("O servidor não respondeu. Confira se o sistema está ligado e tente de novo.");
    } else {
      perdeu((r.json && r.json.detail) ? String(r.json.detail)
             : "Não foi possível abrir a sessão (" + r.status + ").");
    }
  }

  /* --------------------------------------------------------- progresso */

  /* As paradas do topo: um círculo numerado por ideia. O estado vai no
     aria-label, para quem não vê a cor. */
  function desenhaProgresso(progresso, tela) {
    var lista = $("progresso");
    lista.textContent = "";
    if (!progresso) return;
    progresso.premissas.forEach(function (x, i) {
      var classe = "", estado = "ainda não";
      if (x.resultado === "em_aberto") { classe = "t-aberto"; estado = "em aberto"; }
      else if (x.resultado) { classe = "t-bem"; estado = "feita"; }
      else if (tela && tela.premissa === x.no) { classe = "t-atual"; estado = "agora"; }
      lista.appendChild(el("li", {
        "class": classe,
        "aria-label": "Ideia " + (i + 1) + ": " + estado,
        "aria-current": classe === "t-atual" ? "step" : null,
        title: x.resultado ? RESULTADO[x.resultado] : "",
        texto: String(i + 1)
      }));
    });
    lista.setAttribute("aria-label", "Ideias deste tópico: " +
                       progresso.feitas + " de " + progresso.total);
  }

  /* ----------------------------------------------------------- ajustes */

  function desenhaAjustes() {
    function linha(id, mapa, atual, acao) {
      var caixa = $(id);
      caixa.textContent = "";
      Object.keys(mapa).forEach(function (chave) {
        var b = el("button", { type: "button", "class": "conf",
                               "aria-pressed": chave === atual ? "true" : "false",
                               texto: mapa[chave].nome, title: mapa[chave].detalhe });
        b.addEventListener("click", function () {
          var corpo = { acao: acao };
          corpo[acao] = chave;
          S[acao] = chave;
          desenhaAjustes();
          age(corpo, true);
        });
        caixa.appendChild(b);
      });
    }
    linha("ajuste-ritmo", RITMO, S.ritmo, "ritmo");
  }

  $("btn-ajustes").addEventListener("click", function () {
    var aberto = $("ajustes").classList.toggle("oculto") === false;
    $("btn-ajustes").setAttribute("aria-expanded", aberto ? "true" : "false");
  });

  /* -------------------------------------------------------- explicação */

  function corpoDaExplicacao(x, no) {
    var caixa = el("div", {});
    if (x.simples) caixa.appendChild(p("ideia", x.simples));
    (x.frases || []).forEach(function (f) { caixa.appendChild(p("t-frase", f)); });
    if (x.cena && window.Cena) {
      /* A ideia com cena: a cena toma o lugar do código e da figura
       * antiga (docs/interface.md, 8.1). Em tela larga ela fica ao lado
       * do texto, para caber sem rolagem (tema.css, "t-lado-a-lado"). */
      caixa.className = "t-lado-texto";
      return el("div", { "class": "t-lado-a-lado" },
                [caixa, Cena.desenha(x.cena, x.codigo)]);
    }
    if (x.codigo) caixa.appendChild(bloco(x.codigo));
    var figura = el("div", { "class": "figura" });
    caixa.appendChild(figura);
    if (window.Figuras) window.Figuras.dentro(figura, no);
    return caixa;
  }

  function abrePainel(explicacao) {
    var corpo = $("painel-corpo");
    corpo.textContent = "";
    corpo.appendChild(corpoDaExplicacao(explicacao, explicacao.no));
    /* Com cena, o painel alarga em tela de computador. */
    corpo.parentNode.classList.toggle("t-largo", !!(explicacao.cena && window.Cena));
    $("painel").classList.remove("oculto");
    $("btn-fechar-painel").focus();
  }

  function fechaPainel() { $("painel").classList.add("oculto"); }

  $("btn-fechar-painel").addEventListener("click", fechaPainel);
  $("painel").addEventListener("click", function (ev) {
    if (ev.target === $("painel")) fechaPainel();
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") { fechaPainel(); fechaSair(); }
  });

  /* -------------------------------------------------------------- sair */

  /* Sair no meio da sessão (o Rafael, em 19/11/2026): guardar para
   * continuar depois, ou cancelar e começar do zero. Guardar não precisa
   * do servidor: cada resposta já está no registro, e o navegador lembra
   * a sessão. Cancelar marca a sessão no registro (nada é apagado), e o
   * navegador esquece o andamento. */
  function abreSair() {
    $("sair-escolha").hidden = false;
    $("sair-confirma").hidden = true;
    $("sair-erro").hidden = true;
    $("sair").classList.remove("oculto");
    $("btn-guardar-sair").focus();
  }

  function fechaSair() {
    $("sair").classList.add("oculto");
    $("btn-sair").focus();
  }

  /* De volta à página dos tópicos. Fora do portal não há para onde ir: a
   * sessão fica guardada, e o aviso diz como voltar a ela. */
  function vaiAosTopicos() {
    if (NO_PORTAL) { window.location.href = "/"; return; }
    fechaSair();
    avisa("A sessão ficou guardada. Abra este endereço de novo para continuar.");
  }

  function guardaESai() {
    vaiAosTopicos();
  }

  async function cancelaSessao() {
    var r = await pede("/sessoes/" + S.sessao + "/cancela", {});
    /* 410: já estava cancelada (outra aba, um segundo toque). O efeito
     * que a pessoa pediu já existe, e segue igual. */
    if (r.status !== 200 && r.status !== 410) {
      $("sair-erro").textContent = r.status === 0
        ? "O servidor não respondeu, e a sessão não foi cancelada. Tente de novo."
        : "Não foi possível cancelar a sessão (" + r.status + ").";
      $("sair-erro").hidden = false;
      return;
    }
    if (GUARDA) Progresso.apaga(TOPICO);
    S.sessao = null;
    if (NO_PORTAL) { window.location.href = "/"; return; }
    fechaSair();
    recomeca();
  }

  $("btn-sair").addEventListener("click", abreSair);
  $("btn-guardar-sair").addEventListener("click", guardaESai);
  $("btn-ficar").addEventListener("click", fechaSair);
  $("btn-cancelar-sessao").addEventListener("click", function () {
    $("sair-escolha").hidden = true;
    $("sair-confirma").hidden = false;
    $("btn-nao-cancelar").focus();
  });
  $("btn-nao-cancelar").addEventListener("click", function () {
    $("sair-confirma").hidden = true;
    $("sair-escolha").hidden = false;
    $("btn-guardar-sair").focus();
  });
  $("btn-confirma-cancelar").addEventListener("click", cancelaSessao);
  $("sair").addEventListener("click", function (ev) {
    if (ev.target === $("sair")) fechaSair();
  });

  function botaoDaExplicacao() {
    return botao("Ver a explicação", function () {
      age({ acao: "explicacao" }, true);
    }, "btn-topo");
  }

  /* Na reconferência a explicação não abre — o servidor recusa, e o
   * botão nem aparece. Ela existe para separar "acertou logo depois de
   * ler" de "assimilou". */
  function explicacaoSe(t) {
    return t.papel === "reconferencia" ? null : botaoDaExplicacao();
  }

  /* ------------------------------------------------------------- telas */

  var DESENHA = {};

  function desenha(tela) {
    /* O retorno entra ABAIXO do que a pessoa acabou de fazer: ela vê a
     * resposta que deu e o que o sistema diz sobre ela, na mesma tela. */
    if (tela.tipo === "retorno" && S.cartao && S.cartao.isConnected) {
      anexaRetorno(tela);
      return;
    }
    var palco = $("palco");
    palco.textContent = "";
    /* A revisão com cena alarga o palco em tela de computador (tema.css). */
    palco.classList.toggle("t-largo", tela.tipo === "revisao" && !!tela.cena && !!window.Cena);
    var cartao = el("section", { "class": "cartao t-cartao" });
    S.cartao = cartao;
    palco.appendChild(cartao);
    (DESENHA[tela.tipo] || DESENHA["retorno"])(cartao, tela);

    var comAjustes = tela.tipo !== "entrada" && tela.tipo !== "mapa";
    $("btn-ajustes").hidden = !comAjustes;
    /* Sair só faz sentido com a sessão andando: na entrada ainda não há o
     * que guardar, e no mapa ela já terminou. */
    $("btn-sair").hidden = !comAjustes;
    if (!comAjustes) $("ajustes").classList.add("oculto");
    S.inicio = performance.now();
    window.scrollTo(0, 0);
  }

  DESENHA["entrada"] = function (c, t) {
    var ritmo = t.ritmo_padrao;
    c.appendChild(cabeca(t.premissas + " ideias"));
    c.appendChild(el("h2", { texto: t.titulo }));

    c.appendChild(p("t-pede", "Em que ritmo?"));
    var nota = p("aviso", RITMO[ritmo].detalhe);
    var linha = grupo("confianca", "conf",
                      t.ritmos.map(function (r) { return RITMO[r].nome; }),
                      function (i) {
                        ritmo = t.ritmos[i];
                        nota.textContent = RITMO[ritmo].detalhe;
                      });
    linha.children[t.ritmos.indexOf(ritmo)].setAttribute("aria-pressed", "true");
    c.appendChild(linha);
    c.appendChild(nota);

    /* Um botão só. Toda ideia abre com uma pergunta, e a entrada diz o
     * que fazer com ela quando a pessoa não sabe: o "Não sei" leva aos
     * passos, e também é resposta. */
    c.appendChild(p("t-frase",
      "Cada ideia começa com uma pergunta. Se você não souber, toque em " +
      "“Não sei”: a ideia é construída passo a passo, e segue."));
    c.appendChild(el("div", { "class": "t-acoes" }, [
      botao("Começar", function () {
        S.ritmo = ritmo;
        desenhaAjustes();
        age({ acao: "comecar", ritmo: ritmo });
      })
    ]));
  };

  DESENHA["pergunta"] = function (c, t) {
    c.dataset.atividade = t.atividade;
    c.dataset.formato = t.formato;
    c.appendChild(cabeca(PAPEL[t.papel] || PAPEL["abertura"]));
    c.appendChild(p("ideia", t.texto));
    if (t.codigo) c.appendChild(bloco(t.codigo));

    var escolha = null, razao = null, confianca = "";
    /* Com porquê ou certeza depois, a resposta passa por "Confirmar
     * resposta" antes (ver abaixo). Sem eles, não há o que esconder, e a
     * alternativa fica trocável até o Responder. */
    var precisaConfirmar = !!(t.pede_razao || t.pede_certeza);
    var confirmada = !precisaConfirmar;
    var enviar = botao("Responder", function () {
      age({ acao: "responder", escolha: escolha, razao: razao,
            confianca: confianca });
    });
    enviar.disabled = true;
    enviar.hidden = precisaConfirmar;

    function confere() {
      enviar.disabled = !(escolha !== null && confirmada &&
                          (!t.pede_razao || razao !== null) &&
                          (!t.pede_certeza || confianca));
    }

    var etapaCerteza = el("div", { "class": "t-etapa oculto" }, [
      p("t-pede", "Quanta certeza?"),
      grupo("confianca", "conf", t.escala, function (i) {
        confianca = t.escala[i];
        confere();
      })
    ]);
    var etapaRazao = el("div", { "class": "t-etapa oculto" }, [
      p("t-pede", "Por quê?"),
      grupo("opcoes", "opcao",
            t.razoes.map(function (z) { return z.texto; }),
            function (i) {
              razao = i;
              if (t.pede_certeza) etapaCerteza.classList.remove("oculto");
              confere();
            })
    ]);

    /* A resposta TRAVA quando o porquê aparece: é a regra do sistema
     * desde sempre. Quem vê as razões não pode voltar e trocar a
     * resposta para combinar com uma delas.
     *
     * Mas tocar numa alternativa só a MARCA: dá para trocar à vontade,
     * e quem trava é o "Confirmar resposta" — e só então o porquê
     * aparece. O Rafael, em 19/11/2026, tocou na alternativa errada e
     * não tinha como voltar; das três saídas propostas, escolheu esta,
     * que conserta o toque errado sem deixar ver as razões antes. */
    var opcoes = grupo("opcoes", "opcao",
                       t.opcoes.map(function (o) { return o.texto; }),
                       function (i) {
                         escolha = i;
                         if (confirma) confirma.disabled = false;
                         confere();
                       });
    var confirma = null;
    if (precisaConfirmar) {
      confirma = botao("Confirmar resposta", function () {
        if (escolha === null) return;
        confirmada = true;
        opcoes.classList.add("t-travada");
        Array.prototype.forEach.call(opcoes.children, function (b) {
          b.disabled = true;
        });
        confirma.hidden = true;
        enviar.hidden = false;
        var etapa = t.pede_razao ? etapaRazao : etapaCerteza;
        etapa.classList.remove("oculto");
        var primeiro = etapa.querySelector("button");
        if (primeiro) primeiro.focus();
        confere();
      });
      confirma.disabled = true;
    }
    c.appendChild(opcoes);
    if (confirma) c.appendChild(el("div", { "class": "t-acoes" }, [confirma]));
    c.appendChild(etapaRazao);
    c.appendChild(etapaCerteza);
    c.appendChild(el("div", { "class": "t-acoes" }, [
      enviar,
      botao("Não sei", function () { age({ acao: "nao_sei" }); }, "btn-topo"),
      explicacaoSe(t)
    ]));
  };

  /* As cinco formas de produzir. Cada uma desenha o exercício dentro do
   * cartão e chama `pronto(resposta)` quando há o que enviar — ou
   * `pronto(null)` quando deixou de haver. */
  var FORMA = {};

  FORMA["tocar"] = function (c, t, pronto) {
    c.appendChild(p("t-pede", t.pede));
    var linha = grupo("codigo t-toque", "t-peca", t.pecas, function (i) {
      pronto({ pecas: [i] });
    });
    c.appendChild(linha);
  };

  FORMA["escolher"] = function (c, t, pronto) {
    if (t.mostra) c.appendChild(bloco(t.mostra));
    c.appendChild(p("t-pede", t.pede));
    /* Opção que é uma linha de C aparece com cara de código; opção que é
     * frase, não. Quem sabe qual é qual é o conteúdo, não esta tela. */
    c.appendChild(grupo("opcoes" + (t.em_codigo ? " t-codigo" : ""), "opcao",
                        t.pecas, function (i) {
                          pronto({ pecas: [i] });
                        }));
  };

  FORMA["completar"] = function (c, t, pronto) {
    c.appendChild(p("t-pede", t.pede));
    var partes = t.mostra.split("___");
    var buraco = el("span", { "class": "t-buraco", texto: "?" });
    c.appendChild(el("pre", { "class": "codigo" }, [
      document.createTextNode(partes[0] || ""), buraco,
      document.createTextNode(partes.slice(1).join("___"))
    ]));
    c.appendChild(grupo("t-banco", "t-peca", t.pecas, function (i) {
      buraco.textContent = t.pecas[i];
      pronto({ pecas: [i] });
    }));
  };

  FORMA["digitar"] = function (c, t, pronto, envia) {
    if (t.mostra) c.appendChild(bloco(t.mostra));
    c.appendChild(p("t-pede", t.pede));
    var campo = el("input", { type: "text", "class": "t-digita",
                              maxlength: "200", autocomplete: "off",
                              autocapitalize: "off", spellcheck: "false",
                              "aria-label": "Sua resposta" });
    campo.addEventListener("input", function () {
      var valor = campo.value.trim();
      pronto(valor ? { texto: valor } : null);
    });
    campo.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter" && campo.value.trim()) envia();
    });
    c.appendChild(campo);
    window.setTimeout(function () { campo.focus(); }, 0);
  };

  FORMA["montar"] = function (c, t, pronto) {
    if (t.mostra) c.appendChild(bloco(t.mostra));
    c.appendChild(p("t-pede", t.pede));
    /* Peças que são linhas inteiras empilham; peças que são pedaços de
     * uma linha ficam lado a lado. */
    var emLinhas = t.pecas.some(function (x) {
      return x.indexOf(" ") >= 0 || x.indexOf("\n") >= 0;
    });
    var extra = emLinhas ? " t-em-linhas" : "";
    var montada = el("div", { "class": "t-montada" + extra,
                              "aria-label": "Sua resposta" });
    var banco = el("div", { "class": "t-banco" + extra,
                            "aria-label": "Peças" });
    var ordem = [];

    function redesenha() {
      montada.textContent = "";
      ordem.forEach(function (i, posicao) {
        montada.appendChild(el("button", {
          type: "button", "class": "t-peca", texto: t.pecas[i],
          "aria-label": "Tirar " + t.pecas[i],
          onclick: function () { ordem.splice(posicao, 1); redesenha(); }
        }));
      });
      Array.prototype.forEach.call(banco.children, function (b, i) {
        b.classList.toggle("t-usada", ordem.indexOf(i) >= 0);
        b.disabled = ordem.indexOf(i) >= 0;
      });
      pronto(ordem.length ? { pecas: ordem.slice() } : null);
    }

    t.pecas.forEach(function (texto, i) {
      banco.appendChild(el("button", {
        type: "button", "class": "t-peca", texto: texto,
        onclick: function () { ordem.push(i); redesenha(); }
      }));
    });
    c.appendChild(montada);
    c.appendChild(banco);
  };

  DESENHA["degrau"] = function (c, t) {
    c.dataset.degrau = t.degrau;
    c.classList.toggle("t-guiado", !!t.guiado);
    c.appendChild(cabeca(t.papel === "subida"
                         ? "Passo " + t.indice + " de " + t.total
                         : (PAPEL[t.papel] || PAPEL["treino"])));
    if (t.papel === "subida" && t.indice === 1 && t.tentativa === 1) {
      c.appendChild(p("t-intro", "Vamos construir esta ideia passo a passo."));
    }
    if (t.tentativa > 1) {
      c.appendChild(p("t-intro", "De novo, com outros valores."));
    }
    t.frases.forEach(function (f) { c.appendChild(p("t-frase", f)); });
    if (t.antes) {
      c.appendChild(p("t-rotulo", "Já está escrito:"));
      c.appendChild(bloco(t.antes));
    }

    /* O passo em que uma alternativa é a crença pede também a certeza:
     * é ela que separa quem acredita de quem chutou. Sem ela marcada, o
     * botão não responde. */
    var resposta = null;
    var certeza = "";
    function completo() {
      return !!resposta && (!t.pede_certeza || !!certeza);
    }
    function envia() {
      if (!completo()) return;
      age({ acao: "responder", pecas: resposta.pecas || [],
            texto: resposta.texto || "", confianca: certeza });
    }
    var enviar = botao("Responder", envia);
    enviar.disabled = true;
    function pronto(r) {
      resposta = r;
      enviar.disabled = !completo();
    }
    (FORMA[t.forma] || FORMA["escolher"])(c, t, pronto, function () {
      /* O "enter" de quem digita só responde com tudo marcado. */
      envia();
    });
    if (t.pede_certeza) {
      c.appendChild(p("t-pede", "Quanta certeza você tem?"));
      c.appendChild(grupo("confianca", "conf", t.escala, function (i) {
        certeza = t.escala[i];
        enviar.disabled = !completo();
      }));
    }
    c.appendChild(el("div", { "class": "t-acoes" }, [
      enviar, explicacaoSe(t)
    ]));
  };

  function montaRetorno(t) {
    var v = VEREDITO[t.veredito] || VEREDITO["errada"];
    var b = el("div", { "class": "t-retorno " + v.tom, role: "status" });
    b.appendChild(p("veredito " + v.tom, v.titulo));
    if (t.texto) b.appendChild(p("t-frase", t.texto));
    if (t.mostra_certa) {
      b.appendChild(p("t-rotulo", "A resposta certa:"));
      b.appendChild(bloco(t.mostra_certa));
    }
    if (t.escolheu) {
      b.appendChild(p("t-rotulo", "Você marcou:"));
      b.appendChild(el("blockquote", { "class": "t-fala", texto: t.escolheu }));
    }
    /* O porquê da questão acertada (docs/trilha.md, seção 7): uma frase
     * sobre ESTA questão. Quem acertou pela razão certa lê o porquê no
     * lugar da premissa genérica; quem acertou pela razão errada lê os
     * dois, porque a premissa é o que corrige a razão. */
    var noLugar = t.porque && v.tom === "certo";
    if (t.porque) {
      b.appendChild(p("t-rotulo", "Por que está certa:"));
      b.appendChild(p("ideia", t.porque));
      if (noLugar) {
        var desenho = el("div", { "class": "figura" });
        b.appendChild(desenho);
        if (window.Figuras) window.Figuras.dentro(desenho, t.sobre);
      }
    }
    /* A premissa entra quando o retorno é sobre a IDEIA. No erro de um
     * degrau o texto do erro já diz o que faltou, e a ideia inteira ali
     * seria ruído. */
    if (t.premissa_texto && !(t.veredito === "errada" && t.texto) && !noLugar) {
      var rotulo = "A ideia desta pergunta:";
      if (t.escolheu) {
        rotulo = t.contradiz ? "Isso contradiz esta ideia:"
                             : "Essa razão fala de outra ideia. A desta pergunta é:";
      } else if (v.tom === "certo") {
        rotulo = "A ideia:";
      }
      b.appendChild(p("t-rotulo", rotulo));
      b.appendChild(p("ideia", t.premissa_texto));
      var figura = el("div", { "class": "figura" });
      b.appendChild(figura);
      if (window.Figuras) window.Figuras.dentro(figura, t.sobre);
    }
    if (v.depois) b.appendChild(p("aviso", v.depois));
    var seguir = botao("Continuar", function () { age({ acao: "continuar" }); });
    b.appendChild(el("div", { "class": "t-acoes" }, [seguir]));
    window.setTimeout(function () { seguir.focus(); }, 0);
    return b;
  }

  function anexaRetorno(t) {
    var c = S.cartao;
    c.classList.add("t-respondido");
    Array.prototype.forEach.call(c.querySelectorAll(".t-acoes"), function (x) {
      x.remove();
    });
    Array.prototype.forEach.call(c.querySelectorAll("button, input"), function (x) {
      x.disabled = true;
    });
    var r = montaRetorno(t);
    c.appendChild(r);
    S.inicio = performance.now();
    if (r.scrollIntoView) r.scrollIntoView({ block: "nearest" });
  }

  /* Sem cartão na tela — a página foi aberta numa sessão que estava
   * parada num retorno —, ele aparece sozinho. */
  DESENHA["retorno"] = function (c, t) { c.appendChild(montaRetorno(t)); };

  DESENHA["voce_disse"] = function (c, t) {
    c.appendChild(cabeca("Uma ideia para conferir"));
    c.appendChild(p("t-rotulo", "Você disse:"));
    c.appendChild(el("blockquote", { "class": "t-fala", texto: t.crenca }));

    if (!t.previsao) {
      c.appendChild(p("t-frase", "Vamos ver o que a máquina diz sobre isso."));
      c.appendChild(el("div", { "class": "t-acoes" }, [
        botao("Ver a resposta da máquina", function () {
          age({ acao: "continuar" });
        })
      ]));
      return;
    }
    /* Onde a prova é o que o compilador DIZ, a pessoa se compromete
     * antes de ver. */
    c.appendChild(p("t-frase", "Antes de ver a resposta da máquina, leia este trecho:"));
    c.appendChild(bloco(t.programa));
    c.appendChild(p("t-pede", t.previsao.pergunta));
    var escolha = null;
    var ver = botao("Ver a resposta da máquina", function () {
      age({ acao: "responder", escolha: escolha });
    });
    ver.disabled = true;
    /* Empilhadas, como as alternativas de uma pergunta: a previsão da
     * escada é uma frase, e não um "Sim" ou "Não". */
    c.appendChild(grupo("opcoes", "opcao", t.previsao.opcoes, function (i) {
      escolha = i;
      ver.disabled = false;
    }));
    c.appendChild(el("div", { "class": "t-acoes" }, [ver]));
  };

  DESENHA["maquina"] = function (c, t) {
    /* Sem demonstração exibível a tela NÃO diz que a máquina respondeu:
     * mostra o código e a ideia, e só. */
    c.appendChild(cabeca(t.tem_prova ? "A máquina respondeu"
                                     : "O que o código mostra"));
    c.appendChild(bloco(t.programa));
    if (t.tem_prova) {
      if (t.nao_compila) {
        c.appendChild(p("t-caixa", "O compilador recusou este programa: ele não compila."));
      } else if (t.avisa) {
        c.appendChild(p("t-rotulo", "O compilador reclamou:"));
        c.appendChild(bloco(t.avisa, "terminal"));
      } else {
        c.appendChild(p("t-rotulo", "Saída:"));
        c.appendChild(bloco(t.espera, "terminal"));
      }
      if (t.ambiente) c.appendChild(p("nota", t.ambiente));
      if (t.previu !== null && t.previu !== undefined) {
        /* Quem julga a previsão é o servidor. Sem julgamento a tela só
         * repete o que a pessoa disse. */
        var bateu = t.previu_certo === true ? "Foi o que a máquina fez."
                  : t.previu_certo === false ? "A máquina fez outra coisa."
                  : "";
        c.appendChild(el("div", {
          "class": "t-previu" + (t.previu_certo === true ? " ok"
                                 : t.previu_certo === false ? " nao" : "")
        }, [
          p("t-rotulo", "A sua previsão:"),
          p("t-frase", "“" + t.previu + "”"),
          bateu ? p("t-veredito", bateu) : null
        ]));
      }
      if (t.afirma) {
        c.appendChild(p("t-rotulo", "O que isto mostra:"));
        c.appendChild(p("t-frase", t.afirma));
      }
    }
    c.appendChild(p("t-rotulo", "A ideia que fica de pé:"));
    c.appendChild(p("ideia", t.premissa_texto));
    if (t.apoio && t.apoio.length) {
      c.appendChild(p("t-rotulo", "Ela se apoia nestas, pelas quais você já passou:"));
      c.appendChild(el("ul", { "class": "apoio" }, t.apoio.map(function (a) {
        return el("li", { texto: a.texto });
      })));
    }
    c.appendChild(el("div", { "class": "t-acoes" }, [
      botao("Treinar esta ideia", function () { age({ acao: "continuar" }); })
    ]));
  };

  DESENHA["revisao"] = function (c, t) {
    var continuar = el("div", { "class": "t-acoes" }, [
      botao("Continuar", function () { age({ acao: "continuar" }); })
    ]);
    if (t.cena && window.Cena) {
      /* A cena traz o código com a linha que roda marcada, e a tela do
       * programa: toma o lugar dos dois blocos (docs/interface.md, 8). Em
       * tela larga fica ao lado do texto, sem rolagem. */
      var texto = el("div", { "class": "t-lado-texto" }, [cabeca("Vamos rever")]);
      t.frases.forEach(function (f) { texto.appendChild(p("t-frase", f)); });
      texto.appendChild(continuar);
      c.appendChild(el("div", { "class": "t-lado-a-lado" },
                       [texto, Cena.desenha(t.cena, t.codigo)]));
      return;
    }
    c.appendChild(cabeca("Vamos rever"));
    t.frases.forEach(function (f) { c.appendChild(p("t-frase", f)); });
    c.appendChild(bloco(t.codigo));
    if (t.saida) {
      c.appendChild(p("t-rotulo", "A máquina imprime:"));
      c.appendChild(bloco(t.saida, "terminal"));
    }
    c.appendChild(continuar);
  };

  /* O FECHAMENTO. Antes da lista ideia por ideia, o que a sessão achou
   * nesta pessoa: as ideias erradas e se foram corrigidas, as lacunas e
   * em que passos, e o que já estava firme. É o resumo que o Rafael
   * pediu — e é o que o sistema existe para dizer. */
  function grupoDoSumario(titulo, classe, itens, monta) {
    if (!itens.length) return null;
    var caixa = el("section", { "class": "t-sumario " + classe });
    caixa.appendChild(el("h3", { texto: titulo + " (" + itens.length + ")" }));
    var ul = el("ul", {});
    itens.forEach(function (x) { ul.appendChild(monta(x)); });
    caixa.appendChild(ul);
    return caixa;
  }

  function desenhaSumario(c, s) {
    var blocos = [
      grupoDoSumario("Ideias erradas encontradas", "t-ideia-errada",
                     s.ideias_erradas, function (x) {
        var estado = x.corrigida ? "corrigida nesta sessão" : "ainda em aberto";
        if (x.voltou) estado += ", e voltou na reconferência do fim";
        return el("li", {}, [
          el("blockquote", { "class": "t-fala", texto: x.crenca }),
          p("nota", "Situação: " + estado + "."),
          p("nota", "A ideia que fica de pé: " + x.texto)
        ]);
      }),
      grupoDoSumario("Lacunas", "t-lacuna", s.lacunas, function (x) {
        var li = el("li", {}, [p("frase", x.texto)]);
        if (x.passos.length) {
          li.appendChild(p("nota", "Você tropeçou " +
                           (x.passos.length === 1 ? "neste passo:" : "nestes passos:")));
          li.appendChild(el("ul", { "class": "apoio" }, x.passos.map(function (f) {
            return el("li", { texto: f });
          })));
        } else {
          li.appendChild(p("nota", "Você subiu os passos sem tropeçar."));
        }
        li.appendChild(p("nota", x.fechou ? "Situação: aprendida pelos passos."
                                          : "Situação: ainda em aberto."));
        return li;
      }),
      grupoDoSumario("Já estava firme", "t-firme", s.firmes, function (x) {
        return el("li", { texto: x.texto });
      }),
      grupoDoSumario("Ficou em aberto", "t-lacuna", s.em_aberto, function (x) {
        return el("li", { texto: x.texto });
      })
    ];
    blocos.forEach(function (b) { if (b) c.appendChild(b); });
  }

  DESENHA["mapa"] = function (c, t) {
    c.appendChild(el("h2", { texto: "O que esta sessão encontrou" }));
    c.appendChild(p("nota", "Isto fala desta sessão. Manter com o tempo pede voltar ao assunto em outros dias."));
    desenhaSumario(c, t.sumario);
    c.appendChild(el("h3", { "class": "t-sub", texto: "Ideia por ideia" }));
    var lista = el("div", { "class": "mapa" });
    t.premissas.forEach(function (x) {
      var classe = x.resultado === "em_aberto" ? " t-aberto" : " t-bem";
      var corpo = el("div", {}, [p("frase", x.texto)]);
      corpo.appendChild(el("span", { "class": "t-selo",
                                     texto: RESULTADO[x.resultado] || x.resultado }));
      if (x.reconferencia) {
        corpo.appendChild(el("span", {
          "class": "t-selo",
          texto: "no fim: " + (RECONFERENCIA[x.reconferencia] || x.reconferencia)
        }));
      }
      if (x.trabalho === "lacuna") {
        corpo.appendChild(p("nota", "Passos certos: " + x.degrau +
                            " de " + x.degraus + "."));
        (x.tropecos || []).forEach(function (tr) {
          corpo.appendChild(p("nota", "Tropeçou em: " + tr.texto));
        });
      }
      if (x.crenca) corpo.appendChild(p("nota", "A ideia corrigida: “" + x.crenca + "”"));
      (x.apareceu || []).forEach(function (fala) {
        corpo.appendChild(p("nota", "Também apareceu: “" + fala + "”"));
      });
      var detalhe = el("details", {}, [
        el("summary", { texto: "Ver a explicação" }),
        corpoDaExplicacao({ frases: x.frases, codigo: x.codigo }, x.no)
      ]);
      corpo.appendChild(detalhe);
      lista.appendChild(el("article", {
        "class": "premissa" + classe,
        title: x.telas + (x.telas === 1 ? " tela" : " telas")
      }, [el("span", { "class": "id", texto: x.no }), corpo]));
    });
    c.appendChild(lista);
    c.appendChild(el("div", { "class": "t-acoes" }, [
      NO_PORTAL ? el("a", { "class": "btn", href: "/", texto: "Voltar aos tópicos",
                            style: "text-decoration:none" }) : null,
      botao("Fazer de novo", function () { recomeca(); }, "btn-topo")
    ]));
  };

  /* Uma sessão nova, do zero: o que o navegador guardava do tópico sai,
   * para reabrir a página não voltar à sessão de antes. */
  function recomeca() {
    if (GUARDA) Progresso.apaga(TOPICO);
    abre("");
  }

  /* A sessão de quem abriu SEM código e fechou a página: o navegador
   * guardou o número, e o servidor devolve a tela em que ela estava. Se
   * ele não a conhece mais, abre outra; se o conteúdo mudou, a frase
   * dele vai para a tela (docs/trilha.md, 6.12). */
  async function retoma(sessao) {
    $("perdida").classList.add("oculto");
    $("palco").classList.remove("oculto");
    var r = await pede("/sessoes/" + sessao + "/retoma", {});
    if (r.status === 200) {
      S.sessao = r.json.sessao;
      S.codigo = "";
      recebe(r.json);
      return;
    }
    if (r.status === 410) { perdeu(r.json && r.json.detail); return; }
    if (r.status === 0) {
      perdeu("O servidor não respondeu. Confira se o sistema está ligado e tente de novo.");
      return;
    }
    recomeca();
  }

  /* ------------------------------------------------------------ começo */

  function codigoDaURL() {
    var m = /[?&]codigo=([^&]+)/.exec(window.location.search);
    return m ? decodeURIComponent(m[1]) : "";
  }

  $("btn-recomecar").addEventListener("click", function () { recomeca(); });
  if (!NO_PORTAL) $("lnk-topicos").hidden = true;

  /* As figuras são por tópico: id de premissa se repete entre tópicos. */
  fetch(BASE + "/saude").then(function (r) { return r.json(); })
    .then(function (s) {
      if (s && s.topico && window.Figuras) window.Figuras.topico(s.topico);
      if (s && s.titulo) {
        document.title = "Structura — " + s.titulo;
        $("topico-nome").textContent = s.titulo;
      }
    })
    .catch(function () { /* sem saúde, a sessão ainda abre */ });

  /* Abrir: o código da URL vale primeiro. Sem ele, o que o navegador
   * guardou deste tópico — o código com que a pessoa abriu, ou o número
   * da sessão de quem abriu sem código. Sem nada guardado, uma nova. */
  (function () {
    var codigo = codigoDaURL();
    var guardado = (!codigo && GUARDA) ? Progresso.le(TOPICO) : null;
    if (guardado && guardado.codigo) abre(guardado.codigo);
    else if (guardado && guardado.sessao) retoma(guardado.sessao);
    else abre(codigo);
  })();
})();
