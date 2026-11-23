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
