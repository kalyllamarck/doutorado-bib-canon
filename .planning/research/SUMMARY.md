# Project Research Summary

**Project:** Validador & Fixer Acadêmico — Biblioteca Canônica do Doutorado
**Domain:** CLI Python — linter de prosa acadêmica PT-BR com regras em JSON
**Researched:** 2026-05-04
**Confidence:** HIGH

## Executive Summary

Este projeto é um linter de prosa acadêmica em português brasileiro: lê arquivos `.md` e `.tex`, detecta violações das regras canônicas da biblioteca do doutorado (PPGD/Unifor) e propõe correções em três níveis de intervenção (AUTO, ASSISTIDO, LLM). Especialistas constroem sistemas análogos (Vale, proselint, ESLint) com a mesma separação de responsabilidades — parser, validador, fixer, orquestrador — mas nenhum deles conhece PT-BR acadêmico-jurídico nem as regras específicas desta biblioteca. A vantagem competitiva real reside nos 38 JSONs já existentes e versionados, que são ao mesmo tempo a documentação do estilo e o único ponto de verdade dos validadores. A pesquisa confirma que o stack stdlib-first (Python 3.13+, `re`, `dataclasses`, `pathlib`) é a escolha correta, com dependências externas mínimas e verificadas.

A abordagem recomendada é construção em milestones verticais (M1-M8): começar por um piloto ponta a ponta com `cst_012` (anúncio metarretórico), validar a arquitetura contra o artigo Eólica Nordeste com violações conhecidas, e só então escalar os validadores primitivos, agregadores, estruturais e fixers. O piloto M1 serve como firewall arquitetural: se parser, `Violacao`, `Patch` e `PatchAplicador` funcionarem corretamente com cst_012, a escala para os 38 JSONs restantes é incremental e segura. Qualquer atalho nessa base (patches em ordem crescente, sem normalização NFC, sem testes de falso positivo) produz bugs silenciosos que destroem a confiança do autor no sistema.

O risco mais alto é o drift de offsets na aplicação de patches (Pitfall 2): corrupção silenciosa do `.md` que é o único input do pipeline LaTeX. O segundo risco é o fixer LLM introduzir violações novas no texto que está sendo corrigido (Pitfall 4). Ambos têm mitigação clara: patches em ordem reversa byte-exact (arquitetura já prevista no PROJECT.md) e pós-validação obrigatória de toda saída LLM antes de aceitar o patch. Gerúndio (Pitfall 1) e backtracking catastrófico de regex (Pitfall 6) são riscos de M2 que exigem benchmark obrigatório contra o artigo Eólica antes de declarar M2 concluído.

## Key Findings

### Recommended Stack

O stack é stdlib-first deliberadamente. Python 3.13+ com `re` (unicode-aware, todos os regex existentes testados), `dataclasses` (`frozen=True, slots=True` para `Violacao`; mutable `slots=True` para `Patch`), `pathlib` e `json` cobrem o núcleo sem nenhuma dependência de instalação. As quatro dependências externas com justificativa técnica verificada são: `markdown-it-py==4.0.0` (único parser CommonMark que expõe `token.map=[start_line, end_line]` por token de bloco), `pylatexenc==2.10` (fixar `<3.0` enquanto v3 está em alpha; único parser LaTeX com `pos_to_lineno_colno()`), `typer==0.25.1` (CLI com autocompletion e Rich integration, reduz boilerplate em ~60% vs. click direto) e `loguru==0.7.3` (zero-config logging para CLI local). `anthropic==0.97.0` e `jinja2==3.1.6` entram apenas em M7. Dependências ausentes com razão explícita: `pandas` (overkill — soma de penalidades é operação de `dict`), `spacy`/`nltk` (POS tagging desnecessário; os validadores são regex determinísticos), `pylatexenc` 3.0alpha (API instável), `black`+`flake8` (substituídos por `ruff`).

**Core technologies:**
- Python 3.13+ / stdlib `re`: runtime e regex — UNICODE-aware, `\b` funciona com PT-BR, zero instalação
- `markdown-it-py` 4.0.0: parser `.md` — único com source maps (`token.map`) por token de bloco
- `pylatexenc` 2.10: parser `.tex` abntex2 — `pos_to_lineno_colno()` necessário para offsets byte-exact
- `typer` 0.25.1: CLI unificado `validar`/`corrigir`/`auditar` — type hints como spec, Rich embutido
- `dataclasses` (stdlib): modelagem de `Violacao` (frozen) e `Patch` — `asdict()` nativo para JSON output
- `anthropic` 0.97.0 + `jinja2` 3.1.6: fixers LLM (M7 apenas) — SDK oficial com retry; prompts parametrizados
- `pytest` 9.0.3 + `pytest-cov` 7.1.0: testes unitários por validador, input controlado

### Expected Features

**Must have (table stakes):**
- Detecção de violações por regex com localização exata (arquivo:linha:col) — núcleo sem o qual não é linter
- Relatório `AUDITORIA.md` priorizado por severidade (ERRO / ALERTA / INFO) com ID rastreável de regra
- ID da regra violada (`cst_012`, `lex_002`) com sugestão vinculada à regra-fonte
- Saída JSON estruturada (`--output json`) para integração com pre-commit e scripts
- Exit code não-zero se ERRO detectado — requisito de integração CI e pre-commit hook
- Parser `.md` CommonMark + footnotes pandoc com offsets byte-exact

**Should have (differentiators vs. Vale/proselint):**
- Regras em JSON versionado externo — alteração de regra não requer deploy de código
- Mapeamento `cst_XXX -> p_YY` (violação -> princípio canônico) no relatório
- 3 níveis de fixer (AUTO determinístico / ASSISTIDO interativo / LLM semântico)
- Visualização de diff antes de aplicar fix com confirmação `[s]im/[n]ao/[e]ditar`
- Validador de coocorrência (9 regras com multiplicadores de penalidade)
- Validadores estruturais ABNT por componente do artigo
- Parser `.tex` abntex2 com identificação de `\footnote{}` como contexto separado

**Defer (v2+ / M4+):**
- Validadores estruturais ABNT completos (M4) — dependem de parser com `TipoSecao`, alta complexidade
- Fixers ASSISTIDO CLI (M6) e Fixers LLM (M7) — adiar até AUTO (M5) validado com testes
- Integração nativa LaTeX/GDocs e pre-commit hook (M8) — adiar até CLI estável
- LSP server (vale-ls como referência) — pós-M8
- SARIF export — anti-feature deliberada; JSON output cobre todos os casos

### Architecture Approach

A arquitetura é em camadas com separação rígida de responsabilidades: CLI (typer) -> Orchestrator (ordem topológica + ThreadPoolExecutor) -> Validadores (1 arquivo por JSON, stateless após `__init__`) -> Fixers (3 categorias) -> Core (`PatchAplicador` em ordem reversa, `ReportGenerator`). Os validadores rodam em três ondas fixas com barreira explícita: Onda 1 — primitivos em paralelo (ThreadPoolExecutor, CPU-bound, não asyncio); Onda 2 — agregadores que consomem `Violacao[]` acumuladas (zero regex novo); Onda 3 — estruturais opcionais por `TipoSecao`. O `ClaudeClient` é injetado via DI nos fixers LLM (testável com `FakeClaudeClient`). A unidade de processamento é `Paragrafo` (não linha individual) — necessário porque o validador de coocorrência precisa saber quais violações estão no mesmo bloco semântico.

**Major components:**
1. `cli.py` (typer) — 3 comandos: `validar`/`corrigir`/`auditar`; zero lógica de negócio
2. `ValidarOrchestrator` — execução topológica (paralelo primitivos -> serial agregadores -> estruturais opcionais)
3. `ValidadorBase` (ABC) + 1 arquivo por JSON — carrega JSON 1x, compila regex 1x, stateless por chamada
4. `CorrigirOrchestrator` — loop validar->fixar->revalidar com guardrail `MAX_ITERACOES=3`
5. `PatchAplicador` — ordena patches por `(linha, col_inicio)` decrescente antes de aplicar; invariante crítico
6. `ReportGenerator` — serializa `Violacao[]` para `AUDITORIA.md` (Rich) e `violacoes.json`
7. `ParserMd` / `ParserTex` — segmenta em `Paragrafo[]` com offsets byte-exact e `TipoSecao`
8. `ClaudeClient` — módulo isolado injetado nos fixers LLM; mock em testes sem monkeypatching

### Critical Pitfalls

1. **Drift de offsets ao aplicar patches (ALTA)** — patches em ordem crescente corrompem o `.md` silenciosamente quando um fix altera o comprimento da linha. Prevenção obrigatória desde M1: `PatchAplicador` ordena por `(linha, col_inicio)` decrescente; teste unitário com 3 patches no mesmo parágrafo antes de ativar qualquer fixer.

2. **Fixer LLM contamina com termos proibidos (ALTA)** — LLM reescreve parágrafo e introduz "além disso", "articula", "significativo" (termos da lista negra). Prevenção: pós-validação obrigatória com todos os validadores M2 antes de aceitar o patch; todos os JSONs de `termos_proibidos/` injetados no prompt via jinja2; temperatura 0.1; MAX_TENTATIVAS_LLM=2.

3. **Loop infinito no ciclo validar->fixar->revalidar (ALTA)** — fix de cst_001 introduz cst_003; fix de cst_003 reintroduz cst_001. Prevenção: guardrail `MAX_ITERACOES_POR_PARAGRAFO=3`; detecção de ciclo por comparação do conjunto de `regra_id` ativos entre iterações; escalar para `REVISAO_HUMANA` em empate.

4. **Falsos positivos de gerúndio em cst_004 (ALTA)** — regex captura "quando", "Fernando", "grande". Prevenção: campo `exclusoes` do JSON aplicado como filtro antes de emitir `Violacao`; cst_004 forçado a nível ASSISTIDO no código (nunca AUTO); corpus de palavras não-verbais em -ando/-endo/-indo nos testes.

5. **Ambiguidade contextual cst_001 (MEDIA)** — dois-pontos em citações ABNT e URLs marcados como violação. Prevenção: filtros de contexto antes de emitir `Violacao` (ignorar ":" dentro de padrão de citação e URLs); testes de falso positivo obrigatórios para cada cst com exceções documentadas no JSON.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Piloto ponta a ponta — cst_012 e infraestrutura core (M1)

**Rationale:** Toda a arquitetura (parser, `Violacao`, `Patch`, `PatchAplicador`, orchestrator mínimo, CLI) precisa ser validada com um caso real antes de escalar. O cst_012 (anúncio metarretórico) é o caso mais frequente no artigo Eólica e tem lógica de detecção clara. M1 é firewall arquitetural: se os invariantes de offset funcionam aqui, funcionam em todos os milestones seguintes.
**Delivers:** CLI `validar artigo.md` funcional; `AUDITORIA.md` gerado; fixer AUTO cst_012 com visualização de diff; exit code não-zero em ERRO.
**Addresses:** REQ-CORE-01 a REQ-CORE-10 (núcleo completo).
**Avoids:** Pitfall 2 (drift de offsets) — `PatchAplicador` reverso testado antes de qualquer fixer ser ativado; Pitfall 5 — normalização NFC no parser desde o início; Pitfall 12 — três grupos de teste (positivos canônicos, variantes, negativos) mesmo no piloto.

### Phase 2: Validadores primitivos completos (M2)

**Rationale:** Com a infraestrutura core validada, adicionar os 5 validadores restantes (lex, cst completo, sig, con, conjunções) em paralelo. São independentes entre si — cada um lê 1 JSON, zero dependência cruzada. Inclui benchmark obrigatório de performance (< 5s sobre artigo 30k palavras) e parser `.tex`.
**Delivers:** Validação completa dos 6 JSONs de `termos_proibidos/` e conjunções (802 entradas); parser abntex2; ThreadPoolExecutor Onda 1 ativo.
**Uses:** `markdown-it-py` plugin de footnotes; `pylatexenc` 2.10; `re.compile()` chamado 1x na `__init__` de cada validador.
**Implements:** 6 validadores em `validadores/primitivos/`; `ValidarOrchestrator` com execução paralela.
**Avoids:** Pitfall 1 (gerúndio) — filtro de `exclusoes` no cst_004, forçar ASSISTIDO; Pitfall 6 (backtracking) — benchmark `timeit` por regex, substituir `.{0,150}` por `[^\n]{0,150}`; Pitfall 7 (ambiguidade contextual) — filtros de contexto para cst_001 e cst_009; Pitfall 9 (versionamento) — campo `"versao"` semver adicionado a cada JSON.

### Phase 3: Validadores agregadores (M3)

**Rationale:** `CoocorrenciaValidador` e `EscritaCanonica Validador` dependem da saída completa dos primitivos de M2 — são a Onda 2 da execução topológica. Não têm regex próprio: consomem `Violacao[]` já geradas. Completar M2 totalmente é bloqueio real aqui.
**Delivers:** Detecção de coocorrência (9 regras com multiplicadores, VERMELHO_FORTE); mapeamento `cst_XXX -> p_YY` no relatório.
**Implements:** `validadores/agregadores/coocorrencia.py` e `validadores/agregadores/escrita_canonica.py`; barreira explícita Onda 1 -> Onda 2 no orchestrator.
**Avoids:** Anti-pattern de re-executar regex dos primitivos no agregador; Anti-pattern de ThreadPoolExecutor para agregadores em paralelo com primitivos.

### Phase 4: Validadores estruturais ABNT (M4)

**Rationale:** Depende de extensão do parser para identificar `TipoSecao` por heading Markdown — funcionalidade além do parser básico de M1. Pode ser desenvolvido em paralelo com M3 (dependem do mesmo parser mas não entre si). É o milestone de maior complexidade (10 validadores por componente ABNT).
**Delivers:** Validação por componente: introdução sem citações, conclusão sem citações novas, resumo <= 150 palavras, hierarquia de seções, notas de rodapé sequenciais, referências em formato ABNT.
**Implements:** `validadores/estruturais/` (10 arquivos); extensão do `ParserMd` para `TipoSecao`.
**Avoids:** Pitfall 7 (citações ABNT em contexto legítimo) — filtros de contexto nos validadores estruturais de citações.

### Phase 5: Fixers AUTO (M5)

**Rationale:** Com todos os primitivos validados e testados (M2), os fixers AUTO têm `Violacao` canônicas para consumir. Cada fixer corresponde a um validador primitivo. O cst_012 do M1 é refatorado para este diretório.
**Delivers:** Correção determinística para termos lexicais, expressões conectivas, sinais gráficos e cst_012. Visualização de diff completa no CLI.
**Implements:** `fixers/auto/` (5 fixers); `EstadoPatch` enum definido na `dataclass Patch` para suportar estados futuros (ASSISTIDO/LLM).
**Avoids:** Pitfall 8 (contador conta rejeições como "fixed") — modelar `EstadoPatch` desde agora.

### Phase 6: Fixers ASSISTIDO CLI (M6)

**Rationale:** Reutiliza infraestrutura de `Patch` de M5. Adiciona interatividade para violações que requerem julgamento humano. Deve ser estável antes de M7 para validar a infra de Patch sem custo de API.
**Delivers:** Fixers interativos com proposta de N opções e confirmação do autor. Relatório com violações REJEITADAS listadas separadamente como ainda ativas.
**Implements:** `fixers/assistido/` (3-5 fixers); `EstadoPatch` enum completo (PROPOSTO / ACEITO / REJEITADO / SUPRIMIDO).
**Avoids:** Pitfall 8 (contador enganoso); Pitfall 1 (gerúndio) — cst_004 SEMPRE ASSISTIDO.

### Phase 7: Fixers LLM via Claude API (M7)

**Rationale:** Depende de M6 para validar infra de Patch. Claude API introduz riscos exclusivos (rate limits, custo, contaminação) que justificam milestone próprio. `ClaudeClient` pode ser desenvolvido em isolamento enquanto M6 ainda está em progresso.
**Delivers:** Fixers LLM para cst_008, cst_010, cst_007, coc_007. Dry-run mode com estimativa de custo antes de executar.
**Implements:** `fixers/llm/claude_client.py` (DI, mock em testes); `prompts/*.j2` com lista negra completa injetada; pós-validação M2 obrigatória de toda saída LLM.
**Avoids:** Pitfall 3 (loop infinito) — guardrail implementado antes de ativar qualquer fixer LLM; Pitfall 4 (contaminação) — pós-validação obrigatória, temperatura 0.1; Pitfall 11 (rate limits) — cliente sequencial com backoff exponencial.

### Phase 8: Orchestrator completo e integrações (M8)

**Rationale:** `CorrigirOrchestrator` com loop guardrail depende de todos os fixers. Integrações externas dependem de CLI estável. Phase de integração, não de novas features.
**Delivers:** CLI `corrigir` e `auditar` completos; loop validar->fixar->revalidar com guardrail; pre-commit hook; integração no `build.sh` LaTeX e `criar_template.py` GDocs; testes de integração contra `artigo.md` real; git hash dos JSONs no cabeçalho do relatório.
**Implements:** `orchestrator/corrigir_orchestrator.py`; `.pre-commit-hooks.yaml`; hooks no pipeline de render.
**Avoids:** Pitfall 3 (loop); Pitfall 9 (versionamento) — git hash dos JSONs no relatório; Pitfall 10 (corrupção LaTeX) — fixer nunca opera sobre `.tex`; hook no `build.sh` somente valida, nunca corrige.

### Phase Ordering Rationale

- M1 primeiro porque valida os invariantes de offset sem dependências externas. Falhar aqui é barato; falhar em M7 com bugs de offset é caro e custa créditos de API.
- M2 antes de M3 porque `CoocorrenciaValidador` é matematicamente dependente da saída de M2; sem primitivos, a lista de input de coocorrência é vazia.
- M4 pode sobrepor M3 porque ambos dependem do parser (estendido em M1/M2) mas não dependem um do outro.
- M5 antes de M6 porque M6 reutiliza a infraestrutura de Patch de M5 — especificamente a aplicação byte-exact e visualização de diff.
- M6 antes de M7 porque M7 tem custo monetário: validar a infra de Patch sem custo de API antes de pagar por chamadas LLM.
- M8 por último porque é integração pura: depende de CLI estável (M1), todos os validadores (M2-M4) e todos os fixers (M5-M7).

### Research Flags

Phases que provavelmente precisam de pesquisa de fase adicional durante o planejamento:
- **M4 (Estruturais ABNT):** os 10 JSONs de `01_templates/artigo_cientifico/caracteristicas/` precisam ser mapeados para lógica de validador. Alguns campos (ex.: `10_pagina_global.json` com margens e fonte) podem não ser verificáveis em texto plano sem renderização. Identificar quais regras são verificáveis em `.md` vs. somente em PDF renderizado.
- **M7 (Fixers LLM):** mapeamento de cst -> tipo de reescrita esperada nos prompts jinja2 e formatação dos `exemplos_reescritos` dos JSONs como few-shot padronizado. Custo real por sessão precisa de estimativa empírica na primeira execução.

Phases com padrões estabelecidos (pode ir direto para implementação):
- **M1 (Piloto):** arquitetura totalmente especificada em ARCHITECTURE.md com código exemplificado; stack verificado no STACK.md com versões confirmadas no PyPI.
- **M2 (Primitivos):** padrão "1 arquivo por JSON, ValidadorBase ABC" totalmente documentado; ThreadPoolExecutor com CPU-bound tasks é padrão Python estabelecido.
- **M5 (Fixers AUTO):** regex determinístico e `PatchAplicador` reverso já implementados e testados no M1 para cst_012; extensão incremental.
- **M8 (Integrações):** pre-commit hook tem padrão documentado (`.pre-commit-hooks.yaml`); integração LaTeX via exit code é trivial.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Todas as versões verificadas no PyPI; `re` testado empiricamente com regex dos JSONs no Python 3.12; `markdown-it-py` token.map confirmado em documentação oficial; `pylatexenc` `pos_to_lineno_colno()` confirmado |
| Features | HIGH | JSONs lidos diretamente; Vale e proselint verificados via docs oficiais; feature dependencies derivadas dos JSONs existentes, não de inferência |
| Architecture | HIGH | Derivada dos JSONs existentes (`06_regras_coocorrencia.json` define escopo por parágrafo; `escrita_canonica.json` define mapeamento cst->princípio); padrões de concorrência são bem documentados na stdlib Python |
| Pitfalls | HIGH | Pitfalls derivados de leitura direta dos campos `exclusoes` (cst_004) e `observacao` (cst_009) dos JSONs; análise de sistemas análogos (Vale, ESLint, proselint); análise de regex do corpus existente |

**Overall confidence:** HIGH

### Gaps to Address

- **Validação empírica dos regex contra o artigo Eólica:** os regex dos JSONs foram verificados como sintaticamente corretos, mas a cobertura das violações conhecidas (cst_007, cst_008, cst_010, cst_011, cst_012) precisa ser confirmada em produção no M1. Os falsos positivos em parágrafos limpos são desconhecidos até o teste de integração.
- **TipoSecao em M4:** não existe mapeamento documentado de como identificar `INTRODUCAO`, `CONCLUSAO`, `RESUMO` pelos headings Markdown do artigo Eólica. O parser precisará de heurística que pode não cobrir todos os casos do artigo real.
- **Custo real da API em M7:** estimativa de $0.18/sessão baseada em 15 chamadas x ~4k tokens de input. Número real de violações LLM por artigo e tamanho médio do prompt com lista negra injetada precisam ser medidos na primeira sessão de M7.
- **Conjunções (802 entradas) em M2:** a lógica de "primeira palavra de parágrafo deve ser conjunção" pode gerar alto volume de falsos positivos em parágrafos que começam com nome de autor ou ano de citação. Definir escopo da regra antes de implementar REQ-VAL-06.

## Sources

### Primary (HIGH confidence)
- `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/.planning/PROJECT.md` — requisitos, constraints e decisões de arquitetura
- `biblioteca_canonica/02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json` — campos `exclusoes`, `observacao`, `operacao_fix_automatizavel`
- `biblioteca_canonica/02_escrita/termos_proibidos/06_regras_coocorrencia.json` — multiplicadores, escopos, fluxo de penalidade
- `biblioteca_canonica/02_escrita/escrita_canonica.json` — mapeamento cst->princípio, perguntas de teste de estresse
- PyPI (versões confirmadas): markdown-it-py==4.0.0, pylatexenc==2.10, typer==0.25.1, loguru==0.7.3, rich==15.0.0, anthropic==0.97.0, jinja2==3.1.6, pytest==9.0.3, pytest-cov==7.1.0
- markdown-it-py docs (token.map) — https://markdown-it-py.readthedocs.io/en/latest/using.html
- pylatexenc LatexWalker docs — https://pylatexenc.readthedocs.io/en/latest/latexwalker/
- Python 3.13 docs, módulo `re` — https://docs.python.org/3/library/re.html

### Secondary (MEDIUM confidence)
- Vale official docs — https://vale.sh/docs/ (tipos de fixer, modo CI, saída JSON)
- proselint GitHub — https://github.com/amperser/proselint (wire schema JSON, capacidades de fixer)
- Python docs `unicodedata` — normalização NFC/NFD (HIGH em stdlib, mas aplicação ao corpus PT-BR não verificada empiricamente)
- Anthropic SDK docs — retry automático com backoff e rate limits (comportamento inferido, não testado com 429 real)

### Tertiary (LOW confidence)
- Estimativa de custo API ($0.18/sessão) — calculada a partir de número estimado de violações e tokens médios de prompt; precisa de validação empírica na primeira sessão de M7
- Tempo de validação < 5s para 30k palavras — estimativa teórica baseada em ~12.000 operações de regex precompilado; precisa de benchmark real contra o artigo Eólica

---
*Research completed: 2026-05-04*
*Ready for roadmap: yes*
