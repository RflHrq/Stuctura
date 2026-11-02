"""A descida interrogativa: a refutação que pergunta em vez de afirmar.

A refutação de hoje AFIRMA as premissas corretas, uma tela por premissa,
e põe a contradição lado a lado no fim. A descida faz o contrário: toma a
crença da pessoa como verdadeira e vai perguntando o que decorre dela,
até a consequência que ela mesma sabe ser falsa.

ISSO INVERTE A POLARIDADE DE TODO O RESTO DO SISTEMA. Em qualquer
atividade daqui a alternativa certa é a verdadeira; num degrau da
descida, a alternativa que faz a cadeia ANDAR é a falsa — é a previsão da
crença. Os testes deste arquivo existem em boa parte para proteger essa
inversão de quem for mexer depois, inclusive eu.

Três saídas, três dados diferentes:

  recua cedo        a crença era rasa — bastou um passo
  recua no fim      a crença era funda, mas fechou pela boca dela
  sustenta até o fim  a cadeia não bastou, e aí entra a evidência

A chave `STRUCTURA_DESCIDA=1` mantém tudo isto desligado por padrão.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp import motor
from mvp.dominio import DominioInvalido, carrega
from mvp.motor import Resposta

RAIZ = Path(__file__).resolve().parent / "dominio"
ARQUIVOS = ("topic_kc07.yaml", "graph_kc07.yaml", "beliefs_kc07.yaml",
            "activities_kc07.yaml", "descidas_kc07.yaml")

CRENCA = "array_is_pointer"      # a única com cadeia escrita, de propósito
ALVO = "I3"                      # o nó que ela nega
COLIDE = "B1"                    # a premissa com que o último degrau colide


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_07")


@pytest.fixture
def ligada(monkeypatch):
    """Liga a descida sem recarregar o módulo.

    Recarregar `mvp.motor` para reler o ambiente quebraria quem já
    importou os nomes dele — foi o que aconteceu com seis testes do
    gerador quando tentei isso no escopo por premissa.
    """
    monkeypatch.setattr(motor, "DESCIDA_LIGADA", True)


# --------------------------------------------------------------------------
# Chegar até lá
# --------------------------------------------------------------------------

def _politica(d, erra_no="I1"):
    """Acerta tudo, e erra UMA vez pela crença que tem cadeia.

    Erra num item de `I1`, e não de `B1`: assim as quatro observáveis já
    fecharam quando a descida começa, e o último degrau pode dizer "você
    confirmou". É também o caso realista — a atribuição cruzada manda a
    crença para `I3`, que é o nó que ela nega, e não para o nó do item.
    """
    pendente = {"erro": False}

    def politica(tela, estado):
        if tela.tipo in ("ensino", "validacao", "refutacao"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="uma frase")
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "razao":
            razoes = estado.pendente.razoes
            if pendente["erro"]:
                pendente["erro"] = False
                i = next((i for i, z in enumerate(razoes)
                          if z.crenca == CRENCA), None)
                if i is not None:
                    return Resposta(escolha=i)
            return Resposta(escolha=next(i for i, z in enumerate(razoes)
                                         if z.correta))
        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        i = next((i for i, o in enumerate(a.opcoes) if o.crenca == CRENCA),
                 None)
        if (a.no == erra_no and i is not None
                and tela.dados["fase"] == motor.DIAGNOSTICO
                and not estado.no(ALVO).crenca):
            pendente["erro"] = True
            return Resposta(escolha=i, confianca="tenho certeza")
        return Resposta(escolha=a.indice_correto, confianca="tenho certeza")

    return politica


def _ate(d, tipo, limite=120, **kw):
    """Roda a sessão de verdade até a primeira tela daquele tipo."""
    pol = _politica(d, **kw)
    t = motor.inicia(d)
    eventos = list(t.eventos)
    for _ in range(limite):
        if t.tela.tipo == tipo:
            return t, eventos
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
        eventos.extend(t.eventos)
    raise AssertionError("não cheguei à tela %r em %d passos" % (tipo, limite))


def _na_descida(d):
    """O primeiro degrau, alcançado pela sessão inteira."""
    return _ate(d, "descida")


def _degrau(d, e, escolha=motor.DECORRE, **kw):
    return motor.avanca(d, e, Resposta(escolha=escolha, **kw))


# --------------------------------------------------------------------------
# A chave
# --------------------------------------------------------------------------

def test_sem_a_chave_a_descida_nao_existe(d):
    """O padrão é o fluxo de hoje, intacto.

    Uma coleta em andamento mede o fluxo de hoje; trocá-lo no meio
    invalidaria a comparação entre participantes.
    """
    assert motor.DESCIDA_LIGADA is False
    t, _ = _ate(d, "validacao")
    assert motor.avanca(d, t.estado, Resposta()).tela.tipo == "refutacao"


def test_com_a_chave_a_crenca_que_tem_cadeia_desce(d, ligada):
    t, _ = _ate(d, "validacao")
    depois = motor.avanca(d, t.estado, Resposta())
    assert depois.tela.tipo == "descida"
    assert depois.estado.fase == motor.DESCIDA
    iniciada = [e for e in depois.eventos if e.tipo == "descida_iniciada"]
    assert iniciada and iniciada[0].dados["crenca"] == CRENCA
    assert iniciada[0].dados["no"] == ALVO
    assert iniciada[0].dados["colide_com"] == COLIDE


def test_a_chave_ligada_nao_mexe_em_crenca_sem_cadeia(d, ligada):
    """Setenta e oito crenças continuam na refutação de sempre.

    É o que torna o protótipo de UMA cadeia possível: ligar a chave não
    muda o comportamento de nenhuma crença que não tenha descida escrita.
    """
    outra = next(c for c in d.crencas if c != CRENCA)
    e = motor.Estado(fase=motor.VALIDACAO, alvo="B2",
                     nos={"B2": motor.EstadoNo(estado=motor.REFUTADO,
                                               crenca=outra)})
    assert motor.avanca(d, e, Resposta()).tela.tipo == "refutacao"


def test_topico_sem_descida_nenhuma_carrega_e_roda(ligada):
    outro = carrega(topico="kc_00")
    assert outro.descidas == {}
    assert outro.descida("declaration_zeroes") is None


# --------------------------------------------------------------------------
# Os degraus
# --------------------------------------------------------------------------

def test_o_degrau_pergunta_e_oferece_as_duas_saidas(d, ligada):
    t, _ = _na_descida(d)
    assert t.tela.texto.strip().endswith("?"), t.tela.texto
    assert len(t.tela.dados["opcoes"]) == 2
    assert t.tela.dados["passo"] == 1
    assert t.tela.dados["total"] == len(d.descida(CRENCA).passos)
    # A crença fica à vista: a cadeia inteira é "se isto for verdade...".
    assert t.tela.dados["crenca"] == d.crencas[CRENCA].afirma


def test_seguir_a_propria_crenca_anda_na_cadeia(d, ligada):
    t, _ = _na_descida(d)
    for passo in range(1, len(d.descida(CRENCA).passos)):
        t = _degrau(d, t.estado, motor.DECORRE, ms=1200)
        assert t.tela.tipo == "descida"
        assert t.tela.dados["passo"] == passo + 1
        passos = [e for e in t.eventos if e.tipo == "descida_passo"]
        assert passos and passos[0].dados["escolha"] == "decorre"
        assert passos[0].dados["profundidade"] == passo


def test_dizer_a_verdade_encerra_a_descida_ali(d, ligada):
    """Insistir depois disto é argumentar com quem já concordou."""
    t, _ = _na_descida(d)
    t = _degrau(d, t.estado, motor.VERDADE)
    assert t.tela.tipo == "descida_fim"
    assert t.estado.fase == motor.FECHO_DESCIDA
    fechou = [e for e in t.eventos if e.tipo == "descida_fechou"]
    assert fechou and fechou[0].dados["profundidade"] == 1
    assert fechou[0].dados["no_fim"] is False
    # O `porque` daquele degrau é o que a tela diz — e é a consequência
    # do que ela ACABOU de responder, não um sermão genérico.
    assert t.tela.texto == d.descida(CRENCA).passos[0].porque


def test_recuar_no_ultimo_degrau_e_outro_dado(d, ligada):
    """Rasa e funda saem com o mesmo texto na tela, e diferentes no log."""
    t, _ = _na_descida(d)
    total = len(d.descida(CRENCA).passos)
    for _ in range(total - 1):
        t = _degrau(d, t.estado, motor.DECORRE)
    t = _degrau(d, t.estado, motor.VERDADE)
    assert t.tela.tipo == "descida_fim"
    fechou = [e for e in t.eventos if e.tipo == "descida_fechou"][0]
    assert fechou.dados["profundidade"] == total
    assert fechou.dados["no_fim"] is True


def test_a_profundidade_e_o_dado_que_a_descida_existe_para_medir(d, ligada):
    """Cada degrau vai para o log com profundidade e total.

    Sem isto a descida seria só mais uma tela: o que ela acrescenta à
    pesquisa é quão longe a pessoa leva a própria crença antes de largá-la.
    """
    t, _ = _na_descida(d)
    t = _degrau(d, t.estado, motor.DECORRE)
    t = _degrau(d, t.estado, motor.VERDADE)
    fechou = [e for e in t.eventos if e.tipo == "descida_fechou"][0]
    assert fechou.dados["profundidade"] == 2
    assert fechou.dados["total"] == len(d.descida(CRENCA).passos)
    assert fechou.dados["crenca"] == CRENCA
    assert fechou.dados["no"] == ALVO


# --------------------------------------------------------------------------
# O último degrau: "você confirmou" só se ela confirmou
# --------------------------------------------------------------------------

def _no_ultimo(d, confirmou=True):
    nos = {ALVO: motor.EstadoNo(estado=motor.REFUTADO, crenca=CRENCA)}
    if confirmou:
        nos[COLIDE] = motor.EstadoNo(estado=motor.CONFIRMADO)
    e = motor.Estado(fase=motor.VALIDACAO, alvo=ALVO, nos=nos)
    t = motor.avanca(d, e, Resposta())
    for _ in range(len(d.descida(CRENCA).passos) - 1):
        t = _degrau(d, t.estado, motor.DECORRE)
    return t


def test_o_ultimo_degrau_so_diz_voce_disse_se_ela_disse(d, ligada):
    """Atribuir à pessoa o que ela não afirmou derruba a descida inteira.

    A cadeia só funciona se cada passo for reconhecido como dela. Uma
    sessão em que `B1` não fechou — porque ela declarou não saber, ou
    porque o teto de tentativas estourou — não pode receber "no começo
    você afirmou".
    """
    com = _no_ultimo(d, confirmou=True)
    assert com.tela.dados["voce_disse"] is True
    assert com.tela.dados["premissa"] == d.nos[COLIDE].simples
    assert com.tela.dados["premissa_no"] == COLIDE

    sem = _no_ultimo(d, confirmou=False)
    assert sem.tela.dados["voce_disse"] is False
    assert sem.tela.dados["premissa"] == d.nos[COLIDE].simples


def test_a_premissa_da_colisao_so_aparece_no_ultimo_degrau(d, ligada):
    t, _ = _na_descida(d)
    assert t.tela.dados["premissa"] == ""
    assert t.tela.dados["voce_disse"] is False


def test_o_texto_da_cadeia_nao_atribui_nada_a_pessoa(d):
    """Quem decide se cabe "você disse" é o motor, que viu a sessão.

    O YAML não sabe o que aconteceu, então nenhum degrau pode afirmar que
    a pessoa disse alguma coisa. Se um texto futuro trouxer isso de volta,
    este teste cai.
    """
    for i, p in enumerate(d.descida(CRENCA).passos, 1):
        junto = " ".join((p.pergunta, p.porque)).lower()
        for frase in ("você afirmou", "você disse", "voce afirmou",
                      "você tinha dito", "eu já tinha dito"):
            assert frase not in junto, "degrau %d: %r" % (i, frase)


# --------------------------------------------------------------------------
# A evidência: para quem sustentou até o fim
# --------------------------------------------------------------------------

def test_sustentar_ate_o_fim_leva_ao_fato(d, ligada):
    t, _ = _na_descida(d)
    for _ in range(len(d.descida(CRENCA).passos)):
        t = _degrau(d, t.estado, motor.DECORRE)
    assert t.tela.tipo == "evidencia"
    tipos = [e.tipo for e in t.eventos]
    assert "descida_sustentada" in tipos
    assert "evidencia_apresentada" in tipos
    sustentada = [e for e in t.eventos if e.tipo == "descida_sustentada"][0]
    assert sustentada.dados["profundidade"] == len(d.descida(CRENCA).passos)


def test_o_evento_da_evidencia_nao_ocupa_o_campo_tipo(d, ligada):
    """O log escreve `{"tipo": <evento>, **dados}`, e os dados vêm depois.

    Este evento levava o tipo da evidência num campo `tipo`, e a linha
    saía no log chamada `erro_de_compilacao`. O log agora protege os
    campos da casa — e o nome aqui continua tendo de ser outro.
    """
    t = _no_ultimo(d)
    t = _degrau(d, t.estado, motor.DECORRE)
    ev = [e for e in t.eventos if e.tipo == "evidencia_apresentada"][0]
    assert "tipo" not in ev.dados, ev.dados
    assert ev.dados["evidencia"] == d.descida(CRENCA).evidencia.tipo


def test_evidencia_pendente_nao_desenha_terminal(d, ligada):
    """A tela promete evidência, e evidência inventada é pior que nenhuma.

    Não há compilador C na máquina em que esta cadeia foi escrita. Em vez
    de inventar a mensagem do gcc, a evidência fica `pendente`: a tela
    mostra o programa e a GARANTIA do padrão, e não finge um terminal.
    """
    ev = d.descida(CRENCA).evidencia
    assert ev.origem == "pendente"
    assert ev.gravada is False

    t = _no_ultimo(d)
    t = _degrau(d, t.estado, motor.DECORRE)
    assert t.tela.tipo == "evidencia"
    assert t.tela.dados["saida"] == ""
    assert t.tela.dados["gravada"] is False
    # O que sobra tem de ser verdadeiro e bastar: a afirmação e a garantia.
    assert t.tela.texto == ev.afirmacao
    assert "6.3.2.1" in t.tela.dados["garantia"]
    assert t.tela.dados["programa"].strip()


def test_evidencia_gravada_aparece_com_a_saida_e_o_onde(tmp_path, ligada):
    """A contraprova da de cima: quando houve terminal, ele aparece."""
    def muda(c):
        c["evidencia"].update(origem="gravada", saida="erro: tipo array",
                              onde="gcc 13.2, Debian 12")
    gravado = carrega(_monta(tmp_path / "g1", muda), topico="kc_07")
    t = _no_ultimo(gravado)
    t = _degrau(gravado, t.estado, motor.DECORRE)
    assert t.tela.dados["gravada"] is True
    assert t.tela.dados["saida"] == "erro: tipo array"
    assert t.tela.dados["onde"] == "gcc 13.2, Debian 12"


def test_saida_sobrando_numa_evidencia_pendente_nao_vai_para_a_tela(
        tmp_path, ligada):
    """O carregador cobra saída quando a origem é gravada, e não o inverso.

    Então uma saída pode SOBRAR numa evidência que voltou para pendente —
    alguém tirou a máquina do ar, ou copiou a cadeia para outra crença e
    esqueceu o terminal antigo. A tela não pode mostrá-la: ela estaria
    dizendo "foi isto que saiu" sobre uma execução que ninguém fez.
    """
    def muda(c):
        c["evidencia"]["saida"] = "saida de uma execucao que ninguem fez"
    sobrou = carrega(_monta(tmp_path / "p1", muda), topico="kc_07")
    assert sobrou.descida(CRENCA).evidencia.origem == "pendente"
    t = _no_ultimo(sobrou)
    t = _degrau(sobrou, t.estado, motor.DECORRE)
    assert t.tela.dados["saida"] == ""
    assert t.tela.dados["gravada"] is False


def test_nao_sei_na_descida_nao_fecha_pela_boca_dela(d, ligada):
    """Nem seguiu nem contradisse: ninguém pode dizer que ela se convenceu."""
    t, _ = _na_descida(d)
    t = motor.avanca(d, t.estado, Resposta(nao_sei=True))
    tipos = [e.tipo for e in t.eventos]
    assert "descida_fechou" not in tipos
    assert "descida_sem_resposta" in tipos
    assert t.tela.tipo == "evidencia"


def test_declarar_que_nao_sabe_vence_a_alternativa_marcada(d, ligada):
    """O botão "não sei" chega com a alternativa ainda selecionada.

    Se a escolha ganhasse, declarar que não sabe seria registrado como
    seguir a própria crença mais um degrau — inventando convicção onde a
    pessoa acabou de dizer que não tem.
    """
    t, _ = _na_descida(d)
    t = motor.avanca(d, t.estado,
                     Resposta(escolha=motor.DECORRE, nao_sei=True))
    tipos = [e.tipo for e in t.eventos]
    assert "descida_passo" not in tipos, tipos
    assert "descida_sem_resposta" in tipos


def test_indice_que_nao_existe_estoura_em_vez_de_virar_resposta(d, ligada):
    t, _ = _na_descida(d)
    for ruim in (2, -1, True):
        with pytest.raises(motor.EscolhaInvalida):
            motor.avanca(d, t.estado, Resposta(escolha=ruim))


# --------------------------------------------------------------------------
# Depois da descida: o mesmo treino
# --------------------------------------------------------------------------

def test_a_descida_termina_em_treino_como_a_refutacao(d, ligada):
    """RF33 vale igual aqui: convencer não confirma, treinar confirma."""
    t, _ = _na_descida(d)
    t = _degrau(d, t.estado, motor.VERDADE)
    depois = motor.avanca(d, t.estado, Resposta())
    assert depois.estado.no(ALVO).estado == motor.EM_TREINO
    assert depois.estado.fase == motor.TREINO
    tipos = [e.tipo for e in depois.eventos]
    assert "refutacao_concluida" in tipos
    assert "treino_iniciado" in tipos
    concluida = [e for e in depois.eventos
                 if e.tipo == "refutacao_concluida"][0]
    assert concluida.dados["via"] == "descida"
    assert CRENCA in depois.estado.a_retestar


def test_a_sessao_inteira_com_a_descida_termina(d, ligada):
    """Fase nova não pode travar a unidade: tem de chegar ao mapa."""
    pol = _politica(d)
    t = motor.inicia(d)
    tipos = []
    for _ in range(300):
        tipos.append(t.tela.tipo)
        if t.tela.tipo == "mapa":
            break
        if t.tela.tipo == "descida":
            t = _degrau(d, t.estado, motor.DECORRE)
            continue
        if t.tela.tipo in ("descida_fim", "evidencia"):
            t = motor.avanca(d, t.estado, Resposta())
            continue
        t = motor.avanca(d, t.estado, pol(t.tela, t.estado))
    else:
        raise AssertionError("a unidade não terminou")
    assert "descida" in tipos
    assert "evidencia" in tipos
    assert "refutacao" not in tipos, "a descida e a refutação rodaram juntas"


# --------------------------------------------------------------------------
# O carregador: uma cadeia malfeita não entra em sessão
# --------------------------------------------------------------------------

def _monta(destino: Path, muda) -> Path:
    cru = {nome: yaml.safe_load((RAIZ / nome).read_text(encoding="utf-8"))
           for nome in ARQUIVOS}
    muda(cru["descidas_kc07.yaml"]["descidas"][CRENCA])
    destino.mkdir(parents=True, exist_ok=True)
    for nome, dado in cru.items():
        (destino / nome).write_text(
            yaml.safe_dump(dado, allow_unicode=True, sort_keys=False),
            encoding="utf-8")
    return destino


def _recusa(tmp_path, nome, muda):
    with pytest.raises(DominioInvalido) as erro:
        carrega(_monta(tmp_path / nome, muda), topico="kc_07")
    return erro.value.problemas


def test_a_colisao_tem_de_ser_um_no_do_topico(tmp_path):
    p = _recusa(tmp_path, "c1", lambda c: c.update(colide_com="Z9"))
    assert any("colide_com" in x and "Z9" in x for x in p), p


def test_uma_descida_de_um_passo_so_nao_e_descida(tmp_path):
    p = _recusa(tmp_path, "c2", lambda c: c.update(passos=c["passos"][:1]))
    assert any("dois degraus" in x for x in p), p


def test_degrau_sem_as_quatro_partes_nao_carrega(tmp_path):
    def muda(c):
        c["passos"][1] = {k: v for k, v in c["passos"][1].items()
                          if k != "verdade"}
    p = _recusa(tmp_path, "c3", muda)
    assert any("verdade" in x and "degrau 2" in x for x in p), p


def test_evidencia_gravada_sem_saida_nao_carrega(tmp_path):
    """Ou grava de verdade, ou assume que está pendente."""
    def muda(c):
        c["evidencia"]["origem"] = "gravada"
    p = _recusa(tmp_path, "c4", muda)
    assert any("saída vazia" in x for x in p), p
    assert any("ONDE" in x for x in p), p


def test_evidencia_pendente_sem_garantia_nao_carrega(tmp_path):
    """Sem saída gravada, a garantia é tudo o que a tela tem de verdadeiro."""
    def muda(c):
        c["evidencia"]["garantia"] = ""
    p = _recusa(tmp_path, "c5", muda)
    assert any("garantia" in x for x in p), p


def test_descida_de_crenca_que_nao_existe_nao_carrega(tmp_path):
    def muda(c):
        pass

    def monta(destino):
        cru = {nome: yaml.safe_load((RAIZ / nome).read_text(encoding="utf-8"))
               for nome in ARQUIVOS}
        desc = cru["descidas_kc07.yaml"]["descidas"]
        desc["nao_existe"] = copy.deepcopy(desc[CRENCA])
        destino.mkdir(parents=True, exist_ok=True)
        for nome, dado in cru.items():
            (destino / nome).write_text(
                yaml.safe_dump(dado, allow_unicode=True, sort_keys=False),
                encoding="utf-8")
        return destino

    with pytest.raises(DominioInvalido) as erro:
        carrega(monta(tmp_path / "c6"), topico="kc_07")
    assert any("nao_existe" in x for x in erro.value.problemas)


def test_o_corte_por_premissa_leva_a_descida_junto():
    """Cortar o nó que a crença nega tira a cadeia dela da sessão."""
    curto = carrega(topico="kc_07", premissas=3)
    assert CRENCA not in curto.crencas
    assert curto.descida(CRENCA) is None
