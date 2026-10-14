import pytest

from marisqueiras import CategoriaProduto, StatusPedido


class TestFluxoCompleto:
    """P7: consulta → seleção → pedido → análise → aceite → preparação → entrega."""

    def test_fluxo_ponta_a_ponta(self, compradora, marisqueira):
        # cadastro
        p = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)

        # consulta
        encontrados = compradora.consultar_produtos(
            marisqueira.consultar_proprios_produtos(), nome="camarão"
        )
        assert len(encontrados) == 1

        # pedido
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(p, 50)]
        )

        # análise
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        assert p.quantidade_disponivel == 50
        assert pedido.status == StatusPedido.EM_PREPARO

        # entrega
        marisqueira.atualizar_status_entrega(pedido, StatusPedido.EM_CURSO)
        marisqueira.atualizar_status_entrega(pedido, StatusPedido.FINALIZADO)
        assert pedido.status == StatusPedido.FINALIZADO

        # avaliação
        av = compradora.avaliar_empresa(marisqueira, 5, "Ótimo")
        assert av.nota == 5

    def test_fluxo_rejeicao(self, compradora, marisqueira):
        p = marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(p, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.rejeitar_pedido(pedido)

        assert pedido.aceito is False
        assert pedido.status is None
        assert p.quantidade_disponivel == 100

        # não pode avaliar após rejeição
        from marisqueiras import RegraNegocioError
        with pytest.raises(RegraNegocioError):
            compradora.avaliar_empresa(marisqueira, 5)