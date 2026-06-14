# Renderizador .docx ABNT — saída CANÔNICA

O `.docx` é o formato canônico de saída do artigo científico do doutorado.
LaTeX e Google Docs continuam existindo em `../latex/` e `../gdocs/`, mas
são alternativos/legado.

## Estrutura

```
app/docx/
├── render_docx.py        ← script principal
├── _abnt_internals/      ← snapshot do docx-modelo ABNT (V12-final)
│   ├── styles.json       ← estilos Word extraídos do modelo
│   ├── section_properties.json  ← margens ABNT (sup 3cm, inf 2cm, esq 3cm, dir 2cm)
│   ├── font_table.json   ← Times New Roman registrada
│   ├── numbering.json    ← listas numeradas
│   ├── headers/          ← cabeçalho com numeração de página
│   └── ...               ← demais internals OOXML
└── README.md
```

## Como gerar um .docx

### Pré-requisito: ativar o venv do lsa-componentes

```bash
source ~/projetos/bib-extrator-componentes-docx/.venv/bin/activate
# ou instalar diretamente:
pip install -e ~/projetos/bib-extrator-componentes-docx
```

### Rodar

```bash
# Ver schema do JSON de entrada
python3 render_docx.py --schema

# Gerar o .docx
python3 render_docx.py --conteudo meu_artigo.json --out artigo_abnt.docx
```

### Validar o .docx gerado

```bash
lsa validar par artigo_abnt.docx artigo_abnt_v2.docx   # compara dois docx
# ou para conferir integridade interna (o docx é um zip válido):
python3 -c "import zipfile; zipfile.ZipFile('artigo_abnt.docx').testzip() or print('OK')"
```

## Schema do JSON de entrada

```json
{
  "titulo_pt": "Título em português",
  "titulo_en": "Title in English",
  "autores": [
    {
      "nome": "Kalyl Lamarck Silvério Pereira",
      "nota": "Doutor em Direito pela UNIFOR."
    }
  ],
  "resumo": "Texto do resumo (150-250 palavras).",
  "palavras_chave": ["termo1", "termo2", "termo3"],
  "abstract": "Abstract text.",
  "keywords": ["term1", "term2"],
  "secoes": [
    {
      "nivel": 1,
      "numero": "1",
      "titulo": "INTRODUÇÃO",
      "paragrafos": ["Parágrafo 1.", "Parágrafo 2."]
    },
    {
      "nivel": 2,
      "numero": "1.1",
      "titulo": "Subseção",
      "paragrafos": ["Texto."]
    }
  ],
  "referencias": [
    "SILVA, José. Título. Fortaleza: Editora, 2024."
  ]
}
```

## Mapeamento campo `formato_word` → estilo do docx-modelo

| Campo canônico (`caracteristicas/`) | Formatação aplicada | Fonte JSON |
|--------------------------------------|---------------------|------------|
| `titulo_pt.formato_word` | TNR 12 negrito centralizado | `01_titulos.json` |
| `titulo_en.formato_word` | TNR 12 itálico centralizado | `01_titulos.json` |
| `formato_nome_word` (autores) | TNR 12 alinhado à direita | `02_autores.json` |
| `formato_rotulo_word` (Resumo/Abstract) | TNR 12 negrito esquerda | `03_resumo_palavras_chave.json` |
| `formato_texto_resumo_word` | TNR 12 justificado | `03_resumo_palavras_chave.json` |
| `formato_primaria_word` (seção 1) | TNR 12 negrito CAIXA ALTA, antes 18pt, depois 12pt | `05_secoes.json` |
| `formato_secundaria_word` (seção 1.1) | TNR 12 negrito, antes 12pt, depois 6pt | `05_secoes.json` |
| `formato_corpo_word` (parágrafos) | TNR 12 justificado, recuo 1.25cm | `05_secoes.json` |
| `formato_word` (notas rodapé) | TNR 10 justificado | `09_notas_rodape.json` |
| `formato_word` (página global) | A4, margens 3/2/3/2cm, espaç. 1.5 | `10_pagina_global.json` |

As margens e o `sectPr` vêm do snapshot `_abnt_internals/section_properties.json`
(extraído do docx-modelo V12-final), garantindo byte-fidelidade ao modelo aprovado.

## Como regenerar o snapshot `_abnt_internals/`

Se o docx-modelo for atualizado, regenere o snapshot:

```bash
source ~/projetos/bib-extrator-componentes-docx/.venv/bin/activate

# Copie o novo modelo para /tmp (evita lock do Word se estiver aberto)
cp "/mnt/c/Users/klama/Downloads/Artigo-Ingrid-Neurotecnologia-VXX.docx" \
   /tmp/artigo_abnt_modelo.docx

# Extrai os internals
lsa extrair /tmp/artigo_abnt_modelo.docx \
    --out /tmp/componentes_artigo_abnt \
    --slug artigo_abnt

# Substitui o snapshot canônico
rm -rf _abnt_internals/
cp -r /tmp/componentes_artigo_abnt/_docx_internals/. _abnt_internals/
```

## Notas técnicas

- **Dependência única**: `lsa-componentes` (dep: `lxml`). Sem `python-docx`.
- **Modo de reconstrução**: usa `reconstruir_docx_do_zero()` de `lib_ooxml.py`.
  Os estilos, fontes e margens vêm sempre do snapshot (não são reinventados).
- **Notas de rodapé**: o script atual não injeta notas de rodapé automaticamente
  (OOXML requer atualizar `word/footnotes.xml` + referências cruzadas em
  `document.xml`). Para artigos com notas, edite o `.docx` gerado no Word
  e insira as notas manualmente — é mais seguro que geração automática.
- **Sumário**: não gerado automaticamente. O Word atualiza ao abrir
  (Ctrl+A → F9 para forçar atualização de campos).
