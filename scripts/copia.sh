#!/usr/bin/env bash
# A copia do log depois de cada sessao.
#
#   scripts/copia.sh /caminho/da/segunda/midia
#   scripts/copia.sh /caminho/da/segunda/midia --log outro/eventos.jsonl
#
# O PRD exige: "depois de cada sessao, o log vai para uma segunda midia",
# com PERDA TOLERAVEL ZERO. O log de uma coleta e irreproduzivel — a
# pessoa nao volta para refazer. Ate agora a protecao contra perder a
# coleta inteira era lembrar de copiar um arquivo.
#
# A copia e datada e nao sobrescreve nada: a de ontem continua la.
# Depois de copiar, CONFERE — copia que nunca foi conferida nao e copia,
# do mesmo jeito que backup que nunca foi restaurado nao e backup. O
# ensaio de restauracao e outra coisa, e e da revisao final.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
LOG="${STRUCTURA_LOG:-$AQUI/mvp/dados/eventos.jsonl}"

verde() { printf '\033[32m%s\033[0m\n' "$1"; }
vermelho() { printf '\033[31m%s\033[0m\n' "$1"; }

uso() {
  echo "uso: $0 <pasta-de-destino> [--log <arquivo>]"
  echo "     $0 conferir <arquivo> <copia>"
  exit 2
}

# A conferencia, isolada, para poder ser exercitada por teste. Copia que
# nunca foi conferida nao e copia, e checagem que nunca falhou num teste
# e so uma linha bonita no script.
if [ "${1:-}" = "conferir" ]; then
  [ $# -eq 3 ] || uso
  if cmp -s "$2" "$3"; then
    verde "confere"
  else
    vermelho "a copia NAO confere com o original: $3"
    exit 1
  fi
  exit 0
fi

[ $# -ge 1 ] || uso
destino="$1"; shift
if [ "${1:-}" = "--log" ]; then
  [ -n "${2:-}" ] || uso
  LOG="$2"; shift 2
fi
[ $# -eq 0 ] || uso

[ -f "$LOG" ] || { vermelho "nao achei o log: $LOG"; exit 1; }

# TRES GUARDAS NO DESTINO. Cada uma existe por um jeito real de a copia
# nao estar onde se pensa que ela esta — e backup que o operador acredita
# ter e nao tem e pior do que nenhum: ele para de conferir.

# 1. Caminho estilo Windows. Chamado por quem nao e shell (um teste, o
# PowerShell, outro script), `D:\coleta` chega LITERAL: `mkdir -p` cria uma
# pasta com esse nome dentro do diretorio atual, `cp` escreve nela, e o
# script diz "copiado e conferido". Foi exatamente assim que 2,8 MB de log
# de desenvolvimento entraram no repositorio, achados na revisao final.
case "$destino" in
  *\\*|[A-Za-z]:*)
    vermelho "destino em formato Windows: $destino"
    echo "use o caminho no formato do shell: /d/coleta em vez de D:\\coleta"
    exit 2 ;;
esac

# 2. A pasta que vai CONTER o destino tem de existir. Midia desmontada ou
# letra errada precisa falhar alto, nao inventar uma arvore de diretorios.
pai="$(dirname "$destino")"
if [ ! -d "$pai" ]; then
  vermelho "a pasta que conteria o destino nao existe: $pai"
  echo "a segunda midia precisa estar montada antes de copiar."
  exit 1
fi

# 3. Copia dentro do repositorio nao e segunda midia: e o mesmo disco, e e
# o caminho curto para dado de coleta virar commit.
pai_real="$(cd "$pai" && pwd -P)"
case "$pai_real/" in
  "$AQUI"/*)
    vermelho "o destino esta dentro do repositorio: $pai_real"
    echo "copia no mesmo disco nao protege contra o disco, e dado de"
    echo "coleta versionado por acidente ja aconteceu neste projeto."
    exit 2 ;;
esac

mkdir -p "$destino"

carimbo="$(date +%Y%m%d-%H%M%S)"
alvo="$destino/eventos-$carimbo.jsonl"
[ -e "$alvo" ] && { vermelho "ja existe: $alvo"; exit 1; }

cp "$LOG" "$alvo"

# Conferencia byte a byte, pelo mesmo caminho que o subcomando `conferir`
# exercita. `cmp` existe no Git Bash e nao depende de sha256sum.
# A saida da conferencia aparece de proposito: e ela que diz que a copia
# foi conferida, e e o que um teste consegue observar de fora.
bash "${BASH_SOURCE[0]}" conferir "$LOG" "$alvo" || exit 1

linhas=$(grep -c "" "$LOG" || true)
sessoes=$(python -c '
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
    if c:
        s.add(c)
print(len(s))
' "$LOG")

verde "copiado e conferido"
echo "  de:      $LOG"
echo "  para:    $alvo"
echo "  linhas:  $linhas"
echo "  sessoes: $sessoes"
echo
echo "a pasta de destino precisa estar em OUTRA midia — copia no mesmo"
echo "disco nao protege contra o disco."
