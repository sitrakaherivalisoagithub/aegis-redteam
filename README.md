# Aegis AI Red Team 🛡️

**Aegis AI Red Team** is a production-oriented AI Security Assessment and Red Team framework. It is designed to audit AI-powered applications through two complementary approaches:

1. **White-box security assessment**: Analyzes the target application's source code, architecture, and repository using autonomous deep agents to identify potential security weaknesses.
2. **Black-box security assessment**: Interacts with a running AI application (REST APIs, OpenAI-compatible endpoints, RAG applications, etc.) through dynamically configured endpoints to execute adversarial test cases.

The platform combines static analysis, threat modeling, adversarial testing, deterministic evaluation, and LLM-assisted reporting into a cohesive, orchestrated workflow.

---

## 🏗️ Architecture & Core Technologies

*   **Backend API**: FastAPI
*   **Orchestration**: LangGraph
*   **Intelligence & Discovery**: LangChain & Deep Agents SDK
*   **Data Validation**: Pydantic v2
*   **Persistence**: SQLAlchemy + SQLite
*   **UI Dashboard**: Streamlit
*   **Execution Engines**: Native Python, Promptfoo, PyRIT
*   **LLM Provider**: Google Gemini / Vertex AI (via `langchain-google-genai`)

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
*   **Python 3.12+**
*   **uv** (Fast Python package manager)
*   A **Google Gemini** API key or **Google Cloud Vertex AI** project credentials.

---

## 🚀 Installation & Setup

**1. Clone the repository and navigate to the project root:**
```bash
cd aegis-ai-redteam
```

**2. Create and activate a virtual environment using `uv`:**
```bash
# Create virtual environment
uv venv .venv

# Activate on Windows
.venv\Scripts\activate
# OR Activate on macOS/Linux
source .venv/bin/activate
```

**3. Install the project and its dependencies:**
```bash
uv pip install -e .
```

**4. Configure your environment variables:**
Copy the example environment file and fill in your credentials.
```bash
cp .env.example .env
```
Open `.env` and set `SA_FILE_PATH` to the absolute path of your Google Cloud Service Account JSON key file. The system will automatically use this file to authenticate with Vertex AI. If not provided, it will attempt to fallback to Application Default Credentials (ADC).

---

## 💻 Launching the Application

The Aegis AI Red Team platform consists of a backend API and a frontend UI. They need to run simultaneously in separate terminal windows.

### 1. Start the FastAPI Backend
The backend manages the assessment state machine, database, and LangGraph orchestrator.

```bash
# Ensure your virtual environment is active
uvicorn src.aegis.api.main:app --reload --host 127.0.0.1 --port 8000
```
*   **API Base URL**: `http://127.0.0.1:8000/api/v1`
*   **Swagger Documentation**: `http://127.0.0.1:8000/docs`

### 2. Start the Streamlit Dashboard
The frontend provides the user interface for configuring targets, approving test plans, and viewing generated reports.

Open a **new terminal window**, activate the virtual environment, and run:
```bash
# Ensure your virtual environment is active
streamlit run frontend/streamlit_app/app.py
```
*   **Dashboard URL**: `http://localhost:8501`

---

## 🧪 Running Tests

The project includes a suite of programmatic test scripts that validate each phase of the pipeline in isolation without requiring the full server to be running.

Run these scripts directly using Python:

```bash
# Test Phase 1: API and Database Foundation
python test_api.py

# Test Phase 2: Deep Agents Repository Discovery
python test_discovery.py

# Test Phase 3: Threat Modeling & Intelligence Agents
python test_intelligence.py

# Test Phase 4: Native Execution Engine & Adapters
python test_execution.py

# Test Phase 5: Risk Scoring & Finding Evaluation
python test_evaluation.py

# Test Phase 6: Markdown Report Generation
python test_reporting.py
```

---

## 📖 Project Structure

```text
aegis-ai-redteam/
├── src/aegis/
│   ├── api/                 # FastAPI routes and endpoints
│   ├── core/                # Configuration and environment settings
│   ├── discovery/           # Deep Agents repository analyzers
│   ├── domain/              # Pydantic schemas and SQLAlchemy models
│   ├── evaluation/          # Finding and false-positive evaluation logic
│   ├── execution/           # Test engines (Native, Promptfoo, PyRIT)
│   ├── intelligence/        # Code Auditor, Threat Modeler, OWASP Mapper
│   ├── planning/            # Test Plan generator
│   ├── providers/           # LLM Integrations (Gemini / Vertex AI)
│   ├── reporting/           # Markdown & Jinja2 report generators
│   ├── risk/                # Risk assessment and severity scoring
│   ├── storage/             # SQLite / SQLAlchemy persistence setup
│   └── workflows/           # LangGraph state machine orchestrator
├── frontend/                # Streamlit UI application
├── docs/                    # Architecture records and implementation status
├── test_*.py                # Standalone programmatic validation scripts
├── pyproject.toml           # Project dependencies
└── README.md                # This file
```

---

## ⚠️ Security Warning

**Aegis AI Red Team is a security tool.**
*   Do not execute arbitrary code from target repositories.
*   Production assessments should use explicitly approved, non-destructive test plans.
*   Do not expose unrestricted shell or network access to the Deep Agents.
*   Ensure targets explicitly authorize automated adversarial payloads before initiating execution.
