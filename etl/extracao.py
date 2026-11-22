import csv
import json
from pathlib import Path

import requests

URL_BASE = "http://127.0.0.1:8000"
RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_PRODUTOS = RAIZ / "insumos" / "dados" / "produtos.csv"
PASTA_BRUTOS = RAIZ / "brutos"


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


def salvar_bruto(nome, registros, pasta=PASTA_BRUTOS):
    """Grava os registros como vieram da API em <pasta>/<nome>.json."""
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"{nome}.json"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)
