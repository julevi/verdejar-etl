from datetime import date, datetime
from decimal import Decimal


def email_ausente(email):
    """A1: True quando o e-mail veio nulo. O cliente é mantido e o e-mail fica None."""
    return email is None


def padronizar_estado(estado):
    """A2: devolve a sigla do estado em maiúsculas ("sp" vira "SP")."""
    return estado.upper()


def converter_data(texto):
    """A3: converte "AAAA-MM-DD" ou "DD/MM/AAAA" em date."""
    if "/" in texto:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    return date.fromisoformat(texto)


def converter_valor(valor):
    """A4: converte 125.84 ou "125,84" em Decimal com 2 casas."""
    texto = str(valor).replace(",", ".")
    return Decimal(texto).quantize(Decimal("0.01"))


def remover_repetidos(pedidos):
    """A5: mantém só a primeira ocorrência de cada id, na ordem original."""
    ids_vistos = set()
    unicos = []
    for pedido in pedidos:
        if pedido["id"] in ids_vistos:
            continue
        ids_vistos.add(pedido["id"])
        unicos.append(pedido)
    return unicos


def calcular_valor_itens(itens):
    """A6: soma quantidade × preco_unitario dos itens do pedido."""
    return sum(
        item["quantidade"] * converter_valor(item["preco_unitario"])
        for item in itens
    )


def pedido_divergente(valor_total, valor_itens):
    """A6: True quando a diferença entre os dois valores passa de 1 centavo."""
    return abs(valor_total - valor_itens) > Decimal("0.01")


def separar_itens(pedido):
    """Devolve os itens do pedido no formato de itens_pedido, com linha pela posição (1, 2, 3...)."""
    return [
        {
            "pedido_id": pedido["id"],
            "linha": linha,
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": converter_valor(item["preco_unitario"]),
        }
        for linha, item in enumerate(pedido["itens"], start=1)
    ]
