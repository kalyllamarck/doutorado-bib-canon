# Phase 2: Parser Markdown - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisões finais estão em `02-CONTEXT.md` — este log preserva as alternativas consideradas.

**Date:** 2026-05-05
**Phase:** 02-parser-markdown
**Mode:** `--auto` (gray areas auto-selecionadas; respostas pelo recomendado)
**Areas discussed:** Localização do `Paragrafo`, Enum `TipoSecao`, Offsets byte-exact, NFC timing, Footnotes, Granularidade, Encoding, API pública

---

## Localização do `Paragrafo` dataclass

| Option | Description | Selected |
|--------|-------------|----------|
| Novo módulo `parser/types.py` | `Paragrafo` parser-internal, separado de `core/dataclasses.py` (Phase 3) | ✓ |
| `core/dataclasses.py` junto com `Violacao`/`Patch` | Concentra todos os tipos do domínio em um único módulo | |
| Inline em `parser/markdown.py` | Dataclass colocada no mesmo arquivo do parser | |

**Auto-pick:** Novo módulo `parser/types.py`
**Rationale:** `Paragrafo` é artefato do parser; `Violacao`/`Patch` são contratos do domínio de validação. Separação por camada evita acoplamento e facilita import seletivo.

---

## Shape do `Paragrafo`

| Option | Description | Selected |
|--------|-------------|----------|
| `frozen=True, slots=True` | Imutável; produzido uma vez, lido por todos | ✓ |
| Mutável com `slots=True` | Permitiria atribuir `paragrafo_pai_idx` em segundo passo sem recriar | |
| Pydantic model | Validação runtime + serialização JSON | |

**Auto-pick:** `frozen=True, slots=True`
**Rationale:** Pipeline read-only após parse. Resolução de `paragrafo_pai_idx` faz-se construindo lista nova em segundo passo (`replace`/recriação) — custo trivial e mantém invariante imutável que CLAUDE.md sugere para tipos do domínio.

---

## Enum `TipoSecao`

| Option | Description | Selected |
|--------|-------------|----------|
| `enum.Enum` com valores string CAIXA_BAIXA | Vocabulário fechado, legível em logs | ✓ |
| `enum.StrEnum` (3.11+) | Equivalente, herda `str` (compara com strings) | |
| Strings literais sem enum | Menos cerimônia, mais frágil | |

**Auto-pick:** `enum.Enum`
**Rationale:** StrEnum ofusca o tipo (parece string). `enum.Enum` força `paragrafo.tipo == TipoSecao.INTRODUCAO` que é o que validadores ST-XX precisam.

---

## Vocabulário do enum `TipoSecao`

| Option | Description | Selected |
|--------|-------------|----------|
| Alinhado aos 11 JSONs em `01_templates/artigo_cientifico/caracteristicas/` | Cobre TITULO, AUTORES, RESUMO, PALAVRAS_CHAVE, ABSTRACT, KEYWORDS, SUMARIO, INTRODUCAO, SECAO, CONCLUSAO, REFERENCIAS, NOTA_RODAPE, CORPO, DESCONHECIDO | ✓ |
| Mínimo (TITULO, SECAO, NOTA_RODAPE, CORPO) | Adia classificação fina para validadores M4 | |
| Vocabulário aberto (string livre) | Sem enum, parser infere de heading text | |

**Auto-pick:** Alinhado aos 11 JSONs
**Rationale:** ST-XX (M4) precisa filtrar por seção semanticamente. Classificar agora no parser evita que cada validador ST replique o mapa de heading.

---

## Classificação de seção

| Option | Description | Selected |
|--------|-------------|----------|
| Heading-text-based com mapa hardcoded | Dicionário em código, normalização NFKD+casefold+strip | ✓ |
| Mapa carregado de `01_templates/.../caracteristicas/` | Dinâmico, sem duplicação | |
| Heurística por posição/número (1º heading = TITULO, 2º = AUTORES, etc.) | Frágil contra variações | |

**Auto-pick:** Heading-text-based hardcoded
**Rationale:** Carga dinâmica cria dependência circular (parser → templates JSON → validadores M4 que dependem do parser). Hardcoded inline é simples, testável; refactor para carga dinâmica fica como deferred se houver pressão real.

---

## Granularidade

| Option | Description | Selected |
|--------|-------------|----------|
| Apenas parágrafos (M1) | Frases viram helper on-demand quando primeiro validador precisar | ✓ |
| Parágrafos + frases | Parser já segmenta frases via heurística (`re.split(r"[.!?]\s+")`) | |
| Parágrafos + frases + linhas | Granularidade total | |

**Auto-pick:** Apenas parágrafos
**Rationale:** Phase 2 cobre CORE-01 + CORE-11. Frases são necessárias só em M3+ e a heurística PT-BR (abreviações, "Sr.", "art. 5º", citações com ponto) é não trivial. Não construir agora.

---

## Estratégia de offsets byte-exact

| Option | Description | Selected |
|--------|-------------|----------|
| Tabela `linha_offsets` cumulativa + `token.map` | Pré-calcula bytes por linha; combina com map do markdown-it | ✓ |
| Re-tokenizar com regex próprio | Bypass markdown-it e calcular offsets manualmente | |
| Usar `mistune` no lugar do markdown-it | Parser alternativo (rejeitado em STACK.md por não expor offsets de linha) | |

**Auto-pick:** Tabela `linha_offsets` + `token.map`
**Rationale:** STACK.md fixou markdown-it 4.0.0 por causa do `token.map`. Tabela linha→offset é O(n) uma vez na leitura. Combina perfeitamente com tokens de bloco.

---

## Conteúdo do `texto` do parágrafo

| Option | Description | Selected |
|--------|-------------|----------|
| Slice byte raw do source NFC | Preserva markdown markers (`*`, `**`, `_`, `[^n]`); offsets perfeitos | ✓ |
| Texto extraído via `token.children` | Texto puro sem marcadores; perde correspondência byte-exata | |
| Híbrido: raw + propriedade `texto_puro` lazy | Adiciona helper, mais código | |

**Auto-pick:** Slice byte raw
**Rationale:** Validadores PT-BR usam `\b...\b` Unicode-aware; marcadores não atrapalham. Helper `texto_puro` pode entrar depois se necessário (Claude's Discretion).

---

## Linha 1-based vs 0-based

| Option | Description | Selected |
|--------|-------------|----------|
| 1-based | Convertida do `token.map[0]` (0-indexed) somando 1; alinhada com editores e `Violacao.linha_inicio` | ✓ |
| 0-based | Sem conversão; menos cerimônia interna | |

**Auto-pick:** 1-based
**Rationale:** REQUIREMENTS especifica `Violacao(linha_inicio=...)` com convenção de editor (1-based). Manter consistência ponta a ponta.

---

## NFC normalization timing

| Option | Description | Selected |
|--------|-------------|----------|
| Source inteiro para NFC ao ler arquivo | Uma vez; offsets sempre em NFC; PatchAplicador segue mesmo modelo | ✓ |
| Por parágrafo após segmentação | Risk de drift entre source e `texto` | |
| Apenas no momento da regex do validador | Cada validador normaliza; offsets ficam ambíguos | |

**Auto-pick:** Source inteiro NFC ao ler
**Rationale:** PITFALLS.md §"Drift de Offsets" pressiona para invariante única. Normalizar uma vez é a única forma de garantir que `(linha, col, offset_bytes)` mapeie sem ambiguidade. Decisão se propaga para Phase 5 (PatchAplicador).

---

## Tratamento de footnotes

| Option | Description | Selected |
|--------|-------------|----------|
| Body como `Paragrafo(NOTA_RODAPE)` separado, ref `[^n]` permanece embutida no parágrafo pai | Compatível com mdit-py-plugins.footnote; `paragrafo_pai_idx` resolvido em segundo passo | ✓ |
| Body inline no parágrafo pai como sufixo | Distorce offsets; valida regras do corpo na nota | |
| Footnotes ignoradas (filtradas do output) | Perde ST-10 (Phase 30) | |

**Auto-pick:** Body separado + ref embutida
**Rationale:** ST-10 (Phase 30) precisa do corpo da nota para validar TNR 10pt e sequência. Validadores do corpo não devem confundir corpo da nota com corpo do parágrafo. Separar por `tipo` é a abstração correta.

---

## Encoding e bordas

| Option | Description | Selected |
|--------|-------------|----------|
| UTF-8 strict + strip BOM + raise em invalid | Sem fallback; erro propagado com log | ✓ |
| Fallback latin-1/cp1252 em caso de erro | Tolerante a arquivos Windows mal salvos | |
| Detect encoding via `chardet` | Lib extra; complexidade desnecessária | |

**Auto-pick:** UTF-8 strict
**Rationale:** Pipeline do doutorado padroniza UTF-8 (todos os JSONs canônicos, todos os artigos do Eólica). Erro explícito > corrupção silenciosa.

---

## Normalização de quebras de linha

| Option | Description | Selected |
|--------|-------------|----------|
| CRLF→LF antes de NFC | Garante `linha_offsets` coerente com tokens markdown-it (que esperam LF) | ✓ |
| Manter CRLF original | Offsets mais "fiéis" mas tokens markdown-it podem inferir errado | |

**Auto-pick:** CRLF→LF antes de NFC
**Rationale:** markdown-it normaliza internamente para LF. Discrepância entre source visto e source tokenizado é exatamente o que produz drift.

---

## API: classe vs função

| Option | Description | Selected |
|--------|-------------|----------|
| Classe `ParserMd` com `parsear(path)` | Permite injeção futura de config | ✓ |
| Função `parsear_md(path)` top-level | Mais leve, sem estado | |

**Auto-pick:** Classe `ParserMd`
**Rationale:** Phase 4 (Contratos ABC) define `ValidadorBase` como classe. Manter consistência; permite registrar mapa de seção customizado em Phases futuras sem quebrar API.

---

## Logging

| Option | Description | Selected |
|--------|-------------|----------|
| `loguru` desde Phase 2 (primeiro consumidor real) | Phase 1 D-19 já adiou para cá | ✓ |
| `logging` stdlib | STACK.md justificou loguru; rever seria reabrir Phase 1 | |
| Sem logging na Phase 2 | Adiar de novo | |

**Auto-pick:** `loguru`
**Rationale:** Decisão herdada de Phase 1. Parser é o primeiro lugar onde DEBUG por bloco e WARNING por footnote órfã têm valor.

---

## Claude's Discretion (não consultadas)

- Estrutura interna de helpers privados em `markdown.py`.
- Texto exato das mensagens `loguru`.
- Decisão entre `parser/heading_map.py` separado ou inline em `types.py`.
- Mensagens de erro/warning para footnotes órfãs.

## Deferred Ideas

- Segmentação por frase (`Frase` dataclass) — adiada para primeiro validador que precise.
- Mapa de seção dinâmico carregado de JSONs canônicos — pós-M1.
- Parser `.tex` abntex2 — Phase 16.
- Suporte a tabelas, task lists, attrs do CommonMark — out of scope.
- Tratamento explícito de fences ` ``` ` — `tipo=DESCONHECIDO` por padrão.

---

*Generated 2026-05-05 by `/gsd-discuss-phase 2 --auto`.*
