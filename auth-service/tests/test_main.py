from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "auth-service"}


def test_cadastro_medico_exige_crm():
    with TestClient(app) as client:
        response = client.post(
            "/v1/auth/cadastro",
            json={
                "email": "medico-sem-crm@example.com",
                "senha": "senha123",
                "nome": "Medico Sem CRM",
                "idade": 35,
                "role": "MEDICO",
            },
        )

    assert response.status_code == 422


def test_cadastro_e_login_retornam_token():
    email = f"medico-{uuid4()}@example.com"
    payload = {
        "email": email,
        "senha": "senha123",
        "nome": "Dra. Teste",
        "idade": 35,
        "role": "MEDICO",
        "crm": "12345-SP",
    }

    with TestClient(app) as client:
        cadastro = client.post("/v1/auth/cadastro", json=payload)
        login = client.post(
            "/v1/auth/login",
            json={"email": email, "senha": payload["senha"]},
        )

    assert cadastro.status_code == 201
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]
