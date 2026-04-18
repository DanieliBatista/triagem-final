from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.auth import get_current_user
from app.application.use_cases import TriageService
from app.domain.entities import VitalSigns
from app.domain.rules import BiologicalValidationError
from app.infrastructure.repository import triage_repository

router = APIRouter(prefix="/triage", tags=["Triage"])

_service = TriageService(triage_repository)


class VitalSignsInput(BaseModel):
    temperature: float = Field(..., ge=30.0, le=45.0)
    systolic_bp: int = Field(..., ge=50, le=300)
    diastolic_bp: int = Field(..., ge=30, le=200)
    oxygen_saturation: float = Field(..., ge=50.0, le=100.0)
    heart_rate: int = Field(..., ge=20, le=300)
    chest_pain: bool = False


class TriageRequest(BaseModel):
    patient_id: str
    vital_signs: VitalSignsInput


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_triage(
    body: TriageRequest,
    _user: dict = Depends(get_current_user),
):
    vitals = VitalSigns(**body.vital_signs.model_dump())
    try:
        triage = await _service.perform_triage(body.patient_id, vitals)
    except BiologicalValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return {
        "triage_id": str(triage.id),
        "patient_id": triage.patient_id,
        "risk_color": triage.risk_color.value,
        "estimated_wait_minutes": triage.estimated_wait_minutes,
        "created_at": triage.created_at.isoformat(),
    }


@router.get("/{triage_id}")
def get_triage(
    triage_id: UUID,
    _user: dict = Depends(get_current_user),
):
    triage = _service.get_triage(triage_id)
    if not triage:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Triagem não encontrada")

    return {
        "triage_id": str(triage.id),
        "patient_id": triage.patient_id,
        "risk_color": triage.risk_color.value,
        "estimated_wait_minutes": triage.estimated_wait_minutes,
        "requires_retriage": triage.requires_retriage,
        "created_at": triage.created_at.isoformat(),
    }


@router.get("/patient/{patient_id}")
def get_patient_triage(
    patient_id: str,
    _user: dict = Depends(get_current_user),
):
    triage = _service.get_patient_triage(patient_id)
    if not triage:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Nenhuma triagem ativa")

    return {
        "triage_id": str(triage.id),
        "risk_color": triage.risk_color.value,
        "estimated_wait_minutes": triage.estimated_wait_minutes,
        "requires_retriage": triage.requires_retriage,
    }


@router.get("/capacity/status")
def capacity_status(_user: dict = Depends(get_current_user)):
    """RF03 – Alerta de superlotação."""
    return _service.check_capacity()