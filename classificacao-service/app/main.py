"""Aplicação FastAPI - classificacao-service"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.infrastructure.database import criar_tabelas
from app.infrastructure.config import settings


# Lifespan para inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Inicializando classificacao-service...")
    criar_tabelas()
    print("✓ Banco de dados inicializado")

    yield

    # Shutdown
    print("Encerrando classificacao-service...")


# Criar app
app = FastAPI(
    title="MedSync – Serviço de Classificação",
    description="Microsserviço CQRS para gestão de classificações (Protocolo de Manchester)",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)


# Health check
@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "servico": "classificacao-service",
        "versao": "2.0.0",
    }


# Root endpoint
@app.get("/")
def root():
    """Root endpoint com informações do serviço"""
    return {
        "servico": "MedSync – Classificação",
        "versao": "2.0.0",
        "descricao": "Serviço de gestão de classificações com padrão CQRS",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "redoc": "/redoc",
            "classificacoes": "/v1/classificacoes",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level=settings.LOG_LEVEL.lower(),
    )
