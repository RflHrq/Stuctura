# Rodar o Structura com Docker

O sistema inteiro — os treze tópicos, num processo só — sobe num contêiner
e fica ligado.

## No dia a dia

| para | faça |
| --- | --- |
| ligar | dois cliques em `iniciar-structura.bat` |
| usar | `http://127.0.0.1:8010` (o atalho já abre) |
| desligar | dois cliques em `parar-structura.bat` |

O Docker Desktop precisa estar aberto. Depois de ligado, o sistema **continua
ligado**: fechar a janela não o desliga, e ele volta sozinho quando o Docker
inicia. Só para quando alguém clica no `parar-structura.bat`.

Sem os atalhos, os comandos são os mesmos que eles rodam:

```bash
docker compose up -d --build
```

```bash
docker compose down
```

## Onde ficam os dados

Em `coleta/portal/`, na pasta do projeto, um arquivo por tópico
(`kc_02.jsonl`, `kc_07.jsonl`…). A pasta fica **na máquina**, fora do
contêiner: desligar, atualizar ou apagar o contêiner não mexe nela.

- Está no `.gitignore`: registro de sessão nunca vai para um commit.
- **Não** é a `ensaios/portal/`. Lá ficam as sessões simuladas das
  verificações; o que roda pelo Docker nasce separado delas.
- Para as tabelas de análise de um tópico:

```bash
python -m mvp.exporta --log coleta/portal/kc_02.jsonl --out analise/kc_02
```

## Depois de mudar o código ou o conteúdo

Clique no `iniciar-structura.bat` de novo. Ele reconstrói a imagem com o que
estiver na pasta e troca o contêiner; os dados não são tocados.

## Ver o que o sistema está dizendo

```bash
docker compose logs -f portal
```

```bash
docker compose ps
```

## O que o empacotamento decide, e por quê

**Só nesta máquina.** A porta é publicada em `127.0.0.1`, e não na rede. O
sistema não tem login, e o registro guarda o que os participantes escrevem.
Para atender outro computador da rede é preciso trocar a linha de `ports` no
`docker-compose.yml` — é decisão a tomar de propósito, e há um teste
(`mvp/test_docker.py`) que cai quando ela muda, para ninguém mudar sem ver.

**As versões da suíte.** A imagem usa Python 3.14.7 e as mesmas versões de
biblioteca em que os testes rodam. A primeira construção, sem isso fixado,
trouxe um Python e um `pydantic` mais novos; num piloto, descobrir diferença
de versão no meio de uma sessão é o pior momento possível.

**Sem compilador e sem testes na imagem.** As demonstrações em C chegam à
tela com a saída que a verificação já conferiu; nada é compilado durante uma
sessão.

**Sem root.** O processo roda como um usuário comum, que só escreve em
`/dados`.

## Antes de rodar os testes ou o `ensaio.sh`: desligue

O sistema ligado ocupa a porta 8010, e duas coisas do projeto pedem essa
porta livre:

- `scripts/ensaio.sh`, que prepara uma sessão de um tópico só e recusa
  seguir se já houver um servidor atendendo — ele existe para pegar
  servidor esquecido no ar;
- a suíte de testes, que roda o `ensaio.sh` em dois testes.

Com o contêiner ligado, esses dois testes falham dizendo "a porta 8010
ATENDE — servidor velho no ar". Não é defeito: é o sistema ligado. Clique
no `parar-structura.bat`, rode o que precisa, e ligue de novo.

## O que não está no contêiner

- **O painel do pesquisador.** Continua rodando direto, apontado para o
  arquivo do tópico que se quer acompanhar:

```bash
STRUCTURA_TOPICO=kc_02 STRUCTURA_LOG=coleta/portal/kc_02.jsonl python -m mvp.painel
```

- **A suíte de testes e o oráculo.** São de desenvolvimento, e rodam na
  máquina, com `python -m pytest`.

## Como isto foi verificado

Em 12/11/2026, com Docker 29.9 no Windows: a imagem foi construída, o
contêiner subiu saudável, a lista dos treze tópicos respondeu, oito sessões
inteiras foram atravessadas pelo contêiner nos quatro tópicos do piloto
(nenhuma premissa sem medida), os registros apareceram na pasta da máquina,
e os dois atalhos foram executados — desligar, conferir que parou, ligar,
conferir que voltou. As sessões dessa verificação foram movidas para
`ensaios/docker-verificacao/`, e `coleta/portal/` ficou vazia.

O que **não** foi verificado: o reinício automático depois de reiniciar o
computador, e o uso em Linux, onde a pasta `coleta/portal/` pode precisar
de permissão de escrita para o usuário do contêiner.
