"""Comando para criar nova classificação"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities import Classificacao
from app.domain.enums import TipoMudanca, RiskColor
from app.domain.value_objects import SinaisVitais, classificar_paciente, obter_tempo_espera
from app.shared.cqrs import Comando, ManipuladorComando, Evento


@dataclass
class CriarClassificacaoCommand(Comando):
    """Comando para criar uma nova classificação"""
    paciente_id: str
    temperatura: float
    pressao_sistolica: int
    pressao_diastolica: int
    saturacao_oxigenio: float
    frequencia_cardiaca: int
    dor_peito: bool = False
    usuario_id: str = "sistema"


@dataclass
class ClassificacaoCriadaEvento(Evento):
    """Evento: Classificação foi criada"""
    classificacao_id: str = ""
    paciente_id: str = ""
    cor_risco: str = ""
    tempo_espera_minutos: int = 0
    usuario_id: str = ""

    def para_dict(self) -> dict:
        return {
            "tipo_evento": "classificacao.criada",
            "versao": "1.0",
            "timestamp": self.timestamp.isoformat(),
            "dados": {
                "classificacao_id": self.classificacao_id,
                "paciente_id": self.paciente_id,
                "cor_risco": self.cor_risco,
                "tempo_espera_minutos": self.tempo_espera_minutos,
                "usuario_id": self.usuario_id,
            }
        }


class CriarClassificacaoManipulador(ManipuladorComando):
    """Manipulador para criar classificação"""

    def __init__(self, repositorio, despachador):
        self.repositorio = repositorio
        self.despachador = despachador

    async def manipular(self, comando: CriarClassificacaoCommand) -> dict:
        """
        Criar nova classificação baseado em sinais vitais

        RF05: Criar e armazenar classificação
        RN02: Aplicar Protocolo de Manchester
        """
        # 1. Criar sinais vitais (valida automaticamente)
        sinais = SinaisVitais(
            temperatura=comando.temperatura,
            pressao_sistolica=comando.pressao_sistolica,
            pressao_diastolica=comando.pressao_diastolica,
            saturacao_oxigenio=comando.saturacao_oxigenio,
            frequencia_cardiaca=comando.frequencia_cardiaca,
            dor_peito=comando.dor_peito,
        )

        # 2. Classificar paciente
        cor_risco = classificar_paciente(sinais)
        tempo_espera = obter_tempo_espera(cor_risco)

        # 3. Criar entidade
        classificacao = Classificacao(
            paciente_id=comando.paciente_id,
            sinais_vitais=sinais,
            cor_risco=cor_risco,
            tempo_espera_minutos=tempo_espera,
            usuario_id=comando.usuario_id,
            tipo_mudanca=TipoMudanca.AUTOMATICA,
        )

        # 4. Salvar no repositório
        await self.repositorio.salvar(classificacao)

        # 5. Publicar evento
        evento = ClassificacaoCriadaEvento(
            classificacao_id=str(classificacao.id),
            paciente_id=classificacao.paciente_id,
            cor_risco=classificacao.cor_risco.value,
            tempo_espera_minutos=classificacao.tempo_espera_minutos,
            usuario_id=classificacao.usuario_id,
        )
        await self.despachador.despachar(evento)

        # 6. Retornar resultado
        return classificacao.para_dict()
