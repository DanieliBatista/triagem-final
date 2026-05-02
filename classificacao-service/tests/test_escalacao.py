"""Testes para lógica de escalação automática"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.domain.entities import Classificacao
from app.domain.enums import RiskColor, TipoMudanca
from app.domain.value_objects import SinaisVitais


class TestEscalacaoAutomatica:
    """Testes para escalação automática de pacientes"""

    def _criar_classificacao(self, cor: RiskColor, tempo_criacao: datetime = None):
        """Helper para criar classificação com tempo customizável"""
        sinais = SinaisVitais(
            temperatura=37.0,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=80,
        )

        classificacao = Classificacao(
            paciente_id="PAC-001",
            sinais_vitais=sinais,
            cor_risco=cor,
            tempo_espera_minutos=0,
            usuario_id="sistema",
            tipo_mudanca=TipoMudanca.ESCALACAO,
        )

        if tempo_criacao:
            classificacao.data_criacao = tempo_criacao

        return classificacao

    @patch("app.domain.entities._utcnow")
    def test_escalacao_az_para_verde_apos_4_horas(self, mock_utcnow):
        """AZUL escala para VERDE após 4+ horas"""
        tempo_criacao = datetime.now(timezone.utc)
        classificacao = self._criar_classificacao(RiskColor.BLUE, tempo_criacao)

        # Simular 4 horas e 1 minuto
        mock_utcnow.return_value = tempo_criacao + timedelta(hours=4, minutes=1)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.GREEN
        assert classificacao.tipo_mudanca == TipoMudanca.ESCALACAO

    @patch("app.domain.entities._utcnow")
    def test_escalacao_az_sem_mudanca_antes_4_horas(self, mock_utcnow):
        """AZUL não escala antes de 4 horas"""
        tempo_criacao = datetime.now(timezone.utc)
        classificacao = self._criar_classificacao(RiskColor.BLUE, tempo_criacao)

        # Simular apenas 2 horas
        mock_utcnow.return_value = tempo_criacao + timedelta(hours=2)

        resultado = classificacao.escalar()

        assert resultado is False
        assert classificacao.cor_risco == RiskColor.BLUE

    @patch("app.domain.entities._utcnow")
    def test_escalacao_sequencial_az_verde_amarelo(self, mock_utcnow):
        """Escalação sequencial: AZUL → VERDE → AMARELO"""
        tempo_criacao = datetime.now(timezone.utc)

        # Criar como AZUL
        classificacao = self._criar_classificacao(RiskColor.BLUE, tempo_criacao)

        # Primeira escalação após 4+ horas
        mock_utcnow.return_value = tempo_criacao + timedelta(hours=4, minutes=1)
        assert classificacao.escalar() is True
        assert classificacao.cor_risco == RiskColor.GREEN

        # Segunda escalação após 60+ minutos da primeira
        mock_utcnow.return_value = tempo_criacao + timedelta(hours=5, minutes=1)
        assert classificacao.escalar() is True
        assert classificacao.cor_risco == RiskColor.YELLOW

    @patch("app.domain.entities._utcnow")
    def test_escalacao_verde_amarelo_apos_60_min(self, mock_utcnow):
        """VERDE escala para AMARELO após 60+ minutos"""
        tempo_criacao = datetime.now(timezone.utc)
        classificacao = self._criar_classificacao(RiskColor.GREEN, tempo_criacao)

        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=61)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.YELLOW

    @patch("app.domain.entities._utcnow")
    def test_escalacao_amarelo_laranja_apos_30_min(self, mock_utcnow):
        """AMARELO escala para LARANJA após 30+ minutos"""
        tempo_criacao = datetime.now(timezone.utc)
        classificacao = self._criar_classificacao(RiskColor.YELLOW, tempo_criacao)

        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=31)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.ORANGE

    @patch("app.domain.entities._utcnow")
    def test_escalacao_laranja_vermelho_apos_10_min(self, mock_utcnow):
        """LARANJA escala para VERMELHO após 10+ minutos"""
        tempo_criacao = datetime.now(timezone.utc)
        classificacao = self._criar_classificacao(RiskColor.ORANGE, tempo_criacao)

        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=11)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.RED

    @patch("app.domain.entities._utcnow")
    def test_escalacao_vermelho_permanece(self, mock_utcnow):
        """VERMELHO não escala"""
        tempo_criacao = datetime.now(timezone.utc)
        classificacao = self._criar_classificacao(RiskColor.RED, tempo_criacao)

        mock_utcnow.return_value = tempo_criacao + timedelta(days=1)

        resultado = classificacao.escalar()

        assert resultado is False
        assert classificacao.cor_risco == RiskColor.RED
