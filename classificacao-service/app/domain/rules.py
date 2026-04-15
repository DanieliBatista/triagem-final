from .entities import RiskColor, VitalSigns, WAIT_MINUTES

VITAL_LIMITS = {
    "temperature": (30.0, 45.0),
    "systolic_bp": (50, 300),
    "diastolic_bp": (30, 200),
    "oxygen_saturation": (50.0, 100.0),
    "heart_rate": (20, 300),
}


class BiologicalValidationError(ValueError):
    pass


def validate_vital_signs(vitals: VitalSigns) -> None:
    checks = {
        "temperature": vitals.temperature,
        "systolic_bp": vitals.systolic_bp,
        "diastolic_bp": vitals.diastolic_bp,
        "oxygen_saturation": vitals.oxygen_saturation,
        "heart_rate": vitals.heart_rate,
    }
    for field, value in checks.items():
        lo, hi = VITAL_LIMITS[field]
        if not (lo <= value <= hi):
            raise BiologicalValidationError(
                f"{field} fora do limite humano possível: {value} (esperado: {lo}–{hi})"
            )


def classify_patient(vitals: VitalSigns) -> RiskColor:
    color = _base_classification(vitals)
    color = _apply_saturation_escalation(color, vitals.oxygen_saturation)
    return color


def _base_classification(vitals: VitalSigns) -> RiskColor:
    if vitals.chest_pain or vitals.systolic_bp > 180:
        return RiskColor.RED

    if vitals.temperature > 38.5:
        return RiskColor.ORANGE

    if vitals.heart_rate > 120 or vitals.systolic_bp > 160:
        return RiskColor.YELLOW

    if vitals.temperature > 37.5 or vitals.heart_rate > 100:
        return RiskColor.GREEN

    return RiskColor.BLUE


def _apply_saturation_escalation(color: RiskColor, saturation: float) -> RiskColor:
    if saturation >= 92.0:
        return color

    escalation = {
        RiskColor.BLUE: RiskColor.GREEN,
        RiskColor.GREEN: RiskColor.YELLOW,
        RiskColor.YELLOW: RiskColor.ORANGE,
        RiskColor.ORANGE: RiskColor.RED,
        RiskColor.RED: RiskColor.RED,
    }
    return escalation[color]


def calculate_wait_minutes(color: RiskColor) -> int:
    return WAIT_MINUTES[color]