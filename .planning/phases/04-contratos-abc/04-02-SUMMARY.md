---
phase: 04-contratos-abc
plan: 02
subsystem: core/contracts
tags: [abc, contracts, validador, fixer, dataclasses, mypy-strict]
requires:
  - core/dataclasses.py (Phase 3)  -- Patch, Violacao
  - core/enums.py (Phase 3)        -- Severidade, EstadoPatch
  - parser/types.py (Phase 2)      -- Paragrafo
provides:
  - core/enums.py::Scope           -- PARAGRAFO/SECAO/DOCUMENTO
  - core/enums.py::ModoFixer       -- AUTO/ASSISTIDO/LLM
  - core/contracts.py::ValidadorBase    -- ABC com 2 abstractmethods (CORE-04)
  - core/contracts.py::FixerBase        -- ABC com 2 abstractmethods + 1 concrete (CORE-05)
  - core/contracts.py::AplicacaoResultado  -- frozen+slots dataclass (D-25)
  - core/contracts.py::ContextoFixer       -- frozen+slots+eq=False dataclass (D-26)
  - core/contracts.py::_canonical_root         -- helper (D-09)
  - core/contracts.py::_carregar_json_simples  -- helper (D-21)
affects:
  - core/__init__.py    -- Plan 04-03 vai re-exportar 8 simbolos
  - tests/core/         -- Plan 04-03 vai escrever testes
tech-stack:
  added: []  # Sem novas dependencias — toda stdlib
  patterns:
    - "ABC + @abstractmethod (NAO Protocol) — D-05 + RESEARCH Pattern 1"
    - "ClassVar em todos os atributos de classe — D-08"
    - "Decorator order @classmethod ACIMA de @abstractmethod — empiricamente verificado"
    - "frozen+slots+eq=False quando dataclass tem campo Mapping — RESEARCH Pitfall 4"
    - "from __future__ import annotations — D-28"
    - "Cache class-level via cls.__dict__.get (documentado em docstring) — Pitfall 2"
key-files:
  created:
    - src/biblio_validador/core/contracts.py    # 277 linhas
  modified:
    - src/biblio_validador/core/enums.py        # +34 linhas (de 52 -> 86)
decisions:
  - "Decorator order: @classmethod ABOVE @abstractmethod (RESEARCH Pattern 1, empiricamente verificado em Python 3.13.13)"
  - "ContextoFixer obriga eq=False — sem isso, frozen+slots gera __hash__ que tenta hashear Mapping (dict unhashable) -> TypeError (RESEARCH Pitfall 4)"
  - "Cache cls.__dict__.get documentado em docstring de ValidadorBase em vez de implementado na ABC — D-21 mantem carregar_regras como abstract e Pitfall 2 evita compartilhamento entre subclasses via MRO"
  - "Helpers _canonical_root + _carregar_json_simples ficam no modulo (nao na ABC) — escopo flexivel para validadores concretos M2+"
  - "Imports staged com noqa F401 em T-04-02-02 e progressivamente liberados em T-04-02-03/04 — necessario para satisfazer ruff em cada gate de aceitacao do plano"
metrics:
  duration_min: 5
  tasks_completed: 4
  files_changed: 2
  lines_added: 311
  completed: "2026-05-05T19:19:00Z"
---

# Phase 4 Plan 2: Contratos ABC (Production Code) Summary

**One-liner:** ValidadorBase + FixerBase ABCs com helpers de regex compilation, dataclasses ContextoFixer/AplicacaoResultado e enums Scope/ModoFixer, todos com mypy strict + ruff clean.

## Outcome

Phase 4 entregou os contratos abstratos que validadores concretos (M2-M4) e
fixers concretos (M5-M7) implementarão a partir da Phase 6+. O plano cobriu
exclusivamente código de produção; testes correspondentes ficam em Plan 04-03.

`core/enums.py` cresceu de 2 enums (Severidade, EstadoPatch — Phase 3) para
4 enums (+ Scope, + ModoFixer). `core/contracts.py` foi criado do zero com
4 classes (2 ABCs + 2 dataclasses) e 2 helpers de módulo, totalizando 277
linhas.

Os três pitfalls críticos identificados no RESEARCH foram implementados
exatamente como recomendado, e cada um foi verificado empiricamente:

1. **Decorator order**: `@classmethod` aparece ACIMA de `@abstractmethod`
   em `carregar_regras`. Inverter a ordem quebra em tempo de definição da
   classe com `AttributeError: attribute '__isabstractmethod__' of
   'classmethod' objects is not writable`.
2. **`eq=False` em `ContextoFixer`**: o campo `regras_compiladas:
   Mapping[str, re.Pattern[str]]` é dict no runtime e dict é unhashable.
   `frozen=True + slots=True + eq=True` (default) gera `__hash__` que
   tenta hashear o dict → `TypeError`. `eq=False` suprime a geração de
   `__eq__` / `__hash__`.
3. **Cache class-level via `cls.__dict__.get`**: a docstring de
   `ValidadorBase` documenta o pattern correto para subclasses, evitando
   o uso ingênuo `getattr(cls, '_regras_compiladas')` que faria traversal
   de MRO e compartilharia cache entre subclasses.

## Requirements Coverage

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| CORE-04 | ABC `ValidadorBase` com `JSON_SOURCE`, `SCOPE`, `carregar_regras()`, `validar(paragrafos) -> list[Violacao]` | ✓ | `class ValidadorBase(ABC)` em contracts.py com 2 ClassVar + 1 ClassVar nullable + 2 @abstractmethod (carregar_regras como classmethod abstract, validar como instance abstract). TypeError em instanciação verificado. |
| CORE-05 | ABC `FixerBase` com `VIOLACAO_IDS`, `MODO`, `pode_corrigir(v)`, `propor_patches(v, contexto) -> list[Patch]`, `aplicar(patches, modo_interativo)` | ✓ | `class FixerBase(ABC)` em contracts.py com 2 ClassVar + 1 método concreto (`pode_corrigir`) + 2 @abstractmethod (`propor_patches`, `aplicar`). TypeError em instanciação verificado. |

## Tasks Executed

| Task | Title | Commit | Outcome |
|------|-------|--------|---------|
| T-04-02-01 | Estender enums.py com Scope + ModoFixer | `aa178d1` | 34 linhas, 2 novos enums sem regredir Severidade/EstadoPatch |
| T-04-02-02 | Criar contracts.py com helpers | `1d739cc` | 104 linhas iniciais, _canonical_root + _carregar_json_simples; verificado contra JSON real `04_construcoes_sintaticas_proibidas.json` (compila 12 cst_* rules) |
| T-04-02-03 | Adicionar ValidadorBase ABC | `bf71f51` | +63 linhas, decorator order verificado, TypeError em instanciação verificado |
| T-04-02-04 | Adicionar AplicacaoResultado, ContextoFixer (eq=False), FixerBase | `0de9e68` | +110 linhas, 3 blocos em ordem (AplicacaoResultado → ContextoFixer → FixerBase), todos os imports liberados de noqa F401 |

## Verification Results

Plan-level final verification (CONTEXT.md success criteria):

```text
$ uv run python -c "from biblio_validador.core.contracts import (
    ValidadorBase, FixerBase, AplicacaoResultado, ContextoFixer,
    _canonical_root, _carregar_json_simples,
); from biblio_validador.core.enums import (
    Severidade, EstadoPatch, Scope, ModoFixer,
); from biblio_validador.core.dataclasses import Violacao, Patch;
print('all 12 symbols importable from core/')"
all 12 symbols importable from core/

$ uv run pytest tests/core/test_dataclasses.py -x
25 passed in 0.05s

$ uv run mypy --strict src/biblio_validador/core/
Success: no issues found in 4 source files

$ uv run ruff check src/biblio_validador/core/
All checks passed!
```

- Phase 3 tests (25 testes em `test_dataclasses.py`) continuam passando
  — sem regressão.
- mypy strict clean nos 4 arquivos de `core/` (`__init__.py`, `dataclasses.py`,
  `enums.py`, `contracts.py`).
- ruff clean em todo `core/`.
- 12 símbolos importáveis pela superfície que Plan 03 usará via `core/__init__.py`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Imports stage required noqa F401 markers entre tasks**

- **Found during:** T-04-02-02
- **Issue:** O `<action>` de T-04-02-02 inclui imports completos
  (`ABC`, `abstractmethod`, `dataclass`, `ClassVar`, `Patch`, `Violacao`,
  `ModoFixer`, `Scope`, `Paragrafo`) que só são usados em T-04-02-03 e
  T-04-02-04. Mas a acceptance criterion de T-04-02-02 (`uv run ruff
  check src/biblio_validador/core/contracts.py exits 0`) não tolera
  `F401 imported but unused`.
- **Fix:** Adicionei `# noqa: F401` aos imports não-usados naquele momento,
  com comentário indicando em qual task posterior eles são consumidos.
  T-04-02-03 removeu F401 dos imports que aquela task usa (ABC,
  abstractmethod, ClassVar, Violacao, Scope, Paragrafo). T-04-02-04
  removeu F401 dos restantes (dataclass, Patch, ModoFixer). Estado final
  do arquivo: zero comentários `noqa: F401`.
- **Files modified:** `src/biblio_validador/core/contracts.py`
- **Commits:** `1d739cc` (adicionou noqa), `bf71f51` (removeu parte),
  `0de9e68` (removeu o resto)

**2. [Rule 1 — Bug] Linha 39 do exemplo na docstring de `_canonical_root` excedia 80 chars**

- **Found during:** T-04-02-02 ruff check
- **Issue:** A docstring incluía o caminho completo
  `"02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json"`
  em uma única linha (84 chars > 80).
- **Fix:** Quebrei em duas Path operands:
  ```python
  / "02_escrita/termos_proibidos"
  / "04_construcoes_sintaticas_proibidas.json"
  ```
  Comportamento idêntico em runtime (Path supports chained `/`).
- **Files modified:** `src/biblio_validador/core/contracts.py`
- **Commit:** absorvido em `1d739cc`

**3. [Rule 1 — Bug] Linha 159 do docstring de `validar` excedia 80 chars**

- **Found during:** T-04-02-03 ruff check
- **Issue:** `"""Detecta violacoes de regra canonica em uma lista de
  paragrafos (D-11)."""` totalizava 81 chars.
- **Fix:** Substituí "em uma lista de" por "numa lista de" para chegar
  a 80 chars. Sem mudança semântica.
- **Files modified:** `src/biblio_validador/core/contracts.py`
- **Commit:** absorvido em `bf71f51`

### Architectural changes

Nenhuma — todo o plano foi executado conforme spec.

### Authentication gates

Nenhuma — plano sem dependência de credenciais ou rede.

## Threat Surface Status

Threat model do plan-04-02 é LOW para todos os itens:

- **T-04-01 (LOW)** — JSON em `JSON_SOURCE` sob controle do repo. ✓
  `_carregar_json_simples` propaga `FileNotFoundError`,
  `json.JSONDecodeError`, `re.error` sem silenciar (D-22). A `re.error`
  ganha `regra {rid}: ...` antes da mensagem original para diagnóstico.
- **T-04-02 (LOW)** — Regex DoS por backtracking catastrófico. Phase 4
  só compila; validators concretos (M2+) escolhem patterns. Out of
  scope confirmado.

Nenhuma surface nova introduzida fora do escopo do threat model.

## Known Stubs

Nenhum stub. Todos os métodos abstratos estão marcados como tal
(`@abstractmethod`); subclasses concretas (M2+) devem implementar.
A docstring de `ValidadorBase` documenta o pattern de cache que
subclasses devem usar — não é stub, é guia para implementação.

## Integration Notes for Plan 04-03

Plan 04-03 (testes + `core/__init__.py`) pode agora:

1. Importar todos os 6 novos símbolos via:
   ```python
   from biblio_validador.core.contracts import (
       ValidadorBase, FixerBase, AplicacaoResultado, ContextoFixer,
   )
   from biblio_validador.core.enums import Scope, ModoFixer
   ```
2. Usar `_canonical_root()` e `_carregar_json_simples()` como helpers
   internos (leading underscore — exportar opcional, atualmente NÃO
   exportados pelo `__all__` planejado).
3. Atualizar `core/__init__.py` para re-exportar 8 símbolos canônicos
   (Phase 3 + Phase 4) em ordem alfabética dentro de `__all__`:
   `["AplicacaoResultado", "ContextoFixer", "EstadoPatch", "FixerBase",
   "ModoFixer", "Patch", "Scope", "Severidade", "ValidadorBase",
   "Violacao"]` — 10 itens, na verdade.
4. Rodar testes contra fixtures `tests/core/fixtures/regras_fake.json`
   gerados pelo Plan 04-01.

## Self-Check: PASSED

- File `src/biblio_validador/core/enums.py`: FOUND
- File `src/biblio_validador/core/contracts.py`: FOUND
- Commit `aa178d1`: FOUND
- Commit `1d739cc`: FOUND
- Commit `bf71f51`: FOUND
- Commit `0de9e68`: FOUND
- Phase 3 tests still pass: VERIFIED (25/25)
- mypy --strict src/biblio_validador/core/: clean
- ruff check src/biblio_validador/core/: clean
- 12 symbols importable from core/: VERIFIED
