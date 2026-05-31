import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.api.auth import get_current_user

app.dependency_overrides[get_current_user] = lambda: {
    "sub": "medico@hospital.com",
    "role": "MEDICO"
}

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["versao"] == "1.0.0"


@patch("app.api.routes.RepositorioClassificacao")
@patch("app.infrastructure.despachador_eventos.DespachadorEventosMock")
@patch("app.api.routes.ArmazenadorEventos")
def test_criar_classificacao(mock_store, mock_desp, mock_repo):
    mock_repo_instance = AsyncMock()
    mock_repo_instance.salvar = AsyncMock()
    mock_repo.return_value = mock_repo_instance

    mock_desp_instance = AsyncMock()
    mock_desp_instance.despachar = AsyncMock()
    mock_desp.return_value = mock_desp_instance

    mock_store_instance = AsyncMock()
    mock_store.return_value = mock_store_instance

    payload = {
        "paciente_id": "PAC-001",
        "vital_signs": {
            "temperatura": 37.0,
            "pressao_sistolica": 120,
            "pressao_diastolica": 80,
            "saturacao_oxigenio": 98.0,
            "frequencia_cardiaca": 72,
            "dor_peito": False,
        }
    }

    response = client.post("/v1/classificacoes", json=payload)
    assert response.status_code == 201