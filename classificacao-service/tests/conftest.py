import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities import Classificacao
from app.domain.enums import RiskColor, StatusClassificacao, TipoMudanca
from app.domain.value_objects import SinaisVitais


@pytest.fixture
def sinais_vitais_normais():
    return SinaisVitais(
        temperatura=36.5,
        pressao_sistolica=120,
        pressao_diastolica=80,
        saturacao_oxigenio=98.0,
        frequencia_cardiaca=72,
        dor_peito=False,
    )


@pytest.fixture
def sinais_vitais_febre():
    return SinaisVitais(
        temperatura=39.0,
        pressao_sistolica=120,
        pressao_diastolica=80,
        saturacao_oxigenio=98.0,
        frequencia_cardiaca=72,
        dor_peito=False,
    )


@pytest.fixture
def sinais_vitais_taquicardia():
    return SinaisVitais(
        temperatura=37.0,
        pressao_sistolica=120,
        pressao_diastolica=80,
        saturacao_oxigenio=98.0,
        frequencia_cardiaca=125,
        dor_peito=False,
    )


@pytest.fixture
def sinais_vitais_hipertensao_severa():
    return SinaisVitais(
        temperatura=37.0,
        pressao_sistolica=190,
        pressao_diastolica=100,
        saturacao_oxigenio=98.0,
        frequencia_cardiaca=80,
        dor_peito=False,
    )


@pytest.fixture
def sinais_vitais_dor_peito():
    return SinaisVitais(
        temperatura=37.0,
        pressao_sistolica=120,
        pressao_diastolica=80,
        saturacao_oxigenio=98.0,
        frequencia_cardiaca=80,
        dor_peito=True,
    )


@pytest.fixture
def sinais_vitais_hipoxemia():
    return SinaisVitais(
        temperatura=37.0,
        pressao_sistolica=120,
        pressao_diastolica=80,
        saturacao_oxigenio=85.0,
        frequencia_cardiaca=80,
        dor_peito=False,
    )


@pytest.fixture
def classificacao_padrao(sinais_vitais_normais):
    return Classificacao(
        paciente_id="PAC-001",
        sinais_vitais=sinais_vitais_normais,
        cor_risco=RiskColor.BLUE,
        tempo_espera_minutos=120,
        usuario_id="medico-001",
        tipo_mudanca=TipoMudanca.AUTOMATICA,
    )
