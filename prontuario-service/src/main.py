from src.infrastructure.database import Base, get_db, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from src.infrastructure.repository import ProntuarioRepository
from src.application.use_cases import ProntuarioUseCase
from src.infrastructure.auth import get_current_user_role
from pydantic import BaseModel
from typing import List
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microsserviço de Prontuário e Histórico Médico")

repo = ProntuarioRepository()
use_case = ProntuarioUseCase(repo)
class ProntuarioCreate(BaseModel):
    paciente_id: str
    medico_id: str
    anamnese: str
    prescricoes: List[str]


@app.get("/")
def read_root():
    return {"message": "Serviço de Prontuário Ativo"}

@app.post("/prontuarios", status_code=status.HTTP_201_CREATED)
def criar_prontuario(
    dados: ProntuarioCreate, 
    role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        resultado = use_case.registrar_atendimento(db, dados.model_dump(), role)
        return {"status": "Sucesso", "data": resultado}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/prontuarios/{paciente_id}/alta")
def obter_sumario_alta(
    paciente_id: str, 
    role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
):
    try:
        historico = use_case.obter_historico(db, paciente_id, role)
        if not historico:
            raise HTTPException(status_code=404, detail="Histórico não encontrado.")
        return historico
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))