# MVP — treino até domínio

Implementa o laço do documento de 01/10/2026: **identifica → refuta →
treina → confirma**. Um nó só vira premissa correta depois de uma sequência
de acertos no treino, nunca depois de um acerto isolado.

Conteúdo: **kc_00, declaração de variáveis** — 5 premissas, 4 concepções
errôneas, 21 atividades.

```bash
python -m pytest mvp/ -q     # 16 testes
python -m mvp.app            # http://127.0.0.1:8010
```

## O laço

| Passo | O que acontece | Onde |
| --- | --- | --- |
| **Identifica** | errar sem ter chutado, num distrator mapeado, levanta hipótese de crença | `motor._responde_diagnostico` |
| **Refuta** | percurso pelas premissas que sustentam o nó negado, montado do grafo | `motor._plano` |
| **Treina** | itens no mesmo nó, formato diferente a cada tentativa, até a sequência fechar | `motor._proximo_treino` |
| **Confirma** | o nó vira verde no mapa, e só então | `training_streak_completed` |

Errar chutando é lacuna, não crença: o sistema não refuta o que a pessoa
não pensa.

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
│   └── atividades_kc00.yaml   21 atividades  ← TEXTO A REVISAR
├── dominio.py                 carga e validação (falha na carga, nunca em sessão)
├── motor.py                   o laço, puro: (estado, resposta) → (estado, tela, eventos)
├── log.py                     append-only, uma linha JSON por evento
├── app.py                     três rotas
├── web/                       a interface, que não decide nada
└── test_motor.py              16 testes
```

**Uma armadilha de YAML**, já resolvida: a chave `no:` é lida como booleano
falso (YAML 1.1). As atividades usam `premissa:` para apontar o nó.

## O que falta para isto virar coleta

1. **Revisar as 21 atividades.** O texto é meu, não seu, e alimenta a medição.
2. **Decidir os parâmetros** com dados do ensaio: 2 acertos é chute informado.
3. **Reconstrução do estado pelo log.** Hoje a sessão vive em memória; o log
   já guarda tudo o que seria preciso para reconstruir.
4. **Mais um tópico**, para o reteste da pesquisa acontecer longe do treino.
