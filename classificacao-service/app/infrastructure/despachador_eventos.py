"""Despachador de eventos para RabbitMQ"""
import json
import asyncio
from abc import ABC, abstractmethod

from app.shared.cqrs import Evento


class DespachadorEventos(ABC):
    """Interface para despachador de eventos"""

    @abstractmethod
    async def despachar(self, evento: Evento) -> None:
        """Despachar evento"""
        pass


class DespachadorEventosMock(DespachadorEventos):
    """Mock para desenvolvimento local (sem RabbitMQ)"""

    def __init__(self):
        self.eventos = []

    async def despachar(self, evento: Evento) -> None:
        """Despachar evento para log (desenvolvimento)"""
        dados = evento.para_dict()
        self.eventos.append(dados)
        print(f"[EVENTO DESPACHADO] {json.dumps(dados, indent=2, default=str)}")


class DespachadorEventosRabbitMQ(DespachadorEventos):
    """Despachador real usando RabbitMQ"""

    def __init__(self, url_rabbitmq: str, exchange: str):
        self.url_rabbitmq = url_rabbitmq
        self.exchange = exchange
        self._conexao = None
        self._canal = None

    async def conectar(self):
        """Conectar ao RabbitMQ"""
        try:
            import aio_pika
            self._conexao = await aio_pika.connect_robust(self.url_rabbitmq)
            self._canal = await self._conexao.channel()
            await self._canal.declare_exchange(
                self.exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
        except ImportError:
            print("aio-pika não instalado, usando mock")
            self._mock = DespachadorEventosMock()

    async def despachar(self, evento: Evento) -> None:
        """Despachar evento para RabbitMQ"""
        if not self._canal:
            if hasattr(self, "_mock"):
                await self._mock.despachar(evento)
            return

        try:
            import aio_pika

            dados = evento.para_dict()
            mensagem = aio_pika.Message(
                body=json.dumps(dados, default=str).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            routing_key = dados.get("tipo_evento", "evento.generico")
            await self._canal.default_exchange.publish(
                mensagem,
                routing_key=routing_key
            )

            print(f"[EVENTO PUBLICADO NO RABBITMQ] {routing_key}")

        except Exception as e:
            print(f"Erro ao publicar evento: {e}")

    async def desconectar(self):
        """Desconectar do RabbitMQ"""
        if self._conexao:
            await self._conexao.close()
