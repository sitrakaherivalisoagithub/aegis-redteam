from src.aegis.domain.schemas.evaluation import RiskAssessment
from src.aegis.domain.schemas.intelligence import PotentialFinding
from src.aegis.domain.schemas.execution import TestExecution

class RiskScorer:
    """
    Evaluates the risk of a confirmed finding based on its potential weakness 
    and the concrete evidence from test execution.
    """
    
    def calculate_risk(self, finding: PotentialFinding, execution: TestExecution) -> RiskAssessment:
        # Simplistic deterministic logic for V1.
        # In a full implementation, this could blend CVSS vectors or utilize an LLM call.
        
        severity = "informational"
        if execution.status == "failed":
            # If the security test failed, the vulnerability is confirmed
            severity = finding.possible_impact.lower()
            if "override" in severity or "exfiltrate" in severity or "injection" in finding.potential_weakness.lower():
                severity = "high"
        
        confidence = 1.0 if execution.status == "failed" else 0.5
        exploitability = "easy" if "prompt injection" in finding.potential_weakness.lower() else "moderate"
        
        return RiskAssessment(
            severity=severity if severity in ["critical", "high", "medium", "low", "informational"] else "medium",
            confidence=confidence,
            exploitability=exploitability,
            business_impact=finding.possible_impact,
            justification=f"Execution completed with status '{execution.status}'. Automated assessment based on component and test engine outcome."
        )
