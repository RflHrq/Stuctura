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

- [ ] A monografia inteira, na versão final (78 páginas em 23/11/2026).
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
      traz os 114 itens na ordem de leitura, cada uma com a página, o
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
- [x] "Laboratório": o autor esclareceu em 23/11/2026 que o sistema só
      roda no computador dele, e que o laboratório é onde o estudo com
      estudantes deve ser aplicado, para o pesquisador acompanhar o
      participante. A Seção 3.9 diz onde o sistema roda, 6.4 e a
      conclusão falam do "compilador utilizado na verificação", e o
      Apêndice A ganhou o laboratório e a razão da aplicação presencial.
      Em 23/11/2026 o autor precisou: "laboratório" quer dizer um
      lugar em que ele supervisione quem responde, e pode ser uma
      sala. O Apêndice A passou a dizer "de forma presencial e
      supervisionada, em uma sala ou laboratório da universidade".
- [x] Seções 5, 6 e 7, conferidas contra o código, os testes e o
      histórico em 23/11/2026. O conferidor foi executado de novo nos 13
      tópicos, no gcc 16.2: 79 premissas, 402 passos, nenhum problema.
      Conferem: a lista fechada de seis opções do compilador, os limites
      das regras de redação (de três a sete passos, 30 palavras, cinco
      palavras de retorno), os dez perfis nos dois ritmos, a pasta
      separada das sessões de ensaio e o ambiente (gcc 16.2 no Windows).
      Quatro frases diziam mais do que há para mostrar e foram ajustadas:
      - 5.1 dizia que cada parte foi especificada antes e que o teste de
        cada comportamento veio antes do código. O histórico sustenta a
        prática (33 commits registram o teste visto falhar, 51 declaram
        teste alterado de propósito, há oito planos em `docs/`), e não
        cada caso: a frase passou a descrever a prática;
      - 5.1 dizia que as decisões foram registradas com o custo de um
        eventual erro; o registro permanente são as mensagens de commit,
        com a justificativa;
      - 5.2 dizia que cada opção do compilador entrou com um teste. Têm
        esse teste as quatro que as demonstrações usam; `-O1` e `-Wextra`
        estão na lista e nenhuma demonstração as usa;
      - 5.5 atribuía o limiar antigo à "versão 2.0 da norma".
- [ ] Seção 6.4: commits dos defeitos relatados. Achados: `579e89c` (as
      oito questões do kc_02 e a conferência do banco), `9e766dc` (a
      resposta inválida do kc_12 e o "recusa" do kc_11), `7232144` (a
      alternativa "a vira ponteiro para fileira" do kc_10) e `2fe883c`
      (a nota "outros compiladores reclamam"). Faltam localizar o commit
      do treino que repetia a demonstração e os dos dois defeitos de
      interface.
- [ ] Seções 5.5 e 5.6: a conferência no navegador "tela a tela" não
      tem registro além do histórico; a pasta de ensaios existe.
- [x] Figuras da Seção 3, refeitas em 23/11/2026 por
      `scripts/figuras_monografia.py`. As sete capturas mostravam só o
      que cabia na janela (o fim da tela ficava cortado), e as 3.3, 3.4a
      e 3.4b eram de antes do botão Sair. Agora cada uma vai do topo ao
      fim da tela; o fechamento (3.3) e a página inicial (3.6) vão em
      três colunas. O texto dizia que o fechamento tem quatro blocos; o
      quarto ("Ficou em aberto") só aparece quando há o que listar, e
      nenhum dos dez perfis simulados chega a ele: passou a dizer "até
      quatro blocos".
- [ ] "Versão de 19/11/2026" (Seções 3 e 6.1): o catálogo mudou em
      23/11/2026. Fixar a data e o commit no fechamento.
- [ ] A suíte inteira (7 555 testes) não teve rodada completa depois das
      mudanças no catálogo. Numa rodada, um teste de `mvp/test_gerador.py`
      falhou e não repetiu a falha sozinho. Rodar com a máquina acordada.
- [ ] Seções 5.2 e 7.1 dizem que parte do banco de questões depende de
      "leitura". O commit `857c5f4` registra que 252 questões foram lidas
      uma a uma com assistência da ferramenta, e que cinco foram
      corrigidas. O texto não diz quem leu nem relata essas cinco:
      decidir se entra.

## 6. Decisões e dados que só o autor tem

- [x] "kc" é *knowledge component*, componente de conhecimento (o
      autor, em 23/11/2026; os documentos do projeto já diziam
      "componentes de conhecimento"). O termo entrou na Seção 2.3,
      com VanLehn (2006), que já estava na lista e o define (ms p. 3);
      a Seção 3.1 diz o que o código abrevia, e a sigla KC entrou na
      lista de siglas. O texto declara que o tópico é um grão maior
      que o componente do autor, que fica mais perto da premissa.
- [ ] A ordem das seções, para confirmar com o orientador. O texto
      descreve o sistema (Seção 3) e a curadoria (Seção 4) antes do
      método de construção e verificação (Seção 5). Muitos trabalhos
      trazem a metodologia logo depois do referencial. Aqui ela vem
      depois porque verifica peças (passos, demonstrações, cenas) que a
      Seção 3 define, e a Seção 1.6 já anuncia os procedimentos. Se o
      orientador preferir a outra ordem, a Seção 5 sobe para depois da 2.
- [ ] A folha de aprovação está no PDF desde 23/11/2026, como no modelo
      do curso, com as linhas de assinatura e a data em branco. Faltam os
      nomes dos dois membros da banca, a instituição de cada um e, depois
      da defesa, a data da aprovação.
- [x] O texto da folha de rosto passou a ser o do modelo do curso, com a
      disciplina desta entrega, Trabalho de Conclusão de Curso II
      (decisão do autor em 23/11/2026).
- [ ] A ficha catalográfica: o curso exige, e ela é feita depois da
      defesa, para a versão final (o autor, em 23/11/2026). Nada a fazer
      nesta etapa.
- [ ] O repositório: privado ou público, licença e o e-mail que aparece
      nos commits.
- [ ] O documento on-line criado antes neste projeto guarda uma versão
      antiga do texto: atualizar ou apagar.

## 7. Fora do TCC, declarado como trabalho futuro

- O estudo com estudantes, com as providências éticas antes de qualquer
  coleta (Apêndice A, Seção A.5).
