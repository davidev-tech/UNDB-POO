import pytest
from marisqueiras import Avaliacao


def test_avaliacao_criada_com_id(comprador, marisqueira):
    av = comprador.avaliar_empresa(
        id_avaliacao="AV-001", empresa=marisqueira, nota=5,
    )
    assert isinstance(av, Avaliacao)
    assert av.id_avaliacao == "AV-001"
    assert av.nota == 5


@pytest.mark.parametrize("nota", [1, 2, 3, 4, 5])
def test_notas_validas(comprador, marisqueira, nota):
    av = comprador.avaliar_empresa(
        id_avaliacao=f"AV-{nota}", empresa=marisqueira, nota=nota,
    )
    assert av.nota == nota


@pytest.mark.parametrize("nota", [0, 6, -1, 10])
def test_notas_invalidas(comprador, marisqueira, nota):
    with pytest.raises(ValueError):
        comprador.avaliar_empresa(
            id_avaliacao="AV-X", empresa=marisqueira, nota=nota,
        )


def test_registrar_nota_valida(comprador, marisqueira):
    av = comprador.avaliar_empresa(
        id_avaliacao="AV-002", empresa=marisqueira, nota=3,
    )
    av.registrar_nota(4)
    assert av.nota == 4


@pytest.mark.parametrize("nota", [0, 6, -1, 10])
def test_registrar_nota_invalida(comprador, marisqueira, nota):
    av = comprador.avaliar_empresa(
        id_avaliacao="AV-003", empresa=marisqueira, nota=3,
    )
    with pytest.raises(ValueError):
        av.registrar_nota(nota)