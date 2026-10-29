# Contrato de linguagem

Como se escreve conteúdo no Structura: os nós, as crenças, as analogias e
as atividades. É o documento que o autor de domínio usa, e o revisor
cobra.

Ele existe porque o sistema mede **mudança conceitual**, e uma frase mal
escrita não produz um dado ruim — produz um dado *plausível e errado*. Se
a premissa diz duas coisas, a pessoa concorda com uma e o log registra que
ela concordou com as duas. Se a metáfora estica, o sistema ensina uma
concepção errônea nova e depois a mede como se fosse do aluno.

Os exemplos todos saem do material que já existe: `mvp/dominio/` (kc_00) e
`domain/c_pointers/` (12 tópicos, 93 nós). Os ruins também.

---

## 1. As três vozes

Cada nó é escrito duas vezes, e as duas servem a coisas diferentes. Nunca
misture.

| Campo | Para quem | Como soa |
| --- | --- | --- |
| `text` | para o mapa, o log e a análise | afirmação precisa, pode ser técnica |
| `plain_text` | para a pessoa na tela | alguém explicando, sem jargão novo |
| `label_pt` (crença) | para a pessoa, na camada 2 | o que **ela** diria, em primeira pessoa |

**Bom, do kc_00:**

```yaml
text: "Declarar ja reserva o espaco, antes de qualquer valor entrar."
plain_text: >
  Quando voce escreve int x;, a caixa de x ja existe — so o que tem
  dentro ainda nao esta definido.
```

A primeira é uma afirmação que se discute. A segunda é uma pessoa falando.

### Regras do `plain_text`

1. **Presente do indicativo.** "A caixa já existe", não "a caixa terá sido
   reservada".
2. **No máximo ~20 palavras.** Se não cabe, o nó provavelmente são dois.
3. **Nenhum termo que a unidade ainda não apresentou.** Se o nó precisa da
   palavra "endereço" e ela não foi introduzida, ou se introduz antes ou
   se escreve sem ela.
4. **Concreto antes de geral.** "O que estava naquele lugar antes continua
   lá" vence "o conteúdo é indeterminado".
5. **Reler em voz alta.** Se trava na boca, trava na cabeça.

### Regras do `text`

1. Uma afirmação, no indicativo, **com a qual dá para discordar**.
2. Sem "pode", "geralmente", "normalmente": hedge não se nega, e o que não
   se nega não vira crença.
3. Termo técnico é permitido e desejável — este campo é o que vai à banca.

---

## 2. O nó é uma afirmação atômica

**A pergunta de corte:** *dá para concordar com metade desta frase?* Se
dá, são dois nós.

A curadoria já aplica a heurística e marcou 9 nós: o enunciado tem `;`,
"mas" ou "porque" ligando duas afirmações, ou passa de 16 palavras.

**Ruim, de `kc_04:B2`:**

```
&x devolve o endereco de x; nao copia x.
```

São duas afirmações. Alguém pode aceitar a primeira e negar a segunda — e
é exatamente aí que mora a concepção errônea. Viram:

```
B2a  &x devolve o endereco de x.
B2b  &x nao copia x.
```

**Ruim, de `kc_10:B4`:**

```
O tipo diz quantos niveis existem; nao e opcional.
```

A segunda metade nem é sobre o mesmo assunto: é uma regra de uso colada
numa afirmação de modelo.

### Observável ou inferência

- **Observável** é o que a pessoa pode *ver acontecer*: compilar, imprimir,
  comparar duas execuções.
- **Inferência** é o que se conclui de dois ou mais nós, e precisa declarar
  de quais (`support`).

Um nó de inferência com muitos caminhos e **nenhuma crença que o negue** é
sinal de que falta mapear erro ali: é degrau que todo mundo sobe sem
nunca tropeçar, o que raramente é verdade. Hoje são 61 nós assim.

---

## 3. A crença

Uma crença **nega exatamente um nó**. Violou, o domínio não carrega — é
invariante do carregador, não recomendação.

### Ela fala na voz do aluno

**Bom:**

```yaml
label_pt: "Se eu nao dei valor, a variavel ainda nao existe na memoria."
label_pt: "Declarar ja zera a variavel, tipo em outras linguagens."
```

Alguém assina essas frases. É o teste: **se a frase só faz sentido na boca
de quem já sabe que ela é falsa, ela não é uma crença — é uma correção
disfarçada.** "O aluno confunde declaração com alocação" não é crença;
"declarar já reserva e já preenche" é.

### Procedência, sempre

| | O que significa |
| --- | --- |
| **D** | documentada: achado empírico, com fonte e página |
| **L** | registrada como erro comum em obra técnica |
| **T** | transposta de outra linguagem, com a analogia declarada |
| **N** | o erro está em norma (CERT C, CWE); a crença, não |
| **E** | elaborada a partir do modelo de máquina — **hipótese a testar** |

`E` é legítimo e precisa ser declarado como hipótese, no próprio campo
`source`, como está feito em `type_is_a_hint`: *"entra declarada como
HIPÓTESE A TESTAR. Se nenhum participante a sustentar, o achado é esse."*

Uma crença sem procedência é uma invenção sua que vai virar dado.

---

## 4. A metáfora tem o direito de calar

Uma por tópico, declarada no `analogy`, com uma versão por nó em
`resgates`. O kc_00 usa o quarto de hotel e o mantém coerente do B1 ao I1.

**A regra dura: quando a metáfora obrigaria a dizer algo falso, abandone a
metáfora naquela frase.**

**Ruim, de `kc_02:I3`:**

```
Endereço não é um número comum: ele carrega junto o tipo do que está
no destino.
```

Não carrega. O tipo é do ponteiro, e quem sabe dele é o compilador; em
tempo de execução não há tipo nenhum viajando junto do endereço. A frase
foi escrita para salvar a metáfora — e **criou uma concepção errônea nova**,
que o sistema depois mediria como se fosse do aluno.

Escreve-se sem metáfora:

```
O tipo de p não está guardado em p: quem sabe dele é o compilador. É
por isso que p + 1 anda o tamanho de um objeto, e não um byte.
```

Menos bonito, verdadeiro. **Numa ferramenta que mede concepções erradas,
inventar uma é o pior defeito possível.**

### Duas checagens antes de aceitar uma metáfora

1. **Onde ela quebra?** Escreva a resposta. Se não souber, não use.
2. **O resgate de um nó entrega a resposta de outro?** O `analogy` do kc_00
   mapeia os cinco nós de uma vez — por isso quem aparece na validação é o
   resgate **daquele nó**, nunca o resumo.

---

## 5. A atividade

### O enunciado não dá pista

- Sem negativa ("qual **não**..."): ela mede leitura, não conceito.
- Sem "sempre" e "nunca" nas alternativas — absoluto é lido como errado.
- **A alternativa certa não pode ser a mais longa.** É a pista mais comum
  e a mais fácil de eliminar: conte as palavras.
- Nada de "todas as anteriores".
- Pessoa citada no enunciado é **sem nome** ("um colega diz"). Hoje há um
  item que começa com *"Rafael diz:"* — nome do pesquisador dentro do item
  que o participante responde é ruído, e nome real num instrumento de
  pesquisa é um problema a mais.

### O distrator é a crença, dita bem

Um distrator que ninguém escolhe é item desperdiçado; um distrator sem
crença é erro sem diagnóstico. **Todo distrator aponta uma crença do
catálogo, ou sai.** Hoje, 4 dos 27 distratores do kc_00 não apontam
nenhuma.

Dois invariantes que o carregador já cobra: a alternativa certa nunca
carrega crença, e toda crença do catálogo aparece em alguma alternativa.

### Quantas alternativas

**Três ou quatro.** Hoje **13 das 20 atividades do kc_00 têm só duas** —
dois terços do banco são cara ou coroa na camada 1. A razão e a confiança
resgatam parte, mas é a fraqueza mais barata de corrigir que existe.

Máximo **um item binário por nó**, e só quando a pergunta for de fato
binária ("compila ou não compila").

---

## 6. Os formatos

`formato` não é rótulo: é a **superfície** que a CS-5 conta. Confirmar uma
premissa exige acertar em **duas superfícies diferentes**, e o treino exige
formato diferente do anterior. Com quatro formatos, o motor fica sem
superfície nova no meio do treino — está escrito em comentário no próprio
`_proximo_treino`.

**Mais formatos não é variedade: é a CS-5 valendo mais e o treino tendo
para onde ir.**

### Os quatro de hoje

| Formato | O que pede | Onde serve |
| --- | --- | --- |
| `reconhecer_conceito` | escolher a afirmação verdadeira | premissa declarativa |
| `comparar_casos` | dois trechos, mesma coisa ou não | distinguir o que parece igual |
| `achar_o_erro` | julgar uma afirmação de alguém | crença que se enuncia bem |
| `prever_saida` | dizer o que o código imprime | premissa observável |

### Os três propostos

A ordem é de custo crescente. Nenhum existe hoje — todos pedem trabalho de
motor e de tela, e viram tarefa de um ciclo, não conteúdo.

#### `apontar_a_linha` — o mais barato

Código com linhas numeradas; a pessoa escolhe **em qual linha** está o
problema. Cada linha é uma alternativa, então por dentro continua múltipla
escolha: **zero mudança no motor**, só na tela.

```
1  int *p;
2  *p = 10;
3  printf("%d\n", *p);
```
> Em que linha o programa já fez algo inválido?

A linha errada escolhida aponta uma crença, como qualquer distrator. Muda
a sensação sem mudar a mecânica — e é a primeira que eu faria.

#### `completar_lacuna` — o que você pediu

Uma a três palavras, em prosa ou em código. É o formato que mais serve a
conceito, e o que mais **tira a pista**: múltipla escolha entrega a
resposta no meio das outras; digitar, não.

> Depois de `int x;`, o espaço de x já está ________ , mas o conteúdo
> ainda é ________ .

**O que ele custa:**

- um canal de resposta novo (texto na camada 1, onde hoje só vai índice);
- normalização no motor: espaços, maiúsculas, acentos. **E só isso** — o
  motor não interpreta conteúdo, nunca interpretou;
- uma tabela no item, escrita pelo autor:

```yaml
formato: completar_lacuna
lacunas:
  - aceita: [reservado, separado, criado]
    erros:
      "indefinido": no_value_no_memory
      "vazio": no_value_no_memory
  - aceita: [indeterminado, lixo, desconhecido]
    erros:
      "zero": declaration_zeroes
      "0": declaration_zeroes
```

**A regra que vem da revisão do ciclo 1:** uma resposta que não casa com
`aceita` nem com `erros` é **`resposta_nao_prevista`** — errada, sem
crença, e registrada como tal. **Nunca lacuna.** Tratar o imprevisto como
"declarei que não sei" foi exatamente o defeito P1-A, que pôs erro de
cliente na base como declaração do aluno. O painel mostra as não previstas
para o autor crescer a tabela entre sessões.

Limite de 60 caracteres por lacuna. "Não sei" continua sendo um botão, não
uma palavra digitada.

#### `prever_saida_escrita`

O `prever_saida` sem alternativas: a pessoa digita o que o programa
imprime. Mesmo canal do `completar_lacuna`, mesma tabela. É o formato mais
honesto que existe para premissa observável — e o mais duro, porque não há
onde se apoiar.

Use com parcimônia: duro demais cedo demais vira chute, e chute vira
lacuna.

#### Um que eu não recomendo agora

**Ordenar passos** (pôr 3–4 eventos na ordem em que acontecem) mede bem o
modelo de execução, mas pede um canal de resposta que é uma permutação, e
uma tela que funcione no teclado — a pessoa pensa em voz alta e tira a mão
do mouse. Fica para depois dos outros três.

### O que vale para todos os formatos novos

- **A camada 2 não muda.** A crença e o nó a que ela pertence vêm sempre da
  razão: `crenca = p.razao.crenca`, `alvo = p.razao.no`. É por isso que a
  camada 1 pode mudar de forma sem o instrumento perder diagnóstico — e é
  o que torna esta seção possível.
- Todo formato novo entra em `FORMATOS`, em `mvp/dominio.py`, e passa a
  contar como superfície.
- Toda tela nova tem de ser alcançável por Tab e Enter.

---

## 7. A lista de conferência

Antes de aceitar um **nó**:

- [ ] `text` é uma afirmação com a qual dá para discordar
- [ ] não dá para concordar com metade dela
- [ ] menos de 16 palavras, sem `;`, sem "mas", sem "porque"
- [ ] `plain_text` tem até ~20 palavras e nenhum termo não apresentado
- [ ] se é inferência, `support` lista de quais nós ela sai

Antes de aceitar uma **crença**:

- [ ] nega exatamente um nó
- [ ] alguém assinaria a frase em primeira pessoa
- [ ] tem procedência, e `E` está declarada como hipótese
- [ ] aparece em pelo menos uma alternativa

Antes de aceitar uma **atividade**:

- [ ] três ou quatro alternativas (no máximo um binário por nó)
- [ ] a certa não é a mais longa
- [ ] todo distrator aponta uma crença
- [ ] o enunciado não tem negativa, "sempre", "nunca" nem nome de pessoa
- [ ] o nó tem pelo menos dois formatos diferentes no banco de treino

Antes de aceitar um **tópico inteiro**:

- [ ] `python -m tools.curadoria` e olhar os três buracos: nós sem
      atividade, nós sem crença, nós grandes demais
- [ ] o **caminhante** atravessa o tópico com as três personas e **nenhuma
      premissa termina sem estado**

O caminhante é o último portão, e é novo: ele atravessa a unidade pelo
HTTP como quem acerta, como quem erra e aprende, e como quem erra e não
muda de ideia. Foi ele que mostrou, na revisão final, que 9 sessões em 30
terminavam com uma premissa que o sistema não classificou. **Conteúdo novo
passa por ele antes de qualquer pessoa ver a tela.**
