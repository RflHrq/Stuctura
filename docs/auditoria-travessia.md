# Auditoria de percurso: o que atravessa entre tópicos

**08/11/2026. Investigação, sem implementação.** Nada no código foi
alterado para produzir este documento.

A pergunta que a originou: *quando um estudante troca de tópico, o
Structura mantém um histórico individual das oportunidades de
aprendizagem, ou reconstrói o estado a partir do tópico selecionado?*

## A resposta, em uma linha

**Reconstrói a partir do tópico selecionado, e recusa qualquer outra
coisa.** Não existe histórico individual que atravesse tópicos — não
porque alguém o tenha descartado, mas porque a unidade de tudo no
sistema é *uma sessão, um tópico*.

## As quatro evidências

**1. O processo serve um tópico só.** `mvp/app.py` faz `dominio =
carrega()` no import, e `carrega()` lê `STRUCTURA_TOPICO` do ambiente.
Trocar de tópico é reiniciar o servidor. O dicionário `sessoes`, que
guarda o estado em memória, morre junto.

**2. Os identificadores de nó colidem.** Medido nos treze tópicos:

| id | em quantos tópicos existe |
| --- | --- |
| `B1`, `B2`, `I1` | **13** |
| `B3`, `I2` | 12 |
| `I3` | 11 |

E `Estado.nos` é um mapa de **id simples** para `EstadoNo`. Dois tópicos
no mesmo estado compartilhariam a entrada `I3` — a do kc_02 e a do
kc_06, que falam de coisas diferentes.

**3. A reconstrução recusa travessia, de propósito.** `log.reconstroi`
lê o **primeiro** `unidade_iniciada` e levanta `LogIncompleto` se o
tópico não for o do domínio carregado, com esta justificativa escrita:

> *"As entradas são posições de alternativas. Aplicadas a outro banco de
> atividades elas apontam para outras opções, e o estado sai plausível e
> errado."*

É uma recusa correta. Mas ela também sela o ponto: a sessão é de um
tópico, e o log não foi feito para contar uma história mais longa.

**4. O log não registra conceito, só premissa.** Varridos todos os
ensaios:

| evento | ocorrências | o que carrega |
| --- | --- | --- |
| `unidade_iniciada` | 87 | `topico` |
| `ensino_apresentado` | 194 | `no`, `indice`, `total`, `momento` |
| `premissa_apresentada` | 45 | `no`, `antes_de` |

**Nenhum evento diz qual CONCEITO um cartão ensinou.** Que o cartão do
I3 do kc_02 apresenta `funcao_com_parametro` é uma verdade do
`conceitos.yaml`, não do log. A oportunidade de aprendizagem é
*declarada no currículo*, nunca *registrada na sessão*.

## Os cinco cenários

| cenário | o que acontece hoje |
| --- | --- |
| **Início pelo kc_02** | O cartão do I3 é apresentado por `PRIMEIRO_CONTATO` antes da primeira pergunta do I3, com a ampliação que explica passagem por valor. O log grava `premissa_apresentada {no: I3}` — **não grava o conceito**. |
| **Início pelo kc_06** | Nenhuma oportunidade anterior. O processo serve só o kc_06; os cartões dele **pressupõem** `funcao_com_parametro` e não o ensinam. Os 24 itens cobram. |
| **Declaração de desconhecimento** | **Dentro** do tópico, funciona: lacuna leva a construção, que mostra o cartão do nó. **Entre** tópicos, não existe: dizer "não sei" no kc_06 constrói o nó do kc_06, nunca o conceito que falta do kc_02. |
| **Troca de tópico** | Nada é preservado. Processo novo, domínio novo, memória limpa, e a reconstrução recusa um log de outro tópico. |
| **Retorno ao tópico** | Dentro do mesmo tópico, o log reexecuta e o estado volta inteiro — inclusive quais premissas já foram apresentadas. Entre tópicos, nada volta. |

## As três situações, separadas

| situação | onde ela vive hoje | atravessa tópicos? |
| --- | --- | --- |
| **Conhecimento apresentado** | `conceitos.yaml`, por declaração curricular; e `premissa_apresentada` no log, por nó | **não** — o log diz o nó, não o conceito |
| **Conhecimento confirmado** | `EstadoNo.estado == CONFIRMADO`, e `unidade_encerrada {confirmados}` no log | **não** — o id do nó colide entre tópicos |
| **Sem oportunidade** | o validador deriva comparando construto do item com o inventário | sim, mas **por currículo declarado**, não por história da pessoa |

## O que isto significa para o princípio

> *Nenhum conhecimento deve ser cobrado antes de existir uma
> oportunidade identificável de aprendizagem.*

**Dentro de um tópico, o princípio tem mecanismo e teste.** É o
`PRIMEIRO_CONTATO`, criado em `d7bcec4` com este argumento: *"Perguntar
o que não foi apresentado não mede concepção errônea: mede quem já sabia
de antes."* E há teste percorrendo a sessão inteira a cobrar isso.

**Entre tópicos, o princípio é uma declaração sem dente.** O grafo de
pré-requisitos existe (`kc_06 → kc_04 → kc_02`), e o carregador o
**descarta**: `prerequisites` não chega ao objeto `Dominio`, e nada no
motor o lê.

A palavra que falta mecanismo é **"identificável"**. O sistema sabe o
que o currículo promete e o que aconteceu numa sessão. Não sabe o que
aconteceu com uma *pessoa*.

## O que isso muda no desenho do tabuleiro

Um tabuleiro que apenas **recomenda** não fecha essa lacuna: ele ordena
a vitrine e a garantia continua dependendo de o estudante obedecer.

O que fecharia é menor e mais fundo do que um tabuleiro:

1. **O log passar a dizer o conceito**, e não só o nó — `premissa_apresentada` com a lista que aquele cartão apresenta. Aí "teve oportunidade" vira fato registrado, e não inferência a partir do currículo.
2. **O nó ser identificado com o tópico** (`kc_02:I3`, e não `I3`) onde o estado atravessa. Hoje a colisão é inofensiva porque nada atravessa; no dia em que atravessar, ela é silenciosa e grave.
3. **O percurso de uma pessoa ser uma leitura sobre os logs dela**, por código de participante, e não um estado novo a manter.

O item 3 é barato: o log já guarda tudo por sessão, e o código do
participante **é** o id da sessão. O que falta é algo que leia os vários
logs de um mesmo código — e isso não existe porque, até hoje, uma pessoa
fazia uma sessão.

## O que esta auditoria não respondeu

- **Se alguém de fato começaria pelo kc_06.** Hoje quem escolhe o tópico
  é quem sobe o servidor, não o estudante. A pergunta só passa a existir
  quando houver escolha.
- **Quanto da dívida de `funcao_com_parametro` some** se o percurso for
  garantido. São 63 itens em 11 tópicos, e todos a jusante do kc_02 no
  grafo — mas isso é o currículo declarado, não história medida.
- **Se o reteste atravessa.** Não investiguei; ele é por sessão, como o
  resto, mas a medida de transferência da tese pode ter desenho próprio.
