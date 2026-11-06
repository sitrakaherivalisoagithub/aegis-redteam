from pydantic import BaseModel
from typing import List, Dict, Optional

class ApplicationComponent(BaseModel):
    name: str
    component_type: str
    description: str
    source_references: List[str] = []
    confidence: float = 1.0

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
    authentication_mechanisms: List[str] = []
    sensitive_data_categories: List[str] = []
