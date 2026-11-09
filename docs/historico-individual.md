# Histórico individual: especificação

**08/11/2026. Especificação e testes de arquitetura. Nenhuma mudança no
motor.**

O que falta ao Structura não é um tabuleiro. É a quarta camada:

| camada | existe hoje |
| --- | --- |
| grafo curricular | sim — e o `prerequisites` é **descartado** pelo carregador |
| motor pedagógico | sim |
| log de eventos | sim — por sessão e por nó; nenhum evento diz o que um cartão **ensinou** |
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

**E a travessia é da CRENÇA, não do nó.** Medido ao escrever os testes:
das catorze, **treze negam um nó diferente em cada tópico** —
`pointer_is_integer` nega o `I2` no kc_02 e o `B1` no kc_11. Só
`declaration_zeroes` cai no `B3` nos dois, e é coincidência.

Isso decide o índice do histórico. Um histórico indexado por nó perderia
a travessia de treze das catorze e **juntaria erradas as outras**, porque
os ids colidem entre tópicos. O índice é a crença.

E há um custo de banco a registrar: a superfície que falta ao kc_02 para
`pointer_is_integer` — o formato `comparar_casos` — **existe no kc_11**, e
o seletor não a alcança. O limite não é só arquitetural; ele custa
medida que já está escrita.

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

Hoje o log grava `ensino_apresentado {no, indice, total, momento}` e
`premissa_apresentada {no, antes_de}` — **por nó**. Que o cartão do I3 do
kc_02 apresenta `funcao_com_parametro` é verdade do `conceitos.yaml`, não
do log.

### Uma correção: o log JÁ fala de conceito, num lugar

A primeira versão desta especificação escreveu que o log é "por sessão,
por nó, **nunca por conceito**". A segunda metade é falsa, e escrever os
testes é que mostrou.

**Sete eventos da descida carregam `requer`** — `descida_iniciada`,
`descida_passo`, `descida_fechou`, `descida_sustentada`,
`descida_sem_recurso`, `descida_sem_resposta` e `cadeia_abandonada` —, e
`requer` é lista de ids de `conceitos.yaml`. A frase errada passou porque
esses eventos não dizem o que um cartão **ensinou**: dizem o que um
degrau **exige**. São coisas diferentes, e a distinção é a mesma que o
inventário já faz entre `disponivel` e `confirmado`.

Duas consequências, as duas boas:

1. **O vocabulário dos quatro eventos novos já está escolhido**: é o do
   inventário, e não um segundo catálogo. Está conferido — todo `requer`
   de todo degrau é id de `conceitos.yaml`.
2. **A convenção de nomear conceito no log já existe**, e foi construída
   no único lugar onde o projeto precisou dela até hoje.

Com uma ressalva que importa para a leitura dos ensaios: a descida está
**desligada** por padrão e, hoje, sem nenhuma cadeia aprovada — então
nenhuma sessão já gravada contém um desses sete. Medido: treze tópicos,
três personas, 39 sessões, zero eventos com conceito.

**Os quatro estão de pé, desde 09/11/2026.**

| evento | o que demonstra | de onde sai |
| --- | --- | --- |
| `conceito_apresentado` | teve oportunidade | cartão mostrado + os conceitos declarados nele |
| `conceito_diagnosticado` | demonstrou algo no diagnóstico | `episodio_classificado`, com o `estado` do episódio |
| `conceito_confirmado` | o nó fechou pela regra do sistema | `no_confirmado`, com o `via` dele |
| `conceito_revisitado` | foi trabalhado de novo | reexplicação, construção, treino |

**Apresentação não é compreensão.** Os quatro são distintos de
propósito: sem isso, o histórico vira declaração falsa de domínio — que
é o defeito que o `conceitos.yaml` já evita ao separar `disponivel` de
`confirmado`.

### O primeiro está de pé

`conceito_apresentado` entrou em 09/11/2026, com 54 testes. Uma linha
real, de uma sessão real pela rota HTTP:

```json
{"v": 3, "sessao": "P01", "tipo": "conceito_apresentado",
 "conceito": "sizeof", "no": "kc_02:B2",
 "momento": "abertura", "material": "ace8d9db95c8"}
```

**Quatro decisões, e o que cada uma custaria ao contrário:**

| decisão | se fosse ao contrário |
| --- | --- |
| **um evento por conceito** — o B2 apresenta três | uma lista obrigaria a análise a desaninhar para contar qualquer coisa |
| **o nó qualificado** (`kc_02:B2`) só neste evento; os de sessão ficam com o id simples | os ids colidem nos treze tópicos, e dois cartões ocupariam a mesma linha de histórico |
| **a declaração vem do inventário** (`evidencia.cartoes`), não de varredura de código | a auditoria de 05/11 achou **três falsos positivos** de varredura por padrão, todos com o construto num exemplo que ensina outra coisa |
| **a assinatura é do cartão**, não do arquivo | o cartão mora em dois arquivos, e um sha de arquivo mudaria quando um item de outro nó mudasse |

**A versão do log NÃO subiu, e o motivo está escrito em `mvp/log.py`.** O
gate de `reconstroi` protege a *reexecução*, e a v2 e a v3 subiram porque
um campo de **entrada** mudou de significado. Este evento não toca
entrada nenhuma: é linha aditiva, e há teste provando que apagar todas as
linhas conceituais dá o mesmo estado reconstruído. Subir para 4 faria o
sistema recusar todos os logs já gravados em troca de nada.

O que se perde está registrado: a ausência do evento numa linha v3 fica
ambígua — "nenhum conceito declarado" ou "gravada antes de o evento
existir". É tolerável **porque não há coleta gravada**. Com coleta em
andamento, a mesma mudança exigiria o número novo.

### E o número que ele revela

**Sete oportunidades por sessão no kc_02. Zero nos outros doze.**

Não é defeito do mecanismo: a auditoria do inventário cobriu kc_00, kc_01
e kc_02, e só o kc_02 tem cartão com explicação e exemplo. O evento
mostra em números o que o levantamento de material já dizia — e o número
sobe quando material novo for auditado.

E as sete são as mesmas para quem acerta tudo e para quem erra tudo. Isso
tem teste próprio: se divergisse por persona, o evento estaria medindo
desempenho em vez de apresentação, e o histórico passaria a dizer que a
pessoa teve menos chance porque foi mal.

### De onde sai o conceito nos três de percurso

**Esta é uma aproximação, e o payload declara que é.**

A especificação dizia que `conceito_diagnosticado` sairia "com o conceito
do item". **Não existe conceito do item.** O inventário declara CARTÃO, e
derivar do código do item por varredura é exatamente o que a auditoria de
05/11 provou que não funciona: três falsos positivos, todos com o
construto num exemplo que ensina outra coisa.

Então os três atribuem pelo cartão do nó, e cada evento carrega
`atribuicao: "cartao_do_no"`.

**O preço é real e precisa ficar dito:** o cartão do B2 apresenta três
conceitos, então um episódio no B2 produz três eventos, e nenhum afirma
que aquele item mediu aquele conceito — afirma que o episódio foi na
premissa cujo cartão apresenta os três. É diluição. O campo existe para a
análise saber: no dia em que houver declaração por item, ele passa a
`"item"` e as duas épocas ficam separáveis no mesmo arquivo.

E `conceito_confirmado` **não** quer dizer que a pessoa domina o
conceito: quer dizer que o nó cujo cartão o apresenta fechou pela CS-5.
Dissolver essa diferença transformaria o histórico em declaração falsa de
domínio.

### As três trajetórias que o log passou a distinguir

Medido no kc_02, com as mesmas três personas que medem a arquitetura:

| persona | apresentado | diagnosticado | revisitado | confirmado |
| --- | --- | --- | --- | --- |
| **acerta** | 7 | 14 | — | **7** |
| **crente** | 7 | 7 | 7 (treino) | **7** |
| **nao_sabe** | 7 | 14 | 7 (construção) | **nenhum** |

É a diferença entre as três linhas que torna isto uma medida. Se fossem
iguais, o log estaria registrando o currículo e não a pessoa.

E a linha que mais importa é a última: quem diz "não sei" **recebe as sete
oportunidades, é diagnosticado catorze vezes, revisita sete e nunca
confirma nada.** O log já dizia isso por nó; saber qual CONCEITO ficou
sem confirmação exigia reler o `conceitos.yaml` e cruzar à mão.

### A invariante do princípio, agora medida

> *Nenhum conhecimento deve ser cobrado antes de existir uma oportunidade
> identificável de aprendizagem.*

Dentro de um tópico isso já tinha mecanismo — o `PRIMEIRO_CONTATO` — e
nenhuma medida. Agora tem: há teste exigindo que **nenhum conceito seja
diagnosticado, revisitado ou confirmado sem ter sido apresentado antes**,
no mesmo log. A palavra que faltava mecanismo era "identificável".

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

Escritos em `mvp/test_arquitetura.py`: **36 testes**, cinco grupos,
nenhuma linha de `mvp/` alterada.

| grupo | o que pina | testes |
| --- | --- | --- |
| 1. identidade do nó | os oito ids e em quantos tópicos cada um existe; `Estado.nos` indexado por id simples; 29 eventos dizem o nó, 3 dizem o tópico, e **só os quatro conceituais qualificam** | 4 |
| 2. conceito no log | os **53** nomes de evento do motor; os quatro conceituais existem; o log fala de conceito em **duas gramáticas** — `requer`, exigência de degrau, e `conceito`, evidência de percurso — e elas não se misturam; as três trajetórias | 19 |
| 3. `prerequisites` | declarado nos 13; o carregador lê 4 das 7 chaves do tópico e descarta esta; nenhum módulo do `mvp/` a cita; `Dominio` não tem onde guardá-la | 4 |
| 4. limite do reteste | o item sai do banco carregado; esgotado o tópico o seletor desiste em vez de atravessar; a superfície que falta existe no outro tópico; `_superficie_nova` compara formato; o "já viu" é consultado por nó | 6 |
| 5. crenças que atravessam | as 14 de 60, com os tópicos; 13 negam nó diferente em cada um; todas têm item dos dois lados | 3 |

São testes de **constatação**, não de requisito. Eles descrevem o sistema
como ele é, para que cada mudança dessa arquitetura seja deliberada.

**E foram conferidos por sabotagem, não por releitura.** O perigo deste
tipo de teste é virar enfeite: passar hoje e continuar passando depois da
mudança que ele deveria acusar. Então cada fato foi quebrado de
propósito, um por vez, e o teste tinha de cair — **18 sabotagens, 18
quedas**, cobrindo os 22 testes distintos:

| sabotagem | caiu |
| --- | --- |
| nó novo existindo num tópico só | os dois testes de colisão |
| `Estado.com` qualificando o id | o teste do estado |
| `premissa_apresentada` gravando `kc_02:I3` | o teste do evento |
| `Evento("conceito_apresentado", …)` no motor | a catraca dos 49 e o teste dos quatro |
| `ensino_apresentado` ganhando `requer` | o teste da descida |
| `ensino_apresentado` ganhando `conceito` | os treze tópicos |
| `requer` com id fora do inventário | o teste do vocabulário |
| tópico sem `prerequisites` | o teste dos treze |
| carregador lendo `prerequisites` | os dois testes do descarte |
| `Dominio` ganhando o campo | o teste dos quinze campos |
| reteste devolvendo nada / reusando o visto | os dois do seletor |
| "já viu" deixando de ser por nó | o teste que liga o 4 ao 1 |
| o item `comparar_casos` do kc_11 trocando de formato | o teste da superfície que falta |
| `_superficie_nova` sempre verdadeira | o teste do formato |
| crença nova atravessando sem item | os dois do catálogo |
| crença que atravessa negando o mesmo nó | o teste dos treze de catorze |

As duas catracas do grupo 2 — **53 nomes de evento** e **o placar dos
quatro conceituais** — são as que obrigam a passar por aqui. Elas já
fizeram o trabalho: entre 08 e 09/11 **mudaram de lado três vezes**, e
cada mudança foi um commit declarando a arquitetura nova em vez de
descobri-la depois. Cair ali é a especificação acontecendo, não defeito.

E a terceira queda consertou o scanner em vez de abrir mão dele. Quando
os quatro eventos passaram a sair de uma FÁBRICA — `_por_conceito`, que
recebe o nome do evento por parâmetro —, a varredura passou a ver 49 em
vez de 53. A correção foi ensinar o scanner a reconhecer fábrica: a única
coisa que aquele teste tem para oferecer é exaustividade.

## Onde estão os três mecanismos

| mecanismo | estado |
| --- | --- |
| **1. eventos conceituais** | **completo** — os quatro, com 121 testes (40 da declaração e da assinatura, 26 do apresentado, 55 dos três de percurso) |
| **2. identidade de nó qualificada** | **completo** — nos quatro eventos, e o guarda do 409 passou a ser `(código, tópico)`, com 7 testes |
| **3. reconstrução individual por logs** | **completo** — `mvp/historico.py` e `scripts/percurso.py`, com 24 testes |

Nenhum dos dois últimos criou evento, então a catraca dos 53 continuou
valendo sem mexer.

### O guarda da identidade

`app.py` recusava pelo **código sozinho**, e o log é um arquivo. Num log
único — que é o que um histórico individual quer — o participante seria
recusado ao entrar no segundo tópico: o guarda que protege a identidade
era o mesmo que impedia o histórico.

Agora o par: **P07 abre o kc_02 e depois o kc_07; não abre o kc_02 duas
vezes.** A razão original está inteira, porque o que ela protege é a
sessão, não a pessoa.

**E a mudança criou um risco novo, que foi tratado.** O tópico está
**só** no `unidade_iniciada`, e `le_tolerante` pula linha ilegível de
propósito. Se justamente essa linha sair pela metade — o caso que o
`log.py` documenta, o processo morrendo no meio de uma escrita —, não há
como saber de que tópico era. Então o guarda procura o código no texto
cru das linhas quebradas e recusa se o achar. Uma linha quebrada de
**outro** participante continua não impedindo nada.

O que fica indetectável está dito: corrupção que apague o código inteiro
da linha. Não há como achar o que não está escrito, e travar toda sessão
nova porque o arquivo tem um defeito trocaria um risco de pesquisa por
uma coleta parada.

### A leitura do percurso

`mvp/historico.py` — **leitura, nada mais.** Nenhuma função abre arquivo
para escrita, e há teste conferindo que o arquivo não muda. E não é
cadeado: `sem_oportunidade` devolve lista, nunca veredito, e de propósito
não existe campo `pode_entrar` — seria o cadeado entrando pela porta de
trás.

A resposta à pergunta original, de uma execução real:

```text
percurso de P20, entrando em kc_06 (Passagem por referência)
  tópicos antes: kc_02

  com oportunidade registrada (1)
    sizeof                     1 itens  disponivel   em kc_02:B2

  este tópico vai cobrar, sem oportunidade registrada (3)
    funcao_com_parametro      23 itens  nao_introduzido
    ponteiro_de_ponteiro       1 itens  so_avaliado
    scanf                      1 itens  nao_introduzido
```

**E o relatório declara o que ele não vê.** A varredura de construto
cobre **7 dos 14** conceitos do inventário; `derreferencia`, `endereco`,
`operador_endereco`, `ponteiro`, `tipo_do_ponteiro`, `compilacao` e
`atribuicao_entre_tipos` não têm padrão nenhum. Para eles a lista não diz
nada — nem que o tópico cobra, nem que não. Dizer menos do que se sabe é
tolerável; calar que se está dizendo menos, não.

O limite apareceu por um teste meu que esperava `derreferencia` na lista
do kc_11 e caiu.

### Duas sabotagens que acharam defeito, e não só confirmaram

**O mapa de construtos mudou de casa.** `CONSTRUTOS` morava em
`scripts/revisa_material.py` e veio para `mvp/conceitos.py`: deixou de
ser conhecimento de script quando a verificação de entrada passou a
precisar dele. Duas listas divergiriam.

**E o teste que separava apresentado de confirmado não separava nada.**
Com um único participante no arquivo — o que acerta tudo —, todo conceito
apresentado também era confirmado, e os dois conjuntos eram **iguais**:
trocar `confirmados()` por `apresentados()` passava em todos os testes.
Quem achou foi a sabotagem. O conserto foi pôr no arquivo um participante
que declara lacuna: ele tem as cinco oportunidades, é diagnosticado,
revisita na construção e **não confirma nenhuma** — e é ele que torna a
distinção testável.

## O que esta especificação não resolve

- **Se o código do participante deve mesmo ser a identidade.** Ele é
  pseudônimo (P01…P40) e já serve à anonimização. Mas é digitado na
  URL, e nada impede duas pessoas usando o mesmo: o guarda pega
  repetição no log, não impostura.
- **`app.sessoes` continua indexado pelo código sozinho.** Dois tópicos
  no mesmo processo se sobrescreveriam ali. Hoje não acontece porque um
  processo serve um tópico — `carrega()` roda no import, e trocar de
  tópico é reiniciar —, e está pinado em `mvp/test_arquitetura.py`.
- **A verificação de entrada não está na tela.** É de terminal, porque
  quem escolhe o tópico hoje é quem sobe o servidor. Quando o estudante
  escolher, vira rota; `mvp/historico.py` serve as duas.
- **Quanto da dívida de `funcao_com_parametro` some** com percurso
  garantido. São 63 itens, todos a jusante do kc_02 no grafo declarado.
- **O custo da travessia para o piloto.** Um participante que faz vários
  tópicos gera vários `unidade_iniciada` no mesmo código, e o painel e o
  exportador presumem uma unidade por sessão.
