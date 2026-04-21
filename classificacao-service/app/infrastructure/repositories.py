"""Repositório para Classificacao com SQLAlchemy"""
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.domain.entities import Classificacao
from app.domain.value_objects import SinaisVitais
from app.domain.enums import RiskColor, StatusClassificacao, TipoMudanca
from app.infrastructure.database import ClassificacaoModel, SessionLocal


class RepositorioClassificacao:
    """Repositório para operações de Classificacao"""

    def __init__(self, sessao: Optional[Session] = None):
        self.sessao = sessao or SessionLocal()

    async def salvar(self, classificacao: Classificacao) -> Classificacao:
        """Salvar ou atualizar classificação"""
        # Verificar se já existe
        model = self.sessao.query(ClassificacaoModel).filter(
            ClassificacaoModel.id == str(classificacao.id)
        ).first()

        if model:
            # Atualizar
            model.cor_risco = classificacao.cor_risco.value
            model.tempo_espera_minutos = classificacao.tempo_espera_minutos
            model.status = classificacao.status.value
            model.tipo_mudanca = classificacao.tipo_mudanca.value
            model.usuario_id = classificacao.usuario_id
            model.data_atualizacao = classificacao.data_atualizacao
            model.requer_retriage = classificacao.requer_retriage
        else:
            # Criar novo
            model = ClassificacaoModel(
                id=str(classificacao.id),
                paciente_id=classificacao.paciente_id,
                cor_risco=classificacao.cor_risco.value,
                tempo_espera_minutos=classificacao.tempo_espera_minutos,
                status=classificacao.status.value,
                tipo_mudanca=classificacao.tipo_mudanca.value,
                usuario_id=classificacao.usuario_id,
                temperatura=classificacao.sinais_vitais.temperatura,
                pressao_sistolica=classificacao.sinais_vitais.pressao_sistolica,
                pressao_diastolica=classificacao.sinais_vitais.pressao_diastolica,
                saturacao_oxigenio=classificacao.sinais_vitais.saturacao_oxigenio,
                frequencia_cardiaca=classificacao.sinais_vitais.frequencia_cardiaca,
                dor_peito=classificacao.sinais_vitais.dor_peito,
                data_criacao=classificacao.data_criacao,
                requer_retriage=classificacao.requer_retriage,
            )

        self.sessao.add(model)
        self.sessao.commit()
        self.sessao.refresh(model)

        return self._converter_model_para_entidade(model)

    async def obter_por_id(self, classificacao_id: str) -> Optional[Classificacao]:
        """Obter classificação por ID"""
        model = self.sessao.query(ClassificacaoModel).filter(
            ClassificacaoModel.id == classificacao_id
        ).first()

        if not model:
            return None

        return self._converter_model_para_entidade(model)

    async def obter_por_paciente(self, paciente_id: str) -> List[Classificacao]:
        """Obter todas as classificações de um paciente"""
        models = self.sessao.query(ClassificacaoModel).filter(
            ClassificacaoModel.paciente_id == paciente_id
        ).all()

        return [self._converter_model_para_entidade(m) for m in models]

    async def obter_ativa_por_paciente(self, paciente_id: str) -> Optional[Classificacao]:
        """Obter classificação ativa mais recente de um paciente"""
        model = self.sessao.query(ClassificacaoModel).filter(
            ClassificacaoModel.paciente_id == paciente_id,
            ClassificacaoModel.status == StatusClassificacao.ATIVO.value
        ).order_by(ClassificacaoModel.data_criacao.desc()).first()

        if not model:
            return None

        return self._converter_model_para_entidade(model)

    async def contar_criticas(self) -> int:
        """RN03: Contar classificações críticas (RED, ORANGE)"""
        cores_criticas = [RiskColor.RED.value, RiskColor.ORANGE.value]
        count = self.sessao.query(ClassificacaoModel).filter(
            ClassificacaoModel.cor_risco.in_(cores_criticas),
            ClassificacaoModel.status == StatusClassificacao.ATIVO.value
        ).count()

        return count

    async def obter_todas_ativas_ordenadas(self) -> List[Classificacao]:
        """RF03: Obter TODAS as classificações ativas ordenadas por urgência

        Ordena por:
        1. Cor de risco (VERMELHO → AZUL, mais crítica primeiro)
        2. Data de criação (mais antigas primeiro)
        """
        # Ordem de urgência (crítica para controlada)
        ordem_cores = [
            RiskColor.RED.value,       # 0 minutos
            RiskColor.ORANGE.value,    # 10 minutos
            RiskColor.YELLOW.value,    # 30 minutos
            RiskColor.GREEN.value,     # 60 minutos
            RiskColor.BLUE.value,      # 120 minutos
        ]

        # Query ordenada por prioridade da cor e data de criação
        models = self.sessao.query(ClassificacaoModel).filter(
            ClassificacaoModel.status == StatusClassificacao.ATIVO.value
        ).order_by(
            # Ordena por prioridade usando CASE (SQL case expression)
            ClassificacaoModel.cor_risco.asc(),  # Ordem alfabética de cores
            ClassificacaoModel.data_criacao.asc()  # Mais antigas primeiro
        ).all()

        # Converter e ordenar manualmente por prioridade customizada
        classificacoes = [self._converter_model_para_entidade(m) for m in models]

        # Sort customizado por ordem de urgência
        classificacoes.sort(
            key=lambda c: (ordem_cores.index(c.cor_risco.value), c.data_criacao)
        )

        return classificacoes

    def fechar(self):
        """Fechar sessão"""
        self.sessao.close()

    @staticmethod
    def _converter_model_para_entidade(model: ClassificacaoModel) -> Classificacao:
        """Converter ORM Model para entidade Domain"""
        sinais = SinaisVitais(
            temperatura=model.temperatura,
            pressao_sistolica=model.pressao_sistolica,
            pressao_diastolica=model.pressao_diastolica,
            saturacao_oxigenio=model.saturacao_oxigenio,
            frequencia_cardiaca=model.frequencia_cardiaca,
            dor_peito=model.dor_peito,
        )

        return Classificacao(
            id=UUID(model.id),
            paciente_id=model.paciente_id,
            sinais_vitais=sinais,
            cor_risco=RiskColor(model.cor_risco),
            tempo_espera_minutos=model.tempo_espera_minutos,
            usuario_id=model.usuario_id,
            tipo_mudanca=TipoMudanca(model.tipo_mudanca),
            data_criacao=model.data_criacao,
            data_atualizacao=model.data_atualizacao,
            status=StatusClassificacao(model.status),
            requer_retriage=model.requer_retriage,
        )
