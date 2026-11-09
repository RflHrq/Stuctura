# -*- coding: utf-8 -*-
"""`conceito_apresentado`: o primeiro dos quatro eventos conceituais.

O QUE ELE DEMONSTRA: a pessoa teve OPORTUNIDADE de aprender aquele
conceito, naquele cartão, naquela versão do material. É a primeira linha
de log do projeto que fala de conceito e não de nó — e `requer`, da
descida, não conta: aquele diz o que um degrau EXIGE.

AS TRÊS DECISÕES DE DESENHO, e o que cada uma custa se for ao contrário:

    um evento POR CONCEITO        o cartão do B2 apresenta três, e são
                                  três oportunidades. Uma lista num
                                  evento só obrigaria a análise a
                                  desaninhar para contar qualquer coisa.

    o nó QUALIFICADO pelo tópico  `kc_02:B1`, e não `B1`. É o segundo
                                  mecanismo aplicado onde a
                                  especificação manda: só onde o dado
                                  atravessa tópico. Os eventos de
                                  sessão continuam com o id simples.

    a ASSINATURA do material      o que a pessoa viu, não o que o
                                  arquivo diz hoje.

E O QUE ELE NÃO FAZ. Apresentação não é compreensão: este evento não
diz que a pessoa aprendeu, e os outros três do histórico existem para
não deixar confundir. É a mesma separação que o inventário já faz entre
`disponivel` e `confirmado`.

ONDE ELE SAI: nas DUAS entradas do cartão — a abertura, que ensina os
nós observáveis, e o primeiro contato, que apresenta a premissa de
inferência antes da primeira pergunta sobre ela. Construção,
reexplicação e treino são `conceito_revisitado`, que é outro evento e
outra fatia.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from mvp import conceitos, motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

DOMINIO = pathlib.Path(__file__).resolve().parent / "dominio"

# O que o kc_02 declara, medido em `conceitos.yaml`.
NA_ABERTURA = {
    "kc_02:B1": ("endereco", "operador_endereco"),
    "kc_02:B2": ("operador_endereco", "ponteiro", "sizeof"),
    "kc_02:B3": ("derreferencia", "operador_endereco"),
}


def _abre(d, semente="P01"):
    """A abertura inteira: devolve (eventos, transições).

    `inicia` devolve a tela do TEACH-BACK, não o primeiro cartão — a
    primeira versão deste auxiliar parava ali e os doze tópicos sem
    declaração passaram a "não gravar ensino nenhum", que é falso. Aqui
    ele responde a frase e atravessa todos os cartões, parando na
    primeira pergunta.
    """
    t = motor.inicia(d, semente=semente)
    eventos, passos = list(t.eventos), [list(t.eventos)]
    for _ in range(40):
        tela = t.tela
        if tela.tipo == "frase":
            r = Resposta(texto="uma frase de abertura")
        elif tela.tipo == "ensino":
            r = Resposta()
        else:
            break
        t = motor.avanca(d, t.estado, r)
        eventos.extend(t.eventos)
        passos.append(list(t.eventos))
    return eventos, passos


def _conceituais(eventos, tipo="conceito_apresentado"):
    return [e for e in eventos if e.tipo == tipo]


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


# --------------------------------------------------------------------------
# A abertura
# --------------------------------------------------------------------------

def test_a_abertura_grava_um_evento_por_conceito_de_cada_cartao(d):
    eventos, _ = _abre(d)
    por_cartao = {}
    for e in _conceituais(eventos):
        por_cartao.setdefault(e.dados["no"], []).append(e.dados["conceito"])
    assert {k: tuple(sorted(v)) for k, v in por_cartao.items()} == NA_ABERTURA


def test_o_evento_sai_na_mesma_transicao_do_ensino_apresentado(d):
    """Um cartão mostrado e o conceito não registrado seria oportunidade
    perdida do log, e a análise não teria como saber que houve.

    Por passo, e não no total: um evento conceitual que saísse numa
    transição diferente da do cartão deixaria a análise sem como saber
    QUAL cartão deu a oportunidade.
    """
    _, passos = _abre(d)
    com_cartao = [p for p in passos
                  if any(e.tipo == "ensino_apresentado" for e in p)]
    assert len(com_cartao) == 3, len(com_cartao)
    for passo in com_cartao:
        ensino = next(e for e in passo if e.tipo == "ensino_apresentado")
        conceituais = _conceituais(passo)
        assert conceituais, ensino.dados
        for e in conceituais:
            assert e.dados["no"] == "kc_02:" + ensino.dados["no"], e.dados


def test_o_no_do_evento_conceitual_e_qualificado_pelo_topico(d):
    """`kc_02:B1`, e não `B1`.

    Os ids de nó colidem nos treze tópicos — `B1` existe em todos —, e
    este evento é feito para ser lido ATRAVÉS de tópicos. Sem a
    qualificação, dois cartões diferentes ocupariam a mesma linha de
    histórico. Está medido em `mvp/test_arquitetura.py`.
    """
    eventos, _ = _abre(d)
    for e in _conceituais(eventos):
        assert e.dados["no"].startswith("kc_02:"), e.dados
        assert e.dados["no"].split(":")[1] in d.nos, e.dados


def test_o_evento_carrega_a_assinatura_do_material(d):
    """E é a assinatura DAQUELE cartão, não a do arquivo."""
    eventos, _ = _abre(d)
    for e in _conceituais(eventos):
        no = e.dados["no"].split(":")[1]
        assert e.dados["material"] == d.assinatura(no), e.dados


def test_o_momento_diz_por_onde_o_cartao_entrou(d):
    eventos, _ = _abre(d)
    momentos = {e.dados["momento"] for e in _conceituais(eventos)}
    assert momentos == {"abertura"}, momentos


def test_o_evento_nao_diz_que_a_pessoa_aprendeu(d):
    """Apresentação não é compreensão, e o payload não pode sugerir que é.

    Nada de `aprendeu`, `confirmado` ou `dominado` aqui: quem mede isso
    é o diagnóstico e o reteste. Confundir os dois transformaria o
    histórico em declaração falsa de domínio.
    """
    proibidos = ("aprendeu", "confirmado", "dominado", "correta", "sabe")
    eventos, _ = _abre(d)
    for e in _conceituais(eventos):
        assert set(e.dados) == {"conceito", "no", "momento", "material"}, \
            e.dados
        for chave in e.dados:
            assert chave not in proibidos, e.dados


@pytest.mark.parametrize("topico", [t for t in topicos() if t != "kc_02"])
def test_cartao_sem_declaracao_nao_grava_conceito(topico):
    """Doze dos treze tópicos não têm declaração, e o log fica calado.

    Calar é a resposta certa: inventar que o cartão do kc_07 apresenta
    algo seria dizer que houve oportunidade onde a auditoria não achou
    nenhuma. O cartão continua registrado em `ensino_apresentado`.
    """
    eventos, _ = _abre(carrega(topico=topico))
    assert _conceituais(eventos) == []
    assert [e for e in eventos if e.tipo == "ensino_apresentado"]


# --------------------------------------------------------------------------
# O primeiro contato: a outra entrada do cartão
# --------------------------------------------------------------------------

@pytest.fixture
def inventario_de_teste(tmp_path, monkeypatch):
    """Um inventário que declara conceito num nó de INFERÊNCIA.

    Por que artificial: no kc_02 real, os três cartões declarados são
    B1, B2 e B3 — todos observáveis, e todos na abertura. O primeiro
    contato só alcança nó de inferência, então com o inventário real
    este caminho ficaria sem teste.

    MUNDO DE TESTE, e nunca evidência de que alguém auditou o cartão do
    I2. As liberações de verdade ficam em `mvp/dominio/conceitos.yaml`.
    """
    arquivo = tmp_path / "conceitos.yaml"
    arquivo.write_text(
        "conceitos:\n"
        "  tipo_do_ponteiro:\n"
        "    nome: \"mundo de teste\"\n"
        "    status: disponivel\n"
        "    introduzido_em: kc_02\n"
        "    evidencia:\n"
        "      cartoes: [\"kc_02:I2\"]\n"
        "      onde: \"fixture de test_conceito_apresentado.py\"\n"
        "      tipo: explicacao_com_exemplo\n",
        encoding="utf-8")
    monkeypatch.setenv("STRUCTURA_CONCEITOS", str(arquivo))
    conceitos.recarrega()
    yield
    monkeypatch.undo()
    conceitos.recarrega()


def _ate_o_primeiro_contato(d, alvo="I2", limite=400):
    """Acerta tudo até o primeiro contato daquele nó."""
    t = motor.inicia(d)
    eventos = list(t.eventos)
    for _ in range(limite):
        if t.estado.fase == motor.PRIMEIRO_CONTATO and t.estado.alvo == alvo:
            return eventos, t
        tela = t.tela
        if tela.tipo == "frase":
            r = Resposta(texto="uma frase")
        elif tela.tipo == "confianca":
            r = Resposta(confianca="tenho certeza")
        elif tela.tipo == "razao":
            r = Resposta(escolha=next(
                i for i, z in enumerate(t.estado.pendente.razoes) if z.correta))
        elif tela.tipo == "atividade":
            a = next(x for x in d.atividades
                     if x.id == tela.dados["atividade"])
            na_tela = motor.opcoes_na_tela(t.estado.semente, a)
            r = Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                      if o.correta))
        elif tela.tipo == "mapa":
            raise AssertionError("a unidade acabou sem passar pelo %s" % alvo)
        else:
            r = Resposta()
        t = motor.avanca(d, t.estado, r)
        eventos.extend(t.eventos)
    raise AssertionError("não cheguei ao primeiro contato do %s" % alvo)


def test_o_primeiro_contato_tambem_grava_conceito_apresentado(
        inventario_de_teste):
    """A premissa de inferência chega por aqui, com o cartão completo.

    `_primeiro_contato` usa a MESMA tela de construção, com a ampliação
    — está medido em `docs/auditoria-travessia.md`. Então é apresentação
    de cartão como a da abertura, e grava igual.
    """
    d = carrega(topico="kc_02")
    eventos, t = _ate_o_primeiro_contato(d, "I2")
    daqui = [e for e in t.eventos if e.tipo == "conceito_apresentado"]
    assert daqui, [e.tipo for e in t.eventos]
    assert {e.dados["conceito"] for e in daqui} == {"tipo_do_ponteiro"}
    assert daqui[0].dados["no"] == "kc_02:I2"
    assert daqui[0].dados["momento"] == "primeiro_contato"
    assert daqui[0].dados["material"] == d.assinatura("I2")


def test_o_primeiro_contato_sai_junto_da_premissa_apresentada(
        inventario_de_teste):
    d = carrega(topico="kc_02")
    _, t = _ate_o_primeiro_contato(d, "I2")
    tipos = [e.tipo for e in t.eventos]
    assert "premissa_apresentada" in tipos
    assert "conceito_apresentado" in tipos


def test_sem_declaracao_o_primeiro_contato_fica_calado():
    """Com o inventário REAL, o I2 do kc_02 não declara nada."""
    d = carrega(topico="kc_02")
    _, t = _ate_o_primeiro_contato(d, "I2")
    assert [e for e in t.eventos if e.tipo == "conceito_apresentado"] == []
    assert [e for e in t.eventos if e.tipo == "premissa_apresentada"]


# --------------------------------------------------------------------------
# A sessão inteira
# --------------------------------------------------------------------------

def test_a_sessao_do_kc02_grava_as_sete_oportunidades(d):
    """Sete eventos na abertura: dois no B1, três no B2, dois no B3.

    O número é o que a auditoria liberou, e cai quando o inventário
    mudar — promover conceito novo é promover oportunidade registrada.
    """
    eventos, _ = _abre(d)
    assert len(_conceituais(eventos)) == 7


def test_pedir_de_novo_nao_grava_oportunidade_nova(d):
    """"Ainda não entendi" mostra o cartão outra vez, e NÃO é apresentação.

    A decisão importa para os três eventos que faltam: ver de novo é
    `conceito_revisitado`, que é outro evento e mede outra coisa. Contar
    aqui inflaria a oportunidade — a pessoa que pede três vezes passaria
    a ter "três oportunidades" do mesmo conceito, e a análise leria
    insistência como currículo.
    """
    t = motor.inicia(d)
    t = motor.avanca(d, t.estado, Resposta(texto="uma frase"))
    primeira = len(_conceituais(list(t.eventos)))
    assert primeira == 2, [e.dados for e in _conceituais(list(t.eventos))]
    # Mesmo cartão, pedido de novo duas vezes.
    for _ in range(2):
        t = motor.avanca(d, t.estado, Resposta(repetir=True))
        assert _conceituais(list(t.eventos)) == [], [
            e.tipo for e in t.eventos]


def test_os_conceitos_registrados_sao_os_disponiveis_do_inventario(d):
    """Nenhum evento pode falar de conceito que o inventário não liberou.

    É o portão que impede o histórico de declarar oportunidade que a
    auditoria não achou.
    """
    eventos, _ = _abre(d)
    for e in _conceituais(eventos):
        assert conceitos.disponivel(e.dados["conceito"]), e.dados


# --------------------------------------------------------------------------
# O CS-6 continua de pé
# --------------------------------------------------------------------------

def test_a_reexecucao_nao_depende_do_evento_conceitual(tmp_path):
    """Apagar todas as linhas conceituais não muda o estado reconstruído.

    É o que autoriza a versão do log a NÃO subir, e o motivo está escrito
    em `mvp/log.py`: o gate de `reconstroi` protege a reexecução, que lê
    só `entrada_recebida`. Evento novo é linha aditiva.

    Se algum dia a reexecução passar a depender de um evento, este teste
    cai — e aí a versão do log tem de subir no mesmo commit, senão todo
    log já gravado vira irreexecutável em silêncio.
    """
    from mvp import log

    caminho = tmp_path / "com.jsonl"
    d = carrega(topico="kc_02")
    t = motor.inicia(d, semente="P88")
    log.grava("P88", t.eventos, destino=caminho)
    for _ in range(40):
        tela = t.tela
        if tela.tipo == "frase":
            r = Resposta(texto="uma frase")
        elif tela.tipo == "ensino":
            r = Resposta()
        else:
            break
        t = motor.avanca(d, t.estado, r)
        log.grava("P88", t.eventos, destino=caminho, entrada=r)

    com = log.reconstroi(d, "P88", destino=caminho)
    assert com is not None

    sem = tmp_path / "sem.jsonl"
    linhas = [x for x in caminho.read_text(encoding="utf-8").splitlines()
              if x.strip() and json.loads(x).get("tipo")
              != "conceito_apresentado"]
    assert len(linhas) < len(
        [x for x in caminho.read_text(encoding="utf-8").splitlines()
         if x.strip()]), "o log de teste não tinha evento conceitual nenhum"
    sem.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    assert log.reconstroi(d, "P88", destino=sem).estado == com.estado


# --------------------------------------------------------------------------
# E a linha chega ao ARQUIVO
# --------------------------------------------------------------------------

def test_a_linha_do_conceito_e_gravada_no_log(tmp_path, monkeypatch):
    """O motor emitir não é o log registrar, e o que a tese lê é o log.

    Grava pelo `log`, do mesmo jeito que o servidor — então o que este
    teste afirma é sobre o arquivo, e não sobre o que eu acho dele. É o
    mesmo cuidado que `test_exporta.py` já tomava.
    """
    from mvp import log

    destino = tmp_path / "sessao.jsonl"
    monkeypatch.setattr(log, "DESTINO", destino)
    d = carrega(topico="kc_02")

    t = motor.inicia(d, semente="P77")
    log.grava("P77", t.eventos)
    for _ in range(40):
        tela = t.tela
        if tela.tipo == "frase":
            r = Resposta(texto="uma frase de abertura", ms=3000)
        elif tela.tipo == "ensino":
            r = Resposta(ms=2000)
        else:
            break
        t = motor.avanca(d, t.estado, r)
        log.grava("P77", t.eventos)

    linhas = [json.loads(x) for x in
              destino.read_text(encoding="utf-8").splitlines() if x.strip()]
    conceituais = [x for x in linhas if x.get("tipo") == "conceito_apresentado"]
    assert len(conceituais) == 7, [x.get("tipo") for x in linhas]
    # `_linha` ACHATA o payload na linha, com os campos da casa
    # protegidos por sufixo. Nenhum campo deste evento colide — se algum
    # passar a colidir, ele sai como `conceito_dado` e este teste cai,
    # que é o aviso de que alguém precisa renomear.
    for linha in conceituais:
        assert linha["sessao"] == "P77"
        assert linha["no"].startswith("kc_02:"), linha
        assert conceitos.disponivel(linha["conceito"]), linha
        assert len(linha["material"]) == 12, linha
        assert linha["momento"] == "abertura", linha
    # E o conjunto gravado é o que o inventário declara, sem sobra.
    por_cartao = {}
    for linha in conceituais:
        por_cartao.setdefault(linha["no"], []).append(linha["conceito"])
    assert {k: tuple(sorted(v)) for k, v in por_cartao.items()} == NA_ABERTURA