"""Testes para value objects (SinaisVitais)"""
import pytest

from app.domain.value_objects import (
    SinaisVitais,
    classificar_paciente,
    obter_tempo_espera,
    _classificacao_base,
    _aplicar_escalacao_saturacao,
)
from app.domain.enums import RiskColor
from app.domain.exceptions import ValidacaoBiologicaException


class TestSinaisVitais:
    """Testes para a classe SinaisVitais"""

    def test_criar_sinais_vitais_validos(self, sinais_vitais_normais):
        """Deve criar sinais vitais válidos sem erros"""
        assert sinais_vitais_normais.temperatura == 36.5
        assert sinais_vitais_normais.pressao_sistolica == 120
        assert sinais_vitais_normais.frequencia_cardiaca == 72
        assert sinais_vitais_normais.dor_peito is False

    def test_temperatura_abaixo_minimo(self):
        """Deve rejeitar temperatura abaixo de 30°C"""
        with pytest.raises(ValidacaoBiologicaException) as exc_info:
            SinaisVitais(
                temperatura=29.0,
                pressao_sistolica=120,
                pressao_diastolica=80,
                saturacao_oxigenio=98.0,
                frequencia_cardiaca=72,
            )
        assert "temperatura" in str(exc_info.value).lower()

    def test_temperatura_acima_maximo(self):
        """Deve rejeitar temperatura acima de 45°C"""
        with pytest.raises(ValidacaoBiologicaException):
            SinaisVitais(
                temperatura=46.0,
                pressao_sistolica=120,
                pressao_diastolica=80,
                saturacao_oxigenio=98.0,
                frequencia_cardiaca=72,
            )

    def test_pressao_sistolica_baixa(self):
        """Deve rejeitar pressão sistólica abaixo de 50 mmHg"""
        with pytest.raises(ValidacaoBiologicaException):
            SinaisVitais(
                temperatura=37.0,
                pressao_sistolica=40,
                pressao_diastolica=80,
                saturacao_oxigenio=98.0,
                frequencia_cardiaca=72,
            )

    def test_pressao_sistolica_alta(self):
        """Deve rejeitar pressão sistólica acima de 300 mmHg"""
        with pytest.raises(ValidacaoBiologicaException):
            SinaisVitais(
                temperatura=37.0,
                pressao_sistolica=301,
                pressao_diastolica=80,
                saturacao_oxigenio=98.0,
                frequencia_cardiaca=72,
            )

    def test_saturacao_oxigenio_baixa(self):
        """Deve rejeitar saturação abaixo de 50%"""
        with pytest.raises(ValidacaoBiologicaException):
            SinaisVitais(
                temperatura=37.0,
                pressao_sistolica=120,
                pressao_diastolica=80,
                saturacao_oxigenio=40.0,
                frequencia_cardiaca=72,
            )

    def test_frequencia_cardiaca_baixa(self):
        """Deve rejeitar frequência cardíaca abaixo de 20 bpm"""
        with pytest.raises(ValidacaoBiologicaException):
            SinaisVitais(
                temperatura=37.0,
                pressao_sistolica=120,
                pressao_diastolica=80,
                saturacao_oxigenio=98.0,
                frequencia_cardiaca=15,
            )

    def test_para_dict(self, sinais_vitais_normais):
        """Deve converter sinais vitais para dicionário corretamente"""
        resultado = sinais_vitais_normais.para_dict()

        assert isinstance(resultado, dict)
        assert resultado["temperatura"] == 36.5
        assert resultado["pressao_sistolica"] == 120
        assert resultado["pressao_diastolica"] == 80
        assert resultado["saturacao_oxigenio"] == 98.0
        assert resultado["frequencia_cardiaca"] == 72
        assert resultado["dor_peito"] is False

    def test_sinais_vitais_immutavel(self, sinais_vitais_normais):
        """Sinais vitais devem ser imutáveis (frozen dataclass)"""
        with pytest.raises(AttributeError):
            sinais_vitais_normais.temperatura = 40.0


class TestClassificacaoLogica:
    """Testes para a lógica de classificação"""

    def test_classificacao_base_normal(self, sinais_vitais_normais):
        """Sinais vitais normais devem resultar em AZUL"""
        cor = _classificacao_base(sinais_vitais_normais)
        assert cor == RiskColor.BLUE

    def test_classificacao_base_febre_alta(self, sinais_vitais_febre):
        """Temperatura > 38.5°C deve resultar em LARANJA"""
        cor = _classificacao_base(sinais_vitais_febre)
        assert cor == RiskColor.ORANGE

    def test_classificacao_base_taquicardia(self, sinais_vitais_taquicardia):
        """FC > 120 bpm deve resultar em AMARELO"""
        cor = _classificacao_base(sinais_vitais_taquicardia)
        assert cor == RiskColor.YELLOW

    def test_classificacao_base_hipertensao(self, sinais_vitais_hipertensao_severa):
        """PAS > 180 mmHg deve resultar em VERMELHO"""
        cor = _classificacao_base(sinais_vitais_hipertensao_severa)
        assert cor == RiskColor.RED

    def test_classificacao_base_dor_peito(self, sinais_vitais_dor_peito):
        """Dor no peito deve resultar em VERMELHO"""
        cor = _classificacao_base(sinais_vitais_dor_peito)
        assert cor == RiskColor.RED

    def test_classificacao_base_febre_moderada(self):
        """Temperatura 37.5-38.5°C deve resultar em VERDE"""
        sinais = SinaisVitais(
            temperatura=38.0,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=72,
        )
        cor = _classificacao_base(sinais)
        assert cor == RiskColor.GREEN

    def test_classificacao_base_taquicardia_moderada(self):
        """FC 100-120 bpm deve resultar em VERDE"""
        sinais = SinaisVitais(
            temperatura=37.0,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=105,
        )
        cor = _classificacao_base(sinais)
        assert cor == RiskColor.GREEN

    def test_escalacao_saturacao_normal(self, sinais_vitais_normais):
        """Saturação >= 92% não deve escalar"""
        cor_original = RiskColor.BLUE
        cor_final = _aplicar_escalacao_saturacao(cor_original, 95.0)
        assert cor_final == RiskColor.BLUE

    def test_escalacao_saturacao_baixa(self, sinais_vitais_hipoxemia):
        """Saturação < 92% deve escalar para cima"""
        cor_original = RiskColor.BLUE
        cor_final = _aplicar_escalacao_saturacao(cor_original, 85.0)
        assert cor_final == RiskColor.GREEN

    def test_escalacao_saturacao_verde_para_amarelo(self):
        """Saturação baixa: VERDE deve virar AMARELO"""
        cor_final = _aplicar_escalacao_saturacao(RiskColor.GREEN, 85.0)
        assert cor_final == RiskColor.YELLOW

    def test_escalacao_saturacao_amarelo_para_laranja(self):
        """Saturação baixa: AMARELO deve virar LARANJA"""
        cor_final = _aplicar_escalacao_saturacao(RiskColor.YELLOW, 85.0)
        assert cor_final == RiskColor.ORANGE

    def test_escalacao_saturacao_vermelho_permanece(self):
        """Saturação baixa: VERMELHO permanece VERMELHO"""
        cor_final = _aplicar_escalacao_saturacao(RiskColor.RED, 85.0)
        assert cor_final == RiskColor.RED

    def test_classificacao_completa_normal(self, sinais_vitais_normais):
        """Classificação completa: sinais normais = AZUL"""
        cor = classificar_paciente(sinais_vitais_normais)
        assert cor == RiskColor.BLUE

    def test_classificacao_completa_com_hipoxemia(self, sinais_vitais_hipoxemia):
        """Classificação completa: AZUL + hipoxemia = VERDE"""
        cor = classificar_paciente(sinais_vitais_hipoxemia)
        assert cor == RiskColor.GREEN

    def test_classificacao_completa_febre_normal_saturacao(self, sinais_vitais_febre):
        """Classificação completa: febre + saturação normal = LARANJA"""
        cor = classificar_paciente(sinais_vitais_febre)
        assert cor == RiskColor.ORANGE

    def test_classificacao_completa_dor_peito(self, sinais_vitais_dor_peito):
        """Classificação completa: dor no peito = VERMELHO"""
        cor = classificar_paciente(sinais_vitais_dor_peito)
        assert cor == RiskColor.RED


class TestTempoEspera:
    """Testes para cálculo de tempo de espera"""

    def test_tempo_espera_vermelho(self):
        """VERMELHO deve ter tempo 0 minutos"""
        tempo = obter_tempo_espera(RiskColor.RED)
        assert tempo == 0

    def test_tempo_espera_laranja(self):
        """LARANJA deve ter tempo 10 minutos"""
        tempo = obter_tempo_espera(RiskColor.ORANGE)
        assert tempo == 10

    def test_tempo_espera_amarelo(self):
        """AMARELO deve ter tempo 30 minutos"""
        tempo = obter_tempo_espera(RiskColor.YELLOW)
        assert tempo == 30

    def test_tempo_espera_verde(self):
        """VERDE deve ter tempo 60 minutos"""
        tempo = obter_tempo_espera(RiskColor.GREEN)
        assert tempo == 60

    def test_tempo_espera_azul(self):
        """AZUL deve ter tempo 120 minutos"""
        tempo = obter_tempo_espera(RiskColor.BLUE)
        assert tempo == 120
