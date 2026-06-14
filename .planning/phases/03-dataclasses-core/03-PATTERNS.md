# Phase 3: Dataclasses Core - Pattern Map

**Mapped:** 2026-05-05
**Files analyzed:** 5 new + 0 modified
**Analogs found:** 5 / 5 (100%)

## File Classification

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `src/biblio_validador/core/__init__.py` | package re-export | static-import | `src/biblio_validador/parser/__init__.py` | exact |
| `src/biblio_validador/core/enums.py` | model (enum constants) | static-data | `src/biblio_validador/parser/types.py` (enum half) | exact |
| `src/biblio_validador/core/dataclasses.py` | model (frozen + mutable dataclass) | transform / serialization | `src/biblio_validador/parser/types.py` (dataclass half) | exact |
| `tests/core/__init__.py` | pytest package marker | n/a | `tests/parser/__init__.py` | exact |
| `tests/core/test_dataclasses.py` | unit test suite | request-response (pytest) | `tests/parser/test_markdown.py` | role-match (logic differs: no fixture file, pure constructor + invariant tests) |

**No file in Phase 3 modifies existing code.** `pyproject.toml` is referenced read-only (already has `[tool.pytest.ini_options]`, `[tool.coverage.run]`, `pytest>=9.0.3`, `pytest-cov>=7.1.0` — no edits needed).

## Pattern Assignments

### `src/biblio_validador/core/__init__.py` (re-export)

**Analog:** `src/biblio_validador/parser/__init__.py` (exact match — same role, same structure)

**Full file pattern to copy** (`src/biblio_validador/parser/__init__.py` lines 1-7):
```python
"""Sub-pacote parser — segmentação de .md/.tex em list[Paragrafo]."""

from biblio_validador.parser.markdown import ParserMd
from biblio_validador.parser.types import Paragrafo, TipoSecao

__all__ = ["ParserMd", "Paragrafo", "TipoSecao"]
```

**Adaptation for Phase 3** (apply identical shape, swap symbols per CONTEXT D-03):
```python
"""Core domain types — Violacao, Patch, Severidade, EstadoPatch."""

from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import EstadoPatch, Severidade

__all__ = ["EstadoPatch", "Patch", "Severidade", "Violacao"]
```

**Conventions to copy:**
- One-line PT-BR module docstring at top
- Absolute imports (`from biblio_validador.<sub> import ...`) — never relative
- `__all__` lists symbols alphabetically (parser uses topical order; D-03 example uses alphabetical — RESEARCH Pattern 6 confirms alphabetical OK)
- No `__version__`, no side-effect code, no logging configuration

---

### `src/biblio_validador/core/enums.py` (enum constants)

**Analog:** `src/biblio_validador/parser/types.py` lines 1-24 (enum half — exact pattern for `enum.Enum` with string snake_case values)

**Imports pattern** (`src/biblio_validador/parser/types.py` lines 1-5):
```python
"""Tipos parser-internal: Paragrafo + TipoSecao."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
```
For `core/enums.py`, only `from enum import Enum` is needed (no Path, no dataclass).

**Enum class template** (`src/biblio_validador/parser/types.py` lines 8-24):
```python
class TipoSecao(Enum):
    """Vocabulário fechado de tipos de seção/parágrafo (D-03)."""

    TITULO = "titulo"
    AUTORES = "autores"
    RESUMO = "resumo"
    PALAVRAS_CHAVE = "palavras_chave"
    ABSTRACT = "abstract"
    KEYWORDS = "keywords"
    SUMARIO = "sumario"
    INTRODUCAO = "introducao"
    SECAO = "secao"
    CONCLUSAO = "conclusao"
    REFERENCIAS = "referencias"
    NOTA_RODAPE = "nota_rodape"
    CORPO = "corpo"
    DESCONHECIDO = "desconhecido"
```

**Conventions to copy:**
- `class Name(Enum)` (NOT `StrEnum`, NOT `IntEnum` — see RESEARCH "Anti-Patterns" + D-14/D-16/D-20)
- Member names: ALL_CAPS_SNAKE
- Member values: lowercase snake_case strings
- One-line PT-BR docstring referencing decision ID (D-03 in analog → D-15 / D-20 in Phase 3)
- No method on `TipoSecao`; Phase 3 `Severidade` adds `.peso() -> int` (RESEARCH Pattern 3) backed by module-level `_PESOS_SEVERIDADE: dict[Severidade, int]`. No analog for `peso()` in codebase — implement per RESEARCH Pattern 3 lines 401-428.

**Concrete code from RESEARCH Pattern 3** (already empirically verified in Python 3.13.13):
```python
class Severidade(Enum):
    INFO = "info"
    ALERTA = "alerta"
    ERRO = "erro"
    CRITICO = "critico"

    def peso(self) -> int:
        return _PESOS_SEVERIDADE[self]


_PESOS_SEVERIDADE: dict[Severidade, int] = {
    Severidade.INFO: 0,
    Severidade.ALERTA: 1,
    Severidade.ERRO: 2,
    Severidade.CRITICO: 3,
}
```

---

### `src/biblio_validador/core/dataclasses.py` (frozen + mutable dataclasses + JSON helper)

**Analog:** `src/biblio_validador/parser/types.py` lines 27-45 (dataclass half — exact pattern for `@dataclass(frozen=True, slots=True)`)

**Imports pattern** (`src/biblio_validador/parser/types.py` lines 1-5) — extend with `enum.Enum` import for type-narrowing in `_normalize_for_json`, and import own enums:
```python
"""Tipos parser-internal: Paragrafo + TipoSecao."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
```
Phase 3 adaptation: add `from typing import Any` and `from biblio_validador.core.enums import EstadoPatch, Severidade`. `dataclasses.asdict` imported lazily inside `to_dict()` per RESEARCH Pattern 1 lines 313-318 (avoids polluting module namespace where module itself is named `dataclasses.py`).

**Frozen dataclass template** (`src/biblio_validador/parser/types.py` lines 27-45):
```python
@dataclass(frozen=True, slots=True)
class Paragrafo:
    """Bloco de texto identificável linha a linha (D-02).

    Offsets relativos ao source UTF-8 NFC.
    """

    arquivo: Path
    indice: int  # 0-based, ordem topológica
    tipo: TipoSecao
    nivel_heading: int | None  # 1-6 se heading; None se corpo
    texto: str  # slice raw NFC, com markup preservado
    linha_inicio: int  # 1-based
    linha_fim: int  # 1-based, inclusivo
    offset_bytes: int  # absoluto em UTF-8 NFC
    len_bytes: int  # bytes UTF-8 NFC
    ref_nota: str | None  # label da footnote ("a", "1", ...)
    paragrafo_pai_idx: int | None  # idx do parágrafo que cita [^ref_nota]
```

**Conventions to copy verbatim for `Violacao` (D-05, D-09):**
- `@dataclass(frozen=True, slots=True)` — same decorator
- PT-BR class docstring referencing decision ID (`(D-02)` in analog → `(CORE-02 / D-09)` in `Violacao`)
- One inline `# comment` per field documenting semantics (1-based, half-open, etc.) — keeps line ≤ 80 chars
- `int | None` for nullable fields (NOT `Optional[int]`)
- Type-hint EVERY field; no defaults except where D-09 explicitly allows (`sugestoes`, `principio_canonico_violado`)
- Use `Path` (NOT `str`) for file paths — same as `Paragrafo.arquivo`

**Phase 3 additions NOT present in analog** (must be implemented per RESEARCH):

1. **`__post_init__` validators** — analog has none; `Violacao` and `Patch` add invariant validation per D-22/D-23. Pattern from RESEARCH lines 280-311 (Violacao) and 362-377 (Patch). Always include `regra_id` (or relevant id) in error message for diagnose:
   ```python
   if self.linha_inicio < 1:
       raise ValueError(
           f"linha_inicio < 1 em {self.regra_id}: "
           f"{self.linha_inicio}"
       )
   ```

2. **Mutable dataclass `Patch`** — analog only has frozen variant. Use `@dataclass(slots=True)` without `frozen` per D-06. Pattern from RESEARCH lines 333-377.

3. **`tuple[str, ...] = ()`** for `Violacao.sugestoes` (D-07) — analog has no collection field; per RESEARCH "Anti-Patterns" + Pitfall 1, NEVER use `list[str]` in frozen dataclass (defeats immutability). Use `default=()` not `field(default_factory=tuple)` (RESEARCH "Alternatives" + "Anti-Patterns" lines 557-560).

4. **`to_dict() -> dict[str, Any]`** + module-level `_normalize_for_json` helper — no analog. Implement per RESEARCH Pattern 5 lines 500-516 (recursive normalizer for `Path` → `str`, `Enum` → `.value`, `tuple` → `list`).

**Critical naming pitfall** (RESEARCH "Anti-Patterns" line 583-588):
> Module is named `core/dataclasses.py` and imports from stdlib `dataclasses`. ALWAYS use `from dataclasses import dataclass, field, asdict` (never `import dataclasses` bare — would cause recursive self-import).

---

### `tests/core/__init__.py` (pytest package marker)

**Analog:** `tests/parser/__init__.py` (exact match — empty file)

**Full pattern:** zero bytes. The file exists solely to make `tests/core/` a Python package so pytest collects it. Verified by `wc -l tests/parser/__init__.py` returning `0`.

```
# (empty file — no content, no docstring, no imports)
```

---

### `tests/core/test_dataclasses.py` (unit tests)

**Analog:** `tests/parser/test_markdown.py` (role-match — same framework + idiomatic patterns; logic differs: Phase 3 tests pure constructors and invariants, no I/O fixtures)

**Imports pattern** (`tests/parser/test_markdown.py` lines 1-10):
```python
"""Smoke tests Phase 2 — parser CommonMark + footnotes (D-26)."""

import unicodedata
from pathlib import Path

import pytest

from biblio_validador.parser import Paragrafo, ParserMd, TipoSecao

EOLICA_FIXTURE = Path(__file__).parent / "fixtures" / "eolica_first_30.md"
```

**Adaptation for Phase 3** (drop unicodedata + fixture path; add FrozenInstanceError + json):
```python
"""Smoke tests Phase 3 — Violacao + Patch + invariantes (D-28/D-29)."""

import json
from dataclasses import FrozenInstanceError, asdict
from pathlib import Path

import pytest

from biblio_validador.core import EstadoPatch, Patch, Severidade, Violacao
```

**Conventions to copy:**
- One-line PT-BR module docstring referencing decision IDs (`(D-26)` → `(D-28/D-29)`)
- Stdlib imports first (alphabetical), blank line, third-party (`pytest`), blank line, project import
- Use `from biblio_validador.core import ...` (the public re-export, NOT `from biblio_validador.core.dataclasses import ...`) — mirrors how `test_markdown.py` imports from `biblio_validador.parser`, not from the deeper `parser.types` / `parser.markdown`. This validates the re-export contract from `__init__.py`.

**Test function pattern** (`tests/parser/test_markdown.py` lines 18-34):
```python
def test_paragrafo_simples_um_so_paragrafo(
    tmp_path: Path, parser: ParserMd
) -> None:
    """D-26.1: arquivo com 1 parágrafo simples."""
    f = tmp_path / "simples.md"
    f.write_text("Texto simples.\n", encoding="utf-8")
    paragrafos = parser.parsear(f)
    assert len(paragrafos) == 1
    p = paragrafos[0]
    assert p.linha_inicio == 1
    ...
```

**Conventions to copy:**
- Docstring is `"""D-XX.N: short description."""` — references CONTEXT decision ID with sub-numeric (D-26.1, D-26.2, ...). For Phase 3: D-28.1..D-28.4 (success criteria) and D-29.1..D-29.5 (invariantes).
- Function signature `def test_X(...) -> None:` — explicit `-> None` return (mypy strict)
- One assertion focus per test; multiple `assert` lines OK if they verify ONE behavior
- No fixtures needed for Phase 3 (no I/O, no parser instance) — but follow the typing convention for any helper

**Parametrize pattern** — analog does NOT use `@pytest.mark.parametrize`. RESEARCH Pattern lines 807-831 + Discretion D-29 explicitly leave parametrize-vs-separate as executor's call. Reference RESEARCH lines 807-831 if planner chooses parametrize:
```python
@pytest.mark.parametrize(
    "kwargs, msg_substr",
    [
        (
            dict(arquivo=Path("a.md"), linha_inicio=0, linha_fim=1,
                 col_inicio=1, col_fim=2, trecho_violador="ab",
                 regra_id="lex_001", regra_nome="X",
                 severidade=Severidade.ERRO),
            "linha_inicio",
        ),
        ...
    ],
)
def test_violacao_invariantes_raise(
    kwargs: dict[str, object], msg_substr: str
) -> None:
    with pytest.raises(ValueError, match=msg_substr):
        Violacao(**kwargs)  # type: ignore[arg-type]
```

**Auxiliary tests pattern for coverage ≥ 95%** — analog adds `test_aux_*` tests (lines 154-260) to push coverage from canonical-only to ≥ 90%. Phase 3 target is ≥ 95% (D-30); the canonical 4 + 5 + ~5 contract tests should hit it for tiny modules. Pattern: prefix `test_aux_` + docstring `"""<Pitfall ref>: ..."""` per RESEARCH "Contract Tests" lines 893-910 (frozenness, slots, tuple-not-list, JSON round-trip, hashability).

**`pytest.raises` pattern** (`tests/parser/test_markdown.py` lines 159-165):
```python
def test_aux_arquivo_inexistente_propaga(
    tmp_path: Path, parser: ParserMd
) -> None:
    """Pitfall 4: FileNotFoundError propaga após logger.error."""
    inexistente = tmp_path / "no_such_file.md"
    with pytest.raises(FileNotFoundError):
        parser.parsear(inexistente)
```

For Phase 3 (D-29 invariantes):
```python
with pytest.raises(ValueError, match="linha_inicio"):
    Violacao(arquivo=Path("a.md"), linha_inicio=0, ...)
```
Use `match=` to assert the error message contains `regra_id` per D-22 (the diagnostic substring).

---

## Shared Patterns

### PT-BR Docstring + Decision-ID Reference
**Source:** All Phase 1+2 source files (`parser/types.py:9`, `parser/markdown.py`, `parser/__init__.py:1`)
**Apply to:** All Phase 3 modules (every class, every public function)

**Convention:**
- Module docstring: one-line PT-BR sentence summarizing module purpose
- Class docstring: PT-BR with `(D-XX)` or `(CORE-NN / D-XX)` reference at end of summary line. Multi-line docstrings explain invariants (column half-open, transitions, etc.)
- Test docstring: `"""D-XX.N: short description."""`
- Code comments inline next to fields: short PT-BR, ≤ 80 chars (e.g., `# 1-based, inclusivo`)

### Type Hints 100% (CLAUDE.md Rule 9 + mypy strict)
**Source:** All Phase 1+2 source files; `pyproject.toml:49-51` (`[tool.mypy] strict = true`)
**Apply to:** Every function signature, every dataclass field, every test function

**Convention:**
- Every function has `-> ReturnType:` (use `-> None` for tests/`__post_init__`)
- Use builtin generics (`list[str]`, `dict[str, Any]`) — Python 3.13 syntax, NOT `List`/`Dict` from typing
- Use `int | None` (PEP 604 union) NOT `Optional[int]` — confirmed in `parser/types.py:37,43,44`
- `from typing import Any` for `to_dict() -> dict[str, Any]` (RESEARCH line 134)

### Absolute Imports
**Source:** `parser/__init__.py:3-4`, `tests/parser/test_markdown.py:8`
**Apply to:** All Phase 3 source AND test files

```python
from biblio_validador.parser.markdown import ParserMd  # not `.markdown`
from biblio_validador.parser import ParserMd  # via re-export in tests
```
NEVER use relative imports (`from .types import ...`).

### Re-Export Pattern
**Source:** `parser/__init__.py:1-7`
**Apply to:** `core/__init__.py`

```python
"""<one-line PT-BR description>."""

from biblio_validador.<subpkg>.<mod1> import <Symbol1>, <Symbol2>
from biblio_validador.<subpkg>.<mod2> import <Symbol3>

__all__ = ["<Symbol1>", "<Symbol2>", "<Symbol3>"]
```
- `__all__` is a flat list of strings. CONTEXT D-03 lists alphabetical for `core/`; `parser` uses topical (parser class first). Either is acceptable per project convention; alphabetical (D-03) wins because CONTEXT explicitly fixes it.

### `enum.Enum` with String snake_case Values
**Source:** `parser/types.py:8-24` (TipoSecao)
**Apply to:** `core/enums.py` for `Severidade` AND `EstadoPatch`

**Why NOT `StrEnum` or `IntEnum`** (locked by D-14 + D-20 + RESEARCH Anti-Patterns):
- `StrEnum` makes `str(Severidade.INFO) == "info"` — loses type marker in logs (`<Severidade.INFO: 'info'>` becomes ambiguous)
- `IntEnum` perds value string in `repr` and forces `int → str` conversion in every log

### `@dataclass(frozen=True, slots=True)` for Immutable Models
**Source:** `parser/types.py:27` (Paragrafo)
**Apply to:** `core/dataclasses.py` for `Violacao` (D-05)

For `Patch` (D-06), drop `frozen=True` keep `slots=True` — RESEARCH Pattern 2 lines 333-334.

### Test File Layout
**Source:** `tests/parser/__init__.py` (empty) + `tests/parser/test_markdown.py`
**Apply to:** `tests/core/__init__.py` (empty) + `tests/core/test_dataclasses.py`

**Convention:**
- Subdirectory `tests/<subpkg>/` mirrors `src/biblio_validador/<subpkg>/`
- Empty `__init__.py` as pytest package marker
- Single `test_<module>.py` covering the subpackage's main module
- Module-level fixture if needed (parser uses `@pytest.fixture def parser() -> ParserMd`); Phase 3 needs no fixtures (pure constructors)

### Coverage Configuration (Inherited, No Change)
**Source:** `pyproject.toml:53-59`
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"

[tool.coverage.run]
source = ["biblio_validador"]
branch = true
```
**Apply to:** Phase 3 needs zero changes here. Test command: `uv run pytest --cov=biblio_validador.core --cov-report=term-missing` (RESEARCH "Quick run command" line 845). For phase gate, add `--cov-fail-under=95` per D-30.

## No Analog Found

| File / Concern | Reason | Fallback Source |
|----------------|--------|-----------------|
| `Severidade.peso()` method on Enum | No method on `TipoSecao`; project has no precedent for enum behavior | RESEARCH Pattern 3 lines 416-428 (verified empirically) |
| Module-level `_PESOS_SEVERIDADE: dict[Severidade, int]` | No precedent | RESEARCH Pattern 3 lines 423-428 |
| `_normalize_for_json` recursive helper | No serialization helper exists yet in codebase | RESEARCH Pattern 5 lines 500-516 (verified empirically) |
| `to_dict()` method on dataclass | `Paragrafo` has no JSON serialization need | RESEARCH Pattern 1 lines 313-318 + Pattern 2 lines 379-382 |
| `__post_init__` validators | `Paragrafo` has no `__post_init__`; Phase 3 introduces invariants | RESEARCH Pattern 4 lines 462-479 + concrete code in Pattern 1 lines 280-311, Pattern 2 lines 362-377 |
| Mutable dataclass (`Patch`) | All existing dataclasses (`Paragrafo`) are frozen | RESEARCH Pattern 2 lines 333-377 |
| `pytest.mark.parametrize` for invariants | Analog `test_markdown.py` does not use parametrize | RESEARCH Code Examples lines 807-831 (D-29 leaves choice to executor) |
| Contract tests (frozenness, hashability, JSON round-trip) | New category; nothing similar in `test_markdown.py` | RESEARCH "Contract Tests Específicos" lines 893-910 |

When no codebase analog exists, the planner should consume the empirically-verified code from RESEARCH (each block tagged `[VERIFIED: empirical]` was tested in Python 3.13.13 in this project's `.venv` per RESEARCH "Sources" line 941).

## Metadata

**Analog search scope:** `src/biblio_validador/`, `tests/`, `pyproject.toml`
**Files scanned:** 5 source files (parser/__init__.py, parser/types.py, parser/markdown.py via reference, tests/__init__.py, tests/parser/__init__.py, tests/parser/test_markdown.py) + pyproject.toml
**Pattern extraction date:** 2026-05-05
**Analog source phase:** Phase 2 (parser-markdown) — most recent and direct precedent
**Confidence:** HIGH — Phase 3 mirrors Phase 2's structural template (1 frozen dataclass + 1 enum + 1 re-export + 1 test file), with additions (`Patch` mutable, `__post_init__` validators, `to_dict`, `peso()` method) sourced from empirically-verified RESEARCH patterns
