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
