import asyncio
from datetime import datetime

from app.infrastructure.repositories import RepositorioClassificacao
from app.infrastructure.despachador_eventos import DespachadorEventos
from app.application.events.classificacao_escalada import ClassificacaoEscaladaEvento


class AgendadorEscalacao:
    def __init__(self, repositorio: RepositorioClassificacao, despachador: DespachadorEventos):
        self.repositorio = repositorio
        self.despachador = despachador
        self._rodando = False

    async def iniciar(self):
        self._rodando = True
        await self._loop_escalacao()

    async def parar(self):
        self._rodando = False

    async def _loop_escalacao(self):
        while self._rodando:
            try:
                await self._verificar_escalacoes()
                await asyncio.sleep(300)  # 5 minutos
            except Exception as e:
                print(f"Erro no agendador de escalação: {e}")
                await asyncio.sleep(60)  # Tentar novamente em 1 minuto

    async def _verificar_escalacoes(self):
        print("[AGENDADOR] Verificando escalações automáticas...")
        pass

    async def escalar_se_necessario(self, classificacao_id: str):
        classificacao = await self.repositorio.obter_por_id(classificacao_id)

        if not classificacao:
            return False

        cor_anterior = classificacao.cor_risco.value
        if classificacao.escalar():
            await self.repositorio.salvar(classificacao)

            evento = ClassificacaoEscaladaEvento(
                classificacao_id=str(classificacao.id),
                paciente_id=classificacao.paciente_id,
                cor_anterior=cor_anterior,
                cor_nova=classificacao.cor_risco.value,
            )
            await self.despachador.despachar(evento)

            print(f"[ESCALAÇÃO] {classificacao_id}: {cor_anterior} → {classificacao.cor_risco.value}")
            return True

        return False
