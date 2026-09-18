# Documentação do Structura

Quatro documentos escritos, um gerado. Os escritos você edita; o gerado sai
do domínio e não se edita à mão.

| Arquivo | O que responde | Origem |
| --- | --- | --- |
| [plano-tcc.md](plano-tcc.md) | pergunta de pesquisa, estudo, cronograma, o que fica de fora | escrito |
| [fundamentacao.md](fundamentacao.md) | por que o sistema é assim: as cinco ideias e as seis suposições | escrito |
| [requisitos.md](requisitos.md) | atores, RF/RNF com estado, regras de negócio, requisitos novos | escrito |
| [arquitetura.md](arquitetura.md) | camadas, módulos, dados, máquina de estados, decisões | escrito |
| [curadoria-grafos.md](curadoria-grafos.md) | todo nó de todo grafo, e o que pede decisão | **gerado** |

```bash
python -m tools.curadoria
```

Os mesmos textos vivem também num documento online, para comentário do
orientador: <https://claude.ai/code/artifact/4b871c48-835f-4625-9fb6-b13c3fcdc1c6>.
Quando os dois divergirem, **este diretório é a fonte** — ele é versionado
junto com o código que descreve.

## O que ainda não existe

- **Especificação v1.1.** A v1.0 não tem gradação, desafio adaptativo nem
  sondagem, que existem em código e em teste. Nem os requisitos RF18–RF25.
- **Roteiro da sessão, termo de consentimento e questionário de percepção.**
- **Revisão de conteúdo** das 12 atividades escritas com a Claude.
