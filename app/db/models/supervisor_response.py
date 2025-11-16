
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

class SupervisorResponse(SQLModel, table=True):
    __tablename__ = "supervisor_response"
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    help_request_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), ForeignKey("help_request.id", ondelete="CASCADE")))
    message: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")}
    )
