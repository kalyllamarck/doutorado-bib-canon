---
phase: 03-dataclasses-core
plan: "01"
subsystem: core
tags: [dataclasses, enums, modeling, python313, stdlib]
dependency_graph:
  requires:
    - "02-01 (parser/types.py template pattern)"
  provides:
    - "Violacao (frozen+slots) — CORE-02"
    - "Patch (slots, mutable) — CORE-03"
    - "Severidade (enum.Enum + peso()) — CORE-02"
    - "EstadoPatch (enum.Enum) — CORE-03"
    - "_normalize_for_json (helper privado JSON-ready)"
  affects:
    - "Phase 4 (ABCs ValidadorBase/FixerBase — consomem Violacao/Patch em assinaturas)"
    - "Phase 5 (PatchAplicador — ordena list[Patch] reverso por linha/col)"
    - "Phase 6 (ValidadorCst012 — primeiro produtor de Violacao)"
    - "Phase 8 (Orchestrator — lê severidade para exit code e AUDITORIA.md)"
tech_stack:
  added: []
  patterns:
    - "@dataclass(frozen=True, slots=True) para Violacao (imutável, hashável)"
    - "@dataclass(slots=True) para Patch (mutável em estado/requer_revisao_humana)"
    - "enum.Enum com value snake_case (herda TipoSecao Phase 2 D-03)"
    - "_normalize_for_json recursivo: Path->str, Enum->value, tuple->list"
    - "cast(dict[str, Any], ...) para resolver mypy strict no-any-return em to_dict()"
    - "py.typed (PEP 561) para habilitar mypy strict em test files"
key_files:
  created:
    - src/biblio_validador/core/__init__.py
    - src/biblio_validador/core/enums.py
    - src/biblio_validador/core/dataclasses.py
    - src/biblio_validador/py.typed
    - tests/core/__init__.py
    - tests/core/test_dataclasses.py
  modified: []
decisions:
  - "D-05: Violacao frozen+slots (imutável, hashável) — conforme CONTEXT.md"
  - "D-06: Patch slots-only (mutável em estado) — conforme CONTEXT.md"
  - "D-07: tuple[str, ...] em sugestoes (não list) — fecha buraco de imutabilidade"
  - "D-16: Severidade.peso() via dict module-level O(1) — não IntEnum"
  - "cast() em to_dict() — resolve mypy strict sem suprimir type check (Rule 1)"
  - "py.typed marker adicionado — habilita mypy strict para test files (Rule 2)"
metrics:
  duration: "~3h10min (14:30 BRT -> 17:42 BRT)"
  completed_date: "2026-05-05"
  tasks_completed: 5
  tasks_total: 5
  files_created: 6
  files_modified: 0
---

# Phase 03 Plan 01: Dataclasses Core Summary

**One-liner:** Modelagem nuclear `Violacao` (frozen+slots) e `Patch` (slots-mutável)
com enums `Severidade`/`EstadoPatch`, invariantes runtime via `__post_init__`,
serialização JSON-ready via `_normalize_for_json`, 100% coverage, mypy strict.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Criar enums.py (Severidade + EstadoPatch) | ed96264 | src/biblio_validador/core/enums.py |
| 2 | Criar dataclasses.py (Violacao + Patch + _normalize_for_json) | 1e4d928 | src/biblio_validador/core/dataclasses.py |
| 3 | Criar core/__init__.py (re-export público) | 7d91251 | src/biblio_validador/core/__init__.py |
| 4 | Criar tests/core/ + test_dataclasses.py (21 testes) | 0991019 | tests/core/__init__.py, tests/core/test_dataclasses.py, src/biblio_validador/py.typed |
| 5 | Phase gate: coverage >= 95% + mypy + ruff | 4c85f89 | tests/core/test_dataclasses.py (+4 test_aux_) |

## Verification Results

| Gate | Command | Result |
|------|---------|--------|
| Suite isolada Phase 3 | `uv run pytest tests/core/ -x --tb=short` | 25/25 PASS |
| Suite completa (Phases 1+2+3) | `uv run pytest --tb=short` | 42/42 PASS |
| Coverage gate (>= 95%) | `uv run pytest --cov=biblio_validador.core --cov-fail-under=95` | 100% PASS |
| mypy strict (source) | `uv run mypy src/biblio_validador/core/` | 0 errors PASS |
| mypy strict (tests) | `uv run mypy tests/core/test_dataclasses.py` | 0 errors PASS |
| ruff lint | `uv run ruff check src/biblio_validador/core/ tests/core/` | 0 issues PASS |
| ruff format | `uv run ruff format --check src/biblio_validador/core/ tests/core/` | 0 diffs PASS |
| line-length <= 80 | `awk '{ if (length > 80) ... }' src/core/*.py tests/core/*.py` | vazio PASS |
| re-export sanity | `from biblio_validador.core import ...` | OK PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] cast() para resolver mypy strict no-any-return em to_dict()**
- **Found during:** Task 2 (mypy check pós-implementação)
- **Issue:** `_normalize_for_json` retorna `Any`; `to_dict() -> dict[str, Any]` disparava `no-any-return` no mypy strict. O plan original usava `type: ignore[arg-type]` (código errado de suppress).
- **Fix:** `cast(dict[str, Any], _normalize_for_json(asdict(self)))` em ambas dataclasses — mantém type-safe sem suprimir checks.
- **Files modified:** `src/biblio_validador/core/dataclasses.py`
- **Commit:** 1e4d928

**2. [Rule 2 - Missing Critical] py.typed marker PEP 561**
- **Found during:** Task 4 (mypy check em tests)
- **Issue:** `uv run mypy tests/core/test_dataclasses.py` retornava `import-untyped` porque o pacote `biblio_validador` não tinha o marcador PEP 561 `py.typed`. Isso também afetava `tests/parser/test_markdown.py` (pré-existente desde Phase 2). O plan acceptance criteria exige `mypy tests/core/test_dataclasses.py` exit 0.
- **Fix:** `touch src/biblio_validador/py.typed` — habilita mypy strict para qualquer consumidor do pacote.
- **Files modified:** `src/biblio_validador/py.typed` (novo)
- **Commit:** 0991019

**3. [Rule 1 - Bug] 4 test_aux_ para coverage gap (90% → 100%)**
- **Found during:** Task 5 (coverage gate falhou com 90%)
- **Issue:** Branches não cobertos: `_normalize_for_json` list branch (linha 30); `regra_id.strip()` vazio (linha 93); invariante `trecho_violador` len (linha 98); `linha<1`, `col_inicio<1`, `col_fim<col_inicio` em Patch (linhas 145, 147, 149).
- **Fix:** 4 testes `test_aux_*` adicionados seguindo convenção autorizada por STATE.md ("convenção test_aux_<descrição> autorizada para coverage gap fill").
- **Files modified:** `tests/core/test_dataclasses.py`
- **Commit:** 4c85f89

## Known Stubs

Nenhum. Todos os campos e métodos estão implementados. `principio_canonico_violado`
tem default `None` por design (AGR-02 / Phase 19 preenche — documentado em D-09,
não é stub).

## Threat Flags

Nenhum. Phase 3 é modelagem in-process pura — zero superfície de ataque nova.
`to_dict()` normaliza tipos para JSON mas não serializa (o chamador usa `json.dumps`).
T-3-02 do threat register: mitigação confirmada em implementação (`_normalize_for_json`
não injeta marcadores, apenas converte tipos).

## Self-Check: PASSED

Arquivos criados verificados:
- FOUND: src/biblio_validador/core/__init__.py
- FOUND: src/biblio_validador/core/enums.py
- FOUND: src/biblio_validador/core/dataclasses.py
- FOUND: src/biblio_validador/py.typed
- FOUND: tests/core/__init__.py
- FOUND: tests/core/test_dataclasses.py

Commits verificados (git log):
- FOUND: ed96264 feat(03-01): Severidade + EstadoPatch enums
- FOUND: 1e4d928 feat(03-01): Violacao + Patch + _normalize_for_json
- FOUND: 7d91251 feat(03-01): core/__init__.py re-export
- FOUND: 0991019 test(03-01): 21 testes + py.typed marker
- FOUND: 4c85f89 test(03-01): coverage gap fill
