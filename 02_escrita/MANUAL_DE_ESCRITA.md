# Manual de Escrita — Método de Aplicação

> Este manual NÃO repete conteúdo das fontes canônicas. Documenta apenas o **método de aplicação**: ordem de consulta, fluxo de validação, resolução de conflitos, gatilhos por zona do texto.
> Conteúdo de regras está em: `escrita_canonica.json`, `escrita_proibida/*.json`, `conjuncoes/INDEX.json`.
> Conteúdo de voz está em: `voz_autoral.json` (v2).

---

## 1. Hierarquia de fontes (em caso de conflito)

```
1. escrita_canonica.json                    (princípios universais positivos — p_00..p_20)
2. escrita_proibida/*.json                  (regras negativas com regex — 7 categorias)
3. voz_autoral.json                         (voz autoral da tese — 3 eixos, anti-voz, playbook)
4. conjuncoes/INDEX.json + guia.md          (rotação e substituição de conjunções — p_20)
5. 04_normas/INDEX.json + NBRs              (normas ABNT + Guia PPGD — para questões de forma)
6. rag_acad/escrita_academica/01-10         (módulos de referência ampla; eventual consulta)
```

Conflito dentro da mesma camada → id maior prevalece (p_19 vence p_03 se houver disputa). Conflito entre canon e RAG → canon vence. Conflito entre ABNT e Guia PPGD → ver `04_normas/guia_ppgd_unifor.json.regra_precedencia`.

---

## 2. Ordem de aplicação durante a redação

```
[antes de escrever]
  → voz_autoral.json: principio_zero.regra_mae (regra-mãe v_00)
  → voz_autoral.json: mapa_eixo_zona.zonas[<zona>] (qual eixo aqui?)
  → voz_autoral.json: eixos[*].marcas_obrigatorias
  → voz_autoral.json: exemplos_canonicos_paragrafo_inteiro (calibrar ouvido)
  → escrita_canonica.json (princípios universais p_00..p_20)

[durante a escrita]
  → conjuncoes/INDEX.json + conjuncoes/guia.md (rotação p_20)
  → voz_autoral.json: regras_de_estilo_complementares.transicao_entre_autores
  → voz_autoral.json: principios_estruturantes (v_01..v_06 — POR QUÊ de cada decisão)

[depois de escrever — antes de fechar parágrafo]
  → voz_autoral.json: principio_zero.criterio_operacional.checks (4 gatilhos mínimos)
  → voz_autoral.json: testes_de_estresse.perguntas (te_01..te_08, observáveis)
  → voz_autoral.json: anti_voz.padroes_proibidos (av_01..av_06)

[depois do parágrafo — antes de commit]
  → lint contra escrita_proibida/*.json (regex automático)
  → se falha: voz_autoral.json: playbook_remediacao.falhas_e_correcoes
```

---

## 3. Mapa eixo → zona do texto (regra de gatilho)

| Zona | Eixo 1 (estrutural) | Eixo 2 (pedagógico) | Eixo 3 (literário) |
|------|---------------------|---------------------|--------------------|
| Título de capítulo | — | — | ✓ obrigatório |
| Parágrafo de abertura de capítulo | ✓ | ✓ obrigatório | ✓ permitido |
| Preview ordinal de seção | ✓ | ✓ obrigatório | ✗ |
| Sustentação dogmática | ✓ | — | ✗ |
| Análise jurisprudencial | ✓ | — | ✗ |
| Transição maior entre seções | ✓ | ✓ obrigatório | ✓ permitido |
| Tomada de posição | ✓ | ✓ marcador autoral p_19 obrigatório | — |
| Síntese/conclusão parcial | ✓ | ✓ | — |
| Pré-textuais (resumo, abstract) | ✓ exclusivo | ✗ | ✗ |
| Conclusão da tese | ✓ | ✓ | ✓ moderado (sem citações) |

Regra: marcar zona ANTES de escrever. Eixo errado na zona errada = falha no teste de estresse.

---

## 4. Resolução de tensões catalogadas

Em `escrita_canonica.json` há bloco `tensoes_resolvidas` com pares de princípios em aparente conflito + resolução oficial. Consultar SEMPRE que dois princípios parecem se contradizer antes de inventar resolução nova.

Tensões já resolvidas no canon (não reabrir sem patch documentado):
- `p_09` (conectivos discretos no meio) × abertura obrigatória com conjunção
- `p_07` (não encenar lógica) × `se/então` legítimo
- `p_03` (banir gerúndios) × gerúndio de simultaneidade
- `p_08` (não sinalizar esqueleto) × `p_17` (preparação semântica) — resolvido via `padroes_autorizados` (preview híbrido + síntese dedutiva)

Patch ao canon = mudar `escrita_canonica.json` + atualizar `tensoes_resolvidas` + sync `voz_autoral.json`. Nunca patch só do RAG.

---

## 5. Fluxo de validação por parágrafo

O manual NÃO mantém checklist próprio — todas as validações vivem nos JSONs canônicos, e o manual apenas indica a ordem de execução.

### 5.1 Ordem canônica de aplicação

```
[passo 1] Identificar zona (§3 deste manual)
[passo 2] Aplicar criterio_operacional do principio_zero da voz
          → voz_autoral.json: principio_zero.criterio_operacional.checks
          (4 checks observáveis: pessoa gramatical, pulso narrativo,
           fechamento autoral, ausência de sumário neutro)

[passo 3] Aplicar os 8 testes de estresse observáveis
          → voz_autoral.json: testes_de_estresse.perguntas
          (te_01 a te_08 — cada um com sinal lexical/sintático
           e princípio violado quando falha)

[passo 4] Verificar os 6 padrões de anti-voz
          → voz_autoral.json: anti_voz.padroes_proibidos
          (av_01 a av_06 — sumário neutro, 1ª pessoa disfarçada,
           oração curta isolada, metáfora ornamental, marcador excessivo,
           recurso literário em zona dogmática)

[passo 5] Aplicar lint regex contra escrita_proibida/
          → escrita_proibida/*.json (7 categorias)

[passo 6] Em caso de falha, consultar playbook
          → voz_autoral.json: playbook_remediacao.falhas_e_correcoes
          (correção canônica por falha — evita decisão ad hoc)
```

### 5.2 Notas operacionais

- O `criterio_operacional` do `principio_zero` é gatilho mínimo: se qualquer um dos 4 checks falhar, parar e revisar antes de seguir.
- Os 8 testes de estresse (te_01..te_08) substituem o checklist antigo de 14 itens que vivia neste manual. Migração feita em 2026-05-12 para evitar duplicação entre manual (prosa) e JSON (estrutura) — a fonte de verdade é o JSON.
- O playbook em `voz_autoral.json` cobre 7 falhas típicas. Falhas novas devem ser registradas lá, não aqui.
- Para parágrafos em zona dogmática ou jurisprudencial, conferir explicitamente `te_07` (zero recurso literário) e `av_06` (proibição de eixo 3 nessas zonas).
- Distinção crítica entre metáfora isolada (ornamental, proibida — av_04) e metáfora durável (motivo recorrente, autorizada — v_04): conferir `voz_autoral.json: eixos[2].metaforas_duraveis_canonizadas`. Exemplo canônico: Sísifo na Dissertação 2025 reaparece em p.17 (título), p.19 (corpo), p.22 (abertura de capítulo).

---

## 6. Como pedir aplicação ao Claude (em sessão)

**Forma curta (dentro do repo Tese):**
> "Aplique a voz canônica e as regras de escrita."

Claude segue `Tese/CLAUDE.md` → `biblioteca_canonica_doutorado/02_escrita/`. Constituição já carregada na sessão.

**Forma curta (sessão sem CLAUDE.md carregado):**
> "Use o `MANUAL_DE_ESCRITA.md` em `biblioteca_canonica_doutorado/02_escrita/` como mapa. Aplique `escrita_canonica.json` + `escrita_proibida/` + `voz_autoral.json`."

**Forma com zona explícita:**
> "Escreva [trecho] como abertura de capítulo. Eixo 3 obrigatório, eixo 2 obrigatório, preview ordinal com preparação prévia p_17."

---

## 7. Quando atualizar este manual

- Nova fonte canônica criada → adicionar à hierarquia §1.
- Novo passo na ordem de aplicação → adicionar bloco em §2.
- Nova zona do texto identificada → adicionar linha à tabela §3 + atualizar `voz_autoral.json: mapa_eixo_zona`.
- Nova tensão resolvida no canon → adicionar bullet em §4 (a tensão em si vive em `escrita_canonica.json: tensoes_resolvidas` ou `voz_autoral.json: tensoes_resolvidas`).
- Mudança no fluxo de validação → §5 só lista a ORDEM de execução; checks, testes, anti-padrões e playbook vivem em `voz_autoral.json` — alterar lá.
- Nova forma de pedir aplicação ao Claude → §6.

Regra invariável: o manual é mapa, não território. Toda alteração de conteúdo deve ir aos JSONs canônicos; o manual apenas atualiza o ponteiro quando uma chave/path muda.

---

*Manual criado em 2026-05-12. Versão segue a do canon: alterações materiais bumpam versão.*
