---
phase: 03-dataclasses-core
reviewed: 2026-05-05T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - src/biblio_validador/core/__init__.py
  - src/biblio_validador/core/enums.py
  - src/biblio_validador/core/dataclasses.py
  - src/biblio_validador/py.typed
  - tests/core/__init__.py
  - tests/core/test_dataclasses.py
findings:
  critical: 0
  warning: 0
  info: 4
  total: 4
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-05-05
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found (4 Info — no bugs, no security issues)

## Summary

Phase 3 entrega o domínio core do validador (`Violacao`, `Patch`, `Severidade`,
`EstadoPatch`) com qualidade alta. Os arquivos seguem rigorosamente o
`pyproject.toml` (80 chars, type hints completos), referenciam decisões
de design D-05..D-30 explicitamente, e validam invariantes em
`__post_init__`. A suíte (25 testes) cobre frozenness, slots, contratos,
serialização JSON round-trip, e regressões — todos passam (`uv run pytest
tests/core/ -q` → `25 passed in 0.03s`).

**Pontos fortes:**

- Shadowing risk de `dataclasses.py` está documentado em docstring de
  topo (linhas 1–6 de `core/dataclasses.py`) e mitigado pelo uso
  consistente de imports absolutos (`from dataclasses import ...`,
  nunca `import dataclasses`).
- Convenção half-open de coluna (D-10) é validada e a invariante
  `len(trecho_violador) == col_fim - col_inicio` é checada para o caso
  intra-linha.
- `Violacao` é hashable (frozen+tuple); `Patch` é unhashable por
  desenho (mutável) — testado explicitamente no contrato AUX.
- `_normalize_for_json` cobre os 3 tipos não-JSON-nativos produzidos
  por `asdict()`: `Path`, `Enum`, `tuple`. Branch list redundante
  (asdict nunca emite list "raw") foi mantido por defesa em
  profundidade e tem teste dedicado.

Nenhum bug, nenhuma vulnerabilidade de segurança. As 4 observações
abaixo são todas de manutenibilidade — não bloqueiam merge da phase.

## Info

### IN-01: `_normalize_for_json` não normaliza chaves de dict

**File:** `src/biblio_validador/core/dataclasses.py:31-32`
**Issue:** O ramo `isinstance(obj, dict)` recursa apenas nos valores
(`v`), preservando as chaves (`k`) cruas. Se algum dia um caller passar
um dict com chaves `Path`/`Enum`/`tuple` para `_normalize_for_json`,
`json.dumps` levantará `TypeError: keys must be str, int, float, bool
or None`. Hoje o uso é fechado: `asdict()` em `Violacao`/`Patch` só
emite chaves str (nomes de campo), então o caminho é inalcançável. Mas
o helper é genérico (anotação `obj: Any`) e poderá ser reutilizado em
phases futuras (relatório AGR, dump de paragrafos) onde chaves não
triviais apareçam.
**Fix:** normalizar chaves recursivamente, ou documentar a
pré-condição:
```python
if isinstance(obj, dict):
    return {
        _normalize_for_json(k): _normalize_for_json(v)
        for k, v in obj.items()
    }
```
Alternativa (defensiva, mantém escopo): adicionar nota na docstring
indicando que o helper assume chaves já-serializáveis (str/int/None)
e que normalização é só de valores.

### IN-02: `Severidade.peso()` levanta `KeyError` se um membro novo for adicionado sem atualizar `_PESOS_SEVERIDADE`

**File:** `src/biblio_validador/core/enums.py:23-25`
**Issue:** `peso()` faz lookup direto em `_PESOS_SEVERIDADE[self]`. Se
alguém adicionar um quinto valor (ex.: `Severidade.DEBUG = "debug"`) e
esquecer de atualizar a tabela módulo-level, a chamada explode em
runtime com `KeyError: <Severidade.DEBUG: 'debug'>` em vez de uma
mensagem acionável. A separação dict externo + classe (RESEARCH
Pattern 3) é elegante, mas tem esse acoplamento implícito.
**Fix:** opção A — adicionar guarda no carregamento do módulo que
falha cedo na importação:
```python
assert set(_PESOS_SEVERIDADE) == set(Severidade), (
    "Severidade members != _PESOS_SEVERIDADE keys"
)
```
Opção B — mover o peso para dentro do `__init__` do enum via
`_value_` extendido (mais invasivo, viola D-16 que rejeita IntEnum por
boas razões; A é preferível).

### IN-03: `_PESOS_SEVERIDADE` é módulo-level mutável

**File:** `src/biblio_validador/core/enums.py:30-35`
**Issue:** O dict `_PESOS_SEVERIDADE` está declarado como `dict[...]`
mutável. Um consumidor com acesso ao módulo pode `from
biblio_validador.core.enums import _PESOS_SEVERIDADE` e mutar
(`_PESOS_SEVERIDADE[Severidade.INFO] = 99`), corrompendo silenciosamente
a ordenação canônica em todas as chamadas subsequentes de `peso()`. O
prefixo `_` sinaliza privado, mas não impede o acesso. Em um codebase
single-author isto é cosmético; em pipeline com plugins futuros
(fixers LLM da Phase 7, agregadores da Phase 51) a garantia
de imutabilidade vale a pena.
**Fix:**
```python
from types import MappingProxyType

_PESOS_SEVERIDADE: Mapping[Severidade, int] = MappingProxyType({
    Severidade.INFO: 0,
    Severidade.ALERTA: 1,
    Severidade.ERRO: 2,
    Severidade.CRITICO: 3,
})
```
Custo: 1 import, 1 wrap. Benefício: tentativa de mutação levanta
`TypeError` na hora.

### IN-04: Mensagem do invariante `texto_original` vazio refere-se a uma estrutura externa não óbvia

**File:** `src/biblio_validador/core/dataclasses.py:154-157`
**Issue:** `raise ValueError("texto_original vazio (use [] em vez de
Patch nulo)")`. A pista entre parênteses ("use `[]` em vez de Patch
nulo") faz sentido para quem já internalizou que um fixer retorna
`list[Patch]` e que ausência-de-correção se modela como lista vazia,
mas não é óbvia em isolamento. O caller olhando só o traceback pode
ficar confuso sobre onde retornar `[]`. Consequência baixa (mensagem
de erro é texto, não comportamento), mas é a única mensagem do módulo
que codifica conhecimento implícito do contrato de fixers.
**Fix:** explicitar o consumidor pretendido:
```python
raise ValueError(
    "texto_original vazio: fixers que decidem nao corrigir devem "
    "retornar list[Patch] vazia, nao Patch com texto_original=''"
)
```
Ou mover a explicação para a docstring de `Patch` (single source of
truth) e manter a mensagem do erro curta.

---

## Notas adicionais (não-findings)

Itens que considerei e descartei como flag — registro aqui para
auditoria futura caso o entendimento mude:

- **`Violacao.__post_init__` não valida invariante de comprimento em
  caso multi-linha** (`linha_inicio != linha_fim`): correto por
  desenho. D-22 documenta explicitamente "invariante intra-linha". Em
  multi-linha não há relação simples entre `trecho_violador` e
  `(col_inicio, col_fim)` porque a string atravessa quebras.
- **`Patch` não valida `texto_substituto` não-vazio**: correto. Patch
  com `texto_substituto=""` modela deleção (ex.: remover travessão
  proibido por `sin_001`). Esperado.
- **`Patch.confianca` sem default (D-17)**: validado por design. Forçar
  o fixer a declarar confiança evita classificação automática em
  AUTO/ASSISTIDO/LLM por engano.
- **`tests/core/__init__.py` vazio**: idiomático. Marca o diretório
  como package para pytest com `--rootdir` ou testes que importam
  helpers internos. Padrão também usado em `tests/parser/__init__.py`
  (Phase 2 D-26).
- **`src/biblio_validador/py.typed` vazio**: PEP 561. Marca o pacote
  como type-hint-aware para mypy/pyright em consumidores. Conteúdo
  deve mesmo ser vazio (apenas presença do arquivo importa).
- **`cast(dict[str, Any], _normalize_for_json(asdict(self)))` em
  `to_dict()`**: necessário porque `_normalize_for_json` retorna
  `Any` (recursivo, multi-tipo). Alternativa seria overloading com
  `@overload` mas inflaria o módulo sem benefício prático.
- **Branch `list` em `_normalize_for_json` (linha 29-30)**: redundante
  porque `asdict()` converte tuples para tuples e listas só apareceriam
  em campos do dataclass — mas nenhum campo de `Violacao`/`Patch` é
  `list[...]`. Mantido por defesa em profundidade e testado em
  `test_aux_normalize_for_json_list_branch`. OK.
- **Match strings em `pytest.raises(ValueError, match="linha")`**: o
  match é regex parcial e poderia colidir com outras palavras
  contendo "linha". Suficientemente específico no contexto atual; se
  fosse extensível, valeria `match=r"\blinha\b"`.

---

_Reviewed: 2026-05-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
