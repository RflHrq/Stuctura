# Tarefas — ciclo 1

Artefato da fase 5. Fatias verticais, pequenas, na ordem em que devem ser
feitas. Cada uma entrega algo de ponta a ponta, tem um critério de pronto
que uma máquina confere, e um commit só.

Base: [PRD.md](PRD.md). O que cada termo significa:
[context.md](context.md). Por que o código está como está:
[research.md](research.md).

**Portões** (a tarefa não fecha sem eles): **M** dados e migrações ·
**U** interface e usabilidade · **G** privacidade · **T** documentação ·
**S** segurança. Em todo commit, sem exceção: varredura de segredos.

**Parâmetros aceitos em 28/10/2026** — 2 superfícies para confirmar, 2
falsos positivos na mesma crença até virar crença ativa, 2 acertos no
treino, teto de 4, 2 reexplicações, 2 itens de diagnóstico e 2 de treino
por nó.

---

## T0 — A verificação padrão, antes de mexer no motor

**O que muda:** nada para quem usa. Passa a existir um comando único que
roda tudo e imprime pouco.

Hoje não existe `scripts/verify.sh`, não existe hook de pré-commit e não há
varredura de segredos — descoberto na fase 2. Enquanto não existir, toda
tarefa abaixo fecha sem rede de proteção.

**Arquivos prováveis:** `scripts/verify.sh` (novo).

**Pronto quando:** o comando roda varredura de segredos nos arquivos em
staging, os 280 testes, e imprime status final mais no máximo 30 linhas do
primeiro erro.

**Teste:** rodar com um segredo plantado num arquivo temporário faz o script
falhar; rodar limpo faz passar.

**Portões:** S.

---

## T1 — A crença desce da atividade para a alternativa

**O que muda:** nada visível ainda. Passa a ser possível saber **qual** ideia
a pessoa escolheu, não só que ela errou.

Hoje toda alternativa errada recebe a crença da atividade inteira
([mvp/dominio.py:236](../mvp/dominio.py:236)): com três alternativas, as duas
erradas são indistinguíveis. Sem isto, a camada de razão não tem de onde sair.

**Arquivos prováveis:** `mvp/dominio/activities_kc00.yaml`,
`mvp/dominio/graph_kc00.yaml`, `mvp/dominio/beliefs_kc00.yaml`,
`mvp/dominio.py`.

Inclui, porque é a mesma fatia:

- a crença **E** nova de B1 — *"toda variável ocupa o mesmo espaço; o tipo é
  só um aviso para o compilador"* —, com `provenance: E` e a procedência
  declarada como hipótese a testar;
- a remoção do distrator vazio *"porque o nome b vem depois no alfabeto"*
  (`ciu_kc00_t01`), que não corresponde a ideia que alguém sustente;
- as três invariantes do PRD, cobradas **na carga**.

**Pronto quando:** cada alternativa errada aponta para uma crença ou para
nenhuma, explicitamente; e um YAML que viole qualquer invariante não carrega.

**Teste:** três testes de carga, um por invariante, cada um com um YAML
inválido montado em memória; mais um teste de que as 20 atividades reais
carregam.

**Portões:** M, T.

---

## T2 — A camada de razão: segunda tela, razões vindas do grafo

**O que muda:** depois de responder, a resposta **tranca** e a pessoa diz
**por quê**. As razões não são escritas à mão: a certa é o enunciado do nó,
as erradas são as crenças que aparecem nas alternativas.

É a maior mudança de contrato do ciclo, e por isso vem cedo. O mecanismo já
existe no motor antigo ([engine/socratic.py:181](../engine/socratic.py:181));
o que muda é **quando** ele dispara.

**Arquivos prováveis:** `mvp/motor.py`, `mvp/app.py`, `mvp/web/index.html`,
`mvp/web/app.js`.

**Pronto quando:** toda atividade de diagnóstico passa por duas telas, a
resposta não pode ser alterada na segunda, e as razões são geradas do grafo.

**Teste:** o motor devolve as razões certas para um item dado; nenhuma razão
é texto vindo do YAML de atividades.

**Portões:** U, T.

---

## T3 — A confiança em tela própria, com os três pontos da escala

**O que muda:** a confiança é pedida uma vez, depois da razão, em tela
própria (decisão 12), e **em toda atividade** — hoje só no diagnóstico
([mvp/motor.py:227](../mvp/motor.py:227)).

Sem isso, o critério *"a razão muda sem queda de confiança"* não tem como
ser medido: faltaria a segunda medida.

**Arquivos prováveis:** `mvp/motor.py`, `mvp/web/`.

**Pronto quando:** as três camadas gravam eventos separados, com o tempo de
cada uma.

**Teste:** um episódio completo emite `camada1`, `camada2` e `camada3`, nesta
ordem, cada um com `ms` próprio.

**Portões:** U.

---

## T4 — A classificação nos cinco estados, e o estado no nó certo

**O que muda:** o sistema para de tratar acerto como prova. Cada episódio
cai num dos cinco estados, e **a crença vai para o nó que ela nega**, mesmo
tendo aparecido num item de outro nó.

É o coração do ciclo. Motor puro, sem tela.

**Arquivos prováveis:** `mvp/motor.py`.

Regras, conforme o PRD e a decisão 11:

| Resposta | Razão | Confiança | Estado |
| --- | --- | --- | --- |
| certa | certa | tenho certeza | confirmada |
| certa | certa | acho que sei / chutei | frágil |
| certa | errada | qualquer | falso positivo |
| errada | certa | qualquer | falso negativo |
| errada | errada | tenho certeza / acho que sei | crença ativa |
| errada | errada | chutei | lacuna |

**Pronto quando:** CS-1, CS-2, CS-3 e CS-5 passam.

**Teste:** um teste por linha da tabela, mais o teste de CS-2 — razão
`no_value_no_memory` num item de B1 marca **B2**, e deixa B1 em falso
positivo.

**Portões:** T.

---

## T5 — "Não sei" nas três camadas

**O que muda:** a pessoa pode dizer que não sabe, em vez de ser obrigada a
escolher. A lacuna passa a ser **declarada**, não inferida de confiança baixa.

**Arquivos prováveis:** `mvp/motor.py`, `mvp/web/`.

**Pronto quando:** CS-4 passa nas três camadas, e "não sei" nunca produz
crença.

**Teste:** três testes, um por camada.

**Portões:** U.

---

## T6 — O falso positivo: outra superfície, e a regra dos dois

**O que muda:** acertar pela razão errada deixa de confirmar. O sistema diz
à pessoa que a resposta está certa e a explicação leva a outro lugar
(decisão 13), e traz **outra superfície do mesmo nó**. Na segunda vez com a
**mesma** crença, isso vira crença ativa no nó que ela nega, e o percurso de
refutação dispara.

**Arquivos prováveis:** `mvp/motor.py`, `mvp/web/`.

**Pronto quando:** um falso positivo não refuta; dois com a mesma crença
refutam.

**Teste:** dois testes, um por caminho. O segundo verifica que a refutação
começa no nó **negado**, não no nó do item.

**Portões:** U.

---

## T7 — O grafo e o mapa desenhando os cinco estados

**O que muda:** o painel que já fica à vista aprende a mostrar falso
positivo e lacuna, que hoje não existem. O mapa do fim também.

**Arquivos prováveis:** `mvp/motor.py` (`estado_dos_nos`),
`mvp/web/app.js`, `mvp/web/style.css`.

**Pronto quando:** os cinco estados têm desenho distinguível sem depender só
de cor, e a nota em texto explica o caso cruzado ("a crença escolhida nega
B2, onde ela foi registrada").

**Teste:** `estado_dos_nos` devolve os cinco; conferência visual na tela.

**Portões:** U.

---

## T8 — A força da premissa escolhe o próximo item

**O que muda:** a unidade deixa de ser uma fila fixa. O próximo item é o da
premissa **mais fraca que ainda não está de pé** — é o "trabalhar onde está
fraco" sem inventar número.

Hoje a ordem é a do grafo ([mvp/motor.py:200](../mvp/motor.py:200)).

**Arquivos prováveis:** `mvp/motor.py`.

**Pronto quando:** a força é uma função pura do histórico do nó, e a unidade
termina quando a mais fraca está de pé — não quando as telas acabaram.

**Teste:** dado um estado montado à mão, o seletor escolhe o nó previsto;
e um teste de que nenhuma premissa é visitada duas vezes seguidas.

**Portões:** nenhum.

---

## T9 — O teach-back do começo e do fim

**O que muda:** antes de começar, a pessoa escreve uma frase sobre o
conceito. No fim escreve de novo, e **vê as duas lado a lado**.

É a resposta direta ao "não estou sentindo melhora": a melhora fica visível
para ela, e vira o dado mais forte do TCC.

**Arquivos prováveis:** `mvp/motor.py`, `mvp/app.py`, `mvp/web/`.

**Atenção, portão G:** texto livre escrito por participante é **dado
pessoal**. Esta tarefa não fecha sem: o aviso na tela de que a frase é
guardada, e a confirmação de que nenhum identificador direto é pedido.

**Pronto quando:** CS-8 passa.

**Teste:** as duas frases entram no log e saem na tela do mapa.

**Portões:** U, G, T.

---

## T10 — O estado reconstruído pelo log

**O que muda:** se o servidor cair no meio de uma sessão, a sessão volta.
Hoje ela se perde ([mvp/app.py:30](../mvp/app.py:30)), e o log afirma o
contrário ([mvp/log.py:8](../mvp/log.py:8)).

Numa coleta de 10 a 15 pessoas, perder uma é perder 7%.

**Arquivos prováveis:** `mvp/log.py`, `mvp/motor.py`, `mvp/app.py`.

**Pronto quando:** CS-6 passa.

**Teste:** uma sessão completa, gravada; reconstruir do log produz estado
idêntico ao que estava em memória.

**Portões:** M, T.

---

## T11 — O painel do pesquisador

**O que muda:** você observa a sessão sem interromper quem está pensando em
voz alta: estado dos nós, classificação de cada episódio, log ao vivo.

Lê **o arquivo de log**, em processo separado (decisão 10). Nunca a sessão
viva — um erro meu numa consulta não pode custar um participante.

**Arquivos prováveis:** `mvp/painel.py` (novo), `mvp/web/painel.html` (novo).

**Pronto quando:** CS-7 passa.

**Teste:** as rotas do painel são todas GET e não importam o dicionário de
sessões; matar o painel no meio de uma sessão não afeta a sessão.

**Portões:** U, S, G.

---

## T12 — O reteste do fim da sessão

**O que muda:** no fim, as crenças que foram refutadas voltam uma vez, com
outra coisa no meio. É a terceira condição do critério: *não volta*.

O mecanismo existe no motor antigo
([engine/session.py:398](../engine/session.py:398)).

**Arquivos prováveis:** `mvp/motor.py`.

**Pronto quando:** toda crença refutada na sessão é retestada uma vez, e o
resultado entra no log como evento próprio.

**Teste:** uma sessão com uma crença refutada emite exatamente um
`belief_retested`.

**Portões:** T.

---

## Depois (não entra neste ciclo)

| # | O quê | Por quê fica para depois |
| --- | --- | --- |
| D-1 | Montar a cadeia (ordenar premissas) | decisão 7; é o 2º ciclo |
| D-2 | Um terceiro item de treino por nó | elimina a reapresentação; é conteúdo, não motor |
| D-3 | Unificar os dois esquemas de domínio (P2-3) | só compensa quando um segundo tópico entrar |
| D-4 | Exportação em CSV para análise | o log em JSONL basta para 10 a 15 participantes |
| D-5 | Revisar as 20 atividades | é revisão sua, não tarefa de código |
| D-6 | **Mapear o grafo externo no nível da premissa**: qual premissa de uma KC sustenta qual premissa da seguinte | `kcs.yaml` já liga KC a KC; falta a aresta fina. É curadoria de domínio, e precisa de você — não dá para inferir do código |

## Dúvidas

1. **A força da premissa (T8) pode deixar uma premissa de fora.** Se a
   unidade termina quando a mais fraca está de pé, uma premissa que nunca
   foi tocada conta como fraca ou como ausente? Proponho: nenhuma premissa
   fica sem pelo menos um episódio — a força decide a **ordem**, não se o nó
   é visitado.
2. **T6, a regra dos dois falsos positivos**, pode não disparar nunca numa
   sessão de 10 itens, se a pessoa só comete um. Isso é aceitável? Proponho
   que sim: um falso positivo isolado é registrado e tratado com outra
   superfície, e o log guarda o caso para a análise.
3. ~~T12 precisa de "outra coisa no meio" e só o kc_00 existe.~~
   **Resolvida em 28/10/2026.** O intervalo é a **KC seguinte**: as
   premissas de kc_00 que a kc_01 usa como entrada são retestadas na
   abertura da kc_01, de graça, porque a kc_01 depende delas. O reteste
   deixa de ser tela extra e vira **checagem de pré-requisito** — a mesma
   pergunta serve às duas coisas.

   Consequência para o ciclo 1: T12 fica **dentro** da unidade, como está
   escrito, e isso é declarado como limitação de ter uma KC só. Quando a
   segunda KC existir, o reteste migra para a abertura dela, sem mudar o
   evento que o log grava.
