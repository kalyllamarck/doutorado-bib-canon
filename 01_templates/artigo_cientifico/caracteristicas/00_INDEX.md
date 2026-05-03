# Template Artigo Científico — Doutorado PPGD/Unifor

> Specs JSON-only. Cada componente do artigo tem 1 arquivo `.json`. Renderizadores LaTeX e Google Docs leem os mesmos JSONs.
> Fonte de verdade do template. Diff via git.

## Índice de componentes

| # | Arquivo | Componente |
|---|---------|------------|
| 01 | `01_titulos.json` | Título PT + Título EN |
| 02 | `02_autores.json` | Nome, ordem, footnote de autoria, ORCID, e-mail |
| 03 | `03_resumo_palavras_chave.json` | Resumo, Palavras-chave, Abstract, Keywords |
| 03b | `03b_sumario.json` | Sumário (índice de seções, regras de inclusão/exclusão) |
| 04 | `04_introducao.json` | Heading + conteúdo introdução (regras de proibição de citação) |
| 05 | `05_secoes.json` | Heading 1 (numerada CAIXA ALTA), Heading 2, corpo, transições |
| 06 | `06_conclusao.json` | Heading + conteúdo conclusão |
| 07 | `07_referencias.json` | Lista alfabética + filtro qualitativo (Qualis A1-A4 + WoS/Scopus) + formato por tipo de fonte |
| 08 | `08_citacoes.json` | Estilo autor-data por tipo de fonte (livro, artigo, tese, relatório, jurisprudência, lei) |
| 09 | `09_notas_rodape.json` | Formato e regras de uso (TNR 10pt, simples) |
| 10 | `10_pagina_global.json` | Margens, fonte default, espaçamentos, page-break rules (página 1 termina com abstract/keywords) |

## Schema comum

Todo JSON segue:

```json
{
  "id": "<slug-único>",
  "componente": "<nome humano>",
  "descricao": "<o que é>",
  "formato_word": {
    "fonte": "Times New Roman",
    "tamanho_pt": 12,
    "negrito": false,
    "italico": false,
    "alinhamento": "justificado",
    "espacamento_linha": 1.5,
    "recuo_primeira_linha_cm": 0,
    "espaco_antes_pt": 0,
    "espaco_depois_pt": 0,
    "page_break_antes": false,
    "page_break_depois": false
  },
  "regras": [
    "<regra 1>",
    "<regra 2>"
  ],
  "proibicoes": [],
  "exemplo": "<conteúdo modelo>",
  "render_latex": "<comando ou padrão LaTeX>",
  "render_gdocs": "<request batchUpdate Google Docs>"
}
```

## Renderizadores

- `render_latex.py` — lê todos os JSONs + .md de conteúdo → gera `.tex` para compilação
- `render_gdocs.py` — lê JSONs + .md → cria Google Doc via gws CLI

(Renderizadores serão criados após estabilizar todos os 10 JSONs.)
