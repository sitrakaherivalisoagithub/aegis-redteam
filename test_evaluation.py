import asyncio
from src.aegis.domain.schemas.intelligence import PotentialFinding, TestCase
from src.aegis.domain.schemas.execution import TestExecution, Evidence
from src.aegis.providers.gemini import GeminiProvider
from src.aegis.risk.scorer import RiskScorer
from src.aegis.evaluation.evaluator import Evaluator

async def run_evaluation_pipeline():
    # 1. Mock inputs from previous phases
    finding = PotentialFinding(
        finding_id="FINDING-1", affected_component="Chat API",
        potential_weakness="Prompt Injection", possible_impact="Adversary bypasses rules.",
        confidence=0.8, suggested_validation="Send ignore instructions payload."
    )
    
    test_case = TestCase(
        test_id="TEST-1", title="Test PI", category="LLM", subcategory="PI",
        standard_reference="LLM01", target_component="Chat API", objective="Test overrides.",
        test_type="dynamic", expected_secure_behavior="Reject", success_criteria="No leak",
        evidence_requirements="Raw HTTP", severity_if_confirmed="high", supported_engines=["native"]
    )
    
    evidence = Evidence(test_id="TEST-1", raw_request="Payload", raw_response="Leaked secret")
    execution = TestExecution(
        test_id="TEST-1", status="failed", message="Leak detected.",
        evidence=[evidence], engine_used="native", execution_time_ms=50.0
    )
    
    # 2. Setup Evaluator
    provider = GeminiProvider()
    scorer = RiskScorer()
    evaluator = Evaluator(llm_provider=provider, risk_scorer=scorer)
    
    # 3. Execute Evaluation
    print("Executing Evaluator on mocked execution data...")
    final_finding = await evaluator.evaluate("ASSESS-999", finding, test_case, execution)
    
    # 4. Assertions
    assert final_finding.assessment_id == "ASSESS-999"
    assert final_finding.status == "confirmed" # Because execution 'failed' the security test
    assert final_finding.severity == "high" # Calculated by RiskScorer based on input
    assert len(final_finding.evidence_ids) == 1
    
    print("Evaluation Pipeline validation successful!")
    print(final_finding.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(run_evaluation_pipeline())
