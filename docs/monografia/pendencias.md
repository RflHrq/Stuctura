# Pendências da monografia (23/11/2026)

Lista para a revisão ponto a ponto do autor. Só o que está em aberto: o
que já foi fechado está no histórico e em [README.md](README.md). Arquivo
de trabalho, que não vai para o PDF.

## 1. Antes do aceite: perguntar ao orientador

O autor informou em 23/11/2026 que as duas respostas são sim.

- [x] Ele aceita o escopo sem avaliação com estudantes (Seções 1.5 e 7.1)?
- [x] Ele aceita a declaração de uso de IA (página 5 do PDF)? As
      diretrizes de IA da UFV classificam como uso restrito a escrita de
      textos apresentados como autoria própria (página 14 das
      diretrizes), e a declaração diz que o texto foi redigido com a
      ferramenta.

## 2. Leitura do autor

As diretrizes da UFV pedem que o conteúdo seja revisado e validado por
quem assina. Hoje a declaração diz que o conteúdo didático ainda não foi
integralmente revisado.

- [ ] A monografia inteira, na versão final (75 páginas).
- [ ] O conteúdo didático: as 13 escadas (`mvp/dominio/escada_kc00.yaml`
      a `escada_kc12.yaml`), com 402 passos, 80 demonstrações e 79 cenas.
      O campo `revisado_por` está em branco nas 13. Quando a leitura
      terminar, mudam a declaração de IA e as Seções 5.8 e 7.1.

## 3. Referências

São 22 obras na lista. Cada uma tem a entrada em
[conferencia-das-referencias.md](conferencia-das-referencias.md) (onde
foi aberta e o que sustenta, com página) e o arquivo em `fontes/` (fora
do git).

- [ ] Conferir, obra por obra, cada frase do texto que a cita contra o
      arquivo aberto. O [roteiro-de-conferencia.md](roteiro-de-conferencia.md)
      traz as 110 citações na ordem de leitura, cada uma com a página, o
      arquivo a abrir e a frase.
- [ ] Kernighan e Ritchie (1988) saiu da lista em 23/11/2026, porque o
      livro não foi aberto; a refutação passou a citar o padrão da
      linguagem (ISO/IEC, 2011, p. 140). Se o autor quiser a obra de
      volta, é preciso abrir o livro e conferir a seção 2.4.
- [ ] UFV ([2026]), as diretrizes de IA: falta o endereço de onde o
      arquivo foi baixado.
- [ ] ISO/IEC (2011): é o rascunho de 2011 do padrão C. Se o autor
      obtiver a ISO/IEC 9899:2018 pela UFV, troca-se a citação.
- [ ] Seção 1.6: a classificação da pesquisa ("aplicada, de caráter
      tecnológico") está sem citação de obra de metodologia, porque
      nenhuma foi aberta.

Citadas por intermédio de outra obra (apud), não abertas e fora da lista,
como o texto declara: os nove estudos citados por Sorva (2012); Tippett
(2010), por Nussbaum, Cordova e Rehmat (2017); Doignon e Falmagne (1985),
por Falmagne et al. (2006).

- [ ] O autor se dispôs, em 23/11/2026, a obter os originais. Cada um
      que chegar vai para uma pasta própria em `fontes/`, é aberto,
      conferido contra o que o texto lhe atribui e passa de citação
      indireta a citação direta, com entrada na lista. Os que o catálogo
      usa de fato, e a concepção que cada um sustenta:
      - Kaczmarczyk et al. (2010): `no_value_no_memory`;
      - du Boulay (1986) e Samurçay (1989): `declaration_zeroes`;
      - du Boulay (1986), Soloway et al. (1982), Putnam et al. (1986),
        Sleeman et al. (1986) e Doukakis et al. (2007):
        `variable_remembers`;
      - Sleeman et al. (1986): `assignment_symmetric`;
      - Ma (2007): `declaration_allocates`;
      - Tippett (2010), p. 965, e Doignon e Falmagne (1985), na Seção 2.
      Holland et al. (1997) só é nomeado na Seção 4.3.1. Os dados
      bibliográficos estão na lista de trabalho ao fim de `curadoria.md`.

## 4. Catálogo: as oito concepções que a curadoria não confere na obra

As outras 53 das 61 estão conferidas na obra (Apêndice B).

| Concepção | Grau | Situação | O que fecha |
| --- | --- | --- | --- |
| `heap_dies_with_function` | E | hipótese declarada | nada: fica fora da coleta |
| `memory_is_uniform` | E | hipótese declarada | nada: fica fora da coleta |
| `type_is_a_hint` | E | hipótese declarada | nada: fica fora da coleta |
| `memoria_e_do_computador` | E | hipótese declarada | nada: fica fora da coleta |
| `malloc_always_succeeds` | N | cita só CERT C e CWE, abertos na conferência das referências, mas não reconferidos na curadoria | reconferir na curadoria |
| `pointer_is_pointless` | L | citação abreviada, com a forma íntegra localizada | conferir a forma íntegra |
| `uninitialized_is_null` | D | cita Sorva (2012) com página e item, sem frase entre aspas | pôr a frase do item e deixar o programa conferir |
| `voidptr_arith_ok` | L | pergunta 11.24 do FAQ; a seção 11 não foi reaberta | reabrir a seção 11 |

## 5. Afirmações de que algo foi feito (Seções 3, 5 e 6)

- [x] Seção 3, conferida contra o código e os dados em 23/11/2026: as
      duas citações (W3C e padrão C), as finalidades e os níveis das 560
      questões, os textos da interface, a ordem de preferência da
      reconferência, a ordem do caminho na página inicial, o ritmo da
      cena (1,3 s por passo), as licenças das fontes, os quatro blocos do
      fechamento e as explicações das 79 perguntas de abertura. Dois
      trechos não batiam e foram corrigidos: a frase da concepção citada
      em 3.1 não era a do catálogo, e a tela não diz "o compilador
      reclamou desta linha" (diz "O compilador reclamou:").
- [ ] O texto fala em "máquina do laboratório" (3.9) e "compilador do
      laboratório" (6.4 e conclusão). Confirmar com o autor se existe um
      laboratório ou se é o computador dele; se for o computador dele,
      trocar a expressão.
- [ ] Seção 5.1: "o teste de cada comportamento novo foi escrito antes da
      implementação" é uma afirmação sobre o processo inteiro. A evidência
      está nos planos (`docs/plano-*.md`) e nas mensagens de commit.
      Conferir por amostra, ou reduzir a afirmação ao que a amostra
      mostrar.
- [ ] Seções 5.5 e 5.6: a conferência no navegador "tela a tela" e as
      sessões de ensaio. Localizar a evidência de cada uma.
- [ ] Seção 6.4: cada defeito relatado deve ter o commit que o corrigiu.
      Achados até agora: `579e89c` (as oito questões do kc_02 com o código
      dividido, e a conferência do banco), `9e766dc` (a resposta inválida
      do kc_12 e a afirmação "recusa" do kc_11) e `2a549a2` (sair da
      sessão). Faltam os commits dos demais.
- [ ] Seções 5.2 e 7.1 dizem que parte do banco de questões depende de
      "leitura". O commit `857c5f4` registra que 252 questões foram lidas
      uma a uma com assistência da ferramenta, e que cinco foram
      corrigidas. O texto não diz quem leu nem relata essas cinco:
      decidir se entra.
- [ ] Figuras 3.3, 3.4a e 3.4b: capturas de 18/11/2026, anteriores ao
      botão Sair. O texto descreve a versão de 19/11/2026. Refazer.
- [ ] "Versão de 19/11/2026" (Seções 3 e 6.1): o catálogo mudou em
      23/11/2026. Fixar a data e o commit no fechamento.
- [ ] A suíte inteira (7 555 testes) não teve rodada completa depois das
      mudanças no catálogo. Numa rodada, um teste de `mvp/test_gerador.py`
      falhou e não repetiu a falha sozinho. Rodar com a máquina acordada.

## 6. Decisões e dados que só o autor tem

- [ ] O que "kc" significa nos códigos dos tópicos (kc_00 a kc_12).
- [ ] A ordem das seções: o sistema (Seção 3) vem antes do método
      (Seção 5).
- [ ] A folha de aprovação está no PDF desde 23/11/2026, como no modelo
      do curso, com as linhas de assinatura e a data em branco. Faltam os
      nomes dos dois membros da banca, a instituição de cada um e, depois
      da defesa, a data da aprovação.
- [x] O texto da folha de rosto passou a ser o do modelo do curso, com a
      disciplina desta entrega, Trabalho de Conclusão de Curso II
      (decisão do autor em 23/11/2026).
- [ ] A ficha catalográfica, se o curso a exigir.
- [ ] O repositório: privado ou público, licença e o e-mail que aparece
      nos commits.
- [ ] O documento on-line criado antes neste projeto guarda uma versão
      antiga do texto: atualizar ou apagar.

## 7. Fora do TCC, declarado como trabalho futuro

- O estudo com estudantes, com as providências éticas antes de qualquer
  coleta (Apêndice A, Seção A.5).
