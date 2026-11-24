# verdejar-etl
Pipeline ETL em Python que extrai dados de uma API paginada e de um CSV, trata problemas de qualidade e carrega no PostgreSQL (Docker), com testes em pytest, reconciliação e idempotência. Desafio final do AI/R Fellowship AI-Driven Data Engineering.

## Estrutura

```
etl/
  extracao.py       API paginada, CSV de produtos e gravação dos brutos em brutos/
  transformacao.py  uma função por armadilha (A1 a A6) e transformação de cada tabela
  carga.py          conexão, inserts e carga idempotente no PostgreSQL
  main.py           executa o ETL e imprime os contadores
tests/
  test_transformacao.py  testes das armadilhas A1 a A6 e das transformações
  test_reconciliacao.py  origem × banco e teste de consulta
consultas_validacao.sql  vendas por mês, pedidos por estado e pedidos divergentes
CONTRATO_DE_DADOS.md     campos, tipos, nulos e regras de cada tabela
COMO_USEI_IA.md          registro do uso de IA
```

## Como rodar

Comandos para Windows (PowerShell), a partir da raiz do projeto.

**1. Ambiente Python**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

Preencha o `.env` com os dados do banco (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

**2. Banco: PostgreSQL 16 em Docker**

```powershell
docker run --name verdejar-pg -e POSTGRES_PASSWORD=<senha> -e POSTGRES_DB=verdejar -p 5432:5432 -d postgres:16
Get-Content insumos/schema.sql | docker exec -i verdejar-pg psql -U postgres -d verdejar
```

Nas próximas vezes, basta `docker start verdejar-pg`. O banco leva alguns segundos para aceitar conexões depois de iniciar.

**3. API local** (em outro terminal)

```powershell
python insumos/api_verdejar.py --dados insumos/dados
```

**4. ETL, testes e consultas**

```powershell
python -m etl.main
python -m pytest
Get-Content consultas_validacao.sql | docker exec -i verdejar-pg psql -U postgres -d verdejar
```

Os testes de reconciliação leem o banco e o `brutos/pedidos.json`, então o ETL precisa ter rodado antes.

## Banco e biblioteca de conexão

- **Caminho B:** PostgreSQL 16 em Docker, com o `insumos/schema.sql` sem alterações.
- **Biblioteca:** `pg8000` (módulo `pg8000.dbapi`), com parâmetros `%s` em todas as consultas.
- **Por que não `psycopg[binary]`:** o Smart App Control do Windows bloqueia a DLL do libpq usada pelo psycopg. Em vez de desligar a proteção, troquei para o `pg8000`, que é 100% Python.
- O `insumos/schema_sqlite.sql` foi removido, porque o projeto não usa o caminho C (SQLite).

## Idempotência

A carga apaga e regrava as quatro tabelas em uma única transação:

1. `DELETE` na ordem inversa das chaves estrangeiras: `itens_pedido`, `pedidos`, `clientes`, `produtos`.
2. `INSERT` na ordem direta: `produtos`, `clientes`, `pedidos`, `itens_pedido`.
3. Um único `commit` no fim. Se algo falhar no meio, nada é gravado e o banco continua como estava.

As contagens da linha `carga:` são lidas do banco depois do `commit`, com um `SELECT count(*)` por tabela.

Duas execuções seguidas dão o mesmo resultado, sem erro de chave duplicada:

```
(1ª execução)
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455

(2ª execução)
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
```

## Decisões

| Tema | Decisão | Motivo |
|---|---|---|
| Status HTTP na extração | Só o 200 é aceito; qualquer outro interrompe com mensagem clara | Só o 200 traz uma página completa. Um 204 ou 206 faria o ETL perder dados sem perceber |
| A1 (e-mail) | Só `null` conta como ausente | O desafio define a A1 como valor nulo, e os dados não têm e-mail vazio ou só com espaços |
| Contadores | Contam só o que a armadilha corrigiu: estados que estavam minúsculos, datas `DD/MM/AAAA` e valores que vieram como texto | O número mostra quantos registros vieram com problema |
| Base dos contadores | Datas, valores e divergentes são contados só entre os pedidos únicos, depois da A5 | Os contadores descrevem o que vai para o banco, e o repetido já aparece em `repetidos_descartados` |
| `linha` em `itens_pedido` | Gerada pela posição do item no pedido (1, 2, 3...) | O schema exige a coluna, e ela não existe nos dados |
| Valores em dinheiro | `Decimal`, nunca `float` | O `float` acumula erro de arredondamento, e a reconciliação exige diferença zero |
| Vendas por mês | Soma `valor_itens` e exclui pedidos `cancelado` | `valor_itens` é o valor reconciliado com a origem; `valor_total` tem as divergências da A6. Pedido cancelado não gerou venda. O teste de consulta usa o mesmo filtro |
| Pedidos por estado | Inclui todos os status | A pergunta é sobre pedidos, não sobre vendas |
| Desempenho da carga | Inserts com `executemany`, um registro por vez | Prioridade para código simples.|

## Resultados

**Saída do ETL**

```
extracao: clientes paginas=20 registros=1000
extracao: pedidos paginas=102 registros_brutos=5100
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: emails_nulos=81 estados_padronizados=151 datas_convertidas=1037 valores_convertidos=1255
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
reconciliacao: soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```

**Testes (pytest)**

```
============================= 20 passed in 0.57s ==============================
```

São 20 testes: 17 de transformação (as seis armadilhas, a separação dos itens e a transformação de cada tabela), 2 de reconciliação (contagem de pedidos e soma de `valor_itens`, origem × banco) e 1 teste de consulta (a soma das vendas por mês é igual à soma geral, com o mesmo filtro).

**Consultas de validação**

(a) Vendas por mês

```
   mes   | total_vendas 
---------+--------------
 2026-01 |     24251.65
 2026-02 |     26798.74
 2026-03 |     23421.23
 2026-04 |     24706.39
 2026-05 |     24838.16
 2026-06 |     24897.33
 2026-07 |     26088.25
 2026-08 |     24271.32
 2026-09 |     24251.68
 2026-10 |     23937.57
(10 rows)
```

Teste de consulta: a soma dos 10 meses é igual à soma geral da tabela, com o mesmo filtro (sem pedidos `cancelado`).

```
 total_geral 
-------------
   247462.32
(1 row)
```

Soma dos 10 meses: 247462.32 · Soma geral: 247462.32 · Diferença: 0.00

(b) Pedidos por estado

```
 estado | quantidade_pedidos 
--------+--------------------
 RS     |               1543
 SC     |               1127
 PR     |                974
 SP     |                880
 MG     |                476
(5 rows)
```

(c) Pedidos divergentes: a consulta lista os 238 pedidos com `id`, `valor_total`, `valor_itens` e a diferença. A conferência abaixo bate com a linha `divergentes:` do ETL.

```
 total_divergentes 
-------------------
               238
(1 row)
```

## Uso de IA

O registro de como usei IA neste projeto (sugestões aceitas, rejeitadas e falhas) está em [COMO_USEI_IA.md](COMO_USEI_IA.md).
