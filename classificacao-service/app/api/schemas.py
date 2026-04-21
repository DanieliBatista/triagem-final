"""Schemas Pydantic para a API"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SinaisVitaisInput(BaseModel):
    """Input de sinais vitais"""
    temperatura: float = Field(..., ge=30.0, le=45.0, description="Temperatura em °C")
    pressao_sistolica: int = Field(..., ge=50, le=300, description="Pressão sistólica em mmHg")
    pressao_diastolica: int = Field(..., ge=30, le=200, description="Pressão diastólica em mmHg")
    saturacao_oxigenio: float = Field(..., ge=50.0, le=100.0, description="Saturação O2 em %")
    frequencia_cardiaca: int = Field(..., ge=20, le=300, description="Frequência cardíaca em bpm")
    dor_peito: bool = Field(False, description="Paciente sente dor no peito?")


class CriarClassificacaoRequest(BaseModel):
    """Request para criar classificação"""
    paciente_id: str = Field(..., description="ID do paciente")
    vital_signs: SinaisVitaisInput


class ClassificacaoResponse(BaseModel):
    """Response com dados de classificação"""
    id: str
    paciente_id: str
    cor_risco: str
    tempo_espera_minutos: int
    status: str
    tipo_mudanca: str
    usuario_id: str
    data_criacao: str
    data_atualizacao: str
    requer_retriage: bool


class ReclassificarRequest(BaseModel):
    """Request para reclassificar"""
    nova_cor: str = Field(..., description="Nova cor: VERMELHO, LARANJA, AMARELO, VERDE, AZUL")
    justificativa: str = Field(..., min_length=5, description="Justificativa obrigatória")


class RelatorioResponse(BaseModel):
    """Response com relatório de classificação"""
    paciente_id: str
    classificacao_id: str
    classificacao_atual: dict
    sinais_vitais: dict
    timeline: dict
    historico_auditoria: List[dict]


class HistoricoResponse(BaseModel):
    """Response com histórico de classificações"""
    paciente_id: str
    total_classificacoes: int
    historico: List[dict]


class StatusCapacidadeResponse(BaseModel):
    """Response com status de capacidade"""
    pacientes_criticos: int
    limite_capacidade: int
    alerta: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response de erro"""
    detail: str
    status_code: int
