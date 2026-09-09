"""A versão em linguagem corrente das premissas, e a figura de cada nó.

Dois campos opcionais por nó: `plain` (o mesmo que `text` afirma, dito a
quem ainda não tem o vocabulário) e `figure` (a analogia ilustrada).

O que estes testes protegem, em ordem de gravidade:

1. `text` NÃO pode mudar quando `plain` existe. `text` é a proposição com
   proveniência — a que a banca cobra e a que os planos golden congelam.
   Se simplificar reescrevesse o grafo, a simplificação viraria uma
   alteração silenciosa do domínio.

2. Os DOIS braços leem a mesma versão. Se o socrático lesse a versão
   simples e o direto a técnica, a simplificação seria um tratamento
   adicional e a variável isolada deixaria de ser a geração ativa (§8.1).

3. Uma pergunta não mistura os dois registros. Citar uma premissa em
   linguagem corrente e outra em linguagem técnica na mesma frase é pior
   do que não simplificar nada.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import session as S
from engine import socratic, strategy
from engine.loader import load
from tools import validate

WEB = Path(__file__).resolve().parent.parent / "web"


@pytest.fixture(scope="module")
def d():
    return load()


def kc07(d):
    return [n for n in d.kcs["kc_07"].nodes.values()]


# --------------------------------------------------------------------------
# 1. O grafo não muda
# --------------------------------------------------------------------------

def test_o_enunciado_canonico_sobrevive_a_simplificacao(d):
    """`plain` é apresentação; `text` continua sendo o que o grafo afirma."""
    for n in kc07(d):
        assert n.plain, "%s:%s deveria estar simplificado" % (n.kc, n.id)
        assert n.text, "%s:%s perdeu o enunciado canônico" % (n.kc, n.id)
        assert n.plain != n.text


def test_o_passo_carrega_os_dois_textos(d):
    """A análise precisa do canônico; o participante lê o outro."""
    for p in socratic.steps(d, "kc_07", "I1"):
        no = d.node(p.kc, p.node)
        assert p.text == d.study.mask(no.plain)
        assert p.canonical == d.study.mask(no.text)


def test_no_sem_plain_cai_no_texto_do_grafo(d):
    """A simplificação é opcional. Um KC sem ela funciona como sempre."""
    for p in socratic.steps(d, "kc_02", "I1"):
        no = d.node(p.kc, p.node)
        assert not no.plain
        assert no.display_text == no.text
        assert p.text == d.study.mask(no.text)
        assert p.canonical == p.text


# --------------------------------------------------------------------------
# 2. Simetria entre os braços (§8.1)
# --------------------------------------------------------------------------

def test_os_dois_bracos_leem_a_mesma_versao(d):
    """A simplificação não pode ser tratamento de um braço só."""
    for m in d.misconceptions_of("kc_07"):
        a = socratic.steps(d, m.kc, m.node)
        b = [x for x in strategy.DirectStrategy().correct(d, m.kc, m.node)
             if x.kind != "confirm"]
        assert [x.text for x in b] == [d.node(x.kc, x.node).plain
                                       or d.node(x.kc, x.node).text
                                       for x in a]


def test_a_figura_aparece_nos_dois_bracos(d):
    """Ilustrar um braço só seria dar a ele um apoio que o outro não tem."""
    def figuras(arm):
        t = S.start(d, arm, ["kc_07"], seed="s")
        while t.action.kind == "intro":
            t = S.advance(d, t.state, S.Acknowledge(10))
        # força a correção pela crença que nega a conclusão
        estado = S.replace(t.state, phase=S.CORRECAO, kc_index=0,
                           target=("kc_07", "I1"),
                           plan=tuple(socratic.plan(d, "kc_07", "I1")),
                           cursor=0)
        out = []
        for i in range(len(estado.plan)):
            passo = S._apresenta_passo(d, S.replace(estado, cursor=i))
            out.append(passo.action.as_json().get("figure", {}).get("kind"))
        return out

    # `_apresenta_passo` é interno; o que importa é o dado que chega ao
    # cliente, e ele é idêntico nos dois braços.
    assert figuras("socratic") == figuras("direct")


# --------------------------------------------------------------------------
# 3. Registro uniforme
# --------------------------------------------------------------------------

def test_nenhuma_pergunta_do_piloto_mistura_os_registros(d):
    """Dentro dos KCs que o piloto percorre, a mistura seria visível."""
    achados = [a for a in validate.check_mixed_question(d)
               if any(kc in a.split(":")[0] for kc in d.pilot_sequence)]
    # kc_11:I4 é peso morto — nenhum traversal o alcança (ver
    # check_node_coverage). A mistura ali é teórica.
    reais = [a for a in achados if "kc_11:I4" not in a]
    assert reais == [], reais


def test_o_traversal_do_kc07_e_inteiro_em_linguagem_corrente(d):
    """Inclusive kc_06:B2, que kc_07:I4 puxa de outro KC."""
    for m in d.misconceptions_of("kc_07"):
        for p in socratic.steps(d, m.kc, m.node):
            assert d.node(p.kc, p.node).plain, "%s:%s" % (p.kc, p.node)


def test_a_mistura_e_detectada(d, tmp_path):
    """A guarda tem de PEGAR: um teste que não falha quando deveria não vale."""
    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        shutil.copy(f, copia / f.name)
    alvo = copia / "premise_graphs.yaml"
    alvo.write_text(
        alvo.read_text(encoding="utf-8").replace(
            'plain: "int a[5] cria 5 caixas', 'plain_desligado: "int a[5] cria 5 caixas'),
        encoding="utf-8")

    achados = validate.check_mixed_question(load(copia))
    assert any("kc_07:I1" in a for a in achados), achados


# --------------------------------------------------------------------------
# Figuras
# --------------------------------------------------------------------------

def tipos_do_renderizador() -> set[str]:
    fonte = (WEB / "figures.js").read_text(encoding="utf-8")
    ini = fonte.index("var TIPOS = {")
    bloco = fonte[ini:fonte.index("};", ini)]
    return {l.strip().split(":")[0].strip()
            for l in bloco.splitlines()[1:] if l.strip()}


def test_toda_figura_usa_um_tipo_que_o_renderizador_desenha(d):
    """Um `kind` desconhecido não desenha NADA, e não avisa ninguém."""
    conhecidos = tipos_do_renderizador()
    for kc in d.kcs.values():
        for n in kc.nodes.values():
            if n.figure:
                assert n.figure["kind"] in conhecidos, \
                    "%s:%s usa %r, que web/figures.js não desenha" % (
                        n.kc, n.id, n.figure["kind"])


def test_todo_no_simplificado_tem_figura(d):
    """O pedido era ilustrar CADA premissa. Meia ilustração é pior que
    nenhuma: o aluno estranha o passo que não tem."""
    for n in kc07(d):
        assert n.figure, "%s:%s tem `plain` e nenhuma figura" % (n.kc, n.id)


def test_figura_sem_kind_e_recusada_na_carga(d, tmp_path):
    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        shutil.copy(f, copia / f.name)
    alvo = copia / "premise_graphs.yaml"
    alvo.write_text(
        alvo.read_text(encoding="utf-8").replace(
            "          kind: array_row\n", "          alt_sem_kind: x\n", 1),
        encoding="utf-8")
    with pytest.raises(Exception, match="figure sem"):
        load(copia)


# --------------------------------------------------------------------------
# RF10 continua valendo sobre o campo novo
# --------------------------------------------------------------------------

def test_o_termo_tardio_nao_vaza_pelo_campo_novo(d, tmp_path):
    """`plain` é o que o participante lê. Se RF10 só olhasse `text`, o
    vazamento passaria exatamente pelo campo recém-criado."""
    assert validate.check_late_naming(d) == []

    copia = tmp_path / "dominio"
    copia.mkdir()
    for f in d.source.glob("*.yaml"):
        shutil.copy(f, copia / f.name)
    alvo = copia / "premise_graphs.yaml"
    alvo.write_text(
        alvo.read_text(encoding="utf-8").replace(
            'plain: "int *p cria uma caixa só',
            'plain: "isto se chama dangling. int *p cria uma caixa só', 1),
        encoding="utf-8")

    achados = validate.check_late_naming(load(copia))
    assert any("plain" in a and "kc_07:B2" in a for a in achados), achados


# --------------------------------------------------------------------------
# O que o cliente recebe
# --------------------------------------------------------------------------

def test_o_diagrama_do_rf08_tem_precedencia_sobre_a_analogia(d):
    """Duas ilustrações no mesmo passo dividiriam a atenção justamente
    onde o RF08 exige que o aluno observe uma coisa específica."""
    passo = socratic.steps(d, "kc_07", "B1")[0]
    assert passo.figure, "kc_07:B1 tem analogia"

    com_visual = S.SessionState(arm="socratic", kc_sequence=("kc_07",),
                                visual={"kind": "memory_diagram"})
    dados = S._dados_do_passo(com_visual, passo)
    assert "visual" in dados and "figure" not in dados

    sem_visual = S.SessionState(arm="socratic", kc_sequence=("kc_07",))
    dados = S._dados_do_passo(sem_visual, passo)
    assert "figure" in dados and "visual" not in dados
    assert dados["figure"]["kind"] == "array_row"


# --------------------------------------------------------------------------
# Tokens de cor
# --------------------------------------------------------------------------

def test_todo_var_de_cor_esta_definido():
    """Um `var(--x)` sem definição não avisa: o SVG pinta de PRETO.

    Foi o que aconteceu com `--accent-soft`, `--base`, `--base-soft`,
    `--warn` e `--warn-soft` — usados nas figuras, nunca definidos na
    folha. As caixas em destaque saíam pretas, com o texto preto por
    cima, e nenhum erro aparecia em lugar nenhum.
    """
    import re

    css = (WEB / "style.css").read_text(encoding="utf-8")
    definidos = set(re.findall(r"(--[a-z0-9-]+)\s*:", css))
    for arquivo in ("style.css", "figures.js", "diagram.js", "app.js"):
        usados = set(re.findall(r"var\((--[a-z0-9-]+)\)",
                                (WEB / arquivo).read_text(encoding="utf-8")))
        assert not (usados - definidos), \
            "%s usa token(s) que a folha não define: %s" % (
                arquivo, ", ".join(sorted(usados - definidos)))


# --------------------------------------------------------------------------
# O feedback cita o que o aluno LEU
# --------------------------------------------------------------------------

def test_a_contradicao_cita_a_versao_que_o_aluno_confirmou(d):
    """RF17 etapa 2 vale porque diz "repare no que VOCÊ confirmou".

    Se ela devolvesse o enunciado canônico enquanto o aluno confirmou a
    versão em linguagem corrente, ele não reconheceria como sua uma frase
    que nunca leu — e a contradição deixaria de ser entre coisas que ele
    afirmou para virar mais uma afirmação do sistema.
    """
    from engine import feedback as F

    # O molde atual não usa {support} — a pergunta logo abaixo já lista as
    # premissas. Mas o mecanismo que o preenche continua existindo, e é
    # ele que tem de entregar a versão lida.
    lista = F._lista_suporte(d, ("kc_07", "I1"))
    for ref in d.node("kc_07", "I1").support:
        no = d.node(*ref)
        assert no.plain.rstrip(".") in lista, "%s:%s" % (no.kc, no.id)
        assert no.text.rstrip(".") not in lista

    # E nenhum enunciado canônico pode vazar por nenhuma etapa do RF17.
    fb = F.contradiction(d, "kc_07", "I1", belief_id="array_is_pointer")
    assert fb is not None
    for no in d.kcs["kc_07"].nodes.values():
        assert no.text.rstrip(".") not in fb.text, "%s:%s" % (no.kc, no.id)
