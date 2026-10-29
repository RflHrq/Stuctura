# MVP — treino até domínio

Implementa o laço do documento de 01/10/2026: **identifica → refuta →
treina → confirma**. Um nó só vira premissa correta depois de uma sequência
de acertos no treino, nunca depois de um acerto isolado.

Conteúdo: **kc_00, declaração de variáveis** — 5 premissas, 5 concepções
errôneas, 20 atividades e a analogia do quarto de hotel.

As atividades vêm em **dois bancos**, e a diferença importa:

| Banco | Quantas | Quando aparece |
| --- | --- | --- |
| diagnóstico | 10 — uma teórica e uma de código por nó | antes de qualquer refutação; o par sustenta a checagem de vacilo |
| treino | 10 — duas por nó, formatos diferentes | só depois da refutação, para fechar a sequência |

```bash
python -m pytest mvp/ -q     # 219 testes
python -m mvp.app            # http://127.0.0.1:8010  quem responde
python -m mvp.painel         # http://127.0.0.1:8011  quem observa
```

## O laço

| Passo | O que acontece | Onde |
| --- | --- | --- |
| **Pergunta** | camada 1 responde, tranca, e a camada 2 pergunta por quê | `motor._responde_diagnostico`, `motor.razoes_de` |
| **Classifica** | resposta × razão × confiança nos cinco estados, e a crença vai para o nó que ela nega | `motor.classifica`, `motor._resolve_diagnostico` |
| **Valida** | a analogia de resgate daquele nó, antes de qualquer refutação | `motor._inicia_validacao` |
| **Refuta** | percurso pelas premissas que sustentam o nó negado, montado do grafo | `motor._plano` |
| **Treina** | itens no mesmo nó, formato diferente a cada tentativa, até a sequência fechar | `motor._proximo_treino` |
| **Confirma** | o nó vira verde no mapa, e só então | `training_streak_completed` |

Errar chutando é lacuna, não crença: o sistema não refuta o que a pessoa não
pensa.

## A frase do começo e a do fim

A mesma pergunta duas vezes — antes da unidade e no fim —, e **as duas
lado a lado** no mapa. É a resposta direta ao "não estou sentindo
melhora": a mudança fica visível para a própria pessoa, nas palavras dela.

```
ANTES   acho que so reserva o nome, o espaco vem depois quando da o valor
AGORA   int x; ja reserva o espaco na hora; o que falta e o valor, nao o espaco
```

Três decisões:

**A pergunta vem do domínio** (`teachback:` no YAML do tópico), pelo mesmo
motivo que as razões vêm do grafo: o motor não escreve conteúdo. Trocar de
tópico troca a pergunta sem tocar no código.

**No fim, a frase de antes NÃO aparece.** Escrever olhando a própria frase
antiga é copiá-la ou corrigi-la, não reformulá-la. As duas só se encontram
depois, no mapa.

**O sistema não corrige e não classifica.** Nada no log diz se a frase está
certa — nem `correta`, nem `estado`. Quem classifica é o pesquisador,
depois, com codebook. Frase em branco é aceita e registrada como tal: isso
também é dado.

**Portão G.** Texto livre escrito por participante é **dado pessoal**. A
tela diz, antes de a pessoa escrever:

> O que você escrever fica guardado com o seu código de participante, sem
> nome. Ninguém corrige esta frase.

## "Não sei", opção de verdade

Nas **três** camadas. Obrigar a escolher **fabrica chute**: o sistema
criaria o falso positivo que depois tenta detectar. Com a opção
disponível, a lacuna vira dado **observado** — `"declarada": "camada2"` no
log — em vez de inferido de confiança baixa.

Dizer "não sei" numa camada **encerra o episódio**: quem não respondeu não
tem o que justificar, e quem não sabe explicar não tem convicção a
declarar. Perguntar assim mesmo seria teatro.

No treino, "não sei" zera a sequência como um erro zeraria — a sequência
mede premissa de pé, e quem não sabe não a tem de pé.

E o retorno é diferente de errar:

> **Você disse que não sabe.** Isso é informação, não erro: aqui não há
> nada para corrigir, há algo para construir.

## A sessão volta depois de uma queda

O estado vive em memória, e a memória morre com o processo. Numa coleta de
10 a 15 pessoas, **perder uma é perder 7%** — e ela não volta para repetir.

Agora o log guarda **duas coisas diferentes** no mesmo arquivo:

| Linha | O que é | Quem lê |
| --- | --- | --- |
| `entrada_recebida` | o que a pessoa fez, uma por chamada ao motor | a reexecução |
| os eventos | o que aquilo significou | a análise |

`log.reconstroi` reexecuta **só as entradas**, do começo, no motor puro. Não
lê evento nenhum — e por isso não pode divergir das regras: é o mesmo
código que rodou na primeira vez. A alternativa, projetar o estado a partir
de `no_confirmado`, `crenca_detectada` e companhia, seria uma segunda
implementação das regras, livre para discordar da primeira sem ninguém
perceber.

A semente da reexecução é o **código da sessão**, que já era a semente da
ordem das alternativas. Por isso volta também a tela: as mesmas razões, na
mesma ordem em que a pessoa as estava lendo.

Uma resposta que chega sem estado na memória é retomada assim, e a retomada
**vira linha no log** (`sessao_retomada`): uma sessão que teve queda no
meio não é igual às outras, e a análise precisa ver isso sem perguntar a
ninguém.

**Portão M.** Dois casos em que reconstruir seria mentir, e os dois
estouram em vez de devolver estado:

- **log sem entradas** — gravado antes desta tarefa. Reexecutá-lo devolveria
  a tela de abertura: uma sessão em branco com cara de sessão válida.
- **log de outro tópico** — as entradas são posições de alternativas;
  aplicadas a outro banco elas apontam para outras opções, e o estado sai
  plausível e errado.

O que **não** está resolvido: recarregar a página começa uma sessão nova,
porque o navegador não guarda o código da sessão. A queda que esta tarefa
cobre é a do servidor, com a página aberta.

**O preço, declarado:** o texto do teach-back aparece duas vezes na mesma
sessão — uma como entrada, outra como evento. Apagar um participante
continua sendo apagar as linhas com o código dele.

## O painel do pesquisador

Processo **separado**, em `127.0.0.1:8011`, e só leitura. Você acompanha
quem está respondendo sem interromper quem está pensando em voz alta.

A garantia não é cuidado, é **ausência de caminho**: `painel.py` não
importa `mvp.app`, não conhece o dicionário de sessões e não escreve em
lugar nenhum. Tudo o que ele mostra saiu de `mvp/dados/eventos.jsonl`.
Tem teste lendo a árvore sintática do arquivo — a única garantia que não
depende de eu lembrar.

Três razões, em ordem de peso: o painel não pode derrubar a sessão de um
participante; o log é append-only, então ler é seguro por construção; e
assim ele funciona **depois** de um travamento, que é quando mais importa.

O efeito colateral é a melhor parte: se o painel só lê o log, o log tem de
bastar. **O painel é a prova de que basta.**

### A tabela de episódios é o dado do TCC

Uma linha por atividade respondida, com as três camadas lado a lado:

```
#  FASE   NÓ  ITEM     RESPOSTA  RAZÃO                       CONFIANÇA      ESTADO   MS R/Z/C
1  diag.  B1  teorica  ✗ errada  ✗ no_value_no_memory → B2   tenho certeza  crença   17972 / 478 / 17082
```

A seta `→ B2` é o caso cruzado (CS-2): a pergunta era de B1, a ideia que a
pessoa usou é uma afirmação sobre B2, e é lá que ela ficou registrada. É o
achado mais difícil de enxergar à mão, e some se não for escrito.

Os três tempos separados respondem à pergunta que o tempo total não
responde: se a pessoa demorou a **responder** ou a **justificar**.

### Portão G: a lista não mostra texto livre

As frases do teach-back aparecem **só na tela de uma sessão**, nunca na
lista. Uma tela com o que quarenta pessoas escreveram não serve a nada que
este estudo precise, e existir já é risco. Tem teste.

A identificação é só o código da sessão, e o painel atende em `127.0.0.1`
— não há motivo para ele atender à rede.

### Portão S: o código da sessão nunca vira caminho

O painel abre **um** arquivo, decidido no servidor. O que vem do cliente é
valor de filtro, nunca pedaço de caminho. O teste prova a propriedade
direta: para qualquer código hostil, nenhuma leitura escolheu o arquivo a
partir do que o cliente mandou.

### Uma sessão que não volta aparece dizendo por quê

Sessões gravadas antes da T10 não são reexecutáveis. Elas continuam na
lista, marcadas, e abrir mostra o motivo — esconder seria esconder dado.

### A última linha pode estar pela metade

O processo morre no meio de uma escrita e o arquivo termina truncado. A
última linha é descartada; qualquer outra linha quebrada **estoura**.
Pular uma do meio em silêncio significaria reexecutar a sessão sem uma das
respostas, e o estado sairia plausível e errado.

## A força da premissa escolhe o próximo item

A unidade não é uma fila fixa. O próximo item é o da premissa **mais fraca
que ainda não está de pé** — o "trabalhar onde está fraco" sem inventar
número. `motor.forca(EstadoNo)` é função pura, e a banca confere linha a
linha sem rodar nada:

| Evidência | Efeito |
| --- | --- |
| certa pela razão certa, com confiança, numa superfície nova | **+2** |
| sobreviveu à troca de superfície | é a segunda superfície, já contada |
| acerto pela razão errada | **0** — não conta |
| erro pela razão certa (vacilo) | **0** — não enfraquece |
| acerto no treino | **+1** |
| precisou de reexplicação | **−1** |
| tropeçou no treino | **−1** |
| veio de refutação de crença | **−2**, frágil até o reteste |

**Os dois zeros são decisões, não omissões.** Tratar o falso positivo como
erro puniria esta premissa pelo que aconteceu com **outra** — a crença
escolhida fala de outro nó. E quem erra enunciando a premissa direito
escorregou: escorregão não é premissa bamba.

**Empate vale a ordem do grafo.** Não pode virar sorteio — o motor é puro —
e premissa que vem antes sustenta as de depois.

**O falso positivo vence a força** (T6): a pergunta em aberto é sobre
aquela premissa, e adiar não a responde.

### O que mudou na tela

A unidade varre o grafo em largura em vez de esgotar um nó de cada vez:

```
antes   B1/teo  B1/cod  B2/teo  B2/cod  B3/teo  B3/cod  …
agora   B1/teo  B2/teo  B3/teo  B4/teo  I1/teo  B1/cod  …
```

Duas perguntas seguidas sobre a mesma premissa medem o que ficou do item
anterior, não a premissa. Dentro do nó a ordem não mudou: a teórica antes
da de código, que é o par das duas superfícies do CS-5.

### "Confirmada · força −2" não é contradição

São duas medidas, separadas de propósito. `CONFIRMADO` é mecanismo de
**produto**: decide o que o mapa mostra ao aluno, e o streak do treino
basta para chegar lá. A força é medida de **pesquisa**, e nela uma
premissa reconstruída depois de uma crença vale menos do que uma que nunca
caiu. Misturar as duas faria o treino virar uma segunda forma de medir o
reteste.

### O limite, declarado

O documento diz que a unidade termina quando a premissa mais fraca está de
pé. **Com duas atividades de diagnóstico por nó nem sempre dá para chegar
lá**: uma premissa que ficou frágil nas duas não tem terceira superfície
para oferecer, e a unidade encerra com ela ainda frágil. Então o
encerramento **registra** onde cada uma parou:

```json
{"tipo": "unidade_encerrada", "forcas": {"B1": 2, "B2": -5, ...},
 "mais_fraca": "B2", "mais_fraca_de_pe": false}
```

O critério vira dado conferível em vez de afirmação. Fechar a lacuna exige
uma terceira atividade por nó — a mesma falta que o treino já tem.

## O reteste do fim da sessão

O critério de sucesso tem **três** condições, não uma: a razão muda da
razão-crença para a razão-correta **sem queda de confiança**; isso
**sobrevive à troca de superfície**; e **não volta** no reteste do fim da
sessão. As duas primeiras acontecem no diagnóstico e no treino. Esta é a
terceira.

No fim, antes da frase de fecho, cada crença refutada volta **uma vez**,
num item que a pessoa não viu, com as três camadas — porque o critério
fala da razão e da confiança, não só do acerto.

**O reteste observa, não intervém.** Escolher a crença de novo não dispara
outra refutação, não mexe no estado do nó e não adia o fim da unidade.
Uma medida que corrige o que está medindo deixa de ser medida, e refutar
outra vez no fim nunca terminaria. Tem teste para cada metade disso.

**Para quem responde, é uma atividade como outra qualquer.** Avisar que
aquilo é a medida mudaria a medida.

```
belief_retested  {"crenca": "declaration_zeroes", "no": "B3",
                  "voltou": false, "razao_correta": true,
                  "confianca": "tenho certeza",
                  "superficie_nova": false}
```

### O banco não alimenta o mecanismo

Medido em 12 percursos, com erro em cada nó e com o treino acertado e
errado:

| | |
| --- | --- |
| crenças refutadas | 17 |
| retestes que aconteceram | **7** |
| desses, em superfície nova | **3** |

**Quem erra no treino nunca é retestado** — e é justamente quem mais
precisa ser. A causa é o banco, não o motor: cada crença aparece em ~4
itens, e o item que a detectou mais as tentativas de treino consomem
quase todos.

O mecanismo não disfarça a falta. Quando não há item por ver, sai
`reteste_sem_item` com o motivo, e o encerramento conta `refutadas` e
`retestadas` separadas. O painel mostra a diferença em destaque: um
reteste que não aconteceu é uma condição do critério que ficou **sem
medida** naquela sessão.

Quando há item mas não há formato novo, o reteste acontece e
`superficie_nova` sai falso — reteste no mesmo molde é evidência mais
fraca, e isso fica dito em vez de escondido.

**Duas saídas, e a escolha é de conteúdo:** mais itens por crença, ou
reservar um item no momento da detecção — o que tiraria do treino um
candidato e empurraria mais nós para `em_aberto`.

### O limite do ciclo 1

O critério diz "com **outra unidade** no meio". Só existe uma unidade
pronta, então o que fica no meio são as outras premissas desta. É menos
separação do que o critério pede. O reteste de verdade acontece na
abertura da KC seguinte, pelo grafo externo — e isso é o próximo ciclo.

## Operar: copiar e apagar

Dois procedimentos que o PRD exige e que até o ciclo 2 só existiam como
lembrete. Script que nunca foi executado é documentação, não
procedimento — os dois têm teste que roda o script de verdade.

### Depois de cada sessão, a cópia

```bash
bash scripts/copia.sh /caminho/da/segunda/midia
```

Datada, não sobrescreve a de ontem, e **confere** byte a byte depois de
copiar. O log de uma coleta é irreproduzível: a pessoa não volta para
refazer, e a perda tolerável é zero.

A pasta de destino precisa estar em **outra mídia** — cópia no mesmo
disco não protege contra o disco. E cópia conferida ainda não é backup
restaurado: o ensaio de restauração é da revisão final.

**O caminho vai no formato do shell:** `/d/coleta`, e não `D:\coleta`.
Chamado de fora de um shell, um caminho com barra invertida chega literal
e vira uma **pasta com esse nome** dentro do diretório atual — o script
dizia "copiado e conferido" e o backup estava em outro lugar. Hoje ele
recusa três casos: caminho em formato Windows, pasta de destino cuja mãe
não existe (mídia desmontada) e destino dentro do repositório.

### O pedido de exclusão de um participante

```bash
bash scripts/participante.sh ver     P07
bash scripts/participante.sh apagar  P07
```

O PRD declara o direito; declarar um direito sem ter como exercê-lo é
problema de conformidade, e o texto vai ao comitê de ética.

`ver` mostra o que seria apagado, inclusive quantas linhas têm texto
livre. `apagar` pede o código **de novo** antes de agir e guarda uma cópia
do arquivo anterior — irreversível merece rede. Quem confere o pedido
apaga essa cópia depois.

Três cuidados, cada um com teste:

- o código é comparado **campo a campo**, nunca como expressão regular ou
  pedaço de texto: apagar `P1` não pode levar `P10` junto;
- linha ilegível não é de ninguém e **fica** — apagar o que não se
  consegue ler seria apagar o que não se sabe;
- confirmação errada não apaga nada.

## Os cinco estados, e em que nó cada um fica

`motor.classifica(certa, razao, confianca)` é função pura — a banca confere
linha a linha sem rodar nada:

| Resposta | Razão | Confiança | Estado | O que o motor faz |
| --- | --- | --- | --- | --- |
| certa | certa | tenho certeza | **confirmada** | conta uma superfície |
| certa | certa | acho que sei / chutei | **frágil** | não conta superfície |
| certa | **errada** | qualquer | **falso positivo** | não confirma; conta na crença |
| errada | **certa** | qualquer | **falso negativo** | não refuta; registra o vacilo |
| errada | errada | certeza / acho que sei | **crença ativa** | valida, refuta, treina |
| errada | errada | chutei | **lacuna** | registra |

**CS-5, duas superfícies.** Um acerto só deixa a premissa `fragil`: pode
ser reconhecimento do molde da pergunta, não da ideia. Confirmar exige dois
formatos diferentes, pela razão certa, com certeza — e é para isso que o
par teórica + código existe.

**O falso positivo não fica parado.** A pessoa ouve que a resposta está
certa *e* que a explicação leva a outro lugar — com as duas frases lado a
lado, vindas do domínio:

> **Você explicou por:** "Se eu não dei valor, a variável ainda não existe
> na memória."
> **E isso contradiz:** "Quando você escreve `int x;`, a caixa de x já
> existe — só o que tem dentro ainda não está definido."

Depois o sistema traz **outra superfície do mesmo nó**: a pergunta em
aberto é sobre aquela premissa, e seguir adiante não a responde. Na
**segunda** vez com a mesma crença, isso vira refutação — no nó que a
crença nega. Uma vez pode ser acidente de alternativa; duas, na mesma
ideia, é a ideia.

A conta é **por crença**, não por pessoa: explicar mal duas perguntas por
ideias diferentes não é sustentar nenhuma delas. E um nó já confirmado por
duas superfícies não é derrubado por uma explicação ruim noutra pergunta.

**CS-2, a crença vai para o nó que ELA nega.** Errar um item de B1
explicando pela crença de que sem valor não há memória é informação sobre
**B2**: é B2 que fica vermelho, é B2 que a refutação percorre, e B1 segue
em aberto. O evento guarda os dois: `{"no": "B2", "veio_do_item_de": "B1"}`.

**A regra dos dois erros foi aposentada.** Ela existia porque não havia
como saber *por que* a pessoa errou — o segundo erro era um proxy de "não
foi escorregão". A camada 2 substituiu o proxy pela coisa: quem erra pelo
motivo certo escorregou (CS-3), e quem erra pelo motivo errado já disse
qual é a crença.

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
| `B2 ✓` cheio | premissa confirmada, em duas formas de pergunta |
| `B2 ✓` tracejado | confirmada depois de refutação e treino |
| `B2 ✓?` | de pé numa forma só, ou sem convicção — falta superfície |
| `B2 !` | acertou por outro motivo: não confirma |
| `B2 ✗` | crença detectada, ainda não trabalhada |
| `B2 ?` | disse que não sabe |
| `B2 1/2` | em treino: acertos seguidos até confirmar |
| `B2 —` | ficou em aberto |

**Símbolo antes de cor.** Cada estado tem símbolo, traço (cheio, tracejado
ou pontilhado) e **nome por extenso** no mapa. Daltonismo e impressão em
preto e branco não podem apagar a diferença entre "de pé" e "crença ativa".

**O caso cruzado ganha frase.** Um nó pode ficar vermelho sem a pessoa ter
respondido nada sobre ele — porque ela explicou *outra* pergunta por uma
crença que nega este. Sem texto, isso parece bug. Com texto:

> A ideia que você usou na pergunta de B1 é uma afirmação sobre B2 — é lá
> que ela ficou registrada.

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
│   ├── beliefs_kc00.yaml      5 crenças com procedência e fonte
│   └── activities_kc00.yaml   20 atividades, exemplos e analogias de resgate
├── dominio.py                 carga e validação (falha na carga, nunca em sessão)
├── motor.py                   o laço, puro: (estado, resposta) → (estado, tela, eventos)
├── log.py                     append-only; grava as entradas e reexecuta a sessão
├── app.py                     três rotas
├── painel.py                  o painel do pesquisador, só leitura, processo à parte
├── web/                       a interface, que não decide nada
├── web/painel.html            o painel, numa página só
├── web/figuras.js             a analogia desenhada, uma por premissa
├── test_motor.py              o laço, 28 testes
├── test_dominio.py            a carga e as invariantes, 14 testes
├── test_razao.py              as camadas 2 e 3, 18 testes
├── test_classificacao.py      os cinco estados, a projeção, CS-4 e o falso positivo, 37 testes
├── test_teachback.py          a frase do começo e a do fim, 9 testes
├── test_reconstrucao.py       a sessão de volta pelo log, 15 testes
└── test_painel.py             o painel que não pode atrapalhar, 16 testes
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

## A camada da razão

Depois de responder, a resposta **tranca** e vem a segunda pergunta: *por
quê*. Trancar não é detalhe de interface. As razões erradas são enunciados
de crenças — lê-las antes de responder entrega a pista e muda a resposta de
quem ia acertar. Com a camada 1 fechada, o par resposta-razão é
independente, que é o que a classificação pressupõe.

**As razões vêm do grafo, nunca de um banco de razões:**

| Razão | De onde sai |
| --- | --- |
| a certa | o enunciado do nó que o item mira |
| as erradas | o que afirmam as crenças apontadas pelas alternativas |

Se houvesse um banco de razões escritas à mão, a razão e a premissa
poderiam divergir, e o diagnóstico passaria a medir a redação do item.

**Uma razão pode falar de outro nó.** O item `ciu_kc00_002` mira B1 e
oferece, entre as razões, a crença de que sem valor não há memória — que
nega **B2**. Explicar por ela é informação sobre B2, e o evento
`camada2_respondida` grava isso em `fala_do_no`. O que o sistema **faz**
com essa informação é a tarefa seguinte (T4); por ora ele registra.

A ordem das razões é embaralhada por uma permutação derivada da sessão:
`ordem_das_razoes(semente, atividade, n)`. O motor continua puro — não
sorteia — e recarregar a página não reembaralha as alternativas debaixo de
quem está lendo.

**Item sem crença nas alternativas pula a camada 2**, registrando
`razao_pulada`: com uma alternativa só não há escolha a fazer.

## A camada da confiança

Tela própria, depois das duas escolhas, **em toda atividade** — inclusive
no treino. Duas decisões:

**Própria, e não no pé da tela da razão.** A pergunta é sobre as duas
escolhas juntas; declarar confiança antes de ver o par formado mede outra
coisa. Custa um passo a mais por item, e compra independência entre as
camadas — que é o que sustenta a tabela de classificação.

**Em toda atividade, não só no diagnóstico.** O critério de sucesso diz
que a razão muda *sem queda de confiança*. Queda exige **duas** medidas, e
a segunda acontece depois da refutação, no treino. Antes a confiança só
era pedida no diagnóstico, e esse número não existia.

O treino não pergunta o porquê, só a confiança: a razão é do diagnóstico,
onde ela separa chute, vacilo e crença. No treino o nó já foi refutado, e
o que está em jogo é se a premissa se sustenta noutra superfície.

Cada camada grava o **próprio tempo**:

```
camada1_respondida  {correta: true,  ms: 301}
camada2_respondida  {razao_correta: true, fala_do_no: "B1", ms: 703}
camada3_respondida  {confianca: "tenho certeza", ms: 6582}
```

Sem isso não dá para saber se a pessoa demorou a responder ou a
justificar — e é a segunda que interessa.

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
3. **Mais um tópico**, para o reteste da pesquisa acontecer longe do treino.
