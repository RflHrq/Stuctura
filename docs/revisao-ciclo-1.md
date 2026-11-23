# Revisão do ciclo 1 — fase 7

Artefato da fase 7. Revisão **focada**: só o que as treze tarefas da fase
6 mudaram (`8291fe0..d9d65c9`), não o sistema inteiro. A revisão completa
é a final, e ainda não aconteceu.

**O que foi revisado:** `mvp/motor.py`, `mvp/log.py`, `mvp/app.py`,
`mvp/painel.py`, `mvp/web/`, `scripts/verify.sh` — 4.844 linhas
acrescentadas, 160 removidas, em 24 arquivos.

**Linha de base:** 428 testes verdes (176 do MVP, 252 da suíte antiga),
nenhum segredo em 98 arquivos versionados.

**O que isto NÃO diz.** Não diz que o sistema está seguro, rápido, pronto
ou em conformidade. Diz o que foi testado, o que passou, o que falhou e o
que ficou sem cobertura.

---

## Veredito

**Parcial.** Dois P1 e seis P2. Nenhum P0 — nenhum segredo vazou, nenhum
dado de participante saiu da máquina, e as treze tarefas fazem o que os
commits dizem que fazem.

Os dois P1 **precisam estar fechados antes de qualquer coleta com
pessoas**. Um deles contamina o dado do instrumento em silêncio, que é o
pior tipo de defeito que este sistema pode ter.

---

## P1 — fechar antes da coleta

### P1-A · Um índice negativo vira um episódio válido

**Onde:** [mvp/motor.py](../mvp/motor.py) na camada 1, e
[mvp/app.py](../mvp/app.py) que não valida a entrada.

```
POST /sessoes/{s}/responder  {"escolha": -1}   →  200
```

`a.opcoes[r.escolha]` com `-1` devolve a **última alternativa**. O
episódio é classificado, a crença daquela alternativa entra no registro,
e a sessão segue para a tela de confiança como se a pessoa tivesse
escolhido. Nada no log distingue isso de uma resposta de verdade.

A camada 2 já se defende (`0 <= r.escolha < len(p.razoes)`). A camada 1,
não — a assimetria é o próprio defeito.

**Por que é P1 e não P2:** não derruba nada, e é justamente por isso.
Um 500 aparece; um dado inventado não. Numa coleta de 10 a 15 pessoas,
um episódio falso é irreparável, porque a pessoa não volta.

**Como fechar:** rejeitar na fronteira — índice fora de
`0 <= i < len(opcoes)` é requisição inválida (400), e o motor estoura
alto em vez de indexar de trás para frente.

### P1-B · O painel custa quase um segundo por atualização, e pede de 3 em 3

**Onde:** `painel.sessoes()`, que chama `log.reconstroi` para **cada**
sessão só para saber a fase — e cada reconstrução relê e reparseia o
arquivo inteiro.

Medido nesta máquina, no log de desenvolvimento:

| | |
| --- | --- |
| sessões no arquivo | 36 |
| linhas no arquivo | 1.472 |
| tempo da rota `/sessoes` | **966 ms** |
| intervalo de atualização da tela | 3 s |

São 36 leituras completas do arquivo e 36 reexecuções a cada ciclo, e o
custo cresce com a coleta. O computador que roda o painel é o **mesmo**
que atende quem está respondendo.

**Por que é P1:** a tabela de riscos do PRD diz, com todas as letras,
*"o painel atrapalhar a sessão — observar não pode custar o dado"*. A
decisão 10 separou os processos para que uma consulta minha não custasse
um participante; gastar CPU em laço vai pelo mesmo caminho, por outra
porta.

**Correção do perfil do projeto.** O desempenho (**D**) estava registrado
como *não aplicável*. Este achado mostra que não é: o painel introduziu
uma consulta repetida sobre um arquivo que cresce. O perfil precisa ser
corrigido, e é a primeira vez neste processo que um "não aplicável" se
revelou errado.

**Como fechar:** a lista não precisa reexecutar nada. O que vem direto do
log — código, horários, nº de respostas, retomadas, encerrada — basta
para escolher uma sessão. A **fase** exige reexecução e pertence ao
detalhe, que já é de uma sessão por vez. Trocar a fase por "encerrada /
em andamento" na lista elimina as 36 reexecuções sem reimplementar regra
nenhuma.

---

## P2 — fechar antes da entrega

### P2-A · Índice fora da faixa derruba a requisição

```
POST /sessoes/{s}/responder  {"escolha": 999}   →  500
{"escolha": 1.5}                                →  500
```

Menos grave que o P1-A porque aparece, e porque desde a T10 a sessão
volta. Mas um 500 no meio de alguém pensando em voz alta custa a linha de
raciocínio. Mesma correção do P1-A.

### P2-B · O teach-back não tem limite, e `ms` aceita negativo

200.000 caracteres foram aceitos e gravados no log. `ms: -5` também.

É **dado pessoal sem limite de tamanho escrito em disco** (portão G) e
número impossível entrando na base de análise (portão M). Nenhum dos dois
derruba nada; os dois sujam.

**Como fechar:** limite no corpo da requisição e `maxlength` na tela, com
o limite dito à pessoa; `ms` não-negativo.

### P2-C · Uma linha corrompida esconde as outras 35 sessões

`painel.sessoes()` não trata `LinhaCorrompida`: uma linha ilegível no
meio do arquivo derruba a **lista inteira**.

O painel existe, entre outras razões, para funcionar **depois** de um
travamento (decisão 10). Perder 36 sessões por causa de uma linha é o
oposto disso.

**Como fechar:** a lista tolera e **conta** linhas ilegíveis, dizendo
quantas na tela. A reconstrução continua estrita — pular uma entrada lá
produziria estado plausível e errado, e isso é garantia da T10.

### P2-D · O log não tem versão de formato

Os eventos já mudaram de forma duas vezes neste ciclo (T10 acrescentou
`entrada_recebida`, T12 acrescentou `belief_retested`). Nenhuma linha diz
em que versão foi escrita, e a única pista é a ausência de campos.

Com uma coleta em andamento e o código evoluindo, é o caminho curto para
uma análise que mistura formatos sem perceber.

**Como fechar:** um campo de versão em cada linha. Barato agora,
impossível depois.

### P2-E · O direito de exclusão está declarado e não existe

O PRD diz: *"o participante pode pedir a exclusão dos dados dele pelo
código"*. Não há mecanismo — só editar o arquivo à mão.

Para um estudo de graduação, um comando que apaga as linhas de um código
provavelmente basta. Mas declarar um direito e não ter como exercê-lo é
um problema de **conformidade**, não de conveniência, e o texto vai ao
comitê de ética.

**Como fechar:** um comando curto, e o procedimento escrito.

### P2-F · A cópia depois de cada sessão não existe

O PRD exige: *"depois de cada sessão, o log vai para uma segunda mídia"*,
com **perda tolerável zero**. Não há script, não há procedimento escrito,
e `scripts/` só tem `verify.sh`.

Hoje a proteção contra perder uma coleta inteira é lembrar de copiar um
arquivo.

**Como fechar:** um comando que copia e confere, e o ensaio de
restauração — que é da revisão final. Backup que nunca foi restaurado não
conta como backup.

---

## P3 — anotados, não urgentes

- `<th>` sem `scope` na tabela do painel.
- O `aria-label` do SVG do mapa descreve a figura, não os estados —
  débito registrado desde a T7.
- O dicionário de sessões em memória nunca é limpo. Irrelevante na escala
  do estudo; seria vazamento num serviço longo.

---

## O que NÃO foi coberto

Importa tanto quanto o que foi.

- **Nenhum teste com pessoas.** CS-11 e CS-12 não são automáticos, e
  continuam sem evidência. Nada aqui diz que a interface é usável.
- **Nenhuma medida de tempo de sessão.** O risco do PRD — "10 itens × 3
  telas cansa, e cansaço vira chute" — segue sem número.
- **Nenhum ensaio de restauração.** É da revisão final.
- **As 20 atividades não foram revisadas quanto ao conteúdo.** Dez foram
  escritas aqui e alimentam a medição; a revisão é do autor do domínio.
- **A suíte antiga (252 testes) não foi auditada.** Ela passa; não foi
  lida nesta revisão.
- **Nenhuma skill auxiliar foi invocada.** O método de S, U, M, G e T foi
  aplicado direto, como nas fases anteriores. A lacuna fica registrada:
  uma auditoria de segurança de verdade, em modo completo, é da revisão
  final.

---

## Portões, um a um

| Portão | Veredito | O que sustenta |
| --- | --- | --- |
| **S** segurança | **parcial** | camada 0 e 1 limpas: nenhum segredo em 98 arquivos versionados, `mvp/dados/` fora do versionamento, os dois servidores em `127.0.0.1`, sem CORS. Camada 3: **P1-A** e **P2-A** na validação de entrada; **P2-C** em disponibilidade |
| **D** desempenho | **falhou** | **P1-B**. E o perfil do projeto, que dizia "não aplicável", estava errado |
| **U** interface | **parcial** | toda escolha é `<button>`, alcançável por Tab e Enter; símbolo antes de cor nos sete estados. Não testada com pessoas, e os P3 de acessibilidade continuam abertos |
| **M** dados | **parcial** | invariantes cobradas na carga, log append-only, reconstrução com guardas. **P2-B** e **P2-D** |
| **G** privacidade | **parcial** | aviso antes do texto livre, identificação só por código, lista do painel sem texto de participante, painel em `127.0.0.1`. **P2-B** e **P2-E** |
| **T** documentação | **parcial** | o README do MVP acompanha as treze tarefas e declara os limites. Faltam os procedimentos de operação: cópia (**P2-F**) e exclusão (**P2-E**) |
| **I** operação | **parcial** | sobe com um comando, roda offline. **P2-F**, e o ensaio de restauração é da revisão final |
| **P**, **X**, **W**, **E** | não aplicáveis | perfil do projeto |

---

## O que isto propõe

Pela regra do processo, P1 aberto manda abrir um **ciclo 2 de tarefas**.
Os dois P1 e os seis P2 são pequenos e localizados — nenhum pede mudar
desenho, e nenhum pede tocar no motor de aprendizagem.

A decisão de escopo é do dono: o que entra no ciclo 2, o que fica para
depois da coleta, e o que é aceito como está.
