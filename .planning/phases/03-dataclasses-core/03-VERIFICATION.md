---
phase: 03-dataclasses-core
verified: 2026-05-05T20:00:00Z
status: passed
score: 7/7
overrides_applied: 0
re_verification: false
---

# Phase 3: Dataclasses Core — Verification Report

**Phase Goal:** Dataclasses `Violacao` e `Patch` com todos os campos especificados + enum `EstadoPatch` tipado e imutável
**Verified:** 2026-05-05T20:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `Violacao(arquivo=..., linha_inicio=1, ...)` criada com `frozen=True` e `slots=True` | VERIFIED | `__dataclass_params__.frozen is True`; `hasattr(v, '__slots__')`; `not hasattr(v, '__dict__')` — confirmed inline |
| 2 | `Patch` mutável (`slots=True`, sem frozen) e aceita `EstadoPatch.PROPOSTO/ACEITO/REJEITADO/SUPRIMIDO` | VERIFIED | `__dataclass_params__.frozen is False`; `p.estado = EstadoPatch.ACEITO` succeeds; all 4 states confirmed |
| 3 | `dataclasses.asdict(violacao)` produz dict serializável em JSON sem erros | VERIFIED | `asdict()` returns structural dict; `json.dumps(v.to_dict())` round-trip confirmed with field-level assertion |
| 4 | Tentativa de mutar `Violacao.regra_id` lança `FrozenInstanceError` | VERIFIED | Inline check confirmed; `test_violacao_frozen_raises_on_mutate` passes |
| 5 | `Severidade.peso()` retorna 0..3 monotônica (`INFO<ALERTA<ERRO<CRITICO`) | VERIFIED | `[0,1,2,3]` returned — `test_severidade_peso_monotonica` passes |
| 6 | `from biblio_validador.core import Violacao, Patch, Severidade, EstadoPatch` funciona | VERIFIED | `test_aux_imports_via_re_export_funcionam` passes; `__all__` contains all 4 symbols |
| 7 | `json.dumps(violacao.to_dict())` produz string serializável e round-trip preserva campos | VERIFIED | `Path->str`, `Enum->value`, `tuple->list` all confirmed in `test_violacao_to_dict_json_roundtrip` |

**Score:** 7/7 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/biblio_validador/core/__init__.py` | Re-export público com `__all__` | VERIFIED | Exists, 7 lines, exports all 4 symbols |
| `src/biblio_validador/core/enums.py` | `class Severidade(Enum)` + `EstadoPatch` + `_PESOS_SEVERIDADE` | VERIFIED | Exists, 53 lines, all 3 declarations present |
| `src/biblio_validador/core/dataclasses.py` | `@dataclass(frozen=True, slots=True)` + `Violacao` + `Patch` + `_normalize_for_json` + `to_dict()` | VERIFIED | Exists, 164 lines, all required patterns present |
| `src/biblio_validador/py.typed` | PEP 561 marker | VERIFIED | File exists; enables mypy strict for consumers |
| `tests/core/__init__.py` | Package marker (empty) | VERIFIED | Exists (1 line, empty) |
| `tests/core/test_dataclasses.py` | 12+ tests with `test_violacao_instancia_com_frozen_e_slots` | VERIFIED | 25 tests, function found, 100% coverage |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/biblio_validador/core/dataclasses.py` | `src/biblio_validador/core/enums.py` | `from biblio_validador.core.enums import EstadoPatch, Severidade` | WIRED | Line 13 confirmed |
| `src/biblio_validador/core/__init__.py` | `src/biblio_validador/core/dataclasses.py` | `from biblio_validador.core.dataclasses import Patch, Violacao` | WIRED | Line 3 confirmed |
| `tests/core/test_dataclasses.py` | `src/biblio_validador/core/__init__.py` | `from biblio_validador.core import EstadoPatch, Patch, Severidade, Violacao` | WIRED | Lines 9 and 213 confirmed |

---

### Data-Flow Trace (Level 4)

Not applicable — Phase 3 is pure data modeling (no I/O, no rendering, no dynamic data sources). All types are in-process Python objects.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| 25 Phase-3 tests pass | `uv run pytest tests/core/ -v` | 25/25 PASS in 0.04s | PASS |
| Full suite passes (42 tests, no regression) | `uv run pytest --tb=short` | 42/42 PASS in 0.20s | PASS |
| Coverage >= 95% on `biblio_validador.core` | `pytest --cov=biblio_validador.core --cov-fail-under=95` | 100% (89/89 stmts, 34/34 branches) | PASS |
| mypy strict on source | `uv run mypy src/biblio_validador/core/` | 0 errors in 3 files | PASS |
| mypy strict on tests | `uv run mypy tests/core/test_dataclasses.py` | 0 errors | PASS |
| ruff lint | `uv run ruff check src/biblio_validador/core/ tests/core/` | All checks passed | PASS |
| ruff format | `uv run ruff format --check src/biblio_validador/core/ tests/core/` | 5 files already formatted | PASS |
| Line length <= 80 chars | `awk` scan on source + test files | 0 violations | PASS |
| SC1 inline: `frozen=True, slots=True` | Python inline check | Confirmed | PASS |
| SC2 inline: Patch mutable, all states | Python inline check | Confirmed | PASS |
| SC3 inline: `to_dict()` JSON serializable | Python inline check | round-trip confirmed | PASS |
| SC4 inline: `FrozenInstanceError` on mutate | Python inline check | Raised correctly | PASS |

---

### D-XX Decision Compliance (33 decisions from CONTEXT.md)

| Decision | Concern | Status | Evidence |
|----------|---------|--------|---------|
| D-01 | Subpackage `core/` (no shadowing stdlib `dataclasses`) | VERIFIED | `src/biblio_validador/core/` exists |
| D-02 | Files: `__init__.py`, `dataclasses.py`, `enums.py` | VERIFIED | All 3 present |
| D-03 | `__all__` re-exports 4 symbols exactly | VERIFIED | `{'Violacao','Patch','Severidade','EstadoPatch'}` |
| D-04 | No `core/types.py` or extra subdivisions | VERIFIED | Only 3 .py files in core/ |
| D-05 | `Violacao` is `@dataclass(frozen=True, slots=True)` | VERIFIED | `__dataclass_params__.frozen is True`; no `__dict__` |
| D-06 | `Patch` is `@dataclass(slots=True)` without `frozen` | VERIFIED | `__dataclass_params__.frozen is False` |
| D-07 | `Violacao.sugestoes: tuple[str, ...] = ()` | VERIFIED | `isinstance(v.sugestoes, tuple)` confirmed |
| D-08 | Patch collections (preventive): use tuple not list if added | VERIFIED | No list collections in Patch |
| D-09 | `Violacao` 11 fields in declared order; `principio_canonico_violado=None` default; `sugestoes=()` default | VERIFIED | Field list matches exactly |
| D-10 | `col_fim - col_inicio == len(trecho_violador)` invariant (intra-line) | VERIFIED | Holds in valid instances; raised in `test_aux_violacao_trecho_len_invariante` |
| D-11 | `arquivo: Path` in both | VERIFIED | `isinstance(v.arquivo, Path)` and `isinstance(p.arquivo, Path)` |
| D-12 | `linha_fim == linha_inicio` accepted (intra-line case) | VERIFIED | Default test instances use equal values |
| D-13 | No `mensagem` field; cross-line skips len invariant | VERIFIED | No `mensagem` field; multi-line Violacao with mismatched len does not raise |
| D-14 | `Severidade` is `enum.Enum` with string snake_case values | VERIFIED | `INFO='info'`, `ALERTA='alerta'`, `ERRO='erro'`, `CRITICO='critico'` |
| D-15 | 4 Severidade values: INFO/ALERTA/ERRO/CRITICO | VERIFIED | All 4 present |
| D-16 | `Severidade.peso()` via module-level dict `_PESOS_SEVERIDADE` | VERIFIED | Dict present in enums.py; `peso()` returns 0..3 |
| D-17 | `Patch` 10 fields; `confianca` no default; `estado=PROPOSTO` default | VERIFIED | `inspect.Parameter.empty` for confianca; defaults confirmed |
| D-18 | `Patch` is single-line (`linha`, not `linha_inicio/fim`) | VERIFIED | Field `linha` present; `linha_inicio` absent |
| D-19 | No `regra_id_origem` in `Patch` | VERIFIED | Field absent |
| D-20 | `EstadoPatch` 4 values: PROPOSTO/ACEITO/REJEITADO/SUPRIMIDO with snake_case | VERIFIED | All 4 values with correct string representations |
| D-21 | Transitions documented in docstring, not enforced in runtime | VERIFIED | Docstring present in `Patch` class; mutation accepted freely |
| D-22 | `Violacao.__post_init__` validates 6 invariants with `regra_id` in messages | VERIFIED | All 6 branches tested and passing |
| D-23 | `Patch.__post_init__` validates 6 invariants | VERIFIED | All 6 branches tested and passing |
| D-24 | `__post_init__` only validates, no `object.__setattr__` | VERIFIED | `object.__setattr__` absent from source |
| D-25 | `to_dict()` method in both `Violacao` and `Patch` | VERIFIED | Both have `to_dict() -> dict[str, Any]` |
| D-26 | `dataclasses.asdict()` preserves rich types; `to_dict()` needed for JSON | VERIFIED | `asdict()` returns Path/Enum/tuple; `to_dict()` normalizes |
| D-27 | No `from_dict()` (deferred to Phase 58) | VERIFIED | Method absent from both classes |
| D-28 | Tests cover 4 ROADMAP success criteria | VERIFIED | `test_violacao_instancia_com_frozen_e_slots`, `test_violacao_frozen_raises_on_mutate`, `test_violacao_to_dict_json_roundtrip`, `test_patch_mutavel_estado` all present and passing |
| D-29 | 5 invariant tests with `ValueError` checks | VERIFIED | `test_violacao_invariantes_raise` (4 parametrized) + `test_patch_invariantes_raise` (5 parametrized) |
| D-30 | Coverage >= 95% on `core/` | VERIFIED | 100% (0 missing lines, 0 missing branches) |
| D-31 | Type hints 100%; mypy strict passes | VERIFIED | 0 mypy errors on source and tests |
| D-32 | `ruff line-length=80`; no lines > 80 chars | VERIFIED | 0 violations in source or tests |
| D-33 | Zero `loguru` imports in `core/` | VERIFIED | `grep -r loguru src/biblio_validador/core/` returns no output |

All 33 D-XX decisions: VERIFIED.

---

### Requirements Coverage

| Requirement | Phase | Description | Status | Evidence |
|-------------|-------|-------------|--------|---------|
| CORE-02 | Phase 3 | `Violacao(arquivo, linha_inicio, linha_fim, col_inicio, col_fim, trecho_violador, regra_id, regra_nome, severidade, sugestoes, principio_canonico_violado)` | SATISFIED | All 11 fields present in declared order; frozen+slots; `__post_init__` invariants; `to_dict()` serialization |
| CORE-03 | Phase 3 | `Patch(arquivo, linha, col_inicio, col_fim, texto_original, texto_substituto, motivo, confianca, requer_revisao_humana, estado)` with `EstadoPatch` enum | SATISFIED | All 10 fields present; `estado` mutable; all 4 `EstadoPatch` values; `__post_init__` invariants; `to_dict()` |

---

### Anti-Patterns Found

None. No TODO/FIXME/HACK/PLACEHOLDER comments detected. No empty implementations, no stubs, no hardcoded returns, no console.log-only handlers.

---

### Human Verification Required

None. Phase 3 is pure data modeling — all behavior is deterministic and fully verifiable programmatically. All 4 ROADMAP success criteria confirmed by inline Python checks and passing test suite.

---

## Gaps Summary

No gaps. All must-haves verified, all artifacts substantive and wired, all key links confirmed, all 33 context decisions honored, requirements CORE-02 and CORE-03 satisfied, 100% coverage, 0 mypy errors, 0 ruff violations.

**Commit log confirms implementation:**
- `ed96264` — `feat(03-01): Severidade + EstadoPatch enums`
- `1e4d928` — `feat(03-01): Violacao + Patch + _normalize_for_json`
- `7d91251` — `feat(03-01): core/__init__.py re-export`
- `0991019` — `test(03-01): 21 testes + py.typed marker`
- `4c85f89` — `test(03-01): coverage gap fill`

---

_Verified: 2026-05-05T20:00:00Z_
_Verifier: Claude (gsd-verifier)_
