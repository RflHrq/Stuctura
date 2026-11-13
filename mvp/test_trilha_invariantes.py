"""O que vale para TODA sessão da trilha, seja quem for o aluno.

`mvp/test_trilha.py` confere caminho por caminho. Aqui a pergunta é
outra: existe algum jeito de responder que quebre o que a spec promete?
Oito alunos simulados, os dois modos, os dois ritmos e três sementes —
noventa e seis sessões —, e as promessas de docs/trilha.md, seção 8:

  - toda sessão termina, e toda premissa tem resultado;
  - ninguém passa de oito telas numa premissa;
  - nenhuma premissa fecha bem sem resposta certa pela razão certa;
  - a tela só diz "a máquina respondeu" onde há prova;
  - ninguém fica preso num degrau;
  - toda premissa trabalhada é reconferida, e só ela;
  - a mesma sessão, reexecutada, dá as mesmas telas.

O aluno que chuta existe para isso: ele não segue caminho nenhum.
"""

from __future__ import annotations

import functools
import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))
sys.path.insert(0, str(RAIZ.parent / "scripts"))

import trilha_alunos  # noqa: E402
from trilha_alunos import PERSONAS, caminha  # noqa: E402

from mvp import motor, trilha, trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402

D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "dominio" / "escada_kc00.yaml", D)

SEMENTES = ("s1", "s2", "s3")
TODAS = [(p, m, r, s) for p in PERSONAS for m in trilha.MODOS
         for r in trilha.RITMOS for s in SEMENTES]


@functools.lru_cache(maxsize=None)
def _sessao(persona, modo, ritmo, semente):
    return caminha(D, ESC, persona, modo, ritmo, semente)


todas = pytest.mark.parametrize("persona, modo, ritmo, semente", TODAS)


@todas
def test_toda_sessao_termina_e_toda_premissa_tem_resultado(
        persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    assert c.estado.fim and c.telas[-1].tipo == "mapa"
    for no in D.ordem:
        assert c.estado.premissa(no).resultado in trilha.RESULTADOS, no


@todas
def test_ninguem_passa_de_oito_telas_numa_premissa(
        persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    for no in D.ordem:
        assert c.estado.premissa(no).telas <= trilha.TETO_TELAS, no


@todas
def test_a_sessao_inteira_cabe_no_teto(persona, modo, ritmo, semente):
    """Entrada, mapa, e por premissa o teto mais a reconferência.

    `conta` é a conta da spec: a subida inteira da escada vale uma tela,
    e o retorno não conta. O esforço de verdade — cada degrau, cada
    "continuar" — é `toques`, e ele também tem de ter fim.
    """
    c = _sessao(persona, modo, ritmo, semente)
    assert trilha_alunos.conta(c) <= 2 + len(D.ordem) * (trilha.TETO_TELAS + 1)
    assert trilha_alunos.reconferencias(c) <= len(D.ordem)
    por_premissa = 2 * max(len(e.degraus) for e in ESC.values()) + 30
    assert trilha_alunos.toques(c) <= len(D.ordem) * por_premissa


@todas
def test_nenhuma_premissa_fecha_bem_sem_resposta_certa_pela_razao_certa(
        persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    for no in D.ordem:
        if c.estado.premissa(no).resultado == trilha.EM_ABERTO:
            continue
        marcou = [e for e in c.eventos if e.tipo == "episodio_classificado"
                  and e.dados["no"] == no and e.dados["papel"] != "reconferencia"
                  and e.dados["estado"] in (motor.CONFIRMADA, motor.FRAGIL_EP)]
        escreveu = [e for e in c.eventos if e.tipo == "degrau_respondido"
                    and e.dados["no"] == no and e.dados["certa"]
                    and e.dados["papel"] in ("produzir", "treino")]
        assert marcou or escreveu, (no, c.estado.premissa(no).resultado)


@todas
def test_a_certeza_declarada_nao_fecha_premissa_sozinha(
        persona, modo, ritmo, semente):
    """6.14: "já sabia" pede a resposta certa, a razão certa E a certeza."""
    c = _sessao(persona, modo, ritmo, semente)
    for no in D.ordem:
        if c.estado.premissa(no).resultado != trilha.JA_SABIA:
            continue
        firmes = [e for e in c.eventos if e.tipo == "episodio_classificado"
                  and e.dados["no"] == no and e.dados["papel"] == "abertura"
                  and e.dados["estado"] == motor.CONFIRMADA]
        assert firmes, no


@todas
def test_a_maquina_so_respondeu_onde_ha_prova(persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    for t in (t for t in c.telas if t.tipo == "maquina"):
        no = t.dados["premissa"]
        # A prova da escada, para a crença trabalhada naquela premissa; na
        # falta dela, a demonstração do grafo. Fora disso a tela não diz
        # que a máquina respondeu.
        propria = ESC[no].prova(c.estado.premissa(no).crenca)
        do_grafo = motor._prova(D, no)
        assert t.dados["tem_prova"] == bool(propria or do_grafo)
        if propria:
            assert t.dados["programa"] == propria.programa
        elif do_grafo:
            assert t.dados["programa"] == do_grafo[0]["programa"]


@todas
def test_ninguem_fica_preso_num_degrau(persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    assert all(t.dados["tentativa"] <= 2
               for t in c.telas if t.tipo == "degrau")
    for no in D.ordem:
        subidas = [t.dados["indice"] for t in c.telas if t.tipo == "degrau"
                   and t.dados["premissa"] == no
                   and t.dados["papel"] == "subida"]
        assert subidas == sorted(subidas), no
        assert len(subidas) <= 2 * len(ESC[no].degraus), no


@todas
def test_toda_premissa_trabalhada_e_reconferida_e_so_ela(
        persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    reconferidas = [t.dados["premissa"] for t in c.telas
                    if t.dados.get("papel") == "reconferencia"]
    assert len(reconferidas) == len(set(reconferidas))
    for no in D.ordem:
        ep = c.estado.premissa(no)
        assert bool(ep.trabalho) == bool(ep.reconferencia), no
        if no in reconferidas:
            assert ep.reconferencia in (trilha.ASSIMILOU, trilha.NAO_SE_MANTEVE,
                                        trilha.A_IDEIA_VOLTOU)
        elif ep.trabalho:
            assert ep.reconferencia == trilha.SEM_QUESTAO


@todas
def test_cada_premissa_recebe_no_maximo_um_trabalho_de_cada_tipo(
        persona, modo, ritmo, semente):
    c = _sessao(persona, modo, ritmo, semente)
    inicios = [(e.dados["no"], e.dados["trabalho"]) for e in c.eventos
               if e.tipo == "trabalho_iniciado"]
    assert len(inicios) == len(set(inicios))
    provas = [e.dados["no"] for e in c.eventos if e.tipo == "prova_apresentada"]
    assert len(provas) == len(set(provas))


@todas
def test_a_mesma_sessao_reexecutada_da_as_mesmas_telas(
        persona, modo, ritmo, semente):
    a = _sessao(persona, modo, ritmo, semente)
    b = caminha(D, ESC, persona, modo, ritmo, semente)
    assert a.telas == b.telas
    assert [(e.tipo, e.dados) for e in a.eventos] == [
        (e.tipo, e.dados) for e in b.eventos]


def test_a_medida_sai_para_todas_as_personas(capsys):
    """`python scripts/trilha_alunos.py kc_00` é de onde sai a tabela de
    telas da spec. A conta é a da spec, e a tabela traz também os toques."""
    assert trilha_alunos.main(["kc_00"]) == 0
    saida = capsys.readouterr().out
    assert all(p in saida for p in PERSONAS)
    assert "completo" in saida and "rapido" in saida
    assert "direto" in saida and "explique" in saida
    linhas = [l for l in saida.splitlines() if l.startswith("sabe ")]
    assert len(linhas) == 4
    direto_completo = next(l for l in linhas
                           if " direto " in l and " completo " in l).split()
    assert direto_completo[3:6] == ["12", "2", "0"]   # telas, maior, reconferências


def test_a_medida_recusa_topico_sem_escada(capsys):
    # Era o kc_02, até ele ganhar escada em 13/11/2026. O kc_01 é o que
    # está sem; quando ganhar a dele, este teste pede outro tópico.
    assert not (RAIZ / "dominio" / "escada_kc01.yaml").exists()
    assert trilha_alunos.main(["kc_01"]) == 2
    assert "escada" in capsys.readouterr().err


def test_as_sessoes_nao_sao_todas_iguais():
    """As personas servem para alguma coisa: os resultados variam."""
    vistos = {tuple(_sessao(p, "direto", "completo", "s1").estado.premissa(n)
                    .resultado for n in D.ordem) for p in PERSONAS}
    assert len(vistos) >= 5
    todos = {r for p in PERSONAS for m in trilha.MODOS
             for r in (_sessao(p, m, "completo", "s1").estado.premissa(n)
                       .resultado for n in D.ordem)}
    assert todos == set(trilha.RESULTADOS)
