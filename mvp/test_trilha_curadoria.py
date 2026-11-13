"""A curadoria das questões de marcar do kc_00.

A trilha abre cada premissa com uma questão do banco, e reforça, treina
e reconfere com as outras. O banco foi escrito para o fluxo anterior, e
a primeira fatia mostrou o que isso custa: questões com `double` e
`sizeof`, que tópico nenhum ensinou até ali; variáveis `a`, `b`, `x`
numa sessão que só fala de `idade`, `nota` e `turma`; valor dado na
declaração duas premissas antes de isso ser ensinado; a alternativa
certa denunciada pelo tamanho; e uma questão que a trilha nem podia
usar, porque o distrator dela não dizia crença nenhuma.

Estes testes guardam a régua da curadoria — a parte dela que um
programa mede. O que eles não medem é leitura: se a crença está BEM
dita em cada distrator, e se duas questões da mesma premissa não
perguntam a mesma coisa.

Os ids, os nós e a crença de cada distrator não mudaram: são eles que os
outros testes do projeto fixam, e é por eles que o registro de sessões
antigas continua legível.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import revisa_material  # noqa: E402

from mvp import motor, trilha, trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "mvp" / "dominio" / "escada_kc00.yaml", D)

# O cenário da escada: os nomes que a pessoa já viu nos degraus.
NOMES = {"idade", "nota", "turma", "ano", "pontos", "inicial"}


def _texto_todo(a) -> str:
    return "\n".join([a.enunciado, a.codigo or ""] + [o.texto for o in a.opcoes])


def test_os_portoes_mecanicos_nao_acusam_erro_no_banco_do_kc_00():
    """Alternativa certa visivelmente mais longa, nome de pessoa no
    enunciado, severidade de compilador afirmada, cobrança sem ensino."""
    erros = [texto for nivel, texto in revisa_material.audita_dominio("kc_00")
             if nivel == "ERRO"]
    assert erros == []


def test_nenhuma_questao_usa_o_que_a_escada_do_topico_nao_ensina():
    proibido = re.compile(r"\b(double|float|long|sizeof|while|for|if)\b|%zu|%c|%f")
    for a in D.atividades:
        achou = proibido.search(_texto_todo(a))
        assert not achou, (a.id, achou.group(0))


def test_uma_declaracao_por_linha():
    """`int a = 1, b = 2;` é forma que a escada não mostra."""
    for a in D.atividades:
        for linha in (a.codigo or "").splitlines():
            if re.match(r"\s*(int|char)\b", linha):
                assert "," not in linha, (a.id, linha)


def test_so_o_i1_da_valor_na_declaracao():
    """Declarar já com valor é o assunto do I1. Antes dele, as questões
    declaram e depois escrevem — como os degraus."""
    com_valor = re.compile(r"\b(int|char)\s+\w+\s*=")
    for a in D.atividades:
        if a.no == "I1":
            continue
        assert not com_valor.search(_texto_todo(a)), a.id


def test_as_questoes_usam_o_cenario_da_escada():
    for a in D.atividades:
        declaradas = set(re.findall(r"\b(?:int|char)\s+(\w+)", a.codigo or ""))
        assert declaradas <= NOMES, (a.id, declaradas - NOMES)


def test_o_verbo_e_reclama_e_nao_compila():
    """Que o compilador recuse é fato sobre um compilador; que ele tenha
    de reclamar é o que o padrão exige de todos."""
    for a in D.atividades:
        assert not re.search(r"compila\b|recusa", _texto_todo(a)), a.id


# A única questão sobre o NOME da variável. O catálogo não tem crença
# sobre nome, e `mvp/test_razao.py` — anterior à trilha — usa este item
# como o exemplo de questão sem crença nenhuma. Fica de fora da trilha.
SEM_CRENCA = "ciu_kc00_t02"


def test_dezenove_das_vinte_questoes_servem_a_trilha():
    """Duas razões ou mais: a certa e ao menos uma crença. Com uma razão
    só a trilha não pode usar a questão — é a razão que diz a crença."""
    nao_servem = [a.id for a in D.atividades
                  if len(motor.razoes_de(D, a)) < 2]
    assert nao_servem == [SEM_CRENCA]


@pytest.mark.parametrize("no, quantas", [
    ("B1", 3), ("B2", 4), ("B3", 4), ("B4", 4), ("I1", 4)])
def test_as_questoes_que_cada_premissa_tem_para_a_trilha(no, quantas):
    servem = [a for a in D.atividades_do_no(no)
              if len(motor.razoes_de(D, a)) >= 2]
    assert len(servem) == quantas


@pytest.mark.parametrize("no", list(D.ordem))
def test_a_abertura_de_cada_premissa_diz_a_crenca_da_propria_premissa(no):
    """A primeira pergunta da premissa é a que pode achar a crença dela.
    No I1 a abertura anterior perguntava só de `3 = x;` — e a premissa é
    sobre dar o valor na declaração ou depois."""
    a = trilha.abertura(D, no)
    crencas = {o.crenca for o in a.opcoes if o.crenca}
    assert any(D.crencas[c].nega == no for c in crencas), (a.id, crencas)


def test_a_abertura_do_i1_pergunta_a_premissa():
    a = trilha.abertura(D, "I1")
    assert "int nota = 7;" in a.codigo
    certa = next(o for o in a.opcoes if o.correta)
    # Declarar, e depois escrever: o outro caminho para o mesmo lugar.
    assert re.search(r"int nota;\s+nota = 7;", certa.texto)
    da_crenca = next(o for o in a.opcoes if o.crenca == "assignment_symmetric")
    assert "7 = nota;" in da_crenca.texto


def test_ninguem_e_citado_pelo_nome():
    for a in D.atividades:
        assert "Rafael" not in _texto_todo(a), a.id


def test_os_ids_e_as_crencas_que_o_projeto_fixa_nao_mudaram():
    """A curadoria mexe no texto. O que os outros testes fixam fica."""
    por_id = {a.id: a for a in D.atividades}
    assert len(por_id) == 20
    assert sorted(por_id) == sorted(
        ["ciu_kc00_%03d" % i for i in range(1, 11)]
        + ["ciu_kc00_t%02d" % i for i in range(1, 11)])
    erradas = {i: sorted(o.crenca or "" for o in a.opcoes if not o.correta)
               for i, a in por_id.items()}
    assert erradas["ciu_kc00_001"] == ["no_value_no_memory"] * 2
    assert erradas["ciu_kc00_002"] == ["no_value_no_memory", "type_is_a_hint"]
    assert "declaration_zeroes" in erradas["ciu_kc00_005"]
    assert erradas["ciu_kc00_t03"] == ["no_value_no_memory"] * 2
    for i, a in por_id.items():
        esperado = "treino" if "_t" in i else "diagnostico"
        assert a.uso == esperado, i
