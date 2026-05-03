# Biblioteca Canônica — Doutorado PPGD/Unifor

> Fonte de verdade machine-readable do projeto de doutorado.
> Tudo em JSON. Diff via git. Renderizadores leem JSON e geram .tex / Google Doc / .docx.

## Estrutura

```
biblioteca_canonica/
├── 01_templates/        # Templates de DOCUMENTOS por tipo (artigo, tese, relatório, petição)
├── 02_escrita/          # Regras transversais de escrita (canônica, conjunções, termos proibidos)
├── 03_fontes/           # Conteúdo real das obras consultadas (autor → obra → páginas)
├── 04_normas/           # Normas técnicas referenciais (ABNT, NBR) em JSON
└── 05_metadados/        # JSON Schema + glossário do projeto
```

## Componentes prontos (3 maio 2026)

### 01_templates/artigo_cientifico/

- **caracteristicas/** — 11 JSONs estruturais (títulos, autores, resumo, sumário, intro, seções, conclusão, referências, citações, notas de rodapé, página global)
- **app/latex/** — template LaTeX `abntex2` compilável
- **app/gdocs/** — script Python para criar Google Doc via `gws` CLI

### 02_escrita/

- **escrita_canonica.json** — 16 princípios + 6 perguntas de teste de estresse + mapeamento cst→princípio
- **termos_proibidos/** — 6 JSONs (lexicais, expressões, colocações, construções, sinais, regras de coocorrência)
- **conjuncoes/** — 18 JSONs por subtipo (5 coordenativas + 13 subordinativas) totalizando **802 entradas** com schema v2.0 (registro, score acadêmico, polissemia, outros_subtipos)

## Componentes a construir

- **01_templates/** — tese_doutorado/, relatorio_institucional/, peticao_juridica/
- **02_escrita/** — traducao_estrangeirismos/, voz_e_tempo_verbal.json, profundidade_doutrinaria.json, marcadores_discursivos.json
- **03_fontes/** — bootstrap com piloto Leff 2006
- **04_normas/** — extração JSON das NBRs 6023, 6027, 6028, 10520, 14724
- **05_metadados/schemas/** — JSON Schema v7 para validação

## Convenções

### Schema comum dos componentes (01_templates)

```json
{
  "id": "<slug>",
  "componente": "<nome>",
  "descricao": "<o que é>",
  "fonte_normativa": "<NBR / RAG ref>",
  "formato_word": { ... },
  "regras": [ ... ],
  "exemplo": "<modelo>",
  "render_latex": "<comando ou padrão>",
  "render_gdocs": "<request batchUpdate>"
}
```

### Schema das conjunções (02_escrita/conjuncoes/)

```json
{
  "subtipo": "<aditivas|adversativas|...>",
  "categoria": "<coordenativas|subordinativas>",
  "definicao": "<...>",
  "total": N,
  "formais": N,
  "informais": N,
  "polissemicas": N,
  "itens": [
    {
      "forma": "ademais",
      "registro": "formal_academico|informal",
      "score_academico": 1-5,
      "polissemica": bool,
      "outros_subtipos": ["coordenativas/aditivas"],
      "proibido_artigo_academico": bool,
      "motivo_proibicao": "<...>"
    }
  ]
}
```

### Schema das obras (03_fontes/<autor>/<obra>/)

- `ficha.json` — capa, ISBN, ano, editora, edição, referência ABNT renderizada
- `elementos_pretextuais.json` — rosto, créditos, ficha catalográfica, dedicatória, epígrafe, sumário
- `elementos_textuais/cap_NN.json` — capítulos com `{pagina_inicio, pagina_fim, texto, citacoes_extraidas}`
- `elementos_postextuais.json` — bibliografia, índice
- `citacoes_uteis.json` — paráfrases já elaboradas + página de origem + uso em artigos

## Renderizadores

```bash
# LaTeX
cd 01_templates/artigo_cientifico/app/latex
./build.sh artigo

# Google Docs (via gws CLI)
cd 01_templates/artigo_cientifico/app/gdocs
python3 criar_template.py "Título do artigo"
```

## Pré-requisitos

- TeX Live full + biber + abntex2 + ttf-mscorefonts-installer (Times New Roman)
- Python 3.12+ com `lxml`, `python-docx`
- `gws` CLI autenticado no Google Workspace
- Túnel SSH 8401 ativo para consultar RAG CodexAcad (opcional)

## Versionamento

Repositório git próprio (independente do Doutorado raiz). Diffs versionam regras editoriais e templates.

## Histórico

- 2026-05-03 — Bootstrap. Migração de `templates_artigo_cientifico/`, `templates_latex/`, `templates_gdocs/` e `conjuncoes.json`.
