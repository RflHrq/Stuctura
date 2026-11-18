/* O que o navegador lembra da trilha, por tópico (docs/trilha.md, 6.12;
   docs/interface.md, seção 7).

   Chave "structura-trilha-<tópico>", com:
     sessao   o número da sessão de quem abriu SEM código — é o que deixa
              voltar à tela em que estava depois de fechar a página;
     codigo   o código, quando a pessoa informou um (aí quem retoma é o
              próprio código, e o número não é guardado);
     feitas, total   quantas ideias do tópico já fecharam;
     fim      se a pessoa chegou ao fechamento.

   A trilha grava a cada resposta (anota); a página inicial lê para
   desenhar o caminho. O localStorage pode não existir ou lançar erro
   (janela anônima, armazenamento bloqueado): todo acesso fica em
   try/catch, e sem ele nada quebra — só não se lembra. Numa máquina
   compartilhada, o que fica é do navegador, e não da pessoa.

   Também carrega no Node, para os testes (mvp/test_progresso.py). */
(function (global) {
  "use strict";
  var PREFIXO = "structura-trilha-";

  function le(topico) {
    try {
      var cru = global.localStorage.getItem(PREFIXO + topico);
      if (!cru) return null;
      var d = JSON.parse(cru);
      if (!d || typeof d !== "object" || Array.isArray(d)) return null;
      return {
        sessao: typeof d.sessao === "string" ? d.sessao : "",
        codigo: typeof d.codigo === "string" ? d.codigo : "",
        feitas: Number(d.feitas) || 0,
        total: Number(d.total) || 0,
        fim: d.fim === true
      };
    } catch (e) {
      return null;
    }
  }

  function grava(topico, dados) {
    try {
      global.localStorage.setItem(PREFIXO + topico, JSON.stringify(dados));
    } catch (e) { /* sem armazenamento, segue */ }
  }

  function apaga(topico) {
    try { global.localStorage.removeItem(PREFIXO + topico); }
    catch (e) { /* sem armazenamento, segue */ }
  }

  /* A resposta do servidor (sessao, tela, progresso) e o código com que a
   * sessão abriu ("" sem código). */
  function anota(topico, resposta, codigo) {
    if (!topico || !resposta) return;
    var p = resposta.progresso || {};
    grava(topico, {
      sessao: codigo ? "" : String(resposta.sessao || ""),
      codigo: codigo || "",
      feitas: Number(p.feitas) || 0,
      total: Number(p.total) || 0,
      fim: !!(resposta.tela && resposta.tela.tipo === "mapa")
    });
  }

  global.Progresso = { le: le, grava: grava, apaga: apaga, anota: anota };
})(typeof window !== "undefined" ? window : this);
