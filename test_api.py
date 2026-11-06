import os
# Ensure we don't conflict with existing databases for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_aegis.db"

from fastapi.testclient import TestClient
from src.aegis.api.main import app
from src.aegis.domain.models.base import Base
from src.aegis.storage.database import engine

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Aegis API"}
    print("Health check passed.")

def test_create_assessment():
    response = client.post(
        "/api/v1/assessments/",
        json={"name": "Test Assessment", "description": "A quick test", "repo_path": "/mock/path"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Assessment"
    assert "id" in data
    print("Assessment creation passed.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    test_health()
    test_create_assessment()
    print("All basic tests passed successfully!")
