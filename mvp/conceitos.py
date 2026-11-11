# -*- coding: utf-8 -*-
"""O inventário de conceitos, e o portão que ele controla.

O PRINCÍPIO: uma cadeia de refutação só pode ser acionada se todos os
seus degraus forem respondíveis com conhecimentos que o aluno já teve
oportunidade de aprender.

A MEDIÇÃO QUE O TORNOU NECESSÁRIO. Nas 180 detecções de crença da
varredura do kc_02, **135 acontecem no nível 1**, 99 delas depois de um
erro só. E a cadeia `pointer_has_no_address` pergunta sobre `sizeof p`,
que no tópico só aparece em item de **nível 2**, e sobre `int **pp`, que
só aparece em item de **nível 3**. A pessoa cai na descida antes de
encontrar qualquer um dos dois — e responde no chute um degrau que
deveria medir a crença dela.

"ESTÁ NO MATERIAL" É O CRITÉRIO ERRADO, e foi o meu. O certo tem duas
partes: o recurso aparece no tópico, E aparece em ENSINO. Item de prova
não autoriza o uso numa cadeia de recuperação — é por isso que
`so_avaliado` é um estado próprio, e não um sinônimo de disponível.

A LISTA COMEÇA VAZIA. Com ela vazia, nenhuma cadeia roda e o sistema cai
na refutação afirmativa em todo lugar. É conservador de propósito: uma
lista preenchida por suposição faria o portão medir a suposição de quem
a escreveu sobre a ementa da disciplina. A liberação é progressiva, uma
entrada por vez, e cada uma carrega a evidência de ONDE aquilo foi
ensinado — a rastreabilidade é o que separa isto de uma lista de desejos.
"""
from __future__ import annotations

import os
import pathlib
import re

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent / "dominio"
ARQUIVO = RAIZ / "conceitos.yaml"


def caminho() -> pathlib.Path:
    """O inventário em uso. `STRUCTURA_CONCEITOS` troca o arquivo.

    EXISTE PARA TESTE, e o princípio que o governa está escrito em
    `docs/processo.md`: um teste pode criar um mundo pedagógico explícito
    para exercitar o MECANISMO, e nunca pode transformar esse mundo
    artificial em evidência de que a disciplina ensinou aquilo. O portão
    continua rodando contra o inventário de verdade em
    `mvp/dominio/conceitos.yaml`, que começa vazio.
    """
    return pathlib.Path(os.environ.get("STRUCTURA_CONCEITOS") or ARQUIVO)

# Os quatro estados. A diferença entre os dois do meio é a que a medição
# do kc_02 produziu, e é a razão de este módulo existir.
DISPONIVEL = "disponivel"          # ensinado: pode ser exigido
SO_AVALIADO = "so_avaliado"        # cobrado em item, nunca ensinado
NAO_INTRODUZIDO = "nao_introduzido"  # não aparece ainda
DESCONHECIDO = "desconhecido"      # ninguém declarou: o padrão é NÃO
ESTADOS = (DISPONIVEL, SO_AVALIADO, NAO_INTRODUZIDO, DESCONHECIDO)

# A função pedagógica de cada degrau. Declarar obriga quem escreve a
# responder "o que esta pergunta faz?" antes de escrevê-la — e um degrau
# que não faz nenhuma das três provavelmente é dispensável.
EXPLICITAR = "explicitar"    # fazer assumir as consequências da crença
CONFRONTAR = "confrontar"    # apresentar o que não combina com ela
RECONSTRUIR = "reconstruir"  # ajudar a formular a compreensão melhor
FUNCOES = (EXPLICITAR, CONFRONTAR, RECONSTRUIR)

_cache: tuple[str, dict] | None = None


def recarrega() -> dict:
    """Esquece o inventário em memória.

    Para teste, e para quem editar o arquivo com o servidor no ar: sem
    isto, liberar um conceito exigiria reiniciar o processo.
    """
    global _cache
    _cache = None
    return carrega()


def carrega(onde: pathlib.Path | None = None) -> dict:
    """O inventário, do disco. Arquivo ausente é inventário vazio.

    O cache é guardado COM o caminho de onde veio: trocar
    `STRUCTURA_CONCEITOS` e receber o inventário anterior seria o tipo de
    silêncio que este módulo existe para não ter.
    """
    global _cache
    p = pathlib.Path(onde) if onde else caminho()
    if onde is None and _cache is not None and _cache[0] == str(p):
        return _cache[1]
    cru = {}
    if p.exists():
        cru = (yaml.safe_load(p.read_text(encoding="utf-8")) or {})
        cru = cru.get("conceitos") or {}
    inv = {}
    for cid, c in cru.items():
        c = c or {}
        inv[str(cid)] = {
            "nome": c.get("nome") or str(cid),
            "status": c.get("status") or DESCONHECIDO,
            "introduzido_em": c.get("introduzido_em") or "",
            "evidencia": c.get("evidencia") or "",
        }
    if onde is None:
        _cache = (str(p), inv)
    return inv


def status(cid: str) -> str:
    """O estado de um conceito. Id que ninguém declarou é DESCONHECIDO —
    o padrão é não, senão errar o nome do conceito viraria autorização."""
    return carrega().get(cid, {}).get("status", DESCONHECIDO)


def disponivel(cid: str) -> bool:
    return status(cid) == DISPONIVEL


# --------------------------------------------------------------------------
# Que cartão apresenta que conceito
# --------------------------------------------------------------------------
#
# O PRIMEIRO MECANISMO do histórico individual
# (`docs/historico-individual.md`): o log dizer que CONCEITO um cartão
# apresentou, e não só qual nó. `ensino_apresentado {no: B2}` não diz que
# aquele cartão ensina `ponteiro` e `sizeof` — isso é verdade deste
# arquivo, e o log não a tinha.
#
# A DECLARAÇÃO É DADO, NÃO VARREDURA. `evidencia.cartoes` é a forma
# legível por máquina do que a auditoria escreveu em `evidencia.onde`, e
# só quem tem `tipo` de explicação declara cartão: a auditoria de 05/11
# achou três falsos positivos de varredura por padrão, todos com o
# construto num exemplo que ensina outra coisa. Usar não é ensinar.


# Construto no CÓDIGO -> conceito do inventário. NUNCA aplicado à prosa:
# a primeira versão varria tudo junto, e o padrão de "função com
# parâmetro" casou com a frase "...de b / (a não foi tocado...".
#
# MORAVA EM `scripts/revisa_material.py`, e veio para cá em 09/11/2026
# porque deixou de ser conhecimento de script: é o mapa que diz o que um
# ITEM cobra, e a verificação de entrada do histórico individual
# (`mvp/historico.py`) precisa dele. O script continua importando daqui,
# para não haver duas listas.
#
# E ele é o oposto de `cartoes`, de propósito. Este diz o que um item
# COBRA, e varredura serve: o construto está no código ou não está.
# `cartoes` diz o que um cartão ENSINA, e ali varredura não serve — a
# auditoria de 05/11 achou três falsos positivos, todos com o construto
# num exemplo que ensina outra coisa. Cobrar é mecânico; ensinar não.
CONSTRUTOS = (
    (re.compile(r"\bsizeof\b"), "sizeof"),
    (re.compile(r"\bscanf\b"), "scanf"),
    (re.compile(r"%p"), "printf_ponteiro"),
    (re.compile(r"\*\s*\*"), "ponteiro_de_ponteiro"),
    (re.compile(r"\w+\s*\[\s*\d"), "array"),
    (re.compile(r"&\w+\s*==\s*&?\w+"), "comparacao_de_ponteiros"),
    # DEFINIÇÃO de função com parâmetro, e não CHAMADA de função.
    #
    # O padrão anterior pedia UM nome antes do parêntese, e por isso
    # acusava `puts(sizeof p > 0 ? ...)`: `puts` casava como nome de
    # função e `sizeof p` como "tipo seguido de nome de parâmetro". O
    # programa não define função nenhuma, e era barrado do portão de
    # exibição por um construto que não usa.
    #
    # O que separa os dois é simples e é o conserto: uma DEFINIÇÃO tem
    # tipo de retorno E nome antes do parêntese — `int soma(` são dois
    # nomes —, e uma CHAMADA tem um só. Daí o `\s+` obrigatório no
    # meio.
    (re.compile(r"^\s*[A-Za-z_]\w*[\w \*]*?\s+\**[A-Za-z_]\w*\s*\("
                r"\s*(?!void\s*\))[A-Za-z_]\w*\s+\**\w+", re.M),
     "funcao_com_parametro"),
)


def construtos_de(codigo: str | None) -> tuple[str, ...]:
    """Os conceitos que este código usa, pela varredura. Ordenados."""
    texto = codigo or ""
    return tuple(sorted({cid for padrao, cid in CONSTRUTOS
                         if padrao.search(texto)}))


def cartoes(cid: str) -> tuple[str, ...]:
    """Os cartões que apresentam este conceito, como `kc_02:B1`.

    Vazio para conceito que ninguém declarou, para o que só aparece em
    avaliação e para o que é usado sem explicação — e vazio é a resposta
    certa nos três casos.
    """
    ev = carrega().get(cid, {}).get("evidencia") or ""
    if not isinstance(ev, dict):
        return ()
    return tuple(str(c) for c in (ev.get("cartoes") or ()))


def do_cartao(topico: str, no: str) -> tuple[str, ...]:
    """O mapa inverso: os conceitos que ESTE cartão apresenta, ordenados.

    É o que o evento conceitual consulta. Ordenado por id para o log não
    depender da ordem do YAML — duas sessões do mesmo cartão têm de
    gravar a mesma lista.

    Devolve vazio para cartão sem declaração, que hoje são doze dos treze
    tópicos: a auditoria cobriu kc_00, kc_01 e kc_02. Vazio ali é o
    diagnóstico que interessa, não defeito a esconder.
    """
    alvo = "%s:%s" % (topico, no)
    return tuple(sorted(cid for cid in carrega() if alvo in cartoes(cid)))


def faltando(descida) -> tuple[str, ...]:
    """Os conceitos que a cadeia exige e que não estão disponíveis.

    Em ordem de primeira aparição, sem repetir: quem vai liberar precisa
    da lista, e ler a mesma entrada três vezes não ajuda.
    """
    vistos, falta = set(), []
    for p in descida.passos:
        for c in p.requer:
            if c not in vistos and not disponivel(c):
                vistos.add(c)
                falta.append(c)
    return tuple(falta)


def liberada(descida) -> bool:
    return not faltando(descida)


def faltando_para_exibir(codigo: str, topico: str) -> tuple[str, ...]:
    """Os construtos deste código que nenhum cartão do tópico ensina.

    MESMA REGRA DA `faltando`, outro insumo. Lá o requisito é declarado
    por quem escreveu a cadeia, no campo `requer`; aqui ele é VARRIDO do
    programa, porque quem escreve uma prova de premissa escreve para o
    examinador e não repara no que está ensinado.

    E O CARTÃO TEM DE SER DESTE TÓPICO. O `array` é `disponivel` e tem
    cartão — `kc_07:B1` —, e isso não ajuda quem está no kc_02: o tópico
    vem depois. Disponibilidade no inventário é condição necessária e
    não suficiente, e foi aceitá-la como suficiente que deixou passar o
    degrau de abertura reprovado em 05/11/2026.
    """
    fora = []
    for cid in construtos_de(codigo):
        if not any(str(c).startswith(topico + ":") for c in cartoes(cid)):
            fora.append(cid)
    return tuple(fora)


def exibivel(codigo: str, topico: str) -> bool:
    """Este programa pode ser mostrado a quem está neste tópico?

    Não é a mesma pergunta que "esta prova é válida". A prova bloqueada
    continua conferida pelo oráculo e continua valendo para o trabalho —
    ela só não vai para a tela da pessoa. Validar e exibir são duas
    perguntas, e confundi-las faria uma das duas mentir.
    """
    return not faltando_para_exibir(codigo, topico)


def relatorio(dominio) -> list[str]:
    """Uma linha por cadeia, dizendo se roda e o que falta para rodar.

    Bloqueio silencioso seria pior que bloqueio nenhum: com o inventário
    vazio TUDO para, e quem lê precisa saber qual conceito liberar para
    destravar qual cadeia.
    """
    linhas = []
    for cid in sorted(dominio.descidas):
        de = dominio.descidas[cid]
        falta = faltando(de)
        linhas.append(
            "crenca %-28s liberada=%-5s falta=%s"
            % (cid, de.liberada, ", ".join(falta) if falta else "-"))
    return linhas
