import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.requests import Request

from app.api.routes import router
from app.infrastructure.database import criar_tabelas
from app.infrastructure.config import settings


docs_enabled = settings.APP_ENV != "HOMOL"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando classificacao-service...")
    criar_tabelas()
    print("✓ Banco de dados inicializado")
    yield
    print("Encerrando classificacao-service...")


app = FastAPI(
    title="MedSync – Serviço de Classificação",
    description="Microsserviço CQRS para gestão de classificações (Protocolo de Manchester)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics_registry = CollectorRegistry()

http_requests_total = Counter(
    "classificacao_http_requests_total",
    "Total de requisições HTTP do classificacao-service.",
    ["method", "path", "status"],
    registry=metrics_registry,
)

http_request_duration_seconds = Histogram(
    "classificacao_http_request_duration_seconds",
    "Duração das requisições HTTP do classificacao-service.",
    ["method", "path"],
    registry=metrics_registry,
)


@app.middleware("http")
async def registrar_metricas(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    rota = request.scope.get("route")
    path = rota.path if rota else request.url.path
    http_requests_total.labels(request.method, path, str(response.status_code)).inc()
    http_request_duration_seconds.labels(request.method, path).observe(
        time.perf_counter() - inicio
    )
    return response


app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "servico": "classificacao-service",
        "versao": "1.0.0",
    }


@app.get("/", tags=["Root"])
def root():
    endpoints = {
        "health": "/health",
        "classificacoes": "/v1/classificacoes",
        "metrics": "/metrics",
    }
    if docs_enabled:
        endpoints.update({"api_docs": "/docs", "redoc": "/redoc"})
    return {
        "servico": "MedSync – Classificação",
        "versao": "1.0.0",
        "endpoints": endpoints,
    }


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(metrics_registry), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=8001,
        log_level=settings.LOG_LEVEL.lower(),
    )