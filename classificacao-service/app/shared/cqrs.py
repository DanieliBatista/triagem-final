"""Classes base para padrão CQRS"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar


T = TypeVar("T")


@dataclass
class Comando(ABC):
    """Classe base para todos os comandos"""
    pass


@dataclass
class Consulta(ABC):
    """Classe base para todas as consultas"""
    pass


@dataclass
class Evento(ABC):
    """Classe base para todos os eventos"""
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

    @abstractmethod
    def para_dict(self) -> dict:
        """Converter evento para dicionário"""
        pass


class ManipuladorComando(ABC, Generic[T]):
    """Classe base para manipuladores de comando"""

    @abstractmethod
    async def manipular(self, comando: T) -> Any:
        """Executar o comando e retornar resultado"""
        pass


class ManipuladorConsulta(ABC, Generic[T]):
    """Classe base para manipuladores de consulta"""

    @abstractmethod
    async def manipular(self, consulta: T) -> Any:
        """Executar a consulta e retornar resultado"""
        pass


class BarramentoComandos:
    """Bus para executar comandos"""

    def __init__(self):
        self._manipuladores: dict = {}

    def registrar(self, tipo_comando, manipulador: ManipuladorComando):
        """Registrar manipulador para tipo de comando"""
        self._manipuladores[tipo_comando] = manipulador

    async def executar(self, comando: Comando) -> Any:
        """Executar comando"""
        tipo = type(comando)
        if tipo not in self._manipuladores:
            raise ValueError(f"Nenhum manipulador registrado para {tipo.__name__}")

        manipulador = self._manipuladores[tipo]
        return await manipulador.manipular(comando)


class BarramentoConsultas:
    """Bus para executar consultas"""

    def __init__(self):
        self._manipuladores: dict = {}

    def registrar(self, tipo_consulta, manipulador: ManipuladorConsulta):
        """Registrar manipulador para tipo de consulta"""
        self._manipuladores[tipo_consulta] = manipulador

    async def executar(self, consulta: Consulta) -> Any:
        """Executar consulta"""
        tipo = type(consulta)
        if tipo not in self._manipuladores:
            raise ValueError(f"Nenhum manipulador registrado para {tipo.__name__}")

        manipulador = self._manipuladores[tipo]
        return await manipulador.manipular(consulta)


class Despachador:
    """Despachador de eventos"""

    def __init__(self):
        self._subscribers: dict = {}

    def subscrever(self, tipo_evento, handler):
        """Subscrever a um tipo de evento"""
        if tipo_evento not in self._subscribers:
            self._subscribers[tipo_evento] = []
        self._subscribers[tipo_evento].append(handler)

    async def despachar(self, evento: Evento):
        """Despachar evento para todos os subscribers"""
        tipo = type(evento)
        if tipo not in self._subscribers:
            return

        for handler in self._subscribers[tipo]:
            await handler(evento)
