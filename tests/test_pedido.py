import pytest

from marisqueiras import (
    ItemPedido,
    QuantidadeMinimaError,
    EstoqueInsuficienteError,
    StatusPedido,
    RegraNegocioError,
)


class TestItemPedido:
    """RN05, RN07, RN15, RN17, RN18, P30, P34."""

    def test_minimo_25_kg(self, produto_fresco):
        with pytest.raises(QuantidadeMinimaError):
            ItemPedido(produto_fresco, 24)

    def test_exatamente_25_kg_ok(self, produto_fresco):
        item = ItemPedido(produto_fresco, 25)
        assert item.quantidade == 25

    def test_estoque_insuficiente(self, produto_fresco):
        with pytest.raises(EstoqueInsuficienteError):
            ItemPedido(produto_fresco, 101)

    def test_preco_congelado_na_compra(self, produto_fresco):
        item = ItemPedido(produto_fresco, 50)
        produto_fresco.preco = 999.0
        assert item.preco_unitario == 40.0

    def test_atualizar_quantidade_revalida_minimo(self, produto_fresco):
        item = ItemPedido(produto_fresco, 50)
        with pytest.raises(QuantidadeMinimaError):
            item.atualizar_quantidade(10)

    def test_atualizar_quantidade_revalida_estoque(self, produto_fresco):
        item = ItemPedido(produto_fresco, 50)
        produto_fresco.alterar_quantidade(30)
        with pytest.raises(EstoqueInsuficienteError):
            item.atualizar_quantidade(40)

    def test_subtotal(self, produto_fresco):
        item = ItemPedido(produto_fresco, 30)
        assert item.subtotal() == 30 * 40.0


class TestPedido:
    """RN13, RN14, RN22."""

    def test_pedido_guarda_comprador_e_marisqueira(
        self, compradora, marisqueira, produto_fresco
    ):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        assert pedido.empresa_compradora is compradora
        assert pedido.empresa_marisqueira is marisqueira

    def test_pedido_sem_itens_bloqueado(self, compradora, marisqueira):
        """RN13: pedido precisa ter ao menos um item."""
        with pytest.raises(RegraNegocioError):
            compradora.realizar_pedido(marisqueira, "Rua X", "2 dias", [])

    def test_sem_aceite_nao_atualiza_status(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        with pytest.raises(RegraNegocioError):
            pedido.atualizar_status_entrega(StatusPedido.EM_CURSO)

    def test_estado_inicial(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        assert pedido.aceito is None
        assert pedido.status is None

    def test_calcular_total(self, compradora, marisqueira, produto_fresco, produto_congelado):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias",
            [(produto_fresco, 50), (produto_congelado, 30)],
        )
        assert pedido.calcular_total() == 50 * 40.0 + 30 * 35.0