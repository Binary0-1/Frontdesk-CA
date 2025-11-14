from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class SupervisorBase(BaseModel):
    name: str
    email: str

class SupervisorCreate(SupervisorBase):
    pass

class SupervisorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class SupervisorRead(SupervisorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
