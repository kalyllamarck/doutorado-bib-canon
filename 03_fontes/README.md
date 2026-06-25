# 03_fontes — obras consultadas

Conteúdo real das fontes consultadas. Uma pasta por obra, no padrão
planejado no `INDEX.json`:

```
03_fontes/<autor_sobrenome>/<ano>_<obra_slug>/
  ficha.json              ← metadado canônico da obra (sempre)
  elementos_pretextuais.json   (opcional)
  elementos_textuais/cap_NN.json (opcional)
  elementos_postextuais.json   (opcional)
  citacoes_uteis.json     (opcional)
```

## `ficha.json` — schema

| Campo | O que é |
|---|---|
| `id` | identificador curto, ASCII (autor_ano_tema) |
| `tipo` | `livro`, `artigo_seminal`, `tese`, … |
| `autor` | em caixa ABNT (`SOBRENOME, Nome`) |
| `titulo` (+ `titulo_original`) | título da obra |
| `ano`, `edicao`, `local`, `editora` | dados de edição (`a confirmar` quando incerto) |
| `area` | tema/campo |
| `citacao_abnt` | referência ABNT pronta |
| `usado_em` | onde a obra é usada: `projeto`, `decisoes[]`, `para_que` |
| `arquivo_local` | caminho do PDF quando houver (`null` enquanto não anexado) |
| `status` | `referencia_catalogada` / `pdf_anexado` / … |
| `ano_edicao` | `confirmado` ou `a_confirmar` |

## Primeiras fichas (2026-06-25)

Doutrina de modelagem de dados e teoria da organização que fundamenta a
matriz da verdade do **lsa-bib-canon** (decisões D-41/D-44):

- `codd_edgar/1970_modelo_relacional_de_dados` — modelo relacional, normalização
- `date_c_j/2004_introducao_a_sistemas_de_bancos_de_dados` — normalização, integridade
- `chiavenato_idalberto/teoria_geral_da_administracao` — teoria da organização
- `pontes_benedito/administracao_de_cargos_e_salarios` — cargos, carreiras, remuneração
- `mintzberg_henry/criando_organizacoes_eficazes` — configurações estruturais

> Anos/edições marcados `a_confirmar` aguardam conferência pelas normas ABNT
> do doutorado. PDFs entram em `arquivo_local` quando anexados.
