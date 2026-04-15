import pytest
from app.domain.entities import RiskColor
from app.domain.rules import (
    BiologicalValidationError,
    classify_patient,
    validate_vital_signs,
    calculate_wait_minutes,
)
from app.domain.entities import VitalSigns


def make_vitals(**overrides) -> VitalSigns:
    defaults = dict(
        temperature=36.5,
        systolic_bp=120,
        diastolic_bp=80,
        oxygen_saturation=98.0,
        heart_rate=75,
        chest_pain=False,
    )
    return VitalSigns(**{**defaults, **overrides})

class TestValidateVitalSigns:
    def test_valid_vitals_pass(self):
        validate_vital_signs(make_vitals())

    def test_temperature_too_high_raises(self):
        with pytest.raises(BiologicalValidationError):
            validate_vital_signs(make_vitals(temperature=46.0))

    def test_temperature_too_low_raises(self):
        with pytest.raises(BiologicalValidationError):
            validate_vital_signs(make_vitals(temperature=29.0))

    def test_saturation_below_limit_raises(self):
        with pytest.raises(BiologicalValidationError):
            validate_vital_signs(make_vitals(oxygen_saturation=49.0))

class TestClassifyPatient:
    def test_chest_pain_is_red(self):
        assert classify_patient(make_vitals(chest_pain=True)) == RiskColor.RED

    def test_high_systolic_is_red(self):
        assert classify_patient(make_vitals(systolic_bp=181)) == RiskColor.RED

    def test_high_fever_is_orange(self):
        assert classify_patient(make_vitals(temperature=39.0)) == RiskColor.ORANGE

    def test_normal_vitals_is_blue(self):
        assert classify_patient(make_vitals()) == RiskColor.BLUE

    def test_low_saturation_escalates_blue_to_green(self):
        result = classify_patient(make_vitals(oxygen_saturation=91.0))
        assert result == RiskColor.GREEN

    def test_low_saturation_escalates_orange_to_red(self):
        result = classify_patient(make_vitals(temperature=39.0, oxygen_saturation=91.0))
        assert result == RiskColor.RED

    def test_red_stays_red_even_with_low_saturation(self):
        result = classify_patient(make_vitals(chest_pain=True, oxygen_saturation=85.0))
        assert result == RiskColor.RED

class TestCalculateWait:
    def test_red_is_immediate(self):
        assert calculate_wait_minutes(RiskColor.RED) == 0

    def test_orange_is_10_min(self):
        assert calculate_wait_minutes(RiskColor.ORANGE) == 10

    def test_blue_is_120_min(self):
        assert calculate_wait_minutes(RiskColor.BLUE) == 120