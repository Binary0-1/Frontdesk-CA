from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid

class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_base"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    question: str
    answer: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
