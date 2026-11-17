"""A interface nova da trilha e da página inicial (docs/interface.md).

O que dá para conferir lendo os arquivos e rodando os scripts da página
no Node: as fontes e o ícone estão no projeto, com licença; nada é
carregado de outro endereço; os dois temas passam no contraste; o tema é
escolhido antes de a página aparecer, mesmo sem `localStorage`; o realce
de código devolve o texto idêntico; e cada peça das telas está vestida.

O resto — se o desenho ficou como nos esboços — é conferência no
navegador, nos passos do plano (docs/plano-interface.md).
"""

from __future__ import annotations

import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent
WEB = RAIZ / "web"
FONTES = WEB / "fontes"


# --------------------------------------------------------------------------
# As fontes e o ícone
# --------------------------------------------------------------------------

def test_as_fontes_estao_no_projeto_com_licenca():
    for nome in ("nunito", "jetbrains-mono"):
        dados = (FONTES / f"{nome}.woff2").read_bytes()
        assert dados[:4] == b"wOF2", nome
        assert 10_000 < len(dados) < 400_000, nome
        licenca = (FONTES / f"LICENCA-{nome}.txt").read_text(encoding="utf-8")
        assert "SIL OPEN FONT LICENSE" in licenca.upper(), nome


def test_o_icone_da_aba_e_o_s_que_e_um_ponteiro():
    svg = (WEB / "marca.svg").read_text(encoding="utf-8")
    assert svg.lstrip().startswith("<svg") and "viewBox" in svg
    assert "http" not in svg.replace('xmlns="http://www.w3.org/2000/svg"', "")
