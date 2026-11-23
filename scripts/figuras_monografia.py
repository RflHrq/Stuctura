"""As figuras da Seção 3 da monografia, tiradas do sistema em execução.

    python scripts/figuras_monografia.py                 # as sete
    python scripts/figuras_monografia.py 3.3 3.6         # só estas

Precisa do servidor de ENSAIO no ar (porta 8013, pasta ensaios/portal),
nunca do sistema em uso: as sessões que este script abre são simuladas.

O que ele faz, em duas partes:

1. LEVA uma sessão de ensaio até a tela de cada figura. As respostas saem
   dos alunos simulados (scripts/trilha_alunos.py), uma persona por
   premissa. O motor é puro e a sessão é a semente: o mesmo motor roda
   aqui em processo, para saber o que responder, e as mesmas entradas vão
   por HTTP ao servidor, que as grava no registro de ensaio. Os códigos
   começam com F e trazem a hora da rodada: não são participantes.

2. CAPTURA a página no Chrome sem janela, com um perfil descartável, na
   largura de um celular (390 px de CSS, 780 px de imagem). A captura vai
   do topo ao fim do conteúdo, e não só ao que cabe na janela. A tela
   comprida (o fechamento, a página inicial) é partida em três colunas,
   lidas de cima para baixo e da esquerda para a direita, com os cortes
   no vão entre dois blocos.

As figuras da versão entregue foram feitas por este script em 23/11/2026.
A ordem das alternativas sai do código da sessão: outra rodada dá as
mesmas telas, e as alternativas podem vir em outra ordem.

Depende de `requests`, `websockets` e `Pillow`, que não são dependências
do sistema: só deste script.
"""

from __future__ import annotations

import base64
import dataclasses
import io
import itertools
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from mvp import trilha  # noqa: E402
from mvp.dominio import carrega  # noqa: E402
from mvp.trilha_escada import le  # noqa: E402
import trilha_alunos  # noqa: E402

BASE = "http://127.0.0.1:8013"
SAIDA = RAIZ / "docs" / "monografia" / "figuras"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORTA = 9377
LARGURA, ALTURA = 390, 844
VAO = 36                             # o branco entre duas colunas, em px

SABE = ["sabe"]
ATE_A_QUINTA = ["sabe", "sabe", "sabe", "sabe", "crente_aprende", "sabe"]
# Uma premissa de cada jeito, para o fechamento mostrar todos os blocos
# que estas respostas produzem.
MISTA = ["sabe", "nao_sabe_aprende", "crente_aprende", "sabe",
         "crente_teimoso", "nao_sabe_erra", "inseguro"]

# figura -> as sessões de que ela precisa: (tópico, personas, onde parar)
SESSOES = {
    "3.1": [("kc_07", SABE, {"tipo": "pergunta", "premissa": "I1",
                             "papel": "abertura"})],
    "3.2": [("kc_07", ["sabe", "nao_sabe_aprende", "sabe"],
             {"tipo": "degrau", "premissa": "B2", "indice": 1})],
    "3.3": [("kc_07", MISTA, {"tipo": "mapa"})],
    "3.4a": [("kc_07", ATE_A_QUINTA, {"tipo": "voce_disse", "premissa": "I1"})],
    "3.4b": [("kc_07", ATE_A_QUINTA, {"tipo": "maquina", "premissa": "I1"})],
    "3.5": [("kc_06", ["nao_sabe_erra"], {"tipo": "revisao", "premissa": "B1"})],
    "3.6": [("kc_00", SABE, {"tipo": "mapa"}),
            ("kc_02", SABE, {"tipo": "pergunta", "papel": "abertura",
                             "feitas": 3})],
}


# ---------------------------------------------------------------- a sessão

def _bate(tela, estado, d, alvo) -> bool:
    for k, v in alvo.items():
        if k == "tipo":
            if tela.tipo != v:
                return False
        elif k == "feitas":
            if sum(1 for no in d.ordem if estado.premissa(no).resultado) != v:
                return False
        elif tela.dados.get(k) != v:
            return False
    return True


def leva(codigo: str, topico: str, personas, alvo) -> None:
    """A sessão `codigo` daquele tópico, até a tela que `alvo` descreve."""
    import requests

    d = carrega(topico=topico)
    escadas = le(RAIZ / "mvp" / "dominio" /
                 ("escada_%s.yaml" % topico.replace("_", "")), d)
    ordem = list(d.ordem)
    url = "%s/trilha/%s" % (BASE, topico)

    def persona_de(tela):
        no = tela.dados.get("premissa") or ""
        if no in ordem:
            return personas[min(ordem.index(no), len(personas) - 1)]
        return personas[-1]

    r = requests.post(url + "/sessoes", json={"codigo": codigo}, timeout=30)
    r.raise_for_status()
    j = r.json()
    t = trilha.inicia(d, escadas, semente=codigo)
    assert j["tela"]["tipo"] == "entrada", (
        "o código %s já tem sessão em %s" % (codigo, topico))

    def manda(entrada):
        nonlocal t, j
        corpo = {"acao": entrada.acao, "passo": j["passo"],
                 "escolha": entrada.escolha, "razao": entrada.razao,
                 "confianca": entrada.confianca, "pecas": list(entrada.pecas),
                 "texto": entrada.texto, "modo": entrada.modo,
                 "ritmo": entrada.ritmo, "ms": 6000}
        r = requests.post("%s/sessoes/%s/agir" % (url, codigo), json=corpo,
                          timeout=60)
        assert r.status_code == 200, (r.status_code, r.text[:300])
        j = r.json()
        t = trilha.avanca(d, escadas, t.estado,
                          dataclasses.replace(entrada, passo=t.estado.n))
        # O servidor e o motor em processo têm de estar na mesma tela.
        assert j["tela"]["tipo"] == t.tela.tipo, (j["tela"]["tipo"], t.tela.tipo)
        assert j["passo"] == t.estado.n, (j["passo"], t.estado.n)

    # O que a página manda no "Começar": só o ritmo.
    manda(trilha.Entrada(acao="comecar", ritmo="completo"))
    for _ in range(300):
        if _bate(t.tela, t.estado, d, alvo):
            break
        assert t.tela.tipo != "mapa", "chegou ao fechamento sem achar %r" % alvo
        manda(trilha_alunos.responde(d, escadas, t.tela, persona_de(t.tela),
                                     t.estado))
    else:
        raise RuntimeError("a sessão não chegou a %r" % alvo)
    print("  %s em %s: tela %s" % (codigo, topico, t.tela.tipo))


# ------------------------------------------------------------- o navegador

class Navegador:
    """O Chrome sem janela, comandado pela porta de depuração."""

    def __init__(self) -> None:
        from websockets.sync.client import connect

        self.perfil = tempfile.mkdtemp(prefix="structura-figuras-")
        self.proc = subprocess.Popen([
            CHROME, "--headless=new", "--remote-debugging-port=%d" % PORTA,
            "--remote-allow-origins=*", "--user-data-dir=%s" % self.perfil,
            "--no-first-run", "--no-default-browser-check",
            "--hide-scrollbars", "--mute-audio", "--disable-extensions",
            "about:blank"])
        self.ws = connect(self._alvo(), max_size=None)
        self.seq = 0

    def _alvo(self) -> str:
        for _ in range(60):
            try:
                with urllib.request.urlopen(
                        "http://127.0.0.1:%d/json/list" % PORTA, timeout=2) as r:
                    for t in json.load(r):
                        if t.get("type") == "page":
                            return t["webSocketDebuggerUrl"]
            except OSError:
                pass
            time.sleep(0.5)
        raise RuntimeError("o Chrome não abriu a porta de depuração")

    def fecha(self) -> None:
        try:
            self.ws.close()
        finally:
            self.proc.terminate()
            self.proc.wait(timeout=20)
            # O perfil é descartável: sai junto com o navegador.
            shutil.rmtree(self.perfil, ignore_errors=True)

    def cdp(self, metodo: str, **params):
        self.seq += 1
        self.ws.send(json.dumps({"id": self.seq, "method": metodo,
                                 "params": params}))
        while True:
            m = json.loads(self.ws.recv(timeout=60))
            if m.get("id") == self.seq:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (metodo, m["error"]))
                return m.get("result", {})

    def js(self, expr: str):
        r = self.cdp("Runtime.evaluate", expression=expr, awaitPromise=True,
                     returnByValue=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:600])
        return r["result"].get("value")

    def espera(self, expr: str, o_que: str, segundos: int = 20) -> None:
        fim = time.time() + segundos
        while time.time() < fim:
            if self.js(expr):
                return
            time.sleep(0.2)
        raise RuntimeError("não apareceu: %s" % o_que)

    def abre(self, caminho: str, tema: str) -> None:
        self.cdp("Emulation.setDeviceMetricsOverride", width=LARGURA,
                 height=ALTURA, deviceScaleFactor=2, mobile=True)
        self.cdp("Emulation.setEmulatedMedia", features=[
            {"name": "prefers-color-scheme",
             "value": "dark" if tema == "escuro" else "light"}])
        self.cdp("Page.navigate", url=BASE + caminho)
        self.espera("document.readyState === 'complete'", "a página")
        self.js("document.fonts.ready.then(function () { return true; })")
        assert self.js(
            "document.documentElement.getAttribute('data-tema')") == tema

    def trilha(self, topico: str, codigo: str) -> None:
        self.abre("/trilha/%s/?codigo=%s" % (topico, codigo), "claro")
        self.espera(
            "!!document.querySelector('#palco').children.length && "
            "!document.querySelector('#palco').classList.contains('t-ocupado')",
            "a tela da sessão")
        time.sleep(0.8)

    def clica(self, seletor: str, texto: str) -> None:
        ok = self.js("""(function () {
            var alvo = %s, nos = document.querySelectorAll(%s);
            for (var i = 0; i < nos.length; i++) {
                var n = nos[i];
                if (n.textContent.trim() === alvo && !n.disabled && n.offsetParent) {
                    n.click(); return true;
                }
            }
            return false;
        })()""" % (json.dumps(texto), json.dumps(seletor)))
        if not ok:
            raise RuntimeError("não achei %r em %s" % (texto, seletor))

    def _cortes(self, blocos: str, pula: str, colunas: int, total: int):
        """Onde partir a página: no vão entre dois blocos, e nunca no meio
        de um. A coluna mais alta fica o mais baixa possível; no empate,
        as colunas ficam o mais parecidas possível."""
        cand = self.js("""(function (sel, pula) {
            var r = Array.prototype.map.call(document.querySelectorAll(sel), function (n) {
                var b = n.getBoundingClientRect();
                return { t: b.top + window.scrollY, b: b.bottom + window.scrollY,
                         pula: pula ? n.matches(pula) : false };
            });
            r.sort(function (a, b) { return a.t - b.t; });
            var c = [];
            for (var i = 1; i < r.length; i++) {
                if (!r[i].pula) c.push((r[i - 1].b + r[i].t) / 2);
            }
            return c;
        })(%s, %s)""" % (json.dumps(blocos), json.dumps(pula)))
        cand = sorted(int(round(c)) for c in cand if 0 < c < total)
        melhor = None
        for combo in itertools.combinations(cand, colunas - 1):
            bordas = [0] + list(combo) + [total]
            alturas = [b - a for a, b in zip(bordas, bordas[1:])]
            nota = (max(alturas), sum(h * h for h in alturas))
            if melhor is None or nota < melhor[0]:
                melhor = (nota, bordas)
        return melhor[1]

    def fotografa(self, nome: str, ate: str = "", colunas: int = 1,
                  blocos: str = "", pula: str = "") -> None:
        from PIL import Image

        self.js("window.scrollTo(0, 0); document.activeElement && "
                "document.activeElement.blur(); true")
        time.sleep(0.6)
        total = self.cdp("Page.getLayoutMetrics")["cssContentSize"]["height"]
        if ate:
            fim = self.js(
                "(function () { var r = document.querySelector(%s)"
                ".getBoundingClientRect(); return r.bottom + window.scrollY; })()"
                % json.dumps(ate))
            total = min(total, fim + 20)
        total = int(round(total))
        # O fundo quadriculado é preso à janela (background-attachment:
        # fixed). A janela cresce até o fim do conteúdo para a captura, e
        # o fundo cobre a página inteira, como cobre para quem rola a tela.
        self.cdp("Emulation.setDeviceMetricsOverride", width=LARGURA,
                 height=total, deviceScaleFactor=2, mobile=True)
        time.sleep(0.6)
        r = self.cdp("Page.captureScreenshot", format="jpeg", quality=95,
                     clip={"x": 0, "y": 0, "width": LARGURA, "height": total,
                           "scale": 1})
        bruto = base64.b64decode(r["data"])
        destino = SAIDA / nome
        if colunas == 1:
            destino.write_bytes(bruto)
            print("  %s: %d x %d px de CSS" % (nome, LARGURA, total))
            return
        bordas = self._cortes(blocos, pula, colunas, total)
        inteira = Image.open(io.BytesIO(bruto)).convert("RGB")
        alturas = [2 * (b - a) for a, b in zip(bordas, bordas[1:])]
        tela = Image.new("RGB", (colunas * 2 * LARGURA + (colunas - 1) * VAO,
                                 max(alturas)), (255, 255, 255))
        for k, (a, b) in enumerate(zip(bordas, bordas[1:])):
            tela.paste(inteira.crop((0, 2 * a, 2 * LARGURA, 2 * b)),
                       (k * (2 * LARGURA + VAO), 0))
        tela.save(destino, quality=92)
        print("  %s: %d x %d px de CSS, em %d colunas"
              % (nome, LARGURA, total, colunas))


# -------------------------------------------------------------- as figuras

def f31(n: Navegador, codigo: str) -> None:
    n.trilha("kc_07", codigo)
    n.clica("#palco .opcoes .opcao", "Não se atribui ao nome do array")
    n.clica("#palco button", "Confirmar resposta")
    n.espera("!!Array.prototype.find.call("
             "document.querySelectorAll('#palco .t-pede'), function (x) {"
             " return x.textContent.trim() === 'Por quê?' && x.offsetParent; })",
             "as razões")
    n.fotografa("fig-3-1-pergunta.jpg", "#palco")


def f32(n: Navegador, codigo: str) -> None:
    n.trilha("kc_07", codigo)
    n.fotografa("fig-3-2-passo.jpg", "#palco")


def f33(n: Navegador, codigo: str) -> None:
    n.trilha("kc_07", codigo)
    n.fotografa("fig-3-3-fechamento.jpg", "#palco", colunas=3,
                blocos="#palco .t-sumario, #palco .t-sub, #palco .mapa > *",
                pula="#palco .mapa > :first-child")


def f34a(n: Navegador, codigo: str) -> None:
    n.trilha("kc_07", codigo)
    n.fotografa("fig-3-4a-voce-disse.jpg", "#palco")


def f34b(n: Navegador, codigo: str) -> None:
    n.trilha("kc_07", codigo)
    n.fotografa("fig-3-4b-maquina.jpg", "#palco")


def f35(n: Navegador, codigo: str) -> None:
    """A cena parada na linha da função: a cópia `n` acabou de virar 0."""
    n.trilha("kc_06", codigo)
    n.espera("!!document.querySelector('#palco .cena')", "a cena")
    for _ in range(40):
        frase = n.js("document.querySelector('#palco .cn-frase').textContent")
        if frase.startswith("Linha 1: guarda 0 em n"):
            break
        n.clica("#palco .cn-botoes button", "Passo")
        time.sleep(0.15)
    else:
        raise RuntimeError("a cena não chegou à linha da função")
    n.fotografa("fig-3-5-cena.jpg", "#palco")


def f36(n: Navegador, codigo: str) -> None:
    """A página inicial lê do navegador o andamento que a página da trilha
    anotou: as duas sessões são abertas antes, no mesmo navegador."""
    n.trilha("kc_00", codigo)
    n.trilha("kc_02", codigo)
    n.abre("/", "escuro")
    n.espera("document.querySelector('#prox-titulo').textContent.trim() !== '…'",
             "o próximo sugerido")
    time.sleep(0.8)
    n.fotografa("fig-3-6-inicio-escuro.jpg", colunas=3,
                blocos=".p-casa, #todos, #lista > li",
                pula="#lista > li:first-child")


FIGURAS = {"3.1": f31, "3.2": f32, "3.3": f33, "3.4a": f34a, "3.4b": f34b,
           "3.5": f35, "3.6": f36}


def main(args: list[str] | None = None) -> int:
    quais = list(args if args is not None else sys.argv[1:]) or list(FIGURAS)
    for q in quais:
        if q not in FIGURAS:
            print("figura desconhecida: %s (há %s)" % (q, ", ".join(FIGURAS)))
            return 2
    marca = time.strftime("%m%d%H%M%S")
    for q in quais:
        # Um código por figura, e um navegador por figura: o que uma
        # sessão anota no navegador não aparece na página inicial de outra.
        codigo = "F%s-%s" % (q.replace(".", ""), marca)
        print("Figura %s" % q)
        for topico, personas, alvo in SESSOES[q]:
            leva(codigo, topico, personas, alvo)
        n = Navegador()
        try:
            FIGURAS[q](n, codigo)
        finally:
            n.fecha()
    return 0


if __name__ == "__main__":
    sys.exit(main())
