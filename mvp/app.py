"""O MVP no ar: três rotas e a interface.

    python -m mvp.app     →  http://127.0.0.1:8010

A interface não decide nada: ela recebe a próxima tela e desenha. Toda
transição acontece no motor, e o que acontece vira evento no log.

O estado da sessão vive em memória, num dicionário por sessão — e o
dicionário é só um atalho. A fonte é o log: se o processo reinicia no meio
de uma coleta, a sessão que chegar sem estado na memória é reexecutada a
partir dele (`_retoma`). Numa coleta de 10 a 15 pessoas, perder uma é
perder 7%, e a pessoa não volta para repetir.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from mvp import log, motor
from mvp.dominio import Dominio, carrega

AQUI = Path(__file__).resolve().parent

app = FastAPI(title="Structura MVP — treino até domínio")
dominio = carrega()
sessoes: dict[str, motor.Estado] = {}


# Teto do teach-back. Não é limite de pensamento: duas ou três frases é o
# que a pergunta pede, e 2.000 caracteres cabem com folga. O limite existe
# porque isto é DADO PESSOAL escrito em disco — sem teto, uma colagem
# acidental põe meio megabyte de sabe-se lá o quê no log da coleta.
LIMITE_DA_FRASE = 2000

# Um episódio inteiro leva minutos, não horas. O teto corta número
# impossível antes de ele entrar na base de análise; `ge=0` corta o
# negativo, que não é tempo.
LIMITE_MS = 2 * 60 * 60 * 1000


class RespostaBody(BaseModel):
    escolha: int | None = None
    confianca: str = ""
    ms: int = Field(default=0, ge=0, le=LIMITE_MS)
    # "ainda não entendi" num passo da refutação: pede a premissa de novo.
    repetir: bool = False
    # "não sei", em qualquer das três camadas.
    nao_sei: bool = False
    # Texto livre do teach-back. DADO PESSOAL: vai para o log com o código
    # da sessão, nunca com nome.
    texto: str = Field(default="", max_length=LIMITE_DA_FRASE)


# AS FASES EM QUE O SISTEMA ENSINA, e são as únicas que explicam o erro.
#
# Erro de diagnóstico e de reteste é EVIDÊNCIA: é dele que sai a crença, e
# é dele que sai a medida de transferência. Explicar ali ensina no meio da
# medição e contamina os itens seguintes da MESMA sessão. Quem erra no
# diagnóstico com crença detectada já recebe a refutação, que é o
# mecanismo da tese; quem erra sem detecção segue sem explicação de
# propósito, e isso está medido e registrado como pendência.
ENSINA = ("treino", "entrada")


def _explica_erro(d: Dominio, semente: str, dados: dict) -> dict | None:
    """A explicação do erro, MONTADA do domínio — nunca redigida.

    Dois textos, e os dois são cadastrados palavra por palavra: a fala da
    crença que a alternativa escolhida afirma, e o enunciado da premissa
    da pergunta. A frase que liga as duas é do cliente e não varia com o
    conteúdo, então não existe lugar por onde uma justificativa inventada
    entre.

    `contradiz` é o terceiro ingrediente, e é um FATO do domínio, não um
    rótulo: a crença escolhida nega esta premissa ou nega outra. Medido
    nos treze tópicos, 512 das 1.101 alternativas erradas com crença — 46%
    — negam OUTRO nó. Afirmar "e isso contradiz" sem olhar seria falso em
    quase metade das telas, o mesmo defeito que a caixa de contraste da
    refutação já teve.

    E nada disto precisou de campo novo no log: a alternativa clicada é
    RECUPERADA de `atividade` + `escolha`, que o `resposta_registrada` já
    gravava, porque `opcoes_na_tela` é determinística desde a fatia da
    posição. A versão do log continua 3.
    """
    no = dados.get("no")
    if no not in d.nos:
        return None
    i = dados.get("escolha")
    # Quem declarou "não sei", ou não respondeu, não escolheu alternativa
    # nenhuma: não há ideia dela para nomear. O veredito desse caso é
    # `lacuna`, e tem retorno próprio.
    if not isinstance(i, int) or isinstance(i, bool):
        return None
    a = next((x for x in d.atividades if x.id == dados.get("atividade")), None)
    if a is None:
        return None
    na_tela = motor.opcoes_na_tela(semente, a)
    if not 0 <= i < len(na_tela):
        return None
    cid = na_tela[i].crenca or ""
    tem = cid in d.crencas
    return {
        "premissa": d.nos[no].simples,
        # Vazio quando a alternativa é distrator plausível sem crença
        # catalogada — 10 das 1.111 nos treze tópicos. O sistema não sabe
        # por onde a pessoa foi, e calar é o que a regra manda.
        "escolheu": d.crencas[cid].afirma if tem else "",
        "contradiz": bool(tem and d.crencas[cid].nega == no),
        # O `no` havia sido tirado deste retorno com a justificativa de que
        # campo que ninguém lê é campo que ninguém confere. Ele volta COM
        # USO: o banco de figuras é do cliente e é indexado por nó, e é por
        # este campo que o desenho da premissa é escolhido. Quem garante
        # que o uso existe na tela, e não só no JSON, é o
        # `test_o_cliente_le_todos_os_campos_que_o_servidor_monta`.
        "no": no,
        # A analogia DAQUELE NÓ, e nunca `d.resgate(no)`: esse acessador cai
        # no resumo do tópico quando o nó não tem versão própria, e o resumo
        # mapeia as cinco premissas de uma vez — na tela de um erro de
        # treino ele entregaria a resposta de atividade ainda não feita. Nó
        # sem versão própria sai sem analogia, e a tela esconde a linha.
        # Medido: 79 de 79 têm a própria, então hoje a tela nunca cala.
        "resgate": d.resgates.get(no, ""),
    }


def _resposta(sessao: str, t: motor.Transicao,
              entrada: motor.Resposta | None = None) -> dict:
    """A transição, pronta para desenhar.

    `veredito` vem daqui, e não do cliente: quem decide se a resposta foi
    certa, e se o retorno deve ser neutro, é o motor. O front não pode
    inferir isso de tipos de evento — seria regra no lugar errado.

    A entrada vai junto para o log, antes dos eventos que ela provocou: é
    o que permite reexecutar a sessão depois de uma queda.
    """
    sessoes[sessao] = t.estado
    log.grava(sessao, t.eventos, entrada=entrada)

    resposta = next((e for e in t.eventos if e.tipo == "resposta_registrada"), None)
    crenca = next((e for e in t.eventos if e.tipo == "crenca_detectada"), None)
    lacuna = next((e for e in t.eventos if e.tipo == "lacuna_registrada"
                   and e.dados.get("declarada")), None)
    falso = next((e for e in t.eventos if e.tipo == "falso_positivo"), None)
    vacilo = next((e for e in t.eventos if e.tipo == "vacilo_detectado"), None)
    veredito = None
    if crenca is not None:
        veredito = "crenca"        # retorno NEUTRO: a refutação é que ensina
    elif falso is not None:
        # Decisão 13: contar. Calar desperdiça o único momento em que a
        # pessoa percebe que acertou por um caminho que não leva ali.
        veredito = "falso_positivo"
    elif lacuna is not None:
        veredito = "lacuna"        # ela DISSE que não sabe: não é erro
    elif vacilo is not None:
        # O ESCORREGÃO: errou a resposta e enunciou a razão certa. O motor
        # já concluía isso — classifica como `falso_negativo`, grava
        # `vacilo_detectado`, marca `vacilou` no nó — e a tela era o único
        # lugar que não sabia: 79 de 79 liam "Ainda não. Olhe de novo com
        # calma", o mesmo texto de quem tem um mal-entendido.
        #
        # Isto acontece no DIAGNÓSTICO, que mede, e a regra é que ali o
        # sistema não fala. A justificativa da regra é literal — explicar
        # ali ENSINA no meio da medição —, e nomear um escorregão não
        # ensina: `retorno` continua None, então não existe caminho por
        # onde premissa, crença ou figura cheguem à tela. A frase é do
        # cliente e não varia com o conteúdo. O falso positivo, na mesma
        # fase, já diz mais do que isto desde a Decisão 13.
        #
        # O CUSTO, medido: a pessoa fica sabendo que a razão marcada era a
        # certa, e o mesmo nó volta três passos depois em 153 de 158 casos.
        # Está em docs/processo.md como decisão metodológica.
        veredito = "escorregao"
    elif resposta is not None:
        veredito = "certa" if resposta.dados.get("correta") else "errada"

    # O contraste do falso positivo vem montado do domínio, não do cliente:
    # a frase da crença e o enunciado do nó que ela nega.
    retorno = None
    if falso is not None:
        cid = falso.dados.get("crenca")
        alvo = falso.dados.get("fala_do_no")
        if cid in dominio.crencas and alvo in dominio.nos:
            retorno = {
                "crenca": dominio.crencas[cid].afirma,
                "contradiz": dominio.nos[alvo].simples,
                "no": alvo,
                "vezes": falso.dados.get("vezes"),
            }

    # O ERRO QUE EXPLICA. Antes daqui a tela do erro simples dizia "Ainda
    # não. Olhe de novo com calma" e mais nada — 79 vezes por varredura dos
    # treze tópicos, e 24 numa sessão de kc_02 de quem erra. O material
    # estava no domínio desde sempre; faltava montar.
    if (retorno is None and veredito == "errada"
            and resposta.dados.get("fase") in ENSINA):
        retorno = _explica_erro(dominio, t.estado.semente, resposta.dados)

    return {
        "sessao": sessao,
        "tela": t.tela.json(),
        "veredito": veredito,
        "retorno": retorno,
        # O grafo vai em TODA resposta, não só no fim: ele fica à vista
        # durante a unidade, e o aluno acompanha a cadeia se erguendo.
        "grafo": {"nos": motor.estado_dos_nos(dominio, t.estado),
                  "foco": t.tela.no or t.estado.alvo},
        "eventos": [e.tipo for e in t.eventos],
    }


# O código do participante, quando quem abre a sessão informa um. É o
# identificador do PRD — P01…P40, sem nome — e é por ele que o pedido de
# exclusão acha as linhas. Formato estreito de propósito: ele vai para o
# nome de nada, mas vai para a URL e para toda linha do log, e código com
# espaço ou barra é confusão garantida na hora de apagar.
CODIGO = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,15}$")


class SessaoBody(BaseModel):
    codigo: str = ""


@app.post("/sessoes")
def cria_sessao(body: SessaoBody | None = None) -> dict:
    """Sem código informado, um hex aleatório, como sempre foi."""
    codigo = (body.codigo if body else "").strip()
    if codigo:
        if not CODIGO.match(codigo):
            raise HTTPException(
                status_code=400,
                detail="código fora do formato: letra, depois letras, "
                       "números, hífen ou _, até 16")
        # Abrir duas vezes o mesmo código juntaria duas pessoas num
        # participante só, e a análise não teria como separar depois.
        # Tolerante de propósito: uma linha ilegível no arquivo não pode
        # impedir o começo de uma sessão.
        linhas, _ = log.le_tolerante()
        if any(x.get("sessao") == codigo for x in linhas):
            raise HTTPException(
                status_code=409,
                detail="já existe sessão com o código %r neste log" % codigo)
        sessao = codigo
    else:
        sessao = uuid.uuid4().hex[:12]
    # A sessão é a semente da ordem das razões: o motor continua puro, e
    # recarregar a página não reembaralha as alternativas debaixo da pessoa.
    return _resposta(sessao, motor.inicia(dominio, semente=sessao))


def _retoma(sessao: str) -> motor.Estado:
    """Uma sessão que o servidor não tem mais na memória volta pelo log.

    O caso é o servidor ter sido reiniciado no meio de uma coleta: a
    página de quem responde continua aberta, e a próxima resposta precisa
    cair no estado certo em vez de num 404.

    A retomada vira uma linha no log — não é um detalhe de operação: uma
    sessão que teve queda no meio não é igual às outras, e a análise
    precisa poder ver isso sem perguntar a ninguém.
    """
    try:
        t = log.reconstroi(dominio, sessao)
    except log.LogIncompleto as erro:
        # 409: a sessão existe, e este servidor não consegue continuá-la.
        # Dizer 404 esconderia um log que precisa de atenção humana.
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    if t is None:
        raise HTTPException(status_code=404, detail="sessão desconhecida")
    sessoes[sessao] = t.estado
    log.grava(sessao, (motor.Evento("sessao_retomada",
                                    {"fase": t.estado.fase}),))
    return t.estado


@app.post("/sessoes/{sessao}/responder")
def responde(sessao: str, body: RespostaBody) -> dict:
    estado = sessoes.get(sessao)
    if estado is None:
        estado = _retoma(sessao)
    if body.confianca and body.confianca not in motor.CONFIANCAS:
        raise HTTPException(status_code=400, detail="confiança fora da escala")
    r = motor.Resposta(escolha=body.escolha, confianca=body.confianca, ms=body.ms,
                       repetir=body.repetir, nao_sei=body.nao_sei,
                       texto=body.texto)
    try:
        t = motor.avanca(dominio, estado, r)
    except motor.EscolhaInvalida as erro:
        # 400, e não 500: o pedido é que está errado. Antes disto um
        # índice negativo devolvia 200 e virava um episódio de verdade —
        # o defeito que a revisão do ciclo 1 achou. Nada é gravado: a
        # tentativa inválida não é dado, e o estado não anda.
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    return _resposta(sessao, t, entrada=r)


@app.get("/saude")
def saude() -> dict:
    return {
        "ok": True,
        "topico": dominio.id,
        "titulo": dominio.titulo,
        "nos": len(dominio.nos),
        "crencas": len(dominio.crencas),
        "atividades": len(dominio.atividades),
        "streak_alvo": motor.STREAK_ALVO,
        "teto_tentativas": motor.TETO_TENTATIVAS,
        "limite_da_frase": LIMITE_DA_FRASE,
    }


@app.get("/")
def raiz() -> FileResponse:
    return FileResponse(AQUI / "web" / "index.html")


app.mount("/web", StaticFiles(directory=AQUI / "web"), name="web")


def main() -> None:
    import uvicorn

    print("Structura MVP — %s (%s)" % (dominio.titulo, dominio.id))
    print("  nós %d · crenças %d · atividades %d"
          % (len(dominio.nos), len(dominio.crencas), len(dominio.atividades)))
    print("  streak para confirmar: %d · teto de tentativas: %d"
          % (motor.STREAK_ALVO, motor.TETO_TENTATIVAS))
    print("  http://127.0.0.1:8010")
    uvicorn.run(app, host="127.0.0.1", port=8010, log_level="warning")


if __name__ == "__main__":
    main()
