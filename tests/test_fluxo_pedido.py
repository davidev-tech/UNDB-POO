import pytest


def test_receber_pedido(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    # estado inicial permanece sob análise (não é um dos 3 estados do PDF)
    assert pedido.status_pedido not in ("em curso", "finalizado")


def test_aceitar_pedido_leva_a_em_preparo(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    marisqueira.aceitar_pedido(pedido)
    assert pedido.status_pedido == "em preparo"


def test_rejeitar_pedido(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    marisqueira.rejeitar_pedido(pedido)
    assert pedido.status_pedido != "em preparo"


def test_solicitar_ajuste(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    marisqueira.solicitar_ajuste(pedido)
    assert pedido.status_pedido != "em preparo"


def test_nao_aceitar_sem_receber(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    with pytest.raises(ValueError):
        marisqueira.aceitar_pedido(pedido)


def test_atualizar_status_entrega_em_curso(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    marisqueira.aceitar_pedido(pedido)
    marisqueira.atualizar_status_entrega(pedido, "em curso")
    assert pedido.status_pedido == "em curso"


def test_atualizar_status_entrega_finalizado(marisqueira, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    marisqueira.aceitar_pedido(pedido)
    marisqueira.atualizar_status_entrega(pedido, "em curso")
    marisqueira.atualizar_status_entrega(pedido, "finalizado")
    assert pedido.status_pedido == "finalizado"


def test_sem_rastreamento_em_tempo_real(pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    assert not hasattr(pedido, "latitude")
    assert not hasattr(pedido, "longitude")


def test_fluxo_completo(marisqueira, comprador, pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    marisqueira.receber_pedido(pedido)
    marisqueira.aceitar_pedido(pedido)
    marisqueira.atualizar_status_entrega(pedido, "em curso")
    marisqueira.atualizar_status_entrega(pedido, "finalizado")
    assert pedido.status_pedido == "finalizado"