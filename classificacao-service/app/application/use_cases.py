import os
from uuid import UUID

from app.domain.entities import Triage, VitalSigns
from app.domain.rules import (
    BiologicalValidationError,
    calculate_wait_minutes,
    classify_patient,
    validate_vital_signs,
)
from app.infrastructure.event_publisher import publish_triage_completed
from app.infrastructure.repository import TriageRepository

CRITICAL_CAPACITY_LIMIT = int(os.getenv("CRITICAL_CAPACITY_LIMIT", "10"))


class TriageService:
    def __init__(self, repo: TriageRepository) -> None:
        self._repo = repo

    async def perform_triage(self, patient_id: str, vitals: VitalSigns) -> Triage:
        validate_vital_signs(vitals) 

        risk_color = classify_patient(vitals)
        wait = calculate_wait_minutes(risk_color)

        triage = Triage(
            patient_id=patient_id,
            vital_signs=vitals,
            risk_color=risk_color,
            estimated_wait_minutes=wait,
        )
        self._repo.save(triage)
        await publish_triage_completed(triage)
        return triage

    def get_triage(self, triage_id: UUID) -> Triage | None:
        triage = self._repo.find_by_id(triage_id)
        if triage:
            triage.check_expiration()
        return triage

    def get_patient_triage(self, patient_id: str) -> Triage | None:
        return self._repo.find_active_by_patient(patient_id)

    def check_capacity(self) -> dict:
        count = self._repo.count_critical()
        is_critical = count >= CRITICAL_CAPACITY_LIMIT
        return {
            "critical_patients": count,
            "capacity_limit": CRITICAL_CAPACITY_LIMIT,
            "alert": "CAPACIDADE_CRITICA" if is_critical else None,
        }