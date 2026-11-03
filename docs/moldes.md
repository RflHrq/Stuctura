# Moldes paramétricos, com oráculo de compilador

> Desenho aprovado em 03/11/2026 e **implementado** no mesmo dia, no ramo
> `moldes` (plano em [plano-moldes.md](plano-moldes.md), doze tarefas). O
> primeiro molde de verdade está em `mvp/dominio/moldes_kc07.yaml` e
> espera a revisão humana: nenhum item de molde entrou no domínio ainda.
> Os números da sonda que mediu a viabilidade continuam abaixo.

## O problema

São 556 itens em 79 nós. Parece muito; por nó são **sete**:

```
3 de diagnóstico   (um por degrau da escada)
3 de treino        (um por degrau, formatos diferentes)
1 de entrada       (o mais fácil, depois de um "não sei")
```

Três consequências, e nenhuma é de gosto:

**O treino esgota.** Ele exige dois acertos seguidos em formatos
diferentes, com teto de quatro tentativas. Quem erra duas vezes acaba com
o banco do nó e a premissa termina *em aberto* — não por falta de
capacidade de quem responde, por falta de item. Isso tem requisito
próprio (RF36) e já apareceu medido no pior caso.

**Rodar duas vezes é ver as mesmas perguntas.** Todo item é texto fixo:
`int a[5]` é `int a[5]` sempre, com o mesmo nome, o mesmo tamanho e as
mesmas três alternativas.

**Falta o eixo da superfície.** Hoje "duas superfícies diferentes" quer
dizer dois *formatos*. São duas perguntas distintas, que a pessoa pode ter
decorado uma a uma. Não existe como perguntar *a mesma coisa com a
roupa trocada* — e é isso que separa quem generalizou de quem memorizou.

Encher o banco escrevendo mais itens não resolve o terceiro, e o primeiro
só resolve ao preço da sua revisão, item por item: hoje há 51 candidatos
do gerador parados esperando revisão humana.

## O molde

Um arquivo novo por tópico — `mvp/dominio/moldes_kc07.yaml` —, ao lado dos
quatro que já existem. **Ele não entra em sessão**: o gerador o expande em
itens concretos, que vão para `activities_kc07.yaml` como qualquer outro.
O motor não aprende o que é um molde, e a reexecução da sessão continua
idêntica. O item expandido carrega a procedência dele, e é só isso que
chega à sessão — ver *O que fica medível*.

```yaml
mol_kc07_B1_reconhecer:
  node: B1                      # `node`, nunca `no`: em YAML, `no` é falso
  tipo: teorica
  formato: reconhecer_conceito
  nivel: 1
  uso: treino

  parametros:
    tipo: [int, char, double, long, float]
    nome: [a, v, dados, lista, buf]
    n:    [3, 4, 5, 6, 7, 8]

  enunciado: "{tipo} {nome}[{n}] cria o quê?"
  gabarito:  "{extenso} caixas de {tipo}, grudadas"
  distratores:
    - texto: "Uma caixa só, com as {extenso} dentro dela"
      crenca: string_literal_is_array
    - texto: "Um ponteiro para {extenso} {tipo}"
      crenca: array_is_pointer

  oraculo: |
    #include <stdio.h>
    int main(void) {
        {tipo} {nome}[{n}];
        printf("%zu %td\n", sizeof {nome} / sizeof {nome}[0],
               &{nome}[1] - &{nome}[0]);
        return 0;
    }
  espera: "{n} 1"

  revisado_por: ""
  revisado_sha: ""              # a assinatura do conteúdo que foi lido
```

**O gabarito é regra, não texto.** É o que permite uma revisão valer por
muitas: não se leem 150 respostas, lê-se a regra que as produz.

**Cada distrator continua amarrado à crença por id**, da lista fechada do
catálogo. O molde não pode inventar concepção errônea — é a mesma trava
que o gerador de hoje tem.

**O `revisado_por` sai do item e vai para o molde.** É a mudança de objeto
da revisão, e é ela que torna a coisa viável. Os itens expandidos carregam
`do_molde: mol_kc07_B1_reconhecer` para a procedência não se perder.

**E o nome vem acompanhado de assinatura.** `revisado_sha` guarda a
impressão digital do conteúdo que foi lido, e a folha de revisão imprime
a linha pronta para colar. Sem isso, o nome sobrevive a qualquer edição
do molde — e como esta mesma spec prescreve **editar** (estreitar o
domínio de um parâmetro) como conserto de molde reprovado, bastava
corrigir e reexpandir para sair variação inédita estampada com o nome de
quem nunca a leu. Com a assinatura, a carga recusa: *"o molde mudou
depois da revisão"*.

**Em `prever_saida`, o oráculo deixa de conferir e vira gabarito**: a
resposta certa é literalmente o que o programa imprime, e a máquina a
calcula.

## A família de formatos

> Segunda fatia, aprovada e **implementada** em 03/11/2026 (plano em
> [plano-familia.md](plano-familia.md), dez tarefas). A primeira família
> está assinada, e os seis itens dela — dois por formato — estão no
> domínio do kc_07.

O molde acima multiplica o eixo do **conteúdo**: `int a[3]`, `double
lista[8]`, a mesma pergunta com a roupa trocada. Ele não toca no eixo do
**formato**, e o sistema precisa dos dois.

O número que mostrou isso veio da primeira sessão de verdade com um
molde aprovado. O banco de treino do `B1` tinha três itens, um por
formato; depois do molde ficou com nove — e **sete deles do mesmo
formato**, `reconhecer_conceito`, contra um `prever_saida` e um
`comparar_casos`. O motor prefere um formato diferente a cada tentativa
de treino, e confirmar exige **duas superfícies diferentes**, que hoje
quer dizer dois formatos. Multiplicar só o conteúdo deixa essa regra sem
com que morder.

| eixo | o que troca | o que separa |
| --- | --- | --- |
| conteúdo | `int a[3]` → `double lista[8]` | generalizou, ou decorou aquele exemplo |
| formato | "o que existe?" → "qual linha não compila?" | entendeu a ideia, ou reconhece o molde da pergunta |

### Uma afirmação, várias redações

O molde deixa de ser uma pergunta com buracos e passa a ser uma
**afirmação** perguntada de vários jeitos. Compartilhado, porque é a
mesma ideia: o nó, os parâmetros, **as crenças** e o oráculo. Por
formato: a redação, às vezes o código, e às vezes o programa que confere.

```yaml
mol_kc07_B1:
  node: B1
  nivel: 1
  uso: treino
  parametros: { tipo: [int, char, double], nome: [a, v, dados], n: [3, 5, 8] }

  # As crenças são da AFIRMAÇÃO, não da redação.
  crencas: [string_literal_is_array, array_is_pointer]

  oraculo: |                      # o oráculo da afirmação
    #include <stdio.h>
    int main(void) {
        {tipo} {nome}[{n}];
        printf("%zu %td\n", sizeof {nome} / sizeof {nome}[0],
               &{nome}[1] - &{nome}[0]);
        return 0;
    }
  espera: "{n} 1"

  formatos:
    reconhecer_conceito:
      tipo: teorica
      enunciado: "Depois de {tipo} {nome}[{n}]; e nada mais, o que existe na memória?"
      gabarito:  "São {extenso} caixas de {tipo}, grudadas"
      distratores:                                   # NA ORDEM das crenças
        - "Uma caixa só, com {extenso} valores guardados dentro dela"
        - "Um ponteiro, que depois aponta para {extenso} valores do tipo {tipo}"

    achar_o_erro:
      tipo: codigo
      codigo: |
        {tipo} {nome}[{n}];
        {tipo} *p = {nome};
        {nome} = p;
      enunciado: "Uma destas linhas não compila. Qual, e por quê?"
      gabarito:  "A terceira: o nome do array não recebe atribuição"
      distratores:
        - "A segunda: um ponteiro não recebe o nome de um array"
        - "Nenhuma: as três compilam"
      nao_compila: true           # o oráculo deste formato espera a RECUSA

    prever_saida:
      tipo: codigo
      codigo: |
        {tipo} {nome}[{n}];
        printf("%zu", sizeof {nome} / sizeof {nome}[0]);
      enunciado: "O que sai?"
      gabarito: do_oraculo        # a máquina calcula a resposta certa
      distratores:
        - "o tamanho de um ponteiro"
        - "1, porque {nome} é uma coisa só"
```

### As cinco regras da família

**Os distratores são posicionais contra `crencas`.** Não é economia de
digitação: é o que garante que todo formato carrega as mesmas ideias
erradas. Se cada formato escolhesse as suas, dois formatos do mesmo
molde mediriam coisas diferentes — e aí não são duas superfícies da
mesma afirmação, são duas perguntas.

**O oráculo é um só, sobrescrito quando o formato precisa.** Em
`achar_o_erro`, o que se prova é que o programa **não** compila, e o
sistema já sabe fazer isso: é o tipo `erro_de_compilacao` da tela de
evidência da descida, agora no gerador. `nao_compila: true` passa quando
o compilador recusa com diagnóstico, e **reprova quando compila** — um
"ache o erro" num programa que compila é um item sem erro. Nesse
formato o `espera` não existe: não há saída que esperar de um programa
que não vira executável, e declará-lo junto é erro de carga.

**`prever_saida` deixa de ser recusado**, e só aqui. `gabarito:
do_oraculo` faz a máquina **calcular** a resposta certa em vez de
conferi-la: é a promessa que esta spec sempre fez e que a primeira fatia
teve de barrar, porque fora da família `gabarito` e `espera` eram campos
independentes e ninguém provava que diziam a mesma coisa.

**A PRIMEIRA variação de cada formato usa os mesmos parâmetros.** Uma, e
não "as primeiras": com duas variações por formato, duas compartilhadas
seriam todas, e nada divergiria. Se `int a[3]` aparece como
`reconhecer_conceito` e como `achar_o_erro`, a única coisa que mudou
entre as duas foi a forma de perguntar — e aí acertar uma e errar a
outra é um sinal limpo de superfície, e não de conteúdo. Da segunda em
diante, cada formato segue a escolha gulosa de sempre, a partir do que
já foi usado naquele formato.

**A expansão se reparte entre os formatos.** `quantas` passa a ser o
total: seis viram duas por formato em três formatos. É isso que conserta
o sete-contra-um-contra-um do `B1` — **medido depois**: o banco de treino
dele ficou com 3 `reconhecer_conceito`, 3 `comparar_casos`, 2
`achar_o_erro` e 1 `prever_saida`, em quatro formatos em vez de três.

### O que isso não muda

**Uma revisão continua cobrindo a família inteira**, porque o que se
valida é a afirmação e as crenças, que são uma só. A folha cresce um
pouco: as três variações dos extremos num formato, mais uma de cada
outro formato. A assinatura é do arquivo todo, como já é.

**Molde sem `formatos:` continua valendo.** É uma família de um, e é o
que `mol_kc07_B1_treino_1` já é — ele está assinado e os seis itens dele
estão no domínio. Nada do que está no banco precisa ser reescrito.

**O id do item passa a dizer o formato**: `mol_kc07_B1__achar_o_erro_02`.
Sem isso, duas redações da mesma variação colidem no id.

### O que fica de fora desta fatia

Os formatos **autocompletar** (lacuna no código, com alternativas) e
**apontar a linha** cabem na tela que já existe e entram depois, como
conteúdo dentro desta mesma estrutura — não como obra nova. **Ordenar os
passos** e **marcar as caixas da memória** pedem tela nova e ficam para
depois disso. **Prever a saída digitando** fica de fora por decisão, e
não por custo: sem alternativas não há crença para apontar, e a camada 2
some justamente onde ela é a peça central do instrumento.

## O que o item expandido carrega

Dois campos novos em cada atividade gerada, e portanto em `Atividade`:

```yaml
- id: mol_kc07_B1__reconhecer_conceito_03    # o formato entra no id
  node: kc07:B1
  do_molde: mol_kc07_B1
  parametros: {tipo: double, nome: buf, n: 8}
  ...
```

O `do_molde` é o da FAMÍLIA, e não o da redação: duas redações da mesma
afirmação são duas superfícies dela, e é assim que a medida da
generalização as vê. O formato já está no próprio item, em `formato`.

O carregador aceita os dois como **opcionais** — item escrito à mão não
tem molde —, e cobra uma coisa quando eles aparecem: `do_molde` sem
`parametros`, ou o contrário, é recusado na carga. Meia procedência é
pior que nenhuma, porque parece procedência.

## Os portões

```
  modelo escreve o molde          scripts/gerar.py --molde --no B1
        │
        ├─ 1. EXPANSÃO   instancia as combinações dos parâmetros
        ├─ 2. ORÁCULO    compila e roda cada uma; compara com `espera`
        ├─ 3. CONTRATO   os itens passam pelo carregador de verdade,
        │                com as mesmas invariantes dos escritos à mão
        └─ 4. VARIEDADE  nenhuma variação igual a outra, nem a um item
                         que já exista no banco
        │
   a pessoa lê O MOLDE e três variações      revisado_por: ____
        │
   --aprovar  →  os itens entram em activities_kc07.yaml
```

### Três regras, e o motivo de cada uma

**O oráculo reprova o molde, não a variação.** Na sonda, um molde que
afirmava `sizeof a == n` falhou em 18 de 20 e passou nas duas de `char` —
onde a afirmação é verdadeira. A resposta certa não é guardar as duas:
descartar as variações ruins e ficar com as boas é como se esconde uma
generalização indevida. O banco ficaria cheio de itens corretos sobre
`char` com a afirmação falsa ainda escrita no molde, esperando a próxima
expansão. Conserta-se corrigindo a afirmação ou **estreitando o domínio do
parâmetro** (`tipo: [char]`) — e aí a restrição fica visível no arquivo.

**O oráculo é obrigatório, e tem de depender dos parâmetros.** Molde sem
programa que o confira é texto de modelo sem conferência nenhuma. E um
programa CONSTANTE é pior: roda o mesmo código em toda variação, dá seis
"passou", e fica com cara de conferido. Se a afirmação do item não puder
ser verificada por um programa, aquele item continua sendo escrito à
mão — a camada cobre o que a máquina sabe julgar e não finge cobrir o
resto.

**Dois portões que a revisão do ramo acrescentou**, porque deixavam item
errado chegar ao participante: nenhum item sai com **buraco por
preencher** (era o caso de `{extenso}` com `n` fora de 1..10, que
imprimia o literal na tela), e a alternativa certa não pode ser a
**única que começa em minúscula** — num molde essa pista se repete em
todas as variações.

**`prever_saida` não vale em molde de formato único.** A promessa desta
spec é que, nesse formato, o oráculo vira gabarito — e fora da família
`gabarito` e `espera` são campos independentes: o oráculo prova que o
programa imprime `espera`, e ninguém prova que a alternativa certa diz o
mesmo. A carga recusa, com o motivo. Dentro da família ele passa a
valer, com `gabarito: do_oraculo` (ver *A família de formatos*).

**As três variações da revisão humana são escolhidas, não sorteadas:** os
extremos do espaço de parâmetros — o menor e o maior `n`, o nome mais
curto e o mais longo —, que é onde a concordância do português quebra.

## A linha de comando

```bash
# o modelo escreve o molde
python scripts/gerar.py --topico kc_07 --no B1 --molde --degrau 1

# a folha que a pessoa lê para assinar
python scripts/gerar.py --topico kc_07 --molde mol_kc07_B1_reconhecer --revisar

# expande de novo um molde que já existe (depois de editar o YAML)
python scripts/gerar.py --topico kc_07 --molde mol_kc07_B1_reconhecer --expandir

# move para o domínio o que tiver revisado_por preenchido
python scripts/gerar.py --topico kc_07 --aprovar
```

Sem credencial da API, `--prompt` continua escrevendo o prompt num
arquivo: o esquema, os portões e a expansão funcionam igual, com o molde
colado à mão.

## A expansão

**Offline.** O motor nunca instancia molde em sessão. A reexecução da
sessão a partir do log é requisito implementado e testado (CS-6), e um
item montado em tempo de execução precisaria do sorteio gravado para ser
reconstruído. Expandir em sessão continua possível depois — o formato não
impede —, mas não antes da coleta.

**Seis variações por molde**, e não as 150 — e, numa família, seis é o
TOTAL, repartido entre os formatos: dois por formato em três formatos. A escolha é determinística e
gulosa, pela distância de Hamming entre os valores dos parâmetros: começa
pela combinação de índices mais baixos e, a cada passo, acrescenta a
combinação cuja distância mínima às já escolhidas é a maior — empate
resolvido pela ordem de escrita do YAML, para a expansão ser reprodutível.
Com dois ou três moldes por nó, o banco de treino sai de 3 itens para 12 a
18, e os arquivos continuam legíveis por humano.

## O que fica medível

O log ganha dois campos em `atividade_apresentada`:

```
do_molde:   mol_kc07_B1_reconhecer
parametros: {tipo: double, nome: buf, n: 8}
```

Com eles, três coisas hoje invisíveis saem do log sem mudar critério
nenhum:

| o que aconteceu | o que significa |
| --- | --- |
| acertou duas instâncias do mesmo molde, com parâmetros distintos | generalizou |
| acertou a primeira e errou a segunda | memorizou a primeira — e isso hoje conta como domínio |
| errou as duas, com parâmetros distintos | a crença é robusta; não é tropeço de item |

A última linha é o que hoje não dá para distinguir: errar duas vezes no
**mesmo** item pode ser o item, e não a ideia.

O mapa final ganha uma marca discreta na premissa — *de pé, e sustentou a
troca de superfície* —, e a tabela de exportação ganha as duas colunas.

## O que NÃO muda

**O critério de domínio.** `CONFIRMADO` continua exigindo acerto pela
razão certa, com confiança, em dois formatos. Exigir um critério que
ninguém calibrou, logo antes de medir, trocaria a definição do próprio
resultado da pesquisa — e com 10 a 15 participantes não há como calibrar
depois. Mede-se agora; exige-se quando houver número. Esta é uma decisão
tomada, não uma pendência.

**O motor, o log e a reexecução.** A camada é de geração. O que chega à
sessão é um item de YAML como todos os outros.

## Ambiente

O oráculo precisa de um compilador C. Nesta máquina:

```
gcc (MinGW-W64 x86_64-ucrt-posix-seh) 16.2.0   —   C:\Users\Public\gcc
```

**O caminho não pode ter espaço.** O `ld` do MinGW não resolve o próprio
prefixo quando há um, e a instalação padrão do winget caiu em
`C:\Users\Satya Pass\...`: nada linkava, com a mensagem
*"cannot find C:/Users/Satya"*. Reinstalado em `C:\Users\Public\gcc`,
funciona. Quem for rodar o gerador noutra máquina precisa saber disso.

Os programas são compilados e executados **em pasta temporária, com
caminhos relativos**, e o que o oráculo compara é a saída padrão com o
campo `espera`.

## O que a sonda mediu

Um molde, o do `B1` do kc_07, com 150 combinações possíveis:

| | passaram | tempo |
| --- | --- | --- |
| molde certo | 20 de 20 | 6,7 s (0,34 s por variação) |
| molde errado (`sizeof a == n`) | 2 de 20 | 7,1 s |

As duas que passaram no molde errado foram as de `char`. Os 20 itens
gerados pelo molde certo também passaram pelo carregador de verdade: 49
atividades viraram 69.

## Riscos e limites

**A máquina confere o C, não o português.** A própria sonda produziu *"um
ponteiro para quatro long"* e *"tres caixas"*. Nenhum compilador reclama
de concordância, plural ou acento. É por isso que a revisão humana não
desaparece: ela muda de objeto, do item para o molde, e lê os extremos.

**O oráculo não julga pedagogia.** Ele garante que a pergunta é
verdadeira, não que ela ensina, nem que o distrator é tentador. Isso
continua sendo julgamento humano.

**Um molde errado erra em todas as variações de uma vez.** É o preço do
multiplicador, e é exatamente contra isso que o oráculo existe — foi o
caso do `sizeof`, e a máquina pegou.

**Nenhum participante real passou por item gerado de molde.** O primeiro
molde foi assinado em 03/11/2026 e os seis itens dele estão no domínio
do kc_07 — conferidos numa sessão no navegador, com a procedência no
log —, mas quem respondeu fui eu.

## Próximas fatias, fora desta spec

1. **Caminhante com persona de crença**: o `scripts/caminhante.py` hoje
   tem três personas por regra. A versão nova recebe uma crença
   documentada e responde de forma consistente com ela, e a medida é a que
   o log já produz — a descida fecha, e em que degrau? Serve para
   **reprovar material**, nunca para aprovar: um modelo que sabe C não
   consegue não saber, e o que ele produz é o palpite dele sobre como
   alguém erraria. O que ele acha de incoerente é achado; o que ele
   consegue aprender não prova nada.
2. **Escolha adaptativa do próximo item**: pedir ao motor o item mais
   distante, no espaço de parâmetros, do que já foi apresentado. Mexe em
   `proximo_item`, e sem banco não tem o que escolher.

## Decisões tomadas

**Os moldes começam pelos nós dos dois tópicos da coleta** — kc_07 e
kc_09 —, e dentro deles pelos itens de **treino**, que é onde o banco
esgota e onde a falta de item faz a premissa terminar em aberto. São 15
nós; os outros 64 esperam.

**Os 51 candidatos de `candidatos/` não entram no domínio.** Eles foram
escritos para provar que o gerador funcionava, e provaram: o esquema
fechado, a conferência pelo carregador e o portão do `revisado_por` já
tinham rodado ponta a ponta. Como conteúdo, nunca foram avaliados por
ninguém, e os nós deles passam a ser cobertos por molde. A fila de
revisão que estava parada desde outubro deixa de existir — não por ter
sido vencida, por ter perdido a finalidade.
