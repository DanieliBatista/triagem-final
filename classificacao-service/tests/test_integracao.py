"""Testes de integração para endpoints HTTP"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch


class TestIntegracaoEndpoints:
    """Testes de integração para endpoints da API"""

    @pytest.mark.asyncio
    async def test_criar_classificacao_payload(self):
        """Validar payload de criação de classificação"""
        from app.api.schemas import CriarClassificacaoRequest, SinaisVitaisInput
        
        # Deve criar request válida
        vitais = SinaisVitaisInput(
            temperatura=37.0,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=72,
            dor_peito=False,
        )
        
        request = CriarClassificacaoRequest(
            paciente_id="PAC-001",
            vital_signs=vitais,
        )
        
        assert request.paciente_id == "PAC-001"
        assert request.vital_signs.temperatura == 37.0

    @pytest.mark.asyncio
    async def test_reclassificar_payload(self):
        """Validar payload de reclassificação"""
        from app.api.schemas import ReclassificarRequest
        
        request = ReclassificarRequest(
            nova_cor="VERMELHO",
            justificativa="Piora clínica observada",
        )
        
        assert request.nova_cor == "VERMELHO"
        assert len(request.justificativa) >= 5

    @pytest.mark.asyncio
    async def test_status_capacidade_payload(self):
        """Validar payload de status de capacidade"""
        from app.api.schemas import StatusCapacidadeResponse
        
        status = StatusCapacidadeResponse(
            pacientes_criticos=5,
            limite_capacidade=10,
            alerta=None,
        )
        
        assert status.pacientes_criticos == 5
        assert status.alerta is None

    @pytest.mark.asyncio
    async def test_status_capacidade_com_alerta(self):
        """Validar status com alerta de capacidade crítica"""
        from app.api.schemas import StatusCapacidadeResponse
        
        status = StatusCapacidadeResponse(
            pacientes_criticos=11,
            limite_capacidade=10,
            alerta="CAPACIDADE_CRITICA",
        )
        
        assert status.pacientes_criticos == 11
        assert status.alerta == "CAPACIDADE_CRITICA"

    @pytest.mark.asyncio
    async def test_classificacao_response_payload(self):
        """Validar payload de resposta de classificação"""
        from app.api.schemas import ClassificacaoResponse
        
        resposta = ClassificacaoResponse(
            id="cls-001",
            paciente_id="PAC-001",
            cor_risco="AZUL",
            tempo_espera_minutos=120,
            status="ATIVO",
            tipo_mudanca="AUTOMATICA",
            usuario_id="medico-001",
            data_criacao="2026-04-29T10:00:00Z",
            data_atualizacao="2026-04-29T10:00:00Z",
            requer_retriage=False,
        )
        
        assert resposta.id == "cls-001"
        assert resposta.cor_risco == "AZUL"
        assert resposta.status == "ATIVO"

    def test_imports_principais(self):
        """Deve importar módulos principais sem erro"""
        from app.domain.entities import Classificacao
        from app.domain.enums import RiskColor
        from app.domain.value_objects import SinaisVitais
        from app.application.commands import (
            CriarClassificacaoCommand,
            CriarClassificacaoManipulador,
        )
        from app.application.queries.obter_classificacao_atual import (
            ObterClassificacaoQuery,
            ObterClassificacaoManipulador,
        )
        
        assert Classificacao is not None
        assert RiskColor is not None
        assert SinaisVitais is not None
        assert CriarClassificacaoCommand is not None
        assert ObterClassificacaoQuery is not None

    def test_enums_risco(self):
        """Deve ter enum de cores de risco correto"""
        from app.domain.enums import RiskColor
        
        assert RiskColor.RED.value == "VERMELHO"
        assert RiskColor.ORANGE.value == "LARANJA"
        assert RiskColor.YELLOW.value == "AMARELO"
        assert RiskColor.GREEN.value == "VERDE"
        assert RiskColor.BLUE.value == "AZUL"

    def test_enums_status(self):
        """Deve ter enum de status correto"""
        from app.domain.enums import StatusClassificacao
        
        assert StatusClassificacao.ATIVO.value == "ATIVO"
        assert StatusClassificacao.EXPIRADO.value == "EXPIRADO"
        assert StatusClassificacao.COMPLETO.value == "COMPLETO"

    def test_enums_tipo_mudanca(self):
        """Deve ter enum de tipo de mudança correto"""
        from app.domain.enums import TipoMudanca
        
        assert TipoMudanca.AUTOMATICA.value == "AUTOMATICA"
        assert TipoMudanca.MANUAL.value == "MANUAL"
        assert TipoMudanca.ESCALACAO.value == "ESCALACAO"

    def test_reclassificar_request_validacao(self):
        """Validar que ReclassificarRequest rejeita justificativa curta"""
        from app.api.schemas import ReclassificarRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ReclassificarRequest(
                nova_cor="VERMELHO",
                justificativa="ok",  # Menos de 5 caracteres
            )
