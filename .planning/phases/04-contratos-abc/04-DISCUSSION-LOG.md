# Phase 4: Contratos ABC - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-05
**Phase:** 04-contratos-abc
**Mode:** `--auto` (Claude selected recommended option for every gray area)
**Areas discussed:** Localização do módulo, Forma das ABCs, Atributos de classe, Enums (Scope/ModoFixer), Semântica de carregar_regras, Default de pode_corrigir, Design de aplicar(), Tipos auxiliares (AplicacaoResultado/ContextoFixer), Estratégia de testes

---

## Localização do módulo

| Option | Description | Selected |
|--------|-------------|----------|
| `core/contracts.py` (recommended) | ABCs em arquivo único dentro de `core/`, ao lado de dataclasses/enums | ✓ |
| `core/abc.py` | Mesmo lugar, nome alternativo (conflita visualmente com stdlib `abc`) | |
| `validators/base.py` + `fixers/base.py` | Criar subpacotes vazios agora para acomodar futuras concretas | |

**User's choice (auto):** `core/contracts.py`
**Notes:** YAGNI: subpacotes `validators/` e `fixers/` só nascem em Phase 6/7. Forçar criação preventiva polui o tree. Mantém invariante "core/ = tipos + contratos puros" estabelecido em Phase 3 D-33.

---

## Forma das ABCs

| Option | Description | Selected |
|--------|-------------|----------|
| `abc.ABC` + `@abstractmethod` (recommended) | Enforça `TypeError` em instanciação quando método obrigatório falta | ✓ |
| `typing.Protocol` runtime_checkable | Conformidade estrutural; não bloqueia instanciação | |
| Classe regular com `raise NotImplementedError` em métodos | Sem abc; força runtime check manual | |

**User's choice (auto):** `abc.ABC` + `@abstractmethod`
**Notes:** Roadmap success criterion #1 exige TypeError em instanciação. Protocol não atende; raise NotImplementedError é hack que adia o erro até a primeira chamada.

---

## Definição de `JSON_SOURCE` e `SCOPE` (ValidadorBase)

| Option | Description | Selected |
|--------|-------------|----------|
| `ClassVar[Path]` + helper `_canonical_root()` (recommended) | Tipo Path consistente com Phase 2/3; helper resolve raiz da biblioteca | ✓ |
| `ClassVar[str]` com path literal | Mais simples mas perde tipo Path estabelecido | |
| Property abstract retornando Path | Verbose para um valor estático | |

**User's choice (auto):** `ClassVar[Path]` + `_canonical_root()` helper
**Notes:** mypy strict requer ClassVar explícito. Path consistente com Phase 3 D-11.

---

## Definição de `VIOLACAO_IDS` e `MODO` (FixerBase)

| Option | Description | Selected |
|--------|-------------|----------|
| `ClassVar[frozenset[str]]` (recommended) | Imutável, lookup O(1), seguro contra mutação | ✓ |
| `ClassVar[set[str]]` | Mutável — armadilha de set compartilhado entre instâncias | |
| `ClassVar[tuple[str, ...]]` | Imutável mas lookup O(n) | |

**User's choice (auto):** `ClassVar[frozenset[str]]`
**Notes:** Phase 3 D-07 estabelece "tuple sobre list por imutabilidade gratuita". `frozenset` é equivalente para coleção de IDs com lookup; superior a tuple para `pode_corrigir`.

---

## Enum `Scope` (granularidade do validador)

| Option | Description | Selected |
|--------|-------------|----------|
| Enum em `core/enums.py` com PARAGRAFO/SECAO/DOCUMENTO (recommended) | Mesma convenção D-14/D-20 (Enum string snake_case) | ✓ |
| String literal em `Literal["paragrafo", "secao", "documento"]` | Type-safe mas não enumera símbolos | |
| `IntEnum` com peso/ordem | Mistura ordem com semântica (anti D-16) | |

**User's choice (auto):** Enum em `core/enums.py` (PARAGRAFO/SECAO/DOCUMENTO)
**Notes:** Consistente com Severidade/EstadoPatch. Sem peso() — orchestrator decide ordem por match statement.

---

## Enum `ModoFixer` (nível de intervenção)

| Option | Description | Selected |
|--------|-------------|----------|
| Enum em `core/enums.py` com AUTO/ASSISTIDO/LLM (recommended) | Substitui MODO string livre por tipo enumerado | ✓ |
| String literal | Sem enumeração explícita dos valores válidos | |
| Subclasses específicas (FixerAuto, FixerAssistido, FixerLlm) | Hierarquia rígida demais para a flexibilidade que orchestrator quer | |

**User's choice (auto):** Enum `ModoFixer` (AUTO/ASSISTIDO/LLM)
**Notes:** PROJECT.md Key Decision "3 níveis de fixer" tem 3 valores fixos — enum cabe perfeitamente.

---

## Cache de `carregar_regras()`

| Option | Description | Selected |
|--------|-------------|----------|
| Atributo `cls._regras_compiladas: ClassVar` lazy init (recommended) | Class-level cache explícito, auditável, simples | ✓ |
| `functools.lru_cache` em classmethod | Pode reter cls e criar caches independentes; menos auditável | |
| Sem cache (recompilar a cada chamada) | Viola success criterion #2 (compila 1x) | |

**User's choice (auto):** Atributo class-level lazy init
**Notes:** Phase 2 ParserMd usa padrão similar. Auditável: dá pra inspecionar `cls._regras_compiladas` em testes (success #2 verifica `id()` de retorno).

---

## `carregar_regras` como abstract ou default?

| Option | Description | Selected |
|--------|-------------|----------|
| `@abstractmethod` + helper utilitário `_carregar_json_simples` (recommended) | Subclasse ciente da responsabilidade; helper cobre 90% dos casos | ✓ |
| Default concreto na ABC com cache | Subclasse herda sem reimplementar; mas perde ciência da responsabilidade | |
| Mixin separado | Overengineering — só 60 fases no roadmap | |

**User's choice (auto):** `@abstractmethod` + helper utilitário
**Notes:** VAL-06 (conjunções, 802 entradas, schema diferente) e M3 agregadores (consomem list[Violacao]) precisam de override custom. Manter abstract evita ilusão de "default cobre todos".

---

## Default de `pode_corrigir(v)`

| Option | Description | Selected |
|--------|-------------|----------|
| Concreto na ABC: `v.regra_id in type(self).VIOLACAO_IDS` (recommended) | Cobre success criterion #3 sem boilerplate em cada fixer | ✓ |
| `@abstractmethod` forçando reimplementação | Sem ganho — todo fixer faria a mesma checagem | |
| Decorador `@require_violacao_ids` | Overengineering | |

**User's choice (auto):** Default concreto
**Notes:** Subclasses sobrescrevem só se precisarem refinamento (ex.: filtrar por severidade ou principio_canonico_violado).

---

## Design de `aplicar(patches, modo_interativo)`

| Option | Description | Selected |
|--------|-------------|----------|
| `@abstractmethod` que delega ao PatchAplicador (Phase 5) (recommended) | Single responsibility: ABC declara contrato, PatchAplicador executa | ✓ |
| ABC implementa concreta usando PatchAplicador | Cria dependência ABC→Phase 5; mas PatchAplicador ainda não existe | |
| Sem método `aplicar` na ABC; orchestrator faz tudo | Quebra contrato CORE-05 | |

**User's choice (auto):** `@abstractmethod` delegando
**Notes:** Phase 4 declara assinatura; Phase 5 implementa PatchAplicador; Phase 7 (FXA piloto cst_012) é primeiro consumidor real.

---

## Tipo de retorno de `aplicar`: `AplicacaoResultado`

| Option | Description | Selected |
|--------|-------------|----------|
| Dataclass nova frozen+slots em `contracts.py` (recommended) | Auto-documentado, type-safe, custo zero | ✓ |
| Tuple `(aceitos, rejeitados, suprimidos, bytes)` | Compacto mas ordem-de-arg propenso a erro | |
| `dict[str, Any]` | Sem garantia de campos | |

**User's choice (auto):** Dataclass `AplicacaoResultado`
**Notes:** Convenção Phase 3 D-05 (frozen+slots). 4 campos: patches_aceitos, patches_rejeitados, patches_suprimidos, bytes_modificados.

---

## Argumento `contexto` de `propor_patches`: `ContextoFixer`

| Option | Description | Selected |
|--------|-------------|----------|
| Dataclass nova em `contracts.py` com 3 campos (recommended) | Encapsula paragrafo + violacoes_irmas + regras_compiladas | ✓ |
| 3 args separados | Acoplamento maior, signature mais longa | |
| `dict[str, Any]` opaco | Sem type safety | |

**User's choice (auto):** Dataclass `ContextoFixer`
**Notes:** M3 agregadores precisam ver todas violações do parágrafo (não só `v`). Reusar regras_compiladas evita recompilar.

---

## `from __future__ import annotations` em `contracts.py`

| Option | Description | Selected |
|--------|-------------|----------|
| Sim (recommended) | Permite `re.Pattern[str]` sem import runtime; resolve forward refs | ✓ |
| Não, importar `re` no topo | Funciona mas import desnecessário | |
| `TYPE_CHECKING` block | Verbose para o caso simples atual | |

**User's choice (auto):** `from __future__ import annotations`
**Notes:** Convenção já em `parser/markdown.py`. PEP 563.

---

## Estratégia de testes

| Option | Description | Selected |
|--------|-------------|----------|
| `tests/core/test_contracts.py` + `tests/core/fixtures/*.json` minúsculos (recommended) | Fakes locais, fixtures isoladas do dataset canônico | ✓ |
| Reusar JSONs reais de `02_escrita/` | Testes acoplados a dataset que muda | |
| Mock de `Path.read_text` via monkeypatch | Mais frágil que fixture file | |

**User's choice (auto):** Fakes + fixtures locais
**Notes:** 4 success criteria + 3 testes de erro (FileNotFoundError, JSONDecodeError, re.error). Coverage alvo 95%.

---

## Claude's Discretion

- Texto exato de docstrings PT-BR (manter convenção do projeto).
- Estrutura interna dos testes (parametrize vs separado).
- Decisão por validador concreto sobre flags de `re.compile` (UNICODE vs UNICODE|IGNORECASE).
- `__repr__` customizado para `AplicacaoResultado` / `ContextoFixer` se logs ficarem poluídos.

## Deferred Ideas

- State machine enforcement em `EstadoPatch` (Phase 51).
- Subclasse `ValidadorAgregadoBase` (Phase 18 se necessário).
- Async `validar`/`propor_patches` (out of scope — zero rede em validadores).
- Plugin system com discovery dinâmico (out of scope — registro estático em Phase 50 basta).
- `ValidadorBase.versao()` retornando versão do JSON-fonte (Phase 20 AGR-03).
- `FixerBase.confianca_minima` ClassVar (Phase 49 FXL-08).

---

*Auto-resolved 2026-05-05 by `/gsd-discuss-phase 4 --auto`*
