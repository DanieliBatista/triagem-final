from enum import Enum


class StatusClassificacao(str, Enum):
    """Status de uma classificação"""
    ATIVO = "ATIVO"
    EXPIRADO = "EXPIRADO"
    COMPLETO = "COMPLETO"
    RETRIAGE_OBRIGATORIO = "RETRIAGE_OBRIGATORIO"


class TipoMudanca(str, Enum):
    """Tipo de mudança em uma classificação"""
    AUTOMATICA = "AUTOMATICA"
    MANUAL = "MANUAL"
    ESCALACAO = "ESCALACAO"


class RiskColor(str, Enum):
    """Cores de risco segundo Protocolo de Manchester"""
    RED = "VERMELHO"       # Emergência – imediato
    ORANGE = "LARANJA"     # Muito Urgente – 10 min
    YELLOW = "AMARELO"     # Urgente – 30 min
    GREEN = "VERDE"        # Pouco Urgente – 60 min
    BLUE = "AZUL"          # Não Urgente – 120 min


TEMPO_ESPERA_MINUTOS = {
    RiskColor.RED: 0,
    RiskColor.ORANGE: 10,
    RiskColor.YELLOW: 30,
    RiskColor.GREEN: 60,
    RiskColor.BLUE: 120,
}

TEMPO_VALIDADE_HORAS = 4
