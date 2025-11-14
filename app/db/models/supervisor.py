from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid

class Supervisor(SQLModel, table=True):
    __tablename__ = "supervisors"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
