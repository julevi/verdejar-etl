import sys

from etl.extracao import ErroExtracao, extrair_rota, ler_produtos, salvar_bruto


def main():
    try:
        clientes, paginas_clientes = extrair_rota("clientes")
        pedidos, paginas_pedidos = extrair_rota("pedidos")
        produtos = ler_produtos()
    except ErroExtracao as erro:
        sys.exit(f"erro na extracao: {erro}")

    salvar_bruto("clientes", clientes)
    salvar_bruto("pedidos", pedidos)

    print(f"extracao: clientes paginas={paginas_clientes} registros={len(clientes)}")
    print(f"extracao: pedidos paginas={paginas_pedidos} registros_brutos={len(pedidos)}")


if __name__ == "__main__":
    main()
