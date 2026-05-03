#!/usr/bin/env bash
# build.sh — compila artigo.tex via xelatex + bibtex
# Sequência: xelatex (1ª passada) → bibtex → xelatex → xelatex
# Saída: build/artigo.pdf

set -euo pipefail

cd "$(dirname "$0")"
mkdir -p build

NAME="${1:-artigo}"

echo "[1/4] xelatex (passada inicial)..."
xelatex -output-directory=build -interaction=nonstopmode "${NAME}.tex" > build/run1.log 2>&1 || {
    tail -30 build/run1.log
    exit 1
}

echo "[2/4] bibtex..."
# BIBINPUTS resolve paths relativos do .bib no diretorio raiz do projeto
export BIBINPUTS="$(pwd)/referencias:$(pwd):${BIBINPUTS:-}"
(cd build && BIBINPUTS="$BIBINPUTS" bibtex "${NAME}") > build/bibtex.log 2>&1 || {
    tail -30 build/bibtex.log
    echo "bibtex retornou erro (pode ser warning não-fatal — continuando)"
}

echo "[3/4] xelatex (resolve refs)..."
xelatex -output-directory=build -interaction=nonstopmode "${NAME}.tex" > build/run2.log 2>&1 || {
    tail -30 build/run2.log
    exit 1
}

echo "[4/4] xelatex (consolida)..."
xelatex -output-directory=build -interaction=nonstopmode "${NAME}.tex" > build/run3.log 2>&1 || {
    tail -30 build/run3.log
    exit 1
}

if [ -f "build/${NAME}.pdf" ]; then
    PAGES=$(pdfinfo "build/${NAME}.pdf" 2>/dev/null | grep '^Pages:' | awk '{print $2}')
    SIZE=$(stat -c%s "build/${NAME}.pdf")
    echo
    echo "✓ PDF gerado: build/${NAME}.pdf"
    echo "  Páginas: ${PAGES}, Tamanho: ${SIZE} bytes"
else
    echo "✗ Falha — PDF não gerado. Veja build/run3.log"
    exit 1
fi
