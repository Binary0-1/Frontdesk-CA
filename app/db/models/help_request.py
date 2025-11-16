
import enum
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from typing import Optional

class HelpStatus(enum.Enum):
    pending = "pending"
    resolved = "resolved"
    timed_out = "timed_out"

class HelpRequest(SQLModel, table=True):
    __tablename__ = "help_request"
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    question: str = Field(nullable=False)
    customer_contact: dict | None = Field(sa_column=Column(JSONB))
    status: HelpStatus = Field(sa_column=Column(Enum(HelpStatus)), default=HelpStatus.pending)
    supervisor_answer: str | None = Field(default=None)
    answered_at: Optional[datetime] = Field(default=None)
    timeout_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")}
    )
