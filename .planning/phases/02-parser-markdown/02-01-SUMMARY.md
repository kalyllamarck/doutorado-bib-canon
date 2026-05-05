---
phase: 02-parser-markdown
plan: 01
subsystem: parser
tags:
  - parser
  - markdown
  - commonmark
  - footnotes
  - unicode-nfc
  - byte-exact-offsets
  - python

requires:
  - phase: 01-bootstrap
    provides: pyproject.toml com markdown-it-py 4.0.0, mdit-py-plugins, loguru, rich, pylatexenc, typer; layout src/biblio_validador/; pytest+pytest-cov+ruff+mypy via uv sync; estilo (line-length 80, ruff E/F/I/UP/B, mypy strict, type hints obrigatórios, docstring PT-BR)
provides:
  - Sub-pacote `biblio_validador.parser` com classe pública `ParserMd`
  - Dataclass `Paragrafo` (frozen+slots, 11 campos D-02) com offsets byte-exact em UTF-8 NFC
  - Enum `TipoSecao` (14 valores D-03 — vocabulário fechado)
  - `ParserMd.parsear(path) -> list[Paragrafo]` com pipeline NFC source-único (read_bytes -> decode utf-8 strict -> BOM strip -> CRLF/LF -> NFC -> encode -> linha_offsets -> markdown-it parse + footnote_plugin -> walk iterativo -> _resolver_pais)
  - 7 helpers privados (`_construir_linha_offsets`, `_carregar_mapa_secao`, `_classificar_heading`, `_normalizar_heading`, `_build_paragrafo`, `_walk`, `_resolver_pais`)
  - Re-export público D-22 `from biblio_validador.parser import ParserMd, Paragrafo, TipoSecao`
  - Fixture canônica `tests/parser/fixtures/eolica_first_30.md` (excerpt verbatim do artigo Eólica Nordeste com numeração calibrada para testes de integração)
  - Invariante byte-exact pinado: `src_bytes_nfc[offset:offset+len_bytes].decode("utf-8") == p.texto` (consumido por Phase 5 PatchAplicador)
  - Estratégia de footnote linkage (first-occurrence-wins via regex `[^label]` sobre texto de parágrafos não-NOTA)
  - Convenção de prefixo footnote: corpo de definição `[^label]: body` é normalizado para `texto = "body"` com `offset_bytes` deslocado para preservar round-trip
affects:
  - 03-dataclasses-core (Violacao espelha shape de linha_inicio/linha_fim/col_inicio/col_fim)
  - 05-patchaplicador (herda invariante byte-exact; D-13 "gravar sempre em NFC" decidido aqui)
  - 06-validador-piloto-cst_012 (primeiro consumidor real de list[Paragrafo])
  - 16-parser-latex (replica padrão de offsets byte-exact via pylatexenc)
  - todas as Phases M2/M3/M4 (validadores consomem Paragrafo)

tech-stack:
  added:
    - markdown-it-py 4.0.0 (parser CommonMark, primeiro uso real após Phase 1 declarar dependência)
    - mdit-py-plugins.footnote (footnote_plugin, primeiro uso real)
    - loguru 0.7.3 (primeiro emissor real de logs no projeto — Phase 8 orchestrator configurará handlers)
  patterns:
    - "Walker iterativo (sem recursão) sobre stream de tokens markdown-it — mitiga DoS por nesting profundo"
    - "Pipeline NFC source-único: NFC ANTES de encode + linha_offsets (D-11/Pitfall 4)"
    - "Conversão half-open → 1-based inclusive: linha_inicio = map[0]+1, linha_fim = map[1] (Pitfall 2)"
    - "Trailing newline stripped do conteúdo mantendo offset_bytes intacto (Pitfall 3)"
    - "BOM U+FEFF strip ANTES de NFC (Pitfall 6) via Python escape `\\ufeff`"
    - "Frozen dataclass updates via `dataclasses.replace` (D-16) — única forma com slots+frozen"
    - "assert token.map is not None para mypy strict narrowing (Pitfall 8)"
    - "Heading normalization: NFKD → strip combining → casefold → strip pontuação → colapsar espaços (D-08)"
    - "Re-export D-22 em sub-pacote __init__.py com __all__ canônico"
    - "test_aux_* convention para coverage de branches edge sem violar set canônico de 6 testes D-26"

key-files:
  created:
    - src/biblio_validador/parser/__init__.py
    - src/biblio_validador/parser/types.py
    - src/biblio_validador/parser/markdown.py
    - tests/parser/__init__.py
    - tests/parser/fixtures/__init__.py
    - tests/parser/fixtures/eolica_first_30.md
    - tests/parser/test_markdown.py
  modified:
    - .gitignore (+.coverage / .coverage.* / coverage.xml)

key-decisions:
  - "Convenção de prefixo footnote: corpo de definição `[^label]: body` é normalizado para `texto = body` com `offset_bytes` deslocado para preservar round-trip byte-exact (resolve inconsistência detectada entre Contract 5 e Contract 7 do plano)"
  - "Tests auxiliares cobertura: 7 testes test_aux_* adicionados após os 6 canônicos D-26; coverage 88% -> 97%"
  - "Linha 274 de markdown.py (logger.warning para footnote órfã) é defensive code não-alcançável via markdown-it-py 4.0.0 (orphan footnote definitions são silenciosamente discartadas pelo footnote_plugin antes de chegarem ao walker)"
  - "Test 4 footnote literal `texto == \"Corpo da nota.\"` é o contrato user-facing correto; parser strip prefixo `[^N]: ` via fast-path no _build_paragrafo, mantendo round-trip"
  - "Test 2 literal corrigido de `\"Parágrafo do resumo\"` para `\"Parágrafo do resumo.\"` (typo de 1 char no plan: texto[:20] de `Parágrafo do resumo.` retorna 20 chars incluindo o ponto final)"

patterns-established:
  - "Sub-pacote canônico: src/biblio_validador/parser/{__init__,types,markdown}.py + tests/parser/{__init__,test_*,fixtures/}"
  - "Dataclass frozen+slots para tipos parser-internal — replicar para Violacao (Phase 3) e Patch (Phase 3)"
  - "Logger emission patterns: info no entry/exit de operação macro, info para conversões silenciosas (NFD->NFC), error antes de re-raise, warning para defensive paths"
  - "test_aux_<nome> convention para coverage gap fill sem expandir set canônico de testes do plano"

requirements-completed:
  - CORE-01
  - CORE-11

duration: 41min
completed: 2026-05-05
---

# Phase 2 Plan 01: Parser Markdown Summary

**Parser CommonMark + footnotes via markdown-it-py 4.0.0 com offsets byte-exact em UTF-8 NFC source-único e segmentação em list[Paragrafo] linha a linha do artigo Eólica Nordeste real**

## Performance

- **Duration:** ~41 min
- **Started:** 2026-05-05T09:06:31Z
- **Completed:** 2026-05-05T09:47:20Z
- **Tasks:** 3
- **Files created:** 7
- **Files modified:** 1 (.gitignore)
- **Test count:** 14 (6 canônicos D-26 + 7 auxiliares + 1 round-trip property)

## Accomplishments

- `ParserMd.parsear(path: Path) -> list[Paragrafo]` segmenta `.md` em parágrafos com `linha_inicio`, `linha_fim`, `offset_bytes`, `len_bytes` byte-exact sobre source UTF-8 NFC (CORE-01 + CORE-11 cobertos integralmente).
- Footnotes `[^label]` corretamente segmentados como `Paragrafo(tipo=NOTA_RODAPE, ref_nota=label)` com linkage `paragrafo_pai_idx` resolvido em pass-2 via regex first-occurrence-wins.
- Invariante byte-exact `src_bytes_nfc[offset:offset+len_bytes].decode("utf-8") == p.texto` provado por property test (Phase 5 PatchAplicador depende deste invariante para aplicar patches sem drift).
- Cobertura 96.89% no módulo parser/ (gate 90% atendido com folga); mypy strict clean em 5 arquivos; ruff check + format clean em 10 arquivos.
- Fixture canônica do artigo Eólica Nordeste (Pompeu/Lamarck) instrumentada com numeração de linha load-bearing (h1 linha 1, ## RESUMO linha 9, parágrafo Investiga-se linha 11) — pin para integração.

## Task Commits

1. **Task 1: Scaffold módulo parser/ + fixture Eólica + types.py + markdown.py + __init__.py** — `6e95549` (feat)
2. **Task 2: Criar tests/parser/test_markdown.py com 6 testes (D-26 + property) + strip prefixo footnote** — `9fc84f1` (test)
3. **Task 3: Nyquist gate — coverage 97%, mypy strict, ruff verde, +7 test_aux_*** — `2de7a32` (chore)

## Files Created/Modified

### Created (7 files)

- `src/biblio_validador/parser/__init__.py` — Re-export público D-22 (`ParserMd`, `Paragrafo`, `TipoSecao`) + `__all__` canônico.
- `src/biblio_validador/parser/types.py` — Dataclass `Paragrafo(frozen=True, slots=True)` com 11 campos (D-02) + Enum `TipoSecao` com 14 valores (D-03). Inline comments documentam semântica de cada campo. PEP 604 unions (`int | None`).
- `src/biblio_validador/parser/markdown.py` — Classe `ParserMd` (D-21) com pipeline canônico de 9 passos (D-09/D-11/D-18/D-19/D-20) e 7 helpers privados. 3 regex compiladas em module-level constants. Logging via loguru (D-25 — primeiro consumidor real). Walker iterativo (mitiga DoS T-02-05).
- `tests/parser/__init__.py` — Marker vazio (Phase 1 D-16 inheritance).
- `tests/parser/fixtures/__init__.py` — Marker vazio (previne pytest collection ambiguity).
- `tests/parser/fixtures/eolica_first_30.md` — Excerpt verbatim do artigo Eólica Nordeste real (Pompeu/Lamarck, primeiras ~10 linhas + 2 footnotes `[^a]`/`[^b]`). Numeração calibrada: linha 1 = h1 título; linha 9 = `## RESUMO`; linha 11 = parágrafo `Investiga-se`.
- `tests/parser/test_markdown.py` — 14 testes total (6 D-26 canônicos + 1 round-trip property + 7 auxiliares para coverage edge branches). Type hints em todas as assinaturas.

### Modified (1 file)

- `.gitignore` — adiciona `.coverage`, `.coverage.*`, `coverage.xml` (output do pytest-cov).

## Decisions Made

1. **Footnote body prefix stripping (Rule 1 — internal plan inconsistency):** Contract 5 (markdown.py) e Contract 7 (test_markdown.py) do plano discordavam sobre se `Paragrafo.texto` de uma `NOTA_RODAPE` deveria conter o prefixo `[^label]: ` ou só o body. O parser implementado faz strip do prefixo via fast-path em `_build_paragrafo`, ajustando `offset_bytes += len(prefixo)` e `len_bytes -= len(prefixo)` para preservar round-trip byte-exact. Esta é a semantic correta para downstream validators (Phase 6+ não querem o prefixo de markdown como surface de validação) e é coerente com o tratamento que markdown-it-py dá ao token inline (cujo `content` já exclui o prefixo).
2. **Test 2 literal correction (Rule 1 — typo no plan):** `tipos[2] == (TipoSecao.RESUMO, None, "Parágrafo do resumo")` ajustado para `"Parágrafo do resumo."` (20 chars com ponto). O slice `texto[:20]` do parágrafo `"Parágrafo do resumo."` (rstripped do `\n`) retorna a string completa incluindo o ponto final.
3. **`test_aux_*` convention para coverage gap:** 7 testes auxiliares adicionados (FileNotFoundError, UnicodeDecodeError, BOM strip, arquivo vazio, heading SECAO desconhecido, fence/código, footnote órfã silent, footnote dup-ref first-occurrence-wins). Coverage subiu 88% → 97% sem violar VALIDATION.md "6 testes canônicos D-26 com nomes exatos".
4. **Defensive code não-alcançável é aceito:** Linha 274 (`logger.warning` para footnote órfã em `_resolver_pais`) é dead code com markdown-it-py 4.0.0 (orphan definitions são descartadas pelo footnote_plugin). Mantido por defesa contra possíveis mudanças de comportamento da lib em versões futuras.
5. **BOM e NFD literais como Python escape sequences:** `"﻿"` e `"́"` em código fonte (não bytes raw) — segue executor guidance "never paste raw NFD text from RESEARCH.md examples into source".

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test 2 literal off-by-one (typo verbatim do plan)**
- **Found during:** Task 2 (rodando os 6 testes contra o parser correto)
- **Issue:** Plan Contract 7 asserta `tipos[2] == (TipoSecao.RESUMO, None, "Parágrafo do resumo")` (19 chars) mas `texto[:20]` retorna `"Parágrafo do resumo."` (20 chars) — typo de 1 char no plan.
- **Fix:** Asserção alterada para `"Parágrafo do resumo."` (com ponto final), refletindo a documentada convenção do parser (raw slice com markup, rstrip apenas de `\n`).
- **Files modified:** tests/parser/test_markdown.py:58
- **Verification:** test_heading_classificacao_e_heranca PASSED.
- **Committed in:** `9fc84f1` (Task 2 commit)

**2. [Rule 1 - Bug] Inconsistência Contract 5 vs Contract 7 sobre Paragrafo.texto de NOTA_RODAPE**
- **Found during:** Task 2 (test_footnote_separa_e_linka inicialmente falhou — parser retornava `"[^1]: Corpo da nota."`, teste esperava `"Corpo da nota."`)
- **Issue:** Contract 5 (markdown.py) não previa stripping do prefixo `[^label]: ` em footnote bodies, mas Contract 7 (test) assertava texto sem prefixo. Internal plan inconsistency.
- **Fix:** Adicionado fast-path em `_build_paragrafo` que detecta `tipo == NOTA_RODAPE and ref_nota is not None`, calcula `prefixo = f"[^{ref_nota}]: ".encode()`, e se `chunk.startswith(prefixo)` ajusta `offset_bytes += len(prefixo)` e `chunk = chunk[len(prefixo):]`. Round-trip byte-exact preservado (verificado via property test test_round_trip_offset_bytes).
- **Files modified:** src/biblio_validador/parser/markdown.py:147-154
- **Verification:** test_footnote_separa_e_linka PASSED + test_round_trip_offset_bytes PASSED (round-trip mantido).
- **Committed in:** `9fc84f1` (Task 2 commit)

**3. [Rule 2 - Missing Critical] Coverage 88% < 90% gate (branches edge ausentes)**
- **Found during:** Task 3 (primeira execução do coverage gate)
- **Issue:** Os 6 testes canônicos D-26 cobriam apenas 88% de `parser/` — branches de erro/edge não exercitados (FileNotFoundError, UnicodeDecodeError, BOM strip, arquivo vazio, heading SECAO desconhecido, fence/código, footnote dup-ref).
- **Fix:** 7 testes `test_aux_*` adicionados conforme convenção autorizada pelo plano (Task 3 step 1: "testes auxiliares para coverage gap são permitidos sob convenção `test_aux_<descrição>`"). Coverage subiu 88% → 96.89%.
- **Files modified:** tests/parser/test_markdown.py:159-269
- **Verification:** `uv run pytest --cov=biblio_validador.parser --cov-fail-under=90` exit 0; coverage 96.89%.
- **Committed in:** `2de7a32` (Task 3 commit)

**4. [Rule 1 - Bug] UP012 ruff lint: `.encode("utf-8")` redundante**
- **Found during:** Task 3 ruff check
- **Issue:** `f"[^{ref_nota}]: ".encode("utf-8")` — argumento `"utf-8"` é o default de `str.encode()` desde Python 3.0; UP012 sinaliza redundância.
- **Fix:** Substituído por `.encode()`.
- **Files modified:** src/biblio_validador/parser/markdown.py:151
- **Verification:** `uv run ruff check .` exit 0; comportamento idêntico (UTF-8 default).
- **Committed in:** `2de7a32` (Task 3 commit)

**5. [Rule 1 - Bug] F401 ruff lint: Paragrafo importado mas não usado**
- **Found during:** Task 3 ruff check
- **Issue:** Plan Contract 7 obrigava `from biblio_validador.parser import ParserMd, Paragrafo, TipoSecao` (D-22 contrato público) mas `Paragrafo` nunca era referenciado nos testes — F401.
- **Fix:** Adicionada anotação de tipo `paragrafos: list[Paragrafo] = parser.parsear(f)` em `test_round_trip_offset_bytes`. `Paragrafo` agora é usado, F401 silenciado, contrato D-22 mantido.
- **Files modified:** tests/parser/test_markdown.py:141
- **Verification:** `uv run ruff check .` exit 0.
- **Committed in:** `2de7a32` (Task 3 commit)

**6. [Rule 1 - Style] ruff format auto-aplicado (3 arquivos)**
- **Found during:** Task 3 ruff format --check
- **Issue:** 3 arquivos (markdown.py, types.py, test_markdown.py) precisavam reformatação ruff (alinhamento de comentários inline, line breaks, spacing em slices).
- **Fix:** `uv run ruff format .` auto-aplicado. Mudanças cosméticas; comportamento idêntico. ruff também sortou imports alfabeticamente: `Paragrafo, ParserMd, TipoSecao` (era `ParserMd, Paragrafo, TipoSecao`).
- **Files modified:** src/biblio_validador/parser/markdown.py, src/biblio_validador/parser/types.py, tests/parser/test_markdown.py
- **Verification:** `uv run ruff format --check .` retorna `10 files already formatted`.
- **Committed in:** `2de7a32` (Task 3 commit)

**7. [Rule 3 - Blocking] Untracked .coverage file**
- **Found during:** Task 3 git status check
- **Issue:** pytest-cov gera `.coverage` em runtime, não estava em `.gitignore` herdado de Phase 1.
- **Fix:** `.gitignore` ampliado com `.coverage`, `.coverage.*`, `coverage.xml`.
- **Files modified:** .gitignore
- **Verification:** `git status --short` confirma `.coverage` ignorado.
- **Committed in:** `2de7a32` (Task 3 commit)

---

**Total deviations:** 7 auto-fixed (5 Rule 1 — bugs/typos no plan, 1 Rule 2 — missing coverage, 1 Rule 3 — blocking config)
**Impact on plan:** Todas as deviações eram correções de inconsistências internas do plan ou ajustes de tooling necessários para os gates Task 3. Nenhuma alterou o contrato funcional de Phase 2 (4 success criteria de ROADMAP cumpridos integralmente). Sem scope creep.

## Issues Encountered

- **markdown-it-py footnote_plugin discarta orphan footnote definitions:** Inicialmente o teste `test_aux_footnote_orfa` esperava que footnote sem referência no corpo retornasse `Paragrafo(tipo=NOTA_RODAPE, paragrafo_pai_idx=None)`. Verificação empírica mostrou que o `footnote_plugin` simplesmente não emite tokens para definições órfãs (testado com `print()` direto). Teste reformulado para `test_aux_footnote_orfa_silent` que asserta o comportamento real (zero NOTA_RODAPE, parágrafo do corpo intacto) — pin empírico do contrato com a lib.
- **Token map de paragraph_open dentro de footnote_open inclui o prefixo da definição:** `[^1]: Corpo da nota.` produz `paragraph_open` com `map=[2,3]` cobrindo a linha INTEIRA (prefixo + body). O fast-path `_build_paragrafo` strip o prefixo conforme decisão #1 acima.

## User Setup Required

None — Phase 2 não introduz nenhuma configuração externa, secrets, ou dashboards.

## Next Phase Readiness

- **Phase 3 (Dataclasses Core — CORE-02 + CORE-03):** `Paragrafo.linha_inicio/linha_fim/offset_bytes/len_bytes` são o shape que `Violacao` espelha. A convenção `frozen=True, slots=True` está estabelecida; replicar para `Violacao` (frozen) e `Patch` (mutable, slots only). PEP 604 unions e inline comments idem.
- **Phase 5 (PatchAplicador — CORE-06):** Invariante byte-exact `src_bytes_nfc[offset:offset+len_bytes].decode("utf-8") == p.texto` está pinado por property test e foi a base para D-13 ("gravar sempre em NFC"). Phase 5 herda diretamente — `PatchAplicador` deve ler arquivo, normalizar para NFC, aplicar patches em ordem reversa sobre offsets em bytes, e gravar em NFC.
- **Phase 6 (Validador piloto cst_012 — CORE-07):** Primeiro consumidor real de `list[Paragrafo]`. Usa o re-export D-22: `from biblio_validador.parser import ParserMd, Paragrafo, TipoSecao`. `Paragrafo.texto` já está NFC + sem markup de prefixo de footnote, pronto para regex `cst_012`.
- **Phase 16 (Parser LaTeX — VAL-07):** Replicar o pattern de offsets byte-exact via `pylatexenc 2.10` + `pos_to_lineno_colno()`. Estrutura `parser/latex.py` espelha `parser/markdown.py` (mesma classe `ParserTex`, mesma `list[Paragrafo]` retornada).
- **Sem blockers.** Phase 2 está completa e Phase 3 (Dataclasses Core) é a próxima fase no roadmap M1.

## Self-Check

Verificação final do conteúdo declarado neste SUMMARY:

- src/biblio_validador/parser/__init__.py — FOUND
- src/biblio_validador/parser/types.py — FOUND
- src/biblio_validador/parser/markdown.py — FOUND
- tests/parser/__init__.py — FOUND
- tests/parser/fixtures/__init__.py — FOUND
- tests/parser/fixtures/eolica_first_30.md — FOUND
- tests/parser/test_markdown.py — FOUND
- Commit `6e95549` (Task 1) — FOUND
- Commit `9fc84f1` (Task 2) — FOUND
- Commit `2de7a32` (Task 3) — FOUND
- `uv run pytest tests/parser/` → 14 passed
- `uv run pytest tests/` → 17 passed (3 Phase 1 + 14 Phase 2)
- `uv run pytest --cov=biblio_validador.parser --cov-fail-under=90` → 96.89%, exit 0
- `uv run mypy --strict src/biblio_validador/parser/` → Success: no issues found in 3 source files
- `uv run mypy --strict src/` → Success: no issues found in 5 source files
- `uv run ruff check .` → All checks passed
- `uv run ruff format --check .` → 10 files already formatted

## Self-Check: PASSED

---
*Phase: 02-parser-markdown*
*Completed: 2026-05-05*
