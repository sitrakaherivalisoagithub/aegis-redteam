import asyncio
from src.aegis.domain.schemas.inventory import ApplicationInventory
from src.aegis.providers.gemini import GeminiProvider
from src.aegis.intelligence.agents.auditor import CodeAuditor
from src.aegis.intelligence.threat_modeling.modeler import ThreatModeler
from src.aegis.planning.planner import TestPlanner

async def run_intelligence_pipeline():
    # 1. Setup
    provider = GeminiProvider()
    inventory = ApplicationInventory(
        assessment_id="test-5678",
        languages=["Python"],
        frameworks=["FastAPI"],
        prompt_locations=["src/prompts/"]
    )
    
    # 2. Audit
    auditor = CodeAuditor(llm_provider=provider)
    findings = await auditor.audit(inventory)
    assert len(findings) > 0
    assert findings[0].finding_id == "FINDING-STUB-001"
    print(f"Generated {len(findings)} findings.")
    
    # 3. Threat Modeling
    modeler = ThreatModeler(llm_provider=provider)
    threat_model = await modeler.generate_model(inventory, findings)
    assert len(threat_model.threats) > 0
    print(f"Generated Threat Model with {len(threat_model.threats)} threats.")
    
    # 4. Planning
    planner = TestPlanner(llm_provider=provider)
    test_plan = await planner.plan(threat_model, findings)
    assert len(test_plan.test_cases) > 0
    print("Generated Test Plan.")
    print(test_plan.model_dump_json(indent=2))
    
    print("\nIntelligence Pipeline validation successful!")

if __name__ == "__main__":
    asyncio.run(run_intelligence_pipeline())
