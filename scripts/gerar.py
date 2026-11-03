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


def esquema_de_molde(d) -> dict:
    """O esquema do MOLDE. A mesma coleira: `crenca` é um enum dos ids
    que existem, e o modelo não tem como inventar concepção errônea."""
    ids = sorted(d.crencas)
    distrator = {
        "type": "object",
        "properties": {
            "texto": {"type": "string"},
            "crenca": {"type": "string", "enum": ids},
        },
        "required": ["texto", "crenca"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "formato": {"type": "string", "enum": list(FORMATOS)},
            "tipo": {"type": "string", "enum": list(TIPOS)},
            "parametros": {
                "type": "object",
                "description": "nome do parâmetro -> lista de valores",
                "additionalProperties": {"type": "array"},
            },
            "enunciado": {"type": "string"},
            "gabarito": {"type": "string"},
            "distratores": {"type": "array", "items": distrator},
            "oraculo": {"type": "string"},
            "espera": {"type": "string"},
            "por_que_este_oraculo": {"type": "string"},
        },
        "required": ["id", "formato", "tipo", "parametros", "enunciado",
                     "gabarito", "distratores", "oraculo", "espera",
                     "por_que_este_oraculo"],
        "additionalProperties": False,
    }


def prompt_de_molde(d, no: str, degrau: int) -> tuple[str, str]:
    """O pedido de um MOLDE, não de um item.

    Duas instruções que o pedido de item não tem, e que são a diferença
    entre escrever uma pergunta e escrever a fábrica dela: o gabarito é
    REGRA — sai dos parâmetros —, e existe um programa em C que prova a
    afirmação em toda variação.
    """
    sistema_item, _ = prompt(d, no, degrau, 1)
    sistema = sistema_item + """

AGORA O QUE MUDA: você não escreve um item. Escreve o MOLDE dele.

8. OS BURACOS. O enunciado, o gabarito e os distratores trazem buracos
   entre chaves — {tipo}, {nome}, {n} —, e cada buraco é um parâmetro
   com a sua lista de valores. {extenso} é derivado de {n} e dá o número
   por extenso ("cinco"); use-o quando a frase pedir a palavra.
9. O GABARITO É REGRA, NÃO TEXTO. Ele tem de sair certo para TODA
   combinação dos parâmetros. Se a sua afirmação só vale para alguns
   valores, estreite a lista daquele parâmetro — não escreva a regra
   errada e torça.
10. O ORÁCULO (campo `oraculo`). Escreva um programa em C completo
    que, compilado e
    executado com os MESMOS parâmetros, imprime exatamente o que o
    campo `espera` diz. Ele é o que prova a sua afirmação, variação por
    variação: se ela for falsa para algum valor, a máquina reprova o
    molde inteiro. Use os buracos dentro do programa; as chaves do C
    ficam como são.
11. A CONCORDÂNCIA tem de fechar em todas as variações: plural, gênero,
    acento. "uma caixa" e "oito caixas"; "a" e "dados"."""

    cx = contexto(d, no)
    pedido = f"""Tópico: {d.id} — {d.titulo}
Analogia do tópico: {d.analogia}

PREMISSA A MEDIR ({no})
  afirma: {cx['afirma']}
  em linguagem corrente: {cx['em_linguagem_corrente']}
  analogia deste nó: {cx['analogia_do_no']}
  código de apoio:
{cx['exemplo'] or '    (nenhum)'}

CRENÇA DO PRÓPRIO NÓ (obrigatória num dos distratores):
{json.dumps(cx['crenca_do_proprio_no'], ensure_ascii=False, indent=2)}

CRENÇAS DOS VIZINHOS (escolha uma):
{json.dumps(cx['crencas_dos_vizinhos'], ensure_ascii=False, indent=2)}

ITENS QUE JÁ EXISTEM NESTE NÓ — o molde não pode reproduzir nenhum:
{json.dumps(cx['itens_que_ja_existem'], ensure_ascii=False, indent=2)}

ESCREVA UM MOLDE no DEGRAU {degrau}, que pede:
{DEGRAUS[degrau]}

Formatos possíveis: {', '.join(FORMATOS)}.
O `id` começa com `mol_` e diz o tópico, o nó e o formato."""
    return sistema, pedido


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
# Os quatro portões do molde
# --------------------------------------------------------------------------

def _diz(parametros: dict) -> str:
    return ", ".join("%s=%s" % kv for kv in sorted(parametros.items())
                     if kv[0] != "extenso")


def _moldes(d, topico: str, raiz=None) -> dict:
    """Os moldes daquele tópico, do disco."""
    from mvp import molde as mod
    from mvp.dominio import RAIZ as DOMINIO

    base = pathlib.Path(raiz) if raiz else DOMINIO
    return mod.le(base / ("moldes_%s.yaml" % topico.replace("_", "")), d)


def expande_molde(d, topico: str, molde_id: str, raiz=None,
                  quantas: int = 6) -> tuple[list[dict], list[str]]:
    """As variações de um molde, ou os motivos de ele não servir.

    Quatro portões, do mais barato ao mais caro: expansão, oráculo,
    contrato e variedade. Qualquer problema devolve lista de itens VAZIA.

    O ORÁCULO REPROVA O MOLDE, NÃO A VARIAÇÃO. Descartar as reprovadas e
    ficar com as que passaram é como se esconde uma generalização
    indevida: o banco fica cheio de itens corretos sobre o caso que
    funciona — `char`, na sonda — e a afirmação falsa continua escrita no
    molde, esperando a próxima expansão. Conserta-se corrigindo a
    afirmação ou estreitando o domínio do parâmetro, e aí a restrição
    fica visível no arquivo.
    """
    from mvp import molde as mod
    from mvp.dominio import RAIZ as DOMINIO

    import oraculo

    base = pathlib.Path(raiz) if raiz else DOMINIO
    caminho = base / ("moldes_%s.yaml" % topico.replace("_", ""))
    try:
        moldes = mod.le(caminho, d)
    except mod.MoldeInvalido as erro:
        return [], list(erro.problemas)
    m = moldes.get(molde_id)
    if m is None:
        return [], ["molde %r não está em %s (há %s)"
                    % (molde_id, caminho.name, ", ".join(moldes) or "nenhum")]

    # 1. expansão
    variacoes = mod.expande(m, quantas)
    itens = [mod.item_de(m, p, i) for i, p in enumerate(variacoes, 1)]

    # 2. oráculo
    reprovadas = []
    for item, p in zip(itens, variacoes):
        ok, nota = oraculo.roda(mod.preenche(m.oraculo, p),
                                mod.preenche(m.espera, p))
        if not ok:
            reprovadas.append("%s (%s): %s" % (item["id"], _diz(p), nota))
    if reprovadas:
        return [], reprovadas + [
            "o molde %s está reprovado: %d de %d variações não conferem. "
            "Corrija a afirmação ou estreite o domínio do parâmetro — ficar "
            "com as que passaram esconde o erro" % (m.id, len(reprovadas),
                                                    len(itens))]

    # 3. contrato, pelo carregador de verdade
    problemas = confere(topico, itens)
    if problemas:
        return [], problemas

    # 4. variedade
    # Os itens que JÁ saíram deste molde não contam como plágio: eles
    # são a saída anterior dele. Sem isto, reexpandir depois de aprovar
    # acusava "mol_x_01: enunciado igual ao de mol_x_01".
    de_fora = {a.enunciado.strip(): a.id for a in d.atividades
               if a.do_molde != m.id}
    vistos: dict[str, str] = {}
    for item in itens:
        texto = item["enunciado"].strip()
        if texto in de_fora:
            problemas.append("%s: enunciado igual ao de %s"
                             % (item["id"], de_fora[texto]))
        if texto in vistos:
            problemas.append("%s: enunciado igual ao de %s, do mesmo molde"
                             % (item["id"], vistos[texto]))
        vistos[texto] = item["id"]
    if problemas:
        return [], problemas

    return itens, []


# --------------------------------------------------------------------------
# Ler, e aprovar
# --------------------------------------------------------------------------

def extremos(molde, quantas: int = 3) -> list[dict]:
    """As variações que a pessoa lê, escolhidas e não sorteadas.

    Os extremos do espaço de parâmetros — o menor e o maior número, o
    nome mais longo —, que é onde a concordância do português quebra:
    "uma caixa" contra "oito caixas", "a" contra "dados". Três sorteadas
    podem cair todas no meio e não mostrar nada.
    """
    from mvp.molde import expande

    todas = expande(molde, quantas=10 ** 6)
    if not todas:
        return []
    escolhidas: list[dict] = []

    def junta(p):
        if p is not None and p not in escolhidas:
            escolhidas.append(p)

    numericos = [k for k in molde.parametros
                 if all(isinstance(v, int) for v in molde.parametros[k])]
    if numericos:
        chave = numericos[0]
        junta(min(todas, key=lambda p: p[chave]))
        junta(max(todas, key=lambda p: p[chave]))
    textuais = [k for k in molde.parametros
                if all(isinstance(v, str) for v in molde.parametros[k])]
    if textuais:
        longo = max(textuais, key=lambda k: max(len(v)
                                                for v in molde.parametros[k]))
        junta(max(todas, key=lambda p: len(str(p[longo]))))
    for p in todas:
        if len(escolhidas) >= quantas:
            break
        junta(p)
    return escolhidas[:quantas]


def folha_do_molde(d, molde) -> str:
    """O molde como uma PESSOA lê, para preencher o `revisado_por`.

    O que ela confere aqui não é o que a máquina já conferiu. O oráculo
    garante que a afirmação é verdadeira em toda variação; o que fica
    para ela é se a frase fecha em português, se o distrator é a crença
    dita bem, e se a pergunta ensina alguma coisa.
    """
    from mvp.molde import item_de, preenche

    linhas = [
        "# Revisão do molde — %s" % molde.id,
        "",
        "Uma revisão deste arquivo vale por todas as variações dele. Para",
        "aprovar, escreva no molde as DUAS linhas abaixo — o nome diz quem",
        "leu, e a assinatura diz O QUE foi lido:",
        "",
        "```yaml",
        "  revisado_por: <seu nome>",
        "  revisado_sha: %s" % molde.digest,
        "```",
        "",
        "A assinatura é do conteúdo que está nesta folha. Se o molde mudar",
        "depois, ela deixa de bater e a carga recusa, em vez de estampar o",
        "seu nome em variações que você não leu. Depois:",
        "",
        "```bash",
        "python scripts/gerar.py --topico %s --molde %s --expandir"
        % (d.id, molde.id),
        "python scripts/gerar.py --topico %s --aprovar" % d.id,
        "```",
        "",
        "**O que a máquina já conferiu:** que o programa do oráculo compila,",
        "roda e imprime o que o molde promete, em TODA variação. O que fica",
        "para você é o resto:",
        "",
        "- a frase fecha em português em todas elas (plural, gênero, acento);",
        "- cada distrator é a crença **dita bem** — alguém escolheria aquilo;",
        "- o enunciado não entrega a resposta;",
        "- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue.",
        "",
        "---",
        "",
        "## O molde, como está escrito",
        "",
        "**nó %s** · degrau %d · %s · %s · uso %s"
        % (molde.no, molde.nivel, molde.formato, molde.tipo, molde.uso),
        "",
        "- enunciado: %s" % molde.enunciado,
        "- **[certa]** %s" % molde.gabarito,
    ]
    for texto, cid in molde.distratores:
        linhas.append("- [%s → nega %s] %s"
                      % (cid, d.crencas[cid].nega if cid in d.crencas else "?",
                         texto))
    linhas += [
        "",
        "parâmetros:",
        "",
    ]
    for nome, valores in molde.parametros.items():
        linhas.append("- `%s`: %s" % (nome, ", ".join(str(v) for v in valores)))
    linhas += [
        "",
        "oráculo (o que a máquina rodou), que espera `%s`:" % molde.espera,
        "",
        "```c",
        molde.oraculo.rstrip(),
        "```",
        "",
        "---",
        "",
        "## Três variações, dos extremos",
        "",
        "Não são sorteadas: são o menor e o maior número e o nome mais",
        "longo, que é onde a concordância quebra.",
        "",
    ]
    for i, p in enumerate(extremos(molde), 1):
        item = item_de(molde, p, i)
        linhas += [
            "### variação %d — %s" % (i, _diz(p)),
            "",
            item["enunciado"],
            "",
        ]
        for letra, texto in item["alternativas"].items():
            cid = item["crencas"].get(letra)
            if letra == item["gabarito"]:
                linhas.append("- **[certa]** %s" % texto)
            else:
                linhas.append("- [%s] %s" % (cid, texto))
        linhas.append("")
    return "\n".join(linhas) + "\n"


def folha(d, topico: str) -> str:
    """Os candidatos como uma PESSOA lê, não como YAML.

    Revisar item de instrumento de pesquisa é leitura, não diff: o que
    precisa ser conferido é se a pergunta mede o que diz medir, e isso não
    se vê em chave e valor.
    """
    import yaml

    pasta = CANDIDATOS / topico
    linhas = [
        "# Revisão dos candidatos — %s" % topico,
        "",
        "Leia item a item. Para aprovar, escreva seu nome em `revisado_por`",
        "no arquivo `.yaml` do nó e rode:",
        "",
        "```bash",
        "python scripts/gerar.py --topico %s --aprovar" % topico,
        "```",
        "",
        "Só entra no domínio o que tiver `revisado_por` preenchido.",
        "",
        "**O que conferir em cada item** (docs/linguagem.md):",
        "",
        "- a resposta certa está certa, e as erradas estão erradas;",
        "- cada distrator é a crença **dita bem** — alguém escolheria aquilo;",
        "- o enunciado não entrega a resposta;",
        "- o degrau bate: 1 responde na analogia, 2 aplica em C, 3 distingue;",
        "- o código compila e faz o que o enunciado diz.",
        "",
    ]
    total = 0
    for arq in sorted(pasta.glob("*.yaml")):
        no = arq.stem
        # O nome do arquivo é o id do nó, e esta folha agrupa por ele. O
        # `--expandir` escreve `mol_<...>.yaml` na mesma pasta: aquilo é
        # molde expandido, tem folha própria, e aqui só dava KeyError.
        if no not in d.nos:
            continue
        cru = yaml.safe_load(arq.read_text(encoding="utf-8"))["activities"]
        linhas += ["---", "", "## %s — %s" % (no, d.nos[no].simples), ""]
        for a in cru:
            total += 1
            linhas += [
                "### %s · degrau %d · %s · %s"
                % (a["id"], a["nivel"], a["formato"], a["tipo"]),
                "",
                a["enunciado"].strip(),
                "",
            ]
            if a.get("codigo"):
                linhas += ["```c", a["codigo"].rstrip(), "```", ""]
            for chave, texto in a["alternativas"].items():
                cid = a.get("crencas", {}).get(chave)
                if chave == a["gabarito"]:
                    linhas.append("- **[certa]** %s" % texto)
                elif cid:
                    linhas.append("- [%s → nega %s] %s"
                                  % (cid, d.crencas[cid].nega, texto))
                else:
                    linhas.append("- [SEM CRENÇA] %s" % texto)
            linhas += [
                "",
                "> %s" % a.get("por_que_este_distrator", ""),
                "",
                "`revisado_por:` %s" % (a.get("revisado_por") or "________"),
                "",
            ]
    linhas.insert(1, "")
    linhas.insert(2, "**%d itens**, em %d nós." % (total, len(list(pasta.glob('*.yaml')))))
    return "\n".join(linhas) + "\n"


def aprova(topico: str) -> tuple[int, list[str]]:
    """Move para o domínio só o que tem `revisado_por` preenchido.

    Confere ANTES de escrever: se o domínio com os aprovados dentro não
    carregar, não escreve nada. Meio banco gravado é pior do que nenhum.
    """
    import yaml

    from mvp.dominio import RAIZ as DOMINIO

    pasta = CANDIDATOS / topico
    aprovados, pendentes = [], []
    for arq in sorted(pasta.glob("*.yaml")):
        for a in yaml.safe_load(arq.read_text(encoding="utf-8"))["activities"]:
            (aprovados if (a.get("revisado_por") or "").strip()
             else pendentes).append(a)
    if not aprovados:
        return 0, ["nenhum item tem `revisado_por` preenchido"]

    problemas = confere(topico, aprovados)
    if problemas:
        return 0, problemas

    destino = DOMINIO / ("activities_%s.yaml" % topico.replace("_", ""))
    cru = yaml.safe_load(destino.read_text(encoding="utf-8"))
    ja = {x["id"] for x in cru.get("activities") or ()}
    novos = [a for a in aprovados if a["id"] not in ja]
    texto = destino.read_text(encoding="utf-8").rstrip("\n")
    bloco = yaml.safe_dump({"activities": novos}, allow_unicode=True,
                           sort_keys=False, width=78)
    # Acrescenta no fim, preservando os comentários do arquivo: um
    # safe_dump do arquivo inteiro apagaria o contrato escrito nele.
    bloco = "\n".join("  " + l if l.strip() and not l.startswith("activities:")
                      else l for l in bloco.split("\n"))
    bloco = bloco.replace("activities:\n", "", 1)
    destino.write_text(texto + "\n\n  # Aprovados em revisão.\n" + bloco,
                       encoding="utf-8", newline="\n")
    return len(novos), ["%d ainda sem revisão" % len(pendentes)] if pendentes else []


# --------------------------------------------------------------------------

def main(argv):
    import yaml

    topico, no, degrau, quantas, so_prompt = "kc_02", None, 1, 2, False
    importar, por_quem, acao = None, "", None
    molde_id = None
    i = 0
    while i < len(argv):
        if argv[i] == "--topico": topico = argv[i + 1]; i += 2
        elif argv[i] == "--molde": molde_id = argv[i + 1]; i += 2
        elif argv[i] == "--expandir": acao = "expandir"; i += 2 - 1
        elif argv[i] == "--no": no = argv[i + 1]; i += 2
        elif argv[i] == "--degrau": degrau = int(argv[i + 1]); i += 2
        elif argv[i] == "--quantas": quantas = int(argv[i + 1]); i += 2
        elif argv[i] == "--prompt": so_prompt = True; i += 1
        elif argv[i] == "--importar": importar = argv[i + 1]; i += 2
        elif argv[i] == "--por": por_quem = argv[i + 1]; i += 2
        elif argv[i] == "--revisar": acao = "revisar"; i += 1
        elif argv[i] == "--aprovar": acao = "aprovar"; i += 1
        else: raise SystemExit(__doc__)
    d = carrega(topico=topico)

    if acao == "expandir":
        if not molde_id:
            raise SystemExit("--expandir precisa de --molde <id>")
        itens, problemas = expande_molde(d, topico, molde_id)
        if problemas:
            for x in problemas:
                print("  -", x)
            raise SystemExit("o molde %s não passou nos portões." % molde_id)
        pasta = CANDIDATOS / topico
        pasta.mkdir(parents=True, exist_ok=True)
        alvo = pasta / ("%s.yaml" % molde_id)
        alvo.write_text(yaml.safe_dump({"activities": itens},
                                       allow_unicode=True, sort_keys=False,
                                       width=78),
                        encoding="utf-8", newline="\n")
        print("%d variação(ões) em %s" % (len(itens), alvo.relative_to(RAIZ)))
        return

    if acao == "revisar" and molde_id:
        moldes_do_topico = _moldes(d, topico)
        if molde_id not in moldes_do_topico:
            raise SystemExit("molde %s não está no tópico %s (há %s)"
                             % (molde_id, topico,
                                ", ".join(moldes_do_topico) or "nenhum"))
        pasta = CANDIDATOS / topico
        pasta.mkdir(parents=True, exist_ok=True)
        alvo = pasta / ("REVISAO-%s.md" % molde_id)
        alvo.write_text(folha_do_molde(d, moldes_do_topico[molde_id]),
                        encoding="utf-8", newline="\n")
        print("folha do molde em", alvo.relative_to(RAIZ))
        return

    if acao == "revisar":
        alvo = CANDIDATOS / topico / "REVISAO.md"
        alvo.write_text(folha(d, topico), encoding="utf-8", newline="\n")
        print("folha de revisão em", alvo.relative_to(RAIZ))
        return
    if acao == "aprovar":
        quantos, avisos = aprova(topico)
        for x in avisos:
            print("  -", x)
        if not quantos:
            raise SystemExit("nada foi movido.")
        print("%d item(ns) entraram em mvp/dominio/." % quantos)
        return

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
