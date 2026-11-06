from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict

class RepositoryConfiguration(BaseModel):
    source: Literal["local", "github"] = "local"
    path: Optional[str] = Field(None, description="Local path for the repository")
    url: Optional[str] = Field(None, description="GitHub URL")
    branch: str = "main"

class TargetConfiguration(BaseModel):
    target_id: str
    name: str
    target_type: Literal[
        "rest_api",
        "openai_compatible",
        "custom_llm",
        "rag_application",
        "agent_application"
    ]
    base_url: str
    endpoint_path: str
    http_method: str = "POST"
    authentication_type: Literal["none", "bearer", "api_key", "basic", "custom_header"] = "none"
    credential_reference: Optional[str] = None
    headers: Dict[str, str] = {}
    request_template: Dict = {}
    response_mapping: Dict = {}
    timeout_seconds: int = 30
    environment: Literal["development", "staging", "production"] = "staging"

class AssessmentScope(BaseModel):
    target_type: Literal["repository", "live_application", "hybrid"]
    repository: Optional[RepositoryConfiguration] = None
    target_app: Optional[TargetConfiguration] = None
    exclusions: list[str] = []
