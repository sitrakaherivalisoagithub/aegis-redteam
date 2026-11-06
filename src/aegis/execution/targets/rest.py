import httpx
from typing import Dict, Any
from src.aegis.domain.interfaces.execution import TargetAdapter, TargetHealth
from src.aegis.domain.schemas.scope import TargetConfiguration

class SimpleTargetHealth:
    def __init__(self, is_healthy: bool, details: str):
        self.is_healthy = is_healthy
        self.details = details

class RestTargetAdapter(TargetAdapter):
    def __init__(self, config: TargetConfiguration):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers=config.headers,
            timeout=config.timeout_seconds
        )

    async def health_check(self) -> TargetHealth:
        try:
            # Basic health check: try to hit the base URL
            response = await self.client.get("/")
            return SimpleTargetHealth(is_healthy=True, details=f"Status: {response.status_code}")
        except Exception as e:
            return SimpleTargetHealth(is_healthy=False, details=str(e))

    async def send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.endpoint_path
        if self.config.http_method.upper() == "POST":
            response = await self.client.post(url, json=payload)
        else:
            response = await self.client.get(url, params=payload)
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "json": response.json() if "application/json" in response.headers.get("content-type", "") else None
        }

    async def close(self) -> None:
        await self.client.aclose()
