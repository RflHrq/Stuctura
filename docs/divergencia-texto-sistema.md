# A divergência entre o texto e o sistema

Medição de **04/11/2026**. Nenhuma linha de código foi tocada para produzir
este documento: ele compara o que os documentos afirmam sobre o sistema com
o que o sistema faz hoje, e lista só o que divergiu.

O achado de uma frase: **nenhum dos documentos voltados ao TCC descreve o
instrumento que existe.** Três das divergências atingem o método, não a
redação.

## A data é o começo da explicação

| documento | linhas | última mudança |
| --- | --- | --- |
| `README.md` | 456 | **17/09** |
| `docs/fundamentacao.md` | 140 | **18/09** |
| `docs/requisitos.md` | 161 | **18/09** |
| `docs/arquitetura.md` | 192 | **18/09** |
| `docs/plano-tcc.md` | 220 | **18/09** |
| `docs/curadoria-grafos.md` | 548 | **18/09** |

Todo o sistema atual (`mvp/`) é de **28/10 em diante**. Esses seis
documentos são de sete semanas antes, e portanto anteriores ao instrumento
inteiro. A reformulação está registrada em `processo.md` — *"o motor atual
(`mvp/`) e o antigo (`engine/`) ficam onde estão, versionados"* —, mas a
consequência documental dela nunca foi paga.

---

## P1-A · A pipeline de análise aponta para o sistema antigo

`plano-tcc.md` nomeia sete tipos de evento como fonte de dado de V1 a V4.
Onde cada um existe hoje:

| evento | arquivos em `mvp/` | arquivos em `engine/` |
| --- | --- | --- |
| `misconception_detected` | **0** | 6 |
| `ciu_presented` | **0** | 4 |
| `answer_submitted` | **0** | 8 |
| `probe_shown` | **0** | 4 |
| `socratic_step_answered` | **0** | 6 |
| `kc_completed` | **0** | 7 |
| `belief_retested` | 5 | 4 |

**Seis de sete só existem no motor antigo.** O V2 — a coerência da hipótese,
que o plano chama de instrumento principal e de *"o que transforma este
estudo de 'testei com uns colegas' em método defensável"* — mede
`misconception_detected`. O instrumento atual não emite esse evento: emite
`crenca_detectada`.

E a parte que pode inutilizar dado já coletado: o plano afirma que *"a
exportação gera três tabelas (respostas, sessões, calibração)"*. O
`tools/export.py` lê **SQLite** (`data/structura.db`). O MVP grava
**JSONL** (`mvp/dados/eventos.jsonl`). Não existe exportação em `mvp/` —
nenhum arquivo lá menciona export ou csv.

**Uma coleta bem-feita hoje produziria um log de onde ninguém tira tabela.**
É o único item deste documento com essa propriedade: os outros se consertam
depois, sem perda. Este não.

## P1-B · As perguntas de pesquisa e os critérios de sucesso não se cruzam

As quatro subperguntas (V1 viabilidade, V2 coerência, V3 mudança imediata,
V4 aceitação) aparecem **só** em `plano-tcc.md`. Os doze critérios de
sucesso (CS-1 a CS-12) aparecem só em documentos do sistema: `PRD.md`,
`posicao.md`, `processo.md`, `revisao-final.md`, `tasks.md`,
`tasks-ciclo-3.md`.

Busca por qualquer linha que cite os dois juntos: **nenhuma**.

Há semanas o desenvolvimento se confere contra os CS — a revisão final deu
veredito contra eles, os ciclos de tarefa saíram deles. As perguntas que
justificam o trabalho estão órfãs do processo que constrói o instrumento, e
ninguém pode dizer, lendo os documentos, qual CS serve a qual V.

## P1-C · O README inicia o sistema errado

As instruções de execução mandam:

```
python -m api.main            # o servidor
python -m pytest tests/ -q    # 252 testes
python -m tools.export --out analise/
```

Nada em 456 linhas aponta para `mvp/`. **Quem clonar o repositório e seguir
o README sobe o sistema antigo e nunca vê o instrumento** — que tem 830
testes e é o objeto do trabalho.

Isto interage com o P1-4 da revisão final (os dois commits que não
restauram no Windows): hoje o repositório não pode ser clonado numa máquina
Windows, e quando puder, a porta da frente aponta para o lugar errado.

---

## As divergências de texto

| documento | o que afirma | o que é |
| --- | --- | --- |
| `arquitetura.md` | cinco camadas `engine/store/api/web/tools`; SQLite com 4 tabelas; 17 tipos de evento; **dois braços**; 252 testes; domínio em seis YAMLs | correto sobre `engine/`, falso como descrição do instrumento. O MVP é `motor/log/app/dominio/molde/painel`, JSONL, sem braços, 52 YAMLs |
| `requisitos.md` | RF01 a RF17 mapeados para `engine/*.py`, todos marcados "feito" | são os requisitos do sistema antigo |
| `plano-tcc.md` | **duas unidades** por sessão | decisão 18: **um KC por sessão** |
| `plano-tcc.md` | 8 a 10 telas e 5 a 7 minutos por unidade | medido: 14 telas por premissa; 38 a 120 passos por tópico |
| `plano-tcc.md` | "três perguntas rápidas sobre experiência com C" | **não existe**: zero menções a experiência em `mvp/` |
| `plano-tcc.md`, `README.md`, `linguagem.md`, `research.md`, `processo.md` | "93 nós" | o MVP tem **79 nós** em 13 tópicos. 93 é o grafo antigo, em `domain/c_pointers/` |

Duas coisas do `plano-tcc.md` que **não** divergiram, e vale registrar para
ninguém "consertar" o que está certo: a queda do experimento de dois braços
(e com ela a liberação do retorno imediato) está consistente com o
instrumento, e o reteste no fim da sessão também.

## O que não foi examinado

`fundamentacao.md` e `curadoria-grafos.md` passaram limpos — mas pela
checagem **mais fraca** deste documento. Procurei padrões: `engine/`,
SQLite, dois braços, contagens de nós e de tópicos. Teoria e curadoria de
conteúdo podem ter divergido de um jeito que busca por padrão não alcança.
Dar por limpo exigiria leitura linha a linha, que não foi feita.

Nada aqui mede a **qualidade** de documento nenhum. Mede só concordância
com o sistema.

## A ordem sugerida

1. **A exportação do log do MVP.** É a única divergência que pode
   inutilizar dado já coletado.
2. **O mapa V1–V4 × CS-1…CS-12.** É texto, e é o que amarra o instrumento
   à pergunta de pesquisa. Sem ele o TCC tem um sistema verificado e uma
   pergunta não conectada a ele.
3. **O README apontando para o sistema certo**, junto com o P1-4 — a porta
   da frente e a clonabilidade são o mesmo problema visto de dois lados.
4. **`arquitetura.md` e `requisitos.md`**, que descrevem `engine/` como se
   fosse o instrumento. Podem virar documentos do sistema antigo, com um
   par novo para o MVP, ou ser reescritos. É decisão do dono.
5. Os dois P1 de software da revisão final: a exclusão que não alcança as
   cópias, e o histórico que não restaura no Windows.
