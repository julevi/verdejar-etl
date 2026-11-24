# Contrato de dados

Este documento descreve o que o ETL entrega em cada tabela do PostgreSQL (`insumos/schema.sql`): tipo, se o campo aceita nulo, de onde ele vem e a regra aplicada.

## Origens

| Origem | Formato | Registros |
|---|---|---|
| API `GET /clientes` | JSON paginado | 1000 clientes |
| API `GET /pedidos` | JSON paginado, com `itens` aninhados em cada pedido | mais de 5000 registros brutos, 5000 pedidos únicos |
| `insumos/dados/produtos.csv` | CSV com cabeçalho; todos os campos chegam como texto | 12 produtos |

Os registros da API são gravados sem alteração em `brutos/clientes.json` e `brutos/pedidos.json` antes de qualquer transformação.

## Tabela `clientes`

| Campo | Tipo | Nulo | Origem | Regra |
|---|---|---|---|---|
| `id` | INTEGER (PK) | não | `id` | sem alteração |
| `nome` | TEXT | não | `nome` | sem alteração |
| `email` | TEXT | **sim** | `email` | **A1:** quando vier `null`, o cliente é mantido e o campo é gravado como NULL. Contador: `emails_nulos` |
| `cidade` | TEXT | não | `cidade` | sem alteração |
| `estado` | CHAR(2) | não | `estado` | **A2:** convertido para maiúsculas (`"sp"` → `"SP"`). Contador: `estados_padronizados`, só os que mudaram |
| `cadastro_em` | DATE | não | `cadastro_em` | já chega como AAAA-MM-DD; convertido para data |

## Tabela `produtos`

| Campo | Tipo | Nulo | Origem | Regra |
|---|---|---|---|---|
| `produto_id` | INTEGER (PK) | não | `produto_id` | texto convertido para inteiro |
| `nome` | TEXT | não | `nome` | sem alteração |
| `categoria` | TEXT | não | `categoria` | sem alteração |
| `preco_base` | NUMERIC(10,2) | não | `preco_base` | texto convertido para `Decimal` com 2 casas |

## Tabela `pedidos`

| Campo | Tipo | Nulo | Origem | Regra |
|---|---|---|---|---|
| `id` | INTEGER (PK) | não | `id` | **A5:** o mesmo pedido pode vir repetido entre as páginas. Fica a primeira ocorrência de cada `id`. Contadores: `pedidos_unicos` e `repetidos_descartados` |
| `cliente_id` | INTEGER (FK → `clientes.id`) | não | `cliente_id` | sem alteração |
| `data_pedido` | DATE | não | `data_pedido` | **A3:** chega como `AAAA-MM-DD` ou `DD/MM/AAAA`; os dois viram data. Contador: `datas_convertidas`, só as `DD/MM/AAAA` |
| `status` | TEXT | não | `status` | sem alteração; valores: `entregue`, `em_transporte`, `cancelado` |
| `valor_total` | NUMERIC(12,2) | não | `valor_total` | **A4:** chega como número (`125.84`) ou texto com vírgula (`"125,84"`); os dois viram `Decimal` com 2 casas. Contador: `valores_convertidos`, só os que vieram como texto |
| `valor_itens` | NUMERIC(12,2) | não | calculado | **A6:** soma de `quantidade × preco_unitario` dos itens do pedido |
| `divergente` | BOOLEAN | não | calculado | **A6:** `true` quando `|valor_total − valor_itens| > 0,01`. Contador: `divergentes` |

## Tabela `itens_pedido`

| Campo | Tipo | Nulo | Origem | Regra |
|---|---|---|---|---|
| `pedido_id` | INTEGER (PK, FK → `pedidos.id`) | não | `id` do pedido | vem do pedido em que o item está aninhado |
| `linha` | INTEGER (PK) | não | **gerado** | o campo não existe nos dados; é a posição do item na lista `itens`, começando em 1 |
| `produto_id` | INTEGER (FK → `produtos.produto_id`) | não | `itens[].produto_id` | sem alteração |
| `quantidade` | INTEGER | não | `itens[].quantidade` | sem alteração |
| `preco_unitario` | NUMERIC(10,2) | não | `itens[].preco_unitario` | convertido para `Decimal` com 2 casas |

## Regras gerais

- **Valores em dinheiro usam `Decimal`, nunca `float`.** O `float` acumula erros de arredondamento na soma (`0.1 + 0.2` dá `0.30000000000000004`), e a reconciliação exige diferença zero. Números vindos do JSON são convertidos com `Decimal(str(valor))`.
- **Nenhum registro é descartado**, exceto as repetições de pedido (A5). E-mail nulo e valor divergente são mantidos e contados.
- **Ordem da carga:** produtos, clientes, pedidos, itens_pedido, para respeitar as chaves estrangeiras.
