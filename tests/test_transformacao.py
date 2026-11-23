from etl.transformacao import email_ausente, padronizar_estado


def test_email_ausente_quando_nulo():
    assert email_ausente(None) is True


def test_email_ausente_quando_preenchido():
    assert email_ausente("ana@exemplo.com") is False


def test_padronizar_estado_minusculo():
    assert padronizar_estado("sp") == "SP"


def test_padronizar_estado_ja_maiusculo():
    assert padronizar_estado("SP") == "SP"
