from fastapi import FastAPI, Depends, HTTPException, status
from src.infrastructure.repository import ProntuarioRepository
from src.application.use_cases import ProntuarioUseCase
from src.infrastructure.auth import get_current_user_role
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Microsserviço de Prontuário e Histórico Médico")

# --- Instanciação dos Componentes (Injeção de Dependência manual) ---
# Em um projeto real, o repositório seria conectado a um banco de dados real.
repo = ProntuarioRepository()
use_case = ProntuarioUseCase(repo)

# --- Modelos de Dados para a API (Request bodies) ---
class ProntuarioCreate(BaseModel):
    paciente_id: str
    medico_id: str
    anamnese: str
    prescricoes: List[str]

# --- Endpoints (Rotas) ---

@app.get("/")
def read_root():
    return {"message": "Serviço de Prontuário Ativo"}

@app.post("/prontuarios", status_code=status.HTTP_201_CREATED)
def criar_prontuario(
    dados: ProntuarioCreate, 
    role: str = Depends(get_current_user_role)
):
    """
    Endpoint para registrar um novo atendimento.
    A role é extraída automaticamente do Token JWT pelo auth.py.
    """
    try:
        resultado = use_case.registrar_atendimento(dados.model_dump(), role)
        return {"status": "Sucesso", "data": resultado}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/prontuarios/{paciente_id}/alta")
def obter_sumario_alta(
    paciente_id: str, 
    role: str = Depends(get_current_user_role)
):
    """
    Regra 3: Geração de sumário de alta automático.
    """
    try:
        sumario = use_case.fechar_consulta_e_gerar_alta(paciente_id, role)
        return sumario
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/prontuarios/{paciente_id}")
def visualizar_historico(
    paciente_id: str, 
    role: str = Depends(get_current_user_role)
):
    """
    Regra 2: Controle de acesso para visualizar histórico.
    """
    try:
        historico = use_case.obter_historico(paciente_id, role)
        if not historico:
            raise HTTPException(status_code=404, detail="Histórico não encontrado.")
        return historico
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))