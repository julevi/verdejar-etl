from datetime import date
from decimal import Decimal

from etl.transformacao import (
    calcular_valor_itens,
    converter_data,
    converter_valor,
    email_ausente,
    padronizar_estado,
    pedido_divergente,
    remover_repetidos,
)


def test_email_ausente_quando_nulo():
    assert email_ausente(None) is True


def test_email_ausente_quando_preenchido():
    assert email_ausente("ana@exemplo.com") is False


def test_padronizar_estado_minusculo():
    assert padronizar_estado("sp") == "SP"


def test_padronizar_estado_ja_maiusculo():
    assert padronizar_estado("SP") == "SP"


def test_converter_data_formato_iso():
    assert converter_data("2026-02-19") == date(2026, 2, 19)


def test_converter_data_formato_brasileiro():
    assert converter_data("19/02/2026") == date(2026, 2, 19)


def test_converter_valor_texto_com_virgula():
    assert converter_valor("125,84") == Decimal("125.84")


def test_converter_valor_numero():
    assert converter_valor(125.84) == Decimal("125.84")


def test_remover_repetidos_descarta_id_repetido():
    pedidos = [{"id": 1}, {"id": 2}, {"id": 1}]
    assert [p["id"] for p in remover_repetidos(pedidos)] == [1, 2]


def test_remover_repetidos_mantem_primeira_ocorrencia():
    pedidos = [{"id": 1, "origem": "primeira"}, {"id": 1, "origem": "segunda"}]
    assert remover_repetidos(pedidos) == [{"id": 1, "origem": "primeira"}]


def test_calcular_valor_itens_soma_em_decimal():
    itens = [
        {"produto_id": 2, "quantidade": 3, "preco_unitario": 4.3},
        {"produto_id": 9, "quantidade": 2, "preco_unitario": 1.1},
    ]
    assert calcular_valor_itens(itens) == Decimal("15.10")


def test_pedido_divergente_quando_diferenca_passa_de_um_centavo():
    assert pedido_divergente(Decimal("125.84"), Decimal("120.84")) is True


def test_pedido_nao_divergente_com_diferenca_de_um_centavo():
    assert pedido_divergente(Decimal("10.01"), Decimal("10.00")) is False
