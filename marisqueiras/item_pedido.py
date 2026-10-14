from __future__ import annotations

from .excecoes import QuantidadeMinimaError, EstoqueInsuficienteError
from .produto import Produto


class ItemPedido:
    """RN05, RN07, RN15, RN17, RN18."""

    def __init__(self, produto: Produto, quantidade: int):
        if not isinstance(produto, Produto):
            raise ValueError("Produto inválido.")
        self.produto = produto
        self.quantidade = quantidade
        self.preco_unitario = produto.preco  # RN07: preço congelado
        self.validar_quantidade()
        self.verificar_disponibilidade()

    def validar_quantidade(self) -> None:
        """RN05, RN15."""
        if self.quantidade < 25:
            raise QuantidadeMinimaError(
                "Quantidade mínima por produto é de 25 kg. RN15"
            )

    def verificar_disponibilidade(self) -> None:
        """RN17, RN18, P34."""
        if not self.produto.verificar_disponibilidade(self.quantidade):
            raise EstoqueInsuficienteError(
                f"Quantidade indisponível para '{self.produto.nome}'. "
                f"Solicitado: {self.quantidade} kg, "
                f"Disponível: {self.produto.quantidade_disponivel} kg. RN18"
            )

    def atualizar_quantidade(self, nova_quantidade: int) -> None:
        if nova_quantidade < 25:
            raise QuantidadeMinimaError("Quantidade mínima é de 25 kg. RN15")
        if not self.produto.verificar_disponibilidade(nova_quantidade):
            raise EstoqueInsuficienteError(
                f"Quantidade indisponível. Solicitado: {nova_quantidade} kg, "
                f"Disponível: {self.produto.quantidade_disponivel} kg. RN18"
            )
        self.quantidade = nova_quantidade

    def subtotal(self) -> float:
        return self.preco_unitario * self.quantidade

    def __str__(self) -> str:
        return (
            f"{self.produto.nome} ({self.produto.categoria.value}) - "
            f"{self.quantidade} kg x R$ {self.preco_unitario:.2f} = "
            f"R$ {self.subtotal():.2f}"
        )