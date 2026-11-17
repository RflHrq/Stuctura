"""A prova da trilha: em código de iniciante, e com a previsão antes.

A primeira fatia mostrava, na tela da máquina, a demonstração do grafo —
um programa escrito para o examinador, com `#include`, `main` e um
`puts(cond ? "..." : "FALHOU")`. Quem acabou de aprender a declarar uma
variável não lê aquilo, e a tela que devia PROVAR virava a mais difícil
da sessão (docs/trilha.md, 7).

A prova passa a morar na escada, ao lado dos degraus, escrita para a
mesma pessoa: o trecho que um iniciante escreveria, a pergunta que faz a
pessoa se comprometer ANTES de ver, e o que a máquina respondeu. Ela
responde a UMA crença, e diz qual alternativa da previsão é o que a
crença espera — o registro passa a saber se a pessoa previu como quem
acredita.

O compilador confere a prova como confere os degraus, antes de ela
chegar a alguém: o que ela diz que o programa imprime, ele imprime; o
que ela diz que o compilador reclama, ele reclama. Programa que só é
compilado nunca é executado.

A demonstração do grafo continua sendo a RESERVA: tópico cuja escada
ainda não tem prova própria mostra a do grafo, como antes.
"""

from __future__ import annotations

import copy
import pathlib
import subprocess
import sys
from dataclasses import replace

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import confere_escada  # noqa: E402
import oraculo  # noqa: E402
from trilha_alunos import PERSONAS, caminha  # noqa: E402

from mvp import motor, trilha, trilha_escada  # noqa: E402
from mvp.dominio import carrega  # noqa: E402
from mvp.test_trilha import _ate_a_abertura, _crenca_de, _marca  # noqa: E402
from mvp.test_trilha_escada import _escreve, _valida  # noqa: E402

D = carrega(topico="kc_00")
ESC = trilha_escada.le(RAIZ / "mvp" / "dominio" / "escada_kc00.yaml", D)

tem_gcc = pytest.mark.skipif(not oraculo.GCC.exists(),
                             reason="sem compilador em %s" % oraculo.GCC)


def _prova_que_imprime() -> dict:
    return {
        "crenca": "type_is_a_hint",
        "programa": "int nota;\n\nnota = 7;\nnota = 9;\nprintf(\"%d\\n\", nota);\n",
        "espera": "9",
        "previsao": {"pergunta": "O que este trecho imprime?",
                     "opcoes": ["7", "9", "7 e 9"], "real": 1, "crenca": 2},
        "afirma": "Só o 9 aparece: o valor novo entrou no lugar do antigo.",
    }


def _prova_que_reclama() -> dict:
    return {
        "crenca": "type_is_a_hint",
        "programa": "int nota;\n\n7 = nota;\n",
        "reclama": "lvalue required as left operand of assignment",
        "ambiente": "Mensagem do gcc 16.2.",
        "previsao": {"pergunta": "O compilador reclama da última linha?",
                     "opcoes": ["Sim", "Não: é o mesmo que nota = 7;"],
                     "real": 0, "crenca": 1},
        "afirma": "À esquerda do sinal de igual fica quem recebe o valor.",
    }


def _com_prova(*provas) -> dict:
    bloco = _valida()
    bloco["provas"] = [copy.deepcopy(p) for p in provas]
    return bloco


def _le(tmp_path, bloco):
    return trilha_escada.le(_escreve(tmp_path, {"B1": bloco}), D)


# --------------------------------------------------------------------------
# A leitura
# --------------------------------------------------------------------------

def test_a_prova_da_escada_carrega(tmp_path):
    e = _le(tmp_path, _com_prova(_prova_que_reclama()))["B1"]
    assert len(e.provas) == 1
    p = e.prova("type_is_a_hint")
    assert p is e.provas[0]
    assert p.programa.startswith("int nota;") and p.espera == ""
    assert p.reclama == "lvalue required as left operand of assignment"
    assert p.ambiente == "Mensagem do gcc 16.2."
    assert p.afirma.startswith("À esquerda")
    assert p.previsao.pergunta == "O compilador reclama da última linha?"
    assert p.previsao.opcoes == ("Sim", "Não: é o mesmo que nota = 7;")
    assert (p.previsao.real, p.previsao.crenca) == (0, 1)
    assert e.prova("no_value_no_memory") is None


def test_escada_sem_prova_continua_valida(tmp_path):
    e = _le(tmp_path, _valida())["B1"]
    assert e.provas == () and e.prova("type_is_a_hint") is None


def _muda(campo, valor):
    def estraga(p):
        p[campo] = valor
    return estraga


def _muda_previsao(campo, valor):
    def estraga(p):
        p["previsao"][campo] = valor
    return estraga


@pytest.mark.parametrize("estraga, diz", [
    (_muda("crenca", "nao_existe"), "crença desconhecida"),
    # A crença é do tópico, mas nega OUTRA premissa: a prova dela mora lá.
    (_muda("crenca", "no_value_no_memory"), "nega"),
    (_muda("programa", ""), "sem programa"),
    # O trecho é o que a pessoa lê. O `main` é do conferidor.
    (_muda("programa", "#include <stdio.h>\nint main(void) { return 0; }\n"),
     "só o trecho"),
    (_muda("espera", ""), "`espera` ou `reclama`"),
    (_muda("reclama", "qualquer coisa"), "`espera` ou `reclama`"),
    (_muda("afirma", ""), "sem `afirma`"),
    (_muda("previsao", None), "sem previsão"),
    (_muda_previsao("pergunta", ""), "previsão sem pergunta"),
    (_muda_previsao("opcoes", ["9"]), "ao menos duas"),
    (_muda_previsao("real", 7), "fora da faixa"),
    (_muda_previsao("crenca", 9), "fora da faixa"),
    # Se a crença previsse o que a máquina faz, a prova não a refutaria.
    (_muda_previsao("crenca", 1), "não pode ser a mesma"),
])
def test_prova_malformada_e_recusada_dizendo_por_que(tmp_path, estraga, diz):
    prova = _prova_que_imprime()
    estraga(prova)
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, _com_prova(prova))
    assert any(diz in p for p in erro.value.problemas), erro.value.problemas


def test_duas_provas_para_a_mesma_crenca_sao_recusadas(tmp_path):
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, _com_prova(_prova_que_imprime(), _prova_que_reclama()))
    assert any("mais de uma prova" in p for p in erro.value.problemas)


def test_a_assinatura_muda_com_a_prova(tmp_path):
    sem = _le(tmp_path, _valida())
    com = _le(tmp_path, _com_prova(_prova_que_imprime()))
    outra = _prova_que_imprime()
    outra["afirma"] = "Outra frase."
    com_outra = _le(tmp_path, _com_prova(outra))
    assinaturas = {trilha_escada.assinatura(x) for x in (sem, com, com_outra)}
    assert len(assinaturas) == 3


# --------------------------------------------------------------------------
# O compilador confere
# --------------------------------------------------------------------------

@tem_gcc
def test_o_conferidor_aprova_a_prova_que_imprime_o_que_diz(tmp_path):
    assert confere_escada.confere(_le(tmp_path, _com_prova(_prova_que_imprime()))) == []


@tem_gcc
def test_o_conferidor_acusa_a_prova_que_nao_imprime_o_que_diz(tmp_path):
    prova = _prova_que_imprime()
    prova["espera"] = "7"
    problemas = confere_escada.confere(_le(tmp_path, _com_prova(prova)))
    assert len(problemas) == 1
    assert "B1/prova de type_is_a_hint" in problemas[0]
    assert "não imprime" in problemas[0]


@tem_gcc
def test_o_conferidor_aprova_a_prova_de_que_o_compilador_reclama(tmp_path):
    assert confere_escada.confere(_le(tmp_path, _com_prova(_prova_que_reclama()))) == []


@tem_gcc
def test_o_conferidor_acusa_a_reclamacao_que_o_compilador_nao_faz(tmp_path):
    prova = _prova_que_reclama()
    prova["programa"] = "int nota;\n\nnota = 7;\n"       # nada a reclamar disso
    problemas = confere_escada.confere(_le(tmp_path, _com_prova(prova)))
    assert len(problemas) == 1
    assert "B1/prova de type_is_a_hint" in problemas[0]
    assert "não reclama" in problemas[0]


@tem_gcc
def test_a_prova_que_so_reclama_nunca_e_executada(tmp_path, monkeypatch):
    """Ler variável sem valor é o que o tópico ensina a não fazer. A prova
    disso é o que o compilador DIZ — e o programa dela não roda."""
    prova = _prova_que_reclama()
    # `pontos`, e não `idade`: os degraus de `digitar` desta escada de
    # teste imprimem `idade`, com valor, e esses rodam de verdade.
    prova["programa"] = "int pontos;\n\nprintf(\"%d\\n\", pontos);\n"
    prova["reclama"] = "'pontos' is used uninitialized"
    escadas = _le(tmp_path, _com_prova(prova))

    rodados = []
    de_verdade = oraculo.roda

    def espia(programa, *a, **k):
        rodados.append(programa)
        return de_verdade(programa, *a, **k)

    monkeypatch.setattr(oraculo, "roda", espia)
    assert confere_escada.confere(escadas) == []
    assert rodados                                   # os de `digitar` rodam
    assert not any("pontos" in p for p in rodados)


def test_a_leitura_traz_a_prova_na_ordem_em_que_a_pessoa_a_encontra(tmp_path):
    texto = confere_escada.leitura(D, _le(tmp_path, _com_prova(_prova_que_reclama())))
    crenca = D.crencas["type_is_a_hint"].afirma
    assert "### Se a pessoa disser a crença: a prova" in texto
    trecho = texto[texto.index("### Se a pessoa disser a crença: a prova"):]
    ordem = [trecho.index(x) for x in (
        crenca, "7 = nota;", "O compilador reclama da última linha?",
        "Não: é o mesmo que nota = 7;", "lvalue required",
        "À esquerda do sinal de igual")]
    assert ordem == sorted(ordem)
    # As duas marcas que quem lê precisa: o que a máquina faz, e o que a
    # crença espera.
    assert "Sim _(é o que a máquina faz)_" in trecho
    assert "Não: é o mesmo que nota = 7; _(é o que a crença espera)_" in trecho


# --------------------------------------------------------------------------
# O motor
# --------------------------------------------------------------------------

def _prova_no_b2(dados) -> dict:
    """O arquivo da escada do kc_00, com o B2 levando a prova de `dados`.

    A prova é posta no arquivo e LIDA: passa pela mesma validação de
    qualquer outra, com a crença que nega o B2.
    """
    import yaml
    caminho = RAIZ / "mvp" / "dominio" / "escada_kc00.yaml"
    tudo = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    tudo["B2"]["provas"] = [dict(dados, crenca="no_value_no_memory")]
    return tudo


def _escadas_com(tmp_path, dados):
    return trilha_escada.le(_escreve(tmp_path, _prova_no_b2(dados)), D)


def _sem_provas(escadas):
    return {no: replace(e, provas=()) for no, e in escadas.items()}


def _voce_disse(escadas, no="B2"):
    t = _ate_a_abertura(no)
    t = trilha.avanca(D, escadas, t.estado,
                      _marca(t.estado, crenca=_crenca_de(no)))
    assert (t.tela.tipo, t.tela.dados["premissa"]) == ("voce_disse", no)
    return t


def test_a_prova_da_escada_vem_antes_da_do_grafo(tmp_path):
    escadas = _escadas_com(tmp_path, _prova_que_reclama())
    prova = escadas["B2"].prova("no_value_no_memory")
    t = _voce_disse(escadas)
    assert t.tela.dados["crenca"] == D.crencas["no_value_no_memory"].afirma
    assert t.tela.dados["programa"] == prova.programa
    assert t.tela.dados["previsao"] == {
        "pergunta": "O compilador reclama da última linha?",
        "opcoes": ["Sim", "Não: é o mesmo que nota = 7;"]}

    m = trilha.avanca(D, escadas, t.estado,
                      trilha.Entrada(acao="responder", escolha=0)).tela
    assert m.tipo == "maquina" and m.dados["tem_prova"] is True
    assert m.dados["programa"] == prova.programa
    assert "#include" not in m.dados["programa"]
    assert m.dados["avisa"] == prova.reclama and m.dados["espera"] == ""
    assert m.dados["nao_compila"] is False
    assert m.dados["ambiente"] == "Mensagem do gcc 16.2."
    assert m.dados["afirma"] == prova.afirma
    assert m.dados["premissa_texto"] == D.nos["B2"].simples


def test_a_prova_que_imprime_mostra_a_saida(tmp_path):
    escadas = _escadas_com(tmp_path, _prova_que_imprime())
    t = _voce_disse(escadas)
    m = trilha.avanca(D, escadas, t.estado,
                      trilha.Entrada(acao="responder", escolha=1)).tela
    assert m.dados["espera"] == "9" and m.dados["avisa"] == ""


def test_a_previsao_da_escada_e_obrigatoria(tmp_path):
    escadas = _escadas_com(tmp_path, _prova_que_imprime())
    t = _voce_disse(escadas)
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, escadas, t.estado, trilha.Entrada(acao="continuar"))
    with pytest.raises(trilha.EntradaInvalida):
        trilha.avanca(D, escadas, t.estado,
                      trilha.Entrada(acao="responder", escolha=3))


@pytest.mark.parametrize("escolha, texto, certa, como_a_crenca", [
    (1, "9", True, False),
    (2, "7 e 9", False, True),
    (0, "7", False, False),
])
def test_a_previsao_registra_se_acertou_e_se_foi_a_da_crenca(
        tmp_path, escolha, texto, certa, como_a_crenca):
    escadas = _escadas_com(tmp_path, _prova_que_imprime())
    t = _voce_disse(escadas)
    m = trilha.avanca(D, escadas, t.estado,
                      trilha.Entrada(acao="responder", escolha=escolha, ms=1200))
    registro = next(e.dados for e in m.eventos
                    if e.tipo == "previsao_registrada")
    assert registro == {"no": "B2", "previu": texto, "certa": certa,
                        "como_a_crenca": como_a_crenca, "ms": 1200}
    assert m.tela.dados["previu"] == texto
    assert m.tela.dados["previu_certo"] is certa


def test_a_previsao_repetida_nao_pula_a_tela_da_maquina(tmp_path):
    """O mesmo que o ramo já guardava para o "continuar": o pedido diz de
    que tela é, e a previsão reenviada não vale para a tela seguinte."""
    escadas = _escadas_com(tmp_path, _prova_que_imprime())
    t = _voce_disse(escadas)
    previsao = trilha.Entrada(acao="responder", escolha=1, passo=t.estado.n)
    m = trilha.avanca(D, escadas, t.estado, previsao)
    assert m.tela.tipo == "maquina"
    with pytest.raises(trilha.EntradaVelha):
        trilha.avanca(D, escadas, m.estado, previsao)


def test_sem_prova_na_escada_vale_a_do_grafo():
    """A reserva: tópico cuja escada ainda não tem prova própria."""
    escadas = _sem_provas(ESC)
    t = _voce_disse(escadas)
    do_grafo = motor._prova(D, "B2")[0]
    assert t.tela.dados["programa"] == do_grafo["programa"]
    assert t.tela.dados["previsao"] == {
        "pergunta": "Este programa compila?", "opcoes": ["Sim", "Não"]}
    m = trilha.avanca(D, escadas, t.estado,
                      trilha.Entrada(acao="responder", escolha=1))
    assert m.tela.dados["nao_compila"] is True
    assert m.tela.dados["previu"] == "Não"
    # O programa não compila, e "Não" é a previsão certa.
    assert m.tela.dados["previu_certo"] is True
    registro = next(e.dados for e in m.eventos
                    if e.tipo == "previsao_registrada")
    assert registro["certa"] is True and registro["como_a_crenca"] is False
    errou = trilha.avanca(D, escadas, t.estado,
                          trilha.Entrada(acao="responder", escolha=0))
    assert errou.tela.dados["previu_certo"] is False


def test_sem_previsao_a_tela_da_maquina_nao_julga_previsao_nenhuma(monkeypatch):
    monkeypatch.setattr(trilha, "provas_exibiveis", lambda d, no: [])
    escadas = _sem_provas(ESC)
    t = _voce_disse(escadas)
    m = trilha.avanca(D, escadas, t.estado, trilha.Entrada(acao="continuar"))
    assert m.tela.dados["previu"] is None
    assert m.tela.dados["previu_certo"] is None


# --------------------------------------------------------------------------
# O conteúdo do kc_00
# --------------------------------------------------------------------------

def test_toda_crenca_do_kc_00_tem_prova_na_escada():
    for c in D.crencas.values():
        assert ESC[c.nega].prova(c.id) is not None, c.id


def test_as_provas_do_kc_00_usam_o_cenario_da_escada():
    """Os mesmos nomes dos degraus: a prova não apresenta variável nova."""
    import re
    nomes = {"idade", "nota", "turma", "ano", "pontos", "inicial"}
    for e in ESC.values():
        for p in e.provas:
            declaradas = set(re.findall(r"\b(?:int|char)\s+(\w+)", p.programa))
            assert declaradas and declaradas <= nomes, (p.crenca, declaradas)


def test_no_kc_00_a_previsao_nao_e_sempre_na_mesma_posicao():
    """Se a resposta da máquina fosse sempre a primeira alternativa, a
    posição ensinaria a prever."""
    posicoes = {p.previsao.real for e in ESC.values() for p in e.provas}
    assert len(posicoes) >= 2


@tem_gcc
def test_o_compilador_confirma_as_provas_do_kc_00():
    assert confere_escada.confere(ESC) == []


def test_quem_diz_cada_crenca_do_kc_00_ve_a_prova_de_iniciante():
    c = caminha(D, ESC, "crente_aprende")
    maquinas = [t for t in c.telas if t.tipo == "maquina"]
    assert [t.dados["premissa"] for t in maquinas] == list(D.ordem)
    for t in maquinas:
        prova = ESC[t.dados["premissa"]].prova(_crenca_de(t.dados["premissa"]))
        assert t.dados["programa"] == prova.programa
        assert "main" not in t.dados["programa"]
        assert t.dados["previu"] is not None


@pytest.mark.parametrize("persona, certa", [
    ("sabe", True), ("crente_aprende", False), ("crente_teimoso", False),
])
def test_o_aluno_simulado_preve_como_a_persona(persona, certa):
    """Quem acredita prevê o que a crença espera — é o que faz da previsão
    um dado, e não um enfeite."""
    t = _voce_disse(ESC, "B4")
    import trilha_alunos
    entrada = trilha_alunos.responde(D, ESC, t.tela, persona, t.estado)
    prova = ESC["B4"].prova("variable_remembers")
    esperada = prova.previsao.real if certa else prova.previsao.crenca
    assert (entrada.acao, entrada.escolha) == ("responder", esperada)


def test_todas_as_personas_ainda_chegam_ao_mapa():
    for persona in PERSONAS:
        assert caminha(D, ESC, persona).telas[-1].tipo == "mapa", persona


# --------------------------------------------------------------------------
# O que o kc_02 pediu ao conferidor: função e endereço
# --------------------------------------------------------------------------

def test_a_linha_de_funcao_fica_fora_do_main():
    """Um trecho pode trazer uma função de uma linha, acima do resto. Em C
    ela não pode ficar dentro do `main` — o gcc aceita por extensão, e o
    conteúdo não ensina extensão."""
    p = confere_escada.programa_de(
        "void zera(int *q) { *q = 0; }\n\nint idade;\n\nidade = 15;",
        "zera(&idade);")
    assert p.index("void zera(int *q) { *q = 0; }") < p.index("int main(void)")
    assert p.index("int main(void)") < p.index("int idade;") < p.index(
        "zera(&idade);") < p.index("return 0;")


def test_a_chamada_de_funcao_continua_dentro_do_main():
    p = confere_escada.programa_de("int idade;", "zera(&idade);")
    assert p.index("int main(void)") < p.index("zera(&idade);")


@tem_gcc
def test_o_trecho_com_funcao_compila_como_c_padrao():
    programa = confere_escada.programa_de(
        "void zera(int *q) { *q = 0; }\n\nint idade;\n\nidade = 15;",
        "zera(&idade);\nprintf(\"%d\\n\", idade);")
    assert oraculo.roda(programa, "0") == (True, "0")


def _prova_de_enderecos(espera) -> dict:
    return {
        "crenca": "type_is_a_hint",
        "programa": ("int idade;\nint *p;\n\np = &idade;\n"
                     "printf(\"%p\\n\", (void *)&idade);\n"
                     "printf(\"%p\\n\", (void *)&p);\n"),
        "espera": espera,
        "ambiente": "Os números dos lugares mudam de máquina para máquina.",
        "previsao": {"pergunta": "O que as duas linhas mostram?",
                     "opcoes": ["Dois endereços diferentes",
                                "O mesmo endereço, duas vezes"],
                     "real": 0, "crenca": 1},
        "afirma": "Saíram dois endereços, e diferentes.",
    }


@tem_gcc
def test_endereco_de_exemplo_confere_a_forma_e_nao_o_numero(tmp_path):
    """O número de um lugar muda a cada máquina. A prova mostra números
    de exemplo, e o que o compilador confere é a FORMA: quantas linhas,
    e quais endereços são iguais entre si."""
    diferentes = _le(tmp_path, _com_prova(_prova_de_enderecos("0x1000\n0x2A00")))
    assert confere_escada.confere(diferentes) == []


@tem_gcc
def test_endereco_de_exemplo_repetido_exige_o_mesmo_endereco(tmp_path):
    iguais = _le(tmp_path, _com_prova(_prova_de_enderecos("0x1000\n0x1000")))
    problemas = confere_escada.confere(iguais)
    assert len(problemas) == 1 and "não imprime" in problemas[0]


@tem_gcc
def test_endereco_de_exemplo_nao_aceita_saida_de_outra_forma(tmp_path):
    uma_linha = _le(tmp_path, _com_prova(_prova_de_enderecos("0x1000")))
    assert len(confere_escada.confere(uma_linha)) == 1
    com_texto = _prova_de_enderecos("0x1000\n15")
    assert len(confere_escada.confere(_le(tmp_path, _com_prova(com_texto)))) == 1


def test_prova_com_endereco_de_exemplo_tem_de_dizer_que_e_exemplo(tmp_path):
    """A tela mostra `0x1000` debaixo de "a máquina respondeu". Sem a nota
    de ambiente, isso seria afirmar um número que máquina nenhuma deu."""
    prova = _prova_de_enderecos("0x1000\n0x2A00")
    prova["ambiente"] = ""
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, _com_prova(prova))
    assert any("endereço de exemplo" in p for p in erro.value.problemas)


# --------------------------------------------------------------------------
# O tempo que o conferidor espera
# --------------------------------------------------------------------------

@tem_gcc
@pytest.mark.parametrize("prova", [
    _prova_que_imprime,                                  # oraculo.roda
    _prova_que_reclama,                                  # diz
    lambda: _prova_de_enderecos("0x1000\n0x2A00"),       # _saida
], ids=["imprime", "reclama", "enderecos"])
def test_o_conferidor_espera_mais_que_o_oraculo_e_nao_para_sempre(
        tmp_path, monkeypatch, prova):
    """Na suíte inteira, com a máquina carregada, um programa de três
    linhas (`malloc`, `printf`, `free`) chegou a passar dos 10 s do
    oráculo — no kc_01 e no kc_06 —, e o conferidor acusou "não
    terminou". Não era laço: era o Windows olhando o executável novo.

    O conferidor é verificação de autoria, e tem limite próprio, mais
    folgado que o do oráculo. Mas ainda é limite: programa que não para
    continua acusado. Vale para TODO processo que ele abre — compilar,
    só compilar, rodar —, inclusive os que abre pelo `oraculo.roda`.
    """
    bloco = _com_prova(prova())
    # A revisão com saída é o caminho que roda pelo oráculo; os degraus
    # de `digitar` da escada de teste são outro, e os de montar e
    # escolher, o que só compila.
    bloco["revisao"] = {"frases": ["Toda variável tem um nome e um tipo."],
                        "codigo": "int idade;\n\nidade = 20;\n"
                                  "printf(\"%d\\n\", idade);\n",
                        "saida": "20"}
    escadas = _le(tmp_path, bloco)

    tempos = []
    de_verdade = subprocess.run

    def espia(*a, **k):
        tempos.append(k.get("timeout"))
        return de_verdade(*a, **k)

    monkeypatch.setattr(subprocess, "run", espia)
    assert confere_escada.confere(escadas) == []
    assert tempos
    assert all(t is not None and t > oraculo.TEMPO for t in tempos), tempos
    assert set(tempos) == {confere_escada.TEMPO_CONFERE}


# --------------------------------------------------------------------------
# O que o kc_05 pediu ao conferidor: de QUAL linha o compilador reclama
# --------------------------------------------------------------------------

def _prova_de_uma_linha_so(programa, reclama, **mais) -> dict:
    return dict({
        "crenca": "type_is_a_hint",
        "programa": programa,
        "reclama": reclama,
        "ambiente": "Mensagem do gcc 16.2.",
        "previsao": {"pergunta": "De qual linha o compilador reclama?",
                     "opcoes": ["Das duas", "Só da última"],
                     "real": 1, "crenca": 0},
        "afirma": "O compilador reclama de uma linha só.",
    }, **mais)


@tem_gcc
def test_a_reclamacao_tem_de_ser_de_uma_linha_so(tmp_path):
    """A prova diz "o compilador reclama DESTA linha". Se a mesma
    mensagem saísse de duas linhas, a tela estaria dizendo menos do que
    aconteceu — e a pessoa que previu "das duas" teria razão."""
    uma = _prova_de_uma_linha_so(
        "int n;\nint *p;\n\nn = 0;\np = 0;\np = n;\n",
        "makes pointer from integer without a cast")
    assert confere_escada.confere(_le(tmp_path, _com_prova(uma))) == []

    duas = _prova_de_uma_linha_so(
        "int n;\nint *p;\n\nn = 0;\np = n;\np = n;\n",
        "makes pointer from integer without a cast")
    problemas = confere_escada.confere(_le(tmp_path, _com_prova(duas)))
    assert len(problemas) == 1 and "2 linhas" in problemas[0]


@tem_gcc
def test_a_prova_pode_dizer_do_que_o_compilador_nao_reclama(tmp_path):
    """`cala`: o pedaço de mensagem que NÃO pode aparecer. É a metade da
    prova que diz "de p ele não reclama"."""
    programa = "int *p;\nint *q;\nint *r;\n\np = NULL;\nr = p;\nr = q;\n"
    certa = _prova_de_uma_linha_so(
        programa, "'q' is used uninitialized",
        cala="'p' is used uninitialized")
    escadas = _le(tmp_path, _com_prova(certa))
    assert escadas["B1"].provas[0].cala == "'p' is used uninitialized"
    assert confere_escada.confere(escadas) == []

    # Sem o p = NULL; o compilador reclama de p também, e a prova mente.
    mente = _prova_de_uma_linha_so(
        programa.replace("p = NULL;\n", ""), "'q' is used uninitialized",
        cala="'p' is used uninitialized")
    problemas = confere_escada.confere(_le(tmp_path, _com_prova(mente)))
    assert len(problemas) == 1 and "deveria calar" in problemas[0]


@tem_gcc
def test_a_prova_pode_pedir_avisos_a_mais(tmp_path):
    """Há aviso que o gcc só dá olhando o fluxo do programa. `avisos`
    leva as opções; sem elas, a mesma prova não se confirma."""
    programa = "int *p;\n\np = NULL;\nprintf(\"%d\\n\", *p);\n"
    com = _prova_de_uma_linha_so(programa, "null pointer dereference",
                                 avisos="-O2 -Wnull-dereference")
    escadas = _le(tmp_path, _com_prova(com))
    assert escadas["B1"].provas[0].avisos == ("-O2", "-Wnull-dereference")
    assert confere_escada.confere(escadas) == []

    sem = _prova_de_uma_linha_so(programa, "null pointer dereference")
    assert len(confere_escada.confere(_le(tmp_path, _com_prova(sem)))) == 1


@pytest.mark.parametrize("estraga, diz", [
    # Opção de compilador vem do conteúdo, e vira argumento de comando:
    # só passam as da lista.
    (_muda("avisos", "-O2 -o /tmp/x"), "opção de compilador não permitida"),
    (_muda("avisos", "-Werror"), "opção de compilador não permitida"),
    # Sem a nota, a pessoa não saberia que o aviso pede opção a mais.
    (lambda p: p.update(avisos="-O2 -Wnull-dereference", ambiente=""),
     "`ambiente` tem de dizer"),
    # `cala` e `avisos` são do que o compilador DIZ, não de uma saída.
    (lambda p: p.update(cala="qualquer", reclama="", espera="9"),
     "só fazem sentido com `reclama`"),
])
def test_cala_e_avisos_malformados_sao_recusados(tmp_path, estraga, diz):
    prova = _prova_que_reclama()
    estraga(prova)
    with pytest.raises(trilha_escada.EscadaInvalida) as erro:
        _le(tmp_path, _com_prova(prova))
    assert any(diz in p for p in erro.value.problemas), erro.value.problemas


# --------------------------------------------------------------------------
# O que o kc_01 pediu ao conferidor: malloc e free, e o bloco que vaza
# --------------------------------------------------------------------------

# Uma função pede um bloco e termina sem devolver.
VAZA = ("void usa(void) { int *p = malloc(sizeof(int)); "
        "if (p != NULL) *p = 7; }\n\nusa();\n")


@tem_gcc
def test_o_trecho_com_malloc_e_free_compila_e_roda():
    """A escada não mostra `#include`: o conferidor embrulha o trecho. Com
    o kc_01 entram `malloc` e `free`, que moram em <stdlib.h> — sem ele o
    gcc não aceita o trecho, por função que ninguém declarou."""
    programa = confere_escada.programa_de(
        "", "int *p;\n\np = malloc(sizeof(int));\n*p = 7;\n"
            "printf(\"%d\\n\", *p);\nfree(p);\n")
    ok, nota = confere_escada.compila(programa)
    assert ok, nota
    assert confere_escada._saida(programa) == (True, "7")


VARIAS_LINHAS = ("int conta(void) {\n"
                 "    int n = 0;\n"
                 "    n = n + 1;\n"
                 "    return n;\n"
                 "}\n"
                 "\n"
                 "conta();\n"
                 "printf(\"%d\\n\", conta());\n")


def test_a_funcao_de_varias_linhas_tambem_fica_fora_do_main():
    """O banco do kc_01 escreve as funções em várias linhas, que é como
    elas aparecem em qualquer programa. O trecho de um passo pode trazer
    uma assim: da linha que termina em `{` até o `}` sozinho, na margem,
    tudo vai para fora do `main`."""
    p = confere_escada.programa_de("", VARIAS_LINHAS)
    fora, dentro = p.split("int main(void) {")
    for linha in ("int conta(void) {", "    int n = 0;", "    return n;",
                  "\n}\n"):
        assert linha in fora, linha
    assert "conta();" in dentro and "printf(" in dentro
    assert "int n = 0;" not in dentro


def test_chave_de_dentro_do_main_nao_abre_funcao():
    """Só abre função a linha que começa na margem com o tipo e termina em
    `{`. O `if` de uma linha, que a escada já usa, continua onde estava."""
    p = confere_escada.programa_de(
        "", "int *p;\n\np = NULL;\nif (p == NULL) printf(\"%d\\n\", 1);\n")
    assert p.index("int main(void)") < p.index("if (p == NULL)")


def _e_c_padrao(programa: str) -> bool:
    """Função definida dentro do `main` o gcc aceita, por extensão — e por
    isso rodar o programa não diz se ela ficou fora. Com -pedantic-errors
    ele só aceita o que é C padrão."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        (pathlib.Path(tmp) / "o.c").write_text(programa, encoding="utf-8")
        saiu = subprocess.run(
            [str(oraculo.GCC), "-std=c17", "-pedantic-errors",
             "-fsyntax-only", "o.c"],
            capture_output=True, cwd=tmp, timeout=oraculo.TEMPO)
    return saiu.returncode == 0


@tem_gcc
def test_o_trecho_com_funcao_de_varias_linhas_e_c_padrao_e_roda():
    programa = confere_escada.programa_de("", VARIAS_LINHAS)
    assert _e_c_padrao(programa)
    assert oraculo.roda(programa, "1") == (True, "1")
    # A de uma linha, que já ficava fora, continua C padrão.
    assert _e_c_padrao(confere_escada.programa_de(
        "", "int dobro(int n) { return n + n; }\n\n"
            "printf(\"%d\\n\", dobro(4));\n"))


@tem_gcc
def test_o_que_o_compilador_diz_e_lido_como_utf_8():
    """O analisador de fluxo desenha o caminho do programa com caracteres
    que não existem no cp1252. No Windows, ler a saída na codificação da
    máquina quebrava a leitura, e o que o compilador disse se perdia."""
    dito = confere_escada.diz(confere_escada.programa_de("", VAZA),
                              ("-fanalyzer",))
    assert isinstance(dito, str) and "leak of 'p'" in dito


@tem_gcc
def test_a_prova_pode_pedir_o_analisador_de_fluxo(tmp_path):
    """Bloco pedido e nunca devolvido é coisa que o gcc só aponta seguindo
    o caminho do programa (-fanalyzer). A opção entra na lista fechada; sem
    ela, a mesma prova não se confirma."""
    com = _prova_de_uma_linha_so(VAZA, "leak of 'p'", avisos="-fanalyzer")
    escadas = _le(tmp_path, _com_prova(com))
    assert escadas["B1"].provas[0].avisos == ("-fanalyzer",)
    assert confere_escada.confere(escadas) == []

    sem = _prova_de_uma_linha_so(VAZA, "leak of 'p'")
    assert len(confere_escada.confere(_le(tmp_path, _com_prova(sem)))) == 1
