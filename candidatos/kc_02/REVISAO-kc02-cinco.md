# Revisão do material do kc_02 — os cinco nós restantes

Candidatos, não são domínio. Uma folha só para os cinco, porque as
decisões de fundo são comuns a eles. **Cada arquivo tem a sua
assinatura**, e você aprova um por um:

| nó | assinatura |
| --- | --- |
| B1 | `8605c1dbb352` |
| B3 | `acaef4316bb2` |
| I1 | `ab08cde6ea77` |
| I2 | `d83f54514551` |
| I3 | `a89b55c4bd00` |

(O B2, revisado em folha própria, é `091d37b9cac1`.)

Para aprovar, escreva no cabeçalho do YAML correspondente:

```yaml
revisado_por: <seu nome>
revisado_sha: <a assinatura da linha acima>
```

## O tamanho da mudança, medido

| nó | palavras de ensino | itens de entrada |
| --- | --- | --- |
| B1 | 207 → **519** | 1 → 3 |
| B2 | 86 → **577** | 1 → 3 |
| B3 | 248 → **644** | 1 → 3 |
| I1 | 86 → **591** | 1 → 3 |
| I2 | 99 → **641** | 1 → 3 |
| I3 | 85 → **691** | 1 → 3 |
| **kc_02 inteiro** | **811 → 3.663** | **6 → 18** |

O B1 e o B3 **já tinham ampliação** e não ganharam outra — os arquivos
deles trazem `ampliacao: ja_existe_no_dominio`. Os três nós de
inferência ganharam a primeira.

## Três decisões que não são minhas

### 1. O I3 depende de um conceito não introduzido

`funcao_com_parametro` está `nao_introduzido` no inventário, com esta
justificativa: *"Funções aparecem, e PARÂMETRO NENHUM: as duas
assinaturas dos cartões são `int conta(void)` e `int *faz(void)`."*

E o I3 — o nó que **fecha** o tópico — tem como exemplo
`void dobra(int *q)` e dez itens sobre passar endereço para função.
Não há como ensiná-lo sem isso: "de outro ponto do programa" é a
fronteira de uma função; sem ela, bastaria usar o nome e o ponteiro não
teria serventia.

O material que escrevi **introduz** o conceito, no mínimo necessário: o
contraste entre receber o valor e receber o endereço. Suas opções:
aprovar a introdução aqui, mover o I3 para depois de um tópico que
ensine funções, ou tirar o I3 do kc_02. Eu recomendo a primeira — e ela
destrava também o degrau substituto do `scanf`, que o inventário
registra como bloqueado pelo mesmo motivo.

### 2. As inferências não têm cartão de ensino

Está escrito no inventário, na entrada `tipo_do_ponteiro`: *"é premissa
do tópico e tem itens, mas não tem cartão de ensino: o ensino cobre B1,
B2 e B3, e I2 é inferência."*

A abertura da unidade ensina **três** cartões. I1, I2 e I3 só aparecem
para quem declara lacuna. Com o material destes arquivos, a abertura
poderia passar a ter seis. É mudança de desenho da unidade e de
comprimento da sessão — sua e do orientador.

### 3. Dois conceitos sairiam de `so_avaliado`

- **`sizeof`** — hoje só mencionado dentro de um `malloc` do kc_01 cujo
  texto é sobre tempo de vida. A ampliação do B2 e a do I2 o explicam.
- **`tipo_do_ponteiro`** — hoje sem cartão. O material do I2 é o cartão.

Se os arquivos forem aprovados, o inventário precisa ser atualizado
junto, com a evidência apontando para eles. Senão o sistema continua
dizendo que não ensinou o que passou a ensinar.

## O que a máquina já conferiu

**Oráculo (gcc `-Wall -Wextra`):**

```
B1  &idade == &outra -> 0        a=20, b=20, &a==&b -> 0
B3  *p -> 42                     x depois de *p = 7 -> 7
I1  q=&b; *q=99  ->  a = 42, b = 99        &a == &b -> 0
I2  (pi+1)-pi -> 4 bytes         (pc+1)-pc -> 1 byte
I2  int *p = x;  ->  ERRO de compilação, não aviso
I3  dobra(&n) -> n = 20          dobra_valor(m) -> m = 10
```

**A lista de `docs/linguagem.md`, nos doze itens novos:** três
alternativas, a certa não é a mais longa, todo distrator aponta uma
crença que existe no catálogo, o gabarito não é distrator, nenhum id
colide com os 60 que já existem, e nenhum enunciado tem "sempre" nem
"nunca". Rodado: **nenhum problema**.

**Quatro defeitos meus que o conferidor pegou** e que estão
consertados: a chave `no:` virava booleano em YAML; `ciu_kc02_e3` já era
o item de entrada do B3; duas alternativas começadas por `nada:`
quebravam o YAML; e no item do I3 a alternativa certa era a mais longa —
pista de formato.

## O que fica para a sua leitura

- A **regra da seta** (desenhe a seta, nunca diga que o ponteiro É a
  seta) vale em cada linha dos seis arquivos.
- **No B1, nenhum ponteiro pode aparecer** — é a restrição do cabeçalho
  do grafo. Confira se escorreguei.
- **No I2, a metáfora cala**: `p + 1` é kc_11. Usei-o só como evidência
  de que o tipo muda o comportamento, e digo em voz alta que *quanto*
  ele anda é outro tópico. Veja se o limite ficou claro o bastante.
- Os **casos resolvidos** usam endereços inventados (`0x1000`, "digamos")
  em alguns nós e a saída real da máquina em outros. Decida qual dos
  dois é a regra.
- Cada distrator é a crença **dita bem**? Alguém escolheria aquilo?

## O que entra sem mexer em código

**Entra hoje:** as três ampliações novas (o nó já aceita
`interpretation`) e os doze itens de entrada.

**Não entra:** `narracao`, `caso_resolvido` e `reexplicacao` são campos
que não existem — exigem mudança no carregador, no motor e na tela.

## E as descidas, que não precisaram ser escritas

As **seis** crenças do kc_02 já têm descida: quatro passos cada, exceto
`pointer_is_pointless`, com três. No projeto inteiro são 7 para 79
crenças — o kc_02 tem seis delas. Para este tópico, a persona que erra
já tem o caminho inteiro escrito. Falta ligar `STRUCTURA_DESCIDA=1`, e
isso é decisão de coleta: ligar no meio invalida a comparação entre
participantes.
