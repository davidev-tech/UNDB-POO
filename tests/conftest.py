import pytest
from marisqueiras import EmpresaMarisqueira, EmpresaCompradora


@pytest.fixture(autouse=True)
def limpar_registro():
    import marisqueiras
    marisqueiras._REGISTRO_PRODUTOS.clear()
    yield


@pytest.fixture
def marisqueira():
    return EmpresaMarisqueira(
        id_empresa_marisqueira="EM-01",
        CNPJ="00.000.000/0001-00",
        nome="Marisqueira da Vila",
        localizacao="Vila Maresia, Raposa-MA",
    )


@pytest.fixture
def outra_marisqueira():
    return EmpresaMarisqueira(
        id_empresa_marisqueira="EM-02",
        CNPJ="22.222.222/0001-22",
        nome="Outra Marisqueira",
        localizacao="Raposa-MA",
    )


@pytest.fixture
def comprador():
    return EmpresaCompradora(
        id_empresa_compradora="EC-01",
        CNPJ="11.111.111/0001-11",
        nome="Restaurante Maré",
        localizacao="São Luís-MA",
    )


@pytest.fixture
def produto(marisqueira):
    return marisqueira.cadastrar_produto(
        id_produto="P-001",
        nome="Camarão",
        categoria="fresco",
        preco=50.0,
        quantidade_disponivel=100,
    )


@pytest.fixture
def pedido(comprador):
    return comprador.realizar_pedido(
        id_pedido="PED-001",
        endereco_entrega="Rua A, 123",
        tempo_entrega="2 dias",
    )