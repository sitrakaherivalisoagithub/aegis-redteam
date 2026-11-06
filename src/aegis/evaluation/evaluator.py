from src.aegis.domain.schemas.intelligence import PotentialFinding, TestCase
from src.aegis.domain.schemas.execution import TestExecution
from src.aegis.domain.schemas.evaluation import Finding
from src.aegis.risk.scorer import RiskScorer
from src.aegis.domain.interfaces.provider import LLMProvider

class Evaluator:
    """
    Evaluates TestExecution results against original PotentialFindings and TestCases 
    to produce a final, actionable Finding.
    """
    
    def __init__(self, llm_provider: LLMProvider, risk_scorer: RiskScorer):
        self.llm_provider = llm_provider
        self.risk_scorer = risk_scorer

    async def evaluate(self, assessment_id: str, potential_finding: PotentialFinding, test_case: TestCase, execution: TestExecution) -> Finding:
        print(f"Evaluating execution {execution.execution_id} for test {test_case.test_id}...")
        
        # 1. Calculate Risk
        risk = self.risk_scorer.calculate_risk(potential_finding, execution)
        
        # 2. Determine Final Status
        status = "not_reproduced"
        if execution.status == "failed":
            # "Failed" security test means the vulnerability is confirmed
            status = "confirmed"
        elif execution.status == "passed":
            # "Passed" security test means the target protected itself
            status = "false_positive"
        elif execution.status == "inconclusive":
            # Would typically trigger LLM-as-a-judge validation here
            status = "suspected"

        # 3. Construct Final Finding
        finding = Finding(
            assessment_id=assessment_id,
            title=f"{test_case.category} in {potential_finding.affected_component}",
            description=f"Validation of {potential_finding.potential_weakness}. Objective: {test_case.objective}",
            standard="OWASP LLM Top 10",
            standard_version="2026",
            standard_reference=test_case.standard_reference,
            affected_component=potential_finding.affected_component,
            severity=risk.severity,
            confidence=risk.confidence,
            status=status,
            impact=risk.business_impact,
            evidence_ids=[ev.evidence_id for ev in execution.evidence],
            root_cause="Inadequate input sanitization/validation at the trust boundary.",
            recommendations=["Implement robust prompt boundary defenses.", "Restrict model permissions."]
        )
        
        return finding
