"""As telas da trilha, conferidas sem navegador.

O que dá para garantir lendo os arquivos: a página existe e é servida,
os assets são versionados (a porta 8010 já serviu outras páginas, e o
navegador guarda as antigas), o cliente lê cada campo que o servidor
monta, sabe desenhar as cinco formas de exercício e os oito tipos de
tela, trata a sessão perdida, e não escreve conteúdo — toda frase de
premissa e de crença vem do servidor.

O resto — se a tela desenha direito, se o toque monta a linha — é
conferência no navegador, e está no último passo do plano.
"""

from __future__ import annotations

import pathlib
import re
import sys

from fastapi.testclient import TestClient

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

from trilha_alunos import PERSONAS, caminha  # noqa: E402

from mvp import trilha, trilha_app, trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "dominio" / "escada_kc00.yaml", D)
WEB = RAIZ / "web"


def _js():
    return (WEB / "trilha.js").read_text(encoding="utf-8")


def _html():
    return (WEB / "trilha.html").read_text(encoding="utf-8")


def test_a_raiz_serve_a_pagina_da_trilha(tmp_path):
    cliente = TestClient(trilha_app.cria_app(D, ESC, tmp_path / "t.jsonl"))
    r = cliente.get("/")
    assert r.status_code == 200
    assert "/web/trilha.js?v=20261116" in r.text
    assert cliente.get("/web/trilha.js").status_code == 200
    assert cliente.get("/web/trilha.css").status_code == 200


def test_os_assets_da_pagina_sao_versionados():
    html = _html()
    for nome in ("trilha.js", "trilha.css", "figuras.js", "style.css",
                 "tema.js", "tema.css", "marca.svg"):
        assert re.search(r"/web/%s\?v=20261116" % re.escape(nome), html), nome
    # Nenhum asset sem versão: o navegador guardaria o antigo.
    soltos = re.findall(r"""(?:src|href)="(/web/[^"?]+)\"""", html)
    assert soltos == []


def test_o_cliente_le_todos_os_campos_que_o_servidor_monta():
    """Campo que o servidor manda e ninguém lê é seção que some da tela
    sem ninguém perceber — o motor atual já passou por isso duas vezes."""
    js = _js()
    chaves = set()
    for persona in PERSONAS:
        for modo in trilha.MODOS:
            for t in caminha(D, ESC, persona, modo).telas:
                chaves |= set(t.json())
    assert len(chaves) > 40
    faltam = sorted(k for k in chaves
                    if not re.search(r"\b%s\b" % re.escape(k), js))
    assert faltam == []


def test_o_cliente_le_o_que_vem_dentro_do_mapa_e_do_progresso():
    js = _js()
    mapa = caminha(D, ESC, "crente_aprende").telas[-1].json()
    for chave in mapa["premissas"][0]:
        assert re.search(r"\b%s\b" % re.escape(chave), js), chave
    for chave in ("progresso", "feitas", "explicacao", "simples", "veredito",
                  "sessao"):
        assert re.search(r"\b%s\b" % chave, js), chave
    # O ritmo da sessão vem na resposta: quem reabre a página com o código
    # não passou pela tela de entrada, e os ajustes precisam saber o que
    # marcar. O modo também vinha, e a página o lia; desde 13/11/2026 ela
    # não oferece mais a escolha (mvp/test_trilha_diagnostico.py).
    assert "j.ritmo" in js and "j.modo" not in js
    # O fechamento: o que vem dentro do sumário também é lido.
    for chave in mapa["sumario"]:
        assert re.search(r"\b%s\b" % re.escape(chave), js), chave


def test_o_cliente_desenha_as_cinco_formas_e_os_oito_tipos_de_tela():
    js = _js()
    for nome in trilha_escada.FORMAS + (
            "entrada", "pergunta", "degrau", "retorno", "voce_disse",
            "maquina", "revisao", "mapa"):
        assert '"%s"' % nome in js, nome


def test_o_cliente_manda_as_acoes_que_a_pagina_oferece():
    """ERAM as sete do motor. A sétima, `modo`, trocava entre começar pela
    pergunta e começar pelos passos; a página não oferece mais essa
    escolha, e o motor guarda a ação sem ninguém para mandá-la."""
    js = _js()
    assert "modo" in trilha.ACOES
    for acao in trilha.ACOES:
        if acao == "modo":
            assert 'acao: "modo"' not in js and '"modo"' not in js
        else:
            assert '"%s"' % acao in js, acao


def test_o_cliente_conhece_todo_veredito_resultado_e_reconferencia():
    js = _js()
    vereditos = {t.dados["veredito"] for p in PERSONAS for m in trilha.MODOS
                 for t in caminha(D, ESC, p, m).telas if t.tipo == "retorno"}
    for nome in (vereditos | set(trilha.RESULTADOS)
                 | {trilha.ASSIMILOU, trilha.NAO_SE_MANTEVE,
                    trilha.A_IDEIA_VOLTOU, trilha.SEM_QUESTAO}):
        assert re.search(r"\b%s\b" % nome, js), nome


def test_o_cliente_trata_a_sessao_perdida():
    """Review Focus 2: reinício do servidor com a página aberta.

    Ler o arquivo não prova que a tela funciona — isso foi visto no
    navegador —, mas prova que o caminho existe: o 404 de uma ação chama
    a função que troca a tela pela mensagem, e a mensagem tem o botão.
    """
    js, html = _js(), _html()
    assert re.search(r"r\.status === 404\)\s*\{\s*perdeu\(\)", js)
    assert re.search(r"function perdeu\(", js)
    assert 'id="perdida"' in html and "Recomeçar" in html
    assert re.search(r'\$\("btn-recomecar"\)\.addEventListener', js)


def test_o_cliente_nao_manda_duas_vezes():
    """Review Focus 1: enquanto um pedido está no ar, os botões não agem.

    A proteção de verdade é do servidor, que recusa o pedido de uma tela
    que já passou (`mvp/test_trilha_revisao.py`). Aqui se confere a
    metade do cliente: a guarda na entrada de `age`, e a volta dela.
    """
    js = _js()
    assert re.search(r"if \(S\.ocupado[^)]*\) return;", js)
    assert "S.ocupado = true" in js and "S.ocupado = false" in js


def test_o_cliente_diz_de_que_tela_e_o_pedido():
    """E redesenha quando o servidor diz que a tela já mudou."""
    js = _js()
    assert "corpo.passo = S.passo" in js
    assert "S.passo = j.passo" in js
    assert re.search(r"r\.status === 409 && r\.json && r\.json\.tela", js)


def test_na_reconferencia_o_botao_da_explicacao_nao_aparece():
    js = _js()
    assert re.search(
        r't\.papel === "reconferencia" \? null : botaoDaExplicacao\(\)', js)
    # Duas ocorrências: a definição e ESTA chamada. Nenhuma tela chama o
    # botão direto, sem passar pela pergunta do papel.
    assert js.count("botaoDaExplicacao()") == 2
    assert js.count("explicacaoSe(t)") == 3      # a definição e duas telas


def test_o_tempo_mandado_tem_teto():
    """Uma página esquecida aberta não pode travar a sessão."""
    js = _js()
    assert "Math.min(ms, LIMITE_MS)" in js


def test_o_cliente_nao_escreve_conteudo():
    js, html = _js(), _html()
    textos = [n.simples for n in D.nos.values()]
    textos += [c.afirma for c in D.crencas.values()]
    textos += [f for e in ESC.values() for g in e.degraus for f in g.frases]
    for texto in textos:
        assert texto not in js and texto not in html, texto


def test_a_base_da_pagina_sai_do_caminho():
    """Dentro do portal a trilha mora em /trilha/kc_00/, e as rotas dela
    ficam debaixo desse caminho."""
    js = _js()
    assert '"/trilha/"' in js and "location.pathname" in js
