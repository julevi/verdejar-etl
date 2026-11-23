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
    separar_itens,
    transformar_clientes,
    transformar_pedidos,
    transformar_produtos,
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


def test_separar_itens_gera_linha_pela_posicao():
    pedido = {
        "id": 7,
        "itens": [
            {"produto_id": 2, "quantidade": 3, "preco_unitario": 4.3},
            {"produto_id": 9, "quantidade": 1, "preco_unitario": 15.86},
        ],
    }
    assert separar_itens(pedido) == [
        {"pedido_id": 7, "linha": 1, "produto_id": 2, "quantidade": 3, "preco_unitario": Decimal("4.30")},
        {"pedido_id": 7, "linha": 2, "produto_id": 9, "quantidade": 1, "preco_unitario": Decimal("15.86")},
    ]


def test_transformar_clientes_conta_emails_nulos_e_estados_padronizados():
    clientes = [
        {"id": 1, "nome": "Ana", "email": None, "cidade": "Campinas", "estado": "sp", "cadastro_em": "2025-04-04"},
        {"id": 2, "nome": "Bia", "email": "bia@exemplo.com", "cidade": "Curitiba", "estado": "PR", "cadastro_em": "2025-05-10"},
    ]
    tratados, contadores = transformar_clientes(clientes)

    assert contadores == {"emails_nulos": 1, "estados_padronizados": 1}
    assert tratados[0]["email"] is None
    assert tratados[0]["estado"] == "SP"
    assert tratados[0]["cadastro_em"] == date(2025, 4, 4)


def test_transformar_pedidos_aplica_armadilhas_e_conta():
    item = {"produto_id": 1, "quantidade": 1, "preco_unitario": 10.0}
    brutos = [
        {"id": 1, "cliente_id": 5, "data_pedido": "19/02/2026", "status": "entregue", "valor_total": "10,00", "itens": [item]},
        {"id": 1, "cliente_id": 5, "data_pedido": "19/02/2026", "status": "entregue", "valor_total": "10,00", "itens": [item]},
        {"id": 2, "cliente_id": 6, "data_pedido": "2026-02-20", "status": "cancelado", "valor_total": 15.0, "itens": [item]},
    ]
    pedidos, itens, contadores = transformar_pedidos(brutos)

    assert contadores == {
        "pedidos_unicos": 2,
        "repetidos_descartados": 1,
        "datas_convertidas": 1,
        "valores_convertidos": 1,
        "divergentes": 1,
    }
    assert pedidos[0]["data_pedido"] == date(2026, 2, 19)
    assert pedidos[0]["valor_total"] == Decimal("10.00")
    assert pedidos[1]["divergente"] is True
    assert len(itens) == 2


def test_transformar_produtos_converte_tipos_do_csv():
    produtos = [{"produto_id": "1", "nome": "Alface crespa", "categoria": "folhas", "preco_base": "3.5"}]
    assert transformar_produtos(produtos) == [
        {"produto_id": 1, "nome": "Alface crespa", "categoria": "folhas", "preco_base": Decimal("3.50")}
    ]
