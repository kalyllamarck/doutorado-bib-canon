# Phase 2: Parser Markdown - Pattern Map

**Mapped:** 2026-05-05
**Files analyzed:** 7 (all NEW)
**Analogs found:** 7 / 7 (3 from in-repo Phase 1 scaffold; 4 from RESEARCH.md reference snippets — empirically verified)

## Pattern Source Note

Phase 2 introduces three new module types that have **no in-repo analog yet** (`@dataclass(frozen=True, slots=True)` types module, parser class with token walk, parser test file with `tmp_path` fixtures). The repository's only pre-existing Python is the Phase 1 scaffold (3 production files + 2 test files). Therefore PATTERNS.md splits per file:

- **Style/convention analogs** → Phase 1 files (`src/biblio_validador/__init__.py`, `src/biblio_validador/cli.py`, `tests/test_cli.py`). These pin the project's house style: PT-BR docstring on line 1, single blank line between docstring and code, type hints on every signature, line-length 80, ruff `I` import grouping, `from typer.testing import CliRunner` style imports, `tmp_path`-style ad-hoc test fixtures absent (Phase 1 used `runner` module-level).
- **Algorithmic/structural analogs** → RESEARCH.md `## Code Examples` sections "Example 1" (token stream, lines 636-681), "Example 2" (full pipeline, lines 693-936), "Example 3" (`types.py`, lines 938-982), and `## Test Strategy` (lines 996-1160). These reference snippets were **empirically verified** against `markdown-it-py 4.0.0` on 2026-05-05 and produced the expected token structure on the Eólica article — the planner must treat them as the canonical shape, not aspirational.

Where a file has both kinds of analog (e.g., `markdown.py` needs Phase 1 style + RESEARCH.md algorithm), both are cited side by side.

## File Classification

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `src/biblio_validador/parser/__init__.py` | package init / re-export | static-declarative | RESEARCH.md `<user_constraints>` D-22 (lines 128-133) + Phase 1 `src/biblio_validador/__init__.py` (style) | exact — 4-line shape locked by D-22 |
| `src/biblio_validador/parser/types.py` | data model (dataclass + enum) | static-declarative | RESEARCH.md "Example 3: `parser/types.py`" (lines 938-982) + Phase 1 `__init__.py` lines 1-3 (docstring style) | exact (no in-repo dataclass; RESEARCH.md is canonical) |
| `src/biblio_validador/parser/markdown.py` | parser / transform | request-response (file → list[Paragrafo]) | RESEARCH.md "Example 2: Full Pipeline" (lines 693-936) + Phase 1 `cli.py` lines 1-7 (docstring + import style) | exact (no in-repo class; RESEARCH.md is canonical and empirically verified) |
| `tests/parser/__init__.py` | test package marker | n/a | Phase 1 `tests/__init__.py` (zero bytes) | exact (D-16 inheritance) |
| `tests/parser/test_markdown.py` | test (parser smoke + integration + property) | in-process file I/O via `tmp_path` | RESEARCH.md "Test Strategy" lines 1010-1160 + Phase 1 `tests/test_cli.py` lines 1-12 (import grouping + `runner = CliRunner()` module-level pattern) | strong — 5 unit tests + 1 property test fully scripted in RESEARCH.md |
| `tests/parser/fixtures/__init__.py` | package marker (avoid pytest collection ambiguity) | n/a | Phase 1 `tests/__init__.py` (zero bytes) | exact |
| `tests/parser/fixtures/eolica_first_30.md` | test fixture (real artigo excerpt) | static data | `Artigos/Professora Gina Pompeu/Energia Eólica Nordeste/artigo_final/artigo.md` (verbatim first ~30 lines) | exact (D-26.5 calls for trecho real) |

## Pattern Assignments

### `src/biblio_validador/parser/__init__.py` (package init / re-export)

**Analog 1 (shape):** RESEARCH.md `<user_constraints>` D-22 lines 128-133 — exact 4-line snippet.

**Analog 2 (style — docstring presence):** Phase 1 `src/biblio_validador/__init__.py` lines 1-3:

```python
"""Validador & Fixer Acadêmico — Biblioteca Canônica PPGD/Unifor."""

__version__ = "0.1.0"
```

Phase 1's `__init__.py` proves the convention: **PT-BR docstring on line 1, single blank line, then code**. Phase 2's `parser/__init__.py` extends that: PT-BR docstring → blank line → re-exports → `__all__`.

**Canonical content** (copy verbatim, RESEARCH.md D-22 + Phase 1 style):

```python
"""Sub-pacote parser — segmentação de .md/.tex em list[Paragrafo]."""

from biblio_validador.parser.markdown import ParserMd
from biblio_validador.parser.types import Paragrafo, TipoSecao

__all__ = ["ParserMd", "Paragrafo", "TipoSecao"]
```

**Critical conventions:**
- Module docstring in PT-BR (CLAUDE.md "Idioma" rule applied to Phase 1's root `__init__.py`).
- Re-exports use **absolute imports** `biblio_validador.parser.markdown`, NOT relative `.markdown` — matches Phase 1 `tests/test_cli.py` line 5 (`from biblio_validador.cli import app`). Ruff `I` will sort the two imports alphabetically (`markdown` before `types`).
- `__all__` is required to make the `from biblio_validador.parser import *` contract explicit and to silence ruff `F401` on the re-exports.
- Do **NOT** add `__version__` here (single source of truth is the root `__init__.py`).

---

### `src/biblio_validador/parser/types.py` (data model)

**Analog 1 (full content):** RESEARCH.md "Example 3: `parser/types.py`" lines 938-982 — empirical reference, copy near-verbatim.

**Analog 2 (docstring style):** Phase 1 `src/biblio_validador/__init__.py` line 1 — short PT-BR module docstring on a single physical line ending with period.

**Imports pattern** (stdlib-only, matches Phase 1 style of "minimum imports needed"):

```python
"""Tipos parser-internal: Paragrafo + TipoSecao."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
```

Three stdlib imports, no third-party. Ruff `I` will keep them in this alphabetical order (no blank line needed because they're all stdlib).

**Enum pattern** (RESEARCH.md lines 947-962 + CONTEXT.md D-03):

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

**Critical:** `enum.Enum`, **NOT** `enum.StrEnum` (D-03 explicit veto). Values are snake_case lowercase strings — readable in `loguru` log output (`logger.debug(f"tipo={p.tipo.value}")` produces `tipo=resumo`). 14 members exactly — no extras (CONTEXT.md D-03 + Architecture Map line 152).

**Dataclass pattern** (RESEARCH.md lines 965-982 + CONTEXT.md D-02):

```python
@dataclass(frozen=True, slots=True)
class Paragrafo:
    """Bloco de texto identificável linha a linha (D-02).

    Offsets relativos ao source UTF-8 NFC.
    """
    arquivo: Path
    indice: int                       # 0-based, ordem topológica
    tipo: TipoSecao
    nivel_heading: int | None         # 1-6 se heading; None se corpo
    texto: str                        # slice raw NFC, com markup preservado
    linha_inicio: int                 # 1-based
    linha_fim: int                    # 1-based, inclusivo
    offset_bytes: int                 # absoluto em UTF-8 NFC
    len_bytes: int                    # bytes UTF-8 NFC
    ref_nota: str | None              # label da footnote ("a", "1", ...)
    paragrafo_pai_idx: int | None     # idx do parágrafo que cita [^ref_nota]
```

**Critical conventions:**
- `frozen=True` enforces immutability (D-02 rationale: parser produces once, downstream is read-only).
- `slots=True` saves memory and forbids attribute injection (Python 3.10+; project pinned to 3.13 in Phase 1 D-05 → safe).
- **PEP 604 union syntax** `int | None`, NOT `Optional[int]` — required by ruff `UP` rule (configured in Phase 1 `pyproject.toml` line 47).
- Inline `# comment` after each field — RESEARCH.md uses this; mypy strict accepts; ruff does not flag. The comment IS the lightweight schema documentation.
- 11 fields exactly in this order — CONTEXT.md D-02 nails the order; downstream `Violacao` (Phase 3) will mirror `linha_inicio`/`linha_fim` names verbatim.

**Optional:** the heading→TipoSecao map dict (`_HEADING_MAP`) MAY live here per Claude's Discretion (CONTEXT.md `<decisions>` line 224). **Recommendation:** keep map in `markdown.py` as a `@classmethod` (RESEARCH.md Example 2 line 778-794) — `types.py` stays a pure data module, easier for Phase 3+ to import without dragging parser logic.

**Anti-patterns:**
- Do **NOT** use `pydantic.BaseModel` — RESEARCH.md "What NOT to Use" forbids pydantic for this domain.
- Do **NOT** add `__post_init__` validation — frozen dataclass with type hints is sufficient; mypy strict catches type errors at parser-build time.
- Do **NOT** add `__str__`/`__repr__` overrides — default dataclass repr is fine for `loguru` debug logs.

---

### `src/biblio_validador/parser/markdown.py` (parser / transform)

**Analog 1 (full algorithm):** RESEARCH.md "Example 2: Full Pipeline" lines 693-936 — empirically verified against `markdown-it-py 4.0.0` on 2026-05-05; ~340 lines including helpers; covers all 22 D-XX decisions.

**Analog 2 (docstring + imports style):** Phase 1 `src/biblio_validador/cli.py` lines 1-7:

```python
"""CLI entry point — esqueleto Phase 1.

Comandos reais (`validar`, `corrigir`, `auditar`) virão em phases futuras
(M1 piloto Phase 8 + M8 orchestrator Phase 52).
"""
import typer
```

This pins: **multi-line docstring** (line 1 = title; blank line; lines 3-4 = context paragraph), then imports immediately after closing triple-quote. Phase 2's `markdown.py` extends that with stdlib + third-party + local groups (3 groups).

**Imports pattern** (RESEARCH.md lines 696-707, ruff `I` ordering — stdlib → third-party → local with blank lines):

```python
"""biblio_validador/parser/markdown.py — parser CommonMark + footnotes.

Offsets byte-exact sobre source UTF-8 NFC; ver D-09/D-11 do CONTEXT.md.
"""
import dataclasses
import re
import unicodedata
from pathlib import Path

from loguru import logger
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.footnote import footnote_plugin

from biblio_validador.parser.types import Paragrafo, TipoSecao
```

**Critical:** 3 import groups separated by single blank lines (matches `tests/test_cli.py` lines 4-6 of Phase 1: `from typer.testing import CliRunner` then blank then `from biblio_validador.cli import app`). Ruff `I` enforces this ordering automatically.

**Module-level constants** (RESEARCH.md lines 709-711):

```python
_REGEX_FOOTNOTE_REF = re.compile(r"\[\^([^\]]+)\]")
_RE_PUNCT = re.compile(r"[^\w\s-]", re.UNICODE)
_RE_SPACES = re.compile(r"\s+")
```

**Critical:** Underscore prefix marks them private (ruff `F401` won't flag, since used internally). `re.compile` at module level is the canonical Python pattern for hot regex (compiled once per process).

**Class pattern — `ParserMd`** (RESEARCH.md lines 714-936 + CONTEXT.md D-21):

The class has 1 public method (`parsear`) and 6 private helpers. The CONTEXT.md D-21 mandates "classe (não função top-level)" to allow future configuration injection (mapa de seções customizado, callbacks de log). Phase 2 instantiates without args.

```python
class ParserMd:
    """Parser CommonMark + footnotes para biblio_validador.

    Offsets são relativos ao source UTF-8 NFC. Arquivos em NFD
    (ex.: macOS) são convertidos silenciosamente. Validadores
    operam sempre em NFC.
    """

    def __init__(self) -> None:
        self._md = MarkdownIt().use(footnote_plugin)
        self._mapa_secao = self._carregar_mapa_secao()

    def parsear(self, path: Path) -> list[Paragrafo]:
        ...
```

**Critical:** docstring on `parsear` MUST contain the NFC invariant verbatim (D-12 mandate). The text "Offsets são relativos ao source UTF-8 NFC. Arquivos em NFD (ex.: macOS) são convertidos silenciosamente. Validadores operam sempre em NFC." (D-12) is part of the contract — Phase 5 PatchAplicador will rely on this docstring as the documented invariant.

**Core pattern: `parsear()` pipeline** (RESEARCH.md lines 726-760 + CONTEXT.md D-09/D-11/D-18/D-19/D-20):

```python
def parsear(self, path: Path) -> list[Paragrafo]:
    logger.info(f"parsear: {path}")
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        logger.error(f"arquivo não encontrado: {path}")
        raise

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        logger.error(f"encoding inválido em {path}")
        raise

    # BOM strip
    if text.startswith("\ufeff"):
        text = text[1:]
    # CRLF → LF (D-20)
    text = text.replace("\r\n", "\n")
    # NFC (D-11, CORE-11)
    text_nfc = unicodedata.normalize("NFC", text)
    if text != text_nfc:
        logger.info(f"source NFD detectado, convertido para NFC: {path}")

    if not text_nfc.strip():
        return []

    src_bytes = text_nfc.encode("utf-8")
    linha_offsets = self._construir_linha_offsets(src_bytes)

    tokens = self._md.parse(text_nfc)
    paragrafos = self._walk(tokens, src_bytes, linha_offsets, path)
    paragrafos = self._resolver_pais(paragrafos)
    logger.info(f"parsear: {len(paragrafos)} parágrafos")
    return paragrafos
```

**Order is load-bearing** (RESEARCH.md Pitfall 6 line 586): `read_bytes → decode → strip BOM → CRLF→LF → NFC → encode UTF-8 → linha_offsets → parse → walk → resolver`. **Any reordering breaks offsets** (Pitfalls 4 and 6 explicitly).

**Logging pattern** (RESEARCH.md uses + CONTEXT.md D-25):
- `logger.info` at entry: `"parsear: {path}"` and at exit: `"parsear: {N} parágrafos"`.
- `logger.error` before re-raising in `except FileNotFoundError` and `except UnicodeDecodeError` blocks.
- `logger.info` (NOT warning) when NFD→NFC conversion happens — Pitfall 4 mitigation (auditable trail).
- `logger.warning` only inside `_resolver_pais` for orphan footnotes (RESEARCH.md line 415).
- D-25 also calls for `DEBUG por bloco tokenizado` — implementer's discretion (CONTEXT.md `<decisions>` line 223). Recommendation: skip the `DEBUG` per-block log for Phase 2 (would flood logs on 30k-word artigo); add only if a bug requires it.

**Helper pattern: `_construir_linha_offsets`** (RESEARCH.md lines 762-776 — list comprehension idiomático, RESEARCH.md "Don't Hand-Roll" table line 504):

```python
@staticmethod
def _construir_linha_offsets(src_bytes: bytes) -> list[int]:
    """Tabela cumulativa de offsets de início de cada linha.

    linha_offsets[k] = offset em bytes do início da linha (0-indexed).
    Sentinela final = len(src_bytes) garante que slicing do último
    bloco funcione mesmo sem trailing newline.
    """
    offsets = [0]
    for i, b in enumerate(src_bytes):
        if b == 0x0A:
            offsets.append(i + 1)
    if offsets[-1] != len(src_bytes):
        offsets.append(len(src_bytes))
    return offsets
```

**Critical** (RESEARCH.md Pitfall 6 anti-pattern line 492): the trailing sentinel `len(src_bytes)` is mandatory — last block has no trailing `\n`, slice would IndexError without it.

**Helper pattern: `_walk` token iteration** (RESEARCH.md lines 849-908 — heading state machine):

The walker has 5 token-type branches: `footnote_open` / `footnote_close` (state toggle), `heading_open` (emit + advance 3), `paragraph_open` (emit + advance 1), `fence` (emit DESCONHECIDO + advance 1), default (advance 1). All other token types (`bullet_list_open`, `list_item_open`, `blockquote_open`, etc.) are **silently skipped** — RESEARCH.md Pitfall 7 line 600 forbids emitting `Paragrafo` for them (would duplicate, since their inner `paragraph_open` is also emitted).

```python
i = 0
while i < len(tokens):
    t = tokens[i]
    if t.type == "footnote_open":
        in_footnote = t.meta.get("label")
        i += 1
        continue
    if t.type == "footnote_close":
        in_footnote = None
        i += 1
        continue
    if t.type == "heading_open":
        nivel = int(t.tag[1])
        inline = tokens[i + 1]
        secao = self._classificar_heading(
            inline.content, nivel, is_first_h1
        )
        if nivel == 1 and is_first_h1:
            is_first_h1 = False
        current_secao = secao
        out.append(self._build_paragrafo(
            t, src_bytes, linha_offsets, arquivo,
            indice=len(out), tipo=secao,
            nivel_heading=nivel, ref_nota=None,
        ))
        i += 3  # heading_open + inline + heading_close
        continue
    if t.type == "paragraph_open":
        tipo = (TipoSecao.NOTA_RODAPE if in_footnote
                else current_secao)
        out.append(self._build_paragrafo(
            t, src_bytes, linha_offsets, arquivo,
            indice=len(out), tipo=tipo,
            nivel_heading=None,
            ref_nota=in_footnote,
        ))
        i += 1
        continue
    if t.type == "fence":
        out.append(self._build_paragrafo(
            t, src_bytes, linha_offsets, arquivo,
            indice=len(out), tipo=TipoSecao.DESCONHECIDO,
            nivel_heading=None, ref_nota=None,
        ))
        i += 1
        continue
    i += 1
```

**Critical** (RESEARCH.md Pitfall 1 line 513): when `t.type == "paragraph_open"` AND `in_footnote is not None`, emit `tipo=NOTA_RODAPE` with `ref_nota=in_footnote` — the inner `paragraph_open` is the one with `map`, NOT `footnote_open` (which has `map=None`).

**Critical** (RESEARCH.md Pitfall 2 line 529): off-by-one tabulated:
```
# token.map = [0, 1] (0-indexed half-open) → linha_inicio=1, linha_fim=1
# token.map = [2, 5] (3 linhas)            → linha_inicio=3, linha_fim=5
# Regra: linha_inicio = map[0] + 1 ; linha_fim = map[1]
```
This comment SHOULD appear in `_build_paragrafo` body or as a private docstring snippet.

**Helper pattern: `_build_paragrafo`** (RESEARCH.md lines 817-847):

The keyword-only call style (`indice=...`, `tipo=...`, `nivel_heading=...`, `ref_nota=...`) is the canonical shape. The 3 mandatory positional args are `(token, src_bytes, linha_offsets, arquivo)`; the 4 keyword args make the call site self-documenting.

**Pitfall 8 mitigation** (RESEARCH.md line 615 — mypy strict on `Token.map: list[int] | None`):

```python
def _build_paragrafo(
    self,
    token: Token,
    ...
) -> Paragrafo:
    assert token.map is not None
    start, end = token.map
    ...
```

`assert token.map is not None` narrows the type for mypy strict — the walker only ever calls `_build_paragrafo` for `heading_open`/`paragraph_open`/`fence` tokens (all of which have `map`), so the assert never fires in practice but is required for type narrowing.

**Helper pattern: `_classificar_heading` + `_normalizar_heading`** (RESEARCH.md lines 796-815 + Pattern 3 lines 428-470):

```python
def _classificar_heading(
    self, texto: str, nivel: int, is_first_h1: bool
) -> TipoSecao:
    if nivel == 1 and is_first_h1:
        return TipoSecao.TITULO
    chave = self._normalizar_heading(texto)
    if chave in self._mapa_secao:
        return self._mapa_secao[chave]
    if nivel >= 2:
        return TipoSecao.SECAO
    return TipoSecao.DESCONHECIDO

@staticmethod
def _normalizar_heading(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.casefold()
    t = _RE_PUNCT.sub(" ", t)
    t = _RE_SPACES.sub(" ", t).strip()
    return t
```

**Order of branches is load-bearing** (CONTEXT.md D-06): `is_first_h1` check FIRST (h1 first → TITULO regardless of text); THEN map lookup; THEN h2+ fallback to SECAO; THEN DESCONHECIDO. Inverting branches breaks D-06.

**Helper pattern: `_resolver_pais` (Pass 2 footnote linkage)** (RESEARCH.md lines 910-935 + CONTEXT.md D-16):

```python
@staticmethod
def _resolver_pais(paragrafos: list[Paragrafo]) -> list[Paragrafo]:
    label_to_idx: dict[str, int] = {}
    for p in paragrafos:
        if p.tipo == TipoSecao.NOTA_RODAPE:
            continue
        for m in _REGEX_FOOTNOTE_REF.finditer(p.texto):
            label = m.group(1)
            if label not in label_to_idx:
                label_to_idx[label] = p.indice

    final: list[Paragrafo] = []
    for p in paragrafos:
        if p.tipo == TipoSecao.NOTA_RODAPE and p.ref_nota:
            pai_idx = label_to_idx.get(p.ref_nota)
            if pai_idx is None:
                logger.warning(
                    f"footnote órfã: [^{p.ref_nota}] sem ref "
                    f"localizável em {p.arquivo}"
                )
            final.append(
                dataclasses.replace(p, paragrafo_pai_idx=pai_idx)
            )
        else:
            final.append(p)
    return final
```

**Critical** (CONTEXT.md D-16): `dataclasses.replace(p, paragrafo_pai_idx=pai_idx)` is the ONLY way to update a `frozen=True` dataclass. Direct attribute assignment raises `FrozenInstanceError`. The import `import dataclasses` (NOT `from dataclasses import replace`) keeps the call site `dataclasses.replace(...)` self-documenting.

**Critical** (D-16 + RESEARCH.md): when no parent paragraph references the footnote, `pai_idx is None` and `logger.warning` fires — but the footnote is still appended (with `paragrafo_pai_idx=None`). Phase 30 ST-10 will detect orphan notes; Phase 2 only logs and emits.

**Anti-patterns to avoid** (RESEARCH.md "Anti-Patterns to Avoid" lines 472-494):
- Do **NOT** use `read_text(encoding="utf-8")` — loses BOM and strict encoding control.
- Do **NOT** normalize NFC after tokenizing — token.map then references NFD source while linha_offsets is NFC bytes; offsets corrupt.
- Do **NOT** compute `linha_offsets` over `str` (chars); MUST be bytes (Phase 5 PatchAplicador uses byte offsets).
- Do **NOT** reconstruct text via `token.children[*].content` — strips markup; D-09 mandates byte-slice from source.
- Do **NOT** emit `Paragrafo` for `bullet_list_open`/`list_item_open`/`blockquote_open` (Pitfall 7 — duplicates).
- Do **NOT** access `token.map[0]` without the `assert token.map is not None` narrowing (Pitfall 8 — mypy strict fails).

---

### `tests/parser/__init__.py` (test package marker)

**Analog:** Phase 1 `tests/__init__.py` — zero-byte file (verified via `wc -c tests/__init__.py` returning `0` per Phase 1 PATTERNS.md AC-1.11).

**Content:** empty file (zero bytes).

**Why:** matches Phase 1 D-16 — pytest discovery treats nested test packages consistently, prevents conftest collection ambiguity. CONTEXT.md doesn't restate D-16 because it's inherited.

---

### `tests/parser/test_markdown.py` (test — parser smoke + integration + property)

**Analog 1 (full content):** RESEARCH.md "Test Strategy" lines 1010-1160 — 5 unit tests + 1 property test scripted explicitly.

**Analog 2 (style — imports + module-level fixtures):** Phase 1 `tests/test_cli.py`:

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
```

This pins the project's test style:
- **Module docstring on line 1** (PT-BR, identifies the phase + criteria covered).
- **3 import groups** (stdlib → third-party → local) separated by blank lines.
- **Type hints on every test** (`-> None`).
- **PT-BR test docstring** identifying which decision/criterion the test pins.
- **Two assertions per test** (Nyquist 2× — `exit_code` AND content check).

**Imports pattern** (RESEARCH.md lines 1010-1014 + Phase 1 style):

```python
"""Smoke tests Phase 2 — parser CommonMark + footnotes (D-26)."""
import unicodedata
from pathlib import Path

import pytest

from biblio_validador.parser import ParserMd, Paragrafo, TipoSecao
```

`pytest` belongs in third-party group (single line, blank line both sides). Local import `from biblio_validador.parser import ...` follows the public re-export from `parser/__init__.py` D-22 — **this is the contract that downstream validadores will use**, so the test must exercise it.

**Fixture pattern** (RESEARCH.md lines 1016-1018 — module-level fixture, like Phase 1 `runner = CliRunner()`):

```python
@pytest.fixture
def parser() -> ParserMd:
    return ParserMd()
```

Phase 1 used `runner = CliRunner()` at module level (no `@pytest.fixture` decorator) because `CliRunner` is stateless. Phase 2 uses `@pytest.fixture` because `ParserMd.__init__` builds an internal MarkdownIt instance — fixture isolation prevents accidental state leak between tests (in case future PRs add caching). RESEARCH.md uses the fixture form; planner should follow that.

**Test 1 — D-26.1: 1 parágrafo simples** (RESEARCH.md lines 1021-1034):

```python
def test_paragrafo_simples_um_so_paragrafo(tmp_path, parser):
    f = tmp_path / "simples.md"
    f.write_text("Texto simples.\n", encoding="utf-8")
    paragrafos = parser.parsear(f)
    assert len(paragrafos) == 1
    p = paragrafos[0]
    assert p.linha_inicio == 1
    assert p.linha_fim == 1
    assert p.offset_bytes == 0
    assert p.tipo == TipoSecao.DESCONHECIDO
    assert p.texto == "Texto simples."  # sem trailing \n
    assert p.nivel_heading is None
    assert p.ref_nota is None
```

**Critical assertions** (Pitfall 2 line 542 — pins off-by-one): `linha_inicio == 1` AND `linha_fim == 1` for 1-line paragraph. Pitfall 3 line 545 — pins trailing-newline strip: `p.texto == "Texto simples."` (NO `\n`).

**Note on type hints in tests:** RESEARCH.md `tmp_path, parser` doesn't have type annotations on the test signatures. **Phase 1's smoke tests DO** (`def test_validar_help_exit_zero() -> None`). Mypy strict is configured for `src/` only (Phase 1 PATTERNS.md line 432) — tests are exempt; both styles pass mypy. **Recommendation:** add `-> None` to every test signature for consistency with Phase 1 style: `def test_paragrafo_simples_um_so_paragrafo(tmp_path: Path, parser: ParserMd) -> None:`. Ruff line-length 80 may force vertical break:

```python
def test_paragrafo_simples_um_so_paragrafo(
    tmp_path: Path, parser: ParserMd
) -> None:
    ...
```

**Test 2 — D-26.2: heading classificação + herança** (RESEARCH.md lines 1037-1060):

Pins D-05 (heading map), D-06 (h1-first-único → TITULO), D-07 (parágrafos herdam tipo da seção pai). Asserts `tipos[2] == (TipoSecao.RESUMO, None, "Parágrafo do resumo")` — parágrafo abaixo de `## RESUMO` herda RESUMO, não CORPO.

**Test 3 — D-26.3: NFC normalization (CORE-11)** (RESEARCH.md lines 1063-1075):

```python
def test_normalizacao_nfc(tmp_path, parser):
    # NFD form: bare "e" + combining acute (U+0301) — matches RESEARCH.md line 1067
    nfd = "cafe\u0301"
    src = f"Texto com {nfd}.\n"
    f = tmp_path / "nfd.md"
    f.write_bytes(src.encode("utf-8"))
    paragrafos = parser.parsear(f)
    assert len(paragrafos) == 1
    # NFC composed form: "caf" + precomposed e-acute (U+00E9)
    assert "caf\u00e9" in paragrafos[0].texto
    # Inverse check: combining acute MUST NOT survive NFC
    assert "\u0301" not in paragrafos[0].texto
```

**Critical:** uses `f.write_bytes(src.encode("utf-8"))` NOT `f.write_text` — `write_text` may silently re-normalize on some filesystems. The assertion `"\u0301" not in paragrafos[0].texto` is the load-bearing inverse check that pins CORE-11 (Pitfall 4 mitigation).

**Test 4 — D-26.4: footnote separação + linkage** (RESEARCH.md lines 1078-1098):

Pins D-14 + D-15 + D-16: `[^1]` stays embedded in body paragraph's `texto`; `[^1]: corpo` becomes separate `Paragrafo(NOTA_RODAPE, ref_nota="1")`; `paragrafo_pai_idx` resolved to body paragraph's index.

**Test 5 — D-26.5: artigo Eólica integration** (RESEARCH.md lines 1101-1132):

Reads `tests/parser/fixtures/eolica_first_30.md`. Asserts (a) first paragraph is TITULO with "Correntes eólicas" in text, (b) heading "## RESUMO" on line 9 is RESUMO/h2, (c) paragraph on line 11 herda RESUMO. Uses `pytest.skip` if fixture missing — keeps test suite green if fixture is being prepared in a different commit.

**Property test — round-trip offset → texto** (RESEARCH.md lines 1140-1160):

```python
def test_round_trip_offset_bytes(tmp_path, parser):
    """Para qualquer Paragrafo, src_bytes[offset:offset+len_bytes]
    deve igual texto.encode('utf-8')."""
    src = (
        "# Title\n\nFirst para with é.\n\nSecond para[^1].\n\n"
        "[^1]: nota com **bold**.\n"
    )
    f = tmp_path / "rt.md"
    f.write_text(src, encoding="utf-8")
    paragrafos = parser.parsear(f)

    raw = f.read_bytes()
    nfc = unicodedata.normalize("NFC", raw.decode("utf-8")).encode("utf-8")

    for p in paragrafos:
        chunk = nfc[p.offset_bytes:p.offset_bytes + p.len_bytes]
        assert chunk.decode("utf-8") == p.texto, (
            f"round-trip falhou para {p.indice}: "
            f"chunk={chunk!r} texto={p.texto!r}"
        )
```

**Why this is THE most important test:** it pins the byte-exact invariant that Phase 5 PatchAplicador depends on. If `chunk.decode("utf-8") != p.texto` for any paragraph, the offsets are off — Phase 5 patches will corrupt the file. This single test catches Pitfall 2, 3, 4, 6 simultaneously.

**Total file shape:** 1 fixture + 5 unit tests + 1 property test = ~150 lines including docstrings.

---

### `tests/parser/fixtures/__init__.py` (package marker)

**Analog:** Phase 1 `tests/__init__.py` — zero-byte file.

**Why:** Same rationale as `tests/parser/__init__.py` — prevents pytest collection ambiguity when fixtures grow. Strictly speaking the `fixtures/` dir doesn't need to be a package (no Python tests inside), but creating a marker keeps `pyproject.toml [tool.pytest.ini_options] testpaths = ["tests"]` (Phase 1 D-14) walking the tree consistently. Cost: 1 empty file.

---

### `tests/parser/fixtures/eolica_first_30.md` (test fixture)

**Analog:** verbatim copy of the first ~30 lines of `Artigos/Professora Gina Pompeu/Energia Eólica Nordeste/artigo_final/artigo.md` (file confirmed present, 102KB, last modified 2026-04-30).

**Generation strategy:** copy lines 1-30 (or until end of `## INTRODUÇÃO`'s first paragraph) of the source artigo, then append the two footnote bodies (`[^a]:` for Gina Pompeu, `[^b]:` for Kalyl Lamarck) so Test 4 (footnote linkage) has real labels to resolve. RESEARCH.md lines 1167-1198 shows the canonical excerpt structure:

```
# Correntes eólicas sobre a (ir)racionalidade ambiental, ...

***Wind currents over the (ir)rationality of the environment, ...***

**GINA VIDAL MARCÍLIO POMPEU**[^a]

**KALYL LAMARCK**[^b]

## RESUMO

Investiga-se se a expansão da energia eólica no Ceará e no Rio Grande do Norte, entre 2004 e 2025, constitui transição energética no sentido da racionalidade ambiental proposta por Leff, ou se reproduz, sob forma renovável, a racionalidade econômica formalizada por Summers. (...truncado para fixture mínima...)

## PALAVRAS-CHAVE

Transição energética; racionalidade ambiental; racismo ambiental; energia eólica; Nordeste brasileiro.

## ABSTRACT
(...)

## KEYWORDS
(...)

## INTRODUÇÃO

(...primeiro parágrafo da introdução...)

[^a]: Doutorado em Direito Constitucional pela Universidade de Fortaleza...
[^b]: Doutorando em Direito Constitucional pelo Programa de Pós-Graduação...
```

**Critical conventions:**
- File MUST be UTF-8 encoded (Phase 1 D-04 + Phase 2 D-18).
- Line numbers in Test 5 assertions (`linha_inicio == 9` for RESUMO heading, `linha_inicio == 11` for resumo paragraph) DEPEND on this exact line layout. Any reformatting (e.g., extra blank lines, different heading levels) breaks Test 5. **Recommendation for planner:** include in the plan an action that creates this fixture and a verify step that runs Test 5 — circular dependency between the test and the fixture is intentional (the fixture pins the line numbers).
- File should NOT be the full 102KB artigo — keep ~30 lines as RESEARCH.md says ("first 30 lines"); fast test suite (D-27 says no benchmark in Phase 2; smoke tests must stay <1s combined).
- Truncations marked `(...)` are deliberate — fixture is minimum needed for D-26.5 assertions, not a complete document.

**Anti-pattern:** do NOT copy the full artigo.md (would inflate test runtime + repo size).

---

## Shared Patterns

### Language convention (PT-BR everywhere)

**Source:** `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` "Idioma: português brasileiro" + Phase 1 PATTERNS.md "Language convention" section.

**Apply to:** every docstring, every `loguru` log message, every test docstring, every error message in this phase.

Examples already in canonical excerpts above:

```python
"""Sub-pacote parser — segmentação de .md/.tex em list[Paragrafo]."""
"""Vocabulário fechado de tipos de seção/parágrafo (D-03)."""
"""Bloco de texto identificável linha a linha (D-02)."""
"""Parser CommonMark + footnotes para biblio_validador."""
logger.info(f"parsear: {path}")
logger.error(f"arquivo não encontrado: {path}")
logger.warning(f"footnote órfã: [^{p.ref_nota}] sem ref localizável em {p.arquivo}")
```

The smoke-test assertions `"Texto simples." == p.texto` and `"Investiga-se" in paragrafos_resumo[0].texto` depend on this convention being applied to test fixtures too — drift to English breaks Test 5.

---

### Style enforcement (inherited from Phase 1)

**Source:** Phase 1 `pyproject.toml` lines 32-51 (verified intact at `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/pyproject.toml`).

**Apply to:** every `.py` file written in Phase 2 — specifically the 5 new `.py` files in `src/biblio_validador/parser/` and `tests/parser/`.

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

Concrete implications for Phase 2 code:
- **Max 80 chars/line** — `markdown.py` `_walk` token branches have several call sites that would exceed 80 chars without vertical break. RESEARCH.md Example 2 already wraps them properly; copy verbatim.
- **Type hints on every signature** — including private helpers (`_walk`, `_build_paragrafo`, `_resolver_pais`, `_classificar_heading`, `_normalizar_heading`, `_construir_linha_offsets`, `_carregar_mapa_secao`). RESEARCH.md Example 2 covers all.
- **PEP 604 union syntax** (`UP` rule): `int | None`, `str | None`, `list[int] | None` — never `Optional[int]`, never `Union[int, None]`, never `List[int]`. RESEARCH.md Example 3 already uses PEP 604 (verified line 974).
- **Import ordering** (`I` rule): stdlib → third-party → local with blank lines. RESEARCH.md Example 2 lines 696-707 already correct.
- **Bugbear** (`B` rule): no mutable default args, no shadowing builtins, no `except Exception:` bare. None apply to Phase 2 code.

---

### Test invocation contract (inherited from Phase 1)

**Source:** Phase 1 PATTERNS.md "Test invocation contract" section.

**Apply to:** running Phase 2 tests during execution.

```bash
uv run pytest tests/parser/ -v               # full Phase 2 suite
uv run pytest tests/parser/test_markdown.py::test_round_trip_offset_bytes -x  # single property test
```

Always `uv run pytest`, never bare `pytest`. Phase 1 D-14 set `testpaths = ["tests"]`, so `uv run pytest` discovers Phase 1 + Phase 2 tests in one invocation. **Phase 2 verify step should run ALL tests** (not just `tests/parser/`) to confirm Phase 2 didn't regress Phase 1's `tests/test_cli.py` (3 smoke tests).

---

### Logging configuration (Phase 2 first consumer)

**Source:** CONTEXT.md D-19 (Phase 1 deferred logger config) + D-25 (`from loguru import logger` in `markdown.py`).

**Apply to:** `markdown.py` only. `types.py` is data-only (no logger needed). `__init__.py` is re-export (no logger needed).

**Pattern:**

```python
from loguru import logger

# In ParserMd methods:
logger.info(f"parsear: {path}")
logger.info(f"parsear: {len(paragrafos)} parágrafos")
logger.error(f"arquivo não encontrado: {path}")
logger.error(f"encoding inválido em {path}")
logger.info(f"source NFD detectado, convertido para NFC: {path}")
logger.warning(f"footnote órfã: [^{p.ref_nota}] sem ref localizável em {p.arquivo}")
```

**Critical** (loguru convention, NOT stdlib logging):
- Use `from loguru import logger` — single global logger; no `logging.getLogger(__name__)`.
- Do NOT call `logger.add(...)` in `markdown.py` — that's the orchestrator's job (Phase 8+). Phase 2 just emits; default loguru handler writes to stderr with INFO level, which is sufficient for tests.
- f-strings for interpolation — loguru's default formatter handles them; no `%s`/`{}.format()`.

---

## No Analog Found

(none — every file has either a Phase 1 in-repo analog for style or a RESEARCH.md empirically-verified reference snippet for shape. Where a file needs both, both are cited above.)

## Pitfall Cross-Reference (for planner action gates)

| Pitfall | Severity | Affected file | Mitigation embedded in pattern excerpts above |
|---------|----------|---------------|------------------------------------------------|
| #1 `paragraph_open` inside `footnote_open` herda offset errado | ALTA | `markdown.py` (`_walk`) | `in_footnote: str \| None` state + emit on inner `paragraph_open` not on `footnote_open` (RESEARCH.md line 513 + canonical `_walk` excerpt) |
| #2 Off-by-one half-open → 1-based inclusive | ALTA | `markdown.py` (`_build_paragrafo`) | Tabulated comment `linha_inicio = map[0] + 1; linha_fim = map[1]` + Test 1 asserts `linha_inicio == linha_fim == 1` |
| #3 Trailing newline em `texto` e `len_bytes` | MÉDIA | `markdown.py` (`_build_paragrafo`) | `chunk = src_bytes[offset:end].rstrip(b"\n")` + Test 1 asserts `p.texto == "Texto simples."` (no `\n`) |
| #4 Arquivo NFD (macOS) | MÉDIA | `markdown.py` (`parsear` order) | `unicodedata.normalize("NFC", text)` BEFORE `encode("utf-8")` BEFORE `linha_offsets` + Test 3 asserts NFC + log INFO when NFD detected |
| #5 Empty/whitespace file | BAIXA | `markdown.py` (`parsear`) | `if not text_nfc.strip(): return []` (D-19) — no exception |
| #6 BOM offset shift | MÉDIA | `markdown.py` (`parsear`) | `if text.startswith("\ufeff"): text = text[1:]` BEFORE NFC (RESEARCH.md line 595 fixed order) |
| #7 List item duplicates | MÉDIA | `markdown.py` (`_walk`) | Walker only emits for `paragraph_open` / `heading_open` / `fence`; ignores `bullet_list_open` / `list_item_open` / `blockquote_open` |
| #8 mypy strict on `Token.map: list[int] \| None` | BAIXA | `markdown.py` (`_build_paragrafo`) | `assert token.map is not None` narrows type |
| Property regression | n/a (cross-cutting) | `tests/parser/test_markdown.py` | Property test `test_round_trip_offset_bytes` catches #2, #3, #4, #6 simultaneously |

## Sequenced Action Pattern (canonical execution order)

The planner should sequence Phase 2 tasks in this order to avoid forward references during execution:

1. **Create `tests/parser/__init__.py`** (empty) and `tests/parser/fixtures/__init__.py` (empty).
2. **Create `tests/parser/fixtures/eolica_first_30.md`** by copying lines 1-~30 of `Artigos/Professora Gina Pompeu/Energia Eólica Nordeste/artigo_final/artigo.md` + appending the two footnote definitions (`[^a]:` and `[^b]:`).
3. **Create `src/biblio_validador/parser/types.py`** (RESEARCH.md Example 3 verbatim) — has zero internal dependencies.
4. **Create `src/biblio_validador/parser/markdown.py`** (RESEARCH.md Example 2 verbatim, with the type-narrowing assert added per Pitfall 8).
5. **Create `src/biblio_validador/parser/__init__.py`** with the 4-line re-export shape (D-22).
6. **Create `tests/parser/test_markdown.py`** (RESEARCH.md Test Strategy section) — depends on all of the above.
7. **Run `uv run pytest tests/ -v`** — must show 3 (Phase 1) + 6 (Phase 2: 5 unit + 1 property) = 9 passed.
8. **Run `uv run ruff check . && uv run ruff format --check .`** — exit 0 (style gate, Phase 1 D-12).
9. **Run `uv run mypy src/`** — exit 0, `Success: no issues found in 5 source files` (Phase 1 D-13; the 5 files are `__init__.py`, `cli.py`, `parser/__init__.py`, `parser/types.py`, `parser/markdown.py`).

Steps 3-4 can swap order if `markdown.py` is written with `from biblio_validador.parser.types import ...` — mypy/ruff don't care which file is created first as long as both exist before step 6.

## Metadata

**Analog search scope:** repo `src/biblio_validador/` (3 .py files), `tests/` (2 .py files), `.planning/phases/01-bootstrap/01-PATTERNS.md` (Phase 1 conventions), `.planning/phases/02-parser-markdown/02-RESEARCH.md` (lines 636-1198 of reference snippets and test strategy), `Artigos/Professora Gina Pompeu/Energia Eólica Nordeste/artigo_final/artigo.md` (fixture source).
**Files scanned:** 5 Phase 1 .py files (read in full), 2 Phase 1 planning docs (PATTERNS.md + 01-01-PLAN.md), 1 Phase 2 CONTEXT.md (read in full), 1 Phase 2 RESEARCH.md (read sections 1-1198 covering all canonical excerpts).
**Pattern extraction date:** 2026-05-05
**Confidence:** HIGH — RESEARCH.md reference snippets are empirically verified (line 5 declares HIGH confidence; line 224 confirms `markdown_it.__version__ == 4.0.0` empirically). Phase 1 style analogs are read directly from the live scaffold files. The only file without an in-repo or sandbox-verified analog is `tests/parser/fixtures/eolica_first_30.md`, but the source artigo exists at the path RESEARCH.md cites and the line-number assertions in Test 5 (`linha_inicio == 9` for RESUMO heading, `linha_inicio == 11` for first resumo paragraph) constrain the fixture's exact shape.
