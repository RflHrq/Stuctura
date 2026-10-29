"""O painel do pesquisador: só leitura, e só do log.

    python -m mvp.painel     →  http://127.0.0.1:8011

Processo SEPARADO do que atende quem responde (decisão 10). Três razões,
em ordem de peso:

1. o painel não pode derrubar a sessão de quem está pensando em voz alta —
   um erro meu numa consulta não pode custar um participante;
2. o log é append-only, então ler é seguro por construção;
3. assim o painel funciona depois de um travamento, que é quando ele é
   mais necessário.

Por isso este arquivo **não importa `mvp.app`**, e não existe caminho
daqui até o dicionário de sessões. Tem teste para isso: é o CS-7, e é a
única garantia que não depende de eu lembrar.

O efeito colateral é a melhor parte: se o painel só lê o log, o log tem de
bastar. O painel é a prova de que basta — tudo o que ele desenha saiu de
`mvp/dados/eventos.jsonl` e de mais nada.

SOBRE DADO PESSOAL (portão G)
-----------------------------
As frases do teach-back são texto livre escrito pelo participante. Elas
aparecem **só na tela de uma sessão**, nunca na lista: uma tela com o
texto de quarenta pessoas de uma vez não serve a nada que este estudo
precise, e existir já é risco. A identificação é só o código da sessão.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from mvp import log, motor
from mvp.dominio import carrega

AQUI = Path(__file__).resolve().parent

app = FastAPI(title="Structura — painel do pesquisador")
dominio = carrega()

# Quanto do log cru a tela mostra. O arquivo inteiro de uma coleta não
# cabe numa tela nem ajuda: o que interessa ao vivo é o fim dele.
CAUDA = 40


# --------------------------------------------------------------------------
# As leituras, puras: função de (linhas do log) → o que a tela desenha
# --------------------------------------------------------------------------

def episodios(linhas: list[dict]) -> list[dict]:
    """A saída do instrumento, episódio a episódio.

    Cada linha da tabela é uma atividade respondida, com as três camadas
    lado a lado e o tempo de cada uma. É o dado do TCC: sem isto o painel
    seria um log bonito, e o pesquisador continuaria contando a mão.

    Montado dos eventos, não do estado: o estado diz onde a pessoa chegou,
    e esta tabela diz por onde ela passou.
    """
    saida: list[dict] = []
    atual: dict = {}

    def fecha():
        if atual:
            atual["ordem"] = len(saida) + 1
            saida.append(dict(atual))
            atual.clear()

    for linha in linhas:
        tipo = linha["tipo"]
        if tipo == "camada1_respondida":
            # A camada 1 abre um episódio e fecha o anterior. Fechar no
            # `resposta_registrada` seria cedo demais: a classificação e o
            # resultado do treino vêm logo DEPOIS dele.
            fecha()
            atual.update({
                "no": linha.get("no"), "atividade": linha.get("atividade"),
                "item": linha.get("item"), "fase": linha.get("origem"),
                "correta": linha.get("correta"),
                "ms_resposta": linha.get("ms"),
                "nao_sei": "camada1" if linha.get("nao_sei") else "",
                "razao_correta": None, "crenca": None, "fala_do_no": None,
                "ms_razao": None, "confianca": "", "ms_confianca": None,
                "estado": "", "streak": None,
                "voltou": None, "superficie_nova": None,
            })
        elif tipo == "razao_pulada" and atual:
            atual["razao_correta"] = None
            atual["crenca"] = "(item sem crença nas alternativas)"
        elif tipo == "camada2_respondida" and atual:
            atual["razao_correta"] = linha.get("razao_correta")
            atual["crenca"] = linha.get("crenca")
            atual["fala_do_no"] = linha.get("fala_do_no")
            atual["ms_razao"] = linha.get("ms")
            if linha.get("nao_sei"):
                atual["nao_sei"] = "camada2"
        elif tipo == "camada3_respondida" and atual:
            atual["confianca"] = linha.get("confianca")
            atual["ms_confianca"] = linha.get("ms")
            if linha.get("nao_sei"):
                atual["nao_sei"] = "camada3"
        elif tipo == "episodio_classificado" and atual:
            atual["estado"] = linha.get("estado")
        elif tipo == "treino_tentativa" and atual:
            atual["streak"] = linha.get("streak")
        elif tipo == "belief_retested" and atual:
            # A linha mais importante da tabela para o TCC: a terceira
            # condição do critério, "não volta".
            atual["voltou"] = linha.get("voltou")
            atual["superficie_nova"] = linha.get("superficie_nova")
            atual["crenca"] = linha.get("crenca")
        elif tipo == "unidade_encerrada":
            fecha()
    fecha()
    return saida


def _resumo(linhas: list[dict]) -> dict:
    """O que dá para dizer de uma sessão sem reexecutar nada."""
    abertura = next((x for x in linhas if x["tipo"] == "unidade_iniciada"), None)
    fim = next((x for x in linhas if x["tipo"] == "unidade_encerrada"), {})
    return {
        # Quantas crenças foram refutadas e quantas chegaram a voltar. A
        # diferença é o que o banco de itens não deu, e precisa estar à
        # vista: um reteste que não aconteceu é uma condição do critério
        # que ficou sem medida nesta sessão.
        "refutadas": fim.get("refutadas", 0),
        "retestadas": fim.get("retestadas", 0),
        "sem_item": sum(1 for x in linhas if x["tipo"] == "reteste_sem_item"),
        "codigo": linhas[0]["sessao"],
        "topico": (abertura or {}).get("topico", ""),
        "inicio": linhas[0].get("ts", ""),
        "ultimo": linhas[-1].get("ts", ""),
        "linhas": len(linhas),
        "respostas": sum(1 for x in linhas if x["tipo"] == log.ENTRADA),
        "retomadas": sum(1 for x in linhas if x["tipo"] == "sessao_retomada"),
        "encerrada": any(x["tipo"] == "unidade_encerrada" for x in linhas),
    }


def _reexecutavel(linhas: list[dict]) -> tuple[bool, str]:
    """A mesma recusa de `log.reconstroi`, sem reexecutar nada.

    São as duas condições que `reconstroi` confere ANTES do primeiro
    passo: existir abertura do tópico carregado, e existir entrada quando
    a sessão andou. Conferi-las é ler três campos; reexecutar para
    descobrir o mesmo é refazer a sessão inteira.

    **É uma aproximação, de propósito.** Uma sessão pode passar por aqui
    e ainda assim falhar ao ser aberta — é o caso de um log antigo com
    uma entrada que o motor de hoje recusa, que só aparece reexecutando.
    Quem decide é o detalhe, que reexecuta e diz o motivo; a lista
    adianta o que dá para adiantar sem custar uma sessão por pedido.
    """
    abertura = next((x for x in linhas if x["tipo"] == "unidade_iniciada"), None)
    if abertura is None:
        return False, "a sessão não tem abertura no log"
    if abertura.get("topico") != dominio.id:
        return False, ("a sessão é do tópico %r, e o domínio carregado é %r"
                       % (abertura.get("topico"), dominio.id))
    if not any(x["tipo"] == log.ENTRADA for x in linhas) and len(linhas) > 1:
        return False, ("a sessão tem %d linhas e nenhuma entrada: log gravado "
                       "antes de as entradas existirem" % len(linhas))
    return True, ""


def sessoes(destino: Path | None = None) -> list[dict]:
    """Uma linha por sessão do log, da mais recente para a mais antiga.

    **Não reexecuta nada.** A tela pede esta lista de três em três
    segundos, e antes aqui havia uma reconstrução por sessão — cada uma
    relendo e reparseando o arquivo inteiro. Com 36 sessões dava 966 ms
    por chamada, no mesmo computador que atende quem está respondendo. O
    PRD diz que observar não pode custar o dado, e gastar CPU em laço vai
    pelo mesmo caminho que derrubar a sessão, só que por outra porta.

    O que a lista mostra sai do log literalmente: código, horários,
    respostas, retomadas, encerrada. A **fase** exige reexecução e
    pertence ao detalhe, que já é de uma sessão por vez.

    Sem nenhum texto livre: ver a lista não pode ser ver o que quarenta
    pessoas escreveram.
    """
    linhas, ilegiveis = log.le_tolerante(destino)
    por_sessao: dict[str, list[dict]] = {}
    for linha in linhas:
        por_sessao.setdefault(linha.get("sessao", ""), []).append(linha)

    saida = []
    for linhas in por_sessao.values():
        resumo = _resumo(linhas)
        # Sessão que este painel não conseguiria reexecutar continua
        # aparecendo, dizendo por quê. Esconder seria esconder dado.
        ok, motivo = _reexecutavel(linhas)
        resumo.update(reexecutavel=ok, motivo=motivo, ilegiveis=ilegiveis)
        saida.append(resumo)
    return sorted(saida, key=lambda x: x["inicio"], reverse=True)


def detalhe(sessao: str, destino: Path | None = None) -> dict | None:
    """Uma sessão inteira: onde ela chegou e por onde passou."""
    linhas = log.le(sessao, destino)
    if not linhas:
        return None
    t = log.reconstroi(dominio, sessao, destino)
    e = t.estado
    return {
        **_resumo(linhas),
        "fase": e.fase,
        "tela": t.tela.tipo,
        "nos": motor.estado_dos_nos(dominio, e),
        "episodios": episodios(linhas),
        # Texto livre do participante. Só aqui, nunca na lista.
        "frases": {"inicial": e.frase_inicial, "final": e.frase_final},
        "pergunta": dominio.teachback,
        "cauda": linhas[-CAUDA:],
    }


# --------------------------------------------------------------------------
# As rotas. Todas GET, e nenhuma escreve.
# --------------------------------------------------------------------------

@app.get("/sessoes")
def lista() -> dict:
    s = sessoes()
    # Linhas ilegíveis no arquivo. Zero é o normal; qualquer outro número
    # é o pesquisador precisando saber que o log tem buraco.
    return {"sessoes": s, "topico": dominio.id,
            "ilegiveis": s[0]["ilegiveis"] if s else 0}


@app.get("/sessoes/{sessao}")
def uma(sessao: str) -> dict:
    # `sessao` é valor de filtro, nunca pedaço de caminho: o painel lê um
    # arquivo só, decidido aqui dentro, e nada que venha do cliente
    # escolhe o que abrir.
    try:
        d = detalhe(sessao)
    except log.LogIncompleto as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    if d is None:
        raise HTTPException(status_code=404, detail="sessão desconhecida")
    return d


@app.get("/saude")
def saude() -> dict:
    return {"ok": True, "papel": "painel", "somente_leitura": True,
            "log": str(log.DESTINO), "topico": dominio.id}


@app.get("/")
def raiz() -> FileResponse:
    return FileResponse(AQUI / "web" / "painel.html")


def main() -> None:
    import uvicorn

    print("Structura — painel do pesquisador (somente leitura)")
    print("  lendo %s" % log.DESTINO)
    print("  http://127.0.0.1:8011")
    # 127.0.0.1, nunca 0.0.0.0: a sessão roda na sua máquina, e o painel
    # mostra dado de participante. Não há motivo para ele atender a rede.
    uvicorn.run(app, host="127.0.0.1", port=8011, log_level="warning")


if __name__ == "__main__":
    main()
