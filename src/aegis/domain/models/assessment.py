import uuid
from datetime import datetime
from sqlalchemy import String, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.aegis.domain.models.base import Base
from src.aegis.domain.enums.assessment import AssessmentState

class AssessmentModel(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[AssessmentState] = mapped_column(SQLEnum(AssessmentState), default=AssessmentState.CREATED)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
