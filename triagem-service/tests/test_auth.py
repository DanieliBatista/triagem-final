import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api import auth


def test_token_assinado_com_segredo_configurado_e_aceito(monkeypatch):
    monkeypatch.setattr(auth.settings, "JWT_SECRET", "segredo-compartilhado")
    token = jwt.encode(
        {"sub": "medico@hospital.com", "role": "MEDICO"},
        "segredo-compartilhado",
        algorithm=auth.settings.JWT_ALGORITHM,
    )

    usuario = auth.get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))

    assert usuario["sub"] == "medico@hospital.com"
    assert usuario["role"] == "MEDICO"


def test_token_assinado_com_outro_segredo_e_rejeitado(monkeypatch):
    monkeypatch.setattr(auth.settings, "JWT_SECRET", "segredo-esperado")
    token = jwt.encode({"sub": "medico@hospital.com"}, "segredo-incorreto", algorithm="HS256")

    with pytest.raises(HTTPException) as erro:
        auth.get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))

    assert erro.value.status_code == 401
