---
phase: 2
slug: parser-markdown
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-05
updated: 2026-05-05
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + pytest-cov 7.1.0 (instalado em Phase 1 via `[dependency-groups].dev`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `addopts = "--tb=short"`) |
| **Quick run command** | `uv run pytest tests/parser/ -x` |
| **Full suite command** | `uv run pytest --cov=biblio_validador.parser --cov-report=term-missing` |
| **Estimated runtime** | < 2 segundos (full); < 1s (quick) |

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/parser/ -x`
- **After every plan wave:** `uv run pytest --cov=biblio_validador.parser --cov-report=term-missing`
- **Before `/gsd-verify-work`:** Full suite green + coverage >= 90% no módulo `parser/` + `mypy --strict` verde
- **Max feedback latency:** 2 segundos

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-T1 | 01 | 1 | CORE-01, CORE-11 | T-02-01..08 | UTF-8 strict, NFC source-único, walker iterativo | scaffold | `test -f src/biblio_validador/parser/__init__.py && test -f src/biblio_validador/parser/types.py && test -f src/biblio_validador/parser/markdown.py && test -f tests/parser/__init__.py && test -f tests/parser/fixtures/__init__.py && test -f tests/parser/fixtures/eolica_first_30.md` | ❌ W0 | ⬜ pending |
| 02-01-T2.1 | 01 | 1 | CORE-01 | T-02-05 | walker iterativo (sem stack overflow) | unit | `uv run pytest tests/parser/test_markdown.py::test_paragrafo_simples_um_so_paragrafo -x` | ❌ W0 | ⬜ pending |
| 02-01-T2.2 | 01 | 1 | CORE-01 | T-02-07 | exact-match em `_normalizar_heading` | unit | `uv run pytest tests/parser/test_markdown.py::test_heading_classificacao_e_heranca -x` | ❌ W0 | ⬜ pending |
| 02-01-T2.3 | 01 | 1 | CORE-11 | T-02-06 | NFC source-único | unit | `uv run pytest tests/parser/test_markdown.py::test_normalizacao_nfc -x` | ❌ W0 | ⬜ pending |
| 02-01-T2.4 | 01 | 1 | CORE-01 | — | first-occurrence wins | unit | `uv run pytest tests/parser/test_markdown.py::test_footnote_separa_e_linka -x` | ❌ W0 | ⬜ pending |
| 02-01-T2.5 | 01 | 1 | CORE-01 | T-02-06 | round-trip offset/texto idempotente | property | `uv run pytest tests/parser/test_markdown.py::test_round_trip_offset_bytes -x` | ❌ W0 | ⬜ pending |
| 02-01-T2.6 | 01 | 1 | CORE-01 | — | linha-a-linha sobre artigo real | integration | `uv run pytest tests/parser/test_markdown.py::test_artigo_eolica_excerpt -x` | ❌ W0 | ⬜ pending |
| 02-01-T3.1 | 01 | 1 | — | — | coverage gate | gate | `uv run pytest --cov=biblio_validador.parser --cov-fail-under=90` | ❌ W0 | ⬜ pending |
| 02-01-T3.2 | 01 | 1 | — | — | type safety gate | gate | `uv run mypy --strict src/biblio_validador/parser` | ❌ W0 | ⬜ pending |
| 02-01-T3.3 | 01 | 1 | — | — | style gate | gate | `uv run ruff check src/biblio_validador/parser tests/parser && uv run ruff format --check src/biblio_validador/parser tests/parser` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs mapeados ao `02-01-PLAN.md` (Task 1 = scaffold, Task 2 = 6 testes, Task 3 = 3 gates phase-level). A coluna `File Exists` permanece ❌ W0 até a execução criar os arquivos do módulo `parser/`.*

---

## Wave 0 Requirements

- [ ] `src/biblio_validador/parser/__init__.py` — pacote re-exporta `ParserMd`, `Paragrafo`, `TipoSecao`
- [ ] `src/biblio_validador/parser/types.py` — `Paragrafo` (frozen, slots) + `TipoSecao` (Enum) — D-02, D-03
- [ ] `src/biblio_validador/parser/markdown.py` — `ParserMd` classe — D-21
- [ ] `tests/parser/__init__.py` — marker de pacote pytest
- [ ] `tests/parser/test_markdown.py` — 6 testes (5 D-26 unit/integration + 1 property round-trip)
- [ ] `tests/parser/fixtures/__init__.py` — marker
- [ ] `tests/parser/fixtures/eolica_first_30.md` — primeiras ~50 linhas verbatim do artigo Eólica real (heading h1 + autores + RESUMO + PALAVRAS-CHAVE + ABSTRACT + KEYWORDS + INTRODUÇÃO + 2 footnotes `[^a]` `[^b]`)

Framework já instalado em Phase 1 — não há comandos de install adicionais.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Inspeção visual de log `loguru` em DEBUG | — | Garantir que mensagens estão claras (D-25) é avaliação humana de prosa | `uv run python -c "from biblio_validador.parser import ParserMd; from loguru import logger; import sys; logger.remove(); logger.add(sys.stderr, level='DEBUG'); ParserMd().parsear('tests/parser/fixtures/eolica_first_30.md')"` — checar que cada bloco tokenizado emite linha legível |

*Apenas 1 verificação manual; todo comportamento funcional tem teste automatizado.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (10/10 mapped above; T1 is the W0 dependency)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (T2.1..T2.6 all unit/property/integration; T3.1..T3.3 phase-level gates)
- [x] Wave 0 covers all MISSING references (T1 cria os 7 arquivos da §"Wave 0 Requirements")
- [x] No watch-mode flags (commands são one-shot: `pytest -x`, `mypy --strict`, `ruff check`)
- [x] Feedback latency < 2s (full suite verified at < 2s on Eólica fixture per RESEARCH.md §"Performance Notes")
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-05-05
