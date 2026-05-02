from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar


T = TypeVar("T")


@dataclass
class Comando(ABC):
    pass


@dataclass
class Consulta(ABC):
    pass


@dataclass
class Evento(ABC):
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

    @abstractmethod
    def para_dict(self) -> dict:
        pass


class ManipuladorComando(ABC, Generic[T]):
    @abstractmethod
    async def manipular(self, comando: T) -> Any:
        pass


class ManipuladorConsulta(ABC, Generic[T]):
    @abstractmethod
    async def manipular(self, consulta: T) -> Any:
        pass


class BarramentoComandos:
    def __init__(self):
        self._manipuladores: dict = {}

    def registrar(self, tipo_comando, manipulador: ManipuladorComando):
        self._manipuladores[tipo_comando] = manipulador

    async def executar(self, comando: Comando) -> Any:
        tipo = type(comando)
        if tipo not in self._manipuladores:
            raise ValueError(f"Nenhum manipulador registrado para {tipo.__name__}")

        manipulador = self._manipuladores[tipo]
        return await manipulador.manipular(comando)


class BarramentoConsultas:
    def __init__(self):
        self._manipuladores: dict = {}

    def registrar(self, tipo_consulta, manipulador: ManipuladorConsulta):
        self._manipuladores[tipo_consulta] = manipulador

    async def executar(self, consulta: Consulta) -> Any:
        tipo = type(consulta)
        if tipo not in self._manipuladores:
            raise ValueError(f"Nenhum manipulador registrado para {tipo.__name__}")

        manipulador = self._manipuladores[tipo]
        return await manipulador.manipular(consulta)


class Despachador:
    def __init__(self):
        self._subscribers: dict = {}

    def subscrever(self, tipo_evento, handler):
        if tipo_evento not in self._subscribers:
            self._subscribers[tipo_evento] = []
        self._subscribers[tipo_evento].append(handler)

    async def despachar(self, evento: Evento):
        tipo = type(evento)
        if tipo not in self._subscribers:
            return

        for handler in self._subscribers[tipo]:
            await handler(evento)
