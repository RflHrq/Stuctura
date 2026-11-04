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


def test_nao_aprova_pergunta_que_ja_esta_no_banco(tmp_path, monkeypatch):
    """I4: o portão da variedade só existia na EXPANSÃO.

    `aprova` lê de `candidatos/`, e um candidato pode ter sido expandido
    antes de o banco crescer. Ele passava pelo carregador — id novo,
    contrato em ordem — e entrava com a pergunta repetida, que é
    exatamente o que a fatia da família veio desfazer.
    """
    import shutil
    import yaml
    from mvp import dominio as mod

    espelho = tmp_path / "dominio"
    shutil.copytree(mod.RAIZ, espelho)
    monkeypatch.setattr(mod, "RAIZ", espelho)
    antes = (espelho / "activities_kc02.yaml").read_bytes()

    # Copia a pergunta de um item que JÁ está no banco, com id novo.
    arq = espelho / "activities_kc02.yaml"
    ja = yaml.safe_load(arq.read_text(encoding="utf-8"))["activities"][0]
    _candidatos_falsos(tmp_path, monkeypatch,
                       _item(revisado_por="Rafael",
                             enunciado=ja["enunciado"]))

    quantos, avisos = gerar.aprova("kc_02")
    assert quantos == 0, avisos
    assert any(ja["id"] in a for a in avisos), avisos
    assert arq.read_bytes() == antes


def test_id_que_ja_esta_no_banco_e_recusado_e_nao_pulado(tmp_path, monkeypatch):
    """Uma suspeita minha que NÃO se confirmou, virada prova.

    Consertando o I4 eu li `novos = [a for a in aprovados if a["id"] not
    in ja]` e concluí que `aprova` descartava em silêncio um id que já
    estivesse no banco — o que importaria muito, porque reexpandir um
    molde corrigido devolve os MESMOS ids com texto novo, e a correção
    se perderia sem uma palavra.

    Não é o que acontece: `confere` carrega o domínio COM os candidatos
    dentro, e o carregador de verdade recusa id duplicado antes de
    qualquer filtro. O filtro nunca é alcançado. Fica o teste, para o
    dia em que alguém mexer na ordem das duas coisas.

    O que isso significa no caminho de corrigir um molde: reexpandir e
    aprovar NÃO substitui os itens velhos — é preciso apagá-los do
    domínio primeiro, de propósito e num commit que se vê.
    """
    import shutil
    import yaml
    from mvp import dominio as mod

    espelho = tmp_path / "dominio"
    shutil.copytree(mod.RAIZ, espelho)
    monkeypatch.setattr(mod, "RAIZ", espelho)
    arq = espelho / "activities_kc02.yaml"
    antes = arq.read_bytes()
    ja = yaml.safe_load(arq.read_text(encoding="utf-8"))["activities"][0]

    _candidatos_falsos(tmp_path, monkeypatch,
                       _item(revisado_por="Rafael", id=ja["id"]))

    quantos, avisos = gerar.aprova("kc_02")
    assert quantos == 0, avisos
    assert any(ja["id"] in a and "duplicada" in a for a in avisos), avisos
    assert arq.read_bytes() == antes


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


#: O domínio curto dos testes que CHAMAM O COMPILADOR.
#:
#: Desde que o portao do oraculo varre o domínio inteiro (e nao as seis
#: variações sorteadas), cada chamada custa uma compilação por combinacao
#: por formato. Com as 27 combinações dos fixtures, a suite passou de 87
#: segundos para 12 horas e meia: sob carga sustentada o `gcc` comeca a
#: estourar o timeout de dez segundos do oraculo, e a lentidão vira
#: falha. Oito combinações exercitam o mesmo código e cabem no relógio.
#:
#: Quem precisa de domínio grande e
#: `test_o_oraculo_varre_o_domínio_inteiro_e_nao_so_as_variações`, é ele
#: declara o seu.
CURTOS = {"tipo": ["int", "char"], "nome": ["a", "v"], "n": [3, 8]}


def _molde(tmp_path, nome, **troca):
    """Escreve um `moldes_kc07.yaml` numa pasta só deste teste."""
    base = {
        "node": "B1",
        "tipo": "teorica",
        "formato": "reconhecer_conceito",
        "nivel": 1,
        "uso": "treino",
        "parametros": dict(CURTOS),
        "enunciado": "{tipo} {nome}[{n}] guarda quantos valores?",
        # Começa por palavra: o portão novo recusa molde em que a certa
        # é a única alternativa que começa em minúscula.
        "gabarito": "São {extenso} valores, um por caixa",
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
        "São {extenso} valores, um em cada caixa, e as caixas estão grudadas "
        "uma na outra desde a declaração"))
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any("mol_teste__" in p and "mais longa" in p
               for p in problemas), problemas


@tem_gcc
def test_variacao_igual_a_item_que_ja_existe_e_recusada(tmp_path):
    """O molde reproduz, palavra por palavra, um item escrito à mão."""
    # O enunciado vem do DOMÍNIO, e não copiado: corrigir uma vírgula
    # naquele item não pode quebrar um teste que não é sobre ele.
    alvo = next(a for a in D7.atividades if a.no == "B1"
                and a.uso == "diagnostico")
    pasta = _molde(tmp_path, "repetida",
                   parametros={"tipo": ["int"], "nome": ["a"], "n": [5]},
                   enunciado=alvo.enunciado)
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any(alvo.id in p for p in problemas), problemas


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
    # Domínio próprio: este teste cobra o nome mais LONGO, e o padrão
    # dos fixtures é curto para não pagar compilação. Aqui não há
    # compilador, então o domínio grande sai de graça.
    m = _le_molde(tmp_path, "folha",
                  parametros={"tipo": ["int", "char", "double"],
                              "nome": ["a", "v", "dados"],
                              "n": [3, 5, 8]})
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
    # A coleira mudou de lugar com a família: as crenças passaram a ser
    # da AFIRMAÇÃO, então o enum está nelas, e não em cada distrator.
    enum = gerar.esquema_de_molde(D7)["properties"]["crencas"]["items"]["enum"]
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


def test_item_nao_sai_com_buraco_sem_preencher(tmp_path):
    """A rede por baixo das validações, para qualquer derivado futuro.

    Hoje a carga do molde já barra `{extenso}` fora da faixa. Mas basta
    um derivado novo para o caso voltar, e o que chega à tela da pessoa
    é literalmente "{extenso} caixas de int".
    """
    from mvp import molde as mod

    m = _le_molde(tmp_path, "buraco")
    p = dict(mod.expande(m, 1)[0])
    p.pop("extenso", None)                 # como se o derivado não existisse
    item = mod.item_de(m, m.redacoes[0], p, 1)
    assert "{" in str(item["alternativas"]), item["alternativas"]
    assert gerar.sem_buraco(item) is False


def test_o_portao_barra_o_buraco_por_preencher(tmp_path, monkeypatch):
    """E o portão tem de ver isso, não só a função.

    A carga do molde já barra o único caso que existe hoje (`{extenso}`
    fora da faixa), então o portão é rede para o derivado que ainda não
    existe. O teste simula exatamente isso: o derivado deixa de ser
    preenchido, e nada mais muda.
    """
    from mvp import molde as mod

    monkeypatch.setattr(mod, "_com_extenso", lambda p: dict(p))
    pasta = _molde(tmp_path, "rede")
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any("buraco por preencher" in x for x in problemas), problemas


def test_a_certa_nao_pode_ser_a_unica_em_minuscula(tmp_path):
    """Pista de superfície sistemática sobre a resposta certa.

    Vinha do molde começar o gabarito por `{extenso}`: nas seis
    variações, a certa era a única que começava em minúscula. Num
    instrumento que mede concepção errônea, isso é dado contaminado.
    """
    pasta = _molde(tmp_path, "minuscula",
                   gabarito="{extenso} valores, um por caixa")
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any("minúscula" in p for p in problemas), problemas


def test_extremos_pega_o_valor_textual_mais_longo(tmp_path):
    """A folha promete "o nome mais longo" e mostrava o TIPO mais longo.

    A escolha era "o parâmetro textual cujo maior valor é o maior", e no
    molde real isso é `tipo` (double, 6) e não `nome` (dados, 5). Quem
    revisa podia nunca ler o extremo que a folha diz que está lendo.
    """
    # `tipo` tem valores mais longos que `nome` em média — era o que
    # fazia a escolha antiga pegar o tipo e nunca o nome comprido.
    m = _le_molde(tmp_path, "textual", parametros={
        "tipo": ["int", "unsigned"], "nome": ["a", "bb", "comprimento"],
        "n": [3, 8]})
    tres = gerar.extremos(m)
    assert any(p["nome"] == "comprimento" for p in tres), tres


def test_extremos_nao_expande_o_produto_inteiro(tmp_path):
    """Era quártico: 1000 combinações levavam dois minutos, e é ele que
    trava o portão humano — a folha ficava sem imprimir nada."""
    import time

    m = _le_molde(tmp_path, "grande", parametros={
        "tipo": ["int", "char", "double", "long", "float"],
        "nome": ["a", "v", "dados", "lista", "buf", "entrada"],
        "n": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "qual": ["x", "y", "z", "w"]})          # 1200 combinações
    t0 = time.perf_counter()
    tres = gerar.extremos(m)
    assert time.perf_counter() - t0 < 2.0, "extremos ainda é quártico"
    assert len(tres) == 3
    assert [p["n"] for p in tres[:2]] == [1, 10]


def test_duas_variacoes_com_a_mesma_pergunta_e_respostas_diferentes(tmp_path):
    """A metade interna do portão da variedade, que não tinha teste.

    Molde cujo enunciado não usa todos os parâmetros: aqui o `tipo` varia
    só no gabarito. Duas variações saem com a MESMA pergunta e respostas
    certas diferentes — item ambíguo, e quem responde não tem como
    acertar as duas.
    """
    pasta = _molde(tmp_path, "ambigua",
                   parametros={"tipo": ["int", "char"], "nome": ["a"],
                               "n": [5]},
                   enunciado="O que {nome}[{n}] guarda?")
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste", raiz=pasta)
    assert itens == []
    assert any("do mesmo molde" in p for p in problemas), problemas


def test_sem_compilador_a_cli_nao_cospe_traceback(tmp_path, monkeypatch, capsys):
    """Foco 3 do plano, de ponta a ponta.

    A mensagem boa existia dentro do oráculo e saía debaixo de um
    traceback: quem rodasse `--expandir` noutra máquina veria a pilha, e
    a instrução no rodapé.
    """
    import oraculo as orac

    monkeypatch.setattr(gerar, "CANDIDATOS", tmp_path / "cand")
    monkeypatch.setattr(orac, "GCC", tmp_path / "nao" / "existe" / "gcc.exe")
    monkeypatch.setattr(gerar, "RAIZ", gerar.RAIZ)

    with pytest.raises(SystemExit) as saida:
        gerar.expande_molde(D7, "kc_07", "mol_kc07_B1_treino_1")
    assert "STRUCTURA_GCC" in str(saida.value)


# --------------------------------------------------------------------------
# Os portões, por redação
# --------------------------------------------------------------------------

def _familia(tmp_path, nome, **troca):
    """Escreve a família de três formatos do kc_07 numa pasta do teste.

    Com o domínio curto por padrão: o fixture de `test_molde` tem 27
    combinações, e aqui cada uma custa três compilações. Quem precisa de
    domínio grande passa o seu.
    """
    from mvp.test_molde import _cru_familia

    troca.setdefault("parametros", dict(CURTOS))
    pasta = tmp_path / nome
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "moldes_kc07.yaml").write_text(
        _yaml.safe_dump({"mol_teste": _cru_familia(**troca)},
                        allow_unicode=True, sort_keys=False),
        encoding="utf-8")
    return pasta


@tem_gcc
def test_a_familia_inteira_passa_nos_quatro_portoes(tmp_path):
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste",
                                           raiz=_familia(tmp_path, "ok"))
    assert problemas == [], problemas
    assert len(itens) == 6
    assert {i["formato"] for i in itens} == {
        "reconhecer_conceito", "achar_o_erro", "prever_saida"}


@tem_gcc
def test_uma_redacao_reprovada_derruba_a_familia(tmp_path):
    """A mesma regra da fatia anterior, um nível acima.

    Ficar com os formatos que passaram esconde a afirmação errada
    exatamente como ficar com as variações que passaram escondia.
    """
    from mvp.test_molde import _cru_familia

    formatos = _cru_familia()["formatos"]
    # o programa do achar_o_erro passa a COMPILAR: o item perde o erro
    formatos["achar_o_erro"]["oraculo"] = "int main(void) { return 0; }"
    itens, problemas = gerar.expande_molde(
        D7, "kc_07", "mol_teste", raiz=_familia(tmp_path, "ruim",
                                                formatos=formatos))
    assert itens == []
    assert any("achar_o_erro" in p for p in problemas), problemas


@tem_gcc
def test_o_gabarito_do_prever_saida_vem_do_programa(tmp_path):
    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste",
                                           raiz=_familia(tmp_path, "prev"))
    assert problemas == [], problemas
    prev = [i for i in itens if i["formato"] == "prever_saida"]
    assert prev
    for item in prev:
        esperado = str(item["parametros"]["n"])
        assert item["alternativas"]["a"] == esperado, item


@tem_gcc
def test_saida_que_nao_serve_de_alternativa_reprova(tmp_path):
    """Foco 4: a saída existe, o oráculo passa, e mesmo assim ela não
    pode virar a alternativa certa."""
    from mvp.test_molde import _cru_familia

    # A saída longa, e não a vazia: desde que a carga cobra que o
    # oráculo confira o programa MOSTRADO, uma saída vazia só sai de um
    # oráculo que não mostra nada — e esse nem carrega. A frase inteira
    # cabe no programa, passa no oráculo, e não cabe num botão.
    linha = ('printf("sao %zu caixas de {tipo} chamadas {nome}, grudadas uma '
             'na outra, e o compilador nao reclama",'
             ' sizeof {nome} / sizeof {nome}[0]);')
    formatos = _cru_familia()["formatos"]
    formatos["prever_saida"]["codigo"] = "{tipo} {nome}[{n}];" + chr(10) + linha
    formatos["prever_saida"]["oraculo"] = (
        "#include <stdio.h>" + chr(10) +
        "int main(void) {" + chr(10) +
        "    {tipo} {nome}[{n}];" + chr(10) +
        "    " + linha + chr(10) +
        "    return 0;" + chr(10) + "}" + chr(10))
    formatos["prever_saida"]["espera"] = (
        "sao {n} caixas de {tipo} chamadas {nome}, grudadas uma na outra, "
        "e o compilador nao reclama")
    itens, problemas = gerar.expande_molde(
        D7, "kc_07", "mol_teste",
        raiz=_familia(tmp_path, "longa", formatos=formatos))
    assert itens == []
    assert any("alternativa" in p for p in problemas), problemas


def test_a_folha_da_familia_mostra_os_extremos_e_um_de_cada_formato(tmp_path):
    """A pessoa valida a AFIRMAÇÃO, que é uma só — e lê os extremos num
    formato, mais uma amostra de cada um dos outros."""
    from mvp.molde import le

    m = le(_familia(tmp_path, "folha") / "moldes_kc07.yaml", D7)["mol_teste"]
    texto = gerar.folha_do_molde(D7, m)
    assert texto.count("## formato") == 3, texto
    assert texto.count("### variação") == 5, texto     # 3 + 1 + 1
    assert "revisado_sha: %s" % m.digest in texto
    # as crenças são DECLARADAS uma vez, no topo, com o nó que cada uma
    # nega — é o que a pessoa valida, e é por isso que uma assinatura
    # cobre a família inteira. (Elas reaparecem ao lado de cada
    # distrator, que é onde ajudam a ler.)
    assert "`string_literal_is_array` → nega B1" in texto, texto
    assert "`array_is_pointer` → nega I3" in texto, texto
    assert texto.count("## A afirmação") == 1, texto


def test_a_folha_da_familia_de_um_continua_inteira(tmp_path):
    """O molde de formato único não perde nada com a mudança."""
    m = _le_molde(tmp_path, "folha_um")
    texto = gerar.folha_do_molde(D7, m)
    assert texto.count("### variação") == 3
    assert texto.count("## formato") == 1


# --------------------------------------------------------------------------
# O prompt pede a família
# --------------------------------------------------------------------------

def test_o_esquema_pede_um_mapa_de_formatos():
    e = gerar.esquema_de_molde(D7)
    assert "formatos" in e["required"]
    assert "crencas" in e["required"]


def test_o_pedido_explica_a_correspondencia_posicional():
    """Sem isso o modelo escreve distratores na ordem que quiser, e a
    correspondência com as crenças vira sorteio."""
    sistema, pedido = gerar.prompt_de_molde(D7, "B1", 1)
    assert "mesma ordem" in (sistema + pedido).lower()


def test_o_pedido_explica_o_achar_o_erro():
    sistema, pedido = gerar.prompt_de_molde(D7, "B1", 1)
    assert "nao_compila" in (sistema + pedido)


@tem_gcc
def test_o_oraculo_varre_o_dominio_inteiro_e_nao_so_as_variacoes(tmp_path):
    """C4: o portão conferia as variações SORTEADAS e dizia molde provado.

    O molde afirma uma coisa sobre 4 combinações de parâmetro; a
    expansão sorteia 2; o portão rodava o compilador nessas 2 e aprovava
    as 4. Uma afirmação falsa numa combinação não sorteada entrava no
    banco escrita no molde, esperando a próxima expansão — que é
    exatamente o que a camada do oráculo existe para impedir.

    Este é o defeito que estava no molde de verdade: `sizeof {nome} !=
    sizeof p` é falso para `char {nome}[8]`, porque os dois ocupam oito
    bytes. Uma em dezesseis, e a expansão não a sorteou.
    """
    from mvp.molde import le, expande_familia

    oraculo_do_tamanho = (
        "#include <stdio.h>" + chr(10) +
        "int main(void) {" + chr(10) +
        "    {tipo} {nome}[{n}];" + chr(10) +
        "    {tipo} *p;" + chr(10) +
        "    printf(" + chr(34) + "%d" + chr(34) +
        ", (int)(sizeof {nome} != sizeof p));" + chr(10) +
        "    return 0;" + chr(10) + "}" + chr(10))
    formatos = {
        "reconhecer_conceito": {
            "tipo": "teorica",
            "enunciado": "Depois de {tipo} {nome}[{n}]; e {tipo} *p; o que existe?",
            "gabarito": "São {extenso} caixas de {tipo}, e uma de ponteiro",
            "distratores": [
                "Uma caixa só, com {extenso} valores de {tipo} dentro",
                "Duas caixas de ponteiro: {nome} também é um ponteiro",
            ],
            "codigo": "{tipo} {nome}[{n}];" + chr(10) + "{tipo} *p;",
            "oraculo": oraculo_do_tamanho,
            "espera": "1",
        },
    }
    # O mesmo domínio do molde de verdade: 64 combinações.
    parametros = {"tipo": ["int", "char", "double", "long"],
                  "nome": ["a", "v", "dados", "lista"],
                  "n": [3, 4, 6, 8]}
    raiz = _familia(tmp_path, "varre", formatos=formatos,
                    parametros=parametros)

    # A expansão sorteia duas das 64, e nenhuma delas é char[8].
    m = le(raiz / "moldes_kc07.yaml", D7)["mol_teste"]
    sorteadas = [(p["tipo"], p["n"]) for _, p in expande_familia(m, 2)]
    assert len(sorteadas) == 2
    assert ("char", 8) not in sorteadas, sorteadas

    itens, problemas = gerar.expande_molde(D7, "kc_07", "mol_teste",
                                           raiz=raiz, quantas=2)
    assert itens == []
    assert any("char" in p and "8" in p for p in problemas), problemas


@tem_gcc
def test_a_varredura_diz_quantas_combinacoes_conferiu(tmp_path):
    """E a folha não pode prometer mais do que a máquina provou.

    Com o domínio inteiro conferido, o relatório diz 4 de 4. É esse
    número que a folha da validação passa a mostrar, no lugar de "em
    TODA variação" — que era verdade sobre as sorteadas e mentira sobre
    o molde.
    """
    conferidas = gerar.combinacoes_do_oraculo(
        {"tipo": ["int", "char"], "nome": ["a"], "n": [3, 8]})
    assert len(conferidas) == 4
    assert {"tipo": "char", "nome": "a", "n": 8} in conferidas


def test_a_folha_diz_quantas_combinacoes_a_maquina_conferiu(tmp_path):
    """I3: a folha dizia "em TODA variação", e não era verdade.

    O portão conferia as variações expandidas. A folha, que é o que a
    pessoa lê antes de assinar, dizia que a máquina tinha conferido
    todas — e a assinatura dela passava a cobrir uma garantia que
    ninguém deu. Agora o número é o da varredura, e sai escrito.
    """
    from mvp.molde import le

    m = le(_familia(tmp_path, "folha_n") / "moldes_kc07.yaml", D7)["mol_teste"]
    texto = gerar.folha_do_molde(D7, m)
    # O número sai do fixture, e não cravado: foi o defeito que a
    # revisão apontou nos testes de conteúdo, e eu acabei de repeti-lo
    # no teste que o conserta.
    quantas = len(gerar.combinacoes_do_oraculo(m.parametros))
    assert str(quantas) in texto, (quantas, texto)
    assert "TODA" not in texto, texto


def test_a_folha_mostra_o_espera_de_cada_formato(tmp_path):
    """E o `espera` do formato ficava escondido.

    A folha mostrava o `espera` da família e, para o formato com oráculo
    próprio, só o programa. A pessoa lia um programa sem saber o que ele
    tem de imprimir para o molde passar — que é metade da afirmação.
    """
    from mvp.molde import le

    m = le(_familia(tmp_path, "folha_e") / "moldes_kc07.yaml", D7)["mol_teste"]
    texto = gerar.folha_do_molde(D7, m)
    prever = texto.split("## formato: prever_saida")[1]
    assert "espera" in prever.split("## formato")[0], prever[:600]
