from __future__ import annotations
from datetime import datetime
from typing import Optional

from .excecoes import RegraNegocioError


class Avaliacao:
    """RN21, P23, P24."""

    def __init__(self, empresa_compradora, empresa_marisqueira,
                 nota: int, comentario: Optional[str] = None):
        # RN21 / P23: precisa existir compra aceita entre as duas empresas.
        tem_compra = any(
            p.empresa_marisqueira is empresa_marisqueira and p.aceito is True
            for p in empresa_compradora.pedidos_realizados
        )
        if not tem_compra:
            raise RegraNegocioError(
                "A empresa compradora só pode avaliar após a compra. RN21"
            )

        self.empresa_compradora = empresa_compradora
        self.empresa_marisqueira = empresa_marisqueira
        self.comentario = comentario
        self.data = datetime.now()
        self.nota: int = 0
        self.registrar_nota(nota)

    def registrar_nota(self, nota: int) -> None:
        """P24: inteiro de 1 a 5."""
        if not isinstance(nota, int) or nota < 1 or nota > 5:
            raise ValueError("Nota deve ser um inteiro de 1 a 5 estrelas. P24")
        self.nota = nota

    def __str__(self) -> str:
        return (
            f"Avaliação de {self.empresa_marisqueira.nome} por "
            f"{self.empresa_compradora.nome}: {self.nota}★ "
            f"({self.comentario or 'sem comentário'})"
        )