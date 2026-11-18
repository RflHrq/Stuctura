"""As cenas (docs/interface.md, seção 8; docs/plano-cenas.md).

Uma cena por ideia, que anima o código da revisão linha a linha. Fica em
dados, no arquivo da escada, e o conferidor a confere contra o
compilador: a cena que mostra algo que o código não faz não entra.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
import yaml

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import confere_escada  # noqa: E402
import oraculo  # noqa: E402
from mvp import trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

D = carrega(topico="kc_00")
ARQUIVO = RAIZ / "dominio" / "escada_kc00.yaml"
tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(), reason="sem o compilador do oráculo")

CENA_B2 = {"atores": [{"nome": "idade", "tipo": "caixa", "de": "int"}],
           "passos": [{"linha": 1, "faz": [{"cria": "idade"}]},
                      {"linha": 2, "faz": [{"guarda": {"em": "idade", "valor": 20}}]}]}


def _escadas_com(tmp_path, no, cena):
    cru = yaml.safe_load(ARQUIVO.read_text(encoding="utf-8"))
    cru[no]["cena"] = cena
    arq = tmp_path / "escada_kc00.yaml"
    arq.write_text(yaml.safe_dump(cru, allow_unicode=True, sort_keys=False),
                   encoding="utf-8")
    return arq


def _problemas(tmp_path, no, cena):
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        trilha_escada.le(_escadas_com(tmp_path, no, cena), D)
    return str(erro.value)


def test_a_cena_e_lida_com_atores_e_passos(tmp_path):
    esc = trilha_escada.le(_escadas_com(tmp_path, "B2", CENA_B2), D)
    cena = esc["B2"].cena
    assert [a.nome for a in cena.atores] == ["idade"]
    assert cena.atores[0].de == "int"
    assert [p.linha for p in cena.passos] == [1, 2]
    assert cena.passos[1].faz == (("guarda", ("idade", "20")),)


def test_toda_linha_tem_passo(tmp_path):
    cena = {"atores": CENA_B2["atores"], "passos": CENA_B2["passos"][:1]}
    assert "linha 2 sem passo" in _problemas(tmp_path, "B2", cena)


def test_passo_de_linha_que_nao_existe(tmp_path):
    cena = {"atores": CENA_B2["atores"],
            "passos": CENA_B2["passos"] + [{"linha": 9, "faz": [{"le": "idade"}]}]}
    assert "linha 9, que o código não tem" in _problemas(tmp_path, "B2", cena)


def test_ator_que_nao_existe(tmp_path):
    cena = {"atores": CENA_B2["atores"],
            "passos": [{"linha": 1, "faz": [{"cria": "idade"}]},
                       {"linha": 2, "faz": [{"guarda": {"em": "nota", "valor": 20}}]}]}
    assert "ator desconhecido: nota" in _problemas(tmp_path, "B2", cena)


def test_acao_que_nao_existe(tmp_path):
    cena = {"atores": CENA_B2["atores"],
            "passos": [{"linha": 1, "faz": [{"cria": "idade"}]},
                       {"linha": 2, "faz": [{"pinta": "idade"}]}]}
    assert "ação desconhecida: pinta" in _problemas(tmp_path, "B2", cena)


def test_ler_caixa_sem_valor_e_o_que_o_topico_ensina_a_nao_fazer(tmp_path):
    cena = {"atores": CENA_B2["atores"],
            "passos": [{"linha": 1, "faz": [{"cria": "idade"}]},
                       {"linha": 2, "faz": [{"le": "idade"}]}]}
    assert "lê idade, que não tem valor" in _problemas(tmp_path, "B2", cena)


def test_a_cena_nao_muda_a_assinatura(tmp_path):
    """A assinatura protege a reexecução das sessões (as entradas são
    posições de peças); a cena não muda entrada nenhuma."""
    sem = trilha_escada.le(ARQUIVO, D)
    com = trilha_escada.le(_escadas_com(tmp_path, "B2", CENA_B2), D)
    assert com["B2"].cena is not None
    assert trilha_escada.assinatura(com) == trilha_escada.assinatura(sem)


# --------------------------------------------------------------------------
# A conferência contra o compilador
# --------------------------------------------------------------------------

CENA_B3 = {"atores": [{"nome": "idade", "tipo": "caixa", "de": "int"}],
           "passos": [{"linha": 1, "faz": [{"cria": "idade"}]},
                      {"linha": 2, "faz": [{"guarda": {"em": "idade", "valor": 20}}]},
                      {"linha": 3, "faz": [{"le": "idade"}, {"mostra": "20"}]}]}


def _confere(tmp_path, no, cena):
    esc = trilha_escada.le(_escadas_com(tmp_path, no, cena), D)
    return [p for p in confere_escada.confere(esc) if "/cena" in p]


@tem_gcc
def test_a_cena_certa_confere(tmp_path):
    assert _confere(tmp_path, "B3", CENA_B3) == []


@tem_gcc
def test_a_cena_que_diz_outro_valor_e_acusada(tmp_path):
    import copy
    errada = copy.deepcopy(CENA_B3)
    errada["passos"][1]["faz"][0]["guarda"]["valor"] = 21
    problemas = _confere(tmp_path, "B3", errada)
    assert any("idade == 21" in p for p in problemas), problemas


@tem_gcc
def test_a_cena_que_mostra_outra_saida_e_acusada(tmp_path):
    import copy
    errada = copy.deepcopy(CENA_B3)
    errada["passos"][2]["faz"][1]["mostra"] = "0"
    problemas = _confere(tmp_path, "B3", errada)
    assert any("mostra" in p for p in problemas), problemas


# --------------------------------------------------------------------------
# As cenas do kc_00 e o que o servidor manda
# --------------------------------------------------------------------------

def test_toda_ideia_do_kc_00_tem_cena():
    esc = trilha_escada.le(ARQUIVO, D)
    assert [no for no in D.ordem if esc[no].cena is None] == []


def test_a_cena_vai_em_json_para_a_tela():
    esc = trilha_escada.le(ARQUIVO, D)
    j = trilha_escada.cena_json(esc["B3"].cena)
    assert j["atores"] == [{"nome": "idade", "tipo": "caixa", "de": "int"}]
    assert j["passos"][1] == {"linha": 2, "faz": [
        {"acao": "guarda", "em": "idade", "valor": "20"}]}
    assert j["passos"][2]["faz"][1] == {"acao": "mostra", "texto": "20"}


def test_a_revisao_e_a_explicacao_levam_a_cena():
    from mvp import trilha
    esc = trilha_escada.le(ARQUIVO, D)
    e = trilha.inicia(D, esc, semente="cena").estado
    t = trilha._revisao(esc, e, "B3", [])
    assert t.estado.tela.dados["cena"] == trilha_escada.cena_json(esc["B3"].cena)
    assert trilha._explicacao(D, esc, "B3")["cena"] == t.estado.tela.dados["cena"]


# --------------------------------------------------------------------------
# O desenhista (mvp/web/cena.js)
# --------------------------------------------------------------------------

from mvp.test_interface import (_roda_node, contraste, cores_do_tema,  # noqa: E402
                                tem_node)

WEB = RAIZ / "web"


def _estados(no):
    import json
    j = trilha_escada.cena_json(trilha_escada.le(ARQUIVO, D)[no].cena)
    programa = """
    global.window = global;
    require(require("path").join(WEB, "cena.js"));
    console.log(JSON.stringify(global.Cena.estados(%s)));
    """ % json.dumps(j)
    return json.loads(_roda_node(programa))


@tem_node
def test_os_estados_comecam_vazios_e_seguem_os_passos():
    e = _estados("B4")
    assert len(e) == 5                       # o começo, e um por passo
    assert e[0]["caixas"] == [] and e[0]["linha"] == 0
    idade = {c["nome"]: c for c in e[2]["caixas"]}["idade"]
    assert idade["valor"] == "20" and e[2]["linha"] == 2
    assert {c["nome"]: c for c in e[3]["caixas"]}["idade"]["valor"] == "21"
    assert e[4]["saida"] == ["21"]


@tem_node
def test_cada_passo_tem_uma_frase_para_quem_nao_ve():
    e = _estados("B4")
    assert "Linha 1" in e[1]["descricao"] and "cria a caixa idade" in e[1]["descricao"]
    assert "o 20 que estava lá sai" in e[3]["descricao"]
    assert "mostra 21 na tela" in e[4]["descricao"]


@tem_node
def test_a_caixa_sem_valor_aparece_sem_valor():
    e = _estados("B1")
    assert [(c["nome"], c["valor"]) for c in e[2]["caixas"]] == [
        ("idade", None), ("turma", None)]


def test_as_cores_da_cena_passam_no_contraste():
    for tema in ("claro", "escuro"):
        c = cores_do_tema(tema)
        for frente, fundo in (("bilhete-tinta", "bilhete"), ("tinta2", "papel"),
                              ("tinta", "papel"), ("tinta", "acento-fundo"),
                              ("tinta", "destaque-fundo")):
            assert contraste(c[frente], c[fundo]) >= 4.5, (tema, frente, fundo)


def test_a_trilha_desenha_a_cena_na_revisao_e_no_painel():
    html = (WEB / "trilha.html").read_text(encoding="utf-8")
    assert "/web/cena.js?v=" in html and html.index("cena.js") < html.index("trilha.js")
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    assert js.count("Cena.desenha(") >= 2
    assert "t.cena" in js and "x.cena" in js


def test_reduzir_movimento_mostra_o_estado_final():
    js = (WEB / "cena.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in js
    assert 'aria-live' in js


def test_o_botao_da_cena_nao_se_chama_continuar():
    """"Continuar" é o botão da sessão, logo abaixo da cena."""
    js = (WEB / "cena.js").read_text(encoding="utf-8")
    assert '"Continuar"' not in js and '"Retomar"' in js
