"""Main application para Triagem Service"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.auth import obter_usuario_atual
from app.application.use_cases import RealizarTriagemUseCase
from app.domain.rules import ValidacaoBiologicaException
from app.infrastructure.clients.classificacao_client import ClassificacaoClientException
from app.infrastructure.database import criar_tabelas

# Criar tabelas no banco de dados
criar_tabelas()

# FastAPI app
app = FastAPI(
    title="Microsserviço de Triagem",
    description="Serviço responsável por coletar sinais vitais iniciais e solicitar classificação",
    version="1.0.0",
)


# Pydantic Models
class TriagemRequest(BaseModel):
    """Request model para realizar triagem"""
    paciente_id: str = Field(..., description="ID do paciente")
    temperatura: float = Field(..., ge=30.0, le=45.0, description="Temperatura em °C")
    pressao_sistolica: int = Field(..., ge=50, le=300, description="Pressão sistólica em mmHg")
    pressao_diastolica: int = Field(..., ge=30, le=200, description="Pressão diastólica em mmHg")
    saturacao_oxigenio: float = Field(..., ge=50.0, le=100.0, description="Saturação O2 em %")
    frequencia_cardiaca: int = Field(..., ge=20, le=300, description="Frequência cardíaca em bpm")
    dor_peito: bool = Field(default=False, description="Apresenta dor no peito?")


class SinaisVitaisResponse(BaseModel):
    """Response model com sinais vitais coletados"""
    temperatura: float
    pressao_sistolica: int
    pressao_diastolica: int
    saturacao_oxigenio: float
    frequencia_cardiaca: int
    dor_peito: bool


class ClassificacaoResponse(BaseModel):
    """Response model com dados de classificação retornados do Classificação Service"""
    id: str
    paciente_id: str
    cor_risco: str
    tempo_espera_minutos: int
    status: str
    tipo_mudanca: str
    usuario_id: str
    data_criacao: str
    data_atualizacao: str
    requer_retriage: bool
    sinais_vitais: Optional[Dict[str, Any]] = None


class TriagemResponse(BaseModel):
    """Response model para triagem realizada com sucesso"""
    triagem_id: str
    paciente_id: str
    sinais_vitais: SinaisVitaisResponse
    classificacao: ClassificacaoResponse
    usuario_id: str
    data_criacao: str
    status: str


# Dependency para obter use case
def obter_use_case() -> RealizarTriagemUseCase:
    """Factory para obter instância do use case"""
    return RealizarTriagemUseCase()


# Endpoints
@app.post(
    "/v1/triagem",
    response_model=TriagemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Triagem"],
)
async def realizar_triagem(
    body: TriagemRequest,
    usuario=Depends(obter_usuario_atual),
    request: Request = None,
    use_case: RealizarTriagemUseCase = Depends(obter_use_case),
) -> Dict[str, Any]:
    """
    Realizar triagem de um paciente

    Coleta sinais vitais iniciais e solicita classificação para o Classificação Service.
    A triagem é persistida localmente e retorna os dados da classificação obtida.

    Args:
        body: TriagemRequest com sinais vitais
        usuario: Usuário autenticado via JWT
        request: Requisição HTTP (para obter IP de origem)
        use_case: Use case para executar triagem

    Returns:
        TriagemResponse com dados da triagem + classificação

    Raises:
        422: Sinais vitais fora dos limites biológicos
        503: Erro ao comunicar com Classificação Service
        500: Erro interno do servidor
    """
    try:
        # Extrair token do header
        token = None
        if request and request.headers.get("authorization"):
            auth_header = request.headers.get("authorization")
            if auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]

        # Executar use case
        resultado = await use_case.executar(
            paciente_id=body.paciente_id,
            temperatura=body.temperatura,
            pressao_sistolica=body.pressao_sistolica,
            pressao_diastolica=body.pressao_diastolica,
            saturacao_oxigenio=body.saturacao_oxigenio,
            frequencia_cardiaca=body.frequencia_cardiaca,
            dor_peito=body.dor_peito,
            usuario_id=usuario.get("sub"),
            token=token,
            ip_origem=request.client.host if request else "",
        )

        return resultado

    except ValidacaoBiologicaException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except ClassificacaoClientException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Classificação Service indisponível: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar triagem: {str(e)}",
        )


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "triagem-service"}