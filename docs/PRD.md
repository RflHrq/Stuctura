# PRD — Structura, primeiro ciclo

Artefato da fase 4. Descreve **o resultado**, não a implementação.

Entradas: [problema.md](problema.md) (critério e instrumento),
[research.md](research.md) (o que existe), [context.md](context.md)
(vocabulário), [processo.md](processo.md) (decisões 1 a 13).

## Objetivo

Uma unidade de aprendizagem que, para cada premissa de um tópico, descobre
em qual dos **cinco estados** a pessoa está, trata cada estado de um jeito
diferente, e deixa no log a evidência de que o estado mudou — ou de que
não mudou.

O produto é o instrumento do TCC **e** tem de funcionar como produto: se
a pessoa não sentir que está aprendendo, o dado não vale nada, porque ela
responde até o fim no modo "clicar para acabar".

## Usuários

| Quem | O que faz | Onde |
| --- | --- | --- |
| Participante | atravessa uma unidade, 20 a 30 min, pensando em voz alta | máquina do pesquisador, navegador |
| Pesquisador (você) | abre a sessão, observa pelo painel, exporta o log | a mesma máquina, outra janela |
| Orientador | lê o mapa e o log depois | arquivos |

## O fluxo

```
frase do começo (teach-back)
  └─ para cada premissa escolhida pela FORÇA (a mais fraca de pé):
       camada 1  o que acontece        → tranca
       camada 2  por quê               → razões vindas do grafo
       camada 3  quanta confiança      → uma vez
       classifica (resposta × razão × confiança)
         ├─ confirmada     segue
         ├─ frágil         volta depois, noutra superfície
         ├─ falso positivo não confirma; outra superfície do mesmo nó
         ├─ falso negativo segue, sem contestar a ideia
         ├─ crença ativa   valida → refuta → treina → confirma
         └─ lacuna         constrói: ensino do nó e item de entrada
  └─ reteste das crenças refutadas, com outra coisa no meio
  └─ frase do fim, as duas lado a lado
  └─ mapa do que ficou de pé, e por qual caminho
```

As quatro caixas de **crença ativa** já existem e funcionam
([mvp/motor.py](../mvp/motor.py)); o que é novo é tudo o que decide
**quando** entrar nelas.

## Critérios de sucesso

Frases testáveis. Cada uma vira teste automático, exceto onde digo que não
dá — e aí digo como fica provado.

| # | Critério | O que o prova |
| --- | --- | --- |
| CS-1 | Um acerto com razão errada **não** confirma a premissa | teste: episódio certo+errado deixa o nó em `falso_positivo`, nunca `confirmada` |
| CS-2 | A crença escolhida como razão é registrada **no nó que ela nega**, mesmo vindo do item de outro nó | teste: razão `no_value_no_memory` num item de B1 marca B2, e só B2 |
| CS-3 | Um erro com razão certa **não** dispara refutação | teste: episódio errado+certo não emite `refutacao_iniciada` |
| CS-4 | "Não sei" em qualquer camada produz **lacuna**, nunca crença | teste, nas três camadas |
| CS-5 | Nenhuma premissa é confirmada sem **duas superfícies diferentes** | teste: um acerto só deixa o nó `fragil` |
| CS-6 | O estado completo da sessão é reconstruível **só pelo log** | teste: reproduzir o log evento a evento reproduz o mesmo estado final |
| CS-7 | O painel do pesquisador não escreve nada, e não tem acesso à sessão viva | teste: as rotas do painel são GET e não tocam o dicionário de sessões |
| CS-8 | As duas frases do teach-back ficam no log, e aparecem lado a lado no fim | teste de rota, mais conferência na tela |
| CS-9 | O domínio inválido falha **na carga**, nunca em sessão | teste: cada regra de validação tem um YAML que a quebra |
| CS-10 | A unidade termina com toda premissa num dos cinco estados, nenhuma indefinida | teste: percurso completo não deixa `desconhecido` |
| CS-11 | Uma pessoa real atravessa a unidade sozinha, sem perguntar o que a tela quer | **não é teste automático**: ensaio com 3 pessoas, registrado no relatório de interface |
| CS-12 | A pessoa consegue dizer, no fim, o que mudou na cabeça dela | **não é teste automático**: a comparação das duas frases, classificada por codebook |

CS-11 e CS-12 são os únicos que o computador não prova. Estão aqui para
não sumirem.

## Requisitos de interface

- Três camadas em **três telas**, com a resposta trancando antes de as
  razões aparecerem (D-8), e a confiança em tela própria (D-12).
- **"Não sei"** presente nas três camadas, com peso visual de opção, não de
  desistência.
- O grafo à vista a unidade inteira, sabendo desenhar os cinco estados.
- O retorno do falso positivo **conta** à pessoa que a resposta está certa e
  a explicação não (D-13).
- O retorno da crença ativa continua **neutro**: quem ensina é a refutação.
- Teclado: toda escolha alcançável por Tab e Enter; a pessoa pensa em voz
  alta e às vezes tira a mão do mouse.
- Sem efeito visual pesado, sem animação de recompensa.

## Requisitos de dados

| Item | Decisão |
| --- | --- |
| Fonte da verdade | o log append-only de eventos; o estado é projeção |
| Formato | JSONL por execução no primeiro ciclo; SQLite quando a coleta exigir consulta |
| Crença na alternativa | cada alternativa errada aponta para **uma** crença, ou para nenhuma (P1-1) |
| Invariante 1 | uma crença nega **exatamente um** nó; violou, não carrega |
| Invariante 2 | toda crença do catálogo aparece em alguma alternativa |
| Invariante 3 | todo nó tem pelo menos duas superfícies diferentes |
| Retenção | o log fica enquanto o TCC existir; identificação só por código P01…P40 |

## Requisitos de privacidade

O teach-back muda a conversa: **texto livre escrito pelo participante é
dado pessoal**, ainda que sem nome. Alguém pode escrever "não entendi isso
na aula do professor X".

| Item | Decisão |
| --- | --- |
| Finalidade | pesquisa acadêmica de graduação, declarada no termo |
| Base legal | consentimento do participante, por escrito, antes da sessão |
| O que é coletado | respostas, razões, confianças, tempos, as duas frases, áudio se autorizado |
| O que **não** é | nome, matrícula, e-mail, curso, nada que identifique diretamente |
| Direitos | o participante pode pedir a exclusão dos dados dele pelo código |
| Rascunhos | termo de consentimento e aviso são **rascunho**, para revisão do orientador e do comitê de ética |

## Requisitos de operação

Roda na sua máquina, offline, você mesmo opera. Sobe com um comando e o
navegador. Sem nuvem, sem custo, sem domínio.

- **Parada tolerável:** minutos. Se cair no meio de uma sessão, a sessão é
  retomada pelo log (CS-6) — hoje ela se perde (P1-2).
- **Perda tolerável: zero.** O log de uma sessão de coleta é
  irreproduzível: a pessoa não volta.
- **Cópia:** depois de cada sessão, o log vai para uma segunda mídia. Backup
  que nunca foi restaurado não conta — o ensaio de restauração entra na
  revisão final.

## Fora do escopo do primeiro ciclo

- **Montar a cadeia** (ordenar premissas): segundo ciclo, decisão 7.
- XP, vidas, ofensiva, ranking: variável concorrente.
- Repetição espaçada entre dias; BKT ou modelo probabilístico; dica
  progressiva; correção automática do texto livre. Os motivos estão em
  [problema.md](problema.md).
- Mais de um tópico além do kc_00, até você decidir a coleta.
- Qualquer coisa que exija internet.

## Parâmetros, que são decisão sua

O sistema funciona com qualquer valor; estes são o ponto de partida e
**precisam do seu aceite**, porque são regra, não implementação.

| Parâmetro | Proposto | Efeito se mudar |
| --- | --- | --- |
| Superfícies para confirmar | 2 | 3 endurece o verde e alonga a sessão |
| Falsos positivos na mesma crença até virar crença ativa | 2 | 1 refuta cedo demais; 3 pode nunca disparar |
| Acertos seguidos no treino | 2 (como hoje) | — |
| Teto de tentativas por nó | 4 (como hoje) | — |
| Reexplicações por premissa | 2 (como hoje) | — |
| Itens por nó | 2 diagnóstico + 2 treino (como hoje) | 3 de treino elimina a reapresentação |

## Riscos

| Risco | Por que importa | O que reduz |
| --- | --- | --- |
| A sessão fica longa demais com três camadas | 10 itens × 3 telas cansa, e cansaço vira chute | medir o tempo no ensaio antes da coleta; a força da premissa encurta |
| A camada de razão ensina sem querer | as razões são enunciados de premissas; lê-las é informação | a resposta tranca antes (D-8); medir se o acerto sobe depois da primeira razão lida |
| A crença E de B1 não existir na cabeça de ninguém | distrator que ninguém escolhe enfraquece o item | é hipótese declarada; o ensaio diz |
| Perder uma sessão por queda | 1 de 10 a 15 participantes é 7% | CS-6, e cópia depois de cada sessão |
| O painel atrapalhar a sessão | observar não pode custar o dado | CS-7: só leitura, só o log |

## Perguntas em aberto

1. Quantos tópicos a coleta usa, e em que ordem.
2. Onde fica o reteste do fim da sessão enquanto só o kc_00 existe.
3. Quem classifica as frases do teach-back, e com que codebook.
4. A crença E de B1 fica como hipótese, ou você procura fonte antes.
5. Os parâmetros da tabela acima.
