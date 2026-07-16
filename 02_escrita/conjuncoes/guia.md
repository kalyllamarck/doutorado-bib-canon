# Guia de Substituição e Redistribuição de Conjunções

> Este guia opera o catálogo de 802 conjunções armazenado em `coordenativas/` e `subordinativas/`. Define a anatomia obrigatória do parágrafo, a regra de distribuição (máxima diversidade, mínima proximidade) e o procedimento de substituição em texto já escrito.

---

## 1. Anatomia obrigatória do parágrafo

### 1.1 Definições operacionais

- **Parágrafo:** unidade textual entre dois recuos. Contém **várias orações**. Extensão canônica: 100 a 260 palavras (ver `escrita_canonica.json` p_02).
- **Oração:** unidade sintática terminada por **ponto final**. Cada parágrafo tem entre 3 e 8 orações típicas (variável conforme densidade do argumento).
- **Conjunção:** termo de abertura que liga a oração ao fluxo anterior (do parágrafo prévio ou da oração prévia dentro do mesmo parágrafo).
- **Conector com parágrafo anterior:** sintagma que retoma um termo do último período do parágrafo anterior (progressão temática — ver `escrita_canonica.json` p_08, subregra 2).

### 1.2 Esqueleto do parágrafo (regra hard)

```
[Conj_0], [conector com parágrafo anterior], oração_1.
[Conj_1], oração_2.
[Conj_2], oração_3.
[Conj_3], oração_4.
...
[Conj_n], oração_n. ← último período na voz do autor (p_19)
```

**Regras:**

1. **Toda oração abre com conjunção** (`Conj_0` a `Conj_n`). Sem exceção: nem na primeira oração do parágrafo, nem nas internas.
2. **A primeira oração** acumula dois movimentos: conjunção + conector com parágrafo anterior (progressão temática). Conector pode ser sintagma curto: "Diante disso", "Em paralelo", "Apesar do exposto", "Daí que".
3. **Conjunções distintas** entre orações consecutivas — proibido repetir a mesma conjunção dentro do parágrafo.
4. **Último período** fecha na voz do autor da tese, não em citação solta (ver `escrita_canonica.json` p_19).

### 1.3 Exemplo aplicado

> **Embora** a literatura especializada relacione o controle de convencionalidade aos artigos 2º e 68.1 da CADH, **a hermenêutica brasileira atual** indica que tais dispositivos não estabelecem procedimento sistematizado. **Ademais**, os Estados Partes encontram-se juridicamente obrigados a cumprir decisões de Tribunais Internacionais a que se vincularam. **Entretanto**, esses mesmos Tribunais permanecem adstritos ao bloco de convencionalidade que fundamenta sua atuação. **Por essa lógica**, a verificação jurisdicional da conformidade entre normas internas e tratados internacionais depende de critério construído pela própria pesquisa.

Anatomia visível:
- Conj_0 "Embora" + conector "a literatura especializada relacione..." (conexão com parágrafo anterior)
- Conj_1 "Ademais"
- Conj_2 "Entretanto"
- Conj_3 "Por essa lógica" → fechamento na voz do autor

---

## 2. Regra de distribuição (máxima diversidade, mínima proximidade)

Aplica-se quando o validador detecta duas ou mais conjunções repetidas ou próximas dentro da janela de 5 parágrafos (`p_20`).

### 2.1 Princípio

> **Máxima distribuição, mínima proximidade.** Nunca distribuir conjunções por ordem alfabética nem pela ordem do catálogo. Garantir equidistância entre ocorrências da mesma família semântica.

### 2.2 Janela de controle

| Escopo | Repetição tolerada da mesma conjunção |
|--------|---------------------------------------|
| Mesmo parágrafo | **zero** (proibido) |
| 2 parágrafos consecutivos | **zero** (proibido) |
| Janela de 5 parágrafos | máximo 2 ocorrências, com pelo menos 2 parágrafos entre elas |
| Janela de 10 parágrafos | máximo 3 ocorrências, com pelo menos 2 parágrafos entre cada uma |

### 2.3 Famílias semânticas (12 subtipos do catálogo)

Substituição preferida vai à **mesma família** da conjunção sob revisão. Famílias disponíveis:

**Coordenativas** (`coordenativas/`)
- `aditivas` (adição: e, ademais, também, ainda)
- `adversativas` (contraste: mas, porém, contudo, todavia, entretanto)
- `alternativas` (alternância: ou, quer... quer, ora... ora, seja... seja)
- `conclusivas` (consequência: logo, portanto, por conseguinte, pois)
- `explicativas` (justificativa: pois, porque, porquanto, que)

**Subordinativas** (`subordinativas/`)
- `causais`, `comparativas`, `concessivas`, `condicionais`, `conformativas`, `consecutivas`, `finais`, `integrantes`, `locativas`, `modais`, `modo_comparativas_hibridas`, `proporcionais`, `temporais`

Regra: substituir **dentro da mesma família semântica**. Trocar de família muda o sentido — só se justificado por revisão argumentativa.

---

## 3. Procedimento de substituição (texto já escrito)

### Passo 1 — Inventário

Mapear no texto todas as conjunções presentes. Para cada uma, anotar:
- posição (parágrafo N, oração M)
- família semântica
- frequência total no texto

### Passo 2 — Detecção de violações

Marcar como violação:
- (a) repetição **dentro de um parágrafo**
- (b) repetição em **parágrafos consecutivos**
- (c) frequência da mesma conjunção **acima do tolerado** na janela de 5 ou 10 parágrafos

### Passo 3 — Substituição equidistante

Para cada violação, abrir o JSON da família correspondente (ex.: `coordenativas/adversativas.json`) e escolher conjunção alternativa seguindo:

1. **Filtrar candidatos pelo registro** (acadêmico formal; descartar `informais_filtradas` do INDEX).
2. **Filtrar pelo score acadêmico** (preferir maior score quando disponível).
3. **Verificar polissemia** (`INDEX.polissemicas`): conjunção com múltiplos sentidos pode mudar a leitura — usar apenas se o sentido pretendido coincidir com o subtipo.
4. **Distribuir aleatoriamente** entre os candidatos restantes. **Nunca** começar pela primeira do JSON e descer — isso cria viés de catalogação. Sortear ou pular a passos irregulares.

### Passo 4 — Verificação de equidistância

Após substituição, recalcular a janela de 5 e 10 parágrafos para a nova conjunção. Se a substituta cria nova violação adjacente, voltar ao passo 3 e escolher outra.

### Passo 5 — Conectores com parágrafo anterior

Substituir o **conector com parágrafo anterior** (sintagma que retoma termo do parágrafo prévio) é diferente de substituir conjunção interna. Esse conector exige:
- Retomada lexical (termo do parágrafo anterior repetido ou sinônimo próximo)
- Conjunção apropriada à transição (causal, adversativa, conclusiva, conforme o movimento argumentativo)

---

## 4. Tabela de substituição rápida (top adversativas, top conclusivas, top causais)

Tabela operacional para uso durante revisão. Para repertório completo, abrir os JSONs.

### 4.1 Adversativas (`coordenativas/adversativas.json`)

| Forma comum | Substitutas equidistantes (rotação) |
|-------------|-------------------------------------|
| mas | contudo · todavia · entretanto · não obstante · porém |
| porém | todavia · contudo · em contrapartida · não obstante |
| contudo | entretanto · todavia · em todo caso · ainda assim |

### 4.2 Conclusivas (`coordenativas/conclusivas.json`)

| Forma comum | Substitutas equidistantes |
|-------------|---------------------------|
| portanto | por conseguinte · logo · pois · em vista disso · assim |
| logo | portanto · por isso · daí que · em consequência |
| assim | desse modo · dessa maneira · em vista disso · por conseguinte |

### 4.3 Causais (`subordinativas/causais.json`)

| Forma comum | Substitutas equidistantes |
|-------------|---------------------------|
| porque | porquanto · uma vez que · visto que · pois que · dado que |
| pois | porquanto · uma vez que · visto que · já que |
| visto que | dado que · uma vez que · porquanto · porque |

### 4.4 Aditivas (`coordenativas/aditivas.json`)

| Forma comum | Substitutas equidistantes |
|-------------|---------------------------|
| e | bem como · ademais · ainda · além disso |
| também | igualmente · de igual modo · ademais · do mesmo modo |
| ademais | além do mais · acresce que · acrescente-se |

---

## 5. Conjunções proibidas no texto canônico

Mesmo presentes no catálogo, evitar (`INDEX.informais_filtradas` lista equivalente):

- **"Aí"** como conjunção (registro informal)
- **"Daí"** isolado no início de oração formal (preferir "Daí que", "Daí decorre")
- **"Então"** como conector (substituir por "Portanto", "Por conseguinte")
- **"E aí"**, **"Mas tipo"**, **"Só que"** (oral)
- **"De forma que"** repetido em série (preferir "De modo que", "De maneira que", "Por forma a")

---

## 6. Checks operacionais por parágrafo

Aplicar antes de fechar parágrafo:

```
[1] Toda oração abre com conjunção?
[2] Primeira oração tem conjunção + conector com parágrafo anterior?
[3] Conjunções do parágrafo são todas distintas entre si?
[4] Nenhuma conjunção do parágrafo aparece no parágrafo imediatamente anterior?
[5] Janela de 5 parágrafos: nenhuma conjunção excede 2 ocorrências?
[6] Conjunções substituídas vieram da mesma família semântica?
[7] Distribuição é equidistante (não sequencial alfabética nem catalográfica)?
[8] Último período fecha na voz do autor (não citação solta)?
```

Falha em qualquer item = revisão antes de aceitar o parágrafo.

---

## 7. Interface programática (uso por validadores)

Validador automático que consome este guia + INDEX.json:

```python
# Pseudocódigo
for paragrafo in texto:
    for oracao in paragrafo.oracoes:
        if not oracao.starts_with_conjuncao():
            falha("oracao sem conjuncao de abertura")
    conjs = paragrafo.conjuncoes_de_abertura()
    if has_duplicates(conjs):
        falha("conjuncao repetida dentro do paragrafo")
    if intersect(conjs, paragrafo_anterior.conjs):
        falha("conjuncao repetida em paragrafos consecutivos")
    for conj in conjs:
        if count_in_window(conj, window=5) > 2:
            falha(f"frequencia excessiva de {conj} na janela de 5")
```

---

*Guia revisado em 2026-05-12. Versão 2.0: anatomia explícita do parágrafo (oração = unidade entre pontos finais; toda oração abre com conjunção), tabelas de substituição rápida, checks operacionais, interface para validador.*

---

## Proximidade semântica e distância entre conectores (v2.1)

Cada conector das famílias de conectores (anafóricos, elegantes,
metafóricos) carrega um **grupo semântico** (`grupo` no JSON) — o
conjunto dos seus quase-sinônimos ("nesse prumo" e "no mesmo prumo";
"de partida" e "de saída"). Os padrões produtivos usam o próprio
template como grupo ("Nesse retorno," e "Nessa construção," são o
mesmo molde com substantivo trocado).

**Escala de distância** entre dois conectores:

| d | Relação | Exemplo |
|---|---------|---------|
| d0 | mesma forma | "nessa toada" ↔ "nessa toada" |
| d1 | mesmo grupo (quase-sinônimos) | "nesse prumo" ↔ "no mesmo prumo" |
| d2 | mesma família, grupos distintos | "nessa toada" ↔ "sob essa lente" |
| d3 | famílias distintas | "nessa toada" ↔ "porquanto" |

**Regra de rotação (complementa a janela de frequência):** aberturas
de parágrafos consecutivos exigem **distância mínima d2** — vedada a
mesma forma (regra clássica) e vedado o mesmo grupo (quase-repetição,
que o leitor sente como eco: "Nesse retorno, … / Nessa construção, …").

**Regra de escolha (sorteio):** ao escolher um conector novo, buscar a
**máxima distância** disponível em relação ao último conector usado no
documento — preferir outra família; dentro da mesma família, outro
grupo; nunca o mesmo grupo do conector imediatamente anterior.
