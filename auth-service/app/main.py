from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.infrastructure.database import engine, Base, get_db, UserTable
from app.application.use_case import AuthUseCase 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serviço de Autenticação - D2")

auth_use_case = AuthUseCase()

class CadastroRequest(BaseModel):
    email: str
    senha: str
    nome: str
    idade: int

class LoginRequest(BaseModel):
    email: str
    senha: str


@app.post("/v1/auth/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar_paciente(dados: CadastroRequest, db: Session = Depends(get_db)):
    if db.query(UserTable).filter(UserTable.email == dados.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    try:
        usuario = auth_use_case.registrar_paciente(db, dados)
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