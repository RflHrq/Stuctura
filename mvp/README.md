# MVP — treino até domínio

Implementa o laço do documento de 01/10/2026: **identifica → refuta →
treina → confirma**. Um nó só vira premissa correta depois de uma sequência
de acertos no treino, nunca depois de um acerto isolado.

Conteúdo: **kc_00, declaração de variáveis** — 5 premissas, 4 concepções
errôneas, 20 atividades e a analogia do quarto de hotel.

As atividades vêm em **dois bancos**, e a diferença importa:

| Banco | Quantas | Quando aparece |
| --- | --- | --- |
| diagnóstico | 10 — uma teórica e uma de código por nó | antes de qualquer refutação; o par sustenta a checagem de vacilo |
| treino | 10 — duas por nó, formatos diferentes | só depois da refutação, para fechar a sequência |

```bash
python -m pytest mvp/ -q     # 89 testes
python -m mvp.app            # http://127.0.0.1:8010
```

## O laço

| Passo | O que acontece | Onde |
| --- | --- | --- |
| **Pergunta** | camada 1 responde, tranca, e a camada 2 pergunta por quê | `motor._responde_diagnostico`, `motor.razoes_de` |
| **Classifica** | resposta × razão × confiança nos cinco estados, e a crença vai para o nó que ela nega | `motor.classifica`, `motor._resolve_diagnostico` |
| **Valida** | a analogia de resgate daquele nó, antes de qualquer refutação | `motor._inicia_validacao` |
| **Refuta** | percurso pelas premissas que sustentam o nó negado, montado do grafo | `motor._plano` |
| **Treina** | itens no mesmo nó, formato diferente a cada tentativa, até a sequência fechar | `motor._proximo_treino` |
| **Confirma** | o nó vira verde no mapa, e só então | `training_streak_completed` |

Errar chutando é lacuna, não crença: o sistema não refuta o que a pessoa não
pensa.

## "Não sei", opção de verdade

Nas **três** camadas. Obrigar a escolher **fabrica chute**: o sistema
criaria o falso positivo que depois tenta detectar. Com a opção
disponível, a lacuna vira dado **observado** — `"declarada": "camada2"` no
log — em vez de inferido de confiança baixa.

Dizer "não sei" numa camada **encerra o episódio**: quem não respondeu não
tem o que justificar, e quem não sabe explicar não tem convicção a
declarar. Perguntar assim mesmo seria teatro.

No treino, "não sei" zera a sequência como um erro zeraria — a sequência
mede premissa de pé, e quem não sabe não a tem de pé.

E o retorno é diferente de errar:

> **Você disse que não sabe.** Isso é informação, não erro: aqui não há
> nada para corrigir, há algo para construir.

## Os cinco estados, e em que nó cada um fica

`motor.classifica(certa, razao, confianca)` é função pura — a banca confere
linha a linha sem rodar nada:

| Resposta | Razão | Confiança | Estado | O que o motor faz |
| --- | --- | --- | --- | --- |
| certa | certa | tenho certeza | **confirmada** | conta uma superfície |
| certa | certa | acho que sei / chutei | **frágil** | não conta superfície |
| certa | **errada** | qualquer | **falso positivo** | não confirma; conta na crença |
| errada | **certa** | qualquer | **falso negativo** | não refuta; registra o vacilo |
| errada | errada | certeza / acho que sei | **crença ativa** | valida, refuta, treina |
| errada | errada | chutei | **lacuna** | registra |

**CS-5, duas superfícies.** Um acerto só deixa a premissa `fragil`: pode
ser reconhecimento do molde da pergunta, não da ideia. Confirmar exige dois
formatos diferentes, pela razão certa, com certeza — e é para isso que o
par teórica + código existe.

**CS-2, a crença vai para o nó que ELA nega.** Errar um item de B1
explicando pela crença de que sem valor não há memória é informação sobre
**B2**: é B2 que fica vermelho, é B2 que a refutação percorre, e B1 segue
em aberto. O evento guarda os dois: `{"no": "B2", "veio_do_item_de": "B1"}`.

**A regra dos dois erros foi aposentada.** Ela existia porque não havia
como saber *por que* a pessoa errou — o segundo erro era um proxy de "não
foi escorregão". A camada 2 substituiu o proxy pela coisa: quem erra pelo
motivo certo escorregou (CS-3), e quem erra pelo motivo errado já disse
qual é a crença.

## A analogia, desenhada

A mesma analogia do começo ao fim — **quarto de hotel reservado** — e um
desenho por premissa, em `web/figuras.js`. A regra do desenho não muda: o
quarto é a variável, o hóspede é o valor, a placa é o nome, a categoria é o
tipo.

| Premissa | O desenho mostra |
| --- | --- |
| B1 | dois quartos de categorias diferentes, cada um com sua placa |
| B2 | o quarto reservado e vazio: existe antes do hóspede |
| B3 | a bagunça do hóspede anterior — C não manda limpeza |
| B4 | o hóspede novo entrando e o antigo saindo: um por vez |
| I1 | a seta que vale (hóspede → quarto) e a que não vale |

A figura aparece em três momentos: no ensino, na validação (junto da analogia
escrita) e em cada passo da refutação. A tela de ensino mostra ainda o
**código de exemplo** daquele nó: a frase, o código e o desenho são a mesma
ideia em três registros, e a frase sozinha fica abstrata para quem nunca
declarou uma variável.

## Quando ele não entende a premissa

Todo passo da refutação tem **"Ainda não entendi"**. O percurso não anda: a
mesma premissa volta, agora dita pela analogia daquele nó. Até
`LIMITE_REEXPLICACAO` vezes (2) — depois disso o percurso segue e o log
registra `premissa_nao_fechou`.

Insistir numa quarta vez na mesma frase não ensina, e o treino ainda vem
depois para pegar o que ficou. Quem não fechar lá termina o nó em aberto, que
é honesto.

## O grafo durante a atividade

O painel do topo fica visível a unidade inteira, e vem do mesmo dado do mapa
final: toda resposta do servidor carrega o estado dos cinco nós. O aluno vê a
cadeia se erguendo enquanto responde.

| No painel | Significa |
| --- | --- |
| `B2 ✓` cheio | premissa confirmada, em duas formas de pergunta |
| `B2 ✓` tracejado | confirmada depois de refutação e treino |
| `B2 ✓?` | de pé numa forma só, ou sem convicção — falta superfície |
| `B2 !` | acertou por outro motivo: não confirma |
| `B2 ✗` | crença detectada, ainda não trabalhada |
| `B2 ?` | disse que não sabe |
| `B2 1/2` | em treino: acertos seguidos até confirmar |
| `B2 —` | ficou em aberto |

**Símbolo antes de cor.** Cada estado tem símbolo, traço (cheio, tracejado
ou pontilhado) e **nome por extenso** no mapa. Daltonismo e impressão em
preto e branco não podem apagar a diferença entre "de pé" e "crença ativa".

**O caso cruzado ganha frase.** Um nó pode ficar vermelho sem a pessoa ter
respondido nada sobre ele — porque ela explicou *outra* pergunta por uma
crença que nega este. Sem texto, isso parece bug. Com texto:

> A ideia que você usou na pergunta de B1 é uma afirmação sobre B2 — é lá
> que ela ficou registrada.

A aresta entre duas premissas acende quando as duas pontas estão de pé.

## Os quatro requisitos, e o teste de cada um

| Código | Regra | Teste |
| --- | --- | --- |
| RF33 | depois da refutação o nó entra em treino, nunca direto em confirmado | `test_rf33_nenhum_no_vai_de_refutado_a_confirmado_sem_treino` |
| RF34 | cada tentativa muda de formato, e nenhum item se repete | `test_rf34_o_seletor_recusa_o_formato_anterior` |
| RF35 | errar zera a sequência daquele nó, e só dele | `test_rf35_zerar_um_no_nao_mexe_nos_vizinhos` |
| RF36 | esgotar o banco sem fechar a sequência encerra o nó em aberto | `test_rf36_errar_sempre_no_treino_encerra_o_no_em_aberto` |

Os dois primeiros foram verificados por sabotagem: trocar `STREAK_ALVO` para
1 derruba o teste do RF33, e remover a regra de formato derruba o do RF34.

## Parâmetros

Em `motor.py`, no topo. São o ponto de partida do documento, **não valores
validados** — ajustar no ensaio antes de qualquer coleta.

```python
STREAK_ALVO = 2        # acertos seguidos, de formatos diferentes
TETO_TENTATIVAS = 4    # o dobro do streak
```

## O que NÃO está aqui, de propósito

- **Repetição espaçada entre sessões.** O desenho do estudo exclui retenção.
- **BKT ou qualquer modelo probabilístico.** O streak determinístico cobre a
  mesma necessidade sem parâmetro para calibrar.
- **Limiar por aluno ou por nó.** Fixo.
- **O reteste formal da pesquisa.** O streak é mecanismo de produto: ele
  emite `training_streak_completed` e nunca escreve em `belief_retested`.
  Misturar os dois faria o treino virar uma segunda forma de medir V3.

## Arquivos

```
mvp/
├── dominio/
│   ├── topic_kc00.yaml        o tópico
│   ├── graph_kc00.yaml        5 premissas, suporte e crenças que as negam
│   ├── beliefs_kc00.yaml      4 crenças com procedência e fonte
│   └── activities_kc00.yaml   20 atividades, exemplos e analogias de resgate
├── dominio.py                 carga e validação (falha na carga, nunca em sessão)
├── motor.py                   o laço, puro: (estado, resposta) → (estado, tela, eventos)
├── log.py                     append-only, uma linha JSON por evento
├── app.py                     três rotas
├── web/                       a interface, que não decide nada
├── web/figuras.js             a analogia desenhada, uma por premissa
├── test_motor.py              o laço, 28 testes
├── test_dominio.py            a carga e as invariantes, 14 testes
├── test_razao.py              as camadas 2 e 3, 18 testes
└── test_classificacao.py      os cinco estados, a projeção e CS-4, 31 testes
```

**Uma armadilha de YAML**, já resolvida: a chave `no:` é lida como booleano
falso (YAML 1.1). As atividades usam `node:` para apontar o nó.

## A crença é da alternativa, não do item

Cada alternativa errada aponta para **uma** crença, ou para nenhuma:

```yaml
alternativas:
  a: "Nada ainda, nenhuma tem valor"
  b: "Dois espacos reservados, cada um com seu proprio tamanho"
  c: "Um espaco so, compartilhado pelas duas"
gabarito: b
crencas:
  a: no_value_no_memory     # nega B2
  c: type_is_a_hint         # nega B1
```

Antes, toda alternativa errada recebia a crença do item inteiro: com três
alternativas, as duas erradas eram indistinguíveis. O exemplo acima é o
caso — um distrator é sobre valor e memória, o outro sobre tipo e tamanho.
São ideias diferentes, e negam nós diferentes.

`Atividade.crenca` passou a ser **derivada**: entre os distratores, a que
nega o nó que o item mira. Distrator que nega outro nó é informação sobre o
vizinho, e quem vai tratar disso é a camada de razão.

**B1 ganhou crença própria:** `type_is_a_hint` — *"toda variável ocupa o
mesmo espaço; o tipo é só um aviso para o compilador"*. Procedência **E**,
a única do catálogo: elaborada do modelo de máquina, sem fonte empírica,
declarada como hipótese a testar. E o distrator *"porque o nome b vem
depois no alfabeto"* saiu: ninguém sustenta essa ideia, e como razão seria
uma opção que nunca é escolhida.

## A camada da razão

Depois de responder, a resposta **tranca** e vem a segunda pergunta: *por
quê*. Trancar não é detalhe de interface. As razões erradas são enunciados
de crenças — lê-las antes de responder entrega a pista e muda a resposta de
quem ia acertar. Com a camada 1 fechada, o par resposta-razão é
independente, que é o que a classificação pressupõe.

**As razões vêm do grafo, nunca de um banco de razões:**

| Razão | De onde sai |
| --- | --- |
| a certa | o enunciado do nó que o item mira |
| as erradas | o que afirmam as crenças apontadas pelas alternativas |

Se houvesse um banco de razões escritas à mão, a razão e a premissa
poderiam divergir, e o diagnóstico passaria a medir a redação do item.

**Uma razão pode falar de outro nó.** O item `ciu_kc00_002` mira B1 e
oferece, entre as razões, a crença de que sem valor não há memória — que
nega **B2**. Explicar por ela é informação sobre B2, e o evento
`camada2_respondida` grava isso em `fala_do_no`. O que o sistema **faz**
com essa informação é a tarefa seguinte (T4); por ora ele registra.

A ordem das razões é embaralhada por uma permutação derivada da sessão:
`ordem_das_razoes(semente, atividade, n)`. O motor continua puro — não
sorteia — e recarregar a página não reembaralha as alternativas debaixo de
quem está lendo.

**Item sem crença nas alternativas pula a camada 2**, registrando
`razao_pulada`: com uma alternativa só não há escolha a fazer.

## A camada da confiança

Tela própria, depois das duas escolhas, **em toda atividade** — inclusive
no treino. Duas decisões:

**Própria, e não no pé da tela da razão.** A pergunta é sobre as duas
escolhas juntas; declarar confiança antes de ver o par formado mede outra
coisa. Custa um passo a mais por item, e compra independência entre as
camadas — que é o que sustenta a tabela de classificação.

**Em toda atividade, não só no diagnóstico.** O critério de sucesso diz
que a razão muda *sem queda de confiança*. Queda exige **duas** medidas, e
a segunda acontece depois da refutação, no treino. Antes a confiança só
era pedida no diagnóstico, e esse número não existia.

O treino não pergunta o porquê, só a confiança: a razão é do diagnóstico,
onde ela separa chute, vacilo e crença. No treino o nó já foi refutado, e
o que está em jogo é se a premissa se sustenta noutra superfície.

Cada camada grava o **próprio tempo**:

```
camada1_respondida  {correta: true,  ms: 301}
camada2_respondida  {razao_correta: true, fala_do_no: "B1", ms: 703}
camada3_respondida  {confianca: "tenho certeza", ms: 6582}
```

Sem isso não dá para saber se a pessoa demorou a responder ou a
justificar — e é a segunda que interessa.

## As invariantes, cobradas na carga

| # | Regra | Teste |
| --- | --- | --- |
| 1 | uma crença nega **exatamente um** nó, e o grafo concorda | `test_invariante_1_uma_crenca_nega_exatamente_um_no` |
| 2 | toda crença é apontada por **alguma alternativa** | `test_invariante_2_toda_crenca_aparece_em_alguma_alternativa` |
| 3 | todo nó tem pelo menos **duas superfícies** | `test_invariante_3_todo_no_tem_duas_superficies` |
| — | o gabarito nunca carrega crença | `test_uma_crenca_so_pode_ser_apontada_por_alternativa_errada` |
| — | todo nó com crença tem analogia de resgate | `test_todo_no_com_crenca_tem_analogia_de_resgate` |

Cada uma tem um domínio que a quebra, montado do real com uma mutação
cirúrgica — e `test_o_dominio_real_carrega_sem_problema` é a contraprova.

## Por que o treino tem banco próprio

Antes o treino reapresentava as duas perguntas do diagnóstico, e a teórica
voltava logo depois da de código — estranho de responder, e evidência fraca:
um acerto numa pergunta que a pessoa acabou de discutir prova pouco.

Agora o treino tem itens próprios (`uso: treino`), e só cai na reapresentação
quando eles acabam — registrando `item_reapresentado` no log. Com dois itens
de treino por nó e um teto de quatro tentativas, isso acontece quando a pessoa
erra duas vezes no mesmo nó.

**Um terceiro item de treino por nó** eliminaria a reapresentação de vez.

## O que falta para isto virar coleta

1. **Revisar as 20 atividades.** Dez vieram do seu documento; as dez de treino
   e a de código do B2 foram escritas aqui, e alimentam a medição.
2. **Decidir os parâmetros** com dados do ensaio: 2 acertos é chute informado.
3. **Reconstrução do estado pelo log.** Hoje a sessão vive em memória; o log
   já guarda tudo o que seria preciso para reconstruir.
4. **Mais um tópico**, para o reteste da pesquisa acontecer longe do treino.
