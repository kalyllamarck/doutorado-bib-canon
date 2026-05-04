# Phase 1: Bootstrap (CORE-12) - Pattern Map

**Mapped:** 2026-05-04
**Files analyzed:** 7 (5 NEW, 1 MODIFIED, 1 AUTO-GENERATED)
**Analogs found:** 7 / 7 (100% — all from RESEARCH.md empirical sandbox `/tmp/uv-bootstrap-smoke`)

## Pattern Source Note

This is a **greenfield Python project**. The repository contains zero pre-existing Python source — only data (38 JSONs across `01_templates/`, `02_escrita/`, `03_fontes/`, `04_normas/`, `05_metadados/`), `INDEX.json`, `README.md`, `CLAUDE.md`, and `.gitignore`.

Therefore, **the canonical pattern source is RESEARCH.md** (`.planning/phases/01-bootstrap/01-RESEARCH.md`), which documents an end-to-end empirical sandbox validation at `/tmp/uv-bootstrap-smoke` executed on 2026-05-04. Each "analog" below points to a specific RESEARCH.md section that contains the exact tested code. The planner must treat these excerpts as the canonical shape — they are not aspirational; they were executed and produced exit 0 + green pytest in the sandbox.

The only intra-repo analog is `.gitignore`, which exists and must be **appended to** (not rewritten).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `pyproject.toml` | config | static-declarative | RESEARCH.md §"Pattern 4: pyproject.toml canônico" (lines 294-354) | exact (sandbox-verified) |
| `.python-version` | config | static-declarative | RESEARCH.md §"Sequência canônica" Bloco 2 + §"Recommended Project Structure" (lines 200-220) | exact (auto-emitted by `uv init` then overridden) |
| `src/biblio_validador/__init__.py` | package init | static-declarative | RESEARCH.md §"Code Examples" → "Exemplo: __init__.py" (lines 537-543) | exact (PEP 396 + D-03) |
| `src/biblio_validador/cli.py` | CLI entry | request-response (CLI dispatch) | RESEARCH.md §"Pattern 1" + §"Code Examples" → "Exemplo: cli.py" (lines 547-565) | exact (sandbox-verified, fixes Pitfall 1) |
| `tests/__init__.py` | test package marker | n/a | RESEARCH.md §"Code Examples" → "Exemplo: tests/__init__.py" (lines 588-593) | exact (D-16) |
| `tests/test_cli.py` | test (CLI smoke) | in-process invocation | RESEARCH.md §"Pattern 3" + §"Code Examples" → "Exemplo: test_cli.py" (lines 569-586) | exact (sandbox-verified) |
| `.gitignore` (MODIFIED) | config | static-declarative | `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/.gitignore` (existing, lines 1-42) + RESEARCH.md §"Code Examples" → "Exemplo: ampliação do .gitignore" (lines 599-622) | exact (append-only, preserves existing LaTeX/IDE entries) |
| `uv.lock` | lockfile | auto-generated | n/a — produced by `uv sync` | n/a (not hand-written; commit only) |

## Pattern Assignments

### `pyproject.toml` (config, static-declarative)

**Analog:** RESEARCH.md §"Pattern 4: pyproject.toml canônico (D-06 + D-07 + D-08 + D-12 + D-13 + D-14)" lines 294-354 — sandbox-verified canonical TOML.

**Generation strategy** (RESEARCH.md §"Sequência canônica" Bloco 1-2):
1. Run `uv init --package biblio-validador` to scaffold (auto-emits `[build-system]`, `authors`, basic `[project]`).
2. Override 6 default fields explicitly (Pitfall 3) — `requires-python`, `description`, `[project.scripts]`, contents of `__init__.py`, `.python-version`, plus add 4 missing `[tool.*]` tables.
3. Use `uv add` (not manual edit) for dependencies — uv writes them in alphabetical order automatically (Pitfall 4).

**Full canonical content** (RESEARCH.md lines 296-354, sandbox-verified):

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

**Critical conventions to copy** (do not deviate):

- Distribution name = `biblio-validador` (hyphen, PEP 503); module name = `biblio_validador` (underscore, PEP 8). uv normalizes the hyphen to underscore for the filesystem path. (D-01)
- `[build-system]` uses `uv_build`, not `setuptools` — auto-emitted by `uv init --package`.
- Dev deps go in `[dependency-groups]` (PEP 735, installed by default on `uv sync`), NOT `[project.optional-dependencies]` (would require `--extra dev` every time). (D-08)
- `[project.optional-dependencies].llm` deliberately keeps anthropic/jinja2 OUT of default install — saves ~50MB during M1-M6.
- `[tool.coverage.run] source = ["biblio_validador"]` references the **module name** (importable), NOT the distribution name.

---

### `.python-version` (config, static-declarative)

**Analog:** RESEARCH.md §"Sequência canônica" Bloco 1-2 + Pitfall 3 (line 442 — table row "default `3.12` must be overridden to `3.13`").

**Content** (single line, no trailing newline-sensitive issues):

```
3.13
```

**Why pin to `3.13` (not `3.13.13`):** RESEARCH.md Pitfall 2 (line 428) — "uv resolves to any 3.13.x available in the cache, evita download repetido em minor updates." `uv sync` auto-downloads `cpython-3.13.13-linux-x86_64-gnu` (~33.7 MiB) on first invocation if 3.13 is absent.

---

### `src/biblio_validador/__init__.py` (package init, static-declarative)

**Analog:** RESEARCH.md §"Code Examples" → "Exemplo: __init__.py" lines 537-543. Decision D-03.

**Full canonical content** (PEP 396 `__version__` convention, single public attribute for Phase 1):

```python
"""Validador & Fixer Acadêmico — Biblioteca Canônica PPGD/Unifor."""

__version__ = "0.1.0"
```

**Critical conventions:**

- Module docstring in PT-BR (CLAUDE.md "Idioma" rule — applies to docstrings, comments, error messages).
- Single public symbol: `__version__`. No re-exports of classes, no imports from `cli` — Phase 1 keeps the public surface minimal; classes will be exported from Phase 2+ as they materialize.
- **DO NOT** call `loguru.logger.add()` here (D-19 defers logging config to Phase 2).
- **DO NOT** import `markdown_it`, `pylatexenc`, etc. — those imports would be dead code and ruff `F401` would flag them (RESEARCH.md "Anti-Patterns to Avoid", line 372).
- The default `def main(): print("Hello...")` emitted by `uv init --package` MUST be replaced wholesale (Pitfall 3).

---

### `src/biblio_validador/cli.py` (CLI entry, request-response)

**Analog:** RESEARCH.md §"Pattern 1: Typer skeleton via `@app.callback()`" (lines 228-253) + §"Code Examples" → "Exemplo: cli.py" (lines 547-565). Decisions D-10, D-11. Sandbox-verified — exit 0 + smoke test green.

**Full canonical content:**

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

**Imports pattern** (single import, stdlib-first ordering not applicable since only 1 import):

```python
import typer
```

No `from X import Y` aliasing — direct module access (`typer.Typer`) makes it explicit which library provides the symbol. ruff `I` (isort) will leave this single import as-is.

**Core CLI dispatch pattern** (the load-bearing decision, RESEARCH.md Pitfall 1, severity ALTA):

```python
app = typer.Typer(
    help="Validador acadêmico — biblioteca canônica PPGD/Unifor",
)


@app.callback()                                    # NOT @app.command()
def main() -> None:
    """Comandos virão em phases futuras (validar, corrigir, auditar)."""
    pass
```

**WHY `@app.callback()` and NOT `@app.command()` — verified empirically in sandbox 2026-05-04:**

- Empty `Typer()` with zero callbacks/commands raises `RuntimeError: Could not get a command for this Typer instance` — broken entry point.
- Single `@app.command()` collapses Typer into "single-command app mode": `--help` shows the command's docstring, NOT the `Typer(help=...)` text. Smoke test `assert "biblioteca canônica" in result.output` would FAIL.
- `@app.callback()` is the only shape that preserves `Typer(help=...)` as the top-level help text in Phase 1, AND transparently transitions to multi-command mode in Phase 8 when the first real `@app.command()` is added — no refactor needed.

**Anti-patterns to avoid** (RESEARCH.md Pitfall 7, lines 517-531):

- **DO NOT** add `if __name__ == "__main__": app()` at module bottom — entry point already invokes `app()`. If duplicated at module level, `app()` runs on every `import biblio_validador.cli` and breaks tests with `SystemExit`.
- **DO NOT** call `app()` directly in module body for the same reason.
- **DO NOT** import `markdown_it`, `pylatexenc`, `loguru`, etc. — Phase 1 only uses `typer`. Other imports are dead and ruff `F401` flags them.

**Type hint pattern** (CLAUDE.md mandates, D-13 strict mypy):

```python
def main() -> None:
    ...
```

Every function gets a return annotation, even `None`. Strict mypy enforces this.

**Style pattern** (D-12 ruff `line-length = 80`):

The `Typer(...)` constructor breaks across lines because the help string + closing paren would exceed 80 chars on a single line. Ruff format prefers vertical alignment with closing paren on its own line.

---

### `tests/__init__.py` (test package marker)

**Analog:** RESEARCH.md §"Code Examples" → "Exemplo: tests/__init__.py" (lines 588-593). Decision D-16.

**Content:** empty file.

**Why an empty `__init__.py` matters:** marks `tests/` as a Python package so pytest discovery treats `tests/test_cli.py` consistently regardless of pytest's rootdir resolution. Not strictly needed in modern pytest with `pyproject.toml` `testpaths`, but the cost is zero and it prevents subtle `conftest.py` collection ambiguities once Phase 2+ tests grow.

---

### `tests/test_cli.py` (test, in-process CLI invocation)

**Analog:** RESEARCH.md §"Pattern 3: Smoke test via Typer CliRunner (in-process)" (lines 268-292) + §"Code Examples" → "Exemplo: test_cli.py" (lines 569-586). Decision D-15. Sandbox-verified green.

**Full canonical content:**

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

**Imports pattern** (stdlib-first → third-party → local — ruff `I` enforces this ordering):

```python
from typer.testing import CliRunner    # third-party

from biblio_validador.cli import app   # local (blank line between groups)
```

**Core test pattern** (in-process invocation, NOT subprocess):

```python
runner = CliRunner()                                 # module-level instance
result = runner.invoke(app, ["--help"])              # in-process call
assert result.exit_code == 0                         # primary signal
assert "biblioteca canônica" in result.output        # secondary signal (Nyquist 2×)
```

**WHY in-process via `CliRunner` (NOT `subprocess.run([".venv/bin/validar", ...])`):** RESEARCH.md lines 287-292 — CliRunner runs the app in the same Python process as pytest, ~50× faster, no PATH/shell dependency, captures `exit_code` automatically without `try/except SystemExit`. The entry-point script existence is already validated separately by `uv sync` creating `.venv/bin/validar`; doubling up via subprocess in the test would be redundant.

**Validation pattern** (Nyquist 2× — RESEARCH.md "Validation Architecture" lines 800-809):

Two independent assertions per success criterion:

| Signal type | Assertion |
|-------------|-----------|
| Primary (exit code) | `result.exit_code == 0` |
| Secondary (content) | `"biblioteca canônica" in result.output` |

The secondary assertion is the load-bearing check that catches Pitfall 1 (`@app.command()` would print "Comandos virão em phases futuras." instead of "biblioteca canônica" and exit 0 still passes — only the content assertion catches the regression).

**Optional extension (RESEARCH.md "Wave 0 Gaps" line 793-794):** consolidate into the same file two more tests covering success criteria #3 (version exposed) and #4 (deps declared). Recommended single-file shape:

```python
"""Smoke tests Phase 1 — valida 4 success criteria de CORE-12."""
import tomllib
from pathlib import Path

from typer.testing import CliRunner

import biblio_validador
from biblio_validador.cli import app

runner = CliRunner()


def test_validar_help_exit_zero() -> None:
    """Criterion #2: `validar --help` retorna exit 0 + nome canônico."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "biblioteca canônica" in result.output


def test_version_exposed() -> None:
    """Criterion #3: `biblio_validador.__version__` == '0.1.0'."""
    assert biblio_validador.__version__ == "0.1.0"


def test_pyproject_declares_m1_deps() -> None:
    """Criterion #4: pyproject.toml declara as 6 deps M1."""
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = " ".join(data["project"]["dependencies"])
    for required in (
        "markdown-it-py",
        "mdit-py-plugins",
        "pylatexenc",
        "typer",
        "rich",
        "loguru",
    ):
        assert required in deps, f"M1 dep ausente: {required}"
```

The planner may keep just `test_validar_help_exit_zero` (D-15 minimum) or include all three. Keeping all three closes the Wave 0 gap that RESEARCH.md flags (line 786).

**`pythonpath` anti-pattern note** (RESEARCH.md Pitfall 5, lines 473-486): **DO NOT** add `pythonpath = ["src"]` to `[tool.pytest.ini_options]`. After `uv sync`, the package is installed in editable mode and pytest discovers `biblio_validador` via `sys.path` of the active `.venv`. The `pythonpath` config would be required only if running `pytest` outside `uv run`, which is not Phase 1's contract.

---

### `.gitignore` (MODIFIED) (config, static-declarative)

**Analog:** the existing file at the repo root, `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/.gitignore` (42 lines, sections: Python / LaTeX build / Backups / OS / IDE / Tmp).

**Existing relevant content** (lines 1-6):

```
# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
```

**Patch pattern** (RESEARCH.md §"Code Examples" → "Exemplo: ampliação do `.gitignore`" lines 599-622, Pitfall 6):

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

**Critical conventions:**

- **APPEND ONLY** — preserve existing LaTeX (lines 8-23), Backups (24-27), OS (29-31), IDE (33-37), Tmp (39-41) sections verbatim.
- Insert the two new sections (`Python tooling caches`, `Build artifacts`) BETWEEN the existing `# Python` block and the `# LaTeX build` block.
- The existing `**/build/` line (LaTeX section) ALREADY catches `build/` from PEP 517; the explicit `build/` line in the new "Build artifacts" section is redundant but harmless — keep it for clarity (it makes the Python tooling block self-documenting).

---

### `uv.lock` (auto-generated)

**Analog:** none — file is produced by `uv sync` and committed verbatim per D-09.

**Conventions:**

- **DO NOT** hand-edit. Always regenerate via `uv lock` or `uv sync`.
- **DO** commit to git from Phase 1 onward (D-09, RESEARCH.md "State of the Art" line 696 — lockfile cross-platform reproducibility).
- The first `uv sync` requires internet (RESEARCH.md Pitfall 2) — downloads cpython-3.13.13 (~33.7 MiB) plus ~16 wheels.

## Shared Patterns

### Language convention (all human-readable strings)

**Source:** `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` "Idioma: português brasileiro" + `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/CLAUDE.md` "Idioma: PT-BR brasileiro".
**Apply to:** all docstrings, all `Typer(help=...)` and `Typer(...)` strings, all assertion messages, all `description` in `pyproject.toml`.

Examples already in canonical excerpts:

```python
"""Validador & Fixer Acadêmico — Biblioteca Canônica PPGD/Unifor."""
help="Validador acadêmico — biblioteca canônica PPGD/Unifor"
"""Comandos virão em phases futuras (validar, corrigir, auditar)."""
```

```toml
description = "Validador & Fixer acadêmico PT-BR — biblioteca canônica PPGD/Unifor"
```

The smoke-test assertion `"biblioteca canônica" in result.output` depends on this convention being applied consistently to the `Typer(help=...)` string. Drift to English breaks the smoke test.

### Style enforcement

**Source:** RESEARCH.md §"pyproject.toml canônico" lines 336-345 (D-12, D-13).
**Apply to:** every `.py` file written in Phase 1 (so just `__init__.py`, `cli.py`, `tests/__init__.py`, `tests/test_cli.py`).

```toml
[tool.ruff]
line-length = 80
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
python_version = "3.13"
```

Concrete implications for every new `.py`:

- **Max 80 chars/line** — applies to `cli.py` Typer constructor (already wrapped vertically), and any future docstring lines.
- **Type hints mandatory** — `def main() -> None:` not `def main():` (mypy strict will fail otherwise; D-13).
- **Import ordering**: stdlib → third-party → local, blank line between groups. Ruff `I` rule. Demonstrated in `tests/test_cli.py` excerpt above.
- **`UP` rule** (pyupgrade): use `X | Y` instead of `Union[X, Y]`, `list[int]` instead of `List[int]` (Python 3.13 native syntax). No occurrences in Phase 1 code, but informs Phase 2+.
- **`B` rule** (bugbear): prevents common bugs like mutable default args. No occurrences in Phase 1.

### Test invocation contract

**Source:** RESEARCH.md Pitfall 5 + §"Validation Architecture" lines 763-783.
**Apply to:** all test runs in Phase 1 and onward.

Always invoke pytest via `uv run`, never bare `pytest`:

```bash
uv run pytest tests/                       # full suite
uv run pytest tests/test_cli.py -x         # quick fail-fast
uv run pytest tests/test_cli.py::test_validar_help_exit_zero -x  # single test
```

Bare `pytest` would only work if the user activated `.venv` first; `uv run` is the universal contract.

### Dependency management contract

**Source:** RESEARCH.md "Don't Hand-Roll" line 379 + Pitfall 4 line 461.
**Apply to:** any future addition/removal of dependencies during Phase 1 execution.

- Use `uv add <pkg>` for runtime deps (writes to `[project.dependencies]`).
- Use `uv add --optional <extra> <pkg>` for extras (writes to `[project.optional-dependencies].<extra>`).
- Use `uv add --dev <pkg>` for dev deps (writes to `[dependency-groups].dev`).
- **NEVER** hand-edit dependency lists in `pyproject.toml` — uv re-alphabetizes them on next `uv add`, losing manual ordering (Pitfall 4, severity BAIXA, but creates noise in git diffs).

## Sequenced Action Pattern (canonical execution order)

**Source:** RESEARCH.md §"Sequência canônica de comandos para CORE-12" lines 626-662 — sandbox-validated end-to-end.

The planner must ensure plan actions follow this exact order to avoid Pitfall 3 (uv init defaults conflicting with locked decisions):

1. **Bootstrap** (`uv init --package biblio-validador`) — creates `pyproject.toml` skeleton, `src/biblio_validador/__init__.py`, `.python-version`, and a `[build-system]` block with `uv_build`.
2. **Override 6 defaults** (manual edits — Pitfall 3 lines 437-457): `requires-python`, `description`, `[project.scripts]`, `__init__.py` content, `.python-version` value, plus add 4 missing `[tool.*]` tables.
3. **Add new files**: `src/biblio_validador/cli.py`, `tests/__init__.py`, `tests/test_cli.py`.
4. **Append to `.gitignore`**: 7 new lines for tooling caches and build artifacts.
5. **Resolve deps via `uv add`** in 3 passes: core (D-06), `--optional llm` (D-07), `--dev` (D-08).
6. **Validate** the 4 success criteria via `uv sync`, `validar --help`, `python -c "import biblio_validador"`, `grep` deps count, `uv run pytest`.
7. **Commit** `pyproject.toml`, `uv.lock`, `.python-version`, `src/`, `tests/`, `.gitignore`.

Skipping or reordering steps 1-2 would let `uv init` defaults leak into the final state (e.g., `requires-python = ">=3.12"`, `[project.scripts] biblio-validador = "biblio_validador:main"` instead of `validar = "biblio_validador.cli:app"`).

## No Analog Found

(none — every file has either an empirical sandbox match in RESEARCH.md or an in-repo analog in `.gitignore`.)

## Pitfall Cross-Reference (for planner action gates)

| Pitfall | Severity | Affected file | Mitigation embedded in pattern excerpts above |
|---------|----------|---------------|------------------------------------------------|
| #1 `@app.command()` collapses single-command mode | ALTA | `cli.py` | Use `@app.callback()` (shown in canonical excerpt) |
| #2 First `uv sync` needs internet (auto-download Python 3.13) | MÉDIA | `pyproject.toml` / `.python-version` | Document in plan; pin `.python-version = "3.13"` (not `3.13.13`) |
| #3 `uv init` defaults conflict with D-XX | MÉDIA | `pyproject.toml`, `__init__.py`, `.python-version` | Apply 6 explicit overrides (listed in Sequenced Action Pattern step 2) |
| #4 `uv add` re-alphabetizes deps | BAIXA | `pyproject.toml` | Accept alphabetical order; never hand-edit dep lists |
| #5 No `pythonpath` needed | BAIXA | `pyproject.toml` `[tool.pytest.ini_options]` | DO NOT add `pythonpath = ["src"]` (canonical excerpt does not include it) |
| #6 `.gitignore` missing tooling caches | BAIXA | `.gitignore` | Append 7 lines (canonical diff above) |
| #7 `app()` at module level breaks tests | MÉDIA | `cli.py` | DO NOT add `if __name__ == "__main__": app()` (canonical excerpt does not include it) |

## Metadata

**Analog search scope:** repo root + `.planning/phases/01-bootstrap/` + RESEARCH.md sandbox at `/tmp/uv-bootstrap-smoke` (referenced empirically).
**Files scanned:** repo root listing (4 entries: `INDEX.json`, `README.md`, `CLAUDE.md`, `.gitignore`), confirmed zero `.py` files anywhere in tree, confirmed no `pyproject.toml` / `uv.lock` exist.
**Pattern extraction date:** 2026-05-04
**Confidence:** HIGH — every excerpt is sandbox-validated (RESEARCH.md confidence breakdown lines 892-895) or copied verbatim from the existing `.gitignore` patch context.
