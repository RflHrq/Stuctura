# MVP — treino até domínio

Implementa o laço do documento de 01/10/2026: **identifica → refuta →
treina → confirma**. Um nó só vira premissa correta depois de uma sequência
de acertos no treino, nunca depois de um acerto isolado.

Conteúdo: **kc_00, declaração de variáveis** — 5 premissas, 4 concepções
errôneas, 10 atividades (uma teórica e uma de código por nó) e a analogia do
quarto de hotel.

```bash
python -m pytest mvp/ -q     # 26 testes
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
escrita) e em cada passo da refutação.

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
│   └── activities_kc00.yaml   10 atividades + a analogia de resgate por nó
├── dominio.py                 carga e validação (falha na carga, nunca em sessão)
├── motor.py                   o laço, puro: (estado, resposta) → (estado, tela, eventos)
├── log.py                     append-only, uma linha JSON por evento
├── app.py                     três rotas
├── web/                       a interface, que não decide nada
├── web/figuras.js             a analogia desenhada, uma por premissa
└── test_motor.py              26 testes
```

**Uma armadilha de YAML**, já resolvida: a chave `no:` é lida como booleano
falso (YAML 1.1). As atividades usam `premissa:` para apontar o nó.

## O limite do banco atual

Cada nó tem **dois** itens: a teórica e a de código. Os dois são consumidos na
checagem de vacilo, então o treino depois da refutação não tem item inédito —
ele **reapresenta** um dos dois, nunca o que acabou de aparecer, e registra
`item_reapresentado` no log.

Isso cumpre o critério literal do RF34 (não repetir o mesmo item *em
sequência*), mas enfraquece a evidência: um streak de dois acertos em itens já
vistos prova menos do que em itens novos. **Um terceiro item por nó resolve** —
de preferência de transferência distante.

Efeito colateral: com dois itens por nó, as duas metades do RF34 (não repetir
item, não repetir formato) selecionam sempre a mesma coisa, e nenhum teste
sobre este domínio consegue distinguir uma da outra. O teste
`test_rf34_a_regra_de_formato_vale_mesmo_havendo_item_inedito` contorna isso
montando um nó de três itens em memória.

## O que falta para isto virar coleta

1. **Um terceiro item por nó**, para o treino não depender de reapresentação.
2. **Decidir os parâmetros** com dados do ensaio: 2 acertos é chute informado.
3. **Reconstrução do estado pelo log.** Hoje a sessão vive em memória; o log
   já guarda tudo o que seria preciso para reconstruir.
4. **Mais um tópico**, para o reteste da pesquisa acontecer longe do treino.
