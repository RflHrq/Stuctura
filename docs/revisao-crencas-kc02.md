# Revisão das crenças do kc_02 — o que fica, o que sai, o que pode entrar

Conferência das seis crenças propostas para o kc_02 **contra a obra
primária**, não de memória. O que entra num TCC precisa de citação que
alguém possa abrir.

## Como foi conferido

A busca web desta sessão está fora do ar, então a conferência foi feita
baixando as fontes direto:

| Fonte | Como |
| --- | --- |
| Sorva (2012), *Visual Program Simulation in Introductory Programming Education* | texto integral do repositório da Aalto (`aaltodoc`), Apêndice A, Tabela A.1 |
| FAQ comp.lang.c | `c-faq.com`, seção 4 (Pointers), perguntas 4.13 a 4.16 |

O Apêndice A é um **catálogo de 162 concepções errôneas** levantadas da
literatura, com número, tópico, descrição e fonte. Um dos tópicos é
`Refs` — *"references and pointers, reference assignment and object
identity"*.

**A numeração de página foi calibrada contra a sua própria curadoria:** a
citação existente dizia "p. 360, item 14", e o item 14 cai na p. 360 pela
convenção de rodapé do documento. As páginas abaixo seguem a mesma régua.

---

## Veredito, crença por crença

### Ficam, com fonte nova e melhor (3)

**`memory_is_by_name` — B1** · era T sem fonte, vira **D**

> Sorva (2012), p. 360, **item 14**: *"A variable is (merely) a pairing of
> a name to a changeable value (with a type). It is not stored inside the
> computer."* (Sorva 2008; Doukakis et al. 2007)
>
> Reforçada pelo **item 64**, p. 362: *"A variable [...] is merely a name
> which can be used to manipulate an object."* (Sorva 2008; Ma 2007)

Era a minha aposta mais arriscada e é a mais bem documentada das seis. "Não
está guardada dentro do computador" é exatamente a crença de que não existe
lugar numerado — e sem lugar numerado, ponteiro não tem o que guardar.

**`pointer_and_target_are_one` — I1** · era T sem fonte, vira **T com fonte**

> Sorva (2012), pp. 362–363, **itens 66, 67 e 68**, os três de Ma (2007):
> *"Assigning an object means 'sending' an object (or a copy) to a
> variable"*; *"Assigning to an object causes it to become equal to the
> assigned object"*; *"Assigning to an object means that (some) instance
> variables get new values from the assigned object."*

Três itens independentes do mesmo estudo descrevem a mesma confusão. Em C
ela aparece inteira na diferença entre `p = q` e `*p = *q`.

**`pointer_is_data` — B3** · era T, **continua T, com a citação corrigida**

> Sorva (2012), p. 362, **item 65**: *"A (non-primitive Java) variable does
> not hold a reference but a set of object properties."* (Sorva 2008;
> Ma 2007)

**Correção na curadoria antiga.** A citação existente apontava o item 14,
que é sobre variável ser um par nome-valor — **não é sobre ponteiro**. A
crença está no catálogo, mas no item 65. A fonte estava certa, o item não.

### Fica como estava, conferida (1)

**`pointer_is_integer` — I2** · **L**, texto conferido em c-faq.com

> 4.14 — *"How are integers converted to and from pointers? Can I
> temporarily stuff an integer into a pointer, or vice versa?"*
> 4.15 — *"How do I convert an int to a char *? I tried a cast, but it's
> not working."*

Grau **L** e não D, e isso é deliberado: o FAQ é prova de que a pergunta é
feita o tempo todo, não estudo empírico da crença.

### Ficam como hipótese declarada (2)

Procurei as duas nos 162 itens do catálogo. **Não estão lá**, e digo isso
na própria fonte da crença em vez de deixar a dúvida no ar.

**`pointer_has_no_address` — B2** · "o ponteiro é só a seta"

Nenhum dos 162 itens afirma que a referência não ocupa espaço. A suspeita é
que a crença seja **fabricada pelo material didático**: todo mundo desenha o
ponteiro como flecha, e flecha não tem endereço. Se existir, ela explode em
`&p` e explica por que ponteiro para ponteiro trava tanta gente.

**`pointer_is_pointless` — I3** · "é um jeito complicado de fazer o que já dá"

Não está no catálogo porque o catálogo é sobre **mecanismo**, e esta é sobre
**finalidade**. É o que a torna interessante: ela sobrevive a quem acerta
todas as outras premissas. Quem a sustenta decora a sintaxe e não usa
ponteiro quando precisaria.

Duas hipóteses em seis, declaradas, é a mesma proporção que você já aceitou
no kc_00 com `type_is_a_hint` — e com a diferença de que agora está escrito
que a busca foi feita e deu negativo.

### Saem, e por quê (2 — confirmadas)

**`pointer_lives_in_heap`** — depende de stack e heap (kc_01). Volta com o nó.

**`voidptr_is_universal`** — conferida no FAQ 4.13: *"My compiler complained
when I tried to stuff function pointers into a void *"*. É erro de quem **já
sabe** o que é um ponteiro. Fora de um tópico chamado "o que é um ponteiro".

---

## Três candidatas a entrar, todas com fonte

| Candidata | Fonte | Onde cabe |
| --- | --- | --- |
| **`two_pointers_two_objects`** — "dois ponteiros diferentes apontam necessariamente para coisas diferentes" | Sorva (2012), p. 363, **item 75**, Holland et al. (1997): *"Two different variables must refer to two different objects"* | **aqui, se você quiser um 7º nó** |
| **`pointer_never_repoints`** — "depois que p aponta para x, aponta para sempre" | p. 363, **itens 73 e 74**, Holland et al. (1997) | kc_03 (declaração e inicialização) |
| **`arrow_points_backwards`** — "o objeto sabe quem aponta para ele; a seta vai ao contrário" | p. 363, **item 78**, Holland et al. (1997); Sajaniemi et al. (2008) | kc_04 (`*` e `&`) |

**A minha recomendação é não acrescentar o 7º nó agora.** O apelidamento
(`two_pointers_two_objects`) é bonito e documentado, mas custa um nó, 6
atividades e uns 12 passos na sessão — e a revisão final já mostrou que o
caminho difícil do kc_00 bate em 89 passos. Ele é o primeiro candidato do
kc_02 quando houver folga, ou o nó de abertura do tópico seguinte.

---

## Bônus: três achados para o **kc_00**, que não eram o alvo

A mesma conferência atravessou o seu catálogo antigo.

**1. A sua única hipótese está documentada.**

`type_is_a_hint` ("toda variável ocupa o mesmo espaço; o tipo é só um aviso
para o compilador") está declarada como **E — a única E do catálogo,
hipótese a testar**. Ela está no Sorva:

> p. 366, **item 123**: *"Objects are allocated the same amount of memory
> regardless of definition and instantiation."* (Kaczmarczyk et al. 2010)

Se você aceitar a transposição de objeto para variável, `type_is_a_hint`
sobe de **E** para **D**. Muda o que você escreve no TCC: deixa de ser "uma
crença que eu inventei e fui testar" e passa a ser "uma crença documentada
que eu fui confirmar em C".

**2. `declaration_zeroes` tem fonte melhor do que a que está lá.**

Hoje cita K&R §2.4 — uma obra técnica que *contradiz* a crença. O achado
empírico existe:

> p. 359, **item 10**: *"Variables always receive a particular default value
> upon creation."* (du Boulay 1986; Samurçay 1989)

Sobe de **L** para **D**.

**3. As outras três conferem.**

| Crença do kc_00 | Item do catálogo |
| --- | --- |
| `no_value_no_memory` | p. 360, item 22 — *"Unassigned variables of primitive type (in Java) have no memory allocated"* (Kaczmarczyk et al. 2010) — **a mesma fonte que você já citou** |
| `variable_remembers` | p. 359, item 9 — *"A variable can hold multiple values at a time / 'remembers' old values"* (du Boulay 1986; Soloway et al. 1982; Putnam et al. 1986; Sleeman et al. 1986) |
| `assignment_symmetric` | p. 359, item 11 — *"Primitive assignment works in opposite direction"* (du Boulay 1986; **Ma 2007**; Putnam et al. 1986) — **a mesma fonte que você já citou** |

---

## O quadro depois da revisão

| Nó | Crença | Antes | Depois |
| --- | --- | --- | --- |
| B1 | `memory_is_by_name` | T sem fonte | **D** — Sorva item 14 |
| B2 | `pointer_has_no_address` | E | **E**, com a busca registrada |
| B3 | `pointer_is_data` | T, item errado | **T** — Sorva item 65 |
| I1 | `pointer_and_target_are_one` | T sem fonte | **T** — Sorva itens 66–68 |
| I2 | `pointer_is_integer` | L | **L**, texto conferido |
| I3 | `pointer_is_pointless` | E | **E**, com a busca registrada |

**Quatro das seis com fonte verificável, duas declaradas como hipótese.**
Antes da conferência eram duas com fonte e quatro no ar.

## O que precisa da sua decisão

1. **O 7º nó** (`two_pointers_two_objects`, o apelidamento): entra agora ou
   fica para depois? Eu recomendo depois.
2. **`type_is_a_hint` do kc_00 sobe de E para D?** É transposição de objeto
   para variável — defensável, mas a decisão é sua, e muda o texto do TCC.
3. **`declaration_zeroes` troca K&R pelo item 10?** Eu manteria as duas: a
   fonte empírica da crença e a obra técnica que a contradiz fazem papéis
   diferentes.
4. **As duas hipóteses E ficam?** Elas são, para mim, a parte mais
   interessante do catálogo — são as únicas que podem produzir um achado
   negativo publicável.
