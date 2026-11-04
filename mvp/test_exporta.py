# -*- coding: utf-8 -*-
"""A exportação do log do MVP para análise.

O P1-A de `docs/divergencia-texto-sistema.md`: o `plano-tcc.md` afirma que
"a exportação gera três tabelas", e o `tools/export.py` que as gera lê
**SQLite**. O MVP grava **JSONL**. Não existia exportação nenhuma em
`mvp/`, e sem ela uma coleta bem-feita produz um log de onde ninguém tira
tabela. É a única divergência daquele documento que pode inutilizar dado
já coletado.

QUATRO TABELAS, e não as três do plano. A unidade de análise de V2 e V3,
segundo o `processo.md`, é o **episódio de crença detectada** — e isso não
cabe numa linha de resposta. `crencas.csv` existe para ser essa unidade,
com o desfecho do reteste ao lado. Copiar o número três de um documento
que aponta para o sistema antigo seria guardar a forma e perder a função.

O QUE ESTA SUÍTE PROTEGE, em ordem de gravidade:

1. Texto livre do participante não vira fórmula na planilha. O
   teach-back vai do teclado dele direto para o CSV.
2. Nenhuma coluna carrega identificador direto.
3. Tudo sai do LOG. Não há projeção a consultar, e não pode haver:
   reexecutar o motor para preencher coluna faria a exportação medir o
   motor de hoje contra dado de ontem.
4. Sessão interrompida exporta. A que cai no meio é o caso que o CS-6
   existe para cobrir, e é justamente a que não pode sumir da análise.
"""
from __future__ import annotations

import csv
import json

import pytest

from mvp import exporta


# --------------------------------------------------------------------------
# Fixtures: um log escrito à mão, porque a asserção precisa saber a resposta
# --------------------------------------------------------------------------

def _linha(sessao, tipo, **campos):
    return dict(v=2, ts="2026-11-04T12:00:00+00:00", sessao=sessao,
                tipo=tipo, **campos)


@pytest.fixture
def log_simples(tmp_path):
    """Uma sessão completa e minúscula: dois episódios, uma crença
    detectada e retestada, os dois teach-backs."""
    linhas = [
        _linha("P01", "unidade_iniciada", topico="kc_02"),
        _linha("P01", "teachback_inicial", topico="kc_02",
               texto="acho que é um atalho", caracteres=20, em_branco=False,
               ms=4000),
        _linha("P01", "atividade_apresentada", atividade="a1", no="B1",
               formato="reconhecer_conceito", nivel=1, fase="DIAGNOSTICO",
               ordem=[2, 0, 1], item="i1"),
        _linha("P01", "episodio_classificado", atividade="a1", no="B1",
               correta=True, razao_correta=True, estado="confirmada",
               confianca="tenho certeza", crenca=None, nao_sei=False),
        _linha("P01", "atividade_apresentada", atividade="a2", no="B2",
               formato="achar_o_erro", nivel=1, fase="DIAGNOSTICO",
               ordem=[0, 1, 2], item="i2"),
        _linha("P01", "episodio_classificado", atividade="a2", no="B2",
               correta=False, razao_correta=False, estado="crenca",
               confianca="tenho certeza", crenca="pointer_is_data",
               nao_sei=False),
        _linha("P01", "crenca_detectada", crenca="pointer_is_data", no="B2",
               erros=1, veio_do_item_de="B2", vezes=1,
               confianca="tenho certeza", via=None),
        _linha("P01", "belief_retested", crenca="pointer_is_data", no="B2",
               atividade="a9", correta=True, voltou=False,
               razao_correta=True, confianca="tenho certeza",
               superficie_nova=True, nao_sei=False, formato="prever_saida",
               item="i9"),
        _linha("P01", "teachback_final", topico="kc_02",
               texto="são duas caixas", caracteres=15, em_branco=False,
               ms=5000),
        _linha("P01", "unidade_encerrada", confirmados=["B1"],
               em_aberto=[], nao_medidos=[], refutadas=["B2"],
               retestadas=["B2"], forcas={}, mais_fraca="B2",
               mais_fraca_de_pe=True),
    ]
    p = tmp_path / "eventos.jsonl"
    p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in linhas)
                 + "\n", encoding="utf-8")
    return p


def _le_csv(caminho):
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
# 1. A INJEÇÃO DE FÓRMULA — o item mais grave, e o menos óbvio
# --------------------------------------------------------------------------

@pytest.mark.parametrize("texto", [
    "=1+1",
    "+1",
    "-1+1",
    "@SUM(A1)",
    "=HYPERLINK(\"http://x\",\"clique\")",
    "\t=1+1",
    "\r=1+1",
])
def test_texto_que_viraria_formula_e_neutralizado(texto):
    """O teach-back vai do teclado do participante direto para a planilha.

    Um aluno que escreva `=1+1` teria isso EXECUTADO quando o pesquisador
    abrisse o CSV no Excel. Não é hipotético: é o vetor de injeção de
    fórmula em CSV, e aqui o campo é texto livre por desenho.

    O prefixo apóstrofo é a mitigação padrão: a planilha mostra o texto e
    não o avalia. O dado original continua intacto no log, que é a fonte.

    Tab e CR entram na lista porque o Excel os ignora como espaço e
    avalia o que vem depois — uma lista que só olha o primeiro caractere
    deixa passar `\\t=1+1`.
    """
    assert exporta.neutraliza(texto).startswith("'"), repr(texto)


@pytest.mark.parametrize("texto", [
    "ponteiro guarda endereço",
    "a = 3 não é o mesmo que *p = 3",
    "",
    "1+1 é dois",
    "não sei",
])
def test_texto_inofensivo_nao_e_mexido(texto):
    """Neutralizar o que não precisa sujaria o dado: um apóstrofo a mais
    em toda frase estraga a leitura e a contagem de caracteres."""
    assert exporta.neutraliza(texto) == texto, repr(texto)


def test_o_teachback_chega_neutralizado_no_csv(tmp_path):
    """A ponta a ponta do item 1: não basta a função existir, ela tem de
    estar no caminho que o texto do participante percorre."""
    linhas = [
        _linha("P01", "unidade_iniciada", topico="kc_02"),
        _linha("P01", "teachback_inicial", topico="kc_02",
               texto="=1+1", caracteres=4, em_branco=False, ms=100),
        _linha("P01", "teachback_final", topico="kc_02",
               texto="@SUM(A1)", caracteres=8, em_branco=False, ms=100),
    ]
    p = tmp_path / "e.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in linhas) + "\n",
                 encoding="utf-8")
    exporta.exporta(p, tmp_path / "saida")
    linha = _le_csv(tmp_path / "saida" / "sessoes.csv")[0]
    assert linha["teachback_inicial"].startswith("'")
    assert linha["teachback_final"].startswith("'")


def test_nao_sobra_coluna_de_texto_livre_sem_neutralizacao(tmp_path, log_simples):
    """A trava contra a próxima versão deste defeito.

    Toda célula de todo CSV passa pelo neutralizador — não só as que eu
    lembrei de passar. Se alguém acrescentar uma coluna de texto livre e
    esquecer, é aqui que cai.
    """
    exporta.exporta(log_simples, tmp_path / "saida")
    for nome in exporta.TABELAS:
        for linha in _le_csv(tmp_path / "saida" / nome):
            for coluna, valor in linha.items():
                assert not valor.startswith(exporta.PERIGOSOS), (nome, coluna, valor)


# --------------------------------------------------------------------------
# 2. ANONIMIZAÇÃO: nenhuma coluna carrega identificador direto
# --------------------------------------------------------------------------

def test_nenhuma_coluna_e_identificador_direto():
    """Anonimização na origem: o código é P01…P40 e nome, matrícula e
    e-mail ficam em papel, fora do log. Uma coluna chamada `nome` não
    poderia nem ser preenchida — mas existir já convidaria alguém a
    preencher, e a submissão ética fala sobre o que o arquivo PODE ter.

    A primeira versão deste teste comparava SUBSTRING, e acusava
    `participante` por conter "ip" (part-ic-**ip**-ante). Critério burro
    dá falso positivo e ensina quem vier depois a desligar o teste. A
    comparação é por SEGMENTO do nome, separado por `_`, que é como as
    colunas são nomeadas aqui.
    """
    proibidas = {"nome", "matricula", "email", "cpf", "telefone", "ip",
                 "usuario", "login", "turma", "rg", "endereco"}
    for nome, colunas in exporta.COLUNAS.items():
        for c in colunas:
            segmentos = set(c.lower().split("_"))
            assert not (segmentos & proibidas), (nome, c, segmentos & proibidas)


def test_o_participante_sai_como_codigo_de_sessao(tmp_path, log_simples):
    exporta.exporta(log_simples, tmp_path / "saida")
    for nome in exporta.TABELAS:
        for linha in _le_csv(tmp_path / "saida" / nome):
            assert linha["participante"] == "P01", (nome, linha)


# --------------------------------------------------------------------------
# 3. TUDO SAI DO LOG
# --------------------------------------------------------------------------

def test_a_exportacao_nao_importa_o_motor():
    """A regra que o exportador antigo escreveu e que vale igual aqui:
    nenhuma análise lê projeção.

    Aqui é mais forte que lá. Reexecutar o motor para preencher coluna
    faria a exportação medir o motor de HOJE contra dado de ONTEM — e o
    `log.reconstroi` já recusa sessão de versão anterior exatamente por
    isso. Um exportador que importasse o motor contornaria essa recusa
    por acidente.

    A primeira versão fazia grep no arquivo e caía no próprio docstring
    que explica a regra — um teste que proíbe FALAR da coisa em vez de
    proibir USÁ-LA. A leitura é por AST: importa o que a árvore diz que é
    import e o que ela diz que é chamada, e comentário nenhum conta.
    """
    import ast
    import pathlib

    arvore = ast.parse(pathlib.Path(exporta.__file__).read_text(encoding="utf-8"))
    importados = set()
    chamados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados |= {a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            importados.add((no.module or "").split(".")[0])
            importados |= {a.name for a in no.names}
        elif isinstance(no, ast.Attribute):
            chamados.add(no.attr)
        elif isinstance(no, ast.Name):
            chamados.add(no.id)

    for proibido in ("motor", "dominio", "molde", "log"):
        assert proibido not in importados, ("importa %s" % proibido, importados)
    assert "reconstroi" not in chamados, "chama reconstroi"


# --------------------------------------------------------------------------
# 4. SESSÃO INTERROMPIDA EXPORTA
# --------------------------------------------------------------------------

def test_sessao_sem_encerramento_ainda_exporta(tmp_path):
    """A sessão que cai no meio é o caso que o CS-6 existe para cobrir, e
    é justamente a que não pode sumir da análise: o PRD orça perder 1 em
    10 a 15 participantes por queda.

    Um exportador que só emitisse linha ao ver `unidade_encerrada`
    apagaria silenciosamente o participante mais interessante do estudo.
    """
    linhas = [
        _linha("P07", "unidade_iniciada", topico="kc_02"),
        _linha("P07", "episodio_classificado", atividade="a1", no="B1",
               correta=True, razao_correta=True, estado="confirmada",
               confianca="tenho certeza", crenca=None, nao_sei=False),
    ]
    p = tmp_path / "e.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in linhas) + "\n",
                 encoding="utf-8")
    exporta.exporta(p, tmp_path / "saida")

    s = _le_csv(tmp_path / "saida" / "sessoes.csv")
    assert len(s) == 1, s
    assert s[0]["participante"] == "P07"
    assert s[0]["completou"] == "False", s[0]
    assert _le_csv(tmp_path / "saida" / "respostas.csv"), "o episódio sumiu"


def test_linha_ilegivel_nao_derruba_a_exportacao(tmp_path, log_simples):
    """O log é append-only e pode ter a última linha truncada por queda no
    meio da escrita. Isso não pode custar a sessão inteira — e também não
    pode passar calado."""
    with log_simples.open("a", encoding="utf-8") as f:
        f.write('{"v":2,"sessao":"P01","tipo":"episodio_cla\n')
    r = exporta.exporta(log_simples, tmp_path / "saida")
    assert r["ilegiveis"] == 1, r
    assert _le_csv(tmp_path / "saida" / "respostas.csv")


# --------------------------------------------------------------------------
# As quatro tabelas, e o que cada uma promete
# --------------------------------------------------------------------------

def test_respostas_tem_uma_linha_por_episodio(tmp_path, log_simples):
    """O episódio é a unidade, e `estado` é a classificação dos cinco —
    a coluna que carrega a CS-1 inteira."""
    exporta.exporta(log_simples, tmp_path / "saida")
    r = _le_csv(tmp_path / "saida" / "respostas.csv")
    assert len(r) == 2, r
    assert [x["no"] for x in r] == ["B1", "B2"]
    assert [x["estado"] for x in r] == ["confirmada", "crenca"]
    assert r[0]["seq"] == "1" and r[1]["seq"] == "2"


def test_respostas_traz_o_formato_e_a_ordem_da_tela(tmp_path, log_simples):
    """`ordem` é a permutação que a pessoa viu, e sem ela o índice gravado
    não se interpreta — foi a fatia da posição que a pôs no log. `formato`
    é o que distingue as duas superfícies da CS-5."""
    exporta.exporta(log_simples, tmp_path / "saida")
    r = _le_csv(tmp_path / "saida" / "respostas.csv")
    assert r[0]["formato"] == "reconhecer_conceito"
    assert r[0]["ordem"] == "2 0 1", r[0]["ordem"]


def test_crencas_pareia_deteccao_com_reteste(tmp_path, log_simples):
    """A tabela que justifica ser quatro e não três: uma linha por crença
    detectada, com o desfecho do reteste ao lado. É a unidade de análise
    de V2 e V3."""
    exporta.exporta(log_simples, tmp_path / "saida")
    c = _le_csv(tmp_path / "saida" / "crencas.csv")
    assert len(c) == 1, c
    assert c[0]["crenca"] == "pointer_is_data"
    assert c[0]["no"] == "B2"
    assert c[0]["retestada"] == "True"
    assert c[0]["voltou"] == "False"


def test_crenca_detectada_e_nao_retestada_aparece_como_tal(tmp_path):
    """Crença sem reteste não pode sumir nem virar `voltou=False`: as duas
    coisas são afirmações diferentes, e confundi-las inventaria sucesso de
    refutação que ninguém mediu."""
    linhas = [
        _linha("P02", "unidade_iniciada", topico="kc_02"),
        _linha("P02", "crenca_detectada", crenca="array_is_pointer", no="B3",
               erros=1, veio_do_item_de="B3", vezes=1,
               confianca="chutei", via=None),
        _linha("P02", "reteste_sem_item", crenca="array_is_pointer", no="B3",
               motivo="banco esgotado"),
    ]
    p = tmp_path / "e.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in linhas) + "\n",
                 encoding="utf-8")
    exporta.exporta(p, tmp_path / "saida")
    c = _le_csv(tmp_path / "saida" / "crencas.csv")
    assert len(c) == 1
    assert c[0]["retestada"] == "False"
    assert c[0]["voltou"] == "", repr(c[0]["voltou"])


def test_calibracao_e_uma_linha_por_participante_e_confianca(tmp_path, log_simples):
    """A calibração metacognitiva: a proporção de acerto dentro de cada
    nível declarado. É o que diz se "tenho certeza" quer dizer algo."""
    exporta.exporta(log_simples, tmp_path / "saida")
    k = _le_csv(tmp_path / "saida" / "calibracao.csv")
    assert len(k) == 1, k
    assert k[0]["confianca"] == "tenho certeza"
    assert k[0]["n"] == "2"
    assert k[0]["n_corretas"] == "1"
    assert k[0]["prop_corretas"] == "0.5"


def test_a_ordem_da_escala_de_confianca_e_a_da_escala(tmp_path):
    """`confianca_rank` existe porque "chutei" < "acho que sei" <
    "tenho certeza" é ordinal, e ordenar por texto daria alfabético."""
    linhas = [_linha("P03", "unidade_iniciada", topico="kc_02")]
    for i, conf in enumerate(("tenho certeza", "chutei", "acho que sei")):
        linhas.append(_linha("P03", "episodio_classificado", atividade="a%d" % i,
                             no="B1", correta=True, razao_correta=True,
                             estado="confirmada", confianca=conf, crenca=None,
                             nao_sei=False))
    p = tmp_path / "e.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in linhas) + "\n",
                 encoding="utf-8")
    exporta.exporta(p, tmp_path / "saida")
    k = sorted(_le_csv(tmp_path / "saida" / "calibracao.csv"),
               key=lambda x: int(x["confianca_rank"]))
    assert [x["confianca"] for x in k] == ["chutei", "acho que sei",
                                           "tenho certeza"]


def test_sessoes_traz_as_contagens_do_encerramento(tmp_path, log_simples):
    exporta.exporta(log_simples, tmp_path / "saida")
    s = _le_csv(tmp_path / "saida" / "sessoes.csv")[0]
    assert s["topico"] == "kc_02"
    assert s["completou"] == "True"
    assert s["confirmados"] == "B1"
    assert s["refutadas"] == "B2"
    assert s["n_episodios"] == "2"
    assert s["n_crencas_detectadas"] == "1"


# --------------------------------------------------------------------------
# O arquivo
# --------------------------------------------------------------------------

def test_o_csv_abre_no_excel_com_acento_certo(tmp_path, log_simples):
    """`utf-8-sig`: o Excel em português abre acento certo sem perguntar.
    Sem o BOM ele assume a codificação do sistema e come os acentos — e o
    pesquisador não vai reparar numa planilha de 200 linhas."""
    exporta.exporta(log_simples, tmp_path / "saida")
    bruto = (tmp_path / "saida" / "respostas.csv").read_bytes()
    assert bruto.startswith(b"\xef\xbb\xbf"), bruto[:10]


def test_as_quatro_tabelas_saem(tmp_path, log_simples):
    r = exporta.exporta(log_simples, tmp_path / "saida")
    assert set(exporta.TABELAS) == {"respostas.csv", "sessoes.csv",
                                    "calibracao.csv", "crencas.csv"}
    for nome in exporta.TABELAS:
        assert (tmp_path / "saida" / nome).exists(), nome
        assert nome in r, r


def test_duas_sessoes_nao_se_misturam(tmp_path, log_simples):
    """O log é um arquivo só para a coleta inteira: separar por sessão é
    obrigação do exportador, e trocar linhas entre participantes seria o
    erro mais caro possível."""
    outra = [
        _linha("P02", "unidade_iniciada", topico="kc_03"),
        _linha("P02", "episodio_classificado", atividade="b1", no="B1",
               correta=False, razao_correta=False, estado="crenca",
               confianca="chutei", crenca="x", nao_sei=False),
    ]
    with log_simples.open("a", encoding="utf-8") as f:
        for x in outra:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    exporta.exporta(log_simples, tmp_path / "saida")

    s = {x["participante"]: x for x in _le_csv(tmp_path / "saida" / "sessoes.csv")}
    assert set(s) == {"P01", "P02"}
    assert s["P01"]["topico"] == "kc_02" and s["P02"]["topico"] == "kc_03"
    r = _le_csv(tmp_path / "saida" / "respostas.csv")
    assert [x["participante"] for x in r] == ["P01", "P01", "P02"]


# --------------------------------------------------------------------------
# CONTRA LOG DE VERDADE — e a razão de este bloco existir
# --------------------------------------------------------------------------
#
# Os fixtures acima são escritos à mão, e por isso provam o meu MODELO do
# log, não o log. A primeira versão deste módulo saiu com `escolha` e `ms`
# sempre vazias e com `item` carregando o TIPO da atividade, porque eu as
# li de `atividade_apresentada` — onde eu pensava que estavam. Os 29
# testes de fixture passaram todos, porque eu havia escrito os fixtures
# com os campos no lugar errado também.
#
# Fixture feito do próprio modelo confirma o modelo. Este bloco gera a
# sessão pelo MOTOR e grava pelo `log`, do mesmo jeito que o servidor —
# então o que ele afirma é sobre o log, e não sobre o que eu acho dele.

def _sessao_de_verdade(caminho, sessao="P09", topico="kc_02"):
    """Uma sessão inteira, gravada como o servidor grava."""
    from mvp import log, motor
    from mvp.dominio import carrega

    d = carrega(topico=topico)

    def politica(tela, estado):
        if tela.tipo == "frase":
            return motor.Resposta(texto="uma frase qualquer", ms=4000)
        if tela.tipo == "confianca":
            return motor.Resposta(confianca="acho que sei", ms=1500)
        if tela.tipo in ("ensino", "validacao", "refutacao"):
            return motor.Resposta(ms=2000)
        if tela.tipo == "atividade":
            a = next(x for x in d.atividades if x.id == tela.dados["atividade"])
            return motor.Resposta(
                escolha=motor.indice_correto_na_tela(estado.semente, a), ms=3000)
        # camada 2: a razão certa é a fala do nó
        certa = next((i for i, o in enumerate(tela.dados["opcoes"])
                      if o["texto"] in {n.texto for n in d.nos.values()}
                      | {n.simples for n in d.nos.values()}), 0)
        return motor.Resposta(escolha=certa, ms=2500)

    t = motor.inicia(d, semente=sessao)
    log.grava(sessao, t.eventos, destino=caminho)
    for _ in range(400):
        if t.tela.tipo == "mapa":
            return t
        r = politica(t.tela, t.estado)
        t = motor.avanca(d, t.estado, r)
        log.grava(sessao, t.eventos, destino=caminho, entrada=r)
    raise AssertionError("a unidade não terminou")


@pytest.fixture(scope="module")
def real(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("real")
    caminho = pasta / "eventos.jsonl"
    _sessao_de_verdade(caminho)
    exporta.exporta(caminho, pasta / "saida")
    return pasta / "saida"


def test_no_log_real_a_escolha_nao_sai_vazia(real):
    """O defeito que os fixtures não pegaram.

    `escolha` é o índice NA TELA, e sem ela a análise não sabe o que a
    pessoa marcou — é a coluna que a fatia da posição existiu para tornar
    interpretável, junto com `ordem`.
    """
    r = _le_csv(real / "respostas.csv")
    assert r, "nenhuma resposta exportada"
    cheias = [x for x in r if x["escolha"] != ""]
    assert len(cheias) == len(r), (
        "%d de %d linhas sem escolha" % (len(r) - len(cheias), len(r)))


def test_no_log_real_o_ms_nao_sai_vazio(real):
    """`ms` é o tempo por episódio, e é metade do V1 — "em quanto tempo"."""
    r = _le_csv(real / "respostas.csv")
    cheias = [x for x in r if x["ms"] != ""]
    assert len(cheias) == len(r), (
        "%d de %d linhas sem ms" % (len(r) - len(cheias), len(r)))


def test_no_log_real_o_tipo_da_atividade_tem_o_nome_certo(real):
    """A coluna se chamava `item` e carregava "teorica" — o TIPO. Nome de
    coluna que mente é pior que coluna ausente: quem analisa não tem como
    desconfiar.

    O conjunto permitido vem do DOMÍNIO, não da minha memória: a primeira
    versão deste teste permitia "pratica", que não existe. Os 562 itens
    dos treze tópicos são `teorica` (239) ou `codigo` (323).
    """
    from mvp.dominio import carrega, topicos

    permitidos = {a.tipo for t in topicos() for a in carrega(topico=t).atividades}
    r = _le_csv(real / "respostas.csv")
    assert "tipo" in r[0], sorted(r[0])
    assert set(x["tipo"] for x in r) <= permitidos | {""}, (
        set(x["tipo"] for x in r) - permitidos)


def test_no_log_real_a_calibracao_fecha_com_as_respostas(real):
    """A soma dos `n` da calibração tem de bater com o total de episódios
    que declararam confiança. Se não bater, uma das duas tabelas está
    perdendo linha — e perda silenciosa é o defeito que mais custa aqui.
    """
    r = [x for x in _le_csv(real / "respostas.csv") if x["confianca"]]
    k = _le_csv(real / "calibracao.csv")
    assert sum(int(x["n"]) for x in k) == len(r), (
        sum(int(x["n"]) for x in k), len(r))


def test_no_log_real_toda_coluna_declarada_existe_no_csv(real):
    """Coluna declarada em `COLUNAS` e ausente do arquivo significaria que
    o escritor e a declaração divergiram."""
    for nome in exporta.TABELAS:
        linhas = _le_csv(real / nome)
        if not linhas:
            continue
        assert set(linhas[0]) == set(exporta.COLUNAS[nome]), nome


# --------------------------------------------------------------------------
# O DESTINO NÃO PODE SER PASTA VERSIONADA
# --------------------------------------------------------------------------
#
# A exportação carrega TEXTO LIVRE do participante: os dois teach-backs vão
# para `sessoes.csv`. Escrever isso numa pasta versionada é o P0 da revisão
# final de novo — três cópias do log de desenvolvimento entraram no git por
# um caminho que o `.gitignore` não casava, e a varredura de segredos passou
# por cima delas.
#
# O projeto JÁ DECIDIU esta questão para o comando irmão: o `copia.sh`
# recusa destino dentro do repositório, e tem teste
# (`test_destino_dentro_do_repositorio_e_recusado`). Um exportador sem a
# mesma trava seria incoerente com o padrão da própria casa.
#
# A regra não é "fora do repositório": é "o git tem de ignorar". `analise/`
# está no `.gitignore` por decisão declarada, com comentário, e é o destino
# padrão. Fora do repositório é problema do pesquisador, não meu.

def test_destino_versionado_e_recusado(tmp_path):
    """`--out docs/` escreveria teach-back em pasta que vai para o git."""
    log = tmp_path / "e.jsonl"
    log.write_text(json.dumps(_linha("P01", "unidade_iniciada",
                                     topico="kc_02")) + "\n",
                   encoding="utf-8")
    with pytest.raises(exporta.DestinoVersionado) as erro:
        exporta.exporta(log, "docs/saida_proibida")
    assert "versionad" in str(erro.value).lower(), str(erro.value)


def test_destino_versionado_nao_escreve_nada_antes_de_recusar(tmp_path):
    """Recusar depois de escrever o primeiro arquivo seria pior que não
    recusar: o dado já estaria lá, e o erro na tela daria a impressão de
    que não."""
    import pathlib as _p
    log = tmp_path / "e.jsonl"
    log.write_text(json.dumps(_linha("P01", "unidade_iniciada",
                                     topico="kc_02")) + "\n",
                   encoding="utf-8")
    alvo = _p.Path("docs/saida_proibida")
    try:
        exporta.exporta(log, alvo)
    except exporta.DestinoVersionado:
        pass
    assert not alvo.exists(), "a pasta foi criada antes da recusa"


def test_o_destino_padrao_e_ignorado_pelo_git():
    """`analise/` é o padrão, e tem de continuar ignorado. Se alguém tirar
    a linha do `.gitignore`, é aqui que cai — e não na coleta."""
    import subprocess, pathlib as _p
    raiz = _p.Path(exporta.__file__).resolve().parent.parent
    r = subprocess.run(["git", "check-ignore", "-q", "analise"],
                       cwd=raiz, capture_output=True)
    assert r.returncode == 0, "analise/ deixou de ser ignorada pelo git"


def test_destino_fora_do_repositorio_e_aceito(tmp_path, log_simples):
    """Fora do repositório a decisão é do pesquisador — a segunda mídia da
    cópia fica fora, e exigir git lá seria impedir o uso legítimo."""
    r = exporta.exporta(log_simples, tmp_path / "fora")
    assert r["respostas.csv"] == 2
