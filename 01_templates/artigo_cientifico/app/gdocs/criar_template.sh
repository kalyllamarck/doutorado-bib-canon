#!/usr/bin/env bash
# criar_template.sh — Cria Google Doc ABNT vazio reutilizavel
#
# Specs aplicadas (NBR 14724:2024 + NBR 6023:2018):
#   - Margens: 3cm sup/esq, 2cm inf/dir (em pt: 1pt=1/72in, 1cm=28.346pt)
#   - Fonte default: Times New Roman 12pt
#   - Espacamento entre linhas: 1.5
#   - Estilos NORMAL_TEXT (corpo), HEADING_1 (cap), HEADING_2 (subsec)
#
# Uso:
#   ./criar_template.sh "Titulo do novo artigo"
#
# Saida: URL do doc criado no Drive do user.

set -euo pipefail

TITLE="${1:-Template ABNT - $(date +%Y-%m-%d)}"
WORKDIR="$(dirname "$0")"

echo "Criando doc: $TITLE"

# 1. Criar documento vazio
RESPONSE=$(gws docs documents create --json "{\"title\":\"${TITLE}\"}" 2>/dev/null)
DOC_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['documentId'])")
echo "DocumentId: $DOC_ID"

# 2. Aplicar formatacao ABNT via batchUpdate
# Margens: 3cm = 85.04pt, 2cm = 56.69pt
# Page size A4: 595.276pt x 841.890pt (default)

cat > /tmp/abnt_requests.json <<'EOF'
{
  "requests": [
    {
      "updateDocumentStyle": {
        "documentStyle": {
          "marginTop":    {"magnitude": 85.04, "unit": "PT"},
          "marginBottom": {"magnitude": 56.69, "unit": "PT"},
          "marginLeft":   {"magnitude": 85.04, "unit": "PT"},
          "marginRight":  {"magnitude": 56.69, "unit": "PT"},
          "pageSize": {
            "width":  {"magnitude": 595.276, "unit": "PT"},
            "height": {"magnitude": 841.890, "unit": "PT"}
          }
        },
        "fields": "marginTop,marginBottom,marginLeft,marginRight,pageSize"
      }
    },
    {
      "updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": 2},
        "paragraphStyle": {
          "namedStyleType": "NORMAL_TEXT",
          "alignment": "JUSTIFIED",
          "lineSpacing": 150,
          "indentFirstLine": {"magnitude": 42.52, "unit": "PT"},
          "spaceAbove": {"magnitude": 0, "unit": "PT"},
          "spaceBelow": {"magnitude": 0, "unit": "PT"}
        },
        "fields": "namedStyleType,alignment,lineSpacing,indentFirstLine,spaceAbove,spaceBelow"
      }
    },
    {
      "updateTextStyle": {
        "range": {"startIndex": 1, "endIndex": 2},
        "textStyle": {
          "weightedFontFamily": {"fontFamily": "Times New Roman", "weight": 400},
          "fontSize": {"magnitude": 12, "unit": "PT"}
        },
        "fields": "weightedFontFamily,fontSize"
      }
    },
    {
      "updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": 2},
        "paragraphStyle": {
          "namedStyleType": "HEADING_1"
        },
        "fields": "namedStyleType"
      }
    }
  ]
}
EOF

# Atualizar estilos namedStyles para conformidade ABNT
# (NORMAL_TEXT, HEADING_1, HEADING_2 ja existem como named styles globais)
cat > /tmp/abnt_named_styles.json <<'EOF'
{
  "requests": [
    {
      "updateDocumentStyle": {
        "documentStyle": {
          "marginTop":    {"magnitude": 85.04, "unit": "PT"},
          "marginBottom": {"magnitude": 56.69, "unit": "PT"},
          "marginLeft":   {"magnitude": 85.04, "unit": "PT"},
          "marginRight":  {"magnitude": 56.69, "unit": "PT"},
          "pageSize": {
            "width":  {"magnitude": 595.276, "unit": "PT"},
            "height": {"magnitude": 841.890, "unit": "PT"}
          }
        },
        "fields": "marginTop,marginBottom,marginLeft,marginRight,pageSize"
      }
    }
  ]
}
EOF

echo "Aplicando margens ABNT..."
gws docs documents batchUpdate --params "{\"documentId\":\"${DOC_ID}\"}" --json @/tmp/abnt_named_styles.json 2>&1 | head -5

# 3. Inserir esqueleto de conteudo (titulo, autor, secoes)
SKELETON_TEXT='Título do artigo em português

Título do artigo em inglês

NOME DO AUTOR 1
NOME DO AUTOR 2

RESUMO

Texto do resumo em parágrafo único, máximo 150 palavras, justificado, sem recuo, espaçamento simples.

PALAVRAS-CHAVE

Termo 1; termo 2; termo 3; termo 4; termo 5.

ABSTRACT

Abstract text in single paragraph, max 150 words, justified, no indent, single spacing.

KEYWORDS

Term 1; term 2; term 3; term 4; term 5.

INTRODUÇÃO

Texto da introdução. Sem citações conforme NBR 14724.

1 TRANSIÇÃO ENERGÉTICA E SEUS CRITÉRIOS DE RUPTURA

1.1 Racionalidade ambiental como critério epistêmico

Texto do corpo, com citações autor-data, conforme Leff (2006).

CONCLUSÃO

Texto da conclusão. Sem citações novas conforme NBR 14724.

REFERÊNCIAS

LEFF, E. La ecología política en América Latina, un campo en construcción. In: ALIMONDA, H. (Ed.). Los tormentos de la materia. Buenos Aires: CLACSO, 2006. p. 21-39.
'

# Escapar para JSON
SKELETON_JSON=$(python3 -c "
import json, sys
text = '''$SKELETON_TEXT'''
print(json.dumps({
    'requests': [
        {
            'insertText': {
                'location': {'index': 1},
                'text': text
            }
        }
    ]
}))
")

echo "Inserindo esqueleto de conteudo..."
gws docs documents batchUpdate --params "{\"documentId\":\"${DOC_ID}\"}" --json "$SKELETON_JSON" 2>&1 | head -5

# 4. Aplicar fonte TNR 12pt em todo o documento
TOTAL_LEN=$(gws docs documents get --params "{\"documentId\":\"${DOC_ID}\"}" 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
content = d.get('body', {}).get('content', [])
last_idx = max([elem.get('endIndex', 1) for elem in content])
print(last_idx - 1)
")

FONT_REQUEST=$(python3 -c "
import json
print(json.dumps({
    'requests': [
        {
            'updateTextStyle': {
                'range': {'startIndex': 1, 'endIndex': $TOTAL_LEN},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': 'Times New Roman', 'weight': 400},
                    'fontSize': {'magnitude': 12, 'unit': 'PT'}
                },
                'fields': 'weightedFontFamily,fontSize'
            }
        },
        {
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': $TOTAL_LEN},
                'paragraphStyle': {
                    'lineSpacing': 150,
                    'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
                },
                'fields': 'lineSpacing,spaceAbove,spaceBelow'
            }
        }
    ]
}))
")

echo "Aplicando TNR 12pt + espaçamento 1.5 em todo o doc..."
gws docs documents batchUpdate --params "{\"documentId\":\"${DOC_ID}\"}" --json "$FONT_REQUEST" 2>&1 | head -5

# 5. URL do doc
URL="https://docs.google.com/document/d/${DOC_ID}/edit"
echo
echo "=========================================="
echo "Template ABNT criado:"
echo "  ID:  $DOC_ID"
echo "  URL: $URL"
echo "=========================================="
