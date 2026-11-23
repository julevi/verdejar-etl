import sys

from etl.extracao import ErroExtracao, extrair_rota, ler_produtos, salvar_bruto
from etl.transformacao import transformar_clientes, transformar_pedidos, transformar_produtos


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

    clientes_tratados, contadores_clientes = transformar_clientes(clientes)
    pedidos_tratados, itens, contadores_pedidos = transformar_pedidos(pedidos)
    produtos_tratados = transformar_produtos(produtos)

    print(
        f"transformacao: pedidos_unicos={contadores_pedidos['pedidos_unicos']} "
        f"repetidos_descartados={contadores_pedidos['repetidos_descartados']}"
    )
    print(
        f"transformacao: emails_nulos={contadores_clientes['emails_nulos']} "
        f"estados_padronizados={contadores_clientes['estados_padronizados']} "
        f"datas_convertidas={contadores_pedidos['datas_convertidas']} "
        f"valores_convertidos={contadores_pedidos['valores_convertidos']}"
    )


if __name__ == "__main__":
    main()
