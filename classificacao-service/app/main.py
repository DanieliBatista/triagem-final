from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="MedSync – Triage Service",
    description="Microsserviço de Triagem e Classificação (Protocolo de Manchester)",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}