from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from app.infrastructure.database import engine, Base, get_db, UserTable
from app.application.use_case import AuthUseCase 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serviço de Autenticação - D2")

auth_use_case = AuthUseCase()

class CadastroRequest(BaseModel):
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$', description="E-mail válido")
    senha: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")
    nome: str = Field(..., max_length=100, description="Nome completo")
    idade: int = Field(..., ge=0, description="Idade válida")
    role: str = Field(default="PACIENTE")
    crm: Optional[str] = None

@model_validator(mode='after')
def verificar_crm_medico(self):
    if self.role == "MEDICO" and not self.crm:
        raise ValueError("Médicos precisam obrigatoriamente fornecer o CRM.")
    return self

class Config:
        json_schema_extra = {
            "example": {
                "email": "medico@hospital.com",
                "senha": "senha_segura123",
                "nome": "Dr. Roberto",
                "idade": 45,
                "role": "MEDICO",
                "crm": "12345-SP"
            }
        }

class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$', description="E-mail válido")
    senha: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")


@app.post("/v1/auth/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar_novo_usuario(dados: CadastroRequest, db: Session = Depends(get_db)):
    if db.query(UserTable).filter(UserTable.email == dados.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    try:
        usuario = auth_use_case.registrar_usuario(db, dados)
        return {"status": "Sucesso", "usuario_id": usuario.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar cadastro: {str(e)}")

@app.post("/v1/auth/login")
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    resultado = auth_use_case.login(db, dados.email, dados.senha)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
    
    return resultado