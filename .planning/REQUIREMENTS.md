# Requirements: Validador & Fixer Acadêmico

**Defined:** 2026-05-03
**Core Value:** Garantir que todo texto produzido no doutorado passe pelos mesmos crivos editoriais sem fricção manual, com correções rastreáveis até a regra-fonte em JSON canônico

## v1 Requirements

### Core (M1 — Piloto + Infraestrutura)

- [ ] **CORE-01**: Parser que lê `.md` (CommonMark + footnotes) em parágrafos + frases + linhas com offsets byte-exact via `markdown-it-py` 4.0.0
- [ ] **CORE-02**: Dataclass `Violacao(arquivo, linha_inicio, linha_fim, col_inicio, col_fim, trecho_violador, regra_id, regra_nome, severidade, sugestoes, principio_canonico_violado)`
- [ ] **CORE-03**: Dataclass `Patch(arquivo, linha, col_inicio, col_fim, texto_original, texto_substituto, motivo, confianca, requer_revisao_humana, estado)` com enum EstadoPatch (PROPOSTO/ACEITO/REJEITADO/SUPRIMIDO)
- [ ] **CORE-04**: ABC `ValidadorBase` com `JSON_SOURCE`, `SCOPE`, `carregar_regras()`, `validar(paragrafos) -> list[Violacao]`
- [ ] **CORE-05**: ABC `FixerBase` com `VIOLACAO_IDS`, `MODO`, `pode_corrigir(v)`, `propor_patches(v, contexto) -> list[Patch]`, `aplicar(patches, modo_interativo)`
- [ ] **CORE-06**: Aplicador de patches em ordem reversa preservando byte-exact (evita drift de offsets)
- [ ] **CORE-07**: Validador piloto cst_012 (anúncio metarretórico) ponta a ponta sobre `.md`
- [ ] **CORE-08**: Fixer AUTO piloto cst_012 com regex determinístico (`A descoberta específica de X (Y) reside em VERBAR` → `X (Y) VERBA`)
- [ ] **CORE-09**: Orchestrator mínimo + relatório `AUDITORIA.md` priorizado por severidade
- [ ] **CORE-10**: Pipeline funcional contra `Artigos/.../artigo.md` real (artigo Eólica Nordeste como caso de teste)
- [ ] **CORE-11**: Normalização Unicode NFC no parser (evita falhas com acentos compostos)
- [ ] **CORE-12**: Layout `src/biblio_validador/` com `pyproject.toml` + `uv` install + entry point `validar` no PATH

### Validadores Primitivos (M2)

- [ ] **VAL-01**: Validador `01_termos_lexicais_proibidos.json` (14 entradas com regex e variantes morfológicas)
- [ ] **VAL-02**: Validador `02_expressoes_conectivas_proibidas.json` (5 locuções)
- [ ] **VAL-03**: Validador `03_colocacoes_semanticas_proibidas.json` (2 entradas com gatilhos contextuais)
- [ ] **VAL-04**: Validador `04_construcoes_sintaticas_proibidas.json` (12 entradas cst_001..cst_012, respeitando campos `exclusoes` e `observacao`)
- [ ] **VAL-05**: Validador `05_sinais_graficos_proibidos.json` (travessão, dois-pontos com lookahead negativo para horários/URLs)
- [ ] **VAL-06**: Validador `02_escrita/conjuncoes/` (802 entradas, 18 subtipos) com checagem específica de conjunção inicial obrigatória em parágrafos do corpo
- [ ] **VAL-07**: Parser `.tex` (abntex2) via `pylatexenc` 2.10 com offsets via `pos_to_lineno_colno()`
- [ ] **VAL-08**: Benchmark de performance: validador deve processar artigo de 30k palavras em < 5 segundos

### Validadores Agregadores (M3)

- [ ] **AGR-01**: Validador `06_regras_coocorrencia.json` (9 regras com escopo paragrafo + escopo documento) — consome `list[Violacao]` dos primitivos
- [ ] **AGR-02**: Validador `escrita_canonica.json` (16 princípios, 6 perguntas teste de estresse, mapping cst→princípio canônico violado)
- [ ] **AGR-03**: Versionamento das regras: cada JSON ganha campo `versao` e relatório registra qual versão foi aplicada (rastreabilidade pós-evolução de regras)

### Validadores Estruturais ABNT (M4)

- [ ] **ST-01**: Validador `01_titulos.json` (PT centralizado bold sem caixa alta sem ponto; EN centralizado itálico)
- [ ] **ST-02**: Validador `02_autores.json` (CAIXA ALTA bold direita, footnote numérico inicial)
- [ ] **ST-03**: Validador `03_resumo_palavras_chave.json` (max 150 palavras resumo+abstract; 5 palavras-chave; rótulo bold; sem citações)
- [ ] **ST-04**: Validador `03b_sumario.json` (estrutura linha-única com indicativo numérico + página)
- [ ] **ST-05**: Validador `04_introducao.json` (PROIBIDO citações `(Autor, ano)`; voz reflexiva; tempo presente)
- [ ] **ST-06**: Validador `05_secoes.json` (Heading 1 numerada CAIXA ALTA, Heading 2 case normal bold; hierarquia 2 níveis; conjunção inicial em parágrafos do corpo)
- [ ] **ST-07**: Validador `06_conclusao.json` (PROIBIDO citações novas; sem dados/tabelas novos)
- [ ] **ST-08**: Validador `07_referencias.json` (filtro Qualis A1-A4 + WoS/Scopus para artigos; livros isentos; ordem alfabética; formato por tipo)
- [ ] **ST-09**: Validador `08_citacoes.json` (autor+ano sempre; traduções obrigatórias de estrangeirismos; >3 autores et al.)
- [ ] **ST-10**: Validador `09_notas_rodape.json` (TNR 10pt, sequencial, RP)
- [ ] **ST-11**: Validador `10_pagina_global.json` (margens 3/2/3/2; TNR 12pt; espaçamento 1.5; recuo 1.25cm; paginação canto sup direito a partir pg 2)

### Fixers AUTO (M5)

- [ ] **FXA-01**: Fixer `01_termos_lexicais_proibidos` (substituição direta pelo 1º substituto da lista)
- [ ] **FXA-02**: Fixer `02_expressoes_conectivas_proibidas`
- [ ] **FXA-03**: Fixer `05_sinais_graficos_proibidos` (travessão e dois-pontos com heurísticas de contexto)
- [ ] **FXA-04**: Fixer itálico estrangeirismos (B1) — wrap `*termo*` em palavras detectadas
- [ ] **FXA-05**: Fixer `cst_012` anúncio metarretórico (refatorar do M1 para arquitetura final)

### Fixers ASSISTIDO CLI (M6)

- [ ] **FXS-01**: Fixer dois-pontos (cst_001) — propõe 3 reescritas, user escolhe via prompt CLI
- [ ] **FXS-02**: Fixer gerúndio (cst_004) — respeita `exclusoes` do JSON
- [ ] **FXS-03**: Fixer anglicismos (B4) usando dicionário `08_citacoes.json > exemplos_traducoes_consolidadas`
- [ ] **FXS-04**: Fixer omissão de determinante (cst_011) — sugere artigo, user confirma
- [ ] **FXS-05**: Fixer conjunção inicial ausente (B3) — sugere 5 conjunções de `02_escrita/conjuncoes/` filtradas por subtipo + score>=4

### Fixers LLM via Claude API (M7)

- [ ] **FXL-01**: Cliente Claude API (`anthropic` SDK) + biblioteca de prompts `jinja2` + injeção via DI
- [ ] **FXL-02**: Fixer pseudossíntese conciliatória (cst_008)
- [ ] **FXL-03**: Fixer tópico numerado com rótulo nominal (cst_010)
- [ ] **FXL-04**: Fixer abertura lacônica com reancoragem nominal (cst_007)
- [ ] **FXL-05**: Fixer coocorrência VERMELHO_FORTE (coc_007) — reescreve parágrafo inteiro
- [ ] **FXL-06**: Fixer remoção de citação em INTRODUÇÃO/CONCLUSÃO (B2) — reescreve sem citação
- [ ] **FXL-07**: Pós-validação obrigatória da saída LLM (re-roda validadores; se introduzir nova violação, descarta patch)
- [ ] **FXL-08**: Guardrail MAX_ITERACOES + MAX_TENTATIVAS_LLM + temperatura 0.1 + dry-run mode

### Orchestrator + Integração (M8)

- [ ] **ORC-01**: Orchestrator validador (paralelo via ThreadPoolExecutor; ondas: primitivos → agregadores → estruturais)
- [ ] **ORC-02**: Orchestrator fixer (loop validar → fixar → revalidar com guardrail anti-loop infinito; STOP se novas_violacoes >= antigas)
- [ ] **ORC-03**: CLI unificado `validar artigo.md` / `corrigir artigo.md` / `auditar artigo.md` via `typer` 0.25.1
- [ ] **ORC-04**: Testes unitários por validador (input controlado → violação esperada) com `pytest`
- [ ] **ORC-05**: Testes unitários por fixer (violação → patch esperado)
- [ ] **ORC-06**: Integração no pipeline LaTeX (`01_templates/artigo_cientifico/app/latex/build.sh` chama validador antes do build)
- [ ] **ORC-07**: Integração no pipeline GDocs (auditoria pré-render via gws CLI)
- [ ] **ORC-08**: Pre-commit hook opcional para validar `.md` automaticamente em qualquer commit
- [ ] **ORC-09**: Output JSON estruturado (além de AUDITORIA.md) para integração com tooling externo
- [ ] **ORC-10**: Logging estruturado via `loguru` 0.7.3 com níveis DEBUG/INFO/WARN/ERROR

## v2 Requirements

Deferred. Tracked but not in current roadmap.

### Integração Editor

- **EDIT-01**: LSP server Python para integrar em VSCode/Neovim (real-time validation no editor)
- **EDIT-02**: Extension VSCode dedicada com decorações inline

### Métricas e Dashboard

- **MET-01**: Dashboard de evolução do artigo (violações por commit, gráfico de progresso)
- **MET-02**: Comparação entre artigos (autor mais consistente em qual conjunto de regras)

### Templates Estruturais Avançados

- **TPL-01**: Validador para template `tese_doutorado` (NBR 14724 completa)
- **TPL-02**: Validador para template `peticao_juridica`
- **TPL-03**: Validador para template `relatorio_institucional` (PPGD/CAPES)

### IA Avançada

- **IA-01**: Sugestão de reescrita usando o histórico do próprio autor (estilo Kalyl) treinado nos artigos anteriores
- **IA-02**: Auto-completar conjunções no editor com base em contexto

## Out of Scope

| Feature | Reason |
|---------|--------|
| Validação semântica de argumentação jurídica | Requer LLM com treino jurídico especializado, fora do escopo |
| Detecção de plágio | Já existe em ferramentas externas como Turnitin; sobreposição inútil |
| Tradução automática completa | Apenas glosa de estrangeirismos isolados (escopo limitado e específico) |
| Verificação fact-checking de citações | Validador confirma formato, não veracidade dos dados |
| GUI gráfica nativa | CLI primeiro; LSP cobre edição em editores; GUI é overhead |
| Suporte a `.docx` direto como input | Input sempre `.md` ou `.tex`; `.docx` só como output via pandoc |
| Internacionalização | Escopo é PT-BR acadêmico jurídico; outros idiomas exigem outras regras |
| SARIF output | Vale tem; tooling acadêmico não consome SARIF |
| Métricas Flesch-Kincaid PT-BR | Textos jurídicos densos sempre pontuam mal; falso sinal negativo |
| Modo watch | Pre-commit hook + CLI explícito cobre o caso |
| LSP server | v2 (deferred) |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| (Será preenchida pelo gsd-roadmapper na próxima etapa) | | |

**Coverage:**
- v1 requirements: 60 total (CORE: 12 + VAL: 8 + AGR: 3 + ST: 11 + FXA: 5 + FXS: 5 + FXL: 8 + ORC: 10)
- Mapped to phases: 0 (pendente roadmap)
- Unmapped: 60 ⚠️

---
*Requirements defined: 2026-05-03*
*Last updated: 2026-05-03 after initial definition*
