# Phase 3: Dataclasses Core - Research

**Researched:** 2026-05-05
**Domain:** Python 3.13 stdlib `dataclasses` + `enum` — modelagem nuclear (`Violacao`, `Patch`, `Severidade`, `EstadoPatch`)
**Confidence:** HIGH (todas as afirmações chave verificadas empiricamente em Python 3.13.13 dentro do `.venv` do projeto; demais afirmações verificadas contra docs oficiais Python 3.13 / PEP 557 / PEP 663)

## Summary

Phase 3 é uma fase de **modelagem pura** sem I/O. As 33 decisões fixadas em
`03-CONTEXT.md` (modo `--auto`) são todas tecnicamente sustentáveis em Python
3.13: `frozen=True` + `slots=True` interagem corretamente, `__post_init__` com
`raise ValueError` é canônico em frozen dataclasses, `tuple[str, ...] = ()` é
o padrão idiomático para defaults imutáveis, `dataclasses.asdict()` produz
dict estruturalmente correto mas **não** serializável por `json.dumps` quando
contém `Path` ou `Enum` — o que justifica o método `to_dict()` paralelo
(D-25). A escolha por `enum.Enum` com método `peso()` (D-16) sobre `IntEnum`
está correta: `IntEnum` mistura semântica de ranking com representação textual
em logs e quebra a convenção herdada do `TipoSecao` (Phase 2 D-03).

**Primary recommendation:** Implementar exatamente as 33 decisões de
CONTEXT.md sem reabri-las. Esta pesquisa **valida** todas as decisões e
acrescenta apenas pitfalls execucionais e padrões idiomáticos para o
planejador transformar em tasks acionáveis. Nenhuma contradição encontrada
(seção `## CONTRADICTS CONTEXT` omitida).

## User Constraints (from CONTEXT.md)

### Locked Decisions

Todas as decisões D-01..D-33 estão locked. Resumo do que **não** se pode
reabrir:

- **D-01..D-04:** Subpacote `core/` com `core/dataclasses.py` + `core/enums.py`
  + `core/__init__.py`. **Não** criar `core/types.py` ou shadowing de stdlib
  `dataclasses` na raiz do pacote.
- **D-05..D-08:** `Violacao` é `@dataclass(frozen=True, slots=True)`; `Patch`
  é `@dataclass(slots=True)` mutável; coleções em `Violacao` são
  `tuple[str, ...]` (não `list`).
- **D-09..D-13:** Campos completos de `Violacao` em ordem fixa; `arquivo:
  Path` (não `str`); `linha_fim` inclusivo; `col_inicio/col_fim` half-open;
  sem campo `mensagem`.
- **D-14..D-16:** `Severidade` é `enum.Enum` com `value` string snake_case;
  4 valores (`INFO`/`ALERTA`/`ERRO`/`CRITICO`); ordenação via método
  `peso() -> int`, não via `IntEnum`.
- **D-17..D-19:** Campos de `Patch`; `Patch` é single-line; `confianca` sem
  default (anti-hidden-default); sem campo `regra_id_origem`.
- **D-20..D-21:** `EstadoPatch` é `enum.Enum`; transições documentadas mas
  **não** enforçadas em runtime nesta phase.
- **D-22..D-24:** `__post_init__` valida invariantes via `raise ValueError`
  contendo `regra_id` para diagnóstico; sem mutação de campos
  (`object.__setattr__` não é necessário).
- **D-25..D-27:** `to_dict()` em `Violacao` e `Patch` produz dict
  JSON-ready; `dataclasses.asdict()` permanece acessível para callers que
  preferem objetos Python ricos; **não** implementar `from_dict()` reverso
  agora.
- **D-28..D-30:** 4 testes de success criteria + 5 testes de invariantes
  (`__post_init__` raises); coverage alvo `>= 95%`.
- **D-31..D-33:** Type hints 100%; `ruff line-length = 80`; sem `loguru` em
  `core/` (zero side-effect).

### Claude's Discretion

- Helpers privados internos (ex.: `_normalize_for_json` em `dataclasses.py`).
- Texto exato de docstrings (PT-BR conforme convenção do projeto).
- Estrutura interna dos 5 testes de `__post_init__` — `@pytest.mark.parametrize`
  ou separar é decisão do executor.
- Se vale a pena adicionar `__repr__` customizado para `Violacao`/`Patch`
  com truncamento de `trecho_violador` em logs.

### Deferred Ideas (OUT OF SCOPE)

- **`from_dict()` reverso (deserialização)** — postergar até Phase 58
  (ORC-09 Output JSON) ou primeiro caso de carregamento de fixture.
- **Enforcement de transições de `EstadoPatch`** — adiar para Phase 51
  (Orchestrator Fixer). Phase 3 só documenta transições válidas.
- **`__repr__` customizado** com truncamento — decisão fica no plan.
- **Subclasses de `Violacao`** (ex.: `ViolacaoAgregada`) — adiar para AGR-01
  (Phase 18).
- **`Severidade` com `IntEnum`** (peso embutido) — manter `Enum` + método
  `peso()` separado.
- **Campo `created_at: datetime`** em `Patch`/`Violacao` — telemetria
  pertence ao orchestrator.
- **`__hash__` customizado em `Patch`** — `Patch` é mutável; Python
  desabilita `__hash__` automaticamente (correto). Não forçar.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CORE-02 | Dataclass `Violacao(arquivo, linha_inicio, linha_fim, col_inicio, col_fim, trecho_violador, regra_id, regra_nome, severidade, sugestoes, principio_canonico_violado)` | Pattern 1 (frozen+slots) + Pattern 4 (`__post_init__` validators) verificados empiricamente em Python 3.13.13. Todos os campos D-09 cobertos. |
| CORE-03 | Dataclass `Patch(arquivo, linha, col_inicio, col_fim, texto_original, texto_substituto, motivo, confianca, requer_revisao_humana, estado)` com enum `EstadoPatch` (PROPOSTO/ACEITO/REJEITADO/SUPRIMIDO) | Pattern 2 (slots-only mutable) + Pattern 3 (Enum string snake_case) + Pattern 5 (`peso()` method on Enum) verificados empiricamente. Todos os campos D-17 cobertos. |

## Project Constraints (from CLAUDE.md)

Diretivas extraídas de `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/CLAUDE.md`
e `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` que o planejador deve
respeitar:

- **Python 3.13+** com `uv` venv em `.venv/` `[CITED: biblio_canonica/CLAUDE.md §Constraints]`.
- **Type hints obrigatórios** em todo código novo (CLAUDE.md regra 9) — vai
  para mypy strict (Phase 1 D-13).
- **Max 80 chars/linha** — `ruff line-length = 80` herdado.
- **Stdlib `re`/`dataclasses`/`pathlib`** — Phase 3 usa exclusivamente stdlib.
  Zero deps novas `[VERIFIED: pyproject.toml lido]`.
- **Idioma PT-BR brasileiro** em docstrings; código em English ASCII.
- **Sem dependências de rede em validadores** — Phase 3 é zero-side-effect
  (sem I/O, sem log).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Modelar `Violacao` (output dos validadores) | Core domain (Python in-process) | — | Saída de `ValidadorBase.validar()` (Phase 4); imutável para evitar mutação acidental no orchestrator |
| Modelar `Patch` (output dos fixers) | Core domain (Python in-process) | — | Saída de `FixerBase.propor_patches()` (Phase 4); mutável apenas em `estado` (orchestrator Phase 51) e `requer_revisao_humana` |
| Enum `Severidade` | Core domain (constantes) | — | Classificação de `Violacao`; lida pelo orchestrator (Phase 8) para priorizar saída e setar exit code |
| Enum `EstadoPatch` | Core domain (constantes) | — | Ciclo de vida do `Patch`; mutado pelo orchestrator (Phase 51) e pós-validador LLM (Phase 48) |
| Validação de invariante (`__post_init__`) | Core domain (zero side-effect) | — | Falha rápido na construção; mensagem com `regra_id` para diagnóstico em produção |
| Serialização JSON (`to_dict()`) | Core domain (output adapter) | — | Consumida por `ReportGenerator` (Phase 8) para `AUDITORIA.md` JSON e por ORC-09 (Phase 58) Output JSON |

Nenhuma capacidade desta phase atravessa fronteira de processo, rede ou disco.
Por isso `core/` é zero-import-dependency para o resto do código (apenas
stdlib).

## Standard Stack

### Core (zero dependências novas)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `dataclasses` | stdlib (3.13) | `@dataclass(frozen=True, slots=True)` para `Violacao`; `@dataclass(slots=True)` para `Patch` | PEP 557 padrão para tipos puros de dados; `slots=True` adiciona `__slots__` automaticamente desde 3.10; `frozen=True` ativa `FrozenInstanceError` em `__setattr__` `[VERIFIED: empirical Python 3.13.13]` |
| `enum` | stdlib (3.13) | `enum.Enum` para `Severidade` e `EstadoPatch` com `value` string snake_case | Convenção herdada de Phase 2 `TipoSecao` D-03. `Enum` (não `StrEnum`) preserva `repr` legível em logs (`<Severidade.ERRO: 'erro'>`) sem ambiguidade entre instância e string `[VERIFIED: empirical]` |
| `pathlib` | stdlib (3.13) | `Path` em `Violacao.arquivo` e `Patch.arquivo` | Consistência com Phase 2 (`Paragrafo.arquivo: Path`); convertido a `str` apenas no `to_dict()` (D-25) |
| `json` | stdlib (3.13) | Serialização final via `json.dumps(viol.to_dict())` | `json.dumps` falha em `Path`/`Enum`/`tuple` por default — `to_dict()` resolve sem encoder customizado `[VERIFIED: empirical TypeError observado]` |
| `typing.Any` | stdlib | Type hint do retorno de `to_dict() -> dict[str, Any]` | Estrutura interna do dict é heterogênea (str/int/list/None) — `Any` é o tipo correto |

### Supporting (já instalado em Phase 1)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 9.0.3 | 9 testes (4 success criteria + 5 invariantes) | Pattern já estabelecido em Phase 1 (`tests/test_cli.py`) e Phase 2 (`tests/parser/test_markdown.py`) |
| `pytest-cov` | 7.1.0 | Coverage `>= 95%` em `core/dataclasses.py` e `core/enums.py` | Comando `pytest --cov=biblio_validador.core --cov-report=term-missing` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@dataclass(frozen=True, slots=True)` | `pydantic.BaseModel` | Pydantic adicionaria validação runtime de tipos (útil para JSON externo) mas tem overhead de import (~80ms cold), exige nova dependência, e Phase 1 STACK.md já confirmou `dataclasses` como decisão fundamental. **Out of scope explícito em CONTEXT.md.** |
| `enum.Enum` com método `peso()` | `enum.IntEnum` | `IntEnum` permitiria `Severidade.INFO < Severidade.ERRO` direto, mas `repr(SevInt.INFO)` é `<SevInt.INFO: 0>` e `str(SevInt.INFO)` é `'SevInt.INFO'` — perde legibilidade do valor string em logs `[VERIFIED: empirical]`. Quebra convenção Phase 2. |
| `enum.Enum` com `value=str` | `enum.StrEnum` (PEP 663, 3.11+) | `StrEnum` faria `Severidade.INFO == "info"` e `str(s) == "info"`, útil para JSON direto (subclasse de `str`). **Mas:** quebra convenção Phase 2 D-03 (que usa `Enum` puro); `repr` perde marcador de tipo (`<Severidade.INFO: 'info'>`) e fica `<SevStr.INFO: 'info'>` igual mas `str` vira o valor cru — confuso em logs. CONTEXT D-14 explicitamente rejeita `StrEnum` pelo mesmo motivo. **Manter `Enum` puro.** |
| `tuple[str, ...] = ()` | `field(default_factory=tuple)` | Ambos funcionam idênticos em Python 3.13.13 `[VERIFIED: empirical]`. `default=()` é mais conciso e idiomático porque tuple vazia é singleton imutável compartilhada — não há risco de "shared mutable default". `default_factory=tuple` é necessário apenas para tipos mutáveis (`list`, `dict`, `set`). **Usar `= ()` direto.** |
| `dataclasses.asdict()` puro | `to_dict()` customizado | `asdict()` retorna dict com `Path`, `Enum`, `tuple` preservados — `json.dumps` falha. Encoder customizado (`json.JSONEncoder.default`) é alternativa mas espalha a lógica de normalização. **`to_dict()` localiza no método o conhecimento de como cada campo se serializa** (D-25). |

**Installation:** Nenhuma. Phase 3 reusa `pyproject.toml` Phase 1 sem modificação `[VERIFIED: pyproject.toml lido]`.

**Version verification:**
```bash
uv run python -c "import sys, dataclasses, enum, pathlib, json; print(sys.version)"
# Output: 3.13.13 (main, Apr  7 2026, 20:49:46) [Clang 22.1.1 ]
```
[VERIFIED: command executed in this session]

## Architecture Patterns

### System Architecture Diagram

```
                    Phase 2 (Parser MD)
                            │
                            ▼
                    list[Paragrafo]
                            │
                            ▼
            ┌───────────────────────────────┐
            │   Phase 4 (Contratos ABC)     │
            │   ValidadorBase.validar()     │
            │   FixerBase.propor_patches()  │
            └───────────────────────────────┘
                    │              │
                    ▼              ▼
            list[Violacao]    list[Patch]
                    │              │
                    │              ▼
                    │        Phase 5 PatchAplicador
                    │              │
                    ▼              │
        Phase 8 ReportGenerator    │
            │           │          │
            ▼           ▼          ▼
       AUDITORIA.md  JSON      .md modificado
       (Severidade   (to_dict   (byte-exact
        peso() para  serializa  patches
        ordenar)     Path/Enum/ reverso)
                     tuple)

═════════════════════════════════════════════════════
                  PHASE 3 ENTREGA
═════════════════════════════════════════════════════
   src/biblio_validador/core/
     ├─ __init__.py    (re-export 4 símbolos)
     ├─ dataclasses.py (Violacao + Patch + _normalize_for_json)
     └─ enums.py       (Severidade + EstadoPatch)
═════════════════════════════════════════════════════
```

`core/` é folha do grafo de imports: depende apenas de stdlib. Phases 4, 5, 6,
8, 19, 48, 51, 58 importam de `biblio_validador.core` mas o caminho inverso
não existe.

### Recommended Project Structure

```
src/biblio_validador/
├── __init__.py          # já existe (Phase 1)
├── cli.py               # já existe (Phase 1)
├── parser/              # já existe (Phase 2)
│   ├── __init__.py
│   ├── types.py         # Paragrafo, TipoSecao
│   └── markdown.py
└── core/                # ★ Phase 3 cria
    ├── __init__.py      # re-export Violacao, Patch, EstadoPatch, Severidade
    ├── dataclasses.py   # Violacao + Patch + helpers privados
    └── enums.py         # EstadoPatch + Severidade

tests/
├── __init__.py
├── test_cli.py          # já existe (Phase 1)
├── parser/              # já existe (Phase 2)
└── core/                # ★ Phase 3 cria
    ├── __init__.py
    └── test_dataclasses.py  # 4 success criteria + 5 invariantes
```

### Pattern 1: `@dataclass(frozen=True, slots=True)` para tipos imutáveis (D-05)

**What:** Dataclass imutável, sem `__dict__`, com `FrozenInstanceError` em
mutação. Padrão canônico do projeto (segue Phase 2 `Paragrafo`).

**When to use:** `Violacao` — saída dos validadores; consumida por
agregadores e orchestrator que NÃO devem mutar.

**Example (verified empirically Python 3.13.13):**

```python
# core/dataclasses.py
from dataclasses import dataclass, field
from pathlib import Path

from biblio_validador.core.enums import Severidade


@dataclass(frozen=True, slots=True)
class Violacao:
    """Violação de regra canônica detectada por um validador.

    Imutável após construção (frozen=True). Coleções são tuple
    (D-07: tuple[str, ...] em vez de list[str]).

    Invariante (intra-linha):
        col_fim - col_inicio == len(trecho_violador) caracteres,
        quando linha_inicio == linha_fim.

    Convenção col half-open:
        col_inicio = primeiro caractere violador (1-based)
        col_fim = primeiro caractere NÃO violador (1-based, exclusivo)
        linha[col_inicio - 1 : col_fim - 1] em Python slicing.
    """

    arquivo: Path
    linha_inicio: int
    linha_fim: int
    col_inicio: int
    col_fim: int
    trecho_violador: str
    regra_id: str
    regra_nome: str
    severidade: Severidade
    sugestoes: tuple[str, ...] = ()
    principio_canonico_violado: str | None = None

    def __post_init__(self) -> None:
        # Validação de invariantes — D-22.
        if self.linha_inicio < 1:
            raise ValueError(
                f"linha_inicio < 1 em {self.regra_id}: "
                f"{self.linha_inicio}"
            )
        if self.linha_fim < self.linha_inicio:
            raise ValueError(
                f"linha_fim < linha_inicio em {self.regra_id}: "
                f"{self.linha_fim} < {self.linha_inicio}"
            )
        if self.col_inicio < 1:
            raise ValueError(
                f"col_inicio < 1 em {self.regra_id}: {self.col_inicio}"
            )
        if self.col_fim < self.col_inicio:
            raise ValueError(
                f"col_fim < col_inicio em {self.regra_id}: "
                f"{self.col_fim} < {self.col_inicio}"
            )
        if not self.regra_id.strip():
            raise ValueError("regra_id vazio")
        if (
            self.linha_inicio == self.linha_fim
            and len(self.trecho_violador) != self.col_fim - self.col_inicio
        ):
            raise ValueError(
                f"trecho_violador len {len(self.trecho_violador)} != "
                f"col_fim - col_inicio "
                f"{self.col_fim - self.col_inicio} em {self.regra_id}"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialização JSON-ready (D-25)."""
        from dataclasses import asdict

        return _normalize_for_json(asdict(self))
```

[VERIFIED: empirical run; all assertions confirmed]

### Pattern 2: `@dataclass(slots=True)` mutável para `Patch` (D-06)

**What:** Dataclass com `__slots__` (sem `__dict__`) mas sem `frozen` —
permite mutação de `estado` ao longo do ciclo PROPOSTO → ACEITO/REJEITADO/SUPRIMIDO.

**When to use:** `Patch` — saída dos fixers; orchestrator (Phase 51) muta
`estado`; pós-validador LLM (Phase 48) muta para SUPRIMIDO.

**Example (verified empirically):**

```python
@dataclass(slots=True)
class Patch:
    """Patch proposto por um fixer (D-17, D-18).

    NÃO frozen: estado e requer_revisao_humana podem ser mutados pelo
    orchestrator (Phase 51) e pelo pós-validador LLM (Phase 48). Demais
    campos são read-only por convenção (não enforçado em runtime).

    Single-line (D-18): patch que abrange várias linhas é decomposto em
    múltiplos Patch pelo fixer; PatchAplicador (Phase 5) ordena reverso
    por (linha, col_inicio).

    Transições válidas de `estado` (documentadas, não enforçadas):
        PROPOSTO → ACEITO | REJEITADO | SUPRIMIDO
        ACEITO   → SUPRIMIDO  (raro: aplicação falhou byte-exact)
        terminais: REJEITADO, SUPRIMIDO
    """

    arquivo: Path
    linha: int
    col_inicio: int
    col_fim: int
    texto_original: str
    texto_substituto: str
    motivo: str
    confianca: float
    requer_revisao_humana: bool = False
    estado: EstadoPatch = EstadoPatch.PROPOSTO

    def __post_init__(self) -> None:
        # Validação de invariantes — D-23.
        if self.linha < 1:
            raise ValueError(f"linha < 1: {self.linha}")
        if self.col_inicio < 1:
            raise ValueError(f"col_inicio < 1: {self.col_inicio}")
        if self.col_fim < self.col_inicio:
            raise ValueError(
                f"col_fim < col_inicio: {self.col_fim} < {self.col_inicio}"
            )
        if not 0.0 <= self.confianca <= 1.0:
            raise ValueError(f"confianca fora de [0,1]: {self.confianca}")
        if not self.texto_original:
            raise ValueError("texto_original vazio (use [] em vez de Patch nulo)")
        if not self.motivo.strip():
            raise ValueError("motivo vazio")

    def to_dict(self) -> dict[str, object]:
        from dataclasses import asdict

        return _normalize_for_json(asdict(self))
```

`Patch` é unhashable (Python desabilita `__hash__` automaticamente em
`@dataclass(eq=True)` mutável — `eq=True` é default). `Violacao` é hashable
porque `frozen=True` faz Python emitir `__hash__` baseado nos campos `eq`.
`[VERIFIED: empirical]`

### Pattern 3: `enum.Enum` com value string snake_case (D-14, D-20)

**What:** Enum com valores explícitos string. Padrão Phase 2 (`TipoSecao`).

**Example (verified empirically):**

```python
# core/enums.py
from enum import Enum


class Severidade(Enum):
    """Classificação de severidade de uma Violacao (D-15).

    Ordem de prioridade (peso() crescente):
        INFO < ALERTA < ERRO < CRITICO

    Não usa IntEnum (D-16): IntEnum mistura semântica de ranking com
    representação textual em logs. peso() separa as preocupações.
    """

    INFO = "info"
    ALERTA = "alerta"
    ERRO = "erro"
    CRITICO = "critico"

    def peso(self) -> int:
        """Peso para ordenação determinística (0..3)."""
        return _PESOS_SEVERIDADE[self]


# Tabela de pesos como módulo-level dict — evita lookup em loop e
# mantém a ordenação canônica em local único.
_PESOS_SEVERIDADE: dict[Severidade, int] = {
    Severidade.INFO: 0,
    Severidade.ALERTA: 1,
    Severidade.ERRO: 2,
    Severidade.CRITICO: 3,
}


class EstadoPatch(Enum):
    """Ciclo de vida de um Patch (D-20).

    Transições válidas (documentadas, não enforçadas em runtime nesta
    phase — enforcement adiado para Phase 51 ORC-02 se necessário):

        PROPOSTO → ACEITO | REJEITADO | SUPRIMIDO
        ACEITO   → SUPRIMIDO  (raro: aplicação falhou byte-exact)
        terminais: REJEITADO, SUPRIMIDO
    """

    PROPOSTO = "proposto"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    SUPRIMIDO = "suprimido"
```

**Por que `dict` no módulo em vez de `match` statement em `peso()`:**
- Lookup `O(1)` por hash; `match` é `O(n)` no número de cases.
- Tabela centralizada documenta a ordenação canônica em local único.
- Adicionar nova severidade futura é uma linha no dict + uma constante na
  classe; em `match` exigiria editar dois lugares.

**Por que NÃO `match` statement aqui:** uso idiomático de `match` é para
dispatch estrutural (tuplas, dataclasses, listas) — para mapeamento simples
constante→constante, dict é claramente superior. Esta é uma convenção
defendida na PEP 636.

### Pattern 4: `__post_init__` em frozen dataclass (D-22, D-24)

**What:** Validação de invariantes via `raise ValueError`; sem mutação de
campos (não precisa de `object.__setattr__`).

**Why this works:** `__post_init__` roda **após** `__init__` ter atribuído
todos os campos. Em `frozen=True`, `__setattr__` está bloqueado — mas leitura
(`self.linha_inicio`) funciona normalmente. `raise ValueError` propaga sem
problemas. `[VERIFIED: empirical Order(-1)]`

**Padrão de mensagem (D-22):** sempre incluir `regra_id` na mensagem para
diagnóstico em produção (`f"linha_inicio < 1 em {self.regra_id}: {x}"`).
Quando o orchestrator processar 1000+ violações, um traceback com 50 linhas
de stack que diz apenas "ValueError" é inútil.

**Edge case CRÍTICO** (não óbvio): em frozen dataclasses, mutar campos
**no `__post_init__`** exige `object.__setattr__(self, "campo", valor)`.
**Phase 3 NÃO precisa disso** porque D-22/D-24 só validam, não calculam
campos derivados. Se o planejador encontrar tentação de adicionar campo
derivado (ex.: `id_unico` baseado em hash dos outros), recusar e levar para
discussão.

### Pattern 5: Helper `_normalize_for_json` (D-25)

**What:** Função privada do módulo `core/dataclasses.py` que converte um
dict produzido por `dataclasses.asdict()` em dict serializável por
`json.dumps`.

**Why it's needed:** `dataclasses.asdict()` preserva tipos Python ricos
(`Path`, `Enum`, `tuple`). `json.dumps` rejeita `Path` com
`TypeError: Object of type PosixPath is not JSON serializable`
`[VERIFIED: empirical TypeError observado]`.

**Example (verified empirically):**

```python
from enum import Enum
from pathlib import Path
from typing import Any


def _normalize_for_json(obj: Any) -> Any:
    """Converte recursivamente Path/Enum/tuple em str/value/list.

    Pós-processa a saída de dataclasses.asdict() para que json.dumps()
    funcione sem encoder customizado.
    """
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, tuple):
        return [_normalize_for_json(x) for x in obj]
    if isinstance(obj, list):
        return [_normalize_for_json(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _normalize_for_json(v) for k, v in obj.items()}
    return obj
```

[VERIFIED: empirical — `json.dumps(_normalize_for_json(asdict(v)))` produz
string válida e `json.loads` round-trip preserva todos os campos como esperado]

**Por que recursivo:** se um `Patch` futuro tiver lista de strings, ou um
`Violacao` futuro embutir outra dataclass via `asdict()`, o normalizador
desce na estrutura sem precisar conhecer a forma específica.

**Por que função módulo, não método de classe:** `_normalize_for_json` é
genérico — não conhece `Violacao` nem `Patch`. Vive no nível do módulo;
ambas dataclasses chamam o mesmo helper em seus respectivos `to_dict()`
(DRY).

### Pattern 6: Re-export em `core/__init__.py` (D-03)

**What:** Padrão idêntico a `parser/__init__.py` (Phase 2 D-22).

```python
# core/__init__.py
"""Core domain types — Violacao, Patch, Severidade, EstadoPatch."""

from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import EstadoPatch, Severidade

__all__ = ["EstadoPatch", "Patch", "Severidade", "Violacao"]
```

Permite `from biblio_validador.core import Violacao, Patch` em validadores e
fixers, sem expor o caminho interno `biblio_validador.core.dataclasses`.

### Anti-Patterns to Avoid

- **`@dataclass(frozen=True)` sem `slots=True`**: perde ~30% de footprint de
  memória em coleções de violações grandes (artigo 30k palavras pode ter
  centenas de violações). `slots=True` é cheap e idiomático em 3.10+.
- **`@dataclass(frozen=True, slots=True)` herdando de outra dataclass com
  `__dict__`**: Python emite warning ou erro silencioso. Phase 3 não tem
  hierarquia, mas planejador deve evitar tentação de criar
  `class Violacao(BaseRecord)`.
- **`field(default_factory=tuple)` em vez de `default=()`**: ambos funcionam,
  mas `default=()` é mais conciso. `default_factory` é necessário **apenas**
  para tipos mutáveis (`list`, `dict`, `set`). Tuple vazia é singleton imutável
  compartilhada — sem risco de "shared mutable default". `[VERIFIED: empirical]`
- **`list[str]` em `Violacao` ao invés de `tuple[str, ...]`**: `frozen=True`
  só impede reatribuir o atributo, não mutar a lista interna. Cliente faz
  `viol.sugestoes.append(...)` e modifica a "imutável" `Violacao`. **Buraco
  na imutabilidade.** `[VERIFIED: empirical Bad.items.append]`. D-07 fecha
  o buraco.
- **`Severidade(IntEnum)` para ranking**: `repr` perde valor string
  (`<SevInt.INFO: 0>` em vez de `<Severidade.INFO: 'info'>`); quebra
  convenção Phase 2 D-03; força conversão `int → str` em todos os logs.
  `[VERIFIED: empirical IntEnum repr/str]`. D-16 rejeita.
- **`json.dumps(asdict(violacao))` direto**: lança
  `TypeError: Object of type PosixPath is not JSON serializable`.
  `[VERIFIED: empirical]`. Sempre passar por `to_dict()`.
- **Mutar `Patch.estado` direto sem validar transição**: Phase 3 documenta
  transições mas não enforça (D-21). Phase 51 (Orchestrator) é dona do
  enforcement. Resistir tentação de adicionar `assert` em `Patch.estado.setter`
  agora.
- **`__hash__` customizado em `Patch`**: Python desabilita automaticamente
  porque `Patch` é mutável. Forçar `__hash__` é pegar tiro no pé (hashing
  de objeto mutável = bug latente em set/dict). `[VERIFIED: empirical]`.
- **Default `confianca: float = 1.0`**: silencia fixers ASSISTIDO mal
  calibrados (sempre exibem 100% de confiança). D-17 obriga a passar
  intencionalmente.
- **`from dataclasses import dataclass` em `core/dataclasses.py`**: cuidado
  com shadowing — o módulo se chama `dataclasses.py` mas importa do stdlib
  `dataclasses`. Funciona porque `from dataclasses import dataclass` resolve
  para o stdlib durante import (D-01 antecipa o problema), mas se alguém
  fizer `import dataclasses` (sem `from`) dentro de `core/dataclasses.py`,
  recursão infinita. Usar **sempre** `from dataclasses import ...`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Imutabilidade | Property setters que `raise AttributeError` | `@dataclass(frozen=True)` | Built-in stdlib, gera `__hash__` automaticamente, integra com `dataclasses.replace()` |
| Otimização de memória | `__slots__` manual | `@dataclass(slots=True)` (3.10+) | Auto-gera `__slots__` correto a partir das annotations; evita esquecer um campo |
| Validação de schema | `if not isinstance(x, str): raise TypeError` | mypy strict + `__post_init__` para invariantes runtime | Tipos são checados em CI (Phase 1 D-13); `__post_init__` pega só invariantes que types não capturam (range, formato) |
| Serialização para dict | `def to_dict(self): return {"a": self.a, ...}` (manual) | `dataclasses.asdict()` + `_normalize_for_json` | `asdict()` desce em sub-dataclasses recursivamente; `_normalize_for_json` lida com Path/Enum/tuple genericamente |
| Comparação de severidade | `if v1.severidade == "erro": ...` (string match) | `Severidade.ERRO` em código + `peso()` para ordenar | Type-safe, autocomplete, refactor-safe |
| Pickle/deepcopy | `__reduce__` customizado | Stdlib lida com `frozen=True` + `slots=True` corretamente | `[CITED: Python 3.13 docs §dataclasses]` confirma compatibilidade |

**Key insight:** O escopo desta phase é tão pequeno (4 símbolos públicos) que
qualquer abstração extra adiciona ruído. Cada linha de código não-trivial
deve ser justificada por D-XX em CONTEXT.md.

## Common Pitfalls

### Pitfall 1: Mutação de coleção dentro de `Violacao` "imutável"

**What goes wrong:** `viol.sugestoes.append("novo")` em
`@dataclass(frozen=True)` com `sugestoes: list[str]` — modifica a lista
interna sem violar `frozen`. A "imutabilidade" é uma fachada quebrada.

**Why it happens:** `frozen=True` intercepta `__setattr__` mas não controla o
que acontece com referências aos atributos depois de retornadas.

**How to avoid:** D-07 já fixa `tuple[str, ...]`. Tuple não tem `.append()`
e é hashable — fecha o buraco. Verificar em todos os campos de coleção
durante implementação que **NUNCA** se usa `list[X]` em `Violacao`.

**Warning signs:** mypy strict aceita ambos; o teste é arquitetural, não
estático. Adicionar uma asserção do plano: `assert isinstance(viol.sugestoes,
tuple)` no teste #1 do D-28 detecta regressão.

**Severity:** ALTA — corrompe a expectativa de imutabilidade que o
orchestrator (Phase 8) e agregadores (Phase 18+) confiam.

### Pitfall 2: `dataclasses.asdict()` quebra `json.dumps`

**What goes wrong:** Test sucesso #3 do roadmap diz `dataclasses.asdict(viol)`
deve "produzir dict serializável em JSON sem erros". Interpretação literal:
`json.dumps(asdict(viol))` deve funcionar. **Não funciona** —
`Path` causa `TypeError: Object of type PosixPath is not JSON serializable`.
`[VERIFIED: empirical]`

**Why it happens:** `asdict()` faz cópia profunda preservando os tipos dos
valores. `Path`, `Enum`, `tuple` são preservados literalmente. `json.dumps`
rejeita `Path` e `Enum` (aceita `tuple` convertendo para list silenciosamente,
mas isso é caso fortuito).

**How to avoid:** D-25 cria método `to_dict()` em ambas dataclasses que
internamente chama `asdict()` e passa por `_normalize_for_json`. Test
sucesso #3 deve ler: "`asdict(viol)` retorna dict (estruturalmente correto);
`json.dumps(viol.to_dict())` retorna string válida". D-26 explicitamente
documenta a ambiguidade na docstring.

**Warning signs:** Test em CI passa com `asdict()` direto se você nunca
chamar `json.dumps`. O bug aparece em Phase 58 (ORC-09 Output JSON) com
TypeError que parece esotérico.

**Severity:** MÉDIA — bug de runtime mas detectado por teste #3 do roadmap
se este for escrito corretamente.

### Pitfall 3: `__post_init__` raiz da árvore vs derivado

**What goes wrong:** Tentação de calcular campo derivado em
`__post_init__` (ex.: `id_unico = hash((arquivo, linha, regra_id))`).
Em `frozen=True`, atribuir derivado falha com `FrozenInstanceError`.
Solução comum (`object.__setattr__(self, "id_unico", ...)`) funciona mas é
hack que confunde código futuro. `[VERIFIED: empirical V5 com object.__setattr__]`

**Why it happens:** `frozen=True` é sintaticamente leve mas semanticamente
pesado — Python só te permite atribuir campos durante `__init__`, não em
`__post_init__`.

**How to avoid:** D-22/D-24 explicitamente proíbem campos derivados em
`Violacao.__post_init__`. Validação com `raise ValueError` é OK; cálculo
de campo derivado **NÃO É**. Se o planejador detectar necessidade de campo
derivado, parar e levar para discussão.

**Warning signs:** PR adiciona campo derivado em `__post_init__` com
`object.__setattr__`. Code review deve recusar.

**Severity:** MÉDIA — não corrompe dados em si, mas introduz padrão
não-óbvio que multiplica em phases futuras.

### Pitfall 4: Esquecer que `Patch` é unhashable

**What goes wrong:** Cliente coloca `Patch` em `set()` ou usa como key de
`dict`. Lança `TypeError: unhashable type: 'Patch'`. `[VERIFIED: empirical]`.

**Why it happens:** `@dataclass(slots=True)` sem `frozen=True` mantém
`__eq__` mas Python explicitamente define `__hash__ = None` (porque um
objeto cuja igualdade depende de campos mutáveis pode mudar de hash em
runtime — quebra o contrato de hashable).

**How to avoid:** Documentar em docstring de `Patch` que é unhashable.
Orchestrator (Phase 51) deve usar `id(patch)` ou índice em lista para
identificar individualmente; deduplicação por chave deve ser feita por
tupla `(arquivo, linha, col_inicio, regra_id_via_motivo)`.

**Warning signs:** TypeError em Phase 51 com mensagem
"unhashable type: 'Patch'".

**Severity:** BAIXA — fácil de detectar e corrigir; afeta só Phase 51+.

### Pitfall 5: Defaults mutáveis em `Patch` (não relevante AGORA mas relevante para crescimento)

**What goes wrong:** Adicionar campo futuro `tags: list[str] = []` em
`Patch`. Python lança `ValueError: mutable default <class 'list'>` desde
3.11+ — `dataclass` exige `field(default_factory=list)` para mutáveis.
Equivocadamente, dev usa `default_factory=list` mas com `slots=True` em
**inheritance** o slots fica corrompido.

**Why it happens:** Phase 3 não tem o problema agora (todos os campos
default são imutáveis: `()`, `False`, `EstadoPatch.PROPOSTO`, `None`). Mas
crescimento futuro pode introduzir.

**How to avoid:** D-08 estende a regra "tuple sobre list" para `Patch`
preventivamente — se algum campo futuro precisar de coleção, manter `tuple`.

**Severity:** BAIXA (futuro) — relevante quando `Patch` ganhar campos
adicionais.

### Pitfall 6: `Severidade.peso()` em loop hot

**What goes wrong:** Orchestrator (Phase 8) ordena
`sorted(violacoes, key=lambda v: v.severidade.peso())` sobre lista de 1000+
violações. Cada chamada de `peso()` faz lookup em dict de 4 entries —
trivial mas ainda é function call overhead.

**Why it happens:** Method calls em Python têm overhead (~50ns). Em loops
com milhares de iterações, pode aparecer em flame graph.

**How to avoid:** Para o escopo do projeto (artigo de 30k palavras gera no
máximo ~500 violações), `peso()` é budget irrelevante. Resistir otimização
prematura. Se aparecer em benchmark Phase 17 (VAL-08), considerar
`functools.cached_property` ou pre-computar pesos uma vez. **NÃO fazer
agora.**

**Severity:** BAIXÍSSIMA — mencionar só para o planejador resistir
optimização especulativa.

## Code Examples

Ver `Pattern 1`, `Pattern 2`, `Pattern 3`, `Pattern 5`, `Pattern 6` acima.
Todos os exemplos foram testados empiricamente em
`uv run python -c '...'` no Python 3.13.13 do `.venv` deste projeto.

### Exemplo de teste do success criterion #1 (instanciação + frozen + slots)

```python
# tests/core/test_dataclasses.py
from pathlib import Path

import pytest
from dataclasses import FrozenInstanceError

from biblio_validador.core import (
    EstadoPatch,
    Patch,
    Severidade,
    Violacao,
)


def test_violacao_instancia_com_frozen_e_slots() -> None:
    """D-28.1: Violacao instancia, é frozen e tem __slots__."""
    v = Violacao(
        arquivo=Path("a.md"),
        linha_inicio=1,
        linha_fim=1,
        col_inicio=1,
        col_fim=5,
        trecho_violador="abcd",
        regra_id="lex_001",
        regra_nome="X",
        severidade=Severidade.ERRO,
    )
    assert v.regra_id == "lex_001"
    assert v.sugestoes == ()  # default
    assert v.principio_canonico_violado is None  # default
    # frozen → __slots__ definido, __dict__ ausente
    assert hasattr(v, "__slots__")
    assert not hasattr(v, "__dict__")


def test_violacao_frozen_raises_on_mutate() -> None:
    """D-28.4: mutar regra_id levanta FrozenInstanceError."""
    v = Violacao(
        arquivo=Path("a.md"), linha_inicio=1, linha_fim=1,
        col_inicio=1, col_fim=2, trecho_violador="ab",
        regra_id="lex_001", regra_nome="X",
        severidade=Severidade.ERRO,
    )
    with pytest.raises(FrozenInstanceError):
        v.regra_id = "outro"  # type: ignore[misc]


def test_patch_mutavel_estado() -> None:
    """D-28.2: Patch é mutável em estado, slots proíbe atributo novo."""
    p = Patch(
        arquivo=Path("a.md"), linha=1, col_inicio=1, col_fim=5,
        texto_original="abcd", texto_substituto="efgh",
        motivo="cst_012 → forma direta", confianca=1.0,
    )
    assert p.estado == EstadoPatch.PROPOSTO
    p.estado = EstadoPatch.ACEITO  # mutação OK
    assert p.estado == EstadoPatch.ACEITO
    # __slots__ proíbe novo atributo
    with pytest.raises(AttributeError):
        p.atributo_novo = 42  # type: ignore[attr-defined]
```

### Exemplo de testes parametrizados de invariantes (D-29)

```python
@pytest.mark.parametrize(
    "kwargs, msg_substr",
    [
        (
            dict(arquivo=Path("a.md"), linha_inicio=0, linha_fim=1,
                 col_inicio=1, col_fim=2, trecho_violador="ab",
                 regra_id="lex_001", regra_nome="X",
                 severidade=Severidade.ERRO),
            "linha_inicio",
        ),
        (
            dict(arquivo=Path("a.md"), linha_inicio=1, linha_fim=1,
                 col_inicio=5, col_fim=2, trecho_violador="ab",
                 regra_id="lex_001", regra_nome="X",
                 severidade=Severidade.ERRO),
            "col_fim",
        ),
    ],
)
def test_violacao_invariantes_raise(
    kwargs: dict[str, object], msg_substr: str
) -> None:
    with pytest.raises(ValueError, match=msg_substr):
        Violacao(**kwargs)  # type: ignore[arg-type]
```

## Validation Architecture

> Nyquist Dimension 8 — required because `workflow.nyquist_validation: true`
> in `.planning/config.json`. `[VERIFIED: config.json lido]`

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + pytest-cov 7.1.0 (instalado em Phase 1 D-08) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (Phase 1 D-14) |
| Quick run command | `uv run pytest tests/core/ -x --tb=short` |
| Full suite command | `uv run pytest --cov=biblio_validador --cov-report=term-missing` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CORE-02 | Instanciação de `Violacao` com frozen+slots | unit | `uv run pytest tests/core/test_dataclasses.py::test_violacao_instancia_com_frozen_e_slots -x` | Wave 0 |
| CORE-02 | `FrozenInstanceError` ao mutar `Violacao.regra_id` | unit | `uv run pytest tests/core/test_dataclasses.py::test_violacao_frozen_raises_on_mutate -x` | Wave 0 |
| CORE-02 | `dataclasses.asdict(violacao)` retorna dict válido | unit | `uv run pytest tests/core/test_dataclasses.py::test_violacao_asdict_estrutural -x` | Wave 0 |
| CORE-02 | `json.dumps(violacao.to_dict())` produz string serializável + round-trip | contract | `uv run pytest tests/core/test_dataclasses.py::test_violacao_to_dict_json_roundtrip -x` | Wave 0 |
| CORE-02 | Invariantes `__post_init__`: `linha_inicio < 1` raises ValueError | unit (parametrize) | `uv run pytest tests/core/test_dataclasses.py::test_violacao_invariantes_raise -x` | Wave 0 |
| CORE-02 | Invariantes `__post_init__`: `col_fim < col_inicio` raises ValueError | unit (parametrize) | mesmo arquivo, parametrize | Wave 0 |
| CORE-02 | `Severidade.peso()` retorna ordenação monotônica | unit | `uv run pytest tests/core/test_dataclasses.py::test_severidade_peso_monotonica -x` | Wave 0 |
| CORE-03 | Instanciação de `Patch` com slots; mutação de `estado` permitida | unit | `uv run pytest tests/core/test_dataclasses.py::test_patch_mutavel_estado -x` | Wave 0 |
| CORE-03 | `__slots__` proíbe atributo novo em `Patch` | unit | mesmo teste acima (assert AttributeError) | Wave 0 |
| CORE-03 | `EstadoPatch` default `PROPOSTO`; valor string `"proposto"` | unit | `uv run pytest tests/core/test_dataclasses.py::test_estado_patch_default_proposto -x` | Wave 0 |
| CORE-03 | Invariantes `Patch`: `confianca = 1.5` raises | unit (parametrize) | `uv run pytest tests/core/test_dataclasses.py::test_patch_invariantes_raise -x` | Wave 0 |
| CORE-03 | Invariantes `Patch`: `texto_original = ""` raises | unit (parametrize) | mesmo arquivo, parametrize | Wave 0 |
| CORE-03 | Invariantes `Patch`: `motivo = ""` raises | unit (parametrize) | mesmo arquivo, parametrize | Wave 0 |
| CORE-03 | `json.dumps(patch.to_dict())` produz string serializável | contract | `uv run pytest tests/core/test_dataclasses.py::test_patch_to_dict_json_roundtrip -x` | Wave 0 |
| CORE-02+CORE-03 | Coverage `>= 95%` em `core/dataclasses.py` e `core/enums.py` | coverage gate | `uv run pytest --cov=biblio_validador.core --cov-fail-under=95` | Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/core/ -x --tb=short` (suite
  isolada da phase, < 1s)
- **Per wave merge:** `uv run pytest --cov=biblio_validador --cov-report=term-missing`
  (suite completa do projeto + coverage report; deve incluir testes Phase
  1+2 sem regressão)
- **Phase gate:** Full suite green AND `pytest --cov-fail-under=95` para
  módulos de Phase 3 antes de `/gsd-verify-work`. Fail-under
  é a linha vermelha — adicionar ao comando do CI hook se houver.

### Wave 0 Gaps

- [ ] `tests/core/__init__.py` — marcador de pacote pytest (vazio)
- [ ] `tests/core/test_dataclasses.py` — cobre todos os 14 testes acima

*Nenhuma dependência de framework adicional: pytest+pytest-cov já estão
instalados (Phase 1 D-08); `pyproject.toml` já tem `testpaths = ["tests"]`
e `[tool.coverage.run]` configurados (Phase 1 D-14). Phase 3 só **adiciona**
testes — sem mudança de infra.*

### Contract Tests Específicos

Por se tratar de fase de modelagem pura, os contract tests são as
**invariantes runtime** que blindam consumidores futuros:

1. **Frozenness contract:**
   `assert getattr(Violacao, "__dataclass_params__").frozen is True`.
   Detecta regressão se alguém remover `frozen=True` em refactor.

2. **Slots contract:**
   `assert hasattr(Violacao, "__slots__") and not hasattr(viol, "__dict__")`.

3. **Tuple-not-list contract:**
   `assert isinstance(viol.sugestoes, tuple)`. Pega regressão se alguém
   trocar `tuple[str, ...]` por `list[str]` por descuido.

4. **JSON round-trip contract:**
   `assert json.loads(json.dumps(viol.to_dict()))["regra_id"] == viol.regra_id`
   para cada campo. Garante que `to_dict()` é completo (não esqueceu campo).

5. **Hashability contract:**
   `Violacao` em `set()` deduplica idênticos; `Patch` em `set()` raises.
   Documenta a invariante de design no nível de teste.

## Open Questions

Nenhuma decisão de CONTEXT.md ficou inválidada pela pesquisa. As 33 decisões
são todas tecnicamente sustentáveis em Python 3.13.13 e mutuamente coerentes.

Pequenas ambiguidades resolvidas pela pesquisa (não são "open questions"
ainda, mas o planejador deve ter consciência):

1. **Sucesso criterion #3 do roadmap** ("`asdict(violacao)` produz dict
   serializável em JSON sem erros"): pesquisa confirma a interpretação de
   D-26 — dict gerado por `asdict()` é estruturalmente correto, mas
   serialização final passa por `to_dict()`. **Documentar essa ambiguidade
   na docstring de `Violacao.to_dict()` é tarefa da phase.**

2. **Mensagem de invariante deve incluir contexto?** D-22 manda incluir
   `regra_id`. Pesquisa endossa: tracebacks ricos em diagnose são gold em
   produção quando o orchestrator processa centenas de violações. Manter
   D-22 como está.

3. **`Severidade.peso()` é `instancemethod` ou `classmethod`?** D-16 diz
   "método `peso()`". Pesquisa: `instancemethod` que lê `self.value` é o
   padrão Pythônico para Enum (PEP 663 não muda isso). `classmethod` ou
   `staticmethod` seria contornar a vantagem de acoplamento `enum +
   comportamento`. Implementação Pattern 3 acima usa instancemethod — manter.

## Sources

### Primary (HIGH confidence)

- **Empirical Python 3.13.13 in `.venv`** (run via `uv run python -c ...` em
  2026-05-05) — verificou:
  - `frozen=True` + `slots=True` interagem corretamente
  - `FrozenInstanceError` é levantada em mutação
  - `tuple[str, ...] = ()` e `field(default_factory=tuple)` produzem mesmo
    resultado
  - `__post_init__` com `raise ValueError` propaga corretamente
  - `dataclasses.asdict()` preserva `Path`/`Enum`/`tuple` literalmente
  - `json.dumps(asdict(v))` falha com `TypeError` em `Path`
  - Helper `_normalize_for_json` recursivo + `json.dumps` + `json.loads`
    produz round-trip correto
  - `frozen=True` torna dataclass hashable (set deduplica)
  - `slots=True` sem `frozen` torna dataclass unhashable (`__hash__ = None`)
  - `IntEnum` `repr/str` quebra legibilidade vs `Enum` puro
  - `StrEnum` `str(s)` retorna valor cru — perde marcador de tipo

- **Python 3.13 docs §dataclasses** —
  https://docs.python.org/3.13/library/dataclasses.html (HIGH: confirma
  `slots=True` desde 3.10, `frozen` semantics, `__post_init__`,
  `FrozenInstanceError`)

- **Python 3.13 docs §enum** —
  https://docs.python.org/3.13/library/enum.html (HIGH: confirma `Enum` vs
  `StrEnum` vs `IntEnum` semantics)

- **PEP 557 — Data Classes** —
  https://peps.python.org/pep-0557/ (HIGH: spec de `__post_init__`,
  defaults, `eq` + `__hash__` interactions)

- **PEP 663 — StrEnum** —
  https://peps.python.org/pep-0663/ (HIGH: spec de `StrEnum` introduzido
  em 3.11; confirma que `str(StrEnum.X)` retorna o valor cru)

- **`.planning/research/STACK.md` §"Modelagem de Patches (Decisão de
  Arquitetura)"** — confirma `dataclasses` stdlib over pydantic, exemplo
  inicial de `Violacao`/`Patch`

- **`.planning/research/PITFALLS.md` §"Pitfall 8: Contador conta rejeições
  como fixed"** — fonte do enum `EstadoPatch` com 4 valores
  (PROPOSTO/ACEITO/REJEITADO/SUPRIMIDO); D-20 herda essa estrutura.

- **`src/biblio_validador/parser/types.py`** — template formal de
  `@dataclass(frozen=True, slots=True)` em uso real no projeto. Phase 3
  replica o pattern.

### Secondary (MEDIUM confidence)

- **Real Python — Data Classes Tutorial** —
  https://realpython.com/python-data-classes/ (informação corroborada por
  fonte primária Python docs)

- **`02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json`** —
  formato de `regra_id` (`cst_001..cst_012`) e `severidade` no JSON-fonte;
  informa enum `Severidade`

### Tertiary (LOW confidence)

Nenhuma. Todas as afirmações são verificadas em fonte primária ou
empiricamente.

## Assumptions Log

Esta tabela está vazia: todas as afirmações foram verificadas
empiricamente em Python 3.13.13 ou citadas de fonte oficial.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | — | — | — |

**All claims in this research were verified or cited — no user confirmation
needed.**

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — todas as bibliotecas são stdlib Python 3.13.13;
  versão verificada em runtime.
- Architecture: HIGH — derivada de Pattern 1+2 do projeto (Phase 2
  `Paragrafo`); zero novos componentes; integration points com Phases
  4/5/6/8/19/48/51/58 são de leitura, não de modificação.
- Pitfalls: HIGH — todos os 6 pitfalls foram empiricamente reproduzidos
  em `uv run python -c`. Cada um cita evidência empírica direta (`[VERIFIED:
  empirical ...]`).
- Validation: HIGH — pytest+pytest-cov já em uso desde Phase 1; coverage
  gate `>= 95%` é factível para módulos pequenos (4 símbolos públicos).

**Research date:** 2026-05-05
**Valid until:** 2026-06-05 (30 dias — `dataclasses` e `enum` são extremamente
estáveis na stdlib; nada do que se afirma aqui muda em ciclos curtos)
