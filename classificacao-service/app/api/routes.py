from fastapi import APIRouter, Depends, HTTPException, status, Request
from uuid import UUID

from app.api.schemas import (
    CriarClassificacaoRequest,
    ClassificacaoResponse,
    ReclassificarRequest,
    StatusCapacidadeResponse,
)
from app.api.auth import obter_usuario_atual
from app.application.commands import (
    CriarClassificacaoCommand,
    CriarClassificacaoManipulador,
    ReclassificarManualmenteCommand,
    ReclassificarManualmenteManipulador,
)
from app.application.queries import (
    ObterClassificacaoQuery,
    ObterClassificacaoManipulador,
)
from app.domain.exceptions import (
    ValidacaoBiologicaException,
    PermissaoNegadaException,
    JustificativaObrigatoriaException,
)
from app.shared.cqrs import BarramentoComandos, BarramentoConsultas
from app.infrastructure.repositories import RepositorioClassificacao
from app.infrastructure.event_store import ArmazenadorEventos
from app.infrastructure.despachador_eventos import DespachadorEventos
from app.infrastructure.database import SessionLocal


router = APIRouter(prefix="/v1/classificacoes", tags=["Classificações"])

def obter_repositorio():
    return RepositorioClassificacao(SessionLocal())


def obter_event_store():
    return ArmazenadorEventos(SessionLocal())


def obter_despachador():
    from app.infrastructure.despachador_eventos import DespachadorEventosMock
    return DespachadorEventosMock()


def obter_bus_comandos(
    repositorio = Depends(obter_repositorio),
    event_store = Depends(obter_event_store),
    despachador = Depends(obter_despachador),
):
    bus = BarramentoComandos()
    bus.registrar(
        CriarClassificacaoCommand,
        CriarClassificacaoManipulador(repositorio, despachador)
    )
    bus.registrar(
        ReclassificarManualmenteCommand,
        ReclassificarManualmenteManipulador(repositorio, event_store, despachador)
    )
    return bus


def obter_bus_consultas(
    repositorio = Depends(obter_repositorio),
    event_store = Depends(obter_event_store),
):
    bus = BarramentoConsultas()
    bus.registrar(
        ObterClassificacaoQuery,
        ObterClassificacaoManipulador(repositorio)
    )
    return bus


@router.post("", status_code=status.HTTP_201_CREATED)
async def criar_classificacao(
    request: CriarClassificacaoRequest,
    usuario = Depends(obter_usuario_atual),
    bus = Depends(obter_bus_comandos),
):
    try:
        comando = CriarClassificacaoCommand(
            paciente_id=request.paciente_id,
            temperatura=request.vital_signs.temperatura,
            pressao_sistolica=request.vital_signs.pressao_sistolica,
            pressao_diastolica=request.vital_signs.pressao_diastolica,
            saturacao_oxigenio=request.vital_signs.saturacao_oxigenio,
            frequencia_cardiaca=request.vital_signs.frequencia_cardiaca,
            dor_peito=request.vital_signs.dor_peito,
            usuario_id=usuario.get("sub"),
        )

        resultado = await bus.executar(comando)
        return resultado

    except ValidacaoBiologicaException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status")
async def obter_status_pacientes(usuario = Depends(obter_usuario_atual)):
    from datetime import datetime
    from app.infrastructure.config import settings

    repositorio = RepositorioClassificacao(SessionLocal())

    classificacoes = await repositorio.obter_todas_ativas_ordenadas()

    criticos = await repositorio.contar_criticas()

    agora = datetime.utcnow()
    pacientes = []

    for classif in classificacoes:
        tempo_decorrido = (agora - classif.data_criacao).total_seconds() / 60

        pacientes.append({
            "classificacao_id": str(classif.id),
            "paciente_id": classif.paciente_id,
            "cor_risco": classif.cor_risco.value,
            "tempo_espera_minutos": classif.tempo_espera_minutos,
            "data_criacao": classif.data_criacao.isoformat(),
            "status": classif.status.value,
            "sinais_vitais": classif.sinais_vitais.para_dict(),
            "tempo_decorrido_minutos": round(tempo_decorrido, 2),
        })

    is_critical = criticos >= settings.CRITICAL_CAPACITY_LIMIT

    return {
        "timestamp": agora.isoformat(),
        "total_pacientes_ativos": len(classificacoes),
        "pacientes_criticos": criticos,
        "limite_capacidade": settings.CRITICAL_CAPACITY_LIMIT,
        "alerta": "CAPACIDADE_CRITICA" if is_critical else None,
        "pacientes": pacientes,
    }


@router.get("/capacity/status")
async def capacity_status(usuario = Depends(obter_usuario_atual)):

    repositorio = RepositorioClassificacao(SessionLocal())
    count = await repositorio.contar_criticas()

    from app.infrastructure.config import settings

    is_critical = count >= settings.CRITICAL_CAPACITY_LIMIT

    return {
        "pacientes_criticos": count,
        "limite_capacidade": settings.CRITICAL_CAPACITY_LIMIT,
        "alerta": "CAPACIDADE_CRITICA" if is_critical else None,
    }


@router.get("/{classificacao_id}")
async def obter_classificacao(
    classificacao_id: str,
    usuario = Depends(obter_usuario_atual),
    bus = Depends(obter_bus_consultas),
):
    try:
        consulta = ObterClassificacaoQuery(classificacao_id=classificacao_id)
        resultado = await bus.executar(consulta)
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{classificacao_id}/reclassificar", status_code=status.HTTP_200_OK)
async def reclassificar(
    classificacao_id: str,
    request: ReclassificarRequest,
    usuario = Depends(obter_usuario_atual),
    req: Request = None,
    bus = Depends(obter_bus_comandos),
):

    try:
        comando = ReclassificarManualmenteCommand(
            classificacao_id=classificacao_id,
            nova_cor=request.nova_cor,
            usuario_id=usuario.get("sub"),
            usuario_role=usuario.get("role", "PACIENTE"),
            usuario_email=usuario.get("email", "desconhecido@hospital.com"),
            justificativa=request.justificativa,
            ip_origem=req.client.host if req else "",
        )

        resultado = await bus.executar(comando)
        return resultado

    except PermissaoNegadaException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except JustificativaObrigatoriaException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
