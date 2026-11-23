from etl.transformacao import email_ausente


def test_email_ausente_quando_nulo():
    assert email_ausente(None) is True


def test_email_ausente_quando_preenchido():
    assert email_ausente("ana@exemplo.com") is False
