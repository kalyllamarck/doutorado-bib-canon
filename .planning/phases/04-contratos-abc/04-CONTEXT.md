# Phase 4: Contratos ABC - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning
**Mode:** `--auto` (decisões auto-resolvidas pelo recomendado, log abaixo)

<domain>
## Phase Boundary

Phase 4 entrega exclusivamente as **abstract base classes** que definem
o contrato dos validadores e fixers do pipeline:

- `ValidadorBase` — contrato de quem **detecta** violações
  (`JSON_SOURCE`, `SCOPE`, `carregar_regras()`, `validar(paragrafos) -> list[Violacao]`)
- `FixerBase` — contrato de quem **propõe** patches
  (`VIOLACAO_IDS`, `MODO`, `pode_corrigir(v)`, `propor_patches(v, contexto) -> list[Patch]`,
  `aplicar(patches, modo_interativo)`)

Cobre **CORE-04** e **CORE-05**. Sem implementação concreta de regra
(Phase 6 cst_012), sem aplicador byte-exact (Phase 5 PatchAplicador),
sem orchestrator (Phase 8). Apenas:

- `core/contracts.py` — as duas ABCs com `@abstractmethod`
- `core/enums.py` — adição dos enums `Scope` e `ModoFixer` (extensão do
  arquivo já criado em Phase 3)
- `core/__init__.py` — re-export estendido
- `tests/core/test_contracts.py` — fakes mínimos + 4 success criteria
- `tests/core/fixtures/regras_fake.json` — JSON-fonte minúsculo para
  exercitar `carregar_regras()` sem depender de `02_escrita/`

</domain>

<decisions>
## Implementation Decisions

### Localização do módulo (D-01..D-04)

- **D-01:** ABCs ficam em `src/biblio_validador/core/contracts.py`. Mantém
  a regra "core/ é zero-side-effect, só tipos e contratos" (Phase 3 D-33).
  Alternativa rejeitada: criar `validators/base.py` + `fixers/base.py`
  prematuramente — em Phase 4 ainda não há subpacote `validators/` nem
  `fixers/` (só nascem em Phase 6 e Phase 7). Criar pacotes vazios agora
  é YAGNI.
- **D-02:** Único arquivo `contracts.py` cobre ambas as ABCs. As duas
  classes são pequenas (~80 linhas cada com docstrings). Split em
  `validador_base.py` + `fixer_base.py` é refactor pós-M2 se crescerem.
- **D-03:** `core/__init__.py` passa a re-exportar 8 símbolos:
  ```python
  from biblio_validador.core.contracts import FixerBase, ValidadorBase
  from biblio_validador.core.dataclasses import Patch, Violacao
  from biblio_validador.core.enums import (
      EstadoPatch, ModoFixer, Scope, Severidade,
  )

  __all__ = [
      "EstadoPatch", "FixerBase", "ModoFixer", "Patch",
      "Scope", "Severidade", "ValidadorBase", "Violacao",
  ]
  ```
  Ordem alfabética (consistente com Phase 3 D-03).
- **D-04:** Subpacote `validators/` (concretos M2) e `fixers/` (concretos
  M5+) são criados em Phase 6 e Phase 7 respectivamente. Cada um terá
  `__init__.py` próprio re-exportando as classes concretas; eles
  importarão `ValidadorBase`/`FixerBase` de `biblio_validador.core`.

### Forma das ABCs (D-05..D-08)

- **D-05:** Usar `abc.ABC` + `@abstractmethod`. Justificativa: success
  criterion #1 do roadmap exige `TypeError` em **tempo de instanciação**
  quando classe concreta omite `validar()`. `typing.Protocol` (mesmo
  com `runtime_checkable`) só checa conformidade no `isinstance()` ad-hoc
  — não bloqueia instanciação. ABC entrega o invariante diretamente.
- **D-06:** **Não** marcar a ABC como `@dataclass`. ABCs aqui carregam
  apenas atributos de classe (`JSON_SOURCE`, `SCOPE`, `VIOLACAO_IDS`,
  `MODO`) — não instâncias com estado. Subclasses concretas decidem se
  serão dataclass (provavelmente não — vão ser singletons funcionais
  com cache no nível da classe).
- **D-07:** ABCs **não** definem `__init__`. Subclasses concretas
  herdam o `__init__` default de `object` (sem args). `carregar_regras()`
  é `@classmethod` (D-12) e o cache é class-level (D-13) — não há
  estado de instância para inicializar. Validadores/fixers concretos
  são, na prática, namespaces de funções com classmethod.
- **D-08:** Usar `typing.ClassVar` para anotar todos os atributos de
  classe declarados na ABC (`JSON_SOURCE: ClassVar[Path]`,
  `SCOPE: ClassVar[Scope]`, etc.). mypy strict (Phase 1 D-13) força
  distinguir ClassVar de instance attr para evitar bug onde subclasse
  esqueça o `ClassVar` e mypy interprete como instance attr.

### Atributos de classe — `ValidadorBase` (D-09..D-11)

- **D-09:** `JSON_SOURCE: ClassVar[Path]` (Path, não str — consistente
  com Phase 3 D-11 e Phase 2 `Paragrafo.arquivo: Path`). Subclasses
  declaram caminho **absoluto resolvido** ao JSON-fonte. Helper
  `core/contracts.py::_canonical_root() -> Path` retorna a raiz da
  biblioteca canônica (`.../biblioteca_canonica/`) lida via
  `__file__.parents[N]`. Subclasses fazem
  `JSON_SOURCE = _canonical_root() / "02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json"`.
- **D-10:** `SCOPE: ClassVar[Scope]` declara escopo de aplicação:
  - `Scope.PARAGRAFO` — validador opera parágrafo-por-parágrafo (M2 padrão)
  - `Scope.SECAO` — opera por seção (M4 estrutural — ex.: ST-05 Introdução)
  - `Scope.DOCUMENTO` — opera no documento inteiro (M3 agregadores; M4 ST-08 Referências)
  Orchestrator (Phase 50) usa `SCOPE` para roteamento e batching.
- **D-11:** ABC declara dois `@abstractmethod`:
  - `carregar_regras(cls) -> Mapping[str, Any]` — `@classmethod`
  - `validar(self, paragrafos: list[Paragrafo]) -> list[Violacao]`
  Concrete subclasses **devem** implementar ambos para passar
  `TypeError` (success #1).

### Atributos de classe — `FixerBase` (D-12..D-14)

- **D-12:** `VIOLACAO_IDS: ClassVar[frozenset[str]]` declara o conjunto
  de `regra_id` que o fixer cobre. `frozenset` (não `set` nem `list`)
  garante imutabilidade no nível da classe e lookup O(1). Exemplos:
  `VIOLACAO_IDS = frozenset({"cst_012"})` para FXA-05;
  `VIOLACAO_IDS = frozenset({"lex_001", ..., "lex_014"})` para FXA-01.
- **D-13:** `MODO: ClassVar[ModoFixer]` declara o nível de intervenção:
  - `ModoFixer.AUTO` — substituição determinística sem confirmação humana
  - `ModoFixer.ASSISTIDO` — propõe N reescritas, autor escolhe via prompt CLI
  - `ModoFixer.LLM` — chama Claude API para reescrita semântica
  Orchestrator (Phase 51) usa `MODO` para decidir UX (silencioso vs prompt
  vs API call).
- **D-14:** ABC declara dois `@abstractmethod`:
  - `propor_patches(self, v: Violacao, contexto: ContextoFixer) -> list[Patch]`
  - `aplicar(self, patches: list[Patch], modo_interativo: bool) -> AplicacaoResultado`
  E **uma** implementação default concreta:
  - `pode_corrigir(self, v: Violacao) -> bool` — retorna
    `v.regra_id in type(self).VIOLACAO_IDS`. Subclasses sobrescrevem
    apenas se precisarem lógica extra (ex.: filtrar por `severidade`).
    Default cobre o success criterion #3 do roadmap sem boilerplate
    em cada fixer concreto.

### Enum `Scope` (D-15..D-16)

- **D-15:** Adicionar `Scope` em `core/enums.py` (mesmo arquivo que
  `Severidade`/`EstadoPatch`). Enum com valor string snake_case,
  consistente com Phase 2 D-03 + Phase 3 D-14:
  ```python
  class Scope(Enum):
      """Granularidade do alvo de validação (D-10)."""

      PARAGRAFO = "paragrafo"
      SECAO = "secao"
      DOCUMENTO = "documento"
  ```
- **D-16:** Sem método `peso()` em `Scope` — não há ordenação inerente.
  Orchestrator pode mapear para ordem de processamento (PARAGRAFO →
  SECAO → DOCUMENTO) via `match` statement na Phase 50.

### Enum `ModoFixer` (D-17..D-18)

- **D-17:** Adicionar `ModoFixer` em `core/enums.py`. Mesma convenção:
  ```python
  class ModoFixer(Enum):
      """Nível de intervenção de um Fixer (D-13)."""

      AUTO = "auto"
      ASSISTIDO = "assistido"
      LLM = "llm"
  ```
  Substitui o que o Phase 3 documentou como "MODO string livre" — agora
  é tipo enumerado.
- **D-18:** Mapear `ModoFixer → confianca default` é responsabilidade
  do fixer concreto (Phase 7+), não da ABC. ABC só expõe o tipo. Phase 3
  D-17 já registrou: `confianca` em `Patch` é **sem default** — força
  fixer a declarar.

### `carregar_regras()` — semântica e cache (D-19..D-22)

- **D-19:** `carregar_regras` é `@classmethod`. Compila uma vez por
  classe (não por instância) — success criterion #2 exige "compila regex
  1x". Cache class-level via atributo `cls._regras_compiladas:
  ClassVar[Mapping[str, re.Pattern[str]] | None]` inicializado `None` e
  preenchido na primeira chamada (lazy init).
- **D-20:** Implementação default no `ValidadorBase` (não abstract,
  apesar do roadmap listar como contrato):
  1. Se `cls._regras_compiladas is not None`, retorna cache.
  2. Senão: lê `cls.JSON_SOURCE` com `json.loads(path.read_text(encoding="utf-8"))`.
  3. Compila cada `regex_deteccao` do JSON com `re.compile(padrao, re.UNICODE | re.IGNORECASE)`.
  4. Armazena em `cls._regras_compiladas` e retorna.
  Subclasses **podem** sobrescrever se o JSON-fonte precisar de
  pré-processamento custom (ex.: VAL-04 com `exclusoes` por entrada;
  VAL-06 conjunções com 802 entradas e estrutura subtipo→entrada).
  Manter `@abstractmethod` na ABC força a subclasse a estar ciente da
  responsabilidade — mas com helper default disponível via
  `super().carregar_regras()` (não chamamos super em ABC abstrata; usar
  função utilitária `_carregar_json_default(cls)` no módulo).
- **D-21:** Decisão final de D-20: `carregar_regras` é
  **`@abstractmethod`** (não default). A ABC fornece função utilitária
  `_carregar_json_simples(json_source: Path) -> Mapping[str, re.Pattern[str]]`
  que validadores simples (M2 primitivos) chamam dentro do seu
  `carregar_regras` — mantém a obrigação contratual explícita
  (success #1) e oferece o atalho. VAL-06 e M3 agregadores escrevem
  lógica custom sem se sentirem "amarrados" a um default que não serve.
- **D-22:** Tratamento de erro em `_carregar_json_simples`:
  - `FileNotFoundError` propaga (path mal declarado é bug grave —
    falha rápido).
  - `json.JSONDecodeError` propaga (JSON inválido é bug do dataset).
  - `re.error` em `re.compile` propaga com mensagem incluindo o
    `regra_id` para diagnóstico (`raise re.error(f"regra {rid}: {e}") from e`).
  Sem try/except silenciador. PROJECT.md "Constraints" exige
  reprodutibilidade determinística — falha visível > falha silenciosa.

### `pode_corrigir()` default (D-23)

- **D-23:** `FixerBase.pode_corrigir(self, v: Violacao) -> bool` é
  **concreto** na ABC (não abstract):
  ```python
  def pode_corrigir(self, v: Violacao) -> bool:
      """Retorna True se este fixer cobre v.regra_id (D-23)."""
      return v.regra_id in type(self).VIOLACAO_IDS
  ```
  Cobre success criterion #3 do roadmap sem custo. Subclasses
  sobrescrevem só se precisarem refinamento (ex.: filtrar por
  `severidade <= ALERTA`, ou descartar se `principio_canonico_violado is None`).

### `aplicar()` design (D-24..D-25)

- **D-24:** `aplicar` é `@abstractmethod` na ABC, com docstring que
  documenta o contrato (single responsibility):
  - **Não** aplica os patches diretamente em arquivo. Delega ao
    `PatchAplicador` (Phase 5) — que recebe `list[Patch]` e arquivo,
    aplica em ordem reversa, retorna `AplicacaoResultado`.
  - Phase 4 introduz a interface; Phase 5 implementa o aplicador real;
    Phase 7 (Fixer AUTO piloto cst_012) é o primeiro consumidor concreto.
  - Em Phase 4: ABC só declara assinatura
    `aplicar(patches: list[Patch], modo_interativo: bool) -> AplicacaoResultado`.
- **D-25:** Tipo `AplicacaoResultado` é **dataclass nova** declarada em
  `core/contracts.py` (escopo Phase 4):
  ```python
  @dataclass(frozen=True, slots=True)
  class AplicacaoResultado:
      """Resultado de FixerBase.aplicar (D-25)."""
      patches_aceitos: tuple[Patch, ...]
      patches_rejeitados: tuple[Patch, ...]
      patches_suprimidos: tuple[Patch, ...]
      bytes_modificados: int
  ```
  Frozen+slots por consistência com `Violacao`. Tuple-only nas coleções
  (Phase 3 D-07). Não cria método `to_dict()` agora — só quando
  Phase 58 (ORC-09 Output JSON) precisar.

### `ContextoFixer` — argumento de `propor_patches` (D-26..D-27)

- **D-26:** Tipo `ContextoFixer` é **dataclass nova** em
  `core/contracts.py`:
  ```python
  @dataclass(frozen=True, slots=True)
  class ContextoFixer:
      """Contexto que o orchestrator passa ao fixer (D-26)."""
      paragrafo: Paragrafo
      todas_violacoes_paragrafo: tuple[Violacao, ...]
      regras_compiladas: Mapping[str, "re.Pattern[str]"]
  ```
  - `paragrafo` — texto NFC + offsets do parser (Phase 2)
  - `todas_violacoes_paragrafo` — fixers M3 agregados precisam ver
    todas as violações do parágrafo (não só `v`)
  - `regras_compiladas` — fixer reusa o regex pré-compilado pelo
    validador irmão; evita recompilar no fixer
- **D-27:** `Mapping` (não `dict`) na assinatura — covariância. Importar
  de `collections.abc`.

### Segurança de tipos (D-28..D-30)

- **D-28:** Type hints 100% em `contracts.py`. Inclui forward refs
  para `re.Pattern[str]` (string literal nas anotações onde Python
  ainda não tem o tipo no escopo) — alternativa: `from __future__
  import annotations` no topo do arquivo. **Decisão:** usar
  `from __future__ import annotations` no `contracts.py` para
  consistência com PEP 563 e simplificar refs circulares (Paragrafo
  vem de `parser.types`, Violacao de `core.dataclasses`).
- **D-29:** **Não** importar `Paragrafo` no topo de `contracts.py` se
  causar ciclo. Análise: `parser.types` não importa nada de
  `core/`. Hoje sem ciclo. Importar direto:
  `from biblio_validador.parser.types import Paragrafo`. Se futuro
  módulo criar ciclo, mover import para `TYPE_CHECKING` block.
- **D-30:** mypy strict herdado de Phase 1 D-13. Toda subclasse omitindo
  `validar()` será ainda flagrada por **mypy** antes mesmo de instanciar
  (em adição à ABC runtime check). Isso reforça success criterion #1.

### Testes (D-31..D-34)

- **D-31:** `tests/core/test_contracts.py` cobre os 4 success criteria
  do roadmap, sem extras desnecessários:
  1. **Test contract violation:** classe `_ValidadorIncompleto(ValidadorBase)`
     que omite `validar()` deve disparar `TypeError` em
     `_ValidadorIncompleto()`. Mesmo para `_FixerIncompleto(FixerBase)`
     omitindo `propor_patches()`.
  2. **Test `carregar_regras()`:** classe fake `_ValidadorFake` com
     `JSON_SOURCE = fixture_path` e `SCOPE = Scope.PARAGRAFO`. Chamar
     `_ValidadorFake.carregar_regras()` retorna `Mapping[str, re.Pattern]`.
     Chamar 2x retorna o **mesmo objeto** (cache hit) — verificar
     `id()` para confirmar.
  3. **Test `pode_corrigir`:** `_FixerFake` com
     `VIOLACAO_IDS = frozenset({"cst_999"})`. Violação com
     `regra_id="cst_999"` → `True`; com `regra_id="cst_001"` → `False`.
  4. **Test ABC import smoke:** `from biblio_validador.core import
     ValidadorBase, FixerBase, Scope, ModoFixer, AplicacaoResultado,
     ContextoFixer` resolve sem erro.
- **D-32:** `tests/core/fixtures/regras_fake.json` — JSON minúsculo:
  ```json
  {
    "tipo": "fake",
    "entradas": [
      {"id": "cst_999", "regex_deteccao": "\\bfake\\b"}
    ]
  }
  ```
  Vive em `tests/` (não em `02_escrita/`) — fixtures de teste não
  poluem dataset canônico.
- **D-33:** Adicionar 3 testes de erro em `_carregar_json_simples`:
  - `FileNotFoundError` quando JSON_SOURCE aponta para arquivo
    inexistente
  - `json.JSONDecodeError` quando JSON malformado (fixture
    `regras_malformadas.json` com `{` apenas)
  - `re.error` propagada quando regex inválido (fixture
    `regras_regex_invalido.json` com `(?P<unfinished` ou similar)
- **D-34:** Coverage alvo `>= 95%` em `core/contracts.py`. Reusa
  `pytest --cov=biblio_validador.core` configurado em Phase 1.
  Módulo é pequeno (estimado 120-150 linhas com docstrings) — alvo
  factível.

### Tooling (D-35..D-37)

- **D-35:** `ruff line-length = 80` herdado. Quebrar docstrings/long-strings
  em vez de violar.
- **D-36:** Sem `loguru` em `core/contracts.py` — `core/` é puro modelo
  (Phase 3 D-33 herdada). Logging começa nas implementações
  concretas (validadores M2+).
- **D-37:** Type hints validados via `mypy --strict` antes do commit
  final (Phase 1 D-13).

### Folded Todos
Nenhum todo pendente foi mapeado para esta phase (`todo match-phase 4`
retornou 0 matches em 2026-05-05).

### Claude's Discretion

- Texto exato de docstrings PT-BR (manter convenção do projeto).
- Estrutura interna dos testes — parametrizar via
  `@pytest.mark.parametrize` ou separar é decisão do executor.
- Implementação concreta de `_carregar_json_simples`: usar `re.UNICODE`
  vs `re.UNICODE | re.IGNORECASE` é decisão por validador concreto;
  ABC pode aceitar `flags` opcional. Avaliar e decidir no plan.
- Se vale a pena adicionar `__repr__` customizado em
  `AplicacaoResultado` ou `ContextoFixer` para logs.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requisitos
- `.planning/REQUIREMENTS.md` §"Core (M1)" — CORE-04 (ABC `ValidadorBase`)
  e CORE-05 (ABC `FixerBase`)
- `.planning/ROADMAP.md` §"Phase 4: Contratos ABC" — 4 success criteria

### Stack e versões (Phase 1 research)
- `.planning/research/STACK.md` §"Modelagem de Patches (Decisao de
  Arquitetura)" — confirma `dataclasses` stdlib + `abc.ABC`
- `.planning/research/SUMMARY.md` — Python 3.13+, type hints obrigatórios
- `.planning/research/PITFALLS.md` — drift de offsets (informa contrato
  de `Patch.aplicar` em D-24)

### Phase 1 (decisões herdadas)
- `.planning/phases/01-bootstrap/01-CONTEXT.md` §"Identidade do pacote"
  — D-01 (`biblio_validador`), D-02 (layout `src/`), D-13 (mypy strict)

### Phase 2 (decisões herdadas)
- `.planning/phases/02-parser-markdown/02-CONTEXT.md` §"Localização e
  shape do `Paragrafo`" — `Paragrafo.linha_inicio` 1-based informa
  contrato de `validar(paragrafos)` em D-11
- `src/biblio_validador/parser/types.py` — `Paragrafo` é o tipo de
  entrada de `ValidadorBase.validar`
- `src/biblio_validador/parser/__init__.py` — template de re-export

### Phase 3 (decisões herdadas)
- `.planning/phases/03-dataclasses-core/03-CONTEXT.md` §"Forma das
  dataclasses" D-05/D-07 — frozen+slots é o template seguido por
  `AplicacaoResultado` (D-25) e `ContextoFixer` (D-26)
- `.planning/phases/03-dataclasses-core/03-CONTEXT.md` §"Enum
  `Severidade`/`EstadoPatch`" D-14/D-20 — convenção `enum.Enum` com
  valor string snake_case herdada por `Scope` (D-15) e `ModoFixer` (D-17)
- `.planning/phases/03-dataclasses-core/03-CONTEXT.md` §"Validação
  invariante" D-22..D-24 — `__post_init__` em frozen dataclasses
  (template para `AplicacaoResultado`)
- `src/biblio_validador/core/dataclasses.py` — `Violacao`, `Patch`
  importados pelas ABCs
- `src/biblio_validador/core/enums.py` — `Severidade`, `EstadoPatch`
  já presentes; Phase 4 adiciona `Scope` + `ModoFixer` no mesmo arquivo
- `src/biblio_validador/core/__init__.py` — re-export estendido
  (Phase 4 D-03)
- `.planning/phases/03-dataclasses-core/03-PATTERNS.md` — pattern map
  Phase 3 (template para Phase 4 PATTERNS.md)

### JSON-fonte que carregar_regras() consome
- `02_escrita/termos_proibidos/01_termos_lexicais_proibidos.json` —
  formato `lex_NNN`
- `02_escrita/termos_proibidos/02_expressoes_conectivas_proibidas.json`
  — formato de regex composto
- `02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json`
  — formato `cst_NNN`, exemplo concreto de schema com `regex_deteccao`,
  `exclusoes`, `observacao` (informa `_carregar_json_simples` D-21)
- `02_escrita/termos_proibidos/05_sinais_graficos_proibidos.json` —
  contém regex com lookahead negativo (informa que regex devem ser
  preservados literais via `re.compile`)
- `02_escrita/termos_proibidos/06_regras_coocorrencia.json` — formato
  `coc_NNN` agregador (informa `Scope.DOCUMENTO`)

### Projeto e regras globais
- `.planning/PROJECT.md` §"Constraints" — Python 3.13+, type hints,
  max 80 chars/linha
- `.planning/PROJECT.md` §"Key Decisions" — "1 validador por JSON, não
  monolito"; "3 níveis de fixer (AUTO/ASSISTIDO/LLM)"
- `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/CLAUDE.md`
  §"Constraints" — `dataclasses` stdlib + módulo padrão `re`
- `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` §"Regras para o
  Agente" regra 9 (type hints obrigatórios)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/biblio_validador/core/dataclasses.py`** (Phase 3) já exporta
  `Violacao` e `Patch` — Phase 4 importa e usa em assinaturas das ABCs.
- **`src/biblio_validador/core/enums.py`** (Phase 3) já tem `Severidade`
  e `EstadoPatch`. Phase 4 **estende** o arquivo adicionando `Scope` e
  `ModoFixer` — sem criar arquivo novo.
- **`src/biblio_validador/core/__init__.py`** (Phase 3) já tem
  `__all__ = ["EstadoPatch", "Patch", "Severidade", "Violacao"]`.
  Phase 4 adiciona 4 símbolos: `FixerBase`, `ModoFixer`, `Scope`,
  `ValidadorBase` (e dois tipos auxiliares se decidido expor:
  `AplicacaoResultado`, `ContextoFixer`).
- **`src/biblio_validador/parser/types.py`** (Phase 2) exporta
  `Paragrafo` — Phase 4 importa em `contracts.py` para anotação de
  `validar(paragrafos: list[Paragrafo])`.
- **`pyproject.toml`** já tem `pytest>=9.0.3` + `pytest-cov>=7.1.0`.
  Phase 4 reusa sem tocar em deps.
- **`tests/core/`** já existe (Phase 3) com `test_dataclasses.py` —
  Phase 4 adiciona `test_contracts.py` no mesmo subpacote, criando
  `tests/core/fixtures/` para JSONs minúsculos de teste.
- **`tests/parser/test_markdown.py`** (Phase 2) — template formal de
  organização de testes (fixtures, `@pytest.mark.parametrize`,
  PT-BR docstrings).

### Established Patterns

- **`@dataclass(frozen=True, slots=True)`** é a forma canônica
  (Phase 2/3). Phase 4 segue para `AplicacaoResultado` e `ContextoFixer`.
- **`enum.Enum` com valor string snake_case** é a forma canônica.
  Phase 4 segue para `Scope` e `ModoFixer`.
- **`ClassVar` para atributos de classe** é obrigatório sob mypy strict.
- **PT-BR em docstrings, código em English ASCII**. Mantido.
- **Type hints 100%** (CLAUDE.md regra 9). Mantido.
- **Sem `logging`/`print` em `core/`** — `core/` é puro modelo + contrato.
  Logging começa em validadores concretos (Phase 6+).
- **`from __future__ import annotations`** já é convenção em
  `parser/markdown.py` (Phase 2) — Phase 4 segue em `contracts.py`.

### Integration Points

- **Phase 5 (PatchAplicador)** consome `list[Patch]` (Phase 3) e é
  invocado pelo `FixerBase.aplicar()` (Phase 4). PatchAplicador é a
  **implementação** da semântica que `aplicar()` declara.
- **Phase 6 (Validador piloto cst_012)** é o **primeiro consumidor**
  concreto de `ValidadorBase`. Validará Phase 4: se a ABC for incompleta,
  Phase 6 quebra.
- **Phase 7 (Fixer AUTO piloto cst_012)** é o **primeiro consumidor**
  concreto de `FixerBase` + `AplicacaoResultado` + `ContextoFixer`.
  `MODO = ModoFixer.AUTO`, `VIOLACAO_IDS = frozenset({"cst_012"})`.
- **Phase 8 (Orchestrator Mínimo)** lê `SCOPE` para roteamento e
  `MODO` para UX. Lê `severidade` para `AUDITORIA.md` (já em Phase 3).
- **Phases 10-17 (M2 primitivos)** todas implementam `ValidadorBase`.
  Cada uma usa `_carregar_json_simples` (D-21) ou variante.
- **Phase 18 (AGR-01 Coocorrência)** implementa `ValidadorBase` com
  `SCOPE = Scope.PARAGRAFO` mas consome `list[Violacao]` agregado
  pelos primitivos — pode demandar override de `validar()` com
  assinatura compatível mas semântica diferente.
- **Phase 19 (AGR-02 Escrita Canônica)** preenche
  `principio_canonico_violado` em `Violacao` (Phase 3 D-09).
- **Phases 32-49 (M5/M6/M7 fixers)** todas implementam `FixerBase`.
  M7 (LLM) sobrescreve `propor_patches` para chamar Claude API
  (Phase 42 FXL-01).
- **Phase 50 (ORC-01 Orchestrator validador)** roteia por `SCOPE`.
- **Phase 51 (ORC-02 Orchestrator fixer)** roteia por `MODO` e muta
  `patch.estado` (Phase 3 D-20).

</code_context>

<specifics>
## Specific Ideas

- **`abc.ABC` em vez de `typing.Protocol`** (D-05): Protocol é
  estrutural — não enforça contrato em **instanciação**. Roadmap
  success #1 exige `TypeError` na instanciação. ABC entrega isso
  sem custo. Protocol é útil para tipagem ad-hoc; aqui queremos
  o invariante forte.
- **`ClassVar[frozenset[str]]` em `VIOLACAO_IDS`** (D-12): mutabilidade
  de classe é uma armadilha clássica (`set` mutável compartilhado entre
  instâncias é bug latente). `frozenset` é a forma canônica de "set
  imutável de classe".
- **`pode_corrigir()` concreto na ABC** (D-23): cobrir success
  criterion #3 com uma linha em vez de exigir reimplementação em cada
  fixer concreto. Subclasses sobrescrevem só se precisarem refinamento.
- **`AplicacaoResultado` como dataclass nova em Phase 4** (D-25):
  alternativa era declarar via tuple `(aceitos, rejeitados, suprimidos)`.
  Dataclass é mais explícita, mais auto-documentada, mais segura
  contra ordem-de-argumentos errada, e custa nada (frozen+slots).
- **`carregar_regras()` mantém `@abstractmethod`** (D-21): poderia ser
  default. Manter abstract força subclasse a estar **ciente** da
  responsabilidade. Função utilitária `_carregar_json_simples` cobre
  o caso comum sem amarrar arquitetura.
- **`from __future__ import annotations` em `contracts.py`** (D-28):
  permite `re.Pattern[str]` em anotação sem precisar importar `re`
  em runtime, resolve forward refs naturalmente, é convenção já em
  `parser/markdown.py`.
- **Cache class-level via `cls._regras_compiladas`** (D-19): alternativa
  era `functools.lru_cache` no método. `lru_cache` em método com
  `self`/`cls` cria caches independentes por classmethod call e
  pode reter referências a `cls` indefinidamente — atributo de classe
  explícito é mais simples e auditável.

</specifics>

<deferred>
## Deferred Ideas

- **State machine enforcement em `EstadoPatch`** (já deferred em Phase 3):
  Phase 51 (ORC-02 Orchestrator fixer) decide se vale.
- **Subclasse `ValidadorAgregadoBase`** com assinatura
  `validar(violacoes_componentes: list[Violacao]) -> list[Violacao]`:
  adiar para Phase 18 (AGR-01) onde aparece o caso real. Phase 4 não
  cria hierarquia preventiva — agregadores podem usar `ValidadorBase`
  com `SCOPE = Scope.DOCUMENTO` e ignorar o `paragrafos` arg ou
  consumi-lo em outra interface (decisão de Phase 18).
- **LSP server** (já deferred em REQUIREMENTS v2): Phase 4 não pensa
  em integração editor.
- **`ValidadorBase.versao()`** retornando versão do JSON-fonte
  (rastreabilidade pós-evolução de regras): adiar para Phase 20
  (AGR-03 Versionamento) que adiciona o campo `versao` aos JSONs.
- **`FixerBase.confianca_minima`** ClassVar para guardrail:
  adiar para Phase 49 (FXL-08 Guardrail LLM) onde a regra real será
  `if patch.confianca < cls.confianca_minima: descartar`.
- **Async `validar`/`propor_patches`** para validadores que precisem
  I/O (ex.: validador que consulta API externa): out of scope —
  PROJECT.md "Constraints" exige zero rede em validadores.
- **Hooks `pre_validar` / `post_validar`** para instrumentação:
  out of scope — orchestrator (Phase 50) faz instrumentação ao redor,
  não dentro da ABC.
- **Plugin system** com discovery dinâmico de validadores:
  out of scope — registro estático em Phase 50 (`VALIDADORES =
  [TermosLexicaisValidador, ...]`) é suficiente para 60-fase
  roadmap.
- **`__hash__` customizado em `AplicacaoResultado`** ou
  `ContextoFixer`: frozen+slots dá hash automático; não forçar
  custom até demanda real.

</deferred>

---

*Phase: 04-contratos-abc*
*Context gathered: 2026-05-05 (auto-mode)*
