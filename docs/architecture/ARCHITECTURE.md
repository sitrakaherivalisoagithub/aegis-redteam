# Aegis AI Red Team - Architecture

## System Overview
Aegis AI Red Team is a hybrid AI Security Assessment platform designed to audit AI-powered applications through two complementary approaches: White-box security assessment (code/repo analysis) and Black-box security assessment (dynamic API interaction).

## Logical Architecture
```text
                    AEGIS AI RED TEAM
                            |
                  STREAMLIT DASHBOARD
                            |
                       FASTAPI
                            |
                 ASSESSMENT CONTROLLER
                            |
                       LANGGRAPH
                            |
          +-----------------+-----------------+
          |                 |                 |
      DISCOVERY         INTELLIGENCE       EXECUTION
          |                 |                 |
     Deep Agents        Threat Modeler     Test Engines
     Repository         Test Planner       Promptfoo
     Analyzer           OWASP Mapper       PyRIT
     Architecture       Code Auditor       Native Python
          |                 |                 |
          +-----------------+-----------------+
                            |
                      EVALUATION
                            |
                   EVIDENCE VALIDATION
                            |
                     RISK ASSESSMENT
                            |
                      REPORT ENGINE
                            |
              MARKDOWN / JSON / OPTIONAL PDF
```

## Core Components
- **Language**: Python 3.12+
- **API**: FastAPI
- **Orchestration**: LangGraph
- **Repository Exploration**: Deep Agents (LangChain)
- **Execution Engine**: Configurable adapters for Promptfoo, PyRIT, and Native Python.
- **Persistence**: SQLAlchemy + SQLite
- **UI**: Streamlit
