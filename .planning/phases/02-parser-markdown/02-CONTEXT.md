# Phase 2: Parser Markdown - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning
**Mode:** `--auto` (decisões auto-resolvidas pelo recomendado, log abaixo)

<domain>
## Phase Boundary

Parser CommonMark + footnotes para arquivos `.md` que segmenta em
`list[Paragrafo]` com offsets **byte-exact** sobre source normalizado em **NFC**.
Cobre **CORE-01** (parser MD) e **CORE-11** (NFC). Parser `.tex` (CORE-01 lado
LaTeX) fica para **Phase 16** (VAL-07). Dataclasses `Violacao`/`Patch` ficam
para **Phase 3**. PatchAplicador fica para **Phase 5**. Validador piloto cst_012
fica para **Phase 6**.

Phase 2 entrega exclusivamente: módulo `parser/` com `ParserMd.parsear(path)`,
dataclass `Paragrafo`, enum `TipoSecao` e os tipos de apoio que o parser precisa
para emitir parágrafos identificáveis linha a linha.

</domain>

<decisions>
## Implementation Decisions

### Localização e shape do `Paragrafo`

- **D-01:** Novo módulo `src/biblio_validador/parser/` com `__init__.py`,
  `types.py` (dataclass `Paragrafo` + enum `TipoSecao`) e `markdown.py`
  (classe `ParserMd`). `Paragrafo` é parser-internal — não vai junto com
  `Violacao`/`Patch` (Phase 3, `core/dataclasses.py`).
- **D-02:** `Paragrafo` é `@dataclass(frozen=True, slots=True)`. Imutável
  porque o parser produz uma vez e o resto do pipeline lê-only. Campos:
  - `arquivo: Path`
  - `indice: int` — ordem topológica no documento (0-based)
  - `tipo: TipoSecao`
  - `nivel_heading: int | None` — apenas se `tipo` corresponde a heading
    (1-6 markdown), `None` para parágrafos do corpo
  - `texto: str` — slice raw do source NFC entre offsets, preservando
    marcadores markdown (`*`, `**`, `_`, `[^n]`). Validadores operam sobre
    prosa PT-BR; marcadores não atrapalham regex `\b...\b`
  - `linha_inicio: int` (1-based, alinhado com `Violacao.linha_inicio`)
  - `linha_fim: int` (1-based, inclusivo)
  - `offset_bytes: int` — offset absoluto em bytes UTF-8 dentro do source NFC
  - `len_bytes: int` — comprimento em bytes UTF-8 do trecho
  - `ref_nota: str | None` — preenchido apenas quando `tipo == NOTA_RODAPE`,
    contém o label da footnote (`"n"` em `[^n]`)
  - `paragrafo_pai_idx: int | None` — índice do parágrafo do corpo que
    referencia esta nota (resolvido via `footnote_ref` na 1ª ocorrência);
    `None` se a referência não tem corpo localizável

### Enum `TipoSecao`

- **D-03:** `TipoSecao` é `enum.Enum` (não `StrEnum`) com valores explícitos
  string em CAIXA_BAIXA snake (mais legíveis em logs). Vocabulário fechado
  alinhado aos 11 JSONs de `01_templates/artigo_cientifico/caracteristicas/`:
  - `TITULO`, `AUTORES`, `RESUMO`, `PALAVRAS_CHAVE`, `ABSTRACT`, `KEYWORDS`,
    `SUMARIO`, `INTRODUCAO`, `SECAO`, `CONCLUSAO`, `REFERENCIAS`,
    `NOTA_RODAPE`, `CORPO`, `DESCONHECIDO`
- **D-04:** `CORPO` = parágrafo do corpo de uma `SECAO` (texto discursivo
  abaixo de heading não-canônico). `DESCONHECIDO` = parágrafo antes do 1º
  heading legível (cabeçalho institucional, etc.) ou heading não classificado.

### Classificação de seção por heading

- **D-05:** Classificação **heading-text-based** com dicionário canônico
  carregado uma vez via `classmethod` em `ParserMd._carregar_mapa_secao()`.
  Mapa inicial (chave = heading normalizado: `nfkd + casefold + strip de
  pontuação e espaços extras`):

  | Heading reconhecido | TipoSecao |
  |---|---|
  | `resumo` | RESUMO |
  | `palavras-chave` / `palavraschave` | PALAVRAS_CHAVE |
  | `abstract` | ABSTRACT |
  | `keywords` | KEYWORDS |
  | `sumario` / `sumário` | SUMARIO |
  | `introducao` / `introdução` | INTRODUCAO |
  | `consideracoes finais` / `considerações finais` / `conclusao` / `conclusão` | CONCLUSAO |
  | `referencias` / `referências` | REFERENCIAS |
  | `notas` / `notas de rodape` / `notas de rodapé` | NOTA_RODAPE (heading container; corpos individuais ainda viram `Paragrafo` próprio) |

- **D-06:** Heading **nível 1 (h1) único e primeiro** do documento → `TITULO`,
  independente do texto (artigos abntex2 declaram título via `# TITULO DO
  ARTIGO`). 2º+ heading h1 cai em `SECAO`.
- **D-07:** Parágrafos de corpo **herdam o `tipo` da seção mais recente**
  reconhecida (ex.: parágrafos sob `# INTRODUÇÃO` recebem `tipo=INTRODUCAO`,
  não `CORPO`). Isso permite que ST-05 (Phase 25) detecte citação proibida
  em `INTRODUCAO` filtrando `[p for p in paragrafos if p.tipo == INTRODUCAO]`
  sem re-parse. `CORPO` fica reservado para parágrafos dentro de `SECAO`
  genérica.
- **D-08:** Headings com nível >2 (h3+) emitem `Paragrafo(tipo=SECAO,
  nivel_heading=3+)`. ST-06 (Phase 26) usa `nivel_heading > 2` para detectar
  hierarquia profunda proibida — Phase 2 só captura, não valida.

### Offsets byte-exact

- **D-09:** Implementação em **dois passos**:
  1. Ao ler o arquivo: normalizar source para NFC, manter como `bytes` UTF-8;
     pré-computar `linha_offsets: list[int]` onde
     `linha_offsets[n]` = offset em bytes do início da linha (1-based, com
     `linha_offsets[0] = 0` sentinela).
  2. Tokenizar com `markdown-it-py` 4.0.0 + `mdit_py_plugins.footnote.footnote_plugin`.
     Para cada `block_token` com `map=[start, end]` (0-indexed half-open):
     - `linha_inicio = start + 1`
     - `linha_fim = end` (markdown-it usa half-open; `end` já é a próxima
       linha após o bloco — `linha_fim` 1-based inclusive = `end`)
     - `offset_bytes = linha_offsets[start]`
     - `len_bytes = linha_offsets[end] - linha_offsets[start]` (truncar
       trailing newline se presente — calcular sobre bytes do source)
     - `texto = source_nfc_bytes[offset_bytes:offset_bytes+len_bytes].decode("utf-8")`
- **D-10:** O parser **não calcula `col_inicio`/`col_fim`** dos parágrafos
  (sempre 0 para blocos). Esses campos pertencem a `Violacao` (Phase 3),
  produzidos pelos validadores ao localizar o trecho violador dentro do
  `texto` do parágrafo. Phase 2 fornece a base para isso (offsets de bloco
  + texto).

### NFC normalization (CORE-11)

- **D-11:** Normalizar **o source inteiro para NFC uma única vez** logo após
  ler o arquivo (`unicodedata.normalize("NFC", source_str)`), antes de
  qualquer tokenização ou cálculo de offset. Todos os offsets, bytes,
  índices retornados referem-se exclusivamente ao **source NFC**.
- **D-12:** Documentar a invariante em docstring de `ParserMd.parsear`:
  *"Offsets são relativos ao source UTF-8 NFC. Arquivos em NFD (ex.: macOS)
  são convertidos silenciosamente. Validadores operam sempre em NFC."*
- **D-13:** O `PatchAplicador` (Phase 5) lê o arquivo, normaliza para NFC,
  aplica patches sobre os bytes NFC e grava de volta em NFC. Isso é
  **decidido aqui em Phase 2** porque é a única forma de manter consistência
  entre offsets capturados e bytes alterados. (Phase 5 herda essa decisão.)

### Footnotes

- **D-14:** `mdit_py_plugins.footnote.footnote_plugin` registrado no
  `MarkdownIt` é mandatório (sem ele, footnotes viram texto cru). Confirmado
  pela STACK.md.
- **D-15:** `[^n]` no corpo de um parágrafo permanece **embutido no `texto`
  do parágrafo pai** (preservando offset). O parser **não remove a referência**.
  Validadores que quiserem ignorá-la fazem `re.sub(r"\[\^[^\]]+\]", " ", texto)`
  no momento da regex.
- **D-16:** O corpo da footnote (`[^n]: corpo da nota...`) vira um
  `Paragrafo` próprio com:
  - `tipo = TipoSecao.NOTA_RODAPE`
  - `ref_nota = "n"` (label sem `[^]` e sem `:`)
  - `paragrafo_pai_idx` = índice do **primeiro parágrafo** que contém
    `[^n]` no `texto`. Resolução em segundo passo após todos os parágrafos
    estarem segmentados (porque footnote pode aparecer no source antes
    da referência).
  - Footnote sem referência localizável → `paragrafo_pai_idx = None`
    (validador ST-10 sinaliza como "nota órfã" em Phase 30).

### Granularidade

- **D-17:** Phase 2 segmenta **apenas em parágrafos**. Frases e linhas
  individuais não são entidades de saída. O REQUIREMENTS menciona
  "parágrafos + frases + linhas" como cobertura conceitual; "frases" será
  segmentação on-demand dentro dos validadores que precisarem (M3+) usando
  helper a ser criado se necessário. Phase 2 não cria esse helper.

### Encoding e bordas

- **D-18:** Leitura **UTF-8 strict**. BOM (codepoint `U+FEFF` no início) é removido
  silenciosamente após decode. Arquivo em encoding inválido → `UnicodeDecodeError`
  propagado (sem fallback `latin-1`). `loguru.logger.error` emite mensagem
  com path antes de relançar.
- **D-19:** Arquivo vazio ou só whitespace → retorna `[]` (não levanta).
  Arquivo inexistente → `FileNotFoundError` propagado.
- **D-20:** Linhas em CRLF (`\r\n`) são normalizadas para LF (`\n`) **antes**
  de NFC. Justificativa: markdown-it usa LF; manter offsets coerentes.
  `linha_offsets` é calculado sobre o source LF+NFC.

### API pública do módulo `parser`

- **D-21:** `ParserMd` é classe (não função top-level) para permitir
  injeção futura de configuração (mapa de seções customizado, callbacks de
  log). Phase 2 expõe apenas `__init__()` sem args e `parsear(path: Path) ->
  list[Paragrafo]`.
- **D-22:** Re-export em `parser/__init__.py`:
  ```python
  from biblio_validador.parser.markdown import ParserMd
  from biblio_validador.parser.types import Paragrafo, TipoSecao

  __all__ = ["ParserMd", "Paragrafo", "TipoSecao"]
  ```
  Permite `from biblio_validador.parser import ParserMd` em validadores.

### Tooling de qualidade aplicado

- **D-23:** Type hints em **100%** das assinaturas públicas e privadas
  (CLAUDE.md regra 9 + `mypy strict` herdado de Phase 1).
- **D-24:** `ruff` `line-length = 80` herdado. Quebra agressiva em
  comprehensions e regex de classificação de heading (mapa pode ficar longo).
- **D-25:** Logging via `loguru` — primeiro consumidor real (Phase 1 D-19
  adia para cá). `parser/markdown.py` faz `from loguru import logger` e
  emite `INFO` ao iniciar parse, `DEBUG` por bloco tokenizado, `WARNING`
  para footnotes órfãs.

### Testes (smoke obrigatório)

- **D-26:** `tests/parser/test_markdown.py` cobre:
  1. Arquivo com 1 parágrafo simples → `len(paragrafos) == 1`,
     `linha_inicio == linha_fim == 1`, `offset_bytes == 0`,
     `tipo == DESCONHECIDO` (nenhum heading antes).
  2. Arquivo com 3 headings canônicos (`# Título`, `## RESUMO`,
     `## INTRODUÇÃO`) e parágrafos sob cada um → cada parágrafo herda
     `tipo` da seção pai (`TITULO`, `RESUMO`, `INTRODUCAO`).
  3. Acento composto (NFD `é`) no input → `texto` contém `é` (NFC).
  4. `[^1]: nota...` → `Paragrafo(tipo=NOTA_RODAPE, ref_nota="1")` separado;
     `paragrafo_pai_idx` aponta para parágrafo que contém `[^1]`.
  5. Trecho real do artigo Eólica Nordeste (5-10 parágrafos do início) →
     parágrafos retornados, `linha_inicio` confere com inspeção manual.
- **D-27:** Não há benchmark de performance em Phase 2 (Phase 17 = VAL-08
  benchmark). Apenas verificar que parse de 30k palavras não quebra (não
  há contrato de tempo aqui ainda).

### Folded Todos
Nenhum todo pendente foi mapeado para esta phase.

### Claude's Discretion

- Estrutura interna de helpers privados em `markdown.py` (ex.: separar
  `_construir_linha_offsets`, `_classificar_heading`, `_resolver_footnotes`).
- Texto exato das mensagens de log `loguru`.
- Se vale a pena criar `parser/heading_map.py` separado para o dicionário
  de classificação ou manter inline em `types.py`.
- Mensagens de erro/warning para footnotes órfãs.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Stack e versões
- `.planning/research/STACK.md` §"Parser Markdown" — confirma
  `markdown-it-py>=4.0.0` + `mdit-py-plugins`; menciona `token.map=[start_line,
  end_line]` como mecanismo central
- `.planning/research/STACK.md` §"Sources" — link markdown-it-py docs
  https://markdown-it-py.readthedocs.io/en/latest/using.html
- `.planning/research/SUMMARY.md` §"Recommended Stack" — stdlib-first

### Pitfalls relevantes a Phase 2
- `.planning/research/PITFALLS.md` §"Pitfall 2: Drift de Offsets" — embora
  o pitfall seja sobre `PatchAplicador` (Phase 5), Phase 2 produz os offsets
  byte-exact que sustentam o invariante. Decisão D-09 + D-13 deriva daqui.
- `.planning/research/PITFALLS.md` §"Pitfall 5+ (NFC)" se houver — NFC vs
  NFD em macOS é risco conhecido; D-11/D-12 cobrem.

### Requisitos
- `.planning/REQUIREMENTS.md` §"Core (M1)" — CORE-01 (parser `.md`
  CommonMark + footnotes) e CORE-11 (NFC) cobertos exclusivamente nesta
  phase. Lado `.tex` de CORE-01 é Phase 16.
- `.planning/ROADMAP.md` §"Phase 2: Parser Markdown" — 4 success criteria.

### Templates ABNT (informa enum `TipoSecao`)
- `01_templates/artigo_cientifico/caracteristicas/01_titulos.json` — TITULO
- `01_templates/artigo_cientifico/caracteristicas/02_autores.json` — AUTORES
- `01_templates/artigo_cientifico/caracteristicas/03_resumo_palavras_chave.json` —
  RESUMO + PALAVRAS_CHAVE + ABSTRACT + KEYWORDS
- `01_templates/artigo_cientifico/caracteristicas/03b_sumario.json` — SUMARIO
- `01_templates/artigo_cientifico/caracteristicas/04_introducao.json` — INTRODUCAO
- `01_templates/artigo_cientifico/caracteristicas/05_secoes.json` — SECAO
  (hierarquia 2 níveis informará D-08)
- `01_templates/artigo_cientifico/caracteristicas/06_conclusao.json` — CONCLUSAO
- `01_templates/artigo_cientifico/caracteristicas/07_referencias.json` — REFERENCIAS
- `01_templates/artigo_cientifico/caracteristicas/09_notas_rodape.json` — NOTA_RODAPE

### Phase 1 (decisões herdadas)
- `.planning/phases/01-bootstrap/01-CONTEXT.md` §"Identidade do pacote" —
  D-01 (nome), D-02 (layout `src/`), D-19 (loguru adiado para Phase 2)
- `.planning/phases/01-bootstrap/01-PLAN.md` (se existir) — confirma deps
  instaladas via `uv sync`

### Caso de teste real
- `Artigos/Professora Gina Pompeu/Energia Eólica Nordeste/artigo_final/artigo.md` —
  fonte canônica de teste E2E. Phase 2 valida sucesso #4 contra trecho
  inicial deste arquivo.

### Projeto e regras globais
- `.planning/PROJECT.md` §"Constraints" — Python 3.13+, type hints, max 80
- `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/CLAUDE.md` —
  regras locais de stack
- `/home/kalyllamarck/projetos/Doutorado/CLAUDE.md` §"Regras para o Agente"

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`pyproject.toml`** já declara `markdown-it-py>=4.0.0` e
  `mdit-py-plugins` (Phase 1, D-06). `uv sync` instala automaticamente —
  Phase 2 não toca em deps.
- **`src/biblio_validador/__init__.py`** existe com `__version__ = "0.1.0"`.
  Phase 2 adiciona apenas `parser/` como sub-pacote, sem mexer em raiz.
- **`src/biblio_validador/cli.py`** tem `app = typer.Typer()` esqueleto
  (Phase 1, D-11). Phase 2 **não conecta** o parser ao CLI ainda — só Phase
  6 (validador piloto) ou Phase 8 (orchestrator) precisam disso.

### Established Patterns

- **JSON read-only como fonte de verdade**: o mapa de heading→TipoSecao
  pode futuramente vir de `01_templates/artigo_cientifico/caracteristicas/`,
  mas Phase 2 hardcoda inline para evitar dependência circular (validadores
  estruturais M4 só rodam após M1; carregamento dinâmico de mapa de seção
  vira refactor pós-M1 se necessário).
- **`uv` único gerenciador**: nenhum `pip install`/`requirements.txt`.
- **`loguru` único logger**: `from loguru import logger` em todo módulo
  novo. Sem `logging.getLogger(__name__)`.

### Integration Points

- **Phase 3 (Dataclasses Core)** consome `Paragrafo` ao construir `Violacao`
  (campos `linha_inicio`, `linha_fim` herdados; `col_inicio`/`col_fim`
  calculados pelos validadores).
- **Phase 4 (Contratos ABC)** define `ValidadorBase.validar(paragrafos:
  list[Paragrafo]) -> list[Violacao]`. Assinatura confirma que o tipo
  de entrada é `list[Paragrafo]` definido aqui.
- **Phase 5 (PatchAplicador)** assume D-13: arquivo é lido em UTF-8 →
  CRLF→LF → NFC antes de qualquer mutação. Patches operam em coordenadas
  do source NFC.
- **Phase 6 (Validador piloto cst_012)** é o primeiro consumidor real do
  parser. Phase 2 roda em isolamento até lá.

</code_context>

<specifics>
## Specific Ideas

- **Slice raw vs token children**: optei por slice byte direto do source
  (D-09) em vez de extrair `text` via `token.children`. Razão: `children`
  perde os marcadores markdown e força recomputar offsets dentro do bloco.
  Slice byte preserva offsets perfeitamente e validadores PT-BR toleram
  marcadores `*` `**` `_` `[^n]` ao redor de matches `\b`.
- **Herança de `tipo` por seção** (D-07): o REQUIREMENTS implícito é que
  ST-05 detecta citação na INTRODUÇÃO. A forma natural de cumprir isso é
  taggear cada parágrafo com a seção pai no parser, em vez de ST-05
  re-parsear o documento.
- **NFC source-único** (D-11): qualquer alternativa (normalizar por
  parágrafo, comparar pré/pós) abre porta para drift de offset. Source
  inteiro NFC desde a leitura é o único modelo que sustenta byte-exact.

</specifics>

<deferred>
## Deferred Ideas

- **Segmentação por frase** (`Frase` dataclass): adiar para o primeiro
  validador que precise — provavelmente VAL-06 conjunções (Phase 15) ou
  AGR (M3). Não criar agora.
- **Mapa de seção dinâmico** (carregado de `01_templates/.../caracteristicas/`):
  postergar até refactor pós-M1 se houver evidência de necessidade.
- **Parser `.tex` abntex2**: Phase 16 (VAL-07).
- **Suporte a CommonMark extensions além de footnotes** (tabelas, task
  lists, attrs): out of scope; artigos do doutorado usam apenas
  CommonMark + footnotes.
- **Detecção de blocos de código** (` ``` `): tokens são gerados por
  markdown-it (`fence`); virariam `Paragrafo(tipo=DESCONHECIDO)` por padrão.
  Validadores devem ignorar (filtro `tipo != DESCONHECIDO` quando aplicável).
  Adiar tratamento explícito.
- **Validação de schema do JSON de regras dentro do parser**: parser não
  conhece regras; só Validadores. Manter separação.

</deferred>

---

*Phase: 02-parser-markdown*
*Context gathered: 2026-05-05 (auto-mode)*
