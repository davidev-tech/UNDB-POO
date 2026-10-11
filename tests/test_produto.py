import pytest
from marisqueiras import Produto


def test_p15_cadastro_completo_exceto_fotografia(marisqueira):
    p = marisqueira.cadastrar_produto(
        id_produto="P-001",
        nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=25,
    )
    assert isinstance(p, Produto)
    assert p.id_produto == "P-001"
    assert p.nome == "Ostra"
    assert p.categoria == "fresco"
    assert p.fotografia is None


def test_p15_campos_obrigatorios_exceto_fotografia(marisqueira):
    with pytest.raises((TypeError, ValueError)):
        marisqueira.cadastrar_produto(
            id_produto="P-002", nome="Ostra", categoria="fresco", preco=30.0,
        )
    with pytest.raises((TypeError, ValueError)):
        marisqueira.cadastrar_produto(
            id_produto="P-003", nome="Ostra", preco=30.0, quantidade_disponivel=30,
        )


def test_rn05_minimo_25kg_cadastro(marisqueira):
    with pytest.raises(ValueError):
        marisqueira.cadastrar_produto(
            id_produto="P-004", nome="Ostra", categoria="fresco",
            preco=30.0, quantidade_disponivel=24,
        )


def test_rn06_fresco_e_congelado_diferentes(marisqueira):
    f = marisqueira.cadastrar_produto(
        id_produto="P-101", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    c = marisqueira.cadastrar_produto(
        id_produto="P-102", nome="Camarão", categoria="congelado",
        preco=45.0, quantidade_disponivel=30,
    )
    assert f != c
    assert f.categoria != c.categoria


def test_rn08_alterar_quantidade(marisqueira, produto):
    marisqueira.alterar_quantidade(produto, 80)
    assert produto.quantidade_disponivel == 80


def test_rn08_alterar_quantidade_negativa(marisqueira, produto):
    with pytest.raises(ValueError):
        marisqueira.alterar_quantidade(produto, -1)


def test_rn09_produto_zerado_permanece(marisqueira, produto):
    marisqueira.alterar_quantidade(produto, 0)
    assert produto in marisqueira.produtos
    assert produto.verificar_disponibilidade() is False


def test_verificar_disponibilidade_por_quantidade(produto):
    assert produto.verificar_disponibilidade(25) is True
    assert produto.verificar_disponibilidade(100) is True
    assert produto.verificar_disponibilidade(101) is False


def test_atualizar_quantidade_direto_no_produto(produto):
    produto.atualizar_quantidade(80)
    assert produto.quantidade_disponivel == 80


def test_atualizar_quantidade_negativa(produto):
    with pytest.raises(ValueError):
        produto.atualizar_quantidade(-1)