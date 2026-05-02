from dataclasses import dataclass

from app.shared.cqrs import Consulta, ManipuladorConsulta


@dataclass
class ObterClassificacaoQuery(Consulta):
    classificacao_id: str


class ObterClassificacaoManipulador(ManipuladorConsulta):

    def __init__(self, repositorio):
        self.repositorio = repositorio

    async def manipular(self, consulta: ObterClassificacaoQuery) -> dict:
        classificacao = await self.repositorio.obter_por_id(consulta.classificacao_id)

        if not classificacao:
            raise ValueError(f"Classificação {consulta.classificacao_id} não encontrada")

        classificacao.verificar_expiracao()

        return classificacao.para_dict()
