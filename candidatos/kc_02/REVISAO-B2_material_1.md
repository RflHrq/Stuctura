# Revisão do material do B2 — kc_02

Candidato, não é domínio. Para aprovar, escreva as duas linhas no
cabeçalho do YAML:

```yaml
revisado_por: <seu nome>
revisado_sha: 091d37b9cac1
```

A assinatura é deste conteúdo. Se o arquivo mudar, ela deixa de bater —
em vez de estampar o seu nome em texto que você não leu.

## Por que o B2, e não o B1

O B1 é **um dos dois nós, em 79, que já têm ampliação**. Montar o B1 e
achar bonito provaria pouco: ele já era o nó mais rico do projeto. O B2 é
típico — uma analogia, um exemplo, um item de entrada, zero ampliação — e
é onde mora a confusão central do tópico, a de que "ponteiro é a seta".

## O tamanho da mudança, medido

| | hoje | com o candidato |
| --- | --- | --- |
| palavras de ensino do B2 | **86** | **577** |
| itens de entrada | **1** | **3** |
| ampliação | não tem | 147 palavras |
| exemplo narrado linha a linha | não tem | 3 linhas |
| caso resolvido antes de perguntar | não tem | 165 palavras |
| segunda explicação, por outra rota | não tem | 94 palavras |

## O que a máquina já conferiu

**O oráculo (gcc, `-Wall -Wextra`, sem avisos):**

```
&x  = 00000028A21FF6EC
&p  = 00000028A21FF6E0
iguais? 0
sizeof(p) = 8   sizeof(pc) = 8   sizeof(pd) = 8   sizeof(x) = 4
```

Então as três afirmações do material estão conferidas: `&x` e `&p` saem
diferentes; `sizeof(p)` é 8 e `sizeof(x)` é 4; e o 8 é o mesmo para
`int *`, `char *` e `double *` **nesta máquina** — o material diz "nesta
máquina", e não como lei geral.

**A lista de `docs/linguagem.md`, nos dois itens novos:** três
alternativas, a certa não é a mais longa, todo distrator aponta uma
crença que existe no catálogo, o gabarito não é distrator, e o enunciado
não tem negativa, "sempre", "nunca" nem nome de pessoa.

**Duas colisões que o conferidor pegou** e que estão consertadas: a chave
`no:` virava o booleano falso em YAML (agora é `node:`), e `ciu_kc02_e3`
já era o item de entrada do B3 — a sequência `e1..e6` é uma por nó, não
por item. Os ids novos levam o nó dentro.

## O que fica para você

- A **regra da seta** vale em cada linha: desenhe a seta, nunca diga que
  o ponteiro É a seta. Confira se escorreguei em algum lugar — é a frase
  que fabrica exatamente a crença que este nó refuta.
- **Nenhuma derreferência.** `*p` é o B3 e não pode aparecer aqui.
  Confira.
- O **caso resolvido** usa endereços inventados (`0x1000`, `0x2A00`) e
  diz "digamos". Decida se isso basta ou se ele deve usar a saída real de
  uma execução.
- A **segunda explicação** troca de rota, não de metáfora — em vez de
  analogia, evidência da máquina. Veja se é isso que você quer que o
  botão "Ainda não entendi" mostre.
- Cada distrator é a crença **dita bem**? Alguém escolheria aquilo?

## O que entra sem mexer em código, e o que não entra

**Entra hoje:** a ampliação (o nó já aceita `interpretation`) e os dois
itens de entrada.

**Não entra:** `narracao`, `caso_resolvido` e `reexplicacao` são campos
que não existem. Exigem mudança no carregador, no motor e na tela — e
isso só depois de você dizer que o texto presta.

## E a descida, que não precisou ser escrita

A crença `pointer_has_no_address` **já tem descida, com quatro passos**.
São 7 descidas para 79 crenças no projeto, e as 6 do kc_02 estão entre
elas. Para este tópico, a pessoa que erra já tem o caminho inteiro
escrito: falta ligar `STRUCTURA_DESCIDA=1` e decidir, com o orientador,
se ela entra na coleta.
