# -*- coding: utf-8 -*-
"""Os outros três eventos conceituais, e o que eles podem afirmar.

`conceito_apresentado` registra OPORTUNIDADE. Estes três registram o que
aconteceu depois:

    conceito_diagnosticado   demonstrou algo no diagnóstico
    conceito_confirmado      evidência de domínio pela regra do sistema
    conceito_revisitado      foi trabalhado de novo

A DECISÃO DE DESENHO QUE PRECISA FICAR ESCRITA, porque ela é uma
APROXIMAÇÃO e não um fato: **de onde sai o conceito**.

A especificação dizia que `conceito_diagnosticado` sairia de
`episodio_classificado` "com o conceito do item". Não existe conceito do
item. O inventário declara CARTÃO (`evidencia.cartoes`), nunca item — e
derivar o conceito do código do item por varredura é justamente o que a
auditoria de 05/11 provou que não funciona: três falsos positivos, todos
com o construto num exemplo que ensina outra coisa.

Então os três atribuem pelo CARTÃO DO NÓ, e cada evento diz isso no
payload: `atribuicao: "cartao_do_no"`.

O QUE ISSO CUSTA, e o preço é real. O cartão do B2 apresenta três
conceitos. Um episódio no B2 produz TRÊS eventos, e nenhum deles afirma
que aquele item mediu aquele conceito — afirma que o episódio foi na
premissa cujo cartão apresenta os três. É diluição, e a análise tem de
saber. O campo existe para ela saber: no dia em que houver declaração
por item, ele passa a `"item"` e as duas épocas ficam separáveis.

O QUE NÃO SE FAZ COM ISSO. `conceito_confirmado` não quer dizer que a
pessoa domina o conceito: quer dizer que o nó cujo cartão o apresenta
fechou pela regra do sistema — duas superfícies, a CS-5. É a mesma
separação que o inventário faz entre `disponivel` e `confirmado`, e
dissolvê-la transformaria o histórico em declaração falsa de domínio.
"""
from __future__ import annotations

import json

import pytest

from mvp import conceitos, motor
from mvp.dominio import carrega, topicos
from mvp.motor import Resposta

# As três personas e o percurso vêm de `test_arquitetura.py` de propósito:
# são os mesmos que medem a arquitetura, e um quarto caminhante neste
# arquivo poderia divergir deles sem ninguém notar.
from mvp.test_arquitetura import PERSONAS, percorre

OS_QUATRO = ("conceito_apresentado", "conceito_diagnosticado",
             "conceito_confirmado", "conceito_revisitado")

# O que o kc_02 declara: os três nós observáveis, e nenhum de inferência.
COM_CONCEITO = {"B1": 2, "B2": 3, "B3": 2}
SEM_CONCEITO = ("I1", "I2", "I3")


def _de(eventos, tipo):
    return [e for e in eventos if e.tipo == tipo]


@pytest.fixture(scope="module")
def d():
    return carrega(topico="kc_02")


@pytest.fixture(scope="module")
def trilhas(d):
    """Os eventos de cada persona, uma vez só: o percurso é caro."""
    return {nome: percorre(d, nome) for nome in PERSONAS}


# --------------------------------------------------------------------------
# conceito_diagnosticado
# --------------------------------------------------------------------------

def test_todo_episodio_de_no_com_conceito_e_diagnosticado(d, trilhas):
    """Um evento por conceito do cartão, em cada episódio daquele nó.

    Cai se um episódio deixar de ser atribuído — e aí o histórico passa a
    ter oportunidade sem desfecho, que é pior do que não ter nenhum dos
    dois: a análise contaria a apresentação e perderia o resultado.
    """
    for nome, eventos in trilhas.items():
        episodios = _de(eventos, "episodio_classificado")
        assert episodios, nome
        esperado = sum(COM_CONCEITO.get(e.dados["no"], 0) for e in episodios)
        achado = len(_de(eventos, "conceito_diagnosticado"))
        assert achado == esperado, (nome, achado, esperado)


def test_o_evento_do_diagnostico_carrega_o_estado_do_episodio(d, trilhas):
    """O que foi demonstrado é a CLASSIFICAÇÃO, e ela vem inteira.

    Sem o estado, o evento diria apenas "houve episódio" — e lacuna,
    crença e confirmada são diagnósticos opostos.
    """
    for nome, eventos in trilhas.items():
        por_atividade = {}
        for e in _de(eventos, "episodio_classificado"):
            por_atividade[e.dados["atividade"]] = e.dados["estado"]
        for e in _de(eventos, "conceito_diagnosticado"):
            assert e.dados["estado"] == por_atividade[e.dados["atividade"]], \
                (nome, e.dados)


def test_o_payload_do_diagnostico_e_exatamente_estes_campos(d, trilhas):
    for eventos in trilhas.values():
        for e in _de(eventos, "conceito_diagnosticado"):
            assert set(e.dados) == {"conceito", "no", "atividade", "estado",
                                    "atribuicao"}, e.dados
            assert e.dados["atribuicao"] == "cartao_do_no", e.dados


def test_no_de_inferencia_nao_produz_evento_de_diagnostico(d, trilhas):
    """Os três nós de inferência do kc_02 não têm cartão declarado.

    Calar é o certo: atribuir conceito ali seria inventar oportunidade
    que a auditoria não achou.
    """
    for nome, eventos in trilhas.items():
        nos = {e.dados["no"].split(":")[1]
               for e in _de(eventos, "conceito_diagnosticado")}
        assert not (nos & set(SEM_CONCEITO)), (nome, sorted(nos))


def test_a_lacuna_tambem_e_diagnostico(d, trilhas):
    """Quem diz "não sei" demonstrou algo, e o histórico registra.

    Se só o acerto produzisse evento, o histórico teria a forma de um
    boletim — e a lacuna é o dado que mais importa para saber se faltou
    oportunidade.
    """
    eventos = trilhas["nao_sabe"]
    estados = {e.dados["estado"]
               for e in _de(eventos, "conceito_diagnosticado")}
    assert "lacuna" in estados, sorted(estados)


def test_a_crenca_tambem_e_diagnostico(d, trilhas):
    eventos = trilhas["crente"]
    estados = {e.dados["estado"]
               for e in _de(eventos, "conceito_diagnosticado")}
    assert "crenca" in estados, sorted(estados)


# --------------------------------------------------------------------------
# conceito_confirmado
# --------------------------------------------------------------------------

def test_todo_no_confirmado_com_conceito_produz_evento(d, trilhas):
    """E a persona `nao_sabe` confirma ZERO, como tem de ser.

    A primeira versão deste teste exigia que TODA persona confirmasse
    algo, e caiu — corretamente. Quem declara lacuna em metade dos itens
    e "não sei" na razão não fecha nó nenhum pela CS-5, e um histórico
    que lhe atribuísse conceito confirmado estaria mentindo. A asserção
    vale por persona, e o total é que não pode ser zero.
    """
    total = 0
    for nome, eventos in trilhas.items():
        confirmados = _de(eventos, "no_confirmado")
        esperado = sum(COM_CONCEITO.get(e.dados["no"], 0)
                       for e in confirmados)
        achado = len(_de(eventos, "conceito_confirmado"))
        assert achado == esperado, (nome, achado, esperado)
        total += achado
    assert total, "nenhuma persona confirmou nada: o teste ficaria vazio"
    assert not _de(trilhas["nao_sabe"], "conceito_confirmado"), (
        "quem diz 'não sei' passou a ter conceito confirmado")


def test_o_evento_de_confirmacao_carrega_o_via_do_no(d, trilhas):
    """`diagnostico`, `vacilo` ou `treino` — o caminho importa.

    Confirmar no diagnóstico e confirmar depois de uma crença refutada
    são evidências de forças diferentes, e `forca()` já desconta por
    isso. Perder o `via` aqui apagaria a diferença no histórico.
    """
    vias = set()
    for nome, eventos in trilhas.items():
        por_no = {e.dados["no"]: e.dados["via"]
                  for e in _de(eventos, "no_confirmado")}
        for e in _de(eventos, "conceito_confirmado"):
            no = e.dados["no"].split(":")[1]
            assert e.dados["via"] == por_no[no], (nome, e.dados)
            vias.add(e.dados["via"])
    assert vias <= {"diagnostico", "vacilo", "treino"}, sorted(vias)
    assert len(vias) >= 2, sorted(vias)


def test_o_payload_da_confirmacao_e_exatamente_estes_campos(d, trilhas):
    for eventos in trilhas.values():
        for e in _de(eventos, "conceito_confirmado"):
            assert set(e.dados) == {"conceito", "no", "via",
                                    "atribuicao"}, e.dados


def test_a_confirmacao_nao_diz_que_a_pessoa_domina_o_conceito(d, trilhas):
    """O evento é sobre o NÓ ter fechado, e o payload não pode sugerir
    mais do que isso.

    `atribuicao: cartao_do_no` é o que impede a leitura errada: o nó
    fechou pela CS-5, e o conceito está atribuído pelo cartão — não
    medido item por item.
    """
    for eventos in trilhas.values():
        for e in _de(eventos, "conceito_confirmado"):
            assert e.dados["atribuicao"] == "cartao_do_no", e.dados
            for proibido in ("domina", "aprendeu", "sabe", "dominado"):
                assert proibido not in e.dados, e.dados


# --------------------------------------------------------------------------
# conceito_revisitado
# --------------------------------------------------------------------------

def test_pedir_de_novo_grava_revisitado(d):
    """"Ainda não entendi" é trabalhar de novo, e agora deixa rastro.

    Era este o evento que faltava para `conceito_apresentado` poder
    calar na repetição: ver de novo não é oportunidade nova, é revisita.
    """
    t = motor.inicia(d)
    t = motor.avanca(d, t.estado, Resposta(texto="uma frase"))
    assert _de(list(t.eventos), "conceito_apresentado")
    t = motor.avanca(d, t.estado, Resposta(repetir=True))
    revisitados = _de(list(t.eventos), "conceito_revisitado")
    assert len(revisitados) == COM_CONCEITO["B1"], [e.dados for e in
                                                    t.eventos]
    for e in revisitados:
        assert e.dados["momento"] == "reexplicacao", e.dados
        assert e.dados["no"] == "kc_02:B1", e.dados
    assert not _de(list(t.eventos), "conceito_apresentado")


def test_a_construcao_grava_revisitado(d, trilhas):
    """Declarar lacuna leva à construção, que mostra o cartão de novo."""
    eventos = trilhas["nao_sabe"]
    construcoes = [e for e in _de(eventos, "construcao_iniciada")
                   if e.dados["no"] in COM_CONCEITO]
    assert construcoes, "a persona nao_sabe não construiu nó com conceito"
    da_construcao = [e for e in _de(eventos, "conceito_revisitado")
                     if e.dados["momento"] == "construcao"]
    esperado = sum(COM_CONCEITO[e.dados["no"]] for e in construcoes)
    assert len(da_construcao) == esperado, (len(da_construcao), esperado)


def test_o_treino_grava_revisitado(d, trilhas):
    """O treino depois da refutação é revisita, e é onde o nó reconstrói."""
    eventos = trilhas["crente"]
    treinos = [e for e in _de(eventos, "treino_iniciado")
               if e.dados["no"] in COM_CONCEITO]
    assert treinos, "a persona crente não treinou nó com conceito"
    do_treino = [e for e in _de(eventos, "conceito_revisitado")
                 if e.dados["momento"] == "treino"]
    esperado = sum(COM_CONCEITO[e.dados["no"]] for e in treinos)
    assert len(do_treino) == esperado, (len(do_treino), esperado)


def test_os_tres_momentos_da_revisita_aparecem(d, trilhas):
    """Os três existem, e cada um mede coisa diferente: pedir de novo é
    a pessoa dizendo que não entendeu; a construção é o sistema
    respondendo a uma lacuna; o treino é reconstrução depois de crença
    refutada. Colapsá-los num só apagaria a diferença.

    A `reexplicacao` NÃO sai das três personas — nenhuma delas aperta
    "Ainda não entendi" —, e a primeira versão deste teste cobrava isso
    delas e caía. O momento entra aqui pelo percurso que o produz, e o
    teste continua afirmando que os três existem no sistema.
    """
    momentos = set()
    for eventos in trilhas.values():
        for e in _de(eventos, "conceito_revisitado"):
            momentos.add(e.dados["momento"])
    assert momentos == {"construcao", "treino"}, sorted(momentos)

    t = motor.inicia(d)
    t = motor.avanca(d, t.estado, Resposta(texto="uma frase"))
    t = motor.avanca(d, t.estado, Resposta(repetir=True))
    momentos |= {e.dados["momento"]
                 for e in _de(list(t.eventos), "conceito_revisitado")}
    assert momentos == {"reexplicacao", "construcao", "treino"}, \
        sorted(momentos)


def test_o_payload_da_revisita_e_exatamente_estes_campos(d, trilhas):
    for eventos in trilhas.values():
        for e in _de(eventos, "conceito_revisitado"):
            assert set(e.dados) == {"conceito", "no", "momento",
                                    "atribuicao"}, e.dados


# --------------------------------------------------------------------------
# As invariantes dos quatro
# --------------------------------------------------------------------------

@pytest.mark.parametrize("topico", topicos())
def test_os_quatro_eventos_qualificam_o_no_pelo_topico(topico):
    """Todos os quatro são feitos para ser lidos ATRAVÉS de tópicos."""
    d = carrega(topico=topico)
    for nome in PERSONAS:
        for e in percorre(d, nome):
            if e.tipo not in OS_QUATRO:
                continue
            topico_do_evento, _, no = e.dados["no"].partition(":")
            assert topico_do_evento == topico, e.dados
            assert no in d.nos, e.dados


@pytest.mark.parametrize("topico", topicos())
def test_os_quatro_falam_so_de_conceito_disponivel(topico):
    """Nenhum evento conceitual pode falar de conceito que o inventário
    não liberou: seria declarar oportunidade que a auditoria não achou."""
    d = carrega(topico=topico)
    for nome in PERSONAS:
        for e in percorre(d, nome):
            if e.tipo in OS_QUATRO:
                assert conceitos.disponivel(e.dados["conceito"]), e.dados


def test_nenhum_conceito_e_confirmado_sem_ter_sido_apresentado(d, trilhas):
    """A invariante que o princípio do projeto exige, agora no LOG.

    *Nenhum conhecimento deve ser cobrado antes de existir uma
    oportunidade identificável de aprendizagem.* Dentro de um tópico isso
    já tinha mecanismo — o `PRIMEIRO_CONTATO` — e nenhuma medida. Agora
    tem: o log diz quais conceitos foram apresentados e quais foram
    confirmados, e a segunda lista não pode ter nada fora da primeira.
    """
    for nome, eventos in trilhas.items():
        apresentados = {(e.dados["conceito"], e.dados["no"])
                        for e in _de(eventos, "conceito_apresentado")}
        for tipo in ("conceito_diagnosticado", "conceito_confirmado",
                     "conceito_revisitado"):
            for e in _de(eventos, tipo):
                chave = (e.dados["conceito"], e.dados["no"])
                assert chave in apresentados, (nome, tipo, e.dados)


def test_a_reexecucao_nao_depende_de_nenhum_dos_quatro(tmp_path):
    """O CS-6 continua de pé com os quatro no arquivo.

    É o que mantém a versão do log em 3, pelo motivo escrito em
    `mvp/log.py`: os eventos conceituais são linhas aditivas, e a
    reexecução lê só `entrada_recebida`. Se algum dia ela passar a
    depender de um evento, este teste cai e a versão sobe no mesmo
    commit.
    """
    from mvp import log

    caminho = tmp_path / "com.jsonl"
    d = carrega(topico="kc_02")

    t = motor.inicia(d, semente="P91")
    log.grava("P91", t.eventos, destino=caminho)
    for _ in range(600):
        if t.tela.tipo == "mapa":
            break
        tela = t.tela
        if tela.tipo == "frase":
            r = Resposta(texto="uma frase")
        elif tela.tipo == "confianca":
            r = Resposta(confianca="tenho certeza")
        elif tela.tipo == "razao":
            r = Resposta(escolha=next(
                i for i, z in enumerate(t.estado.pendente.razoes)
                if z.correta))
        elif tela.tipo == "atividade":
            a = next(x for x in d.atividades
                     if x.id == tela.dados["atividade"])
            na_tela = motor.opcoes_na_tela(t.estado.semente, a)
            r = Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                      if o.correta))
        else:
            r = Resposta()
        t = motor.avanca(d, t.estado, r)
        log.grava("P91", t.eventos, destino=caminho, entrada=r)

    com = log.reconstroi(d, "P91", destino=caminho)
    assert com is not None

    cruas = [x for x in caminho.read_text(encoding="utf-8").splitlines()
             if x.strip()]
    linhas = [x for x in cruas if json.loads(x).get("tipo") not in OS_QUATRO]
    assert len(linhas) < len(cruas), "o log não tinha evento conceitual"
    sem = tmp_path / "sem.jsonl"
    sem.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    assert log.reconstroi(d, "P91", destino=sem).estado == com.estado


COM_DECLARACAO = ("kc_02", "kc_07")


@pytest.mark.parametrize("topico", [t for t in topicos()
                                    if t not in COM_DECLARACAO])
def test_os_onze_topicos_sem_declaracao_continuam_calados(topico):
    """Zero eventos conceituais, e isso é verdade medida.

    ERAM DOZE, e caiu em 09/11/2026 — exatamente como estava escrito
    aqui: "quando material novo for auditado, este teste cai, e cair
    aqui é o currículo crescendo". O B1 do kc_07 ganhou material de
    ensino profundo e o `array` foi promovido a `disponivel`.

    Cada tópico que ganhar material derruba este teste de novo, e é
    assim que o placar não envelhece calado.
    """
    d = carrega(topico=topico)
    for nome in PERSONAS:
        for e in percorre(d, nome):
            assert e.tipo not in OS_QUATRO, (topico, nome, e.tipo, e.dados)
