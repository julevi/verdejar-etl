import os

import pg8000.dbapi
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """Abre a conexão com o PostgreSQL usando as variáveis do .env."""
    return pg8000.dbapi.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def inserir_produtos(cursor, produtos):
    """Insere os produtos tratados na tabela produtos."""
    cursor.executemany(
        "INSERT INTO produtos (produto_id, nome, categoria, preco_base) VALUES (%s, %s, %s, %s)",
        [(p["produto_id"], p["nome"], p["categoria"], p["preco_base"]) for p in produtos],
    )


def inserir_clientes(cursor, clientes):
    """Insere os clientes tratados na tabela clientes."""
    cursor.executemany(
        "INSERT INTO clientes (id, nome, email, cidade, estado, cadastro_em) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        [
            (c["id"], c["nome"], c["email"], c["cidade"], c["estado"], c["cadastro_em"])
            for c in clientes
        ],
    )


def inserir_pedidos(cursor, pedidos):
    """Insere os pedidos tratados na tabela pedidos."""
    cursor.executemany(
        "INSERT INTO pedidos (id, cliente_id, data_pedido, status, valor_total, valor_itens, divergente) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        [
            (p["id"], p["cliente_id"], p["data_pedido"], p["status"],
             p["valor_total"], p["valor_itens"], p["divergente"])
            for p in pedidos
        ],
    )


def inserir_itens(cursor, itens):
    """Insere os itens na tabela itens_pedido."""
    cursor.executemany(
        "INSERT INTO itens_pedido (pedido_id, linha, produto_id, quantidade, preco_unitario) "
        "VALUES (%s, %s, %s, %s, %s)",
        [
            (i["pedido_id"], i["linha"], i["produto_id"], i["quantidade"], i["preco_unitario"])
            for i in itens
        ],
    )


def carregar(produtos, clientes, pedidos, itens):
    """Apaga os dados anteriores e grava as 4 tabelas em uma transação. Devolve as contagens."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()

        # Idempotência: apaga na ordem inversa das chaves estrangeiras
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM clientes")
        cursor.execute("DELETE FROM produtos")

        # Insere na ordem direta das chaves estrangeiras
        inserir_produtos(cursor, produtos)
        inserir_clientes(cursor, clientes)
        inserir_pedidos(cursor, pedidos)
        inserir_itens(cursor, itens)

        conexao.commit()

        # Contagens lidas do banco, depois do commit
        contagens = {}
        cursor.execute("SELECT count(*) FROM clientes")
        contagens["clientes"] = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM produtos")
        contagens["produtos"] = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM pedidos")
        contagens["pedidos"] = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM itens_pedido")
        contagens["itens"] = cursor.fetchone()[0]
        return contagens
    finally:
        conexao.close()


def somar_valor_itens_no_banco():
    """Reconciliação: devolve a soma de valor_itens gravada na tabela pedidos."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT sum(valor_itens) FROM pedidos")
        return cursor.fetchone()[0]
    finally:
        conexao.close()
