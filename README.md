# Structura

Instrumento de diagnóstico e refutação de concepções errôneas sobre
**ponteiros em C**. Rafael H. S. Simão, UFV–CRP.

O sistema apresenta uma atividade, pergunta **a resposta, a razão da
resposta e a confiança declarada**, infere daí qual crença errônea está
em jogo, e a refuta conduzindo a pessoa pelo grafo de premissas do
tópico — não dizendo que ela errou.

## Rodar

Python 3.11 ou mais novo (desenvolvido em 3.14.7).

```bash
python -m pip install -r requirements.txt
```

```bash
python -m mvp.app
```

Abra **http://127.0.0.1:8010**. O tópico padrão é o `kc_00`; para
abrir o tópico com material de ensino completo:

```bash
STRUCTURA_TOPICO=kc_02 python -m mvp.app
```

No PowerShell, variável de ambiente se escreve antes, em outra linha:

```bash
$env:STRUCTURA_TOPICO = "kc_02"; python -m mvp.app
```

O painel de acompanhamento, que lê o log da coleta, sobe separado:

```bash
python -m mvp.painel
```

## DUAS GERAÇÕES NESTE REPOSITÓRIO — leia antes de avaliar

O repositório guarda duas gerações do sistema, e **só uma é o
instrumento**:

| pasta | o que é |
| --- | --- |
| **`mvp/`** | **o instrumento.** Motor, domínio, rotas, telas, painel e exportador. 1.663 testes. |
| **`scripts/`** | ferramentas de curadoria: oráculo, gerador de item, gerador de tabela de mesa, validador de material, caminhante |
| **`docs/`** | o registro do processo e as decisões, com as medições que as produziram |
| **`candidatos/`** | material e itens propostos, antes de entrarem no domínio |
| `api/` `engine/` `store/` `tools/` `tests/` | **geração anterior**, de setembro. 252 testes próprios, que ainda passam. O `mvp/` **não importa nada dela** — conferido. |
| `domain/` `prototipo/` `analise/` `web/` | restos da geração anterior, sem código Python |

A versão anterior deste README mandava rodar `python -m api.main` na
porta 8000, que é a geração anterior. Quem avaliar seguindo aquilo
avalia o protótipo de setembro.

## Para ver o mecanismo em cinco minutos

Com `STRUCTURA_TOPICO=kc_02`:

1. **Teach-back inicial.** Escreva o que você acha que é um ponteiro. O
   sistema não corrige — ele guarda, e pergunta de novo no fim.
2. **Três cartões de ensino**, um por premissa observável. Cada um traz
   a frase, o exemplo em C, uma figura da memória, a ampliação
   explicativa, o **teste de mesa** — a tabela com o valor de cada
   variável depois de cada linha, *gerada compilando e executando o
   exemplo* — e uma analogia de resgate. O botão "Ainda não entendi"
   traz material diferente, não a mesma frase de novo.
3. **Diagnóstico.** Responda uma atividade **escolhendo a alternativa
   errada que corresponde a uma crença** — por exemplo, no nó B3, que o
   ponteiro guarda o valor e não o endereço. Na tela seguinte, escolha
   como razão a frase daquela mesma crença, e declare confiança alta.
4. **A refutação dispara.** O sistema não diz "errado": ele percorre as
   premissas que sustentam aquele nó, uma tela por premissa, e só então
   volta a perguntar.
5. **Treino e reteste.** O nó só fecha com dois acertos em **formatos
   diferentes** de pergunta. E, no fim da unidade, a crença refutada
   volta num item que a pessoa não viu — é a medida de transferência.
6. **Teach-back final**, e o mapa do que ficou confirmado, frágil ou em
   aberto.

Tudo isso vira linha de log. A sessão inteira é **reconstruível só pelo
arquivo de log**, sem estado guardado em outro lugar.

## O escopo, delimitado

| | |
| --- | --- |
| domínio | ponteiros em C, 13 tópicos, 79 premissas, 560 itens |
| catálogo | 61 crenças errôneas distintas, cada uma com procedência declarada e fonte conferida na **obra primária** |
| fontes | Sorva (2012), Apêndice A, Tabela A.1 — citado com página e item; FAQ do comp.lang.c, conferido entrada por entrada; Kaczmarczyk et al. (2010) |
| material de ensino em profundidade | **um tópico** (`kc_02`), e o primeiro nó de um segundo (`kc_07:B1`) |
| avaliação com participantes | **não foi feita.** Nenhuma afirmação deste repositório é sobre aprendizagem medida. |

## A limitação principal, medida

**A fragilidade do sistema hoje é a qualidade e a profundidade do
material de ensino**, e ela não é uma impressão — é número:

```text
palavras de ensino por tópico
   kc_02    2828      <- material profundo: ampliação, narração,
   kc_07     578         caso resolvido, outra rota e teste de mesa
   kc_09     257
   kc_12     239
   ...
   kc_01     130      <- só a frase da premissa e um exemplo
```

As consequências, também medidas:

- **oportunidade de aprendizagem registrada por sessão:** 7 no `kc_02`,
  1 no `kc_07`, **zero nos outros onze**. O log só registra que um
  conceito foi apresentado onde o material o ensina com explicação e
  exemplo.
- **inventário de conceitos:** 6 de 14 estão `disponivel`. Quatro são
  `so_avaliado` — cobrados em item, nunca ensinados.
- **67 itens cobram construto que o percurso não ensinou**, 64 deles
  `funcao_com_parametro`, em 11 tópicos.
- **7 cadeias de refutação interrogativa escritas, nenhuma acionável:**
  cada uma exige que todo conceito dos seus degraus esteja ensinado, e
  nenhuma passa.

### E por que isto está escrito aqui, e não escondido

Porque o instrumento inclui os mecanismos que **impedem essa limitação
de passar calada**, e eles são parte da contribuição:

- `mvp/test_coerencia.py` — uma catraca que pina, por tópico, quantos
  itens cobram construto não ensinado, e **falha quando o número
  cresce**. Dívida antiga não trava o trabalho; dívida nova não entra.
- `mvp/dominio/conceitos.yaml` — um conceito só entra como `disponivel`
  com a **evidência de onde foi ensinado**, e a regra é estreita:
  explicação com exemplo. Menção não conta.
- `docs/revisao-de-material.md` — seis portões de julgamento para
  material novo, cada um com o defeito real que o motivou.
- `mvp/test_yaml_duplicado.py` — recusa chave repetida em todo YAML de
  domínio, porque `yaml.safe_load` fica com a última em silêncio.

O que o sistema não sabe, ele diz que não sabe: premissa não medida sai
nomeada no fim da sessão, distrator sem crença não recebe atribuição, e
conceito sem evidência não é declarado ensinado.

## Testes

```bash
python -m pytest mvp -q
```

1.663 testes do instrumento. A suíte inteira do repositório
(`python -m pytest -q`) soma 1.915, porque inclui os 252 da geração
anterior.

## Privacidade

Participantes são identificados por **pseudônimo** (`P01`…`P40`). Não há
nome, matrícula ou identificador direto em banco nem em exportação. O
token de exportação fica em `data/export_token.txt`, fora do controle de
versão.

## Licença

O código e o conteúdo de ensino do Structura estão sob a licença MIT
(arquivo [LICENSE](LICENSE)). Ficam fora dela, por terem dono ou licença
própria:

- as fontes tipográficas em `mvp/web/fontes/`, sob a SIL Open Font
  License (as licenças estão na mesma pasta);
- os arquivos de estilo do LaTeX em `docs/monografia/latex/`
  (`abntex2-UFV.sty` e `abntex2-alf-tcc.bst`), sob a LaTeX Project Public
  License;
- o texto da monografia, em `docs/monografia/`, que é o Trabalho de
  Conclusão de Curso do autor e não é licenciado para reuso;
- os trechos de obras de terceiros citados no catálogo e nos documentos,
  que pertencem aos respectivos autores.
