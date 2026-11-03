"""O gerador de atividades: a coleira e a conferência.

O orientador pediu automatizar a criação das questões. O risco da
automação não é o item sair ruim — é o item sair **plausível e errado**,
que é o pior defeito possível num instrumento que mede concepções
erradas.

Duas defesas, e as duas têm teste aqui:

**A coleira.** O esquema da resposta só aceita ids de crença que já
existem no catálogo. O modelo escreve o item; ele não inventa a
concepção errônea nem a procedência dela, porque procedência é afirmação
sobre a literatura e isso não se gera.

**A conferência.** O candidato passa pelo carregador DE VERDADE — o mesmo
que roda em sessão — e pelas regras de `docs/linguagem.md` que o
carregador não cobra. Candidato que não passa não vira domínio.

Estes testes não chamam a API: o que eles exercitam é o esquema, o prompt
e a conferência, que é onde mora a garantia.
"""

from __future__ import annotations

import sys
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import gerar  # noqa: E402

from mvp.dominio import carrega  # noqa: E402

D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d2():
    return D2


def _item(**troca):
    base = dict(
        id="t_1", node="kc02:B2", nivel=2, formato="reconhecer_conceito",
        tipo="teorica", codigo="", gerado_por="teste", revisado_por="",
        por_que_este_distrator="x",
        enunciado="O ponteiro p ocupa espaço na memória?",
        alternativas={"a": "Sim, e tem endereço próprio",
                      "b": "Não, ele é só a ligação entre as caixas",
                      "c": "Só depois que apontar para alguma coisa real"},
        gabarito="a",
        crencas={"b": "pointer_has_no_address", "c": "pointer_is_data"},
    )
    base.update(troca)
    return base


# --------------------------------------------------------------------------
# A coleira: o modelo não inventa crença
# --------------------------------------------------------------------------

def test_o_esquema_so_aceita_crenca_que_existe(d2):
    """É a defesa principal. Uma crença inventada entraria no catálogo com
    cara de achado da literatura e sem fonte nenhuma."""
    esq = gerar.esquema(d2)
    alt = esq["properties"]["atividades"]["items"]["properties"]["alternativas"]
    ids = alt["items"]["properties"]["crenca"]["enum"]
    assert set(ids) == set(d2.crencas) | {""}
    assert "pointer_has_no_address" in ids


def test_o_esquema_fecha_as_listas_que_o_carregador_cobra(d2):
    """Formato, tipo e gabarito saem de enum: erro de digitação do modelo
    vira recusa da API, não domínio inválido depois."""
    item = gerar.esquema(d2)["properties"]["atividades"]["items"]
    from mvp.dominio import FORMATOS, TIPOS
    assert set(item["properties"]["formato"]["enum"]) == set(FORMATOS)
    assert set(item["properties"]["tipo"]["enum"]) == set(TIPOS)
    assert item["additionalProperties"] is False


def test_o_prompt_leva_a_crenca_do_no_as_dos_vizinhos_e_o_que_ja_existe(d2):
    """Sem a do próprio nó o item não mede o nó; sem as dos vizinhos não
    há atribuição cruzada; sem os itens que já existem o modelo repete."""
    _, pedido = gerar.prompt(d2, "B2", 2, 2)
    assert "pointer_has_no_address" in pedido          # a do próprio nó
    assert "pointer_is_data" in pedido                 # de um vizinho
    assert "ciu_kc02_004" in pedido                    # item que já existe
    assert "DEGRAU 2" in pedido


def test_o_prompt_de_degrau_1_pede_a_analogia(d2):
    """O degrau 1 responde NA ANALOGIA, antes de ser em C. É a regra que
    faz o primeiro degrau ser respondível por quem acabou de ler a tela."""
    _, pedido = gerar.prompt(d2, "B2", 1, 1)
    assert "ANALOGIA" in pedido


def test_a_procedencia_do_item_fica_no_yaml(d2):
    """Vai para o método do TCC: item gerado com assistência de modelo,
    sob contrato declarado, e validado um a um por uma pessoa. Declarado
    assim é defensável; calado, não."""
    bruto = [{
        "enunciado": "x", "codigo": "", "formato": "reconhecer_conceito",
        "tipo": "teorica", "gabarito": "a", "por_que_este_distrator": "y",
        "alternativas": [
            {"chave": "a", "texto": "certa", "crenca": ""},
            {"chave": "b", "texto": "errada", "crenca": "pointer_has_no_address"},
            {"chave": "c", "texto": "outra", "crenca": "pointer_is_data"},
        ],
    }]
    saida = gerar.para_yaml(d2, "B2", 2, bruto)[0]
    assert saida["gerado_por"].startswith(gerar.MODELO)
    assert saida["revisado_por"] == "", "o revisor é pessoa, e começa vazio"
    assert saida["nivel"] == 2
    assert saida["crencas"] == {"b": "pointer_has_no_address",
                                "c": "pointer_is_data"}
    assert "a" not in saida["crencas"], "o gabarito não carrega crença"


# --------------------------------------------------------------------------
# A conferência: o candidato passa pelo carregador de verdade
# --------------------------------------------------------------------------

def test_um_item_bom_passa():
    """A contraprova das seis abaixo."""
    assert gerar.confere("kc_02", [_item()]) == []


@pytest.mark.parametrize("nome,troca,sinal", [
    ("a certa é a mais longa",
     dict(alternativas={"a": "Uma variável que ocupa espaço na memória e tem endereço próprio dela",
                        "b": "Só uma seta", "c": "O próprio valor"}),
     "mais longa"),
    ("distrator sem crença",
     dict(crencas={"b": "pointer_has_no_address"}),
     "sem crença"),
    ("nenhuma crença do próprio nó",
     dict(crencas={"b": "pointer_is_data", "c": "memory_is_by_name"}),
     "próprio nó"),
    ("duas alternativas",
     dict(alternativas={"a": "Sim", "b": "Não, é só a seta"},
          crencas={"b": "pointer_has_no_address"}),
     "três alternativas"),
    ("negativa no enunciado",
     dict(enunciado="Qual não é verdade sobre p?"),
     "pista no enunciado"),
    ("nível que não existe",
     dict(nivel=9),
     "nivel inválido"),
])
def test_a_conferencia_pega(nome, troca, sinal):
    problemas = gerar.confere("kc_02", [_item(**troca)])
    assert problemas, nome
    assert any(sinal in p for p in problemas), (nome, problemas)


def test_a_conferencia_usa_o_carregador_de_verdade():
    """Não é uma segunda implementação das regras: é o mesmo `carrega` que
    roda em sessão. Crença que não existe no catálogo é recusada por ele,
    não por uma checagem paralela que pode divergir."""
    problemas = gerar.confere("kc_02", [_item(
        crencas={"b": "crenca_que_nao_existe", "c": "pointer_is_data"})])
    assert any("catálogo" in p for p in problemas), problemas


def test_o_candidato_nao_toca_o_dominio_de_verdade():
    """A conferência monta o domínio numa cópia temporária. Candidato
    ruim não pode sujar `mvp/dominio/` nem por um instante."""
    from mvp.dominio import RAIZ as DOMINIO
    antes = {p.name: p.read_bytes() for p in DOMINIO.glob("*.yaml")}
    gerar.confere("kc_02", [_item(nivel=9)])
    assert {p.name: p.read_bytes() for p in DOMINIO.glob("*.yaml")} == antes


# --------------------------------------------------------------------------
# A folha de revisão, e o portão da aprovação
#
# O mecanismo só vale se a aprovação for de PESSOA. Testar isso é testar
# que o programa recusa o que ninguém leu.
# --------------------------------------------------------------------------

def test_a_folha_mostra_o_item_como_uma_pessoa_le(d2, tmp_path, monkeypatch):
    """Revisar é leitura, não diff: a folha tem de dizer qual é a certa e
    que crença cada distrator levanta — inclusive em qual nó ela bate,
    que é a atribuição cruzada ficando visível.

    OS CANDIDATOS SÃO DESTE TESTE, como nos três vizinhos. Ele lia a pasta
    `candidatos/` de verdade e caiu no dia em que ela foi apagada — sem
    nenhuma regra ter quebrado: o que sumiu foi a fixture. Teste de
    formato não se amarra a conteúdo que existe por outro motivo.
    """
    _candidatos_falsos(tmp_path, monkeypatch,
                       _item(id="t_1", nivel=1),
                       _item(id="t_3", nivel=3,
                             enunciado="Qual das duas linhas não compila?"))
    texto = gerar.folha(d2, "kc_02")
    assert "**[certa]**" in texto
    assert "nega B3" in texto or "nega B2" in texto
    assert "revisado_por" in texto
    assert "degrau 1" in texto and "degrau 3" in texto


def test_nao_aprova_o_que_ninguem_revisou(tmp_path, monkeypatch):
    """O portão. Sem nome em `revisado_por`, nada entra.

    O espelho NÃO é zelo excessivo. Na primeira versão este teste chamava
    `aprova` contra o domínio de verdade: passava normalmente, e quando a
    sabotagem tirou o portão ele gravou os 18 candidatos em
    `mvp/dominio/activities_kc02.yaml`. Teste que pode estragar o projeto
    quando o código falha é teste perigoso — quem achou foi o `git status`.
    """
    import shutil
    from mvp import dominio as mod

    espelho = tmp_path / "dominio"
    shutil.copytree(mod.RAIZ, espelho)
    monkeypatch.setattr(mod, "RAIZ", espelho)
    antes = (espelho / "activities_kc02.yaml").read_bytes()
    # Candidatos PRÓPRIOS, não os do projeto: os de lá já foram revisados
    # e aprovados, e um teste que depende do estado do repositório deixa de
    # morder no dia em que o repositório muda. Foi o que aconteceu aqui.
    _candidatos_falsos(tmp_path, monkeypatch, _item(revisado_por=""))

    quantos, avisos = gerar.aprova("kc_02")
    assert quantos == 0
    assert any("revisado_por" in a for a in avisos)
    assert (espelho / "activities_kc02.yaml").read_bytes() == antes


def _candidatos_falsos(tmp_path, monkeypatch, *itens):
    """Candidatos de mentira, numa pasta de mentira.

    O nome do arquivo é o id do nó: a folha agrupa por ele e procura o
    enunciado simples daquele nó no domínio.
    """
    import yaml
    pasta = tmp_path / "candidatos" / "kc_02"
    pasta.mkdir(parents=True)
    (pasta / "B2.yaml").write_text(
        yaml.safe_dump({"activities": list(itens)}, allow_unicode=True),
        encoding="utf-8")
    monkeypatch.setattr(gerar, "CANDIDATOS", tmp_path / "candidatos")


def test_aprovado_e_valido_entra_no_dominio(tmp_path, monkeypatch):
    import shutil
    import yaml
    from mvp import dominio as mod

    espelho = tmp_path / "dominio"
    shutil.copytree(mod.RAIZ, espelho)
    monkeypatch.setattr(mod, "RAIZ", espelho)
    _candidatos_falsos(tmp_path, monkeypatch, _item(revisado_por="Rafael"))

    quantos, avisos = gerar.aprova("kc_02")
    assert quantos == 1, avisos
    cru = yaml.safe_load((espelho / "activities_kc02.yaml").read_text(encoding="utf-8"))
    assert any(a["id"] == "t_1" for a in cru["activities"])
    # e o arquivo continua carregando, com os comentários do contrato nele
    assert "REGRA DE DISTRATOR" in (espelho / "activities_kc02.yaml").read_text(encoding="utf-8")
    assert carrega(espelho, topico="kc_02")


def test_aprovado_mas_invalido_nao_escreve_nada(tmp_path, monkeypatch):
    """Meio banco gravado é pior do que nenhum: confere ANTES de escrever."""
    import shutil
    from mvp import dominio as mod

    espelho = tmp_path / "dominio"
    shutil.copytree(mod.RAIZ, espelho)
    monkeypatch.setattr(mod, "RAIZ", espelho)
    antes = (espelho / "activities_kc02.yaml").read_bytes()
    _candidatos_falsos(tmp_path, monkeypatch,
                       _item(revisado_por="Rafael", nivel=9))

    quantos, avisos = gerar.aprova("kc_02")
    assert quantos == 0
    assert avisos
    assert (espelho / "activities_kc02.yaml").read_bytes() == antes


# --------------------------------------------------------------------------
# Os quatro portões do molde
# --------------------------------------------------------------------------

import yaml as _yaml            # noqa: E402

sys.path.insert(0, str(RAIZ / "scripts"))
import oraculo  # noqa: E402

D7 = carrega(topico="kc_07")
tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)


def _molde(tmp_path, nome, **troca):
    """Escreve um `moldes_kc07.yaml` numa pasta só deste teste."""
    base = {
        "node": "B1",
        "tipo": "teorica",
        "formato": "reconhecer_conceito",
        "nivel": 1,
        "uso": "treino",
        "parametros": {"tipo": ["int", "char", "double"],
                       "nome": ["a", "v", "dados"],
                       "n": [3, 5, 8]},
        "enunciado": "{tipo} {nome}[{n}] guarda quantos valores?",
        "gabarito": "{extenso}, um por caixa",
        "distratores": [
            {"texto": "Um só, com os outros dentro dele",
             "crenca": "string_literal_is_array"},
            {"texto": "Nenhum: {nome} é um ponteiro",
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
    pasta = tmp_path / nome
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "moldes_kc07.yaml").write_text(
        _yaml.safe_dump({"mol_teste": base}, allow_unicode=True),
        encoding="utf-8")
    return pasta


@tem_gcc
def test_molde_certo_expande_e_passa_nos_quatro_portoes(tmp_path):
    itens, problemas = gerar.expande_molde(
        D7, "kc_07", "mol_teste", raiz=_molde(tmp_path, "ok"))
    assert problemas == []
    assert len(itens) == 6
    assert {i["do_molde"] for i in itens} == {"mol_teste"}


@tem_gcc
def test_uma_variacao_reprovada_derruba_o_molde_inteiro(tmp_path):
    """O oráculo reprova o MOLDE, não a variação.

    Ficar com as que passaram é como se esconde uma generalização
    indevida: o banco fica cheio de itens corretos sobre o caso que
    funciona, e a afirmação falsa continua escrita no molde, esperando a
    próxima expansão.
    """
    # `sizeof` mede BYTES: só vale para char. É o erro da sonda.
    pasta = _molde(tmp_path, "ruim",
                   oraculo="#include <stdio.h>\n"
                           "int main(void) {\n"
                           "    {tipo} {nome}[{n}];\n"
                           "    printf(\"%zu\\n\", sizeof {nome});\n"
                           "    return 0;\n"
                           "}\n")
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == [], "guardou as variações que passaram"
    assert any("promete" in p for p in problemas), problemas
    assert any("molde" in p.lower() for p in problemas), problemas


@tem_gcc
def test_o_portao_do_contrato_diz_qual_variacao_quebrou(tmp_path):
    """Foco 5: a alternativa certa não pode ser a mais longa."""
    pasta = _molde(tmp_path, "longa", gabarito=(
        "{extenso} valores, um em cada caixa, e as caixas estão grudadas "
        "uma na outra desde a declaração"))
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any("mol_teste_0" in p and "mais longa" in p
               for p in problemas), problemas


@tem_gcc
def test_variacao_igual_a_item_que_ja_existe_e_recusada(tmp_path):
    """O molde reproduz, palavra por palavra, um item escrito à mão."""
    pasta = _molde(tmp_path, "repetida",
                   parametros={"tipo": ["int"], "nome": ["a"], "n": [5]},
                   enunciado="int a[5] cria o quê?")
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any("ciu_kc07_001" in p for p in problemas), problemas


def test_molde_que_nao_existe_no_arquivo(tmp_path):
    itens, problemas = gerar.expande_molde(
        D7, "kc_07", "mol_fantasma", raiz=_molde(tmp_path, "fantasma"))
    assert itens == []
    assert any("mol_fantasma" in p for p in problemas), problemas


# --------------------------------------------------------------------------
# A folha do molde: o que a pessoa lê para preencher o revisado_por
# --------------------------------------------------------------------------

def _le_molde(tmp_path, nome, **troca):
    from mvp import molde as mod
    return mod.le(_molde(tmp_path, nome, **troca) / "moldes_kc07.yaml",
                  D7)["mol_teste"]


def test_a_folha_do_molde_mostra_o_texto_e_os_extremos(tmp_path):
    """A máquina confere o C; o português é da pessoa.

    E ela o lê nos EXTREMOS do espaço de parâmetros, que é onde a
    concordância quebra — não em três variações sorteadas, que podem cair
    todas no meio.
    """
    m = _le_molde(tmp_path, "folha")
    texto = gerar.folha_do_molde(D7, m)
    assert "{tipo} {nome}[{n}]" in texto, "o molde com os buracos não aparece"
    assert texto.count("### variação") == 3, texto
    assert "n=3" in texto and "n=8" in texto, texto
    assert "dados" in texto, "faltou o nome mais longo"
    assert "revisado_por" in texto


def test_a_folha_do_molde_diz_a_crenca_de_cada_distrator(tmp_path):
    """O mesmo que a folha dos itens faz: a atribuição cruzada visível."""
    m = _le_molde(tmp_path, "folha2")
    texto = gerar.folha_do_molde(D7, m)
    assert "array_is_pointer" in texto
    assert "nega I3" in texto


def test_a_folha_do_molde_mostra_o_oraculo(tmp_path):
    """Quem revisa o molde precisa ver o que a máquina conferiu."""
    m = _le_molde(tmp_path, "folha3")
    texto = gerar.folha_do_molde(D7, m)
    assert "sizeof" in texto and "espera" in texto


def test_os_extremos_nao_sao_as_tres_primeiras_da_expansao(tmp_path):
    """A sabotagem que passou limpa, virada teste.

    Trocar os extremos pelas três primeiras da expansão NÃO derrubou
    `test_a_folha_do_molde_mostra_o_texto_e_os_extremos`: com três
    parâmetros de três valores, as três primeiras da escolha gulosa são
    justamente os extremos, por coincidência do tamanho. A asserção não
    media a regra — media aquele molde.

    Aqui o espaço é largo o bastante para as duas coisas discordarem.
    """
    from mvp.molde import expande

    m = _le_molde(tmp_path, "largo", parametros={
        "tipo": ["int", "char"],
        "nome": ["a", "bb", "ccc", "dddd", "comprido"],
        "n": [2, 3, 4, 5, 6, 7, 8]})
    tres = gerar.extremos(m)
    assert [p["n"] for p in tres[:2]] == [2, 8], tres
    assert any(p["nome"] == "comprido" for p in tres), tres
    assert tres != expande(m, 3), "os extremos viraram as três primeiras"


# --------------------------------------------------------------------------
# O molde escrito pelo modelo
# --------------------------------------------------------------------------

def test_o_esquema_de_molde_so_aceita_crenca_que_existe():
    """A mesma coleira do gerador de itens: enum dos ids do catálogo.

    É o que impede o pior defeito possível num instrumento que mede
    concepções errôneas — o modelo inventar uma.
    """
    enum = gerar.esquema_de_molde(D7)["properties"]["distratores"]["items"][
        "properties"]["crenca"]["enum"]
    assert set(enum) == set(D7.crencas)


def test_o_esquema_de_molde_cobra_o_oraculo():
    e = gerar.esquema_de_molde(D7)
    assert "oraculo" in e["required"] and "espera" in e["required"]
    assert "parametros" in e["required"]


def test_o_pedido_manda_escrever_o_oraculo():
    sistema, pedido = gerar.prompt_de_molde(D7, "B1", 1)
    junto = sistema + pedido
    assert "oraculo" in junto and "espera" in junto


def test_o_pedido_diz_que_o_gabarito_e_regra():
    """É a diferença entre escrever um item e escrever a fábrica dele."""
    sistema, pedido = gerar.prompt_de_molde(D7, "B1", 1)
    assert "regra" in (sistema + pedido).lower()


def test_o_pedido_leva_as_crencas_do_no_e_dos_vizinhos():
    sistema, pedido = gerar.prompt_de_molde(D7, "B1", 1)
    assert "string_literal_is_array" in pedido      # a crença do próprio B1


# --------------------------------------------------------------------------
# O ciclo humano do molde: folha, assinatura, reexpansão
# --------------------------------------------------------------------------

def test_a_folha_dos_itens_ignora_o_yaml_de_molde(tmp_path, monkeypatch):
    """`--revisar` quebrava com KeyError depois da primeira expansão.

    A folha dos itens agrupa por nó e tira o nome do nó do NOME DO
    ARQUIVO. O `--expandir` escreve `mol_kc07_B1_treino_1.yaml` na mesma
    pasta, e aquele stem não é nó nenhum.
    """
    import yaml as y
    pasta = tmp_path / "candidatos" / "kc_02"
    pasta.mkdir(parents=True)
    (pasta / "B2.yaml").write_text(
        y.safe_dump({"activities": [_item(nivel=1)]}, allow_unicode=True),
        encoding="utf-8")
    (pasta / "mol_kc02_B2_treino_1.yaml").write_text(
        y.safe_dump({"activities": [_item(id="m_1", do_molde="mol_x",
                                          parametros={"n": 3})]},
                    allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(gerar, "CANDIDATOS", tmp_path / "candidatos")
    texto = gerar.folha(D2, "kc_02")          # não pode estourar
    assert "**[certa]**" in texto
    assert "mol_kc02_B2_treino_1" not in texto


def test_a_folha_do_molde_diz_o_que_escrever_para_aprovar(tmp_path):
    """Sem a assinatura na folha, ninguém tem como preenchê-la."""
    m = _le_molde(tmp_path, "assina")
    texto = gerar.folha_do_molde(D7, m)
    assert "revisado_sha: %s" % m.digest in texto, texto


def test_reexpandir_um_molde_aprovado_nao_acusa_plagio_de_si_mesmo(tmp_path):
    """O portão da variedade comparava com TODAS as atividades do
    domínio, inclusive as que tinham saído daquele mesmo molde.

    Depois do primeiro `--aprovar`, reexpandir dava "mol_x_01: enunciado
    igual ao de mol_x_01" — o mesmo id nos dois lados da frase.
    """
    from dataclasses import replace as _replace

    pasta = _molde(tmp_path, "reexp")
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert problemas == []

    # o domínio agora contém os itens daquele molde
    d_com = _replace(D7, atividades=D7.atividades + tuple(
        _atividade_de(i) for i in itens))
    de_novo, problemas = gerar.expande_molde(d_com, "kc_07", "mol_teste",
                                             raiz=pasta)
    assert problemas == [], problemas
    assert len(de_novo) == 6


def _atividade_de(item: dict):
    """O item cru virado `Atividade`, só com o que o portão 4 olha."""
    from mvp.dominio import Atividade, Opcao
    return Atividade(
        id=item["id"], no=item["node"].split(":")[-1], tipo=item["tipo"],
        formato=item["formato"], enunciado=item["enunciado"],
        opcoes=tuple(Opcao(texto=t, correta=(k == item["gabarito"]))
                     for k, t in item["alternativas"].items()),
        uso=item["uso"], nivel=item["nivel"], do_molde=item["do_molde"],
        parametros=item["parametros"])


def test_aprovar_item_com_id_que_ja_existe_diz_que_esta_duplicado(
        tmp_path, monkeypatch):
    """A revisão do ramo apontou aqui um beco silencioso, e não é.

    O relato era que reexpandir depois de aprovar descartava tudo por
    colisão de id e o CLI dizia só "nada foi movido". Medido: o
    `confere` roda ANTES e devolve "atividade X duplicada", que o CLI
    imprime. A mensagem já existe; este teste é que não existia.
    """
    import shutil
    from mvp import dominio as mod

    espelho = tmp_path / "dominio"
    shutil.copytree(mod.RAIZ, espelho)
    monkeypatch.setattr(mod, "RAIZ", espelho)

    _candidatos_falsos(tmp_path, monkeypatch,
                       _item(id="ciu_kc02_001", revisado_por="Rafael"))
    quantos, avisos = gerar.aprova("kc_02")
    assert quantos == 0
    assert any("ciu_kc02_001" in a and "duplicada" in a for a in avisos), avisos
