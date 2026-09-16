"""A máquina de estados da sessão (§6). Item 4 do §13.

Sessões scriptadas ponta a ponta, sem HTTP e sem banco — que é o que a
pureza da FSM compra. O mesmo roteiro roda nos dois braços e as diferenças
entre eles são afirmadas explicitamente.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import model, session as S, socratic, strategy
from engine.loader import load


@pytest.fixture(scope="module")
def d():
    return load()


# --------------------------------------------------------------------------
# Utilidades de roteiro
# --------------------------------------------------------------------------

def comeca(d, arm, kcs):
    """Abre a sessão e atravessa a introdução.

    A introdução é orientação, não medida: nenhum teste de fluxo, de
    paridade ou de diagnóstico depende dela. Atravessá-la aqui mantém cada
    teste falando do que ele de fato verifica.
    """
    t = S.start(d, arm, kcs)
    while t.action.kind == "intro":
        t = S.advance(d, t.state, S.Acknowledge(500))
    return t


def idx_de(ciu, misconception=None, correct=False):
    """Índice da alternativa correta, ou da que carrega dada crença."""
    for i, o in enumerate(ciu.options):
        if correct and o.correct:
            return i
        if misconception and o.misconception == misconception:
            return i
    raise AssertionError("%s não tem alternativa pedida" % ciu.id)


def responde(d, t, *, errando=None, confianca="tenho certeza", ms=5000):
    """Responde a CIU atual: certa por padrão, ou com a crença pedida."""
    ciu = d.cius[t.action.ciu_id]
    if ciu.is_choice:
        i = idx_de(ciu, misconception=errando, correct=errando is None)
        return S.advance(d, t.state, S.Answer(ciu.id, confianca, ms, option_idx=i))
    if ciu.type == "fill_blank":
        texto = ciu.answer if errando is None else "sei la"
        return S.advance(d, t.state, S.Answer(ciu.id, confianca, ms, text=texto))
    if ciu.type == "parsons":
        ordem = ciu.steps_correct if errando is None else ciu.common_wrong_orders[0].order
        return S.advance(d, t.state, S.Answer(ciu.id, confianca, ms, text=tuple(ordem)))
    alvo = next(p for p in ciu.paths if (p.correct if errando is None
                                         else p.misconception == errando))
    return S.advance(d, t.state, S.Answer(ciu.id, confianca, ms, text=alvo.label))


def roda(d, arm, kcs, *, erra_primeira=None, limite=400):
    """Roda uma sessão até o fim, acertando tudo salvo o que for pedido.

    Devolve (estado final, lista de eventos, lista de ações).
    """
    t = S.start(d, arm, kcs)
    eventos, acoes = list(t.events), [t.action]
    primeira = True
    for _ in range(limite):
        if t.action.kind == "done":
            break
        if t.action.kind == "ciu":
            erro = erra_primeira if (primeira and erra_primeira) else None
            ciu = d.cius[t.action.ciu_id]
            if erro and not any(o.misconception == erro for o in ciu.options):
                erro = None
            if erro:
                primeira = False
            t = responde(d, t, errando=erro)
        elif t.action.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 3000))
        else:  # diagram | conclude
            t = S.advance(d, t.state, S.Acknowledge(1500))
        eventos.extend(t.events)
        acoes.append(t.action)
    else:
        raise AssertionError("sessão não terminou em %d passos" % limite)
    return t.state, eventos, acoes


# --------------------------------------------------------------------------
# Roteiro completo, nos dois braços
# --------------------------------------------------------------------------

@pytest.mark.parametrize("arm", ["socratic", "direct"])
def test_sessao_completa_roda_ponta_a_ponta(d, arm):
    estado, eventos, acoes = roda(d, arm, ["kc_09"], erra_primeira="free_nullifies")
    assert estado.done
    assert estado.kc_status["kc_09"] == S.COMPLETO
    tipos = [e.type for e in eventos]
    # A sessão abre pela introdução; a primeira coisa MEDIDA é a atividade.
    assert tipos[0] == "stage_acknowledged"
    assert eventos[0].payload["stage"] == "intro"
    assert next(t for t in tipos if t != "stage_acknowledged") == "ciu_presented"
    assert tipos[-1] == "session_ended"
    assert "misconception_detected" in tipos
    assert "kc_completed" in tipos


@pytest.mark.parametrize("arm", ["socratic", "direct"])
def test_sessao_com_todos_os_kcs_do_piloto(d, arm):
    estado, eventos, _ = roda(d, arm, list(d.pilot_sequence))
    assert estado.done
    assert set(estado.kc_status) == set(d.pilot_sequence)
    assert [e.payload["kc"] for e in eventos if e.type == "kc_completed"] == \
        list(d.pilot_sequence)


def test_os_dois_bracos_veem_as_mesmas_cius_na_mesma_ordem(d):
    """§8.1: as CIUs diagnósticas, na mesma ordem, com os mesmos distratores."""
    _, ev_a, _ = roda(d, "socratic", ["kc_09"], erra_primeira="free_nullifies")
    _, ev_b, _ = roda(d, "direct", ["kc_09"], erra_primeira="free_nullifies")
    cius = lambda evs: [e.payload["ciu_id"] for e in evs if e.type == "ciu_presented"]
    assert cius(ev_a) == cius(ev_b)


def test_os_dois_bracos_percorrem_os_mesmos_nos(d):
    """§8.2: o conteúdo da correção é o mesmo; só a forma muda."""
    _, ev_a, _ = roda(d, "socratic", ["kc_09"], erra_primeira="free_nullifies")
    _, ev_b, _ = roda(d, "direct", ["kc_09"], erra_primeira="free_nullifies")
    nos_a = [(e.payload["kc"], e.payload["node"])
             for e in ev_a if e.type == "socratic_step_shown"]
    nos_b = [(e.payload["kc"], e.payload["node"])
             for e in ev_b if e.type == "direct_explanation_shown"]
    assert nos_a == nos_b and nos_a


def test_so_o_braco_a_pergunta_e_so_o_b_explica(d):
    _, _, acoes_a = roda(d, "socratic", ["kc_09"], erra_primeira="free_nullifies")
    _, _, acoes_b = roda(d, "direct", ["kc_09"], erra_primeira="free_nullifies")
    assert any(a.kind == "ask" for a in acoes_a)
    assert not any(a.kind == "explain" for a in acoes_a)
    assert any(a.kind == "explain" for a in acoes_b)
    assert not any(a.kind == "ask" for a in acoes_b)


# --------------------------------------------------------------------------
# §7.3: a confiança separa lacuna de crença
# --------------------------------------------------------------------------

def test_errar_com_certeza_marca_o_no_como_errado(d):
    t = comeca(d, "socratic", ["kc_09"])
    ciu = d.cius[t.action.ciu_id]
    t = S.advance(d, t.state, S.Answer(
        ciu.id, "tenho certeza", 8000,
        option_idx=idx_de(ciu, misconception="free_nullifies")))
    assert t.state.vector[("kc_09", "I1")] == model.WRONG
    assert t.state.detected == "free_nullifies"


def test_errar_chutando_marca_ausente_e_nao_detecta_crenca(d):
    t = comeca(d, "socratic", ["kc_09"])
    ciu = d.cius[t.action.ciu_id]
    t = S.advance(d, t.state, S.Answer(
        ciu.id, "chutei", 8000,
        option_idx=idx_de(ciu, misconception="free_nullifies")))
    estados = {t.state.vector.get(("kc_09", n)) for n in ciu.targets}
    assert estados == {model.ABSENT}
    assert t.state.detected is None
    assert not any(e.type == "misconception_detected" for e in t.events)


def test_a_mesma_resposta_leva_a_estados_cognitivos_opostos(d):
    """O mesmo erro, duas confianças, dois diagnósticos. É o mecanismo central.

    Com nada confirmado ainda, chutar dá DESCONHECIMENTO — não LACUNA. A
    diferença entre os dois é quantidade de premissa já erguida (§7.2); o
    que a confiança separa é crença ativa de ausência de conhecimento, e
    é essa a oposição que importa.
    """
    def estado_apos(conf):
        t = comeca(d, "socratic", ["kc_09"])
        ciu = d.cius[t.action.ciu_id]
        t = S.advance(d, t.state, S.Answer(
            ciu.id, conf, 8000, option_idx=idx_de(ciu, misconception="free_nullifies")))
        return model.cognitive_state(d, t.state.vector, "kc_09"), t.state.vector

    com_certeza, v1 = estado_apos("tenho certeza")
    chutando, v2 = estado_apos("chutei")

    assert com_certeza == model.MISCONCEPTION
    assert chutando != model.MISCONCEPTION
    # com certeza, o nó que a crença NEGA vira errado
    assert v1[("kc_09", "I1")] == model.WRONG
    assert v2.get(("kc_09", "I1")) != model.WRONG
    # chutando, o que a atividade MIRAVA vira ausente: ele sabe que não sabe.
    # Não se afirma I1 aqui de propósito — a atividade de abertura do kc_09
    # mira I2, e o nó negado pela crença não precisa estar entre os alvos.
    ciu = d.cius[comeca(d, "socratic", ["kc_09"]).action.ciu_id]
    for alvo in ciu.targets:
        assert v2[("kc_09", alvo)] == model.ABSENT


def test_chutar_depois_de_acertar_algo_da_lacuna(d):
    """Com premissa já erguida, o chute produz LACUNA: prefixo confirmado,
    resto ausente, nenhum errado."""
    t = comeca(d, "socratic", ["kc_09"])
    ciu = d.cius[t.action.ciu_id]
    t = S.advance(d, t.state, S.Answer(ciu.id, "tenho certeza", 1000,
                                       option_idx=idx_de(ciu, correct=True)))
    assert t.action.kind == "ciu"
    ciu2 = d.cius[t.action.ciu_id]
    errado = next(i for i, o in enumerate(ciu2.options) if not o.correct)
    t = S.advance(d, t.state, S.Answer(ciu2.id, "chutei", 1000, option_idx=errado))
    assert model.cognitive_state(d, t.state.vector, "kc_09") == model.LACUNA


# --------------------------------------------------------------------------
# RF08: confronto visual antes do traversal
# --------------------------------------------------------------------------

def test_crenca_que_nega_no_base_passa_pelo_diagrama(d):
    """`star_assigns_pointer` nega kc_04:B4, um nó-base."""
    t = comeca(d, "socratic", ["kc_04"])
    vistos = []
    for _ in range(20):
        if t.action.kind == "diagram":
            vistos.append("diagram")
            break
        if t.action.kind == "ciu":
            ciu = d.cius[t.action.ciu_id]
            erro = ("star_assigns_pointer"
                    if any(o.misconception == "star_assigns_pointer" for o in ciu.options)
                    else None)
            t = responde(d, t, errando=erro)
        else:
            t = S.advance(d, t.state, S.StepAnswer(True, 100))
        vistos.append(t.action.kind)
    assert "diagram" in vistos
    assert t.action.data["controlled_by"] == "student", "o aluno controla a alternância"


def test_crenca_derivacional_nao_passa_pelo_diagrama(d):
    """`free_nullifies` nega kc_09:I1, uma inferência: o traversal basta."""
    t = comeca(d, "socratic", ["kc_09"])
    ciu = d.cius[t.action.ciu_id]
    t = S.advance(d, t.state, S.Answer(
        ciu.id, "tenho certeza", 8000,
        option_idx=idx_de(ciu, misconception="free_nullifies")))
    acoes = [t.action.kind]
    for _ in range(30):
        if t.action.kind in ("ask", "done", "conclude"):
            break
        if t.action.kind == "ciu":
            t = responde(d, t)
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
        acoes.append(t.action.kind)
    assert "diagram" not in acoes


# --------------------------------------------------------------------------
# §7.4 / RF09: regressão controlada
# --------------------------------------------------------------------------

def _ate_o_primeiro_ask(d, kc="kc_09", crenca="free_nullifies"):
    t = comeca(d, "socratic", [kc])
    for _ in range(20):
        if t.action.kind == "ask":
            return t
        if t.action.kind == "ciu":
            ciu = d.cius[t.action.ciu_id]
            erro = crenca if any(o.misconception == crenca for o in ciu.options) else None
            t = responde(d, t, errando=erro)
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
    raise AssertionError("não chegou a um passo socrático")


def test_primeiro_erro_reformula_sem_andar(d):
    t = _ate_o_primeiro_ask(d)
    cursor, no = t.state.cursor, t.action.node
    t2 = S.advance(d, t.state, S.StepAnswer(False, 4000))
    assert t2.state.cursor == cursor
    assert t2.action.node == no
    assert t2.action.text != t.action.text, "a pergunta tem de ser reformulada"
    assert not any(e.type == "regression_triggered" for e in t2.events)


def test_segundo_erro_no_mesmo_no_retrocede_um_passo(d):
    t = _ate_o_primeiro_ask(d)
    # anda um passo para ter para onde voltar
    t = S.advance(d, t.state, S.StepAnswer(True, 1000))
    assert t.action.kind == "ask"
    cursor = t.state.cursor
    t = S.advance(d, t.state, S.StepAnswer(False, 1000))   # 1a tentativa
    t = S.advance(d, t.state, S.StepAnswer(False, 1000))   # 2a tentativa
    assert t.state.cursor == cursor - 1
    assert any(e.type == "regression_triggered" for e in t.events)


def test_regressao_nao_descarta_o_confirmado(d):
    t = _ate_o_primeiro_ask(d)
    primeiro = t.action.node
    t = S.advance(d, t.state, S.StepAnswer(True, 1000))
    confirmado = t.state.vector[("kc_09", primeiro)]
    t = S.advance(d, t.state, S.StepAnswer(False, 1000))
    t = S.advance(d, t.state, S.StepAnswer(False, 1000))
    assert t.state.vector[("kc_09", primeiro)] == confirmado == model.CONFIRMED


def test_terceiro_erro_no_mesmo_no_encerra_o_kc_em_progresso(d):
    """As tentativas são POR NÓ (§7.4). Errar três nós diferentes uma vez
    cada não encerra nada — o aluno tem de travar no mesmo ponto.
    """
    t = _ate_o_primeiro_ask(d)
    t = S.advance(d, t.state, S.StepAnswer(True, 1000))   # confirma o 1o
    travado = t.action.node
    eventos = []

    t = S.advance(d, t.state, S.StepAnswer(False, 1000))  # 1a: reformula
    eventos.extend(t.events)
    assert t.action.node == travado

    t = S.advance(d, t.state, S.StepAnswer(False, 1000))  # 2a: retrocede
    eventos.extend(t.events)
    assert t.action.node != travado

    t = S.advance(d, t.state, S.StepAnswer(True, 1000))   # reconfirma o anterior
    eventos.extend(t.events)
    assert t.action.node == travado, "volta ao nó em que travou"

    t = S.advance(d, t.state, S.StepAnswer(False, 1000))  # 3a no mesmo nó
    eventos.extend(t.events)

    assert any(e.type == "kc_incomplete" for e in eventos)
    incompleto = next(e for e in eventos if e.type == "kc_incomplete")
    assert incompleto.payload["node"] == travado
    assert t.state.kc_status.get("kc_09") == S.EM_PROGRESSO


def test_sessao_travada_nao_entra_em_laco(d):
    """O invariante do §6: sempre há saída da correção."""
    t = comeca(d, "socratic", ["kc_09"])
    for i in range(300):
        if t.action.kind == "done":
            break
        if t.action.kind == "ciu":
            t = responde(d, t, errando="free_nullifies"
                         if any(o.misconception == "free_nullifies"
                                for o in d.cius[t.action.ciu_id].options) else None)
        elif t.action.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(False, 100))  # erra SEMPRE
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
    else:
        raise AssertionError("laço: o aluno que erra tudo não chega ao fim")
    assert t.state.done


# --------------------------------------------------------------------------
# RF10 e RF11
# --------------------------------------------------------------------------

def test_o_termo_tecnico_so_aparece_na_conclusao(d):
    _, _, acoes = roda(d, "socratic", ["kc_09"], erra_primeira="free_nullifies")
    termos = d.study.late_named_terms
    for a in acoes:
        texto = " ".join(str(v) for v in (a.text, a.data) if v).lower()
        vazou = [t for t in termos if t in texto]
        if a.kind == "conclude":
            continue
        assert not vazou, "%s vazou %s antes da conclusão" % (a.kind, vazou)
    conclusoes = [a for a in acoes if a.kind == "conclude"]
    assert conclusoes, "a sessão nunca nomeou a conclusão"


def test_kc_so_fecha_com_vetor_completo_e_acerto_na_variacao(d):
    estado, eventos, _ = roda(d, "socratic", ["kc_09"], erra_primeira="free_nullifies")
    completou = [e for e in eventos if e.type == "kc_completed"]
    assert len(completou) == 1
    vetor = completou[0].payload["vector"]
    assert set(vetor.values()) == {model.CONFIRMED}
    assert set(vetor) == set(d.kcs["kc_09"].nodes)


def test_errar_a_variacao_devolve_para_a_correcao(d):
    t = comeca(d, "socratic", ["kc_09"])
    for _ in range(60):
        if t.state.phase == S.VARIACAO:
            break
        if t.action.kind == "ciu":
            t = responde(d, t)
        elif t.action.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 100))
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
    assert t.state.phase == S.VARIACAO
    ciu = d.cius[t.action.ciu_id]
    errado = next(o.misconception for o in ciu.options
                  if not o.correct and o.misconception)
    t = responde(d, t, errando=errado)
    assert t.state.phase == S.CORRECAO
    assert t.action.kind in ("ask", "explain")


# --------------------------------------------------------------------------
# Pureza e determinismo (RNF02)
# --------------------------------------------------------------------------

def test_a_fsm_e_deterministica(d):
    corridas = {
        tuple((e.type, e.payload.get("kc"), e.payload.get("node"),
               e.payload.get("ciu_id")) for e in roda(d, "socratic", ["kc_09"],
                                                      erra_primeira="free_nullifies")[1])
        for _ in range(20)
    }
    assert len(corridas) == 1


def test_a_fsm_nao_muta_o_estado_recebido(d):
    t = comeca(d, "socratic", ["kc_09"])
    antes = dict(t.state.vector)
    ciu = d.cius[t.action.ciu_id]
    S.advance(d, t.state, S.Answer(ciu.id, "tenho certeza", 1000,
                                   option_idx=idx_de(ciu, correct=True)))
    assert dict(t.state.vector) == antes


def test_evento_do_tipo_errado_falha_alto(d):
    t = comeca(d, "socratic", ["kc_09"])
    with pytest.raises(ValueError, match="DIAGNOSTICO espera Answer"):
        S.advance(d, t.state, S.StepAnswer(True, 0))


def test_braco_desconhecido_falha_no_start(d):
    with pytest.raises(ValueError, match="braço desconhecido"):
        S.start(d, "hibrido", ["kc_09"])


def test_a_acao_serializa_para_o_contrato_do_paragrafo_9(d):
    t = comeca(d, "socratic", ["kc_09"])
    j = t.action.as_json()
    assert j["kind"] == "ciu" and j["ciu_id"] and "options" in j
    assert set(j) >= {"kind", "kc", "ciu_id"}


def test_crenca_fundacional_na_variacao_tambem_passa_pelo_diagrama(d):
    """RF08 vale em QUALQUER ponto em que a crença é detectada.

    `string_literal_is_array` nega kc_07:B1, um nó-base, e só é detectável
    por `ciu_kc07_006`, que é de variação. Se o confronto visual só
    existisse na saída do diagnóstico, essa crença — uma das três
    fundacionais do catálogo — nunca teria diagrama.
    """
    t = comeca(d, "socratic", ["kc_07"])
    for _ in range(40):
        if t.action.kind == "diagram":
            break
        if t.action.kind == "ciu":
            ciu = d.cius[t.action.ciu_id]
            erro = ("string_literal_is_array"
                    if any(o.misconception == "string_literal_is_array"
                           for o in ciu.options) else None)
            t = responde(d, t, errando=erro)
        elif t.action.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 100))
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
    assert t.action.kind == "diagram", "a crença fundacional não acionou o diagrama"
    assert t.action.node == "B1"
    assert t.action.data["visual"], "o diagrama veio sem especificação visual"


# --------------------------------------------------------------------------
# A pergunta não pode mandar olhar o que não está na tela
# --------------------------------------------------------------------------

def test_sem_diagrama_a_pergunta_nao_manda_olhar_o_diagrama(d):
    """O confronto visual acontece antes do traversal e só quando a crença
    nega um nó-base. Na maioria dos traversals não há diagrama nenhum, e a
    pergunta mandava o aluno olhar para algo que não existe na tela."""
    t = comeca(d, "socratic", ["kc_07"])
    vistos = 0
    for _ in range(40):
        a = t.action
        if a.kind == "done":
            break
        if a.kind in ("ask", "explain"):
            vistos += 1
            tem_figura = bool((a.data or {}).get("visual"))
            menciona = "diagrama" in (a.text or "").lower()
            assert menciona <= tem_figura, (
                "%s:%s manda olhar o diagrama e não há diagrama na tela"
                % (a.kc, a.node)
            )
            t = S.advance(d, t.state, S.StepAnswer(True, 100))
        elif a.kind == "ciu":
            t = responde(d, t)
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
    assert vistos > 0, "a sessão não chegou a nenhum passo"


def test_com_confronto_visual_o_diagrama_segue_no_traversal(d):
    """RF08 existe porque só a observação direta reintroduz um fato-base.
    Tirar a figura da tela justo quando o aluno vai confirmar esses fatos
    desfaria o efeito — e deixaria a pergunta mentindo."""
    t = comeca(d, "socratic", ["kc_07"])
    for _ in range(40):
        if t.action.kind == "diagram":
            break
        if t.action.kind == "ciu":
            ciu = d.cius[t.action.ciu_id]
            erro = ("string_literal_is_array"
                    if any(o.misconception == "string_literal_is_array"
                           for o in ciu.options) else None)
            t = responde(d, t, errando=erro)
        elif t.action.kind in ("ask", "explain"):
            t = S.advance(d, t.state, S.StepAnswer(True, 100))
        else:
            t = S.advance(d, t.state, S.Acknowledge(0))
    assert t.action.kind == "diagram"

    t = S.advance(d, t.state, S.Acknowledge(1000))     # fecha o confronto
    assert t.action.kind in ("ask", "explain")
    assert t.action.data.get("visual"), "o diagrama sumiu ao entrar no traversal"
    assert "diagrama" in t.action.text.lower()


def test_o_diagrama_no_traversal_e_igual_nos_dois_bracos(d):
    """§8.1: o diagrama está na lista do que não pode diferir."""
    def figuras(arm):
        t = comeca(d, arm, ["kc_07"])
        out = []
        for _ in range(60):
            a = t.action
            if a.kind == "done":
                break
            if a.kind in ("ask", "explain"):
                out.append((a.kc, a.node, bool((a.data or {}).get("visual"))))
                t = S.advance(d, t.state, S.StepAnswer(True, 100))
            elif a.kind == "ciu":
                ciu = d.cius[a.ciu_id]
                erro = ("string_literal_is_array"
                        if any(o.misconception == "string_literal_is_array"
                               for o in ciu.options) else None)
                t = responde(d, t, errando=erro)
            else:
                t = S.advance(d, t.state, S.Acknowledge(0))
        return out
    assert figuras("socratic") == figuras("direct")
