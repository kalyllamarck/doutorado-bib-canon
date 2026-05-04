# Pitfalls Research

**Domain:** CLI Python — linter de prosa acadêmica PT-BR + auto-fix com regras em JSON
**Researched:** 2026-05-04
**Confidence:** HIGH — pitfalls derivados da leitura direta dos JSONs canônicos, do PROJECT.md,
e de análise de sistemas análogos (Vale, ESLint, proselint, regex engines). Confirmação
via análise da cst_004 (campo `exclusoes`) e coc_007 (multiplicador 5.0) já existentes.

---

## Pitfalls Críticos

### Pitfall 1: Regex de Gerúndio Captura Palavras Não-Verbais

**O que dá errado:**
O regex de cst_004 (`\b[a-zà-ÿ]{3,}(ando|endo|indo)\b`) captura "quando", "grande",
"calendo", "lenda", "senda", "vendo" e qualquer substantivo ou adjetivo com essas
terminações. O campo `exclusoes` no JSON já lista 9 palavras, mas o corpus PT-BR tem
centenas de casos não listados: "Fernando", "Orlando", "fundo", "sendo" (particípio de
ser, não gerúndio), "tendo" (= possuindo, mas também auxiliar em "tendo em vista"),
"fazendo" (gerúndio legítimo a suprimir) vs. "fazendo" em título de seção entre aspas.

**Por que acontece:**
Regex posicional sem contexto morfológico. PT-BR tem grande número de palavras com
sufixos -ando/-endo/-indo que não são formas verbais. A lista de exclusões no JSON
é finita e foi construída ad-hoc. Cada novo artigo pode revelar novos falsos positivos
não cobertos.

**Como evitar:**
1. Implementar o campo `exclusoes` do JSON como `re.compile(r'\b(' + '|'.join(exclusoes) + r')\b', re.IGNORECASE)` e filtrar matches antes de emitir Violacao.
2. Para cst_004 especificamente, o validador NUNCA deve ser AUTO: forçar nível ASSISTIDO no código, independente do que o orchestrator decida. A `observacao` do JSON já indica "Exige revisão humana."
3. Expandir `exclusoes` progressivamente a cada artigo novo: quando o autor rejeita um patch de cst_004, o ID da palavra rejeitada entra na lista de exclusões do JSON automaticamente (aprendizado incremental sem code change).
4. Testar cst_004 com corpus mínimo de palavras não-verbais em -ando/-endo/-indo coletadas do artigo Eólica Nordeste (ex.: "quando", "grande", "tendo em vista", "Orlando", "demandando" vs. "demanda").

**Sinais de alerta:**
- Mais de 30% dos matches de cst_004 sendo rejeitados pelo autor na fase de revisão assistida.
- Relatório lista a mesma palavra 5+ vezes e ela é claramente um substantivo.
- Testes unitários com corpus limpo retornam violações.

**Phase a tratar:** M2 (implementação do validador cst_004). Nunca presumir que lista de exclusões do JSON é completa. Tratar como dado vivo.

**Severidade:** ALTA — falso positivo de gerúndio em nome próprio no artigo gera relatório de auditoria inútil e destrói a confiança do autor no sistema inteiro.

---

### Pitfall 2: Drift de Offsets ao Aplicar Patches que Alteram Comprimento

**O que dá errado:**
Um artigo de 30k palavras pode ter 40 violações. Se os patches forem aplicados em ordem
de linha crescente (de cima para baixo), cada substituição que insere ou remove caracteres
invalida os offsets de todas as violações abaixo dela. O fixer aplica "reside em" no
lugar de "a tese central de X (2020) reside em" — reduz 28 chars — e o próximo patch
(que apontava para col 45 na linha seguinte ao parágrafo deslocado) aponta agora para
posição errada.

**Por que acontece:**
Offsets são capturados no momento da validação sobre o texto original. A aplicação
sequencial de patches cria um gap entre coordenadas capturadas e posição real após
modificações anteriores. O PROJECT.md já prevê "aplicar patches em ordem reversa"
(REQ-CORE-06), mas a implementação pode falhar em casos menos óbvios:
- Patches em linhas diferentes do mesmo parágrafo (linha N e linha N+2 dentro do mesmo bloco).
- Fixer LLM que reescreve um parágrafo inteiro (de 4 linhas para 2 linhas) e reduz o número de linhas do arquivo.
- Patches em notas de rodapé que alteram numeração das linhas do corpo do texto.

**Como evitar:**
1. Implementar patch reverso por posição de byte no arquivo inteiro (não por linha+col separados): converter (linha, col) em offset de byte absoluto no momento da captura, aplicar em ordem decrescente de offset absoluto.
2. Aplicar patches em lote por parágrafo: se um fixer LLM reescreve o parágrafo, invalidar e descartar todos os outros patches do mesmo parágrafo antes de aplicar.
3. Revalidar o arquivo inteiro após cada lote de patches de um parágrafo (não após cada patch individual — custo alto — mas após fechar o lote do parágrafo).
4. Escrever teste unitário específico: dois patches no mesmo parágrafo, o primeiro reduz 10 chars, verificar que o segundo ainda aponta para posição correta.

**Sinais de alerta:**
- Fixer substitui texto em posição errada (ex.: sobrescreve meio de uma palavra).
- Após aplicar fix, o arquivo fica com caracteres repetidos ou deletados em excesso.
- Testes de integração (fixar artigo Eólica, re-validar) mostram violações em posições que não existiam no original.

**Phase a tratar:** M1 (REQ-CORE-06 patch em ordem reversa). Esse é o risco arquitetural mais alto do sistema inteiro. Deve ter testes de regressão antes de qualquer fixer ser ativado.

**Severidade:** ALTA — corrompe o arquivo `.md` do artigo, que é o único input do pipeline LaTeX. Corrupção silenciosa (sem mensagem de erro) é o pior caso.

---

### Pitfall 3: Loop Infinito no Ciclo Validar→Fixar→Revalidar

**O que dá errado:**
O fixer AUTO de cst_001 (dois-pontos) substitui ":" por um ponto. O texto resultante
cria uma nova construção que ativa cst_003 (oração intercalada). O orchestrator detecta
a nova violação e tenta fixar cst_003. A correção de cst_003 reintroduz o dois-pontos.
Loop infinito, ou loop com 50 iterações até guardrail explodido.

Variante mais sutil: o fixer LLM de cst_008 (pseudossíntese conciliatória) reescreve
o parágrafo usando "articular" (lex_008) que estava ausente no original. lex_008 dispara
coc_001 junto com cst_004 latente. Duas violações novas, nenhuma existia antes.

**Por que acontece:**
Fixers operam localmente (sobre a violação capturada) sem visibilidade do efeito no
parágrafo inteiro. Fixers LLM são especialmente perigosos porque o LLM não tem os JSONs
de termos proibidos memorizados com fidelidade — ele "sabe" as regras do prompt, mas
produz texto com termos que nunca viu na lista negra.

**Como evitar:**
1. Guardrail por parágrafo: `MAX_ITERACOES_POR_PARAGRAFO = 3`. Se após 3 ciclos o parágrafo ainda tem violações, emitir `FLAG_REVISAO_HUMANA` e parar (não continuar tentando).
2. Guardrail por sessão: `MAX_PATCHES_TOTAIS = 100`. Se o orchestrator aplicou 100 patches numa sessão, parar e reportar ao autor.
3. Para fixers LLM: injetar TODOS os JSONs de termos_proibidos no prompt (não apenas a regra que disparou o fix). O prompt deve conter: "As seguintes palavras e construções são proibidas: [lista completa extraída dos JSONs]. Nunca use nenhuma delas na reescrita."
4. Revalidar o parágrafo inteiro (não só a violação corrigida) antes de declarar o patch como aceito.
5. Detectar ciclo: se o conjunto de violações ativas num parágrafo for idêntico ao da iteração anterior (mesmos ids), declarar empate e escalar para REVISAO_HUMANA.

**Sinais de alerta:**
- Orchestrator roda por mais de 30 segundos num artigo de 30k palavras (validação pura deve ser < 5s; loops aumentam o tempo desproporcionalmente).
- Log mostra o mesmo parágrafo sendo processado 3+ vezes.
- Relatório final lista violações ativas em parágrafos marcados como "corrigidos".

**Phase a tratar:** M8 (REQ-ORC-02 orchestrator fixer com guardrail). O guardrail deve ser implementado antes de qualquer fixer LLM ser ativado em M7.

**Severidade:** ALTA — sem guardrail, uma sessão pode rodar indefinidamente, consumir créditos da Claude API e deixar o arquivo em estado indeterminado.

---

### Pitfall 4: Fixer LLM Introduz Violações Novas (Risco de Contaminação)

**O que dá errado:**
O fixer LLM recebe o parágrafo com cst_008 (pseudossíntese conciliatória) e reescreve
corretamente, eliminando a metáfora geométrica vazia. Mas a reescrita usa "além disso"
(con_002, expressão conectiva proibida), "articula" (lex_008), "significativo" (lex_002)
e abre com gerúndio ("Considerando que..."). Quatro violações novas foram introduzidas
onde havia uma.

**Por que acontece:**
O LLM gera texto fluente segundo seu treinamento — que inclui prosa acadêmica com
exatamente os padrões que este sistema proíbe. O prompt injeta as regras, mas o modelo
distribui probabilidade sobre todo o vocabulário de treino. Termos de alta frequência em
prosa acadêmica (exatamente os que estão na lista negra) têm peso alto no distribuição.

**Como evitar:**
1. Pós-validação obrigatória de toda saída LLM antes de aceitar o patch: rodar todos os validadores primitivos (M2) sobre o texto proposto pelo LLM. Se houver qualquer nova violação, rejeitar o patch automaticamente e tentar de novo (até MAX_TENTATIVAS_LLM = 2).
2. Injetar lista negra completa no prompt jinja2 (ver Pitfall 3). Isso reduz (mas não elimina) a probabilidade de termos proibidos na saída.
3. Temperatura zero ou temperatura muito baixa (0.1) para fixers LLM: reduz variabilidade e mantém a saída mais próxima do exemplo `reescrito` do JSON da regra.
4. O prompt deve incluir o `exemplo_reescrito` do JSON correspondente como few-shot: "Exemplo de correção aceitável: [exemplo_reescrito do cst_008]."
5. Após MAX_TENTATIVAS_LLM tentativas fracassadas, escalar para ASSISTIDO (mostrar ao autor as tentativas e a violação original, deixar o autor decidir).

**Sinais de alerta:**
- Relatório de pós-validação da saída LLM mostra violações em parágrafos que o LLM acabou de "corrigir".
- Custo da API aumenta desproporcionalmente (reruns por rejeição de saída contaminada).
- O autor aceita o patch e, na próxima rodada de validação, o mesmo parágrafo volta com violações diferentes.

**Phase a tratar:** M7 (Fixers LLM). Deve ter suite de testes específica: para cada cst que tem fixer LLM, criar corpus de parágrafos-teste e verificar que a saída do LLM passa a validação M2 completa.

**Severidade:** ALTA — é o único pitfall que pode degradar a qualidade do texto em vez de melhorá-la, contrariando o propósito do sistema.

---

### Pitfall 5: Unicode PT-BR — Quebra de Word Boundary com Acentos

**O que dá errado:**
`re.compile(r'\bsignificativo\b')` não captura "significativo" no início de uma linha
após um travessão (`—significativo`), porque `—` (U+2014) não é `\W` em todas as
implementações. Mais crítico: `r'\b[a-zà-ÿ]{3,}(ando|endo|indo)\b'` no cst_004 pode
falhar em palavras com acento antes do sufixo (ex.: "sendo" vs. "péssendo" hipotético).
O range `à-ÿ` cobre U+00E0–U+00FF, que inclui "ÿ" mas exclui caracteres fora desse
bloco Unicode (ex.: alguns caracteres usados por pandoc em output intermediário).

**Por que acontece:**
`re.UNICODE` é default em Python 3, mas `\b` trata como "fronteira de palavra" a
transição entre `\w` e `\W`. `\w` em Python 3 com UNICODE cobre letras, dígitos e
underscore Unicode — mas `à-ÿ` como range de caractere numa classe `[...]` é interpretado
literalmente como "qualquer caractere com codepoint entre 0xE0 e 0xFF", não como "qualquer
letra acentuada". Isso é correto para PT-BR básico, mas pode criar gaps para:
- Caracteres compostos (ex.: "ã" como U+00E3 está dentro do range, OK; mas "a" + combining tilde U+0303 não está).
- Travessão tipográfico (U+2014) embutido por pandoc no texto.
- Aspas tipográficas ("texto") que afetam o contexto de `\b`.

**Como evitar:**
1. Validar empiricamente cada regex dos JSONs contra o artigo Eólica Nordeste antes de declarar M2 pronto. O artigo é o ground truth — se o regex não detecta uma violação conhecida (ex.: "significativo" que está no artigo), há bug de regex, não de regra.
2. Normalizar o texto de entrada: `unicodedata.normalize('NFC', texto)` antes de aplicar qualquer regex. Isso converte compostos para forma precomposta, eliminando o problema de "a" + combining tilde.
3. Pré-processar travessões e aspas tipográficas: substituir `—` (U+2014) por ` — ` (com espaços) antes de rodar validadores, para que `\b` funcione corretamente no limite da palavra.
4. Testes unitários de regex devem incluir strings com acentos precompostos E compostos para cada cst/lex com range `à-ÿ`.

**Sinais de alerta:**
- Um termo proibido conhecido no artigo (ex.: "consolidar") não é detectado pelo validador.
- Regex de cst_003 (`^[A-ZÀ-Ý]`) não captura linha que começa com "Ê" (U+00CA, dentro do range, mas verificar).
- Testes com strings copiadas do terminal vs. strings lidas do arquivo produzem resultados diferentes.

**Phase a tratar:** M1 (REQ-CORE-01 parser) e M2 (validadores primitivos). A normalização NFC deve estar no parser, antes de qualquer validador receber o texto.

**Severidade:** MÉDIA — falsos negativos são silenciosos (violação existe mas não é detectada). O autor acredita que o texto está limpo quando não está.

---

### Pitfall 6: Catastrophic Backtracking em Regex Complexos

**O que dá errado:**
O regex de cst_002 contém `.{0,150}` no meio:
`\bnão (apenas|só|somente)\b.{0,150}\bmas (também|ainda)\b`
Para um parágrafo de 400 chars sem o match esperado, o engine tenta todas as combinações
de `.{0,150}` antes de declarar "não encontrado". O regex de cst_008 tem múltiplos grupos
alternados: `(ângulos?|eixos?|planos?|vetores?|perspectivas?|registros?|frentes?|prismas?|flancos?|vieses?|vertentes?|direções)`.
Sobre um parágrafo de 2000 chars que não tem match, o engine pode tentar O(n²) ou O(2^n)
combinações dependendo da interação entre os quantificadores.

**Por que acontece:**
Regex com `.*` ou `.{0,N}` no meio de padrões longos criam ambiguidade que o engine
resolve por backtracking. Com `re.UNICODE`, cada passo de backtrack precisa verificar
propriedades Unicode dos caracteres, aumentando o custo por passo. Artigos de 30k palavras
com parágrafos de 500+ chars + 12 cst + 14 lex + 9 coc = centenas de aplicações de regex
sobre cada parágrafo.

**Como evitar:**
1. Para cada regex com `.{0,N}` no meio, medir o tempo de execução com `timeit` sobre o parágrafo mais longo do artigo Eólica Nordeste (ground truth). Se > 50ms por parágrafo, reescrever.
2. Usar `re.compile()` fora do loop de parágrafos (compilar uma vez, usar muitas). Isso já é padrão, mas fácil de esquecer em refatorações.
3. Converter `.{0,150}` para `[^\n]{0,150}` quando o match deve ocorrer dentro de uma linha (proíbe backtrack cross-line). Isso reduz o espaço de busca.
4. Para cst_008 com lista longa de metáforas espaciais: testar se `re.compile(..., re.IGNORECASE)` piora a performance. Se sim, considerar normalizar o texto para lowercase antes de aplicar o regex (e ajustar o regex para lowercase puro).
5. Adicionar timeout por regex se stdlib `re` for mantida: envolver em `threading.Timer` ou usar `signal.alarm` (Unix). Alternativamente, usar o pacote `regex` com suporte a timeout (`regex.compile(..., timeout=0.5)`) apenas para os regexes problemáticos.
6. Benchmark obrigatório: a constraint de projeto é < 5s para artigo de 30k palavras. Escrever benchmark que roda todos os validadores contra o artigo Eólica e mede tempo total. Se > 5s, identificar o regex responsável e reescrever.

**Sinais de alerta:**
- `python -m timeit` mostrando > 10ms por aplicação de regex sobre parágrafo médio.
- Validação de artigo inteiro levando > 30s (10x o limite).
- O sistema "trava" visivelmente em certos parágrafos (os mais longos do artigo).

**Phase a tratar:** M2 (validadores primitivos). Implementar benchmark de performance como parte dos testes de aceitação de M2. Não esperar M8 para descobrir que é lento.

**Severidade:** MÉDIA — afeta usabilidade (lento) mas não corrompe dados. Pode mascarar o problema se o dev só testa com parágrafos curtos.

---

### Pitfall 7: Ambiguidade Contextual — Mesmo Termo Proibido em Posição Legítima

**O que dá errado:**
cst_009 proíbe abertura condicional "Se... então..." em posição de abertura argumentativa,
mas o JSON diz explicitamente: "Permitido em contextos genuinamente hipotéticos (cálculos,
simulações, contrafactuais explícitos)." O validador que só aplica o regex de detecção
vai marcar TODA construção "Se X, então Y" como violação — inclusive num trecho de
análise contrafactual do Cap. 2 do artigo (ex.: "Se o REIDI não existisse, então a TIR
dos parques seria X%").

Outro caso: cst_001 (dois-pontos) proíbe ":" introduzindo explicação, mas dois-pontos
em citações ABNT (`AUTOR, Ano, p. X: "citação direta"`) e em URLs
(`https://www.aneel.gov.br/`) são legítimos e não devem ser detectados.

**Por que acontece:**
Regex captura forma sintática, não função pragmática. A distinção "abertura argumentativa"
vs. "contrafactual explícito" requer compreensão do parágrafo — que está fora do alcance
de qualquer regex determinístico.

**Como evitar:**
1. Implementar filtros de contexto antes de emitir Violacao:
   - Para cst_001: ignorar ":" dentro de padrão de citação ABNT (`\(.*\d{4}.*\)`) e dentro de URLs (precedido de `http` ou `https`).
   - Para cst_009: verificar se o parágrafo contém marcadores de contrafactual ("se não existisse", "se fosse", "na hipótese de") antes de marcar como violação.
2. Definir, para cada cst com exceções documentadas no JSON (cst_004 tem `exclusoes`, cst_009 tem `observacao`, cst_011 tem `observacao`), um campo `contextos_excluidos` a ser adicionado ao JSON. O validador lê esse campo e aplica filtros antes de emitir.
3. Para violações de nível ALERTA (não ERRO), sempre mostrar o trecho ao autor no modo ASSISTIDO e pedir confirmação — nunca fazer AUTO em casos ambíguos.
4. Testes de falso positivo são tão importantes quanto testes de detecção: para cada cst, ter um conjunto de inputs onde a violação NÃO deve ser detectada (contextos legítimos).

**Sinais de alerta:**
- Relatório marca como violação uma citação ABNT (dois-pontos dentro da citação).
- O autor rejeita mais de 20% dos patches de uma regra específica — indica que o contexto legítimo é frequente no domínio jurídico.
- URLs de fontes oficiais (ANEEL, CCEE, IBAMA) são marcadas como tendo dois-pontos proibido.

**Phase a tratar:** M2 (validadores primitivos). Cada validador deve ter testes de falso positivo com exemplos de contextos legítimos do domínio jurídico.

**Severidade:** MÉDIA — falsos positivos em contextos legítimos destroem a credibilidade do sistema e fazem o autor ignorar o relatório inteiro.

---

### Pitfall 8: Contador de "Fixed" Conta Rejeições como Correções

**O que dá errado:**
O orchestrator mostra ao autor: "12 violações corrigidas." Mas o autor rejeitou 5 patches
no modo ASSISTIDO. O contador contabilizou "proposta apresentada" como "corrigida". O
relatório final diz que o artigo tem 3 violações ativas, mas na verdade tem 8 (as 5
rejeitadas mais as 3 não cobertas).

**Por que acontece:**
Confusão entre estado do patch e estado da violação. Estados distintos:
- `patch_proposto` — fixer gerou o patch, ainda não foi apresentado ao autor
- `patch_apresentado` — autor viu o diff
- `patch_aceito` — autor confirmou, texto foi alterado
- `patch_rejeitado` — autor recusou, texto inalterado (VIOLAÇÃO PERMANECE ATIVA)
- `violacao_suprimida` — autor decidiu ignorar a violação (INTENCIONALMENTE não corrigi)

**Como evitar:**
1. Modelar o estado do patch como enum separado do estado da violação:
   ```python
   class EstadoPatch(str, Enum):
       PROPOSTO = "PROPOSTO"
       ACEITO = "ACEITO"
       REJEITADO = "REJEITADO"
       SUPRIMIDO = "SUPRIMIDO"  # autor escolheu ignorar a violação
   ```
2. O relatório final deve listar separadamente: violações corrigidas (ACEITO), violações
   com correção rejeitada (REJEITADO — ainda ativas), violações suprimidas pelo autor
   (SUPRIMIDO — ativas mas aceitas conscientemente).
3. O contador "corrigidas" deve contar SOMENTE patches com estado ACEITO.
4. Patches REJEITADOS devem reaparecer no relatório da próxima rodada, a menos que o
   autor explicitamente os mova para SUPRIMIDO.

**Sinais de alerta:**
- O número de violações no relatório final é menor que o número de violações no relatório inicial menos o número de patches que o autor confirmou.
- Ao revalidar o artigo após uma sessão, violações que o autor "rejeitou" não aparecem mais no relatório.

**Phase a tratar:** M6 (Fixers ASSISTIDO CLI). O modelo de estado deve ser definido em M1 (dataclass Patch) com campos que suportem os estados futuros, mesmo que os estados REJEITADO/SUPRIMIDO só sejam usados em M6.

**Severidade:** MÉDIA — não corrompe o texto, mas gera relatório enganoso. O autor acredita que o artigo está mais limpo do que está.

---

### Pitfall 9: Versionamento de Regras — Artigo Escrito Sob v1.0, Revalidado Sob v2.0

**O que dá errado:**
O artigo Eólica Nordeste foi escrito e auditado manualmente com base nas regras dos
JSONs vigentes em abril/2026. Em setembro/2026, o JSON cst_004 é expandido com 15 novos
termos na lista `exclusoes` E o regex de cst_012 é ajustado para capturar mais casos.
Ao revalidar o artigo, surgem 20 "violações novas" que não existiam antes — porque o
validador mudou, não o artigo. O autor não sabe se o texto piorou ou se as regras
ficaram mais estritas.

**Por que acontece:**
Os JSONs de regras são "fonte de verdade viva" (versionados em git, mas sem campo de
versão semântica interno). O validador carrega sempre a versão HEAD dos JSONs. Um
relatório de auditoria gerado hoje não é comparável a um gerado amanhã se os JSONs
mudaram no intervalo.

**Como evitar:**
1. Adicionar campo `"versao": "1.0.0"` (semver) a cada JSON de regras. O validador deve registrar no cabeçalho do relatório `AUDITORIA.md` a versão de cada JSON utilizado.
2. Incluir no relatório o git hash do commit dos JSONs no momento da validação (`git rev-parse HEAD` no diretório `biblioteca_canonica/`).
3. Para re-validação, o orchestrator deve avisar se a versão dos JSONs mudou desde a última auditoria do arquivo: "Atenção: as regras mudaram desde a última auditoria (commit abc123 → def456). Violações novas podem ser decorrentes da mudança de regras."
4. Manter changelog dos JSONs (`biblioteca_canonica/CHANGELOG.md`) com semver, para que o autor saiba o que mudou entre versões.

**Sinais de alerta:**
- Uma re-validação de artigo sem alterações no texto retorna mais violações que a validação anterior.
- O autor não consegue saber se o texto piorou ou as regras ficaram mais estritas.

**Phase a tratar:** M2 (validadores primitivos — campo versão nos JSONs) e M8 (relatório do orchestrator — registrar hash dos JSONs).

**Severidade:** MÉDIA — não corrompe dados, mas destrói a rastreabilidade e gera ruído no processo de auditoria.

---

### Pitfall 10: Integração com Pipeline LaTeX — Validador Altera Texto que o LaTeX Assume Imutável

**O que dá errado:**
O pipeline LaTeX (`build.sh`) compila o `.tex` a partir do `.md` via pandoc. Se o fixer
AUTO altera o `.md` em memória e grava de volta, e o build.sh roda logo em seguida sem
detectar a mudança, o output LaTeX pode ser compilado a partir de uma versão stale do
`.md` (cached). Pior: se o fixer opera sobre o `.tex` diretamente (para validar o LaTeX),
e comete um erro de offset (Pitfall 2), ele pode corromper o `.tex` com comandos LaTeX
quebrados (ex.: substituir texto dentro de `\footnote{...}` e deixar a chave aberta).

**Por que acontece:**
O pipeline LaTeX não tem mecanismo de detecção de "arquivo modificado durante build"
nativo. O `build.sh` atual assume que o `.tex` é estável. A integração do validador
no pipeline (REQ-ORC-06) pode introduzir uma etapa que modifica o fonte entre o parse
do pandoc e a compilação do pdflatex.

**Como evitar:**
1. Separar estritamente as operações: o validador lê e reporta; o fixer grava. A integração no `build.sh` deve ser somente de validação (exit code não-zero bloqueia build), nunca de fix automático. Fix automático só via CLI explícito do autor.
2. O fixer NUNCA opera sobre `.tex` — sempre sobre `.md`. O `.tex` é output do pandoc, não input do sistema. Isso simplifica o problema: o validador de LaTeX lê o `.tex` para detectar violações, mas as correções são aplicadas no `.md` de origem.
3. Se o fixer modifica o `.md`, ele deve invalidar qualquer `.tex` compilado existente (tocar em `artigo.tex` ou deletar `artigo.pdf`) para forçar recompilação limpa.
4. Implementar lock de arquivo durante aplicação de patches: `fcntl.flock()` ou `pathlib.Path.with_suffix('.lock')` para prevenir escrita concorrente.

**Sinais de alerta:**
- Após uma sessão de fixers, o `build.sh` compila sem erros mas o PDF não reflete as correções aplicadas.
- O PDF tem texto duplicado ou fragmentos de LaTeX visíveis no output (ex.: `\footnote{` sem fechar).
- `git diff artigo.tex` mostra mudanças que não correspondem ao que o autor editou no `.md`.

**Phase a tratar:** M8 (REQ-ORC-06 integração LaTeX). A regra "fixer só no `.md`, nunca no `.tex`" deve ser documentada como invariante de arquitetura desde M1.

**Severidade:** MÉDIA — pode corromper o output final (PDF) mas não o arquivo-fonte `.md`. Recuperável via `git checkout artigo.tex`.

---

### Pitfall 11: Claude API — Rate Limits e Custos em Sessão de Fixer LLM

**O que dá errado:**
O artigo Eólica tem 12 ocorrências de cst_012 (anúncio metarretórico) e 3 ocorrências
de coc_007 (VERMELHO_FORTE, multiplicador 5.0). Se todos os fixers LLM rodarem em modo
paralelo (para cada violação, uma chamada à API), a sessão pode fazer 15+ chamadas
simultâneas a `claude-sonnet-*`. O rate limit da API (por padrão: requests por minuto
por API key) é excedido; o SDK retorna 429; o orchestrator não tem retry com backoff;
a sessão falha no meio, deixando o arquivo parcialmente corrigido.

Custo: claude-sonnet-4-5 custa ~$3/MTok de input. Um prompt com todos os JSONs de
termos_proibidos injetados (necessário para Pitfall 4) pode ter 4000+ tokens por chamada.
15 chamadas = 60k tokens de input = ~$0.18 por sessão. Para 50 sessões de auditoria no
ciclo de doutorado, o custo pode chegar a $9 — controlável, mas invisível sem tracking.

**Como evitar:**
1. Fixers LLM devem ser sequenciais por padrão, não paralelos: uma chamada por vez, com backoff exponencial em 429 (`time.sleep(2 ** tentativa)` até MAX_RETRIES = 3).
2. O SDK `anthropic` já implementa retry automático com backoff — verificar se `max_retries` está configurado corretamente no cliente.
3. Implementar modo dry-run para LLM: `corrigir artigo.md --nivel llm --dry-run` mostra quantas chamadas seriam feitas e o custo estimado antes de executar.
4. Cachear respostas LLM por hash do parágrafo + hash da regra: se o mesmo parágrafo com a mesma violação já foi enviado à API nesta sessão (ex.: por retry após Pitfall 3), não reenviar.
5. Adicionar `--budget-limit-tokens N` como flag do CLI: abortar a sessão de fixers LLM se o total de tokens estimados ultrapassar N. Default: 100k tokens por sessão.

**Sinais de alerta:**
- Sessão de fixers LLM demora > 2 minutos (indica muitas chamadas ou backoff excessivo).
- Erro 429 visível no log sem retry automático.
- Custo da API cresce entre sessões sem que o artigo tenha crescido proporcionalmente.

**Phase a tratar:** M7 (Fixers LLM). O cliente Claude API deve ser configurado com retry, timeout e estimativa de custo desde o início de M7, antes de integrar ao orchestrator.

**Severidade:** MÉDIA — não corrompe dados; o maior risco é custo inesperado e sessão incompleta. Recuperável; o arquivo não é alterado até o patch ser aceito.

---

### Pitfall 12: Testes Unitários — Corpus Mínimo Insuficiente para Cobrir Edge Cases

**O que dá errado:**
O teste de cst_012 verifica apenas o exemplo exato do JSON (`"A descoberta específica de
Raworth (2017, p. e48) reside em..."`). O validador passa no teste. Em produção, o artigo
contém `"A tese de fundo de Leff (2006) consiste em..."` — variação com "tese de fundo"
(que está na lista `sintagmas_metarretoricos_suspeitos`) e "consiste" (que está nos
`verbos_estativos_associados`). O validador detecta corretamente. Mas não detecta `"A
intuição de Leff (2006) reside em..."` porque "intuição" sem "central" não está no regex.
Falso negativo não coberto pelo teste.

Outro caso: o teste de offset verifica que a linha 42 do arquivo é corretamente apontada.
Mas não testa artigo com footnotes pandoc (`[^1]`), que podem deslocar a contagem de
linhas do markdown-it-py se o plugin de footnotes não estiver ativado.

**Como evitar:**
1. Para cada validador, o corpus de testes deve ter TRÊS grupos:
   - **Positivos canônicos:** exemplos exatos do JSON (`exemplo_proibido`).
   - **Positivos variantes:** variações que o regex deve capturar mas que não estão no JSON (ex.: sintagmas da lista `sintagmas_metarretoricos_suspeitos` com diferentes verbos da lista `verbos_estativos_associados`).
   - **Negativos (falsos positivos):** textos limpos que o regex NÃO deve capturar (ex.: citação ABNT com dois-pontos, "quando" para cst_004, "Se não fosse" em contrafactual).
2. Usar `pytest.mark.parametrize` para alimentar os grupos: um parâmetro por entrada, resultado esperado (`True`/`False`) por parâmetro.
3. O artigo Eólica Nordeste (`artigo_final/artigo.md`) deve ser um teste de integração explícito: as violações conhecidas (cst_007, cst_008, cst_010, cst_011, cst_012) devem ser detectadas, e os parágrafos limpos não devem ter falsos positivos.
4. Testes de offset: fixtures com arquivo markdown multi-parágrafo com footnotes pandoc. Verificar que a linha reportada pelo validador coincide com a linha real no arquivo (comparar com grep).

**Sinais de alerta:**
- Coverage do validador mostra branch não coberto no filtro de exclusões.
- O artigo Eólica tem uma violação conhecida que o validador não detecta (falso negativo descoberto em produção, não em teste).
- Testes passam com strings hardcoded mas falham com strings lidas de arquivo (encoding UTF-8 vs. UTF-8-BOM, ou `\r\n` vs. `\n`).

**Phase a tratar:** M1 (testes do piloto cst_012) e M2 (testes de cada validador primitivo). REQ-ORC-04 deve ser tratado como critério de aceitação de cada validador, não como tarefa de M8.

**Severidade:** MÉDIA — falsos negativos silenciosos e falsos positivos em produção que os testes não cobrem. O custo de um teste insuficiente é um sistema que parece funcionar mas não é confiável.

---

## Technical Debt Patterns

| Atalho | Benefício imediato | Custo de longo prazo | Quando é aceitável |
|--------|-------------------|---------------------|-------------------|
| Hardcodar lista de exclusões em Python em vez de ler do JSON | Velocidade de implementação no piloto M1 | Toda mudança na lista exige code change; derrota a arquitetura "1 JSON por regra" | Nunca — o JSON já tem o campo `exclusoes` |
| Aplicar patches em ordem crescente (top-down) em vez de reversa | Código mais simples | Drift de offsets garante corrupção do arquivo em artigos com múltiplas violações por parágrafo | Nunca — é o pitfall 2 |
| Não revalidar após fix LLM | Economiza tempo e tokens | Fix LLM pode introduzir novas violações (Pitfall 4); o artigo fica em estado pior | Nunca — a pós-validação é a única proteção contra contaminação LLM |
| Contar rejeições como "corrigidas" no contador | Contador parece mais alto | Relatório enganoso; o autor não sabe o estado real do artigo | Nunca |
| Testar apenas com exemplo canônico do JSON | Rápido de escrever | Falsos negativos em variantes não cobertas pelo exemplo (Pitfall 12) | Só aceitável no piloto M1 se o corpus de variantes for adicionado em M2 como dívida explícita |
| Injetar apenas a regra violada no prompt LLM (não a lista negra completa) | Prompt menor, menor custo de API | Alta probabilidade de o LLM usar termos proibidos (Pitfall 4) | Nunca para fixers LLM de cst_008/cst_010/cst_007 que reescrevem parágrafos inteiros |
| Sem normalização NFC antes de validar | Código mais simples | Falsos negativos para textos com combining characters (Pitfall 5) | Nunca se o input vier de pandoc ou de cópia de PDF |
| Sem campo `versao` nos JSONs de regras | JSONs mais simples | Impossível rastrear qual versão de regras produziu um relatório de auditoria (Pitfall 9) | Aceitável no piloto M1; obrigatório antes de M3 |

---

## Integration Gotchas

| Integração | Erro comum | Abordagem correta |
|------------|-----------|------------------|
| Claude API (M7) | Chamadas paralelas sem controle de rate limit → 429 em lote | Sequencial com retry exponencial; `max_retries=3` no cliente `anthropic`; dry-run antes de executar |
| Claude API (M7) | Prompt sem lista negra completa → LLM contamina com termos proibidos | Injetar todos os JSONs de `termos_proibidos/` no sistema prompt via jinja2; temperatura 0.1; pós-validar saída |
| Pipeline LaTeX (`build.sh`) | Fixer modifica `.md` durante build → PDF stale ou corrompido | Fixer nunca no `.tex`; sempre no `.md`; invalidar `.tex` após fix; hook no build só valida (exit code), nunca corrige |
| Pre-commit hook (M8) | Hook roda fixers automáticos em modo non-interactive → bloqueia commit sem saída legível | Pre-commit hook só valida (exit code 1 se ERRO); nunca aplica fix; exibir lista de violações no STDOUT |
| markdown-it-py (M1) | Plugin de footnotes não ativado → `[^n]` tratado como texto plano, offsets errados | `from mdit_py_plugins.footnote import footnote_plugin; md.use(footnote_plugin)` antes de parsear qualquer `.md` |
| pylatexenc (M2) | Parsear `\footnote{...}` como corpo de texto → regex de cst aplicado ao argumento da footnote | Identificar contexto `NOTA_RODAPE` vs. `CORPO` no walker; aplicar validadores diferentes por contexto |
| git hooks (M8) | Hook instalado por `pre-commit install` usa PATH do sistema, não o venv do projeto | Especificar `language: python` e `entry:` com o caminho do venv no `.pre-commit-hooks.yaml` |

---

## Performance Traps

| Armadilha | Sintomas | Prevenção | Quando quebra |
|-----------|----------|-----------|---------------|
| `re.compile()` dentro do loop de parágrafos | Lentidão proporcional ao número de parágrafos (compilação O(n) em vez de O(1)) | Compilar todos os regexes na inicialização do validador (`__init__`) | Qualquer artigo com > 50 parágrafos |
| `.{0,150}` em regex sem âncora de linha (cst_002) | Exponencial em parágrafos longos sem match | Trocar por `[^\n]{0,150}` para limitar a uma linha | Parágrafos > 200 chars sem o padrão esperado |
| Validador coocorrência (M3) re-executa regex dos primitivos | Duplica o custo de M2 | O validador de coocorrência consome a saída em memória dos primitivos (lista de Violacao), não re-aplica regex | Qualquer artigo (custo é 2x desnecessariamente) |
| Fixer LLM chamado em loop sem cache | Custo de API O(n) por violação, sem reaproveitar respostas idênticas | Cache por hash(parágrafo + regra_id); evitar chamadas duplicadas em reruns | Sessão com > 5 fixers LLM no mesmo artigo |
| unicodedata.normalize() chamado por parágrafo em vez de uma vez no arquivo | Custo de normalização O(n * p) onde p = parágrafos | Normalizar o arquivo inteiro antes de segmentar em parágrafos | Artigos com > 5k palavras e muitos combining characters |

---

## "Looks Done But Isn't" Checklist

- [ ] **Validador cst_004 (gerúndio):** O campo `exclusoes` do JSON está sendo lido e aplicado como filtro? Testar com "quando", "grande", "vendo" — não devem gerar Violacao.
- [ ] **Aplicação de patches reversa:** Aplicar 3 patches com offsets diferentes no mesmo parágrafo. O parágrafo resultante deve ser semanticamente coerente e com posições corretas.
- [ ] **Guardrail anti-loop:** O orchestrator para após MAX_ITERACOES_POR_PARAGRAFO mesmo se ainda há violações? Testar com input que causa loop (fix de cst_001 que introduz cst_003).
- [ ] **Contador de estado:** Rejeitar um patch no modo ASSISTIDO. O relatório final deve listar essa violação como REJEITADA (ainda ativa), não como corrigida.
- [ ] **Normalização NFC:** Inserir "ã" como `a` + combining tilde no texto de teste. O validador deve detectar "consolidação" tanto na forma NFC quanto na NFD (após normalizar para NFC antes de validar).
- [ ] **Versão dos JSONs no relatório:** O cabeçalho do `AUDITORIA.md` deve incluir o git hash dos JSONs usados e a data da validação.
- [ ] **Integração LaTeX:** Após fix no `.md`, o `.tex` existente é invalidado ou deletado para forçar recompilação?
- [ ] **Rate limit API:** Simular 15 chamadas LLM em sequência rápida. O cliente retenta com backoff em 429 sem abortar a sessão?
- [ ] **Corpus de falsos positivos:** Para cada validador, existe pelo menos um teste com input limpo que NÃO deve gerar Violacao?
- [ ] **Plugin de footnotes ativado:** Parsear o artigo Eólica com footnotes `[^n]`. As linhas reportadas devem corresponder à posição real no arquivo (verificar com `grep -n`).

---

## Recovery Strategies

| Pitfall | Custo de Recuperação | Passos de Recuperação |
|---------|---------------------|-----------------------|
| Drift de offsets corrompeu `.md` | ALTO | `git checkout artigo.md`; re-rodar fixer com implementação corrigida; perda de todas as correções manuais não commitadas |
| Loop infinito sem guardrail (sessão bloqueada) | BAIXO | `Ctrl+C`; verificar estado do arquivo (diff com `git diff`); se parcialmente modificado, `git checkout artigo.md`; implementar guardrail antes de tentar novamente |
| Fixer LLM introduziu termos proibidos e o autor aceitou sem notar | MÉDIO | Revalidar o artigo após cada sessão de fix LLM; se já commitado, `git show HEAD:artigo.md` e recriar a sessão de auditoria sobre a versão anterior |
| Rate limit excedido no meio de sessão LLM | BAIXO | O SDK retenta automaticamente se configurado; se sessão abortou sem aplicar todos os patches, revalidar o artigo para ver o estado atual e retomar |
| Regex de cst_004 gerou falso positivo aceito pelo autor | BAIXO | Identificar a palavra erroneamente corrigida; `git diff` para ver o patch; reverter manualmente ou via `git checkout -p`; adicionar a palavra à lista `exclusoes` do JSON |
| Versão de regras mudou sem rastreamento | MÉDIO | `git log --oneline biblioteca_canonica/02_escrita/` para identificar mudanças; re-auditar o artigo com a versão dos JSONs do momento da escrita (via `git checkout HASH -- 02_escrita/`) |

---

## Pitfall-to-Phase Mapping

| Pitfall | Phase de Prevenção | Verificação |
|---------|-------------------|-------------|
| P1 — Falsos positivos cst_004 (gerúndio) | M2 — Validador cst_004 | Testes com corpus de palavras não-verbais; `exclusoes` do JSON aplicado como filtro |
| P2 — Drift de offsets | M1 — REQ-CORE-06 patch reverso | Teste unitário: 3 patches no mesmo parágrafo, verificar resultado final |
| P3 — Loop validar→fixar→revalidar | M8 — REQ-ORC-02 guardrail | Teste de integração com input que causa loop; verificar que orchestrator para em ≤ 3 iterações |
| P4 — Fixer LLM contamina com termos proibidos | M7 — Fixers LLM | Pós-validação obrigatória de saída LLM antes de aceitar patch; suite de testes LLM |
| P5 — Unicode PT-BR (NFC/combining) | M1 — REQ-CORE-01 parser | `unicodedata.normalize('NFC', texto)` no parser; testes com ambas as formas |
| P6 — Catastrophic backtracking | M2 — Benchmark de performance | Benchmark < 5s sobre artigo Eólica 30k palavras; timeit por regex suspeito |
| P7 — Ambiguidade contextual | M2 — Filtros de contexto nos validadores | Testes de falso positivo: citação ABNT com ":", contrafactual com "Se", URL com ":" |
| P8 — Contador conta rejeições como "fixed" | M6 — Fixer ASSISTIDO CLI | Cenário de teste: rejeitar patch, verificar que relatório final lista violação como REJEITADA |
| P9 — Versionamento de regras | M2 (campo versão) + M8 (hash no relatório) | Re-validar artigo após mudar JSON; relatório deve indicar que regras mudaram |
| P10 — Fixer corrompe integração LaTeX | M8 — REQ-ORC-06 integração | Regra arquitetural documentada: fixer só no `.md`; teste de integração com build.sh |
| P11 — Rate limits e custo API | M7 — Cliente Claude API | Dry-run mode; retry com backoff; teste simulando 429 |
| P12 — Corpus de testes insuficiente | M1 (piloto) + M2 (primitivos) | Três grupos de testes (positivos canônicos, variantes, negativos) por validador |

---

## Sources

- `biblioteca_canonica/02_escrita/termos_proibidos/04_construcoes_sintaticas_proibidas.json`
  — campo `exclusoes` de cst_004 e `observacao` de cst_009 e cst_011 lidos diretamente;
  campo `operacao_fix_automatizavel.ressalva` de cst_012 (conjugação humana obrigatória)
- `biblioteca_canonica/02_escrita/termos_proibidos/06_regras_coocorrencia.json`
  — coc_007 (multiplicador 5.0, VERMELHO_FORTE) e coc_009 (escopo documento_inteiro vs.
  parágrafo) lidos diretamente; campo `como_aplicar` com fluxo de penalidade
- `biblioteca_canonica/.planning/PROJECT.md` — REQ-CORE-06 (patches em ordem reversa),
  constraint < 5s, REQ-ORC-02 (guardrail loop), caso de teste artigo Eólica Nordeste
- `biblioteca_canonica/.planning/research/STACK.md` — decisão `re` stdlib vs. `regex`
  module; análise de `\b` Unicode em Python 3; modelo de Patch/Violacao com campos de estado
- `biblioteca_canonica/.planning/research/FEATURES.md` — análise de Vale e proselint
  (comparação de capacidades de fixer); anti-feature "LLM irrestrito"; conflito entre
  fixer LLM e restrição "zero dependências de rede em validadores"
- Python docs `re` module — https://docs.python.org/3/library/re.html
  (comportamento de `\b` com Unicode; ausência de `\p{}` property escapes)
- Python docs `unicodedata` — https://docs.python.org/3/library/unicodedata.html
  (normalização NFC/NFD)
- Anthropic SDK docs — comportamento de retry e rate limiting (HIGH confidence)
- ESLint `--fix-dry-run` como referência para modo dry-run de fixer
- Análise empírica das violações conhecidas do artigo Eólica Nordeste (cst_007, cst_008,
  cst_010, cst_011, cst_012 detectadas via inspeção manual — documentado em PROJECT.md)

---

*Pitfalls research for: Validador & Fixer Acadêmico — linter de prosa PT-BR com regras JSON*
*Researched: 2026-05-04*
