# -*- coding: utf-8 -*-
"""Testes de arquitetura: o que atravessa tópico, e o que não atravessa.

SÃO TESTES DE CONSTATAÇÃO, e não de requisito. Eles descrevem o sistema
como ele é — a colisão de ids, o log sem conceito, o `prerequisites`
descartado, o limite do reteste, as crenças compartilhadas — para que
cada mudança dessa arquitetura seja DELIBERADA em vez de surpresa.

A especificação que os pediu está em `docs/historico-individual.md`, e a
auditoria que a originou em `docs/auditoria-travessia.md`. Nenhum dos dois
documentos tocou no motor, e este arquivo também não: ele mede.

O PERIGO DESTE TIPO DE TESTE é virar enfeite. Teste que passa hoje e
continuaria passando depois da mudança que ele deveria acusar não guarda
nada — e este projeto já produziu um desses, descoberto por sabotagem e
não por releitura. Então cada teste aqui diz, no corpo da mensagem de
falha, O QUE FAZER quando ele cair: quase sempre a queda é a mudança
chegando, e a correção é atualizar o número E o documento.

UMA CORREÇÃO QUE ESTE ARQUIVO TROUXE. A especificação escreveu que o log
é "por sessão, por nó, **nunca por conceito**". A primeira metade é
verdade; a segunda, não: SETE eventos da descida carregam `requer`, que é
lista de ids do inventário de conceitos. Eles não dizem o que um cartão
ENSINOU — dizem o que um degrau EXIGE —, e é por isso que a frase passou
tanto tempo de pé. Está medido em
`test_so_a_descida_carrega_conceito_e_como_exigencia`.
"""
from __future__ import annotations

import ast
import collections
import dataclasses
import hashlib
import pathlib

import pytest
import yaml

from mvp import motor
from mvp.dominio import Dominio, carrega, topicos
from mvp.motor import Resposta

RAIZ = pathlib.Path(__file__).resolve().parent
DOMINIO = RAIZ / "dominio"

_INVENTARIO = yaml.safe_load(
    (DOMINIO / "conceitos.yaml").read_text(encoding="utf-8"))["conceitos"]
CONCEITOS = frozenset(_INVENTARIO)


# --------------------------------------------------------------------------
# O percurso: três personas, em processo, sem servidor
# --------------------------------------------------------------------------
#
# Os testes de conceito e de identidade de nó precisam dos EVENTOS de uma
# sessão inteira, e não de uma chamada isolada ao motor. As personas são
# as do caminhante, reescritas aqui em vinte linhas porque `caminha()`
# fala HTTP e isto não precisa de servidor:
#
#     acerta     tudo certo, razão certa, confiança alta
#     crente     erra pela crença duas vezes por nó, e sustenta a razão
#     nao_sabe   diz "não sei" em metade dos itens, pelo id
#
# As três juntas cobrem 33 dos 49 nomes de evento do motor. Os 16 que
# faltam são da descida, que está DESLIGADA por padrão e, hoje, sem
# cadeia aprovada — e é por isso que o teste de conceito também lê o
# código-fonte, que é exaustivo.

PERSONAS = ("acerta", "crente", "nao_sabe")


def _cala(aid: str) -> bool:
    """A alternância da persona `nao_sabe`: pelo id, nunca por sorteio."""
    return hashlib.sha256(aid.encode("utf-8")).digest()[0] % 2 == 0


def _politica(d: Dominio, nome: str, m: dict):
    def escolhe(tela, e):
        if tela.tipo in ("ensino", "validacao", "refutacao", "mapa"):
            return Resposta()
        if tela.tipo == "frase":
            return Resposta(texto="uma frase de " + tela.dados["momento"])
        if tela.tipo == "confianca":
            return Resposta(confianca="tenho certeza")
        if tela.tipo == "razao":
            razoes = e.pendente.razoes
            if nome == "nao_sabe":
                return Resposta(nao_sei=True)
            if nome == "acerta" or not m["errou"]:
                return Resposta(escolha=next(i for i, z in enumerate(razoes)
                                             if z.correta))
            i = next((i for i, z in enumerate(razoes)
                      if z.crenca and z.crenca == m["crenca"]), None)
            if i is None:
                i = next(i for i, z in enumerate(razoes) if not z.correta)
            return Resposta(escolha=i)
        if tela.tipo != "atividade":
            return Resposta()

        a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
        na_tela = motor.opcoes_na_tela(e.semente, a)

        def pela_crenca():
            i = next((k for k, o in enumerate(na_tela)
                      if o.crenca is not None and o.crenca == a.crenca),
                     next((k for k, o in enumerate(na_tela)
                           if not o.correta and o.crenca is not None), None))
            return i if i is not None else next(
                k for k, o in enumerate(na_tela) if not o.correta)

        if nome == "nao_sabe":
            if _cala(a.id):
                return Resposta(nao_sei=True)
            return Resposta(escolha=pela_crenca())
        if nome == "acerta":
            return Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                         if o.correta))
        if m["erros"][a.no] < 2:
            if e.fase != motor.RETESTE:
                m["erros"][a.no] += 1
            i = pela_crenca()
            m["errou"], m["crenca"] = True, na_tela[i].crenca
            return Resposta(escolha=i)
        m["errou"], m["crenca"] = False, None
        return Resposta(escolha=next(i for i, o in enumerate(na_tela)
                                     if o.correta))

    return escolhe


def percorre(d: Dominio, nome: str, semente: str = "P01",
             limite: int = 2000) -> list:
    """A unidade inteira, do começo ao mapa. Devolve os eventos."""
    m = {"erros": collections.Counter(), "errou": False, "crenca": None}
    politica = _politica(d, nome, m)
    t = motor.inicia(d, semente=semente)
    eventos = list(t.eventos)
    for _ in range(limite):
        if t.tela.tipo == "mapa":
            return eventos
        t = motor.avanca(d, t.estado, politica(t.tela, t.estado))
        eventos.extend(t.eventos)
    raise AssertionError("%s/%s não terminou em %d passos"
                         % (d.id, nome, limite))


@pytest.fixture(scope="module")
def eventos_kc02():
    return [e for nome in PERSONAS for e in percorre(carrega(topico="kc_02"),
                                                     nome)]


# --------------------------------------------------------------------------
# 1. Os ids de nó colidem entre tópicos
# --------------------------------------------------------------------------
#
# Medido em 08/11/2026 nos treze grafos. Hoje a colisão é INOFENSIVA,
# porque nada atravessa: um processo serve um tópico. No dia em que o
# estado atravessar, ela é silenciosa e grave — o `I3` do kc_02 e o do
# kc_06 ocupariam a mesma entrada de `Estado.nos`, e falam de coisas
# diferentes.

COLISOES = {"B1": 13, "B2": 13, "I1": 13, "B3": 12, "I2": 12, "I3": 11,
            "B4": 3, "I4": 2}


def _nos_por_topico() -> dict[str, set[str]]:
    fora: dict[str, set[str]] = collections.defaultdict(set)
    for p in sorted(DOMINIO.glob("graph_kc*.yaml")):
        topico = "kc_" + p.stem[len("graph_kc"):]
        grafo = yaml.safe_load(p.read_text(encoding="utf-8"))
        for nid in (grafo.get("nodes") or {}):
            fora[nid].add(topico)
    return dict(fora)


def test_os_ids_de_no_colidem_entre_topicos():
    """O número exato, por id.

    Cai quando um tópico ganha ou perde nó — e aí a pergunta a responder
    é se o estado já atravessa. Se atravessar, o id passa a ser
    `kc_02:I3`, como `docs/historico-individual.md` especifica, e este
    teste é reescrito junto.
    """
    medido = {nid: len(ts) for nid, ts in _nos_por_topico().items()}
    assert medido == COLISOES, (
        "a distribuição dos ids de nó mudou.\n"
        "  medido:  %s\n"
        "  esperado: %s\n"
        "Nó novo ou nó removido muda este mapa. Se o estado passou a "
        "atravessar tópicos, a correção NÃO é mexer no número: é "
        "qualificar o id com o tópico." % (sorted(medido.items()),
                                           sorted(COLISOES.items())))


def test_nenhum_id_de_no_e_exclusivo_de_um_topico():
    """Não há um id sequer que sirva de chave global.

    É o que torna a colisão arquitetural e não acidental: qualquer estado
    que junte dois tópicos colide no primeiro nó.
    """
    sozinhos = {nid: sorted(ts) for nid, ts in _nos_por_topico().items()
                if len(ts) == 1}
    assert not sozinhos, sozinhos


def test_o_estado_da_sessao_e_indexado_por_id_simples():
    """`Estado.nos` é mapa de id SIMPLES, e é aí que a colisão morde.

    Cai no dia em que as chaves virarem `kc_02:B1` — que é a mudança
    especificada. Nesse dia, confira se `log.reconstroi` e o exportador
    acompanharam.
    """
    d = carrega(topico="kc_02")
    t = motor.inicia(d)
    m = {"erros": collections.Counter(), "errou": False, "crenca": None}
    politica = _politica(d, "crente", m)
    for _ in range(2000):
        if t.tela.tipo == "mapa":
            break
        t = motor.avanca(d, t.estado, politica(t.tela, t.estado))
    chaves = sorted(t.estado.nos)
    assert chaves, "a sessão não registrou nó nenhum"
    qualificadas = [k for k in chaves if ":" in k]
    assert not qualificadas, (
        "o estado passou a qualificar o nó: %s. Se foi de propósito, este "
        "teste e `docs/historico-individual.md` mudam juntos."
        % qualificadas)
    assert set(chaves) <= set(d.nos), (
        "o estado guardou nó que não é do domínio carregado: %s"
        % sorted(set(chaves) - set(d.nos)))


def test_so_o_evento_conceitual_qualifica_o_no_com_o_topico(eventos_kc02):
    """O SEGUNDO MECANISMO, aplicado só onde o dado atravessa tópico.

    ESTE TESTE MUDOU DE LADO em 09/11/2026, e era para mudar. Ele dizia
    "nenhum evento qualifica o nó", e caiu quando `conceito_apresentado`
    entrou — que é a mudança que `docs/historico-individual.md`
    especifica. A catraca funcionou: quem mexeu veio aqui declarar a
    arquitetura nova em vez de descobri-la depois.
    """
    com_no = {e.tipo for e in eventos_kc02 if "no" in (e.dados or {})}
    com_topico = {e.tipo for e in eventos_kc02
                  if "topico" in (e.dados or {})}
    assert len(com_no) == 29, sorted(com_no)
    assert com_topico == {"unidade_iniciada", "teachback_inicial",
                          "teachback_final"}, sorted(com_topico)

    # Os eventos de SESSÃO ficam com o id simples: eles são lidos dentro
    # de um tópico, e qualificar ali mexeria no motor sem necessidade.
    qualificam = {e.tipo for e in eventos_kc02
                  if isinstance((e.dados or {}).get("no"), str)
                  and ":" in e.dados["no"]}
    assert qualificam == set(CONCEITUAIS), sorted(qualificam)

    # E o que eles qualificam é um nó de verdade, deste tópico.
    for e in eventos_kc02:
        if e.tipo not in CONCEITUAIS:
            continue
        topico, _, no = e.dados["no"].partition(":")
        assert topico == "kc_02", e.dados
        assert no in carrega(topico="kc_02").nos, e.dados


# --------------------------------------------------------------------------
# 2. Nenhum evento diz que CONCEITO um cartão apresentou
# --------------------------------------------------------------------------
#
# O log grava `ensino_apresentado {no}` e `premissa_apresentada {no}` —
# por NÓ. Que o cartão do I3 do kc_02 apresenta `funcao_com_parametro` é
# verdade do `conceitos.yaml`, nunca do log. É a lacuna que os quatro
# eventos conceituais da especificação existem para fechar.
#
# A LEITURA DO FONTE, e não só o percurso: a descida está desligada por
# padrão e sem cadeia aprovada, então nenhuma persona alcança os eventos
# dela. Varrer o fonte com `ast` cobre os 49 nomes, inclusive os que
# sessão nenhuma produz hoje.

EVENTOS_DO_MOTOR = 53
CONCEITUAIS = ("conceito_apresentado", "conceito_diagnosticado",
               "conceito_confirmado", "conceito_revisitado")
# Os quatro entraram em 09/11/2026: o primeiro, e depois os três de
# percurso. O primeiro mecanismo do histórico individual está completo.
CONCEITUAIS_PRONTOS = CONCEITUAIS

# A única chave de payload que carrega conceito, e os eventos que a levam.
CHAVE_DE_CONCEITO = "requer"
LEVAM_CONCEITO = frozenset((
    "descida_iniciada", "descida_passo", "descida_fechou",
    "descida_sustentada", "descida_sem_recurso", "descida_sem_resposta",
    "cadeia_abandonada"))

# O único espalhamento que o `ast` não lê: `**_procedencia(a)`, que põe
# `do_molde` e `parametros` quando o item vem de molde. Nomeado aqui para
# que um espalhamento NOVO caia no teste em vez de abrir um buraco calado.
ESPALHAMENTOS = (("atividade_apresentada", "_procedencia"),)


def _chaves_de(no: ast.AST, locais: dict, espalha: list) -> set:
    """As chaves de um payload de evento, resolvendo `dict(base, ...)`."""
    if isinstance(no, ast.Dict):
        fora = set()
        for chave, valor in zip(no.keys, no.values):
            if isinstance(chave, ast.Constant):
                fora.add(chave.value)
            elif chave is None:          # **algo
                if (isinstance(valor, ast.Call)
                        and isinstance(valor.func, ast.Name)):
                    espalha.append(valor.func.id)
                else:
                    fora.add(None)
            else:
                fora.add(None)
        return fora
    if (isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
            and no.func.id == "dict"):
        fora = {kw.arg for kw in no.keywords if kw.arg}
        for a in no.args:
            if isinstance(a, ast.Name) and a.id in locais:
                fora |= locais[a.id]
            else:
                fora.add(None)
        return fora
    if isinstance(no, ast.Name) and no.id in locais:
        return set(locais[no.id])
    return {None}


def _fabricas(arvore) -> dict:
    """As funções que constroem `Evento` com o NOME vindo de parâmetro.

    `_por_conceito(d, nid, tipo, **campos)` é uma: ela faz
    `Evento(tipo, {...})`, e por isso o nome do evento não está onde ela
    está — está em quem a chama. Sem reconhecer isso, a varredura
    perderia os quatro eventos conceituais e deixaria de ser exaustiva,
    que é a única coisa que ela tem para oferecer.

    Devolve {função: (parâmetro do nome, chaves literais, parâmetro **)}.
    """
    fora = {}
    for fn in [n for n in ast.walk(arvore)
               if isinstance(n, ast.FunctionDef)]:
        nomes_de_param = [a.arg for a in fn.args.args]
        kwargs = fn.args.kwarg.arg if fn.args.kwarg else None
        for no in ast.walk(fn):
            if not (isinstance(no, ast.Call)
                    and isinstance(no.func, ast.Name)
                    and no.func.id == "Evento"
                    and no.args and isinstance(no.args[0], ast.Name)
                    and no.args[0].id in nomes_de_param):
                continue
            chaves = set()
            if len(no.args) > 1 and isinstance(no.args[1], ast.Dict):
                for chave in no.args[1].keys:
                    if isinstance(chave, ast.Constant):
                        chaves.add(chave.value)
            fora[fn.name] = (no.args[0].id, chaves, kwargs)
    return fora


def eventos_do_fonte(alvo: pathlib.Path | None = None):
    """{nome do evento: chaves do payload}, e os espalhamentos opacos.

    Lê `Evento(...)` no fonte do motor, e também as FÁBRICAS — funções
    que recebem o nome do evento por parâmetro. É a varredura EXAUSTIVA:
    inclui o que nenhuma sessão de hoje produz.
    """
    arvore = ast.parse((alvo or (RAIZ / "motor.py"))
                       .read_text(encoding="utf-8"))
    achados: dict[str, set] = collections.defaultdict(set)
    opacos: list = []
    fabricas = _fabricas(arvore)

    escopos = [arvore] + [n for n in ast.walk(arvore)
                          if isinstance(n, ast.FunctionDef)]
    for escopo in escopos:
        locais: dict[str, set] = {}
        espalha: list[str] = []
        for no in ast.walk(escopo):
            if (isinstance(no, ast.Assign) and len(no.targets) == 1
                    and isinstance(no.targets[0], ast.Name)):
                locais[no.targets[0].id] = _chaves_de(no.value, locais,
                                                      espalha)
        for no in ast.walk(escopo):
            if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Name)):
                continue

            # Chamada a uma fábrica: o nome do evento está AQUI.
            if no.func.id in fabricas:
                param, literais, kwargs = fabricas[no.func.id]
                pos = [a.arg for a in next(
                    f for f in ast.walk(arvore)
                    if isinstance(f, ast.FunctionDef)
                    and f.name == no.func.id).args.args].index(param)
                valor = None
                if len(no.args) > pos and isinstance(no.args[pos],
                                                     ast.Constant):
                    valor = no.args[pos].value
                else:
                    for kw in no.keywords:
                        if kw.arg == param and isinstance(kw.value,
                                                          ast.Constant):
                            valor = kw.value.value
                if valor is None:
                    continue           # repasse entre fábricas
                achados[valor] |= set(literais)
                achados[valor] |= {kw.arg for kw in no.keywords
                                   if kw.arg and kw.arg != param}
                continue

            if no.func.id != "Evento":
                continue
            if not no.args or not isinstance(no.args[0], ast.Constant):
                # Nome vindo de parâmetro DENTRO da fábrica: resolvido
                # pelos chamadores, logo não é opaco.
                if any(isinstance(no.args[0], ast.Name)
                       and no.args[0].id == p
                       for p, _, _ in fabricas.values()):
                    continue
                opacos.append(("<nome não literal>", no.lineno))
                continue
            nome = no.args[0].value
            achados[nome]          # existe mesmo sem payload
            if len(no.args) > 1:
                espalhados: list[str] = []
                chaves = _chaves_de(no.args[1], locais, espalhados)
                if None in chaves:
                    opacos.append((nome, "<payload não literal>"))
                for f in espalhados:
                    opacos.append((nome, f))
                achados[nome] |= (chaves - {None})
    return dict(achados), tuple(sorted(set(opacos)))


def test_o_motor_tem_cinquenta_e_tres_eventos():
    """A catraca que obriga quem criar evento novo a passar por aqui.

    Era 49, virou 50 com `conceito_apresentado` e 53 com os três de
    percurso, tudo em 09/11/2026. Quando ela cair: suba o número E
    responda, no mesmo commit, se o evento novo carrega conceito.

    E ela só continua valendo porque a varredura enxerga FÁBRICA: os
    quatro conceituais são construídos por `_por_conceito`, que recebe o
    nome do evento por parâmetro. Quando eles entraram, o scan passou a
    ver 49 em vez de 53 — e consertar o scanner foi o certo, porque a
    única coisa que este teste tem para oferecer é exaustividade.
    """
    nomes, _ = eventos_do_fonte()
    assert len(nomes) == EVENTOS_DO_MOTOR, (
        "o motor tem %d nomes de evento, e este teste esperava %d.\n"
        "  agora:  %s\n"
        "Evento novo não entra calado: diga se ele carrega conceito."
        % (len(nomes), EVENTOS_DO_MOTOR, sorted(nomes)))


def test_os_quatro_eventos_conceituais_existem():
    """O placar do histórico individual: os quatro estão de pé.

    O teste nasceu em 08/11 negando os quatro, e mudou de lado duas
    vezes num dia — primeiro para "existe um, faltam três", agora para os
    quatro. Era para ser assim: ele é o placar, e placar que não muda
    não está medindo nada.

    Com os quatro prontos, o PRIMEIRO mecanismo do histórico individual
    está completo. Faltam o guarda `(código, tópico)` e a leitura por
    código — e nenhum dos dois cria evento.
    """
    nomes, _ = eventos_do_fonte()
    existem = tuple(n for n in CONCEITUAIS if n in nomes)
    assert existem == CONCEITUAIS_PRONTOS, (
        "o placar dos eventos conceituais mudou.\n"
        "  existem: %s\n  esperado: %s\n"
        "Atualize CONCEITUAIS_PRONTOS e `docs/historico-individual.md` "
        "no mesmo commit." % (sorted(existem), sorted(CONCEITUAIS_PRONTOS)))
    # E cada um carrega o que o desenho dele exige: o conceito, o nó
    # qualificado, e o campo que diz de onde o conceito foi atribuído.
    for nome in CONCEITUAIS:
        assert "conceito" in nomes[nome], (nome, sorted(nomes[nome]))
        assert "no" in nomes[nome], (nome, sorted(nomes[nome]))
    assert "material" in nomes["conceito_apresentado"]
    for nome in CONCEITUAIS[1:]:
        assert "atribuicao" in nomes[nome], (nome, sorted(nomes[nome]))


def test_o_log_fala_de_conceito_em_duas_gramaticas_e_so_duas():
    """`requer` diz o que um degrau EXIGE; `conceito` diz o que ACONTECEU.

    A CORREÇÃO QUE ESTE TESTE FEZ, em 08/11: a especificação dizia que o
    log nunca fala de conceito. Falava — sete eventos da descida carregam
    `requer`, lista de ids do inventário —, e a frase errada passou
    porque eles não dizem que um cartão apresentou algo.

    Hoje são duas gramáticas, e é importante que continuem separadas: a
    exigência de um degrau de refutação não é evidência sobre a pessoa.
    Misturá-las deixaria a análise somar coisas que não se somam.

    E O ENSINO CONTINUA MUDO sobre conceito: `ensino_apresentado` e
    `premissa_apresentada` dizem só o nó, e quem fala de conceito é o
    evento conceitual ao lado deles. É o que mantém os dois registros
    independentes — se um dia o evento do nó passar a carregar conceito,
    haverá duas fontes para o mesmo fato.
    """
    nomes, opacos = eventos_do_fonte()
    assert opacos == ESPALHAMENTOS, (
        "o fonte ganhou payload que o `ast` não lê: %s. Enquanto ele "
        "existir, a varredura não é exaustiva e a afirmação deste "
        "arquivo sobre conceito fica sem prova." % (opacos,))

    exigencia = {n for n, ch in nomes.items() if CHAVE_DE_CONCEITO in ch}
    assert exigencia == LEVAM_CONCEITO, (
        "quem carrega `requer` mudou.\n  agora: %s\n  antes: %s"
        % (sorted(exigencia), sorted(LEVAM_CONCEITO)))
    for nome in exigencia:
        assert nome.startswith("descida") or nome == "cadeia_abandonada", nome

    evidencia = {n for n, ch in nomes.items() if "conceito" in ch}
    assert evidencia == set(CONCEITUAIS), sorted(evidencia)
    assert not (exigencia & evidencia), sorted(exigencia & evidencia)

    assert nomes["ensino_apresentado"] == {"no", "indice", "total", "momento"}
    assert nomes["premissa_apresentada"] == {"no", "antes_de"}
    assert nomes["episodio_classificado"] == {
        "atividade", "no", "estado", "correta", "confianca", "nao_sei",
        "razao_correta", "crenca"}
    assert nomes["no_confirmado"] == {"no", "via", "superficies"}


def test_o_requer_da_descida_fala_o_vocabulario_do_inventario():
    """Todo `requer` de todo degrau é id de `conceitos.yaml`.

    É o que permite dizer que os quatro eventos novos não precisam de
    catálogo próprio. Cai se alguém escrever um requisito fora do
    inventário — e aí o inventário é que ganha a entrada.
    """
    fora = []
    for p in sorted(DOMINIO.glob("descidas_kc*.yaml")):
        cru = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for crenca, cadeia in (cru.get("descidas") or {}).items():
            for i, degrau in enumerate(cadeia.get("passos") or (), 1):
                for cid in degrau.get("requer") or ():
                    if cid not in CONCEITOS:
                        fora.append((p.name, crenca, i, cid))
    assert not fora, (
        "requisito que não está no inventário: %s" % fora)


# Quantas oportunidades de aprendizagem cada tópico registra por sessão.
#
# Medido em 09/11/2026. O kc_02 tem sete — dois no B1, três no B2, dois
# no B3. E o kc_07 tem UMA, a do `array` no B1, que entrou no mesmo dia
# com o material de ensino profundo daquele cartão.
#
# O SEGUNDO TÓPICO É O QUE IMPORTA AQUI: enquanto só o kc_02 declarava,
# "histórico individual" e "histórico de um tópico" eram a mesma coisa.
# Com dois, a travessia passa a ter o que atravessar.
# SUBIU PARA 8 NO KC_02 EM 12/11/2026, com a promoção do
# `comparacao_de_ponteiros`. O cartão `kc_02:B1` o ensinava desde
# 05/11, e o que segurava era a decisão do dono — tomada hoje. Um
# conceito a mais declarado no cartão é uma oportunidade a mais no log,
# e por isso este número e os de `TRAJETORIAS` subiram juntos, como
# estava escrito aqui que subiriam.
#
# O KC_06 ENTROU EM 12/11/2026, com UMA: a do `funcao_com_parametro` no
# B1, com a assinatura dos seis materiais do tópico. É o TERCEIRO
# tópico a aparecer aqui, e o primeiro cujo cartão declarado fica na
# ABERTURA — o B1 é nó observável, então a oportunidade é de quem entra
# no tópico, e não só de quem declara lacuna.
#
# E O KC_10 ENTROU NO MESMO DIA, também com UMA: a do
# `ponteiro_de_ponteiro` no B1. São QUATRO tópicos declarando, e os dois
# que entraram hoje são os dois que tinham dívida de construto.
OPORTUNIDADES = {"kc_02": 8, "kc_06": 1, "kc_07": 1, "kc_10": 1}

# O HISTÓRICO CONCEITUAL DE CADA PERSONA no kc_02, medido. São três
# trajetórias de aprendizagem diferentes, e o log passou a contá-las por
# conceito — que é o que o histórico individual existe para fazer.
#
#   acerta     teve oportunidade, foi diagnosticado, CONFIRMOU, e nunca
#              precisou revisitar
#   crente     teve oportunidade, errou pela crença, REVISITOU no treino
#              e aí confirmou
#   nao_sabe   teve oportunidade, declarou lacuna, revisitou na
#              construção e NUNCA CONFIRMOU
#
# É a diferença entre as três que torna o histórico uma medida. Se as
# três linhas fossem iguais, o log estaria registrando o currículo e não
# a pessoa.
#
# SUBIRAM PARA 8 (e 16) EM 12/11/2026, junto com o `OPORTUNIDADES`
# acima e pelo mesmo motivo — e era isto que esta nota previa, nestas
# palavras. O que este teste guarda não são os números: é que as três
# linhas continuem DIFERENTES entre si, e continuam.
TRAJETORIAS = {
    "acerta": {"conceito_apresentado": 8, "conceito_diagnosticado": 16,
               "conceito_confirmado": 8},
    "crente": {"conceito_apresentado": 8, "conceito_diagnosticado": 8,
               "conceito_revisitado": 8, "conceito_confirmado": 8},
    "nao_sabe": {"conceito_apresentado": 8, "conceito_diagnosticado": 16,
                 "conceito_revisitado": 8},
}


@pytest.mark.parametrize("topico", topicos())
def test_o_conceito_no_log_sai_so_pelos_eventos_conceituais(topico):
    """Os treze tópicos, as três personas: quem fala de conceito.

    ESTE TESTE MUDOU DE LADO DUAS VEZES em 09/11/2026 — exigia que
    nenhuma sessão gravasse conceito, depois que só um evento gravasse, e
    agora que só os quatro gravem.

    Doze tópicos continuam em ZERO, e é verdade medida, não defeito
    escondido: a auditoria do inventário cobriu kc_00, kc_01 e kc_02, e
    só o kc_02 tem cartão com explicação. O número sobe quando material
    novo for auditado — e é esse o trabalho que destrava o resto.
    """
    d = carrega(topico=topico)
    fora = []
    for nome in PERSONAS:
        apresentados = 0
        for e in percorre(d, nome):
            if e.tipo in CONCEITUAIS:
                if e.tipo == "conceito_apresentado":
                    apresentados += 1
                continue
            for chave, valor in (e.dados or {}).items():
                if "conceito" in chave.lower():
                    fora.append((nome, e.tipo, chave, valor))
                elif isinstance(valor, str) and valor in CONCEITOS:
                    fora.append((nome, e.tipo, chave, valor))
        assert apresentados == OPORTUNIDADES.get(topico, 0), (
            "%s/%s: %d oportunidades registradas, esperava %d"
            % (topico, nome, apresentados, OPORTUNIDADES.get(topico, 0)))
    assert not fora, (
        "%s: evento que NÃO é conceitual falou de conceito: %s. Se foi "
        "de propósito, diga aqui qual e por quê." % (topico, fora[:5]))


def test_a_oportunidade_nao_depende_de_quem_acerta():
    """As três personas recebem as MESMAS sete oportunidades no kc_02.

    É o que a palavra oportunidade tem de significar: quem erra tudo viu
    o mesmo cartão que quem acerta tudo. Se o número divergisse por
    persona, o evento estaria medindo desempenho e não apresentação — e
    o histórico passaria a dizer que a pessoa teve menos chance porque
    foi mal, que é o contrário do princípio.
    """
    d = carrega(topico="kc_02")
    por_persona = {nome: sum(1 for e in percorre(d, nome)
                             if e.tipo == "conceito_apresentado")
                   for nome in PERSONAS}
    assert set(por_persona.values()) == {OPORTUNIDADES["kc_02"]}, por_persona


def test_as_tres_personas_deixam_tres_historicos_diferentes():
    """O que o histórico conceitual passou a poder distinguir.

    E a linha que mais importa é a última: a persona que diz "não sei"
    recebe as sete oportunidades, é diagnosticada catorze vezes,
    revisita sete — e NUNCA confirma nada. Antes disto o log dizia isso
    por NÓ, e saber qual CONCEITO ficou sem confirmação exigia reler o
    `conceitos.yaml` e cruzar à mão.
    """
    d = carrega(topico="kc_02")
    medido = {}
    for nome in PERSONAS:
        contas = collections.Counter(e.tipo for e in percorre(d, nome)
                                     if e.tipo in CONCEITUAIS)
        medido[nome] = dict(contas)
    assert medido == TRAJETORIAS, (
        "as trajetórias conceituais mudaram.\n  agora: %s\n  antes: %s"
        % (sorted(medido.items()), sorted(TRAJETORIAS.items())))
    assert "conceito_confirmado" not in medido["nao_sabe"]
    assert "conceito_revisitado" not in medido["acerta"]


# --------------------------------------------------------------------------
# 3. O `prerequisites` não chega ao domínio carregado
# --------------------------------------------------------------------------
#
# O grafo curricular existe, declarado nos treze YAMLs de tópico — e o
# carregador o DESCARTA. É o que torna o princípio "nada é cobrado sem
# oportunidade anterior" uma declaração sem dente ENTRE tópicos: dentro
# de um, o `PRIMEIRO_CONTATO` o garante e há teste; entre tópicos, nada
# lê a dependência.

PREREQUISITOS = {
    "kc_00": [], "kc_01": ["kc_00"], "kc_02": ["kc_00"],
    "kc_03": ["kc_02"], "kc_04": ["kc_02", "kc_03"],
    "kc_05": ["kc_03", "kc_04"], "kc_06": ["kc_04"],
    "kc_07": ["kc_04", "kc_06"], "kc_08": ["kc_01", "kc_02", "kc_05"],
    "kc_09": ["kc_08", "kc_06"], "kc_10": ["kc_04", "kc_06", "kc_07"],
    "kc_11": ["kc_04", "kc_07"], "kc_12": ["kc_01", "kc_04", "kc_06"],
}

# O que o YAML do tópico declara, e o que o carregador lê. A diferença é
# o que está escrito e não vale nada.
CHAVES_DO_TOPICO = ("conclusion_node", "id", "pilot", "prerequisites",
                    "summary", "teachback", "title")
LIDAS_PELO_CARREGADOR = ("conclusion_node", "id", "teachback", "title")


def test_os_treze_topicos_declaram_o_prerequisito():
    """O grafo curricular está escrito, e está completo."""
    medido = {}
    for topico in topicos():
        sufixo = topico.replace("_", "")
        cru = yaml.safe_load((DOMINIO / ("topic_%s.yaml" % sufixo))
                             .read_text(encoding="utf-8"))
        assert "prerequisites" in cru, (
            "%s não declara `prerequisites`" % topico)
        medido[topico] = list(cru["prerequisites"] or [])
    assert medido == PREREQUISITOS, (
        "o grafo curricular mudou.\n  agora: %s\n  antes: %s"
        % (sorted(medido.items()), sorted(PREREQUISITOS.items())))


def test_o_carregador_le_quatro_das_sete_chaves_do_topico():
    """E `prerequisites` é uma das três que ele joga fora.

    Esta é a prova mecânica do descarte, e ela é exaustiva: lê no fonte
    de `dominio.py` TODO acesso a `cru_topico`. Cai no dia em que alguém
    ligar o campo — que é o que a especificação pede — e aí a lista de
    lidas cresce e o teste é atualizado de propósito.
    """
    arvore = ast.parse((RAIZ / "dominio.py").read_text(encoding="utf-8"))
    lidas = set()
    for no in ast.walk(arvore):
        alvo = None
        if (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)
                and no.func.attr in ("get", "pop")
                and isinstance(no.func.value, ast.Name)
                and no.func.value.id == "cru_topico"
                and no.args and isinstance(no.args[0], ast.Constant)):
            alvo = no.args[0].value
        elif (isinstance(no, ast.Subscript) and isinstance(no.value, ast.Name)
              and no.value.id == "cru_topico"
              and isinstance(no.slice, ast.Constant)):
            alvo = no.slice.value
        if alvo is not None:
            lidas.add(alvo)
    assert tuple(sorted(lidas)) == LIDAS_PELO_CARREGADOR, (
        "o carregador passou a ler %s. Se `prerequisites` entrou, o "
        "histórico individual começou: atualize este teste e o documento."
        % sorted(lidas))
    assert "prerequisites" not in lidas


def test_nenhum_modulo_do_mvp_le_o_prerequisito():
    """Nem o carregador, nem o motor, nem o painel, nem o exportador.

    Testes ficam de fora da varredura de propósito — este arquivo cita o
    nome do campo em cada linha.
    """
    chave = "prerequisites"
    acharam = [p.name for p in sorted(RAIZ.glob("*.py"))
               if not p.name.startswith("test_")
               and chave in p.read_text(encoding="utf-8")]
    assert not acharam, (
        "%s passou a citar `%s`. Isso é a mudança especificada chegando: "
        "confira se o motor a LÊ ou se é só comentário, e atualize este "
        "teste." % (acharam, chave))


def test_o_dominio_carregado_nao_tem_onde_guardar_o_prerequisito():
    """`Dominio` não tem campo para isso — os quinze são estes.

    Pinar os nomes é o que impede o campo de entrar sem ninguém decidir:
    um `prerequisitos: tuple = ()` novo derruba este teste.
    """
    nomes = tuple(f.name for f in dataclasses.fields(Dominio))
    assert nomes == ("id", "titulo", "conclusao", "nos", "crencas",
                     "atividades", "analogia", "teachback", "resgates",
                     "exemplos", "narracoes", "casos_resolvidos",
                     "outras_rotas", "testes_de_mesa", "descidas"), nomes
    for nome in nomes:
        assert "requisit" not in nome and "prereq" not in nome, nome
    # E o valor declarado não aparece em nenhum campo do objeto: o kc_09
    # depende do kc_08 e do kc_06, e o domínio dele não sabe disso.
    d = carrega(topico="kc_09")
    declarado = PREREQUISITOS["kc_09"]
    for f in dataclasses.fields(Dominio):
        valor = getattr(d, f.name)
        assert valor != declarado and valor != tuple(declarado), f.name


# --------------------------------------------------------------------------
# 4. O reteste não atravessa tópico
# --------------------------------------------------------------------------
#
# O reteste é A MEDIDA DE TRANSFERÊNCIA da tese, e o que ela mede hoje é
# transferência de SUPERFÍCIE dentro de um tópico: `_item_de_reteste`
# procura em `d.atividades`, que é o domínio carregado, e
# `_superficie_nova` compara FORMATO de pergunta.
#
# `pointer_is_integer` é o caso que mostra o limite inteiro: a crença
# existe nos dois tópicos, com nove itens no kc_02 e oito no kc_11 — e no
# kc_02 ela nega o I2, no kc_11 o B1.

CRENCA_QUE_ATRAVESSA = "pointer_is_integer"
ONDE_ELA_VIVE = {"kc_02": 9, "kc_11": 8}


def _oferecem(d: Dominio, crenca: str) -> list:
    return [a for a in d.atividades
            if any(o.crenca == crenca for o in a.opcoes)]


def test_a_crenca_de_teste_existe_nos_dois_topicos():
    """Sem isto, os três testes abaixo ficariam vazios e passariam."""
    medido = {t: len(_oferecem(carrega(topico=t), CRENCA_QUE_ATRAVESSA))
              for t in ONDE_ELA_VIVE}
    assert medido == ONDE_ELA_VIVE, medido
    assert carrega(topico="kc_02").crencas[CRENCA_QUE_ATRAVESSA].nega == "I2"
    assert carrega(topico="kc_11").crencas[CRENCA_QUE_ATRAVESSA].nega == "B1"


def test_o_item_de_reteste_sai_do_banco_do_topico_carregado():
    d = carrega(topico="kc_02")
    a = motor._item_de_reteste(d, motor.Estado(), CRENCA_QUE_ATRAVESSA)
    assert a is not None
    assert a in d.atividades
    assert a in _oferecem(d, CRENCA_QUE_ATRAVESSA)


def test_esgotado_o_topico_o_reteste_desiste_em_vez_de_atravessar():
    """Oito itens do kc_11 oferecem a mesma crença, e ficam inalcançáveis.

    É o teste que prende o limite: com o banco do kc_02 gasto, o seletor
    devolve `None` — e quem o chama grava `reteste_sem_item`. A travessia
    não é recusada por decisão; ela não é cogitada.
    """
    kc02 = carrega(topico="kc_02")
    kc11 = carrega(topico="kc_11")
    itens = _oferecem(kc02, CRENCA_QUE_ATRAVESSA)
    e = motor.Estado()
    for no in {a.no for a in itens}:
        e = e.com(no, usadas=tuple(a.id for a in itens if a.no == no))
    assert motor._item_de_reteste(kc02, e, CRENCA_QUE_ATRAVESSA) is None
    sobraram = _oferecem(kc11, CRENCA_QUE_ATRAVESSA)
    assert len(sobraram) == 8, [a.id for a in sobraram]


def test_a_superficie_que_falta_ao_topico_existe_no_outro():
    """E é por isso que o limite custa medida, e não só arquitetura.

    `comparar_casos` é formato que o kc_02 NÃO tem para esta crença e o
    kc_11 tem. A troca de superfície que o kc_02 não consegue oferecer
    está escrita, pronta, num tópico que o reteste não alcança.
    """
    daqui = {a.formato for a in _oferecem(carrega(topico="kc_02"),
                                          CRENCA_QUE_ATRAVESSA)}
    dela = {a.formato for a in _oferecem(carrega(topico="kc_11"),
                                         CRENCA_QUE_ATRAVESSA)}
    assert "comparar_casos" in dela - daqui, (sorted(daqui), sorted(dela))


def test_a_superficie_nova_compara_formato_e_nao_contexto():
    """O critério é o MOLDE da pergunta, dentro do tópico.

    Dois itens da mesma crença: um repete o formato já visto e sai
    `False`; o outro troca e sai `True`. Nenhum dos dois olha tópico — e
    é por isso que a medida de contexto precisa de evento próprio, como
    `docs/historico-individual.md` especifica.
    """
    d = carrega(topico="kc_02")
    itens = _oferecem(d, CRENCA_QUE_ATRAVESSA)
    usado = next(a for a in itens
                 if sum(1 for x in itens if x.formato == a.formato) > 1)
    e = motor.Estado().com(usado.no, usadas=(usado.id,))
    mesmo = next(a for a in itens
                 if a.formato == usado.formato and a.id != usado.id)
    outro = next(a for a in itens if a.formato != usado.formato)
    assert motor._superficie_nova(d, e, CRENCA_QUE_ATRAVESSA, mesmo) is False
    assert motor._superficie_nova(d, e, CRENCA_QUE_ATRAVESSA, outro) is True


def test_o_visto_do_reteste_e_consultado_no_no_do_item():
    """E é aqui que o limite 4 encosta na colisão do 1.

    `_item_de_reteste` pergunta `e.no(a.no).usadas` — por NÓ. A mesma
    crença mora no I2 no kc_02 e no B1 no kc_11: num estado que juntasse
    os dois bancos, o "já viu" seria consultado na entrada errada, e o
    erro sairia plausível. Juntar bancos exige qualificar o nó ANTES.
    """
    d = carrega(topico="kc_02")
    itens = _oferecem(d, CRENCA_QUE_ATRAVESSA)
    um = itens[0]
    # Marcado como usado no nó CERTO: o seletor não o devolve.
    certo = motor.Estado().com(um.no, usadas=(um.id,))
    assert motor._item_de_reteste(d, certo,
                                 CRENCA_QUE_ATRAVESSA) is not um
    # Marcado no nó ERRADO: o seletor o devolve como se nunca tivesse
    # aparecido. É este o modo de falha silencioso da travessia.
    outro_no = next(n for n in d.nos if n != um.no)
    errado = motor.Estado().com(outro_no, usadas=(um.id,))
    assert motor._item_de_reteste(d, errado, CRENCA_QUE_ATRAVESSA) is um


# --------------------------------------------------------------------------
# 5. Catorze crenças aparecem em mais de um tópico
# --------------------------------------------------------------------------
#
# É a boa notícia da auditoria: a IDENTIDADE que permitiria medir
# transferência de CONTEXTO já existe no catálogo. Uma crença refutada no
# kc_02 pode voltar no kc_08, com o mesmo id, num contexto outro.
#
# O catálogo sustenta a medida que a tese quer; o mecanismo é que não a
# faz.

CRENCAS_EM_VARIOS = {
    "ampersand_copies": ["kc_04", "kc_06", "kc_10", "kc_12"],
    "pointer_is_data": ["kc_02", "kc_04", "kc_08", "kc_12"],
    "pointer_is_just_a_name": ["kc_04", "kc_05", "kc_10"],
    "declaration_allocates": ["kc_03", "kc_07"],
    "declaration_zeroes": ["kc_00", "kc_03"],
    "function_gets_original": ["kc_06", "kc_09"],
    "memory_is_uniform": ["kc_01", "kc_12"],
    "modify_pp_changes_p": ["kc_06", "kc_10"],
    "no_value_no_memory": ["kc_00", "kc_03"],
    "pointer_is_integer": ["kc_02", "kc_11"],
    "pointer_knows_block_size": ["kc_09", "kc_11"],
    "pointer_lives_in_heap": ["kc_08", "kc_09"],
    "string_literal_is_array": ["kc_07", "kc_11"],
    "system_frees_auto": ["kc_01", "kc_08"],
}
# Eram 60 até 09/11/2026, quando `array_confused_with_cell` entrou no
# kc_07 — a crença que o B1 não tinha, e sem a qual seis distratores
# daquele nó eram atribuídos a `string_literal_is_array`, que é sobre
# literal de string. Ela é de um tópico só, então as catorze que
# atravessam não mudaram.
CRENCAS_DO_PROJETO = 61

# A crença que atravessa negando o MESMO id de nó nos dois tópicos. Uma,
# de catorze — e é coincidência, não desenho.
MESMO_NO_NOS_DOIS = ("declaration_zeroes",)


def _crencas_por_topico() -> dict[str, dict[str, str]]:
    """{crença: {tópico: nó que ela nega}}."""
    fora: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for p in sorted(DOMINIO.glob("beliefs_kc*.yaml")):
        topico = "kc_" + p.stem[len("beliefs_kc"):]
        for bruto in yaml.safe_load(p.read_text(encoding="utf-8")) or ():
            fora[bruto["id"]][topico] = str(bruto.get("negates", "")).split(":")[-1]
    return dict(fora)


def test_catorze_das_sessenta_crencas_atravessam_topico():
    """A identidade para o reteste entre contextos já existe.

    Cai quando o catálogo mudar — e aí vale reler se a crença nova
    aumenta ou diminui o que a tese pode medir.
    """
    todas = _crencas_por_topico()
    assert len(todas) == CRENCAS_DO_PROJETO, len(todas)
    medido = {cid: sorted(onde) for cid, onde in todas.items()
              if len(onde) > 1}
    assert medido == CRENCAS_EM_VARIOS, (
        "as crenças que atravessam mudaram.\n  agora: %s\n  antes: %s"
        % (sorted(medido.items()), sorted(CRENCAS_EM_VARIOS.items())))


def test_a_crenca_que_atravessa_nega_no_diferente_em_cada_topico():
    """TREZE DAS CATORZE. Só `declaration_zeroes` cai no B3 nos dois.

    É a medida que decide o desenho: a crença é a identidade que
    atravessa; o nó NÃO é. Um histórico individual indexado por nó
    perderia a travessia de treze das catorze — e as juntaria erradas,
    porque os ids colidem.
    """
    mudam, iguais = [], []
    for cid, onde in sorted(_crencas_por_topico().items()):
        if len(onde) < 2:
            continue
        (iguais if len(set(onde.values())) == 1 else mudam).append(cid)
    assert tuple(iguais) == MESMO_NO_NOS_DOIS, (iguais, mudam)
    assert len(mudam) == 13, mudam


def test_a_travessia_de_crenca_tem_item_nos_dois_lados():
    """Identidade sem item dos dois lados não mede nada.

    Para cada uma das catorze, cada tópico onde ela vive tem pelo menos
    um item que a oferece — logo a medida de contexto é alcançável com o
    banco de hoje, e falta só o mecanismo.
    """
    magros = []
    for cid, topicos_ in sorted(CRENCAS_EM_VARIOS.items()):
        for topico in topicos_:
            quantos = len(_oferecem(carrega(topico=topico), cid))
            if quantos == 0:
                magros.append((cid, topico))
    assert not magros, (
        "crença que atravessa sem item em algum tópico: %s" % magros)
