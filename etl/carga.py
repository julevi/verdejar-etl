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
