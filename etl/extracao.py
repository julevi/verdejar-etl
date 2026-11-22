import requests

URL_BASE = "http://127.0.0.1:8000"


def extrair_rota(rota, page_size=50):
    """Busca todas as páginas de uma rota e devolve (registros, total_paginas)."""
    registros = []
    pagina = 1
    total_paginas = 1  # valor provisório: a primeira resposta traz o número real

    while pagina <= total_paginas:
        resposta = requests.get(
            f"{URL_BASE}/{rota}",
            params={"page": pagina, "page_size": page_size},
            timeout=10,
        )
        if resposta.status_code != 200:
            raise RuntimeError(
                f"GET /{rota} page={pagina} respondeu status {resposta.status_code}"
            )

        dados = resposta.json()
        registros.extend(dados["items"])
        total_paginas = dados["total_pages"]
        pagina += 1

    return registros, total_paginas


# Verificação temporária: sai daqui quando o main.py existir
if __name__ == "__main__":
    clientes, paginas = extrair_rota("clientes")
    print(f"extracao: clientes paginas={paginas} registros={len(clientes)}")
