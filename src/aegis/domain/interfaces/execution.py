from typing import Protocol, List, Dict, Any
from src.aegis.domain.schemas.intelligence import TestCase
from src.aegis.domain.schemas.execution import TestExecution

class TargetHealth(Protocol):
    is_healthy: bool
    details: str

class TargetAdapter(Protocol):
    async def health_check(self) -> TargetHealth:
        ...

    async def send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    async def close(self) -> None:
        ...

class EngineCapabilities(Protocol):
    supported_types: List[str]
    can_multi_turn: bool

class TestEngine(Protocol):
    async def health_check(self) -> bool:
        ...

    async def execute(self, test_case: TestCase, target: TargetAdapter) -> TestExecution:
        ...

    def capabilities(self) -> EngineCapabilities:
        ...
