from pydantic import BaseModel
from src.aegis.domain.schemas.inventory import ApplicationInventory
from src.aegis.domain.schemas.intelligence import PotentialFinding
from src.aegis.domain.interfaces.provider import LLMProvider

class AuditorOutput(BaseModel):
    findings: list[PotentialFinding]

class CodeAuditor:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def audit(self, inventory: ApplicationInventory) -> list[PotentialFinding]:
        print(f"🧠 [Code Auditor] Analyzing inventory for assessment: {inventory.assessment_id}")
        
        prompt = f"""You are an expert AI Security Auditor.
Review the following Application Inventory for an AI/LLM-based project.
Identify potential security weaknesses, focusing on OWASP Top 10 for LLMs (e.g., Prompt Injection, Insecure Output Handling, Training Data Poisoning, Sensitive Information Disclosure).

Application Inventory:
{inventory.model_dump_json(indent=2)}

Provide a list of potential findings. Be precise and technical.
"""
        try:
            response = await self.llm_provider.generate(
                messages=[{"role": "system", "content": "You are a specialized AI security auditor."},
                          {"role": "user", "content": prompt}],
                response_schema=AuditorOutput
            )
            findings = response.findings if hasattr(response, 'findings') else []
            print(f"✅ [Code Auditor] Found {len(findings)} potential weaknesses.")
            return findings
        except Exception as e:
            print(f"❌ [Code Auditor] Error during LLM generation: {e}")
            return []
