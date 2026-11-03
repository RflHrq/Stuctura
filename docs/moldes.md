# Moldes paramétricos, com oráculo de compilador

> Desenho aprovado em 03/11/2026. Ainda não implementado — o que existe é
> a sonda descartável que mediu a viabilidade, e os números dela estão
> aqui.

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
  node: B1
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
```

**O gabarito é regra, não texto.** É o que permite uma revisão valer por
muitas: não se leem 150 respostas, lê-se a regra que as produz.

**Cada distrator continua amarrado à crença por id**, da lista fechada do
catálogo. O molde não pode inventar concepção errônea — é a mesma trava
que o gerador de hoje tem.

**O `revisado_por` sai do item e vai para o molde.** É a mudança de objeto
da revisão, e é ela que torna a coisa viável. Os itens expandidos carregam
`do_molde: mol_kc07_B1_reconhecer` para a procedência não se perder.

**Em `prever_saida`, o oráculo deixa de conferir e vira gabarito**: a
resposta certa é literalmente o que o programa imprime, e a máquina a
calcula.

## O que o item expandido carrega

Dois campos novos em cada atividade gerada, e portanto em `Atividade`:

```yaml
- id: mol_kc07_B1_reconhecer_03
  node: kc07:B1
  do_molde: mol_kc07_B1_reconhecer
  parametros: {tipo: double, nome: buf, n: 8}
  ...
```

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

**O oráculo é obrigatório.** Molde sem programa que o confira é texto de
modelo sem conferência nenhuma. Se a afirmação do item não puder ser
verificada por um programa, aquele item continua sendo escrito à mão. A
camada cobre o que a máquina sabe julgar e não finge cobrir o resto.

**As três variações da revisão humana são escolhidas, não sorteadas:** os
extremos do espaço de parâmetros — o menor e o maior `n`, o nome mais
curto e o mais longo —, que é onde a concordância do português quebra.

## A linha de comando

```bash
# o modelo escreve o molde, e os quatro portões rodam em seguida
python scripts/gerar.py --topico kc_07 --no B1 --molde --degrau 1

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

**Seis variações por molde**, e não as 150. A escolha é determinística e
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

**Nenhum participante real passou por item gerado de molde.**

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
