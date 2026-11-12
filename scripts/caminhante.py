"""Atravessa a unidade inteira pelo HTTP, como um participante faria.

É o portão de conteúdo que `docs/linguagem.md` manda rodar antes de
qualquer pessoa ver a tela: ele diz quantas premissas um tópico novo
deixaria sem medida, e quantos passos a sessão custa.

Três personas, e cada uma existe por um motivo:

    sabido    acerta tudo                  — o caminho curto
    aprende   erra, e acerta depois da     — o caminho que o laço foi
              refutação                      desenhado para produzir
    crente    erra e nunca muda de ideia   — o pior caso

    python scripts/caminhante.py --persona aprende --quantas 10
    python scripts/caminhante.py --persona crente --codigo DEMO

Precisa do servidor no ar (`python -m mvp.app`) e carrega o domínio no
próprio processo para saber o gabarito — a tela NÃO entrega a resposta, e
isso é garantia do sistema, não limitação daqui.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request

# `STRUCTURA_BASE` aponta o caminhante para um topico do PORTAL:
#   STRUCTURA_BASE=http://127.0.0.1:8010/kc/kc_11 python scripts/caminhante.py
# Sem ela, o servidor de um topico so, na raiz, como sempre.
BASE = os.environ.get("STRUCTURA_BASE", "http://127.0.0.1:8010").rstrip("/")
PERSONAS = ("sabido", "aprende", "crente", "nao_sabe", "explica_mal",
            "duvida")

# O sinal de "não sei", devolvido por `escolhe` no lugar de um índice.
#
# Sentinela própria, e não `None`: `None` já significa "esta tela não tem
# alternativas", e sobrecarregá-lo faria o portão mandar `nao_sei` numa
# tela que só precisava de um `ms`.
NAO_SEI = "nao_sei"

# OS ESTADOS QUE NÃO SÃO FIM DE SESSÃO.
#
# Isto contava só `desconhecido` e `nao_medido`. Mas `refutado` (crença
# detectada, ainda não trabalhada) e `em_treino` (falta fechar a
# sequência) também são sessão parada no meio: a premissa não chegou a
# nenhum dos estados que a CS-10 promete, e o portão dizia "0 sem medida".
#
# `em_aberto` ficou FORA de propósito: o banco de itens acabou, e o
# projeto decidiu que isso é medida — é o que o pior caso roteirizado
# produz nos treze tópicos (`test_medida.py`). Contá-lo aqui faria o
# portão acusar o comportamento que ele próprio especifica.
SEM_MEDIDA = ("desconhecido", "nao_medido", "refutado", "em_treino")


def sem_medida(nos):
    """As premissas que terminaram a sessão sem estado nenhum dos cinco."""
    return [n["no"] for n in nos if n["estado"] in SEM_MEDIDA]


# OS EPISÓDIOS, e por que o portão passou a relatá-los.
#
# A quinta persona expôs um limite deste arquivo: a sessão do
# `explica_mal` termina com todos os nós `confirmado`, e está CORRETO —
# dois falsos positivos na mesma crença disparam `crenca_detectada`, vem
# refutação, vem treino, e o treino confirma. `falso_positivo` é
# transitório por desenho.
#
# Olhando só o estado final, o portão nunca poderia ter visto
# `falso_positivo` — nem quando ele acontece 36 vezes em três sessões. A
# conclusão "nenhuma persona produz falso_positivo" estava certa pelo
# motivo errado, e o instrumento trabalha justamente no meio.
#
# A fonte é o `veredito` que o servidor manda em TODA resposta: quem
# classifica é o motor, não o cliente, e é a mesma decisão que a tela
# mostra à pessoa.
VEREDITOS = ("certa", "errada", "falso_positivo", "crenca", "lacuna")

# Os eventos que o estado final apaga. Os dois primeiros dizem por qual
# PORTA a refutação entrou — pelo erro comum, ou por falso positivo
# repetido. `no_fragil` é da mesma família: um nó pode ficar frágil num
# momento e confirmar depois, e sem ele no relatório a persona que acerta
# duvidando seria invisível pelo mesmo motivo que a que explica mal era.
TRANSITORIOS = ("falso_positivo", "crenca_detectada", "no_fragil")


def episodios(vereditos):
    """Quantos episódios de cada tipo a sessão produziu.

    Passo sem veredito (ensino, refutação) não é episódio e sai fora.

    Os conhecidos vêm primeiro, na ordem de leitura; os DESCONHECIDOS
    vêm depois, e nunca calados. Filtrar pela lista que este arquivo
    conhece faria um veredito novo do motor sumir do relatório sem
    ninguém notar — que é o mesmo defeito que esta função existe para
    consertar, um nível acima.
    """
    c = collections.Counter(v for v in vereditos if v)
    resumo = {k: c.pop(k) for k in VEREDITOS if k in c}
    resumo.update(sorted(c.items()))
    return resumo


def _conta(resumo):
    """`{"certa": 30}` -> `"certa=30"`, na ordem recebida.

    A ordem vem de `episodios`, que põe os conhecidos antes dos
    desconhecidos de propósito — reordenar aqui desfaria isso.
    """
    return " ".join("%s=%d" % kv for kv in resumo.items())


def transitorios(eventos_por_passo):
    """Os eventos que o estado final apaga, contados pela sessão.

    Sem zeros de enchimento: sessão que não produziu nenhum não ganha
    linha no relatório.
    """
    c = collections.Counter(t for passo in eventos_por_passo for t in passo)
    return {k: c[k] for k in TRANSITORIOS if c[k]}


def _cala(atividade):
    """Se a persona `nao_sabe` diz "não sei" já na camada 1 deste item.

    Metade dos itens, decidida pelo id — não por sorteio. Um portão que
    muda de resultado sem o código mudar não serve de portão, e o motivo
    de não ser "sempre" está no docstring de `mvp/test_caminhante.py`: um
    "não sei" na camada 1 encerra o episódio, e a camada 2 — que é a que
    estava descoberta — nunca seria alcançada.
    """
    return hashlib.sha256(atividade.encode("utf-8")).digest()[0] % 2 == 0


def post(caminho, dados=None):
    req = urllib.request.Request(
        BASE + caminho, data=json.dumps(dados or {}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return r, (time.perf_counter() - t0) * 1000


def escolhe(tela, persona, chaves, sessao):
    """O índice da alternativa, pela persona.

    `sessao` é a SEMENTE: desde que a camada 1 é permutada, o índice
    da certa é posição de TELA, e sem a semente o andarilho não sabe
    mais qual é. Antes `gabarito` era `{id: posição no arquivo}`;
    agora é `{id: atividade}`, e a posição se calcula.
    """
    opcoes = [o["texto"] for o in tela.get("opcoes", [])]
    if not opcoes:
        return None
    gabarito, crencas, nos = chaves
    convencido = (
        persona == "sabido"
        or (persona == "aprende" and tela.get("fase") in ("TREINO", "RETESTE"))
        # A INCOERÊNCIA, de propósito: certa na camada 1, crença na
        # camada 2. É o único jeito de produzir `falso_positivo`, que é o
        # estado da CS-1 — e as quatro personas anteriores eram todas
        # internamente coerentes, de modo que nenhuma o produzia.
        or (persona == "explica_mal" and tela["tipo"] == "atividade")
        # `duvida` escolhe igual ao `sabido` nas DUAS camadas. O que a
        # separa é a camada 3, e só ela: `classifica` devolve `fragil` em
        # vez de `confirmada` quando a confiança fica abaixo de certeza.
        # É a única persona cuja diferença não está em escolha nenhuma.
        or persona == "duvida")
    if persona == "nao_sabe":
        # A camada 2 sempre, a camada 1 em metade dos itens. Quando ela
        # RESPONDE a camada 1, cai no caminho de quem não está convencido
        # logo abaixo — e erra, porque quem não sabe não acerta por sorte.
        if tela["tipo"] != "atividade" or _cala(tela.get("atividade") or ""):
            return NAO_SEI
    if tela["tipo"] == "atividade":
        a = gabarito.get(tela.get("atividade"))
        if a is None:
            return 0
        from mvp.motor import indice_correto_na_tela, opcoes_na_tela
        if convencido:
            return indice_correto_na_tela(sessao, a)
        # A CRENÇA DO ITEM, e não "a seguinte à certa".
        #
        # `(certa + 1) % n` era posição de arquivo, e dava na crença do
        # nó quase sempre por convenção de escrita: o YAML põe o
        # distrator do próprio nó logo depois do gabarito. Aplicada à
        # posição de TELA ela cai noutra crença em 1 de 5 itens, e a
        # refutação vai para o vizinho — o mesmo desvio que já foi
        # corrigido nas políticas de teste, e que aqui ficou para trás.
        # `a.crenca is not None` NÃO é defensividade: sem ele,
        # `o.crenca == a.crenca` vira `None == None` e casa a alternativa
        # CERTA — a persona que existe para errar acertava. Três itens dos
        # 562 têm crença nula, e um deles é de diagnóstico, onde acertar
        # cancela a refutação inteira. Ver `test_caminhante.py`.
        na_tela = opcoes_na_tela(sessao, a)
        return next((i for i, o in enumerate(na_tela)
                     if a.crenca is not None and o.crenca == a.crenca),
                    next((i for i, o in enumerate(na_tela) if not o.correta), 0))
    # camada 2: a razão certa é a fala do nó; as erradas são crenças
    crenta = [i for i, x in enumerate(opcoes) if x in crencas]
    certa = [i for i, x in enumerate(opcoes) if x in nos]
    if convencido:
        return certa[0] if certa else 0
    return crenta[0] if crenta else 0


def caminha(persona, chaves, codigo="", limite=400):
    r, ms = post("/sessoes", {"codigo": codigo} if codigo else None)
    sessao = r["sessao"]
    tempos = [ms]
    # O que o estado final apaga: o veredito de cada passo e os eventos
    # que ele provocou. Colhidos a cada resposta, porque `r` é sobrescrito
    # no laço e o fim da sessão não lembra do meio.
    vereditos, eventos = [], []
    for _ in range(limite):
        tela = r["tela"]
        tipo = tela["tipo"]
        if tipo == "mapa":
            break
        if tipo == "frase":
            corpo = {"texto": FRASES[persona][tela.get("momento", "inicio")],
                     "ms": 4000}
        elif tipo in ("ensino", "validacao", "refutacao"):
            corpo = {"ms": 2000}
        elif tipo == "confianca":
            corpo = {"confianca": CONFIANCA[persona], "ms": 1500}
        else:
            i = escolhe(tela, persona, chaves, sessao)
            corpo = ({"nao_sei": True, "ms": 3000} if i == NAO_SEI
                     else {"escolha": i, "ms": 3000})
        r, ms = post("/sessoes/%s/responder" % sessao, corpo)
        tempos.append(ms)
        vereditos.append(r.get("veredito"))
        eventos.append(r.get("eventos") or [])
    else:
        raise SystemExit("a unidade não terminou em %d passos" % limite)
    nos = r.get("grafo", {}).get("nos", [])
    return {
        "sessao": sessao,
        "passos": len(tempos),
        "tempos": tempos,
        "estados": [n["estado"] for n in nos],
        "sem_medida": sem_medida(nos),
        "episodios": episodios(vereditos),
        "transitorios": transitorios(eventos),
    }


# As frases do teach-back. Escritas como alguém escreveria, e diferentes
# entre começo e fim na persona que aprende: é o par que o mapa mostra.
FRASES = {
    "sabido": {
        "inicio": "é uma variável que guarda o endereço de outra variável",
        "fim": "uma variável cujo valor é o endereço de outra; são duas coisas separadas",
    },
    "aprende": {
        "inicio": "é tipo um atalho para outra variável, acho",
        "fim": "é uma caixa que guarda o endereço de outra caixa — duas caixas, não uma",
    },
    "crente": {
        "inicio": "é um jeito complicado de usar uma variável",
        "fim": "continuo achando que é a mesma variável com outro nome",
    },
    # Quem declara não saber escreve pouco, e no fim continua declarando:
    # a frase do teach-back dela não pode SOAR como aprendizagem, ou o par
    # antes-e-depois mente sobre o que a sessão produziu.
    "nao_sabe": {
        "inicio": "não sei, nunca entendi essa parte",
        "fim": "ainda não sei explicar, mas já sei onde eu travo",
    },
    # Quem acerta mal explicado soa seguro nas duas pontas, e é por isso
    # que o par antes-e-depois dela não mostra mudança: a resposta já
    # estava certa, e o que estava torto era a rota.
    "explica_mal": {
        "inicio": "é a variável que aponta pra outra, eu sei fazer isso",
        "fim": "é a variável que aponta pra outra, continuo sabendo fazer",
    },
    # Quem acerta duvidando escreve com ressalva nas duas pontas: o par
    # antes-e-depois dela mostra ganho de SEGURANÇA, não de conteúdo, e
    # essa distinção é o que o codebook vai ter de separar.
    "duvida": {
        "inicio": "acho que guarda um endereço, mas não tenho certeza",
        "fim": "guarda um endereço de outra variável — acho que é isso",
    },
}

# A camada 3. Quem declara não saber não tem certeza de nada — e `chutei`
# é o único valor que não contamina a medida de confiança dela.
#
# `explica_mal` vai com certeza total de propósito: `classifica` devolve
# `falso_positivo` para acerto com razão errada em QUALQUER confiança, e a
# certeza é o caso que mais exige do instrumento — alguém convicto de uma
# explicação torta.
#
# `duvida` vai com o MEIO da escala, e é a persona inteira: pela decisão
# 11 o meio puxa para o lado conservador de cada linha, e acerto com razão
# certa e confiança abaixo de certeza é `fragil`, não `confirmada`.
CONFIANCA = {"sabido": "tenho certeza", "aprende": "tenho certeza",
             "crente": "acho que sei", "nao_sabe": "chutei",
             "explica_mal": "tenho certeza", "duvida": "acho que sei"}


def main(argv):
    persona = "aprende"
    quantas = 1
    codigo = ""
    i = 0
    while i < len(argv):
        if argv[i] == "--persona" and i + 1 < len(argv):
            persona = argv[i + 1]; i += 2
        elif argv[i] == "--quantas" and i + 1 < len(argv):
            quantas = int(argv[i + 1]); i += 2
        elif argv[i] == "--codigo" and i + 1 < len(argv):
            codigo = argv[i + 1]; i += 2
        else:
            raise SystemExit(__doc__)
    if persona not in PERSONAS:
        raise SystemExit("persona: %s" % ", ".join(PERSONAS))

    sys.path.insert(0, ".")
    from mvp.dominio import carrega
    try:
        saude = json.loads(urllib.request.urlopen(BASE + "/saude", timeout=10).read())
    except (urllib.error.URLError, OSError):
        raise SystemExit("o servidor não está no ar: python -m mvp.app")
    d = carrega(topico=saude["topico"])
    chaves = ({a.id: a for a in d.atividades},
              {c.afirma for c in d.crencas.values()},
              {n.texto for n in d.nos.values()} | {n.simples for n in d.nos.values()})

    print("%s — %s" % (d.id, d.titulo))
    passos, sem = [], 0
    eps, trans = collections.Counter(), collections.Counter()
    for n in range(quantas):
        cod = codigo if quantas == 1 else ("%s%d" % (codigo, n + 1) if codigo else "")
        r = caminha(persona, chaves, cod)
        passos.append(r["passos"])
        sem += 1 if r["sem_medida"] else 0
        eps.update(r["episodios"])
        trans.update(r["transitorios"])
        marca = ("  SEM MEDIDA: " + ", ".join(r["sem_medida"])) if r["sem_medida"] else ""
        print("  %-11s %-14s %3d passos   %-28s  %s%s"
              % (persona, r["sessao"], r["passos"],
                 " ".join(sorted(set(r["estados"]))),
                 _conta(r["episodios"]), marca))
    if quantas > 1:
        print("  %d sessões: %d a %d passos (mediana %d) · %d com premissa sem medida"
              % (quantas, min(passos), max(passos),
                 statistics.median(passos), sem))
        # OS EPISÓDIOS, somados, e os transitórios por fora.
        #
        # O estado final apaga os dois transitórios, então eles vão numa
        # linha própria: é por ali que se vê por qual PORTA a refutação
        # entrou, e foi a cegueira que a quinta persona expôs.
        print("  episódios: %s" % (_conta(eps) or "nenhum"))
        if trans:
            print("  no meio:   %s" % _conta(trans))


if __name__ == "__main__":
    main(sys.argv[1:])
