#!/usr/bin/env bash
# Verificacao padrao do projeto. Um comando, pouca saida.
#
#   scripts/verify.sh              varre segredos, roda os testes
#   scripts/verify.sh --rapido     so o MVP (0,3 s em vez de 67 s)
#   scripts/verify.sh --autoteste  prova que a varredura de segredos morde
#
# Ordem deliberada, do mais barato ao mais caro, parando na primeira falha:
# um segredo no commit e irreversivel (ele fica no historico), entao a
# varredura vem antes de qualquer teste. Testes que falham a gente conserta;
# chave vazada a gente revoga.
#
# A saida e curta de proposito: status final e, no maximo, LIMITE_LINHAS do
# primeiro erro. Saida longa nao e lida.

set -u

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIMITE_LINHAS=30
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

vermelho() { printf '\033[31m%s\033[0m\n' "$1"; }
verde()    { printf '\033[32m%s\033[0m\n' "$1"; }

# ---------------------------------------------------------------------------
# Varredura de segredos
# ---------------------------------------------------------------------------
# Sem gitleaks instalado, isto e o substituto honesto: pega as formas que
# vazam na pratica (chave privada, credencial da AWS, token de provedor,
# atribuicao de segredo com valor longo). NAO substitui uma ferramenta de
# verdade, e o relatorio da revisao final diz isso.
#
# Os padroes sao montados por concatenacao para o proprio arquivo nao casar
# com eles quando ele mesmo for varrido.

padroes() {
  printf '%s\n' \
    "-----BEGIN [A-Z ]*PRIVATE KEY-----" \
    "AKIA[0-9A-Z]{16}" \
    "gh[pousr]_[A-Za-z0-9]{20,}" \
    "sk""-[A-Za-z0-9]{24,}" \
    "(api[_-]?key|apikey|secret|token|password|senha)[\"' ]*[:=][\"' ]*[A-Za-z0-9_/+-]{16,}"
}

# Arquivos que nunca devem ser versionados, por conterem dado de coleta ou
# credencial. Entram aqui por nome, nao por conteudo.
# `.*\.jsonl` e proposital, e nao so `eventos.jsonl`: a copia datada se chama
# `eventos-20261029-133345.jsonl`, passou por fora da regra estreita, e tres
# copias do log de desenvolvimento ficaram versionadas por dois commits. O
# unico JSONL deste projeto e log; nenhum tem por que entrar no repositorio.
PROIBIDOS='(^|/)(export_token\.txt|.*\.db|.*\.db-wal|.*\.db-shm|.*\.jsonl|\.env)$'

# Caminho que um clone nao consegue criar. No Windows `:` e `\` dentro de um
# nome de arquivo viram caracteres de uso privado, e `git clone` falha no
# checkout: o repositorio deixa de ser reproduzivel do zero. A varredura de
# conteudo nao pegava isso porque o teste `-f` nem abria um arquivo cujo nome
# nao resolve. Lista branca, que e o unico jeito de pegar o que nao se previu.
SEGURO='^[A-Za-z0-9._/-]+$'

caminhos() {
  # caminhos <caminho>... -> 0 limpo, 1 sujo. Escreve os achados em $TMP/caminhos
  local sujo=0 arq
  : > "$TMP/caminhos"
  for arq in "$@"; do
    if ! printf '%s' "$arq" | grep -qE "$SEGURO"; then
      echo "$arq: caminho que um clone nao cria" >> "$TMP/caminhos"
      sujo=1
    fi
  done
  return $sujo
}

varre() {
  # varre <arquivo>... -> 0 limpo, 1 sujo. Escreve os achados em $TMP/segredos
  local sujo=0 arq numero
  : > "$TMP/segredos"
  for arq in "$@"; do
    [ -f "$arq" ] || continue
    if printf '%s' "$arq" | grep -qE "$PROIBIDOS"; then
      echo "$arq: arquivo que nao deve ser versionado" >> "$TMP/segredos"
      sujo=1
      continue
    fi
    # -I ignora binario; -n da a linha; o valor em si nunca e impresso.
    while IFS= read -r numero; do
      echo "$arq:$numero: possivel segredo" >> "$TMP/segredos"
      sujo=1
    done < <(grep -InE -f <(padroes) "$arq" 2>/dev/null | cut -d: -f1 || true)
  done
  return $sujo
}

autoteste() {
  local sujo="$TMP/sujo.txt" limpo="$TMP/limpo.txt" falhas=0
  # Montado em pedacos: escrito inteiro, o arquivo deste script casaria com
  # o proprio padrao na varredura do commit que o introduz.
  printf 'api_key%s"%s"\n' " = " "AbCdEf0123456789XyZw" > "$sujo"
  printf 'import secrets\nsenha = pedir()\n' > "$limpo"

  if varre "$sujo"; then
    vermelho "autoteste: a varredura NAO pegou um segredo plantado"
    falhas=1
  fi
  if ! varre "$limpo"; then
    vermelho "autoteste: a varredura acusou um arquivo limpo"
    cat "$TMP/segredos"
    falhas=1
  fi

  # O nome que escapou: a copia datada do log, que a regra estreita nao pegava.
  : > "$TMP/eventos-20261029-133345.jsonl"
  if varre "$TMP/eventos-20261029-133345.jsonl"; then
    vermelho "autoteste: a varredura NAO pegou uma copia datada do log"
    falhas=1
  fi

  # E o caminho que um clone nao cria.
  if caminhos 'pasta/C:\Users\x/eventos.jsonl'; then
    vermelho "autoteste: a checagem NAO pegou um caminho inclonavel"
    falhas=1
  fi
  if ! caminhos 'mvp/app.py' 'docs/PRD.md'; then
    vermelho "autoteste: a checagem acusou um caminho normal"
    cat "$TMP/caminhos"
    falhas=1
  fi

  [ "$falhas" -eq 0 ] && verde "autoteste: as duas checagens mordem, e nao mordem errado"
  return "$falhas"
}

# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------
roda_testes() {
  local alvo="$1" rotulo="$2"
  if (cd "$RAIZ" && python -m pytest $alvo -q > "$TMP/pytest.txt" 2>&1); then
    verde "ok   $rotulo: $(grep -oE '[0-9]+ passed' "$TMP/pytest.txt" | tail -1)"
    return 0
  fi
  vermelho "FALHOU   $rotulo"
  grep -E "^(FAILED|ERROR|E  )" "$TMP/pytest.txt" | head -n "$LIMITE_LINHAS"
  tail -n 3 "$TMP/pytest.txt"
  return 1
}

# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------
case "${1:-}" in
  --autoteste) autoteste; exit $?;;
esac

# Em staging, se houver; senao, os arquivos versionados. Rodar fora de um
# commit tambem tem de servir para alguma coisa.
mapfile -t ALVOS < <(cd "$RAIZ" && git diff --cached --name-only --diff-filter=ACM)
if [ "${#ALVOS[@]}" -eq 0 ]; then
  mapfile -t ALVOS < <(cd "$RAIZ" && git ls-files)
  ESCOPO="arquivos versionados"
else
  ESCOPO="arquivos em staging"
fi

cd "$RAIZ"
if ! caminhos "${ALVOS[@]}"; then
  vermelho "FALHOU   caminhos (${#ALVOS[@]} $ESCOPO)"
  head -n "$LIMITE_LINHAS" "$TMP/caminhos"
  echo
  vermelho "Nada foi testado: um clone destes nao chega de pe."
  exit 1
fi

if ! varre "${ALVOS[@]}"; then
  vermelho "FALHOU   segredos (${#ALVOS[@]} $ESCOPO)"
  head -n "$LIMITE_LINHAS" "$TMP/segredos"
  echo
  vermelho "Nada foi testado: resolva isto primeiro."
  exit 1
fi
verde "ok   segredos: nada em ${#ALVOS[@]} $ESCOPO"

roda_testes "mvp/" "testes do MVP" || exit 1
case "${1:-}" in
  --rapido) echo "(suite antiga pulada: --rapido)"; exit 0;;
esac
roda_testes "--ignore=mvp" "suite antiga" || exit 1

verde "tudo verde"
