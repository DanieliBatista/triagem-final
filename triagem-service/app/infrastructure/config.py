"""Configuração da aplicação de Triagem"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação de Triagem"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./triagem.db"
    )
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Classificação Service
    CLASSIFICACAO_SERVICE_URL: str = os.getenv(
        "CLASSIFICACAO_SERVICE_URL",
        "http://d5_classificacao:8000"
    )

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"


settings = Settings()
