from typing import Any

import httpx

from pseudo_apis.config import settings
from pseudo_apis.models import Severity


class IncidentTriageClient:
    def __init__(self, base_url: str = settings.incident_triage_url) -> None:
        self.base_url = base_url.rstrip("/")

    async def analyze(
        self,
        *,
        question: str,
        service: str,
        severity: Severity,
    ) -> dict[str, Any]:
        payload = {
            "question": question,
            "service": service,
            "severity": severity.value,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{self.base_url}/incidents/analyze", json=payload)
            response.raise_for_status()
            return response.json()

