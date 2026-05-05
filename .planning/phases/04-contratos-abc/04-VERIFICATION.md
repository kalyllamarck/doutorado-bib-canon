---
phase: 04-contratos-abc
verified: 2026-05-05T20:00:00Z
status: passed
score: 4/4 success criteria verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
---

# Phase 4: Contratos ABC — Verification Report

**Phase Goal:** ABCs `ValidadorBase` e `FixerBase` com contratos completos
que forçam implementação dos métodos obrigatórios.

**Verified:** 2026-05-05T20:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (4 ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Instanciar classe concreta que omite `validar()` lança `TypeError` em tempo de instanciação | VERIFIED | 4 tests pass: `test_validador_base_abstract_validar`, `test_validador_base_abstract_carregar_regras`, `test_fixer_base_abstract_propor_patches`, `test_fixer_base_abstract_aplicar`. Each instantiates a subclass omitting one abstract method and asserts `pytest.raises(TypeError, match="abstract")`. |
| 2 | `ValidadorBase.carregar_regras()` carrega o JSON referenciado em `JSON_SOURCE` e compila regex 1x | VERIFIED | 2 tests pass: `test_carregar_regras_cache_hit` confirms `id(r1) == id(r2)` after second invocation; `test_carregar_regras_per_subclass_isolation` confirms cache is per-subclass via `cls.__dict__.get` (Pitfall 2 mitigation). Helper `_carregar_json_simples` in contracts.py:52-98 handles file read + regex compilation. |
| 3 | `FixerBase.pode_corrigir(v)` retorna `False` para `regra_id` não listado em `VIOLACAO_IDS` | VERIFIED | 2 tests pass: `test_pode_corrigir_returns_true_for_known_id` (regra_id="cst_999" → True) and `test_pode_corrigir_returns_false_for_unknown_id` (regra_id="cst_001" → False). Concrete default in contracts.py:235-241 returns `v.regra_id in type(self).VIOLACAO_IDS`. |
| 4 | Testes unitários dos ABCs passam (incluindo teste de violação de contrato) | VERIFIED | 40 tests pass (15 contracts + 25 dataclasses, 0 failures). Coverage 99.49% on `biblio_validador.core` (gate ≥95%). Suite runtime 0.20s. |

**Score:** 4/4 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/biblio_validador/core/contracts.py` | ABCs ValidadorBase + FixerBase + dataclasses AplicacaoResultado + ContextoFixer + helpers | VERIFIED | 277 lines, 4 classes, 2 module helpers, 58 stmts, 98% coverage |
| `src/biblio_validador/core/enums.py` | Adds Scope + ModoFixer (extends Phase 3) | VERIFIED | 86 lines (was 52 in Phase 3), 4 enums total, 100% coverage |
| `src/biblio_validador/core/__init__.py` | Re-exports 10 symbols alphabetically | VERIFIED | `__all__` contains exactly 10 symbols (AplicacaoResultado, ContextoFixer, EstadoPatch, FixerBase, ModoFixer, Patch, Scope, Severidade, ValidadorBase, Violacao); 100% coverage |
| `tests/core/test_contracts.py` | 15 tests covering 4 success criteria + error paths + dataclass aux + smoke | VERIFIED | 369 lines, 15 tests collected, all pass |
| `tests/core/fixtures/regras_fake.json` | Single-entry happy path fixture | VERIFIED | 1 entry `cst_999` with `regex_deteccao: "\\bfake\\b"` |
| `tests/core/fixtures/regras_malformadas.json` | Invalid JSON to force JSONDecodeError | VERIFIED | Truncated `{ "entradas": [` triggers `json.JSONDecodeError` |
| `tests/core/fixtures/regras_regex_invalido.json` | Bad regex to force re.error | VERIFIED | Entry `cst_invalido` with `(?P<unfinished` regex |
| `tests/core/fixtures/regras_str_e_lista.json` | 4 entries: str, list, alt-key, skip | VERIFIED | All 4 entries present; covers Pattern 5 schema heterogeneity + skip branch |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `core/__init__.py` | `core/contracts.py` | `from biblio_validador.core.contracts import (AplicacaoResultado, ContextoFixer, FixerBase, ValidadorBase)` | WIRED | Line 8-13; smoke test confirms 10 symbols importable |
| `core/__init__.py` | `core/enums.py` | `from biblio_validador.core.enums import (EstadoPatch, ModoFixer, Scope, Severidade)` | WIRED | Line 15-20 |
| `core/contracts.py` | `core/dataclasses.py` | `from biblio_validador.core.dataclasses import Patch, Violacao` | WIRED | Line 26; Patch + Violacao consumed in method signatures |
| `core/contracts.py` | `core/enums.py` | `from biblio_validador.core.enums import ModoFixer, Scope` | WIRED | Line 27; ClassVar attribute types |
| `core/contracts.py` | `parser/types.py` | `from biblio_validador.parser.types import Paragrafo` | WIRED | Line 28; `validar(paragrafos: list[Paragrafo])` signature |
| `tests/core/test_contracts.py` | `core/contracts.py::_carregar_json_simples` | `from biblio_validador.core.contracts import _carregar_json_simples` | WIRED | Line 39; consumed in 6 tests |
| `tests/core/test_contracts.py` | `core` re-export surface | `from biblio_validador.core import (AplicacaoResultado, ContextoFixer, ..., Violacao)` | WIRED | Line 27-38; 10-symbol import — exercises full public surface |

---

### Pitfall Verifications (RESEARCH-mandated)

| # | Pitfall | Status | Evidence |
|---|---------|--------|----------|
| 1 | Decorator order: `@classmethod` ABOVE `@abstractmethod` for classmethod abstracts | VERIFIED | contracts.py:141-143 has `@classmethod` then `@abstractmethod` then `def carregar_regras(cls)`. Inverting would fail at class-definition time. |
| 2 | Cache isolation via `cls.__dict__.get` (not `getattr`/MRO) | VERIFIED | Documented in `ValidadorBase` docstring (contracts.py:113-125) AND used in test fake `_ValidadorComCache` (test_contracts.py:167). `test_carregar_regras_per_subclass_isolation` proves Sub A and Sub B do NOT share cache. |
| 4 | `ContextoFixer` has `eq=False` on dataclass decorator | VERIFIED | contracts.py:188 — `@dataclass(frozen=True, slots=True, eq=False)`. `grep "eq=False"` finds 6 matches (1 source + 5 in docs/comments). `test_contexto_fixer_eq_false_unhashable_safe` confirms instantiation with Mapping field works. |
| 5 | `_carregar_json_simples` handles str/list/alt-key/skip schema heterogeneity | VERIFIED | `regras_str_e_lista.json` has 4 entries (cst_str, cst_lista, cst_alt_key, cst_skip). Test `test_carregar_regras_normalizes_str_and_list` asserts result keys equal `{"cst_str", "cst_lista", "cst_alt_key"}` — skip branch covered. Helper code at contracts.py:74-98 normalizes str/list and accepts alternative key `regex_deteccao_aproximada`. |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All ABC + dataclass + enum symbols importable from public surface | `uv run python -c "from biblio_validador.core import AplicacaoResultado, ContextoFixer, EstadoPatch, FixerBase, ModoFixer, Patch, Scope, Severidade, ValidadorBase, Violacao; print('all 10 OK')"` | `all 10 OK` | PASS |
| Full test suite passes | `uv run pytest tests/core/ -v` | `40 passed in 0.20s` | PASS |
| Coverage gate ≥95% | `uv run pytest tests/core/ --cov=biblio_validador.core --cov-fail-under=95` | `Required test coverage of 95% reached. Total coverage: 99.49%` | PASS |
| mypy --strict passes | `uv run mypy --strict src/biblio_validador/core/` | `Success: no issues found in 4 source files` | PASS |
| ruff check passes | `uv run ruff check src/biblio_validador/core/ tests/core/` | `All checks passed!` | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CORE-04 | 04-02-PLAN.md | ABC `ValidadorBase` com `JSON_SOURCE`, `SCOPE`, `carregar_regras()`, `validar(paragrafos) -> list[Violacao]` | SATISFIED | `class ValidadorBase(ABC)` at contracts.py:101 with both ClassVars (JSON_SOURCE: Path, SCOPE: Scope), 1 nullable cache ClassVar, and 2 @abstractmethod (carregar_regras as classmethod abstract, validar as instance abstract). 7 tests directly verify the contract. |
| CORE-05 | 04-02-PLAN.md, 04-03-PLAN.md | ABC `FixerBase` com `VIOLACAO_IDS`, `MODO`, `pode_corrigir(v)`, `propor_patches(v, contexto) -> list[Patch]`, `aplicar(patches, modo_interativo)` | SATISFIED | `class FixerBase(ABC)` at contracts.py:212 with both ClassVars (VIOLACAO_IDS: frozenset[str], MODO: ModoFixer), concrete `pode_corrigir` (D-23), and 2 @abstractmethod (propor_patches, aplicar). 6 tests directly verify the contract. |

REQUIREMENTS.md traceability table already marks CORE-04 and CORE-05 as Complete (lines 142-143).

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | grep for `TODO|FIXME|XXX|HACK|PLACEHOLDER` returned zero matches in production source (contracts.py, enums.py) and tests (test_contracts.py). |

No anti-patterns found. The 277-line contracts.py is fully implemented (no placeholders), the only "uncovered" line per coverage report is line 49 of `_canonical_root` (helper exercised indirectly via JSON_SOURCE declaration in concrete validators starting Phase 6).

---

### Human Verification Required

None. All 4 success criteria are programmatically verifiable via the test suite and gate commands. The single VALIDATION.md "manual-only" item (regex error message contains `regra_id`) is implicitly covered by `test_carregar_regras_regex_error` which uses `pytest.raises(re.error, match="cst_invalido")` — that match assertion confirms the error message includes the regra_id.

---

### Gaps Summary

No gaps. Phase 4 delivered exactly what ROADMAP.md and REQUIREMENTS.md specified:

- 2 ABCs with full contract enforcement (TypeError on incomplete instantiation)
- 2 frozen+slots auxiliary dataclasses (AplicacaoResultado, ContextoFixer with critical eq=False)
- 2 new enums (Scope, ModoFixer) extending Phase 3 enums.py
- Public re-export surface expanded from 4 to 10 symbols alphabetically
- 15 new tests covering 4 success criteria + 7 error/auxiliary paths
- 4 fixture JSON files covering happy path + 3 error paths + schema heterogeneity
- Coverage 99.49% (gate 95%), mypy strict clean, ruff clean

The 3 RESEARCH-identified pitfalls (decorator order, cache isolation via cls.__dict__, eq=False for Mapping fields) are all correctly mitigated and documented inline. Phase 5 (PatchAplicador) can proceed — it will consume `Patch` (Phase 3) and implement the semantics that `FixerBase.aplicar()` declares as abstract.

---

### Recommendation for Next Phase

Phase 5 (PatchAplicador) is unblocked. Phase 4 delivered a stable contract surface that downstream phases depend on:

- Phase 5 implements byte-exact patch application (`FixerBase.aplicar` calls into it)
- Phase 6 first concrete `ValidadorBase` (cst_012 piloto)
- Phase 7 first concrete `FixerBase` (cst_012 fixer AUTO)
- Phase 8 orchestrator routes by `SCOPE` and `MODO`

No remediation required. Proceed to Phase 5.

---

## VERIFICATION PASSED — all goals achieved

**Verifier:** Claude (gsd-verifier)
**Verified:** 2026-05-05T20:00:00Z
