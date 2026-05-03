#!/usr/bin/env python3
"""criar_template.py — Cria Google Doc ABNT vazio reutilizavel via gws CLI.

Specs aplicadas (NBR 14724:2024 + NBR 6023:2018):
- Margens: 3cm sup/esq, 2cm inf/dir
- Fonte default: Times New Roman 12pt
- Espacamento entre linhas: 1.5
- Esqueleto: titulo, autores, resumo, abstract, intro, secoes, conclusao, refs
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

# 1cm = 28.346 pt (1 in = 72 pt; 1 in = 2.54 cm)
CM_PT = 28.346
A4_W_PT = 595.276
A4_H_PT = 841.890


def gws(args: list[str], stdin_json: dict | None = None) -> dict:
    """Invoca gws CLI; retorna JSON parseado."""
    cmd = ['gws'] + args
    if stdin_json is not None:
        cmd += ['--json', json.dumps(stdin_json, ensure_ascii=False)]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(f'[gws ERR] {proc.stderr}\n')
        sys.exit(1)
    out = proc.stdout.strip()
    if not out:
        return {}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        sys.stderr.write(f'[gws JSON ERR] output: {out[:200]}\n')
        sys.exit(1)


def criar_doc(title: str) -> str:
    print(f'Criando doc: {title}')
    resp = gws(
        ['docs', 'documents', 'create'],
        stdin_json={'title': title},
    )
    doc_id = resp['documentId']
    print(f'  DocumentId: {doc_id}')
    return doc_id


def aplicar_margens(doc_id: str) -> None:
    print('Aplicando margens 3/2/3/2 cm + A4...')
    gws(
        ['docs', 'documents', 'batchUpdate',
         '--params', json.dumps({'documentId': doc_id})],
        stdin_json={
            'requests': [{
                'updateDocumentStyle': {
                    'documentStyle': {
                        'marginTop':    {'magnitude': 3 * CM_PT, 'unit': 'PT'},
                        'marginBottom': {'magnitude': 2 * CM_PT, 'unit': 'PT'},
                        'marginLeft':   {'magnitude': 3 * CM_PT, 'unit': 'PT'},
                        'marginRight':  {'magnitude': 2 * CM_PT, 'unit': 'PT'},
                        'pageSize': {
                            'width':  {'magnitude': A4_W_PT, 'unit': 'PT'},
                            'height': {'magnitude': A4_H_PT, 'unit': 'PT'},
                        },
                    },
                    'fields': 'marginTop,marginBottom,marginLeft,marginRight,pageSize',
                },
            }],
        },
    )


SKELETON = '''Título do artigo em português

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
'''


def inserir_esqueleto(doc_id: str) -> int:
    print('Inserindo esqueleto de conteudo...')
    gws(
        ['docs', 'documents', 'batchUpdate',
         '--params', json.dumps({'documentId': doc_id})],
        stdin_json={
            'requests': [{
                'insertText': {
                    'location': {'index': 1},
                    'text': SKELETON,
                },
            }],
        },
    )
    return len(SKELETON) + 1


def aplicar_tipografia(doc_id: str, end_index: int) -> None:
    """TNR 12pt + espacamento 1.5 + recuo 1.5cm em todo o doc."""
    print(f'Aplicando TNR 12pt + 1.5 line + recuo 1.5cm (range 1-{end_index})...')
    gws(
        ['docs', 'documents', 'batchUpdate',
         '--params', json.dumps({'documentId': doc_id})],
        stdin_json={
            'requests': [
                {
                    'updateTextStyle': {
                        'range': {'startIndex': 1, 'endIndex': end_index},
                        'textStyle': {
                            'weightedFontFamily': {
                                'fontFamily': 'Times New Roman',
                                'weight': 400,
                            },
                            'fontSize': {'magnitude': 12, 'unit': 'PT'},
                        },
                        'fields': 'weightedFontFamily,fontSize',
                    },
                },
                {
                    'updateParagraphStyle': {
                        'range': {'startIndex': 1, 'endIndex': end_index},
                        'paragraphStyle': {
                            'lineSpacing': 150,
                            'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 0, 'unit': 'PT'},
                            'alignment': 'JUSTIFIED',
                            'indentFirstLine': {
                                'magnitude': 1.5 * CM_PT, 'unit': 'PT',
                            },
                        },
                        'fields': (
                            'lineSpacing,spaceAbove,spaceBelow,'
                            'alignment,indentFirstLine'
                        ),
                    },
                },
            ],
        },
    )


def main() -> int:
    title = sys.argv[1] if len(sys.argv) > 1 else 'Template ABNT - Doutorado'
    doc_id = criar_doc(title)
    aplicar_margens(doc_id)
    end_idx = inserir_esqueleto(doc_id)
    aplicar_tipografia(doc_id, end_idx)
    url = f'https://docs.google.com/document/d/{doc_id}/edit'
    print()
    print('=' * 50)
    print(f'Template ABNT criado:')
    print(f'  ID:  {doc_id}')
    print(f'  URL: {url}')
    print('=' * 50)
    return 0


if __name__ == '__main__':
    sys.exit(main())
