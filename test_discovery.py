import asyncio
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_aegis.db"

from src.aegis.domain.schemas.scope import RepositoryConfiguration
from src.aegis.domain.schemas.inventory import ApplicationInventory
from src.aegis.discovery.repository.analyzer import RepositoryAnalyzer
from src.aegis.providers.gemini import GeminiProvider

async def test_discovery_stub():
    import os
    os.environ["DATABASE_URL"] = "sqlite:///./test_aegis.db"
    os.environ["GOOGLE_API_KEY"] = "mock_api_key_for_testing"

    # Provide the mocked Gemini Provider
    provider = GeminiProvider()
    
    # Configure the repository target
    config = RepositoryConfiguration(
        source="local",
        path="/mock/path/to/repo"
    )
    
    analyzer = RepositoryAnalyzer(llm_provider=provider)
    
    print("Executing RepositoryAnalyzer stub...")
    inventory = await analyzer.analyze(assessment_id="test-1234", repo_config=config)
    
    assert isinstance(inventory, ApplicationInventory)
    assert inventory.assessment_id == "test-1234"
    
    print("Application Inventory generation (with Deep Agents exception fallback) passed!")
    print(inventory.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(test_discovery_stub())
