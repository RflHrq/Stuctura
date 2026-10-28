# Glossário

Um termo, um significado. Estes são os termos que as telas, o código e o TCC
usam — se um deles aparecer com dois sentidos, é bug de conceito.

## O conhecimento

**Premissa (nó).** Uma afirmação que a pessoa pode aceitar ou negar, escrita
de forma que caiba uma resposta de sim ou não. *"`int x;` já reserva o espaço
de x."* Não é tópico ("variáveis"), não é habilidade ("declarar variáveis"):
é uma frase sobre o mundo.

**Premissa observável.** Verifica-se olhando: rodar o código, ler a saída.
É o chão da cadeia.

**Premissa de inferência.** Decorre de outras, que são o seu **suporte**.
*"Então a e p são coisas diferentes."*

**Grafo de premissas.** As premissas de um tópico ligadas por "portanto",
das observáveis até a **conclusão**. Não é mapa conceitual: as arestas são
passos de um argumento, não associações.

**Conclusão do tópico.** A premissa que fecha a cadeia. O que o tópico
ensina.

**Unidade de conhecimento (KC).** Uma habilidade com grafo próprio:
"declaração de variáveis", "o que é um ponteiro", "aritmética de
ponteiros". Dentro dela, premissas; fora dela, outras KCs.

**Grafo interno e grafo externo.** São dois níveis, e a palavra "grafo"
sozinha é ambígua a partir daqui:

- **interno:** as premissas de uma KC ligadas por "portanto", até a
  conclusão. É o que o aluno percorre numa unidade.
- **externo:** as KCs ligadas por pré-requisito. A conclusão de uma KC é
  premissa de entrada da seguinte. É o que decide a ordem das unidades.

O externo já existe em `domain/c_pointers/kcs.yaml`: 12 KCs com
`prerequisites`, `teaching_order` e `conclusion_node`. O que falta é dizer
**qual premissa** de uma KC sustenta **qual premissa** da seguinte — hoje a
aresta liga KC a KC, não premissa a premissa.

**Crença (concepção errônea).** Uma afirmação que a pessoa sustenta e que
**nega exatamente uma premissa** do grafo. É isso que a torna endereçável:
`declaration_zeroes` nega `kc_00:B3`. Se não nega nenhuma, falta premissa no
grafo; se nega duas, são duas crenças.

**Razão.** A justificativa que a pessoa escolhe para a própria resposta. A
razão correta é o enunciado da premissa; as razões erradas são as crenças
que a negam. **A razão não é escrita pelo autor do item: ela já está no
grafo.**

## O estado de uma premissa, para uma pessoa

Cinco estados, lidos do cruzamento entre resposta, razão e confiança.

**Desconhecida.** Nenhuma evidência ainda.

**Lacuna.** A pessoa sabe que não sabe: ela escolhe **"não sei"**, ou erra
com confiança baixa. É o que o método de Feynman procura. Trata-se
**construindo**, não refutando.

**Crença ativa (misconception).** Resposta errada *pela razão errada*, com
confiança. É a rota errada no grafo. Trata-se **refutando**.

**Falso positivo.** Resposta certa *pela razão errada* — o chute, ou o acerto
pelo motivo errado. **Não confirma a premissa**: investiga.

**Falso negativo.** Resposta errada *pela razão certa* — o vacilo, o clique
errado, a leitura apressada. **Não dispara refutação**: segue.

**Confirmada.** Resposta certa, razão certa, com confiança, e sobrevivendo à
troca de superfície. É o verde do mapa.

## O que acontece na sessão

**Diagnóstico.** As perguntas que revelam o estado de uma premissa, antes de
qualquer correção.

**Refutação.** O percurso pelas premissas que sustentam o nó negado, até a
pessoa afirmar o contrário da crença com que entrou. O caminho é **derivado
do grafo**, não escrito à mão.

**Validação.** Reconhecer a ideia da pessoa como razoável antes de contestá-la,
com a analogia do tópico. Quem se sente corrigido defende; quem se sente
ouvido examina.

**Analogia.** A mesma imagem do começo ao fim de um tópico (no kc_00: quarto
de hotel reservado). Serve à condição de **inteligibilidade**: a ideia nova
precisa fazer sentido antes de parecer verdadeira.

**Treino.** Itens sobre a mesma premissa, em superfícies diferentes, depois
da refutação.

**Teach-back (a frase do começo e a do fim).** A pessoa escreve, com as
próprias palavras, o que acontece no conceito — antes da unidade e no fim —
e vê as duas frases lado a lado. Não é corrigido pelo sistema: é registrado
para o pesquisador classificar, e devolvido à pessoa como evidência da
própria mudança.

**Força da premissa.** Quanto a evidência sustenta aquele verde: quantas
superfícies diferentes, com que razão, com que confiança, com quantos
tropeços. É o que decide o que revisitar.

**Mudança conceitual observada.** O critério de sucesso, definido antes da
coleta: a razão escolhida muda da razão-crença para a razão-correta sem
queda de confiança; sobrevive à troca de superfície; e não volta no reteste
do fim da sessão.

## O que NÃO dizemos

**Aprendizagem.** Dentro de uma sessão não se mede aprendizagem, mede-se
desempenho e mudança conceitual observada. "Aprendeu" exige intervalo de
tempo que este estudo não cobre.

**Domínio.** Evitado: sugere permanência. Use *premissa confirmada*.

**Nível / XP / vidas.** Não existem aqui. O progresso é o grafo acendendo.
