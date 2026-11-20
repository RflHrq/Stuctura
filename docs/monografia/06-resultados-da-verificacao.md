# 6. Resultados da verificação

## 6.1 Escopo verificado

O Quadro 6.1 resume a dimensão do sistema abrangido pela verificação descrita na Seção 5, na versão de 19/11/2026.

**Quadro 6.1 — Dimensão do sistema verificado**

| Elemento | Quantidade |
| --- | --- |
| Tópicos, todos na trilha | 13 |
| Premissas | 79 |
| Concepções errôneas no catálogo | 61 |
| Questões no banco | 560 |
| Passos de escada (versões) | 402 (804) |
| Demonstrações com previsão | 80 (41 saídas, 39 do compilador) |
| Cenas da revisão | 79 |
| Trechos de código das escadas | 1 762 |
| Testes automatizados | 7 553 |

## 6.2 Conferência do conteúdo por compilador

O conferidor não acusa nenhum problema nos 13 tópicos: os 402 passos, os 79 exemplos resolvidos e as 80 demonstrações comportam-se, no gcc 16.2, como o texto afirma. Das 80 demonstrações, nove requerem opções adicionais do compilador: sete, o analisador de fluxo (`-fanalyzer`); uma, a opção `-Wpointer-arith`; e uma, a do valor `NULL` no tópico kc_05, as opções `-O2` com `-Wnull-dereference`. As demonstrações que dependem do ambiente contêm nota que explicita essa dependência.

As 79 cenas também foram aprovadas na conferência: em cada ponto percorrido por cada cena, o programa instrumentado afirma o valor de cada variável, o destino de cada ponteiro e o número de execuções da linha, e nenhuma afirmação falha. Das 79, 20 passam por dentro de funções (duas delas, a da função `conta`, no kc_01, e a da função `dobra`, no kc_12, pela mesma função duas vezes), 13 por arrays e 17 por blocos do `malloc`.

No banco de questões, das 69 questões de prever a saída conferidas, todas imprimem o valor da alternativa correta, e nenhum trecho das 321 questões com código divide uma cadeia de caracteres entre duas linhas. Os defeitos identificados pela conferência do banco são relatados na Seção 6.4.

A seleção de questões deixa 93 questões do banco fora da trilha, por utilizarem construções que nenhum tópico ensinou até aquele ponto. Com essa exclusão, as 79 premissas têm como abertura uma questão com código.

## 6.3 Medida do percurso com estudantes simulados

O Quadro 6.2 apresenta o número de telas e de toques necessários para que cada perfil percorra cada tópico, no ritmo completo. Um toque corresponde a um envio, isto é, a cada vez que a pessoa responde ou avança: selecionar a resposta, confirmá-la e escolher a razão e a certeza, na mesma tela, contam como um único toque.

**Quadro 6.2 — Número de telas e de toques (telas / toques) por tópico e por perfil, no ritmo completo**

| Tópico | Sabe tudo | Não sabe, aprende | Erra todo passo | Sustenta e muda | Sustenta e não muda |
| --- | --- | --- | --- | --- | --- |
| kc_00 | 12 / 16 | 22 / 38 | 32 / 80 | 32 / 31 | 37 / 56 |
| kc_01 | 12 / 16 | 22 / 36 | 32 / 76 | 32 / 31 | 37 / 56 |
| kc_02 | 14 / 19 | 26 / 45 | 38 / 95 | 38 / 37 | 44 / 67 |
| kc_03 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_04 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_05 | 14 / 19 | 26 / 44 | 38 / 93 | 38 / 37 | 44 / 67 |
| kc_06 | 14 / 19 | 26 / 44 | 38 / 93 | 38 / 37 | 44 / 67 |
| kc_07 | 16 / 22 | 30 / 51 | 44 / 108 | 44 / 43 | 51 / 78 |
| kc_08 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_09 | 18 / 25 | 34 / 57 | 50 / 121 | 50 / 49 | 58 / 89 |
| kc_10 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_11 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |
| kc_12 | 14 / 19 | 26 / 43 | 38 / 91 | 38 / 37 | 44 / 67 |

Três observações decorrem do quadro:

- A extensão da sessão varia conforme a necessidade da pessoa, e não conforme o tópico. O perfil que sabe todo o conteúdo percorre um tópico de seis premissas em 14 telas; os que necessitam de ensino ou de correção em todas as premissas, em 26 a 44 telas. O tamanho do tópico influi apenas pelo número de premissas: o kc_09, com oito, é o mais longo em todos os perfis.
- O limite de duração é respeitado. Mesmo o perfil que erra todos os passos conclui o tópico, com as premissas em aberto e sem repetição indefinida: o pior caso é finito e previsível.
- A demonstração é breve. O perfil que sustenta a concepção errônea e a abandona realiza menos toques do que o que não sabe e aprende (37 e 43, respectivamente, em um tópico de seis premissas), pois a demonstração substitui o percurso da escada, e não se soma a ele.

Os valores referem-se a perfis simulados e servem para mostrar que o percurso se comporta conforme o projeto. Não indicam o tempo que uma pessoa leva para concluir a sessão nem se ela aprende, o que exigiria o estudo descrito no Apêndice A.

## 6.4 Defeitos identificados pela verificação

O resultado mais relevante da verificação não é a ausência de problemas na versão descrita, mas o conjunto de defeitos identificados ao longo do processo.

A leitura do sistema pelo autor, realizada quando a verificação automatizada já não acusava problemas, identificou um tipo de defeito que nenhum teste apontaria, por não se tratar de afirmação falsa, e sim de deficiência de clareza: perguntas que repetiam a frase anterior (Seção 5.7). Dos 244 passos guiados, 101 tiveram a frase reescrita: o passo lido inicialmente pelo autor, 46 dos marcados pelo programa e 54 que o programa não marcou e que somente a leitura identificou. O programa identificou, portanto, menos da metade dos casos: a marcação por palavras serviu como ponto de partida, e não como critério.

A verificação automatizada identificou defeitos de outra natureza, todos corrigidos na versão descrita:

- Oito questões com o código dividido na tela. No tópico kc_02, oito questões continham a sequência `\n` do `printf` gravada como quebra de linha real, de modo que a chamada a `printf` era exibida em duas linhas e o código não compilava. Uma delas era a pergunta de abertura da premissa B3. A leitura não havia percebido o defeito, identificado nas oito questões pela conferência do banco.
- Uma resposta inválida no compilador do laboratório. Uma questão do tópico kc_12 perguntava o que é impresso por `p == NULL` depois de `p` receber o endereço de uma variável local de uma função já encerrada, e indicava 0 como resposta correta. No gcc 16.2, o compilador emite um aviso e devolve `NULL` no lugar desse endereço, e o valor impresso é 1; além disso, o padrão da linguagem C não define aquele valor.
- Uma afirmação dependente da versão do compilador. Uma questão do tópico kc_11 afirmava que o compilador "recusa" a aritmética com `void *`; o gcc aceita a operação por uma extensão própria e apenas emite aviso com a opção `-Wpointer-arith`. A questão permanece fora da trilha, por utilizar uma função de várias linhas, e a demonstração do tópico utiliza essa opção e o informa na nota de ambiente.
- Uma alternativa correta que utilizava conceito não ensinado. Uma questão do tópico kc_10 indicava como correta a alternativa "a vira ponteiro para fileira", conceito que a escada deliberadamente não aborda.
- Um treino que repetia a demonstração. Em uma sessão de ensaio, o primeiro passo de prática posterior a uma demonstração exibia a mesma função que a demonstração acabara de exibir, o que resultava na mesma tela duas vezes seguidas. O teste correspondente a essa regra (Seção 5.3) identificou o mesmo defeito em passos de outros três tópicos.
- Uma nota de ambiente que afirmava o que não havia sido conferido ("outros compiladores reclamam").
- Dois defeitos de interface. O teste de contraste e a conferência no navegador identificaram uma lacuna de exercício ilegível no tema claro e uma barra superior que ultrapassava a largura da tela do celular no tópico de oito premissas.

Trata-se de defeitos que uma leitura atenta não percebe e que a verificação automatizada identifica, por comparar o texto com o programa, e não com a lembrança de quem o redigiu.
