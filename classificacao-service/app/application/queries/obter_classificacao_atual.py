"""Consulta para obter classificação atual"""
from dataclasses import dataclass

from app.shared.cqrs import Consulta, ManipuladorConsulta


@dataclass
class ObterClassificacaoQuery(Consulta):
    """Consulta para obter uma classificação específica"""
    classificacao_id: str


class ObterClassificacaoManipulador(ManipuladorConsulta):
    """Manipulador para obter classificação"""

    def __init__(self, repositorio):
        self.repositorio = repositorio

    async def manipular(self, consulta: ObterClassificacaoQuery) -> dict:
        """Obter classificação por ID"""
        classificacao = await self.repositorio.obter_por_id(consulta.classificacao_id)

        if not classificacao:
            raise ValueError(f"Classificação {consulta.classificacao_id} não encontrada")

        # Verificar expiração
        classificacao.verificar_expiracao()

        return classificacao.para_dict()
