# Phase 3: Dataclasses Core - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-05
**Phase:** 03-dataclasses-core
**Mode:** `--auto` (Claude selecionou recomendados sem AskUserQuestion)
**Areas discussed:** Localização do módulo, Forma das dataclasses, Campos de Violacao, Enum Severidade, Campos de Patch, Enum EstadoPatch, Validação invariante, Serialização JSON, Testes

---

## Localização do módulo

| Option | Description | Selected |
|--------|-------------|----------|
| Subpacote `core/` (recomendado) | `core/dataclasses.py` + `core/enums.py` + `core/__init__.py` re-export. Evita shadow do stdlib `dataclasses`. | ✓ |
| Top-level `dataclasses.py` | `src/biblio_validador/dataclasses.py` direto. Conflita com import `from dataclasses import dataclass` em IDE refactors. | |
| Módulo único `models.py` | Tudo em 1 arquivo. Cresceria com enums + helpers. | |

**User's choice:** Subpacote `core/` (auto-selected — Phase 2 D-01 já antecipou esta localização)
**Notes:** D-01..D-04. Mantém separação `core/dataclasses.py` (estruturas) vs `core/enums.py` (vocabulários fechados).

---

## Forma das dataclasses

| Option | Description | Selected |
|--------|-------------|----------|
| `Violacao` frozen+slots / `Patch` slots-only (recomendado) | Spec do roadmap. Imutável onde faz sentido, mutável onde estado evolui. | ✓ |
| Ambos frozen | Patch precisaria recriar instância em cada transição de estado. Overhead em loop validar→fixar→revalidar. | |
| Ambos mutáveis | Perde proteção contra mutação acidental da saída do validador. | |

**User's choice:** frozen+slots para Violacao, slots-only para Patch (auto)
**Notes:** D-05, D-06. Coleções dentro de Violacao usam tuple (D-07) para fechar o buraco do frozen-mas-lista-mutável.

---

## Campos de Violacao — sugestoes

| Option | Description | Selected |
|--------|-------------|----------|
| `tuple[str, ...] = ()` (recomendado) | Imutável de fato; hashable; coerente com `frozen=True`. | ✓ |
| `list[str] = field(default_factory=list)` | Comum em Python, mas mutável apesar do `frozen`. | |
| `frozenset[str]` | Perde ordem; sugestões têm ordem semântica (1ª = preferida). | |

**User's choice:** tuple (auto)
**Notes:** D-07.

---

## Enum Severidade

| Option | Description | Selected |
|--------|-------------|----------|
| `enum.Enum` com valor string + método `peso()` (recomendado) | Coerente com Phase 2 `TipoSecao`; logs legíveis; ordenação via método explícito. | ✓ |
| `IntEnum` (1=INFO..4=CRITICO) | Mistura semântica de peso com representação. Pior em logs. | |
| `StrEnum` | Subclasse de str — perde tipagem forte (mistura com strings cruas). | |

**User's choice:** Enum + peso() (auto)
**Notes:** D-14..D-16. Valores `INFO/ALERTA/ERRO/CRITICO` extraídos do uso no código (orchestrator exit code) e dos JSONs canônicos.

---

## Campos de Patch — confianca default

| Option | Description | Selected |
|--------|-------------|----------|
| Sem default — obrigatório (recomendado) | Força fixer a declarar intencionalmente. Anti-hidden-default. | ✓ |
| `confianca: float = 1.0` | Silencia fixers ASSISTIDO mal calibrados. | |
| `confianca: float = 0.5` | Default conservador, mas ainda implícito. | |

**User's choice:** sem default (auto)
**Notes:** D-17.

---

## Enum EstadoPatch — enforcement de transições

| Option | Description | Selected |
|--------|-------------|----------|
| Documentar em docstring, sem enforcement runtime (recomendado) | Mantém Patch como dataclass simples. State machine vai para Phase 51 se necessário. | ✓ |
| Property setter custom validando transições | Custo runtime + complexidade em phase de modelagem; prematuro. | |
| State machine via biblioteca externa | Dep adicional, overkill. | |

**User's choice:** docstring (auto)
**Notes:** D-21. Decisão prematura de enforcement aqui; orchestrator Phase 51 decide se precisa.

---

## Validação invariante (`__post_init__`)

| Option | Description | Selected |
|--------|-------------|----------|
| Light validation (recomendado) | Checa invariantes baratos (linha>=1, col_fim>=col_inicio, confianca em [0,1]). Falha rápido. | ✓ |
| Sem validação | Bugs cascatam para Phase 5 (offsets errados); mais difícil debugar. | |
| Validação extensiva (Pydantic-like) | Custo runtime alto + dependência adicional. | |

**User's choice:** light (auto)
**Notes:** D-22..D-24.

---

## Serialização JSON

| Option | Description | Selected |
|--------|-------------|----------|
| `to_dict()` paralelo a `asdict()` (recomendado) | `asdict()` puro disponível; `to_dict()` normaliza Path/Enum/tuple para JSON nativo. | ✓ |
| Apenas `asdict()` puro | Path e Enum quebram `json.dumps` sem encoder customizado. Success criterion ambíguo. | |
| Encoder customizado `JsonViolacaoEncoder(json.JSONEncoder)` | Mais flexível, mais código. Adiar até Phase 58. | |

**User's choice:** to_dict() + asdict() (auto)
**Notes:** D-25, D-26. `from_dict()` reverso adiado para Phase 58 (D-27).

---

## Testes — escopo

| Option | Description | Selected |
|--------|-------------|----------|
| 4 success-criteria + 5 invariantes (recomendado) | Cobre roadmap explicitamente + cobertura defensiva de `__post_init__`. ~95% coverage. | ✓ |
| Apenas 4 success-criteria | Não cobre branches de validação; risco de regressão. | |
| Property-based testing (hypothesis) | Overkill em modelo de 2 dataclasses; adiar se houver evidência. | |

**User's choice:** 4 + 5 (auto)
**Notes:** D-28..D-30.

---

## Claude's Discretion

- Helpers privados internos (ex.: `_normalize_for_json`)
- Texto exato de docstrings (PT-BR)
- Estrutura de parametrize nos testes de invariante
- Decidir no plan se vale `__repr__` customizado para truncar `trecho_violador`

## Deferred Ideas

- `from_dict()` reverso → Phase 58 (ORC-09)
- Enforcement de state machine de `EstadoPatch` → Phase 51 (ORC-02)
- `__repr__` customizado → decisão do plan
- Subclasses de Violacao (`ViolacaoAgregada`) → Phase 18 (AGR-01)
- `IntEnum` para Severidade → manter Enum + peso() separado
- Campo `created_at: datetime` → telemetria não pertence à dataclass
- `__hash__` customizado em Patch → Python desabilita auto, correto
