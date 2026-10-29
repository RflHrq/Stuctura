# Apresentação ao orientador — o que mostrar, e em que ordem

Dez minutos de demonstração, e as perguntas que ele vai fazer com a
resposta honesta de cada uma.

## Antes (cinco minutos)

```bash
bash scripts/demo.sh
```

Ele confere tudo e imprime os quatro passos. Resumidos:

```bash
# terminal A
STRUCTURA_TOPICO=kc_02 STRUCTURA_LOG=ensaios/demo.jsonl python -m mvp.app
# aqui
bash scripts/demo.sh semear
# terminal B
STRUCTURA_TOPICO=kc_02 STRUCTURA_LOG=ensaios/demo.jsonl python -m mvp.painel
```

Duas abas abertas **antes** de ele chegar:

- `http://127.0.0.1:8010/?codigo=DEMO-AOVIVO` — quem responde
- `http://127.0.0.1:8011` — o painel

A semeadura cria três sessões prontas, uma por persona, para o painel ter o
que mostrar sem você ter que atravessar 80 telas ao vivo.

---

## O roteiro

### 1. A frase de abertura (trinta segundos)

> O sistema não pergunta se a pessoa acerta. Ele pergunta **por quê** ela
> acertou, e usa a resposta errada para descobrir **em qual premissa** ela
> está errada — e refuta aquela, não a pergunta.

### 2. A tela, ao vivo (três minutos)

Na aba de quem responde, faça **uma** atividade:

1. Responda a camada 1 **errado**, de propósito.
2. A resposta **tranca** — e só então aparecem as razões. Diga por quê:
   *"as razões são enunciados de crenças; lê-las antes entrega a pista e
   muda a resposta de quem ia acertar"*.
3. Escolha uma razão errada.
4. Diga a confiança.

O que acontece a seguir é a demonstração inteira: valida com uma analogia,
**refuta percorrendo as premissas que sustentam a que ela negou**, e só
então treina.

**O ponto que vale parar e explicar:** a crença que ela escolheu pode negar
**outro nó** que não o da pergunta. O sistema registra a crença no nó que
ela nega, não no nó do item. É a CS-2, e é o que separa isto de um quiz.

### 3. O painel, com as três sessões (quatro minutos)

Abra **DEMO-APRENDE** — é a que mostra o laço inteiro.

| O que apontar | O que dizer |
| --- | --- |
| as **duas frases**, lado a lado | antes: *"é tipo um atalho para outra variável, acho"* · depois: *"é uma caixa que guarda o endereço de outra caixa — duas caixas, não uma"*. É a mudança conceitual nas palavras dela |
| **24 episódios**, cada um classificado | resposta × razão × confiança nos cinco estados |
| **refutadas 6 · retestadas 5** | toda crença detectada voltou no fim, numa superfície diferente |
| o **mapa** | as seis premissas de pé, e por qual caminho cada uma chegou lá |

Depois abra **DEMO-CRENTE** e mostre o contrário: 120 respostas, e uma
premissa que o sistema marca como **não medida**.

> Esta é a parte de que eu mais gosto: quando o banco de itens acaba sem
> conseguir medir uma premissa, o sistema **diz isso**, em vez de deixar a
> premissa cinza como se nunca tivesse sido perguntada.

### 4. O que o sistema custa, em número (um minuto)

Trinta sessões atravessadas por um programa que simula três tipos de aluno,
antes de qualquer pessoa ver a tela:

| Persona | Passos | Premissas sem medida |
| --- | --- | --- |
| acerta tudo | 42 | 0 em 10 |
| erra e aprende com a refutação | 81 | **0 em 10** |
| erra e nunca muda de ideia | 90–121 | 4 em 10, **todas nomeadas** |

E o processo: **261 testes** no MVP, 252 na suíte antiga, varredura de
segredos em todo commit, e uma revisão final que **reprovou** o sistema para
coleta e listou o que falta.

---

## As perguntas que ele vai fazer

Responda assim. A honestidade aqui é o seu ativo mais forte: aluno que
chega com "está pronto" é mais frágil que aluno que chega com "funciona, e
eu sei exatamente o que ainda não funciona".

**"Isso já foi testado com gente?"**
> Não. Nenhuma pessoa real atravessou. Os dois critérios que dependem de
> gente — CS-11, atravessar sozinha, e CS-12, conseguir dizer o que mudou —
> estão declarados no PRD como os únicos que o computador não prova. O
> roteiro do primeiro ensaio está pronto; é o próximo passo.

**"Como você sabe que funciona, então?"**
> Por três caminhos independentes: 261 testes automáticos, 30 sessões
> simuladas de ponta a ponta, e uma revisão final que subiu o sistema de um
> clone do zero, derrubou o servidor no meio de uma sessão, apagou o log e
> restaurou da cópia. A sessão restaurada reconstruiu com a mesma
> impressão digital.

**"Está pronto para coletar?"**
> Não, e eu sei por quê. A revisão final deu **NO-GO**, por quatro motivos.
> Um era de software e está resolvido. Os outros três: o termo de
> consentimento não existe nem como rascunho, não há plano de incidente, e
> o pedido de exclusão de um participante não alcança as cópias de
> segurança. Os dois primeiros eu queria discutir com o senhor hoje.

**"Qual a diferença disso para um quiz?"**
> Três camadas em vez de uma. Um acerto com explicação errada **não**
> confirma a premissa — vira falso positivo. Um erro com explicação certa
> **não** dispara refutação — é escorregão. E a crença vai para o nó que
> ela nega, que pode não ser o nó da pergunta.

**"E se a pessoa chutar?"**
> Chute declarado vira **lacuna**, não crença. O sistema não refuta o que a
> pessoa não pensa — refutar um chute ensinaria uma crença que ela não
> tinha.

**"De onde vêm as concepções erradas?"**
> De catálogo, com procedência declarada. Quatro das seis do tópico têm
> fonte verificada na obra primária — Sorva 2012 e o FAQ do comp.lang.c —
> e duas estão declaradas como **hipótese a testar**. Se nenhum
> participante sustentar essas duas, isso também é achado.

**"Quanto tempo leva uma sessão?"**
> Entre 42 e 121 telas, dependendo de quanto a pessoa erra. Quantos minutos
> isso dá eu ainda **não sei** — tudo o que medi está em cliques. É uma das
> coisas que o ensaio com uma pessoa responde.

---

## O que **não** dizer

- Não diga que está pronto, nem que é seguro, nem que está validado.
- Não prometa prazo de coleta antes de saber o que o comitê de ética pede.
- Se ele perguntar algo que você não sabe, diga que não sabe e anote. Toda
  pergunta que você não souber responder hoje é uma tarefa boa.

## O que pedir a ele

1. **Quem escreve o termo de consentimento**, e quando ele vai ao comitê —
   é o item com o prazo mais longo de tudo que falta.
2. **Um nome** para revisar o conteúdo das 36 atividades de ponteiros, se
   não for ele mesmo.
3. **Autorização para o primeiro ensaio** com uma pessoa, e a opinião dele
   sobre onde fica a linha entre ensaio de interface e pesquisa com seres
   humanos.
