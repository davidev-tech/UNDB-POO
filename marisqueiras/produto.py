from __future__ import annotations
from typing import Optional

from .enums import CategoriaProduto


class Produto:
    """
    RN04 (kg), RN05 (mín. venda 25 kg), RN06 (fresco ≠ congelado),
    RN07 (preço fixo na venda), RN08/RN09 (estoque),
    RN17/RN18 (limite), RN19/RN20 (indisponível mas visível).
    """

    def __init__(
        self,
        nome: str,
        categoria: CategoriaProduto,
        preco: float,
        quantidade_disponivel: int,
        empresa,  # EmpresaMarisqueira
        foto: Optional[str] = None,
    ):
        if not nome or not isinstance(nome, str):
            raise ValueError("Nome do produto é obrigatório. P15")
        if not isinstance(categoria, CategoriaProduto):
            raise ValueError("Categoria inválida. Use CategoriaProduto. RN06")
        if preco <= 0:
            raise ValueError("Preço deve ser maior que zero. RN07")
        if quantidade_disponivel < 0:
            raise ValueError("Quantidade não pode ser negativa.")

        self.nome = nome
        self.categoria = categoria
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.empresa = empresa
        self.foto = foto  # único campo opcional (P15)

    def alterar_quantidade(self, nova_quantidade: int) -> None:
        """RN08, RN09."""
        if nova_quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa.")
        self.quantidade_disponivel = nova_quantidade

    def verificar_disponibilidade(self, quantidade: int) -> bool:
        """RN17, RN18."""
        if quantidade < 0:
            raise ValueError("Quantidade deve ser positiva.")
        return self.quantidade_disponivel >= quantidade

    def esta_disponivel(self) -> bool:
        """RN09, RN20."""
        return self.quantidade_disponivel > 0

    def __str__(self) -> str:
        return (
            f"{self.nome} ({self.categoria.value}) - "
            f"R$ {self.preco:.2f}/kg - {self.quantidade_disponivel} kg - "
            f"Empresa: {self.empresa.nome}"
        )