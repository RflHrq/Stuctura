# Revisar material do Structura

> Os seis portões de julgamento para material didático novo. O mesmo
> texto é usado, no computador do autor, como instrução do assistente
> de IA que apoia a revisão; por isso ele fala em "esta skill".

## Duas camadas, e esta skill é só a de cima

`python scripts/revisa_material.py candidatos/<topico>/` decide tudo que
é decidível por programa: YAML, id repetido, alternativa mais longa,
distrator sem crença, conceito fora do inventário, forma dos blocos, e o
oráculo compilando cada trecho. **Rode primeiro. ERRO ali encerra a
revisão** — não há o que julgar em material que não carrega.

O que sobra são seis perguntas que programa nenhum responde. Cada uma
está aqui porque o material do kc_02 falhou nela, depois de uma leitura
humana e de uma revisão independente.

## Os seis portões de julgamento

**1. Este item repete pergunta que já existe?**
Leia **os dez itens do nó, em todos os degraus** — `atividades_do_no(no)`
devolve os dez — e compare **cenário**, não palavras. Olhar só o degrau
do item novo não basta: num arquivo revisado, o item de entrada que eu
escrevi era o item de **degrau 3** com a atribuição invertida, e a
escada passaria a medir a mesma coisa nas duas pontas. O script imprime
semelhança léxica como PISTA e esse par deu **0.067**.

**1b. O motor chega a servir este item?**
Antes de escrever item novo, conte o que o motor CONSOME, não o que o
banco tem. Medido: o motor constrói cada nó **uma vez por sessão**
(`construcoes == 0`, `mvp/motor.py:1163`), então serve **um** item de
`entrada` por nó — 74 nós, máximo de 1. Doze itens foram escritos contra
uma escassez que não existe.

**2. O cabeçalho promete o que o corpo entrega?**
O comentário do topo pede assinatura. Confira cada afirmação dele contra
o texto. Defeito real: um arquivo dizia *"usa sizeof e o EXPLICA"*, e o
sizeof aparecia só como rótulo de número já medido — que é a definição
de `mencionado_sem_explicacao`.

**3. Alguma afirmação depende do ambiente?**
Severidade de compilador, tamanho de tipo, valor de endereço. Defeito
real: *"não é aviso, é erro"* é verdade no gcc ≥ 14 e falso antes. Num
laboratório com compilador que avisa, o participante vê o programa
compilar e **não tem alternativa certa para marcar**. O domínio já
resolveu isso: o verbo é **"reclama"**.

**4. Falta pré-requisito que o regex não vê?**
`atribuicao_entre_tipos` e `compilacao` não têm construto que os
denuncie. `aprovacoes.yaml` registra uma cadeia **reprovada** por
exatamente isto — exigir conceito não ensinado e não declarado em
`requer`.

**5. O limite da metáfora foi anunciado e furado?**
O cabeçalho de cada grafo declara onde a metáfora cala. Defeito real: o
material dava *"andam 4 e 1 byte, que é sizeof(int) e sizeof(char)"* e
na frase seguinte dizia que o quanto era de outro tópico.

**6. Cada distrator é a crença dita bem, e a crença certa?**
Alguém assinaria aquela frase? E dois itens do mesmo nó não podem
diagnosticar a mesma resposta errada como crenças diferentes — num
sistema cuja saída é atribuição de crença, isso é defeito de medida.

## Procedência: quando sair para a literatura

Só quando o material **introduz crença nova**, muda um `label_pt`, ou
traz `source` que você não consegue conferir. Material que só usa
crenças já catalogadas não precisa de busca nenhuma — dizer isso é
melhor que inventar trabalho.

Quando precisar, a régua é `docs/linguagem.md`: `D` documentada com
fonte e página, `L` obra técnica, `T` transposta de outra linguagem com
a analogia declarada, `N` norma, `E` hipótese a testar **declarada como
tal**. As fontes livres que o projeto já usa são Sorva (2012), a
dissertação em acesso aberto, e o FAQ do comp.lang.c; CERT C e CWE para
`N`.

O cabeçalho de `beliefs_kc02.yaml` fixa o padrão: *"AS FONTES FORAM
CONFERIDAS NA OBRA PRIMÁRIA, não de memória"*. Abra a obra, cite página
e item. **Fonte que você só consegue parafrasear de memória não é
fonte**, e `docs/linguagem.md` já diz o resto: *"uma crença sem
procedência é uma invenção sua que vai virar dado"*.

## A forma do parecer

Entregue exatamente estas cinco partes, nesta ordem:

```
VEREDITO: aprovar | não aprovar
PORTÕES MECÂNICOS: <saída do script, em uma linha>
BLOQUEIOS: <um por linha, com arquivo e trecho; vazio se não houver>
PROCEDÊNCIA: <conferida, com a fonte | não se aplica, e por quê>
MUDA NO INVENTÁRIO: <conceitos que trocam de status se aprovado>
```

A última parte é obrigatória mesmo quando é "nada". Aprovar material que
ensina um construto sem atualizar o inventário deixa o sistema dizendo
que não ensinou o que passou a ensinar.

## Desculpas que já apareceram

| Desculpa | O que é verdade |
| --- | --- |
| "O script passou, então está bom" | O script não lê. Os seis portões acima são o que ele não decide. |
| "Semelhança baixa, não é duplicata" | O pior par do projeto deu 0.08. Leia os dois itens. |
| "O texto está tecnicamente certo" | Certo nesta máquina não é certo no laboratório. Portão 3. |
| "O cabeçalho explica a decisão" | O cabeçalho é afirmação do autor. Portão 2 existe porque um deles era falso. |
| "A fonte eu conheço" | Conhecer não é conferir. Abra a obra, cite a página. |
| "É só mais um item de entrada" | O motor serve **um** por nó. Doze foram escritos contra escassez que não existe, e os doze eram paráfrase. |
| "Olhei o degrau deste item" | O gêmeo mora em outro degrau. São dez itens por nó; leia os dez. |
| "O distrator aponta a crença certa" | Veja como aquela crença é **dita** nos outros itens do nó. Se o enunciado novo não deixa ela ser escolhida, o item não mede o que declara. |
