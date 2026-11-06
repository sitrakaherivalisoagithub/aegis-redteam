from src.aegis.domain.schemas.inventory import ApplicationInventory
from src.aegis.domain.schemas.intelligence import PotentialFinding, ThreatModel, Threat
from src.aegis.domain.interfaces.provider import LLMProvider

class ThreatModeler:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def generate_model(self, inventory: ApplicationInventory, findings: list[PotentialFinding]) -> ThreatModel:
        print(f"🧠 [Threat Modeler] Generating Threat Model...")
        
        prompt = f"""You are an expert Threat Modeler specializing in AI applications.
Based on the application inventory and the potential findings provided by the auditor, build a structured Threat Model.
Identify the assets, trust boundaries, actors, entry points, and specific threat scenarios.
Map them to recognized standard mappings (e.g., OWASP LLM01, LLM02, etc.).

Inventory:
{inventory.model_dump_json(indent=2)}

Findings:
{[f.model_dump_json() for f in findings]}

Generate the threat model structured output.
"""
        try:
            response = await self.llm_provider.generate(
                messages=[{"role": "system", "content": "You are a cyber security threat modeler."},
                          {"role": "user", "content": prompt}],
                response_schema=ThreatModel
            )
            response.assessment_id = inventory.assessment_id
            print(f"✅ [Threat Modeler] Generated {len(response.threats)} threats.")
            return response
        except Exception as e:
            print(f"❌ [Threat Modeler] Error during LLM generation: {e}")
            return ThreatModel(assessment_id=inventory.assessment_id, threats=[])
