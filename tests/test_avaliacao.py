import pytest

from marisqueiras import (
    Avaliacao,
    RegraNegocioError,
)


class TestAvaliacao:
    """RN21, P23, P24."""

    def test_avaliar_sem_compra_bloqueado(self, compradora, marisqueira):
        with pytest.raises(RegraNegocioError):
            compradora.avaliar_empresa(marisqueira, 5)

    def test_avaliar_com_pedido_pendente_bloqueado(self, compradora, marisqueira, produto_fresco):
        compradora.realizar_pedido(marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)])
        with pytest.raises(RegraNegocioError):
            compradora.avaliar_empresa(marisqueira, 5)

    def test_avaliar_com_pedido_rejeitado_bloqueado(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.rejeitar_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            compradora.avaliar_empresa(marisqueira, 5)

    def test_avaliar_apos_compra_aceita(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        av = compradora.avaliar_empresa(marisqueira, 5, "Excelente")
        assert av.nota == 5
        assert av in marisqueira.avaliacoes_recebidas
        assert av in compradora.avaliacoes_feitas

    def test_nota_1_valida(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        assert compradora.avaliar_empresa(marisqueira, 1).nota == 1

    def test_nota_5_valida(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        assert compradora.avaliar_empresa(marisqueira, 5).nota == 5

    def test_nota_0_invalida(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(ValueError):
            compradora.avaliar_empresa(marisqueira, 0)

    def test_nota_6_invalida(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(ValueError):
            compradora.avaliar_empresa(marisqueira, 6)

    def test_nota_nao_inteira_invalida(self, compradora, marisqueira, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(ValueError):
            compradora.avaliar_empresa(marisqueira, 4.5)

    def test_media_avaliacoes(self, compradora, marisqueira, produto_fresco):
        for nota in (5, 4):
            pedido = compradora.realizar_pedido(
                marisqueira, "Rua X", "2 dias", [(produto_fresco, 25)]
            )
            marisqueira.receber_pedido(pedido)
            marisqueira.aceitar_pedido(pedido)
            compradora.avaliar_empresa(marisqueira, nota)
        assert marisqueira.media_avaliacoes() == 4.5

    def test_media_sem_avaliacoes_e_zero(self, marisqueira):
        assert marisqueira.media_avaliacoes() == 0.0