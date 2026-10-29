"""Gera atividades candidatas para um nó, sob o contrato de linguagem.

    python scripts/gerar.py --topico kc_02 --no B2 --degrau 2 --quantas 2
    python scripts/gerar.py --topico kc_02 --no B2 --degrau 2 --prompt

O QUE ESTE PROGRAMA NÃO FAZ
---------------------------
Não gera **nó** nem **crença**. O grafo e o catálogo entram como dado
curado, e a crença de cada distrator sai de uma lista fechada — o esquema
da resposta só aceita ids que já existem. O modelo não tem como inventar
uma concepção errônea, que é justamente onde o instrumento perderia o
valor: a procedência (`provenance: D|L|T|E`) é afirmação sobre a
literatura, e isso não se gera.

O QUE ELE FAZ
-------------
Escreve o item: enunciado, alternativas, gabarito, e qual crença cada
distrator levanta. Depois **confere** o resultado com o carregador de
verdade, que é o mesmo que roda em sessão, e com as regras de
`docs/linguagem.md`.

Candidato **nunca** vira domínio sozinho: sai em `candidatos/`, e quem
move para `mvp/dominio/` é você.

    gerado por: modelo, data            <- fica no YAML
    revisado por: ____                  <- você preenche ao aprovar

Sem credencial da API, `--prompt` escreve o prompt num arquivo para você
colar onde quiser. O resto do programa — esquema, conferência, YAML —
funciona igual.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
import tempfile
from datetime import date

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mvp.dominio import FORMATOS, NIVEIS, TIPOS, DominioInvalido, carrega  # noqa: E402

MODELO = "claude-opus-5-5"
CANDIDATOS = RAIZ / "candidatos"

DEGRAUS = {
    1: "reconhecer a ideia que acabou de ser apresentada, NA ANALOGIA do "
       "tópico, antes de ser em C",
    2: "aplicar num caso concreto, em C, com o código à vista",
    3: "distinguir dois casos que parecem iguais, ou achar o erro, em C e "
       "sem apoio",
}


# --------------------------------------------------------------------------
# O que o modelo recebe
# --------------------------------------------------------------------------

def contexto(d, no: str) -> dict:
    """Tudo o que o item precisa saber, e nada do que ele não precisa."""
    n = d.nos[no]
    propria = [c for c in d.crencas.values() if c.nega == no]
    vizinhas = [c for c in d.crencas.values() if c.nega != no]
    return {
        "no": no,
        "afirma": n.texto,
        "em_linguagem_corrente": n.simples,
        "exemplo": d.exemplo(no),
        "analogia_do_no": d.resgate(no),
        "crenca_do_proprio_no": [
            {"id": c.id, "afirma": c.afirma} for c in propria],
        "crencas_dos_vizinhos": [
            {"id": c.id, "nega": c.nega, "afirma": c.afirma} for c in vizinhas],
        "itens_que_ja_existem": [
            {"id": a.id, "nivel": a.nivel, "formato": a.formato,
             "uso": a.uso, "enunciado": a.enunciado}
            for a in d.atividades_do_no(no)],
    }


def prompt(d, no: str, degrau: int, quantas: int) -> tuple[str, str]:
    """Devolve (sistema, pedido). O contrato vai inteiro no sistema."""
    sistema = """Você escreve itens de avaliação para um sistema que mede
mudança conceitual em programação. Escreve em português do Brasil, com
acentuação correta.

O CONTRATO (docs/linguagem.md), e ele não é negociável:

1. ALTERNATIVAS: três ou quatro. Nunca duas.
2. A CERTA NÃO PODE SER A MAIS LONGA. Conte os caracteres: se a correta
   passar de 20% do segundo maior, reescreva até emparelhar.
3. TODO DISTRATOR APONTA UMA CRENÇA da lista fechada que você recebe. Um
   distrator sem crença é erro sem diagnóstico.
4. Em todo item, UM distrator aponta a crença do PRÓPRIO nó e outro a de
   um VIZINHO. A do próprio nó é obrigatória: sem ela o nó nunca recebe
   atribuição e termina sem medida.
5. O ENUNCIADO NÃO DÁ PISTA: sem negativa ("qual NÃO..."), sem "sempre"
   ou "nunca" nas alternativas, sem "todas as anteriores", sem nome de
   pessoa (use "um colega").
6. A METÁFORA DO TÓPICO tem o direito de calar. Se ela obrigaria a dizer
   algo falso, escreva sem ela. Inventar uma concepção errônea nova é o
   pior defeito possível num instrumento que mede concepções errôneas.
7. O DEGRAU manda no que se pede e em que linguagem se pede.

Você NÃO inventa crença: só pode usar os ids que recebeu."""

    cx = contexto(d, no)
    pedido = f"""Tópico: {d.id} — {d.titulo}
Analogia do tópico: {d.analogia}

PREMISSA A MEDIR ({no})
  afirma: {cx['afirma']}
  em linguagem corrente: {cx['em_linguagem_corrente']}
  analogia deste nó: {cx['analogia_do_no']}
  código de apoio:
{cx['exemplo'] or '    (nenhum)'}

CRENÇA DO PRÓPRIO NÓ (obrigatória em todo item):
{json.dumps(cx['crenca_do_proprio_no'], ensure_ascii=False, indent=2)}

CRENÇAS DOS VIZINHOS (escolha uma por item):
{json.dumps(cx['crencas_dos_vizinhos'], ensure_ascii=False, indent=2)}

ITENS QUE JÁ EXISTEM NESTE NÓ — não repita enunciado nem molde:
{json.dumps(cx['itens_que_ja_existem'], ensure_ascii=False, indent=2)}

ESCREVA {quantas} item(ns) NOVO(S) no DEGRAU {degrau}, que pede:
{DEGRAUS[degrau]}

Formatos possíveis: {', '.join(FORMATOS)}.
Use `codigo` só quando o item mostrar código; senão deixe vazio."""
    return sistema, pedido


def esquema(d) -> dict:
    """O esquema da resposta. É aqui que a coleira aperta: `crenca` é um
    enum dos ids que existem, então o modelo não tem como inventar."""
    ids = sorted(d.crencas) + [""]
    alternativa = {
        "type": "object",
        "properties": {
            "chave": {"type": "string", "enum": ["a", "b", "c", "d"]},
            "texto": {"type": "string"},
            "crenca": {"type": "string", "enum": ids},
        },
        "required": ["chave", "texto", "crenca"],
        "additionalProperties": False,
    }
    atividade = {
        "type": "object",
        "properties": {
            "enunciado": {"type": "string"},
            "codigo": {"type": "string"},
            "formato": {"type": "string", "enum": list(FORMATOS)},
            "tipo": {"type": "string", "enum": list(TIPOS)},
            "alternativas": {"type": "array", "items": alternativa},
            "gabarito": {"type": "string", "enum": ["a", "b", "c", "d"]},
            "por_que_este_distrator": {"type": "string"},
        },
        "required": ["enunciado", "codigo", "formato", "tipo",
                     "alternativas", "gabarito", "por_que_este_distrator"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"atividades": {"type": "array", "items": atividade}},
        "required": ["atividades"],
        "additionalProperties": False,
    }


# --------------------------------------------------------------------------
# A chamada
# --------------------------------------------------------------------------

def gera(d, no: str, degrau: int, quantas: int) -> list[dict]:
    import anthropic

    sistema, pedido = prompt(d, no, degrau, quantas)
    cliente = anthropic.Anthropic()
    resposta = cliente.messages.create(
        model=MODELO,
        max_tokens=16000,
        system=sistema,
        thinking={"type": "adaptive"},
        output_config={"effort": "high",
                       "format": {"type": "json_schema", "schema": esquema(d)}},
        messages=[{"role": "user", "content": pedido}],
    )
    if resposta.stop_reason == "refusal":
        raise SystemExit("o modelo recusou: %s" % resposta.stop_details)
    texto = next(b.text for b in resposta.content if b.type == "text")
    return json.loads(texto)["atividades"]


# --------------------------------------------------------------------------
# O YAML, e a conferência
# --------------------------------------------------------------------------

def para_yaml(d, no: str, degrau: int, brutas: list[dict],
              por_quem: str = "") -> list[dict]:
    """A forma do banco, com a procedência do item junto.

    Cada item pode trazer o próprio `degrau`; sem isso vale o pedido.
    """
    saida = []
    for i, a in enumerate(brutas, 1):
        degrau = a.get("degrau", degrau)
        alternativas = {x["chave"]: x["texto"] for x in a["alternativas"]}
        crencas = {x["chave"]: x["crenca"] for x in a["alternativas"]
                   if x["crenca"] and x["chave"] != a["gabarito"]}
        saida.append({
            "id": "%s_g%s_n%d_%d" % (d.id.replace("_", ""), no.lower(), degrau, i),
            "node": "%s:%s" % (d.id.replace("_", ""), no),
            "nivel": degrau,
            "formato": a["formato"],
            "tipo": a["tipo"],
            "enunciado": a["enunciado"],
            "codigo": a["codigo"],
            "alternativas": alternativas,
            "gabarito": a["gabarito"],
            "crencas": crencas,
            # Procedência do ITEM, como as crenças já têm a delas. Vai para
            # o método do TCC: item gerado com assistência de modelo, sob
            # contrato declarado, e validado um a um por uma pessoa.
            "gerado_por": "%s em %s" % (por_quem or MODELO,
                                        date.today().isoformat()),
            "revisado_por": "",
            "por_que_este_distrator": a["por_que_este_distrator"],
        })
    return saida


def confere(topico: str, novas: list[dict]) -> list[str]:
    """Carrega o domínio COM os candidatos dentro, pelo carregador de
    verdade — o mesmo que roda em sessão —, e aplica as regras do contrato
    que o carregador não cobra."""
    import yaml

    from mvp.dominio import RAIZ as DOMINIO

    with tempfile.TemporaryDirectory() as tmp:
        destino = pathlib.Path(tmp) / "dominio"
        shutil.copytree(DOMINIO, destino)
        arq = destino / ("activities_%s.yaml" % topico.replace("_", ""))
        cru = yaml.safe_load(arq.read_text(encoding="utf-8"))
        limpas = [{k: v for k, v in a.items()
                   if k not in ("gerado_por", "revisado_por",
                                "por_que_este_distrator")}
                  for a in novas]
        cru["activities"] = (cru.get("activities") or []) + limpas
        arq.write_text(yaml.safe_dump(cru, allow_unicode=True, sort_keys=False),
                       encoding="utf-8")
        try:
            d = carrega(destino, topico=topico)
        except DominioInvalido as erro:
            return list(erro.problemas)

    problemas = []
    ids = {a["id"] for a in novas}
    for a in d.atividades:
        if a.id not in ids:
            continue
        if len(a.opcoes) < 3:
            problemas.append("%s: menos de três alternativas" % a.id)
        tams = sorted((len(o.texto), o.correta) for o in a.opcoes)
        segundo = tams[-2][0] if len(tams) > 1 else 0
        if tams[-1][1] and tams[-1][0] > segundo * 1.2:
            problemas.append("%s: a certa é a mais longa com folga" % a.id)
        sem = [o.texto[:40] for o in a.opcoes if not o.correta and not o.crenca]
        if sem:
            problemas.append("%s: distrator sem crença: %s" % (a.id, sem))
        if not any(o.crenca and d.crencas[o.crenca].nega == a.no
                   for o in a.opcoes):
            problemas.append(
                "%s: nenhum distrator aponta a crença do próprio nó" % a.id)
        baixo = [p for p in ("qual não", "sempre", "nunca", "todas as anteriores")
                 if p in a.enunciado.lower()]
        if baixo:
            problemas.append("%s: pista no enunciado: %s" % (a.id, baixo))
    return problemas


# --------------------------------------------------------------------------

def main(argv):
    import yaml

    topico, no, degrau, quantas, so_prompt = "kc_02", None, 1, 2, False
    importar, por_quem = None, ""
    i = 0
    while i < len(argv):
        if argv[i] == "--topico": topico = argv[i + 1]; i += 2
        elif argv[i] == "--no": no = argv[i + 1]; i += 2
        elif argv[i] == "--degrau": degrau = int(argv[i + 1]); i += 2
        elif argv[i] == "--quantas": quantas = int(argv[i + 1]); i += 2
        elif argv[i] == "--prompt": so_prompt = True; i += 1
        elif argv[i] == "--importar": importar = argv[i + 1]; i += 2
        elif argv[i] == "--por": por_quem = argv[i + 1]; i += 2
        else: raise SystemExit(__doc__)
    d = carrega(topico=topico)
    if no not in d.nos:
        raise SystemExit("nó: %s" % ", ".join(d.ordem))
    if degrau not in NIVEIS:
        raise SystemExit("degrau: %s" % ", ".join(map(str, NIVEIS)))

    pasta = CANDIDATOS / topico
    pasta.mkdir(parents=True, exist_ok=True)

    if so_prompt:
        sistema, pedido = prompt(d, no, degrau, quantas)
        alvo = pasta / ("%s-degrau%d.prompt.md" % (no, degrau))
        alvo.write_text(
            "# SISTEMA\n\n%s\n\n# PEDIDO\n\n%s\n\n# ESQUEMA DA RESPOSTA\n\n"
            "```json\n%s\n```\n"
            % (sistema, pedido, json.dumps(esquema(d), ensure_ascii=False, indent=2)),
            encoding="utf-8", newline="\n")
        print("prompt escrito em", alvo.relative_to(RAIZ))
        return

    if importar:
        # O mesmo esquema, vindo de fora: quem escreveu pode ter sido a API,
        # uma conversa, ou uma pessoa. A conferência é a mesma — e é ela
        # que decide se o item serve, não quem o escreveu.
        brutas = json.loads(pathlib.Path(importar).read_text(encoding="utf-8"))
        brutas = brutas["atividades"] if isinstance(brutas, dict) else brutas
        print("importando %d item(ns) de %s" % (len(brutas), importar))
        novas = para_yaml(d, no, degrau, brutas, por_quem)
    else:
        print("gerando %d item(ns) para %s:%s, degrau %d..."
              % (quantas, topico, no, degrau))
        novas = para_yaml(d, no, degrau, gera(d, no, degrau, quantas))
    alvo = pasta / ("%s-degrau%d.yaml" % (no, degrau) if not importar
                    else "%s.yaml" % no)
    alvo.write_text(yaml.safe_dump({"activities": novas}, allow_unicode=True,
                                   sort_keys=False, width=78),
                    encoding="utf-8", newline="\n")
    print("escrito em", alvo.relative_to(RAIZ))

    problemas = confere(topico, novas)
    if problemas:
        print("\nNAO PASSOU na conferência — %d problema(s):" % len(problemas))
        for p in problemas:
            print("   -", p)
        print("\nO arquivo fica para você olhar; não mova para mvp/dominio/.")
        raise SystemExit(1)
    print("\nconferido: carrega no domínio e passa nas regras do contrato.")
    print("Leia item a item, preencha `revisado_por` e mova para mvp/dominio/.")


if __name__ == "__main__":
    main(sys.argv[1:])
