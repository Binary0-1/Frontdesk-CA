from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class CustomerBase(BaseModel):
    phone_number: str
    name: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None

class CustomerRead(CustomerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
