"""Repositório para Triagem com SQLAlchemy"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.database import TriagemModel, SessionLocal


class RepositorioTriagem:
    """Repositório para operações de Triagem"""

    def __init__(self, sessao: Optional[Session] = None):
        self.sessao = sessao or SessionLocal()

    async def salvar(self, triagem_data: dict) -> TriagemModel:
        """
        Salvar nova triagem no banco de dados

        Args:
            triagem_data: Dicionário com dados da triagem

        Returns:
            TriagemModel salvo com ID atribuído
        """
        model = TriagemModel(
            paciente_id=triagem_data["paciente_id"],
            temperatura=triagem_data["temperatura"],
            pressao_sistolica=triagem_data["pressao_sistolica"],
            pressao_diastolica=triagem_data["pressao_diastolica"],
            saturacao_oxigenio=triagem_data["saturacao_oxigenio"],
            frequencia_cardiaca=triagem_data["frequencia_cardiaca"],
            dor_peito=triagem_data.get("dor_peito", False),
            classificacao_id=triagem_data.get("classificacao_id"),
            usuario_id=triagem_data["usuario_id"],
            ip_origem=triagem_data.get("ip_origem"),
        )

        self.sessao.add(model)
        self.sessao.commit()
        self.sessao.refresh(model)

        return model

    async def obter_por_id(self, triagem_id: str) -> Optional[TriagemModel]:
        """Obter triagem por ID"""
        return self.sessao.query(TriagemModel).filter(
            TriagemModel.id == triagem_id
        ).first()

    async def obter_por_paciente(self, paciente_id: str) -> List[TriagemModel]:
        """Obter todas as triagens de um paciente"""
        return self.sessao.query(TriagemModel).filter(
            TriagemModel.paciente_id == paciente_id
        ).order_by(TriagemModel.data_criacao.desc()).all()

    def converter_model_para_dict(self, model: TriagemModel) -> dict:
        """Converter ORM Model para dicionário"""
        return {
            "id": model.id,
            "paciente_id": model.paciente_id,
            "temperatura": model.temperatura,
            "pressao_sistolica": model.pressao_sistolica,
            "pressao_diastolica": model.pressao_diastolica,
            "saturacao_oxigenio": model.saturacao_oxigenio,
            "frequencia_cardiaca": model.frequencia_cardiaca,
            "dor_peito": model.dor_peito,
            "classificacao_id": model.classificacao_id,
            "usuario_id": model.usuario_id,
            "ip_origem": model.ip_origem,
            "data_criacao": model.data_criacao.isoformat(),
        }

    def fechar(self):
        """Fechar sessão"""
        self.sessao.close()
