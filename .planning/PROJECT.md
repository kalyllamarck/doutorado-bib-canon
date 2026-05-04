# Validador & Fixer Acadêmico — Biblioteca Canônica do Doutorado

## What This Is

Sistema modular de validação e correção automatizada para artigos científicos em português brasileiro conforme regras canônicas do doutorado em Direito Constitucional (PPGD/Unifor). Lê arquivos `.md`/`.tex`, detecta violações de termos proibidos, construções sintáticas vetadas e princípios de escrita canônica, e aplica correções em três níveis (auto/assistido/LLM). Reusável em qualquer artigo, capítulo de tese ou petição.

## Core Value

**Garantir que todo texto produzido no doutorado passe pelos mesmos crivos editoriais sem fricção manual.** O autor escreve; o sistema audita contra `biblioteca_canonica/02_escrita/` e propõe correções rastreáveis até a regra-fonte. Sem isso, a biblioteca canônica é só documentação inerte.

## Requirements

### Validated

(None yet — ship to validate)

### Active

#### Núcleo (M1 piloto end-to-end)

- [ ] REQ-CORE-01: Parser que lê `.md` e `.tex` em parágrafos + frases + linhas com offsets byte-exact
- [ ] REQ-CORE-02: Dataclass `Violacao` (arquivo, linha, col, regra_id, severidade, sugestões, princípio_canônico_violado)
- [ ] REQ-CORE-03: Dataclass `Patch` (linha, col, before, after, motivo, confiança, requer_revisão)
- [ ] REQ-CORE-04: Contrato `ValidadorBase` (carregar JSON → aplicar regex → emitir Violacao[])
- [ ] REQ-CORE-05: Contrato `FixerBase` (Violacao → propor Patch[] → aplicar byte-exact)
- [ ] REQ-CORE-06: Aplicador de patches em ordem reversa (evita drift de offsets)
- [ ] REQ-CORE-07: Validador piloto cst_012 (anúncio metarretórico) ponta a ponta
- [ ] REQ-CORE-08: Fixer AUTO piloto cst_012 com regex determinístico
- [ ] REQ-CORE-09: Orchestrator mínimo + relatório `AUDITORIA.md` priorizado
- [ ] REQ-CORE-10: Validar e corrigir piloto contra `Artigos/.../artigo.md` real

#### Validadores primitivos (M2)

- [ ] REQ-VAL-01: validador `01_termos_lexicais_proibidos.json` (14 entradas)
- [ ] REQ-VAL-02: validador `02_expressoes_conectivas_proibidas.json` (5)
- [ ] REQ-VAL-03: validador `03_colocacoes_semanticas_proibidas.json` (2)
- [ ] REQ-VAL-04: validador `04_construcoes_sintaticas_proibidas.json` (12 cst)
- [ ] REQ-VAL-05: validador `05_sinais_graficos_proibidos.json` (3)
- [ ] REQ-VAL-06: validador `02_escrita/conjuncoes/` (802 entradas, 18 subtipos) com checagem de abertura de parágrafo

#### Validadores agregadores (M3)

- [ ] REQ-AGR-01: validador `06_regras_coocorrencia.json` (9 regras, consome saída dos primitivos)
- [ ] REQ-AGR-02: validador `escrita_canonica.json` (16 princípios + 6 perguntas teste de estresse + mapping cst→princípio)

#### Validadores estruturais (M4 — 1 por componente do artigo)

- [ ] REQ-ST-01: validador `01_titulos.json`
- [ ] REQ-ST-02: validador `02_autores.json`
- [ ] REQ-ST-03: validador `03_resumo_palavras_chave.json` (max 150 palavras, 5 palavras-chave)
- [ ] REQ-ST-04: validador `03b_sumario.json`
- [ ] REQ-ST-05: validador `04_introducao.json` (PROIBIDO citações)
- [ ] REQ-ST-06: validador `05_secoes.json` (CAIXA ALTA, hierarquia, recuos)
- [ ] REQ-ST-07: validador `06_conclusao.json` (PROIBIDO citações novas)
- [ ] REQ-ST-08: validador `07_referencias.json` (Qualis A1-A4, alfabética, formato por tipo)
- [ ] REQ-ST-09: validador `08_citacoes.json` (autor+ano sempre, traduções)
- [ ] REQ-ST-10: validador `09_notas_rodape.json` (TNR 10pt, sequencial)
- [ ] REQ-ST-11: validador `10_pagina_global.json` (margens, fonte, paginação)

#### Fixers AUTO (M5)

- [ ] REQ-FXA-01: fixer `01_termos_lexicais_proibidos` (substituição direta)
- [ ] REQ-FXA-02: fixer `02_expressoes_conectivas_proibidas`
- [ ] REQ-FXA-03: fixer `05_sinais_graficos_proibidos` (travessão, dois-pontos com heurísticas)
- [ ] REQ-FXA-04: fixer itálico estrangeirismos (B1)
- [ ] REQ-FXA-05: fixer `cst_012` anúncio metarretórico (refatorar do M1)

#### Fixers ASSISTIDO CLI (M6)

- [ ] REQ-FXS-01: fixer dois-pontos (cst_001) — propõe 3 reescritas
- [ ] REQ-FXS-02: fixer gerúndio (cst_004)
- [ ] REQ-FXS-03: fixer anglicismos (B4) usando dicionário de `08_citacoes.json`
- [ ] REQ-FXS-04: fixer omissão de determinante (cst_011)
- [ ] REQ-FXS-05: fixer conjunção inicial ausente (B3)

#### Fixers LLM via Claude API (M7)

- [ ] REQ-FXL-01: cliente Claude API + biblioteca de prompts jinja2
- [ ] REQ-FXL-02: fixer pseudossíntese conciliatória (cst_008)
- [ ] REQ-FXL-03: fixer tópico numerado (cst_010)
- [ ] REQ-FXL-04: fixer abertura lacônica (cst_007)
- [ ] REQ-FXL-05: fixer coocorrência VERMELHO_FORTE (coc_007)
- [ ] REQ-FXL-06: fixer remoção de citação em INTRODUÇÃO/CONCLUSÃO (B2)

#### Orchestrator + integração (M8)

- [ ] REQ-ORC-01: orchestrator validador (paralelo + ordem topológica)
- [ ] REQ-ORC-02: orchestrator fixer (loop validar → fixar → revalidar com guardrail)
- [ ] REQ-ORC-03: CLI unificado `validar artigo.md` / `corrigir artigo.md` / `auditar artigo.md`
- [ ] REQ-ORC-04: testes unitários para cada validador (input controlado → violação esperada)
- [ ] REQ-ORC-05: testes unitários para cada fixer (violação → patch esperado)
- [ ] REQ-ORC-06: integração no pipeline LaTeX (`01_templates/artigo_cientifico/app/latex/build.sh`)
- [ ] REQ-ORC-07: integração no pipeline GDocs (auditoria pré-render)
- [ ] REQ-ORC-08: pre-commit hook opcional para `.md` em qualquer artigo do repo

### Out of Scope

- Validação semântica de argumentação jurídica (requer LLM com treino jurídico, fora do escopo)
- Detecção de plágio (já existe em ferramentas externas como Turnitin)
- Tradução automática completa de textos (apenas glosa de estrangeirismos isolados)
- Verificação fact-checking de citações (validador confirma formato, não veracidade)
- GUI gráfica (CLI primeiro; GUI talvez em milestone futuro fora deste roadmap)
- Suporte a `.docx` direto (input sempre `.md` ou `.tex`; `.docx` só como output)
- Internacionalização (escopo é PT-BR acadêmico jurídico)

## Context

**Origem:** Sessão de trabalho intensa em maio/2026 sobre o artigo "Energia Eólica Nordeste" (Profa. Gina Pompeu). Identificou-se que regras editoriais aplicadas manualmente eram inconsistentes (ex.: termos proibidos detectados visualmente; reescritas reaparecendo em iterações sucessivas). A biblioteca canônica foi criada com 18 JSONs (escrita) + 11 JSONs (estrutura) + 802 conjunções classificadas, mas sem validador automatizado, ficou inerte.

**Tecnologias-base disponíveis:**
- Python 3.13+ com `uv` (venv padrão do doutorado)
- `lxml` (já usado em `_tmp_postprocess.py` do artigo Eólica)
- Claude API (para fixers LLM)
- Pandoc + abntex2 (renderização final)
- gws CLI autenticado (Google Docs)

**Material existente reusável:**
- 36 JSONs validados em `biblioteca_canonica/02_escrita/` e `01_templates/artigo_cientifico/caracteristicas/`
- Renderizador LaTeX funcional em `01_templates/artigo_cientifico/app/latex/`
- Renderizador GDocs funcional em `01_templates/artigo_cientifico/app/gdocs/`
- Artigo Eólica Nordeste serve como **caso de teste real** com violações conhecidas (cst_007, cst_008, cst_010, cst_011, cst_012 já detectadas via inspeção manual)

## Constraints

- **Tech stack:** Python 3.13+, type hints obrigatórios, max 80 chars/linha, módulo padrão `re` (regex), `dataclasses`, `pathlib`
- **Idioma:** PT-BR brasileiro (regex Unicode com `\b[a-zà-ÿ]`)
- **Performance:** validação de artigo de 30k palavras < 5 segundos
- **Reprodutibilidade:** zero dependências de rede em validadores (só fixers LLM chamam API)
- **Versionamento:** repo git próprio dentro de `biblioteca_canonica/` (já inicializado, commit `6226adc`)
- **Sem cache stateful:** cada execução parte do zero, output determinístico
- **Compatibilidade:** lê `.md` (CommonMark + footnotes) e `.tex` (LaTeX abntex2)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 1 validador por JSON, não monolito | Modularidade, testabilidade isolada, substituibilidade | — Pending |
| 3 níveis de fixer (AUTO/ASSISTIDO/LLM) | Severidade da violação determina nível de intervenção; alguns padrões exigem reescrita semântica | — Pending |
| Loop validar→fixar→revalidar com guardrail | Evita loops infinitos quando fix piora violação | — Pending |
| Patches em ordem reversa | Evita drift de offsets quando aplicação altera comprimento | — Pending |
| Piloto cst_012 antes de escalar | Validar arquitetura ponta-a-ponta com caso real (artigo Eólica) antes de gastar 11h | — Pending |
| YOLO mode + parallel + fine granularity | User pediu execução ágil; phases são pequenas e independentes (1 JSON cada) | — Pending |
| Balanced model profile (Sonnet) | Custo/qualidade adequados para validadores; Opus apenas se Sonnet falhar | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-03 after initialization*
