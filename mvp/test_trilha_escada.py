"""A escada da premissa: o modelo, a leitura e a correção.

A escada é o conteúdo novo da trilha (docs/trilha.md, 6.16): uma
sequência de degraus, do mais mecânico até a ideia, em que cada degrau é
uma ou duas frases e um exercício pequeno de PRODUZIR — tocar numa
parte, montar uma linha, escolher, completar, digitar.

Estes testes guardam duas coisas. A leitura recusa escada malformada
dizendo por quê, com todos os problemas de uma vez, como o carregador do
domínio faz. E a correção é exata: sem compilador na sessão e sem
adivinhar, a resposta bate ou não com o que o conteúdo previu.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp import trilha_escada
from mvp.dominio import carrega

D = carrega(topico="kc_00")

PROGRAMA = (
    "#include <stdio.h>\n"
    "int main(void) {\n"
    "    int idade = 20;\n"
    "    idade = 21;\n"
    "    printf(\"%d\\n\", idade);\n"
    "    return 0;\n"
    "}\n"
)


def _montar(nome: str) -> dict:
    return {
        "pede": "Monte a linha com as peças.",
        "pecas": ["int", nome, ";", "="],
        "certa": [[0, 1, 2]],
        "certa_texto": "int %s;" % nome,
        "erros": [
            {"exata": [1, 0, 2], "invalida": True,
             "retorno": "Em C o tipo vem primeiro, depois o nome: int %s;" % nome},
            {"sem": [2], "invalida": True,
             "retorno": "Toda declaração termina com ;"},
        ],
        "retorno_geral": "A declaração é o tipo, o nome e o ponto e vírgula: "
                         "int %s;" % nome,
    }


def _escolher(nome: str) -> dict:
    return {
        "pede": "Uma destas linhas não é uma declaração válida. Qual?",
        "pecas": ["int %s;" % nome, "%s int;" % nome, "char turma;"],
        "certa": [[1]],
        "certa_texto": "%s int;" % nome,
        "invalidas": [1],
        "erros": [{"exata": [0], "retorno": "Essa é válida: tipo, nome e ;"}],
        "retorno_geral": "A inválida é a que põe o nome antes do tipo.",
    }


def _digitar(valor: str) -> dict:
    return {
        "pede": "O que este programa imprime?",
        "programa": PROGRAMA.replace("21", valor),
        "aceitas": [valor],
        "certa_texto": valor,
        "erros": [{"texto": "20", "crenca": "variable_remembers",
                   "retorno": "O 20 foi apagado quando o valor novo entrou."}],
        "retorno_geral": "Vale o último valor escrito.",
    }


def _valida() -> dict:
    """Uma escada válida do B1: um degrau guiado e dois de prática."""
    return {
        "revisao": {"frases": ["Toda variável tem um nome e um tipo."],
                    "codigo": "int idade;\n", "saida": ""},
        "degraus": [
            {"id": "esc_t_B1_1", "guiado": True, "forma": "montar",
             "codigo": True,
             "frases": ["Agora você.",
                        "Declare uma variável inteira chamada nota."],
             "versoes": [_montar("nota"), _montar("ano")]},
            {"id": "esc_t_B1_2", "guiado": False, "forma": "escolher",
             "codigo": True, "frases": [],
             "versoes": [_escolher("idade"), _escolher("pontos")]},
            {"id": "esc_t_B1_3", "guiado": False, "forma": "digitar",
             "codigo": True, "frases": [],
             "versoes": [_digitar("21"), _digitar("35")]},
        ],
    }


def _escreve(tmp_path, dados) -> Path:
    caminho = tmp_path / "escada_teste.yaml"
    caminho.write_text(yaml.safe_dump(dados, allow_unicode=True,
                                      sort_keys=False), encoding="utf-8")
    return caminho


def _le(tmp_path, dados):
    return trilha_escada.le(_escreve(tmp_path, dados), D)


# --------------------------------------------------------------------------
# A leitura
# --------------------------------------------------------------------------

def test_uma_escada_valida_carrega(tmp_path):
    e = _le(tmp_path, {"B1": _valida()})["B1"]
    assert e.premissa == "B1"
    assert [g.forma for g in e.degraus] == ["montar", "escolher", "digitar"]
    assert len(e.guiados) == 1 and len(e.pratica) == 2
    assert e.revisao.frases == ("Toda variável tem um nome e um tipo.",)
    v = e.degraus[0].versoes[0]
    assert v.certa == ((0, 1, 2),) and v.pecas == ("int", "nota", ";", "=")
    assert v.erros[0].exata == (1, 0, 2) and v.erros[0].invalida
    assert v.erros[1].sem == (2,)


@pytest.mark.parametrize("estraga, diz", [
    (lambda b: b["degraus"].__delitem__(slice(1, None)), "ao menos 3 degraus"),
    (lambda b: b["degraus"].extend(
        [copy.deepcopy(b["degraus"][1]) for _ in range(5)]),
     "no máximo 7 degraus"),
    (lambda b: b["degraus"][0]["versoes"].pop(), "ao menos 2 versões"),
    (lambda b: b["degraus"][0]["frases"].extend(["a", "b"]),
     "no máximo 2 frases"),
    (lambda b: b["degraus"][0]["frases"].__setitem__(0, "palavra " * 31),
     "30 palavras"),
    (lambda b: b["degraus"][1].__setitem__("guiado", True)
     or b["degraus"][0].__setitem__("guiado", False),
     "guiado depois de prática"),
    (lambda b: b["degraus"][1].__setitem__("frases", ["x"]),
     "degrau de prática não tem frase"),
    (lambda b: b["degraus"][0].__setitem__("frases", []),
     "degrau guiado sem frase"),
    (lambda b: b["degraus"][0].__setitem__("forma", "arrastar"),
     "forma desconhecida"),
    (lambda b: b["degraus"][0]["versoes"][0].__setitem__("certa", [[9]]),
     "peça fora da faixa"),
    (lambda b: b["degraus"][0]["versoes"][0]["erros"][0].__setitem__(
        "exata", [0, 1, 2]), "erro previsto é uma resposta aceita"),
    (lambda b: b["degraus"][0]["versoes"][0]["erros"][0].__setitem__(
        "crenca", "nao_existe"), "crença desconhecida"),
    (lambda b: b["degraus"][0]["versoes"][0].__setitem__("certa_texto", ""),
     "sem certa_texto"),
    (lambda b: b["degraus"][0]["versoes"][0].__setitem__("pede", ""),
     "sem o que se pede"),
    (lambda b: b["degraus"][2]["versoes"][0].__setitem__("aceitas", []),
     "sem resposta aceita"),
    (lambda b: b["degraus"][1]["versoes"][0].__setitem__("certa", [[0, 1]]),
     "uma peça só"),
    (lambda b: b["degraus"].__setitem__(
        2, dict(copy.deepcopy(b["degraus"][0]), id="esc_t_B1_3")),
     "ao menos 2 degraus de prática"),
    (lambda b: b["revisao"].__setitem__("frases", []), "revisão sem frase"),
])
def test_a_leitura_recusa_e_diz_por_que(tmp_path, estraga, diz):
    b = _valida()
    estraga(b)
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, {"B1": b})
    assert any(diz in p for p in erro.value.problemas), erro.value.problemas


def test_a_leitura_junta_todos_os_problemas_de_uma_vez(tmp_path):
    b = _valida()
    b["degraus"][0]["forma"] = "arrastar"
    b["degraus"][1]["frases"] = ["x"]
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, {"B1": b})
    juntos = " | ".join(erro.value.problemas)
    assert "forma desconhecida" in juntos
    assert "degrau de prática não tem frase" in juntos


def test_premissa_que_o_topico_nao_tem_e_recusada(tmp_path):
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, {"Z9": _valida()})
    assert any("premissa desconhecida" in p for p in erro.value.problemas)


def test_id_de_degrau_repetido_e_recusado(tmp_path):
    b = _valida()
    b["degraus"][2]["id"] = b["degraus"][1]["id"]
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, {"B1": b})
    assert any("id repetido" in p for p in erro.value.problemas)


def test_completar_pede_a_lacuna_uma_vez(tmp_path):
    def completar(mostra):
        return {"pede": "Complete.", "mostra": mostra,
                "pecas": ["idade", "int", "20"], "certa": [[0]],
                "certa_texto": "idade = 7;", "erros": [],
                "retorno_geral": "É a variável que foi declarada."}
    b = _valida()
    b["degraus"][1] = {"id": "esc_t_B1_2", "guiado": False,
                       "forma": "completar", "codigo": True, "frases": [],
                       "versoes": [completar("___ = 7;"), completar("___ = 9;")]}
    assert _le(tmp_path, {"B1": b})["B1"].degraus[1].forma == "completar"

    b["degraus"][1]["versoes"][0]["mostra"] = "idade = 7;"
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, {"B1": b})
    assert any("lacuna" in p for p in erro.value.problemas)


def test_digitar_aceita_o_trecho_mostrado_no_lugar_do_programa(tmp_path):
    """O trecho que a pessoa lê e o que o compilador roda são o MESMO texto.

    Um degrau de `digitar` pode trazer só `mostra`: o conferidor embrulha
    o trecho num `main`. Com `programa` à parte, o que se mostra e o que
    se confere poderiam divergir sem ninguém ver.
    """
    b = _valida()
    for v in b["degraus"][2]["versoes"]:
        v["mostra"] = "int idade = 20;" + chr(10) + "idade = 21;"
        v["programa"] = ""
    v = _le(tmp_path, {"B1": b})["B1"].degraus[2].versoes[0]
    assert v.programa == "" and v.mostra.startswith("int idade = 20;")


def test_digitar_sem_programa_e_sem_trecho_e_recusado(tmp_path):
    b = _valida()
    b["degraus"][2]["versoes"][0]["programa"] = ""
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, {"B1": b})
    assert any("digitar sem programa" in p for p in erro.value.problemas)


def test_faltando_lista_as_premissas_sem_escada(tmp_path):
    escadas = _le(tmp_path, {"B1": _valida()})
    assert trilha_escada.faltando(D, escadas) == ("B2", "B3", "B4", "I1")
    assert trilha_escada.faltando(D, {}) == tuple(D.ordem)


# --------------------------------------------------------------------------
# A correção
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def escada(tmp_path_factory):
    return _le(tmp_path_factory.mktemp("escada"), {"B1": _valida()})["B1"]


def test_montar_certo(escada):
    c = trilha_escada.corrige(escada.degraus[0].versoes[0], "montar",
                              pecas=(0, 1, 2))
    assert c.certa and c.retorno == "" and c.mostra_certa == ""


def test_montar_erro_exato(escada):
    c = trilha_escada.corrige(escada.degraus[0].versoes[0], "montar",
                              pecas=(1, 0, 2))
    assert not c.certa
    assert c.retorno == "Em C o tipo vem primeiro, depois o nome: int nota;"
    assert c.mostra_certa == "int nota;"


def test_montar_erro_por_falta_de_peca(escada):
    c = trilha_escada.corrige(escada.degraus[0].versoes[0], "montar",
                              pecas=(0, 1))
    assert not c.certa and c.retorno == "Toda declaração termina com ;"


def test_montar_erro_nao_previsto_cai_no_retorno_geral(escada):
    c = trilha_escada.corrige(escada.degraus[0].versoes[0], "montar",
                              pecas=(0, 3, 1, 2))
    assert not c.certa
    assert c.retorno.startswith("A declaração é o tipo, o nome")
    assert c.mostra_certa == "int nota;"


def test_peca_repetida_ou_fora_da_faixa_e_pedido_invalido(escada):
    v = escada.degraus[0].versoes[0]
    for ruim in ((0, 0, 2), (0, 1, 7), (-1,), ()):
        with pytest.raises(trilha_escada.RespostaInvalida):
            trilha_escada.corrige(v, "montar", pecas=ruim)


def test_escolher_com_duas_pecas_e_pedido_invalido(escada):
    v = escada.degraus[1].versoes[0]
    with pytest.raises(trilha_escada.RespostaInvalida):
        trilha_escada.corrige(v, "escolher", pecas=(0, 1))
    assert trilha_escada.corrige(v, "escolher", pecas=(1,)).certa
    errada = trilha_escada.corrige(v, "escolher", pecas=(0,))
    assert errada.retorno == "Essa é válida: tipo, nome e ;"
    assert trilha_escada.corrige(v, "escolher", pecas=(2,)).retorno == \
        "A inválida é a que põe o nome antes do tipo."


def test_digitar_ignora_espaco_nas_pontas(escada):
    v = escada.degraus[2].versoes[0]
    assert trilha_escada.corrige(v, "digitar", texto=" 21 ").certa
    assert trilha_escada.corrige(v, "digitar", texto="21\n").certa
    assert not trilha_escada.corrige(v, "digitar", texto="2 1").certa
    assert not trilha_escada.corrige(v, "digitar", texto="").certa


def test_digitar_errado_previsto_traz_o_retorno_e_a_crenca(escada):
    c = trilha_escada.corrige(escada.degraus[2].versoes[0], "digitar",
                              texto="20")
    assert not c.certa and c.crenca == "variable_remembers"
    assert c.retorno == "O 20 foi apagado quando o valor novo entrou."
    assert c.mostra_certa == "21"


def test_forma_que_nao_existe_e_pedido_invalido(escada):
    with pytest.raises(trilha_escada.RespostaInvalida):
        trilha_escada.corrige(escada.degraus[0].versoes[0], "arrastar",
                              pecas=(0,))


# --------------------------------------------------------------------------
# A ordem das peças
# --------------------------------------------------------------------------

def test_a_ordem_das_pecas_e_estavel_e_e_permutacao():
    a = trilha_escada.ordem_das_pecas("s1", "esc_kc00_B1_2", 0, "montar", 4)
    assert a == trilha_escada.ordem_das_pecas("s1", "esc_kc00_B1_2", 0,
                                              "montar", 4)
    assert sorted(a) == [0, 1, 2, 3]


def test_a_ordem_muda_com_a_semente_ou_com_a_versao():
    ordens = {trilha_escada.ordem_das_pecas(s, "esc_kc00_B1_2", v, "montar", 6)
              for s in ("s1", "s2", "s3", "s4") for v in (0, 1)}
    assert len(ordens) > 1


def test_tocar_e_digitar_nao_embaralham():
    assert trilha_escada.ordem_das_pecas("s1", "x", 0, "tocar", 3) == (0, 1, 2)
    assert trilha_escada.ordem_das_pecas("s1", "x", 0, "digitar", 0) == ()
