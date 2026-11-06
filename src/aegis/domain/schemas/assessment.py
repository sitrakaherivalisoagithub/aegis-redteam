from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from src.aegis.domain.enums.assessment import AssessmentState

class AssessmentBase(BaseModel):
    name: str = Field(..., description="Name of the assessment")
    description: Optional[str] = Field(None, description="Description of the assessment")

class AssessmentCreate(AssessmentBase):
    repo_path: str = Field(..., description="Path to the repository to analyze")

class AssessmentResponse(AssessmentBase):
    id: str
    state: AssessmentState
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
