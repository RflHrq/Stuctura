#!/usr/bin/env bash
# Os dados de um participante, pelo código da sessão.
#
#   scripts/participante.sh ver     P07
#   scripts/participante.sh apagar  P07
#   scripts/participante.sh apagar  P07 --log outro/eventos.jsonl
#   scripts/participante.sh apagar  P07 --confirmo P07   (sem perguntar)
#
# O PRD declara: "o participante pode pedir a exclusão dos dados dele pelo
# código". Declarar um direito e não ter como exercê-lo é problema de
# conformidade, não de conveniência — e o texto vai ao comitê de ética.
#
# APAGAR É IRREVERSÍVEL, e o log de uma coleta é irreproduzível: a pessoa
# não volta para refazer. Por isso aqui se mostra o que será apagado, se
# pede confirmação, e se guarda uma cópia do arquivo antes de reescrevê-lo.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${STRUCTURA_LOG:-$AQUI/mvp/dados/eventos.jsonl}"

verde() { printf '\033[32m%s\033[0m\n' "$1"; }
vermelho() { printf '\033[31m%s\033[0m\n' "$1"; }

uso() {
  echo "uso: $0 {ver|apagar} <codigo-da-sessao> [--log <arquivo>] [--confirmo <codigo>]"
  exit 2
}

[ $# -ge 2 ] || uso
acao="$1"; codigo="$2"; shift 2
confirmo=""
while [ $# -gt 0 ]; do
  case "$1" in
    --log)      [ -n "${2:-}" ] || uso; LOG="$2"; shift 2 ;;
    # A garantia nao e ser interativo: e DIZER O CODIGO DUAS VEZES. Quem
    # chama de outro script precisa de um caminho sem pergunta, e este
    # exige a mesma coisa que o teclado exigiria.
    --confirmo) [ -n "${2:-}" ] || uso; confirmo="$2"; shift 2 ;;
    *)          uso ;;
  esac
done

# Caminho estilo Windows chega literal quando quem chama nao e shell, e aqui
# o estrago seria dizer "nenhuma linha com este codigo" sobre um arquivo que
# nunca foi aberto — a pessoa pediria a exclusao e nada seria apagado.
case "$LOG" in
  *\\*|[A-Za-z]:*)
    vermelho "log em formato Windows: $LOG"
    echo "use o caminho no formato do shell: /d/eventos.jsonl"
    exit 2 ;;
esac

[ -f "$LOG" ] || { vermelho "nao achei o log: $LOG"; exit 1; }

# O código entra como VALOR comparado campo a campo, nunca como pedaço de
# expressão regular: um código com ponto ou colchete casaria linhas de
# outros participantes, e apagar demais é pior do que não apagar.
contar() {
  python -c '
import json, sys
alvo = sys.argv[2]
n = 0
for linha in open(sys.argv[1], encoding="utf-8"):
    linha = linha.strip()
    if not linha:
        continue
    try:
        if json.loads(linha).get("sessao") == alvo:
            n += 1
    except json.JSONDecodeError:
        pass
print(n)
' "$LOG" "$codigo"
}

total=$(contar)

case "$acao" in
  ver)
    echo "codigo:  $codigo"
    echo "arquivo: $LOG"
    echo "linhas:  $total"
    [ "$total" -eq 0 ] && { vermelho "nenhuma linha com este codigo"; exit 1; }
    python -c '
import json, sys
from collections import Counter
alvo = sys.argv[2]
tipos = Counter()
texto = 0
for linha in open(sys.argv[1], encoding="utf-8"):
    linha = linha.strip()
    if not linha:
        continue
    try:
        d = json.loads(linha)
    except json.JSONDecodeError:
        continue
    if d.get("sessao") != alvo:
        continue
    tipos[d["tipo"]] += 1
    if d.get("texto"):
        texto += 1
print("  com texto livre do participante: %d" % texto)
for t, n in sorted(tipos.items()):
    print("  %-24s %d" % (t, n))
' "$LOG" "$codigo"
    ;;

  apagar)
    [ "$total" -eq 0 ] && { vermelho "nenhuma linha com o codigo $codigo"; exit 1; }
    outros=$(python -c '
import json, sys
s = set()
for linha in open(sys.argv[1], encoding="utf-8"):
    linha = linha.strip()
    if not linha:
        continue
    try:
        c = json.loads(linha).get("sessao")
    except json.JSONDecodeError:
        continue
    if c and c != sys.argv[2]:
        s.add(c)
print(len(s))
' "$LOG" "$codigo")

    echo "vai apagar $total linhas do codigo $codigo"
    echo "ficam $outros outras sessoes no arquivo"
    # A confirmacao e escrever o codigo de novo. Nao ha como pular: um
    # comando irreversivel que aceita "sim" aceita tambem o enter dado
    # sem ler, e o log de uma coleta nao volta.
    if [ -n "$confirmo" ]; then
      resposta="$confirmo"
    else
      printf 'confirma? escreva o codigo de novo: '
      # `|| true`: sem isto, entrada que acaba sem quebra de linha
      # devolve EOF, o `set -e` mata o script antes da comparacao, e um
      # comando destrutivo sai em silencio sem dizer por que.
      resposta=''
      read -r resposta || true
    fi
    [ "$resposta" = "$codigo" ] || { vermelho "nao confere; nada foi apagado"; exit 1; }

    copia="$LOG.antes-de-apagar-$(date +%Y%m%d-%H%M%S)"
    cp "$LOG" "$copia"

    python -c '
import json, sys
alvo, origem, destino = sys.argv[2], sys.argv[1], sys.argv[3]
with open(destino, "w", encoding="utf-8", newline="") as saida:
    for linha in open(origem, encoding="utf-8"):
        bruta = linha.rstrip("\n")
        if not bruta.strip():
            continue
        try:
            fora = json.loads(bruta).get("sessao") == alvo
        except json.JSONDecodeError:
            # Linha ilegivel nao e de ninguem, e apagar o que nao se
            # consegue ler seria apagar o que nao se sabe.
            fora = False
        if not fora:
            saida.write(bruta + "\n")
' "$copia" "$codigo" "$LOG"

    restam=$(contar)
    if [ "$restam" -ne 0 ]; then
      vermelho "sobraram $restam linhas; o arquivo anterior esta em $copia"
      exit 1
    fi
    verde "apagadas $total linhas do codigo $codigo"
    echo "copia de antes: $copia"
    echo "apague a copia quando o pedido estiver cumprido e conferido."
    ;;

  *) uso ;;
esac
