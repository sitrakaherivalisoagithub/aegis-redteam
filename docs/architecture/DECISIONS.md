# Architectural Decisions Record (ADR)

## 1. Modular Monolith Approach
**Decision**: Adopt a modular monolith architecture instead of microservices.
**Rationale**: Keeps the codebase cohesive, simplifies deployment, and avoids the complexity of distributed systems overhead in the early stages, while maintaining strict module boundaries.

## 2. Pydantic for Data Contracts
**Decision**: Use Pydantic v2 for all inter-module data contracts.
**Rationale**: Provides strict data validation, serialization, and typing, ensuring that modules communicate with predictable data structures.

## 3. Interchangeable Execution Engines
**Decision**: The execution layer will be abstracted to support multiple engines (Promptfoo, PyRIT, Native).
**Rationale**: Avoids vendor lock-in and allows the platform to choose the best tool for specific test cases (e.g., Promptfoo for simple eval, PyRIT for multi-turn adversarial).

## 4. LangGraph for Orchestration
**Decision**: Use LangGraph to manage the assessment lifecycle.
**Rationale**: Assessments require a stateful, resumable, and interruptible workflow, which LangGraph naturally supports.
