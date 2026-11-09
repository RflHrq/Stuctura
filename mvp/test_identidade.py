# -*- coding: utf-8 -*-
"""A identidade do participante entre tópicos: o guarda passa a ser um par.

O SEGUNDO MECANISMO do histórico individual, e a parte dele que faltava.

O 409 existe por uma razão escrita em `app.py`: *"abrir duas vezes o
mesmo código juntaria duas pessoas num participante só, e a análise não
teria como separar depois."* A razão continua inteira.

MAS ELE RECUSAVA PELO CÓDIGO SOZINHO, e o log é UM ARQUIVO. Enquanto
cada tópico rodava com `STRUCTURA_LOG` próprio, o mesmo código reaparecia
noutro tópico — por acidente de arquivo, não por desenho. Num log único,
que é o que um histórico individual quer, **o participante seria recusado
ao entrar no segundo tópico**: o guarda que protege a identidade era o
mesmo que impedia o histórico.

Então ele passa a ser `(código, tópico)`. P07 abre o kc_02 e depois o
kc_07; não abre o kc_02 duas vezes. O que a razão original protege é a
SESSÃO, não a pessoa.

O QUE ELE NÃO RESOLVE, e fica registrado em vez de escondido:

  - o código é digitado na URL, e nada impede duas pessoas usando o
    mesmo. O guarda pega repetição no log, não impostura.
  - `app.sessoes`, o estado em memória, é indexado pelo código sozinho.
    Dois tópicos no mesmo processo se sobrescreveriam ali. Hoje isso não
    acontece porque um processo serve um tópico — `carrega()` roda no
    import —, e trocar de tópico é reiniciar. Está pinado em
    `mvp/test_arquitetura.py`.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mvp import log
from mvp.dominio import carrega


@pytest.fixture
def servidor(tmp_path, monkeypatch):
    """Devolve (abre, arquivo): `abre(codigo, topico)` faz o POST.

    Cada chamada troca o domínio do módulo e LIMPA `app.sessoes` — é o
    que um reinício de servidor faz, e é a única forma de o mesmo
    processo atender dois tópicos. O log, de propósito, é UM só: é a
    situação que o guarda novo existe para atender.
    """
    from mvp import app as aplicacao

    arquivo = tmp_path / "um_log_so.jsonl"
    monkeypatch.setattr(log, "DESTINO", arquivo)
    dominios = {t: carrega(topico=t) for t in ("kc_02", "kc_07", "kc_11")}

    def abre(codigo, topico="kc_02"):
        monkeypatch.setattr(aplicacao, "dominio", dominios[topico])
        aplicacao.sessoes.clear()
        with TestClient(aplicacao.app) as c:
            return c.post("/sessoes", json={"codigo": codigo})

    return abre, arquivo


# --------------------------------------------------------------------------
# O par
# --------------------------------------------------------------------------

def test_o_mesmo_codigo_abre_outro_topico_no_mesmo_log(servidor):
    """É isto que não era possível, e sem isto não há histórico individual.

    Antes, o segundo tópico levava 409 e o participante ficava de fora —
    ou a coleta era obrigada a usar um arquivo por tópico, que é o que
    torna o percurso de uma pessoa ilegível.
    """
    abre, _ = servidor
    assert abre("P07", "kc_02").status_code == 200
    assert abre("P07", "kc_07").status_code == 200
    assert abre("P07", "kc_11").status_code == 200


def test_o_mesmo_codigo_no_mesmo_topico_continua_recusado(servidor):
    """A razão original do 409 fica inteira: duas sessões do mesmo tópico
    com o mesmo código juntariam duas pessoas num participante só."""
    abre, arquivo = servidor
    assert abre("P08", "kc_02").status_code == 200
    antes = arquivo.read_bytes()
    r = abre("P08", "kc_02")
    assert r.status_code == 409
    assert arquivo.read_bytes() == antes, "gravou mesmo recusando"


def test_a_recusa_diz_o_codigo_e_o_topico(servidor):
    """Quem conduz a coleta precisa saber QUAL par colidiu: a mensagem
    antiga dizia "neste log", e com um log por tópico isso bastava."""
    abre, _ = servidor
    abre("P09", "kc_07")
    detalhe = abre("P09", "kc_07").json()["detail"]
    assert "P09" in detalhe
    assert "kc_07" in detalhe


def test_codigos_diferentes_no_mesmo_topico_passam(servidor):
    abre, _ = servidor
    assert abre("P10", "kc_02").status_code == 200
    assert abre("P11", "kc_02").status_code == 200


def test_um_log_com_tres_topicos_do_mesmo_codigo_fica_legivel(servidor):
    """O arquivo que o histórico individual vai ler.

    Três `unidade_iniciada` com o mesmo código e tópicos diferentes — e é
    exatamente o que `docs/historico-individual.md` registrava como custo
    a pagar: *"o painel e o exportador presumem uma unidade por sessão"*.
    """
    import json

    abre, arquivo = servidor
    for topico in ("kc_02", "kc_07", "kc_11"):
        assert abre("P12", topico).status_code == 200
    linhas = [json.loads(x) for x in
              arquivo.read_text(encoding="utf-8").splitlines() if x.strip()]
    inicios = [x for x in linhas
               if x["tipo"] == "unidade_iniciada" and x["sessao"] == "P12"]
    assert [x["topico"] for x in inicios] == ["kc_02", "kc_07", "kc_11"]


# --------------------------------------------------------------------------
# O caso conservador: não dá para saber o tópico
# --------------------------------------------------------------------------

def test_codigo_cuja_abertura_ficou_pela_metade_e_recusado(servidor):
    """Linha truncada: recusa, porque não dá para saber de que tópico era.

    É O RISCO NOVO QUE ESTA MUDANÇA CRIA, e por isso entra aqui. Antes, o
    guarda olhava QUALQUER linha com aquele código; agora o tópico está
    só no `unidade_iniciada`, e `le_tolerante` PULA linha ilegível de
    propósito — o painel existe para funcionar depois de um travamento.

    O caso real é o documentado em `log.py`: o processo morre no meio de
    uma escrita e a linha sai pela metade. Aí o código ainda está no
    texto cru, e é nele que o guarda procura. Deixar passar arriscaria
    juntar duas pessoas, que é o dano que ele existe para impedir.

    O QUE CONTINUA INDETECTÁVEL: corrupção que apague o código inteiro da
    linha. Não há como achar o que não está escrito, e preferir recusar
    toda sessão nova porque o arquivo tem um defeito seria trocar um
    risco de pesquisa por uma coleta travada.
    """
    abre, arquivo = servidor
    assert abre("P13", "kc_02").status_code == 200
    # Uma sessão DEPOIS, para a linha estragada não ser a última: a
    # última tem desculpa e `_le` a descarta sem contar.
    assert abre("P14", "kc_02").status_code == 200

    linhas = arquivo.read_text(encoding="utf-8").splitlines()
    pela_metade = [x[:x.index('"tipo"')] if '"sessao": "P13"' in x else x
                   for x in linhas]
    assert pela_metade != linhas, "não achei a linha de abertura do P13"
    assert "P13" in pela_metade[0], "o truncamento apagou o código"
    arquivo.write_text("\n".join(pela_metade) + "\n", encoding="utf-8")

    r = abre("P13", "kc_07")
    assert r.status_code == 409
    assert "P13" in r.json()["detail"]


def test_codigo_novo_passa_mesmo_com_log_estragado(servidor):
    """Tolerar não é travar: uma linha ilegível de OUTRO participante não
    pode impedir o começo de uma sessão. Era a razão escrita no guarda
    antigo, e ela continua valendo."""
    abre, arquivo = servidor
    assert abre("P14", "kc_02").status_code == 200
    arquivo.write_text(arquivo.read_text(encoding="utf-8")
                       + "{isto nao e json\n", encoding="utf-8")
    assert abre("P15", "kc_02").status_code == 200
