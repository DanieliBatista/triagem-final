"""Event Store para auditoria completa"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.infrastructure.database import AuditoriaModel, SessionLocal


class ArmazenadorEventos:
    """Armazena todos os eventos para auditoria (RN05)"""

    def __init__(self, sessao: Session = None):
        self.sessao = sessao or SessionLocal()

    async def registrar(self, auditoria: dict) -> None:
        """RN05: Registrar auditoria completa"""
        model = AuditoriaModel(
            classificacao_id=auditoria.get("classificacao_id"),
            acao=auditoria.get("acao"),
            usuario_id=auditoria.get("usuario_id"),
            usuario_email=auditoria.get("usuario_email"),
            usuario_role=auditoria.get("usuario_role"),
            timestamp=datetime.utcnow(),
            cor_anterior=auditoria.get("cor_anterior"),
            cor_nova=auditoria.get("cor_nova"),
            justificativa=auditoria.get("justificativa"),
            ip=auditoria.get("ip"),
        )

        self.sessao.add(model)
        self.sessao.commit()

    async def obter_por_classificacao(self, classificacao_id: str) -> list:
        """Obter todo o histórico de auditoria de uma classificação"""
        models = self.sessao.query(AuditoriaModel).filter(
            AuditoriaModel.classificacao_id == classificacao_id
        ).order_by(AuditoriaModel.timestamp.asc()).all()

        return [
            {
                "acao": m.acao,
                "usuario_id": m.usuario_id,
                "usuario_email": m.usuario_email,
                "usuario_role": m.usuario_role,
                "timestamp": m.timestamp.isoformat(),
                "cor_anterior": m.cor_anterior,
                "cor_nova": m.cor_nova,
                "justificativa": m.justificativa,
                "ip": m.ip,
            }
            for m in models
        ]

    def fechar(self):
        """Fechar sessão"""
        self.sessao.close()
