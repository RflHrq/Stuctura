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

import json
import statistics
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8010"
PERSONAS = ("sabido", "aprende", "crente")


def post(caminho, dados=None):
    req = urllib.request.Request(
        BASE + caminho, data=json.dumps(dados or {}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return r, (time.perf_counter() - t0) * 1000


def escolhe(tela, persona, chaves):
    """O índice da alternativa, pela persona."""
    opcoes = [o["texto"] for o in tela.get("opcoes", [])]
    if not opcoes:
        return None
    gabarito, crencas, nos = chaves
    convencido = persona == "sabido" or (
        persona == "aprende" and tela.get("fase") in ("TREINO", "RETESTE"))
    if tela["tipo"] == "atividade":
        certa = gabarito.get(tela.get("atividade"))
        if convencido:
            return certa if certa is not None else 0
        return (certa + 1) % len(opcoes) if certa is not None else 0
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
            corpo = {"confianca": "tenho certeza" if persona != "crente"
                     else "acho que sei", "ms": 1500}
        else:
            corpo = {"escolha": escolhe(tela, persona, chaves), "ms": 3000}
        r, ms = post("/sessoes/%s/responder" % sessao, corpo)
        tempos.append(ms)
    else:
        raise SystemExit("a unidade não terminou em %d passos" % limite)
    nos = r.get("grafo", {}).get("nos", [])
    return {
        "sessao": sessao,
        "passos": len(tempos),
        "tempos": tempos,
        "estados": [n["estado"] for n in nos],
        "sem_medida": [n["no"] for n in nos
                       if n["estado"] in ("desconhecido", "nao_medido")],
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
}


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
    chaves = ({a.id: a.indice_correto for a in d.atividades},
              {c.afirma for c in d.crencas.values()},
              {n.texto for n in d.nos.values()} | {n.simples for n in d.nos.values()})

    print("%s — %s" % (d.id, d.titulo))
    passos, sem = [], 0
    for n in range(quantas):
        cod = codigo if quantas == 1 else ("%s%d" % (codigo, n + 1) if codigo else "")
        r = caminha(persona, chaves, cod)
        passos.append(r["passos"])
        sem += 1 if r["sem_medida"] else 0
        marca = ("  SEM MEDIDA: " + ", ".join(r["sem_medida"])) if r["sem_medida"] else ""
        print("  %-8s %-14s %3d passos   %s%s"
              % (persona, r["sessao"], r["passos"],
                 " ".join(sorted(set(r["estados"]))), marca))
    if quantas > 1:
        print("  %d sessões: %d a %d passos (mediana %d) · %d com premissa sem medida"
              % (quantas, min(passos), max(passos),
                 statistics.median(passos), sem))


if __name__ == "__main__":
    main(sys.argv[1:])
