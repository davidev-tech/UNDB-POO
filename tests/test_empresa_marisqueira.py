import pytest


def test_rn08_alterar_quantidade(marisqueira, produto):
    marisqueira.alterar_quantidade(produto, 70)
    assert produto.quantidade_disponivel == 70


def test_rn08_alterar_quantidade_negativa(marisqueira, produto):
    with pytest.raises(ValueError):
        marisqueira.alterar_quantidade(produto, -5)


def test_rn19_empresa_sem_estoque_permanece_cadastrada(marisqueira, produto):
    marisqueira.alterar_quantidade(produto, 0)
    assert marisqueira.produtos
    assert produto in marisqueira.produtos


def test_p25_marisqueira_ve_apenas_proprios_produtos(marisqueira, outra_marisqueira):
    meu = marisqueira.cadastrar_produto(
        id_produto="P-201", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    outro = outra_marisqueira.cadastrar_produto(
        id_produto="P-202", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=30,
    )
    assert meu in marisqueira.produtos
    assert outro not in marisqueira.produtos