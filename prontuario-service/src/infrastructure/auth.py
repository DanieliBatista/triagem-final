import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuração do esquema de segurança (Bearer Token)
reusable_oauth2 = HTTPBearer()

# EM PRODUÇÃO: Essa chave deve ser igual à do Serviço de Autenticação e vir do .env
SECRET_KEY = "chave_secreta_do_grupo"
ALGORITHM = "HS256"

def get_current_user_role(res: HTTPAuthorizationCredentials = Security(reusable_oauth2)) -> str:
    """
    RN02: Controle de acesso.
    Esta função extrai o token, valida a assinatura e retorna a 'role' (MEDICO, ENFERMEIRO, etc).
    """
    token = res.credentials
    try:
        # Decodifica o token usando a chave secreta do grupo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_role = payload.get("role")
        
        if user_role is None:
            raise HTTPException(
                status_code=401, 
                detail="Token inválido: Role não encontrada."
            )
            
        return user_role

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro na autenticação: {str(e)}")