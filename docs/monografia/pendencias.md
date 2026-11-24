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
quem assina.

- [x] O autor informou em 24/11/2026 que leu e valida a monografia
      inteira e todos os materiais. O campo `revisado_por` das 13
      escadas traz o nome dele e a data, com o texto de leitura que ele
      leu (`docs/escada-kcNN-leitura.md`: os passos, os exemplos
      resolvidos e as demonstrações). A declaração de IA e as Seções 5.8
      e 7.1 passaram a dizer que o conteúdo foi lido e validado pelo
      autor e que não foi revisado por especialista no domínio; a 7.2
      deixou de listar a revisão pelo autor como trabalho futuro. O
      registro é comentário no cabeçalho das escadas: a assinatura do
      conteúdo ficou igual, e a versão descrita segue a do commit
      `16d448b`.
- [ ] As 79 cenas não estão nos textos de leitura: são animações do
      código do exemplo resolvido, conferidas por programa. O texto diz
      que o autor leu as escadas, os exemplos e as demonstrações, e não
      que assistiu às cenas. Se ele as tiver visto no sistema, o texto
      pode dizer também isso.

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

## 4. Catálogo: as quatro hipóteses, que ficam sem fonte por desenho

As outras 57 das 61 estão conferidas na obra (Apêndice B).

| Concepção | Grau | Situação | O que fecha |
| --- | --- | --- | --- |
| `heap_dies_with_function` | E | hipótese declarada | nada: fica fora da coleta |
| `memory_is_uniform` | E | hipótese declarada | nada: fica fora da coleta |
| `type_is_a_hint` | E | hipótese declarada | nada: fica fora da coleta |
| `memoria_e_do_computador` | E | hipótese declarada | nada: fica fora da coleta |

- [x] As quatro que a curadoria não conferia por inteiro foram fechadas
      em 23/11/2026, a pedido do autor:
      - `uninitialized_is_null` ganhou a frase do item 10 de Sorva
        (2012), e o gerador a localiza no texto da obra;
      - `malloc_always_succeeds` cita só normas: a página da ERR33-C
        lista malloc com NULL no erro, e a CWE-252 tem o título citado;
      - `voidptr_arith_ok`: o índice da seção 11 do FAQ e a página da
        pergunta 11.24 foram baixados (com autorização do autor). A
        frase citada estava encurtada sem marca de corte e passou a ser
        literal;
      - `pointer_is_pointless`: o título da pergunta 4.1 do FAQ confere
        no índice. Estava contada na classe 1 só porque a nota dela
        menciona Sorva para dizer que a concepção NÃO está lá. A classe
        1 passou de 23 para 22 concepções e a classe 2, de 34 para 35; o
        gerador só conta Sorva como fonte quando há página ou item.
      A Seção 4 traz os números novos e relata os dois defeitos de
      registro (4.6.6). O teste anterior ao ramo
      (`mvp/test_procedencia.py`) teve três números atualizados, com
      autorização do autor.

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
- [x] Seção 6.4: os commits dos defeitos relatados, localizados em
      23/11/2026: `3f0c1e3` (as oito questões do kc_02 e a conferência do
      banco), `99abee5` (a resposta inválida do kc_12 e o "recusa" do
      kc_11), `1fb5635` (a alternativa "a vira ponteiro para fileira" do
      kc_10), `0729299` (a nota "outros compiladores reclamam"),
      `729d029` e `8710bfa` (o treino que repetia a demonstração: visto
      no ensaio do kc_01, e o teste achou o mesmo no kc_05, no kc_06 e
      no kc_12), `f7f6fd5` (a lacuna do completar, que sumia no tema
      claro) e `099a46c` (a barra superior com oito paradas em 360 px).
      A conferência mostrou que a frase atribuía os dois defeitos de
      interface ao "teste de contraste": o histórico diz que a lacuna
      foi achada na conferência no navegador e a barra, na revisão,
      confirmada no navegador; os testes vieram com as correções. A
      frase foi corrigida, e a abertura e o fecho da lista deixaram de
      dizer que tudo foi achado pela verificação automatizada.
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
- [x] A versão descrita passou a ser a de 23/11/2026, commit `16d448b`
      (Seções 3 e 6.1). A Seção 3 traz o endereço do repositório, por
      decisão do autor. O que vier depois desse commit e mexer no
      sistema ou no conteúdo pede nova rodada da suíte e nova data.
- [x] A suíte inteira rodou em 23/11/2026 sobre o commit `16d448b`, com
      a árvore limpa: 7 556 testes, 7 548 aprovados, 8 dispensados por
      construção (as demonstrações por aviso, que outro teste confere
      sem executar), nenhuma falha, em 35 min 26 s. O maior intervalo
      entre dois testes foi de 72 s: a máquina não dormiu. O log, com a
      hora em cada linha, está em `ensaios/suite-20261123/`, fora do
      repositório. A falha isolada de `mvp/test_gerador.py`, vista em
      20/11 numa rodada em que a máquina dormiu, não se repetiu. O
      Quadro 6.1 passou a 7 556 (entrou o teste das figuras em
      colunas) e ganhou a frase com o resultado da rodada.
- [x] A leitura das 252 questões com código que a saída não confere
      entrou no texto, por decisão do autor em 23/11/2026: a Seção 5.2
      diz que foi feita uma vez, com assistência do modelo de linguagem
      e com o resultado da compilação de cada trecho; a 6.4 relata as
      cinco questões corrigidas; a 7.1 diz de que leitura se trata. É o
      que o commit `2ba98f6` registra.

## 6. Decisões e dados que só o autor tem

- [x] "kc" é *knowledge component*, componente de conhecimento (o
      autor, em 23/11/2026; os documentos do projeto já diziam
      "componentes de conhecimento"). O termo entrou na Seção 2.3,
      com VanLehn (2006), que já estava na lista e o define (ms p. 3);
      a Seção 3.1 diz o que o código abrevia, e a sigla KC entrou na
      lista de siglas. O texto declara que o tópico é um grão maior
      que o componente do autor, que fica mais perto da premissa.
- [x] A ordem das seções fica como está (o autor, em 23/11/2026). O texto
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
- [x] O repositório é público, em `https://github.com/RflHrq/Stuctura`
      (decisão do autor em 23/11/2026, para o orientador e a banca
      acessarem). Antes do envio, o histórico foi reescrito:
      - o e-mail de todos os commits passou a ser o endereço noreply do
        GitHub, também nos dois planos que o traziam no texto;
      - saiu o token de exportação que ficou versionado por um dia, em
        03/09/2026 (não era mais o token em uso);
      - saíram as três cópias do registro de sessões de desenvolvimento
        de 29/10/2026.
      - numa segunda reescrita, no mesmo dia, saiu a pasta `.claude`
        (configuração local dos servidores de ensaio e do assistente de
        IA), que não tinha segredo e o autor preferiu não publicar. O
        texto dos seis portões de revisão, que o README cita, foi para
        `docs/revisao-de-material.md`.
      Todo o conteúdo de todos os commits foi varrido atrás de senhas,
      chaves de API, tokens e chaves privadas: nada. Os hashes dos
      commits mudaram; os citados nas mensagens e nos documentos foram
      trocados pelos novos. A cópia do repositório de antes da limpeza
      está em `backup/`, fora do controle de versão. Os commits novos
      saem com o e-mail noreply (configuração local do repositório).
      Só os ramos `trilha` e `master` vão para o GitHub: o ramo
      `claude/elastic-perlman-c65bb1`, de uma sessão antiga, ainda tem o
      histórico anterior e não pode ser enviado.
- [x] A licença do repositório é a MIT (o autor, em 23/11/2026): arquivo
      `LICENSE` na raiz, e uma seção no README que diz o que fica fora
      dela: as fontes tipográficas (OFL), os estilos do LaTeX (LPPL), os
      trechos citados de obras de terceiros e o texto da monografia. A
      exclusão do texto da monografia foi escolha de quem escreveu a
      seção, por cautela: se o autor quiser a monografia também sob a
      MIT, basta tirar a linha.
- [x] A declaração do orientador sobre as correções da banca (SIN499),
      preenchida a partir do modelo do curso com o nome e a matrícula
      do aluno e o nome do orientador, está em `entrega/`, fora do
      repositório. É para depois da defesa. A data do `.doc` é
      automática (a do dia em que o arquivo é aberto).
- [ ] O documento on-line criado antes neste projeto guarda uma versão
      antiga do texto: atualizar ou apagar.

## 7. Fora do TCC, declarado como trabalho futuro

- O estudo com estudantes, com as providências éticas antes de qualquer
  coleta (Apêndice A, Seção A.5).
