import pytest

from marisqueiras import (
    CategoriaProduto,
    StatusEmpresa,
    StatusPedido,
    RegraNegocioError,
)


class TestStatusVisual:
    """P33 / RN20."""

    def test_fora_do_horario_vermelho(self):
        from marisqueiras import EmpresaMarisqueira
        m = EmpresaMarisqueira("X", "Raposa", "Resp", (8, 18))
        m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
        assert m.status_visual(hora_atual=20) == StatusEmpresa.FORA_DO_HORARIO

    def test_disponivel_verde(self, marisqueira, produto_fresco):
        assert marisqueira.status_visual(hora_atual=10) == StatusEmpresa.DISPONIVEL

    def test_estoque_baixo_laranja(self, marisqueira):
        marisqueira.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 10)
        assert marisqueira.status_visual(hora_atual=10) == StatusEmpresa.ESTOQUE_BAIXO

    def test_sem_produtos_laranja(self, marisqueira):
        assert marisqueira.status_visual(hora_atual=10) == StatusEmpresa.ESTOQUE_BAIXO


class TestAnalisePedido:
    """P7, RN07, RN08."""

    def test_aceitar_da_baixa_no_estoque(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        assert pedido.aceito is True
        assert produto_fresco.quantidade_disponivel == 50
        assert pedido.status == StatusPedido.EM_PREPARO

    def test_aceitar_duas_vezes_bloqueado(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            marisqueira.aceitar_pedido(pedido)

    def test_rejeitar_nao_altera_estoque(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.rejeitar_pedido(pedido)
        assert pedido.aceito is False
        assert produto_fresco.quantidade_disponivel == 100
        assert pedido.status is None

    def test_rejeitar_depois_de_aceitar_bloqueado(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            marisqueira.rejeitar_pedido(pedido)

    def test_solicitar_ajuste_registra_mensagem(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.solicitar_ajuste(pedido, "Aumentar 10 kg")
        assert pedido.mensagem_ajuste == "Aumentar 10 kg"

    def test_solicitar_ajuste_apos_analise_bloqueado(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            marisqueira.solicitar_ajuste(pedido, "x")

    def test_pedido_de_outra_marisqueira_bloqueado(self, marisqueira, marisqueira_b, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        with pytest.raises(RegraNegocioError):
            marisqueira_b.receber_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            marisqueira_b.aceitar_pedido(pedido)


class TestStatusEntrega:
    """RN22, P7."""

    def test_sem_aceite_nao_pode_atualizar(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            marisqueira.atualizar_status_entrega(pedido, StatusPedido.EM_CURSO)

    def test_fluxo_valido(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        marisqueira.atualizar_status_entrega(pedido, StatusPedido.EM_CURSO)
        marisqueira.atualizar_status_entrega(pedido, StatusPedido.FINALIZADO)
        assert pedido.status == StatusPedido.FINALIZADO

    def test_transicao_invalida(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(RegraNegocioError):
            marisqueira.atualizar_status_entrega(pedido, StatusPedido.FINALIZADO)

    def test_nao_avanca_apos_finalizado(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        marisqueira.atualizar_status_entrega(pedido, StatusPedido.EM_CURSO)
        marisqueira.atualizar_status_entrega(pedido, StatusPedido.FINALIZADO)
        with pytest.raises(RegraNegocioError):
            marisqueira.atualizar_status_entrega(pedido, StatusPedido.FINALIZADO)

    def test_status_invalido(self, marisqueira, compradora, produto_fresco):
        pedido = compradora.realizar_pedido(
            marisqueira, "Rua X", "2 dias", [(produto_fresco, 50)]
        )
        marisqueira.receber_pedido(pedido)
        marisqueira.aceitar_pedido(pedido)
        with pytest.raises(ValueError):
            marisqueira.atualizar_status_entrega(pedido, "entregue")