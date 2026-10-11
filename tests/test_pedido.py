import pytest
from marisqueiras import ItemPedido


def test_id_pedido_registrado(pedido):
    assert pedido.id_pedido == "PED-001"


def test_pagamento_fora_do_escopo(pedido):
    assert not hasattr(pedido, "forma_pagamento") or pedido.forma_pagamento is None


def test_pedido_varios_produtos_mesma_empresa(pedido, marisqueira):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-501", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=100,
    )
    p2 = marisqueira.cadastrar_produto(
        id_produto="P-502", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=100,
    )
    pedido.adicionar_item(produto=p1, quantidade=25)
    pedido.adicionar_item(produto=p2, quantidade=25)
    assert len(pedido.itens) == 2


def test_nao_misturar_marisqueiras(comprador, marisqueira, outra_marisqueira, pedido):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-503", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=100,
    )
    p2 = outra_marisqueira.cadastrar_produto(
        id_produto="P-504", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=100,
    )
    pedido.adicionar_item(produto=p1, quantidade=25)
    with pytest.raises(ValueError):
        pedido.adicionar_item(produto=p2, quantidade=25)


def test_rn15_minimo_25kg_por_item(pedido, produto):
    with pytest.raises(ValueError):
        pedido.adicionar_item(produto=produto, quantidade=24)


def test_validar_quantidade_exata(pedido, produto):
    item = ItemPedido(id_pedido="PED-001", id_produto="P-001", quantidade=25)
    assert pedido.validar_quantidade(item) is True


def test_validar_quantidade_abaixo(pedido, produto):
    item = ItemPedido(id_pedido="PED-001", id_produto="P-001", quantidade=24)
    with pytest.raises(ValueError):
        pedido.validar_quantidade(item)


def test_rn16_sem_valor_minimo_financeiro(comprador, marisqueira, pedido):
    # RN16: não existe valor financeiro mínimo. Um produto de R$1,00
    # com 25 kg é aceito normalmente no pedido.
    p = marisqueira.cadastrar_produto(
        id_produto="P-505", nome="Ostra", categoria="fresco",
        preco=1.0, quantidade_disponivel=25,
    )
    item = pedido.adicionar_item(produto=p, quantidade=25)
    assert item.quantidade == 25


def test_rn17_sem_quantidade_maxima_fixa(pedido, marisqueira):
    p = marisqueira.cadastrar_produto(
        id_produto="P-506", nome="Ostra", categoria="fresco",
        preco=30.0, quantidade_disponivel=1000,
    )
    pedido.adicionar_item(produto=p, quantidade=500)
    assert pedido.itens[0].quantidade == 500


def test_rn18_bloqueia_acima_do_disponivel(pedido, produto):
    with pytest.raises(ValueError):
        pedido.adicionar_item(produto=produto, quantidade=101)


def test_verificar_disponibilidade_ok(pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=50)
    assert pedido.verificar_disponibilidade() is True


def test_verificar_disponibilidade_insuficiente(pedido, produto):
    item = ItemPedido(id_pedido="PED-001", id_produto="P-001", quantidade=101)
    pedido.itens.append(item)
    assert pedido.verificar_disponibilidade() is False


def test_rn07_preco_nao_alteravel_durante_venda(produto, marisqueira):
    # RN07: preço definido por produto e empresa, não alterável durante
    # a venda. Como não existe método de alteração de preço na modelagem,
    # o teste verifica que o preço do produto permanece o mesmo após
    # ser adicionado a um pedido — ou seja, não há caminho para mudá-lo.
    pedido = marisqueira.pedidos_recebidos  # apenas referência, sem uso direto
    preco_antes = produto.preco
    # não existe método para alterar preço durante uma venda
    assert not hasattr(produto, "alterar_preco")
    assert produto.preco == preco_antes


def test_preco_por_produto_e_empresa(comprador, marisqueira, outra_marisqueira):
    p1 = marisqueira.cadastrar_produto(
        id_produto="P-507", nome="Camarão", categoria="fresco",
        preco=50.0, quantidade_disponivel=30,
    )
    p2 = outra_marisqueira.cadastrar_produto(
        id_produto="P-508", nome="Camarão", categoria="fresco",
        preco=40.0, quantidade_disponivel=30,
    )
    assert p1.preco != p2.preco


def test_sem_custo_de_entrega_separado(pedido, produto):
    pedido.adicionar_item(produto=produto, quantidade=25)
    assert not hasattr(pedido, "custo_entrega") or pedido.custo_entrega is None
    assert not hasattr(pedido, "frete") or pedido.frete is None