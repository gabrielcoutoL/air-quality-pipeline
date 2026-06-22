# Desafio — Pipeline de Qualidade do Ar (foco em Pandera)

Mini-projeto de Engenharia de Dados para praticar: **ingestão → validação (Pandera) →
transformação (pandas) → carga (SQLAlchemy Core + Postgres no Docker)**.

Domínio: **rede de monitoramento de qualidade do ar** (sensores IoT ambientais).

> Este README é o "contrato" dos dados: tipos pretendidos, categorias permitidas e
> faixas esperadas. A **sujeira foi plantada de propósito** — os dados NÃO seguem este
> contrato. Seu trabalho é escrever schemas Pandera que detectem as violações e um
> transform que as corrija.

---

## Arquivos e relacionamentos

```
limites_parametro.csv   (referência, LIMPA)
        ▲ parametro
        │
estacoes.csv  ◄──estacao_id──  sensores.csv  ◄──sensor_id──  leituras.csv
 (dimensão)                      (FK estacoes)                 (FK sensores)
```

- `leituras.sensor_id`  → `sensores.sensor_id`
- `sensores.estacao_id` → `estacoes.estacao_id`
- `sensores.parametro`  → `limites_parametro.parametro` (e, por transitividade, as leituras)

Volume aproximado: 26 estações, 86 sensores, ~2.650 leituras, 6 parâmetros.

---

## Dicionário de dados (schema PRETENDIDO / limpo)

### estacoes.csv
| coluna | tipo | nulo? | regra |
|---|---|---|---|
| estacao_id | str | não | PK, único, padrão `E\d{3}` |
| nome | str | sim | atributo |
| cidade | str | não | livre, mas normalizar caixa/espaços |
| uf | str | não | 2 letras maiúsculas |
| latitude | float | não | faixa global [-90, 90]; Brasil ≈ [-34, 6] |
| longitude | float | não | faixa global [-180, 180]; Brasil ≈ [-74, -34] |
| data_instalacao | date | não | não pode ser futura |
| status | categoria | não | ∈ {`ativa`, `inativa`, `manutencao`} |

### sensores.csv
| coluna | tipo | nulo? | regra |
|---|---|---|---|
| sensor_id | str | não | PK, único, padrão `S\d{4}` |
| estacao_id | str | não | FK → estacoes |
| parametro | categoria | não | ∈ {`PM25`,`PM10`,`NO2`,`O3`,`SO2`,`CO`} |
| unidade | categoria | não | ∈ {`ug/m3`, `mg/m3`}; deve bater com `limites_parametro.unidade_esperada` |
| data_calibracao | date | sim | — |

### leituras.csv
| coluna | tipo | nulo? | regra |
|---|---|---|---|
| leitura_id | str | não | PK, único, padrão `L\d{6}` |
| sensor_id | str | não | FK → sensores |
| timestamp | datetime | não | não pode ser futura |
| valor | float | não | ≥ 0 e dentro de [valor_min, valor_max] do parâmetro |
| flag_qualidade | categoria | não | ∈ {`valida`, `suspeita`, `invalida`} |

### limites_parametro.csv (LIMPA — fonte de verdade)
| coluna | tipo | regra |
|---|---|---|
| parametro | str | PK |
| valor_min | float | piso válido |
| valor_max | float | teto válido |
| unidade_esperada | str | unidade canônica do parâmetro |

---

## Sujeira plantada (categorias — você descobre as linhas)

**estacoes.csv**
- 1 duplicata EXATA (linha inteira repetida).
- `cidade`/`uf` com caixa e espaços inconsistentes (ex.: `rio de janeiro`, `SALVADOR`, `Curitiba `, ` BA`, `mg`).
- `nome` com nulo e com espaços sobrando.
- `latitude` nula em 1 linha.
- coordenadas fora de faixa: latitude > 90, longitude < -180, e 1 longitude válida no mundo mas fora do Brasil.
- `status` com categorias inválidas/caixa/acento/espaço (`ativo`, `ATIVA`, `manutenção`, `desativada`, ` inativa`).
- `data_instalacao` em formato misto (`DD/MM/YYYY` vs ISO) e 1 data no futuro.

**sensores.csv**
- 2 FKs órfãs (`estacao_id` inexistente) + 1 FK nula.
- `parametro` fora do conjunto / caixa (`PM2.5`, `pm10`, `Ozonio`, `no2`, `Co`).
- `sensor_id` duplicado (viola unicidade da PK).
- `unidade` inconsistente (`µg/m³` vs `ug/m3`, espaço sobrando) e 1 sensor de CO com unidade incompatível.
- `data_calibracao` em formato misto + 1 nula.

**leituras.csv**
- 5 FKs órfãs (`sensor_id` inexistente).
- 5 duplicatas EXATAS.
- `valor`: 10 negativos, 10 nulos, 6 sentinelas (99999), 15 com vírgula decimal (string), e ~8 que violam a faixa específica do parâmetro (passam numa sanidade global, mas excedem o limite do parâmetro — só pegam após merge com `limites_parametro`).
- `flag_qualidade` fora do conjunto / caixa / acento / vazio (`válida`, `VALIDA`, `ok`, `n/a`, ``, ...).
- `timestamp` em formato misto, alguns no futuro, alguns nulos.

`limites_parametro.csv` está limpa de propósito (é a referência).

---

## Etapas do desafio

1. **Ingestão** — ler os 4 arquivos, tipar com cuidado (decida o que tipar na leitura vs. depois).
2. **Validação (Pandera)** — schemas declarativos por tabela; tipos, `nullable`, `unique`,
   `coerce`, ranges com `Check`, categorias com `Check.isin`, regex, checks customizados
   (inclusive cross-column após o merge); validação na entrada e na saída do transform;
   estratégia para linhas inválidas (lazy validation + coletar erros vs. falhar).
3. **Transformação (pandas)** — normalizar caixa/espaços, converter tipos (vírgula decimal,
   datas multi-formato), deduplicar, resolver FKs órfãs (merge com `indicator`), enriquecer
   (juntar parâmetro/limite/cidade) e marcar/derivar qualidade.
4. **Carga (SQLAlchemy Core)** — schema com `MetaData`/`Table`, PK/FK/índices; idempotência
   por **TRUNCATE full-refresh** OU **UPSERT** (você escolhe e justifica).
5. **Docker** — `docker-compose` com Postgres (volume, healthcheck, `.env`) + container do pipeline.

## Perguntas de negócio (responder com SQL e/ou pandas no fim)
1. Top 5 cidades por concentração média de PM25 (após normalizar cidade).
2. Quantas estações por `status` (após canonicalizar)?
3. Para cada parâmetro: % de leituras fora da faixa válida (KPI de qualidade).
4. Nº de leituras válidas por estação por dia (exige timestamp parseado).
5. Quantas FKs órfãs foram descartadas em cada relação (KPI de integridade)?
6. Qual estação tem a maior proporção de leituras não-`valida`?