from datetime import date
from decimal import Decimal

from etl.transformacao import converter_data, converter_valor, email_ausente, padronizar_estado


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
