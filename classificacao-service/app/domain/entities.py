"""Entidades do Domain"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from .enums import StatusClassificacao, TipoMudanca, RiskColor, TEMPO_VALIDADE_HORAS
from .value_objects import SinaisVitais


def _utcnow() -> datetime:
    """Retornar timestamp UTC atual"""
    return datetime.now(timezone.utc)


@dataclass
class Classificacao:
    """Entidade que representa uma classificação de paciente"""
    paciente_id: str
    sinais_vitais: SinaisVitais
    cor_risco: RiskColor
    tempo_espera_minutos: int
    usuario_id: str = "sistema"
    tipo_mudanca: TipoMudanca = TipoMudanca.AUTOMATICA

    # Metadata
    id: UUID = field(default_factory=uuid4)
    data_criacao: datetime = field(default_factory=_utcnow)
    data_atualizacao: datetime = field(default_factory=_utcnow)
    status: StatusClassificacao = StatusClassificacao.ATIVO
    requer_retriage: bool = False

    def verificar_expiracao(self) -> None:
        """RN03: Verificar se triagem expirou (4 horas)"""
        limite = self.data_criacao + timedelta(hours=TEMPO_VALIDADE_HORAS)
        if _utcnow() > limite:
            self.status = StatusClassificacao.EXPIRADO
            self.requer_retriage = True

    def reclassificar(
        self,
        nova_cor: RiskColor,
        novo_tempo_espera: int,
        usuario_id: str,
        justificativa: str = ""
    ) -> None:
        """Reclassificar um paciente manualmente"""
        self.cor_risco = nova_cor
        self.tempo_espera_minutos = novo_tempo_espera
        self.usuario_id = usuario_id
        self.tipo_mudanca = TipoMudanca.MANUAL
        self.data_atualizacao = _utcnow()

    def escalar(self) -> bool:
        """RN06: Escalar automaticamente se tempo expirou"""
        tempo_decorrido = (_utcnow() - self.data_criacao).total_seconds() / 60

        escalacoes = {
            RiskColor.BLUE: (TEMPO_VALIDADE_HORAS * 60, RiskColor.GREEN),
            RiskColor.GREEN: (60, RiskColor.YELLOW),
            RiskColor.YELLOW: (30, RiskColor.ORANGE),
            RiskColor.ORANGE: (10, RiskColor.RED),
            RiskColor.RED: (0, RiskColor.RED),
        }

        if self.cor_risco not in escalacoes:
            return False

        tempo_limite, proxima_cor = escalacoes[self.cor_risco]

        if tempo_decorrido > tempo_limite and self.cor_risco != proxima_cor:
            self.cor_risco = proxima_cor
            self.tempo_espera_minutos = {
                RiskColor.RED: 0,
                RiskColor.ORANGE: 10,
                RiskColor.YELLOW: 30,
                RiskColor.GREEN: 60,
                RiskColor.BLUE: 120,
            }[proxima_cor]
            self.tipo_mudanca = TipoMudanca.ESCALACAO
            self.data_atualizacao = _utcnow()
            return True

        return False

    def para_dict(self) -> dict:
        """Converter entidade para dicionário"""
        return {
            "id": str(self.id),
            "paciente_id": self.paciente_id,
            "cor_risco": self.cor_risco.value,
            "tempo_espera_minutos": self.tempo_espera_minutos,
            "status": self.status.value,
            "tipo_mudanca": self.tipo_mudanca.value,
            "usuario_id": self.usuario_id,
            "data_criacao": self.data_criacao.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat(),
            "requer_retriage": self.requer_retriage,
            "sinais_vitais": self.sinais_vitais.para_dict(),
        }
