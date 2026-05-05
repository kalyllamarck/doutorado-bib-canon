---
phase: 2
slug: parser-markdown
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-05
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
| 02-XX-01 | TBD | 0 | — | — | N/A | scaffold | `test -f tests/parser/__init__.py && test -f tests/parser/fixtures/eolica_first_30.md` | ❌ W0 | ⬜ pending |
| 02-XX-02 | TBD | 1 | CORE-01 | — | N/A | unit | `uv run pytest tests/parser/test_markdown.py::test_paragrafo_simples_um_so_paragrafo -x` | ❌ W0 | ⬜ pending |
| 02-XX-03 | TBD | 1 | CORE-01 | — | N/A | unit | `uv run pytest tests/parser/test_markdown.py::test_heading_classificacao_e_heranca -x` | ❌ W0 | ⬜ pending |
| 02-XX-04 | TBD | 1 | CORE-11 | — | N/A | unit | `uv run pytest tests/parser/test_markdown.py::test_normalizacao_nfc -x` | ❌ W0 | ⬜ pending |
| 02-XX-05 | TBD | 1 | CORE-01 | — | N/A | unit | `uv run pytest tests/parser/test_markdown.py::test_footnote_separa_e_linka -x` | ❌ W0 | ⬜ pending |
| 02-XX-06 | TBD | 1 | CORE-01 | — | N/A | property | `uv run pytest tests/parser/test_markdown.py::test_round_trip_offset_bytes -x` | ❌ W0 | ⬜ pending |
| 02-XX-07 | TBD | 1 | CORE-01 | — | N/A | integration | `uv run pytest tests/parser/test_markdown.py::test_artigo_eolica_excerpt -x` | ❌ W0 | ⬜ pending |
| 02-XX-08 | TBD | 1 | — | — | N/A | gate | `uv run pytest --cov=biblio_validador.parser --cov-fail-under=90` | ❌ W0 | ⬜ pending |
| 02-XX-09 | TBD | 1 | — | — | N/A | gate | `uv run mypy src/biblio_validador/parser` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs serão refinados pelo planner. A coluna `File Exists` é ❌ W0 porque o módulo `parser/` ainda não existe.*

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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
