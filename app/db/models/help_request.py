
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey
import uuid
from typing import Optional

class HelpRequest(SQLModel, table=True):  
    __tablename__ = "help_requests" 
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(sa_column=Column("customer_id", ForeignKey("customer.id")))
    question: str
    status: str = Field(default="pending")
    supervisor_response: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None)
    notified: bool = Field(default=False)
    notified_at: Optional[datetime] = Field(default=None)
    
