from __future__ import annotations
from datetime import datetime
from typing import Optional, Tuple


class Empresa:
    """
    RN01: B2B — somente empresas.
    RN02: 1 habitação = 1 empresa.
    P12: uma pessoa por habitação responde pelo cadastro/acesso.
    """

    def __init__(
        self,
        nome: str,
        localizacao: str,
        responsavel: str,
        horario_funcionamento: Tuple[int, int],
    ):
        if not nome or not isinstance(nome, str):
            raise ValueError("Nome da empresa é obrigatório.")
        if not localizacao:
            raise ValueError("Localização é obrigatória.")
        if not responsavel:
            raise ValueError("Uma pessoa por habitação deve ser responsável. P12")
        if (
            not isinstance(horario_funcionamento, tuple)
            or len(horario_funcionamento) != 2
            or horario_funcionamento[0] >= horario_funcionamento[1]
        ):
            raise ValueError("Horário deve ser uma tupla (abertura, fechamento).")

        self.nome = nome
        self.localizacao = localizacao
        self.responsavel = responsavel
        self.horario_funcionamento = horario_funcionamento

    def esta_no_horario(self, hora_atual: Optional[int] = None) -> bool:
        if hora_atual is None:
            hora_atual = datetime.now().hour
        abertura, fechamento = self.horario_funcionamento
        return abertura <= hora_atual < fechamento

    def __str__(self) -> str:
        return f"{self.nome} ({self.localizacao})"