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
def test_o_passo_de_pratica_da_subida_tem_nome(topico):
    """É o passo em que a pessoa mais tropeça, e o enunciado dele pode ser
    só "Que número este trecho mostra na tela?". O fechamento diz o NOME
    do passo, que é a ideia dele — e por isso ele não é uma pergunta."""
    for e in _escadas(topico).values():
        g = e.pratica[0]
        assert g.nome, g.id
        assert "?" not in g.nome and len(g.nome.split()) <= 10, g.id


@cada_topico
def test_o_treino_nao_repete_o_trecho_da_prova(topico):
    """Quem diz a crença vê a prova e vai direto para os passos de prática
    da mesma premissa. Um passo que mostre o trecho que a prova acabou de
    mostrar é a mesma tela duas vezes seguidas — foi o que apareceu no
    ensaio do kc_01, com a função que devolve o endereço de uma local."""
    def limpo(codigo):
        return " ".join(codigo.split())

    for e in _escadas(topico).values():
        provas = [limpo(p.programa) for p in e.provas]
        for g in e.pratica:
            for k, v in enumerate(g.versoes):
                trecho = "\n".join(x for x in (v.antes, v.mostra) if x.strip())
                linhas = [x for x in trecho.split("\n") if x.strip()]
                # Uma declaração solta todo trecho do tópico tem. Conta
                # como repetição a função inteira, ou três linhas ou mais.
                if not (len(linhas) >= 3 or any(
                        confere_escada.FUNCAO.match(x) for x in linhas)):
                    continue
                assert not any(limpo(trecho) in p for p in provas), (
                    g.id, k + 1)


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


def _selecao(topico):
    """O que a escada do tópico deixa fora, quantas questões cada
    premissa tem para a trilha, e com qual ela abre."""
    d, escadas = _dominio(topico), _escadas(topico)
    return (
        {no: e.fora for no, e in escadas.items() if e.fora},
        {no: len(_servidas_pela_trilha(topico, no)) for no in d.ordem},
        {no: trilha.abertura(d, no, fora=escadas[no].fora).id
         for no in d.ordem})


def test_no_kc_04_ficam_fora_nove_e_toda_premissa_abre_com_codigo():
    fora, quantas, abre = _selecao("kc_04")
    assert fora == {
        "B1": ("ciu_kc04_002", "ciu_kc04_t02", "ciu_kc04_t03"),
        "B2": ("ciu_kc04_t06",),
        "B3": ("ciu_kc04_008",),
        "I1": ("ciu_kc04_t12",),
        "I2": ("ciu_kc04_014", "ciu_kc04_t14"),
        "I3": ("ciu_kc04_017",),
    }
    assert quantas == {"B1": 3, "B2": 5, "B3": 5, "I1": 5, "I2": 4, "I3": 5}
    assert abre == {
        "B1": "ciu_kc04_003", "B2": "ciu_kc04_005", "B3": "ciu_kc04_009",
        "I1": "ciu_kc04_011", "I2": "ciu_kc04_015", "I3": "ciu_kc04_018"}
    d = _dominio("kc_04")
    por_id = {a.id: a for a in d.atividades}
    assert all(por_id[i].codigo for i in abre.values())
    # Nenhuma questão servida usa o que as escadas até o kc_04 não
    # ensinam: vetor, malloc, o ++, protótipo sem corpo, aritmética de
    # ponteiro, a comparação impressa.
    ruim = re.compile(
        r"\b(malloc|sizeof|return)\b|\+\+|\[|=="
        # o protótipo, que é a função sem corpo: `void f(int *p);`
        r"|^\s*(?:void|int)\s+\w+\([^)]*\);"
        # e o ponteiro andando: `p = p + 1`. A conta no VALOR,
        # `*p = *p + 1`, é outra coisa, e é servida.
        r"|(?<![*\w])p\s*=\s*p\s*\+", re.M)
    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_04", no):
            achou = ruim.search(por_id[i].codigo or "")
            assert not achou, (i, achou.group(0))
    # A régua morde: as nove de fora são pegas por ela, menos a da
    # multiplicação escrita com o mesmo * (`*n = *n * 2`), que é saída
    # por leitura, e não por construto.
    pegas = {i for ids in fora.values() for i in ids
             if ruim.search(por_id[i].codigo or "")}
    assert {i for ids in fora.values() for i in ids} - pegas == {
        "ciu_kc04_t06"}


def test_no_kc_05_ficam_fora_doze_e_so_o_i2_abre_com_conceito():
    fora, quantas, abre = _selecao("kc_05")
    assert fora == {
        "B1": ("ciu_kc05_002", "ciu_kc05_t02"),
        "B2": ("ciu_kc05_t06",),
        "B3": ("ciu_kc05_009", "ciu_kc05_t09"),
        "I1": ("ciu_kc05_011", "ciu_kc05_t12"),
        "I2": ("ciu_kc05_014", "ciu_kc05_t14", "ciu_kc05_015"),
        "I3": ("ciu_kc05_017", "ciu_kc05_t18"),
    }
    assert quantas == {"B1": 4, "B2": 5, "B3": 4, "I1": 4, "I2": 3, "I3": 4}
    assert abre == {
        "B1": "ciu_kc05_003", "B2": "ciu_kc05_005", "B3": "ciu_kc05_008",
        "I1": "ciu_kc05_012", "I2": "ciu_kc05_013", "I3": "ciu_kc05_018"}
    d = _dominio("kc_05")
    por_id = {a.id: a for a in d.atividades}
    assert [no for no, i in abre.items() if not por_id[i].codigo] == ["I2"]
    ruim = re.compile(r"\b(malloc|sizeof|return|memcpy|memcmp|memset)\b"
                      r"|&&|\[|%zu|%s|%c")
    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_05", no):
            assert not ruim.search(por_id[i].codigo or ""), i


FUNCAO_NO_TRECHO = re.compile(r"^\s*(?:/\*.*?\*/\s*)?(?:void|int)\s+\w+\(", re.M)


def _tem_global(codigo):
    """Variável declarada ANTES da linha de uma função: no trecho de uma
    questão, é a variável global — a que a função enxerga sem receber."""
    linhas = [x for x in codigo.split("\n") if x.strip()]
    funcoes = [i for i, x in enumerate(linhas) if FUNCAO_NO_TRECHO.match(x)]
    return bool(funcoes) and any(
        re.match(r"\s*int\b[^()]*;", x) for x in linhas[:funcoes[-1]])


def test_no_kc_06_ficam_fora_sete_e_so_o_b2_abre_com_conceito():
    """O banco do kc_06 não foi mexido. Ficam fora as sete questões que
    usam o que escada nenhuma ensinou até aqui: variável global, `return`,
    o `++`, ponteiro para ponteiro, `malloc`."""
    fora, quantas, abre = _selecao("kc_06")
    assert fora == {
        "B1": ("ciu_kc06_003",),
        "B2": ("ciu_kc06_005", "ciu_kc06_t05", "ciu_kc06_006", "ciu_kc06_t06"),
        "I3": ("ciu_kc06_015", "ciu_kc06_t15"),
    }
    # O custo, dito: o B2 fica com as duas questões de conceito, e é a
    # única premissa do tópico que não abre com código.
    assert quantas == {"B1": 5, "B2": 2, "I1": 6, "I2": 6, "I3": 4, "I4": 6}
    assert abre == {
        "B1": "ciu_kc06_002", "B2": "ciu_kc06_004", "I1": "ciu_kc06_008",
        "I2": "ciu_kc06_011", "I3": "ciu_kc06_014", "I4": "ciu_kc06_017"}
    d = _dominio("kc_06")
    por_id = {a.id: a for a in d.atividades}
    assert [no for no, i in abre.items() if not por_id[i].codigo] == ["B2"]
    ruim = re.compile(r"\b(malloc|sizeof|return)\b|\+\+|\*\*|\(void\)")

    def fora_da_regua(i):
        codigo = por_id[i].codigo or ""
        return bool(ruim.search(codigo)) or _tem_global(codigo)

    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_06", no):
            assert not fora_da_regua(i), i
    # A régua morde: as sete de fora são pegas por ela, todas.
    assert all(fora_da_regua(i) for ids in fora.values() for i in ids)


def test_o_kc_06_ensina_o_que_as_questoes_dele_usam():
    """Sete questões servidas usam função com mais de um parâmetro, ou
    variável declarada dentro da função — a troca de dois valores entre
    elas. As duas coisas são apresentadas num passo guiado do B1, a
    primeira premissa, antes de qualquer questão que as use no treino."""
    d, escadas = _dominio("kc_06"), _escadas("kc_06")
    por_id = {a.id: a for a in d.atividades}
    dois = re.compile(r"\w+\((?:int\s*\*?\s*\w+\s*,\s*)+int\s*\*?\s*\w+\)\s*\{")
    local = re.compile(r"\{[^}]*\bint\s*\*?\s*\w+\s*=")
    usam = {i for no in d.ordem for i in _servidas_pela_trilha("kc_06", no)
            if dois.search(por_id[i].codigo or "")
            or local.search(por_id[i].codigo or "")}
    assert usam == {"ciu_kc06_t02", "ciu_kc06_t03", "ciu_kc06_t09",
                    "ciu_kc06_t12", "ciu_kc06_014", "ciu_kc06_t17",
                    "ciu_kc06_t18"}
    guiados = [g for g in escadas["B1"].degraus if g.guiado]
    apresenta = [g for g in guiados
                 if any(dois.search(v.mostra) and local.search(v.mostra)
                        for v in g.versoes)]
    assert len(apresenta) == 1
    frases = " ".join(apresenta[0].frases)
    assert "mais de um parâmetro" in frases and "dentro das chaves" in frases
    # E as palavras que as questões de conceito usam estão ditas num passo
    # guiado: argumento, local, por valor, por referência.
    dito = " ".join(f for e in escadas.values() for g in e.degraus
                    for f in g.frases)
    for palavra in ("argumento", "local", "passagem por valor",
                    "passagem por referência"):
        assert palavra in dito, palavra


def test_no_kc_07_ficam_fora_dezesseis_e_toda_premissa_abre_com_codigo():
    """O banco do kc_07 não foi mexido. É o tópico que mais apresenta
    coisa nova, e mesmo assim dezesseis das 48 questões usam o que escada
    nenhuma ensinou."""
    fora, quantas, abre = _selecao("kc_07")
    assert fora == {
        "B1": ("ciu_kc07_003", "ciu_kc07_t03",
               "mol_kc07_B1_treino_1__achar_o_erro_05",
               "mol_kc07_B1_treino_1__comparar_casos_06"),
        "B2": ("ciu_kc07_t06",),
        "B3": ("ciu_kc07_t09",),
        "B4": ("ciu_kc07_012", "ciu_kc07_t11", "ciu_kc07_t12"),
        "I1": ("ciu_kc07_015", "ciu_kc07_t14"),
        "I2": ("ciu_kc07_018", "ciu_kc07_t17", "ciu_kc07_t18"),
        "I3": ("ciu_kc07_020", "ciu_kc07_t21"),
    }
    assert quantas == {"B1": 8, "B2": 5, "B3": 5, "B4": 3,
                       "I1": 4, "I2": 3, "I3": 4}
    assert abre == {
        "B1": "ciu_kc07_002", "B2": "ciu_kc07_005", "B3": "ciu_kc07_008",
        "B4": "ciu_kc07_011", "I1": "ciu_kc07_014", "I2": "ciu_kc07_017",
        "I3": "ciu_kc07_021"}
    d = _dominio("kc_07")
    por_id = {a.id: a for a in d.atividades}
    assert all(por_id[i].codigo for i in abre.values())
    # O que escada nenhuma ensinou até aqui: malloc, strcpy, extern,
    # return, laço, double e long, ponteiro para ponteiro, a conta com
    # endereço (a + 1), a conversão para (void *), o protótipo sem corpo,
    # escrever num texto entre aspas (p[0] = 'E') e variável global.
    ruim = re.compile(
        r"\b(malloc|strcpy|extern|return|for|double|long)\b"
        r"|\*\*|\+ 1|\(void \*\)|= 'E'"
        r"|^\s*(?:void|int)\s+\w+\([^)]*\);", re.M)

    def fora_da_regua(i):
        codigo = por_id[i].codigo or ""
        return bool(ruim.search(codigo)) or _tem_global(codigo)

    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_07", no):
            assert not fora_da_regua(i), i
    # A régua morde: as dezesseis de fora são pegas por ela, todas.
    assert all(fora_da_regua(i) for ids in fora.values() for i in ids)


def test_o_b1_do_kc_07_tem_duas_crencas_e_cada_uma_a_sua_prova():
    """É a primeira premissa com duas crenças que a negam: "uma caixa com
    os valores dentro" e "char * e char [] guardam do mesmo jeito". Cada
    uma tem a sua prova, e cada uma é dita num passo guiado diferente."""
    d, e = _dominio("kc_07"), _escadas("kc_07")["B1"]
    duas = {c.id for c in d.crencas.values() if c.nega == "B1"}
    assert duas == {"array_confused_with_cell", "string_literal_is_array"}
    assert {p.crenca for p in e.provas} == duas
    onde = {x.crenca: g.id for g in e.degraus for v in g.versoes
            for x in v.erros if x.crenca}
    assert set(onde) == duas and len(set(onde.values())) == 2


def test_cada_crenca_do_b1_do_kc_07_leva_a_prova_dela():
    """As duas crenças do B1 chegam à prova por caminhos diferentes: a das
    letras pela pergunta de abertura, que é sobre elas; a da caixa única
    pelo primeiro passo de quem não sabe e sobe."""
    d, escadas = _dominio("kc_07"), _escadas("kc_07")
    c = _sessao("kc_07", "crente_aprende", "direto", "rapido")
    primeira = next(e.dados for e in c.eventos if e.tipo == "prova_apresentada")
    assert (primeira["no"], primeira["crenca"]) == (
        "B1", "string_literal_is_array")

    t = trilha.inicia(d, escadas, "s-kc07")
    t = trilha.avanca(d, escadas, t.estado,
                      trilha.Entrada(acao="comecar", ritmo="completo"))
    t = trilha.avanca(d, escadas, t.estado, trilha.Entrada(acao="nao_sei"))
    assert t.tela.dados["degrau"] == "esc_kc07_B1_1"
    assert t.tela.dados["pede_certeza"] is True
    passo, g = t.estado.passo, escadas["B1"].degraus[0]
    v = g.versoes[passo.versao]
    erro = next(x for x in v.erros if x.crenca)
    ordem = trilha_escada.ordem_das_pecas(t.estado.semente, g.id, passo.versao,
                                          g.forma, len(v.pecas))
    r = trilha.avanca(d, escadas, t.estado, trilha.Entrada(
        acao="responder", confianca="tenho certeza",
        pecas=tuple(ordem.index(i) for i in erro.exata)))
    assert r.tela.tipo == "voce_disse"
    assert r.estado.premissa("B1").crenca == "array_confused_with_cell"
    assert r.tela.dados["programa"] == escadas["B1"].prova(
        "array_confused_with_cell").programa


def test_no_kc_07_ninguem_digita_tamanho_que_muda_de_maquina():
    """O tamanho de um int e o de um ponteiro mudam de máquina para
    máquina. Passo de `digitar` só mede array de char, em que o número é
    o de caixas, ou divide o conjunto por uma caixa. O tamanho de um
    ponteiro só aparece em prova, e a nota de ambiente diz que é desta
    máquina."""
    com_sizeof = 0
    for e, g, k, v in _versoes("kc_07"):
        if g.forma == "digitar" and "sizeof" in v.mostra:
            com_sizeof += 1
            medidos = re.findall(r"sizeof (\w+)", v.mostra)
            assert "/ sizeof" in v.mostra or all(
                re.search(r"char %s\[" % m, v.mostra) for m in medidos), g.id
    assert com_sizeof >= 6
    provas = [p for e in _escadas("kc_07").values() for p in e.provas
              if "sizeof" in p.programa]
    assert len(provas) == 3
    for p in provas:
        assert "nesta máquina" in p.ambiente, p.crenca
        # O número que NÃO é o do ponteiro nunca coincide com ele.
        assert not {"4"} & set(p.espera.split()), p.crenca
        assert p.espera.split().count("8") == 1, p.crenca


def test_o_kc_07_diz_as_palavras_que_as_questoes_dele_usam():
    """"Item", "expressão", "terminador" e "tipos" estão nas questões de
    marcar; cada uma é dita num passo guiado. E o sizeof, que quatro
    premissas usam, é apresentado na primeira."""
    escadas = _escadas("kc_07")
    dito = " ".join(f for e in escadas.values() for g in e.degraus
                    for f in g.frases)
    for palavra in ("item", "expressão", "terminador", "tipos diferentes"):
        assert palavra in dito, palavra
    apresenta = [g.id for g in escadas["B1"].degraus
                 if g.guiado and any("sizeof" in f for f in g.frases)]
    assert apresenta == ["esc_kc07_B1_3"]


def test_no_kc_01_ficam_fora_cinco_e_toda_premissa_abre_com_codigo():
    """O banco do kc_01 não foi mexido. É o tópico em que a escada mais
    acompanha o banco: ensina `return`, `malloc`, `free` e a função em
    várias linhas, e só cinco das 30 questões ficam fora."""
    fora, quantas, abre = _selecao("kc_01")
    assert fora == {
        "B1": ("ciu_kc01_t03",), "B2": ("ciu_kc01_t06",),
        "B3": ("ciu_kc01_t08",), "I1": ("ciu_kc01_t11",),
        "I2": ("ciu_kc01_t15",),
    }
    assert quantas == {"B1": 5, "B2": 5, "B3": 5, "I1": 5, "I2": 5}
    assert abre == {
        "B1": "ciu_kc01_002", "B2": "ciu_kc01_005", "B3": "ciu_kc01_008",
        "I1": "ciu_kc01_011", "I2": "ciu_kc01_014"}
    d = _dominio("kc_01")
    por_id = {a.id: a for a in d.atividades}
    assert all(por_id[i].codigo for i in abre.values())
    # O que escada nenhuma ensinou até aqui: o +=, a multiplicação (que
    # neste banco só aparece em `100 * sizeof(int)`) e variável global.
    ruim = re.compile(r"\+=|\d \* sizeof")

    def fora_da_regua(i):
        a = por_id[i]
        return (bool(ruim.search(a.codigo or ""))
                or "variável global" in a.enunciado)

    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_01", no):
            assert not fora_da_regua(i), i
    assert all(fora_da_regua(i) for ids in fora.values() for i in ids)


def test_o_kc_01_apresenta_o_que_o_banco_dele_usa():
    """`return`, a função em várias linhas, `malloc`, `free`, pilha e
    monte: cada um é apresentado num passo guiado. Sete questões servidas
    trazem a função em várias linhas, que a escada não mostrava."""
    d, escadas = _dominio("kc_01"), _escadas("kc_01")
    por_id = {a.id: a for a in d.atividades}
    varias = re.compile(r"\)\s*\{[ \t]*\n")
    assert {i for no in d.ordem for i in _servidas_pela_trilha("kc_01", no)
            if varias.search(por_id[i].codigo or "")} == {
        "ciu_kc01_005", "ciu_kc01_006", "ciu_kc01_t05", "ciu_kc01_008",
        "ciu_kc01_009", "ciu_kc01_t12", "ciu_kc01_014"}

    def apresenta(no, trecho):
        """O primeiro passo guiado da premissa cujas frases dizem o trecho."""
        return next(g.id for g in escadas[no].degraus
                    if g.guiado and any(trecho in f for f in g.frases))

    assert apresenta("B2", "return") == "esc_kc01_B2_1"
    assert apresenta("B2", "(void)") == "esc_kc01_B2_2"
    assert apresenta("B2", "várias linhas") == "esc_kc01_B2_3"
    assert apresenta("B3", "malloc(sizeof(int))") == "esc_kc01_B3_1"
    assert apresenta("B3", "free(p);") == "esc_kc01_B3_2"
    assert apresenta("I2", "pilha") == "esc_kc01_I2_1"
    assert apresenta("I2", "monte") == "esc_kc01_I2_1"
    # E o passo que diz "várias linhas" MOSTRA uma, conferida pelo
    # compilador: a função de fora do `main`, linha por linha.
    g = next(g for g in escadas["B2"].degraus if g.id == "esc_kc01_B2_3")
    assert g.codigo and all(varias.search(v.mostra) for v in g.versoes)


def test_a_prova_do_b1_do_kc_01_diz_o_que_ela_nao_mostra():
    """A premissa é sobre OUTRO programa, e de dentro de um não se vê
    outro — o grafo do tópico já dizia. A prova mostra a consequência (o
    C não garante o que há onde esta execução não escreveu), e a nota de
    ambiente diz o limite com todas as letras."""
    p = _escadas("kc_01")["B1"].prova("memoria_e_do_computador")
    assert p.reclama == "'nota' is used uninitialized"
    assert "programa nenhum mostra sozinho" in p.ambiente


def test_a_prova_do_vazamento_tem_a_funcao_que_devolve_e_a_que_esquece():
    """O que desmente "o sistema recolhe sozinho" é o compilador apontar o
    bloco que vazou — e só ele: no mesmo trecho, da função que chama free
    ele não reclama. Isso pede o analisador de fluxo, e a nota diz."""
    p = _escadas("kc_01")["B3"].prova("system_frees_auto")
    assert p.reclama == "leak of 'p'" and p.avisos == ("-fanalyzer",)
    assert "-fanalyzer" in p.ambiente
    funcoes = [x for x in p.programa.split("\n") if "malloc" in x]
    assert len(funcoes) == 2
    assert sum(1 for x in funcoes if "free(p)" in x) == 1


def _onde_se_apresenta(topico, no, trecho):
    """O primeiro passo guiado da premissa cujas frases dizem o trecho."""
    return next(g.id for g in _escadas(topico)[no].degraus
                if g.guiado and any(trecho in f for f in g.frases))


def test_no_kc_08_ficam_fora_nove_e_toda_premissa_abre_com_codigo():
    """O banco do kc_08 não foi mexido. Ficam fora as nove questões que
    usam laço, `+=`, `strlen` e `strcpy`, `%s`, a conversão para
    `(void *)`, o `int main` e o `return` solto no trecho."""
    fora, quantas, abre = _selecao("kc_08")
    assert fora == {
        "B1": ("ciu_kc08_t02",),
        "B2": ("ciu_kc08_006", "ciu_kc08_t06"),
        "B3": ("ciu_kc08_008", "ciu_kc08_t09"),
        "I2": ("ciu_kc08_t14", "ciu_kc08_t15"),
        "I3": ("ciu_kc08_017", "ciu_kc08_t17"),
    }
    assert quantas == {"B1": 5, "B2": 4, "B3": 4, "I1": 6, "I2": 4, "I3": 4}
    assert abre == {
        "B1": "ciu_kc08_002", "B2": "ciu_kc08_005", "B3": "ciu_kc08_009",
        "I1": "ciu_kc08_011", "I2": "ciu_kc08_014", "I3": "ciu_kc08_018"}
    d = _dominio("kc_08")
    por_id = {a.id: a for a in d.atividades}
    assert all(por_id[i].codigo for i in abre.values())
    # O `return` que fica fora é o solto no trecho (`return;`, `return 1;`):
    # o que devolve um valor de dentro da função o kc_01 ensinou.
    ruim = re.compile(r"\b(for|strlen|strcpy|main)\b|\+=|%s|\(void \*\)"
                      r"|\breturn\s*(1\s*)?;")
    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_08", no):
            assert not ruim.search(por_id[i].codigo or ""), i
    assert all(ruim.search(por_id[i].codigo or "")
               for ids in fora.values() for i in ids)


def test_o_kc_08_apresenta_o_byte_a_multiplicacao_e_o_calloc():
    """O banco fala em bytes desde a primeira questão, multiplica por
    sizeof(int) e cita o calloc. Cada coisa é dita num passo guiado."""
    assert _onde_se_apresenta("kc_08", "B1", "byte") == "esc_kc08_B1_1"
    assert _onde_se_apresenta("kc_08", "B1", "sinal de vezes") == "esc_kc08_B1_2"
    assert _onde_se_apresenta("kc_08", "B3", "calloc") == "esc_kc08_B3_3"
    assert _onde_se_apresenta("kc_08", "I2", "NULL") == "esc_kc08_I2_1"


def test_no_kc_08_ninguem_digita_o_tamanho_de_um_int():
    """Quanto vale sizeof(int) muda de máquina para máquina. Os passos de
    `digitar` usam o bloco — escrevem e leem valores — e nenhum imprime
    um tamanho."""
    digitar = [v for e, g, k, v in _versoes("kc_08") if g.forma == "digitar"]
    assert len(digitar) >= 16
    for v in digitar:
        assert "%zu" not in v.mostra, v.mostra


def test_tres_provas_do_kc_08_pedem_o_analisador_e_a_nota_diz():
    """O tamanho que não fecha, a escrita sem conferir o NULL e o bloco
    que vaza são coisas que o gcc só aponta seguindo o caminho do
    programa. As outras três provas são avisos e erros comuns."""
    provas = {p.crenca: p for e in _escadas("kc_08").values() for p in e.provas}
    com = {c for c, p in provas.items() if p.avisos == ("-fanalyzer",)}
    assert com == {"malloc_conta_elementos", "malloc_always_succeeds",
                   "system_frees_auto"}
    assert all("-fanalyzer" in provas[c].ambiente for c in com)
    # Cinco das seis são o que o compilador diz; a outra é uma saída.
    assert [c for c, p in provas.items() if p.espera] == ["pointer_is_data"]
    # A crença do I3 é a do B3 do kc_01, e a evidência é a mesma — o
    # bloco que vaza. O trecho não é.
    do_kc_01 = _escadas("kc_01")["B3"].prova("system_frees_auto")
    assert provas["system_frees_auto"].programa != do_kc_01.programa


def test_no_kc_09_ficam_fora_sete_e_toda_premissa_abre_com_codigo():
    """O banco do kc_09 não foi mexido, e o tópico não apresenta construto
    novo. Ficam fora as sete questões com ponteiro para ponteiro (que é o
    tópico seguinte), `struct` e variável global."""
    fora, quantas, abre = _selecao("kc_09")
    assert fora == {
        "B2": ("ciu_kc09_006", "ciu_kc09_t06"),
        "B3": ("ciu_kc09_009",),
        "B4": ("ciu_kc09_t12",),
        "I1": ("ciu_kc09_t15",),
        "I3": ("ciu_kc09_021", "ciu_kc09_t21"),
    }
    assert quantas == {"B1": 6, "B2": 4, "B3": 5, "B4": 5,
                       "I1": 5, "I2": 6, "I3": 4, "I4": 6}
    assert abre == {
        "B1": "ciu_kc09_002", "B2": "ciu_kc09_005", "B3": "ciu_kc09_008",
        "B4": "ciu_kc09_011", "I1": "ciu_kc09_014", "I2": "ciu_kc09_017",
        "I3": "ciu_kc09_020", "I4": "ciu_kc09_023"}
    d = _dominio("kc_09")
    por_id = {a.id: a for a in d.atividades}
    assert all(por_id[i].codigo for i in abre.values())
    ruim = re.compile(r"\*\*|\bstruct\b")

    def fora_da_regua(i):
        codigo = por_id[i].codigo or ""
        return bool(ruim.search(codigo)) or _tem_global(codigo)

    for no in d.ordem:
        for i in _servidas_pela_trilha("kc_09", no):
            assert not fora_da_regua(i), i
    assert all(fora_da_regua(i) for ids in fora.values() for i in ids)


def test_as_oito_provas_do_kc_09_e_o_limite_da_comparacao():
    """Oito premissas, oito crenças, oito provas. Três são o que o
    compilador diz. As duas que imprimem p == NULL depois do free dizem,
    na nota de ambiente, que o padrão do C não garante essa comparação —
    que é o que a última premissa do tópico ensina."""
    escadas = _escadas("kc_09")
    provas = {p.crenca: p for e in escadas.values() for p in e.provas}
    assert len(provas) == 8
    assert {c for c, p in provas.items() if p.reclama} == {
        "pointer_knows_block_size", "heap_persists", "double_free_is_safe"}
    assert provas["double_free_is_safe"].avisos == ("-fanalyzer",)
    for crenca in ("free_nullifies", "null_after_free_redundant"):
        p = provas[crenca]
        assert "== NULL" in p.programa and "não garante" in p.ambiente, crenca
    # E um passo guiado do I4 diz que aquelas comparações valem nesta
    # máquina, para a pessoa não sair achando que pode contar com elas.
    assert _onde_se_apresenta("kc_09", "I4", "nesta máquina") == "esc_kc09_I4_3"
    # A prova de "a função recebe o original" não usa p depois do free:
    # a função só escreve NULL na cópia.
    assert "free(x)" not in provas["function_gets_original"].programa


def test_o_kc_09_diz_pendente_e_o_free_de_null_e_separa_as_ideias_vizinhas():
    """Entra uma palavra, "pendente", e um fato, free(NULL) não faz nada.
    E o I1, o I2 e o I3, que ficam muito perto um do outro, têm cada um o
    seu passo de prática com outro nome — outra ideia."""
    assert _onde_se_apresenta("kc_09", "I2", "pendente") == "esc_kc09_I2_1"
    assert _onde_se_apresenta("kc_09", "I4", "free(NULL)") == "esc_kc09_I4_2"
    escadas = _escadas("kc_09")
    nomes = [escadas[no].pratica[0].nome for no in _dominio("kc_09").ordem]
    assert len(set(nomes)) == 8
    assert [escadas[no].pratica[0].nome for no in ("I1", "I2", "I3")] == [
        "free não muda o valor de p",
        "Depois do free, p continua existindo",
        "Escrever NULL depois do free"]


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
