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
    assert "/web/trilha.js?v=20261113" in r.text
    assert cliente.get("/web/trilha.js").status_code == 200
    assert cliente.get("/web/trilha.css").status_code == 200


def test_os_assets_da_pagina_sao_versionados():
    html = _html()
    for nome in ("trilha.js", "trilha.css", "figuras.js", "style.css"):
        assert re.search(r"/web/%s\?v=2026111[23]" % re.escape(nome), html), nome
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


def test_o_cliente_desenha_as_cinco_formas_e_os_oito_tipos_de_tela():
    js = _js()
    for nome in trilha_escada.FORMAS + (
            "entrada", "pergunta", "degrau", "retorno", "voce_disse",
            "maquina", "revisao", "mapa"):
        assert '"%s"' % nome in js, nome


def test_o_cliente_manda_as_sete_acoes():
    js = _js()
    for acao in trilha.ACOES:
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
    """Review Focus 2: reinício do servidor com a página aberta."""
    assert "404" in _js() and "Recomeçar" in _html()
    assert "btn-recomecar" in _js()


def test_o_cliente_nao_manda_duas_vezes():
    """Review Focus 1: enquanto um pedido está no ar, os botões não agem."""
    assert "ocupado" in _js()


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
