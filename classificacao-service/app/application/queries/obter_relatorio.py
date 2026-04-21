"""Consulta para obter relatório de classificação"""
from dataclasses import dataclass

from app.shared.cqrs import Consulta, ManipuladorConsulta


@dataclass
class ObterRelatorioQuery(Consulta):
    """Consulta para obter relatório de uma classificação"""
    classificacao_id: str
    paciente_id: str


class ObterRelatorioManipulador(ManipuladorConsulta):
    """Manipulador para obter relatório"""

    def __init__(self, repositorio, event_store):
        self.repositorio = repositorio
        self.event_store = event_store

    async def manipular(self, consulta: ObterRelatorioQuery) -> dict:
        """
        Obter relatório completo de uma classificação

        RF07: Retornar relatório com histórico + auditoria
        """
        # 1. Obter classificação
        classificacao = await self.repositorio.obter_por_id(consulta.classificacao_id)
        if not classificacao:
            raise ValueError(f"Classificação {consulta.classificacao_id} não encontrada")

        # 2. Validar paciente
        if classificacao.paciente_id != consulta.paciente_id:
            raise ValueError("Classificação não pertence a este paciente")

        # 3. Obter auditoria completa
        auditoria = await self.event_store.obter_por_classificacao(consulta.classificacao_id)

        # 4. Verificar expiração
        classificacao.verificar_expiracao()

        # 5. Montar relatório
        relatorio = {
            "paciente_id": classificacao.paciente_id,
            "classificacao_id": consulta.classificacao_id,
            "classificacao_atual": {
                "cor": classificacao.cor_risco.value,
                "tempo_espera": classificacao.tempo_espera_minutos,
                "status": classificacao.status.value,
                "requer_retriage": classificacao.requer_retriage,
            },
            "sinais_vitais": classificacao.sinais_vitais.para_dict(),
            "timeline": {
                "data_criacao": classificacao.data_criacao.isoformat(),
                "data_atualizacao": classificacao.data_atualizacao.isoformat(),
            },
            "auditoria": auditoria,
            "historico_auditoria": [
                {
                    "acao": reg.get("acao", "DESCONHECIDA"),
                    "usuario": reg.get("usuario_email", "SISTEMA"),
                    "timestamp": reg.get("timestamp", "").isoformat() if isinstance(reg.get("timestamp"), str) else str(reg.get("timestamp")),
                    "cor_anterior": reg.get("cor_anterior", "N/A"),
                    "cor_nova": reg.get("cor_nova", "N/A"),
                    "justificativa": reg.get("justificativa", ""),
                }
                for reg in auditoria
            ]
        }

        return relatorio
