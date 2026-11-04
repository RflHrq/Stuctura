"""A escada de dificuldade: começa no degrau 1 e sobe um por vez.

O domínio antigo de ponteiros já tinha `nivel: 1|2|3` por item, e a
curadoria descrevia a escada — *"a sessão começa no nível 1 e sobe um
degrau por vez; tópico sem algum degrau não consegue oferecer a escada
inteira"*. O MVP tinha perdido o campo, e quem atravessou a unidade disse,
nessas palavras, que parecia **"entrar no chefão já"**.

Duas regras, e as duas têm teste aqui:

1. **nunca pular degrau por conta própria.** Pular só quando o banco não
   tem item naquele degrau — e aí o log diz que pulou, porque é furo de
   conteúdo, não decisão do motor;
2. **só sobe quem ficou de pé ali.** Errar, chutar ou acertar pela razão
   errada não promove: o degrau mede o que a pessoa venceu, e promover
   quem não venceu transformaria a escada em contador de perguntas.
"""

from __future__ import annotations

import pytest

from mvp import motor
from mvp.dominio import NIVEIS, DominioInvalido, carrega, topicos
from mvp.motor import Resposta
from mvp.test_motor import _politica, roda

D = carrega()
D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d():
    return D


@pytest.fixture(scope="module")
def d2():
    return D2


def _dos(eventos, tipo):
    return [e for e in eventos if e.tipo == tipo]


def _degraus_por_no(eventos):
    por_no = {}
    for e in _dos(eventos, "atividade_apresentada"):
        if e.dados["fase"] != motor.DIAGNOSTICO:
            continue
        por_no.setdefault(e.dados["no"], []).append(e.dados["nivel"])
    return por_no


# --------------------------------------------------------------------------
# A escada existe, e começa embaixo
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_todo_no_comeca_no_degrau_um(topico):
    """O primeiro item que a pessoa vê de cada premissa é o mais fácil
    que o banco tem. É isto que faltava."""
    dd = carrega(topico=topico)
    _, eventos = roda(dd, _politica(d=dd))
    for no, degraus in _degraus_por_no(eventos).items():
        assert degraus[0] == 1, (no, degraus)


@pytest.mark.parametrize("topico", topicos())
def test_o_degrau_sobe_de_um_em_um(topico):
    """Nunca de 1 para 3. A escada inteira ou nada."""
    dd = carrega(topico=topico)
    _, eventos = roda(dd, _politica(d=dd))
    for no, degraus in _degraus_por_no(eventos).items():
        for antes, depois in zip(degraus, degraus[1:]):
            assert depois - antes <= 1, (no, degraus)


def test_quem_erra_nao_sobe(d2):
    """Promover quem não venceu o degrau transformaria a escada em
    contador de perguntas."""
    t = motor.inicia(d2, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    no = t.tela.no
    assert t.estado.no(no).nivel == 1
    item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
    errada = next(i for i, o in enumerate(item.opcoes) if not o.correta)
    t = motor.avanca(d2, t.estado, Resposta(escolha=errada))
    # camada 2 e 3, explicando pela crença: episódio de crença, não de pé
    razoes = t.estado.pendente.razoes
    i = next((i for i, z in enumerate(razoes) if z.crenca), 0)
    t = motor.avanca(d2, t.estado, Resposta(escolha=i))
    if t.tela.tipo == "confianca":
        t = motor.avanca(d2, t.estado, Resposta(confianca="tenho certeza"))
    assert t.estado.no(no).nivel == 1, "subiu o degrau de quem errou"


def test_quem_acerta_pela_razao_certa_sobe(d2):
    t = motor.inicia(d2, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    no = t.tela.no
    item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
    t = motor.avanca(d2, t.estado, Resposta(escolha=item.indice_correto_no_arquivo))
    razoes = t.estado.pendente.razoes
    t = motor.avanca(d2, t.estado,
                     Resposta(escolha=next(i for i, z in enumerate(razoes) if z.correta)))
    t = motor.avanca(d2, t.estado, Resposta(confianca="tenho certeza"))
    assert t.estado.no(no).nivel == 2


def test_o_degrau_chega_a_tela(d2):
    """Quem responde merece saber que a pergunta ficou mais dura porque
    ele subiu, e não por acaso."""
    t = motor.inicia(d2, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            break
        t = motor.avanca(d2, t.estado, Resposta(texto="x"))
    assert t.tela.dados["nivel"] == 1
    assert t.tela.dados["niveis"] == max(NIVEIS)


# --------------------------------------------------------------------------
# Os buracos do banco são do banco, e aparecem
# --------------------------------------------------------------------------

def test_domínio_sem_o_primeiro_degrau_nao_carrega(tmp_path):
    """Nó que começa no meio é exatamente o "entrar no chefão já" — e isso
    falha na carga, não em sessão."""
    import shutil
    import yaml
    from mvp.dominio import RAIZ

    destino = tmp_path / "dominio"
    shutil.copytree(RAIZ, destino)
    arq = destino / "activities_kc02.yaml"
    cru = yaml.safe_load(arq.read_text(encoding="utf-8"))
    for a in cru["activities"]:
        if a.get("uso", "diagnostico") == "diagnostico" and a["nivel"] == 1:
            a["nivel"] = 2
    arq.write_text(yaml.safe_dump(cru, allow_unicode=True), encoding="utf-8")
    with pytest.raises(DominioInvalido) as erro:
        carrega(destino, topico="kc_02")
    assert any("nível 1" in p for p in erro.value.problemas)


def test_nivel_invalido_nao_carrega(tmp_path):
    import shutil
    import yaml
    from mvp.dominio import RAIZ

    destino = tmp_path / "dominio"
    shutil.copytree(RAIZ, destino)
    arq = destino / "activities_kc02.yaml"
    cru = yaml.safe_load(arq.read_text(encoding="utf-8"))
    cru["activities"][0]["nivel"] = 9
    arq.write_text(yaml.safe_dump(cru, allow_unicode=True), encoding="utf-8")
    with pytest.raises(DominioInvalido) as erro:
        carrega(destino, topico="kc_02")
    assert any("nivel inválido" in p for p in erro.value.problemas)


def test_degrau_vazio_no_banco_vira_evento(d2):
    """Pular degrau é furo de conteúdo, não decisão do motor. O log diz."""
    e = motor.Estado().com("B1", nivel=2)
    # B1 tem item de nível 2, então aqui NÃO pula
    escolhida, pulo, motivo = motor._no_degrau(d2, e, "B1")
    assert escolhida.nivel == 2 and pulo is None

    # gastando os de nível 2, sobra só o 3: pula, e diz que ESGOTOU
    usadas = tuple(a.id for a in d2.atividades_do_no("B1", "diagnostico")
                   if a.nivel <= 2)
    e = motor.Estado().com("B1", nivel=2, usadas=usadas)
    escolhida, pulo, motivo = motor._no_degrau(d2, e, "B1")
    assert escolhida.nivel == 3 and pulo == 3
    assert "acabou" in motivo, motivo


def test_o_evento_distingue_o_degrau_do_item_do_contador_do_no(d2):
    """Um nó confirmado pela CS-5 no degrau 2 fica com o contador em 3 sem
    nunca ter visto um item de 3. Quem analisa precisa saber qual dos dois
    está olhando."""
    _, eventos = roda(d2, _politica(d=d2))
    for e in _dos(eventos, "degrau"):
        assert "degrau_do_item" in e.dados
        assert e.dados["degrau_do_item"] in NIVEIS


def _ate_a_atividade(d):
    t = motor.inicia(d, semente="s")
    for _ in range(12):
        if t.tela.tipo == "atividade":
            return t
        t = motor.avanca(d, t.estado, Resposta(texto="x"))
    raise AssertionError("não cheguei à atividade")


def test_quem_declara_que_nao_sabe_nao_sobe(d2):
    """A sabotagem pegou este buraco: o teste da crença passava e o da
    lacuna não existia. Declarar "não sei" leva à construção — e construir
    não é vencer o degrau."""
    t = _ate_a_atividade(d2)
    no = t.tela.no
    assert t.estado.no(no).nivel == 1
    t = motor.avanca(d2, t.estado, Resposta(nao_sei=True))
    assert t.estado.no(no).nivel == 1, "a lacuna promoveu o nó"


def test_quem_acerta_pela_razao_errada_nao_sobe(d2):
    """Falso positivo: a resposta está certa e a explicação leva a outro
    lugar. Não demonstrou a premissa naquele degrau."""
    t = _ate_a_atividade(d2)
    no = t.tela.no
    item = next(x for x in d2.atividades if x.id == t.tela.dados["atividade"])
    t = motor.avanca(d2, t.estado, Resposta(escolha=item.indice_correto_no_arquivo))
    razoes = t.estado.pendente.razoes
    errada = next((i for i, z in enumerate(razoes) if z.crenca), None)
    assert errada is not None, "o item não oferece razão errada; o teste não morde"
    t = motor.avanca(d2, t.estado, Resposta(escolha=errada))
    if t.tela.tipo == "confianca":
        t = motor.avanca(d2, t.estado, Resposta(confianca="tenho certeza"))
    # O contador pode subir por falta de item no degrau; a REGRA é sobre
    # promover, e é nela que o teste pega.
    #
    # A versão anterior também exigia um `degrau_pulado` por esgotamento —
    # mas isso era propriedade do BANCO de um item por degrau, não do
    # motor. Com dois itens por degrau sobra onde tentar de novo, e o pulo
    # deixou de acontecer aqui. A garantia do motor continua coberta, por
    # construção de estado, em `test_degrau_vazio_no_banco_vira_evento`.
    subiu = [e for e in t.eventos
             if e.tipo == "degrau" and e.dados["no"] == no and e.dados["subiu"]]
    assert subiu == [], "o falso positivo promoveu o nó"
