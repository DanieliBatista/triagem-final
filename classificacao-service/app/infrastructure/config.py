"""Configuração da aplicação"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./classificacao.db"
    )
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Triage
    CRITICAL_CAPACITY_LIMIT: int = int(os.getenv("CRITICAL_CAPACITY_LIMIT", "10"))
    TRIAGE_VALIDITY_HOURS: int = int(os.getenv("TRIAGE_VALIDITY_HOURS", "4"))

    # RabbitMQ
    RABBITMQ_URL: str = os.getenv(
        "RABBITMQ_URL",
        "amqp://guest:guest@localhost:5672/"
    )
    RABBITMQ_EXCHANGE: str = os.getenv("RABBITMQ_EXCHANGE", "classificacao_events")
    RABBITMQ_QUEUE: str = os.getenv("RABBITMQ_QUEUE", "queue.classificacao")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"


settings = Settings()
