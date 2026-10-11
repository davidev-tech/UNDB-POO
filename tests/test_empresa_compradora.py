def test_rn10_filtro_por_nome(comprador, marisqueira, produto):
    outro = marisqueira.cadastrar_produto(
        id_produto="P-401", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    assert produto in comprador.consultar_produtos(nome="Camarão")
    assert outro not in comprador.consultar_produtos(nome="Camarão")


def test_rn10_filtro_por_categoria(comprador, marisqueira):
    marisqueira.cadastrar_produto(
        id_produto="P-402", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    marisqueira.cadastrar_produto(
        id_produto="P-403", nome="Camarão", categoria="congelado",
        preco=45.0, quantidade_disponivel=30,
    )
    assert len(comprador.consultar_produtos(categoria="fresco")) == 1
    assert len(comprador.consultar_produtos(categoria="congelado")) == 1


def test_rn10_filtro_por_localizacao(comprador, marisqueira, outra_marisqueira):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-404", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    p2 = outra_marisqueira.cadastrar_produto(
        id_produto="P-405", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    resultado = comprador.consultar_produtos(localizacao="Vila Maresia, Raposa-MA")
    assert p1 in resultado
    assert p2 not in resultado


def test_rn10_filtro_por_empresa(comprador, marisqueira, outra_marisqueira):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-406", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    p2 = outra_marisqueira.cadastrar_produto(
        id_produto="P-407", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    assert p1 in comprador.consultar_produtos(empresa=marisqueira)
    assert p2 not in comprador.consultar_produtos(empresa=marisqueira)


def test_rn11_ordenar_por_menor_e_maior_preco(comprador, marisqueira):
    marisqueira.cadastrar_produto(
        id_produto="P-408", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    marisqueira.cadastrar_produto(
        id_produto="P-409", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    menores = comprador.consultar_produtos(ordenar_por="menor_preco")
    assert menores[0].preco <= menores[1].preco

    maiores = comprador.consultar_produtos(ordenar_por="maior_preco")
    assert maiores[0].preco >= maiores[1].preco


def test_rn12_comprador_ve_multiplas_empresas(comprador, marisqueira, outra_marisqueira):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-410", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    p2 = outra_marisqueira.cadastrar_produto(
        id_produto="P-411", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    assert p1 in comprador.consultar_produtos()
    assert p2 in comprador.consultar_produtos()


def test_comparar_produtos(comprador, marisqueira, outra_marisqueira):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-412", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    p2 = outra_marisqueira.cadastrar_produto(
        id_produto="P-413", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    assert comprador.comparar_produtos([p1, p2]) is not None


def test_comparar_lista_vazia(comprador):
    assert comprador.comparar_produtos([]) in ([], None, {})


def test_comparar_um_unico(comprador, produto):
    assert comprador.comparar_produtos([produto]) is not None