"""Comando para gerar relatório de classificação"""
from dataclasses import dataclass
from uuid import uuid4

from app.shared.cqrs import Comando, ManipuladorComando, Evento


@dataclass
class GerarRelatorioCommand(Comando):
    """Comando para gerar relatório de classificação"""
    classificacao_id: str
    usuario_id: str
    usuario_email: str


@dataclass
class RelatorioGeradoEvento(Evento):
    """Evento: Relatório foi gerado"""
    relatorio_id: str = ""
    classificacao_id: str = ""
    paciente_id: str = ""
    usuario_id: str = ""

    def para_dict(self) -> dict:
        return {
            "tipo_evento": "relatorio.gerado",
            "versao": "1.0",
            "timestamp": self.timestamp.isoformat(),
            "dados": {
                "relatorio_id": self.relatorio_id,
                "classificacao_id": self.classificacao_id,
                "paciente_id": self.paciente_id,
                "usuario_id": self.usuario_id,
            }
        }


class GerarRelatorioManipulador(ManipuladorComando):
    """Manipulador para gerar relatório"""

    def __init__(self, repositorio, event_store, despachador):
        self.repositorio = repositorio
        self.event_store = event_store
        self.despachador = despachador

    async def manipular(self, comando: GerarRelatorioCommand) -> dict:
        """
        Gerar relatório de classificação

        RF07: Gerar relatório com histórico completo
        """
        # 1. Obter classificação atual
        classificacao = await self.repositorio.obter_por_id(comando.classificacao_id)
        if not classificacao:
            raise ValueError(f"Classificação {comando.classificacao_id} não encontrada")

        # 2. Obter auditoria (histórico de mudanças)
        auditoria = await self.event_store.obter_por_classificacao(comando.classificacao_id)

        # 3. Montar histórico formatado
        historico = []
        for registro in auditoria:
            historico.append({
                "acao": registro.get("acao", "DESCONHECIDA"),
                "usuario_email": registro.get("usuario_email", "SISTEMA"),
                "timestamp": registro.get("timestamp", "").isoformat() if isinstance(registro.get("timestamp"), str) else registro.get("timestamp"),
                "cor": registro.get("cor_nova", "N/A"),
                "justificativa": registro.get("justificativa", ""),
            })

        # 4. Criar relatório
        relatorio_id = str(uuid4())
        relatorio = {
            "relatorio_id": relatorio_id,
            "paciente_id": classificacao.paciente_id,
            "classificacao_id": comando.classificacao_id,
            "gerado_em": None,  # Será preenchido pelo handler
            "gerado_por": comando.usuario_email,
            "classificacao_atual": {
                "cor": classificacao.cor_risco.value,
                "tempo_espera": classificacao.tempo_espera_minutos,
                "data": classificacao.data_atualizacao.isoformat(),
            },
            "historico": historico,
            "sinais_vitais": classificacao.sinais_vitais.para_dict(),
            "status": classificacao.status.value,
        }

        # 5. Publicar evento
        evento = RelatorioGeradoEvento(
            relatorio_id=relatorio_id,
            classificacao_id=comando.classificacao_id,
            paciente_id=classificacao.paciente_id,
            usuario_id=comando.usuario_id,
        )
        await self.despachador.despachar(evento)

        # 6. Retornar relatório
        return relatorio
