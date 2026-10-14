from __future__ import annotations
from typing import List, Optional, Tuple

from .empresa import Empresa
from .enums import CategoriaProduto, StatusEmpresa, StatusPedido
from .excecoes import RegraNegocioError
from .produto import Produto


class EmpresaMarisqueira(Empresa):
    """
    RN03, RN12, RN19, RN20, RN22.
    Analisa pedidos: aceita, rejeita ou solicita ajuste.
    """

    def __init__(self, nome, localizacao, responsavel, horario_funcionamento):
        super().__init__(nome, localizacao, responsavel, horario_funcionamento)
        self.produtos: List[Produto] = []
        self.pedidos_recebidos: List["Pedido"] = []
        self.avaliacoes_recebidas: List["Avaliacao"] = []

    # Cadastro --------------------------------------------------------------
    def cadastrar_produto(
        self,
        nome: str,
        categoria: CategoriaProduto,
        preco: float,
        quantidade_disponivel: int,
        foto: Optional[str] = None,
    ) -> Produto:
        """P15, P16, P18, RN06."""
        for p in self.produtos:
            if p.nome.lower() == nome.lower() and p.categoria == categoria:
                raise RegraNegocioError(
                    f"Já existe um produto '{nome}' na categoria {categoria.value}. RN06"
                )
        novo = Produto(nome, categoria, preco, quantidade_disponivel, self, foto)
        self.produtos.append(novo)
        return novo

    def consultar_proprios_produtos(self) -> List[Produto]:
        """RN12 / P25."""
        return list(self.produtos)

    def alterar_quantidade(self, produto: Produto, nova_quantidade: int) -> None:
        """RN08."""
        if produto not in self.produtos:
            raise RegraNegocioError("Produto não pertence a esta empresa.")
        produto.alterar_quantidade(nova_quantidade)

    # Análise de pedido -----------------------------------------------------
    def receber_pedido(self, pedido: "Pedido") -> None:
        self._validar_pedido(pedido)
        if pedido not in self.pedidos_recebidos:
            self.pedidos_recebidos.append(pedido)

    def aceitar_pedido(self, pedido: "Pedido") -> None:
        """RN07, RN08, RN18."""
        self._validar_pedido(pedido)
        if pedido.aceito is not None:
            raise RegraNegocioError("Pedido já foi analisado.")
        if not pedido.itens:
            raise RegraNegocioError("Pedido sem itens não pode ser aceito. RN13")

        pedido.verificar_disponibilidade()
        for item in pedido.itens:
            nova_qtd = item.produto.quantidade_disponivel - item.quantidade
            item.produto.alterar_quantidade(nova_qtd)

        pedido.aceito = True
        pedido.status = StatusPedido.EM_PREPARO

    def rejeitar_pedido(self, pedido: "Pedido") -> None:
        self._validar_pedido(pedido)
        if pedido.aceito is not None:
            raise RegraNegocioError("Pedido já foi analisado.")
        pedido.aceito = False

    def solicitar_ajuste(self, pedido: "Pedido", mensagem: str = "") -> None:
        self._validar_pedido(pedido)
        if pedido.aceito is not None:
            raise RegraNegocioError("Pedido já foi analisado.")
        pedido.mensagem_ajuste = mensagem

    # Entrega ---------------------------------------------------------------
    def atualizar_status_entrega(self, pedido: "Pedido", novo_status: StatusPedido) -> None:
        """RN22."""
        self._validar_pedido(pedido)
        if pedido.aceito is not True:
            raise RegraNegocioError(
                "Só é possível atualizar entrega de pedido aceito. RN22"
            )
        pedido.atualizar_status_entrega(novo_status)

    # Avaliações ------------------------------------------------------------
    def registrar_avaliacao(self, avaliacao: "Avaliacao") -> None:
        if avaliacao.empresa_marisqueira is not self:
            raise RegraNegocioError("Avaliação não pertence a esta empresa.")
        self.avaliacoes_recebidas.append(avaliacao)

    def media_avaliacoes(self) -> float:
        if not self.avaliacoes_recebidas:
            return 0.0
        return sum(a.nota for a in self.avaliacoes_recebidas) / len(
            self.avaliacoes_recebidas
        )

    # Indicador visual ------------------------------------------------------
    def status_visual(self, hora_atual: Optional[int] = None) -> StatusEmpresa:
        """P33 / RN20."""
        if not self.esta_no_horario(hora_atual):
            return StatusEmpresa.FORA_DO_HORARIO
        if any(p.quantidade_disponivel >= 25 for p in self.produtos):
            return StatusEmpresa.DISPONIVEL
        return StatusEmpresa.ESTOQUE_BAIXO

    # Auxiliar --------------------------------------------------------------
    def _validar_pedido(self, pedido: "Pedido") -> None:
        from .pedido import Pedido  # import tardio evita ciclo
        if not isinstance(pedido, Pedido):
            raise ValueError("Pedido inválido.")
        if pedido.empresa_marisqueira is not self:
            raise RegraNegocioError("Pedido não pertence a esta empresa.")