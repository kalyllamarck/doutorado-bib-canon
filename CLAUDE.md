<!-- GSD:project-start source:PROJECT.md -->
## Project

**Validador & Fixer Acadêmico — Biblioteca Canônica do Doutorado**

Sistema modular de validação e correção automatizada para artigos científicos em português brasileiro conforme regras canônicas do doutorado em Direito Constitucional (PPGD/Unifor). Lê arquivos `.md`/`.tex`, detecta violações de termos proibidos, construções sintáticas vetadas e princípios de escrita canônica, e aplica correções em três níveis (auto/assistido/LLM). Reusável em qualquer artigo, capítulo de tese ou petição.

**Core Value:** **Garantir que todo texto produzido no doutorado passe pelos mesmos crivos editoriais sem fricção manual.** O autor escreve; o sistema audita contra `biblioteca_canonica/02_escrita/` e propõe correções rastreáveis até a regra-fonte. Sem isso, a biblioteca canônica é só documentação inerte.

### Constraints

- **Tech stack:** Python 3.13+, type hints obrigatórios, max 80 chars/linha, módulo padrão `re` (regex), `dataclasses`, `pathlib`
- **Idioma:** PT-BR brasileiro (regex Unicode com `\b[a-zà-ÿ]`)
- **Performance:** validação de artigo de 30k palavras < 5 segundos
- **Reprodutibilidade:** zero dependências de rede em validadores (só fixers LLM chamam API)
- **Versionamento:** repo git próprio dentro de `biblioteca_canonica/` (já inicializado, commit `6226adc`)
- **Sem cache stateful:** cada execução parte do zero, output determinístico
- **Compatibilidade:** lê `.md` (CommonMark + footnotes) e `.tex` (LaTeX abntex2)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Decisoes Fundamentais (Pre-Pesquisa)
| Decisão fixada | Veredito da pesquisa | Ação |
|----------------|---------------------|------|
| Usar stdlib `re` | CONFIRMAR — cobre todos os padrões dos JSONs existentes | Manter |
| Usar `dataclasses` | CONFIRMAR — modelagem de Patch/Violacao perfeita | Manter |
| Usar `pathlib` | CONFIRMAR — padrão moderno | Manter |
| Python 3.13+ | CONFIRMAR — suportado por todas as libs recomendadas | Manter |
## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.13+ | Runtime | Dataclasses com `slots=True` (3.10+), `match` statement para dispatch de tipo de violação, `tomllib` embutido para leitura de config |
| stdlib `re` | built-in | Aplicação de regex dos JSONs | Os 38 JSONs existentes usam `À-ÿ` ranges e `\b` — testado: funciona corretamente com `re.UNICODE` em PT-BR. Zero dependência de rede. Sem overhead de instalação. |
| `dataclasses` | built-in | Modelagem de `Violacao` e `Patch` | Serialização JSON nativa via `asdict()`, slots para performance, `frozen=True` para imutabilidade de patches, sem instalação extra |
| `pathlib` | built-in | Manipulação de caminhos | API moderna, sem strings de path manual |
| `json` | built-in | Carga dos JSONs de regras | Os JSONs já estão validados; carga simples sem schema enforcement em runtime |
### Parser Markdown
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `markdown-it-py` | 4.0.0 | Parse `.md` CommonMark + footnotes pandoc | **Escolha principal.** Token stream com `map=[start_line, end_line]` em tokens de bloco — exatamente o que REQ-CORE-01 exige. Suporte a footnotes via `mdit_py_plugins.footnote`. Mantida pelo Google Assured OSS. |
### Parser LaTeX
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pylatexenc` | 2.10 (estável) | Parse `.tex` abntex2 com offsets | **Escolha principal.** `LatexWalker` retorna `(node, pos, len)` e tem `pos_to_lineno_colno()` — atende REQ-CORE-01 diretamente. Parágrafo detectado via token `\n\n` (SpecialsSpec). |
### CLI
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `typer` | 0.25.1 | CLI unificado `validar`/`corrigir`/`auditar` | **Escolha principal.** Type hints como spec da CLI — zero boilerplate adicional. Autocompletion, subcomandos, `--help` automático. Rich integration embutida para output colorido. Python 3.13 explicitamente suportado. |
### Output e Logging
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `rich` | 15.0.0 | Tabelas, painéis, progresso, cores no terminal | Relatório `AUDITORIA.md` exibido no terminal antes de gravar. `Table`, `Panel`, `Progress` para orchestrator. Dependência transitiva do typer — sem custo extra de instalação. |
| `loguru` | 0.7.3 | Logging estruturado com zero config | **Escolha principal sobre stdlib logging.** `from loguru import logger` + um `logger.add()` — sem `basicConfig`, sem handlers manuais. Rotação de log automática. Colorização no terminal. Para um CLI local single-user, o overhead de configuração do stdlib logging é injustificado. |
### LLM Integration
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `anthropic` | 0.97.0 | Chamadas Claude API para fixers LLM (M7) | SDK oficial. Suporte a streaming, retries, timeout configurável. `claude-sonnet-*` via `client.messages.create()`. |
| `jinja2` | 3.1.6 | Templates de prompt para fixers LLM | Prompts parametrizados por violação + contexto do parágrafo. Separação lógica do conteúdo do prompt do código Python. `Environment(loader=FileSystemLoader("prompts/"))`. |
### Testing
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 9.0.3 | Testes unitários REQ-ORC-04 e REQ-ORC-05 | Padrão de facto. Fixtures, parametrize para testar cada regra JSON com input controlado. |
| `pytest-cov` | 7.1.0 | Coverage de cada validador | REQ-ORC-04 exige `input controlado → violação esperada`. Coverage força cobertura de branches nos regex. |
### Packaging
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `uv` | latest | Venv + instalação | Padrão do doutorado. `uv sync` instala tudo do `pyproject.toml`. |
## Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `mdit-py-plugins` | latest compatível com markdown-it-py 4.0.0 | Plugin de footnotes pandoc para o parser MD | Sempre que parsear `.md` com `[^n]`. `from mdit_py_plugins.footnote import footnote_plugin`. |
| `tomllib` | built-in (3.11+) | Leitura de `pyproject.toml` para config interna | Se precisar expor config de thresholds ou caminhos padrão via `pyproject.toml`. Zero install. |
## Sobre `re` vs `regex` — Decisao Definitiva
## Modelagem de Patches (Decisao de Arquitetura)
## Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| `uv` | Gestão de venv e dependências | `uv sync`, `uv run pytest`. Padrão do doutorado. |
| `ruff` | Linter + formatter | Substitui flake8 + black + isort. Configurar `line-length = 80` conforme CLAUDE.md. |
| `mypy` | Type checking | Type hints obrigatórios (CLAUDE.md). `strict = true` no pyproject.toml. |
| `pytest` + `pytest-cov` | Testes + coverage | `pytest --cov=validador --cov-report=term-missing`. |
## Installation
# Criar e ativar venv
# Dependências core
# Dev
## pyproject.toml Exemplificado
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `markdown-it-py` 4.0.0 | `mistune` 3.2.1 | Nunca aqui — mistune não expõe offsets de linha nos tokens |
| `markdown-it-py` 4.0.0 | `python-markdown` | Só se precisar de output HTML — não é o caso; este pipeline precisa de token stream com posições |
| `pylatexenc` 2.10 | `TexSoup` | Apenas para extração simples de texto sem necessidade de offsets |
| `typer` | `click` direto | Se precisar de comportamento customizado não suportado por Typer (improvável neste escopo) |
| `loguru` | stdlib `logging` | Se o projeto for parte de uma biblioteca pública (logging é melhor em libs para não poluir handlers do caller) — não é o caso aqui, é CLI |
| stdlib `re` | `regex` 2026.4.4 | Se um validador futuro precisar de `\p{Lu}`, fuzzy matching ou lookbehind variável — trocar localmente só nesse módulo |
| `dataclasses` | `pydantic` v2 | Se houver necessidade de validação de schema em runtime para os JSONs de regra (atualmente confiamos que os JSONs são válidos por serem mantidos manualmente) |
| `anthropic` SDK | `httpx` direto | Nunca — o SDK oficial gerencia retries, streaming e versionamento da API |
| `jinja2` | f-strings | Para prompts simples sem loops/condicionais — aceitável nos fixers AUTO, mas não nos LLM |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `pandas` | Overkill total para este domínio. Soma de penalidades e agrupamento por parágrafo são operações simples em `dict` Python. Pandas adicionaria ~30MB de dependência, import lento, e força paradigma dataframe onde não cabe. | `dict`, `Counter`, `defaultdict` da stdlib |
| `spacy` | Processamento linguístico pesado (modelos de 100-500MB) para PT-BR. Os validadores não fazem POS tagging, NER nem parsing sintático — só regex sobre padrões fixos. | stdlib `re` |
| `nltk` | Mesma razão que spacy — infraestrutura NLP desnecessária para regex matching determinístico | stdlib `re` |
| `pylatexenc` 3.0alpha | API instável, pode quebrar entre alpha releases. PyPI ainda publica 2.10 como estável. | `pylatexenc==2.10` |
| `click` com decoradores manuais | Typer é uma abstração sem custo sobre click. Decoradores manuais duplicam trabalho. | `typer` |
| `yaml` para config interna | Os JSONs de regras já estão em JSON. Adicionar YAML criaria dois formatos de config. | `json` stdlib + `tomllib` para pyproject |
| `black` standalone | `ruff format` substitui black completamente desde ruff 0.1+. Evitar dois formatters. | `ruff format` |
| `flake8` + `isort` | `ruff lint` + `ruff check --select I` substitui ambos. | `ruff` |
| `pytest-asyncio` | Nenhum código assíncrono no core. Fixers LLM usam anthropic SDK síncrono. Async só se houver orchestração paralela de múltiplos artigos — fora do escopo M1-M8. | `pytest` síncrono |
## Version Compatibility
| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `markdown-it-py>=4.0.0` | `mdit-py-plugins` latest | mdit-py-plugins segue versão do markdown-it-py; instalar sem pinning de versão |
| `pylatexenc>=2.10,<3.0` | Python 3.13 | Fixar `<3.0` para evitar alpha. PyPI tem 2.10 como latest stable (2021, mas estável e suficiente) |
| `typer>=0.25.1` | `rich>=15.0.0` | Typer usa rich para output; rich já é dependência transitiva — não instalar separado se já veio via typer |
| `anthropic>=0.97.0` | Python >=3.9 | SDK oficial. O modelo recomendado é `claude-sonnet-4-5` ou posterior |
## Sources
- PyPI `regex` 2026.4.4 — https://pypi.org/project/regex/ (versão confirmada)
- PyPI `markdown-it-py` 4.0.0 — https://pypi.org/project/markdown-it-py/ (versão confirmada)
- markdown-it-py docs, token.map — https://markdown-it-py.readthedocs.io/en/latest/using.html (HIGH: confirma `map=[start_line, end_line]`)
- PyPI `pylatexenc` 2.10 — https://pypi.org/project/pylatexenc/ (estável); alpha em https://pylatexenc.readthedocs.io/en/latest/
- pylatexenc LatexWalker — https://pylatexenc.readthedocs.io/en/latest/latexwalker/ (HIGH: confirma `pos`, `len`, `pos_to_lineno_colno()`)
- PyPI `typer` 0.25.1 — https://pypi.org/project/typer/ (Python 3.13 explicitamente suportado)
- PyPI `loguru` 0.7.3 — https://pypi.org/project/loguru/
- PyPI `rich` 15.0.0 — https://pypi.org/project/rich/
- PyPI `anthropic` 0.97.0 — https://pypi.org/project/anthropic/
- PyPI `jinja2` 3.1.6 — https://pypi.org/project/Jinja2/
- PyPI `pytest` 9.0.3 — https://pypi.org/project/pytest/
- PyPI `pytest-cov` 7.1.0 — https://pypi.org/project/pytest-cov/
- Python 3.13 docs, `re` module — https://docs.python.org/3/library/re.html (HIGH: confirma ausência de `\p{}`, confirma `\b` Unicode-aware)
- Teste empírico local Python 3.12 — `re.search(r'\bsignificativo\b', ...)` retorna match correto; `cst_012` regex retorna match correto sobre exemplo do JSON
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
