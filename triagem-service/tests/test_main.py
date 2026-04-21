import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

# Importações do seu projeto
from app.main import app, obter_use_case
from app.api.auth import obter_usuario_atual
from app.application.use_cases import RealizarTriagemUseCase
from app.infrastructure.clients.classificacao_client import ClassificacaoClient, ClassificacaoClientException
from app.infrastructure.repositories import RepositorioTriagem
from app.domain.rules import validar_sinais_vitais, ValidacaoBiologicaException

def override_obter_usuario_atual():
    return{"sub": "medico-teste-123"}
app.dependency_overrides[obter_usuario_atual] = override_obter_usuario_atual
client = TestClient(app)

@pytest.fixture
def mock_classificacao_client():
    mock = AsyncMock(spec=ClassificacaoClient)
    mock.criar_classificacao.return_value = {
        "id": "classificacao-teste-123",
        "paciente_id": "paciente-teste-123",
        "cor_risco": "VERMELHO",
        "tempo_espera_minutos": 0,
        "status": "PENDENTE",
        "tipo_mudanca": "NENHUMA",
        "usuario_id": "medico-teste-123",
        "data_criacao": "2026-04-10T10:00:00",
        "data_atualizacao": "2026-04-10T10:00:00",
        "requer_retriage": False
    }
    return mock
@pytest.fixture
def mock_repositorio():
    mock = AsyncMock(spec=RepositorioTriagem)
    # Fingimos que o banco de dados salvou com sucesso e gerou um ID
    mock_model = MagicMock()
    mock_model.id = "triagem-salva-789"
    mock_model.data_criacao = datetime.now()
    mock.salvar.return_value = mock_model
    return mock

# 4. Injetar os Dublês no Caso de Uso Real
@pytest.fixture
def override_use_case(mock_classificacao_client, mock_repositorio):
    use_case = RealizarTriagemUseCase(
        classificacao_client=mock_classificacao_client,
        repositorio=mock_repositorio
    )
    app.dependency_overrides[obter_use_case] = lambda: use_case
    return use_case

# ========================== TESTES DA API ==========================

def test_health_check():
    """Testa se o servidor está vivo"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "triagem-service"}

def test_realizar_triagem_sucesso(override_use_case):
    """O Caminho Feliz: Testa toda a rota, o use_case e a regra de negócio de uma vez!"""
    payload = {
        "paciente_id": "pac-456",
        "temperatura": 37.0,
        "pressao_sistolica": 120,
        "pressao_diastolica": 80,
        "saturacao_oxigenio": 98.0,
        "frequencia_cardiaca": 75,
        "dor_peito": False
    }
    
    # Fazemos um POST simulando a requisição do Postman
    response = client.post("/v1/triagem", json=payload, headers={"Authorization": "Bearer token-falso"})
    
    # Tem que retornar 201 Created!
    assert response.status_code == 201
    data = response.json()
    assert data["triagem_id"] == "triagem-salva-789"
    assert data["classificacao"]["cor_risco"] == "VERMELHO"

def test_realizar_triagem_falha_comunicacao(mock_classificacao_client, mock_repositorio):
    """Testa se o sistema devolve o Erro 503 (Serviço Indisponível) se o microsserviço do Bruno cair"""
    # Forçamos o cliente a dar erro de Timeout
    mock_classificacao_client.criar_classificacao.side_effect = ClassificacaoClientException("Timeout")
    
    use_case = RealizarTriagemUseCase(classificacao_client=mock_classificacao_client, repositorio=mock_repositorio)
    app.dependency_overrides[obter_use_case] = lambda: use_case

    payload = {"paciente_id": "pac-456", "temperatura": 37.0, "pressao_sistolica": 120, "pressao_diastolica": 80, "saturacao_oxigenio": 98.0, "frequencia_cardiaca": 75, "dor_peito": False}
    
    response = client.post("/v1/triagem", json=payload)
    
    assert response.status_code == 503
    assert "Classificação Service indisponível" in response.json()["detail"]

def test_sinais_vitais_dentro_do_limite_biologico():
    validar_sinais_vitais(
        temperatura=36.5,
        pressao_sistolica=120,
        pressao_diastolica=80,
        saturacao_oxigenio=98.0,
        frequencia_cardiaca=75
    )

def test_temperatura_fora_do_limite_deve_falhar():
    with pytest.raises(ValidacaoBiologicaException) as erro:
        validar_sinais_vitais(
            temperatura=50.0, 
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=75
        )
    assert "Temperatura 50.0°C fora do intervalo" in str(erro.value)

def test_pressao_sistolica_absurda_deve_falhar():
    with pytest.raises(ValidacaoBiologicaException) as erro:
        validar_sinais_vitais(
            temperatura=36.5,
            pressao_sistolica=500,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=75
        )
    assert "Pressão sistólica 500 mmHg fora do intervalo" in str(erro.value)