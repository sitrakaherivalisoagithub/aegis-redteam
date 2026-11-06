from fastapi import FastAPI
from src.aegis.api.routes import assessments
from src.aegis.storage.database import engine
from src.aegis.domain.models.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aegis AI Red Team",
    description="API for AI Security Assessment Platform",
    version="0.1.0"
)

app.include_router(assessments.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Aegis API"}
