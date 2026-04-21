"""Consulta para obter histórico de classificações"""
from dataclasses import dataclass
from typing import List

from app.shared.cqrs import Consulta, ManipuladorConsulta


@dataclass
class ObterHistoricoQuery(Consulta):
    """Consulta para obter histórico de um paciente"""
    paciente_id: str


class ObterHistoricoManipulador(ManipuladorConsulta):
    """Manipulador para obter histórico"""

    def __init__(self, repositorio, event_store):
        self.repositorio = repositorio
        self.event_store = event_store

    async def manipular(self, consulta: ObterHistoricoQuery) -> dict:
        """
        Obter histórico completo de classificações de um paciente

        RF05: Retornar histórico com timeline
        """
        # 1. Obter todas as classificações do paciente
        classificacoes = await self.repositorio.obter_por_paciente(consulta.paciente_id)

        if not classificacoes:
            return {
                "paciente_id": consulta.paciente_id,
                "total_classificacoes": 0,
                "historico": []
            }

        # 2. Construir histórico
        historico = []
        for classificacao in classificacoes:
            # Obter auditoria desta classificação
            auditoria = await self.event_store.obter_por_classificacao(str(classificacao.id))

            historico.append({
                "classificacao_id": str(classificacao.id),
                "cor": classificacao.cor_risco.value,
                "tempo_espera": classificacao.tempo_espera_minutos,
                "status": classificacao.status.value,
                "tipo_mudanca": classificacao.tipo_mudanca.value,
                "usuario_id": classificacao.usuario_id,
                "data_criacao": classificacao.data_criacao.isoformat(),
                "data_atualizacao": classificacao.data_atualizacao.isoformat(),
                "auditoria": auditoria,
            })

        # 3. Ordenar por data de criação
        historico.sort(key=lambda x: x["data_criacao"])

        # 4. Retornar resultado
        return {
            "paciente_id": consulta.paciente_id,
            "total_classificacoes": len(historico),
            "historico": historico
        }
