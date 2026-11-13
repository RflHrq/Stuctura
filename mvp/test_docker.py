"""O empacotamento em Docker: o que ele não pode fazer calado.

    docker compose up -d --build     →  http://127.0.0.1:8010

O contêiner serve o portal (`mvp/portal.py`) e mais nada. Estes testes
não sobem contêiner — isso é verificação de quem empacota, e está
descrita no `docs/docker.md`. O que eles guardam são as quatro decisões
do empacotamento que, erradas, não dão erro nenhum:

    a porta só na máquina   o sistema não tem login, e o registro guarda
                            o que os participantes escrevem. Publicar a
                            porta em todas as interfaces o poria na rede
                            inteira sem ninguém ter decidido isso;
    os dados fora do git    a pasta em que o contêiner grava tem de
                            estar no .gitignore, ou uma coleta vai
                            parar num commit;
    as versões iguais       a imagem instala as MESMAS versões em que a
                            suíte roda — é a razão de o requirements.txt
                            fixá-las;
    o padrão intacto        fora do contêiner, o portal continua
                            escutando só em 127.0.0.1.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mvp import portal


def _pins(arquivo: Path) -> dict[str, str]:
    """`pacote==versao` de um requirements, sem comentário nem extra."""
    fora = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.split("#", 1)[0].strip()
        m = re.match(r"^([A-Za-z0-9_.-]+)(\[[^\]]*\])?==(\S+)$", linha)
        if m:
            fora[m.group(1).lower()] = (m.group(2) or "") + "==" + m.group(3)
    return fora


# --------------------------------------------------------------------------
# O endereço em que o portal escuta
# --------------------------------------------------------------------------

def test_sem_configuracao_o_portal_escuta_so_na_maquina(monkeypatch):
    monkeypatch.delenv("STRUCTURA_HOST", raising=False)
    monkeypatch.delenv("STRUCTURA_PORTA", raising=False)
    assert portal.endereco() == ("127.0.0.1", 8010)


def test_o_conteiner_pode_pedir_outro_endereco(monkeypatch):
    """Dentro do contêiner, 127.0.0.1 é o contêiner: ninguém de fora chega."""
    monkeypatch.setenv("STRUCTURA_HOST", "0.0.0.0")
    monkeypatch.setenv("STRUCTURA_PORTA", "9000")
    assert portal.endereco() == ("0.0.0.0", 9000)


def test_porta_que_nao_e_numero_falha_alto(monkeypatch):
    monkeypatch.setenv("STRUCTURA_PORTA", "oitenta")
    try:
        portal.endereco()
    except SystemExit as erro:
        assert "STRUCTURA_PORTA" in str(erro)
    else:
        raise AssertionError("porta inválida passou calada")


# --------------------------------------------------------------------------
# O compose
# --------------------------------------------------------------------------

def _compose() -> dict:
    return yaml.safe_load(
        (RAIZ / "docker-compose.yml").read_text(encoding="utf-8"))


def test_a_porta_e_publicada_so_na_propria_maquina():
    """`8010:8010` publicaria em todas as interfaces. Tem de ser 127.0.0.1."""
    portas = _compose()["services"]["portal"]["ports"]
    assert portas, "o serviço não publica porta nenhuma"
    for p in portas:
        assert str(p).startswith("127.0.0.1:"), (
            "%r publica o sistema na rede. Ele não tem login, e o registro "
            "guarda texto de participante: abrir para a rede tem de ser "
            "decisão escrita, não o padrão." % p)


def test_o_conteiner_sobe_sozinho_de_novo():
    """É o "deixar ativado": cai e volta, e volta quando o Docker inicia."""
    assert _compose()["services"]["portal"]["restart"] == "unless-stopped"


def test_os_dados_ficam_numa_pasta_da_maquina_e_fora_do_git():
    servico = _compose()["services"]["portal"]
    volumes = [str(v) for v in servico["volumes"]]
    assert len(volumes) == 1, volumes
    origem, destino = volumes[0].split(":", 1)
    # A pasta do contêiner é a que o portal usa.
    assert servico["environment"]["STRUCTURA_PASTA"] == destino
    # E a da máquina não pode ir para um commit.
    pasta = origem.lstrip("./").split("/")[0]
    ignoradas = [x.strip().rstrip("/") for x in
                 (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()]
    assert pasta in ignoradas, (
        "a pasta %r recebe os registros do contêiner e não está no "
        ".gitignore" % pasta)


def test_o_conteiner_nao_grava_na_pasta_dos_ensaios():
    """Ensaio e coleta em arquivos diferentes, desde a primeira subida.

    `ensaios/portal/` tem as sessões simuladas de quando o portal foi
    verificado. Se o contêiner gravasse lá, a primeira sessão de verdade
    nasceria misturada com elas.
    """
    origem = str(_compose()["services"]["portal"]["volumes"][0]).split(":")[0]
    assert "ensaios" not in origem, origem


# --------------------------------------------------------------------------
# A imagem
# --------------------------------------------------------------------------

def test_a_imagem_instala_as_versoes_em_que_a_suite_roda():
    da_suite = _pins(RAIZ / "requirements.txt")
    da_imagem = _pins(RAIZ / "docker" / "requirements.txt")
    assert da_imagem, "docker/requirements.txt sem versão fixa nenhuma"
    for pacote, versao in da_imagem.items():
        assert da_suite.get(pacote) == versao, (
            "%s: a imagem instala %s e a suíte roda em %s"
            % (pacote, versao, da_suite.get(pacote)))


def test_a_imagem_nao_leva_teste_nem_dado():
    ignora = (RAIZ / ".dockerignore").read_text(encoding="utf-8").splitlines()
    ignora = [x.strip() for x in ignora if x.strip() and not x.startswith("#")]
    for padrao in (".git", "ensaios", "coleta", "data", "mvp/dados",
                   "mvp/test_*.py"):
        assert padrao in ignora, "%r tinha de estar no .dockerignore" % padrao


def test_a_imagem_nao_roda_como_root():
    texto = (RAIZ / "Dockerfile").read_text(encoding="utf-8")
    usuarios = re.findall(r"^USER\s+(\S+)", texto, re.M)
    assert usuarios and usuarios[-1] not in ("root", "0"), usuarios
