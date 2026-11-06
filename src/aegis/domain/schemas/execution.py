from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any
from datetime import datetime
import uuid

class Evidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    raw_request: str
    raw_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TestExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    status: Literal["passed", "failed", "inconclusive", "error"]
    message: str
    evidence: List[Evidence] = []
    engine_used: str
    execution_time_ms: float
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime = Field(default_factory=datetime.utcnow)
