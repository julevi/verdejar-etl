import json
from decimal import Decimal

from etl.carga import conectar, somar_valor_itens_no_banco
from etl.extracao import PASTA_BRUTOS
from etl.transformacao import transformar_pedidos


def pedidos_da_origem():
    """Transforma os pedidos salvos em brutos/ na última execução do ETL."""
    with open(PASTA_BRUTOS / "pedidos.json", encoding="utf-8") as arquivo:
        brutos = json.load(arquivo)
    pedidos, _itens, _contadores = transformar_pedidos(brutos)
    return pedidos


def test_contagem_de_pedidos_unicos_bate_com_o_banco():
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT count(*) FROM pedidos")
        contagem_destino = cursor.fetchone()[0]
    finally:
        conexao.close()

    assert len(pedidos_da_origem()) == contagem_destino


def test_soma_de_valor_itens_bate_com_o_banco():
    soma_origem = sum(p["valor_itens"] for p in pedidos_da_origem())
    soma_destino = somar_valor_itens_no_banco()

    assert abs(soma_origem - soma_destino) <= Decimal("0.01")


def consultar(sql):
    """Executa uma consulta e devolve todas as linhas."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conexao.close()


def test_vendas_por_mes_somam_o_total_geral():
    vendas_por_mes = consultar("""
        SELECT
            to_char(data_pedido, 'YYYY-MM') AS mes,
            sum(valor_itens) AS total_vendas
        FROM pedidos
        WHERE status <> 'cancelado'
        GROUP BY mes
        ORDER BY mes
    """)
    total_geral = consultar("""
        SELECT sum(valor_itens)
        FROM pedidos
        WHERE status <> 'cancelado'
    """)[0][0]

    soma_dos_meses = sum(total for _mes, total in vendas_por_mes)
    assert soma_dos_meses == total_geral
