from sqlalchemy.orm import Session
from app.infrastructure.database import UserTable, PatientTable
from app.domain.security import verificar_senha, criar_token_jwt, gerar_hash_senha

class AuthUseCase:
    def login(self, db: Session, email: str, senha: str):
        usuario = db.query(UserTable).filter(UserTable.email == email).first()
        
        if not usuario or not verificar_senha(senha, usuario.senha_hash):
            return None
        
        token = criar_token_jwt({"sub": usuario.email, "role": usuario.role})
        return {"access_token": token, "token_type": "bearer"}
    
    def registrar_usuario(self, db: Session, dados): 
        hash_senha = gerar_hash_senha(dados.senha)
        
        novo_usuario = UserTable(
            email=dados.email, 
            senha_hash=hash_senha, 
            role=dados.role,   
            crm=dados.crm
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        if dados.role == "PACIENTE":
            novo_paciente = PatientTable(
                user_id=novo_usuario.id, 
                nome=dados.nome, 
                idade=dados.idade
            )
            db.add(novo_paciente)
            db.commit()
        
        return novo_usuario