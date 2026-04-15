import pytest
from app.domain.rules import calcular_risco

def test_deve_classificar_como_vermelho_se_dor_no_peito():
    resultado = calcular_risco(36.5, 120, True)
    assert resultado == "VERMELHO (Emergencia)"

def test_deve_classificar_laranja_febre_alta():
    resultado = calcular_risco(39.0, 120, False)
    assert resultado == "LARANJA (Muito urgente)"

def test_deve_classificar_verde_em_caso_estavel():
    resultado = calcular_risco(36.0, 110, False)
    assert resultado == "VERDE (Pouco Urgente)"

def test_deve_lancar_erro_para_temperatura_invalida():
    with pytest.raises(ValueError, match="Dados biométricos fora da realidade humana."):
        calcular_risco(50.0, 120, False)

