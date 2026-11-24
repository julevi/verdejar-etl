-- (a) Total de vendas por mês
-- Soma valor_itens (valor reconciliado) e exclui pedidos cancelados
SELECT
    to_char(data_pedido, 'YYYY-MM') AS mes,
    sum(valor_itens) AS total_vendas
FROM pedidos
WHERE status <> 'cancelado'
GROUP BY mes
ORDER BY mes;

-- Teste de consulta da (a): a soma geral, com o mesmo filtro, deve ser igual à soma dos meses
SELECT sum(valor_itens) AS total_geral
FROM pedidos
WHERE status <> 'cancelado';


-- (b) Quantidade de pedidos por estado
-- Inclui todos os status: a pergunta é sobre pedidos, não sobre vendas
SELECT
    c.estado,
    count(*) AS quantidade_pedidos
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
GROUP BY c.estado
ORDER BY quantidade_pedidos DESC;


-- (c) Pedidos divergentes (A6): valor_total difere de valor_itens em mais de 1 centavo
SELECT
    id,
    valor_total,
    valor_itens,
    valor_total - valor_itens AS diferenca
FROM pedidos
WHERE divergente
ORDER BY id;

-- Conferência: deve bater com a linha "divergentes:" do ETL
SELECT count(*) AS total_divergentes
FROM pedidos
WHERE divergente;
