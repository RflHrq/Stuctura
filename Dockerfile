# Structura — o portal dos tópicos, pronto para deixar ligado.
#
#   docker compose up -d --build     ->  http://127.0.0.1:8010
#
# A imagem leva SÓ o que o portal precisa para rodar: o pacote `mvp`
# (motor, domínio, interface) e três dependências. Não leva teste, não
# leva o compilador C — as demonstrações chegam à tela com a saída que a
# verificação já conferiu, e nada é compilado durante uma sessão — e não
# leva dado nenhum: os registros ficam numa pasta da máquina, montada em
# /dados pelo docker-compose.yml.
# 3.14.7, e nao so 3.14: e a versao em que a suite roda. A primeira
# construcao, com a tag 3.14, trouxe a 3.14.10.
FROM python:3.14.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STRUCTURA_HOST=0.0.0.0 \
    STRUCTURA_PORTA=8010 \
    STRUCTURA_PASTA=/dados

WORKDIR /app

# As MESMAS versões em que a suíte roda. `mvp/test_docker.py` compara
# este arquivo com o requirements.txt da raiz.
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY mvp/ /app/mvp/

# Sem root: o processo só precisa ler o código e escrever em /dados.
RUN useradd --create-home --uid 10001 structura \
    && mkdir -p /dados \
    && chown structura:structura /dados
USER structura

EXPOSE 8010

# "Saudável" é responder a lista de tópicos — o que prova que os treze
# domínios carregaram, e não só que o processo existe.
HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8010/topicos', timeout=4)" || exit 1

CMD ["python", "-m", "mvp.portal"]
