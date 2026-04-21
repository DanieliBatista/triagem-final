"""Evento de escalação automática"""
from dataclasses import dataclass

from app.shared.cqrs import Evento


@dataclass
class ClassificacaoEscaladaEvento(Evento):
    """Evento: Classificação foi escalada automaticamente"""
    classificacao_id: str = ""
    paciente_id: str = ""
    cor_anterior: str = ""
    cor_nova: str = ""

    def para_dict(self) -> dict:
        return {
            "tipo_evento": "classificacao.escalada",
            "versao": "1.0",
            "timestamp": self.timestamp.isoformat(),
            "dados": {
                "classificacao_id": self.classificacao_id,
                "paciente_id": self.paciente_id,
                "cor_anterior": self.cor_anterior,
                "cor_nova": self.cor_nova,
            }
        }
