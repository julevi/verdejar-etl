import csv
import sys
from pathlib import Path

import requests

URL_BASE = "http://127.0.0.1:8000"
RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_PRODUTOS = RAIZ / "insumos" / "dados" / "produtos.csv"


class ErroExtracao(Exception):
    """Falha ao buscar dados na API, com mensagem pronta para mostrar na tela."""


def extrair_rota(rota, page_size=50):
    """Busca todas as páginas de uma rota e devolve (registros, total_paginas)."""
    registros = []
    pagina = 1
    total_paginas = 1  # valor provisório: a primeira resposta traz o número real

    while pagina <= total_paginas:
        try:
            resposta = requests.get(
                f"{URL_BASE}/{rota}",
                params={"page": pagina, "page_size": page_size},
                timeout=10,
            )
        except requests.exceptions.ConnectionError as erro:
            raise ErroExtracao(
                f"não foi possível conectar em {URL_BASE}. "
                "Certifique-se de que a API está rodando."
            ) from erro
        except requests.exceptions.Timeout as erro:
            raise ErroExtracao(
                f"GET /{rota} page={pagina} demorou mais de 10 segundos"
            ) from erro

        # Só o 200 traz uma página completa; 204 ou 206 fariam o ETL perder dados
        if resposta.status_code != 200:
            raise ErroExtracao(
                f"GET /{rota} page={pagina} respondeu status {resposta.status_code}"
            )

        dados = resposta.json()
        registros.extend(dados["items"])
        total_paginas = dados["total_pages"]
        pagina += 1

    return registros, total_paginas


def ler_produtos(caminho=CAMINHO_PRODUTOS):
    """Lê o CSV de produtos e devolve uma lista de dicionários."""
    try:
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))
    except FileNotFoundError as erro:
        raise ErroExtracao(f"arquivo não encontrado: {caminho}") from erro


# Verificação temporária: sai daqui quando o main.py existir
if __name__ == "__main__":
    try:
        clientes, paginas_clientes = extrair_rota("clientes")
        pedidos, paginas_pedidos = extrair_rota("pedidos")
        produtos = ler_produtos()
    except ErroExtracao as erro:
        sys.exit(f"erro na extracao: {erro}")
    print(f"extracao: clientes paginas={paginas_clientes} registros={len(clientes)}")
    print(f"extracao: pedidos paginas={paginas_pedidos} registros_brutos={len(pedidos)}")
    print(f"produtos={len(produtos)}")
