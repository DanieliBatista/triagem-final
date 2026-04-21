"""Value Objects do domain"""
from dataclasses import dataclass
from .enums import RiskColor
from .exceptions import ValidacaoBiologicaException


LIMITES_VITAIS = {
    "temperatura": (30.0, 45.0),
    "pressao_sistolica": (50, 300),
    "pressao_diastolica": (30, 200),
    "saturacao_oxigenio": (50.0, 100.0),
    "frequencia_cardiaca": (20, 300),
}


@dataclass(frozen=True)
class SinaisVitais:
    """Sinais vitais do paciente - Value Object (imutável)"""
    temperatura: float
    pressao_sistolica: int
    pressao_diastolica: int
    saturacao_oxigenio: float
    frequencia_cardiaca: int
    dor_peito: bool = False

    def __post_init__(self):
        """Validar sinais vitais após inicialização"""
        validacoes = {
            "temperatura": self.temperatura,
            "pressao_sistolica": self.pressao_sistolica,
            "pressao_diastolica": self.pressao_diastolica,
            "saturacao_oxigenio": self.saturacao_oxigenio,
            "frequencia_cardiaca": self.frequencia_cardiaca,
        }

        for campo, valor in validacoes.items():
            min_val, max_val = LIMITES_VITAIS[campo]
            if not (min_val <= valor <= max_val):
                raise ValidacaoBiologicaException(
                    f"{campo} fora do limite humano possível: {valor} "
                    f"(esperado: {min_val}–{max_val})"
                )

    def para_dict(self) -> dict:
        """Converter para dicionário"""
        return {
            "temperatura": self.temperatura,
            "pressao_sistolica": self.pressao_sistolica,
            "pressao_diastolica": self.pressao_diastolica,
            "saturacao_oxigenio": self.saturacao_oxigenio,
            "frequencia_cardiaca": self.frequencia_cardiaca,
            "dor_peito": self.dor_peito,
        }


def classificar_paciente(sinais: SinaisVitais) -> RiskColor:
    """
    Classificar paciente segundo Protocolo de Manchester

    RN02: Lógica de Priorização
    - Dor no peito OU PAS > 180 → VERMELHO
    - Febre > 38.5°C → LARANJA
    - FC > 120 OU PAS > 160 → AMARELO
    - Febre > 37.5 OU FC > 100 → VERDE
    - Caso contrário → AZUL
    - Se SpO2 < 92% → Escala uma categoria acima
    """
    cor = _classificacao_base(sinais)
    cor = _aplicar_escalacao_saturacao(cor, sinais.saturacao_oxigenio)
    return cor


def _classificacao_base(sinais: SinaisVitais) -> RiskColor:
    """Classificação base sem considerar saturação"""
    if sinais.dor_peito or sinais.pressao_sistolica > 180:
        return RiskColor.RED

    if sinais.temperatura > 38.5:
        return RiskColor.ORANGE

    if sinais.frequencia_cardiaca > 120 or sinais.pressao_sistolica > 160:
        return RiskColor.YELLOW

    if sinais.temperatura > 37.5 or sinais.frequencia_cardiaca > 100:
        return RiskColor.GREEN

    return RiskColor.BLUE


def _aplicar_escalacao_saturacao(cor: RiskColor, saturacao: float) -> RiskColor:
    """Aplicar escalação automática se saturação < 92%"""
    if saturacao >= 92.0:
        return cor

    escalacao = {
        RiskColor.BLUE: RiskColor.GREEN,
        RiskColor.GREEN: RiskColor.YELLOW,
        RiskColor.YELLOW: RiskColor.ORANGE,
        RiskColor.ORANGE: RiskColor.RED,
        RiskColor.RED: RiskColor.RED,
    }
    return escalacao[cor]


def obter_tempo_espera(cor: RiskColor) -> int:
    """Obter tempo estimado de espera em minutos"""
    tempos = {
        RiskColor.RED: 0,
        RiskColor.ORANGE: 10,
        RiskColor.YELLOW: 30,
        RiskColor.GREEN: 60,
        RiskColor.BLUE: 120,
    }
    return tempos[cor]
