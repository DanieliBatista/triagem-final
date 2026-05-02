from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from uuid import uuid4

from app.infrastructure.config import settings
from app.domain.enums import StatusClassificacao, TipoMudanca, RiskColor

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ClassificacaoModel(Base):
    __tablename__ = "classificacoes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    paciente_id = Column(String(50), nullable=False, index=True)
    cor_risco = Column(String(20), nullable=False)
    tempo_espera_minutos = Column(Integer, nullable=False)
    status = Column(String(30), default=StatusClassificacao.ATIVO.value)
    tipo_mudanca = Column(String(20), default=TipoMudanca.AUTOMATICA.value)
    usuario_id = Column(String(100), default="sistema")

    temperatura = Column(Float, nullable=False)
    pressao_sistolica = Column(Integer, nullable=False)
    pressao_diastolica = Column(Integer, nullable=False)
    saturacao_oxigenio = Column(Float, nullable=False)
    frequencia_cardiaca = Column(Integer, nullable=False)
    dor_peito = Column(Boolean, default=False)

    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    requer_retriage = Column(Boolean, default=False)


class AuditoriaModel(Base):
    __tablename__ = "auditoria"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    classificacao_id = Column(String(36), nullable=False, index=True)
    acao = Column(String(50), nullable=False)
    usuario_id = Column(String(100))
    usuario_email = Column(String(100))
    usuario_role = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    cor_anterior = Column(String(20))
    cor_nova = Column(String(20))
    justificativa = Column(String(500))
    ip = Column(String(50))


def criar_tabelas():
    Base.metadata.create_all(bind=engine)


def obter_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
