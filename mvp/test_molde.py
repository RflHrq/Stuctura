"""O molde: uma pergunta com buracos, e um programa que a confere.

Um molde errado erra em TODAS as variações de uma vez — é o preço do
multiplicador. Por isso a carga dele é tão desconfiada quanto a do
domínio: o que não puder ser conferido não entra.

A leitura e a validação são puras e moram aqui, no pacote do MVP, e não
no gerador: o gerador precisa da API da Anthropic para escrever molde, e
conferir molde não precisa de rede nenhuma.
"""

from __future__ import annotations

import collections
import itertools
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp.dominio import RAIZ as RAIZ_DOMINIO, carrega, topicos
from mvp.molde import (Molde, MoldeInvalido, expande, expande_familia,
                       item_de, le, serve_de_alternativa)


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
    it = item_de(m, m.redacoes[0], expande(m, 6)[0], 1)
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
    it = item_de(m, m.redacoes[0], p, 1)
    assert it["do_molde"] == "mol_teste"
    assert it["parametros"] == {k: v for k, v in p.items() if k != "extenso"}


def test_o_id_do_item_diz_o_molde_e_a_variacao(m):
    """O formato entra no id desde a família: duas redações da mesma
    variação colidiriam sem ele."""
    assert item_de(m, m.redacoes[0], expande(m, 6)[2], 3)["id"] ==         "mol_teste__reconhecer_conceito_03"


def test_o_revisado_por_vem_do_molde(tmp_path, d7):
    """A mudança de objeto da revisão: quem é lido é o molde.

    É assim que o `--aprovar` de hoje continua valendo sem saber o que é
    molde — ele olha o `revisado_por` de cada item, e o item copia o do
    molde.
    """
    em_branco = _le(tmp_path, d7, "r1")["mol_teste"]
    assert item_de(em_branco, em_branco.redacoes[0], expande(em_branco, 1)[0], 1)["revisado_por"] == ""

    # "Revisado" passou a ser nome MAIS assinatura do conteúdo lido, então
    # o molde revisado deste teste assina. A asserção é a mesma.
    revisado = _le(tmp_path, d7, "r2", revisado_por="Rafael",
                   revisado_sha=em_branco.digest)["mol_teste"]
    assert item_de(revisado, revisado.redacoes[0], expande(revisado, 1)[0], 1)["revisado_por"] == "Rafael"


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
    assert item_de(m, m.redacoes[0], expande(m, 1)[0], 1)["revisado_por"] == ""


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
    assert item_de(assinado, assinado.redacoes[0], expande(assinado, 1)[0], 1)["revisado_por"] == "Rafael"

    velho = replace(m, revisado_por="Rafael", revisado_sha="0000deadbeef")
    assert velho.revisado is False
    assert item_de(velho, velho.redacoes[0], expande(velho, 1)[0], 1)["revisado_por"] == ""


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

# --------------------------------------------------------------------------
# A família de formatos: uma afirmação, várias redações
# --------------------------------------------------------------------------

def _cru_familia(**troca) -> dict:
    """Uma família de três formatos para o mesmo B1."""
    base = {
        "node": "B1",
        "nivel": 1,
        "uso": "treino",
        "parametros": {"tipo": ["int", "char", "double"],
                       "nome": ["a", "v", "dados"],
                       "n": [3, 5, 8]},
        "crencas": ["string_literal_is_array", "array_is_pointer"],
        "oraculo": "#include <stdio.h>\n"
                   "int main(void) {\n"
                   "    {tipo} {nome}[{n}];\n"
                   "    printf(\"%zu\\n\", sizeof {nome} / sizeof {nome}[0]);\n"
                   "    return 0;\n"
                   "}\n",
        "espera": "{n}",
        "revisado_por": "",
        "formatos": {
            "reconhecer_conceito": {
                "tipo": "teorica",
                "enunciado": "Depois de {tipo} {nome}[{n}]; o que existe?",
                "gabarito": "São {extenso} caixas de {tipo}, grudadas",
                "distratores": [
                    "Uma caixa só, com {extenso} valores dentro dela",
                    "Um ponteiro, que aponta para {extenso} valores",
                ],
            },
            "achar_o_erro": {
                "tipo": "codigo",
                "codigo": "{tipo} {nome}[{n}];\n"
                          "{tipo} *p = {nome};\n"
                          "{nome} = p;\n",
                "enunciado": "Uma destas linhas não compila. Qual?",
                "gabarito": "A terceira: o nome do array não recebe nada",
                "distratores": [
                    "A segunda: um ponteiro não recebe o nome de um array",
                    "Nenhuma delas: as três compilam sem reclamação",
                ],
                "nao_compila": True,
                # Oráculo próprio: o da família compila, e este formato
                # prova o contrário. O `codigo` acima é o que a pessoa
                # vê; o oráculo é o programa inteiro.
                "oraculo": "int main(void) {\n"
                           "    {tipo} {nome}[{n}];\n"
                           "    {tipo} *p = {nome};\n"
                           "    {nome} = p;\n"
                           "    return 0;\n"
                           "}\n",
            },
            "prever_saida": {
                "tipo": "codigo",
                "codigo": "{tipo} {nome}[{n}];\n"
                          "printf(\"%zu\", sizeof {nome} / sizeof {nome}[0]);\n",
                "enunciado": "O que este programa imprime, exatamente?",
                "gabarito": "do_oraculo",
                "oraculo": "#include <stdio.h>\n"
                           "int main(void) {\n"
                           "    {tipo} {nome}[{n}];\n"
                           "    printf(\"%zu\", sizeof {nome} / sizeof {nome}[0]);\n"
                           "    return 0;\n"
                           "}\n",
                "espera": "{n}",
                "distratores": [
                    "o tamanho de um ponteiro, em bytes",
                    "1, porque {nome} é uma coisa só",
                ],
            },
        },
    }
    base.update(troca)
    return base


def _le_familia(tmp_path, d7, nome="f1", **troca):
    pasta = tmp_path / nome
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "moldes_kc07.yaml"
    # sort_keys=False: a ORDEM dos formatos é a do arquivo, e os testes
    # cobram essa ordem.
    caminho.write_text(
        yaml.safe_dump({"mol_teste": _cru_familia(**troca)},
                       allow_unicode=True, sort_keys=False),
        encoding="utf-8")
    return le(caminho, d7)


def _recusa_familia(tmp_path, d7, nome, **troca) -> list[str]:
    with pytest.raises(MoldeInvalido) as erro:
        _le_familia(tmp_path, d7, nome, **troca)
    return erro.value.problemas


def test_familia_de_tres_formatos_carrega(tmp_path, d7):
    m = _le_familia(tmp_path, d7, "f1")["mol_teste"]
    assert [r.formato for r in m.redacoes] == [
        "reconhecer_conceito", "achar_o_erro", "prever_saida"]
    assert m.crencas == ("string_literal_is_array", "array_is_pointer")
    # o que é de cada redação fica na redação
    achar = m.redacoes[1]
    assert achar.nao_compila is True
    assert "{nome} = p;" in achar.codigo
    assert len(achar.distratores) == 2


def test_molde_sem_formatos_e_familia_de_um(tmp_path, d7):
    """Foco 1: o que está no domínio hoje não pode precisar de reescrita.

    A família de um tem de ser indistinguível do molde de ontem — as
    crenças saem dos distratores, na ordem em que eles estão.
    """
    m = _le(tmp_path, d7, "velho")["mol_teste"]
    assert len(m.redacoes) == 1
    r = m.redacoes[0]
    assert r.formato == m.formato
    assert r.enunciado == m.enunciado
    assert r.gabarito == m.gabarito
    assert r.distratores == tuple(texto for texto, _ in m.distratores)
    assert m.crencas == tuple(cid for _, cid in m.distratores)
    assert r.nao_compila is False


def test_a_familia_do_kc07_esta_assinada():
    """Um fato de CONTEÚDO, cobrado onde fatos de conteúdo pertencem.

    Este teste nasceu como guarda — "a fatia não pode quebrar por
    acidente a assinatura do molde que está no domínio" — e afirmava
    `len(redacoes) == 1`. A família quebrou a assinatura DE PROPÓSITO,
    que é a trava funcionando: conteúdo novo pede leitura nova. A regra
    da família de um continua coberta por
    `test_molde_sem_formatos_e_familia_de_um`; o que mora aqui agora é o
    estado do arquivo de verdade.
    """
    d = carrega(topico="kc_07")
    m = le(RAIZ_DOMINIO / "moldes_kc07.yaml", d)["mol_kc07_B1_treino_1"]
    assert m.revisado is True, "a família está sem assinatura válida"
    assert [r.formato for r in m.redacoes] == [
        "reconhecer_conceito", "achar_o_erro", "comparar_casos"]
    assert m.crencas == ("string_literal_is_array", "array_is_pointer")


def test_familia_sem_crencas_nao_carrega(tmp_path, d7):
    p = _recusa_familia(tmp_path, d7, "c0b", crencas=[])
    assert any("sem crença" in x for x in p), p


def test_redacao_sem_enunciado_nao_carrega(tmp_path, d7):
    formatos = _cru_familia()["formatos"]
    formatos["achar_o_erro"]["enunciado"] = ""
    p = _recusa_familia(tmp_path, d7, "c0c", formatos=formatos)
    assert any("achar_o_erro" in x and "enunciado" in x for x in p), p


def test_cada_formato_tem_um_distrator_por_crenca(tmp_path, d7):
    """Foco 2: a correspondência é POSICIONAL, e quebraria em silêncio.

    Se um formato trouxesse dois distratores e outro um, as crenças
    deixariam de ser as mesmas nos dois — e aí eles não são duas
    superfícies da mesma afirmação, são duas perguntas.
    """
    formatos = _cru_familia()["formatos"]
    formatos["achar_o_erro"]["distratores"] = ["Só um distrator aqui"]
    p = _recusa_familia(tmp_path, d7, "c1", formatos=formatos)
    assert any("achar_o_erro" in x and "2 crença" in x for x in p), p


def test_crenca_da_familia_tem_de_existir(tmp_path, d7):
    p = _recusa_familia(tmp_path, d7, "c2", crencas=["nao_existe"])
    assert any("nao_existe" in x for x in p), p


def test_a_familia_precisa_da_crenca_do_proprio_no(tmp_path, d7):
    """A regra do contrato, cobrada uma vez na família.

    Sem um distrator que aponte a crença do próprio nó, o nó nunca
    recebe atribuição e termina a sessão sem medida — foi o que a
    revisão final mediu em 9 de 30 sessões do kc_00.
    """
    p = _recusa_familia(tmp_path, d7, "c3",
                        crencas=["array_is_pointer", "declaration_allocates"])
    assert any("próprio nó" in x for x in p), p


@pytest.fixture
def mf(tmp_path, d7):
    """A família de três formatos."""
    return _le_familia(tmp_path, d7, "mf")["mol_teste"]


def test_o_id_do_item_diz_a_familia_e_o_formato(mf):
    """Sem o formato no id, duas redações da mesma variação colidem."""
    it = item_de(mf, mf.redacoes[1], expande(mf, 6)[0], 2)
    assert it["id"] == "mol_teste__achar_o_erro_02"
    # o `do_molde` é o da FAMÍLIA: duas redações da mesma afirmação são
    # duas superfícies dela, e é assim que a generalização as vê.
    assert it["do_molde"] == "mol_teste"
    assert it["formato"] == "achar_o_erro"


def test_as_crencas_do_item_saem_da_familia(mf):
    it = item_de(mf, mf.redacoes[0], expande(mf, 6)[0], 1)
    assert list(it["crencas"].values()) == list(mf.crencas)


def test_o_codigo_da_redacao_vai_para_o_item(mf):
    it = item_de(mf, mf.redacoes[1], expande(mf, 6)[0], 1)
    assert it["codigo"].strip()
    assert "{" not in it["codigo"], it["codigo"]
    # e o da redação que NÃO tem código continua vazio
    assert item_de(mf, mf.redacoes[0], expande(mf, 6)[0], 1)["codigo"] == ""


# --------------------------------------------------------------------------
# O gabarito que sai do oráculo
# --------------------------------------------------------------------------

def test_do_oraculo_so_vale_em_prever_saida(tmp_path, d7):
    """Foco 4: noutro formato, a saída do programa não é a resposta."""
    formatos = _cru_familia()["formatos"]
    formatos["reconhecer_conceito"]["gabarito"] = "do_oraculo"
    p = _recusa_familia(tmp_path, d7, "g1", formatos=formatos)
    assert any("do_oraculo" in x and "prever_saida" in x for x in p), p


def test_prever_saida_na_familia_exige_do_oraculo(tmp_path, d7):
    """O contrário também: neste formato o gabarito TEM de sair do
    programa, senão `gabarito` e `espera` voltam a ser independentes e
    ninguém prova que dizem a mesma coisa."""
    formatos = _cru_familia()["formatos"]
    formatos["prever_saida"]["gabarito"] = "5"
    p = _recusa_familia(tmp_path, d7, "g2", formatos=formatos)
    assert any("prever_saida" in x and "do_oraculo" in x for x in p), p


def test_prever_saida_sozinho_continua_recusado(tmp_path, d7):
    """Fora da família, gabarito e espera são campos independentes."""
    p = _recusa(tmp_path, d7, "g3", formato="prever_saida")
    assert any("prever_saida" in x for x in p), p


def test_saida_que_serve_de_alternativa(tmp_path, d7):
    assert serve_de_alternativa("3") == (True, "3")
    ok, motivo = serve_de_alternativa("")
    assert not ok and "vazia" in motivo
    ok, motivo = serve_de_alternativa("3\n1")
    assert not ok and "linha" in motivo
    ok, motivo = serve_de_alternativa("x" * 80)
    assert not ok and "longa" in motivo


# --------------------------------------------------------------------------
# A expansão se reparte entre os formatos
# --------------------------------------------------------------------------

def test_a_expansao_se_reparte_entre_os_formatos(mf):
    """`quantas` é o TOTAL da família, não o de cada formato."""
    pares = expande_familia(mf, 6)
    assert len(pares) == 6
    assert collections.Counter(r.formato for r, _ in pares) == {
        "reconhecer_conceito": 2, "achar_o_erro": 2, "prever_saida": 2}


def test_a_primeira_variacao_e_a_mesma_em_todos_os_formatos(mf):
    """É isso que torna a troca de formato a única coisa que mudou.

    Acertar `int a[3]` como reconhecer e errar como achar-o-erro é sinal
    de superfície; se os parâmetros também mudassem, não dava para saber
    o que a pessoa não sustentou.
    """
    por_formato = collections.defaultdict(list)
    for r, p in expande_familia(mf, 6):
        por_formato[r.formato].append(p)
    primeiras = {tuple(sorted(v[0].items())) for v in por_formato.values()}
    assert len(primeiras) == 1, por_formato


def test_as_segundas_variacoes_divergem(mf):
    """Da segunda em diante, cada formato segue o seu caminho — senão a
    família inteira seria a mesma pergunta três vezes."""
    por_formato = collections.defaultdict(list)
    for r, p in expande_familia(mf, 6):
        por_formato[r.formato].append(p)
    segundas = {tuple(sorted(v[1].items())) for v in por_formato.values()}
    assert len(segundas) == 3, por_formato


def test_menos_variacoes_do_que_formatos(mf):
    """Foco 5: três formatos, duas variações.

    A ordem do YAML decide, e nenhum formato recebe duas antes de todos
    terem uma.
    """
    pares = expande_familia(mf, 2)
    assert [r.formato for r, _ in pares] == [
        "reconhecer_conceito", "achar_o_erro"]


def test_o_banco_de_treino_do_b1_ficou_com_quatro_formatos():
    """O número que motivou a fatia: 7 de um formato contra 1 e 1.

    O molde multiplicava o eixo do conteúdo e deixava o do formato como
    estava, e o motor prefere formato diferente a cada tentativa de
    treino — a regra ficava sem com que morder.
    """
    import collections

    d = carrega(topico="kc_07")
    por_formato = collections.Counter(
        a.formato for a in d.atividades if a.no == "B1" and a.uso == "treino")
    # RELATIVO ao banco, e nao 4 e 3 cravados: o 7-1-1 que motivou a
    # fatia nao era "sete", era "um formato com a maioria do banco". Com
    # os numeros cravados, o teste caia toda vez que o banco crescia por
    # um motivo legitimo — e caiu duas vezes neste ramo.
    total = sum(por_formato.values())
    assert len(por_formato) >= 3, por_formato
    assert max(por_formato.values()) * 2 <= total, (por_formato, total)


# --------------------------------------------------------------------------
# A revisão do ramo: as validações tinham ficado olhando o TOPO
# --------------------------------------------------------------------------

def test_buraco_dentro_de_um_formato_nao_carrega(tmp_path, d7):
    """C1: a varredura de buracos nunca descia em `formatos:`.

    Esta fatia passou a emitir `codigo` em todo item, e o item saía com
    `int a[{tamanho_errado}];` na tela da pessoa — exatamente o defeito
    para o qual o portão foi criado, reaberto por um campo novo.
    """
    formatos = _cru_familia()["formatos"]
    formatos["achar_o_erro"]["codigo"] = "{tipo} {nome}[{tamanho_errado}];"
    p = _recusa_familia(tmp_path, d7, "b1", formatos=formatos)
    assert any("tamanho_errado" in x and "buraco" in x for x in p), p


def test_a_linha_que_nao_compila_tem_de_estar_na_tela(tmp_path, d7):
    """C2: nada amarrava o programa conferido ao programa MOSTRADO.

    Dava para perguntar "qual destas duas linhas não compila?" com as
    duas corretas, e um oráculo com uma terceira linha que falha — e a
    alternativa certa apontando uma linha que não está na tela. O
    oráculo diria que sim, o compilador recusa, e estaria certo: a
    pessoa é que não tem como ver por quê.
    """
    formatos = _cru_familia()["formatos"]
    formatos["achar_o_erro"]["codigo"] = "{tipo} {nome}[{n}];\n{tipo} *p = {nome};"
    p = _recusa_familia(tmp_path, d7, "b2", formatos=formatos)
    assert any("achar_o_erro" in x and "a pessoa lê" in x for x in p), p


def test_o_codigo_mostrado_tem_de_estar_no_oraculo(tmp_path, d7):
    """A metade fraca da mesma regra, para os formatos que medem.

    O `comparar_casos` do molde de verdade mostra duas declarações e o
    oráculo acrescenta um `printf` que as mede — isso é legítimo, a
    medição não é programa que a pessoa lê. O que não pode é o
    contrário: uma linha na tela que o oráculo nunca compilou.
    """
    formatos = _cru_familia()["formatos"]
    formatos["prever_saida"]["codigo"] = "{tipo} {nome}[{n}];\n{nome}[{n}] = 0;"
    p = _recusa_familia(tmp_path, d7, "b2b", formatos=formatos)
    assert any("prever_saida" in x and "não está no oráculo" in x
               for x in p), p


def test_oraculo_de_formato_tambem_depende_dos_parametros(tmp_path, d7):
    """C3: a regra existia e era contornada por omissão.

    Sem oráculo de topo e com um constante em cada formato, a família
    carregava e passava nos quatro portões — e o `prever_saida` saía com
    a mesma resposta certa para n=3 e para n=8.
    """
    formatos = _cru_familia()["formatos"]
    for nome, r in formatos.items():
        r["oraculo"] = '#include <stdio.h>\nint main(void){ printf("7"); return 0; }'
        r["espera"] = "7"
        r.pop("nao_compila", None)
    cru = _cru_familia(formatos=formatos)
    cru.pop("oraculo")
    cru.pop("espera")
    pasta = tmp_path / "b3"
    pasta.mkdir()
    (pasta / "moldes_kc07.yaml").write_text(
        yaml.safe_dump({"mol_teste": cru}, allow_unicode=True, sort_keys=False),
        encoding="utf-8")
    with pytest.raises(MoldeInvalido) as erro:
        le(pasta / "moldes_kc07.yaml", d7)
    assert any("parâmetro" in x for x in erro.value.problemas), erro.value.problemas


def test_formato_com_oraculo_proprio_precisa_de_espera(tmp_path, d7):
    """I1: o `espera` caía para o da FAMÍLIA, que é a promessa de outro
    programa — e o portão comparava a saída de um com a promessa do
    outro."""
    formatos = _cru_familia()["formatos"]
    formatos["comparar_casos"] = {
        "tipo": "codigo",
        "codigo": "{tipo} {nome}[{n}];",
        "enunciado": "Quantas caixas, nos dois casos?",
        "gabarito": "São {extenso} caixas",
        "distratores": ["Uma só, com {extenso} dentro", "Nenhuma: {nome} é ponteiro"],
        "oraculo": '#include <stdio.h>\nint main(void){ {tipo} {nome}[{n}];'
                   ' printf("%zu", sizeof {nome} / sizeof {nome}[0]); return 0; }',
    }
    p = _recusa_familia(tmp_path, d7, "b4", formatos=formatos)
    assert any("comparar_casos" in x and "espera" in x for x in p), p


def test_nao_compila_com_espera_nao_carrega(tmp_path, d7):
    """A spec diz que declarar os dois juntos é erro de carga: não há
    saída que esperar de um programa que não vira executável."""
    formatos = _cru_familia()["formatos"]
    formatos["achar_o_erro"]["espera"] = "qualquer coisa"
    p = _recusa_familia(tmp_path, d7, "b5", formatos=formatos)
    assert any("nao_compila" in x and "espera" in x for x in p), p


def test_mais_de_tres_crencas_nao_carrega(tmp_path, d7):
    """I7: a quarta crença e o distrator dela sumiam no `zip`.

    O molde declarava uma crença que os itens não mediam, e ela nunca
    receberia atribuição. E o item sairia com cinco alternativas, contra
    as três ou quatro do contrato.
    """
    formatos = _cru_familia()["formatos"]
    for r in formatos.values():
        r["distratores"] = r["distratores"] + ["Mais um", "E mais um"]
    p = _recusa_familia(tmp_path, d7, "b6", formatos=formatos,
                        crencas=["string_literal_is_array", "array_is_pointer",
                                 "declaration_allocates", "array_is_assignable"])
    assert any("crença" in x and "contrato" in x for x in p), p
