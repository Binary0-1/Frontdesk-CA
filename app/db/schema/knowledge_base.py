from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class KnowledgeBaseBase(BaseModel):
    question: str
    answer: str

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

class KnowledgeBaseRead(KnowledgeBaseBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
