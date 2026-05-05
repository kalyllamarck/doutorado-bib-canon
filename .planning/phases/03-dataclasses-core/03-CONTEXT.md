# Phase 3: Dataclasses Core - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning
**Mode:** `--auto` (decisões auto-resolvidas pelo recomendado, log abaixo)

<domain>
## Phase Boundary

Modelagem nuclear das estruturas que circulam pelo pipeline de validação:
`Violacao` (saída de `ValidadorBase`), `Patch` (saída de `FixerBase`),
enum `EstadoPatch` (ciclo de vida do patch) e enum `Severidade` (classificação
de `Violacao`). Cobre **CORE-02** e **CORE-03**.

Phase 3 entrega exclusivamente o módulo `src/biblio_validador/core/` com:
- `core/dataclasses.py` — `Violacao`, `Patch`
- `core/enums.py` — `EstadoPatch`, `Severidade`
- `core/__init__.py` — re-export público

Sem lógica de validação (Phase 6+), sem ABCs (Phase 4), sem aplicação de patches
(Phase 5). Apenas tipos imutáveis/mutáveis com invariantes mínimas.

</domain>

<decisions>
## Implementation Decisions

### Localização do módulo (D-01..D-04)

- **D-01:** Subpacote novo `src/biblio_validador/core/`. Evita shadowing do
  stdlib `dataclasses` (anti-pattern: `biblio_validador/dataclasses.py`
  conflitaria com `from dataclasses import dataclass` por sombra de
  `sys.path`/IDE refactors). Decisão tomada de Phase 2 D-01 já antecipava
  `core/dataclasses.py`.
- **D-02:** Arquivos:
  - `core/__init__.py` — re-export
  - `core/dataclasses.py` — `Violacao` + `Patch` + helpers de serialização
  - `core/enums.py` — `EstadoPatch` + `Severidade`
- **D-03:** `core/__init__.py` re-exporta os 4 símbolos públicos:
  ```python
  from biblio_validador.core.dataclasses import Violacao, Patch
  from biblio_validador.core.enums import EstadoPatch, Severidade

  __all__ = ["Violacao", "Patch", "EstadoPatch", "Severidade"]
  ```
  Permite `from biblio_validador.core import Violacao, Patch` em validadores
  e fixers.
- **D-04:** Não criar `core/types.py` ou outras subdivisões agora — 4 símbolos
  caben em 2 arquivos. Refactor pós-M1 se quantidade crescer.

### Forma das dataclasses (D-05..D-08)

- **D-05:** `Violacao` é `@dataclass(frozen=True, slots=True)`. Imutabilidade
  protege a saída dos validadores contra mutação acidental no orchestrator e
  agregadores M3 (que consomem `list[Violacao]` puro). `slots=True` corta
  overhead de `__dict__`.
- **D-06:** `Patch` é `@dataclass(slots=True)` **sem** `frozen` — `estado` muta
  ao longo do ciclo (PROPOSTO → ACEITO/REJEITADO/SUPRIMIDO) e `requer_revisao_humana`
  pode ser flipado pelo orchestrator. Convenção: **somente** `estado` e
  `requer_revisao_humana` mudam após construção; demais campos são tratados
  como read-only por convenção (não enforçado em runtime). Mantém footprint
  mínimo sem custom property setters.
- **D-07:** Coleções dentro de `Violacao` usam `tuple[str, ...]` em vez de
  `list[str]`. `frozen=True` só impede reatribuir o atributo, não mutar o
  conteúdo da lista — `tuple` fecha o buraco e dá hashabilidade gratuita
  (útil para deduplicação no orchestrator). `field(default_factory=tuple)` =
  `()`.
- **D-08:** Coleções dentro de `Patch` permanecem `list[str]`/`tuple` conforme
  semântica. `Patch` em si não tem coleção planejada nesta fase; D-08 é
  preventivo: se algum campo futuro precisar de coleção, manter `tuple`.

### Campos de `Violacao` (D-09..D-13)

- **D-09:** Campos completos (em ordem de declaração — todos sem default
  exceto onde indicado):
  - `arquivo: Path`
  - `linha_inicio: int` — 1-based, alinha com `Paragrafo.linha_inicio`
  - `linha_fim: int` — 1-based inclusivo
  - `col_inicio: int` — 1-based, posição do 1º caractere violador na linha
  - `col_fim: int` — 1-based exclusivo (col_inicio = primeiro char violador,
    col_fim = primeiro char NÃO violador). Convenção half-open consistente com
    Python slicing — facilita `linha[col_inicio-1:col_fim-1]`.
  - `trecho_violador: str` — texto exato detectado (recortado via regex match)
  - `regra_id: str` — ex.: `"cst_012"`, `"lex_001"`, `"coc_007"`
  - `regra_nome: str` — ex.: `"Anúncio metarretórico"` (lido do JSON)
  - `severidade: Severidade` — enum (ver D-14)
  - `sugestoes: tuple[str, ...] = ()` — lista de reescritas alternativas;
    pode ser vazia (validador puro sem proposta de fix)
  - `principio_canonico_violado: str | None = None` — preenchido por
    AGR-02 (Phase 19) que mapeia cst→p_YY; primitivos M2 deixam `None`
- **D-10:** Convenção col half-open: `col_fim - col_inicio == len(trecho_violador)`
  em caracteres. Documentar invariante na docstring. Validadores que
  produzam `Violacao` com inconsistência triggam pós-validação no
  orchestrator (Phase 8/50).
- **D-11:** `arquivo` é `pathlib.Path`, não `str`. Consistente com Phase 2
  (`Paragrafo.arquivo: Path`). Helpers de serialização (D-25) convertem
  para str na hora de exportar JSON.
- **D-12:** `linha_fim` aceita ser igual a `linha_inicio` (caso comum:
  violação intra-linha). Inclusivo facilita `range(linha_inicio, linha_fim+1)`.
- **D-13:** Sem campo `mensagem` adicional — `regra_nome` + `regra_id` +
  `trecho_violador` é suficiente para o relatório `AUDITORIA.md` (Phase 8).
  Mensagem humanizada é responsabilidade do `ReportGenerator`, não da
  dataclass.

### Enum `Severidade` (D-14..D-16)

- **D-14:** `Severidade` é `enum.Enum` com valor string snake_case. Coerente
  com Phase 2 D-03 (`TipoSecao`) — usa `Enum` (não `StrEnum`) pelo mesmo
  motivo: legibilidade em `loguru` logs (`Severidade.ERRO` aparece como
  `"erro"` quando `.value`, mas como `"Severidade.ERRO"` em `repr`).
- **D-15:** Valores fixos:
  - `INFO = "info"` — informativo, não conta para exit code
  - `ALERTA = "alerta"` — aviso, ainda não bloqueia
  - `ERRO = "erro"` — viola regra canônica direta; exit code 1
  - `CRITICO = "critico"` — coocorrência VERMELHO_FORTE (AGR-01); exit code 1
- **D-16:** Ordem de prioridade (ranking) é monotônica: `INFO < ALERTA < ERRO
  < CRITICO`. Implementar via método `Severidade.peso() -> int` (retorna
  0..3) para ordenação determinística no relatório. Não usar `IntEnum`
  porque mistura semântica (peso) com representação (string em log).

### Campos de `Patch` (D-17..D-19)

- **D-17:** Campos completos:
  - `arquivo: Path`
  - `linha: int` — 1-based; patch sempre intra-linha (multi-linha = múltiplos
    patches; PatchAplicador da Phase 5 ordena reverso por (linha, col))
  - `col_inicio: int` — 1-based, half-open consistente com `Violacao.col_inicio`
  - `col_fim: int` — 1-based, half-open
  - `texto_original: str` — bytes que serão substituídos (validação pré-aplicação:
    `texto_atual_no_arquivo == texto_original`; se diverge, patch falha,
    Phase 5)
  - `texto_substituto: str` — bytes que entram no lugar
  - `motivo: str` — ex.: `"Aplicação de cst_012: anúncio metarretórico → forma direta"`
  - `confianca: float` — `0.0..1.0`. **Sem default** — força fixer a declarar
    intencionalmente (anti-hidden-default). 1.0 = AUTO determinístico,
    >=0.85 = ASSISTIDO típico, <0.85 = LLM ou edge case.
  - `requer_revisao_humana: bool = False` — fixer pode marcar `True` quando
    detecta ambiguidade (ex.: FXA-03 dois-pontos em contexto incerto)
  - `estado: EstadoPatch = EstadoPatch.PROPOSTO` — default no construtor;
    orchestrator (Phase 51) muta para ACEITO/REJEITADO/SUPRIMIDO.
- **D-18:** `Patch` é **single-line**. Patch que abrangeria várias linhas é
  decomposto em múltiplos patches pelo fixer (mesmo `motivo`, ordenados
  reverso pelo aplicador). Justificativa: simplifica ordenação reversa do
  PatchAplicador (Phase 5) e diff visualization (Phase 7).
- **D-19:** Sem campo `regra_id_origem`. Rastreabilidade ao validador-origem
  feita via `motivo` (string narrativa) e via grafo de execução do
  orchestrator (Phase 51). Adicionar campo só se Phase 51 evidenciar
  necessidade.

### Enum `EstadoPatch` (D-20..D-21)

- **D-20:** `EstadoPatch` é `enum.Enum` com valor string snake_case (mesma
  convenção D-14):
  - `PROPOSTO = "proposto"` — fixer emitiu, ainda não decidido
  - `ACEITO = "aceito"` — orchestrator aprovou, será aplicado
  - `REJEITADO = "rejeitado"` — autor (modo ASSISTIDO) ou guardrail rejeitou
  - `SUPRIMIDO = "suprimido"` — pós-validação LLM (Phase 48) descartou por
    introduzir nova violação
- **D-21:** Transições válidas (documentadas em docstring; **não** enforçadas
  em runtime nesta phase — enforcement vai para o orchestrator Phase 51 se
  necessário):
  - `PROPOSTO → ACEITO | REJEITADO | SUPRIMIDO`
  - `ACEITO → SUPRIMIDO` (raro: aplicação falhou byte-exact)
  - estados terminais: `REJEITADO`, `SUPRIMIDO` (não voltam)

### Validação invariante (`__post_init__`) (D-22..D-24)

- **D-22:** `Violacao.__post_init__` valida (raise `ValueError` com mensagem
  contendo `regra_id` para diagnóstico):
  - `linha_inicio >= 1`
  - `linha_fim >= linha_inicio`
  - `col_inicio >= 1`
  - `col_fim >= col_inicio`
  - `regra_id` não vazio (`bool(regra_id.strip())`)
  - `len(trecho_violador) == col_fim - col_inicio` quando `linha_inicio ==
    linha_fim` (intra-linha; cross-line skip por simplicidade)
- **D-23:** `Patch.__post_init__` valida:
  - `linha >= 1`
  - `col_inicio >= 1`
  - `col_fim >= col_inicio`
  - `0.0 <= confianca <= 1.0`
  - `texto_original` não vazio (patch nulo é code smell — fixer deveria
    retornar `[]` em vez)
  - `motivo` não vazio
- **D-24:** `__post_init__` em `frozen=True` exige `object.__setattr__`
  apenas se modificar campos. Aqui só validamos, não mutamos — `raise
  ValueError` direto. Documentar.

### Serialização para JSON (D-25..D-27)

- **D-25:** Adicionar método `to_dict() -> dict[str, Any]` em **Violacao** e
  **Patch** que produz dict imediatamente serializável via `json.dumps`
  sem encoder customizado:
  - `Path → str(path)`
  - `Severidade/EstadoPatch → enum.value` (string)
  - `tuple → list` (json não tem tuple)
  - Demais campos passam diretos
  Implementação: chamar `dataclasses.asdict()` e pós-processar (helper
  privado `_normalize_for_json` no módulo).
- **D-26:** Manter `dataclasses.asdict()` puro acessível para callers que
  preferem objetos Python ricos (ex.: testes). Success criterion #3 do
  ROADMAP exige que `asdict(violacao)` "produza dict serializável em JSON
  sem erros" — interpretado como: dict gerado é estruturalmente correto;
  serialização final passa por `to_dict()` ou encoder customizado. Documentar
  ambiguidade em docstring para evitar discussão futura.
- **D-27:** **Não** implementar `from_dict()` reverso nesta fase. Caso de
  uso (deserialização) só aparece em Phase 58 (ORC-09 Output JSON) ou em
  testes que carreguem fixtures — adiar até demanda real.

### Testes (D-28..D-30)

- **D-28:** `tests/core/test_dataclasses.py` cobre os 4 success criteria do
  roadmap (Phase 3) sem extras:
  1. `Violacao(arquivo=Path("a.md"), linha_inicio=1, linha_fim=1,
     col_inicio=1, col_fim=5, trecho_violador="abcd", regra_id="lex_001",
     regra_nome="X", severidade=Severidade.ERRO)` — instancia, tem `frozen`
     e `slots`.
  2. `Patch(arquivo=..., linha=1, col_inicio=1, col_fim=5,
     texto_original="abcd", texto_substituto="efgh", motivo="...",
     confianca=1.0)` — `estado` default `EstadoPatch.PROPOSTO`; mutar
     `patch.estado = EstadoPatch.ACEITO` funciona; `__slots__` proíbe
     atributo novo.
  3. `dataclasses.asdict(violacao)` retorna dict; `json.dumps(viol.to_dict())`
     retorna string válida (round-trip via `json.loads` confirma campos).
  4. Tentar `violacao.regra_id = "x"` levanta `dataclasses.FrozenInstanceError`.
- **D-29:** Adicionar 5 testes de invariante (`__post_init__` raises
  `ValueError`):
  - `linha_inicio = 0` em `Violacao`
  - `col_fim < col_inicio` em `Violacao`
  - `confianca = 1.5` em `Patch`
  - `texto_original = ""` em `Patch`
  - `motivo = ""` em `Patch`
- **D-30:** Coverage alvo `>= 95%` em `core/dataclasses.py` e
  `core/enums.py` (módulos pequenos, alvo factível). Reusa
  `pytest --cov=biblio_validador.core` configurado em Phase 1.

### Tooling (D-31..D-33)

- **D-31:** Type hints 100% (CLAUDE.md regra 9 + mypy strict). Inclui
  `Severidade` e `EstadoPatch` como tipos retornáveis de `peso()` (`int`).
- **D-32:** `ruff line-length = 80` herdado de Phase 1. Quebrar docstrings
  longas em vez de violar.
- **D-33:** Sem `loguru` neste módulo — `core/` é zero-side-effect (sem I/O,
  sem log). Logging começa em Phase 2 (parser) e continua em validadores
  (Phase 6+).

### Folded Todos
Nenhum todo pendente foi mapeado para esta phase.

### Claude's Discretion

- Helpers privados internos (ex.: `_normalize_for_json` em `dataclasses.py`).
- Texto exato de docstrings (manter PT-BR conforme convenção do projeto).
- Estrutura interna dos 5 testes de `__post_init__` (parametrizar via
  `@pytest.mark.parametrize` ou separar é decisão do executor).
- Se vale a pena adicionar `__repr__` customizado para `Violacao`/`Patch`
  com truncamento de `trecho_violador` em logs (default repr fica longo).
  Avaliar e decidir no plan.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requisitos
- `.planning/REQUIREMENTS.md` §"Core (M1)" — CORE-02 (campos de
  `Violacao`) e CORE-03 (campos de `Patch` + enum `EstadoPatch`)
- `.planning/ROADMAP.md` §"Phase 3: Dataclasses Core" — 4 success criteria

### Stack e versões (Phase 1)
- `.planning/research/STACK.md` §"Modelagem de Patches (Decisão de
  Arquitetura)" — confirma `dataclasses` stdlib over pydantic
- `.planning/research/SUMMARY.md` — Python 3.13+, slots=True, frozen=True
- `.planning/research/PITFALLS.md` — drift de offsets (informa convenção
  half-open D-09/D-17)

### Phase 1 (decisões herdadas)
- `.planning/phases/01-bootstrap/01-CONTEXT.md` §"Identidade do pacote" —
  D-01 (nome `biblio_validador`), D-02 (layout `src/`), D-13 (mypy strict)

### Phase 2 (decisões herdadas)
- `.planning/phases/02-parser-markdown/02-CONTEXT.md` §"Localização e
  shape do `Paragrafo`" — `Paragrafo.linha_inicio` 1-based informa D-09
- `.planning/phases/02-parser-markdown/02-CONTEXT.md` §"Enum `TipoSecao`"
  D-03 — convenção `enum.Enum` com valor string snake_case herdada para
  `Severidade` (D-14) e `EstadoPatch` (D-20)
- `src/biblio_validador/parser/types.py` — `Paragrafo` em
  `@dataclass(frozen=True, slots=True)` é o template formal seguido por
  `Violacao` (D-05)

### Construções referenciadas (info de campos `regra_id`, `severidade`)
- `02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json` —
  formato de `regra_id` (`cst_001..cst_012`) e estrutura de `severidade`
  no JSON-fonte (informa enum `Severidade` D-14)
- `02_escrita/termos_proibidos/01_termos_lexicais_proibidos.json` —
  formato `lex_NNN`
- `02_escrita/termos_proibidos/06_regras_coocorrencia.json` — formato
  `coc_NNN` e severidade `CRITICO` (informa D-15)

### Projeto e regras globais
- `.planning/PROJECT.md` §"Constraints" — Python 3.13+, type hints, max 80
- `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/CLAUDE.md`
  §"Constraints" — `dataclasses` stdlib confirmado
- `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` §"Regras para o Agente"
  regra 9 (type hints obrigatórios)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/biblio_validador/__init__.py`** já existe com `__version__ = "0.1.0"`
  (Phase 1, D-03). Phase 3 adiciona apenas subpacote `core/` — sem mexer
  na raiz.
- **`src/biblio_validador/parser/types.py`** (Phase 2) é template formal
  para Phase 3: mesmo decorator pattern (`@dataclass(frozen=True, slots=True)`),
  mesma convenção de campos com `int | None`, mesmo estilo de docstring
  PT-BR. Replicar.
- **`src/biblio_validador/parser/__init__.py`** (Phase 2) é template do
  re-export — Phase 3 D-03 segue o mesmo padrão `__all__` explícito.
- **`pyproject.toml`** já tem `pytest>=9.0.3` + `pytest-cov>=7.1.0`
  (Phase 1, D-08). Phase 3 reusa sem tocar em deps.
- **`tests/`** já tem padrão de organização (Phase 1 D-15: `tests/test_cli.py`;
  Phase 2 D-26: `tests/parser/test_markdown.py`). Phase 3 cria
  `tests/core/test_dataclasses.py` seguindo mesma estrutura.

### Established Patterns

- **`@dataclass(frozen=True, slots=True)`** é a forma canônica de tipos
  imutáveis (Phase 2 `Paragrafo`). Phase 3 `Violacao` segue idêntico.
- **`enum.Enum` com valor string snake_case** é a forma canônica de enums
  (Phase 2 `TipoSecao`). Phase 3 `Severidade` e `EstadoPatch` seguem.
- **PT-BR em docstrings, código em English ASCII**. Mantido.
- **Type hints 100%** (CLAUDE.md regra 9). Mantido.
- **Sem `logging`/`print` — `loguru` apenas onde houver I/O**. Phase 3
  `core/` é puro modelo, sem log.

### Integration Points

- **Phase 4 (Contratos ABC)** consome `Violacao` e `Patch` em assinaturas:
  - `ValidadorBase.validar(paragrafos: list[Paragrafo]) -> list[Violacao]`
  - `FixerBase.propor_patches(v: Violacao, contexto) -> list[Patch]`
  Importa de `biblio_validador.core`.
- **Phase 5 (PatchAplicador)** consome `list[Patch]` ordenando reverso
  por `(linha, col_inicio)` decrescente; lê `texto_original` e valida
  contra source NFC antes de substituir por `texto_substituto` (D-17).
- **Phase 6 (Validador piloto cst_012)** é o primeiro produtor real de
  `Violacao` — instancia diretamente.
- **Phase 8 (Orchestrator Mínimo)** lê `severidade` para priorizar saída
  no `AUDITORIA.md` e setar exit code (`ERRO/CRITICO → 1`, `INFO/ALERTA → 0`).
- **Phase 19 (AGR-02)** preenche `principio_canonico_violado` mapeando
  cst→p_YY após executar primitivos.
- **Phase 48 (FXL-07)** muta `patch.estado = EstadoPatch.SUPRIMIDO` quando
  pós-validação LLM detecta nova violação.
- **Phase 51 (ORC-02)** muta `patch.estado` para ACEITO/REJEITADO conforme
  decisão do autor (modo ASSISTIDO).
- **Phase 58 (ORC-09)** chama `to_dict()` para serializar como JSON.

</code_context>

<specifics>
## Specific Ideas

- **`tuple[str, ...]` em `Violacao.sugestoes`** (D-07): justificativa é o
  padrão `frozen=True` ser meramente a proibição de `__setattr__` — coleção
  mutável dentro abre buraco. Tuple é hashable e imutável de fato.
- **`confianca` sem default em `Patch`** (D-17): forçar fixer a declarar
  intencionalmente é anti-hidden-default. Default 1.0 silenciaria fixers
  ASSISTIDO mal calibrados.
- **`__post_init__` como camada barata de invariante** (D-22, D-23):
  validar onde custa pouco evita cascata de bugs em Phase 5+ (offsets
  errados em produção difíceis de rastrear). Falha rápido = manutenção
  barata.
- **`to_dict()` paralelo a `asdict()`** (D-25): o roadmap success criterion
  pede "asdict serializável em JSON" — interpreto que dict gerado é
  estruturalmente correto e que **serialização final** passa por
  `to_dict()` (Path/Enum normalizados). Manter ambos disponíveis evita
  ambiguidade em testes.
- **Convenção half-open `col_inicio/col_fim`** (D-10, D-17): consistente
  com Python slicing, evita off-by-one em PatchAplicador (Phase 5) e em
  testes de drift (Phase 5 sucesso #1).

</specifics>

<deferred>
## Deferred Ideas

- **`from_dict()` reverso (deserialização)**: postergar até Phase 58
  (ORC-09 Output JSON) ou primeiro caso de carregamento de fixture.
- **Enforcement de transições de `EstadoPatch`** (state machine): adiar
  para Phase 51 (Orchestrator Fixer) se evidenciar bug de estado
  inconsistente. Phase 3 só documenta transições válidas.
- **`__repr__` customizado** com truncamento de `trecho_violador` longo:
  decisão fica no plan (D-Discretion). Default repr pode poluir logs.
- **Subclasses de `Violacao`** (ex.: `ViolacaoAgregada` com campo extra
  `violacoes_componentes: tuple[Violacao, ...]`): adiar para AGR-01
  (Phase 18) onde aparece o caso real. Phase 3 não cria hierarquia
  preventiva.
- **`Severidade` com `IntEnum`** (peso embutido): trocaria semântica por
  conveniência. Manter `Enum` + método `peso()` separado.
- **Campo `created_at: datetime` em `Patch`/`Violacao`**: telemetria
  pertence ao orchestrator, não à dataclass. Out of scope.
- **`__hash__` customizado em `Patch`**: `Patch` é mutável (D-06); python
  desabilita `__hash__` automaticamente (correto). Não forçar.

</deferred>

---

*Phase: 03-dataclasses-core*
*Context gathered: 2026-05-05 (auto-mode)*
