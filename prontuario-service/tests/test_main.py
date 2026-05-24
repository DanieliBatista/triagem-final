import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.main import app
from src.infrastructure.database import get_db

# CORREÇÃO 1: Importamos o nome exato que a Heloísa usou
from src.infrastructure.auth import get_current_user_role

# CORREÇÃO 2: O Mock agora devolve apenas a string "MEDICO", igual à função original
app.dependency_overrides[get_current_user_role] = lambda: "MEDICO"

# Mock do Banco de Dados para a API
def override_get_db():
    db = MagicMock()
    # Simula um prontuário existente para o GET
    mock_p = MagicMock(id=1, paciente_id="10", medico_id="M1", anamnese="Tosse", prescricoes=[], status="ABERTO")
    db.query().filter().first.return_value = mock_p
    db.query().filter().all.return_value = [mock_p]
    yield db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ========================== TESTES DA API ==========================

def test_api_criar_prontuario():
    payload = {"paciente_id": "10", "medico_id": "M1", "anamnese": "Paciente estável", "prescricoes": []}
    response = client.post("/prontuarios", json=payload)
    assert response.status_code == 201

def test_api_obter_historico():
    response = client.get("/prontuarios/10")
    assert response.status_code == 200