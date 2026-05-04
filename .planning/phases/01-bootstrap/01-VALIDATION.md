---
phase: 1
slug: bootstrap
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-04
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + typer.testing.CliRunner (in-process) |
| **Config file** | `[tool.pytest.ini_options]` em `pyproject.toml` (D-14) — Wave 0 cria |
| **Quick run command** | `uv run pytest tests/test_cli.py -x` |
| **Full suite command** | `uv run pytest tests/ -v && uv run ruff check . && uv run mypy src/` |
| **Estimated runtime** | ~2 segundos (smoke test in-process; ruff+mypy ~1s cada) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_cli.py -x`
- **After every plan wave:** Run full suite (pytest + ruff + mypy)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

> Tarefas concretas serão atribuídas pelo planner. Mapa preenchido aqui com placeholders correspondentes aos 4 success criteria de CORE-12. Planner refina IDs durante geração de PLAN.md.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-XX | 01 | 1 | CORE-12 (#1 install) | — | `uv sync` exit 0 sem erro | smoke | `uv sync` | ✅ executor cria pyproject.toml | ⬜ pending |
| 01-01-XX | 01 | 1 | CORE-12 (#2 --help) | — | `validar --help` exit 0 + contém "biblioteca canônica" | unit | `uv run pytest tests/test_cli.py::test_validar_help_exit_zero -x` | ❌ W0 (test não existe ainda) | ⬜ pending |
| 01-01-XX | 01 | 1 | CORE-12 (#3 version) | — | `import biblio_validador; assert __version__ == "0.1.0"` | unit | `uv run pytest tests/test_cli.py::test_version_exposed -x` | ❌ W0 | ⬜ pending |
| 01-01-XX | 01 | 1 | CORE-12 (#4 deps) | — | pyproject.toml declara 6 deps M1 com versões pinadas | structural | `uv run pytest tests/test_cli.py::test_pyproject_declares_m1_deps -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — marcador de pacote pytest (D-16)
- [ ] `tests/test_cli.py` — 3 testes consolidados:
  - `test_validar_help_exit_zero` (CORE-12 #2)
  - `test_version_exposed` (CORE-12 #3)
  - `test_pyproject_declares_m1_deps` (CORE-12 #4 via `tomllib.load()`)
- [ ] `pytest 9.0.3` + `pytest-cov 7.1.0` instalados via `uv add --dev` (D-08)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `validar` aparece em `.venv/bin/` após `uv sync` | CORE-12 #1 | Filesystem check fora do pytest scope | `test -x .venv/bin/validar && echo OK` (Wave gate manual) |
| `uv.lock` commitado no git | CORE-12 / D-09 | Git state, não runtime | `git ls-files | grep uv.lock` deve retornar 1 linha |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
