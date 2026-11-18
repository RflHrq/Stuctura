# 7. Limitações e trabalhos futuros

## 7.1 Limitações

**O sistema não foi avaliado com estudantes.** É a limitação central, e
foi uma decisão de recorte, não um esquecimento: o estudo com
participantes não coube no prazo. Por isso este trabalho não afirma que
estudantes consigam ou queiram completar a sessão, que a hipótese de
concepção errônea gerada pelo sistema coincida com o que eles pensam, nem
que a demonstração os faça mudar de ideia. O que se afirma é que o
sistema faz o que o desenho diz, e que o conteúdo é correto segundo o
compilador.

**A verificação mecânica não verifica a pedagogia.** O compilador confirma
o que um programa faz; não confirma que a ideia ensinada é a certa para um
iniciante, que a ordem dos passos é a mais fácil, nem que a frase de um
passo é clara (5.7).

**O conteúdo foi escrito com assistência de um modelo de linguagem**, e
as escadas aguardam a revisão do autor. A verificação reduz o risco de
afirmação errada sobre C, mas não substitui a leitura de quem conhece o
domínio.

**As concepções errôneas têm procedência desigual.** A maior parte do
catálogo vem de obras técnicas e de corpus de praticantes, e poucas de
medição empírica direta em C (Capítulo 4). O sistema diagnostica as
concepções que a literatura registra; se um estudante tiver outra, o
diagnóstico a registra como erro fora do catálogo, sem tratá-la.

**A certeza declarada é um sinal barato e ruidoso.** Quem marca "tenho
certeza" por hábito gera uma hipótese de concepção errônea errada. O
sistema mitiga isso exigindo a razão da concepção, e não só a resposta
errada, mas não elimina o ruído.

**O que se mede é a sessão.** O fechamento fala de assimilação dentro de
uma sessão: acertar de novo com outras premissas no meio. Isso não é
aprendizagem duradoura, que exigiria reteste dias depois **[conferir:
Soderstrom e Bjork, 2015]**.

**Um ambiente.** As demonstrações foram conferidas no gcc 16.2, no
Windows. Onde o resultado depende do ambiente, a demonstração diz isso;
mas outro compilador, ou outra versão, pode dar outra mensagem.

## 7.2 Trabalhos futuros

1. **O estudo com estudantes**, como desenhado no Apêndice A: de 10 a 15
   participantes que cursam ou cursaram a disciplina com C, pensando em
   voz alta, com quatro perguntas — se concluem a sessão sem ajuda (V1),
   se a concepção detectada coincide com a verbalizada (V2), se mudam de
   resposta num item novo depois da demonstração (V3) e como percebem o
   sistema (V4). O sistema já grava tudo o que o estudo precisa; falta a
   exportação das sessões da trilha em tabelas, o termo de consentimento
   e a submissão ao comitê de ética, se exigida.
2. **A revisão das escadas por especialistas**, com o registro de quem
   revisou cada uma.
3. **O caminho desenhado na página inicial**, com a ordem sugerida dos
   tópicos e o estado de cada um, e as **cenas animadas** que ilustram
   cada premissa com analogias visuais (a caixa, o bilhete), já
   desenhadas e planejadas.
4. **Um modo de prática**, só com os exercícios da escada e retorno de
   certo e errado, para uso fora da sessão de diagnóstico.
5. **Retenção**: um reteste dias depois, para medir o que fica.
6. **Outros compiladores**: conferir as demonstrações também no clang, e
   marcar as que mudam.
