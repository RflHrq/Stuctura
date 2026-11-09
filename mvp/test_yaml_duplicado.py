# -*- coding: utf-8 -*-
"""Nenhum YAML do domínio tem chave duplicada.

A OCORRÊNCIA QUE PEDIU ESTE ARQUIVO, 09/11/2026. Ao promover o conceito
`array` eu escrevi `tipo: explicacao_com_exemplo` dentro da `evidencia`,
e o entry antigo já tinha `tipo: nao_auditado` algumas linhas abaixo —
fora do trecho que eu estava editando. `yaml.safe_load` aceita a
duplicata **em silêncio** e fica com a ÚLTIMA, então o conceito entrou
no domínio com o tipo errado e o inventário passou a dizer que a
explicação não foi auditada.

Nada estourou. Quem pegou foi um teste de conteúdo
(`test_so_quem_tem_explicacao_declara_cartao`), e por sorte: ele cobre
`tipo`. Uma duplicata em campo sem teste passaria.

É o modo de falha pior que existe num arquivo de dado curado — a
mudança parece aplicada, o arquivo parece certo quando se lê de cima
para baixo, e o valor que vale é outro. Este arquivo fecha a classe
inteira, e não só o caso.
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

DOMINIO = pathlib.Path(__file__).resolve().parent / "dominio"
CANDIDATOS = pathlib.Path(__file__).resolve().parent.parent / "candidatos"


class _Vigia(yaml.SafeLoader):
    """SafeLoader que RECUSA chave repetida, em vez de ficar com a última."""


def _mapa(loader, node, deep=False):
    fora = {}
    for chave, valor in node.value:
        k = loader.construct_object(chave, deep=deep)
        if k in fora:
            raise yaml.constructor.ConstructorError(
                None, None,
                "chave duplicada %r na linha %d (a primeira está na %d)"
                % (k, chave.start_mark.line + 1, fora[k] + 1),
                chave.start_mark)
        fora[k] = chave.start_mark.line
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_Vigia.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapa)


def _arquivos():
    return sorted(DOMINIO.glob("*.yaml")) + sorted(CANDIDATOS.glob("*/*.yaml"))


def test_o_vigia_pega_duplicata():
    """Primeiro o teste do teste: um vigia que não pega nada passaria em
    todo arquivo e não guardaria coisa alguma."""
    cru = "a: 1" + chr(10) + "b: 2" + chr(10) + "a: 3" + chr(10)
    assert yaml.safe_load(cru) == {"a": 3, "b": 2}, "o safe_load mudou"
    with pytest.raises(yaml.constructor.ConstructorError) as erro:
        yaml.load(cru, Loader=_Vigia)
    assert "duplicada" in str(erro.value)


def test_o_vigia_pega_duplicata_aninhada():
    """O caso real era dentro de um mapa aninhado, não no topo."""
    cru = chr(10).join(["conceitos:", "  array:", "    tipo: bom",
                        "    nome: x", "    tipo: ruim", ""])
    with pytest.raises(yaml.constructor.ConstructorError):
        yaml.load(cru, Loader=_Vigia)


@pytest.mark.parametrize("caminho", _arquivos(),
                         ids=lambda p: "%s/%s" % (p.parent.name, p.name))
def test_nenhuma_chave_duplicada(caminho):
    """Todo YAML de domínio e de candidato, um por um.

    Quando este teste cair: a chave repetida está na linha que a
    mensagem diz, e o valor que VALE hoje é o da última. Decida qual é o
    certo antes de apagar a outra.
    """
    try:
        yaml.load(caminho.read_text(encoding="utf-8"), Loader=_Vigia)
    except yaml.constructor.ConstructorError as erro:
        pytest.fail("%s: %s" % (caminho.name, erro))
