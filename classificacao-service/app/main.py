from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest
from fastapi.responses import Response

from app.api.routes import router
from app.infrastructure.database import criar_tabelas
from app.infrastructure.config import settings

docs_enabled = settings.APP_ENV != "HOMOL"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Inicializando...")
    criar_tabelas()
    print("Banco inicializado")
    yield
    # Shutdown
    print("Encerrando...")

# Prometheus
app = FastAPI(
    title="MedSync – Serviço de Classificação",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

metrics_registry = CollectorRegistry()

http_requests_total = Counter(
    "classificacao_http_requests_total",
    "Total de requisições HTTP",
    ["method", "path", "status"],
    registry=metrics_registry,
)

http_request_duration_seconds = Histogram(
    "classificacao_http_request_duration_seconds",
    "Duração das requisições HTTP",
    ["method", "path"],
    registry=metrics_registry,
)

@app.middleware("http")
async def registrar_metricas(request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    rota = request.scope.get("route")
    path = rota.path if rota else request.url.path
    http_requests_total.labels(request.method, path, str(response.status_code)).inc()
    http_request_duration_seconds.labels(request.method, path).observe(time.perf_counter() - inicio)
    return response

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

# Endpoints pras métricas
@app.get("/metrics", include_in_schema=False)
async def metrics():
    # Métricas pro promethus
    return Response(generate_latest(metrics_registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "ok", "servico": "classificacao-service"}

@app.get("/")
def root():
    return {"servico": "MedSync – Classificação", "versao": "2.0.0"}