from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .empresa import Empresa
from .enums import CategoriaProduto
from .excecoes import RegraNegocioError


class EmpresaCompradora(Empresa):
    """RN10, RN11, RN12, RN13, RN21."""

    def __init__(self, nome, localizacao, responsavel, horario_funcionamento):
        super().__init__(nome, localizacao, responsavel, horario_funcionamento)
        self.pedidos_realizados: List["Pedido"] = []
        self.avaliacoes_feitas: List["Avaliacao"] = []

    # Consulta --------------------------------------------------------------
    def consultar_produtos(
        self,
        produtos_disponiveis,
        nome: Optional[str] = None,
        categoria: Optional[CategoriaProduto] = None,
        localizacao: Optional[str] = None,
        empresa_marisqueira=None,
        avaliacao_minima: Optional[float] = None,
        ordenar_por: Optional[str] = None,
    ):
        """RN10, RN11 / P9, P21, P22."""
        resultado = []
        for p in produtos_disponiveis:
            if nome and nome.lower() not in p.nome.lower():
                continue
            if categoria and p.categoria != categoria:
                continue
            if localizacao and p.empresa.localizacao != localizacao:
                continue
            if empresa_marisqueira and p.empresa is not empresa_marisqueira:
                continue
            if (avaliacao_minima is not None
                    and p.empresa.media_avaliacoes() < avaliacao_minima):
                continue
            resultado.append(p)

        if ordenar_por == "menor_preco":
            resultado.sort(key=lambda p: p.preco)
        elif ordenar_por == "maior_preco":
            resultado.sort(key=lambda p: p.preco, reverse=True)
        elif ordenar_por == "melhor_avaliacao":
            resultado.sort(key=lambda p: p.empresa.media_avaliacoes(), reverse=True)
        elif ordenar_por == "localizacao":
            resultado.sort(key=lambda p: p.empresa.localizacao)
        elif ordenar_por is not None:
            raise ValueError(
                "Ordenação inválida. Use: menor_preco, maior_preco, "
                "melhor_avaliacao ou localizacao. P22"
            )
        return resultado

    def comparar_produtos(self, produto_a, produto_b) -> Dict[str, Any]:
        """RN12 / P26."""
        return {
            "produto_a": str(produto_a),
            "produto_b": str(produto_b),
            "empresa_a": produto_a.empresa.nome,
            "empresa_b": produto_b.empresa.nome,
            "diferenca_preco": produto_a.preco - produto_b.preco,
            "diferenca_estoque": (
                produto_a.quantidade_disponivel - produto_b.quantidade_disponivel
            ),
            "avaliacao_empresa_a": produto_a.empresa.media_avaliacoes(),
            "avaliacao_empresa_b": produto_b.empresa.media_avaliacoes(),
        }

    # Pedido ----------------------------------------------------------------
    def realizar_pedido(
        self,
        empresa_marisqueira,
        endereco_entrega: str,
        tempo_entrega: str,
        itens: List[Tuple["Produto", int]],
    ) -> "Pedido":
        """RN13, RN14, RN15, RN18, P27, P28, P29, P30, P32, P34."""
        from .pedido import Pedido  # import tardio evita ciclo
        from .empresa_marisqueira import EmpresaMarisqueira

        if not isinstance(empresa_marisqueira, EmpresaMarisqueira):
            raise ValueError("É necessário informar uma EmpresaMarisqueira. RN14")
        if not endereco_entrega:
            raise ValueError("Endereço de entrega é obrigatório. RN13")
        if not tempo_entrega:
            raise ValueError("Tempo de entrega é obrigatório. RN13")
        if not itens:
            raise RegraNegocioError("Pedido deve ter pelo menos um item. RN13")

        pedido = Pedido(self, empresa_marisqueira, endereco_entrega, tempo_entrega)
        for produto, quantidade in itens:
            pedido.adicionar_item(produto, quantidade)

        self.pedidos_realizados.append(pedido)
        return pedido

    # Avaliação -------------------------------------------------------------
    def avaliar_empresa(self, empresa_marisqueira, nota: int, comentario=None):
        """RN21, P23, P24."""
        from .avaliacao import Avaliacao
        from .empresa_marisqueira import EmpresaMarisqueira

        if not isinstance(empresa_marisqueira, EmpresaMarisqueira):
            raise ValueError("É necessário informar uma EmpresaMarisqueira. RN21")

        avaliacao = Avaliacao(self, empresa_marisqueira, nota, comentario)
        empresa_marisqueira.registrar_avaliacao(avaliacao)
        self.avaliacoes_feitas.append(avaliacao)
        return avaliacao