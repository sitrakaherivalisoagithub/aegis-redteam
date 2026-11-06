from pydantic import BaseModel
import json
from src.aegis.domain.schemas.scope import RepositoryConfiguration
from src.aegis.domain.schemas.inventory import ApplicationInventory
from src.aegis.domain.interfaces.provider import LLMProvider
from src.aegis.core.config import settings
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend, CompositeBackend

class RepositoryAnalyzer:
    """
    Adapter for LangChain Deep Agents exploration.
    This component uses the Deep Agents SDK to analyze the target repository and generate an ApplicationInventory.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def analyze(self, assessment_id: str, repo_config: RepositoryConfiguration) -> ApplicationInventory:
        print(f"Starting repository analysis for {repo_config.source} at {repo_config.path or repo_config.url}")
        
        target_path = repo_config.path if repo_config.source == "local" else repo_config.url
        
        # System prompt for the deep agent
        system_prompt = f"""You are a senior security architect exploring a target repository. 
Your goal is to identify languages, frameworks, dependencies, AI components, LLM integrations, and security mechanisms.
The target repository is mounted at /workspace/

Use your tools to read files and explore the repository. 
Focus on identifying AI architectures, agents, prompts, and authentication mechanisms.
"""

        state_backend = StateBackend()
        
        if repo_config.source == "local" and repo_config.path:
            fs_backend = FilesystemBackend(root_dir=repo_config.path, virtual_mode=True)
            backend = CompositeBackend(
                default=state_backend,
                routes={
                    "/workspace/": fs_backend,
                }
            )
        else:
            backend = state_backend

        try:
            # We must use the properly authenticated ChatGoogleGenerativeAI instance from the provider.
            # If initialization failed in GeminiProvider, agent_model will be None and this should catch safely.
            agent_model = getattr(self.llm_provider, "model", None)
            
            if not agent_model:
                raise ValueError("Authenticated ChatGoogleGenerativeAI model instance is not available.")

            # Initialize the Deep Agent
            agent = create_deep_agent(
                model=agent_model,
                tools=[], 
                system_prompt=system_prompt,
                response_format=ApplicationInventory,
                backend=backend
            )
            print("Invoking Deep Agent traversal (this may take a moment)...")
            result = agent.invoke({"messages": [{"role": "user", "content": "Begin repository exploration and output the requested report."}]})
            
            inventory = result.get("structured_response")
            if not inventory:
                inventory = ApplicationInventory(assessment_id=assessment_id)
            else:
                inventory.assessment_id = assessment_id
            return inventory
        except Exception as e:
            print(f"Deep Agent initialization or execution failed: {e}")
            print("Falling back to stub inventory generation.")
            inventory = ApplicationInventory(assessment_id=assessment_id)
            return inventory
