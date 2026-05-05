---
phase: 3
slug: dataclasses-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-05
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derivado de `03-RESEARCH.md` §"Validation Architecture" (Nyquist Dim 8).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + pytest-cov 7.1.0 (Phase 1 D-08) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (Phase 1 D-14) |
| **Quick run command** | `uv run pytest tests/core/ -x --tb=short` |
| **Full suite command** | `uv run pytest --cov=biblio_validador --cov-report=term-missing` |
| **Estimated runtime** | < 1 second (testes puros sem I/O) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/core/ -x --tb=short`
- **After every plan wave:** Run `uv run pytest --cov=biblio_validador --cov-report=term-missing`
- **Before `/gsd-verify-work`:** Full suite green AND `pytest --cov-fail-under=95` para módulos `biblio_validador.core`
- **Max feedback latency:** ~1 segundo

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | CORE-02 | — | Violacao instancia com frozen+slots | unit | `uv run pytest tests/core/test_dataclasses.py::test_violacao_instancia_com_frozen_e_slots -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | CORE-02 | — | FrozenInstanceError ao mutar regra_id | unit | `uv run pytest tests/core/test_dataclasses.py::test_violacao_frozen_raises_on_mutate -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | CORE-02 | — | dataclasses.asdict retorna dict válido | unit | `uv run pytest tests/core/test_dataclasses.py::test_violacao_asdict_estrutural -x` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | CORE-02 | — | json.dumps(to_dict()) round-trip | contract | `uv run pytest tests/core/test_dataclasses.py::test_violacao_to_dict_json_roundtrip -x` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | CORE-02 | — | Violacao invariantes raise (linha<1, col_fim<col_inicio) | unit (parametrize) | `uv run pytest tests/core/test_dataclasses.py::test_violacao_invariantes_raise -x` | ❌ W0 | ⬜ pending |
| 03-01-06 | 01 | 1 | CORE-02 | — | Severidade.peso() monotônica INFO<ALERTA<ERRO<CRITICO | unit | `uv run pytest tests/core/test_dataclasses.py::test_severidade_peso_monotonica -x` | ❌ W0 | ⬜ pending |
| 03-01-07 | 01 | 1 | CORE-03 | — | Patch slots; mutação de estado permitida | unit | `uv run pytest tests/core/test_dataclasses.py::test_patch_mutavel_estado -x` | ❌ W0 | ⬜ pending |
| 03-01-08 | 01 | 1 | CORE-03 | — | __slots__ proíbe atributo novo em Patch | unit | mesmo arquivo, mesmo teste | ❌ W0 | ⬜ pending |
| 03-01-09 | 01 | 1 | CORE-03 | — | EstadoPatch default PROPOSTO; valor "proposto" | unit | `uv run pytest tests/core/test_dataclasses.py::test_estado_patch_default_proposto -x` | ❌ W0 | ⬜ pending |
| 03-01-10 | 01 | 1 | CORE-03 | — | Patch invariantes raise (confianca>1, texto_original/motivo vazios) | unit (parametrize) | `uv run pytest tests/core/test_dataclasses.py::test_patch_invariantes_raise -x` | ❌ W0 | ⬜ pending |
| 03-01-11 | 01 | 1 | CORE-03 | — | json.dumps(patch.to_dict()) round-trip | contract | `uv run pytest tests/core/test_dataclasses.py::test_patch_to_dict_json_roundtrip -x` | ❌ W0 | ⬜ pending |
| 03-01-12 | 01 | 1 | CORE-02+03 | — | Coverage >= 95% em core/dataclasses.py + core/enums.py | coverage gate | `uv run pytest --cov=biblio_validador.core --cov-fail-under=95` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/core/__init__.py` — marcador de pacote pytest (vazio)
- [ ] `tests/core/test_dataclasses.py` — stubs para CORE-02 + CORE-03 (12 testes acima)
- [x] `pytest>=9.0.3` + `pytest-cov>=7.1.0` — instalados em Phase 1 D-08 (sem ação)
- [x] `[tool.pytest.ini_options] testpaths = ["tests"]` — configurado em Phase 1 D-14 (sem ação)
- [x] `[tool.coverage.run] source = ["biblio_validador"]` — configurado em Phase 1 D-14 (sem ação)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification — Phase 3 é modelagem pura, sem I/O nem UI.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`tests/core/__init__.py`, `tests/core/test_dataclasses.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 1s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
