# Architecture Research

**Domain:** CLI Python — linter de prosa acadêmica PT-BR com regras editoriais em JSON
**Researched:** 2026-05-04
**Confidence:** HIGH (PROJECT.md + JSONs lidos + STACK.md + FEATURES.md como contexto)

---

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  CLI Layer (typer)                                                   │
│  validar artigo.md  |  corrigir artigo.md  |  auditar artigo.md     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  Orchestrator                                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ValidarOrchestrator            CorrigirOrchestrator         │    │
│  │  - ordem topológica             - loop validar→fixar→         │    │
│  │  - ThreadPoolExecutor           revalidar + guardrail         │    │
│  │    (primitivos em paralelo)                                   │    │
│  └────────────────────────┬────────────────────────────────────┘    │
└────────────────────────────│────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  Validadores (1 por JSON de regra)                                   │
│                                                                      │
│  [M2 — Primitivos: rodam em paralelo]                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ TLexical │ │ TConect. │ │ TColocac.│ │ TCst     │ │ TSinal   │  │
│  │ (01.json)│ │ (02.json)│ │ (03.json)│ │ (04.json)│ │ (05.json)│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │            │         │
│       └────────────┴────────────┴────────────┴────────────┘         │
│                         │ Violacao[] acumuladas                      │
│  [M3 — Agregadores: aguardam primitivos]                             │
│  ┌─────────────────────▼──────┐  ┌──────────────────────────────┐   │
│  │  CoocorrenciaValidador      │  │  EscritaCanonica Validador   │   │
│  │  (06_coocorrencia.json)     │  │  (escrita_canonica.json)     │   │
│  └─────────────────────────────┘  └──────────────────────────────┘   │
│                                                                      │
│  [M4 — Estruturais: sequenciais, dependem de seção-tipo]            │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │
│  │ Intro     │ │ Conclusao │ │ Resumo    │ │ Refs      │ ...        │
│  │ (04.json) │ │ (06.json) │ │ (03.json) │ │ (07.json) │           │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  Fixers (1 por regra; 3 categorias)                                  │
│                                                                      │
│  AUTO (M5)               ASSISTIDO (M6)          LLM (M7)           │
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────────┐  │
│  │ TLexicalFixer   │     │ DoisPontosFixer  │     │ ClaudeClient  │  │
│  │ TSinalFixer     │     │ GerundioFixer    │     │ + jinja2      │  │
│  │ Cst012Fixer     │     │ OmissaoDetFixer  │     │ prompts/      │  │
│  └─────────────────┘     └─────────────────┘     └───────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  Core Layer                                                          │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────────┐    │
│  │  Parser      │  │  PatchAplicad.│  │  ReportGenerator       │    │
│  │  (md + tex)  │  │  (ord. reversa│  │  (AUDITORIA.md + JSON) │    │
│  └──────────────┘  └───────────────┘  └────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  Dados (somente leitura em runtime)                                  │
│  biblioteca_canonica/02_escrita/termos_proibidos/*.json              │
│  biblioteca_canonica/02_escrita/escrita_canonica.json                │
│  biblioteca_canonica/02_escrita/conjuncoes/*.json                    │
│  biblioteca_canonica/01_templates/artigo_cientifico/caracteristicas/ │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Componente | Responsabilidade | Não faz |
|------------|-----------------|---------|
| `cli.py` (typer) | Recebe argumentos, chama orchestrator, exibe output Rich | Lógica de negócio |
| `ValidarOrchestrator` | Determina ordem topológica, despacha primitivos em paralelo, aguarda agregadores | Regex |
| `CorrigirOrchestrator` | Loop validar→fixar→revalidar com guardrail (max N iterações) | Aplicação de patches |
| `ValidadorBase` (ABC) | Contrato: `carregar_json()` + `validar(paragrafos) -> list[Violacao]` | Sabe de outros validadores |
| Validadores primitivos | Regex sobre texto plano do parágrafo, emitem `Violacao[]` | Lógica de coocorrência |
| `CoocorrenciaValidador` | Recebe `Violacao[]` dos primitivos, aplica multiplicadores, emite novas `Violacao[]` de nível agregado | Regex direto |
| `EscritaCanonica Validador` | Mapeia `cst_XXX` → `p_YY`, enriquece `Violacao.principio_canonico` | Detecção primária |
| Validadores estruturais | Operam sobre `Paragrafo` com `tipo_secao` (INTRODUCAO, CONCLUSAO...) | Texto bruto |
| `FixerBase` (ABC) | Contrato: `fixar(violacao) -> list[Patch]` | Aplicação ao arquivo |
| Fixers AUTO | Regex determinístico → `Patch` com `confianca=1.0` | Semântica |
| Fixers ASSISTIDO | Propõe N opções, aguarda seleção do autor | Aplicação |
| Fixers LLM | Chama `ClaudeClient` com prompt jinja2, retorna `Patch` com `confianca < 1.0` | Aplicação |
| `ClaudeClient` | Módulo isolado, injetado via DI em fixers LLM | Lógica de validação |
| `PatchAplicador` | Aplica `Patch[]` em ordem reversa (linha/col decrescentes) | Geração de patches |
| `ReportGenerator` | Serializa `Violacao[]` → `AUDITORIA.md` (Rich) + JSON estruturado | Geração de patches |
| `ParserMd` / `ParserTex` | Segmenta arquivo em `Paragrafo[]` com offsets byte-exact | Validação |

---

## Recommended Project Structure

Layout: **src layout** com pacote `validador_academico`.

Motivo do src layout: evita importação acidental do pacote sem instalação (confundindo `validador_academico/` no cwd com o pacote instalado). `uv` instala em modo editable por padrão; `pytest` exige `src/` no sys.path — configurar em `pyproject.toml [tool.pytest.ini_options] pythonpath = ["src"]`.

```
biblioteca_canonica/
├── .planning/
│   └── research/
│       └── ARCHITECTURE.md   (este arquivo)
├── src/
│   └── validador_academico/
│       ├── __init__.py
│       ├── cli.py                  # typer app — 3 comandos: validar/corrigir/auditar
│       ├── core/
│       │   ├── __init__.py
│       │   ├── modelos.py          # Violacao, Patch, Paragrafo, TipoSecao, Severidade, NivelFixer
│       │   ├── parser_md.py        # markdown-it-py → Paragrafo[] com offsets
│       │   ├── parser_tex.py       # pylatexenc → Paragrafo[] com offsets
│       │   ├── patch_aplicador.py  # aplica Patch[] em ordem reversa
│       │   └── report_generator.py # Violacao[] → AUDITORIA.md + JSON
│       ├── base/
│       │   ├── __init__.py
│       │   ├── validador_base.py   # ABC ValidadorBase (carregar_json + validar)
│       │   └── fixer_base.py       # ABC FixerBase (fixar)
│       ├── validadores/
│       │   ├── __init__.py
│       │   ├── primitivos/
│       │   │   ├── __init__.py
│       │   │   ├── termos_lexicais.py      # 01_termos_lexicais_proibidos.json
│       │   │   ├── expressoes_conectivas.py # 02_expressoes_conectivas_proibidas.json
│       │   │   ├── colocacoes.py            # 03_colocacoes_semanticas_proibidas.json
│       │   │   ├── construcoes.py           # 04_construcoes_sintaticas_proibidas.json
│       │   │   ├── sinais.py                # 05_sinais_graficos_proibidos.json
│       │   │   └── conjuncoes.py            # 02_escrita/conjuncoes/*.json (802 entradas)
│       │   ├── agregadores/
│       │   │   ├── __init__.py
│       │   │   ├── coocorrencia.py          # 06_regras_coocorrencia.json
│       │   │   └── escrita_canonica.py      # escrita_canonica.json — enriquece principio
│       │   └── estruturais/
│       │       ├── __init__.py
│       │       ├── titulos.py               # 01_titulos.json
│       │       ├── autores.py               # 02_autores.json
│       │       ├── resumo.py                # 03_resumo_palavras_chave.json
│       │       ├── introducao.py            # 04_introducao.json
│       │       ├── secoes.py                # 05_secoes.json
│       │       ├── conclusao.py             # 06_conclusao.json
│       │       ├── referencias.py           # 07_referencias.json
│       │       ├── citacoes.py              # 08_citacoes.json
│       │       ├── notas_rodape.py          # 09_notas_rodape.json
│       │       └── pagina_global.py         # 10_pagina_global.json
│       ├── fixers/
│       │   ├── __init__.py
│       │   ├── auto/
│       │   │   ├── __init__.py
│       │   │   ├── termos_lexicais_fixer.py
│       │   │   ├── expressoes_conectivas_fixer.py
│       │   │   ├── sinais_fixer.py
│       │   │   └── cst012_fixer.py          # piloto M1
│       │   ├── assistido/
│       │   │   ├── __init__.py
│       │   │   ├── dois_pontos_fixer.py     # cst_001
│       │   │   ├── gerundio_fixer.py        # cst_004
│       │   │   └── omissao_det_fixer.py     # cst_011
│       │   └── llm/
│       │       ├── __init__.py
│       │       ├── claude_client.py         # módulo isolado, injetado via DI
│       │       ├── pseudossintese_fixer.py  # cst_008
│       │       ├── topico_numerado_fixer.py # cst_010
│       │       └── abertura_laconica_fixer.py # cst_007
│       ├── orchestrator/
│       │   ├── __init__.py
│       │   ├── validar_orchestrator.py      # ordem topológica + ThreadPoolExecutor
│       │   └── corrigir_orchestrator.py     # loop + guardrail
│       └── prompts/                         # templates jinja2 para fixers LLM
│           ├── base.j2
│           ├── pseudossintese.j2
│           ├── topico_numerado.j2
│           └── abertura_laconica.j2
├── tests/
│   ├── conftest.py                          # fixtures: paragrafos de teste, violacoes mock
│   ├── unit/
│   │   ├── test_parser_md.py
│   │   ├── test_parser_tex.py
│   │   ├── test_patch_aplicador.py
│   │   ├── validadores/
│   │   │   ├── test_termos_lexicais.py      # input controlado → Violacao esperada
│   │   │   ├── test_construcoes.py
│   │   │   ├── test_coocorrencia.py
│   │   │   └── ...
│   │   └── fixers/
│   │       ├── test_cst012_fixer.py
│   │       └── ...
│   └── integration/
│       └── test_piloto_eolica.py            # roda contra artigo.md real
└── pyproject.toml
```

### Structure Rationale

- **`src/` layout:** isolamento de importação; `uv` suporta editable install (`pip install -e .`); `pytest` com `pythonpath = ["src"]` no pyproject.
- **`core/`:** tudo que não tem dependência de regra. `modelos.py` é importado por todo o resto — zero imports circulares possíveis (regra: `modelos.py` não importa nada de dentro do pacote).
- **`base/`:** ABCs separadas de `core/` para que validadores e fixers importem apenas o contrato, não a implementação do parser.
- **`validadores/primitivos/`:** 1 arquivo por JSON. Benefício: `pytest -k termos_lexicais` testa exatamente 1 arquivo de regras, falha isolada.
- **`validadores/agregadores/`:** separados dos primitivos para deixar explícito que dependem da saída acumulada dos primitivos (dependência de dado, não de módulo).
- **`validadores/estruturais/`:** separados porque dependem de `TipoSecao` (INTRODUCAO, CONCLUSAO...) — precisam de `Paragrafo.tipo_secao` que os primitivos não exigem.
- **`fixers/llm/claude_client.py`:** isolado em módulo próprio para que os testes de fixers LLM possam mockar apenas o cliente, não o SDK inteiro.
- **`prompts/`:** arquivos `.j2` fora do código Python; substituíveis sem tocar no código; testáveis com `jinja2.Environment` apontando para o diretório.

---

## Architectural Patterns

### Pattern 1: Registry Manual (não entry points)

**O que:** Cada validador registra-se num dicionário central `VALIDADORES: dict[str, type[ValidadorBase]]` em `validadores/__init__.py`. O orchestrator instancia apenas os validadores necessários por nome.

**Por que não entry points (`pyproject.toml [project.entry-points]`):** Entry points são o padrão de plugin para pacotes de terceiros instalados em ambientes diferentes. Este sistema é um pacote fechado, monorepo dentro de `biblioteca_canonica/`. Não há cenário de "instalar validador de terceiro em runtime". Entry points adicionariam complexidade de `importlib.metadata.entry_points()` sem benefício real. Registry manual tem zero overhead de descoberta e é trivialmente testável (`assert "cst_012" in VALIDADORES`).

**Quando usar entry points:** apenas se no futuro existir a necessidade de usuários externos adicionarem validadores sem fork do repositório — improvável dado o escopo pessoal.

```python
# validadores/__init__.py
from validador_academico.validadores.primitivos.termos_lexicais import (
    TermosLexicaisValidador,
)
from validador_academico.validadores.primitivos.construcoes import (
    ConstrucoesValidador,
)
# ... demais imports

VALIDADORES_PRIMITIVOS: dict[str, type[ValidadorBase]] = {
    "termos_lexicais": TermosLexicaisValidador,
    "expressoes_conectivas": ExpressoesConectivasValidador,
    "colocacoes": ColocacoesValidador,
    "construcoes": ConstrucoesValidador,
    "sinais": SinaisValidador,
    "conjuncoes": ConjuncoesValidador,
}

VALIDADORES_AGREGADORES: dict[str, type[ValidadorBase]] = {
    "coocorrencia": CoocorrenciaValidador,
    "escrita_canonica": EscritaCanonica Validador,
}

VALIDADORES_ESTRUTURAIS: dict[str, type[ValidadorBase]] = {
    "titulos": TitulosValidador,
    # ...
}
```

### Pattern 2: Topological Dispatch no Orchestrator

**O que:** O `ValidarOrchestrator` executa validadores em três ondas fixas com barreira entre elas. Dentro de cada onda, `ThreadPoolExecutor` para paralelismo.

**Ondas fixas:**
1. Primitivos — sem dependência entre si, paralelos
2. Agregadores — aguardam `Violacao[]` acumuladas dos primitivos
3. Estruturais — aguardam resultado completo (podem usar `Violacao[]` para enriquecer output)

**Por que ThreadPoolExecutor e não asyncio:** os validadores são CPU-bound (regex), não I/O-bound. Asyncio não traz ganho para operações CPU-bound dentro do GIL Python. `ThreadPoolExecutor` com `max_workers=len(primitivos)` é suficiente para artigos de 30k palavras em < 5 segundos (cada worker roda 1 JSON de regras, ~14 entradas com regex precompilados). Asyncio seria justificado apenas se os validadores fizessem I/O (ex.: consulta a API externa) — o que é explicitamente proibido em PROJECT.md.

```python
# orchestrator/validar_orchestrator.py
from concurrent.futures import ThreadPoolExecutor, as_completed

class ValidarOrchestrator:
    def validar(
        self,
        paragrafos: list[Paragrafo],
        grupos: GruposValidadores,
    ) -> list[Violacao]:
        violacoes: list[Violacao] = []

        # Onda 1: primitivos em paralelo
        with ThreadPoolExecutor(
            max_workers=len(grupos.primitivos)
        ) as executor:
            futuros = {
                executor.submit(v.validar, paragrafos): nome
                for nome, v in grupos.primitivos.items()
            }
            for futuro in as_completed(futuros):
                violacoes.extend(futuro.result())

        # Onda 2: agregadores recebem violacoes acumuladas
        for validador in grupos.agregadores.values():
            violacoes.extend(validador.validar_agregado(paragrafos, violacoes))

        # Onda 3: estruturais (opcionais, ativados com --estrutural)
        if grupos.estruturais:
            for validador in grupos.estruturais.values():
                violacoes.extend(validador.validar(paragrafos))

        return sorted(violacoes, key=lambda v: (v.linha, v.col))
```

**Nota crítica:** `CoocorrenciaValidador` recebe `Violacao[]` já acumuladas, não refaz regex. O método tem assinatura diferente do `ValidadorBase`: `validar_agregado(paragrafos, violacoes_anteriores)`. Isso é intencional: ele é um validador de segundo nível que opera sobre resultado de outros, não sobre texto bruto.

### Pattern 3: Dependency Injection para ClaudeClient

**O que:** `ClaudeClient` é instanciado fora dos fixers e injetado via construtor. Fixers LLM recebem o cliente como parâmetro, nunca o instanciam internamente.

**Por que:** permite substituir por mock em testes sem monkeypatching. Fixers LLM são testáveis com `FakeClaudeClient` que retorna respostas fixas.

```python
# fixers/llm/claude_client.py
from anthropic import Anthropic

class ClaudeClient:
    def __init__(
        self,
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 1024,
    ) -> None:
        self._client = Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def completar(self, prompt: str) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

# fixers/llm/pseudossintese_fixer.py
class PseudossinteseFixer(FixerBase):
    def __init__(self, cliente: ClaudeClient) -> None:
        self._cliente = cliente
        # jinja2 carrega prompt de prompts/pseudossintese.j2

# em tests/unit/fixers/test_pseudossintese_fixer.py:
# fixer = PseudossinteseFixer(cliente=FakeClaudeClient(...))
```

### Pattern 4: Patches em Ordem Reversa

**O que:** `PatchAplicador` ordena patches por `(linha, col_inicio)` decrescente antes de aplicar. Garante que aplicar patch na linha 50 não altera offsets de patch na linha 30.

**Por que é crítico:** qualquer fixer que altera o comprimento do texto (ex.: remove "a descoberta específica de X reside em" e substitui por "X") muda os offsets das posições subsequentes no mesmo arquivo. Aplicar na ordem inversa garante que cada patch opera sobre o estado pré-modificado do trecho correto.

```python
# core/patch_aplicador.py
def aplicar(linhas: list[str], patches: list[Patch]) -> list[str]:
    ordenados = sorted(
        patches,
        key=lambda p: (p.linha, p.col_inicio),
        reverse=True,   # ordem reversa: linha maior primeiro
    )
    for patch in ordenados:
        idx = patch.linha - 1  # 1-based -> 0-based
        linha = linhas[idx]
        linhas[idx] = (
            linha[:patch.col_inicio]
            + patch.depois
            + linha[patch.col_fim:]
        )
    return linhas
```

### Pattern 5: Contexto de Parágrafo como Unidade de Processamento

**O que:** O parser não emite linhas individuais para os validadores. Emite `Paragrafo` — unidade semântica que contém texto completo do bloco, lista de frases, offsets de linha de início e fim, e `tipo_secao` (quando identificável).

**Por que:** validadores primitivos precisam apenas do texto do parágrafo para regex. `CoocorrenciaValidador` precisa saber quais `ids` de violação estão no **mesmo parágrafo** (escopo do JSON é `"paragrafo"`). Sem encapsular o parágrafo, o orchestrator teria que implementar groupby de violações por linha, reconstruindo a segmentação que o parser já fez.

```python
# core/modelos.py
from dataclasses import dataclass, field
from enum import Enum

class TipoSecao(str, Enum):
    CORPO = "CORPO"
    INTRODUCAO = "INTRODUCAO"
    CONCLUSAO = "CONCLUSAO"
    RESUMO = "RESUMO"
    REFERENCIAS = "REFERENCIAS"
    NOTA_RODAPE = "NOTA_RODAPE"
    TITULO = "TITULO"
    AUTOR = "AUTOR"
    DESCONHECIDO = "DESCONHECIDO"

@dataclass(slots=True)
class Paragrafo:
    texto: str           # texto completo do bloco (sem markup MD/LaTeX)
    linha_inicio: int    # 1-based, compativel com token.map[0] do markdown-it-py
    linha_fim: int       # 1-based
    tipo_secao: TipoSecao = TipoSecao.CORPO
    frases: list[str] = field(default_factory=list)
    # frases usadas por validadores que precisam de periodo como unidade (p_02)
```

---

## Data Flow

### Fluxo Completo: Validação

```
artigo.md / artigo.tex
        |
        v
  [ParserMd / ParserTex]
        |  markdown-it-py tokens (map=[start, end])
        |  pylatexenc nodes (pos, len, pos_to_lineno_colno)
        v
  list[Paragrafo]
  (texto, linha_inicio, linha_fim, tipo_secao, frases)
        |
        |──────────────────────────────────────────┐
        v                                          v
  [ThreadPoolExecutor]                    (aguarda Onda 1)
  Primitivos em paralelo:                         |
  TLexical  TConectiva  TCst  TSinal  TConj       |
        |                                          |
        v                                          |
  list[Violacao][] (por validador)                 |
        |                                          |
        v                                          v
  [merge + sort por (linha, col)]       [CoocorrenciaValidador]
        |                               recebe Violacao[] acumuladas
        |                               calcula penalidade por parágrafo
        |                               aplica multiplicadores
        |                               emite novas Violacao[] VERMELHO_FORTE
        |<──────────────────────────────────────────┘
        |
        v
  [EscritaCanonica Validador]
  mapeia cst_XXX → p_YY
  enriquece Violacao.principio_canonico
        |
        v
  list[Violacao] final (ordenada por severidade + linha)
        |
        v
  [ReportGenerator]
  ├── AUDITORIA.md (Rich — tabela + painéis por severidade)
  └── violacoes.json (schema estruturado, --output json)
```

### Fluxo Completo: Correção

```
list[Violacao] (saída da validação)
        |
        v
  [CorrigirOrchestrator]
  para cada Violacao (por severidade, mais grave primeiro):
        |
        |── AUTO?  ──> [Fixer AUTO]  ──> list[Patch] (confianca=1.0)
        |── ASSISTIDO? > [Fixer ASSISTIDO] > propõe N opções > autor seleciona
        |── LLM?   ──> [Fixer LLM]  ──> [ClaudeClient] ──> list[Patch]
        |
        v
  list[Patch] acumulados
        |
        v
  [PatchAplicador] (ordem reversa: linha/col decrescente)
        |
        v
  artigo_corrigido.md (arquivo modificado in-place ou --output novo_arquivo)
        |
        v
  [ValidarOrchestrator] (revalidação automática)
        |
        v
  list[Violacao] residuais
        |
  guardrail: se len(residuais) >= len(anteriores), PARAR (fix não convergiu)
  guardrail: se iteracao >= MAX_ITER (default=3), PARAR com aviso
        |
        v
  AUDITORIA_pos_fix.md (relatório final com violações residuais)
```

### Fluxo de Dados de Regra (carregamento)

```
biblioteca_canonica/02_escrita/termos_proibidos/01_termos_lexicais_proibidos.json
        |
        v
  [ValidadorBase.carregar_json()]  (chamado 1x na inicialização, não por parágrafo)
        |  json.load() + re.compile() de cada regex
        v
  list[RegexCompilado]  (em memória, reutilizado para todos os parágrafos)
        |
        v  para cada Paragrafo:
  re.finditer(regex, paragrafo.texto)
        |
        v
  Violacao(arquivo, linha, col, regra_id, severidade, trecho_original, sugestoes)
```

**Nota de performance:** cada validador compila seus regex UMA vez no `__init__`. Para um artigo de 30k palavras (~300 parágrafos), cada primitivo executa `N_regras * 300` operações de `finditer`. Com 6 primitivos e ~40 regras totais, isso é ~12.000 operações de regex precompilado — bem dentro do limite de 5 segundos.

---

## Build Order (Dependências entre Milestones)

```
M1 — Piloto cst_012 ponta-a-ponta
 ├── core/modelos.py          (Violacao, Patch, Paragrafo, TipoSecao)
 ├── core/parser_md.py        (só .md; .tex adiado para M2)
 ├── base/validador_base.py   (ABC)
 ├── base/fixer_base.py       (ABC)
 ├── validadores/primitivos/construcoes.py  (só cst_012 inicialmente)
 ├── fixers/auto/cst012_fixer.py
 ├── core/patch_aplicador.py
 ├── core/report_generator.py (AUDITORIA.md básico)
 └── cli.py                   (comando `validar` mínimo)
      |
      | BLOQUEIO: M2 depende de M1 estável com testes passando
      v
M2 — Primitivos completos (paralelos)
 ├── validadores/primitivos/termos_lexicais.py
 ├── validadores/primitivos/expressoes_conectivas.py
 ├── validadores/primitivos/colocacoes.py
 ├── validadores/primitivos/construcoes.py   (completar além do cst_012)
 ├── validadores/primitivos/sinais.py
 ├── validadores/primitivos/conjuncoes.py    (802 entradas — mais trabalhoso)
 ├── orchestrator/validar_orchestrator.py    (ThreadPoolExecutor Onda 1)
 └── core/parser_tex.py                      (pylatexenc)
      |
      | BLOQUEIO: M3 depende de Violacao[] dos primitivos M2
      v
M3 — Agregadores
 ├── validadores/agregadores/coocorrencia.py   (consome Violacao[] dos primitivos)
 └── validadores/agregadores/escrita_canonica.py  (enriquece principio_canonico)
      |
      | SEMI-BLOQUEIO: M4 pode ser desenvolvido em paralelo com M3
      |   mas depende de parser com tipo_secao (extensão do M1/M2)
      v
M4 — Estruturais (1 por componente ABNT)
 ├── extensão do parser_md: detecção de TipoSecao por heading Markdown
 ├── validadores/estruturais/introducao.py   (proibição de citações)
 ├── validadores/estruturais/conclusao.py    (proibição de citações novas)
 ├── validadores/estruturais/resumo.py       (max 150 palavras, 5 kw)
 └── ... (demais 8 estruturais)
      |
      | BLOQUEIO: M5 depende de Violacao[] de M2 (e opcionalmente M3/M4)
      v
M5 — Fixers AUTO
 ├── fixers/auto/termos_lexicais_fixer.py
 ├── fixers/auto/expressoes_conectivas_fixer.py
 ├── fixers/auto/sinais_fixer.py
 └── (refatorar cst012_fixer.py do M1 para este diretório)
      |
      | SEMI-BLOQUEIO: M6 reutiliza infra de Patch do M5
      v
M6 — Fixers ASSISTIDO
 ├── fixers/assistido/dois_pontos_fixer.py
 ├── fixers/assistido/gerundio_fixer.py
 └── fixers/assistido/omissao_det_fixer.py
      |
      | BLOQUEIO: M7 depende de ClaudeClient + jinja2 (dependência de rede)
      v
M7 — Fixers LLM
 ├── fixers/llm/claude_client.py
 ├── prompts/*.j2
 ├── fixers/llm/pseudossintese_fixer.py    (cst_008)
 ├── fixers/llm/topico_numerado_fixer.py   (cst_010)
 └── fixers/llm/abertura_laconica_fixer.py (cst_007)
      |
      | SEMI-BLOQUEIO: M8 depende de CLI estável (M1) e todos validadores
      v
M8 — Orchestrator completo + integração
 ├── orchestrator/corrigir_orchestrator.py  (loop + guardrail)
 ├── cli.py                                 (comandos `corrigir` e `auditar`)
 ├── testes de integração contra artigo.md real
 ├── .pre-commit-hooks.yaml
 └── hooks em build.sh LaTeX / criar_template.py GDocs
```

**Dependências reais (não apenas convencionais):**

| Milestone | Bloqueador real | Motivo |
|-----------|----------------|--------|
| M3 Agregadores | M2 Primitivos completos | `CoocorrenciaValidador` recebe `list[Violacao]` com `regra_id` dos primitivos; sem eles, não há coocorrência para calcular |
| M4 Estruturais | Parser com `tipo_secao` | Requer identificação de seção por heading Markdown — extensão não-trivial do parser básico do M1 |
| M5 Fixers AUTO | M2 Primitivos | Cada fixer AUTO corresponde a um validador primitivo; sem o validador testado, o fixer não tem `Violacao` canônicas para consumir |
| M7 Fixers LLM | M6 ASSISTIDO | Não técnico: M6 valida a infra de Patch antes de gastar custo de API em M7 |
| M8 Integração | CLI M1 estável | hooks precisam de exit code confiável; corrigir_orchestrator precisa de todos fixers |

**Paralelismo possível no desenvolvimento:**

- M4 pode ser desenvolvido em paralelo com M3 (dependem do mesmo parser, mas não entre si)
- M5 e M6 podem ser intercalados (um fixer AUTO + fixer ASSISTIDO por construção em vez de todos AUTO depois todos ASSISTIDO)
- M7 pode começar com `ClaudeClient` isolado enquanto M6 ainda está em desenvolvimento

---

## Integration Points

### Externos

| Serviço | Padrão de Integração | Notas |
|---------|---------------------|-------|
| Claude API | `ClaudeClient` com `anthropic` SDK síncrono; injetado via DI nos fixers LLM | Somente em fixers LLM (M7); validadores nunca chamam rede. `ANTHROPIC_API_KEY` via variável de ambiente |
| Pre-commit framework | `.pre-commit-hooks.yaml` na raiz de `biblioteca_canonica/`; hook chama `validar {file}` | Exit code 1 se ERRO detectado; configurável com `--nivel alerta` para bloquear só erros críticos |
| LaTeX build.sh | Chamada ao CLI antes de `pdflatex`: `validar artigo.tex || exit 1` | Modo CI (não-interativo): sem prompts de ASSISTIDO |
| GDocs criar_template.py | Chamada ao CLI antes de render: `validar artigo.md || raise` | Mesma lógica de exit code |

### Internos (fronteiras entre módulos)

| Fronteira | Comunicação | Invariante |
|-----------|------------|-----------|
| Parser → Validador | `list[Paragrafo]` (imutável após criação) | Parser nunca modifica texto; validadores leem apenas |
| Validador → Orchestrator | `list[Violacao]` (dataclass frozen) | Violações são imutáveis; orchestrator agrega, não edita |
| Orchestrator → Fixer | `Violacao` individual | Fixer recebe 1 violação, retorna `list[Patch]` |
| Fixer → PatchAplicador | `list[Patch]` (acumulados de todos os fixers) | Aplicador não sabe origem dos patches; ordena e aplica |
| PatchAplicador → arquivo | `list[str]` (linhas modificadas) | Arquivo original preservado até confirmação explícita |
| ValidadorBase → JSON | `pathlib.Path` resolvida na inicialização | JSON carregado 1x; regex compilado 1x; stateless após |
| ClaudeClient → Fixer LLM | Interface `completar(prompt: str) -> str` | Fixer não conhece modelo; parâmetros de modelo ficam no cliente |

---

## Anti-Patterns

### Anti-Pattern 1: Monolito de Validação

**O que se faz:** um único arquivo `validador.py` com todos os regex de todos os JSONs e toda a lógica de aplicação.

**Por que é errado:** impossível testar uma regra isolada; uma mudança em `cst_012` pode quebrar `cst_001`; adicionar novo JSON exige editar o monolito; não permite paralelização por regra.

**Em vez disso:** 1 arquivo por JSON, 1 classe por arquivo, cada uma com seus próprios testes unitários.

### Anti-Pattern 2: Reexecutar Regex no Agregador de Coocorrência

**O que se faz:** `CoocorrenciaValidador` roda seus próprios `re.finditer` sobre o texto para verificar se `cst_007` está presente, em vez de consumir o `list[Violacao]` já produzido pelos primitivos.

**Por que é errado:** duplicação de custo computacional; inconsistência possível se o regex do primitivo tiver exclusões (`cst_004.exclusoes`) que o agregador não reimplementa corretamente; viola o design de "agregadores consomem saída dos primitivos".

**Em vez disso:** `CoocorrenciaValidador.validar_agregado(paragrafos, violacoes)` recebe `violacoes` e filtra por `regra_id` e `paragrafo` (usando `linha_inicio`/`linha_fim`). Zero regex no agregador.

### Anti-Pattern 3: Estado Global de Validação

**O que se faz:** usar variável de módulo ou singleton para acumular violações entre chamadas (`VIOLACOES_GLOBAIS = []`).

**Por que é errado:** não-testável (estado vaza entre testes); não-threadsafe (ThreadPoolExecutor com workers simultâneos podem corromper a lista); comportamento não-determinístico em execuções subsequentes.

**Em vez disso:** cada chamada a `validador.validar(paragrafos)` retorna nova `list[Violacao]`. O orchestrator acumula; os validadores são stateless após `__init__`.

### Anti-Pattern 4: Fixer que Chama Validador Internamente

**O que se faz:** `Cst012Fixer.fixar(violacao)` instancia `ConstrucoesValidador` internamente para "confirmar" que a violação ainda existe antes de aplicar o patch.

**Por que é errado:** acopla fixer a validador; duplica lógica de validação; o loop validar→fixar→revalidar do `CorrigirOrchestrator` já trata o caso de violação resolvida por outro patch anterior.

**Em vez disso:** fixer recebe `Violacao` com `trecho_original` preenchido pelo validador. Usa `trecho_original` para construir o regex de substituição do patch. O orchestrator revalida após aplicação.

### Anti-Pattern 5: ThreadPoolExecutor para Agregadores

**O que se faz:** executar `CoocorrenciaValidador` em paralelo com os primitivos para economizar tempo.

**Por que é errado:** `CoocorrenciaValidador` precisa da saída **completa** dos primitivos antes de calcular coocorrências. Executá-lo em paralelo com primitivos significa que ele operaria sobre `list[Violacao]` incompleta. A penalidade de multiplicador 5.0 do `coc_007` exige que todos os `ids` candidatos (`cst_010`, `cst_007`, `cst_011`, `cst_012`, `lex_010`, `lex_013`) já estejam detectados.

**Em vez disso:** barreira explícita entre Onda 1 (primitivos) e Onda 2 (agregadores). Executor finaliza completamente antes do início dos agregadores.

---

## Scaling Considerations

Este é um CLI local, single-user. "Escala" aqui significa tamanho de artigo, não usuários concorrentes.

| Escopo | Estimativa | Estratégia |
|--------|-----------|-----------|
| Artigo padrão (15-30k palavras) | ~300 parágrafos, ~40 regras, ~12.000 operações regex | ThreadPoolExecutor 6 workers; regex precompilados na init; meta < 5s |
| Tese completa (80-100k palavras) | ~1.000 parágrafos | Mesma arquitetura; se > 10s, adicionar cache de hash por parágrafo para revalidação incremental |
| Múltiplos artigos simultâneos | Improvável no escopo | CLI stateless; se necessário, invocar processo filho por artigo |

**Cache:** PROJECT.md define "Sem cache stateful: cada execução parte do zero, output determinístico". Não implementar cache em M1-M8. Se artigo de tese (100k palavras) exceder 5s, avaliar cache de hash de parágrafo como extensão pós-M8.

---

## Sources

- PROJECT.md lido diretamente: `/home/kalyllamarck/projetos/Doutorado/biblioteca_canonica/.planning/PROJECT.md`
- `06_regras_coocorrencia.json` lido diretamente: escopo por parágrafo, dependência de saída dos primitivos, multiplicadores e thresholds
- `escrita_canonica.json` lido diretamente: mapeamento `cst_XXX → p_YY`, tensões resolvidas, `interacao_com_validador`
- `04_construcoes_sintaticas_proibidas.json` lido parcialmente: schema de `regex_deteccao`, `exclusoes`, `alternativas`
- STACK.md da pesquisa: decisões de `ThreadPoolExecutor vs asyncio`, `frozen=True em Violacao`, modelagem de Patch
- FEATURES.md da pesquisa: feature dependencies map, notas sobre dependência do agregador de coocorrência
- Python `concurrent.futures` docs: `ThreadPoolExecutor`, `as_completed` — padrão para CPU-bound paralelo
- Python `dataclasses` docs: `frozen=True`, `slots=True` — imutabilidade e performance
- Vale architecture (comparativo): https://vale.sh/docs/ — plugin discovery via config YAML vs registry manual

---

*Architecture research for: Validador & Fixer Acadêmico — CLI Python modular*
*Researched: 2026-05-04*
