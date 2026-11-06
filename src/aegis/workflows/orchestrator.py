from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.aegis.domain.schemas.scope import AssessmentScope
from src.aegis.domain.schemas.inventory import ApplicationInventory
from src.aegis.domain.schemas.intelligence import PotentialFinding, ThreatModel, TestPlan
from src.aegis.domain.schemas.evaluation import Finding
from src.aegis.domain.enums.assessment import AssessmentState
from src.aegis.discovery.repository.analyzer import RepositoryAnalyzer
from src.aegis.intelligence.agents.auditor import CodeAuditor
from src.aegis.intelligence.threat_modeling.modeler import ThreatModeler
from src.aegis.planning.planner import TestPlanner
from src.aegis.providers.gemini import GeminiProvider

class AssessmentGraphState(TypedDict):
    assessment_id: str
    scope: AssessmentScope
    state: AssessmentState
    inventory: ApplicationInventory | None
    findings: list[PotentialFinding]
    threat_model: ThreatModel | None
    test_plan: TestPlan | None
    final_findings: list[Finding]

class AssessmentOrchestrator:
    def __init__(self):
        self.provider = GeminiProvider()
        self.analyzer = RepositoryAnalyzer(self.provider)
        self.auditor = CodeAuditor(self.provider)
        self.modeler = ThreatModeler(self.provider)
        self.planner = TestPlanner(self.provider)
        
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AssessmentGraphState)
        
        # Define nodes
        workflow.add_node("discovery", self._node_discovery)
        workflow.add_node("intelligence", self._node_intelligence)
        workflow.add_node("planning", self._node_planning)
        
        # Define edges
        workflow.set_entry_point("discovery")
        workflow.add_edge("discovery", "intelligence")
        workflow.add_edge("intelligence", "planning")
        workflow.add_edge("planning", END)
        
        return workflow.compile()

    async def _node_discovery(self, state: AssessmentGraphState) -> dict:
        print(f"[{state['assessment_id']}] Running Discovery Node...")
        if state["scope"].repository:
            inventory = await self.analyzer.analyze(state["assessment_id"], state["scope"].repository)
        else:
            # Empty fallback if no repository defined in scope
            inventory = ApplicationInventory(assessment_id=state["assessment_id"])
            
        return {"inventory": inventory, "state": AssessmentState.DISCOVERED}

    async def _node_intelligence(self, state: AssessmentGraphState) -> dict:
        print(f"[{state['assessment_id']}] Running Intelligence Node...")
        findings = await self.auditor.audit(state["inventory"])
        threat_model = await self.modeler.generate_model(state["inventory"], findings)
        return {"findings": findings, "threat_model": threat_model, "state": AssessmentState.ANALYZED}

    async def _node_planning(self, state: AssessmentGraphState) -> dict:
        print(f"[{state['assessment_id']}] Running Planning Node...")
        test_plan = await self.planner.plan(state["threat_model"], state["findings"])
        return {"test_plan": test_plan, "state": AssessmentState.PLANNED}

    async def run(self, assessment_id: str, scope: AssessmentScope) -> AssessmentGraphState:
        initial_state = AssessmentGraphState(
            assessment_id=assessment_id,
            scope=scope,
            state=AssessmentState.CREATED,
            inventory=None,
            findings=[],
            threat_model=None,
            test_plan=None,
            final_findings=[]
        )
        final_state = await self.graph.ainvoke(initial_state)
        
        import os
        artifacts_dir = f"artifacts/{assessment_id}"
        os.makedirs(artifacts_dir, exist_ok=True)
        
        if final_state.get("inventory"):
            with open(f"{artifacts_dir}/inventory.json", "w", encoding='utf-8') as f:
                f.write(final_state["inventory"].model_dump_json(indent=2))
        
        if final_state.get("threat_model"):
            with open(f"{artifacts_dir}/threat_model.json", "w", encoding='utf-8') as f:
                f.write(final_state["threat_model"].model_dump_json(indent=2))
                
        if final_state.get("test_plan"):
            with open(f"{artifacts_dir}/test_plan.json", "w", encoding='utf-8') as f:
                f.write(final_state["test_plan"].model_dump_json(indent=2))
                
        return final_state
