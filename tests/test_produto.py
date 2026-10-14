import pytest

from marisqueiras import CategoriaProduto


class TestCadastroProduto:
    """P15, P16, P18, RN06."""

    def test_p15_foto_opcional(self, marisqueira):
        p = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
        assert p.foto is None

    def test_preco_obrigatorio_positivo(self, marisqueira):
        with pytest.raises(ValueError):
            marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 0, 100)

    def test_rn06_fresco_congelado_distintos(self, marisqueira):
        p1 = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
        p2 = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.CONGELADO, 35.0, 100)
        assert p1 is not p2
        assert len(marisqueira.produtos) == 2

    def test_rn06_duplicado_mesma_categoria(self, marisqueira):
        from marisqueiras import RegraNegocioError
        marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
        with pytest.raises(RegraNegocioError):
            marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 42.0, 50)

    def test_cadastro_com_menos_de_25_kg_permitido(self, marisqueira):
        """RN05 é regra de venda, não de cadastro."""
        p = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 10)
        assert p.quantidade_disponivel == 10

    def test_cadastro_com_zero_kg_permitido(self, marisqueira):
        """RN09 / P20: produto pode ser cadastrado como indisponível."""
        p = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 0)
        assert not p.esta_disponivel()


class TestAlterarQuantidade:
    """RN08, RN09, P19, P20."""

    def test_alterar_estoque(self, marisqueira, produto_fresco):
        marisqueira.alterar_quantidade(produto_fresco, 50)
        assert produto_fresco.quantidade_disponivel == 50

    def test_zerar_estoque_produto_permanece(self, marisqueira, produto_fresco):
        marisqueira.alterar_quantidade(produto_fresco, 0)
        assert produto_fresco.quantidade_disponivel == 0
        assert not produto_fresco.esta_disponivel()
        assert produto_fresco in marisqueira.produtos

    def test_quantidade_negativa(self, marisqueira, produto_fresco):
        with pytest.raises(ValueError):
            marisqueira.alterar_quantidade(produto_fresco, -5)

    def test_produto_de_outra_empresa(self, marisqueira, marisqueira_b, produto_fresco):
        from marisqueiras import RegraNegocioError
        with pytest.raises(RegraNegocioError):
            marisqueira_b.alterar_quantidade(produto_fresco, 50)