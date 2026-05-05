# Phase 4: Contratos ABC — Research

**Researched:** 2026-05-05
**Domain:** Python 3.13.13 ABCs (`abc.ABC` + `@abstractmethod`) com
`@classmethod`, `ClassVar`, `re.Pattern` cache class-level e dataclass
`frozen+slots` consumindo `Mapping`. Sem dependências externas — só stdlib.
**Confidence:** HIGH (todas as afirmações abaixo foram empiricamente
verificadas em Python 3.13.13 instalado no `.venv` deste projeto, salvo
indicação `[ASSUMED]` ou `[CITED]`).

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

Origem: `.planning/phases/04-contratos-abc/04-CONTEXT.md` (auto-mode).
Reproduzidas verbatim — pesquisa **NÃO** propõe alternativas a estas; só
documenta como implementar.

**Localização e shape do módulo (D-01..D-04):**
- **D-01:** ABCs ficam em `src/biblio_validador/core/contracts.py`.
- **D-02:** Único arquivo `contracts.py` cobre ambas as ABCs
  (`ValidadorBase` e `FixerBase`).
- **D-03:** `core/__init__.py` re-exporta 8 símbolos:
  `FixerBase, ValidadorBase, ModoFixer, Scope, AplicacaoResultado,
  ContextoFixer + EstadoPatch, Patch, Severidade, Violacao` da Phase 3.
  Ordem alfabética em `__all__`.
- **D-04:** Subpacotes `validators/` e `fixers/` só nascem em Phase 6/7.

**Forma das ABCs (D-05..D-08):**
- **D-05:** `abc.ABC` + `@abstractmethod` (NÃO `typing.Protocol`).
  Justificativa locked: success criterion #1 exige `TypeError` em
  **instanciação**.
- **D-06:** ABC NÃO é `@dataclass`.
- **D-07:** ABC NÃO define `__init__`.
- **D-08:** `typing.ClassVar` em todos os atributos de classe declarados
  na ABC.

**Atributos `ValidadorBase` (D-09..D-11):**
- **D-09:** `JSON_SOURCE: ClassVar[Path]`. Helper
  `_canonical_root() -> Path` no módulo.
- **D-10:** `SCOPE: ClassVar[Scope]` com valores
  `PARAGRAFO/SECAO/DOCUMENTO`.
- **D-11:** Dois `@abstractmethod`:
  `carregar_regras(cls) -> Mapping[str, Any]` (`@classmethod`) e
  `validar(self, paragrafos: list[Paragrafo]) -> list[Violacao]`.

**Atributos `FixerBase` (D-12..D-14):**
- **D-12:** `VIOLACAO_IDS: ClassVar[frozenset[str]]`.
- **D-13:** `MODO: ClassVar[ModoFixer]` com valores
  `AUTO/ASSISTIDO/LLM`.
- **D-14:** Dois `@abstractmethod`: `propor_patches(self, v, contexto)`
  e `aplicar(self, patches, modo_interativo)`. Implementação concreta
  default de `pode_corrigir(self, v) -> bool`.

**Enums `Scope` e `ModoFixer` (D-15..D-18):** ambos em `core/enums.py`,
`enum.Enum` com valor string snake_case. Sem método de ranking.
`ModoFixer → confianca default` é responsabilidade do fixer concreto.

**`carregar_regras()` semântica e cache (D-19..D-22):**
- **D-19:** Cache class-level via
  `cls._regras_compiladas: ClassVar[Mapping[str, re.Pattern[str]] | None]`.
- **D-21:** `carregar_regras` é `@abstractmethod`. Helper utilitário
  `_carregar_json_simples(json_source: Path) ->
  Mapping[str, re.Pattern[str]]` no módulo (não na ABC).
- **D-22:** `FileNotFoundError` / `json.JSONDecodeError` / `re.error`
  propagam (com `regra_id` no contexto da `re.error`).

**`pode_corrigir()` default (D-23):**
```python
def pode_corrigir(self, v: Violacao) -> bool:
    return v.regra_id in type(self).VIOLACAO_IDS
```

**`aplicar` design (D-24..D-25):**
- **D-24:** `aplicar` é `@abstractmethod`.
- **D-25:** Dataclass `AplicacaoResultado` (`frozen=True, slots=True`)
  em `contracts.py` com tuple-only collections.

**`ContextoFixer` (D-26..D-27):**
- **D-26:** Dataclass `ContextoFixer` (`frozen=True, slots=True`) em
  `contracts.py` com campos `paragrafo: Paragrafo`,
  `todas_violacoes_paragrafo: tuple[Violacao, ...]`,
  `regras_compiladas: Mapping[str, "re.Pattern[str]"]`.
- **D-27:** `Mapping` (não `dict`) na assinatura. Importar de
  `collections.abc`.

**Tipos (D-28..D-30):**
- **D-28:** `from __future__ import annotations` no topo de `contracts.py`.
- **D-29:** Importar `Paragrafo` direto (sem ciclo hoje).
- **D-30:** mypy strict herdado.

**Testes (D-31..D-34):**
- **D-31:** 4 testes alinhados aos 4 success criteria.
- **D-32:** `tests/core/fixtures/regras_fake.json` minúsculo.
- **D-33:** 3 testes de erro (`FileNotFoundError`, `JSONDecodeError`,
  `re.error`).
- **D-34:** Coverage `>= 95%` em `core/contracts.py`.

**Tooling (D-35..D-37):** ruff line-length=80, sem `loguru` em `core/`,
mypy strict obrigatório.

### Claude's Discretion (do CONTEXT)

- Texto exato de docstrings PT-BR.
- Estrutura interna dos testes (parametrize ou separar).
- `re.UNICODE` vs `re.UNICODE | re.IGNORECASE` em `_carregar_json_simples`
  — decisão por validador concreto; ABC pode aceitar `flags` opcional.
- `__repr__` customizado em `AplicacaoResultado` ou `ContextoFixer`.

### Deferred Ideas (OUT OF SCOPE)

- State machine enforcement em `EstadoPatch` (Phase 51).
- `ValidadorAgregadoBase` separado (Phase 18).
- `ValidadorBase.versao()` (Phase 20).
- `FixerBase.confianca_minima` (Phase 49).
- Async `validar`/`propor_patches` (PROJECT.md proíbe rede em
  validadores).
- Hooks `pre_validar`/`post_validar`.
- Plugin system com discovery dinâmico.
- `__hash__` customizado em `AplicacaoResultado` ou `ContextoFixer`.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CORE-04 | ABC `ValidadorBase` com `JSON_SOURCE`, `SCOPE`, `carregar_regras()`, `validar(paragrafos) -> list[Violacao]` | Pattern 1 (ABC com classmethod abstrata + ClassVar) + Pattern 4 (cache class-level) + Pattern 5 (`_carregar_json_simples`) + Pattern 9 (regex flags + JSON schema) |
| CORE-05 | ABC `FixerBase` com `VIOLACAO_IDS`, `MODO`, `pode_corrigir(v)`, `propor_patches(v, contexto) -> list[Patch]`, `aplicar(patches, modo_interativo)` | Pattern 2 (FixerBase com pode_corrigir concreto) + Pattern 6 (`AplicacaoResultado` dataclass) + Pattern 7 (`ContextoFixer` dataclass + eq=False trade-off) |

</phase_requirements>

## Project Constraints (from CLAUDE.md)

Extraídos dos dois CLAUDE.md (raiz `Doutorado/CLAUDE.md` + projeto
`biblioteca_canonica/CLAUDE.md`). Planner DEVE auditar PLAN contra esta
lista — divergência é bug do plan, não desta pesquisa.

| # | Diretiva | Origem |
|---|----------|--------|
| C1 | Python 3.13+ obrigatório | biblioteca/CLAUDE.md "Constraints" |
| C2 | Type hints 100% (CLAUDE.md raiz regra 9) | doutorado/CLAUDE.md |
| C3 | max 80 chars/linha | biblioteca/CLAUDE.md + Phase 1 D-12 |
| C4 | Módulo padrão `re` (NÃO `regex`) | biblioteca/CLAUDE.md "Tech Stack" |
| C5 | `dataclasses` stdlib (NÃO pydantic) | biblioteca/CLAUDE.md |
| C6 | `pathlib` (NÃO strings de path) | biblioteca/CLAUDE.md |
| C7 | Zero dependências de rede em validadores | biblioteca/CLAUDE.md "Constraints" |
| C8 | Reprodutibilidade — output determinístico | biblioteca/CLAUDE.md "Constraints" |
| C9 | mypy strict habilitado | Phase 1 D-13 (herdado) |
| C10 | ruff `select = ["E", "F", "I", "UP", "B"]` | Phase 1 D-12 (pyproject.toml:47) |
| C11 | Performance: validador 30k palavras < 5s | biblioteca/CLAUDE.md (informa aqui via Pattern 4) |
| C12 | Sem `loguru`/`logging` em `core/` (puro modelo) | Phase 3 D-33 (herdado) |
| C13 | PT-BR em docstrings, código em English ASCII | Phase 1+2+3 convenção |
| C14 | Absolute imports (`from biblio_validador.<sub>...`) | parser/__init__.py:3-4 (precedente) |
| C15 | `from __future__ import annotations` em `contracts.py` | locked D-28 |
| C16 | Working through GSD commands (não editar fora) | biblioteca/CLAUDE.md "GSD Workflow Enforcement" |

## Summary

Phase 4 é uma fase de **contrato puro**, sem lógica de negócio. Todos os
elementos críticos foram **empiricamente verificados** no `.venv` do
projeto (Python 3.13.13). Os achados não-óbvios que devem entrar no plano
são:

1. **Decoradores em ordem fixa**: `@classmethod` → `@abstractmethod`.
   Inverter (`@abstractmethod` acima de `@classmethod`) **falha em
   tempo de definição da classe** com `AttributeError: attribute
   '__isabstractmethod__' of 'classmethod' objects is not writable`
   (não em `__init__`). [VERIFIED]

2. **Mensagem exata do `TypeError`** que o success criterion #1 exige
   confirmar: `"Can't instantiate abstract class <Cls> without an
   implementation for abstract method[s] '<nome>'"` (ou `methods` no
   plural). [VERIFIED]

3. **Cache class-level via `cls.__dict__`** é o pattern correto para
   evitar que subclasses compartilhem o cache do parent — o uso ingênuo
   `if cls._regras_compiladas is None` lê via MRO e fura o isolamento
   por subclasse. [VERIFIED]

4. **`@dataclass(frozen=True, slots=True)` com campo `Mapping[str,
   re.Pattern[str]]` quebra `__hash__`** — Python tenta hashear o `dict`
   passado e levanta `TypeError: unhashable type: 'dict'`. Solução
   prática: passar `eq=False` no decorator OU aceitar instâncias
   nãohashable e documentar. Este é o achado mais importante e não está
   na CONTEXT.md. [VERIFIED]

5. **Schema JSON dos regex é heterogêneo**: 4 das 12 entradas de
   `04_construcoes_sintaticas_proibidas.json` têm `regex_deteccao: str`
   (cst_001..cst_004); 7 têm `regex_deteccao: list[str]`
   (cst_005..cst_010, cst_012); cst_011 usa chave alternativa
   `regex_deteccao_aproximada`. `_carregar_json_simples` precisa
   normalizar para `list[str]` antes de compilar. [VERIFIED]

6. **`re.UNICODE` é default em Python 3** e todos os 23 regex do JSON
   compilam **sem `re.IGNORECASE`** (porque os autores usam ranges
   explícitos `[a-zà-ÿ]` e prefixo `[Aa]` para casing). Adicionar
   `IGNORECASE` em `_carregar_json_simples` mudaria semântica e poderia
   gerar falsos positivos. [VERIFIED]

7. **Custo de `re.compile`** sobre os 3 regex mais complexos do dataset:
   ~0.15ms por compilação a frio; com cache do módulo `re` o custo
   amortiza para ~0.0004ms. O cache class-level (D-19) **é** necessário
   para garantir success criterion #2 ("compila regex 1x") como
   contrato de API, **mas não é otimização performática crítica** —
   compilar 30 regex × 50 validadores ainda fica em < 200ms.
   [VERIFIED]

**Primary recommendation:** Implementar exatamente o que CONTEXT.md fixou,
com **três adições obrigatórias** que CONTEXT não mencionou:
- (a) usar `eq=False` em `ContextoFixer` (caso contrário `Mapping`
  no campo quebra `__hash__`);
- (b) fazer cache via `cls.__dict__` (não via `getattr`/MRO);
- (c) `_carregar_json_simples` normaliza `str|list[str]` em uma única
  forma antes de compilar.

## Architectural Responsibility Map

Phase 4 é mono-tier (CLI Python local). Mapa por capacidade lógica:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Definir contrato de validador | core/ (API) | — | Pattern matching com Phase 3: tipos+contratos vivem em core/, side-effect zero. |
| Definir contrato de fixer | core/ (API) | — | Mesmo princípio. |
| Carregar JSON-fonte → regex compilados | core/ (helper utilitário) | — | `_carregar_json_simples` é helper isolado, sem estado, idempotente. |
| Cache de regras compiladas | core/ (estado de classe) | — | Cache vive na classe concreta (não na ABC) via `cls.__dict__`. |
| Aplicar patches a arquivo | (Phase 5) | — | Out of scope — `aplicar` é só assinatura aqui. |
| I/O de relatório / logging | (Phase 8/Phase 59) | — | Out of scope — `core/` permanece sem `loguru`. |

## Standard Stack

### Core (todos stdlib — zero novas dependências)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `abc` | stdlib | `ABC` + `@abstractmethod` para enforço de contrato em **instanciação** | [VERIFIED: Python 3.13.13 docs + empirical] CONTEXT D-05 locked. |
| `typing` | stdlib | `ClassVar`, `cast`, `Any` | [VERIFIED] CONTEXT D-08 locked. |
| `collections.abc` | stdlib | `Mapping` (covariância em assinaturas) | [CITED: Python 3.13 docs `collections.abc.Mapping`] CONTEXT D-27 locked. |
| `dataclasses` | stdlib | `@dataclass(frozen=True, slots=True)` para `AplicacaoResultado` e `ContextoFixer` | [VERIFIED: Phase 3 já usa] CONTEXT D-25/D-26 locked. |
| `pathlib` | stdlib | `Path` para `JSON_SOURCE` e `_canonical_root()` | [VERIFIED: Phase 2/3 já usa] CONTEXT D-09 locked. |
| `re` | stdlib | `re.Pattern[str]`, `re.compile`, `re.error` | [VERIFIED] biblioteca/CLAUDE.md C4 locked. |
| `json` | stdlib | Carga determinística do JSON-fonte | [CITED: Python 3.13 docs] D-22 propagação de `JSONDecodeError`. |
| `enum` | stdlib | `Enum` para `Scope` e `ModoFixer` | [VERIFIED: Phase 3 `Severidade`/`EstadoPatch`] CONTEXT D-15/D-17 locked. |
| `__future__` | stdlib | `from __future__ import annotations` (PEP 563) | [VERIFIED] CONTEXT D-28 locked. |

### Already Installed (do pyproject.toml — não tocar)

| Library | Version | Status |
|---------|---------|--------|
| `pytest` | `>=9.0.3` | Presente em `[dependency-groups].dev`. |
| `pytest-cov` | `>=7.1.0` | Presente — Phase 4 reusa para `--cov=biblio_validador.core --cov-fail-under=95`. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff | Verdict |
|------------|-----------|----------|---------|
| `abc.ABC` | `typing.Protocol` (`runtime_checkable`) | Protocol é estrutural — não bloqueia instanciação. Falha success criterion #1. | **CONTEXT D-05 já bloqueou** — pesquisa confirma: `Protocol` não emite `TypeError` em construção. [VERIFIED]: classe que omite método "abstract" de Protocol instancia normalmente. |
| `cls._regras_compiladas` (atributo) | `functools.cache`/`lru_cache` em método | `lru_cache` em método retém referência forte a `self`/`cls` → memory leak. Atributo explícito é auditável e per-subclass via `cls.__dict__`. | **Manter atributo** — locked. |
| `eq=True` (default) em `ContextoFixer` | `eq=False` | `eq=True` exige `__hash__` que tenta hashear o `Mapping` (dict) → `TypeError`. `eq=False` desabilita ambos e usa identity. | **Recomendar `eq=False`** (gap em CONTEXT — ver Pitfall 4 abaixo). |
| `dict` na assinatura | `Mapping` | `dict` impede passagem de `MappingProxyType` ou subclasse de Mapping; perde covariância. | **`Mapping` locked D-27.** |
| Helper como classmethod default na ABC | Função module-level `_carregar_json_simples` | Função module-level desacopla helper de hierarquia ABC; subclasses chamam explicitamente. CONTEXT D-21 locked. | **Função locked.** |

**Installation:** Nenhuma. Phase 4 não instala nada novo.

**Version verification:** Os versionamentos abaixo foram verificados
contra o `.venv` deste projeto em 2026-05-05:
- `python --version` → `Python 3.13.13` [VERIFIED via `uv run python -c
  "import sys; print(sys.version_info)"`]
- Todas as libs acima são stdlib — versão = versão do interpretador.

## Architecture Patterns

### System Architecture Diagram

```
                ┌──────────────────────────────────────────────┐
                │  Subclasse concreta (Phase 6+: cst_012Validador)│
                │  declara JSON_SOURCE, SCOPE, VIOLACAO_IDS, MODO │
                └─────────────┬────────────────────────────────┘
                              │ herda
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      core/contracts.py                          │
│                                                                 │
│  ┌────────────────────────────┐   ┌──────────────────────────┐ │
│  │       ValidadorBase        │   │       FixerBase          │ │
│  │  (abc.ABC)                 │   │  (abc.ABC)               │ │
│  │                            │   │                          │ │
│  │  + JSON_SOURCE: ClassVar   │   │  + VIOLACAO_IDS: ClassVar│ │
│  │  + SCOPE: ClassVar[Scope]  │   │  + MODO: ClassVar        │ │
│  │  + _regras_compiladas:     │   │                          │ │
│  │      ClassVar[Mapping|None]│   │  @abstractmethod         │ │
│  │                            │   │  propor_patches(v, ctx)  │ │
│  │  @classmethod              │   │  @abstractmethod         │ │
│  │  @abstractmethod           │   │  aplicar(patches, modo)  │ │
│  │  carregar_regras()         │   │                          │ │
│  │  @abstractmethod           │   │  pode_corrigir(v)        │ │
│  │  validar(paragrafos)       │   │  (concreto, default)     │ │
│  └────────────┬───────────────┘   └──────────────────────────┘ │
│               │                                                 │
│               │ chama opcionalmente                              │
│               ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  _carregar_json_simples(path: Path)                     │   │
│  │     → Mapping[str, re.Pattern[str]]                     │   │
│  │  (helper utilitário; subclasses simples chamam dentro    │   │
│  │   do seu carregar_regras())                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────┐   ┌────────────────────────────┐   │
│  │  AplicacaoResultado    │   │  ContextoFixer             │   │
│  │  (frozen+slots, tuples)│   │  (frozen+slots, eq=False)  │   │
│  │  patches_aceitos       │   │  paragrafo                 │   │
│  │  patches_rejeitados    │   │  todas_violacoes_paragrafo │   │
│  │  patches_suprimidos    │   │  regras_compiladas         │   │
│  │  bytes_modificados     │   │                            │   │
│  └────────────────────────┘   └────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │ importa
                   ▼
            core/dataclasses.py    parser/types.py
            (Violacao, Patch)      (Paragrafo)
            core/enums.py
            (Severidade, EstadoPatch,
             Scope NOVO, ModoFixer NOVO)
```

**Componentes (mapeamento responsabilidade ↔ arquivo):**

| Componente | Arquivo | Responsabilidade |
|------------|---------|-------------------|
| `ValidadorBase` | `core/contracts.py` | Contrato de detecção. Abstract até subclasse decidir como compilar regras. |
| `FixerBase` | `core/contracts.py` | Contrato de fix. `pode_corrigir` concreto; `propor_patches` + `aplicar` abstratos. |
| `_carregar_json_simples` | `core/contracts.py` (módulo, não classe) | Carga + compile + propagação de erros (D-22). |
| `_canonical_root` | `core/contracts.py` (módulo, não classe) | Resolve `Path` raiz da biblioteca via `__file__.parents[3]`. |
| `AplicacaoResultado` | `core/contracts.py` | Tipo de retorno de `aplicar()`. |
| `ContextoFixer` | `core/contracts.py` | Tipo de argumento de `propor_patches()`. |
| `Scope`, `ModoFixer` | `core/enums.py` (estende Phase 3) | Enums novos com convenção snake_case. |
| Re-export | `core/__init__.py` | Estende Phase 3 com 4 novos símbolos. |

### Recommended Project Structure

```
src/biblio_validador/
├── __init__.py                  (Phase 1, intocado)
├── cli.py                       (Phase 1, intocado)
├── core/
│   ├── __init__.py              (ESTENDIDO Phase 4 — re-export 8 símbolos)
│   ├── contracts.py             (NOVO Phase 4)
│   ├── dataclasses.py           (Phase 3, intocado)
│   └── enums.py                 (ESTENDIDO Phase 4 — adiciona Scope+ModoFixer)
└── parser/
    ├── __init__.py              (Phase 2, intocado)
    ├── types.py                 (Phase 2, intocado — exporta Paragrafo)
    └── markdown.py              (Phase 2, intocado)

tests/
└── core/
    ├── __init__.py              (Phase 3, intocado)
    ├── test_dataclasses.py      (Phase 3, intocado)
    ├── test_contracts.py        (NOVO Phase 4)
    └── fixtures/                (NOVO Phase 4)
        ├── regras_fake.json
        ├── regras_malformadas.json
        └── regras_regex_invalido.json
```

### Pattern 1: Abstract `@classmethod` — ordem dos decoradores

**What:** Declarar método de classe abstrato em ABC.
**When to use:** `carregar_regras` (D-21) — método que opera sobre a
classe (não sobre instância) mas é obrigatório implementar na subclasse.
**Critical:** A ordem dos decoradores **importa em tempo de definição da
classe** (não em runtime). [VERIFIED]

```python
# CERTO — @classmethod abaixo de @abstractmethod (no decorator stack,
# isso significa @classmethod é aplicado PRIMEIRO).
class ValidadorBase(ABC):
    @classmethod
    @abstractmethod
    def carregar_regras(cls) -> Mapping[str, re.Pattern[str]]:
        """Compila regras do JSON-fonte (CORE-04)."""
        ...
```

```python
# ERRADO — @abstractmethod acima de @classmethod (=@classmethod aplicado
# por último). Falha em DEFINIÇÃO DA CLASSE (não em instanciação) com:
#   AttributeError: attribute '__isabstractmethod__' of 'classmethod'
#   objects is not writable
class WRONG(ABC):
    @abstractmethod
    @classmethod
    def carregar_regras(cls): ...
```

**Source:** [VERIFIED empirically em Python 3.13.13]. Em Python <3.3
existia `@abstractclassmethod` separado; desde 3.3 é a composição
`@classmethod` + `@abstractmethod` na ordem correta. [CITED: Python 3.13
abc docs — `abc.abstractclassmethod` deprecated since 3.3 in favor of
plain `@classmethod` + `@abstractmethod`.]

### Pattern 2: ABC com método abstract + método concreto default

**What:** ABC declara contrato (abstract) e fornece implementação default
(concreto) em uma única classe.
**When to use:** `FixerBase.pode_corrigir` (D-23) é concreto enquanto
`propor_patches` e `aplicar` são abstract.

```python
class FixerBase(ABC):
    VIOLACAO_IDS: ClassVar[frozenset[str]]
    MODO: ClassVar[ModoFixer]

    @abstractmethod
    def propor_patches(
        self, v: Violacao, contexto: ContextoFixer,
    ) -> list[Patch]:
        """Propõe patches para v (CORE-05)."""
        ...

    @abstractmethod
    def aplicar(
        self,
        patches: list[Patch],
        modo_interativo: bool,
    ) -> AplicacaoResultado:
        """Delega ao PatchAplicador da Phase 5."""
        ...

    def pode_corrigir(self, v: Violacao) -> bool:
        """Cobre o regra_id de v (D-23)."""
        return v.regra_id in type(self).VIOLACAO_IDS
```

**Note:** `type(self).VIOLACAO_IDS` (não `self.VIOLACAO_IDS`) é
preferível em método de instância para deixar explícito que se está
acessando atributo de classe — também é mais resistente a confusão de
shadowing por instance attr (mypy strict pega isso, mas torna o código
auto-documentado).

### Pattern 3: `ClassVar` declarations sem default + override em subclasse

**What:** ABC declara `ClassVar` sem inicializador (forma de "exigir que
subclasse declare"); subclasse atribui valor concreto.
**When to use:** `JSON_SOURCE`, `SCOPE`, `VIOLACAO_IDS`, `MODO` (D-09,
D-10, D-12, D-13).

```python
# Em core/contracts.py:
class ValidadorBase(ABC):
    JSON_SOURCE: ClassVar[Path]   # sem default — subclasse declara
    SCOPE: ClassVar[Scope]
    _regras_compiladas: ClassVar[
        Mapping[str, re.Pattern[str]] | None
    ] = None  # tem default — opcional

# Em phase 6 (cst_012Validador):
class Cst012Validador(ValidadorBase):
    JSON_SOURCE = (
        _canonical_root()
        / "02_escrita/termos_proibidos"
        / "04_construcoes_sintaticas_proibidas.json"
    )
    SCOPE = Scope.PARAGRAFO
```

**Critical pitfall:** Sob mypy strict, omitir o anotação `: ClassVar[...]`
no override silenciosamente cria um instance attribute na subclasse (com
mesmo nome) — mypy detecta isso (Phase 1 D-13 garante). Mas a anotação
**não precisa repetir-se no override em runtime**: Python aceita o
literal `frozenset({'cst_012'})` como atribuição. [VERIFIED]

```python
# Em FxA01:
class FxA01(FixerBase):
    VIOLACAO_IDS = frozenset({'cst_012'})  # OK — runtime aceita
    MODO = ModoFixer.AUTO
```

[VERIFIED] empírico: `FxA01.VIOLACAO_IDS == frozenset({'cst_012'})`,
mypy strict aceita o override sem reclamar (covariância de literal
`frozenset` com `frozenset[str]` declarada no parent).

### Pattern 4: Cache class-level com `cls.__dict__` lookup (não `getattr`)

**What:** Cache que vive **por subclasse**, não compartilhado pela
hierarquia.
**When to use:** Cache de regex compilado (D-19), `_regras_compiladas`.
**Critical:** O pattern ingênuo `if cls._regras_compiladas is None`
**lê via MRO** — primeira chamada em `SubA` escreve em `SubA._regras...`,
mas em `SubB` o atributo de classe ainda é `None` (lido do parent), e o
cache reprocessará corretamente. **Porém**, se em algum momento o parent
fosse mutado (raro mas possível), todas as subclasses passariam a
compartilhar. O pattern robusto é checar `cls.__dict__` diretamente:

```python
# Em ValidadorBase ou no método override em subclasse:
@classmethod
def carregar_regras(cls) -> Mapping[str, re.Pattern[str]]:
    """Compila uma vez por subclasse (success criterion #2).

    Cache class-level via cls.__dict__ — não compartilha entre
    subclasses na hierarquia (RESEARCH Pattern 4).
    """
    cached = cls.__dict__.get("_regras_compiladas")
    if cached is not None:
        return cached  # type: ignore[no-any-return]
    compiladas = _carregar_json_simples(cls.JSON_SOURCE)
    cls._regras_compiladas = compiladas
    return compiladas
```

**Why not `if cls._regras_compiladas is None`?** Porque `cls._...` lê
via MRO; se subclasse B herda de A e A já tem cache, B.carregar_regras
lê A._regras (errado — são regras de A, não de B). [VERIFIED] empirical
no Test #3.

**Note:** A ABC `ValidadorBase` declara o atributo com default `None`,
mas como `carregar_regras` é `@abstractmethod` (D-21), a ABC nunca
**executa** o cache. As **subclasses** implementam `carregar_regras` —
ou copiam o pattern acima ou chamam `_carregar_json_simples` direto sem
cache (cada subclasse decide). O `_regras_compiladas: ClassVar[...]`
declarado na ABC **garante** que mypy strict reconheça o atributo no
namespace de qualquer subclasse.

### Pattern 5: `_carregar_json_simples` — schema heterogêneo + flags

**What:** Helper module-level que carrega JSON, normaliza schema, compila
regex.
**When to use:** Sempre que validador concreto simples (M2 primitivos)
quiser delegar a carga.

```python
def _carregar_json_simples(
    json_source: Path,
) -> Mapping[str, re.Pattern[str]]:
    """Carrega JSON-fonte + compila regex 1x (D-21).

    Schema esperado:
        {
          "tipo": "...",
          "entradas": [
            {"id": "cst_NNN", "regex_deteccao": "..." | [...]},
            ...
          ]
        }

    Raises:
        FileNotFoundError: json_source inexistente (D-22).
        json.JSONDecodeError: JSON malformado (D-22).
        re.error: regex inválido — mensagem inclui regra_id (D-22).
    """
    data = json.loads(json_source.read_text(encoding="utf-8"))
    compiladas: dict[str, re.Pattern[str]] = {}
    for entrada in data["entradas"]:
        rid = entrada["id"]
        # Schema heterogêneo (Pattern 9): chave pode ser
        # regex_deteccao OU regex_deteccao_aproximada (cst_011),
        # valor pode ser str OU list[str].
        raw = entrada.get("regex_deteccao") or entrada.get(
            "regex_deteccao_aproximada"
        )
        if raw is None:
            continue  # entrada sem regex (ex.: cst_005 só com listas)
        padroes = [raw] if isinstance(raw, str) else list(raw)
        # Convenção: se list, joinar com '|' como alternativas.
        # Cada subclasse pode override _carregar_json_simples se
        # quiser semântica diferente (ex.: lista = N regras).
        try:
            if len(padroes) == 1:
                compiladas[rid] = re.compile(padroes[0])
            else:
                compiladas[rid] = re.compile("|".join(
                    f"(?:{p})" for p in padroes
                ))
        except re.error as e:
            raise re.error(f"regra {rid}: {e}") from e
    return compiladas
```

**Key decisions in this snippet (research-driven, not in CONTEXT):**

- **Sem `re.IGNORECASE`** — todos os 23 regex do JSON compilam OK sem
  IGNORECASE. Os autores codificaram casing explícito (`[a-zà-ÿ]`,
  `[Aa]`, etc.). Adicionar IGNORECASE alteraria semântica. [VERIFIED]
- **Sem `re.UNICODE` explícito** — é o default em Python 3, redundante.
  [CITED: Python 3.13 `re` docs.]
- **Lista → alternativas com `|`** — convenção razoável para schema
  com `regex_deteccao: list[str]`. cst_005 (3 regex), cst_007 (2), etc.
  Validador concreto pode override `_carregar_json_simples` se quiser
  semântica diferente (ex.: cada item é uma sub-regra).
- **Encoding `utf-8` obrigatório** — JSONs canônicos têm acentos.
- **`raise ... from e`** preserva chain do error para debug.

### Pattern 6: `AplicacaoResultado` — frozen+slots OK (sem dict)

**What:** Dataclass de retorno de `aplicar()`.
**When to use:** D-25.

```python
@dataclass(frozen=True, slots=True)
class AplicacaoResultado:
    """Resultado de FixerBase.aplicar (D-25).

    Tuple-only nas coleções (Phase 3 D-07): garante imutabilidade
    real e hashabilidade.
    """
    patches_aceitos: tuple[Patch, ...]
    patches_rejeitados: tuple[Patch, ...]
    patches_suprimidos: tuple[Patch, ...]
    bytes_modificados: int
```

**Hashabilidade:** `Patch` é unhashable (Phase 3 D-06: mutável).
Portanto `tuple[Patch, ...]` é unhashable também. Isto significa
`AplicacaoResultado` é unhashable (não pode ir em set/dict-key) — mas
sua **igualdade estrutural** funciona (`==` compara campos). É aceitável
porque ninguém vai armazenar `AplicacaoResultado` num `set`. Documentar
em docstring.

[ASSUMED] o uso em testes/orchestrator é sempre por igualdade
estrutural ou inspeção campo-a-campo, não por hash.

### Pattern 7: `ContextoFixer` — frozen+slots COM `eq=False` (CONTÉM dict)

**What:** Dataclass de argumento de `propor_patches`.
**When to use:** D-26.
**Critical:** Esta é a divergência mais importante entre research e
CONTEXT.md.

CONTEXT.md D-26 declara `regras_compiladas: Mapping[str, "re.Pattern[str]"]`
como campo. Em runtime, `Mapping` é `dict` — que é unhashable. Com
`@dataclass(frozen=True, slots=True)` (defaults: `eq=True`),
Python gera um `__hash__` que tenta hashear cada campo. **`hash(Ctx(...))`
levanta `TypeError: unhashable type: 'dict'`.** [VERIFIED empirical no
Test #7/#8.]

Soluções (recomendar (a) ao planner):

**Opção (a) — adicionar `eq=False` (recomendado):**
```python
@dataclass(frozen=True, slots=True, eq=False)
class ContextoFixer:
    """Contexto que o orchestrator passa ao fixer (D-26).

    eq=False (RESEARCH Pattern 7):
        - Igualdade vira identity (`is`).
        - hash() funciona via id() (object.__hash__).
        - Justificativa: campo regras_compiladas é Mapping (dict em
          runtime), que é unhashable. Sem eq=False, hash(ctx) levanta
          TypeError. ContextoFixer é argumento de chamada, não chave
          de cache — identity equality é semanticamente correta.
    """
    paragrafo: Paragrafo
    todas_violacoes_paragrafo: tuple[Violacao, ...]
    regras_compiladas: Mapping[str, re.Pattern[str]]
```

**Opção (b) — manter `eq=True` e documentar a limitação:**
```python
@dataclass(frozen=True, slots=True)
class ContextoFixer:
    """... — INSTÂNCIAS NÃO SÃO HASHABLE (Pitfall 4)."""
    ...
```

Recommendation: **(a)**. Razão: `ContextoFixer` é descartável (instância
por chamada), nunca vai num `set` ou dict-key. Igualdade por valor
(comparar dois `ContextoFixer` campo-a-campo, em particular comparando
dicts) é cara e raramente útil. Identity é mais coerente.

### Pattern 8: `from __future__ import annotations` + `re.Pattern[str]`

**What:** Anotações como strings (PEP 563).
**When to use:** Todo o módulo `contracts.py` (D-28).
**Effect:** `re.Pattern[str]` em type hints **não exige** import runtime
de `re` apenas para a anotação — mas como o módulo **usa** `re.compile`
e `re.error` em runtime, o import direto é necessário de qualquer forma.
PEP 563 só ajuda com tipos que de outra forma exigiriam string literal
forward ref.

```python
from __future__ import annotations  # PEP 563

import re  # necessário em runtime (re.compile, re.error)
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar

from biblio_validador.parser.types import Paragrafo
from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import ModoFixer, Scope
```

[VERIFIED] empirical: `class Foo: REGRAS: ClassVar[Mapping[str,
re.Pattern[str]]] = {}` compila sem erro com `from __future__ import
annotations`.

### Pattern 9: JSON regex schema heterogêneo (verificado)

[VERIFIED] inspeção de `04_construcoes_sintaticas_proibidas.json`:

| `id` | Tipo de `regex_deteccao` | count | Notas |
|------|--------------------------|-------|-------|
| `cst_001` | `str` | 1 | `:\\s+[a-zA-ZÀ-ÿ]` |
| `cst_002` | `str` | 1 | 57 chars |
| `cst_003` | `str` | 1 | 75 chars |
| `cst_004` | `str` | 1 | gerundio + `exclusoes` |
| `cst_005` | `list[str]` | 3 | atribuição genérica |
| `cst_006` | `list[str]` | 3 | tríade refinamento |
| `cst_007` | `list[str]` | 2 | abertura lacônica |
| `cst_008` | `list[str]` | 4 | pseudossíntese |
| `cst_009` | `list[str]` | 2 | abertura condicional |
| `cst_010` | `list[str]` | 1 | tópico numerado |
| `cst_011` | `list[str]` | 2 | **chave alternativa** `regex_deteccao_aproximada` |
| `cst_012` | `list[str]` | 2 | anúncio metarretórico |

**Implicação para `_carregar_json_simples`:**
- Aceitar ambos `regex_deteccao` e `regex_deteccao_aproximada` como
  fonte (cst_011).
- Aceitar ambos `str` e `list[str]` como valor.
- Compilar todos sem `IGNORECASE` (regex já têm casing embutido).
- Total: 23 regex; 0 falham ao compilar com flags default. [VERIFIED]

**Note:** Outros JSONs (`01_termos_lexicais_proibidos.json`,
`05_sinais_graficos_proibidos.json`, `06_regras_coocorrencia.json`)
podem ter schemas levemente diferentes — mas Phase 4 só precisa que
`_carregar_json_simples` cubra o schema mais comum. Validadores
concretos com schema exótico (VAL-06 conjuncoes 802 entradas em 18
subtipos) **devem** override `carregar_regras` ao invés de chamar
`_carregar_json_simples` (CONTEXT D-21 prevê isso).

### Anti-Patterns to Avoid

- **`@abstractmethod` ACIMA de `@classmethod`** — falha em definição da
  classe com `AttributeError`. [VERIFIED] Test #12.
- **`Protocol` em vez de `ABC`** — não bloqueia instanciação; falha
  success criterion #1.
- **`set[str]` em vez de `frozenset[str]` para `VIOLACAO_IDS`** —
  mutabilidade de classe attr é bug latente.
- **`dict` em vez de `Mapping` na assinatura** — perde covariância,
  impede passar `MappingProxyType`.
- **`if cls._regras_compiladas is None`** — lê via MRO, fura isolamento
  per-subclasse. Usar `cls.__dict__.get("_regras_compiladas")`.
- **Try/except silenciador em `_carregar_json_simples`** — viola D-22 e
  PROJECT.md "reprodutibilidade determinística".
- **`@dataclass(frozen=True, slots=True)` com `Mapping` field e `eq=True`
  default** — `hash()` quebra. Usar `eq=False` (Pattern 7).
- **Importar `dataclasses` bare em `core/contracts.py`** — outro arquivo
  do mesmo subpacote chama-se `dataclasses.py`; confunde. Sempre
  `from dataclasses import dataclass` (Phase 3 já segue isso).
- **`re.IGNORECASE` em `_carregar_json_simples`** — JSONs codificaram
  casing intencional; flag mudaria semântica. [VERIFIED] sobre os 23
  regex.
- **Logging em `core/contracts.py`** — viola convenção `core/` puro.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Enforço de contrato em instanciação | Custom `__init_subclass__` que checa atributos manualmente | `abc.ABC` + `@abstractmethod` | ABC é semântica de Python idiomática; mensagem de erro padronizada; mypy entende; docs explicam. [CITED: PEP 3119, Python 3.13 `abc` docs.] |
| Cache de regex compilado | `functools.lru_cache` em método de classe | Atributo `cls._regras_compiladas` + `cls.__dict__.get(...)` | `lru_cache` retém ref a `cls` indefinidamente, dificulta limpeza em testes; atributo é auditável e fácil de resetar. |
| Serialização de `Path` em log/repr | Override `__str__` em `Path` | `Path` já tem `__fspath__` e `__str__` corretos | stdlib resolve. |
| Validação de schema JSON em runtime | Loop manual com `assert` | Pular validação — JSONs são curados manualmente | CONTEXT D-21 + biblioteca/CLAUDE.md "Sem cache stateful": JSONs são fonte de verdade versionada. Validar runtime adicionaria custo sem ROI. |
| Verificar igualdade estrutural de dataclass | `__eq__` manual | `@dataclass(eq=True)` default | dataclass já gera. (Para `ContextoFixer` queremos `eq=False` por outras razões — Pattern 7.) |
| Filter de `regra_id` em fixer | Loop com `for ... in self.list_de_ids` | `v.regra_id in type(self).VIOLACAO_IDS` (frozenset O(1)) | `frozenset` lookup é amortizado O(1). |
| Reescrever import path resolution | `os.path.dirname(__file__)` + concat | `Path(__file__).parents[N]` | `pathlib` é stdlib idiomática (biblioteca/CLAUDE.md C6). |

**Key insight:** Phase 4 é fina (~150 linhas). Não introduzir nenhuma
abstração nova além das mandadas pela CONTEXT. Toda stdlib resolve cada
sub-problema.

## Common Pitfalls

### Pitfall 1: Decorator order — `@abstractmethod @classmethod` é fatal

**What goes wrong:** `AttributeError` em definição da classe (não em
construção, não em chamada). Difícil de associar à ordem de decoradores
sem precedente.
**Why it happens:** `@classmethod` envolve a função num descriptor; o
descriptor `classmethod` (em Python pré-3.9) não tinha
`__isabstractmethod__` writable. Em 3.13.13, ainda raise. [VERIFIED] Test
#12. Stack overflow vs. recente: o assunto está documentado mas a maioria
dos tutoriais ainda mostra ordem errada.
**How to avoid:** Sempre `@classmethod` mais próximo da função
(decorator stack: `@abstractmethod` em cima → aplicado por último).
**Warning signs:** Tracebacks com `attribute '__isabstractmethod__' of
'classmethod' objects is not writable` apontando para a definição da
classe.

### Pitfall 2: Cache class-level shared via MRO

**What goes wrong:** Subclasse B compartilha cache compilado pela
subclasse A (ou parent ABC, se ABC executasse o cache).
**Why it happens:** Acesso `cls._regras_compiladas` em método de classe
faz lookup via MRO. Atribuição `cls._regras_compiladas = X` escreve em
`cls.__dict__` (sempre na classe correta), MAS leitura passa por MRO.
Se A.carregar_regras escreveu em A.__dict__, B.carregar_regras lê A...
mas o cache pertence a A, não a B. Resultado: B nunca recompila, retorna
regras de A.
**How to avoid:** Pattern 4 — usar `cls.__dict__.get("_regras_compiladas")`
para leitura. Atribuição direta via `cls._regras_compiladas = X`
funciona corretamente.
**Warning signs:** Test que instancia 2 validadores diferentes recebe
mesma `Mapping` em ambos. Adicionar test parametrizado com 2 subclasses
fake distintas — `r1 is not r2` deve passar.

### Pitfall 3: `JSONDecodeError` é subclasse de `ValueError`

**What goes wrong:** Test que faz `pytest.raises(ValueError)` em vez de
`pytest.raises(json.JSONDecodeError)` passa, mas mascarando intent. Test
robusto deve usar a classe específica.
**Why it happens:** `json.JSONDecodeError(ValueError, ...)` — herança
documentada. [CITED: Python 3.13 `json` docs.]
**How to avoid:** Em `tests/core/test_contracts.py` usar
`pytest.raises(json.JSONDecodeError)` para o teste de fixture
malformada (D-33). `ValueError` também passaria mas perde precisão.
**Warning signs:** Test de erro passa com qualquer raise.

### Pitfall 4: `frozen=True` + `eq=True` + `Mapping` field → `TypeError`

**What goes wrong:** `hash(ContextoFixer(...))` levanta `TypeError:
unhashable type: 'dict'`. CONTEXT.md D-26 não menciona isto. Plan que
copiar D-26 verbatim e usar dataclass default vai escrever um teste que
falha (ou pior — não escrever esse teste e descobrir no consumidor da
API em Phase 7).
**Why it happens:** `dataclass(frozen=True, eq=True)` (default eq) gera
`__hash__` baseado em `tuple(getattr(self, f) for f in fields)`. Se
algum campo é unhashable (dict), `hash()` falha em runtime. [VERIFIED]
empirical no Test #8. Frozen sem eq=False **NÃO** torna campos imutáveis
recursivamente.
**How to avoid:** Pattern 7 — `eq=False` em `ContextoFixer`. Documentar
a razão na docstring.
**Warning signs:** Test de smoke `ctx = ContextoFixer(...); hash(ctx)`
falha com `unhashable type: 'dict'`.

### Pitfall 5: Subclasse esquece anotação `ClassVar`

**What goes wrong:** Subclasse declara `JSON_SOURCE = Path("...")` sem
`: ClassVar[Path]`. Em runtime funciona. Sob mypy strict, pode aparecer
warning sutil — ou pior — `JSON_SOURCE` pode ser interpretado como
instance attr na subclasse.
**Why it happens:** `ClassVar` é dica para mypy/runtime checkers, não
sintaxe imperativa. Sem repetir, mypy infere de novo a partir do
literal.
**How to avoid:** Em testes (D-31), incluir test que valida a anotação
em **ambas** ABC e subclasse fake — ou aceitar prática: subclasses
NÃO precisam repetir `: ClassVar[...]` no override **desde que** a ABC
já declare. mypy strict aceita isto. [VERIFIED] empirical Test #13.
Documentar em docstring de `ValidadorBase`/`FixerBase` que subclasses
podem omitir o re-anotar.
**Warning signs:** mypy reclama "Incompatible types in assignment
(expression has type ..., variable has type 'instance attr')".

### Pitfall 6: `_canonical_root()` quebra se `__file__` não existir

**What goes wrong:** Em runtimes embeddable (zipapp, alguns
PyInstaller), `__file__` pode estar ausente em `core/contracts.py`.
**Why it happens:** Convenção, não obrigatório.
**How to avoid:** [ASSUMED — não vamos rodar em zipapp neste projeto.]
Para o projeto doutorado (CLI local + uv venv), `__file__` é sempre
preenchido. Documentar invariante e seguir adiante.
**Warning signs:** N/A — este pitfall é teórico para o uso atual.

### Pitfall 7: Test que importa `dataclasses` (módulo padrão) confunde com `core/dataclasses.py`

**What goes wrong:** `import dataclasses` em test pode resolver para
`biblio_validador.core.dataclasses` se cwd estiver em `src/biblio_validador/core/` ou se `sys.path` incluir esse dir.
**Why it happens:** Phase 3 D-01 já antecipou (nome `core/dataclasses.py`
sombra `stdlib.dataclasses` em cwd certos). `tests/core/test_contracts.py`
deve seguir Phase 3 convenção: `from dataclasses import dataclass,
asdict, FrozenInstanceError`.
**How to avoid:** Manter convenção `from dataclasses import ...` (NUNCA
`import dataclasses` bare).
**Warning signs:** ImportError críptico em CI.

## Code Examples

### Verified `core/contracts.py` skeleton

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
from typing import Any, ClassVar

from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import ModoFixer, Scope
from biblio_validador.parser.types import Paragrafo


# ───────────────────────── helpers module-level ──────────────────────


def _canonical_root() -> Path:
    """Raiz da biblioteca canônica (D-09).

    Resolução: <repo>/biblioteca_canonica/ via __file__.parents[3]:
        contracts.py -> core/ -> biblio_validador/ -> src/ -> root
    """
    return Path(__file__).parents[3]


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


# ───────────────────────── dataclasses auxiliares ────────────────────


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


# ───────────────────────── ABCs ──────────────────────────────────────


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

### Verified `core/enums.py` extension

```python
"""Enums core: Severidade + EstadoPatch + Scope + ModoFixer."""

from enum import Enum


class Severidade(Enum):
    """... (Phase 3 — intocado)."""
    INFO = "info"
    ALERTA = "alerta"
    ERRO = "erro"
    CRITICO = "critico"

    def peso(self) -> int:
        return _PESOS_SEVERIDADE[self]


_PESOS_SEVERIDADE: dict[Severidade, int] = {
    Severidade.INFO: 0,
    Severidade.ALERTA: 1,
    Severidade.ERRO: 2,
    Severidade.CRITICO: 3,
}


class EstadoPatch(Enum):
    """... (Phase 3 — intocado)."""
    PROPOSTO = "proposto"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    SUPRIMIDO = "suprimido"


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

### Verified `core/__init__.py` extension

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

### Verified `tests/core/test_contracts.py` skeleton

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


# ───────── 1. Contract violation: TypeError em instanciação (D-31.1) ──


class _ValidadorIncompleto(ValidadorBase):
    """Falta validar() E carregar_regras() — ABC bloqueia instanciar."""

    JSON_SOURCE = FIXT / "regras_fake.json"
    SCOPE = Scope.PARAGRAFO


def test_validador_incompleto_raises_typeerror() -> None:
    """D-31.1 / Success #1: instanciar subclasse incompleta lança TypeError."""
    with pytest.raises(TypeError, match="abstract method"):
        _ValidadorIncompleto()  # type: ignore[abstract]


class _FixerIncompleto(FixerBase):
    """Falta propor_patches() — ABC bloqueia instanciar."""

    VIOLACAO_IDS = frozenset({"cst_999"})
    MODO = ModoFixer.AUTO

    def aplicar(
        self,
        patches: list[Patch],
        modo_interativo: bool,
    ) -> AplicacaoResultado:
        return AplicacaoResultado((), (), (), 0)


def test_fixer_incompleto_raises_typeerror() -> None:
    """D-31.1 / Success #1: FixerBase também bloqueia."""
    with pytest.raises(TypeError, match="propor_patches"):
        _FixerIncompleto()  # type: ignore[abstract]


# ───────── 2. carregar_regras compila 1x (D-31.2 / Success #2) ────────


class _ValidadorFake(ValidadorBase):
    JSON_SOURCE: ClassVar[Path] = FIXT / "regras_fake.json"
    SCOPE = Scope.PARAGRAFO

    @classmethod
    def carregar_regras(cls) -> Mapping[str, re.Pattern[str]]:
        cached = cls.__dict__.get("_regras_compiladas")
        if cached is not None:
            return cached  # type: ignore[no-any-return]
        compiladas = _carregar_json_simples(cls.JSON_SOURCE)
        cls._regras_compiladas = compiladas
        return compiladas

    def validar(self, paragrafos: list[Paragrafo]) -> list[Violacao]:
        return []


def test_carregar_regras_retorna_mapping() -> None:
    """D-31.2 / Success #2: retorna Mapping[str, re.Pattern[str]]."""
    regras = _ValidadorFake.carregar_regras()
    assert isinstance(regras, Mapping)
    assert "cst_999" in regras
    assert isinstance(regras["cst_999"], re.Pattern)


def test_carregar_regras_cache_idempotente() -> None:
    """D-31.2 / Success #2: chamada 2x retorna o MESMO objeto (cache)."""
    # Reset cache (caso teste anterior tenha populado)
    if "_regras_compiladas" in _ValidadorFake.__dict__:
        del _ValidadorFake._regras_compiladas
    r1 = _ValidadorFake.carregar_regras()
    r2 = _ValidadorFake.carregar_regras()
    assert r1 is r2  # mesma identity = cache hit


# ───────── 3. pode_corrigir default (D-31.3 / Success #3) ─────────────


class _FixerFake(FixerBase):
    VIOLACAO_IDS = frozenset({"cst_999"})
    MODO = ModoFixer.AUTO

    def propor_patches(
        self, v: Violacao, contexto: ContextoFixer
    ) -> list[Patch]:
        return []

    def aplicar(
        self,
        patches: list[Patch],
        modo_interativo: bool,
    ) -> AplicacaoResultado:
        return AplicacaoResultado((), (), (), 0)


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


def test_pode_corrigir_match() -> None:
    """D-31.3 / Success #3: True para regra_id em VIOLACAO_IDS."""
    assert _FixerFake().pode_corrigir(_viol_fake("cst_999")) is True


def test_pode_corrigir_no_match() -> None:
    """D-31.3 / Success #3: False para regra_id fora de VIOLACAO_IDS."""
    assert _FixerFake().pode_corrigir(_viol_fake("cst_001")) is False


# ───────── 4. Smoke imports via re-export (D-31.4) ────────────────────


def test_import_smoke_via_re_export() -> None:
    """D-31.4: __init__.py re-exporta os 8 símbolos novos."""
    from biblio_validador.core import (
        AplicacaoResultado,
        ContextoFixer,
        EstadoPatch,
        FixerBase,
        ModoFixer,
        Patch,
        Scope,
        Severidade,
        ValidadorBase,
        Violacao,
    )
    # Type smoke: classes existem e são chamáveis
    assert callable(ValidadorBase)
    assert callable(FixerBase)
    assert Scope.PARAGRAFO.value == "paragrafo"
    assert ModoFixer.AUTO.value == "auto"


# ───────── D-33: testes de erro de _carregar_json_simples ─────────────


def test_carregar_filenotfound_propaga() -> None:
    """D-33 / D-22: arquivo inexistente propaga FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        _carregar_json_simples(FIXT / "nao_existe.json")


def test_carregar_json_decode_error_propaga() -> None:
    """D-33 / D-22: JSON malformado propaga JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        _carregar_json_simples(FIXT / "regras_malformadas.json")


def test_carregar_re_error_propaga_com_regra_id() -> None:
    """D-33 / D-22: re.error propaga incluindo regra_id."""
    with pytest.raises(re.error, match="cst_invalido"):
        _carregar_json_simples(FIXT / "regras_regex_invalido.json")
```

### Verified test fixtures

`tests/core/fixtures/regras_fake.json`:
```json
{
  "tipo": "fake",
  "entradas": [
    {"id": "cst_999", "regex_deteccao": "\\bfake\\b"}
  ]
}
```

`tests/core/fixtures/regras_malformadas.json`:
```json
{ "entradas": [
```
(JSON propositalmente truncado — gera `json.JSONDecodeError`.)

`tests/core/fixtures/regras_regex_invalido.json`:
```json
{
  "tipo": "fake",
  "entradas": [
    {"id": "cst_invalido", "regex_deteccao": "(?P<unfinished"}
  ]
}
```

[VERIFIED] `re.compile("(?P<unfinished")` levanta
`re.error: missing >` em Python 3.13.13. Mensagem do helper passa a ser
`re.error: regra cst_invalido: missing >`.

## State of the Art

Domain stability: `abc.ABC` é estável desde Python 3.4. Mudanças
relevantes nos últimos anos:

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| `abc.abstractclassmethod` | `@classmethod` + `@abstractmethod` | Python 3.3 (deprecated) | Use only the composition. |
| `Optional[T]` | `T | None` (PEP 604) | Python 3.10 | Já em uso (Phase 2/3). |
| `typing.List`, `typing.Dict` | `list`, `dict` (PEP 585) | Python 3.9 | Já em uso. |
| `Mapping` em `typing` | `collections.abc.Mapping` | Python 3.9 (preferred) | CONTEXT D-27 segue o moderno. |

**Deprecated/outdated:**
- `abc.abstractclassmethod`/`abc.abstractstaticmethod` — usar
  composição.
- `typing.ClassVar` ainda é o lugar canônico (não migrou para
  `collections.abc`).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `ContextoFixer` é descartável (instância por chamada, nunca chave de cache) — justifica `eq=False` | Pattern 7 | Baixo. Se algum consumidor futuro precisar `set[ContextoFixer]`, terá que adicionar `__hash__` custom. Improvável dado escopo. |
| A2 | `__file__` sempre preenchido (sem zipapp/PyInstaller) | Pitfall 6 | Baixo — projeto é CLI local com uv venv; nenhum bundler em uso. |
| A3 | Lista de regex em `cst_005..cst_012` deve ser tratada como alternativas via `\|` | Pattern 5 / 9 | Médio. Validador concreto (M2) pode discordar e querer N regras separadas. CONTEXT D-21 prevê override. Documentado. |
| A4 | `re.IGNORECASE` não é necessário para o JSON atual | Pattern 5 / Anti-Pattern | Baixo. Verificado contra os 23 regex de `04_construcoes_sintaticas_proibidas.json`. Outros JSONs (M2 phases) podem requerer IGNORECASE — validador concreto override `_carregar_json_simples` ou passa flags. |
| A5 | Performance de `re.compile` (~0.15ms cold, ~0.0004ms cached) é insignificante face ao orçamento de 5s/30k palavras | Summary | Baixo — orchestrator (Phase 50) compila ~30 regex de M2 + ~15 de M3 + ~30 de M4 = ~75 regex × 0.15ms = 12ms total cold. Margem confortável. |
| A6 | mypy strict aceita override `VIOLACAO_IDS = frozenset({"cst_012"})` sem re-anotar `: ClassVar[frozenset[str]]` | Pattern 3 | Baixo. Verificado runtime; mypy strict (Phase 1) é o oráculo final — Phase 4 deve rodar `uv run mypy src/biblio_validador/core/contracts.py` no gate. |
| A7 | Phase 6 (validador concreto cst_012) será o primeiro consumidor real e validará todas as decisões deste plan | Code Examples | Médio — bug latente só aparece em Phase 6. Mitigação: testes de fakes em Phase 4 cobrem instanciação, cache, pode_corrigir, e os 3 erros de `_carregar_json_simples`. |

**A1, A2 são marcados verbatim no campo `[ASSUMED]` do código.** A3, A4
são decisões prescritivas que CONTEXT D-21 explicitamente delega ao
validador concreto — Phase 4 implementa a forma "default razoável". A5
é justificativa para success criterion #2 ("compila 1x") como **API
contract**, não como otimização performática.

## Open Questions

1. **`_carregar_json_simples` — list[str] como alternativas (`|`) ou
   N regras independentes?**
   - What we know: schema do JSON atual tem 7/12 entradas com list. CONTEXT
     D-21 delega ao validador concreto.
   - What's unclear: o validador piloto Phase 6 (cst_012) tem 2 regex em
     `regex_deteccao` — vai querer matchá-los como um único composto ou
     iterar separados para ter `match.lastindex` pra contexto? Sem ver
     Phase 6 plan, não dá pra responder.
   - Recommendation: implementar `_carregar_json_simples` com a
     convenção "alternativas via `|`" como default, documentar
     trade-off, deixar override fácil para validadores que prefiram
     N-regras.

2. **`carregar_regras` é `@abstractmethod` (D-21) — duplicação para
   validadores simples?**
   - What we know: M2 tem 8 phases (10-17), 6 delas são primitivos
     simples. Cada uma vai escrever a mesma boilerplate de cache.
   - What's unclear: vale a pena ter um mixin `ValidadorPrimitivoBase`
     (Phase 6+) que implementa `carregar_regras` chamando
     `_carregar_json_simples`? **CONTEXT D-21 já decidiu manter
     abstract** — research só registra a observação. Phase 6 pode
     descobrir que vale criar o mixin como evolução.
   - Recommendation: seguir CONTEXT (abstract). Deixar ferramentas para
     Phase 6 decidir mixin se quiser.

3. **`AplicacaoResultado.bytes_modificados` — semântica?**
   - What we know: D-25 não define se é diff size, soma de bytes
     reescritos, ou byte-count do arquivo final.
   - What's unclear: definição precisa.
   - Recommendation: deixar para Phase 5 (PatchAplicador) decidir; ABC
     só declara o tipo `int` >= 0. Documentar invariante na docstring
     de `AplicacaoResultado`.

## Environment Availability

> Phase 4 é code-only (sem deps externas além do que Phase 1 já
> instalou). Audit abaixo confirma stack atual.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.13 | Toda a phase | ✓ | 3.13.13 | — |
| `pytest` | tests/core/test_contracts.py | ✓ (via `uv run`) | >=9.0.3 (locked pyproject.toml) | — |
| `pytest-cov` | gate cobertura ≥ 95% | ✓ | >=7.1.0 | — |
| `mypy` | gate strict | ✓ | >=1.20.2 | — |
| `ruff` | gate lint | ✓ | >=0.15.12 | — |
| `02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json` | inspeção schema (research) — NÃO consumido em runtime de Phase 4 | ✓ | committed | — |

**Missing dependencies with no fallback:** Nenhuma.
**Missing dependencies with fallback:** Nenhuma.

Tudo pronto. `uv run pytest`, `uv run mypy`, `uv run ruff` funcionam
imediatamente.

## Validation Architecture

> `workflow.nyquist_validation = true` em `.planning/config.json`. Esta
> seção é mandatória.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` 9.0.3 + `pytest-cov` 7.1.0 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (Phase 1 D-14) |
| Quick run command | `uv run pytest tests/core/test_contracts.py -x` |
| Full suite command | `uv run pytest --cov=biblio_validador --cov-report=term-missing` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CORE-04 | `ValidadorBase.JSON_SOURCE` declarável; ABC bloqueia instanciação se falta `validar`/`carregar_regras` | unit | `pytest tests/core/test_contracts.py::test_validador_incompleto_raises_typeerror -x` | ❌ Wave 0 |
| CORE-04 | `carregar_regras` retorna `Mapping[str, re.Pattern[str]]` | unit | `pytest tests/core/test_contracts.py::test_carregar_regras_retorna_mapping -x` | ❌ Wave 0 |
| CORE-04 | `carregar_regras` chamado 2x retorna mesmo objeto (cache) | unit | `pytest tests/core/test_contracts.py::test_carregar_regras_cache_idempotente -x` | ❌ Wave 0 |
| CORE-05 | `FixerBase` bloqueia instanciação sem `propor_patches`/`aplicar` | unit | `pytest tests/core/test_contracts.py::test_fixer_incompleto_raises_typeerror -x` | ❌ Wave 0 |
| CORE-05 | `pode_corrigir` retorna True quando match | unit | `pytest tests/core/test_contracts.py::test_pode_corrigir_match -x` | ❌ Wave 0 |
| CORE-05 | `pode_corrigir` retorna False quando no-match (Success #3) | unit | `pytest tests/core/test_contracts.py::test_pode_corrigir_no_match -x` | ❌ Wave 0 |
| CORE-04+05 | Re-export 8 símbolos via `core/__init__.py` | unit | `pytest tests/core/test_contracts.py::test_import_smoke_via_re_export -x` | ❌ Wave 0 |
| Error handling D-22 | `FileNotFoundError` propaga | unit | `pytest tests/core/test_contracts.py::test_carregar_filenotfound_propaga -x` | ❌ Wave 0 |
| Error handling D-22 | `JSONDecodeError` propaga | unit | `pytest tests/core/test_contracts.py::test_carregar_json_decode_error_propaga -x` | ❌ Wave 0 |
| Error handling D-22 | `re.error` propaga incluindo regra_id | unit | `pytest tests/core/test_contracts.py::test_carregar_re_error_propaga_com_regra_id -x` | ❌ Wave 0 |

**Sampling Rate:**
- **Per task commit:** `uv run pytest tests/core/test_contracts.py -x`
  (~< 1s).
- **Per wave merge:** `uv run pytest --cov=biblio_validador.core --cov-report=term-missing --cov-fail-under=95`
  (Phase 3 + Phase 4 combinados; ~< 3s).
- **Phase gate:** Full suite green + `uv run mypy src/biblio_validador/core/`
  + `uv run ruff check src/biblio_validador/core/` antes de
  `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `tests/core/test_contracts.py` — covers CORE-04, CORE-05.
- [ ] `tests/core/fixtures/regras_fake.json` — fixture sucesso.
- [ ] `tests/core/fixtures/regras_malformadas.json` — fixture
  `JSONDecodeError`.
- [ ] `tests/core/fixtures/regras_regex_invalido.json` — fixture
  `re.error`.

(Framework e config existem desde Phase 1; nada a instalar.)

### Validation Dimensions

| Dimension | What to measure | Threshold | Command |
|-----------|-----------------|-----------|---------|
| **Correctness** | Todos os testes em `test_contracts.py` passam | 100% green | `uv run pytest tests/core/test_contracts.py -x` |
| **Coverage** | Cobertura de `core/contracts.py` | ≥ 95% (D-34) | `uv run pytest --cov=biblio_validador.core.contracts --cov-fail-under=95` |
| **Type safety** | mypy strict sem erros | 0 errors | `uv run mypy src/biblio_validador/core/` |
| **Lint** | ruff sem violations | 0 errors | `uv run ruff check src/biblio_validador/core/ tests/core/` |
| **Performance** | tempo de teste | < 3s para suite Phase 3+4 | observação manual ou `pytest --durations=10` |
| **Regression** | Phase 3 tests continuam green | 100% green | `uv run pytest tests/core/ -x` |

### Nyquist Test Cases (edge cases obrigatórios)

| # | Edge case | Why it matters | Where covered |
|---|-----------|----------------|---------------|
| N1 | Subclasse omite só `validar()` (mantém `carregar_regras`) | Verifica TypeError mensagem inclui `'validar'` | `test_validador_incompleto_raises_typeerror` (parametrize ou separado) |
| N2 | Subclasse omite só `carregar_regras()` | Verifica TypeError mensagem inclui `'carregar_regras'` | idem (variante) |
| N3 | Subclasse omite **ambos** | Verifica mensagem com `methods` plural | idem |
| N4 | `VIOLACAO_IDS = frozenset()` (vazio) | `pode_corrigir` deve retornar False sempre | adicionar test_pode_corrigir_violacao_ids_vazio |
| N5 | JSON com `entradas: []` | `_carregar_json_simples` retorna `{}` (Mapping vazio, não erro) | adicionar test_carregar_entradas_vazias |
| N6 | JSON com regex contendo char não-ASCII (`\bnão\b`) | re.compile não falha; Python 3 default UNICODE | implícito em `regras_fake.json` ampliar com 1 entrada |
| N7 | Subclasse SEM cache (não implementa cache class-level) | Cada chamada compila — performance pior mas correto. Documenta liberdade do CONTEXT D-21. | optional aux test `test_aux_subclasse_sem_cache_funciona` |
| N8 | `cls.__dict__` cache não vaza entre 2 subclasses | Pitfall 2 — duas subclasses fakes paralelas com JSONs diferentes confirmam isolamento | adicionar `test_cache_isolado_entre_subclasses` |
| N9 | `ContextoFixer` instância: `hash(ctx)` funciona (eq=False) | Pitfall 4 — confirma que `eq=False` resolve | adicionar `test_aux_contexto_fixer_hashable_via_identity` |
| N10 | `AplicacaoResultado` igualdade estrutural | success #4 implícito | adicionar `test_aux_aplicacao_resultado_eq` |
| N11 | Override `pode_corrigir` em subclasse para refinamento por severidade | D-23 documenta possibilidade — confirmar não quebra default | optional |
| N12 | `_canonical_root()` retorna path correto | D-09 invariante | `test_aux_canonical_root` |

**Total testes:** 4 success criteria + 3 erros (D-33) + 4-6 contract
aux tests = **11–13 testes**. Coverage ≥ 95% factível para módulo de
~150-200 linhas.

## Security Domain

`security_enforcement` não é setting explícito em `.planning/config.json`
para este projeto. Phase 4 é puro modelo (`core/`), sem rede, sem
parsing de input adversário, sem auth, sem crypto. Aplicabilidade ASVS:

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | n/a |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | partial | JSON-fonte é input; assumido confiável (curado por humano em git). `_carregar_json_simples` propaga erros sem sanitização — correto para curated data. |
| V6 Cryptography | no | n/a |

**Known threat patterns para CLI Python local:**

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| ReDoS via regex catastrophic backtracking | DoS | Pitfall 6 da `PITFALLS.md` (Phase 1) já cobre. Phase 17 (VAL-08) é o gate de performance. Phase 4 só compila — não executa contra input não-confiável. |
| Path traversal via `JSON_SOURCE` | Tampering | Subclasse declara `JSON_SOURCE` como literal absoluto resolvido via `_canonical_root()` — não construído de input externo. Sem risco. |
| Pickle/deserialização hostil | Tampering | Phase 4 só usa `json` (texto, sem deserialização de objetos). Sem risco. |

**Nenhum dos riscos mais sérios para CLIs Python aplica a Phase 4.**

## Sources

### Primary (HIGH confidence)

- **Phase 4 CONTEXT.md** (`.planning/phases/04-contratos-abc/04-CONTEXT.md`)
  — fonte de todas as decisões locked.
- **Phase 3 CONTEXT.md** + **`src/biblio_validador/core/dataclasses.py`**
  + **`src/biblio_validador/core/enums.py`** — código já implementado;
  shape de `Violacao`/`Patch` lido direto.
- **Phase 2 CONTEXT.md** + **`src/biblio_validador/parser/types.py`** —
  shape de `Paragrafo` lido direto.
- **`02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json`**
  — schema heterogêneo de `regex_deteccao` (12 entradas) inspeção direta
  (script Python rodado no `.venv`).
- **`pyproject.toml`** — versões `pytest`, `pytest-cov`, `mypy`, `ruff`.
- **Empirical Python 3.13.13 testing no `.venv` deste projeto** (2026-05-05):
  - Test #1 (TypeError exact message in incomplete ABC) — VERIFIED.
  - Test #2 (`@classmethod` + `@abstractmethod` order works) — VERIFIED.
  - Test #3 (cache via `cls.__dict__` vs MRO) — VERIFIED.
  - Test #4 (`from __future__ import annotations` + `re.Pattern[str]`)
    — VERIFIED.
  - Test #5 (JSON regex schema inspection: 4 str + 7 list + 1 alt key)
    — VERIFIED.
  - Test #6 (todos os 23 regex compilam sem IGNORECASE) — VERIFIED.
  - Test #7/#8 (frozen+slots+dict field quebra `__hash__`; `eq=False`
    resolve) — VERIFIED.
  - Test #9 (subclass override de `ClassVar[frozenset[str]]`) —
    VERIFIED.
  - Test #10 (regex compile cost: 0.15ms cold / 0.0004ms cached) —
    VERIFIED.
  - Test #11 (`Path.parents[3]` resolve canonical root) — VERIFIED.
  - Test #12 (`@abstractmethod` acima de `@classmethod` falha em
    definição) — VERIFIED.
  - Test #14 (mensagens distintas de TypeError per missing-method) —
    VERIFIED.

### Secondary (MEDIUM confidence — official docs)

- [CITED: Python 3.13 `abc` module docs](https://docs.python.org/3/library/abc.html)
  — composição `@classmethod` + `@abstractmethod` é a forma current;
  `abstractclassmethod` deprecated.
- [CITED: Python 3.13 `re` module docs](https://docs.python.org/3/library/re.html)
  — `re.UNICODE` é default; `re.error` é a base class de regex syntax
  errors.
- [CITED: Python 3.13 `dataclasses` docs](https://docs.python.org/3/library/dataclasses.html)
  — `frozen=True` + default `eq=True` gera `__hash__` que pode falhar
  em campo unhashable.
- [CITED: Python 3.13 `json` docs](https://docs.python.org/3/library/json.html)
  — `JSONDecodeError(ValueError, ...)`.
- [CITED: PEP 563 — Postponed Evaluation of Annotations](https://peps.python.org/pep-0563/)
  — `from __future__ import annotations`.
- [CITED: PEP 3119 — Introducing Abstract Base Classes](https://peps.python.org/pep-3119/)
  — design rationale de `abc.ABC`.

### Tertiary (LOW confidence — assumed/training data)

- [ASSUMED] mypy strict aceita `VIOLACAO_IDS = frozenset({"cst_012"})`
  override sem re-anotar — Phase 4 plan **deve** validar via `uv run
  mypy --strict` no gate.
- [ASSUMED] subclasse `_FixerIncompleto` que herda `aplicar` ainda
  sintetiza erro de instanciação por causa de `propor_patches`. (Test
  exemplo deve confirmar).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pure stdlib, todas as APIs verificadas em
  3.13.13 local.
- Architecture (ABC com abstract classmethod, ClassVar, dataclass
  frozen+slots): HIGH — patterns testados empiricamente.
- Pitfalls: HIGH — Pitfall 4 (frozen+slots+dict+eq) é a descoberta
  desta pesquisa, não estava em CONTEXT.
- JSON schema heterogêneo: HIGH — inspecionado o JSON-fonte real.
- Cache idempotência via `cls.__dict__`: HIGH — verificado.
- Mensagens exatas de `TypeError`: HIGH — string capturada do
  interpretador.

**Research date:** 2026-05-05
**Valid until:** 2026-06-04 (30 dias — stack stable, sem deps externas)

---

*Phase 4 — Contratos ABC*
*Research conducted in Python 3.13.13 / `uv` venv ativa em
`/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/.venv`*
