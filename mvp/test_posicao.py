"""A posição da alternativa certa.

Nos 562 itens dos treze tópicos, a resposta certa estava na **primeira**
alternativa em 553 deles — 98,4%. Isso não é detalhe de apresentação: o
instrumento passa a medir, em parte, quem reparou no padrão, e o viés é
sistemático, então não some na média de 40 participantes.

Pior: ele contamina a medida central do trabalho. Quem acerta por posição
ainda escolhe uma razão, e o par sai "acerto com razão errada" — que o
CS-1 lê como falso positivo. O viés produziria falsos positivos em massa,
e eles pareceriam achado.

A permutação já existia no motor, escrita para a camada das razões
(`ordem_das_razoes`). A camada 1 ficou de fora, e os 98,4% são a
consequência disso. O desenho está em [../docs/posicao.md](../docs/posicao.md).
"""

from __future__ import annotations

import collections

import pytest

from mvp import motor
from mvp.dominio import carrega

D = carrega(topico="kc_07")


@pytest.fixture(scope="module")
def d():
    return D


# --------------------------------------------------------------------------
# A permutação
# --------------------------------------------------------------------------

def test_a_ordem_e_estavel(d):
    a = d.atividades[0]
    assert (motor.ordem_das_opcoes("P01", a.id, 3)
            == motor.ordem_das_opcoes("P01", a.id, 3))


def test_a_ordem_e_uma_permutacao(d):
    for n in (2, 3, 4):
        assert sorted(motor.ordem_das_opcoes("P01", "x", n)) == list(range(n))


def test_sementes_diferentes_dao_ordens_diferentes(d):
    """O que mata o vazamento entre participantes: o P03 contar ao P04
    que "a do array é a terceira" não transfere."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    ordens = {motor.ordem_das_opcoes("P%02d" % i, a.id, 3) for i in range(1, 41)}
    assert len(ordens) > 1, ordens


def test_a_semente_vazia_nao_devolve_a_ordem_do_arquivo(d):
    """Sessão sem código não é desculpa para o viés voltar."""
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    assert motor.ordem_das_opcoes("", a.id, 3) != (0, 1, 2)


def test_as_duas_camadas_nao_recebem_a_mesma_permutacao(d):
    """Se recebessem, a posição da resposta prediria a posição da razão —
    um segundo viés no lugar do primeiro. Medido no banco inteiro: duas
    funções iguais dariam 100%."""
    tres = [x for x in d.atividades if len(x.opcoes) == 3]
    iguais = sum(motor.ordem_das_opcoes("P01", x.id, 3)
                 == motor.ordem_das_razoes("P01", x.id, 3) for x in tres)
    assert iguais < len(tres) * 0.5, (iguais, len(tres))


def test_itens_diferentes_podem_coincidir(d):
    """Contraprova: colisão de digest entre itens é esperada e inofensiva.
    Nenhum teste pode exigir que ordens de itens diferentes difiram."""
    tres = [x for x in d.atividades if len(x.opcoes) == 3]
    ordens = [motor.ordem_das_opcoes("P01", x.id, 3) for x in tres]
    assert len(set(ordens)) <= 6, "são 6 permutações possíveis para n=3"


def test_o_indice_certo_na_tela_aponta_a_alternativa_certa(d):
    a = next(x for x in d.atividades if len(x.opcoes) == 3)
    ordem = motor.ordem_das_opcoes("P01", a.id, 3)
    i = motor.indice_correto_na_tela("P01", a)
    assert a.opcoes[ordem[i]].correta


def test_a_escala_de_confianca_nao_e_embaralhada():
    """Fronteira de escopo, pinada. `CONFIANCAS` é ORDINAL: a ordem dela
    É a escala, e embaralhar destruiria a leitura. Além disso o viés nem
    existe ali, porque nenhuma das três é a certa."""
    assert motor.CONFIANCAS == ("chutei", "acho que sei", "tenho certeza")


# --------------------------------------------------------------------------
# A trava contra o erro silencioso
# --------------------------------------------------------------------------

def test_nao_existe_mais_indice_correto_sem_qualificacao(d):
    """A trava desta fatia.

    O nome antigo dizia "a posição da certa", e essa pergunta passou a
    ter duas respostas: no arquivo e na tela. Enquanto ele existir, as
    22 chamadas continuam executando e querendo dizer a errada — e o
    motor ACEITA o índice: não é erro de programa, é uma resposta
    errada. A escada desce em vez de subir, a crença errada é
    registrada, e a suíte fica verde contando outra história.

    Renomear troca 22 erros silenciosos por 22 `AttributeError`.
    """
    a = d.atividades[0]
    # O nome velho, escrito por partes: uma renomeação em massa pelo
    # arquivo inteiro já o comeu aqui uma vez, e o teste passou a dizer
    # o contrário do que foi escrito para dizer.
    velho = "indice_" + "correto"
    assert not hasattr(a, velho)
    assert isinstance(a.indice_correto_no_arquivo, int)
