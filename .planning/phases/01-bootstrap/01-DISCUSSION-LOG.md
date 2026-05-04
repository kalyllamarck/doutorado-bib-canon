# Phase 1: Bootstrap - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisões em CONTEXT.md — log preserva alternativas consideradas.

**Date:** 2026-05-04
**Phase:** 01-bootstrap
**Mode:** `--auto` (Claude escolheu opção recomendada de cada gray area; usuário não foi consultado interativamente)
**Areas discussed:** Identidade do pacote, Gestão de dependências, CLI/entry point, Tooling de qualidade, Smoke test, Itens diferidos

---

## Identidade do pacote

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `biblio_validador` | Match REQ-CORE-12; nome descritivo | ✓ |
| `validador` | Match exemplo STACK.md (curto) | |
| `biblio_canon_validator` | Mais explícito sobre origem | |

**Auto-pick:** `biblio_validador` — REQ-CORE-12 é fonte de verdade, STACK.md é exemplo informal.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| Layout `src/` | PEP 621, uv padrão, evita import-from-cwd | ✓ |
| Layout flat | `biblio_validador/` na raiz | |

**Auto-pick:** `src/` — STACK.md exemplifica explicitamente; previne anti-padrão.

---

## Gestão de dependências

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| Python `>=3.13` | Match STACK.md, alinhado com features modernas | ✓ |
| Python `>=3.11` | Maior compatibilidade (tomllib OK) | |
| Python `>=3.12` | Meio-termo | |

**Auto-pick:** `>=3.13` — sem requisito de retrocompatibilidade; STACK.md já confirmou.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| Deps M7 em `[project.optional-dependencies].llm` | Install M1 enxuto, opt-in para Claude API | ✓ |
| Tudo em `[project.dependencies]` | Simples, mas pesado em M1-M6 | |
| Deps M7 em `[dependency-groups].llm` (uv-native) | Equivalente, menos portável | |

**Auto-pick:** optional-dependencies `llm` — padrão PEP 621, instalação via `uv sync --extra llm`.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| Commitar `uv.lock` desde já | Reprodutibilidade dia 1 | ✓ |
| Adicionar `uv.lock` ao `.gitignore` | Mais leve, mas perde reprodutibilidade | |

**Auto-pick:** commitar — alinha com postura geral do doutorado.

---

## CLI / entry point

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| Entry único `validar` typer com subcomandos | Convenção typer; STACK.md exemplifica | ✓ |
| Três entry points (`validar`/`corrigir`/`auditar`) | Comandos isolados | |
| Entry único `biblio` com subcomandos | Mais genérico | |

**Auto-pick:** `validar` único com subcomandos — STACK.md §"pyproject.toml Exemplificado" usa exatamente isso.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `cli.py` esqueleto: `app = typer.Typer()` + callback placeholder | Atende success criteria #2 (`validar --help`) sem implementar lógica | ✓ |
| `cli.py` com subcomando dummy `validar arquivo.md` que retorna stub | Mais funcional, mas mistura escopos | |

**Auto-pick:** esqueleto mínimo — Phase 1 = bootstrap, não funcionalidade.

---

## Tooling de qualidade

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `ruff` (lint + format) | Substitui flake8+black+isort, single tool | ✓ |
| `black` + `flake8` + `isort` | Tradicional, 3 ferramentas | |

**Auto-pick:** ruff — STACK.md já estabelece; CLAUDE.md doutorado usa.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `mypy strict = true` | Type hints rigorosos desde início | ✓ |
| `mypy` permissivo | Migração gradual | |
| Sem mypy | Só ruff cobre lint | |

**Auto-pick:** mypy strict — CLAUDE.md raiz exige type hints; rigor desde dia 1 é mais barato que retrofit.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `line-length = 80` | CLAUDE.md doutorado | ✓ |
| `line-length = 100` | Padrão moderno | |
| `line-length = 120` | Black recente | |

**Auto-pick:** 80 — regra explícita do doutorado.

---

## Smoke test

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `tests/test_cli.py` valida `validar --help` agora | Atende success criteria #2 verificável | ✓ |
| Sem teste em Phase 1 | Mais leve, mas critério #2 vira manual | |
| Suite completa de testes de smoke | Overkill para bootstrap | |

**Auto-pick:** 1 teste mínimo — verificabilidade automática da Phase 1.

---

## Itens diferidos

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| Pre-commit hook adiado para M8 | Mantém Phase 1 enxuta | ✓ |
| Pre-commit hook agora | Maior rigor desde início, mas escopo cresce | |

**Auto-pick:** adiar — M8 já planejado para integrações.

| Opção | Descrição | Selecionada |
|-------|-----------|-------------|
| `loguru` config adiada para Phase 2 | Primeiro consumidor real está lá | ✓ |
| `loguru` config em Phase 1 | Sem uso ainda; código morto | |

**Auto-pick:** adiar — evita código morto.

---

## Claude's Discretion

- Estrutura de subdiretórios além de `src/biblio_validador/__init__.py` e `cli.py`
- Texto exato do `description` no `pyproject.toml`
- Conteúdo do `@app.callback()` placeholder
- Edição (ou não) do `README.md` raiz

## Deferred Ideas

- Pre-commit hook (.pre-commit-config.yaml) → M8
- CI/CD GitHub Actions → fora do roadmap
- Pacote em PyPI → out of scope (uso interno)
- Dockerfile → sem justificativa
- Configuração loguru → Phase 2
- Subcomandos CLI corrigir/auditar → Phase 8 + Phase 52
