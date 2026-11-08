# Histórico individual: especificação

**08/11/2026. Especificação e testes de arquitetura. Nenhuma mudança no
motor.**

O que falta ao Structura não é um tabuleiro. É a quarta camada:

| camada | existe hoje |
| --- | --- |
| grafo curricular | sim — e o `prerequisites` é **descartado** pelo carregador |
| motor pedagógico | sim |
| log de eventos | sim — por sessão, por nó, **nunca por conceito** |
| **histórico individual** | **não** |

## As três perguntas, respondidas com evidência

### 1. O código do participante é a mesma pessoa entre sessões?

**Hoje, por acidente de arquivo — e o guarda que protege a identidade é
o mesmo que impede o histórico.**

`app.py` recusa com **409** um código que já exista **naquele log**, e a
razão está escrita: *"abrir duas vezes o mesmo código juntaria duas
pessoas num participante só, e a análise não teria como separar
depois."*

O log é **um arquivo**, escolhido por `STRUCTURA_LOG`. Como cada
configuração de lançamento usa um arquivo diferente, o mesmo código
hoje **pode** reaparecer noutro tópico — não por desenho, mas porque os
arquivos são separados.

**A colisão:** um histórico individual quer **um log para todos os
tópicos**. Nesse log, o 409 recusaria o participante no segundo tópico.

**Especificação.** O guarda passa a ser `(código, tópico)`, não
`código`. Um participante pode abrir o kc_02 e depois o kc_06; não pode
abrir o kc_02 duas vezes. A razão original — não fundir duas pessoas —
continua atendida, porque o que ela protege é a sessão, não a pessoa.

### 2. O reteste atravessa tópicos?

**Não. E isso é mais sério do que parece, porque a identidade que
permitiria atravessar já existe.**

`_item_de_reteste` procura em `d.atividades` — o domínio carregado, que
é **um tópico**. E `_superficie_nova` compara **formato de pergunta**.
Então o que o reteste mede hoje é:

> a crença refutada volta numa **superfície diferente** — outro formato
> de pergunta — **dentro do mesmo tópico**.

Isso é transferência de **superfície**, não de **contexto**.

**E a travessia é alcançável.** Medido: **14 das 60 crenças do projeto
aparecem em mais de um tópico.**

| crença | tópicos |
| --- | --- |
| `ampersand_copies` | kc_04, kc_06, kc_10, kc_12 |
| `pointer_is_data` | kc_02, kc_04, kc_08, kc_12 |
| `pointer_is_just_a_name` | kc_04, kc_05, kc_10 |
| `pointer_is_integer` | kc_02, kc_11 |
| (mais dez) | dois tópicos cada |

Uma crença refutada no kc_02 poderia voltar no kc_08, no mesmo id, num
contexto genuinamente outro. **O catálogo já sustenta a medida que a
tese quer; o mecanismo é que não a faz.**

**Especificação.** O reteste entre contextos é uma medida NOVA, e não
uma extensão da atual. Ela precisa de nome próprio no log
(`crenca_retestada_em_outro_contexto`), porque misturá-la com
`belief_retested` tornaria impossível separar as duas na análise — e são
coisas diferentes para a banca.

### 3. Como reconhecer que falta oportunidade, ao começar pelo kc_06?

As peças existem e estão desligadas:

| peça | estado |
| --- | --- |
| `prerequisites` no YAML do tópico | declarado nos 13, **descartado pelo carregador** |
| `conceitos.yaml` com `introduzido_em` | existe |
| construto que cada item usa | o validador já detecta |

**Especificação, sem tocar no motor.** Uma verificação de entrada, antes
da sessão começar: dado um código e um tópico, ler os logs daquele
código, computar quais tópicos ele concluiu, e dizer quais conceitos
exigidos pelo tópico escolhido **não têm oportunidade registrada**.

É leitura, não estado novo. E responde na forma que o princípio pede:
não *"você não pode"*, mas *"isto aqui vai cobrar o que você não teve
chance de aprender"*.

## Os quatro eventos conceituais

Hoje o log grava `ensino_apresentado {no}` e `premissa_apresentada
{no}` — **por nó, nunca por conceito**. Que o cartão do I3 do kc_02
apresenta `funcao_com_parametro` é verdade do `conceitos.yaml`, não do
log.

| evento | o que demonstra | de onde sai |
| --- | --- | --- |
| `conceito_apresentado` | teve oportunidade | cartão mostrado + os conceitos declarados nele |
| `conceito_diagnosticado` | demonstrou algo no diagnóstico | `episodio_classificado`, com o conceito do item |
| `conceito_confirmado` | evidência de domínio pela regra do sistema | `no_confirmado`, com os conceitos do nó |
| `conceito_revisitado` | foi trabalhado de novo | treino, reexplicação, construção |

**Apresentação não é compreensão.** Os quatro são distintos de
propósito: sem isso, o histórico vira declaração falsa de domínio — que
é o defeito que o `conceitos.yaml` já evita ao separar `disponivel` de
`confirmado`.

### A versão do material

Cada `conceito_apresentado` carrega a **assinatura do material** que
gerou aquela tela. Se um cartão mudar amanhã, é preciso saber o que a
pessoa viu ontem.

A forma já existe no projeto: os candidatos usam `revisado_sha`, doze
primeiros caracteres do sha256 do arquivo. O mesmo serve aqui.

**Sem isso, o histórico mente em silêncio** quando o material evolui — e
este projeto reescreveu dois cartões inteiros numa única noite.

## A identidade do nó

`B1`, `B2` e `I1` existem nos **treze** tópicos; `Estado.nos` é um mapa
de **id simples**. Hoje a colisão é inofensiva porque nada atravessa.
No dia em que atravessar, ela é silenciosa e grave: o `I3` do kc_02 e o
do kc_06 ocupariam a mesma entrada.

**Especificação.** Onde o estado atravessa tópicos, o nó é
`kc_02:I3`. Dentro de uma sessão o id simples pode ficar — mudá-lo ali
mexeria no motor sem necessidade.

## Testes de arquitetura, sem tocar no motor

Cinco, e todos verificam o que já existe:

1. **Os ids de nó colidem** — pina a colisão como fato conhecido, para
   que ela seja decisão e não surpresa.
2. **Nenhum evento do log carrega conceito** — cai no dia em que o
   primeiro carregar, que é quando a especificação começa a existir.
3. **O `prerequisites` não chega ao `Dominio`** — pina o descarte.
4. **O reteste só acha item do tópico carregado** — pina o limite da
   medida de transferência atual.
5. **14 crenças aparecem em mais de um tópico** — pina a travessia
   possível, e avisa se o catálogo mudar.

São testes de **constatação**, não de requisito. Eles descrevem o
sistema como ele é, para que cada mudança dessa arquitetura seja
deliberada.

## O que esta especificação não resolve

- **Se o código do participante deve mesmo ser a identidade.** Ele é
  pseudônimo (P01…P40) e já serve à anonimização. Mas é digitado na
  URL, e nada impede duas pessoas usando o mesmo — o 409 só pega dentro
  de um log.
- **Quanto da dívida de `funcao_com_parametro` some** com percurso
  garantido. São 63 itens, todos a jusante do kc_02 no grafo declarado.
- **O custo da travessia para o piloto.** Um participante que faz vários
  tópicos gera vários `unidade_iniciada` no mesmo código, e o painel e o
  exportador presumem uma unidade por sessão.
