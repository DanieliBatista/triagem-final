import logging
import os
import httpx
from app.domain.entities import Triage

logger = logging.getLogger(__name__)

EVENT_BUS_URL = os.getenv("EVENT_BUS_URL", "http://event-bus-service:8001/events")


async def publish_triage_completed(triage: Triage) -> None:
    payload = {
        "event": "triage.completed",
        "triage_id": str(triage.id),
        "patient_id": triage.patient_id,
        "risk_color": triage.risk_color.value,
        "estimated_wait_minutes": triage.estimated_wait_minutes,
        "vital_signs": {
            "temperature": triage.vital_signs.temperature,
            "systolic_bp": triage.vital_signs.systolic_bp,
            "diastolic_bp": triage.vital_signs.diastolic_bp,
            "oxygen_saturation": triage.vital_signs.oxygen_saturation,
            "heart_rate": triage.vital_signs.heart_rate,
            "chest_pain": triage.vital_signs.chest_pain,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(EVENT_BUS_URL, json=payload)
            response.raise_for_status()
            logger.info("Evento triage.completed publicado: %s", triage.id)
    except Exception as exc:
        logger.error("Falha ao publicar evento de triagem %s: %s", triage.id, exc)