# Revisão final total — o veredito da entrega

Artefato da fase 7, modo **completo**. Diferente das revisões de ciclo, que
olham o que mudou: esta olha o sistema inteiro e termina num veredito.

Entradas: [PRD.md](PRD.md) (os 12 critérios de sucesso e os requisitos),
[tasks.md](tasks.md) (ciclo 1), [tasks-ciclo-2.md](tasks-ciclo-2.md),
[revisao-ciclo-1.md](revisao-ciclo-1.md), [processo.md](processo.md).

O que esta revisão tem de diferente é que ela **executa**: sobe o sistema de
um clone do zero, derruba o servidor no meio de uma sessão, apaga o log e
restaura da cópia, volta uma versão, pede a exclusão de um participante e
atravessa a unidade do começo ao fim, três vezes dez. Nada aqui é opinião
sobre código.

---

## Veredito: **NO-GO para a coleta com participantes**

O sistema sobe, resiste a queda, restaura, reverte e valida o que entra. O
que impede a coleta não é o código: são **quatro achados P1**, e dois deles
não são software.

**GO para continuar o desenvolvimento e para um ensaio-piloto com você
mesmo.** A distinção importa: o instrumento funciona o bastante para ser
ensaiado, e não o bastante para ser aplicado em gente.

Nenhuma frase deste documento diz que o sistema é seguro, rápido, pronto
para produção ou em conformidade. Diz o que foi testado, o que passou, o
que falhou e o que **não** foi coberto.

---

## O P0: achado e fechado durante a revisão

O primeiro comando do primeiro ensaio falhou:

```
$ git clone . .../zero
fatal: cannot create directory at 'CUsers...midia': Filename too long
```

**O repositório não podia ser clonado no Windows.** Três arquivos estavam
versionados desde `75ac709` dentro de pastas cujo nome é um caminho Windows
literal. Eram **cópias byte a byte do log de desenvolvimento**: 925 KB cada,
1.503 linhas, 38 sessões, 23 linhas de texto livre de teach-back.

O `.gitignore` tem `mvp/dados/` e não casava com aqueles caminhos. A
varredura de segredos passou neles: a regra proibia `eventos.jsonl` e a
cópia datada se chama `eventos-20261029-133345.jsonl`. E o teste `-f` da
varredura nem abria os arquivos, porque o nome não resolve no sistema.

**A causa não foi descuido de quem digitou o comando.** O `copia.sh`
recebendo um caminho estilo Windows de quem não é shell: o MSYS não traduz
argumento assim, `mkdir -p` cria uma **pasta** com aquele nome no diretório
atual, `cp` escreve nela, e o script responde:

```
copiado e conferido
```

Código de saída 0. É o pior desfecho possível para um procedimento cuja
razão de existir é **perda tolerável zero** — e o mesmo engano esperava
quem chamasse o script do PowerShell com `D:\coleta`.

**Fechado em `d19f03b`**: os três arquivos fora do versionamento; o
`copia.sh` recusa destino em formato Windows, destino cuja pasta-mãe não
existe (mídia desmontada) e destino dentro do repositório; o
`participante.sh` recusa `--log` em formato Windows; o `verify.sh` ganhou
lista branca de caminhos e proíbe qualquer `.jsonl`; a área de teste saiu
de dentro do repositório, que foi o atalho que permitiu tudo isso. Cinco
sabotagens, cinco mordidas.

**O que fica em aberto, e é decisão sua:** os blobs continuam no histórico
local. Não há remoto, e o dado é de desenvolvimento, não de piloto — mas se
o repositório for publicado junto com o TCC, o log vai junto. Reescrever os
dois commits resolve e muda hashes citados nos documentos.

---

## Os quatro P1 que sustentam o NO-GO

### P1-1 · Uma premissa termina sem estado, e o instrumento não mede

**CS-10:** *"a unidade termina com toda premissa num dos cinco estados,
nenhuma indefinida"*. Trinta sessões atravessadas de ponta a ponta, três
personas:

| Persona | Passos | Estados finais | Sessões com premissa **sem estado** |
| --- | --- | --- | --- |
| acerta tudo | 37 | 50 confirmadas | **0 de 10** |
| erra e aprende com a refutação | 65–71 | 47 confirmadas, 3 desconhecidas | **3 de 10** |
| erra e não muda de ideia | 76–89 | 44 `em_aberto`, 6 desconhecidas | **6 de 10** |

**Nove sessões em trinta terminam com uma premissa que o sistema não
classificou.** E `em_aberto` — "o banco de itens acabou antes da sequência"
— é um sexto estado, que o PRD não nomeia.

A causa do `desconhecido` é a CS-2 funcionando **como foi desenhada**. No
rastro de uma sessão: nos dois itens de B1 a pessoa escolheu como razão a
crença `no_value_no_memory`, que nega **B2**. A crença foi para B2, que foi
validado, refutado, treinado e confirmado — correto. Só que B1 tem dois
itens de diagnóstico, os dois foram gastos, e **nenhum episódio foi
atribuído a B1**. B1 termina `desconhecido`: nem no mapa que a pessoa vê,
nem no dado que você vai analisar.

É a mesma raiz do achado da T12 (o banco não alimenta o reteste), e o
remédio é o mesmo e é seu: **mais itens por nó**, ou reservar um item no
momento da detecção. O teste automático de CS-10 passa porque o percurso
dele não cai nesse caso.

O caso do `em_aberto` é pior de ler: quem chega com as cinco concepções e
não muda de ideia termina com **zero premissas confirmadas** e cinco nós
cinzas. O instrumento degrada justamente na pessoa que ele mais quer medir.

### P1-2 · O pedido de exclusão não alcança as cópias

Ensaiado com um participante de verdade no log do clone. O `ver` mostrou
221 linhas, 4 com texto livre; o `apagar` tirou todas; as outras 38 sessões
ficaram intactas e reexecutáveis. Até aí, passou.

Depois, a mesma pergunta feita a todos os arquivos:

```
  120 linhas  eventos-20261029-154806.jsonl      (cópia na segunda mídia)
  120 linhas  eventos-20261029-155121.jsonl      (cópia na segunda mídia)
  120 linhas  eventos.jsonl.antes-de-apagar-...  (rede do próprio comando)
  120 linhas  eventos.jsonl.antes-de-apagar-...  (rede do próprio comando)
    0 linhas  eventos.jsonl                      (o log de verdade)
```

O participante pediu a exclusão e os dados dele continuam em **quatro
arquivos**. O PRD manda copiar o log **depois de cada sessão**, então o
número de cópias que guardam cada participante cresce com a coleta. O
`apagar` diz "apague a cópia quando o pedido estiver cumprido" — um
lembrete, que é exatamente a categoria de coisa que a R6 existiu para
eliminar.

### P1-3 · O termo de consentimento não existe, nem como rascunho

O PRD declara a base legal: *consentimento do participante, por escrito,
antes da sessão*, e diz que o termo e o aviso entram como rascunho para o
orientador e o comitê de ética. **Não há arquivo nenhum.** A palavra
"incidente" não aparece em documento algum do projeto: não há plano de
incidente.

Coletar dado pessoal de estudantes sem o termo escrito não é pendência de
engenharia. É o que impede a coleta de começar, independentemente do
estado do código.

### P1-4 · Dois commits não podem ser restaurados no Windows

Ensaio de reversão, no clone:

```
$ git checkout 71ebf25     → fatal: cannot create directory ... (fim do ciclo 2)
$ git checkout 75ac709     → fatal: cannot create directory ... (R6)
$ git checkout da92f9a     → ok                                 (R5)
```

Se a versão de hoje der problema no meio da coleta, a volta pula dois
commits. A correção é a mesma decisão do P0: reescrever o histórico.

---

## O que foi executado, e passou

### Operação (I)

| Ensaio | Resultado |
| --- | --- |
| **Subida do zero** | clone novo, `python -m pytest mvp/ -q` → **219 passed**; `python -m mvp.app` sobe e responde `/saude` |
| **Queda no meio da sessão** | servidor morto por PID na fase TREINO; reiniciado; a resposta seguinte foi servida em **127 ms** e a sessão foi até o mapa. O log registra `sessao_retomada TREINO` |
| **Restauração** | 38 sessões, impressão digital `ab14bed6…`; log apagado; painel passa a mostrar 0; restaurado da cópia; **mesma impressão digital**, 38/38 reexecutadas |
| **Reversão** | voltando para R5: 200 testes passam e as **39 sessões reexecutam com impressão digital idêntica** à da versão de hoje. Voltar não muda o significado do dado já coletado |

### Dados (M)

Os três invariantes do PRD, conferidos contra o domínio real: cada crença
nega exatamente um nó (5 de 5); toda crença aparece em alguma alternativa;
todo nó tem ao menos duas superfícies. CS-9 (domínio inválido falha na
carga) tem seis testes, cada um com um YAML que quebra uma regra.

O banco, por nó: **2 de diagnóstico + 2 de treino**, exatamente o parâmetro
aceito — e exatamente a causa do P1-1.

### Segurança (S)

- **Camada 0:** `.gitignore` cobre banco, token, backup e `mvp/dados/`.
  **Não há hook de pré-commit** — a varredura só roda quando alguém a chama
  (P2-1).
- **Camada 1:** nada em 106 arquivos versionados. No histórico, um achado:
  `data/export_token.txt` foi versionado em `0824410` e removido em
  `74f9bc7`, no mesmo dia. **O valor vazado não é o de hoje** — o arquivo
  foi regerado — e não há remoto. P2-2, pela mesma decisão do P0.
- **Camada 3:** validação de entrada, contra o servidor rodando:

  | Entrada | Resposta |
  | --- | --- |
  | `escolha: -1`, `999`, `3` numa tela de 3 opções | **400**, e nada gravado |
  | `escolha: 1.5`, `"a"` | 422 |
  | `ms` negativo, `ms` de 10¹² | 422 |
  | teach-back com 2.001 caracteres | 422 · com 2.000, 200 |
  | confiança fora da escala | 400 |
  | sessão inexistente, `../../../mvp/app.py` | 404 |

  O painel só responde GET. O código da sessão nunca entra num caminho de
  arquivo. Não há cabeçalho de CORS — e também não há `X-Frame-Options` nem
  CSP (P3).
- **Camada 4:** a lista do painel tolera linha ilegível e conta quantas; a
  reexecução continua estrita.

### Desempenho (D)

O PRD não tem meta numérica — a única que existia era o P1-B do ciclo 1.
Medido agora, em 1.832 chamadas de 30 sessões completas:

| | |
| --- | --- |
| `POST /sessoes/{id}/responder` | p50 **6,3 ms** · p95 **28,2 ms** · p99 **35,1 ms** · máx 129 ms |
| `GET /sessoes` do painel, 38 sessões, log de 1,6 MB | **36–67 ms** (era 966 ms antes da R2) |
| detalhe de uma sessão, com reexecução | **92 ms** |
| primeira resposta depois de uma queda | **127 ms** |

Nenhum número perto de incomodar alguém respondendo.

### Interface (U)

Medido na tela, não olhado:

- `lang="pt-BR"`, nenhum controle sem nome acessível, nenhuma imagem sem
  alt, nenhum `tabindex` positivo, uma região `aria-live="polite"`.
- **Ordem de tabulação limpa:** só os 4 controles visíveis entram. As telas
  ocultas não vazam foco.
- O SVG do mapa tem `role="img"` e `aria-label`. O rótulo é estático: diz
  que há um mapa, não o que está nele (P3).
- **Nenhum texto abaixo de 4,5:1** de contraste, nas duas telas.
- O `textarea` do teach-back tem `maxlength="2000"` e nome acessível.
- **"Não sei" tem peso de opção**, como o PRD exige: mesma caixa, mesma
  borda, mesmo tamanho, mesmo peso de fonte; só a cor do texto é mais suave
  (7,5:1, acima do mínimo). A impressão de que ele parecia mais fraco não
  se sustentou na medição.
- No painel, **9 `<th>` sem `scope`** e tabela sem `<caption>` (P3, já
  conhecido e deixado de fora do ciclo 2 de propósito).

---

## O que **não** foi coberto

Isto não é lista de desculpas: é o que o veredito não cobre.

1. **CS-11 e CS-12 continuam sem evidência.** Nenhuma pessoa real
   atravessou a unidade. As trinta sessões foram feitas por um programa que
   conhece o gabarito; ele prova que o sistema termina, não que alguém
   entende a tela. O PRD já dizia que o computador não prova estes dois.
2. **Nenhum teste de usabilidade com pessoas**, e nenhum guia testado com
   alguém de fora. O portão T está cumprido no que é verificável (todos os
   comandos do README foram executados nesta revisão) e vazio no que exige
   gente.
3. **A instalação das dependências não foi exercitada offline.** O ensaio de
   subida do zero usou os pacotes já instalados. `pip install -r
   requirements.txt` precisa de internet, e a máquina da coleta é offline:
   se ela for reinstalada na véspera, não há rodas guardadas localmente.
4. **A varredura de segredos não é gitleaks.** É um substituto por padrões,
   e o próprio script diz isso. Pega o que vaza na prática; não substitui a
   ferramenta.
5. **Concorrência não foi testada.** O desenho é de um participante por
   vez; duas sessões simultâneas escrevendo no mesmo arquivo nunca foram
   exercitadas.
6. **O conteúdo das 20 atividades não foi revisto por autor de domínio.**
   Continua pendente desde o ciclo 1.
7. **O dicionário de sessões em memória nunca é limpo** (P3 conhecido).
8. O caminho **"lacuna → constrói"** aparece no fluxo do PRD e não tem
   tarefa em nenhum ciclo.

---

## Vereditos por auxiliar

| Auxiliar | Modo | Veredito |
| --- | --- | --- |
| **S** segurança | completa, camadas 0 a 4 | **parcial** — P0 fechado na revisão; P2 do hook de pré-commit e do token no histórico; camadas 1, 3 e 4 limpas |
| **D** desempenho | completa | **passou** — nenhuma operação perto de incomodar; sem meta no PRD para comparar |
| **M** dados | completa | **passou** — invariantes de pé, CS-9 coberto, restauração com impressão digital idêntica |
| **G** privacidade | completa | **falhou** — P1-2 (exclusão não alcança as cópias) e P1-3 (termo e plano de incidente inexistentes) |
| **U** interface | completa | **parcial** — acessibilidade e teclado medidos e em ordem; sem teste com pessoas, CS-11 em aberto |
| **I** operação | completa | **parcial** — quatro ensaios passaram; P1-4 na reversão e a instalação offline não exercitada |
| **T** documentação | completa | **parcial** — todos os comandos executados; README corrigido (212→219 testes, 4→5 crenças); guia nunca testado com pessoa de fora |
| **E** pós-entrega | completa | **não aplicável como canal** — não há usuários depois da entrega; quem relata é o participante, na sessão, para você |
| **P** dados sensíveis | dentro de G | ver G |
| **X**, **W** | — | não aplicáveis, pelo perfil |

---

## As decisões que são suas

1. **O histórico:** reescrever os dois commits (tira os blobs do log,
   destrava a reversão, muda hashes citados nos documentos) ou aceitar como
   está e nunca publicar o repositório.
2. **O banco de itens:** mais itens por nó, ou reservar um item no momento
   da detecção. É a raiz do P1-1 e do achado da T12.
3. **O `em_aberto`:** nomear como sexto estado no PRD, ou tratá-lo como
   defeito a eliminar.
4. **A exclusão e as cópias:** um comando que varre as cópias, ou um
   procedimento escrito com uma lista de onde elas estão.
5. **O termo e o aviso:** quem escreve o rascunho e quando ele vai ao
   orientador e ao comitê.
6. **As 20 atividades:** quem é o autor de domínio que as revisa.
