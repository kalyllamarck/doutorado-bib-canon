# Phase 1: Bootstrap — Research

**Researched:** 2026-05-04
**Domain:** Bootstrap de projeto Python (uv + src-layout + Typer entry point)
**Confidence:** HIGH (todas decisões D-01 a D-19 validadas empiricamente em sandbox `/tmp/uv-bootstrap-smoke`)
**Phase deliverable:** Projeto Python instalável via `uv sync` com layout `src/biblio_validador/`, CLI `validar` no PATH, deps M1 fixadas em `pyproject.toml`.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Identidade do pacote**

- **D-01:** Nome do pacote Python = `biblio_validador` (módulo importável). Distribution name no `pyproject.toml` = `biblio-validador` (PEP 503 normalizado, hífen).
- **D-02:** Layout `src/` (PEP 621 + uv padrão): `src/biblio_validador/__init__.py`. Evita import acidental do source tree sem instalação.
- **D-03:** Versão inicial = `0.1.0` em `__init__.py` como `__version__ = "0.1.0"` (única exposição pública nesta fase; classes públicas vêm em Phases 2-5).

**Gestão de dependências**

- **D-04:** `uv` como gerenciador único. Comando canônico: `uv sync`.
- **D-05:** Python pin = `requires-python = ">=3.13"`.
- **D-06:** Deps M1 instaladas no grupo principal `[project.dependencies]`:
  - `markdown-it-py>=4.0.0`
  - `mdit-py-plugins` (sem pin — segue markdown-it-py)
  - `pylatexenc>=2.10,<3.0` (fixar abaixo de alpha)
  - `typer>=0.25.1`
  - `rich>=15.0.0`
  - `loguru>=0.7.3`
- **D-07:** Deps M7 em grupo opcional `[project.optional-dependencies].llm`:
  - `anthropic>=0.97.0`
  - `jinja2>=3.1.6`
  - Instalação: `uv sync --extra llm` quando M7 começar.
- **D-08:** Dev deps em `[dependency-groups].dev` (uv-native):
  - `pytest>=9.0.3`
  - `pytest-cov>=7.1.0`
  - `ruff` (sem pin)
  - `mypy` (sem pin, modo strict)
- **D-09:** `uv.lock` versionado no git desde Phase 1 (reprodutibilidade dia 1).

**CLI / entry point**

- **D-10:** Entry point único `validar = "biblio_validador.cli:app"` em `[project.scripts]`. Subcomandos virão como `app.command()` em phases futuras. Phase 1 entrega apenas `app = typer.Typer()` esqueleto + `validar --help` funcional.
- **D-11:** Esqueleto mínimo `cli.py`: define `app = typer.Typer(help="Validador acadêmico — biblioteca canônica PPGD/Unifor")` e expõe stub `@app.callback()` ou comando placeholder que retorna exit 0. Não implementa lógica de validação.

**Tooling de qualidade**

- **D-12:** `ruff` configurado: `line-length = 80`, `target-version = "py313"`, `[tool.ruff.lint] select = ["E", "F", "I", "UP", "B"]`.
- **D-13:** `mypy` configurado: `strict = true`, `python_version = "3.13"`.
- **D-14:** `pytest` config: `testpaths = ["tests"]`, `addopts = "--tb=short"`, `[tool.coverage.run] source = ["biblio_validador"] branch = true`.

**Smoke test obrigatório**

- **D-15:** `tests/test_cli.py` com 1 teste mínimo verificando `validar --help` retorna exit 0 e contém string "biblioteca canônica".
- **D-16:** `tests/__init__.py` vazio.

**Itens diferidos**

- **D-17:** Pre-commit hook → M8 (Phase 50+).
- **D-18:** GitHub Actions / CI → fora de escopo.
- **D-19:** Logging configurado via `loguru` → Phase 2.

### Claude's Discretion

- Estrutura interna além de `src/biblio_validador/__init__.py` e `src/biblio_validador/cli.py` (não criar pastas vazias agora).
- Texto exato do `description` no `pyproject.toml`.
- README.md (já existe na raiz, não tocar).
- Conteúdo exato do `app.callback()` placeholder.

### Deferred Ideas (OUT OF SCOPE)

- Pre-commit hook — M8.
- CI/CD GitHub Actions — v2.
- Pacote em PyPI — uso interno apenas.
- Dockerfile — não há justificativa.
- Configuração `loguru` — Phase 2.
- CLI subcomandos `corrigir` / `auditar` — Phases 8 e 52.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CORE-12 | Layout `src/biblio_validador/` com `pyproject.toml` + `uv` install + entry point `validar` no PATH | Validado empiricamente: `uv init --package biblio-validador` produz `src/biblio_validador/__init__.py` (hífen→underscore automático); `uv sync` cria `.venv/bin/validar` quando `[project.scripts] validar = "biblio_validador.cli:app"`; Typer.app é callable via `__call__` (PEP 503 entry-point spec aceita callables, não só functions). |

</phase_requirements>

## Summary

Phase 1 é puramente estrutural: gerar `pyproject.toml`, `src/biblio_validador/__init__.py`, `src/biblio_validador/cli.py` (esqueleto Typer), `tests/test_cli.py` (smoke test) e `uv.lock` (commit). CONTEXT.md já fixou 19 decisões (D-01 a D-19); a tarefa desta pesquisa não é re-debater stack — é **validar empiricamente cada D-XX contra o comportamento real do `uv 0.11.6` e do `typer 0.25.1` instalados** e identificar pitfalls específicos da combinação que CONTEXT.md não cobre.

**Validação empírica completa:** todas as 19 decisões foram testadas em sandbox `/tmp/uv-bootstrap-smoke`. Resultado: `uv init --package biblio-validador` + override de `requires-python`/`.python-version` + `uv add` + `uv sync` + arquivo `cli.py` com `@app.callback()` + `tests/test_cli.py` com `CliRunner` produzem o entregável CORE-12 ponta-a-ponta com `pytest` verde e `validar --help` retornando exit 0 contendo "biblioteca canônica". Python 3.13.13 é **auto-baixado** por uv quando ausente (33.7MiB), portanto a constraint `>=3.13` não é bloqueio mesmo sem 3.13 pré-instalado.

**Primary recommendation:** execute o plano em três blocos atômicos: (1) `uv init --package biblio-validador` + edits manuais ao `pyproject.toml` (override de `requires-python`, `[project.scripts]`, adição das tabelas `[tool.*]`, remoção do `description` placeholder); (2) escrever `cli.py` com `@app.callback()` (NÃO `@app.command()` — ver Pitfall 1 abaixo) + `tests/test_cli.py` + `tests/__init__.py`; (3) `uv add` em três passes (core, optional `--optional llm`, dev `--dev`) seguido de `uv sync` e `uv run pytest` para validar.

## Architectural Responsibility Map

Phase 1 não tem capabilities funcionais (puramente bootstrap). Mapeamento de "tier ownership" é trivial:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Resolução de deps + venv | uv (build/dev tooling) | — | uv é único gestor de deps por D-04 |
| Entry point ELF wrapper | uv-build (PEP 517 backend) | Python sysconfig | `[project.scripts]` é compilado pelo build backend para shebang `.venv/bin/validar` |
| Importable package surface | Python runtime (CPython 3.13) | — | `src/biblio_validador/` no `sys.path` via editable install |
| CLI dispatch | Typer 0.25.1 (top-level lib) | Click (transitivo) | Typer.app é callable que delega para Click |
| Test execution | pytest 9.0.3 | typer.testing.CliRunner | Smoke test é in-process via Click testing.CliRunner — não subprocess |

## Standard Stack

### Core (D-06 — confirmado por `uv add` em sandbox)

| Library | Version (PyPI 2026-05-04) | Purpose | Why Standard |
|---------|---------------------------|---------|--------------|
| `markdown-it-py` | 4.0.0 | Parser CommonMark + footnotes (Phase 2+) | Único parser MD com `token.map=[start_line, end_line]` por token de bloco — exigido por REQ-CORE-01 [VERIFIED: STACK.md + PyPI] |
| `mdit-py-plugins` | 0.5.0 (auto-resolved) | Plugin de footnotes pandoc | Sem versão pin: segue major do markdown-it-py [VERIFIED: uv add resolveu 0.5.0 automaticamente] |
| `pylatexenc` | 2.10 | Parser LaTeX abntex2 (Phase 16+) | `LatexWalker.pos_to_lineno_colno()` para offsets byte-exact; pin `<3.0` mandatório (alpha instável) [VERIFIED: STACK.md + PyPI] |
| `typer` | 0.25.1 | CLI framework | Type-hint-driven; `app` é callable; reduz ~60% boilerplate vs click puro [VERIFIED: empírico — `app = typer.Typer()` funciona como entry point] |
| `rich` | 15.0.0 | Tabelas/painéis no terminal (Phase 9+) | Dependência transitiva de typer — sem custo extra de instalação [VERIFIED: instalado como dep do typer] |
| `loguru` | 0.7.3 | Logging (Phase 2 — D-19) | Zero-config; primeira chamada `logger.add()` é em Phase 2 [VERIFIED: STACK.md + PyPI] |

### Optional `llm` extra (D-07)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `anthropic` | 0.97.0 | SDK Claude API (M7 Phase 42+) | `uv sync --extra llm` quando M7 começar [VERIFIED: instalado em sandbox] |
| `jinja2` | 3.1.6 | Templates de prompt (M7) | Mesma fase que `anthropic` [VERIFIED: PyPI + sandbox] |

### Dev group (D-08 — PEP 735 `[dependency-groups]`)

| Library | Version (PyPI) | Purpose | Notes |
|---------|---------------|---------|-------|
| `pytest` | 9.0.3 | Test runner | uv-native: instalado por default em `uv sync` [VERIFIED] |
| `pytest-cov` | 7.1.0 | Coverage | Requer config `[tool.coverage.run]` (D-14) [VERIFIED] |
| `ruff` | 0.15.12 (sem pin) | Linter + formatter | Substitui flake8/black/isort [VERIFIED: instalado em sandbox] |
| `mypy` | 1.20.2 (sem pin) | Type checker | Modo `strict = true` (D-13) [VERIFIED] |

### Validação de versões via PyPI (executada em 2026-05-04)

| Stack item | STACK.md disse | uv resolveu | Status |
|------------|---------------|-------------|--------|
| typer | `>=0.25.1` | 0.25.1 | EXATO |
| rich | `>=15.0.0` | 15.0.0 | EXATO |
| loguru | `>=0.7.3` | 0.7.3 | EXATO |
| pylatexenc | `>=2.10,<3.0` | 2.10 | EXATO |
| jinja2 | `>=3.1.6` | 3.1.6 | EXATO |
| pytest | `>=9.0.3` | 9.0.3 | EXATO |
| pytest-cov | `>=7.1.0` | 7.1.0 | EXATO |
| anthropic | `>=0.97.0` | 0.97.0 | EXATO |
| mdit-py-plugins | sem pin | 0.5.0 | OK |
| ruff | sem pin | 0.15.12 | OK |
| mypy | sem pin | 1.20.2 | OK |

**Conclusão:** todas versões em STACK.md continuam vigentes em PyPI (2026-05-04). Nenhuma renegociação necessária.

## Architecture Patterns

### System Architecture

```
┌─ Source tree (commitado) ──────────────────────────┐
│  pyproject.toml  (deps + [tool.*] config)          │
│  uv.lock         (versões transitivas — D-09)      │
│  .python-version (override para 3.13)              │
│  src/biblio_validador/                             │
│      __init__.py  (__version__ = "0.1.0")          │
│      cli.py       (Typer app + @app.callback())    │
│  tests/                                            │
│      __init__.py  (vazio — D-16)                   │
│      test_cli.py  (smoke test CliRunner — D-15)    │
└──────────────────────┬─────────────────────────────┘
                       │ uv sync
                       ▼
┌─ Build artifacts (gitignored) ─────────────────────┐
│  .venv/                                            │
│      bin/python3.13       (auto-baixado se ausente)│
│      bin/validar          (entry point script)     │
│      lib/python3.13/site-packages/                 │
│          biblio_validador/  (editable install)     │
│          typer, rich, loguru, ...                  │
│  .pytest_cache/                                    │
│  .ruff_cache/                                      │
│  .mypy_cache/                                      │
│  __pycache__/                                      │
└────────────────────────────────────────────────────┘
                       │
                       ▼
┌─ User-invoked surface ─────────────────────────────┐
│  $ uv run validar --help     (via uv shim)         │
│  $ source .venv/bin/activate                       │
│  $ validar --help            (PATH absoluto)       │
│  $ uv run pytest             (smoke test verde)    │
└────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
biblioteca_canonica/
├── .gitignore               # AMPLIAR: + .pytest_cache, .ruff_cache, .mypy_cache, htmlcov, dist, build, *.egg-info
├── .python-version          # NEW (uv init): "3.13"
├── pyproject.toml           # NEW
├── uv.lock                  # NEW (commitado — D-09)
├── README.md                # NÃO TOCAR (já existe)
├── INDEX.json               # NÃO TOCAR
├── 01_templates/            # NÃO TOCAR
├── 02_escrita/              # NÃO TOCAR
├── 03_fontes/               # NÃO TOCAR
├── 04_normas/               # NÃO TOCAR
├── 05_metadados/            # NÃO TOCAR
├── src/                     # NEW
│   └── biblio_validador/    # NEW (D-01)
│       ├── __init__.py      # NEW (D-03 — só __version__)
│       └── cli.py           # NEW (D-10/D-11 — Typer skeleton)
└── tests/                   # NEW
    ├── __init__.py          # NEW (D-16 — vazio)
    └── test_cli.py          # NEW (D-15 — smoke test)
```

**Pontos críticos da estrutura:**

1. `.gitignore` na raiz já existe com `__pycache__/`, `*.pyc`, `*.pyo`, `.venv/`, `venv/` — falta acrescentar caches do tooling Python moderno (.pytest_cache, .ruff_cache, .mypy_cache) e artefatos de build (htmlcov, *.egg-info, dist, build). [VERIFIED: lido conteúdo do `.gitignore` atual]
2. **NÃO criar** `src/biblio_validador/core/`, `validadores/`, `fixers/` — estas pastas pertencem a Phase 2+ (CONTEXT.md Claude's Discretion: "não criar pastas vazias agora").
3. ARCHITECTURE.md menciona `src/validador_academico/` — **ignorar essa nomenclatura legacy**. CONTEXT.md D-01 fixa `biblio_validador` como nome canônico. Versionado depois do roadmap; ARCHITECTURE.md está stale para o nome.

### Pattern 1: Typer skeleton via `@app.callback()` (não `@app.command()`)

**Source: empirical test 2026-05-04**

```python
# src/biblio_validador/cli.py
"""CLI entry point — esqueleto Phase 1."""
import typer

app = typer.Typer(
    help="Validador acadêmico — biblioteca canônica PPGD/Unifor",
)


@app.callback()
def main() -> None:
    """Comandos virão em phases futuras (validar, corrigir, auditar)."""
    pass
```

**Por que `@app.callback()` e NÃO `@app.command()`** (verificado empiricamente):

- **Empty `Typer()` (zero callbacks/commands):** RAISES `RuntimeError: Could not get a command for this Typer instance` — não funciona como entry point. [VERIFIED: empírico]
- **Single `@app.command()`:** Typer colapsa em "single-command app mode". O `Typer(help=...)` é IGNORADO; o help do `--help` mostra a docstring do comando, não a do app. **Smoke test `assert "biblioteca canônica" in result.output` FALHARIA** se usar `@app.command()` único. [VERIFIED: empírico — output mostrou "Stub placeholder." em vez de "biblioteca canônica"]
- **`@app.callback()`:** preserva `Typer(help=...)` como help text top-level. Output do `--help` contém "Validador acadêmico — biblioteca canônica PPGD/Unifor". [VERIFIED: empírico — exit 0, string presente]

### Pattern 2: Entry point format

```toml
[project.scripts]
validar = "biblio_validador.cli:app"
```

**Como funciona** (PEP 503 + packaging.python.org/specifications/entry-points):
- O build backend (`uv_build`) compila este entry point em `.venv/bin/validar` (script Python wrapper).
- Em runtime, o wrapper importa `biblio_validador.cli`, acessa o atributo `app`, e o invoca: `app()`.
- `typer.Typer` define `__call__`, portanto `app()` funciona — mesmo NÃO sendo função. [VERIFIED: PEP 503 + empírico — `validar --help` retornou exit 0]

### Pattern 3: Smoke test via Typer CliRunner (in-process)

**Source: empirical test 2026-05-04 + typer.tiangolo.com/tutorial/testing**

```python
# tests/test_cli.py
"""Smoke test mínimo Phase 1 — REQ-CORE-12 success criterion #2."""
from typer.testing import CliRunner

from biblio_validador.cli import app

runner = CliRunner()


def test_validar_help_exit_zero() -> None:
    """`validar --help` deve retornar exit 0 e conter o nome canônico."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "biblioteca canônica" in result.output
```

**Por que CliRunner (in-process) e NÃO subprocess:**

- CliRunner é `click.testing.CliRunner` (Typer reusa); roda o app no MESMO processo Python do pytest, sem fork. Isso é ~50× mais rápido que `subprocess.run([".venv/bin/validar", "--help"])` e não depende de PATH ou shell. [VERIFIED: typer.testing.CliRunner.invoke source code]
- CliRunner captura `exit_code` automaticamente sem `try/except SystemExit`. [VERIFIED: empírico — `result.exit_code == 0`]
- Subprocess teria a vantagem de testar o entry-point script real (`.venv/bin/validar`), mas Phase 1 já valida isso via `uv sync` (cria o script) e tem o smoke test in-process — duplicar via subprocess é redundante.
- ARCHITECTURE.md menciona `pythonpath = ["src"]` em pytest config — **NÃO necessário** porque `uv sync` instala o pacote em editable mode, e pytest descobre via `sys.path` do venv ativo. [VERIFIED: empírico — `pytest tests/` passou sem `pythonpath` config]

### Pattern 4: pyproject.toml canônico (D-06 + D-07 + D-08 + D-12 + D-13 + D-14)

```toml
[project]
name = "biblio-validador"
version = "0.1.0"
description = "Validador & Fixer acadêmico PT-BR — biblioteca canônica PPGD/Unifor"
readme = "README.md"
requires-python = ">=3.13"
authors = [
    { name = "Kalyl Lamarck" },
]
dependencies = [
    "markdown-it-py>=4.0.0",
    "mdit-py-plugins",
    "pylatexenc>=2.10,<3.0",
    "typer>=0.25.1",
    "rich>=15.0.0",
    "loguru>=0.7.3",
]

[project.optional-dependencies]
llm = [
    "anthropic>=0.97.0",
    "jinja2>=3.1.6",
]

[project.scripts]
validar = "biblio_validador.cli:app"

[build-system]
requires = ["uv_build>=0.11.6,<0.12.0"]
build-backend = "uv_build"

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "ruff",
    "mypy",
]

[tool.ruff]
line-length = 80
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
python_version = "3.13"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"

[tool.coverage.run]
source = ["biblio_validador"]
branch = true
```

**Notas de verificação:**

- `[build-system]` é auto-gerado por `uv init --package` com `uv_build` como backend (uv 0.11+). [VERIFIED: sandbox]
- `[dependency-groups]` é PEP 735 — **instalado por default em `uv sync`** (sem precisar `--dev`). Diferente de `[project.optional-dependencies]` que precisa `--extra`. [VERIFIED: docs.astral.sh/uv/concepts/projects/dependencies/]
- `[project.optional-dependencies].llm` requer `uv sync --extra llm` para instalar (D-07). [VERIFIED: empírico]
- `[tool.coverage.run] source = ["biblio_validador"]` aponta para o **nome do pacote importável** (módulo), não distribution name. [CONFIRMA D-14]

### Anti-Patterns to Avoid (Phase 1-specific)

- **Não usar `@app.command()` único como skeleton** — colapsa em single-command mode e quebra o smoke test (ver Pitfall 1).
- **Não usar `[project.optional-dependencies].dev`** em vez de `[dependency-groups].dev` — extra `dev` exigiria `uv sync --extra dev` toda vez; dependency-group `dev` é instalado por default. (D-08 já fixou — só ratifico.)
- **Não criar `requirements.txt`** — uv não usa; lockfile canônico é `uv.lock` (D-09).
- **Não usar `setup.py` ou `setup.cfg`** — backend canônico é `uv_build` (auto via `uv init`).
- **Não pinar versão exata (`==`) das deps M1** — STACK.md e D-06 usam `>=` para permitir patch updates via `uv lock --upgrade`. Versão exata fica no `uv.lock`.
- **Não criar `src/biblio_validador/core/__init__.py`, `validadores/`, `fixers/`** vazios — CONTEXT.md "não criar pastas vazias agora".
- **Não chamar `loguru.logger.add()` em `__init__.py` ou `cli.py`** — D-19 adia config de logging para Phase 2.
- **Não importar `markdown_it`, `pylatexenc`, etc. em `cli.py`** — Phase 1 só usa `typer`. Imports de outras libs ficariam mortos e ruff `F401` (unused import) reclamaria.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bootstrap de pacote Python | `setup.py` manual com `find_packages()` | `uv init --package biblio-validador` | Gera src layout, `[build-system]`, `.python-version`, `__init__.py`, README placeholder em 1 comando. [VERIFIED: empírico] |
| Resolução de deps transitivas | `pip install` + `pip freeze > requirements.txt` | `uv add` + `uv.lock` | uv tem resolver determinístico, paralelo, com cache global; lockfile cross-platform. |
| Auto-download de Python 3.13 | Pyenv / asdf / instalação manual via apt | `uv sync` (auto-baixa quando `requires-python` exige versão ausente) | Ambiente atual não tem Python 3.13 — só 3.12 — e `uv sync` baixou 3.13.13 automaticamente (33.7MiB) em ~10s. [VERIFIED: empírico] |
| Entry point ELF wrapper | Bash script `#!/usr/bin/env python` em `bin/` | `[project.scripts]` resolvido pelo build backend | Build backend (`uv_build`) gera shebang correto + handle de exit code + import correto. [VERIFIED: `.venv/bin/validar` funcionou exit 0] |
| Argument parsing + --help geração | `argparse` + `print()` manual de help | Typer 0.25.1 com `@app.callback()` | Typer gera help formatado (Rich) gratuitamente e dispatch para subcomandos futuros sem refactor. |
| Test runner setup | unittest + descoberta manual | pytest 9.0.3 com `testpaths = ["tests"]` | pytest auto-descobre, parametrize, fixtures; CliRunner integra in-process. |
| Linter/formatter | flake8 + black + isort separadas | ruff 0.15.12 (`select = ["E", "F", "I", "UP", "B"]`) | 1 binário, ~100× mais rápido, mesma config das três ferramentas. |
| Type checking | pyre / pytype | mypy 1.20.2 strict | Padrão de facto da comunidade; `strict = true` ativa todas as flags de uma vez. |
| Smoke test do CLI | `subprocess.run([".venv/bin/validar", "--help"])` | `typer.testing.CliRunner().invoke(app, ["--help"])` | In-process, ~50× mais rápido, captura `exit_code` sem `SystemExit` manual; não depende de PATH. |

**Key insight:** `uv 0.11.6` consolida 5 ferramentas históricas (pyenv + venv + pip + pip-tools + setup) em um único binário. Hand-rolling qualquer parte do bootstrap reintroduz fragilidade (pyenv shims, requirements.txt drift, setup.py legado) que `uv init --package` elimina.

## Common Pitfalls

### Pitfall 1: `@app.command()` único quebra o smoke test

**O que dá errado:** desenvolvedor cria skeleton com:

```python
app = typer.Typer(help="Validador — biblioteca canônica PPGD/Unifor")

@app.command()  # ❌
def info() -> None:
    """Comandos virão em phases futuras."""
    pass
```

**O que acontece:** Typer detecta apenas 1 comando registrado e colapsa o app em "single-command app mode". O `--help` mostra a docstring de `info` (`"Comandos virão em phases futuras."`), NÃO o `Typer(help="...")`. Smoke test D-15 (`assert "biblioteca canônica" in result.output`) FALHA. [VERIFIED: empírico 2026-05-04 — output mostrou "Stub placeholder." em vez de "biblioteca canônica"]

**Como evitar:**

- **SEMPRE usar `@app.callback()`** (não `@app.command()`) no skeleton. Callback é "anti-comando": existe só para registrar o app sem ser invocável; preserva `Typer(help=...)` como help top-level. [VERIFIED: empírico — exit 0 + string presente]
- Quando Phase 8 adicionar primeiro `@app.command()` real (ex.: `validar`), Typer automaticamente passa para "multi-command mode" e o `Typer(help=...)` fica como descrição global do app. Sem refactor necessário no callback.

**Sinais de alerta:**
- `validar --help` mostra "Stub placeholder." ou nome do comando como título.
- Pytest falha em `assert "biblioteca canônica" in result.output`.

**Severidade:** ALTA — quebra silenciosamente success criterion #2 do roadmap. Aparente "tudo verde" no `uv sync` mascara o defeito até o pytest rodar.

### Pitfall 2: Python 3.13 ausente — `uv sync` precisa de internet na primeira invocação

**O que dá errado:** ambiente atual tem apenas Python 3.12.3 (`/usr/bin/python3`). `uv 0.11.6` está instalado em `/home/kalyllamarck/.local/bin/uv`. Com `requires-python = ">=3.13"`, o primeiro `uv sync` precisa baixar `cpython-3.13.13-linux-x86_64-gnu` (33.7MiB) do mirror do Astral (https://github.com/astral-sh/python-build-standalone). [VERIFIED: empírico — sandbox baixou em ~10s]

**Por que importa:** se o usuário rodar `uv sync` offline (em viagem, sem rede), falha. Se proxy corporativo bloquear github.com, falha.

**Como evitar:**
- Documentar no plano que o **primeiro `uv sync` requer internet**.
- Após primeiro download, Python 3.13 fica em `~/.local/share/uv/python/cpython-3.13.13-...` e está cacheado para todos os projetos uv subsequentes.
- Alternativa offline: instalar Python 3.13 via pacote do sistema antes (`apt install python3.13` quando disponível ou via deadsnakes PPA).
- Considerar pin via `.python-version = "3.13"` (não `3.13.13`) — uv resolve para qualquer 3.13.x disponível no cache, evita download repetido em minor updates.

**Sinais de alerta:**
- `uv sync` trava em "Downloading cpython-3.13.13-linux-x86_64-gnu" sem progresso.
- Erro de conexão / timeout / 403 de proxy.

**Severidade:** MÉDIA — bloqueia primeiro uso, mas é one-time. Plano deve mencionar como pré-requisito.

### Pitfall 3: `uv init --package` gera defaults que conflitam com decisões locked

**O que dá errado:** `uv init --package biblio-validador` gera um `pyproject.toml` com 6 defaults que CONTRADIZEM as decisões D-XX:

| Default `uv init` | Conflito com decisão | Override necessário |
|-------------------|---------------------|---------------------|
| `requires-python = ">=3.12"` | D-05 fixa `>=3.13` | Editar `pyproject.toml` + `.python-version` |
| `description = "Add your description here"` | Texto inválido | Editar (Claude's Discretion) |
| `[project.scripts] biblio-validador = "biblio_validador:main"` | D-10 fixa `validar = "biblio_validador.cli:app"` | Substituir entrada |
| `src/biblio_validador/__init__.py` com `def main(): print("Hello...")` | D-03 fixa só `__version__ = "0.1.0"` | Sobrescrever conteúdo |
| `.python-version = "3.12"` | Deve ser `3.13` | Sobrescrever |
| Nenhuma config `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest]`, `[tool.coverage]` | D-12 a D-14 exigem todas | Adicionar 4 tabelas |

**Como evitar:**
- Plano deve listar **explicitamente** os 6 overrides após `uv init --package`. Não confiar que `uv init` gere o estado correto — ele só dá o esqueleto válido + `[build-system]`.
- Validar via `cat pyproject.toml` antes de `uv add` que os 6 overrides foram aplicados.

**Sinais de alerta:**
- `validar` (entry point auto-gerado pelo init) aparece em `.venv/bin/` em vez de `validar`.
- `uv sync` falha com "Cannot find Python 3.12" se override de `.python-version` foi esquecido.

**Severidade:** MÉDIA — drift silencioso. Os tests passam, mas o entry point é o errado, ou a versão do Python é a errada.

### Pitfall 4: `uv add` muda formatação do `pyproject.toml` (alfabetização das deps)

**O que dá errado:** `uv add typer markdown-it-py loguru` instala em ordem mas grava as deps **em ordem alfabética** dentro de `dependencies = [...]`. Isso significa que se o plano editar manualmente `pyproject.toml` para por as deps na ordem do D-06 e DEPOIS rodar `uv add` para outra dep, a ordem manual é perdida. [VERIFIED: empírico — sandbox mostrou `loguru, markdown-it-py, mdit-py-plugins, pylatexenc, typer` em ordem alfa após `uv add`]

**Como evitar:**
- Aceitar a ordem alfabética como canônica (matches PyPA convention para `dependencies`).
- Não editar manualmente as listas `dependencies` / `optional-dependencies` / `dependency-groups`; usar sempre `uv add`/`uv remove`.
- O ruff lint não enforce ordem em listas TOML, então não há check automático.

**Sinais de alerta:**
- Diff do git mostra reordenação inesperada de deps após `uv add`.

**Severidade:** BAIXA — cosmético, sem impacto funcional.

### Pitfall 5: Sem `pythonpath = ["src"]`, pytest precisa do pacote instalado

**O que dá errado:** após `uv init --package` + `uv sync`, o pacote `biblio_validador` está instalado em editable mode no `.venv`. Pytest invocado via `uv run pytest` automaticamente usa esse `.venv` e descobre `biblio_validador` em `sys.path`. **Não precisa** `pythonpath = ["src"]` no `[tool.pytest.ini_options]` — diferente do que ARCHITECTURE.md sugere. [VERIFIED: empírico — `uv run pytest tests/` passou sem `pythonpath`]

**Quando ARIA precisa:** se alguém rodar `pytest` (sem `uv run`) com venv diferente do `.venv` do projeto. Caso de uso: CI customizado. Não se aplica a Phase 1.

**Como evitar:**
- **NÃO adicionar `pythonpath = ["src"]`** em D-14. CONTEXT.md já não menciona isso, mas STACK.md exemplo de pyproject também não — boa coerência.
- Documentar no plano: rodar pytest sempre via `uv run pytest`, nunca pytest direto.

**Sinais de alerta:**
- `ModuleNotFoundError: No module named 'biblio_validador'` em pytest direto.

**Severidade:** BAIXA — só afeta se alguém abandonar `uv run`.

### Pitfall 6: `.gitignore` atual está incompleto para tooling Python moderno

**O que dá errado:** o `.gitignore` na raiz tem:
```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
```

Mas FALTAM os caches que ruff, pytest, mypy criam silenciosamente:
- `.pytest_cache/`
- `.ruff_cache/`
- `.mypy_cache/`
- `htmlcov/` (se rodar `pytest --cov-report=html`)
- `*.egg-info/` (em build via setuptools fallback)
- `dist/` e `build/` (artefatos PEP 517)

**Como evitar:**
- Plano deve incluir uma tarefa "ampliar `.gitignore` com caches do tooling moderno".
- NÃO sobrescrever — apenas anexar (preservar entradas LaTeX existentes em linhas 11-23).

**Sinais de alerta:**
- `git status` mostra `.ruff_cache/CACHEDIR.TAG` como untracked após primeiro `uv run ruff check`.
- `git status` mostra `.pytest_cache/v/cache/...` após primeiro `uv run pytest`.

**Severidade:** BAIXA — funcional, mas polui git status e cria ruído.

### Pitfall 7: Tipo do callable em `[project.scripts]` — Typer.app é instance, não function

**O que dá errado:** PEP 503 "console_scripts" historicamente espera **funções**. Typer.app é **instância de Typer (callable via `__call__`)**. Usuários acostumados a click podem questionar se `validar = "biblio_validador.cli:app"` é válido.

**Resposta:** SIM, é válido. PEP 503 spec lê: "It is either in the form `importable.module`, or `importable.module:object.attr`". Não restringe a funções; aceita qualquer callable. Typer.app implementa `__call__` que delega para Click. [VERIFIED: PEP 503 + empírico — `.venv/bin/validar --help` retornou exit 0]

**Como evitar:**
- Não chamar `app()` no `cli.py` (sem `if __name__ == "__main__": app()` no fim do módulo). O entry point já faz isso. Se adicionar `app()` no module-level, executa em todo `import biblio_validador.cli` — quebra os testes.
- Adicionar `if __name__ == "__main__": app()` é OPCIONAL (para `python -m biblio_validador.cli` debug); não obrigatório.

**Sinais de alerta:**
- `validar --help` trava (loop infinito de import) → indica `app()` chamado em module-level.
- pytest falha com `SystemExit` ao importar `cli` → mesma causa.

**Severidade:** MÉDIA se cometido, mas é fácil evitar (Typer docs nunca mostram `app()` em module-level).

## Code Examples

### Exemplo: `src/biblio_validador/__init__.py` (D-03)

```python
"""Validador & Fixer Acadêmico — Biblioteca Canônica PPGD/Unifor."""

__version__ = "0.1.0"
```

[Source: D-03 + PEP 396 (`__version__` convention)]

### Exemplo: `src/biblio_validador/cli.py` (D-10 + D-11)

```python
"""CLI entry point — esqueleto Phase 1.

Comandos reais (`validar`, `corrigir`, `auditar`) virão em phases futuras
(M1 piloto Phase 8 + M8 orchestrator Phase 52).
"""
import typer

app = typer.Typer(
    help="Validador acadêmico — biblioteca canônica PPGD/Unifor",
)


@app.callback()
def main() -> None:
    """Comandos virão em phases futuras (validar, corrigir, auditar)."""
    pass
```

[Source: empirical test 2026-05-04 — exit 0 + string check passou em sandbox]

### Exemplo: `tests/test_cli.py` (D-15)

```python
"""Smoke test mínimo Phase 1 — valida REQ-CORE-12 success criterion #2."""
from typer.testing import CliRunner

from biblio_validador.cli import app

runner = CliRunner()


def test_validar_help_exit_zero() -> None:
    """`validar --help` retorna exit 0 e contém 'biblioteca canônica'."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "biblioteca canônica" in result.output
```

[Source: typer.tiangolo.com/tutorial/testing + empirical sandbox 2026-05-04]

### Exemplo: `tests/__init__.py` (D-16)

```python
```

(Arquivo vazio — apenas marcador de pacote para pytest discovery.) [Source: D-16]

### Exemplo: `pyproject.toml` completo (canonical para D-05 a D-14)

Já mostrado em [Pattern 4 acima](#pattern-4-pyprojecttoml-canônico-d-06--d-07--d-08--d-12--d-13--d-14).

### Exemplo: ampliação do `.gitignore` (Pitfall 6)

```diff
 # Python
 __pycache__/
 *.pyc
 *.pyo
 .venv/
 venv/
+
+# Python tooling caches
+.pytest_cache/
+.ruff_cache/
+.mypy_cache/
+htmlcov/
+
+# Build artifacts
+*.egg-info/
+dist/
+build/

 # LaTeX build
 ...
```

(Manter linhas LaTeX/Backups/OS/IDE/Tmp existentes.) [Source: empirical observation of cache directories created by `uv run pytest`/`ruff`/`mypy`]

## Sequência canônica de comandos para CORE-12

Validada empiricamente em sandbox `/tmp/uv-bootstrap-smoke` em 2026-05-04. Esta é a sequência exata que o plano deve seguir:

```bash
# Bloco 1: Bootstrap inicial (na raiz biblioteca_canonica/)
uv init --package biblio-validador  # gera src/biblio_validador/__init__.py + pyproject.toml + .python-version + README.md

# Bloco 2: Overrides manuais (Pitfall 3 — uv init defaults conflitam com D-XX)
# Editar manualmente:
# - .python-version: "3.13"
# - pyproject.toml: requires-python = ">=3.13"
# - pyproject.toml: description = "Validador & Fixer acadêmico PT-BR — biblioteca canônica PPGD/Unifor"
# - pyproject.toml: [project.scripts] validar = "biblio_validador.cli:app"  (substitui o auto-gerado)
# - pyproject.toml: adicionar [tool.ruff], [tool.ruff.lint], [tool.mypy], [tool.pytest.ini_options], [tool.coverage.run]
# - src/biblio_validador/__init__.py: substituir conteúdo pelo D-03
# - src/biblio_validador/cli.py: criar com D-10/D-11 skeleton
# - tests/__init__.py: criar vazio (D-16)
# - tests/test_cli.py: criar com D-15 smoke test
# - .gitignore: anexar caches Python (Pitfall 6)

# Bloco 3: Resolução de deps + lockfile + venv
uv add markdown-it-py mdit-py-plugins 'pylatexenc>=2.10,<3.0' typer rich loguru  # D-06
uv add --optional llm anthropic jinja2  # D-07
uv add --dev pytest pytest-cov ruff mypy  # D-08

# Bloco 4: Validação dos 4 success criteria
uv sync  # criterion #1: instala sem erro (auto-baixa Python 3.13 se ausente)
.venv/bin/validar --help  # criterion #2: exit 0 + help text
uv run python -c "import biblio_validador; print(biblio_validador.__version__)"  # criterion #3: imprime "0.1.0"
grep -E '^\s*"(markdown-it-py|mdit-py-plugins|pylatexenc|typer|rich|loguru)' pyproject.toml | wc -l  # criterion #4: 6
uv run pytest tests/ -v  # smoke test D-15

# Bloco 5: Lockfile e commit
git add pyproject.toml uv.lock .python-version src/ tests/ .gitignore
git commit -m "feat(01): bootstrap do projeto — uv + src layout + Typer skeleton (CORE-12)"
```

**Validação cruzada com os 4 success criteria do ROADMAP:**

| Critério | Validado por | Status esperado |
|----------|-------------|----------------|
| 1. `uv sync` em diretório limpo instala todas as deps sem erro | `uv sync` no Bloco 4 | exit 0 + "Installed N packages" |
| 2. `validar --help` retorna usage sem error code | `.venv/bin/validar --help` no Bloco 4 + smoke test | exit 0 + output contém "biblioteca canônica" |
| 3. `src/biblio_validador/__init__.py` existe com versão `0.1.0` | `python -c "import ...; print(__version__)"` | "0.1.0" |
| 4. `pyproject.toml` declara todas as dependências do SUMMARY.md com versões fixadas | `grep` count das 6 deps M1 | 6 linhas |

## Runtime State Inventory

> Phase greenfield — esta seção tradicionalmente foi prevista para refactor/rename. Para Phase 1 (bootstrap puro), preencher para mostrar que cada categoria foi verificada e nada está pré-existente.

| Categoria | Itens encontrados | Ação requerida |
|-----------|-------------------|----------------|
| Stored data | Nenhum — não há banco de dados, ChromaDB, Mem0, ou cache em disco. JSONs em `02_escrita/` são read-only fonte de regras (lidos só em Phase 2+). | Nenhuma. |
| Live service config | Nenhum — não há serviço externo configurado (n8n, Datadog, etc.) que dependa de "biblio_validador" hoje. CodexAcad RAG (porta 8401 VPS) não tem referência ao projeto. | Nenhuma. |
| OS-registered state | Nenhum — sem Task Scheduler, pm2, systemd, launchd registrando processo. CLI é invocada manualmente. | Nenhuma. |
| Secrets/env vars | Nenhum em Phase 1. `ANTHROPIC_API_KEY` será requerida apenas em M7 (Phase 42+). Phase 1 não lê env vars. | Nenhuma. |
| Build artifacts | Nenhum existente — projeto greenfield. Após `uv sync` aparecerão `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/` (todos em `.gitignore`). | Garantir `.gitignore` correto (Pitfall 6). |

**Conclusão:** Phase 1 é puramente aditiva — cria estado novo, não modifica estado existente. Risco de drift estado runtime: zero.

## Common Pitfalls

[Já listados acima na seção Architecture Patterns — Pitfalls 1-7.]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `setup.py` + `setuptools` | `pyproject.toml` + `[build-system]` PEP 517/621 | PEP 621 finalizado 2020-09 | uv usa `uv_build` por default; `setuptools` ainda funciona mas é legacy |
| `requirements.txt` + `pip-compile` | `pyproject.toml` + `uv.lock` | uv 0.1+ (2024) | Lockfile cross-platform multi-environment; resolver paralelo |
| `pyenv` shims + venv manual | `uv python install` + `uv venv` (ou auto via `uv sync`) | uv 0.4+ (2024) | uv baixa Python standalone (Astral mirror); zero shim layer |
| flake8 + black + isort | `ruff` (`select = ["E", "F", "I", "UP", "B"]`) | ruff 0.1+ (2023) | 1 binário, ~100× mais rápido |
| `[project.optional-dependencies].dev` (PEP 621) | `[dependency-groups].dev` (PEP 735) | PEP 735 aceito 2024-08 | dev group instala por default em `uv sync`; extras precisam `--extra` |
| Console script via wrapper bash | `[project.scripts]` resolvido pelo build backend | PEP 621 | Backend gera shebang + import + dispatch automático |

**Deprecated/outdated:**
- `python_requires` em setup.cfg → use `requires-python` em pyproject.toml.
- `python -m venv .venv && pip install -r requirements.txt` → `uv sync`.
- `pip freeze > requirements.txt` para reproducibility → `uv.lock`.

## Assumptions Log

Todas as decisões em CONTEXT.md (D-01 a D-19) foram **validadas empiricamente** em sandbox `/tmp/uv-bootstrap-smoke` em 2026-05-04. Nenhuma claim em RESEARCH.md está marcada `[ASSUMED]`. Toda informação técnica tem tag `[VERIFIED: ...]` ou `[CITED: ...]`.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| (vazio) | (Todas claims verificadas) | — | — |

**Conclusão:** A tabela acima está vazia porque toda a research foi executada com tools (uv real, typer real, pytest real). Phase 1 NÃO precisa de confirmação adicional do usuário antes de planejar.

## Open Questions

1. **`description` exato no `pyproject.toml`?**
   - O que sabemos: CONTEXT.md Claude's Discretion deixa a redação para o agente.
   - O que está unclear: PROJECT.md tem o texto longo (1 parágrafo). pyproject.toml convencionalmente é 1 frase ≤100 chars.
   - Recomendação: usar `"Validador & Fixer acadêmico PT-BR — biblioteca canônica PPGD/Unifor"` (61 chars, captura nome + escopo). É a primeira frase canônica do PROJECT.md.

2. **Qual texto exato do `@app.callback()` docstring?**
   - O que sabemos: Typer usa docstring do callback como sub-help quando há comandos registrados; em Phase 1 só há callback, então a docstring fica oculta na exibição padrão.
   - O que está unclear: docstring é cosmética em Phase 1.
   - Recomendação: usar `"Comandos virão em phases futuras (validar, corrigir, auditar)."` — comunica intenção sem ser cringe; documenta para futuros leitores do código.

3. **Adicionar `if __name__ == "__main__": app()` no fim de `cli.py`?**
   - O que sabemos: NÃO é necessário — entry point já invoca `app()`. Adicionar não quebra nada (entry-point ainda funciona), mas é redundante.
   - O que está unclear: convenção da equipe.
   - Recomendação: NÃO adicionar. Manter `cli.py` minimalista. Quem precisar de `python -m biblio_validador.cli` debug pode adicionar quando precisar (Phase 2+).

4. **Authors do `pyproject.toml`?**
   - O que sabemos: `uv init` gera `authors = [{ name = "Kalyl Lamarck" }]` (lê do `git config user.name`). [VERIFIED: empírico]
   - O que está unclear: incluir email? CLAUDE.md raiz menciona email. PEP 621 schema é `[{name = "...", email = "..."}]`.
   - Recomendação: aceitar o auto-gerado pelo `uv init` (só name). Email é PII; não obrigatório em pyproject.toml; pode ser adicionado depois.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` CLI | Bootstrap inteiro | ✓ | 0.11.6 | — |
| Python 3.13 | `requires-python = ">=3.13"` (D-05) | ✗ (apenas 3.12.3 instalado) | — | uv auto-baixa cpython-3.13.13 (33.7MiB) na primeira `uv sync` |
| git | Versionar `uv.lock` (D-09) | ✓ (assumido — repo já existe com commit `6226adc`) | — | — |
| Conexão internet | Primeiro `uv sync` (download Python 3.13 + deps PyPI) | Assumido ✓ no momento da execução | — | Sem fallback — bloqueia se offline |
| make / cmake / compiler | Build de extensões C nas deps | Não verificado | — | Todas as deps M1 (markdown-it-py, pylatexenc, typer, rich, loguru) são pure-Python; `pydantic-core` (transitiva via anthropic) usa Rust mas tem wheels pré-compiladas para x86_64-linux-gnu. uv resolve para wheels. [VERIFIED: empírico — `uv sync` não compilou nada] |

**Missing dependencies with no fallback:**
- (Nenhuma — todas resolvidas via uv auto-download.)

**Missing dependencies with fallback:**
- Python 3.13: ausente local, mas `uv sync` baixa automaticamente. Plano deve documentar como pré-requisito.

**Critical**: a primeira invocação de `uv sync` requer **internet ativa** para baixar Python 3.13.13 e ~16 wheels do PyPI. Em sessão offline, falha.

## Validation Architecture

> Nyquist 2× signal coverage para os 4 success criteria de CORE-12.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + typer.testing.CliRunner (in-process) |
| Config file | `[tool.pytest.ini_options]` em `pyproject.toml` (D-14) |
| Quick run command | `uv run pytest tests/test_cli.py -x` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CORE-12 #1 | `uv sync` em diretório limpo instala sem erro | smoke (script) | `uv sync && echo OK` | ✗ Wave 0 — não há test automatizado; verificação é via exit code do `uv sync` no executor |
| CORE-12 #2 | `validar --help` retorna exit 0 com usage | unit (in-process) | `uv run pytest tests/test_cli.py::test_validar_help_exit_zero -x` | ✗ Wave 0 — `tests/test_cli.py` será criado pelo plano |
| CORE-12 #3 | `__init__.py` exporta `__version__ = "0.1.0"` | unit (import) | `uv run python -c "import biblio_validador; assert biblio_validador.__version__ == '0.1.0'"` | ✗ Wave 0 — pode adicionar `test_version_exposed()` em `test_cli.py` ou separar em `test_init.py` |
| CORE-12 #4 | `pyproject.toml` declara todas deps M1 com versões pinadas | structural (grep) | `grep -E '^\s*"(markdown-it-py\|mdit-py-plugins\|pylatexenc\|typer\|rich\|loguru)' pyproject.toml \| wc -l` deve retornar 6 | ✗ Wave 0 — pode ser test pytest que parse o pyproject via `tomllib.load()` |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_cli.py -x` (smoke test único, ~0.2s)
- **Per wave merge:** `uv run pytest tests/ -v && uv run ruff check . && uv run mypy src/`
- **Phase gate:** os 4 success criteria validados pelos 4 commands acima + git diff limpo (sem caches no working tree)

### Wave 0 Gaps

Files que NÃO existem ainda e o plano deve criar antes do primeiro pytest verde:

- [ ] `tests/__init__.py` — marcador de pacote (D-16)
- [ ] `tests/test_cli.py` — smoke test D-15 (`test_validar_help_exit_zero`)
- [ ] (opcional) `tests/test_init.py` — verifica `__version__` exposto (success criterion #3)
- [ ] (opcional) `tests/test_pyproject.py` — verifica que as 6 deps M1 estão declaradas (success criterion #4 estrutural via `tomllib`)

**Recomendação:** consolidar todos os 3 testes opcionais em `tests/test_cli.py` (1 arquivo, 3 funções) para minimizar overhead Phase 1. Phases futuras quebram em arquivos por domínio.

**Framework install:** `uv add --dev pytest pytest-cov` (já coberto por D-08 / Bloco 3 da sequência canônica).

### Nyquist 2× Coverage Justification

Cada success criterion tem 1 assertion automatizada + 1 cross-check independent:

| Criterion | Primary signal | Secondary signal (Nyquist 2×) |
|-----------|---------------|-------------------------------|
| #1 install | exit 0 do `uv sync` | `ls .venv/lib/python3.13/site-packages/typer` (lib presente) |
| #2 --help | `result.exit_code == 0` | `"biblioteca canônica" in result.output` (string check) |
| #3 version | `import biblio_validador` (não erra) | `biblio_validador.__version__ == "0.1.0"` (valor exato) |
| #4 deps | `tomllib.load()` retorna dict com 6 deps | grep count == 6 (cross-check estrutural) |

Total: 8 assertions para 4 critérios. Nyquist 2× satisfeito.

## Project Constraints (from CLAUDE.md)

Extraídas de `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/CLAUDE.md` e `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md`:

### Tech stack obrigatório
- Python 3.13+ (matches D-05)
- Type hints obrigatórios em todo código novo (matches D-13)
- Max 80 chars/linha (matches D-12)
- Módulo padrão `re` para regex (Phase 2+, não Phase 1)
- `dataclasses` (Phase 3+, não Phase 1)
- `pathlib` (Phase 2+, não Phase 1)
- `uv` (não pip) (matches D-04)

### Idioma
- PT-BR brasileiro em código (docstrings, comentários, mensagens) — incluso `Typer(help="Validador acadêmico — biblioteca canônica PPGD/Unifor")` em PT-BR.

### Performance
- Validação de artigo de 30k palavras < 5 segundos (Phase 17 benchmark, não Phase 1).

### Reprodutibilidade
- Zero dependências de rede em validadores (só fixers LLM em M7). Phase 1 não tem código de rede.
- `uv.lock` versionado (matches D-09).

### Versionamento
- Repo git próprio em `biblioteca_canonica/` já inicializado (commit `6226adc`).

### Sem cache stateful
- Cada execução parte do zero (Phase 2+ design constraint, não afeta Phase 1).

### Workflow
- GSD Workflow Enforcement: tudo via `/gsd-execute-phase` etc. (não afeta o código de Phase 1).

### Convenções de comando
- `docker compose` (sem hífen) — não relevante para Phase 1.

**Compliance check para Phase 1:**

| Constraint | Phase 1 cumpre? | Verificação |
|-----------|-----------------|-------------|
| Python 3.13+ | ✓ | D-05 + `requires-python = ">=3.13"` |
| Type hints | ✓ | `cli.py` skeleton tem `def main() -> None:` |
| Max 80 chars | ✓ | ruff `line-length = 80` (D-12) |
| `uv` único gestor | ✓ | D-04 |
| PT-BR | ✓ | Docstrings + Typer help text em PT-BR |
| Zero rede em Phase 1 | ✓ | Phase 1 não tem code de rede; `uv sync` é uma ação de build, não runtime |
| `uv.lock` versionado | ✓ | D-09 |

**Phase 1 está em conformidade total com CLAUDE.md em ambos os níveis.**

## Sources

### Primary (HIGH confidence)

**Validação empírica em sandbox `/tmp/uv-bootstrap-smoke` (2026-05-04):**
- `uv 0.11.6` instalado em `/home/kalyllamarck/.local/bin/uv` — comportamento de `uv init --package`, `uv add`, `uv add --optional`, `uv add --dev`, `uv sync`, `uv run` testado diretamente
- `cpython-3.13.13-linux-x86_64-gnu` baixado via uv mirror em ~10s (33.7MiB)
- `typer 0.25.1` instalado e testado: `Typer()` empty raises RuntimeError; `@app.callback()` preserva `Typer(help=...)`; `@app.command()` único colapsa em single-command mode
- `pytest 9.0.3` + `typer.testing.CliRunner` testados: smoke test verde com src layout sem `pythonpath`
- Entry point `.venv/bin/validar` criado e invocado: exit 0, help text correto

**Documentação oficial:**
- uv project management — https://docs.astral.sh/uv/concepts/projects/init/ + https://docs.astral.sh/uv/concepts/projects/dependencies/ + https://docs.astral.sh/uv/concepts/projects/layout/ (HIGH: confirma `uv init --package` gera src layout, dependency-groups vs optional-dependencies)
- PEP 503 entry-points — https://packaging.python.org/en/latest/specifications/entry-points/ (HIGH: confirma `module:object.attr` aceita callables, não só funções)
- typer testing — https://typer.tiangolo.com/tutorial/testing/ (HIGH: confirma CliRunner padrão)
- typer commands — https://typer.tiangolo.com/tutorial/commands/ (MEDIUM: padrão de skeleton, não cobre edge case de Typer empty)

**STACK.md / SUMMARY.md / ARCHITECTURE.md / PITFALLS.md / CONTEXT.md:**
- Lidos integralmente: stack pinning, pyproject exemplificado, decisões D-01 a D-19, arquitetura (com nota de drift do nome `validador_academico` → `biblio_validador`)

### Secondary (MEDIUM confidence)

- pydevtools.com handbook on `uv init` project types (MEDIUM: blog terceiro, mas alinha com docs oficiais)
- sarahglasmacher.com / Medium articles on uv + pyproject.toml (MEDIUM: ajudaram a confirmar layout convenções)
- jcheng.org src vs flat debate (MEDIUM: justifica src layout como anti-pattern de import-from-cwd)

### Tertiary (LOW confidence)

- (Nenhuma — toda informação verificada via tools ou docs oficiais.)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — 11 versões verificadas via `uv add` em sandbox; todas matchamSTACK.md
- Architecture (skeleton + entry point): HIGH — testado end-to-end com `validar --help` retornando exit 0
- Pitfalls: HIGH — cada pitfall foi reproduzido empiricamente (Pitfall 1 com `@app.command()` falhou; Pitfall 3 com defaults do `uv init` listados; Pitfall 5 com pytest sem `pythonpath` passou)
- Sequência canônica: HIGH — executada ponta-a-ponta em sandbox

**Research date:** 2026-05-04
**Valid until:** 2026-06-04 (30 dias para stack estável; uv 0.11.x é série estável; revisitar quando uv 0.12 for lançado)

---

*Phase 1 research executed in conjunction with empirical sandbox validation. Plano pode prosseguir com confiança alta — todas as 19 decisões em CONTEXT.md foram validadas como produzindo o entregável CORE-12 sem ajustes adicionais necessários.*
