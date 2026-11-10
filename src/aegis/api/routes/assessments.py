from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.aegis.storage.database import get_db
from src.aegis.domain.models.assessment import AssessmentModel
from src.aegis.domain.schemas.assessment import AssessmentCreate, AssessmentResponse
from src.aegis.domain.schemas.scope import AssessmentScope, RepositoryConfiguration
from src.aegis.workflows.orchestrator import AssessmentOrchestrator
import asyncio

router = APIRouter(prefix="/assessments", tags=["Assessments"])

async def run_pipeline_task(assessment_id: str, repo_path: str):
    try:
        print(f"\n🚀 [BACKGROUND TASK] Starting Analysis Pipeline for {assessment_id}")
        print(f"📁 Target Repository: {repo_path}")
        
        scope = AssessmentScope(
            target_type="repository", 
            repository=RepositoryConfiguration(source="local", path=repo_path)
        )
        orchestrator = AssessmentOrchestrator()
        await orchestrator.run(assessment_id, scope)
        print(f"✅ [BACKGROUND TASK] Pipeline completed for {assessment_id}\n")
    except Exception as e:
        print(f"❌ [BACKGROUND TASK] Pipeline failed for {assessment_id}: {e}\n")

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(assessment: AssessmentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_assessment = AssessmentModel(
        name=assessment.name,
        description=assessment.description
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    
    background_tasks.add_task(run_pipeline_task, db_assessment.id, assessment.repo_path)
    
    return db_assessment

@router.get("/", response_model=list[AssessmentResponse])
def list_assessments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AssessmentModel).offset(skip).limit(limit).all()

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.query(AssessmentModel).filter(AssessmentModel.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

from pydantic import BaseModel
class PentestRequest(BaseModel):
    agent_endpoint: str
    auth_type: str = "none"
    auth_header: str | None = None
    api_key: str | None = None
    request_template: dict | None = None
    response_field: str | None = None

@router.post("/{assessment_id}/pentest")
async def run_pentest_endpoint(assessment_id: str, request: PentestRequest):
    import os
    from src.aegis.execution.pentest_runner import PentestRunner
    from src.aegis.domain.schemas.scope import TargetConfiguration
    
    artifacts_dir = f"artifacts/{assessment_id}"
    if os.path.exists(os.path.join(artifacts_dir, "FINAL_REPORT.md")):
        return {"status": "error", "message": "Un rapport existe déjà pour cet audit."}
        
    # Build the target config dynamically
    target_config = TargetConfiguration(
        target_id="dynamic-target",
        name="Dynamic UI Target",
        target_type="rest_api",
        base_url=request.agent_endpoint,
        endpoint_path="",
        authentication_type=request.auth_type,
        auth_header=request.auth_header,
        request_template=request.request_template or {},
        response_mapping={"output": request.response_field} if request.response_field else {}
    )
    
    credentials = {"password": request.api_key} if request.api_key else {}
    runner = PentestRunner(target_config=target_config, credentials=credentials)
    success = await runner.run_full_pentest(assessment_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Plan de test introuvable pour cet audit.")
        
    return {"status": "success", "message": "Pentest exécuté avec succès et rapport généré."}
