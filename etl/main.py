import sys

from etl.carga import carregar, somar_valor_itens_no_banco
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

    contagens = carregar(produtos_tratados, clientes_tratados, pedidos_tratados, itens)
    print(
        f"carga: clientes={contagens['clientes']} produtos={contagens['produtos']} "
        f"pedidos={contagens['pedidos']} itens={contagens['itens']}"
    )

    soma_origem = sum(p["valor_itens"] for p in pedidos_tratados)
    soma_destino = somar_valor_itens_no_banco()
    print(
        f"reconciliacao: soma_valor_itens_origem={soma_origem} "
        f"soma_valor_itens_destino={soma_destino} "
        f"diferenca={soma_origem - soma_destino}"
    )
    print(f"divergentes: {contadores_pedidos['divergentes']} pedidos com valor_total diferente da soma dos itens")


if __name__ == "__main__":
    main()
