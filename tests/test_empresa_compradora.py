import pytest

from marisqueiras import (
    CategoriaProduto,
    EstoqueInsuficienteError,
    QuantidadeMinimaError,
    RegraNegocioError,
)


class TestConsulta:
    """RN10, RN11, P9, P21, P22, P25."""

    def test_p25_marisqueira_ve_somente_proprios(self, marisqueira, marisqueira_b, produto_fresco):
        marisqueira_b.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 38.0, 100)
        assert len(marisqueira.consultar_proprios_produtos()) == 1
        assert produto_fresco in marisqueira.consultar_proprios_produtos()

    def test_filtro_por_nome(self, compradora, marisqueira, produto_fresco, produto_congelado):
        r = compradora.consultar_produtos(marisqueira.produtos, nome="camarão")
        assert len(r) == 2

    def test_filtro_por_categoria(self, compradora, marisqueira, produto_fresco, produto_congelado):
        r = compradora.consultar_produtos(
            marisqueira.produtos, categoria=CategoriaProduto.CONGELADO
        )
        assert r == [produto_congelado]

    def test_filtro_por_localizacao(self, compradora, marisqueira, produto_fresco):
        r = compradora.consultar_produtos(
            marisqueira.produtos, localizacao="Raposa - MA"
        )
        assert produto_fresco in r

    def test_filtro_por_empresa(self, compradora, marisqueira, marisqueira_b, produto_fresco):
        produto_b = marisqueira_b.cadastrar_produto(
            "Camarão", CategoriaProduto.FRESCO, 38.0, 100
        )
        todos = marisqueira.produtos + marisqueira_b.produtos
        r = compradora.consultar_produtos(todos, empresa_marisqueira=marisqueira_b)
        assert r == [produto_b]

    def test_ordenar_menor_preco(self, compradora, marisqueira, produto_fresco, produto_congelado):
        r = compradora.consultar_produtos(marisqueira.produtos, ordenar_por="menor_preco")
        assert r[0].preco == 35.0

    def test_ordenar_maior_preco(self, compradora, marisqueira, produto_fresco, produto_congelado):
        r = compradora.consultar_produtos(marisqueira.produtos, ordenar_por="maior_preco")
        assert r[0].preco == 40.0

    def test_ordenacao_invalida(self, compradora, marisqueira, produto_fresco):
        with pytest.raises(ValueError):
            compradora.consultar_produtos(marisqueira.produtos, ordenar_por="aleatorio")


class TestComparacao:
    """RN12 / P26."""

    def test_comparar_entre_empresas(self, compradora, marisqueira, marisqueira_b, produto_fresco):
        produto_b = marisqueira_b.cadastrar_produto(
            "Camarão", CategoriaProduto.FRESCO, 35.0, 80
        )
        info = compradora.comparar_produtos(produto_fresco, produto_b)
        assert info["diferenca_preco"] == 5.0
        assert info["empresa_a"] == "Marisqueira da Vila"
        assert info["empresa_b"] == "Marisqueira B"


class TestRealizarPedido:
    """RN13, RN14, RN15, RN16, RN17, RN18, P27–P34."""

    def test_dados_obrigatorios(self, compradora, marisqueira, produto_fresco):
        with pytest.raises(ValueError):
            compradora.realizar_pedido(marisqueira, "", "2 dias", [(produto_fresco, 25)])
        with pytest.raises(ValueError):
            compradora.realizar_pedido(marisqueira, "Rua X", "", [(produto_fresco, 25)])

    def test_multiplos_produtos_mesma_empresa(self, compradora, marisqueira, produto_fresco, produto_congelado):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias",
            [(produto_fresco, 25), (produto_congelado, 30)],
        )
        assert len(pedido.itens) == 2

    def test_rn14_produto_de_outra_empresa_bloqueado(self, compradora, marisqueira, marisqueira_b, produto_fresco):
        p_outro = marisqueira_b.cadastrar_produto(
            "Camarão", CategoriaProduto.FRESCO, 38.0, 100
        )
        with pytest.raises(RegraNegocioError):
            compradora.realizar_pedido(
                marisqueira, "Rua X", "2 dias",
                [(produto_fresco, 25), (p_outro, 25)],
            )

    def test_rn15_minimo_por_produto(self, compradora, marisqueira, produto_fresco):
        with pytest.raises(QuantidadeMinimaError):
            compradora.realizar_pedido(marisqueira, "Rua X", "2 dias", [(produto_fresco, 24)])

    def test_rn18_p34_quantidade_maior_que_estoque(self, compradora, marisqueira, produto_fresco):
        with pytest.raises(EstoqueInsuficienteError):
            compradora.realizar_pedido(marisqueira, "Rua X", "2 dias", [(produto_fresco, 101)])

    def test_rn16_sem_minimo_financeiro(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)])
        assert pedido.calcular_total() == 25 * 40.0

    def test_rn17_sem_maximo_fixo(self, compradora, marisqueira, produto_fresco):
        produto_fresco.alterar_quantidade(1000)
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 999)]
        )
        assert pedido.itens[0].quantidade == 999