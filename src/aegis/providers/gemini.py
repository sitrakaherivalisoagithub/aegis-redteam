import os
import google.auth
from google.oauth2 import service_account
from pydantic import BaseModel
from typing import Dict, Any, Type
from src.aegis.domain.interfaces.provider import LLMProvider
from src.aegis.core.config import settings

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

def get_google_credentials():
    SA_FILE_PATH = settings.SA_FILE_PATH
    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
    
    # Allow testing bypass
    if SA_FILE_PATH == "mock_path_for_testing":
        return None
        
    if SA_FILE_PATH and os.path.exists(SA_FILE_PATH):
        print(f"Loading service account credentials from file: {SA_FILE_PATH}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_FILE_PATH
        creds = service_account.Credentials.from_service_account_file(
            SA_FILE_PATH, scopes=SCOPES
        )
    else:
        print("Key file not found or not provided. Using Application Default Credentials (ADC).")
        try:
            creds, _ = google.auth.default(scopes=SCOPES)
        except Exception as e:
            print(f"Failed to load ADC: {e}")
            creds = None
    return creds

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.location = settings.GEMINI_LOCATION
        self.model = None
        
        if LANGCHAIN_AVAILABLE:
            creds = get_google_credentials()
            if creds:
                # Use project ID from service account if available, fallback to config
                project_id = getattr(creds, "project_id", settings.GEMINI_PROJECT_ID)
                self.model = ChatGoogleGenerativeAI(
                    model=settings.MODEL_NAME,
                    project=project_id,
                    location=self.location,
                    credentials=creds,
                    temperature=0.2
                )

    async def generate(self, messages: list[dict[str, str]], response_schema: type[BaseModel] | None = None) -> Any:
        if not self.model:
            print("WARNING: GeminiProvider missing credentials or langchain_google_genai is not installed. Returning stub.")
            if response_schema:
                return response_schema.model_construct()
            return "Stub response from Gemini."
            
        lc_messages = []
        for msg in messages:
            role = msg.get("role", "user").lower()
            content = msg.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        
        try:
            if response_schema:
                structured_llm = self.model.with_structured_output(response_schema)
                response = await structured_llm.ainvoke(lc_messages)
                return response
            else:
                response = await self.model.ainvoke(lc_messages)
                return response.content
        except Exception as e:
            print(f"Failed to generate from Gemini via LangChain: {e}")
            if response_schema:
                return response_schema.model_construct()
            return str(e)

    async def health_check(self) -> bool:
        return self.model is not None
