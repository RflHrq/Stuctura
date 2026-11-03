"""O molde: uma pergunta com buracos, e um programa que a confere.

Um molde errado erra em TODAS as variações de uma vez — é o preço do
multiplicador. Por isso a carga dele é tão desconfiada quanto a do
domínio: o que não puder ser conferido não entra.

A leitura e a validação são puras e moram aqui, no pacote do MVP, e não
no gerador: o gerador precisa da API da Anthropic para escrever molde, e
conferir molde não precisa de rede nenhuma.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp.dominio import carrega
from mvp.molde import Molde, MoldeInvalido, le


@pytest.fixture(scope="module")
def d7():
    return carrega(topico="kc_07")


def _cru(**troca) -> dict:
    """Um molde válido do B1 do kc_07, como ele é no arquivo."""
    base = {
        "no": "B1",
        "tipo": "teorica",
        "formato": "reconhecer_conceito",
        "nivel": 1,
        "uso": "treino",
        "parametros": {
            "tipo": ["int", "char", "double"],
            "nome": ["a", "v", "dados"],
            "n": [3, 5, 8],
        },
        "enunciado": "{tipo} {nome}[{n}] cria o quê?",
        "gabarito": "{extenso} caixas de {tipo}, grudadas",
        "distratores": [
            {"texto": "Uma caixa só, com as {extenso} dentro dela",
             "crenca": "string_literal_is_array"},
            {"texto": "Um ponteiro para {extenso} {tipo}",
             "crenca": "array_is_pointer"},
        ],
        "oraculo": "#include <stdio.h>\n"
                   "int main(void) {\n"
                   "    {tipo} {nome}[{n}];\n"
                   "    printf(\"%zu\\n\", sizeof {nome} / sizeof {nome}[0]);\n"
                   "    return 0;\n"
                   "}\n",
        "espera": "{n}",
        "revisado_por": "",
    }
    base.update(troca)
    return base


def _le(tmp_path, d7, nome="m1", **troca):
    caminho = tmp_path / ("moldes_%s.yaml" % nome)
    caminho.write_text(
        yaml.safe_dump({"mol_teste": _cru(**troca)}, allow_unicode=True),
        encoding="utf-8")
    return le(caminho, d7)


def _recusa(tmp_path, d7, nome, **troca) -> list[str]:
    with pytest.raises(MoldeInvalido) as erro:
        _le(tmp_path, d7, nome, **troca)
    return erro.value.problemas


# --------------------------------------------------------------------------
# O que carrega
# --------------------------------------------------------------------------

def test_le_um_molde_valido(tmp_path, d7):
    moldes = _le(tmp_path, d7)
    m = moldes["mol_teste"]
    assert isinstance(m, Molde)
    assert m.id == "mol_teste" and m.no == "B1"
    # Os parâmetros viram tupla: molde é dado de leitura, e lista que o
    # código pode remendar é convite a remendo.
    assert m.parametros["n"] == (3, 5, 8)
    assert m.distratores[0][1] == "string_literal_is_array"


def test_arquivo_que_nao_existe_devolve_vazio(tmp_path, d7):
    """Tópico sem molde nenhum é o caso de doze dos treze."""
    assert le(tmp_path / "moldes_nao_existe.yaml", d7) == {}


# --------------------------------------------------------------------------
# O que não carrega, uma invariante por teste
# --------------------------------------------------------------------------

def test_molde_sem_oraculo_nao_carrega(tmp_path, d7):
    """Molde sem programa que o confira é texto de modelo sem conferência
    nenhuma — é o nível 1 com cara de nível 2."""
    p = _recusa(tmp_path, d7, "c1", oraculo="")
    assert any("oráculo" in x for x in p), p


def test_molde_sem_espera_nao_carrega(tmp_path, d7):
    """Programa que roda e não diz o que devia sair não confere nada."""
    p = _recusa(tmp_path, d7, "c2", espera="")
    assert any("espera" in x for x in p), p


def test_buraco_que_nao_e_parametro_nao_carrega(tmp_path, d7):
    """Foco 1: `{tamanho}` quando o parâmetro é `n`.

    Tem de ser erro de validação com o nome do buraco, e não um
    `KeyError` no meio da expansão.
    """
    p = _recusa(tmp_path, d7, "c3",
                enunciado="{tipo} {nome}[{tamanho}] cria o quê?")
    assert any("buraco" in x and "tamanho" in x for x in p), p


def test_extenso_so_vale_quando_ha_n(tmp_path, d7):
    """`extenso` é derivado de `n`: sem `n`, não há de onde derivar."""
    p = _recusa(tmp_path, d7, "c4",
                parametros={"tipo": ["int"], "nome": ["a"]},
                enunciado="{tipo} {nome} e {extenso}",
                oraculo="int main(void) { {tipo} {nome}; return 0; }",
                espera="x")
    assert any("extenso" in x for x in p), p


def test_crenca_de_distrator_tem_de_existir(tmp_path, d7):
    """A mesma coleira do gerador de itens: o molde não inventa crença."""
    p = _recusa(tmp_path, d7, "c5", distratores=[
        {"texto": "Uma caixa só", "crenca": "nao_existe"}])
    assert any("crença" in x and "nao_existe" in x for x in p), p


def test_formato_nivel_e_uso_tem_de_ser_dos_catalogos(tmp_path, d7):
    assert any("formato" in x for x in _recusa(tmp_path, d7, "c6",
                                               formato="adivinhacao"))
    assert any("nível" in x for x in _recusa(tmp_path, d7, "c7", nivel=9))
    assert any("uso" in x for x in _recusa(tmp_path, d7, "c8", uso="enfeite"))
    assert any("tipo" in x for x in _recusa(tmp_path, d7, "c9", tipo="poesia"))


def test_no_tem_de_ser_do_topico(tmp_path, d7):
    p = _recusa(tmp_path, d7, "c10", no="Z9")
    assert any("nó" in x and "Z9" in x for x in p), p


def test_parametro_sem_valor_nao_carrega(tmp_path, d7):
    """Lista vazia não gera variação nenhuma, e o molde inteiro morre
    em silêncio na expansão."""
    p = _recusa(tmp_path, d7, "c11",
                parametros={"tipo": [], "nome": ["a"], "n": [3]})
    assert any("tipo" in x and "sem valor" in x for x in p), p


def test_menos_de_dois_distratores_nao_carrega(tmp_path, d7):
    """Item de duas alternativas é cara ou coroa."""
    p = _recusa(tmp_path, d7, "c12", distratores=[
        {"texto": "Uma caixa só", "crenca": "array_is_pointer"}])
    assert any("distrator" in x for x in p), p


# --------------------------------------------------------------------------
# A chave do C não é buraco
# --------------------------------------------------------------------------

def test_as_chaves_do_c_nao_sao_buracos(tmp_path, d7):
    """O oráculo é um programa em C, e C é cheio de chaves.

    Se a substituição fosse `str.format`, cada `{` do programa teria de
    ser dobrado — e quem escreve o molde escreveria C errado de propósito
    para o Python ficar feliz. Os buracos são identificadores entre
    chaves; o resto é código.
    """
    m = _le(tmp_path, d7, "ok")["mol_teste"]
    assert "int main(void) {" in m.oraculo
