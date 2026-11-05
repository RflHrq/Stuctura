"""R6: apagar um participante, e copiar depois da sessão.

Os dois procedimentos que o PRD exige e que não existiam como comando —
só como lembrete.

> *"o participante pode pedir a exclusão dos dados dele pelo código"*

Declarar um direito e não ter como exercê-lo é problema de conformidade,
não de conveniência, e o texto vai ao comitê de ética.

> *"depois de cada sessão, o log vai para uma segunda mídia"*, com
> **perda tolerável zero**

O log de uma coleta é irreproduzível: a pessoa não volta para refazer.

Estes testes rodam os scripts de verdade, num log de teste. Script que
nunca foi executado é documentação, não procedimento.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
# Caminhos RELATIVOS: o bash do Git no Windows não abre um caminho com
# barras invertidas, e os testes rodam com `cwd=RAIZ`.
APAGAR = "scripts/participante.sh"
COPIAR = "scripts/copia.sh"

# O que um clone consegue criar em qualquer sistema. Usado pelo teste de
# higiene do repositório, e é a mesma lista branca do `scripts/verify.sh`.
SEGURO = re.compile(r"^[A-Za-z0-9._/-]+$")


def rel(caminho: pathlib.Path) -> str:
    """O caminho como este bash consegue abrir: relativo à raiz.

    O bash que o Python encontra aqui não resolve caminho absoluto do
    Windows em forma nenhuma — nem `C:\\x`, nem `C:/x`, nem `/c/x`; foi
    medido. O que ele resolve é caminho relativo ao diretório de trabalho,
    inclusive com `..`.

    É por isso que a área de teste pode ficar FORA do repositório, que é
    onde ela tem de ficar: a primeira versão deste arquivo pôs a área
    dentro, e três cópias do log de desenvolvimento ficaram versionadas por
    dois commits. Quem achou foi a revisão final, na primeira tentativa de
    clonar o repositório.
    """
    return pathlib.Path(os.path.relpath(caminho, RAIZ)).as_posix()


def roda(script, *args, log=None, confirma=None):
    """Roda o script de verdade, com o log passado por argumento.

    `confirma` vira `--confirmo`, que é como `apagar` aceita a
    confirmação sem perguntar. Não é porta dos fundos: a garantia do
    comando não é ser interativo, é **dizer o código duas vezes**, e
    `--confirmo` exige exatamente o mesmo que o teclado exigiria.

    (O bash deste ambiente não recebe a entrada padrão de um
    subprocesso, então testar pela pergunta não era possível aqui.)
    """
    extra = ["--log", rel(log)] if log is not None else []
    if confirma is not None:
        extra += ["--confirmo", confirma]
    return subprocess.run(["bash", script, *args, *extra], cwd=RAIZ,
                          capture_output=True, text=True)


@pytest.fixture
def area(tmp_path):
    """Área de trabalho FORA do repositório — a pasta temporária do pytest.

    Os scripts a recebem como caminho relativo à raiz, com `..` — ver
    `rel`. Nada que um teste escreva pode cair dentro do repositório: o
    `copia.sh` agora recusa destino aqui dentro, e é por bom motivo.
    """
    return tmp_path


@pytest.fixture
def log_de_teste(area):
    """Três participantes no mesmo arquivo, um deles com texto livre."""
    caminho = area / "eventos.jsonl"
    linhas = []
    for codigo in ("P01", "P02", "P03"):
        linhas.append({"v": 1, "ts": "2026-10-29T10:00:00.000+00:00",
                       "sessao": codigo, "tipo": "unidade_iniciada",
                       "topico": "kc_00"})
        linhas.append({"v": 1, "ts": "2026-10-29T10:01:00.000+00:00",
                       "sessao": codigo, "tipo": "teachback_inicial",
                       "texto": "o que %s escreveu" % codigo})
        linhas.append({"v": 1, "ts": "2026-10-29T10:02:00.000+00:00",
                       "sessao": codigo, "tipo": "unidade_encerrada"})
    caminho.write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in linhas) + "\n",
        encoding="utf-8")
    return caminho


def codigos(caminho):
    return [json.loads(x)["sessao"]
            for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


# --------------------------------------------------------------------------
# Apagar um participante
# --------------------------------------------------------------------------

def test_ver_mostra_o_que_seria_apagado_sem_apagar(log_de_teste):
    """Olhar antes de apagar: o log é irreproduzível, e o comando não
    pode ser a primeira vez que se vê o que ele alcança."""
    antes = log_de_teste.read_bytes()
    r = roda(APAGAR, "ver", "P02", log=log_de_teste)
    assert r.returncode == 0, r.stderr
    assert "teachback_inicial" in r.stdout
    assert "com texto livre do participante: 1" in r.stdout
    assert log_de_teste.read_bytes() == antes


def test_apagar_remove_todas_as_linhas_de_um_e_nenhuma_de_outro(log_de_teste):
    r = roda(APAGAR, "apagar", "P02", log=log_de_teste, confirma="P02")
    assert r.returncode == 0, r.stderr
    restantes = codigos(log_de_teste)
    assert "P02" not in restantes
    assert restantes.count("P01") == 3
    assert restantes.count("P03") == 3


def test_o_texto_livre_do_participante_some_do_arquivo(log_de_teste):
    """O que o pedido de exclusão quer dizer na prática."""
    roda(APAGAR, "apagar", "P02", log=log_de_teste, confirma="P02")
    assert "o que P02 escreveu" not in log_de_teste.read_text(encoding="utf-8")
    assert "o que P01 escreveu" in log_de_teste.read_text(encoding="utf-8")


def test_apagar_guarda_uma_copia_de_antes(log_de_teste, area):
    """Irreversível merece rede. A cópia é apagada por quem conferiu o
    pedido, não pelo script."""
    roda(APAGAR, "apagar", "P02", log=log_de_teste, confirma="P02")
    copias = list(area.glob("eventos.jsonl.antes-de-apagar-*"))
    assert len(copias) == 1
    assert "o que P02 escreveu" in copias[0].read_text(encoding="utf-8")


def test_codigo_que_nao_existe_nao_mexe_no_arquivo(log_de_teste):
    antes = log_de_teste.read_bytes()
    r = roda(APAGAR, "apagar", "P99", log=log_de_teste, confirma="P99")
    assert r.returncode != 0
    assert log_de_teste.read_bytes() == antes


def test_o_codigo_nao_e_expressao_regular(log_de_teste):
    """Um código com ponto ou colchete casaria linhas de outros
    participantes se entrasse como padrão. Apagar demais é pior do que
    não apagar."""
    antes = log_de_teste.read_bytes()
    for padrao in ("P.2", "P0[123]", ".*"):
        r = roda(APAGAR, "apagar", padrao, log=log_de_teste, confirma=padrao)
        assert r.returncode != 0, padrao
    assert log_de_teste.read_bytes() == antes


def test_a_linha_ilegivel_nao_e_apagada(log_de_teste):
    """Apagar o que não se consegue ler seria apagar o que não se sabe."""
    texto = log_de_teste.read_text(encoding="utf-8")
    log_de_teste.write_text(texto + '{"ts": "2026-\n', encoding="utf-8")
    roda(APAGAR, "apagar", "P02", log=log_de_teste, confirma="P02")
    assert '{"ts": "2026-' in log_de_teste.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Copiar depois da sessão
# --------------------------------------------------------------------------

def test_a_copia_bate_byte_a_byte(log_de_teste, area):
    destino = area / "midia"
    r = roda(COPIAR, rel(destino), log=log_de_teste)
    assert r.returncode == 0, r.stderr
    copias = list(destino.glob("eventos-*.jsonl"))
    assert len(copias) == 1
    assert copias[0].read_bytes() == log_de_teste.read_bytes()
    # A conferência acontece no caminho da cópia, e não só quando alguém
    # chama `conferir` à mão: a saída dela é a prova observável de fora.
    assert "confere" in r.stdout
    assert "NAO confere" not in r.stdout
    assert "copiado e conferido" in r.stdout
    assert "3" in r.stdout      # três sessões


def test_copiar_duas_vezes_nao_sobrescreve_a_primeira(log_de_teste, area):
    """A cópia de ontem continua lá. Sobrescrever transformaria a rotina
    de proteção numa forma de perder a versão anterior."""
    destino = area / "midia"
    roda(COPIAR, rel(destino), log=log_de_teste)
    primeira = list(destino.glob("eventos-*.jsonl"))[0]
    conteudo = primeira.read_bytes()

    log_de_teste.write_text(log_de_teste.read_text(encoding="utf-8") +
                            '{"v": 1, "sessao": "P04", "tipo": "x"}\n',
                            encoding="utf-8")
    import time
    time.sleep(1.1)             # o carimbo tem segundos
    roda(COPIAR, rel(destino), log=log_de_teste)

    assert len(list(destino.glob("eventos-*.jsonl"))) == 2
    assert primeira.read_bytes() == conteudo


def test_copiar_sem_log_falha_em_vez_de_criar_arquivo_vazio(area):
    """Uma cópia vazia de um log que não foi achado seria pior do que
    erro: pareceria proteção."""
    destino = area / "midia"
    r = roda(COPIAR, rel(destino),
             log=area / "nao-existe.jsonl")
    assert r.returncode != 0
    assert not list(destino.glob("*.jsonl"))


def test_os_scripts_tem_fim_de_linha_unix():
    """No Windows o Git converte para CRLF no diretório de trabalho, e o
    bash lê `set -euo pipefail\r` como opção inválida — o script morre na
    primeira linha, com uma mensagem que não ajuda.

    O `.gitattributes` fixa isso no versionamento; este teste pega quem
    reescrever o arquivo com a conversão ligada, que foi o que aconteceu
    duas vezes escrevendo esta tarefa.
    """
    for script in sorted((RAIZ / "scripts").glob("*.sh")):
        assert b"\r\n" not in script.read_bytes(), script.name


def test_confirmacao_errada_nao_apaga_nada(log_de_teste):
    """A garantia do comando não é ser interativo: é **dizer o código
    duas vezes**. `--confirmo` com outra coisa não vale."""
    antes = log_de_teste.read_bytes()
    r = roda(APAGAR, "apagar", "P02", log=log_de_teste, confirma="P01")
    assert r.returncode != 0
    assert "nao confere" in r.stdout
    assert log_de_teste.read_bytes() == antes


def test_um_codigo_que_e_prefixo_de_outro_nao_leva_o_outro_junto(area):
    """P1 e P10 no mesmo arquivo. Se a comparação fosse por substring —
    e era o que uma sabotagem mostrou passar — apagar P1 levaria P10
    junto, e o participante errado perderia os dados."""
    caminho = area / "eventos.jsonl"
    caminho.write_text("\n".join(json.dumps(x) for x in [
        {"v": 1, "sessao": "P1", "tipo": "unidade_iniciada"},
        {"v": 1, "sessao": "P10", "tipo": "unidade_iniciada"},
        {"v": 1, "sessao": "P10", "tipo": "teachback_inicial", "texto": "de P10"},
        {"v": 1, "sessao": "P1", "tipo": "unidade_encerrada"},
    ]) + "\n", encoding="utf-8")

    r = roda(APAGAR, "apagar", "P1", log=caminho, confirma="P1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert codigos(caminho) == ["P10", "P10"]
    assert "de P10" in caminho.read_text(encoding="utf-8")


def test_a_conferencia_da_copia_acusa_diferenca(area):
    """A checagem exercitada de verdade. `cmp` num script que ninguém
    testou é uma linha bonita, não uma garantia."""
    igual_a = area / "a.txt"
    igual_b = area / "b.txt"
    diferente = area / "c.txt"
    igual_a.write_text("mesmo conteudo\n", encoding="utf-8")
    igual_b.write_text("mesmo conteudo\n", encoding="utf-8")
    diferente.write_text("outro conteudo\n", encoding="utf-8")

    def conferir(x, y):
        return roda(COPIAR, "conferir",
                    rel(x),
                    rel(y))

    assert conferir(igual_a, igual_b).returncode == 0
    ruim = conferir(igual_a, diferente)
    assert ruim.returncode != 0
    assert "NAO confere" in ruim.stdout


# --------------------------------------------------------------------------
# O destino da cópia, e o repositório
#
# Tudo nesta seção vem de um único incidente, achado na revisão final: três
# cópias do log de desenvolvimento — 2,8 MB, 38 sessões, 23 linhas de texto
# livre — ficaram versionadas por dois commits, e `git clone` passou a
# falhar no Windows. A causa não foi descuido de quem escreveu o comando:
# foi o script dizer **"copiado e conferido"** para uma cópia que estava em
# outro lugar.
# --------------------------------------------------------------------------

def test_destino_em_formato_windows_e_recusado(log_de_teste):
    r"""`D:\coleta` chega literal quando quem chama não é shell, e
    `mkdir -p` cria uma PASTA com esse nome dentro do diretório atual.

    O desfecho antigo era o pior possível: código de saída 0, a frase
    "copiado e conferido" na tela, e o backup em lugar nenhum.
    """
    antes = set(os.listdir(RAIZ))
    r = roda(COPIAR, "D:\\coleta", log=log_de_teste)
    assert r.returncode != 0
    assert "formato Windows" in r.stdout
    assert "copiado e conferido" not in r.stdout
    assert set(os.listdir(RAIZ)) == antes


def test_destino_cuja_pasta_nao_existe_e_recusado(log_de_teste, area):
    """Mídia desmontada, ou letra errada, tem de falhar alto.

    `mkdir -p` inventando uma árvore de diretórios é o mesmo engano por
    outro caminho: a cópia existe, e não está na segunda mídia.
    """
    r = roda(COPIAR, rel(area / "nao-montada" / "midia"), log=log_de_teste)
    assert r.returncode != 0
    assert "nao existe" in r.stdout
    assert not (area / "nao-montada").exists()


def test_destino_dentro_do_repositorio_e_recusado(log_de_teste):
    """Cópia no mesmo disco não protege contra o disco — e dado de coleta
    dentro do repositório é commit acidental esperando acontecer."""
    antes = set(os.listdir(RAIZ / "docs"))
    r = roda(COPIAR, "docs/midia-de-teste", log=log_de_teste)
    assert r.returncode != 0
    assert "dentro do repositorio" in r.stdout
    assert set(os.listdir(RAIZ / "docs")) == antes


def test_nenhum_caminho_versionado_e_inclonavel():
    r"""O repositório tem de chegar de pé num clone.

    `:` e `\` dentro de um nome de arquivo viram caracteres de uso privado
    no Windows, e `git clone` falha no checkout — foi assim que o incidente
    apareceu, e nada no projeto o teria percebido sem tentar clonar.
    """
    bruto = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ,
                           capture_output=True).stdout
    caminhos = [c.decode("utf-8") for c in bruto.split(b"\0") if c]
    assert caminhos, "git ls-files nao devolveu nada"
    ruins = [c for c in caminhos if not SEGURO.match(c)]
    assert ruins == [], ruins


def test_nenhum_log_versionado():
    """O único JSONL deste projeto é log, e log não entra no repositório.

    A regra existia e era estreita: pegava `eventos.jsonl` e deixava passar
    `eventos-20261029-133345.jsonl`, que é justamente o nome que a cópia
    datada gera.
    """
    bruto = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ,
                           capture_output=True).stdout
    jsonl = [c.decode("utf-8") for c in bruto.split(b"\0")
             if c.endswith(b".jsonl")]
    assert jsonl == [], jsonl


# --------------------------------------------------------------------------
# Preparar o ensaio
#
# `scripts/ensaio.sh` não sobe servidor: confere o que precisa estar certo
# ANTES e imprime os comandos. Descobrir que o código não serve, ou que um
# servidor velho ficou no ar com outro tópico, com a pessoa sentada ao lado
# é o pior momento possível.
# --------------------------------------------------------------------------

ENSAIO = "scripts/ensaio.sh"


def _ensaio(*args):
    return subprocess.run(["bash", ENSAIO, *args], cwd=RAIZ,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def test_o_ensaio_imprime_os_comandos_com_o_ambiente_montado(area):
    r = _ensaio("E01", "--pasta", rel(area))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "STRUCTURA_TOPICO=kc_02" in r.stdout
    assert "STRUCTURA_LOG=" in r.stdout
    assert "python -m mvp.app" in r.stdout
    assert "python -m mvp.painel" in r.stdout
    # o código vai na URL: sem isso a sessão sai anônima
    assert "?codigo=E01" in r.stdout
    # e o que fazer depois, na ordem
    assert "copia.sh" in r.stdout


def test_o_ensaio_recusa_codigo_fora_do_formato(area):
    """A mesma regra do servidor. Um código com ponto ou barra passa aqui e
    estoura lá, ou pior: vira problema na hora de apagar."""
    for codigo in ("E 01", "../x", "7E", "E.01"):
        r = _ensaio(codigo, "--pasta", rel(area))
        assert r.returncode != 0, codigo
        assert "codigo fora do formato" in r.stdout, codigo


def test_o_ensaio_recusa_codigo_ja_usado(area, log_de_teste):
    """Abrir o mesmo código duas vezes juntaria duas pessoas num
    participante só."""
    destino = area / "kc_02.jsonl"
    destino.write_text(
        json.dumps({"v": 1, "sessao": "P02", "tipo": "unidade_iniciada"}) + chr(10),
        encoding="utf-8")
    r = _ensaio("P02", "--pasta", rel(area))
    assert r.returncode != 0
    assert "ja tem" in r.stdout
    livre = _ensaio("P03", "--pasta", rel(area))
    assert livre.returncode == 0, livre.stdout


def test_o_ensaio_recusa_topico_que_nao_carrega(area):
    """Domínio inválido falha na carga — e tem de falhar agora, não na
    frente de quem responde."""
    r = _ensaio("E01", "--pasta", rel(area), "--topico", "kc_99")
    assert r.returncode != 0
    assert "NAO carrega" in r.stdout


# --------------------------------------------------------------------------
# O CLIENTE PRECISA AO MENOS FAZER PARSE
# --------------------------------------------------------------------------
#
# Achado ao ampliar o cartao B3: um script meu escreveu uma expressao
# regular quebrada em `app.js`, partindo a linha no meio, e a suite
# inteira — 1026 testes — passou verde. Nenhum deles abre o cliente.
#
# Um `app.js` que nao faz parse derruba a sessao na primeira tela, e o
# participante ve uma pagina morta. E o tipo de defeito que custa o
# ensaio inteiro, e custa zero para pegar.

def _tem_node():
    import shutil
    return shutil.which("node") is not None


@pytest.mark.skipif(not _tem_node(), reason="sem node para conferir sintaxe")
@pytest.mark.parametrize("arquivo", ["app.js", "figuras.js"])
def test_o_javascript_do_cliente_faz_parse(arquivo):
    r = subprocess.run(["node", "--check", "mvp/web/%s" % arquivo],
                       cwd=RAIZ, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout


# --------------------------------------------------------------------------
# NENHUM BYTE DE CONTROLE NO FONTE
# --------------------------------------------------------------------------
#
# Cinco vezes numa sessao um escape se perdeu ao escrever arquivo por
# script: um regex do app.js virou quebra de linha de verdade, o
# especificador de nova linha de um printf no YAML partiu a linha em
# duas, e a borda-de-palavra de um teste virou o caractere BACKSPACE
# (0x08) — invisivel na listagem, e o teste passou a casar contra nada.
#
# O ultimo e o pior: o fonte parece certo na tela e esta errado no disco.
# Nenhuma revisao de codigo pega isso lendo.

@pytest.mark.parametrize("pasta", ["mvp", "scripts"])
def test_nenhum_byte_de_controle_invisivel_no_fonte(pasta):
    maus = []
    for caminho in sorted((RAIZ / pasta).rglob("*")):
        if caminho.suffix not in (".py", ".js", ".yaml", ".html", ".css", ".sh"):
            continue
        if "__pycache__" in caminho.parts:
            continue
        bruto = caminho.read_bytes()
        achados = sorted({b for b in bruto if b < 9 or (13 < b < 32)})
        if achados:
            maus.append((caminho.name, achados))
    assert not maus, maus
