from typing import Protocol, Any, Dict

class LLMProvider(Protocol):
    async def generate(self, messages: list[Dict[str, str]], response_schema: type | None = None) -> Any:
        ...

    async def health_check(self) -> bool:
        ...
