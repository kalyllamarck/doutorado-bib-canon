# Stack Research

**Domain:** CLI Python — validador e fixer acadêmico PT-BR com regras editoriais em JSON
**Researched:** 2026-05-04
**Confidence:** HIGH (todas versões verificadas via PyPI; regex testado na instalação local Python 3.12)

---

## Decisoes Fundamentais (Pre-Pesquisa)

O PROJECT.md já fixou quatro decisões de stack que esta pesquisa confirma ou desafia:

| Decisão fixada | Veredito da pesquisa | Ação |
|----------------|---------------------|------|
| Usar stdlib `re` | CONFIRMAR — cobre todos os padrões dos JSONs existentes | Manter |
| Usar `dataclasses` | CONFIRMAR — modelagem de Patch/Violacao perfeita | Manter |
| Usar `pathlib` | CONFIRMAR — padrão moderno | Manter |
| Python 3.13+ | CONFIRMAR — suportado por todas as libs recomendadas | Manter |

---

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

**Por que não mistune 3.2.1:** mistune não expõe posições/offsets nos nós do AST. Não foi encontrada documentação de source map. Seria necessário hackear o parser para obter linha — esforço unjustificado quando markdown-it-py entrega isso nativamente.

**Por que não pandoc via subprocess:** latência de processo externo, sem API Python de token stream, impossível obter offsets sem parsear output intermediário. Use pandoc apenas na fase de rendering final (já existe no pipeline LaTeX).

### Parser LaTeX

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pylatexenc` | 2.10 (estável) | Parse `.tex` abntex2 com offsets | **Escolha principal.** `LatexWalker` retorna `(node, pos, len)` e tem `pos_to_lineno_colno()` — atende REQ-CORE-01 diretamente. Parágrafo detectado via token `\n\n` (SpecialsSpec). |

**Nota de versão:** pylatexenc 3.0 está em alpha (`3.0alpha000033`) com API instável. A versão 2.10 (estável, PyPI) tem `pos` e `len` por nó e é suficiente. Não usar 3.0alpha em produção.

**Por que não TexSoup:** TexSoup não expõe offsets de caractere com precisão byte-exact. pylatexenc foi projetado explicitamente para parsing com posicionamento.

### CLI

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `typer` | 0.25.1 | CLI unificado `validar`/`corrigir`/`auditar` | **Escolha principal.** Type hints como spec da CLI — zero boilerplate adicional. Autocompletion, subcomandos, `--help` automático. Rich integration embutida para output colorido. Python 3.13 explicitamente suportado. |

**Por que não click diretamente:** Typer é built on click mas elimina decoradores manuais e `@option`/`@argument`. Para este escopo (3 comandos principais, poucos flags), Typer reduz o código CLI em ~60%. Click direto só vale se precisar de comportamento que Typer não expõe — improvável aqui.

**Por que não argparse:** Verbose, sem autocompletion nativo, sem Rich integration. Padrão para scripts simples, não para CLI com múltiplos subcomandos e progressive output.

### Output e Logging

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `rich` | 15.0.0 | Tabelas, painéis, progresso, cores no terminal | Relatório `AUDITORIA.md` exibido no terminal antes de gravar. `Table`, `Panel`, `Progress` para orchestrator. Dependência transitiva do typer — sem custo extra de instalação. |
| `loguru` | 0.7.3 | Logging estruturado com zero config | **Escolha principal sobre stdlib logging.** `from loguru import logger` + um `logger.add()` — sem `basicConfig`, sem handlers manuais. Rotação de log automática. Colorização no terminal. Para um CLI local single-user, o overhead de configuração do stdlib logging é injustificado. |

**Por que não stdlib logging:** Requer `basicConfig` ou `DictConfig`, formatters manuais, handlers explícitos. Para um CLI local com 1 usuário, loguru é objetivamente mais simples sem nenhum downside.

### LLM Integration

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `anthropic` | 0.97.0 | Chamadas Claude API para fixers LLM (M7) | SDK oficial. Suporte a streaming, retries, timeout configurável. `claude-sonnet-*` via `client.messages.create()`. |
| `jinja2` | 3.1.6 | Templates de prompt para fixers LLM | Prompts parametrizados por violação + contexto do parágrafo. Separação lógica do conteúdo do prompt do código Python. `Environment(loader=FileSystemLoader("prompts/"))`. |

**Por que jinja2 e não f-strings:** prompts LLM têm estrutura complexa (regra JSON injetada, parágrafo original, alternativas). f-strings multi-linha ficam ilegíveis. Jinja2 permite iterar sobre listas de alternativas, condicionais por severidade, herança de template base. Manutenibilidade superior.

### Testing

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 9.0.3 | Testes unitários REQ-ORC-04 e REQ-ORC-05 | Padrão de facto. Fixtures, parametrize para testar cada regra JSON com input controlado. |
| `pytest-cov` | 7.1.0 | Coverage de cada validador | REQ-ORC-04 exige `input controlado → violação esperada`. Coverage força cobertura de branches nos regex. |

### Packaging

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `uv` | latest | Venv + instalação | Padrão do doutorado. `uv sync` instala tudo do `pyproject.toml`. |

---

## Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `mdit-py-plugins` | latest compatível com markdown-it-py 4.0.0 | Plugin de footnotes pandoc para o parser MD | Sempre que parsear `.md` com `[^n]`. `from mdit_py_plugins.footnote import footnote_plugin`. |
| `tomllib` | built-in (3.11+) | Leitura de `pyproject.toml` para config interna | Se precisar expor config de thresholds ou caminhos padrão via `pyproject.toml`. Zero install. |

---

## Sobre `re` vs `regex` — Decisao Definitiva

**Usar stdlib `re`. Não instalar o pacote `regex`.**

Fundamento verificado empiricamente (Python 3.12, instalação local):

1. `re.UNICODE` é default em Python 3 para strings `str`. `\b` reconhece `ã`, `ç`, `é`, `õ` como `\w` — os padrões `cst_012`, `cst_002`, `cst_004` foram testados e funcionam.
2. Os 38 JSONs existentes usam `À-ÿ` ranges e `\b` com `[a-zà-ÿ]` — zero ocorrências de `\p{...}` property escapes. Portanto o `regex` module NÃO adiciona nada que o corpus atual precise.
3. `regex` 2026.4.4 adicionaria `\p{L}`, fuzzy matching e variable-length lookbehind — nenhum dos quais é necessário para os padrões existentes.
4. Stdlib `re` = zero dependência de rede, zero risco de quebra de versão, zero overhead de instalação.

**Única exceção:** se um validador futuro precisar de `\p{Lu}` (uppercase Unicode) ou lookbehind variável, trocar apenas esse validador para `import regex as re` localmente — sem mudar o projeto inteiro.

---

## Modelagem de Patches (Decisao de Arquitetura)

Usar `dataclasses` com estilo LSP-inspired, sem biblioteca externa:

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

class NivelFixer(str, Enum):
    AUTO = "AUTO"
    ASSISTIDO = "ASSISTIDO"
    LLM = "LLM"

class Severidade(str, Enum):
    ALERTA = "ALERTA"
    FIX_PONTUAL = "FIX_PONTUAL"
    REESCREVER_PARAGRAFO = "REESCREVER_PARAGRAFO"
    VERMELHO_FORTE = "VERMELHO_FORTE"

@dataclass(frozen=True, slots=True)
class Violacao:
    arquivo: str
    linha: int          # 1-based, compativel com markdown-it-py token.map[0]
    col: int            # 0-based character offset na linha
    regra_id: str       # ex: "cst_012", "coc_007"
    severidade: Severidade
    trecho_original: str
    sugestoes: tuple[str, ...]
    principio_canonico: str | None = None
    penalidade: float = 1.0

@dataclass(slots=True)
class Patch:
    linha: int          # 1-based
    col_inicio: int     # 0-based
    col_fim: int        # 0-based, exclusive
    antes: str
    depois: str
    motivo: str         # regra_id que gerou o patch
    confianca: float    # 0.0-1.0
    nivel: NivelFixer
    requer_revisao: bool = True
```

**Por que frozen=True em Violacao:** violações são imutáveis após criação. `slots=True` reduz memória em corpora grandes (artigo 30k palavras pode gerar centenas de violações).

**Por que não JSON Patch (RFC 6902):** JSON Patch opera em estruturas JSON, não em texto. O formato interno é mais simples e direto para a operação de aplicação byte-exact em ordem reversa (REQ-CORE-06).

**Por que não attrs ou pydantic:** dataclasses stdlib são suficientes. pydantic adicionaria validação em runtime, mas os campos são simples (int, str, float) — overhead injustificado. attrs não tem vantagem sobre dataclasses com `slots=True`.

---

## Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `uv` | Gestão de venv e dependências | `uv sync`, `uv run pytest`. Padrão do doutorado. |
| `ruff` | Linter + formatter | Substitui flake8 + black + isort. Configurar `line-length = 80` conforme CLAUDE.md. |
| `mypy` | Type checking | Type hints obrigatórios (CLAUDE.md). `strict = true` no pyproject.toml. |
| `pytest` + `pytest-cov` | Testes + coverage | `pytest --cov=validador --cov-report=term-missing`. |

---

## Installation

```bash
# Criar e ativar venv
uv venv .venv
source .venv/bin/activate

# Dependências core
uv add markdown-it-py==4.0.0 mdit-py-plugins
uv add pylatexenc==2.10
uv add typer==0.25.1
uv add rich==15.0.0
uv add loguru==0.7.3
uv add jinja2==3.1.6
uv add anthropic==0.97.0

# Dev
uv add --dev pytest==9.0.3 pytest-cov==7.1.0 ruff mypy
```

---

## pyproject.toml Exemplificado

```toml
[project]
name = "validador-academico"
version = "0.1.0"
description = "Validador & Fixer acadêmico PT-BR — biblioteca canônica PPGD/Unifor"
requires-python = ">=3.13"
dependencies = [
    "markdown-it-py>=4.0.0",
    "mdit-py-plugins",
    "pylatexenc>=2.10,<3.0",   # fixar abaixo de 3.0 enquanto alpha
    "typer>=0.25.1",
    "rich>=15.0.0",
    "loguru>=0.7.3",
    "jinja2>=3.1.6",
    "anthropic>=0.97.0",
]

[project.scripts]
validar = "validador.cli:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"

[tool.ruff]
line-length = 80
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
python_version = "3.13"

[tool.coverage.run]
source = ["validador"]
branch = true
```

---

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

---

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

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `markdown-it-py>=4.0.0` | `mdit-py-plugins` latest | mdit-py-plugins segue versão do markdown-it-py; instalar sem pinning de versão |
| `pylatexenc>=2.10,<3.0` | Python 3.13 | Fixar `<3.0` para evitar alpha. PyPI tem 2.10 como latest stable (2021, mas estável e suficiente) |
| `typer>=0.25.1` | `rich>=15.0.0` | Typer usa rich para output; rich já é dependência transitiva — não instalar separado se já veio via typer |
| `anthropic>=0.97.0` | Python >=3.9 | SDK oficial. O modelo recomendado é `claude-sonnet-4-5` ou posterior |

---

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

---

*Stack research for: Validador & Fixer Acadêmico — biblioteca_canonica/02_escrita/*
*Researched: 2026-05-04*
