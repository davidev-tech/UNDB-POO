import pytest

from marisqueiras import (
    EmpresaCompradora,
    EmpresaMarisqueira,
    CategoriaProduto,
)


@pytest.fixture
def marisqueira():
    """Marisqueira sempre aberta (para status_visual não atrapalhar)."""
    return EmpresaMarisqueira(
        nome="Marisqueira da Vila",
        localizacao="Raposa - MA",
        responsavel="Dona Maria",
        horario_funcionamento=(0, 24),
    )


@pytest.fixture
def marisqueira_b():
    return EmpresaMarisqueira(
        nome="Marisqueira B",
        localizacao="São Luís - MA",
        responsavel="Sr. Pedro",
        horario_funcionamento=(0, 24),
    )


@pytest.fixture
def compradora():
    return EmpresaCompradora(
        nome="Restaurante Maré",
        localizacao="São Luís - MA",
        responsavel="Sr. João",
        horario_funcionamento=(8, 22),
    )


@pytest.fixture
def produto_fresco(marisqueira):
    return marisqueira.cadastrar_produto(
        "Camarão", CategoriaProduto.FRESCO, 40.0, 100
    )


@pytest.fixture
def produto_congelado(marisqueira):
    return marisqueira.cadastrar_produto(
        "Camarão", CategoriaProduto.CONGELADO, 35.0, 80
    )