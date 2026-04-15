from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.application.use_cases import RealizarTriagemUseCase 

app = FastAPI(title="Microsserviço de Triagem")
use_case = RealizarTriagemUseCase() 

class TriagemRequest(BaseModel):
    paciente_id: int
    temperatura: float
    peso: float
    pressao_sistolica: int
    dor_peito: bool

@app.post("/v1/triagem")
async def realizar_triagem(dados: TriagemRequest):
    try:
        resultado = use_case.executar(
            dados.paciente_id, 
            dados.temperatura, 
            dados.pressao_sistolica, 
            dados.dor_peito
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))