# Tarefas — ciclo 3

**Fechado.** Três tarefas, de `23de1e5` em diante.

Artefato da fase 5 do terceiro ciclo. Fecha as três decisões que a medição
do kc_02 deixou em aberto — e as três eram de **motor**, não de conteúdo.

O que as origina está em [processo.md](processo.md#o-que-a-medição-do-kc_02-mostrou):
36 atividades novas não fecharam o buraco da CS-10, e um terço das telas
pedia confiança onde ela não entra em decisão nenhuma.

**Portões:** **S** segurança · **M** dados · **U** interface. Em todo
commit: varredura de segredos e sabotagem antes de acreditar em teste verde.

---

## C1 — A crença já tratada sai da cédula, e a premissa não medida diz o nome

**O que muda:** a crença de um nó **já sustentado** deixa de ser oferecida
como razão; e `desconhecido`, no fim da unidade, vira `nao_medido`.

O rastro que obrigou a isso, de uma sessão de verdade:

```
nó B2 — os três itens dele apresentados
razão escolhida em 004 -> crença de I1
razão escolhida em 005 -> crença de B3
razão escolhida em 006 -> crença de I1   (I1 já confirmado)
estado final de B2: desconhecido
```

A crença do próprio B2 estava na cédula **nas três vezes** e nunca foi
escolhida. Oferecer para sempre uma ideia que a unidade já tratou gasta os
itens do nó hospedeiro sem nunca medi-lo. Quem checa se ela voltou é o
reteste, que tem fase própria.

**Pronto quando:** nenhuma premissa termina em `desconhecido`; o cardápio
nunca cai para uma razão só; e o log diz, por nó não medido, se ele nem foi
perguntado ou se os itens foram gastos sem atribuição.

**Portões:** M, U.

**Feito** (`23de1e5`). `razoes_de(d, a, e)` filtra por `sustentado`, com
fallback que devolve a lista inteira quando filtrar deixaria menos de duas
— com uma opção a camada 2 vira teatro. `NAO_MEDIDO` é estado próprio, com
evento `no_nao_medido` e motivo. A tela de quem responde e o painel ganharam
símbolo e nome para ele.

**Um teste existente caiu, e foi reescrito com aprovação.**
`test_t6_nao_refuta_um_no_ja_confirmado` montava exatamente a cena que a C1
tornou inalcançável. Virou dois: a garantia nova (a crença sai da cédula) e
a original, viva no caminho de fallback — em `ciu_kc00_001` os dois
distratores apontam a mesma crença, então ela continua sendo oferecida, e é
lá que a regra antiga precisa valer.

---

## C2 — A confiança fica onde ela decide alguma coisa

**O que muda:** no treino, a confiança só é perguntada no item que **fecha**
a sequência.

Medido: 44,8 telas de confiança por sessão de quem erra muito, 34% da
sessão. A classificação não roda no treino (`_resolve_treino` só olha
certo/errado), e o critério exige **duas** medidas — a confiança de quando
a crença foi detectada e a de quando a premissa foi confirmada. Essas duas
continuam.

**Decisão do dono**, entre três opções: ficou a do meio, que preserva o par
antes/depois por cerca de um terço do custo.

**Pronto quando:** uma pergunta de confiança por sequência fechada, não uma
por tentativa; o diagnóstico e o reteste não mudam; e pular fica registrado.

**Portões:** U, M.

**Feito** (`23de1e5`). Evento `confianca_pulada` com motivo — pular em
silêncio faria "não perguntei" e "perguntei e não respondeu" ficarem iguais
no log.

---

## C3 — O tamanho do tópico, decidido pela medição

**O que muda:** nada no código. A pergunta era se seis nós com 3+3 cabem na
sessão, e a resposta depende do que C1 e C2 fizeram ao tamanho dela.

**Resposta: cabem.** O caminhante, 30 sessões, antes e depois:

| Persona | antes da C1/C2 | depois | sem medida, antes → depois |
| --- | --- | --- | --- |
| acerta tudo | 42 passos | **42** | 0/10 → 0/10 |
| erra e aprende | 84–123 | **81** | 4/10 → **0/10** |
| erra e não muda | 110–149 | **90–118** | 6/10 → 0/10 em `desconhecido`, 4/10 nomeadas `nao_medido` |

**A C1 fechou o buraco no caminho realista.** Quem erra e aprende com a
refutação agora termina com as seis premissas confirmadas, sempre. Quem
nunca muda de ideia continua tendo premissas que a unidade não mede — o que
é verdade sobre a pessoa, não defeito do sistema — e agora elas aparecem
**nomeadas**, no mapa e no log.

A composição também mudou: a confiança caiu de 44,8 para 12,0 telas por
sessão de quem erra muito, de 34% para 12%.

**O único risco de estouro é a cauda de quem nunca muda de ideia**, em 118
passos. A alavanca, se o ensaio com pessoas mostrar que é longo demais, é o
**teto de tentativas por nó** — hoje 4, e parâmetro seu pela decisão 14.
Não mexi.

**Portões:** nenhum: é medição, não mudança.

---

## O que este ciclo não resolve

- **CS-11 e CS-12** continuam sem evidência: nenhuma pessoa real atravessou
  nada. O caminhante prova que a unidade termina e que as premissas ficam
  medidas; não prova que alguém entende a tela.
- Os **P1 da revisão final** que não eram de motor continuam de pé: o termo
  de consentimento, o plano de incidente, a exclusão que não alcança as
  cópias e os dois commits que não restauram no Windows.
- As **três crenças do kc_02 sem fonte empírica** — duas declaradas como
  hipótese, uma transposição à espera de fonte.
