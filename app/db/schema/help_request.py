from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class HelpRequestBase(BaseModel):
    customer_id: uuid.UUID
    question: str

class HelpRequestCreate(HelpRequestBase):
    pass

class HelpRequestUpdate(BaseModel):
    status: Optional[str] = None
    supervisor_response: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notified: Optional[bool] = None
    notified_at: Optional[datetime] = None

class HelpRequestRead(HelpRequestBase):
    id: uuid.UUID
    status: str
    supervisor_response: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    notified: bool
    notified_at: Optional[datetime]

    class Config:
        orm_mode = True
