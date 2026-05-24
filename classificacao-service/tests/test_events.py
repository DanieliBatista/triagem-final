"""Testes para eventos (Event Sourcing)"""
import pytest
from datetime import datetime
from app.application.commands.criar_classificacao import ClassificacaoCriadaEvento
from app.application.commands.reclassificar_manualmente import (
    ClassificacaoAlteradaManualmenteEvento,
)


class TestEventos:
    """Testes para eventos de domínio"""

    def test_classificacao_criada_evento_criar(self):
        """Deve criar evento de classificação criada"""
        evento = ClassificacaoCriadaEvento(
            classificacao_id="cls-001",
            paciente_id="PAC-001",
            cor_risco="AZUL",
            tempo_espera_minutos=120,
            usuario_id="medico-001",
        )

        assert evento.classificacao_id == "cls-001"
        assert evento.paciente_id == "PAC-001"
        assert evento.cor_risco == "AZUL"
        assert evento.timestamp is not None

    def test_classificacao_criada_evento_para_dict(self):
        """Evento de classificação criada deve serializar para dict"""
        evento = ClassificacaoCriadaEvento(
            classificacao_id="cls-001",
            paciente_id="PAC-001",
            cor_risco="AZUL",
            tempo_espera_minutos=120,
            usuario_id="medico-001",
        )

        resultado = evento.para_dict()

        assert resultado["tipo_evento"] == "classificacao.criada"
        assert resultado["versao"] == "1.0"
        assert resultado["dados"]["classificacao_id"] == "cls-001"
        assert resultado["dados"]["paciente_id"] == "PAC-001"
        assert resultado["dados"]["cor_risco"] == "AZUL"
        assert resultado["dados"]["tempo_espera_minutos"] == 120
        assert "timestamp" in resultado

    def test_classificacao_alterada_manualmente_evento_criar(self):
        """Deve criar evento de classificação alterada manualmente"""
        evento = ClassificacaoAlteradaManualmenteEvento(
            classificacao_id="cls-001",
            paciente_id="PAC-001",
            cor_anterior="AZUL",
            cor_nova="VERMELHO",
            usuario_id="medico-001",
            usuario_email="medico@hospital.com",
            justificativa="Piora clínica",
        )

        assert evento.classificacao_id == "cls-001"
        assert evento.cor_anterior == "AZUL"
        assert evento.cor_nova == "VERMELHO"
        assert evento.justificativa == "Piora clínica"

    def test_classificacao_alterada_manualmente_evento_para_dict(self):
        """Evento de alteração manual deve serializar para dict"""
        evento = ClassificacaoAlteradaManualmenteEvento(
            classificacao_id="cls-001",
            paciente_id="PAC-001",
            cor_anterior="AZUL",
            cor_nova="VERMELHO",
            usuario_id="medico-001",
            usuario_email="medico@hospital.com",
            justificativa="Piora clínica",
        )

        resultado = evento.para_dict()

        assert resultado["tipo_evento"] == "classificacao.alterada.manual"
        assert resultado["versao"] == "1.0"
        assert resultado["dados"]["cor_anterior"] == "AZUL"
        assert resultado["dados"]["cor_nova"] == "VERMELHO"
        assert resultado["dados"]["justificativa"] == "Piora clínica"
        assert resultado["dados"]["usuario_email"] == "medico@hospital.com"
