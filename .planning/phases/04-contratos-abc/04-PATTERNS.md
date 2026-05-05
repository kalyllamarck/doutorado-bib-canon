# Phase 4: Contratos ABC - Pattern Map

**Mapped:** 2026-05-05
**Files analyzed:** 6 new + 2 modified = 8 total
**Analogs found:** 8 / 8 (100%) — all files have an exact or role-match analog inside the repo (Phase 2 + Phase 3)

> Phase 4 is purely additive: it extends `core/` (already well-formed by Phase 3) with two ABCs, two auxiliary frozen dataclasses, two enums, and a test module. **Every file maps to an existing precedent.** Patterns to copy are concrete excerpts from Phase 2 (`parser/`) and Phase 3 (`core/`). Three Phase 4 specifics have NO codebase analog and must be sourced from RESEARCH (verified empirically in `.venv` Python 3.13.13): `@classmethod` + `@abstractmethod` order (Pattern 1), per-subclass cache via `cls.__dict__.get()` (Pattern 4), `eq=False` on `ContextoFixer` (Pattern 7).

## File Classification

| File | Status | Role | Data Flow | Closest Analog | Match |
|------|--------|------|-----------|----------------|-------|
| `src/biblio_validador/core/contracts.py` | NEW | abstract base classes + helpers + auxiliary dataclasses | model + transform | (a) `src/biblio_validador/core/dataclasses.py` for frozen dataclasses + `_normalize_for_json` module-level helper; (b) `src/biblio_validador/parser/markdown.py` for class with module-level helpers + `from __future__ import annotations` | composite (a)+(b); role-match for ABC novelty |
| `src/biblio_validador/core/enums.py` | MODIFIED (extend) | model (enum constants) | static-data | itself, Phase 3 (already declares `Severidade` + `EstadoPatch` in same file) | exact (additive append) |
| `src/biblio_validador/core/__init__.py` | MODIFIED (extend) | package re-export | static-import | itself, Phase 3 (4 symbols → 10 symbols) AND `src/biblio_validador/parser/__init__.py` for shape | exact |
| `tests/core/test_contracts.py` | NEW | unit test suite (17 tests) | request-response (pytest) | `tests/core/test_dataclasses.py` (same subpackage); `tests/parser/test_markdown.py` for fixture-file pattern | exact for layout; role-match for ABC fakes (no precedent) |
| `tests/core/fixtures/regras_fake.json` | NEW | test fixture (happy path) | static-data | `tests/parser/fixtures/eolica_first_30.md` (analog directory + `Path(__file__).parent / "fixtures" / ...` pattern) | role-match (different content type, same layout) |
| `tests/core/fixtures/regras_malformadas.json` | NEW | test fixture (`JSONDecodeError`) | static-data | same as above | role-match |
| `tests/core/fixtures/regras_regex_invalido.json` | NEW | test fixture (`re.error`) | static-data | same as above | role-match |
| `tests/core/fixtures/regras_str_e_lista.json` | NEW | test fixture (heterogeneous schema) | static-data | same as above | role-match |

**Note:** `tests/core/fixtures/__init__.py` is NOT created — fixtures dir matches `tests/parser/fixtures/` which has `__init__.py` (empty) but treated as data dir, not a Python package. CONTEXT D-32 only specifies the JSONs; the executor MAY add an empty `__init__.py` for stylistic mirror.

## Pattern Assignments

### `src/biblio_validador/core/contracts.py` (NEW — 6 components in 1 file)

**Composite analog:**
- **Frozen+slots+`__post_init__` dataclass shape** → `core/dataclasses.py` (Phase 3 — exact)
- **Module-level helpers + class with classmethods** → `parser/markdown.py` (Phase 2 — exact for `from __future__ import annotations`, module-level pattern compilation, classmethod helpers)
- **`_normalize_for_json` module-level helper next to dataclasses** → `core/dataclasses.py:16-33` (Phase 3 — exact for "helper next to types")

This file packs 6 logical components — each gets its own pattern excerpt below.

#### Imports header (verbatim copy convention)

**Analog excerpt** (`src/biblio_validador/core/dataclasses.py` lines 1-13):
```python
"""Dataclasses core: Violacao + Patch + helper _normalize_for_json.

CRITICAL: módulo se chama `dataclasses.py` mas importa do stdlib
`dataclasses`. SEMPRE usar `from dataclasses import dataclass, asdict`
(NUNCA `import dataclasses` bare — causaria self-import recursivo).
"""

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast

from biblio_validador.core.enums import EstadoPatch, Severidade
```

**Phase 4 adaptation** (with `from __future__ import annotations` per CONTEXT D-28 + RESEARCH Pattern 8):
```python
"""Contratos ABC: ValidadorBase + FixerBase + AplicacaoResultado +
ContextoFixer + helpers (D-01..D-30).

CRITICAL: este módulo segue a convenção de imports estabelecida em
Phase 3 (core/dataclasses.py): SEMPRE 'from dataclasses import dataclass'
(nunca 'import dataclasses' bare).
"""

from __future__ import annotations  # D-28: PEP 563

import json
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import ModoFixer, Scope
from biblio_validador.parser.types import Paragrafo
```

**Conventions to copy from analog:**
- Module-level docstring is multi-line PT-BR with the CRITICAL warning preserved verbatim (the `dataclasses.py` shadow concern is the SAME concern in `contracts.py`).
- Stdlib imports first (alphabetical), blank line, project imports (alphabetical by module).
- Use `from biblio_validador.core.<mod> import <Symbols>` (absolute) — confirmed in `parser/__init__.py:3-4` and `core/dataclasses.py:13`.

**Phase 4 deltas vs analog:**
- `from __future__ import annotations` (Phase 4 adds; Phase 3 omits because `core/dataclasses.py` doesn't need forward refs).
- `from collections.abc import Mapping` (D-27).
- `from abc import ABC, abstractmethod` — first occurrence in project; no prior analog inside `biblio_validador/`.
- `from typing import ClassVar` (no `Any`/`cast` needed — Phase 4 has no `to_dict()` helpers).

#### Module-level helper `_canonical_root` (lines ~21-29)

**No exact codebase analog.** Phase 2 `parser/markdown.py` uses module-level constants but no `Path(__file__).parents[N]` resolver. Source: RESEARCH Pattern + Code Examples (verified `Path(__file__).parents[3]` resolves to `biblioteca_canonica/`).

**Pattern excerpt to write** (RESEARCH Code Examples lines 916-922):
```python
def _canonical_root() -> Path:
    """Raiz da biblioteca canônica (D-09).

    Resolução: <repo>/biblioteca_canonica/ via __file__.parents[3]:
        contracts.py -> core/ -> biblio_validador/ -> src/ -> root
    """
    return Path(__file__).parents[3]
```

**Conventions still derived from analogs:**
- PT-BR docstring with `(D-09)` reference at end of summary line — exact mirror of `core/dataclasses.py:38` (`(CORE-02)`) and `parser/types.py:29` (`(D-02)`).
- `Path(__file__)` (NOT `os.path.dirname`) — biblioteca/CLAUDE.md C6 + Phase 2/3 idiom.
- One-line return — same density as `parser/markdown.py:71-85` `_construir_linha_offsets`.

#### Module-level helper `_carregar_json_simples` (lines ~32-65)

**Analog:** `core/dataclasses.py:16-33` (`_normalize_for_json`) for "module-level helper near class definitions, name with leading underscore, recursive logic, PT-BR docstring with `(D-XX)` reference, raises clear errors".

**Analog excerpt** (`src/biblio_validador/core/dataclasses.py` lines 16-33):
```python
def _normalize_for_json(obj: Any) -> Any:
    """Converte recursivamente Path/Enum/tuple em str/value/list (D-25).

    Pós-processa a saída de dataclasses.asdict() para que json.dumps()
    funcione sem encoder customizado. Recursivo: desce em dicts, listas
    e tuples para normalizar estruturas aninhadas (RESEARCH Pattern 5).
    """
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, tuple):
        return [_normalize_for_json(x) for x in obj]
    if isinstance(obj, list):
        return [_normalize_for_json(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _normalize_for_json(v) for k, v in obj.items()}
    return obj
```

**Phase 4 adaptation** (per RESEARCH Pattern 5 + Pattern 9 — heterogeneous JSON schema verified in `04_construcoes_sintaticas_proibidas.json`):
```python
def _carregar_json_simples(
    json_source: Path,
) -> Mapping[str, re.Pattern[str]]:
    """Carrega JSON-fonte + compila regex 1x (D-21).

    Schema esperado (verificado contra
    02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json):
        {
          "tipo": "...",
          "entradas": [
            {"id": "cst_NNN",
             "regex_deteccao": "..." | [...]},
            ...
          ]
        }

    Variantes aceitas (RESEARCH Pattern 9):
        - regex_deteccao: str OU list[str].
        - chave alternativa regex_deteccao_aproximada (cst_011).

    Sem flags adicionais: re.UNICODE é default em Python 3, e os JSONs
    codificam casing explícito — IGNORECASE alteraria semântica.

    Raises:
        FileNotFoundError: json_source inexistente (D-22).
        json.JSONDecodeError: JSON malformado (D-22).
        re.error: regex inválido — mensagem inclui regra_id (D-22).
    """
    data = json.loads(json_source.read_text(encoding="utf-8"))
    compiladas: dict[str, re.Pattern[str]] = {}
    for entrada in data["entradas"]:
        rid = entrada["id"]
        raw = entrada.get("regex_deteccao") or entrada.get(
            "regex_deteccao_aproximada"
        )
        if raw is None:
            continue
        padroes = [raw] if isinstance(raw, str) else list(raw)
        try:
            if len(padroes) == 1:
                compiladas[rid] = re.compile(padroes[0])
            else:
                compiladas[rid] = re.compile(
                    "|".join(f"(?:{p})" for p in padroes)
                )
        except re.error as e:
            raise re.error(f"regra {rid}: {e}") from e
    return compiladas
```

**Conventions copied from analog (`_normalize_for_json`):**
- Leading underscore for module-private helper.
- PT-BR docstring with `(D-21)` reference + `Raises:` block. (`_normalize_for_json` doesn't raise; this is an additive convention also seen in `parser/markdown.py:35-48` where `parsear` documents `FileNotFoundError` propagation.)
- Body uses simple `dict` accumulator + `for` loop — no comprehension that obscures the error path.
- `from e` chain on the re-raise — analog doesn't show this (no raises) but `parser/markdown.py:39-46` uses `raise` (re-raise) with logger; Phase 4 follows D-22's "fail fast no silenciador" principle.

**Phase 4 specifics with NO analog:**
- `re.compile` with explicit `regra_id` in error message — sourced from RESEARCH (D-22 + Pattern 5).
- Schema heterogeneity normalization (`str | list[str]` + alternative key `regex_deteccao_aproximada`) — sourced from RESEARCH Pattern 9 (verified empirically against the real JSON).
- Convention "list → `|`-joined alternatives" — sourced from RESEARCH Pattern 5 + Open Question #1 (deferred to validador concreto Phase 6 if it needs different semantics).

#### `AplicacaoResultado` dataclass (frozen+slots+tuples) (lines ~71-83)

**Analog:** `core/dataclasses.py:36-69` (`Violacao` — frozen+slots+tuple-only collections, exact match).

**Analog excerpt** (`src/biblio_validador/core/dataclasses.py` lines 36-58):
```python
@dataclass(frozen=True, slots=True)
class Violacao:
    """Violação de regra canônica detectada por um validador (CORE-02).

    Imutável após construção (frozen=True, D-05). Coleções são tuple
    (D-07: tuple[str, ...] em vez de list[str] — frozen só impede
    reatribuir o atributo, tuple fecha o buraco da imutabilidade).
    ...
    """

    arquivo: Path
    linha_inicio: int  # 1-based
    linha_fim: int  # 1-based, inclusivo
    ...
    sugestoes: tuple[str, ...] = ()  # D-07: tuple, não list
```

**Phase 4 adaptation** (per CONTEXT D-25 + RESEARCH Pattern 6):
```python
@dataclass(frozen=True, slots=True)
class AplicacaoResultado:
    """Resultado de FixerBase.aplicar (D-25).

    Tuple-only nas coleções (Phase 3 D-07): imutabilidade real.
    Patch é unhashable (Phase 3 D-06), portanto AplicacaoResultado
    também é (na prática); use comparação estrutural via ==.
    """

    patches_aceitos: tuple[Patch, ...]
    patches_rejeitados: tuple[Patch, ...]
    patches_suprimidos: tuple[Patch, ...]
    bytes_modificados: int
```

**Conventions to copy verbatim from analog:**
- `@dataclass(frozen=True, slots=True)` decorator — exact.
- PT-BR class docstring with `(D-25)` reference at end of summary line.
- Multi-line docstring referencing the heritage (Phase 3 D-07 tuple-only convention; Phase 3 D-06 Patch unhashability).
- `tuple[T, ...]` (NOT `list[T]`) — exact mirror of `Violacao.sugestoes: tuple[str, ...] = ()`.
- One inline `# comment` per field is OPTIONAL (analog uses it for index/byte-offset semantics; Phase 4 fields are self-documenting from name + type).

**Phase 4 deltas vs analog:**
- NO `__post_init__` validator (CONTEXT D-25 doesn't list invariants; the only candidate would be `bytes_modificados >= 0`, which RESEARCH Open Question #3 defers to Phase 5). Document semantics in docstring; do NOT write a validator that has nothing to enforce.
- NO `to_dict()` method (CONTEXT D-25 explicitly defers serialization to Phase 58 ORC-09).

#### `ContextoFixer` dataclass (frozen+slots+**eq=False**) (lines ~86-105)

**Analog:** `core/dataclasses.py:36-69` (`Violacao`) for shape — but Phase 4 introduces a critical delta verified empirically in RESEARCH Pattern 7.

**Analog excerpt for shape** — same as `AplicacaoResultado` block above.

**Phase 4 adaptation** (CRITICAL: `eq=False` is a research-driven addition NOT in CONTEXT.md — see RESEARCH Pitfall 4):
```python
@dataclass(frozen=True, slots=True, eq=False)
class ContextoFixer:
    """Contexto que o orchestrator passa ao fixer (D-26).

    eq=False (RESEARCH Pattern 7 — Pitfall 4):
        - regras_compiladas é Mapping (dict em runtime), unhashable.
        - Sem eq=False, hash(ctx) levanta TypeError.
        - Igualdade vira identity (`is`); semanticamente correto
          porque ContextoFixer é descartável (instância por chamada,
          nunca chave de cache).
    """

    paragrafo: Paragrafo
    todas_violacoes_paragrafo: tuple[Violacao, ...]
    regras_compiladas: Mapping[str, re.Pattern[str]]
```

**Conventions copied from analog:**
- `@dataclass(frozen=True, slots=True, ...)` — same base flags.
- PT-BR docstring with `(D-26)` reference.
- Tuple-only on `todas_violacoes_paragrafo: tuple[Violacao, ...]` — exact mirror of `Violacao.sugestoes`.
- `Mapping` from `collections.abc` — analog `Paragrafo` doesn't carry a Mapping field, so this is a Phase 4 first; the type hint convention (`Mapping[K, V]` not `dict[K, V]`) is RESEARCH-locked (CONTEXT D-27).

**Phase 4 deltas vs analog (the THREE that are research-only):**
1. `eq=False` (RESEARCH Pitfall 4 — VERIFIED empirically: `frozen+slots+Mapping field+eq=True` ⇒ `hash(ctx)` raises `TypeError: unhashable type: 'dict'`).
2. Multi-line PT-BR docstring **explicitly explains why `eq=False`** — this is a learning that future maintainers MUST see; the analog has no equivalent because Phase 3's `Violacao` is fully hashable.
3. Field order: `paragrafo` first (the violator's host), violations second (aggregated context), regras third (compiled deps) — semantic ordering from CONTEXT D-26.

#### `ValidadorBase` ABC (lines ~111-149)

**No direct codebase analog** for the ABC pattern. Phase 4 introduces the first `abc.ABC` in `biblio_validador/`.

**Component-level analogs:**
- Class docstring conventions → `core/dataclasses.py:38-58` (`Violacao` docstring style).
- `ClassVar` declarations without default → no analog in codebase; sourced from RESEARCH Pattern 3 (verified mypy strict accepts override without re-annotating).
- `@classmethod` definition → `parser/markdown.py:87-103` (`_carregar_mapa_secao` is a `@classmethod`).
- Cache class-level via `cls.__dict__.get()` → no analog; sourced from RESEARCH Pattern 4 (verified empirically).

**Pattern excerpt to write** (RESEARCH Code Examples lines 1013-1051):
```python
class ValidadorBase(ABC):
    """Contrato de validador que detecta violações (CORE-04 / D-09..D-11).

    Subclasses concretas DEVEM declarar:
        - JSON_SOURCE: Path do JSON-fonte.
        - SCOPE: granularidade (Scope.PARAGRAFO/SECAO/DOCUMENTO).
        - carregar_regras(): @classmethod que retorna
          Mapping[str, re.Pattern[str]] e compila 1x por subclasse.
        - validar(paragrafos): list[Violacao].

    Cache class-level (D-19, RESEARCH Pattern 4):
        cls._regras_compiladas vive em cls.__dict__ — não compartilhado
        entre subclasses na hierarquia. Subclasses simples implementam
        carregar_regras() chamando _carregar_json_simples e fazendo
        cache via cls.__dict__.get("_regras_compiladas").
    """

    JSON_SOURCE: ClassVar[Path]
    SCOPE: ClassVar[Scope]
    _regras_compiladas: ClassVar[
        Mapping[str, re.Pattern[str]] | None
    ] = None

    @classmethod
    @abstractmethod
    def carregar_regras(cls) -> Mapping[str, re.Pattern[str]]:
        """Compila regras do JSON-fonte (D-21).

        Subclasses devem implementar; podem reusar
        _carregar_json_simples(cls.JSON_SOURCE) para o caso padrão.
        """
        ...

    @abstractmethod
    def validar(
        self, paragrafos: list[Paragrafo]
    ) -> list[Violacao]:
        """Detecta violações nos parágrafos fornecidos (D-11)."""
        ...
```

**Conventions copied from analog (`Violacao` class docstring):**
- Multi-line PT-BR docstring with `(CORE-04 / D-09..D-11)` reference at end of summary line — exact mirror of `Violacao.__doc__: "(CORE-02 / D-09)"`.
- Multi-paragraph docstring lists *invariants subclasses must satisfy* (analog lists *invariants the constructor enforces*; semantic flip due to ABC vs concrete).
- One field per line, type-annotated, default value RHS only when CONTEXT explicitly allows (`_regras_compiladas` has `= None` per D-19).

**Phase 4 specifics with NO codebase analog (sourced from RESEARCH):**

| Pattern | Source | Critical detail |
|---------|--------|-----------------|
| `@classmethod` ABOVE `@abstractmethod` decorator order | RESEARCH Pattern 1 + Pitfall 1 | Inverting fails at **class definition time** with `AttributeError: attribute '__isabstractmethod__' of 'classmethod' objects is not writable`. VERIFIED empirically in 3.13.13. |
| `JSON_SOURCE: ClassVar[Path]` (no default) | RESEARCH Pattern 3 + CONTEXT D-08 | Subclass declares; mypy strict accepts override without re-annotating `: ClassVar[...]`. |
| `_regras_compiladas: ClassVar[Mapping[...] \| None] = None` | CONTEXT D-19 + RESEARCH Pattern 4 | **Default `= None` lives on the ABC but the ABC NEVER reads it** (`carregar_regras` is `@abstractmethod`); subclass implementations read `cls.__dict__.get("_regras_compiladas")` — NOT `cls._regras_compiladas` (which traverses MRO). |
| `Mapping[str, re.Pattern[str]]` return type | CONTEXT D-27 + RESEARCH Pattern 8 | `from __future__ import annotations` makes `re.Pattern[str]` resolvable as string-deferred annotation. |

#### `FixerBase` ABC (lines ~152-189)

**No direct codebase analog** — same novelty as `ValidadorBase`.

**Component-level analogs:**
- ABC with abstract + concrete methods in same class → no analog; sourced from RESEARCH Pattern 2.
- Class docstring → `core/dataclasses.py:36-58` (Violacao) — same style.

**Pattern excerpt to write** (RESEARCH Code Examples lines 1054-1090):
```python
class FixerBase(ABC):
    """Contrato de fixer que propõe patches (CORE-05 / D-12..D-14).

    Subclasses concretas DEVEM declarar:
        - VIOLACAO_IDS: frozenset[str] de regra_id que cobre.
        - MODO: nível de intervenção (AUTO/ASSISTIDO/LLM).
        - propor_patches(v, contexto): list[Patch].
        - aplicar(patches, modo_interativo): AplicacaoResultado
          (delega ao PatchAplicador da Phase 5).

    pode_corrigir(v) é CONCRETO (D-23): subclasses sobrescrevem só
    se precisarem refinamento (ex.: filtrar por severidade).
    """

    VIOLACAO_IDS: ClassVar[frozenset[str]]
    MODO: ClassVar[ModoFixer]

    @abstractmethod
    def propor_patches(
        self, v: Violacao, contexto: ContextoFixer
    ) -> list[Patch]:
        """Propõe patches para a violação v dado contexto (D-14)."""
        ...

    @abstractmethod
    def aplicar(
        self,
        patches: list[Patch],
        modo_interativo: bool,
    ) -> AplicacaoResultado:
        """Aplica patches; delega ao PatchAplicador (D-24)."""
        ...

    def pode_corrigir(self, v: Violacao) -> bool:
        """True se este fixer cobre v.regra_id (D-23)."""
        return v.regra_id in type(self).VIOLACAO_IDS
```

**Conventions copied from analog (`Violacao` class):**
- Multi-line PT-BR docstring with `(CORE-05 / D-12..D-14)` reference.
- Class docstring lists subclass obligations + clarifies which methods are concrete vs abstract.
- `ClassVar` annotations in attribute declaration block before method definitions.
- `@abstractmethod` decorator on instance methods has NO `@classmethod` companion — these are pure instance abstracts (D-14 specifies `self` signatures).

**Phase 4 specifics with NO codebase analog (sourced from RESEARCH):**
- `frozenset[str]` for `VIOLACAO_IDS` (RESEARCH Pattern 3 + CONTEXT D-12) — chosen over `set[str]` to lock immutability at class-attr level. O(1) lookup matches `pode_corrigir` body.
- `type(self).VIOLACAO_IDS` (NOT `self.VIOLACAO_IDS`) in `pode_corrigir` body — RESEARCH Pattern 2 documents this is preferred to make the class-attr access explicit and resistant to instance shadowing.
- Inline default implementation of `pode_corrigir` is the FIRST concrete method in an ABC in this codebase. Convention from RESEARCH Pattern 2 (verified): `pode_corrigir` is one-line return; docstring above; subclass override is opt-in for refinement (e.g., filter by severity).

---

### `src/biblio_validador/core/enums.py` (MODIFIED — extend, don't replace)

**Analog:** ITSELF — Phase 3 already defines `Severidade` + `EstadoPatch` in this file with the snake_case-string Enum convention. Phase 4 appends two more enums.

**Existing structure to preserve** (`src/biblio_validador/core/enums.py` lines 1-53, must remain UNTOUCHED):
```python
"""Enums core: Severidade + EstadoPatch (D-14, D-20)."""

from enum import Enum


class Severidade(Enum):
    """Classificação de severidade de uma Violacao (D-15).
    ...
    """
    INFO = "info"
    ALERTA = "alerta"
    ERRO = "erro"
    CRITICO = "critico"

    def peso(self) -> int:
        ...

_PESOS_SEVERIDADE: dict[Severidade, int] = {...}


class EstadoPatch(Enum):
    """Ciclo de vida de um Patch (D-20).
    ...
    """
    PROPOSTO = "proposto"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    SUPRIMIDO = "suprimido"
```

**Phase 4 additive change** (RESEARCH Code Examples lines 1127-1144):
```python
# ─────────────────────── Phase 4 additions ────────────────────────────


class Scope(Enum):
    """Granularidade do alvo de validação (D-10/D-15)."""

    PARAGRAFO = "paragrafo"
    SECAO = "secao"
    DOCUMENTO = "documento"


class ModoFixer(Enum):
    """Nível de intervenção de um Fixer (D-13/D-17)."""

    AUTO = "auto"
    ASSISTIDO = "assistido"
    LLM = "llm"
```

**Module docstring update** (line 1) — extend:
```python
# Was:
"""Enums core: Severidade + EstadoPatch (D-14, D-20)."""
# Becomes:
"""Enums core: Severidade + EstadoPatch + Scope + ModoFixer."""
```

**Conventions copied from existing-self analog:**
- `class Name(Enum)` — NOT `StrEnum`, NOT `IntEnum` (Phase 3 D-14/D-20 + Phase 4 RESEARCH "Anti-Patterns"). Loss of type marker in repr is the documented reason.
- Member names ALL_CAPS_SNAKE; values lowercase snake_case strings — exact mirror of `Severidade.INFO = "info"`.
- One-line PT-BR docstring with `(D-XX)` reference at end of summary line — exact mirror of `Severidade` and `EstadoPatch`.
- NO method on `Scope` or `ModoFixer` (CONTEXT D-16 + D-18 both explicitly defer ranking/peso to orchestrator). This mirrors `EstadoPatch` (no method) and contrasts with `Severidade.peso()` (which has business rationale for ranking).

**Phase 4 deltas vs analog:**
- Two NEW classes appended after the EstadoPatch block. The convention separator `# ─────────── Phase 4 additions ────────────` is RESEARCH-suggested for visual grouping (no codebase precedent — but Phase 3's `# Tabela de pesos` separator at line 28 confirms inline section headers are an accepted style).
- NO new helper dict like `_PESOS_SEVERIDADE` — `Scope` and `ModoFixer` have no ranking semantics.

---

### `src/biblio_validador/core/__init__.py` (MODIFIED — extend re-exports)

**Analog:** `src/biblio_validador/parser/__init__.py` (Phase 2 — exact re-export shape) AND ITSELF (Phase 3 — current 4-symbol export).

**Existing structure** (`src/biblio_validador/core/__init__.py` lines 1-6):
```python
"""Core domain types — Violacao, Patch, Severidade, EstadoPatch."""

from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import EstadoPatch, Severidade

__all__ = ["EstadoPatch", "Patch", "Severidade", "Violacao"]
```

**Phase 4 adaptation** (RESEARCH Code Examples lines 1148-1177 — alphabetical per CONTEXT D-03):
```python
"""Core domain types — Violacao, Patch, ABCs, enums."""

from biblio_validador.core.contracts import (
    AplicacaoResultado,
    ContextoFixer,
    FixerBase,
    ValidadorBase,
)
from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import (
    EstadoPatch,
    ModoFixer,
    Scope,
    Severidade,
)

__all__ = [
    "AplicacaoResultado",
    "ContextoFixer",
    "EstadoPatch",
    "FixerBase",
    "ModoFixer",
    "Patch",
    "Scope",
    "Severidade",
    "ValidadorBase",
    "Violacao",
]
```

**Conventions copied from analog (`parser/__init__.py:1-7`):**
- One-line PT-BR module docstring at top.
- Absolute imports (`from biblio_validador.<sub> import ...`) — never relative.
- `__all__` is a flat list of strings.
- No `__version__`, no side-effect code, no logging configuration.
- Multi-line `from X import (A, B, C,)` form when count > 2 — copies the format from `core/dataclasses.py:13` (single-line `from biblio_validador.core.enums import EstadoPatch, Severidade` because count is 2; for 4 symbols the parenthesized form is used to keep ≤ 80 chars/line per Phase 1 D-12).

**Phase 4 deltas vs the previous Phase 3 version of this file:**
- 4 NEW symbols added (`AplicacaoResultado`, `ContextoFixer`, `FixerBase`, `ModoFixer`, `Scope`, `ValidadorBase` = 6 in CONTEXT D-03; plus retained 4 Phase 3 = 10 total — alphabetical).
- Module docstring updated to "Core domain types — Violacao, Patch, ABCs, enums." (semantic delta: now mentions ABCs).
- `__all__` is now 10 entries; sort key is alphabetical (CONTEXT D-03 explicit; Phase 3 also followed alphabetical).

---

### `tests/core/test_contracts.py` (NEW — 17 tests)

**Analog:** `tests/core/test_dataclasses.py` (Phase 3 — exact for layout, fixture-free convention, helper functions, parametrize idiom, contract tests). Secondary analog: `tests/parser/test_markdown.py` (Phase 2 — fixture-file pattern: `Path(__file__).parent / "fixtures" / "..."` constant at module top).

**Imports header pattern** (RESEARCH Code Examples lines 1182-1206 — already an exact composition of patterns from both analogs):
```python
"""Smoke tests Phase 4 — ValidadorBase + FixerBase contratos (D-31..D-34)."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar

import pytest

from biblio_validador.core import (
    AplicacaoResultado,
    ContextoFixer,
    FixerBase,
    ModoFixer,
    Scope,
    ValidadorBase,
)
from biblio_validador.core.contracts import _carregar_json_simples
from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.parser.types import Paragrafo

FIXT = Path(__file__).parent / "fixtures"
```

**Conventions copied from `tests/core/test_dataclasses.py` (Phase 3 — exact):**
- Module docstring `"""Smoke tests Phase X — ... (D-XX/D-YY)."""` — exact mirror of Phase 3:1.
- Stdlib first (alphabetical) → blank line → third-party (`pytest`) → blank line → project imports.
- Use `from biblio_validador.core import ...` (the public re-export) for symbols re-exported by `__init__.py` — validates the re-export contract (mirrors Phase 3 test_dataclasses.py:9 `from biblio_validador.core import EstadoPatch, Patch, Severidade, Violacao`).
- Internal/private symbols imported via deeper path (`from biblio_validador.core.contracts import _carregar_json_simples`) — same convention; `_carregar_json_simples` is module-private to `contracts.py`.

**Conventions copied from `tests/parser/test_markdown.py` (Phase 2 — fixture-file constant):**
- Module-level `FIXT = Path(__file__).parent / "fixtures"` constant — exact mirror of `EOLICA_FIXTURE = Path(__file__).parent / "fixtures" / "eolica_first_30.md"` at line 10.
- Test functions reference `FIXT / "regras_fake.json"` — same pattern as analog's `EOLICA_FIXTURE.exists()`.

**Phase 4 deltas vs analog (Phase 3 has no fixture files; Phase 2 has fixtures but no ABC fakes):**
- `from __future__ import annotations` at top — Phase 3 test doesn't use this; Phase 4 adds it because the test file declares fake subclasses with `ClassVar[...]` annotations (and `Paragrafo` import is type-only-relevant for the `_FixerFake` aplicar signature).
- Two fake ABC subclasses INSIDE the test module (`_ValidadorFake`, `_FixerFake`, `_ValidadorIncompleto`, `_FixerIncompleto`) — no analog; sourced from RESEARCH Pattern 2 + Pitfall 8 (testing ABC instantiation `TypeError` requires concrete subclasses fakes).
- Test pattern `with pytest.raises(TypeError, match="abstract method"):` — RESEARCH-locked exact `TypeError` message substring.
- Test pattern `r1 is r2` to assert cache identity — RESEARCH Pattern 9 (verified empirically).

#### Test functions — concrete patterns from analog `test_dataclasses.py`

**Helper function pattern** (`tests/core/test_dataclasses.py` lines 19-33):
```python
def _violacao_minima(**overrides: object) -> Violacao:
    """Helper: Violacao com defaults validos, parametrizavel via kwargs."""
    base: dict[str, object] = dict(
        arquivo=Path("a.md"),
        linha_inicio=1,
        linha_fim=1,
        col_inicio=1,
        col_fim=5,
        trecho_violador="abcd",
        regra_id="lex_001",
        regra_nome="X",
        severidade=Severidade.ERRO,
    )
    base.update(overrides)
    return Violacao(**base)  # type: ignore[arg-type]
```

**Phase 4 adaptation** (RESEARCH Code Examples lines 1303-1315):
```python
def _viol_fake(rid: str) -> Violacao:
    from biblio_validador.core.enums import Severidade
    return Violacao(
        arquivo=Path("a.md"),
        linha_inicio=1,
        linha_fim=1,
        col_inicio=1,
        col_fim=2,
        trecho_violador="x",
        regra_id=rid,
        regra_nome="X",
        severidade=Severidade.ERRO,
    )
```

**Convention copied:** helper takes single positional arg (`rid`) instead of `**overrides` because Phase 4 only varies `regra_id`. Same one-line PT-BR docstring optional convention (Phase 4 simpler helper omits docstring; Phase 3 helper documents `**overrides` because it varies many fields).

**Lazy import inside helper** — Phase 4 uses `from biblio_validador.core.enums import Severidade` inside `_viol_fake` to avoid polluting the test module's top-level imports with `Severidade` (which is only used inside this helper). Phase 3 imports `Severidade` at top-level because every test uses it. Phase 4's narrow scope justifies the lazy import — convention documented in Phase 3 D-01 (avoid `core/dataclasses.py` shadowing) and reasonable here.

**Test function pattern** (`tests/core/test_dataclasses.py` lines 36-43, 46-50):
```python
def test_violacao_instancia_com_frozen_e_slots() -> None:
    """D-28.1: Violacao instancia, e frozen e tem __slots__."""
    v = _violacao_minima()
    assert v.regra_id == "lex_001"
    assert v.sugestoes == ()  # default D-09
    ...

def test_violacao_frozen_raises_on_mutate() -> None:
    """D-28.4: mutar regra_id levanta FrozenInstanceError."""
    v = _violacao_minima()
    with pytest.raises(FrozenInstanceError):
        v.regra_id = "outro"  # type: ignore[misc]
```

**Conventions copied:**
- `def test_NAME() -> None:` — explicit `-> None` return (mypy strict).
- Docstring `"""D-XX.N: short description."""` references CONTEXT decision ID with sub-numeric.
- `# type: ignore[misc]` (or `[abstract]`, `[arg-type]`) inline comment on the line that triggers a mypy issue intentional to the test — exact mirror of analog line 50 (`# type: ignore[misc]`) and Phase 4's planned `_ValidadorIncompleto()  # type: ignore[abstract]`.

**Parametrize pattern** (`tests/core/test_dataclasses.py` lines 87-101):
```python
@pytest.mark.parametrize(
    "overrides, msg_substr",
    [
        (dict(linha_inicio=0), "linha_inicio"),
        (dict(linha_inicio=2, linha_fim=1), "linha_fim"),
        (dict(col_inicio=0), "col_inicio"),
        (dict(col_inicio=5, col_fim=2, trecho_violador="ab"), "col_fim"),
    ],
)
def test_violacao_invariantes_raise(
    overrides: dict[str, object], msg_substr: str
) -> None:
    """D-29: __post_init__ raises ValueError com regra_id no contexto."""
    with pytest.raises(ValueError, match=msg_substr):
        _violacao_minima(**overrides)
```

**Phase 4 application:** D-31's 4 success criteria can be split into individual test functions (RESEARCH Code Examples 1219-1349 shows split form) OR parametrized (CONTEXT D-31 leaves to executor's discretion). The split form is recommended to mirror RESEARCH's verified examples and to make per-test failure messages crisp; parametrize is acceptable for the 3 D-33 error tests if executor prefers (one parametrized function with the 3 file-name + expected-exception pairs).

**Auxiliary tests pattern** (`tests/core/test_dataclasses.py` lines 187-272):
```python
def test_aux_violacao_frozenness_contract() -> None:
    """Contract 1: detecta regressao se alguem remover frozen=True."""
    params = Violacao.__dataclass_params__  # type: ignore[attr-defined]
    assert params.frozen is True
```

**Phase 4 application** — RESEARCH Nyquist tests (N1-N12) suggest `test_aux_*` functions for:
- `test_aux_canonical_root` (N12) — `_canonical_root()` returns `Path` ending with `biblioteca_canonica`.
- `test_aux_contexto_fixer_hashable_via_identity` (N9) — `hash(ContextoFixer(...))` works because `eq=False`.
- `test_aux_aplicacao_resultado_eq` (N10) — structural equality on `AplicacaoResultado`.
- `test_aux_cache_isolado_entre_subclasses` (N8) — two fake subclasses have isolated `_regras_compiladas`.
- `test_aux_pode_corrigir_violacao_ids_vazio` (N4) — `frozenset()` ⇒ False always.
- `test_aux_carregar_entradas_vazias` (N5) — `entradas: []` returns `{}`.

Each follows the analog convention: prefix `test_aux_` + docstring `"""<Pitfall/Pattern ref>: ..."""`.

---

### Test fixtures `tests/core/fixtures/*.json` (4 NEW JSON files)

**Analog:** `tests/parser/fixtures/eolica_first_30.md` — sibling fixture file in same directory layout.

**Layout precedent verified** (`ls tests/parser/fixtures/`):
```
__init__.py
eolica_first_30.md
```

**Phase 4 directory mirror** — create `tests/core/fixtures/` (no analog inside `tests/core/` yet; Phase 3 had no fixtures). Optional empty `__init__.py` for stylistic mirror with `tests/parser/fixtures/__init__.py` (verified `wc -l` returns 0).

**Fixture content patterns** (RESEARCH Code Examples lines 1373-1404):

**`regras_fake.json`** (happy path — exercises `_carregar_json_simples` success):
```json
{
  "tipo": "fake",
  "entradas": [
    {"id": "cst_999", "regex_deteccao": "\\bfake\\b"}
  ]
}
```
Schema convention: `tipo` + `entradas[] {id, regex_deteccao}` — matches the real `04_construcoes_sintaticas_proibidas.json` minimum schema (RESEARCH Pattern 9). Fixture is INTENTIONALLY minimal (1 entry) — fixtures live in `tests/`, NOT in `02_escrita/` (CONTEXT D-32 explicit: don't pollute canonical dataset).

**`regras_malformadas.json`** (truncated JSON — triggers `json.JSONDecodeError`):
```json
{ "entradas": [
```
Just `{ "entradas": [` (truncated). Verified: triggers `json.JSONDecodeError`.

**`regras_regex_invalido.json`** (invalid regex — triggers `re.error`):
```json
{
  "tipo": "fake",
  "entradas": [
    {"id": "cst_invalido", "regex_deteccao": "(?P<unfinished"}
  ]
}
```
Verified: `re.compile("(?P<unfinished")` raises `re.error: missing >`; `_carregar_json_simples` re-raises with `regra cst_invalido: missing >`.

**`regras_str_e_lista.json`** (heterogeneous schema — exercises Pattern 9 normalization):
```json
{
  "tipo": "fake",
  "entradas": [
    {"id": "cst_str", "regex_deteccao": "\\bsimples\\b"},
    {"id": "cst_lista", "regex_deteccao": ["\\ba\\b", "\\bb\\b"]},
    {"id": "cst_alt_key", "regex_deteccao_aproximada": ["\\bc\\b"]}
  ]
}
```
This fixture is NOT explicitly in CONTEXT D-32 but is REQUIRED to verify that `_carregar_json_simples` correctly handles the heterogeneous schema (RESEARCH Pattern 5/9 — VERIFIED empirically against the real JSON-fonte). Without this fixture, the heterogeneous-schema branch is uncovered → coverage drops below 95% (D-34) and Phase 6 (cst_012 validador, which uses `regex_deteccao: list[str]`) hits an untested code path.

**Conventions copied from analog `eolica_first_30.md`:**
- Fixtures live in `tests/<subpkg>/fixtures/` directory.
- Filename is descriptive (`regras_fake.json` mirrors `eolica_first_30.md`).
- Contents are minimal but real-shaped (analog has 30 lines of real article; Phase 4 fixtures have 1-3 entries of real-shaped JSON-fonte).

---

## Shared Patterns

These patterns apply across multiple Phase 4 files and are derived from existing-codebase precedents (Phase 1 → 3) plus locked-RESEARCH additions.

### PT-BR Docstring + Decision-ID Reference

**Source:** All Phase 1+2+3 source files (`parser/types.py:9`, `parser/markdown.py:1-4`, `core/dataclasses.py:38`, `core/enums.py:6`).
**Apply to:** All Phase 4 modules (every class, every public function, every test function).

**Convention:**
- Module docstring: one-line PT-BR sentence summarizing module purpose.
- Class docstring: PT-BR with `(D-XX)` or `(CORE-NN / D-XX)` reference at end of summary line. Multi-line docstrings explain invariants and subclass obligations.
- Helper docstring: PT-BR with `(D-XX)` reference + optional `Raises:` block.
- Test docstring: `"""D-XX.N: short description."""` — references CONTEXT decision ID with sub-numeric (D-31.1, D-31.2, ...).
- Code comments inline next to fields: short PT-BR, ≤ 80 chars (e.g., `# 1-based, inclusivo`).

### Type Hints 100% (CLAUDE.md Rule 9 + mypy strict)

**Source:** All Phase 1+2+3 source files; `pyproject.toml [tool.mypy] strict = true` (Phase 1 D-13).
**Apply to:** Every function signature, every dataclass field, every test function, every helper.

**Convention:**
- Every function has `-> ReturnType:` (use `-> None` for tests/`__post_init__`).
- Use builtin generics (`list[str]`, `dict[str, Any]`, `tuple[Patch, ...]`) — Python 3.13 syntax, NOT `List`/`Dict` from typing.
- Use `int | None` (PEP 604 union) NOT `Optional[int]` — confirmed in `parser/types.py:37,43,44` and `core/dataclasses.py:70,140`.
- `from typing import ClassVar` for class-level attribute annotations (Phase 4 first occurrence — locked by CONTEXT D-08).
- `Mapping[K, V]` from `collections.abc` (NOT `dict[K, V]` in signatures) — RESEARCH Pattern 8 + CONTEXT D-27.

### Absolute Imports Only

**Source:** `parser/__init__.py:3-4`, `core/__init__.py:3-4`, `tests/parser/test_markdown.py:8`, `tests/core/test_dataclasses.py:9`.
**Apply to:** All Phase 4 source AND test files.

```python
# CORRECT (Phase 4 must follow):
from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.parser.types import Paragrafo
from biblio_validador.core import ValidadorBase  # via re-export in tests

# WRONG (NEVER use):
from .dataclasses import Patch
from ..parser.types import Paragrafo
```

### English ASCII in Code, PT-BR in Docstrings

**Source:** Phase 1+2+3 convention (CONTEXT 03 §"Established Patterns" + CONTEXT 04 §"Established Patterns").
**Apply to:** All Phase 4 modules.

**Examples from analogs:**
- `parser/markdown.py`: identifier `_construir_linha_offsets` (PT-BR ASCII identifier) + docstring `"""Tabela cumulativa de offsets de início de cada linha."""`.
- `core/dataclasses.py`: identifier `_normalize_for_json` (English ASCII) + docstring `"""Converte recursivamente Path/Enum/tuple em str/value/list."""`.

**Phase 4 application:**
- `_canonical_root`, `_carregar_json_simples` — English ASCII identifier (the latter has PT-BR sub-word `carregar` because the *concept* "load JSON simples" is project domain term).
- `ValidadorBase`, `FixerBase`, `AplicacaoResultado`, `ContextoFixer` — English-rooted PT-BR with ASCII characters only.
- Field names: `JSON_SOURCE`, `SCOPE`, `VIOLACAO_IDS`, `MODO`, `paragrafo`, `todas_violacoes_paragrafo`, `regras_compiladas` — PT-BR ASCII, snake_case for instance attrs and ALL_CAPS for class attrs.

### NO `loguru`/`logging`/`print` in `core/`

**Source:** Phase 3 D-33 (locked) — `core/` is pure model + contract.
**Apply to:** `src/biblio_validador/core/contracts.py`, `src/biblio_validador/core/enums.py`.

**Compare to analogs:**
- `parser/markdown.py:11` imports `loguru.logger` — OK because `parser/` is I/O.
- `core/dataclasses.py` does NOT import `loguru` — pure model.
- `core/enums.py` does NOT import `loguru` — pure model.

**Phase 4 application:**
- `_carregar_json_simples` raises errors with `regra_id` in message — but does NOT log them. Caller (Phase 8 orchestrator) handles logging.
- `_canonical_root` returns `Path` — no logging.
- ABC methods are abstract — no body to log.

### `from __future__ import annotations` in `contracts.py` (Phase 4 specific)

**Source:** CONTEXT D-28 (locked) + RESEARCH Pattern 8 + Phase 2 precedent (`parser/markdown.py` does NOT have it; Phase 4 INTRODUCES it).

**Apply to:** `src/biblio_validador/core/contracts.py` ONLY.
- Other Phase 4 files (`enums.py`, `__init__.py`, `tests/core/test_contracts.py`) — `test_contracts.py` DOES have it (RESEARCH Code Examples line 1184), but `enums.py` and `__init__.py` do NOT need it (no forward refs, no PEP 604 union of class-not-yet-defined types).

**Why required for `contracts.py`:**
- `re.Pattern[str]` annotation — works without `from __future__ import annotations` in Python 3.13 because `re.Pattern` is generic in 3.9+, but PEP 563 deferred evaluation simplifies any future forward refs (e.g., if `ContextoFixer` later self-references).
- Consistency with RESEARCH Code Examples (skeleton uses it).

### Frozen+slots Dataclass for Immutable Models

**Source:** `parser/types.py:27` (Paragrafo) + `core/dataclasses.py:36` (Violacao).
**Apply to:** `AplicacaoResultado` (frozen+slots) AND `ContextoFixer` (frozen+slots+`eq=False`).

**Phase 4 critical delta from analog:**
- `AplicacaoResultado` follows analog exactly: `@dataclass(frozen=True, slots=True)`.
- `ContextoFixer` adds `eq=False` — RESEARCH Pattern 7 + Pitfall 4 (verified: `frozen+slots+Mapping field+default eq=True` ⇒ `hash()` raises `TypeError: unhashable type: 'dict'`).

### Tuple-Only Collections in Frozen Dataclasses

**Source:** `core/dataclasses.py:69` (`Violacao.sugestoes: tuple[str, ...] = ()`) — Phase 3 D-07 anti-pitfall (frozen only blocks reassignment, not mutation; tuple closes the gap).
**Apply to:** `AplicacaoResultado.patches_aceitos/rejeitados/suprimidos: tuple[Patch, ...]`; `ContextoFixer.todas_violacoes_paragrafo: tuple[Violacao, ...]`.

**Phase 4 application:** No `list[Patch]` in dataclass fields — only `tuple[Patch, ...]`. The `aplicar(self, patches: list[Patch], ...)` method signature uses `list` (mutable input arg from caller is fine), but the `AplicacaoResultado` field is `tuple` (immutable record).

### `enum.Enum` with String snake_case Values

**Source:** `parser/types.py:8-24` (TipoSecao), `core/enums.py:6-21` (Severidade), `core/enums.py:38-52` (EstadoPatch).
**Apply to:** `Scope` and `ModoFixer` (Phase 4 additions to `core/enums.py`).

**Why NOT `StrEnum` or `IntEnum`** (Phase 3 D-14/D-20 + Phase 4 RESEARCH "Anti-Patterns"):
- `StrEnum` makes `str(Scope.PARAGRAFO) == "paragrafo"` — loses type marker in logs.
- `IntEnum` perds value string in `repr` and forces `int → str` conversion in every log.

### Test File Layout

**Source:** `tests/parser/__init__.py` (empty 0 bytes) + `tests/parser/test_markdown.py`; `tests/core/__init__.py` (empty 0 bytes) + `tests/core/test_dataclasses.py`.
**Apply to:** `tests/core/test_contracts.py` + `tests/core/fixtures/` (mirrors `tests/parser/fixtures/`).

**Convention:**
- Subdirectory `tests/<subpkg>/` mirrors `src/biblio_validador/<subpkg>/`.
- Empty `__init__.py` as pytest package marker (verified 0 bytes in both `tests/parser/` and `tests/core/`).
- One `test_<module>.py` per source module: Phase 4 `tests/core/test_contracts.py` covers `core/contracts.py` (and `core/enums.py` extensions are tested via the smoke import).
- Module-level fixture constant `FIXT = Path(__file__).parent / "fixtures"` (mirrors `EOLICA_FIXTURE` in `test_markdown.py:10`).

### Coverage Configuration (Inherited from Phase 1)

**Source:** `pyproject.toml [tool.coverage.run] source = ["biblio_validador"]; branch = true` + `[tool.pytest.ini_options]` (Phase 1 D-14).
**Apply to:** Phase 4 needs zero changes here.

**Test commands per validation level:**
- Per-task: `uv run pytest tests/core/test_contracts.py -x` (~< 1s).
- Per-wave: `uv run pytest --cov=biblio_validador.core --cov-report=term-missing --cov-fail-under=95` (Phase 3 + 4 combined; ~< 3s).
- Phase gate: full suite + `uv run mypy src/biblio_validador/core/` + `uv run ruff check src/biblio_validador/core/ tests/core/`.

### `pytest.raises` with `match=` for Error Tests

**Source:** `tests/core/test_dataclasses.py:99-101` (`pytest.raises(ValueError, match="linha_inicio")`); `tests/parser/test_markdown.py:163-165` (`pytest.raises(FileNotFoundError)`).
**Apply to:** Phase 4 D-33 error tests AND D-31.1 contract tests.

**Phase 4 application:**
```python
# D-31.1 — contract violation:
with pytest.raises(TypeError, match="abstract method"):
    _ValidadorIncompleto()  # type: ignore[abstract]

# D-33 — error propagation in _carregar_json_simples:
with pytest.raises(FileNotFoundError):
    _carregar_json_simples(FIXT / "nao_existe.json")
with pytest.raises(json.JSONDecodeError):
    _carregar_json_simples(FIXT / "regras_malformadas.json")
with pytest.raises(re.error, match="cst_invalido"):
    _carregar_json_simples(FIXT / "regras_regex_invalido.json")
```

The `match=` argument is mandatory whenever the error message conveys diagnostic info (e.g., `regra_id` per D-22 — Phase 4 verifies the helper actually injects `regra_id` in the `re.error` re-raise).

---

## No Analog Found

Three Phase 4 patterns have NO precedent in the existing codebase. The planner MUST source these from RESEARCH (each verified empirically in `.venv` Python 3.13.13):

| Pattern | Source | Why no codebase analog |
|---------|--------|------------------------|
| `@classmethod` ABOVE `@abstractmethod` decorator order | RESEARCH Pattern 1 + Pitfall 1 (lines 374-408) | First ABC in the project; first `@abstractmethod` ever. Inverting fails at class-definition time with `AttributeError`. |
| Per-subclass cache via `cls.__dict__.get("_regras_compiladas")` (NOT `cls._regras_compiladas`) | RESEARCH Pattern 4 + Pitfall 2 (lines 492-532) | First class-level cache pattern in the project. Naive `cls._regras_compiladas` reads via MRO and shares cache across hierarchy. |
| `eq=False` on frozen+slots dataclass with `Mapping` field | RESEARCH Pattern 7 + Pitfall 4 (lines 632-678) | First dataclass in project with a `Mapping` field. Default `eq=True` generates `__hash__` that raises `TypeError` on unhashable dict. |
| `_canonical_root()` via `Path(__file__).parents[N]` | RESEARCH Code Examples lines 916-922 | First `__file__`-relative path resolver in `core/`. Trivial pattern; no codebase precedent only because Phase 1-3 didn't need to resolve `<repo>/biblioteca_canonica/`. |
| ABC + abstract `@classmethod` + `ClassVar` decls | RESEARCH Pattern 1 + 3 (lines 374-490) | First ABC; first `ClassVar` in project. mypy strict accepts subclass override without re-annotating `: ClassVar[...]` (verified). |
| Concrete method (`pode_corrigir`) inside ABC alongside abstract methods | RESEARCH Pattern 2 (lines 411-447) | First ABC; first mixed abstract+concrete pattern. `type(self).VIOLACAO_IDS` (NOT `self.VIOLACAO_IDS`) is the explicit-class-access idiom. |
| Heterogeneous JSON-fonte schema normalization (`str | list[str]` + `regex_deteccao_aproximada`) | RESEARCH Pattern 5 + 9 (lines 534-602, 707-740) | Phase 4 is the first consumer of `02_escrita/termos_proibidos/*.json` — schema heterogeneity verified empirically against the real JSON. |

When the planner writes the PLAN.md `actions:` for these items, the source MUST be the RESEARCH section (cited line numbers above) and NOT a guess from prior similar codebase pieces (because there are none).

---

## Adaptations Needed for Phase 4 (Deltas Summary)

| File | Pattern from analog | Phase 4 delta | Source of delta |
|------|---------------------|---------------|-----------------|
| `core/contracts.py` | Frozen+slots+`__post_init__` from `core/dataclasses.py` | NO `__post_init__` on `AplicacaoResultado` (no invariants to enforce) | CONTEXT D-25 absence of invariants |
| `core/contracts.py` | Frozen+slots from `core/dataclasses.py` | `eq=False` on `ContextoFixer` (Mapping field) | RESEARCH Pattern 7 + Pitfall 4 |
| `core/contracts.py` | Class with classmethod from `parser/markdown.py` | `@classmethod` + `@abstractmethod` composition (decorator order) | RESEARCH Pattern 1 + Pitfall 1 |
| `core/contracts.py` | Module-level helper from `core/dataclasses.py` (`_normalize_for_json`) | Two helpers (`_canonical_root`, `_carregar_json_simples`); the second has `Raises:` block | RESEARCH Pattern 5 + CONTEXT D-22 |
| `core/contracts.py` | NO precedent for ABC | Two `abc.ABC` classes; first in project | RESEARCH Pattern 1 + 2 |
| `core/contracts.py` | NO precedent for `ClassVar` | 6 `ClassVar` declarations (4 in ABCs + `_regras_compiladas` w/ default + `_PESOS_SEVERIDADE`-style) | RESEARCH Pattern 3 + CONTEXT D-08 |
| `core/contracts.py` | NO precedent for `from __future__ import annotations` in `core/` | Add at top of file | CONTEXT D-28 + RESEARCH Pattern 8 |
| `core/enums.py` | Self (already has 2 enums in this file) | Append 2 more enums (`Scope`, `ModoFixer`); update module docstring | CONTEXT D-15..D-18 |
| `core/__init__.py` | Self (4 symbols) + `parser/__init__.py` (shape) | Re-export grows 4→10 symbols; alphabetical; module docstring updated | CONTEXT D-03 |
| `tests/core/test_contracts.py` | `tests/core/test_dataclasses.py` (layout, helper, parametrize) + `tests/parser/test_markdown.py` (FIXT constant) | 4 fake ABC subclasses inside test module + `from __future__ import annotations` | RESEARCH Code Examples 1209-1349 |
| `tests/core/fixtures/*.json` | `tests/parser/fixtures/eolica_first_30.md` (layout) | 4 minimal JSON fixtures in different content type | CONTEXT D-32 + D-33 + RESEARCH Pattern 9 (additional `regras_str_e_lista.json`) |

---

## Conventions to Preserve (Don't Drift)

These are NOT new for Phase 4 — they are existing project conventions that Phase 4 must NOT erode:

1. **Python 3.13.13 idioms** — `int | None`, `list[str]`, `dict[str, Any]`. NEVER `Optional`/`List`/`Dict`.
2. **Absolute imports only.** NEVER `from .X import` in `src/` or `tests/`.
3. **`from dataclasses import dataclass` (NEVER `import dataclasses` bare)** — `core/dataclasses.py` shadow concern preserved in `core/contracts.py` per RESEARCH Pitfall 7.
4. **PT-BR docstrings, English ASCII identifiers** — every Phase 4 file.
5. **One-line module docstring referencing decision IDs** — `(D-XX)` or `(CORE-NN / D-XX)`.
6. **No `loguru`/`print` in `core/`** — `core/` is pure model + contract (Phase 3 D-33).
7. **No `__version__`, no side-effect code in `__init__.py`** — `parser/__init__.py:1-7` precedent.
8. **`@dataclass(frozen=True, slots=True)` for immutable models** — `Paragrafo`, `Violacao` precedents.
9. **`tuple[T, ...]` (NOT `list[T]`) for collection fields in frozen dataclasses** — `Violacao.sugestoes` precedent.
10. **`enum.Enum` (NOT `StrEnum`/`IntEnum`)** — `TipoSecao`, `Severidade`, `EstadoPatch` precedents.
11. **Member values: lowercase snake_case strings** — exact convention since Phase 2.
12. **mypy strict + ruff line-length=80** — Phase 1 D-12/D-13 inherited.
13. **`pytest.raises(ExcType, match="substring")` for error tests** — `test_dataclasses.py:100,225,241,257-262` precedent.
14. **Test function `def test_X() -> None:`** — explicit `-> None` (mypy strict).
15. **Test docstring `"""D-XX.N: ..."""`** — Phase 2/3 convention.
16. **`tests/<subpkg>/__init__.py` empty (0 bytes)** as pytest package marker — verified in `tests/parser/__init__.py` and `tests/core/__init__.py`.
17. **Helper functions in tests use `_underscore_prefix`** — `_violacao_minima`, `_patch_minimo` precedent → Phase 4 `_viol_fake`, `_ValidadorFake`, `_FixerFake`.
18. **Inline `# type: ignore[xxx]`** for intentional mypy bypasses in tests — `test_dataclasses.py:33,50,134,145` precedent → Phase 4 `# type: ignore[abstract]` and `# type: ignore[no-any-return]`.

---

## Metadata

**Analog search scope:** `src/biblio_validador/`, `tests/`, `pyproject.toml`, `.planning/phases/03-dataclasses-core/`.
**Files scanned (read in full):** `src/biblio_validador/parser/types.py`, `src/biblio_validador/parser/__init__.py`, `src/biblio_validador/parser/markdown.py`, `src/biblio_validador/core/dataclasses.py`, `src/biblio_validador/core/enums.py`, `src/biblio_validador/core/__init__.py`, `tests/core/test_dataclasses.py`, `.planning/phases/03-dataclasses-core/03-PATTERNS.md`. Plus partial scans of `tests/parser/test_markdown.py` (header + fixture pattern) and verified empty state of `tests/parser/__init__.py`, `tests/core/__init__.py`.
**Fixtures inspected:** `tests/parser/fixtures/eolica_first_30.md` (presence verified via `ls`).
**Pattern extraction date:** 2026-05-05.
**Analog source phases:** Phase 2 (parser-markdown) for `from __future__ import annotations`, class with module-level helpers, fixture file pattern; Phase 3 (dataclasses-core) for frozen+slots + `__post_init__` + module-level helper + re-export shape + test file layout + parametrize idiom.
**RESEARCH-only sources (no codebase analog):** Pattern 1 (decorator order), Pattern 2 (mixed abstract+concrete in ABC), Pattern 3 (`ClassVar` declarations), Pattern 4 (`cls.__dict__.get()` cache), Pattern 5 (`_carregar_json_simples` heterogeneous schema), Pattern 7 (`eq=False` on frozen+slots+Mapping field), Pattern 8 (`from __future__ import annotations` + `re.Pattern[str]`), Pattern 9 (verified JSON schema heterogeneity).
**Confidence:** HIGH — every codebase pattern was read directly from source; every research-only pattern was verified empirically per RESEARCH "Sources" section (Tests #1-#14 in Python 3.13.13 .venv).

---

*Phase 4 — Contratos ABC*
*Pattern map: 8 files, all matched (5 exact analogs + 3 role-match composites). 7 research-only patterns called out explicitly in §"No Analog Found".*
