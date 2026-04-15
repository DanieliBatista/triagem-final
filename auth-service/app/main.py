from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.infrastructure.database import engine, Base, get_db, UserTable, PatientTable
from app.domain.security import gerar_hash_senha, criar_token_jwt, verificar_senha

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Serviço de Autenticação - D2")

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
    
    novo_usuario = UserTable(
        email=dados.email, 
        senha_hash=gerar_hash_senha(dados.senha),
        role="PACIENTE" 
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    novo_paciente = PatientTable(
        user_id=novo_usuario.id,
        nome=dados.nome,
        idade=dados.idade,
    )
    db.add(novo_paciente)
    db.commit()
    
    return {"status": "Sucesso", "usuario_id": novo_usuario.id}

@app.post("/v1/auth/login")
def login(email: str, senha: str, db: Session = Depends(get_db)):
    usuario = db.query(UserTable).filter(UserTable.email == email).first()
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = criar_token_jwt({"sub": usuario.email, "role": usuario.role})
    return {"access_token": token, "token_type": "bearer"}