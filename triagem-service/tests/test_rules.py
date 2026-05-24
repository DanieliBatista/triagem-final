import pytest

from app.domain.rules import ValidacaoBiologicaException, validar_sinais_vitais


def test_deve_aceitar_sinais_vitais_dentro_dos_limites():
    resultado = validar_sinais_vitais(36.5, 120, 80, 98.0, 72)

    assert resultado is None


@pytest.mark.parametrize(
    ("sinais_vitais", "mensagem"),
    [
        ((50.0, 120, 80, 98.0, 72), "Temperatura"),
        ((36.5, 40, 80, 98.0, 72), "sist"),
        ((36.5, 120, 20, 98.0, 72), "diast"),
        ((36.5, 120, 80, 40.0, 72), "oxig"),
        ((36.5, 120, 80, 98.0, 10), "card"),
    ],
)
def test_deve_rejeitar_sinais_vitais_fora_dos_limites(sinais_vitais, mensagem):
    with pytest.raises(ValidacaoBiologicaException, match=mensagem):
        validar_sinais_vitais(*sinais_vitais)
