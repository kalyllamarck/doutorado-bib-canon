# Template Tese de Doutorado — PPGD/Unifor

> Specs JSON-only. Fonte normativa: ABNT NBR 14724:2024 + Guia Metodológico PPGD/Unifor.
> Renderizadores LaTeX (abntex2) e Google Docs leem os mesmos JSONs.

## Índice de componentes

| # | Arquivo | Componente |
|---|---------|------------|
| 01 | `01_pre_textuais.json` | Ordem e specs: capa, folha rosto, ficha, aprovação, dedicatória, agradecimentos, epígrafe, resumo, abstract, listas, sumário |
| 02 | `02_textuais.json` | Introdução, 4 capítulos (desenvolvimento), conclusão |
| 03 | `03_pos_textuais.json` | Referências, glossário, apêndice, anexo, índice |
| 04 | `04_formatacao_global.json` | Papel, fonte, margens, entrelinhas, paginação, alinhamento |
| 05 | `05_citacoes.json` | NBR 10520 + exigência PPGD (página obrigatória em indiretas) |

## Schema comum

Cada JSON segue:

```json
{
  "id": "<slug>",
  "componente": "<nome humano>",
  "descricao": "<o que é>",
  "fonte_normativa": "<NBRs + Guia PPGD>",
  "<blocos específicos do componente>": {},
  "regras": [],
  "proibicoes": [],
  "render_latex": "<comandos abntex2>",
  "render_gdocs": "<batchUpdate>"
}
```

## Estrutura textual definida

- **Introdução** (sem indicativo numérico)
- **Capítulo 1** — [a definir]
- **Capítulo 2** — [a definir]
- **Capítulo 3** — [a definir]
- **Capítulo 4** — [a definir]
- **Conclusão** (sem indicativo numérico)

Volume sugerido: 50 páginas/capítulo. Referências: 250-300.
