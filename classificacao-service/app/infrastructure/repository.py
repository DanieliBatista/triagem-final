from uuid import UUID
from app.domain.entities import Triage, RiskColor


class TriageRepository:

    def __init__(self) -> None:
        self._store: dict[UUID, Triage] = {}

    def save(self, triage: Triage) -> None:
        self._store[triage.id] = triage

    def find_by_id(self, triage_id: UUID) -> Triage | None:
        return self._store.get(triage_id)

    def find_active_by_patient(self, patient_id: str) -> Triage | None:
        for triage in reversed(list(self._store.values())):
            if triage.patient_id == patient_id:
                triage.check_expiration()
                return triage
        return None

    def count_critical(self) -> int:
        critical_colors = {RiskColor.RED, RiskColor.ORANGE}
        return sum(
            1 for t in self._store.values()
            if t.risk_color in critical_colors and not t.requires_retriage
        )

triage_repository = TriageRepository()