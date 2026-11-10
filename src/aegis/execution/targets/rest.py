import httpx
import uuid
import json
from typing import Dict, Any, Optional
from src.aegis.domain.interfaces.execution import TargetAdapter, TargetHealth
from src.aegis.domain.schemas.scope import TargetConfiguration

PROMPT_PLACEHOLDER = "{{PROMPT}}"
SESSION_PLACEHOLDER = "{{SESSION}}"

class SimpleTargetHealth:
    def __init__(self, is_healthy: bool, details: str):
        self.is_healthy = is_healthy
        self.details = details

def _fill(value: Any, prompt: str, session_id: str) -> Any:
    if isinstance(value, dict):
        return {k: _fill(v, prompt, session_id) for k, v in value.items()}
    if isinstance(value, list):
        return [_fill(v, prompt, session_id) for v in value]
    if isinstance(value, str):
        # Handle both uppercase and lowercase placeholder conventions
        res = value.replace("{{PROMPT}}", prompt).replace("{{prompt}}", prompt)
        res = res.replace("{{SESSION}}", session_id).replace("{{session_id}}", session_id)
        return res
    return value

def _extract(data: Any, dotted_path: str) -> Any:
    if not dotted_path:
        return data
    for key in dotted_path.split("."):
        if isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        elif isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data

class RestTargetAdapter(TargetAdapter):
    def __init__(self, config: TargetConfiguration, credentials: Optional[Dict[str, str]] = None):
        self.config = config
        headers, auth = self._auth(config, credentials or {})
        self.url = config.base_url.rstrip("/") + config.endpoint_path if config.endpoint_path else config.base_url
        self.client = httpx.AsyncClient(
            headers=headers,
            auth=auth,
            timeout=config.timeout_seconds,
        )

    @staticmethod
    def _auth(config: TargetConfiguration, credentials: Dict[str, str]):
        headers = dict(config.headers)
        username = credentials.get("username") or ""
        secret = credentials.get("password") or ""
        
        if not username and not secret:
            return headers, None
            
        auth_type = config.authentication_type
        if auth_type == "bearer":
            headers["Authorization"] = f"Bearer {secret}"
            return headers, None
        if auth_type in ("api_key", "custom_header"):
            headers[config.auth_header or "X-API-Key"] = secret
            return headers, None
        if auth_type == "basic":
            return headers, (username, secret)
            
        return headers, None

    async def health_check(self) -> TargetHealth:
        try:
            response = await self.client.get(self.url)
            return SimpleTargetHealth(is_healthy=True, details=f"Status: {response.status_code}")
        except Exception as e:
            return SimpleTargetHealth(is_healthy=False, details=str(e))

    async def send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.config.http_method.upper() == "POST":
            response = await self.client.post(self.url, json=payload)
        else:
            response = await self.client.get(self.url, params=payload)

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "json": response.json() if "application/json" in response.headers.get("content-type", "") else None,
        }

    async def send_prompt(self, prompt: str) -> str:
        # Check if template is provided, else fallback to a default chat structure
        template = self.config.request_template
        if not template:
            template = {"messages": [{"role": "user", "content": PROMPT_PLACEHOLDER}]}
            
        payload = _fill(template, prompt, uuid.uuid4().hex)
        try:
            response = await self.send_request(payload)
        except Exception as e:
            return f"Endpoint Connection Error: {str(e)}"
        
        status = response["status_code"]
        if status in (401, 403) or status >= 500:
            return f"Endpoint Connection or Auth Error: HTTP {status} - {response['body'][:200]}"
            
        output_path = self.config.response_mapping.get("output")
        if output_path and response["json"] is not None:
            answer = _extract(response["json"], output_path)
            if answer is not None:
                return answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
                
        return response["body"]

    async def close(self) -> None:
        await self.client.aclose()
