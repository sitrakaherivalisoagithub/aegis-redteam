from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

class ApplicationComponent(BaseModel):
    name: str
    component_type: str
    description: str
    source_references: List[str] = []
    confidence: float = 1.0

class ApiEndpoint(BaseModel):
    """HTTP endpoint of the application that forwards user input to an LLM."""
    path: str = Field(description="Route path as declared in the code, e.g. /api/v1/chat")
    http_method: str = "POST"
    request_template: str = Field(
        default="",
        description=(
            'JSON request body as a string. Put "{{prompt}}" where the user message goes and '
            '"{{session_id}}" for any conversation/thread id, e.g. '
            '{"message": "{{prompt}}", "thread_id": "{{session_id}}"}'
        ),
    )
    response_field: Optional[str] = Field(
        default=None,
        description="Dotted path of the LLM answer in the JSON response, e.g. choices.0.message.content",
    )
    authentication_type: Literal["none", "bearer", "api_key", "basic", "custom_header"] = "none"
    auth_header: Optional[str] = Field(
        default=None,
        description="Header name carrying the credential for api_key/custom_header. Never a secret value.",
    )
    source_references: List[str] = []


class ApplicationInventory(BaseModel):
    assessment_id: str
    languages: List[str] = []
    frameworks: List[str] = []
    dependencies: List[Dict[str, str]] = []
    ai_components: List[ApplicationComponent] = []
    llm_providers: List[str] = []
    prompt_locations: List[str] = []
    rag_components: List[ApplicationComponent] = []
    vector_databases: List[str] = []
    agent_components: List[ApplicationComponent] = []
    mcp_servers: List[ApplicationComponent] = []
    api_integrations: List[str] = []
    api_endpoints: List[ApiEndpoint] = []
    authentication_mechanisms: List[str] = []
    sensitive_data_categories: List[str] = []
