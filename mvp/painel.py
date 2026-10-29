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


def sessoes(destino: Path | None = None) -> list[dict]:
    """Uma linha por sessão do log, da mais recente para a mais antiga.

    Sem nenhum texto livre: ver a lista não pode ser ver o que quarenta
    pessoas escreveram.
    """
    por_sessao: dict[str, list[dict]] = {}
    for linha in log.le(None, destino):
        por_sessao.setdefault(linha.get("sessao", ""), []).append(linha)

    saida = []
    for codigo, linhas in por_sessao.items():
        resumo = _resumo(linhas)
        try:
            t = log.reconstroi(dominio, codigo, destino)
        except log.LogIncompleto as erro:
            # Sessão que este painel não consegue reexecutar continua
            # aparecendo, dizendo por quê. Esconder seria esconder dado.
            resumo.update(reexecutavel=False, fase="", motivo=str(erro))
        else:
            resumo.update(reexecutavel=True, motivo="",
                          fase=t.estado.fase if t else "")
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
    return {"sessoes": sessoes(), "topico": dominio.id}


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
