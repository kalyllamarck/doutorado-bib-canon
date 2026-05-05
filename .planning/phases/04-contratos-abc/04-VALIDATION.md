---
phase: 4
slug: contratos-abc
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-05
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + pytest-cov 7.1.0 (already installed via Phase 1 D-08) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.coverage.run]` herdado de Phase 1) |
| **Quick run command** | `uv run pytest tests/core/test_contracts.py -x` |
| **Full suite command** | `uv run pytest --cov=biblio_validador.core --cov-report=term-missing --cov-fail-under=95` |
| **Estimated runtime** | ~2 segundos (módulo pequeno, sem I/O além de fixtures JSON minúsculas) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/core/test_contracts.py -x`
- **After every plan wave:** Run `uv run pytest --cov=biblio_validador.core --cov-fail-under=95`
- **Before `/gsd-verify-work`:** Full suite must be green + mypy strict + ruff
- **Max feedback latency:** 5 segundos

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | CORE-04 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_validador_base_abstract_validar -x` | ❌ W0 | ⬜ pending |
| 4-01-02 | 01 | 1 | CORE-04 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_validador_base_abstract_carregar_regras -x` | ❌ W0 | ⬜ pending |
| 4-01-03 | 01 | 1 | CORE-04 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_carregar_regras_cache_hit -x` | ❌ W0 | ⬜ pending |
| 4-01-04 | 01 | 1 | CORE-04 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_carregar_regras_per_subclass_isolation -x` | ❌ W0 | ⬜ pending |
| 4-01-05 | 01 | 1 | CORE-04 | — | N/A | unit (error) | `uv run pytest tests/core/test_contracts.py::test_carregar_regras_file_not_found -x` | ❌ W0 | ⬜ pending |
| 4-01-06 | 01 | 1 | CORE-04 | — | N/A | unit (error) | `uv run pytest tests/core/test_contracts.py::test_carregar_regras_json_decode_error -x` | ❌ W0 | ⬜ pending |
| 4-01-07 | 01 | 1 | CORE-04 | — | N/A | unit (error) | `uv run pytest tests/core/test_contracts.py::test_carregar_regras_regex_error -x` | ❌ W0 | ⬜ pending |
| 4-01-08 | 01 | 1 | CORE-04 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_carregar_regras_normalizes_str_and_list -x` | ❌ W0 | ⬜ pending |
| 4-02-01 | 01 | 1 | CORE-05 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_fixer_base_abstract_propor_patches -x` | ❌ W0 | ⬜ pending |
| 4-02-02 | 01 | 1 | CORE-05 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_fixer_base_abstract_aplicar -x` | ❌ W0 | ⬜ pending |
| 4-02-03 | 01 | 1 | CORE-05 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_pode_corrigir_returns_true_for_known_id -x` | ❌ W0 | ⬜ pending |
| 4-02-04 | 01 | 1 | CORE-05 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_pode_corrigir_returns_false_for_unknown_id -x` | ❌ W0 | ⬜ pending |
| 4-02-05 | 01 | 1 | CORE-05 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_aplicacao_resultado_frozen_slots -x` | ❌ W0 | ⬜ pending |
| 4-02-06 | 01 | 1 | CORE-05 | — | N/A | unit | `uv run pytest tests/core/test_contracts.py::test_contexto_fixer_eq_false_unhashable_safe -x` | ❌ W0 | ⬜ pending |
| 4-03-01 | 01 | 1 | CORE-04, CORE-05 | — | N/A | smoke | `uv run python -c "from biblio_validador.core import FixerBase, ValidadorBase, ModoFixer, Scope, AplicacaoResultado, ContextoFixer"` | ❌ W0 | ⬜ pending |
| 4-03-02 | 01 | 1 | CORE-04, CORE-05 | — | N/A | static | `uv run mypy --strict src/biblio_validador/core/contracts.py src/biblio_validador/core/enums.py` | ❌ W0 | ⬜ pending |
| 4-03-03 | 01 | 1 | CORE-04, CORE-05 | — | N/A | lint | `uv run ruff check src/biblio_validador/core/ tests/core/test_contracts.py` | ❌ W0 | ⬜ pending |
| 4-03-04 | 01 | 1 | CORE-04, CORE-05 | — | N/A | coverage | `uv run pytest --cov=biblio_validador.core --cov-fail-under=95` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/core/__init__.py` — already created in Phase 3 (D-31), reusable
- [ ] `tests/core/test_contracts.py` — new test module covering CORE-04 + CORE-05
- [ ] `tests/core/fixtures/` — new directory for JSON fixtures
- [ ] `tests/core/fixtures/regras_fake.json` — happy path fixture (1 entrada `cst_999` com `regex_deteccao: "\\bfake\\b"`)
- [ ] `tests/core/fixtures/regras_malformadas.json` — JSON inválido (apenas `{`)
- [ ] `tests/core/fixtures/regras_regex_invalido.json` — entrada com regex `(?P<unfinished` para forçar `re.error`
- [ ] `tests/core/fixtures/regras_str_e_lista.json` — fixture com 2 entradas: uma com `regex_deteccao: str`, outra com `regex_deteccao: list[str]`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Mensagem da `re.error` inclui `regra_id` | CORE-04 (D-22) | Mensagem é texto humano para diagnóstico — assertion exata é frágil | Rodar fixture `regras_regex_invalido.json`, inspecionar visualmente que a exception message contém `regra cst_INVALIDO` |
| Documentação inline em PT-BR (docstrings) | Convenção do projeto | Estilo, não correção | Code review pelo autor antes de commit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (4 fixtures JSON + 1 test file + 1 init)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] Coverage threshold 95% set in `pyproject.toml` (herdado de Phase 1) — confirm `--cov-fail-under=95` no comando de full suite
- [ ] mypy strict passa em `core/contracts.py` e `core/enums.py`
- [ ] ruff passa em `src/biblio_validador/core/` e `tests/core/test_contracts.py`
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
