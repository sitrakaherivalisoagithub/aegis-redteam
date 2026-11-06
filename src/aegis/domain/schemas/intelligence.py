from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class PotentialFinding(BaseModel):
    finding_id: str
    affected_component: str
    source_reference: Optional[str] = None
    potential_weakness: str
    owasp_mapping: Optional[str] = None
    possible_impact: str
    confidence: float
    suggested_validation: str

class Threat(BaseModel):
    threat_id: str
    asset: str
    trust_boundary: str
    actor: str
    entry_point: str
    threat_scenario: str
    standard_mapping: Optional[str] = None

class ThreatModel(BaseModel):
    assessment_id: str
    threats: List[Threat] = []

class TestCase(BaseModel):
    test_id: str
    title: str
    category: str
    subcategory: str
    standard_reference: str
    target_component: str
    objective: str
    preconditions: List[str] = []
    test_type: Literal["static", "dynamic", "adversarial", "hybrid"]
    expected_secure_behavior: str
    success_criteria: str
    evidence_requirements: str
    severity_if_confirmed: Literal["critical", "high", "medium", "low", "informational"]
    supported_engines: List[Literal["promptfoo", "pyrit", "native"]]
    execution_constraints: List[str] = []

class TestPlan(BaseModel):
    assessment_id: str
    test_cases: List[TestCase] = []
