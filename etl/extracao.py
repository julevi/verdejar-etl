import requests

URL_BASE = "http://127.0.0.1:8000"

resposta = requests.get(
    f"{URL_BASE}/clientes",
    params={"page": 1, "page_size": 50},
    timeout=10,
)
dados = resposta.json()

print(f"status={resposta.status_code}")
print(f"itens={len(dados['items'])} total_pages={dados['total_pages']}")
