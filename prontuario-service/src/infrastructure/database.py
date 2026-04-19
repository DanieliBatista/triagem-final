from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/auth_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProntuarioTable(Base):
    __tablename__ = "prontuarios"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(String, index=True)
    medico_id = Column(String)
    anamnese = Column(String)
    prescricoes = Column(JSON) 
    status = Column(String, default="EM_ANDAMENTO")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()