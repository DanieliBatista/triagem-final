import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.domain.entities import Classificacao
from app.domain.enums import RiskColor, StatusClassificacao, TipoMudanca
from app.domain.value_objects import SinaisVitais


class TestClassificacao:

    def test_criar_classificacao(self, classificacao_padrao):
        assert classificacao_padrao.paciente_id == "PAC-001"
        assert classificacao_padrao.cor_risco == RiskColor.BLUE
        assert classificacao_padrao.tempo_espera_minutos == 120
        assert classificacao_padrao.usuario_id == "medico-001"
        assert classificacao_padrao.status == StatusClassificacao.ATIVO
        assert classificacao_padrao.tipo_mudanca == TipoMudanca.AUTOMATICA
        assert classificacao_padrao.requer_retriage is False

    def test_classificacao_tem_uuid(self, classificacao_padrao):
        assert classificacao_padrao.id is not None
        assert len(str(classificacao_padrao.id)) == 36  # Formato UUID

    def test_classificacao_tem_timestamp_criacao(self, classificacao_padrao):
        assert classificacao_padrao.data_criacao is not None
        assert isinstance(classificacao_padrao.data_criacao, datetime)

    def test_para_dict(self, classificacao_padrao):
        resultado = classificacao_padrao.para_dict()

        assert isinstance(resultado, dict)
        assert resultado["paciente_id"] == "PAC-001"
        assert resultado["cor_risco"] == "AZUL"
        assert resultado["tempo_espera_minutos"] == 120
        assert resultado["status"] == "ATIVO"
        assert resultado["tipo_mudanca"] == "AUTOMATICA"
        assert resultado["requer_retriage"] is False
        assert "id" in resultado
        assert "data_criacao" in resultado
        assert "data_atualizacao" in resultado
        assert "sinais_vitais" in resultado

    def test_verificar_expiracao_ativa(self, classificacao_padrao):
        classificacao_padrao.verificar_expiracao()
        assert classificacao_padrao.status == StatusClassificacao.ATIVO

    @patch("app.domain.entities._utcnow")
    def test_verificar_expiracao_expirada(self, mock_utcnow, classificacao_padrao):
        tempo_criacao = datetime.now(timezone.utc) - timedelta(hours=5)
        classificacao_padrao.data_criacao = tempo_criacao
        
        mock_utcnow.return_value = tempo_criacao + timedelta(hours=5)

        classificacao_padrao.verificar_expiracao()
        assert classificacao_padrao.status == StatusClassificacao.EXPIRADO
        assert classificacao_padrao.requer_retriage is True

    def test_reclassificar(self, classificacao_padrao):

        classificacao_padrao.reclassificar(
            nova_cor=RiskColor.RED,
            novo_tempo_espera=0,
            usuario_id="medico-002",
            justificativa="Piora clínica observada",
        )

        assert classificacao_padrao.cor_risco == RiskColor.RED
        assert classificacao_padrao.tempo_espera_minutos == 0
        assert classificacao_padrao.usuario_id == "medico-002"
        assert classificacao_padrao.tipo_mudanca == TipoMudanca.MANUAL
        assert classificacao_padrao.data_atualizacao > classificacao_padrao.data_criacao

    @patch("app.domain.entities._utcnow")
    def test_escalar_azul_para_verde(self, mock_utcnow, classificacao_padrao):

        tempo_criacao = datetime.now(timezone.utc)
        classificacao_padrao.data_criacao = tempo_criacao


        mock_utcnow.return_value = tempo_criacao + timedelta(hours=4, minutes=1)

        resultado = classificacao_padrao.escalar()

        assert resultado is True
        assert classificacao_padrao.cor_risco == RiskColor.GREEN
        assert classificacao_padrao.tempo_espera_minutos == 60
        assert classificacao_padrao.tipo_mudanca == TipoMudanca.ESCALACAO

    @patch("app.domain.entities._utcnow")
    def test_escalar_verde_para_amarelo(self, mock_utcnow):
        sinais = SinaisVitais(
            temperatura=37.0,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=80,
        )

        tempo_criacao = datetime.now(timezone.utc)

        classificacao = Classificacao(
            paciente_id="PAC-001",
            sinais_vitais=sinais,
            cor_risco=RiskColor.GREEN,
            tempo_espera_minutos=60,
            usuario_id="sistema",
            tipo_mudanca=TipoMudanca.ESCALACAO,
        )
        classificacao.data_criacao = tempo_criacao

        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=61)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.YELLOW

    @patch("app.domain.entities._utcnow")
    def test_escalar_amarelo_para_laranja(self, mock_utcnow):
        sinais = SinaisVitais( 
            temperatura=37.0, pressao_sistolica=120, pressao_diastolica=80, saturacao_oxigenio=98.0, frequencia_cardiaca=80,
        )

        tempo_criacao = datetime.now(timezone.utc)

        classificacao = Classificacao(
            paciente_id="PAC-001",sinais_vitais=sinais,cor_risco=RiskColor.YELLOW, tempo_espera_minutos=30, usuario_id="sistema", tipo_mudanca=TipoMudanca.ESCALACAO,
        )
        classificacao.data_criacao = tempo_criacao

        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=31)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.ORANGE

    @patch("app.domain.entities._utcnow")
    def test_escalar_laranja_para_vermelho(self, mock_utcnow):
        sinais = SinaisVitais(
            temperatura=37.0, pressao_sistolica=120, pressao_diastolica=80, saturacao_oxigenio=98.0, frequencia_cardiaca=80,
        )

        tempo_criacao = datetime.now(timezone.utc)

        classificacao = Classificacao(
            paciente_id="PAC-001", sinais_vitais=sinais, cor_risco=RiskColor.ORANGE, tempo_espera_minutos=10, usuario_id="sistema", tipo_mudanca=TipoMudanca.ESCALACAO,
        )
        classificacao.data_criacao = tempo_criacao

        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=11)

        resultado = classificacao.escalar()

        assert resultado is True
        assert classificacao.cor_risco == RiskColor.RED

    @patch("app.domain.entities._utcnow")
    def test_escalar_vermelho_permanece_vermelho(self, mock_utcnow):
        sinais = SinaisVitais(
            temperatura=37.0, pressao_sistolica=120, pressao_diastolica=80, saturacao_oxigenio=98.0, frequencia_cardiaca=80,
        )

        tempo_criacao = datetime.now(timezone.utc)

        classificacao = Classificacao(
            paciente_id="PAC-001", sinais_vitais=sinais, cor_risco=RiskColor.RED, tempo_espera_minutos=0, usuario_id="sistema", tipo_mudanca=TipoMudanca.ESCALACAO,
        )
        classificacao.data_criacao = tempo_criacao

        mock_utcnow.return_value = tempo_criacao + timedelta(hours=10)

        resultado = classificacao.escalar()

        assert resultado is False
        assert classificacao.cor_risco == RiskColor.RED

    @patch("app.domain.entities._utcnow")
    def test_escalar_sem_mudanca_se_tempo_insuficiente(self, mock_utcnow, classificacao_padrao):
        tempo_criacao = datetime.now(timezone.utc)
        classificacao_padrao.data_criacao = tempo_criacao

        # Simular apenas 30 minutos decorridos (insuficiente para AZUL)
        mock_utcnow.return_value = tempo_criacao + timedelta(minutes=30)

        resultado = classificacao_padrao.escalar()

        assert resultado is False
        assert classificacao_padrao.cor_risco == RiskColor.BLUE
