# Phase 1: Bootstrap - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning
**Mode:** `--auto` (decisões auto-resolvidas pelo recomendado, log abaixo)

<domain>
## Phase Boundary

Projeto Python instalável com layout canônico `src/biblio_validador/`, entry point `validar` no PATH e dependências M1 gerenciadas via `uv`. Cobre exclusivamente CORE-12 do REQUIREMENTS.md. Parser, dataclasses, validadores e fixers ficam para Phases 2+.

</domain>

<decisions>
## Implementation Decisions

### Identidade do pacote

- **D-01:** Nome do pacote Python = `biblio_validador` (módulo importável). Distribution name no `pyproject.toml` = `biblio-validador` (PEP 503 normalizado, hífen).
- **D-02:** Layout `src/` (PEP 621 + uv padrão): `src/biblio_validador/__init__.py`. Evita import acidental do source tree sem instalação.
- **D-03:** Versão inicial = `0.1.0` em `__init__.py` como `__version__ = "0.1.0"` (única exposição pública nesta fase; classes públicas vêm em Phases 2-5).

### Gestão de dependências

- **D-04:** `uv` como gerenciador único. Comando canônico: `uv sync`.
- **D-05:** Python pin = `requires-python = ">=3.13"` (STACK.md confirma; `tomllib`, `match` statement, `slots=True` exigem 3.10+, mas alinhar com 3.13 corta retrocompatibilidade desnecessária).
- **D-06:** Deps M1 instaladas no grupo principal `[project.dependencies]`:
  - `markdown-it-py>=4.0.0`
  - `mdit-py-plugins` (sem pin — segue markdown-it-py)
  - `pylatexenc>=2.10,<3.0` (fixar abaixo de alpha)
  - `typer>=0.25.1`
  - `rich>=15.0.0`
  - `loguru>=0.7.3`
- **D-07:** Deps M7 em grupo opcional `[project.optional-dependencies].llm`:
  - `anthropic>=0.97.0`
  - `jinja2>=3.1.6`
  - Instalação: `uv sync --extra llm` quando M7 começar.
- **D-08:** Dev deps em `[dependency-groups].dev` (uv-native):
  - `pytest>=9.0.3`
  - `pytest-cov>=7.1.0`
  - `ruff` (sem pin)
  - `mypy` (sem pin, modo strict)
- **D-09:** `uv.lock` versionado no git desde Phase 1 (reprodutibilidade dia 1; lockfile é fonte de verdade de versões transitivas).

### CLI / entry point

- **D-10:** Entry point único `validar = "biblio_validador.cli:app"` em `[project.scripts]`. Subcomandos `validar`, `corrigir`, `auditar` virão como `app.command()` em phases futuras (M1 piloto + M8 orchestrator). Phase 1 entrega apenas `app = typer.Typer()` esqueleto + `validar --help` funcional.
- **D-11:** Esqueleto mínimo `cli.py`: define `app = typer.Typer(help="Validador acadêmico — biblioteca canônica PPGD/Unifor")` e expõe stub `@app.callback()` ou comando placeholder que retorna exit 0. Não implementa lógica de validação (Phases 6-9).

### Tooling de qualidade

- **D-12:** `ruff` configurado em `pyproject.toml`:
  - `line-length = 80` (CLAUDE.md doutorado)
  - `target-version = "py313"`
  - `[tool.ruff.lint] select = ["E", "F", "I", "UP", "B"]`
  - Substitui flake8 + black + isort.
- **D-13:** `mypy` configurado strict:
  - `[tool.mypy] strict = true`
  - `python_version = "3.13"`
  - Type hints obrigatórios em todo código novo (CLAUDE.md regra 9).
- **D-14:** `pytest` config em `pyproject.toml`:
  - `testpaths = ["tests"]`
  - `addopts = "--tb=short"`
  - `[tool.coverage.run] source = ["biblio_validador"] branch = true`

### Smoke test obrigatório

- **D-15:** `tests/test_cli.py` com 1 teste mínimo verificando `validar --help` retorna exit 0 e contém string "biblioteca canônica". Atende success criteria #2 do roadmap. Sem este teste, Phase 1 não pode declarar conclusão verificável.
- **D-16:** `tests/__init__.py` vazio (marcador de pacote pytest).

### Itens diferidos para outras Phases

- **D-17:** Pre-commit hook (`.pre-commit-config.yaml`) → M8 (Phase 50+). Phase 1 entrega só infra mínima.
- **D-18:** GitHub Actions / CI → fora de escopo M1 (projeto local single-user; CI vira relevante em M8 se publicar).
- **D-19:** Logging configurado via `loguru` → adiar para Phase 2 (parser) onde primeiro `logger.add()` faz sentido.

### Claude's Discretion

- Estrutura interna de subdiretórios além de `src/biblio_validador/__init__.py` e `src/biblio_validador/cli.py` (parser/validadores/fixers só em Phases seguintes — não criar pastas vazias agora).
- Texto exato do `description` no `pyproject.toml` (deve refletir o do PROJECT.md).
- README.md (já existe na raiz, não tocar nele aqui).
- Conteúdo exato do `app.callback()` placeholder no `cli.py`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Stack e versões
- `.planning/research/STACK.md` — versões fixadas no PyPI, justificativa de cada lib, `pyproject.toml` exemplificado §"pyproject.toml Exemplificado"
- `.planning/research/SUMMARY.md` §"Recommended Stack" — confirmação stdlib-first
- `.planning/research/PITFALLS.md` — riscos a evitar desde Phase 1

### Requisitos
- `.planning/REQUIREMENTS.md` §"Core (M1)" — CORE-12 (única req que Phase 1 cobre); CORE-11 (NFC) é Phase 2
- `.planning/ROADMAP.md` §"Phase 1: Bootstrap" — 4 success criteria explícitos

### Projeto e regras
- `.planning/PROJECT.md` §"Constraints" — Python 3.13+, uv, ruff, mypy
- `CLAUDE.md` (raiz biblioteca_canonica, se existir) — regras globais
- `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` §"Regras para o Agente" — type hints, max 80 chars, uv (não pip), `docker compose` (sem hífen)

### Arquitetura futura (informa decisões agora)
- `.planning/research/ARCHITECTURE.md` — confirma que `cli.py` é entry único; valida nome `biblio_validador`
- `.planning/research/FEATURES.md` — confirma que CLI tem 3 comandos (validar/corrigir/auditar) — justifica entry point único com subcomandos

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **Nenhum código Python pré-existente** — `biblioteca_canonica/` contém apenas dados (38 JSONs em `02_escrita/`, `01_templates/`, `03_fontes/`, `04_normas/`, `05_metadados/`). Greenfield Python project.
- `INDEX.json` (raiz) — índice global da biblioteca; informativo, não consumido pelo validador.
- `README.md` (raiz) — descrição da biblioteca; não tocar nesta phase.
- `.gitignore` (raiz) — já existe; adicionar `__pycache__/`, `.venv/`, `.pytest_cache/`, `htmlcov/`, `*.egg-info/`, `dist/`, `build/` se ausentes.

### Established Patterns

- **JSON como fonte de verdade**: regras editoriais em `02_escrita/termos_proibidos/` são consumidas read-only pelos validadores (Phases 10+). Phase 1 não precisa carregá-los, mas o layout deve permitir acesso fácil via `Path(__file__).parent.parent.parent / "02_escrita"`.
- **uv**: o doutorado todo padroniza `uv` (CLAUDE.md raiz). Sem `requirements.txt` legado.

### Integration Points

- **Não há sistema legado a integrar nesta phase.** Validador é processo standalone. Integrações externas (build.sh LaTeX, pre-commit, gws GDocs) ficam para M8 (Phases 55-57).
- Após `uv sync`, o entry point `validar` deve ficar em `.venv/bin/validar` e ser invocável de qualquer cwd com venv ativa.

</code_context>

<specifics>
## Specific Ideas

- **Layout `src/`**: explicitado pela STACK.md exemplo + REQ-CORE-12. Evita o anti-padrão "import-from-cwd" que mascara bugs de packaging.
- **Lockfile commitado**: alinhado com a postura "reprodutibilidade desde dia 1" de toda a infra do doutorado (PROJECT.md menciona `uv` como padrão; lockfile é o complemento natural).
- **Optional deps `llm`**: economiza ~50MB de install (anthropic SDK + tokenizers transitivos) durante M1-M6 onde Claude API não é tocada.

</specifics>

<deferred>
## Deferred Ideas

- **Pre-commit hook** (`.pre-commit-config.yaml`) — M8 (Phase 50+).
- **CI/CD GitHub Actions** — fora do roadmap atual; v2.
- **Pacote em PyPI** — out of scope; uso interno do doutorado.
- **Dockerfile** — não há justificativa (CLI local single-user).
- **Configuração `loguru`** — Phase 2 (primeiro consumidor real).
- **CLI subcomandos `corrigir` / `auditar`** — Phase 8 (orchestrator mínimo) + Phase 52 (CLI unificado).

</deferred>

---

*Phase: 01-bootstrap*
*Context gathered: 2026-05-04 (auto-mode)*
