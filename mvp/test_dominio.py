"""A carga do domínio, e as invariantes que ela cobra.

O princípio: **falha na carga, nunca em sessão**. Um YAML inconsistente
derruba o processo antes de qualquer participante ver a tela — o que não
pode acontecer é um erro de catálogo virar diagnóstico errado no meio de
uma coleta, em silêncio.

Cada invariante do PRD tem aqui um domínio que a quebra. Os domínios
inválidos são montados a partir do real, com uma mutação cirúrgica: assim
o teste falha pelo motivo que diz, e não porque esqueci uma chave.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

import os
import sys

import yaml

from mvp.dominio import RAIZ, DominioInvalido, carrega, topicos

ARQUIVOS = ("topic_kc00.yaml", "graph_kc00.yaml",
            "beliefs_kc00.yaml", "activities_kc00.yaml")


@pytest.fixture(scope="module")
def d():
    return carrega()


def monta(destino: Path, muda=None) -> Path:
    """Copia o domínio real para `destino`, aplicando uma mutação.

    `muda` recebe os quatro YAMLs já desserializados, num dicionário por
    nome de arquivo, e altera o que quiser.
    """
    cru = {nome: yaml.safe_load((RAIZ / nome).read_text(encoding="utf-8"))
           for nome in ARQUIVOS}
    if muda:
        muda(copy.deepcopy(cru) if False else cru)
    destino.mkdir(parents=True, exist_ok=True)
    for nome, dado in cru.items():
        (destino / nome).write_text(
            yaml.safe_dump(dado, allow_unicode=True, sort_keys=False),
            encoding="utf-8")
    return destino


def atividade(cru: dict, aid: str) -> dict:
    return next(a for a in cru["activities_kc00.yaml"]["activities"]
                if a["id"] == aid)


# --------------------------------------------------------------------------
# P1-1: a crença é da alternativa, não do item
# --------------------------------------------------------------------------

def test_dois_distratores_do_mesmo_item_podem_apontar_crencas_diferentes(d):
    """O achado P1-1, virado teste.

    Antes, toda alternativa errada recebia a crença do item inteiro: as duas
    erradas ficavam indistinguíveis, e a camada de razão não teria de onde
    sair. Este item é o caso: um distrator é sobre valor e memória, o outro
    é sobre tipo e tamanho — ideias diferentes, nós diferentes.
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    por_crenca = {o.crenca for o in a.opcoes if not o.correta}
    assert por_crenca == {"no_value_no_memory", "type_is_a_hint"}


def test_a_alternativa_certa_nunca_carrega_crenca(d):
    for a in d.atividades:
        certa = next(o for o in a.opcoes if o.correta)
        assert certa.crenca is None, a.id


def test_a_crenca_do_item_e_a_que_nega_o_proprio_no(d):
    """`Atividade.crenca` passa a ser DERIVADA das alternativas.

    É a crença que, entre os distratores do item, nega o nó que o item mira.
    Um distrator que nega outro nó não vira a crença do item: ele é
    informação sobre o vizinho, e quem trata disso é a camada de razão.
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    assert a.no == "B1"
    assert a.crenca == "type_is_a_hint"      # nega B1
    assert any(o.crenca == "no_value_no_memory" for o in a.opcoes)   # nega B2


def test_um_item_cujos_distratores_so_negam_vizinhos_nao_tem_crenca(d):
    """Errar aqui não é evidência sobre B1: os dois distratores são sobre B2.

    Sem crença no item, o motor atual trata o erro como lacuna — que é o
    comportamento correto enquanto a camada de razão não existe (T2).
    """
    a = next(x for x in d.atividades if x.id == "ciu_kc00_001")
    assert a.no == "B1"
    assert a.crenca is None
    assert {o.crenca for o in a.opcoes if not o.correta} == {"no_value_no_memory"}


# --------------------------------------------------------------------------
# A crença nova de B1, e o distrator que saiu
# --------------------------------------------------------------------------

def test_b1_ganhou_crenca_propria_declarada_como_hipotese(d):
    c = d.crencas["type_is_a_hint"]
    assert c.nega == "B1"
    # E: elaborada a partir do modelo de máquina, hipótese a testar. É a
    # primeira do catálogo, e é honesto que seja — não há fonte empírica.
    assert c.procedencia == "E"


def test_todo_no_com_crenca_tem_analogia_de_resgate(d):
    for c in d.crencas.values():
        assert d.resgate(c.nega), c.nega


def test_o_distrator_vazio_saiu(d):
    """"Porque o nome b vem depois no alfabeto" não é ideia que alguém
    sustente. Como alternativa é inofensiva; como RAZÃO seria uma opção que
    ninguém escolhe, e enfraquece o item."""
    textos = [o.texto.lower() for a in d.atividades for o in a.opcoes]
    assert not any("alfabeto" in t for t in textos)


# --------------------------------------------------------------------------
# As invariantes, cada uma com um domínio que a quebra
# --------------------------------------------------------------------------

def test_invariante_1_uma_crenca_nega_exatamente_um_no(tmp_path):
    def muda(cru):
        for b in cru["beliefs_kc00.yaml"]:
            if b["id"] == "declaration_zeroes":
                b["negates"] = "kc_00:B4"      # o grafo diz B3
    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "d1", muda))
    assert any("declaration_zeroes" in p for p in erro.value.problemas)


def test_invariante_2_toda_crenca_aparece_em_alguma_alternativa(tmp_path):
    def muda(cru):
        for a in cru["activities_kc00.yaml"]["activities"]:
            a["crencas"] = {k: v for k, v in (a.get("crencas") or {}).items()
                            if v != "variable_remembers"}
    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "d2", muda))
    assert any("variable_remembers" in p for p in erro.value.problemas)


def test_invariante_3_todo_no_tem_duas_superficies(tmp_path):
    def muda(cru):
        atv = cru["activities_kc00.yaml"]["activities"]
        cru["activities_kc00.yaml"]["activities"] = [
            a for a in atv if a["id"] != "ciu_kc00_t06"]
    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "d3", muda))
    assert any("B3" in p and "formato" in p for p in erro.value.problemas)


def test_uma_crenca_so_pode_ser_apontada_por_alternativa_errada(tmp_path):
    def muda(cru):
        a = atividade(cru, "ciu_kc00_002")
        a["crencas"]["b"] = "type_is_a_hint"      # b é o gabarito
    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "d4", muda))
    assert any("gabarito" in p for p in erro.value.problemas)


def test_crenca_de_alternativa_precisa_existir_no_catalogo(tmp_path):
    def muda(cru):
        atividade(cru, "ciu_kc00_002")["crencas"]["c"] = "nao_existe"
    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "d5", muda))
    assert any("nao_existe" in p for p in erro.value.problemas)


def test_crenca_nao_pode_apontar_alternativa_inexistente(tmp_path):
    def muda(cru):
        atividade(cru, "ciu_kc00_002")["crencas"]["z"] = "type_is_a_hint"
    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "d6", muda))
    assert any("'z'" in p or '"z"' in p for p in erro.value.problemas)


def test_o_dominio_real_carrega_sem_problema():
    """A contraprova das seis acima: o domínio de verdade passa por todas."""
    assert carrega().id == "kc_00"


# --------------------------------------------------------------------------
# Mais de um tópico
#
# O carregador tinha os nomes `*_kc00.yaml` fixos no código, o que bastava
# enquanto havia um tópico só. O kc_02 é o segundo.
# --------------------------------------------------------------------------

def test_carrega_o_topico_pelo_nome():
    """E o padrão continua sendo o kc_00: nada do que existia muda."""
    assert carrega().id == "kc_00"
    assert carrega(topico="kc_02").id == "kc_02"


def test_o_id_do_topico_e_o_nome_do_arquivo_podem_divergir():
    """`kc_02` é o id; `topic_kc02.yaml` é o arquivo. As duas formas valem,
    porque a convenção veio do kc_00 e um tópico novo não pode quebrar por
    causa de um underscore."""
    assert carrega(topico="kc02").id == "kc_02"


def test_topico_que_nao_existe_falha_na_carga():
    """Falha na carga, nunca em sessão — inclusive quando o que falta é o
    arquivo inteiro."""
    with pytest.raises(DominioInvalido) as erro:
        carrega(topico="kc_99")
    assert any("kc_99" in p for p in erro.value.problemas)


# --------------------------------------------------------------------------
# A qualidade do banco dos tópicos POSTERIORES AO CONTRATO
#
# Estas quatro cobram o contrato de docs/linguagem.md. Valem para todo
# tópico escrito depois dele — kc_01, kc_02 e kc_03 — e ainda NÃO para o
# kc_00, que tem dívida registrada na revisão: 1 item sem a crença do
# próprio nó, 1 distrator sem crença, 9 itens em que a certa é a mais longa
# com folga e 13 itens binários. O banco dele é anterior ao contrato.
#
# Cada tópico novo entra nesta lista, e é aqui que ele passa a ser cobrado.
# --------------------------------------------------------------------------

POS_CONTRATO = tuple(t for t in topicos() if t != "kc_00")

# Os que tem a escada inteira (um item por degrau) E item de entrada em
# todo no. O kc_00 e o kc_02 ficam de fora: os bancos deles vieram antes
# do item de entrada, e a divida esta registrada.
ESCADA_COMPLETA = tuple(t for t in topicos()
                        if t not in ("kc_00", "kc_02"))


@pytest.mark.parametrize("topico", POS_CONTRATO)
def test_todo_item_de_diagnostico_oferece_a_crenca_do_proprio_no(topico):
    """Sem isto, o nó não recebe atribuição: as razões da camada 2 saem das
    alternativas do item (`motor.razoes_de`), então um item que só oferece a
    crença do vizinho manda toda razão errada para outro nó. Os itens do nó
    se gastam e ele termina `desconhecido` — foi o que a revisão final mediu
    em 9 de 30 sessões do kc_00."""
    d = carrega(topico=topico)
    sem = [a.id for a in d.atividades if a.uso == "diagnostico"
           and not any(o.crenca and d.crencas[o.crenca].nega == a.no
                       for o in a.opcoes)]
    assert sem == [], sem


@pytest.mark.parametrize("topico", POS_CONTRATO)
def test_nenhum_distrator_de_diagnostico_fica_sem_crenca(topico):
    """Distrator sem crença é erro sem diagnóstico — e, pior, encolhe a
    camada 2, que é montada das alternativas. No treino é aceitável: lá a
    camada 2 não roda."""
    d = carrega(topico=topico)
    sem = [(a.id, o.texto[:40]) for a in d.atividades if a.uso == "diagnostico"
           for o in a.opcoes if not o.correta and not o.crenca]
    assert sem == [], sem


@pytest.mark.parametrize("topico", POS_CONTRATO)
def test_a_alternativa_certa_nao_e_a_mais_longa_com_folga(topico):
    """A pista mais comum de todas: dá para acertar contando palavras."""
    d = carrega(topico=topico)
    pistas = []
    for a in d.atividades:
        tams = sorted((len(o.texto), o.correta) for o in a.opcoes)
        segundo = tams[-2][0] if len(tams) > 1 else 0
        if tams[-1][1] and tams[-1][0] > segundo * 1.2:
            pistas.append(a.id)
    assert pistas == [], pistas


@pytest.mark.parametrize("topico", POS_CONTRATO)
def test_nao_tem_item_binario(topico):
    """13 dos 20 itens do kc_00 têm duas alternativas: dois terços do banco
    em cara ou coroa na camada 1."""
    d = carrega(topico=topico)
    assert [a.id for a in d.atividades if len(a.opcoes) == 2] == []


# --------------------------------------------------------------------------
# A ESCADA, em todo tópico que a tem
#
# A pessoa que atravessou a unidade primeiro disse, nessas palavras, que
# parecia "entrar no chefão já". O carregador já cobra o degrau 1; o que
# falta cobrar é a escada INTEIRA, degrau por degrau, sem buraco no meio.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", ESCADA_COMPLETA)
def test_a_escada_de_diagnostico_nao_tem_buraco(topico):
    """Nó com item de nível 3 e sem item de nível 2 faz o motor pular um
    degrau — e `_no_degrau` registra o pulo, mas o salto já aconteceu."""
    d = carrega(topico=topico)
    buracos = []
    for nid in d.nos:
        graus = sorted({a.nivel for a in d.atividades_do_no(nid, "diagnostico")})
        if graus != list(range(1, len(graus) + 1)):
            buracos.append((nid, graus))
    assert buracos == [], buracos


@pytest.mark.parametrize("topico", ESCADA_COMPLETA)
def test_todo_no_tem_item_de_entrada(topico):
    """O item de entrada é o que a pessoa responde DEPOIS do ensino, quando
    declarou que não sabe. Sem ele a construção ensina e não mede — e é
    dívida aberta do kc_00 e do kc_02."""
    d = carrega(topico=topico)
    sem = [nid for nid in d.nos if not d.atividades_do_no(nid, "entrada")]
    assert sem == [], sem


# --------------------------------------------------------------------------
# A lista de tópicos sai do DISCO
#
# Cada tópico novo precisava entrar à mão em seis listas de teste
# espalhadas, e duas estavam defasadas: o kc_03 e o kc_04 nunca tinham
# sido varridos pelos testes de construção e de escada. Lista escrita à
# mão é lista que envelhece, e o jeito de ela não envelhecer é não existir.
# --------------------------------------------------------------------------

def test_a_lista_de_topicos_sai_dos_arquivos():
    """E carrega cada um. Se o glob achar um nome que o carregador recusa,
    é aqui que aparece — não numa sessão."""
    achados = topicos()
    assert len(achados) >= 6, achados
    assert achados == tuple(sorted(achados)), "fora de ordem"
    for t in achados:
        assert carrega(topico=t).id == t


def test_topico_novo_no_disco_entra_na_lista_sozinho(tmp_path):
    """A garantia que faz a lista valer a pena: ninguém precisa lembrar."""
    (tmp_path / "topic_kc99.yaml").write_text("id: kc_99\n", encoding="utf-8")
    assert topicos(tmp_path) == ("kc_99",)


# --------------------------------------------------------------------------
# NENHUM TÓPICO-PILOTO TEM CRENÇA ESTIMADA
#
# Piloto é o que a coleta usa e o que vai para a monografia. Crença `E` é
# hipótese sem fonte: declarar uma como achado seria afirmar sobre a
# literatura o que a literatura não diz.
#
# As duas que o kc_02 tinha foram resolvidas quando a busca foi refeita com
# outro vocabulário — `pointer_has_no_address` estava na segunda frase do
# item 14 do Sorva ("It is not stored inside the computer"), e
# `pointer_is_pointless` é a primeira pergunta da seção de ponteiros do
# FAQ de C. As duas que restam no projeto estão no kc_00 e no kc_01, que
# não são piloto, e o que foi procurado para elas está escrito no
# `beliefs_kc02.yaml`.
# --------------------------------------------------------------------------

PILOTOS = ("kc_02", "kc_07", "kc_09", "kc_11")


@pytest.mark.parametrize("topico", PILOTOS)
def test_piloto_nao_tem_crenca_estimada(topico):
    """Se alguém marcar uma crença de piloto como `E`, é aqui que cai."""
    d = carrega(topico=topico)
    estimadas = [c.id for c in d.crencas.values() if c.procedencia == "E"]
    assert estimadas == [], estimadas


@pytest.mark.parametrize("topico", PILOTOS)
def test_toda_crenca_de_piloto_tem_fonte_escrita(topico):
    """Procedência sem fonte é procedência sem valor. A `D`, a `L`, a `T` e
    a `N` todas afirmam algo sobre onde a crença está registrada, e o campo
    `source` é onde isso fica."""
    d = carrega(topico=topico)
    sem = [c.id for c in d.crencas.values() if len(c.fonte) < 40]
    assert sem == [], sem


# --------------------------------------------------------------------------
# O ESCOPO DE SESSÃO POR PREMISSA
#
# `docs/plano-tcc.md` define a unidade da coleta em quatro estágios —
# ensina (2 telas), pratica (4 a 6), refuta (3 a 5), fecha (1) — e a sessão
# como DUAS unidades em cerca de 30 minutos. Medido, um nó custa 14 telas,
# das quais 10 são desses quatro estágios: a unidade do plano é UMA
# PREMISSA, não um tópico inteiro. O motor sempre rodou o tópico inteiro, e
# continua rodando por padrão; o escopo é o que permite parar em N.
#
# O corte é por PREFIXO da ordem do grafo, e o motivo é o fechamento do
# suporte: prefixo garante que nenhuma inferência fique sem a premissa que
# a sustenta. Nos treze tópicos não há N que quebre isso — e se um dia
# houver, a carga recusa.
# --------------------------------------------------------------------------

def test_sem_escopo_a_sessao_e_o_topico_inteiro():
    """O padrão não muda: quem não pede escopo recebe o tópico todo."""
    for t in topicos():
        d = carrega(topico=t)
        inteiro = len(yaml.safe_load(
            (RAIZ / ("graph_%s.yaml" % t.replace("_", "")))
            .read_text(encoding="utf-8"))["nodes"])
        assert len(d.nos) == inteiro, t


@pytest.mark.parametrize("quantas", [1, 2, 3, 4, 5, 6])
def test_o_escopo_para_em_n_premissas(quantas):
    """E o que fica é o PREFIXO da ordem, com crenças e itens dos nós que
    ficaram — nada do que saiu."""
    inteiro = carrega(topico="kc_12")
    d = carrega(topico="kc_12", premissas=quantas)
    assert d.ordem == inteiro.ordem[:quantas]
    assert len(d.crencas) == quantas
    assert {c.nega for c in d.crencas.values()} == set(d.ordem)
    assert {a.no for a in d.atividades} == set(d.ordem)


def test_o_escopo_move_a_conclusao_para_a_ultima_premissa_que_fica():
    """Conclusão que saiu no corte deixaria o mapa e o teach-back apontando
    para um nó que não existe."""
    for quantas in (1, 3, 5):
        d = carrega(topico="kc_12", premissas=quantas)
        assert d.conclusao == d.ordem[-1]
    assert carrega(topico="kc_12", premissas=6).conclusao == "I3"


@pytest.mark.parametrize("pedido", [0, -1, 99, "dois", "1", 1.0, True])
def test_o_escopo_recusa_pedido_sem_sentido(pedido):
    """Falha na carga, nunca em sessão. `True` entra na lista de propósito:
    em Python ele é um inteiro, e `premissas=True` é erro de digitação, não
    um pedido de uma premissa."""
    with pytest.raises(DominioInvalido):
        carrega(topico="kc_12", premissas=pedido)


def test_o_escopo_recusa_corte_que_deixaria_suporte_de_fora(tmp_path):
    """A garantia que faz o prefixo valer. Nos treze tópicos de hoje não há
    corte que quebre o suporte — este domínio é montado à mão para que
    haja, e o teste morde o caminho da recusa."""
    dom = tmp_path / "dominio"
    dom.mkdir()
    (dom / "topic_kc99.yaml").write_text(
        "id: kc_99\ntitle: t\nconclusion_node: I2\nteachback: q\n",
        encoding="utf-8")
    # ordem = [B1, I1, I2]; premissas=2 fica com B1 e I1, e I1 depende de I2
    (dom / "graph_kc99.yaml").write_text(
        "topic: kc_99\nnodes:\n"
        "  B1:\n    type: observavel\n    support: []\n    text: b\n"
        "  I1:\n    type: inferencia\n    support: [I2]\n    text: i1\n"
        "  I2:\n    type: inferencia\n    support: [B1]\n    text: i2\n",
        encoding="utf-8")
    (dom / "beliefs_kc99.yaml").write_text("[]\n", encoding="utf-8")
    (dom / "activities_kc99.yaml").write_text("activities: []\n",
                                              encoding="utf-8")

    with pytest.raises(DominioInvalido) as erro:
        carrega(dom, topico="kc_99", premissas=2)

    # E a MENSAGEM tem de ser a do corte, nao a da invariante geral.
    #
    # Sem a checagem do corte isto falharia assim mesmo: a invariante
    # geral do carregador ("no I1: suporte 'I2' nao existe") dispara de
    # qualquer jeito, e a mensagem estaria ERRADA — o suporte existe no
    # topico, e foi o corte que o tirou. Quem lesse "nao existe" iria
    # procurar erro no YAML. Por isso o teste cobra a palavra, e nao so
    # a excecao: foi uma sabotagem que passou limpa e mostrou que a
    # assercao era fraca.
    problemas = erro.value.problemas
    assert any("corta" in p and "sustenta" in p for p in problemas), problemas
    assert any("premissas=2" in p for p in problemas), problemas


@pytest.mark.parametrize("topico", topicos())
def test_o_escopo_vale_para_todo_topico_e_todo_n(topico):
    """Cortar não pode produzir domínio inválido em nenhum tópico: as
    invariantes da carga rodam no domínio CORTADO, de propósito."""
    inteiro = carrega(topico=topico)
    for quantas in range(1, len(inteiro.nos) + 1):
        d = carrega(topico=topico, premissas=quantas)
        assert len(d.nos) == quantas, (topico, quantas)


def test_o_escopo_vem_do_ambiente_quando_ninguem_pede():
    """É assim que o servidor recebe o escopo:

        STRUCTURA_TOPICO=kc_12 STRUCTURA_PREMISSAS=2 python -m mvp.app

    EM SUBPROCESSO, e não com `importlib.reload`. A primeira versão deste
    teste recarregava o módulo, e isso derrubou seis testes do gerador:
    o `scripts/gerar.py` faz `from mvp.dominio import carrega,
    DominioInvalido`, e depois do reload ele continua apontando para a
    função e a CLASSE antigas — então o `pytest.raises` com a classe nova
    deixa de pegar a exceção da antiga. Recarregar módulo no meio da suíte
    é efeito colateral em todo mundo que importou dele.
    """
    import subprocess

    def roda(env_extra, pedido):
        codigo = (
            "from mvp.dominio import PREMISSAS_PADRAO, carrega;"
            "print(PREMISSAS_PADRAO, len(carrega(topico='kc_12'%s).nos))"
            % pedido)
        amb = dict(os.environ, **env_extra)
        r = subprocess.run([sys.executable, "-c", codigo], cwd=str(RAIZ.parent.parent),
                           capture_output=True, text=True, env=amb)
        assert r.returncode == 0, r.stderr
        return r.stdout.split()

    assert roda({"STRUCTURA_PREMISSAS": "2"}, "") == ["2", "2"]
    # o argumento explícito ganha do ambiente
    assert roda({"STRUCTURA_PREMISSAS": "2"}, ", premissas=4") == ["2", "4"]
    # sem a variável, o padrão é o tópico inteiro
    amb = {k: v for k, v in os.environ.items() if k != "STRUCTURA_PREMISSAS"}
    assert roda(amb, "")[0] == "None"


# --------------------------------------------------------------------------
# Marcação: o que vai para a tela se escreve sem enfeite
# --------------------------------------------------------------------------

def textos_de_tela(d):
    """Todo texto deste tópico que alguma tela escreve, com o caminho.

    FORA DAQUI, de propósito: `Crenca.fonte`. Ela é a citação da
    procedência — lida no YAML e nos docs por quem pesquisa, e nenhuma
    tela a mostra, nem o painel. Marcação em texto que se lê como texto
    é marcação útil, e é por isso que a regra é "o que vai para a TELA",
    e não "o domínio inteiro".
    """
    yield "titulo", d.titulo
    yield "teachback", d.teachback
    yield "analogia", d.analogia
    for nid, no in d.nos.items():
        yield "nos/%s/texto" % nid, no.texto
        yield "nos/%s/simples" % nid, no.simples
    for cid, c in d.crencas.items():
        yield "crencas/%s/afirma" % cid, c.afirma
    for a in d.atividades:
        yield "%s/enunciado" % a.id, a.enunciado
        yield "%s/codigo" % a.id, a.codigo
        for i, o in enumerate(a.opcoes):
            yield "%s/opcao[%d]" % (a.id, i), o.texto
    for nid, texto in d.resgates.items():
        yield "resgates/%s" % nid, texto
    for nid, texto in d.exemplos.items():
        yield "exemplos/%s" % nid, texto
    for cid, desc in d.descidas.items():
        for i, p in enumerate(desc.passos, 1):
            for campo in ("pergunta", "decorre", "verdade", "porque"):
                yield "descida/%s/%d/%s" % (cid, i, campo), getattr(p, campo)
        ev = desc.evidencia
        for campo in ("fonte", "comando", "afirmacao", "garantia",
                      "saida", "onde"):
            yield "descida/%s/evidencia/%s" % (cid, campo), getattr(ev, campo)


@pytest.mark.parametrize("topico", topicos())
def test_nenhum_texto_de_tela_usa_crase(topico):
    """O cliente escreve com `textContent`: crase no YAML vira crase na
    cara da pessoa.

    Não é hipótese — foi visto na tela, rodando a descida do kc_07: a
    pergunta saiu com os acentos graves no meio da frase. A varredura
    achou mais 28 em `analogy` e `resgates` de três tópicos, que estavam
    lá desde que aqueles textos foram escritos.

    Código dentro de frase se escreve sem enfeite: int a[5], sizeof a,
    *p, &x — que é o que a maioria dos textos do domínio já fazia.
    """
    d = carrega(topico=topico)
    com_crase = [(onde, texto) for onde, texto in textos_de_tela(d)
                 if "`" in (texto or "")]
    assert not com_crase, com_crase


# --------------------------------------------------------------------------
# Procedência: de que molde veio o item
# --------------------------------------------------------------------------

def test_item_sem_molde_continua_valendo(d):
    """Os 556 itens de hoje foram escritos à mão, e continuam válidos."""
    a = next(x for x in d.atividades if x.id == "ciu_kc00_001")
    assert a.do_molde == ""
    assert a.parametros == {}


def test_item_de_molde_carrega_a_procedencia(tmp_path):
    def muda(cru):
        atividade(cru, "ciu_kc00_002").update(
            do_molde="mol_teste", parametros={"tipo": "int", "n": 5})
    d = carrega(monta(tmp_path / "m1", muda))
    a = next(x for x in d.atividades if x.id == "ciu_kc00_002")
    assert a.do_molde == "mol_teste"
    assert a.parametros == {"tipo": "int", "n": 5}


def test_meia_procedencia_nao_carrega(tmp_path):
    """Molde sem parâmetros, ou o contrário, PARECE procedência.

    Quem ler o log vai achar que sabe de onde o item veio, e não sabe:
    sem os parâmetros não dá para dizer qual variação a pessoa respondeu,
    e sem o molde os parâmetros não significam nada.
    """
    for i, campo in enumerate(("do_molde", "parametros")):
        def muda(cru, campo=campo):
            atividade(cru, "ciu_kc00_002")[campo] = (
                "mol_teste" if campo == "do_molde" else {"n": 5})
        with pytest.raises(DominioInvalido) as erro:
            carrega(monta(tmp_path / ("m2_%d" % i), muda))
        assert any("procedência" in p and "ciu_kc00_002" in p
                   for p in erro.value.problemas), erro.value.problemas
