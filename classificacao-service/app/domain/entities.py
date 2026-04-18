from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RiskColor(str, Enum):
    RED = "VERMELHO"       # Emergência – imediato
    ORANGE = "LARANJA"     # Muito Urgente – 10 min
    YELLOW = "AMARELO"     # Urgente – 30 min
    GREEN = "VERDE"        # Pouco Urgente – 60 min
    BLUE = "AZUL"          # Não Urgente – 120 min


WAIT_MINUTES: dict[RiskColor, int] = {
    RiskColor.RED: 0,
    RiskColor.ORANGE: 10,
    RiskColor.YELLOW: 30,
    RiskColor.GREEN: 60,
    RiskColor.BLUE: 120,
}

TRIAGE_VALIDITY_HOURS = 4


@dataclass
class VitalSigns:
    temperature: float          # °C
    systolic_bp: int            # mmHg
    diastolic_bp: int           # mmHg
    oxygen_saturation: float    # %
    heart_rate: int             # bpm
    chest_pain: bool = False


@dataclass
class Triage:
    patient_id: str
    vital_signs: VitalSigns
    risk_color: RiskColor
    estimated_wait_minutes: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utcnow)
    requires_retriage: bool = False

    def check_expiration(self) -> None:
        expiry = self.created_at + timedelta(hours=TRIAGE_VALIDITY_HOURS)
        if _utcnow() > expiry:
            self.requires_retriage = True