def email_ausente(email):
    """A1: True quando o e-mail veio nulo. O cliente é mantido e o e-mail fica None."""
    return email is None


def padronizar_estado(estado):
    """A2: devolve a sigla do estado em maiúsculas ("sp" vira "SP")."""
    return estado.upper()
