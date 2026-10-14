from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from .enums import StatusPedido
from .excecoes import RegraNegocioError
from .item_pedido import ItemPedido
from .produto import Produto


class Pedido:
    """
    RN07, RN13, RN14, RN15, RN17, RN18, RN21, RN22.

    aceito: None (pendente) / True (aceito) / False (rejeitado)
    status: None → EM_PREPARO → EM_CURSO → FINALIZADO
    """

    def __init__(self, empresa_compradora, empresa_marisqueira,
                 endereco_entrega: str, tempo_entrega: str):
        if empresa_compradora is None:
            raise ValueError("Empresa compradora inválida. RN13")
        if empresa_marisqueira is None:
            raise ValueError("Empresa marisqueira inválida. RN14")
        if not endereco_entrega:
            raise ValueError("Endereço de entrega é obrigatório. RN13")
        if not tempo_entrega:
            raise ValueError("Tempo de entrega é obrigatório. RN13")

        self.empresa_compradora = empresa_compradora
        self.empresa_marisqueira = empresa_marisqueira
        self.endereco_entrega = endereco_entrega
        self.tempo_entrega = tempo_entrega

        self.itens: List[ItemPedido] = []
        self.aceito: Optional[bool] = None
        self.status: Optional[StatusPedido] = None
        self.mensagem_ajuste: Optional[str] = None
        self.criado_em = datetime.now()

    def adicionar_item(self, produto: Produto, quantidade: int) -> None:
        """RN14, RN15, P28."""
        if produto.empresa is not self.empresa_marisqueira:
            raise RegraNegocioError(
                "Um pedido não pode reunir produtos de empresas diferentes. RN14"
            )
        item = ItemPedido(produto, quantidade)
        self.itens.append(item)

    def validar_quantidade(self) -> None:
        """RN15."""
        if not self.itens:
            raise RegraNegocioError("Pedido deve ter pelo menos um item. RN13")
        for item in self.itens:
            item.validar_quantidade()

    def verificar_disponibilidade(self) -> None:
        """RN17, RN18."""
        for item in self.itens:
            item.verificar_disponibilidade()

    def calcular_total(self) -> float:
        return sum(item.subtotal() for item in self.itens)

    def atualizar_status_entrega(self, novo_status: StatusPedido) -> None:
        """RN22: EM_PREPARO → EM_CURSO → FINALIZADO."""
        if self.aceito is not True:
            raise RegraNegocioError("Pedido precisa ter sido aceito. RN07, RN22")
        if not isinstance(novo_status, StatusPedido):
            raise ValueError("Status inválido.")

        transicoes = {
            StatusPedido.EM_PREPARO: StatusPedido.EM_CURSO,
            StatusPedido.EM_CURSO: StatusPedido.FINALIZADO,
        }
        esperado = transicoes.get(self.status)
        if esperado is None:
            raise RegraNegocioError(
                f"Pedido já está em estado final ({self.status.value})."
            )
        if novo_status != esperado:
            raise RegraNegocioError(
                f"Transição inválida: {self.status.value} → {novo_status.value}. "
                f"Esperado: {esperado.value}."
            )
        self.status = novo_status

    def __str__(self) -> str:
        itens_str = "\n".join(f"  - {item}" for item in self.itens) or "  (sem itens)"
        if self.aceito is None:
            analise = "pendente"
        elif self.aceito:
            analise = "aceito"
        else:
            analise = "rejeitado"
        status_str = self.status.value if self.status else "—"
        ajuste = f" | ajuste: {self.mensagem_ajuste}" if self.mensagem_ajuste else ""
        return (
            f"Pedido #{id(self)}\n"
            f"Análise: {analise} | Entrega: {status_str}{ajuste}\n"
            f"Comprador: {self.empresa_compradora}\n"
            f"Marisqueira: {self.empresa_marisqueira}\n"
            f"Endereço: {self.endereco_entrega}\n"
            f"Tempo de entrega: {self.tempo_entrega}\n"
            f"Itens:\n{itens_str}\n"
            f"Total: R$ {self.calcular_total():.2f}"
        )