"""Setup de banco de dados com SQLAlchemy"""
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from uuid import uuid4

from app.infrastructure.config import settings


# Setup Engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Setup Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


# ORM Models
class TriagemModel(Base):
    """Model ORM para Triagem"""
    __tablename__ = "triagens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    paciente_id = Column(String(50), nullable=False, index=True)

    # Sinais vitais coletados
    temperatura = Column(Float, nullable=False)
    pressao_sistolica = Column(Integer, nullable=False)
    pressao_diastolica = Column(Integer, nullable=False)
    saturacao_oxigenio = Column(Float, nullable=False)
    frequencia_cardiaca = Column(Integer, nullable=False)
    dor_peito = Column(Boolean, default=False)

    # Classificação obtida (referência para auditoria)
    classificacao_id = Column(String(36), nullable=True, index=True)

    # Metadata
    usuario_id = Column(String(100), nullable=False)
    ip_origem = Column(String(50), nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)


def criar_tabelas():
    """Criar todas as tabelas"""
    Base.metadata.create_all(bind=engine)


def obter_sessao():
    """Dependency para obter sessão"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
