#!/usr/bin/env bash
# Prepara uma demonstracao do sistema, em quatro passos.
#
#   scripts/demo.sh            confere tudo e imprime os passos
#   scripts/demo.sh semear     cria tres sessoes de exemplo (servidor no ar)
#
# Log PROPRIO: ensaios/demo.jsonl. Sessao simulada nao encosta no log de
# desenvolvimento nem no do ensaio nem no do piloto — os codigos comecam
# com DEMO justamente para ninguem confundir depois.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TOPICO="${STRUCTURA_TOPICO:-kc_02}"
LOG="ensaios/demo.jsonl"

verde()    { printf '\033[32m%s\033[0m\n' "$1"; }
vermelho() { printf '\033[31m%s\033[0m\n' "$1"; }

# ---------------------------------------------------------------- semear
if [ "${1:-}" = "semear" ]; then
  cd "$AQUI"
  if ! curl -s -m 5 http://127.0.0.1:8010/saude > /dev/null 2>&1; then
    vermelho "o servidor nao esta no ar. Faca o passo 1 primeiro."
    exit 1
  fi
  echo "tres sessoes de exemplo, uma por persona:"
  echo
  python scripts/caminhante.py --persona sabido  --codigo DEMO-SABE
  python scripts/caminhante.py --persona aprende --codigo DEMO-APRENDE
  python scripts/caminhante.py --persona crente  --codigo DEMO-CRENTE
  echo
  verde "pronto. Recarregue o painel: as tres aparecem na lista."
  echo "  DEMO-SABE     acerta tudo        — o caminho curto"
  echo "  DEMO-APRENDE  erra e aprende     — o laco inteiro, e e esta que voce mostra"
  echo "  DEMO-CRENTE   erra e nao muda    — o pior caso, com premissa nao medida"
  exit 0
fi

# -------------------------------------------------------------- preparar
falhou=0
aviso() { vermelho "  nao  $1"; falhou=1; }
ok()    { verde    "  ok   $1"; }

echo "demonstracao — topico $TOPICO"
echo

mkdir -p "$AQUI/ensaios"
if [ -f "$AQUI/$LOG" ]; then
  linhas=$(grep -c "" "$AQUI/$LOG" || true)
  ok "log da demo ja existe, com $linhas linhas (apague se quiser comecar limpo)"
else
  ok "log da demo: $LOG (vazio)"
fi

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
" "$TOPICO"); then
  ok "o topico carrega"
else
  aviso "o topico NAO carrega"
fi

for porta in 8010 8011; do
  if netstat -ano 2>/dev/null | grep -q "[:.]$porta .*LISTEN"; then
    aviso "a porta $porta ja esta ocupada — servidor velho no ar?"
  else
    ok "porta $porta livre"
  fi
done

echo
if [ "$falhou" -ne 0 ]; then
  vermelho "resolva o que esta acima antes de apresentar."
  exit 1
fi

cat <<FIM
QUATRO PASSOS, nesta ordem:

  1. terminal A — quem responde
     STRUCTURA_TOPICO=$TOPICO STRUCTURA_LOG=$LOG python -m mvp.app

  2. aqui mesmo  — tres sessoes de exemplo, para o painel ter o que mostrar
     bash scripts/demo.sh semear

  3. terminal B  — o painel do pesquisador
     STRUCTURA_TOPICO=$TOPICO STRUCTURA_LOG=$LOG python -m mvp.painel

  4. abra as duas abas
     http://127.0.0.1:8010/?codigo=DEMO-AOVIVO   quem responde
     http://127.0.0.1:8011                        voce observa

O roteiro do que mostrar, e em que ordem, esta em docs/apresentacao.md.
FIM
