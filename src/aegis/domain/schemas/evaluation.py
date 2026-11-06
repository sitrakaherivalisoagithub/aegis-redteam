from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from datetime import datetime
import uuid

class Recommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    effort: Literal["low", "medium", "high"]

class RiskAssessment(BaseModel):
    severity: Literal["critical", "high", "medium", "low", "informational"]
    confidence: float
    exploitability: Literal["easy", "moderate", "difficult", "unlikely"]
    business_impact: str
    justification: str

class Finding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str

    title: str
    description: str

    standard: str
    standard_version: str
    standard_reference: str

    affected_component: str

    severity: Literal["critical", "high", "medium", "low", "informational"]
    confidence: float

    status: Literal["suspected", "confirmed", "not_reproduced", "false_positive", "accepted_risk"]

    impact: str
    evidence_ids: List[str]

    root_cause: Optional[str] = None
    recommendations: List[str] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
