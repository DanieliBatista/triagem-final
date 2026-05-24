from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Classificacao
from app.domain.enums import RiskColor
from app.domain.exceptions import PermissaoNegadaException, JustificativaObrigatoriaException
from app.domain.value_objects import obter_tempo_espera
from app.shared.cqrs import Comando, ManipuladorComando, Evento


@dataclass
class ReclassificarManualmenteCommand(Comando):
    classificacao_id: str
    nova_cor: str
    usuario_id: str
    usuario_role: str
    usuario_email: str
    justificativa: str
    ip_origem: str = ""


@dataclass
class ClassificacaoAlteradaManualmenteEvento(Evento):
    classificacao_id: str = ""
    paciente_id: str = ""
    cor_anterior: str = ""
    cor_nova: str = ""
    usuario_id: str = ""
    usuario_email: str = ""
    justificativa: str = ""

    def para_dict(self) -> dict:
        return {
            "tipo_evento": "classificacao.alterada.manual",
            "versao": "1.0",
            "timestamp": self.timestamp.isoformat(),
            "dados": {
                "classificacao_id": self.classificacao_id,
                "paciente_id": self.paciente_id,
                "cor_anterior": self.cor_anterior,
                "cor_nova": self.cor_nova,
                "usuario_id": self.usuario_id,
                "usuario_email": self.usuario_email,
                "justificativa": self.justificativa,
            }
        }


class ReclassificarManualmenteManipulador(ManipuladorComando):
    def __init__(self, repositorio, event_store, despachador):
        self.repositorio = repositorio
        self.event_store = event_store
        self.despachador = despachador

    async def manipular(self, comando: ReclassificarManualmenteCommand) -> dict:

        if comando.usuario_role != "MEDICO":
            raise PermissaoNegadaException(
                "Apenas médicos podem reclassificar pacientes"
            )

        if not comando.justificativa or len(comando.justificativa.strip()) < 5:
            raise JustificativaObrigatoriaException(
                "Justificativa obrigatória com mínimo 5 caracteres"
            )

        classificacao = await self.repositorio.obter_por_id(comando.classificacao_id)
        if not classificacao:
            raise ValueError(f"Classificação {comando.classificacao_id} não encontrada")

        auditoria = {
            "acao": "RECLASSIFICACAO_MANUAL",
            "usuario_id": comando.usuario_id,
            "usuario_email": comando.usuario_email,
            "usuario_role": comando.usuario_role,
            "timestamp": None,
            "classificacao_id": comando.classificacao_id,
            "cor_anterior": classificacao.cor_risco.value,
            "cor_nova": comando.nova_cor,
            "justificativa": comando.justificativa,
            "ip": comando.ip_origem,
        }
        await self.event_store.registrar(auditoria)

        cor_anterior = classificacao.cor_risco.value
        nova_cor_enum = RiskColor(comando.nova_cor)
        novo_tempo = obter_tempo_espera(nova_cor_enum)

        classificacao.reclassificar(
            nova_cor=nova_cor_enum,
            novo_tempo_espera=novo_tempo,
            usuario_id=comando.usuario_id,
            justificativa=comando.justificativa,
        )

        await self.repositorio.salvar(classificacao)

        evento = ClassificacaoAlteradaManualmenteEvento(
            classificacao_id=comando.classificacao_id,
            paciente_id=classificacao.paciente_id,
            cor_anterior=cor_anterior,
            cor_nova=comando.nova_cor,
            usuario_id=comando.usuario_id,
            usuario_email=comando.usuario_email,
            justificativa=comando.justificativa,
        )
        await self.despachador.despachar(evento)

        return classificacao.para_dict()
