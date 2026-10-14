from enum import Enum


class CategoriaProduto(Enum):
    """RN06 / P18: fresco e congelado são produtos distintos."""
    FRESCO = "fresco"
    CONGELADO = "congelado"


class StatusPedido(Enum):
    """Apenas os 3 estados do PDF (P7)."""
    EM_PREPARO = "em_preparo"
    EM_CURSO = "em_curso"
    FINALIZADO = "finalizado"


class StatusEmpresa(Enum):
    """P33 / RN20: indicador visual da empresa."""
    DISPONIVEL = "verde"
    ESTOQUE_BAIXO = "laranja"
    FORA_DO_HORARIO = "vermelho"