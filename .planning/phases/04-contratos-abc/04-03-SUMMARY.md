---
phase: 04-contratos-abc
plan: 03
subsystem: core/tests
tags: [tests, contracts, abc, re-export, coverage, mypy-strict]
requires:
  - tests/core/fixtures/ (Plan 04-01)         -- 4 fixtures JSON
  - src/biblio_validador/core/contracts.py (Plan 04-02)  -- ABCs + helpers
  - src/biblio_validador/core/enums.py (Plan 04-02)      -- Scope, ModoFixer
  - src/biblio_validador/core/dataclasses.py (Phase 3)   -- Patch, Violacao
  - src/biblio_validador/parser/types.py (Phase 2)       -- Paragrafo, TipoSecao
provides:
  - src/biblio_validador/core/__init__.py        -- 10-symbol public surface
  - tests/core/test_contracts.py                 -- 15 tests for CORE-04 + CORE-05
  - .planning/phases/04-contratos-abc/04-VALIDATION.md  -- approved 2026-05-05
affects:
  - tests/core/test_dataclasses.py  -- Phase 3 test updated (Rule 1: __all__ subset)
tech-stack:
  added: []
  patterns:
    - "noqa: F401 imports staged across tasks (Plan 04-02 pattern reused)"
    - "ClassVar[Path]/[Scope]/[frozenset[str]]/[ModoFixer] em subclasses concretas"
    - "cls.__dict__.get cache pattern em _ValidadorComCache (Pitfall 2 mitigation)"
    - "_make_violacao(**overrides) + _make_paragrafo() builders (Phase 3 D-26 carried)"
    - "with pytest.raises(TypeError, match='abstract') para contract violation tests"
    - "issubset() em assertions de re-export (forward-compatible com phases futuras)"
key-files:
  created:
    - tests/core/test_contracts.py        # 369 linhas, 15 testes
    - .planning/phases/04-contratos-abc/04-03-SUMMARY.md
  modified:
    - src/biblio_validador/core/__init__.py     # 7 -> 33 linhas (4 -> 10 symbols)
    - tests/core/test_dataclasses.py            # subset() em test_aux_imports_via_re_export_funcionam
    - .planning/phases/04-contratos-abc/04-VALIDATION.md  # frontmatter sign-off
decisions:
  - "Test-staging com noqa F401 reusado de Plan 04-02 (T-04-03-02 mantém imports de json/ClassVar/FrozenInstanceError/EstadoPatch que serão usados em T-04-03-03/04)"
  - "Rule 1 fix em test_aux_imports_via_re_export_funcionam: assertion strict-equality contra os 4 símbolos da Phase 3 atualizada para issubset() — Phase 4 expandiu __all__ de 4 para 10, mas o contrato Phase 3 (4 símbolos re-exportados) permanece preservado"
  - "Long lines (E501) reflowadas em docstrings/comentários para satisfazer 80 cols/linha do CLAUDE.md (Rule 3 deviation, mantém semântica)"
  - "_FixerCompleto sem cobertura específica do branch fixer.pode_corrigir vazio porque o teste já garante o caminho True/False — coverage 99.49% comprova"
  - "test_contexto_fixer_eq_false_unhashable_safe não chama hash(ctx) explicitamente — eq=False com frozen=True pode dar __hash__ id-based herdado de object que NÃO levanta TypeError; o contrato testado é apenas a instanciação bem-sucedida com Mapping field, evidência primária de Pitfall 4 mitigado"
metrics:
  duration_min: 7
  tasks_completed: 5
  files_changed: 4
  lines_added: ~140
  completed: "2026-05-05T19:31:30Z"
---

# Phase 4 Plan 3: Contratos ABC (Tests + Re-export) Summary

**One-liner:** 15 testes para CORE-04 + CORE-05 cobrindo os 4 success criteria do roadmap, re-export de 10 símbolos públicos em `core/__init__.py`, e 4 gates finais (mypy strict, ruff, pytest, coverage 99.49%) verdes — Phase 4 fechada.

## Outcome

Phase 4 está completa. O Plan 03 (Wave 2) entregou:

1. **Re-export expandido**: `src/biblio_validador/core/__init__.py` cresceu de 4 para 10 símbolos (alfabéticos em `__all__`), unificando o ponto de entrada público para Phase 3 (Violacao, Patch, EstadoPatch, Severidade) + Phase 4 (ValidadorBase, FixerBase, AplicacaoResultado, ContextoFixer, Scope, ModoFixer).

2. **Suite de contratos**: `tests/core/test_contracts.py` com 369 linhas e 15 testes cobrindo todos os 4 success criteria do roadmap Phase 4:

   | # | Success Criterion | Tests |
   |---|-------------------|-------|
   | 1 | TypeError em subclasse incompleta | `test_validador_base_abstract_validar`, `test_validador_base_abstract_carregar_regras`, `test_fixer_base_abstract_propor_patches`, `test_fixer_base_abstract_aplicar` (4) |
   | 2 | `carregar_regras` compila regex 1x | `test_carregar_regras_cache_hit`, `test_carregar_regras_per_subclass_isolation` (2) |
   | 3 | `pode_corrigir` retorna False fora de VIOLACAO_IDS | `test_pode_corrigir_returns_true_for_known_id`, `test_pode_corrigir_returns_false_for_unknown_id` (2) |
   | 4 | Testes unitários passam | toda a suite + os 6 testes adicionais para erros e dataclasses auxiliares |

   Os outros 7 testes cobrem error paths (`FileNotFoundError`, `json.JSONDecodeError`, `re.error`), schema heterogêneo (str/list/alt-key + skip-branch), `AplicacaoResultado` frozen+slots, `ContextoFixer` eq=False (Pitfall 4 mitigation evidence) e re-export smoke.

3. **Gates finais verdes**:
   - `uv run mypy --strict src/biblio_validador/core/` — 4 source files clean
   - `uv run ruff check src/biblio_validador/core/ tests/core/` — clean
   - `uv run pytest tests/core/` — 40 passed (15 contracts + 25 dataclasses)
   - `uv run pytest tests/core/ --cov=biblio_validador.core --cov-fail-under=95` — coverage = **99.49%** (gate exigia 95%)

4. **VALIDATION.md sign-off**: frontmatter atualizado para `status: green`, `nyquist_compliant: true`, `wave_0_complete: true`, `Approval: approved 2026-05-05`.

## Task Trail

| Task | Hash | Description |
|------|------|-------------|
| T-04-03-01 | `2ed65fe` | Re-export 10 symbols alphabetically from core/__init__.py |
| T-04-03-02 | `8cdf535` | Create test_contracts.py with helpers + 4 abstract tests |
| T-04-03-03 | `8b1831c` | Add carregar_regras tests (cache + isolation + 3 errors + normalize) |
| T-04-03-04 | `fe7fa34` | Add pode_corrigir + frozen + eq=False + smoke (15 total) |
| T-04-03-05 | `a8c2ae6` | Final gates green + VALIDATION.md sign-off |

## Coverage Report

```
Name                                       Stmts   Miss Branch BrPart  Cover
----------------------------------------------------------------------------
src/biblio_validador/core/__init__.py          4      0      0      0   100%
src/biblio_validador/core/contracts.py        58      1      6      0    98%
src/biblio_validador/core/dataclasses.py      72      0     34      0   100%
src/biblio_validador/core/enums.py            22      0      0      0   100%
----------------------------------------------------------------------------
TOTAL                                        156      1     40      0    99%
```

A única linha não coberta em `contracts.py` é a docstring de `_canonical_root`'s implementation walk (linha 49); o helper é exercitado indiretamente pelos validators concretos a serem implementados em M2+ (Phase 6+).

## Suite Performance

```
40 passed in 0.13s
```

Tempo total da suite < 1 segundo, bem abaixo do limite de 5s do VALIDATION.md.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] noqa F401 em imports staged**
- **Found during:** T-04-03-02
- **Issue:** Plan código copia 4 imports (json, FrozenInstanceError, ClassVar, EstadoPatch) que só são usados em T-04-03-03/04, mas ruff falha com F401 ao final de T-04-03-02 (acceptance gate exige `ruff check` exit 0).
- **Fix:** Adicionei `# noqa: F401  # used in T-04-03-XX` aos 4 imports. Liberados progressivamente: T-04-03-03 removeu noqa de json/ClassVar; T-04-03-04 removeu de FrozenInstanceError; EstadoPatch permanece staged porque é referenciado apenas como string literal em `assert {...}.issubset()` no smoke test.
- **Pattern:** Já documentado em Plan 04-02 SUMMARY como "Imports staged with noqa F401 in T-04-02-02 and progressively liberated in T-04-02-03/04".
- **Files modified:** tests/core/test_contracts.py
- **Commits:** 8cdf535, 8b1831c, fe7fa34

**2. [Rule 3 - Blocking] Long docstring/comment lines (E501)**
- **Found during:** T-04-03-02 e T-04-03-04
- **Issue:** O caractere em-dash `—` (U+2014) é 1 caractere visualmente mas algumas docstrings ficaram com 81-86 cols. CLAUDE.md exige `<=80 chars/linha`.
- **Fix:** Reflowei 4 linhas de docstring/comentário (substituí em-dash por dois pontos ou reflowei para múltiplas linhas) sem alterar semântica. Não alterou nenhum nome de teste, identificador ou lógica.
- **Files modified:** tests/core/test_contracts.py (4 linhas afetadas)
- **Commits:** 8cdf535, fe7fa34

**3. [Rule 1 - Bug] test_aux_imports_via_re_export_funcionam strict equality**
- **Found during:** T-04-03-05 (gate 3 — full pytest suite)
- **Issue:** Em `tests/core/test_dataclasses.py`, o teste `test_aux_imports_via_re_export_funcionam` asseverava `set(__all__) == {"EstadoPatch", "Patch", "Severidade", "Violacao"}` — válido em Phase 3 quando havia exatamente 4 símbolos. Após T-04-03-01 expandir `__all__` para 10 símbolos (Phase 4), essa assertiva passou a falhar.
- **Fix:** Substituí strict-equality por `issubset()` — o teste agora garante que os 4 símbolos da Phase 3 permanecem re-exportados, sem fazer assertiva sobre símbolos novos. A assertiva forte sobre os 10 símbolos de Phase 4 está em `test_core_reexport_smoke` no novo `test_contracts.py`.
- **Files modified:** tests/core/test_dataclasses.py (1 teste, ~7 linhas)
- **Commit:** a8c2ae6

### Acceptance Criteria Note

- T-04-03-03 acceptance: `grep -c "cls.__dict__.get" tests/core/test_contracts.py == 1`. Atual count = 3 (1× docstring `_ValidadorComCache`, 1× código real, 1× docstring de `test_carregar_regras_per_subclass_isolation`). Todas as 3 ocorrências são exatamente como o plano especificou (copiei verbatim). A regra está corretamente implementada — apenas o grep não distingue uso real de menção em docstring/comentário. Os 6 testes da task passam, e a função real `cls.__dict__.get(...)` aparece exatamente 1 vez no código executável (linha 167). Sem ação corretiva.

### Authentication Gates

Nenhum. Plan 03 é totalmente local (zero rede, zero credentials).

## Threat Surface Scan

Plan 03 introduziu apenas tests + re-export. Não há nova superfície fora do `<threat_model>` original (T-04-01 LOW, T-04-02 LOW). Test fixtures permanecem read-only versionados.

## Known Stubs

Nenhum. Os métodos abstratos da Phase 4 são intencionalmente abstratos (não stubs); subclasses concretas (M2+) implementam. A suite de testes valida o contrato (TypeError em instanciação direta), não simula implementações stub.

## Phase 4 Status: COMPLETE

| Item | Status |
|------|--------|
| CORE-04 (ValidadorBase) | ✅ implementado + 4 testes (abstract+cache+errors+normalize) |
| CORE-05 (FixerBase) | ✅ implementado + 5 testes (abstract+pode_corrigir+frozen+eq=False+smoke) |
| Roadmap success #1 (TypeError) | ✅ 4 testes |
| Roadmap success #2 (cache 1x) | ✅ 1 teste + 1 isolation |
| Roadmap success #3 (pode_corrigir) | ✅ 2 testes |
| Roadmap success #4 (suite + coverage) | ✅ 99.49% > 95% |
| mypy --strict | ✅ 4 source files clean |
| ruff | ✅ src+tests clean |
| Phase 3 sem regressão | ✅ 25/25 testes |

Phase 5 (PatchAplicador) pode começar — consumirá `Patch` (Phase 3) e implementará a semântica que `FixerBase.aplicar()` declara como abstract.

## Self-Check: PASSED

- File `src/biblio_validador/core/__init__.py`: FOUND (33 linhas, 10 símbolos)
- File `tests/core/test_contracts.py`: FOUND (15 testes coletados)
- File `.planning/phases/04-contratos-abc/04-VALIDATION.md`: FOUND (status green)
- Commit `2ed65fe` (T-04-03-01): FOUND
- Commit `8cdf535` (T-04-03-02): FOUND
- Commit `8b1831c` (T-04-03-03): FOUND
- Commit `fe7fa34` (T-04-03-04): FOUND
- Commit `a8c2ae6` (T-04-03-05): FOUND
- 10 imports from biblio_validador.core: VERIFIED
- mypy --strict src/biblio_validador/core/: clean (4 files)
- ruff check src/biblio_validador/core/ tests/core/: clean
- pytest tests/core/: 40 passed (15 contracts + 25 dataclasses)
- coverage biblio_validador.core: 99.49% (>= 95% gate)
- Phase 3 regression: ZERO (25/25 dataclasses tests pass)
- VALIDATION.md frontmatter: status=green, nyquist_compliant=true, wave_0_complete=true, Approval=approved 2026-05-05
