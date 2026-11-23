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
