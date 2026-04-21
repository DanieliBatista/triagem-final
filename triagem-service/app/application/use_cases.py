"""Use cases para Triagem Service"""
from typing import Dict, Any, Optional
from app.domain.rules import validar_sinais_vitais, ValidacaoBiologicaException
from app.infrastructure.clients.classificacao_client import (
    ClassificacaoClient,
    ClassificacaoClientException,
)
from app.infrastructure.repositories import RepositorioTriagem
from app.infrastructure.database import SessionLocal


class RealizarTriagemUseCase:
    """Use case para realizar triagem completa com classificação"""

    def __init__(
        self,
        classificacao_client: Optional[ClassificacaoClient] = None,
        repositorio: Optional[RepositorioTriagem] = None,
    ):
        """
        Inicializar use case

        Args:
            classificacao_client: Cliente para comunicar com Classificação Service
            repositorio: Repositório para persistir triagem
        """
        self.classificacao_client = classificacao_client or ClassificacaoClient()
        self.repositorio = repositorio or RepositorioTriagem(SessionLocal())

    async def executar(
        self,
        paciente_id: str,
        temperatura: float,
        pressao_sistolica: int,
        pressao_diastolica: int,
        saturacao_oxigenio: float,
        frequencia_cardiaca: int,
        dor_peito: bool,
        usuario_id: str,
        token: str,
        ip_origem: str = "",
    ) -> Dict[str, Any]:
        """
        Executar triagem completa

        Args:
            paciente_id: ID do paciente
            temperatura: Temperatura em °C
            pressao_sistolica: Pressão sistólica em mmHg
            pressao_diastolica: Pressão diastólica em mmHg
            saturacao_oxigenio: Saturação O2 em %
            frequencia_cardiaca: Frequência cardíaca em bpm
            dor_peito: Se tem dor no peito
            usuario_id: ID do usuário que realizou a triagem
            token: JWT token para autenticação na Classificação Service
            ip_origem: IP de origem da requisição

        Returns:
            Dicionário com dados da triagem + classificação obtida

        Raises:
            ValidacaoBiologicaException: Se sinais vitais inválidos
            ClassificacaoClientException: Se erro ao chamar Classificação Service
        """

        # 1. Validar sinais vitais localmente (sem classificar)
        validar_sinais_vitais(
            temperatura=temperatura,
            pressao_sistolica=pressao_sistolica,
            pressao_diastolica=pressao_diastolica,
            saturacao_oxigenio=saturacao_oxigenio,
            frequencia_cardiaca=frequencia_cardiaca,
        )

        # 2. Chamar Classificação Service para obter classificação
        classificacao = await self.classificacao_client.criar_classificacao(
            paciente_id=paciente_id,
            temperatura=temperatura,
            pressao_sistolica=pressao_sistolica,
            pressao_diastolica=pressao_diastolica,
            saturacao_oxigenio=saturacao_oxigenio,
            frequencia_cardiaca=frequencia_cardiaca,
            dor_peito=dor_peito,
            token=token,
        )

        # 3. Persistir triagem no banco de dados
        triagem_data = {
            "paciente_id": paciente_id,
            "temperatura": temperatura,
            "pressao_sistolica": pressao_sistolica,
            "pressao_diastolica": pressao_diastolica,
            "saturacao_oxigenio": saturacao_oxigenio,
            "frequencia_cardiaca": frequencia_cardiaca,
            "dor_peito": dor_peito,
            "classificacao_id": classificacao.get("id"),
            "usuario_id": usuario_id,
            "ip_origem": ip_origem,
        }

        triagem_model = await self.repositorio.salvar(triagem_data)

        # 4. Retornar resultado combinado (triagem + classificação)
        sinais_vitais = {
            "temperatura": temperatura,
            "pressao_sistolica": pressao_sistolica,
            "pressao_diastolica": pressao_diastolica,
            "saturacao_oxigenio": saturacao_oxigenio,
            "frequencia_cardiaca": frequencia_cardiaca,
            "dor_peito": dor_peito,
        }

        return {
            "triagem_id": triagem_model.id,
            "paciente_id": paciente_id,
            "sinais_vitais": sinais_vitais,
            "classificacao": classificacao,
            "usuario_id": usuario_id,
            "data_criacao": triagem_model.data_criacao.isoformat(),
            "status": "Triagem concluída com classificação obtida",
        }