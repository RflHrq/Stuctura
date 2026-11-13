"""O que vale para TODO tópico que tem escada.

O kc_00 foi o molde, e os testes dele (`test_trilha_conteudo.py`,
`test_trilha_invariantes.py`) conferem o conteúdo e as sessões daquele
tópico. A partir do kc_02 os tópicos entram um a um, e o que se exige de
um se exige de todos: é o que "tópico pronto" quer dizer em
docs/trilha.md, seção 7.

    - a escada cobre todas as premissas, e o compilador a aprova;
    - a leitura que está em docs/ é a do conteúdo de hoje;
    - toda crença tem a sua prova de iniciante, e é dita num degrau
      guiado da premissa que ela nega;
    - ninguém digita endereço: o número de um lugar muda a cada máquina;
    - e as sessões dos alunos simulados cabem nos tetos, terminam, e não
      fecham premissa sem resposta certa.

Tópico novo entra aqui sozinho: basta o arquivo da escada existir.
"""

from __future__ import annotations

import functools
import pathlib
import re
import sys

import pytest
from fastapi.testclient import TestClient

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import confere_escada  # noqa: E402
import oraculo  # noqa: E402
from trilha_alunos import PERSONAS, caminha, conta  # noqa: E402

from mvp import motor, portal, trilha, trilha_escada  # noqa: E402
from mvp.dominio import carrega, topicos  # noqa: E402

TOPICOS = [t for t in topicos() if confere_escada.arquivo_da_escada(t).exists()]

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)
cada_topico = pytest.mark.parametrize("topico", TOPICOS)


@functools.lru_cache(maxsize=None)
def _dominio(topico):
    return carrega(topico=topico)


@functools.lru_cache(maxsize=None)
def _escadas(topico):
    return trilha_escada.le(confere_escada.arquivo_da_escada(topico),
                            _dominio(topico))


def _versoes(topico):
    for e in _escadas(topico).values():
        for g in e.degraus:
            for k, v in enumerate(g.versoes):
                yield e, g, k, v


def test_o_kc_00_e_o_kc_02_tem_escada():
    """Os dois tópicos prontos em 13/11/2026. A lista só cresce."""
    assert {"kc_00", "kc_02"} <= set(TOPICOS)


# --------------------------------------------------------------------------
# O conteúdo
# --------------------------------------------------------------------------

@cada_topico
def test_a_escada_cobre_todas_as_premissas(topico):
    d, escadas = _dominio(topico), _escadas(topico)
    assert trilha_escada.faltando(d, escadas) == ()
    assert list(escadas) == list(d.ordem)


@cada_topico
@tem_gcc
def test_o_compilador_aprova_a_escada_e_as_provas(topico):
    assert confere_escada.confere(_escadas(topico)) == []


@cada_topico
def test_a_leitura_no_repositorio_e_a_do_conteudo_de_hoje(topico):
    arquivo = RAIZ / "docs" / ("escada-%s-leitura.md" % topico.replace("_", ""))
    assert arquivo.read_text(encoding="utf-8") == confere_escada.leitura(
        _dominio(topico), _escadas(topico))


@cada_topico
def test_os_ids_dos_degraus_seguem_o_padrao_do_topico(topico):
    prefixo = "esc_%s_" % topico.replace("_", "")
    for e in _escadas(topico).values():
        for i, g in enumerate(e.degraus):
            assert g.id == "%s%s_%d" % (prefixo, e.premissa, i + 1)


@cada_topico
def test_toda_crenca_tem_prova_de_iniciante(topico):
    d, escadas = _dominio(topico), _escadas(topico)
    for c in d.crencas.values():
        assert escadas[c.nega].prova(c.id) is not None, c.id


@cada_topico
def test_toda_crenca_e_dita_num_degrau_guiado_da_premissa_que_ela_nega(topico):
    d = _dominio(topico)
    ditas = set()
    for e, g, k, v in _versoes(topico):
        for x in v.erros:
            if x.crenca:
                assert g.guiado, (g.id, x.crenca)
                assert d.crencas[x.crenca].nega == e.premissa, (g.id, x.crenca)
                ditas.add(x.crenca)
    assert ditas == set(d.crencas)


@cada_topico
def test_as_duas_versoes_de_um_degrau_nao_sao_a_mesma(topico):
    for e in _escadas(topico).values():
        for g in e.degraus:
            assert len({(v.pede, v.mostra, v.antes, v.pecas)
                        for v in g.versoes}) == len(g.versoes), g.id


@cada_topico
def test_todo_exercicio_tem_erro_previsto_e_retorno_que_explica(topico):
    for e, g, k, v in _versoes(topico):
        assert v.erros, (g.id, k + 1)
        for texto in [x.retorno for x in v.erros] + [v.retorno_geral]:
            assert len(texto.split()) >= 5, (g.id, k + 1, texto)


@cada_topico
def test_ninguem_digita_endereco(topico):
    """O número de um lugar muda a cada máquina e a cada execução: não é
    resposta que se confira. Degrau de `digitar` pede valor guardado."""
    for e, g, k, v in _versoes(topico):
        if g.forma == "digitar":
            assert "%p" not in (v.mostra + v.programa), (g.id, k + 1)


@cada_topico
def test_nenhuma_prova_e_programa_de_examinador(topico):
    for e in _escadas(topico).values():
        for p in e.provas:
            assert "puts(" not in p.programa and "?" not in p.programa, p.crenca
            assert len(p.programa.strip().splitlines()) <= 9, p.crenca


@cada_topico
def test_a_previsao_nao_e_sempre_na_mesma_posicao(topico):
    posicoes = {p.previsao.real for e in _escadas(topico).values()
                for p in e.provas}
    assert len(posicoes) >= 2


@cada_topico
def test_o_verbo_e_reclama(topico):
    """Que o compilador recuse é fato sobre um compilador."""
    for e, g, k, v in _versoes(topico):
        for texto in [x.retorno for x in v.erros] + [v.retorno_geral, v.pede]:
            assert not re.search(r"não compila|recusa", texto), (g.id, texto)


# --------------------------------------------------------------------------
# As sessões
# --------------------------------------------------------------------------

SESSOES = [(t, p, m, r) for t in TOPICOS for p in PERSONAS
           for m in trilha.MODOS for r in trilha.RITMOS]
cada_sessao = pytest.mark.parametrize("topico, persona, modo, ritmo", SESSOES)


@functools.lru_cache(maxsize=None)
def _sessao(topico, persona, modo, ritmo):
    return caminha(_dominio(topico), _escadas(topico), persona, modo, ritmo,
                   "t1")


@cada_sessao
def test_toda_sessao_termina_com_resultado_em_toda_premissa(
        topico, persona, modo, ritmo):
    c = _sessao(topico, persona, modo, ritmo)
    assert c.estado.fim and c.telas[-1].tipo == "mapa"
    for no in _dominio(topico).ordem:
        assert c.estado.premissa(no).resultado in trilha.RESULTADOS, no


@cada_sessao
def test_ninguem_passa_do_teto_numa_premissa(topico, persona, modo, ritmo):
    c = _sessao(topico, persona, modo, ritmo)
    for no in _dominio(topico).ordem:
        assert c.estado.premissa(no).telas <= trilha.TETO_TELAS, no


@cada_sessao
def test_ninguem_fica_preso_num_degrau(topico, persona, modo, ritmo):
    c = _sessao(topico, persona, modo, ritmo)
    assert all(t.dados["tentativa"] <= 2
               for t in c.telas if t.tipo == "degrau")


@cada_sessao
def test_nenhuma_premissa_fecha_bem_sem_resposta_certa(
        topico, persona, modo, ritmo):
    c = _sessao(topico, persona, modo, ritmo)
    bons = (trilha.JA_SABIA, trilha.FIRMOU, trilha.APRENDEU, trilha.CORRIGIU)
    for no in _dominio(topico).ordem:
        if c.estado.premissa(no).resultado not in bons:
            continue
        certas = [e for e in c.eventos
                  if e.dados.get("no") == no and (
                      (e.tipo == "episodio_classificado"
                       and e.dados["estado"] in (motor.CONFIRMADA,
                                                 motor.FRAGIL_EP))
                      or (e.tipo == "degrau_respondido" and e.dados["certa"]))]
        assert certas, no


@cada_sessao
def test_a_maquina_mostra_a_prova_da_escada(topico, persona, modo, ritmo):
    c = _sessao(topico, persona, modo, ritmo)
    escadas = _escadas(topico)
    for t in (t for t in c.telas if t.tipo == "maquina"):
        no = t.dados["premissa"]
        propria = escadas[no].prova(c.estado.premissa(no).crenca)
        assert propria is not None and t.dados["tem_prova"] is True
        assert t.dados["programa"] == propria.programa
        assert t.dados["previu"] is not None


@cada_topico
def test_quem_sabe_tudo_termina_dentro_do_teto(topico):
    """Duas telas por premissa, mais a entrada e o mapa (spec, seção 8)."""
    d = _dominio(topico)
    for ritmo in trilha.RITMOS:
        c = _sessao(topico, "sabe", "direto", ritmo)
        assert conta(c) <= 2 * len(d.ordem) + 2, ritmo
        assert {c.estado.premissa(n).resultado for n in d.ordem} == {
            trilha.JA_SABIA}


@cada_topico
def test_quem_diz_cada_crenca_passa_pela_prova_dela(topico):
    d = _dominio(topico)
    c = _sessao(topico, "crente_aprende", "direto", "rapido")
    provas = [e.dados for e in c.eventos if e.tipo == "prova_apresentada"]
    assert sorted(p["no"] for p in provas) == sorted(d.ordem)
    assert all(d.crencas[p["crenca"]].nega == p["no"] for p in provas)


# --------------------------------------------------------------------------
# O portal
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    return TestClient(portal.cria_portal(tmp_path_factory.mktemp("topicos")))


def test_o_portal_abre_a_trilha_de_todo_topico_com_escada(cliente):
    lista = cliente.get("/topicos").json()["topicos"]
    assert {t["id"]: t["trilha"] for t in lista} == {
        t: ("/trilha/%s/" % t if t in TOPICOS else None) for t in topicos()}


@cada_topico
def test_a_trilha_do_topico_responde(cliente, topico):
    d = _dominio(topico)
    saude = cliente.get("/trilha/%s/saude" % topico).json()
    assert saude["topico"] == topico and saude["premissas"] == len(d.ordem)
    r = cliente.post("/trilha/%s/sessoes" % topico, json={})
    assert r.status_code == 200 and r.json()["tela"]["tipo"] == "entrada"


# --------------------------------------------------------------------------
# Questão posta fora da trilha
# --------------------------------------------------------------------------
#
# A trilha serve as questões de marcar do banco do tópico, e o banco foi
# escrito para o fluxo anterior, em que um cartão ensinava cada construto
# antes de ele ser cobrado. Onde uma questão usa o que a escada do tópico
# não ensina — `sizeof` e `int **` no kc_02 —, a escada a declara fora,
# com o motivo. O banco não muda: é material revisado, e o fluxo anterior
# continua servindo a questão.

def test_a_escada_declara_as_questoes_que_ficam_fora(tmp_path):
    from mvp.test_trilha_escada import _escreve, _valida
    d = _dominio("kc_00")
    bloco = _valida()
    bloco["fora_da_trilha"] = ["ciu_kc00_t01"]
    e = trilha_escada.le(_escreve(tmp_path, {"B1": bloco}), d)["B1"]
    assert e.fora == ("ciu_kc00_t01",)
    sem = trilha_escada.le(_escreve(tmp_path, {"B1": _valida()}), d)["B1"]
    assert sem.fora == ()


@pytest.mark.parametrize("ids, diz", [
    (["nao_existe"], "questão desconhecida"),
    # A questão é do tópico, mas de OUTRA premissa.
    (["ciu_kc00_004"], "não é desta premissa"),
    # Tirar as duas de diagnóstico com razão deixa a premissa sem abertura.
    (["ciu_kc00_001", "ciu_kc00_002"], "sem pergunta de abertura"),
])
def test_questao_fora_da_trilha_e_conferida(tmp_path, ids, diz):
    from mvp.test_trilha_escada import _escreve, _valida
    bloco = _valida()
    bloco["fora_da_trilha"] = ids
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        trilha_escada.le(_escreve(tmp_path, {"B1": bloco}), _dominio("kc_00"))
    assert any(diz in p for p in erro.value.problemas), erro.value.problemas


def test_a_abertura_pula_a_questao_que_esta_fora():
    d = _dominio("kc_00")
    de_sempre = trilha.abertura(d, "B1")
    outra = trilha.abertura(d, "B1", fora=(de_sempre.id,))
    assert outra.id != de_sempre.id and outra.no == "B1"


def test_nenhuma_sessao_serve_questao_que_esta_fora():
    """Com uma questão de treino do kc_00 posta fora, ninguém a recebe —
    nem no reforço, nem no treino, nem na reconferência."""
    import dataclasses
    d, escadas = _dominio("kc_00"), dict(_escadas("kc_00"))
    servidas = {t.dados["atividade"] for p in PERSONAS
                for t in caminha(d, escadas, p).telas if t.tipo == "pergunta"}
    alvo = "ciu_kc00_t03"
    assert alvo in servidas                      # sem a marca, ela aparece
    escadas["B2"] = dataclasses.replace(escadas["B2"], fora=(alvo,))
    for persona in PERSONAS:
        for modo in trilha.MODOS:
            c = caminha(d, escadas, persona, modo)
            assert c.telas[-1].tipo == "mapa"
            assert alvo not in {t.dados["atividade"] for t in c.telas
                                if t.tipo == "pergunta"}, (persona, modo)


@cada_sessao
def test_as_questoes_declaradas_fora_nao_aparecem(topico, persona, modo, ritmo):
    fora = {i for e in _escadas(topico).values() for i in e.fora}
    c = _sessao(topico, persona, modo, ritmo)
    assert not fora & {t.dados["atividade"] for t in c.telas
                       if t.tipo == "pergunta"}


def test_no_kc_02_ficam_fora_as_quatro_que_usam_o_que_a_escada_nao_ensina():
    escadas = _escadas("kc_02")
    assert {no: e.fora for no, e in escadas.items() if e.fora} == {
        "B2": ("kc02_gb2_n2_2", "kc02_gb2_n3_3"),
        "I2": ("ciu_kc02_t14", "kc02_gi2_n2_2"),
    }
    # E são só elas: nenhuma outra questão que a trilha pode servir usa
    # sizeof, %zu, ponteiro para ponteiro ou double.
    d = _dominio("kc_02")
    fora = {i for e in escadas.values() for i in e.fora}
    ruim = re.compile(r"\b(double|float|sizeof)\b|%zu|\*\*")
    for a in d.atividades:
        if a.id not in fora and len(motor.razoes_de(d, a)) >= 2:
            assert not ruim.search((a.codigo or "") + a.enunciado), a.id


def _servidas_pela_trilha(topico, no):
    d, fora = _dominio(topico), _escadas(topico)[no].fora
    return [a.id for uso in ("diagnostico", "treino")
            for a in d.atividades_do_no(no, uso)
            if a.id not in fora and len(motor.razoes_de(d, a)) >= 2]


def test_no_kc_03_ficam_fora_as_onze_que_usam_o_que_a_escada_nao_ensina():
    """O banco do kc_03 não foi mexido: os cartões do tópico contam com o
    cenário de cada questão. O que a escada não ensina fica fora."""
    escadas = _escadas("kc_03")
    assert {no: e.fora for no, e in escadas.items() if e.fora} == {
        "B1": ("ciu_kc03_002", "ciu_kc03_t03"),
        "B3": ("ciu_kc03_008", "ciu_kc03_009", "ciu_kc03_t08", "ciu_kc03_t09"),
        "I1": ("ciu_kc03_t11",),
        "I2": ("ciu_kc03_014", "ciu_kc03_t14", "ciu_kc03_t15"),
        "I3": ("ciu_kc03_017",),
    }
    d = _dominio("kc_03")
    ruim = re.compile(r"\b(double|float|sizeof|malloc|if|for|while|return)\b"
                      r"|%zu|\*\*|\[|\(void\)")
    por_id = {a.id: a for a in d.atividades}
    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_03", no):
            a = por_id[i]
            assert not ruim.search((a.codigo or "") + a.enunciado), i
    # O custo, dito: o B3 fica com duas questões de marcar, e é a única
    # premissa do tópico que abre com a de conceito.
    assert {no: len(_servidas_pela_trilha("kc_03", no)) for no in d.ordem} == {
        "B1": 4, "B2": 6, "B3": 2, "I1": 5, "I2": 3, "I3": 5}
    aberturas = {no: trilha.abertura(d, no, fora=escadas[no].fora)
                 for no in d.ordem}
    assert {no: a.id for no, a in aberturas.items()} == {
        "B1": "ciu_kc03_003", "B2": "ciu_kc03_005", "B3": "ciu_kc03_007",
        "I1": "ciu_kc03_011", "I2": "ciu_kc03_015", "I3": "ciu_kc03_018"}
    assert [no for no, a in aberturas.items() if not a.codigo] == ["B3"]


def test_sem_a_questao_de_degrau_2_a_premissa_abre_com_a_de_codigo():
    """A abertura é a questão de código de degrau 2: é a que APLICA a
    ideia. Quando ela fica fora da trilha, quem abre é outra de código, e
    não a que pede só a definição — foi o que o kc_03 pediu, onde quatro
    das seis questões de degrau 2 usam o que a escada não ensina."""
    d = _dominio("kc_00")
    de_sempre = trilha.abertura(d, "B4")
    assert de_sempre.nivel == 2 and de_sempre.codigo
    # Sem ela, sobram no B4 uma de conceito (a 007) — e nenhuma de código
    # de diagnóstico: a abertura cai na de conceito, que é o que há.
    sem = trilha.abertura(d, "B4", fora=(de_sempre.id,))
    assert sem.uso == "diagnostico" and not sem.codigo

    d3 = _dominio("kc_03")
    # No B1 do kc_03, sem a 002, sobram a 001 (conceito) e a 003 (código,
    # degrau 3). A de código vem primeiro.
    assert trilha.abertura(d3, "B1").id == "ciu_kc03_002"
    outra = trilha.abertura(d3, "B1", fora=("ciu_kc03_002",))
    assert outra.id == "ciu_kc03_003" and outra.codigo
