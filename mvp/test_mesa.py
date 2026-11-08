# -*- coding: utf-8 -*-
"""O teste de mesa: a tabela que a execução gera.

O DONO, depois de usar o sistema: o cartão está verborrágico, é pouco
ilustrado, e `printf("%p", (void *)&x)` é elaborado demais para quem
está aprendendo o que é um ponteiro. Medido, ele tinha razão nos três:

    palavras numa tela só ................ 372 a 560 (eram ~135)
    `(void *)` no material de ensino ..... 11 vezes
    `(void *)` em 562 itens do banco ......  5 vezes

O material de ensino tinha ficado mais elaborado que a prova.

A TABELA RESOLVE OS TRÊS DE UMA VEZ. A do I1 mostra, sem uma palavra,
que `p = &y` muda só o p, que `*p = 99` muda só o y, e que `&p` nunca
muda — que são as premissas B2, B3 e I1 inteiras. E o `(void *)` sai da
tela: ele fica no programa instrumentado, não no que o aluno lê.

E ELA NÃO É ESCRITA À MÃO. Sai de um programa compilado e executado
pelo mesmo gcc que o projeto usa como oráculo, e `test_a_tabela_bate_com
_a_execucao` regenera e compara — é o que impede a tabela de envelhecer
quando alguém mexer no exemplo do cartão.
"""
from __future__ import annotations

import pathlib

import pytest

from mvp import motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

D2 = carrega(topico="kc_02")


@pytest.fixture(scope="module")
def d():
    return D2


def _tem_gcc() -> bool:
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                           / "scripts"))
    try:
        from oraculo import GCC                      # type: ignore
    except ImportError:
        return False
    return pathlib.Path(GCC).exists()


# --------------------------------------------------------------------------
# O domínio carrega
# --------------------------------------------------------------------------

def test_o_dominio_tem_o_acessador(d):
    assert hasattr(d, "teste_de_mesa")


def test_no_sem_tabela_devolve_vazio(d):
    assert d.teste_de_mesa("ZZ") == {}


@pytest.mark.parametrize("topico", topicos())
def test_a_tabela_tem_forma(topico):
    """Colunas e linhas, e toda linha com um valor por coluna. Linha
    torta é tabela desalinhada na tela, e ninguém percebe lendo YAML."""
    dd = carrega(topico=topico)
    for nid in dd.ordem:
        t = dd.teste_de_mesa(nid)
        if not t:
            continue
        assert set(t) == {"colunas", "linhas"}, "%s: %s" % (nid, sorted(t))
        assert t["colunas"], "%s: tabela sem colunas" % nid
        for l in t["linhas"]:
            assert set(l) == {"codigo", "valores"}, "%s: %s" % (nid, sorted(l))
            assert len(l["valores"]) == len(t["colunas"]), (
                "%s: linha %r tem %d valores para %d colunas"
                % (nid, l["codigo"], len(l["valores"]), len(t["colunas"])))


@pytest.mark.parametrize("topico", topicos())
def test_a_tabela_nao_mostra_o_cast(topico):
    """O MOTIVO DE ELA EXISTIR. O `(void *)` fica no programa que o
    gerador compila; o que chega ao aluno é o valor."""
    dd = carrega(topico=topico)
    for nid in dd.ordem:
        for l in dd.teste_de_mesa(nid).get("linhas", ()):
            assert "(void *)" not in l["codigo"], "%s: %s" % (nid, l["codigo"])
            assert "printf" not in l["codigo"], (
                "%s: printf na tabela — ele é saída, não estado" % nid)


# --------------------------------------------------------------------------
# A tabela não envelhece
# --------------------------------------------------------------------------

@pytest.mark.skipif(not _tem_gcc(), reason="sem compilador nesta máquina")
@pytest.mark.parametrize("topico", topicos())
def test_a_tabela_bate_com_a_execucao(topico):
    """Regenera e compara.

    Sem isto, mexer no exemplo do cartão deixa a tabela dizendo o que o
    código não faz mais — e tabela errada é pior que tabela nenhuma,
    porque ela parece medida.

    Os ENDEREÇOS mudam a cada execução, então o que se compara é a
    estrutura e os valores que não são endereço. O que a tabela ensina
    é quais endereços são IGUAIS entre si, e isso se compara pelo
    padrão de repetição, não pelo número.
    """
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                           / "scripts"))
    from mesa import NaoSeiSondar, gera              # type: ignore

    dd = carrega(topico=topico)
    for nid in dd.ordem:
        guardada = dd.teste_de_mesa(nid)
        if not guardada:
            continue
        _VISTAS.append("%s/%s" % (topico, nid))
        try:
            agora = gera(dd.exemplo(nid))
        except NaoSeiSondar as e:
            pytest.fail("%s/%s: guardou tabela e o gerador recusa agora: %s"
                        % (topico, nid, e))
        assert agora["colunas"] == guardada["colunas"], nid
        assert ([l["codigo"] for l in agora["linhas"]]
                == [l["codigo"] for l in guardada["linhas"]]), nid
        for a, g in zip(agora["linhas"], guardada["linhas"]):
            assert _padrao(a["valores"]) == _padrao(g["valores"]), (
                "%s/%s: o padrão de igualdade mudou na linha %r"
                % (topico, nid, a["codigo"]))


_VISTAS: list[str] = []


def test_a_regeneracao_nao_e_vazia():
    """A TRAVA DE VACUIDADE do teste acima.

    Enquanto nenhum tópico tiver tabela guardada, aquele laço não
    compara nada e passa calado. Com cinco nós do kc_02 gerados, ele
    tem o que conferir — e se alguém apagar as tabelas, esta linha
    avisa em vez de a suíte ficar verde por falta de objeto.

    Depende de rodar DEPOIS do teste acima, e por isso olha o que ele
    viu em vez de contar por conta própria.

    O NÚMERO É QUATRO, e não cinco, e a diferença é deliberada: o I2
    ficou SEM tabela de propósito. O ponto dele é o tipo, e o que o
    ensina são dois `sizeof` — que são saída, não estado. A tabela
    gerada para ele tinha oito colunas e mostrava quatro variáveis em
    endereços diferentes, que é o ponto do B2. O motivo está em
    `SEM_TABELA`, em `scripts/mesa.py`.

    Quando eu baixei de cinco para quatro, foi esta trava que avisou —
    que é exatamente o que ela existe para fazer.
    """
    QUATRO = 4   # B1, B2, B3 e I1 do kc_02
    assert len(_VISTAS) >= QUATRO, (
        "só %d nós com tabela guardada: o teste de regeneração está "
        "quase vazio — %s" % (len(_VISTAS), _VISTAS))


def _padrao(valores):
    """Quem é igual a quem, mais os valores que não são endereço.

    Endereço muda a cada execução; o que a tabela ensina é que `p` vale
    o MESMO que `&x`. Isso é o padrão de repetição, e ele é estável.
    """
    indice, saida = {}, []
    for v in valores:
        if v.strip() and all(c in "0123456789ABCDEFabcdefxX" for c in v) \
                and len(v) >= 8:
            saida.append("end%d" % indice.setdefault(v, len(indice)))
        else:
            saida.append(v)
    return saida


# --------------------------------------------------------------------------
# A tela
# --------------------------------------------------------------------------

def _ate_a_construcao(d):
    t = motor.inicia(d, semente="MESA")
    for _ in range(60):
        tela = t.tela
        if tela.tipo == "ensino" and tela.dados.get("motivo") == "lacuna":
            return t
        r = (Resposta(texto="nao sei") if tela.tipo == "frase"
             else Resposta(nao_sei=True) if tela.tipo in ("atividade", "razao")
             else Resposta(confianca="chutei") if tela.tipo == "confianca"
             else Resposta())
        t = motor.avanca(d, t.estado, r)
    raise AssertionError("não cheguei à construção")


def test_as_duas_telas_de_ensino_mandam_a_tabela(d):
    abertura = motor.avanca(d, motor.inicia(d).estado,
                            Resposta(texto="uma frase")).tela
    lacuna = _ate_a_construcao(d).tela
    for tela, nome in ((abertura, "abertura"), (lacuna, "construção")):
        assert "teste_de_mesa" in tela.dados, "a %s não manda a tabela" % nome


def _web(arquivo):
    import re
    texto = (pathlib.Path(__file__).resolve().parent / "web" / arquivo
             ).read_text(encoding="utf-8")
    if arquivo.endswith(".html"):
        return re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", texto, flags=re.S)


def test_o_cliente_desenha_a_tabela():
    js = _web("app.js")
    assert "t.teste_de_mesa" in js, "o cliente não lê a tabela"
    assert "ensino-mesa" in js
    assert ('id="ensino-mesa"') in _web("index.html"), "falta #ensino-mesa"


def test_o_codigo_nao_dobra_no_meio():
    """`pre-wrap` quebrava `printf("%p\\n", (void *)&idade);` no meio da
    expressão, e código que dobra deixa de parecer código."""
    css = _web("style.css")
    import re
    m = re.search(r"\.codigo\{([^}]*)\}", css, re.S)
    assert m, "a classe .codigo sumiu"
    assert "white-space:pre;" in m.group(1).replace(" ", "").replace(
        "white-space:pre-wrap", "X"), "o código ainda dobra no meio"
