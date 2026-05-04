---
phase: 01-bootstrap
plan: 01
subsystem: infra
tags:
  - bootstrap
  - python
  - uv
  - typer
  - packaging
  - ruff
  - mypy
  - pytest

# Dependency graph
requires: []
provides:
  - "Pacote Python `biblio_validador` instalável via uv (src layout)"
  - "Entry point `validar` no PATH após `uv sync` (`@app.callback()` skeleton)"
  - "6 deps M1 fixadas: markdown-it-py, mdit-py-plugins, pylatexenc, typer, rich, loguru"
  - "Optional `llm` extra: anthropic, jinja2 (declarado, NÃO instalado em sync default)"
  - "Dev deps PEP 735: pytest 9.0.3, pytest-cov 7.1.0, ruff 0.15.12, mypy 1.20.2"
  - "`uv.lock` cross-platform commitado (D-09)"
  - "Tooling config canônico: ruff line-length=80 + mypy strict + pytest testpaths"
  - "3 smoke tests in-process via CliRunner (cobrem 4 success criteria CORE-12)"
affects:
  - 02-parser-md (consumirá markdown-it-py + token.map; logger.add inicializado aqui via D-19)
  - 03-dataclasses (importará biblio_validador como pacote já instalado)
  - todas as phases 2+ (bootstrap é pré-requisito estrutural)

# Tech tracking
tech-stack:
  added:
    - "uv 0.11.6 (gerenciador único — D-04)"
    - "Python 3.13.13 (auto-resolvido do cache uv)"
    - "typer 0.25.1 + click 8.3.3 (CLI dispatch)"
    - "rich 15.0.0 (output formatado)"
    - "loguru 0.7.3 (logging Phase 2+)"
    - "markdown-it-py 4.0.0 + mdit-py-plugins 0.5.0 (parser MD Phase 2)"
    - "pylatexenc 2.10 (parser LaTeX Phase 16+)"
    - "pytest 9.0.3 + pytest-cov 7.1.0 (test runner)"
    - "ruff 0.15.12 (linter+formatter — substitui flake8+black+isort)"
    - "mypy 1.20.2 (type checker strict)"
  patterns:
    - "src layout (PEP 621) — `src/biblio_validador/` editable install"
    - "PEP 735 dependency-groups para dev deps (instalado por default em uv sync)"
    - "Entry point `module:object.attr` apontando para Typer.app callable (PEP 503)"
    - "@app.callback() skeleton — preserva Typer(help=...) sem colapsar single-command"
    - "In-process smoke test via typer.testing.CliRunner (~50× mais rápido que subprocess)"
    - "Tooling config único em pyproject.toml (sem setup.cfg, sem requirements.txt)"

key-files:
  created:
    - "pyproject.toml — PEP 621 metadata + 6 deps M1 + optional llm + dev group + 4 [tool.*] tables"
    - ".python-version — pin Python 3.13"
    - "src/biblio_validador/__init__.py — `__version__ = '0.1.0'` (D-03)"
    - "src/biblio_validador/cli.py — Typer skeleton com @app.callback() (D-10/D-11 + Pitfall 1)"
    - "tests/__init__.py — marcador de pacote vazio (D-16)"
    - "tests/test_cli.py — 3 smoke tests cobrindo CORE-12 #2/#3/#4 (D-15 + Wave 0)"
    - "uv.lock — lockfile cross-platform hash-pinned (D-09)"
  modified:
    - ".gitignore — append-only: +.pytest_cache, +.ruff_cache, +.mypy_cache, +htmlcov, +*.egg-info, +dist, +build (Pitfall 6)"

key-decisions:
  - "Usar @app.callback() (NÃO @app.command()) no skeleton — Pitfall 1 ALTA: @app.command() único colapsa Typer em single-command mode e quebra smoke test silenciosamente"
  - "uv add re-alfabetiza deps automaticamente (Pitfall 4 cosmético) — aceitar como ordem canônica"
  - "Optional llm declarado mas NÃO instalado em uv sync default — economiza ~50MB durante M1-M6"
  - "PEP 735 [dependency-groups].dev em vez de [project.optional-dependencies].dev — instalação por default em sync, sem --extra"
  - "extend-exclude no [tool.ruff] para 01_templates/...05_metadados/ — legacy Python fora do scope Phase 1 (será normalizado em M8)"
  - "uv.lock commitado desde Phase 1 — reprodutibilidade dia 1, hash-pinned cross-platform"

patterns-established:
  - "Skeleton CLI Typer: app = typer.Typer(help='...PT-BR...') + @app.callback() def main() -> None: pass"
  - "Smoke test CLI: from typer.testing import CliRunner; runner.invoke(app, ['--help']); assert exit_code==0 and 'string' in output"
  - "Entry point PEP 503: validar = 'biblio_validador.cli:app' (Typer.app é callable)"
  - "Tooling pyproject.toml: ruff line-length=80 + select=[E,F,I,UP,B] + mypy strict + pytest testpaths=['tests']"
  - "Idioma PT-BR em docstrings, Typer help, descriptions e mensagens de erro (CLAUDE.md)"
  - "uv run pytest (não pytest direto — Pitfall 5)"

requirements-completed:
  - CORE-12

# Metrics
duration: 14min
completed: 2026-05-04
---

# Phase 01 Plan 01: Bootstrap & Tooling Summary

**Projeto Python `biblio-validador` instalável via uv com src layout, entry point `validar` no PATH, 3 smoke tests verdes e 6 deps M1 fixadas em pyproject.toml + uv.lock cross-platform commitado.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-05-04T15:02:22Z
- **Completed:** 2026-05-04T15:16:56Z
- **Tasks:** 3 (executed sequentially)
- **Files created:** 7
- **Files modified:** 1 (.gitignore append-only)

## Accomplishments

- Pacote `biblio_validador` 0.1.0 instalável via `uv sync` em editable mode com Python 3.13.13 auto-resolvido (sem download — cache hit)
- Entry point `validar` invocável diretamente em `.venv/bin/validar` retornando exit 0 com help text PT-BR contendo "biblioteca canônica" — Pitfall 1 mitigado via `@app.callback()`
- 6 deps M1 declaradas com versões pinadas (markdown-it-py 4.0.0, mdit-py-plugins 0.5.0, pylatexenc 2.10, typer 0.25.1, rich 15.0.0, loguru 0.7.3) + optional `llm` extra (anthropic 0.97.0, jinja2 3.1.6) declarado mas não instalado por default
- Tooling config completo em pyproject.toml: ruff (line-length=80, select=[E,F,I,UP,B]), mypy (strict=true, py3.13), pytest (testpaths=tests, --tb=short), coverage (source=biblio_validador, branch=true)
- 3 smoke tests in-process via CliRunner cobrindo CORE-12 #2/#3/#4 — passam em 0.13s
- Phase 1 gate completo verificado: pytest 3/3 + ruff check repo-wide + ruff format + mypy strict + uv sync idempotent + 4 success criteria CORE-12

## Task Commits

1. **Task 1: Scaffold projeto + overrides D-XX + arquivos novos** — `98ddde3` (feat)
2. **Task 2: Resolver dependências via uv add x3 + lockfile** — `d431be0` (chore)
3. **Task 3: Validar 4 success criteria + extend-exclude legacy** — `fb9fa5b` (chore)

## Files Created/Modified

### Created (7)
- `pyproject.toml` — PEP 621 metadata + 6 M1 deps + optional llm + PEP 735 dev group + 4 [tool.*] tables (ruff/mypy/pytest/coverage) + extend-exclude para legacy
- `.python-version` — pin "3.13" (uv resolve qualquer 3.13.x do cache)
- `src/biblio_validador/__init__.py` — `__version__ = "0.1.0"` (D-03, PEP 396)
- `src/biblio_validador/cli.py` — Typer app + `@app.callback()` skeleton em PT-BR (D-10/D-11)
- `tests/__init__.py` — vazio (D-16, marcador de pacote pytest)
- `tests/test_cli.py` — 3 smoke tests: `test_validar_help_exit_zero`, `test_version_exposed`, `test_pyproject_declares_m1_deps`
- `uv.lock` — lockfile hash-pinned cross-platform (43 packages resolvidos, D-09)

### Modified (1)
- `.gitignore` — append-only patch (Pitfall 6): +`.pytest_cache/`, +`.ruff_cache/`, +`.mypy_cache/`, +`htmlcov/`, +`*.egg-info/`, +`dist/`, +`build/`. Seções LaTeX/Backups/OS/IDE/Tmp preservadas verbatim.

## Decisions Made

Todas as 19 decisões D-01 a D-19 do CONTEXT.md foram aplicadas exatamente como locked. Decisões adicionais durante execução:

1. **`uv init --package --name biblio-validador .`** (em vez de `uv init --package biblio-validador`) — segunda forma cria subdiretório `./biblio-validador/`; primeira forma inicializa o cwd. README.md raiz preservado pelo uv init (não sobrescreveu o de 115 linhas existente).
2. **`extend-exclude` no [tool.ruff]** para `01_templates/`, `02_escrita/`, `03_fontes/`, `04_normas/`, `05_metadados/` — legacy Python em `01_templates/artigo_cientifico/app/gdocs/criar_template.py` flagaria E501+F401+F541 e bloquearia o gate. Estes diretórios pertencem à biblioteca canônica de dados, não ao projeto Python; serão integrados em M8 (Phases 55-57).
3. **Linha em branco entre `import typer` e o resto do código** — ruff format exige PEP 8 — foi inserida automaticamente.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `uv init --package biblio-validador` cria subdiretório**
- **Found during:** Task 1 (Passo 1 — uv init)
- **Issue:** O comando do plano `uv init --package biblio-validador` cria `./biblio-validador/` como subdiretório (uv interpreta o argumento posicional como path-or-name). Como queremos inicializar no cwd com o nome `biblio-validador`, é necessário separar nome de path.
- **Fix:** Removi o subdiretório e re-rodei como `uv init --package --name biblio-validador .` (cwd com nome explícito).
- **Files modified:** Nenhum permanente (subdiretório intermediário foi removido com `rm -rf`).
- **Verification:** Após o segundo `uv init`, files canônicos em `./pyproject.toml`, `./src/biblio_validador/__init__.py`, `./.python-version`, README.md original preservado (uv não sobrescreve readme existente em init).
- **Committed in:** Não impactou commits (corrigido antes de commit).

**2. [Rule 3 - Blocking] Legacy Python em `01_templates/` quebra `ruff check .`**
- **Found during:** Task 3 (passo 2 — ruff check repo-wide)
- **Issue:** `01_templates/artigo_cientifico/app/gdocs/criar_template.py` é um script gdocs render legacy com 7 violações ruff (E501 long lines, F401 unused import, F541 f-string sem placeholders). O plano AC-3.2 exige `uv run ruff check .` exit 0 — falha porque scaneia repo-wide. Esse arquivo NÃO é parte do projeto biblio_validador (CLAUDE.md raiz documenta `01_templates/` como módulo de geração de documentos do doutorado, separado do validador).
- **Fix:** Adicionei `extend-exclude = ["01_templates", "02_escrita", "03_fontes", "04_normas", "05_metadados"]` em `[tool.ruff]`. Excluí os 5 diretórios da biblioteca canônica de dados — projeto Python ocupa apenas `src/`, `tests/` e arquivos raiz como `pyproject.toml`/`*.py`. Comentário no pyproject explica que será removido seletivamente em M8 quando o orchestrator integrar pipeline LaTeX/GDocs.
- **Files modified:** `pyproject.toml` (+10 linhas em `[tool.ruff]`).
- **Verification:** `uv run ruff check .` → "All checks passed!"; `uv run ruff format --check .` → "4 files already formatted"; pytest e mypy seguem clean.
- **Committed in:** `fb9fa5b` (Task 3 commit).

**3. [Rule 1 - Bug] `uv add --optional llm` instala extras transientemente no venv**
- **Found during:** Task 2 (Passo 2 — uv add --optional)
- **Issue:** Plano AC-2.5 afirmou `! test -d .venv/lib/python3.13/site-packages/anthropic` após `uv add --optional`. Mas em uv 0.11.6, `uv add --optional <extra>` instala o extra IMEDIATAMENTE no venv ativo (para que o user possa testá-lo na sessão). Snapshot intermediário mostrou anthropic+jinja2+15 transitivos instalados.
- **Fix:** Não é bug — comportamento correto do uv 0.11. `uv sync` posterior (sem `--extra llm`) **uninstalou** anthropic+jinja2+15 transitivos automaticamente, restaurando steady state esperado pelo AC-2.5. Verificação final confirmou `! test -d .venv/lib/python3.13/site-packages/anthropic` após sync.
- **Files modified:** Nenhum (comportamento de uv, não código do plano).
- **Verification:** `uv sync` → "Uninstalled 17 packages" (anthropic + 16 transitivas); subsequente `test -d .venv/.../anthropic` retorna falso. AC-2.5 cumprido em steady state.
- **Committed in:** Não impactou commits — observação documentada aqui.

---

**Total deviations:** 3 auto-fixed (2 Rule 3 blocking, 1 Rule 1 bug observação)
**Impact on plan:** Todas as deviations resolvidas em Phase 1 sem retrabalho. Plano executou na ordem prescrita das 3 tasks; success criteria CORE-12 (#1/#2/#3/#4) cumpridos com 8 assertions independentes (Nyquist 2× preservado).

## Pitfalls Actively Mitigated

| Pitfall | Severidade | Mitigação aplicada | Verificação |
|---------|-----------|-------------------|-------------|
| #1 `@app.command()` único colapsa Typer | ALTA | `cli.py` usa `@app.callback()` exclusivamente; verify por grep `! grep -E "^@app\.command\("`; smoke test `assert "biblioteca canônica" in result.output` | `validar --help` mostra "Validador acadêmico — biblioteca canônica PPGD/Unifor" como help top-level (não docstring de comando) |
| #2 Primeira `uv sync` precisa internet (Python 3.13 download) | MÉDIA | Cache uv local já tinha cpython-3.13.13 — sem download necessário (`uv add` reportou "Using CPython 3.13.13") | Sem mensagem "Downloading cpython-3.13.13"; venv criada em ~22ms |
| #3 `uv init` defaults conflitam com D-XX | MÉDIA | 6 overrides explícitos aplicados: requires-python (já 3.13 — uv default), description (Add your description here → canônica), [project.scripts] (biblio-validador → validar=...cli:app), __init__.py (def main → __version__), .python-version (já 3.13), 4 [tool.*] tables adicionadas | Verify por grep: `! grep "biblio-validador = "`, `grep "validar = ..."`, `! grep "def main" __init__.py`, `grep -c "^\[tool\." pyproject.toml` ≥ 5 |
| #4 `uv add` re-alfabetiza deps | BAIXA | Aceita como ordem canônica — pyproject mostra deps em `loguru, markdown-it-py, mdit-py-plugins, pylatexenc, rich, typer` (alfabética) | Sem fix — diff git mostra ordem alfabética imediatamente |
| #5 Sem `pythonpath` no pytest | BAIXA | NÃO adicionado `pythonpath = ["src"]` em [tool.pytest.ini_options]; uv editable install resolve | `! grep "pythonpath" pyproject.toml`; pytest rodou via `uv run pytest` sem ModuleNotFoundError |
| #6 `.gitignore` incompleto para tooling Python moderno | BAIXA | Append-only patch: 7 linhas adicionadas em 2 seções novas (Python tooling caches, Build artifacts) entre as seções existentes Python e LaTeX. Verbatim preservation das seções LaTeX/Backups/OS/IDE/Tmp | `git status --short` retorna 0 untracked após `uv sync` + `pytest` + `ruff` (cachedirs ignorados); seções `# LaTeX build` + `*.synctex.gz` + `.DS_Store` ainda presentes |
| #7 `app()` em module-level ou `if __name__ == "__main__"` | MÉDIA | NÃO adicionado nenhum dos dois ao `cli.py`; entry point já invoca `app()` via PEP 503 wrapper | `! grep "if __name__ ==" cli.py`; pytest passa sem `SystemExit` no import |

## Verification Outputs (snippets)

```
$ uv run pytest tests/ -v
tests/test_cli.py::test_validar_help_exit_zero PASSED                    [ 33%]
tests/test_cli.py::test_version_exposed PASSED                           [ 66%]
tests/test_cli.py::test_pyproject_declares_m1_deps PASSED                [100%]
============================== 3 passed in 0.12s ===============================

$ uv run ruff check .
All checks passed!

$ uv run ruff format --check .
4 files already formatted

$ uv run mypy src/
Success: no issues found in 2 source files

$ uv sync
Resolved 43 packages in 1ms
Checked 24 packages in 0.31ms

$ .venv/bin/validar --help
 Usage: validar [OPTIONS] COMMAND [ARGS]...
 Validador acadêmico — biblioteca canônica PPGD/Unifor

$ .venv/bin/python -c "import biblio_validador; print(biblio_validador.__version__)"
0.1.0

$ grep -cE '^\s*"(markdown-it-py|mdit-py-plugins|pylatexenc|typer|rich|loguru)' pyproject.toml
6
```

## Issues Encountered

Nenhum issue não-coberto pelas 3 deviations acima. Plano executou exatamente como sequenciado em RESEARCH.md "Sequência canônica" Blocos 1-4. Bloco 5 (commit) foi feito por task individual (3 commits) em vez de commit único final, alinhado com CLAUDE.md "GSD Workflow" + execute-plan.md per-task atomic commits.

## User Setup Required

Nenhum — Phase 1 é puramente estrutural. Sem env vars, sem secrets, sem serviços externos. Phase 7 (M7 fixers LLM) será a primeira a precisar `ANTHROPIC_API_KEY`.

## Carryover into Phase 2

**Pronto para Phase 2 (Parser Markdown — REQ-CORE-01 + REQ-CORE-11):**
- `markdown-it-py 4.0.0` + `mdit-py-plugins 0.5.0` instalados — primeiro consumidor real do parser MD será o módulo `src/biblio_validador/parser/markdown.py` (Phase 2)
- `loguru 0.7.3` instalado mas D-19 adia `logger.add()` config para Phase 2 (primeiro consumidor real). Phase 2 deve criar `src/biblio_validador/log.py` com `logger.add(sys.stderr, level="INFO")` ou similar
- `unicodedata.normalize("NFC", text)` no parser para REQ-CORE-11 (PT-BR braces como ç, ã com decomposição NFD do filesystem). stdlib only.
- Token `token.map = [start_line, end_line]` é o mecanismo central para offsets byte-exact (REQ-CORE-01) — verificado em RESEARCH.md
- src layout permite `from biblio_validador.parser.markdown import parse_md` sem ajuste de pythonpath
- pytest config (testpaths=tests, --tb=short) já cobre `tests/test_parser_*.py` que Phase 2 criará

**Concerns / blockers para próxima phase:** nenhum bloqueador identificado. Phase 2 pode começar sem dependências adicionais.

## Threat Flags

Nenhuma — superficie de threat enumerada em PLAN.md `<threat_model>` foi mitigada conforme planejado (T-01-01 supply chain via uv.lock, T-01-03 defaults via overrides, T-01-06 spoofing via `@app.callback()`, T-01-07 reprodutibilidade via D-09). Sem novas threat surfaces introduzidas além das listadas.

## Self-Check: PASSED

**Files created (verified via test -f):**
- FOUND: pyproject.toml
- FOUND: .python-version
- FOUND: uv.lock
- FOUND: src/biblio_validador/__init__.py
- FOUND: src/biblio_validador/cli.py
- FOUND: tests/__init__.py
- FOUND: tests/test_cli.py

**Commits (verified via git log --oneline):**
- FOUND: 98ddde3 (Task 1)
- FOUND: d431be0 (Task 2)
- FOUND: fb9fa5b (Task 3)

---

*Phase: 01-bootstrap*
*Plan: 01*
*Completed: 2026-05-04*
