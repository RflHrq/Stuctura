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


def _arquivo(topico):
    return RAIZ / "dominio" / ("escada_%s.yaml" % topico.replace("_", ""))


def _escadas_com(tmp_path, no, cena, topico="kc_00"):
    cru = yaml.safe_load(_arquivo(topico).read_text(encoding="utf-8"))
    cru[no]["cena"] = cena
    arq = tmp_path / _arquivo(topico).name
    arq.write_text(yaml.safe_dump(cru, allow_unicode=True, sort_keys=False),
                   encoding="utf-8")
    return arq


def _problemas(tmp_path, no, cena, topico="kc_00"):
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        trilha_escada.le(_escadas_com(tmp_path, no, cena, topico),
                         carrega(topico=topico))
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


def _confere(tmp_path, no, cena, topico="kc_00"):
    esc = trilha_escada.le(_escadas_com(tmp_path, no, cena, topico),
                           carrega(topico=topico))
    return [p for p in confere_escada.confere({no: esc[no]}) if "/cena" in p]


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
# A fatia 4: a bancada (função), a fileira (array) e o bloco alugado
# (malloc). docs/plano-cenas.md, "Fatia 4".
# --------------------------------------------------------------------------

import copy  # noqa: E402

# kc_06 B1: void zera(int n) { n = 0; } — a cópia muda, idade não.
CENA_ZERA = {
    "atores": [{"nome": "idade", "tipo": "caixa", "de": "int"},
               {"nome": "zera", "tipo": "bancada", "de": "void zera(int n)"},
               {"nome": "n", "tipo": "caixa", "de": "int"}],
    "passos": [
        {"linha": 3, "faz": [{"cria": "idade"}]},
        {"linha": 5, "faz": [{"guarda": {"em": "idade", "valor": 15}}]},
        {"linha": 6, "faz": [{"le": "idade"}, {"chama": "zera"}, {"cria": "n"},
                             {"guarda": {"em": "n", "valor": 15}}]},
        {"linha": 1, "faz": [{"guarda": {"em": "n", "valor": 0}}]},
        {"linha": 6, "faz": [{"volta": "zera"}]},
        {"linha": 7, "faz": [{"le": "idade"}, {"mostra": "15"}]}]}

# kc_01 B2: a mesma função chamada duas vezes, e o n nasce de novo.
CENA_CONTA = {
    "atores": [{"nome": "conta", "tipo": "bancada", "de": "int conta(void)"},
               {"nome": "n", "tipo": "caixa", "de": "int"}],
    "passos": [
        {"linha": 3, "faz": [{"chama": "conta"}]},
        {"linha": 1, "faz": [{"cria": "n"}, {"guarda": {"em": "n", "valor": 0}},
                             {"guarda": {"em": "n", "valor": 1}},
                             {"diz": "conta devolve 1"}]},
        {"linha": 3, "faz": [{"volta": "conta"}]},
        {"linha": 4, "faz": [{"chama": "conta"}]},
        {"linha": 1, "faz": [{"cria": "n"}, {"guarda": {"em": "n", "valor": 0}},
                             {"guarda": {"em": "n", "valor": 1}}]},
        {"linha": 4, "faz": [{"volta": "conta"}, {"mostra": "1"}]}]}

# kc_07 B1: a fileira.
CENA_NOTAS = {
    "atores": [{"nome": "notas", "tipo": "fileira", "de": "int", "tamanho": 3}],
    "passos": [
        {"linha": 1, "faz": [{"cria": "notas"},
                             {"guarda": {"em": "notas", "valor": [7, 8, 9]}}]},
        {"linha": 3, "faz": [{"le": "notas[2]"}, {"mostra": "9"}]}]}

# kc_08 B1: o bloco alugado com três int.
CENA_BLOCO = {
    "atores": [{"nome": "p", "tipo": "ponteiro", "de": "int *"},
               {"nome": "bloco", "tipo": "bloco", "de": "int", "tamanho": 3}],
    "passos": [
        {"linha": 1, "faz": [{"cria": "p"}]},
        {"linha": 3, "faz": [{"aluga": {"nome": "bloco", "para": "p"}}]},
        {"linha": 4, "faz": [{"segue": "p"}, {"guarda": {"em": "bloco[2]", "valor": 9}}]},
        {"linha": 5, "faz": [{"le": "bloco[2]"}, {"mostra": "9"}]},
        {"linha": 6, "faz": [{"devolve": "bloco"}]}]}

# kc_12 B1: a função de várias linhas, chamada duas vezes.
CENA_DOBRA = {
    "atores": [{"nome": "dobra", "tipo": "bancada", "de": "int dobra(void)"},
               {"nome": "n", "tipo": "caixa", "de": "int"}],
    "passos": [
        {"linha": 7, "faz": [{"chama": "dobra"}]},
        {"linha": 2, "faz": [{"cria": "n"}, {"guarda": {"em": "n", "valor": 3}}]},
        {"linha": 3, "faz": [{"le": "n"}, {"guarda": {"em": "n", "valor": 6}}]},
        {"linha": 4, "faz": [{"le": "n"}, {"diz": "dobra devolve 6"}]},
        {"linha": 7, "faz": [{"volta": "dobra"}]},
        {"linha": 8, "faz": [{"chama": "dobra"}]},
        {"linha": 2, "faz": [{"cria": "n"}, {"guarda": {"em": "n", "valor": 3}}]},
        {"linha": 3, "faz": [{"le": "n"}, {"guarda": {"em": "n", "valor": 6}}]},
        {"linha": 4, "faz": [{"le": "n"}]},
        {"linha": 8, "faz": [{"volta": "dobra"}, {"mostra": "6"}]}]}


def test_as_caixas_da_bancada_somem_na_volta(tmp_path):
    cena = copy.deepcopy(CENA_ZERA)
    cena["passos"][5]["faz"].insert(0, {"le": "n"})
    assert "linha 7: n não existe nesse ponto" in _problemas(
        tmp_path, "B1", cena, "kc_06")


def test_volta_de_outra_bancada_e_acusada(tmp_path):
    cena = copy.deepcopy(CENA_ZERA)
    cena["atores"].append({"nome": "outra", "tipo": "bancada", "de": "void outra(void)"})
    cena["passos"][4]["faz"] = [{"volta": "outra"}]
    assert "volta outra, que não é a bancada aberta" in _problemas(
        tmp_path, "B1", cena, "kc_06")


def test_a_linha_da_funcao_so_roda_dentro_da_bancada(tmp_path):
    cena = copy.deepcopy(CENA_ZERA)
    cena["passos"][2]["faz"] = [{"le": "idade"}]        # sem chamar
    cena["passos"][4]["faz"] = []
    assert "linha 1 é de zera" in _problemas(tmp_path, "B1", cena, "kc_06")


def test_a_cabeca_e_o_fecho_da_funcao_nao_pedem_passo(tmp_path):
    trilha_escada.le(_escadas_com(tmp_path, "B1", CENA_DOBRA, "kc_12"),
                     carrega(topico="kc_12"))


def test_a_fileira_nao_tem_caixa_fora_do_tamanho(tmp_path):
    cena = copy.deepcopy(CENA_NOTAS)
    cena["passos"][1]["faz"][0] = {"le": "notas[3]"}
    assert "notas[3] fora da fileira" in _problemas(tmp_path, "B1", cena, "kc_07")


def test_a_fileira_recebe_um_valor_por_caixa(tmp_path):
    cena = copy.deepcopy(CENA_NOTAS)
    cena["passos"][0]["faz"][1]["guarda"]["valor"] = [7, 8]
    assert "2 valores para 3 caixas" in _problemas(tmp_path, "B1", cena, "kc_07")


def test_o_texto_entra_na_fileira_de_char_com_o_zero_no_fim(tmp_path):
    cena = {"atores": [{"nome": "letras", "tipo": "fileira", "de": "char", "tamanho": 5},
                       {"nome": "c", "tipo": "ponteiro", "de": "char *"}],
            "passos": [{"linha": 1, "faz": [{"cria": "letras"},
                                            {"guarda": {"em": "letras", "texto": "casa"}}]},
                       {"linha": 2, "faz": [{"cria": "c"},
                                            {"aponta": {"de": "c", "para": "letras[0]"}}]},
                       {"linha": 4, "faz": [{"diz": "sizeof *c é 1: c aponta para um char"},
                                            {"mostra": "1"}]}]}
    esc = trilha_escada.le(_escadas_com(tmp_path, "B2", cena, "kc_11"),
                           carrega(topico="kc_11"))
    assert esc["B2"].cena.passos[0].faz[1] == (
        "guarda", ("letras", ("'c'", "'a'", "'s'", "'a'", "'\\0'")))


def test_seguir_o_bilhete_do_bloco_devolvido_e_acusado(tmp_path):
    cena = copy.deepcopy(CENA_BLOCO)
    cena["passos"][4]["faz"].append({"segue": "p"})
    assert "segue p, que aponta para um bloco devolvido" in _problemas(
        tmp_path, "B1", cena, "kc_08")


def test_a_cena_nao_termina_com_a_bancada_aberta(tmp_path):
    cena = copy.deepcopy(CENA_ZERA)
    cena["passos"][4]["faz"] = []
    assert "termina com a bancada de zera aberta" in _problemas(
        tmp_path, "B1", cena, "kc_06")


def test_a_cena_nova_vai_em_json(tmp_path):
    esc = trilha_escada.le(_escadas_com(tmp_path, "B1", CENA_BLOCO, "kc_08"),
                           carrega(topico="kc_08"))
    j = trilha_escada.cena_json(esc["B1"].cena)
    assert j["atores"][1] == {"nome": "bloco", "tipo": "bloco", "de": "int",
                              "tamanho": [3]}
    assert j["passos"][1]["faz"] == [{"acao": "aluga", "nome": "bloco", "para": "p"}]
    assert j["passos"][4]["faz"] == [{"acao": "devolve", "nome": "bloco"}]
    esc = trilha_escada.le(_escadas_com(tmp_path, "B1", CENA_NOTAS, "kc_07"),
                           carrega(topico="kc_07"))
    j = trilha_escada.cena_json(esc["B1"].cena)
    assert j["passos"][0]["faz"][1] == {"acao": "guarda", "em": "notas",
                                        "valor": ["7", "8", "9"]}


@tem_gcc
@pytest.mark.parametrize("topico, no, cena", [
    ("kc_06", "B1", CENA_ZERA), ("kc_01", "B2", CENA_CONTA),
    ("kc_07", "B1", CENA_NOTAS), ("kc_08", "B1", CENA_BLOCO),
    ("kc_12", "B1", CENA_DOBRA)])
def test_a_cena_certa_da_fatia_4_confere(tmp_path, topico, no, cena):
    assert _confere(tmp_path, no, cena, topico) == []


@tem_gcc
def test_o_valor_errado_dentro_da_funcao_e_acusado(tmp_path):
    errada = copy.deepcopy(CENA_ZERA)
    errada["passos"][3]["faz"][0]["guarda"]["valor"] = 1
    problemas = _confere(tmp_path, "B1", errada, "kc_06")
    assert any("linha 1" in p and "n == 1" in p for p in problemas), problemas


@tem_gcc
def test_a_segunda_chamada_e_conferida_a_parte(tmp_path):
    """A crença de que o n da função continua de uma chamada para a outra:
    a cena que a dissesse (n == 2 na segunda vez) é acusada uma vez só —
    a primeira chamada está certa."""
    errada = copy.deepcopy(CENA_CONTA)
    errada["passos"][4]["faz"][2]["guarda"]["valor"] = 2
    problemas = _confere(tmp_path, "B2", errada, "kc_01")
    assert len([p for p in problemas if "n == 2" in p]) == 1, problemas


@tem_gcc
def test_a_caixa_errada_da_fileira_e_acusada(tmp_path):
    errada = copy.deepcopy(CENA_NOTAS)
    errada["passos"][0]["faz"][1]["guarda"]["valor"] = [7, 8, 10]
    problemas = _confere(tmp_path, "B1", errada, "kc_07")
    assert any("notas[2] == 10" in p for p in problemas), problemas


@tem_gcc
def test_o_valor_errado_no_bloco_e_acusado(tmp_path):
    errada = copy.deepcopy(CENA_BLOCO)
    errada["passos"][2]["faz"][1]["guarda"]["valor"] = 8
    problemas = _confere(tmp_path, "B1", errada, "kc_08")
    assert any("bloco[2] == 8" in p for p in problemas), problemas


@tem_gcc
def test_o_ponteiro_para_a_caixa_errada_e_acusado(tmp_path):
    cena = {"atores": [{"nome": "idade", "tipo": "caixa", "de": "int"},
                       {"nome": "p", "tipo": "ponteiro", "de": "int *"},
                       {"nome": "pp", "tipo": "ponteiro", "de": "int **"}],
            "passos": [{"linha": 1, "faz": [{"cria": "idade"},
                                            {"guarda": {"em": "idade", "valor": 15}}]},
                       {"linha": 2, "faz": [{"cria": "p"},
                                            {"aponta": {"de": "p", "para": "idade"}}]},
                       {"linha": 3, "faz": [{"cria": "pp"},
                                            {"aponta": {"de": "pp", "para": "p"}}]},
                       {"linha": 5, "faz": [{"segue": "pp"}, {"mostra": "15"}]}]}
    assert _confere(tmp_path, "B2", cena, "kc_10") == []
    errada = copy.deepcopy(cena)
    errada["passos"][2]["faz"][1]["aponta"]["para"] = "idade"
    problemas = _confere(tmp_path, "B2", errada, "kc_10")
    assert any("pp == &idade" in p for p in problemas), problemas


@tem_gcc
def test_a_chamada_que_o_programa_nao_faz_e_acusada(tmp_path):
    """A cena conta duas chamadas de zera; o programa faz uma."""
    errada = copy.deepcopy(CENA_ZERA)
    errada["passos"][5:5] = [
        {"linha": 7, "faz": [{"chama": "zera"}, {"cria": "n"},
                             {"guarda": {"em": "n", "valor": 15}}]},
        {"linha": 1, "faz": [{"guarda": {"em": "n", "valor": 0}}]},
        {"linha": 7, "faz": [{"volta": "zera"}]}]
    problemas = _confere(tmp_path, "B1", errada, "kc_06")
    assert any("a entrada de zera: a cena passa 2 vez(es)" in p
               for p in problemas), problemas


@tem_gcc
def test_o_dobra_que_acumulasse_seria_acusado(tmp_path):
    errada = copy.deepcopy(CENA_DOBRA)
    errada["passos"][6]["faz"][1]["guarda"]["valor"] = 6
    problemas = _confere(tmp_path, "B1", errada, "kc_12")
    assert any("linha 2" in p and "n == 6" in p for p in problemas), problemas


# --------------------------------------------------------------------------
# As cenas do kc_00 e o que o servidor manda
# --------------------------------------------------------------------------

def test_toda_ideia_do_kc_00_tem_cena():
    esc = trilha_escada.le(ARQUIVO, D)
    assert [no for no in D.ordem if esc[no].cena is None] == []


@pytest.mark.parametrize("topico", ["kc_%02d" % i for i in range(13)])
def test_toda_ideia_de_todo_topico_tem_cena(topico):
    """A fatia 4 (docs/plano-cenas.md): as 79 ideias dos treze tópicos.
    A conferência delas contra o compilador é a do test_trilha_topicos,
    que confere a escada inteira de cada tópico."""
    d = carrega(topico=topico)
    esc = trilha_escada.le(_arquivo(topico), d)
    assert [no for no in d.ordem if esc[no].cena is None] == []


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


def _estados_da(tmp_path, topico, no, cena):
    import json
    esc = trilha_escada.le(_escadas_com(tmp_path, no, cena, topico),
                           carrega(topico=topico))
    programa = """
    global.window = global;
    require(require("path").join(WEB, "cena.js"));
    console.log(JSON.stringify(global.Cena.estados(%s)));
    """ % json.dumps(trilha_escada.cena_json(esc[no].cena))
    return json.loads(_roda_node(programa))


def _caixas(estado):
    return {c["nome"]: c for c in estado["caixas"]}


@tem_node
def test_a_bancada_abre_com_as_caixas_dela_e_fecha_sem_elas(tmp_path):
    e = _estados_da(tmp_path, "kc_06", "B1", CENA_ZERA)
    dentro = e[3]                                   # depois de chamar zera
    assert dentro["bancadas"] == [{"nome": "zera", "de": "void zera(int n)"}]
    assert _caixas(dentro)["n"]["dono"] == "zera"
    assert _caixas(dentro)["n"]["valor"] == "15"
    assert _caixas(dentro)["idade"]["dono"] is None
    depois = e[5]                                   # depois da volta
    assert depois["bancadas"] == [] and "n" not in _caixas(depois)
    assert "a bancada de zera abre" in e[3]["descricao"]
    assert "a bancada fecha" in e[5]["descricao"]


@tem_node
def test_a_fileira_tem_um_valor_por_caixa(tmp_path):
    e = _estados_da(tmp_path, "kc_07", "B1", CENA_NOTAS)
    notas = _caixas(e[1])["notas"]
    assert notas["valores"] == ["7", "8", "9"] and notas["tamanho"] == [3]
    assert "guarda 7, 8, 9 em notas" in e[1]["descricao"]
    # a caixinha que a linha lê fica marcada, e só naquele passo
    assert notas["foco"] is None and _caixas(e[2])["notas"]["foco"] == 2


@tem_node
def test_o_bloco_mora_no_monte_e_o_free_o_devolve(tmp_path):
    e = _estados_da(tmp_path, "kc_08", "B1", CENA_BLOCO)
    bloco = _caixas(e[2])["bloco"]
    assert bloco["tipo"] == "bloco" and bloco["devolvido"] is False
    assert bloco["valores"] == [None, None, None]
    assert _caixas(e[2])["p"]["aponta"] == "bloco"
    assert _caixas(e[3])["bloco"]["valores"] == [None, None, "9"]
    assert _caixas(e[5])["bloco"]["devolvido"] is True
    assert "aluga no monte" in e[2]["descricao"]
    assert "devolve o bloco" in e[5]["descricao"]


@tem_node
def test_o_static_fica_depois_da_volta(tmp_path):
    cena = {"atores": [{"nome": "f", "tipo": "bancada", "de": "int *f(void)"},
                       {"nome": "n", "tipo": "caixa", "de": "static int", "fica": True},
                       {"nome": "p", "tipo": "ponteiro", "de": "int *"}],
            "passos": [{"linha": 3, "faz": [{"chama": "f"}]},
                       {"linha": 1, "faz": [{"cria": "n"},
                                            {"guarda": {"em": "n", "valor": 7}}]},
                       {"linha": 3, "faz": [{"volta": "f"}, {"cria": "p"},
                                            {"aponta": {"de": "p", "para": "n"}}]},
                       {"linha": 4, "faz": [{"segue": "p"}, {"mostra": "7"}]}]}
    e = _estados_da(tmp_path, "kc_12", "I2", cena)
    assert _caixas(e[3])["n"]["dono"] is None and _caixas(e[3])["n"]["valor"] == "7"
    assert _caixas(e[3])["p"]["aponta"] == "n"
    assert "n fica: é static" in e[3]["descricao"]


@tem_node
def test_o_diz_entra_na_frase_do_passo(tmp_path):
    e = _estados_da(tmp_path, "kc_01", "B2", CENA_CONTA)
    assert "conta devolve 1" in e[2]["descricao"]


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


def test_em_tela_larga_a_cena_fica_ao_lado_do_texto():
    """O Rafael, em 18/11/2026: no painel de explicação a cena pedia
    rolagem. Em tela de computador o painel e a revisão alargam, com o
    texto à esquerda e a cena à direita; no celular, um embaixo do outro."""
    import re
    css = (WEB / "tema.css").read_text(encoding="utf-8")
    largo = re.search(r"@media \(min-width: 1000px\) \{(.*?)\n\}", css, re.S)
    assert largo, "tema.css não tem o bloco de tela larga da cena"
    for regra in (".palco.t-largo", ".t-painel.t-largo", ".t-lado-a-lado"):
        assert regra in largo.group(1), regra
    js = (WEB / "trilha.js").read_text(encoding="utf-8")
    assert js.count('"t-lado-a-lado"') >= 2
    assert 'classList.toggle("t-largo"' in js
