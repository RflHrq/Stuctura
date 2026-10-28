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
python -m pytest mvp/ -q     # 42 testes
python -m mvp.app            # http://127.0.0.1:8010
```

## O laço

| Passo | O que acontece | Onde |
| --- | --- | --- |
| **Identifica** | errar sem ter chutado levanta SUSPEITA; a segunda pergunta do nó, de outro formato, decide | `motor._responde_diagnostico` |
| **Valida** | a analogia de resgate daquele nó, antes de qualquer refutação | `motor._inicia_validacao` |
| **Refuta** | percurso pelas premissas que sustentam o nó negado, montado do grafo | `motor._plano` |
| **Treina** | itens no mesmo nó, formato diferente a cada tentativa, até a sequência fechar | `motor._proximo_treino` |
| **Confirma** | o nó vira verde no mapa, e só então | `training_streak_completed` |

Errar chutando é lacuna, não crença: o sistema não refuta o que a pessoa não
pensa. E um erro isolado é **vacilo** até prova em contrário — são precisos
dois erros no mesmo nó, em formatos diferentes, para a refutação disparar.

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
| `B2 ✓` cheio | premissa confirmada |
| `B2 ✓` tracejado | confirmada depois de refutação e treino |
| `B2 ✗` | crença detectada, ainda não trabalhada |
| `B2 1/2` | em treino: acertos seguidos até confirmar |
| `B2 —` | ficou em aberto |

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
└── test_dominio.py            a carga e as invariantes, 14 testes
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
