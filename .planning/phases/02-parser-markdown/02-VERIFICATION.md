---
phase: 02-parser-markdown
verified: 2026-05-05T07:10:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
re_verification: false
---

# Phase 2: Parser Markdown — Verification Report

**Phase Goal:** Parser `.md` CommonMark + footnotes que segmenta em parágrafos com offsets byte-exact e normalização NFC
**Verified:** 2026-05-05T07:10:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (from ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `ParserMd.parsear("artigo.md")` retorna `list[Paragrafo]` com `linha_inicio`, `linha_fim`, `offset_bytes` corretos | VERIFIED | `markdown.py:35-69` retorna `list[Paragrafo]`. Test `test_paragrafo_simples_um_so_paragrafo` (test_markdown.py:18-33) valida `linha_inicio==1`, `linha_fim==1`, `offset_bytes==0`. Test `test_round_trip_offset_bytes` (test_markdown.py:129-151) prova invariante byte-exact `src_bytes_nfc[offset:offset+len_bytes].decode("utf-8") == p.texto`. Spot-check sobre fixture Eólica: 16 paragrafos com linha_inicio/fim/offset corretos (TITULO linha 1, RESUMO linha 9, parágrafo Investiga-se linha 11). |
| 2 | Parágrafo com acento composto (NFD) é normalizado para NFC antes de indexar | VERIFIED | `markdown.py:55` aplica `unicodedata.normalize("NFC", text)` source-único antes de tokenizar (D-11). Test `test_normalizacao_nfc` (test_markdown.py:63-74) valida NFD `café` → NFC `café` no `texto` retornado, e asserta que `́` (combining acute) NÃO sobrevive. |
| 3 | Footnotes `[^n]` são segmentados como `TipoSecao.NOTA_RODAPE` separado do corpo | VERIFIED | `markdown.py:185-192` rastreia `in_footnote` via `footnote_open`/`footnote_close`; `markdown.py:216-233` aplica `tipo=NOTA_RODAPE` quando dentro de footnote. Test `test_footnote_separa_e_linka` (test_markdown.py:77-92) valida que `[^1]: Corpo da nota.` vira `Paragrafo(tipo=NOTA_RODAPE, ref_nota="1", texto="Corpo da nota.", paragrafo_pai_idx=corpo[0].indice)`. Spot-check Eólica: footnotes [^a] e [^b] linkadas aos parágrafos dos autores nas linhas 5 e 7. |
| 4 | Teste com trecho do artigo Eólica Nordeste retorna parágrafos identificáveis linha a linha | VERIFIED | Fixture `tests/parser/fixtures/eolica_first_30.md` (excerpt verbatim do artigo Pompeu/Lamarck). Test `test_artigo_eolica_excerpt` (test_markdown.py:95-126) valida `linha_inicio==1` para TITULO, `linha_inicio==9` para `## RESUMO`, `linha_inicio==11` para parágrafo "Investiga-se". Spot-check executado: 16 parágrafos retornados com linha_inicio/fim corretos para todos. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/biblio_validador/parser/__init__.py` | Re-export D-22 (`ParserMd`, `Paragrafo`, `TipoSecao`) com `__all__` | VERIFIED | 7 linhas; `__all__ = ["ParserMd", "Paragrafo", "TipoSecao"]` confere com D-22 (ordem alfabética por ruff) |
| `src/biblio_validador/parser/types.py` | Dataclass `Paragrafo(frozen=True, slots=True)` com 11 campos D-02 + Enum `TipoSecao` com 14 valores D-03 | VERIFIED | Linha 27: `@dataclass(frozen=True, slots=True)`. 11 campos confirmados (`arquivo, indice, tipo, nivel_heading, texto, linha_inicio, linha_fim, offset_bytes, len_bytes, ref_nota, paragrafo_pai_idx`). Enum com 14 valores confirmados. |
| `src/biblio_validador/parser/markdown.py` | Classe `ParserMd` com pipeline NFC + 7 helpers privados | VERIFIED | 282 linhas. Classe `ParserMd` com `parsear()` + 7 helpers (`_construir_linha_offsets`, `_carregar_mapa_secao`, `_classificar_heading`, `_normalizar_heading`, `_build_paragrafo`, `_walk`, `_resolver_pais`). Pipeline read_bytes → BOM strip → CRLF→LF → NFC → encode → linha_offsets → parse → walk → resolver_pais confirmado. |
| `tests/parser/__init__.py` | Marker vazio | VERIFIED | Existe (0 bytes) |
| `tests/parser/fixtures/__init__.py` | Marker vazio | VERIFIED | Existe (0 bytes) |
| `tests/parser/fixtures/eolica_first_30.md` | Excerpt verbatim Eólica + 2 footnotes | VERIFIED | 30 linhas; h1 linha 1 (TITULO), `## RESUMO` linha 9, parágrafo "Investiga-se" linha 11, `[^a]:` e `[^b]:` linhas 29-30 |
| `tests/parser/test_markdown.py` | 6 testes canônicos D-26 + 1 round-trip property + 7 auxiliares | VERIFIED | 14 testes confirmados (5 D-26 + 1 round-trip + 1 integration Eólica + 7 aux). Todos passam. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `ParserMd.__init__` | `MarkdownIt + footnote_plugin` | `MarkdownIt().use(footnote_plugin)` | WIRED | `markdown.py:32` — D-14 (footnote_plugin obrigatório) |
| `ParserMd.parsear` | NFC normalization | `unicodedata.normalize("NFC", text)` | WIRED | `markdown.py:55` — D-11 source-único |
| `ParserMd.parsear` | linha_offsets table | `_construir_linha_offsets(src_bytes)` | WIRED | `markdown.py:63` calcula tabela cumulativa em UTF-8 NFC |
| `ParserMd.parsear` | walker iterativo | `_walk(tokens, src_bytes, linha_offsets, path)` | WIRED | `markdown.py:66` — sem recursão (D-25 mitigation T-02-05) |
| `ParserMd.parsear` | footnote linkage | `_resolver_pais(paragrafos)` | WIRED | `markdown.py:67` resolve `paragrafo_pai_idx` via regex `\[\^([^\]]+)\]` (D-16) |
| `_build_paragrafo` | byte-exact slice | `src_bytes[offset_bytes:end_offset]` | WIRED | `markdown.py:146` slice direto sobre source NFC bytes (D-09) |
| `_classificar_heading` | mapa canônico | `self._mapa_secao` | WIRED | `markdown.py:111-113` lookup via `_normalizar_heading` (D-05) |
| Public API re-export | `parser.markdown.ParserMd` | `from biblio_validador.parser import ParserMd, Paragrafo, TipoSecao` | WIRED | `__init__.py:3-6`; consumido por test_markdown.py:8 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `ParserMd.parsear` retorna `list[Paragrafo]` | `paragrafos` | `_walk` + `_resolver_pais` sobre tokens markdown-it reais sobre fixture Eólica | Yes — 16 paragrafos com texto/offsets/linha reais | FLOWING |
| `Paragrafo.texto` | `chunk.decode("utf-8")` | slice `src_bytes[offset_bytes:end_offset]` sobre source NFC real | Yes — round-trip provado por property test e por spot-check Eólica | FLOWING |
| `Paragrafo.paragrafo_pai_idx` (footnote linkage) | `label_to_idx[label]` | regex `\[\^[^\]]+\]` sobre texto de parágrafos não-NOTA | Yes — Eólica spot-check: [^a]→idx 2 (POMPEU), [^b]→idx 3 (LAMARCK) | FLOWING |
| `Paragrafo.tipo` (herança de seção) | `current_secao` | state-machine no `_walk` propagando seção mais recente | Yes — Eólica spot-check: TITULO inicial, RESUMO depois de `## RESUMO`, INTRODUCAO depois de `## INTRODUÇÃO` | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 14 parser tests pass | `uv run pytest tests/parser/ -x` | `14 passed in 0.28s` | PASS |
| Coverage gate (>= 90%) | `uv run pytest --cov=biblio_validador.parser --cov-fail-under=90` | `96.89%` | PASS |
| Mypy strict gate | `uv run mypy --strict src/biblio_validador/parser` | `Success: no issues found in 3 source files` | PASS |
| Ruff lint gate | `uv run ruff check src/biblio_validador/parser tests/parser` | `All checks passed!` | PASS |
| Ruff format gate | `uv run ruff format --check src/biblio_validador/parser tests/parser` | `6 files already formatted` | PASS |
| Full regression suite (Phase 1 + Phase 2) | `uv run pytest tests/ -q` | `17 passed in 0.42s` | PASS |
| Live parse of Eólica fixture | `python -c "ParserMd().parsear(...)"` | 16 paragrafos, byte-exact round-trip OK, footnotes linkadas corretamente | PASS |
| Task commits exist in history | `git show 6e95549 9fc84f1 2de7a32` | All 3 commits present (feat/test/chore Task 1-3) | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CORE-01 | 02-01-PLAN.md | Parser que lê `.md` (CommonMark + footnotes) em parágrafos com offsets byte-exact via `markdown-it-py` 4.0.0 | SATISFIED | `markdown.py:65` usa `MarkdownIt().use(footnote_plugin).parse()`; offsets byte-exact provados por property test e Eólica integration. NOTE: REQUIREMENTS.md description menciona "parágrafos + frases + linhas" mas D-17 do CONTEXT.md descopia "frases" e "linhas" para validadores on-demand em M3+; ROADMAP.md success criteria não mencionam frases/linhas. Phase boundary explicitly limits scope to paragraphs. Já marcado `[x]` em REQUIREMENTS.md linha 31. |
| CORE-11 | 02-01-PLAN.md | Normalização Unicode NFC no parser (evita falhas com acentos compostos) | SATISFIED | `markdown.py:55` aplica `unicodedata.normalize("NFC", text)` source-único; test_normalizacao_nfc valida NFD→NFC; documentado em docstring (D-12). Já marcado `[x]` em REQUIREMENTS.md. |

Both requirements declared by 02-01-PLAN.md (CORE-01, CORE-11). REQUIREMENTS.md mapping table lines 113-114 confirms both `Phase 2 — Parser Markdown | Complete`. No orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `markdown.py` | 274 | `logger.warning("footnote órfã ...")` defensive code não-alcançável (markdown-it-py 4.0.0 silently discards orphan footnote definitions) | Info | Documentado em SUMMARY.md decisão #4. Mantido por defesa contra mudanças futuras da lib. NÃO é stub — é um warning para um caminho real, mas inacessível com a versão atual da dep. Não afeta correção. |

No TODO/FIXME/PLACEHOLDER, nenhum return null/return [] sem justificativa, nenhum console.log, nenhum prop hardcoded. O retorno `[]` em `markdown.py:60` para arquivo vazio é comportamento contratado (D-19) e testado por `test_aux_arquivo_vazio_retorna_lista_vazia`.

### Decision Compliance (D-01..D-27)

| Decisão | Implementado em | Status |
|---------|----------------|--------|
| D-01: módulo `src/biblio_validador/parser/` com `__init__/types/markdown` | tree confirmado | OK |
| D-02: `Paragrafo(frozen=True, slots=True)` 11 campos | types.py:27-44 | OK |
| D-03: `TipoSecao` Enum com 14 valores explícitos string snake_case | types.py:8-24 | OK |
| D-04: CORPO/DESCONHECIDO semântica | types.py:23-24, markdown.py:178 (DESCONHECIDO inicial) | OK |
| D-05: classificação heading-text-based via `_carregar_mapa_secao` | markdown.py:87-103 | OK |
| D-06: h1 primeiro → TITULO; 2º+ h1 → SECAO | markdown.py:109-110 + flag `is_first_h1` linha 199 | OK |
| D-07: parágrafos do corpo herdam `tipo` da seção mais recente | markdown.py:178 + `current_secao` linha 219 | OK |
| D-08: headings h3+ → `SECAO` com `nivel_heading` 3+ | markdown.py:114-115 | OK |
| D-09: offsets byte-exact em dois passos (linha_offsets + slice) | markdown.py:63 + 142-146 | OK |
| D-10: parser não calcula `col_inicio/col_fim` (Paragrafo não tem esses campos) | types.py | OK |
| D-11: NFC source-único antes de tokenização | markdown.py:55 | OK |
| D-12: invariante NFC documentada em docstring | markdown.py:26-29 | OK |
| D-13: PatchAplicador herda decisão (referenciado em SUMMARY § Next Phase Readiness) | scope Phase 5 | DEFERRED (próxima phase) |
| D-14: `footnote_plugin` registrado | markdown.py:32 | OK |
| D-15: `[^n]` permanece embutido no texto do pai | markdown.py:127-168 (não há remoção); test_footnote_separa_e_linka assert `"[^1]" in pai.texto` | OK |
| D-16: corpo footnote vira `Paragrafo(NOTA_RODAPE, ref_nota=label)` | markdown.py:185-192, 219, 271-278 | OK |
| D-17: apenas parágrafos (sem frases/linhas) | types.py — único shape Paragrafo | OK |
| D-18: UTF-8 strict, BOM strip silencioso, FileNotFoundError/UnicodeDecodeError propagados | markdown.py:38-51, 274 | OK |
| D-19: arquivo vazio → `[]`, inexistente → FileNotFoundError | markdown.py:38-41, 59-60 | OK |
| D-20: CRLF→LF antes de NFC | markdown.py:53 | OK |
| D-21: `ParserMd` é classe com `__init__()` + `parsear(path)` | markdown.py:23, 31, 35 | OK |
| D-22: re-export em `parser/__init__.py` com `__all__ = ["ParserMd", "Paragrafo", "TipoSecao"]` | __init__.py:3-6 | OK |
| D-23: type hints 100% | mypy strict clean confirma | OK |
| D-24: ruff line-length 80 | ruff check + format clean | OK |
| D-25: loguru — primeiro consumidor real (info entry/exit, info NFD→NFC, error antes de re-raise, warning footnote órfã) | markdown.py:11, 36, 40, 46, 57, 68, 274 | OK |
| D-26: 6 testes canônicos (5 D-26.1..5 + 1 round-trip property) | test_markdown.py:18-151 | OK |
| D-27: sem benchmark (Phase 17) | nenhum benchmark adicionado | OK |

All 27 decisions honored. D-13 is decided in Phase 2 but its enforcement is in Phase 5 (PatchAplicador) per SUMMARY.

### Human Verification Required

None. All ROADMAP success criteria are programmatically verified via tests + spot-checks. The single Manual-Only verification in 02-VALIDATION.md (visual inspection of loguru DEBUG log prose) is non-functional (verifies log message clarity), and the loguru emissions are confirmed working in spot-check above. No UI, no real-time behavior, no external service.

### Gaps Summary

No gaps. Phase 2 achieves its goal completely:

- All 4 ROADMAP success criteria verified by test + spot-check
- All 27 implementation decisions (D-01..D-27) honored in code
- All 7 expected artifacts present and substantive
- All key links wired (parser pipeline ⇄ NFC ⇄ markdown-it ⇄ footnote_plugin ⇄ resolver_pais)
- Coverage 96.89% (gate 90%); mypy strict clean; ruff check + format clean
- Full regression: 17/17 tests pass (3 Phase 1 + 14 Phase 2)
- CORE-01 and CORE-11 already marked `[x]` in REQUIREMENTS.md
- Phase 2 marker `[ ]` on ROADMAP.md line 25 should be flipped to `[x]` by the orchestrator (post-verification action, mirrors what was done for Phase 1 in commit `b20baa5`).

---

*Verified: 2026-05-05T07:10:00Z*
*Verifier: Claude (gsd-verifier)*
