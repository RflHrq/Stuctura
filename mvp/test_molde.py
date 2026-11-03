"""O molde: uma pergunta com buracos, e um programa que a confere.

Um molde errado erra em TODAS as variações de uma vez — é o preço do
multiplicador. Por isso a carga dele é tão desconfiada quanto a do
domínio: o que não puder ser conferido não entra.

A leitura e a validação são puras e moram aqui, no pacote do MVP, e não
no gerador: o gerador precisa da API da Anthropic para escrever molde, e
conferir molde não precisa de rede nenhuma.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp.dominio import RAIZ as RAIZ_DOMINIO, carrega, topicos
from mvp.molde import Molde, MoldeInvalido, expande, item_de, le


@pytest.fixture(scope="module")
def d7():
    return carrega(topico="kc_07")


def _cru(**troca) -> dict:
    """Um molde válido do B1 do kc_07, como ele é no arquivo."""
    base = {
        "node": "B1",
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
    """O arquivo chama-se sempre `moldes_kc07.yaml`: é do NOME dele que
    sai o prefixo do `node` dos itens, como no carregador do domínio.
    Cada teste escreve o seu numa subpasta."""
    pasta = tmp_path / nome
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "moldes_kc07.yaml"
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
    assert le(tmp_path / "moldes_kc99.yaml", d7) == {}


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
    p = _recusa(tmp_path, d7, "c10", node="Z9")
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


# --------------------------------------------------------------------------
# A expansão
# --------------------------------------------------------------------------

def _hamming(a: dict, b: dict) -> int:
    """Em quantos parâmetros as duas variações diferem.

    `extenso` fica de fora: ele acompanha o `n`, e contá-lo seria contar
    o mesmo parâmetro duas vezes.
    """
    return sum(1 for k in a if k != "extenso" and a[k] != b[k])


@pytest.fixture
def m(tmp_path, d7):
    return _le(tmp_path, d7, "exp")["mol_teste"]


def test_a_expansao_e_estavel(m):
    """Mesma entrada, mesma saída: o candidato tem de ser reprodutível.

    Sem isso, reexpandir um molde revisado produz outro banco, e o
    `revisado_por` passa a valer para itens que ninguém viu.
    """
    assert expande(m, 6) == expande(m, 6)


def test_as_variacoes_sao_distantes(m):
    """Trocar de item tem de trocar de superfície.

    Seis variações que diferem num parâmetro só são a mesma pergunta seis
    vezes, e o eixo que o molde existe para criar não aparece.
    """
    saiu = expande(m, 6)
    assert len(saiu) == 6
    assert all(_hamming(a, b) >= 2
               for a, b in itertools.combinations(saiu, 2)), saiu


def test_menos_combinacoes_do_que_o_pedido(tmp_path, d7):
    """Foco 2: dois parâmetros de um valor só dão duas variações."""
    pequeno = _le(tmp_path, d7, "peq", parametros={
        "tipo": ["int"], "nome": ["a"], "n": [3, 5]})["mol_teste"]
    assert len(expande(pequeno, 6)) == 2


def test_extenso_acompanha_o_n(m):
    for p in expande(m, 6):
        assert p["extenso"] == {3: "três", 5: "cinco", 8: "oito"}[p["n"]]


def test_a_expansao_nao_repete_variacao(m):
    vistas = [tuple(sorted(p.items())) for p in expande(m, 6)]
    assert len(set(vistas)) == len(vistas)


# --------------------------------------------------------------------------
# O item expandido
# --------------------------------------------------------------------------

def test_o_item_sai_no_formato_do_dominio(m):
    """O que chega à sessão é um item de YAML como todos os outros."""
    it = item_de(m, expande(m, 6)[0], 1)
    assert it["node"] == "kc07:B1"          # prefixo sem underscore
    assert it["gabarito"] == "a"
    assert set(it["alternativas"]) == {"a", "b", "c"}
    assert it["crencas"] == {"b": "string_literal_is_array",
                             "c": "array_is_pointer"}
    assert it["nivel"] == 1 and it["uso"] == "treino"
    assert "{" not in it["enunciado"], "sobrou buraco no enunciado"


def test_o_item_carrega_a_procedencia(m):
    """Os dois campos que a Tarefa 1 ensinou o carregador a ler."""
    p = expande(m, 6)[0]
    it = item_de(m, p, 1)
    assert it["do_molde"] == "mol_teste"
    assert it["parametros"] == {k: v for k, v in p.items() if k != "extenso"}


def test_o_id_do_item_diz_o_molde_e_a_variacao(m):
    assert item_de(m, expande(m, 6)[2], 3)["id"] == "mol_teste_03"


def test_o_revisado_por_vem_do_molde(tmp_path, d7):
    """A mudança de objeto da revisão: quem é lido é o molde.

    É assim que o `--aprovar` de hoje continua valendo sem saber o que é
    molde — ele olha o `revisado_por` de cada item, e o item copia o do
    molde.
    """
    em_branco = _le(tmp_path, d7, "r1")["mol_teste"]
    assert item_de(em_branco, expande(em_branco, 1)[0], 1)["revisado_por"] == ""

    # "Revisado" passou a ser nome MAIS assinatura do conteúdo lido, então
    # o molde revisado deste teste assina. A asserção é a mesma.
    revisado = _le(tmp_path, d7, "r2", revisado_por="Rafael",
                   revisado_sha=em_branco.digest)["mol_teste"]
    assert item_de(revisado, expande(revisado, 1)[0], 1)["revisado_por"] == "Rafael"


# --------------------------------------------------------------------------
# Os moldes que existem no disco
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_todo_molde_do_disco_carrega(topico):
    """O mesmo que a lista de tópicos faz com os tópicos.

    Se alguém escrever um molde quebrado, cai aqui — e não na hora de
    gerar, com a expansão já rodando e o compilador já ligado.
    """
    d = carrega(topico=topico)
    caminho = RAIZ_DOMINIO / ("moldes_%s.yaml" % topico.replace("_", ""))
    moldes = le(caminho, d)
    for mid, m in moldes.items():
        assert m.no in d.nos, mid
        assert m.oraculo.strip() and m.espera.strip(), mid


def test_o_kc07_tem_o_primeiro_molde():
    """O primeiro molde de verdade, num nó de treino do tópico-piloto."""
    d = carrega(topico="kc_07")
    moldes = le(RAIZ_DOMINIO / "moldes_kc07.yaml", d)
    assert "mol_kc07_B1_treino_1" in moldes
    m = moldes["mol_kc07_B1_treino_1"]
    assert m.uso == "treino" and m.no == "B1"
    assert len(expande(m, 6)) == 6


def test_quem_escrever_no_em_vez_de_node_recebe_a_instrucao(tmp_path, d7):
    """`no:` em YAML 1.1 é o booleano FALSO — o problema da Noruega.

    O campo some, e a mensagem natural seria "nó '' não é deste tópico",
    que manda a pessoa procurar no lugar errado. Foi o que aconteceu na
    primeira expansão de verdade.
    """
    pasta = tmp_path / "noruega"
    pasta.mkdir()
    cru = _cru()
    cru.pop("node")
    texto = yaml.safe_dump({"mol_teste": cru}, allow_unicode=True)
    # escrito à mão, como alguém escreveria: `no: B1`, sem aspas
    texto = texto.replace("mol_teste:", "mol_teste:\n  no: B1", 1)
    (pasta / "moldes_kc07.yaml").write_text(texto, encoding="utf-8")

    with pytest.raises(MoldeInvalido) as erro:
        le(pasta / "moldes_kc07.yaml", d7)
    assert any("`node:`" in x for x in erro.value.problemas), erro.value.problemas


# --------------------------------------------------------------------------
# A trava da revisão: o nome vale para o conteúdo que foi lido
# --------------------------------------------------------------------------

def test_molde_revisado_com_a_assinatura_certa_vale(tmp_path, d7):
    cru = _cru()
    pasta = tmp_path / "ok"
    pasta.mkdir()
    (pasta / "moldes_kc07.yaml").write_text(
        yaml.safe_dump({"mol_teste": cru}, allow_unicode=True), encoding="utf-8")
    sem_nome = le(pasta / "moldes_kc07.yaml", d7)["mol_teste"]
    assert sem_nome.revisado is False

    cru.update(revisado_por="Rafael", revisado_sha=sem_nome.digest)
    (pasta / "moldes_kc07.yaml").write_text(
        yaml.safe_dump({"mol_teste": cru}, allow_unicode=True), encoding="utf-8")
    assert le(pasta / "moldes_kc07.yaml", d7)["mol_teste"].revisado is True


def test_molde_editado_depois_da_revisao_nao_carrega(tmp_path, d7):
    """O defeito que a revisão do ramo achou, e é o pior deles.

    Preencher `revisado_por`, expandir, aprovar, e depois acrescentar um
    valor em `n:` ou trocar uma palavra do gabarito: saíam variações
    inéditas já estampadas com o nome de quem nunca as leu, e o
    `--aprovar` as movia para o domínio. Num instrumento de pesquisa, o
    método afirma que cada item foi validado por uma pessoa.

    E não é uso torto: a spec documenta a reexpansão depois de editar, e
    prescreve editar — estreitar o domínio do parâmetro — como o conserto
    de um molde reprovado.
    """
    cru = _cru()
    pasta = tmp_path / "editado"
    pasta.mkdir()
    (pasta / "moldes_kc07.yaml").write_text(
        yaml.safe_dump({"mol_teste": cru}, allow_unicode=True), encoding="utf-8")
    sha = le(pasta / "moldes_kc07.yaml", d7)["mol_teste"].digest

    # revisado, e DEPOIS mexido
    cru.update(revisado_por="Rafael", revisado_sha=sha)
    cru["parametros"]["n"] = [3, 5, 8, 16]
    (pasta / "moldes_kc07.yaml").write_text(
        yaml.safe_dump({"mol_teste": cru}, allow_unicode=True), encoding="utf-8")

    with pytest.raises(MoldeInvalido) as erro:
        le(pasta / "moldes_kc07.yaml", d7)
    assert any("depois da revisão" in x for x in erro.value.problemas), \
        erro.value.problemas


def test_nome_sem_assinatura_nao_carrega(tmp_path, d7):
    """Nome sem assinatura é revisão de conteúdo nenhum."""
    p = _recusa(tmp_path, d7, "sem_sha", revisado_por="Rafael")
    assert any("revisado_sha" in x for x in p), p


def test_o_item_so_herda_o_nome_de_molde_revisado(tmp_path, d7):
    m = _le(tmp_path, d7, "herda")["mol_teste"]
    assert m.revisado is False
    assert item_de(m, expande(m, 1)[0], 1)["revisado_por"] == ""


def test_o_item_nao_herda_nome_de_molde_com_assinatura_velha(tmp_path, d7):
    """A segunda rede, e a única que `item_de` enxerga.

    A carga já recusa molde assinado e depois editado — mas `item_de`
    recebe um `Molde`, e nada garante que ele veio da carga. Se a
    propriedade `revisado` olhasse só o nome, bastaria montar o objeto na
    mão para o nome do revisor voltar a vazar para itens que ele não leu.
    """
    from dataclasses import replace

    m = _le(tmp_path, d7, "velha")["mol_teste"]
    assinado = replace(m, revisado_por="Rafael", revisado_sha=m.digest)
    assert assinado.revisado is True
    assert item_de(assinado, expande(assinado, 1)[0], 1)["revisado_por"] == "Rafael"

    velho = replace(m, revisado_por="Rafael", revisado_sha="0000deadbeef")
    assert velho.revisado is False
    assert item_de(velho, expande(velho, 1)[0], 1)["revisado_por"] == ""


# --------------------------------------------------------------------------
# Os portões que deixavam dado errado passar
# --------------------------------------------------------------------------

def test_oraculo_que_nao_usa_parametro_nao_carrega(tmp_path, d7):
    """Oráculo constante satisfaz a obrigatoriedade sem conferir nada.

    Seis compilações do mesmo programa, seis "passou", relatório verde —
    e com CARA de conferido, que é o pior resultado possível numa camada
    que existe para separar conferido de não conferido.
    """
    p = _recusa(tmp_path, d7, "const",
                oraculo='#include <stdio.h>\nint main(void) { printf("ok"); return 0; }\n',
                espera="ok")
    assert any("não usa parâmetro" in x for x in p), p


def test_extenso_exige_que_todo_n_tenha_nome(tmp_path, d7):
    """`{extenso}` fora de 1..10 deixava o buraco LITERAL no item.

    O participante receberia "{extenso} caixas de int, grudadas". Passa
    na validação (o `n` existe), e nenhum dos quatro portões olha: o
    oráculo não usa `{extenso}`, o contrato não repara, a variedade não
    repara.
    """
    p = _recusa(tmp_path, d7, "grande", parametros={
        "tipo": ["int"], "nome": ["a"], "n": [8, 16]})
    assert any("extenso" in x and "16" in x for x in p), p


def test_prever_saida_ainda_nao_vale_como_molde(tmp_path, d7):
    """A spec promete que, neste formato, o oráculo vira GABARITO.

    Enquanto isso não existir, `gabarito` e `espera` são campos
    independentes: o oráculo prova que o programa imprime `espera`, e
    ninguém prova que a alternativa certa diz a mesma coisa. Formato
    aceito e meio implementado é pior que formato recusado.
    """
    p = _recusa(tmp_path, d7, "prev", formato="prever_saida")
    assert any("prever_saida" in x and "gabarito" in x for x in p), p
