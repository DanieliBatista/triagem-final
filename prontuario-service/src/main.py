import os
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.use_cases import ProntuarioUseCase
from src.infrastructure.auth import get_current_user_role
from src.infrastructure.database import Base, engine, get_db
from src.infrastructure.repository import ProntuarioRepository


docs_enabled = os.getenv("APP_ENV", "DEV").upper() != "HOMOL"

app = FastAPI(
    title="Microsservico de Prontuario e Historico Medico",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

Instrumentator().instrument(app).expose(app)

repo = ProntuarioRepository()
use_case = ProntuarioUseCase(repo)


class ProntuarioCreate(BaseModel):
    paciente_id: str
    medico_id: str
    anamnese: str
    prescricoes: List[str]


@app.on_event("startup")
def inicializar_banco() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Servico de Prontuario Ativo"}


@app.get("/health", tags=["Health"])
def health() -> Dict[str, str]:
    return {"status": "healthy", "service": "prontuario-service"}


@app.post("/prontuarios", status_code=status.HTTP_201_CREATED)
def criar_prontuario(
    dados: ProntuarioCreate,
    role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
):
    try:
        resultado = use_case.registrar_atendimento(db, dados.dict(), role)
        return {"status": "Sucesso", "data": resultado}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/prontuarios/{paciente_id}/alta")
def obter_sumario_alta(
    paciente_id: str,
    role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
):
    try:
        sumario = use_case.fechar_consulta_e_gerar_alta(db, paciente_id, role)
        return sumario
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/prontuarios/{paciente_id}")
def visualizar_historico(
    paciente_id: str,
    role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
):
    try:
        historico = use_case.obter_historico(db, paciente_id, role)
        if not historico:
            raise HTTPException(status_code=404, detail="Historico nao encontrado.")
        return historico
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
