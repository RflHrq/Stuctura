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
import subprocess
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
# Caminhos RELATIVOS: o bash do Git no Windows não abre um caminho com
# barras invertidas, e os testes rodam com `cwd=RAIZ`.
APAGAR = "scripts/participante.sh"
COPIAR = "scripts/copia.sh"


def roda(script, *args, log=None, confirma=None):
    """Roda o script de verdade, com o log passado por argumento.

    `confirma` vira `--confirmo`, que é como `apagar` aceita a
    confirmação sem perguntar. Não é porta dos fundos: a garantia do
    comando não é ser interativo, é **dizer o código duas vezes**, e
    `--confirmo` exige exatamente o mesmo que o teclado exigiria.

    (O bash deste ambiente não recebe a entrada padrão de um
    subprocesso, então testar pela pergunta não era possível aqui.)
    """
    # Caminho RELATIVO à raiz: o bash que o Python encontra no PATH aqui
    # é o de `Git/usr/bin`, que não traduz caminho com letra de unidade.
    # Por isso o log de teste vive dentro do repositório.
    extra = ["--log", log.relative_to(RAIZ).as_posix()] if log is not None else []
    if confirma is not None:
        extra += ["--confirmo", confirma]
    return subprocess.run(["bash", script, *args, *extra], cwd=RAIZ,
                          capture_output=True, text=True)


@pytest.fixture
def area(tmp_path_factory):
    """Área de trabalho DENTRO do repositório, apagada no fim.

    Os scripts recebem um caminho relativo à raiz — ver `roda`.
    """
    import shutil
    import tempfile

    pasta = pathlib.Path(tempfile.mkdtemp(prefix="teste-procedimentos-",
                                          dir=RAIZ))
    try:
        yield pasta
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


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
    r = roda(COPIAR, destino.relative_to(RAIZ).as_posix(), log=log_de_teste)
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
    roda(COPIAR, destino.relative_to(RAIZ).as_posix(), log=log_de_teste)
    primeira = list(destino.glob("eventos-*.jsonl"))[0]
    conteudo = primeira.read_bytes()

    log_de_teste.write_text(log_de_teste.read_text(encoding="utf-8") +
                            '{"v": 1, "sessao": "P04", "tipo": "x"}\n',
                            encoding="utf-8")
    import time
    time.sleep(1.1)             # o carimbo tem segundos
    roda(COPIAR, destino.relative_to(RAIZ).as_posix(), log=log_de_teste)

    assert len(list(destino.glob("eventos-*.jsonl"))) == 2
    assert primeira.read_bytes() == conteudo


def test_copiar_sem_log_falha_em_vez_de_criar_arquivo_vazio(area):
    """Uma cópia vazia de um log que não foi achado seria pior do que
    erro: pareceria proteção."""
    destino = area / "midia"
    r = roda(COPIAR, destino.relative_to(RAIZ).as_posix(),
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
                    x.relative_to(RAIZ).as_posix(),
                    y.relative_to(RAIZ).as_posix())

    assert conferir(igual_a, igual_b).returncode == 0
    ruim = conferir(igual_a, diferente)
    assert ruim.returncode != 0
    assert "NAO confere" in ruim.stdout
