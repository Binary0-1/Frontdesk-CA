
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid

class Customer(SQLModel, table=True): 
    __tablename__ = "customers"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    phone_number: str = Field(unique=True,index=True)
    name: str 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
