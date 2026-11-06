from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Aegis AI Red Team"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "sqlite:///./aegis.db"
    
    # Gemini configurations
    GEMINI_PROJECT_ID: str = ""
    GEMINI_LOCATION: str = "us-central1"
    MODEL_NAME: str = "gemini-1.5-pro-preview-0409"
    SA_FILE_PATH: str | None = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
