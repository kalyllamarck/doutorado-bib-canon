# Feature Research

**Domain:** Linter de prosa acadêmica PT-BR com regras canonizadas em JSON
**Researched:** 2026-05-04
**Confidence:** HIGH (PROJECT.md + JSONs lidos diretamente; Vale/proselint verificados via docs oficiais)

---

## Feature Landscape

### Table Stakes (Sem isto, ferramenta é inútil para o autor)

| Feature | Por que é esperado | Complexidade | Notas |
|---------|-------------------|-------------|-------|
| **Detecção de violações por regex** | Núcleo do produto; sem isto não é linter | LOW | `re` stdlib; patterns já existem nos 6 JSONs de `termos_proibidos/`. Cada validador lê 1 JSON. |
| **Relatório de violações priorizado por severidade** | Autor precisa saber o que corrigir primeiro; Vale e ESLint fazem isso | LOW | 3 níveis: ERRO (bloqueia render), ALERTA (requer revisão), INFO (sugestão). Mapear: `cst_*` = ERRO, `lex_*` = ALERTA, coocorrência = ERRO ou ALERTA por nível. |
| **Localização exata (arquivo, linha, coluna)** | Sem localização, o relatório é inutilizável | LOW | `REQ-CORE-02` já prevê offsets byte-exact. Crítico para aplicação de patches. |
| **Sugestão de reescrita vinculada à regra-fonte** | Diferencia de grep simples; proselint e Vale fornecem `replacements` | MEDIUM | `escrita_canonica.json` mapeia cada `cst_XXX → p_YY.exemplo_bom`. O validador recupera o exemplo canônico e o exibe junto da violação. |
| **Identificação da regra violada (ID rastreável)** | Permite buscar documentação, entender o porquê, e desabilitar seletivamente | LOW | `cst_001`…`cst_012`, `lex_001`…`lex_014`, `sig_001`…`sig_003`, `con_001`…`con_005`, `coc_001`…`coc_009`. IDs já existem nos JSONs. |
| **Saída legível em terminal (STDOUT padrão)** | Expectativa universal de CLI; proselint e Vale fazem | LOW | Formato `arquivo:linha:col [ERRO] regra_id — mensagem (sugestão)`. Colorize com ANSI se TTY. |
| **Saída JSON estruturada (`--output json`)** | Necessário para integração com scripts, CI e editores | LOW | Schema: `{arquivo, linha, col, regra_id, severidade, mensagem, sugestao, principio_canonico}`. Equivalente ao wire schema estável do proselint. |
| **Parser `.md` em parágrafos/frases/linhas** | Input primário do projeto é CommonMark + footnotes | MEDIUM | `REQ-CORE-01`. Preservar offsets byte-exact para patch reverso. Ignorar blocos de código e blocos de citação (`>`). |
| **Parser `.tex` (abntex2)** | Input secundário; pipeline LaTeX canônico usa `.tex` | MEDIUM | Ignorar comandos LaTeX ao validar conteúdo prosa; validar argumentos de `\footnote{}`, `\textit{}` etc. |
| **Exit code não-zero em caso de ERRO** | Requisito de integração CI; sem isso pre-commit hook não funciona | LOW | `sys.exit(1)` se qualquer violação de nível ERRO; `sys.exit(0)` se só ALERTAs (configurável). |
| **Pre-commit hook opcional** | Previne commits com violações críticas; padrão do ecossistema de qualidade | LOW | `REQ-ORC-08`. Arquivo `.pre-commit-hooks.yaml` + entrada em `.pre-commit-config.yaml` do artigo. |
| **Testes unitários por validador** | Sem testes, não há confiança na ausência de falsos positivos | MEDIUM | `REQ-ORC-04/05`. Input controlado → violação esperada; input limpo → zero violações. |

### Differentiators (Vantagem competitiva vs. Vale/proselint)

| Feature | Proposta de valor | Complexidade | Notas |
|---------|------------------|-------------|-------|
| **Regras em JSON versionado externo (não embutido)** | Vale usa YAML por regra; proselint embute regras em Python. Aqui o JSON canônico é o único ponto de verdade — mesma fonte que documenta o estilo. Alteração de regra não exige deploy de código. | LOW | `ValidadorBase.carregar_json()` lê arquivo; nenhuma regra hardcoded. Suporte a múltiplos perfis por diretório `.validador.json`. |
| **Mapeamento violação → princípio canônico** | Vale detecta mas não rastreia por que a regra existe. Aqui cada violação exibe o princípio (`p_01`…`p_16`) + a pergunta de teste de estresse (`q1`…`q6`) que ela viola. | LOW | `escrita_canonica.json > interacao_com_validador.mapeamento_cst_to_principio` já provê o mapeamento completo. Exibir no relatório: "Violação de p_16 (autor como interlocutor, não como objeto)". |
| **3 níveis de fixer (AUTO / ASSISTIDO / LLM)** | Vale tem 4 tipos de fixer (suggest/replace/remove/edit), todos determinísticos. proselint só sugere. Este sistema adiciona o nível LLM para violações que requerem reescrita semântica (cst_008 pseudossíntese). | HIGH | AUTO = regex determinístico; ASSISTIDO = propõe N opções, autor escolhe; LLM = Claude API com prompt jinja2 contextualizado. Guardrail: loop validar→fixar→revalidar com limite de iterações. |
| **Visualização de diff antes de aplicar fix** | Ruff tem `--diff`; ESLint tem `--fix-dry-run`. Vale não tem diff nativo. Este sistema mostra diff unificado (`antes/depois`) para qualquer nível de fixer antes de confirmar. | LOW | `Patch.before` / `Patch.after` já previstos em `REQ-CORE-03`. Exibir com `difflib.unified_diff`. Confirmar com `[s]im/[n]ão/[e]ditar`. |
| **Validadores estruturais ABNT por componente** | Vale valida estilo genérico. proselint não conhece estrutura de artigo. Este sistema valida componentes específicos do artigo ABNT: introdução proibida de citações, conclusão proibida de citações novas, resumo ≤ 150 palavras, hierarquia de seções em caixa alta. | HIGH | M4 (`REQ-ST-01`…`REQ-ST-11`). Requer identificação de seções por tipo, não só por linha. |
| **Validador de coocorrência amplificada** | Nenhum linter de prosa tem regras de coocorrência. `06_regras_coocorrencia.json` penaliza combinações de violações (ex.: `cst_007 + cst_012 + lex_010` = VERMELHO_FORTE). | MEDIUM | `REQ-AGR-01`. Consome saída dos primitivos; não requer re-execução de regex. |
| **Validador de conjunções (802 entradas, 18 subtipos)** | Vale pode checar existência de conectivos; não classifica por registro, score acadêmico ou polissemia. Este sistema detecta ausência de conjunção inicial de parágrafo usando 802 entradas classificadas. | MEDIUM | `REQ-VAL-06`. Checar primeira palavra de cada parágrafo contra lista por subtipo. Score acadêmico como critério de preferência. |
| **Integração nativa com renderizadores LaTeX e GDocs** | Vale e proselint são ferramentas genéricas, desacopladas de pipeline de saída. Este sistema se acopla ao `build.sh` LaTeX e ao `criar_template.py` GDocs como etapa obrigatória de pré-render. | LOW | `REQ-ORC-06/07`. Hook no Makefile ou script de build; auditoria pré-render falha se ERRO detectado. |
| **Localização de violação por footnote vs corpo** | Vale e proselint ignoram notas de rodapé ou as tratam como texto plano. Este sistema valida `[^n]` em Markdown e `\footnote{}` em LaTeX como contexto separado (regras próprias: TNR 10pt, sequencial, sem citações de abertura). | MEDIUM | `REQ-ST-10`. Parser precisa identificar footnotes como contexto `NOTA_RODAPE` separado de `CORPO`. |

### Anti-Features (Explicitamente fora do escopo)

| Feature | Por que parece atraente | Por que evitar | Alternativa |
|---------|------------------------|---------------|-------------|
| **GUI gráfica** | Usabilidade para não-técnicos | Custo de desenvolvimento desproporcionalmente alto para usuário único (o doutorando); a integração com VS Code via LSP provê feedback visual sem GUI própria | Integração com editor via LSP (vale-ls como referência); output ANSI colorido no terminal |
| **Métricas de legibilidade (Flesch-Kincaid PT-BR)** | Parece útil para aferir qualidade geral do texto | FK não foi validado para português acadêmico-jurídico de alto registro; produziria scores ruins em textos densos que são deliberadamente complexos; falso sinal negativo constante | As 6 perguntas de teste de estresse do `escrita_canonica.json` provêm avaliação qualitativa mais precisa para este domínio |
| **Modo watch (`--watch`)** | Feedback em tempo real | Adiciona complexidade de inotify/polling; o caso de uso real é rodada pré-commit e pré-render, não edição contínua; VS Code com LSP já fornece feedback contínuo | Pre-commit hook (cobertura no commit) + integração LaTeX (cobertura no render) |
| **Exportação SARIF** | Padrão de análise estática; GitHub Code Scanning consome SARIF | Overhead de formato para uso pessoal de um doutorando; GitHub Code Scanning é para código, não prosa acadêmica; o repo não é público com Code Scanning habilitado | JSON output (`--output json`) cobre todos os casos de integração necessários; SARIF pode ser gerado por wrapper externo se necessário |
| **Suporte a `.docx` como input** | Formato final de entrega | Word XML é difícil de parsear com offsets byte-exact; `python-docx` não preserva posição de caractere para patches; o projeto já usa `.md`/`.tex` como fonte de verdade | `.docx` só como output (Phase 5 do artigo); validar na fonte `.md` antes de converter |
| **Internacionalização (i18n)** | Permitiria uso em outros idiomas | Escopo é PT-BR acadêmico-jurídico; as regras, mensagens e princípios canônicos são intraduzíveis sem perda semântica; nenhum outro idioma usa estes JSONs | Escopo fixo PT-BR; mensagens e sugestões em português |
| **Detecção de plágio** | Integridade acadêmica | Já coberto por Turnitin/Urkund na Unifor; requer acesso a base de dados externos, incompatível com "zero dependências de rede em validadores" | Ferramenta externa Turnitin (já obrigatória no PPGD) |
| **Verificação de veracidade de citações (fact-checking)** | Garantir que Leff (2006, p. 22) diz o que o texto afirma | Requer RAG + LLM com acesso ao PDF; custo e latência incompatíveis com < 5s de runtime; fora do escopo definido em PROJECT.md | Validador confirma formato da citação; verificação de conteúdo fica com o autor via RAG CodexAcad |
| **LLM irrestrito como fixer** | Conveniência de "conserta tudo" | Produz texto fora do estilo canônico do autor; viola a regra de que cada citação deve ter sugestão rastreável à regra-fonte; risco de introduzir termos proibidos na correção | LLM só em M7 para cst específicos (cst_008, cst_010, cst_007, cst_004) com prompts jinja2 que injetam os princípios canônicos e exemplos proibidos/reescritos dos JSONs |
| **Validação semântica de argumentação jurídica** | Detectar raciocínio circular, falácias, incoerência tática | Requer LLM com treino jurídico + contexto do artigo inteiro; falsos positivos altíssimos; explicitamente Out of Scope em PROJECT.md | RAG CodexAcad consultado pelo autor; auditoria manual via perguntas de teste de estresse |

---

## Feature Dependencies

```
[Parser .md / .tex]
    └──requires──> [Dataclass Violacao com offsets byte-exact]
                       └──requires──> [Patch em ordem reversa]
                                          └──enables──> [Fixer AUTO]
                                          └──enables──> [Fixer ASSISTIDO]
                                          └──enables──> [Fixer LLM]

[Validadores primitivos (M2: lex, cst, sig, con)]
    └──requires──> [Parser .md/.tex]
    └──enables──> [Validador coocorrência M3]
    └──enables──> [Relatório priorizado por severidade]

[Validador coocorrência (coc_001..coc_009)]
    └──requires──> [Validadores primitivos M2] (consome saída, não reexecuta regex)

[Validador escrita_canonica.json (p_00..p_16)]
    └──requires──> [Validadores primitivos M2] (mapeamento cst→princípio)

[Validadores estruturais ABNT (M4: intro, conclusao, resumo, refs)]
    └──requires──> [Parser com identificação de seção por tipo]
    └──enhances──> [Relatório priorizado por severidade]

[Mapeamento violação → princípio canônico]
    └──requires──> [escrita_canonica.json carregado em memória]
    └──enhances──> [Sugestão de reescrita vinculada à regra-fonte]

[Fixer AUTO]
    └──requires──> [Patch em ordem reversa]
    └──enhances──> [Visualização de diff antes de aplicar]

[Fixer ASSISTIDO]
    └──requires──> [Fixer AUTO] (mesma infra de Patch)

[Fixer LLM]
    └──requires──> [Claude API + prompts jinja2]
    └──conflicts──> [Zero dependências de rede em validadores] (só fixers LLM chamam API)

[Pre-commit hook]
    └──requires──> [CLI unificado com exit code não-zero]
    └──requires──> [Saída JSON ou legível por hook]

[Integração LaTeX/GDocs]
    └──requires──> [Orchestrator com modo CI (non-interactive)]
    └──requires──> [Exit code não-zero em ERRO]

[Saída JSON estruturada]
    └──enhances──> [Pre-commit hook]
    └──enhances──> [Integração LaTeX/GDocs]
```

### Notas de dependência

- **Patch em ordem reversa** é pré-requisito de qualquer fixer: aplicar patches de baixo para cima no arquivo evita drift de offsets quando um fix altera o comprimento da linha.
- **Validador coocorrência conflita com execução paralela irrestrita**: deve rodar após todos os primitivos numa mesma passagem, nunca em paralelo com eles (depende da saída acumulada).
- **Fixer LLM conflita com a restrição "zero dependências de rede em validadores"**: o conflito é resolvido por segregação — validadores nunca chamam rede; fixers LLM chamam Claude API de forma explícita e opt-in (`corrigir --nivel llm`).
- **Validadores estruturais ABNT (M4)** requerem que o parser identifique tipo de seção (INTRODUCAO, CONCLUSAO, RESUMO, NOTAS) — funcionalidade além do parser básico de linha/parágrafo.

---

## MVP Definition

### Launch With (v1 — M1 piloto)

- [x] Parser `.md` em parágrafos/frases/linhas com offsets byte-exact
- [x] Dataclass `Violacao` e `Patch`
- [x] Contrato `ValidadorBase` e `FixerBase`
- [x] Validador + fixer AUTO piloto `cst_012` (anúncio metarretórico) — caso de uso mais frequente no artigo Eólica
- [x] Relatório `AUDITORIA.md` com violações ordenadas por severidade
- [x] Exit code não-zero se ERRO detectado
- [x] Saída STDOUT legível (arquivo:linha:col)

Critério: executar contra `artigo_final/artigo.md` do artigo Eólica e detectar as violações cst_007, cst_008, cst_010, cst_011, cst_012 já mapeadas manualmente. Nenhum falso positivo em parágrafos limpos.

### Add After Validation (v1.x — M2+M3)

- [ ] Validadores primitivos completos (lex, cst, sig, con) — adicionar quando piloto estiver estável
- [ ] Validador coocorrência — adicionar quando primitivos estiverem testados
- [ ] Mapeamento violação → princípio canônico no relatório — adicionar ao lado do piloto cst_012
- [ ] Saída JSON estruturada (`--output json`) — trigger: necessidade de integração com pre-commit ou outro script
- [ ] Visualização de diff (`--diff`) antes de aplicar fix — adicionar com primeiro fixer que altere texto não-trivialmente

### Future Consideration (v2+ — M4..M8)

- [ ] Validadores estruturais ABNT (M4) — adiar até M3 estiver completo; complexidade de identificação de seção é alta
- [ ] Fixers ASSISTIDO CLI (M6) — adiar até AUTO (M5) validado com testes
- [ ] Fixers LLM via Claude API (M7) — adiar até ASSISTIDO validado; custo de API justificado só depois de AUTO/ASSISTIDO esgotados
- [ ] Integração nativa LaTeX/GDocs (M8) — adiar até todos os validadores estáveis
- [ ] Pre-commit hook (M8) — adiar até CLI estável e testado contra artigo real

---

## Feature Prioritization Matrix

| Feature | Valor para o autor | Custo de implementação | Prioridade |
|---------|-------------------|----------------------|-----------|
| Detecção de violações por regex (primitivos) | HIGH | LOW | P1 |
| Relatório priorizado por severidade | HIGH | LOW | P1 |
| Localização exata (arquivo:linha:col) | HIGH | LOW | P1 |
| Sugestão de reescrita vinculada à regra-fonte | HIGH | LOW | P1 |
| ID de regra rastreável | HIGH | LOW | P1 |
| Saída JSON estruturada | MEDIUM | LOW | P1 |
| Exit code não-zero em ERRO | HIGH | LOW | P1 |
| Parser .md com offsets | HIGH | MEDIUM | P1 |
| Visualização de diff antes de fix | HIGH | LOW | P2 |
| Mapeamento violação → princípio canônico | HIGH | LOW | P2 |
| Fixer AUTO determinístico | HIGH | MEDIUM | P2 |
| Pre-commit hook | MEDIUM | LOW | P2 |
| Parser .tex (abntex2) | MEDIUM | MEDIUM | P2 |
| Validador coocorrência | HIGH | MEDIUM | P2 |
| Validador conjunções (802 entradas) | MEDIUM | MEDIUM | P2 |
| Validadores estruturais ABNT (M4) | HIGH | HIGH | P3 |
| Fixer ASSISTIDO CLI | MEDIUM | MEDIUM | P3 |
| Integração LaTeX/GDocs (pré-render) | HIGH | LOW | P3 |
| Fixer LLM via Claude API | MEDIUM | HIGH | P3 |
| Validador estrutural notas de rodapé | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Deve estar no piloto M1 ou imediatamente após (M2)
- P2: Deve estar no M3–M5
- P3: M6+ após P1/P2 estarem estáveis

---

## Competitor Feature Analysis

| Feature | Vale | proselint | Este sistema |
|---------|------|-----------|-------------|
| Regras externas (não embutidas) | YAML por arquivo de regra | Python embutido | JSON canônico versionado; mesma fonte que documenta o estilo |
| Tipos de fixer | suggest/replace/remove/edit (determinístico) | Apenas suggest (replacements no JSON) | AUTO (det.) + ASSISTIDO (interativo) + LLM (semântico) |
| Rastreabilidade de regra a princípio de escrita | Não (regra é arquivo YAML isolado) | Não | Sim — cst→p_YY mapeado em `escrita_canonica.json` |
| Saída JSON | Sim | Sim (wire schema estável) | Sim (schema análogo ao proselint) |
| LSP server | Sim (vale-ls, implementação em Rust) | Não nativo | Não nativo — P3, adiar; editores de texto que suportam vale-ls podem ser configurados com este tool como backend |
| Modo CI / exit code | Sim | Sim | Sim (P1) |
| Modo watch | Não documentado | Não | Não (Anti-Feature deliberada) |
| Exportação SARIF | Não nativo (via wrapper externo) | Não | Não (Anti-Feature deliberada; JSON suficiente) |
| Suporte PT-BR acadêmico | Não (focado em inglês) | Não (focado em inglês) | Sim (único diferencial do produto) |
| Validadores estruturais por componente de artigo | Não | Não | Sim (M4) |
| Validação de coocorrência de violações | Não | Não | Sim (M3, 9 regras) |
| Métricas de legibilidade | Sim (Flesch-Kincaid para inglês) | Não | Não (Anti-Feature deliberada) |
| Pre-commit hook | Sim (via exit code + .pre-commit-hooks.yaml) | Sim | Sim (M8, via exit code) |
| Input .md | Sim (markup-aware) | Texto plano | Sim (CommonMark + footnotes) |
| Input .tex | Sim | Não | Sim (abntex2-aware) |
| Input .docx | Não | Não | Não (Anti-Feature deliberada) |
| Regras de conjunções com score acadêmico | Não | Não | Sim (802 entradas, 18 subtipos, M2) |

---

## Sources

- PROJECT.md lido diretamente: `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/.planning/PROJECT.md`
- JSONs canônicos lidos diretamente: `02_escrita/escrita_canonica.json`, `02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json`
- Vale official docs: https://vale.sh/docs/ (verificado via WebFetch, MEDIUM confidence — docs não listaram todos os output formats explicitamente)
- Vale GitHub: https://github.com/vale-cli/vale (MEDIUM confidence via WebSearch)
- Vale LSP (vale-ls): https://vale.sh/docs/ — implementação em Rust separada do CLI principal (HIGH confidence)
- proselint GitHub: https://github.com/amperser/proselint (MEDIUM confidence via WebSearch)
- proselint PyPI / wire schema JSON: https://pypi.org/project/proselint/ (MEDIUM confidence)
- Ruff `--diff` mode: https://docs.astral.sh/ruff/linter/ (HIGH confidence — padrão documentado)
- ESLint `--fix-dry-run`: https://eslint.org/docs/latest/use/command-line-interface (HIGH confidence)
- ALT (readability PT-BR): https://arxiv.org/pdf/2210.00553 (MEDIUM confidence — ferramenta acadêmica, não produção)
- Flesch-Kincaid PT-BR: nenhum linter de prosa com suporte verificado para PT-BR acadêmico (LOW confidence de existência de ferramenta pronta)
- SARIF: https://docs.oasis-open.org/sarif/sarif/v2.0/ — formato padrão, não suportado nativamente por Vale

---

*Feature research for: Validador & Fixer Acadêmico — Biblioteca Canônica do Doutorado*
*Researched: 2026-05-04*
