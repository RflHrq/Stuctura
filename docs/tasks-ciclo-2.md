# Tarefas — ciclo 2

**Fechado.** Seis tarefas, seis commits, de `8ebafb0` a `15cd3c3`.

Artefato da fase 5 do segundo ciclo. Fecha os oito achados da
[revisão do ciclo 1](revisao-ciclo-1.md): dois P1 e seis P2.

Nenhuma destas tarefas muda desenho, e nenhuma toca o motor de
aprendizagem. São a fronteira do sistema — o que entra, o que sai, e o
que acontece quando algo quebra.

**Portões** (a tarefa não fecha sem eles): **S** segurança · **D**
desempenho · **M** dados · **G** privacidade · **U** interface ·
**I** operação · **T** documentação. Em todo commit, sem exceção:
varredura de segredos e sabotagem antes de acreditar em teste verde.

---

## R1 — A entrada inválida para de virar dado  · P1-A, P2-A

**O que muda:** `{"escolha": -1}` deixa de ser aceito como resposta.

Hoje devolve 200 e vira um episódio válido com a última alternativa — a
crença daquela opção entra no registro e nada no log distingue isso de
uma resposta de verdade. `{"escolha": 999}` derruba a requisição.

**Arquivos prováveis:** `mvp/motor.py`, `mvp/app.py`.

**Pronto quando:** índice fora de `0 <= i < len(opcoes)` é requisição
inválida (400), e o motor estoura alto em vez de indexar de trás para
frente. Nenhum episódio é gravado.

**Teste:** `-1`, `999` e `1.5` em cada camada; e nenhum evento de
episódio no log depois de qualquer um deles.

**Portões:** S, M.

**Feito** (`8ebafb0`). As três camadas passam por `_indice()`: `None` vale, índice que existe vale, o resto estoura `EscolhaInvalida` e a rota devolve 400. A camada 2 tinha o mesmo defeito por outro caminho — índice fora da faixa virava `None`, e `None` na razão é lacuna; um erro de cliente entrava na base como alguém declarando que não sabe. A revisão não tinha visto esse.

---

## R2 — A lista do painel para de reexecutar  · P1-B

**O que muda:** abrir o painel deixa de custar uma reexecução por sessão.

Hoje são 966 ms com 36 sessões, de 3 em 3 segundos, no mesmo computador
que atende quem está respondendo.

A lista mostra o que o log diz literalmente — código, horários, respostas,
retomadas, encerrada. A **fase** exige reexecução e pertence ao detalhe,
que já é de uma sessão por vez.

**Arquivos prováveis:** `mvp/painel.py`, `mvp/web/painel.html`.

**Pronto quando:** `sessoes()` não chama `reconstroi`, e o arquivo é lido
uma vez por chamada.

**Teste:** a rota `/sessoes` não reexecuta — com `reconstroi` sabotado
para estourar, a lista continua respondendo. E a medida antes/depois, com
o mesmo log.

**Portões:** D, U.

**Feito** (`3f0023e`). 966 ms → **7 ms**, no mesmo log. A fase saiu da lista; `reexecutavel` é apurado sem reexecutar, e isso é uma aproximação declarada — quem decide é o detalhe. Apareceu junto uma consequência da R1: logs do ciclo 1 têm entradas que o motor de hoje recusa, e reexecutá-las estourava erro de servidor; agora vira 409 com o motivo.

---

## R3 — Limite no que entra  · P2-B

**O que muda:** o teach-back passa a ter tamanho máximo, dito à pessoa, e
`ms` não aceita número impossível.

Hoje 200.000 caracteres são aceitos e gravados. É dado pessoal sem limite
escrito em disco, e número impossível entrando na base de análise.

**Arquivos prováveis:** `mvp/app.py`, `mvp/web/index.html`.

**Pronto quando:** o corpo da requisição recusa texto acima do limite e
`ms` negativo; a tela diz o limite antes de a pessoa escrever.

**Teste:** o limite exato, um caractere acima, e `ms` negativo.

**Portões:** G, M, U.

**Feito** (`d500edd`). Teto de 2.000 caracteres no teach-back, `0 <= ms <= 2h`, e a tela diz o limite com um contador que só aparece nos últimos 200 — contador que grita o tempo todo compete com a pergunta.

---

## R4 — O painel sobrevive a uma linha corrompida  · P2-C

**O que muda:** uma linha ilegível deixa de esconder as outras sessões.

O painel existe, entre outras razões, para funcionar **depois** de um
travamento. Perder 36 sessões por causa de uma linha é o oposto disso.

**Arquivos prováveis:** `mvp/log.py`, `mvp/painel.py`,
`mvp/web/painel.html`.

**Pronto quando:** a lista tolera e **conta** linhas ilegíveis, e diz
quantas na tela. A reconstrução continua estrita — pular uma entrada lá
produz estado plausível e errado, e isso é garantia da T10.

**Teste:** linha corrompida no meio: a lista responde e avisa; a
reconstrução daquela sessão continua estourando.

**Portões:** S.

**Feito** (`4fb254d`). `log.le_tolerante()` pula linhas ilegíveis e **conta** quantas; a tela mostra o número. A reconstrução continua estrita, que é garantia da T10.

---

## R5 — O log diz em que versão foi escrito  · P2-D

**O que muda:** cada linha passa a carregar a versão do formato.

O formato já mudou duas vezes neste ciclo (T10 acrescentou
`entrada_recebida`, T12 acrescentou `belief_retested`) e a única pista é
a ausência de campos. Com coleta em andamento e código evoluindo, é o
caminho curto para uma análise que mistura formatos sem perceber.

**Arquivos prováveis:** `mvp/log.py`.

**Pronto quando:** toda linha nova tem versão; linhas antigas, sem o
campo, continuam legíveis e aparecem como anteriores à versão 1.

**Teste:** a versão chega ao arquivo; um log misto é lido sem erro e
distingue as duas origens.

**Portões:** M.

**Feito** (`5489db2`). Campo `v` em toda linha nova; linha sem o campo é lida como `VERSAO_ZERO`. Um log misto continua legível e separa as duas origens — que é o caso do arquivo de desenvolvimento aqui.

---

## R6 — Apagar um participante, e copiar depois da sessão  · P2-E, P2-F

**O que muda:** os dois procedimentos que o PRD exige passam a existir
como comando, e não como lembrete.

O PRD declara que *"o participante pode pedir a exclusão dos dados dele
pelo código"* — não há mecanismo. E exige que *"depois de cada sessão, o
log vai para uma segunda mídia"*, com perda tolerável zero — não há
script.

**Arquivos prováveis:** `scripts/participante.sh` (novo),
`scripts/copia.sh` (novo), `mvp/README.md`.

**Pronto quando:** apagar um código remove **todas** as linhas dele e
nenhuma de outro; copiar confere o que copiou.

**Teste:** apagar num log de teste com três sessões deixa duas intactas;
a cópia bate byte a byte.

**Portões:** G, I, T.

**Feito** (`15cd3c3`). `scripts/participante.sh` e `scripts/copia.sh`, com teste que roda os scripts de verdade. Três cuidados no apagar: código comparado campo a campo (apagar `P1` não leva `P10`), linha ilegível fica, confirmação errada não apaga nada.

---

## Fora deste ciclo, de propósito

- Os **P3** da revisão: `<th>` sem `scope`, o `aria-label` do SVG, o
  dicionário de sessões que não é limpo.
- O **ensaio de restauração**: é da revisão final total, e backup que
  nunca foi restaurado não conta como backup.
- As decisões de **conteúdo** que a fase 6 levantou: o banco de itens não
  alimenta o reteste; "lacuna → constrói" não tem tarefa; as 20
  atividades precisam de revisão do autor do domínio.
