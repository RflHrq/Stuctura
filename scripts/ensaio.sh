#!/usr/bin/env bash
# Prepara uma sessao de ensaio e diz como subir.
#
#   scripts/ensaio.sh E01
#   scripts/ensaio.sh P07 --topico kc_00 --pasta ensaios
#
# NAO sobe servidor: confere o que precisa estar certo ANTES e imprime os
# dois comandos, com o ambiente ja montado. Quem sobe e voce, e os dois
# terminais ficam a vista — se um cair no meio da sessao, da para ver.
#
# O que ele confere, e por que cada um:
#
#   o formato do codigo   e o mesmo que o servidor exige; descobrir que o
#                         codigo nao serve com a pessoa sentada e o pior
#                         momento possivel;
#   o codigo nao usado    abrir o mesmo codigo duas vezes juntaria duas
#                         pessoas num participante so;
#   o topico carrega      dominio invalido falha na carga, e isso tem de
#                         acontecer agora, nao na frente de quem responde;
#   as portas livres      servidor velho esquecido no ar atende com outro
#                         topico e outro log, e ninguem percebe;
#   a pasta do ensaio     dado de ensaio longe do log de desenvolvimento.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

verde()    { printf '\033[32m%s\033[0m\n' "$1"; }
vermelho() { printf '\033[31m%s\033[0m\n' "$1"; }

uso() {
  echo "uso: $0 <codigo> [--topico kc_02] [--pasta ensaios]"
  exit 2
}

[ $# -ge 1 ] || uso
codigo="$1"; shift
topico="kc_02"
pasta="ensaios"
while [ $# -gt 0 ]; do
  case "$1" in
    --topico) [ -n "${2:-}" ] || uso; topico="$2"; shift 2 ;;
    --pasta)  [ -n "${2:-}" ] || uso; pasta="$2";  shift 2 ;;
    *) uso ;;
  esac
done

falhou=0
aviso() { vermelho "  nao  $1"; falhou=1; }
ok()    { verde    "  ok   $1"; }

echo "ensaio $codigo, topico $topico"
echo

# 1. O formato do codigo, igual ao do servidor.
if printf '%s' "$codigo" | grep -qE '^[A-Za-z][A-Za-z0-9_-]{0,15}$'; then
  ok "o codigo serve"
else
  aviso "codigo fora do formato: letra, depois letras, numeros, - ou _, ate 16"
fi

# 2. A pasta do ensaio, fora de mvp/dados.
mkdir -p "$AQUI/$pasta"
LOG="$AQUI/$pasta/$topico.jsonl"
ok "log do ensaio: $pasta/$topico.jsonl"

# 3. O codigo ainda nao foi usado NESTE log.
if [ -f "$LOG" ]; then
  usado=$(python -c '
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
' "$LOG" "$codigo")
  if [ "$usado" -eq 0 ]; then
    ok "o codigo $codigo ainda nao aparece no log"
  else
    aviso "o codigo $codigo ja tem $usado linhas neste log"
  fi
else
  ok "log novo; o codigo $codigo esta livre"
fi

# 4. O dominio carrega.
if (cd "$AQUI" && python -c "
import sys
from mvp.dominio import carrega, DominioInvalido
try:
    d = carrega(topico=sys.argv[1])
except DominioInvalido as erro:
    for p in erro.problemas:
        print('   ', p)
    raise SystemExit(1)
print('    %s: %d nos, %d crencas, %d atividades'
      % (d.id, len(d.nos), len(d.crencas), len(d.atividades)))
" "$topico"); then
  ok "o topico carrega"
else
  aviso "o topico NAO carrega (acima o que esta errado)"
fi

# 5. As portas.
for porta in 8010 8011; do
  if netstat -ano 2>/dev/null | grep -q "[:.]$porta .*LISTEN"; then
    aviso "a porta $porta ja esta ocupada — servidor velho no ar?"
  else
    ok "porta $porta livre"
  fi
done

echo
if [ "$falhou" -ne 0 ]; then
  vermelho "resolva o que esta acima antes de chamar a pessoa."
  exit 1
fi

verde "pronto. Suba os dois, cada um no seu terminal:"
cat <<FIM

  STRUCTURA_TOPICO=$topico STRUCTURA_LOG=$pasta/$topico.jsonl python -m mvp.app
  STRUCTURA_TOPICO=$topico STRUCTURA_LOG=$pasta/$topico.jsonl python -m mvp.painel

  quem responde:  http://127.0.0.1:8010/?codigo=$codigo
  voce observa:   http://127.0.0.1:8011

  Abra a pagina de quem responde ANTES de chamar a pessoa: o codigo vai na
  URL, nao numa tela a mais. Se a pagina abrir sem ?codigo=, a sessao sai
  anonima e nao da para ligar ao participante depois.

DEPOIS DA SESSAO, na ordem:
  1. scripts/copia.sh <pasta-na-outra-midia> --log $pasta/$topico.jsonl
  2. anote o que a folha de observacao pede, enquanto esta fresco
  3. so entao feche os servidores
FIM
