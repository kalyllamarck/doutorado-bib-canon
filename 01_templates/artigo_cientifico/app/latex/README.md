# Template ABNT-Unifor PPGD (LaTeX)

Template reutilizável de artigo acadêmico em LaTeX conforme ABNT NBR 14724:2024 e NBR 6023:2018, ajustado para o Programa de Pós-Graduação em Direito Constitucional (PPGD/Unifor).

## Estrutura

```
abnt-unifor-ppgd/
├── artigo.tex                      # arquivo principal — edite metadados e \input
├── preamble.tex                    # tunings ABNT (TNR 12pt, margens, citações)
├── secoes/
│   ├── 00_introducao.tex
│   ├── 01_capitulo1.tex
│   ├── 02_capitulo2.tex
│   └── 99_conclusao.tex
├── referencias/
│   └── referencias_doutorado.bib   # bibliografia central reutilizável
├── build.sh                        # script de compilação
└── build/                          # saída (gerado pelo script)
```

## Pré-requisitos

```bash
sudo apt-get install -y \
    texlive-full \
    biber \
    texlive-bibtex-extra \
    texlive-publishers \
    texlive-lang-portuguese
```

Pacotes-chave usados: `abntex2`, `abntex2cite`, `fontspec` (xelatex), `babel/portuguese`, `geometry`, `hyperref`.

## Compilação

```bash
cd abnt-unifor-ppgd
./build.sh artigo       # gera build/artigo.pdf
```

A sequência de compilação é `xelatex → bibtex → xelatex → xelatex` (necessária para resolver referências autor-data e bibliografia).

Para iteração rápida sem bibliografia:

```bash
xelatex -output-directory=build artigo.tex
```

## Conformidade ABNT aplicada

| Item NBR 14724/6023 | Implementação |
|---------------------|----------------|
| Fonte Times New Roman 12pt em corpo + headings | `\setmainfont{Times New Roman}` + `\renewcommand{\ABNTEX*fontsize}{\normalsize}` |
| Margens 3 cm sup/esq, 2 cm inf/dir | `\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}` |
| Espaçamento 1,5 no corpo | `\OnehalfSpacing` (de abntex2) |
| Recuo 1,5 cm primeira linha | `\setlength{\parindent}{1.5cm}` |
| Headings primários CAIXA ALTA negrito | `\section{\MakeUppercase{...}}` |
| Subseções negrito case normal | `\subsection{...}` |
| Citação autor-data ABNT | `\citeonline{key}` → "Autor (Ano)"; `\citeauthoronline{key}` → "Autor" |
| Referências alfabéticas, esquerda, sem recuo, simples | gerado por `abntex2-alf.bst` |
| Notas de rodapé TNR 10pt | `\renewcommand{\footnotesize}{\fontsize{10pt}{12pt}\selectfont}` |
| Sem cores em links/citações (impressão B&W) | `\hypersetup{colorlinks=false}` |

## Modificando o conteúdo

Edite os arquivos em `secoes/` para o conteúdo do artigo. Cada arquivo é um `\input` separado para facilitar versionamento por seção.

Para adicionar referência nova: edite `referencias/referencias_doutorado.bib` em ordem alfabética. Exemplo de entrada de livro:

```bibtex
@book{nomedoautor_ano,
  author = {Sobrenome, Nome},
  title = {Título da obra},
  subtitle = {subtítulo opcional},
  publisher = {Editora},
  address = {Cidade},
  year = {AAAA},
}
```

No texto, citar com `\citeonline{nomedoautor_ano}` (resulta em "Sobrenome (Ano)") ou `\cite{nomedoautor_ano}` (resulta em "(SOBRENOME, Ano)").

## Submissão a periódico que exige `.docx`

```bash
pandoc build/artigo.pdf -o artigo_submissao.docx \
    --reference-doc=template_periodico.docx
```

Ou converter direto do `.tex` (recomendado):

```bash
pandoc artigo.tex -o artigo_submissao.docx \
    --bibliography=referencias/referencias_doutorado.bib \
    --citeproc
```

Conversão `.tex → .docx` perde alguns elementos de layout (cabeçalhos numerados, espaçamentos exatos). Sempre conferir manualmente o `.docx` antes de submeter.

## Adaptação para tese

Mudar a primeira linha de `artigo.tex`:

```latex
\documentclass[12pt,a4paper,oneside,openright,brazil]{abntex2}
% remover 'article' das opções
```

Adicionar elementos pré-textuais (capa, folha de rosto, dedicatória, agradecimentos, resumo/abstract no idioma original e em inglês, lista de figuras, sumário, ficha catalográfica).

`abntex2` traz comandos prontos: `\imprimircapa`, `\imprimirfolhaderosto`, `\imprimirfichacatalografica`, `\imprimirsumario`.

## Versionamento

`.tex` é texto puro — git diff funciona perfeitamente. Recomenda-se `.gitignore` excluindo `build/` e arquivos auxiliares (`.aux`, `.log`, `.bbl`, `.blg`, `.toc`).

## Próximos passos

1. **Plan 14-03** — popular `referencias_doutorado.bib` com toda a bibliografia do doutorado (~50-100 entradas).
2. **Plan 14-04** — pipeline `.tex → .docx` para submissão (testar `pandoc` com reference-doc do periódico-alvo).
3. **Plan 14-05** — migrar capítulos da tese para este formato.
4. **Plan 14-06** — avaliar Typst após estabilizar uso do LaTeX.

---

*Template criado em 2026-04-30 como parte da Phase 14 do projeto Doutorado PPGD/Unifor.*
*Para uso em artigos e tese de doutorado de Kalyl Lamarck.*
