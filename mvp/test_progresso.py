"""O navegador lembra a trilha (docs/trilha.md, 6.12; docs/interface.md, 7).

`mvp/web/progresso.js` guarda, por tópico: o número da sessão de quem
abriu sem código (ou o código), quantas ideias fecharam e se a pessoa
chegou ao fechamento. A trilha grava a cada resposta; a página inicial
lê para desenhar o caminho. O localStorage pode não existir ou lançar
erro — sem ele, nada quebra, só não se lembra.
"""

from __future__ import annotations

import json
import pathlib

from mvp.test_interface import _roda_node, tem_node

WEB = pathlib.Path(__file__).resolve().parent / "web"

PAGINA = """
const guardados = {};
const quebrado = %s;
global.window = global;
Object.defineProperty(global, "localStorage", { get() {
    if (quebrado) throw new Error("bloqueado");
    return { getItem: (k) => (k in guardados ? guardados[k] : null),
             setItem: (k, v) => { guardados[k] = String(v); },
             removeItem: (k) => { delete guardados[k]; } }; } });
require(require("path").join(WEB, "progresso.js"));
const P = global.Progresso;
"""


def _roda(corpo: str, quebrado: bool = False):
    return json.loads(_roda_node(PAGINA % json.dumps(quebrado) + corpo))


@tem_node
def test_sem_nada_guardado_le_nada():
    assert _roda("console.log(JSON.stringify(P.le('kc_02')));") is None


@tem_node
def test_quem_abriu_sem_codigo_guarda_o_numero_da_sessao():
    r = _roda("""
    P.anota('kc_02', {sessao: 'a1b2c3d4e5f6', tela: {tipo: 'pergunta'},
                      progresso: {feitas: 2, total: 6}}, '');
    console.log(JSON.stringify(P.le('kc_02')));""")
    assert r["sessao"] == "a1b2c3d4e5f6" and r["codigo"] == ""
    assert (r["feitas"], r["total"], r["fim"]) == (2, 6, False)


@tem_node
def test_quem_abriu_com_codigo_guarda_o_codigo_e_nao_o_numero():
    r = _roda("""
    P.anota('kc_02', {sessao: 'P01', tela: {tipo: 'mapa'},
                      progresso: {feitas: 6, total: 6}}, 'P01');
    console.log(JSON.stringify(P.le('kc_02')));""")
    assert r["codigo"] == "P01" and r["sessao"] == ""
    assert r["fim"] is True


@tem_node
def test_apagar_esquece_so_aquele_topico():
    r = _roda("""
    P.anota('kc_02', {sessao: 'a1b2c3d4e5f6', tela: {tipo: 'pergunta'},
                      progresso: {feitas: 1, total: 6}}, '');
    P.anota('kc_03', {sessao: 'b1b2c3d4e5f6', tela: {tipo: 'pergunta'},
                      progresso: {feitas: 1, total: 6}}, '');
    P.apaga('kc_02');
    console.log(JSON.stringify([P.le('kc_02'), P.le('kc_03').sessao]));""")
    assert r == [None, "b1b2c3d4e5f6"]


@tem_node
def test_o_que_foi_guardado_estragado_vale_como_nada():
    r = _roda("""
    guardados['structura-trilha-kc_02'] = '{isto nao e json';
    guardados['structura-trilha-kc_03'] = '[1, 2]';
    console.log(JSON.stringify([P.le('kc_02'), P.le('kc_03')]));""")
    assert r == [None, None]


@tem_node
def test_sem_armazenamento_nada_quebra():
    r = _roda("""
    P.anota('kc_02', {sessao: 'a1b2c3d4e5f6', tela: {tipo: 'pergunta'},
                      progresso: {feitas: 1, total: 6}}, '');
    P.apaga('kc_02');
    console.log(JSON.stringify(P.le('kc_02')));""", quebrado=True)
    assert r is None


def test_a_trilha_carrega_o_progresso_antes_do_seu_script():
    html = (WEB / "trilha.html").read_text(encoding="utf-8")
    assert "/web/progresso.js?v=" in html
    assert html.index("progresso.js") < html.index("trilha.js")


def test_a_trilha_grava_retoma_e_esquece():
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    # grava a cada resposta, com o código com que a sessão abriu
    assert "Progresso.anota(TOPICO, j, S.codigo)" in js
    # ao abrir sem código: o código guardado, ou o número guardado
    assert '"/sessoes/" + sessao + "/retoma"' in js
    # sessão que não volta, e "fazer de novo", esquecem o guardado
    assert js.count("Progresso.apaga(TOPICO)") >= 2
