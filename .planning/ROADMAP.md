# Roadmap: Validador & Fixer Acadêmico — Biblioteca Canônica

## Overview

Construção incremental de um linter de prosa acadêmica PT-BR organizada em 8 milestones. O M1 valida a arquitetura ponta a ponta com o caso piloto cst_012 antes de qualquer escala. M2-M4 completam os validadores em ordem topológica (primitivos -> agregadores -> estruturais). M5-M7 implementam os três níveis de fixer (AUTO -> ASSISTIDO -> LLM) após validadores estáveis. M8 fecha o ciclo com o orchestrator completo e todas as integrações externas.

## Milestones

- 📋 **M1 — Piloto + Infraestrutura Core** — Phases 1-9 (sequencial)
- 📋 **M2 — Validadores Primitivos** — Phases 10-17 (4 paralelizáveis após M1)
- 📋 **M3 — Validadores Agregadores** — Phases 18-20 (sequencial; bloqueado por M2)
- 📋 **M4 — Validadores Estruturais ABNT** — Phases 21-31 (todas paralelizáveis; bloqueado por M1)
- 📋 **M5 — Fixers AUTO** — Phases 32-36 (paralelizáveis; bloqueado por M2)
- 📋 **M6 — Fixers ASSISTIDO CLI** — Phases 37-41 (paralelizáveis; bloqueado por M5)
- 📋 **M7 — Fixers LLM via Claude API** — Phases 42-49 (bloqueado por M6)
- 📋 **M8 — Orchestrator + Integração** — Phases 50-59 (bloqueado por M2-M7)

## Phases

**Phase Numbering:** Integer phases (1-59) em ordem contínua por milestone.

### M1 — Piloto + Infraestrutura Core

- [x] **Phase 1: Bootstrap** - `pyproject.toml` + layout `src/biblio_validador/` + `uv` install + entry point CLI
- [ ] **Phase 2: Parser Markdown** - Parser `.md` CommonMark + footnotes com offsets byte-exact e NFC
- [ ] **Phase 3: Dataclasses Core** - `Violacao` + `Patch` + enum `EstadoPatch`
- [ ] **Phase 4: Contratos ABC** - `ValidadorBase` + `FixerBase` com contratos completos
- [ ] **Phase 5: PatchAplicador** - Aplicador de patches em ordem reversa com testes de drift
- [ ] **Phase 6: Validador Piloto cst_012** - Validador anúncio metarretórico ponta a ponta
- [ ] **Phase 7: Fixer AUTO Piloto cst_012** - Fixer determinístico com visualização de diff
- [ ] **Phase 8: Orchestrator Mínimo** - Orchestrator básico + geração de `AUDITORIA.md`
- [ ] **Phase 9: Pipeline E2E** - Validação e correção contra `artigo.md` real do Eólica Nordeste

### M2 — Validadores Primitivos

- [ ] **Phase 10: VAL-01 Termos Lexicais** - Validador `01_termos_lexicais_proibidos.json` (14 entradas)
- [ ] **Phase 11: VAL-02 Expressões Conectivas** - Validador `02_expressoes_conectivas_proibidas.json` (5 locuções)
- [ ] **Phase 12: VAL-03 Colocações Semânticas** - Validador `03_colocacoes_semanticas_proibidas.json` (2 entradas)
- [ ] **Phase 13: VAL-04 Construções Sintáticas** - Validador `04_construcoes_sintaticas_proibidas.json` (12 cst)
- [ ] **Phase 14: VAL-05 Sinais Gráficos** - Validador `05_sinais_graficos_proibidos.json` com lookahead
- [ ] **Phase 15: VAL-06 Conjunções** - Validador conjunções (802 entradas, checagem de abertura de parágrafo)
- [ ] **Phase 16: VAL-07 Parser LaTeX** - Parser `.tex` abntex2 via `pylatexenc` com offsets
- [ ] **Phase 17: VAL-08 Benchmark** - Benchmark de performance (< 5s em artigo 30k palavras)

### M3 — Validadores Agregadores

- [ ] **Phase 18: AGR-01 Coocorrência** - Validador `06_regras_coocorrencia.json` (9 regras, Onda 2)
- [ ] **Phase 19: AGR-02 Escrita Canônica** - Validador `escrita_canonica.json` (16 princípios, mapping cst->princípio)
- [ ] **Phase 20: AGR-03 Versionamento** - Campo `versao` semver nos JSONs + registro no relatório

### M4 — Validadores Estruturais ABNT

- [ ] **Phase 21: ST-01 Títulos** - Validador `01_titulos.json` (PT centralizado bold; EN itálico)
- [ ] **Phase 22: ST-02 Autores** - Validador `02_autores.json` (CAIXA ALTA bold, footnote numérico)
- [ ] **Phase 23: ST-03 Resumo** - Validador `03_resumo_palavras_chave.json` (max 150 palavras, 5 palavras-chave)
- [ ] **Phase 24: ST-04 Sumário** - Validador `03b_sumario.json` (estrutura linha-única com indicativo)
- [ ] **Phase 25: ST-05 Introdução** - Validador `04_introducao.json` (PROIBIDO citações, voz reflexiva)
- [ ] **Phase 26: ST-06 Seções** - Validador `05_secoes.json` (hierarquia CAIXA ALTA, 2 níveis)
- [ ] **Phase 27: ST-07 Conclusão** - Validador `06_conclusao.json` (PROIBIDO citações novas)
- [ ] **Phase 28: ST-08 Referências** - Validador `07_referencias.json` (Qualis A1-A4, ordem alfabética)
- [ ] **Phase 29: ST-09 Citações** - Validador `08_citacoes.json` (autor+ano, et al., traduções)
- [ ] **Phase 30: ST-10 Notas de Rodapé** - Validador `09_notas_rodape.json` (TNR 10pt, sequencial)
- [ ] **Phase 31: ST-11 Página Global** - Validador `10_pagina_global.json` (margens, fonte, paginação)

### M5 — Fixers AUTO

- [ ] **Phase 32: FXA-01 Fixer Termos Lexicais** - Fixer substituição direta para termos proibidos
- [ ] **Phase 33: FXA-02 Fixer Expressões Conectivas** - Fixer `02_expressoes_conectivas_proibidas`
- [ ] **Phase 34: FXA-03 Fixer Sinais Gráficos** - Fixer travessão e dois-pontos com heurísticas
- [ ] **Phase 35: FXA-04 Fixer Estrangeirismos** - Fixer itálico B1 (wrap `*termo*`)
- [ ] **Phase 36: FXA-05 Fixer cst_012 Refatorado** - Fixer cst_012 migrado do M1 para arquitetura final

### M6 — Fixers ASSISTIDO CLI

- [ ] **Phase 37: FXS-01 Fixer Dois-pontos** - Fixer cst_001 com proposta de 3 reescritas e escolha CLI
- [ ] **Phase 38: FXS-02 Fixer Gerúndio** - Fixer cst_004 ASSISTIDO, respeitando `exclusoes` do JSON
- [ ] **Phase 39: FXS-03 Fixer Anglicismos** - Fixer B4 usando dicionário `08_citacoes.json`
- [ ] **Phase 40: FXS-04 Fixer Determinante** - Fixer cst_011 omissão de determinante com confirmação
- [ ] **Phase 41: FXS-05 Fixer Conjunção Inicial** - Fixer B3 com 5 sugestões filtradas por subtipo e score

### M7 — Fixers LLM via Claude API

- [ ] **Phase 42: FXL-01 Cliente Claude API** - Cliente `anthropic` SDK + biblioteca de prompts `jinja2` + DI
- [ ] **Phase 43: FXL-02 Fixer Pseudossíntese** - Fixer LLM cst_008 pseudossíntese conciliatória
- [ ] **Phase 44: FXL-03 Fixer Tópico Numerado** - Fixer LLM cst_010 tópico numerado com rótulo nominal
- [ ] **Phase 45: FXL-04 Fixer Abertura Lacônica** - Fixer LLM cst_007 abertura com reancoragem nominal
- [ ] **Phase 46: FXL-05 Fixer Coocorrência** - Fixer LLM coc_007 VERMELHO_FORTE (parágrafo completo)
- [ ] **Phase 47: FXL-06 Fixer Citação Proibida** - Fixer LLM B2 remoção de citação em INTRODUÇÃO/CONCLUSÃO
- [ ] **Phase 48: FXL-07 Pós-validação LLM** - Re-validação obrigatória de saída LLM antes de aceitar patch
- [ ] **Phase 49: FXL-08 Guardrail LLM** - MAX_ITERACOES + MAX_TENTATIVAS + temperatura 0.1 + dry-run

### M8 — Orchestrator + Integração

- [ ] **Phase 50: ORC-01 Orchestrator Validador** - ThreadPoolExecutor paralelo + ordem topológica (3 ondas)
- [ ] **Phase 51: ORC-02 Orchestrator Fixer** - Loop validar->fixar->revalidar com guardrail anti-loop
- [ ] **Phase 52: ORC-03 CLI Unificado** - `validar`/`corrigir`/`auditar` via `typer` 0.25.1
- [ ] **Phase 53: ORC-04 Testes Validadores** - Testes unitários por validador (input controlado)
- [ ] **Phase 54: ORC-05 Testes Fixers** - Testes unitários por fixer (violação -> patch esperado)
- [ ] **Phase 55: ORC-06 Integração LaTeX** - Hook no `build.sh` (validar antes de compilar, nunca corrigir)
- [ ] **Phase 56: ORC-07 Integração GDocs** - Auditoria pré-render via `gws CLI`
- [ ] **Phase 57: ORC-08 Pre-commit Hook** - Hook opcional para `.md` em qualquer commit do repo
- [ ] **Phase 58: ORC-09 Output JSON** - Output estruturado `violacoes.json` além de `AUDITORIA.md`
- [ ] **Phase 59: ORC-10 Logging Estruturado** - `loguru` 0.7.3 com DEBUG/INFO/WARN/ERROR

## Phase Details

### Phase 1: Bootstrap
**Goal**: Projeto Python instalável com layout canônico, entry point no PATH e dependências gerenciadas pelo `uv`
**Depends on**: Nothing (first phase)
**Requirements**: CORE-12
**Success Criteria** (what must be TRUE):
  1. `uv sync` em diretório limpo instala todas as dependências sem erro
  2. `validar --help` retorna usage sem error code
  3. `src/biblio_validador/__init__.py` existe com versão `0.1.0`
  4. `pyproject.toml` declara todas as dependências do SUMMARY.md com versões fixadas
**Plans:** 1 plan
- [x] 01-01-PLAN.md — Bootstrap: uv init + overrides D-XX + 3 tasks (scaffold, deps, validation)

### Phase 2: Parser Markdown
**Goal**: Parser `.md` CommonMark + footnotes que segmenta em parágrafos com offsets byte-exact e normalização NFC
**Depends on**: Phase 1
**Requirements**: CORE-01, CORE-11
**Success Criteria** (what must be TRUE):
  1. `ParserMd.parsear("artigo.md")` retorna `list[Paragrafo]` com `linha_inicio`, `linha_fim`, `offset_bytes` corretos
  2. Parágrafo com acento composto (NFD) é normalizado para NFC antes de indexar
  3. Footnotes `[^n]` são segmentados como `TipoSecao.NOTA_RODAPE` separado do corpo
  4. Teste com trecho do artigo Eólica Nordeste retorna parágrafos identificáveis linha a linha
**Plans:** 1 plan
- [ ] 02-01-PLAN.md — Parser Markdown: scaffold parser/ + types.py + markdown.py + 6 tests + gate (3 tasks)

### Phase 3: Dataclasses Core
**Goal**: Dataclasses `Violacao` e `Patch` com todos os campos especificados + enum `EstadoPatch` tipado e imutável
**Depends on**: Phase 1
**Requirements**: CORE-02, CORE-03
**Success Criteria** (what must be TRUE):
  1. `Violacao(arquivo=..., linha_inicio=1, ...)` é criada com `frozen=True` e `slots=True`
  2. `Patch` é mutável (`slots=True`, sem frozen) e aceita `EstadoPatch.PROPOSTO/ACEITO/REJEITADO/SUPRIMIDO`
  3. `dataclasses.asdict(violacao)` produz dict serializável em JSON sem erros
  4. Tentativa de mutar `Violacao.regra_id` lança `FrozenInstanceError`
**Plans**: TBD

### Phase 4: Contratos ABC
**Goal**: ABCs `ValidadorBase` e `FixerBase` com contratos completos que forçam implementação dos métodos obrigatórios
**Depends on**: Phase 3
**Requirements**: CORE-04, CORE-05
**Success Criteria** (what must be TRUE):
  1. Instanciar classe concreta que omite `validar()` lança `TypeError` em tempo de instanciação
  2. `ValidadorBase.carregar_regras()` carrega o JSON referenciado em `JSON_SOURCE` e compila regex 1x
  3. `FixerBase.pode_corrigir(v)` retorna `False` para `regra_id` não listado em `VIOLACAO_IDS`
  4. Testes unitários dos ABCs passam (incluindo teste de violação de contrato)
**Plans**: TBD

### Phase 5: PatchAplicador
**Goal**: Aplicador de patches byte-exact em ordem reversa que preserva integridade do arquivo após múltiplas substituições simultâneas
**Depends on**: Phase 4
**Requirements**: CORE-06
**Success Criteria** (what must be TRUE):
  1. Aplicar 3 patches simultâneos no mesmo parágrafo produz texto correto sem drift de offsets
  2. Patches aplicados em ordem `(linha, col_inicio)` decrescente (teste confirma a ordem de execução)
  3. Arquivo original é preservado se qualquer patch falhar (rollback transacional)
  4. Teste de regressão: texto de 1000 chars com 5 substituições sobrepostas produz saída determinística
**Plans**: TBD

### Phase 6: Validador Piloto cst_012
**Goal**: Validador de anúncio metarretórico (cst_012) funcionando ponta a ponta: carrega JSON, detecta violação, emite `Violacao` com linha:col exatos
**Depends on**: Phase 4
**Requirements**: CORE-07
**Success Criteria** (what must be TRUE):
  1. Frase "A pesquisa de X (Y) revela que..." é detectada como `regra_id=cst_012` com `severidade=ERRO`
  2. `violacao.linha_inicio` e `col_inicio` apontam para o caractere exato do trecho violador
  3. `violacao.sugestoes` contém ao menos 1 reescrita alternativa
  4. Parágrafos limpos (sem cst_012) retornam `[]` (zero falsos positivos no artigo Eólica)
**Plans**: TBD

### Phase 7: Fixer AUTO Piloto cst_012
**Goal**: Fixer determinístico para cst_012 que propõe e aplica substituição com visualização de diff antes de confirmar
**Depends on**: Phase 5, Phase 6
**Requirements**: CORE-08
**Success Criteria** (what must be TRUE):
  1. `fixer.propor_patches(violacao, contexto)` retorna `Patch` com `confianca >= 0.9`
  2. Frase "A descoberta específica de X (Y) reside em VERBAR" é reescrita para "X (Y) VERBA"
  3. CLI exibe diff colorido antes de confirmar aplicação
  4. Após aplicação, re-validar o arquivo retorna `[]` para cst_012 no trecho corrigido
**Plans**: TBD

### Phase 8: Orchestrator Mínimo
**Goal**: Orchestrator básico que executa ValidadorBase[] sobre um arquivo e gera `AUDITORIA.md` priorizado por severidade
**Depends on**: Phase 6
**Requirements**: CORE-09
**Success Criteria** (what must be TRUE):
  1. `orchestrator.auditar("artigo.md")` retorna `list[Violacao]` de todos os validadores registrados
  2. `AUDITORIA.md` gerado lista violações agrupadas por ERRO -> ALERTA -> INFO com ID de regra rastreável
  3. Exit code 1 quando há ao menos 1 violação com severidade ERRO
  4. Exit code 0 quando nenhuma violação de nível ERRO é detectada
**Plans**: TBD

### Phase 9: Pipeline E2E
**Goal**: Pipeline `validar` + `corrigir` funcionando contra o artigo Eólica Nordeste real, detectando violações cst_012 conhecidas
**Depends on**: Phase 7, Phase 8
**Requirements**: CORE-10
**Success Criteria** (what must be TRUE):
  1. `validar artigo_final/artigo.md` detecta ao menos as violações cst_012 identificadas na inspeção manual
  2. `corrigir artigo_final/artigo.md` aplica fixer cst_012 e produz arquivo modificado válido
  3. Arquivo corrigido re-processado pelo validador retorna 0 violações cst_012
  4. Tempo de processamento < 5 segundos para o artigo completo
**Plans**: TBD

---

### Phase 10: VAL-01 Termos Lexicais
**Goal**: Validador `01_termos_lexicais_proibidos.json` que detecta as 14 entradas com variantes morfológicas usando regex compilado 1x
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 11-15 (todos os VAL-0x são independentes entre si)
**Requirements**: VAL-01
**Success Criteria** (what must be TRUE):
  1. "consolidar", "consolidação", "consolidada" são todos detectados como `lex_001` (variante morfológica)
  2. Palavra "consolidar" em contexto de citação entre aspas não gera falso positivo (se JSON indica exclusão)
  3. Todas as 14 entradas do JSON produzem ao menos 1 hit no artigo Eólica Nordeste
  4. Testes unitários com frases positivas e negativas para cada entrada passam
**Plans**: TBD

### Phase 11: VAL-02 Expressões Conectivas
**Goal**: Validador `02_expressoes_conectivas_proibidas.json` que detecta as 5 locuções proibidas com delimitação correta de palavra
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 10, 12-15
**Requirements**: VAL-02
**Success Criteria** (what must be TRUE):
  1. "além disso" isolado é detectado; "além disso que" (parte de construção maior) também é detectado
  2. "em suma" no meio de sentença é detectado com col_inicio correto
  3. Testes de falso positivo passam (ex.: locução proibida dentro de citação entre aspas, se JSON indica exclusão)
  4. Regex não causa backtracking catastrófico (timeit < 1ms por parágrafo de 200 chars)
**Plans**: TBD

### Phase 12: VAL-03 Colocações Semânticas
**Goal**: Validador `03_colocacoes_semanticas_proibidas.json` que detecta as 2 entradas com gatilhos contextuais (par de termos)
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 10-11, 13-15
**Requirements**: VAL-03
**Success Criteria** (what must be TRUE):
  1. Par gatilho detectado no mesmo parágrafo emite `Violacao` com referência a ambos os termos
  2. Par separado em parágrafos distintos não emite violação (escopo parágrafo)
  3. Testes unitários cobrem os 2 pares com casos positivos e negativos
**Plans**: TBD

### Phase 13: VAL-04 Construções Sintáticas
**Goal**: Validador `04_construcoes_sintaticas_proibidas.json` que detecta as 12 construções (cst_001..cst_012) respeitando campos `exclusoes` e `observacao`
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 10-12, 14-15
**Requirements**: VAL-04
**Success Criteria** (what must be TRUE):
  1. cst_004 (gerúndio) não detecta "Fernando", "quando", "grande" como falsos positivos
  2. cst_001 (dois-pontos) não detecta URLs e timestamps como violação (lookahead negativo)
  3. Cada uma das 12 entradas tem ao menos 1 teste positivo e 1 teste negativo nos testes unitários
  4. cst_012 reutiliza o regex do piloto M1 sem duplicação de código
**Plans**: TBD

### Phase 14: VAL-05 Sinais Gráficos
**Goal**: Validador `05_sinais_graficos_proibidos.json` que detecta travessão e dois-pontos com lookahead negativo para horários, URLs e citações ABNT
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 10-13, 15
**Requirements**: VAL-05
**Success Criteria** (what must be TRUE):
  1. Travessão em meio de sentença emite violação com col_inicio correto
  2. "15:30" (horário), "https://url" e "(Autor, 2024, p. 15)" não emitem falso positivo
  3. Dois-pontos em construção explicativa proibida emite violação
  4. Testes unitários com corpus de 10 casos positivos e 10 negativos passam
**Plans**: TBD

### Phase 15: VAL-06 Conjunções
**Goal**: Validador de conjunções (802 entradas, 18 subtipos) com checagem de conjunção inicial obrigatória em parágrafos do corpo
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 10-14
**Requirements**: VAL-06
**Success Criteria** (what must be TRUE):
  1. Parágrafo do corpo que começa sem conjunção emite `Violacao` com `regra_id=conj_ausencia`
  2. Parágrafo que começa com nome de autor ("Leff (2006)...") não emite falso positivo (exclusão definida)
  3. As 18 categorias de conjunções são indexadas corretamente (teste de lookup por subtipo)
  4. Benchmark: indexar 802 entradas na `__init__` leva < 100ms
**Plans**: TBD

### Phase 16: VAL-07 Parser LaTeX
**Goal**: Parser `.tex` abntex2 via `pylatexenc` 2.10 que segmenta em `Paragrafo[]` com offsets byte-exact e identifica `\footnote{}` como contexto separado
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 10-15
**Requirements**: VAL-07
**Success Criteria** (what must be TRUE):
  1. `ParserTex.parsear("artigo.tex")` retorna parágrafos com `linha_inicio/fim` usando `pos_to_lineno_colno()`
  2. `\footnote{texto}` é segmentado como `TipoSecao.NOTA_RODAPE` separado do parágrafo pai
  3. Comandos LaTeX (`\textbf{}`, `\emph{}`) são removidos do texto para validação sem afetar offsets
  4. Teste com arquivo `.tex` real (template do doutorado) retorna parágrafos corretos
**Plans**: TBD

### Phase 17: VAL-08 Benchmark
**Goal**: Validação de performance que garante processamento de artigo de 30k palavras em < 5 segundos com todos os validadores primitivos ativos
**Depends on**: Phases 10-16 (todos os primitivos completos)
**Requirements**: VAL-08
**Success Criteria** (what must be TRUE):
  1. `timeit` de `orchestrator.auditar(artigo_eolica)` com M2 completo retorna < 5.0s em 3 execuções
  2. Se algum validador exceder 1s individualmente, relatório identifica o gargalo por nome
  3. Regex com `.{0,150}` substituídos por `[^\n]{0,150}` onde necessário (anti-backtracking)
  4. Benchmark integrado ao CI (testa antes de aceitar novos validadores)
**Plans**: TBD

---

### Phase 18: AGR-01 Coocorrência
**Goal**: Validador `06_regras_coocorrencia.json` (9 regras) que consome `list[Violacao]` dos primitivos e detecta coocorrências com multiplicadores de penalidade
**Depends on**: Phase 17 (M2 complete)
**Requirements**: AGR-01
**Success Criteria** (what must be TRUE):
  1. Parágrafo com 2 violações que disparam coc_007 (VERMELHO_FORTE) emite violação agregadora com multiplicador correto
  2. Violação VERMELHO_FORTE tem `severidade=CRITICO` distinguível das primitivas
  3. Coocorrência de escopo `documento` detecta par em parágrafos distintos
  4. Sem acesso a regex novo: o validador opera exclusivamente sobre `list[Violacao]` entrada
**Plans**: TBD

### Phase 19: AGR-02 Escrita Canônica
**Goal**: Validador `escrita_canonica.json` (16 princípios, 6 perguntas teste de estresse) que mapeia `cst_XXX -> p_YY` no relatório de auditoria
**Depends on**: Phase 17 (M2 complete)
**Requirements**: AGR-02
**Success Criteria** (what must be TRUE):
  1. `violacao.principio_canonico_violado` é preenchido com o princípio mapeado do JSON (ex.: "p_03")
  2. AUDITORIA.md exibe o nome do princípio canônico junto ao ID da construção violada
  3. Todas as 6 perguntas de teste de estresse aparecem no relatório quando nível CRITICO é atingido
  4. Testes unitários verificam o mapeamento cst->princípio para ao menos 6 das 12 construções
**Plans**: TBD

### Phase 20: AGR-03 Versionamento
**Goal**: Campo `versao` semver em todos os JSONs + cabeçalho de AUDITORIA.md registra qual versão de cada JSON foi aplicada
**Depends on**: Phase 19
**Requirements**: AGR-03
**Success Criteria** (what must be TRUE):
  1. Todos os JSONs em `02_escrita/` e `01_templates/artigo_cientifico/caracteristicas/` têm campo `"versao": "1.0.0"`
  2. Cabeçalho de AUDITORIA.md lista: `[nome_json] v[versao] (git:hash_curto)`
  3. Atualizar versão de um JSON sem re-executar não afeta o histórico de auditorias anteriores
  4. `ReportGenerator` lê versão do JSON e a emite mesmo sem acesso ao git
**Plans**: TBD

---

### Phase 21: ST-01 Títulos
**Goal**: Validador `01_titulos.json` que detecta violações de formatação no título PT (centralizado, bold, sem caixa alta, sem ponto final) e EN (centralizado, itálico)
**Depends on**: Phase 9 (M1 complete — parser com TipoSecao necessário)
**Parallelizable with**: Phases 22-31
**Requirements**: ST-01
**Success Criteria** (what must be TRUE):
  1. Título em CAIXA ALTA no `.md` emite violação `st_titulo_caixa_alta`
  2. Título com ponto final emite violação separada
  3. Ausência de título EN (abstract title) emite violação de componente ausente
  4. Testes com artigo Eólica identificam corretamente a seção TÍTULO pelo heading hierárquico
**Plans**: TBD

### Phase 22: ST-02 Autores
**Goal**: Validador `02_autores.json` que verifica formato CAIXA ALTA bold à direita e presença de footnote numérico de qualificação
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21, 23-31
**Requirements**: ST-02
**Success Criteria** (what must be TRUE):
  1. Autor sem CAIXA ALTA emite violação `st_autor_formato`
  2. Ausência de footnote numérico após nome do autor emite violação `st_autor_sem_footnote`
  3. Múltiplos autores são verificados individualmente
  4. Artigo Eólica com 2 autores corretos retorna 0 violações neste validador
**Plans**: TBD

### Phase 23: ST-03 Resumo
**Goal**: Validador `03_resumo_palavras_chave.json` que conta palavras do resumo (max 150), verifica 5 palavras-chave e ausência de citações
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-22, 24-31
**Requirements**: ST-03
**Success Criteria** (what must be TRUE):
  1. Resumo com 151 palavras emite violação `st_resumo_excede_limite` com contagem exata
  2. Resumo com 4 palavras-chave emite violação `st_palavras_chave_insuficientes`
  3. Resumo com citação `(Leff, 2006)` emite violação `st_resumo_citacao_proibida`
  4. Abstract EN é verificado com as mesmas regras (150 palavras, 5 keywords)
**Plans**: TBD

### Phase 24: ST-04 Sumário
**Goal**: Validador `03b_sumario.json` que verifica estrutura linha-única com indicativo numérico e número de página alinhado
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-23, 25-31
**Requirements**: ST-04
**Success Criteria** (what must be TRUE):
  1. Entrada de sumário sem número de página emite violação `st_sumario_sem_pagina`
  2. Entrada com dois pontos entre título e página emite violação (dois-pontos proibidos)
  3. Hierarquia incorreta (subseção sem seção pai) emite violação `st_sumario_hierarquia`
  4. Testes unitários com 3 casos de sumário válido e 3 inválido passam
**Plans**: TBD

### Phase 25: ST-05 Introdução
**Goal**: Validador `04_introducao.json` que detecta citações `(Autor, ano)` em qualquer parágrafo da introdução e ausência de voz reflexiva
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-24, 26-31
**Requirements**: ST-05
**Success Criteria** (what must be TRUE):
  1. Citação `(Leff, 2006)` na introdução emite violação `st_intro_citacao_proibida`
  2. Parágrafo da introdução em 1ª pessoa ("investigamos") emite violação de voz verbal
  3. Introdução sem delimitação de problema emite ALERTA (não ERRO) informativo
  4. Parser identifica corretamente o bloco INTRODUÇÃO pelo heading do artigo Eólica
**Plans**: TBD

### Phase 26: ST-06 Seções
**Goal**: Validador `05_secoes.json` que verifica Heading 1 numerada em CAIXA ALTA, Heading 2 bold case normal, hierarquia máxima 2 níveis e conjunção inicial em parágrafos do corpo
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-25, 27-31
**Requirements**: ST-06
**Success Criteria** (what must be TRUE):
  1. Heading 1 sem numeração emite violação `st_secao_sem_numero`
  2. Heading 3 (terceiro nível) emite violação `st_secao_hierarquia_profunda`
  3. Parágrafo do corpo sem conjunção inicial emite violação delegando ao VAL-06
  4. Heading 1 em caixa normal (sem CAIXA ALTA no `.md`) emite violação de formatação
**Plans**: TBD

### Phase 27: ST-07 Conclusão
**Goal**: Validador `06_conclusao.json` que detecta citações novas e dados/tabelas não presentes nas seções anteriores
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-26, 28-31
**Requirements**: ST-07
**Success Criteria** (what must be TRUE):
  1. Citação `(Autor, ano)` na conclusão que não aparece nas seções do corpo emite violação `st_conclusao_citacao_nova`
  2. Citação que já aparece no corpo é aceita (não é nova)
  3. Parser identifica corretamente o bloco CONCLUSÃO pelo heading do artigo Eólica
  4. Testes com artigo Eólica identificam ao menos 1 violação conhecida nesta seção
**Plans**: TBD

### Phase 28: ST-08 Referências
**Goal**: Validador `07_referencias.json` que verifica Qualis A1-A4 para artigos de periódico, ordem alfabética e formato por tipo de fonte
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-27, 29-31
**Requirements**: ST-08
**Success Criteria** (what must be TRUE):
  1. Artigo de periódico não indexado em Qualis A1-A4 emite ALERTA `st_ref_qualis_insuficiente`
  2. Referências fora de ordem alfabética emitem violação `st_ref_ordem_alfabetica`
  3. Livros são isentos da verificação de Qualis (corretamente ignorados)
  4. Referência com campo ausente (ex.: sem ano) emite violação de formato
**Plans**: TBD

### Phase 29: ST-09 Citações
**Goal**: Validador `08_citacoes.json` que verifica autor+ano sempre presentes, et al. para mais de 3 autores e traduções obrigatórias de estrangeirismos
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-28, 30-31
**Requirements**: ST-09
**Success Criteria** (what must be TRUE):
  1. Citação sem ano `(Leff, p. 45)` emite violação `st_citacao_sem_ano`
  2. 4 autores sem et al. emite violação `st_citacao_mais_3_autores`
  3. Estrangeirismo sem tradução entre parênteses emite violação `st_estrangeirismo_sem_traducao`
  4. Citação ABNT correta `(Leff, 2006, p. 75)` retorna 0 violações
**Plans**: TBD

### Phase 30: ST-10 Notas de Rodapé
**Goal**: Validador `09_notas_rodape.json` que verifica sequência numérica contínua e identificação de contexto separado do corpo
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-29, 31
**Requirements**: ST-10
**Success Criteria** (what must be TRUE):
  1. Nota de rodapé `[^3]` após `[^1]` sem `[^2]` emite violação `st_nota_sequencia_quebrada`
  2. Referência a nota inexistente (`[^99]` sem definição) emite violação
  3. Nota de rodapé sem conteúdo (referência órfã) emite violação
  4. Artigo Eólica com notas corretas retorna 0 violações neste validador
**Plans**: TBD

### Phase 31: ST-11 Página Global
**Goal**: Validador `10_pagina_global.json` que verifica o que é inferível de `.md`: recuo de parágrafo, espaçamento declarado e ausência de formatação inconsistente
**Depends on**: Phase 9 (M1 complete)
**Parallelizable with**: Phases 21-30
**Requirements**: ST-11
**Success Criteria** (what must be TRUE):
  1. Validador documenta explicitamente quais regras do JSON são verificáveis em `.md` vs. somente em PDF renderizado
  2. Regras não verificáveis em `.md` emitem INFO (não ERRO) com mensagem "verificar na renderização"
  3. Inconsistência de espaçamento detectável no `.md` emite ALERTA
  4. Testes cobrem todas as regras verificáveis com casos positivos e negativos
**Plans**: TBD

---

### Phase 32: FXA-01 Fixer Termos Lexicais
**Goal**: Fixer AUTO que substitui termos lexicais proibidos pelo 1º substituto do JSON sem interação do usuário
**Depends on**: Phase 17 (M2 complete — VAL-01 validado e testado)
**Parallelizable with**: Phases 33-36
**Requirements**: FXA-01
**Success Criteria** (what must be TRUE):
  1. "consolidar" é substituído por o 1º substituto do JSON com `confianca=1.0`
  2. Substituição preserva capitalização (ex.: "Consolidar" -> "Firmar" com C maiúsculo)
  3. Patch aplicado produz texto correto sem drift de offsets (re-usa `PatchAplicador` do M1)
  4. Re-validar o arquivo após fixer retorna 0 violações `lex_*` nos trechos corrigidos
**Plans**: TBD

### Phase 33: FXA-02 Fixer Expressões Conectivas
**Goal**: Fixer AUTO que remove ou substitui locuções conectivas proibidas pelo substituto do JSON
**Depends on**: Phase 17 (M2 complete)
**Parallelizable with**: Phases 32, 34-36
**Requirements**: FXA-02
**Success Criteria** (what must be TRUE):
  1. "além disso" é substituído por alternativa do JSON ou removido com ajuste de pontuação
  2. Substituição preserva sentido da frase (locução no início vs. meio de sentença tratadas separadamente)
  3. Patch tem `confianca >= 0.85`
  4. Re-validar após fixer retorna 0 violações de expressões conectivas nos trechos corrigidos
**Plans**: TBD

### Phase 34: FXA-03 Fixer Sinais Gráficos
**Goal**: Fixer AUTO para travessão e dois-pontos com heurísticas de contexto (enumeração vs. explicação vs. citação)
**Depends on**: Phase 17 (M2 complete)
**Parallelizable with**: Phases 32-33, 35-36
**Requirements**: FXA-03
**Success Criteria** (what must be TRUE):
  1. Travessão em enumeração é substituído por vírgula ou ponto-e-vírgula conforme contexto
  2. Dois-pontos em frase explicativa proibida recebe `requer_revisao_humana=True` quando ambiguidade alta
  3. Patch com `requer_revisao_humana=True` não é aplicado automaticamente (aguarda confirmação)
  4. Heurísticas documentadas em docstring com exemplos dos 3 casos de contexto
**Plans**: TBD

### Phase 35: FXA-04 Fixer Estrangeirismos
**Goal**: Fixer AUTO que envolve estrangeirismos detectados em itálico Markdown (`*termo*`) sem alterar o texto
**Depends on**: Phase 17 (M2 complete)
**Parallelizable with**: Phases 32-34, 36
**Requirements**: FXA-04
**Success Criteria** (what must be TRUE):
  1. "governance" em texto plano é transformado em `*governance*`
  2. "governance" já em itálico (`*governance*`) não recebe duplicação de marcação
  3. Patch tem `confianca=1.0` (operação puramente aditiva, reversível)
  4. Re-validar após fixer retorna 0 violações B1 nos trechos corrigidos
**Plans**: TBD

### Phase 36: FXA-05 Fixer cst_012 Refatorado
**Goal**: Fixer cst_012 do piloto M1 refatorado para herdar `FixerBase` e residir em `fixers/auto/` junto dos demais AUTO fixers
**Depends on**: Phase 17 (M2 complete)
**Parallelizable with**: Phases 32-35
**Requirements**: FXA-05
**Success Criteria** (what must be TRUE):
  1. Fixer migrado para `fixers/auto/cst_012.py` herdando `FixerBase`
  2. Testes do M1 para cst_012 continuam passando após refatoração (zero regressão)
  3. Fixer responde a `FixerBase.MODO = "AUTO"` corretamente
  4. Código do piloto M1 removido de localização temporária (sem duplicação)
**Plans**: TBD

---

### Phase 37: FXS-01 Fixer Dois-pontos
**Goal**: Fixer ASSISTIDO para cst_001 que propõe 3 reescritas e apresenta prompt CLI para o autor escolher
**Depends on**: Phase 36 (M5 complete — PatchAplicador e infra validados)
**Parallelizable with**: Phases 38-41
**Requirements**: FXS-01
**Success Criteria** (what must be TRUE):
  1. Frase com dois-pontos proibidos recebe 3 propostas de reescrita distintas no terminal
  2. Autor digita `1`, `2`, `3`, `n` (rejeitar) ou `e` (editar manualmente) sem crash
  3. Patch com escolha `n` recebe `EstadoPatch.REJEITADO` e violação permanece ativa no relatório
  4. Violação rejeitada aparece em seção "Pendentes (rejeitadas)" do AUDITORIA.md atualizado
**Plans**: TBD

### Phase 38: FXS-02 Fixer Gerúndio
**Goal**: Fixer ASSISTIDO para cst_004 que respeita o campo `exclusoes` do JSON e sempre opera em modo ASSISTIDO (nunca AUTO)
**Depends on**: Phase 36 (M5 complete)
**Parallelizable with**: Phases 37, 39-41
**Requirements**: FXS-02
**Success Criteria** (what must be TRUE):
  1. "estudando" é detectado como gerúndio candidato mas "Fernando" e "grande" não são
  2. Exclusões do JSON (`exclusoes` lista) filtram falsos positivos antes de emitir `Violacao`
  3. `MODO = "ASSISTIDO"` é verificado no código; tentativa de setar AUTO lança `AssertionError`
  4. Proposta de reescrita sugere forma nominal equivalente (ex.: "no estudo de")
**Plans**: TBD

### Phase 39: FXS-03 Fixer Anglicismos
**Goal**: Fixer ASSISTIDO que usa dicionário `08_citacoes.json > exemplos_traducoes_consolidadas` para sugerir tradução de anglicismos detectados
**Depends on**: Phase 36 (M5 complete)
**Parallelizable with**: Phases 37-38, 40-41
**Requirements**: FXS-03
**Success Criteria** (what must be TRUE):
  1. "governance" presente no dicionário recebe sugestão "governança" com fonte rastreável no JSON
  2. Anglicismo não presente no dicionário emite ALERTA com sugestão de adicionar ao dicionário
  3. Autor confirma ou rejeita via prompt CLI
  4. Rejeição registrada como `EstadoPatch.REJEITADO` no relatório
**Plans**: TBD

### Phase 40: FXS-04 Fixer Determinante
**Goal**: Fixer ASSISTIDO para cst_011 que sugere artigo definido/indefinido faltante e solicita confirmação do autor
**Depends on**: Phase 36 (M5 complete)
**Parallelizable with**: Phases 37-39, 41
**Requirements**: FXS-04
**Success Criteria** (what must be TRUE):
  1. "pesquisa demonstra" (sem artigo) recebe sugestão "a pesquisa demonstra" ou "esta pesquisa demonstra"
  2. Contexto é usado para inferir artigo adequado (definido vs. indefinido)
  3. Prompt exibe contexto completo (frase inteira) antes da confirmação
  4. `confianca` do Patch é declarada como 0.7 (subjetivo, requer confirmação)
**Plans**: TBD

### Phase 41: FXS-05 Fixer Conjunção Inicial
**Goal**: Fixer ASSISTIDO para B3 que sugere 5 conjunções filtradas por subtipo semântico e score >= 4 do arquivo de conjunções
**Depends on**: Phase 36 (M5 complete)
**Parallelizable with**: Phases 37-40
**Requirements**: FXS-05
**Success Criteria** (what must be TRUE):
  1. Parágrafo sem conjunção inicial recebe 5 sugestões filtradas do JSON de conjunções com score >= 4
  2. Sugestões são ordenadas por score decrescente
  3. Autor escolhe por número ou rejeita
  4. Conjunção escolhida é inserida como 1ª palavra do parágrafo com ajuste de capitalização da 2ª palavra
**Plans**: TBD

---

### Phase 42: FXL-01 Cliente Claude API
**Goal**: Cliente `anthropic` SDK com injeção de dependência, biblioteca de prompts `jinja2` e `FakeClaudeClient` para testes sem API key
**Depends on**: Phase 41 (M6 complete)
**Requirements**: FXL-01
**Success Criteria** (what must be TRUE):
  1. `ClaudeClient.completar(prompt)` retorna string com retry automático em 429 (backoff exponencial)
  2. `FakeClaudeClient` implementa a mesma interface e retorna resposta configurável nos testes
  3. Templates `prompts/*.j2` renderizam com `jinja2` injetando lista de termos proibidos completa
  4. `dry_run=True` estima tokens e custo sem chamar a API real
**Plans**: TBD

### Phase 43: FXL-02 Fixer Pseudossíntese
**Goal**: Fixer LLM para cst_008 que reescreve pseudossíntese conciliatória via Claude com pós-validação obrigatória
**Depends on**: Phase 42
**Requirements**: FXL-02
**Success Criteria** (what must be TRUE):
  1. Parágrafo com cst_008 detectado é enviado ao Claude com prompt especializado em cst_008
  2. Resposta LLM passa por re-validação M2 antes de aceitar o patch
  3. Se resposta LLM introduz violação nova, patch é descartado e `EstadoPatch.SUPRIMIDO` é registrado
  4. `temperatura=0.1` e `max_tokens=512` são configurados no cliente
**Plans**: TBD

### Phase 44: FXL-03 Fixer Tópico Numerado
**Goal**: Fixer LLM para cst_010 que reescreve tópicos numerados com rótulo nominal em parágrafo contínuo
**Depends on**: Phase 42
**Requirements**: FXL-03
**Success Criteria** (what must be TRUE):
  1. Lista numerada detectada como cst_010 é convertida em parágrafo discursivo pelo LLM
  2. Resultado tem estrutura de parágrafo académico (sem números, com conectivos)
  3. Pós-validação confirma ausência de novos termos proibidos na reescrita
  4. FakeClaudeClient em testes simula conversão correta e incorreta para testar guardrail
**Plans**: TBD

### Phase 45: FXL-04 Fixer Abertura Lacônica
**Goal**: Fixer LLM para cst_007 que reancora abertura lacônica de parágrafo com referência nominal ao autor ou conceito anterior
**Depends on**: Phase 42
**Requirements**: FXL-04
**Success Criteria** (what must be TRUE):
  1. Abertura curta detectada como cst_007 recebe reescrita com ancoragem nominal pelo LLM
  2. Contexto do parágrafo anterior é incluído no prompt para reancoragem coerente
  3. Pós-validação após reescrita confirma ausência de cst_007 e termos proibidos
  4. Tamanho do prompt (parágrafo + contexto + lista negra) documentado e < 4k tokens
**Plans**: TBD

### Phase 46: FXL-05 Fixer Coocorrência
**Goal**: Fixer LLM para coc_007 VERMELHO_FORTE que reescreve o parágrafo inteiro para eliminar todas as coocorrências simultâneas
**Depends on**: Phase 42
**Requirements**: FXL-05
**Success Criteria** (what must be TRUE):
  1. Parágrafo com coc_007 ativo é enviado com todas as violações individuais listadas no prompt
  2. Reescrita elimina todas as violações primitivas que compõem a coocorrência
  3. Pós-validação confirma que nenhuma das violações primitivas reaparece
  4. `MAX_TENTATIVAS_LLM=2` é respeitado; na 2ª falha, patch recebe `SUPRIMIDO` e escala para revisão humana
**Plans**: TBD

### Phase 47: FXL-06 Fixer Citação Proibida
**Goal**: Fixer LLM B2 que reescreve parágrafo de introdução ou conclusão removendo citação proibida e integrando a informação organicamente
**Depends on**: Phase 42
**Requirements**: FXL-06
**Success Criteria** (what must be TRUE):
  1. Parágrafo com `(Leff, 2006)` na introdução é reescrito sem a citação, mantendo a ideia
  2. Versão reescrita não introduz nova citação (pós-validação ST-05 confirma)
  3. Prompt inclui o texto original completo e indica qual citação deve ser removida
  4. Resultado tem qualidade acadêmica preservada (informação integrada, não apenas deletada)
**Plans**: TBD

### Phase 48: FXL-07 Pós-validação LLM
**Goal**: Módulo de pós-validação obrigatória que re-roda todos os validadores M2 sobre a saída LLM antes de aceitar qualquer patch
**Depends on**: Phase 47
**Requirements**: FXL-07
**Success Criteria** (what must be TRUE):
  1. Saída LLM com novo termo proibido é detectada antes de aceitar patch
  2. Patch rejeitado por pós-validação recebe `EstadoPatch.SUPRIMIDO` com razão registrada
  3. Pós-validação roda em < 500ms (subset dos validadores M2, não M3-M4)
  4. Testes unitários simulam saída LLM com e sem violações novas e verificam comportamento correto
**Plans**: TBD

### Phase 49: FXL-08 Guardrail LLM
**Goal**: Guardrails completos para M7: MAX_ITERACOES, MAX_TENTATIVAS_LLM, temperatura 0.1, dry-run mode e detecção de ciclo
**Depends on**: Phase 48
**Requirements**: FXL-08
**Success Criteria** (what must be TRUE):
  1. Após `MAX_ITERACOES=3` tentativas sem convergência, loop para e escala para `REVISAO_HUMANA`
  2. Dry-run exibe estimativa de custo em USD antes de qualquer chamada à API
  3. Detecção de ciclo: se conjunto de `regra_id` ativos é igual entre iterações, loop para imediatamente
  4. Log `loguru` de cada tentativa LLM com tokens input/output e custo estimado
**Plans**: TBD

---

### Phase 50: ORC-01 Orchestrator Validador
**Goal**: Orchestrator validador com execução paralela via ThreadPoolExecutor e ondas topológicas (primitivos -> agregadores -> estruturais)
**Depends on**: Phase 20 (M3 complete) e Phase 31 (M4 complete)
**Requirements**: ORC-01
**Success Criteria** (what must be TRUE):
  1. Primitivos (M2) são executados em paralelo via ThreadPoolExecutor(max_workers=cpu_count)
  2. Barreira explícita: agregadores (M3) iniciam somente após todos os primitivos completarem
  3. Estruturais (M4) iniciam após barreira dos primitivos (paralelos entre si)
  4. Tempo total de execução < 5s (benchmark integrado ao orchestrator)
**Plans**: TBD

### Phase 51: ORC-02 Orchestrator Fixer
**Goal**: Orchestrator fixer com loop validar->fixar->revalidar e guardrail anti-loop que para se novas violações >= antigas
**Depends on**: Phase 49 (M7 complete)
**Requirements**: ORC-02
**Success Criteria** (what must be TRUE):
  1. Loop executa até convergência (0 violações) ou `MAX_ITERACOES=3`, o que vier primeiro
  2. Se `len(novas_violacoes) >= len(violacoes_anteriores)`, loop para com `STOP` registrado
  3. Relatório final distingue violações corrigidas, rejeitadas e em revisão humana
  4. Loop testado com caso artificial de cst_001 <-> cst_003 ciclando (deve parar em iteração 2)
**Plans**: TBD

### Phase 52: ORC-03 CLI Unificado
**Goal**: CLI `typer` com 3 comandos (`validar`/`corrigir`/`auditar`) com autocompletion, Rich output e saída JSON opcional
**Depends on**: Phase 50, Phase 51
**Requirements**: ORC-03
**Success Criteria** (what must be TRUE):
  1. `validar artigo.md --output json` produz `violacoes.json` válido e `AUDITORIA.md` simultaneamente
  2. `corrigir artigo.md --dry-run` exibe diff sem modificar arquivo
  3. `auditar artigo.md` produz relatório completo com todas as ondas e estatísticas
  4. `validar --help` exibe documentação completa de cada flag com autocompletion funcional
**Plans**: TBD

### Phase 53: ORC-04 Testes Validadores
**Goal**: Suite de testes unitários por validador com input controlado (frases positivas + variantes + negativas) usando pytest
**Depends on**: Phase 50
**Requirements**: ORC-04
**Success Criteria** (what must be TRUE):
  1. Cada validador (M2-M4) tem ao menos 3 testes positivos e 3 testes negativos
  2. `pytest --cov=biblio_validador` retorna cobertura >= 80% nos módulos de validação
  3. Testes rodam em < 30s sem acesso à rede ou API
  4. CI: `pytest` passa em `uv run pytest` sem configuração adicional
**Plans**: TBD

### Phase 54: ORC-05 Testes Fixers
**Goal**: Suite de testes unitários por fixer (violação -> patch esperado) incluindo testes de pós-validação com FakeClaudeClient
**Depends on**: Phase 51
**Requirements**: ORC-05
**Success Criteria** (what must be TRUE):
  1. Cada fixer (M5-M7) tem teste que verifica: violação entrada -> patch saída com campos corretos
  2. `FakeClaudeClient` é usado em testes M7 sem necessidade de API key real
  3. Teste de drift de offsets com 5 patches simultâneos passa para cada fixer AUTO
  4. Cobertura >= 75% nos módulos de fixers
**Plans**: TBD

### Phase 55: ORC-06 Integração LaTeX
**Goal**: Hook no `build.sh` do template LaTeX que executa `validar` antes de compilar e interrompe o build se houver ERRO
**Depends on**: Phase 52
**Requirements**: ORC-06
**Success Criteria** (what must be TRUE):
  1. `./build.sh` chama `validar artigo.md` antes do `pdflatex`; se exit code != 0, build aborta
  2. Hook é somente de validação (nunca executa `corrigir` automaticamente)
  3. Mensagem de erro do validador aparece no terminal antes da mensagem de aborto do build
  4. `./build.sh --skip-validar` permite bypass explícito documentado
**Plans**: TBD

### Phase 56: ORC-07 Integração GDocs
**Goal**: Auditoria pré-render no pipeline GDocs que executa `auditar` via `gws CLI` antes de criar o Google Doc
**Depends on**: Phase 52
**Requirements**: ORC-07
**Success Criteria** (what must be TRUE):
  1. `criar_template.py` chama `auditar artigo.md` antes de enviar conteúdo ao GDocs
  2. Se auditoria retorna ERRO, script pergunta confirmação antes de continuar
  3. Log de auditoria é salvo em `auditoria/AUDITORIA_gdocs_YYYYMMDD.md` antes do upload
  4. Flag `--force` ignora auditoria e procede com upload (escape hatch documentado)
**Plans**: TBD

### Phase 57: ORC-08 Pre-commit Hook
**Goal**: Hook pre-commit opcional que valida arquivos `.md` modificados antes de cada commit no repo do doutorado
**Depends on**: Phase 52
**Requirements**: ORC-08
**Success Criteria** (what must be TRUE):
  1. `.pre-commit-hooks.yaml` configurado para `validar` arquivos `.md` staged
  2. Commit com arquivo `.md` contendo violação ERRO é bloqueado com mensagem clara
  3. `SKIP=biblio-validador git commit` permite bypass explícito
  4. `pre-commit install` em qualquer artigo do repo configura o hook automaticamente
**Plans**: TBD

### Phase 58: ORC-09 Output JSON
**Goal**: Output JSON estruturado `violacoes.json` com todos os campos de `Violacao` serializados para integração com tooling externo
**Depends on**: Phase 52
**Requirements**: ORC-09
**Success Criteria** (what must be TRUE):
  1. `validar artigo.md --output json` produz `violacoes.json` válido contra schema publicado
  2. JSON inclui metadados: arquivo, data, versões dos JSONs de regra aplicados, hash git
  3. Schema `violacoes.schema.json` documentado e incluído no repo
  4. `cat violacoes.json | jq '.violacoes[] | select(.severidade == "ERRO")'` funciona corretamente
**Plans**: TBD

### Phase 59: ORC-10 Logging Estruturado
**Goal**: Logging `loguru` 0.7.3 com 4 níveis (DEBUG/INFO/WARN/ERROR) integrado a todos os módulos, configurável via CLI flag
**Depends on**: Phase 52
**Requirements**: ORC-10
**Success Criteria** (what must be TRUE):
  1. `validar artigo.md --log-level debug` exibe cada regex testado com resultado
  2. `validar artigo.md` (sem flag) exibe apenas INFO+ (progresso e resultado)
  3. Erros de leitura de JSON de regra emitem ERROR com path do arquivo e stack trace
  4. Logging não vaza para stdout em modo `--output json` (apenas para stderr)
**Plans**: TBD

## Progress

**Execution Order:**
M1: Phases 1-9 (sequencial) -> M2: Phases 10-17 (10-16 em paralelo, 17 bloqueado por 10-16) -> M3: Phases 18-20 (sequencial) -> M4: Phases 21-31 (em paralelo) -> M5: Phases 32-36 (em paralelo) -> M6: Phases 37-41 (em paralelo) -> M7: Phases 42-49 (42 primeiro, 43-47 em paralelo, 48-49 sequenciais) -> M8: Phases 50-59 (com dependências internas)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Bootstrap | M1 | 0/1 | Not started | - |
| 2. Parser Markdown | M1 | 0/? | Not started | - |
| 3. Dataclasses Core | M1 | 0/? | Not started | - |
| 4. Contratos ABC | M1 | 0/? | Not started | - |
| 5. PatchAplicador | M1 | 0/? | Not started | - |
| 6. Validador Piloto cst_012 | M1 | 0/? | Not started | - |
| 7. Fixer AUTO Piloto cst_012 | M1 | 0/? | Not started | - |
| 8. Orchestrator Mínimo | M1 | 0/? | Not started | - |
| 9. Pipeline E2E | M1 | 0/? | Not started | - |
| 10. VAL-01 Termos Lexicais | M2 | 0/? | Not started | - |
| 11. VAL-02 Expressões Conectivas | M2 | 0/? | Not started | - |
| 12. VAL-03 Colocações Semânticas | M2 | 0/? | Not started | - |
| 13. VAL-04 Construções Sintáticas | M2 | 0/? | Not started | - |
| 14. VAL-05 Sinais Gráficos | M2 | 0/? | Not started | - |
| 15. VAL-06 Conjunções | M2 | 0/? | Not started | - |
| 16. VAL-07 Parser LaTeX | M2 | 0/? | Not started | - |
| 17. VAL-08 Benchmark | M2 | 0/? | Not started | - |
| 18. AGR-01 Coocorrência | M3 | 0/? | Not started | - |
| 19. AGR-02 Escrita Canônica | M3 | 0/? | Not started | - |
| 20. AGR-03 Versionamento | M3 | 0/? | Not started | - |
| 21. ST-01 Títulos | M4 | 0/? | Not started | - |
| 22. ST-02 Autores | M4 | 0/? | Not started | - |
| 23. ST-03 Resumo | M4 | 0/? | Not started | - |
| 24. ST-04 Sumário | M4 | 0/? | Not started | - |
| 25. ST-05 Introdução | M4 | 0/? | Not started | - |
| 26. ST-06 Seções | M4 | 0/? | Not started | - |
| 27. ST-07 Conclusão | M4 | 0/? | Not started | - |
| 28. ST-08 Referências | M4 | 0/? | Not started | - |
| 29. ST-09 Citações | M4 | 0/? | Not started | - |
| 30. ST-10 Notas de Rodapé | M4 | 0/? | Not started | - |
| 31. ST-11 Página Global | M4 | 0/? | Not started | - |
| 32. FXA-01 Fixer Termos Lexicais | M5 | 0/? | Not started | - |
| 33. FXA-02 Fixer Expressões Conectivas | M5 | 0/? | Not started | - |
| 34. FXA-03 Fixer Sinais Gráficos | M5 | 0/? | Not started | - |
| 35. FXA-04 Fixer Estrangeirismos | M5 | 0/? | Not started | - |
| 36. FXA-05 Fixer cst_012 Refatorado | M5 | 0/? | Not started | - |
| 37. FXS-01 Fixer Dois-pontos | M6 | 0/? | Not started | - |
| 38. FXS-02 Fixer Gerúndio | M6 | 0/? | Not started | - |
| 39. FXS-03 Fixer Anglicismos | M6 | 0/? | Not started | - |
| 40. FXS-04 Fixer Determinante | M6 | 0/? | Not started | - |
| 41. FXS-05 Fixer Conjunção Inicial | M6 | 0/? | Not started | - |
| 42. FXL-01 Cliente Claude API | M7 | 0/? | Not started | - |
| 43. FXL-02 Fixer Pseudossíntese | M7 | 0/? | Not started | - |
| 44. FXL-03 Fixer Tópico Numerado | M7 | 0/? | Not started | - |
| 45. FXL-04 Fixer Abertura Lacônica | M7 | 0/? | Not started | - |
| 46. FXL-05 Fixer Coocorrência | M7 | 0/? | Not started | - |
| 47. FXL-06 Fixer Citação Proibida | M7 | 0/? | Not started | - |
| 48. FXL-07 Pós-validação LLM | M7 | 0/? | Not started | - |
| 49. FXL-08 Guardrail LLM | M7 | 0/? | Not started | - |
| 50. ORC-01 Orchestrator Validador | M8 | 0/? | Not started | - |
| 51. ORC-02 Orchestrator Fixer | M8 | 0/? | Not started | - |
| 52. ORC-03 CLI Unificado | M8 | 0/? | Not started | - |
| 53. ORC-04 Testes Validadores | M8 | 0/? | Not started | - |
| 54. ORC-05 Testes Fixers | M8 | 0/? | Not started | - |
| 55. ORC-06 Integração LaTeX | M8 | 0/? | Not started | - |
| 56. ORC-07 Integração GDocs | M8 | 0/? | Not started | - |
| 57. ORC-08 Pre-commit Hook | M8 | 0/? | Not started | - |
| 58. ORC-09 Output JSON | M8 | 0/? | Not started | - |
| 59. ORC-10 Logging Estruturado | M8 | 0/? | Not started | - |
