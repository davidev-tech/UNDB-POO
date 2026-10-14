class RegraNegocioError(Exception):
    """Exceção base para violações de regras de negócio."""


class QuantidadeMinimaError(RegraNegocioError):
    """Quantidade inferior ao mínimo permitido para venda (25 kg). RN05, RN15."""


class EstoqueInsuficienteError(RegraNegocioError):
    """Quantidade solicitada maior que a disponível. RN18."""