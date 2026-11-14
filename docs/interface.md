# A interface do Structura — identidade, caminho e cenas

Desenho aprovado em conversa com o Rafael em 14/11/2026. Os esboços
que ele viu e escolheu estão em `docs/esbocos/` (abrem direto no
navegador, sem servidor). Este documento é o que um construtor precisa
para planejar sem voltar a perguntar; o que está marcado **(decisão
minha)** o Rafael ainda pode corrigir.

## 1. A intenção

O Rafael jogou a sessão nova da trilha e aprovou o rumo pedagógico: a
sessão descobre se a pessoa sabe, não sabe ou "pensa que sabe, mas não
sabe", e corrige. Esse comportamento **não muda** aqui. O que ele pediu
em seguida foi a cara do sistema:

1. **O caminho à vista.** "O conhecimento é progressivo: primeiro você
   tem que saber declarar variável, depois…" A página inicial deixa de
   ser uma lista numerada solta e mostra o caminho natural entre os
   tópicos, desenhado "como um grafo", "um caminho que ele possa
   percorrer". A ordem é **sugerida**: todos os tópicos ficam abertos.
2. **Ilustração que explica.** "As imagens seriam mais para explicar",
   com "um entendimento mais empírico", para "quem tem esse pensamento
   mais lúdico, que precisa fazer mais essas analogias". Arte, e não
   diagrama de quadro: "mais artístico, e mais animado", com a mesma
   pegada de transformação dos vídeos. Não precisa ser uma analogia só:
   "se a gente tiver uma analogia já pronta, é só pegar e ilustrar".
3. **Um sistema apresentável, com cara de programação.** Um logo, menos
   branco "muito básico", "uma pegada um pouco mais de programação".

## 2. Objetivos, não objetivos, anti-objetivos

**Objetivos**

- Identidade nova: logo, ícone de aba, dois temas (escuro e claro),
  fontes, cantos, brilhos — em todas as telas da trilha e na página
  inicial.
- As telas da trilha refeitas nessa identidade, com o código em cores.
- O caminho dos treze tópicos desenhado na página inicial.
- Uma cena ilustrada e animada por ideia, que anda junto com o código,
  linha por linha, e que o conferidor confere contra o compilador.

**Não objetivos**

- Mudar as regras da sessão, as escadas, as provas ou o que é gravado
  em `coleta/`. As telas mudam de roupa; o que a pessoa responde e o que
  a página manda ao servidor continua o mesmo. A única mudança do lado
  do servidor é ele passar a mandar a cena (seção 8) junto com a revisão
  e com a explicação — dado a mais na tela, sem regra nova; por isso a
  versão das regras do registro (`trilha_log.VERSAO`) não muda.
- O fluxo anterior (`/kc/<tópico>/`, `index.html`, `app.js`) e o painel
  do pesquisador (`painel.html`). Ficam como estão; só o link de
  "versão anterior" continua acessível pela página inicial.
- O modo Praticar (exercício rápido, só certo e errado), que continua
  por fazer, em outro desenho.

**Anti-objetivos — se acontecer, falhou mesmo funcionando**

- Uma cena mostrar algo que o código não faz. É a promessa do sistema:
  "a máquina respondeu" é sempre verdade.
- A animação atrapalhar a leitura ou não parar para quem marcou
  "reduzir movimento" no sistema operacional.
- O sistema passar a depender de internet, de serviço externo ou pago.
  Ele roda no laboratório, sem rede.
- O caminho trancar tópicos. A ordem é sugestão.
- A sessão perder o diagnóstico (a pergunta com razão e certeza no
  começo de cada ideia) por causa de algo da interface.

## 3. Restrições

- **Sem dependência externa.** Nenhum arquivo carregado de outro
  endereço; nenhuma biblioteca de animação. Desenho em SVG feito por
  código e movimento por CSS (e, onde precisar de sequência, pela API de
  animação do próprio navegador), como as figuras de hoje (`figuras.js`
  já segue essa regra).
- **Fontes guardadas no projeto**, de licença livre (OFL). Baixar o
  arquivo da fonte é um download e **pede a autorização do Rafael antes**
  (seção 10). Sem a fonte, a pilha de fontes do sistema serve.
- **Contraste** de texto AA (4,5:1 para texto comum, 3:1 para texto
  grande e ícones) nos dois temas.
- **Telas pequenas.** Tudo funciona a partir de 360 px de largura, sem
  rolagem lateral.
- **Testes de hoje continuam valendo.** Nove arquivos de teste leem as
  páginas (`test_trilha_telas.py`, `test_trilha_portal.py`,
  `test_trilha_diagnostico.py`, entre outros). Assets continuam com
  versão no endereço (`?v=…`), e o teste que confere isso continua.
  Teste existente não é alterado para passar; se um precisar mudar
  porque descrevia o visual antigo, isso é dito ao Rafael antes.
- **O fluxo anterior não muda de cara.** `index.html` e `app.js` usam
  `style.css`, que hoje também é carregado pela trilha e pela página
  inicial. A identidade nova não pode quebrar o fluxo anterior: ou ela
  mora numa folha de estilo nova, carregada só pela trilha e pela página
  inicial, ou o que mudar em `style.css` é conferido também no fluxo
  anterior. A escolha é do construtor.
- **Cor nunca é a única informação.** As paradas (feita, agora, depois)
  e as alternativas marcadas também dizem o estado em texto para leitor
  de tela e com forma (sinal de certo, contorno), não só com a cor.
- **Dados.** Nada da interface grava em `coleta/`; ensaio usa
  `ensaios/`. O código do participante continua anônimo.

## 4. As abordagens consideradas

**Telas, tema e caminho — um jeito só faz sentido:** refazer o visual
das páginas que já existem, no mesmo código simples de hoje (HTML, CSS e
JavaScript sem framework). Reescrever com uma ferramenta nova
quebraria os testes atuais e daria muito trabalho sem mudar nada do que
a pessoa vê.

**As cenas — três caminhos:**

1. **Cada cena desenhada à mão.** Liberdade artística total; 80 desenhos
   para manter; nada confere a cena contra o código, e uma mudança no
   trecho deixa a cena errada sem ninguém ver.
2. **Cena descrita em dados, ao lado da escada, e um desenhista único
   que anima todas** — **a escolhida pelo Rafael.** Mesmo estilo em
   todas, e o conferidor confere, linha a linha, que a cena mostra o
   que o programa faz. Custa construir o desenhista primeiro, e a arte
   fica limitada aos personagens que ele sabe desenhar; personagem novo
   entra quando um tópico pedir, e uma cena isolada pode ser feita à mão.
3. **Biblioteca de animação pronta (a dos vídeos).** Efeitos mais ricos
   com menos código, mas é dependência externa, com licença própria, e o
   sistema tem de rodar sem rede.

## 5. A identidade (decidido pelo Rafael)

- **Logo: o "S que é um ponteiro"** — a letra S desenhada como o
  caminho de uma seta que termina numa caixinha laranja, dentro de um
  quadrado de cantos redondos (esboço 3, opção B). Versão para cada tema
  e ícone de aba (favicon) em SVG.
- **Modo escuro = "noite de editor"** (esboço 5, A): fundo azul-noite com
  pontilhado discreto, cartões um tom acima, as cores do código como cores
  da interface, e **brilhos** suaves no que está selecionado, no próximo
  passo e no botão principal.
- **Modo claro = "moldura de terminal"** (esboço 5, B): topo escuro como
  janela de terminal, fundo de papel quadriculado no lugar do branco,
  cartão claro com a borda esquerda em degradê, botão principal laranja.
- **Rótulos com cara de código** nos dois: "// ideia 1 de 5 · pergunta"
  no escuro, "/* ideia 1 de 5 */" no claro, em fonte monoespaçada.

**Decisões minhas, dentro disso:**

- O tema segue o do sistema operacional na primeira visita, e há um
  botão no topo para trocar; a escolha fica lembrada no navegador
  (`localStorage`, com a página funcionando se ele não existir).
- As cores são variáveis de CSS por tema, com estes papéis (os valores
  dos esboços são o ponto de partida): fundo, cartão, linha, texto,
  texto secundário, primária (azul/petróleo), destaque (laranja — o
  próximo, a certeza escolhida), bilhete (amarelo), acerto (verde), erro
  (vermelho), e as cinco cores do código (palavra-chave, número, função,
  texto entre aspas, comentário).
- Fontes: uma sem serifa arredondada para a interface e uma mono para
  código e rótulos — proposta: **Nunito** e **JetBrains Mono**, ambas
  OFL, guardadas em `mvp/web/fontes/` (seção 10).

## 6. As telas

Todas as telas da trilha (`trilha.html`, `trilha.css`, `trilha.js`) e a
página inicial (`portal.html`) ganham a identidade. Por tela:

- **Topo, em todas:** logo, nome do tópico, as ideias do tópico como
  **paradas** numeradas ligadas por um fio (verde = feita, laranja com
  brilho = agora, contorno = depois), Ajustes e a troca de tema. Hoje o
  topo já recebe o estado de cada ideia do servidor (`progresso`); muda
  o desenho, não o dado.
- **Código, em todas as telas que mostram código:** moldura de editor
  (três pontinhos no alto), e cores por um realce próprio, pequeno:
  palavras-chave do C, números, textos entre aspas, comentários e nome
  de função antes de "(". O texto que a pessoa lê é o mesmo, caractere
  por caractere — o realce só envolve pedaços em `<span>`.
- **entrada:** a escolha do ritmo e o Começar, no cartão novo.
- **pergunta:** código, pergunta, alternativas em botões grandes,
  "Por quê?", certeza em três botões redondos, Responder e Não sei
  (esboço 4, tela 2).
- **degrau:** as formas de produzir (tocar, montar, escolher, completar,
  digitar) com o mesmo vocabulário visual; peças de montar como blocos
  de código.
- **retorno:** acerto com uma animação curta (o sinal de certo
  aparecendo); erro com a correção e, quando houver, a cena.
- **voce_disse e maquina (a prova):** "Você disse" num balão; a previsão;
  na tela da máquina, a saída numa moldura de terminal, o "você previu",
  e o que a prova mostra. (A cena da prova é a seção 8.4.)
- **revisao:** o texto da ideia, o código e **a cena**.
- **mapa (o fechamento):** o resumo de hoje, nos cartões novos, e o
  caminho das ideias do tópico desenhado como as paradas do topo, todas
  marcadas.
- **O painel de explicação** ("Ver a explicação"): a ideia, o código e
  **a cena**, no lugar da figura do hotel.

## 7. O caminho na página inicial

**Decidido pelo Rafael:** ordem sugerida, todos abertos, desenhado como
um caminho que se percorre.

**Decisões minhas:**

- **Estilo: a trilha de jogo** (esboço 2, opção A; esboço 4, tela 1): um
  caminho sinuoso de cima para baixo, uma parada por tópico, e no fim o
  caminho se abre em três. Ao lado, em telas largas, o cartão "Próximo
  sugerido" com o botão Começar; em telas estreitas, o cartão vem acima
  da trilha.
- **A ordem sugerida** fica num arquivo do domínio,
  `mvp/dominio/caminho.yaml`, e não no HTML:
  `kc_00, kc_02, kc_03, kc_04, kc_05, kc_06, kc_07, kc_01, kc_08, kc_09`,
  e no fim os três que não dependem um do outro: `kc_10, kc_11, kc_12`.
  Um teste confere que todo tópico existe uma vez e que cada um vem
  depois de todos os pré-requisitos dele (`prerequisites` em
  `topic_kcNN.yaml`). O portal manda essa ordem em `/topicos`.
- **Estado de cada parada:** "feito" quando a pessoa chegou ao
  fechamento daquele tópico neste navegador; "próximo" é o primeiro da
  ordem ainda não feito; o resto, "aberto". Fica guardado no navegador,
  como o "já aberto" de hoje — numa máquina de laboratório compartilhada,
  o código do participante não muda isso (limitação dita na tela de
  ajuda, se houver, e no relatório).
- Cada parada é um link para o tópico; a "versão anterior" (fluxo antigo)
  continua num link discreto, dentro do cartão do tópico.
- O código do participante sai do meio da página e vai para um campo no
  topo, com o mesmo comportamento e a mesma validação de hoje.

## 8. As cenas

### 8.1 O que é

Uma cena por ideia, que anima o **código da revisão** daquela ideia
(`revisao.codigo` na escada — de três a nove linhas, e todas já rodam no
compilador): a linha que está rodando fica marcada no código, e a cena
mostra o que ela fez. Ela aparece na revisão, no painel de explicação e
no retorno de erro da pergunta de topo. Ao fim, a cena para no último
estado, com um botão de rever.

A analogia é a que o texto daquela ideia já usa. Medido no conteúdo de
hoje: a **caixa** aparece nos 13 tópicos e é a espinha; por cima, a
**rua e as casas** (kc_01, kc_04, kc_06, kc_07), o **papel** com o número
(kc_04), a **viagem** até o endereço (kc_04, kc_05), o **pedaço alugado**
(kc_08, kc_09), as **quadras** (kc_01), a **fileira** (kc_10). O hotel
das figuras antigas sai.

### 8.2 Os personagens do desenhista (primeira leva)

- **caixa** — de papelão, aberta em cima; etiqueta na frente (o nome),
  carimbo na lateral (o endereço, de exemplo), e o valor como uma
  bolinha que aparece dentro. Sem valor escolhido: a caixa mostra "?"
  meio apagado ("sobra").
- **bilhete** — o ponteiro: um papel dentro da caixa do ponteiro com
  "vá até a nº …"; ao seguir o ponteiro (`*p`), vira aviãozinho e voa
  até a caixa daquele número (esboço 2).
- **NULL** — o bilhete em branco, com um traço.
- **fileira** — caixas grudadas, para array, com o índice embaixo.
- **bancada** — a área tracejada de uma função ("dentro de zera(int n)"),
  onde nascem as caixas dela e de onde elas somem quando a função
  termina (esboço 4, tela 3).
- **bloco alugado** — a caixa do `malloc`, num terreno à parte (o
  monte), com uma placa; o `free` tira a placa.

Personagem novo entra quando um tópico pedir, no mesmo estilo; as cenas
que nenhum personagem cobre podem ser feitas à mão, como exceção dita no
arquivo da escada.

### 8.3 A cena em dados, e a conferência

A cena fica no arquivo da escada, no bloco da premissa, ao lado da
revisão. Um passo por linha do código (forma ilustrativa — o formato
final é do construtor):

```yaml
B1:
  revisao:
    frases: [...]
    codigo: |
      int idade = 15;
      int *p = &idade;
      printf("%d\n", *p);
    saida: "15"
  cena:
    atores:
      - {nome: idade, tipo: caixa}
      - {nome: p, tipo: caixa}
    passos:
      - {linha: 1, faz: [{cria: idade}, {guarda: {em: idade, valor: 15}}]}
      - {linha: 2, faz: [{cria: p}, {aponta: {de: p, para: idade}}]}
      - {linha: 3, faz: [{segue: p}, {mostra: 15}]}
```

**A conferência é o que torna a escolha 2 melhor que a 1.** O
conferidor (`scripts/confere_escada.py`) já compila e roda cada código
de revisão. Para a cena, ele monta um segundo programa com o mesmo
código e, depois de cada linha, uma checagem gerada a partir do que a
cena afirma naquele passo: o valor de cada caixa que tem valor
(`printf` do valor), cada ponteiro apontando para quem a cena diz
(`p == &idade`), cada `NULL` (`p == NULL`). Roda, e compara com o que a
cena diz. Mais:

- toda linha do código tem um passo, e nenhum passo aponta para linha
  que não existe;
- o que a cena mostra com `mostra` é a `saida` da revisão, quando a
  revisão tem saída (9 das 61 revisões de hoje não imprimem nada, e a
  cena delas termina sem `mostra`);
- **dentro de uma função** (a bancada), o que a cena diz das caixas da
  função é conferido por uma checagem posta no fim do corpo dela, antes
  do `}` — as funções da escada são de uma linha ou de poucas linhas, e o
  conferidor já sabe separá-las do `main`; depois da chamada, a checagem
  volta a ser a das caixas de quem chamou;
- endereços são de exemplo e nunca são conferidos pelo número (como já é
  nas provas); o carimbo de endereço só aparece nas ideias que falam de
  endereço, e nas fileiras a caixa mostra o índice, não um endereço em
  bytes (o tamanho de cada caixa muda de máquina para máquina);
- caixa sem valor escolhido não é lida pela checagem (ler seria o que o
  tópico ensina a não fazer).

A cena que não confere não entra — como o degrau que não compila.

### 8.4 A cena da prova (segunda etapa)

As provas que imprimem (`espera`) também podem ganhar cena, pelo mesmo
formato e a mesma conferência — é o que o esboço 4 mostra na tela da
máquina. **(decisão minha)** Entra **depois** das cenas de revisão de
todos os tópicos: é outra leva do mesmo tamanho, e a revisão é onde a
cena ajuda mais gente (todo mundo que erra a pergunta de topo).

### 8.5 Movimento

- Cada passo dura por volta de um segundo, com uma pausa no fim de cada
  linha; a pessoa pode pausar, avançar passo a passo e rever.
- Com "reduzir movimento" ligado no sistema, a cena aparece já no estado
  final, com o passo a passo disponível por botão, sem animação.
- A cena é SVG com texto alternativo que descreve o que acontece em cada
  passo (para leitor de tela), gerado dos mesmos dados.

## 9. A ordem do trabalho, em fatias

Cada fatia deixa o sistema funcionando e passa pela suíte inteira.

1. **Identidade e telas.** Os dois temas como variáveis de CSS, o logo e
   o ícone, as fontes (se autorizadas), o topo com paradas e a troca de
   tema, o realce de código, e todas as telas da trilha e a página
   inicial (ainda em lista) na roupa nova. As figuras antigas ficam até a
   fatia 3 de cada tópico **(decisão minha)**: tirá-las antes deixaria
   tópicos sem desenho nenhum.
2. **O caminho.** `caminho.yaml`, o teste da ordem, `/topicos` mandando
   a ordem, e a trilha desenhada na página inicial com o estado de cada
   parada.
3. **O desenhista e as cenas do kc_00**, o tópico-modelo, como foi com
   as escadas: o formato da cena, a conferência, os personagens da
   primeira leva, e as cinco cenas do kc_00. O Rafael olha antes de
   seguir.
4. **As cenas dos outros tópicos**, um de cada vez, na ordem do caminho.
   Ao entrar a cena de um tópico, a figura antiga dele sai.
5. **As cenas das provas** (8.4).

As escadas que faltam (kc_10, kc_11, kc_12) seguem em paralelo, no
formato de sempre, e ganham cena quando chegar a vez delas na fatia 4.

## 10. Para o Rafael decidir

1. **A ordem do kc_01.** O arquivo do tópico diz que ele depende só do
   kc_00; a escada dele, escrita em 13/11, usa função, `return`, `malloc`
   e `sizeof`, e por isso o caminho o põe depois do kc_07. A proposta é
   acertar `prerequisites` do kc_01 para `[kc_00, kc_06, kc_07]` — é
   dado do domínio, e é você quem muda.
2. **Baixar as fontes.** Nunito e JetBrains Mono, licença OFL, do
   repositório oficial de cada uma, cerca de 200 KB no total, para
   `mvp/web/fontes/`. Sem autorização, fica a pilha de fontes do sistema
   (Segoe UI no Windows), e o visual muda pouco.
3. **O estilo do caminho.** Fiquei com a trilha de jogo (opção A do
   esboço 2); você não chegou a escolher entre as três.

## 11. Como saber que funcionou

Conferido por teste:

- nenhuma página nem asset carrega nada de outro endereço (sem `http://`
  nem `https://` em `src`/`href` de `mvp/web/`);
- os pares de cor de texto de cada tema passam no contraste AA;
- o CSS tem a regra de "reduzir movimento" que desliga as animações;
- o realce de código devolve exatamente o texto original;
- `caminho.yaml` tem todo tópico uma vez, cada um depois dos seus
  pré-requisitos, e `/topicos` manda essa ordem;
- toda cena confere (8.3), e a conferência acusa uma cena errada de
  propósito (o teste vê ela falhar);
- toda premissa de tópico com cena tem cena, depois da fatia 4;
- as sessões simuladas continuam passando como hoje, e nenhum teste
  existente foi alterado para passar.

Conferido a olho, com o sistema de ensaio (porta 8013, `ensaios/`): os
dois temas em 360 px e em tela larga, a sessão inteira de um tópico, a
cena com "reduzir movimento" ligado. E o Rafael joga.

## 12. O que fica com o construtor

O formato final da cena em YAML, os nomes dos arquivos novos, a
organização do CSS por tema, como o desenhista divide o SVG, o tempo
exato de cada passo, o desenho fino de cada personagem a partir dos
esboços, e o texto de ajuda da troca de tema — dentro das regras acima.
