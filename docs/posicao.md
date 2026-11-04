# A posição da alternativa certa

> Desenho aprovado em 04/11/2026. Ainda não implementado.

## O problema

Nos 562 itens dos treze tópicos, a resposta certa está na **primeira**
alternativa em 553 deles:

| posição | itens | |
| --- | --- | --- |
| `a` | 553 | 98,4% |
| `b` | 9 | 1,6% |
| `c` | 0 | — |
| `d` | 0 | — |

Isso não é detalhe de apresentação. É ameaça à validade do dado, e de um
tipo específico: o instrumento deixa de medir concepção errônea e passa a
medir, em parte, **quem reparou no padrão**. Um participante que note a
regularidade acerta sem saber o conteúdo, e o acerto dele entra na análise
indistinguível de um acerto de verdade.

Pior do que o ruído: o viés é **sistemático**, não aleatório. Ruído
aleatório some na média de 40 participantes; um viés que empurra todo
mundo na mesma direção, não. E ele contamina a medida central do trabalho
— a dupla resposta-razão —, porque quem acerta por posição ainda assim
escolhe uma razão, e o par sai "acerto com razão errada", que o CS-1 lê
como falso positivo. O viés produziria falsos positivos em massa, e eles
pareceriam achado.

### De onde ele veio

Não de uma decisão. O motor **já tem** a permutação estável, escrita para
a camada das razões:

```python
# mvp/motor.py:730
def ordem_das_razoes(semente: str, atividade: str, n: int) -> tuple[int, ...]:
    """Permutação estável, derivada da semente. Sem sortear: o motor é puro
    e a mesma sessão redesenha a mesma tela depois de um recarregamento."""
    digest = hashlib.sha256(("%s|razoes|%s" % (semente, atividade)).encode()).digest()
    return tuple(i for _, i in sorted((digest[i % len(digest)], i) for i in range(n)))
```

A camada 1 — as alternativas da pergunta — ficou de fora:

```python
# mvp/motor.py:671
"opcoes": [{"texto": o.texto} for o in a.opcoes],
```

Ordem crua do YAML, e o YAML escreve a certa em primeiro porque é assim
que um humano escreve um gabarito. Os 98,4% são a consequência de uma
camada ter recebido a permutação e a outra não.

A promessa, aliás, **já está escrita** — no docstring de `log.reconstroi`:

> Devolve a transição inteira — estado e tela —, porque quem retoma
> precisa saber não só em que ponto a pessoa parou, mas o que estava na
> frente dela: **a ordem das alternativas vem da semente, que é o código
> da sessão**.

O `reconstroi` já chama `motor.inicia(d, semente=sessao)`. A infraestrutura
está de pé; o que falta é a camada 1 cumprir o que o arquivo diz que ela
faz.

## O risco de verdade, que não é o embaralhamento

```python
# mvp/dominio.py:181
@property
def indice_correto(self) -> int:
    return next(i for i, o in enumerate(self.opcoes) if o.correta)
```

São 60 chamadas de `Resposta(escolha=...)` nos testes, e as que respondem
certo usam `a.indice_correto` — a posição **no arquivo**. No dia em que a
permutação existir, esse índice aponta para outra alternativa, e o motor
**aceita**: não é erro de programa, é uma resposta errada. A escada desce
em vez de subir, a crença errada é registrada, o estado sai plausível e
errado, e a suíte fica verde contando outra história.

É o mesmo defeito que o `log.py` já descreve em dois lugares — "o estado
sairia plausível e errado" — agora com os testes como vítima.

**O desenho tem de tornar isso impossível, não improvável.** É por isso que
a renomeação abaixo é parte da spec, e não arrumação.

## O desenho

### 1. A permutação

Uma função irmã da que já existe, no motor:

```python
def ordem_das_opcoes(semente: str, atividade: str, n: int) -> tuple[int, ...]:
    digest = hashlib.sha256(("%s|opcoes|%s" % (semente, atividade)).encode()).digest()
    return tuple(i for _, i in sorted((digest[i % len(digest)], i) for i in range(n)))
```

O separador `|opcoes|` em vez de `|razoes|` é o que impede as duas camadas
de receberem a mesma permutação para o mesmo item — o que seria uma
correlação entre a posição da resposta e a posição da razão, e um segundo
viés no lugar do primeiro.

**Pura, sem sorteio, derivada de (semente, item).** A semente é o código da
sessão, então:

- cada participante vê uma ordem diferente, e o que o P03 contar ao P04 não
  transfere;
- o mesmo item reapresentado dentro da sessão volta na **mesma** ordem — é
  a mesma pergunta, e a pessoa pode raciocinar "a primeira eu já descartei";
- recarregar a página redesenha a tela igual;
- a reexecução do log reproduz a ordem sem precisar gravá-la.

Semente vazia devolve uma permutação também — não a identidade. É o
comportamento que as razões já têm, e manter as duas camadas iguais vale
mais do que a conveniência de um caso especial.

### 2. Onde ela é lida

Hoje seis lugares dependem da posição em `opcoes` — dois que **escrevem**
a tela e quatro que **leem** o que voltou dela:

| | função | |
| --- | --- | --- |
| `motor.py:671` | `_apresenta` | escreve a tela do diagnóstico e do treino |
| `motor.py:1108` | `_entrada` | escreve a tela da entrada |
| `motor.py:747` | `_responde_diagnostico` | lê a escolha |
| `motor.py:1526` | `_responde_treino` | lê a escolha |
| `motor.py:1129` | `_responde_entrada` | lê a escolha |
| `motor.py:852` | `_pede_confianca` | lê a escolha guardada, para repetir o texto |

A simetria é o que torna a fatia verificável: **duas escritas e quatro
leituras, e as seis pela mesma ordem**. Qualquer uma que fique para trás
produz o desencontro entre o que foi mostrado e o que foi julgado — e é
por isso que o teste decisivo atravessa a sessão de fora, e não chama a
permutação dos dois lados.

Todos passam a ler pela ordem mostrada. **Nenhum estado novo**: a ordem é
função de (semente, item), e quem precisa dela a calcula.

As duas alternativas descartadas, e por quê:

**Permutar na carga** (`dominio.py` reordena ao montar a `Atividade`) seria
um lugar só. Mas a semente não existe na carga — a sessão ainda não
começou —, então todo participante veria a mesma ordem. Resolveria o viés
de posição e deixaria de pé o vazamento entre participantes, e tornaria
falsa a frase que já está escrita no `reconstroi`.

**Guardar a ordem no estado**, como as razões fazem em `pendente.razoes`,
imitaria o padrão ao pé da letra. Mas quem responde vai buscar a
`Atividade` no domínio, não no `pendente`: exigiria um campo novo e um
invariante — "a ordem no estado é a que foi mostrada" — que nada obriga a
continuar verdadeiro.

### 3. A trava contra o erro silencioso

`Atividade.indice_correto` é **renomeada** para
`indice_correto_no_arquivo`, e ganha uma companheira no motor:

```python
def indice_correto_na_tela(semente: str, a: Atividade) -> int:
```

A renomeação é o mecanismo de segurança. Sem ela, as 60 chamadas
continuariam executando e significando outra coisa; com ela, cada uma vira
um `AttributeError` que uma pessoa tem de olhar e trocar. O nome novo
também diz, no próprio nome, que aquela posição é a do arquivo e não a da
tela — que é a distinção que esta fatia inteira inventa.

Quem usa `indice_correto_no_arquivo` depois disto: o gerador e a folha de
revisão, que falam do arquivo. Quem usa `indice_correto_na_tela`: os
testes que atravessam uma sessão.

### 4. O log

`atividade_apresentada` ganha a ordem mostrada, espelhando o
`razoes_apresentadas`, que já grava as crenças na ordem exibida:

```json
{"tipo": "atividade_apresentada", "atividade": "...", "ordem": [2, 0, 1], ...}
```

É redundante para o CS-6 — a semente basta —, e não é redundante para a
análise: com o campo, o viés residual é medível no próprio dado, sem
ninguém reimplementar a permutação para conferir; e uma mudança futura na
função não reescreve o que os participantes viram.

**`VERSAO` sobe para 2.** A regra está escrita no `log.py`: *"sobe quando o
significado de uma linha muda, não quando o código muda"*. Um índice
gravado em `entrada_recebida` deixa de querer dizer "posição no YAML" e
passa a querer dizer "posição na tela". É exatamente isso.

Sessão `v1` continua reexecutável, **e sem ramo dentro do motor**: o
`reconstroi` lê a versão da abertura e passa `semente=""` para uma sessão
`v1`, porque foi assim que ela foi gravada — sem permutação na camada 1.
Não há dado de piloto a preservar (só sessões simuladas, que por regra
nunca entram no banco do piloto), mas o caminho fica honesto de graça, e é
o que o `LogIncompleto` já defende: falhar ou acertar, nunca devolver
estado plausível e errado.

> Isto é um remendo com prazo: a semente vazia só reproduz um `v1` porque
> a camada 1 não era permutada nele. No dia em que a permutação mudar de
> novo, nem isso serve, e aí a resposta é a versão recusar em vez de
> reexecutar.

## O que fica provado, e como

**O teste que importa não é unitário.** É um que atravessa a sessão pelas
rotas HTTP: a tela entrega uma lista de textos, a pessoa clica num índice,
e o que o motor julga tem de ser o texto que estava naquela posição. É o
único que pega o desencontro entre o que foi mostrado e o que foi lido —
um teste de unidade que chama a permutação dos dois lados concorda consigo
mesmo mesmo quando está errado.

| o que | como |
| --- | --- |
| a ordem é estável | mesma (semente, item) → mesma ordem, em chamadas separadas |
| a ordem muda entre sessões | sementes diferentes → ordens diferentes, no mesmo item |
| as duas camadas não correlacionam | sobre o banco inteiro, as duas ordens coincidem na frequência do acaso, e não sempre — num item de três alternativas há seis permutações, e duas funções iguais dariam 100% |
| o clique bate com o texto | sessão pelas rotas: o índice clicado julga o texto que estava ali |
| a reapresentação é igual | o mesmo item, duas vezes na mesma sessão, na mesma ordem |
| o viés acabou | nos 562 itens, com uma semente, nenhuma posição fica acima do que o acaso permite |
| CS-6 continua de pé | reexecutar uma sessão `v2` devolve o mesmo estado; reexecutar uma `v1` também |
| o rename não deixou resto | nenhuma chamada a `indice_correto` sobreviveu |

### A medida do viés, como teste

Hoje: 553 de 562 em `a`. Depois, com uma semente fixa, a contagem por
posição tem de caber no que o acaso produz. O teste afirma o **limite**, e
não o número: a maior posição não passa de uma folga sobre `n/k`, com `k`
alternativas. Número cravado é a quinta recorrência do defeito de teste que
este projeto já catalogou quatro vezes.

Este teste é a única prova direta de que a fatia resolveu o problema que a
motivou. Os outros provam o mecanismo.

## O que esta fatia NÃO faz

**Não embaralha a camada 3 (a confiança).** `CONFIANCAS` é
`("chutei", "acho que sei", "tenho certeza")`: três opções **ordinais**, e
a ordem delas *é* a escala. Embaralhar destruiria a leitura — e o viés de
posição nem existe ali, porque nenhuma das três é a certa.

**Não mexe no YAML, nem nos 562 itens.** A certa continua escrita em
primeiro, que é como se lê um gabarito. A folha de revisão do molde
continua mostrando `**[certa]**` em primeiro, e a assinatura de quem
revisou continua valendo — a permutação não é conteúdo.

**Não mexe nos portões do gerador.** `a certa é a única que começa em
minúscula` e `a certa é a mais longa com folga` olham **texto**, não
posição, e continuam valendo: são pistas que sobrevivem a qualquer
embaralhamento, e é por isso que elas existem separadas desta fatia.

**Não resolve o viés de comprimento nem o de vocabulário.** Só o de
posição. Os outros têm portão próprio, e se houver um terceiro ele é outra
fatia.
