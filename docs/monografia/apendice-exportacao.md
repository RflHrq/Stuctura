# Apêndice C — Formato da exportação das sessões

Este apêndice descreve as tabelas geradas pelo exportador das sessões da trilha (Seção 3.7), que fornecem os dados do sistema para o estudo com estudantes (Apêndice A). O exportador é executado pelo pesquisador, no computador em que o sistema roda, com o comando `python -m mvp.exporta_trilha --pasta coleta/portal --out analise/trilha`, e gera três arquivos: `sessoes.csv`, `premissas.csv` e `respostas.csv`.

Os arquivos seguem o formato *Comma-Separated Values* (CSV), com a primeira linha de cabeçalho e codificação *8-bit Unicode Transformation Format* (UTF-8) com marca de ordem de bytes, de modo que as planilhas eletrônicas, como o Microsoft Excel e o LibreOffice Calc, os abrem com a acentuação correta. Adotou-se esse formato, e não o formato próprio de pasta de trabalho do Excel, por ser texto aberto, legível por qualquer planilha e por ferramentas de análise estatística, sem dependência de programa específico; a planilha que o abrir pode salvá-lo naquele formato. Toda célula iniciada por caractere que a planilha interpretaria como fórmula recebe um apóstrofo, para que o conteúdo seja exibido, e não executado.

Em todas as tabelas, o participante é identificado pelo código com que entrou na sessão (P01, P02...), sem nome nem matrícula; a sessão aberta sem código é identificada pelo número que o sistema lhe atribuiu. Os valores lógicos são registrados como "sim" ou "não", e o campo sem valor fica vazio.

## C.1 Tabela de sessões

A tabela `sessoes.csv` tem uma linha por sessão, isto é, por participante e tópico (Quadro C.1).

**Quadro C.1 — Colunas de `sessoes.csv`**

| Coluna | Conteúdo |
| --- | --- |
| `participante` | código do participante |
| `topico` | código do tópico (kc_00 a kc_12) |
| `iniciada_em` | data e hora do primeiro evento da sessão |
| `ultima_em` | data e hora do último evento da sessão |
| `ritmo` | ritmo escolhido na entrada do tópico ("completo" ou "rapido") |
| `encerrada` | se a sessão chegou ao fechamento |
| `cancelada` | se a pessoa cancelou a sessão pelo botão Sair |
| `retomadas` | número de vezes que a sessão foi retomada ou reconstruída |
| `n_premissas` | número de premissas do tópico |
| `n_fechadas` | número de premissas concluídas na sessão |
| `n_respostas` | número de respostas (perguntas, passos e previsões) |
| `n_corretas` | número de respostas corretas |
| `ja_sabia` | premissas concluídas com resposta firme na abertura |
| `firmou` | premissas em que a pessoa estava insegura e confirmou |
| `aprendeu_agora` | premissas ensinadas pela escada e confirmadas em seguida |
| `corrigiu` | premissas em que a concepção errônea foi trabalhada pela demonstração e pelo treino |
| `em_aberto` | premissas cujo trabalho não se concluiu dentro do limite de telas |
| `ms_total` | soma dos tempos de resposta, em milissegundos |

## C.2 Tabela de premissas

A tabela `premissas.csv` tem uma linha por premissa aberta em cada sessão e reúne, lado a lado, o diagnóstico, o trabalho realizado e o resultado, que constituem a unidade de análise das questões V2 e V3 (Quadro C.2).

**Quadro C.2 — Colunas de `premissas.csv`**

| Coluna | Conteúdo |
| --- | --- |
| `participante` | código do participante |
| `topico` | código do tópico |
| `premissa` | identificador da premissa no tópico (B1, I2...) |
| `ordem` | posição em que a premissa foi aberta na sessão |
| `situacao_na_abertura` | situação atribuída à resposta da pergunta de abertura (Quadro C.4) |
| `confianca_na_abertura` | certeza declarada na pergunta de abertura |
| `trabalho` | intervenção realizada: "lacuna" (escada de passos), "crenca" (demonstração) ou vazio (nenhuma) |
| `crenca` | concepção errônea trabalhada ou registrada na premissa, pelo identificador do catálogo (Apêndice B) |
| `previsao_como_a_crenca` | se a previsão feita na demonstração foi a que a concepção errônea indica |
| `resultado` | como a premissa terminou: "ja_sabia", "firmou", "aprendeu_agora", "corrigiu" ou "em_aberto" (Quadro C.1) |
| `telas` | número de telas percorridas na premissa |
| `reconferencia` | resultado da pergunta da reconferência ao final do tópico: "assimilou", "nao_se_manteve", "a_ideia_voltou" ou "sem_questao" |

## C.3 Tabela de respostas

A tabela `respostas.csv` tem uma linha por resposta da pessoa, na ordem em que foram dadas (Quadro C.3).

**Quadro C.3 — Colunas de `respostas.csv`**

| Coluna | Conteúdo |
| --- | --- |
| `participante` | código do participante |
| `topico` | código do tópico |
| `seq` | posição do evento no registro da sessão |
| `ts` | data e hora da resposta |
| `premissa` | identificador da premissa |
| `tela` | tipo de tela: "pergunta", "passo" (da escada) ou "previsao" (da demonstração) |
| `papel` | papel da pergunta ("abertura", "reforco", "topo", "confirmacao" ou "reconferencia") ou do passo ("subida", "produzir", "treino" ou "reconferencia"); vazio na previsão |
| `item` | identificador da questão ou do passo |
| `versao` | versão do passo exibida (cada passo tem duas) |
| `tentativa` | número da tentativa no passo |
| `escolha` | posição da alternativa escolhida, na ordem da tela |
| `razao` | posição da razão escolhida, na ordem da tela |
| `resposta` | texto da resposta do passo ou da alternativa prevista |
| `correta` | se a resposta foi correta |
| `razao_correta` | se a razão escolhida foi a correta |
| `nao_sei` | se a pessoa respondeu "Não sei" |
| `confianca` | certeza declarada ("chutei", "acho que sei" ou "tenho certeza") |
| `confianca_rank` | a certeza em escala ordinal, de 1 a 3 |
| `crenca` | concepção errônea indicada pela alternativa ou pela razão escolhida |
| `como_a_crenca` | na previsão, se ela foi a que a concepção errônea indica |
| `situacao` | na pergunta, situação atribuída à resposta (Quadro C.4) |
| `ms` | tempo de resposta, em milissegundos |

## C.4 Valores da situação atribuída

As colunas `situacao_na_abertura` e `situacao` registram a situação atribuída a uma resposta de pergunta, com os valores do Quadro C.4, que correspondem às situações do Quadro 3.2.

**Quadro C.4 — Valores da situação atribuída a uma resposta**

| Valor | Situação (Quadro 3.2) |
| --- | --- |
| `confirmada` | sabe: resposta correta, razão correta e "tenho certeza" |
| `fragil` | acerto sem firmeza: resposta e razão corretas, sem certeza |
| `falso_positivo` | sinais divergentes: resposta correta pela razão de uma concepção errônea |
| `falso_negativo` | sinais divergentes: resposta incorreta pela razão correta |
| `lacuna` | não sabe: "Não sei", ou resposta incorreta com "chutei" |
| `crenca` | sustenta uma concepção errônea: resposta incorreta, pela razão de uma concepção errônea, com alguma certeza |

## C.5 Exemplo

O Quadro C.5 apresenta parte da tabela `premissas.csv` exportada da sessão de ensaio que produziu a tela de fechamento da Figura 3.3, no tópico kc_07. Trata-se de sessão de estudante simulado, e não de participante.

**Quadro C.5 — Exemplo de `premissas.csv`: sessão de ensaio da Figura 3.3**

| Premissa | Abertura | Concepção errônea | Resultado | Reconferência |
| --- | --- | --- | --- | --- |
| B1 | confirmada | | ja_sabia | |
| B2 | lacuna | | aprendeu_agora | assimilou |
| B3 | crenca | `array_passed_by_reference` | corrigiu | assimilou |
| B4 | confirmada | | ja_sabia | |
| I1 | crenca | `array_is_assignable` | em_aberto | a_ideia_voltou |
| I2 | lacuna | `sizeof_array_via_pointer` | em_aberto | nao_se_manteve |
| I3 | fragil | | firmou | |

Nas premissas B3 e I1, a previsão feita na demonstração foi a que a concepção errônea indica (coluna `previsao_como_a_crenca` igual a "sim"). Na premissa I2, a concepção errônea apareceu durante a escada, sem demonstração. O quadro omite, por espaço, as colunas de participante, tópico, ordem, certeza na abertura, trabalho e telas; nesse exemplo, a coluna `trabalho` traz "lacuna" nas premissas B2 e I2 e "crenca" nas premissas B3 e I1.
